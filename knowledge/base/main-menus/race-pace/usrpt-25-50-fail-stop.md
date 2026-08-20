# USRPT 25/50 with Fail-Stop / USRPT 25・50 (フェイルストップ付)

公開配布用のメインセットパターンです。個人名・実在施設名・日付は含めません。Coach-agnostic template として利用します。

## Summary

| 項目 | 内容 |
|---|---|
| Applicable Phase | B〜D (特に C-Trans / D-Real) |
| Zone | SP2 (race pace) |
| Target distance range | 400〜800m main; session 2000〜3200m |
| Pattern name | Ultra-Short Race-Pace Training (USRPT), 25m or 50m unit at target race pace with 2-consecutive-fail stop rule |
| References | `../../references/zone-phase-mapping.md`, `../../references/phase-method-mapping.md`, `../../references/menu-design.md` |

## Background

Rich Hood 由来の Race-Pace Transfer プロトコル。フル距離を「短い単位 × 多数の反復 × 短休息」に分割し、レース速度そのものを反復させることで神経系・技術・pacing を race-specific に転写します。**Fail-stop rule (連続 2 本 target 超過で終了)** で無理な volume を防ぎ、質を保ちます。

## Set structure

| Block | Set | Intensity / Cycle | Target purpose |
|---|---|---|---|
| Prep | 4 × 50m build to race pace, 1:30 | EN2 → SP2 | 速度感覚を作る |
| Main (200 target) | 10〜16 × 50m at 200m race pace, cycle 1:00〜1:15 | SP2 | 200m 速度転写 |
| Main (100 target, alt) | 12〜20 × 25m at 100m race pace, cycle 30〜40s | SP2 | 100m 速度転写 |
| Fail rule | 連続 2 本 target 秒数を超えたらそのセットは終了 | — | 質担保 |
| Bridge | Failure 後は 50〜100m easy を挿入して次の main へ | EN1 | 回復 |
| Finish | 100〜200m easy | EN1 | 品質維持 |

## Execution steps

1. Warm-up 後、選手ごとの target time (200m race pace / 4 = 50 unit target、100m race pace / 4 = 25 unit target) を確認します。
2. 1 本目から target を要求します (USRPT は「入り easy → build」ではなく最初から race pace を要求)。
3. 連続 2 本を target + 1s 以上で超えたら fail-stop、そのセットを終了します。残り本数は easy 50m で置換します。
4. Fail した選手は次のセット (もう一巡) から再合流可能。
5. Cool-down は EN1 で行います。

## Coach notes

- USRPT は「本数を稼ぐ」ではなく「target 秒数をどれだけ維持できたか」で成功を測ります。
- Rest を削らないでください。short-rest だが「rest がある」ことが前提のプロトコルです。
- Target 秒数は current-paces.json の best race time から逆算しますが、疲労・年齢・レース水着差の 4 大現実補正を必ず入れます。

## Variants

- **Short-course**: 50 unit の cycle は 1:00 が標準。25 unit は 30s。
- **Long-course**: 50 unit の cycle を 1:10〜1:15 に緩めます (turn なしでスタミナ要求が上がる)。
- **Junior-friendly**: 25 unit のみ、cycle を 40〜50s に緩めます。fail 許容を「連続 3 本」に緩和します。

## Scaling guide

| Group | Adjustment |
|---|---|
| masters group A | Target を race best から 0.5〜1.0s 保守側に。fail-stop を厳格に。 |
| junior group B | 25 unit のみ、cycle 40〜50s、fail 連続 3 本許容。 |
| elite group | 50 unit フルで target 厳守、fail-stop は 1 本オーバーでも警告。 |
| triathlon group | Free 中心、200p target 主体で 100p は補助 (400/1500 race に近い)。 |
| mixed/any | Lane 別に cycle を分け、target を lane 内で個別設定。 |

## When to avoid

- 選手の best race time が最近 4 週間内に測定されていない (target が推定になり過ぎる)。
- 大会 D-3 以内 (体力消耗が本番に響く)。
- 準備期 A の初週 (有酸素土台不足で fail 連発)。

## Data-free coaching record example

| Field | Example without PII |
|---|---|
| group | masters group A |
| course | local pool SCM |
| result | Lane 1 held 10/10 at target, lane 2 fail-stopped at rep 7. |
| next adjustment | Lane 2 target を 0.5s 緩めて次回再挑戦。 |

## Quality checklist

- Target 秒数が各選手に共有されている。
- Fail-stop が実行されたか (甘やかしていないか)。
- Rest 秒数が守られている (short-rest だが省略されていない)。
- 個人名、施設名、医療・体調詳細などの PII を記録しない。

## Pace setting examples

| Situation | Adjustment |
|---|---|
| Lane holds target easily | Target を 0.3〜0.5s 上げるか、cycle を 5s 短くする。 |
| Lane fail-stops at rep 3-4 | Target を 1s 緩めるか、cycle を 5s 延ばす。 |
| Stroke count rises sharply | 途中で 100m easy 挟んで技術リセット、fail 待たずに介入。 |
| RPE 低い | Target 未達なのに苦しくないなら target 上げ余地あり。 |
| RPE 高いのに target 未達 | 疲労シグナル、次回セッションを保護。 |

## Coach observation prompts

- Breathing rhythm が set 中盤で崩れていないか？
- Kick timing が body line を支えているか、抵抗を生んでいるか？
- Turns と breakouts が race pace 相当か？
- 選手が「target 秒数」を意識できているか (「速く泳ぐ」ではなく)？
- Fail-stop 後の easy 置換を選手が受け入れているか？

## Modification recipes

| Need | Modification |
|---|---|
| Lower total distance | Main セット数を減らす前に prep 距離を削減。 |
| Lower intensity | 25 unit → 50 unit に切替、cycle を延ばす。 |
| More technique | Fail 後の easy を drill-swim にする。 |
| More race specificity | 200 target と 100 target を同日 2 セット構成にする。 |
| Mixed ability lanes | Target を lane 別に、cycle を lane 別に。fail-stop は個別判定。 |

## Privacy and publication guardrails

- Do not add swimmer names, real facility names, medical details, or private notes.
- Use placeholders such as `masters group A`, `junior group B`, or `local pool SCM`.
- If importing a real past menu, sanitize it before merging into public base knowledge.
