# 研究用語集（Glossary）

最終更新: 2026-04-05

---

## 風の物理

| 略語・用語 | 正式名称 | 意味 |
|---|---|---|
| V | Wind Speed | 風速（m/s）。通常は10分間平均値 |
| V̄ | Mean Wind Speed | 10分間の平均風速 |
| σ_V | Wind Speed Std. Dev. | 10分間の風速の標準偏差（揺らぎの大きさ） |
| TI | Turbulence Intensity | 乱流強度 = σ_V / V̄。風の揺らぎの激しさを表す無次元量 |
| Weibull分布 | Weibull Distribution | 風速の確率分布を表すモデル。弱〜中の風が多く、強い風は少ないが存在する形 |

## 風車の性能

| 略語・用語 | 正式名称 | 意味 |
|---|---|---|
| P | Power | 出力（W, kW） |
| ρ | Air Density | 空気密度（約1.225 kg/m³） |
| A | Swept Area | ローター掃引面積 = πR² |
| R | Rotor Radius | ローター半径（m） |
| Cp | Power Coefficient | パワー係数。風のエネルギーのうち電力に変換できる割合（0〜0.593） |
| Cp_max | Maximum Power Coefficient | Cpの最大値。タービンの性能指標。高いほど効率が良い |
| AEP | Annual Energy Production | 年間発電量（MWh/yr） |
| カットイン | Cut-in Wind Speed | 発電を開始する最低風速（通常3〜4 m/s） |
| 定格 | Rated Wind Speed | 定格出力に達する風速（通常11〜13 m/s） |
| カットアウト | Cut-out Wind Speed | 安全のため停止する風速（通常25 m/s） |

## 疲労・荷重

| 略語・用語 | 正式名称 | 意味 |
|---|---|---|
| DEL | Damage Equivalent Load | 疲労等価荷重。不規則な荷重履歴を「1つの等価振幅」に変換した値（kN·m） |
| Rainflow counting | Rainflow Cycle Counting | 不規則な荷重波形を「何回、どの振幅で繰り返したか」に分解する手法（ASTM E1049） |
| S-N曲線 | Stress-Number Curve | 応力振幅 vs 破壊までの繰り返し回数の関係曲線。Wöhler曲線とも呼ぶ |
| m | Wöhler Exponent | S-N曲線の傾き。材料特性。複合材では m=10 が一般的 |
| N_eq | Equivalent Number of Cycles | 等価繰り返し回数。DEL算出時の基準（通常 600s × 1Hz = 600回） |

## シミュレーション

| 略語・用語 | 正式名称 | 意味 |
|---|---|---|
| OpenFAST | Open-source Framework for Aeroelastic Simulation of Turbines | NRELが開発した風車の空力弾性シミュレーター |
| NREL | National Renewable Energy Laboratory | 米国国立再生可能エネルギー研究所 |
| DLC | Design Load Case | IEC 61400-1に基づく設計荷重ケース。風況条件の標準的な組み合わせ |
| DLC 1.2 | — | 通常発電条件。正常運転中の疲労荷重評価に使う |
| IEC 61400-1 | — | 風車の設計要件に関する国際規格 |
| λ_R | Rotor Scaling Ratio | ローター半径のスケーリング比。λ_R = R_target / R_reference |

## 画像検出

| 略語・用語 | 正式名称 | 意味 |
|---|---|---|
| YOLO | You Only Look Once | リアルタイム物体検出アルゴリズム。画像を一度見るだけで検出する1-stage型 |
| YOLOv8n | YOLOv8 nano | YOLOv8の最小モデル。軽量で高速 |
| BBox | Bounding Box | 検出された物体を囲む矩形 |
| IoU | Intersection over Union | 予測BBoxと正解BBoxの重なり度合い（0〜1） |
| AP | Average Precision | クラスごとのPrecision-Recall曲線の下の面積 |
| mAP | mean Average Precision | 全クラスAPの平均。検出性能の総合指標 |
| mAP@0.5 | — | IoU閾値0.5でのmAP |
| Precision | 適合率 | 検出したもののうち正解の割合 |
| Recall | 再現率 | 正解のうち検出できた割合 |

## 損傷クラス（Paper 1）

| 略語 | 意味 |
|---|---|
| LE;ER | Leading Edge Erosion（前縁エロージョン） |
| LE;CR | Leading Edge Crack（前縁亀裂） |
| SU;DA | Surface Damage（表面損傷） |
| LI;DA | Lightning Damage（雷撃損傷） |
| PB;DA | Paint/Coating Damage（塗装損傷） |

## リスクスコア・統合

| 略語・用語 | 正式名称 | 意味 |
|---|---|---|
| Tip / Mid / Root | — | ブレードのスパン方向の3領域。先端 / 中間 / 根元 |
| α, β | Integration Weights | 統合層の重み。画像リスク(α) と 荷重リスク(β) の相対重要度。未較正 |
| w_V, w_TI | DEL Calibration Weights | Module B内部の重み。DELに対する風速(w_V)とTI(w_TI)の相対寄与。較正済み |

## データソース

| 名称 | 内容 |
|---|---|
| DTU | デンマーク工科大学。公開ブレード点検画像の提供元（Nordtankタービン） |
| Penmanshiel | スコットランドのウィンドファーム。Senvion MM82 × 14基。公開SCADA（Zenodo） |
| MM82 | Senvion社製 2MW級タービン。ローター直径82m |
| NREL 5MW | NRELが定義した参照タービン。OpenFASTのベースモデル |

## 統計

| 略語・用語 | 意味 |
|---|---|
| R² | 決定係数。回帰モデルの当てはまりの良さ（0〜1） |
| Pearson r | ピアソン相関係数。線形相関の強さ（-1〜1） |
| Spearman r | スピアマン順位相関。単調関係の強さ（-1〜1） |
| p値 | 帰無仮説（相関なし等）が正しい場合にその結果が出る確率。小さいほど有意 |
