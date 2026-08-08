# Troubleshooting

spagent の問題を「症状」「原因候補」「解決手順」「予防策」で整理します。
エラー文を共有する時は、実名・施設名・画像などの PII を取り除いてください。

## Pillow が入らない

### 症状

`pip install -r scripts\requirements.txt` が Pillow で止まる。

### 原因候補

- Python が古い。
- pip が古い。
- Windows で wheel が使えずビルドが走っている。
- 仮想環境を使っていない。

### 解決手順

1. `python --version` で 3.10+ を確認する。
2. `python -m pip install --upgrade pip` を実行する。
3. `.venv` を作り直す。
4. 必要なら管理者に Visual C++ Build Tools を相談する。

### 予防策

- 仮想環境を使う。
- 古い Python を使い回さない。

## Python 見つからない

### 症状

`python --version` が `Python was not found` になる。

### 原因候補

- Python 未インストール。
- PATH に入っていない。
- Windows のアプリ実行エイリアスが影響している。

### 解決手順

1. Python 3.10+ をインストールする。
2. Add python.exe to PATH を有効にする。
3. `py --version` を試す。
4. PowerShell を開き直す。

### 予防策

- セットアップ直後にバージョン確認する。

## pip permission denied

### 症状

pip が権限エラーで止まる。

### 原因候補

- グローバル Python に書き込もうとしている。
- 組織 PC の権限制約。

### 解決手順

1. `python -m venv .venv` を作る。
2. `.\.venv\Scripts\Activate.ps1` を実行する。
3. 仮想環境内で pip install する。
4. 必要なら `pip install --user` を使う。

### 予防策

- プロジェクトごとに仮想環境を作る。

## 過去メニュー取り込みで解析失敗

### 症状

Workflow G で Excel / PDF / 画像が構造化できない。

### 原因候補

- セル結合が複雑。
- PDF が画像化されている。
- 手書きが読みにくい。
- `openpyxl` や `pdfplumber` がない。

### 解決手順

1. 必要なオプション依存を入れる。
2. 素材を少数に分けて取り込む。
3. プレビューで手動修正する。
4. 次回用に標準テンプレートを作る。

### 予防策

- ファイル名を匿名化する。
- 同じ形式の素材をまとめる。

## PII 検知の誤検出

### 症状

エイリアスや一般語が PII として警告される。

### 原因候補

- ブロックリストが広すぎる。
- 電話番号に似た数字列がある。
- 施設名に見える語がある。

### 解決手順

1. 警告内容を確認する。
2. 本当に PII でなければ承認して進む。
3. `data/pii-blocklist.json` を見直す。

### 予防策

- エイリアスは `athlete-01` のように機械的にする。

## 画像から時間認識できない

### 症状

Workflow B でタイムが抜ける、桁がずれる。

### 原因候補

- 写真が暗い。
- 斜めから撮っている。
- 数字とメモが重なっている。
- 単位や set 番号がない。

### 解決手順

1. 画像を撮り直す。
2. プレビューを手動修正する。
3. 次回から表形式でメモする。
4. RPE とタイムを別列にする。

### 予防策

- 顔や名札が写らない構図にする。
- 太いペンで書く。

## Zone tag が想定と違う

### 症状

EN2 のつもりが EN1 や SP1 と判定される。

### 原因候補

- キーワードが曖昧。
- 独自表現が辞書にない。
- Phase と Method の文脈が不足。

### 解決手順

1. メニューに主 Zone を明示する。
2. [../references/zone-phase-mapping.md](../references/zone-phase-mapping.md) を確認する。
3. `python scripts\index\tag_zones_phases.py` を再実行する。

### 予防策

- Custom Method に想定 Zone を書く。

## JSON パースエラー

### 症状

`data/*.json` を読めず Workflow が止まる。

### 原因候補

- カンマ抜け。
- コメントを書いた。
- 全角引用符を使った。
- 文字コードが壊れた。

### 解決手順

1. エラー行を見る。
2. JSON validator で確認する。
3. 直近編集を戻す。
4. テンプレートから作り直す。

### 予防策

- 手動編集後に保存前確認する。
- コメントは JSON ではなく README に書く。

## プロファイル not found

### 症状

グループから `profile_id` が見つからない。

### 原因候補

- `groups.json` と `coaching-profiles.json` の ID 不一致。
- プロファイルを削除した。
- 複数ファイルを別々に編集した。

### 解決手順

1. `groups.json` の `profile_id` を確認する。
2. 同じ ID が `coaching-profiles.json` にあるか確認する。
3. Workflow F で紐付けを作り直す。

### 予防策

- プロファイル変更は Workflow F 経由にする。

## 選手が group_ids から見つからない

### 症状

参加者確認で選手が表示されない。

### 原因候補

- `athletes.json` の `group_ids` が空。
- グループ ID の typo。
- 選手を別グループに移した。

### 解決手順

1. 選手の `group_ids` を確認する。
2. `groups.json` と ID を一致させる。
3. 当日追加として一時参加させる。

### 予防策

- グループ変更時は選手側も更新する。

## PDF 生成できない

### 症状

TSV はできたが PDF 出力で止まる。

### 原因候補

- `reportlab` 未インストール。
- 出力パスに権限がない。
- 日本語フォント設定が未整備。

### 解決手順

1. `pip install reportlab` を実行する。
2. まず TSV 出力で内容を確認する。
3. PDF は後から再生成する。

### 予防策

- 初回は TSV を primary output にする。

## Excel テンプレートマッピング不整合

### 症状

Excel 出力でセル位置がずれる。

### 原因候補

- テンプレートが変更された。
- `sheet_name` が違う。
- `table_start_row` が古い。
- 結合セルの扱いが合わない。

### 解決手順

1. `data/excel-template-mapping.json` を確認する。
2. テンプレート変更後にマッピングを再作成する。
3. 小さいメニューで出力確認する。

### 予防策

- テンプレート更新時は version を付ける。

## 大量の menu-index.json で遅い

### 症状

過去メニュー検索や Workflow A の候補提示が遅い。

### 原因候補

- 索引が大きい。
- 古いタグが混ざっている。
- 条件が広すぎる。

### 解決手順

1. Phase / Zone / Method で絞る。
2. `python scripts\index\tag_zones_phases.py` を再実行する。
3. 古い parsed ファイルを整理する。

### 予防策

- Workflow B 後に索引化する。
- ファイルをむやみに複製しない。

## それでも解決しない場合

Issue には PII を含めないでください。
OS、Python バージョン、実行コマンド、期待した動作、実際の動作だけを書きます。
スクリーンショットに顔、名札、施設名が写っていないか確認してください。
