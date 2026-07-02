# 第10バッチ第2ラウンド-B 第1部 精読進捗（2026-04-29）

**目的**: data/ フォルダから発見された2本（Vera-Tudela 2017 / Heo & Na 2025）の主張駆動完全精読の結果記録

**精読順序**: Vera-Tudela 2017 → Heo & Na 2025

---

## 1. Vera-Tudela & Kühn (2017)（全9頁、完了）✅

**ファイル**: `data/9_VeraTudela_2017.pdf`

**書誌**:
- Title: Analysing wind turbine fatigue load prediction: The impact of wind farm flow conditions
- Authors: Luis Vera-Tudela, Martin Kühn
- Affiliation: ForWind - Carl von Ossietzky University of Oldenburg, Germany
- Journal: Renewable Energy 107 (2017) 352-360
- DOI: 10.1016/j.renene.2017.01.065
- Received 22 Jan 2016, Revised 16 Jan 2017, Accepted 30 Jan 2017
- 取得経緯: himinさんによる data/ フォルダ配置（取得経路は memory に未記録）

**論文概要**:
- データ駆動型疲労荷重予測モデル（neural network）を、Wind farm flow 条件下で評価
- データ：EnBW Baltic 1 オフショア風車（21台 Siemens 2.3MW、HH=93m）の B01/B08 タービン
- 計測：2013年3月〜2014年3月（1年間）の SCADA + 機械的荷重計測（IEC 61400-13 準拠）
- 6 つの wind farm flow conditions: free stream / single wake / mixing wake / multiple wake / platform wake / all data
- 48 cases（2 indicators × 2 blades × 2 turbines × 6 scenarios）の neural network 予測評価

**主要結果**:
- Wind farm flow conditions が短期予測の質に影響、長期評価では cancel out
- Edgewise direction：average relative error <0.1%, std 1.9%（gravitational loading dominant でほぼ deterministic）
- Flapwise direction：average relative error <1.5%, std 11.2%（thrust dominant で wake の影響大）
- NTL (Natural Tolerance Limits): edgewise 0.07%±6.45%, flapwise 1.27%±32.83%
- Lifetime Δeq 推定の overall accuracy: 97.32%〜100.19%

**Paper 2 [20] の引用検証**:

### 検証ポイント 1: Paper 2 §2.3 line 126

> "Vera-Tudela & Kühn (2017) [20] はSCADA信号からの疲労荷重予測を実証し"

| 主張 | 結果 | 根拠 |
|---|---|---|
| V1: SCADA信号からの疲労荷重予測を実証 | ✅ **完全整合** | §2.4 Regression analysis: feed-forward neural network で 10-min SCADA 統計量 → blade root edgewise/flapwise DEL を予測。§3 Evaluation で 48 cases 評価、Table 4-6 で precision/accuracy を定量化 |

→ **Paper 2 line 126 引用は完全整合、修正不要**

### 検証ポイント 2: Paper 2 §1.4 line 99（A5 対象）

> "**bin-averaged vs. 直接計測TIの実データ差異**: 約4倍の差を実サイトデータで確認（既存文献での同種指摘の有無は第10バッチで Vera-Tudela & Kühn 2017 / Dimitrov et al. 2015 を全頁精読後に確定）"

| 確認項目 | 結果 |
|---|---|
| 本論文で「bin-averaged TI vs 直接計測 TI」の比較を扱っているか | ❌ **扱っていない** |
| TI（turbulence intensity）という用語の本文中での明示的使用 | ❌ **Nomenclature にも本文にも明示的言及なし** |
| 風速統計量の扱い | ✅ 入力変数として mean, max, min, range, variance, std, skewness, kurtosis を使用 |
| IEC 規格の引用 | IEC 61400-13（mechanical loads measurement）と IEC 61400-1（design requirements, ref [2]）を引用 |

→ **Vera-Tudela 2017 は Paper 2 line 99「bin-averaged vs 直接計測 TI の差異」の引用先として不適切**

### A5 暫定結論

Vera-Tudela 2017 だけでは line 99 の引用先確定不可。残る選択肢：

1. **Dimitrov 2015 取得・精読を待つ**（取得待ち）
2. **「既存文献に同種指摘なし、本研究で初めて実データで報告」と結論**
3. **別の引用先（IEC 61400-1 §6.3 turbulence model 規定）に変更**

