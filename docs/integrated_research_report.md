# 風車ブレード劣化予測に向けた統合研究基盤の構築
## 画像・SCADA・空力シミュレーションの統合的アプローチ

**作成日**: 2026-04-02
**最終更新**: 2026-04-04（v3.0: 論文品質化・全フェーズ統合）
**著者**: himin（Wind Turbine Technician / 研究者）
**対象リポジトリ**: blade-degradation-research/

---

## Abstract

本研究は、風車ブレードの劣化予測に向けた統合研究基盤を段階的に構築することを目的とした。画像ベースの損傷検出（Phase 1-2）、SCADAデータによる疲労リスク代理指標の構築（Phase 3）、統合パイプラインのI/O仕様実装（Phase 4）、および空力シミュレーションによる荷重較正と終局荷重評価（Phase 5〜N）を体系的に実施した。

OpenFAST v3.5.1 を用いた一連のシミュレーション解析では、NREL 5MW 参照タービン 240 ケース（DLC 1.2, IEC 61400-1 NTM, 8V × 5TI × 6seed）に加え、実機 Senvion MM82 へのスケーリングモデル 240 ケース、DLC 1.3（ETM）48 ケース、DLC 2.1/2.2（フォルト荷重）計 72 ケースの合計 **600 ケース**を実行した。DEL 算出には ASTM E1049 系標準 Rainflow（rainflow 3.2.0）を使用した。

主な定量的知見：

- **Rainflow 実装精度**: 標準 Rainflow は簡易版に対し平均 42% 高い DEL を算出。高精度疲労評価には標準実装が必須
- **マルチシード再現性**: V ≥ 8 m/s では CV 中央値 5.9%。低 TSR 域（V = 4 m/s）では最大 35%
- **機種適合モデル**: NREL 5MW → MM82 幾何スケーリング（λ_R = 0.651）により DEL 比 0.258（理論 0.276、誤差 6.5%）を達成。MM82 固有 DEL 範囲 215〜4,046 kN·m
- **疲労支配因子**: MM82 DEL matrix による較正で w_V = 0.725 / w_TI = 0.275（R² = 0.943）。小型機では TI 寄与が相対的に増大
- **実サイト DEL**: Penmanshiel SCADA（Senvion MM82, 7 台, 2020 年）に MM82 matrix を適用し、年間平均 DEL 1,497〜1,742 kN·m。ピーク 2 月（冬季強風）
- **縦断トレンド（2016-2021）**: T01 の DEL 増加（+13.7%）は風況の年変動（V_mean / TI 増加）が主因。Cp_max 増加傾向（劣化なし）と整合
- **終局荷重**: DLC 2.1（全ブレード正常停止）では緊急ピッチによる荷重低減が有効（比率 0.54〜0.87）。DLC 2.2（ピッチ固着）では高風速域（V ≥ 16 m/s）で DLC 2.1 比 ×1.4〜2.1 の非対称荷重増大

本研究は「劣化予測モデルの実証」ではなく、同一タービンでの実データ統合を見据えた**統合研究基盤の構築と方法論の検証**として位置づける。

---

## 1. はじめに

### 1.1 研究動機

現場でのロープアクセスによるブレード点検・補修経験から、補修箇所の「1年後」を予測したいという実践的動機を持つ。
再エネO&Mの現場では、補修計画が検査タイミングと補修コストの権衡で決まるが、
その判断を支える定量的な劣化予測モデルは整備されていない。

本研究は、公開データを用いて「画像×運転データ×物理モデル」を統合する枠組みを構築し、
将来の実データ投入時に即活用できる型を作ることを目標とした。

### 1.2 研究の位置づけ

| 視点 | 役割 |
|---|---|
| ロープアクセス技術者 | 補修対象の特定・優先付けに直結 |
| O&M分析担当者 | 意思決定支援ツールの基盤 |
| 大学院研究候補 | 修士研究への発展的接続 |

### 1.3 全体構成

```
Phase 0:  研究基盤整備（再現性確保）
Phase 1:  画像損傷検出 → 部位別リスクスコア
Phase 2:  時点差画像 → 損傷進行の探索的分析
Phase 3:  SCADA時系列 → 疲労リスク代理指標
Phase 4:  画像×SCADA統合パイプライン（I/O仕様検証）
Phase 5:  簡易荷重モデル → DELプロキシ
Phase 5b: OpenFAST NREL 5MW → DELマトリクス・重み較正
Phase 6:  DLC 1.3（ETM）疲労荷重増分の定量化
Phase H:  Penmanshiel SCADA → 実サイトDEL推定
Phase I:  MM82スケーリングモデル → 機種適合DELマトリクス
Phase J:  パワーカーブ台間比較（2020フリート）
Phase K:  縦断パワーカーブ（T01, 2016-2021）
Phase L:  縦断DELトレンド（T01, 2016-2021）
Phase M:  DLC 2.1 グリッド喪失 → 終局荷重
Phase N:  DLC 2.2 ピッチ固着 → 非対称終局荷重
```

---

## 2. Phase 0: 研究基盤整備

**完了日**: 2026-03-31

- GitHubリポジトリ構築（再現性確保）
- データ辞書テンプレート作成（data/data_dict.md）
- OpenOA / OpenFAST 環境構築（conda env: blade-phase3）
- 実験ログテンプレ・データソース一覧整備

---

## 3. Phase 1: 画像ベース損傷検出・部位別リスクスコア

**完了日**: 2026-04-02

### 3.1 データ

| 項目 | 内容 |
|---|---|
| データ | DTU Wind Turbine Inspection Images（Mendeley） |
| 形式 | YOLOv8アノテーション済み（Backbone: Mendeley二次） |
| 画像数 | 2017年161枚 + 2018年398枚（合計559枚） |
| クラス数 | 10（Leading Edge Erosion, Crack, Surface Damage等） |
| 分割 | 画像単位でtrain/val/test分割（同一ブレード由来画像が複数セットに混入しないよう配慮） |

### 3.2 手法

- **EXP-001**: YOLOv8n ベースライン学習（640px, 50 epoch）
- **EXP-002**: ピラミッドパッチ拡張（1024pxパッチ×スライディングウィンドウ）
- 部位定義: スパン方向（Tip: cy≦0.33, Mid: 0.33<cy≦0.67, Root: cy>0.67）
  - chord方向（LE/TE）は cx分布が 0.004〜0.992 に均一分布し信頼性低のため除外

### 3.3 リスクスコア定義

各検出に対して以下のスコアを算出し、部位ごとに合計：

```
score_i = confidence_i × area_ratio_i × class_weight_i × region_weight_i
region_score = Σ score_i  (同一部位の全検出を合計)
```

| パラメータ | 定義 | 値 |
|---|---|---|
| confidence | YOLOv8の検出信頼度（0〜1） | モデル出力値 |
| area_ratio | 正規化バウンディングボックス面積（w×h） | 0〜1 |
| class_weight | 損傷クラスの重篤度重み | CR:3.0, ER:2.0, MT/DA:1.5, PO:1.0 |
| region_weight | スパン部位の重み | Tip:3.0, Mid:2.0, Root:1.0 |

部位重みの根拠: 翼端（Tip）はエロージョン感応速度（周速最大）・疲労応力集中の観点から最高リスクと設定（現場知識・Malik & Bak 2025と整合）。

### 3.4 結果

| 実験 | mAP@0.5 | mAP@0.5:0.95 |
|---|---|---|
| EXP-001（ベースライン） | 0.3476 | 0.1891 |
| EXP-002（パッチ拡張） | **0.5805** | **0.3347** |
| 改善率 | +67% | +77% |

**部位別リスクスコア（2018年, EXP-002, 上位3部位）**:

| 部位 | 累積スコア | 主要クラス |
|---|---|---|
| Tip | 最高 | LE;ER（浸食）・LE;CR（クラック）集中 |
| Mid | 中程度 | 散発的損傷 |
| Root | 低め | 構造的損傷少 |

### 3.5 限界

- chord方向（LE/TE）の判別は信頼性低（cx分布が均一）→ Phase 2以降は除外
- 公開データのアノテーション品質にばらつきあり
- train/val/test分割は画像単位であり、同一ブレード内の異なる角度の画像間の独立性は完全には保証されない

---

## 4. Phase 2: 時点差画像と損傷進行の探索的分析

**完了日**: 2026-04-02

### 4.1 分析方針の修正

Phase 1の検証結果より、2017/2018の同一箇所対応付けは構造的に不可能と確認：
- ファイル名重複: 0件
- GPS誤差: 2〜5m（ブレード長63mに対し分解能不足）

→ 個別ペア比較を断念し、**データセットレベルの分布比較**（探索的）に変更。

### 4.2 結果

| 部位 | 2017年 スコア中央値 | 2018年 スコア中央値 | Mann-Whitney p値 |
|---|---|---|---|
| Tip | 0.142 | 0.135 | 0.423（非有意） |
| Mid | 0.088 | 0.092 | 0.671（非有意） |
| Root | 0.071 | 0.091 | **0.022（有意）** |

