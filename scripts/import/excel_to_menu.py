"""Convert Excel swim menus to JSON records.

Excel の title/date/facility/theme/header/body/TOTAL という慣習を読み取り、
メニュー JSON の配列として出力する。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable


HEADER_ALIASES = {
    "category": "category",
    "times": "times",
    "distance": "distance",
    "set": "set",
    "cycle": "cycle",
    "description": "description",
    "gears": "gears",
    "subtotal": "subtotal",
}


def import_openpyxl() -> Any:
    """Import openpyxl with a helpful error.

    依存がない場合はインストール方法を含む例外にする。
    """
    try:
        import openpyxl
    except ImportError as exc:
        raise RuntimeError("openpyxl is required. Install with: python -m pip install openpyxl") from exc
    return openpyxl


def normalize(value: Any) -> str:
    """Normalize a cell value for matching.

    空白や記号を削って小文字にする。
    """
    return re.sub(r"[^a-z0-9]+", "", str(value or "").strip().lower())


def text(value: Any) -> str:
    """Convert a cell value to display text.

    日付型は ISO 形式に変換する。
    """
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value).strip() if value is not None else ""


def row_values(row: Iterable[Any]) -> list[Any]:
    """Return raw values from a worksheet row.

    openpyxl の cell オブジェクトから値だけを取り出す。
    """
    return [cell.value for cell in row]


def find_header_row(ws: Any) -> int | None:
    """Find the likely menu header row.

    Category/Times/Distance などの見出しが複数ある行を探す。
    """
    for row in ws.iter_rows():
        values = row_values(row)
        hits = sum(1 for value in values if normalize(value) in HEADER_ALIASES)
        if hits >= 3:
            return row[0].row
    return None


def extract_meta(ws: Any, header_row: int | None) -> dict[str, str]:
    """Extract title, date, facility, and theme from rows above the header.

    先頭行からヘッダ直前までを慣習的なメタデータとして読む。
    """
    limit = (header_row or 6) - 1
    rows = [row_values(row) for row in ws.iter_rows(min_row=1, max_row=max(limit, 1))]
    first_values = [text(value) for row in rows for value in row if text(value)]
    meta: dict[str, str] = {}
    if first_values:
        meta["title"] = first_values[0]
    labels = {"date": ("date", "日付"), "facility": ("facility", "場所", "施設"), "theme": ("theme", "テーマ")}
    for row in rows:
        row_texts = [text(value) for value in row]
        joined = " ".join(row_texts).lower()
        for key, words in labels.items():
            if key in meta:
                continue
            if any(word in joined for word in words):
                non_empty = [value for value in row_texts if value]
                meta[key] = non_empty[-1] if non_empty else ""
    if "date" not in meta:
        for value in first_values:
            if re.search(r"\d{4}[-/.]\d{1,2}[-/.]\d{1,2}", value):
                meta["date"] = value[:10].replace("/", "-").replace(".", "-")
                break
    return meta


def safe_int(value: Any) -> int:
    """Extract an integer from a cell value.

    距離計算用に数値部分だけを取得する。
    """
    if isinstance(value, (int, float)):
        return int(value)
    match = re.search(r"\d+", str(value or ""))
    return int(match.group(0)) if match else 0


def parse_sheet(ws: Any, source_path: Path) -> dict[str, Any]:
    """Parse one worksheet as a menu record.

    TOTAL 行に到達したら本文の読み取りを終了する。
    """
    header_row = find_header_row(ws)
    meta = extract_meta(ws, header_row)
    structure: list[dict[str, Any]] = []
    if header_row is None:
        return {
            "id": f"{source_path.stem}-{ws.title}",
            "title": meta.get("title") or ws.title,
            "date": meta.get("date"),
            "facility": meta.get("facility"),
            "theme": meta.get("theme"),
            "total_distance": 0,
            "structure": structure,
            "source_type": "excel",
            "source_path": str(source_path),
            "sheet_name": ws.title,
            "warnings": ["header row was not detected"],
        }

    headers = [HEADER_ALIASES.get(normalize(cell.value), normalize(cell.value) or f"col_{cell.column}") for cell in ws[header_row]]
    for row in ws.iter_rows(min_row=header_row + 1):
        values = row_values(row)
        if not any(text(value) for value in values):
            continue
        if any(str(value).strip().upper() == "TOTAL" for value in values if value is not None):
            break
        item = {headers[index]: text(value) for index, value in enumerate(values) if index < len(headers)}
        if any(item.values()):
            item["set_no"] = str(len(structure) + 1)
            subtotal = safe_int(item.get("subtotal"))
            if not subtotal:
                subtotal = (safe_int(item.get("times")) or 1) * safe_int(item.get("distance"))
            item["estimated_distance"] = subtotal
            structure.append(item)
    total_distance = sum(safe_int(item.get("estimated_distance")) for item in structure)
    return {
        "id": f"{meta.get('date') or source_path.stem}-{ws.title}",
        "title": meta.get("title") or ws.title,
        "date": meta.get("date"),
        "facility": meta.get("facility"),
        "theme": meta.get("theme"),
        "total_distance": total_distance,
        "structure": structure,
        "source_type": "excel",
        "source_path": str(source_path),
        "sheet_name": ws.title,
    }


def convert_workbook(path: Path, sheet_name: str | None = None) -> list[dict[str, Any]]:
    """Convert workbook sheets to menu records.

    `--sheet-name` が指定された場合はそのシートだけを処理する。
    """
    openpyxl = import_openpyxl()
    workbook = openpyxl.load_workbook(path, data_only=True, read_only=False)
    worksheets = [workbook[sheet_name]] if sheet_name else list(workbook.worksheets)
    return [parse_sheet(ws, path) for ws in worksheets]


def write_output(records: list[dict[str, Any]], out_path: Path | None) -> None:
    """Write JSON output to file or stdout.

    `--out` があればファイル、なければ標準出力に出す。
    """
    payload = json.dumps(records, ensure_ascii=False, indent=2)
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser.

    Excel パス、出力先、対象シートを受け取る。
    """
    parser = argparse.ArgumentParser(description="Convert an Excel workbook to menu JSON.")
    parser.add_argument("path", type=Path, help="Input .xlsx path.")
    parser.add_argument("--out", type=Path, help="Output JSON file.")
    parser.add_argument("--sheet-name", help="Only convert one sheet.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the Excel menu converter.

    変換に失敗した場合は非ゼロ終了する。
    """
    args = build_parser().parse_args(argv)
    try:
        records = convert_workbook(args.path, args.sheet_name)
        write_output(records, args.out)
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