→ Dimitrov 2015 の精読結果に依存して最終判断。himinさん の判断事項。

**重要副次発見**:

1. **EnBW Baltic 1 dataset の概要**
   - 21台 Siemens 2.3MW、Darß 半島北方、ドイツ・バルト海オフショア
   - 計測は WIND-consult 社、IEC 61400-13 standard 準拠
   - SCADA 信号: wind speed, electrical power, generator speed, pitch angle, yaw direction, nacelle acceleration (fore-aft & side-to-side)
   - 10-min statistics: mean, max, min, range, variance, std, skewness, kurtosis

2. **Edgewise vs Flapwise の精度差の物理的根拠**
   - Edgewise: gravitational loading dominant → 重力で振幅がほぼ一定 → deterministic
   - Flapwise: thrust dominant → wake effects に強く影響される
   - → Paper 1/2/3 で blade root **flapwise** に着目している場合、本論文の知見と整合する

3. **Hampel identifier による outlier 除去（k=15, z=4.5）**
   - moving window filter
   - Paper 2 の QC フィルタ設計の参考になる可能性

4. **Pearson correlation の閾値 Corr ≥ 0.5 で入力変数選定**
   - bootstrap algorithm（1000 randomized sampling）で安定性確認
   - 高相関ペア（|Corr| > 0.95）の片方を削除して redundancy 排除
   - Paper 1/2 のシンプルな feature engineering の参考

---

## 2. Heo & Na (2025)（全18頁、完了）✅

**ファイル**: `data/electronics-14-00227.pdf`

**書誌**:
- Title: Review of Drone-Based Technologies for Wind Turbine Blade Inspection
- Authors: Seong-Jun Heo, Wongi S. Na
- Affiliation: Department of Civil Engineering, Seoul National University of Science and Technology, Republic of Korea
- Journal: Electronics 14, 227 (2025)
- DOI: 10.3390/electronics14020227
- License: CC-BY 4.0
- Editor: **Davide Astolfi**（Paper 3 [18] Castellani et al. 2024 の共著者）
- Received 1 Dec 2024, Published 8 Jan 2025
- 取得経緯: himinさんによる data/ フォルダ配置（経緯は失念）

**論文構成**:
- §1 Introduction
- §2 Different Drone Types（multirotor / fixed-wing / hybrid VTOL）
- §3 Drone Path Planning for Inspection
- §4 Commonly Used Turbine Blade Inspection Sensing Technologies for Drones
  - §4.1 High-Resolution Cameras
  - §4.2 Thermal Imaging
  - §4.3 LiDAR
- §5 Ultrasonic and Acoustic Emission Techniques in Drone-Based Wind Turbine Blade Inspection
- §6 Challenges and Limitations
- §7 Conclusions

### Paper 1 / Paper 3 との関連性評価

**論文の主軸**: Drone hardware + multi-modal sensing technology の網羅レビュー

**Paper 1 との関連**:
- ✅ **直接関連**（ドローンベースのブレード点検レビュー）
- §4.1 で **Shihavuddin 2019 [41] を 80%+ accuracy として引用**、Figure 3 で **LE erosion / VG panel / Lightning receptor** の検出例を提示
- これは Paper 1 のクラス分類（LE;ER / VG;MT / LR;DA 等）と完全に一致
- ただし本論文の主軸は **sensing modality 比較** であり、Paper 1 のような **camera + DL の精度評価** ではない
- → Paper 1 §2.1 Related Work の **追加 Survey 引用候補**

**Paper 3 との関連**:
- ✅ **間接関連**（multi-modal sensing integration の提唱）
- §6 で satellite × drone integration を提案 → Paper 3 §1 Introduction の SCADA × 画像 × 気象データ統合に類似
- ただし Heo & Na 2025 は **drone sensors の multi-modality**（camera/thermal/LiDAR/UT/AE）であり、Paper 3 の **SCADA + image + meteorological data** とは異なる軸の融合
- → Paper 3 §2 Related Work の **multi-modal context 補強候補**

### 主張駆動検証

