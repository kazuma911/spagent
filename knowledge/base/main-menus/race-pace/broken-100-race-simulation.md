# Broken 100/200 Race Simulation / ブロークン 100・200 レース シミュレーション

公開配布用のメインセットパターンです。個人名・実在施設名・日付は含めません。Coach-agnostic template として利用します。

## Summary

| 項目 | 内容 |
|---|---|
| Applicable Phase | C-Trans〜D-Real (レース想定期) |
| Zone | SP1〜SP2 (race pace) |
| Target distance range | 600〜1200m main; session 2200〜3400m |
| Pattern name | Race distance broken into short reps with brief rest, simulating race split targets |
| References | `../../references/zone-phase-mapping.md`, `../../references/phase-method-mapping.md`, `../../references/menu-design.md` |

## Background

Race distance (100 / 200) を短い分割 (25 or 50) と短休息 (10s) で再構築し、race pace 相当の速度を「分割された形で」達成するプロトコル。USRPT より休息時間が長く「1 本の 100/200 として意識できる」点が特徴で、race のペース感覚と breakout / turn 技術を統合しやすい。

## Set structure

| Block | Set | Intensity / Cycle | Target purpose |
|---|---|---|---|
| Prep | 4 × 50m descending + 2 × 25m from dive | EN2 → SP2 | Neural priming |
| Main (100 broken) | 4〜6 × [4 × 25m at 100 race pace, 10s rest] on 3:00〜4:00 recovery | SP2 | 100 分割再構築 |
| Main (200 broken, alt) | 3〜4 × [4 × 50m at 200 race pace, 10s rest] on 4:00〜5:00 recovery | SP2 | 200 分割再構築 |
| Record | 各 25/50 の split と合計を記録 | Race analysis | 配分検証 |
| Finish | 200m easy | EN1 | 品質維持 |

## Execution steps

1. Warm-up 後、race pace target (100 race best time / 4 = 25 split target、200 race best time / 4 = 50 split target) を確認します。
2. 各 25 (or 50) を race split target で実行、間 10s rest。合計時間 (rest 込み) が race best time より 10〜20s 短い程度に収まるのが目安。
3. 4 本 (or 5 本) 終わったら long recovery (3〜5 分)、その間に split time を記録。
4. 次のセットで前セットの結果を反映 (前半速すぎたら後半 target を守る、等)。
5. Cool-down は EN1 で行います。

## Coach notes

- Broken は「rest がある分楽」ではなく「race pace を分割で試す」プロトコルです。**Rest 中は歩かず、水中で軽く動きます**。
- Split ごとの target を race pace で厳守。合計時間が race best time より遅い場合は target が甘い、10s 以上速い場合は target がタイトすぎる。
- Turn / breakout は race 相当。25 の折り返しでは特に breakout 距離を計測します。

## Variants

- **Short-course**: 100 broken = 4 × 25, 200 broken = 4 × 50 が標準。turn は race 相当。
- **Long-course**: 100 broken = 2 × 50 with 5s rest、200 broken = 4 × 50 with 10s rest。turn なしで stroke length 要求。
- **Junior-friendly**: 100 broken を 2 × 50 with 15s rest、200 broken は使わず 100 のみ。

## Scaling guide

| Group | Adjustment |
|---|---|
| masters group A | Target split を race best から 0.5〜1.0s 保守側に。4 セットで開始。 |
| junior group B | 100 broken (2 × 50) のみ、rest 15s、セット数を 3 に。 |
| elite group | Target split 厳守、6 セットまで。Recovery を 3 分に短縮も可。 |
| triathlon group | Freestyle 中心、200 broken を主に。1500 race 対応は別プロトコル。 |
| mixed/any | Target split を lane 別に、Recovery を共通で。 |

## When to avoid

- 大会 D-2 以内 (体力消耗が本番に響く)。
- 選手の race best time が最近 8 週間内に測定されていない。
- 準備期 A / B の serial acidosis 未対応期。

## Data-free coaching record example

| Field | Example without PII |
|---|---|
| group | masters group A |
| course | local pool SCM |
| result | Lane 1 100 broken合計 held race best -8s across 5 sets. Lane 2 200 broken 3 sets held -15s (target range). |
| next adjustment | Lane 1 target split を 0.3s 上げて次回。Lane 2 は現状維持。 |

## Quality checklist

- Target split が race best から論理的に導かれている。
- Rest 10s が守られている (延ばしていないか)。
- 合計時間が race best time より短い範囲に収まっている。
- Turn / breakout が race 相当。
- 個人名、施設名、医療・体調詳細などの PII を記録しない。

## Pace setting examples

| Situation | Adjustment |
|---|---|
| 合計時間が race best より 20s 以上速い | Target split がタイトすぎる、0.3〜0.5s 緩める。 |
| 合計時間が race best より遅い | Target split が甘い、要見直し。または疲労シグナル。 |
| 前半 split 速い / 後半崩れる | Even split cue を強調、前半の pace 抑制を要求。 |
| Turn 後 breakout が短い | Breakout drill を別途、broken では breakout 距離を意識可視化。 |
| Stroke count が set 中盤で崩れる | Set 数を減らし、split target を守れる範囲まで。 |

## Coach observation prompts

- Rest 10s 中、選手は水中で軽く動いているか (歩いていないか)？
- Split ごとの target を口に出せているか？
- Turn の入り速度が race 相当か？
- 合計時間の目安を選手が理解しているか？
- 次セットで前セットの反省を反映できているか？

## Modification recipes

| Need | Modification |
|---|---|
| Lower total distance | セット数を 1 減らす前に prep 距離を削減。 |
| Lower intensity | 100 broken を SP1 (400 pace) target に切替。 |
| More technique | Prep セットで dive start / breakout を強化。 |
| More race specificity | Broken の最終セットを完全連続 (rest なし race 相当) にする。 |
| Mixed ability lanes | Target split と Recovery 時間を lane 別に個別化。 |

## Privacy and publication guardrails

- Do not add swimmer names, real facility names, medical details, or private notes.
- Use placeholders such as `masters group A`, `junior group B`, or `local pool SCM`.
- If importing a real past menu, sanitize it before merging into public base knowledge.
