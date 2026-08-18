"""Materialize classified menus into knowledge/custom (content-based clustering).

`classify_menus.py` で仕分けした JSON を入力に受け取り、次を生成する:

- `knowledge/custom/main-menus/{method}/{cluster-slug}.md`
  - 1 パターン = 1 ファイル (fingerprint で重複マージし、`example_dates` に登場日をまとめる)
- `knowledge/custom/menu-index.json`
  - 検索用の集約 (method / zone_tags / total_distance / example_dates など)
- `knowledge/custom/drills/{stroke}.md`
  - 全シートから抽出したユニーク drill を stroke 別コレクションで書き出す
- `knowledge/custom/drill-index.json`
  - 各 drill の (description, stroke, seen_count, example_dates)

`classification.valid == False` の record と、`fingerprint == None` の record は skip。
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


VALID_METHODS = ["endurance", "threshold", "vo2max", "sprint", "race-pace",
                 "recovery", "mixed", "technique"]

# 中央定義された main_body_rows を再利用 (classify とロジック共有)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "classify"))
from classify_menus import main_body_rows  # noqa: E402  (path manipulation intentional)

STROKE_KEYWORDS: list[tuple[str, re.Pattern[str]]] = [
    ("backstroke", re.compile(r"\b(back|ba\b|背泳ぎ|背)\b", re.I)),
    ("breaststroke", re.compile(r"\b(breast|br\b|平泳ぎ|平)\b", re.I)),
    ("butterfly", re.compile(r"\b(fly|butterfly|バタフライ|dolphin\s*crawl|ドルフィン)\b", re.I)),
    ("freestyle", re.compile(r"\b(free|fr\b|freestyle|クロール|自由形)\b", re.I)),
    ("kick", re.compile(r"\b(kick|キック|slash\s*kick|dolphin\s*kick|flutter)\b", re.I)),
    ("start-turn", re.compile(r"\b(start|turn|dive|underwater|u/w|streamline|ke?nobi|けのび)\b", re.I)),
]


# Drill 記述からテクニック タグを推定するためのキーワード表。
# Workflow A Step 12「選手の focus_areas 反映」で drill を絞込するのに使う。
_TECHNIQUE_KEYWORDS: list[tuple[str, re.Pattern[str]]] = [
    ("catch_up", re.compile(r"catch[\s\-]*up|キャッチ\s*アップ|front[\s\-]*quadrant", re.I)),
    ("single_arm", re.compile(r"single\s*arm|片手|3r\b|3l\b|片腕", re.I)),
    ("sculling", re.compile(r"scull|スカーリング|sweep\s*out", re.I)),
    ("kick_only", re.compile(r"^kick|6\s*kick|4\s*kick|kick\s*set|キック", re.I)),
    ("vertical_kick", re.compile(r"vertical\s*kick|垂直|立ち泳ぎ|treadmill\s*kick", re.I)),
    ("underwater", re.compile(r"underwater|u/w|水中|dolphin\s*u/w|ドルフィン\s*u/w", re.I)),
    ("streamline", re.compile(r"streamline|け?のび|ストリーム", re.I)),
    ("breathing", re.compile(r"breath|呼吸|3-3|3\s*breath|hypoxic|no\s*breath", re.I)),
    ("body_position", re.compile(r"body\s*position|体軸|ローリング|rotation|balance", re.I)),
    ("head_position", re.compile(r"head\s*(up|down|position)|頭|look", re.I)),
    ("tempo", re.compile(r"tempo|テンポ|stroke\s*rate|sr\b", re.I)),
    ("finish", re.compile(r"finish|フィニッシュ|push|プッシュ", re.I)),
    ("entry_catch", re.compile(r"entry|エントリー|catch|キャッチ", re.I)),
    ("pull_pattern", re.compile(r"s\s*pull|s\s*字|pull\s*pattern|high\s*elbow|ハイエルボー", re.I)),
    ("board_kick", re.compile(r"board|板|kickboard|kick\s*board|w/\s*board", re.I)),
    ("fins", re.compile(r"\bfins?\b|フィン", re.I)),
    ("dive_start", re.compile(r"\bdive|start|飛び込み|スタート", re.I)),
    ("turn", re.compile(r"\bturn|ターン", re.I)),
    ("dolphin", re.compile(r"dolphin|ドルフィン", re.I)),
]


def derive_technique_tags(description: str) -> list[str]:
    """Extract normalized technique tags from a drill description."""
    tags: list[str] = []
    for label, rx in _TECHNIQUE_KEYWORDS:
        if rx.search(description):
            tags.append(label)
    # dedup while preserving order
    seen: set[str] = set()
    return [t for t in tags if not (t in seen or seen.add(t))]


# --- Phase 推定 (example_dates × A 大会 から phase_hints を導出) ---------------

def load_a_priority_competitions(root: Path) -> list[dict[str, Any]]:
    """Return list of {name, start_date} for priority=A competitions, if any."""
    comps_path = root / "data" / "competitions.json"
    if not comps_path.exists():
        return []
    try:
        payload = json.loads(comps_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    comps = payload.get("competitions") if isinstance(payload, dict) else payload
    out: list[dict[str, Any]] = []
    for c in comps or []:
        if c.get("priority") == "A" and c.get("start_date"):
            out.append({"name": c.get("short_name") or c.get("name") or "", "start_date": c["start_date"]})
    return out


def _weeks_between(a: str, b: str) -> int | None:
    """Return |weeks(a - b)|, or None if either date fails to parse."""
    import datetime as _dt
    try:
        da = _dt.date.fromisoformat(a)
        db = _dt.date.fromisoformat(b)
    except Exception:
        return None
    return abs((da - db).days) // 7


def phase_from_weeks(weeks_to_meet: int, past_meet: bool) -> str:
    """Map weeks-to-nearest-A-meet to Phase label used by Workflow A."""
    if past_meet and weeks_to_meet <= 2:
        return "Trans"  # post-meet transition
    if weeks_to_meet <= 2:
        return "D"      # Taper
    if weeks_to_meet <= 6:
        return "C"      # Race-specific
    if weeks_to_meet <= 12:
        return "B"      # Build
    return "A"           # Base


def derive_phase_hints(example_dates: list[str], comps: list[dict[str, Any]]) -> list[str]:
    """Union of Phase labels seen across example_dates given A-priority meets."""
    if not comps or not example_dates:
        return []
    phases: set[str] = set()
    for date_str in example_dates:
        best: tuple[int, bool] | None = None
        for cp in comps:
            wk = _weeks_between(date_str, cp["start_date"])
            if wk is None:
                continue
            past = date_str > cp["start_date"]
            if best is None or wk < best[0]:
                best = (wk, past)
        if best is not None:
            phases.add(phase_from_weeks(best[0], best[1]))
    # preserve canonical ordering
    order = ["A", "B", "C", "D", "Trans"]
    return [p for p in order if p in phases]


def repo_root() -> Path:
    """Return the repository root."""
    return Path(__file__).resolve().parents[2]


def sanitize_slug(text: str, max_len: int = 60) -> str:
    """Return a filesystem-safe kebab-case slug."""
    if not text:
        return "pattern"
    ascii_only = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    if not ascii_only:
        return "pattern"
    return ascii_only[:max_len].strip("-") or "pattern"


def infer_course(facility: str | None) -> str | None:
    """Infer SCM/LCM course from facility string."""
    if not facility:
        return None
    lowered = facility.lower()
    if "lcm" in lowered or "50m" in lowered or "50 m" in lowered or "長水路" in facility or "メイン" in facility:
        return "LCM"
    if "scm" in lowered or "25m" in lowered or "25 m" in lowered or "短水路" in facility or "サブ" in facility:
        return "SCM"
    return None


def load_records(path: Path) -> list[dict[str, Any]]:
    """Load a JSON array of records, filtering to valid dicts."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise SystemExit(f"error: expected list in {path}, got {type(data).__name__}")
    return [r for r in data if isinstance(r, dict)]


