# Cross-Paper 整合性チェック レポート

**実施日**: 2026-04-27
**対象**: Paper 1 v9.2 / Paper 2 v9.4 / Paper 3 v5.3
**目的**: 単一論文監査では出ない問題（複数 paper 間の表記・用語・数値・参照形式の不一致）を捕捉

## 集計

| 観点 | 重大 | 中程度 | 軽微 | 合計 |
|---|---|---|---|---|
| 引用書誌の表記統一 | 0 | 1 | 4 | 5 |
| 用語統一 | 0 | 0 | 1 | 1 |
| 数値整合 | 0 | 0 | 0 | 0 |
| Paper 間参照リンク | 0 | 0 | 0 | 0 |
| 参考文献フォーマット | 0 | 1 | 0 | 1 |

**重大な問題は0件**。中程度2件・軽微5件の発見があり、いずれも投稿前に統一しておくと査読時の些細な指摘を回避できる類のものです。

---

## 中程度の発見

### 中-1：Tautz-Weinert 2017 の DOI 表記不統一

| Paper | Reference | DOI 表記 |
|---|---|---|
| Paper 2 [4] | `Tautz-Weinert, J. and Watson, S.J. (2017). Using SCADA data for wind turbine condition monitoring — a review. IET Renewable Power Generation, 11(4), 382–394.` | **DOI なし** |
| Paper 3 [7] | `Tautz-Weinert, J. and Watson, S.J. (2017): Using SCADA data for wind turbine condition monitoring — a review. IET Renewable Power Generation, 11(4), 382–394. DOI: 10.1049/iet-rpg.2016.0248` | DOI あり |

**判定**：同じ文献を引用しているのに DOI 表記の有無が分かれている。Paper 2 [4] に DOI を追記して統一するのが望ましい。

**影響**：軽い不統一だが、最終ドラフト時に修正可能な低コスト案件。

### 中-2：参考文献フォーマットが3 paper で異なる

| Paper | Format Pattern |
|---|---|
| Paper 1 | `1. AuthorList (Year): "Title" — Journal, Vol(Issue), Page. DOI: 10.xxx` |
| Paper 2 | `[N] AuthorList (Year). Title. Journal, Vol(Issue), Page–Page. DOI: 10.xxx.` |
| Paper 3 | `[N] AuthorList (Year): Title. Journal, Vol(Issue), Page–Page. DOI: 10.xxx` |

**主な差異**：
- 番号表記：`1.`（Paper 1）vs `[N]`（Paper 2/3）
- 年と本文の区切り：`(Year):`（Paper 1/3）vs `(Year).`（Paper 2）
- タイトル表記：引用符 `"...Title..."`（Paper 1）vs 引用符なし（Paper 2/3）
- 著者表記：`A. et al.`（Paper 1/3 多用）vs `A., B., and C.` 列挙（Paper 2 多用）
- DOI 末尾：終止符あり（Paper 2）vs 終止符なし（Paper 1/3）

**判定**：3 paper を「研究シリーズ」として共通投稿先に出す場合、フォーマット統一が必要。同一ジャーナルに別個投稿する場合はジャーナルガイドラインに従えばよく、本研究内での統一は必須ではない。

**推奨**：投稿先が決まった段階でジャーナルガイドラインに従って一括書式変換する。Paper 1 の `"...Title..."` 引用符のみ Paper 2/3 から浮いており、最低限ここは統一する価値あり。

---

## 軽微な発見

### 軽-1：著者列挙の `&` vs `and` 不統一

| Paper | 表記例 |
|---|---|
| Paper 1 §2.3 | `Malik & Bak (2025) used aeroelastic simulations...` |
| Paper 1 §5.3 | `Malik & Bak (2025), who applied leading-edge erosion...` |
| Paper 2 [8] | `Malik, T.H. and Bak, C. (2025).` |
| Paper 3 [4] | `Malik, T.H. and Bak, C. (2025):` |

**判定**：本文中の引用形式（"Malik & Bak"）と reference list の形式（"Malik, T.H. and Bak, C."）の差は通常許容される。Paper 内では一貫している。

**影響**：投稿先のスタイルガイドが `&` か `and` を明示する場合のみ修正必要。

### 軽-2：Plumley 2022 (Penmanshiel) の区切り文字不統一

| Paper | 表記 |
|---|---|
| Paper 2 [5] | `Plumley, C. (2022). Penmanshiel Wind Farm Data. Zenodo. DOI: 10.5281/zenodo.5946808.` |
| Paper 3 [5] | `Plumley, C. (2022): Penmanshiel Wind Farm Data. Zenodo. DOI: 10.5281/zenodo.5946808` |

**判定**：年と本文の区切りが `.` vs `:` で異なるが、上記「軽-2」（フォーマット差）の派生。

### 軽-3：Hayman 2012 報告書番号の placeholder

| Paper | 表記 |
|---|---|
| Paper 2 [10] | `Hayman, G.J. (2012). MLife Theory Manual for Version 1.00. NREL/TP-xxxx. National Renewable Energy Laboratory.` |
| Paper 3 [8] | `Hayman, G.J. (2012): MLife Theory Manual. NREL.` |

**重要な発見**：MLife Theory Manual 原本（取得済 PDF 表紙）には実際に `NREL/TP-XXXXX` と表示されており、**正式な TP 番号が割り当てられないまま発行された**ことが確認できる。Paper 2 の "TP-xxxx" は原本の状態を反映しており、誤記ではない。

