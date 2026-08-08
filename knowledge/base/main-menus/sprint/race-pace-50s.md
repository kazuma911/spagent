# Race-Pace 50s / レースペース50

公開配布用のメインセットパターンです。個人名・実在施設名・日付は含めません。Coach-agnostic template として利用します。

## Summary

| 項目 | 内容 |
|---|---|
| Applicable Phase | C〜D |
| Zone | SP2 |
| Target distance range | 600〜1200m main; session 2200〜3200m |
| Pattern name | 12 × 50m at 100m race pace |
| References | `../../references/zone-phase-mapping.md`, `../../references/phase-method-mapping.md`, `../../references/menu-design.md` |

## Set structure

| Block | Set | Intensity / Cycle | Target purpose |
|---|---|---|---|
| Prep | 6 × 50m 25 fast/25 easy | SP2 touch | 準備 |
| Main | 12 × 50m at 100m race pace, 1:30〜2:30 cycle | SP2 | race pace維持 |
| Reset | 100m easy after every 4 | EN1 | 品質維持 |
| Finish | 4 starts or breakouts optional | SP3 neural | 必要時 |

## Execution steps

1. Warm-up 後、今日の Zone と target pace を全員に共有します。
2. 1本目は速く入りすぎず、指定 Zone の範囲で確認します。
3. 中盤は stroke count、breathing rhythm、turn / breakout を観察します。
4. 後半にフォームが崩れる場合は距離・本数・cycle のいずれかを調整します。
5. Cool-down は EN1 で行い、次回に残すメモは PII を含まない形にします。

## Coach notes

- 休息を削ると別練習になります。
- time だけでなく stroke count も見ます。
- D期は本数を減らします。

## Variants

- **Short-course**: turn込み。
- **Long-course**: turnなし速度確認。
- **Junior-friendly**: 8 × 50m full rest。

## Scaling guide

| Group | Adjustment |
|---|---|
| masters group A | 休息を多めにし、quality を保ってから volume を増やす。 |
| junior group B | 距離を短くし、cue を1つに絞る。 |
| elite group | target intensity を維持し、崩れない範囲で volume を追加。 |
| triathlon group | Free 中心にしてもよいが、open-water skill は別ブロックで扱う。 |
| mixed/any | Lane ごとに cycle を分け、目的 Zone は揃える。 |

## When to avoid

- 体調不良者が多く、指定 Zone を安全に保てない日。
- Pool traffic が多く、send-off や race pace が危険な日。
- Recovery 目的の日に、隠れた高強度になりそうな場合。

## Data-free coaching record example

| Field | Example without PII |
|---|---|
| group | masters group A |
| course | local pool SCM |
| result | Most lanes held target pace through final round. |
| next adjustment | Add 5s rest or reduce one repeat if technique drops. |

## Quality checklist

- Target Zone と実際の RPE が合っている。
- Main set の目的が warm-up / drill / cool-down とつながっている。
- 個人名、施設名、医療・体調詳細などの PII を記録しない。

## Pace setting examples

| Situation | Adjustment |
|---|---|
| Lane holds target easily | Keep pace, reduce rest by 5s only if technique stays stable. |
| Lane misses target early | Add 5〜10s rest or reduce repeat distance. |
| Stroke count rises sharply | Hold intensity, insert 50m easy technique reset. |
| RPE is lower than expected | Confirm target pace before increasing speed. |
| RPE is higher than expected | Treat as fatigue signal; protect the next session. |

## Coach observation prompts

- Is breathing rhythm stable through the middle of the set?
- Does kick timing support body line rather than create drag?
- Are turns and breakouts consistent with the purpose of the Zone?
- Does the group understand whether today is aerobic, threshold, VO2max, sprint, recovery, or mixed?
- Are swimmers finishing with better awareness, not just more fatigue?

## Modification recipes

| Need | Modification |
|---|---|
| Lower total distance | Remove the final round before changing the warm-up. |
| Lower intensity | Keep structure but change target from EN3/SP1 to EN2. |
| More technique | Replace 25% of main distance with drill/swim by 25m. |
| More race specificity | Add 2〜4 breakouts or finishes with full rest. |
| Mixed ability lanes | Keep the same work:rest ratio and vary cycle by lane. |

## Privacy and publication guardrails

- Do not add swimmer names, real facility names, medical details, or private notes.
- Use placeholders such as `masters group A`, `junior group B`, or `local pool SCM`.
- If importing a real past menu, sanitize it before merging into public base knowledge.
