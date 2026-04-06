# OpenFAST-Based DEL Matrix for NREL 5MW Under DLC 1.2: Multi-seed Analysis, Standard Rainflow, and Lifetime Load Estimation

**Technical Note — Draft v0.4** — 2026-04-03  
**Author**: himin (Wind Turbine Technician / Researcher)  
**Repository**: blade-degradation-research / phase5_openfast_shm/

---

## Abstract

We present a reproducible simulation pipeline for computing blade root flap bending Damage Equivalent Loads (DEL) for the NREL 5MW reference turbine under IEC 61400-1 DLC 1.2 (Normal Turbulence Model). The pipeline uses OpenFAST v3.5.1 with the ROSCO v2.10.1 controller and covers 8 wind speeds (4–18 m/s) × 5 turbulence intensities (8–20%) × 6 random seeds = 240 simulation cases. To address the observed gap between the matrix lower bound (TI = 8%) and the target SCADA site TI (3–4%), a low-TI extension of 8 × 3 × 6 = 144 additional cases (TI = 2%, 4%, 6%) was subsequently simulated, yielding an extended matrix of 64 conditions total. DEL is computed using the ASTM E1049 standard Rainflow counting algorithm (rainflow 3.2.0). We quantify the underestimation error of a commonly used simplified (peak-valley half-cycle) Rainflow method, finding a mean error of 42% with the largest errors at low wind speed (V = 4–6 m/s: 57–76%). Multi-seed coefficient of variation (CV) averages 8.9% overall and 5.9% at V ≥ 8 m/s. Weibull-weighted lifetime DEL for a representative site (IEC Class II / Class C, V_ave = 8.5 m/s, I_ref = 0.12) is approximately 9,000 kN-m (9.0 MN-m), increasing to 10,900 kN-m (+21%) for a high-turbulence site (IEC Class A). The DEL matrix and calibrated weighting coefficients provide a physical basis for integrating SCADA-derived operational statistics into a blade degradation risk score. Multi-seed standard Rainflow calibration yields w_V = 0.740, w_TI = 0.260 (R² = 0.939); single-seed simplified Rainflow yields w_V = 0.810, w_TI = 0.190 (R² = 0.926). The multi-seed values are used in the integrated pipeline (Phase 4).

---

## 1. Background

### 1.1 Fatigue and DEL

Blade surface erosion and structural fatigue damage are driven by the accumulated stress cycles experienced during operation. The Damage Equivalent Load (DEL) is a single-value fatigue load metric that represents the amplitude of a constant-amplitude sinusoidal load that produces equivalent fatigue damage over a reference number of cycles N_eq:

```
DEL = [ Σ(n_i × ΔS_i^m) / N_eq ]^(1/m)
```

where ΔS_i is the stress range and n_i is the cycle count from Rainflow analysis, m is the material S-N slope exponent, and N_eq = T_sim / T_eq × N_ref. For glass fiber reinforced polymer (GFRP) blades, m = 10 is the standard value (DNV GL ST-0376; Brøndsted & Nijssen 2013).

### 1.2 Importance of Rainflow Implementation

Rainflow cycle counting is standardized in ASTM E1049-85. A commonly used simplified variant counts half-cycles from successive peak-valley pairs. This note quantifies the error introduced by the simplified method, which to our knowledge has not been systematically evaluated across the wind speed and turbulence intensity space of interest.

### 1.3 Motivation for Multi-seed Analysis

IEC 61400-1 Ed.4 recommends a minimum of 6 seeds per load case to achieve statistically stable load estimates. Single-seed results can vary substantially, particularly at low wind speeds where rotor aerodynamics are unsteady. We confirm this recommendation quantitatively using CV analysis.

---

## 2. Simulation Setup

### 2.1 Software Environment

| Component | Version |
|---|---|
| OpenFAST | v3.5.1 |
| TurbSim | v3.5.1 |
| Reference turbine | NREL 5MW Land-Based (r-test v3.5.1) |
| Controller | ROSCO v2.10.1 (libdiscon.dylib) |
| Platform | macOS, Apple M3, blade-phase3 conda env |

### 2.2 Simulation Parameters

