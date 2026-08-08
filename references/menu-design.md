# メニュー骨格設計

この文書は Workflow A Step 13 のメニュー骨格設計テンプレートです。Phase/Zone は [zone-phase-mapping.md](zone-phase-mapping.md)、Method は [phase-method-mapping.md](phase-method-mapping.md)、運用制約は [menu-rules.md](menu-rules.md) を参照します。

## 1. 骨格設計の目的

骨格は「どの順で、どの距離比率で、何を狙うか」を先に決めるためのテンプレートです。細かいセットを作る前に骨格をコーチへ提示し、承認後に本メニューへ展開します。

## 2. Default skeleton

| Block | Ratio | 目的 |
|---|---:|---|
| W-up | 20% | 体温、呼吸、関節、当日テーマへの導入 |
| Drill | 10% | 技術課題、Phase 別ルーティン |
| Kick | 10% | 姿勢、脚、種目特異性 |
| Main | 45% | 主 Zone / Method の中心刺激 |
| Cool-down | 15% | 回復、フォーム確認、終了 |

例: 4,000m の場合:

| Block | Distance |
|---|---:|
| W-up | 800m |
| Drill | 400m |
| Kick | 400m |
| Main | 1,800m |
| Cool-down | 600m |

## 3. Variant: aerobic day

| Block | Ratio | 内容 |
|---|---:|---|
| W-up | 18% | Easy + build |
| Drill | 8% | 姿勢・キャッチ |
| Pull/Kick | 14% | EN2 の支え |
| Main EN2/EN3 | 50% | 長めの反復 |
| Cool-down | 10% | Easy |

狙い:

- Phase A/B。
- LSD、Threshold、Descending。
- Masters / Triathlon に使いやすい。

## 4. Variant: speed day

| Block | Ratio | 内容 |
|---|---:|---|
| W-up | 25% | 十分な準備、activation |
| Drill | 10% | レース動作 |
| Pre-set | 15% | build, dive, turn |
| Main SP2/SP3 | 35% | 高品質・低本数 |
| Cool-down | 15% | 長めに回復 |

狙い:

- Phase C/D。
- USRPT、Broken、HIIT。
- 量を増やさず質を維持する。

## 5. Variant: recovery day

| Block | Ratio | 内容 |
|---|---:|---|
| W-up | 20% | Very easy |
| Mobility Drill | 20% | 技術、可動域 |
| Easy Swim/Kick | 35% | EN1/EN2 |
| Play/Fartlek | 10% | 軽い変化 |
| Cool-down | 15% | Relax |

狙い:

- REC。
- 高 RPE 後。
- Junior の楽しい技術日。

## 6. menu_structure_pattern_id による上書き

`data/coaching-profiles.json` の `menu_structure_pattern_id` が設定されている場合、`knowledge/custom/menu-structure-patterns.json` の骨格を優先します。

```json
{
  "id": "masters-short-threshold",
  "name": "Masters 75min Threshold",
  "total_distance_range": [2800, 3600],
  "blocks": [
    {"name": "W-up", "ratio": 0.20},
    {"name": "Drill", "ratio": 0.10},
    {"name": "Main", "ratio": 0.55},
    {"name": "C-down", "ratio": 0.15}
  ]
}
```

上書き時の原則:

- Warm-up / Cool-down は消さない。
- 怪我制約は Custom pattern より優先する。
- Phase/Zone の目的と矛盾する場合は警告する。
- コーチの Custom pattern は尊重するが、安全上限を超えない。

## 7. Example skeletons

### 7.1 default-balanced-4000

| Order | Block | Ratio | Distance | Notes |
|---|---|---:|---:|---|
| 1 | W-up | 20% | 800 | choice + build |
| 2 | Drill | 10% | 400 | phase routine |
| 3 | Kick | 10% | 400 | stroke balance |
| 4 | Main | 45% | 1800 | primary method |
| 5 | Cool-down | 15% | 600 | EN1 |

### 7.2 aerobic-threshold-4500

| Order | Block | Ratio | Distance | Notes |
|---|---|---:|---:|---|
| 1 | W-up | 18% | 800 | easy + drill |
| 2 | Pull/Kick | 16% | 700 | EN2 support |
| 3 | Pre-main | 10% | 450 | descend |
| 4 | Main | 46% | 2050 | EN3 Threshold |
| 5 | Cool-down | 10% | 500 | easy |

### 7.3 speed-quality-3200

| Order | Block | Ratio | Distance | Notes |
|---|---|---:|---:|---|
| 1 | W-up | 25% | 800 | longer preparation |
| 2 | Drill/Activation | 15% | 500 | dive/turn/build |
| 3 | Main Race Pace | 35% | 1100 | high rest, high quality |
| 4 | Recovery Swim | 10% | 300 | between rounds |
| 5 | Cool-down | 15% | 500 | EN1 |

### 7.4 junior-skill-im-3800

| Order | Block | Ratio | Distance | Notes |
|---|---|---:|---:|---|
| 1 | W-up IM | 18% | 700 | 4 strokes |
| 2 | Drill rotation | 18% | 700 | Fly/Bk/Br/Fr |
| 3 | Kick | 14% | 500 | safe volume |
| 4 | Main aerobic | 35% | 1300 | EN2, IM mix |
| 5 | Game/Relay | 5% | 200 | motivation |
| 6 | Cool-down | 10% | 400 | easy |

### 7.5 triathlon-efficient-3000

| Order | Block | Ratio | Distance | Notes |
|---|---|---:|---:|---|
| 1 | W-up | 15% | 450 | relaxed |
| 2 | Technique | 15% | 450 | catch, sighting if needed |
| 3 | Main aerobic | 55% | 1650 | steady EN2/EN3 |
| 4 | Pace change | 5% | 150 | short surge |
| 5 | Cool-down | 10% | 300 | bike/run fatigue considered |

## 8. 距離と時間の変換

| 練習時間 | 目安総距離 | 注意 |
|---|---|---|
| 45 分 | 1800-2600m | 説明時間を短く |
| 60 分 | 2500-3600m | Masters 標準 |
| 75 分 | 3200-4600m | Main を十分に取れる |
| 90 分 | 4000-6000m | Junior/Elite 向け |
| 120 分 | 5500m+ | 回復と補給を設計 |

## 9. 交代制時の骨格

| Block | Group A | Group B |
|---|---|---|
| W-up | Swim | Stretch |
| Drill | Swim | 陸上 Drill |
| Main round 1 | Swim | 軽セット |
| Main round 2 | 軽セット | Swim |
| Cool-down | Swim | Swim |

## 10. 保存前チェック

- [ ] 骨格を先に提示した。
- [ ] `menu_structure_pattern_id` の有無を確認した。
- [ ] Warm-up / Cool-down がある。
- [ ] Phase / Zone / Method と矛盾しない。
- [ ] Junior は 4 泳法バランスを維持した。
- [ ] 怪我・疲労制約を反映した。
