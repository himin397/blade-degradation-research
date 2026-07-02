# A11c: Maniaci et al. (2022) IEA Wind Task 46 全頁主張駆動精読結果

**実施日**: 2026-06-12
**目的**: A11c 候補論文 Maniaci 2022 IEA Wind Task 46 の精読・Paper 1 への引用候補確定
**取得経路**: IEA Wind 公式 PDF（iea-wind.org/wp-content/uploads/2023/02/IEA-Wind-Task-46-Erosion-Classification-System-report.pdf）

---

## 1. 書誌情報

| 項目 | 内容 |
|---|---|
| Title | Leading Edge Erosion Classification System |
| Authors | David Maniaci (Sandia), Hamish MacDonald (ORE Catapult UK), Joshua Paquette (Sandia), Ryan Clarke (Sandia) |
| Document | Technical report, IEA Wind TCP Task 46 |
| Report ID | SAND2023-11986R |
| Date | December 2022 |
| Prepared for | International Energy Agency Wind Technology Collaboration Programme |
| DOI | 10.2172/2432094 (OSTI) |
| Pages | 52 頁 |
| ファイル配置 | `open_access/Maniaci_2022_LEE_Classification_System_IEA_Wind_Task46.pdf`（3.86 MB） |
| 助成 | Sandia (U.S. DOE NNSA contract DE-NA0003525) + IEA Wind TCP Task 46 |
| IEA Task 46 参加国（2021-2025） | Belgium, Canada, Denmark, Finland, Germany, Ireland, Netherlands, Norway, Spain, UK, US |
| 主要参加組織 | DTU (co-OA), Hempel, Ørsted A/S, VTT, Fraunhofer IWES, Covestro, TU Delft, Equinor, Siemens Gamesa, Nordex Energy, ORE Catapult, U Bristol, Cornell, Sandia, 3M |

→ **風力産業の主要研究機関・OEM・運用事業者の合意による業界標準フレームワーク**

---

## 2. 論文構成

| 章 | 内容 |
|---|---|
| Executive Summary | 4 軸 (Visual / Mass Loss / Aero / Structural) の severity 分類提案 |
| §1 Introduction (WP3 Activity 3.2) | IEA Wind Task 46 の 5 つの研究活動（WP3.1-3.5） |
| §2 Erosion Damage Categorization | §2.1 Motivations、§2.2 Examples（Testing/Standards, Research, Operational） |
| §3 Methodology | Figure 3-1 の 8 つの categorization considerations |
| §4 Erosion Classification System（核心） | §4.1 Criteria、§4.2 Guidelines、§4.3 Severity Levels (4 軸 × 6 段階)、Table 4-1 |
| §5 Future Considerations | 検査技術 / Recommended actions / Modelling / Blade Technology |
| §6 Key Conclusions/Recommendations | Scope, Remedial actions, Visual imagery, Data provision, System adaptability |
| Appendix A | Example Assessments from WP3 Activity |
| Appendix B | Example Erosion/LEP Damage Images |

---

## 3. 核心フレームワーク：Erosion Classification System

### 3.1 4 つの Evaluation Criteria（§4.1）

| 軸 | 焦点 | 主な評価対象 |
|---|---|---|
| **Visual Condition** (LEP) | LEP の劣化状態 | LEP の整合性、adhesion failure |
| **Visual Condition** (No LEP) | 裸 blade の劣化状態 | Pinholes, pitting, gouges |
| **Mass Loss** | 材料喪失 | Coating mass loss %, Laminate mass loss % |
| **Aerodynamic Performance** | 空力性能低下 | Region 2 power loss % |
| **Blade Integrity** | 構造的整合性 | 層構造透過（LEP → Topcoat → Filler → Biaxial → UD） |

### 3.2 Table 4-1: 6 段階 (0-5) Severity Levels（核心テーブル）