| Parameter | Value |
|---|---|
| Design Load Case | DLC 1.2 (IEC 61400-1, Normal Turbulence Model) |
| Wind type | IEC Kaimal (IECKAI) |
| Wind speed V | 4, 6, 8, 10, 12, 14, 16, 18 m/s |
| Turbulence intensity TI | 8%, 12%, 14%, 16%, 20% |
| Seeds per condition | 6 |
| Total cases | 240 |
| Simulation duration | 660 s (600 s analysis + 60 s transient removal) |
| Time step | 0.00625 s |
| Hub height | 90 m |
| Wind profile | Power law (PLExp = 0.2) |

The base random seed for condition (V_i, TI_j) is set as `base_seed = i × 100,000 + j × 10,000`, where i ∈ {0,...,7} indexes wind speed (4→18 m/s in steps of 2) and j ∈ {0,...,4} indexes turbulence intensity (8%→20%). Seeds s = base_seed + 1 through base_seed + 6 are used for the 6 realizations per condition, ensuring reproducibility and statistical independence across conditions.

### 2.3 DEL Channel and Parameters

| Parameter | Value | Reference |
|---|---|---|
| Channel | RootMyb1 (blade 1 root flap bending moment) | NREL 5MW output |
| m (S-N slope) | 10 | GFRP; DNV GL ST-0376 |
| T_eq | 600 s | IEC 61400-1 |
| Transient skip | 60 s (first 9,600 time steps) | |
| Rainflow method | ASTM E1049, 4-point algorithm | rainflow 3.2.0 |

---

## 3. Rainflow Implementation Comparison

### 3.1 Methods

Two Rainflow implementations were compared:

- **Standard**: ASTM E1049 4-point Rainflow algorithm, implemented via the `rainflow` Python library (v3.2.0). Returns (range, count) pairs for arbitrary cycle sequences.
- **Simplified**: Peak-valley extraction followed by half-cycle counting from successive extrema pairs. Equivalent to a simplified range-mean method.

Both methods were applied to the single-seed DEL results (40 cases) to isolate the Rainflow error from seed variability.

### 3.2 Results

**Table 1: Rainflow underestimation error (simplified relative to standard)**

| V (m/s) | Mean error (%) | Max error (%) | TI range of max |
|---|---|---|---|
| 4 | 63.9 | 75.7 | TI=12% |
| 6 | 55.5 | 58.7 | TI=8% |
| 8 | 55.4 | 60.6 | TI=14% |
| 10 | 37.3 | 44.4 | TI=20% |
| 12 | 27.4 | 37.6 | TI=20% |
| 14 | 29.4 | 39.1 | TI=20% |
| 16 | 30.7 | 35.7 | TI=20% |
| 18 | 36.1 | 47.7 | TI=20% |
| **Overall** | **42.0%** | **75.7%** | |

*(See: fig_rainflow_comparison.png)*

### 3.3 Interpretation

The simplified method systematically underestimates DEL across all conditions. The underestimation is largest at low wind speed (V = 4–6 m/s, errors 56–76%), where the rotor operates below rated and exhibits high aerodynamic unsteadiness with complex non-stationary load sequences that are not well-represented by successive peak-valley pairs. At rated and above-rated wind speeds (V = 12–18 m/s), errors narrow to 27–48% but remain substantial.

**Implication**: Use of simplified Rainflow in any fatigue assessment based on this turbine or similar GFRP blades will yield DEL values that are approximately 40% below the ASTM-compliant estimate. For preliminary screening this may be acceptable, but for weight calibration or lifetime estimation the standard implementation is required.

---

## 4. Multi-seed Analysis

### 4.1 DEL Matrix (Mean over 6 Seeds, Standard Rainflow)

**Table 2: DEL matrix — mean values (kN-m), extended to low-TI domain**

*Shaded columns (TI = 2–6%) are from the low-TI extension (144 additional cases). Target site TI ≈ 3–4% (★).*

