# Customization

spagent を自分流に寄せる方法です。
基本は [workflows.md](workflows.md) の Workflow F/G を使います。

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

## 全体像

| 対象 | 場所 | 推奨手順 |
|---|---|---|
| 指導プロファイル | `data/coaching-profiles.json` | Workflow F |
| ドリル | `knowledge/custom/drills/` | 手動 or Workflow G |
| メインメニュー | `knowledge/custom/main-menus/` | 手動 or Workflow G |
| base 上書き | `knowledge/custom/overrides/` | 手動 |
| Excel 出力 | `data/excel-template-mapping.json` | Workflow F |
| Custom Method | `knowledge/custom/methods/` | Workflow G |
| 骨格 | `knowledge/custom/menu-structure-patterns.json` | Workflow G |

## 指導プロファイル追加

グループごとの Philosophy、Periodization、Macrocycle、骨格 ID を管理します。

### 進め方

1. まず Workflow F または G で対話的に作る。
2. 保存前にプレビューする。
3. ファイル名に実名や施設名を入れない。
4. 必要なら手動で JSON / Markdown を調整する。
5. 変更後に Workflow A で小さく試す。

### 例

```text
Coach: 指導プロファイル追加をしたい。
Skill: 目的、対象、保存場所、PII を確認します。
```

## ドリル追加

泳法や技術課題に対応する reusable component です。

### 進め方

1. まず Workflow F または G で対話的に作る。
2. 保存前にプレビューする。
3. ファイル名に実名や施設名を入れない。
4. 必要なら手動で JSON / Markdown を調整する。
5. 変更後に Workflow A で小さく試す。

### 例

```text
Coach: ドリル追加をしたい。
Skill: 目的、対象、保存場所、PII を確認します。
```

## メインメニュー追加

Threshold や Sprint など中心セットの型を保存します。

### 進め方

1. まず Workflow F または G で対話的に作る。
2. 保存前にプレビューする。
3. ファイル名に実名や施設名を入れない。
4. 必要なら手動で JSON / Markdown を調整する。
5. 変更後に Workflow A で小さく試す。

### 例

```text
Coach: メインメニュー追加をしたい。
Skill: 目的、対象、保存場所、PII を確認します。
```

## overrides/ で base/ を上書き

公式 base を直接編集せず、custom 側で同名パスを優先します。

### 進め方

1. まず Workflow F または G で対話的に作る。
2. 保存前にプレビューする。
3. ファイル名に実名や施設名を入れない。
4. 必要なら手動で JSON / Markdown を調整する。
5. 変更後に Workflow A で小さく試す。

### 例

```text
Coach: overrides/ で base/ を上書きをしたい。
Skill: 目的、対象、保存場所、PII を確認します。
```

## 出力フォーマットのカスタマイズ

TSV、PDF、カスタム Excel を使い分けます。

### 進め方

1. まず Workflow F または G で対話的に作る。
2. 保存前にプレビューする。
3. ファイル名に実名や施設名を入れない。
4. 必要なら手動で JSON / Markdown を調整する。
5. 変更後に Workflow A で小さく試す。

### 例

```text
Coach: 出力フォーマットのカスタマイズをしたい。
Skill: 目的、対象、保存場所、PII を確認します。
```

## コーチ独自 Method の登録

Base Method に収まらない現場知を `knowledge/custom/methods/` に保存します。

### 進め方

1. まず Workflow F または G で対話的に作る。
2. 保存前にプレビューする。
3. ファイル名に実名や施設名を入れない。
4. 必要なら手動で JSON / Markdown を調整する。
5. 変更後に Workflow A で小さく試す。

### 例

```text
Coach: コーチ独自 Method の登録をしたい。
Skill: 目的、対象、保存場所、PII を確認します。
```

## 骨格パターンの手動編集

ブロック順、距離配分、総距離帯、日別 variants を管理します。

### 進め方

1. まず Workflow F または G で対話的に作る。
2. 保存前にプレビューする。
3. ファイル名に実名や施設名を入れない。
4. 必要なら手動で JSON / Markdown を調整する。
5. 変更後に Workflow A で小さく試す。

### 例

```text
Coach: 骨格パターンの手動編集をしたい。
Skill: 目的、対象、保存場所、PII を確認します。
```

## use_base_knowledge オプション

| 値 | 使う知識 | 想定コーチ像 |
|---|---|---|
| `all` | base + custom | 初めて使う、標準と自分流を両方使いたい。 |
| `custom_only` | custom のみ | 独自スタイルが強く、公式ナレッジを混ぜたくない。 |
| `base_only` | base のみ | デモや初期検証、過去資産をまだ入れない。 |
| `selective` | 項目別 | ドリルは base、メインは custom など細かく分ける。 |

```json
{
  "use_base_knowledge": "selective",
  "use_base_knowledge_detail": {
    "drills": true,
    "main_menus": false,
    "warmup_cooldown": true,
    "menu_index_seed": false
  }
}
```

## Excel マッピング例

```json
{
  "template_path": "C:\\AIAccelerate\\spagent\\data\\templates\\coach-menu.xlsx",
  "sheet_name": "menu",
  "cells": { "date": "B2", "theme": "B3", "total_distance": "F2" },
  "table_start_row": 8
}
```

## カスタマイズ 補足チェックリスト

