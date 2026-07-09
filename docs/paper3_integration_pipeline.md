# Paper 3: 風車ブレード劣化予測に向けた画像・SCADA・空力シミュレーション統合パイプラインの設計とギャップ分析

**ステータス**: v5.8（v5.7 = Paper 1 案a 連動（test mAP@0.5 = 0.56、3箇所）＋ §7.3 決定論的可視化の将来拡張 → v5.8 = IEC 61400-28/LifeWind 引用追加（§1.1・参考文献 [29]、himinさん承認 2026-07-09。原文に忠実に「二大重点項目の一つ」と較正））
**最終更新**: 2026-07-05

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
2. Related Work
   2.1 Single-Modality Approaches and Their Limits
   2.2 Multi-Modal Fusion and Digital Twin
   2.3 Condition-Based Maintenance Frameworks
   2.4 Summary: Research Gap
3. Component Summary
   3.1 Image-Based Damage Detection and Risk Scoring (Paper 1)
   3.2 Fatigue Load Estimation Framework (Paper 2)
   3.3 Physical Calibration via OpenFAST
4. Integration Pipeline Design
   4.1 Architecture Overview
   4.2 I/O Specification
   4.3 Fusion Logic and Weight Design
   4.4 Implementation Status
5. I/O Connection Test (Synthetic Data)
6. Gap Analysis
   6.1 What Has Been Achieved
   6.2 What Remains Unresolved
   6.3 Data Requirements for True Integration
7. Research Roadmap
   7.1 Short-Term: Same-Turbine Data Acquisition
   7.2 Medium-Term: Master's Research Design
   7.3 Long-Term: Toward Predictive Degradation Modeling