|  V \ TI  | **2%** ★ | **4%** ★ | **6%** | 8%    | 12%   | 14%   | 16%   | 20%   |
|---------|-------|-------|-------|-------|-------|-------|-------|-------|
| 4 m/s   | 567   | 675   | 870   | 970   | 1,417 | 1,559 | 1,484 | 1,864 |
| 6 m/s   | 779   | 1,096 | 1,447 | 1,749 | 2,704 | 3,070 | 3,414 | 4,159 |
| 8 m/s   | 1,580 | 2,116 | 2,696 | 3,425 | 4,612 | 5,506 | 6,218 | 7,173 |
| 10 m/s  | 2,445 | 3,077 | 3,780 | 4,673 | 6,196 | 7,156 | 7,824 | 9,282 |
| 12 m/s  | 3,511 | 4,350 | 5,167 | 6,176 | 7,979 | 8,759 | 9,804 | 11,859 |
| 14 m/s  | 4,297 | 5,186 | 6,261 | 7,290 | 9,316 | 9,910 | 11,146 | 12,798 |
| 16 m/s  | 5,165 | 5,910 | 6,869 | 7,951 | 10,240 | 11,192 | 11,952 | 14,472 |
| 18 m/s  | 6,053 | 6,730 | 7,583 | 8,692 | 11,034 | 12,095 | 12,972 | 15,109 |

*(See: fig_del_heatmap.png for TI = 8–20% heatmap; extended matrix: del_matrix_ms_extended.csv)*

**Observations**:
- DEL increases monotonically with TI at all wind speeds across the full extended range (TI = 2–20%).
- At the target site TI (≈ 3–4%), DEL is approximately **40% lower** than at TI = 8% (matrix lower bound prior to extension). This confirmed that the initial Phase 3b DEL estimates were systematically overestimated by ~41% due to TI clipping.
- DEL peaks in the V = 12–18 m/s range. The transition at V = 10→12 m/s corresponds to crossing rated wind speed, where pitch control activates and load character changes.
- At V ≥ 12 m/s, pitch control limits rotor thrust, moderating but not eliminating DEL growth with wind speed.
- CV at low TI (TI = 2–4%) remains acceptable at V ≥ 6 m/s (CV < 15%), though V = 4 m/s shows high variability (CV = 31–44%) consistent with low-TSR unsteady aerodynamics.

### 4.2 Coefficient of Variation

**Table 3: DEL CV statistics across conditions**

| Statistic | Value |
|---|---|
| CV mean (all 40 conditions) | 8.9% |
| CV median | 5.9% |
| CV maximum | 35.1% (V=4 m/s, TI=8%) |
| CV range at V ≥ 8 m/s | 1.8–14.4% |
| Conditions with CV > 20% | V=4 m/s only |

*(See: fig_cv_boxplot.png)*

**Interpretation**: At V ≥ 6 m/s, CV is generally below 15%, indicating that 6 seeds provide a statistically stable mean. The high CV at V = 4 m/s (tip speed ratio is low, rotor aerodynamics are unsteady) is a known characteristic of below-cut-in-adjacent operation. However, the contribution of V = 4 m/s to lifetime DEL is small because the Weibull distribution assigns low probability weight to very low wind speeds; the impact on lifetime DEL is limited (see §5).

---

## 5. Lifetime DEL

### 5.1 Stage 2: Weibull-Weighted Lifetime DEL (Fixed TI)

Wind speed was weighted by a Weibull distribution (shape parameter k = 2, scale parameter λ derived from V_ave). The lifetime DEL is computed as the m-power weighted average over the discretized wind speed bins:

```
p(V) = (k/λ) × (V/λ)^(k-1) × exp(-(V/λ)^k)
DEL_lifetime = [ Σ_V p(V) × DEL(V, TI)^m ]^(1/m)
```

Note: this form is equivalent to the standard DEL definition (§1.1) when the bin probabilities p(V) replace the N_eq weighting — each bin's DEL contributes proportionally to its occurrence frequency.

**Table 4: Stage 2 lifetime DEL by TI and IEC wind class (kN-m)**

| TI | IEC Class I (V_ave=10.0) | IEC Class II (V_ave=8.5) | IEC Class III (V_ave=7.5) |
|---|---|---|---|
| 8% | 6,942 | 6,605 | 6,263 |
| 12% | 8,871 | 8,447 | 8,018 |
| 14% | 9,674 | 9,204 | 8,729 |
| 16% | 10,474 | 9,995 | 9,513 |
| 20% | 12,365 | 11,809 | 11,248 |

