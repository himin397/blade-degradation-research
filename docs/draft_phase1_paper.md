# Wind Turbine Blade Surface Damage Detection and Region-wise Risk Scoring Using YOLOv8 with Pyramid Patch Augmentation

**Draft v0.4** — 2026-04-03  
**Author**: himin (Wind Turbine Technician / Researcher)

---

## Abstract

We propose a method to detect surface damage on wind turbine blades from publicly available drone inspection images and quantify the results as region-wise risk scores along the blade span direction. Using the DTU Wind Turbine Inspection Image Dataset (559 images, 5 damage classes), we applied YOLOv8n with a pyramid patch augmentation strategy that generates multi-scale tiles from 5280×2970 px source images. The proposed method (EXP-002) achieved mAP@0.5 = 0.581, a 59% improvement over the baseline (EXP-001: mAP@0.5 = 0.365, evaluated on the same test set). Risk scores were computed per blade span region (Tip, Mid, Root) by weighting each detection by its confidence, bounding box area, damage class severity, and region-specific load-based weighting. Sensitivity analysis of the weighting scheme showed that the Tip > Mid > Root rank is stable under class weight variation and under ±50% changes to Mid and Root region weights, but can be reversed if the Tip weight is reduced by 50% or the Mid weight is increased by 50%, indicating a moderate sensitivity given the current weight ratio (Tip:Mid = 3:2). The chord-direction (leading edge / trailing edge) classification was found to be structurally unreliable due to the oblique shooting geometry of the DTU dataset and was excluded from the risk score. These results constitute a reproducible, end-to-end pipeline from raw drone images to span-region risk scores, serving as a quantitative image-based damage input for future integrated degradation prediction models.

---

## 1. Introduction

### 1.1 Background

Wind turbine blades are among the most maintenance-intensive components in wind energy systems. Leading edge erosion (LEE) and surface cracking accumulate over time due to rain, sand, and fatigue loading, progressively reducing aerodynamic efficiency and structural integrity. Malik & Bak (2025) reported that blade erosion causes AEP losses of 0.82–2.14% depending on severity and turbulence intensity, with the most sensitive wind speed range around 9–13 m/s where tip speed is highest.

Drone-based inspection has become a standard tool for detecting blade surface damage. However, the resulting images are rarely processed beyond manual labeling: quantitative, region-resolved damage metrics that can be fed into O&M decision-support systems are lacking. The present study addresses this gap by building a reproducible pipeline from raw drone images to blade region-level risk scores.

### 1.2 Research Objective and Contribution

The objectives of this study are:
1. To detect surface damage on wind turbine blades from drone inspection images using YOLOv8 with pyramid patch augmentation.
2. To assign each detected damage instance to a blade span region (Tip, Mid, Root) and aggregate a quantitative risk score per region.
3. To quantitatively characterize the sensitivity of the risk score ranking to the choice of weighting parameters.

The primary contributions are:
- Demonstration that pyramid patch augmentation at 1× / 0.67× / 0.33× scales improves mAP@0.5 by 67% over single-scale baseline on the DTU dataset.
- Establishment of a span-region risk scoring scheme grounded in aerodynamic and fatigue considerations, with documented weighting rationale and sensitivity bounds.
- Quantitative confirmation that chord-direction (LE/TE) classification is structurally unreliable under the DTU oblique shooting geometry, providing a replicable negative finding for future dataset design.

### 1.3 Relation to Prior Work

Shihavuddin et al. (2019) applied Faster R-CNN with Inception-ResNet-V2 to DTU-origin images, achieving mAP@0.5 = 0.811. The present study uses a lighter model (YOLOv8n, 3.0M parameters vs. ~55M for the reference) with 30 training epochs and targets a different output: regional risk scores rather than detection accuracy alone. Gohar et al. (2023) released a re-annotation of the DTU dataset (used here); with their annotations, YOLOv8 achieved approximately mAP@0.5 = 0.54 without multi-scale augmentation (as reported in their study). Our pyramid augmentation raises this to 0.581 on the same annotation set.

---

## 2. Data

### 2.1 Dataset

We used the DTU Wind Turbine Inspection Image Dataset (Shihavuddin et al., DOI: 10.17632/hd96prn3nc.2), comprising drone inspection photographs of a Nordtank 500 kW turbine taken in 2017 (161 images) and 2018 (398 images), totaling 559 images at 5280×2970 px resolution. YOLO-format annotations were sourced from Gohar et al. (2023), covering 5 damage classes:

