# 研究ロードマップ

最終更新: 2026-03-31

---

## 最終目標

風車ブレードの劣化進行予測モデルを構築し、O&M意思決定支援へ接続する。

現場（ロープアクセス点検）・メーカー・発電事業者の3視点を持つ経験を研究に転化する。
単なる学位取得ではなく、分析・研究・意思決定支援に強い人材になることが目的。

---

## 研究の基本方針

- 最終目標は大きいが、短期では部分問題を切り出して1本ずつ完走する
- 公開データでできる範囲をまず固める
- 各ステップで GitHub・レポート・ノート・図表など、成果物を残す
- 必ず「この作業は最終目標のどの部品か」を明示する
- 画像分類1本で満足せず、進行・時系列・統合へ接続する
- Kaggleは入口・練習・補助として使ってよいが、一次ソースが存在する場合は一次ソースを優先する

---

## フェーズ構成

### Phase 0：研究基盤整備（全フェーズ共通）

**目的**
- 研究環境を整える
- 何を積み上げるかを明確にする
- 再現性のための記録体制を作る

**主な作業**
- GitHubリポジトリ構成
- OpenOA・OpenFASTの概要把握
- データ辞書テンプレ作成
- 実験ログテンプレ作成

**一次ソース**

| 名称 | URL |
|---|---|
| OpenOA Documentation | https://openoa.readthedocs.io/ |
| OpenOA JOSS Paper | https://www.theoj.org/joss-papers/joss.02171/10.21105.joss.02171.pdf |
| OpenFAST Documentation | https://openfast.readthedocs.io/ |
| OpenFAST GitHub | https://github.com/OpenFAST/openfast |

**位置づけ**：研究練習用ではなく、全フェーズ共通の基盤整備。再現性のため必須。

---

### Phase 1：画像ベースの基礎研究（最初の完走テーマ）

**候補テーマ**
「公開ドローン点検画像を用いた風車ブレード表面損傷の部位別リスクスコアリング」

**目的**
1. DTU公開ドローン点検画像から損傷領域を検出する
2. 部位（Leading Edge / Trailing Edge / 翼根 / 翼端）ごとに損傷重篤度スコアを算出する
3. スコアを可視化・比較可能な形で出力する

**最終目標との接続**
→ 「画像由来の損傷状態定量化」という部品。統合モデルの入力になる。

**手法**
1. データ辞書作成（部位定義・損傷カテゴリ定義）
2. アノテーション確認・変換（YOLO形式）
3. YOLOv8による損傷検出
4. 部位ラベルとのマッピング
5. 部位別損傷面積・信頼度からリスクスコア算出（加重和方式）
6. スコアの可視化（ブレード展開図への投影）

**評価方法**
- 検出精度：mAP@0.5、mAP@0.5:0.95
- Energies 2019論文との手法比較

**成果物**
- 学習済みモデル（weights）
- 部位別リスクスコア出力ノートブック
- 結果レポート（PDF）

**データ（優先順位順）**

| 優先順位 | 名称 | 種別 | URL |
|---|---|---|---|
| 1 | DTU Wind Turbine Inspection Images | 一次 | https://data.mendeley.com/datasets/hd96prn3nc |
| 2 | YOLO Annotated Mendeley | 二次（原典: DTU） | https://data.mendeley.com/datasets/t6fwpc735s |
| 3 | Kaggle mirror | 二次（原典: DTU） | https://www.kaggle.com/datasets/ajifoster3/yolo-annotated-wind-turbines-586x371 |

**参考論文**
- Energies 2019: Wind Turbine Surface Damage Detection by Deep Learning
  https://www.mdpi.com/1996-1073/12/4/676

**注意点**
- 同一風車・同一ブレード由来画像の分割方法を明示する（データリーク防止）
- 単なる画像分類大会にしない。部位別リスクスコアまで進める

**位置づけ**：最初の完走テーマ。研究練習と本命テーマの両方を兼ねる。

---

### Phase 2：時点差・損傷進行の扱い

**候補テーマ**
「時点差画像を用いた風車ブレード損傷進行スコアの試作」

**目的**
- 静的な損傷検出から、劣化進行の方向へ一歩進む
- 擬似ラベルと差分特徴量の考え方を習得する

