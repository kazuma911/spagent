# =============================================================================
# spagent Launcher (Windows / PowerShell)
# =============================================================================
# spagent を「使う」ためのスクリプト。**毎回**これを叩けば動きます。
#
# - 初回: 必要なものを全部インストール（Python / Git / VS Code / Copilot 拡張 / 依存ライブラリ）
# - 2 回目以降: 既にあるものはスキップし、数秒で VS Code を立ち上げます
#
# 使い方: PowerShell を開いて以下を実行
#
#   iex (irm https://raw.githubusercontent.com/kazuma911/spagent/main/scripts/setup/setup.ps1)
#
# または、リポジトリを既に clone 済みなら:
#
#   .\scripts\setup\setup.ps1
#
# オプション:
#   -SkipVSCode              VS Code とその拡張の導入をスキップ
#   -SkipCopilotExtension    Copilot 拡張のインストール確認をスキップ
#   -SkipClone               リポジトリ clone をスキップ
#   -NoLaunch                最後に VS Code を起動しない
#   -InstallDir <path>       clone 先を指定 (既定: $HOME\spagent)
# =============================================================================

[CmdletBinding()]
param(
    [switch]$SkipVSCode,
    [switch]$SkipCopilotExtension,
    [switch]$SkipClone,
    [switch]$NoLaunch,
    [string]$InstallDir = "$HOME\spagent"
)

$ErrorActionPreference = "Stop"
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "  [OK] $msg"   -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  [!]  $msg"   -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "  [X]  $msg"   -ForegroundColor Red }

