# Installation

spagent の詳細セットアップです。
コーチ向けには必要最小限、エンジニア向けには依存関係を明確にします。

## 用語ミニ辞典

| 用語 | コーチ向け説明 | エンジニア向け説明 |
|---|---|---|
| RPE | 主観的運動強度。1 が楽、10 が限界。 | 人間入力の負荷メトリクス。 |
| PB | 自己ベスト。 | ペース推定の基準値。 |
| LCM | 長水路、50m プール。 | `course = LCM`。 |
| SCM | 短水路、25m プール。 | `course = SCM`。 |
| T-pace | 閾値ペース。少しきついが持続できる速度。 | Threshold の基準。 |
| Phase | 大会までの時期区分。 | A/B/C/D の状態。 |
| Zone | EN1 から SP3 などの強度帯。 | 検索・タグ付け軸。 |
| Method | Threshold, Broken などの練習手法。 | Workflow A で当日選ぶ戦術。 |
| Cycle | 出発間隔。 | interval / send-off。 |
| PII | 個人情報 (Personal Identifiable Information)。 | git に入れない保護対象。 |

## Windows

PowerShell と `C:\...` 形式のパスを使います。

```text
python --version / pip --version
```

## macOS

Homebrew や公式 installer の Python を使えます。

```text
python3 --version / pip3 --version
```

## Linux

ディストリビューションのパッケージ管理に従います。

```text
python3 --version / pip3 --version
```

## 仮想環境を推奨する理由

仮想環境は spagent 専用の Python 道具箱です。
コーチ向けには、普段の練習道具と遠征バッグを分けるイメージです。
エンジニア向けには global site-packages を汚さない isolated environment です。

## venv の例

```powershell
cd C:\AIAccelerate\spagent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r scripts\requirements.txt
```

## conda の例

```powershell
conda create -n spagent python=3.10
conda activate spagent
pip install -r scripts\requirements.txt
```

## 必須依存

`pip install -r scripts\requirements.txt` で Pillow のみが入る想定です。

```text
Pillow>=10.0.0
```

## オプション依存

| 機能 | 依存 | コマンド |
|---|---|---|
| PDF 出力 | reportlab | `pip install reportlab` |
| Excel 出力/取り込み | openpyxl | `pip install openpyxl` |
| PDF 取り込み | pdfplumber | `pip install pdfplumber` |

## Copilot CLI

GitHub Copilot CLI の導入は公式ドキュメントを参照してください。
- https://docs.github.com/copilot
- https://cli.github.com/
ここでは深掘りしません。重要なのは Copilot が `SKILL.md` を読めることです。

## SKILL.md の読み込ませ方

Copilot CLI では一般に `/skill` のようなコマンドで Skill を読み込みます。
実際のコマンドは環境差があるため `/help` を確認してください。

```text
/skill C:\AIAccelerate\spagent\SKILL.md
```

## Smoke test

```text
Coach: バージョン確認して。
Skill: requirements.md v0.6.0 と SKILL.md の Workflow A-G を確認しました。
Coach: Workflow A の流れを短く説明して。まだ保存しないで。
Skill: 環境確認、グループ選択、Phase、Zone、Method、骨格、タイム、Cycle、承認後保存です。
```

## トラブル: Python not found

### 解決手順

1. Python 3.10+ をインストールする。
2. PATH を有効にする。
3. `py --version` も試す。

## トラブル: pip permission denied

### 解決手順

1. 仮想環境を使う。
2. 必要なら `pip install --user`。
3. 組織 PC では管理者ポリシーを確認する。

## トラブル: Pillow install fails on Windows

### 解決手順

1. `python -m pip install --upgrade pip`。
2. Python を 3.10+ にする。
3. 必要なら Microsoft C++ Build Tools を相談する。

## インストール 補足チェックリスト

- インストール 確認 1: 保存前にコーチが承認する。
- インストール 確認 2: 実名・施設名・連絡先を入れない。
- インストール 確認 3: LCM/SCM と練習時間を毎回確認する。
- インストール 確認 4: RPE が高い選手には次回負荷を補正する。
- インストール 確認 5: TSV で内容を確認してから PDF/Excel にする。
- インストール 確認 6: 迷ったら安全側に倒す。
- インストール 確認 7: custom はローカル専用として扱う。
- インストール 確認 8: base を直接変えず overrides を使う。
- インストール 確認 9: 保存前にコーチが承認する。
- インストール 確認 10: 実名・施設名・連絡先を入れない。
- インストール 確認 11: LCM/SCM と練習時間を毎回確認する。
- インストール 確認 12: RPE が高い選手には次回負荷を補正する。
- インストール 確認 13: TSV で内容を確認してから PDF/Excel にする。
- インストール 確認 14: 迷ったら安全側に倒す。
- インストール 確認 15: custom はローカル専用として扱う。
- インストール 確認 16: base を直接変えず overrides を使う。
- インストール 確認 17: 保存前にコーチが承認する。
- インストール 確認 18: 実名・施設名・連絡先を入れない。
- インストール 確認 19: LCM/SCM と練習時間を毎回確認する。
- インストール 確認 20: RPE が高い選手には次回負荷を補正する。
- インストール 確認 21: TSV で内容を確認してから PDF/Excel にする。
- インストール 確認 22: 迷ったら安全側に倒す。
- インストール 確認 23: custom はローカル専用として扱う。
- インストール 確認 24: base を直接変えず overrides を使う。
- インストール 確認 25: 保存前にコーチが承認する。
- インストール 確認 26: 実名・施設名・連絡先を入れない。
- インストール 確認 27: LCM/SCM と練習時間を毎回確認する。
- インストール 確認 28: RPE が高い選手には次回負荷を補正する。
- インストール 確認 29: TSV で内容を確認してから PDF/Excel にする。
- インストール 確認 30: 迷ったら安全側に倒す。
- インストール 確認 31: custom はローカル専用として扱う。
- インストール 確認 32: base を直接変えず overrides を使う。
- インストール 確認 33: 保存前にコーチが承認する。
- インストール 確認 34: 実名・施設名・連絡先を入れない。
- インストール 確認 35: LCM/SCM と練習時間を毎回確認する。
- インストール 確認 36: RPE が高い選手には次回負荷を補正する。
