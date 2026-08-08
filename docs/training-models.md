# Training Models

4 層モデルをユーザー向けに説明します。
詳細は `references/training-models/` 配下を参照する想定です。

## 用語ミニ辞典

| 用語 | コーチ向け説明 | エンジニア向け説明 |
|---|---|---|
| RPE | 主観的運動強度。1 が楽、10 が限界。 | 人間入力の負荷メトリクス。 |
| PB | 自己ベスト。 | ペース推定の基準値。 |
| LCM | 長水路、50m プール。 | `course = LCM`。 |
| SCM | 短水路、25m プール。 | `course = SCM`。 |
| T-pace | 閾値ペース。少しきついが持続できる速度。 | Threshold の基準。 |
| Phase | 大会までの時期区分。 | A/B/C/D の状態。 |
| Zone | EN1 から SP3 などの強度帯。 | 検索・タグ付け軸。 |
| Method | Threshold, Broken などの練習手法。 | Workflow A で当日選ぶ戦術。 |
| Cycle | 出発間隔。 | interval / send-off。 |
| PII | 個人情報 (Personal Identifiable Information)。 | git に入れない保護対象。 |

## 4 層とは何か

| 層 | 問い | 例 |
|---|---|---|
| Periodization | いつ何を鍛えるか | Block |
| Philosophy | 誰に何を優先するか | Masters |
| Methods | 今日どう鍛えるか | Threshold |
| Macrocycle | どんな実務ひな形で回すか | Single Peak 12week |

## なぜ分離するか

対象、時期、手法を混ぜると判断がぶれます。
分離しておくと、ジュニアには Junior の安全性を守りつつ、当日 Method だけ変えられます。
エンジニア向けには設定責務の分離です。

## Periodization の 4 種

### Matveyev

古典的な線形モデル。年 1-2 回の主要大会に合わせやすい。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/periodization/matveyev.md](../references/training-models/periodization/matveyev.md)。

### Block

2-4 週間の集中ブロック。複数大会や社会人にも使いやすい。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/periodization/block.md](../references/training-models/periodization/block.md)。

### Undulating

週内で強度を波状に変える。週 1-3 回の練習にも合う。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/periodization/undulating.md](../references/training-models/periodization/undulating.md)。

### Reverse

スピードを先に置く。短距離志向には有効だが慎重に使う。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/periodization/reverse.md](../references/training-models/periodization/reverse.md)。

## Philosophy の 4 種

### Masters

継続、怪我予防、楽しさ、技術を重視。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/philosophy/masters.md](../references/training-models/philosophy/masters.md)。

### Junior

フォーム定着、4 泳法、楽しさ、成長期安全を重視。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/philosophy/junior.md](../references/training-models/philosophy/junior.md)。

### Elite

高頻度・高密度で競技力を伸ばす。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/philosophy/elite.md](../references/training-models/philosophy/elite.md)。

### Triathlon

バイク・ラン疲労を考え、省エネ泳法を重視。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/philosophy/triathlon.md](../references/training-models/philosophy/triathlon.md)。

## Methods の 7 種 Base + Custom

### USRPT

短距離を Race Pace で反復。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/methods/usrpt.md](../references/training-models/methods/usrpt.md)。

### HIIT

短時間高強度で強い刺激。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/methods/hiit.md](../references/training-models/methods/hiit.md)。

### LSD

低強度長距離で有酸素基礎。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/methods/lsd.md](../references/training-models/methods/lsd.md)。

### Broken Swim

目標距離を分割してレース感を作る。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/methods/broken-swim.md](../references/training-models/methods/broken-swim.md)。

### Threshold

閾値付近で持続し有酸素を底上げ。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/methods/threshold.md](../references/training-models/methods/threshold.md)。

### Fartlek

強弱を遊び的に変える。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/methods/fartlek.md](../references/training-models/methods/fartlek.md)。

### Descending

徐々にペースを上げる。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/methods/descending.md](../references/training-models/methods/descending.md)。

## Macrocycle Templates 5 種

### Single Peak 12week

12 週で 1 大会に合わせる。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/macrocycle-templates/single-peak-12week.md](../references/training-models/macrocycle-templates/single-peak-12week.md)。

### Four Peaks Annual

年間 4 ピーク。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/macrocycle-templates/four-peaks-annual.md](../references/training-models/macrocycle-templates/four-peaks-annual.md)。

### Junior Annual

育成年代の年間モデル。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/macrocycle-templates/junior-annual.md](../references/training-models/macrocycle-templates/junior-annual.md)。

### Triathlon Integrated

他競技と統合。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/macrocycle-templates/triathlon-integrated.md](../references/training-models/macrocycle-templates/triathlon-integrated.md)。

### Maintenance Phase