※ 多重比較補正（Bonferroni: α=0.05/3=0.017）を適用すると、Root部位も非有意となる。

### 4.3 解釈

Root部位のみ統計的有意差が検出されたが、（1）多重比較補正後は非有意、（2）学習データ中の2018年比率44% vs 2017年12%のバイアスを考慮すると実質的意味は限定的。

**主な成果は「できなかったこと」の定量化**: 「同一ブレードの経年変化追跡」は現在の公開データ構造では構造的に困難であることを確認した点が主な貢献である。

---

## 5. Phase 3: SCADAデータによる疲労リスク代理指標

**完了日**: 2026-04-02

### 5.1 データ

| 項目 | 内容 |
|---|---|
| ソース | Kaggle Wind Turbine SCADA（Berker Isen, 2018） |
| タービン | トルコ, 定格出力~3,600kW |
| 期間 | 2018年1〜12月（10分値, 47,592件） |
| 定格風速 | ~12 m/s（実測パワーカーブより推定） |

### 5.2 指標定義

| 指標 | 定義 | 根拠 |
|---|---|---|
| `hrs_above_rated` | 定格風速超の月間運転時間[h] | 高風速 = 高荷重 = 疲労蓄積の代理 |
| `mean_ti` | 月平均乱流強度（風速ビン内σ/μ） | TI高 = 荷重変動大 |
| `fatigue_risk_score` | 上記の正規化加重和 | 複合疲労代理指標 |

### 5.3 主要結果

- 最高リスク月: **8月**（fatigue_risk_score=0.482）← hrs_above_rated=124h
- このサイトは極低乱流環境（mean_ti: 0.027〜0.047）
- TIが低いため、wind speed（hrs_above_rated）が疲労リスクを支配

---

## 5b. Phase 3b: DELルックアップテーブル化

**完了日**: 2026-04-03

### 5b.1 目的

Phase 3の疲労代理指標（無次元スコア）を、OpenFAST DELマトリクス（Phase 5b）を使った物理量（kN-m）へ格上げする。あわせてTI計算をIEC 61400-1準拠（1 m/s整数ビン平均、V>3 m/s、ビン内N≥5）に刷新する。

### 5b.2 実装

| 要素 | 実装内容 |
|---|---|
| 補間器 | `scipy.interpolate.RegularGridInterpolator`（V×TI 2次元線形補間） |
| 補間元 | `del_matrix_ms_extended.csv`（384ケース・標準Rainflow・マルチシード平均） |
| V範囲 | 4〜18 m/s（行列端でクリップ） |
| TI範囲 | **0.02〜0.20**（低TI域拡張後） |
| 疲労リスクスコア再定義 | DEL正規化値（全タービン横断0-1） |

#### 低TI域拡張（Phase 3 Priority 2）

実サイトTI（0.030〜0.044）が既存行列下限（TI=0.08）を下回るTIクリッピング問題を解消するため、TI=0.02/0.04/0.06 × V=4〜18 m/s × 6シード = **144ケース**を追加シミュレート。

| 新TI点 | V=6 m/s DEL | V=8 m/s DEL | V=10 m/s DEL |
|---|---|---|---|
| TI=2% | 779 kN-m | 1,580 kN-m | 2,445 kN-m |
| TI=4% | 1,096 kN-m | 2,116 kN-m | 3,077 kN-m |
| TI=6% | 1,447 kN-m | 2,696 kN-m | 3,780 kN-m |
| （参考）TI=8%（既存） | 1,749 kN-m | 3,425 kN-m | 4,673 kN-m |

### 5b.3 月次DEL推定結果（低TI拡張後）

| 月 | V_mean (m/s) | TI_iec | DEL_est (kN-m) | 旧推定 | 変化 |
|---|---|---|---|---|---|
| 1月 | 7.97 | 0.031 | **1,850** | 3,396 | -46% |
| 2月 | 7.22 | 0.032 | **1,527** | 2,770 | -45% |
| 3月 | 8.61 | 0.030 | **2,116** | 3,808 | -44% |
| 4月 | 5.38 | 0.037 | **925** | 1,508 | -39% |
| 5月 | 5.86 | 0.040 | **1,062** | 1,694 | -37% |
| 6月 | 6.19 | 0.038 | **1,165** | 1,909 | -39% |
| 7月 | 4.95 | 0.044 | **931** | 1,341 | -31% |
| **8月** | **9.08** | 0.038 | **2,582** | 4,097 | -37% |
| 9月 | 7.26 | 0.036 | **1,638** | 2,805 | -42% |
| 10月 | 7.28 | 0.038 | **1,700** | 2,821 | -40% |
| 11月 | 8.48 | 0.032 | **2,135** | 3,725 | -43% |
| 12月 | 6.43 | 0.032 | **1,164** | 2,113 | -45% |
| **年間平均** | — | — | **1,566** | 2,665 | **-41%** |

**解釈**: 旧推定はTI=0.08クリップにより約41%過大推定していた。拡張後は実サイトTI（0.03〜0.04）を正しく補間できており、月ごとのDEL差にTI変動の影響が反映されるようになった（最低月が7月→4月に変化）。

### 5b.4 TI計算手法の比較

| 手法 | 年平均TI | 備考 |
|---|---|---|
| 旧（σ/μ直接計算） | 0.0317 | Phase 3 従来手法 |
| 新（IEC 61400-1 ビン平均） | 0.0356 | +12%（低速ビンの高TI値を加重） |

---

## 6. Phase 4: 画像×SCADA統合パイプライン（I/O仕様検証）

**完了日**: 2026-04-02

### 6.1 設計方針

DTU画像（デンマーク・Nordtank）とKaggle SCADA（トルコ・別メーカー）は**異なるタービン**であるため、直接統合は統計的に無意味。

**本フェーズの目的は「予測性能の検証」ではなく、将来の実機データ統合を見据えた「I/O仕様の検証・パイプライン型実装」である。**

→ パイプライン構造のみを実装し、合成データで動作確認。自社データへの差し替え手順を明記。

### 6.2 統合スコア定義（Phase 5b較正前）

```
統合リスクスコア = α × 画像リスク + β × 疲労リスク
疲労リスクスコア = hrs_above_rated_norm × 0.5 + mean_ti_norm × 0.5  (等重み・暫定)
```

### 6.3 合成データによるI/O仕様確認

| 指標 | 値 | 解釈 |
|---|---|---|
| Pearson r（画像リスク vs 疲労リスク） | 0.256（p=0.048） | パイプラインが壊れていないことの確認に留まる |
| Spearman r | 0.212（p=0.104, 非有意） | 同上 |

合成データ上での相関確認は「パイプラインが壊れていない」ことの確認であり、実際の予測性能の検証ではない。

---

## 7. Phase 5: 簡易ブレード荷重モデルによるDELプロキシ

**完了日**: 2026-04-02

### 7.1 モデル定式

IEC 61400-1 / Sutherland (1999) 参考の解析式モデル:

```
I_fatigue(V, TI) = (V / V_rated)^n × CT(V) × (1 + γ × TI)
```

| パラメータ | 値 | 根拠 |
|---|---|---|
| n=3 | 疲労損傷の風速指数 | IEC 61400-1 Annex H |
| γ=5 | TI増幅係数 | Sutherland 1999 |
| m=10 | SN曲線指数 | GFRP、DNV GL 2016 |
| V_rated=11.4 m/s | 定格風速 | NREL 5MW参照タービン |
| CT(V) | スラスト係数 | V≦V_rated: 0.80, 超過: 0.80×(V_rated/V)² |

### 7.2 主要結果

| 指標 | Pearson r | p値 | 解釈 |
|---|---|---|---|
| hrs_above_rated vs DEL_proxy | +0.808 | 0.001 | 強い正相関 |
| mean_ti vs DEL_proxy | -0.899 | <0.001 | 強い負相関（Simpson's Paradox） |

`mean_ti`の負相関はSimpson's Paradox: 高TI月（夏）が低風速季節と重なるため見かけ上負相関。風速ビンで条件付けると正相関に反転（図: docs/simpsons_paradox.png参照）。

**Panel 1（全体）**: r = -0.899 → 見かけ上の強い負相関
**Panel 2（風速ビン別）**: 各グループ内では正相関（Low: r≈+0.6, Mid: r≈+0.7, High: r≈+0.8）

季節的な交絡（夏＝高TI×低風速）が原因であり、TI自体は疲労荷重を増加させる正の効果を持つ。

---

## 8. Phase 5b: OpenFASTシミュレーションによるDEL算出と重み較正

**完了日**: 2026-04-02

### 8.1 シミュレーション設定

