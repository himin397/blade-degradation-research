# 外部データセット一覧（2026-04-13時点）

## 入手済み

| データセット | 画像数 | 種類 | サイズ | ローカルパス | URL |
|---|---|---|---|---|---|
| **DTU/Nordtank**（研究使用中） | 559 | RGB ドローン、5クラス | ~2GB | `data/processed/yolo_dataset/` | https://data.mendeley.com/datasets/hd96prn3nc/2 |
| **WTBD** (Scientific Data 2026) | 1,065 | RGB ドローン、6クラス、1024×1024px、PASCAL VOC XML | 91MB | `data/external_datasets/WT blade defect dataset/` | DOI: 10.6084/m9.figshare.30210175 |
| **Blade30 part1** (blade 1-15) | ~650 | RGB ドローン、5400×3600px、アノテーション付き | 2.2GB | `data/external_datasets/3_blade_1_15_with_labeldata/` | https://drive.google.com/file/d/1HbB4t9xV2oCgSSxR9hMEOU6v9qDfetmR |
| **Blade30 part2** (blade 16-30) | ~650 | RGB ドローン、5400×3600px、アノテーション付き | 2.6GB | `data/external_datasets/3_blade_16_30_with_labeldata/` | https://drive.google.com/file/d/1SwRdMzA7zCkNVlHuWvk8uK6eDToM0mUV |
| **CAI-SWTB** | 6,000 | RGB 小型風車、健全/損傷の2クラス | 182MB | `data/external_datasets/CAI-SWTB-Dataset/` | https://www.kaggle.com/datasets/mohammadshekaramiz/small-wind-turbine-blade-dataset-cai-swtb |
| **Small-WTB-Thermal** | 1,000 | RGB+熱画像マルチスペクトル、小型風車 | 22MB | `data/external_datasets/Small-WTB-Thermal1/` | https://github.com/MoShekaramiz/Small-WTB-Thermal1 |

## 未入手（将来候補）

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
| **DTU Thermography** | パッシブサーモグラフィ、疲労負荷中の損傷検出 | https://data.mendeley.com/datasets/jmm33c6dny/1 | 中 | 2026-04-13時点でサーバー不調によりDL失敗 |

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

## 研究段階別の活用計画

| 段階 | 活用するデータ | 目的 |
|---|---|---|
| **現在（論文投稿準備）** | DTU + Penmanshiel のみ | Paper 1-3の完成 |
| **査読対応時** | WTBD | クロスデータセット検証（Limitation #5への対応） |
| **修士研究** | 自社O&Mデータ（本命） + Blade30（予備検証） | 同一タービンの経年追跡 |
| **将来** | Fraunhofer LBF + OpenWindSCADA | 振動/SCADA統合の拡張 |
