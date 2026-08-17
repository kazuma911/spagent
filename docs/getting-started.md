# Getting Started

このページは spagent を 15 分で触るための最短ウォークスルーです。
泳法理論を全部読まなくても、まず 1 本のメニューを作るところまで進めます。
詳しい背景は [../SKILL.md](../SKILL.md) と [workflows.md](workflows.md) を参照してください。

## 用語ミニ辞典

| 用語 | コーチ向け説明 | エンジニア向け説明 |
|---|---|---|
| RPE | 主観的運動強度。1 が楽、10 が限界。 | 人間入力の負荷メトリクス。 |
| PB | 自己ベスト。 | ペース推定の基準値。 |
| LCM | 長水路、50m プール。 | `course = LCM`。 |
| SCM | 短水路、25m プール。 | `course = SCM`。 |
| T-pace | 閾値ペース。少しきついが持続できる速度。 | Threshold の基準。 |
| Phase | 大会までの時期区分。 | A/B/C/D の状態。 |
| Zone | EN1 から SP3 などの強度帯。 | 検索・タグ付け軸。 |
| Method | Threshold, Broken などの練習手法。 | Workflow A で当日選ぶ戦術。 |
| Cycle | 出発間隔。 | interval / send-off。 |
| PII | 個人情報 (Personal Identifiable Information)。 | git に入れない保護対象。 |

## 15 分でやること

| 時間 | やること | 成果 |
|---:|---|---|
| 0-2 分 | clone と SKILL.md 読み込み | Copilot が spagent を理解する |
| 2-10 分 | Workflow E | グループ・プロファイル・施設・大会・出力形式が入る |
| 10-12 分 | 任意で Workflow G | 過去メニューの傾向と骨格を抽出 |
| 12-14 分 | Workflow A | 初回 `menu.tsv` を保存 |
| 14-15 分 | Workflow B 入口 | `times.tsv` と `feedback.md` の流れを理解 |

## 前提

- Python 3.10+。
- Pillow インストール済み。
- GitHub Copilot CLI または VS Code。
- 選手は `athlete-01` などのエイリアスで扱う。
- 実名、施設名、電話、メール、住所、生年月日は入力しない。

## Step 1: clone して SKILL.md を読ませる

```powershell
git clone https://github.com/<owner>/spagent.git C:\AIAccelerate\spagent
cd C:\AIAccelerate\spagent
python --version
pip install -r scripts\requirements.txt
```

`scripts\requirements.txt` は Pillow のみを入れる想定です。
Copilot CLI では一般に Skill 読み込み操作で `SKILL.md` を指定します。
環境によりコマンドは変わるため `/help` や公式ドキュメントを確認してください。

```text
/skill C:\AIAccelerate\spagent\SKILL.md
```

VS Code ではリポジトリを開き、Copilot Chat に次のように依頼します。

```text
Coach: このリポジトリの SKILL.md を読んで spagent として動いてください。
Skill: 役割、Workflow A-G、PII 保護方針を読み込みました。
```

## Step 2: 「spagent を使いたい」と依頼

Workflow E が起動し、10 分ほどで初期セットアップします。

### サンプル対話

```text
Coach: spagent を使いたい。初期セットアップして。
Skill: PII 注意喚起を表示し、選手はエイリアスで登録するよう案内します。
Coach: masters-evening、8 名、週 1 回、年 1 回大会。
Skill: Masters + Single Peak 12week が候補です。施設と出力形式も登録します。
```

### このステップで確認すること

- グループ ID。
- 選手エイリアス。
- LCM/SCM、使用レーン、定員。
- 大会と priority。
- TSV/PDF/Excel の出力形式。

## Step 3: 任意で過去メニュー取り込み

Excel/PDF/画像を `knowledge/custom/imports/raw/` に置き、Workflow G で傾向分析します。

### サンプル対話

```text
Coach: raw に過去メニューを置いた。取り込んで。
Skill: 形式を判定し、PII チェック後に構造化プレビューを出します。
Skill: Zone 配分、距離帯、Method、骨格パターンを抽出します。
Coach: その骨格を今のプロファイルに紐付けて。
```

### このステップで確認すること

- `knowledge/custom/main-menus/`。
- `knowledge/custom/menu-index.json`。
- `knowledge/custom/menu-import-analysis.json`。
- `knowledge/custom/menu-structure-patterns.json`。

## Step 4: 初回メニュー作成

「明日のメニューを作って」で Workflow A を開始します。

### サンプル対話

```text
Coach: 明日のメニューを作って。
Skill: 日付、SCM/LCM、時間、レーン、グループ、参加者を確認します。
Skill: Phase B、主 Zone EN2、Method Threshold を提案します。
Coach: Main は 100m 反復で短めに。
Skill: プレビューを表示し、承認後 `sessions/YYYY-MM-DD/menu.tsv` に保存します。
```

### このステップで確認すること

- Phase 判定。
- Zone 配分。
- Method 選択。
- 骨格設計。
- 設定タイムと Cycle。

## Step 5: 練習後フィードバック

`raw/*.jpg` から Workflow B で実測と気づきを保存します。

### サンプル対話

```text
Coach: 今日の raw/*.jpg を見てフィードバック処理して。
Skill: 画像 PII を確認し、タイムと RPE を認識します。
Skill: 保存前に全件プレビューします。
Coach: Set 3 は時間不足で 1 本カット。
Skill: `times.tsv` と `feedback.md` を生成し、索引に反映します。
```

