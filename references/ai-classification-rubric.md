# AI Classification Rubric (取り込み時 canonical 判定基準)

この文書は **Workflow G Step 7.5** で LLM が個々のメニュー / ドリルを分類する際の一次情報です。ここに書かれたルールは canonical であり、`scripts/classify/classify_menus.py`（キーワード tagger）はこれのフォールバックに徹します。

関連: [phase-method-mapping.md](phase-method-mapping.md) / [zone-phase-mapping.md](zone-phase-mapping.md) / [menu-design.md](menu-design.md)

---

## 0. なぜ必要か（背景）

キーワードベースの Script tagger は次の限界を持ちます:

1. **意図の読み取り不可**: メニュー名が「recovery」でも中身が高強度の場合を検出できない
2. **多信号 fusion 不可**: date × zone × method × structure を統合判断できない
3. **event 特化推定不可**: 距離だけでは 200Fr 中心か IM 中心か区別不能
4. **命名と実体のズレ検出不可**: `endurance` シートに Descending + Race Pace が入っている等
5. **サブグループ抽出不可**: 「A: athlete-a / B: athlete-i」の並列指示を認識できない

これらは LLM が本文を読んで判定する必要があります。ルーブリックがなければ判定は "勘" になり再現性が下がるため、本文書で**判定基準を明文化**します。

---

## 1. 出力スキーマ（canonical）

1 メニュー = 1 レコードで以下を出力します。`menu-index.json` の `entries[]` に取り込まれます。

```json
{
  "id": "<method>-<hash>",
  "source": "<file_path_or_url>#<sheet_or_page>",
  "date": "YYYY-MM-DD",

  "main_menu": {
    "structure_summary": "自然文で 1-2 行",
    "total_distance": 3200,
    "main_distance": 1800,
    "duration_est_min": 75,
    "course": "SCM | LCM"
  },

  "method": {
    "primary": "threshold | descending | broken | usrpt | hiit | lsd | fartlek | <custom_slug>",
    "secondary": ["broken"],
    "canonical_match": ["Threshold Training", "Descending Sets"],
    "confidence": "high | medium | low",
    "evidence": "本文の何を根拠にこの method と判定したかを 1-2 行"
  },

  "phase": {
    "primary": "A | B | C | D | REC",
    "secondary": ["C"],
    "signals": {
      "date_d_minus_n": -21,
      "date_nearest_comp": "2026-08-08 tokyo-shakaijin",
      "date_derived_phase": "C",
      "method_derived_phase": "B",
      "zone_derived_phase": "B"
    },
    "confidence": "high | medium | low",
    "evidence": "3 シグナルが一致 / 乖離あり (2/3) 等の説明を 1-2 行"
  },

  "zone_tags": ["EN2", "EN3", "SP1"],

  "target": {
    "philosophy": "masters | junior | elite | triathlon",
    "event_focus": ["200Fr", "400Fr"],
    "level": "beginner | intermediate | intermediate-advanced | elite",
    "group_type": "single | mixed-ability | sprinter-only | distance-only",
    "sub_groups": [
      { "id": "A", "athletes_hint": "200Fr build", "distance": 1800, "focus": "Threshold" }
    ],
    "evidence": "対象判定の根拠 1 行"
  },

  "theme_interpretation": "元テーマ文の意図を 1 行で言い直したもの",

  "coach_review_needed": false,
  "review_reasons": [],

  "judged_by": "spagent-classify-v1",
  "judged_at": "YYYY-MM-DDTHH:MM:SS+09:00"
}
```

### 1.1 必須フィールド

`id`, `source`, `main_menu.total_distance`, `method.primary`, `method.confidence`, `phase.primary`, `phase.confidence`, `zone_tags`, `judged_by`, `judged_at`

### 1.2 追加フィールド（既存 `menu-index.json` との後方互換）

既存の `count`, `example_dates`, `themes_top`, `md_path`, `fingerprint`, `main_avg`, `main_range` は保持。上記スキーマは "1 セッション判定" で、パターンクラスタ側（`menu-index.json`）は複数セッションの集約なので、下記のマージルールに従います。

---

## 2. Method 判定ルール

