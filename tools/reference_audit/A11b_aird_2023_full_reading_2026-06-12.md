# A11b: Aird, Barthelmie & Pryor (2023) 全頁主張駆動精読結果

**実施日**: 2026-06-12
**目的**: A11b 候補論文 Aird 2023 の精読・Paper 1/3 への引用候補確定
**取得経路**: himinさん 配置（`docs/energies-16-02820.pdf` + `energies-16-02820.xml`）。PDF 版で精読

---

## 1. 書誌情報

| 項目 | 内容 |
|---|---|
| Title | Automated Quantification of Wind Turbine Blade Leading Edge Erosion from Field Images |
| Authors | Jeanie A. Aird, Rebecca J. Barthelmie, Sara C. Pryor |
| Affiliation | Sibley School of Mechanical and Aerospace Engineering (Cornell), Department of Earth and Atmospheric Sciences (Cornell) |
| Journal | Energies 16, 2820 (2023) |
| DOI | 10.3390/en16062820 |
| License | CC-BY 4.0 |
| Editor | **Davide Astolfi**（Heo & Na 2025 と同じ Editor） |
| Received | 24 February 2023 |
| Accepted | 14 March 2023 |
| Published | 17 March 2023 |
| Pages | 23 頁 |
| ファイル配置 | `docs/energies-16-02820.pdf`（4.35 MB）/ `docs/energies-16-02820.xml`（183 KB） |
| 助成 | US DOE (Sandia subcontract, DE-SC0016438), NSF GRFP (DGE-1650441), NSF XSEDE |
| Data Availability | "**image sets used in this research are confidential and cannot be provided**" |

---

## 2. 論文構成

| 章 | 内容 |
|---|---|
| §1 Introduction | LEE 普遍性、AEP loss 数値、CFD 研究、4 種類の damage 紹介 |
| §2 Methodology | §2.1 Field images description、§2.2 Workflow（image preprocessing + blade area quantification + CNN/PTS）、§2.3 PTS unsupervised method、§2.4 CNN supervised method |
| §3 Results | §3.1 Blade area quantification、§3.2 illustrative examples、§3.3 damage quantification、§3.4 damage classification |
| §4 Discussion and Conclusions | 両モデル成果、shallow detection の困難、将来研究 |

---

## 3. 主要数値・主張

### 3.1 LEE 関連の数値（§1 Introduction）

- **AEP losses 2-3.7%**（NREL 5MW CFD, [14] Schramm 2017）
- **AEP losses 9% (severe damage, delamination)** ([15] Papi 2020)
- **40% reduction in lift/drag coefficients** due to LEE (18% airfoil, [17] Gaudern 2014)
- **Blade replacement cost > $200,000/blade** for severe damage ([34][35])
- LEP tapes themselves cause **AEP losses 2-3%** ([36] Major 2021)
- Erosion-safe mode operation: tip speed reduction extends LE life ([37] Bech 2017, 既に Mishnaevsky 経由で発見)

### 3.2 Dataset

**140 field images** of wind turbines:
- Central US wind farm, **3-year period**
- Turbines: **8-10 years old**
- **1.6 MW** rated capacity, **77 m** rotor diameter
- Images taken by technicians **using rope access**
- Train / Validation / Test: 80 / 30 / 30
- **2300 shallow damage + 1200 deep damage instances**

**4 LEE 分類** (§2):
- **Pitting (shallow)**: intermittent perforations, circular cavities
- **Marring (shallow)**: surface-level scratches
- **Gouges (deep)**: deep cavities exposing underlying material
- **Delamination (deep)**: removal of outer laminate

これらは 2 グループに集約: **Shallow** (Pits, Marring) / **Deep** (Gouges, Delamination)

### 3.3 評価結果（Table 5）

| Task | PTS (Unsupervised) | CNN (Supervised, Mean) | CNN Best | CNN Worst |
|---|---|---|---|---|
| Blade Area Quantification | **93.7%** | - | - | - |
| Damage Quantification | 63.9% | 61.4% [58.1-65.9] | CNN_RC: 65.9% | CNN_UC: 58.1% |
| Deep Damage Classification | 62.1% | 68.3% [65.5-72.5] | CNN_RC: 72.5% | CNN_UC: 65.5% |
| Shallow Damage Classification | 6.6% | 26.1% [24.5-28.5] | CNN_UBW: 28.5% | CNN_RC: 24.5% |