| 項目 | 設定値 |
|---|---|
| コード | OpenFAST v3.5.1 |
| 参照タービン | NREL 5MW Land-Based (r-test v3.5.1) |
| 設計荷重ケース | DLC 1.2（IEC 61400-1 NTM） |
| 風速V | 4, 6, 8, 10, 12, 14, 16, 18 m/s（8点） |
| 乱流強度TI | 8, 12, 14, 16, 20%（5点） |
| ケース総数 | 40（単一シード） |
| シミュレーション時間 | 600秒（+ 60秒過渡除去） |
| モジュール | ElastoDyn + AeroDyn15 + ServoDyn(ROSCO 2.10.1) + InflowWind |
| 風場生成 | TurbSim v3.5.1（IEC IECKAI, PL profile, HubHt=90m） |

**注**: 初期解析は単一シードで実施。その後IEC 61400-1推奨に従い各条件6シード（計240ケース）のマルチシード解析を追加実施した（下記 §8.6参照）。

### 8.2 DEL定義

```
DEL = (Σ(n_i × ΔS_i^m) / N_eq)^(1/m)
```

| パラメータ | 値 |
|---|---|
| チャンネル | RootMyb1（ブレード1根元フラップモーメント） |
| m | 10（GFRP） |
| T_eq | 600 s |
| 過渡除去 | 最初60秒スキップ |
| Rainflow法 | ASTM E1049系 4点法（rainflow 3.2.0）※初期解析は簡易版、マルチシード解析から標準実装に刷新 |

### 8.3 DELマトリクス（kN-m）

|  V \ TI  | 0.08  | 0.12  | 0.14  | 0.16  | 0.20  |
|---------|-------|-------|-------|-------|-------|
| 4 m/s   | 331   | 439   | 554   | 560   | 868   |
| 6 m/s   | 781   | 1120  | 1194  | 1687  | 1797  |
| 8 m/s   | 1591  | 2148  | 2146  | 2574  | 3461  |
| 10 m/s  | 2515  | 3829  | 4929  | 4786  | 5185  |
| 12 m/s  | 5658  | 6024  | 6416  | 6500  | 6268  |
| 14 m/s  | 5121  | 6712  | 8064  | 7991  | 7452  |
| 16 m/s  | 6256  | 6494  | 7448  | 8870  | 9135  |
| 18 m/s  | 6366  | 6971  | 7691  | 8534  | 8742  |

**特記事項**:
- V=12 m/s（定格付近）でDELが最大化する傾向あり（V=10→12でジャンプ）
- V=14〜18では定格出力制限（ピッチ制御）によりDELが頭打ち傾向
- TIの増加はDELを一貫して増加させる

### 8.4 簡易モデルとOpenFASTの比較

| 検定 | r値 | p値 |
|---|---|---|
| Pearson | **0.978** | <0.0001 |
| Spearman | **0.975** | <0.0001 |

NREL 5MW参照タービン・DLC 1.2・単一シード条件下において、簡易モデルはOpenFASTのDELトレンドを高い精度で再現した。この整合性は本研究条件に限定されるものであり、実機タービンや異なるサイト条件への一般化には追加検証が必要。

### 8.5 Phase 4重みの較正（偏回帰）

LinearRegression(positive=True): DEL_norm ~ V_norm + TI_norm

| 重み | 値 | 解釈 |
|---|---|---|
| **w_V** | **0.810** | 風速（hrs_above_rated）が支配的 |
| **w_TI** | **0.190** | TI（mean_ti）は補助的 |
| R² | 0.926 | 高い説明力 |

この較正結果はNREL 5MW参照条件下での値であり、対象SCADAサイト（低TI内陸）の特性と整合的であることを確認した。ただし、本較正値を対象SCADAサイト固有の重みとして直接解釈するには、同一タービン・実サイト条件での追加検証が必要である。

**fusion_pipeline.pyに反映済み**（等重み0.5/0.5 → 較正済み0.81/0.19）

### 8.6 マルチシード解析結果（IEC 61400-1準拠）

**設定**: 各40条件 × 6シード = 240ケース、ASTM E1049系標準Rainflow

#### Rainflow実装比較

| 指標 | 値 |
|---|---|
| 標準Rainflow vs 簡易版の平均誤差 | **42%**（簡易版が系統的に過小評価） |
| 最大誤差 | **76%**（V=4 m/s, TI=12%） |
| 誤差の傾向 | 低風速・低定常域で大きく、高風速域（V≥12）では12〜40%に縮小 |

簡易版のハーフサイクルカウントは、低TSR域（V=4〜8 m/s）での非定常成分を大幅に過小評価することが判明した。**高精度疲労評価には標準Rainflow実装が必須**。

#### マルチシードDEL統計

| 統計量 | 値 |
|---|---|
| CV 全体平均 | **8.9%** |
| CV 中央値 | **5.9%** |
| CV 最大 | **35.1%**（V=4 m/s, TI=8%：低TSR域で変動大） |
| V≥8 m/s でのCV範囲 | 1.8〜14.4%（概ね安定） |

V=4 m/s は低TSR（翼端速度比が低く空力が不安定）で確率的変動が大きい。実用的な疲労評価では**V≥6 m/sの寄与が支配的**であり、低風速ビンの高CVは長期DELへの影響は限定的。

#### マルチシードDEL平均マトリクス（kN-m、標準Rainflow）

|  V \ TI  | 0.08  | 0.12  | 0.14  | 0.16  | 0.20  |
|---------|-------|-------|-------|-------|-------|
| 4 m/s   | 970   | 1417  | 1559  | 1484  | 1864  |
| 6 m/s   | 1749  | 2704  | 3070  | 3414  | 4159  |
| 8 m/s   | 3425  | 4612  | 5506  | 6218  | 7173  |
| 10 m/s  | 4673  | 6196  | 7156  | 7824  | 9282  |
| 12 m/s  | 6176  | 7979  | 8759  | 9804  | 11859 |
| 14 m/s  | 7290  | 9316  | 9910  | 11146 | 12798 |
| 16 m/s  | 7951  | 10240 | 11192 | 11952 | 14472 |
| 18 m/s  | 8692  | 11034 | 12095 | 12972 | 15109 |

### 8.7 長期DEL算出

#### Stage 2: Weibull風速重み付き長期DEL（kN-m）

Weibull分布（k=2）で風速方向に重み付け。各TIビンを固定した場合の長期DEL：

| TI | IEC Class I (Vave=10.0) | IEC Class II (Vave=8.5) | IEC Class III (Vave=7.5) |
|---|---|---|---|
| 8% | 6,942 | 6,605 | 6,263 |
| 12% | 8,871 | 8,447 | 8,018 |
| 14% | 9,674 | 9,204 | 8,729 |
| 16% | 10,474 | 9,995 | 9,513 |
| 20% | 12,365 | 11,809 | 11,248 |

#### Stage 3: V-TI同時分布（独立近似）による長期DEL（kN-m）

IEC NTM式（TI(V) = I_ref × (0.75 + 5.6/V)）で各VのTI代表値を決定し、Weibull重み付きで統合：

| IECクラス | IEC Class I | IEC Class II | IEC Class III |
|---|---|---|---|
| Class C (I_ref=0.12) | 9,366 | 8,965 | 8,564 |
| Class B (I_ref=0.14) | 10,348 | 9,938 | 9,529 |
| Class A (I_ref=0.16) | 11,327 | 10,891 | 10,452 |

**解釈**: 対象SCADAサイト（低TI内陸）はIEC Class C / Class II相当と推定され、長期DELの目安は**約9,000 kN-m**。Class Aサイト（高TI）では**約10,900 kN-m**と21%増加する。この差がエロージョン進行速度の差に直結する（Malik & Bak 2025）。

---

## 9. 考察

### 9.1 疲労支配因子の機種間比較

DELマトリクスに基づく疲労支配因子較正を、NREL 5MW 参照タービンと実機 MM82 スケーリングモデルの2機種で実施した。

| | NREL 5MW（§8.5） | MM82（§16.5） |
|---|:---:|:---:|
| **w_V** | 0.810 | **0.725** |
| **w_TI** | 0.190 | **0.275** |
| R² | 0.926 | 0.943 |
| DEL範囲 (kN·m) | 970〜15,109 | 215〜4,046 |

MM82 では TI の寄与が相対的に増大する。**仮説**: 小型機（R=41m）はローター面内の乱流スケール比（L_t/D）が相対的に大きくなるため、TI 変動がフラップ荷重に強く反映される可能性がある。ただし翼型プロキシ使用の不確実性もあり、確定結論ではない。

いずれの機種でも w_V > w_TI（風速が支配的）だが、サイトの TI 水準により影響度は変化する。

| サイト種別 | 想定 w_V | 想定 w_TI | 再較正の必要性 |
|---|---|---|---|
| 低TI内陸（Kaggle SCADA相当） | ~0.81 | ~0.19 | NREL 5MW ベースライン |
| 中TI内陸（Penmanshiel相当） | ~0.73 | ~0.27 | MM82 較正済み |
| 高TI沿岸/複雑地形 | ~0.5〜0.6 | ~0.4〜0.5 | **要再較正** |

### 9.2 縦断分析に基づく劣化有無の評価

