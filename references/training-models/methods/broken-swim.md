# Broken Swim（分割レース泳）

## 概要

目標距離を分割し、合計でレースを再現する。

## 由来・提唱者

実務で広く使われる手法として扱います。特定個人名ではなく、目的・強度・停止条件を明確にして運用します。

## 生理学的根拠

レース速度、乳酸耐性、ペース配分、後半維持を練習する。 評価はタイム、RPE、フォーム、回復の 4 点で行います。

## 代表セット例

| Set | 内容 | Target |
|---|---|---|
| 1 | Broken 200: 4×50 rest :20 | 主目的を維持 |
| 2 | Broken 100: 50+25+25 rest :20/:15 | ペース再現 |
| 3 | 3 rounds: 6×25 quality + 200 easy | 短縮/応用 |

## 適用フェーズ

Phase C/D。詳細は [Phase × Method](../../phase-method-mapping.md) を参照します。

## 適用対象

100-400m Race Pace、Masters/Elite。

## 注意点

レスト設定で刺激が変わる。

## メニュー化の手順

1. Phase を確認する。
2. 主 Zone を [zone-phase-mapping.md](../../zone-phase-mapping.md) で確認する。
3. 対象 Philosophy に合わせて本数・休息を調整する。
4. `athlete-conditions.json` で禁止動作を確認する。
5. [pace-estimation.md](../../pace-estimation.md) で目標タイムを出す。

## 置換ルール

| 問題 | 置換 |
|---|---|
| 肩痛 | Fly/Paddle を避け Free easy または Back drill |
| 高疲労 | Zone を 1 段階下げる |
| レーン混雑 | 距離を短くし出発間隔を広げる |
| Junior のフォーム崩れ | Drill に戻す |
| Masters の回復不足 | 本数 -20%、rest +10-20 秒 |

## セット設計パラメータ

| Parameter | 説明 | 調整例 |
|---|---|---|
| distance | 1 本の距離 | 25/50/100/200m |
| repeats | 本数 | 疲労時は -20% |
| cycle | 出発間隔 | 混雑時は +5-10 秒 |
| rest | 休息 | Race Pace は長めも可 |
| target | 目標タイム | [pace-estimation](../../pace-estimation.md) で算出 |
| stop rule | 中止条件 | miss、痛み、フォーム崩壊 |

## Progression（発展）

- 同じタイムで本数を増やす。
- 同じ本数で rest を短くする。
- 同じ rest で target を少し速くする。
- 種目を専門種目に近づける。
- ターン、スタート、呼吸制限などレース要素を足す。

一度に複数の変数を上げないことが原則です。

## Regression（軽減）

- 本数を減らす。
- Zone を 1 段階下げる。
- rest を長くする。
- 距離を 100m から 50m に短くする。
- Paddle、Fly、Breast kick など負担の強い要素を外す。

## ペース設定

| 状況 | 判断 |
|---|---|
| target 達成 + RPE 低い | 次回少し強める |
| target 達成 + RPE 高い | 維持または本数減 |
| target 未達 + RPE 高い | 強度を下げる |
| target 未達 + RPE 低い | 技術・集中・設定ミスを確認 |
| ばらつき大 | Descending や短距離で再学習 |

## よくある失敗

| 失敗 | 修正 |
|---|---|
| Method 名だけで作る | Zone と停止条件を明記する |
| 全員同じ target | レーンまたは個人で丸める |
| 疲労時も予定本数を維持 | RPE とフォームで調整 |
| Junior に高強度を長く続ける | Drill と遊びを挟む |
| Cool-down を削る | Main を削って C-down を残す |

## TSV 記述例

```text
block	set	distance	stroke	cycle	target	note
main	8x100	100	Free	1:30	EN3 target	RPE 7-8, hold form
```

## フィードバック記録

実施後は [feedback-process](../../feedback-process.md) の 7 項目テンプレートに、成功条件・変更履歴・次回ペース案を書きます。

## 安全上の停止条件

- 痛みが出る、または増える。
- 呼吸が戻らない。
- 目標意図を超えて RPE 10 が続く。
- フォームが崩れ、修正しても戻らない。
- レーン混雑で接触リスクがある。

## コーチ確認質問

1. 今日の Method を選ぶ理由は何か。
2. どの Zone が主目的か。
3. 成功条件はタイムかフォームか。
4. 何回 miss したら止めるか。
5. 怪我で置換する選手はいるか。
6. 次回に何を記録するか。

## 対象別補正

| Philosophy | 補正 |
|---|---|
| Masters | rest 長め、本数少なめ、回復重視 |
| Junior | 技術停止条件、4 泳法バランス |
| Elite | データで精密化、目的を狭く |
| Triathlon | Bike/Run 疲労を考慮、脚負荷を抑える |

## 最終確認チェックリスト

- [ ] 今日の主目的を 1 文で説明できる。
- [ ] Phase と Zone の根拠が明記されている。
- [ ] Method の停止条件がある。
- [ ] Warm-up と Cool-down が残っている。
- [ ] 怪我・疲労制約を反映した。
- [ ] Junior は 4 泳法バランスを崩していない。
- [ ] Masters は回復時間を確保した。
- [ ] Triathlon は Bike/Run 疲労を確認した。
- [ ] Elite は測定指標と主観を併用した。
- [ ] 変更があれば `feedback.md` に残す。

## 参照リンク

- [Zone × Phase](../../zone-phase-mapping.md)
- [Phase × Method](../../phase-method-mapping.md)
- [Pace Estimation](../../pace-estimation.md)
- [Menu Rules](../../menu-rules.md)
- [Feedback Process](../../feedback-process.md)

