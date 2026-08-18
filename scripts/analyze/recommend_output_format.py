"""Recommend output format for a menu based on past imports and coach preferences.

Workflow A の書き出し段階 (Step 17.5) で呼ぶ想定。以下のシグナルを重み付け合成:

- Coach preferences (`data/coach-preferences.json`)
    - preferred_output_format / preferred_layout_id (最優先ヒント)
- Layout Descriptor 群 (`data/excel-templates/*.json`)
    - v2 descriptor の confidence, detected_from, sample_sheets
- 出力履歴 (`coach-preferences.json` の output_history)
    - recency_half_life_days で減衰
- 対象グループ / 選手 (--group-or-athlete で渡す)
    - prefer_same_group 有効時、同一 group/athlete の履歴を強化

推奨は上位 3 件をスコア付き JSON で出力。Workflow A はコーチに提示 → 選択。

**依存**: 標準ライブラリのみ。
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any


DEFAULT_POLICY: dict[str, Any] = {
    "prefer_recent_imports": True,
    "recency_half_life_days": 90,
    "minimum_confidence": 0.7,
    "prefer_same_group": True,
}


def repo_root() -> Path:
    """Return repository root inferred from this script location."""
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict[str, Any] | None:
    """Load JSON with `None` on missing / broken files."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_coach_preferences(prefs_path: Path | None) -> dict[str, Any]:
    """Load coach preferences with sane defaults."""
    prefs = load_json(prefs_path) if prefs_path else None
    prefs = prefs or {}
    prefs.setdefault("preferred_output_format", "tsv")
    prefs.setdefault("preferred_layout_id", None)
    prefs.setdefault("auto_open_after_export", True)
    policy = {**DEFAULT_POLICY, **(prefs.get("layout_recommendation_policy") or {})}
    prefs["layout_recommendation_policy"] = policy
    prefs.setdefault("output_history", [])
    return prefs


def enumerate_layout_descriptors(templates_dir: Path) -> list[dict[str, Any]]:
    """Return every v2 layout descriptor found under `data/excel-templates/`."""
    if not templates_dir.exists():
        return []
    result: list[dict[str, Any]] = []
    for path in sorted(templates_dir.glob("*.json")):
        data = load_json(path)
        if not data:
            continue
        if str(data.get("$schema_version", "")).startswith("excel-layout-descriptor/v"):
            data["_path"] = str(path)
            data["_layout_id"] = data.get("layout_id") or path.stem
            result.append(data)
    return result


def days_between(iso_date_or_now: str | None, ref: date | None = None) -> float:
    """Return absolute day diff between an ISO date and today (or ref)."""
    ref = ref or date.today()
    if not iso_date_or_now:
        return math.inf
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            d = datetime.strptime(iso_date_or_now[:10], fmt).date()
            return abs((ref - d).days)
        except Exception:
            continue
    return math.inf


def recency_weight(days: float, half_life: float) -> float:
    """Exponential decay: 1.0 at day 0, 0.5 at half_life."""
    if not math.isfinite(days) or half_life <= 0:
        return 0.0
    return 0.5 ** (days / half_life)


def score_layout(
    descriptor: dict[str, Any],
    prefs: dict[str, Any],
    group_or_athlete: str | None,
) -> tuple[float, dict[str, Any]]:
    """Score a single Layout Descriptor.

    Signals:
    - confidence (0-1)
    - preferred_layout_id match → +0.5
    - most recent output_history entry with this layout → +recency_weight
    - prefer_same_group + matching group_or_athlete in history → +0.2
    """
    policy = prefs["layout_recommendation_policy"]
    confidence = float(descriptor.get("confidence") or 0.0)
    layout_id = descriptor["_layout_id"]

    breakdown: dict[str, float] = {"confidence": confidence}
    total = confidence

    if prefs.get("preferred_layout_id") == layout_id:
        breakdown["preferred_layout_id_match"] = 0.5
        total += 0.5

    if policy.get("prefer_recent_imports"):
        history = prefs.get("output_history") or []
        matching = [h for h in history if h.get("layout_id") == layout_id]
        if matching:
            most_recent_days = min(days_between(h.get("date")) for h in matching)
            r = recency_weight(most_recent_days, policy.get("recency_half_life_days", 90))
            breakdown["recency_bonus"] = r
            total += r

            if policy.get("prefer_same_group") and group_or_athlete:
                if any(h.get("group_or_athlete") == group_or_athlete for h in matching):
                    breakdown["same_group_bonus"] = 0.2
                    total += 0.2

    below_min = confidence < policy.get("minimum_confidence", 0.7)
    return total, {"breakdown": breakdown, "below_min_confidence": below_min}


