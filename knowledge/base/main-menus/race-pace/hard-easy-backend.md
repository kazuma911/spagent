# Hard-Easy Backend Correction / Hard-Easy 後半失速矯正

公開配布用のメインセットパターンです。個人名・実在施設名・日付は含めません。Coach-agnostic template として利用します。

## Summary

| 項目 | 内容 |
|---|---|
| Applicable Phase | B〜D (特に 100/200 種目の C-Trans / D-Real) |
| Zone | SP1〜SP2 (100 race pace) |
| Target distance range | 400〜800m main; session 2000〜3000m |
| Pattern name | Alternating easy 50 → hard 50 with backend at 100m race pace |
| References | `../../references/zone-phase-mapping.md`, `../../references/phase-method-mapping.md`, `../../references/menu-design.md` |

## Background

100/200m 種目で頻出する「前半速すぎて後半失速」を、練習で **逆転構造 (前半 easy / 後半 hard)** を反復することで矯正します。負荷は前半 easy で下げつつ、後半 hard を race pace で反復するため、race-specific なわりに総疲労は USRPT より軽いのが特徴。

## Set structure

| Block | Set | Intensity / Cycle | Target purpose |
|---|---|---|---|
| Prep | 4 × 50m descending 4→1 | EN2 → SP2 | 速度階段作り |
| Main | 8〜12 × 50m as (odd=easy loose / even=hard @100p) on 1:00〜1:15 cycle | Alt EN1 / SP2 | Backend hard 反復 |
| Alt (100 unit) | 4〜6 × 100m as 50 easy + 50 hard @100p, cycle 2:00〜2:30 | Alt EN1 / SP2 | Negative split 感覚 |
| Bridge | Between sets, 100m easy | EN1 | 回復 |
| Finish | 200m easy | EN1 | 品質維持 |

## Execution steps

1. Warm-up 後、各選手の 100m race pace / 2 = hard-50 target を確認します。
2. Easy 50 は「pace ではなく感覚」で loose、fatigue を残さないこと。
3. Hard 50 は最初から race pace target を要求。ここで守れないと逆順練習になりません。
4. Odd (easy) → even (hard) の交互は「後半を hard で終わる」感覚を作るのが目的です。
5. Cool-down は EN1 で行います。

## Coach notes

- Easy を「本当に easy に」できるかがコアです。中途半端な easy だと hard が落ちます。
- Hard-50 の target 秒数は race best (dive 100 / 2) より 0.5〜1.0s 保守側で始め、達成できたら詰めます。
- Backend fade の可視化は「hard-50 の 1 本目 vs 最終本の差」で見ます。差が 1s 以内なら成功。

## Variants

- **Short-course**: 50 unit @ 1:00 が標準。turn breakout を hard の 15m breakout として利用。
- **Long-course**: 50 unit @ 1:10〜1:15 に緩めます。turn なしで stroke length が試されます。
- **Junior-friendly**: 25 unit (odd easy / even hard) で 30〜40s cycle、感覚定着優先。

## Scaling guide

| Group | Adjustment |
|---|---|
| masters group A | Hard-50 target を race best から 0.5s 保守、本数 8〜10 で始める。 |
| junior group B | 25 unit のみ、cycle を長めに、hard の感覚定着を最優先。 |
| elite group | Hard-50 target 厳守、本数 12 まで、cycle を短めに。 |
| triathlon group | Freestyle 中心、200p target で 100 backend の代替も可。 |
| mixed/any | Lane 別に hard target を分け、cycle は共通で運用。 |

## When to avoid

- Recovery セッション日 (hard 50 が高強度で recovery にならない)。
- Warm-up / kick 系のみの日 (骨格が合わない)。
- Backend が既に強い選手 (frontend 修正の別パターンが必要)。

## Data-free coaching record example

| Field | Example without PII |
|---|---|
| group | masters group A |
| course | local pool SCM |
| result | Lane 1 hard-50 held 30.5±0.4s all 10 reps. Lane 2 backend improved from 32.5 to 31.8 across the set. |
| next adjustment | Lane 1 target を 30.0 に。Lane 2 は現状維持でもう 1 週。 |

## Quality checklist

- Easy と Hard の pace 差が明確 (easy は本当に easy か)。
- Hard-50 target が race best から論理的に導かれている。
- Backend fade が set 中盤・終盤で悪化していない。
- 個人名、施設名、医療・体調詳細などの PII を記録しない。

## Pace setting examples

| Situation | Adjustment |
|---|---|
| Hard-50 が最初 hit → 中盤崩れる | 本数を 2 本減らすか、easy を 5s 長めに。 |
| Hard-50 が全本届かない | Target を 0.5s 緩める。cycle を 5s 延ばす。 |
| Easy が easy になっていない | Cue を「呼吸を戻す」に統一、実測 pace を計らない。 |
| Backend が frontend より速い (逆転成功) | Target を 0.3s 上げるか、race pace の見直し。 |
| Stroke count が hard で増加 | Hard の pace を守るために stroke length を優先、fail 判定。 |

## Coach observation prompts

- Hard-50 の入りで「余裕がある」と感じたか？ (余裕があれば target 上げ余地)
- Easy 50 の終わりで呼吸が整っているか？
- Hard の後半 25m で失速していないか (半 50 内でも fade は起きる)？
- 選手が「後半 hard」の意識を持てているか (前半で使い切っていないか)？

## Modification recipes

| Need | Modification |
|---|---|
| Lower total distance | 本数を 2 本削減。または easy を skip して hard のみ (別パターンに変化)。 |
| Lower intensity | Hard の target を race pace ではなく EN3 相当に。 |
| More technique | Easy を drill-swim (breathing / stroke length focus) に。 |
| More race specificity | Hard を 100m 全体にして、pattern を easy 100 → hard 100 に拡張。 |
| Mixed ability lanes | Hard target を lane 別、easy の cue を共通に。 |

## Privacy and publication guardrails

- Do not add swimmer names, real facility names, medical details, or private notes.
- Use placeholders such as `masters group A`, `junior group B`, or `local pool SCM`.
- If importing a real past menu, sanitize it before merging into public base knowledge.
