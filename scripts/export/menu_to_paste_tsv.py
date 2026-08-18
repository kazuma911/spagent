"""Emit a paste-ready TSV aligned to the coach's Excel Layout Descriptor v2.

**方針**: Excel の書式・数式・conditional formatting はコーチのテンプレートに任せ、
本スクリプトは「そのシートにコピペしたら意味が通る TSV」を生成する。

**出力**:

- ``menu.paste.tsv`` — 貼り付け専用。data 列だけ (formula 列は Excel 側で自動計算)
- ``menu.paste-instructions.md`` — 貼り付け手順、列意味、セクション/個別注記の書き方

**貼り付け手順** (instructions.md にも記載):

1. コーチのテンプレート xlsx を開く
2. 直近のシートを右クリック → 「移動またはコピー...」でコピーを作成、日付にリネーム
3. body 開始セル (例: B6) をクリック
4. ``menu.paste.tsv`` を開いて全選択 → コピー → Excel に貼り付け
5. formula 列 (subtotal / 変換 / block / elapsed) は自動計算される

**依存**: 標準ライブラリのみ。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

# Column canonical → human label (JP) fallback.
CANONICAL_TO_JP = {
    "category": "種目区分",
    "times": "本数",
    "distance": "距離",
    "set": "セット",
    "cycle": "サイクル",
    "description": "内容",
    "gears": "使用器具",
}


def repo_root() -> Path:
    """Return repository root."""
    return Path(__file__).resolve().parents[2]


def load_descriptor(path: Path) -> dict[str, Any]:
    """Load a Layout Descriptor v2 JSON."""
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_key(k: str) -> str:
    """menu.tsv のヘッダ表記揺れを canonical key に寄せる。

    例: `Category` → `category`, `WithGears`/`Gears` → `gears`, `Times`/`Reps` → `times`.
    canonical key と一致しないヘッダはそのまま lower() 済み文字列を返す。
    """
    s = k.strip().lower().replace(" ", "").replace("_", "")
    aliases = {
        "withgears": "gears",
        "equipment": "gears",
        "reps": "times",
        "count": "times",
        "dist": "distance",
        "desc": "description",
        "content": "description",
        "sets": "set",
    }
    return aliases.get(s, s)


def parse_menu_tsv(path: Path) -> tuple[dict[str, str], list[dict[str, Any]]]:
    """Parse `sessions/YYYY-MM-DD/menu.tsv` with `# meta`, `# section`, blank lines.

    - `# key: value` は meta として扱う
    - `# section: name` はセクション行 (`row_kind=section`)
    - 完全空行はブロック区切り (`row_kind=blank`)
    - それ以外は data 行 (最初のヘッダ行を列名として利用; canonical key に正規化)
    """
    meta: dict[str, str] = {}
    rows: list[dict[str, Any]] = []
    header: list[str] | None = None
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh, delimiter="\t")
        for raw in reader:
            if not raw or all((not c or not c.strip()) for c in raw):
                rows.append({"row_kind": "blank"})
                continue
            first = raw[0]
            if first.startswith("#"):
                text = first.lstrip("#").strip()
                if text.startswith("section:"):
                    rows.append({"row_kind": "section", "section_name": text.split(":", 1)[1].strip()})
                    continue
                if ":" in text:
                    k, v = text.split(":", 1)
                    meta[k.strip()] = v.strip()
                continue
            if header is None:
                header = [_normalize_key(c) for c in raw]
                continue
            row = {header[i] if i < len(header) else f"col{i}": (raw[i] if i < len(raw) else "") for i in range(len(raw))}
            row["row_kind"] = "data"
            rows.append(row)
    return meta, rows


def data_column_order(descriptor: dict[str, Any]) -> list[tuple[str, str, str]]:
    """Return only *input* data columns in physical (col letter) order.

    formula 列は Excel が自動計算するので除外する。
    戻り値: [(canonical_key, col_letter, header_label), ...]
    """
    columns = descriptor.get("table", {}).get("columns", {}) or {}
    result: list[tuple[str, str, str]] = []
    for key, spec in columns.items():
        col_letter = spec.get("col")
        if not col_letter:
            continue
        label = spec.get("header_label") or CANONICAL_TO_JP.get(key, key)
        result.append((key, col_letter, label))
    result.sort(key=lambda t: _col_idx(t[1]))
    return result


def _col_idx(letter: str) -> int:
    """Excel column letter → 0-based index."""
    idx = 0
    for ch in letter:
        idx = idx * 26 + (ord(ch.upper()) - ord("A") + 1)
    return idx - 1


def _format_cell(value: Any) -> str:
    """Format one cell for TSV. int-friendly numeric strings kept as-is."""
    if value is None:
        return ""
    s = str(value)
    return s.replace("\t", " ").replace("\n", " ").rstrip()


def emit_paste_tsv(
    order: list[tuple[str, str, str]],
    rows: list[dict[str, Any]],
    out_path: Path,
) -> int:
    """Write the paste-ready TSV. Return the number of data rows emitted."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n_data = 0
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        for row in rows:
            kind = row.get("row_kind", "data")
            if kind == "blank":
                fh.write("\t".join(["" for _ in order]) + "\n")
                continue
            if kind == "section":
                cells = [_format_cell(row.get("section_name", ""))] + ["" for _ in order[1:]]
                fh.write("\t".join(cells) + "\n")
                continue
            cells = [_format_cell(row.get(key, "")) for key, _, _ in order]
            fh.write("\t".join(cells) + "\n")
            n_data += 1
    return n_data


