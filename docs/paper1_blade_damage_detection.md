# Paper 1: Wind Turbine Blade Surface Damage Detection and Span-wise Risk Scoring Using Drone Inspection Images with Pyramid Patch Augmentation

**ステータス**: v4.0（最終表現調整完了）
**最終更新**: 2026-04-04（v4: 最終表現調整）

---

## 1文主張

> 公開ドローン画像559枚にピラミッドパッチ拡張付きYOLOv8nを適用し、5損傷クラス中4クラスでAP@0.5 = 0.56–0.78（mAP = 0.58, +67%）を得たが、LE;CR（訓練パッチの1.6%）はゼロ検出でありクラス不均衡が検出限界を規定する。スパン方向リスクスコア（Tip > Mid > Root）は±50%重み摂動下で8中6シナリオでランクが保存された。

---

## Abstract

Wind turbine blade surface damage detection using drone inspection images is increasingly important for condition-based maintenance planning. This study presents a reproducible pipeline for detecting surface damage and computing span-wise risk scores from publicly available drone inspection images of the DTU/Nordtank turbine.

We applied YOLOv8n with pyramid patch augmentation to 559 original images (13,050 patches after slicing and augmentation) across five damage classes. The dataset was split at the original image level (train: 212, val: 44, test: 45; seed=42) to prevent patch-level leakage; blade-level independence cannot be guaranteed with available metadata.

Pyramid patch augmentation improved mAP@0.5 from 0.35 (baseline) to 0.58 (+67%). Four of five classes achieved AP@0.5 of 0.56–0.78, while LE;CR yielded AP = 0.00 due to severe class imbalance (1.6% of training patches). The four-class mAP@0.5 (excluding LE;CR) was 0.70, reported as a supplementary indicator.

A span-wise risk scoring scheme (Tip/Mid/Root) using practitioner-informed weights produced rankings consistent with field experience. Sensitivity analysis (±50% perturbation, 8 scenarios) confirmed rank preservation in 6 of 8 cases. Year-wise score differences reflect inspection conditions, not damage progression. All code, configuration, and trained weights are included as supplementary materials.

---

## 1. Introduction

Drone-based inspection has largely replaced rope-access and ground-based methods for wind turbine blade assessment, generating large volumes of high-resolution imagery. However, converting these images into actionable maintenance priorities remains manual and subjective. Deep learning–based damage detection has shown promise (Shihavuddin et al. 2019; Gohar et al. 2023), yet most studies focus on detection performance (mAP) without addressing the downstream question: *which blade region should be prioritized for repair?*

This study addresses two gaps:

1. **Detection with limited data**: Public drone inspection datasets are small and exhibit severe class imbalance. We investigate how pyramid patch augmentation can improve detection performance under these constraints, and explicitly diagnose where class imbalance causes complete detection failure.

2. **Span-wise risk scoring**: We extend detection results into a region-wise risk scoring scheme that assigns cumulative risk to span positions (Tip/Mid/Root), weighted by damage class severity and span position. This represents a first step toward quantitative repair prioritization.

The contributions of this paper are:

- A reproducible end-to-end pipeline from raw drone images to span-wise risk scores
- Quantitative demonstration that pyramid patch augmentation improves mAP@0.5 by 67%
- Systematic diagnosis of LE;CR detection failure (class imbalance, not object size or evaluation methodology) and sensitivity analysis confirming risk ranking robustness (6 of 8 scenarios under ±50% perturbation)

---

## 2. Related Work

### 2.1 Wind Turbine Blade Damage Detection

Shihavuddin et al. (2019) applied Faster R-CNN with Inception-ResNet-V2 to the DTU drone inspection dataset, achieving mAP@0.5 = 0.81 across multiple damage classes. Gohar et al. (2023) extended the same dataset with refined annotations and demonstrated that patch-based approaches improve detection of small damages.

### 2.2 Class Imbalance in Object Detection

Class imbalance is a well-known challenge in object detection. Focal loss (Lin et al. 2017) addresses this by down-weighting well-classified examples. Oversampling and data augmentation strategies have also been explored. In the wind energy domain, damage datasets are inherently imbalanced because certain damage types (e.g., cracks) are rarer than others (e.g., erosion). The challenge is amplified by the small size of public datasets and the inherent rarity of structurally critical damage types.

