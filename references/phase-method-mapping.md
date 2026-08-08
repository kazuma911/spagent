# Phase × Method マッピング

この文書は 7 つの Base Methods（USRPT, HIIT, LSD, Broken, Threshold, Fartlek, Descending）を Phase A/B/C/D/REC にどう割り当てるかを定義します。Zone 配分は [zone-phase-mapping.md](zone-phase-mapping.md)、骨格は [menu-design.md](menu-design.md) を参照します。

## 1. 記号

| 記号 | 意味 |
|---|---|
| ⭐ | 推奨。Phase の主目的と強く合う |
| ○ | 使用可。量・強度を調整すれば有効 |
| △ | 文脈依存。対象や疲労で判断 |
| ✗ | 原則避ける。安全・目的の面で不一致 |

## 2. Matrix

| Method | Phase A | Phase B | Phase C | Phase D | REC |
|---|---|---|---|---|---|
| USRPT | △ | ○ | ⭐ | ⭐ | ✗ |
| HIIT | △ | ○ | ⭐ | ○ | ✗ |
| LSD | ⭐ | ○ | △ | ✗ | ○ |
| Broken Swim | △ | ○ | ⭐ | ⭐ | ✗ |
| Threshold Training | ○ | ⭐ | ○ | △ | ✗ |
| Fartlek | ○ | ○ | △ | △ | ⭐ |
| Descending Sets | ○ | ⭐ | ⭐ | ○ | △ |

## 3. 理由

Phase A は有酸素基礎と技術再構築が中心です。LSD（Long Slow Distance = 低強度長距離）は基礎づくりに向きますが、単調になりやすいため Fartlek（変化泳）や Descending（徐々に上げる）を少量入れると集中が続きます。USRPT や HIIT は少量の神経刺激としてなら使えますが、主役にすると基礎期の目的から外れます。

Phase B は Threshold Training（乳酸閾値付近の持続）が中心です。EN3 を厚くし、Descending で後半に上げる力を作ります。Broken Swim はレースペースへの橋渡しとして有効です。

Phase C は Race Pace（レースペース）と高強度耐性を高める時期です。Broken、HIIT、USRPT が主役になります。ただし疲労が溜まりやすいため、Masters や Junior では本数を減らし、フォーム維持を条件にします。

Phase D は taper です。総量を落としつつ、Broken と USRPT でレース速度の感覚を残します。LSD は疲労を増やすだけになりやすいため避けます。

REC は回復期です。Fartlek を遊び的に軽く使うか、EN1/EN2 の easy swim にします。HIIT、USRPT、Broken のような高強度手法は避けます。

## 4. Method 別メモ

### 4.1 USRPT

- 25m/50m を Race Pace で反復する。
- Missed repeats（目標未達が続いたら終了）を守る。
- Phase C/D では質を保ちやすい。
- Phase A では技術が崩れない少量のみ。

### 4.2 HIIT

- 心肺・VO2max・乳酸耐性に有効。
- 短時間で強い刺激を出せる。
- Junior はフォーム崩壊に注意。
- Masters は翌日回復を考える。

### 4.3 LSD

- EN1/EN2 の基礎づくり。
- Phase A と REC に適する。
- 速度感を失わないよう 25m build や Drill を挟む。

### 4.4 Broken Swim

- 目標距離を分割し、合計でレースを再現する。
- Phase C/D の主力。
- レストが長すぎると別物になるため目的を明記する。

### 4.5 Threshold Training

- EN3 の持続力を作る。
- Phase B の中心。
- RPE が高止まりする日は EN2 に落とす。

### 4.6 Fartlek

- 速い/遅いを自由に切り替える。
- REC や Masters の継続性に有効。
- 目的が曖昧にならないよう、速い区間の距離を決める。

### 4.7 Descending Sets

- ペース感覚と後半上げる能力を作る。
- Phase B/C で有効。
- 全本 all-out にしない。最後に向けて上げる。

## 5. Philosophy による補正

| Philosophy | 補正 |
|---|---|
| Masters | HIIT/USRPT/Broken の連続実施を避ける。回復日を入れる |
| Junior | 技術崩れを停止条件にする。4 泳法を維持 |
| Elite | 乳酸・心拍・動画指標で精密化する |
| Triathlon | Bike/Run 疲労を考慮し、LSD/Threshold を多めにする |

## 6. Custom Methods

コーチ固有の方法は `knowledge/custom/methods/` に Markdown として保存されます。Workflow G の傾向分析で、Base Methods に分類しにくい頻出パターンがあれば Custom Method として抽出します。

### 6.1 読み込みルール

- ファイル名は `<slug>.md`。
- 先頭に目的、適用 Phase、主 Zone、代表セットを書く。
- Workflow A Step 10 では Base Methods と同列に候補提示する。
- `data/coach-preferences.json` の `use_base_knowledge` が `custom_only` の場合、Custom Methods を優先する。

### 6.2 推奨フォーマット

```markdown
# custom-method-name

## 概要

## 主 Zone

## 適用 Phase

## 代表セット

## 避ける条件
```

### 6.3 Base との競合

Custom Method が Threshold と似ていても、コーチの意図が異なるなら Custom として残します。例: 「週末 3000m 変化持久」は EN2/EN3/Fartlek の混合ですが、定番骨格として扱う価値があります。
