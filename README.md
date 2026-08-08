# spagent — Swim Practice Agent 🏊‍♀️

> **「自分の分身を作ってみたら練習メニュー作成の時間がゼロになった話」**

水泳の練習メニュー作成を、あなたの指導哲学と過去メニューから抽出した骨格パターンで自動化する **GitHub Copilot Skill** です。コーチ（メニュー担当者）向けに、非エンジニアでも使えるように書きました。

## 目次

- [これは何？](#これは何)
- [向いている人](#向いている人)
- [用意するもの](#用意するもの)
- [インストール（3 ステップ）](#インストール3-ステップ)
- [初回セットアップ（10 分）](#初回セットアップ10-分)
- [毎回の使い方](#毎回の使い方)
- [できること一覧](#できること一覧)
- [4 層トレーニングモデル](#4-層トレーニングモデル)
- [個人情報 (PII) の扱い](#個人情報-pii-の扱い)
- [用語ミニ辞典](#用語ミニ辞典)
- [困ったときは](#困ったときは)
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

## 用意するもの

これだけあれば動きます。

| 必要なもの | 説明 |
|---|---|
| **Windows / Mac / Linux** の PC | OS はどれでも OK |
| **Python 3.10 以上** | https://www.python.org/downloads/ からダウンロード。インストール時「Add Python to PATH」に必ずチェック |
| **GitHub Copilot が使える環境** | VS Code の GitHub Copilot 拡張、または GitHub Copilot CLI |
| **ネット接続** | 初回のダウンロードと Copilot の実行に必要 |

Python がすでに入っているか確認したい場合：

```powershell
# Windows (PowerShell)
python --version
```

```bash
# Mac / Linux
python3 --version
```

`Python 3.10.x` 以上なら OK です。

## インストール（3 ステップ）

### ステップ 1: リポジトリを取得

```powershell
# Windows (PowerShell)
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

### ステップ 2: 必要なライブラリを入れる

```powershell
# Windows
pip install -r scripts\requirements.txt
```

```bash
# Mac / Linux
pip3 install -r scripts/requirements.txt
```

必須は **Pillow** ひとつだけ。以下は使う機能が出てきたときに追加で入れれば OK：

| 機能 | 追加コマンド |
|---|---|
| PDF 出力 | `pip install reportlab` |
| Excel テンプレート出力 / 取り込み | `pip install openpyxl` |
| PDF 取り込み | `pip install pdfplumber` |

### ステップ 3: GitHub Copilot に SKILL.md を読み込ませる

**VS Code の場合**：
1. VS Code で `spagent` フォルダを開く
2. GitHub Copilot Chat を開く
3. `#SKILL.md` を添えて「この Skill を使いたい」と依頼

**GitHub Copilot CLI の場合**：
1. `cd spagent` で移動
2. `copilot` などのコマンドで起動（環境により差あり）
3. Skill を明示的に読ませる指示を送る

初回起動時、Copilot が **PII 注意喚起** と **初期セットアップ** の案内を出したら成功です。

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