Phase K（パワーカーブ）と Phase L（DELトレンド）を組み合わせた6年間の縦断分析（T01, 2016-2021）から、以下の整合的な結論が得られた。

- **Cp_max**: 2017→2020 で 0.4275→0.4513 と増加（空力劣化は観察されない）
- **DEL**: 同期間に +13.7% 増加したが、V_mean・TI_med の増加に連動しており風況変動が主因
- 2021 年に V が低下すると DEL も 2017 水準に回帰 → 機体状態の経年変化ではなく、風況の年変動で説明可能

**解釈**: 本データセットの観測期間（稼働開始後5年）では、SCADAベースの指標に検出可能な劣化信号は確認されなかった。ただし、エロージョンによる Cp 低下は年間 0.1〜0.5% 程度と報告されており（Malik & Bak 2025）、5年間の風況変動（V_mean ±0.7 m/s）のノイズに埋もれている可能性がある。

### 9.3 疲労荷重と終局荷重の支配条件

DLC 1.2（疲労）・DLC 2.1（正常停止）・DLC 2.2（ピッチ固着）の3ケースを統合的に比較すると、荷重評価の支配条件が荷重タイプにより明確に異なる。

| 評価タイプ | 支配ケース | 支配風速域 | 根拠 |
|---|---|---|---|
| **疲労（DEL）** | DLC 1.2 / DLC 1.3 | V=14〜18 m/s | 累積サイクル数が風速と共に増加 |
| **終局（ピーク）正常停止** | DLC 2.1 | V=10〜12 m/s | 定格付近の過渡応答が最大 |
| **終局（ピーク）ピッチ固着** | DLC 2.2 | **V=16〜18 m/s** | 非対称荷重が定格以上で急増（×2.09） |

DLC 2.2 は高風速域で DLC 2.1 を大幅に上回り（V=18 m/s で ×2.09）、定格以上の風速域で設計支配ケースとなりうる。ピッチ冗長性（独立ピッチ駆動）を持たない機種では、DLC 2.2 が終局設計の決定因子となる可能性が高い。

### 9.4 研究の強みと限界

**強み**:
- 画像・SCADA・物理シミュレーションの3ソースを統合する枠組みを、公開データのみで構築
- Phase 2 で「できなかった理由」を成果化（同一箇所追跡の構造的困難の定量化）
- NREL 5MW + MM82 の2機種で DEL マトリクスを構築し、機種間の重み差を定量化
- Penmanshiel 実 SCADA（7台・6年）に基づく実サイト DEL 推定とフリート間比較
- DLC 1.2/1.3/2.1/2.2 の4ケースによる疲労・終局荷重の包括的評価（合計 600 ケース）
- 自社データへの差し替え手順を明記した実務接続可能な設計

**限界**:
- 画像と SCADA が異なるタービン（同一タービンでの統合検証は未実施）
- Phase 4 は合成データによる I/O 仕様検証に留まる（予測性能未検証）
- MM82 モデルは翼型プロキシを使用（Senvion 翼型データ非公開）。DEL 絶対値は参考値
- 低 TSR 域（V=4 m/s）の CV 最大 35% — 低風速ビンには追加シードが望ましい
- 長期 DEL の TI 分布は独立近似（V-TI 相関を無視）— 実サイトの結合分布があれば精度向上可能
- 縦断分析は単一タービン（T01）のみ。フリート全体の経年変化には追加タービンの分析が必要

### 9.5 大学院研究への接続

本研究の枠組みは以下の方向に発展可能：

1. **疲労余寿命推定**: 累積 DEL と許容 DEL の比較（マイナー則）。本研究の年間 DEL（1,500 kN·m 級、MM82 基準）を起点に、設計寿命 20 年での累積疲労損傷度を算出できる
2. **劣化加速モデル**: エロージョン → 空力性能低下 → AEP 損失の定量化（Malik & Bak 2025）。Phase K/L の縦断データ基盤がそのまま活用可能
3. **状態ベースメンテナンス（CBM）**: DEL 予測 × 点検間隔最適化。DLC 2.2 の非対称荷重増大（×2.09）はピッチ機構の健全性監視の重要性を示唆
4. **デジタルツイン接続**: リアルタイム SCADA → 動的 DEL 推定。Phase H のパイプライン（phase3_penmanshiel.py）が雛形となる

---

## 10. 成果物一覧

| フェーズ | ファイル | 内容 |
|---|---|---|
| Phase 1 | phase1_image_risk_score/phase1_summary.md | 損傷検出・リスクスコア概要 |
| Phase 1 | phase1_image_risk_score/risk_scores.csv | 部位別リスクスコア |
| Phase 1 | runs/pyramid_yolov8n/weights/best.pt | 学習済みYOLOv8モデル |
| Phase 2 | phase2_temporal/phase2_summary.md | 時点差分析概要 |
| Phase 2 | phase2_temporal/phase2_score_comparison.png | 年次比較可視化 |
| Phase 3 | phase3_scada/phase3_fatigue_proxy.csv | 月次疲労代理指標 |
| Phase 3 | phase3_scada/fatigue_proxy_monthly.png | 月次可視化 |
| Phase 3b | phase3_scada/phase3b_del_lookup.py | DELルックアップ・IEC TI計算スクリプト（拡張行列対応） |
| Phase 3b | phase3_scada/phase3b_monthly_del.csv | 月次DEL推定値（kN-m）・低TI拡張後（年平均1,566 kN-m） |
| Phase 3b | phase3_scada/phase3b_del_comparison.png | 旧疲労スコアvs新DEL推定値 4パネル比較図 |
| Phase 3b 拡張 | phase5_openfast_shm/openfast_cases/results/del_matrix_ms_extended.csv | 拡張DEL行列（384ケース・TI=0.02〜0.20） |
| Phase 3b 拡張 | phase5_openfast_shm/openfast_cases/scripts/low_ti_extension_pipeline.py | 低TI域拡張パイプライン（TI=0.02/0.04/0.06、144ケース） |
| Phase 4 | phase4_fusion/fusion_pipeline.py | 統合パイプライン（w_V=0.740較正済み） |
| Phase 4 | phase4_fusion/fusion_results.csv | 統合リスクスコア（合成） |
| Phase 5 | phase5_openfast_shm/phase5_del_proxy.csv | 月次DELプロキシ |
| Phase 5b | phase5_openfast_shm/openfast_cases/results/del_matrix.csv | OpenFAST DELマトリクス（40ケース・単一シード簡易Rainflow） |
| Phase 5b | phase5_openfast_shm/openfast_cases/results/model_comparison.png | 簡易モデル vs OpenFAST比較 |
| Phase 5b | phase5_openfast_shm/openfast_cases/results/phase4_weights_calibrated.json | 較正済み重み |
| Phase 5b マルチシード | phase5_openfast_shm/openfast_cases/results/del_matrix_ms.csv | DELマトリクス（240ケース・標準Rainflow・mean/std/CV） |
| Phase 5b マルチシード | phase5_openfast_shm/openfast_cases/results/del_single_rainflow_comparison.csv | 標準vs簡易Rainflow比較（平均誤差42%） |
| Phase 5b 長期DEL | phase5_openfast_shm/openfast_cases/results/lifetime_del_stage2.csv | Weibull重み付き長期DEL（TIビン別） |
| Phase 5b 長期DEL | phase5_openfast_shm/openfast_cases/results/lifetime_del_stage3.csv | V-TI同時分布長期DEL（IECクラス別） |
| Phase 5b 長期DEL | phase5_openfast_shm/openfast_cases/results/lifetime_del_analysis.png | 長期DEL可視化 |
| Phase 5 | docs/simpsons_paradox.png | TI vs DEL Simpson's Paradox 補助図 |
| Phase 6 | results/del_comparison_dlc12_vs_dlc13.csv | DLC 1.2 vs DLC 1.3 比較表 |
| Phase 6 | results/del_comparison_dlc12_vs_dlc13.png | DLC 1.3 vs 1.2 DEL比率図 |
| Phase H | phase3_scada/phase3_penmanshiel.py | Penmanshiel SCADA解析パイプライン |
| Phase H | phase3_scada/penmanshiel_monthly_del.csv | 月次DEL推定値（全タービン） |
| Phase H | phase3_scada/penmanshiel_ti_analysis.png | TI分布・DEL月次推移図 |
| Phase I | phase5_openfast_shm/openfast_cases/results/del_matrix_mm82.csv | MM82 DELマトリクス（240ケース） |
| Phase I | phase5_openfast_shm/openfast_cases/results/phase4_weights_mm82.json | MM82較正重み（w_V=0.725, w_TI=0.275） |
| Phase I | phase5_openfast_shm/openfast_cases/template_mm82/ | MM82スケーリングモデルテンプレート |
| Phase J | phase3_scada/penmanshiel_power_curve_fleet.png | フリートパワーカーブ比較図 |
| Phase J | phase3_scada/penmanshiel_performance_summary.csv | 台間性能サマリー |
| Phase K | phase3_scada/longitudinal_cp_trend.png | Cp_max 経年トレンド図 |
| Phase K | phase3_scada/longitudinal_annual_summary.csv | 年次パワーカーブサマリー |
| Phase L | phase3_scada/phase_L_longitudinal_del.py | 縦断DEL算出スクリプト |
| Phase L | phase3_scada/longitudinal_del_T01.csv | 月次DEL集計（T01, 2016-2021） |
| Phase L | phase3_scada/longitudinal_del_trend.png | 年次DELトレンド図 |
| Phase M | phase5_openfast_shm/openfast_cases/results/peak_loads_dlc21.csv | DLC 2.1 ピーク荷重 |
| Phase M | phase5_openfast_shm/openfast_cases/results/dlc21_vs_dlc12.csv | DLC 2.1 vs DLC 1.2 対比表 |
| Phase N | phase5_openfast_shm/openfast_cases/results/peak_loads_dlc22.csv | DLC 2.2 ピーク荷重 |
| Phase N | phase5_openfast_shm/openfast_cases/results/dlc22_vs_dlc21.csv | DLC 2.2 vs DLC 2.1 対比表 |
| 全体 | docs/research_roadmap.md | フェーズ計画・進捗 |
| 全体 | docs/integrated_research_report.md | 本レポート |

