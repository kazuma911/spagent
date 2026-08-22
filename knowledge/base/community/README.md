# Community-Contributed Knowledge

コーチが取り込んだ過去メニュー・ドリル・骨格パターンを公開したもの (Workflow G Step 8 で AI 分類済み)。

**構造**:
- `main-menus/<method>/` — AI 分類済みメインメニュー (117 パターン)
- `drills/` — 追加ドリル (6 カテゴリ)
- `menu-index.json` — 検索インデックス (`source: "community"`)
- `drill-index.json` — ドリル索引
- `menu-structure-patterns.json` — 骨格パターン

**使い方**: Workflow A Step 10 / 10.5 / 11 で Base 候補と並んで自動的にサジェストされます。

**PII 精査**: 全ファイル `scripts/pii/text_pii_check.py` でクリーン確認済。
