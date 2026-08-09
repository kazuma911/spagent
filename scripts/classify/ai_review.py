"""Emit / apply AI review batches for low-confidence classification records.

低信頼レコードだけを取り出して AI (Copilot / task agent) が処理しやすい形に整形する。

- `emit` サブコマンド: classified JSON から `confidence in {low}` を抽出し、
  {sheet_name, theme, body} だけの軽量 batch を出力。
- `apply` サブコマンド: AI が埋めた answers JSON を元の classified JSON に上書き。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


VALID_METHODS = {
    "endurance", "threshold", "vo2max", "sprint", "race-pace",
    "recovery", "mixed", "technique",
}


def condense_body(record: dict[str, Any], max_rows: int = 20) -> list[dict[str, Any]]:
    """Return a compact body for AI review: only real rows, at most max_rows."""
    rows: list[dict[str, Any]] = []
    for row in record.get("structure", []) or []:
        cat = str(row.get("category") or "").strip()
        desc = str(row.get("description") or "").strip()
        times = str(row.get("times") or "").strip()
        dist = str(row.get("distance") or "").strip()
        if not (cat or desc):
            continue
        rows.append({"cat": cat, "n": times, "m": dist, "d": desc[:200]})
        if len(rows) >= max_rows:
            break
    return rows


def cmd_emit(args: argparse.Namespace) -> int:
    """Extract low-confidence records into a batch file."""
    data = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        print("error: input must be a list", file=sys.stderr)
        return 1

    picked = []
    for record in data:
        if not isinstance(record, dict):
            continue
        cls = record.get("classification", {})
        if cls.get("confidence") not in {"low"}:
            continue
        picked.append({
            "sheet_name": record.get("sheet_name"),
            "date": record.get("date"),
            "theme": record.get("theme") or "",
            "total_distance": record.get("total_distance"),
            "current_method": cls.get("method"),
            "current_reason": cls.get("reason"),
            "body": condense_body(record),
        })

    args.output.write_text(json.dumps(picked, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(picked)} records to {args.output}")
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    """Merge AI answers back into the classified JSON."""
    data = json.loads(args.input.read_text(encoding="utf-8"))
    answers = json.loads(args.answers.read_text(encoding="utf-8"))
    if isinstance(answers, dict) and "answers" in answers:
        answers = answers["answers"]
    if not isinstance(answers, list):
        print("error: answers must be a list", file=sys.stderr)
        return 1

    by_key: dict[str, dict[str, Any]] = {}
    for ans in answers:
        if not isinstance(ans, dict):
            continue
        key = ans.get("sheet_name") or ans.get("id")
        if key:
            by_key[str(key)] = ans

    applied = 0
    skipped = 0
    for record in data:
        if not isinstance(record, dict):
            continue
        key = record.get("sheet_name")
        ans = by_key.get(str(key)) if key else None
        if not ans:
            continue
        method = str(ans.get("method") or "").strip()
        if method not in VALID_METHODS:
            skipped += 1
            continue
        cls = record.setdefault("classification", {})
        cls["method"] = method
        if isinstance(ans.get("zone_tags"), list):
            cls["zone_tags"] = sorted({str(z) for z in ans["zone_tags"] if z})
        cls["confidence"] = "ai-reviewed"
        cls["reason"] = f"AI: {str(ans.get('reason') or '')[:200]}"
        applied += 1

    out_path = args.output or args.input
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"applied {applied} AI answers; skipped {skipped} (invalid method)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """CLI parser with two subcommands."""
    parser = argparse.ArgumentParser(description="Emit / apply AI classification review batches.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_emit = sub.add_parser("emit", help="Extract low-confidence records into a batch file.")
    p_emit.add_argument("input", type=Path)
    p_emit.add_argument("--output", type=Path, required=True)
    p_emit.set_defaults(func=cmd_emit)

    p_apply = sub.add_parser("apply", help="Merge AI answers back into the classified JSON.")
    p_apply.add_argument("input", type=Path)
    p_apply.add_argument("--answers", type=Path, required=True)
    p_apply.add_argument("--output", type=Path)
    p_apply.set_defaults(func=cmd_apply)
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