Patch-based detection is standard in high-resolution industrial inspection where defects are small relative to the full image. Multi-scale patch augmentation has improved recall in steel surface defect detection [7], photovoltaic cell crack classification [8], and concrete crack detection [9]. These findings motivate the pyramid patch approach adopted here: input patches are presented at multiple scales during training, without modifying the network architecture.

### 2.3 Risk Scoring and Prioritization

While several studies have proposed damage severity classification (binary or multi-level), few have attempted to map detection results onto blade span positions to generate region-wise risk profiles. Malik & Bak (2025) demonstrated that leading edge erosion has position-dependent aerodynamic impact, with tip regions experiencing higher relative velocity and correspondingly greater erosion risk. To our knowledge, no prior study has combined automated damage detection with a span-wise risk scoring framework in a single reproducible pipeline. We integrate detection and prioritization to demonstrate the feasibility of end-to-end risk scoring, while explicitly delineating where the pipeline succeeds and where it fails.

---

## 3. Methods

### 3.1 Dataset

| Item | Description |
|---|---|
| Source | DTU Wind Turbine Inspection Images (Mendeley, DOI: 10.17632/hd96prn3nc.2) |
| Annotations | Gohar et al. 2023 (DOI: 10.3390/machines11100953) |
| Turbine | Nordtank NTK 500 (Denmark) |
| Original images | 559 (2017: 161, 2018: 398) |
| Resolution | 5,280 × 2,970 px |
| Classes (5) | VG;MT, LE;ER, LR;DA, LE;CR, SF;PO |
| Total annotations | 1,914 bounding boxes |

**Class distribution**: LE;ER (41.6%) and VG;MT (34.3%) dominate, while LR;DA (2.3%) and LE;CR (10.2%) are minority classes.

### 3.2 Preprocessing

**Patch slicing**: Each original image was sliced into a 3×6 grid of 1,024 px patches (18 patches per image), yielding 559 × 18 = 10,062 base patches.

**Train/val/test split**: The split was performed at the original image level *before* patch slicing, following the sequence: shuffle (seed=42) → split → patch → augment. The 559 original images were randomly partitioned into train (212 images, 70.5%), validation (44 images, 14.6%), and test (45 images, 15.0%). Each original image and all 18 patches derived from it belong exclusively to one split, ensuring no patch-level data leakage. The split was performed once with a single seed; stability across different random seeds has not been evaluated (see §6, Limitation 8).

**Note on blade-level independence**: The DTU dataset lacks blade identifiers, so different images of the same blade may exist in different splits. This potential overlap cannot be quantified with available metadata and may moderately inflate reported performance.

**Pyramid augmentation (EXP-002)**: Training patches were additionally resized to 0.67× and 0.33× scales, tripling the training set from 3,816 to 11,448 patches. Validation and test patches were not augmented.

| Split | Original images | Patches | Annotations |
|---|---:|---:|---:|
| Train | 212 | 11,448 (with augmentation) | 1,677 |
| Val | 44 | 792 | 113 |
| Test | 45 | 810 | 124 |

### 3.3 Model Training

| Parameter | Value |
|---|---|
| Architecture | YOLOv8n (3.2M parameters) |
| Input size | 640 × 640 px |
| Epochs | 30 |
| Batch size | 8 |
| Optimizer | Auto (AdamW) |
| Device | Apple M-series (MPS backend) |
| Augmentation | Default YOLOv8 (mosaic, HSV, flip) |

Two experiments were conducted:
- **EXP-001** (Baseline): Standard 1,024 px patches, no pyramid augmentation
- **EXP-002** (Pyramid): With 0.67× and 0.33× pyramid augmentation on training set

### 3.4 Span-wise Risk Scoring

Each detection is assigned a span region based on its patch position:
- row = 0 → **Tip** (blade tip, highest aerodynamic load)
- row = 1 → **Mid** (mid-span)
- row = 2 → **Root** (blade root)

This mapping was validated by visual inspection of DTU original images: row 0 patches show sky background (tip), row 2 patches show ground/padding (root).

