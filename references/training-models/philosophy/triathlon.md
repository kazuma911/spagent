# Triathlon（水泳統合）

## 対象特性

Bike/Run と両立し、効率的なスイム、オープンウォーター対応、疲労を残さない持久力を作ります。

## 週の頻度

週 2-3 回。全競技の疲労総量で判断。

## 優先順位

有酸素持久力 >> 技術 > Bike への疲労波及回避 >> レーススピード

## 避けるべき

脚を潰す Kick 大量、肩に過負荷な Paddle、翌日の Bike/Run を壊す SP3。

## 典型週次パターン

| Day | Theme | Notes |
|---|---|---|
| Mon | Technique / Easy | 前回疲労を確認 |
| Tue | Aerobic or Threshold | 主刺激は 1 つ |
| Wed | Off or Mobility | 回復を優先 |
| Thu | Skill + Pace | 短い質の刺激 |
| Fri | Easy | 状態により休養 |
| Sat | Main session | 週の中心練習 |
| Sun | Recovery / Off | 次週へつなぐ |

## 大会目標例

OW 完泳、スイム後半の余裕、T1 への疲労軽減、ミドル/ロング完走。

## Phase 別方針

| Phase | 方針 | Method |
|---|---|---|
| A | 基礎と技術 | LSD / Fartlek / Drill |
| B | Threshold と専門化 | Threshold / Descending |
| C | Race Pace | Broken / HIIT |
| D | 量を落として速度維持 | USRPT / Broken short |
| REC | 回復 | Easy / Fartlek light |

## 実務ポイント

- Warm-up / Cool-down を必ず入れる。
- [Zone × Phase](../../zone-phase-mapping.md) と [Phase × Method](../../phase-method-mapping.md) を照合する。
- `athlete-conditions.json` の制約を最優先する。
- ペースは [pace-estimation.md](../../pace-estimation.md) で RPE と直近タイムから補正する。

## spagent での指定

```json
{ "philosophy": "triathlon" }
```

## 観察ポイント

| 項目 | 見ること | 記録先 |
|---|---|---|
| 技術 | キャッチ、姿勢、呼吸、ターン | `athlete-skill-notes.json` |
| 体調 | 睡眠、疲労、痛み、欠席 | `athlete-conditions.json` |
| ペース | target 達成、後半落ち | `times.tsv` |
| RPE | セット別・全体 | `times.tsv` |
| 学習 | 次回に活かす傾向 | `athlete-insights.json` |

## 強度配分の考え方

| Phase | 推奨 | 避けること |
|---|---|---|
| A | EN1/EN2 と技術 | 早すぎる専門化 |
| B | EN3 と専門 Drill | 毎回 all-out |
| C | Race Pace と回復の両立 | 量を増やし続ける |
| D | 短く速く、疲労を抜く | 新しい技術課題 |
| REC | EN1、可動域、楽しさ | 記録狙い |

## Drill 優先順位

1. 安全に泳げる姿勢。
2. キャッチと水感。
3. 呼吸と回旋。
4. キックと体幹連動。
5. ターン、スタート、レース細部。

## 声かけテンプレート

- 今日の目的は `主 Zone` と `技術キュー` の 2 つだけです。
- 速さより先に、狙った動作を守ります。
- 痛みが出たら止めます。止めることも練習判断です。
- 失敗は次の設定を良くする材料です。

## メニュー例の読み替え

| 状況 | 読み替え |
|---|---|
| 人数が多い | 距離を短くし、出発間隔を広げる |
| レーンが少ない | 交代制と待機側 Drill を使う |
| 疲労が高い | Zone を 1 段階下げる |
| 技術が崩れる | Main を止めて Drill に戻す |
| 大会直前 | 量を下げ、速度感だけ残す |

## 代表的な週のバリエーション

| Pattern | Mon | Wed | Fri | Sat |
|---|---|---|---|---|
| 低頻度 | Technique | Threshold | Off | Race Pace short |
| 標準 | EN2 | Drill+Kick | EN3 | Broken |
| 高頻度 | EN2 | SP1 | REC | EN3 |
| 回復週 | Easy | Drill | Easy | Fartlek light |

## フィードバック観点

- 今日の目的に対して成功したか。
- タイムよりフォーム維持を優先すべき場面はあったか。
- 次回の Zone を上げるか、維持するか、下げるか。
- 怪我や疲労の制約を更新する必要があるか。
- コーチの Custom pattern に反映すべき発見はあるか。

## 安全境界

以下の場合は高強度を避けます。

- 痛みが増える。
- 睡眠不足が強い。
- RPE 9-10 が続く。
- 呼吸が戻らない。
- 技術が明らかに崩れる。

## 出力サマリ例

```text
Philosophy: selected profile
Main priority: technique + aerobic base
Adjustment: athlete-001 shoulder restriction, no paddles
Next review: after 2 sessions
```

## 最終確認チェックリスト

- [ ] 今日の主目的を 1 文で説明できる。
- [ ] Phase と Zone の根拠が明記されている。
- [ ] Method の停止条件がある。
- [ ] Warm-up と Cool-down が残っている。
- [ ] 怪我・疲労制約を反映した。
- [ ] Junior は 4 泳法バランスを崩していない。
- [ ] Masters は回復時間を確保した。
- [ ] Triathlon は Bike/Run 疲労を確認した。
- [ ] Elite は測定指標と主観を併用した。
- [ ] 変更があれば `feedback.md` に残す。

## 参照リンク

- [Zone × Phase](../../zone-phase-mapping.md)
- [Phase × Method](../../phase-method-mapping.md)
- [Pace Estimation](../../pace-estimation.md)
- [Menu Rules](../../menu-rules.md)
- [Feedback Process](../../feedback-process.md)