def emit_instructions(
    descriptor: dict[str, Any],
    order: list[tuple[str, str, str]],
    tsv_path: Path,
    md_path: Path,
    meta: dict[str, str],
) -> None:
    """Write a Markdown instructions file that explains how to paste the TSV."""
    table = descriptor.get("table", {}) or {}
    body_start = table.get("body_start_row", 6)
    header_row = table.get("header_row", 5)
    template_source = descriptor.get("template_source") or {}
    template_xlsx = template_source.get("xlsx_path", "(未検出)")
    template_sheet = template_source.get("sheet_name", "(未検出)")
    layout_id = descriptor.get("layout_id", "(unknown)")
    display_name = descriptor.get("display_name") or layout_id
    confidence = descriptor.get("confidence", 0.0)

    first_col_letter = order[0][1] if order else "B"
    paste_target = f"{first_col_letter}{body_start}"

    header_cells = descriptor.get("header_cells", {}) or {}
    ind_note = descriptor.get("individual_note") or {}
    section_rule = descriptor.get("section_header_rule") or {}
    formulas = descriptor.get("formulas", {}) or {}

    lines: list[str] = []
    lines.append(f"# 貼り付け手順 — {display_name}")
    lines.append("")
    lines.append(f"- **descriptor**: `{layout_id}` (confidence {confidence})")
    lines.append(f"- **貼り付け元**: `{tsv_path.name}`")
    lines.append(f"- **貼り付け先テンプレート**: `{template_xlsx}` シート `{template_sheet}` を複製")
    lines.append(f"- **貼り付け開始セル**: `{paste_target}` (body_start_row={body_start})")
    lines.append("")

    lines.append("## 手順 (Excel / Google Sheets 共通)")
    lines.append("")
    lines.append(f"1. コーチのテンプレート (`{template_xlsx}` 相当) を開く — Excel / Google Sheets どちらでも可")
    lines.append(f"2. シート `{template_sheet}` を複製 → 新シート名を今日の日付に")
    lines.append("   - Excel: シートタブを右クリック → 「移動またはコピー」 → **コピーを作成**")
    lines.append("   - Sheets: シートタブを右クリック → **「複製」**")
    lines.append("3. 新シート上部のヘッダブロック (チーム名/日付/場所/テーマ/器具) を今日の内容に手動更新")
    lines.append(f"4. セル `{paste_target}` をクリック")
    lines.append(f"5. `{tsv_path.name}` をテキストエディタで開き **全選択 → コピー** (または `--clipboard` オプションで自動)")
    lines.append("6. 貼り付け → formula 列 (I/J/K/L 等) はテンプレの数式が自動計算")
    lines.append("   - Excel Table (ListObject) は行を追加すると自動で数式を伸ばす")
    lines.append("   - Google Sheets の場合は数式列も一緒にドラッグコピーして伸ばす必要あり")
    lines.append("")

    lines.append("## 列マップ")
    lines.append("")
    lines.append("| 列 | canonical | header_label | 意味 |")
    lines.append("|---|---|---|---|")
    for key, col, label in order:
        meaning = CANONICAL_TO_JP.get(key, key)
        lines.append(f"| {col} | `{key}` | `{label}` | {meaning} |")
    lines.append("")
    lines.append("`I`/`J`/`K`/`L` 等の formula 列は貼り付けデータに含めない — Excel Table が自動で数式を伸ばす。")
    lines.append("")

    if formulas:
        lines.append("## Excel 側で自動計算される列")
        lines.append("")
        for name, spec in formulas.items():
            if not isinstance(spec, dict) or name in {"total_marker"}:
                continue
            col = spec.get("col", "-")
            typ = spec.get("type", "-")
            lines.append(f"- `{col}` **{name}** ({typ})")
        tm = formulas.get("total_marker") or {}
        if tm.get("template_row"):
            lines.append(f"- TOTAL 行: `{tm.get('column', 'F')}{tm['template_row']}` (テンプレの既存行を利用)")
        lines.append("")

    if header_cells:
        lines.append("## ヘッダブロック (手動記入)")
        lines.append("")
        for name, spec in header_cells.items():
            cell = spec.get("cell") if isinstance(spec, dict) else spec
            sample = spec.get("sample_value") if isinstance(spec, dict) else None
            hint = f"例: {sample}" if sample else ""
            lines.append(f"- `{cell}` **{name}** {hint}")
        lines.append("")

    if section_rule:
        target = section_rule.get("target_column", "B")
        lines.append("## セクション行の書き方")
        lines.append("")
        lines.append(f"- 列 `{target}` のみに文字列 (他列は空) → セクションヘッダとして扱う")
        examples = section_rule.get("examples") or []
        if examples:
            lines.append("- 例: " + " / ".join(f"`{ex}`" for ex in examples[:5]))
        lines.append("")

    if ind_note:
        opener = ind_note.get("opener", "【")
        closer = ind_note.get("closer", "】")
        col = ind_note.get("column", "G")
        lines.append("## 個別注記")
        lines.append("")
        lines.append(f"- 列 `{col}` の先頭に `{opener}選手名{closer}` を書くと個別注記として扱われる")
        lines.append(f"- 複数選手は `{opener}選手A・選手B{closer}` のように区切る")
        lines.append(f"- TOTAL 行の distance SUM から自動で減算される")
        lines.append("")

    lines.append("## meta (TSV 冒頭にあった値)")
    lines.append("")
    if meta:
        for k, v in meta.items():
            lines.append(f"- `{k}` = {v}")
    else:
        lines.append("- (なし)")
    lines.append("")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def copy_to_clipboard(path: Path) -> bool:
    """Copy the TSV file contents to the OS clipboard."""
    text = path.read_text(encoding="utf-8")
    try:
        if sys.platform.startswith("win"):
            proc = subprocess.Popen(["powershell", "-NoProfile", "-Command", "Set-Clipboard"], stdin=subprocess.PIPE)
            proc.communicate(text.encode("utf-16le"))
            return proc.returncode == 0
        if sys.platform == "darwin":
            proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            proc.communicate(text.encode("utf-8"))
            return proc.returncode == 0
        for cmd in (["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]):
            try:
                proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
                proc.communicate(text.encode("utf-8"))
                if proc.returncode == 0:
                    return True
            except FileNotFoundError:
                continue
        return False
    except Exception:
        return False


def open_file_with_default_app(path: Path) -> bool:
    """OS 既定アプリでファイルを開く。"""
    p = Path(path).resolve()
    if not p.exists():
        return False
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(p))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(p)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["xdg-open", str(p)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def build_parser() -> argparse.ArgumentParser:
    """CLI parser."""
    p = argparse.ArgumentParser(description="Emit a paste-ready TSV + instructions aligned to a coach's Excel Layout Descriptor.")
    p.add_argument("tsv", type=Path, help="Input menu.tsv path (with # meta / # section headers).")
    p.add_argument("--descriptor", type=Path, required=True, help="Excel Layout Descriptor v2 JSON.")
    p.add_argument("--out-tsv", type=Path, help="Output paste-ready TSV path (default: <tsv>.paste.tsv).")
    p.add_argument("--out-md", type=Path, help="Instructions markdown path (default: <tsv>.paste-instructions.md).")
    p.add_argument("--clipboard", action="store_true", help="Copy paste-ready TSV contents to the OS clipboard.")
    p.add_argument("--open", dest="open_after", action="store_true", default=True, help="Open the paste TSV + instructions after generation (default: on).")
    p.add_argument("--no-open", dest="open_after", action="store_false", help="Do not open files.")
    return p


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    args = build_parser().parse_args(argv)
    descriptor = load_descriptor(args.descriptor)
    meta, rows = parse_menu_tsv(args.tsv)
    order = data_column_order(descriptor)
    if not order:
        print("error: descriptor has no table.columns", file=sys.stderr)
        return 1

    out_tsv = args.out_tsv or args.tsv.with_suffix(".paste.tsv")
    out_md = args.out_md or args.tsv.with_name(args.tsv.stem + ".paste-instructions.md")

    n = emit_paste_tsv(order, rows, out_tsv)
    emit_instructions(descriptor, order, out_tsv, out_md, meta)
    print(f"tsv: {out_tsv} ({n} data rows)")
    print(f"instructions: {out_md}")

    if args.clipboard:
        ok = copy_to_clipboard(out_tsv)
        print(f"clipboard: {'copied' if ok else 'failed'}", file=sys.stderr)
    if args.open_after:
        open_file_with_default_app(out_md)
        open_file_with_default_app(out_tsv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
