#!/usr/bin/env bash
# =============================================================================
# spagent Test Runner (macOS / Linux)
# =============================================================================
# 全セルフテストを実行します。
#   bash scripts/tests/run_all_tests.sh
# =============================================================================

set -euo pipefail
export PYTHONIOENCODING=utf-8
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Running spagent self-tests from $REPO_ROOT"
python3 "$SCRIPT_DIR/run_all_tests.py"
