"""Merge planned menu TSV and executed times TSV.

`sessions/YYYY-MM-DD/menu.tsv` と `times.tsv` を set_no または set 表記で照合し、
`menu-executed.json` を生成する。
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    """Return the repository root.

    スクリプトの位置からルートを推定する。
    """
    return Path(__file__).resolve().parents[2]


def normalize_header(value: str) -> str:
    """Normalize a TSV header.

    ヘッダ名を比較しやすい小文字キーへ変換する。
    """
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def read_tsv_table(path: Path) -> list[dict[str, str]]:
    """Read the first non-comment TSV table.

    コメントと空行を除き、最初の表を辞書リストに変換する。
    """
    lines: list[str] = []
    in_table = False
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        for raw_line in file:
            stripped = raw_line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                if in_table and stripped.lower().startswith("# _"):
                    break
                continue
            in_table = True
            lines.append(raw_line.rstrip("\n"))
    if not lines:
        return []
    reader = csv.DictReader(lines, delimiter="\t")
    return [
        {normalize_header(key or ""): (value or "").strip() for key, value in row.items()}
        for row in reader
        if any((value or "").strip() for value in row.values())
    ]


def match_key(row: dict[str, str], fallback_index: int) -> str:
    """Build a stable key for planned/actual matching.

    `set_no`、`set_label`、`set` の順に利用し、なければ行番号を使う。
    """
    for key in ("set_no", "set_label", "set", "no"):
        value = row.get(key)
        if value:
            return value.strip().lower()
    return str(fallback_index)


def merge_session(session_date: str, root: Path | None = None) -> dict[str, Any]:
    """Merge menu and times files for one session.

    出力は `sessions/YYYY-MM-DD/menu-executed.json` に保存する。
    """
    root = root or repo_root()
    session_dir = root / "sessions" / session_date
    menu_path = session_dir / "menu.tsv"
    times_path = session_dir / "times.tsv"
    if not menu_path.exists():
        raise FileNotFoundError(f"missing menu TSV: {menu_path}")
    if not times_path.exists():
        raise FileNotFoundError(f"missing times TSV: {times_path}")

    menu_rows = read_tsv_table(menu_path)
    time_rows = read_tsv_table(times_path)
    actual_by_key: dict[str, list[dict[str, str]]] = {}
    for index, row in enumerate(time_rows, start=1):
        actual_by_key.setdefault(match_key(row, index), []).append(row)

    merged_sets: list[dict[str, Any]] = []
    matched_actual_ids: set[int] = set()
    for index, planned in enumerate(menu_rows, start=1):
        key = match_key(planned, index)
        actual = actual_by_key.get(key, [])
        matched_actual_ids.update(id(item) for item in actual)
        merged_sets.append({"set_no": key, "planned": planned, "actual": actual})

    unmatched_actual = [row for row in time_rows if id(row) not in matched_actual_ids]
    result = {
        "id": f"{session_date}-executed",
        "date": session_date,
        "source_menu": str(menu_path.as_posix()),
        "source_times": str(times_path.as_posix()),
        "sets": merged_sets,
        "unmatched_actual": unmatched_actual,
    }
    out_path = session_dir / "menu-executed.json"
    with out_path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)
        file.write("\n")
    return {"out": str(out_path), "planned_sets": len(menu_rows), "actual_rows": len(time_rows)}


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser.

    日付引数だけを受け取る。
    """
    parser = argparse.ArgumentParser(description="Merge menu.tsv and times.tsv into menu-executed.json.")
    parser.add_argument("date", help="Session date in YYYY-MM-DD format.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the merge CLI.

    結果サマリを JSON で標準出力に出す。
    """
    args = build_parser().parse_args(argv)
    try:
        result = merge_session(args.date)
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
