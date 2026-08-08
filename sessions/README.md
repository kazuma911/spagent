# sessions/

日々の練習セッション記録。**このディレクトリは `.gitignore` で除外されています**（`README.md` のみ公開）。

## 構造

セッションごとに `YYYY-MM-DD/` フォルダを作り、以下のファイルを保持します。

```
sessions/
└─ 2026-08-11/
   ├─ menu.tsv              Skill が生成した予定メニュー
   ├─ times.tsv             実測タイム + RPE
   ├─ feedback.md           総括メモ + メニュー変更履歴
   ├─ menu-executed.json    実施ベースの内部形式（自動生成、索引化用）
   └─ raw/
      └─ *.jpg              撮影メモ画像
```

## ワークフロー

- **メニュー作成**: [Workflow A](../SKILL.md#workflow-a-練習メニュー作成) → `menu.tsv` 生成
- **記録・フィードバック**: [Workflow B](../SKILL.md#workflow-b-記録フィードバック) → `raw/*.jpg` 投入 → `times.tsv` + `feedback.md` 作成
- **索引化**: `scripts/index/import_tsv_menus.py YYYY-MM-DD` で `knowledge/custom/menu-index.json` に反映

## PII 保護

- `raw/*.jpg` の画像はコーチ承認後のみ処理、Exif GPS 削除推奨
- 顔・名札は自動マスク（Workflow B の PII 検知ステップ）
- 詳細は [`docs/security.md`](../docs/security.md) を参照
