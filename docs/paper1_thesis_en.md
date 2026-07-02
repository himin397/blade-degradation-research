# Automated Detection of Wind Turbine Blade Surface Damage and Span-wise Risk Scoring Using Drone Inspection Images with Pyramid Patch Augmentation

**Document type**: Graduation-thesis-style draft (English version)
**Source document**: `paper1_blade_damage_detection.md` v9.6 (all figures verified against experimental data on 2026-07-02)
**Created**: 2026-07-03
**Note**: All numerical values follow the verified v9.6 source. Detection performance is reported with an explicit distinction between the *validation set* (used during training) and the *held-out test set* (final evaluation). Disclosure of AI assistance follows `ai_assisted_workflow_disclosure.md` (decision pending).

---

## Abstract

As wind power expands worldwide, detecting surface damage on turbine blades early and deciding which repairs to prioritize has become a central task in operation and maintenance (O&M). Drone-based inspection now produces large volumes of high-resolution imagery, yet the step from raw images to repair decisions still relies on manual interpretation and individual experience. This study builds a single, reproducible pipeline that combines (1) deep-learning-based detection of surface damage in publicly available drone inspection images, and (2) a scheme that aggregates the detections into span-wise risk scores for three blade regions (tip, mid-span, and root).

For detection, we use the lightweight object detector YOLOv8n. High-resolution images are sliced into 1,024-pixel patches, and we propose *pyramid patch augmentation*, which presents each training patch at multiple scales. Experiments use the 301 annotated images (13,050 patches) of the public DTU inspection dataset of the Nordtank turbine. With pyramid augmentation, the validation-set mAP@0.5 improved from 0.35 (baseline) to 0.58, a gain of about 67%. On the held-out test set, the final five-class mAP@0.5 was 0.56, with four of the five damage classes reaching AP@0.5 between 0.56 and 0.78. The remaining class, leading-edge cracks (LE;CR), was never detected (AP = 0.00). A systematic differential diagnosis identified severe class imbalance — LE;CR appears in only 1.2% of training patches — as the root cause.

The detections were then converted into region-wise risk scores by weighting each detection with the structural severity of its damage class and the aerodynamic importance of its span position. The resulting ranking (tip > mid > root) is consistent with field experience. A sensitivity analysis perturbing the weights by ±50% preserved this ranking in six of eight scenarios. The main contribution of this work is a reproducible end-to-end pipeline, built entirely from public data, whose performance and limitations — in particular the inability to detect a rare but structurally critical damage class — are quantified and documented.

**Keywords**: wind turbine blade, surface damage detection, deep learning, YOLOv8, class imbalance, risk scoring, drone inspection

---

## Chapter 1 Introduction

### 1.1 Background

Wind power is a major renewable energy source with continuing global deployment. Over an operating life of twenty years or more, turbine blades are exposed to wind, rain, and airborne particles, and various forms of surface damage accumulate. Leading-edge erosion (LEE) — the gradual wearing away of the blade's leading edge by droplet and particle impacts — is nearly universal on aging blades and is increasingly studied as a multiscale, multiphysics process spanning meteorology, aerodynamics, materials science, and computational mechanics [17].

Field data confirm the practical importance of the problem. An inspection of 201 rotor blades after 14 years of operation found visible erosion on 87% (174 blades), with 50% classified as severe [18]. The economic impact is substantial: estimates put the cost to the European offshore wind sector at 56–75 million euros per year [17], and the UK-wide impact in 2019 alone at 76.5 million pounds [18]. Reported annual energy production (AEP) losses range from 1.75% for medium erosion to 4.93% for the worst-affected turbine [18].

Drone-based inspection has largely replaced rope access and ground-based observation. Drones generate large sets of high-resolution images, but converting those images into the practical judgment — *which blade region should be repaired first?* — still depends on manual work by inspectors.

### 1.2 Problem statement

Deep-learning-based damage detection is a promising field with a growing body of results on public datasets [1][2]. Two gaps remain.

