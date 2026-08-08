"""Analyze tendencies in menu index records.

`menu-index.json` から Zone 配分、距離帯、手法頻度、メニュー骨格パターン、
想定対象層を集計する。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ZONES = ("EN1", "EN2", "EN3", "SP1", "SP2", "SP3")
METHOD_KEYWORDS = {
    "threshold": ("threshold", "t-pace", "t30", "tempo"),
    "broken": ("broken", "split rest"),
    "descending": ("descending", "descend", "build"),
    "usrpt": ("usrpt", "race pace"),
    "hiit": ("hiit", "high intensity"),
    "lsd": ("lsd", "long slow distance"),
    "fartlek": ("fartlek", "variable pace"),
    "sprint": ("sprint", "speed", "all-out"),
}


def repo_root() -> Path:
    """Return the repository root.

    スクリプトの場所からリポジトリルートを推定する。
    """
    return Path(__file__).resolve().parents[2]


def safe_int(value: Any) -> int:
    """Convert a loose value to int.

    数字を含む文字列から距離を取り出す。
    """
    if isinstance(value, (int, float)):
        return int(value)
    match = re.search(r"\d+", str(value or ""))
    return int(match.group(0)) if match else 0


def load_menus(path: Path) -> list[dict[str, Any]]:
    """Load menu index records.

    JSON 配列以外の場合はエラーにする。
    """
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return [item for item in data if isinstance(item, dict)]


def menu_text(menu: dict[str, Any]) -> str:
    """Build searchable text for method detection.

    メニュー本文・カテゴリ・説明を連結する。
    """
    parts = [str(menu.get(key, "")) for key in ("title", "theme", "method", "description")]
    for block in menu.get("structure", []) or []:
        if isinstance(block, dict):
            parts.extend(str(block.get(key, "")) for key in ("category", "description", "set", "method"))
    return " ".join(parts).lower()


def zone_distribution(menus: list[dict[str, Any]]) -> dict[str, float]:
    """Compute average zone percentage across menus.

    1 メニュー内のタグを均等重みとして平均する。
    """
    totals = Counter({zone: 0.0 for zone in ZONES})
    if not menus:
        return {zone: 0.0 for zone in ZONES}
    for menu in menus:
        tags = [tag for tag in menu.get("zone_tags", []) if tag in ZONES]
        if not tags:
            continue
        weight = 1.0 / len(tags)
        for tag in tags:
            totals[tag] += weight
    return {zone: round((totals[zone] / len(menus)) * 100, 2) for zone in ZONES}


def distance_histogram(menus: list[dict[str, Any]], bin_size: int = 500) -> dict[str, int]:
    """Build a total-distance histogram.

    500m 単位で距離帯を集計する。
    """
    histogram: Counter[str] = Counter()
    for menu in menus:
        distance = safe_int(menu.get("total_distance"))
        start = (distance // bin_size) * bin_size
        end = start + bin_size - 1
        histogram[f"{start}-{end}m"] += 1
    return dict(histogram)


def method_frequency(menus: list[dict[str, Any]]) -> dict[str, int]:
    """Count explicit and inferred training methods.

    `method` フィールドがあれば優先し、なければキーワードで推定する。
    """
    counter: Counter[str] = Counter()
    for menu in menus:
        explicit = str(menu.get("method", "")).strip().lower()
        if explicit:
            counter[explicit] += 1
            continue
        text = menu_text(menu)
        matched = False
        for method, keywords in METHOD_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                counter[method] += 1
                matched = True
        if not matched:
            counter["unspecified"] += 1
    return dict(counter.most_common())


def block_distance(block: dict[str, Any]) -> int:
    """Estimate distance for one block.

    `subtotal`、`estimated_distance`、または Times × Distance を利用する。
    """
    for key in ("subtotal", "estimated_distance"):
        value = safe_int(block.get(key))
        if value:
            return value
    times = safe_int(block.get("times")) or 1
    return times * safe_int(block.get("distance"))


def skeleton_patterns(menus: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Extract top menu skeleton patterns.

    category の並びで単純クラスタ化し、上位 2〜4 パターンを返す。
    """
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for menu in menus:
        structure = [block for block in menu.get("structure", []) or [] if isinstance(block, dict)]
        sequence = tuple(str(block.get("category") or "Unknown").strip() or "Unknown" for block in structure)
        if sequence:
            groups[sequence].append(menu)
    ranked = sorted(groups.items(), key=lambda item: len(item[1]), reverse=True)
    if not ranked:
        return []
    limit = max(2, min(4, len(ranked)))
    patterns: list[dict[str, Any]] = []
    for index, (sequence, members) in enumerate(ranked[:limit], start=1):
        ratio_totals: Counter[str] = Counter()
        total_distances: list[int] = []
        for menu in members:
            structure = [block for block in menu.get("structure", []) or [] if isinstance(block, dict)]
            total = safe_int(menu.get("total_distance")) or sum(block_distance(block) for block in structure)
            total_distances.append(total)
            if total <= 0:
                continue
            by_category: Counter[str] = Counter()
            for block in structure:
                by_category[str(block.get("category") or "Unknown")] += block_distance(block)
            for category, distance in by_category.items():
                ratio_totals[category] += distance / total
        ratios = {category: round((value / len(members)) * 100, 2) for category, value in ratio_totals.items()}
        patterns.append(
            {
                "pattern_id": f"pattern_{index}",
                "block_sequence": list(sequence),
                "distance_ratios_percent": ratios,
                "average_total_distance": round(sum(total_distances) / len(total_distances), 1) if total_distances else 0,
                "support_percent": round((len(members) / len(menus)) * 100, 2) if menus else 0,
                "menu_count": len(members),
            }
        )
    return patterns


