"""SPA scenario regression tests.

以下を自動検証する:

* Excel import ができ、350+ シートから 90%+ で date が抽出できていること (T02)
* PDF import ができ、少なくとも 1 PDF あたり 10 行以上抽出できること (T03)
* Custom-only 宣言が data/coach-preferences.json に存在すること (T04)
* Workflow A 生成物 sessions/2026-08-11/menu.tsv が PII クリーンで round-trip 可能 (T05)
* data/*.json 全体が PII scanner でクリーン (T10)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
RAW_IMPORTS = REPO_ROOT / "knowledge" / "custom" / "imports" / "raw"


@dataclass
class TestResult:
    """Track pass/fail counts and messages."""

    passed: int = 0
    failed: int = 0
    messages: list[str] = field(default_factory=list)

    def ok(self, name: str) -> None:
        """Record a pass."""
        self.passed += 1
        print(f"  [PASS] {name}")

    def fail(self, name: str, reason: str) -> None:
        """Record a failure."""
        self.failed += 1
        self.messages.append(f"{name}: {reason}")
        print(f"  [FAIL] {name}: {reason}")


def section(title: str) -> None:
    """Print a section header."""
    print(f"\n== {title} ==")


def _env() -> dict[str, str]:
    """Return env dict with PYTHONIOENCODING=utf-8 for child processes."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def test_excel_import_quality(result: TestResult) -> None:
    """T02: Excel 取り込みが 350 シート級で meta を高精度で拾えるか."""
    section("T02: SPA.xlsx import (350 sheets, meta extraction)")
    xlsx = RAW_IMPORTS / "SPA.xlsx"
    if not xlsx.exists():
        result.fail("SPA.xlsx", f"missing: {xlsx}")
        return
    out = REPO_ROOT / "sessions" / "_test-t02" / "excel-import.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "import" / "excel_to_menu.py"), str(xlsx), "--out", str(out)],
        env=_env(), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if completed.returncode != 0:
        result.fail("excel_to_menu.py", completed.stderr.strip()[:200])
        return
    data = json.loads(out.read_text(encoding="utf-8"))
    total = len(data)
    if total < 300:
        result.fail("record count", f"got {total}, expected >= 300")
    else:
        result.ok(f"record count: {total}")
    date_ok = sum(1 for m in data if m.get("date"))
    facility_ok = sum(1 for m in data if m.get("facility"))
    team_ok = sum(1 for m in data if m.get("team_name"))
    if date_ok / total < 0.95:
        result.fail("date coverage", f"{date_ok}/{total}")
    else:
        result.ok(f"date coverage: {date_ok}/{total}")
    if facility_ok / total < 0.90:
        result.fail("facility coverage", f"{facility_ok}/{total}")
    else:
        result.ok(f"facility coverage: {facility_ok}/{total}")
    if team_ok / total < 0.90:
        result.fail("team_name coverage", f"{team_ok}/{total}")
    else:
        result.ok(f"team_name coverage: {team_ok}/{total}")
    bad_id = sum(1 for m in data if not m.get("date") or "(" in (m.get("date") or ""))
    if bad_id > 0:
        result.fail("id sanity", f"{bad_id} records have malformed date component")
    else:
        result.ok("id sanity (dates are all clean YYYY-MM-DD)")
    row_leak = 0
    for m in data:
        for r in m.get("structure", []):
            if any(str(v).startswith("Team Alpha") for v in r.values()):
                row_leak += 1
    if row_leak > 0:
        result.fail("Team Alpha leak into rows", f"{row_leak} rows")
    else:
        result.ok("no Team Alpha watermark leaked into body rows")


def test_pdf_import_quality(result: TestResult) -> None:
    """T03: SPA PDF から meta と行が取れているか."""
    section("T03: SPA PDF import (meta + body extraction)")
    pdfs = ["SPA-20260529.pdf", "SPA-20260609.pdf", "SPA-20260613.pdf"]
    for pdf_name in pdfs:
        pdf = RAW_IMPORTS / pdf_name
        if not pdf.exists():
            result.fail(f"{pdf_name}", "missing file")
            continue
        out = REPO_ROOT / "sessions" / "_test-t03" / (pdf_name.replace(".pdf", ".json"))
        out.parent.mkdir(parents=True, exist_ok=True)
        completed = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "import" / "pdf_to_menu.py"), str(pdf), "--out", str(out)],
            env=_env(), capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if completed.returncode != 0:
            result.fail(f"{pdf_name}", completed.stderr.strip()[:200])
            continue
        data = json.loads(out.read_text(encoding="utf-8"))
        record = data[0]
        if not record.get("date"):
            result.fail(f"{pdf_name} date", "not extracted")
        else:
            result.ok(f"{pdf_name} date: {record['date']}")
        rows = len(record.get("structure", []))
        if rows < 10:
            result.fail(f"{pdf_name} row count", f"got {rows}, expected >= 10")
        else:
            result.ok(f"{pdf_name} rows: {rows}")