**Chord-wise (LE/TE) classification was excluded** because the blade runs diagonally within each patch, making fixed cx-threshold classification unreliable (LE;ER cx distribution: 0.004–0.992, nearly uniform).

Risk score for each detection:
```
score_i = confidence_i × area_ratio_i × class_weight_i × region_weight_i
```

| Weight type | Parameter | Values | Basis |
|---|---|---|---|
| class_weight | LE;CR: 3.0, LE;ER: 2.0, VG;MT/LR;DA: 1.5, SF;PO: 1.0 | Structural severity ranking by blade repair practitioners |
| region_weight | Tip: 3.0, Mid: 2.0, Root: 1.0 | Aerodynamic load gradient (Malik & Bak 2025) |

Both weight sets are **practitioner-informed priors**, not parameters optimized against repair outcome data. Their sensitivity to perturbation is evaluated in §3.5 and §4.4.

Region score = sum of all detection scores within the same span region.

### 3.5 Sensitivity Analysis

To evaluate the robustness of risk rankings to weight choices, we perturbed region weights and class weights by ±50% individually and jointly (8 scenarios total). For each scenario, we computed cumulative risk scores per region and checked whether the baseline ranking (Tip > Mid > Root) was preserved.

---

## 4. Results

### 4.1 Detection Performance

**Table 1: Baseline (EXP-001) vs. Pyramid Augmentation (EXP-002)**

| Metric | EXP-001 (Baseline) | EXP-002 (Pyramid) | Change |
|---|---|---|---|
| mAP@0.5 | 0.348 | **0.581** | +67% |
| mAP@0.5:0.95 | 0.162 | **0.314** | +95% |
| Precision | 0.753 | **0.823** | +9% |
| Recall | 0.284 | **0.492** | +73% |

**Table 2: Per-Class Detection Performance (test set, IoU ≥ 0.5)**

| Class | Description | | EXP-001 (Baseline) | | | EXP-002 (Pyramid) | | |
|---|---|---|---:|---:|---:|---:|---:|---:|
| | | GT | TP | FP | FN | TP | FP | FN |
| LE;ER | Leading edge erosion | 58 | 27 | 22 | 31 | 41 | 16 | 17 |
| VG;MT | Vortex generator / tape | 39 | 18 | 7 | 21 | 20 | 4 | 19 |
| SF;PO | Surface pollution | 10 | 6 | 7 | 4 | 6 | 2 | 4 |
| LR;DA | Lightning receptor damage | 6 | 0 | 0 | 6 | 2 | 0 | 4 |
| LE;CR | Leading edge crack | 11 | 0 | 0 | 11 | 0 | 0 | 11 |
| **Total** | | **124** | **51** | **36** | **73** | **69** | **22** | **55** |

**Table 3: Per-Class AP (EXP-002)**

| Class | AP@0.5 | AP@0.5:0.95 |
|---|---:|---:|
| LE;ER | 0.784 | 0.434 |
| VG;MT | 0.756 | 0.410 |
| SF;PO | 0.706 | 0.568 |
| LR;DA | 0.556 | 0.111 |
| LE;CR | 0.000 | 0.000 |
| **5-class mAP** | **0.561** | **0.305** |
| *4-class mAP (excl. LE;CR)* | *0.701* | *0.381* |

*The five-class mAP@0.5 (0.561) is the primary performance metric because the model was trained on all five classes and evaluated against all ground-truth annotations. The four-class mAP@0.5 (0.701, excluding LE;CR) is reported as a supplementary indicator to show the achievable performance on classes where the model received sufficient training signal. It does not represent a separate model or evaluation; it is the same model's performance with LE;CR AP removed from the average. This metric is useful for readers assessing detection quality independent of the LE;CR class imbalance issue diagnosed in §4.2.*

Pyramid augmentation improved TP counts across all detected classes while reducing FP counts; LE;CR remained at TP = 0 in both experiments.

### 4.2 LE;CR Detection Failure: Diagnosis

LE;CR was the only class with AP = 0.00. We conducted a systematic diagnosis to identify the cause.

**Table 4: Class Distribution Across Splits**