| Class ID | Label | Description | Class Weight |
|---|---|---|---|
| 0 | VG;MT | Vortex generator / mechanical damage | 1.5 |
| 1 | LE;ER | Leading edge erosion | 2.0 |
| 2 | LR;DA | Lightning receptor / surface damage | 1.5 |
| 3 | LE;CR | Leading edge crack | **3.0** |
| 4 | SF;PO | Surface pollution / contamination | 1.0 |

Class weights were assigned in descending order of structural criticality: cracks (LE;CR) are the most severe as they can propagate to delamination; erosion (LE;ER) directly increases drag and reduces AEP; vortex generator and surface damage are moderate; contamination is lowest severity.

### 2.2 Preprocessing and Dataset Split

Source images (5280×2970 px) were tiled into 1024×1024 px patches with 20% overlap using a sliding window, yielding 13 tiles per image on average. The dataset was split at the source-image level (not patch level) to prevent patches from the same image appearing in both training and test sets:

| Split | Source images | Annotated patches | Background patches | Total patches |
|---|---|---|---|---|
| Train | 212 | 1,269 | 6,786 | 8,055 (→11,448 with augmentation) |
| Val | 44 | 82 | 710 | 792 |
| Test | 45 | 93 | 717 | 810 |

**Annotation counts by class (train / val / test)**:

| Class | Train | Val | Test |
|---|---|---|---|
| VG;MT | 588 | 29 | 39 |
| LE;ER | 687 | 51 | 58 |
| LR;DA | 36 | 2 | 6 |
| LE;CR | 171 | 14 | 11 |
| SF;PO | 195 | 17 | 10 |
| **Total** | **1,677** | **113** | **124** |

**Note on independence**: Split was performed at the source-image level. Patches originating from the same source image are constrained to a single split. However, different images in the DTU dataset may depict the same physical blade region from different angles; full independence between splits cannot be guaranteed.

### 2.3 Pyramid Patch Augmentation

To address the multi-scale nature of blade damage (millimeter-scale erosion pits to meter-scale surface contamination), each training patch was supplemented with two down-scaled versions (×0.67 and ×0.33), tripling the effective training set size from 3,816 to 11,448 patches. This strategy follows the feature pyramid principle and is analogous to the approach reported by Gohar et al. (2023), who noted a +35% mAP gain from multi-scale training; our implementation yielded +67%.

---

## 3. Method

### 3.1 Object Detection Model

We used YOLOv8n (Ultralytics, 2023) — the nano variant with 3.0M parameters — trained for 30 epochs at 640 px input resolution on an Apple M3 GPU (MPS backend). The baseline experiment (EXP-001) used single-scale 640 px patches without augmentation; the augmented experiment (EXP-002) added the pyramid multi-scale training described in §2.3.

### 3.2 Span-Region Assignment

Each 1024×1024 px patch encodes its blade span position in the filename: `DJI_{ID}_{col}_{row}.JPG`. Based on visual inspection of the DTU imagery, the blade runs diagonally from upper-left (tip) to lower-right (root) within each source image:

- **row = 0** → Tip region (tip-side of blade span, upper portion of source image)
- **row = 1** → Mid region (mid-span)
- **row = 2+** → Root region (root-side, lower portion with visible ground)

This mapping was verified by comparing annotated examples at row=0 and row=2, and is consistent with the observation that LE;ER annotations are most concentrated at row=0 (highest tip speed, highest erosion exposure).

### 3.3 Chord-Direction Exclusion

We investigated whether the horizontal position of a bounding box (cx coordinate) could be used to classify damage as leading edge (LE) or trailing edge (TE). Analysis of 229 LE;ER annotations revealed a near-uniform cx distribution (range: 0.004–0.992), with no clustering near cx = 0. This is structurally caused by the oblique shooting geometry: the leading edge position in the image plane varies as a function of the row position within the source image. Fixed-threshold chord classification (e.g., cx < 0.25 → LE) is therefore unreliable and was excluded from the risk scoring pipeline.

### 3.4 Risk Score Definition

For each detected damage instance *i* in patch *p*, a contribution score is computed as:

```
score_i = confidence_i × area_ratio_i × class_weight_i × region_weight_i
```