First, **limited data and class imbalance**. Public drone inspection datasets are small, and the frequency of damage types is highly skewed. In real operating environments, the most structurally critical damage (such as cracks) is also the rarest, so the imbalance is intrinsic rather than an artifact of data collection. Few studies have quantitatively diagnosed how this imbalance limits detection.

Second, **the gap between detection and maintenance decisions**. Most prior work aims at maximizing detection accuracy (mAP) and does not connect detections to the downstream question of repair prioritization.

### 1.3 Objectives

This study has two objectives:

1. To build a detection pipeline that combines patch slicing with multi-scale training augmentation (pyramid patch augmentation) for public drone inspection images, quantify the performance gain under limited data, and systematically diagnose the cause of any class-level detection failure.
2. To design a scheme that aggregates detections into span-wise (tip/mid/root) risk scores, and to evaluate the robustness of the resulting ranking through sensitivity analysis.

The intended long-term context is a two-stage inspection regime in which 2D image screening selects candidates for detailed 3D assessment. In that context, recall — the ability to avoid missed detections — becomes the metric that governs the reliability of the entire monitoring pipeline.

### 1.4 Thesis outline

Chapter 2 reviews the technical background and related work. Chapter 3 describes the dataset and the proposed methods. Chapter 4 reports the experimental results. Chapter 5 discusses interpretation, comparison with prior work, and limitations. Chapter 6 concludes and outlines future work.

---

## Chapter 2 Background and Related Work

### 2.1 Blade surface damage and inspection

Following the annotation scheme of the dataset [2], this study considers five damage classes:

| Class | Name | Description |
|---|---|---|
| LE;ER | Leading-edge erosion | Surface wear of the leading edge caused by droplet/particle impacts |
| VG;MT | Vortex generator / missing tape | Missing aerodynamic add-ons or repair-tape marks |
| LR;DA | Lightning receptor damage | Damage around lightning receptors |
| LE;CR | Leading-edge crack | Cracks at the leading edge; the most consequential for structural integrity |
| SF;PO | Surface pollution | Oil, dirt, and other contamination |

Among these, LE;CR is the most serious in practice because unrepaired cracks can progress to structural failure — yet it occurs infrequently. This combination of "critical but rare" lies at the heart of the class-imbalance problem examined later.

### 2.2 Deep-learning object detection

Object detection is the task of simultaneously estimating the location (a rectangular *bounding box*) and the class of objects in an image. This study uses the YOLO (You Only Look Once) family of one-stage detectors, which process the whole image in a single forward pass and are therefore fast and widely used in industrial applications. We use YOLOv8n [5], the smallest member of the YOLOv8 family (3.2M parameters), which can be trained and run on modest hardware.

For very high-resolution images, *patch-based detection* — slicing the image into smaller tiles before detection — is standard in industrial inspection, because downscaling a full image would shrink small defects to a few pixels. Patch-based training has been applied to steel surface defects [7], photovoltaic cell cracks [8], and concrete cracks [9]. The SAHI framework [16] offers a general-purpose pipeline of slicing-aided inference with automatic merging of overlapping detections.

### 2.3 Evaluation metrics

We briefly introduce the standard metrics (formulas in plain text):

- **IoU (Intersection over Union)**: overlap between a predicted and a ground-truth box; IoU = (intersection area) / (union area). A detection counts as correct when IoU exceeds a threshold (0.5 in this study).
- **Precision**: P = TP / (TP + FP), the fraction of predictions that are correct.
- **Recall**: R = TP / (TP + FN), the fraction of ground-truth objects that are found; high recall means few missed detections.
- **AP (Average Precision)**: the area under the precision–recall curve for one class, swept over confidence thresholds.
- **mAP (mean Average Precision)**: the mean of AP over all classes. mAP@0.5 uses an IoU threshold of 0.5; mAP@0.5:0.95 averages over IoU thresholds from 0.5 to 0.95 in steps of 0.05.

