#!/usr/bin/env bash
# =============================================================================
# spagent Launcher (macOS / Linux)
# =============================================================================
# spagent を「使う」ためのスクリプト。**毎回**これを叩けば動きます。
#
# - 初回: 必要なものを全部インストール（Python / Git / Node.js / GitHub Copilot CLI / 依存ライブラリ）
# - 2 回目以降: 既にあるものはスキップし、数秒で Copilot CLI を立ち上げます
#
# 使い方:
#
#   curl -fsSL https://raw.githubusercontent.com/kazuma911/spagent/main/scripts/setup/setup.sh | bash
#
# または、リポジトリを既に clone 済みなら:
#
#   bash scripts/setup/setup.sh
#
# オプション:
#   --skip-copilot-cli         GitHub Copilot CLI の導入をスキップ
#   --skip-clone               リポジトリ clone をスキップ
#   --no-launch                最後に Copilot CLI を起動しない
#   --install-dir=<path>       clone 先を指定（既定: $HOME/spagent）
# =============================================================================

set -euo pipefail

SKIP_COPILOT_CLI=0
SKIP_CLONE=0
NO_LAUNCH=0
INSTALL_DIR="${HOME}/spagent"

for arg in "$@"; do
  case "$arg" in
    --skip-copilot-cli) SKIP_COPILOT_CLI=1 ;;
    --skip-clone) SKIP_CLONE=1 ;;
    --no-launch) NO_LAUNCH=1 ;;
    --install-dir=*) INSTALL_DIR="${arg#*=}" ;;
    -h|--help)
      grep -E '^#( |$)' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "Unknown argument: $arg"; exit 1 ;;
  esac
done

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'
step() { echo -e "\n${CYAN}==> $*${NC}"; }
ok()   { echo -e "  ${GREEN}[OK]${NC} $*"; }
warn() { echo -e "  ${YELLOW}[!] ${NC} $*"; }
err()  { echo -e "  ${RED}[X] ${NC} $*"; }

echo ""
echo -e "${CYAN}======================================${NC}"
echo -e "${CYAN}  spagent Launcher (macOS / Linux)    ${NC}"
echo -e "${CYAN}======================================${NC}"

# -----------------------------------------------------------------------------
# OS 判定
# -----------------------------------------------------------------------------
step "OS 判定"
OS="unknown"
case "$(uname -s)" in
  Darwin*) OS="mac"; ok "macOS" ;;
  Linux*)  OS="linux"; ok "Linux ($(uname -r))" ;;
  *) err "未サポートの OS: $(uname -s)"; exit 1 ;;
esac

PKG_MGR=""
if [[ "$OS" == "mac" ]]; then
  if ! command -v brew >/dev/null 2>&1; then
    step "Homebrew インストール"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    if [[ -d "/opt/homebrew/bin" ]]; then
      eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
  fi
  ok "brew: $(brew --version | head -n1)"
  PKG_MGR="brew"
else
  if command -v apt-get >/dev/null 2>&1; then PKG_MGR="apt"
  elif command -v dnf >/dev/null 2>&1; then PKG_MGR="dnf"
  elif command -v pacman >/dev/null 2>&1; then PKG_MGR="pacman"
  else err "対応パッケージマネージャが見つかりません (apt / dnf / pacman)"; exit 1
  fi
  ok "package manager: $PKG_MGR"
fi

# -----------------------------------------------------------------------------
# Python 3.10+
# -----------------------------------------------------------------------------
step "Python 3.10+ 確認"
py_ok=0
if command -v python3 >/dev/null 2>&1; then
  ver=$(python3 --version 2>&1 | awk '{print $2}')
  major=$(echo "$ver" | cut -d. -f1); minor=$(echo "$ver" | cut -d. -f2)
  if [[ "$major" -eq 3 && "$minor" -ge 10 ]]; then
    ok "Python $ver"
    py_ok=1
  else
    warn "Python $ver (3.10 以上が必要)"
  fi
fi

if [[ "$py_ok" -eq 0 ]]; then
  case "$PKG_MGR" in
    brew)   brew install python@3.11 ;;
    apt)    sudo apt-get update && sudo apt-get install -y python3.11 python3-pip python3.11-venv ;;
    dnf)    sudo dnf install -y python3.11 python3-pip ;;
    pacman) sudo pacman -S --noconfirm python python-pip ;;
  esac
  ok "Python installed: $(python3 --version)"
