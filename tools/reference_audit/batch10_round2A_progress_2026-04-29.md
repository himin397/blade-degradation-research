# 第10バッチ第2ラウンド-A 精読進捗（2026-04-29）

**目的**: 取得済3本（Hu 2025 / Yang 2013 / Gohar 2025）の主張駆動完全精読の進捗管理。コンパクト後の作業再開時の引継ぎ用。

**精読順序**: Hu 2025 → Yang 2013 → Gohar 2025（テーマ近接性順）

---

## 1. Hu 2025（全44頁、完了）✅

**ファイル**: `open_access/Hu_2025_DigitalTwin_BladeDamage_SSRN.pdf`

**書誌**:
- Title: Digital Twin of Wind Turbine Surface Damage Detection Based on Deep Learning-Aided Drone Inspection
- Authors: Weifei Hu, Jianhao Fang, Yaxuan Zhang, Zhenyu Liu, Amrit Shankar Verma, Hongwei Liu, Feiyun Cong, Jianrong Tan
- preprint 提出先: Renewable and Sustainable Energy Reviews（Confidential manuscript）
- 最終掲載: Renewable Energy 241 (2025), 122332（DOI: 10.1016/j.renene.2024.122332）
- 提出先誌が変更された patternなので、Paper 3 [22] の書誌登録（Renewable Energy 241）は正しい

**Paper 3 line 102 主張駆動検証**:

| 主張 | 結果 | 根拠 |
|---|---|---|
| H1: 画像由来の損傷情報を DT に反映するアプローチを示した | ✅ 完全整合 | §2.3 DT framework 5部構成、§3.1 DTU dataset 3 damage classes（VG/VGMT/RUST）、§3.2 実機検証（DJI MATRICE M30, Hubei Province China, 4×2.5MW WTs） |
| H2: SCADAとの統合は対象外 | ✅ 完全整合 | §4 Limitations 2 (p.41): "The proposed DT framework is mainly focused on surface damage on WTs. However...by analyzing SCADA or CMS data. Further research will extend the development of DT for the monitoring and diagnosis of the WT in its whole lifecycle." |

**結論**: Paper 3 line 102 引用は完全整合、**修正不要**。

**重要副次発見**: §4 Limitations 1 (p.41) で著者自身が研究ギャップを明示：
> "RDSS-YOLO can provide the characteristics (e.g., location, shape) of the damage on the WT surface. However, **the trend of these characteristics to failures or fatigue is still unknown** and is a challenging task in real-time WT damage detection. Future research could focus on the **relationship between fatigue or failure and these characteristics**."

→ himinさんの Paper 1（画像損傷検出）+ Paper 2（疲労荷重評価）+ Paper 3（統合パイプライン）が、Hu et al. の Future Work をまさに具現化する位置付け。Paper 3 §1 Introduction 強化に有力な引用素材。

**技術内容（参考）**:
- RDSS-YOLO NN: YOLOv5 + Swin Transformer (C3STR) + Small-scale prediction head + PSPNet semantic segmentation
- mAP 95.7%, precision 93.9%, recall 96.8%, MIoU 81.5%（augmented DTU dataset）

---

## 2. Yang 2013（全12頁、完了）✅

**ファイル**: `open_access/Yang_2013_WT_SCADA_CM.pdf`

**書誌**:
- Title: Wind turbine condition monitoring by the approach of SCADA data analysis
- Authors: Wenxian Yang (NaREC), Richard Court (NaREC), Jiesheng Jiang (Northwestern Polytechnical Univ.)
- Journal: Renewable Energy 53 (2013) 365-376, DOI: 10.1016/j.renene.2012.11.030

**Paper 3 line 100 主張駆動検証**:

| 主張 | 結果 | 根拠 |
|---|---|---|
| Y1: SCADAの複数パラメータ結合による異常検出を実証 | ✅ 完全整合 | §3.2 CM criterion で2変数 {x,y} の相関を polynomial regression（k=4）で modeling、Table 1 で subassembly 別の複数SCADAパラメータ correlation rules、§4 Lab tests（generator winding fault / gearbox tooth fault）、§5 Case studies（blade failure / generator bearing failure） |

**結論**: Paper 3 line 100 引用は完全整合、**修正不要**。

**軽微な精緻化候補（任意・優先度低）**:

実際の §5 Case studies は2例の実機検証：
- §5.1 **Blade failure detection**（two-bladed WT, 4ヶ月 SCADA, c=0→59.9 で月毎に劣化進行）
- §5.2 Generator bearing failure detection（c=0→0.75）

引用精緻化案（Paper 3 §2.2 line 100）：
> 現状: "Yang et al. (2013) [17] はSCADAの複数パラメータ結合による異常検出を実証し"
> 案: "Yang et al. (2013) [17] はSCADAの複数パラメータの相関分析（CM criterion 法）により、ドライブトレイン故障および本研究テーマと直接関連するブレード故障の両方を実機データで検出することを実証し"

