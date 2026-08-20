# Theme Mapping (対話テーマ → 内部パラメータ)

Workflow A の Step 7.5 で使用。schedule / plans が未登録のとき、コーチに 6 択でテーマを聞き、
以下の対応表で Phase / 主 Zone / 推奨 Method 候補を導出する。

## 対応表

| # | Theme | Phase 傾向 (デフォルト) | 主 Zone 配分 | 推奨 Method 候補 |
|---|---|---|---|---|
| ① | **有酸素土台** | Acc / Trans | EN2 45% + EN1 30% + SP1 15% + SP2 10% | threshold / endurance / mixed-stroke aerobic |
| ② | **レース想定** | Real / Peak | SP1 30% + EN2 30% + EN1 20% + SP2 15% + SP3 5% | race-pace / broken-swim / descending / USRPT |
| ③ | **スプリント** | Real / Peak | SP2 35% + SP1 25% + EN1 25% + EN2 15% | sprint / USRPT (25/50 unit) / speed-alactic / short broken |
| ④ | **回復・軽め** | Recovery / Trans2 | EN1 55% + recovery 25% + EN2 15% + technique 5% | recovery / technique / drill-heavy |
| ⑤ | **混合・ミックス** | 任意 (Acc デフォルト) | 均等 (EN1/EN2/SP1 各 25%、SP2 15%、recovery 10%) | 任意組み合わせ (Method 2-3 種類) |
| ⑥ | **自由指定 (自然文)** | 対話パース | 対話パース | 対話パース |

## 自由指定 (⑥) のパース方針

コーチが「今日はスプリントベースで USRPT メインで」のように自然文で答えた場合、以下のキーワードマッピングで解釈:

### Phase キーワード

| キーワード | Phase |
|---|---|
| 準備期 / 準備 / base / 土台 / 骨太 | Acc |
| 強化期 / 強化 / build / 追い込み | Real |
| 仕上げ / peak / test / 試技 | Peak |
| 調整 / taper / 落とす / 軽め (大会前) | Trans |
| 回復 / recovery / off / 軽め (大会後) | Recovery |
| 完全休 / rest / off day | Trans2 |

### Zone キーワード

| キーワード | Zone |
|---|---|
| 有酸素 / aerobic / エアロ | EN1 + EN2 |
| 閾値 / threshold / スレッショルド | EN2 + SP1 |
| レース pace / race pace / RP | SP1 + SP2 |
| スプリント / sprint / 全力 / max effort | SP2 + SP3 |
| ゆるく / easy / low / EN0-1 | recovery + EN1 |

### Method キーワード

| キーワード | Method |
|---|---|
| USRPT / fail-stop / 25 unit / 50 unit | usrpt |
| Broken / 分割 / 100 broken / 200 broken | broken-swim |
| Descending / desc / 下降 | descending |
| Threshold / 閾値 / 中強度 | threshold |
| Endurance / 有酸素 / 継続 | endurance |
| Sprint / 全力 / 短距離 | sprint |
| Kick メイン / キック中心 | kick-focus |
| Pull メイン / プル中心 | pull-focus |
| Drill / 技術 / テクニック | technique / drill-heavy |
| IM / 個メ / 4 種目 | mixed-stroke aerobic |

## 冒頭サマリのフォーマット (由来を必ず明示)

Workflow A の Step 7.5 完了後、以下 1 行を必ず出力:

```
Phase: <phase> (<D±n or 推定>) / Theme: <theme name> (<由来: schedule | plan | 対話選択① | 対話⑥自由指定>) / 主 Zone: <zone(s)> / 総距離目標: <Nm>
```

例:
- `Phase: Acc (D-118) / Theme: Threshold 週 (schedule 由来) / 主 Zone: SP1+EN2 / 総距離目標: 3400m`
- `Phase: Acc (推定) / Theme: 有酸素土台 (対話選択①) / 主 Zone: EN2+EN1 / 総距離目標: 3400m`
- `Phase: Real (推定) / Theme: スプリント + USRPT (対話⑥自由指定) / 主 Zone: SP2+SP1 / 総距離目標: 2800m`

## 「テーマ聞かない」の範囲 (懸念 4 対応)

- **テーマ確定 = Phase + 主 Zone + メイン主眼**の 3 点セットの確定
- **Method 選定 (Step 10) と 骨格 A/B/C (Step 10.5) は常にコーチ対話が残る**
- コーチがテーマ確定後も「Method は自分で選びたい / 骨格 3 案から選びたい」ため、fast-path 全自動化はしない
