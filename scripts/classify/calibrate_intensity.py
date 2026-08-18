"""Team-agnostic intensity_signature classifier (rubric v1.1 §4.5, self-calibrating).

Two-pass algorithm:
  Pass 1: Extract cycle_per_100m_sec for every cluster; compute method-level and
          cross-method p25/p75 percentiles from the coach's own data.
  Pass 2: Apply percentile-based rules + descriptor upgrade + method overrides
          to assign soft | balanced | high per cluster.

Outputs:
  1. Updates knowledge/custom/main-menus/**/*.md Summary tables (Intensity row)
  2. Updates knowledge/custom/menu-index.json entries[].intensity_signature
  3. Writes data/intensity-calibration.json (audit: percentiles + n per method)

No hard-coded pace assumptions. Team-agnostic by construction.
"""
from __future__ import annotations

import json
import re
import statistics
from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]
MENU_ROOT = ROOT / "knowledge" / "custom" / "main-menus"
INDEX_PATH = ROOT / "knowledge" / "custom" / "menu-index.json"
CALIB_PATH = ROOT / "data" / "intensity-calibration.json"

INTENSITY_ZONE_HINTS = {
    "RACE_PACE", "SP1", "SP2", "SP3", "BROKEN", "USRPT", "MSS", "SPRINT", "VO2MAX",
}
INTENSITY_KEYWORDS = [
    "all out", "max", "descending to max", "rp", "race pace", "race-pace",
    "sprint", "fast", "race",
]

METHOD_FORCE = {
    "recovery": "soft",
    "technique": "soft",
    "lsd": "balanced",
}


def parse_cycle_to_sec(raw: str) -> int | None:
    """Parse cycle like `1'30"`, `1'`, `45"` to seconds."""
    if not raw:
        return None
    s = raw.strip().replace("’", "'").replace("″", '"').replace("''", '"')
    if not s or s == "-":
        return None
    m = re.match(r"^(?:(\d+)\s*')?\s*(\d+)?\s*\"?$", s)
    if not m:
        return None
    minutes = int(m.group(1)) if m.group(1) else 0
    seconds = int(m.group(2)) if m.group(2) else 0
    total = minutes * 60 + seconds
    return total if total > 0 else None


def parse_main_table(text: str) -> list[dict]:
    m = re.search(r"## Representative main set(.+?)(?=\n## |\Z)", text, re.S)
    if not m:
        return []
    rows = []
    for line in m.group(1).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6 or cells[0] in {"#", "---"} or not cells[0].isdigit():
            continue
        try:
            count = int(cells[2]) if cells[2].isdigit() else 1
            distance = int(re.match(r"(\d+)", cells[3]).group(1))
        except (ValueError, AttributeError):
            continue
        cycle_sec = parse_cycle_to_sec(cells[4])
        rows.append({
            "category": cells[1],
            "count": count,
            "distance": distance,
            "cycle_sec": cycle_sec,
            "description": cells[5],
        })
    return rows


def parse_summary(text: str) -> dict:
    def grab(label):
        m = re.search(r"\|\s*" + re.escape(label) + r"\s*\|\s*([^|]+?)\s*\|", text)
        return m.group(1).strip() if m else ""
    zt = grab("Zone tags")
    return {
        "method": grab("Method"),
        "zone_tags": [t.strip() for t in zt.split(",") if t.strip() and t.strip() != "-"],
        "course": grab("Course"),
    }


def is_swim_row(row: dict) -> bool:
    cat = row["category"].lower()
    if not cat:
        return True
    if any(k in cat for k in ["dryland", "warm", "w-up", "cool", "c-down"]):
        return False
    return True


def compute_cycle_per_100m(rows: list[dict]) -> float | None:
    """Weighted average cycle_sec normalized to 100m distance."""
    total_weight = 0
    weighted_cycle = 0.0
    for r in rows:
        if not is_swim_row(r) or not r["cycle_sec"] or r["distance"] <= 0:
            continue
        cycle_per_100 = r["cycle_sec"] * (100.0 / r["distance"])
        weight = r["distance"] * r["count"]
        weighted_cycle += cycle_per_100 * weight
        total_weight += weight
    if total_weight == 0:
        return None
    return weighted_cycle / total_weight