**最終目標との接続**
→ 「時間変化の扱い」という部品。

**データ**
- DTU原データの2017年・2018年時点差画像
  https://data.mendeley.com/datasets/hd96prn3nc

**参考論文**
- Digital twin of wind turbine surface damage detection:
  https://www.sciencedirect.com/science/article/abs/pii/S0960148124024005

**注意点**
- ラベルは擬似ラベルになりやすい
- "進行予測"ではなく、まず"進行スコア化"を優先する
- モデル精度より定義と解釈可能性を重視する

**位置づけ**：画像分類から予測方向へ踏み込む段階。

---

### Phase 3：SCADA・時系列の基礎研究

**候補テーマ**
「風車SCADAデータを用いたブレード疲労リスク代理指標の試作」

**目的**
- 負荷側・運転側の情報を扱えるようにする
- 将来の疲労・劣化推定につながる土台を作る

**最終目標との接続**
→ 「負荷履歴・運転履歴の扱い」という部品。

**ツール・データ**

| 名称 | 種別 | URL |
|---|---|---|
| OpenOA | ツール（一次） | https://openoa.readthedocs.io/ |
| Wind Turbine SCADA Dataset (Kaggle) | 二次（練習用） | https://www.kaggle.com/datasets/berkerisen/wind-turbine-scada-dataset |

**注意点**
- SCADAだけでブレード劣化と断定しない
- "疲労リスク代理指標"や"運転負荷ベースライン"を作ることが目標
- Kaggleデータは形式・品質がまちまち。必ずデータ辞書を作る
- 後で実務データに差し替え可能な構造にする

**位置づけ**：練習的要素も強いが、本命への負荷側部品として重要。

---

### Phase 4：画像と時系列の統合

**候補テーマ**
「画像損傷スコアと運転データを用いたブレード劣化進行リスク推定」

**目的**
- 見た目の損傷と運転・負荷情報をつなげる
- 劣化進行予測の前段階を作る

**最終目標との接続**
→ 「マルチモーダル統合」という部品。

**将来的に接続候補として意識するもの**
- 自社点検画像
- 補修履歴
- 停止履歴
- 気象イベント履歴

**注意点**
- 公開データだけだと弱い場合がある
- 公開データで枠組みを作り、自社データ接続を見据える構造にする

**位置づけ**：本命テーマにかなり近い。公開データで「型」を作り、実務データで育てる段階。

---

### Phase 5：SHM・シミュレーション・デジタルツイン連携

**候補テーマ**
「OpenFASTを用いた風車ブレード負荷応答と劣化リスク推定の連携検討」

**目的**
- 工学的裏付けを追加する
- 個人研究から大学院研究へ接続しやすくする

**最終目標との接続**
→ 「物理モデルとの接続」という部品。

**一次ソース**

| 名称 | URL |
|---|---|
| OpenFAST Documentation | https://openfast.readthedocs.io/ |
| OpenFAST GitHub | https://github.com/OpenFAST/openfast |
| Zenodo ブレードSHM Dataset | https://zenodo.org/records/13692213 |
| Zenodo Vibration Benchmark | https://zenodo.org/records/3229743 |

**注意点**
- 最初から本格実装しない。まずはOpenFASTを読める・少し動かせることが目標
- SHMは"完全なブレード余寿命"より"損傷指標設計"の練習として扱う
- ここは大学院研究への橋渡しとして重要

**位置づけ**：本命テーマの上級部品。個人研究から大学院研究へ接続するための工学的基盤。

---

## 3か月の週次計画

| 週 | 作業内容 | 成果物 |
|---|---|---|
| W01 | リポジトリ構成・README・研究ログテンプレ | repo初期構成 ✅ |
| W02 | OpenOA/OpenFAST概要把握・環境構築メモ | environment_setup.md |
| W03 | DTU原データ取得・画像・アノテーション構造把握 | データ辞書v1 |
| W04 | アノテーション変換・YOLO形式整備・クラス定義確認 | 前処理スクリプト |
| W05 | YOLOv8学習（ベースライン）・train/val/test分割設計 | ベースライン結果 |
| W06 | mAP確認・誤検出分析・アノテーション品質再確認 | 実験ログv1 |
| W07 | 部位定義設計・バウンディングボックス×部位マッピング | 部位定義ドキュメント |
| W08 | リスクスコア算出ロジック実装 | スコアリングスクリプト |
| W09 | スコア可視化・解釈可能性確認 | 可視化ノートブック |
| W10 | Energies 2019論文との比較・差分整理 | 比較メモ |
| W11 | レポート草案（目的・データ・手法・結果・考察） | レポートv1 |
| W12 | README最終化・GitHub公開整備・Phase 2移行計画 | 完成リポジトリ |

