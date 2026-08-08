"""Tag menu index entries with training zones and phase hints.

`knowledge/custom/menu-index.json` を読み込み、キーワードに基づく
`zone_tags` と、大会日程から推定した `phase_hint` を付与する。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any


ZONES = ("EN1", "EN2", "EN3", "SP1", "SP2", "SP3")

ZONE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "EN1": ("easy", "recovery", "loosen", "cooldown", "cool-down", "down"),
    "EN2": ("aerobic base", "aerobic", "endurance", "steady", "long swim"),
    "EN3": ("threshold", "t-pace", "t30", "tempo", "critical speed"),
    "SP1": ("vo2", "vo2max", "3-6min all-out", "3-6 min all-out", "anaerobic endurance"),
    "SP2": ("race pace", "sprint 50", "broken", "pace 50", "specific pace"),
    "SP3": ("all-out 25", "speed", "max speed", "power", "start dash"),
}


def repo_root() -> Path:
    """Return the repository root.

    スクリプトの場所からリポジトリルートを推定する。
    """
    return Path(__file__).resolve().parents[2]


def load_json_list(path: Path) -> list[dict[str, Any]]:
    """Load a JSON list from disk.

    ファイルが存在しない場合は空リストを返す。
    """
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return [item for item in data if isinstance(item, dict)]


def write_json_list(path: Path, entries: list[dict[str, Any]]) -> None:
    """Write a JSON list with stable formatting.

    親ディレクトリを作成し、UTF-8 JSON として保存する。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(entries, file, ensure_ascii=False, indent=2)
        file.write("\n")


def entry_text(entry: dict[str, Any]) -> str:
    """Build searchable text for one menu entry.

    構造化メニューのカテゴリ、説明、手法などを連結する。
    """
    parts: list[str] = []
    for key in ("title", "theme", "method", "description", "notes"):
        value = entry.get(key)
        if value:
            parts.append(str(value))
    for block in entry.get("structure", []) or []:
        if isinstance(block, dict):
            parts.extend(str(block.get(key, "")) for key in ("category", "set", "description", "gears", "method"))
    return " ".join(parts).lower()


def infer_zone_tags(entry: dict[str, Any]) -> list[str]:
    """Infer zone tags from menu text.

    `ZONE_KEYWORDS` の単純なキーワード一致で EN1〜SP3 を推定する。
    """
    text = entry_text(entry)
    tags: list[str] = []
    for zone, keywords in ZONE_KEYWORDS.items():
        if any(keyword.lower() in text for keyword in keywords):
            tags.append(zone)
    if not tags:
        distance = safe_int(entry.get("total_distance"))
        if distance >= 3500:
            tags.append("EN2")
        elif 0 < distance <= 1800:
            tags.append("EN1")
    return tags


def safe_int(value: Any) -> int:
    """Convert a value to int when possible.

    距離や回数の文字列から数値部分を取り出す。
    """
    if isinstance(value, (int, float)):
        return int(value)
    match = re.search(r"\d+", str(value or ""))
    return int(match.group(0)) if match else 0


def parse_date(value: Any) -> date | None:
    """Parse a date-like value.

    ISO 形式または YYYY/MM/DD 形式を日付に変換する。
    """
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    text = str(value or "").strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(text[:10], fmt).date()
        except ValueError:
            continue
    return None


def load_priority_a_competitions(root: Path) -> list[dict[str, Any]]:
    """Load priority A competitions.

    `data/competitions.json` がない場合は空リストを返す。
    """
    path = root / "data" / "competitions.json"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    items = data if isinstance(data, list) else data.get("competitions", []) if isinstance(data, dict) else []
    return [item for item in items if isinstance(item, dict) and str(item.get("priority", "")).upper() == "A"]


def infer_phase_hint(entry: dict[str, Any], competitions: list[dict[str, Any]]) -> str | None:
    """Infer phase hint from the closest priority A competition.

    大会情報がない場合は `None` を返す。
    """
    menu_date = parse_date(entry.get("date"))
    if menu_date is None or not competitions:
        return None
    upcoming: list[tuple[int, dict[str, Any]]] = []
    for competition in competitions:
        comp_date = parse_date(competition.get("start_date") or competition.get("date"))
        if comp_date is None:
            continue
        days = (comp_date - menu_date).days
        if days >= 0:
            upcoming.append((days, competition))
    if not upcoming:
        return None
    days_to_comp = min(upcoming, key=lambda item: item[0])[0]
    weeks = days_to_comp / 7
    if weeks <= 2:
        return "D"
    if weeks <= 6:
        return "C"
    if weeks <= 12:
        return "B"
    return "A"


def tag_entries(entries: list[dict[str, Any]], competitions: list[dict[str, Any]], force: bool = False) -> int:
    """Tag entries in place and return the updated count.

    `force=True` の場合は既存タグも再計算する。
    """
    updated = 0
    for entry in entries:
        changed = False
        if force or not entry.get("zone_tags"):
            entry["zone_tags"] = infer_zone_tags(entry)
            changed = True
        if force or "phase_hint" not in entry or entry.get("phase_hint") in ("", None):
            entry["phase_hint"] = infer_phase_hint(entry, competitions)
            changed = True
        if changed:
            updated += 1
    return updated


def retag_menu_index(
    root: Path | None = None,
    include_seed: bool = False,
    force: bool = False,
    write: bool = True,
) -> dict[str, int]:
    """Retag menu indexes and optionally persist custom entries.

    通常は custom 索引のみを書き戻す。seed は確認用に読み込むが変更しない。
    """
    root = root or repo_root()
    custom_path = root / "knowledge" / "custom" / "menu-index.json"
    seed_path = root / "knowledge" / "base" / "menu-index.seed.json"
    competitions = load_priority_a_competitions(root)
    custom_entries = load_json_list(custom_path)
    custom_updated = tag_entries(custom_entries, competitions, force=force)
    seed_updated = 0
    if include_seed:
        seed_entries = load_json_list(seed_path)
        seed_updated = tag_entries(seed_entries, competitions, force=force)
    if write:
        write_json_list(custom_path, custom_entries)
    return {
        "custom_entries": len(custom_entries),
        "custom_updated": custom_updated,
        "seed_entries_checked": len(load_json_list(seed_path)) if include_seed and seed_path.exists() else 0,
        "seed_updated_preview": seed_updated,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser.

    CLI 引数を定義する。
    """
    parser = argparse.ArgumentParser(description="Tag menu indexes with zone_tags and phase_hint.")
    parser.add_argument("--include-seed", action="store_true", help="Also inspect base seed entries without writing them.")
    parser.add_argument("--force", action="store_true", help="Recompute existing tags and phase hints.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the tagger CLI.

    エラー時は stderr に表示し非ゼロ終了する。
    """
    args = build_parser().parse_args(argv)
    try:
        summary = retag_menu_index(include_seed=args.include_seed, force=args.force)
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