#### CNN 4 configurations
| Notation | Rotation | Color |
|---|---|---|
| CNN_RBW | Rotated | Black & White |
| CNN_RC | Rotated | Color |
| CNN_UBW | Unrotated | Black & White |
| CNN_UC | Unrotated | Color |

**Mask R-CNN training**: LR = 0.001, Batch Size = 2, **Epochs = 225**

### 3.4 重要な観察

1. **両モデルとも total damage area の ~65% を識別**
2. **両モデルとも deep damage の方が shallow damage より識別容易**
3. **CNN は shallow damage で PTS を大幅に上回る**（26% vs 6.6%）
4. **PTS は false positive 低い** (99.5-99.9% true negative)
5. **Blade orientation を統一すると CNN の damage 検出精度向上**
6. **Black/white と color の変換は damage detection 性能にほぼ影響しない**
7. **Image quality (解像度) が高いと MSE 低下**

---

## 4. Paper 1/3 との関係性評価

### 4.1 Paper 1 との比較

| 項目 | Aird 2023 | Paper 1 (himinさん) |
|---|---|---|
| アーキテクチャ | Mask R-CNN (two-stage) + FPN | YOLOv8n (single-stage) + pyramid patch augmentation |
| Damage 分類 | 4 種類 → 2 種類（shallow/deep） | 5 種類（LE;ER, VG;MT, LR;DA, LE;CR, SF;PO） |
| Dataset | 140 field images, **confidential** | 559 images, **DTU public dataset** |
| 評価指標 | % TP per image (pixel-level) | mAP@0.5 (bbox-level) |
| 出力 | binary damage masks + classification | bbox + class + risk scoring |
| 主目的 | **automated quantification** | **detection + region-wise risk scoring** |

→ **直接比較不可**（評価指標とタスク粒度が異なる）。両者は **補完的**

### 4.2 Paper 3 との比較

- Aird 2023 は完全に画像処理ベースの研究で、**SCADA や気象データとの統合は扱っていない**
- Paper 3 の 3-modality fusion とは別の方向性

---

## 5. Paper 1/3 への引用候補

### 5.1 Paper 1 への引用候補（2 件、優先度中）

#### P1-A-A: §2.1 Related Work（先行研究の厚み追加）

**引用箇所**: Paper 1 §2.1（line 52 周辺、Shihavuddin / Gohar の段落）

**引用案**:
> "Recent work has extended detection to areal quantification: Aird et al. (2023) [19] compared supervised (Mask R-CNN) and unsupervised (pixel intensity thresholding + shadow ratio) methods on 140 field images from a US central-plains wind farm, classifying damage into shallow (pitting, marring) and deep (gouges, delamination) categories, with both methods identifying approximately 65% of total damage area."

**根拠**: §3 Results、Table 5、§4 Discussion

**効果**: Paper 1 §2.1 の field-image LEE detection 研究群に最新の自動定量化研究を加える（任意・優先度中）

#### P1-A-B: §5.4 Comparison with Prior Work（評価指標差異の注記）

**引用箇所**: Paper 1 §5.4 末尾

**引用案**:
> "Direct comparison with quantification-focused works is constrained by evaluation differences: Aird et al. (2023) [19] reported pixel-level identification accuracies of 61-66% for total damage and 65-73% for deep damage using Mask R-CNN on confidential field images, but these are not directly comparable to bounding-box mAP metrics employed here."

**根拠**: Table 5

**効果**: 評価指標の差異を明確にしつつ、関連研究の認知度を高める（任意・優先度中-低）

### 5.2 Paper 3 への引用候補

**結論**: Paper 3 への直接の引用候補は無し（SCADA・気象データ統合を扱っていないため）

ただし、Paper 3 §2.1 の "画像" 段落で他のレビュー（Gohar 2025 など）と並列に追加引用するなら可能だが、必須ではない。

---

## 6. 副次発見（Aird 2023 経由で発見）

