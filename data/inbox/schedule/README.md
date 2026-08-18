# data/inbox/schedule/

このフォルダは **スケジュール登録のファイル入力受け皿** です。
Workflow E / F の 3 モード登録のうち「② ファイル」で使います。

## 使い方

1. 大会予定や練習予定が書かれた Excel / PDF / CSV / TXT / Markdown をこのフォルダに置く
2. Copilot CLI で「大会を登録したい (ファイルから)」と伝える → Workflow F.schedule が起動
3. Skill 内部で以下を実行:
   ```
   python scripts/import/register_schedule.py --mode file \
     --input data/inbox/schedule/<your-file> \
     --output data/inbox/schedule/<your-file>.raw.json
   ```
4. LLM が raw.json を読み、**candidates.json** (下記スキーマ) に変換して見せる
5. コーチが確認 → 修正 → OK なら:
   ```
   python scripts/import/register_schedule.py --merge candidates.json
   ```

## candidates.json スキーマ

```json
{
  "competitions": [
    {
      "id": "2026-11-tokyo-masters-lcm",
      "name": "2026 東京マスターズ LCM",
      "start_date": "2026-11-15",
      "end_date": "2026-11-15",
      "course": "LCM",
      "priority": "A",
      "venue": "東京アクアティクスセンター",
      "location_city": "東京都",
      "entries": [
        {"athlete_id": "haruto", "event": "100Fr", "target_time": "58.90"}
      ]
    }
  ],
  "sessions": [
    {"date": "2026-08-25", "dow": "火", "course": "SCM", "block": "Acc", "focus": "USRPT 50s", "managed_by": "self"}
  ]
}
```

## サポートするファイル形式

| 形式 | 抽出方法 |
|---|---|
| `.xlsx` / `.xlsm` / `.xls` | openpyxl で全シートの非空セル |
| `.pdf` | pdfplumber でテキスト + テーブル |
| `.csv` / `.tsv` / `.txt` / `.md` | テキスト直読 (先頭 20KB) |

## PII 注意

このフォルダは `.gitignore` 済みです。コーチのローカルファイルとして扱われ、
GitHub には push されません。ただし他のツールでバックアップされる可能性は
考慮してください。個人特定情報 (フルネーム、生年月日、電話番号など) を
含むファイルを長期保管しないでください。