Here TP, FP, and FN denote true positives (correct detections), false positives (spurious detections), and false negatives (missed objects), respectively.

### 2.4 Related work

**Damage detection.** Shihavuddin et al. [1] released the DTU drone inspection dataset (Nordtank turbine, 701 public images) and applied Faster R-CNN with several backbones; their best reported figure, mAP = 81.1%, was obtained at IoU = 0.3 on the non-public EasyInspect dataset and is not directly comparable to this study. Gohar et al. [2] re-annotated the public DTU dataset for five defect classes and reported mAP@0.5 = 81.3% (YOLOv5) under patch-based inference. More recent architecture-modification studies include YOLO-Wind [12] (83.9% on DTU), DMR-YOLO [13] (82.2% on DTU), and DCW-YOLO [14] (93.7%) / AUD-YOLO [15] (92%) on an independently collected 600-image dataset. These works maximize detection accuracy; the mapping from detections to maintenance-relevant prioritization has received less attention. Beyond box-level detection, Aird et al. [20] compared Mask R-CNN with unsupervised pixel-thresholding methods on 140 confidential field images, identifying about 65% of the total damage area (a pixel-level evaluation not directly comparable to bounding-box mAP).

**Class imbalance.** Known countermeasures in detection include focal loss [4], which down-weights well-classified examples, and oversampling of minority classes.

**Risk scoring and industry standards.** Several studies propose severity classification, but few map detections onto span positions to produce region-wise risk profiles. That aerodynamic loading increases toward the blade tip is established knowledge (Burton et al., *Wind Energy Handbook*), and Malik & Bak [3] showed by aeroelastic simulation that erosion on the outer 15% of the blade causes AEP losses of 0.82% (mild) to 1.46% (severe), and up to 2.14% under high turbulence. As an industry standard, IEA Wind Task 46 [19] defines a four-criterion, six-level severity classification; the risk scoring in this study operates at the pre-classification detection stage relative to that system.

---

## Chapter 3 Dataset and Methods

The pipeline (Figure 1, `reports/fig_pipeline_overview.png`) proceeds from raw images through patch slicing, augmentation, detection, region mapping, and risk scoring.

### 3.1 Dataset

We use the public "DTU Wind Turbine Inspection Images" dataset [6] of the Nordtank NTK 500 turbine in Denmark. The public release contains 701 images (303 from 2017, 398 from 2018) at 5,280 × 2,970 pixels. Annotations follow the five-class re-annotation by Gohar et al. [2], which covers 301 of the original images (57 from 2017 and 244 from 2018); this study uses those 301 annotated images.

The dataset contains 1,914 bounding-box annotations in total (counting the training set after pyramid augmentation). The class distribution is highly skewed: LE;ER accounts for 41.6% and VG;MT for 34.3%, while LR;DA amounts to only 2.3%.

### 3.2 Preprocessing and data split

**Patch slicing.** Each image was sliced into a 3 × 6 grid of 1,024-pixel patches (18 patches per image; 301 × 18 = 5,418 base patches).

**Split.** The split was performed *at the original-image level*, in the order shuffle (random seed 42) → split → slice → augment. The 301 annotated images were randomly partitioned into training (212 images, 70.4%), validation (44 images, 14.6%), and test (45 images, 15.0%). Because every patch derived from an image belongs to the same split as that image, patch-level leakage between splits cannot occur. However, the dataset provides no blade identifiers, so different photographs of the same physical blade may appear in different splits (see Limitation 2, Section 5.5).

**Patch and annotation counts per split:**

| Split | Images | Patches | Ground-truth boxes |
|---|---:|---:|---:|
| Train | 212 | 11,448 (after augmentation) | 1,677 |
| Validation | 44 | 792 | 113 |
| Test | 45 | 810 | 124 |

### 3.3 Pyramid patch augmentation

