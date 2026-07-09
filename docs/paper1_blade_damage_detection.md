# Paper 1: Wind Turbine Blade Surface Damage Detection and Span-wise Risk Scoring Using Drone Inspection Images with Pyramid Patch Augmentation

**ステータス**: v9.9（v9.7 = mAP 案a 適用（test 主指標化 0.38→0.56, +46%）→ v9.8 = Codex レビュー反映 → v9.9 = 再現パッケージ棚卸しによる §3.3/§7 の誤記修正：ultralytics 8.3.x→**8.4.33**、シード記述の精密化（分割 seed=42／学習 seed=0）、学習スクリプト記述の実態整合）
**最終更新**: 2026-07-05（詳細は `tools/reference_audit/paper123_consistency_audit_2026-07-02.md`・`codex_review_decisions_2026-07-05.md`・`repro_package_inventory_2026-07-05.md`）

---

## 1文主張

> 公開ドローン画像のアノテーション付き301枚にピラミッドパッチ拡張付きYOLOv8nを適用し、5損傷クラス中4クラスでAP@0.5 = 0.56–0.78（test mAP = 0.56、ベースライン比 +46%）を得たが、LE;CR（訓練パッチの1.2%）はゼロ検出でありクラス不均衡が検出限界を規定する。スパン方向リスクスコア（Tip > Mid > Root）は±50%重み摂動下で8中6シナリオ（実質は部位重み個別6中4、クラス重み一括2件は自明保存）でランクが保存された。

---

## Abstract

Wind turbine blade surface damage detection using drone inspection images is increasingly important for condition-based maintenance planning. This study presents a reproducible pipeline for detecting surface damage and computing span-wise risk scores from publicly available drone inspection images of the DTU/Nordtank turbine.

We applied YOLOv8n with pyramid patch augmentation to the 301 annotated original images of the public DTU dataset (13,050 patches after slicing and augmentation) across five damage classes. The dataset was split at the original image level (train: 212, val: 44, test: 45; seed=42) to prevent patch-level leakage; blade-level independence cannot be guaranteed with the available metadata.

Pyramid patch augmentation improved held-out test mAP@0.5 from 0.38 (baseline) to 0.56 (+46%); on the validation set used for model selection, the best-epoch improvement was 0.35 to 0.58 (+67%). Four of five classes achieved test AP@0.5 of 0.56–0.78, while LE;CR yielded AP = 0.00 due to severe class imbalance (1.2% of training patches). The four-class test mAP@0.5 (excluding LE;CR) was 0.70, reported as a supplementary indicator.

A span-wise risk scoring scheme (Tip/Mid/Root) using practitioner-informed weights produced rankings consistent with field experience. Sensitivity analysis (±50% perturbation, 8 scenarios) confirmed rank preservation in 6 of 8 cases (4 of the 6 substantive region-weight perturbations; the two uniform class-weight scalings preserve rank trivially). Year-wise score differences reflect inspection conditions, not damage progression. The primary contribution is the end-to-end pipeline from detection outputs to region-wise risk scores; the detection backbone can be upgraded independently to improve input quality. All code, configuration, and trained weights are included as supplementary materials.

---

## 1. Introduction

Leading edge erosion (LEE) is a near-universal phenomenon on aging wind turbine blades and is increasingly recognized as a multiscale, multiphysics process involving meteorology, aerodynamics, materials science, and computational mechanics (Mishnaevsky et al. 2021 [17]). Empirical surveys confirm this ubiquity: an inspection of 201 rotor blades after 14 years of operation found visible erosion on 174 blades (87%), with 50% showing severe levels of LEE (cited in Law and Koutsos 2020 [18]). The operational urgency was demonstrated by Ørsted's 2016 repair campaign at the Anholt Offshore Wind Farm (Mishnaevsky et al. 2021 [17]). The associated economic impact is substantial: leading edge erosion of blades has been estimated to cost the European offshore wind energy sector €56–75 million per year (Mishnaevsky et al. 2021 [17]), while a UK-focused study estimated the 2019 nationwide impact at £76.5 million based on observed AEP losses of 1.75% (medium erosion) to 4.93% (worst-affected turbine) across 18 operational wind farms (Law and Koutsos 2020 [18]).

Drone-based inspection has largely replaced rope-access and ground-based methods for wind turbine blade assessment, generating large volumes of high-resolution imagery. However, converting these images into actionable maintenance priorities remains manual and subjective. Deep learning–based damage detection has shown promise (Shihavuddin et al. 2019; Gohar et al. 2023), yet most studies focus on detection performance (mAP) without addressing the downstream question: *which blade region should be prioritized for repair?*

This study addresses two gaps:

1. **Detection with limited data**: Public drone inspection datasets are small and exhibit severe class imbalance. We investigate how pyramid patch augmentation can improve detection performance under these constraints, and explicitly diagnose where class imbalance causes complete detection failure.

2. **Span-wise risk scoring**: We extend detection results into a region-wise risk scoring scheme that assigns cumulative risk to span positions (Tip/Mid/Root), weighted by damage class severity and span position. This represents a first step toward quantitative repair prioritization.

In a future inspection regime where 2D screening identifies candidates for detailed 3D assessment, the reliability of the 2D screening stage — particularly its Recall (ability to avoid missed detections) — becomes a critical bottleneck for the entire degradation monitoring pipeline.

The contributions of this paper are:

- A reproducible end-to-end pipeline from raw drone images to span-wise risk scores, designed as a screening layer in a potential 2D–3D two-stage inspection framework
- Quantitative demonstration that pyramid patch augmentation improves test-set mAP@0.5 by 46% (0.38 → 0.56; validation best-epoch basis: +67%)
- Systematic diagnosis of LE;CR detection failure (class imbalance, not object size or evaluation methodology) and sensitivity analysis confirming risk ranking robustness (6 of 8 scenarios under ±50% perturbation; 4 of 6 substantive)

---

## 2. Related Work

### 2.1 Wind Turbine Blade Damage Detection

Recent surveys [10][11] highlight the rapid growth of deep learning methods for wind turbine blade inspection, particularly YOLO-based approaches on public datasets.

Shihavuddin et al. (2019) released the publicly-available DTU Drone Inspection dataset (Nordtank turbine, 701 images) and applied Faster R-CNN with multiple CNN backbones. Their best reported result (Inception-ResNet-V2 with pyramid+patching+regular augmentation) achieved mAP = 81.1% at IoU = 0.3 on the non-public EasyInspect dataset (4 classes); per-backbone results on the public DTU dataset are not reported in the same form. Gohar et al. (2023) re-annotated the publicly-available DTU dataset for 5 defect classes and reported mAP@0.5 of 81.3% (YOLOv5) and 73.2% (Faster-RCNN) under their patch-based inference scenario, both at the standard IoU = 0.5 protocol. Several recent studies have applied modified YOLOv8-based architectures to blade defect detection: YOLO-Wind [12] reported 83.9% mAP@0.5 on the DTU dataset and DMR-YOLO [13] 82.2% on the same dataset, while DCW-YOLO [14] (93.7%) and AUD-YOLO [15] (92%) were evaluated on an independently collected dataset of 600 images from Liaoning/Jiangsu wind farms. These works focus on maximizing detection accuracy through architectural changes; the downstream mapping from detections to maintenance-relevant risk prioritization has received less attention. Beyond detection, areal quantification approaches have also been explored: Aird et al. (2023) [20] compared supervised (Mask R-CNN) and unsupervised (pixel intensity thresholding and shadow ratio) methods on 140 confidential field images, classifying damage into shallow (pits, marring) and deep (gouges, delamination) categories, with both methods identifying approximately 65% of total damage area; their pixel-level evaluation is not directly comparable to bounding-box mAP metrics employed here.

