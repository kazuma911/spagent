# FAQ

spagent のよくある質問です。
コーチ向けの運用質問と、エンジニア向けの設定質問を一緒にまとめます。
詳細は [workflows.md](workflows.md)、[customization.md](customization.md)、[security.md](security.md) を参照してください。

## Q1. Skill と Agent の違いは?

Skill は Copilot に読ませる手順書・知識パッケージです。Agent はその場で対話し、ファイルを読んだり保存したりする実行役です。spagent では `SKILL.md` が Skill の入口で、Copilot が Agent として Workflow A-G を進めます。

### 運用ポイント

- Skill はルール、Agent は実行者と考える。
- 迷ったら `../SKILL.md` の Workflow を確認する。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q2. `use_base_knowledge = custom_only` はどんな時使う?

公式 base を混ぜず、自分の過去メニューやドリルだけで組みたい時に使います。独自スタイルが強いコーチ向けですが、custom が少ない初期状態では提案が薄くなります。

### 運用ポイント

- Workflow G で過去メニューを取り込んでから使うと効果的。
- 初回は `all`、慣れたら `custom_only` でもよい。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q3. Method はなぜプロファイルに含めない?

同じグループでも当日の Phase、人数、体調、時間で適切な Method が変わるためです。プロファイルは対象と長期の型、Method は当日の戦術として分けています。

### 運用ポイント

- preferred/avoided は参考として持てる。
- 最終 Method は Workflow A Step 10 で決める。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q4. 交代制になったときの群分けは自動?

Skill は人数、レーン数、泳力差から群分けを提案できます。ただし安全面、人間関係、当日の混雑は現場判断が必要なので、最終決定はコーチです。

### 運用ポイント

- 待機側の過ごし方も必ず決める。
- 完全待機、ストレッチ、軽ドリル、陸トレ、軽セットから選ぶ。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q5. 過去メニューが Excel でセル構造がバラバラだけど取り込める?

完全自動で読めない場合があります。Workflow G はまず構造化プレビューを出し、コーチが誤認識を直してから保存します。

### 運用ポイント

- 似た形式ごとに分けて取り込む。
- テンプレートがあるなら `excel-template-mapping.json` を作る。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q6. 選手が急に休んだ時のメニュー調整は?

Workflow A の参加者確認で欠席を反映します。人数が減ると交代制が不要になったり、Cycle を締めたりできます。

### 運用ポイント

- 練習後は Workflow B で欠席履歴を残す。
- 欠席理由に PII を含めない。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q7. 怪我をした選手の Fly 回避はどう反映される?

`data/athlete-conditions.json` に練習上の制約として保存します。Workflow A は Drill、種目、設定タイム補正で参照します。

### 運用ポイント

- 医療判断はしない。必要なら専門家相談。
- 例: `avoid_fly`, `reduce_kick_volume` のように練習制約で書く。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q8. 集団の中で個別ペースをどう扱う?

基本メニューは共有し、設定タイムや Cycle を選手別または小グループ別に出します。泳力差が大きい場合は lane group や A/B 群に分けます。

### 運用ポイント

- PB と直近 RPE の両方を見る。
- 同じ距離でも目標タイムを変える。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q9. 骨格パターンを途中で変えたい

Workflow F でプロファイルの `menu_structure_pattern_id` を変えます。手動編集する場合は `menu-structure-patterns.json` の距離比率と総距離帯を確認します。

### 運用ポイント

- いきなり全グループに適用しない。
- 1 回のメニューで試してから採用する。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q10. Custom Method の命名ルールは?

ファイル名は英数字小文字とハイフンを推奨します。表示名は日本語でも構いませんが、個人名、施設名、実在大会名は入れないでください。

### 運用ポイント

- 例: `threshold-200-blocks.md`。
- 目的がわかる名前にする。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q11. 複数プロファイルを切り替えられる?

できます。Workflow A Step 3 で今日使うグループを選び、その `profile_id` からプロファイルを読みます。

### 運用ポイント

- マスターズとジュニアは別プロファイルにする。
- 個別指導は 1 人グループで扱える。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q12. 予定と違う時間になった時は?

Workflow A Step 2 で練習時間を上書きします。短縮時は W-up、Main、C-down の優先順位を見て再配分します。

### 運用ポイント

- C-down は安全上なるべく残す。
- Main の本数や距離を先に調整する。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q13. Docker 対応は?

v0.6.0 の要件では Docker は必須ではありません。Python 3.10+ と Pillow が基本です。