def test_custom_only_preference(result: TestResult) -> None:
    """T04: coach-preferences.json が Custom-only を宣言していること."""
    section("T04: coach-preferences custom_only")
    prefs_path = REPO_ROOT / "data" / "coach-preferences.json"
    if not prefs_path.exists():
        result.fail("coach-preferences.json", "missing")
        return
    prefs = json.loads(prefs_path.read_text(encoding="utf-8"))
    if prefs.get("use_base_knowledge") != "custom_only":
        result.fail("use_base_knowledge", f"got {prefs.get('use_base_knowledge')!r}, want 'custom_only'")
    else:
        result.ok("use_base_knowledge = custom_only")
    detail = prefs.get("use_base_knowledge_detail", {})
    if any(detail.get(k) for k in ("drills", "main_menus", "warmup_cooldown", "menu_index_seed")):
        result.fail("use_base_knowledge_detail", f"expected all False, got {detail}")
    else:
        result.ok("all detail flags are False")


def test_workflow_a_output(result: TestResult) -> None:
    """T05: sessions/2026-08-11/menu.tsv が正しく round-trip できること."""
    section("T05: Workflow A output (menu.tsv → xlsx → import)")
    menu_tsv = REPO_ROOT / "sessions" / "2026-08-11" / "menu.tsv"
    if not menu_tsv.exists():
        result.fail("menu.tsv", "missing (expected after Workflow A demo)")
        return
    result.ok("menu.tsv exists")

    pii = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "pii" / "text_pii_check.py"), str(menu_tsv)],
        env=_env(), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if pii.returncode != 0:
        result.fail("menu.tsv PII", pii.stdout.strip()[:200])
    else:
        result.ok("menu.tsv PII clean")

    src_xlsx = RAW_IMPORTS / "SPA.xlsx"
    if not src_xlsx.exists():
        result.fail("SPA.xlsx source", "missing")
        return
    appended = REPO_ROOT / "sessions" / "2026-08-11" / "SPA-appended.xlsx"
    import shutil
    shutil.copy2(src_xlsx, appended)
    export = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "export" / "tsv_to_excel_custom.py"),
         str(menu_tsv), "--append-to", str(appended), "--new-sheet-name", "11-08-26"],
        env=_env(), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if export.returncode != 0:
        result.fail("tsv_to_excel_custom.py", export.stderr.strip()[:200])
        return
    result.ok("append-to new sheet succeeded")

    roundtrip = REPO_ROOT / "sessions" / "2026-08-11" / "roundtrip.json"
    reimport = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "import" / "excel_to_menu.py"),
         str(appended), "--sheet-name", "11-08-26", "--out", str(roundtrip)],
        env=_env(), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if reimport.returncode != 0:
        result.fail("round-trip import", reimport.stderr.strip()[:200])
        return
    data = json.loads(roundtrip.read_text(encoding="utf-8"))
    r = data[0]
    if r.get("date") != "2026-08-11":
        result.fail("round-trip date", f"got {r.get('date')!r}")
    else:
        result.ok("round-trip date preserved")
    if r.get("team_name") != "Team Alpha":
        result.fail("round-trip team_name", f"got {r.get('team_name')!r}")
    else:
        result.ok("round-trip team_name preserved")
    if len(r.get("structure", [])) < 8:
        result.fail("round-trip rows", f"got {len(r.get('structure', []))}, expected >= 8")
    else:
        result.ok(f"round-trip rows: {len(r['structure'])}")


def test_data_pii_clean(result: TestResult) -> None:
    """T10: data/ 配下の JSON が PII scanner でクリーンなこと."""
    section("T10: data/ PII scan (real athletes / schedules)")
    data_dir = REPO_ROOT / "data"
    for json_path in sorted(data_dir.glob("*.json")):
        pii = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "pii" / "text_pii_check.py"), str(json_path)],
            env=_env(), capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if pii.returncode != 0:
            result.fail(f"data/{json_path.name}", pii.stdout.strip()[:200])
        else:
            result.ok(f"data/{json_path.name} PII clean")


def main() -> int:
    """Run SPA scenario tests."""
    result = TestResult()
    print(f"SPA scenario test suite: repo={REPO_ROOT}")
    test_excel_import_quality(result)
    test_pdf_import_quality(result)
    test_custom_only_preference(result)
    test_workflow_a_output(result)
    test_data_pii_clean(result)
    print("\n=== SPA scenarios Summary ===")
    print(f"passed: {result.passed}")
    print(f"failed: {result.failed}")
    if result.messages:
        print("\nFailures:")
        for msg in result.messages:
            print(f"  - {msg}")
    return 1 if result.failed else 0


if __name__ == "__main__":
    sys.exit(main())