### 2.2 Class Imbalance in Object Detection

Class imbalance is a well-known challenge in object detection. Focal loss (Lin et al. 2017) addresses this by down-weighting well-classified examples. Oversampling and data augmentation strategies have also been explored. In the wind energy domain, damage datasets are inherently imbalanced because certain damage types (e.g., cracks) are rarer than others (e.g., erosion). The challenge is amplified by the small size of public datasets and the inherent rarity of structurally critical damage types.

Patch-based detection is standard in high-resolution industrial inspection where defects are small relative to the full image. The SAHI framework (Akyon et al. 2022) [16] proposes a generic pipeline that combines slicing-aided fine-tuning (training-time patch augmentation) with slicing-aided inference (test-time slicing followed by NMS merging of overlapping detections). Patch-based training has been applied to small-defect detection in industrial inspection contexts, including steel surface defect detection [7], photovoltaic cell crack classification [8], and concrete crack detection [9]. These findings motivate the pyramid patch approach adopted here: input patches are presented at multiple discrete scales during training while preserving standard single-scale inference at deployment. Our approach differs from SAHI's slicing-aided fine-tuning in that patches are explicitly presented at distinct scale levels rather than slice-and-resize augmentation, and we do not employ slicing-aided inference at test time.

### 2.3 Risk Scoring and Prioritization

While several studies have proposed damage severity classification (binary or multi-level), few have attempted to map detection results onto blade span positions to generate region-wise risk profiles. The position-dependent nature of aerodynamic loading along the blade span is a well-established principle in wind turbine aerodynamics (Burton et al., *Wind Energy Handbook*), where tip regions experience higher relative wind velocity than root regions. Malik & Bak (2025) used aeroelastic simulations with leading-edge erosion modeled as aerofoil roughness on the outer 15% of blade length and reported AEP losses of 0.82% (mild), 1.46% (severe), and up to 2.14% under high-turbulence conditions, supporting the focus on outer-span erosion.

Industry-standard severity classification frameworks have also been formalized: the IEA Wind Task 46 system (Maniaci et al. 2022 [19]) defines a four-criterion scale—Visual Condition (with/without leading-edge protection), Mass Loss, Aerodynamic Performance, and Blade Integrity—across six severity levels (0–5), with severity assigned via the rule "when 5% of blade span is in a given class the blade is considered that severity rating." The risk scoring framework developed in the present study operates at the pre-classification detection stage: it detects and prioritizes damage features for repair planning, rather than assigning standardized severity ratings to the blade as a whole. The relationship between detection-derived region scores and IEA Wind Task 46 severity categories is left as a direction for future work.

To our knowledge, no prior study on the DTU dataset has combined automated damage detection with a span-wise risk scoring framework in a single reproducible pipeline, though this claim is limited by the rapid growth of the literature. We integrate detection and prioritization to demonstrate the feasibility of end-to-end risk scoring, while explicitly delineating where the pipeline succeeds and where it fails.

---

## 3. Methods

The overall pipeline — from raw drone images through patch slicing, augmentation, detection, and span-wise risk scoring — is illustrated in Fig. 1.

### 3.1 Dataset

| Item | Description |
|---|---|
| Source | DTU Wind Turbine Inspection Images (Mendeley, DOI: 10.17632/hd96prn3nc.2) |
| Annotations | Gohar et al. 2023 (DOI: 10.3390/machines11100953) |
| Turbine | Nordtank NTK 500 (Denmark) |
| Original images (annotated) | 301 of the 701 public images (2017: 57, 2018: 244) |
| Resolution | 5,280 × 2,970 px |
| Classes (5) | VG;MT, LE;ER, LR;DA, LE;CR, SF;PO |
| Total annotations | 1,914 bounding boxes |

**Class distribution**: LE;ER (41.6%) and VG;MT (34.3%) dominate, while LR;DA (2.3%) and LE;CR (10.2%) are minority classes.

### 3.2 Preprocessing

**Patch slicing**: Each original image was sliced into a 3×6 grid of 1,024 px patches (18 patches per image), yielding 301 × 18 = 5,418 base patches.

**Train/val/test split**: The split was performed at the original image level *before* patch slicing, following the sequence: shuffle (seed=42) → split → patch → augment. The 301 annotated original images were randomly partitioned into train (212 images, 70.4%), validation (44 images, 14.6%), and test (45 images, 15.0%). Each original image and all 18 patches derived from it belong exclusively to one split, ensuring no patch-level data leakage. The split was performed once with a single seed; stability across different random seeds has not been evaluated (see §6, Limitation 8).

**Note on blade-level independence**: The DTU dataset lacks blade identifiers, so different images of the same blade may exist in different splits. This potential overlap cannot be quantified with the available metadata and may moderately inflate reported performance.

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
| Framework | ultralytics==8.4.33 (pinned in supplementary `requirements_phase1.txt`) |
| Python | 3.11.x |
| Input size | 640 × 640 px |
| Epochs | 30 |
| Batch size | 8 |
| Optimizer | Auto (AdamW) |
| Initial learning rate | 0.01 (ultralytics default) |
| Final learning rate | 0.01 × lrf (lrf=0.01, i.e., final lr ≈ 0.0001) |
| Weight decay | 0.0005 (ultralytics default) |
| Early stopping | Not used (fixed 30 epochs) |
| Device | Apple M-series (MPS backend) |
| Augmentation | Default YOLOv8 (mosaic, HSV jitter, horizontal flip) |

**Augmentation note**: "Default YOLOv8" augmentations vary by ultralytics version. The key augmentation parameters used were: mosaic=1.0, hsv_h=0.015, hsv_s=0.7, hsv_v=0.4, flipud=0.0, fliplr=0.5, close_mosaic=20 (mosaic disabled at epoch 20). The exact configuration is recorded in the supplementary training configuration file.

**MPS backend note**: Training was conducted on Apple MPS (Metal Performance Shaders). MPS may produce numerically different results from CUDA due to differences in floating-point operation ordering. Results should be verified on CUDA for exact reproducibility.

Training convergence is shown in Fig. 6; both training loss and validation mAP plateaued before epoch 30, suggesting that the fixed epoch budget was sufficient for this dataset size.

Two experiments were conducted:
- **EXP-001** (Baseline): Standard 1,024 px patches, no pyramid augmentation
- **EXP-002** (Pyramid): With 0.67× and 0.33× pyramid augmentation on the training set

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
| region_weight | Tip: 3.0, Mid: 2.0, Root: 1.0 | Span-wise aerodynamic load gradient (general wind turbine aerodynamics; see Burton et al. *Wind Energy Handbook*). Outer-span erosion focus consistent with Malik & Bak (2025). Practitioner-informed priors |

