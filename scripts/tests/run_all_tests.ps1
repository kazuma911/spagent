#!/usr/bin/env pwsh
# =============================================================================
# spagent Test Runner (Windows / PowerShell)
# =============================================================================
# 全セルフテストを実行します。
#   .\scripts\tests\run_all_tests.ps1
# =============================================================================

$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot  = Split-Path -Parent (Split-Path -Parent $scriptDir)

Write-Host "Running spagent self-tests from $repoRoot" -ForegroundColor Cyan
python (Join-Path $scriptDir "run_all_tests.py")
exit $LASTEXITCODE