The central technique of this study, pyramid patch augmentation, presents each training patch not only at its original scale (1.0×) but also rescaled to 0.67× and 0.33×, tripling the training set from 3,816 to 11,448 patches. Since apparent object size strongly affects detector performance, showing each damage instance at several scales is expected to make the model robust to size variation. The network architecture is unchanged, and inference remains standard single-scale — which distinguishes this approach from SAHI's slicing-aided *inference* [16]. Validation and test patches are not augmented.

### 3.4 Training configuration

| Item | Setting |
|---|---|
| Model | YOLOv8n (3.2M parameters) |
| Framework | ultralytics 8.3.x |
| Input size | 640 × 640 pixels |
| Epochs | 30 (no early stopping) |
| Batch size | 8 |
| Optimizer | AdamW (initial LR 0.01, final ≈ 0.0001) |
| Default augmentation | mosaic=1.0, HSV jitter, horizontal flip (mosaic disabled at epoch 20) |
| Hardware | Apple M-series (MPS backend) |

Two experiments were run: **EXP-001 (baseline)** with standard 1,024-pixel patches only, and **EXP-002 (pyramid)** adding the 0.67×/0.33× augmentation. Training curves (Figure 6) confirm that both training loss and validation mAP plateaued within the 30-epoch budget.

Because the MPS backend may order floating-point operations differently from CUDA, exact numerical reproduction on CUDA is not guaranteed; the model-scale comparison (Section 5.4) was run on CUDA T4.

### 3.5 Span-wise risk scoring

Each detection is assigned to a span region by its patch row: row 0 (top of image) = tip, row 1 = mid, row 2 = root. Visual inspection of the originals (sky visible in row 0, ground in row 2) confirmed this mapping. Chord-wise classification (leading vs. trailing edge) was excluded because the blade runs diagonally within patches, making a fixed-coordinate rule unreliable (Limitation 3).

The risk score of detection i is:

```
score_i = confidence_i × area_ratio_i × class_weight_i × region_weight_i
```

where confidence is the detector confidence and area_ratio the box area relative to the patch. The class weights encode structural severity (LE;CR: 3.0, LE;ER: 2.0, VG;MT and LR;DA: 1.5, SF;PO: 1.0) and the region weights encode aerodynamic importance (tip: 3.0, mid: 2.0, root: 1.0). Both weight sets are *practitioner-informed priors* elicited from blade-repair practice; they have not been calibrated against repair-outcome data (Limitation 4). The region score is the sum of all detection scores within that region.

### 3.6 Sensitivity analysis design

To assess how the subjective weights affect the ranking, region weights and class weights were perturbed by ±50%, individually and jointly, giving eight scenarios; we checked whether the baseline ranking (tip > mid > root) survived. Note that the two scenarios scaling *all* class weights jointly multiply every score by a constant and therefore cannot change the ranking by construction; this is made explicit in Section 4.4.

---

## Chapter 4 Results

### 4.1 Detection performance

Performance is reported separately for (a) the **validation set**, used during training and for the baseline comparison, and (b) the held-out **test set**, used for the final evaluation.

**(a) Validation set (Table 1).** Pyramid patch augmentation raised mAP@0.5 from 0.348 to 0.581 (best epoch), a **+67%** gain, and mAP@0.5:0.95 from 0.162 to 0.314 (+95%). Precision rose from 0.753 to 0.823 (+9%) and recall from 0.284 to 0.492 (+73%): the improvement came mainly from fewer missed detections.

**Table 1: Validation-set evaluation (EXP-001 vs. EXP-002)**

| Metric | EXP-001 (baseline) | EXP-002 (pyramid) | Change |
|---|---:|---:|---:|
| mAP@0.5 | 0.348 | **0.581** | +67% |
| mAP@0.5:0.95 | 0.162 | **0.314** | +95% |
| Precision | 0.753 | 0.823 | +9% |
| Recall | 0.284 | 0.492 | +73% |

