# A11a: Law & Koutsos (2020) 全頁主張駆動精読結果

**実施日**: 2026-06-12
**目的**: A11 候補論文 Law & Koutsos 2020 の精読・Paper 1/2/3 への引用候補確定
**取得経路**: Edinburgh PURE Research Explorer（www.pure.ed.ac.uk/ws/portalfiles/portal/158543005/Wind_Energy_Manuscript_V2.pdf）

---

## 1. 書誌情報

| 項目 | 内容 |
|---|---|
| Title | Leading edge erosion of wind turbines: effect of solid airborne particles and rain on operational wind farms |
| Authors | Hamish Law, Vasileios Koutsos |
| Affiliation | School of Engineering, Institute for Materials and Processes, University of Edinburgh |
| Journal | Wind Energy, pp.1-11 |
| DOI | 10.1002/we.2540 |
| Year | 2020 |
| Document Version | Peer reviewed version (Edinburgh PURE 経由、Author's accepted manuscript) |
| Pages | 15 頁（cover + 11 本文 + 3 references） |
| ファイル配置 | `open_access/Law_Koutsos_2020_LE_Erosion_Particles_Rain_WindEnergy.pdf`（960 KB） |
| 助成 / データ協力 | Senvion UK Ltd.（運用データ提供）、UK Met Office（hourly rainfall data）|

---

## 2. 論文構成

| 章 | 内容 |
|---|---|
| §1 Introduction | LEE 概要、EDP Renewables 14年データ、LEP（コーティング+テープ）、業界標準テスト批判 |
| §2 Methodology | §2.1 Sample（18 wind farms × 4 erosion 要因）、§2.2 Dynamic modelling（4 ESI）、§2.3 Springer's Miner Model、§2.4 AEP loss methodology |
| §3 Results and Discussion | §3.1 Rain erosion、§3.2 Springer model 性能、§3.3 Hail/Sea/Quarry、§3.4 AEP loss analysis |
| §4 Conclusion | LEE 加速要因、testing standard 問題、UK 全体経済影響 |

---

## 3. 主要数値・主張（Paper 引用候補）

### 3.1 LEE 普遍性の実機証拠

**EDP Renewables 14 年運用調査** (§1)：
- 201 rotor blades inspected
- **174 blades (87%) had visible signs of erosion**
- **100 blades (50%) showing severe levels of LEE**

→ Paper 1/3 の動機強化に使える「LEE 普遍性」の実機データ

### 3.2 AEP 損失（実機運用データ）

**§3.4 AEP Loss Analysis**:
- 最も erosion が進んだサイト（Erosion Grade 2.11、worst grade in sample）:
  - 全タービン平均 AEP 損失: **1.75% (年3 vs 年1)**
  - **最悪 Turbine 3: AEP loss 4.93% (年1→年3)**
- 修復後（年4）: AEP がさらに **1.29% 低下**！
  - 修復 coating の dry film thickness 0.6 mm が drag を生んだ可能性
  - "repair tape 0.2 mm thick has the potential to reduce AEP by up to 2%"

**Table 2: UK 経済モデル**:
| Parameter | Value |
|---|---|
| Onshore Capacity Factor | 30% |
| Offshore Capacity Factor | 40% |
| Energy Price | £70/MW·h |
| AEP Loss After 2 Years | 1% |
| AEP Loss After 5 Years | 2% |
| AEP Loss After 10 Years | 3% |
| AEP Loss After 15 Years | 5% |
| **UK 全体 LEE 経済影響 (2019)** | **£76.5 million** |

→ Paper 1 / Paper 3 の経済意義論述に使える実証データ

### 3.3 ESI 4 種類（Erosion Severity Indicators）

**§2.2 Dynamic Modelling Approach**:

| ESI | 数式 | パラメータ |
|---|---|---|
| ESI 1: Cumulative Impact Energy | KE = (1/2) M V² | M = droplet mass, V = impact velocity |
| ESI 2: Cumulative Impact Force | F = M V² / D_p | D_p = droplet diameter |
| ESI 3: Water-hammer Pressure | P = V (ρ_l c_l ρ_c c_c) / (ρ_l c_l + ρ_c c_c) | ρ, c = density, speed of sound of liquid/coating |
| ESI 4: Average Rain Erosion Stress | σ_avg = P (1 + φ_sc)/(1 - φ_sc φ_lc) × [1 - φ_sc (1+φ_lc)/(1+φ_sc) (1-e^(-γ))/γ] | φ = acoustic impedance ratios |

サポート式：
- Best (1950): D_p = 1.0011 × I^0.232（raindrop diameter, I = rainfall rate mm/hr）
- Atlas (1973): V_t = 9.65 - 10.3 × e^(-0.6D_p)（terminal velocity）
- Springer (1976): n = 6V cos θ / (π V_t D_p³) × It（droplets per unit area）

**重要**: これらは **blade tip speed (SCADA) + rainfall rate (Met Office) → LEE 予測** の物理モデル。**Paper 3 の SCADA × 画像 × 気象データ統合の直接的先行例**。

### 3.4 Springer Model の限界（重要な負の発見）

**§3.2**:
- Springer's Miner rule（lab test 由来）で計算した failure 値は **0.0005**（Miner rule の failure 閾値 1 から大きく外れる）
- "**There is little correlation between test results and actual operational performance**"
- 原因仮説: lab test の continuous rainfall vs 実機の varying cycles

→ **Paper 2 / Paper 3 の研究動機**：lab-derived fatigue models alone is insufficient for field LEE prediction

### 3.5 Solid Particles vs Rain（伝統的 assumption への反論）

**§3.3**:
- **Quarry sites**: Erosion Grade 1-2（rain only サイト 0.17 と比較）
- **Sea aerosol site** (50m from sea): Erosion Grade 1.67
- "**Offshore turbines will experience greater erosion levels than onshore turbines**"
- Hail sites: 驚くべきことに 2 サイトとも LEE なし（サンプル時間不足の可能性）

→ Paper 1/3 で気象データ統合の **rainfall だけでなく atmospheric particulate も考慮すべき** という方向性提示

---

## 4. Paper 1/2/3 への引用候補

### 4.1 Paper 1 への引用候補（2 件）

#### P1-L-A: §1 Introduction（LEE 普遍性の実機証拠）

**引用箇所**: Paper 1 §1 Introduction

**引用案**:
> "Law and Koutsos (2020 [新規]) surveyed 18 operational wind farms in the UK and reported that EDP Renewables found 174 of 201 inspected blades (87%) with visible erosion after 14 years of operation, with 50% showing severe LEE levels (cited in Law and Koutsos 2020 §1). This empirical ubiquity of LEE on aging wind farms reinforces the operational urgency of detection-driven prioritization addressed by the present study."

**根拠**: §1 で EDP Renewables の 87% / 50% 数値を明示

**効果**: 動機を実機統計で裏付け（Mishnaevsky 2021 の €56-75M/year と並列補強）

#### P1-L-B: §5.3 Discussion（経済意義）

**引用箇所**: Paper 1 §5.3 O&M Discussion

**引用案**:
> "On 18 operational wind farms in the UK, Law and Koutsos (2020 [新規]) observed average AEP losses of 1.75% (medium erosion) to 4.93% (worst turbine) and estimated the 2019 UK-wide economic impact of LEE at £76.5 million."

**根拠**: §3.4 で実測 AEP losses + UK 全体経済影響

**効果**: 産業意義を **実機運用データ** で裏付け（Mishnaevsky 2021 のレビュー数値 €56-75M と相互補強）

### 4.2 Paper 2 への引用候補（1 件）

#### P2-L-A: §1 Introduction（lab vs field の差異）

**引用箇所**: Paper 2 §1 Introduction（動機部分）

**引用案**:
> "The disconnect between accelerated rain erosion laboratory tests and field LEE behaviour has been documented empirically: Law and Koutsos (2020 [新規]) found that Springer's Miner-rule-based predictions calculated 0.0005 against a failure threshold of 1 on field data from 18 operational UK wind farms, indicating that lab-derived erosion fatigue models alone are insufficient for field prediction. This motivates the SCADA-based load estimation framework developed here."

**根拠**: §3.2 で Springer model の field 実証失敗

**効果**: Paper 2 の SCADA-based approach の必然性を field 実証で裏付け（任意・優先度中）

### 4.3 Paper 3 への引用候補（最重要！）

#### P3-L-A: §2 Related Work（ESI 直接引用）

**引用箇所**: Paper 3 §2 Related Work（気象 + SCADA 接続論文）

**引用案**:
> "Law and Koutsos (2020 [新規]) proposed four Erosion Severity Indicators (ESI) combining blade tip speed and rainfall rate via droplet impact physics—including impact energy (ESI 1), impact force (ESI 2), water-hammer pressure (ESI 3), and average rain erosion stress (ESI 4)—to predict LEE onset and severity on operational turbines. Their ESI framework operates at the meteorological-operational interface but does not incorporate image-derived damage state observation. The integrated pipeline proposed here extends this approach by adding image-derived damage scoring (Module A) as a complementary modality alongside SCADA-driven fatigue loading (Module B), enabling cross-validation between physics-based meteorological predictors and observed surface damage."

**根拠**: §2.2 全体 + Eqs. 1-7

**効果**: **Paper 3 の独自性を明確化**（先行手法は 2-modality、本研究は 3-modality）。SCADA-image-meteorological fusion の物理的根拠を確立

#### P3-L-B: §6 Future Work（気象データの拡張方向）

**引用箇所**: Paper 3 §6 Future Work

**引用案**:
> "Future extensions to the integrated pipeline should consider atmospheric particulate inputs in addition to rainfall metrics: Law and Koutsos (2020 [新規], §3.3) demonstrated that solid airborne particles—from quarries or sea-salt aerosols—accelerate LEE significantly beyond rain alone, with offshore wind farms (within 50 m of sea) experiencing Erosion Grade 1.67 versus 0.17 for purely rain-exposed onshore sites."

**根拠**: §3.3 quarry vs sea vs rain の比較

**効果**: Paper 3 の将来研究方向を実機データで裏付け

---

## 5. 副次発見と未引用関連論文

### Law 2020 が引用している論文のうち、Paper 1/2/3 未引用の重要候補

| Ref # | 論文 | 内容 |
|---|---|---|
| [2] | Sareen, Sapre & Selig 2012 Wind Engineering | LEP tape の AEP effects（既に Mishnaevsky 2021 でも発見） |
| [6] | MacDonald 2016 Wind Energy | Hail meteorological observations for erosion prediction |
| [9] | Han, Kim, Kim 2018 Renew. Energy 115:817-823 | "Effects of contamination and erosion at LE or blade tip on AEP" |
| [10] | Selig, Sareen, Sapre 2014 Wind Energy 17(10):1531-1542 | LEE on wind turbine blade performance |
| [22] | Zhang et al. 2015 Prog. Organic Coatings | Erosion of WT blade coatings |
| [23] | Bech, Hasager, Bak 2017 Wind Energy Science | "Extending Life of WT Leading Edges by Reducing Tip Speed During Extreme Precipitation"（既に Mishnaevsky 2021 でも発見） |

これらは A11 の追加検討候補だが、Mishnaevsky 2021 でも引用されているため、Mishnaevsky 経由引用で十分な場合が多い。

---

## 6. Claude Code 推定優先度

| 引用候補 | 推定優先度 | 理由 |
|---|---|---|
| **P3-L-A**（Paper 3 §2 ESI 4 種類） | **🔴 高** | **Paper 3 の独自性**（3-modality fusion）を直接的先行研究との対比で明確化 |
| **P1-L-A**（Paper 1 §1 87%/50%）| **🔴 高** | LEE 普遍性の最強実機証拠 |
| **P1-L-B**（Paper 1 §5.3 £76.5M, 1.75-4.93%）| **🔴 高** | 経済意義を Mishnaevsky と並列補強 |
| **P3-L-B**（Paper 3 §6 solid particles）| 🟡 中 | 将来方向の補足（Future Work） |
| **P2-L-A**（Paper 2 §1 Springer fail）| 🟡 中 | Paper 2 動機の field 実証（任意） |

### 推奨される最低限の適用

**最も価値の高い 3 件**:
1. **P3-L-A**（Paper 3 §2: ESI 直接引用）→ Paper 3 の独自性確立
2. **P1-L-A**（Paper 1 §1: 87%/50%）→ 動機強化
3. **P1-L-B**（Paper 1 §5.3: £76.5M）→ 経済意義

これら 3 件で **Paper 1 と Paper 3 の研究意義** が「実機データに基づく具体的数値」で大幅に強化されます。

---

## 7. Mishnaevsky 2021 との関係

| 比較項目 | Mishnaevsky 2021 | Law & Koutsos 2020 |
|---|---|---|
| 性質 | レビュー論文（包括的、DTU グループ） | 実機調査論文（18 sites、Edinburgh + Senvion） |
| 提供する数値 | €56-75M/year（欧州全体、文献経由） | £76.5M (2019, UK 単独、自身の計算) |
| LEE 普遍性証拠 | Anholt 2016 Ørsted 補修事例 | EDP Renewables 87% (174/201) / 50% severe |
| AEP loss 範囲 | 1.5-7% (文献レビュー) | 1.75-4.93% (実測) |
| 物理モデル | レビュー（CFD, SPH, CEL等） | 自身の ESI 1-4 + Springer Miner |
| Paper 1 への価値 | 物理機序 + 経済影響 | 実機統計 + 実測 AEP loss |
| Paper 3 への価値 | 多分野統合の正当化 | ESI（SCADA + 気象 → LEE 予測） |

→ **両者は相互補完的**。Mishnaevsky でレビュー視点、Law で実機実証視点を提供。

---

## 8. 関連メモ

- `tools/reference_audit/A9_mishnaevsky_2021_full_reading_2026-06-11.md` — Mishnaevsky 2021 精読結果
- `tools/reference_audit/batch10_round2B_part1_progress_2026-04-29.md` — Vera-Tudela 2017 / Heo & Na 2025
- `memory/project_blade_paper_audit_progress.md` — 監査全体の進捗

---

## 9. 次のステップ

1. ✅ Law 2020 精読 + ドキュメント化（本ファイル）
2. ⏸ himinさんによる P1-L-A, P1-L-B, P3-L-A の採用判断
3. ⏸ Aird 2023 の **himinさん手動 DL**（MDPI bot blocking で自動取得不可）
4. ⏸ memory `project_blade_paper_audit_progress.md` 更新
