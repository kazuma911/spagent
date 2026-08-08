# spagent — Swim Practice Agent 🏊‍♀️

> **「自分の分身を作ってみたら練習メニュー作成の時間がゼロになった話」**

水泳の練習メニュー作成を、あなたの指導哲学と過去メニューから抽出した骨格パターンで自動化する **GitHub Copilot Skill** です。コーチ（メニュー担当者）向けに、非エンジニアでも使えるように書きました。

## 目次

- [これは何？](#これは何)
- [向いている人](#向いている人)
- [使い方（最速）](#使い方最速)
- [用意するもの](#用意するもの)
- [インストール & 起動（1 行）](#インストール--起動1-行)
- [初回セットアップ（10 分）](#初回セットアップ10-分)
- [毎回の使い方](#毎回の使い方)
- [できること一覧](#できること一覧)
- [4 層トレーニングモデル](#4-層トレーニングモデル)
- [個人情報 (PII) の扱い](#個人情報-pii-の扱い)
- [用語ミニ辞典](#用語ミニ辞典)
- [困ったときは](#困ったときは)
- [手動でやりたい人向け（従来のやり方）](#手動でやりたい人向け従来のやり方)
- [ライセンス / Author](#ライセンス--author)

## これは何？

**spagent** は、水泳コーチや練習メニュー作成担当者向けの **GitHub Copilot Skill**（GitHub Copilot に読み込ませる指示書）です。

読み込ませると、Copilot があなたの「分身」として動きます。過去メニュー・指導哲学・大会予定を渡すと、あなたと同じ流儀で練習メニューを組んでくれます。

**主なポイント**

- ✅ 集団指導と個別指導の両立
- ✅ Excel / PDF / 画像の過去メニュー・ドリル資料を取り込める
- ✅ 過去メニューから「あなたらしい骨格」を抽出して以後のメニューに反映
- ✅ 大会までの週数からフェーズ（準備期・強化期・仕上期・調整期）を自動判定
- ✅ 選手ごとの怪我・体調・技術課題を継続追跡
- ✅ 個人情報 (PII) はローカルのみで完結、GitHub には送らない設計

## 向いている人

- マスターズ社会人スイマーのコーチ
- ジュニアクラブのコーチ
- 集団指導のフィットネスインストラクター
- 個人選手の自己コーチング
- トライアスロン選手 / コーチ

## 使い方（最速）

**毎回この 1 行を叩けば起動します。** Python も Git も VS Code も Copilot 拡張も、無ければ自動でインストールされます（既にあればスキップ）。

**Windows (PowerShell)**
```powershell
iwr https://raw.githubusercontent.com/kazuma911/spagent/main/scripts/setup/setup.ps1 -OutFile $env:TEMP\spagent-launcher.ps1; & $env:TEMP\spagent-launcher.ps1
```

**Mac / Linux (bash)**
```bash
curl -fsSL https://raw.githubusercontent.com/kazuma911/spagent/main/scripts/setup/setup.sh | bash
```

これで：
1. 必要なもの（Python / Git / VS Code / Copilot 拡張 / Python 依存ライブラリ）を確認・導入
2. `~/spagent`（Windows は `%USERPROFILE%\spagent`）にリポジトリを clone、既にあれば `git pull` で最新化
3. VS Code で spagent フォルダを開く
4. Copilot Chat 用の起動メッセージをクリップボードにコピー

VS Code が立ち上がったら **Copilot Chat を開いて（`Ctrl+Alt+I` / macOS: `Cmd+Ctrl+I`）Ctrl+V → Enter** で送るだけで、あなたの分身が動き出します。

## 用意するもの

**PC とネット接続だけで大丈夫**。他は上の 1 行スクリプトが自動で入れます。

| 必要なもの | 説明 |
|---|---|
| **Windows / Mac / Linux** の PC | OS はどれでも OK |
| **ネット接続** | ダウンロードと Copilot の実行に必要 |
| **GitHub アカウント** | Copilot のサインインに使います（有料の Copilot 契約が必要） |

自動で入るもの：**Python 3.11 / Git / VS Code / GitHub Copilot 拡張 / Copilot Chat 拡張 / Pillow / reportlab / openpyxl / pdfplumber**

## インストール & 起動（1 行）

上の [使い方（最速）](#使い方最速) の 1 行を叩けば以下が全部走ります。**2 回目以降は数秒**で終わって VS Code が立ち上がります（既存はスキップ、リポジトリは `git pull` で最新化）。

**オプション**

```powershell
# 例: VS Code 起動をスキップしたい
iwr https://raw.githubusercontent.com/kazuma911/spagent/main/scripts/setup/setup.ps1 -OutFile $env:TEMP\spagent-launcher.ps1; & $env:TEMP\spagent-launcher.ps1 -NoLaunch
```

```bash
# 例: リポジトリ clone 先を変えたい
curl -fsSL https://raw.githubusercontent.com/kazuma911/spagent/main/scripts/setup/setup.sh | bash -s -- --install-dir=$HOME/work/spagent
```

| フラグ | 意味 |
|---|---|
| `-NoLaunch` / `--no-launch` | 最後の VS Code 起動をスキップ |
| `-SkipClone` / `--skip-clone` | clone / pull をスキップ |
| `-SkipVSCode` / `--skip-vscode` | VS Code の導入をスキップ（既に別途入れている人向け） |
| `-SkipCopilotExtension` / `--skip-copilot-extension` | Copilot 拡張の確認をスキップ |
| `-InstallDir <path>` / `--install-dir=<path>` | clone 先を指定（既定: `~/spagent`） |

**手元に clone 済みの場合**は、リポジトリ内で直接叩けます：
```powershell
# Windows
.\scripts\setup\setup.ps1
```
```bash
# Mac / Linux
bash scripts/setup/setup.sh
```

## 初回セットアップ（10 分）

Copilot が対話で聞いてくるので、順に答えるだけです。以下は例：

```
Copilot: spagent へようこそ。まず、指導対象を教えてください。
         ① 個別選手（複数可）  ② クラス／グループ  ③ 両方

あなた: ③

Copilot: 選手を登録します。表示用エイリアス（ニックネームまたは
         イニシャル）でお願いします。本名は登録しないでください。

あなた: ally、100m 自由形、上級

Copilot: 登録しました: ally / 100Fr / 上級
         次の選手または「終了」と教えてください。

...（続く）

Copilot: プール施設を教えてください。
         例: 長水路 (LCM) 50m、レーン 6 本、1 レーンあたり最大 4 人

あなた: 短水路 (SCM) 25m、3 レーン、1 レーンあたり 3 人

Copilot: 過去のメニュー資料はありますか？
         ① まずは公式ナレッジだけで試す
         ② Excel / PDF / 画像の過去メニューを取り込む（推奨）

あなた: ②

Copilot: knowledge/custom/imports/raw/ にファイルを置くか、
         パスを教えてください。

あなた: C:\coach\2025-menus.xlsx

Copilot: 解析しました。メニュー 42 本を認識、傾向は以下です：
         - Zone 配分: EN2 35% / EN3 30% / SP1 20% / その他 15%（有酸素基礎重視）
         - 骨格パターン: W-up 600 → Kick 300 → Pull 300 → Main 1500-1800 → C-down 300
         - 総距離帯: 3000-3300m
         - 想定対象: マスターズ社会人

         これを「あなたの分身」の初期設定にしますか？

あなた: OK
```

10 分ほどで、あなたの流儀を覚えた分身の完成です。

## 毎回の使い方

**練習前に上の 1 行を叩くだけ。**

```powershell
# Windows
iwr https://raw.githubusercontent.com/kazuma911/spagent/main/scripts/setup/setup.ps1 -OutFile $env:TEMP\spagent-launcher.ps1; & $env:TEMP\spagent-launcher.ps1
```
```bash
# Mac / Linux
curl -fsSL https://raw.githubusercontent.com/kazuma911/spagent/main/scripts/setup/setup.sh | bash
```

数秒で VS Code が立ち上がり、Copilot Chat に貼るための起動メッセージがクリップボードに入っています。あとは：

1. Copilot Chat を開く（`Ctrl+Alt+I` / macOS: `Cmd+Ctrl+I`）
2. `Ctrl+V` → `Enter`

セットアップ済みなら、あとはひとことでメニューが上がってきます。

```
あなた: 明日 20:00-21:30 のメニューを作って。参加者は全員 + 見学 2 名。

Copilot: 明日 2026-08-11(月) のプランを確認しました。
         - コース: SCM 25m
         - 使用レーン: 3 本
         - 参加 10 名（レーン容量 9 名を超えるため群 A/B の交代制を推奨）

         フェーズ判定: B（次の大会まで 6 週）
         主ゾーン: EN3（乳酸閾値付近）
         おすすめ手法: Threshold Training

         骨格（あなたのパターンに沿う）:
         - W-up 500m
         - Kick 300m
         - Pull 300m
         - Main: 4 × (200m Threshold + 50m Recovery) × 2 sets = 2000m
         - C-down 400m

         合計 3500m。この骨格で作りますか？

あなた: いいけど、carol は右肩痛だから Fly はナシで。

Copilot: 承知しました。carol の Pull ブロックだけ Free/Back に差し替えます。
         全体プレビューをお見せしますね。

...（承認後）

Copilot: sessions/2026-08-11/menu.tsv に保存しました。
         PDF も同フォルダに出力済みです。
```

## できること一覧

7 種類の Workflow があります。すべて Copilot に自然文で依頼するだけで動きます。

| # | 依頼例 | Copilot がやること |
|---|---|---|
| **A** | 「明日のメニューを作って」 | フェーズ・強度帯・手法・骨格・タイム設定まで自動、承認後 TSV / PDF 保存 |
| **B** | 「今日のタイム表を投入」 | 撮影したタイム表画像から実測タイムを認識、選手ごとの傾向を学習 |
| **C** | 「Threshold 系の過去メニューは？」 | Phase × Zone × 距離で過去メニューを横断検索 |
| **D** | 「秋の大会まで 12 週の計画を立てて」 | 4 層モデルを使って年間・シーズン計画を生成 |
| **E** | 「初めて使う。セットアップして」 | 選手・グループ・施設・大会・出力形式を対話で登録 |
| **F** | 「新しいグループを追加したい」 | プロファイル追加・ドリル追加・選手情報更新 |
| **G** | 「過去メニューを取り込みたい」 | Excel / PDF / 画像を解析、傾向分析、骨格パターン抽出 |

## 4 層トレーニングモデル

「あなたの分身」の性格を決める 4 つの選択軸。組み合わせは自由で、Copilot が各項目の意味を説明しながら選ばせてくれます。

| 層 | 選択肢 | 何を決めるか |
|---|---|---|
| **Periodization**（時間軸） | Matveyev / Block / Undulating / Reverse | 大会に向けて量と質をどう動かすか |
| **Philosophy**（対象哲学） | Masters / Junior / Elite / Triathlon | 誰向けか、何を優先するか |
| **Methods**（手法論） | USRPT / HIIT / LSD / Broken / Threshold / Fartlek / Descending + あなたの独自手法 | メイン セットの組み立て方 |
| **Macrocycle Templates**（実務ひな形） | Single Peak 12week / Four Peaks Annual / Junior Annual / Triathlon Integrated / Maintenance | 年間の大枠 |

詳細: [docs/training-models.md](docs/training-models.md)

## 個人情報 (PII) の扱い

このスキルは **選手の個人情報を GitHub に送りません**。以下の徹底で守っています。

- **選手氏名はエイリアス**（ニックネームまたはイニシャル）で登録。本名を入れないでください。
- **電話・メール・住所・生年月日** は入力を避けてください。Copilot が検出したら警告します。
- **画像から顔・名札・Exif GPS を自動検出**、必要ならマスク。
- 個人情報が入るフォルダ（`data/` `sessions/` `plans/` `knowledge/custom/`）は `.gitignore` で GitHub 除外。**ローカルの PC 内だけで完結**します。
- 選手・保護者向けの **同意書テンプレート** を [templates/consent-form.template.md](templates/consent-form.template.md) に同梱。

詳細: [docs/security.md](docs/security.md)

## 用語ミニ辞典

Copilot が使う専門用語です。初回だけ覚えれば OK。

| 用語 | 日本語 | 意味 |
|---|---|---|
| RPE | 主観的運動強度 | 選手が感じたきつさ、1（楽）〜10（限界） |
| PB | 自己ベスト | Personal Best、過去最高タイム |
| LCM | 長水路 | 50m プール |
| SCM | 短水路 | 25m プール |
| Phase | フェーズ | 大会までの時期区分（A 準備期 / B 強化期 / C 仕上期 / D 調整期） |
| Zone | 強度帯 | EN1（回復）〜 SP3（全力）の 6 段階 |
| Method | 手法 | Threshold / Broken などメインの組み立て方 |
| Cycle | サイクル | 出発間隔（例: `@ 1'30"`） |
| T-pace | 閾値ペース | 少しきついが持続できるペース |
| PII | 個人情報 | Personal Identifiable Information、本名や連絡先など |

## 困ったときは

### よくある質問と解決

**Python が見つからない**
→ https://www.python.org/downloads/ から Python 3.10 以上をインストール。Windows は「Add Python to PATH」に必ずチェックしてからインストール。

**`pip install` が失敗する（権限エラー）**
→ `pip install --user -r scripts/requirements.txt` を試す。それでもだめなら仮想環境を使う（[docs/installation.md](docs/installation.md) 参照）。

**Copilot が SKILL.md を読んでくれない**
→ `SKILL.md` のあるフォルダにいるか確認。VS Code Chat なら `#SKILL.md` を明示的に添える。

**過去メニューの取り込みで誤認識される**
→ プレビュー段階で「セット 3 を 200×6 IM に修正」など自然文で伝えれば直します。承認までは保存されません。

**選手が急に休んだ・追加された**
→ メニュー作成時に「今日は ben 欠席、代わりに frank 参加」と伝えるだけで反映されます。

もっと詳しく: [docs/faq.md](docs/faq.md) / [docs/troubleshooting.md](docs/troubleshooting.md)

## 手動でやりたい人向け（従来のやり方）

自動スクリプトを使わず、手で入れたい人向けの手順です。

### ステップ 1: Python 3.10 以上を入れる

https://www.python.org/downloads/ から Python 3.10 以上をダウンロード。
Windows は **「Add Python to PATH」に必ずチェック**。

確認：
```powershell
python --version   # Windows
```
```bash
python3 --version  # Mac / Linux
```

### ステップ 2: リポジトリを clone

```powershell
# Windows
cd C:\
git clone https://github.com/kazuma911/spagent.git
cd spagent
```
```bash
# Mac / Linux
cd ~
git clone https://github.com/kazuma911/spagent.git
cd spagent
```

### ステップ 3: 依存ライブラリを入れる

```powershell
# Windows
pip install -r scripts\requirements.txt
```
```bash
# Mac / Linux
pip3 install -r scripts/requirements.txt
```

入るもの：**Pillow / reportlab / openpyxl / pdfplumber**（PDF・Excel・画像処理に使用）

### ステップ 4: VS Code + GitHub Copilot / Copilot Chat 拡張を入れる

VS Code をインストールし、拡張として `GitHub.copilot` と `GitHub.copilot-chat` を入れる。

### ステップ 5: SKILL.md を読み込ませる

VS Code で spagent フォルダを開き、Copilot Chat で以下を送信：

```
#SKILL.md を読み込んで、今日のメニューを一緒に作りたい。まだ初期セットアップしていなければ Workflow E から始めて。
```

### さらに詳しく知りたい

| ドキュメント | 内容 |
|---|---|
| [docs/getting-started.md](docs/getting-started.md) | 詳しいクイックスタート |
| [docs/installation.md](docs/installation.md) | インストールで詰まったとき |
| [docs/workflows.md](docs/workflows.md) | 7 種の Workflow 詳細 |
| [docs/customization.md](docs/customization.md) | 分身をもっとカスタムしたい |
| [docs/training-models.md](docs/training-models.md) | 4 層モデルの選び方 |
| [docs/security.md](docs/security.md) | セキュリティと PII 保護の詳細 |
| [docs/faq.md](docs/faq.md) | よくある質問 |
| [docs/troubleshooting.md](docs/troubleshooting.md) | トラブルシューティング |
| [docs/contributing.md](docs/contributing.md) | 貢献ガイド |
| [SKILL.md](SKILL.md) | Copilot が読む Skill 定義本体 |
| [CHANGELOG.md](CHANGELOG.md) | 変更履歴 |

## ライセンス / Author

**明示的なライセンスファイルは配置していません**（デフォルトで全著作権保有扱い）。

- **個人利用**: 自由
- **商用利用・再配布**: 要相談

**Author**: network engineer / hobby swim coach。趣味の水泳メニュー作成を **GitHub Copilot Skill** 化した副産物です。同じ立場のコーチ・メニュー担当者向けに公開しています。

もう一つの趣味は亀の飼育 🐢
