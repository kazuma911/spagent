# ペース推定ロジック

この文書は PB（Personal Best = 自己ベスト）、直近 `times.tsv`、RPE（Rate of Perceived Exertion = 主観的運動強度 1-10）から現在の設定ペースを推定するルールです。Workflow A Step 14 で使用し、[zone-phase-mapping.md](zone-phase-mapping.md) の Zone と組み合わせます。

## 1. 基本式

```text
current_estimate = PB × (1 + degradation_factor(RPE_avg, days_since_last_measure))
```

水泳では時間が短いほど速いため、`current_estimate` は PB より遅い値になることが一般的です。

## 2. degradation_factor

| 条件 | factor |
|---|---:|
| RPE_avg <= 4 かつ 7 日以内 | 0.00-0.01 |
| RPE_avg 5-6 かつ 14 日以内 | 0.01-0.03 |
| RPE_avg 7-8 | 0.03-0.06 |
| RPE_avg >= 9 | 0.06-0.10 |
| 30 日以上測定なし | +0.02 |
| 60 日以上測定なし | +0.04 |

例:

```text
PB = 60.00 sec
RPE_avg = 7.5
last_measure = 21 days ago
base_factor = 0.05
staleness = 0.01
current_estimate = 60.00 × (1 + 0.06) = 63.60 sec
```

## 3. Zone target as % of current_estimate

| Zone | 目標 | 100m current_estimate が 63.60 の例 |
|---|---:|---:|
| EN1 | 115%+ | 73.14 秒以上 |
| EN2 | 108% | 68.69 秒 |
| EN3 | 102% | 64.87 秒 |
| SP1 | 100% | 63.60 秒 |
| SP2 | 98% | 62.33 秒 |
| SP3 | 95% | 60.42 秒 |

`115%+` は「それ以上遅くてもよい」という意味です。EN1 で速く泳がせすぎると回復目的から外れます。

## 4. recent times.tsv の使い方

### 4.1 優先順位

1. 同距離・同泳法・同水路（LCM/SCM）の直近タイム。
2. 同距離・同泳法・別水路の補正タイム。
3. 近い距離からの換算。
4. PB のみ。

### 4.2 読み方

| データ | 解釈 |
|---|---|
| 目標達成 + RPE 低い | current_estimate を少し速める |
| 目標達成 + RPE 高い | 維持、または本数を減らす |
| 目標未達 + RPE 高い | factor を増やす |
| タイムばらつき大 | 設定を緩め、技術課題を確認 |

## 5. 怪我・疲労補正

`athlete-conditions.json` の情報を設定タイムに反映します。

| 条件 | 補正 |
|---|---|
| 肩痛 moderate | Pull / Fly / Paddle を避け、設定 +3-5% |
| 膝痛 | Breast kick を置換、Kick set +5% |
| 腰痛 | Dolphin / UDK を減らす |
| RPE 7 日平均 > 7 | Main 距離 -10-20%、SP2/SP3 を 1 段階下げる |
| 睡眠不足 | EN1/EN2 中心、Race Pace は activation のみ |
| 病み上がり | EN1、短時間、PB ベース計算を使いすぎない |

## 6. 100m Fr 例: PB 1:00、RPE avg 7.5

### 6.1 入力

```text
athlete_id: athlete-001
stroke: Free
race_distance: 100m
PB: 1:00.00 = 60.00 sec
recent RPE avg: 7.5
last measured: 21 days ago
condition: no injury, fatigue moderate
```

### 6.2 factor 決定

- RPE 7.5 は高めなので base_factor = 0.05。
- 測定が 21 日前なので staleness = 0.01。
- 怪我なしなので injury_factor = 0.00。

```text
degradation_factor = 0.05 + 0.01 + 0.00 = 0.06
```

### 6.3 current_estimate

```text
current_estimate = 60.00 × (1 + 0.06)
                 = 63.60 sec
                 = 1:03.60
```

### 6.4 Zone target

| Zone | 計算 | 設定 |
|---|---|---|
| EN1 | 63.60 × 1.15 | 1:13.1 以上 |
| EN2 | 63.60 × 1.08 | 1:08.7 |
| EN3 | 63.60 × 1.02 | 1:04.9 |
| SP1 | 63.60 × 1.00 | 1:03.6 |
| SP2 | 63.60 × 0.98 | 1:02.3 |
| SP3 | 63.60 × 0.95 | 1:00.4 |

### 6.5 メニュー反映

Phase B の Threshold day:

```text
8×100 Free @ 1:30, target 1:05-1:07, RPE 7-8
```

Phase C の Race Pace day:

```text
2 rounds:
4×50 Free @ 1:20, target 31.0-31.5, focus race rhythm
200 easy between rounds
```

疲労が高いため、SP3 の 1:00.4 相当を大量反復しません。短い activation として扱います。

## 7. グループ設定への変換