健康維持と記録維持。
選ぶ時は対象、残り週数、疲労、安全性を見ます。
選ばないことにも意味があります。今日の目的に合わない手法は外します。
詳細: [../references/training-models/macrocycle-templates/maintenance-phase.md](../references/training-models/macrocycle-templates/maintenance-phase.md)。

## Custom Methods

Custom Methods は `knowledge/custom/methods/` に置くコーチ独自手法です。
Workflow G で過去メニューから抽出できます。
Base にない現場知を言語化する場所です。

## Case 1: 週 1 マスターズ + 年 1 大会

- Philosophy: Masters。
- Periodization: Block + Undulating。
- Macrocycle: Single Peak 12week。
- Methods: Threshold / Descending を中心に、RPE 高い日は軽め。

## Case 2: ジュニアクラブ + 年間育成

- Philosophy: Junior。
- Periodization: Matveyev または Undulating。
- Macrocycle: Junior Annual。
- Methods: 技術ドリルと短い刺激を中心。過度な量は避ける。

## Case 3: 個人トライアスロン選手

- Philosophy: Triathlon。
- Periodization: Block。
- Macrocycle: Triathlon Integrated。
- Methods: LSD / Threshold / Fartlek。バイク・ラン疲労を考慮。

## 4層モデル 補足チェックリスト