def compute_intensity_distance(rows: list[dict], zone_tags: list[str]) -> int:
    zones_upper = [z.upper() for z in zone_tags]
    zone_hot = any(z in INTENSITY_ZONE_HINTS for z in zones_upper)
    total = 0
    for r in rows:
        if not is_swim_row(r):
            continue
        desc = r["description"].lower()
        if zone_hot or any(k in desc for k in INTENSITY_KEYWORDS):
            total += r["distance"] * r["count"]
    return total


def descriptor_hot(rows: list[dict]) -> bool:
    swim_rows = [r for r in rows if is_swim_row(r)]
    if not swim_rows:
        return False
    hits = sum(1 for r in swim_rows if any(k in r["description"].lower() for k in INTENSITY_KEYWORDS))
    return hits >= max(1, len(swim_rows) // 2)


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    return sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)


def load_index() -> tuple[dict, list[dict]]:
    index_root = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    entries = index_root.get("entries", index_root) if isinstance(index_root, dict) else index_root
    return index_root, entries


def update_md_summary(text: str, level: str) -> str:
    if re.search(r"\|\s*Intensity\s*\|", text):
        return re.sub(r"\|\s*Intensity\s*\|\s*[^|]+\|", f"| Intensity | {level} |", text)
    return re.sub(
        r"(\|\s*Zone tags\s*\|[^|]+\|)\n",
        rf"\1\n| Intensity | {level} |\n",
        text,
        count=1,
    )