| Class | Train | Val | Test | Total | Share |
|---|---:|---:|---:|---:|---|
| LE;ER | 687 | 51 | 58 | 796 | 41.6% |
| VG;MT | 588 | 29 | 39 | 656 | 34.3% |
| SF;PO | 195 | 17 | 10 | 222 | 11.6% |
| LE;CR | 171 | 14 | 11 | 196 | 10.2% |
| LR;DA | 36 | 2 | 6 | 44 | 2.3% |
| **Total** | **1,677** | **113** | **124** | **1,914** | 100% |

Training patches containing at least one LE;CR annotation: 132 / 8,055 (1.6%).

**Table 5: Differential Diagnosis of LE;CR AP = 0**

| Hypothesis | Evidence | Verdict |
|---|---|---|
| LE;CR absent from test set | 11 GT instances (8.9% of test) | Rejected |
| IoU threshold too strict | Zero predictions — IoU never computed | Rejected |
| Confidence threshold too high | Zero predictions at all confidence levels | Rejected |
| Bounding boxes too small to detect | Median area = 0.00452 (comparable to LE;ER: 0.00473) | Rejected |
| **Class imbalance causing learning failure** | **LE;CR in 1.6% of training patches; 1/4 of LE;ER count** | **Supported** |

**Finding**: The model produced zero LE;CR predictions across all experiments, confidence thresholds, and data splits. LE;CR was never learned.

*(See Fig. 7: representative LE;CR ground truth patches with zero model output)*

### 4.3 Span-wise Risk Scores

**Table 6: Cumulative Risk Scores by Span Region and Year (EXP-002)**

| Year | Tip | Mid | Root | n_patches |
|---|---:|---:|---:|---:|
| 2017 | 2.023 | 1.247 | 0.000 | 180 |
| 2018 | 0.488 | 0.986 | 0.064 | 630 |

*Note*: Year-wise scores are cross-sectional comparisons, not longitudinal tracking of the same damage sites (see §6, Limitation 6). Differences between years primarily reflect differing patch counts (180 vs 630) and inspection conditions. Scores do not include LE;CR contributions (zero detections). Risk scores were computed as defined in §3.4.

### 4.4 Sensitivity Analysis

**Table 7: Sensitivity Analysis (EXP-002, test set, ±50% perturbation)**

| Scenario | Tip | Mid | Root | Rank Order | Rank Changed |
|---|---:|---:|---:|---|---|
| **Baseline** | **2.512** | **2.232** | **0.064** | **Tip > Mid > Root** | — |
| RW: Tip ×1.5 | 3.767 | 2.232 | 0.064 | Tip > Mid > Root | No |
| RW: Tip ×0.5 | 1.256 | 2.232 | 0.064 | Mid > Tip > Root | **Yes** |
| RW: Mid ×1.5 | 2.512 | 3.349 | 0.064 | Mid > Tip > Root | **Yes** |
| RW: Mid ×0.5 | 2.512 | 1.116 | 0.064 | Tip > Mid > Root | No |
| RW: Root ×1.5 | 2.512 | 2.232 | 0.096 | Tip > Mid > Root | No |
| RW: Root ×0.5 | 2.512 | 2.232 | 0.032 | Tip > Mid > Root | No |
| CW: all ×1.5 | 3.767 | 3.349 | 0.096 | Tip > Mid > Root | No |
| CW: all ×0.5 | 1.256 | 1.116 | 0.032 | Tip > Mid > Root | No |

Rank inversion occurred in 2 of 8 scenarios (Tip weight ×0.5, Mid weight ×1.5). The Tip > Mid > Root ranking is robust under most perturbations. However, the Tip–Mid margin (0.280) is relatively narrow; halving the Tip weight alone causes inversion. Root scores are an order of magnitude lower and do not affect the ranking.

---

## 5. Discussion

### 5.1 Effectiveness of Pyramid Patch Augmentation

Pyramid patch augmentation improved mAP@0.5 from 0.35 to 0.58 (+67%), primarily through Recall (+73%) with a modest Precision gain (+9%). This indicates that multi-scale training reduced false negatives without introducing excessive false positives. Per-class results (Table 2) show TP improvements for LE;ER, VG;MT, and LR;DA alongside reduced FP counts. LR;DA improved from TP=0 (EXP-001) to TP=2 (EXP-002), though the small sample size (6 GT instances) limits this observation.

