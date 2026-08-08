"""Import session menu TSV files into the custom menu index.

`sessions/YYYY-MM-DD/menu.tsv` を解析し、`knowledge/custom/menu-index.json`
に実施ベースのメニューとして追加する。
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

    スクリプトの位置からリポジトリルートを推定する。
    """
    return Path(__file__).resolve().parents[2]


def normalize_header(value: str) -> str:
    """Normalize a TSV header name.

    大文字小文字や空白を吸収して snake_case 風のキーにする。
    """
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def safe_int(value: Any) -> int:
    """Extract an integer from a loose value.

    距離・本数などの文字列から数値を取り出す。
    """
    if isinstance(value, (int, float)):
        return int(value)
    match = re.search(r"\d+", str(value or ""))
    return int(match.group(0)) if match else 0


def parse_meta_line(line: str) -> tuple[str, str] | None:
    """Parse a comment metadata line.

    `# key: value` 形式の行をメタデータとして扱う。
    """
    text = line.lstrip("#").strip()
    if not text or text.startswith("_"):
        return None
    if ":" in text:
        key, value = text.split(":", 1)
    elif "\t" in text:
        key, value = text.split("\t", 1)
    else:
        return None
    return normalize_header(key), value.strip()


def read_primary_tsv(path: Path) -> tuple[dict[str, str], list[dict[str, str]]]:
    """Read metadata and the first table from a session TSV.

    `# _pace_table` 以降のセクションは主メニューではないため除外する。
    """
    meta: dict[str, str] = {}
    table_lines: list[str] = []
    in_table = False
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        for raw_line in file:
            line = raw_line.rstrip("\n")
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                parsed = parse_meta_line(stripped)
                if parsed:
                    meta[parsed[0]] = parsed[1]
                if stripped.lower().startswith("# _"):
                    if in_table:
                        break
                continue
            in_table = True
            table_lines.append(line)
    if not table_lines:
        return meta, []
    reader = csv.DictReader(table_lines, delimiter="\t")
    rows: list[dict[str, str]] = []
    for row in reader:
        normalized = {normalize_header(key or ""): (value or "").strip() for key, value in row.items()}
        if any(normalized.values()):
            rows.append(normalized)
    return meta, rows


def row_distance(row: dict[str, str]) -> int:
    """Estimate one row's distance.

    Subtotal があれば優先し、なければ Times × Distance を使う。
    """
    subtotal = safe_int(row.get("subtotal"))
    if subtotal:
        return subtotal
    times = safe_int(row.get("times") or row.get("repeats") or 1) or 1
    distance = safe_int(row.get("distance"))
    return times * distance


def parse_menu_tsv(path: Path, session_date: str) -> dict[str, Any]:
    """Parse a menu TSV into a menu-index record.

    TSV の各行を `structure` のブロックとして保持する。
    """
    meta, rows = read_primary_tsv(path)
    structure: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        block = {
            "set_no": str(row.get("set_no") or row.get("set") or index),
            "category": row.get("category", ""),
            "times": row.get("times", ""),
            "distance": row.get("distance", ""),
            "set": row.get("set", ""),
            "cycle": row.get("cycle", ""),
            "description": row.get("description", ""),
            "gears": row.get("gears", ""),
            "subtotal": row.get("subtotal", ""),
        }
        block["estimated_distance"] = row_distance(row)
        structure.append(block)
    total_distance = sum(safe_int(item.get("estimated_distance")) for item in structure)
    return {
        "id": f"{session_date}-agent-tsv",
        "date": session_date,
        "title": meta.get("title") or meta.get("theme") or f"Session menu {session_date}",
        "facility": meta.get("facility"),
        "theme": meta.get("theme"),
        "total_distance": total_distance,
        "structure": structure,
        "source_type": "agent_tsv",
        "source_path": str(path.as_posix()),
    }


def load_menu_index(path: Path) -> list[dict[str, Any]]:
    """Load the menu index JSON.

    `knowledge/custom/menu-index.json` を読み込み、ファイルがなければ空配列を返す。
    """
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return [item for item in data if isinstance(item, dict)]


def save_menu_index(path: Path, entries: list[dict[str, Any]]) -> None:
    """Save the menu index JSON.

    親ディレクトリを作成し、UTF-8 JSON で保存する。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(entries, file, ensure_ascii=False, indent=2)
        file.write("\n")


def import_menu(session_date: str, root: Path | None = None) -> dict[str, Any]:
    """Import one dated session menu and retag the index.

    同じ `id` の既存レコードは置き換えて重複を防ぐ。
    """
    root = root or repo_root()
    menu_path = root / "sessions" / session_date / "menu.tsv"
    if not menu_path.exists():
        raise FileNotFoundError(f"missing TSV: {menu_path}")
    index_path = root / "knowledge" / "custom" / "menu-index.json"
    record = parse_menu_tsv(menu_path, session_date)
    entries = [entry for entry in load_menu_index(index_path) if entry.get("id") != record["id"]]
    entries.append(record)
    entries.sort(key=lambda item: str(item.get("date", "")))
    save_menu_index(index_path, entries)

    script_dir = Path(__file__).resolve().parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    import tag_zones_phases

    tag_summary = tag_zones_phases.retag_menu_index(root=root)
    return {"imported_id": record["id"], "index_path": str(index_path), "tag_summary": tag_summary}


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser.

    `YYYY-MM-DD` の日付引数を受け取る。
    """
    parser = argparse.ArgumentParser(description="Import sessions/YYYY-MM-DD/menu.tsv into menu-index.json.")
    parser.add_argument("date", help="Session date in YYYY-MM-DD format.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the import CLI.

    取り込み失敗時は stderr に理由を表示する。
    """
    args = build_parser().parse_args(argv)
    try:
        result = import_menu(args.date)
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