### 5.2 Stage 3: V-TI Joint Distribution (IEC NTM)

Representative TI at each wind speed was computed using the IEC NTM characteristic turbulence model:

```
TI(V) = I_ref × (0.75 + 5.6/V)
```

**Table 5: Stage 3 lifetime DEL by IEC turbulence and wind class (kN-m)**

| Turbulence class | IEC Class I | IEC Class II | IEC Class III |
|---|---|---|---|
| Class C (I_ref=0.12) | 9,366 | 8,965 | 8,564 |
| Class B (I_ref=0.14) | 10,348 | 9,938 | 9,529 |
| Class A (I_ref=0.16) | 11,327 | 10,891 | 10,452 |

*(See: fig_lifetime_del_sensitivity.png)*

**Site estimate**: The Kaggle SCADA dataset used in Phase 3 of this research program exhibited mean_TI ≈ 0.03–0.05, consistent with IEC Class C (I_ref = 0.12) and a low-wind-speed inland site (IEC Class II–III). The corresponding lifetime DEL estimate is approximately **9,000 kN-m**, compared to **10,900 kN-m** (+21%) for a high-turbulence coastal site (IEC Class A/II).

**Limitation**: Stage 3 assumes V and TI are statistically independent. In reality, many sites exhibit a negative V-TI correlation (high wind speeds tend to have lower TI). Site-specific V-TI joint distributions would improve the accuracy of lifetime DEL estimates.

---

## 6. Phase 4 Weight Calibration

The relative contributions of wind speed and turbulence intensity to normalized DEL were estimated by non-negative linear regression (`sklearn LinearRegression(positive=True)`):

```
DEL_norm ≈ w_V × V_norm + w_TI × TI_norm
```

Two calibration results were obtained depending on the Rainflow method and seed count:

| Method | w_V | w_TI | R² | Dataset |
|---|---|---|---|---|
| Single-seed, simplified Rainflow | 0.810 | 0.190 | 0.926 | 40 cases (1 seed) |
| **Multi-seed, standard Rainflow** | **0.740** | **0.260** | **0.939** | **40 conditions (6-seed mean)** |

The multi-seed standard Rainflow result reflects higher TI sensitivity compared to the single-seed simplified version, because:
1. Standard Rainflow captures complex load cycles that are TI-sensitive but missed by the simplified method (§3.3).
2. Multi-seed averaging reduces seed-specific noise, allowing the TI signal to emerge more clearly.

**Applied calibration**: The Phase 4 integrated pipeline uses the multi-seed standard Rainflow weights (w_V = 0.740, w_TI = 0.260):

```
fatigue_risk_score = w_V × hrs_above_rated_norm + w_TI × mean_ti_norm
```

**Phase 3b connection**: DEL estimates from the Phase 3 SCADA analysis (via RegularGridInterpolator on `del_matrix_ms.csv`) revealed that the actual site TI (0.030–0.044) fell below the simulation matrix lower bound (TI = 0.08), causing systematic overestimation of ~41%. The low-TI extension (TI = 0.02, 0.04, 0.06; 144 additional cases) resolved this clipping constraint. After switching to `del_matrix_ms_extended.csv`, the annual mean DEL estimate corrected from 2,665 kN-m to **1,566 kN-m** (-41%), with TI variation now properly reflected in monthly DEL estimates.

**Scope**: These weights are calibrated for NREL 5MW / DLC 1.2 / low-TI conditions. For high-TI sites (IEC Class A, offshore), w_TI is expected to increase significantly, and recalibration using site-specific simulations is necessary.

---

## 7. Discussion

### 7.1 Scope and Generalizability

All results in this note are specific to:
- NREL 5MW Land-Based reference turbine (Jonkman et al. 2009)
- DLC 1.2 (NTM, normal operation)
- Steady-state turbulent inflow (TurbSim IECKAI model)

Transfer to real turbines requires recalibration. The NREL 5MW is a 2009 reference design; modern multi-MW turbines have different blade geometries, controller strategies, and structural dynamics that will shift the DEL matrix. The DLC 1.2 normal production case covers the majority of operational lifetime but excludes fault events, extreme loads (DLC 1.3 ETM), and start/stop cycles.