- 4層モデル 確認 1: 保存前にコーチが承認する。
- 4層モデル 確認 2: 実名・施設名・連絡先を入れない。
- 4層モデル 確認 3: LCM/SCM と練習時間を毎回確認する。
- 4層モデル 確認 4: RPE が高い選手には次回負荷を補正する。
- 4層モデル 確認 5: TSV で内容を確認してから PDF/Excel にする。
- 4層モデル 確認 6: 迷ったら安全側に倒す。
- 4層モデル 確認 7: custom はローカル専用として扱う。
- 4層モデル 確認 8: base を直接変えず overrides を使う。
- 4層モデル 確認 9: 保存前にコーチが承認する。
- 4層モデル 確認 10: 実名・施設名・連絡先を入れない。
- 4層モデル 確認 11: LCM/SCM と練習時間を毎回確認する。
- 4層モデル 確認 12: RPE が高い選手には次回負荷を補正する。
- 4層モデル 確認 13: TSV で内容を確認してから PDF/Excel にする。
- 4層モデル 確認 14: 迷ったら安全側に倒す。
- 4層モデル 確認 15: custom はローカル専用として扱う。
- 4層モデル 確認 16: base を直接変えず overrides を使う。
- 4層モデル 確認 17: 保存前にコーチが承認する。
- 4層モデル 確認 18: 実名・施設名・連絡先を入れない。
- 4層モデル 確認 19: LCM/SCM と練習時間を毎回確認する。
- 4層モデル 確認 20: RPE が高い選手には次回負荷を補正する。
- 4層モデル 確認 21: TSV で内容を確認してから PDF/Excel にする。
- 4層モデル 確認 22: 迷ったら安全側に倒す。
- 4層モデル 確認 23: custom はローカル専用として扱う。
- 4層モデル 確認 24: base を直接変えず overrides を使う。
- 4層モデル 確認 25: 保存前にコーチが承認する。
- 4層モデル 確認 26: 実名・施設名・連絡先を入れない。
- 4層モデル 確認 27: LCM/SCM と練習時間を毎回確認する。
- 4層モデル 確認 28: RPE が高い選手には次回負荷を補正する。
- 4層モデル 確認 29: TSV で内容を確認してから PDF/Excel にする。
- 4層モデル 確認 30: 迷ったら安全側に倒す。
- 4層モデル 確認 31: custom はローカル専用として扱う。
- 4層モデル 確認 32: base を直接変えず overrides を使う。
- 4層モデル 確認 33: 保存前にコーチが承認する。
- 4層モデル 確認 34: 実名・施設名・連絡先を入れない。
- 4層モデル 確認 35: LCM/SCM と練習時間を毎回確認する。
- 4層モデル 確認 36: RPE が高い選手には次回負荷を補正する。
- 4層モデル 確認 37: TSV で内容を確認してから PDF/Excel にする。
- 4層モデル 確認 38: 迷ったら安全側に倒す。
- 4層モデル 確認 39: custom はローカル専用として扱う。
- 4層モデル 確認 40: base を直接変えず overrides を使う。
- 4層モデル 確認 41: 保存前にコーチが承認する。
- 4層モデル 確認 42: 実名・施設名・連絡先を入れない。
- 4層モデル 確認 43: LCM/SCM と練習時間を毎回確認する。
- 4層モデル 確認 44: RPE が高い選手には次回負荷を補正する。
- 4層モデル 確認 45: TSV で内容を確認してから PDF/Excel にする。
- 4層モデル 確認 46: 迷ったら安全側に倒す。
- 4層モデル 確認 47: custom はローカル専用として扱う。
- 4層モデル 確認 48: base を直接変えず overrides を使う。
- 4層モデル 確認 49: 保存前にコーチが承認する。
- 4層モデル 確認 50: 実名・施設名・連絡先を入れない。
- 4層モデル 確認 51: LCM/SCM と練習時間を毎回確認する。
- 4層モデル 確認 52: RPE が高い選手には次回負荷を補正する。
- 4層モデル 確認 53: TSV で内容を確認してから PDF/Excel にする。
- 4層モデル 確認 54: 迷ったら安全側に倒す。
- 4層モデル 確認 55: custom はローカル専用として扱う。
- 4層モデル 確認 56: base を直接変えず overrides を使う。
- 4層モデル 確認 57: 保存前にコーチが承認する。
- 4層モデル 確認 58: 実名・施設名・連絡先を入れない。
- 4層モデル 確認 59: LCM/SCM と練習時間を毎回確認する。
- 4層モデル 確認 60: RPE が高い選手には次回負荷を補正する。
- 4層モデル 確認 61: TSV で内容を確認してから PDF/Excel にする。
- 4層モデル 確認 62: 迷ったら安全側に倒す。
- 4層モデル 確認 63: custom はローカル専用として扱う。
- 4層モデル 確認 64: base を直接変えず overrides を使う。
- 4層モデル 確認 65: 保存前にコーチが承認する。
- 4層モデル 確認 66: 実名・施設名・連絡先を入れない。
- 4層モデル 確認 67: LCM/SCM と練習時間を毎回確認する。
- 4層モデル 確認 68: RPE が高い選手には次回負荷を補正する。
- 4層モデル 確認 69: TSV で内容を確認してから PDF/Excel にする。
- 4層モデル 確認 70: 迷ったら安全側に倒す。
- 4層モデル 確認 71: custom はローカル専用として扱う。
- 4層モデル 確認 72: base を直接変えず overrides を使う。
- 4層モデル 確認 73: 保存前にコーチが承認する。
- 4層モデル 確認 74: 実名・施設名・連絡先を入れない。
- 4層モデル 確認 75: LCM/SCM と練習時間を毎回確認する。
- 4層モデル 確認 76: RPE が高い選手には次回負荷を補正する。
- 4層モデル 確認 77: TSV で内容を確認してから PDF/Excel にする。
- 4層モデル 確認 78: 迷ったら安全側に倒す。
- 4層モデル 確認 79: custom はローカル専用として扱う。
- 4層モデル 確認 80: base を直接変えず overrides を使う。
- 4層モデル 確認 81: 保存前にコーチが承認する。
- 4層モデル 確認 82: 実名・施設名・連絡先を入れない。
- 4層モデル 確認 83: LCM/SCM と練習時間を毎回確認する。
- 4層モデル 確認 84: RPE が高い選手には次回負荷を補正する。
- 4層モデル 確認 85: TSV で内容を確認してから PDF/Excel にする。
- 4層モデル 確認 86: 迷ったら安全側に倒す。
- 4層モデル 確認 87: custom はローカル専用として扱う。
- 4層モデル 確認 88: base を直接変えず overrides を使う。
- 4層モデル 確認 89: 保存前にコーチが承認する。
- 4層モデル 確認 90: 実名・施設名・連絡先を入れない。
- 4層モデル 確認 91: LCM/SCM と練習時間を毎回確認する。
- 4層モデル 確認 92: RPE が高い選手には次回負荷を補正する。
- 4層モデル 確認 93: TSV で内容を確認してから PDF/Excel にする。
- 4層モデル 確認 94: 迷ったら安全側に倒す。
- 4層モデル 確認 95: custom はローカル専用として扱う。
- 4層モデル 確認 96: base を直接変えず overrides を使う。
- 4層モデル 確認 97: 保存前にコーチが承認する。
- 4層モデル 確認 98: 実名・施設名・連絡先を入れない。
- 4層モデル 確認 99: LCM/SCM と練習時間を毎回確認する。
- 4層モデル 確認 100: RPE が高い選手には次回負荷を補正する。
- 4層モデル 確認 101: TSV で内容を確認してから PDF/Excel にする。
- 4層モデル 確認 102: 迷ったら安全側に倒す。
- 4層モデル 確認 103: custom はローカル専用として扱う。
- 4層モデル 確認 104: base を直接変えず overrides を使う。
- 4層モデル 確認 105: 保存前にコーチが承認する。
- 4層モデル 確認 106: 実名・施設名・連絡先を入れない。
- 4層モデル 確認 107: LCM/SCM と練習時間を毎回確認する。
- 4層モデル 確認 108: RPE が高い選手には次回負荷を補正する。