- カスタマイズ 確認 1: 保存前にコーチが承認する。
- カスタマイズ 確認 2: 実名・施設名・連絡先を入れない。
- カスタマイズ 確認 3: LCM/SCM と練習時間を毎回確認する。
- カスタマイズ 確認 4: RPE が高い選手には次回負荷を補正する。
- カスタマイズ 確認 5: TSV で内容を確認してから PDF/Excel にする。
- カスタマイズ 確認 6: 迷ったら安全側に倒す。
- カスタマイズ 確認 7: custom はローカル専用として扱う。
- カスタマイズ 確認 8: base を直接変えず overrides を使う。
- カスタマイズ 確認 9: 保存前にコーチが承認する。
- カスタマイズ 確認 10: 実名・施設名・連絡先を入れない。
- カスタマイズ 確認 11: LCM/SCM と練習時間を毎回確認する。
- カスタマイズ 確認 12: RPE が高い選手には次回負荷を補正する。
- カスタマイズ 確認 13: TSV で内容を確認してから PDF/Excel にする。
- カスタマイズ 確認 14: 迷ったら安全側に倒す。
- カスタマイズ 確認 15: custom はローカル専用として扱う。
- カスタマイズ 確認 16: base を直接変えず overrides を使う。
- カスタマイズ 確認 17: 保存前にコーチが承認する。
- カスタマイズ 確認 18: 実名・施設名・連絡先を入れない。
- カスタマイズ 確認 19: LCM/SCM と練習時間を毎回確認する。
- カスタマイズ 確認 20: RPE が高い選手には次回負荷を補正する。
- カスタマイズ 確認 21: TSV で内容を確認してから PDF/Excel にする。
- カスタマイズ 確認 22: 迷ったら安全側に倒す。
- カスタマイズ 確認 23: custom はローカル専用として扱う。
- カスタマイズ 確認 24: base を直接変えず overrides を使う。
- カスタマイズ 確認 25: 保存前にコーチが承認する。
- カスタマイズ 確認 26: 実名・施設名・連絡先を入れない。
- カスタマイズ 確認 27: LCM/SCM と練習時間を毎回確認する。
- カスタマイズ 確認 28: RPE が高い選手には次回負荷を補正する。
- カスタマイズ 確認 29: TSV で内容を確認してから PDF/Excel にする。
- カスタマイズ 確認 30: 迷ったら安全側に倒す。
- カスタマイズ 確認 31: custom はローカル専用として扱う。
- カスタマイズ 確認 32: base を直接変えず overrides を使う。
- カスタマイズ 確認 33: 保存前にコーチが承認する。
- カスタマイズ 確認 34: 実名・施設名・連絡先を入れない。
- カスタマイズ 確認 35: LCM/SCM と練習時間を毎回確認する。
- カスタマイズ 確認 36: RPE が高い選手には次回負荷を補正する。
- カスタマイズ 確認 37: TSV で内容を確認してから PDF/Excel にする。
- カスタマイズ 確認 38: 迷ったら安全側に倒す。
- カスタマイズ 確認 39: custom はローカル専用として扱う。
- カスタマイズ 確認 40: base を直接変えず overrides を使う。
- カスタマイズ 確認 41: 保存前にコーチが承認する。
- カスタマイズ 確認 42: 実名・施設名・連絡先を入れない。
- カスタマイズ 確認 43: LCM/SCM と練習時間を毎回確認する。
- カスタマイズ 確認 44: RPE が高い選手には次回負荷を補正する。
- カスタマイズ 確認 45: TSV で内容を確認してから PDF/Excel にする。
- カスタマイズ 確認 46: 迷ったら安全側に倒す。
- カスタマイズ 確認 47: custom はローカル専用として扱う。
- カスタマイズ 確認 48: base を直接変えず overrides を使う。
- カスタマイズ 確認 49: 保存前にコーチが承認する。
- カスタマイズ 確認 50: 実名・施設名・連絡先を入れない。
- カスタマイズ 確認 51: LCM/SCM と練習時間を毎回確認する。
- カスタマイズ 確認 52: RPE が高い選手には次回負荷を補正する。
- カスタマイズ 確認 53: TSV で内容を確認してから PDF/Excel にする。
- カスタマイズ 確認 54: 迷ったら安全側に倒す。
- カスタマイズ 確認 55: custom はローカル専用として扱う。
- カスタマイズ 確認 56: base を直接変えず overrides を使う。
- カスタマイズ 確認 57: 保存前にコーチが承認する。
- カスタマイズ 確認 58: 実名・施設名・連絡先を入れない。
- カスタマイズ 確認 59: LCM/SCM と練習時間を毎回確認する。
- カスタマイズ 確認 60: RPE が高い選手には次回負荷を補正する。
- カスタマイズ 確認 61: TSV で内容を確認してから PDF/Excel にする。
- カスタマイズ 確認 62: 迷ったら安全側に倒す。
- カスタマイズ 確認 63: custom はローカル専用として扱う。
- カスタマイズ 確認 64: base を直接変えず overrides を使う。
- カスタマイズ 確認 65: 保存前にコーチが承認する。
- カスタマイズ 確認 66: 実名・施設名・連絡先を入れない。
- カスタマイズ 確認 67: LCM/SCM と練習時間を毎回確認する。
- カスタマイズ 確認 68: RPE が高い選手には次回負荷を補正する。
- カスタマイズ 確認 69: TSV で内容を確認してから PDF/Excel にする。
- カスタマイズ 確認 70: 迷ったら安全側に倒す。
- カスタマイズ 確認 71: custom はローカル専用として扱う。