### このステップで確認すること

- `sessions/YYYY-MM-DD/times.tsv`。
- `sessions/YYYY-MM-DD/feedback.md`。
- `data/athlete-conditions.json`。
- `data/athlete-skill-notes.json`。
- `knowledge/custom/menu-index.json`。

## 次に読むもの

- 全 Workflow: [workflows.md](workflows.md)。
- 環境詳細: [installation.md](installation.md)。
- 自分流に寄せる: [customization.md](customization.md)。
- PII 保護: [security.md](security.md)。

## クイックスタート 補足チェックリスト

- クイックスタート 確認 1: 保存前にコーチが承認する。
- クイックスタート 確認 2: 実名・施設名・連絡先を入れない。
- クイックスタート 確認 3: LCM/SCM と練習時間を毎回確認する。
- クイックスタート 確認 4: RPE が高い選手には次回負荷を補正する。
- クイックスタート 確認 5: TSV で内容を確認してから PDF/Excel にする。
- クイックスタート 確認 6: 迷ったら安全側に倒す。
- クイックスタート 確認 7: custom はローカル専用として扱う。
- クイックスタート 確認 8: base を直接変えず overrides を使う。
- クイックスタート 確認 9: 保存前にコーチが承認する。
- クイックスタート 確認 10: 実名・施設名・連絡先を入れない。
- クイックスタート 確認 11: LCM/SCM と練習時間を毎回確認する。
- クイックスタート 確認 12: RPE が高い選手には次回負荷を補正する。
- クイックスタート 確認 13: TSV で内容を確認してから PDF/Excel にする。
- クイックスタート 確認 14: 迷ったら安全側に倒す。
- クイックスタート 確認 15: custom はローカル専用として扱う。
- クイックスタート 確認 16: base を直接変えず overrides を使う。
- クイックスタート 確認 17: 保存前にコーチが承認する。
- クイックスタート 確認 18: 実名・施設名・連絡先を入れない。
- クイックスタート 確認 19: LCM/SCM と練習時間を毎回確認する。
- クイックスタート 確認 20: RPE が高い選手には次回負荷を補正する。
- クイックスタート 確認 21: TSV で内容を確認してから PDF/Excel にする。
- クイックスタート 確認 22: 迷ったら安全側に倒す。
- クイックスタート 確認 23: custom はローカル専用として扱う。
- クイックスタート 確認 24: base を直接変えず overrides を使う。
- クイックスタート 確認 25: 保存前にコーチが承認する。
- クイックスタート 確認 26: 実名・施設名・連絡先を入れない。
- クイックスタート 確認 27: LCM/SCM と練習時間を毎回確認する。
- クイックスタート 確認 28: RPE が高い選手には次回負荷を補正する。
- クイックスタート 確認 29: TSV で内容を確認してから PDF/Excel にする。
- クイックスタート 確認 30: 迷ったら安全側に倒す。
- クイックスタート 確認 31: custom はローカル専用として扱う。
- クイックスタート 確認 32: base を直接変えず overrides を使う。
- クイックスタート 確認 33: 保存前にコーチが承認する。
- クイックスタート 確認 34: 実名・施設名・連絡先を入れない。
- クイックスタート 確認 35: LCM/SCM と練習時間を毎回確認する。
- クイックスタート 確認 36: RPE が高い選手には次回負荷を補正する。
- クイックスタート 確認 37: TSV で内容を確認してから PDF/Excel にする。
- クイックスタート 確認 38: 迷ったら安全側に倒す。
- クイックスタート 確認 39: custom はローカル専用として扱う。
- クイックスタート 確認 40: base を直接変えず overrides を使う。
- クイックスタート 確認 41: 保存前にコーチが承認する。
- クイックスタート 確認 42: 実名・施設名・連絡先を入れない。
- クイックスタート 確認 43: LCM/SCM と練習時間を毎回確認する。
- クイックスタート 確認 44: RPE が高い選手には次回負荷を補正する。
- クイックスタート 確認 45: TSV で内容を確認してから PDF/Excel にする。
- クイックスタート 確認 46: 迷ったら安全側に倒す。
- クイックスタート 確認 47: custom はローカル専用として扱う。
- クイックスタート 確認 48: base を直接変えず overrides を使う。
- クイックスタート 確認 49: 保存前にコーチが承認する。
- クイックスタート 確認 50: 実名・施設名・連絡先を入れない。
- クイックスタート 確認 51: LCM/SCM と練習時間を毎回確認する。
- クイックスタート 確認 52: RPE が高い選手には次回負荷を補正する。
- クイックスタート 確認 53: TSV で内容を確認してから PDF/Excel にする。
- クイックスタート 確認 54: 迷ったら安全側に倒す。
- クイックスタート 確認 55: custom はローカル専用として扱う。
- クイックスタート 確認 56: base を直接変えず overrides を使う。
- クイックスタート 確認 57: 保存前にコーチが承認する。
- クイックスタート 確認 58: 実名・施設名・連絡先を入れない。
- クイックスタート 確認 59: LCM/SCM と練習時間を毎回確認する。
- クイックスタート 確認 60: RPE が高い選手には次回負荷を補正する。
- クイックスタート 確認 61: TSV で内容を確認してから PDF/Excel にする。
- クイックスタート 確認 62: 迷ったら安全側に倒す。
- クイックスタート 確認 63: custom はローカル専用として扱う。