---

## 11. 参考文献

1. Shihavuddin, A.S.M. et al. (2019): "Wind Turbine Surface Damage Detection by Deep Learning Aided Drone Inspection Analysis" — Energies, https://www.mdpi.com/1996-1073/12/4/676
2. Sutherland, H.J. (1999): "On the Fatigue Analysis of Wind Turbines" — Sandia SAND99-0089
3. IEC 61400-1 Ed.4 (2019): "Wind energy generation systems — Design requirements"
4. Malik, A. & Bak, C. (2025): "Aerodynamic impact of leading edge erosion on wind turbine blades" — Wind Energy Science, DOI: 10.5194/wes-10-227-2025
5. DNV GL ST-0376 (2015): "Rotor Blades for Wind Turbines"
6. Jonkman, J.M. et al. (2009): "Definition of a 5-MW Reference Wind Turbine for Offshore System Development" — NREL/TP-500-38060
7. ROSCO (v2.10.1): "Reference OpenSource Controller for Wind Turbines" — NREL, github.com/NREL/ROSCO
8. ASTM E1049-85 (2017): "Standard Practices for Cycle Counting in Fatigue Analysis" — ASTM International
9. Hayman, G.J. (2012): "MLife Theory Manual for Version 1.00" — NREL/TP-5000-55799（Rainflow/DEL計算の実装参考）
10. Brøndsted, P. & Nijssen, R.P.L. (eds.) (2013): "Advances in Wind Turbine Blade Design and Materials" — Woodhead Publishing（GFRP疲労特性）
11. Toft, H.S. et al. (2016): "Assessment of wind turbine structural integrity using response surface methodology" — Engineering Structures（構造信頼性・長期荷重評価）
12. Natarajan, A. (2014): "Damage equivalent load synthesis and stochastic extrapolation for wind turbine fatigue design" — Wind Energy（長期DEL・Weibull重み付け）
13. Bak, C. et al. (2013): "Light Rotor: The 10-MW reference wind turbine" — EWEA 2012 Proceedings（ブレード質量スケーリング則 λ^2.3）
14. IEC 61400-1 Ed.4 (2019): §7.4 DLC 2.1/2.2 — フォルト荷重ケース（グリッド喪失・ピッチ固着）
15. Penmanshiel Wind Farm SCADA Dataset (2022): Zenodo DOI: 10.5281/zenodo.5946808（CC-BY 4.0, Senvion MM82, 14台, 2016-2021）
16. Senvion SE: "MM82 2.05 MW Technical Specifications"（定格出力2,050kW, ロータ径82m, ハブ高59m）

---

## 12. Phase 6: DLC 1.3（ETM）補助確認

**完了日**: 2026-04-03

### 12.1 設定

IEC 61400-1 Ed.4 DLC 1.3（Extreme Turbulence Model）: 8風速×6シード=48ケース。DLC 1.2との疲労荷重増分を定量化することが目的。

### 12.2 DLC 1.3 DEL結果（標準Rainflow, 6シード平均）

| V (m/s) | DEL_1.3 (kN-m) | CV (%) |
|---|---|---|
| 4  | 6,490 | 7.1 |
| 6  | 9,801 | 10.8 |
| 8  | 12,435 | 4.9 |
| 10 | 13,587 | 8.6 |
| 12 | 16,046 | 8.3 |
| 14 | 16,490 | 10.8 |
| 16 | 16,300 | 7.8 |
| 18 | 16,996 | 4.0 |

### 12.3 DLC 1.3 vs DLC 1.2 比率

| V (m/s) | DLC1.3 / DLC1.2(TI=14%) | DLC1.3 / DLC1.2(TI=8%) |
|---|---|---|
| 4  | **×4.2** | ×6.7 |
| 6  | **×3.2** | ×5.6 |
| 8  | **×2.3** | ×3.6 |
| 10 | **×1.9** | ×2.9 |
| 12 | **×1.8** | ×2.6 |
| 14 | **×1.7** | ×2.3 |
| 16 | **×1.5** | ×2.1 |
| 18 | **×1.4** | ×2.0 |

### 12.4 解釈

- DLC 1.3（ETM）はDLC 1.2（NTM, TI=14%）の**1.4〜4.2倍のDEL**を生成する
- 低風速（V=4〜6 m/s）で比率が最大（×3〜4以上）: ETMの乱流強度がNTMを大幅に上回る低速域での影響
- 高風速（V≥14 m/s）では比率が縮小（×1.4〜1.7）: ピッチ制御による荷重制限が効いて差が減少
- **疲労設計の観点**: DLC 1.3はDLC 1.2より常に支配的であり、疲労寿命の決定ケースはDLC 1.3であることが多い（ただし出現確率が低いため長期寄与は別途評価が必要）

**成果物**:
- `results/del_comparison_dlc12_vs_dlc13.csv`
- `results/del_comparison_dlc12_vs_dlc13.png`

---

---

## 13. Phase H: Penmanshiel SCADA による Phase 3 置き換え

**完了日**: 2026-04-03

### 13.1 背景・動機

Phase 3bまでは Kaggle Wind Turbine SCADA（出所不明・単一タービン）を使用していた。
主な問題点:
- TI計算が風速ビン内σ/μ 近似（IEC非準拠）
- 算出TI ~0.03〜0.04 は陸上サイトとして低すぎる（疑義あり）
- タービン型式・設置場所が不明

### 13.2 Penmanshiel データセット

| 項目 | 内容 |
|---|---|
| データソース | Zenodo DOI: 10.5281/zenodo.5946808 (CC-BY 4.0) |
| タービン数 | 14台（Senvion MM82, 2.05 MW, D=82m, hub=59m） |
| 対象年 | 2020年（本研究では T01-T07 使用） |
| 時間分解能 | 10分間平均 |
| 風速標準偏差列 | "Wind speed, Standard deviation (m/s)" — 直接提供 |
| 設置場所 | スコットランド・Penmanshiel Wind Farm (陸上) |
| 稼働開始 | 2016年9月 |

### 13.3 TI直接計測（方法論の改善）

| 方法 | Kaggle Phase 3b | Penmanshiel Phase H |
|---|---|---|
| TI計算式 | bin内 σ(V_bin) / μ(V_bin) | σ_10min / V_10min（各レコード） |
| IEC 61400-1準拠 | 近似（bin幅1m/s）| 完全準拠（10分値直接） |
| 算出TI 中央値 | ~0.035（疑義あり）| 0.133〜0.144 |
| サイト特性との整合 | 不明 | 陸上スコットランドとして妥当 |

**解釈（仮説）**: Kaggle SCADAのbin近似は「ビン内のレコード散らばり」を測っており、
10分間の真の乱流強度ではない。月次データ点数が少ない場合にさらに不安定になる。
Penmanshielの直接計測値（中央値 0.133〜0.144）は陸上オンショアサイトとして妥当な範囲。

### 13.4 月次DEL推定結果（Penmanshiel 2020）

5台の全年データ（T01, T02, T04, T05, T06）の代表値:

| 月 | V_mean (m/s) | TI_median | DEL_est (kN-m) |
|---|---|---|---|
| 1月 | 9.9〜10.3 | 0.144〜0.155 | 7,200〜7,540 |
| 2月 | 11.3〜11.9 | 0.145〜0.157 | 8,720〜9,019 ← ピーク |
| 3月 | 9.4〜9.6 | 0.135〜0.144 | 6,400〜6,760 |
| 4月 | 6.5〜6.8 | 0.135〜0.144 | 3,750〜3,970 |
| 5月 | 7.2〜7.5 | 0.134〜0.145 | 4,640〜4,860 |
| 6月 | 8.2〜8.3 | 0.128〜0.139 | 5,200〜5,730 |
| 7月 | 6.8〜7.3 | 0.135〜0.150 | 4,270〜4,450 |
| 8月 | 7.2〜7.5 | 0.129〜0.138 | 4,220〜4,640 |
| 9月 | 7.8〜8.1 | 0.136〜0.149 | 5,200〜5,620 |
| 10月 | 8.0〜8.3 | 0.118〜0.127 | 4,740〜4,990 |
| 11月 | 8.7〜9.1 | 0.128〜0.138 | 5,780〜5,960 |
| 12月 | 8.6〜8.8 | 0.119〜0.126 | 5,200〜5,420 |

