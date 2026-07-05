# Paper 2: OpenFASTスケーリングモデルと公開SCADAを用いたSenvion MM82風車の長期疲労荷重推定基盤の構築

**ステータス**: v10.1（Codex 独立レビュー（2026-07-03）の指摘反映：集約値の意味の注記追加、「主因」→「整合的」への弱化、クリップ率の定量開示、§4.6.4 仮説の実測訂正、図生成スクリプトの v2 CSV 切替）
**最終更新**: 2026-07-03（v10.0 で A-9 案b 採用・レコード別補間へ全面移行（年間DEL 1,393〜1,431 kN·m、トレンド +9.8%）→ v10.1 で Codex レビュー指摘を反映）

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

**どう作ったか**: NREL 5MW参照タービンのOpenFASTシミュレーション（DLC 1.2, 240ケース, ASTM E1049 Rainflow）でDELマトリクスを作成し、Senvion MM82への幾何スケーリング（λ_R = 0.651, 理論比との誤差6.5%）により機種適合DELマトリクスを生成した。これをPenmanshiel Wind Farm（2020年通年データを持つ5台, Zenodo公開SCADA）に適用し、10分値直接計測TIに基づく月次DELを算出した。

**主要結果**: 年間平均DELは1,393〜1,431 kN·m（5台のタービン間幅）で、冬季にピークを示す季節性を確認した。6年間の縦断分析（T01）では、DEL変動（2017→2020で+9.8%）は風況変動と整合的であり、公開SCADA指標の範囲内ではCp_maxの低下傾向は観察されなかった。

**何を主張しないか**: 本基盤は荷重環境の相対的な定量化を目的としており、絶対荷重精度の保証およびブレード劣化の直接検出は対象外である。

---

## 1. Introduction

### 1.1 Background

風車ブレードは20年以上の設計寿命を通じて繰り返し疲労荷重を受ける。IEC 61400-1:2019 [7] に規定されるDLC 1.2（正常乱流モデル, NTM）は疲労設計の基本ケースであり、ブレード根元のフラップ方向曲げモーメントが主要な疲労損傷チャンネルとなる。疲労等価荷重（DEL: Damage Equivalent Load）は、Rainflow計数法に基づいて算出され、材料のS-Nカーブ（Wöhler曲線）の指数mに依存する。

一方、ブレード表面の前縁エロージョン等の損傷は発電性能（AEP）の低下要因として近年注目されている [8]。エロージョンの検出は乱流強度や時間平均の扱いによって困難であり、軽度で-0.82%、重度で-1.46%、高TI条件下では-2.14%のAEP損失が報告されている [8]。本研究はまず疲労荷重の推定基盤を構築し、将来的には表面損傷（点検画像）との統合による劣化進行リスク評価を目指す（統合設計はPaper 3で議論）。

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
- **bin-averaged vs. 直接計測TIの実データ差異**: 約4倍の差を実サイトデータで確認（Vera-Tudela & Kühn 2017 [20] は全頁精読済（2026-06-11）で同種の TI 方法論比較を扱っていないことを確認。既存文献での同種指摘の有無の最終確定は Dimitrov et al. 2015 [12] の全頁精読後に行う）
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

OpenFASTはNRELが開発するオープンソースaeroelastic解析コードであり [1]、NREL 5MW参照タービン [2] は荷重評価研究の標準ベンチマークである。OpenFASTを含む複数の風力工学ツールはOC5プロジェクト等の第三者比較検証に参加しており、コード間の差異と実験との整合性が継続的に評価されている [16]（同プロジェクトはfloating semisubmersibleが対象で、本研究のonshore風車とは適用条件が異なる点に留意する）。Hayman (2012) はMLifeツールによるDEL算出手法（Downing & Socie (1982) のone-pass Rainflow計数、等価サイクル数正規化）を体系化した [10]。Rainflow計数法の原理はMatsuishi & Endo (1968) [13] に遡り、Downing & Socie (1982) [14] が計算アルゴリズムを体系化した。ASTM E1049-85 [6] はこのアルゴリズムを業界標準として整理した規格であり、本研究は同規格準拠のPython `rainflow` 3.2.0 [22] を使用する。ただし、荷重時系列からサイト固有の長期DELへ接続するパイプラインは標準化されておらず、TI計測精度への依存が大きい。

### 2.2 Reference Turbine Scaling

Bak et al. (2013) はDTU 10MW参照タービンの設計にあたり、幾何スケーリングの背景（Mass ~ Diameter^3 の古典的関係）を紹介した [3]。Fingersh et al. (2006) はNRELの風車設計コスト・スケーリングモデルにおいて、ブレード質量のスケーリング則としてbaseline = 0.1452 × R^2.9158、advanced = 0.4948 × R^2.53 per blade を提示した [15]。Bak et al. (2013) もglass fiber: Mass = 0.0023 × Length^2.17、carbon fiber: Mass = 9×10^-5 × Length^2.95 を報告している [3]。本研究ではブレード質量密度のスケーリング指数として**λ_R^2.3**を採用した。これはFingersh (2006) とBak (2013) の報告値の範囲内の経験的選択（glass fiber設計とカーボン強化設計の中間的想定）であり、特定の文献から導出された値ではない点に注意する（§5.4 Limitation 1参照）。断面剛性はR^4でスケーリングする経験則と合わせ、これらが広く用いられている。ただし、翼型データの機種固有性（メーカー独自設計で非公開の場合が多い）がスケーリング精度の主要な不確実性要因となり、幾何スケーリングのみでは動的応答の精密な再現に限界がある。本研究はこの限界を前提とし、スケーリングモデルの主張範囲を相対比較に限定する。

