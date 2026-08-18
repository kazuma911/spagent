"""Two-stage Workflow G pipeline: stage1 (parse+cluster) → [LLM AI classification] → stage2 (build).

Excel/PDF から `knowledge/custom/*` を作る Workflow G の実行フロー。
[references/ai-classification-rubric.md](../../references/ai-classification-rubric.md)
に従い **必ず LLM による AI 分類ステップを経由**する 2 フェーズ構成:

    # Stage 1: 機械抽出 + クラスタリング + AI 分類テンプレ生成 (script tagger は暫定 fallback)
    python scripts/import/run_import_pipeline.py stage1 \\
        --source knowledge/custom/imports/raw/SPA.xlsx \\
        --workdir sessions/_reimport-YYYYMMDD \\
        --clean

      → sessions/<workdir>/raw-import.json
      → sessions/<workdir>/classified.json               (script-tagger fallback、後で上書きされる)
      → knowledge/custom/menu-index.json                 (暫定、AI 分類前)
      → sessions/<workdir>/ai-classification-todo.json   ★ここで停止★
         コーチ or LLM が rubric v1 に従い分類して ai-classification.json を作成

    # Stage 2: AI 分類必須の build (validate → migrate → cluster md 再生成)
    python scripts/import/run_import_pipeline.py stage2 \\
        --workdir sessions/_reimport-YYYYMMDD \\
        --ai-answers sessions/_reimport-YYYYMMDD/ai-classification.json

      → validate 通過 → menu-index.json 上書き → knowledge/custom/ finalize
      → 全クラスタの `classification.judged_by == "spagent-classify-v1"` を検証
      → 未 AI 判定クラスタが残っていたら --allow-partial なしでエラー

`all` サブコマンドは旧挙動 (script tagger だけで完走) をテスト用に残すが、警告を出す。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent


def repo_root() -> Path:
    """Return the repository root."""
    return Path(__file__).resolve().parents[2]


def run(cmd: list[str], cwd: Path | None = None) -> None:
    """Run a subprocess, echoing the command and raising on failure."""
    print(f"$ {' '.join(str(c) for c in cmd)}", file=sys.stderr)
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        raise SystemExit(f"step failed: {' '.join(str(c) for c in cmd)}")


def _emit_ai_classification_todo(menu_index_path: Path, out_path: Path,
                                  workdir: Path) -> int:
    """Emit an AI-classification skeleton for every cluster in menu-index.json.

    Each todo record contains ``id``, ``md_path``, ``count``, ``current`` (the
    script tagger output for reference) and a ``TODO`` slot to be filled per
    rubric v1. LLM should read each ``md_path`` and produce ``records[]`` in
    the schema expected by ``ai_classify.py``.
    """
    if not menu_index_path.exists():
        print(f"warning: {menu_index_path} does not exist, skipping todo emit", file=sys.stderr)
        return 0
    index = json.loads(menu_index_path.read_text(encoding="utf-8"))
    if not isinstance(index, list):
        print(f"warning: {menu_index_path} not a list", file=sys.stderr)
        return 0

    records = []
    for entry in index:
        if not isinstance(entry, dict):
            continue
        records.append({
            "id": entry.get("id"),
            "md_path": entry.get("md_path"),
            "count": entry.get("count"),
            "example_dates": entry.get("example_dates", []),
            "current_script_tagger": {
                "method": entry.get("method"),
                "phase_hints": entry.get("phase_hints"),
                "zone_tags": entry.get("zone_tags"),
            },
            "TODO": "Read md_path, apply references/ai-classification-rubric.md v1.1, "
                    "fill {method, phase, zone_tags, intensity_signature, target, "
                    "theme_interpretation, coach_review_needed, review_reasons}. "
                    "See ai-classify apply schema.",
        })

    payload = {
        "rubric_version": "v1.1",
        "generated_at": datetime.now().astimezone().isoformat(),
        "workdir": str(workdir),
        "menu_index": str(menu_index_path),
        "instructions": [
            "1. For each todo entry, read the md_path file.",
            "2. Apply the rubric in references/ai-classification-rubric.md v1.1.",
            "3. Output records[] in the format expected by ai_classify.py apply/migrate:",
            "   { id, method:{primary,secondary,confidence,evidence}, phase:{primary,secondary,signals,confidence,evidence},",
            "     zone_tags:[canonical EN1-SP3], intensity_signature:{level:soft|balanced|high,signals,confidence,evidence},",
            "     target:{philosophy,event_focus,level,group_type,sub_groups},",
            "     theme_interpretation, coach_review_needed, review_reasons }",
            "4. Save as ai-classification.json in this workdir.",
            "5. Run: python scripts/import/run_import_pipeline.py stage2 --workdir <this> --ai-answers ai-classification.json",
        ],
        "todo": records,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(f"emitted AI classification todo for {len(records)} clusters -> {out_path}",
          file=sys.stderr)
    return len(records)


def _validate_ai_coverage(menu_index_path: Path, allow_partial: bool) -> tuple[int, int]:
    """Check every menu-index entry has `classification.judged_by=spagent-classify-v1`.

    Returns (ai_classified_count, total_count). Raises SystemExit if coverage
    is incomplete and allow_partial is False.
    """
    index = json.loads(menu_index_path.read_text(encoding="utf-8"))
    if not isinstance(index, list):
        raise SystemExit(f"menu-index.json not a list: {menu_index_path}")

    total = 0
    ai_classified = 0
    missing = []
    for entry in index:
        if not isinstance(entry, dict):
            continue
        total += 1
        cls = entry.get("classification") or {}
        judged_by = cls.get("judged_by", "")
        if judged_by.startswith("spagent-classify"):
            ai_classified += 1
        else:
            missing.append(entry.get("id"))

    print(f"AI coverage: {ai_classified}/{total} clusters", file=sys.stderr)
    if ai_classified < total and not allow_partial:
        print(f"error: {len(missing)} cluster(s) still lack AI classification "
              f"(rubric v1). Re-run stage2 with --allow-partial to accept, "
              f"or complete AI classification first. Missing:", file=sys.stderr)
        for mid in missing[:20]:
            print(f"  - {mid}", file=sys.stderr)
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more", file=sys.stderr)
        raise SystemExit(2)
    return ai_classified, total


def _stage1_parse_and_cluster(args: argparse.Namespace) -> None:
    """Run mechanical parse + script-tagger + clustering; emit AI todo."""
    args.workdir.mkdir(parents=True, exist_ok=True)
    raw_json = args.workdir / "raw-import.json"
    classified = args.workdir / "classified.json"
    todo_json = args.workdir / "ai-classification-todo.json"

    if args.source:
        ext = args.source.suffix.lower()
        if ext in {".xlsx", ".xlsm"}:
            run([args.python, str(SCRIPTS / "excel_to_menu.py"), str(args.source),
                 "--out", str(raw_json)])
        elif ext == ".pdf":
            run([args.python, str(SCRIPTS / "pdf_to_menu.py"), str(args.source),
                 "--out", str(raw_json)])
        else:
            raise SystemExit(f"unsupported source extension: {ext}")
    elif not raw_json.exists():
        raise SystemExit(f"--source not given and {raw_json} does not exist")

    classify_script = SCRIPTS.parent / "classify" / "classify_menus.py"
    run([args.python, str(classify_script), str(raw_json),
         "--output", str(classified), "--report"])

    build = SCRIPTS / "build_custom_knowledge.py"
    build_cmd = [args.python, str(build), str(classified),
                 "--out-dir", str(args.out_dir)]
    if args.clean:
        build_cmd.append("--clean")
    run(build_cmd)

    analyze = SCRIPTS.parent / "analyze" / "build_import_analysis.py"
    run([args.python, str(analyze), str(classified), "--out-dir", str(args.out_dir)])

    menu_index = args.out_dir / "menu-index.json"
    n = _emit_ai_classification_todo(menu_index, todo_json, args.workdir)

    print("", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(f"STAGE 1 complete. {n} cluster(s) parsed + script-tagger fallback.", file=sys.stderr)
    print(f"⚠  menu-index.json contains script-tagger classifications only.", file=sys.stderr)
    print(f"⚠  DO NOT USE these classifications until Stage 2 completes.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Next: LLM produces ai-classification.json per rubric v1, then run:", file=sys.stderr)
    print(f"  python scripts/import/run_import_pipeline.py stage2 \\", file=sys.stderr)
    print(f"    --workdir {args.workdir} \\", file=sys.stderr)
    print(f"    --ai-answers {args.workdir}/ai-classification.json", file=sys.stderr)
    print("=" * 70, file=sys.stderr)


def _stage2_apply_ai_and_finalize(args: argparse.Namespace) -> None:
    """Validate AI answers, migrate into menu-index, verify coverage."""
    if not args.ai_answers or not args.ai_answers.exists():
        raise SystemExit(f"--ai-answers is required and must exist: {args.ai_answers}")

    ai_classify = SCRIPTS.parent / "classify" / "ai_classify.py"

    run([args.python, str(ai_classify), "validate",
         "--answers", str(args.ai_answers)])

    menu_index = args.out_dir / "menu-index.json"
    if not menu_index.exists():
        raise SystemExit(f"menu-index.json not found: {menu_index}. Run stage1 first.")

    run([args.python, str(ai_classify), "migrate",
         "--index", str(menu_index),
         "--answers", str(args.ai_answers)])

    ai_classified, total = _validate_ai_coverage(menu_index, args.allow_partial)

    print("", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(f"STAGE 2 complete. AI coverage: {ai_classified}/{total} clusters.", file=sys.stderr)
    if ai_classified < total:
        print(f"⚠  {total - ai_classified} cluster(s) still on script-tagger fallback.", file=sys.stderr)
    else:
        print(f"✅ All clusters classified per rubric v1.", file=sys.stderr)
    print("=" * 70, file=sys.stderr)


def _stage_all_legacy(args: argparse.Namespace) -> None:
    """Legacy one-shot pipeline (script tagger only). Emits a warning."""
    print("⚠  WARNING: `all` runs script-tagger only, no AI classification.", file=sys.stderr)
    print("⚠  This is CI/test use only. Production imports must use stage1 → stage2.", file=sys.stderr)
    _stage1_parse_and_cluster(args)


def build_parser() -> argparse.ArgumentParser:
    """CLI parser with stage1 / stage2 / all subcommands."""
    parser = argparse.ArgumentParser(
        description="Workflow G two-stage pipeline (parse → [AI classify] → build)."
    )
    parser.add_argument("--python", default=sys.executable,
                        help="Python interpreter to use for subprocesses.")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("stage1",
                        help="Parse + script-tagger fallback + emit AI classification todo.")
    p1.add_argument("--source", type=Path,
                    help="Excel (.xlsx) or PDF (.pdf) source.")
    p1.add_argument("--workdir", type=Path, required=True)
    p1.add_argument("--out-dir", type=Path,
                    default=repo_root() / "knowledge" / "custom")
    p1.add_argument("--clean", action="store_true",
                    help="Wipe existing knowledge/custom/main-menus and drills before writing.")
    p1.set_defaults(func=_stage1_parse_and_cluster)

    p2 = sub.add_parser("stage2",
                        help="Apply AI classification answers and finalize menu-index.")
    p2.add_argument("--workdir", type=Path, required=True)
    p2.add_argument("--out-dir", type=Path,
                    default=repo_root() / "knowledge" / "custom")
    p2.add_argument("--ai-answers", type=Path, required=True)
    p2.add_argument("--allow-partial", action="store_true",
                    help="Accept incomplete AI coverage (some clusters remain on script-tagger).")
    p2.set_defaults(func=_stage2_apply_ai_and_finalize)

    p_all = sub.add_parser("all",
                           help="[DEPRECATED] Script-tagger one-shot (no AI). CI/test only.")
    p_all.add_argument("--source", type=Path)
    p_all.add_argument("--workdir", type=Path, required=True)
    p_all.add_argument("--out-dir", type=Path,
                       default=repo_root() / "knowledge" / "custom")
    p_all.add_argument("--clean", action="store_true")
    p_all.set_defaults(func=_stage_all_legacy)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    args = build_parser().parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

