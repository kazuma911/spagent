"""Compare athletes' target paces and recommend same-set vs split-set operation.

**目的**: Workflow A Step 13-14 で「今日は同じセットで回せるか、別 set に分けるか」
を自動判定する。

**しきい値** (改善軸 P2-8 決定): **100m 換算 pace 差 ≤ 10 秒 → 同一 set + 個別 pace_table**。
超える場合は別 set 提案。

**入力**:

- ``--athletes <id> [<id>...]`` 対象選手
- ``--focus <benchmark_key>`` 例: ``200p_50`` / ``en3_100`` / ``race_100``
- ``--course lcm|scm`` (default lcm)
- ``--paces <path>`` (省略時 ``data/current-paces.json``)

**出力** (JSON):

.. code-block:: json

    {
      "focus": "200p_50",
      "course": "lcm",
      "targets_100m": {"athlete-b": 68.0, "athlete-a": 62.0, "athlete-c": 63.0},
      "pair_diffs_100m": [
        {"a": "athlete-a", "b": "athlete-c", "diff_sec": 1.0, "over_threshold": false},
        {"a": "athlete-a", "b": "athlete-b", "diff_sec": 6.0, "over_threshold": false},
        {"a": "athlete-c", "b": "athlete-b", "diff_sec": 5.0, "over_threshold": false}
      ],
      "max_diff_100m_sec": 6.0,
      "threshold_sec": 10.0,
      "recommendation": "same_set",
      "note": "最大 pace 差 6.0s ≤ 10s → 同一 set + 個別 pace_table で対応可"
    }

**pace 文字列パーサ**: ``"34-35"`` / ``"1:14"`` / ``"1:04-1:06"`` / ``"31"`` を
秒に変換し、範囲表記は平均値を採用。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from itertools import combinations
from pathlib import Path
from typing import Any

DEFAULT_THRESHOLD_SEC = 10.0


# event 記述 → 該当 RP キー の解決順序。
# ``current-paces.athletes.<id>.event`` の文字列を含むかで判定。
EVENT_TO_RP_KEYS: list[tuple[list[str], dict[str, list[str]]]] = [
    # 200/400 Fr 系 (athlete-a, athlete-b 等)
    (["200", "400"], {
        "race_pace_50": ["200p_50", "rp_200_50"],
        "race_pace_100": ["race_100"],
        "race_pace_200": ["race_200"],
    }),
    # 100 Fr sprinter (athlete-c, athlete-g, aya 等)
    (["100Fr", "100sprinter", "50/100"], {
        "race_pace_50": ["100p_50", "rp_100_50", "sharp_50"],
        "race_pace_100": ["race_100", "lcm_100_selfreport"],
    }),
    # 50 Fr pure sprinter
    (["50Fr", "50sprinter"], {
        "race_pace_50": ["sharp_50", "50_max"],
    }),
]


def resolve_event_focus(athlete_data: dict[str, Any], generic_focus: str) -> str | None:
    """event 非依存 focus を athlete-specific キーに解決する。

    ``generic_focus`` が ``race_pace_50`` / ``race_pace_100`` / ``race_pace_200``
    の場合、athlete の ``event`` フィールドを見て該当 RP キー候補を返す。
    それ以外の focus はそのまま返す。
    """
    if not generic_focus.startswith("race_pace_"):
        return generic_focus
    event = str(athlete_data.get("event", "")).lower()
    for tokens, mapping in EVENT_TO_RP_KEYS:
        if any(t.lower() in event for t in tokens):
            return mapping.get(generic_focus, [generic_focus])[0] if generic_focus in mapping else None
    return None


def find_target_pace_with_candidates(athlete_data: dict[str, Any], focus_key: str, course: str, candidates: list[str] | None = None) -> tuple[float | None, str | None]:
    """複数の候補キーから最初に見つかった target pace を返す。

    ``candidates`` に候補リストが渡されればそれを試し、なければ ``focus_key`` を substring 検索する。
    """
    keys_to_try = candidates or [focus_key]
    for cand in keys_to_try:
        sec, matched = find_target_pace(athlete_data, cand, course)
        if sec is not None:
            return sec, matched
    return None, None


def repo_root() -> Path:
    """Return the repository root."""
    return Path(__file__).resolve().parents[2]


TIME_TOKEN_RE = re.compile(r"(\d+):(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)")


def parse_pace_seconds(text: str) -> float | None:
    """Parse a pace-like string to average seconds.

    受け入れ形式:

    - ``34`` → 34.0
    - ``34.5`` → 34.5
    - ``34-35`` → 34.5 (range 平均)
    - ``1:14`` → 74.0
    - ``1:04-1:06`` → 65.0
    - ``1:04.6`` → 64.6
    """
    if not text:
        return None
    # Split on hyphen for range.
    parts = re.split(r"\s*[-–]\s*", text.strip())
    vals: list[float] = []
    for part in parts:
        m = re.search(r"(\d+):(\d+(?:\.\d+)?)", part)
        if m:
            vals.append(int(m.group(1)) * 60 + float(m.group(2)))
            continue
        m = re.search(r"(\d+(?:\.\d+)?)", part)
        if m:
            vals.append(float(m.group(1)))
    if not vals:
        return None
    return sum(vals) / len(vals)


def normalize_to_100m(pace_sec: float, benchmark_key: str) -> float:
    """Scale pace to 100m equivalent given the benchmark key.

    キー中の距離ヒント (``50`` / ``100`` / ``200``) を使って線形換算。
    """
    key = benchmark_key.lower()
    if "_50" in key or "50_" in key:
        return pace_sec * 2
    if "_200" in key or "200_" in key:
        return pace_sec / 2
    # default: assume 100m
    return pace_sec


def find_target_pace(athlete_data: dict[str, Any], focus_key: str, course: str) -> tuple[float | None, str | None]:
    """Locate a target pace value for ``focus_key`` under next_targets_[course]."""
    section = athlete_data.get(f"next_targets_{course}") or {}
    for k, v in section.items():
        if focus_key in k:
            if not isinstance(v, str):
                continue
            sec = parse_pace_seconds(v)
            if sec is not None:
                return sec, k
    # fallback: latest_benchmarks
    section2 = athlete_data.get("latest_benchmarks") or {}
    for k, v in section2.items():
        if focus_key in k and course in k:
            if isinstance(v, str):
                sec = parse_pace_seconds(v)
                if sec is not None:
                    return sec, k
    return None, None


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    p = argparse.ArgumentParser(description="Compare athletes' target paces and recommend same-set vs split-set.")
    p.add_argument("--athletes", nargs="+", help="Athlete ids (individual mode).")
    p.add_argument("--group", help="Group id (group-only mode). data/groups.json の pace_band を返す。個別 pair diff は不要になる。")
    p.add_argument("--groups-file", type=Path, default=None, help="Path to groups.json (default: data/groups.json).")
    p.add_argument("--focus", help="Benchmark key substring (e.g. 200p_50, race_100). individual mode で必須。group-only では未使用.")
    p.add_argument("--course", default="lcm", choices=["lcm", "scm"], help="Course code (default: lcm).")
    p.add_argument("--paces", type=Path, default=None, help="Path to current-paces.json.")
    p.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD_SEC, help="Threshold in seconds per 100m (default: 10.0).")
    return p


def emit_group_only(group_id: str, groups_data: dict[str, Any]) -> dict[str, Any]:
    """group-only モード: pace_band を返し、pair diff はスキップ。"""
    groups = groups_data.get("groups") or []
    group = next((g for g in groups if g.get("id") == group_id), None)
    if not group:
        return {"error": f"group not found: {group_id}", "recommendation": "unknown"}
    pace_band = group.get("pace_band")
    mode = group.get("mode", "individual")
    if mode != "group-only":
        return {
            "warning": f"group '{group_id}' mode='{mode}' — group-only 判定は不要。individual mode で --athletes を使ってください",
            "recommendation": "use_individual_mode",
        }
    return {
        "mode": "group-only",
        "group_id": group_id,
        "group_name": group.get("name"),
        "pace_band": pace_band,
        "typical_pace": group.get("typical_pace"),
        "skill_level": group.get("skill_level"),
        "recommendation": "same_set_uniform",
        "note": f"group-only モード: 全員 pace_band 内 ({pace_band.get('min') if pace_band else '?'}-{pace_band.get('max') if pace_band else '?'}) で回る想定。Cycle は band の最遅値 + rest 30s で共通提案。個別 pace_table は不要。",
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    args = build_parser().parse_args(argv)
    if not args.athletes and not args.group:
        print("error: either --athletes or --group must be specified", file=sys.stderr)
        return 1
    root = repo_root()
    if args.group:
        groups_path = args.groups_file or (root / "data" / "groups.json")
        try:
            groups_data = json.loads(groups_path.read_text(encoding="utf-8")) if groups_path.exists() else {"groups": []}
        except Exception as exc:  # noqa: BLE001
            print(f"error: {exc}", file=sys.stderr)
            return 1
        result = emit_group_only(args.group, groups_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if not args.focus:
        print("error: --focus is required in individual mode", file=sys.stderr)
        return 1
    paces_path = args.paces or (root / "data" / "current-paces.json")
    try:
        paces = json.loads(paces_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1
    athletes_data = paces.get("athletes") or {}
    results: dict[str, float] = {}
    matched_keys: dict[str, str] = {}
    missing: list[str] = []
    resolved_focus_per_athlete: dict[str, str] = {}
    is_generic = args.focus.startswith("race_pace_")
    for a in args.athletes:
        ad = athletes_data.get(a)
        if not ad:
            missing.append(a)
            continue
        if is_generic:
            # event-specific 候補リストを解決
            candidates: list[str] = []
            event = str(ad.get("event", "")).lower()
            for tokens, mapping in EVENT_TO_RP_KEYS:
                if any(t.lower() in event for t in tokens):
                    candidates = mapping.get(args.focus, [])
                    break
            if not candidates:
                missing.append(a)
                continue
            resolved_focus_per_athlete[a] = candidates[0]
            sec, key = find_target_pace_with_candidates(ad, args.focus, args.course, candidates)
        else:
            sec, key = find_target_pace(ad, args.focus, args.course)
        if sec is None:
            missing.append(a)
            continue
        norm = normalize_to_100m(sec, key or args.focus)
        results[a] = norm
        matched_keys[a] = key or ""
    if len(results) < 2:
        print(json.dumps({
            "focus": args.focus,
            "course": args.course,
            "targets_100m": results,
            "missing": missing,
            "warning": "2 選手以上の target pace が取れず pair diff 算出不可",
        }, ensure_ascii=False, indent=2))
        return 0

    pair_diffs = []
    max_diff = 0.0
    for a, b in combinations(results.keys(), 2):
        diff = abs(results[a] - results[b])
        pair_diffs.append({
            "a": a,
            "b": b,
            "diff_sec": round(diff, 2),
            "over_threshold": diff > args.threshold,
        })
        max_diff = max(max_diff, diff)

    recommendation = "same_set" if max_diff <= args.threshold else "split_set"
    if recommendation == "same_set":
        note = f"最大 pace 差 {round(max_diff,2)}s ≤ {args.threshold}s → 同一 set + 個別 pace_table で対応可"
    else:
        over = [p for p in pair_diffs if p["over_threshold"]]
        pairs = ", ".join(f"{p['a']}↔{p['b']} ({p['diff_sec']}s)" for p in over)
        note = f"最大 pace 差 {round(max_diff,2)}s > {args.threshold}s → 別 set 提案 ({pairs})"

    out = {
        "focus": args.focus,
        "course": args.course,
        "resolved_focus_per_athlete": resolved_focus_per_athlete if is_generic else None,
        "matched_keys": matched_keys,
        "targets_100m": {k: round(v, 2) for k, v in results.items()},
        "pair_diffs_100m": pair_diffs,
        "max_diff_100m_sec": round(max_diff, 2),
        "threshold_sec": args.threshold,
        "recommendation": recommendation,
        "note": note,
    }
    if missing:
        out["missing"] = missing
    # drop None fields for cleanliness
    out = {k: v for k, v in out.items() if v is not None}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
