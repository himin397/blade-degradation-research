# Paper 3: 風車ブレード劣化予測に向けた画像・SCADA・空力シミュレーション統合パイプラインの設計とギャップ分析

**ステータス**: v3.0（最終調整）
**最終更新**: 2026-04-04

---

## タイトル案（推奨順）

1. **Toward Multi-Modal Blade Degradation Assessment: Pipeline Design, Data Requirements, and Research Roadmap for Image–SCADA–Simulation Integration** ← 推奨（設計論・ロードマップを前面化）
2. **Architecture and Gap Analysis for Wind Turbine Blade Degradation Risk Assessment: Integrating Image-Based Damage Scores, SCADA Fatigue Indicators, and Aeroelastic Calibration**
3. **Designing an Integration Pipeline for Blade Degradation Risk Scoring: Component Summary, Gap Analysis, and Data Requirements from Public-Data Pilot Studies**

## 1文主張

> 画像損傷スコア・SCADA疲労荷重指標・空力シミュレーション較正を接続する統合パイプラインを設計し、真の統合研究に必要なデータ要件と残存ギャップを明確化した。

---

## 章立て

```
1. Introduction
   1.1 Background and Motivation
   1.2 Problem: The Integration Gap
   1.3 Objective and Scope
2. Component Summary
   2.1 Image-Based Damage Detection and Risk Scoring (Paper 1)
   2.2 Fatigue Load Estimation Framework (Paper 2)
   2.3 Physical Calibration via OpenFAST
3. Integration Pipeline Design
   3.1 Architecture Overview
   3.2 I/O Specification
   3.3 Fusion Logic and Weight Design
   3.4 Implementation Status
4. I/O Connection Test (Synthetic Data)
5. Gap Analysis
   5.1 What Has Been Achieved
   5.2 What Remains Unresolved
   5.3 Data Requirements for True Integration
6. Research Roadmap
   6.1 Short-Term: Same-Turbine Data Acquisition
   6.2 Medium-Term: Master's Research Design
   6.3 Long-Term: Toward Predictive Degradation Modeling
7. Conclusion
References
```

---

## Abstract

風車ブレードの劣化予測には、表面損傷の画像情報、運転荷重履歴、および物理モデルによる較正を統合するアプローチが必要とされている [9][10]。本研究では、公開データを用いた先行研究（画像損傷検出: Paper 1、疲労荷重推定基盤: Paper 2）の成果を部品として、3モダリティを接続する統合パイプラインのアーキテクチャとI/O仕様を設計した。

パイプラインは、画像由来のスパン方向リスクスコア、SCADA由来の月次DEL推定値、およびOpenFASTによる重み較正係数を入力とし、タービン別・月別の統合リスクスコアを出力する。合成データによるI/O接続テストでデータフローの整合性を確認したが、これはパイプライン動作の確認であり、予測性能の検証ではない。

画像データ（DTU/Nordtank）とSCADAデータ（Penmanshiel/MM82）は異なるタービン・異なるサイトであり、同一タービン上での統合検証は未達である。本研究の主たる価値は、統合パイプラインの設計図、真の統合に必要なデータ要件の明確化、および修士・博士研究への段階的ロードマップの提示にある。

---

## 1. Introduction

### 1.1 Background and Motivation

風車ブレードは20年以上の運用期間を通じて、エロージョン、亀裂、雷撃損傷等の表面劣化と、繰り返し疲労荷重による構造的劣化を同時に受ける [10]。現行のO&M実務では、定期的なドローン点検やロープアクセス点検による画像評価と、SCADAデータに基づく運転状態監視が独立に行われている [9]。しかし、表面損傷の視覚的評価と運転荷重履歴を統合して劣化進行リスクを定量的に評価する枠組みは、まだ確立されていない。

### 1.2 Problem: The Integration Gap

劣化予測に必要な3種の情報 ― 画像由来の損傷状態、SCADA由来の荷重履歴、物理モデルによる荷重較正 ― は独立に発展してきた。統合の主要な障壁は:

1. **データの非同一性**: 公開画像データセット（DTU等）と公開SCADAデータセット（Penmanshiel等）は異なるタービン・異なるサイトであり、同一タービンの同時期データは一般に非公開
2. **I/Oの不整合**: 画像検出の出力（バウンディングボックス、クラス、信頼度）とSCADA指標の出力（月次統計量）は粒度・形式が異なる
3. **重みの根拠不在**: 画像スコアと荷重スコアを統合する際の重み（α, β）に、データ駆動の根拠が存在しない

### 1.3 Objective and Scope

本研究の目的は、(1) Paper 1・Paper 2 の成果を接続する統合パイプラインのアーキテクチャとI/O仕様を設計し、(2) 合成データで動作を確認し、(3) 同一タービンでの真の統合研究に必要なデータ要件と残存ギャップを明確化することである。統合予測モデルの性能実証は対象外（予備研究）である。

---

## 2. Component Summary

### 2.1 Image-Based Damage Detection and Risk Scoring (Paper 1)

Paper 1では、DTU公開画像559枚にYOLOv8n＋ピラミッドパッチ拡張を適用し、5損傷クラスの検出（mAP@0.5 = 0.58）とスパン方向リスクスコア（Tip/Mid/Root）を算出した。既知の制約として、LE;CR検出不能（AP = 0.00）、chord方向除外、重みはpractitioner-informed priorsである（Paper 1 §3.4）。

**出力粒度の注記**: DTU画像は単一サイト（Nordtank）の横断的データであり、turbine_id × monthの時系列粒度を持たない。Table 1の出力スキーマは実機での定期点検データ蓄積後に実現される将来仕様であり、現状は「1時点分」に相当する。

### 2.2 Fatigue Load Estimation Framework (Paper 2)

Paper 2では、NREL 5MWからSenvion MM82への幾何スケーリングとPenmanshiel公開SCADAのIEC準拠TI直接計測を組み合わせ、月次・年次DEL推定基盤を構築した。統合パイプラインへの出力は月次DEL推定値（kN·m）と疲労リスクスコア（0–1正規化）であり、タービンID × 月の粒度を持つ。既知の制約として、MM82翼型プロキシは相対比較のみ有効であり、DLC 1.2単独での推定である（詳細はPaper 2 §5.4）。

### 2.3 Physical Calibration via OpenFAST

Paper 2のDELマトリクス（8V × 5TI）とw_V/w_TI較正（MM82: 0.725/0.275, R² = 0.943）は、Module B内部での風況→DEL変換に物理的根拠を付与する。統合層のα/β較正は補修記録が必要であり未達（§3.3で詳述）。

---

## 3. Integration Pipeline Design

### 3.1 Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│ Module A: Image Risk Scoring (Paper 1 output)       │
│   Input:  Drone images → YOLOv8n detection          │
│   Output: [turbine_id, month, tip_score, mid_score, │
│            root_score, image_risk_composite]         │
└────────────────────┬────────────────────────────────┘
                     │
                     │ merge on [turbine_id, month]
                     │
┌────────────────────▼────────────────────────────────┐
│ Module B: SCADA Fatigue Estimation (Paper 2 output) │
│   Input:  10-min SCADA → DEL matrix interpolation   │
│   Output: [turbine_id, month, DEL_est_kNm,          │
│            fatigue_risk_score]                       │
└────────────────────┬────────────────────────────────┘
                     │
                     │ weighted fusion
                     │
┌────────────────────▼────────────────────────────────┐
│ Module C: Integration & Risk Assessment             │
│   Fusion: α × image_risk + β × fatigue_risk         │
│   Output: [turbine_id, month, integrated_risk,      │
│            ranking, priority_flag]                   │
└─────────────────────────────────────────────────────┘
                     │
                     ▼
         Physical Calibration Layer (Paper 2)
         w_V / w_TI → fatigue_risk の内部較正
         α / β → 統合重みの将来較正（要: 補修記録）