def main() -> None:
    md_files = sorted(MENU_ROOT.glob("*/*.md"))
    cluster_data = []
    for md in md_files:
        text = md.read_text(encoding="utf-8")
        summary = parse_summary(text)
        rows = parse_main_table(text)
        cyc = compute_cycle_per_100m(rows)
        int_dist = compute_intensity_distance(rows, summary["zone_tags"])
        d_hot = descriptor_hot(rows)
        cluster_data.append({
            "md": md,
            "text": text,
            "method": summary["method"] or "unknown",
            "zone_tags": summary["zone_tags"],
            "cycle_per_100m": cyc,
            "intensity_distance_m": int_dist,
            "descriptor_hot": d_hot,
            "row_count": sum(1 for r in rows if is_swim_row(r)),
        })

    # === Pass 1: compute percentile thresholds ===
    method_cycles: dict[str, list[float]] = defaultdict(list)
    all_cycles: list[float] = []
    for c in cluster_data:
        if c["cycle_per_100m"] is not None:
            method_cycles[c["method"]].append(c["cycle_per_100m"])
            all_cycles.append(c["cycle_per_100m"])

    cross_p25 = percentile(all_cycles, 25)
    cross_p75 = percentile(all_cycles, 75)

    method_percentiles: dict[str, dict] = {}
    for method, cycles in method_cycles.items():
        if len(cycles) >= 5:
            method_percentiles[method] = {
                "n": len(cycles),
                "p25": round(percentile(cycles, 25), 2),
                "p75": round(percentile(cycles, 75), 2),
                "median": round(statistics.median(cycles), 2),
                "source": "method-internal",
            }
        else:
            method_percentiles[method] = {
                "n": len(cycles),
                "p25": round(cross_p25, 2),
                "p75": round(cross_p75, 2),
                "median": round(statistics.median(cycles), 2) if cycles else 0.0,
                "source": f"cross-method-fallback (n={len(cycles)}<5)",
            }

    # === Pass 2: classify ===
    index_root, entries = load_index()
    id_to_entry = {e["id"]: e for e in entries if isinstance(e, dict) and e.get("id")}

    by_category: dict[str, Counter] = defaultdict(Counter)
    by_method: dict[str, Counter] = defaultdict(Counter)
    total = Counter()
    method_level_cycle: dict[tuple, list[float]] = defaultdict(list)
    updated_files = 0

    for c in cluster_data:
        method = c["method"]
        cyc = c["cycle_per_100m"]
        cross_only = len(all_cycles) < 10

        if method in METHOD_FORCE:
            level = METHOD_FORCE[method]
            confidence = "high"
            evidence = f"method={method} → force {level} (percentile 参照せず)"
        elif cyc is None:
            level = "balanced"
            confidence = "low"
            evidence = "no parseable swim rows; default balanced"
        elif cross_only:
            if c["descriptor_hot"] and c["intensity_distance_m"] >= 400:
                level = "high"
            elif c["intensity_distance_m"] < 100:
                level = "soft"
            else:
                level = "balanced"
            confidence = "low"
            evidence = f"cross-method fallback (total n={len(all_cycles)}<10), descriptor_hot={c['descriptor_hot']}"
        else:
            pct = method_percentiles[method]
            p25, p75 = pct["p25"], pct["p75"]
            if cyc < p25:
                level = "high"
            elif cyc > p75:
                level = "soft"
            else:
                level = "balanced"

            upgraded = ""
            if c["descriptor_hot"]:
                if level == "soft":
                    level = "balanced"
                    upgraded = " [descriptor upgrade soft→balanced]"
                elif level == "balanced" and c["intensity_distance_m"] >= 400:
                    level = "high"
                    upgraded = " [descriptor upgrade balanced→high]"

            if pct["source"].startswith("cross"):
                confidence = "low"
            elif pct["n"] >= 10:
                confidence = "high"
            else:
                confidence = "medium"

            evidence = (
                f"cycle_per_100m={cyc:.1f}s "
                f"(method {method} p25={p25:.1f}, p75={p75:.1f}, n={pct['n']}, {pct['source']}), "
                f"intensity_dist {c['intensity_distance_m']}m, descriptor_hot={c['descriptor_hot']} → {level}{upgraded}"
            )

        new_text = update_md_summary(c["text"], level)
        if new_text != c["text"]:
            c["md"].write_text(new_text, encoding="utf-8")
            updated_files += 1

        for eid, entry in id_to_entry.items():
            if entry.get("md_path") and c["md"].name in entry["md_path"]:
                entry["intensity_signature"] = level
                entry.setdefault("intensity_details", {}).update({
                    "cycle_per_100m_sec": round(cyc, 1) if cyc else None,
                    "intensity_distance_m": c["intensity_distance_m"],
                    "descriptor_hot": c["descriptor_hot"],
                    "confidence": confidence,
                    "evidence": evidence,
                    "judged_by": "spagent-calibrate-v1.1-selfcal",
                })
                break

        cat = c["md"].parent.name
        by_category[cat][level] += 1
        by_method[method][level] += 1
        total[level] += 1
        if cyc is not None:
            method_level_cycle[(method, level)].append(cyc)

    INDEX_PATH.write_text(json.dumps(index_root, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    calib_payload = {
        "calibrated_at": datetime.now().astimezone().isoformat(),
        "cluster_source": str(INDEX_PATH.relative_to(ROOT)),
        "n_clusters": len(cluster_data),
        "cross_method_percentiles": {
            "n": len(all_cycles),
            "p25": round(cross_p25, 2),
            "p75": round(cross_p75, 2),
        },
        "method_percentiles": method_percentiles,
        "notes": "team-agnostic percentile calibration; regenerate on each Workflow G import cycle",
    }
    CALIB_PATH.parent.mkdir(parents=True, exist_ok=True)
    CALIB_PATH.write_text(json.dumps(calib_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"=== self-calibration complete: {updated_files} md files updated ===")
    print(f"    calibration saved to {CALIB_PATH.relative_to(ROOT)}")
    print()
    print("=== cross-method cycle_per_100m percentiles (n={}) ===".format(len(all_cycles)))
    print(f"    p25={cross_p25:.1f}s  p75={cross_p75:.1f}s  (values below p25 = high, above p75 = soft)")
    print()
    print("=== per-method percentiles ===")
    print(f"  {'method':12s} {'n':>4s} {'p25':>7s} {'p75':>7s} {'median':>7s}  source")
    for method, pct in sorted(method_percentiles.items(), key=lambda x: -x[1]["n"]):
        print(f"  {method:12s} {pct['n']:>4} {pct['p25']:>7.1f} {pct['p75']:>7.1f} {pct['median']:>7.1f}  {pct['source']}")
    print()
    print("=== overall distribution ===")
    for lvl in ["soft", "balanced", "high"]:
        cnt = total[lvl]
        pct = 100 * cnt / sum(total.values()) if total else 0
        print(f"  {lvl:10s} {cnt:3d}  ({pct:4.1f}%)")
    print(f"  TOTAL      {sum(total.values())}")
    print()
    print("=== by category ===")
    print(f"  {'category':12s} {'soft':>6} {'balanced':>10} {'high':>6}")
    for cat in ["mixed", "race-pace", "recovery", "sprint", "endurance", "threshold", "technique", "vo2max"]:
        d = by_category.get(cat, Counter())
        print(f"  {cat:12s} {d['soft']:>6} {d['balanced']:>10} {d['high']:>6}")


if __name__ == "__main__":
    main()
