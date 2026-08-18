"""spagent 総合セルフテスト.

以下を順に検証し、失敗があれば非 0 で終了する:
  1. JSON: 全 .json ファイルがパースできる
  2. Python: 全 .py ファイルがコンパイルできる
  3. Template: session-menu.template.tsv に Team Alpha などの watermark が残っていない
  4. Cross-links: SKILL.md / README.md / docs/*.md 内のローカル相対リンクが解決する
  5. PII scanner: エイリアス / グループ名で False Positive を出さない、フルネームで検出する
  6. Knowledge policy: Base only / Base+Custom / Custom only の 3 択が定義されている

CI での利用と、コーチが手元で「壊れてないか」を確かめる用途を兼ねる。
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestResult:
    """Aggregate pass / fail counts for the final summary."""

    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0
        self.failures: list[str] = []

    def ok(self, name: str) -> None:
        self.passed += 1
        print(f"  [PASS] {name}")

    def fail(self, name: str, detail: str) -> None:
        self.failed += 1
        self.failures.append(f"{name}: {detail}")
        print(f"  [FAIL] {name}: {detail}")


def section(title: str) -> None:
    print(f"\n== {title} ==")


def test_json(result: TestResult) -> None:
    section("JSON validity")
    for path in REPO_ROOT.rglob("*.json"):
        if any(part.startswith(".git") for part in path.parts):
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
            result.ok(str(path.relative_to(REPO_ROOT)))
        except Exception as exc:  # noqa: BLE001
            result.fail(str(path.relative_to(REPO_ROOT)), str(exc))


def test_python(result: TestResult) -> None:
    section("Python compilation")
    for path in REPO_ROOT.rglob("*.py"):
        if any(part.startswith(".git") or part == "__pycache__" for part in path.parts):
            continue
        proc = subprocess.run(
            [sys.executable, "-m", "py_compile", str(path)],
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            result.ok(str(path.relative_to(REPO_ROOT)))
        else:
            result.fail(str(path.relative_to(REPO_ROOT)), proc.stderr.strip() or proc.stdout.strip())


def test_watermarks(result: TestResult) -> None:
    section("Template watermarks (Team Alpha etc.)")
    banned = [
        (re.compile(r"^\s*S\.P\.A\.?\s*$", re.MULTILINE), "Team Alpha"),
        (re.compile(r"^\s*SPA\s*$", re.MULTILINE), "SPA"),
        (re.compile(r"^\s*S\.\s?P\.\s?A\.?\s*$", re.MULTILINE), "S. P. A."),
    ]
    for path in (REPO_ROOT / "templates").rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        hits: list[str] = []
        for pattern, label in banned:
            if pattern.search(text):
                hits.append(label)
        if hits:
            result.fail(str(path.relative_to(REPO_ROOT)), f"watermarks found: {', '.join(hits)}")
        else:
            result.ok(str(path.relative_to(REPO_ROOT)))


def test_crosslinks(result: TestResult) -> None:
    section("Markdown cross-links")
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)#\s]+)(?:#[^)]+)?\)")
    md_files = [
        REPO_ROOT / "SKILL.md",
        REPO_ROOT / "README.md",
        *(REPO_ROOT / "docs").rglob("*.md"),
    ]
    for md in md_files:
        if not md.exists():
            continue
        text = md.read_text(encoding="utf-8")
        missing: list[str] = []
        for match in link_pattern.finditer(text):
            target = match.group(1)
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (md.parent / target).resolve()
            if not resolved.exists():
                missing.append(target)
        if missing:
            result.fail(str(md.relative_to(REPO_ROOT)), f"missing: {', '.join(missing[:5])}")
        else:
            result.ok(str(md.relative_to(REPO_ROOT)))


def _run_pii_scanner(content: str) -> tuple[int, list[dict[str, str]]]:
    tmp = REPO_ROOT / "sessions" / "_pii_test_input.tmp.tsv"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(content, encoding="utf-8")
    import os
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "pii" / "text_pii_check.py"), str(tmp), "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        findings = json.loads(proc.stdout or "[]")
        return proc.returncode, findings
    finally:
        tmp.unlink(missing_ok=True)


def test_pii_negatives(result: TestResult) -> None:
    section("PII scanner: should NOT flag aliases / group names")
    cases = [
        ("alias-ascii", "name\talias\ntimes\nally\tfreestyle_100m\n1:04\n"),
        ("alias-katakana", "alias: アリス\nalias: カロル\n"),
        ("group-name-jp", "group_name: 月曜マスターズ\ngroup_name: 水曜ジュニア\n"),
        ("group-name-en", "group_name: monday-masters\n"),
        ("nickname", "nickname: たろう\n"),
    ]
    for name, content in cases:
        _, findings = _run_pii_scanner(content)
        name_findings = [f for f in findings if f.get("kind") in ("jp_name", "kana_name")]
        if not name_findings:
            result.ok(f"negative: {name}")
        else:
            result.fail(f"negative: {name}", f"unexpected findings: {name_findings}")


def test_pii_positives(result: TestResult) -> None:
    section("PII scanner: should flag real PII")
    cases = [
        ("full-name-kanji", "氏名: 田中太郎\n", "jp_name"),
        ("full-name-space", "選手名: 山田 太郎\n", "jp_name"),
        ("full-name-katakana", "選手名: タナカ タロウ\n", "kana_name"),
        ("email", "coach@example.com\n", "email"),
        ("phone", "090-1234-5678\n", "phone"),
        ("birthday", "生年月日: 2001-04-15\n", "birth_date"),
    ]
    for name, content, expected_kind in cases:
        _, findings = _run_pii_scanner(content)
        kinds = {f.get("kind") for f in findings}
        if expected_kind in kinds:
            result.ok(f"positive: {name} → {expected_kind}")
        else:
            result.fail(f"positive: {name}", f"expected {expected_kind}, got {kinds}")


def test_knowledge_policy_choices(result: TestResult) -> None:
    section("Knowledge policy: Base only / Base+Custom / Custom only")
    skill = (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")
    checks = [
        ("Base のみ", re.compile(r"Base\s*のみ")),
        ("Custom のみ", re.compile(r"Custom\s*のみ")),
        ("Base\\s*\\+\\s*Custom", re.compile(r"Base\s*\+\s*Custom|Custom\s*も追加")),
    ]
    for label, pattern in checks:
        if pattern.search(skill):
            result.ok(f"SKILL.md mentions '{label}'")
        else:
            result.fail(f"SKILL.md '{label}'", "not found in Workflow E policy choices")


def test_phase_resolver_fallback(result: TestResult) -> None:
    """phase_resolver should exit 0 with phase=unknown when schedule/paces are missing."""
    section("phase_resolver graceful fallback (no schedule)")
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        missing_sched = Path(tmp_dir) / "no-schedule.json"
        missing_paces = Path(tmp_dir) / "no-paces.json"
        script = REPO_ROOT / "scripts" / "analyze" / "phase_resolver.py"
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        proc = subprocess.run(
            [sys.executable, str(script), "--date", "2026-08-18", "--athlete", "test_athlete",
             "--schedule", str(missing_sched), "--paces", str(missing_paces)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", env=env,
        )
        if proc.returncode != 0:
            result.fail("phase_resolver no-schedule exit code", f"expected 0, got {proc.returncode} stderr={(proc.stderr or '')[:200]}")
            return
        stdout = proc.stdout or ""
        try:
            out = json.loads(stdout)
        except json.JSONDecodeError as exc:
            result.fail("phase_resolver no-schedule JSON parse", f"{exc}; stdout={stdout[:200]!r}")
            return
        if out.get("warnings"):
            result.ok("warnings included when schedule missing")
        else:
            result.fail("phase_resolver no-schedule warnings", "warnings array missing")
        ath = out.get("athletes", {}).get("test_athlete", {})
        if ath.get("phase") == "unknown":
            result.ok("phase=unknown when schedule missing")
        else:
            result.fail("phase_resolver no-schedule phase", f"expected 'unknown', got {ath.get('phase')}")


def test_register_schedule(result: TestResult) -> None:
    """register_schedule.py --merge should validate candidates and idempotently upsert."""
    section("register_schedule.py merge & validation")
    import os
    import tempfile
    import shutil

    script = REPO_ROOT / "scripts" / "import" / "register_schedule.py"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        tmp_data = tmp_root / "data"
        tmp_data.mkdir()
        (tmp_root / "scripts" / "import").mkdir(parents=True)
        for sub in ("scripts",):
            shutil.copytree(REPO_ROOT / sub, tmp_root / sub, dirs_exist_ok=True)

        candidates_valid = {
            "competitions": [{
                "id": "test-comp-2027",
                "name": "Test comp",
                "start_date": "2027-04-10",
                "end_date": "2027-04-10",
                "course": "LCM",
                "priority": "B",
                "entries": [{"athlete_id": "test_athlete", "event": "100Fr", "target_time": "1:05.00"}],
            }],
            "sessions": [{"date": "2027-04-08", "dow": "木", "course": "SCM", "block": "Taper", "focus": "sharpening", "managed_by": "self"}],
        }
        cand_path = tmp_root / "cand.json"
        cand_path.write_text(json.dumps(candidates_valid, ensure_ascii=False), encoding="utf-8")

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        proc = subprocess.run(
            [sys.executable, str(tmp_root / "scripts" / "import" / "register_schedule.py"),
             "--merge", str(cand_path), "--dry-run"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", env=env, cwd=str(tmp_root),
        )
        if proc.returncode != 0:
            result.fail("register_schedule dry-run valid", f"exit={proc.returncode} stderr={(proc.stderr or '')[:200]}")
        else:
            try:
                report = json.loads(proc.stdout or "")
                if report["added"]["competitions"] == 1 and report["added"]["sessions"] == 1 and not report["errors"]:
                    result.ok("valid candidates: dry-run reports 1+1 added")
                else:
                    result.fail("register_schedule dry-run valid", f"unexpected report: {report}")
            except json.JSONDecodeError as exc:
                result.fail("register_schedule dry-run JSON", str(exc))

        candidates_invalid = {
            "competitions": [{"id": "", "name": "Bad", "start_date": "not-a-date", "course": "OWS"}],
            "sessions": [{"date": "no-date", "course": "OWS", "block": "InvalidBlock"}],
        }
        bad_path = tmp_root / "bad.json"
        bad_path.write_text(json.dumps(candidates_invalid), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(tmp_root / "scripts" / "import" / "register_schedule.py"),
             "--merge", str(bad_path), "--dry-run"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", env=env, cwd=str(tmp_root),
        )
        if proc.returncode == 2:
            try:
                report = json.loads(proc.stdout or "")
                if len(report.get("errors", [])) >= 3:
                    result.ok("invalid candidates: multiple validation errors reported")
                else:
                    result.fail("register_schedule invalid", f"expected >=3 errors, got {report.get('errors')}")
            except json.JSONDecodeError as exc:
                result.fail("register_schedule invalid JSON", str(exc))
        else:
            result.fail("register_schedule invalid exit code", f"expected 2, got {proc.returncode}")


def main() -> int:
    result = TestResult()
    print(textwrap.dedent(f"""\
        spagent self-test
        repo: {REPO_ROOT}
        python: {sys.executable}
    """))
    test_json(result)
    test_python(result)
    test_watermarks(result)
    test_crosslinks(result)
    test_pii_negatives(result)
    test_pii_positives(result)
    test_knowledge_policy_choices(result)
    test_phase_resolver_fallback(result)
    test_register_schedule(result)

    print("\n=== Summary ===")
    print(f"passed: {result.passed}")
    print(f"failed: {result.failed}")
    if result.failures:
        print("\nFailures:")
        for line in result.failures:
            print(f"  - {line}")
        return 1
    print("\nAll tests passed 🏊‍♀️🐢")
    return 0


if __name__ == "__main__":
    sys.exit(main())