function Refresh-Path {
    $env:Path =
        [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
        [System.Environment]::GetEnvironmentVariable("Path", "User")
}

function Test-Command($name) {
    $null = Get-Command $name -ErrorAction SilentlyContinue
    return $?
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  spagent Launcher (Windows)          " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# -----------------------------------------------------------------------------
# 1. winget 確認
# -----------------------------------------------------------------------------
Write-Step "winget 確認"
if (Test-Command winget) {
    Write-Ok "winget: $(winget --version)"
} else {
    Write-Err "winget が見つかりません。"
    Write-Host "  Windows 10 (1809 以降) または Windows 11 で最新の App Installer をご利用ください。"
    Write-Host "  https://apps.microsoft.com/detail/9nblggh4nns1 からインストールしてください。"
    exit 1
}

# -----------------------------------------------------------------------------
# 2. Python
# -----------------------------------------------------------------------------
Write-Step "Python 3.10+ 確認"
$needPython = $true
if (Test-Command python) {
    $verLine = (python --version 2>&1) -join ""
    if ($verLine -match "Python 3\.(\d+)") {
        $minor = [int]$Matches[1]
        if ($minor -ge 10) {
            Write-Ok "$verLine"
            $needPython = $false
        } else {
            Write-Warn "$verLine (3.10 以上が必要)"
        }
    }
}
if ($needPython) {
    Write-Host "  Python 3.11 を winget でインストールします..."
    winget install --id Python.Python.3.11 -e --accept-source-agreements --accept-package-agreements --silent
    Refresh-Path
    if (Test-Command python) {
        Write-Ok "Python installed: $(python --version 2>&1)"
    } else {
        Write-Err "Python のインストールに失敗しました。PowerShell を再起動してから再実行してください。"
        exit 1
    }
}

# pip 確認 & upgrade
Write-Step "pip 確認・アップグレード"
if (-not (Test-Command pip)) {
    Write-Host "  pip が見つかりません。ensurepip で復旧を試みます..."
    python -m ensurepip --upgrade
    Refresh-Path
}
python -m pip install --upgrade pip
Write-Ok "pip: $(python -m pip --version)"

# -----------------------------------------------------------------------------
# 3. Git
# -----------------------------------------------------------------------------
Write-Step "Git 確認"
if (Test-Command git) {
    Write-Ok "$(git --version)"
} else {
    Write-Host "  Git を winget でインストールします..."
    winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements --silent
    Refresh-Path
    if (Test-Command git) {
        Write-Ok "Git installed: $(git --version)"
    } else {
        Write-Err "Git のインストールに失敗しました。PowerShell を再起動してから再実行してください。"
        exit 1
    }
}

# -----------------------------------------------------------------------------
# 4. VS Code
# -----------------------------------------------------------------------------
if (-not $SkipVSCode) {
    Write-Step "VS Code 確認"
    if (Test-Command code) {
        Write-Ok "code CLI 見つかりました"
    } else {
        Write-Host "  VS Code を winget でインストールします..."
        winget install --id Microsoft.VisualStudioCode -e --accept-source-agreements --accept-package-agreements --silent
        Refresh-Path
        if (Test-Command code) {
            Write-Ok "VS Code installed"
        } else {
            Write-Warn "VS Code の code CLI が見つかりません。手動で PATH を通してください。"
        }
    }

    # ---------------------------------------------------------------------------
    # 5. GitHub Copilot 拡張
    # ---------------------------------------------------------------------------
    if ((-not $SkipCopilotExtension) -and (Test-Command code)) {
        Write-Step "GitHub Copilot 拡張 インストール"
        $ext = code --list-extensions 2>&1
        if ($ext -match "GitHub.copilot(\b|$)") {
            Write-Ok "GitHub.copilot 既に導入済み"
        } else {
            code --install-extension GitHub.copilot --force | Out-Null
            Write-Ok "GitHub.copilot"
        }
        if ($ext -match "GitHub.copilot-chat(\b|$)") {
            Write-Ok "GitHub.copilot-chat 既に導入済み"
        } else {
            code --install-extension GitHub.copilot-chat --force | Out-Null
            Write-Ok "GitHub.copilot-chat"
        }
    }
} else {
    Write-Step "VS Code (SkipVSCode 指定によりスキップ)"
}

# -----------------------------------------------------------------------------
# 6. リポジトリ clone
# -----------------------------------------------------------------------------
$repoDir = $null
function Update-Repo($dir) {
    if (-not (Test-Path (Join-Path $dir ".git"))) { return }
    if (-not (Test-Command git)) { return }
    Write-Host "  最新の main を取り込みます (git pull --ff-only)" -ForegroundColor DarkGray
    $prevErr = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        git -C $dir fetch --quiet origin main 2>$null
        $fetchOk = ($LASTEXITCODE -eq 0)
        git -C $dir pull --ff-only --quiet origin main 2>$null
        $pullOk = ($LASTEXITCODE -eq 0)
        if ($fetchOk -and $pullOk) {
            Write-Ok "main ブランチ 最新化"
        } else {
            Write-Warn "pull スキップ (ローカル変更やブランチ差分がある可能性)"
        }
    } finally {
        $ErrorActionPreference = $prevErr
    }
}

if (Test-Path "SKILL.md") {
    $repoDir = (Get-Location).Path
    Write-Step "リポジトリ確認: 既に spagent フォルダ内 ($repoDir)"
    Write-Ok "SKILL.md 発見"
    if (-not $SkipClone) { Update-Repo $repoDir }
} elseif ($SkipClone) {
    Write-Warn "SKILL.md が見つかりませんが SkipClone 指定のためスキップ"
} else {
    Write-Step "リポジトリ clone / 更新"
    if (Test-Path "$InstallDir\SKILL.md") {
        Write-Ok "既に $InstallDir に clone 済み"
        $repoDir = $InstallDir
        Update-Repo $repoDir
    } else {
        if (Test-Path $InstallDir) {
            Write-Warn "$InstallDir が存在しますが SKILL.md がありません。別のパスを指定してください。"
            Write-Host "  例: .\setup.ps1 -InstallDir C:\spagent"
            exit 1
        }
        git clone https://github.com/kazuma911/spagent.git $InstallDir
        Write-Ok "clone 完了 → $InstallDir"
        $repoDir = $InstallDir
    }
    Set-Location $repoDir
}

# -----------------------------------------------------------------------------
# 7. Python 依存インストール
# -----------------------------------------------------------------------------
Write-Step "Python 依存ライブラリ インストール (Pillow / reportlab / openpyxl / pdfplumber)"
$reqPath = "scripts\requirements.txt"
if (-not (Test-Path $reqPath)) {
    Write-Err "$reqPath が見つかりません。spagent フォルダ内で実行しているか確認してください。"
    exit 1
}
python -m pip install -r $reqPath
Write-Ok "全依存ライブラリのインストール完了"

# -----------------------------------------------------------------------------
# 8. 動作確認
# -----------------------------------------------------------------------------
Write-Step "動作確認"
python -c "import PIL, reportlab, openpyxl, pdfplumber; print('  Pillow:', PIL.__version__); print('  reportlab:', reportlab.Version); print('  openpyxl:', openpyxl.__version__); print('  pdfplumber:', pdfplumber.__version__)"

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "  準備 OK！ spagent を起動します       " -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""

# -----------------------------------------------------------------------------
# 9. VS Code 起動 + Copilot Chat への起動メッセージ提示
# -----------------------------------------------------------------------------
$launchPrompt = "#SKILL.md を読み込んで、今日のメニューを一緒に作りたい。まだ初期セットアップしていなければ Workflow E から始めて。"

if ($NoLaunch) {
    Write-Host "  (-NoLaunch 指定のため VS Code は起動しません)" -ForegroundColor Yellow
} elseif ($repoDir -and (Test-Command code)) {
    Write-Host "  VS Code で spagent を開いています..." -ForegroundColor Cyan
    Start-Process code -ArgumentList @("`"$repoDir`"", "`"$repoDir\SKILL.md`"")
    Start-Sleep -Seconds 1
    Write-Ok "VS Code 起動"
} else {
    Write-Warn "VS Code の code CLI がないため自動起動できません。手動で spagent フォルダを開いてください。"
}

Write-Host ""
Write-Host "次にやること:" -ForegroundColor Cyan
Write-Host "  1. VS Code で GitHub Copilot にサインイン (右下のアイコンから、初回のみ)"
Write-Host "  2. Copilot Chat を開く (Ctrl+Alt+I)"
Write-Host "  3. 下のメッセージをコピーして送信 (👇 クリップボードに入れました)"
Write-Host ""
Write-Host "     $launchPrompt" -ForegroundColor White
Write-Host ""

try {
    Set-Clipboard -Value $launchPrompt -ErrorAction Stop
    Write-Ok "起動メッセージをクリップボードにコピーしました。Copilot Chat で Ctrl+V → Enter で送信"
} catch {
    Write-Warn "クリップボードへのコピーに失敗しました。上のメッセージを手動でコピーしてください。"
}

Write-Host ""
Write-Host "楽しんで！ 🏊‍♀️🐢" -ForegroundColor Cyan