fi

# -----------------------------------------------------------------------------
# pip
# -----------------------------------------------------------------------------
step "pip 確認・アップグレード"
if ! command -v pip3 >/dev/null 2>&1 && ! python3 -m pip --version >/dev/null 2>&1; then
  case "$PKG_MGR" in
    brew)   ok "brew の python は pip 同梱" ;;
    apt)    sudo apt-get install -y python3-pip ;;
    dnf)    sudo dnf install -y python3-pip ;;
    pacman) sudo pacman -S --noconfirm python-pip ;;
  esac
fi
python3 -m pip install --upgrade pip
ok "pip: $(python3 -m pip --version)"

# -----------------------------------------------------------------------------
# Git
# -----------------------------------------------------------------------------
step "Git 確認"
if command -v git >/dev/null 2>&1; then
  ok "$(git --version)"
else
  case "$PKG_MGR" in
    brew)   brew install git ;;
    apt)    sudo apt-get install -y git ;;
    dnf)    sudo dnf install -y git ;;
    pacman) sudo pacman -S --noconfirm git ;;
  esac
  ok "Git installed: $(git --version)"
fi

# -----------------------------------------------------------------------------
# Node.js + GitHub Copilot CLI
# -----------------------------------------------------------------------------
if [[ "$SKIP_COPILOT_CLI" -eq 0 ]]; then
  step "Node.js 22+ 確認"
  node_ok=0
  if command -v node >/dev/null 2>&1; then
    node_ver=$(node --version 2>&1 | sed 's/^v//')
    node_major=$(echo "$node_ver" | cut -d. -f1)
    if [[ "$node_major" -ge 22 ]]; then
      ok "Node.js $node_ver"
      node_ok=1
    else
      warn "Node.js $node_ver (22 以上が必要)"
    fi
  fi
  if [[ "$node_ok" -eq 0 ]]; then
    case "$PKG_MGR" in
      brew)   brew install node ;;
      apt)
        curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
        sudo apt-get install -y nodejs
        ;;
      dnf)
        curl -fsSL https://rpm.nodesource.com/setup_22.x | sudo -E bash -
        sudo dnf install -y nodejs
        ;;
      pacman) sudo pacman -S --noconfirm nodejs npm ;;
    esac
    ok "Node.js installed: $(node --version)"
  fi

  step "GitHub Copilot CLI 確認"
  if command -v copilot >/dev/null 2>&1; then
    ok "copilot 既に導入済み ($(copilot --version 2>/dev/null | head -n1)) (スキップ)"
  else
    echo "  npm で @github/copilot をインストールします..."
    if npm install -g @github/copilot 2>/dev/null; then
      :
    else
      warn "グローバルインストールに失敗。sudo 付きで再試行します..."
      sudo npm install -g @github/copilot
    fi
    if command -v copilot >/dev/null 2>&1; then
      ok "GitHub Copilot CLI installed"
    else
      warn "copilot コマンドが PATH に見つかりません。シェルを再起動してください。"
    fi
  fi
else
  step "GitHub Copilot CLI (--skip-copilot-cli 指定によりスキップ)"
fi

# -----------------------------------------------------------------------------
# リポジトリ clone
# -----------------------------------------------------------------------------
REPO_DIR=""
if [[ -f "SKILL.md" ]]; then
  REPO_DIR="$(pwd)"
  step "リポジトリ確認: 既に spagent フォルダ内 ($REPO_DIR)"
  ok "SKILL.md 発見"
  if [[ "$SKIP_CLONE" -eq 0 ]] && [[ -d ".git" ]] && command -v git >/dev/null 2>&1; then
    echo "  最新の main を取り込みます (git pull --ff-only)"
    if git -C "$REPO_DIR" fetch --quiet origin main 2>/dev/null \
       && git -C "$REPO_DIR" pull --ff-only --quiet origin main 2>/dev/null; then
      ok "main ブランチ 最新化"
    else
      warn "pull スキップ (ローカル変更やブランチ差分がある可能性)"
    fi
  fi
elif [[ "$SKIP_CLONE" -eq 1 ]]; then
  warn "SKILL.md が見つかりませんが --skip-clone 指定のためスキップ"
