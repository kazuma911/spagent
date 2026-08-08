# spagent — Swim Practice Agent

> **「自分の分身を作ってみたら練習メニュー作成の時間がゼロになった話」**
>
> 水泳の練習メニュー作成・長期プラン設計を、あなたの指導哲学と過去メニューから抽出した骨格パターンで自動化する **GitHub Copilot Skill**。

## これは何？

**spagent** は、水泳コーチ / メニュー作成担当者向けの GitHub Copilot Skill です。あなたの指導プロファイル（対象哲学 × 時間軸 × 実務ひな形）と過去メニューを取り込むと、あなたと同じ流儀でメニューを組む「AI 分身」ができあがります。

- ✅ 集団指導と個別指導の両立
- ✅ 過去メニュー / ドリル資料の取り込み（Excel / PDF / 画像）
- ✅ 傾向分析からのメニュー骨格パターン抽出
- ✅ Phase × Zone × Method の三層タギングによる横断検索
- ✅ 既存 Excel テンプレートへの出力
- ✅ PII（個人情報）保護を前提とした設計

## 対象読者

- マスターズ社会人スイマーのコーチ
- ジュニアクラブのコーチ
- 集団指導のフィットネスインストラクター
- 個人選手の自己コーチング
- トライアスロン選手 / コーチ

## 必要環境

- **OS**: Windows / macOS / Linux
- **Python**: 3.10 以上
- **必須ライブラリ**: `Pillow`
- **オプション**:
  - `reportlab` (PDF 出力)
  - `openpyxl` (カスタム Excel 出力)
  - `pdfplumber` (PDF 取り込み)
- **Skill 動作環境**: GitHub Copilot の Skill を読み込める環境（VS Code、Copilot CLI 等）

詳細: [docs/installation.md](docs/installation.md)

## インストール

```bash
git clone https://github.com/<owner>/spagent.git
cd spagent
pip install -r scripts/requirements.txt
```

その後、Copilot CLI 等で `SKILL.md` を読み込ませ、「spagent を使いたい」と依頼すると **Workflow E（初期セットアップ）** が起動します。

## クイックスタート

1. **セットアップ** — 「セットアップして」→ Skill が対話でグループ・プロファイル・施設・大会を登録
2. **過去メニュー取り込み**（任意）— 「過去のメニューを取り込みたい」→ Excel/PDF/画像を投入 → 傾向分析
3. **メニュー作成** — 「明日のメニューを作って」→ Skill が Phase / Zone / Method / 骨格パターンを提案 → 承認後 TSV 保存

詳細: [docs/getting-started.md](docs/getting-started.md)

## 主な機能

| # | 機能 | 対応 Workflow |
|---|------|---------------|
| 1 | 練習メニュー作成 | A |
| 2 | 記録・フィードバック（画像→タイム認識） | B |
| 3 | 過去メニュー索引参照 | C |
| 4 | 長期プラン作成 | D |
| 5 | 初期セットアップ | E |
| 6 | メンテナンス | F |
| 7 | 過去メニュー / ドリル取り込み & 傾向分析 | G |

詳細: [docs/workflows.md](docs/workflows.md)

## 4 層トレーニングモデル

コーチが任意に組み合わせ可能：

- **Periodization**（時間軸）: Matveyev / Block / Undulating / Reverse
- **Philosophy**（対象哲学）: Masters / Junior / Elite / Triathlon
- **Methods**（手法論）: USRPT / HIIT / LSD / Broken / Threshold / Fartlek / Descending + Custom
- **Macrocycle Templates**（実務ひな形）: Single Peak 12week / Four Peaks Annual / Junior Annual / Triathlon Integrated / Maintenance

詳細: [docs/training-models.md](docs/training-models.md)

## セキュリティ・PII 保護

- 選手氏名はエイリアス（ニックネームまたはイニシャル）で登録
- 電話・メール・住所・生年月日は入力を避ける
- 画像から顔・名札・Exif GPS を自動検出 → マスク
- `data/`, `sessions/`, `plans/`, `knowledge/custom/` は `.gitignore` で除外
- 同意書テンプレート同梱

詳細: [docs/security.md](docs/security.md)

## ドキュメント

- [docs/getting-started.md](docs/getting-started.md) — クイックスタート
- [docs/installation.md](docs/installation.md) — 詳細インストール
- [docs/workflows.md](docs/workflows.md) — 7 種の Workflow 詳細
- [docs/customization.md](docs/customization.md) — カスタマイズと `use_base_knowledge`
- [docs/training-models.md](docs/training-models.md) — 4 層モデル詳細
- [docs/security.md](docs/security.md) — セキュリティ・PII 保護
- [docs/faq.md](docs/faq.md) — よくある質問
- [docs/troubleshooting.md](docs/troubleshooting.md) — トラブルシューティング
- [docs/contributing.md](docs/contributing.md) — 貢献ガイド

## ライセンス

**明示的なライセンスファイルは配置していません**（デフォルトで全著作権保有扱い）。

- **個人利用**: 自由
- **商用利用・再配布**: 要相談

## 変更履歴

[CHANGELOG.md](CHANGELOG.md) を参照。

## Author

network engineer / hobby swim coach — spagent は趣味の水泳コーチング業務を GitHub Copilot Skill 化した副産物です。同じ立場のコーチ・メニュー担当者向けに公開しています。
