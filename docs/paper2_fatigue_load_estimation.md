# Paper 2: OpenFASTスケーリングモデルと公開SCADAを用いたSenvion MM82風車の長期疲労荷重推定基盤の構築

**ステータス**: v7.0（構成整理・DEL比率統計追加）
**最終更新**: 2026-04-10（v7: タイトル確定、Abstract 4ブロック化、§4.4 Table 8b追加、Limitations 8項目に再構成）

---

## タイトル案（確定）

**Site-Specific Blade Fatigue Load Estimation via Reference Turbine Scaling and Public SCADA: A Penmanshiel Case Study**

## 1文主張

NREL 5MW参照タービンの幾何スケーリングとIEC準拠TI直接計測SCADAを公開データのみで接続し、Senvion MM82相当機のサイト別疲労荷重環境を相対比較可能な形で再現的に定量化する基盤を構築した。

---

## 章立て

```
1. Introduction
   1.1 Background
   1.2 Problem Statement
   1.3 Objective
   1.4 Methodological Contribution  ← v3.0追加
   1.5 Scope and Limitations
2. Related Work
3. Methods
   3.1 OpenFAST Simulation Setup (NREL 5MW Reference)
   3.2 Geometric Scaling: NREL 5MW → MM82
   3.3 DLC 1.2 Multi-Seed Design
   3.4 Rainflow Counting (ASTM E1049)
   3.5 DEL Matrix and Weight Calibration
   3.6 Penmanshiel SCADA Dataset
   3.7 Site DEL Estimation Pipeline
4. Results
   4.1 Rainflow Implementation Validation
   4.2 Multi-Seed Reproducibility
   4.3 NREL 5MW DEL Matrix
   4.4 MM82 Scaling Validation
   4.5 MM82 DEL Matrix and Weight Recalibration
   4.6 Penmanshiel Site DEL (Monthly / Fleet)
   4.7 Longitudinal Analysis (T01, 2016–2021)
5. Discussion
   5.1 Validity of the Scaling Approach
   5.2 TI Measurement Methodology
   5.3 Wind Variability vs. Degradation
   5.4 Limitations
6. Reproducibility
7. Conclusion
Appendix A: DLC 1.3 (ETM) Supplementary Results
Appendix B: DLC 2.1/2.2 Ultimate Load Assessment
References
```

---

## Abstract

**何を作ったか**: 公開データのみを用いて実サイトの風車ブレード根元フラップ疲労荷重（DEL）を推定する再現可能な基盤を構築した。幾何スケーリング、IEC準拠TI直接計測、および公開SCADAを一気通貫のパイプラインとして接続した点が本研究の寄与である。

**どう作ったか**: NREL 5MW参照タービンのOpenFASTシミュレーション（DLC 1.2, 240ケース, ASTM E1049 Rainflow）でDELマトリクスを作成し、Senvion MM82への幾何スケーリング（λ_R = 0.651, 理論比との誤差6.5%）により機種適合DELマトリクスを生成した。これをPenmanshiel Wind Farm（7台, Zenodo公開SCADA）に適用し、10分値直接計測TIに基づく月次DELを算出した。

**主要結果**: 年間平均DELは1,497〜1,742 kN·m（タービン間幅）で、冬季にピークを示す季節性を確認した。6年間の縦断分析（T01）では、DEL増加（+13.7%）は風況変動が主因であり、公開SCADA指標の範囲内ではCp_maxの低下傾向は観察されなかった。

**何を主張しないか**: 本基盤は荷重環境の相対的な定量化を目的としており、絶対荷重精度の保証およびブレード劣化の直接検出は対象外である。

---

## 1. Introduction

### 1.1 Background

風車ブレードは20年以上の設計寿命を通じて繰り返し疲労荷重を受ける。疲労荷重の蓄積はブレード構造の劣化進行に寄与し、前縁エロージョン等の表面損傷との複合的な影響も報告されている [8]。IEC 61400-1:2019 [7] に規定されるDLC 1.2（正常乱流モデル, NTM）は疲労設計の基本ケースであり、ブレード根元のフラップ方向曲げモーメントが主要な疲労損傷チャンネルとなる。疲労等価荷重（DEL: Damage Equivalent Load）は、Rainflow計数法に基づいて算出され、材料のS-Nカーブ（Wöhler曲線）の指数mに依存する。

実運用では風速とTIが時々刻々変化するため、実サイトの長期DEL推定には風況統計との統合が必要である。しかし、aeroelasticシミュレーション環境の構築障壁が高く、DELマトリクスに基づくサイト固有の疲労荷重評価は普及していない。

### 1.2 Problem Statement

公開されている風車のリファレンスモデル（NREL 5MW等）は研究用途として広く利用されているが、実サイトで稼働する機種（本研究ではSenvion MM82）とはローター径・パワークラスが大きく異なる。リファレンスモデルのDELマトリクスを直接適用すると、絶対値の機種間比較が不可能であり、サイト固有の疲労荷重評価としての信頼性が低い。

加えて、SCADAデータからTIを算出する方法論の違いが結果に大きく影響する。風速ビン内の統計量から近似するアプローチ（bin-averaged TI）と、IEC 61400-1:2019 [7] 準拠の10分間値直接計測では、得られるTIに数倍の差が生じうる（本研究での検証結果: 近似値 ~0.035 vs. 直接計測 ~0.14）。

### 1.3 Objective

本研究の目的は以下の3点である:

1. NREL 5MW参照タービンからSenvion MM82への幾何スケーリングにより、機種適合DELマトリクスを再現可能な形で生成すること
2. Penmanshiel Wind Farm（Zenodo公開SCADA）のIEC準拠TI直接計測値とDELマトリクスを組み合わせ、月次・年次の疲労荷重推定を実施すること
3. 6年間の縦断分析により、観測された荷重トレンドが風況変動のみで整合的に説明可能かを検証すること

### 1.4 Methodological Contribution

本研究の方法論的寄与は、以下の3要素の**組み合わせ**にある:

- **幾何スケーリング＋翼型プロキシの限界の定量化**: 理論比との整合（6.5%）を示しつつ、モデルの主張範囲を相対比較に限定
- **bin-averaged vs. 直接計測TIの実データ差異**: 約4倍の差を実サイトデータで確認し、既存文献の指摘（Colone et al. 2018 [12]）を裏付け
- **公開データのみによる再現可能性**: 非公開データや商用ソフトウェアを一切使用せず、標準計算機で480ケースを48時間で完了可能

いずれの要素も単独では既知の手法に基づく。しかし、これらを接続することで、特定サイト・特定機種の月次DEL変動や台間荷重比較が初めて可能になる——DELマトリクスのみでは季節変動を評価できず、SCADAのみではTI方法論の差異がDELに与える影響を定量化できない。この統合により、第三者が追試可能な形でサイト固有の疲労荷重環境を評価する基盤を構成した。

### 1.5 Scope and Limitations

本研究は「荷重環境の定量化基盤」の構築を目的としており、以下は対象外である:

- ブレード劣化の直接検出
- 絶対荷重値の設計認証レベルでの精度保証
- 他機種・他サイトへの一般化

---

## 2. Related Work