| Severity Level | Visual (LEP) | Visual (No LEP) | Mass-loss | Aero | Blade Integrity |
|---|---|---|---|---|---|
| **0** | Initial factory condition | - | - | - | - |
| **1** | Lightly worn LEP / reduced adhesion (≥1 cm², ≤10 cm²) | Erosion barely visible (≤1 cm²) | Coating <10%, Laminate 0% | Region 2 0-1% | Initial erosion of topcoat |
| **2** | Notable areas of localized LEP damage (≥10 cm², ≤1 m²) | Localized pitting (≥1 cm²) | Coating 10-50%, Laminate 0% | Region 2 1-2% | Erosion through topcoat |
| **3** | LEP compromised over large area (≥1 m²) | Widespread pits, some gouges (≤10 cm²) | Coating 50-100%, Laminate <10% | Region 2 2-3% | Initial exposure of laminate |
| **4** | Delamination of topcoat with layer underneath visible | Erosion of topcoat (≥10 cm², laminate ≤1 cm²) | Coating 100%, Laminate 10-100% | Region 2 3-4% | Erosion through immediate laminate |
| **5** | Notable damage to substrate | Erosion of laminate (≥1 cm²) | Coating 100%, Laminate 100% | Region 2 >4% | Exposure of structural layers |

### 3.3 重要な評価ルール

- **5% blade span rule**: "When 5% of blade span is in a given class, the blade is considered that severity rating"
- LEE は典型的に **outer one-third of LE**（最高 relative velocity）で発生（Letson 2020）

### 3.4 Table 4-2: AEP Loss 推定（Maniaci 2020 由来）

| Erosion Category | 4 m/s | 6 m/s | 7.5 m/s | 8.5 m/s | 10 m/s |
|---|---|---|---|---|---|
| 0 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 2 | -1.0% | -0.9% | -0.7% | -0.6% | -0.4% |
| 3 | -1.9% | -1.6% | -1.3% | -1.1% | -0.8% |
| 4 | -3.0% | -2.6% | -2.2% | -1.9% | -1.6% |

→ **Mishnaevsky 2021 / Law 2020 の AEP 損失数値と並列で参照可能**

---

## 4. Paper 1/3 への引用候補

### 4.1 Paper 1 への引用候補（3 件）

#### P1-M2-A: §2.3 Risk Scoring（業界標準との対比）

**引用箇所**: Paper 1 §2.3 Risk Scoring の冒頭または末尾

**引用案**:
> "Industry-standard severity classification frameworks have been developed by IEA Wind Task 46 (Maniaci et al. 2022 [19]), which defines a four-criterion system—Visual Condition (with/without LEP), Mass Loss, Aerodynamic Performance, and Blade Integrity—across six severity levels (0-5), assigned via the rule 'when 5% of blade span is in a given class the blade is considered that severity rating.' The risk scoring framework in this study operates at the pre-classification detection stage: it detects and prioritizes damage features for repair planning, rather than assigning standardized severity ratings to the blade as a whole."

**根拠**: §4.1, §4.2 5%-rule, §4.3 Severity Levels

**効果**: 本研究の研究範囲を業界標準の枠組みで位置づけ、混同を避ける（推定優先度: 🟡 中-高）

#### P1-M2-B: §6 Limitations（業界標準との未対応を明示）

**引用箇所**: Paper 1 §6 Limitations

**引用案**:
> "**Industry-standard severity alignment**: The detection classes used here (e.g., LE;ER, VG;MT) derive from the DTU dataset annotations and do not directly correspond to the four-criterion, six-level severity classification system proposed by IEA Wind Task 46 (Maniaci et al. 2022 [19]). Mapping detection outputs to these standardized categories—e.g., assigning Visual Condition severity based on detected damage area, or estimating Aerodynamic Performance category from cumulative damage scores—represents a path toward operational integration but requires severity-thresholding logic that is outside the scope of this study."

**根拠**: §4.1-4.3

**効果**: 査読対策として研究限界を業界文脈で明示（推定優先度: 🟡 中-高）

#### P1-M2-C: §5.3 Risk Score Interpretation（AEP loss と並列）

**引用箇所**: Paper 1 §5.3（既存の Mishnaevsky / Law 経済影響パラグラフ周辺）

**引用案**:
> "Industry-standard quantification efforts such as IEA Wind Task 46 (Maniaci et al. 2022 [19]) map severity categories to AEP loss: approximately 0.4-0.8% at Category 2 and 0.8-1.6% at Category 3 (for mean wind speeds of 6-10 m/s, Table 4-2 of Maniaci et al. 2022). These thresholds provide quantitative anchors that future O&M-validated extensions of the present risk scoring framework could align with."

**根拠**: Table 4-2

