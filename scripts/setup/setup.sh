#!/usr/bin/env bash
# =============================================================================
# spagent Launcher (macOS / Linux)
# =============================================================================
# spagent を「使う」ためのスクリプト。**毎回**これを叩けば動きます。
#
# - 初回: 必要なものを全部インストール（Python / Git / VS Code / Copilot 拡張 / 依存ライブラリ）
# - 2 回目以降: 既にあるものはスキップし、数秒で VS Code を立ち上げます
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
#   --skip-vscode              VS Code とその拡張の導入をスキップ
#   --skip-copilot-extension   Copilot 拡張のインストール確認をスキップ
#   --skip-clone               リポジトリ clone をスキップ
#   --no-launch                最後に VS Code を起動しない
#   --install-dir=<path>       clone 先を指定（既定: $HOME/spagent）
# =============================================================================

set -euo pipefail

SKIP_VSCODE=0
SKIP_COPILOT_EXT=0
SKIP_CLONE=0
NO_LAUNCH=0
INSTALL_DIR="${HOME}/spagent"

for arg in "$@"; do
  case "$arg" in
    --skip-vscode) SKIP_VSCODE=1 ;;
    --skip-copilot-extension) SKIP_COPILOT_EXT=1 ;;
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
# VS Code
# -----------------------------------------------------------------------------
if [[ "$SKIP_VSCODE" -eq 0 ]]; then
  step "VS Code 確認"
  if command -v code >/dev/null 2>&1; then
    ok "code CLI 見つかりました"
  else
    case "$OS" in
      mac)
        brew install --cask visual-studio-code
        ;;
      linux)
        case "$PKG_MGR" in
          apt)
            if ! grep -q "packages.microsoft.com/repos/code" /etc/apt/sources.list.d/vscode.list 2>/dev/null; then
              sudo apt-get install -y wget gpg apt-transport-https
              wget -qO- https://packages.microsoft.com/keys/microsoft.asc \
                | gpg --dearmor > packages.microsoft.gpg
              sudo install -D -o root -g root -m 644 packages.microsoft.gpg \
                /etc/apt/keyrings/packages.microsoft.gpg
              sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
              rm packages.microsoft.gpg
              sudo apt-get update
            fi
            sudo apt-get install -y code
            ;;
          dnf)
            sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
            sudo sh -c 'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo'
            sudo dnf install -y code
            ;;
          pacman)
            warn "Arch Linux では AUR から visual-studio-code-bin を導入してください: yay -S visual-studio-code-bin"
            ;;
        esac
        ;;
    esac
    if command -v code >/dev/null 2>&1; then
      ok "VS Code installed"
    else
      warn "VS Code の code CLI が見つかりません。手動確認してください。"
    fi
  fi

  # ---------------------------------------------------------------------------
  # GitHub Copilot 拡張
  # ---------------------------------------------------------------------------
  if [[ "$SKIP_COPILOT_EXT" -eq 0 ]] && command -v code >/dev/null 2>&1; then
    step "GitHub Copilot 拡張 インストール"
    installed=$(code --list-extensions 2>/dev/null || true)
    if echo "$installed" | grep -qi "^GitHub.copilot$"; then
      ok "GitHub.copilot 既に導入済み"
    else
      code --install-extension GitHub.copilot --force >/dev/null
      ok "GitHub.copilot"
    fi
    if echo "$installed" | grep -qi "^GitHub.copilot-chat$"; then
      ok "GitHub.copilot-chat 既に導入済み"
    else
      code --install-extension GitHub.copilot-chat --force >/dev/null
      ok "GitHub.copilot-chat"
    fi
  fi
else
  step "VS Code (--skip-vscode 指定によりスキップ)"
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
# VS Code 起動 + Copilot Chat への起動メッセージ提示
# -----------------------------------------------------------------------------
LAUNCH_PROMPT="#SKILL.md を読み込んで、今日のメニューを一緒に作りたい。まだ初期セットアップしていなければ Workflow E から始めて。"

if [[ "$NO_LAUNCH" -eq 1 ]]; then
  warn "--no-launch 指定のため VS Code は起動しません"
elif [[ -n "$REPO_DIR" ]] && command -v code >/dev/null 2>&1; then
  echo -e "${CYAN}  VS Code で spagent を開いています...${NC}"
  code "$REPO_DIR" "$REPO_DIR/SKILL.md" >/dev/null 2>&1 || true
  sleep 1
  ok "VS Code 起動"
else
  warn "VS Code の code CLI がないため自動起動できません。手動で spagent フォルダを開いてください。"
fi

echo ""
echo -e "${CYAN}次にやること:${NC}"
echo "  1. VS Code で GitHub Copilot にサインイン (右下のアイコンから、初回のみ)"
echo "  2. Copilot Chat を開く (Ctrl+Alt+I / macOS: Cmd+Ctrl+I)"
echo "  3. 下のメッセージをコピーして送信 (👇 クリップボードに入れました)"
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
  ok "起動メッセージをクリップボードにコピーしました。Copilot Chat で Ctrl+V (macOS: Cmd+V) → Enter で送信"
else
  warn "クリップボードへのコピーに失敗（pbcopy / xclip / wl-copy 未導入）。上のメッセージを手動でコピーしてください。"
fi

echo ""
echo -e "${CYAN}楽しんで！ 🏊‍♀️🐢${NC}"
