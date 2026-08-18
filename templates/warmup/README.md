# W-up テンプレート集

Workflow A の Step 11 (W-up 設計) で使用する再利用可能なテンプレート。

## 使い方

1. Workflow A の Step 11 に到達したら、`applicable_conditions` に合致するテンプレートを候補提示
2. コーチは以下の 5 択から選択:
   - **A: そのまま採用** — `sessions/YYYY-MM-DD/warmup.md` にコピー
   - **B: このセッションだけカスタマイズ** — 対話で行編集 → `sessions/YYYY-MM-DD/warmup.md` に保存 (元テンプレ不変)
   - **C: テンプレ自体を編集** — `templates/warmup/<id>.md` に反映 (次回以降も適用)
   - **D: 叩き台に新規テンプレ作成** — 新 id/name を対話入力 → `templates/warmup/<新id>.md` を新規保存
   - **E: ゼロから新規** — 対話で組立 → 保存時に「テンプレ化する？」を確認
3. B/C/D/E は次を順に対話確認: `セット内容 (行単位)` → `総距離` → `目安時間` → `applicable_conditions (C/D)` → `目的コメント`
4. C/D で保存する時はフロントマターに `updated: YYYY-MM-DD`, `updated_by: coach` を追加

## テンプレは無制限に増やせる

`templates/warmup/` に `.md` を置くだけで自動的に候補入りする。命名は下記規則を守れば「マッチ絞込 → 一覧提示 → 選択」がスムーズになる。

## テンプレート命名規則

`{course}-{purpose}-{total_distance}.md`

- course: `scm` / `lcm` / `any` (両対応)
- purpose: `standard` / `short` / `race-taper` / `recovery` / `junior-4stroke` / `sprint-focus`
- total_distance: おおよその総距離（m）

## ファイル構造

各テンプレートは以下のフロントマターを持つ:

```markdown
---
id: scm-standard-400
name: SCM 標準 400m W-up
course: SCM
duration_min: 8
total_distance: 400
applicable_conditions:
  practice_duration_min: [90, 120, 150]
  phase: [Acc, Trans, Peak]
  gear: [0, -1]
tags: [standard, threshold-day]
---

## セット内容

...

## 目的・意図

...
```

## 現行テンプレート一覧

### SPA 固定 W-up シリーズ (2026-08-06 v4.7 移植・swimassistant §3.3)

「試合週数に応じたドリルルーティン」を Phase A/B/C/D で切替える公式運用。**適用フェーズはグループ内で試合が最も近い選手の週数で全員一律決定** (試合なし選手も同フェーズを踏む)。

| ID | 用途 | 総距離 | 対応時間 | Race weeks out |
|---|---|---:|---|---|
| `spa-fixed-phaseA-1100` | 試合遠い / なし (base building) | 1100 (AP込) | 90-150 min | ≥8 or none |
| `spa-fixed-phaseB-1100` | Acc-Trans 移行期 | 1100 (AP込) | 90-150 min | 4-8 |
| `spa-fixed-phaseC-1100` | Peak 直前 (RP cue 導入) | 1100 (AP込) | 90-150 min | 2-4 |
| `spa-fixed-phaseD-taper` | Taper / Race week (段階圧縮 950→850→700) | 950 (AP軽/省略) | 60-120 min | 0-2 |

### 汎用 W-up

| ID | 用途 | 総距離 | 対応時間 | Phase/Gear |
|---|---|---:|---|---|
| `scm-standard-400` | 汎用 (Threshold/Descending day) | 400 | 90-150 min | Acc/Trans/Peak, gear 0/-1 |
| `scm-short-300` | 90 min 短縮版 | 300 | 90 min | 全 phase |
| `scm-recovery-300` | 疲労回復・軽め日 | 300 | 90-120 min | gear -2/-3 |
| `scm-sprint-400` | Sprint/RP day | 400 | 90-120 min | Trans/Peak |
| `lcm-standard-500` | LCM 標準 | 500 | 120-150 min | Acc/Trans/Peak |
| `lcm-race-taper-300` | LCM レース前 taper | 300 | 60-90 min | Peak |
