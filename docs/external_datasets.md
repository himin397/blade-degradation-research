# 外部データセット（一覧 + 詳細分析 + 活用計画）

最終更新：2026-05-03（旧 `external_datasets_inventory.md`（2026-04-13）と `external_datasets_analysis.md`（2026-04-14）を統合）

このドキュメントは、ブレード劣化予測研究で使用するすべての外部データセットの一覧、入手済みデータの詳細分析、研究段階別の活用計画、浅井先生面談での確認事項を一元管理する。

---

## 1. 入手済みデータセット（一覧）

| データセット | 画像数 | 種類 | サイズ | ローカルパス | URL |
|---|---|---|---|---|---|
| **DTU/Nordtank**（研究使用中・主データ） | 559 | RGB ドローン、5クラス | ~2GB | `data/processed/yolo_dataset/` | https://data.mendeley.com/datasets/hd96prn3nc/2 |
| **WTBD** (Scientific Data 2026) | 1,065 | RGB ドローン、6クラス、1024×1024px、PASCAL VOC XML | 91MB | `data/external_datasets/WT blade defect dataset/` | DOI: 10.6084/m9.figshare.30210175 |
| **Blade30 part1** (blade 1-15) | 1,210（※要確認） | RGB ドローン、5400×3600px、JSON+マスク | 2.2GB | `data/external_datasets/3_blade_1_15_with_labeldata/` | https://drive.google.com/file/d/1HbB4t9xV2oCgSSxR9hMEOU6v9qDfetmR |
| **Blade30 part2** (blade 16-30) | 1,394（※要確認） | RGB ドローン、5400×3600px、JSON+マスク | 2.6GB | `data/external_datasets/3_blade_16_30_with_labeldata/` | https://drive.google.com/file/d/1SwRdMzA7zCkNVlHuWvk8uK6eDToM0mUV |
| **CAI-SWTB** | 6,000 | RGB 小型風車、健全/損傷の2クラス | 182MB | `data/external_datasets/CAI-SWTB-Dataset/` | https://www.kaggle.com/datasets/mohammadshekaramiz/small-wind-turbine-blade-dataset-cai-swtb |
| **Small-WTB-Thermal** | 1,000 | RGB+熱画像マルチスペクトル、小型風車 | 22MB | `data/external_datasets/Small-WTB-Thermal1/` | https://github.com/MoShekaramiz/Small-WTB-Thermal1 |

**※注意：Blade30 の画像数について**
- 旧 inventory（2026-04-13）：part1/part2 各 ~650 枚（概算）
- 旧 analysis（2026-04-14）：part1: 1,210 枚、part2: 1,394 枚（合計 2,604 枚）
- 統合時点では analysis の数値（より詳細・新しい）を採用したが、ローカル実数の確認が望ましい。

---

## 2. 入手済みデータセットの詳細分析

### 2.1 DTU/Nordtank（主データ・研究使用中）

- Paper 1 の主データ（559枚、5クラス）
- 詳細は `paper1_blade_damage_detection.md` および `data_sources.md` を参照
- 強み：研究のベースライン、リスクスコア設計
- 弱み：単一タービン、限定クラス、経年情報なし

### 2.2 WTBD（Wind Turbine Blade Defect）

#### 基本情報
| 項目 | 値 |
|---|---|
| 画像数 | 1,065枚 |
| 画像サイズ | 1024×1024 px（固定） |
| アノテーション形式 | PASCAL VOC XML |
| クラス数 | 6 |
| train/val/test分割 | 既定義（CSV） |

#### クラス分布
| クラス | 件数 | 割合 |
|---|---|---|
| surface_injure | 412 | 26.0% |
| hide_craze | 342 | 21.6% |
| corrosion | 257 | 16.2% |
| craze | 257 | 16.2% |
| crack | 224 | 14.1% |
| **thunderstrike** | **92** | **5.8%** ← 最少 |
| 合計 | 1,584 | — |

