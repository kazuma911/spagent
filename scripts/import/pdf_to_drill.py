"""Extract drill records from a text PDF.

pdfplumber で抽出したテキストを見出し単位に分け、ドリル候補 JSON を作る。
スキャン PDF の解析は画像処理スクリプトへ委譲する。
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

    依存がない場合はインストール方法を含む例外を出す。
    """
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError("pdfplumber is required. Install with: python -m pip install pdfplumber") from exc
    return pdfplumber


def extract_text(path: Path) -> str:
    """Extract all text from a PDF.

    テキスト抽出できない場合は空文字になる。
    """
    pdfplumber = import_pdfplumber()
    with pdfplumber.open(path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def split_sections(text: str) -> list[list[str]]:
    """Split PDF text into likely drill sections.

    空行や番号付き見出しを区切りとして扱う。
    """
    sections: list[list[str]] = []
    current: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if current:
                sections.append(current)
                current = []
            continue
        if current and re.match(r"^\d+[.)]\s+\S+", stripped):
            sections.append(current)
            current = [stripped]
        else:
            current.append(stripped)
    if current:
        sections.append(current)
    return sections


def parse_section(section: list[str], source_path: Path, index: int) -> dict[str, Any]:
    """Parse one text section as a drill record.

    先頭行をドリル名、残りを説明として扱う。
    """
    body = "\n".join(section[1:])
    focus_points = re.findall(r"(?:focus|point|key)[:：]\s*([^\n]+)", body, flags=re.IGNORECASE)
    mistakes = re.findall(r"(?:mistake|avoid)[:：]\s*([^\n]+)", body, flags=re.IGNORECASE)
    return {
        "id": f"{source_path.stem}-pdf-{index}",
        "name": re.sub(r"^\d+[.)]\s*", "", section[0]),
        "purpose": "",
        "description": body,
        "focus_points": focus_points,
        "common_mistakes": mistakes,
        "source_type": "pdf",
        "source_path": str(source_path),
    }


def convert_pdf(path: Path) -> list[dict[str, Any]]:
    """Convert a PDF to drill records.

    テキストが空なら image_to_drill.py の利用を促す。
    """
    text = extract_text(path)
    if not text.strip():
        raise RuntimeError("No text was extracted. If this is a scanned image PDF, use image_to_drill.py instead.")
    sections = [section for section in split_sections(text) if section]
    return [parse_section(section, path, index) for index, section in enumerate(sections, start=1)]


def write_output(records: list[dict[str, Any]], out_path: Path | None) -> None:
    """Write JSON output.

    `--out` があればファイルへ保存する。
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
    parser = argparse.ArgumentParser(description="Extract drill records from a text PDF.")
    parser.add_argument("path", type=Path, help="Input .pdf path.")
    parser.add_argument("--out", type=Path, help="Output JSON file.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the PDF drill converter.

    変換結果を JSON として出力する。
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
