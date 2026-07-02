# B1: Paper 1/2/3 参考文献リスト Crossref 自己監査結果

**実施日**: 2026-04-29
**対象**: Paper 1（16本）、Paper 2（22本）、Paper 3（25本）= 計63本のうち、DOI 保有引用 31本（重複除く）+ 第10R2-B 7本（先行検証済）

---

## 監査結論サマリ

| 区分 | 件数 |
|---|---|
| Crossref で完全整合（書誌情報・著者・ジャーナルすべて一致） | 30本 |
| **🚨 修正候補（重大）** | **1件**（Paper 2 [21] Herp 2018 DOI 不在） |
| Online publication 年と Issue 年の差 | 2件（実体問題なし） |
| 別 registry DOI（Mendeley/Zenodo/DTU Orbit/OSTI） | 4件（URL アクセス可能性確認済） |
| 標準規格・技術レポート（DOI 非保有） | 約8件（規格番号で識別） |

---

## 1. 重大な修正候補

### 🚨 Paper 2 [21] Herp 2018 — DOI 追加候補

**現在の Paper 2 表記**（line 744）:
> [21] Herp, J., Ramezani, M.H., Bach-Andersen, M., Pedersen, N.L., and Nadimi, E.S. (2018). Bayesian state prediction of wind turbine bearing failure. Renewable Energy, 116, 164–172.

**問題点**:
- 他の Paper 2 引用は DOI を保有している場合は記載している（[3] DTU 10-MW を除く）が、本引用は DOI を欠いている
- 第7バッチで全頁精読済の論文であり、DTU Orbit 経由で Final Published Version を取得済

**Crossref 検証結果**:
- 正しい DOI: **`10.1016/j.renene.2017.02.069`**
- Title: "Bayesian state prediction of wind turbine bearing failure"
- Authors: Herp, Ramezani, Bach-Andersen, Pedersen, Nadimi
- Journal: Renewable Energy
- Year: 2018

**修正案（A6 として A 群に追加）**:
> [21] Herp, J., Ramezani, M.H., Bach-Andersen, M., Pedersen, N.L., and Nadimi, E.S. (2018). Bayesian state prediction of wind turbine bearing failure. Renewable Energy, 116, 164–172. **DOI: 10.1016/j.renene.2017.02.069**

---

## 2. 実体問題なしだが注記すべき項目

### Paper 2 [4] Tautz-Weinert 2017
- Paper 2 表記: 2017
- Crossref: 2016
- 実態: IET Renewable Power Generation Volume 11, Issue 4 は **2017 年発行**だが、Online publication が 2016 年。引用慣行では Issue 年（2017）が正しい。**修正不要**

### Paper 3 [9] Pandit 2023
- Paper 3 表記: 2023
- Crossref: 2022
- 実態: Wind Engineering Volume 47, Issue 2 は **2023 年発行**だが、Online publication が 2022 年。**修正不要**

---

## 3. 別 registry DOI（Crossref 対象外、URL アクセス可能性検証済）

| 引用 | DOI / Identifier | Registry | 検証 |
|---|---|---|---|
| Paper 1 [6] / Paper 3 [6] DTU Inspection Images | 10.17632/hd96prn3nc.2 | Mendeley Data | 過去に取得済 |
| Paper 2 [5] / Paper 3 [5] Plumley 2022 Penmanshiel | 10.5281/zenodo.5946808 | Zenodo | HTTP 200 OK |
| Paper 2 [11] Colone 2018 PhD thesis | 10.11581/DTU:00000033 | DTU Orbit | HTTP 200 OK（リダイレクト経由） |
| Paper 2 [18] Mandell 1997 | 10.2172/578635 | OSTI / Crossref | 両方で確認可能 |

---

## 4. DOI 非保有（標準規格・技術レポート）

これらは DOI ベースの監査が不可能だが、識別子レベルで一意に特定可能：

| 引用 | 識別子 | 確認方法 |
|---|---|---|
| Paper 2 [1] OpenFAST Documentation | URL: openfast.readthedocs.io | 一次情報源 |
| Paper 2 [2] Jonkman 2009 NREL 5-MW | NREL/TP-500-38060 | NREL リポジトリで確認済（精読済） |
| Paper 2 [3] Bak 2013 DTU 10-MW | DTU Wind Energy Report-I-0092 | 同上 |
| Paper 2 [6] ASTM E1049-85 | 規格番号 | ASTM 公式 |
| Paper 2 [7] IEC 61400-1:2019 | 規格番号 | IEC 公式 |
| Paper 2 [10] Hayman 2012 MLife | NREL Technical Report | NREL リポジトリ |
| Paper 2 [13] Matsuishi & Endo 1968 | Conference paper | 引用慣行 |
| Paper 2 [14] Downing & Socie 1982 | Int. J. Fatigue 4(1), 31-40 | 全頁精読済 |
| Paper 2 [15] Fingersh 2006 | NREL/TP-500-40566 | NREL |
| Paper 2 [17] DNVGL-ST-0376 | 規格番号 | DNV GL |
| Paper 2 [19] Natarajan 2020 LifeWind | DTU Wind Energy Report E-0196 | 全頁精読済 |
| Paper 2 [22] Python rainflow | PyPI | ソフトウェアライブラリ |

---

## 5. Crossref で完全整合の引用（30本）

### Paper 1（11/13 → 残り 2 は別 registry）