**推奨**：可読性のため Paper 2 [10] を `Hayman, G.J. (2012). MLife Theory Manual for Version 1.00. NREL Technical Report (no TP number assigned). National Renewable Energy Laboratory.` または Paper 3 [8] のように省略形に統一するのが無難。

### 軽-4：Shihavuddin 2019 タイトル case 不統一

| Paper | タイトル |
|---|---|
| Paper 1 [1] | `"Wind Turbine Surface Damage Detection by Deep Learning Aided Drone Inspection Analysis"`（Title Case） |
| Paper 3 [3] | `Wind turbine surface damage detection by deep learning aided drone inspection analysis`（sentence case） |

**判定**：実際の論文タイトル（Energies 誌掲載）は sentence case が原型。Paper 1 の Title Case は引用慣例。投稿先のスタイル次第で統一。

### 軽-5：DEL の正式名称定義位置

| Paper | DEL の初出位置 | 正式名定義の有無 |
|---|---|---|
| Paper 2 §1.1 line 74 | 初出 | `疲労等価荷重（DEL: Damage Equivalent Load）` 定義あり ✅ |
| Paper 3 Abstract line 60 | Abstract | `月次疲労等価荷重（DEL: Damage Equivalent Load）` 定義あり ✅ |

**判定**：両 paper で正式名と略号の対応が示されており整合 ✅。

### 軽-6：用語「TI」と「Turbulence Intensity」の併用

- "Turbulence Intensity" 完全表記は3 paper どこにも見当たらない
- 全て「TI」略号で記述されている（Paper 2: 22回、Paper 3: 6回、Paper 1: 0回）
- IEC 61400-1 規格内で "Turbulence Intensity" の定義参照があるため、初出時に正式名展開しておくと親切

**推奨**：Paper 2 §1.1 または Abstract で `乱流強度（TI: Turbulence Intensity）` のような正式定義を追加すると初読者に親切。Paper 3 は Paper 2 を参照する位置づけのため不要。

---

## 数値整合（OK 確認）

| Paper 3 で参照されている Paper 1/2 の数値 | Paper 1/2 での実値 | 整合 |
|---|---|---|
| Paper 3 §3.1 "Paper 1: mAP@0.5 = 0.58" | Paper 1 Table mAP@0.5 = 0.581（小数2桁丸め） | ✅ |
| Paper 3 §3.2 "Paper 2のDELマトリクス（8V × 5TI）" | Paper 2 §4.5 "全40条件（8V × 5TI、各6シード平均）" | ✅ |
| Paper 3 §3.2 "MM82: 0.725/0.275, R² = 0.943" | Paper 2 Table w_V=0.725, w_TI=0.275, R²=0.943 | ✅ |
| Paper 3 §6.1 "Paper 2: 240 MM82 cases, R² = 0.943" | Paper 2 Abstract "240ケース"、§4.5 "R²=0.943" | ✅ |

数値の Cross-paper 整合は完全に保たれている。

---

## Paper 間参照リンクの整合（OK 確認）

| Paper 3 References | 実際の Paper 1/2 タイトル | 整合 |
|---|---|---|
| Paper 3 [1] "Paper 1: Wind Turbine Blade Surface Damage Detection and Span-wise Risk Scoring Using Drone Inspection Images with Pyramid Patch Augmentation" | Paper 1 タイトル：完全一致 | ✅ |
| Paper 3 [2] "Paper 2: Site-Specific Blade Fatigue Load Estimation via Reference Turbine Scaling and Public SCADA: A Penmanshiel Case Study" | Paper 2 §タイトル案（確定）：完全一致 | ✅ |

Paper 2 のメインタイトル（日本語：`OpenFASTスケーリングモデルと公開SCADAを用いたSenvion MM82風車の長期疲労荷重推定基盤の構築`）と英訳タイトル（`Site-Specific Blade Fatigue Load Estimation via Reference Turbine Scaling and Public SCADA: A Penmanshiel Case Study`）が併存しているが、Paper 3 [2] が引用しているのは英訳の方で論文内に明記されている。

---

## 推奨対応一覧

| # | 対象 | 優先度 | アクション |
|---|---|---|---|
| 1 | Paper 2 [4] Tautz-Weinert | 中 | DOI `10.1049/iet-rpg.2016.0248` を追記して Paper 3 [7] と統一 |
| 2 | Paper 2 [21] Herp | 中 | DOI `10.1016/j.renene.2017.02.069` を追記（Crossref 一括検証で発覚） |
| 3 | 3-paper の参考文献フォーマット | 中 | 投稿先確定後に統一（共通投稿シリーズの場合） |
| 4 | Paper 2 [10] Hayman | 低 | `NREL/TP-xxxx` を `NREL Technical Report (no TP number assigned)` に変更、または Paper 3 [8] と同形に短縮 |
| 5 | Paper 1 [1] vs Paper 3 [3] Shihavuddin | 低 | Title case を sentence case に統一（または逆）。投稿先スタイル次第 |
| 6 | Paper 2 §1.1 TI 用語定義 | 低 | `乱流強度（TI: Turbulence Intensity）` を初出時に展開 |

---

## 結論

- **重大な不整合は0件**
- 中程度2件・軽微5件はすべて最終ドラフト確定段階での書式統一作業の範疇
- 数値・参照リンクは完全整合
- DEL 定式化・記号表記・用語の本質的な使い方は全 paper で一貫している（v9.x / v5.x の精読修正で整理済み）

待機作業 B として実施した cross-paper 整合性チェックの結論：**現時点で論文の科学的整合性に影響する問題は見つからなかった**。投稿前の最終整形時に上記6項目を一括対応すれば足りる。