ただし現状でも論理整合は保たれているため、必須修正ではない。

**手法的位置付けの明確化**:
- Yang 2013 は **fault detection（故障検出）** = 故障が起きた後にSCADA異常を検出
- himinさんの **degradation prediction（劣化予測）** = 故障前段階の進行追跡
- → Paper 3 §2.2 「ブレード劣化に対する3モダリティ融合は検討していない」主張の妥当性を強化

---

## 3. Gohar 2025（全16頁、完了）✅

**ファイル**: `open_access/Gohar_2025_BladeDefect_Review_EAAI.pdf`（2.4MB, 16頁）

**⚠️ 重要訂正（2026-04-29 コンパクト後）**:
- 当初 open_access に置かれていた `Gohar_2025_BladeDefect_Review_EAAI.pdf`（15MB）は**ファイル名と中身が一致しない誤ファイル**であった
- 中身は実は Guo, Zhao, Yang, Kitipornchai (2025) "Input-optimized physics-informed neural networks for wave propagation problems in laminated structures" (EAAI 141, 109755) という別論文
- コンパクト後の精読再開時にページ16を読み込んだ際に発覚（ヘッダーが "Eng. Appl. Artif. Intell. 141 (2025) 109755" であった）
- 誤ファイルは `supplementary/Guo_2025_PINN_WavePropagation_EAAI_MISFILED.pdf` にリネーム退避
- 正しい Gohar 2025 を Heriot-Watt University Pure リポジトリ（pure.hw.ac.uk）から取得し、open_access に配置

**書誌**:
- Title: Review of state-of-the-art surface defect detection on wind turbine blades through aerial imagery: Challenges and recommendations
- Authors: Imad Gohar, Weng Kean Yew, Abderrahim Halimi, John See
- Affiliation: Heriot-Watt University Malaysia (Putrajaya) + Heriot-Watt University Edinburgh
- Journal: Engineering Applications of Artificial Intelligence 144 (2025) 109970
- DOI: 10.1016/j.engappai.2024.109970
- License: CC-BY 4.0 (open access)
- Funding: HWUM JWS 2021 funding + UK Royal Academy of Engineering Research Fellowship Scheme RF/201718/17128
- 取得先: https://pure.hw.ac.uk/ws/portalfiles/portal/145817807/1-s2.0-S0952197624021298-main.pdf

**論文構成**:
- §1 Introduction（4 RQs 提示）
- §2 Literature and motivation（2.1 既存サーベイ比較, 2.2 WTB 表面欠陥4分類 DEF/N-DEF/SCM/Area, 2.3 Dataset annotation, 2.4 Aerial imagery & drone scenarios）
- §3 Image processing and learning methods（3.1 Statistical, 3.2 Conventional, 3.3 Traditional ML, 3.4 Deep learning, 3.5 Performance evaluation）
- §4 Challenges and limitations（4.1 Data acquisition, 4.2 Data processing, 4.3 Geometrical difficulties）
- §5 Future directions（5.1 Image stitching, 5.2 Rotated BB, 5.3 Federated learning, 5.4 Few-shot learning, 5.5 Multi-labelling）
- §6 Conclusion

**Paper 3 line 94 主張駆動検証**:

| 主張 | 結果 | 根拠 |
|---|---|---|
| G1: ドローン画像×深層学習によるブレード損傷検出のレビュー論文か | ✅ 完全整合 | Title 直接該当, Abstract で aerial imagery × surface defect detection を主題化, §1 Introduction で 4 RQs（object detection pipeline / defect categories / state-of-the-art methodologies / future directions）, §2 Literature review で Pennacchi 2014 / Wang 2022 / Hwang 2021 / Civera & Surace 2022 / Tanrıverdi 2023 / Kong 2023 と差別化を明示 |
| G2: 最新動向を整理しているか | ✅ 完全整合 | §3.4 Deep learning で 2017-2024 の DL 手法を5分類体系化（Two-stage / Single-stage / Attention-based / Lightweight / Data manipulation）、Table 1（17論文の defect class 比較）、Table 2（10論文の方法・dataset・architecture 比較）、Table 3（DTU dataset 利用7論文の mAP 比較）、Fig. 5（image resolution × class数 × mAP 散布図）で体系化、§5 で5つの将来方向（image stitching / rotated BB / federated learning / few-shot / multi-labelling）を提示 |

**結論**: Paper 3 line 94 引用は完全整合、**修正不要**。

**重要副次発見**:

1. **Akyon 2022 SAHI が §3.4 Data Manipulation Strategies で正規にレビューされている**
   > "Akyon et al. (2022) presented Slice-Aided Hyper Inference (SAHI), a method that improves object detection in large, high-resolution images by dividing them into smaller, overlapping slices for localised processing. This approach is particularly effective for detecting small or distant objects and alleviates memory constraints during inference, making it invaluable for tasks such as aerial imagery and defect detection where fine details are critical. Similarly, Gohar et al. (2023a) utilised the SAHI approach to efficiently process high-resolution images in the inference phase. Their method, assessed on the DTU dataset, demonstrated enhanced accuracy in identifying small-scale defects using models like Faster R-CNN, YOLOv5, and RetinaNet."
   → Paper 1 §2.2 line 58 の Akyon 2022 SAHI 引用と直接呼応。Gohar 2025 は SAHI を「small object detection への有効手法」として同定しており、Paper 1 修正案①（SAHI vs MM82 single-class trade-off の対比論述）の根拠強化材料となる

