#!/usr/bin/env python
"""Promote custom knowledge (menus + drills + patterns) to knowledge/base/community/.

Renames: <folder>-<hash>-*.md -> <method>-<distance>m-<zone>-<hash>.md
Preserves original folder structure under base/community/.
Regenerates community-menu-index.json (relative paths adjusted).
"""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CUSTOM = ROOT / "knowledge" / "custom"
COMMUNITY = ROOT / "knowledge" / "base" / "community"

HEADER = (
    "<!-- Community-contributed pattern promoted from a coach's imported past menus\n"
    "     (AI-classified via Workflow G Step 8, rubric v1.1). PII-scanned clean. -->\n\n"
)


def slugify_zone(zone_tags):
    if not zone_tags:
        return "mixed"
    return zone_tags[0].lower().replace("_", "-")


def build_new_name(entry):
    method = entry.get("method", "mixed")
    dist = int(entry.get("main_avg") or 0)
    zone = slugify_zone(entry.get("zone_tags"))
    hash8 = entry["id"].split("-")[-1]
    return f"{method}-{dist}m-{zone}-{hash8}.md"


def get_folder(entry):
    parts = entry["md_path"].split("/")
    return parts[1] if len(parts) >= 3 else "misc"


def main():
    index_path = CUSTOM / "menu-index.json"
    entries = json.loads(index_path.read_text(encoding="utf-8"))

    if COMMUNITY.exists():
        shutil.rmtree(COMMUNITY)
    COMMUNITY.mkdir(parents=True)

    new_entries = []
    copied = 0
    skipped = []
    for e in entries:
        src = CUSTOM / e["md_path"]
        if not src.exists():
            skipped.append(str(src))
            continue
        folder = get_folder(e)
        new_name = build_new_name(e)
        dest_dir = COMMUNITY / "main-menus" / folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / new_name

        body = src.read_text(encoding="utf-8")
        if not body.startswith("<!-- Community"):
            body = HEADER + body
        dest.write_text(body, encoding="utf-8")

        new_e = dict(e)
        new_e["md_path"] = f"main-menus/{folder}/{new_name}"
        new_e["source"] = "community"
        new_entries.append(new_e)
        copied += 1

    idx_out = COMMUNITY / "menu-index.json"
    idx_out.write_text(
        json.dumps(new_entries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    drill_src_dir = CUSTOM / "drills"
    if drill_src_dir.exists():
        drill_dest = COMMUNITY / "drills"
        drill_dest.mkdir(parents=True, exist_ok=True)
        for p in drill_src_dir.iterdir():
            if p.is_file() and p.suffix == ".md":
                body = p.read_text(encoding="utf-8")
                if not body.startswith("<!-- Community"):
                    body = HEADER + body
                (drill_dest / p.name).write_text(body, encoding="utf-8")

    for name in ("drill-index.json", "menu-structure-patterns.json"):
        src = CUSTOM / name
        if src.exists():
            shutil.copy2(src, COMMUNITY / name)

    readme = COMMUNITY / "README.md"
    readme.write_text(
        "# Community-Contributed Knowledge\n\n"
        "コーチが取り込んだ過去メニュー・ドリル・骨格パターンを公開したもの (Workflow G Step 8 で AI 分類済み)。\n\n"
        "**構造**:\n"
        "- `main-menus/<method>/` — AI 分類済みメインメニュー (117 パターン)\n"
        "- `drills/` — 追加ドリル (6 カテゴリ)\n"
        "- `menu-index.json` — 検索インデックス (`source: \"community\"`)\n"
        "- `drill-index.json` — ドリル索引\n"
        "- `menu-structure-patterns.json` — 骨格パターン\n\n"
        "**使い方**: Workflow A Step 10 / 10.5 / 11 で Base 候補と並んで自動的にサジェストされます。\n\n"
        "**PII 精査**: 全ファイル `scripts/pii/text_pii_check.py` でクリーン確認済。\n",
        encoding="utf-8",
    )

    print(f"copied: {copied} menu files")
    print(f"skipped: {len(skipped)}")
    for s in skipped:
        print(f"  {s}")
    print(f"community index: {idx_out}")


if __name__ == "__main__":
    main()