| レーン | 対象 | 100m EN3 target |
|---|---|---:|
| A | fastest group | 1:05 |
| B | middle group | 1:12 |
| C | development group | 1:20 |

怪我制約はレーンではなく個人単位で反映します。

## 8. 設定タイム決定時の**4 大現実補正**（最重要ルール）

`current_estimate` は「本人のベスト条件下 (dive / rested / 本番緊張)」のタイム目安であり、**そのまま練習設定には使えません**。以下 4 要素で必ず補正します。この補正は Workflow A Step 14 で**すべてのセット設定タイム**に適用します。

### 8.1 Dive vs Push-off の差

多くの PB / target は **dive (飛び込みスタート)** で計測されています。練習セットの多くは push-off (壁蹴りスタート) なので、そのまま target を使うと **達成不可** or **神経系疲労だけ増加** します。

| 距離 | Dive → Push-off 差 (加算) |
|---|---:|
| 50m | +1.0-1.5s |
| 100m | +1.5-2.5s |
| 200m | +2.5-4.0s |
| 400m 以上 | +4.0-6.0s |

Dive を使うセット (Dive start と明記) は補正なし。壁蹴りセットは必ず加算します。

### 8.2 練習中であること (疲労蓄積補正)

セット内で本数が進むにつれ**疲労が蓄積**します。1 本目基準の pace で最終本も達成できると仮定すると崩壊します (athlete-c 7/18 の「+10s 大失速」が典型)。

| セット構造 | 補正 |
|---|---|
| 単発 / 全力 1 本 | 補正なし |
| 少本数 (2-4 本), 十分な rest | +1-2s (100m 基準) |
| Threshold / EN3 セット (6-12 本) | **+3-5s** |
| Broken / RP hold (疲労下 hold) | **+5-8s** |
| 長い LSD 内 build | **+2-4s** |

### 8.3 年齢 (Masters / Junior 補正)

回復力・出力持続・reaction time が年代で異なります。**Masters と Junior は Elite の pace formula をそのまま使わない**。

| 対象 | 補正 |
|---|---|
| Junior (U15) | 出だし速すぎ抑制のため target を +2-3% (100m で +2s) |
| Junior (U18) | 補正なし〜+1% |
| Elite / Age group | 補正なし (base rule) |
| Masters (40 代) | +2-3% (100m で +2s) |
| Masters (50-60 代) | +4-6% (100m で +3-5s) |
| Masters (60 代以上) | +7-10% (100m で +5-7s) |

### 8.4 本番とは違うこと (本番緊張・アドレナリン補正)

PB / race target は「本番のアドレナリン + 完全休養 + 集中」の値。練習では出せない前提で:

- **練習 target = PB + (本番 - 練習の差) 3-5s (100m 基準)**
- Trans 期 (Phase B) の練習で PB hit を狙わない — 神経系のみ疲労
- Peak 期 (Phase C/D) でも練習は本番 -2s / +2s の幅で扱う (RP hit は Race day 用)

### 8.5 補正まとめ (Free 100m 例)

athlete-a 200Fr 選手 (30 代)、PB LCM 200Fr 2:04 (dive), 練習 SCM で 4×200 Descending 最終本を組む場合:

```
base = PB 200 SCM (dive) ≈ 2:00 (SCM 換算 -4s)
+ push-off penalty (200m)  ≈ +3s
+ 練習内本数疲労 (Descending 4本目)  ≈ +2s
+ 年齢 30代 補正  ≈ +1s
+ 本番との差 (Trans 期)  ≈ +4s
────────────────────────────────────
practice_final_target ≈ 2:10 (RP+10, Threshold+ zone)
```

**練習で 2:04 (=SCM race PB) を設定するのは Peak 期の Broken か Time trial のみ**。Trans 期の Descending 最終本は **T-pace+ (RP+7-10s)** が現実的上限。

### 8.6 チェックリスト (Step 14 で確認)

- [ ] Dive スタート指定なら target = そのまま、Push-off なら +1-4s
- [ ] セット本数 5 本以上なら fatigue 補正 +3-5s
- [ ] 対象選手が Masters/Junior なら年齢補正を加算
- [ ] Trans 期 (Phase B) は RP hit をセット目標にしない (Descending 最終でも RP+5 以上)
- [ ] 練習 target が PB より 5s 以上速い場合は再計算

## 9. 実装メモ

- 秒で計算し、表示時に `m:ss.xx` に変換する。
- LCM/SCM の換算は別ルールとして持ち、同水路を優先する。
- RPE は平均だけでなく直近 1 回の極端値も見る。
- PB が古すぎる場合は `current-paces.json` の現行値を優先する。
- 計算結果はコーチに提示し、保存前に対話調整する。
- **§8 の 4 大現実補正を必ず適用してから提示する** (これを飛ばすと過大 target になる)。
