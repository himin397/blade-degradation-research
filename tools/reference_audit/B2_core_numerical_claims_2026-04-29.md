# B2: 既精読論文の核心数値・引用箇所対応リスト

**実施日**: 2026-04-29
**目的**: Paper 1/2/3 で外部論文から引用している数値・図表を整理し、将来の細部精読フェーズで「引用箇所 vs 引用元頁」の照合が即実施できる状態を準備する

---

## 概要

Paper 1/2/3 の本文から、外部論文の **特定の数値・式・パラメータ** を引用している箇所を網羅的に抽出しました。各引用について「Paper 内の引用箇所」「引用元論文」「核心数値の内容」を対応付けています。

**細部精読時に確認すべき項目**:
- 桁数・小数点以下の正確性
- 単位（%, m/s, Hz など）
- 適用条件（IoU 値、評価データセット、クラス数、サイクル数など）
- 文脈整合性（数値が引用元の主張と一致するか）

---

## Paper 1（数値引用 7 グループ）

### P1-N1: Shihavuddin 2019 mAP

| 項目 | 内容 |
|---|---|
| Paper 1 引用箇所 | §2.1 line 52 |
| 引用テキスト | "Their best reported result (Inception-ResNet-V2 with pyramid+patching+regular augmentation) achieved **mAP = 81.1% at IoU = 0.3** on the non-public EasyInspect dataset (4 classes)" |
| 引用元論文 | Shihavuddin et al. 2019, Energies 12(4), 676 |
| 確認すべき細部 | (a) mAP 値 81.1% の正確性、(b) IoU = 0.3 の適用、(c) Inception-ResNet-V2 + pyramid+patching+regular の augmentation 組み合わせ、(d) EasyInspect dataset 4 classes、(e) DTU dataset での per-backbone 結果が同じ形で報告されていないこと |
| 既精読深度 | 全頁精読済（v9 で引用文修正済） |
| 推定リスク | 低（v9 修正で精緻化済） |

### P1-N2: Gohar 2023 mAP@0.5

| 項目 | 内容 |
|---|---|
| Paper 1 引用箇所 | §2.1 line 52 |
| 引用テキスト | "Gohar et al. (2023) re-annotated the publicly-available DTU dataset for 5 defect classes and reported **mAP@0.5 of 81.3% (YOLOv5) and 73.2% (Faster-RCNN)** under their patch-based inference scenario, both at the standard IoU = 0.5 protocol" |
| 引用元論文 | Gohar et al. 2023, Machines 11(10), 953 |
| 確認すべき細部 | (a) 81.3% (YOLOv5)、(b) 73.2% (Faster-RCNN)、(c) IoU = 0.5、(d) patch-based inference scenario、(e) 5 defect classes、(f) DTU dataset 公開版の使用 |
| 既精読深度 | 全頁精読済 |
| 推定リスク | 低 |

### P1-N3: YOLO 派生モデル mAP（Zhao & Li / Shi / Zou × 2）

| 項目 | 内容 |
|---|---|
| Paper 1 引用箇所 | §2.1 line 52 |
| 引用テキスト | "YOLO-Wind [12] reported **83.9% mAP@0.5** on the DTU dataset and DMR-YOLO [13] **82.2%** on the same dataset, while DCW-YOLO [14] (**93.7%**) and AUD-YOLO [15] (**92%**) were evaluated on an independently collected dataset of 600 images from Liaoning/Jiangsu wind farms" |
| 引用元論文 | (12) Zhao & Li 2025, Sci. Rep.; (13) Shi 2026, Appl. Sci.; (14) Zou 2024, Appl. Sci.; (15) Zou 2025, Sci. Rep. |
| 確認すべき細部 | (a) 各モデルの mAP@0.5 数値、(b) データセット帰属（DTU vs Liaoning/Jiangsu 600 枚）、(c) DCW-YOLO / AUD-YOLO の同一研究グループ・同一データセット帰属 |
| 既精読深度 | 全頁精読済（v9.2 で帰属精緻化済） |
| 推定リスク | 低（v9.2 で個別検証済） |

### P1-N4: Malik & Bak 2025 AEP 損失

