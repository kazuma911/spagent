"""Extract menu records from a text PDF.

pdfplumber でテキストを抽出し、表らしい行を簡易ヒューリスティックで
メニュー構造に変換する。スキャン PDF は画像処理スクリプトへ誘導する。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def import_pdfplumber() -> Any:
    """Import pdfplumber with a helpful error.

    依存がない場合はインストール方法を含む例外にする。
    """
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError("pdfplumber is required. Install with: python -m pip install pdfplumber") from exc
    return pdfplumber


def split_row(line: str) -> list[str]:
    """Split a likely table line into columns.

    タブまたは複数空白を列区切りとして扱う。
    """
    return [part.strip() for part in re.split(r"\t+|\s{2,}", line.strip()) if part.strip()]


def parse_distance(parts: list[str]) -> int:
    """Estimate distance from row parts.

    `4 x 100` や `100` のような表記から距離を推定する。
    """
    text = " ".join(parts)
    repeat_match = re.search(r"(\d+)\s*[x×]\s*(\d+)", text, flags=re.IGNORECASE)
    if repeat_match:
        return int(repeat_match.group(1)) * int(repeat_match.group(2))
    numbers = [int(value) for value in re.findall(r"\b\d{2,4}\b", text)]
    return max(numbers) if numbers else 0


def extract_text_pages(path: Path) -> list[str]:
    """Extract text from each PDF page.

    テキストが取得できないページは空文字になる。
    """
    pdfplumber = import_pdfplumber()
    with pdfplumber.open(path) as pdf:
        return [page.extract_text() or "" for page in pdf.pages]


def convert_pdf(path: Path) -> list[dict[str, Any]]:
    """Convert a PDF to menu JSON records.

    テキスト抽出が空の場合はスキャン画像として扱い、例外で案内する。
    """
    pages = extract_text_pages(path)
    if not any(page.strip() for page in pages):
        raise RuntimeError("No text was extracted. If this is a scanned image PDF, use image_to_menu.py instead.")
    structure: list[dict[str, Any]] = []
    title = path.stem
    for page_no, page_text in enumerate(pages, start=1):
        for line in page_text.splitlines():
            parts = split_row(line)
            if len(parts) < 2:
                continue
            distance = parse_distance(parts)
            if distance == 0 and not re.search(r"warm|main|drill|kick|pull|down|swim", line, flags=re.IGNORECASE):
                continue
            structure.append(
                {
                    "set_no": str(len(structure) + 1),
                    "category": parts[0],
                    "description": " ".join(parts[1:]),
                    "estimated_distance": distance,
                    "source_page": page_no,
                }
            )
    return [
        {
            "id": f"{path.stem}-pdf",
            "title": title,
            "date": None,
            "total_distance": sum(item["estimated_distance"] for item in structure),
            "structure": structure,
            "source_type": "pdf",
            "source_path": str(path),
            "warnings": [] if structure else ["No clear table rows were detected; review extracted text manually."],
        }
    ]


def write_output(records: list[dict[str, Any]], out_path: Path | None) -> None:
    """Write JSON output.

    出力先が指定されない場合は標準出力に出す。
    """
    payload = json.dumps(records, ensure_ascii=False, indent=2)
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser.

    PDF パスと任意の出力先を受け取る。
    """
    parser = argparse.ArgumentParser(description="Extract menu records from a text PDF.")
    parser.add_argument("path", type=Path, help="Input .pdf path.")
    parser.add_argument("--out", type=Path, help="Output JSON file.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the PDF menu converter.

    スキャン PDF の場合は image_to_menu.py の利用を案内する。
    """
    args = build_parser().parse_args(argv)
    try:
        records = convert_pdf(args.path)
        write_output(records, args.out)
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