**(b) Test set (Tables 2 and 3).** On the test set (45 images, 124 ground-truth boxes), the final five-class mAP@0.5 was **0.561**; restricted to the four detectable classes (excluding LE;CR) it was 0.701. Four classes reached AP@0.5 between 0.556 and 0.784, while LE;CR produced no predictions at all (AP = 0.000).

**Table 2: Per-class test-set counts (EXP-002, IoU = 0.5)**

| Class | GT | TP | FP | FN |
|---|---:|---:|---:|---:|
| LE;ER | 58 | 41 | 16 | 17 |
| VG;MT | 39 | 20 | 4 | 19 |
| SF;PO | 10 | 6 | 2 | 4 |
| LR;DA | 6 | 2 | 0 | 4 |
| LE;CR | 11 | 0 | 0 | 11 |
| **Total** | **124** | **69** | **22** | **55** |

The baseline totals were TP 51 / FP 36 / FN 73: pyramid augmentation increased true positives while reducing false positives.

**Table 3: Per-class test-set AP (EXP-002)**

| Class | AP@0.5 | AP@0.5:0.95 |
|---|---:|---:|
| LE;ER | 0.784 | 0.434 |
| VG;MT | 0.756 | 0.410 |
| SF;PO | 0.706 | 0.568 |
| LR;DA | 0.556 | 0.111 |
| LE;CR | 0.000 | 0.000 |
| **5-class mean (primary)** | **0.561** | **0.305** |
| 4-class mean (supplementary) | 0.701 | 0.381 |

The gap of about 0.02 between validation mAP (0.581) and test mAP (0.561) is within the range ordinarily attributable to model selection (choosing the best epoch on the validation set). Hereafter, test-set values are used as the primary performance claims.

### 4.2 Diagnosis of the LE;CR detection failure

LE;CR produced **zero predictions** across all experiments, confidence thresholds, and splits. Table 4 summarizes a systematic differential diagnosis.

**Table 4: Differential diagnosis of LE;CR AP = 0**

| Hypothesis | Evidence | Verdict |
|---|---|---|
| LE;CR absent from the test set | 11 GT instances (8.9% of test boxes) | Rejected |
| IoU threshold too strict | Zero predictions — IoU never enters | Rejected |
| Confidence threshold too high | Zero predictions at every threshold | Rejected |
| Boxes too small to detect | Median area 0.00452 ≈ LE;ER (0.00473) | Rejected |
| **Class imbalance → learning failure** | **LE;CR in only 1.2% of training patches (132 / 11,448)** | **Supported** |

We conclude that the failure stems not from object size or evaluation methodology, but from severe class imbalance in the training data. Focal loss and minority oversampling are known remedies; implementing them was left outside the scope of this study, whose primary aim was the end-to-end pipeline.

### 4.3 Span-wise risk scores

**Table 5: Cumulative risk scores by region (EXP-002, test set)**

| Year | Tip | Mid | Root | Patches |
|---|---:|---:|---:|---:|
| 2017 | 2.023 | 1.247 | 0.000 | 180 |
| 2018 | 0.488 | 0.986 | 0.064 | 630 |
| Combined | 2.512 | 2.232 | 0.064 | 810 |

Year-wise scores are cross-sectional comparisons, not longitudinal tracking of the same damage sites; the two years also differ in patch counts (180 vs. 630) and imaging conditions (Limitation 6). LE;CR contributes nothing to the scores because it is never detected.

### 4.4 Sensitivity analysis

**Table 6: Sensitivity analysis (±50% perturbation, 8 scenarios)**