where:
- `confidence_i` ∈ [0, 1]: YOLOv8 detection confidence
- `area_ratio_i = w_i × h_i`: normalized bounding box area (0–1)
- `class_weight_i`: severity weight per damage class (see §2.1)
- `region_weight_i`: span-region weight (Tip: 3.0, Mid: 2.0, Root: 1.0)

The region-level risk score is the sum over all detections assigned to that region:

```
region_score_r = Σ_i score_i,  for all i with region_i = r
```

**Rationale for region weights**: Tip (region_weight = 3.0) experiences the highest tangential velocity and therefore the highest erosion rate, the largest centrifugal stress, and the greatest contribution to fatigue loading at the blade root. This is consistent with Malik & Bak (2025) and with field observation. Mid and Root weights (2.0 and 1.0) reflect decreasing tip speed and fatigue exposure toward the root.

### 3.5 Sensitivity Analysis

To quantify the robustness of the Tip > Mid > Root rank under weight perturbation, we varied each region weight individually by ±50% while holding others constant, and also uniformly scaled all class weights by ±50%.

---

## 4. Results

### 4.1 Detection Performance

| Experiment | mAP@0.5 | mAP@0.5:0.95 | Precision | Recall |
|---|---|---|---|---|
| EXP-001 (baseline, single-scale) | 0.365 | 0.160 | 0.824 | 0.286 |
| EXP-002 (pyramid augmentation) | **0.581** | **0.314** | **0.823** | **0.492** |
| Improvement | +59% | +96% | ±0% | +72% |

*Both experiments evaluated on the same test set (810 patches, 124 annotated instances) via model.val(conf=0.001, iou=0.5). EXP-001 uses best.pt from single-scale training. Note: earlier draft reported EXP-001 mAP@0.5 = 0.348 (training val set) and mAP@0.5:0.95 = 0.189 (integrated report); the corrected test-set evaluation yields 0.365 and 0.160 respectively. The mAP@0.5 improvement over EXP-001 is accordingly revised from +67% to +59%.*

#### Per-class AP (EXP-002, test set)

| Class | AP@0.5 | AP@0.5:0.95 | Train count |
|---|---|---|---|
| LE;ER (erosion) | 0.784 | 0.434 | 687 |
| VG;MT (mech. damage) | 0.756 | 0.410 | 588 |
| SF;PO (contamination) | 0.706 | 0.568 | 195 |
| LR;DA (surface damage) | 0.556 | 0.111 | 36 |
| LE;CR (crack) | **0.000** | 0.000 | 171 |

*EXP-001 per-class AP@0.5 on test set for reference: VG;MT=0.557, LE;ER=0.473, LR;DA=0.200, LE;CR=0.025, SF;PO=0.572. Note: EXP-001 LE;CR AP=0.025 (non-zero) vs EXP-002 AP=0.000 — pyramid augmentation did not improve crack detection and may have slightly reduced it, likely due to scale-dependent annotation mismatches at ×0.33 tiles.*

LE;CR achieved AP = 0.000 despite 171 training instances. Visual inspection of crack annotations reveals that crack bounding boxes are typically very thin and elongated (low area ratio), making them difficult for anchor-based detectors to localize at the IoU threshold of 0.5. This limits the utility of the LE;CR class weight (3.0) in practice, as very few cracks are detected with sufficient confidence.

### 4.2 Region-wise Risk Scores

Risk scores were computed from EXP-002 predictions on the test set. To account for the unequal number of test patches per year (2017: n=180; 2018: n=630), per-patch normalized scores are reported alongside cumulative totals.

| Year | Tip (total) | Mid (total) | Root (total) | n_patches | Tip/patch | Mid/patch | Root/patch |
|---|---|---|---|---|---|---|---|
| 2017 | **2.023** | 1.247 | 0.000 | 180 | **0.01124** | 0.00693 | 0.00000 |
| 2018 | 0.488 | **0.986** | 0.064 | 630 | 0.00078 | 0.00157 | 0.00010 |

On a per-patch basis, 2017 images show 14× higher Tip-region risk than 2018 images (0.01124 vs. 0.00078). This may reflect genuine year-to-year differences in Tip damage state, or a difference in image composition between the two subsets. The Root score is zero for 2017 despite 60 row=2 patches being present in the test set: the model produced no detections in any of those patches. This suggests that the 2017 Root-region patches either contained no visible damage or contained damage types that EXP-002 failed to detect (possibly LE;CR, which has AP = 0.000).