| 項目 | 内容 |
|---|---|
| Paper 1 引用箇所 | §2.3 line 62 |
| 引用テキスト | "Malik & Bak (2025) used aeroelastic simulations with leading-edge erosion modeled as aerofoil roughness on the **outer 15% of blade length** and reported **AEP losses of 0.82% (mild), 1.46% (severe), and up to 2.14% under high-turbulence conditions**" |
| 引用元論文 | Malik & Bak 2025, Wind Energy Science 10, 227–243 |
| 確認すべき細部 | (a) AEP 損失 3 数値（0.82%, 1.46%, 2.14%）、(b) 軽度・重度・高乱流条件の対応、(c) outer 15%、(d) "aeroelastic simulation" 表記（v9.1 で "experimentally" → simulation に修正済） |
| 既精読深度 | 全17頁精読済（v9.1 修正） |
| 推定リスク | 低 |

### P1-N5: アノテーション分布（Gohar 2023 由来）

| 項目 | 内容 |
|---|---|
| Paper 1 引用箇所 | §3.1 line 82 / §4.2 Table 4 |
| 引用テキスト | "**Class distribution**: LE;ER (41.6%) and VG;MT (34.3%) dominate, while LR;DA (2.3%) and LE;CR (10.2%) are minority classes" |
| 引用元 | Gohar et al. 2023 アノテーション（再アノテーション） |
| 確認すべき細部 | クラス分布パーセンテージが Gohar 2023 のアノテーションファイルと一致するか |
| 推定リスク | 低（自実験の数値、引用元アノテーションファイル参照可能） |

---

## Paper 2（数値引用 9 グループ）

### P2-N1: Mandell 1997 S-N exponent

| 項目 | 内容 |
|---|---|
| Paper 2 引用箇所 | §3.4 line 207-208 |
| 引用テキスト | "Mandell & Samborsky (1997) [18] の DOE/MSU データベースは GFRP の "best-case fiberglass response" を semi-log 表現 S/S₀ = 1 − **b·log N**（同 [18] Eq. 6）における fatigue coefficient **b = 0.10** と報告している（同 [18] Fig. 13(b), Fig. 18, Fig. 24、および繊維含有率 30–42% 帯の D155B / D092D / A130C 等で **b ≈ 0.090–0.108** を実測）。同データベースの log-log 表現 S/S₀ = B·N^(−1/n)（同 [18] Eq. 7）では、**R = 0.1** の longitudinal データに対し **n = 11.6**（**10³–10⁸ cycles**, [18] Table 12）と報告される" |
| 引用元論文 | Mandell & Samborsky 1997, SAND97-3002, DOE/MSU Composite Material Fatigue Database |
| 確認すべき細部 | (a) Eq. 6 / Eq. 7 番号、(b) b = 0.10、(c) b ≈ 0.090-0.108 の D155B/D092D/A130C 各値、(d) Fig. 13(b) / 18 / 24 番号、(e) Table 12 の n = 11.6、(f) R = 0.1、(g) 10³-10⁸ cycles、(h) 繊維含有率 30-42% 範囲 |
| 既精読深度 | pp.1-100 主張駆動精読済（v9.2 で表現精緻化） |
| 推定リスク | **中（数値が多く、引用元の表番号と図番号の正確性は要再確認）** |

### P2-N2: Fingersh 2006 ブレード質量スケーリング

| 項目 | 内容 |
|---|---|
| Paper 2 引用箇所 | §2 line 122 |
| 引用テキスト | "Fingersh et al. (2006) はNRELの風車設計コスト・スケーリングモデルにおいて、ブレード質量のスケーリング則として **baseline = 0.1452 × R^2.9158、advanced = 0.4948 × R^2.53 per blade** を提示した [15]" |
| 引用元論文 | Fingersh et al. 2006, NREL/TP-500-40566 |
| 確認すべき細部 | (a) baseline 係数 0.1452、指数 2.9158、(b) advanced 係数 0.4948、指数 2.53、(c) "per blade" の単位、(d) v8.0 で訂正された値 |
| 既精読深度 | 精読済（v8.0 で訂正） |
| 推定リスク | 低（v8.0 で訂正済） |

### P2-N3: Bak 2013 DTU 10-MW スケーリング

