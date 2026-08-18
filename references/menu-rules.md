# メニュー運用ルール

この文書は spagent が Workflow A（練習メニュー作成）で使う運用ルールです。対象は水泳コーチと、メニュー生成ロジックを扱うエンジニアです。骨格は [menu-design.md](menu-design.md)、Phase/Zone は [zone-phase-mapping.md](zone-phase-mapping.md)、ペースは [pace-estimation.md](pace-estimation.md) を併用します。

## 1. 基本原則

- コーチの最終判断を優先する。
- 全メニューに Warm-up（ウォームアップ）と Cool-down（クールダウン）を必ず入れる。
- Junior は 4 strokes（Fly / Back / Breast / Free）を週内に入れ、早期専門化を避ける。
- `athlete-conditions.json` の怪我・疲労制約はメニュー内容とペースに直接反映する。
- グループ指導では全体テーマを揃え、個別条件は距離・サイクル・泳法置換で調整する。
- 選手は `athlete-001` のようなエイリアスで扱い、実名・施設実名・連絡先は書かない。

## 2. Workflow A での位置づけ

| Step | 判断 | 参照 |
|---|---|---|
| 2 | LCM/SCM、時間、使用レーン | `data/training-schedule.json`, `data/facilities.json` |
| 4 | 出席者 | `data/groups.json`, `data/athletes.json` |
| 5 | 怪我・体調・技術課題 | `data/athlete-conditions.json`, `data/athlete-skill-notes.json` |
| 6 | 交代制 | 本文書 §4-§7 |
| 8 | Phase 判定 | [Phase 判定](zone-phase-mapping.md#4-phase判定-rules) |
| 13 | 骨格設計 | [menu-design.md](menu-design.md) |
| 14 | ペース設定 | [pace-estimation.md](pace-estimation.md) |

## 3. 個別指導とグループ指導

### 3.1 個別指導

- 対象選手の `priority=A` 大会から Phase を決める。
- 技術課題は `athlete-skill-notes.json` の `focus_areas` から Drill に反映する。
- レース種目に合わせて Zone 配分を微調整する。
- 痛みがある場合は該当動作を避け、医療従事者への相談を案内する。

### 3.2 グループ指導

- Phase は参加者の中で最も近い `priority=A` 大会に合わせる。
- Main set の主 Zone は揃え、個別化は距離・サイクル・泳法で行う。
- 速度差が大きい場合は 5-10 秒間隔で出す。
- レーン内追い越しルールを練習前に確認する。
- Junior グループは全泳法と基礎運動を含める。

## 4. 収容人数と交代制判定

交代制は次の式で判断します。

```text
capacity = usable_lanes × max_swimmers_per_lane
```

| 変数 | 意味 | 例 |
|---|---|---|
| `usable_lanes` | 実際に使えるレーン数 | 2 |
| `max_swimmers_per_lane` | 1 レーンの安全上限 | 4 |
| `participants` | 当日の実出席者数 | 10 |
| `capacity` | 通常運用可能人数 | 8 |

`participants > capacity` の場合は群 A / 群 B の交代制を提案します。例: `2 × 4 = 8` で 10 人なら 2 人分が収容超過です。

## 5. 交代制の設計

### 5.1 群分け

- 2 群を基本にする。
- 速度差だけでなく安全なレーン流れを優先する。
- 怪我のある選手は待機側も低負荷にする。
- 同じ選手が常に先行群にならないよう順序を回す。

### 5.2 交代単位

| 交代単位 | 適する場面 | 注意 | 総距離補正 |
|---|---|---|---|
| ブロック単位 | Drill / Kick / Main を分ける | 待機が長くなりすぎない | ×0.7 |
| セット単位 | 8×50 など本数が明確 | コーチの声かけがしやすい | ×1.0 |
| 時間単位 | 10 分交代 | 距離記録がずれやすい | **×0.5** |
| レーン単位 | 片側水中、片側待機 | 施設制約に左右される | ×1.0 |

**総距離補正**は「群 A/B **各群あたり**の泳距離見積もり」に掛ける係数。時間単位はほぼ半分の実泳時間になるため必ず ×0.5 を適用します。ブロック単位は待機側の陸ドリル等を挟むため ×0.7。セット/レーン単位は両群がほぼ同時に水中なので補正不要。

## 6. 待機側パターン（Workflow A Step 6）

### 6.1 ① 完全待機

高強度直後、体調不良者が多い日、安全確保を優先する日に使います。水分補給、呼吸調整、次セット確認を行い、3 分を超える場合は体が冷えないよう軽い肩回しを入れます。

### 6.2 ② ストレッチ

肩甲帯、胸椎、股関節、足首を軽く動かします。Masters では可動域維持、Junior では身体操作の学習として使えます。

| 部位 | 内容 | 時間 |
|---|---|---|
| 肩甲帯 | 肩回し、壁スライド | 30-60 秒 |
| 胸椎 | 回旋ストレッチ | 左右 5 回 |
| 股関節 | ランジ姿勢 | 左右 30 秒 |
| 足首 | カーフレイズ軽め | 10 回 |

### 6.3 ③ 軽ドリル

技術テーマを待機側にも浸透させたい日に使います。EVF（Early Vertical Forearm = 早い前腕の立ち上げ）、ストリームライン、呼吸時の体幹回旋を陸上で確認します。

### 6.4 ④ 陸トレ

待機時間が長い場合、Junior の全身運動能力を育てたい場合に使います。ただし濡れた床でのジャンプ、肩痛者への腕立て、Main 前に脚を潰す種目は避けます。

| 目的 | 種目 | 量 |
|---|---|---|
| 体幹 | Dead bug | 左右 6 回 |
| 肩安定 | Scapular push-up | 8 回 |
| 股関節 | Hip hinge | 10 回 |
| 反応 | ミニジャンプ | 5 回、安全時のみ |

### 6.5 ⑤ 軽セット

サブレーンや浅いスペースがある時に使います。RPE（主観的運動強度 1-10）は 3-4 に抑え、待機側で疲労を増やしすぎないようにします。

```text
4×25 Easy Swim @ :45, focus: long body
4×25 Kick easy @ :50, no board if shoulder pain
2×50 Drill/Swim by 25 @ 1:20
```

## 7. athlete-conditions.json との統合

### 7.1 例

```json
{
  "athlete_id": "athlete-001",
  "fatigue_rpe_7d_avg": 7.2,
  "injuries": [
    {"area": "shoulder", "side": "right", "severity": "moderate", "avoid": ["butterfly", "paddles", "all-out"]}
  ]
}
```

### 7.2 制約と変更

| 条件 | メニュー変更 |
|---|---|
| 肩痛 | Fly、Paddle、長い Pull を避ける |
| 腰痛 | Dolphin kick、反りの強い Drill を避ける |
| 膝痛 | Breast kick、強い壁蹴りを減らす |
| RPE 7 日平均 > 7 | Main 本数 -10-20%、Zone を 1 段階下げる |
| 睡眠不足 | SP2/SP3 を EN1/EN2 に置換 |
| 病み上がり | REC/EN1 のみ、短時間 |

### 7.3 Butterfly 制限

バタフライ制限がある選手には `Fly -> Free smooth`、`Fly -> Back drill`、または `Body dolphin easy` へ置換します。Junior 全体では 4 泳法バランスを維持しつつ、該当選手の痛み回避を優先します。

| athlete_scope | stroke | distance | instruction |
|---|---|---|---|
| all | IM | 4×100 | odd smooth / even build |
| athlete-001 | Free | 4×100 | Fly segment replaced by Free smooth |

## 7.4 USRPT の反復ユニット原則

USRPT (Ultra-Short Race-Pace Training) は「レース pace の忠実再現」＋「fail-stop 即中止」が本質。反復距離 (unit) は**目標種目の距離に応じて縮める**:

| 目標種目 | USRPT ユニット | 例 |
|---|---|---|
| 200 | **50 m** | 12–20×50 @ 200p, rest 20–30s |
| 100 | **25 m** | 16–30×25 @ 100p, rest 15–25s |
| 50 | **25 m 未満 / 12.5 m** | 25/12.5 @ 50p, rest 15–20s |
| 400 以上 | 50–100 m | 200 event と同等でも可 |

理由: USRPT の目的は race pace を反復可能な rest で維持すること。unit が目標距離に近すぎると通常の RP セットになり、fail-stop の意味が薄れる。sprinter (athlete-c / aya / athlete-i) に対しては **25m unit を第一選択**にする。

## 7.5 REST / 中盤休憩ルール

セッション内の Rest には 2 種類ある。それぞれ**目的が違う**ので混同しない:

### 7.5.1 セクション間 Rest (短)

セクション (W-up / Main-A / Main-B など) の区切りに入れる短い間。**Excel の時間計算式維持のため必ず 1 行入れる** (description = `rest`)。

| 直前セクションの強度 | Rest 目安 |
|---|---|
| Easy (W-up, Recovery, Bridge) | 1' |
| Moderate (Pre-set, Broken 短め) | 2' |
| Hard (Threshold, USRPT, Descending) | 2-3' |

### 7.5.2 中盤 REST (長)

Main ブロックの中間に置く**戦略的な長休憩**。以下のいずれかに該当したら中盤 REST を組み込むこと:

- 練習時間 ≥ 90 min
- 主要 Main セットが 3 セット以上
- サブグループ交代で疲労蓄積が読める場合
- gear -1 以下の選手を含む
- 気温が高い / 集中力低下が懸念される

**最低所要時間**:

| 練習時間 | 中盤 REST 最低 | 推奨 |
|---|---|---|
| 60-89 min | 3' | 5' |
| 90-119 min | **5'** | **8'** |
| 120-149 min | 8' | 10-12' |
| ≥ 150 min | 10' | 12-15' (2 回分割も可) |

- **水分補給 / 給水は 5 min 以上を推奨** (2-3 min では実質補給できない)
- REST 中の活動: 水分・簡単ストレッチ・耳学 (他サブグループのセット観察) 全て OK
- **表示**: `🛑 REST 共通 8 min` のようにアイコン + 時間を明示

### 7.5.3 例外

- レース前 Peak/Taper 期 の short session (60 min 未満) は中盤 REST 不要
- Recovery / gear-3 練習は全体が休憩相当なので中盤 REST 不要
- コーチが「詰めて実施したい」と明示した場合は中盤 REST を圧縮可 (最低値まで)

## 8. Warm-up / Cool-down 必須ルール

### 8.1 Warm-up

Warm-up は距離稼ぎではなく、神経・関節・呼吸を Main に接続する時間です。

必須要素:

1. Easy swim。
2. Mobility と Drill。
3. Main Zone へ向かう build。
4. 安全確認。

```text
400 choice easy
6×50 Drill/Swim by 25 @ 1:10
4×25 build to EN2 @ :45
```

### 8.2 Cool-down

Cool-down は EN1 以下で 200-600m を目安にします。高強度日ほど長めにし、Junior では最後に「今日の良かった動作」を言語化させます。

## 9. Junior の 4 泳法バランス

| 泳法 | 最低頻度 | 目的 |
|---|---|---|
| Free | ほぼ毎回 | 基礎持久力と基準ペース |
| Back | 週 2-3 回 | 姿勢、肩バランス |
| Breast | 週 2 回 | キック可動域、タイミング |
| Fly | 週 1-2 回 | 体幹連動、リズム |
| IM | 週 1 回以上 | 早期専門化回避 |

避けること:

- 毎回 Free だけで距離を稼ぐ。
- 50m が速い選手を早期に Sprint 専門化する。
- 成長痛や膝痛があるのに Breast kick を増やす。
- 技術が崩れた状態で SP3 を繰り返す。

## 10. レーン内ローテーション

- 安定してサイクルを守れる選手を先頭にする。
- Junior は先頭固定を避け、リーダー経験を回す。
- 速度差がある場合は距離差スタートやサイクル差を使う。
- 壁で譲る位置は施設ルールに合わせ、練習前に宣言する。

| 状況 | 調整 |
|---|---|
| レーン詰まり | サイクル +5-10 秒 |
| 先頭だけ余裕 | 先頭に追加 underwater など |
| 後続が遅れる | 本数を減らすか出発間隔を広げる |
| 全員余裕 | 次ラウンドで Descend を追加 |

## 11. 安全停止ルール

以下があれば、その選手の高強度セットを停止します。

- 痛みが増える。
- めまい、吐き気、寒気。
- フォーム崩壊が続く。
- 呼吸が戻らない。
- RPE 10 が連続し、練習意図を超える。

代替:

```text
4×50 easy choice @ 1:20
200 easy swim-down
プールサイドで状態確認
```

## 12. 出力サマリ例

```text
Phase: B (試合まで 10 週)
主ゾーン: EN3 / SP1
Method: Threshold + Descending
骨格パターン: default-aerobic
練習計画: plans/2026-spring-training-plan.md Week 4
安全配慮: athlete-001 は Fly/Paddle 回避
```

## 13. 保存前チェックリスト

- [ ] 参加者数と収容人数を確認した。
- [ ] 交代制の有無と待機側パターンを明記した。
- [ ] Warm-up / Cool-down がある。
- [ ] Phase / Zone / Method の根拠がある。
- [ ] `athlete-conditions.json` の制約を反映した。
- [ ] Junior の 4 泳法バランスを崩していない。
- [ ] TSV 保存前に全件プレビューした。
- [ ] PII を含まない。
