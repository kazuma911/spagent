"""Render a session TSV menu to PDF.

`sessions/YYYY-MM-DD/menu.tsv` を reportlab で読みやすい PDF に変換する。
pace table セクションがあれば別表として出力する。
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Any


def import_reportlab() -> dict[str, Any]:
    """Import reportlab pieces with a helpful error.

    依存がない場合はインストール方法を含む例外にする。
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError as exc:
        raise RuntimeError("reportlab is required. Install with: python -m pip install reportlab") from exc
    return {
        "colors": colors,
        "pagesize": landscape(A4),
        "getSampleStyleSheet": getSampleStyleSheet,
        "Paragraph": Paragraph,
        "SimpleDocTemplate": SimpleDocTemplate,
        "Spacer": Spacer,
        "Table": Table,
        "TableStyle": TableStyle,
    }


def normalize_key(value: str) -> str:
    """Normalize metadata keys.

    コメントメタデータのキーを小文字で扱う。
    """
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def parse_tsv_sections(path: Path) -> tuple[dict[str, str], list[list[str]], list[list[str]], list[str]]:
    """Parse menu, pace table, and notes from TSV.

    `# _pace_table` と `# _notes` セクションを特別扱いする。
    """
    meta: dict[str, str] = {}
    menu_lines: list[str] = []
    pace_lines: list[str] = []
    notes: list[str] = []
    section = "menu"
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        for raw_line in file:
            line = raw_line.rstrip("\n")
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                marker = stripped.lower()
                if marker.startswith("# _pace_table"):
                    section = "pace"
                    continue
                if marker.startswith("# _notes"):
                    section = "notes"
                    continue
                text = stripped.lstrip("#").strip()
                if ":" in text:
                    key, value = text.split(":", 1)
                    meta[normalize_key(key)] = value.strip()
                continue
            if section == "pace":
                pace_lines.append(line)
            elif section == "notes":
                notes.append(line)
            else:
                menu_lines.append(line)

    def read(lines: list[str]) -> list[list[str]]:
        return list(csv.reader(lines, delimiter="\t")) if lines else []

    return meta, read(menu_lines), read(pace_lines), notes


def style_table(table: Any, reportlab: dict[str, Any]) -> None:
    """Apply common table styling.

    ヘッダ背景、罫線、余白を設定する。
    """
    colors = reportlab["colors"]
    table_style = reportlab["TableStyle"]
    table.setStyle(
        table_style(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )


def convert_tsv_to_pdf(path: Path, out_path: Path | None = None) -> Path:
    """Convert a TSV menu to PDF.

    出力先省略時は入力ファイルと同じディレクトリに `.pdf` で保存する。
    """
    reportlab = import_reportlab()
    meta, menu_rows, pace_rows, notes = parse_tsv_sections(path)
    out_path = out_path or path.with_suffix(".pdf")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    styles = reportlab["getSampleStyleSheet"]()
    story: list[Any] = []
    paragraph = reportlab["Paragraph"]
    spacer = reportlab["Spacer"]
    table_cls = reportlab["Table"]
    document = reportlab["SimpleDocTemplate"](str(out_path), pagesize=reportlab["pagesize"])

    title = meta.get("title") or f"Swim menu {path.stem}"
    header = " / ".join(value for value in [meta.get("date"), meta.get("facility"), meta.get("theme")] if value)
    story.append(paragraph(title, styles["Title"]))
    if header:
        story.append(paragraph(header, styles["Normal"]))
    story.append(spacer(1, 8))
    if menu_rows:
        table = table_cls(menu_rows, repeatRows=1)
        style_table(table, reportlab)
        story.append(table)
    if pace_rows:
        story.append(spacer(1, 12))
        story.append(paragraph("Pace table", styles["Heading2"]))
        pace_table = table_cls(pace_rows, repeatRows=1)
        style_table(pace_table, reportlab)
        story.append(pace_table)
    if notes:
        story.append(spacer(1, 12))
        story.append(paragraph("Notes", styles["Heading2"]))
        for note in notes:
            story.append(paragraph(note, styles["Normal"]))
    document.build(story)
    return out_path


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser.

    入力 TSV と任意の PDF 出力先を受け取る。
    """
    parser = argparse.ArgumentParser(description="Convert a session menu TSV to PDF.")
    parser.add_argument("path", type=Path, help="Input menu.tsv path.")
    parser.add_argument("--out", type=Path, help="Output PDF path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the PDF export CLI.

    成功時は出力パスを表示する。
    """
    args = build_parser().parse_args(argv)
    try:
        out_path = convert_tsv_to_pdf(args.path, args.out)
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
