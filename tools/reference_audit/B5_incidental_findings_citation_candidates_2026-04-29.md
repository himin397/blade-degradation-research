# B5: 副次発見からの引用候補集

**実施日**: 2026-04-29
**対象**: 第10バッチ第1ラウンド・第2ラウンド-A の精読で発見された、Paper 1/2/3 への追加引用候補
**目的**: A3/A4 の判断材料として、副次発見を Paper 別に整理

---

## 概要

第10バッチで全頁主張駆動精読を行った6本（Akyon 2022 / Downing & Socie 1982 / Natarajan 2020 / Hu 2025 / Yang 2013 / Gohar 2025）から、Paper 1/2/3 への引用候補となる副次発見を抽出しました。

| 発見元 | Paper 1 への候補 | Paper 2 への候補 | Paper 3 への候補 |
|---|---|---|---|
| Hu 2025 | - | - | ✅ §1 / §6 強化 |
| Yang 2013 | - | - | ✅ §2.2 強化 |
| Gohar 2025 | ✅ §2.2 / §6 強化 | - | ✅ §6 強化 |
| Natarajan 2020 (LifeWind) | ✅ §1 強化 | - | ✅ §1 強化 |

---

## 1. Hu 2025 §4 Limitations 1（Paper 3 強化候補）

### 原文
> "RDSS-YOLO can provide the characteristics (e.g., location, shape) of the damage on the WT surface. However, **the trend of these characteristics to failures or fatigue is still unknown** and is a challenging task in real-time WT damage detection. Future research could focus on the **relationship between fatigue or failure and these characteristics**."

### Paper 3 への引用候補位置

**§1 Introduction または §6 Conclusion の研究意義論述**

### 引用案
> "Hu et al. (2025) [22] explicitly identify the relationship between visually detectable damage characteristics and fatigue progression as a key open question for future research, stating that 'the trend of these characteristics to failures or fatigue is still unknown.' The integrated framework proposed in this paper—combining image-derived damage scores (Paper 1), aeroelastic fatigue load estimation (Paper 2), and SCADA-based operational indicators—directly addresses this gap by providing a quantitative bridge between surface damage state and load history."

### 効果
- Paper 1+2+3 統合の研究意義を **第三者（Hu et al.）の Future Work** で裏付けられる
- 自己評価でなく外部視点からの研究意義主張になり、説得力が増す

---

## 2. Yang 2013 fault detection vs degradation prediction の対比（Paper 3 強化候補）

### 発見内容
Yang 2013 の手法は **fault detection（故障検出）**：故障が起きた後に SCADA 異常を検出する
- §5.1 Blade failure detection: c値が4ヶ月で 0→59.9 と上昇（既に故障進行中の検出）
- §5.2 Generator bearing failure detection: c=0→0.75

himinさんの研究は **degradation prediction（劣化予測）**：故障前段階の進行追跡を志向

### Paper 3 への引用候補位置

**§2.2 Related Work（SCADA-based methods）の Yang 2013 引用周辺**

### 引用案
> "Yang et al. (2013) [17] established a foundational SCADA-based condition monitoring framework using polynomial regression of paired SCADA parameters, demonstrating fault detection capability for both drivetrain failures and—directly relevant to this study—blade failures (§5.1 of Yang 2013). However, their method targets *post-onset fault detection* (e.g., the criterion value evolved from 0 to 59.9 over four months as the fault progressed), whereas our framework targets *pre-onset degradation prediction* by integrating image-derived damage scores. This distinction motivates the three-modality fusion proposed here, which is not addressed in existing SCADA-only frameworks."

### 効果
- Paper 3 §2.2 の「3モダリティ融合は未検討」主張の妥当性を、**先行研究の手法的位置付けの差異**として明確化
- 引用先の論文の良い点（実機検証あり）を認めた上で、自研究の差別化を論理的に示せる

---

## 3. Gohar 2025 §3.4 Akyon 2022 SAHI レビュー（Paper 1 強化候補）

### 原文
> "Akyon et al. (2022) presented Slice-Aided Hyper Inference (SAHI), a method that improves object detection in large, high-resolution images by dividing them into smaller, overlapping slices for localised processing. This approach is particularly effective for detecting small or distant objects and alleviates memory constraints during inference, making it invaluable for tasks such as aerial imagery and defect detection where fine details are critical. Similarly, Gohar et al. (2023a) utilised the SAHI approach to efficiently process high-resolution images in the inference phase. Their method, assessed on the DTU dataset, demonstrated enhanced accuracy in identifying small-scale defects using models like Faster R-CNN, YOLOv5, and RetinaNet."

