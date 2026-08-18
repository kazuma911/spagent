"""Apply AI classification (rubric v1) to parsed menu records.

Workflow G Step 7.5 で LLM が [references/ai-classification-rubric.md](../../references/ai-classification-rubric.md)
に従って各メニューを判定した結果 JSON を、parsed records に反映するスクリプト。

`ai_review.py` は low-confidence レコードだけを method/zone_tags に絞って上書きする軽量版。
本スクリプトはそれと違い、**全レコード** に対して **フルスキーマ**（method / phase / zone_tags /
target / theme_interpretation / coach_review_needed / review_reasons / judged_by / judged_at）
を書き込む。既存の `classification` フィールドは上書き（旧 script tagger の判定を置き換える）。

入力 JSON 形式（LLM が生成する分類結果）:
```json
{
  "rubric_version": "v1",
  "judged_by": "spagent-classify-v1",
  "judged_at": "2026-08-17T18:00:00+09:00",
  "records": [
    {
      "id": "recovery-19fca077",
      "method": { "primary": "descending", ... },
      "phase": { "primary": "A", "signals": {...}, ... },
      "zone_tags": ["EN1", "EN2", "EN3", "SP2"],
      "target": { ... },
      "theme_interpretation": "...",
      "coach_review_needed": true,
      "review_reasons": [...]
    }
  ]
}
```

対応する parsed records の突合キーは `id` 優先、なければ `sheet_name`。

使い方:
    # parsed JSON に AI 分類を適用
    python scripts/classify/ai_classify.py apply \\
        --parsed sessions/2026-06-13/excel-import.classified.json \\
        --answers sessions/2026-06-13/ai-classification.json

    # menu-index.json に既存 AI 判定を再適用（rejudge / 移行）
    python scripts/classify/ai_classify.py migrate \\
        --index knowledge/custom/menu-index.json \\
        --answers knowledge/custom/ai-classification-batch.json

    # rubric 準拠チェック（zone tag 語彙、必須フィールド等）
    python scripts/classify/ai_classify.py validate \\
        --answers sessions/2026-06-13/ai-classification.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


RUBRIC_VERSION = "v1.1"
JUDGED_BY_DEFAULT = "spagent-classify-v1.1"

CANONICAL_METHODS = {
    "lsd", "threshold", "descending", "broken", "usrpt", "hiit", "fartlek",
}
CANONICAL_ZONE_TAGS = {"EN1", "EN2", "EN3", "SP1", "SP2", "SP3"}
CANONICAL_PHASES = {"A", "B", "C", "D", "REC"}
CANONICAL_INTENSITY_SIGNATURES = {"soft", "balanced", "high"}

LEGACY_ZONE_TAG_MAP = {
    "RECOVERY": "EN1",
    "AEROBIC": "EN2",
    "RACE_PACE": "SP2",
    "USRPT": "SP2",
    "BROKEN": "SP2",
    "SPRINT": "SP3",
    "VO2MAX": "SP1",
    "MSS": "SP1",
    "RP": "SP2",
}

REQUIRED_FIELDS = [
    "id",
    "method.primary",
    "method.confidence",
    "phase.primary",
    "phase.confidence",
    "zone_tags",
]

OPTIONAL_FIELDS = [
    "intensity_signature.level",
    "intensity_signature.confidence",
]


def _get_nested(obj: dict[str, Any], dotted_key: str) -> Any:
    """Retrieve dotted key path from nested dict; return None if missing."""
    cur: Any = obj
    for part in dotted_key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _normalize_zone_tags(tags: list[str]) -> tuple[list[str], list[str]]:
    """Split zone tags into canonical zones and method-like tags.

    Returns (canonical_zone_tags, method_tags).
    Legacy tags (RECOVERY / AEROBIC / RACE_PACE / ...) are converted using
    LEGACY_ZONE_TAG_MAP. Method-like tags are preserved separately.
    """
    zones: set[str] = set()
    methods: set[str] = set()
    for raw in tags:
        if not isinstance(raw, str):
            continue
        tag = raw.strip().upper()
        if tag in CANONICAL_ZONE_TAGS:
            zones.add(tag)
        elif tag in LEGACY_ZONE_TAG_MAP:
            zones.add(LEGACY_ZONE_TAG_MAP[tag])
            methods.add(tag.lower().replace("_", "-"))
    return sorted(zones), sorted(methods)


def _validate_record(record: dict[str, Any]) -> list[str]:
    """Return list of validation errors for a single classification record."""
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if _get_nested(record, field) in (None, "", []):
            errors.append(f"missing required field: {field}")

    method_primary = _get_nested(record, "method.primary")
    if method_primary and method_primary not in CANONICAL_METHODS:
        if not method_primary.startswith("custom_"):
            errors.append(
                f"method.primary '{method_primary}' is not canonical "
                f"(expected one of {sorted(CANONICAL_METHODS)} or 'custom_*')"
            )

    phase_primary = _get_nested(record, "phase.primary")
    if phase_primary and phase_primary not in CANONICAL_PHASES:
        errors.append(
            f"phase.primary '{phase_primary}' is not canonical "
            f"(expected one of {sorted(CANONICAL_PHASES)})"
        )

    zone_tags = record.get("zone_tags") or []
    non_canonical = [
        t for t in zone_tags
        if isinstance(t, str) and t.upper() not in CANONICAL_ZONE_TAGS
    ]
    if non_canonical:
        errors.append(
            f"zone_tags contains non-canonical entries {non_canonical} "
            f"(rubric §6 requires EN1-SP3; move method-like tags to method_tags[])"
        )

    signals = _get_nested(record, "phase.signals") or {}
    if not signals and _get_nested(record, "phase.confidence") == "high":
        errors.append("phase.confidence=high requires phase.signals to be populated")

    intensity_level = _get_nested(record, "intensity_signature.level")
    if intensity_level and intensity_level not in CANONICAL_INTENSITY_SIGNATURES:
        errors.append(
            f"intensity_signature.level '{intensity_level}' is not canonical "
            f"(expected one of {sorted(CANONICAL_INTENSITY_SIGNATURES)})"
        )

    return errors


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate an AI classification answer file against the rubric."""
    data = json.loads(args.answers.read_text(encoding="utf-8"))
    records = data.get("records") if isinstance(data, dict) else data
    if not isinstance(records, list):
        print("error: answers must contain a list of records", file=sys.stderr)
        return 1

    total_errors = 0
    for idx, record in enumerate(records):
        if not isinstance(record, dict):
            print(f"[{idx}] error: record is not a dict", file=sys.stderr)
            total_errors += 1
            continue
        errors = _validate_record(record)
        if errors:
            record_id = record.get("id") or f"index-{idx}"
            print(f"[{record_id}] {len(errors)} error(s):", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            total_errors += len(errors)

    if total_errors:
        print(f"validation FAILED: {total_errors} error(s) across {len(records)} records", file=sys.stderr)
        return 2
    print(f"validation OK: {len(records)} record(s) conform to rubric {RUBRIC_VERSION}")
    return 0


def _merge_classification(target: dict[str, Any], ai_record: dict[str, Any],
                          judged_by: str, judged_at: str) -> None:
    """Overwrite `target['classification']` with AI record fields."""
    canonical_zones, method_tags = _normalize_zone_tags(ai_record.get("zone_tags") or [])

    classification = {
        "method": ai_record.get("method", {}),
        "phase": ai_record.get("phase", {}),
        "zone_tags": canonical_zones,
        "method_tags": method_tags,
        "intensity_signature": ai_record.get("intensity_signature", {}),
        "target": ai_record.get("target", {}),
        "theme_interpretation": ai_record.get("theme_interpretation", ""),
        "coach_review_needed": bool(ai_record.get("coach_review_needed", False)),
        "review_reasons": list(ai_record.get("review_reasons") or []),
        "confidence": _get_nested(ai_record, "phase.confidence") or "medium",
        "judged_by": judged_by,
        "judged_at": judged_at,
        "rubric_version": RUBRIC_VERSION,
    }
    target["classification"] = classification


def cmd_apply(args: argparse.Namespace) -> int:
    """Apply AI classification to parsed records JSON."""
    parsed = json.loads(args.parsed.read_text(encoding="utf-8"))
    answers = json.loads(args.answers.read_text(encoding="utf-8"))

    if not isinstance(parsed, list):
        print("error: --parsed must be a JSON list of records", file=sys.stderr)
        return 1

    judged_by = answers.get("judged_by", JUDGED_BY_DEFAULT) if isinstance(answers, dict) else JUDGED_BY_DEFAULT
    judged_at = answers.get("judged_at") if isinstance(answers, dict) else None
    judged_at = judged_at or datetime.now().astimezone().isoformat()

    records = answers.get("records") if isinstance(answers, dict) else answers
    if not isinstance(records, list):
        print("error: --answers must contain a list of records", file=sys.stderr)
        return 1

    by_id: dict[str, dict[str, Any]] = {}
    for ans in records:
        if not isinstance(ans, dict):
            continue
        key = ans.get("id") or ans.get("sheet_name")
        if key:
            by_id[str(key)] = ans

    applied = 0
    validation_errors = 0
    for target in parsed:
        if not isinstance(target, dict):
            continue
        key = target.get("id") or target.get("sheet_name")
        ai_record = by_id.get(str(key)) if key else None
        if not ai_record:
            continue

        errors = _validate_record(ai_record)
        if errors and not args.force:
            print(f"[{key}] skipping due to {len(errors)} validation error(s):", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            validation_errors += 1
            continue

        _merge_classification(target, ai_record, judged_by, judged_at)
        applied += 1

    out_path = args.output or args.parsed
    out_path.write_text(json.dumps(parsed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"applied {applied} AI classification(s) to {out_path}; "
          f"validation errors: {validation_errors}")
    return 0 if validation_errors == 0 else 3


def cmd_migrate(args: argparse.Namespace) -> int:
    """Overwrite classification block in menu-index.json entries with AI batch."""
    index = json.loads(args.index.read_text(encoding="utf-8"))
    answers = json.loads(args.answers.read_text(encoding="utf-8"))

    if not isinstance(index, list):
        print("error: --index must be a JSON list of entries", file=sys.stderr)
        return 1

    judged_by = answers.get("judged_by", JUDGED_BY_DEFAULT) if isinstance(answers, dict) else JUDGED_BY_DEFAULT
    judged_at = answers.get("judged_at") if isinstance(answers, dict) else None
    judged_at = judged_at or datetime.now().astimezone().isoformat()

    records = answers.get("records") if isinstance(answers, dict) else answers
    if not isinstance(records, list):
        print("error: --answers must contain a list of records", file=sys.stderr)
        return 1

    by_id: dict[str, dict[str, Any]] = {}
    for ans in records:
        if isinstance(ans, dict) and ans.get("id"):
            by_id[str(ans["id"])] = ans

    updated = 0
    for entry in index:
        if not isinstance(entry, dict):
            continue
        eid = entry.get("id")
        if not eid or str(eid) not in by_id:
            continue
        ai_record = by_id[str(eid)]
        errors = _validate_record(ai_record)
        if errors and not args.force:
            print(f"[{eid}] skipping due to validation errors", file=sys.stderr)
            continue
        _merge_classification(entry, ai_record, judged_by, judged_at)

        canonical_zones, method_tags = _normalize_zone_tags(ai_record.get("zone_tags") or [])
        entry["zone_tags"] = canonical_zones
        entry["method_tags"] = method_tags
        phase_primary = _get_nested(ai_record, "phase.primary")
        phase_secondary = _get_nested(ai_record, "phase.secondary") or []
        if phase_primary:
            entry["phase_hints"] = [phase_primary] + [p for p in phase_secondary if p != phase_primary]
        method_primary = _get_nested(ai_record, "method.primary")
        if method_primary and not method_primary.startswith("custom_"):
            entry["method"] = method_primary
        intensity_level = _get_nested(ai_record, "intensity_signature.level")
        if intensity_level:
            entry["intensity_signature"] = intensity_level
        updated += 1

    args.index.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"migrated {updated} entries in {args.index}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """CLI parser."""
    parser = argparse.ArgumentParser(
        description="Apply AI classification (rubric v1) to parsed records or menu-index."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_val = sub.add_parser("validate", help="Validate AI classification answers against rubric.")
    p_val.add_argument("--answers", type=Path, required=True)
    p_val.set_defaults(func=cmd_validate)

    p_apply = sub.add_parser("apply", help="Merge AI classifications into parsed records JSON.")
    p_apply.add_argument("--parsed", type=Path, required=True)
    p_apply.add_argument("--answers", type=Path, required=True)
    p_apply.add_argument("--output", type=Path)
    p_apply.add_argument("--force", action="store_true",
                        help="Apply even when validation errors present.")
    p_apply.set_defaults(func=cmd_apply)

    p_mig = sub.add_parser("migrate", help="Overwrite menu-index.json entries with AI batch.")
    p_mig.add_argument("--index", type=Path, required=True)
    p_mig.add_argument("--answers", type=Path, required=True)
    p_mig.add_argument("--force", action="store_true")
    p_mig.set_defaults(func=cmd_migrate)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