Both weight sets are **practitioner-informed priors**, not parameters optimized against repair outcome data. Their sensitivity to perturbation is evaluated in §3.5 and §4.4.

Region score = sum of all detection scores within the same span region.

### 3.5 Sensitivity Analysis

To evaluate the robustness of risk rankings to weight choices, we perturbed region weights and class weights by ±50% individually and jointly (8 scenarios total). For each scenario, we computed cumulative risk scores per region and checked whether the baseline ranking (Tip > Mid > Root) was preserved.

---

## 4. Results

### 4.1 Detection Performance

All headline performance figures in this paper are reported on the held-out test set (45 original images, 810 patches), evaluated with the final weights of each experiment (best validation epoch). The validation set was used for model and epoch selection only; validation metrics are reported in Table 1b for transparency.

**Table 1: Baseline (EXP-001) vs. Pyramid Augmentation (EXP-002), test set**

| Metric | EXP-001 (Baseline) | EXP-002 (Pyramid) | Change* |
|---|---|---|---|
| mAP@0.5 | 0.383 | **0.561** | +46% |
| mAP@0.5:0.95 | 0.192 | **0.305** | +59% |
| Precision | 0.424 | **0.691** | +63% |
| Recall | 0.285 | **0.425** | +49% |

*The Change column shows relative change from the baseline (EXP-001) metric value, computed as (EXP-002 − EXP-001) / EXP-001 × 100%.

**Table 1b: Validation metrics (best epoch, used for model/epoch selection)**

| Metric | EXP-001 (Baseline) | EXP-002 (Pyramid) | Change* |
|---|---|---|---|
| mAP@0.5 | 0.348 | **0.581** | +67% |
| mAP@0.5:0.95 | 0.162 | **0.314** | +95% |
| Precision | 0.753 | **0.823** | +9% |
| Recall | 0.284 | **0.492** | +73% |

The validation-based improvement (+67% in mAP@0.5) is larger than the test-based improvement (+46%), as expected when the best epoch is selected on the validation set. The Precision/Recall decomposition also differs between the two sets: on validation the gain is recall-driven (+73% Recall vs. +9% Precision), whereas on the test set both improve substantially (+63% Precision, +49% Recall; see the metric provenance note below Table 3).

**Table 2: Per-Class Detection Performance (test set, IoU threshold = 0.5)**

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

**Metric provenance**: Table 1 and Table 3 are computed with ultralytics `model.val()` on the test split with a confidence filter of 0.25 (identical configuration for both experiments). AP is derived from the precision–recall curve over the retained predictions; the reported Precision/Recall correspond to the F1-optimal point of that curve, not to a fixed threshold. Table 2 reports raw TP/FP/FN counts at a fixed confidence threshold of 0.25. Table 1b reports the standard ultralytics training-time validation metrics (best epoch).

Representative detection examples (true positives, false positives, and false negatives) are shown in Fig. 2. The normalized confusion matrix (Fig. 3) illustrates inter-class confusion patterns, and Precision–Recall curves for each class are presented in Fig. 4.

Pyramid augmentation improved TP counts across all detected classes while reducing FP counts; LE;CR remained at TP = 0 in both experiments. In per-class test AP@0.5 terms, the baseline (EXP-001) achieved 0.538 (LE;ER), 0.704 (VG;MT), 0.672 (SF;PO), and 0.000 for both LR;DA and LE;CR; pyramid augmentation raised LE;ER to 0.784 and enabled LR;DA detection (0.556), while LE;CR remained at 0.000.

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

Training patches containing at least one LE;CR annotation: 132 / 11,448 (1.2%).

**Table 5: Differential Diagnosis of LE;CR AP = 0**

| Hypothesis | Evidence | Verdict |
|---|---|---|
| LE;CR absent from test set | 11 GT instances (8.9% of test) | Rejected |
| IoU threshold too strict | Zero predictions — IoU never computed | Rejected |
| Confidence threshold too high | Zero predictions at all confidence levels | Rejected |
| Bounding boxes too small to detect | Median area = 0.00452 (comparable to LE;ER: 0.00473) | Rejected |
| **Class imbalance causing learning failure** | **LE;CR in 1.2% of training patches; 1/4 of LE;ER count** | **Supported** |

Focal loss and minority oversampling are known mitigation strategies for class imbalance but were not tested in this study because the primary objective was to establish the detection-to-risk-scoring pipeline rather than to optimize per-class detection performance.

**Finding**: The model produced zero LE;CR predictions across all experiments, confidence thresholds, and data splits. LE;CR was never learned. The bounding box area distribution by class (Fig. 9) confirms that LE;CR objects are not anomalously small — their median area is comparable to LE;ER — ruling out object size as the cause of detection failure.

*(See Fig. 7: representative LE;CR ground truth patches with zero model output)*

### 4.3 Span-wise Risk Scores

**Table 6: Cumulative Risk Scores by Span Region and Year (EXP-002)**

| Year | Tip | Mid | Root | n_patches |
|---|---:|---:|---:|---:|
| 2017 | 2.023 | 1.247 | 0.000 | 180 |
| 2018 | 0.488 | 0.986 | 0.064 | 630 |

*Notes*: `n_patches` denotes the total number of test-set patches evaluated for that year (each original image yields 18 patches from the 3×6 grid; e.g., 2017: 10 test images × 18 = 180 patches, 2018: 35 test images × 18 = 630 patches). Year-wise scores are cross-sectional comparisons, not longitudinal tracking of the same damage sites (see §6, Limitation 6). Differences between years primarily reflect differing patch counts (180 vs 630) and inspection conditions. Scores do not include LE;CR contributions (zero detections). Risk scores were computed as defined in §3.4. Normalized risk score distributions (cumulative and per-patch) are visualized in Fig. 8.

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

Rank inversion occurred in 2 of 8 scenarios (Tip weight ×0.5, Mid weight ×1.5), as visualized in Fig. 5. The Tip > Mid > Root ranking is robust under most perturbations. However, the Tip–Mid margin (0.280) is relatively narrow; halving the Tip weight alone causes inversion. Root scores are an order of magnitude lower and do not affect the ranking.

*Note: scaling all class weights jointly (CW all ×1.5 / ×0.5) multiplies every score by the same constant, so the ranking is preserved trivially in those two scenarios. The substantive sensitivity test therefore consists of the six individual region-weight scenarios, of which four preserved the ranking.*

---

## 5. Discussion

### 5.1 Effectiveness of Pyramid Patch Augmentation

Pyramid patch augmentation improved test mAP@0.5 from 0.38 to 0.56 (+46%), with both Precision (+63%) and Recall (+49%) improving (Table 1); on the test set it reduced both false negatives (73 → 55) and false positives (36 → 22) at the fixed counting threshold of 0.25 (Table 2). On the validation set the gain was recall-driven (+73% Recall vs. +9% Precision, Table 1b). Per-class results (Table 2) show TP improvements for LE;ER, VG;MT, and LR;DA alongside reduced FP counts. LR;DA improved from TP=0 (EXP-001) to TP=2 (EXP-002), though the small sample size (6 GT instances) limits the reliability of this comparison.