### 7.2 V-TI Independence Assumption

The lifetime DEL computation (Stage 3) assumes that V and TI are drawn independently. For sites with strong seasonal patterns where high-TI conditions coincide with high wind speeds (e.g., northern offshore sites), this assumption underestimates the joint contribution. A copula-based joint distribution model would address this but requires site-specific meteorological data.

### 7.3 Seed Variability at Low Wind Speed

CV = 35% at V = 4 m/s suggests that 6 seeds are insufficient to characterize DEL at very low wind speeds. IEC 61400-1 recommends checking convergence; for design-critical applications, 12–24 seeds may be needed at V ≤ 4 m/s. However, given the low Weibull weight of V = 4 m/s in the lifetime integral (< 3% for Class II), the impact on lifetime DEL is small and was confirmed to be < 1% sensitivity in our analysis.

---

## 8. Conclusion

1. **Standard Rainflow is essential**: Simplified Rainflow underestimates DEL by a mean of 42% (up to 76% at V = 4 m/s). Any fatigue analysis for GFRP blades should use ASTM E1049-compliant counting.
2. **Multi-seed CV is acceptable at V ≥ 6 m/s**: CV median = 5.9% confirms that 6 seeds per condition satisfy the IEC 61400-1 recommendation for normal production cases.
3. **Lifetime DEL spans 9,000–10,900 kN-m** depending on site class, quantifying the 21% load increase between low- and high-turbulence sites.
4. **Wind speed dominates fatigue (w_V = 0.740)** for low-TI inland sites under multi-seed standard Rainflow calibration, consistent with the Phase 3 SCADA analysis. TI contribution (w_TI = 0.260) is higher than single-seed simplified Rainflow suggests (0.190), underscoring the importance of method choice.
5. The resulting DEL matrix and calibrated weights provide a physics-grounded basis for the integrated blade degradation scoring pipeline.

---

## 9. Code Availability

All scripts are available in:
```
blade-degradation-research/phase5_openfast_shm/openfast_cases/scripts/
  01ms_generate_turbsim_inputs.py   … TurbSim input generation (240 cases)
  02ms_run_turbsim.py               … TurbSim batch execution
  03ms_generate_openfast_inputs.py  … OpenFAST input generation
  04ms_run_openfast.py              … OpenFAST batch execution
  05ms_extract_del_multiseed.py     … DEL extraction (standard + simplified Rainflow)
  06_lifetime_del.py                … Lifetime DEL (Stage 2 + Stage 3)
  week3_figures.py                  … Figures (heatmap, Rainflow comparison, CV, lifetime DEL)
  low_ti_extension_pipeline.py     … 低TI域拡張（TI=0.02/0.04/0.06, 144ケース, 実行中）
```

Results are stored in:
```
results/
  del_matrix_ms.csv                 … Multi-seed DEL matrix (240 cases, mean/std/CV)
  del_single_rainflow_comparison.csv … Standard vs. simplified error
  lifetime_del_stage2.csv           … Stage 2 lifetime DEL
  lifetime_del_stage3.csv           … Stage 3 lifetime DEL
  fig_del_heatmap.png
  fig_rainflow_comparison.png
  fig_cv_boxplot.png
  fig_lifetime_del_sensitivity.png
```

---

## References

1. IEC 61400-1 Ed.4 (2019): "Wind energy generation systems — Part 1: Design requirements." IEC.
2. ASTM E1049-85 (2017): "Standard Practices for Cycle Counting in Fatigue Analysis." ASTM International.
3. Jonkman, J.M. et al. (2009): "Definition of a 5-MW Reference Wind Turbine for Offshore System Development." NREL/TP-500-38060.
4. Sutherland, H.J. (1999): "On the Fatigue Analysis of Wind Turbines." Sandia National Laboratories, SAND99-0089.
5. DNV GL ST-0376 (2015): "Rotor Blades for Wind Turbines." DNV GL.
6. Brøndsted, P. & Nijssen, R.P.L. (eds.) (2013): "Advances in Wind Turbine Blade Design and Materials." Woodhead Publishing.
7. Hayman, G.J. (2012): "MLife Theory Manual for Version 1.00." NREL/TP-5000-55799.
8. Natarajan, A. (2014): "Damage equivalent load synthesis and stochastic extrapolation for wind turbine fatigue design." *Wind Energy* 17(8), 1250–1265.
9. ROSCO (v2.10.1): "Reference OpenSource Controller for Wind Turbines." NREL. https://github.com/NREL/ROSCO
10. Malik, A. & Bak, C. (2025): "Aerodynamic impact of leading edge erosion on wind turbine blades." *Wind Energy Science* 10, 227–247. https://doi.org/10.5194/wes-10-227-2025