| Scenario | Tip | Mid | Root | Ranking | Inversion |
|---|---:|---:|---:|---|---|
| Baseline | 2.512 | 2.232 | 0.064 | Tip > Mid > Root | — |
| Region weight, Tip ×1.5 | 3.767 | 2.232 | 0.064 | Tip > Mid > Root | No |
| Region weight, Tip ×0.5 | 1.256 | 2.232 | 0.064 | Mid > Tip > Root | **Yes** |
| Region weight, Mid ×1.5 | 2.512 | 3.349 | 0.064 | Mid > Tip > Root | **Yes** |
| Region weight, Mid ×0.5 | 2.512 | 1.116 | 0.064 | Tip > Mid > Root | No |
| Region weight, Root ×1.5 | 2.512 | 2.232 | 0.096 | Tip > Mid > Root | No |
| Region weight, Root ×0.5 | 2.512 | 2.232 | 0.032 | Tip > Mid > Root | No |
| Class weights, all ×1.5 | 3.767 | 3.349 | 0.096 | Tip > Mid > Root | No* |
| Class weights, all ×0.5 | 1.256 | 1.116 | 0.032 | Tip > Mid > Root | No* |

\* Scaling all class weights jointly multiplies every score by the same constant, so the ranking is preserved trivially. The substantive sensitivity test therefore consists of the six individual region-weight scenarios, of which four preserved the ranking.

Inversions occurred only when the tip weight was halved or the mid weight increased by 50%, reflecting the relatively narrow tip–mid margin (0.280). The root score is an order of magnitude smaller and never left last place.

---

## Chapter 5 Discussion

### 5.1 Effect of pyramid patch augmentation

The +67% validation-mAP gain was driven mainly by recall (+73%) with no loss of precision — the augmentation reduced missed detections without inflating false alarms, a desirable property for a screening application. Per class, TP counts rose and FP counts fell for LE;ER, VG;MT, and LR;DA. LR;DA improved from TP = 0 to TP = 2, though with only six ground-truth instances this comparison carries limited statistical weight.

### 5.2 Implications of class imbalance

The complete failure on LE;CR is the most important negative result of this study. Leading-edge cracks matter most for structural integrity — our own scoring scheme assigns them the highest class weight (3.0) — yet the detector cannot find them, which rules out unmodified practical deployment.

More generally, public drone inspection datasets inherit the field reality that the most critical damage is also the rarest. Without explicit counter-measures (focal loss, oversampling, targeted data collection), detection of safety-relevant rare classes is not guaranteed. This is a caution applicable to detection studies on public data at large.

### 5.3 Interpreting the risk scores

The tip > mid > root ordering agrees with the physical expectation from blade-element momentum theory (higher relative velocity toward the tip), with field experience, and with the outer-span erosion focus of Malik & Bak [3]. The sensitivity analysis bounds the effect of weight subjectivity: the ranking is robust except when the tip weight is halved or the mid weight raised by half.

The scores are designed for *relative* prioritization within a dataset; absolute values depend on image and detection counts and are not comparable across datasets. Whether the scores correspond to actual repair need remains unvalidated — verification against repair records from operating wind farms is the prerequisite for any operational use.

### 5.4 Comparison with prior work

Our test mAP@0.5 of 0.56 is lower than Gohar et al.'s 81.3% on the same dataset [2] and the 0.82–0.94 reported by architecture-modification studies [12]–[15]. The gap reflects a combination of (i) differing evaluation protocols (IoU threshold, dataset version, class taxonomy, public vs. non-public test sets) and (ii) a deliberate design choice: this study uses unmodified YOLOv8 to keep the pipeline simple and reproducible rather than maximizing accuracy through architectural changes.

To check that model capacity is not the bottleneck, YOLOv8s (11.1M parameters) and YOLOv8m (25.9M) were trained on the same pyramid-augmented data (30 epochs, CUDA T4, seed 0). Validation mAP@0.5 was 0.581 (YOLOv8n), 0.575 (YOLOv8s), and 0.425 (YOLOv8m): enlarging the model did not help and eventually hurt, indicating that the bottleneck lies in the data (class imbalance, 301 images, annotation granularity) rather than in capacity. Because the scoring framework is independent of the detection backbone, future adoption of improved detectors would upgrade input quality without any change to the scoring pipeline.

For the screening use case, recall (currently 0.49) is the metric that matters most: roughly half of all damage instances would currently fail to reach a 3D follow-up stage. Improving recall is therefore a precondition for deploying 2D screening in a two-stage inspection regime.