### 5.2 Class Imbalance and LE;CR Detection Failure

As shown in §4.2, LE;CR yielded zero predictions across all experiments. The most supported explanation — severe class imbalance (1.2% of training patches; §4.2) — has two implications. First, in blade inspection, leading edge cracks are structurally critical — hence the highest class weight (3.0) in our scoring scheme — and the inability to detect this class represents a significant limitation for practical deployment. Second, public drone inspection datasets exhibit inherent class imbalance because certain damage types are rarer in the field; addressing this requires either targeted data collection, class-aware loss functions (e.g., focal loss), or minority oversampling.

### 5.3 Risk Score Interpretation

The span-wise risk scores showed Tip > Mid > Root ordering, consistent with field experience and the physical expectation that tip regions experience higher relative wind velocity (a general principle of blade element momentum theory). This ordering is also consistent with the outer-span erosion focus reported by Malik & Bak (2025), who applied leading-edge erosion to the outer 15% of blade length and quantified AEP losses.

Three caveats apply:

1. **LE;CR exclusion**: Current scores omit LE;CR contributions. If LE;CR were detected, Tip scores would likely increase (LE;CR carries the highest class weight).
2. **Weight subjectivity**: class_weight and region_weight are practitioner-informed priors (see §6, Limitation 4). The sensitivity analysis (§4.4) bounds this uncertainty: rank inversion occurs only when the Tip weight is halved or the Mid weight is increased by 50%.
3. **Absolute values**: Cumulative scores depend on image count and detection count; cross-dataset comparison of absolute values is not meaningful.

**Potential O&M applications**: The risk scoring framework outputs region-wise scores in a format compatible with O&M decision-making — e.g., ranking blade regions by severity or comparing damage profiles across turbines. However, specific thresholds and practical utility remain unvalidated; the present study demonstrates that detection outputs can be structured into this format, not that the format improves maintenance outcomes. Validation against repair records from operational wind farms is required before any O&M application can be claimed.

The industrial relevance of detection-driven prioritization is reinforced by the empirical economic data: Law and Koutsos (2020) [18] reported average AEP losses of 1.75% (medium erosion) to 4.93% (worst-affected turbine) on 18 operational UK wind farms, with a UK-wide 2019 financial impact of £76.5 million; Mishnaevsky et al. (2021) [17] reviewed comparable estimates at €56–75 million per year across the European offshore sector. Risk-scoring frameworks that prioritize repair targets by region can, in principle, support the operational decisions underlying these aggregated losses, though validation against repair-record outcomes remains an open task.

### 5.4 Comparison with Prior Work

Our test mAP@0.5 of 0.56 is lower than recent results on related datasets, but a strict apples-to-apples comparison is not possible because evaluation protocols differ across studies. On the publicly-available DTU dataset (Gohar et al. 2023 annotations, 5 classes, IoU=0.5), Gohar et al. reported mAP@0.5 of 81.3% (YOLOv5) and 73.2% (Faster-RCNN) under patch-based inference. Shihavuddin et al. (2019) reported mAP = 81.1% but at IoU = 0.3 on the non-public EasyInspect dataset (4 classes), which is not directly comparable to ours. YOLO-Wind [12] reports 83.9% and DMR-YOLO [13] 82.2% on the DTU dataset, while DCW-YOLO [14] (93.7%) and AUD-YOLO [15] (92%) report their results on an independently collected dataset of 600 images rather than DTU. The gap between our 0.56 and these published values therefore reflects a combination of (i) differences in evaluation protocol (IoU threshold, dataset version, class taxonomy, public vs. non-public test set), and (ii) a deliberate design choice in this study: the detection module uses unmodified YOLOv8 to keep the pipeline simple and reproducible, rather than maximizing detection accuracy through architectural changes.

To verify that this gap is not attributable to model capacity, we trained YOLOv8s (11.1M parameters, 3.5× larger than YOLOv8n) on the same pyramid-augmented dataset under identical conditions (30 epochs, seed=0, CUDA T4). Table 3b summarizes the comparison.

**Table 3b: Model Scale Comparison (Pyramid Augmented Data, 30 epochs, CUDA T4; validation set, best epoch)**

| Model | Params | mAP@0.5 | mAP@0.5:0.95 | P | R |
|---|---|---|---|---|---|
| YOLOv8n (EXP-002) | 3.2M | **0.581** | **0.314** | 0.823 | 0.492 |
| YOLOv8s | 11.1M | 0.575 | 0.309 | 0.872 | 0.487 |
| YOLOv8m | 25.9M | 0.425 | 0.216 | 0.855 | 0.341 |

Increasing model capacity did not improve mAP; performance degraded with larger models (YOLOv8m validation mAP@0.5 = 0.43, below YOLOv8n's 0.58; model selection was performed on the validation set, and the selected YOLOv8n's held-out test mAP@0.5 is 0.56, Table 3). This indicates that the bottleneck lies in data characteristics (class imbalance, dataset size of 301 annotated original images, annotation granularity) rather than model capacity. Larger models likely require more training data or epochs to converge — the 30-epoch budget may be insufficient for YOLOv8m (25.9M parameters) given this dataset size. The scoring framework proposed in §3.4 is independent of the detection backbone; adopting architectural improvements from YOLO-Wind, DMR-YOLO, or AUD-YOLO would improve detection inputs without requiring changes to the risk scoring pipeline.

Newer architectures (YOLOv9, YOLOv10, YOLOv11) were not tested and may offer further improvements. Evaluating these within the proposed pipeline is a direction for future work.

Direct comparison with quantification-focused works employing different evaluation paradigms is also constrained: Aird et al. (2023) [20] reported pixel-level identification accuracies of 61–66% for total damage and 65–73% for deep damage on 140 confidential field images using Mask R-CNN with Feature Pyramid Network. These metrics—percent of pixels correctly classified relative to ground-truth annotations—are not directly comparable to bounding-box mAP@0.5 employed here, since the two paradigms answer different operational questions (areal extent vs. localization-and-classification). A unified evaluation across these paradigms is a direction for future work.

**Recall as the priority metric for screening**: If 2D detection serves as the first stage of a two-stage inspection framework (2D screening → 3D detailed assessment), Recall becomes the most critical metric — missed detections at the screening stage propagate as blind spots through the entire degradation monitoring pipeline. The current test-set Recall of 0.43 (Table 1) means that more than half of all damage instances would not be flagged for 3D follow-up, limiting the reliability of any downstream degradation prediction. Improving Recall — through class balancing, architectural changes, or additional training data — is therefore a prerequisite for integrating 2D screening into a practical inspection workflow.

---

## 6. Limitations

1. **LE;CR detection failure**: LE;CR achieved AP = 0.00 due to severe class imbalance (1.2% of training patches). LE;CR-related damage assessment is not possible with the current model. Focal loss and oversampling were not tested (scope limitation; see §4.2).

2. **Blade-level independence**: The DTU dataset does not include blade identifiers. Multiple images of the same physical blade may exist across splits, potentially inflating reported performance. This cannot be quantified with the available metadata.

3. **Chord-wise exclusion**: LE/TE classification was unreliable due to near-uniform cx distribution; only span-wise (Tip/Mid/Root) scoring was adopted.