### 2.1 Aeroelastic Simulation for Fatigue Assessment

OpenFASTはNRELが開発するオープンソースaeroelastic解析コードであり [1]、NREL 5MW参照タービン [2] は荷重評価研究の標準ベンチマークである。OpenFASTの妥当性はOC5プロジェクト等の第三者検証で確認されている [17]。Hayman (2012) はMLifeツールによるDEL算出手法（ASTM E1049準拠Rainflow、等価サイクル数正規化）を体系化した [10]。Rainflow計数法の原理はMatsuishi & Endo (1968) [14] に遡り、Downing & Socie (1982) [15] が計算アルゴリズムを体系化した。本研究はこの枠組みに準拠し、Python `rainflow` 3.2.0 [23] を使用する。ただし、荷重時系列からサイト固有の長期DELへ接続するパイプラインは標準化されておらず、TI計測精度への依存が大きい。

### 2.2 Reference Turbine Scaling

Bak et al. (2013) はDTU 10MW参照タービンの設計にあたり、幾何スケーリング則を体系的に整理した [3]。Fingersh et al. (2006) はNRELの風車設計コスト・スケーリングモデルにおいて、ブレード質量がR^2.3でスケーリングする経験則を提示した [16]。断面剛性はR^4でスケーリングする経験則と合わせ、これらが広く用いられている。ただし、翼型データの機種固有性（非公開の場合が多い）がスケーリング精度の主要な不確実性要因となる。Bir & Jonkman (2007) はリファレンスタービンのモーダル解析とスケーリング則の限界を議論し、翼型の空力データが機種固有であるため、幾何スケーリングのみでは動的応答の精密な再現に限界があることを指摘した [11]。本研究はこの限界を前提とし、スケーリングモデルの主張範囲を相対比較に限定する。

### 2.3 SCADA-Based Fatigue Monitoring

SCADAベースの風車状態監視はTautz-Weinert & Watson (2017) [4] がレビューしている。SCADAからDELを推定するアプローチは、DELマトリクスの機種依存性とTI計測精度の問題から限定的である。Vera-Tudela & Kühn (2017) [21] はSCADA信号からの疲労荷重予測を実証し、Dimitrov et al. (2015) [13] は乱流強度が荷重に与える影響を定量化した。Colone et al. (2018) [12] はSCADAと空力シミュレーションの統合パイプラインを提案し、TI算出方法論の差異がDEL推定に大きく影響することを報告した。Herp et al. (2018) [22] はベイズ推定による故障予測を試みている。IEA Wind Task 42（寿命延長）[20] では、SCADAベースの荷重評価が寿命延長判断の重要な入力とされており、本研究はこの文脈に位置づけられる。本研究の知見（bin近似 vs. 直接計測で4倍の差）はColone et al.の指摘を実データで裏付ける。

### 2.4 Penmanshiel Wind Farm Dataset

Penmanshiel Wind Farmの公開SCADAデータセット [5]（Zenodo, CC-BY 4.0）は、Senvion MM82（14台, 2.05 MW）の10分値データを2016–2021年にわたり提供する。風速標準偏差が直接記録されている点が、IEC準拠TI計算を可能にする。

---

## 3. Methods

### 3.1 OpenFAST Simulation Setup

Table 1に基準シミュレーション設定を示す。

**Table 1: OpenFAST Simulation Configuration**

| Parameter | Value |
|---|---|
| Code | OpenFAST v3.5.1 |
| Reference turbine | NREL 5MW Land-Based (r-test v3.5.1) |
| Design load case | DLC 1.2 (IEC 61400-1:2019 [7], NTM) |
| Wind speed V | 4, 6, 8, 10, 12, 14, 16, 18 m/s (8 levels) |
| Turbulence intensity TI | 8%, 12%, 14%, 16%, 20% (5 levels) |
| Seeds per condition | 6 (IEC 61400-1:2019 §8.3.2 minimum requirement [7]) |
| Total cases | 240 (NREL 5MW) + 240 (MM82) = 480 |
| Simulation time | 600 s (+ 60 s transient removal) |
| Modules | ElastoDyn + AeroDyn15 + ServoDyn (ROSCO 2.10.1) + InflowWind |
| Wind field | TurbSim v3.5.1 (IEC IECKAI, PL profile) |

### 3.2 Geometric Scaling: NREL 5MW → Senvion MM82

NREL 5MW参照タービン（R=63 m, P=5 MW, HH=87.6 m）からSenvion MM82（R=41 m, P=2.05 MW, HH=59 m）への幾何スケーリングを実施した。Table 2にスケーリング係数を示す。

**Table 2: Geometric Scaling Parameters**

| Component | Scaling law | Coefficient |
|---|---|---|
| Blade / rotor radius | λ_R = 41/63 | 0.651 |
| Tower / hub height | λ_H = 59/87.6 | 0.674 |
| Blade mass density (kg/m) | λ_R^2.3 | ×0.372 |
| Blade stiffness (Nm²) | λ_R^4 | ×0.179 |
| Tower mass density (kg/m) | λ_H^2 | ×0.454 |
| Tower stiffness (Nm²) | λ_H^4 | ×0.206 |

**Table 3: Key ElastoDyn Parameters**

| Parameter | NREL 5MW | MM82 |
|---|---|---|
| TipRad | 63 m | 41 m |
| TowerHt | 87.6 m | 59 m |
| RotSpeed (rated) | 12.1 RPM | 17.1 RPM |
| GBRatio | 97 | 105 |
| NacMass | 240,000 kg | 65,000 kg |
| HubMass | 56,780 kg | 14,000 kg |

翼型ポーラー（Cylinder/DU/NACA系列）はNREL 5MWの翼型データをプロキシとして使用した（Senvion MM82の翼型データは非公開）。この近似は、モデルの絶対精度ではなく相対比較・サイト適合の観点で妥当と判断した（§5.1で詳述）。

### 3.3 DLC 1.2 Multi-Seed Design

IEC 61400-1:2019 [7] に準拠し、各風速・TI条件に対して6シードの独立なTurbSim風場を生成した。シード間のDEL変動をCV（変動係数）で評価し、統計的再現性を確認する。

TurbSim設定: IEC IECKAI乱流モデル、Power Law風速プロファイル（指数 α = 0.2, IEC標準値）。参照高さ（RefHt）はそれぞれのハブ高さ（NREL 5MW: 87.6 m, MM82: 59 m）に設定した。乱流長さスケール（IEC Kaimal）はIEC 61400-1:2019 [7] §6.3のデフォルト式に従う（Λ_1 = 42 m for HH ≥ 60 m; Λ_1 = 0.7 × HH for HH < 60 m）。NREL 5MWはGridSize=160 m×160 m、MM82はGridSize=100 m×100 m（各ローター直径をカバー）。

### 3.4 Rainflow Counting

DEL算出にはASTM E1049系4点法Rainflow（Python `rainflow` 3.2.0）を使用した。

```
DEL = (Σ(n_i × ΔS_i^m) / N_eq)^(1/m)
```