| 項目 | 内容 |
|---|---|
| Paper 2 引用箇所 | §2 line 122 |
| 引用テキスト | "Bak et al. (2013) もglass fiber: **Mass = 0.0023 × Length^2.17**、carbon fiber: **Mass = 9×10^-5 × Length^2.95** を報告している [3]" |
| 引用元論文 | Bak et al. 2013, DTU Wind Energy Report-I-0092 |
| 確認すべき細部 | (a) glass fiber 係数 0.0023, 指数 2.17、(b) carbon fiber 係数 9×10⁻⁵, 指数 2.95、(c) Length の単位（m）、(d) "古典的関係 Mass ~ Diameter^3" の言及位置 |
| 既精読深度 | 精読済 |
| 推定リスク | 低 |

### P2-N4: Hayman 2012 MLife DEL 正規化

| 項目 | 内容 |
|---|---|
| Paper 2 引用箇所 | §3.4 line 205 |
| 引用テキスト | "*N_eq (equivalent cycle count) is the product of an assumed reference frequency (**1 Hz**) and the equivalent time period **T_eq = 600 s**, yielding **N_eq = 600** equivalent cycles per simulation. The DEL normalization framework (the structure DEL = (Σ n_i ΔS_i^m / N_eq)^(1/m), where N_eq corresponds to **f^eq × T_j in Hayman (2012) [10] Eq. 26**) follows Hayman (2012)" |
| 引用元論文 | Hayman 2012, MLife Theory Manual, NREL |
| 確認すべき細部 | (a) Eq. 26 の番号、(b) f^eq, T_j パラメータ表記、(c) MLife 内では f^eq, T_j は抽象パラメータで、N_eq = 600 は本研究の選択であること、(d) IEC 61400-1:2019 の 10-minute simulation duration との整合性 |
| 既精読深度 | 全頁精読済（v9.3 で表現精緻化） |
| 推定リスク | 低（v9.3 で精緻化済） |

### P2-N5: Jonkman 2009 NREL 5-MW 諸元

| 項目 | 内容 |
|---|---|
| Paper 2 引用箇所 | §3.2 line 157 |
| 引用テキスト | "NREL 5MW参照タービン（**R=63 m, P=5 MW, Tower top/TurbSim RefHt=87.6 m, Hub Height=90 m**）...Jonkman et al. (2009) [2] のTable 1-1ではNREL 5MWのHub Heightは90 mと定義されており、87.6 mはtower top（yaw bearing）高さである" |
| 引用元論文 | Jonkman et al. 2009, NREL/TP-500-38060 |
| 確認すべき細部 | (a) Table 1-1 の番号、(b) Rotor radius 63 m、(c) Rated power 5 MW、(d) Hub Height 90 m、(e) Tower top/TurbSim RefHt 87.6 m、(f) yaw bearing 高さの解釈 |
| 既精読深度 | 全頁精読済（v8.0 で曖昧性解消） |
| 推定リスク | 低（v8.0 で訂正済） |

### P2-N6: IEC 61400-1:2019 仕様

| 項目 | 内容 |
|---|---|
| Paper 2 引用箇所 | §3.2 line 149, 187, 257 / §4 line 569 |
| 引用テキスト | (a) "Seeds per condition | **6 (IEC 61400-1:2019 §8.3.2 minimum requirement [7])**" (b) "**§6.3** のデフォルト式に従う（**Λ_1 = 42 m for HH ≥ 60 m**; Λ_1 = 0.7 × HH for HH < 60 m）" (c) "**TI > 0.5**...IEC 61400-1:2019 [7] のNTMモデルにおいて想定されるTI範囲を大幅に超過する値" (d) "**DLC 1.3**（Extreme Turbulence Model）...8風速 × 6シード = 48ケース" |
| 引用元規格 | IEC 61400-1:2019 |
| 確認すべき細部 | (a) §8.3.2 6-seed minimum requirement の出典正確性、(b) §6.3 Λ_1 = 42 m for HH ≥ 60 m、Λ_1 = 0.7 × HH for HH < 60 m、(c) §7.4 / §7.6 (extreme load vs fatigue load) 項番、(d) DLC 1.2 NTM, DLC 1.3 ETM, DLC 2.1 Grid Loss の各定義、(e) Power Law 指数 α = 0.2 の標準値 |
| 既精読深度 | **DRAFT 確認のみ（IEC 規格全体は未取得・未精読）** |
| 推定リスク | **中（規格番号の正確性は未検証、ただし引用慣行としては規格番号で十分）** |