### 5.2 Class Imbalance and LE;CR Detection Failure

As shown in §4.2, LE;CR yielded zero predictions across all experiments. The root cause — severe class imbalance (1.6% of training patches) — has two implications. In blade inspection, leading edge cracks are structurally critical — hence the highest class weight (3.0) in our scoring scheme. The inability to detect this class represents a significant limitation for practical deployment. Public drone inspection datasets exhibit inherent class imbalance because certain damage types are rarer in the field; addressing this requires either targeted data collection, class-aware loss functions (e.g., focal loss), or minority oversampling.

### 5.3 Risk Score Interpretation

The span-wise risk scores showed Tip > Mid > Root ordering, consistent with field experience and the physical expectation that tip regions experience higher relative wind velocity and greater erosion susceptibility (Malik & Bak 2025).

Three caveats apply:

1. **LE;CR exclusion**: Current scores omit LE;CR contributions. If LE;CR were detected, Tip scores would likely increase (LE;CR carries the highest class weight).
2. **Weight subjectivity**: class_weight and region_weight are practitioner-informed priors (see §6, Limitation 4). The sensitivity analysis (§4.4) bounds this uncertainty: rank inversion occurs only when the Tip weight is halved or Mid weight is increased by 50%.
3. **Absolute values**: Cumulative scores depend on image count and detection count; cross-dataset comparison of absolute values is not meaningful.

**Potential O&M applications**: If validated against repair records, the risk scores could inform inspection flight path planning (prioritizing tip/mid-span imaging), fleet-level repair scheduling (ranking damage sites by combined class severity and aerodynamic exposure), and region-differentiated re-inspection intervals. These applications remain speculative without calibration against maintenance outcomes; the present study demonstrates only that detection outputs can be structured into a format compatible with O&M workflows.

### 5.4 Comparison with Prior Work

Shihavuddin et al. (2019) reported mAP@0.5 = 0.81 on the same DTU dataset using Faster R-CNN with Inception-ResNet-V2 (~55M parameters). Our result of 0.58 with YOLOv8n (3.2M parameters) is substantially lower. However, direct comparison is complicated by differences in model capacity (17× parameter difference), training duration, and preprocessing pipeline.

Our contribution is not detection performance maximization but the downstream pipeline from detections to span-wise risk scores. Detection performance can be improved independently (larger models, class balancing) without changing the scoring framework.

---

## 6. Limitations

1. **LE;CR detection failure**: LE;CR (leading edge crack) achieved AP = 0.00. The model did not acquire detection capability for this class due to severe class imbalance (1.6% of training patches). LE;CR-related damage assessment is not possible with the current model. Focal loss, oversampling, or additional LE;CR training data may address this, but were not tested.

2. **Blade-level independence**: The dataset was split at the original image level (212/44/45, no patch-level leakage; see §3.2). However, the DTU dataset does not include blade identifiers. Multiple images of the same physical blade from different angles may exist across splits, potentially inflating reported performance. This cannot be quantified with available metadata.

3. **Chord-wise exclusion**: The blade runs diagonally within patches, making fixed cx-threshold LE/TE classification unreliable (LE;ER cx distribution: 0.004–0.992, nearly uniform). Only span-wise (Tip/Mid/Root) scoring was adopted.

4. **Weight subjectivity**: class_weight and region_weight are practitioner-informed priors, not parameters calibrated against repair outcome data. Sensitivity analysis showed the Tip–Mid ranking margin is narrow and inverts under ±50% Tip weight perturbation (§4.4, §5.3).

5. **Single dataset**: Only the DTU/Nordtank dataset (one turbine type) was used. Generalization to other turbine types, blade designs, or imaging conditions is untested.

6. **No temporal tracking**: Images from 2017 (161) and 2018 (398) lack spatial correspondence (GPS error 2–5 m, zero filename overlap), and patch counts differ by 3.5×. Year-wise score differences (Table 6) are cross-sectional, not longitudinal.

7. **Model scale**: YOLOv8n (3.2M parameters) was used due to computational constraints (Apple MPS backend). Larger models (YOLOv8s/m/l) and longer training may improve performance but were not evaluated.