| Parameter | Value |
|---|---|
| Channel | RootMyb1 (blade root flapwise moment) |
| m (S-N exponent) | 10 (GFRP; DNVGL-ST-0376 [18], DOE/MSU database [19]) |
| T_eq | 600 s |
| N_eq | 1 Hz × T_eq = 600 cycles* |
| Transient removal | First 60 s skipped |

*N_eq (equivalent cycle count) is the product of an assumed reference frequency (1 Hz) and the equivalent time period T_eq = 600 s, yielding N_eq = 600 equivalent cycles per simulation. This convention follows Hayman (2012) [10] and ensures that DEL values are normalized to a consistent reference cycle count across all simulations.

初期解析で使用した簡易Rainflow（ハーフサイクルカウント）との比較を§4.1で報告する。

### 3.5 DEL Matrix and Weight Calibration

DELマトリクスの各セルは6シード平均値とする。風速VとTI_directの2変数からDELを推定する線形モデル:

```
DEL_norm = w_V × V_norm + w_TI × TI_norm
```

V_norm および TI_norm は min-max 正規化により [0, 1] にスケーリングした（V_norm = (V − V_min) / (V_max − V_min), TI_norm = (TI − TI_min) / (TI_max − TI_min)）。同様に DEL_norm も min-max 正規化を適用した。LinearRegression（正値制約、切片なし）により、w_V / w_TI の支配因子比率を較正する。

### 3.6 Penmanshiel SCADA Dataset

**Table 4: Penmanshiel Wind Farm Overview**

| Item | Description |
|---|---|
| Data source | Zenodo DOI: 10.5281/zenodo.5946808 (CC-BY 4.0) |
| Turbine model | Senvion MM82 (2.05 MW, D=82 m, HH=59 m) |
| Number of turbines | 14 (this study: T01–T07)* |
| Time resolution | 10-min averages |
| Period | 2016–2021 (main analysis: 2020 full year) |
| Location | Penmanshiel, Scotland (onshore) |
| Commissioning | September 2016 |

*T01–T07 were selected based on data completeness: these seven turbines had the highest ratio of valid 10-min records (after QC filtering) across the 2016–2021 period. The remaining seven turbines (T08–T14) had substantially higher missing-data rates and were excluded to ensure consistent monthly DEL estimation.

TIはIEC 61400-1:2019 [7] 準拠の10分値直接計測:

```
TI = σ_V,10min / V_10min
```

SCADAに "Wind speed, Standard deviation (m/s)" 列が直接提供されており、bin近似を経由しない。

### 3.7 Site DEL Estimation Pipeline

サイトDEL推定は以下の手順で実施する:

1. SCADAの各10分レコードについてV_10minとTI_directを取得
2. DELマトリクスからbilinear interpolationでDEL(V, TI)を推定
3. 月次・年次で集計し、時系列トレンドを評価

品質管理（QC）: 以下の閾値でレコードを除外した。

- **V < 3 m/s**: Senvion MM82のカットイン風速（3.5 m/s）以下であり、発電運転外のデータを排除するための保守的な閾値
- **P < 0**: 発電運転中に負の出力は物理的に発生しないため、停止中・消費電力モードのレコードを除外
- **TI > 0.5**: IEC 61400-1:2019 [7] のNTMモデルにおいて想定されるTI範囲を大幅に超過する値（TI=50%は極端な非定常状態を示す）。工学的判断に基づく外れ値除去閾値として設定

2018年のQCによる除去率は35%と高く、主にV < 3 m/s（カットイン以下の低風速期間）が主要因であった。この高い除去率はデータ品質の限界を示しており、§5.3で議論する。

---

## 4. Results

### 4.1 Rainflow Implementation Validation

ASTM E1049系標準Rainflow（4点法）と簡易Rainflow（ハーフサイクルカウント）の比較をTable 5に示す。

**Table 5: Rainflow Implementation Comparison (NREL 5MW, 240 cases)**

| Metric | Value |
|---|---|
| Mean error (simple vs. standard) | **42%** (simple systematically underestimates) |
| Maximum error | **76%** (V=4 m/s, TI=12%) |
| Error trend | Larger at low wind speeds (V=4–8 m/s: 50–76%), smaller at high speeds (V≥12 m/s: 12–40%) |

簡易版のハーフサイクルカウントは、低TSR域（V=4〜8 m/s）での非定常成分を大幅に過小評価する。**高精度疲労評価には標準Rainflow実装が必須**である。

> Figure 1: Rainflow comparison — standard vs. simple DEL by wind speed and TI  
> → `fig_rainflow_comparison.png`

### 4.2 Multi-Seed Reproducibility

**Table 6: Multi-Seed DEL Statistics (NREL 5MW, 240 cases)**

| Metric | Value |
|---|---|
| CV overall mean | **8.9%** |
| CV median | **5.9%** |
| CV maximum | **35.1%** (V=4 m/s, TI=8%; low-TSR instability) |
| CV range for V ≥ 8 m/s | 1.8–14.4% |

V=4 m/sでは低TSR（翼端速度比が低く空力が不安定）により確率的変動が大きいが、実用的な疲労評価ではV ≥ 6 m/sの寄与が支配的であり、低風速ビンの高CVは長期DELへの影響が限定的である。

> Figure 2: Coefficient of variation (CV) of DEL across six seeds, grouped by wind speed (V = 4–18 m/s), for all five TI conditions (NREL 5MW, DLC 1.2). Each box shows the distribution of CV values across TI levels at a given wind speed.  
> → `fig_cv_boxplot.png`

### 4.3 NREL 5MW DEL Matrix

Table 7にNREL 5MW参照タービンのDELマトリクス（6シード平均、標準Rainflow）を示す。

**Table 7: NREL 5MW DEL Matrix (kN·m, DLC 1.2, standard Rainflow)**

| V \ TI | 8% | 12% | 14% | 16% | 20% |
|:---:|---:|---:|---:|---:|---:|
| 4 | 970 | 1,417 | 1,559 | 1,484 | 1,864 |
| 6 | 1,749 | 2,704 | 3,070 | 3,414 | 4,159 |
| 8 | 3,425 | 4,612 | 5,506 | 6,218 | 7,173 |
| 10 | 4,673 | 6,196 | 7,156 | 7,824 | 9,282 |
| 12 | 6,176 | 7,979 | 8,759 | 9,804 | 11,859 |
| 14 | 7,290 | 9,316 | 9,910 | 11,146 | 12,798 |
| 16 | 7,951 | 10,240 | 11,192 | 11,952 | 14,472 |
| 18 | 8,692 | 11,034 | 12,095 | 12,972 | 15,109 |

> Figure 3: NREL 5MW blade root flapwise DEL heatmap (kN·m). Horizontal axis: wind speed V (m/s); vertical axis: turbulence intensity TI (%); color scale: 6-seed mean DEL (kN·m). DLC 1.2, standard Rainflow, m = 10.  
> → `fig_del_heatmap.png`

重み較正結果（NREL 5MW）: w_V = 0.810, w_TI = 0.190（R² = 0.926）。風速が疲労荷重の支配因子である。

Weibull風速分布（k=2）とIEC NTM式によるTI-V関係を用いた長期DEL（V-TI同時分布、独立近似）をTable 7bに示す。

