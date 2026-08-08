# data/

コーチ担当領域（実データ格納）。**このディレクトリは `.gitignore` で除外されています**（`README.md` のみ公開）。

## 目的

指導プロファイル・選手情報・施設・大会・ペース・環境設定など、コーチ固有の実データを保持します。PII（個人情報）を含む可能性が高いため、リポジトリには含めません。

## セットアップ

初回起動時、Skill が [Workflow E](../SKILL.md#workflow-e-初期セットアップ) を案内し、以下のファイルを対話式に生成します。`templates/*.template.json` をひな形として使ってください。

| ファイル | 役割 | ひな形 |
|---|---|---|
| `athletes.json` | 選手情報（エイリアス推奨） | `templates/athletes.template.json` |
| `groups.json` | クラス／グループ情報、`profile_id` 保持 | `templates/groups.template.json` |
| `coaching-profiles.json` | 指導プロファイル（対象×時間軸×骨格パターン） | `templates/coaching-profiles.template.json` |
| `facilities.json` | プール施設情報 | `templates/facilities.template.json` |
| `competitions.json` | 大会情報・エントリー | `templates/competitions.template.json` |
| `training-schedule.json` | 練習予定 | `templates/training-schedule.template.json` |
| `current-paces.json` | 各選手の現在ペース | `templates/current-paces.template.json` |
| `output-preferences.json` | 出力形式設定 | `templates/output-preferences.template.json` |
| `excel-template-mapping.json` | カスタム Excel テンプレートのセルマッピング | （初回のみ Skill が自動生成） |
| `coach-preferences.json` | プロファイル横断のコーチ設定 | `templates/coach-preferences.template.json` |
| `pii-blocklist.json` | PII ブロックリスト | （初回のみ Skill が自動生成） |
| `athlete-conditions.json` | 選手の怪我・体調・欠席履歴 | `templates/athlete-conditions.template.json` |
| `athlete-skill-notes.json` | 選手の技術課題・カルテ | `templates/athlete-skill-notes.template.json` |
| `athlete-insights.json` | AI 学習の選手適応傾向（コーチ承認済み） | `templates/athlete-insights.template.json` |

## PII 保護

- 選手氏名はエイリアス（ニックネームまたはイニシャル）で登録
- 電話・メール・住所・生年月日は入力を避ける
- 詳細は [`docs/security.md`](../docs/security.md) を参照