---

## データ・ツール優先順位

| 系統 | 優先ツール・データ | 位置づけ |
|---|---|---|
| 画像 | DTU/Mendeley原データ | 一次ソース。研究引用の根拠 |
| 時系列基盤 | OpenOA | 共通解析基盤 |
| 時系列練習 | Kaggle公開SCADA | 二次。後で実務データに差し替え |
| シミュレーション | OpenFAST | 工学的基盤 |
| SHM | Zenodo | 一次ソース |
| Kaggle全般 | 補助・入口 | 一次ソースがある場合は一次ソースを正とする |

---

## Kaggle等の二次ソースを使う場合の注意点

1. 使用前に原典URLを確認し、実験ログに記録する
2. 研究記録・引用には一次ソースのURLを記載する
3. KaggleスコアをそのままProposaに使わない
4. データ辞書を必ず作る（列名・単位・欠損処理を確認）
5. Kaggleは入口として使い、そこで完結させない

---

## 現在の進捗

最終更新: 2026-04-02

- **Phase 0**：完了（2026-03-31）
  - W01：リポジトリ作成・GitHub push・docs/data_sources.md・data/data_dict.md・実験ログテンプレ
  - W02：OpenOA/OpenFAST概要把握・environment_setup.md・Python仮想環境構築手順記載

- **Phase 1**：完了（2026-04-02）
  - DTU画像データによるYOLOv8損傷検出（EXP-001ベースライン→EXP-002ピラミッド拡張）
  - mAP@0.5: 0.3476 → **0.5805**（+67%）
  - 部位別リスクスコア算出・可視化まで完了
  - スパン方向マッピング確定・chord方向の限界を定量的に把握
  - 成果物: phase1_summary.md / risk_scores.csv / region_risk_scores.png

- **Phase 2**：完了（2026-04-02）
  - 2017/2018データセットレベルの損傷分布比較（探索的分析）
  - Mann-Whitney U検定（Root部位のみ有意: p=0.022、ただし実質的意味は限定的）
  - 同一箇所対応付け不可という構造的限界を定量的に確認
  - 成果物: phase2_summary.md / phase2_score_comparison.png / scores_by_year.json

- **Phase 3**：完了（2026-04-02）
  - Kaggle Wind Turbine SCADAデータ（トルコ、2018年、10分値）から疲労リスク代理指標を試作
  - 指標: hrs_above_rated / mean_ti / hrs_high_ti / fatigue_risk_score（月次）
  - 8月が最高リスク（0.482）。TIは全月0.03〜0.05の極低乱流環境
  - 成果物: phase3_summary.md / phase3_fatigue_proxy.csv / fatigue_proxy_monthly.png

- **Phase 4**：完了（2026-04-02）
  - 画像リスクスコア（Phase 1/2）× SCADA疲労代理指標（Phase 3）統合パイプラインの「型」実装
  - 合成データで動作確認（Pearson r=0.256、有意）
  - 自社データへの差し替え手順を明記（fusion_pipeline.py）
  - 成果物: phase4_summary.md / fusion_results.csv / fusion_results.png

- **Phase 5**：完了（2026-04-02）
  - IEC 61400-1 / Sutherland 1999参考の簡易解析荷重モデルによるDELプロキシ算出
  - hrs_above_rated vs DEL: Pearson r=+0.808（強い正相関）
  - このサイトではhrs_above_ratedが疲労を支配（TIの寄与は小さい：極低乱流環境のため）
  - OpenFAST DLC 1.2実行仕様を設計（openfast_pipeline_spec.md）
  - 成果物: phase5_summary.md / phase5_del_proxy.csv / phase5_load_analysis.png

