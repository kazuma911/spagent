"""Extract menu records from a text PDF.

pdfplumber でテキストを抽出し、Category / Times / Distance などのキーワードを
起点にメニュー構造へ変換する。スキャン PDF は画像処理スクリプトへ誘導する。
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


CATEGORY_RE = re.compile(
    r"^(Swim(?:\s*\(Main\))?|Drill|Kick|Pull|Rest|Kick\s*&\s*Pull|Main|W-?up|C-?down|Dryland|dryland|IM|Fly|Back|Br|Fr)\b",
    re.IGNORECASE,
)
_DATE_RE = re.compile(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})")
_FACILITY_HINT_RE = re.compile(
    r"(SCM|LCM|\d{2,3}\s*m|pool|プール|センター|アクアティクス|温水|ジム|体育館|施設|場所|facility)",
    re.IGNORECASE,
)
_THEME_HINT_RE = re.compile(
    r"(Phase\s*[A-Z]|D-\s*\d+|Taper|Threshold|Sprint|Recovery|Base|USRPT|Broken|Descending"
    r"|Aerobic|Race\s*Pace|Endurance|IM\s*day|VO2|EN[123]|SP[12]"
    r"|大会|試合|レース|基礎期|準備期|移行期|テーマ|theme)",
    re.IGNORECASE,
)


def extract_text_pages(path: Path) -> list[str]:
    """Extract text from each PDF page.

    テキストが取得できないページは空文字になる。
    """
    pdfplumber = import_pdfplumber()
    with pdfplumber.open(path) as pdf:
        return [page.extract_text() or "" for page in pdf.pages]


def parse_body_row(line: str) -> dict[str, Any] | None:
    """Parse one whitespace-separated body row that starts with a category.

    先頭にカテゴリ名がある行を Times / Distance / Set / Cycle / Description に分解する。
    """
    match = CATEGORY_RE.match(line)
    if not match:
        return None
    category = match.group(1)
    tail = line[match.end():].strip()
    tokens = re.split(r"\s+", tail) if tail else []

    times = distance = set_no = cycle = ""
    description_start = 0
    if tokens and re.fullmatch(r"\d+", tokens[0]):
        times = tokens[0]
        description_start = 1
    if len(tokens) > description_start and re.fullmatch(r"\d+", tokens[description_start]):
        distance = tokens[description_start]
        description_start += 1
    if len(tokens) > description_start and re.fullmatch(r"\d+", tokens[description_start]):
        set_no = tokens[description_start]
        description_start += 1
    if len(tokens) > description_start and re.match(r"^\d+['\"´:.]", tokens[description_start]):
        cycle = tokens[description_start]
        description_start += 1
    description = " ".join(tokens[description_start:])
    estimated_distance = 0
    if times and distance:
        try:
            estimated_distance = int(times) * int(distance)
        except ValueError:
            estimated_distance = int(distance) if distance.isdigit() else 0
    elif distance.isdigit():
        estimated_distance = int(distance)
    return {
        "category": category,
        "times": times,
        "distance": distance,
        "set": set_no,
        "cycle": cycle,
        "description": description,
        "estimated_distance": estimated_distance,
    }


def extract_meta_lines(lines: list[str]) -> dict[str, str]:
    """Extract team_name / date / facility / theme / equipment from header lines.

    先頭の数行に含まれる典型的なメタ情報を汎用ヒューリスティックで拾う。
    """
    meta: dict[str, str] = {}
    for line in lines[:12]:
        stripped = line.strip()
        if not stripped:
            continue
        equipment_match = re.search(r"equipment\s*[:：]?\s*(.+)", stripped, re.IGNORECASE)
        if equipment_match and "equipment" not in meta:
            meta["equipment"] = equipment_match.group(1).strip()
        if "date" not in meta:
            date_match = _DATE_RE.search(stripped)
            if date_match:
                y, m, d = date_match.groups()
                meta["date"] = f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
        if "facility" not in meta and _FACILITY_HINT_RE.search(stripped):
            if not re.search(r"equipment\s*[:：]", stripped, re.IGNORECASE):
                meta["facility"] = stripped
        if "theme" not in meta and _THEME_HINT_RE.search(stripped):
            if not re.search(r"equipment\s*[:：]", stripped, re.IGNORECASE):
                meta["theme"] = stripped
        if "team_name" not in meta and len(stripped) <= 12 and not _DATE_RE.search(stripped):
            if not _FACILITY_HINT_RE.search(stripped) and not _THEME_HINT_RE.search(stripped):
                meta["team_name"] = stripped
    return meta


def convert_pdf(path: Path) -> list[dict[str, Any]]:
    """Convert a PDF to menu JSON records.

    テキスト抽出が空の場合はスキャン画像として扱い、例外で案内する。
    メニュー本文はカテゴリキーワード起点で 1 行 1 セットに分割する。
    """
    pages = extract_text_pages(path)
    if not any(page.strip() for page in pages):
        raise RuntimeError("No text was extracted. If this is a scanned image PDF, use image_to_menu.py instead.")
    all_lines: list[str] = []
    for page_text in pages:
        all_lines.extend(page_text.splitlines())
    meta = extract_meta_lines(all_lines)
    structure: list[dict[str, Any]] = []
    for page_no, page_text in enumerate(pages, start=1):
        for line in page_text.splitlines():
            parsed = parse_body_row(line.strip())
            if parsed is None:
                continue
            parsed["set_no"] = str(len(structure) + 1)
            parsed["source_page"] = page_no
            structure.append(parsed)
    total_distance = sum(int(item.get("estimated_distance") or 0) for item in structure)
    return [
        {
            "id": f"{meta.get('date') or path.stem}-pdf",
            "title": meta.get("theme") or meta.get("team_name") or path.stem,
            "date": meta.get("date"),
            "team_name": meta.get("team_name"),
            "facility": meta.get("facility"),
            "theme": meta.get("theme"),
            "equipment": meta.get("equipment"),
            "total_distance": total_distance,
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
