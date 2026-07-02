# データソース一覧

最終更新: 2026-03-31（**注意：2026-04 以降に追加された WTBD・Blade30・CAI-SWTB・Small-WTB-Thermal 等は本ファイルには未反映**）

## 凡例

- **種別**: 一次ソース / 二次ソース（原典あり）/ ツール
- 研究記録・引用には必ず一次ソースのURLを記載する

---

## 下書き注記（2026-05-03 追加・要 himinさん 判断）

**役割が `external_datasets.md` と重複する状態**になっています。Codex 独立レビューの指摘：
- `external_datasets.md`（2026-05-03 統合）は「実データ候補・ローカル入手状況・卒論への活用計画」を担当
- 本ファイル `data_sources.md` は 2026-03-31 時点の凡例・URL 集で、新規データセットが反映されていない

### 処置の選択肢（himinさん 判断）

| 選択肢 | 内容 | メリット | デメリット |
|---|---|---|---|
| **A. 役割分離** | 本ファイルを「**引用・一次ソース台帳**」（論文の References セクションで使う原典 URL・DOI 集）として再定義。データセットの入手状況・活用計画は `external_datasets.md` に集約 | 役割が明確、論文用と研究計画用を分離 | 一部内容を `external_datasets.md` から戻す必要あり |
| **B. 統合管理** | 本ファイルを更新して、`external_datasets.md` の内容を吸収。`external_datasets.md` を削除 | 単一管理 | せっかく統合した `external_datasets.md` を再構成する手戻り |
| **C. 当面そのまま** | 古い記述を残し、参照先として `external_datasets.md` を併記する | 工数小 | 重複が残る |

**Claude Code の所感**：選択肢 A が論文執筆時に最も使いやすい構成。Paper 1/2/3 の References を確認しながら、本ファイルを「論文で引用した原典」のリストとして整備し直すと、データセットと文献の両方が管理できます。ただし工数は中。選択肢 C は短期的な対応として許容範囲。

---

## 画像系

| 優先順位 | 名称 | 種別 | URL |
|---|---|---|---|
| 1 | DTU Wind Turbine Inspection Images | 一次 | https://data.mendeley.com/datasets/hd96prn3nc |
| 1 | DTU Orbit 紹介ページ | 一次（補足） | https://orbit.dtu.dk/en/publications/dtu-drone-inspection-images-of-wind-turbine |
| 2 | YOLO Annotated Wind Turbine Surface Damage | 二次（原典: DTU） | https://data.mendeley.com/datasets/t6fwpc735s |
| 3 | Kaggle mirror (YOLO形式) | 二次（原典: DTU） | https://www.kaggle.com/datasets/ajifoster3/yolo-annotated-wind-turbines-586x371 |
| 3 | Kaggle (Faster-RCNN形式) | 二次（原典: DTU） | https://www.kaggle.com/datasets/stmlen/nordtank-windturbine-dataset-faster-rcnn-format |

---

## 時系列系

| 優先順位 | 名称 | 種別 | URL |
|---|---|---|---|
| 1 | OpenOA（解析基盤） | ツール | https://openoa.readthedocs.io/ |
| 1 | OpenOA JOSS Paper | 論文 | https://www.theoj.org/joss-papers/joss.02171/10.21105.joss.02171.pdf |
| 2 | Wind Turbine SCADA Dataset (Kaggle) | 二次（練習用） | https://www.kaggle.com/datasets/berkerisen/wind-turbine-scada-dataset |
| 2 | Wind Turbine SCADA for Early Fault Detection | 二次（練習用） | https://www.kaggle.com/datasets/azizkasimov/wind-turbine-scada-data-for-early-fault-detection |

---

## シミュレーション系

| 優先順位 | 名称 | 種別 | URL |
|---|---|---|---|
| 1 | OpenFAST Documentation | ツール | https://openfast.readthedocs.io/ |
| 1 | OpenFAST GitHub | ツール | https://github.com/OpenFAST/openfast |

---

## SHM / 損傷インデックス系

| 優先順位 | 名称 | 種別 | URL |
|---|---|---|---|
| 1 | Wind turbine blade SHM dataset (Zenodo) | 一次 | https://zenodo.org/records/13692213 |
| 1 | Vibration-based Monitoring benchmark (Zenodo) | 一次 | https://zenodo.org/records/3229743 |

---

## 参考論文

| タイトル | DOI / URL |
|---|---|
| Wind Turbine Surface Damage Detection by Deep Learning (Energies 2019) | https://www.mdpi.com/1996-1073/12/4/676 |
| Digital twin of wind turbine surface damage detection | https://www.sciencedirect.com/science/article/abs/pii/S0960148124024005 |