8. Conclusion
References
```

---

## Abstract

風車ブレードの劣化予測には、表面損傷の画像情報、運転荷重履歴、および物理モデルによる較正を統合するアプローチが必要とされている [9][11][12]。しかし、これら複数モダリティの情報を具体的なI/O仕様で接続する設計論は十分に確立されていない [17][19]。本研究では、公開データを用いた先行研究（画像損傷検出: Paper 1、疲労荷重推定基盤: Paper 2）の成果を部品として、3モダリティを接続する統合パイプラインのアーキテクチャとI/O仕様を設計した。

パイプラインは、画像由来のスパン方向リスクスコア、SCADA由来の月次疲労等価荷重（DEL: Damage Equivalent Load）推定値、およびOpenFASTによる重み較正係数を入力とし、タービン別・月別の統合リスクスコアを出力する。合成データによるI/O接続テストでデータフローの整合性を確認したが、これはパイプライン動作の確認であり、予測性能の検証ではない。

画像データ（DTU/Nordtank）とSCADAデータ（Penmanshiel/MM82）は異なるタービン・異なるサイトであり、同一タービン上での統合検証は未達である。本研究の主たる価値は、統合パイプラインの設計図、真の統合に必要なデータ要件の明確化、および修士・博士研究への段階的ロードマップの提示にある。

---

## 1. Introduction

### 1.1 Background and Motivation

風車ブレードは20年以上の運用期間を通じて、エロージョン、亀裂、雷撃損傷等の表面劣化と、繰り返し疲労荷重による構造的劣化を同時に受ける [10][11]。特に前縁エロージョン（LEE: Leading Edge Erosion）は、Mishnaevsky et al. (2021) [26] が指摘するように、気象学・空力・材料科学・計算力学にまたがる multiscale multiphysics プロセスであり、その評価と対策には複数分野の情報統合が本質的に要請される。さらに、Pryor et al. (2022) [28] は北米・欧州 6 地点の長期 disdrometer 観測を整理し、降雨強度（RR）・droplet size distribution（DSD）・雹頻度の地点間変動性と風速との同時分布が LEE 発生条件を支配することを示しており、site-specific な大気観測の重要性が再確認されている。産業側でも、EUDP LifeWind project（Natarajan et al. 2020）[29] が策定中の IEC 61400-28（寿命延長標準）への推奨事項として、ブレード前縁エロージョンを寿命延長期間の点検で特に焦点を当てるべき項目（ボルト締結と並ぶ二大重点項目の一つ）として明示しており、本研究が扱う画像・SCADA・物理モデル統合による劣化評価の産業意義を裏付けている。現行のO&M実務では、定期的なドローン点検やロープアクセス点検による画像評価と、SCADAデータに基づく運転状態監視が独立に行われている [9][13]。しかし、表面損傷の視覚的評価と運転荷重履歴を統合して劣化進行リスクを定量的に評価する枠組みは、まだ確立されていない [11][12]。

### 1.2 Problem: The Integration Gap

劣化予測に必要な3種の情報 ― 画像由来の損傷状態、SCADA由来の荷重履歴、物理モデルによる荷重較正 ― は独立に発展してきた。統合の主要な障壁は:

1. **データの非同一性**: 公開画像データセット（DTU等）と公開SCADAデータセット（Penmanshiel等）は異なるタービン・異なるサイトであり、同一タービンの同時期データは一般に非公開
2. **I/Oの不整合**: 画像検出の出力（バウンディングボックス、クラス、信頼度）とSCADA指標の出力（月次統計量）は粒度・形式が異なる
3. **重みの根拠不在**: 画像スコアと荷重スコアを統合する際の重み（α, β）に、データ駆動の根拠が存在しない

### 1.3 Objective and Scope

本研究の目的は、(1) Paper 1・Paper 2 の成果を接続する統合パイプラインのアーキテクチャとI/O仕様を設計し、(2) 合成データで動作を確認し、(3) 同一タービンでの真の統合研究に必要なデータ要件と残存ギャップを明確化することである。統合予測モデルの性能実証は対象外（予備研究）である。

---

## 2. Related Work

本節では、統合パイプライン設計の背景として、各モダリティの研究動向と統合の現状を整理し、本研究が対処するギャップを特定する。

### 2.1 Single-Modality Approaches and Their Limits

**SCADA**: Tautz-Weinert & Watson (2017) [7] のレビュー以降、SCADAベースの状態監視は急速に発展している。Pandit et al. (2023) [9] はSCADAデータを用いた状態監視・性能監視の最新動向を概観し、Stetco et al. (2019) [13] は機械学習手法を体系的に分類・比較した。Dao et al. (2018) [14] はSCADA信号の組み合わせによるコンポーネント故障診断を実証した。しかし、SCADAデータは10分平均という時間粒度のため故障の二次的影響を捉えるに留まり、機械系・電気系故障の根本原因を直接弁別することは困難であることが指摘されている [9]。

**画像**: Shihavuddin et al. (2019) [3] 以降、ドローン画像×深層学習によるブレード損傷検出は急速に進歩し、Gohar et al. (2025) [15] が最新動向を整理している。Liu et al. (2024) [16] はアテンション機構による軽量検出ネットワークを提案した。しかし、検出結果を運転データと統合してリスク評価に接続する枠組みは提示されていない。

**包括的レビュー**: Tchakoua et al. (2014) [10]、Memari et al. (2024) [11]、García Márquez & Peco Chacón (2020) [12] はいずれも、単一モダリティの限界と複数情報源の統合の必要性を示唆しているが、画像・SCADA・物理モデルを具体的なI/O仕様で接続する設計論は提示していない。

### 2.2 Multi-Modal Fusion and Digital Twin

マルチモーダル融合研究は主にドライブトレインに集中している。Yang et al. (2013) [17] はSCADAの複数パラメータ結合による異常検出を実証し、Castellani et al. (2024) [18] はSCADAとCMS振動データの融合でギアボックス故障を検出した。Maldonado-Correa et al. (2020) [19] はSCADAデータに基づくAIベース状態監視手法を体系的にレビューしつつ、公開データの不足を障壁として指摘した。いずれもブレード劣化に対する画像・SCADA・物理モデルの3モダリティ融合は検討していない。

ブレード LEE に特化した先行研究として、Law & Koutsos (2020) [27] は SCADA 由来の blade tip speed と気象データ由来の rainfall rate を droplet impact 物理（kinetic energy / impact force / water-hammer pressure / average rain erosion stress の 4 種類の Erosion Severity Indicators, ESI 1-4）を介して結合し、18 のオペレーショナル wind farms（UK）における LEE 発症と severity の予測を試みた。ESI は気象・運転情報の 2 モダリティを物理ベースで統合する先行例であり、本研究と方向性を共有する一方、画像由来の損傷状態は組み込まれていない。本パイプラインはこの 2 モダリティに **画像由来の損傷スコア（Module A）** を加えることで、物理ベース予測子と観測された surface damage の cross-validation を可能にする 3 モダリティ統合に拡張する点が、Law & Koutsos のフレームワークと異なる位置にある。

なお、Pryor et al. (2022) [28] は ESI 系手法の入力となる気象観測自体の不確実性を体系的に整理しており、(a) Marshall-Palmer や Best DSD の標準近似が実観測 DSD（特に D > 0.5 mm の大粒径領域）を十分に表現しないこと、(b) RR と hub-height 風速の同時分布が地点間で桁レベルで変動すること、(c) 運動エネルギ評価には ideally 1-min 分解能の DSD/RR サンプリングが必要であることを推奨事項として挙げている。これらは Law & Koutsos の物理ベース ESI を実 wind farm に適用する際の前処理仕様に対する制約条件であり、本パイプラインの将来拡張（気象記録の取り扱い、Module B の入力前処理）における設計指針として位置づけられる。

デジタルツインの領域では、Kandemir et al. (2024) [20] が物理駆動型・データ駆動型・ハイブリッド型を整理し、Branlard et al. (2020) [21] がOpenFASTベースのリアルタイム荷重推定を提示した。Hu et al. (2025) [22] は画像由来の損傷情報をデジタルツインに反映するアプローチを示したが、SCADAとの統合は対象外である。本パイプラインは完全なデジタルツインではなく、その構成要素のI/O仕様と接続設計を整理する予備段階に位置する。

### 2.3 Condition-Based Maintenance Frameworks

CBM/RBIフレームワークは、リスク評価の入力として「状態情報」を必要とする。Nielsen & Sørensen (2011) [23] はベイズ更新による検査計画を、Florian & Sørensen (2017) [24] は疲労損傷と点検コストのトレードオフを、Yeter et al. (2020) [25] はリスク基準保全の枠組みをそれぞれ提案した。しかし、状態情報を複数モダリティから統合する方法論は十分に確立されていない。本パイプラインの統合リスクスコアは、将来的にこれらのCBM/RBI意思決定フレームワークへの入力として機能する可能性がある。

### 2.4 Summary: Research Gap

以上から、以下の3つのギャップが明らかになる:

1. **モダリティ間の分断**: 画像検出、SCADA監視、物理シミュレーションは独立に発展しており、具体的なI/O仕様で接続する設計論が不足している
2. **ブレード特化の融合研究の不在**: マルチモーダル融合研究はドライブトレインに集中しており、ブレード劣化に対する3モダリティ融合は未探索である
3. **設計から検証への橋渡し**: デジタルツインやCBMの枠組みは提示されているが、公開データを用いた段階的構築方法論と、真の統合検証に必要なデータ要件の明確化が欠けている

本研究は、これらのギャップに対し、統合パイプラインのアーキテクチャ設計・I/O仕様定義・残存課題の体系的整理を通じて、予備的な貢献を行う。

---

## 3. Component Summary

### 3.1 Image-Based Damage Detection and Risk Scoring (Paper 1)

Paper 1では、DTU公開画像のアノテーション付き301枚にYOLOv8n＋ピラミッドパッチ拡張を適用し、5損傷クラスの検出（test mAP@0.5 = 0.56）とスパン方向リスクスコア（Tip/Mid/Root）を算出した。既知の制約として、LE;CR検出不能（AP = 0.00）、chord方向除外、重みはpractitioner-informed priorsである（Paper 1 §3.4）。

**出力粒度の注記**: DTU画像は単一サイト（Nordtank）の横断的データであり、turbine_id × monthの時系列粒度を持たない。Table 1の出力スキーマは実機での定期点検データ蓄積後に実現される将来仕様であり、現状は「1時点分」に相当する。

### 3.2 Fatigue Load Estimation Framework (Paper 2)

Paper 2では、NREL 5MWからSenvion MM82への幾何スケーリングとPenmanshiel公開SCADAのIEC準拠TI直接計測を組み合わせ、月次・年次DEL推定基盤を構築した。統合パイプラインへの出力は月次DEL推定値（kN·m）と疲労リスクスコア（0–1正規化）であり、タービンID × 月の粒度を持つ。既知の制約として、MM82翼型プロキシは相対比較のみ有効であり、DLC 1.2単独での推定である（詳細はPaper 2 §5.4）。

### 3.3 Physical Calibration via OpenFAST

Paper 2のDELマトリクス（8V × 5TI）とw_V/w_TI較正（MM82: 0.725/0.275, R² = 0.943）は、Module B内部での風況→DEL変換に物理的根拠を付与する。統合層のα/β較正は補修記録が必要であり未達（§4.3で詳述）。

---

## 4. Integration Pipeline Design

### 4.1 Architecture Overview

> **注記**: 以下のアーキテクチャ図は設計仕様を表す。同一タービンのデータを用いた統合検証は未実施である。
> 正式版図: `docs/fig_paper3_architecture.png`

```
DATA SOURCES                    PIPELINE MODULES                         OUTPUT
─────────────                   ────────────────                         ──────

                        ┌──────────────────────────────────────┐
  Drone inspection  ──▶ │  Module A: Image Risk Scoring        │
  images (per turbine,  │  ● YOLOv8n detection → 5 classes     │
  per inspection date)  │  ● Span-wise scoring (Tip/Mid/Root) │
                        │  ● image_risk_composite output       │
                        │  [STATUS: Implemented — Paper 1]     │
                        └──────────────┬───────────────────────┘
                                       │
                                       │  merge on [turbine_id, month]
                                       │  ※ Requires same-turbine data
                                       │    (INNER JOIN; see §4.2 notes)
                                       │
                        ┌──────────────▼───────────────────────┐
  10-min SCADA      ──▶ │  Module B: SCADA Fatigue Estimation  │
  (wind speed, power,   │  ● DEL matrix interpolation (8V×5TI)│
  TI, timestamps)       │  ● w_V/w_TI calibration (OpenFAST)  │
                        │  ● Monthly DEL + fatigue_risk_score  │
                        │  [STATUS: Implemented — Paper 2]     │
                        └──────────────┬───────────────────────┘
                                       │
                                       │  weighted fusion
                                       │  α × image_risk + β × fatigue_risk
                                       │
                        ┌──────────────▼───────────────────────┐
  Maintenance records ─▶│  Module C: Integration & Risk        │
  (for future α/β       │  ● Linear fusion (α=β=0.5, default) │
  calibration)          │  ● integrated_risk_norm (0–1)        │
                        │  [STATUS: I/O spec verified — this   │
                        │   paper; synthetic data only]        │
                        └──────────────┬───────────────────────┘
                                       │
                                       ▼
                          Physical Calibration Layer
                          ● w_V/w_TI: Paper 2で較正済み
                          ● α/β: 未較正（要: 補修記録）
                          [STATUS: w_V/w_TI calibrated;
                           α/β NOT YET calibrated]