4. **Weight subjectivity**: class_weight and region_weight are practitioner-informed priors, not calibrated against repair outcomes. The Tip–Mid ranking margin is narrow and inverts under ±50% Tip weight perturbation (§4.4).

5. **Single dataset and annotation dependency**: Only the DTU/Nordtank dataset (one turbine type, 301 annotated images) was used. Generalization to other turbine types or imaging conditions is untested. Detection results are also bounded by the annotation quality of Gohar et al. (2023), for which inter-annotator agreement was not assessed. The DTU Blade Defect Dataset (Scientific Data, 2026; 1,065 images, 6 classes) is a candidate for future cross-dataset validation.

6. **No temporal tracking**: Images from 2017 and 2018 lack spatial correspondence; year-wise score differences (Table 6) are cross-sectional, not longitudinal.

7. **Model scale and architecture scope**: Three YOLO variants were tested (YOLOv8n/s/m, 3.2M–25.9M parameters); mAP decreased with larger models (Table 3b), confirming that the bottleneck is data-related, not model capacity. However, architectural modifications ([12]–[15]) achieving 0.82–0.94 mAP@0.5 — YOLO-Wind and DMR-YOLO on the DTU dataset; DCW-YOLO and AUD-YOLO on an independently collected dataset — were not replicated. The mAP gap indicates that detection can be improved through architecture design rather than model scaling.

8. **Split seed dependence**: The train/val/test split was performed once with seed=42. Given the small test set (45 images, 124 annotations), metric estimates may have non-negligible sampling variance.

9. **Industry-standard severity alignment**: The detection classes used here (LE;ER, VG;MT, LR;DA, LE;CR, SF;PO) derive from the DTU dataset annotations and do not directly correspond to the four-criterion, six-level severity classification system proposed by IEA Wind Task 46 (Maniaci et al. 2022 [19]). Mapping detection outputs to these standardized categories—for instance, estimating Visual Condition or Aerodynamic Performance severity from cumulative damage scores—would enable industry-aligned reporting but requires severity-thresholding logic outside the scope of this study.

---

## 7. Reproducibility

The input dataset is publicly available; all code and trained weights are included as supplementary materials:

- **Dataset**: DTU Wind Turbine Inspection Images (Mendeley, DOI: 10.17632/hd96prn3nc.2) with annotations by Gohar et al. (2023)
- **Code**: Preprocessing, evaluation, and figure generation scripts; training was executed via the ultralytics API/CLI, with the complete training configuration preserved in each experiment's `args.yaml`
- **Configuration**: YOLOv8n training configuration (`args.yaml`, training seed=0) and the dataset split seed (seed=42, `preprocess.py`), with all hyperparameters
- **Trained weights**: Model weights for EXP-001 and EXP-002
- **Risk scoring**: `risk_score.py` for all risk score calculations and sensitivity analysis

No proprietary data or commercial software was used. The pipeline runs on consumer hardware (Apple M-series, MPS backend).

---

## 8. Conclusion

This study presented a reproducible pipeline that bridges automated damage detection and region-wise risk prioritization for wind turbine blade inspection. The detection backbone is deliberately simple (unmodified YOLOv8n) and separable from the scoring framework, so that future improvements in detection accuracy directly strengthen the downstream risk scores without requiring pipeline redesign.

The main findings are:

1. **Pyramid patch augmentation** improved held-out test mAP@0.5 from 0.38 to 0.56 (+46%; validation best-epoch basis: 0.35 to 0.58, +67%), improving both Precision and Recall on the test set, demonstrating the effectiveness of multi-scale training for small damage detection.

2. **Per-class analysis** revealed that four of five damage classes achieved AP@0.5 of 0.56–0.78, while LE;CR (leading edge crack) was completely undetected (AP = 0.00). Systematic diagnosis identified class imbalance as the most supported explanation (object size, confidence thresholding, and evaluation methodology were ruled out): LE;CR was present in only 1.2% of training patches, and the model produced zero LE;CR predictions across all experiments. Confirmation through class-balancing interventions (focal loss, oversampling) remains future work.

3. **Span-wise risk scoring** produced Tip > Mid > Root ordering consistent with field experience. Sensitivity analysis confirmed that this ranking is robust to ±50% weight perturbation in 6 of 8 scenarios (two of which are uniform class-weight scalings that preserve rank trivially; 4 of the 6 substantive scenarios preserved the ranking, §4.4).

4. **The LE;CR failure carries practical implications** because leading edge cracks are among the most structurally critical damage types. This result suggests that public drone inspection datasets, without dedicated class balancing measures, may be insufficient for reliable detection of rare but safety-relevant damage classes.

Future work should address LE;CR detection through class-aware training strategies and validate risk scores against repair records from operational wind farms. More broadly, improving Recall is a prerequisite for deploying 2D detection as a reliable screening layer in a two-stage inspection framework (2D screening → 3D detailed assessment), where missed detections at the screening stage directly limit the coverage of downstream degradation prediction.

---

## 9. References