### 運用ポイント

- 将来の再現性向上として追加余地はある。
- 現時点はローカル Python 前提。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q14. 商用利用したい

README の通り、明示的なライセンスファイルはなく、商用利用・再配布は要相談です。

### 運用ポイント

- 利用前にリポジトリオーナーへ確認する。
- 顧客データや選手データを共有しない。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q15. 他コーチと共有したい

PII を除外した base 追加や匿名化サンプルなら共有しやすいです。`data/`, `sessions/`, `plans/`, `knowledge/custom/` をそのまま渡さないでください。

### 運用ポイント

- 共有用に別サンプルを作る。
- エイリアスも特定されにくいものにする。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q16. ペース推定が実測と合わない時は?

`current-paces.json` と直近 `times.tsv` を見直します。PB が古い、RPE が高い、LCM/SCM 差、体調制約が原因になりがちです。

### 運用ポイント

- Workflow B で実測を蓄積する。
- 数回続けてずれるなら基準ペースを更新する。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q17. 出力 PDF の見た目を変えたい

PDF 出力は `reportlab` を使う想定です。レイアウト変更は export スクリプトやテンプレート設計の変更になります。

### 運用ポイント

- まず TSV の列を固める。
- 見た目だけでなく現場で読みやすい余白を重視する。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q18. `athlete-insights.json` を修正したい

できます。AI 推論はコーチ承認済みだけ残す方針です。誤った傾向は削除するか、承認状態を外す運用にしてください。

### 運用ポイント

- 推論の根拠 session を確認する。
- 一回だけの結果で決めつけない。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q19. 画像から時間認識できない時は?

手書きが薄い、斜め、光反射、単位が不明などが原因です。Workflow B のプレビューで手動修正します。

### 運用ポイント

- 次回から表形式で書く。
- 顔や名札が写らない角度で撮る。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q20. Zone tag が想定と違う

`references/zone-phase-mapping.md` と `scripts/index/tag_zones_phases.py` のキーワードが合っているか確認します。独自表現が多い場合は custom 側に補助説明を足します。

### 運用ポイント

- メニュー内に主 Zone を明示する。
- 索引再構築を実行する。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q21. Base knowledge を編集してよい?

直接編集は推奨しません。公式配布との差分が追いにくくなるため、`knowledge/custom/overrides/` で上書きしてください。

### 運用ポイント

- base は標準教科書として扱う。
- 自分流は custom に置く。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q22. ジュニアに高強度メニューを出す?

出す場合も量と頻度を抑え、技術優先にします。痛みや疲労がある場合は避けます。spagent は過度なボリュームや高強度を推奨しない方針です。

### 運用ポイント

- 早期専門化を避ける。
- 4 泳法と楽しさを残す。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q23. 大会がない時期はどうする?

Maintenance Phase として扱います。健康維持、技術改善、有酸素基礎、楽しさを中心にします。

### 運用ポイント

- 強度を上げる理由がない時は上げない。
- 継続できる負荷を優先する。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q24. カスタム Excel のセル対応がずれる

`data/excel-template-mapping.json` の `sheet_name`, `cells`, `table_start_row` を確認します。テンプレートを変更したらマッピングも更新します。

### 運用ポイント

- テンプレートに version を付ける。
- 小さいメニューで試す。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q25. 取り込み素材に施設名が入っていた

Workflow G の PII チェックでマスクまたは削除します。公開サンプルに使う場合は `main-pool` などに置き換えてください。

### 運用ポイント

- ファイル名も確認する。
- PDF のヘッダーやフッターも見る。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q26. メニューを保存した後に修正したい

既存 `sessions/YYYY-MM-DD/menu.tsv` を上書きする場合は差分提示と承認が必要です。実施時の変更は `feedback.md` に残します。

### 運用ポイント

- 予定変更と実施差分を混ぜない。
- 上書き前にバックアップを確認する。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)

## Q27. どの順番でドキュメントを読めばよい?

まず [getting-started.md](getting-started.md)、次に [workflows.md](workflows.md)、必要に応じて [customization.md](customization.md)、[training-models.md](training-models.md)、[security.md](security.md) へ進んでください。

### 運用ポイント

- 困った時は [troubleshooting.md](troubleshooting.md)。
- 貢献時は [contributing.md](contributing.md)。

### 関連

- [../SKILL.md](../SKILL.md)
- [workflows.md](workflows.md)