### 2.1 Base 7 手法の識別シグナル

| Method | 主要シグナル | 補助シグナル |
|---|---|---|
| **LSD** | Main が uniform low-intensity, 距離 800m+ 継続, cycle 緩め | "aerobic", "EN1/EN2", "distance swim" |
| **Threshold** | Main が T-pace / EN3 hold, 100-400m × N @ tight cycle | "T-pace", "T30", "CSS", "閾値", "EN3" |
| **Descending** | 各本徐々に上げる指示 (`best+14 -> +10`, `3'->2'50"->2'40"`) | "descend", "build", "negative split" |
| **Broken** | 目標距離を分割 (200 = 4×50 R:10) して race pace 再現 | "broken", "race pace ±", "分割" |
| **USRPT** | 25/50m を Race Pace で反復 + Missed repeats ルール | "USRPT", "race pace hold", "miss out" |
| **HIIT** | 短時間高強度 (30s-3min) の反復, VO2max / MSS 系 | "VO2max", "MSS", "max aerobic", "HIIT" |
| **Fartlek** | 速い / 遅いの自由切替, 目的距離が可変 | "fartlek", "change of pace", "変化泳" |

### 2.2 判定手順

```
1. Main セット行を抽出 (WU/CD/Drill/Kick を除外)
2. 各 Main 行を 2.1 のシグナルで採点
3. 最高スコアの method を primary、次点を secondary (差 < 30% なら)
4. 該当スコア 0 の場合 → "mixed" or Custom Method 候補
5. Custom Method 候補は knowledge/custom/methods/*.md のフロントマターと照合
```

### 2.3 method 名 → 内容ミスマッチ検出

**取り込み元の method 名（シート名 / ファイル名）と Main 内容が一致しない場合、必ず `coach_review_needed = true`**。

例:
- ファイル名 `recovery-*` だが Main に `All Out` / `Descending best` を含む → mismatch
- ファイル名 `endurance-*` だが zone 配分の 50% 超が SP1-SP3 → mismatch
- ファイル名 `threshold-*` だが Main が全て 25/50m → USRPT 候補

**Sample 2 (`recovery-19fca077`), Sample 4 (`endurance-24498576`) の誤分類はこのルールで検出されます。**

### 2.4 Custom Method 候補の提案

Base 7 手法いずれの primary スコアも `medium` 未満なら:

```json
"method": {
  "primary": "custom_candidate",
  "custom_candidate_name_suggestion": "block-acc-en3-race-pace",
  "custom_candidate_source_dates": ["2026-06-29", "2026-07-14", "2026-07-18"],
  "confidence": "low"
}
```

Workflow G Step 11 でコーチ承認後、`knowledge/custom/methods/<slug>.md` に格納。

---

## 3. Phase 判定ルール

### 3.1 3 シグナル fusion

Phase は **date / method / zone の 3 シグナル**を融合して判定します。

#### Signal a: date × competitions.json → D-n

```
1. session.date と data/competitions.json の priority=A 大会を突合
2. 最も近い未来の大会を選択 (or 完了直後の大会)
3. D-n = (comp.start_date - session.date).days
```

| D-n の範囲 | Phase (default) |
|---|---|
| D-84 以上 (12週以上前) | A |
| D-42 〜 D-83 (6-12週前) | B |
| D-15 〜 D-41 (2-6週前) | C |
| D-1 〜 D-14 (2週以内) | D |
| D+1 〜 D+7 (試合直後) | REC |
| D+8 以上でも次 A 大会が D-84 以上 | A (基礎期再開) |
| priority=A 大会が近未来にない | A (offseason 扱い) |

#### Signal b: method-derived phase

canonical マトリクス（`phase-method-mapping.md §2`）から:

| Method | 推奨 Phase (⭐) |
|---|---|
| LSD | A, REC |
| Threshold | B |
| Descending | B, C |
| Broken | C, D |
| HIIT | C |
| USRPT | C, D |
| Fartlek | REC |

Custom Method は `knowledge/custom/methods/<slug>.md` フロントマターの `適用 Phase` を参照。

#### Signal c: zone-derived phase