else
  step "リポジトリ clone / 更新"
  if [[ -f "$INSTALL_DIR/SKILL.md" ]]; then
    ok "既に $INSTALL_DIR に clone 済み"
    REPO_DIR="$INSTALL_DIR"
    if [[ -d "$INSTALL_DIR/.git" ]] && command -v git >/dev/null 2>&1; then
      echo "  最新の main を取り込みます (git pull --ff-only)"
      if git -C "$REPO_DIR" fetch --quiet origin main 2>/dev/null \
         && git -C "$REPO_DIR" pull --ff-only --quiet origin main 2>/dev/null; then
        ok "main ブランチ 最新化"
      else
        warn "pull スキップ (ローカル変更やブランチ差分がある可能性)"
      fi
    fi
  else
    if [[ -d "$INSTALL_DIR" ]]; then
      err "$INSTALL_DIR が存在しますが SKILL.md がありません。別のパスを --install-dir=... で指定してください。"
      exit 1
    fi
    git clone https://github.com/kazuma911/spagent.git "$INSTALL_DIR"
    ok "clone 完了 → $INSTALL_DIR"
    REPO_DIR="$INSTALL_DIR"
  fi
  cd "$REPO_DIR"
fi

# -----------------------------------------------------------------------------
# Python 依存インストール
# -----------------------------------------------------------------------------
step "Python 依存ライブラリ インストール (Pillow / reportlab / openpyxl / pdfplumber)"
if [[ ! -f "scripts/requirements.txt" ]]; then
  err "scripts/requirements.txt が見つかりません。spagent フォルダ内で実行しているか確認してください。"
  exit 1
fi
python3 -m pip install -r scripts/requirements.txt
ok "全依存ライブラリのインストール完了"

# -----------------------------------------------------------------------------
# 動作確認
# -----------------------------------------------------------------------------
step "動作確認"
python3 -c "import PIL, reportlab, openpyxl, pdfplumber; print('  Pillow:', PIL.__version__); print('  reportlab:', reportlab.Version); print('  openpyxl:', openpyxl.__version__); print('  pdfplumber:', pdfplumber.__version__)"

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  準備 OK！ spagent を起動します       ${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

# -----------------------------------------------------------------------------
# GitHub Copilot CLI 起動 + セッション提示
# -----------------------------------------------------------------------------
LAUNCH_PROMPT="このリポジトリの SKILL.md を読み込んで、今日のメニューを一緒に作りたい。まだ初期セットアップしていなければ Workflow E から始めて。"

if [[ "$NO_LAUNCH" -eq 1 ]]; then
  warn "--no-launch 指定のため GitHub Copilot CLI は起動しません"
elif [[ -n "$REPO_DIR" ]] && command -v copilot >/dev/null 2>&1; then
  echo -e "${CYAN}  GitHub Copilot CLI を起動しています ($REPO_DIR)...${NC}"
  echo ""
  echo -e "${CYAN}起動後、以下をそのまま貼付して Enter:${NC}"
  echo -e "     ${GREEN}${LAUNCH_PROMPT}${NC}"
  echo ""
  exec copilot -C "$REPO_DIR"
else
  warn "copilot コマンドがないため自動起動できません。ターミナルを開き直して \"copilot -C $REPO_DIR\" を実行してください。"
fi

echo ""
echo -e "${CYAN}次にやること:${NC}"
echo "  1. Copilot CLI 初回起動時は 'copilot login' で GitHub にサインイン"
echo "  2. 下のメッセージを貼り付けて送信 (👇 クリップボードに入れました)"
echo ""
echo -e "     ${GREEN}${LAUNCH_PROMPT}${NC}"
echo ""

copied=0
if [[ "$OS" == "mac" ]] && command -v pbcopy >/dev/null 2>&1; then
  printf '%s' "$LAUNCH_PROMPT" | pbcopy && copied=1
elif command -v xclip >/dev/null 2>&1; then
  printf '%s' "$LAUNCH_PROMPT" | xclip -selection clipboard && copied=1
elif command -v wl-copy >/dev/null 2>&1; then
  printf '%s' "$LAUNCH_PROMPT" | wl-copy && copied=1
fi

if [[ "$copied" -eq 1 ]]; then
  ok "起動メッセージをクリップボードにコピーしました。Copilot CLI の入力欄で Ctrl+V (macOS: Cmd+V) → Enter で送信"
else
  warn "クリップボードへのコピーに失敗（pbcopy / xclip / wl-copy 未導入）。上のメッセージを手動でコピーしてください。"
fi

echo ""
echo -e "${CYAN}楽しんで！ 🏊‍♀️🐢${NC}"