### 4.3 Sensitivity of Risk Score Ranking

| Scenario | Tip score | Mid score | Root score | Rank | Changed? |
|---|---|---|---|---|---|
| **Baseline** (Tip=3.0, Mid=2.0, Root=1.0) | **2.512** | **2.232** | **0.064** | Tip > Mid > Root | — |
| RW: Tip ×1.5 | 3.767 | 2.232 | 0.064 | Tip > Mid > Root | No |
| RW: Tip ×0.5 | 1.256 | 2.232 | 0.064 | Mid > Tip > Root | **Yes** |
| RW: Mid ×1.5 | 2.512 | 3.349 | 0.064 | Mid > Tip > Root | **Yes** |
| RW: Mid ×0.5 | 2.512 | 1.116 | 0.064 | Tip > Mid > Root | No |
| RW: Root ×1.5 | 2.512 | 2.232 | 0.096 | Tip > Mid > Root | No |
| RW: Root ×0.5 | 2.512 | 2.232 | 0.032 | Tip > Mid > Root | No |
| CW: all ×1.5 | 3.767 | 3.349 | 0.096 | Tip > Mid > Root | No |
| CW: all ×0.5 | 1.256 | 1.116 | 0.032 | Tip > Mid > Root | No |

The Tip > Root order is robust under all tested perturbations. The Tip > Mid order, however, is sensitive to the Tip:Mid weight ratio: rank inversion occurs when Tip weight is halved (ratio 1.5:2) or Mid weight is increased by 50% (ratio 3:3). The current baseline margin between Tip and Mid scores is small (2.512 vs. 2.232; 13% difference), indicating that this ranking should be interpreted with caution.

---

## 5. Discussion

### 5.1 LE;CR Zero Detection

The most structurally critical class — LE;CR (crack, class weight = 3.0) — achieved AP = 0.000. This limits the risk score's ability to capture the most severe damage type. Two contributing factors are likely:

1. **Geometry**: Crack bounding boxes are thin and elongated (low area ratio), making them difficult to localize at IoU = 0.5. A lower IoU threshold (e.g., 0.3) or a shape-aware loss function may improve recall.
2. **Annotation quality**: Crack annotations in the DTU dataset are known to be sparse and potentially inconsistent across labelers.

Until crack detection improves, the risk score underestimates risk in images with cracks. For practical use, crack-positive images should be flagged separately.

### 5.2 Chord-Direction Limitation

The exclusion of chord-direction scoring (LE vs. TE) is a structural limitation of the DTU dataset, not of the method. Future datasets with standardized orthogonal shooting (blade axis aligned with image horizontal) would enable chord-resolved scoring and substantially increase the diagnostic value of the pipeline.

### 5.3 Weight Sensitivity and Scope of Conclusions

The sensitivity analysis (§4.3) shows that the Tip > Mid ranking is not robust to ±50% weight perturbation. The current weights are grounded in physical reasoning (Malik & Bak 2025; DNV GL ST-0376), but were not calibrated against measured fatigue data. Two implications follow:

1. The statement "Tip carries the highest risk" should be qualified as: "under the physically-motivated weighting scheme (Tip=3.0, Mid=2.0, Root=1.0), Tip > Mid > Root, but the Tip–Mid margin is narrow (13%) and can be reversed by moderate weight changes."
2. Weight calibration using site-specific DEL data would substantially strengthen the scoring scheme. In Phase 5b of this research program, OpenFAST DLC 1.2 simulations (240 cases, multi-seed standard Rainflow) yielded calibrated weighting coefficients w_V = 0.740, w_TI = 0.260 for a low-TI inland site (R² = 0.939), providing a physics-grounded alternative to the heuristic region weights used here.

### 5.4 Limitations

- **Single turbine type**: The DTU dataset covers a single Nordtank 500 kW turbine. Generalization to other turbine geometries requires retraining.
- **Split independence**: Patch-level split was performed at the source-image level, but different source images may depict overlapping blade regions.
- **Model scale**: YOLOv8n (3M parameters, 30 epochs) underperforms larger models trained longer. The 0.581 mAP vs. 0.811 (Shihavuddin 2019) gap reflects this tradeoff. A full comparison would require equal compute budget.
- **Temporal comparison**: The 2017 vs. 2018 risk score comparison (§4.2) cannot be interpreted as evidence of damage progression because the image sets contain different blades and different coverage proportions.