### 2.3 SCADA-Based Fatigue Monitoring

SCADAベースの風車状態監視はTautz-Weinert & Watson (2017) [4] がレビューしている。SCADAからDELを推定するアプローチは、DELマトリクスの機種依存性とTI計測精度の問題から限定的である。Vera-Tudela & Kühn (2017) [20] はSCADA信号からの疲労荷重予測を実証し、Dimitrov et al. (2015) [12] は乱流強度が荷重に与える影響を定量化した。Colone (2018) [11] は wind farm scale で運用 SCADA（pitch alarm log）と aeroelastic simulation を組み合わせた fatigue load mapping の枠組みをPCE surrogate modelで構築し、turbulence と wake angle が blade root flapwise DEL の主要 driver であることをSobol感度解析で示した。Herp et al. (2018) [21] はベイズ推定による故障予測を試みている。DTU 主導の EUDP LifeWind project (Natarajan et al. 2020) [19] は、SCADA + aeroelastic + ML を組み合わせた寿命延長評価の体系化を行い、策定中の IEC 61400-28 標準への入力資料となっている。本研究は同方法論的文脈に位置づけられる。

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

NREL 5MW参照タービン（R=63 m, P=5 MW, Tower top/TurbSim RefHt=87.6 m, Hub Height=90 m）からSenvion MM82（R=41 m, P=2.05 MW, HH=59 m）への幾何スケーリングを実施した。Jonkman et al. (2009) [2] のTable 1-1ではNREL 5MWのHub Heightは90 mと定義されており、87.6 mはtower top（yaw bearing）高さである。本研究ではOpenFASTのTowerHt入力およびTurbSim RefHtに87.6 mを採用し、scaling係数 λ_H = 59/87.6 を用いた。Table 2にスケーリング係数を示す。

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
| m (S-N exponent) | 10 (GFRP; DNVGL-ST-0376 [17]）* |
| T_eq | 600 s |
| N_eq | 1 Hz × T_eq = 600 cycles* |
| Transient removal | First 60 s skipped |

*N_eq (equivalent cycle count) is the product of an assumed reference frequency (1 Hz) and the equivalent time period T_eq = 600 s, yielding N_eq = 600 equivalent cycles per simulation. The DEL normalization framework (the structure DEL = (Σ n_i ΔS_i^m / N_eq)^(1/m), where N_eq corresponds to f^eq × T_j in Hayman (2012) [10] Eq. 26) follows Hayman (2012). The specific values f^eq = 1 Hz and T_eq = 600 s are conventional choices consistent with the 10-minute simulation duration standardized in IEC 61400-1:2019 [7], and ensure that DEL values are normalized to a consistent reference cycle count across all simulations.

**S-N exponent m = 10 の根拠**: GFRP（glass fiber reinforced polymer）風車ブレードの疲労設計では、m = 10 が慣用的に採用される。本研究では DNVGL-ST-0376 [17] が風車ブレードの疲労評価に推奨する m = 10 をそのまま採用する。実験的支持として、Mandell & Samborsky (1997) [18] の DOE/MSU データベースは GFRP の "best-case fiberglass response" を semi-log 表現 S/S₀ = 1 − b·log N（同 [18] Eq. 6）における fatigue coefficient **b = 0.10** と報告している（同 [18] Fig. 13(b), Fig. 18, Fig. 24、および繊維含有率 30–42% 帯の D155B / D092D / A130C 等で b ≈ 0.090–0.108 を実測）。同データベースの log-log 表現 S/S₀ = B·N^(−1/n)（同 [18] Eq. 7）では、R = 0.1 の longitudinal データに対し n = 11.6（10³–10⁸ cycles, [18] Table 12）と報告される。両表現は数学的に厳密に等価ではないが、いずれも DNVGL-ST-0376 推奨値 m = 10 と同等のオーダーにあり、本研究の m = 10 採用と整合する。

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
| Number of turbines | 14 (numbered T01–T15, no T03; this study: 5 turbines)* |
| Time resolution | 10-min averages |
| Period | 2016–2021 (main analysis: 2020 full year) |
| Location | Penmanshiel, Scotland (onshore) |
| Commissioning | September 2016 |

*The farm's turbines are numbered T01–T15 with no T03 (14 units; Zenodo static metadata). The fleet analysis (§4.6) uses the five turbines with complete 2020 monthly coverage after QC filtering (T01, T02, T04, T05, T06). T07 (6 months) and T11 (3 months) had only partial 2020 coverage in the processed dataset and were excluded from annual inter-turbine statistics; the remaining turbines had substantially higher missing-data rates and were excluded to ensure consistent monthly DEL estimation.

TIはIEC 61400-1:2019 [7] 準拠の10分値直接計測:

```
TI = σ_V,10min / V_10min
```

SCADAに "Wind speed, Standard deviation (m/s)" 列が直接提供されており、bin近似を経由しない。

### 3.7 Site DEL Estimation Pipeline

サイトDEL推定は以下の手順で実施する（実装: `phase3_scada/penmanshiel_del_perrecord.py`）:

1. SCADAの各10分レコードについてV_10minとTI_directを取得
2. **各10分レコードごとに**DELマトリクスからbilinear interpolationでDEL(V, TI)を推定
3. 月次・年次で集計し、時系列トレンドを評価

集計の定義は以下の通りとする。

- **月次DEL（タービン別）**: 当月のQC通過レコードのDEL値の単純平均
- **フリート月次DEL**: 対象タービンの月次DEL値の単純平均（タービン等価重み。欠測率の差による偏りを避けるため、レコード合算ではなくタービン別月次値を平均する）
- **年間DEL**: 利用可能な月次DEL値の単純平均（月等価重み）

**集約値の意味に関する注記**: 上記の月次・年間値は10分DELの**算術平均**であり、荷重環境の相対比較のための指標である。損傷等価の意味での期間DEL（べき平均 mean(DEL^m)^(1/m)、m = 10）とは異なる。後者は高荷重レコードに支配されるため大幅に高い値となり（T01 2020年の試算で算術平均比 約+85%）、寿命評価目的の集約にはべき平均が適切となる。本研究の主張範囲（月次・台間の相対比較）では算術平均を採用し、損傷等価集約への拡張は今後の課題とする（§5.4, Limitation 5）。

**グリッド範囲外レコードの取り扱い**: DELマトリクスの格子範囲は V = 4〜18 m/s、TI = 8〜20% である。範囲外のレコードは補間前に格子境界へクリップする（例: カットイン風速 3.5 m/s 以上・格子下限 4 m/s 未満のレコードは V = 4 m/s として評価される）。2020年の5台ではQC通過レコードの約19%（V軸 約8%、TI軸 約13%）が少なくとも一軸でクリップの対象となる。クリップは分布の裾の荷重寄与を平坦化する方向に働くが、月次・年次の相対比較を主張範囲とする本研究では許容可能と判断した（§5.4, Limitation 5）。なお、月次集計値（V_mean, TI_median）の点で一回だけ補間する簡便法との比較を §4.6.4 に示す。

品質管理（QC）: 以下の閾値でレコードを除外した。

- **V < 3.5 m/s**: Senvion MM82のカットイン風速（3.5 m/s）未満であり、発電運転外のデータを排除
- **P < 0**: 発電運転中に負の出力は物理的に発生しないため、停止中・消費電力モードのレコードを除外
- **TI > 0.5**: IEC 61400-1:2019 [7] のNTMモデルにおいて想定されるTI範囲を大幅に超過する値（TI=50%は極端な非定常状態を示す）。工学的判断に基づく外れ値除去閾値として設定（下限 TI < 0.005 も同時に除外）

2018年のQCによる除去率は35%と高く、主にV < 3.5 m/s（カットイン以下の低風速期間）が主要因であった。この高い除去率はデータ品質の限界を示しており、§5.3で議論する。

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

*Error is defined as |DEL_standard − DEL_simple| / DEL_standard × 100% (40 single-seed cases). A mean error of 42% relative to the standard value corresponds to the standard implementation yielding on average ~1.7× the simple-count DEL.*

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

**Table 12: Penmanshiel Monthly DEL — Fleet Average (5 turbines, 2020, per-record interpolation)**

| Month | V_mean (m/s) | TI_median | DEL_est (kN·m) |
|---|---|---|---|
| Jan | 10.0 | 0.148 | 1,811 |
| Feb | 11.6 | 0.150 | 2,136 |
| Mar | 9.4 | 0.137 | 1,616 |
| Apr | 6.6 | 0.140 | 1,037 |
| May | 7.4 | 0.139 | 1,203 |
| Jun | 8.3 | 0.133 | 1,360 |
| Jul | 7.0 | 0.143 | 1,163 |
| Aug | 7.3 | 0.134 | 1,138 |
| Sep | 7.9 | 0.142 | 1,363 |
| Oct | 8.1 | 0.123 | 1,282 |
| Nov | 8.8 | 0.133 | 1,501 |
| Dec | 8.7 | 0.123 | 1,388 |

*各列は5台のタービン別月次値（§3.7 の定義）の単純平均。*

年間平均DEL: 1,393〜1,431 kN·m（2020年通年データを持つ5台のタービン間幅）。ピーク月: 2月（冬季北海低気圧による強風、タービン別月次の最大は2,156 kN·m = T01）。

> Figure 6: Penmanshiel monthly mean DEL (MM82 basis), 2020  
> → `fig_penmanshiel_monthly_del_mm82.png`

#### 4.6.3 Fleet Comparison (2020)

台間DEL比較（5台, 2020年）の結果をTable 13に示す。DELの台間変動幅は1,393〜1,431 kN·m（2.7%）と小さく、フリート内の荷重環境は均質である。AEPの台間差（最大-3.5%）は主に風速差（V_mean: 0.3 m/s）に帰属される。

**Table 13: Penmanshiel Fleet Performance (2020)**

| Turbine | V_mean (m/s) | Cp_max | AEP_est (MWh) | Annual DEL (kN·m) |
|---|---|---|---|---|
| T01 | 7.62 | 0.451 | 6,506 | 1,422 |
| T02 | 7.41 | 0.445 | 6,113 | 1,431 |
| T04 | 7.45 | 0.451 | 6,381 | 1,413 |
| T05 | 7.32 | 0.444 | 6,010 | 1,424 |
| T06 | 7.30 | 0.447 | 6,129 | 1,393 |

*V_mean・Cp_max・AEP_est はQC前の全レコードに基づく性能統計（DEL集計とは母集団が異なる）。*

#### 4.6.4 Sensitivity to the Aggregation Method

§3.7 のレコード別補間（本研究の主法）に対し、月次集計値（V_mean, TI_median）の点で一回だけ補間する簡便法を参照として比較した。簡便法は本研究の主法に対し、タービン別月次DELで +1.4〜+14.8%（平均 +6.9%、2020年・5台・60タービン月）、2020年の年間DELで +5.7〜+8.1% 系統的に高い値を与えた。この差は、(a) DEL-V 曲線の局所的な曲率（V ≥ 8 m/s 域では上に凸に近く、平均点での評価がレコード別評価の平均を上回る方向に働く）を主要因とし、(b) 格子境界へのクリップ（QC通過レコードの約19%が対象、§3.7）も寄与しうる複合効果と考えられる（仮説）。なお、QC通過レコードにおける V と TI の相関は弱い正（Pearson r ≈ +0.11、2020年5台）であり、V-TI 相関の寄与は小さいとみられる。

重要な点として、季節パターン（2月ピーク）とフリート均質性（台間幅 約3%）は両方法で保存された。すなわち本研究の主張範囲である相対比較の結論は集計方法の選択に対して頑健であるが、**絶対値は集計方法の選択だけで約7%変動する**。これは翼型プロキシ（§5.1）と並ぶ絶対値の不確実性要因であり、絶対荷重を扱う後続研究では集計方法の明示が不可欠である。比較の詳細は `tools/reference_audit/paper123_consistency_audit_2026-07-02.md`（A-9）に記録した。

### 4.7 Longitudinal Analysis (T01, 2016–2021)

**Table 14: T01 Longitudinal Trends (per-record interpolation)**

| Year | Period | V_mean (m/s) | TI_med | DEL_annual (kN·m) | Cp_max |
|---|---|---|---|---|---|
| 2016 | Jun–Dec | 7.67 | 0.114 | 1,117 | 0.412 |
| 2017 | Full year | 8.35 | 0.119 | 1,295 | 0.428 |
| 2018 | Full year | 8.16 | 0.127 | 1,289 | 0.443 |
| 2019 | Full year | 8.10 | 0.129 | 1,303 | 0.450 |
| 2020 | Full year | 8.66 | 0.133 | 1,422 | 0.451 |
| 2021 | Jan–Jun | 7.94 | 0.132 | 1,276 | 0.454 |

*Notes*: (a) 2016年のデータは6月から存在するが、営業運転開始日（Commercial Operations Date）は2016-09-01であり（Zenodo static metadata）、6〜8月は営業運転開始前の期間を含む。(b) V_mean・TI_medは当年のQC通過レコードに対する統計量、DEL_annualは月次DELの単純平均（§3.7）。Table 12–14は単一のパイプライン（`penmanshiel_del_perrecord.py`）による統一集計であり、旧版に存在したフリート解析と縦断解析のスクリプト差（T01 2020: 1,503 vs 1,507）は解消されている。

2017→2020のDEL増加（+127 kN·m, +9.8%）はV_mean増加（8.35→8.66 m/s）とTI_med増加（0.119→0.133）に連動している。2018〜2019年はV_meanが2017年を下回り、DELもほぼ横ばい（1,289〜1,303 kN·m）であった。2021年はV_meanの低下とともにDELも1,276 kN·mと2017年水準（1,295 kN·m）近くまで戻った。

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

1. **DEL増加（2017→2020で+9.8%）は、同期間のV_meanおよびTI_medの増加と連動しており、風況変動で説明可能な範囲内にある**
2. **公開SCADAで利用可能な指標の範囲内では、Cp_maxの低下傾向は確認されない**（2017→2021: 0.428→0.454と増加傾向）

ただし、「劣化が存在しない」と結論づけることはできない:

- 微小なCp低下が風況年変動のノイズ（ΔV_mean ~0.6 m/s）に埋もれている可能性がある
- Cp_max増加およびTI_med経年増加（0.119→0.133）の原因が未特定（制御更新、補修、風速計ドリフト等）
- 2018年のQC除去率35%がデータ品質の限界を示す

本分析が示しているのは、**DELトレンドを解釈する前に風況正規化が不可欠であること**、および**公開SCADAのみでは劣化検出には証拠が不足すること**である。劣化検出には、風況正規化に加え、点検画像・補修履歴との統合が必要となる。

### 5.4 Limitations

1. **翼型プロキシによる空力近似**: MM82の翼型データは非公開であり、NREL 5MWの翼型をプロキシとして使用した。本モデル最大の不確実性要因であり、DEL絶対値の精度、w_V/w_TI較正（§4.5）、高TI条件での相対比較精度（§5.1）に影響する。このため主張範囲を相対比較に限定した
2. **スケーリング指数λ_R^2.3の経験的選択**: ブレード質量密度のスケーリング指数として2.3を採用したが、これはFingersh (2006) のbaseline 2.9158 / advanced 2.53、Bak (2013) のglass 2.17 / carbon 2.95 の範囲内での経験的選択であり、特定の一次文献から直接導出された値ではない。採用値（指数2.3相当、比率0.372）はこの範囲の中央付近に位置する。この選択は本研究の数値結果（DEL比率0.263）に影響を与えているが、相対比較を主張範囲とする本研究においては許容可能な不確実性と判断した
3. **DLC 1.2のみ**: 疲労設計には複数DLC（1.1, 1.2, 1.3等）の重み付き合成が必要。本研究はDLC 1.2単独
4. **単一サイト**: Penmanshielの結果を他サイトに一般化するには追加検証が必要
5. **線形重みモデルとbilinear補間**: DEL-V関係は非線形であるが、支配因子比率の把握を目的に線形近似を使用した（R² = 0.926–0.943）。DELマトリクスの8×5グリッドからのbilinear補間もグリッド端部で精度が低下する。また格子範囲外（V < 4 / V > 18 m/s、TI < 8% / TI > 20%）のレコードは境界にクリップして評価しており（QC通過レコードの約19%が対象）、分布の裾の荷重寄与は平坦化される（§3.7）。さらに集計方法の選択だけで年間DELの絶対値が約7%変動し（§4.6.4）、月次・年間値は10分DELの算術平均（荷重環境指標）であって損傷等価集約（m乗平均、算術平均比 約+85%）ではない（§3.7）。いずれも局所的な予測精度・絶対値精度に限界があることを示す
6. **スケーリング比率の風速依存性**: 全40条件のDEL比率は平均0.263（理論0.276に対し−4.6%）だが、V=4–6 m/sでは散らばりが大きい（0.208–0.326）。低風速域での相対比較精度は限定的である（§4.4 Table 8b）
7. **縦断分析の制約**: 補修履歴が未入手のため、Cp_maxに劣化が見られない原因として補修実施の可能性を排除できない。TI_medの経年増加（0.119→0.133）の原因も気象記録との照合が未実施（§5.3で議論）
8. **構造応答の線形性仮定**: スケーリング則は線形弾性範囲を仮定。非線形挙動は考慮していない
9. **MM82長期DEL未算出**: MM82プロキシでは翼型近似の不確実性が長期積算に蓄積するため、意図的に未算出とした。実測荷重との照合が得られた段階で実施すべき課題である

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
| 重み較正 | `scripts/calibrate_weights.py` | LinearRegression（正値制約・切片なし） |
| サイトDEL（QC・補間・集計） | `phase3_scada/penmanshiel_del_perrecord.py` | レコード別bilinear補間 + 月次・年次DEL集計（§3.7の定義を単一スクリプトで実装） |
| 図表生成 | `scripts/paper2_figures.py` | 全Figure再生成 |

---

## 7. Conclusion

本研究は、NREL 5MW参照タービンからSenvion MM82への幾何スケーリング（λ_R = 0.651）とPenmanshiel公開SCADAの10分値TI直接計測を組み合わせることで、実サイトの長期疲労荷重推定基盤を再現可能な形で構築した。

主な成果:

1. **スケーリング妥当性**: MM82プロキシモデルのDEL比率（0.258）は理論予測（0.276）と6.5%の誤差で整合し、相対比較に有効な精度を持つ
2. **Rainflow実装精度**: 簡易Rainflow（ハーフサイクルカウント）は標準Rainflow（ASTM E1049）に対しDELを平均42%過小評価する（標準値基準、40ケース）。高精度疲労評価には標準実装が必須
3. **サイトDEL推定**: Penmanshielの年間平均DELは1,393〜1,431 kN·m（2020年通年5台, MM82基準, レコード別補間）。冬季（2月）にピークを示す季節性を確認。集計方法の選択による絶対値の変動は約7%（§4.6.4）
4. **縦断分析**: 6年間のDEL変動（2017→2020で+9.8%）は同期間の風況変動（V_mean・TI_med）と整合的。公開SCADA指標の範囲内ではCp_maxの低下傾向は未確認。劣化検出には風況正規化が前提条件

なお、MM82プロキシモデルの長期DELは翼型近似の不確実性蓄積を考慮し、意図的に未算出とした（§5.4, Limitation 9）。本基盤は荷重環境の定量化を目的としており、劣化の直接検出は対象外である。点検画像・補修履歴との統合による劣化進行リスク評価を次の研究段階として位置づける。

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

[11] Colone, L. (2018). Cost-Effective Strategies for Wind Farm O&M: Topics in Structural Reliability, Load Analysis, Predictive Maintenance and Decision Making. PhD thesis, DTU Wind Energy PhD-0088. Technical University of Denmark. DOI: 10.11581/DTU:00000033.

[12] Dimitrov, N., Natarajan, A., and Kelly, M. (2015). Model of wind shear conditional on turbulence and its impact on wind turbine loads. Wind Energy, 18(11), 1917–1931.

[13] Matsuishi, M. and Endo, T. (1968). Fatigue of metals subjected to varying stress. Japan Society of Mechanical Engineers, Fukuoka, Japan.

[14] Downing, S.D. and Socie, D.F. (1982). Simple rainflow counting algorithms. International Journal of Fatigue, 4(1), 31–40.

[15] Fingersh, L., Hand, M., and Laxson, A. (2006). Wind Turbine Design Cost and Scaling Model. NREL/TP-500-40566. National Renewable Energy Laboratory.

[16] Robertson, A.N., et al. (2017). OC5 Project Phase II: Validation of Global Loads of the DeepCwind Floating Semisubmersible Wind Turbine. Energy Procedia, 137, 38–57. DOI: 10.1016/j.egypro.2017.10.333

[17] DNV GL (2015). DNVGL-ST-0376: Rotor blades for wind turbines. DNV GL AS.

[18] Mandell, J.F. and Samborsky, D.D. (1997). DOE/MSU Composite Material Fatigue Database: Test Methods, Materials, and Analysis. SAND97-3002. Sandia National Laboratories. DOI: 10.2172/578635.

[19] Natarajan, A., Dimitrov, N.K., William Peter, D.R., Bergami, L., Madsen, J., Olesen, N., et al. (2020). Demonstration of Requirements for Life Extension of Wind Turbines Beyond Their Design Life. DTU Wind Energy Report No. E-0196.

[20] Vera-Tudela, L. and Kühn, M. (2017). Analysing wind turbine fatigue load prediction: The impact of wind farm flow conditions. Renewable Energy, 107, 352–360. DOI: 10.1016/j.renene.2017.01.065.

[21] Herp, J., Ramezani, M.H., Bach-Andersen, M., Pedersen, N.L., and Nadimi, E.S. (2018). Bayesian state prediction of wind turbine bearing failure. Renewable Energy, 116, 164–172.

[22] Python `rainflow` library, version 3.2.0. PyPI. https://pypi.org/project/rainflow/

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
| v8.0 | 2026-04-14 | 引用整合性修正（PDF精読による発見）: (1)§1.1 Malik 2025引用文脈修正（疲労荷重×エロージョン複合→AEP検出の文脈に訂正）、(2)§2.2 Fingersh/Bakスケーリング指数訂正（Fingersh 2006: R^2.9158/2.53、Bak 2013: Length^2.17/2.95を明記）、(3)§3.4 Mandell 1997からのm=10導出を明示（b=0.10→n=10の変換経路）、(4)§3.2 HH曖昧性解消（Jonkman Table 1-1のHub Height=90m、TowerHt=87.6mを明確化）、(5)§5.4 Limitationに「スケーリング指数λ_R^2.3の経験的選択」を追加（#2として挿入、以降番号シフト） |
| v9.0 | 2026-04-26 | 引用ハルシネーション修正: (1)§2.2 Bir & Jonkman 2007 [11]の引用を削除（PDF全頁精読の結果、論文主題はNREL 5MW aeroelastic stability解析であり、引用文「スケーリング則の限界」「翼型空力データの機種固有性」「幾何スケーリング限界」は論文中に該当議論なしと確認）、(2)文章を一般論として再記述、(3)参考文献[12]–[23]を[11]–[22]に繰り上げ＋本文中の引用番号を全て更新（[12]→[11], [13]→[12], ... [23]→[22]）。さらに(4)§参考文献[16]Robertson 2017 DOI追加（10.1016/j.egypro.2017.10.333、Crossref API検証で旧DOI .10.371は別論文を指していたと判明） |
| v9.1 | 2026-04-26 | Robertson 2017 引用文の弱体化（全頁精読による発見）: §2の「OpenFASTの妥当性はOC5プロジェクト等の第三者検証で確認されている」を「OpenFASTを含む複数の風力工学ツールはOC5プロジェクト等の第三者比較検証に参加しており、コード間の差異と実験との整合性が継続的に評価されている」に修正。OC5 Phase IIはfloating semisubmersibleが対象でonshore風車とは適用条件が異なる旨を併記。論文の実態は10-21%の過小評価（妥当性確認ではなく課題発見）であるため誇張表現を回避 |
| v9.2 | 2026-04-26 | §3.4「m = 10 の根拠」表現精緻化（Mandell 1997 pp.1-100 主張駆動精読による発見）: 旧版「Mandell 1997 から導出した m=10（b=0.10 → n=10 の変換経路）」「n = 1/b = 10 に相当する（b = 0.10〜0.14、n = 7〜10）」という単純逆数変換は Mandell 1997 内に直接的な変換式が存在しないことを反映し削除。新版では (1) DNVGL-ST-0376 を直接の出典として明確化、(2) Mandell 1997 [18] の b = 0.10 を独立した実験的支持として位置づけ（Fig. 13(b), Fig. 18, Fig. 24 と繊維含有率 30-42% 帯の D155B/D092D/A130C 実測値 b ≈ 0.090-0.108 を引用根拠として明示）、(3) Mandell の log-log 表現（Eq. 7）における実測 n = 11.6（Table 12, R=0.1, 10³-10⁸ cycles）も併記、(4) 両表現が数学的に等価ではないが m = 10 と同等のオーダーにあると明記 |
| v9.3 | 2026-04-26 | Hayman 2012 全頁精読による §2/§3.4 表現精緻化: (1)§2の「Hayman (2012) はMLifeツールによるDEL算出手法（ASTM E1049準拠Rainflow、等価サイクル数正規化）を体系化した」を「Hayman (2012) はMLifeツールによるDEL算出手法（Downing & Socie (1982) のone-pass Rainflow計数、等価サイクル数正規化）を体系化した」に修正し、ASTM E1049-85 を別文で「Downing & Socie アルゴリズムを業界標準として整理した規格」として分離記述。理由：Hayman 2012 はASTM E1049ではなく明示的に Downing & Socie (1982) を引用しており、ASTM E1049 が Hayman 2012 から直接来ているかのような誤解を回避。(2)§3.4 の「This convention follows Hayman (2012)」を「The DEL normalization framework (...) follows Hayman (2012). The specific values f^eq = 1 Hz and T_eq = 600 s are conventional choices consistent with the 10-minute simulation duration standardized in IEC 61400-1:2019」に修正。理由：Hayman 2012 内では f^eq, T_j は抽象パラメータとして定義されているのみで、N_eq=600 という具体値は論文内に存在しない。フレームワーク準拠と具体値選択の出典を分離 |
| v9.4 | 2026-04-27 | Colone 2018 全179頁完全精読による Reference [11] 差し替え＋引用文修正: (1)Reference [11] を Article I（Ocean Engineering 155:295-309, monopile fatigue reliability + IEC turbulence percentile + wave kinematic models）から PhD thesis 全体（DTU Wind Energy PhD-0088, DOI: 10.11581/DTU:00000033）に変更。理由：Article I は MC + HAWC2 aeroelastic simulation のみで SCADA データを使用せず、bin-averaged vs 直接計測 TI 比較も行っていないため、Paper 2 line 99/126 の主張の出典として不適切（引用文脈ハルシネーション）。PhD thesis 全体は Chapter 3 で wind farm scale の SCADA（pitch alarm log）と aeroelastic simulation の組み合わせによる fatigue load mapping を扱っており、line 126 の趣旨と整合する。(2)§2.3 line 126：「Colone et al. (2018) [11] はSCADAと空力シミュレーションの統合パイプラインを提案し、TI算出方法論の差異がDEL推定に大きく影響することを報告した」を「Colone (2018) [11] は wind farm scale で運用 SCADA（pitch alarm log）と aeroelastic simulation を組み合わせた fatigue load mapping の枠組みを PCE surrogate model で構築し、turbulence と wake angle が blade root flapwise DEL の主要 driver であることを Sobol 感度解析で示した」に修正。これは PhD thesis Chapter 3（§3.6 Wind farm load mapping）の実態（PCE surrogate, m=12 GFRP, DWM, Sobol indexes for blade root flapwise）と完全整合。(3)§2.3 末尾の「本研究の知見（bin近似 vs. 直接計測で4倍の差）はColone et al.の指摘を実データで裏付ける」を削除。Article I/PhD thesis ともに bin-averaged vs 直接計測比較は扱っていない。(4)§1.4 line 99：「既存文献の指摘（Colone et al. 2018 [11]）を裏付け」を「既存文献での同種指摘の有無は第10バッチで Vera-Tudela & Kühn 2017 / Dimitrov et al. 2015 を全頁精読後に確定」に書き換え。代替引用先は両論文取得後に確定 |
| v9.5 | 2026-04-27 | Natarajan 2020 LifeWind 全110頁完全精読による §2.3 line 126 のプロジェクト名ハルシネーション修正: 旧版「IEA Wind Task 42（寿命延長）[19] では、SCADAベースの荷重評価が寿命延長判断の重要な入力とされており、本研究はこの文脈に位置づけられる」を「DTU 主導の EUDP LifeWind project (Natarajan et al. 2020) [19] は、SCADA + aeroelastic + ML を組み合わせた寿命延長評価の体系化を行い、策定中の IEC 61400-28 標準への入力資料となっている。本研究は同方法論的文脈に位置づけられる」に修正。理由：参考文献 [19] (DTU Wind Energy E-0196) は Project no 64017-05114「Energy Technology Development and Demonstration Programme (EUDP)」資金による LifeWind project の成果報告書であり、IEA Wind Task 42 の output ではない（全110頁で IEA Wind Task 42 への言及なし、§5.3 で著者自身「The major EUDP Lifewind contributions」と明示）。書誌情報（著者・タイトル・年・出版者）は正しいが、所属プロジェクト名の誤帰属は Bir & Jonkman 2007 / Pandit 2023 / Colone 2018 と同種の引用文脈ハルシネーションパターン。修正により方法論的特徴（SCADA + aeroelastic + ML）と IEC 61400-28（策定中の寿命延長標準）への接続を明示。参考文献 [19] 自体は変更なし。Paper 1/Paper 2 v9.5 修正案ドキュメント（tools/reference_audit/batch10_round1_revision_proposals.md）の修正案③-案B を採用 |
| v9.6 | 2026-07-02 | 内部整合性監査（Paper 1-3 全文精査）に基づく機械的修正: (1) ヘッダのバージョン表記を v9.6 に統一（旧: ステータス行 v7.0 / 最終更新行 v9.4 / 改訂履歴・フッタ v9.5 の三重表記が残存していた）。(2) §2.1 の編集プレースホルダ「ASTM E1049-85 [規格番号は§3.4で参照]」を正規の引用番号 [6] に置換。(3) §1.4 の Vera-Tudela / Dimitrov 注記を精読進捗（Vera-Tudela 2026-06-11 精読完了・TI 方法論比較は扱われていないという負の発見）を反映した記述に更新。(4) §7 Conclusion の MM82 長期DEL 参照を「Limitation 8」→「Limitation 9」に修正（v8.0 での項目 2 挿入による番号シフトが Conclusion に未反映だった）。**非機械的な数値矛盾（Abstract/Conclusion の年間 DEL 1,497–1,742 vs Table 13 の 1,497–1,539、Table 4 の T01–T07 宣言 vs Table 12/13 の 5 台、Table 5 誤差の分母未定義、Table 13 vs 14 の T01 2020 値 1,503/1,507、就役 9 月 vs 2016 Jun–Dec データ）は実験ログ・Zenodo メタデータ照合が必要なため未修正**。詳細は `tools/reference_audit/paper123_consistency_audit_2026-07-02.md` |
| v9.7 | 2026-07-02 | 実データ照合による数値矛盾の解決（監査記録 A-6〜A-8, B-1 の事実確定分を適用）: (1) **年間DELレンジ 1,497〜1,742 → 1,497〜1,539**（Abstract・§4.6.2・Conclusion の3箇所）：phase3_scada/penmanshiel_monthly_del.csv の照合により、1,742 の正体は **T11 の3ヶ月分断片データの平均（1,741.9）** と確定。T11 は宣言されたタービンセット外で年間統計として不成立のため除外。5台（T01/T02/T04/T05/T06、各12ヶ月）の実レンジ 1,497.3〜1,539.2 を採用（Table 13 と整合）。(2) **タービン記述の訂正**：Zenodo static metadata により Penmanshiel は **T01–T15 の番号付けで T03 欠番**（14台）と確認。Table 4 の「this study: T01–T07」を「5 turbines」に訂正し、脚注で T07（6ヶ月）・T11（3ヶ月）の部分データ除外を明記。Abstract の「7台」→「5台」。(3) **Rainflow 誤差の方向修正**：算出スクリプト（05ms_extract_del_multiseed.py line 109）で誤差 = \|std−simple\|/std（**分母=standard**）と確定（mean 42.0%・max 75.7% は CSV 再計算と一致）。旧 Conclusion「標準は簡易版に対し平均42%高い」は分母の取り違え（正: 簡易版が標準を42%過小評価 = 標準は簡易比約1.7倍）のため修正。Table 5 に誤差定義の注記を追加。(4) **Table 14 に脚注追加**：(a) 2016年6〜8月は営業運転開始日（2016-09-01、static metadata で確認）以前を含む、(b) T01 2020 の 1,507（縦断スクリプト）vs 1,503（フリートスクリプト）は別集計経路による0.3%差。**新発見（未修正・判断待ち）**：§3.7 は「各10分レコードに bilinear 補間→月次集計」と記述するが、実装は**月次集計点（V_mean, TI_med）での一回補間**（T01 1月 1,904.5・2月 2,355.5 が手計算補間と完全一致）。DEL は V に凸なので Jensen の不等式により月次点補間は mean(DEL) を過小評価しうる。記述修正か再計算かは himinさん 判断待ち |
| v10.0 | 2026-07-03 | **A-9 案b 採用：サイトDELのレコード別補間への全面移行**（himinさん 承認の D1〜D3 に基づく）。(1) **実装刷新**：`phase3_scada/penmanshiel_del_perrecord.py` を新設し、§3.7 の記述どおり「QC通過の各10分レコードに bilinear 補間 → 月次集計」を実装。旧実装（月次集計点で一回補間）の値は参照列として同 CSV に併記。出力は `penmanshiel_monthly_del_v2.csv` / `penmanshiel_fleet_monthly_v2.csv` / `longitudinal_del_T01_v2.csv` / `longitudinal_annual_del_v2.csv`（旧 CSV は保全、git スナップショット 720d146）。(2) **集計定義の明文化（D1）**：月次=当月レコードの単純平均、フリート=タービン別月次値の単純平均（タービン等価重み）、年間=月次値の単純平均（月等価重み）を §3.7 に明記。(3) **クリップ規則の明文化（D2）**：格子範囲外レコードは補間前に境界へクリップ（V→[4,18]、TI→[0.08,0.20]）と §3.7 に明記、Limitation 5 にも追記。QC 記述の誤り（旧「V < 3 m/s」→実装は V < 3.5 m/s 除外）も修正。(4) **§4.6.4「Sensitivity to the Aggregation Method」新設（D3）**：簡便法（集計点補間）は主法に対し月次 +1.4〜+14.8%・年間 +5.7〜+8.1% 高い旨と、季節性・フリート均質性は両方法で保存される旨を開示。(5) **数値更新**：年間DEL 1,497〜1,539 → **1,393〜1,431 kN·m**（Table 13: T01 1,422 / T02 1,431 / T04 1,413 / T05 1,424 / T06 1,393）、Table 12 全12ヶ月更新（2月ピーク 2,136、タービン別月次最大 2,156 = T01 2月）、Table 14 全年更新（2016: 1,117 / 2017: 1,295 / 2018: 1,289 / 2019: 1,303 / 2020: 1,422 / 2021: 1,276）、縦断トレンド **+13.7% → +9.8%**（2017→2020、+127 kN·m）。(6) **旧版の表間不整合の解消**：Table 12–14 が単一パイプライン・単一QCによる統一集計となり、v9.7 注記の「T01 2020: 1,503 vs 1,507」問題は消滅。(7) 図6・図7 を新数値で再生成。検証：レコード別 2020 年間値は監査スクリプト a9_jensen_bias_check.py の値と完全一致、旧法参照列は旧公表 CSV と完全一致（連続性確認） |
| v10.1 | 2026-07-03 | **Codex 独立レビュー（gpt-5.5、読み取り専用）の指摘反映**。レビュー結果：実装（QC・クリップ・groupby・平均）と D1〜D3 定義の一致、Table 12/13/14 と v2 CSV の転記整合、旧法参照列の旧CSV完全一致は**すべて問題なし**と確認。指摘5件（高2・中2・低1）の採否と対応：(1) **高**：月次・年間DELの算術平均は損傷等価集約（mean(DEL^m)^(1/m)）と異なる → 採用。§3.7 に「集約値の意味に関する注記」を追加（Claude Code の独自検証で m=10 べき平均は算術平均比 約+85%＝T01 2020 と定量化）。**べき平均への移行是非は himinさん 判断待ちの新規事項**として監査記録に登録。(2) **高**：paper2_figures.py が旧CSVを参照し図6/7を旧値で上書きするリスク → 採用。fig 6/7 の読込を v2 CSV に切替（タイトルにも per-record 明記）。(3) **中**：「風況変動が主因」は因果帰属として過大 → 採用（Proposal Policy 整合）。Abstract・Conclusion を「風況変動と整合的」に弱化。(4) **中**：クリップ率の定量開示不足 → 採用。Codex 算出値を Claude Code が独立再計算で検証（2020年5台：V軸 8.0%・TI軸 12.7%・少なくとも一軸 19.2%）し、§3.7・§4.6.4・Limitation 5 に約19%を明記。(5) **低**：§4.6.4 の原因説明に実測補助を → 採用＋**仮説(b)の訂正**：V-TI 相関を実測したところ弱い正（Pearson r ≈ +0.11）で、v10.0 で記載した「V と TI の負の相関」仮説は本データで不成立と判明。(a) 曲率主因＋(b) クリップ寄与の構成に書き換え、相関の実測値を明記。§4.6.4 に「タービン別月次DELで」の限定も追加（フリート月次のみでは +2.0〜+12.3% のため） |

*Paper 2 Draft v10.1 | 2026-07-03 | Author: himin | Research Assistant: Claude Code*