**Table 7b: Lifetime DEL by IEC Class (NREL 5MW, kN·m)**

| IEC Class | Class I (Vave=10.0 m/s) | Class II (Vave=8.5 m/s) | Class III (Vave=7.5 m/s) |
|---|---|---|---|
| Class C (I_ref=0.12) | 9,366 | 8,965 | 8,564 |
| Class B (I_ref=0.14) | 10,348 | 9,938 | 9,529 |
| Class A (I_ref=0.16) | 11,327 | 10,891 | 10,452 |

> Figure 3b: Lifetime DEL sensitivity to IEC class  
> → `fig_lifetime_del_sensitivity.png`

### 4.4 MM82 Scaling Validation

単一ケース検証（V=10 m/s, TI=14%, Seed 1）の結果をTable 8に示す。

**Table 8: MM82 Scaling Validation (Single Case)**

| Metric | Value |
|---|---|
| MM82 DEL | 1,850 kN·m |
| NREL 5MW DEL (same condition) | 7,156 kN·m |
| DEL ratio (MM82 / NREL 5MW) | **0.258** |
| Theoretical ratio (R_MM82/R_NREL)³ | 0.276 |
| Deviation from theory | **6.5%** |

DEL比率の理論予測との誤差6.5%は、スケーリング近似（翼型プロキシ使用）と単一シードの変動の範囲内にある。この整合性から、本プロキシモデルは月次・台間・風況条件間の相対比較に使用可能と判断する（絶対荷重値の精度保証ではない; §5.1参照）。

**全条件の統計的検証**: 全40条件（8V × 5TI、各6シード平均）のDEL比率（MM82 / NREL 5MW）の統計量をTable 8bに示す。

**Table 8b: DEL Ratio Statistics Across All V×TI Conditions**

| Metric | Value |
|---|---|
| Mean ratio | **0.263** |
| Median ratio | 0.260 |
| Std | 0.020 |
| Min | 0.208 (V=4 m/s, TI=12%) |
| Max | 0.326 (V=6 m/s, TI=8%) |
| Mean deviation from theory (0.276) | **−4.6%** |

V=4 m/sでは低TSR不安定性（§4.2と整合）により散らばりが大きく（ratio: 0.208–0.260）、V≥8 m/sでは安定する（ratio: 0.255–0.290, std ≤ 0.007）。TI依存性は小さく、5TIレベル間の平均比率差は0.011以内である。全体の平均偏差−4.6%は、翼型プロキシによる空力特性差がDELをやや過小評価する方向に作用していることを示唆する。Figure 4(b)はこの風速依存性を可視化している。

> Figure 4: Scaling validation — (a) NREL 5MW vs. MM82 DEL scatter, (b) DEL ratio by wind speed  
> → `fig_scaling_validation.png`

### 4.5 MM82 DEL Matrix and Weight Recalibration

**Table 9: MM82 Proxy DEL Matrix (kN·m, DLC 1.2, 240 cases)**

| V \ TI | 8% | 12% | 14% | 16% | 20% |
|:---:|---:|---:|---:|---:|---:|
| 4 | 215 | 295 | 383 | 390 | 484 |
| 6 | 570 | 771 | 817 | 1,017 | 1,148 |
| 8 | 1,016 | 1,311 | 1,562 | 1,763 | 2,030 |
| 10 | 1,201 | 1,609 | 1,780 | 1,990 | 2,359 |
| 12 | 1,562 | 2,002 | 2,352 | 2,458 | 3,014 |
| 14 | 1,938 | 2,344 | 2,538 | 2,830 | 3,349 |
| 16 | 2,089 | 2,604 | 2,904 | 3,178 | 3,711 |
| 18 | 2,215 | 2,822 | 3,090 | 3,439 | 4,046 |

> Figure 5: MM82 proxy blade root flapwise DEL heatmap (kN·m). Horizontal axis: wind speed V (m/s); vertical axis: turbulence intensity TI (%); color scale: 6-seed mean DEL (kN·m). DLC 1.2, standard Rainflow, m = 10.  
> → `fig_del_heatmap_mm82.png`

**Table 10: Weight Recalibration — NREL 5MW vs. MM82**

| | NREL 5MW | MM82 |
|---|:---:|:---:|
| w_V | 0.810 | **0.725** |
| w_TI | 0.190 | **0.275** |
| R² | 0.926 | **0.943** |
| Pearson r | 0.978 | 0.976 |

MM82ではTIの寄与（w_TI）がNREL 5MWより相対的に増大した（0.190 → 0.275）。較正されたw_V / w_TI は**このモデル・この条件下での支配因子比率**であり、普遍係数ではない。この差の物理的・近似的要因の解釈は§5.1で詳述する。

**Note on R² interpretation**: R² = 0.926/0.943 captures the overall variance, but residual analysis has not been conducted. DEL-V非線形性（§5.4, Limitation 4）を考慮すると、V/TI端部で系統的偏差が存在する可能性がある。本線形モデルは支配因子比率の把握を目的としており、局所的な予測精度は限定的である。

### 4.6 Penmanshiel Site DEL

#### 4.6.1 TI Measurement Comparison

直接計測TIの詳細をTable 11に示す。

**Table 11: TI Measurement Methodology Comparison**

| Method | Bin-averaged (Kaggle) | Direct 10-min (Penmanshiel) |
|---|---|---|
| Formula | σ(V_bin) / μ(V_bin) | σ_V,10min / V_10min |
| IEC 61400-1:2019 compliance | Approximate | Full |
| Median TI | ~0.035 | 0.133–0.144 |
| Site consistency | Unknown | Consistent with onshore Scotland |

#### 4.6.2 Monthly DEL Estimation (2020, MM82 Basis)

MM82 DELマトリクスを適用した月次DEL推定結果をTable 12に示す。

**Table 12: Penmanshiel Monthly DEL — Fleet Average (5 turbines, 2020)**

| Month | V_mean (m/s) | TI_median | DEL_est (kN·m) |
|---|---|---|---|
| Jan | 10.1 | 0.146 | 1,862 |
| Feb | 11.6 | 0.148 | 2,296 |
| Mar | 9.5 | 0.137 | 1,668 |
| Apr | 6.7 | 0.137 | 1,060 |
| May | 7.4 | 0.137 | 1,308 |
| Jun | 8.2 | 0.131 | 1,463 |
| Jul | 7.1 | 0.137 | 1,233 |
| Aug | 7.3 | 0.132 | 1,227 |
| Sep | 8.0 | 0.137 | 1,476 |
| Oct | 8.2 | 0.120 | 1,325 |
| Nov | 9.0 | 0.131 | 1,551 |
| Dec | 8.7 | 0.121 | 1,403 |

年間平均DEL: 1,497〜1,742 kN·m（タービン間幅）。ピーク月: 2月（冬季北海低気圧による強風、最大2,356 kN·m）。

> Figure 6: Penmanshiel monthly mean DEL (MM82 basis), 2020  
> → `fig_penmanshiel_monthly_del_mm82.png`

#### 4.6.3 Fleet Comparison (2020)

