# データ辞書

最終更新: 2026-04-01

---

## 1. DTU Wind Turbine Inspection Images（一次ソース）

| 項目 | 内容 |
|---|---|
| 正式名称 | DTU - Drone inspection images of wind turbine |
| 出典 | Mendeley Data |
| DOI | 10.17632/hd96prn3nc.2 |
| URL | https://data.mendeley.com/datasets/hd96prn3nc |
| 作者 | ASM SHIHAVUDDIN, Xiao Chen |
| 公開日 | 2018年9月26日（Version 2） |
| ライセンス | CC BY NC 3.0（非営利研究利用OK、商用不可） |
| 引用方法 | SHIHAVUDDIN, ASM; Chen, Xiao (2018), "DTU - Drone inspection images of wind turbine", Mendeley Data, V2, doi: 10.17632/hd96prn3nc.2 |

### 撮影対象

| 項目 | 内容 |
|---|---|
| 風車機種 | Nordtank（デンマーク製）|
| 設置場所 | DTU Wind Energy test site, Roskilde, Denmark |
| 撮影年 | 2017年・2018年（同一風車の時点差データ） |
| 撮影手段 | ドローン（Drone） |
| 総画像数 | 701枚（高解像度） |

### 損傷クラス定義（Energies 2019論文準拠）

| クラスID | クラス名 | 略称 | 定義 |
|---|---|---|---|
| 0 | Leading Edge Erosion | LE | ブレード前縁部の浸食。雨滴・砂・虫などの衝突で発生。LEEの主要な視覚的特徴 |
| 1 | Vortex Generator Panel | VG | ブレード表面に取り付けられたVGパネル（剥離抑制部品）。損傷ではなく取付部品だが点検対象 |
| 2 | VG Panel with Missing Teeth | VG-MT | VGパネルの歯が欠損した状態。補修・交換の要否判断に使う |
| 3 | Lightning Receptor | LR | 落雷保護のための受雷部品。損傷ではなく点検対象部品 |

**注記**：VGパネルとLightning Receptorは損傷ではなく「取付部品」だが、点検上重要なため対象クラスに含まれている。

### データ分割

| 分割 | 比率（論文） | 本研究での推奨 |
|---|---|---|
| Train | 60% | 70% |
| Val | - | 15% |
| Test | 40% | 15% |

**重要**：同一ブレード・同一年の画像が分割をまたがないよう設計する（データリーク防止）。

### アノテーション形式

| 項目 | 内容 |
|---|---|
| 形式 | バウンディングボックス（専門家による手動ラベリング） |
| 参考GitHubリポジトリ | https://github.com/imadgohar/DTU-annotations |

### データ取得・品質メモ

（データダウンロード後に記入）
- フォルダ構成：
- 2017年画像数：
- 2018年画像数：
- 画像形式：
- 平均解像度：
- 欠損・破損ファイル：

---

## 2. YOLO Annotated Wind Turbine Surface Damage（二次ソース）

| 項目 | 内容 |
|---|---|
| 正式名称 | YOLO Annotated Wind Turbine Surface Damage |
| 出典 | Mendeley Data |
| DOI | 10.17632/t6fwpc735s.1 |
| URL | https://data.mendeley.com/datasets/t6fwpc735s |
| 作者 | Ashley Foster |
| 公開日 | 2021年9月14日 |
| ライセンス | CC BY NC 3.0 |
| **原典** | DTU原データ（DOI: 10.17632/hd96prn3nc.2）を加工したもの |

### 変換内容

| 処理 | 内容 |
|---|---|
| 画像サイズ | 586 × 371 px に統一 |
| フィルタリング | 風車表面が映っていないフレームを除外 |
| アノテーション | Makesense.aiで手動ラベリング → YOLO形式に変換 |
| クラス | 4クラス → 2クラスに簡略化 |

### クラス定義（YOLO変換版）

| クラスID | クラス名 |
|---|---|
| 0 | Dirt（汚れ・表面コンタミネーション） |
| 1 | Damage（LE Erosion・VG-MT等の物理損傷） |

### YOLO形式アノテーションの読み方

```
# 各行の形式：<class_id> <center_x> <center_y> <width> <height>
# すべて0〜1に正規化された値
# 例：0 0.512 0.340 0.120 0.085
#     → クラス0（Dirt）、中心座標(51.2%, 34.0%)、幅12%、高さ8.5%
```

### 利用上の注意

- **研究記録・論文引用には必ずDTU原典（DOI: 10.17632/hd96prn3nc.2）を記載する**
- クラス定義がDTU原典と異なる（4→2クラス）ため、比較時は注意
- 本研究では前処理スクリプトの参照・形式確認として使用

---

## 3. 参考論文

### Energies 2019（主要参考論文）

| 項目 | 内容 |
|---|---|
| タイトル | Wind Turbine Surface Damage Detection by Deep Learning Aided Drone Inspection Analysis |
| 著者 | ASM Shihavuddin et al. |
| 掲載誌 | Energies, MDPI |
| DOI | 10.3390/en12040676 |
| URL | https://www.mdpi.com/1996-1073/12/4/676 |

**主要な知見**：
- Faster R-CNN（Inception-ResNet-V2バックボーン）でmAP 81.10%を達成
- ピラミッド拡張（multi-scale）＋パッチ拡張で約35%の精度向上
- 小規模データセットでの学習では高度なデータ拡張が重要

**本研究との差分**：
- 本研究はYOLOv8を使う予定。Faster R-CNNとの速度・精度トレードオフを比較する
- 本研究は「部位別リスクスコア」まで進める（同論文は損傷検出止まり）