### Paper 1 への引用候補位置

**§2.2 Related Work（SAHI 言及部分、line 58 周辺の修正案①と組み合わせ）**

### 引用案（修正案①と統合した形）
> "Slice-Aided Hyper Inference (SAHI) [16] addresses memory and small-object constraints by dividing high-resolution images into overlapping slices for inference, and has been characterized as 'particularly effective for detecting small or distant objects' in the WTB defect detection literature [15]. Gohar et al. (2023) [2] applied SAHI to the DTU dataset, demonstrating its effectiveness for small-scale defect detection. The pyramid patch augmentation proposed here differs from SAHI in that it operates at *training time* by exposing the model to multi-scale views, while SAHI operates at *inference time*; the two approaches address complementary aspects of the small-object detection problem and could in principle be combined."

### 効果
- Paper 1 §2.2 line 58 修正案①の根拠を、**第三者によるレビュー論文での位置づけ** で強化
- SAHI vs Pyramid augmentation の対比を「training-time vs inference-time」の論理的差異として整理

### Paper 3 への引用候補位置

**§6 Future Work セクション（拡張方向の論述）**

### 引用案
> "Gohar et al. (2025) [15] identify five future directions for WTB defect detection: image stitching, rotated bounding boxes, federated learning, few-shot learning, and component-based multi-labelling. Among these, **few-shot learning** (§5.4 of Gohar 2025) is particularly aligned with the data scarcity challenge in degradation progression studies—where labelled examples of intermediate erosion stages are inherently limited—and represents a natural extension of the current framework. **Component-based multi-labelling** (e.g., 'leading edge; erosion; continuous or deep' as proposed in §5.5 of Gohar 2025) also aligns with the location-aware risk scoring approach developed in Paper 1."

### 効果
- Paper 3 §6 の「今後の発展」を、**最新レビュー論文の方向性提言と接続**できる
- 自研究が field の前進と整合していることを示せる

---

## 4. Natarajan 2020 LifeWind §8 IEC 61400-28 推奨（Paper 1 / Paper 3 強化候補）

### 原文（既に memory `reference_iec61400_28_blade_erosion.md` で記録済）

#### §8 Summary Recommendation to IEC Standards (p.106)
> "Based on the multiple project results and findings, a recommended text for the IEC 61400-28 standards is formulated to be concise as follows:
> - A plan for inspections should be made for the period of lifetime extension... **Special focus should be made to:**
>   – **Leading edge erosion of blades.**
>   – Sufficient tension of bolts at major component interfaces in the primary load path."

#### §3.1.1 Wind turbine rotor inspections (p.13)
> "Blades. Inspections show that **erosion on leading edge needs further focus**. The bigger wind turbines/blades the bigger problem... **Almost all blades show erosion**. Therefore, these blade repairs need to be performed in a higher quality and method."

### Paper 1 への引用候補位置

**§1 Introduction（研究意義の冒頭）または §2.3 Risk Scoring**

### 引用案（Paper 1 §1 Introduction 末尾）
> "The industry's prioritization of leading-edge erosion is reinforced by the EUDP LifeWind project's recommendations to the upcoming IEC 61400-28 lifetime extension standard [REF: Natarajan et al. 2020], which explicitly identifies leading-edge erosion of blades as a special-focus inspection item alongside primary-load-path bolt tension. This industry positioning underpins the present study's emphasis on detection-driven prioritization of blade erosion damage."

### 効果
- 研究の **industry relevance** を、最新の標準策定動向で裏付けられる
- 「Almost all blades show erosion」「needs further focus」という表現は問題の普遍性を示す強力な引用素材

### Paper 3 への引用候補位置

**§1 Introduction（パイプラインの実用意義）**

### 引用案
> "EUDP LifeWind project (Natarajan et al. 2020) [REF] における IEC 61400-28（策定中の寿命延長標準）への推奨事項では、ブレード前縁エロージョンを重点点検項目として明示的に挙げている。本研究が提案する SCADA × 画像 × 気象データ統合パイプラインは、この産業要請に対する技術的応答として位置づけられる。"

### 引用追加に伴う書誌追加の必要性

| Paper | 現状 | 必要な変更 |
|---|---|---|
| Paper 1 | Natarajan 2020 引用なし | 参考文献リストに追加（[17] 等）、§1 に挿入 |
| Paper 2 | [19] として既に引用済 | 追加引用挿入のみ（書誌追加不要） |
| Paper 3 | Natarajan 2020 引用なし | 参考文献リストに追加（[26] 等）、§1 に挿入 |

---