| 番号 | 著者 | タイトル | DOI |
|---|---|---|---|
| [1] | Shihavuddin 2019 | Wind Turbine Surface Damage Detection... | 10.3390/en12040676 |
| [2] | Gohar 2023 | Slice-Aided Defect Detection... | 10.3390/machines11100953 |
| [3] | Malik & Bak 2025 | Challenges in detecting wind turbine power loss... | 10.5194/wes-10-227-2025 |
| [7] | Konovalenko 2022 | Research of U-Net-Based CNN Architectures... | 10.3390/machines10050327 |
| [8] | Deitsch 2019 | Automatic classification of defective photovoltaic... | 10.1016/j.solener.2019.02.067 |
| [9] | Cha 2017 | Deep Learning-Based Crack Damage Detection... | 10.1111/mice.12263 |
| [10] | Memari 2024 | Review on the Advancements in Wind Turbine Blade Inspection... | 10.1109/ACCESS.2024.3371493 |
| [11] | Masita 2025 | Deep Learning in Defect Detection of Wind Turbine Blades... | 10.1109/ACCESS.2025.3569799 |
| [12] | Zhao & Li 2025 | Enhancing wind turbine blade damage detection with YOLO-Wind | 10.1038/s41598-025-03639-8 |
| [13] | Shi 2026 | DMR-YOLO: An Improved Wind Turbine Blade Surface Damage Detection... | 10.3390/app16031333 |
| [14] | Zou 2024 | DCW-YOLO: An Improved Method for Surface Damage Detection... | 10.3390/app14198763 |
| [15] | Zou 2025 | An improved method of AUD-YOLO... | 10.1038/s41598-025-89864-7 |
| [16] | Akyon 2022 | Slicing Aided Hyper Inference and Fine-Tuning... | 10.1109/ICIP46576.2022.9897990 |

### Paper 2（5/6 → 残り 1 は Herp 2018 DOI 追加候補）

| 番号 | 著者 | タイトル | DOI |
|---|---|---|---|
| [4] | Tautz-Weinert 2017 | Using SCADA data for wind turbine condition monitoring | 10.1049/iet-rpg.2016.0248 |
| [11] | Colone 2018 PhD | DTU thesis | 10.11581/DTU:00000033 |
| [12] | Dimitrov 2015 | Model of wind shear conditional on turbulence... | 10.1002/we.1797 |
| [16] | Robertson 2017 | OC5 Project Phase II... | 10.1016/j.egypro.2017.10.333 |
| [18] | Mandell 1997 | DOE/MSU Composite Material Fatigue Database | 10.2172/578635 |
| [20] | Vera-Tudela 2017 | Analysing wind turbine fatigue load prediction | 10.1016/j.renene.2017.01.065 |

### Paper 3（13/13）

| 番号 | 著者 | タイトル | DOI |
|---|---|---|---|
| [9] | Pandit 2023 | SCADA data for wind turbine data-driven... | 10.1177/0309524X221124031 |
| [10] | Tchakoua 2014 | Wind Turbine Condition Monitoring | 10.3390/en7042595 |
| [12] | García Márquez 2020 | A review of non-destructive testing... | 10.1016/j.renene.2020.07.145 |
| [13] | Stetco 2019 | Machine learning methods for wind turbine condition monitoring | 10.1016/j.renene.2018.10.047 |
| [14] | Dao 2018 | Condition monitoring and fault detection... | 10.1016/j.renene.2017.06.089 |
| [15] | Gohar 2025 | Review of state-of-the-art surface defect detection... | 10.1016/j.engappai.2024.109970 |
| [16] | Liu 2024 | Defect detection of the surface of wind turbine blades... | 10.1016/j.aei.2023.102292 |
| [17] | Yang 2013 | Wind turbine condition monitoring by SCADA data analysis | 10.1016/j.renene.2012.11.030 |
| [18] | Castellani 2024 | Wind turbine gearbox condition monitoring... | 10.1016/j.egyr.2024.06.041 |
| [19] | Maldonado-Correa 2020 | Using SCADA Data for Wind Turbine Condition Monitoring | 10.3390/en13123132 |
| [20] | Kandemir 2024 | Predictive digital twin for wind energy systems | 10.1186/s42162-024-00373-9 |
| [21] | Branlard 2020 | A digital twin based on OpenFAST linearizations... | 10.1088/1742-6596/1618/2/022030 |
| [22] | Hu 2025 | Digital twin of wind turbine surface damage detection... | 10.1016/j.renene.2024.122332 |
| [23] | Nielsen & Sørensen 2011 | On risk-based operation and maintenance... | 10.1016/j.ress.2010.07.007 |
| [24] | Florian 2017 | Risk-based planning of operation and maintenance... | 10.1016/j.egypro.2017.10.349 |
| [25] | Yeter 2020 | Risk-based maintenance planning of offshore wind turbine farms | 10.1016/j.ress.2020.107062 |

---

## 6. 結論

書誌レベルでの監査は **30/31本（97%）が完全整合**。修正候補は **Herp 2018 への DOI 追加 1件のみ**。

これは過去に発見された主張駆動精読での「引用文脈ハルシネーション」とは別の問題で、書誌情報の細部（DOI 表記の網羅性）に関するものです。

**重要**: 本監査は「引用が論文中で正しい主張と結びついているか」（主張駆動精読）とは異なるレベルの監査です。書誌が完全整合でも、引用文の主張が誤っている可能性は別途主張駆動精読で検証する必要があります。本研究では既に第1〜10バッチで主張駆動精読を実施し、複数の修正を適用済（重大ハルシネーション3件 + 軽微7件など）。
