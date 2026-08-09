"""Scan text files for possible PII.

テキストまたは JSON ファイルを行単位で読み、電話番号、メール、住所関連、
生年月日文脈などの個人情報らしいパターンを検出する。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass
class Finding:
    """Represent one PII finding.

    CI と人間向け出力の両方で使う検出結果。
    """

    line: int
    kind: str
    severity: str
    excerpt: str


BUILT_IN_PATTERNS: list[tuple[str, str, str, re.Pattern[str]]] = [
    ("email", "high", "email address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
    ("phone", "high", "Japanese phone number", re.compile(r"(?:\+81[-\s]?\d{1,4}|0\d{1,4})[-\s]?\d{1,4}[-\s]?\d{3,4}\b")),
    ("postal_code", "medium", "Japanese postal code", re.compile(r"(?:^|[^0-9\-])(?:〒\s*)?\d{3}-\d{4}\b")),
    ("credit_card", "critical", "credit card pattern", re.compile(r"\b(?:\d[ -]?){13,19}\b")),
    ("birth_date", "high", "birth date context", re.compile(r"(?:birth|birthday|dob|生年月日|誕生日).{0,16}\d{4}[-/]\d{1,2}[-/]\d{1,2}", re.IGNORECASE)),
    # jp_name: 「name / 氏名 / 名前 / 選手名」ラベル直後に 姓 + 名 の CJK 名っぽいパターン。
    # 区切りは 姓と名の間にある場合 (`山田 太郎`) もない場合 (`田中太郎`) もある。
    # エイリアス系ラベル (alias / group_name / group_id / nickname) は allowlist で除外する。
    ("jp_name", "medium", "Japanese full name (surname + given)", re.compile(r"(?<![A-Za-z_])(?:氏名|名前|選手名|フルネーム|full[_\s-]?name|real[_\s-]?name)[\"'\s:：,]+[\u4E00-\u9FFF]{2,4}[\s　・]*[\u4E00-\u9FFFァ-ヴー]{0,4}", re.IGNORECASE)),
    # kana_name: カナ姓 <sep>? カナ名。少なくとも 4 文字以上のカナ列（単一エイリアス `アリス` はキー allowlist で除外）。
    ("kana_name", "medium", "Katakana full name (surname + given)", re.compile(r"(?<![A-Za-z_])(?:氏名|名前|選手名|フルネーム|full[_\s-]?name|real[_\s-]?name)[\"'\s:：,]+[ァ-ヴー]{2,6}[\s　・]*[ァ-ヴー]{0,6}", re.IGNORECASE)),
]

# エイリアス・グループ名など、選手匿名 ID として TSV / JSON に載せて OK なラベル。
# これらのキー配下の行では jp_name / kana_name を発火させない。
ALIAS_LABEL_PATTERN = re.compile(
    r"(?:^|[\s,\"'])(alias(?:es)?|nickname|group[_\s-]?name|group[_\s-]?id|team[_\s-]?name|club[_\s-]?name|handle|display[_\s-]?name)[\s\"':：]",
    re.IGNORECASE,
)


def mask_excerpt(text: str, start: int, end: int) -> str:
    """Return a short masked excerpt.

    検出値そのものを全部表示しないように一部をマスクする。
    """
    snippet = text[max(0, start - 16) : min(len(text), end + 16)].strip()
    detected = text[start:end]
    if len(detected) <= 4:
        masked = "***"
    else:
        masked = detected[:2] + "***" + detected[-2:]
    return snippet.replace(detected, masked)


def luhn_valid(number_text: str) -> bool:
    """Validate a possible card number with Luhn checksum.

    偶然の長い数字列を減らすために利用する。
    """
    digits = [int(char) for char in re.sub(r"\D", "", number_text)]
    if len(digits) < 13:
        return False
    total = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def load_blocklist(path: Path | None) -> list[tuple[str, str, re.Pattern[str]]]:
    """Load custom blocklist patterns.

    JSON 配列、または `terms` / `patterns` を持つ JSON オブジェクトに対応する。
    """
    if path is None or not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    terms: list[str] = []
    patterns: list[str] = []
    if isinstance(data, list):
        terms = [str(item) for item in data]
    elif isinstance(data, dict):
        terms = [str(item) for item in data.get("terms", [])]
        patterns = [str(item) for item in data.get("patterns", [])]
    loaded: list[tuple[str, str, re.Pattern[str]]] = []
    for term in terms:
        if term:
            loaded.append(("custom_blocklist", "high", re.compile(re.escape(term), re.IGNORECASE)))
    for pattern in patterns:
        if pattern:
            loaded.append(("custom_pattern", "high", re.compile(pattern, re.IGNORECASE)))
    return loaded


def scan_lines(lines: Iterable[str], blocklist: list[tuple[str, str, re.Pattern[str]]]) -> list[Finding]:
    """Scan lines for built-in and custom PII patterns.

    検出結果には行番号、種別、重要度、マスク済み抜粋を含める。
    エイリアス系ラベル (alias / group_name / nickname 等) が同じ行にある場合、
    jp_name / kana_name は誤検出を避けるためスキップする。
    """
    findings: list[Finding] = []
    for line_no, line in enumerate(lines, start=1):
        line_has_alias_label = bool(ALIAS_LABEL_PATTERN.search(line))
        for kind, severity, label, pattern in BUILT_IN_PATTERNS:
            if line_has_alias_label and kind in ("jp_name", "kana_name"):
                continue
            for match in pattern.finditer(line):
                if kind == "credit_card" and not luhn_valid(match.group(0)):
                    continue
                findings.append(Finding(line_no, kind, severity, f"{label}: {mask_excerpt(line, match.start(), match.end())}"))
        for kind, severity, pattern in blocklist:
            for match in pattern.finditer(line):
                findings.append(Finding(line_no, kind, severity, mask_excerpt(line, match.start(), match.end())))
    return findings


def default_blocklist_path(target: Path) -> Path:
    """Return the default blocklist path.

    実行場所から `data/pii-blocklist.json` を推定する。
    """
    for parent in [target.resolve().parent, *target.resolve().parents]:
        candidate = parent / "data" / "pii-blocklist.json"
        if candidate.exists():
            return candidate
    return Path("data") / "pii-blocklist.json"


def print_findings(findings: list[Finding], as_json: bool) -> None:
    """Print findings for CLI users.

    `--json` の場合は JSON 配列、それ以外は行単位で表示する。
    """
    if as_json:
        print(json.dumps([asdict(finding) for finding in findings], ensure_ascii=False, indent=2))
        return
    if not findings:
        print("clean: no PII patterns found")
        return
    for finding in findings:
        print(f"line {finding.line}: {finding.severity}: {finding.kind}: {finding.excerpt}")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser.

    対象ファイル、ブロックリスト、JSON 出力フラグを定義する。
    """
    parser = argparse.ArgumentParser(description="Scan a text or JSON file for possible PII.")
    parser.add_argument("path", type=Path, help="Text or JSON file to scan.")
    parser.add_argument("--blocklist", type=Path, help="Custom blocklist JSON path.")
    parser.add_argument("--json", action="store_true", help="Emit JSON findings.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the PII scanner CLI.

    検出ありなら CI 用に終了コード 1 を返す。
    """
    args = build_parser().parse_args(argv)
    try:
        if not args.path.exists():
            raise FileNotFoundError(f"missing file: {args.path}")
        blocklist_path = args.blocklist or default_blocklist_path(args.path)
        blocklist = load_blocklist(blocklist_path)
        lines = args.path.read_text(encoding="utf-8").splitlines()
        findings = scan_lines(lines, blocklist)
        print_findings(findings, args.json)
        return 1 if findings else 0
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