| 主張 | 結果 |
|---|---|
| H1: ドローンベース風車ブレード点検技術の包括的レビュー | ✅ 完全整合（Title 直接、§1-§7 全体構成で網羅） |
| H2: Sensing technology（camera/thermal/LiDAR/UT/AE）の比較分析 | ✅ 完全整合（Table 1 で 5 modality を defects/advantages/limitations/cost/adoption の 5 軸で比較） |
| H3: Drone path planning と hardware の論述 | ✅ 完全整合（§2 / §3 で詳述） |

### Paper 1 引用候補位置（任意・優先度中）

**Paper 1 §2.1 Related Work（Survey 引用パラグラフ）**:

> 現状: Memari 2024 [10], Masita 2025 [11] の survey を引用

> 追加候補: 
> "Heo & Na (2025) [新規] provided a recent overview of drone-based blade inspection technologies, comparing five sensing modalities (camera, thermal, LiDAR, ultrasonic, and acoustic emission). Their analysis confirms that camera-based methods remain the most widely adopted while thermal imaging and LiDAR are gaining traction for subsurface and structural deformation detection."

### Paper 3 引用候補位置（任意・優先度中）

**Paper 3 §2.1 SCADA-based methods または §6 Future Directions**:

> 追加候補:
> "ドローン点検側の multi-modal integration として、Heo & Na (2025) [新規] は camera/thermal/LiDAR/UT/AE の 5 modality の補完性を整理し、satellite データとの融合の可能性も指摘している。本研究の SCADA × image × meteorological data 統合は、点検モダリティ側ではなく **データソース側の融合**を志向する点で補完的な方向性である。"

### 重要副次発見：Heo & Na 2025 で引用されている未引用論文

Paper 1/3 で **未引用** だが、本研究と関連性のある論文：

| # | 論文 | 関連分野 | Paper 1/3 への適合性 |
|---|---|---|---|
| 1 | **Mishnaevsky Jr 2021** "Leading edge erosion of wind turbine blades: Understanding, prevention, and protection" Renew. Energy 169:953-967 | LE erosion 物理メカニズム | **🔴 高**：Paper 1/2/3 すべての erosion 文脈で核心引用候補 |
| 2 | **Aird & Barthelmie 2023** "Automated quantification of wind turbine blade leading edge erosion from field images" Energies 16:2820 | LE erosion 画像定量化 | **🟡 中-高**：Paper 1 のリスクスコアリングの先行研究として参照可能 |
| 3 | **Law & Koutsos 2020** "Leading edge erosion of wind turbines: Effect of solid airborne particles and rain on operational wind farms" Wind Energy 23:1955-1965 | LE erosion 実機運用評価 | **🟡 中**：Paper 1 §2.3 / Paper 2 動機文脈で参照可能 |
| 4 | **Katsaprakakis 2021** "A comprehensive analysis of wind turbine blade damage" Energies 14:5974 | ブレード damage 包括分析 | **🟢 中**：Paper 1 Related Work の Survey 補強 |
| 5 | **Iyer 2022** "Learning to identify cracks on wind turbine blade surfaces using drone-based inspection images" arXiv 2207.11186 | クラック検出専用 | **🟡 中**：Paper 1 §4.2 LE;CR 検出失敗議論で参考になる先行例 |
| 6 | **Yang 2023** "Towards accurate image stitching for drone-based wind turbine blade inspection" Renew. Energy 203:267-279 | 画像スティッチング | **🟢 低-中**：Paper 1 / Paper 3 §6 Future work で参照可能（Gohar 2025 §5.1 でも引用済） |
| 7 | **Dhiman & Khan Nizami 2024** "Wind turbine blade erosion detection using visual inspection and transfer learning" ICCAD | erosion 検出 + transfer learning | **🟡 中**：Paper 1 §2.1 YOLO 派生モデル群と並列引用候補（Gohar 2025 でも引用済） |
| 8 | **Xu 2019** "Wind turbine blade surface inspection based on deep learning and UAV-taken images" J. Renew. Sustain. Energy 11:053305 | ドローン画像 DL 検出 | **🟢 中**：Paper 1 §2.1 先行研究厚みの補強 |
| 9 | **Wang & Zhang 2017** "Automatic detection of wind turbine blade surface cracks based on UAV-taken images" IEEE Trans. Ind. Electron. 64:7293-7303 | クラック検出（古典） | **🟢 低-中**：Paper 1 §2.1 historical context |
| 10 | **Pierce 2018** "Quantitative inspection of wind turbine blades using UAV deployed photogrammetry" EWSHM | photogrammetry 定量化 | **🟢 低**：参考程度 |
| 11 | **Reddy 2019** "Detection of Cracks and Damage in Wind Turbine Blades Using Artificial Intelligence-Based Image Analytics" Measurement 147:106823 | AI ベース画像分析 | **🟢 低-中**：Paper 1 §2.1 補強 |
| 12 | **Tan & Zhang 2022** "Research on surface defect detection technology of wind turbine blade based on UAV image" Instrumentation 9:41-48 | 表面欠陥検出 | **🟢 低**：参考程度 |

