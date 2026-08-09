"""Workflow G Step 9 & 10: import analysis and structure patterns.

分類済み JSON を入力に、次を書き出す:

- Step 9: `knowledge/custom/menu-import-analysis.json`
    - Method / Zone / 距離帯 / 曜日 / 施設 / 器具の統計
    - 推奨 Periodization / Philosophy / Methods / 想定対象選手層
    - 根拠付き reasoning

- Step 10: `knowledge/custom/menu-structure-patterns.json`
    - Method × 距離帯ごとの骨格 (ブロック並び順・距離配分比率・総距離範囲)
    - `menu_structure_pattern_id` として profile から参照可能

CLI:

    python scripts/analyze/build_import_analysis.py \
        sessions/_test-t02/classified.json
"""

from __future__ import annotations

import argparse
import collections
import datetime as _dt
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any


# classify_menus のロジック (main_body_rows / _iter_sections / normalize_category) を再利用
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "classify"))
from classify_menus import (  # noqa: E402
    _iter_sections,
    main_body_rows,
    normalize_category,
    valid_rows,
)


BLOCK_CATEGORIES = ["WU", "Drill", "Kick", "Pull", "Swim", "Main", "CD", "Rec"]


def infer_course(facility: str | None) -> str | None:
    """Infer SCM/LCM from facility string (mirrors build_custom_knowledge)."""
    if not facility:
        return None
    lowered = facility.lower()
    if "lcm" in lowered or "50m" in lowered or "50 m" in lowered or "長水路" in facility or "メイン" in facility:
        return "LCM"
    if "scm" in lowered or "25m" in lowered or "25 m" in lowered or "短水路" in facility or "サブ" in facility:
        return "SCM"
    return None


def repo_root() -> Path:
    """Return the repository root."""
    return Path(__file__).resolve().parents[2]


def _row_dist(row: dict[str, Any]) -> int:
    """Safely return the row's estimated distance."""
    try:
        return int(row.get("estimated_distance") or 0)
    except (TypeError, ValueError):
        return 0


def _percentile(values: list[int], pct: float) -> int:
    """Return the requested percentile (0-100) of the value list."""
    if not values:
        return 0
    ordered = sorted(values)
    if pct <= 0:
        return ordered[0]
    if pct >= 100:
        return ordered[-1]
    idx = int(round((pct / 100) * (len(ordered) - 1)))
    return ordered[idx]


def _weekday(date_str: str) -> str | None:
    """Return the English weekday name for an ISO date string, or None if unparseable."""
    if not date_str:
        return None
    try:
        return _dt.date.fromisoformat(date_str).strftime("%a")
    except ValueError:
        return None


def _month(date_str: str) -> str | None:
    """Return the ISO year-month prefix for a date string, or None."""
    if not date_str or len(date_str) < 7:
        return None
    return date_str[:7]


def _tokenize_equipment(equipment: str) -> list[str]:
    """Split an equipment string into individual gear tokens."""
    parts = re.split(r"[,\s、/]+", equipment)
    return [p.strip("()") for p in parts if p.strip()]


