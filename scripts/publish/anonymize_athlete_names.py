#!/usr/bin/env python3
"""Anonymize athlete names across the spagent repo.

Real name -> generic alias. Applied to all text files.
Includes context-sensitive handling for ambiguous tokens like 「たい」.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

# Mapping. Order matters: longer / more-specific first to avoid partial overlap.
MAPPING: list[tuple[str, str, bool]] = [
    # (pattern, replacement, is_word_bounded_romaji)
    ("athlete-e", "athlete-e", False),
    ("athlete-c", "athlete-c", False),
    ("athlete-a", "athlete-a", False),
    ("athlete-i", "athlete-i", False),
    ("athlete-f", "athlete-f", False),
    ("athlete-d", "athlete-d", False),
    ("athlete-j",   "athlete-j", False),
    ("athlete-g",   "athlete-g", False),
    ("athlete-b",   "athlete-b", False),
    # Romaji (word-bounded to avoid munging kazuma911 etc.)
    ("athlete-a", "athlete-a", True),
    ("athlete-c", "athlete-c", True),
    ("athlete-g", "athlete-g", True),
    ("athlete-b", "athlete-b", True),
    ("athlete-i", "athlete-i", True),
    ("athlete-j", "athlete-j", True),
]

# Team Alpha group generalization (from groups.json etc.).
SPA_REPLACEMENTS: list[tuple[str, str]] = [
    ("Team Alpha コア", "Team Alpha コア"),
    ("Team Alpha 拡張", "Team Alpha 拡張"),
    ("Team Alpha", "Team Alpha"),
]

# 「たい」 handled only in name-context: between/adjacent to 「・」「/」「(」「（」.
TAI_REPLACEMENTS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(?<=[・/(（])たい(?=[・/、）)])"), "athlete-h"),   # ・athlete-h・
    (re.compile(r"たい(?=・)"), "athlete-h"),                       # athlete-h・
    (re.compile(r"(?<=[・/])たい(?![\u3040-\u30ff\u4e00-\u9fff])"), "athlete-h"),  # ・athlete-h end
]

TEXT_EXTENSIONS = {".md", ".json", ".py", ".txt", ".yml", ".yaml", ".tsv", ".csv"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist"}


def anonymize_text(text: str) -> tuple[str, int]:
    """Apply all replacements to text; return (new_text, total_replacements)."""
    total = 0

    for pat, repl, word_bounded in MAPPING:
        if word_bounded:
            regex = re.compile(rf"\b{re.escape(pat)}\b")
            new_text, n = regex.subn(repl, text)
        else:
            new_text = text.replace(pat, repl)
            n = text.count(pat)
        text = new_text
        total += n

    for src, dst in SPA_REPLACEMENTS:
        n = text.count(src)
        text = text.replace(src, dst)
        total += n

    for regex, repl in TAI_REPLACEMENTS:
        text, n = regex.subn(repl, text)
        total += n

    return text, total


def process_repo(root: Path, dry_run: bool = False) -> dict:
    stats = {"files_scanned": 0, "files_changed": 0, "replacements": 0}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        stats["files_scanned"] += 1
        new_text, n = anonymize_text(original)
        if n > 0:
            stats["files_changed"] += 1
            stats["replacements"] += n
            if not dry_run:
                path.write_text(new_text, encoding="utf-8", newline="\n")
            print(f"  {path.relative_to(root)}: {n} replacement(s)")
    return stats


def main():
    if len(sys.argv) < 2:
        print("Usage: anonymize.py <repo_root> [--dry-run]")
        sys.exit(1)
    root = Path(sys.argv[1]).resolve()
    dry_run = "--dry-run" in sys.argv
    print(f"[{'DRY' if dry_run else 'APPLY'}] scanning {root} ...")
    stats = process_repo(root, dry_run=dry_run)
    print(f"\n=== summary ===")
    print(f"files scanned: {stats['files_scanned']}")
    print(f"files changed: {stats['files_changed']}")
    print(f"replacements : {stats['replacements']}")


if __name__ == "__main__":
    main()