2. **著者連続体の確認**: Shihavuddin 2019 → Gohar 2023a/b → Gohar 2025
   - Gohar 2023a (Machines 11(10), 953, "Slice-aided defect detection"): DTU dataset に SAHI 適用、Faster R-CNN/YOLOv5/RetinaNet で評価、mAP 85.1%
   - Gohar 2023b (ICMEW IEEE): YOLOv5s/m の DTU bounding box aspect ratio 検討、mAP 75.2%
   - Gohar 2024 (EUSIPCO IEEE): Rotated bounding box approach
   - Gohar 2025 (EAAI 144, 109970, 本論文): 上記研究の延長としての包括的レビュー
   - Paper 1 の引用構造（[2] Shihavuddin 2019 + [3] Gohar 2023 + [15] Gohar 2025）はこの著者連続体を正しく捉えており、論理的整合性が高い

3. **Future Direction §5.4 Few-shot learning が himinさん研究と直結**
   > "WTB surface defect detection often faces challenges due to limited data availability and the need for models to quickly adapt to new defect classes. Few-shot object detection (FSOD) is a few-shot learning method that allows models to learn from a limited number of examples..."
   → エロージョン進行段階のデータ希少性（Paper 1/2 で論じる課題）に対応する技術として、将来 Paper 3 拡張時の引用候補

4. **§5.5 Multi-labelling の component-based labelling 提案**
   > "one label reads 'leading edge; erosion; continuous or deep', which is comprised of three parts: the first part specifies the location of the defects, the second part describes the type of defects, and the third part indicates the severity of the defects."
   → Paper 1 のクラス設計（VG/VGMT/RUST など）と、Paper 2/3 の劣化 severity 推定との接続点として、将来研究の方向性提示

---

## 4. 第2ラウンド-A 総括（3本完了 ✅）

| # | 論文 | 該当 Paper | 結果 |
|---|---|---|---|
| 1 | Hu 2025 (Renewable Energy 241, 122332) | Paper 3 line 102 | ✅ 完全整合（修正不要） |
| 2 | Yang 2013 (Renewable Energy 53, 365-376) | Paper 3 line 100 | ✅ 完全整合（修正不要） |
| 3 | Gohar 2025 (EAAI 144, 109970) | Paper 3 line 94 | ✅ 完全整合（修正不要） |

**Paper 3 §2 Related Work セクション全体の引用整合性が確認された**ことになる。

## 5. 残作業

### 第2ラウンド-A の事後処理
1. ✅ Gohar 2025 全頁精読完了（本マークダウン § 3 で記録）
2. memory `project_blade_paper_audit_progress.md` の Gohar 2025 行を「✅完了」に訂正
3. URL_INDEX.md の Gohar 2025 ステータスを「OA取得済（Heriot-Watt Pure）」に更新
4. supplementary/README.md に Guo 2025 misfile の経緯を追記

### 第2ラウンド-B（取得待ち2本）
4. WAKABA 取得待ち：Vera-Tudela 2017 / Dimitrov 2015 / Cha 2017 / Dao 2018 / Liu 2024 / Nielsen 2011 / Yeter 2020（合計7本、`acquisition_status_2026-04-29.md` 参照）
5. 取得後、主張駆動完全精読

### 第10バッチ完了後
6. Paper 2 v9.6 統合修正案策定（修正案①②③＋Vera-Tudela/Dimitrov 結果統合）
7. Paper 2 line 99 引用先確定（bin-averaged vs 直接計測 TI）
8. Tautz-Weinert 候補1 最終再評価

---

## 5. 既適用の修正

- **Paper 2 v9.5** (2026-04-27): §2.3 line 126 修正案③-案B 適用済（IEA Wind Task 42 → EUDP LifeWind project）
- それ以外の修正案①②（Akyon SAHI / Downing & Socie 体系化表現）は himin判断待ち

---

## 6. 関連ファイル

- `acquisition_status_2026-04-29.md` — 参考文献取得状況サマリ
- `batch10_round1_revision_proposals.md` — 第1ラウンド3本（Akyon/D&S/Natarajan）の修正案
- `batch10_reading_checklist.md` — 第10バッチ全体チェックリスト
- `memory/project_blade_paper_audit_progress.md` — 精読進捗メモリ
- `memory/feedback_reference_verification.md` — 参考文献検証ルール
- `memory/reference_iec61400_28_blade_erosion.md` — Natarajan 2020 §8 IEC 61400-28 推奨記録
