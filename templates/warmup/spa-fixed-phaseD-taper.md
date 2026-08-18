---
id: spa-fixed-phaseD-taper
name: SPA 固定W-up Phase D (試合 0-2週 テーパー) 900/800/700m
course: SCM, LCM
duration_min: 16
total_distance: 950
applicable_conditions:
  practice_duration_min: [60, 90, 120]
  phase: [Peak, Taper]
  gear: [-1, -2]
  race_weeks_out: "0-2"
tags: [固定アップ, phase-D, spa, taper, race-week, compressed]
source: swimassistant/references/menu-rules.md §3.3 (v4.7, 2026-08-06)
imported: 2026-08-10
---

## セット内容 (Taper 段階圧縮)

### 標準 Phase D (試合まで 1-2 週, 950m)

```
[1] Swim  1×400 @8'   — Choice / Easy (Z1, DPS 一定)
[2] Drill 4×50 @1'30" — Phase D ルーティン:
      Scull fast / SA 2-beat R / Dolphin Crawl fast / Swim w/ RP cues
[3] Swim  6×50 @50"   — IM-mix: Fly / Fr / Ba / Fr / Br / Fr (moderate)
[4] AP    1×50 @2'    — 腹圧軽め (v1=buoy 片手キック のみ、v2 は疲労させないため省略)
[5] Rest  1'
```
**総距離**: 950m / **目安時間**: 17 min

### Race week (試合 3-7 日前, 850m)

```
[1] Swim  1×400 @8'   — Choice / Easy
[2] Drill 3×50 @1'30" — Scull fast / SA 2-beat R / Swim w/ RP cues
[3] Swim  5×50 @50"   — IM-mix (Fly 除外可): Fr / Ba / Fr / Br / Fr
[4] AP    1×50 @2'    — 腹圧軽め (v1 のみ、体感確認レベル)
[5] Rest  1'
```
**総距離**: 850m / **目安時間**: 15 min

### Race day / Race eve (試合 0-2 日前, 700m)

```
[1] Swim  1×300 @6'   — Choice / Easy
[2] Drill 2×50 @1'30" — Scull fast / Swim w/ RP cues
[3] Swim  4×50 @50"   — Fr のみ moderate (神経系起こし)
[4] AP    ★省略        — Race day は神経系温存優先
[5] Rest  1'
```
**総距離**: 700m / **目安時間**: 12 min

## 目的・意図

- Taper 期 = 疲労を残さず神経系起動
- 距離を段階圧縮 (900 → 800 → 700)
- RP cue 系を残し、race pace 感覚を neuro で維持

## Phase D ドリル解説

- **Scull fast**: 最高 tempo でキャッチ位置固定
- **SA 2-beat R** (省略可 in race week): 片側リズム最終確認
- **Dolphin Crawl fast**: 推進タイミング fast (レース前神経系起こし)
- **Swim w/ RP cues**: race pace SR で 25-50 上げ

## 適用場面

- 試合まで 0-2 週
- Race week (D-3 ~ D-7)
- Race day / Race eve

## AP 腹圧統合 (§3.4) ★段階別に組込済

上記各 taper 段階の [4] に統合済み:
- 1-2 週前: 50m v1 のみ
- Race week: 50m v1 (体感確認)
- Race day / eve: 省略 (神経系温存)

## 非推奨

- 試合 2 週以上 → `spa-fixed-phaseC-1000` を使う
- 通常練習 (試合遠い) → `spa-fixed-phaseA/B-1000` を使う
