# Reverse（逆順型）

## 概要

高強度短距離を先に作り、後から有酸素基礎を足す。Sprint の速度天井を早く確認できる。

## 由来

持久系の逆順モデルを短距離水泳に応用。

## 適用対象

50/100m 専門、短期準備、速度感を失いやすい Masters sprinter。

## メニュー設計の含意

序盤から SP2/SP3 を少量高品質で入れ、後半に EN2/EN3 を足す。 Zone 配分は [Zone × Phase](../../zone-phase-mapping.md)、Method は [Phase × Method](../../phase-method-mapping.md) を参照します。

## 週間サンプル

| Day | Theme | Zone | Example |
|---|---|---|---|
| Mon | 技術 + 基礎 | EN1/EN2 | Drill 600 + 10×100 steady |
| Tue | 主刺激 | EN2/EN3 | 6×200 target pace |
| Wed | Recovery | EN1 | 2000 easy + mobility |
| Thu | 専門刺激 | EN3/SP1 | 12×50 build/hold |
| Fri | 技術補強 | EN1/EN2 | Kick + Pull moderate |
| Sat | Race link | SP1/SP2 | Broken set or descend |
| Sun | Off | REC | 休養または easy swim |

## 長所

- 速度感を早く作る。
- 短時間で効果感。
- Race Pace のズレを発見。

## 短所

- 中長距離に不向き。
- 怪我リスク。
- 有酸素不足。
- Junior は早期専門化注意。

## 運用チェック

- Warm-up / Cool-down を省略しない。
- `athlete-conditions.json` の痛み・疲労を優先する。
- Junior は 4 泳法バランスを保つ。
- Masters は高強度連続を避ける。
- 予定より安全を優先し、変更は [feedback-process](../../feedback-process.md) に残す。

## spagent での指定

```json
{ "periodizations": ["reverse"] }
```

## Phase 別の詳細運用

| Phase | 量 | 強度 | 技術 | 注意 |
|---|---|---|---|---|
| A | 多め | 低-中 | 多い | 単調化を避ける |
| B | 中 | 中-高 | 目的別 | Threshold の疲労を監視 |
| C | 中-少 | 高 | Race specific | 成功反復を優先 |
| D | 少 | 高品質 | 短く明確 | 新しい課題を入れない |
| REC | 少 | 低 | 楽に | 回復を最優先 |

## 週次負荷調整ルール

- 3 週積み上げたら 1 週は軽くする。
- RPE 平均が 7 を超える週は翌週の Main volume を 10-20% 減らす。
- タイム低下とフォーム崩れが同時に出たら、強度ではなく回復不足を疑う。
- Junior は成長痛や学校行事を考慮する。
- Masters は仕事疲労と睡眠不足を確認する。
- Elite は乳酸値、心拍、動画、主観を合わせて判断する。

## メニュー骨格への落とし込み

| Day type | W-up | Drill | Main | C-down |
|---|---:|---:|---:|---:|
| Aerobic | 18% | 10% | 55% | 12% |
| Threshold | 20% | 8% | 55% | 12% |
| Race Pace | 25% | 10% | 40% | 15% |
| Recovery | 20% | 25% | 35% | 20% |

## コーチへの確認質問

1. 主要大会はいつか。
2. 今週の最優先テーマは何か。
3. 参加者の疲労は高いか。
4. 怪我で避ける動作はあるか。
5. レーン数と時間は十分か。
6. 今日の成功条件はタイムか、フォームか、完遂か。
7. 次回に残したい観察項目は何か。

## よくある失敗

| 失敗 | 修正 |
|---|---|
| すべての能力を毎回鍛える | 主目的を 1 つに絞る |
| 高強度を予定通り強行 | RPE とフォームで中止判断 |
| Phase D で量を落とさない | 距離を減らし速度刺激を残す |
| REC で追い込む | EN1 と技術に戻す |
| Junior が専門種目だけになる | IM と 4 泳法を入れる |

## データ反映

`plans/*.md` には週テーマ、主 Zone、想定 Method を書きます。実施後は [feedback-process](../../feedback-process.md) に従い、実際の負荷と変更履歴を残します。

```markdown
Week 5:
- Phase: B
- Main Zone: EN3
- Method: Threshold + Descending
- Risk: shoulder fatigue check
```

## 指標

- 予定距離に対する実施距離。
- 目標タイム達成率。
- RPE 平均と最大値。
- 技術キューの達成度。
- 次回までの回復状況。
- 怪我・痛みの有無。

## 短縮版運用

時間が短い日は、W-up と C-down を残して Main の本数を減らします。Drill を完全に削るより、2-4 本だけでもテーマを残します。

```text
通常: 8×100 main
短縮: 5×100 main + 200 easy
```

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