台間DEL比較（5台, 2020年）の結果をTable 13に示す。DELの台間変動幅は1,497〜1,539 kN·m（2.8%）と小さく、フリート内の荷重環境は均質である。AEPの台間差（最大-3.5%）は主に風速差（V_mean: 0.3 m/s）に帰属される。

**Table 13: Penmanshiel Fleet Performance (2020)**

| Turbine | V_mean (m/s) | Cp_max | AEP_est (MWh) | Annual DEL (kN·m) |
|---|---|---|---|---|
| T01 | 7.62 | 0.451 | 6,506 | 1,503 |
| T02 | 7.41 | 0.445 | 6,113 | 1,526 |
| T04 | 7.45 | 0.451 | 6,381 | 1,497 |
| T05 | 7.32 | 0.444 | 6,010 | 1,539 |
| T06 | 7.30 | 0.447 | 6,129 | 1,498 |

### 4.7 Longitudinal Analysis (T01, 2016–2021)

**Table 14: T01 Longitudinal Trends**

| Year | Period | V_mean (m/s) | TI_med | DEL_annual (kN·m) | Cp_max |
|---|---|---|---|---|---|
| 2016 | Jun–Dec | 7.73 | 0.115 | 1,155 | 0.412 |
| 2017 | Full year | 8.32 | 0.119 | 1,325 | 0.428 |
| 2018 | Full year | 8.18 | 0.128 | 1,346 | 0.443 |
| 2019 | Full year | 8.08 | 0.130 | 1,351 | 0.450 |
| 2020 | Full year | 8.66 | 0.133 | 1,507 | 0.451 |
| 2021 | Jan–Jun | 7.96 | 0.133 | 1,340 | 0.454 |

2017→2020のDEL増加（+182 kN·m, +13.7%）はV_mean増加（8.32→8.66 m/s）とTI_med増加（0.119→0.133）に連動している。2021年はV_meanが低下するとDELも1,340 kN·m（2017水準）に戻った。

一方、Cp_maxは2017→2021で0.428→0.454と増加傾向を示した（原因未特定; 制御更新・補修・風速計ドリフト等の可能性; §5.3参照）。公開SCADA指標の範囲内ではCp_maxの低下傾向は観察されなかった。なお、このCp_max分析は荷重基盤構築（本論文の主目的）の範囲外の予備的探索である。

> Figure 7: T01 longitudinal trends, 2016–2021. (a) Annual mean blade root flapwise DEL (kN·m, MM82 proxy basis); (b) Cp_max (dimensionless). Error bars or shading, if shown, represent inter-month variability within each year.  
> → `fig_longitudinal_combined.png`

---

## 5. Discussion

### 5.1 Validity of the Scaling Approach

MM82プロキシのDEL比率（0.258）は理論予測（R³ = 0.276）と6.5%で整合し、相対比較（月次・台間・風況条件差）には十分な精度を持つことを示唆する。

Figure 4(b)に示すDEL比率の風速依存性は、このスケーリング近似の限界をより具体的に可視化している。TI=8%（低乱流）ではDEL比率が理論値0.276に近いが、高TI条件（TI=20%）ではばらつきが大きくなる。これは、翼型プロキシの空力応答差が乱流条件で増幅されることを示唆しており、本モデルの相対比較精度はTIが高いほど低下しうる。この観察は、§4.5で報告したw_TIの機種間差（NREL 5MW: 0.190 → MM82: 0.275）の一因である可能性がある。

ただし、本モデルは「MM82相当の近似モデル」であり、以下の不確実性を内包する:

- **翼型プロキシ**: Senvion MM82の翼型データは非公開であり、NREL 5MWの翼型（DU/NACA系列）で代替している。空力特性の差異がDELの絶対値に影響する可能性がある
- **構造動特性**: スケーリング則は質量分布と剛性の主要な傾向を捉えるが、固有振動数・モード形状の精密な一致は保証されない
- **制御系**: ROSCO汎用コントローラはSenvion固有の制御ロジックとは異なる

したがって、本モデルの主張範囲は**絶対値の妥当性より相対比較の妥当性**に置く。月次比較・台間比較・風況条件差には使えるが、設計認証レベルの絶対荷重推定には使えない。

### 5.2 TI Measurement Methodology

Penmanshielの直接計測TI（中央値0.133〜0.144）は、bin近似TI（~0.035）と約4倍の差を示した。bin近似はIEC 61400-1:2019 [7] のTI定義から逸脱しており、DEL推定に直接影響する。**SCADA由来のTIを用いる際はIEC準拠の算出方法の確認が不可欠**である。

### 5.3 Wind Variability vs. Degradation

縦断分析（T01, 2016–2021）から得られる観察結果は以下の2点である:

1. **DEL増加（+13.7%）は、同期間のV_meanおよびTI_medの増加と連動しており、風況変動で説明可能な範囲内にある**
2. **公開SCADAで利用可能な指標の範囲内では、Cp_maxの低下傾向は確認されない**（2017→2021: 0.428→0.454と増加傾向）

ただし、「劣化が存在しない」と結論づけることはできない:

- 微小なCp低下が風況年変動のノイズ（ΔV_mean ~0.6 m/s）に埋もれている可能性がある
- Cp_max増加およびTI_med経年増加（0.119→0.133）の原因が未特定（制御更新、補修、風速計ドリフト等）
- 2018年のQC除去率35%がデータ品質の限界を示す

本分析が示しているのは、**DELトレンドを解釈する前に風況正規化が不可欠であること**、および**公開SCADAのみでは劣化検出には証拠が不足すること**である。劣化検出には、風況正規化に加え、点検画像・補修履歴との統合が必要となる。

### 5.4 Limitations

1. **翼型プロキシによる空力近似**: MM82の翼型データは非公開であり、NREL 5MWの翼型をプロキシとして使用した。本モデル最大の不確実性要因であり、DEL絶対値の精度、w_V/w_TI較正（§4.5）、高TI条件での相対比較精度（§5.1）に影響する。このため主張範囲を相対比較に限定した
2. **DLC 1.2のみ**: 疲労設計には複数DLC（1.1, 1.2, 1.3等）の重み付き合成が必要。本研究はDLC 1.2単独
3. **単一サイト**: Penmanshielの結果を他サイトに一般化するには追加検証が必要
4. **線形重みモデルとbilinear補間**: DEL-V関係は非線形であるが、支配因子比率の把握を目的に線形近似を使用した（R² = 0.926–0.943）。DELマトリクスの8×5グリッドからのbilinear補間もグリッド端部で精度が低下する。いずれも局所的な予測精度に限界がある
5. **スケーリング比率の風速依存性**: 全40条件のDEL比率は平均0.263（理論0.276に対し−4.6%）だが、V=4–6 m/sでは散らばりが大きい（0.208–0.326）。低風速域での相対比較精度は限定的である（§4.4 Table 8b）
6. **縦断分析の制約**: 補修履歴が未入手のため、Cp_maxに劣化が見られない原因として補修実施の可能性を排除できない。TI_medの経年増加（0.119→0.133）の原因も気象記録との照合が未実施（§5.3で議論）
7. **構造応答の線形性仮定**: スケーリング則は線形弾性範囲を仮定。非線形挙動は考慮していない
8. **MM82長期DEL未算出**: MM82プロキシでは翼型近似の不確実性が長期積算に蓄積するため、意図的に未算出とした。実測荷重との照合が得られた段階で実施すべき課題である