### 5.5 Limitations

1. **LE;CR undetectable**: AP = 0.00 due to severe class imbalance (1.2% of training patches); focal loss and oversampling untested.
2. **Blade-level independence**: no blade identifiers exist, so images of the same physical blade may cross splits, potentially inflating performance.
3. **Chord-wise exclusion**: no leading/trailing-edge distinction.
4. **Weight subjectivity**: class and region weights are practitioner-informed priors, not calibrated against repair outcomes.
5. **Single dataset**: one turbine, 301 images; generalization to other turbine types and imaging conditions untested; annotation quality (inter-annotator agreement) unassessed.
6. **No temporal tracking**: 2017 and 2018 images lack spatial correspondence; year-wise score differences do not indicate damage progression.
7. **Architecture scope**: only unmodified YOLOv8 variants tested; published architectural improvements were not replicated.
8. **Single split seed**: one split (seed 42); with a small test set (45 images, 124 boxes), metric estimates carry sampling variance.
9. **Industry-standard alignment**: the detection classes do not map directly onto the IEA Wind Task 46 severity classification [19]; standard-compliant reporting would require additional severity-thresholding logic.

---

## Chapter 6 Conclusion and Future Work

This study built a reproducible pipeline from public drone inspection images to span-wise blade risk scores and established the following:

1. Pyramid patch augmentation substantially improves detection without any architectural change (validation mAP@0.5 +67%, driven by recall); the final held-out test performance is five-class mAP@0.5 = 0.56.
2. Four of five damage classes reach AP@0.5 of 0.56–0.78, but the structurally most critical class, leading-edge cracks, is entirely undetectable; systematic diagnosis attributes this to class imbalance (1.2% of training patches).
3. Span-wise risk scores reproduce the ranking expected from physics and field experience (tip > mid > root), preserved in four of the six substantive sensitivity scenarios.
4. Scaling up the model does not help, confirming that the bottleneck is the data, not model capacity.

Future work includes: realizing LE;CR detection through class-aware training; validating and calibrating the risk scores against repair records from operating wind farms; improving recall toward practical deployment as the first stage of a 2D-screening → 3D-assessment inspection regime; and testing generalization across turbine types and sites.

---

## Acknowledgments

(To be completed upon submission.)

---

## References