1. Shihavuddin, A.S.M. et al. (2019): "Wind Turbine Surface Damage Detection by Deep Learning Aided Drone Inspection Analysis" — Energies, 12(4), 676. DOI: 10.3390/en12040676
2. Gohar, I. et al. (2023): "Slice-Aided Defect Detection in Ultra High-Resolution Wind Turbine Blade Images" — Machines, 11(10), 953. DOI: 10.3390/machines11100953
3. Malik, T.H. & Bak, C. (2025): "Challenges in detecting wind turbine power loss: the effects of blade erosion, turbulence, and time averaging" — Wind Energy Science, 10, 227–243. DOI: 10.5194/wes-10-227-2025
4. Lin, T.-Y. et al. (2017): "Focal Loss for Dense Object Detection" — ICCV 2017. arXiv:1708.02002
5. Ultralytics (2023): "YOLOv8" — github.com/ultralytics/ultralytics
6. DTU Wind Turbine Inspection Images: Mendeley Data, DOI: 10.17632/hd96prn3nc.2
7. Konovalenko, I. et al. (2022): "Research of U-Net-Based CNN Architectures for Metal Surface Defect Detection" — Machines, 10(5), 327. DOI: 10.3390/machines10050327
8. Deitsch, S. et al. (2019): "Automatic Classification of Defective Photovoltaic Module Cells in Electroluminescence Images" — Solar Energy, 185, 455–468. DOI: 10.1016/j.solener.2019.02.067
9. Cha, Y.-J. et al. (2017): "Deep Learning-Based Crack Damage Detection Using Convolutional Neural Networks" — Computer-Aided Civil and Infrastructure Engineering, 32(5), 361–378. DOI: 10.1111/mice.12263
10. Memari, M.; Shakya, P.; Shekaramiz, M.; Seibi, A.C.; Masoum, M.A.S. (2024): "Review on the Advancements in Wind Turbine Blade Inspection: Integrating Drone and Deep Learning Technologies for Enhanced Defect Detection" — IEEE Access. DOI: 10.1109/ACCESS.2024.3371493
11. Masita, K.; Hasan, A.N.; Shongwe, T.; Hilal, H.A. (2025): "Deep Learning in Defect Detection of Wind Turbine Blades: A Review" — IEEE Access. DOI: 10.1109/ACCESS.2025.3569799
12. Zhao, Z. & Li, T. (2025): "Enhancing wind turbine blade damage detection with YOLO-Wind" — Scientific Reports, 15, 18667. DOI: 10.1038/s41598-025-03639-8
13. Shi, L.; Wang, S.; Zhao, J.; Kuang, Z.; Wang, L.; Ma, L.; Yang, H.; Wang, H. (2026): "DMR-YOLO: An Improved Wind Turbine Blade Surface Damage Detection Method Based on YOLOv8" — Applied Sciences, 16(3), 1333. DOI: 10.3390/app16031333
14. Zou, L.; Chen, A.; Li, C.; Yang, X.; Sun, Y. (2024): "DCW-YOLO: An Improved Method for Surface Damage Detection of Wind Turbine Blades" — Applied Sciences, 14(19), 8763. DOI: 10.3390/app14198763
15. Zou, L.; Chen, A.; Yang, X.; Sun, Y. (2025): "An improved method of AUD-YOLO for surface damage detection of wind turbine blades" — Scientific Reports, 15, 5833. DOI: 10.1038/s41598-025-89864-7
16. Akyon, F.C.; Altinuc, S.O.; Temizel, A. (2022): "Slicing Aided Hyper Inference and Fine-Tuning for Small Object Detection" — IEEE International Conference on Image Processing (ICIP), 966–970. DOI: 10.1109/ICIP46576.2022.9897990
17. Mishnaevsky Jr., L.; Hasager, C.B.; Bak, C.; Tilg, A.-M.; Bech, J.I.; Doagou Rad, S.; Fæster, S. (2021): "Leading edge erosion of wind turbine blades: Understanding, prevention and protection" — Renewable Energy, 169, 953–969. DOI: 10.1016/j.renene.2021.01.044
18. Law, H.; Koutsos, V. (2020): "Leading edge erosion of wind turbines: Effect of solid airborne particles and rain on operational wind farms" — Wind Energy, 23(10), 1955–1965. DOI: 10.1002/we.2540
19. Maniaci, D.; MacDonald, H.; Paquette, J.; Clarke, R. (2022): "Leading Edge Erosion Classification System" — Technical Report from IEA Wind Task 46, Technical University of Denmark: Lyngby, Denmark. December 2022. Sandia Report SAND2023-11986R. URL: https://iea-wind.org/wp-content/uploads/2023/02/IEA-Wind-Task-46-Erosion-Classification-System-report.pdf
20. Aird, J.A.; Barthelmie, R.J.; Pryor, S.C. (2023): "Automated Quantification of Wind Turbine Blade Leading Edge Erosion from Field Images" — Energies, 16, 2820. DOI: 10.3390/en16062820

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
| 4 | 先行研究との差 | 「test mAP 0.56 vs 0.82–0.94」 | §5.4でmAP gap議論、YOLO-Wind/DMR-YOLO/DCW-YOLO/AUD-YOLO引用（データセット帰属明示）、アーキテクチャ非改変を明示 | YOLOv8s/m/YOLO-Wind再現実験 |
| 5 | chord 除外 | 「前縁/後縁不明は大きい」 | cx 均一分布の証拠提示 | 幾何推定の予備実験 |
| 6 | スコア未検証 | 「補修優先度との対応は」 | 未検証と明記 | 実データがあれば大幅強化 |
| 7 | 学習設定 | 「30 epoch / nano は十分か」 | 計算資源制約を記述 | 追加 epoch 実験 |
| 8 | 年次バイアス | 「2017=180 vs 2018=630 で公平か」 | n_patches 明記、cross-sectionalと明言 | per-patch 正規化スコア併記 |
| 9 | split seed依存性 | 「seed=42の1回だけで結果は安定か」 | §3.2にseed単一性明記、§6 Limitation 8に追加 | 複数seed（5-fold等）の安定性は未検証。短報の範囲として許容的だが指摘はありうる |
| 10 | アノテーション品質 | 「Gohar et al.のアノテーションは検証済みか」 | §6 Limitation 5に統合 | 独立アノテーションによる検証 |
| 11 | 単一アーキテクチャ＋検出性能gap | 「YOLOv8nだけでtest mAP 0.56は低い」 | §5.4で簡潔に認め、§6 Limitation 7に統合。パイプラインの主価値と分離 | 検出バックボーン改善実験 |

---

## 改訂履歴