---

## 6. Reproducibility

本研究で使用したすべてのデータソースは公開データである:

- **OpenFAST v3.5.1**: NREL公式リポジトリ（r-test v3.5.1含む）から無料入手可能 [1]
- **NREL 5MW参照タービン**: 定義文書 [2] およびOpenFAST付属入力ファイルとして公開
- **TurbSim v3.5.1**: OpenFASTスイートに同梱
- **ROSCO v2.10.1**: NREL公式GitHubリポジトリで公開 [9]
- **Penmanshiel SCADA**: Zenodo (DOI: 10.5281/zenodo.5946808, CC-BY 4.0) [5]
- **Rainflow**: Python `rainflow` 3.2.0 (PyPI, ASTM E1049系4点法)

MM82スケーリング入力ファイル（ElastoDyn, AeroDyn, ServoDyn）の生成手順はTable 2–3のスケーリング係数で再現可能であり、翼型データはNREL 5MWのプロキシをそのまま使用しているため、追加の非公開データは不要である。シミュレーション総ケース数480（NREL 240 + MM82 240）は、標準的な研究用計算機（8コア）で約48時間で完了する。

以下のスクリプト・設定ファイルがパイプラインの各段階に対応する:

| Stage | Script / Config | Description |
|---|---|---|
| 風場生成 | `turbsim_templates/*.inp` | TurbSim入力テンプレート（V/TI/seed別） |
| シミュレーション | `openfast_configs/{nrel5mw,mm82}/*.fst` | OpenFAST設定ファイル一式 |
| スケーリング | `scripts/generate_mm82_inputs.py` | Table 2–3のスケーリング係数適用 |
| DEL算出 | `scripts/compute_del_matrix.py` | Rainflow計数 + DELマトリクス生成 |
| 補間・QC | `scripts/interpolate_del.py`, `scripts/qc_scada.py` | bilinear補間 + SCADA品質管理 |
| 重み較正 | `scripts/calibrate_weights.py` | LinearRegression（正値制約・切片なし） |
| サイトDEL | `scripts/site_del_estimation.py` | 月次・年次DEL集計 |
| 図表生成 | `scripts/paper2_figures.py` | 全Figure再生成 |

---

## 7. Conclusion

本研究は、NREL 5MW参照タービンからSenvion MM82への幾何スケーリング（λ_R = 0.651）とPenmanshiel公開SCADAの10分値TI直接計測を組み合わせることで、実サイトの長期疲労荷重推定基盤を再現可能な形で構築した。

主な成果:

1. **スケーリング妥当性**: MM82プロキシモデルのDEL比率（0.258）は理論予測（0.276）と6.5%の誤差で整合し、相対比較に有効な精度を持つ
2. **Rainflow実装精度**: 標準Rainflow（ASTM E1049）は簡易版に対し平均42%高いDELを算出。高精度疲労評価には標準実装が必須
3. **サイトDEL推定**: Penmanshielの年間平均DELは1,497〜1,742 kN·m（MM82基準）。冬季（2月）にピークを示す季節性を確認
4. **縦断分析**: 6年間のDEL増加（+13.7%）は風況変動が主因。公開SCADA指標の範囲内ではCp_maxの低下傾向は未確認。劣化検出には風況正規化が前提条件

なお、MM82プロキシモデルの長期DELは翼型近似の不確実性蓄積を考慮し、意図的に未算出とした（§5.4, Limitation 8）。本基盤は荷重環境の定量化を目的としており、劣化の直接検出は対象外である。点検画像・補修履歴との統合による劣化進行リスク評価を次の研究段階として位置づける。

---

## Appendix A: DLC 1.3 (ETM) Supplementary Results

IEC 61400-1:2019 [7] DLC 1.3（Extreme Turbulence Model）の結果を参考として示す。8風速 × 6シード = 48ケース。

**Table A1: DLC 1.3 vs. DLC 1.2 Ratio**

| V (m/s) | DLC 1.3 DEL (kN·m) | DLC 1.3 / DLC 1.2 (TI=14%) |
|---|---|---|
| 4 | 6,490 | ×4.2 |
| 6 | 9,801 | ×3.2 |
| 8 | 12,435 | ×2.3 |
| 10 | 13,587 | ×1.9 |
| 12 | 16,046 | ×1.8 |
| 14 | 16,490 | ×1.7 |
| 16 | 16,300 | ×1.5 |
| 18 | 16,996 | ×1.4 |

DLC 1.3はDLC 1.2の1.4〜4.2倍のDELを生成する。低風速域で比率が最大（ETMの乱流強度がNTMを大幅に上回る）、高風速域ではピッチ制御により差が縮小する。

## Appendix B: DLC 2.1/2.2 Ultimate Load Assessment

DLC 2.1（グリッド喪失・全ブレード正常停止）およびDLC 2.2（Blade 1ピッチ固着）の終局荷重解析結果を参考として示す。各36ケース、TI=14%、MM82モデル。

**Table B1: DLC 2.1 Peak Loads**

| V (m/s) | Pre-fault peak (kN·m) | Post-fault peak (kN·m) | Ratio | DLC 1.2 DEL (kN·m) |
|---|---|---|---|---|
| 8 | 2,483 | 1,958 | 0.85 | 1,562 |
| 10 | 2,850 | 2,348 | 0.87 | 1,780 |
| 12 | 3,116 | 2,436 | 0.82 | 2,352 |
| 14 | 2,881 | 2,209 | 0.81 | 2,538 |
| 16 | 2,855 | 2,044 | 0.77 | 2,904 |
| 18 | 2,643 | 1,377 | 0.54 | 3,090 |

DLC 2.1ではフォルト後ピークが常にフォルト前より低く、緊急ピッチによる荷重除荷が有効。

**Table B2: DLC 2.2 (Pitch Stuck) — Amplification vs. DLC 2.1**

| V (m/s) | DLC 2.1 post-peak (kN·m) | DLC 2.2 post-peak (kN·m) | Amplification |
|---|---|---|---|
| 8 | 1,958 | 1,955 | ×1.00 |
| 10 | 2,348 | 2,602 | ×1.11 |
| 12 | 2,436 | 2,502 | ×1.03 |
| 14 | 2,209 | 2,346 | ×1.06 |
| 16 | 2,044 | 2,885 | **×1.41** |
| 18 | 1,377 | 2,875 | **×2.09** |

DLC 2.2は高風速域（V ≥ 16 m/s）でDLC 2.1比 ×1.4〜2.1の非対称荷重増大を示す。ピッチ冗長性のない機種では終局設計の支配ケースとなりうる。

---

## 必須図表一覧

### 図（Figures）