def cluster_records(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group records by (method, fingerprint). Skip invalid or fingerprint-less ones."""
    clusters: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for record in records:
        cls = record.get("classification") or {}
        if not cls.get("valid"):
            continue
        fp = cls.get("fingerprint")
        method = cls.get("method")
        if not fp or method not in VALID_METHODS:
            continue
        clusters[fp].append(record)
    return clusters


def _main_total(record: dict[str, Any]) -> int:
    """Return the distance of the main body (excluding prep/finisher)."""
    total = 0
    for row in main_body_rows(record):
        try:
            total += int(row.get("estimated_distance") or 0)
        except (TypeError, ValueError):
            pass
    return total


def build_cluster_summary(cluster: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate a cluster of similar sessions into a single summary."""
    method = cluster[0]["classification"]["method"]
    total_dists = [int(r.get("total_distance") or 0) for r in cluster]
    main_dists = [_main_total(r) for r in cluster]
    total_avg = sum(total_dists) // len(total_dists) if total_dists else 0
    main_avg = sum(main_dists) // len(main_dists) if main_dists else 0

    all_zones: collections.Counter[str] = collections.Counter()
    intensity_votes: collections.Counter[str] = collections.Counter()
    for record in cluster:
        cls = record.get("classification", {}) or {}
        for zone in cls.get("zone_tags", []):
            all_zones[zone] += 1
        intensity = cls.get("intensity_signature")
        if isinstance(intensity, dict):
            level = intensity.get("level")
        else:
            level = intensity
        if level:
            intensity_votes[level] += 1
    zone_tags = [z for z, _ in all_zones.most_common(8)]
    intensity_level = intensity_votes.most_common(1)[0][0] if intensity_votes else None

    facilities: collections.Counter[str] = collections.Counter()
    themes: list[str] = []
    dates: list[str] = []
    for record in cluster:
        if record.get("facility"):
            facilities[record["facility"]] += 1
        theme = (record.get("theme") or "").strip()
        if theme:
            themes.append(theme)
        if record.get("date"):
            dates.append(record["date"])

    # facility は course 判定用にのみ使う (MD には出さない)
    facility_top = facilities.most_common(1)[0][0] if facilities else None
    course = infer_course(facility_top)

    representative = max(cluster, key=lambda r: int(r.get("total_distance") or 0))

    return {
        "method": method,
        "count": len(cluster),
        "total_avg": total_avg,
        "total_min": min(total_dists),
        "total_max": max(total_dists),
        "main_avg": main_avg,
        "main_min": min(main_dists) if main_dists else 0,
        "main_max": max(main_dists) if main_dists else 0,
        "zone_tags": zone_tags,
        "intensity_signature": intensity_level,
        "course": course,
        "themes": themes[:10],
        "example_dates": sorted(set(dates))[-10:],
        "representative": representative,
    }


def build_cluster_markdown(summary: dict[str, Any]) -> str:
    """Render one cluster (pattern) as a Markdown file."""
    method = summary["method"]
    rep = summary["representative"]
    lines: list[str] = []
    lines.append(f"# {method.title()} pattern (main ~{summary['main_avg']}m, seen {summary['count']}x)")
    lines.append("")
    lines.append("Content-based cluster generated by Workflow G Step 8. 同じ骨格を持つ実録セッションを集約したもの (Dryland / W-up / C-down は除外)。")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| 項目 | 内容 |")
    lines.append("|---|---|")
    lines.append(f"| Method | {method} |")
    lines.append(f"| Course | {summary.get('course') or '?'} |")
    lines.append(f"| Main body distance | {summary['main_min']} - {summary['main_max']} m (avg {summary['main_avg']}) |")
    lines.append(f"| Full session distance | {summary['total_min']} - {summary['total_max']} m (avg {summary['total_avg']}) |")
    lines.append(f"| Seen | {summary['count']} sessions |")
    lines.append(f"| Zone tags | {', '.join(summary['zone_tags']) if summary['zone_tags'] else '-'} |")
    lines.append(f"| Intensity | {summary.get('intensity_signature') or '-'} |")
    lines.append(f"| Example dates | {', '.join(summary['example_dates']) if summary['example_dates'] else '-'} |")
    lines.append("")

    if summary["themes"]:
        lines.append("## Themes seen in this cluster")
        lines.append("")
        for theme in summary["themes"]:
            lines.append(f"- {theme}")
        lines.append("")

    lines.append("## Representative main set")
    lines.append("")
    lines.append(f"Sourced from `{rep.get('sheet_name','')}` (date {rep.get('date','')}). Dryland / W-up / C-down は除外し、メインとして機能する行だけ抜粋。")
    lines.append("")
    lines.append("| # | Category | Times | Distance | Cycle | Description |")
    lines.append("|---|---|---|---|---|---|")
    rendered = 0
    for i, row in enumerate(main_body_rows(rep), start=1):
        cat = str(row.get("category") or "").replace("|", "/").strip()
        desc = str(row.get("description") or "").replace("|", "/").strip()
        times = str(row.get("times") or "").strip()
        dist = str(row.get("distance") or "").strip()
        cycle = str(row.get("cycle") or "").strip()
        if not (cat or desc):
            continue
        lines.append(f"| {i} | {cat} | {times} | {dist} | {cycle} | {desc[:200]} |")
        rendered += 1
    if rendered == 0:
        lines.append("| - | (main body could not be isolated) | | | | |")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append(f"- クラスタリング基準: fingerprint = `{rep.get('classification',{}).get('fingerprint','')}`")
    lines.append(f"- 分類確信度 (代表): {rep.get('classification',{}).get('confidence')} — {rep.get('classification',{}).get('reason','')}")
    lines.append("- 代表以外のセッション日は `example_dates` を参照 (menu-index.json)。")
    lines.append("")
    return "\n".join(lines)


def cluster_id_for(method: str, fingerprint: str) -> str:
    """Return a stable short id per cluster."""
    hashed = hashlib.sha1(fingerprint.encode("utf-8")).hexdigest()[:8]
    return f"{method}-{hashed}"


def write_main_menus(clusters: dict[str, list[dict[str, Any]]], out_dir: Path,
                     a_comps: list[dict[str, Any]] | None = None) -> tuple[int, list[dict[str, Any]]]:
    """Write per-cluster MD + build index entries.

    ``a_comps`` は Workflow A Step 11 の Phase フィルタ用に priority=A の大会日程。
    渡された場合、各クラスタの example_dates から phase_hints を推定して index に載せる。
    """
    md_root = out_dir / "main-menus"
    md_root.mkdir(parents=True, exist_ok=True)

    index_entries: list[dict[str, Any]] = []
    md_count = 0
    for fp, cluster in clusters.items():
        summary = build_cluster_summary(cluster)
        method = summary["method"]
        (md_root / method).mkdir(parents=True, exist_ok=True)
        cid = cluster_id_for(method, fp)
        rep_theme = summary["themes"][0] if summary["themes"] else method
        slug = sanitize_slug(rep_theme, 40) or "pattern"
        md_name = f"{cid}-{slug}.md"
        md_path = md_root / method / md_name
        md_path.write_text(build_cluster_markdown(summary), encoding="utf-8")
        md_count += 1

        phase_hints = derive_phase_hints(summary["example_dates"], a_comps or [])
        index_entries.append({
            "id": cid,
            "method": method,
            "count": summary["count"],
            "phase_hints": phase_hints,
            "main_avg": summary["main_avg"],
            "main_range": [summary["main_min"], summary["main_max"]],
            "total_avg": summary["total_avg"],
            "total_range": [summary["total_min"], summary["total_max"]],
            "course": summary["course"],
            "zone_tags": summary["zone_tags"],
            "intensity_signature": summary.get("intensity_signature"),
            "example_dates": summary["example_dates"],
            "themes_top": summary["themes"][:5],
            "md_path": md_path.relative_to(out_dir).as_posix(),
            "fingerprint": fp,
        })

    index_entries.sort(key=lambda e: (e["method"], -e["count"]))
    return md_count, index_entries


def infer_stroke(text: str) -> str:
    """Guess the primary stroke for a drill description."""
    for stroke, rx in STROKE_KEYWORDS:
        if rx.search(text):
            return stroke
    return "other"


def normalize_drill_key(description: str) -> str:
    """Normalize a drill description into a dedup key."""
    text = re.sub(r"\s+", " ", description.strip().lower())
    text = re.sub(r"[\(\)（）\[\]【】'\"、,。.!\?？！]", "", text)
    return text[:120]


def collect_drills(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Aggregate unique drills across records, grouped by stroke.

    key = normalized description; value keeps first-seen full description + occurrences.
    """
    by_stroke: dict[str, dict[str, dict[str, Any]]] = collections.defaultdict(dict)
    for record in records:
        cls = record.get("classification") or {}
        if not cls.get("valid"):
            continue
        for row in record.get("structure", []) or []:
            cat = str(row.get("category") or "").strip().lower()
            if cat != "drill":
                continue
            desc = str(row.get("description") or "").strip()
            if not desc:
                continue
            key = normalize_drill_key(desc)
            stroke = infer_stroke(desc)
            entry = by_stroke[stroke].setdefault(key, {
                "description": desc,
                "count": 0,
                "example_dates": [],
                "gears": collections.Counter(),
            })
            entry["count"] += 1
            date = record.get("date")
            if date and len(entry["example_dates"]) < 5 and date not in entry["example_dates"]:
                entry["example_dates"].append(date)
            gear = str(row.get("wgears") or row.get("gears") or row.get("withgears") or "").strip()
            if gear:
                entry["gears"][gear] += 1
    finalized: dict[str, list[dict[str, Any]]] = {}
    for stroke, drills in by_stroke.items():
        rows = []
        for entry in drills.values():
            top_gear = entry["gears"].most_common(1)[0][0] if entry["gears"] else ""
            rows.append({
                "description": entry["description"],
                "count": entry["count"],
                "example_dates": entry["example_dates"],
                "top_gear": top_gear,
            })
        rows.sort(key=lambda r: -r["count"])
        finalized[stroke] = rows
    return finalized


def write_drills(drills_by_stroke: dict[str, list[dict[str, Any]]], out_dir: Path) -> tuple[int, list[dict[str, Any]]]:
    """Write one MD per stroke and build a drill-index.json."""
    drill_root = out_dir / "drills"
    drill_root.mkdir(parents=True, exist_ok=True)

    index: list[dict[str, Any]] = []
    md_count = 0
    for stroke, drills in drills_by_stroke.items():
        if not drills:
            continue
        lines: list[str] = []
        lines.append(f"# {stroke.title()} drills (Workflow G Step 8)")
        lines.append("")
        lines.append(f"取り込み元シートから抽出した {stroke} 系ドリル。使用頻度順に並べている。")
        lines.append("")
        lines.append("| # | Drill (description) | Uses | Top gear | Technique tags | Example dates |")
        lines.append("|---|---|---|---|---|---|")
        for i, entry in enumerate(drills, start=1):
            desc = entry["description"].replace("|", "/")
            gear = entry["top_gear"].replace("|", "/")
            dates = ", ".join(entry["example_dates"][:3])
            tags = derive_technique_tags(entry["description"])
            tags_str = ", ".join(tags) if tags else "-"
            lines.append(f"| {i} | {desc[:200]} | {entry['count']} | {gear} | {tags_str} | {dates} |")
            index.append({
                "stroke": stroke,
                "description": entry["description"],
                "count": entry["count"],
                "top_gear": entry["top_gear"],
                "technique_tags": tags,
                "example_dates": entry["example_dates"],
            })
        lines.append("")
        (drill_root / f"{stroke}.md").write_text("\n".join(lines), encoding="utf-8")
        md_count += 1
    index.sort(key=lambda e: (e["stroke"], -e["count"]))
    return md_count, index


def build_parser() -> argparse.ArgumentParser:
    """CLI parser."""
    parser = argparse.ArgumentParser(description="Materialize classified menus into knowledge/custom.")
    parser.add_argument("input", type=Path, help="classified JSON from classify_menus.py")
    parser.add_argument("--out-dir", type=Path,
                        default=repo_root() / "knowledge" / "custom",
                        help="Root of knowledge/custom (default: <repo>/knowledge/custom)")
    parser.add_argument("--clean", action="store_true",
                        help="Remove existing main-menus/ and drills/ before writing.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Materialize classified menus into knowledge/custom."""
    args = build_parser().parse_args(argv)
    records = load_records(args.input)

    if args.clean:
        import shutil
        for sub in ("main-menus", "drills"):
            target = args.out_dir / sub
            if target.exists():
                shutil.rmtree(target)

    clusters = cluster_records(records)
    a_comps = load_a_priority_competitions(repo_root())
    md_menus, index_menus = write_main_menus(clusters, args.out_dir, a_comps=a_comps)

    drills_by_stroke = collect_drills(records)
    md_drills, index_drills = write_drills(drills_by_stroke, args.out_dir)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "menu-index.json").write_text(
        json.dumps(index_menus, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    (args.out_dir / "drill-index.json").write_text(
        json.dumps(index_drills, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )

    valid_count = sum(1 for r in records if (r.get("classification") or {}).get("valid"))
    invalid_count = len(records) - valid_count
    print(f"records read: {len(records)} (valid: {valid_count}, skipped: {invalid_count})")
    print(f"main-menu clusters written: {md_menus} across {len(set(e['method'] for e in index_menus))} methods")
    print(f"drill collections written: {md_drills} strokes, {len(index_drills)} unique drills")
    print(f"outputs:")
    print(f"  {args.out_dir / 'main-menus'}/")
    print(f"  {args.out_dir / 'drills'}/")
    print(f"  {args.out_dir / 'menu-index.json'}")
    print(f"  {args.out_dir / 'drill-index.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
