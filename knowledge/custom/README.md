# knowledge/custom/

コーチ固有の知識ベース。**このディレクトリは `.gitignore` で除外されています**（`README.md` のみ公開）。

## 目的

コーチが手動追加した、または過去メニュー / ドリル取り込み（[Workflow G](../../SKILL.md#workflow-g-過去メニュードリル取り込み傾向分析)）で自動生成された Custom 知識を保持します。

## 構造

```
knowledge/custom/
├─ drills/                    追加ドリル（.md）
├─ main-menus/                追加メインメニュー（.md）
├─ methods/                   過去メニューから抽出された「コーチ独自手法」（.md）
├─ overrides/                 base/ の同名ファイルを上書き
├─ imports/
│  ├─ raw/                    取り込み元素材（.xlsx / .pdf / .jpg 等）
│  └─ parsed/                 解析結果 JSON（承認前）
├─ menu-index.json            実施ベース索引（自動追記）
├─ menu-import-analysis.json  傾向分析結果（コーチ承認後）
└─ menu-structure-patterns.json  メニュー骨格パターン（承認後、プロファイルから参照）
```

## 使い方

### 1. 過去メニュー / ドリルを取り込む

コーチが持つ Excel / PDF / 画像を `imports/raw/` に配置し、Skill に「取り込んで」と依頼すると Workflow G が起動します。取り込み後：

- メニュー: `main-menus/YYYY-MM-DD-<slug>.md` + `menu-index.json`
- ドリル: `drills/<stroke>.md`
- 傾向: `menu-import-analysis.json`
- 骨格パターン: `menu-structure-patterns.json`
- 独自手法: `methods/<slug>.md`

### 2. base/ を上書きする

例: `base/drills/freestyle.md` の一部だけ変えたい場合は `overrides/drills/freestyle.md` を作成すると、Skill はまず overrides を、次に base を参照します。

### 3. 使用範囲を制御する

`data/coach-preferences.json` の `use_base_knowledge` で custom / base の使い分けが可能。詳細は [`docs/customization.md`](../../docs/customization.md) 参照。

## PII 保護

`imports/raw/` に置いた元ファイルは PII を含む可能性が高いため、取り込み後の削除を推奨します（Skill が案内）。詳細は [`docs/security.md`](../../docs/security.md) 参照。