```

### 3.2 I/O Specification

**Table 1: Module A Output Schema**

| Column | Type | Source | Description |
|---|---|---|---|
| turbine_id | str | Inspection record | タービン識別子 |
| month | int | Inspection date | 月（1–12） |
| tip_score | float | Paper 1 §3.4 | Tip領域リスクスコア |
| mid_score | float | Paper 1 §3.4 | Mid領域リスクスコア |
| root_score | float | Paper 1 §3.4 | Root領域リスクスコア |
| image_risk_composite | float | 加重和 | (tip×3 + mid×2 + root×1) / 6 |

**Table 2: Module B Output Schema**

| Column | Type | Source | Description |
|---|---|---|---|
| turbine_id | str | SCADA record | タービン識別子 |
| month | int | SCADA timestamp | 月（1–12） |
| DEL_est_kNm | float | Paper 2 §3.7 | 月次DEL推定値（kN·m） |
| fatigue_risk_score | float | 0–1正規化 | DELの全タービン横断正規化 |

**Table 3: Module C Output Schema**

| Column | Type | Description |
|---|---|---|
| turbine_id | str | タービン識別子 |
| month | int | 月（1–12） |
| integrated_risk | float | α × image_risk + β × fatigue_risk |
| integrated_risk_norm | float | 0–1正規化済み統合リスク |

### 3.3 Fusion Logic and Weight Design

統合リスクスコアは以下の線形結合で算出する:

```
integrated_risk = α × image_risk_composite + β × fatigue_risk_score
```

| Parameter | 現状値 | 根拠 | 将来の改善方向 |
|---|---|---|---|
| α (image weight) | 0.5 | 等重み（暫定） | 補修記録との照合で較正 |
| β (fatigue weight) | 0.5 | 等重み（暫定） | 同上 |

等重みは暫定設定であり、改善方向として (1) expert elicitation、(2) 補修記録との回帰分析（data-driven）、(3) AEP損失モデルとの接続（physics-informed, cf. [4]）がある。

**w_V/w_TI と α/β の区別**

本パイプラインには2層の重みが存在する。

| Parameter | Layer | Scope | Status |
|---|---|---|---|
| w_V, w_TI | Module B内部 | DELマトリクスにおける風速とTIの相対寄与 | Paper 2で較正済み（MM82: w_V=0.725, w_TI=0.275, R²=0.943） |
| α, β | Module C（統合層） | 画像リスクスコアと疲労リスクスコアの統合重み | 未較正（等重み α=β=0.5） |

w_V/w_TIは同一物理量（風況パラメータ）間の相対重要度であり、OpenFASTシミュレーション結果から回帰的に較正できた。一方、α/βは異種情報（画像 vs 荷重）間の相対重要度であり、較正には補修記録との照合が必要となる。この非対称性が、統合パイプラインの主要な未解決課題である。

### 3.4 Implementation Status

| Component | Status | Script | Notes |
|---|---|---|---|
| Module A: Image scoring | Paper 1で完了 | `phase1_damage_detection/` | DTUデータのみ |
| Module B: DEL estimation | Paper 2で完了 | `phase3_scada/`, `phase5_openfast_shm/` | Penmanshielのみ |
| Module C: Fusion pipeline | I/O仕様検証済み | `phase4_fusion/fusion_pipeline.py` | 合成データで動作確認 |
| α/β calibration | **未着手** | — | 補修記録が必要 |
| Same-turbine validation | **未着手** | — | 同一タービンデータが必要 |

---

## 4. I/O Connection Test (Synthetic Data)

同一タービンのデータが存在しないため、合成データによるI/O接続テストを実施した。Module Aに5タービン × 12ヶ月のランダム生成リスクスコア（seed=42）、Module BにPaper 2の疲労推定ワークフローを模した合成DEL系列（月次変動＋タービン間ノイズ）、Module Cに等重み（α = β = 0.5）を入力し、パイプライン全体の動作を確認した。

**Table 4: Correlation Analysis (Synthetic Data)**

| Metric | Value | Interpretation |
|---|---|---|
| Pearson r | 0.256 | 弱い正の相関（p = 0.048） |
| Spearman r | 0.212 | 弱い正の相関（p = 0.104, 非有意） |

この相関値は**パイプライン動作の確認**であり、予測性能の証拠ではない。Module Aの入力がランダム生成であるため、相関の大きさ自体に意味はない。本テストの意義は「データ形式の整合性」「マージロジックの正常動作」「出力の妥当な範囲」の確認に限定される。

---

## 5. Gap Analysis

### 5.1 What Has Been Achieved

| Component | Achievement | Evidence |
|---|---|---|
| 画像損傷検出 | 自動検出 + スパン方向リスクスコア | Paper 1: mAP@0.5 = 0.58 |
| 疲労荷重推定 | MM82 DELマトリクス + サイト月次DEL | Paper 2: 240 cases, R² = 0.943 |
| I/O仕様 | 統合パイプラインの型実装 + I/O接続テスト | Phase 4: 合成データ動作確認 |
| データ要件 | 真の統合に必要な条件の明確化 | 本論文 §5.3 |

### 5.2 What Remains Unresolved

| Gap | Description | Severity |
|---|---|---|
| **同一タービンデータの不在** | 画像とSCADAが異なるタービン。統合検証が不可能 | **Critical** |
| **α/β重みの根拠不在** | 等重みは暫定。補修記録による較正が必要 | High |
| **LE;CR検出不能** | Paper 1で亀裂が検出不能。統合スコアから亀裂リスクが欠落 | High |
| **chord方向の欠如** | 前縁/後縁の区別なし。エロージョンリスクの精密化に必要 | Medium |
| **月次粒度の粗さ** | 短期イベント（暴風、急激な劣化）を捉えられない | Medium |
| **Cp_max増加の原因不明** | 劣化なしの証拠か、交絡因子か判別不能 | Medium |
| **翼型プロキシの絶対精度** | MM82 DELの絶対値は参考値のみ | Low（相対比較には影響小） |

上記のうち、修士研究における first-order bottleneck は「同一タービンデータの不在」と「α/β重みの根拠不在」の2点である。前者はデータ取得（§6.1）で解消するが、後者は補修記録の質と量に依存し、サンプルサイズが小さい場合には回帰的較正が統計的に不安定になる可能性がある。この2点が解消されない限り、他のギャップ（LE;CR、chord方向等）を改善しても統合スコアの妥当性を主張できない。

### 5.3 Data Requirements for True Integration

同一タービンでの真の統合研究には、以下のデータが最低限必要である:

**Table 6: Required Data for True Integration**

| Data Type | Required Content | Minimum Scale | Priority |
|---|---|---|---|
| **点検画像** | 同一タービンの複数時点のドローン画像、ブレードID付き | 1タービン × 3時点以上 | **必須** |
| **SCADA** | 同一タービンの10分値、風速標準偏差含む | 同期間（≥1年） | **必須** |
| **補修履歴** | 補修箇所、日時、損傷タイプ、補修種別 | 同一タービン | **必須** |
| **気象記録** | サイト近傍の気象データ（風況正規化用） | 同期間 | 推奨 |
| **故障/停止記録** | 計画停止/非計画停止の時刻・原因 | 同期間 | 推奨 |
| **翼型データ** | 対象機種のブレード翼型ポーラー | — | 理想的 |

**最小実行可能な統合研究**:
- 1タービン × 2時点の点検画像 + 同期間のSCADA + 補修履歴
- これだけで「画像スコア変化量 vs 荷重累積量 vs 補修実績」の三角検証が可能

---

## 6. Research Roadmap

### 6.1 Short-Term: Same-Turbine Data Acquisition

**目標**: 同一タービンの点検画像・SCADA・補修履歴を確保する

| Action | Timeline | Feasibility |
|---|---|---|
| 自社O&Mデータへのアクセス交渉 | 0–6ヶ月 | 現職の立場で可能性あり |
| 学術データ共有プログラムの探索 | 0–6ヶ月 | DTU, Strathclyde, ORE Catapult等 |
| 公開データセットの新規リリース監視 | 継続 | Zenodo, OpenFAST community |

### 6.2 Medium-Term: Master's Research Design

**修士テーマ候補**: 「風車ブレードの表面損傷スコアと運転荷重指標を用いた補修優先順位・劣化進行リスク評価」

| Phase | Content | 依存 |
|---|---|---|
| M1 | 同一タービンデータの取得・品質評価 | §6.1の成果 |
| M2 | 画像損傷スコアの定義・算出（Paper 1手法の実機適用） | M1 |
| M3 | DEL/荷重指標の推定（Paper 2手法の実機適用） | M1 |
| M4 | 劣化進行リスクスコアの設計（α/β較正含む） | M2, M3 + 補修記録 |
| M5 | 補修要否・点検優先順位との整合性評価 | M4 |

**最小成功ライン（Minimum Viable Thesis）**

修士研究として成立する最小条件は以下の通りである:

- **データ**: 1タービン × 2時点以上の点検画像 + 同期間SCADA（≥1年）+ 補修履歴
- **検証**: 画像リスクスコアの変化量と荷重累積量の組み合わせが、いずれかの単独指標よりも補修実績（補修の有無または損傷進行度）の説明力が統計的に高いことを示す
- **成果物**: 統合リスクスコアの定義、α/β較正結果、単独指標との比較評価

単独指標で十分に説明できるという結果も、それ自体が有意義な知見である（統合の付加価値の限界を示す）。If only one modality proves sufficient explanatory power, that result still defines a valid boundary condition for the value of integration.

### 6.3 Long-Term: Toward Predictive Degradation Modeling

**博士テーマ候補**: 「風車ブレードの表面損傷・運転荷重履歴・空力応答を統合した劣化進行予測モデルの構築」

修士からの発展として、経年データ（≥3年の同一タービン追跡）の導入による劣化進行速度モデル、空力性能低下（AEP損失）への接続、および因果推論的アプローチの検討が考えられる。

---

## 7. Conclusion

本研究は、風車ブレードの劣化予測に向けて、画像損傷スコア・SCADA疲労荷重指標・空力シミュレーション較正を接続する統合パイプラインのアーキテクチャを設計し、残存ギャップとデータ要件を明確化した。

主な成果:

1. **パイプライン設計**: 3モジュールのI/O仕様を定義し、2層の重みパラメータ（Module B内部のw_V/w_TI、統合層のα/β）の役割を区別した
2. **ギャップの明確化**: 同一タービンデータの不在、α/β重みの根拠不在、LE;CR検出不能を主要な残存課題として特定した
3. **データ要件の整理**: 真の統合研究に必要な最小データセット（1タービン × 2時点画像 + SCADA + 補修履歴）を定義した
4. **研究ロードマップ**: 修士の最小成功ラインを含む段階的発展計画を提示した

本研究は設計論・ギャップ分析であり、統合予測モデルの性能実証は対象外である。同一タービンの点検画像・SCADA・補修履歴が揃った時点で、本設計図に基づく統合検証が初めて可能になる。そのデータ取得が、修士研究の出発点であり、本パイプラインの価値を実証する唯一の条件である。

---

## References

[1] Paper 1: Wind Turbine Blade Surface Damage Detection and Span-wise Risk Scoring Using Drone Inspection Images with Pyramid Patch Augmentation (本研究シリーズ)
[2] Paper 2: Fatigue Load Estimation for Senvion MM82 via NREL 5MW Geometric Scaling and Public SCADA with IEC-Compliant Turbulence Measurement (本研究シリーズ)
[3] Shihavuddin, A.S.M. et al. (2019): Energies, 12(4), 676. DOI: 10.3390/en12040676
[4] Malik, A. & Bak, C. (2025): Wind Energy Science, 10, 227–247. DOI: 10.5194/wes-10-227-2025
[5] Plumley, C. (2022): Penmanshiel Wind Farm Data. Zenodo. DOI: 10.5281/zenodo.5946808
[6] DTU Wind Turbine Inspection Images: Mendeley Data, DOI: 10.17632/hd96prn3nc.2
[7] Tautz-Weinert, J. and Watson, S.J. (2017): IET Renewable Power Generation, 11(4), 382–394
[8] Hayman, G.J. (2012): MLife Theory Manual. NREL
[9] Pandit, R. et al. (2023): SCADA data for wind turbine data-driven condition/performance monitoring: A review on state-of-art, challenges and future trends. Wind Engineering, 47(2), 339–350. DOI: 10.1177/0309524X221124031
[10] Tchakoua, P. et al. (2014): Wind Turbine Condition Monitoring: State-of-the-Art Review, New Trends, and Future Challenges. Energies, 7(4), 2595–2630. DOI: 10.3390/en7042595

---

## 真の統合研究に必要なデータ要件一覧

データ要件の詳細は §5.3 Table 6 を参照。以下に入手可能性の補足を示す。

| Priority | Data Type | 入手可能性 |
|---|---|---|
| **必須** | 点検画像（同一タービン複数時点） | 自社O&Mデータ or 学術データ共有 |
| **必須** | SCADA（10分値、風速σ含む） | 自社 or Zenodo等公開データ |
| **必須** | 補修履歴（箇所、日時、損傷タイプ） | 自社のみ（非公開） |
| 推奨 | 気象記録、故障/停止記録 | 気象庁等公開 / 自社 |
| 理想的 | 翼型データ（ポーラー） | メーカーのみ |

---

## 研究計画書として使える要約

**研究題目**: 風車ブレードの表面損傷スコアと運転荷重指標を用いた劣化進行リスク評価

**研究の背景**: 風車ブレードの劣化予測は、点検画像による損傷状態評価と運転データによる荷重履歴推定を統合する必要があるが、両者を接続する定量的枠組みは確立されていない。

**先行研究（自身の成果）**:
- 公開ドローン画像による損傷検出と部位別リスクスコアリング（Paper 1: mAP@0.5 = 0.58）
- OpenFASTスケーリングと公開SCADAによる疲労荷重推定基盤（Paper 2: MM82 DELマトリクス, Penmanshiel月次DEL）
- 統合パイプラインのアーキテクチャ設計とギャップ分析（本論文）

**研究の問い**: 同一タービンにおける表面損傷スコアと荷重履歴指標を組み合わせることで、ブレード劣化進行リスクを実務に有用な精度で評価できるか。

**方法**: 同一タービンの点検画像・SCADA・補修履歴を用いて、画像損傷スコアの変化量と荷重累積量を補修実績と照合し、統合リスクスコアの妥当性を検証する。

**必要データ**: 1タービン × 2時点以上の点検画像 + 同期間SCADA + 補修履歴

**期待される成果**: 劣化進行リスクの定量的評価手法の提案と、補修優先順位付けへの応用可能性の実証

**今後の発展**: 経年データの拡充による進行速度モデル、空力性能低下（AEP損失）への接続

---

## まだ言えないこと一覧

| # | Statement | Reason |
|---|---|---|
| 1 | **同一タービンで画像・SCADA・補修履歴を統合して予測性能を検証した** | 画像（DTU/Nordtank）とSCADA（Penmanshiel/MM82）は異なるタービン。合成データのみで動作確認 |
| 2 | **劣化進行を定量的に予測できた** | 劣化進行の時系列データが存在しない。cross-sectionalな差異のみ観察（Paper 1 §6 Limitation 6） |
| 3 | **実運用にそのまま導入可能な統合モデルを完成させた** | α/βは等重み（暫定）、LE;CRは検出不能、chord方向なし |
| 4 | **合成データの相関が予測性能を示す** | Module Aがランダム生成。相関はパイプライン動作の確認のみ |
| 5 | **統合重み（α/β）の最適値を決定した** | 補修記録による較正が未実施 |
| 6 | **この枠組みが他機種・他サイトに一般化できる** | 単一データセット（DTU画像 + Penmanshiel SCADA）のみで構築 |
| 7 | **Paper 1とPaper 2の結果を直接組み合わせた定量的結論を出した** | 別タービン・別サイトのため、定量的統合は未達 |

---

## 改訂履歴

| Version | Date | 内容 |
|---|---|---|
| v1.0 | 2026-04-04 | 初稿完了: 全7出力（タイトル案、1文主張、章立て、本文Introduction〜Conclusion、データ要件、研究計画書要約、まだ言えないこと） |
| v2.0 | 2026-04-04 | 設計論・研究計画書寄りに改訂: タイトルをDesign/Roadmap前面化、Abstract設計図価値前面化、§2.1 Module A将来仕様注記、§3.3 w_V/w_TI vs alpha/beta区別、§4→I/O Connection Test・Table 5削除、§6.2最小成功ライン、文献[9][10]追加 |
| v3.0 | 2026-04-04 | 最終調整: 1文主張短縮、§2圧縮、§4 Kaggle SCADA→合成DEL系列に表現調整、§5.2後にfirst-order bottlenecks段落、Conclusion最終文を条件・意義明確化、§1.2/§1.3/§3.3/§5.1の冗長部圧縮（全体約8%） |