```

**Table 5: Current State vs Target State**

| Component | Current State (2026-04) | Target State (with same-turbine data) | Gap |
|---|---|---|---|
| **Module A** | YOLOv8n trained on DTU/Nordtank images; cross-sectional scores only (1 time point) | Same-turbine multi-temporal scores (turbine_id × month) | Same-turbine inspection images needed |
| **Module B** | DEL matrix for MM82 proxy; Penmanshiel monthly DEL estimated | DEL estimation for the same turbine as Module A | Same-turbine SCADA needed |
| **Module C** | I/O schema defined; synthetic data pipeline test passed | Weighted fusion with calibrated α/β on real data | Maintenance records needed for α/β calibration |
| **Merge point** | Not executed with real data (different turbines in Modules A and B) | Inner join on [turbine_id, month] with matched data | **Critical**: same-turbine data acquisition |
| **Calibration** | w_V/w_TI calibrated (Paper 2); α/β at equal-weight defaults | α/β calibrated via maintenance outcome regression | Maintenance records + sufficient sample size |

### 4.1.1 Design Rationale: Why a Linear Modular Pipeline?

本パイプラインは、Module A → B → C の線形モジュール構成と決定レベル融合（decision-level fusion）を採用している。この設計選択の根拠を以下に述べる。

代替案として、(1) 早期融合（early fusion: 画像特徴量とSCADA特徴量を連結して単一モデルに入力）、(2) エンドツーエンド深層学習（画像とSCADAを同時に入力するマルチモーダルネットワーク）が考えられる。しかし、本研究では以下の理由からモジュール型の線形パイプラインを選択した。第一に、**O&M実務者にとっての解釈可能性**: 各モジュールの中間出力（画像リスクスコア、疲労リスクスコア）が個別に解釈可能であることは、風車技術者による結果の検証と信頼性判断に不可欠である。第二に、**段階的開発のためのモジュール性**: 画像データのみが利用可能な場合はModule A単独で、SCADAデータのみの場合はModule B単独で動作する縮退モード（degraded mode）が可能である。第三に、**公開データの制約への適応**: 現状では画像とSCADAが異なるタービンであり、各モジュールを独立に開発・検証してからI/O仕様で接続する方が、段階的な研究進展に適している。将来、同一タービンの大規模データが利用可能になった段階で、特徴量レベル融合やエンドツーエンド手法との性能比較が研究課題となる [17][19]。

### 4.2 I/O Specification

**Table 1: Module A Output Schema**

| Column | Type | Source | Description |
|---|---|---|---|
| turbine_id | str | Inspection record | タービン識別子 |
| month | int | Inspection date | 月（1–12）†1 |
| tip_score | float | Paper 1 §3.4 | Tip領域リスクスコア |
| mid_score | float | Paper 1 §3.4 | Mid領域リスクスコア |
| root_score | float | Paper 1 §3.4 | Root領域リスクスコア |
| image_risk_composite | float | 加重和 | (tip×3 + mid×2 + root×1) / 6 †2 |

> †1 **将来仕様**: 現状のPaper 1はDTU横断的画像データから単一時点のスコアのみを生成する。`month`カラムによる月次時系列は、同一タービンに対する定期点検データの蓄積後に実現される将来仕様である。
>
> †2 **重み根拠**: Tip:Mid:Root = 3:2:1 の重みはpractitioner-informed priors（Paper 1 §3.4）に基づく。エロージョンの進行速度がTip側で大きいという実務的知見を反映しているが、データ駆動の較正は未実施である。

**Table 2: Module B Output Schema**

| Column | Type | Source | Description |
|---|---|---|---|
| turbine_id | str | SCADA record | タービン識別子 |
| month | int | SCADA timestamp | 月（1–12） |
| DEL_est_kNm | float | Paper 2 §3.7 | 月次DEL推定値（kN·m） |
| fatigue_risk_score | float | 0–1正規化 | DELの全タービン横断正規化 †3 |

> †3 **正規化方法**: `fatigue_risk_score` はmin-max正規化を採用する（全タービン・全月の DEL_est_kNm の最小値を0、最大値を1にスケーリング）。この正規化は同一サイト内のタービン間相対比較を前提としており、異なるサイト間での比較にはサイト固有のスケーリングファクターが必要となる。パーセンタイル正規化やZスコア正規化は将来の代替案として検討対象である。

**Table 3: Module C Output Schema**

| Column | Type | Description |
|---|---|---|
| turbine_id | str | タービン識別子 |
| month | int | 月（1–12） |
| integrated_risk | float | α × image_risk + β × fatigue_risk |
| integrated_risk_norm | float | 0–1正規化済み統合リスク |

**マージ仕様**: Module AとModule Bの結合はinner joinを使用する（結合キー: `[turbine_id, month]`）。inner joinの選択により、画像データまたはSCADAデータの一方が欠損している月は出力から除外される。これは、統合リスクスコアが両モダリティの情報を反映することを保証するための設計判断である。画像データのみ、またはSCADAデータのみが利用可能な月に対しては、Module A単独スコアまたはModule B単独スコアを参考値として出力する縮退モード（degraded mode）を将来的に実装予定である。欠損月のimputationは現時点では行わない（欠損パターンが実データで把握されるまでimputation戦略の選択は保留する）。

### 4.3 Fusion Logic and Weight Design

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

### 4.4 Implementation Status

| Component | Status | Script | Notes |
|---|---|---|---|
| Module A: Image scoring | Paper 1で完了 | `phase1_damage_detection/` | DTUデータのみ |
| Module B: DEL estimation | Paper 2で完了 | `phase3_scada/`, `phase5_openfast_shm/` | Penmanshielのみ |
| Module C: Fusion pipeline | I/O仕様検証済み | `phase4_fusion/fusion_pipeline.py` | 合成データで動作確認 |
| α/β calibration | **未着手** | — | 補修記録が必要 |
| Same-turbine validation | **未着手** | — | 同一タービンデータが必要 |

---

## 5. I/O Connection Test (Synthetic Data)

同一タービンのデータが存在しないため、合成データによるI/O接続テストを実施した。Module Aに5タービン × 12ヶ月のランダム生成リスクスコア（seed=42）、Module BにPaper 2の疲労推定ワークフローを模した合成DEL系列（月次変動＋タービン間ノイズ）、Module Cに等重み（α = β = 0.5）を入力し、パイプライン全体のデータフロー整合性を確認した。

**Table 4: Pipeline Integration Test Results (Synthetic Data)**

| Test Item | Result | Pass/Fail |
|---|---|---|
| **型整合性**: Module A出力 → Module C入力の型一致 | 全カラムの型が仕様通り（str, int, float） | Pass |
| **マージ正常動作**: inner join on [turbine_id, month] | 60行入力 → 60行出力（行数保存） | Pass |
| **NULL処理**: マージ後の欠損値 | 欠損値なし（合成データのため） | Pass |
| **出力範囲**: integrated_risk_norm の値域 | [0, 1] 範囲内（min=0.12, max=0.89） | Pass |
| **重み反映**: α=β=0.5 でのfusion計算 | image_risk × 0.5 + fatigue_risk × 0.5 と一致 | Pass |

> **補足**: 合成データに対してPearson r = 0.256、Spearman r = 0.212が観察されたが、Module Aの入力がランダム生成であるため、これらの相関値は統計的に意味を持たない。数値はパイプラインが計算を正常に実行したことの副次的確認にすぎず、予測性能や変数間関係の証拠ではない。

本テストの意義は「I/Oスキーマの整合性」「マージロジックの正常動作」「出力の妥当な範囲」の確認に限定される。実データによる統合検証は、同一タービンのデータ取得後に初めて可能となる。

---

## 6. Gap Analysis

### 6.1 What Has Been Achieved

| Component | Achievement | Evidence |
|---|---|---|
| 画像損傷検出 | 自動検出 + スパン方向リスクスコア | Paper 1: test mAP@0.5 = 0.56 |
| 疲労荷重推定 | MM82 DELマトリクス + サイト月次DEL | Paper 2: 240 MM82 cases, R² = 0.943 |
| I/O仕様 | 統合パイプラインのI/O仕様定義 + 合成データによるパイプライン接続テスト | Phase 4: 合成データでのデータフロー整合性確認 |
| データ要件 | 真の統合に必要な条件の明確化 | 本論文 §6.3 |

### 6.2 What Remains Unresolved

| Gap | Description | Severity |
|---|---|---|
| **同一タービンデータの不在** | 画像とSCADAが異なるタービン。統合検証が不可能 | **Critical** |
| **α/β重みの根拠不在** | 等重みは暫定。補修記録による較正が必要 | High |
| **LE;CR検出不能** | Paper 1で亀裂が検出不能。統合スコアから亀裂リスクが欠落 | High |
| **chord方向の欠如** | 前縁/後縁の区別なし。エロージョンリスクの精密化に必要 | Medium |
| **月次粒度の粗さ** | 短期イベント（暴風、急激な劣化）を捉えられない | Medium |
| **Cp_max増加の原因不明** | 劣化なしの証拠か、交絡因子か判別不能 | Medium |
| **翼型プロキシの絶対精度** | MM82 DELの絶対値は参考値のみ | Low（相対比較には影響小） |

**ギャップ間の依存関係**: 上記のギャップは独立ではなく、以下の依存構造を持つ。

- 「同一タービンデータの不在」は他のすべてのギャップの前提条件（root dependency）である。データ取得なしにα/β較正もLE;CR検出の実機検証も不可能
- 「α/β重みの根拠不在」は「同一タービンデータ」+「補修記録」に依存する（sequential dependency）
- 「LE;CR検出不能」と「chord方向の欠如」は互いに独立であり、それぞれ画像データ・モデル改善で並行して対処可能（independent）
- 「月次粒度の粗さ」は同一タービンデータの取得により部分的に解消される可能性がある（SCADAの10分値は既に利用可能であり、画像の頻度が月次以上になれば粒度が改善する）が、短期イベントの画像捕捉には別途対策が必要
- 「Cp_max増加の原因不明」と「翼型プロキシの絶対精度」は、同一タービンデータの取得とは独立に、追加分析（気象記録照合、翼型データ入手）で対処する性質の課題である

上記のうち、修士研究における first-order bottleneck は「同一タービンデータの不在」と「α/β重みの根拠不在」の2点である。前者はデータ取得（§7.1）で解消するが、後者は補修記録の質と量に依存し、サンプルサイズが小さい場合には回帰的較正が統計的に不安定になる可能性がある。この2点が解消されない限り、他のギャップ（LE;CR、chord方向等）を改善しても統合スコアの妥当性を主張できない。

### 6.3 Data Requirements for True Integration

同一タービンでの真の統合研究には、以下のデータが最低限必要である:

**Table 6: Required Data for True Integration**

| Data Type | Required Content | Minimum Scale | Priority |
|---|---|---|---|
| **点検画像** | 同一タービンの複数時点のドローン画像、ブレードID付き | 1タービン × 3時点以上 | **必須** |
| **SCADA** | 同一タービンの10分値、風速標準偏差含む | 同期間（≥1年） | **必須** |
| **補修履歴** | 補修箇所、日時、損傷タイプ、補修種別 | 同一タービン | **必須** |
| **気象記録** | サイト近傍の気象データ（風況正規化用、DSD/RR 情報があれば望ましい [28]） | 同期間（≥1年） | 推奨（LEE 主軸の研究では準必須） |
| **故障/停止記録** | 計画停止/非計画停止の時刻・原因 | 同期間 | 推奨 |
| **翼型データ** | 対象機種のブレード翼型ポーラー | — | 理想的 |

**最小実行可能な統合研究**:
- 1タービン × 2時点の点検画像 + 同期間のSCADA + 補修履歴
- これだけで「画像スコア変化量 vs 荷重累積量 vs 補修実績」の三角検証が可能

---

## 7. Research Roadmap

### 7.1 Short-Term: Same-Turbine Data Acquisition

**目標**: 同一タービンの点検画像・SCADA・補修履歴を確保する

| Action | Timeline | Feasibility |
|---|---|---|
| 自社O&Mデータへのアクセス交渉 | 0–6ヶ月 | 現職の立場で可能性あり |
| 学術データ共有プログラムの探索 | 0–6ヶ月 | DTU, Strathclyde, ORE Catapult等 |
| 公開データセットの新規リリース監視 | 継続 | Zenodo, OpenFAST community |

### 7.1.1 Gap Resolution Priority After Data Acquisition

同一タービンデータ取得（first-order bottleneck解消）後の残存ギャップに対する推奨解決順序:

1. **α/β較正**（最優先）: 補修記録との回帰分析による統合重みの較正。これなしに統合スコアの妥当性は主張不可。M4フェーズに対応
2. **LE;CR検出改善**（高優先）: focal loss、minority oversampling、または追加データによる亀裂検出能力の獲得。α/β較正と並行して実施可能
3. **chord方向の追加**（中優先）: LE/TE弁別の実現。LE;CR改善と並行可能だが、画像品質とブレード形状への依存が大きく、データ取得後に実現可能性を再評価する
4. **月次粒度の改善**（低優先）: 点検頻度の増加またはイベント駆動型点検との組み合わせ。α/β較正の結果、月次粒度で十分な説明力が得られるかにより必要性が変わる
5. **Cp_max原因特定・翼型精度向上**（低優先）: 気象記録照合、翼型データ入手。独立に進行可能だが、本パイプラインの統合スコア改善への直接的寄与は限定的

### 7.2 Medium-Term: Master's Research Design

**修士テーマ候補**: 「風車ブレードの表面損傷スコアと運転荷重指標を用いた補修優先順位・劣化進行リスク評価」

| Phase | Content | 依存 |
|---|---|---|
| M1 | 同一タービンデータの取得・品質評価 | §7.1の成果 |
| M2 | 画像損傷スコアの定義・算出（Paper 1手法の実機適用） | M1 |
| M3 | DEL/荷重指標の推定（Paper 2手法の実機適用） | M1 |
| M4 | 劣化進行リスクスコアの設計（α/β較正含む） | M2, M3 + 補修記録 |
| M5 | 補修要否・点検優先順位との整合性評価 | M4 |

**最小成功ライン（Minimum Viable Thesis）**

修士研究として成立する最小条件は以下の通りである:

- **データ**: 1タービン × 2時点以上の点検画像 + 同期間SCADA（≥1年）+ 補修履歴
- **検証**: 画像リスクスコアの変化量と荷重累積量の組み合わせが、いずれかの単独指標よりも補修実績（補修の有無または損傷進行度）の説明力が統計的に高いことを示す
- **成果物**: 統合リスクスコアの定義、α/β較正結果、単独指標との比較評価

単独指標で十分に説明できるという結果も、それ自体が有意義な知見である。統合が単独指標を上回らない場合、その結果は統合の付加価値の限界を画定する境界条件として意味を持つ。

### 7.3 Long-Term: Toward Predictive Degradation Modeling

**博士テーマ候補**: 「風車ブレードの表面損傷・運転荷重履歴・空力応答を統合した劣化進行予測モデルの構築」

修士からの発展として、経年データ（≥3年の同一タービン追跡）の導入による劣化進行速度モデル、空力性能低下（AEP損失）への接続、および因果推論的アプローチの検討が考えられる。

将来の点検体制として、2Dスクリーニング（フリート全体の損傷候補抽出）→ 3D精密検査（候補ブレードの損傷定量化）の2段階構造が想定される。この構造では、2D検出のRecall（見逃し率）が劣化予測パイプライン全体のボトルネックとなる——2D段階で見逃された損傷は3D精密検査にも劣化予測モデルにも到達しない。本パイプラインのModule Aは、この2段階構造の第1段階として位置づけられ、Recall向上が最優先の改善課題となる。3D精密検査で得られる損傷の面積・深さ・体積は、Module Cの統合リスクスコアの精度を大幅に向上させる可能性があるが、フリート規模での3Dデータ管理コストとの兼ね合いが実用上の制約となる。

また、現場技術者への伝達手段として、パイプラインの予測出力（部位別リスクスコア・劣化進行予測）を汎用ブレードの3Dモデルまたは模式図上に描画する可視化レイヤーが将来拡張として考えられる。描画内容がすべてモデル出力に対応する決定論的可視化を基本とする。生成AIによる写実的な損傷画像の生成は、物理的裏付けのない細部まで描き予測確度以上の説得力を与えるリスクがあるため、意思決定用途には採用しない。

---

## 8. Conclusion

本研究は、風車ブレードの劣化予測に向けて、画像損傷スコア・SCADA疲労荷重指標・空力シミュレーション較正を接続する統合パイプラインのアーキテクチャを設計し、残存ギャップとデータ要件を明確化した。

主な成果:

1. **パイプライン設計**: 3モジュールのI/O仕様を定義し、2層の重みパラメータの役割を区別した。Module B内部のw_V/w_TIはPaper 2においてOpenFASTシミュレーションから較正済み（MM82: w_V=0.725, w_TI=0.275）であるのに対し、統合層のα/βは等重みデフォルト（α=β=0.5）のまま未較正である
2. **ギャップの明確化**: 同一タービンデータの不在、α/β重みの根拠不在、LE;CR検出不能を主要な残存課題として特定した
3. **データ要件の整理**: 真の統合研究に必要な最小データセット（1タービン × 2時点画像 + SCADA + 補修履歴）を定義した
4. **研究ロードマップ**: 修士の最小成功ラインを含む段階的発展計画を提示した

本研究は設計論・ギャップ分析であり、統合予測モデルの性能実証は対象外である。同一タービンの点検画像・SCADA・補修履歴が揃った時点で、本設計図に基づく統合検証が初めて可能になる。そのデータ取得が、修士研究の出発点であり、本パイプラインの価値を実証する唯一の条件である。

---

## References

[1] Paper 1: Wind Turbine Blade Surface Damage Detection and Span-wise Risk Scoring Using Drone Inspection Images with Pyramid Patch Augmentation (本研究シリーズ)
[2] Paper 2: Site-Specific Blade Fatigue Load Estimation via Reference Turbine Scaling and Public SCADA: A Penmanshiel Case Study (本研究シリーズ)
[3] Shihavuddin, A.S.M. et al. (2019): Wind turbine surface damage detection by deep learning aided drone inspection analysis. Energies, 12(4), 676. DOI: 10.3390/en12040676
[4] Malik, T.H. and Bak, C. (2025): Challenges in detecting wind turbine power loss: the effects of blade erosion, turbulence, and time averaging. Wind Energy Science, 10, 227–243. DOI: 10.5194/wes-10-227-2025
[5] Plumley, C. (2022): Penmanshiel Wind Farm Data. Zenodo. DOI: 10.5281/zenodo.5946808
[6] DTU Wind Turbine Inspection Images. Mendeley Data. DOI: 10.17632/hd96prn3nc.2
[7] Tautz-Weinert, J. and Watson, S.J. (2017): Using SCADA data for wind turbine condition monitoring — a review. IET Renewable Power Generation, 11(4), 382–394. DOI: 10.1049/iet-rpg.2016.0248
[8] Hayman, G.J. (2012): MLife Theory Manual. NREL.
[9] Pandit, R. et al. (2023): SCADA data for wind turbine data-driven condition/performance monitoring: A review on state-of-art, challenges and future trends. Wind Engineering, 47(2), 422–441. DOI: 10.1177/0309524X221124031
[10] Tchakoua, P. et al. (2014): Wind Turbine Condition Monitoring: State-of-the-Art Review, New Trends, and Future Challenges. Energies, 7(4), 2595–2630. DOI: 10.3390/en7042595
[11] Memari, M. et al. (2024): Review on the advancements in wind turbine blade inspection: Integrating drone and deep learning technologies for enhanced defect detection. IEEE Access, 12, 33236–33282. DOI: 10.1109/ACCESS.2024.3371493
[12] García Márquez, F.P. and Peco Chacón, A.M. (2020): A review of non-destructive testing on wind turbines blades. Renewable Energy, 161, 998–1010. DOI: 10.1016/j.renene.2020.07.145
[13] Stetco, A. et al. (2019): Machine learning methods for wind turbine condition monitoring: A review. Renewable Energy, 133, 620–635. DOI: 10.1016/j.renene.2018.10.047
[14] Dao, P.B. et al. (2018): Condition monitoring and fault detection in wind turbines based on cointegration analysis of SCADA data. Renewable Energy, 116, 107–122. DOI: 10.1016/j.renene.2017.06.089
[15] Gohar, I. et al. (2025): Review of state-of-the-art surface defect detection on wind turbine blades through aerial imagery: Challenges and recommendations. Engineering Applications of Artificial Intelligence, 144, 109970. DOI: 10.1016/j.engappai.2024.109970
[16] Liu, Y.-H. et al. (2024): Defect detection of the surface of wind turbine blades combining attention mechanism. Advanced Engineering Informatics, 59, 102292. DOI: 10.1016/j.aei.2023.102292
[17] Yang, W. et al. (2013): Wind turbine condition monitoring by the approach of SCADA data analysis. Renewable Energy, 53, 365–376. DOI: 10.1016/j.renene.2012.11.030
[18] Castellani, F. et al. (2024): Wind turbine gearbox condition monitoring through the sequential analysis of industrial SCADA and vibration data. Energy Reports, 12, 750–761. DOI: 10.1016/j.egyr.2024.06.041
[19] Maldonado-Correa, J. et al. (2020): Using SCADA data for wind turbine condition monitoring: A systematic literature review. Energies, 13(12), 3132. DOI: 10.3390/en13123132
[20] Kandemir, E. et al. (2024): Predictive digital twin for wind energy systems: A literature review. Energy Informatics, 7, 68. DOI: 10.1186/s42162-024-00373-9
[21] Branlard, E. et al. (2020): A digital twin based on OpenFAST linearizations for real-time load and fatigue estimation of land-based turbines. Journal of Physics: Conference Series, 1618, 022030. DOI: 10.1088/1742-6596/1618/2/022030
[22] Hu, W. et al. (2025): Digital twin of wind turbine surface damage detection based on deep learning-aided drone inspection. Renewable Energy, 241, 122332. DOI: 10.1016/j.renene.2024.122332
[23] Nielsen, J.S. and Sørensen, J.D. (2011): On risk-based operation and maintenance of offshore wind turbine components. Reliability Engineering & System Safety, 96(1), 218–229. DOI: 10.1016/j.ress.2010.07.007
[24] Florian, M. and Sørensen, J.D. (2017): Risk-based planning of operation and maintenance for offshore wind farms. Energy Procedia, 137, 261–272. DOI: 10.1016/j.egypro.2017.10.349
[25] Yeter, B. et al. (2020): Risk-based maintenance planning of offshore wind turbine farms. Reliability Engineering & System Safety, 202, 107062. DOI: 10.1016/j.ress.2020.107062
[26] Mishnaevsky Jr., L. et al. (2021): Leading edge erosion of wind turbine blades: Understanding, prevention and protection. Renewable Energy, 169, 953–969. DOI: 10.1016/j.renene.2021.01.044
[27] Law, H. and Koutsos, V. (2020): Leading edge erosion of wind turbines: Effect of solid airborne particles and rain on operational wind farms. Wind Energy, 23(10), 1955–1965. DOI: 10.1002/we.2540
[28] Pryor, S.C.; Barthelmie, R.J.; Cadence, J.; Dellwik, E.; Hasager, C.B.; Kral, S.T.; Reuder, J.; Rodgers, M.; Veraart, M. (2022): Atmospheric Drivers of Wind Turbine Blade Leading Edge Erosion: Review and Recommendations for Future Research. Energies, 15(22), 8553. DOI: 10.3390/en15228553
[29] Natarajan, A.; Dimitrov, N.K.; William Peter, D.R.; Bergami, L.; Madsen, J.; Olesen, N. et al. (2020): Demonstration of Requirements for Life Extension of Wind Turbines Beyond Their Design Life (LifeWind). DTU Wind Energy Report No. E-0196, EUDP Project no. 64017-05114.

---

## 真の統合研究に必要なデータ要件一覧

データ要件の詳細は §6.3 Table 6 を参照。以下に入手可能性の補足を示す。

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
- 公開ドローン画像による損傷検出と部位別リスクスコアリング（Paper 1: test mAP@0.5 = 0.56）
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
| v4.0 | 2026-04-08 | 構造改訂: §2 Related Work新設（7小節、文献[11]–[25]追加で計25件）、§4.1アーキテクチャ図を改善（実装ステータス・マージ条件・注記追加）、Table 5 Current State vs Target State追加、§4.1.1設計根拠（なぜ線形パイプラインか）追加、Table 4をPipeline Integration Test Resultsとして再構成、Table 1/2に脚注追加（将来仕様・重み根拠・正規化方法）、マージ仕様（inner join・欠損月処理）明記、§6.1「型実装」→「I/O仕様定義」に修正、§8 Conclusion item 1でw_V/w_TIとα/βの較正ステータスを明確化、全§番号を新構造に合わせて更新 |
| v5.0 | 2026-04-10 | §2 Related Work圧縮（7小節→4小節、文献25件は維持、記述を約60%圧縮）。§7.2の英日混在文を日本語に統一 |
| v5.1 | 2026-04-26 | 参考文献検証による軽微修正：[21] Branlard 2020 のタイトル「real-time load estimation」→「real-time load and fatigue estimation」に修正（実物の正式タイトルから "and fatigue" が脱落していた。Branlard 2020 全12頁主張駆動精読で発見、本文§2.4 line 102 の主張記述は完全整合のため修正不要） |
| v5.2 | 2026-04-27 | 参考文献検証による軽微修正：§2.1 line 92 の Pandit 2023 [9] と Stetco 2019 [13] の引用文脈ハルシネーションを修正。Pandit 2023 全20頁主張駆動精読で発見：(a) 「正常挙動モデリング・異常検知・残余寿命推定の3段階を整理」という記述は Pandit 2023 本文に存在しない（実際は Regression vs Classification の2分類が主軸）→「SCADAデータを用いた状態監視・性能監視の最新動向を概観」に修正。(b) 「ブレード損傷 vs 機械的摩耗 vs 電気系統の弁別困難」のうち「ブレード損傷」は Pandit 2023 p.430 の「pitch等のSCADA検出可能」記述と矛盾→「機械系・電気系故障の根本原因の直接弁別困難」に修正。(c) 共通限界の引用 [9][13] のうち Stetco 2019 [13] には対応する明示記述がないため [9] のみに変更。Pandit 2023 p.428 の「SCADA targets secondary effects」「10 minutes averaging time」記述に整合する表現に書き換え。Stetco 2019 全16頁精読も完了（書誌情報・「機械学習手法の体系的比較」帰属は完全整合・修正不要）。García Márquez 2020 全28頁完全精読完了（line 96 の3主張すべて完全整合・修正不要） |
| v5.3 | 2026-04-27 | 参考文献検証による軽微修正：§2.2 line 100 の Maldonado-Correa et al. (2020) [19] の引用表現を精緻化。Maldonado-Correa 2020 全20頁主張駆動精読で発見：本論文の主旨は「SCADA + AI による Condition Monitoring の Systematic Literature Review」であり、Fig. 4 の Conceptual Mind Map で parametric modelling と intrusive monitoring techniques は exclusion として明示的に除外されている。本文中で「fusion」「data fusion」という用語は単一引用 [43] のみで、「fusion methods」を独立カテゴリにしたレビューではない。「データ融合手法を整理しつつ」→「SCADAデータに基づくAIベース状態監視手法を体系的にレビューしつつ」に修正（「公開データの不足を障壁として指摘した」部分は Abstract・§3.1・§4 で完全整合のため維持）。Tchakoua 2014 全36頁・Castellani 2024 全12頁・Kandemir 2024 全36頁の主張駆動精読も完了（いずれも完全整合・修正不要） |
| v5.4 | 2026-06-12 | Mishnaevsky 2021 / Law & Koutsos 2020 の主張駆動全頁精読（A9 + A11a）による §1.1 と §2.2 の補強: (1) §1.1 Background and Motivation に Mishnaevsky 2021 [26] の multiscale multiphysics 性質に関する一文を追加（複数分野統合の本質的要請を示し、本研究の整合性を裏付け）。(2) §2.2 Multi-Modal Fusion に Law & Koutsos 2020 [27] の **ESI 1-4**（kinetic energy / impact force / water-hammer pressure / average rain erosion stress）に関するパラグラフを追加。Law の枠組みは SCADA (blade tip speed) + 気象（rainfall rate）の 2 モダリティを物理ベースで結合する直接の先行例であり、本研究は **画像由来の損傷スコア（Module A）を加えた 3 モダリティ統合への拡張** として位置づけを明確化（Paper 3 の独自性の論述強化）。(3) 参考文献 [26] Mishnaevsky 2021 と [27] Law & Koutsos 2020 を追加。引用根拠の詳細は `tools/reference_audit/A9_mishnaevsky_2021_full_reading_2026-06-11.md` と `tools/reference_audit/A11a_law_koutsos_2020_full_reading_2026-06-12.md` |
| v5.6 | 2026-07-02 | Paper 1 v9.6 の実データ照合による数値訂正を反映: §3.1 の「DTU公開画像559枚」→「DTU公開画像のアノテーション付き301枚」。559 は訓練 bbox アノテーション数の誤転記だったことが Paper 1 側の実データ照合（yolo_dataset・COCO JSON）で確定（詳細は `tools/reference_audit/paper123_consistency_audit_2026-07-02.md`）。mAP@0.5 = 0.58 の表記は Paper 1 側の提示方法決定（val 最良 0.581 vs test 0.561）待ちで現状維持 |
| v5.7 | 2026-07-05 | (1) Paper 1 v9.7 の mAP 提示方法 案a（test 主指標化、himinさん 決定 2026-07-05）に連動し、§3.1・§6.1（表）・§8 の「mAP@0.5 = 0.58」3箇所を「test mAP@0.5 = 0.56」に修正。(2) §7.3 末尾に可視化レイヤーの将来拡張を追記：予測出力を汎用ブレード3Dモデル/模式図に描画する**決定論的可視化を基本**とし、生成AIによる写実的損傷画像の生成は予測確度以上の説得力を与えるリスクから意思決定用途に採用しない方針を明記（himinさん 決定 2026-07-05：形態A基本。新規文献引用は実物精読ルールに従い追加せず） |
| v5.5 | 2026-06-13 | Pryor et al. 2022 [28] の主張駆動全 41p 精読（A11d）による §1.1・§2.2・§6.3 の補強: (1) §1.1 Background and Motivation に Pryor 2022 [28] の北米・欧州 6 地点 disdrometer 観測レビューの結果（DSD/RR/雹頻度の地点間変動性と風速 joint 分布が LEE 発生条件を支配）を追加し、site-specific な大気観測の重要性を明示。(2) §2.2 Multi-Modal Fusion で Law & Koutsos 段落の直後に Pryor 2022 の核心的推奨事項（Marshall-Palmer/Best DSD の不十分性、地点間変動性、1-min 分解能の必要性）をパラグラフ追加し、ESI 系手法を実 wind farm に適用する際の前処理仕様への制約条件として位置づけ（Module B 入力前処理の将来拡張の設計指針として）。(3) §6.3 Table 6 で気象記録の Priority を「推奨」から「推奨（LEE 主軸の研究では準必須）」に格上げし、DSD/RR 情報があれば望ましい旨を [28] と共に追記。(4) 参考文献 [28] Pryor et al. 2022 を追加。引用根拠の詳細は `tools/reference_audit/A11d_pryor_2022_full_reading_2026-06-13.md`。Paper 3 の主軸（画像 + SCADA + 物理較正）を歪めないよう、引用は最小限・限定的位置に留めた |