def estimate_target_group(menus: list[dict[str, Any]], methods: dict[str, int]) -> dict[str, Any]:
    """Estimate likely target group type.

    総距離、手法頻度、セッション数から masters/junior/elite/triathlon を推定する。
    """
    distances = [safe_int(menu.get("total_distance")) for menu in menus if safe_int(menu.get("total_distance"))]
    average_distance = sum(distances) / len(distances) if distances else 0
    session_count = len(menus)
    if average_distance >= 5000 and methods.get("threshold", 0) + methods.get("race pace", 0) >= session_count * 0.2:
        group = "elite"
    elif methods.get("lsd", 0) or average_distance >= 4200:
        group = "triathlon"
    elif average_distance <= 2800:
        group = "masters"
    else:
        group = "junior"
    return {
        "estimated_type": group,
        "average_total_distance": round(average_distance, 1),
        "session_count": session_count,
        "basis": "Heuristic based on total distance ranges, method frequency, and session count.",
    }


def analyze(source: Path) -> dict[str, Any]:
    """Analyze a menu index file.

    集計結果を JSON 互換辞書で返す。
    """
    menus = load_menus(source)
    methods = method_frequency(menus)
    return {
        "source": str(source),
        "menu_count": len(menus),
        "zone_distribution_percent": zone_distribution(menus),
        "distance_histogram": distance_histogram(menus),
        "method_frequency": methods,
        "skeleton_patterns": skeleton_patterns(menus),
        "estimated_target_group": estimate_target_group(menus, methods),
    }


def write_output(summary: dict[str, Any], out_path: Path | None) -> None:
    """Write analysis JSON to file or stdout.

    `--out` 指定時はファイルへ保存する。
    """
    payload = json.dumps(summary, ensure_ascii=False, indent=2)
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser.

    入力索引と任意の出力先を受け取る。
    """
    parser = argparse.ArgumentParser(description="Analyze menu tendency from a menu index JSON file.")
    parser.add_argument("--source", type=Path, default=repo_root() / "knowledge" / "custom" / "menu-index.json")
    parser.add_argument("--out", type=Path, help="Output JSON file.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the analyzer CLI.

    エラー時は stderr に表示し非ゼロ終了する。
    """
    args = build_parser().parse_args(argv)
    try:
        write_output(analyze(args.source), args.out)
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