`zone_tags` の主要 zone から `zone-phase-mapping.md §1` の逆引き:

| 主要 Zone (>= 40% 距離) | Phase |
|---|---|
| EN1 / EN2 | A |
| EN3 | B |
| SP1 | B or C |
| SP2 | C |
| SP3 | C or D |
| EN1 のみ (70%+) | REC |

### 3.2 融合ロジック

```
1. Signal a, b, c を計算
2. 3 つが一致 → confidence = high
3. 2 つが一致 → primary = 一致した Phase、secondary = 残り 1 つ、confidence = medium
4. 3 つが全部異なる → primary = Signal a（実施日ベース最優先）、confidence = low
5. Signal a が取れない（大会情報なし）→ Signal b/c のみで判定、confidence を 1 段下げる
```

### 3.3 Phase 判定の例（実サンプルより）

| Menu | Signal a | Signal b | Signal c | Final | Confidence |
|---|---|---|---|---|---|
| `sprint-2c1434c8` (2026-06-13, 松山 D-7) | **D** | D (broken+usrpt) | D (SP2/SP3) | D | **high** (3/3 一致) |
| `threshold-fdb30961` (2026-07-14, 東京社会人 D-25) | C | **B** (threshold) | B (EN3 主) | B, secondary=C | medium (2/3) |
| `race-pace-0415f41a` (2026-04-15, 松山 D-66) | B | **C** (usrpt) | C (SP2/SP3) | C, secondary=B | medium (2/3) |

---

## 4. Target 判定ルール

### 4.1 Philosophy

| Philosophy | 判定シグナル |
|---|---|
| **masters** | RPE 記述、休息比 20%+、Team 分割、成人選手名 alias |
| **junior** | Drill 量 30%+、4 泳法必修、フォーム停止条件、身長基準の distance |
| **elite** | 乳酸値 / 動画注記、cycle が厳格、Missed repeats ルール |
| **triathlon** | EN2 40%+、Bike/Run 疲労言及、pull-heavy |

判定に迷う場合は `masters` を default（spagent の主要ターゲット）。

### 4.2 Event Focus

Main の距離帯から:

| Main 距離帯 | Event Focus |
|---|---|
| 25/50m 中心 | 50Fr, 50-stroke |
| 100m 中心 | 100Fr, 100-stroke |
| 200m 中心 | 200Fr, 200IM |
| 400m 以上 | 400Fr, 800Fr, 1500Fr |
| 100 + 200 混合 | 100Fr + 200Fr (mid-distance) |
| IM 明記 | 200IM, 400IM |

複数該当時は `event_focus[]` に全部並記。

### 4.3 Sub-groups

Main セットに `(A)` / `(B)` / `Team A` / `Team B` / 選手 alias（athlete-a、athlete-b等）が並列指示されていたら `sub_groups[]` を抽出:

```json
"sub_groups": [
  { "id": "A", "athletes_hint": "athlete-a/athlete-b", "distance": 800, "focus": "200Fr Broken" },
  { "id": "B", "athletes_hint": "athlete-i", "distance": 400, "focus": "100Fr Broken" },
  { "id": "C", "athletes_hint": "たい", "distance": 300, "focus": "50Fr Max Sprint" }
]
```

---

## 5. Confidence & Review Flagging

### 5.1 confidence 定義

| Level | 条件 |
|---|---|
| **high** | 3 シグナル一致、method / phase / target すべて明快 |
| **medium** | 2/3 シグナル一致、method-content ミスマッチなし |
| **low** | 1/3 一致 / method-content ミスマッチ検出 / 情報欠損 |

### 5.2 coach_review_needed = true にする条件

以下のいずれかで自動的に true にセット:

- **method.confidence または phase.confidence が `low`**
- **method-content ミスマッチ検出**（§2.3）
- **Signal a が取れなかった**（`competitions.json` に近隣 comp がない）
- **Custom Method 候補**として判定した
- **zone_tags と method-derived phase が矛盾**（例: threshold なのに zone_tags=SP3 100%）

### 5.3 review_reasons への理由記述

```json
"review_reasons": [
  "method-content mismatch: file name says 'recovery' but Main has 2x100 All Out",
  "phase signals disagree (a=B, b=C, c=A)"
]
```

