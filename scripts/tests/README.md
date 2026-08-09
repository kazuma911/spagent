# spagent 自動テスト

**壊れていないか手元で確かめる**ためのセルフテストです。ランチャー起動が成功しない、
Copilot が予期せぬ反応をする、といったときに最初に叩いてみてください。

## 使い方

**Windows (PowerShell)**
```powershell
.\scripts\tests\run_all_tests.ps1
```

**macOS / Linux**
```bash
bash scripts/tests/run_all_tests.sh
```

**Python 直接**
```bash
python scripts/tests/run_all_tests.py
```

## 何をテストしているか

| 項目 | 内容 |
|---|---|
| JSON validity | `**/*.json` が全部パースできるか |
| Python compilation | `**/*.py` が全部コンパイルできるか |
| Template watermarks | `templates/` 内に `Team Alpha` などの不要文字列が残っていないか |
| Markdown cross-links | SKILL.md / README.md / docs/*.md 内のローカル相対リンクが解決するか |
| PII scanner (negatives) | エイリアス / グループ名 / ニックネームで**誤検出しない**か |
| PII scanner (positives) | フルネーム / メール / 電話 / 生年月日を**ちゃんと検出**するか |
| Knowledge policy choices | Base のみ / Base+Custom / **Custom のみ** の 3 択が SKILL.md に定義されているか |

**成功時**：`All tests passed 🏊‍♀️🐢`（exit 0）
**失敗時**：Failures セクションに詳細（exit 1）

## テストが失敗したら

- **リンク切れ (Markdown cross-links)** → 該当ファイルが存在するか、パスが正しいか確認
- **PII 誤検出 (negatives が FAIL)** → `scripts/pii/text_pii_check.py` の `ALIAS_LABEL_PATTERN` に追加候補があるか検討
- **PII 検出漏れ (positives が FAIL)** → `BUILT_IN_PATTERNS` の該当パターンを確認
- **Watermark (Team Alpha)** → `templates/session-menu.template.tsv` などから該当行を削除