def recommend(
    prefs_path: Path,
    templates_dir: Path,
    group_or_athlete: str | None = None,
    top_n: int = 3,
) -> dict[str, Any]:
    """Return ranked recommendations plus non-Excel format alternatives."""
    prefs = load_coach_preferences(prefs_path)
    descriptors = enumerate_layout_descriptors(templates_dir)

    ranked: list[dict[str, Any]] = []
    for d in descriptors:
        score, meta = score_layout(d, prefs, group_or_athlete)
        ranked.append(
            {
                "format": "excel_layout",
                "layout_id": d["_layout_id"],
                "display_name": d.get("display_name") or d["_layout_id"],
                "descriptor_path": d["_path"],
                "score": round(score, 3),
                "confidence": d.get("confidence"),
                "detected_from": d.get("detected_from"),
                **meta,
            }
        )

    ranked.sort(key=lambda r: r["score"], reverse=True)

    baseline = [
        {
            "format": "paste_tsv",
            "layout_id": None,
            "display_name": "Paste-ready TSV (menu.paste.tsv) + instructions",
            "score": 0.4 + (0.4 if prefs["preferred_output_format"] == "paste_tsv" else 0),
            "note": "requires a Layout Descriptor; combines best with #1 layout above",
        },
        {
            "format": "tsv",
            "layout_id": None,
            "display_name": "Plain TSV (sessions/YYYY-MM-DD/menu.tsv)",
            "score": 0.5 + (0.3 if prefs["preferred_output_format"] == "tsv" else 0),
            "note": "always available; needed for downstream indexing",
        },
        {
            "format": "pdf",
            "layout_id": None,
            "display_name": "PDF (print-ready)",
            "score": 0.3 + (0.3 if prefs["preferred_output_format"] == "pdf" else 0),
            "note": "requires scripts/export/menu_to_pdf.py",
        },
    ]

    combined = ranked + baseline
    combined.sort(key=lambda r: r["score"], reverse=True)
    top = combined[:top_n]

    return {
        "recommended": top[0] if top else None,
        "alternatives": top[1:],
        "coach_preferences": {
            "preferred_output_format": prefs["preferred_output_format"],
            "preferred_layout_id": prefs.get("preferred_layout_id"),
            "auto_open_after_export": prefs.get("auto_open_after_export", True),
        },
        "group_or_athlete": group_or_athlete,
        "all_layouts_found": len(descriptors),
    }


def build_parser() -> argparse.ArgumentParser:
    """CLI parser."""
    p = argparse.ArgumentParser(description="Recommend menu output format based on past imports and coach preferences.")
    p.add_argument("--prefs", type=Path, default=None, help="coach-preferences.json path (default: data/coach-preferences.json).")
    p.add_argument("--templates-dir", type=Path, default=None, help="Excel Layout Descriptor directory (default: data/excel-templates/).")
    p.add_argument("--group-or-athlete", default=None, help="Target group slug or athlete name to weight recent same-target imports.")
    p.add_argument("--top", type=int, default=3, help="Top N recommendations (default 3).")
    return p


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint. Emits JSON to stdout."""
    args = build_parser().parse_args(argv)
    root = repo_root()
    prefs_path = args.prefs or (root / "data" / "coach-preferences.json")
    templates_dir = args.templates_dir or (root / "data" / "excel-templates")
    result = recommend(prefs_path, templates_dir, group_or_athlete=args.group_or_athlete, top_n=args.top)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
