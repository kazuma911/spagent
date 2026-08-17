# インストール詳細

**多くの場合はランチャー 1 行で全部入ります。** 以下は「うまくいかなかった」「自動化に頼りたくない」時の詳細ガイドです。

```powershell
# Windows: これで Python / Git / VS Code / Copilot 拡張まで全部入る
iwr https://raw.githubusercontent.com/kazuma911/spagent/main/scripts/setup/setup.ps1 -OutFile $env:TEMP\spagent-launcher.ps1; & $env:TEMP\spagent-launcher.ps1
```
```bash
# Mac / Linux: 同上
curl -fsSL https://raw.githubusercontent.com/kazuma911/spagent/main/scripts/setup/setup.sh | bash
```

まずは [README のクイックスタート](../README.md#使い方最速) を試してください。ここは **詰まったとき用の詳細ガイド** です。

## 前提のおさらい

- OS: Windows / Mac / Linux
- Python 3.10 以上
- GitHub Copilot が使える環境（VS Code + Copilot 拡張、または Copilot CLI）
- ネット接続

## Python のインストール

### Windows

1. https://www.python.org/downloads/ から Python 3.10 以上を DL
2. インストーラを起動、**「Add python.exe to PATH」に必ずチェック**
3. インストール後、新しい PowerShell を開いて確認：

```powershell
python --version
```

`Python 3.10.x` 以上なら OK。

### Mac

Homebrew 推奨：

```bash
brew install python@3.11
python3 --version
```

または https://www.python.org/downloads/macos/ から公式インストーラ。

### Linux

ディストリのパッケージで：

```bash
# Ubuntu / Debian
sudo apt install python3.11 python3-pip

# Fedora
sudo dnf install python3.11 python3-pip

python3 --version
```

## 仮想環境 (venv) を使うか

**使わなくても動きます**。ただし他のプロジェクトと Python ライブラリを分けたい場合は仮想環境が便利です。

```powershell
# Windows
cd C:\spagent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r scripts\requirements.txt
```

```bash
# Mac / Linux
cd ~/spagent
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
```

以降 `spagent` フォルダで作業する前に `Activate.ps1`（Windows）や `source .venv/bin/activate`（Mac/Linux）で仮想環境を有効化してください。

## 必須ライブラリ

```
Pillow>=10.0.0
```

これだけです。

## 使う機能ごとの追加ライブラリ

必要になった時点で入れれば OK。

| 機能 | 必要ライブラリ | インストール |
|---|---|---|
| PDF 出力 | `reportlab` | `pip install reportlab` |
| カスタム Excel 出力 | `openpyxl` | `pip install openpyxl` |
| Excel から過去メニュー取り込み | `openpyxl` | `pip install openpyxl` |
| PDF から過去メニュー取り込み | `pdfplumber` | `pip install pdfplumber` |

## GitHub Copilot Skill としての読み込ませ方

### VS Code + Copilot Chat

1. VS Code で `spagent` フォルダを **フォルダとして開く**（File → Open Folder）
2. Copilot Chat を開く
3. 最初のメッセージで `#SKILL.md` をアタッチして「この Skill を使いたい」と依頼

### GitHub Copilot CLI

Copilot CLI のインストールは公式ドキュメントを参照：

- https://docs.github.com/copilot
- https://cli.github.com/

`spagent` フォルダで起動すれば、Copilot が周辺の `SKILL.md` を認識します。うまく認識しない場合は「`SKILL.md` を読んで」と明示的に依頼してください。

## よくあるインストールトラブル

### Python: `'python' は認識されません`

**原因**: Python の PATH が通っていない（Windows）
**対処**:
1. Python を再インストールし、**「Add python.exe to PATH」にチェック**
2. または、`py` コマンドを使う（`py --version`）
3. Mac / Linux では `python3` と入力

### pip: `Permission denied`

**原因**: システム全体にインストールしようとして権限がない
**対処**:
1. **仮想環境を使う**（上記 venv 手順）
2. または `pip install --user -r scripts/requirements.txt`（ユーザー領域だけに入れる）
3. 会社支給 PC ではポリシー上インストールが制限されている場合あり、情シスへ確認

### Pillow: Windows で `error: Microsoft Visual C++ 14.0 or greater is required`

**原因**: 古い Python か、C++ ビルドツール不足
**対処**:
1. `python -m pip install --upgrade pip` で pip 更新
2. Python を 3.10 以上に更新（通常はプリビルドされた wheel が入るはず）
3. それでも駄目な場合は https://visualstudio.microsoft.com/visual-cpp-build-tools/ から Build Tools を導入

### Copilot が SKILL.md を無視する

**原因**: 別フォルダで開いている / Skill が読み込まれていない
**対処**:
1. `spagent` を **プロジェクトルートとして開いているか** 確認
2. Copilot Chat で `#SKILL.md` を明示的にアタッチ
3. 会話冒頭で「`SKILL.md` を最初に読んでから答えて」と指示

## 動作確認

インストール後、以下のように会話できれば成功です：

```
あなた: SKILL.md を読み込んで、対応している Workflow を教えて。

Copilot: SKILL.md v0.6.0 を確認しました。以下の 7 種の Workflow に対応しています：
         - Workflow A: 練習メニュー作成
         - Workflow B: 記録・フィードバック
         - Workflow C: 索引参照
         - Workflow D: 長期プラン作成
         - Workflow E: 初期セットアップ
         - Workflow F: メンテナンス
         - Workflow G: 過去メニュー取り込み & 傾向分析
         初めての場合は Workflow E からどうぞ。
```

## 次のステップ

- [README.md § 初回セットアップ](../README.md#初回セットアップ10-分) — 対話でグループ・プロファイル・施設を登録
- [docs/getting-started.md](getting-started.md) — 一連の流れをステップ別に
- [docs/workflows.md](workflows.md) — 7 種の Workflow 詳細
