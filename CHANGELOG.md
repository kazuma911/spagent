# Changelog

`spagent` の変更履歴。形式は [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/)、バージョニングは [Semantic Versioning](https://semver.org/lang/ja/) に準じます。

## [Unreleased]

- 初回公開に向けた実装作業中

## [0.6.0] - 2026-08-08

### Added

- **メニュー骨格パターン学習**（Workflow G の傾向分析に追加）
  - `knowledge/custom/menu-structure-patterns.json` を新設。ブロック並び順・距離配分比率・総距離帯・有酸素の日 / スピードの日の骨格バリエーションを保存
  - `data/coaching-profiles.json` に `menu_structure_pattern_id` を追加（プロファイル単位で骨格パターンを保持）
- **Workflow A Step 13** にメニュー骨格設計を明示。プロファイルの `menu_structure_pattern_id` があれば読み込みそれに沿って組む、なければデフォルト
- **Workflow G Step 9-10** に骨格パターン抽出・保存を追加

### Changed

- Workflow G Step 10 でプロファイルへの骨格パターン紐付けを明示

## [0.5.0] - 2026-08-07

### Added

- **`references/phase-method-mapping.md`** — Phase × Method 推奨マトリクス
- **`references/pace-estimation.md`** — PB + RPE から現在ペース推定、Zone 目標 % ロジック
- **Workflow A Step 10** に Method 推奨提示と対話選択を明示化（Base + Custom Methods 両方から選択）
- **Custom Methods** 概念を追加 — Workflow G の傾向分析から抽出したコーチ独自パターンを `knowledge/custom/methods/` に保存し、Workflow A の Method 選択候補に追加

### Changed

- 4 層モデルの Methods 層を「メニュー作成時に選択する層」として位置付け明確化（プロファイルには含めず、当日決定）

## [0.4.0] - 2026-08-06

### Added

- **指導プロファイル** 概念を導入（`data/coaching-profiles.json`）
- **グループ / 選手** の多対多関係を整理（`groups.json`, `athletes.json`）
- **Workflow A** をプロファイル判定フローに刷新
- **交代制判定** ロジック（`facilities.usable_lanes × max_swimmers_per_lane`）

### Changed

- Philosophy / Periodizations / Macrocycle をフラット配列から「指導プロファイル」単位へ再構成

## [0.3.0] - 2026-08-05

### Added

- **Workflow G** — 過去メニュー / ドリル取り込み & 傾向分析
- **`scripts/import/`** — Excel / PDF / 画像からの取り込みスクリプト群
- **`scripts/analyze/menu_tendency_analyzer.py`** — 傾向分析補助
- **`knowledge/custom/imports/`** — 取り込み元素材の一時保管

## [0.2.0] - 2026-08-04

### Added

- **4 層トレーニングモデル** を明文化（Periodization × Philosophy × Methods × Macrocycle）
- **`references/training-models/`** ディレクトリ構造を確定
- **`use_base_knowledge`** オプション（all / custom_only / base_only / selective）

## [0.1.0] - 2026-08-03

### Added

- 初版要件定義書 `requirements.md`
- ディレクトリ構造の骨格
- `SKILL.md` フロントマターと役割定義
- PII 保護方針
