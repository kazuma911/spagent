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

## 8. 実装メモ

- 秒で計算し、表示時に `m:ss.xx` に変換する。
- LCM/SCM の換算は別ルールとして持ち、同水路を優先する。
- RPE は平均だけでなく直近 1 回の極端値も見る。
- PB が古すぎる場合は `current-paces.json` の現行値を優先する。
- 計算結果はコーチに提示し、保存前に対話調整する。