| Version | Date | 内容 |
|---|---|---|
| v1 | 2026-04-04 | 初稿完了（Step 4/4: 弱点補強） |
| v2 | 2026-04-04 | 査読耐性改訂（Step 5/5）: 1文主張・Abstract・split記述・4-class位置づけ・重み説明・年次差解釈・Related Work・Reproducibility追加・査読論点更新 |
| v3 | 2026-04-04 | 投稿準備改訂: 1文主張短縮、§3.2 split手順明示（shuffle→split→patch→augment）、§2.2 patch-based detection文献[7]–[9]追加、§5.3 O&M実務接続追加、Limitation #8 split seed依存追加、冗長箇所短縮（Abstract・§4.1・§4.3・§5.2・§5.3） |
| v4 | 2026-04-04 | 最終表現調整: Abstract再現性表現修正（supplementary materials）、Table 6にcross-sectional注記追加、§3.4重み表にpractitioner-informed priors明示、Conclusion #4トーンダウン、全体5–10%圧縮（§1/§2.2/§2.3/§3.2/§4.2/§5.1/§5.3/§5.4/§6/§7/§8） |
| v5 | 2026-04-08 | 競合文献・再現性・制限事項追加: §2.1にYOLO-Wind/DMR-YOLO/DCW-YOLO/AUD-YOLO・サーベイ2件追加、§2.2にSAHI追加、§2.3の"To our knowledge"スコープ修正、§3.3に再現性詳細（lr/wd/early stopping/Python/ultralytics版/MPS注記）追加、§4.1に信頼度閾値明記・Fig.2-4参照追加、§4.2にFig.9参照、§4.3にFig.8参照、§4.4にFig.5参照、§5.4にmAP gap議論・YOLOv9/v10/v11言及追加、§5.3のO&M段落を559枚制約に合わせて弱化、§6にLimitation 9-11（アノテーション品質・単一アーキテクチャ・検出性能gap）追加、参考文献[10]-[16]追加、全図のbody text参照確認 |
| v6 | 2026-04-10 | 自己批判の過剰を整理: §5.4を短縮（弁明削除、貢献に再集中）、§2.1簡潔化（競合4件を1文に集約）、§2.3の競合重複削除、Limitations 11→8項目（#5にアノテーション品質統合、#7にアーキテクチャ＋性能gap統合、#10-11削除）、§5.3 O&M段落を意義と限界のバランスに再調整、Abstract・Conclusion冒頭にパイプライン主価値を明示 |
| v7 | 2026-04-12 | モデルスケール実験完了: §5.4 Table 3bにYOLOv8n/s/m 3モデル比較追加（n: 0.581, s: 0.554, m: 0.425 → モデル増大でmAP低下、データ側ボトルネック確認）。Limitation #7更新 |
| v8 | 2026-04-14 | 引用整合性修正（PDF精読による発見）: (1)§2.3 Malik 2025引用文脈修正（Tip領域の空力知識はBurton *Wind Energy Handbook*由来とし、Malik 2025はouter-span erosion focusの裏付けとして引用）、(2)§3.4 region_weightテーブルの根拠を一般空力知識+practitioner-informed priorsに修正、(3)§5.3のTip領域の表現を一般BEM理論に帰属、(4)§2.1/§5.4 AUD-YOLOのデータセットを独自収集600枚と明記（DTUと誤解を招く記述を修正）|
| v9 | 2026-04-26 | Shihavuddin 2019 引用文修正（全頁精読による発見）: Shihavuddin の最高 mAP=81.1% は (i) **IoU=0.3** での値（Paper 1 では mAP@0.5 と表記していたが論文 §2.4 で IoU=0.3 を明示使用）、(ii) **EasyInspect dataset（非公開）** での結果（公開された DTU dataset とは別物）、(iii) **Inception-ResNet-V2** backbone での結果（Faster R-CNN との表記は backbone を含めた総称として誤解を招く）。§2.1 と §5.4 の引用文を改訂し、Gohar 2023 の DTU dataset での mAP@0.5（YOLOv5: 81.3%, Faster-RCNN: 73.2%）を正しい比較対象として併記。§5.4 の「our 0.58 is substantially lower than Shihavuddin's 0.81」型の直接比較を、評価プロトコルの差異（IoU閾値・dataset・class分類）を明示する形に変更 |
| v9.1 | 2026-04-26 | Malik 2025 全17頁主張駆動精読による軽微修正: §2.3 line 62 の引用文「Malik & Bak (2025) **experimentally** applied leading-edge erosion to the outer 15%...」を「**used aeroelastic simulations with** leading-edge erosion modeled as aerofoil roughness on the outer 15%...」に修正。Malik 2025 は HAWC2 を用いたシミュレーション研究であり、wind tunnel 実験データ（Krog Kruse 2021 の P40/P400 sandpaper）は入力として参照したのみで、Malik 2025 自身が実験を実施したわけではない。Abstract も "simulated erosion" と明記。AEP 数値（0.82%/1.46%/2.14%）と outer 15% の特定は完全整合のため変更なし |
| v9.2 | 2026-04-27 | 第6・第7バッチ精読（Zou 2024/Zou 2025/Konovalenko 2022/Deitsch 2019）による引用文脈精緻化: (1) §2.1 line 52 の YOLOv8 派生モデル数値範囲「reported mAP@0.5 of 0.82–0.92」を、個別モデル・個別データセット帰属を明示する記述に変更。DCW-YOLO 93.7% は元の範囲「0.82-0.92」を超えており、また DCW-YOLO/AUD-YOLO は同一研究グループ（Dalian Jiaotong Univ.）が同じ Liaoning/Jiangsu 600-image dataset で評価した連続研究であることを明確化。修正後：「YOLO-Wind [12] reported 83.9% mAP@0.5 on the DTU dataset and DMR-YOLO [13] 82.2% on the same dataset, while DCW-YOLO [14] (93.7%) and AUD-YOLO [15] (92%) were evaluated on an independently collected dataset of 600 images from Liaoning/Jiangsu wind farms」。(2) §2.2 line 58「Multi-scale patch augmentation has improved recall in steel surface defect detection [7], photovoltaic cell crack classification [8], and concrete crack detection [9]」を「Patch-based training has been applied to small-defect detection in industrial inspection contexts, including steel surface defect detection [7], photovoltaic cell crack classification [8], and concrete crack detection [9]」に弱化。Konovalenko 2022 は 256×256 単一スケール random crop（multi-scale ではない）で Recall は補助メトリクス（DSC との相関 r=0.11）にとどまる。Deitsch 2019 では multi-scale は feature descriptor (KAZE/SIFT/SURF) の性質で、CNN augmentation は ±2% scale variation のみ。両者とも「Multi-scale patch augmentation has improved recall」の根拠としては薄いため、事実だけ残し「improved recall」の数値主張を削除 |
| v9.3 | 2026-06-12 | Mishnaevsky 2021 / Law & Koutsos 2020 の主張駆動全頁精読（A9 + A11a）に基づく動機・産業意義の補強: (1) §1 Introduction 冒頭に LEE 普遍性と産業意義の段落を追加 — Mishnaevsky 2021 [17] の multiscale multiphysics 性質と Anholt 2016 補修事例、Law 2020 [18] 経由 EDP Renewables 14年データ（87% / 50%）、Mishnaevsky 2021 [17] の欧州オフショア €56-75M/year と Law 2020 [18] の UK £76.5M (2019) / AEP 1.75-4.93% を盛り込み。(2) §5.3 Risk Score Interpretation に「Potential O&M applications」段落の後、経済意義段落を追加（実機データに基づく経済影響の集約による検出駆動 prioritization の意義づけ、ただし validation を要する旨を明示）。(3) 参考文献 [17] Mishnaevsky 2021 と [18] Law & Koutsos 2020 を追加。主張の強度は両論文の数値・記述に限定し、推測や誇張は加えない。引用根拠の詳細は `tools/reference_audit/A9_mishnaevsky_2021_full_reading_2026-06-11.md` と `tools/reference_audit/A11a_law_koutsos_2020_full_reading_2026-06-12.md` |
| v9.4 | 2026-06-12 | Maniaci 2022 IEA Wind Task 46 / Aird 2023 Energies の主張駆動全頁精読（A11c + A11b）に基づく業界文脈・先行研究厚みの補強: (1) §2.1 Related Work に Aird et al. 2023 [20] の Mask R-CNN + PTS 2 モデル比較（140 confidential field images、shallow/deep 分類、両モデル 65% damage area 識別）を追加。評価指標の差異（pixel-level vs bbox-level mAP）を明示。(2) §2.3 Risk Scoring に IEA Wind Task 46（Maniaci et al. 2022 [19]）の 4 軸 × 6 段階業界標準分類への言及を追加。本研究が pre-classification detection stage で動作することを明確化。(3) §5.4 Comparison with Prior Work 末尾に Aird 2023 の pixel-level accuracy（61-66% 総damage、65-73% deep damage）への直接比較不能性を注記。(4) §6 Limitations に項目 9 として「Industry-standard severity alignment」を追加（IEA Wind Task 46 業界標準との未対応を将来研究の課題として明示）。(5) 参考文献 [19] Maniaci 2022 IEA Wind Task 46 と [20] Aird 2023 Energies を追加。主張の強度は両論文の記述・数値に限定し、推測や誇張は加えない。引用根拠の詳細は `tools/reference_audit/A11b_aird_2023_full_reading_2026-06-12.md` と `tools/reference_audit/A11c_maniaci_2022_full_reading_2026-06-12.md` |
| v9.5 | 2026-07-02 | 内部整合性監査（Paper 1-3 全文精査）に基づく機械的修正: (1) §5.4 の「(DMR-YOLO, DCW-YOLO, AUD-YOLO) report 0.82–0.92」を個別数値・データセット帰属明示に変更（DCW-YOLO 93.7% がレンジ外である点は v9.2 で §2.1 のみ修正済みで、§5.4 は未反映だった）。(2) §6 Limitation 7 の「achieving 0.82–0.92 on the same dataset」を「0.82–0.94、YOLO-Wind/DMR-YOLO は DTU・DCW/AUD-YOLO は独立データセット」に修正（「same dataset」は v9.2 の §2.1 修正内容と矛盾していた）。(3) 査読論点表 #4 のレンジ表記を 0.82–0.94 に更新。**非機械的な数値矛盾（559 vs 301 分割、mAP 0.581 vs 0.561、Table 1 P/R と Table 2 集計の不一致、8,055 vs 11,448 分母、Table 3b s=0.575 vs 履歴 s=0.554）は実験ログ照合が必要なため未修正**。詳細は `tools/reference_audit/paper123_consistency_audit_2026-07-02.md` |
| v9.6 | 2026-07-02 | 実験環境の実データ照合による数値矛盾の解決（監査記録 A-1〜A-5 のうち事実確定分を適用）: (1) **画像数 559→301**：yolo_dataset の実ファイル数（train 212 + val 44 + test 45 = 301 元画像、パッチ 11,448/792/810）と Gohar COCO JSON（train1024-s.json 559 **annotations**・3 JSON 合計 301 unique 元画像）を照合。「559」は訓練 bbox アノテーション数の誤転記と確定（559×3 スケール = 1,677 = Table 4 train 合計とも整合）。年別内訳も「2017: 161, 2018: 398」→「2017: 57, 2018: 244」に修正（旧 398 は raw 2018 フォルダ枚数、161 は 559−398 の導出値と推定）。1文主張・Abstract・§3.1 表・§3.2 に適用。§3.2 基本パッチ数 10,062→5,418。(2) **LE;CR 訓練パッチ比率 1.6%→1.2%**：8,055 はラベルファイル総数（空 6,786 含む）であり、全訓練パッチ 11,448 を分母とする 132/11,448 = 1.2% に統一（132 はラベル走査で検証済み、クラス別 bbox 数 588/687/36/171/195 も Table 4 と完全一致）。(3) Table 6 の年別 n_patches（2017: 10 枚・2018: 35 枚）は実データと一致確認・変更なし。**mAP 0.581（val 最良エポック）vs 0.561（test per-class 平均）の提示方法と Table 1 P/R 注記（0.25 閾値記載は要再検討）は himinさん 判断待ちのため未修正**。Table 3b の 0.575 は exp003 results.csv の最良エポック値 0.57539 と一致確認（改訂履歴 v7 の「s: 0.554」が誤記） |
| v9.7 | 2026-07-05 | **mAP 提示方法 案a（test 主指標化）適用 + 修正案① SAHI 案A + B-2 脚注**（himinさん 決定 2026-07-05）: (1) **EXP-001 の test セット評価を新規実行**（`phase1_image_risk_score/src/eval_test_per_class.py`。手順検証として exp002 を同スクリプトで再評価し、公表値と完全一致（mAP@0.5 0.560519・per-class 全5クラス一致）を確認した上で実施）。EXP-001 test: mAP@0.5 0.383 / mAP@0.5:0.95 0.192 / P 0.424 / R 0.285（conf フィルタ 0.25 の model.val、P/R は ultralytics 仕様により F1 最適点の値。`reports/table_class_ap_exp001_baseline_yolov8n.csv`）。(2) **Table 1 を test 基準比較に差し替え**（mAP@0.5 +46%・mAP@0.5:0.95 +59%・P +63%・R +49%）、旧 val 値は Table 1b（best epoch・モデル/エポック選択用）として保持し、§4.1 冒頭に test 主指標の方針文を追加。Abstract・1文主張・貢献・§5.1・§5.4・Conclusion・査読論点表 #4/#11 の「0.58 / +67%」を「test 0.56 / +46%（val 併記）」に統一。(3) **§5.1「Recall 主導」を val 限定の観察に修正**：test では P +63% / R +49% の両改善（FN 73→55・FP 36→22）であり、val（R +73% / P +9%）とパターンが異なることを明示。§5.4 の「Recall of 0.49」も test 0.43 に統一。A-3 で指摘されていた §4.1 の P/R 注記の不正確さ（「Tables 1–2 とも conf 0.25」）も是正し、Metric provenance 注記（Table 1/3 = conf フィルタ 0.25 の model.val で P/R は F1 最適点、Table 2 = 固定閾値 0.25 の生カウント、Table 1b = 学習時 val 指標）に書き換え。(4) **修正案① 案A 適用**：§2.2 の SAHI 記述を SF（訓練時）+ SAHI（推論時）の二段構成として正確化し、pyramid との差別化（離散スケール提示・test-time slicing 不使用）を具体化。(5) **B-2 脚注適用**：§4.4 と Conclusion 3 に「CW 一様スケーリング2件は順位不変が自明、実質は部位重み個別6シナリオ中4で保存」を明記（卒論版 paper1_thesis_ja/en の脚注文面を移植）。(6) v9.6 で見逃された「559」残存2箇所（§5.4 Table 3b 考察・Limitation 5）を 301 に修正。Table 3b ヘッダに validation（best epoch）ラベルを明示 |
| v9.8 | 2026-07-05 | **Codex 独立レビュー（v9.7 適用直後・gpt-5.5・読み取り専用）の指摘反映**。レビュー結果：AP/mAP 転記の CSV 一致・eval スクリプトの条件一致（week1_analysis task2 と同一）・test 主指標化の消し忘れなし・Paper 3 連動 3箇所適用済みは**すべて問題なし**。指摘5件（中2・低3）を全件採用：(1) **中**：Table 1 の P/R が成果物 CSV から独立検証不可 → eval_test_per_class.py に P/R 列（クラス別 = F1最適点、全体 = mp/mr）を追加し両 CSV を再生成（exp001 mP 0.4236/mR 0.2848、exp002 mP 0.6911/mR 0.4247 = Table 1 と一致）。(2) **低**：LE;CR「confirmed ... root cause」が介入実験なしには強い → §5.2 と Conclusion 2 を「most supported explanation（代替仮説は消去済み、介入による確認は future work）」に較正（Proposal Policy 整合）。(3) **低**：Abstract の「6 of 8」に自明性の言及なし → Abstract・1文主張・貢献に「実質は部位重み個別6中4」を併記。残り2件は Paper 2 側（v10.3 参照） |
| v9.9 | 2026-07-05 | **再現パッケージ棚卸し（`tools/reference_audit/repro_package_inventory_2026-07-05.md`）による誤記修正**: (1) §3.3 の「ultralytics==8.3.x」→「**8.4.33**」。根拠 = requirements_phase1.txt の git 履歴（学習3日後の 2026-04-16 フリーズで 8.4.33）＋ 8.4.33 環境での test 再評価が公表値と完全一致。(2) §7 のシード記述を「分割 seed=42（preprocess.py）／学習 seed=0（args.yaml）」に精密化（旧記述は分割シードのみ）。(3) §7 の「training scripts」を実態（ultralytics API/CLI 実行＋args.yaml 保存）に整合。その他の §7 主張項目（データ・前処理/評価/図/リスクスコアのコード・4実験の args.yaml・重み・requirements ピン止め）は実在を確認済み |