**年間平均**: 5,500〜5,700 kN-m（T01-T06 平均、**NREL 5MW マトリクス基準**）  
**ピーク月**: 2月（冬季北海低気圧 — 8,720〜9,019 kN-m）  
**最低月**: 4月（春季小康 — 3,750〜3,970 kN-m）

> **注**: 上記 DEL は NREL 5MW マトリクスによる推定値。Phase I（§16）で構築した MM82 固有マトリクスによる再推定では **年間平均 1,497〜1,742 kN·m**（§16.6 参照）。以降の定量的議論では MM82 基準値を使用する。

### 13.5 DEL値の解釈上の注意点

| 比較 | Kaggle Phase 3b | Penmanshiel Phase H | Penmanshiel（MM82較正後, §16.6） |
|---|---|---|---|
| タービン | 不明 | Senvion MM82 (2.05 MW) | 同左 |
| DEL matrix | NREL 5MW | NREL 5MW（転用） | **MM82（機種適合）** |
| 絶対値の信頼性 | 低（型式不一致 + TI不正確）| 中（TI正確だが機種不一致） | **高（TI正確 + 機種適合）** |
| 相対比較 | 月次傾向のみ有効 | 月次・季節・機台間比較有効 | 同左 |
| 年間平均DEL | 1,566 kN-m | 5,500〜5,700 kN-m | **1,497〜1,742 kN·m** |

**重要**: NREL 5MW 基準の Penmanshiel DEL（5,500〜5,700 kN-m）と MM82 基準値（1,497〜1,742 kN·m）の比率 ≈ 0.28 は、理論スケーリング比（R_MM82/R_NREL）³ = 0.276 と整合的であり、スケーリング手法の妥当性を裏付ける。

### 13.6 Low-TI拡張マトリクスとの関係

Penmanshielサイトの実測TI（5th–95th pct: 0.063〜0.220）は、
Low-TI拡張（TI=0.02/0.04/0.06追加）の有効範囲（≥0.02）を完全にカバーしている。
0.04以下のレコードは0〜0.7%のみ。

これは重要な知見: **Low-TI拡張はKaggle SCADAのために必要だったが、
現実的な陸上サイト（Penmanshiel）では元のDELマトリクス（TI_min=0.08）でほぼカバー可能。**
すなわち、KaggleのTI（~0.035）が現実を反映していなかった可能性がある。

### 13.7 成果物

- `data/penmanshiel/Penmanshiel_WT_static.csv` — タービン諸元
- `data/penmanshiel/Penmanshiel_WT_dataSignalMapping.xlsx` — 信号マッピング
- `data/penmanshiel/scada_2020/` — 2020年SCADA（T01-T07, T11）
- `phase3_scada/phase3_penmanshiel.py` — 解析パイプライン
- `phase3_scada/penmanshiel_monthly_del.csv` — 月次DEL推定値（全タービン）
- `phase3_scada/penmanshiel_ti_analysis.png` — TI分布・DEL月次推移図
- `phase3_scada/penmanshiel_summary.md` — サマリーレポート

---

## 14. Phase J: パワーカーブ分析（台間比較）

**完了日**: 2026-04-03

### 14.1 概要

Penmanshiel 2020（T01-T06 全年）のパワーカーブをIEC 61400-12-1準拠で構築し、台間比較を実施。

### 14.2 結果

| タービン | V_mean (m/s) | Cp_max | AEP推定 (MWh) | フリート比 |
|---|---|---|---|---|
| T01 | 7.62 | **0.4513** | 6,506 | +4.5% |
| T02 | 7.41 | 0.4454 | 6,113 | -1.8% |
| T04 | 7.45 | **0.4514** | 6,381 | +2.5% |
| T05 | 7.32 | 0.4441 | 6,010 | **-3.5%** ← |
| T06 | 7.30 | 0.4471 | 6,129 | -1.6% |

- Cp_maxピーク風速: 全台 V=8.8 m/s で一致（設計点正常）
- T05が最低AEP・最低Cp_max。ただし風況差（V_meanが0.3 m/s低い）が主因の可能性あり
- AEP差最大6%（T01 vs T05）はほぼ風況差で説明可能

### 14.3 成果物

- `phase3_scada/penmanshiel_power_curves.csv`
- `phase3_scada/penmanshiel_power_curve_fleet.png`
- `phase3_scada/penmanshiel_cp_curve.png`
- `phase3_scada/penmanshiel_performance_summary.csv`

---

## 15. Phase K: 縦断パワーカーブ分析（2016-2021）

**完了日**: 2026-04-03

### 15.1 概要

T01を基準タービンとして、2016-2021の6年間にわたるCp_max・AEPの経年変化を追跡。

| 年 | 対象月数 | V_mean (m/s) | Cp_max | AEP推定 (MWh) | 備考 |
|---|---|---|---|---|---|
| 2016 | 7 | 6.98 | 0.4121 | 4,987 | 部分年（6-12月） |
| 2017 | 12 | 7.74 | 0.4275 | 6,577 | 全年 |
| 2018 | 11 | 7.16 | 0.4429 | 5,822 | QC除去35%（異常多） |
| 2019 | 12 | 7.05 | 0.4502 | 5,635 | 全年 |
| 2020 | 12 | 7.62 | 0.4513 | 6,506 | 全年 |
| 2021 | 6 | 6.78 | 0.4536 | 5,215 | 部分年（1-6月） |

### 15.2 主要発見と解釈

**Cp_max の経年変化**（全年データのみ: 2017-2020）:
- 2017: 0.4275 → 2020: 0.4513 (+0.024)
- 方向は「改善」方向 → エロージョン劣化（Cp低下）は確認できない
- **考えられる解釈**:
  1. **2018 QC異常（35%除去）**: 2018の低Cp（0.4429）はカーテイルメント/メンテ期間の影響かもしれない
  2. **制御ソフトウェア更新**: Senvion MM82はソフトウェア最適化により性能が向上することがある
  3. **エロージョンの影響が統計的ノイズの中に埋もれている**: 1-2%のCp変化は年間風況差で隠れる
  4. **2016が過渡期**: 稼働初期（2016年）は最適化されていない → 以後に改善

**重要な限界**:
- 年ごとの平均風速差（6.98〜7.74 m/s）がAEP変動の主因であり、空力性能差（Cp）は区別が難しい
- 真の劣化検出には「同一風況条件での比較（正規化パワー曲線）」が必要 → Phase I（MM82モデル）への動機
- 2016は稼働開始年（初期性能の基準として使いにくい）

### 15.3 2018の異常

QC除去率が35%（他年は1-20%）。2018年は異常に多いカーテイルメントまたはダウンタイムを示唆。
実際のO&M記録がなければ断言不可（仮説）。

### 15.4 成果物

- `phase3_scada/longitudinal_power_curves.csv`
- `phase3_scada/longitudinal_annual_summary.csv`
- `phase3_scada/longitudinal_power_curves.png`
- `phase3_scada/longitudinal_cp_trend.png`

---

## 16. Phase I: Senvion MM82 スケーリング済み OpenFAST モデル

### 16.1 問題の所在

Phase H（Penmanshiel SCADA）で取得したDEL推定値はNREL 5MW参照タービン（R=63m, P=5MW）のDELマトリクスに基づく。
Penmanshielの実機はSenvion MM82（R=41m, P=2050kW）であり、**絶対DEL値の機種間比較は不可**（ローター径・パワークラスが異なる）。
この「機種不一致」を解消するため、MM82にスケーリングしたOpenFASTモデルを構築し、
MM82固有のDELマトリクスを生成する。

### 16.2 スケーリング手法

NREL 5MW参照タービンの構造データを幾何スケーリングにより変換する。

**スケーリング係数**:
| 対象 | 係数 | 値 |
|------|------|-----|
| ブレード/ロータ | λ_R = 41/63 | 0.651 |
| タワー/ハブ高さ | λ_H = 59/87.6 | 0.674 |

**ブレード構造プロパティ**:
| 物理量 | スケーリング則 | 係数 |
|--------|--------------|------|
| BMassDen (kg/m) | λ_R^2.3 | ×0.372 |
| FlpStff / EdgStff (Nm²) | λ_R^4 | ×0.179 |

*λ_R^2.3: 経験的ブレード質量スケーリング則（Bak et al.）; λ_R^4: 断面二次モーメントの幾何スケーリング*