- **Phase 5b**：完了（2026-04-02）
  - OpenFAST v3.5.1 + TurbSim: NREL 5MW, DLC 1.2, 8V×5TI=40ケース
  - DEL算出（RootMyb1, m=10, Teq=600s）: 全40ケース成功
  - 簡易モデル vs OpenFAST: Pearson r=0.978（高相関確認）
  - Phase 4重み較正: **w_V=0.810, w_TI=0.190**（V支配型サイト）
  - fusion_pipeline.py更新: 等重み0.5/0.5 → 較正済み0.81/0.19
  - 成果物: del_matrix.csv / model_comparison.png / phase4_weights_calibrated.json

- **マルチシード・標準Rainflow・長期DEL**：完了（2026-04-03）
  - 240ケース（8V×5TI×6seeds）、ASTM E1049標準Rainflow導入
  - 平均CV=8.9%（V≥8では安定）、簡易版との誤差平均42%（標準実装の必要性を確認）
  - 長期DEL（Weibull/IEC Class II・TI=14%）：約9,200 kN-m
  - 成果物: del_matrix_ms.csv / del_single_rainflow_comparison.csv / lifetime_del_stage2/3.csv

- **Phase 6: DLC 1.3（ETM）**：完了（2026-04-03）
  - 48ケース（8V×6seeds）、DLC 1.2比較
  - DLC 1.3 / DLC 1.2(TI=14%) 比率: 低速域×4.2、高速域×1.4
  - 成果物: del_comparison_dlc12_vs_dlc13.csv / del_comparison_dlc12_vs_dlc13.png

- **Phase H（Penmanshiel SCADA）**：完了（2026-04-03）
  - Zenodo Penmanshiel T01-T07, 2020年全年
  - TI直接計測（中央値0.133〜0.144）、DEL年間平均5,500〜5,700 kN-m
  - pipeline: phase3_scada/phase3_penmanshiel.py

- **Phase J（台間パワーカーブ比較）**：完了（2026-04-03）
  - T01-T06 fleet比較、Cp_max=0.45〜0.47、T05が最低(-3.5% AEP)
  - pipeline: phase3_scada/penmanshiel_power_curve.py

- **Phase K（縦断パワーカーブ 2016-2021）**：完了（2026-04-03）
  - T01、Cp_max 2017→2020: 0.4275→0.4513（増加傾向 ≠ 劣化）
  - pipeline: phase3_scada/penmanshiel_longitudinal.py

- **Phase I（MM82 OpenFASTモデル）**：完了（2026-04-04）
  - NREL 5MW → Senvion MM82 幾何スケーリング（λ_R=0.651, λ_H=0.674）
  - 検証ケース: DEL比0.258（理論0.276, 誤差6.5%）
  - 240ケース完了: DEL 215〜4,046 kN·m、CV平均6.1%
  - W_V/W_TI MM82再較正: w_V=0.725, w_TI=0.275（R²=0.943）
  - Penmanshiel DEL（MM82基準）: 年間平均1,497〜1,742 kN·m、ピーク2月

- **Phase L（縦断DELトレンド）**：完了（2026-04-04）
  - T01（2016-2021）: DEL 1,155〜1,507 kN·m
  - DEL増加は風況年変動（V_mean/TI増加）が主因。Cp_max増加（劣化なし）と整合
  - pipeline: phase3_scada/phase_L_longitudinal_del.py

- **Phase M（DLC 2.1 終局荷重）**：完了（2026-04-04）
  - グリッド喪失→緊急停止、36ケース（V=8〜18m/s × 6seeds）
  - フォルト後ピーク < フォルト前（比率0.54〜0.87）→ 緊急ピッチの荷重低減有効
  - V=12m/s でフォルト前ピーク最大（3,116 kN·m）

- **Phase N（DLC 2.2 ピッチ固着）**：完了（2026-04-04）
  - Blade 1 固着 × 36ケース。V=18m/sで DLC 2.1 比×2.09の荷重増大
  - 定格以上（V>13m/s）で非対称荷重が急増。DLC 2.2 が支配ケースになりうる

- **統合レポート**：v2.1（docs/integrated_research_report.md）
