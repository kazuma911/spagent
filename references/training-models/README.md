# Training Models Overview

spagent のトレーニングモデルは **Periodization × Philosophy × Methods × Macrocycle** の 4 層です。コーチの「分身」が、対象者・大会までの時間・当日の手法・年間骨格を一貫して選ぶための共通語です。

## 1. 4-layer system

| Layer | 役割 | 選択肢 |
|---|---|---|
| Periodization | いつ何を鍛えるか | Matveyev / Block / Undulating / Reverse |
| Philosophy | 誰向けに何を優先するか | Masters / Junior / Elite / Triathlon |
| Methods | 具体的にどう鍛えるか | USRPT / HIIT / LSD / Broken / Threshold / Fartlek / Descending |
| Macrocycle Templates | 週次・年次の骨格 | Single Peak / Four Peaks / Junior Annual / Triathlon / Maintenance |

## 2. How they combine

例: `Masters × Block+Undulating × Single Peak 12week` では、社会人の回復力を考慮しながら 2-4 週単位で主能力を作り、週内は強度を波状にします。Method は固定せず、Workflow A で Phase / Zone / 体調に応じて選びます。

## 3. data/coaching-profiles.json

`data/coaching-profiles.json` はグループごとの既定モデルを保持します。

```json
{
  "id": "group-001-profile",
  "philosophy": "masters",
  "periodizations": ["block", "undulating"],
  "macrocycle": "single-peak-12week",
  "preferred_methods": ["threshold", "descending"]
}
```

## 4. Periodization

- [Matveyev](periodization/matveyev.md)
- [Block](periodization/block.md)
- [Undulating](periodization/undulating.md)
- [Reverse](periodization/reverse.md)

## 5. Philosophy

- [Masters](philosophy/masters.md)
- [Junior](philosophy/junior.md)
- [Elite](philosophy/elite.md)
- [Triathlon](philosophy/triathlon.md)

## 6. Methods

- [USRPT](methods/usrpt.md)
- [HIIT](methods/hiit.md)
- [LSD](methods/lsd.md)
- [Broken Swim](methods/broken-swim.md)
- [Threshold](methods/threshold.md)
- [Fartlek](methods/fartlek.md)
- [Descending](methods/descending.md)

## 7. Macrocycle Templates

- [Single Peak 12week](macrocycle-templates/single-peak-12week.md)
- [Four Peaks Annual](macrocycle-templates/four-peaks-annual.md)
- [Junior Annual](macrocycle-templates/junior-annual.md)
- [Triathlon Integrated](macrocycle-templates/triathlon-integrated.md)
- [Maintenance Phase](macrocycle-templates/maintenance-phase.md)

## 8. 選択目安

| 状況 | 推奨 |
|---|---|
| 年 1 回の大目標 | Single Peak + Matveyev/Block |
| 年複数回レース | Four Peaks + Block |
| 週 2-3 回 | Undulating + Masters |
| U15 育成 | Junior + Junior Annual |
| 50m Sprint | Reverse + USRPT/Broken |
| トライアスロン | Triathlon Integrated + Threshold/LSD |
