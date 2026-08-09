"""Classify imported menu records (Workflow G Step 8 pre-processing).

`excel_to_menu.py` / `pdf_to_menu.py` は「そのまま読む」だけ。
このスクリプトは読み終わった JSON を受け取り、次を付与する:

- `classification.method` (endurance / threshold / sprint / vo2max / recovery / mixed / technique)
- `classification.zone_tags` (EN1/EN2/EN3/SP1/SP2/RP/USRPT/...)
- `classification.confidence` (high / medium / low)  <- low は AI 再判定候補
- `classification.valid` (bool)  <- 意味不明・空同然のシートを除外
- `classification.fingerprint` (Method + total 500m バケット + カテゴリ比率シグネチャ)
- `classification.reason` (なぜその method / valid=False になったかの説明)

デフォルト動作は「新規フィールドを付けて上書き保存」。
`--report` で分布サマリを stderr に吐く。
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path
from typing import Any


CAT_MAP = {
    "swim": "Swim", "drill": "Drill", "kick": "Kick", "pull": "Pull", "main": "Main",
    "w-up": "WU", "warmup": "WU", "warm-up": "WU", "warm up": "WU", "wup": "WU",
    "c-down": "CD", "cooldown": "CD", "cool-down": "CD", "cool down": "CD", "cdown": "CD",
    "rest": "Rest", "dryland": "Dry", "recovery": "Rec", "kick&pull": "KP",
    "kickpull": "KP", "im": "Swim", "fly": "Swim", "back": "Swim", "br": "Swim", "fr": "Swim",
}

CATS_ORDER = ["WU", "Drill", "Kick", "Pull", "Swim", "Main", "CD", "Rec", "KP"]

_ZONE_RE = re.compile(
    r"\b(EN[123]|SP[123]|VO2(?:max)?|USRPT|RP\d*|Race\s*Pace|Threshold|Aerobic|Anaerobic|Recovery|MSS|Broken|Sprint)\b",
    re.IGNORECASE,
)

METHOD_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("threshold", re.compile(r"(threshold|閾値|\bEN3\b|LT\b)", re.I)),
    ("vo2max", re.compile(r"(\bvo2max\b|\bvo2\b|\bMSS\b|max\s*aerobic)", re.I)),
    ("sprint", re.compile(r"(\bsprint\b|\bSP[12]\b|dive\s*start|全力|max\s+effort|start\+dive)", re.I)),
    ("race-pace", re.compile(r"(race\s*pace|\bRP\b|\bUSRPT\b|broken\s*\d+)", re.I)),
    ("recovery", re.compile(r"(recovery|リカバリ|回復|active\s*regen|easy\s*day|off\s*day)", re.I)),
    ("endurance", re.compile(r"(\bEN[12]\b|aerobic|有酸素|endurance|dps|distance\s*swim)", re.I)),
    ("technique", re.compile(r"(technique|フォーム|技術|drill\s*day|posture|catch\s*focus)", re.I)),
]


def normalize_category(cat: str | None) -> str | None:
    """Return canonical category tag or None if unknown/empty."""
    if not cat:
        return None
    key = str(cat).strip().lower()
    if key in CAT_MAP:
        return CAT_MAP[key]
    for k, v in CAT_MAP.items():
        if k in key:
            return v
    return None


_HEADER_MAIN_KEYWORDS = re.compile(
    r"(main|core|dive|start\s*dive|race\s*pace|rp\b|usrpt|broken|threshold|閾値|sprint|"
    r"best\+?\d+|max\s*out|kick\s*out|repet|challenge|test\s*set|時間走|"
    r"peak|acc|kick\s*set|pull\s*set|swim\s*set|uw\s*set|underwater\s*set|"
    r"タバタ|tabata|persist|持続|hard\s*set)",
    re.I,
)
_HEADER_WARMUP_KEYWORDS = re.compile(
    r"(w[-\s]?up|warm[-\s]?up|warmup|in\s*water)",
    re.I,
)
_HEADER_PREP_KEYWORDS = re.compile(
    r"(dryland|chest\s*press|narrow\s*press|dips|stabilization|trunk\s*twist|"
    r"目的の共有|今日の目的|target[-\s]?share|goal[-\s]?share)",
    re.I,
)
_HEADER_COOLDOWN_KEYWORDS = re.compile(
    r"(c[-\s]?down|cool[-\s]?down|down\s*$|recovery|クールダウン|リカバリー\s*(?:d|down|プール)?|回復)",
    re.I,
)


def _row_has_body_metrics(row: dict[str, Any]) -> bool:
    """Return True if the row has any of times/distance/cycle set (i.e. actionable body row)."""
    for key in ("times", "distance", "cycle", "estimated_distance"):
        val = row.get(key)
        if val is None:
            continue
        if isinstance(val, (int, float)) and val:
            return True
        if isinstance(val, str) and val.strip():
            return True
    return False


def _classify_header(category: str) -> str | None:
    """Return the section label if the string looks like a section header.

    Returns one of: "prep", "warmup", "main", "cooldown", or None if not a header.
    """
    cat = category.strip()
    if not cat:
        return None
    if _HEADER_PREP_KEYWORDS.search(cat):
        return "prep"
    if _HEADER_COOLDOWN_KEYWORDS.search(cat):
        return "cooldown"
    if _HEADER_WARMUP_KEYWORDS.search(cat):
        return "warmup"
    if _HEADER_MAIN_KEYWORDS.search(cat):
        return "main"
    return None


def _iter_sections(record: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """Yield (section, row) pairs by walking the sheet and tracking section state.

    Row without times/distance but with a header-like category flips the section.
    First body row before any header defaults to "prep" so leading exercise entries
    (dryland chest press etc.) do not get counted as main.
    """
    state = "prep"
    out: list[tuple[str, dict[str, Any]]] = []
    for row in record.get("structure", []) or []:
        cat = str(row.get("category") or "")
        has_metrics = _row_has_body_metrics(row)
        label = _classify_header(cat)
        if label and not has_metrics:
            state = label
            continue
        if label and has_metrics:
            # header text on a body row: treat as body of that section
            state = label
        out.append((state, row))
    return out


def main_body_rows(record: dict[str, Any]) -> list[dict[str, Any]]:
    """Return only the body rows that belong to the 'main' section(s).

    セクション ヘッダで区切り、Main / Race Pace / Sprint 相当のセクションに属する行のみ返す。
    Main セクションが 1 つも見つからない場合は「全て W-up として扱われている」
    = technique/recovery day とみなし、warmup セクション行を返す (フォールバック)。

    Drill/Rec/Rest カテゴリと、距離が付いていないつなぎ行は「main の中身」として
    見せる価値がないので除外する (メニュー生成時にはあくまで本セットだけを参照したい)。
    """
    labelled = _iter_sections(record)
    mains = []
    warmups = []
    for state, row in labelled:
        cat = normalize_category(row.get("category"))
        try:
            dist = int(row.get("estimated_distance") or 0)
        except (TypeError, ValueError):
            dist = 0
        # skip dividers / empty rows outright
        if not (cat and dist > 0) and not str(row.get("description") or "").strip():
            continue
        # main-set として意味のあるカテゴリだけ残す (Drill / Rec / Rest は本セットではない)
        if not _is_main_material(row, cat, dist):
            continue
        if state == "main":
            mains.append(row)
        elif state == "warmup":
            warmups.append(row)
    if mains:
        return mains
    return warmups  # fallback: technique/recovery days with no explicit main header


# --- Main-set 判定 ------------------------------------------------------------
# 「本セット」として集計・表示すべきカテゴリのみ許可。
# Drill / Rec / Rest / (空カテゴリで距離ゼロ) は W-up 起源かつスキル系のため除外。
_MAIN_MATERIAL_CATS = {"Swim", "Kick", "Pull", "Main", "IM", "Broken", "Sprint", "USRPT",
                       "Race Pace", "RP"}
_MAIN_EXCLUDE_CATS = {"Drill", "Rec", "Rest", "Recovery"}


def _is_main_material(row: dict[str, Any], cat: str, dist: int) -> bool:
    """本セットとして扱えるかどうか (Drill/Recovery系は除外)."""
    if cat in _MAIN_EXCLUDE_CATS:
        return False
    # 距離が付いていない (= セット間 rest / お知らせ行) は集計対象から外す
    if dist <= 0:
        return False
    # 明示的な main カテゴリはそのまま許可
    if cat in _MAIN_MATERIAL_CATS:
        return True
    # 未知カテゴリでも距離があれば残す (誤除外を避ける)
    return True


def valid_rows(record: dict[str, Any]) -> list[dict[str, Any]]:
    """Return structure rows that have a canonical category and positive distance."""
    out = []
    for row in record.get("structure", []) or []:
        cat = normalize_category(row.get("category"))
        try:
            dist = int(row.get("estimated_distance") or 0)
        except (TypeError, ValueError):
            dist = 0
        if cat and dist > 0:
            out.append(row)
    return out


def is_valid(record: dict[str, Any]) -> tuple[bool, str]:
    """Determine whether a record represents a real menu.

    2 未満の実行 row しかない、総距離ゼロ、body 記述が全部空、のようなシートは除外。
    """
    rows = valid_rows(record)
    if len(rows) < 2:
        return False, f"only {len(rows)} usable row(s)"
    total = int(record.get("total_distance") or 0)
    if total <= 0:
        return False, "total_distance is zero"
    non_empty_desc = sum(1 for r in rows if str(r.get("description") or "").strip())
    if non_empty_desc == 0:
        return False, "no descriptions on any row"
    return True, "ok"


def extract_zone_tags(record: dict[str, Any]) -> list[str]:
    """Collect Zone tokens from theme + row descriptions (deduplicated, sorted)."""
    tags: set[str] = set()
    corpus: list[str] = [record.get("theme") or "", record.get("title") or ""]
    for row in record.get("structure", []) or []:
        corpus.append(str(row.get("description") or ""))
    for text in corpus:
        for match in _ZONE_RE.finditer(text):
            token = match.group(1).upper().replace(" ", "_")
            tags.add(token)
    return sorted(tags)


_AEROBIC_HINT_RE = re.compile(r"(smooth|easy|choice|dps|aerobic|Fr\b|IM\b|loosen|even\s*pace|steady)", re.I)
_RP_HINT_RE = re.compile(r"(dive|start|max\s*out|kick\s*out|underwater|u/w|best[+\s]?\d*|RP\d*|race)", re.I)
_TECH_HINT_RE = re.compile(r"(one\s*arm|scull|sculling|catch|posture|streamline|glide|dolphin\s*crawl|dpk|dpc|body\s*line)", re.I)


def infer_method(record: dict[str, Any]) -> tuple[str, str, str]:
    """Return (method, confidence, reason).

    3 段: 1) theme + body の method 直接キーワード, 2) 構造比率 + body の意味ヒント, 3) fallback "mixed".
    """
    theme = record.get("theme") or ""
    descs = [str(r.get("description") or "") for r in record.get("structure", []) or []]
    corpus = " ".join([theme] + descs)

    # 1) 直接キーワードマッチ
    hits: list[str] = []
    matched_in_theme = False
    for method, rx in METHOD_RULES:
        if rx.search(corpus):
            hits.append(method)
            if rx.search(theme):
                matched_in_theme = True
    if hits:
        primary = hits[0]
        conf = "high" if len(hits) == 1 or matched_in_theme else "medium"
        return primary, conf, f"keyword match: {','.join(hits[:3])}"

    # 2) 構造比率 + body の意味ヒント (theme が空でも当てにいく)
    total = int(record.get("total_distance") or 0)
    if total > 0:
        dist = cat_distribution(record)
        drill = dist.get("Drill", 0)
        drill_share = drill / total
        aerobic_hits = sum(1 for d in descs if _AEROBIC_HINT_RE.search(d))
        rp_hits = sum(1 for d in descs if _RP_HINT_RE.search(d))
        tech_hits = sum(1 for d in descs if _TECH_HINT_RE.search(d))
        non_empty = sum(1 for d in descs if d.strip())

        if drill_share >= 0.35 or (tech_hits >= 3 and drill_share >= 0.2):
            return "technique", "medium", f"drill share {drill}/{total}, tech hints {tech_hits}"
        if rp_hits >= 3:
            return "race-pace", "medium", f"rp/dive/max hints {rp_hits}"
        if non_empty and aerobic_hits / max(non_empty, 1) >= 0.4:
            return "endurance", "medium", f"aerobic hints {aerobic_hits}/{non_empty}"
        if total <= 2500 and drill_share >= 0.15:
            return "recovery", "medium", f"short session ({total}m) with drill share {drill_share:.2f}"

    # 3) fallback
    return "mixed", "low", "no keyword hit; fallback"


def cat_distribution(record: dict[str, Any]) -> dict[str, int]:
    """Return {canonical_category: total_distance} for the record (main body only)."""
    out: collections.Counter[str] = collections.Counter()
    for row in main_body_rows(record):
        cat = normalize_category(row.get("category"))
        try:
            dist = int(row.get("estimated_distance") or 0)
        except (TypeError, ValueError):
            dist = 0
        if cat and dist > 0:
            out[cat] += dist
    return dict(out)


def fingerprint(record: dict[str, Any], method: str) -> str:
    """Return a coarse similarity key for clustering (main body only).

    Method + main-total 500m バケット + カテゴリ距離比率 (20% バケット) の連結。
    W-up / dryland / C-down は fingerprint から除外して「メインセットが似ているか」で寄せる。
    """
    dist = cat_distribution(record)
    main_total = sum(dist.values())
    bucket = (main_total // 500) * 500
    grand = main_total or 1
    ratio_parts = []
    for cat in CATS_ORDER:
        if dist.get(cat):
            pct = round(dist[cat] / grand * 5) * 20  # 20% ステップに粗く
            if pct > 0:
                ratio_parts.append(f"{cat}{pct}")
    return f"{method}|{bucket}|" + "-".join(ratio_parts)


def classify(record: dict[str, Any]) -> dict[str, Any]:
    """Return the classification payload for a single record."""
    ok, reason = is_valid(record)
    if not ok:
        return {
            "method": None,
            "zone_tags": [],
            "confidence": "n/a",
            "valid": False,
            "fingerprint": None,
            "reason": reason,
        }
    method, confidence, mreason = infer_method(record)
    return {
        "method": method,
        "zone_tags": extract_zone_tags(record),
        "confidence": confidence,
        "valid": True,
        "fingerprint": fingerprint(record, method),
        "reason": mreason,
    }


def build_parser() -> argparse.ArgumentParser:
    """CLI parser."""
    parser = argparse.ArgumentParser(description="Classify imported menu JSON records.")
    parser.add_argument("input", type=Path, help="JSON file from excel_to_menu.py / pdf_to_menu.py")
    parser.add_argument("--output", type=Path, help="Where to write enriched JSON (default: overwrite input)")
    parser.add_argument("--report", action="store_true", help="Print distribution summary to stderr")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Enrich records with a `classification` field."""
    args = build_parser().parse_args(argv)
    data = json.loads(args.input.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        records = [data]
    elif isinstance(data, list):
        records = data
    else:
        print("error: input must be a JSON object or list", file=sys.stderr)
        return 1

    for record in records:
        if isinstance(record, dict):
            record["classification"] = classify(record)

    out_path = args.output or args.input
    out_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.report:
        method_counts: collections.Counter[str | None] = collections.Counter()
        conf_counts: collections.Counter[str] = collections.Counter()
        valid_count = 0
        for record in records:
            if not isinstance(record, dict):
                continue
            cls = record.get("classification", {})
            if cls.get("valid"):
                valid_count += 1
                method_counts[cls.get("method")] += 1
                conf_counts[cls.get("confidence", "?")] += 1
        print(f"valid: {valid_count}/{len(records)}", file=sys.stderr)
        print(f"methods: {dict(method_counts.most_common())}", file=sys.stderr)
        print(f"confidence: {dict(conf_counts.most_common())}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