コーチが確認しやすいよう 1 reason = 1 文。

---

## 6. Zone Tags の canonical 語彙統一

**取り込み時点で必ず `EN1 / EN2 / EN3 / SP1 / SP2 / SP3` に統一**。以下の旧語彙が入力に含まれていたら変換:

| 旧語彙 (Script tagger 出力) | 統一先 |
|---|---|
| `RECOVERY` | EN1 |
| `AEROBIC` | EN2 |
| `RACE_PACE` | SP2 (100RP), SP3 (50RP) |
| `USRPT` | SP2 or SP3（距離で判定） |
| `BROKEN` | SP2 |
| `SPRINT` | SP3 |
| `VO2MAX` | SP1 |
| `MSS` | SP1 |
| `RP` | SP2 or SP3 |

**method_tags[]** フィールドを別に持つ（USRPT / BROKEN / RACE_PACE / DESCENDING 等）と、zone と method を分離できます。

---

## 7. 判定パス例（Sample 2: `recovery-19fca077` の再判定）

```
入力:
  file_name: recovery-19fca077-recovery.md
  method_hint: recovery
  main_set:
    - 300 easy Fr+Ba
    - 200 IM
    - 5x100 kick 15m u/w
    - 3x100 build up/down @60% effort
    - 2x100 All Out
    - 6x100 keep + descend last 2
    - Team A 6x100 @1'20"
    - Team B 2x100 @1'20"
    - 300 choice

Step 1. Method 判定:
  - "All Out" 2x100 + "descend" 6x100 + "Team A/B" 分割
  - LSD シグナル(0), Threshold(0), Descending(2), Broken(0), USRPT(0), HIIT(0), Fartlek(0)
  - method.primary = "descending"
  - method.secondary = []
  - method_content_mismatch = true (file says recovery, content says descending)
  - method.confidence = low

Step 2. Phase 判定:
  - date 2025-01-08 → data/competitions.json に近隣 A 大会なし (offseason)
  - Signal a = A (default offseason)
  - Signal b = B/C (descending 由来)
  - Signal c = B (mixed EN2-EN3-SP2)
  - 3 シグナル不一致 → primary = A (Signal a 優先), secondary = [B]
  - phase.confidence = low

Step 3. Target 判定:
  - Team A/B 分割 → mixed-ability group
  - 総距離 3600m + descend → intermediate-advanced
  - philosophy = masters (default)
  - event_focus = ["100Fr", "200IM"]

Step 4. Review flag:
  - method_content_mismatch → coach_review_needed = true
  - confidence low → coach_review_needed = true
  - review_reasons:
    - "File name says 'recovery' but Main contains 2x100 All Out and 6x100 descend"
    - "Phase signals disagree: date=A (offseason), method=B/C, zone=B"
```

これを Sample 2 の元の Script 判定（method=recovery, phase=A, coach_review=false）と比較すると、AI 判定は **method mismatch を明示検出**して**コーチレビューに回している**点が決定的に優れています。

---

## 8. Workflow G との統合

Workflow G の Step 7 と Step 8 の間に **Step 7.5 「AI 分類判定」** を挿入します。詳細は `SKILL.md` Workflow G を参照。

```
Step 7. 修正反復 (parsed JSON 確定)
   ↓
Step 7.5. AI 分類判定 ← このルーブリックに従って LLM が判定
   ↓ 出力: parsed_records[].classification (上記スキーマ)
   ↓
Step 8. 承認 & 保存
   - coach_review_needed=false → 自動採用 → menu-index.json 追記
   - coach_review_needed=true → コーチに提示 → 修正 → 追記
```

**スクリプト `classify_menus.py` は Step 7.5 のフォールバック**（LLM が使えない環境や大量バッチの前処理）に格下げします。

---

## 9. バージョン管理

- `judged_by` フィールドに `spagent-classify-v1` を記録
- 本ルーブリック改訂時は `judged_by` を `v2` に上げ、既存判定は再判定候補にする
- 再判定は `scripts/classify/ai_classify_apply.py --rejudge --version v2` で一括実行想定
