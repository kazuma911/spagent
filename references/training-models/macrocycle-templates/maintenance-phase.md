# Maintenance Phase（維持フェーズ型）

## 対象コーチ像

大会目標なし、健康維持、復帰、技術維持を重視するコーチ。

## ピークの数と配置

ピークを作らず、月単位で小テーマを回す。

## フェーズ配分

A/REC 中心に B/C 刺激を少量。D は原則使わない。 Phase 定義は [Phase 判定](../../zone-phase-mapping.md#4-phase判定-rules) を参照します。

## 週次テーマの流れ

| Week | Theme | Phase | Zone / Method |
|---|---|---|---|
| 1 | 現状確認・技術 | A | EN1/EN2, Drill |
| 2 | 基礎持久 | A | EN2, LSD/Fartlek |
| 3 | 基礎 + 変化 | A | EN2 + Descending |
| 4 | Threshold 導入 | B | EN3, Threshold |
| 5 | Threshold 発展 | B | EN3, Descending |
| 6 | Race link | B/C | SP1, Broken intro |
| 7 | Race Pace | C | SP1/SP2, Broken |
| 8 | Speed quality | C | SP2/SP3, USRPT short |
| 9 | 調整 | D | Volume down, intensity keep |
| 10 | Race or test | D | Sharpen |
| 11 | Recovery | REC | EN1, technique |
| 12 | Review | A/REC | feedback and planning |

## サンプル年間 / 半期スケジュール

| 期間 | 目的 | Notes |
|---|---|---|
| Month 1 | 技術と基礎 | Kick/Drill と EN2 |
| Month 2 | Threshold | EN3 と Descending |
| Month 3 | Race Pace | Broken / USRPT / taper |
| Race week | Sharpen | 量を落として速度維持 |
| Post race | Recovery | feedback, conditions update |

## メニュー設計の含意

- Macrocycle は骨格であり、当日は Workflow A で Phase / Zone / Method に落とす。
- `menu_structure_pattern_id` があれば [menu-design.md](../../menu-design.md) の Custom pattern を優先する。
- 疲労や怪我があれば計画より安全を優先する。
- 実施後は [feedback-process.md](../../feedback-process.md) で索引と insight を更新する。

## 運用チェックリスト

- [ ] 主要大会が `data/competitions.json` にある。
- [ ] 週テーマが `plans/*.md` に反映されている。
- [ ] 回復週がある。
- [ ] Junior は 4 泳法バランスを保つ。
- [ ] Masters は高強度連続を避ける。
- [ ] Triathlon は Bike/Run 疲労を確認する。

## spagent での指定

```json
{ "macrocycle": "maintenance-phase" }
```

## 計画作成ステップ

1. `data/competitions.json` で主要大会を確認する。
2. 今日の日付から残り週数を計算する。
3. Phase を割り当てる。
4. 週ごとの主 Zone を決める。
5. 回復週を先に置く。
6. Method 候補を決める。
7. `plans/*.md` に週テーマを書く。
8. Workflow A で当日メニューに展開する。
9. Workflow B で実施結果を反映する。

## Phase 配分例

| Block | Weeks | Main Zone | Method |
|---|---:|---|---|
| Base | 1-4 | EN1/EN2 | LSD / Fartlek |
| Build | 5-8 | EN3 | Threshold / Descending |
| Race | 9-10 | SP1/SP2 | Broken / HIIT |
| Taper | 11 | SP2/SP3 | USRPT short |
| Recover | 12 | EN1 | Easy / technique |

## 週次レビュー項目

- 予定距離と実施距離。
- 主 Zone が守られたか。
- RPE が想定内か。
- 怪我・痛みの更新があるか。
- 次週に上げるか、維持するか、下げるか。
- Custom pattern に反映すべき傾向があるか。

## サンプル plans/*.md 記述

```markdown
## Week 6

- Phase: B
- Main Zone: EN3 / SP1
- Method candidates: Threshold, Descending
- Technical focus: catch timing and turn speed
- Risk controls: no paddles for athlete-001
```

## メニュー生成への接続

| Workflow A Step | Macrocycle から渡すもの |
|---|---|
| Step 7 | Profile と週テーマ |
| Step 8 | Phase の前提 |
| Step 9 | Zone 配分の目安 |
| Step 10 | Method 候補 |
| Step 13 | 骨格パターン |
| Step 14 | ペース設定への強度情報 |

## よくある失敗

| 失敗 | 修正 |
|---|---|
| 年間表だけ作り実施を見ない | 毎週 feedback を反映する |
| 大会が増えても Phase を変えない | `competitions.json` を更新する |
| REC を省略 | 大会後 1 週は回復を入れる |
| 全員同じピーク | グループの大会優先度を確認する |
| Custom pattern が計画を壊す | 安全制約と Phase を優先する |

## 短期変更ルール

- 体調不良者が多い: その週を REC 寄りにする。
- 施設時間が短い: Main を削り、W-up/C-down は残す。
- 大会が前倒し: C/D を圧縮し、量を急に増やさない。
- 大会が延期: B を延長し、同じ刺激を繰り返しすぎない。
- 技術課題が重大: Phase より Drill 比率を上げる。

## 成功指標

- 主要大会で狙った週に疲労が抜けている。
- 直前期に速度感が残っている。
- 怪我で離脱しない。
- Junior は多種目の基礎が伸びる。
- Masters は継続率が高い。
- Triathlon は Bike/Run へ疲労を残しすぎない。

## レビュー後の保存

計画変更は `plans/*.md` に、実施差分は `sessions/YYYY-MM-DD/feedback.md` に残します。AI insight はコーチ承認後にのみ `athlete-insights.json` へ保存します。

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