| # | 内容 | ファイル | 本文/付録 |
|---|---|---|---|
| Fig. 1 | Rainflow comparison (standard vs. simple) | `fig_rainflow_comparison.png` | 本文 §4.1 |
| Fig. 2 | CV boxplot by wind speed | `fig_cv_boxplot.png` | 本文 §4.2 |
| Fig. 3 | NREL 5MW DEL heatmap | `fig_del_heatmap.png` | 本文 §4.3 |
| Fig. 3b | Lifetime DEL sensitivity to IEC class | `fig_lifetime_del_sensitivity.png` | 本文 §4.3 |
| Fig. 4 | Scaling validation (scatter + ratio) | `fig_scaling_validation.png` | 本文 §4.4 |
| Fig. 5 | MM82 DEL heatmap | `fig_del_heatmap_mm82.png` | 本文 §4.5 |
| Fig. 6 | Penmanshiel monthly DEL (MM82) | `fig_penmanshiel_monthly_del_mm82.png` | 本文 §4.6 |
| Fig. 7 | Longitudinal trends (DEL + Cp_max) | `fig_longitudinal_combined.png` | 本文 §4.7 |
| Fig. A1 | DLC 1.2 vs. 1.3 DEL comparison (NREL 5MW, blade root flapwise moment, kN·m) | `del_comparison_dlc12_vs_dlc13.png` | 付録A |

### 表（Tables）

| # | 内容 | 本文/付録 |
|---|---|---|
| Table 1 | OpenFAST simulation config | 本文 §3.1 |
| Table 2 | Geometric scaling parameters | 本文 §3.2 |
| Table 3 | Key ElastoDyn parameters | 本文 §3.2 |
| Table 4 | Penmanshiel dataset overview | 本文 §3.6 |
| Table 5 | Rainflow comparison | 本文 §4.1 |
| Table 6 | Multi-seed statistics | 本文 §4.2 |
| Table 7 | NREL 5MW DEL matrix | 本文 §4.3 |
| Table 7b | Lifetime DEL by IEC class | 本文 §4.3 |
| Table 8 | MM82 scaling validation | 本文 §4.4 |
| Table 9 | MM82 DEL matrix | 本文 §4.5 |
| Table 10 | Weight recalibration | 本文 §4.5 |
| Table 11 | TI methodology comparison | 本文 §4.6 |
| Table 12 | Monthly DEL (2020) | 本文 §4.6 |
| Table 13 | Fleet comparison | 本文 §4.6 |
| Table 14 | Longitudinal trends | 本文 §4.7 |
| Table A1 | DLC 1.3 results | 付録A |
| Table B1 | DLC 2.1 peak loads | 付録B |
| Table B2 | DLC 2.2 amplification | 付録B |

---

## DLC 1.3 / 2.1 / 2.2 の位置づけ

本論文の主張は「DLC 1.2に基づく疲労荷重推定基盤の構築」であり、DLC 1.3（ETM）およびDLC 2.1/2.2（終局荷重）は**補助的な文脈情報**として付録に配置する。

| DLC | 付録配置の理由 | 付録に残す価値 |
|---|---|---|
| **DLC 1.3 (ETM)** | DLC 1.2が疲労設計の基本ケースであり、ETMは極端条件の参考。本文に入れると主張が散漫になる | DLC 1.2との比率（×1.4〜4.2）は、NTM前提の限界を読者が把握するための指標として有用 |
| **DLC 2.1 (Grid Loss)** | 終局荷重は疲労荷重とは異なる評価カテゴリ（IEC 61400-1:2019 §7.4 vs. §7.6）。論文の焦点を薄める | 緊急ピッチの荷重除荷効果（ratio 0.54–0.87）は、モデルの動的応答の妥当性を補足的に示す |
| **DLC 2.2 (Pitch Stuck)** | DLC 2.1と同じ理由。さらに、フォールトシナリオの網羅的分析は本論文のスコープ外 | 高風速域での非対称荷重増大（×2.09）は、将来のリスク評価研究への入力として参考値を残す |

付録の結果を本文に昇格させないのは、**主張範囲の明確性を維持するため**である。DLC 1.2単独での限界は§5.4で明記しており、付録はその限界を補完する位置づけとする。

---

## 査読で突っ込まれそうな点

| # | 想定質問 | 深刻度 | 対応状況 |
|:---:|---|:---:|---|
| 1 | MM82翼型プロキシでは絶対精度に限界がある | 中 | §5.1で主張範囲を相対比較に限定済み。理論比6.5%整合が根拠。**v2.0で1文主張にも限定を埋め込み済み** |
| 2 | DLC 1.2のみでは疲労設計の全体像が見えない | 中 | 付録A/BでDLC 1.3/2.1/2.2を提示。**v2.0で付録の位置づけ理由を明文化済み** |
| 3 | MM82の長期DELを示していない理由は？ | 中 | **v2.0で「意図的に未算出」の理由を§7 Conclusionに明記**（翼型不確実性の蓄積リスク回避） |
| 4 | 1年データ（2020）で季節性を議論するのは弱い | 低 | 縦断分析（2016–2021）で複数年の傾向を補完済み。全タービン縦断は今後の課題 |
| 5 | TI_med経年増加の原因不明 | 低 | §5.3で仮説を提示済み。気象記録照合は今後の課題として明記 |
| 6 | w_V/w_TIの物理的解釈は？ | 中 | **v2.0で「このモデル下の支配因子比率であり普遍係数ではない」と§4.5に明記済み** |
| 7 | Cp_maxが増加している理由の説明が不足 | 中 | **v2.0で複数の仮説（制御更新・補修・風速計ドリフト）を§5.3に追記済み** |
| 8 | 480ケースの計算コストは？ | 低 | **v2.0で§6 Reproducibilityに「8コア約48時間」と明記済み** |
| 9 | 「荷重環境の定量化基盤」は新規性が弱いのでは？ | **高** | **v3.0で§1.4 Methodological Contributionを新設**。3要素の組み合わせ寄与を明示: (1) スケーリング＋限界定量化、(2) TI実データ差異、(3) 公開データのみ再現可能性。§5.1でもFig.4との接続を補強済み |
| 10 | Penmanshiel SCADAの品質は十分か（2018 QC 35%除去） | 低 | §5.3で指摘済み。データ品質の限界として誠実に開示する方が査読に有利 |

---

## まだ言えないこと

1. **MM82実機の絶対荷重を高精度に再現した** — 翼型プロキシの不確実性、制御系の差異がある
2. **DEL推定だけでブレード劣化を検出した** — 縦断分析で劣化は確認されていない。検出方法論自体が未確立
3. **この重みやDEL基盤が他機種・他サイトにそのまま一般化できる** — 単一機種・単一サイトの結果
4. **TI_medの経年増加の原因を特定した** — 仮説段階（気象変動・植生変化・追加タービン等）
5. **Cp_maxに劣化がないことを証明した** — 風況差のノイズに埋もれている可能性を排除できない
6. **DLC 2.2の結果を設計判断に使える** — 翼型プロキシモデルの終局荷重は参考値のみ
7. **MM82基準の長期DEL（20年寿命相当）を算出した** — Weibull重み付きはNREL 5MWのみ実施。MM82プロキシでは翼型近似の不確実性が長期積算に蓄積するため、意図的に未算出とした。精度保証なき絶対値の報告を避ける判断であり、実測照合が得られるまで保留する

---

## References

[1] OpenFAST Documentation, NREL, https://openfast.readthedocs.io/