### Mishnaevsky Jr 2021 の特別な位置づけ

**最も重要な未引用候補**:
- LE erosion の **物理メカニズム + 防護策の包括的レビュー**
- 著者は LE erosion 分野の中核研究者
- Paper 1/2/3 すべての erosion 関連論述で引用候補：
  - Paper 1 §1 Introduction（erosion の物理機序）
  - Paper 1 §2.3 Risk scoring（重み付けの物理的根拠強化）
  - Paper 2 §1 Introduction（動機の物理的根拠）
  - Paper 3 §1 Introduction（劣化予測の物理的根拠）

himinさんの研究動機（ロープアクセス補修経験から）と直結する可能性が高く、研究の **物理的・実務的厚み** を加える素材として最有力候補。

---

## 3. 既存第10R2-B 進捗状況の更新

| 第10R2-B 7本 | 取得状況 | 精読状況 |
|---|---|---|
| ✅ Vera-Tudela & Kühn 2017 | **取得済** | **✅ 完了（本日）** |
| ⏸ Dimitrov 2015 | 未取得 | 未精読 |
| ⏸ Cha 2017 | 未取得 | 未精読 |
| ⏸ Dao 2018 | 未取得 | 未精読 |
| ⏸ Liu 2024 | 未取得 | 未精読 |
| ⏸ Nielsen & Sørensen 2011 | 未取得 | 未精読 |
| ⏸ Yeter 2020 | 未取得 | 未精読 |

加えて：
| 関連論文 | 取得状況 | 精読状況 |
|---|---|---|
| ✅ Heo & Na 2025（Electronics 14, 227） | **取得済（経緯不明）** | **✅ 完了（本日）** |

---

## 4. 監査結果のまとめ

### Vera-Tudela 2017
- Paper 2 line 126 引用は **完全整合・修正不要**
- Paper 2 line 99（A5: bin-averaged vs 直接計測 TI）の引用先としては **不適切**
  - → Dimitrov 2015 取得後に最終判断

### Heo & Na 2025
- Paper 1 / Paper 3 の Related Work で引用可能だが **必須ではない**（任意・優先度中）
- 主要な価値は **本論文経由で発見される未引用重要論文12本**
  - 特に **Mishnaevsky Jr 2021 (LE erosion 包括レビュー)** が最有力候補

### A 群への追加候補（B 群作業時点では未追加）

| # | 案件 | 工数 | Claude Code 推定優先度 |
|---|---|---|---|
| A9 | Paper 1 / 2 / 3 に Mishnaevsky Jr 2021 LE erosion を引用追加 | 中（書誌追加要） | **🔴 高**（物理機序の補強） |
| A10 | Paper 1 / 3 に Heo & Na 2025 を Survey 引用として追加 | 小 | 中 |
| A11 | Aird & Barthelmie 2023 / Law & Koutsos 2020 等の追加 erosion 関連論文の引用検討 | 中 | 中 |

---

## 5. 関連ファイル

- `tools/reference_audit/batch10_round2A_progress_2026-04-29.md` — 第2ラウンド-A 精読記録
- `tools/reference_audit/B5_incidental_findings_citation_candidates_2026-04-29.md` — 副次発見の引用候補集
- `tools/reference_audit/B6_mid_audit_summary_2026-04-29.md` — 監査全体の中間サマリ
- `memory/project_blade_paper_audit_progress.md` — 精読進捗メモリ