### P2-N7: Penmanshiel SCADA 仕様

| 項目 | 内容 |
|---|---|
| Paper 2 引用箇所 | §2 line 130 |
| 引用テキスト | "Penmanshiel Wind Farmの公開SCADAデータセット [5]（Zenodo, CC-BY 4.0）は、**Senvion MM82（14台, 2.05 MW）の10分値データを2016–2021年**にわたり提供する" |
| 引用元 | Plumley 2022 Penmanshiel Wind Farm Data, Zenodo |
| 確認すべき細部 | (a) 14 台数、(b) 2.05 MW 定格、(c) 2016-2021 年範囲、(d) 10 分値、(e) MM82 機種 |
| 既精読深度 | データ自体は使用済 |
| 推定リスク | 低 |

### P2-N8: TI 計測の差異

| 項目 | 内容 |
|---|---|
| Paper 2 引用箇所 | §1.4 line 84 / §5 line 493 |
| 引用テキスト | "(a) 風速ビン内の統計量から近似するアプローチ（bin-averaged TI）と、IEC 61400-1:2019 [7] 準拠の10分間値直接計測では、得られるTIに数倍の差が生じうる（本研究での検証結果: **近似値 ~0.035 vs. 直接計測 ~0.14**）" "(b) "Penmanshielの直接計測TI（**中央値0.133〜0.144**）は、bin近似TI（**~0.035**）と**約4倍の差**を示した" |
| 引用元 | 本研究の検証結果（外部論文引用ではない） |
| 確認すべき細部 | 自実験の数値整合性のみ（外部引用なし） |
| 推定リスク | 低（自実験） |

### P2-N9: DEL 結果（Table 7b）

| 項目 | 内容 |
|---|---|
| Paper 2 引用箇所 | §4.3 Table 7b |
| 引用テキスト | "Lifetime DEL by IEC Class (NREL 5MW, kN·m) | Class I (Vave=10.0 m/s) | Class II (Vave=8.5 m/s) | Class III (Vave=7.5 m/s)" |
| 引用元 | 本研究の計算結果（IEC 61400-1:2019 Class 定義との対応） |
| 確認すべき細部 | (a) Vave 値（10.0, 8.5, 7.5 m/s）の IEC 規格との対応、(b) DEL 計算結果の数値整合性 |
| 推定リスク | 低（自実験 + 規格定義） |

---

## Paper 3（数値引用 4 グループ）

### P3-N1: Yang 2013 fault detection 実証

| 項目 | 内容 |
|---|---|
| Paper 3 引用箇所 | §2.2 line 100 |
| 引用元論文 | Yang et al. 2013, Renewable Energy 53, 365-376 |
| 副次発見の数値（B5 引用候補で活用） | "c=0→59.9 で月毎に劣化進行（4 ヶ月）"、"c=0→0.75（generator bearing failure）" |
| 確認すべき細部（引用追加時） | (a) blade failure case の c値変化（0→59.9 over 4 months）、(b) generator bearing case の c値変化（0→0.75）、(c) §5.1 / §5.2 の章番号 |
| 既精読深度 | 全12頁精読済（B5 引用候補に活用） |
| 推定リスク | 低 |

### P3-N2: Hu 2025 DT 性能指標

| 項目 | 内容 |
|---|---|
| Paper 3 引用箇所 | §2.4 line 102 周辺（Hu 2025 DT 引用） |
| 副次発見の数値（B5 引用候補で活用） | "RDSS-YOLO NN: **mAP 95.7%, precision 93.9%, recall 96.8%, MIoU 81.5%**（augmented DTU dataset）" |
| 引用元論文 | Hu et al. 2025, Renewable Energy 241, 122332 |
| 確認すべき細部（引用追加時） | (a) mAP 95.7%、(b) precision 93.9%、(c) recall 96.8%、(d) MIoU 81.5%、(e) augmented DTU dataset の使用、(f) RDSS-YOLO の構成（YOLOv5 + Swin Transformer + Small-scale prediction head + PSPNet）|
| 既精読深度 | 全44頁精読済 |
| 推定リスク | 低 |

