# Zone × Phase マッピング

この文書は spagent の canonical（標準）な Zone（強度帯）と Phase（大会までの時期）対応表です。Workflow A Step 8-10、索引タグ付け、長期計画作成で参照します。関連: [phase-method-mapping.md](phase-method-mapping.md)、[pace-estimation.md](pace-estimation.md)。

## 1. Phase-Zone weight table

メインセット総距離または主練習時間を 100% とした推奨配分です。

| Phase | 位置づけ | EN1 | EN2 | EN3 | SP1 | SP2 | SP3 | 主目的 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| A | General Preparation（基礎準備） | 30% | 40% | 20% | 10% | 0% | 0% | 有酸素基礎、技術再構築、量への適応 |
| B | Specific Preparation（専門準備） | 0% | 30% | 40% | 20% | 10% | 0% | Threshold、レース強度への移行 |
| C | Pre-Competition（試合前） | 0% | 20% | 20% | 30% | 20% | 10% | Race Pace、VO2max、耐乳酸 |
| D | Taper / Sharpen（調整） | 0% | 0% | 20% | 30% | 30% | 20% | 量を落として強度・速度感を維持 |
| REC | Recovery（回復） | 70% | 30% | 0% | 0% | 0% | 0% | 回復、技術確認、血流促進 |

### 1.1 補正

- Phase D は taper（テーパー = 試合前に練習量を落とす調整）なので、距離は減らすが強度刺激は残す。
- Masters は Phase C/D でも EN1 を追加してよい。
- Junior は Zone 配分だけでなく 4 泳法と Drill の学習量を優先する。
- Triathlon は EN2 を厚めに残し、Bike/Run 疲労で SP2/SP3 を抑える。

## 2. Zone descriptions

| Zone | 名称 | 目安心拍 | RPE | ペース感 | 主な使い方 |
|---|---|---|---|---|---|
| EN1 | Recovery / Easy（回復・軽め） | 約 65% MHR | 3-5 | 会話可能、楽 | W-up、C-down、回復日、技術確認 |
| EN2 | Aerobic Base（有酸素基礎） | 約 75% MHR | 5-6 | 持続可能、呼吸安定 | 基礎持久力、長めの set |
| EN3 | Lactate Threshold（乳酸閾値） | 約 85% MHR | 7-8 | きついが維持可能 | T-pace、Threshold set |
| SP1 | VO2max（最大酸素摂取能力） | 約 92% MHR | 8-9 | 3-6 分相当の高強度 | 100-400m 系高強度反復 |
| SP2 | Lactate Tolerance（耐乳酸） | 約 96% MHR | 9 | 100-200m Race Pace | Broken、Race Pace repeat |
| SP3 | Speed / Race Pace（速度・レース速度） | 100%+ | 9-10 | 短距離全力、神経系 | Dive、25/50 sprint、USRPT |

MHR = maximum heart rate（最大心拍数）。短距離では心拍が遅れて出るため、RPE、タイム、フォーム維持を併用します。

## 3. Keyword → Zone tagging rules

`scripts/index/tag_zones_phases.py` はメニュー名、テーマ、セット説明から以下のキーワードを読み取り、`zone_tags` を付与します。

### 3.1 Canonical dict

```python
ZONE_KEYWORDS = {
    "EN1": [
        "easy", "recovery", "recover", "smooth", "loosen", "swim down",
        "cool-down", "c-down", "down", "drill easy", "form", "technique",
        "リカバリ", "回復", "軽め", "楽に", "フォーム", "技術", "ダウン"
    ],
    "EN2": [
        "aerobic", "endurance", "base", "steady", "long", "distance",
        "pull steady", "kick steady", "EN2", "z2",
        "有酸素", "持久", "基礎", "一定", "長め"
    ],
    "EN3": [
        "threshold", "t-pace", "t pace", "T30", "critical swim speed", "css",
        "hold pace", "negative split threshold", "EN3", "AT", "LT",
        "閾値", "スレッショルド", "乳酸閾値", "一定高強度"
    ],
    "SP1": [
        "VO2", "VO2max", "3'-6'", "3-6min", "max aerobic", "hard aerobic",
        "SP1", "200 pace strong", "400 pace hard", "最大酸素", "高強度有酸素"
    ],
    "SP2": [
        "lactate tolerance", "race pace", "100 race pace", "200 race pace",
        "broken 100", "broken 200", "sprint 50", "SP2", "RP100", "RP200",
        "耐乳酸", "レースペース", "50 スプリント", "100 ペース"
    ],
    "SP3": [
        "all-out", "max", "sprint 25", "dive", "start", "power", "speed",
        "USRPT", "race pace 50", "SP3", "25 fast", "underwater fast",
        "全力", "ダイブ", "スタート", "神経", "パワー", "最速"
    ]
}
```

### 3.2 複数タグ時の優先

| 状況 | 付与 |
|---|---|
| Easy + Drill + Sprint | EN1 と SP3 |
| Threshold main + Sprint finisher | EN3 と SP3 |
| Race pace 100 と Broken 200 | SP2 |
| VO2 4 分反復 | SP1 |
| Long aerobic with final descend | EN2 と EN3 |

`fast` 単独では Zone を決めません。距離、本数、rest、文脈を読みます。

## 4. Phase判定 rules

Phase は `data/competitions.json` の最も近い `priority=A` 大会 `start_date` を基準にします。グループでは、参加者の中で最も近い `priority=A` 大会を持つ選手の Phase に合わせます。

```text
weeks_remaining = (competition.start_date - session_date) / 7
```

| 条件 | Phase | 意味 |
|---|---|---|
| 大会なし、または 12 週超 | A | General Preparation |
| 8-12 週 | B | Specific Preparation |
| 4-7 週 | C | Pre-Competition |
| 1-3 週 | D | Taper / Sharpen |
| 大会翌日から 1 週程度 | REC | Recovery / Transition |

### 4.1 post-race 判定

- `session_date` が `start_date` 後で、次の主要大会が未登録なら REC。
- 複数日大会の最終日後 1-7 日は REC を推奨。
- REC 中は技術・可動域・EN1/EN2 で回復を促す。

### 4.2 手動上書き

コーチ判断で Phase は手動上書き可能です。ただし出力サマリに理由を明記します。

```text
Phase: REC (manual override; originally C, competition in 5 weeks)
Reason: 直近 7 日 RPE 平均が高く、肩痛者が複数いるため
```

## 5. Workflow での使い方

1. Phase を判定する。
2. §1 の Zone 配分をベースに主 Zone を選ぶ。
3. [phase-method-mapping.md](phase-method-mapping.md) で Method 候補を選ぶ。
4. [pace-estimation.md](pace-estimation.md) で設定タイムを計算する。
5. [menu-design.md](menu-design.md) で骨格に落とし込む。
6. 実施後は [feedback-process.md](feedback-process.md) に沿って索引を更新する。