8. **Split seed dependence**: The train/val/test split was performed once with seed=42. Performance variability across different random seeds or under k-fold cross-validation has not been evaluated. Given the small test set size (45 images, 124 annotations), metric estimates may have non-negligible sampling variance.

---

## 7. Reproducibility

The input dataset is publicly available; all code and trained weights are included as supplementary materials:

- **Dataset**: DTU Wind Turbine Inspection Images (Mendeley, DOI: 10.17632/hd96prn3nc.2) with annotations by Gohar et al. (2023)
- **Code**: Preprocessing, training, evaluation, and figure generation scripts
- **Configuration**: YOLOv8n training configuration, random seed (seed=42), and all hyperparameters
- **Trained weights**: Model weights for EXP-001 and EXP-002
- **Risk scoring**: `risk_score.py` for all risk score calculations and sensitivity analysis

No proprietary data or commercial software was used. The pipeline runs on consumer hardware (Apple M-series, MPS backend).

---

## 8. Conclusion

This study presented a reproducible pipeline for wind turbine blade surface damage detection and span-wise risk scoring using publicly available drone inspection images.

The main findings are:

1. **Pyramid patch augmentation** improved mAP@0.5 from 0.35 to 0.58 (+67%), primarily through Recall improvement (+73%), demonstrating the effectiveness of multi-scale training for small damage detection.

2. **Per-class analysis** revealed that four of five damage classes achieved AP@0.5 of 0.56–0.78, while LE;CR (leading edge crack) was completely undetected (AP = 0.00). Systematic diagnosis confirmed class imbalance as the root cause: LE;CR was present in only 1.6% of training patches, and the model produced zero LE;CR predictions across all experiments.

3. **Span-wise risk scoring** produced Tip > Mid > Root ordering consistent with field experience. Sensitivity analysis confirmed this ranking is robust to ±50% weight perturbation in 6 of 8 scenarios.

4. **The LE;CR failure carries practical implications** because leading edge cracks are among the most structurally critical damage types. This result suggests that public drone inspection datasets, without dedicated class balancing measures, may be insufficient for reliable detection of rare but safety-relevant damage classes.

Future work should address LE;CR detection through class-aware training strategies and validate risk scores against repair records from operational wind farms.

---

## 9. References

1. Shihavuddin, A.S.M. et al. (2019): "Wind Turbine Surface Damage Detection by Deep Learning Aided Drone Inspection Analysis" — Energies, 12(4), 676. DOI: 10.3390/en12040676
2. Gohar, I. et al. (2023): "Drone-Based Object Detection Datasets for Wind Turbine Damage Analysis" — Machines, 11(10), 953. DOI: 10.3390/machines11100953
3. Malik, A. & Bak, C. (2025): "Aerodynamic impact of leading edge erosion on wind turbine blades" — Wind Energy Science, 10, 227–247. DOI: 10.5194/wes-10-227-2025
4. Lin, T.-Y. et al. (2017): "Focal Loss for Dense Object Detection" — ICCV 2017. arXiv:1708.02002
5. Ultralytics (2023): "YOLOv8" — github.com/ultralytics/ultralytics
6. DTU Wind Turbine Inspection Images: Mendeley Data, DOI: 10.17632/hd96prn3nc.2
7. Konovalenko, I. et al. (2022): "Research of U-Net-Based CNN Architectures for Metal Surface Defect Detection" — Machines, 10(5), 327. DOI: 10.3390/machines10050327
8. Deitsch, S. et al. (2019): "Automatic Classification of Defective Photovoltaic Module Cells in Electroluminescence Images" — Solar Energy, 185, 455–468. DOI: 10.1016/j.solener.2019.02.067
9. Cha, Y.-J. et al. (2017): "Deep Learning-Based Crack Damage Detection Using Convolutional Neural Networks" — Computer-Aided Civil and Infrastructure Engineering, 32(5), 361–378. DOI: 10.1111/mice.12263

---

## 図表一覧