#### DTUクラスとの対応（推定）
| DTU | WTBD | 対応度 |
|---|---|---|
| LE;ER（前縁エロージョン） | corrosion | 中 |
| LE;CR（前縁亀裂） | crack / craze | 高 |
| LR;DA（雷撃受雷部損傷） | thunderstrike | 高 |
| VG;MT（渦発生器欠損） | surface_injure? | 低 |
| SF;PO（表面穴） | surface_injure? | 低 |

**DTU と WTBD のクラス定義は完全一致しない**。クロス検証にはクラスマッピングの設計が必要。

#### 活用候補（卒論テーマ別）
| 卒論テーマ案 | 活用度 |
|---|---|
| **案A: 少数クラス問題** | ◎ DTU の LE;CR(1.6%) より WTBD の thunderstrike(5.8%) のほうが緩い。両方で検証可能 |
| **案B: クロスデータセット検証** | ◎ DTU で学習 → WTBD で評価が直接できる |

### 2.3 Blade30

#### 基本情報
| 項目 | 値 |
|---|---|
| 画像数 | part1 (Blade 1-15): 1,210枚、part2 (Blade 16-30): 1,394枚 |
| 総画像数 | **2,604枚（要再確認）** |
| 画像サイズ | 高解像度（推定5400×3600px） |
| アノテーション形式 | JSON + マスク画像（セグメンテーション用） |
| 特徴 | **30個の完全ブレード**に整理されており、ブレードIDが追跡可能 |

#### ディレクトリ構造
```
3_blade_1_15_with_labeldata/
├── Blade_1/
│   └── 1_1/
│       ├── 0_{uuid}.jpg         ← 画像
│       ├── 0_{uuid}.json        ← JSONアノテーション
│       └── mask/
│           └── 0_{uuid}.png     ← マスク画像
```

#### 独自の価値
- **ブレードIDが明示的**：DTU は「このブレードが誰か」がわからない。Blade30 は30ブレードの識別が可能
- **同一ブレード内の複数画像**：1つのブレードを異なる角度/部位から撮影した画像がある
- **セグメンテーションマスク付き**：物体検出（バウンディングボックス）より精密な損傷領域が記録されている

#### 活用候補
| 卒論テーマ案 | 活用度 |
|---|---|
| **案A: 少数クラス問題** | △ クラス別詳細が未確認。調査が必要 |
| **案B: クロスデータセット検証** | ○ 検証先の1つとして使える |
| **将来の修士・博士** | ◎ ブレードID追跡による経時変化研究の予備実験に最適 |

### 2.4 CAI-SWTB / Small-WTB-Thermal（補助）

- CAI-SWTB：小型風車の健全/損傷2クラス。スケール感が異なるため Paper 1 への直接適用は困難
- Small-WTB-Thermal：熱画像マルチスペクトルが特徴。将来の熱画像研究の予備データ

---

## 3. 未入手（将来候補）

### 画像系
| データセット | 内容 | URL | 優先度 | メモ |
|---|---|---|---|---|
| **DTU Risø Video** | 同じDTUタービンのドローン動画29本（DJI Mavic 2） | https://data.mendeley.com/datasets/6nzbdvjn87/1 | 高 | 静止画切り出しで学習データ増加可能 |
| **Wind Turbine Blade Surfaces** | ブレード表面画像 | https://data.mendeley.com/datasets/jrmm82m4mv/1 | 低 | 詳細未確認 |
| **Sandpaper Blade Benchmark** | SfM用表面粗さベンチマーク | https://data.mendeley.com/datasets/hcgcnm269w/2 | 低 | 3D再構成用。現スコープ外 |
| **SfM Image Setups** | ブレード断面の3D再構成用18セット | https://data.mendeley.com/datasets/fptxw8cynv/1 | 低 | 3D再構成用。現スコープ外 |

