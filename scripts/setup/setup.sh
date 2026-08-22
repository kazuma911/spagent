#!/usr/bin/env bash
# =============================================================================
# spagent Launcher (macOS / Linux)
# =============================================================================
# spagent を「使う」ためのスクリプト。**毎回**これを叩けば動きます。
#
# - 初回: 必要なものを全部インストール（Python / Git / GitHub Copilot CLI / 依存ライブラリ）
# - 2 回目以降: 既にあるものはスキップし、数秒で spagent フォルダに入ります
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
#   --install-dir=<path>       clone 先を指定（既定: $HOME/spagent）
# =============================================================================

set -euo pipefail

SKIP_COPILOT_CLI=0
SKIP_CLONE=0
INSTALL_DIR="${HOME}/spagent"

for arg in "$@"; do
  case "$arg" in
    --skip-copilot-cli) SKIP_COPILOT_CLI=1 ;;
    --skip-clone) SKIP_CLONE=1 ;;
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
# GitHub Copilot CLI
# -----------------------------------------------------------------------------
if [[ "$SKIP_COPILOT_CLI" -eq 0 ]]; then
  step "GitHub Copilot CLI 確認"
  if command -v copilot >/dev/null 2>&1; then
    ok "copilot コマンド 見つかりました"
  else
    case "$OS" in
      mac)
        if command -v brew >/dev/null 2>&1; then
          brew install github/copilot-cli/copilot 2>/dev/null || {
            warn "Homebrew tap での導入に失敗。npm 経由に切替えます"
            if command -v npm >/dev/null 2>&1; then
              npm install -g @github/copilot
            else
              warn "npm がありません。Node.js 22+ を先に導入してください (brew install node)"
            fi
          }
        elif command -v npm >/dev/null 2>&1; then
          npm install -g @github/copilot
        else
          warn "brew も npm もありません。https://github.com/features/copilot/cli の手順で手動導入してください"
        fi
        ;;
      linux)
        if command -v npm >/dev/null 2>&1; then
          npm install -g @github/copilot
        else
          warn "npm がありません。Node.js 22+ を先に導入してください (例: $PKG_MGR install nodejs)"
        fi
        ;;
    esac
    if command -v copilot >/dev/null 2>&1; then
      ok "GitHub Copilot CLI installed"
    else
      warn "copilot コマンドが見つかりません。シェルを開き直すか、手動で PATH を通してください。"
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
# spagent 起動 (Copilot CLI を直接立ち上げ)
# -----------------------------------------------------------------------------
if [[ -n "$REPO_DIR" ]]; then
  cd "$REPO_DIR"
  ok "作業ディレクトリを spagent に切替: $REPO_DIR"
fi

echo ""
echo -e "${CYAN}GitHub Copilot CLI を起動し、ウェルカムメニューを自動表示します。${NC}"
echo "  - 初回のみ /login で GitHub アカウント認証 (ブラウザが開きます)"
echo "  - メニューが出たら番号 or 自然文で答えてください。"
echo ""
echo -e "${CYAN}楽しんで！ 🏊‍♀️🐢${NC}"
echo ""

if command -v copilot >/dev/null 2>&1; then
  if [[ -t 0 && -t 1 ]]; then
    exec copilot -i "spagent"
  else
    warn "対話端末ではないので自動起動をスキップ。ターミナルで 'copilot -i spagent' と実行してください。"
    warn "  (curl | bash で入れた場合は 'bash <(curl -fsSL ...)' で叩き直すと自動起動できます)"
  fi
else
  warn "copilot コマンドが未検出。シェルを開き直してから 'copilot -i spagent' を実行してください。"
fi