def _cluster_key(record: dict[str, Any]) -> tuple[str, int, str] | None:
    """Return (method, total_bucket_500, course) for grouping structure patterns."""
    cls = record.get("classification") or {}
    if not cls.get("valid"):
        return None
    method = cls.get("method")
    if not method:
        return None
    total = int(record.get("total_distance") or 0)
    bucket = (total // 500) * 500
    course = infer_course(record.get("facility") or "") or "any"
    return (method, bucket, course)


def _record_block_sequence(record: dict[str, Any]) -> tuple[list[str], dict[str, int]]:
    """Return (ordered_block_categories, distance_by_state) for one session.

    セクション ヘッダ状態機械に沿って、状態遷移列と状態別距離を返す。
    """
    order: list[str] = []
    dist_by_state: collections.Counter[str] = collections.Counter()
    for state, row in _iter_sections(record):
        d = _row_dist(row)
        if d <= 0:
            continue
        dist_by_state[state] += d
        if not order or order[-1] != state:
            order.append(state)
    return order, dict(dist_by_state)


def _record_body_distribution(record: dict[str, Any]) -> dict[str, int]:
    """Distance distribution per canonical category for the main body only."""
    dist: collections.Counter[str] = collections.Counter()
    for row in main_body_rows(record):
        cat = normalize_category(row.get("category"))
        d = _row_dist(row)
        if cat and d > 0:
            dist[cat] += d
    return dict(dist)


def build_analysis(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the Step 9 menu-import-analysis payload."""
    valid = [r for r in records if (r.get("classification") or {}).get("valid")]
    total_distances = [int(r.get("total_distance") or 0) for r in valid if r.get("total_distance")]
    dates = sorted(r.get("date") for r in valid if r.get("date"))
    method_share: collections.Counter[str] = collections.Counter()
    zone_share: collections.Counter[str] = collections.Counter()
    course_share: collections.Counter[str] = collections.Counter()
    dow_share: collections.Counter[str] = collections.Counter()
    month_share: collections.Counter[str] = collections.Counter()
    facilities: collections.Counter[str] = collections.Counter()
    equipment_tokens: collections.Counter[str] = collections.Counter()
    themes: collections.Counter[str] = collections.Counter()
    distance_buckets: collections.Counter[int] = collections.Counter()

    for record in valid:
        cls = record.get("classification") or {}
        if cls.get("method"):
            method_share[cls["method"]] += 1
        for zone in cls.get("zone_tags") or []:
            zone_share[zone] += 1
        course = infer_course(record.get("facility") or "")
        if course:
            course_share[course] += 1
        dow = _weekday(record.get("date") or "")
        if dow:
            dow_share[dow] += 1
        month = _month(record.get("date") or "")
        if month:
            month_share[month] += 1
        facility = record.get("facility")
        if facility:
            facilities[facility] += 1
        equipment = record.get("equipment")
        if equipment:
            for token in _tokenize_equipment(equipment):
                equipment_tokens[token] += 1
        theme = (record.get("theme") or "").strip()
        if theme:
            themes[theme] += 1
        total = int(record.get("total_distance") or 0)
        if total > 0:
            distance_buckets[(total // 500) * 500] += 1

    def to_share(counter: collections.Counter, total_count: int) -> dict[str, float]:
        return {k: round(v / total_count, 3) for k, v in counter.most_common() if total_count}

    n = len(valid)
    payload: dict[str, Any] = {
        "generated_at": _dt.date.today().isoformat(),
        "source_records": len(records),
        "valid_records": n,
        "date_range": [dates[0] if dates else None, dates[-1] if dates else None],
        "method_share": to_share(method_share, n),
        "zone_share": to_share(zone_share, n),
        "course_share": to_share(course_share, n),
        "distance_distribution": {
            "avg": int(statistics.mean(total_distances)) if total_distances else 0,
            "median": int(statistics.median(total_distances)) if total_distances else 0,
            "p25": _percentile(total_distances, 25),
            "p75": _percentile(total_distances, 75),
            "min": min(total_distances) if total_distances else 0,
            "max": max(total_distances) if total_distances else 0,
            "buckets_500m": {str(k): distance_buckets[k] for k in sorted(distance_buckets)},
        },
        "session_distribution_by_dow": dict(dow_share.most_common()),
        "session_distribution_by_month": dict(sorted(month_share.items())),
        "top_facilities": [{"name": k, "count": v} for k, v in facilities.most_common(5)],
        "top_equipment_tokens": [{"name": k, "count": v} for k, v in equipment_tokens.most_common(15)],
        "top_themes": [{"name": k, "count": v} for k, v in themes.most_common(10)],
    }

    # 4 層モデルの推奨を method_share から導出
    top_methods = [m for m, _ in method_share.most_common(3)]
    if any(m in {"race-pace", "sprint", "vo2max"} for m in top_methods) and any(m in {"recovery", "endurance"} for m in top_methods):
        periodization = "Block"
        peri_reason = "スピード系と有酸素系が明確に分かれ、シーズン内で目的別ブロックを構成しやすい配分"
    elif "threshold" in top_methods:
        periodization = "Undulating"
        peri_reason = "閾値中心で日ごとの負荷を波状に変える運用が想定される"
    else:
        periodization = "Matveyev"
        peri_reason = "有酸素基盤中心の分布のため、線形ピリオダイゼーションが自然"

    if course_share.get("SCM", 0) >= course_share.get("LCM", 0):
        philosophy_target = "Masters"
        philo_reason = "SCM 中心のマスターズ運用と一致"
    else:
        philosophy_target = "Masters"
        philo_reason = "LCM 比率が高くても Master 帯の距離配分を維持"

    payload["recommendations"] = {
        "periodization": periodization,
        "philosophy": philosophy_target,
        "methods": top_methods,
        "target_group_type": "masters",
        "reasoning": (
            f"Method 上位 {top_methods} = {periodization} 推奨: {peri_reason}. "
            f"Course = {philosophy_target}: {philo_reason}. "
            f"距離中央値 {payload['distance_distribution']['median']}m, "
            f"最頻曜日 {next(iter(dow_share), '-')}."
        ),
    }
    return payload


def build_structure_patterns(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build the Step 10 structure patterns payload.

    Method × 総距離 500m バケット × Course でクラスタリング。
    ブロック並び順・距離配分比率・総距離範囲・例日を集約。
    """
    groups: dict[tuple[str, int, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for record in records:
        key = _cluster_key(record)
        if key is None:
            continue
        groups[key].append(record)

    patterns: list[dict[str, Any]] = []
    for (method, bucket, course), cluster in groups.items():
        if len(cluster) < 2:
            continue  # 骨格パターンは 2 セッション以上の再現性がある場合のみ
        totals = [int(r.get("total_distance") or 0) for r in cluster]
        # 状態別距離を集計 → 平均比率
        state_totals: collections.Counter[str] = collections.Counter()
        state_sessions: collections.Counter[str] = collections.Counter()
        sequences: collections.Counter[tuple[str, ...]] = collections.Counter()
        body_cat_totals: collections.Counter[str] = collections.Counter()
        for record in cluster:
            order, dist_by_state = _record_block_sequence(record)
            sequences[tuple(order)] += 1
            for state, d in dist_by_state.items():
                state_totals[state] += d
                state_sessions[state] += 1
            for cat, d in _record_body_distribution(record).items():
                body_cat_totals[cat] += d
        grand = sum(state_totals.values()) or 1
        state_ratio = {s: round(v / grand, 3) for s, v in state_totals.most_common() if v > 0}
        body_grand = sum(body_cat_totals.values()) or 1
        body_ratio = {c: round(v / body_grand, 3) for c, v in body_cat_totals.most_common() if v > 0}

        top_order = sequences.most_common(1)[0][0] if sequences else ()
        dates = sorted({r.get("date") for r in cluster if r.get("date")})

        pattern_id_bits = [method, f"{bucket}m"]
        if course != "any":
            pattern_id_bits.append(course.lower())
        pattern_id = "spa-" + "-".join(pattern_id_bits)

        patterns.append({
            "id": pattern_id,
            "label": f"{method.title()} {course} ~{bucket}m",
            "method": method,
            "course": course if course != "any" else None,
            "total_distance_target": bucket,
            "total_distance_range": [min(totals), max(totals)],
            "total_distance_avg": int(sum(totals) / len(totals)),
            "block_order": list(top_order),
            "block_distance_ratio": state_ratio,
            "body_category_ratio": body_ratio,
            "count": len(cluster),
            "example_dates": dates[-6:],
            "notes": (
                f"{len(cluster)} sessions ({dates[0] if dates else '?'} - {dates[-1] if dates else '?'}). "
                f"Main body: {', '.join(f'{c}={p}' for c, p in list(body_ratio.items())[:4])}."
            ),
        })

    patterns.sort(key=lambda p: (p["method"], -p["count"]))
    return patterns


def build_parser() -> argparse.ArgumentParser:
    """CLI parser."""
    parser = argparse.ArgumentParser(description="Build Workflow G Step 9 & 10 artifacts.")
    parser.add_argument("input", type=Path, help="classified JSON from classify_menus.py")
    parser.add_argument("--out-dir", type=Path,
                        default=repo_root() / "knowledge" / "custom",
                        help="Where to write the two JSON files.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Emit the two Workflow G analysis artifacts."""
    args = build_parser().parse_args(argv)
    data = json.loads(args.input.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        records = [data]
    elif isinstance(data, list):
        records = [r for r in data if isinstance(r, dict)]
    else:
        raise SystemExit("input must be a JSON object or array of objects")

    analysis = build_analysis(records)
    patterns = build_structure_patterns(records)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "menu-import-analysis.json").write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    (args.out_dir / "menu-structure-patterns.json").write_text(
        json.dumps(patterns, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )

    print(f"analysis: valid={analysis['valid_records']}, methods={list(analysis['method_share'])[:3]}")
    print(f"patterns: {len(patterns)} (>=2 sessions/cluster)")
    print(f"outputs:")
    print(f"  {args.out_dir / 'menu-import-analysis.json'}")
    print(f"  {args.out_dir / 'menu-structure-patterns.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