**効果**: AEP 損失数値を業界標準で補強（推定優先度: 🟢 中-低、Mishnaevsky / Law と一部重複）

### 4.2 Paper 3 への引用候補

Maniaci 2022 は **画像由来の severity 評価**フレームワークであり、Paper 3 の SCADA × 画像 × 気象データ統合とは異なる軸。Paper 3 への直接引用は **不要**。

ただし Paper 3 §6 Future Work で「画像由来の damage score を industry-standard severity に変換するレイヤを追加する」という方向性を示すなら、補助的に引用可能。優先度: 🟢 低。

---

## 5. Maniaci 2022 の Paper 1 への引用推奨度

| 引用箇所 | 推定優先度 | 理由 |
|---|---|---|
| **P1-M2-A**（§2.3 業界標準の対比）| 🟡 中-高 | 本研究のスコープを明確化、混同回避 |
| **P1-M2-B**（§6 Limitations）| 🟡 中-高 | 査読対策として有効、研究限界の明示 |
| **P1-M2-C**（§5.3 AEP threshold）| 🟢 中-低 | Mishnaevsky / Law と一部重複 |

### 推奨される最低限の適用

**最も価値の高い 2 件**:
1. **P1-M2-A**（§2.3 業界標準の対比）→ 研究範囲の明確化
2. **P1-M2-B**（§6 Limitations）→ 業界標準との未対応を限界として明示

これらにより Paper 1 が「**業界標準を意識した研究**」として位置づけられ、査読時の「業界標準との関係はどうか」という問いに事前回答できる。

---

## 6. 副次発見

### 6.1 Maniaci 2022 経由で発見された関連研究

| Ref | 論文 | 用途 |
|---|---|---|
| Bak 2020 | "The influence of LE roughness, rotor control and wind climate on energy production loss" J. Phys. Conf. Ser. 1618 | Paper 1/2 の AEP 影響補強 |
| Cortés 2017 | "Material Characterisation of WT Blade Coatings" Materials 28(10), 1146 | LEP material 研究 |
| DNV 2018 (DNV-RP-0171) | Testing of rotor blade erosion protection systems | テスト規格 |
| DNV 2020 (DNV-RP-0573) | Evaluation of erosion and delamination for LEP systems | テスト規格 |
| Eisenberg 2018 | "WT blade coating LE rain erosion model" Wind Energy 21(10), 942-951 | erosion modelling |
| Gaudern 2014 | "A practical study of the aerodynamic impact of WT blade LE erosion" J. Phys. Conf. Ser. 524(1) | aero impact |
| Maniaci 2020 | "Uncertainty Quantification of LEE Impacts on WT Performance" J. Phys. Conf. Ser. 1618 | AEP uncertainty |
| Verma 2021 | "A probabilistic long-term framework for site-specific erosion analysis: 31 Dutch sites" Wind Energy 24(11) | 確率的 erosion analysis |

これらは将来検討候補。

### 6.2 LEE の物理機序（§2.1）の確認

"LEE is caused by multiple, high-velocity impacts from hydrometeors impacting the area (±5-10%) around the blade leading-edge and focused on the outer one-third of the leading edge which experiences the highest relative velocities" (Letson 2020 引用)

→ **Paper 1 §2.3 Malik & Bak 2025 outer 15% の主張と整合**

---

## 7. 関連メモ

- `tools/reference_audit/A9_mishnaevsky_2021_full_reading_2026-06-11.md` — Mishnaevsky 2021 精読
- `tools/reference_audit/A11a_law_koutsos_2020_full_reading_2026-06-12.md` — Law 2020 精読
- `tools/reference_audit/A11b_aird_2023_full_reading_2026-06-12.md` — Aird 2023 精読
- `memory/project_blade_paper_audit_progress.md` — 監査全体の進捗

---

## 8. 次のステップ

1. ✅ Maniaci 2022 全頁精読 + ドキュメント化（本ファイル）
2. ⏸ Paper 1 への引用適用（P1-M2-A + P1-M2-B）
3. ⏸ Aird 2023 を Paper 1 §2.1 + §5.4 に引用適用
4. ⏸ Paper 1 改訂履歴 v9.4 として統合記録
5. ⏸ memory 更新と Pryor 2022 取得困難の報告
