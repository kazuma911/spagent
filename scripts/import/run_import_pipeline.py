"""One-shot Workflow G pipeline: import -> classify -> (AI review) -> build -> analyze.

Excel/PDF から読み込んだ生データを一気に `knowledge/custom/*` まで展開する。

    python scripts/import/run_import_pipeline.py \
        --source knowledge/custom/imports/raw/SPA.xlsx \
        --workdir sessions/_test-t02 \
        --clean

生成物:
  <workdir>/raw-import.json                       ← excel_to_menu.py / pdf_to_menu.py の生 dump
  <workdir>/classified.json                       ← 分類フィールド付与済み
  <workdir>/ai-review-batch.json                  ← 低信頼分 (AI 判定候補)
  knowledge/custom/main-menus/{method}/*.md
  knowledge/custom/menu-index.json
  knowledge/custom/drills/{stroke}.md
  knowledge/custom/drill-index.json
  knowledge/custom/menu-import-analysis.json      ← Workflow G Step 9
  knowledge/custom/menu-structure-patterns.json   ← Workflow G Step 10

`--ai-answers PATH` を渡すと分類 JSON にマージしてから build に進む。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
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


def build_parser() -> argparse.ArgumentParser:
    """CLI parser."""
    parser = argparse.ArgumentParser(description="Workflow G pipeline (import → classify → build).")
    parser.add_argument("--source", type=Path,
                        help="Excel (.xlsx) or PDF (.pdf) source. If omitted, --raw-json must exist.")
    parser.add_argument("--workdir", type=Path, required=True,
                        help="Directory for intermediate JSON files (raw-import.json etc).")
    parser.add_argument("--out-dir", type=Path,
                        default=repo_root() / "knowledge" / "custom",
                        help="Where knowledge/custom is (default: <repo>/knowledge/custom).")
    parser.add_argument("--ai-answers", type=Path,
                        help="Apply an existing AI review answers JSON before building.")
    parser.add_argument("--clean", action="store_true",
                        help="Wipe existing knowledge/custom/main-menus and drills before writing.")
    parser.add_argument("--python", default=sys.executable,
                        help="Python interpreter to use for subprocesses.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the full Workflow G pipeline."""
    args = build_parser().parse_args(argv)
    args.workdir.mkdir(parents=True, exist_ok=True)

    raw_json = args.workdir / "raw-import.json"
    classified = args.workdir / "classified.json"
    review_batch = args.workdir / "ai-review-batch.json"

    # Step 1: parse Excel/PDF
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

    # Step 2: classify
    classify_script = SCRIPTS.parent / "classify" / "classify_menus.py"
    run([args.python, str(classify_script), str(raw_json),
         "--output", str(classified), "--report"])

    # Step 3: emit AI review batch (informational; not fatal if empty)
    ai_review = SCRIPTS.parent / "classify" / "ai_review.py"
    run([args.python, str(ai_review), "emit", str(classified),
         "--output", str(review_batch)])

    # Step 4: apply AI answers if provided
    if args.ai_answers:
        if not args.ai_answers.exists():
            raise SystemExit(f"--ai-answers {args.ai_answers} does not exist")
        run([args.python, str(ai_review), "apply", str(classified),
             "--answers", str(args.ai_answers)])

    # Step 5: build knowledge/custom
    build = SCRIPTS / "build_custom_knowledge.py"
    build_cmd = [args.python, str(build), str(classified),
                 "--out-dir", str(args.out_dir)]
    if args.clean:
        build_cmd.append("--clean")
    run(build_cmd)

    # Step 6: analysis (Workflow G Step 9 & 10)
    analyze = SCRIPTS.parent / "analyze" / "build_import_analysis.py"
    run([args.python, str(analyze), str(classified), "--out-dir", str(args.out_dir)])

    print("", file=sys.stderr)
    print(f"pipeline done. review batch at {review_batch}", file=sys.stderr)
    if not args.ai_answers:
        print("(tip) run AI review over the batch and re-run with --ai-answers PATH", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
