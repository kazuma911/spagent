"""Resolve training phase and gear adjustment for a given (date, athlete).

**目的**: Workflow A Step 5-6 で「今日は誰にとって何期か・レース直前後か・gear
どれくらい抑えるか」を自動判定してコーチに提示する。

**入力**:

- ``--date YYYY-MM-DD`` (必須)
- ``--athlete <id>`` (必須, 複数可)
- ``--schedule <path>`` (省略時 ``data/training-schedule.json``)
- ``--paces <path>`` (省略時 ``data/current-paces.json`` — PB 検出用)

**出力** (JSON, stdout):

.. code-block:: json

    {
      "date": "2026-08-10",
      "athletes": {
        "athlete-b": {
          "phase": "Trans2",
          "d_plus_last_race_days": 2,
          "d_minus_next_race_days": 34,
          "last_race": {"date":"2026-08-08","event":"東京都社会人 100/200Fr","pb_flag":true},
          "next_race": {"date":"2026-09-13","event":"神奈川マスターズ LCM"},
          "gear_adjustment": -1,
          "recommendation_note": "Trans2 開始日 (schedule 準拠)。8/8 レース D+2 + PB 更新のため gear -1 (aerobic/技術寄せ、intensity 30% 程度に抑制)。",
          "confidence": 0.85
        }
      }
    }

**判定ロジック**:

1. training-schedule.json の ``summer_lcm_campaign_2026.sessions`` から当日ブロック取得
2. ``block`` 記述に ``Trans``/``Acc``/``Real``/``Recovery`` を含むか正規表現で判定
3. race 記述 (``★RACE``) の直近 過去/未来 との日数差を計算
4. gear_adjustment ルール:
   - D+1: -2 (完全リカバリ)
   - D+2: -1 (aerobic/技術)
   - D+3〜D+6: 0 (通常)
   - D-7〜D-4: -1 (テーパー導入)
   - D-3〜D-1: -2 (sharpen のみ)
   - D-14〜D-8: 0 (通常 build)
5. PB 更新直後 (current-paces.json の latest_benchmarks に race_*_YYYY_ + PB を示すマーカー) は追加 -1
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    """Return the repository root."""
    return Path(__file__).resolve().parents[2]


def parse_date(s: str) -> date:
    """Parse an ISO date."""
    return datetime.strptime(s, "%Y-%m-%d").date()


BLOCK_RE = re.compile(r"(Trans2|Trans|Acc-peak|Acc|Real|Recovery)", re.IGNORECASE)


def resolve_block_for_athlete(block_field: str | None, athlete: str) -> str | None:
    """Extract per-athlete phase from a ``block`` string.

    ``block`` は ``"athlete-b:Trans / athlete-a:Acc-peak"`` のような per-athlete 記述、
    または ``"両者:Trans"``, ``"Acc"`` 等の共通記述を許容する。
    """
    if not block_field:
        return None
    text = block_field
    # per-athlete pattern
    per = re.findall(r"(\w+):([^/,]+)", text)
    for who, phase in per:
        if who.strip().lower() == athlete.lower():
            m = BLOCK_RE.search(phase)
            if m:
                return _canonical_phase(m.group(1))
    # 両者 / common
    if "両者" in text or ":" not in text:
        m = BLOCK_RE.search(text)
        if m:
            return _canonical_phase(m.group(1))
    return None


def _canonical_phase(raw: str) -> str:
    """Normalize phase spelling."""
    r = raw.lower()
    if r.startswith("trans2"):
        return "Trans2"
    if r.startswith("trans"):
        return "Trans"
    if r.startswith("acc-peak"):
        return "Acc-peak"
    if r.startswith("acc"):
        return "Acc"
    if r.startswith("real"):
        return "Real"
    if r.startswith("recovery"):
        return "Recovery"
    return raw


def load_schedule(path: Path) -> list[dict[str, Any]]:
    """Load and flatten schedule sessions including races."""
    data = json.loads(path.read_text(encoding="utf-8"))
    sessions: list[dict[str, Any]] = []
    campaign = data.get("summer_lcm_campaign_2026") or {}
    for s in campaign.get("sessions", []) or []:
        sessions.append(s)
    # Also include race entries in top-level "race" if present.
    for r in data.get("race", []) or []:
        sessions.append({**r, "block": "★RACE"})
    return sessions


def find_session(sessions: list[dict[str, Any]], the_date: date) -> dict[str, Any] | None:
    """Find a session entry for ``the_date`` (first match)."""
    for s in sessions:
        d = s.get("date")
        if not d:
            continue
        if parse_date(d) == the_date:
            return s
    return None


def find_races(sessions: list[dict[str, Any]], athlete: str) -> list[tuple[date, dict[str, Any]]]:
    """List all race entries relevant to the athlete (sorted by date).

    厳格化: block フィールドに ``★RACE`` を含むエントリのみを race と判定する。
    session の ``focus`` や ``theme`` に「本番」等の文字列が入っていても、
    それは build 期の準備セッションで race 記述ではないので誤検出しない。
    """
    out: list[tuple[date, dict[str, Any]]] = []
    for s in sessions:
        block = str(s.get("block", ""))
        if "★RACE" not in block and "RACE" not in block.upper():
            continue
        focus = str(s.get("focus", "")) + " " + str(s.get("theme", "")) + " " + str(s.get("event", ""))
        # per-athlete filter — includes 日本語エイリアス.
        name_hits = {
            "athlete-b": "athlete-b" in focus or "athlete-b" in focus.lower(),
            "athlete-a": "athlete-a" in focus or "athlete-a" in focus.lower(),
            "athlete-c": "athlete-c" in focus or "athlete-c" in focus.lower(),
        }
        athlete_key = athlete.lower()
        # If focus mentions a specific athlete list, respect it.
        specific_mention = any(name_hits.values())
        if specific_mention:
            if name_hits.get(athlete_key, False):
                out.append((parse_date(s["date"]), s))
            continue
        # No specific mention → treat as shared (all core athletes).
        out.append((parse_date(s["date"]), s))
    out.sort(key=lambda t: t[0])
    return out


def compute_gear_adjustment(d_plus: int | None, d_minus: int | None) -> tuple[int, list[str]]:
    """Compute intensity gear (0 = normal, negative = reduce)."""
    notes: list[str] = []
    gear = 0
    if d_plus is not None:
        if d_plus == 0:
            gear = min(gear, -3)
            notes.append("race 当日 → 全力レース (gear -3, planning は前提外)")
        elif d_plus == 1:
            gear = min(gear, -2)
            notes.append("D+1 → 完全リカバリ (gear -2, 有酸素 easy のみ)")
        elif d_plus == 2:
            gear = min(gear, -1)
            notes.append("D+2 → aerobic/技術寄せ (gear -1, intensity 30% 目安)")
        elif d_plus <= 6:
            notes.append(f"D+{d_plus} → 通常 build 復帰可 (gear 0)")
    if d_minus is not None:
        if 1 <= d_minus <= 3:
            gear = min(gear, -2)
            notes.append(f"D-{d_minus} → sharpen のみ (gear -2)")
        elif 4 <= d_minus <= 7:
            gear = min(gear, -1)
            notes.append(f"D-{d_minus} → テーパー導入 (gear -1, 量↓ intensity 維持)")
        elif 8 <= d_minus <= 14:
            notes.append(f"D-{d_minus} → 通常 build (gear 0)")
    return gear, notes


def detect_pb_flag(paces: dict[str, Any], athlete: str, race_date: date) -> bool:
    """Heuristically detect a PB update in current-paces.json.

    ``race_YYYY_MM_DD_lcm`` 等のキーに `PB更新` / `PB` を含めば PB とみなす。
    """
    ath = (paces.get("athletes") or {}).get(athlete) or {}
    for k, v in (ath.get("latest_benchmarks") or {}).items():
        if str(race_date.year) in k and str(race_date.month) in k:
            if isinstance(v, str) and ("PB" in v or "★" in v):
                return True
    return False


def resolve_for_athlete(
    the_date: date,
    athlete: str,
    sessions: list[dict[str, Any]],
    paces: dict[str, Any],
) -> dict[str, Any]:
    """Return the phase resolution dict for one athlete."""
    session = find_session(sessions, the_date)
    phase = None
    focus = None
    course = None
    if session:
        phase = resolve_block_for_athlete(session.get("block"), athlete)
        focus = session.get("focus")
        course = session.get("course")

    races = find_races(sessions, athlete)
    past = [(d, s) for d, s in races if d < the_date]
    future = [(d, s) for d, s in races if d > the_date]

    last_race = past[-1] if past else None
    next_race = future[0] if future else None

    d_plus = (the_date - last_race[0]).days if last_race else None
    d_minus = (next_race[0] - the_date).days if next_race else None

    gear, notes = compute_gear_adjustment(d_plus, d_minus)
    pb_flag = False
    if last_race and d_plus is not None and d_plus <= 5:
        pb_flag = detect_pb_flag(paces, athlete, last_race[0])
        if pb_flag:
            gear -= 1
            notes.append("直近レースで PB 更新 → gear -1 追加 (神経系疲労大)")

    confidence = 0.9 if phase else 0.4
    if not phase:
        # fallback to date-relative inference
        if d_plus is not None and d_plus <= 2:
            phase = "Recovery"
        elif d_minus is not None and d_minus <= 3:
            phase = "Real"
        else:
            phase = "unknown"

    return {
        "phase": phase,
        "course": course,
        "session_focus": focus,
        "d_plus_last_race_days": d_plus,
        "d_minus_next_race_days": d_minus,
        "last_race": {
            "date": last_race[0].isoformat(),
            "event": last_race[1].get("focus") or last_race[1].get("event"),
            "pb_flag": pb_flag,
        } if last_race else None,
        "next_race": {
            "date": next_race[0].isoformat(),
            "event": next_race[1].get("focus") or next_race[1].get("event"),
        } if next_race else None,
        "gear_adjustment": gear,
        "gear_notes": notes,
        "recommendation_note": " / ".join(notes) if notes else "通常運用 (gear 0)",
        "confidence": confidence,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    p = argparse.ArgumentParser(description="Resolve training phase and gear adjustment for a session date.")
    p.add_argument("--date", required=True, help="Session date, YYYY-MM-DD.")
    p.add_argument("--athlete", action="append", help="Athlete id (repeat for multiple). individual モード用.")
    p.add_argument("--group", help="Group id (group-only mode). data/groups.json を参照。個別選手なしで phase/D±n のみ算出.")
    p.add_argument("--groups-file", type=Path, default=None, help="Path to groups.json (default: data/groups.json). --group 指定時のみ使用.")
    p.add_argument("--schedule", type=Path, default=None, help="Path to training-schedule.json (default: data/training-schedule.json).")
    p.add_argument("--paces", type=Path, default=None, help="Path to current-paces.json (default: data/current-paces.json).")
    return p


def resolve_for_group(
    the_date: date,
    group_id: str,
    sessions: list[dict[str, Any]],
    groups_data: dict[str, Any],
) -> dict[str, Any]:
    """Group-only モード: 個別選手なしで phase / D-n だけ算出する。

    group が競技会 (competitions) を持つ場合 D-n だけ算出。個別 PB 追跡がないので
    gear_adjustment は D-n ベースのみ (D+n の PB 更新加点はスキップ)。
    """
    groups = groups_data.get("groups") or []
    group = next((g for g in groups if g.get("id") == group_id), None)
    if not group:
        return {"error": f"group not found: {group_id}"}
    session = find_session(sessions, the_date)
    phase = None
    focus = None
    course = None
    if session:
        # group-only モードでは athlete 別 phase は取らず、共通 phase を取る
        block = session.get("block") or ""
        m = BLOCK_RE.search(block)
        phase = _canonical_phase(m.group(1)) if m else None
        focus = session.get("focus")
        course = session.get("course")

    # group が primary_events を持てば、schedule の race entries から D-n を取れる
    d_minus = None
    next_race = None
    if group.get("primary_events"):
        # 共有 race を最も近い将来から探す
        future_races = sorted(
            [(parse_date(s["date"]), s) for s in sessions if "★RACE" in str(s.get("block", "")) and parse_date(s["date"]) > the_date],
            key=lambda t: t[0],
        )
        if future_races:
            next_race = future_races[0]
            d_minus = (next_race[0] - the_date).days

    gear, notes = compute_gear_adjustment(None, d_minus)
    if not phase:
        phase = "unknown"
    return {
        "group_id": group_id,
        "group_name": group.get("name"),
        "mode": group.get("mode", "individual"),
        "pace_band": group.get("pace_band"),
        "phase": phase,
        "course": course,
        "session_focus": focus,
        "d_minus_next_race_days": d_minus,
        "next_race": {
            "date": next_race[0].isoformat(),
            "event": next_race[1].get("focus") or next_race[1].get("event"),
        } if next_race else None,
        "gear_adjustment": gear,
        "gear_notes": notes,
        "recommendation_note": " / ".join(notes) if notes else "通常運用 (gear 0)",
        "confidence": 0.7 if phase != "unknown" else 0.3,
    }


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    args = build_parser().parse_args(argv)
    if not args.athlete and not args.group:
        print("error: either --athlete or --group must be specified", file=sys.stderr)
        return 1
    root = repo_root()
    schedule_path = args.schedule or (root / "data" / "training-schedule.json")
    paces_path = args.paces or (root / "data" / "current-paces.json")
    try:
        sessions = load_schedule(schedule_path)
        paces = json.loads(paces_path.read_text(encoding="utf-8")) if paces_path.exists() else {}
        the_date = parse_date(args.date)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1
    out: dict[str, Any] = {"date": the_date.isoformat()}
    if args.group:
        groups_path = args.groups_file or (root / "data" / "groups.json")
        try:
            groups_data = json.loads(groups_path.read_text(encoding="utf-8")) if groups_path.exists() else {"groups": []}
        except Exception as exc:  # noqa: BLE001
            print(f"error: {exc}", file=sys.stderr)
            return 1
        out["group"] = resolve_for_group(the_date, args.group, sessions, groups_data)
    if args.athlete:
        out["athletes"] = {}
        for ath in args.athlete:
            out["athletes"][ath] = resolve_for_athlete(the_date, ath, sessions, paces)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