**タワー構造プロパティ**:
| 物理量 | スケーリング則 | 係数 |
|--------|--------------|------|
| TMassDen (kg/m) | λ_H^2 | ×0.454 |
| TwFAStif / TwSSStif (Nm²) | λ_H^4 | ×0.206 |

**ElastoDyn 主要パラメータ（MM82）**:
| パラメータ | NREL 5MW | MM82 |
|-----------|---------|------|
| TipRad | 63 m | 41 m |
| TowerHt | 87.6 m | 59 m |
| RotSpeed (rated) | 12.1 RPM | 17.1 RPM |
| GBRatio | 97 | 105 |
| NacMass | 240,000 kg | 65,000 kg |
| HubMass | 56,780 kg | 14,000 kg |

**ROSCO DISCON.IN 定格条件更新**:
| パラメータ | NREL 5MW | MM82 |
|-----------|---------|------|
| PC_RefSpd / VS_RefSpd | 122.91 rad/s | 188.02 rad/s |
| VS_RtPwr | 5,000,000 W | 2,050,000 W |
| VS_RtTq | 43,094 Nm | 11,550 Nm |
| VS_Rgn2K | 2.311 | 0.213 |
| WE_BladeRadius | 63 m | 41 m |
| WE_GearboxRatio | 97 | 105 |

**注記**: 翼型ポーラー（Cylinder/DU/NACA）はNREL 5MW翼型をプロキシとして使用（Senvion MM82の翼型データは非公開）。
モードシェイプ多項式係数は非次元形状を記述するため変更なし。

### 16.3 検証結果（単一ケース）

検証ケース：V=10 m/s, TI=0.14, Seed 1（MM82 TurbSim HH=59m）

| 指標 | 値 |
|------|-----|
| RootMyb1 信号 平均 | 2,013.4 kN-m |
| RootMyb1 信号 標準偏差 | 257.6 kN-m |
| DEL（ASTM Rainflow, m=10） | 1,849.6 kN-m |
| NREL 5MW 同条件 DEL | 7,155.5 kN-m |
| **比率 MM82/NREL5MW** | **0.258** |
| 理論予測値 (R_MM82/R_NREL)^3 | 0.276 |
| 理論誤差 | 6.5% |

DEL比率の理論予測との誤差6.5%は、スケーリング近似と単一シードの変動の範囲内であり、**モデルは物理的に妥当**と判断する。

### 16.4 シミュレーション結果（2026-04-04 完了）

- **グリッド**: V=[4,6,8,10,12,14,16,18] m/s × TI=[0.08,0.12,0.14,0.16,0.20] × 6 Seed = **240ケース**
- **TurbSim**: HH=59m, GridSize=100m×100m（D=82m をカバー）
- **有効グリッド点**: 40/40（全条件で6シード平均が取得できた）
- **DEL範囲**: 214.9〜4,046.1 kN·m（V=4/TI=0.08 → V=18/TI=0.20）
- **CV平均**: 6.1%（シード間再現性。NREL 5MWマルチシード時と同等）

#### DEL マトリクス（kN·m, MM82プロキシ）

| V \ TI | 0.08 | 0.12 | 0.14 | 0.16 | 0.20 |
|:---:|---:|---:|---:|---:|---:|
| 4 | 215 | 295 | 383 | 390 | 484 |
| 6 | 570 | 771 | 817 | 1,017 | 1,148 |
| 8 | 1,016 | 1,311 | 1,562 | 1,763 | 2,030 |
| 10 | 1,201 | 1,609 | 1,780 | 1,990 | 2,359 |
| 12 | 1,562 | 2,002 | 2,352 | 2,458 | 3,014 |
| 14 | 1,938 | 2,344 | 2,538 | 2,830 | 3,349 |
| 16 | 2,089 | 2,604 | 2,904 | 3,178 | 3,711 |
| 18 | 2,215 | 2,822 | 3,090 | 3,439 | 4,046 |

### 16.5 MM82 DEL matrix による W_V/W_TI 再較正

MM82 DELマトリクスで LinearRegression（正値制約・切片なし）を再実行した結果：

| | NREL 5MW（旧） | MM82（新） |
|---|:---:|:---:|
| **w_V** | 0.810 | **0.725** |
| **w_TI** | 0.190 | **0.275** |
| R² | 0.926 | **0.943** |
| Pearson r | 0.978 | 0.976 |

**解釈（仮説）**: MM82 の方が w_TI が高くなった。小型機（R=41m）は大型機（R=63m）に比べてローター面内の乱流スケールが相対的に大きくなるため、TIの影響が強く現れる可能性がある。ただし翼型プロキシ使用の不確実性もあり、確定結論ではない。

### 16.6 Penmanshiel DEL 推定（MM82較正後）

| タービン | 年間平均 DEL (kN·m) |
|:---:|---:|
| T01 | 1,503 |
| T02 | 1,526 |
| T04 | 1,497 |
| T05 | 1,539 |
| T06 | 1,498 |
| T07 | 1,559 |
| T11 | 1,742 |
| **全体平均** | **1,552** |

ピーク: 2月（冬季強風、T01で2,356 kN·m）。旧NREL 5MW基準値（5,500〜5,700 kN·m）との比率≈0.28 は理論スケーリング（0.258〜0.276）と整合的。

### 16.5 成果物

- `phase5_openfast_shm/openfast_cases/template_mm82/` — MM82 テンプレートファイル群
- `phase5_openfast_shm/openfast_cases/scripts/mm82_00_create_model.py` — スケーリングモデル生成
- `phase5_openfast_shm/openfast_cases/scripts/mm82_01_gen_turbsim.py` — TurbSim入力生成
- `phase5_openfast_shm/openfast_cases/scripts/mm82_02_run_turbsim.py` — TurbSim実行
- `phase5_openfast_shm/openfast_cases/scripts/mm82_03_gen_openfast.py` — OpenFASTケース生成
- `phase5_openfast_shm/openfast_cases/scripts/mm82_04_run_openfast.py` — OpenFAST実行
- `phase5_openfast_shm/openfast_cases/scripts/mm82_05_extract_del.py` — DEL抽出
- `phase5_openfast_shm/openfast_cases/results/del_matrix_mm82.csv` — MM82 DELマトリクス（240ケース完了）
- `phase5_openfast_shm/openfast_cases/results/phase4_weights_mm82.json` — MM82較正重み（w_V=0.725, w_TI=0.275）

---

## 17. Phase L: Penmanshiel T01 縦断 DEL トレンド（2016-2021）

### 17.1 目的

Phase K（縦断パワーカーブ）で「Cp_max は 2017→2020 増加傾向（劣化なし）」が確認された。
Phase L では同期間の疲労荷重（DEL推定）を追跡し、「荷重増加が風況変動によるものか、機体状態変化によるものか」を確認する。

### 17.2 結果

| 年 | 期間 | V_mean (m/s) | TI_med | DEL年平均 (kN·m) |
|:---:|---|:---:|:---:|---:|
| 2016 | 2016-06〜12（半年） | 7.73 | 0.115 | 1,155 |
| 2017 | 通年 | 8.32 | 0.119 | 1,325 |
| 2018 | 通年 | 8.18 | 0.128 | 1,346 |
| 2019 | 通年 | 8.08 | 0.130 | 1,351 |
| 2020 | 通年 | 8.66 | 0.133 | 1,507 |
| 2021 | 〜2021-06（半年） | 7.96 | 0.133 | 1,340 |

### 17.3 考察

**DEL増加は風況の年変動が主因（データ観察）:**
- 2017→2020 の DEL 増加（+182 kN·m, +13.7%）は V_mean 増加（8.32→8.66 m/s）と TI_med 増加（0.119→0.133）に連動
- 2021 は V が下がると DEL も 1,325 水準に戻る → 機体状態の変化ではなく風況変動で説明できる

**Phase K との整合:**
- Phase K: Cp_max は 2017→2020 で 0.4275→0.4513 と増加（劣化なし）
- Phase L: DEL は風況依存で増加しており、ブレード劣化に由来する荷重増加ではない

**仮説（要検証）**: TI_med の経年増加（0.119→0.133）が DEL 増加に寄与している可能性。
サイト周辺の植生変化・フロント列タービンの追加等が考えられるが、気象記録との比較が必要。

### 17.4 成果物

- `phase3_scada/phase_L_longitudinal_del.py` — 縦断DEL算出スクリプト
- `phase3_scada/longitudinal_del_T01.csv` — 月次DEL集計（2016-2021）
- `phase3_scada/longitudinal_del_trend.png` — 年次DELトレンド図

---

## 18. Phase M: DLC 2.1 グリッド喪失 → 緊急停止 終局荷重解析

### 18.1 目的

IEC 61400-1:3 §7.4 DLC 2.1（フォルト荷重ケース）に従い、グリッド喪失時の緊急停止過渡応答を解析する。DLC 1.2（疲労荷重）と異なり、DLC 2.1 は終局荷重（最大ピーク）を評価する。

### 18.2 解析条件

