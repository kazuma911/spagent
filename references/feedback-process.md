# フィードバック処理プロセス

この文書は Workflow B（記録・フィードバック）の詳細手順です。実測タイム、RPE（主観的運動強度 1-10）、メニュー変更、体調、技術観察を整理し、次回メニューと索引に反映します。

## 1. 目的

- 実施結果を `times.tsv` と `feedback.md` に残す。
- `athlete-conditions.json` と `athlete-skill-notes.json` を更新する。
- 実施メニューを `knowledge/custom/menu-index.json` に追加する。
- AI が推論した傾向を、コーチ承認後に `athlete-insights.json` へ保存する。

## 2. Workflow B 全体

| Step | 内容 | 保存先 |
|---|---|---|
| 1 | 撮影メモ画像取得 | `sessions/YYYY-MM-DD/raw/` |
| 2 | 画像 PII 検知 | マスク済み画像 |
| 3 | タイム・RPE 抽出 | プレビュー |
| 4 | サマリー全件表示 | 未保存 |
| 5 | 修正反復 | 未保存 |
| 6 | `times.tsv` 保存 | `sessions/YYYY-MM-DD/times.tsv` |
| 7 | メニュー変更履歴 | `feedback.md` |
| 8 | 体調・怪我・欠席 | `athlete-conditions.json` |
| 9 | 技術課題観察 | `athlete-skill-notes.json` |
| 10 | 実施ベース索引化 | `knowledge/custom/menu-index.json` |
| 11 | 現在ペース更新提案 | `current-paces.json` |
| 12 | AI 適応学習 | `athlete-insights.json` |

## 3. feedback.md の 7-item template

```markdown
# YYYY-MM-DD Feedback

## 1. Overview

## 2. 選手別ハイライト

## 3. メニュー変更履歴

## 4. 次回への申し送り

## 5. 体調・怪我更新

## 6. 技術課題観察

## 7. 次回ペース設定案
```

## 4. 1. Overview

含めるもの:

- 実施日、コース、時間。
- Phase / 主 Zone / Method。
- 予定総距離と実施総距離。
- 全体 RPE の傾向。
- 安全上の特記事項。

例:

```markdown
Phase B / EN3 Threshold day。予定 4,200m、実施 4,000m。
後半の 100m repeat は target から平均 +1.5 秒。
athlete-003 は肩の違和感により Pull を中止し Easy に置換。
```

## 5. 2. 選手別ハイライト

| athlete_id | 良かった点 | 課題 | RPE |
|---|---|---|---:|
| athlete-001 | EN3 target を安定 | 75m 以降で呼吸が上がる | 7 |
| athlete-002 | Drill の姿勢改善 | ターン後 5m が弱い | 6 |

書き方:

- 評価は事実ベース。
- 人格評価を書かない。
- 次回につながる観察にする。

## 6. 3. メニュー変更履歴

`menu.tsv` と実施内容の差分を書きます。

| planned | actual | reason |
|---|---|---|
| 8×100 EN3 | 6×100 EN3 | 全体 RPE 高く、フォーム崩れ |
| 4×25 Fly sprint | 4×25 Free fast | 肩痛者対応 |

予定だけを索引化すると実際の負荷がずれるため、変更履歴は重要です。

## 7. 4. 次回への申し送り

次回コーチが最初に見るべき情報を短く書きます。

- EN3 は維持できたが、SP2 に上げる前に easy day を挟む。
- athlete-001 は 100m target を 1:05 から 1:06 に調整。
- Junior group は Back drill を継続。

## 8. 5. 体調・怪我更新

| athlete_id | condition | action |
|---|---|---|
| athlete-003 | right shoulder discomfort | Fly/Paddle 回避、医療相談を案内 |
| athlete-004 | fatigue high | next session EN1/EN2 |

注意:

- 医療診断はしない。
- 痛みが続く場合は医療従事者へ相談を案内する。
- 痛みを我慢して継続する前提にしない。

## 9. 6. 技術課題観察

`athlete-skill-notes.json` の `focus_areas` 更新に使います。

| athlete_id | observation | next drill |
|---|---|---|
| athlete-001 | catch が外に逃げる | Front scull, Doggy paddle |
| athlete-002 | turn 後の streamline が緩い | Streamline kick, push-off check |

良い技術も記録します。改善傾向が見えると、AI insight の精度が上がります。

## 10. 7. 次回ペース設定案

[pace-estimation.md](pace-estimation.md) に沿って提案します。

```markdown
athlete-001:
- 100m Free EN3 target: 1:05 -> 1:06
- 理由: RPE 8、後半 +2 秒、フォーム維持優先

athlete-002:
- 50m Free SP2 target: 32.0 維持
- 理由: RPE 7、target 達成、フォーム安定
```

## 11. AI insight learning step（Workflow B Step 12）

AI 選手適応学習は、過去 `times.tsv` + RPE + `feedback.md` を読み、選手ごとの傾向を推論します。ただし保存はコーチ承認後だけです。

### 11.1 推論してよいこと

- 高強度に強い / 弱い。
- 朝練で RPE が上がりやすい。
- Threshold は安定するが Sprint でフォームが崩れる。
- Kick set 後に Main のタイムが落ちる。
- Drill の効果が出やすいテーマ。

### 11.2 推論してはいけないこと

- 医学的診断。
- 性格や家庭状況などの個人属性。
- 実名、連絡先、学校・勤務先など PII。
- コーチが承認していない断定。

### 11.3 athlete-insights.json 例

```json
{
  "athlete_id": "athlete-001",
  "insights": [
    {
      "type": "pace_response",
      "summary": "EN3 repeat は 6 本目以降に +1.5 秒遅れやすい",
      "evidence_sessions": ["2026-08-01", "2026-08-08"],
      "coach_approved": true
    }
  ]
}
```

## 12. セッション終了時の menu index update

Workflow B の最後に、実施内容を索引へ反映します。

```text
python scripts/index/import_tsv_menus.py YYYY-MM-DD
python scripts/index/tag_zones_phases.py
```

処理内容:

1. `sessions/YYYY-MM-DD/menu.tsv` と実施差分を読み取る。
2. `knowledge/custom/menu-index.json` に追加する。
3. [zone-phase-mapping.md](zone-phase-mapping.md#3-keyword--zone-tagging-rules) のキーワードで `zone_tags` を付与する。
4. Phase を再判定する。
5. 次回 Workflow C / A の検索候補に反映する。

## 13. 品質チェック

- [ ] `times.tsv` に RPE 列がある。
- [ ] `feedback.md` は 7 項目すべてある。
- [ ] 変更履歴が予定との差分として読める。
- [ ] 怪我・体調更新が安全に書かれている。
- [ ] AI insight はコーチ承認済みだけ保存する。
- [ ] 実名・施設名・連絡先など PII がない。