### P3-N3: Pandit 2023 SCADA 制約

| 項目 | 内容 |
|---|---|
| Paper 3 引用箇所 | §2.1 line 92 |
| 引用テキスト | （引用文中の数値）"**10 minutes averaging time**"、"SCADA targets secondary effects"|
| 引用元論文 | Pandit et al. 2023, Wind Engineering 47(2), 422-441 |
| 確認すべき細部 | (a) p.428 の "10 minutes averaging time" 表現、(b) "SCADA targets secondary effects" の文脈 |
| 既精読深度 | 全20頁精読済（v5.2 で引用文修正） |
| 推定リスク | 低 |

### P3-N4: Branlard 2020 DT 役割

| 項目 | 内容 |
|---|---|
| Paper 3 引用箇所 | §2.4 line 102 |
| 引用元論文 | Branlard et al. 2020, J. Phys. Conf. Ser. 1618, 022030 |
| 引用テキスト（要旨） | "OpenFAST linearizations for **real-time load and fatigue estimation** of land-based turbines" |
| 確認すべき細部 | タイトル正確性（v5.1 で "and fatigue" 追加） |
| 既精読深度 | 全12頁精読済 |
| 推定リスク | 低（v5.1 で訂正済） |

---

## 細部精読の優先順位（Claude Code の推定）

### 優先度高（数値が多く、表番号・図番号を含むため誤読リスクが相対的に大きい）

| # | 引用 | 理由 |
|---|---|---|
| 1 | **P2-N1 Mandell 1997**（b=0.10, n=11.6, Eq.6/7, Fig.13(b)/18/24, Table 12） | 9 個の数値・式・図表番号が連続して引用されており、桁単位・図番号単位の誤読リスクが高い |
| 2 | **P2-N6 IEC 61400-1:2019**（§6.3, §7.4, §7.6, §8.3.2, Λ_1, DLC 1.2/1.3/2.1） | 規格項番が複数あり、規格本体は未取得のため、項番の正確性は外部検証推奨 |

### 優先度中

| # | 引用 | 理由 |
|---|---|---|
| 3 | P2-N2/N3 Fingersh 2006 / Bak 2013（スケーリング指数） | v8.0 で訂正済だが、係数値の小数点以下確認は再度推奨 |
| 4 | P2-N5 Jonkman 2009 NREL 5-MW（Table 1-1） | v8.0 で訂正済 |
| 5 | P3-N2 Hu 2025（mAP/precision/recall/MIoU 4 数値） | 4 つの精度指標を連続引用、桁単位確認推奨 |

### 優先度低（既に十分検証されている）

| # | 引用 | 理由 |
|---|---|---|
| 6 | P1-N1 Shihavuddin 2019 / P1-N2 Gohar 2023 | v9 で精緻化済、文脈整合性も確認済 |
| 7 | P1-N3 YOLO 派生モデル（4 件） | v9.2 で帰属精緻化済 |
| 8 | P1-N4 Malik & Bak 2025 | v9.1 で表現修正済 |

---

## 細部精読のチェックリスト形式（将来の作業用）

論文取得後に細部精読を実施する際は、以下のチェックリストを活用：

```
□ 数値が引用元の正確な値と一致するか（桁数・小数点・単位）
□ 数値の適用条件（IoU/評価データセット/クラス数/サイクル数等）が一致するか
□ 図表番号・章番号・式番号が引用元と一致するか
□ 数値の出現箇所（Abstract / 本文 / Table / Fig）が引用元で正しく特定されているか
□ 文脈整合性（数値が引用元の主張と矛盾しないか）
□ 単位の統一（kN·m, m/s, Hz, % など）
```

---

## 関連メモ

- `B1_crossref_audit_2026-04-29.md` — 書誌レベルの監査結果
- `B5_incidental_findings_citation_candidates_2026-04-29.md` — 副次発見の引用候補集
- `batch10_round1_revision_proposals.md` — 第10バッチ第1ラウンド修正案
- `batch10_round2A_progress_2026-04-29.md` — 第2ラウンド-A 精読記録
- `memory/project_blade_paper_audit_progress.md` — 監査全体の進捗