## 5. Gohar 2025 著者連続体の確認（Paper 1 整合性裏付け）

### 発見内容
Shihavuddin 2019 → Gohar 2023a (Machines) → Gohar 2023b (ICMEW) → Gohar 2024 (EUSIPCO) → **Gohar 2025 (EAAI)** が同じ研究グループ（John See / Heriot-Watt Univ. Malaysia）の連続研究

### Paper 1 への影響
- 既存の引用構造 [1] Shihavuddin 2019 + [2] Gohar 2023 + [16] Akyon 2022 + Paper 3 [15] Gohar 2025 は**著者連続体を正しく捉えている**
- これは **修正不要、整合性裏付け** の知見

### Paper 3 への影響
- §1 Introduction で「Shihavuddin 2019 以降の最新動向」を Gohar 2025 で代表させる現在の引用構造は、author lineage の観点からも論理整合的
- **修正不要**

---

## 6. 引用候補のまとめと判断軸

### Paper 1 への候補（3件）

| # | 候補 | 該当箇所 | 工数 | 優先度（Claude Code 推定） |
|---|---|---|---|---|
| P1-A | Gohar 2025 §3.4 SAHI 位置づけ引用 | §2.2 line 58（修正案①と統合） | 小 | 中（SAHI 論述強化） |
| P1-B | Natarajan 2020 IEC 61400-28 推奨 | §1 Introduction 末尾 | 中（書誌追加要） | **高**（industry relevance） |
| P1-C | Gohar 2025 §5.4 few-shot learning | §6 Future Work（オプション） | 小 | 低 |

### Paper 2 への候補（0件）

第10バッチ第1〜2A の精読では、Paper 2 への新規引用候補は発見されませんでした。
（修正案③ Natarajan 2020 関連は v9.5 で適用済）

### Paper 3 への候補（4件）

| # | 候補 | 該当箇所 | 工数 | 優先度（Claude Code 推定） |
|---|---|---|---|---|
| P3-A | Hu 2025 §4 Limitations 1（fatigue gap） | §1 Intro / §6 Conclusion | 小 | **高**（研究意義裏付け） |
| P3-B | Yang 2013 fault detection vs degradation prediction 対比 | §2.2 Related Work | 小 | 中（差別化強化） |
| P3-C | Gohar 2025 §5 Future Directions（few-shot, multi-labelling） | §6 Future Work | 小 | 中（field との整合） |
| P3-D | Natarajan 2020 IEC 61400-28 推奨 | §1 Introduction | 中（書誌追加要） | **高**（industry relevance） |

---

## 7. 判断のポイント（himinさんが A4 判断時に参照）

### 「優先度高」と Claude Code が推定する根拠

1. **P1-B / P3-D（Natarajan 2020 IEC 61400-28）**
   - 産業との接続を国際標準への入力という形で示せる
   - 「Almost all blades show erosion」という記述は、研究問題の普遍性を強力に支持
   - 書誌追加が必要だが、研究意義の説得力が大きく上がる

2. **P3-A（Hu 2025 fatigue gap）**
   - **Hu et al. 自身が Future Work として明示している研究ギャップ**を、本研究が埋めるという論理が成立
   - 自己評価でなく第三者視点からの研究意義主張は、査読対策として有効

### 「優先度中」と Claude Code が推定する根拠

3. **P1-A（Gohar 2025 SAHI 位置づけ）**
   - 修正案①と組み合わせることで、SAHI vs Pyramid augmentation の対比論述を**第三者レビューでの位置づけ**で強化できる
   - 修正案① の判断と一緒に検討するのが自然

4. **P3-B（Yang 2013 対比）**
   - fault detection vs degradation prediction の用語的差異を明確化できる
   - 既存引用は完全整合のため、加筆は補強的

5. **P3-C（Gohar 2025 few-shot, multi-labelling）**
   - 将来研究の方向性を field の最新動向と接続
   - 必須ではないが、研究の継続性をアピールできる

### 「優先度低」

6. **P1-C（Gohar 2025 few-shot）**
   - Paper 1 では本筋から離れる
   - Paper 3 §6 Future Work で扱えば十分

---

## 8. 関連メモ

- `memory/reference_iec61400_28_blade_erosion.md` — Natarajan 2020 LifeWind §8 詳細記録
- `tools/reference_audit/batch10_round1_revision_proposals.md` — 修正案①②③の詳細
- `tools/reference_audit/batch10_round2A_progress_2026-04-29.md` — Hu/Yang/Gohar 2025 精読記録
- `memory/project_blade_paper_audit_progress.md` — 監査全体の進捗