- **フォルト**: t=300s にグリッド喪失
  - 発電機遮断（TimGenOf=300s）
  - ブレード緊急ピッチ（TPitManS=300s, PitManRat=8 deg/s → BlPitchF=90°）
  - HSS ブレーキ展開（THSSBrDp=300s, HSSBrTqF=8,154 N-m）
- **風況**: NTM（DLC 1.2 と同一 BTS 再利用）, TI=0.14
- **条件**: V=[8,10,12,14,16,18] m/s × 6 seeds = **36 ケース**
- **評価**: RootMyb1 絶対値ピーク（フォルト前 t=60〜300s vs フォルト後 t=300〜600s）

### 18.3 結果

| V (m/s) | フォルト前 max (kN·m) | フォルト後 max (kN·m) | 比率 | DLC1.2 DEL (kN·m) |
|:---:|---:|---:|:---:|---:|
| 8 | 2,483 | 1,958 | 0.85 | 1,562 |
| 10 | 2,850 | 2,348 | 0.87 | 1,780 |
| 12 | 3,116 | 2,436 | 0.82 | 2,352 |
| 14 | 2,881 | 2,209 | 0.81 | 2,538 |
| 16 | 2,855 | 2,044 | 0.77 | 2,904 |
| 18 | 2,643 | 1,377 | 0.54 | 3,090 |

### 18.4 考察

**フォルト後ピーク < フォルト前ピーク（データ観察）:**
- 比率がすべて 1.0 未満 → 緊急ピッチによるブレード荷重除荷が有効に機能している
- 高風速ほど比率が低い（V=18m/s で 0.54）→ 高風速ほど停止後の荷重低減効果が大きい
- V=12m/s でフォルト前ピーク最大（3,116 kN·m）→ 定格付近が最も荷重変動が大きい

**DEL（疲労荷重）との関係（データ観察）:**
- DLC 1.2 DEL は高風速ほど高い（V依存）
- DLC 2.1 ピークは V=12〜14 m/s 付近で最大 → 疲労と終局の支配条件が異なる
- 終局設計は「定格付近の過渡応答」、疲労設計は「高風速の累積」が支配的

**仮説（要検証）**: フォルト後のピーク荷重が DLC 1.2 の瞬時最大値（DEL ではなくピーク）と比較すると、DLC 2.1 が支配的になる可能性がある。ただし本解析は翼型プロキシ使用のため絶対値は参考値。

### 18.5 成果物

- `phase5_openfast_shm/openfast_cases/scripts/dlc21_01_gen_cases.py` — ケース生成
- `phase5_openfast_shm/openfast_cases/scripts/dlc21_02_run_openfast.py` — OpenFAST実行
- `phase5_openfast_shm/openfast_cases/scripts/dlc21_03_extract_peaks.py` — ピーク抽出
- `phase5_openfast_shm/openfast_cases/cases_dlc21/` — 36ケースディレクトリ
- `phase5_openfast_shm/openfast_cases/results/peak_loads_dlc21.csv` — ピーク荷重CSV
- `phase5_openfast_shm/openfast_cases/results/dlc21_vs_dlc12.csv` — DLC対比表

---

## 19. Phase N: DLC 2.2 ピッチ固着 → 非対称緊急停止 終局荷重解析

### 19.1 目的

IEC 61400-1:3 DLC 2.2 として、1 枚のブレードのピッチ機構が固着した状態での緊急停止を解析する。DLC 2.1（全ブレード正常）との比較で非対称荷重の増大を定量化する。

### 19.2 解析条件

- **フォルト**: t=300s にグリッド喪失
  - **Blade 1**: ピッチ固着（フォルト時の角度を維持）
  - **Blade 2/3**: 正常緊急ピッチ（8 deg/s → 90°）
  - 発電機遮断・HSS ブレーキ展開（DLC 2.1 と同条件）
- **風況**: NTM, TI=0.14, V=8〜18 m/s（DLC 2.1 と同一 BTS）
- **ケース数**: 36 ケース（6V × 6 seeds）

### 19.3 結果

| V (m/s) | フォルト前 max | フォルト後 max | 比率 | DLC2.1後ピーク | **増幅率** |
|:---:|---:|---:|:---:|---:|:---:|
| 8 | 2,483 | 1,955 | 0.85 | 1,958 | ×1.00 |
| 10 | 2,850 | 2,602 | 0.96 | 2,348 | ×1.11 |
| 12 | 3,116 | 2,502 | 0.84 | 2,436 | ×1.03 |
| 14 | 2,881 | 2,346 | 0.86 | 2,209 | ×1.06 |
| **16** | 2,855 | **2,885** | **1.09** | 2,044 | **×1.41** |
| **18** | 2,643 | **2,875** | **1.13** | 1,377 | **×2.09** |

（単位: kN·m）

### 19.4 考察

**高風速でピッチ固着荷重が急増（データ観察）:**
- V=8〜14 m/s: DLC 2.2 ≈ DLC 2.1（増幅率 1.00〜1.11）
- V=16 m/s: ×1.41、V=18 m/s: ×2.09 と急増
- 定格以上では Blade 2/3 が 90° フェザーして揚力を失う一方、固着した Blade 1 は風を受け続けるため、非対称荷重が急激に増大する

**比率 > 1.0 の意味（データ観察）:**
- V=16,18 m/s では `フォルト後 > フォルト前` になっている（比率 1.09, 1.13）
- DLC 2.1 では全ケース比率 < 1.0 だったが、ピッチ固着では高風速域で逆転する
- これが DLC 2.2 が設計上の支配ケースになりうる根拠

**仮説（要検証）**: ピッチ固着の影響は定格風速（≈13 m/s）を境に急変する可能性がある。定格以上では DISCON コントローラが正常ブレードをフェザーしようとする動作が非対称荷重を増幅させる機序が考えられる。

### 19.5 DLC 2.1/2.2 総括

| 評価項目 | DLC 2.1（全ブレード正常） | DLC 2.2（Blade 1 固着） |
|---|---|---|
| 最大フォルト後ピーク | 2,348 kN·m（V=10） | **2,885 kN·m（V=16,18）** |
| 比率 > 1.0 のケース | なし | V=16, V=18 |
| 支配風速域 | V=10〜12 m/s（定格付近） | **V=16〜18 m/s（定格以上）** |

### 19.6 成果物

- `phase5_openfast_shm/openfast_cases/scripts/dlc22_01_gen_cases.py` — ケース生成
- `phase5_openfast_shm/openfast_cases/scripts/dlc22_02_run_openfast.py` — OpenFAST実行
- `phase5_openfast_shm/openfast_cases/scripts/dlc22_03_extract_peaks.py` — ピーク抽出
- `phase5_openfast_shm/openfast_cases/results/peak_loads_dlc22.csv` — ピーク荷重CSV
- `phase5_openfast_shm/openfast_cases/results/dlc22_vs_dlc21.csv` — DLC 2.1/2.2 対比表

---

## 20. 結論

本研究は、風車ブレード劣化予測に必要な3つのデータソース（画像・SCADA・空力シミュレーション）を統合する研究基盤を、公開データのみを用いて段階的に構築した。全15フェーズ、合計600ケースのOpenFASTシミュレーションを含む体系的な解析を通じて、以下の主要成果を得た。

**方法論の確立:**
1. YOLOv8 による損傷検出・部位別リスクスコアリング（mAP@0.5 = 0.58）から、SCADA 疲労代理指標、OpenFAST DEL マトリクス、DLC フォルト荷重解析までを一貫して接続するパイプラインを構築した
2. NREL 5MW → MM82 幾何スケーリング（λ_R=0.651）により、参照タービンの DEL マトリクスを実機仕様に適合させる手法を実証した（理論予測との誤差 6.5%）
3. ASTM E1049 標準 Rainflow が簡易版に対し平均 42% 高い DEL を算出することを定量的に示し、高精度疲労評価における標準実装の必要性を確認した

**定量的知見:**
4. MM82 基準で Penmanshiel サイト（7台、2020年）の年間平均 DEL は 1,497〜1,742 kN·m。冬季（2月）にピークを示す明確な季節性が確認された
5. 6年間の縦断分析（T01, 2016-2021）では、DEL 増加（+13.7%）は風況変動が主因であり、Cp_max の劣化は観察されなかった
6. DLC 2.2（ピッチ固着）は高風速域（V≥16 m/s）で DLC 2.1 比 ×1.4〜2.1 の非対称荷重増大を示し、ピッチ冗長性のない機種では終局設計の支配ケースとなりうる

**今後の展望:**
本研究基盤は「劣化予測モデルの実証」ではなく、同一タービンでの実データ統合を見据えた**統合研究基盤の構築と方法論の検証**として位置づけられる。自社 O&M データ（点検画像・SCADA・補修記録）への差し替えにより、ブレード状態監視・補修計画最適化に直結する予測モデルへの発展が可能である。

---

*最終更新: 2026-04-04 (v3.0: 論文品質化・全フェーズ統合) | 著者: himin | 研究期間: 2026-03-31〜2026-04-04*