### 熱画像系
| データセット | 内容 | URL | 優先度 | メモ |
|---|---|---|---|---|
| **DTU Thermography** | パッシブサーモグラフィ、疲労負荷中の損傷検出 | https://data.mendeley.com/datasets/jmm33c6dny/1 | 中 | 2026-04-13時点でサーバー不調により DL 失敗 |

### 振動/SHM系
| データセット | 内容 | URL | 優先度 | メモ |
|---|---|---|---|---|
| **Fraunhofer LBF** | 750W風車の加速度計+気象データ、故障シナリオ付き | https://www.nature.com/articles/s41597-024-03934-5 | 中 | Paper 3の統合パイプラインへの入力候補 |
| **ETH Zurich SHM** | 疲労試験+ガイド波センシング | https://zenodo.org/records/13692213 | 低 | 実験室規模。現スコープ外 |
| **OSTI 振動データ** | エロージョン・亀裂・質量不均衡の振動データ | https://www.osti.gov/servlets/purl/1095939 | 低 | 振動ベース診断用 |

### SCADA系
| データセット | 内容 | URL | 優先度 | メモ |
|---|---|---|---|---|
| **Penmanshiel**（研究使用中） | MM82 14台、10分値、2016-2021 | DOI: 10.5281/zenodo.5946808 | — | 使用中 |
| **OpenWindSCADA** | 公開SCADAデータのキュレーションリスト | https://github.com/sltzgs/OpenWindSCADA | 中 | 他サイトのSCADAデータ候補を探すときに参照 |

---

## 4. 研究段階別の活用計画

| 段階 | 活用するデータ | 目的 |
|---|---|---|
| **現在（論文投稿準備）** | DTU + Penmanshiel のみ | Paper 1-3の完成 |
| **査読対応時** | WTBD | クロスデータセット検証（Limitation #5への対応） |
| **卒論（情報学）** | DTU + WTBD（直接活用可能） or DTU + Blade30 | 案A（少数クラス問題）/ 案B（クロスデータセット検証）のいずれか |
| **修士研究** | 自社 O&M データ（本命） + Blade30（予備検証） | 同一タービンの経年追跡 |
| **将来** | Fraunhofer LBF + OpenWindSCADA | 振動/SCADA統合の拡張 |

### 卒論テーマ別の使い分け（詳細は `thesis_topic_proposals.md` 参照）

**案A（少数クラス問題）を選ぶ場合**
- 主データ：DTU（LE;CR = 1.6%の極端な不均衡を扱う）
- 補助データ：WTBD（thunderstrike = 5.8%で緩やかな不均衡と比較）
- 追加の問い：「不均衡の程度による対処手法の効き方の違い」

**案B（クロスデータセット検証）を選ぶ場合**
- 主データ：DTU → WTBD（直接転移が可能）
- 補助データ：Blade30（セグメンテーション主体のため、物体検出タスクへの流用は要工夫）

**どちらの案でも共通**
- WTBD は直接活用可能（1,024×1024 px、VOC XML で既存 YOLO 学習パイプラインと親和性高い）
- Blade30 は修士以降の研究で価値が高い（ブレード ID 追跡）
- DTU + WTBD + Blade30 を全て使うと論文のスコープが膨らみすぎる。**卒論では1つに絞る**のが現実的。修士で広げる

---

## 5. 浅井先生面談での確認事項（2026年6月）

1. どちらの卒論テーマ案（A: 少数クラス / B: クロスデータセット）がより情報学として評価されるか
2. WTBD でのクロス検証を卒論に含めるべきか
3. Blade30（セグメンテーション）まで視野に入れるべきか
4. 自社 O&M データの利用可能性（守秘義務・共同研究契約）について研究室の方針

---

## 6. 関連ドキュメント
- 一次ソース台帳：`data_sources.md`（DTU・Penmanshiel 等の引用情報）
- Paper 1 ドラフト：`paper1_blade_damage_detection.md`
- 卒論テーマ案：`thesis_topic_proposals.md`
- 業界動向：`industry_landscape_2025.md`