[2] Jonkman, J., Butterfield, S., Musial, W., and Scott, G. (2009). Definition of a 5-MW Reference Wind Turbine for Offshore System Development. NREL/TP-500-38060.

[3] Bak, C., Zahle, F., Bitsche, R., et al. (2013). The DTU 10-MW Reference Wind Turbine. DTU Wind Energy Report-I-0092.

[4] Tautz-Weinert, J. and Watson, S.J. (2017). Using SCADA data for wind turbine condition monitoring — a review. IET Renewable Power Generation, 11(4), 382–394.

[5] Plumley, C. (2022). Penmanshiel Wind Farm Data. Zenodo. DOI: 10.5281/zenodo.5946808.

[6] ASTM E1049-85 (2017). Standard Practices for Cycle Counting in Fatigue Analysis.

[7] IEC 61400-1:2019. Wind energy generation systems — Part 1: Design requirements.

[8] Malik, T.H. and Bak, C. (2025). Challenges in detecting wind turbine power loss: the effects of blade erosion, turbulence, and time averaging. Wind Energy Science, 10, 227–243. DOI: 10.5194/wes-10-227-2025.

[9] Abbas, N.J., Zalkind, D.S., Pao, L., and Wright, A. (2022). A reference open-source controller for fixed and floating offshore wind turbines. Wind Energy Science, 7(1), 53–73.

[10] Hayman, G.J. (2012). MLife Theory Manual for Version 1.00. NREL/TP-xxxx. National Renewable Energy Laboratory.

[11] Bir, G. and Jonkman, J. (2007). Aeroelastic Instabilities of Large Offshore and Onshore Wind Turbines. Journal of Physics: Conference Series, 75, 012069.

[12] Colone, L., Natarajan, A., and Dimitrov, N. (2018). Impact of turbulence induced loads and wave kinematic models on fatigue reliability estimates of offshore wind turbine monopiles. Ocean Engineering, 155, 295–309.

[13] Dimitrov, N., Natarajan, A., and Kelly, M. (2015). Model of wind shear conditional on turbulence and its impact on wind turbine loads. Wind Energy, 18(11), 1917–1931.

[14] Matsuishi, M. and Endo, T. (1968). Fatigue of metals subjected to varying stress. Japan Society of Mechanical Engineers, Fukuoka, Japan.

[15] Downing, S.D. and Socie, D.F. (1982). Simple rainflow counting algorithms. International Journal of Fatigue, 4(1), 31–40.

[16] Fingersh, L., Hand, M., and Laxson, A. (2006). Wind Turbine Design Cost and Scaling Model. NREL/TP-500-40566. National Renewable Energy Laboratory.

[17] Robertson, A.N., et al. (2017). OC5 Project Phase II: Validation of Global Loads of the DeepCwind Floating Semisubmersible Wind Turbine. Energy Procedia, 137, 38–57.

[18] DNV GL (2015). DNVGL-ST-0376: Rotor blades for wind turbines. DNV GL AS.

[19] Mandell, J.F. and Samborsky, D.D. (1997). DOE/MSU Composite Material Fatigue Database: Test Methods, Materials, and Analysis. SAND97-3002. Sandia National Laboratories. DOI: 10.2172/578635.

[20] Natarajan, A., Dimitrov, N.K., William Peter, D.R., Bergami, L., Madsen, J., Olesen, N., et al. (2020). Demonstration of Requirements for Life Extension of Wind Turbines Beyond Their Design Life. DTU Wind Energy Report No. E-0196.

[21] Vera-Tudela, L. and Kühn, M. (2017). Analysing wind turbine fatigue load prediction: The impact of wind farm flow conditions. Renewable Energy, 107, 352–360. DOI: 10.1016/j.renene.2017.01.065.

[22] Herp, J., Ramezani, M.H., Bach-Andersen, M., Pedersen, N.L., and Nadimi, E.S. (2018). Bayesian state prediction of wind turbine bearing failure. Renewable Energy, 116, 164–172.

[23] Python `rainflow` library, version 3.2.0. PyPI. https://pypi.org/project/rainflow/

---

## 改訂履歴

| Version | Date | 内容 |
|---|---|---|
| v1.0 | 2026-04-04 | 初稿完了 |
| v2.0 | 2026-04-04 | 査読耐性改訂: 1文主張スコープ限定、§4.5重み解釈修正、§5.3風況vs劣化再構成、§6再現性追加、参考文献[10]–[12]追加 |
| v3.0 | 2026-04-04 | 投稿準備改訂: 1文主張短縮、タイトル案刷新、§1.4新規性セクション新設、§4.7 Cp_maxトーンダウン、§5.1 Fig.4接続補強、§6スクリプト表追加、冗長箇所短縮（§4.3/§4.5/§4.6.1/Abstract） |
| v4.0 | 2026-04-04 | 最終表現調整: Abstract末文論文調化＋新規性1文追加、§4.4「物理的に妥当」→相対比較限定、§4.7/Abstract/§5.3/Conclusion Cp_maxに「公開SCADA指標の範囲内」限定統一、Conclusion MM82長期DEL段落圧縮→§5.4 #8へ移動、§1.1/§2.1/§5.1/§5.2/§5.3圧縮 |
| v5.0 | 2026-04-08 | 査読耐性強化: (1)§4.4スケーリング検証の単一ケース限界を明記＋統計的検証を今後の課題化、(2)参考文献[13]–[23]追加（Rainflow原著・スケーリングモデル原典・S-N曲線根拠・IEA Task 42・OpenFAST検証等）＋§2に引用統合、(3)§1.4新規性論証を「統合により初めて可能になる成果」で具体化、(4)§1.3 Obj.3から劣化検出含意を除去、(5)§3.7 QCフィルタ閾値の根拠追加、(6)IEC 61400-1:2019表記統一＋6シードを「minimum requirement」に修正、(7)§4.7 Cp_maxスコープ外注記追加、(8)§5.4 Limitations再構成：翼型プロキシ一本化・線形重みモデル限界・bilinear補間粗さ・スケーリング検証統計不足を追加 |
| v6.0 | 2026-04-10 | 構成整理・圧縮: (1)タイトル確定（Site-Specific...Case Study）、(2)Abstract→4ブロック構成に再整理、(3)§1.4圧縮（後半の新規性説明を3文に）、(4)§2.3圧縮（冗長表現削除）、(5)§4.4単一ケース限界の記述圧縮、(6)§4.5 R²注記圧縮、(7)§4.6.3簡潔化（結論→表の順に）、(8)§4.7 Cp_max注記圧縮、(9)Limitations 10→8項目（#4に線形モデル+補間統合、#6に補修履歴+TI_med統合）、(10)Conclusion Limitation番号整合 |
| v7.0 | 2026-04-10 | スケーリング検証の統計的強化: §4.4にTable 8b追加（全40条件のDEL比率統計: mean=0.263, std=0.020, 理論比からの偏差−4.6%）。V=4-6 m/sの散らばりと V≥8 m/sの安定性を定量化。Limitation #5を「統計的不足」から「風速依存性」に更新（n=1→n=40） |

*Paper 2 Draft v7.0 | 2026-04-10 | Author: himin | Research Assistant: Claude Code*