| Ref # | 論文 | 用途 |
|---|---|---|
| [6] | **Pryor et al. 2022** "Atmospheric Drivers of WT Blade LE Erosion: Review and Recommendations" Energies 15, 8553 | **Paper 3 の気象データ統合の根拠として最有力候補**（A11c として検討） |
| [7] | Mishnaevsky 2021 (既に [17]/[26] として追加済) | - |
| [9] | **Mishnaevsky 2020** "LEE: Influence of technology aspects" Wind Energy 23, 2247-2255 | 未引用、任意 |
| [16] | **Papi et al. 2020** "Uncertainty quantification of blade damage on AEP" Energies 13, 3785 | Paper 2 / Paper 3 の不確実性論述強化 |
| [25] | Pryor et al. 2023 "Evaluation of WRF simulation of deep convection in US Southern Great Plains" J. Appl. Meteorol. Climatol. | 気象データの根拠 |
| [26] | **Letson et al. 2020** "Radar-derived precipitation climatology for WT blade LEE" Wind Energy Sci. 5, 331-347 | 既に Mishnaevsky 2021 経由で発見、Paper 3 に有用 |
| [52] | **Maniaci, MacDonald, Paquette, Clarke 2022** "Leading Edge Erosion Classification System" IEA Wind Task 46（DTU Technical Report） | **重要**：LEE 業界標準。Paper 1 の damage 分類との対応に利用可能（A11d として検討） |

特に **Pryor 2022** と **Maniaci 2022 IEA Wind Task 46** が次に取得・精読すべき候補。

---

## 7. Claude Code 推定優先度

| 引用候補 | 推定優先度 | 理由 |
|---|---|---|
| P1-A-A（§2.1 先行研究の厚み）| 🟡 中 | 関連研究として有用だが必須ではない。評価指標が異なる |
| P1-A-B（§5.4 評価指標差異注記）| 🟢 中-低 | 査読対策として有効だが、混乱を招くリスクもある |
| Paper 3 への引用 | 🟢 不要 | Aird 2023 は SCADA や気象データを扱っていない |

**結論**: Aird 2023 は **Paper 1 の関連研究厚み補強** には有用だが、Mishnaevsky 2021 / Law 2020 のような「決定的に追加すべき」引用ではありません。**himinさん の判断に委ねる**のが妥当。

---

## 8. Mishnaevsky 2021 / Law 2020 との比較

| 項目 | Mishnaevsky 2021 | Law 2020 | Aird 2023 |
|---|---|---|---|
| 性質 | DTU の包括レビュー | UK 18 wind farms 実機調査 | Cornell ML 比較研究 |
| LEE 普遍性 | Anholt 2016 補修 | 87%/50% (EDP 14年) | 140 images（confidential） |
| AEP loss | 1.5-7% レビュー | 1.75-4.93% 実測 | レビュー数値のみ（2-9%） |
| 経済影響 | €56-75M/year 欧州 | £76.5M UK (2019) | $200K/blade 補修コストのみ |
| Paper 1 引用優先度 | 🔴 高（決定的） | 🔴 高（決定的） | 🟡 中（任意） |
| Paper 3 引用優先度 | 🔴 高（決定的） | 🔴 高（決定的） | 🟢 不要 |

---

## 9. 推奨される追加取得・精読候補（Aird 2023 経由）

1. **Pryor et al. 2022** "Atmospheric Drivers of WT Blade LEE: Review and Recommendations" Energies 15, 8553 → Paper 3 §1 / §2 の気象データ統合の決定的根拠として有力
2. **Maniaci 2022 IEA Wind Task 46** "Leading Edge Erosion Classification System" → Paper 1 の damage クラス分類の業界標準として有力
3. **Letson 2020** "Radar-derived precipitation climatology for WT blade LEE" Wind Energy Sci. → Paper 3 §2 気象データ統合の先行例

これらは himinさん の優先度判断次第。

---

## 10. 関連メモ

- `tools/reference_audit/A9_mishnaevsky_2021_full_reading_2026-06-11.md` — Mishnaevsky 2021 精読
- `tools/reference_audit/A11a_law_koutsos_2020_full_reading_2026-06-12.md` — Law 2020 精読
- `tools/reference_audit/batch10_round2B_part1_progress_2026-04-29.md` — Vera-Tudela 2017 / Heo & Na 2025
- `memory/project_blade_paper_audit_progress.md` — 監査全体の進捗

---

## 11. 次のステップ

1. ✅ Aird 2023 全頁精読 + ドキュメント化（本ファイル）
2. ⏸ himinさん による Aird 2023 引用採否判断（Paper 1 §2.1 / §5.4 の P1-A-A / P1-A-B）
3. ⏸ Aird 2023 PDF/XML を `docs/` から `open_access/` に整理移動
4. ⏸ Pryor 2022 / Maniaci 2022 / Letson 2020 の取得検討
5. ⏸ memory 更新
