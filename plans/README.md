# plans/

長期練習計画（シーズン計画・年間計画）。**このディレクトリは `.gitignore` で除外されています**（`README.md` のみ公開）。

## 用途

特定選手 or グループの中長期プランがある場合のみ利用します。ファイル命名は自由ですが、日付範囲や対象を含めると探しやすいです。

```
plans/
├─ 2026-summer-training-plan.md
├─ 2027-annual-junior.md
└─ ally-100fr-sub60-project.md
```

## テンプレート

`templates/training-plan.template.md` に骨格を用意しています。以下の要素を推奨：

- 対象選手 / グループ
- 主要大会と日付
- 4 層モデル選択（Periodization / Philosophy / Methods / Macrocycle）
- 週別テーマ
- 週別 Zone 配分の目安
- マイルストーン（中間チェック大会等）

## Workflow との連携

- [Workflow D](../SKILL.md#workflow-d-長期プラン作成): 大会情報 + 4 層モデル選択から `plans/*.md` を自動生成
- [Workflow A](../SKILL.md#workflow-a-練習メニュー作成): 該当週のテーマを一次情報として参照