---

## 6. Conclusion

We developed a pipeline for drone inspection image-based blade damage detection and span-region risk scoring using YOLOv8n with pyramid patch augmentation. The main findings are:

1. **Pyramid augmentation (+59% mAP)**: Multi-scale training at 1×/0.67×/0.33× tile scales substantially improves detection performance, particularly for small and mid-size damage instances (Recall: +72%). Both experiments evaluated on the same test set (810 patches).
2. **Class-level heterogeneity**: LE;ER and VG;MT are well-detected (AP@0.5 = 0.78 and 0.76); LE;CR (the most critical class) achieves AP = 0.000, requiring further method development.
3. **Chord-direction classification is structurally unreliable** in the DTU dataset due to oblique shooting geometry; span-direction (Tip/Mid/Root) classification is reliable via patch row index.
4. **Risk score sensitivity**: The Tip > Mid > Root rank is stable under Root weight variation and class weight scaling, but can be reversed if the Tip:Mid weight ratio falls below approximately 1.5:2. This is a documented limitation to be addressed by DEL-calibrated weight updating in future work.

The pipeline produces a quantitative, reproducible damage score that can serve as the image-derived input component of an integrated blade degradation prediction model.

---

## References

1. Shihavuddin, A.S.M. et al. (2019): "Wind Turbine Surface Damage Detection by Deep Learning Aided Drone Inspection Analysis." *Energies* 12(4), 676. https://doi.org/10.3390/en12040676
2. Gohar, I.M. et al. (2023): "Wind Turbine Blade Defect Detection Using Deep Learning." *Machines* 11(10), 953. https://doi.org/10.3390/machines11100953
3. Shihavuddin, A.S.M. et al. (2021): "DTU Wind Turbine Inspection Images." *Mendeley Data*, V2. https://doi.org/10.17632/hd96prn3nc.2
4. Malik, A. & Bak, C. (2025): "Aerodynamic impact of leading edge erosion on wind turbine blades." *Wind Energy Science* 10, 227–247. https://doi.org/10.5194/wes-10-227-2025
5. Jocher, G. et al. (2023): *Ultralytics YOLOv8*. https://github.com/ultralytics/ultralytics
6. DNV GL ST-0376 (2015): "Rotor Blades for Wind Turbines." DNV GL.
7. IEC 61400-1 Ed.4 (2019): "Wind energy generation systems — Part 1: Design requirements." IEC.

---

---

## Submission Checklist

**Status: v0.3 — 投稿準備完了（以下の作業完了後に投稿可）**

### 必須（投稿前に完了すること）
- [x] **Fig. 1: 検出例画像** — `reports/fig_detection_examples_en.png`（英語・TP/FP/FN 3パネル）生成済み
- [x] **Fig. 2: Sensitivity 棒グラフ** — `reports/fig_sensitivity_bars_en.png`（英語・2パネル）生成済み。論文 §4.3 Table と数値一致確認済み（Baseline: Tip=2.512, Mid=2.232, Root=0.064）
- [x] **EXP-001 test set 再評価** — 完了。mAP@0.5=0.365, mAP@0.5:0.95=0.160（test set）。改善率を +67% → **+59%** に修正。Abstract・Table 1・§6 更新済み

### 推奨（精度向上・査読対応）
- [ ] **LE;CR 改善実験** — IoU 閾値 0.3 での再評価 or shape-aware loss（WIOU/SIoU）の試験
- [ ] **EXP-003（TI 拡張データ）** — DTU 以外のデータセット（e.g., CaRINA, OpenAI Blade Dataset）で再学習・転移学習検証

### 完了済み
- [x] v0.1 ドラフト作成（全セクション）
- [x] v0.2 査読修正（7点：引用表現・typo・脚注・説明修正）
- [x] v0.3 Phase 5b 重み更新（w_V=0.810→0.740、マルチシード標準Rainflow較正値）
- [x] v0.4 EXP-001 test set 再評価・改善率修正（+67%→+59%）・英語図表2点生成

**Draft v0.4** — 2026-04-03  
**Status: 投稿可能（全必須項目完了）**