---

## Appendix A: DLC 1.3 (Extreme Turbulence Model) — Supplementary Confirmation

DLC 1.3 uses the IEC Extreme Turbulence Model (ETM, IEC_WindType = "1ETM") to represent the most severe turbulent conditions expected during the turbine's design lifetime. 48 cases (8 wind speeds × 6 seeds) were simulated to quantify the DEL ratio relative to DLC 1.2.

**Table A1: DLC 1.3 DEL results (standard Rainflow, 6-seed mean)**

| V (m/s) | DEL_1.3 (kN-m) | CV (%) | Ratio vs DLC1.2(TI=14%) | Ratio vs DLC1.2(TI=8%) |
|---|---|---|---|---|
| 4 | 6,490 | 7.1 | ×4.2 | ×6.7 |
| 6 | 9,801 | 10.8 | ×3.2 | ×5.6 |
| 8 | 12,435 | 4.9 | ×2.3 | ×3.6 |
| 10 | 13,587 | 8.6 | ×1.9 | ×2.9 |
| 12 | 16,046 | 8.3 | ×1.8 | ×2.6 |
| 14 | 16,490 | 10.8 | ×1.7 | ×2.3 |
| 16 | 16,300 | 7.8 | ×1.5 | ×2.1 |
| 18 | 16,996 | 4.0 | ×1.4 | ×2.0 |

**Interpretation**: DLC 1.3 generates 1.4–4.2× higher DEL than DLC 1.2 at TI=14%. The amplification is largest at low wind speed (V = 4–6 m/s) where ETM turbulence intensity substantially exceeds NTM. At high wind speed (V ≥ 14 m/s), pitch control limits rotor loads, narrowing the ratio to ×1.4–1.7.

**Note on lifetime contribution**: DLC 1.3 represents an extreme condition with low annual occurrence frequency. Direct integration into lifetime DEL requires multiplication by occurrence probability per IEC 61400-1; this analysis was not performed. DLC 1.3 results should be treated as an upper-bound load characterization, not a lifetime load estimate.

---

---

## Submission Checklist

**Status: v0.3 — 投稿準備完了（以下の作業完了後に投稿可）**

### 必須（投稿前に完了すること）
- [x] **低TI域拡張完了後にAbstractとTable 2を更新** — TI=0.02/0.04/0.06 の DEL 値追加済み。実SCADAサイトのTI範囲（3〜4%）をカバー
- [x] **§6 Phase 4 較正の低TI外挿誤差を定量化** — 2,665→1,566 kN-m（-41%）を明記済み
- [x] **Table 2 に拡張行列を追加** — TI=2%, 4%, 6% 列追加済み

### 推奨（査読対応）
- [ ] **DLC 1.3 寄与率の定量化** — Appendix A の結果に "lifetime contribution rate" を追記（IEC 61400-1 Table F.1 の発生確率を使用）
- [ ] **V-TI 独立性仮定の感度確認** — Stage 3 の結果に対して V-TI 相関 ρ=-0.2, -0.5 のケースを追加

### 完了済み
- [x] v0.1 ドラフト作成（全セクション）
- [x] v0.2 査読修正（6点：シード番号式・Table誤差・DEL式説明・較正値比較）
- [x] v0.3 Phase 4 重み更新（0.810→0.740、マルチシード標準Rainflow）・Phase 3b 接続明記
- [x] v0.4 低TI域拡張完了（144ケース）・Abstract/Table 2/§6を更新・TIクリッピング解消を反映

*Technical Note Draft v0.4 — 2026-04-03 | Status: 投稿準備完了（図表挿入のみ残）*