1. Shihavuddin, A.S.M. et al. (2019): "Wind Turbine Surface Damage Detection by Deep Learning Aided Drone Inspection Analysis," Energies, 12(4), 676. DOI: 10.3390/en12040676
2. Gohar, I. et al. (2023): "Slice-Aided Defect Detection in Ultra High-Resolution Wind Turbine Blade Images," Machines, 11(10), 953. DOI: 10.3390/machines11100953
3. Malik, T.H. & Bak, C. (2025): "Challenges in detecting wind turbine power loss: the effects of blade erosion, turbulence, and time averaging," Wind Energy Science, 10, 227–243. DOI: 10.5194/wes-10-227-2025
4. Lin, T.-Y. et al. (2017): "Focal Loss for Dense Object Detection," ICCV 2017. arXiv:1708.02002
5. Ultralytics (2023): "YOLOv8," github.com/ultralytics/ultralytics
6. DTU Wind Turbine Inspection Images: Mendeley Data, DOI: 10.17632/hd96prn3nc.2
7. Konovalenko, I. et al. (2022): "Research of U-Net-Based CNN Architectures for Metal Surface Defect Detection," Machines, 10(5), 327. DOI: 10.3390/machines10050327
8. Deitsch, S. et al. (2019): "Automatic Classification of Defective Photovoltaic Module Cells in Electroluminescence Images," Solar Energy, 185, 455–468. DOI: 10.1016/j.solener.2019.02.067
9. Cha, Y.-J. et al. (2017): "Deep Learning-Based Crack Damage Detection Using Convolutional Neural Networks," Computer-Aided Civil and Infrastructure Engineering, 32(5), 361–378. DOI: 10.1111/mice.12263
10. Memari, M. et al. (2024): "Review on the Advancements in Wind Turbine Blade Inspection: Integrating Drone and Deep Learning Technologies for Enhanced Defect Detection," IEEE Access. DOI: 10.1109/ACCESS.2024.3371493
11. Masita, K. et al. (2025): "Deep Learning in Defect Detection of Wind Turbine Blades: A Review," IEEE Access. DOI: 10.1109/ACCESS.2025.3569799
12. Zhao, Z. & Li, T. (2025): "Enhancing wind turbine blade damage detection with YOLO-Wind," Scientific Reports, 15, 18667. DOI: 10.1038/s41598-025-03639-8
13. Shi, L. et al. (2026): "DMR-YOLO: An Improved Wind Turbine Blade Surface Damage Detection Method Based on YOLOv8," Applied Sciences, 16(3), 1333. DOI: 10.3390/app16031333
14. Zou, L. et al. (2024): "DCW-YOLO: An Improved Method for Surface Damage Detection of Wind Turbine Blades," Applied Sciences, 14(19), 8763. DOI: 10.3390/app14198763
15. Zou, L. et al. (2025): "An improved method of AUD-YOLO for surface damage detection of wind turbine blades," Scientific Reports, 15, 5833. DOI: 10.1038/s41598-025-89864-7
16. Akyon, F.C. et al. (2022): "Slicing Aided Hyper Inference and Fine-Tuning for Small Object Detection," IEEE ICIP, 966–970. DOI: 10.1109/ICIP46576.2022.9897990
17. Mishnaevsky Jr., L. et al. (2021): "Leading edge erosion of wind turbine blades: Understanding, prevention and protection," Renewable Energy, 169, 953–969. DOI: 10.1016/j.renene.2021.01.044
18. Law, H. & Koutsos, V. (2020): "Leading edge erosion of wind turbines: Effect of solid airborne particles and rain on operational wind farms," Wind Energy, 23(10), 1955–1965. DOI: 10.1002/we.2540
19. Maniaci, D. et al. (2022): "Leading Edge Erosion Classification System," IEA Wind Task 46 Technical Report, SAND2023-11986R.
20. Aird, J.A. et al. (2023): "Automated Quantification of Wind Turbine Blade Leading Edge Erosion from Field Images," Energies, 16, 2820. DOI: 10.3390/en16062820

---

## Appendix A Reproducibility

- **Data**: DTU Wind Turbine Inspection Images (Mendeley, DOI: 10.17632/hd96prn3nc.2) with public annotations by Gohar et al. [2]
- **Code**: preprocessing (`slice_images.py`, `pyramid_augment.py`), training/evaluation, risk scoring (`risk_score.py`), and figure-generation scripts
- **Configuration**: random seed (split: 42) and all hyperparameters recorded
- **Hardware**: Apple M-series (MPS); model-scale comparison on CUDA T4
- No proprietary data or commercial software is used anywhere in the pipeline

## Appendix B List of Figures

| No. | Content | File |
|---|---|---|
| Fig. 1 | Pipeline overview | `reports/fig_pipeline_overview.png` |
| Fig. 2 | Detection examples (TP/FP/FN) | `reports/fig_detection_examples_en.png` |
| Fig. 3 | Normalized confusion matrix | `pyramid_yolov8n/confusion_matrix_normalized.png` |
| Fig. 4 | Precision–recall curves | `pyramid_yolov8n/BoxPR_curve.png` |
| Fig. 5 | Sensitivity analysis | `reports/fig_sensitivity_bars_en.png` |
| Fig. 6 | Training curves | `reports/training_curves.png` |
| Fig. 7 | Missed LE;CR examples | `reports/fig_lecr_missed.png` |
| Fig. 8 | Normalized risk scores | `reports/fig_risk_scores_normalized.png` |
| Fig. 9 | Bounding-box area distribution | `reports/fig_bbox_area_distribution.png` |