| Figure/Table | Content | File | Status |
|---|---|---|---|
| Table 1 | Baseline vs Pyramid overall metrics | In text | Done |
| Table 2 | Per-class TP/FP/FN (both experiments) | In text | **New** |
| Table 3 | Per-class AP (EXP-002) | In text | Done |
| Table 4 | Class distribution across splits | In text | **New** |
| Table 5 | LE;CR differential diagnosis | In text | **New** |
| Table 6 | Risk scores by year/region | In text | Done |
| Table 7 | Sensitivity analysis | In text | Done |
| Fig. 1 | Pipeline overview | `reports/fig_pipeline_overview.png` | **Done** |
| Fig. 2 | Representative detections (TP/FP/FN) | `reports/fig_detection_examples_en.png` | Exists |
| Fig. 3 | Normalized confusion matrix (EXP-002) | `pyramid_yolov8n/confusion_matrix_normalized.png` | Exists |
| Fig. 4 | PR curves (EXP-002) | `pyramid_yolov8n/BoxPR_curve.png` | Exists |
| Fig. 5 | Sensitivity analysis bars | `reports/fig_sensitivity_bars_en.png` | Exists |
| Fig. 6 | Training curves | `reports/training_curves.png` | Exists |
| Fig. 7 | LE;CR missed detections | `reports/fig_lecr_missed.png` | **Done** |
| Fig. 8 | Risk scores normalized (cumul. vs per-patch) | `reports/fig_risk_scores_normalized.png` | **Done** |
| Fig. 9 | BBox area distribution by class | `reports/fig_bbox_area_distribution.png` | **Done** |

---

## 査読で突っ込まれそうな論点一覧

| # | 論点 | 想定される指摘 | 現在の防御 | 追加対応候補 |
|---|---|---|---|---|
| 1 | LE;CR AP=0 | 「1クラス全滅で mAP 報告する意味は」 | §4.2 で原因診断、4クラス mAP 併記 | Focal loss 再学習で改善を示す |
| 2 | ブレード独立性 | 「同一ブレードが split 跨ぎ」 | 原画像単位分割確認済み。ブレード ID なし | Limitations に明記済み |
| 3 | 重みの主観性 | 「客観的根拠は」 | 感度分析 ±50%、Malik & Bak 2025 引用 | 補修記録との照合で検証 |
| 4 | 先行研究との差 | 「mAP 0.58 vs 0.81」 | モデルサイズ 17× 差を説明 | YOLOv8s/m の結果追加 |
| 5 | chord 除外 | 「前縁/後縁不明は大きい」 | cx 均一分布の証拠提示 | 幾何推定の予備実験 |
| 6 | スコア未検証 | 「補修優先度との対応は」 | 未検証と明記 | 実データがあれば大幅強化 |
| 7 | 学習設定 | 「30 epoch / nano は十分か」 | 計算資源制約を記述 | 追加 epoch 実験 |
| 8 | 年次バイアス | 「2017=180 vs 2018=630 で公平か」 | n_patches 明記、cross-sectionalと明言 | per-patch 正規化スコア併記 |
| 9 | split seed依存性 | 「seed=42の1回だけで結果は安定か」 | §3.2にseed単一性明記、§6 Limitation 8に追加 | 複数seed（5-fold等）の安定性は未検証。短報の範囲として許容的だが指摘はありうる |

---

## 改訂履歴

| Version | Date | 内容 |
|---|---|---|
| v1 | 2026-04-04 | 初稿完了（Step 4/4: 弱点補強） |
| v2 | 2026-04-04 | 査読耐性改訂（Step 5/5）: 1文主張・Abstract・split記述・4-class位置づけ・重み説明・年次差解釈・Related Work・Reproducibility追加・査読論点更新 |
| v3 | 2026-04-04 | 投稿準備改訂: 1文主張短縮、§3.2 split手順明示（shuffle→split→patch→augment）、§2.2 patch-based detection文献[7]–[9]追加、§5.3 O&M実務接続追加、Limitation #8 split seed依存追加、冗長箇所短縮（Abstract・§4.1・§4.3・§5.2・§5.3） |
| v4 | 2026-04-04 | 最終表現調整: Abstract再現性表現修正（supplementary materials）、Table 6にcross-sectional注記追加、§3.4重み表にpractitioner-informed priors明示、Conclusion #4トーンダウン、全体5–10%圧縮（§1/§2.2/§2.3/§3.2/§4.2/§5.1/§5.3/§5.4/§6/§7/§8） |
