# B3: Paper 1/2/3 内部自己整合性チェック結果

**実施日**: 2026-04-29
**対象**: Paper 1（442 行）、Paper 2（769 行）、Paper 3（516 行）の内部整合性
**チェック項目**: (1) 引用番号と参考文献リストの対応、(2) 章間の数値整合性、(3) 専門用語の表記揺れ、(4) 図表番号の整合性

---

## 監査結論サマリ

| 区分 | 件数 |
|---|---|
| ✅ 整合性 OK | Paper 2 / Paper 3（数値・引用ともに整合） |
| ⚠️ 表記が読者の混乱を招く可能性 | Paper 1 で2件 |
| ✅ 一見問題に見えたが整合（解消） | 引用番号 [23] / [43] の出現（改訂履歴ログ内の説明文） |

---

## 1. 引用番号 vs 参考文献リスト整合性

### Paper 1（参考文献 [1]-[16]）

#### 整合性
- 本文中で番号引用されているのは **[7]-[16]** のみ
- **[1]-[6] は著者名形式（"Shihavuddin et al. (2019)" 等）で引用**されており、番号引用されていない
- 学術論文の慣行として **ハイブリッド引用スタイル（著者名 + 番号）は許容される** が、editorial review で「all references should be cited consistently」と指摘される可能性がある

#### 具体例
- [1] Shihavuddin 2019: line 28, 52, 282, 294 で著者名引用
- [2] Gohar 2023: line 28, 52, 75, 282, 294, 324 で著者名引用
- [3] Malik & Bak 2025: line 62, 147, 282 で著者名引用
- [4] Lin 2017: line 56 で著者名引用（"Focal loss (Lin et al. 2017)"）
- [5] Ultralytics 2023: 本文中の番号引用なし（YOLOv8 = ultralytics の暗黙引用）
- [6] DTU Mendeley: line 74, 338 で DOI 形式で参照

#### 推奨（任意）
ジャーナル投稿時の最終形式として、すべての参考文献を **番号引用形式に統一** することが editorial 観点では望ましい。ただし、現状の表記でも論文として論理整合性は確保されている。

### Paper 2（参考文献 [1]-[22]）

✅ **完全整合**: 本文中の番号引用 [1]-[22] が全て参考文献リストに存在し、欠落なし。

### Paper 3（参考文献 [1]-[25]）

✅ **完全整合**: 本文中の番号引用 [1]-[25] が全て参考文献リストに存在し、欠落なし。

### 一見問題に見えたが解消されたもの

#### Paper 2 line 758, 762 の "[23]" 表記
- 改訂履歴 v5.0 / v9.0 内の説明文で "参考文献[12]–[23]を[11]–[22]に繰り上げ" と過去の参考文献番号を記述
- **本文ではない（改訂履歴内）** ため、本文中の引用としては問題なし

#### Paper 3 line 516 の "[43]" 表記
- 改訂履歴 v5.3 内で Maldonado-Correa 2020 の論文中の引用 [43] に言及した説明
- **Paper 3 自体の引用ではない（Maldonado-Correa 内の参照）** ため問題なし

---

## 2. Paper 1 の数値整合性

### ⚠️ 問題 1: Table 1 (0.581) vs Table 2 (0.561) の "5-class mAP@0.5"

| 出現箇所 | 表記 | 値 |
|---|---|---|
| Abstract (line 10, 20) | "mAP = 0.58" / "mAP@0.5 ... to 0.58" | 0.58（丸め値） |
| Table 1 (line 167) | "mAP@0.5" | **0.581** |
| Table 2 (line 195) | "**5-class mAP**" | **0.561** |
| Table 3b (line 302) | "YOLOv8n (EXP-002) mAP@0.5" | **0.581** |
| §5.4 文中 (line 274, 294, 306) | "mAP@0.5" | 0.58 |
| Conclusion (line 354) | "mAP@0.5" | 0.58 |

#### 問題点
- Table 1 と Table 3b では **0.581**
- Table 2 では **0.561**
- 両者とも「5-class mAP@0.5」として表記されているが値が異なる
- line 198 の脚注で「The five-class mAP@0.5 (0.561) is the primary performance metric」と記載されており、**Table 2 の値（0.561）が主要指標**として扱われている

#### 推定原因
- Table 1: ultralytics の自動レポート値（おそらく集約計算方式）
- Table 2: per-class AP の単純算術平均（`mean(AP_LE;ER, AP_VG;MT, AP_SF;PO, AP_LR;DA, AP_LE;CR) = (0.784 + 0.756 + 0.706 + 0.556 + 0.000) / 5 = 0.561`）

#### 推奨される修正候補（A 群への追加候補 A7 として）
1. Table 1 に脚注を追加：「Table 1 reports the ultralytics-aggregated mAP@0.5 = 0.581. Per-class AP averages computed manually yield 0.561 (see Table 2). The discrepancy arises from differences in aggregation methodology; both values are reported for transparency.」
2. または、Abstract の「mAP = 0.58」を「mAP@0.5 = 0.56–0.58 (depending on aggregation methodology)」と表現する
3. または、両者の差異の詳細説明を追加

### ⚠️ 問題 2: LE;CR 比率の文脈表記

| 出現箇所 | 表記 | 値 | 尺度 |
|---|---|---|---|
| Abstract (line 10) | "LE;CR（訓練パッチの1.6%）" | 1.6% | 訓練パッチに対するLE;CR を含む割合 |
| Abstract (line 20) | "1.6% of training patches" | 1.6% | 同上（英語版） |
| §3.1 (line 82) | "LE;CR (10.2%)" | 10.2% | 全 instances に対する LE;CR の割合 |
| Table 4 (line 217) | "LE;CR \| 171 \| 14 \| 11 \| 196 \| 10.2%" | 10.2% (= 196/1,914) | 同上 |
| line 221 注記 | "Training patches containing at least one LE;CR annotation: **132 / 8,055 (1.6%)**" | 1.6% | パッチ単位 |
| Table 5 (line 231) | "LE;CR in 1.6% of training patches" | 1.6% | パッチ単位 |

#### 整合性評価
**論理的には整合**しています：
- 1.6% = LE;CR を含む訓練パッチ数 / 全訓練パッチ数 = 132 / 8,055
- 10.2% = LE;CR インスタンス数 / 全インスタンス数 = 196 / 1,914

これらは **異なる尺度** であり、line 221 の脚注で明示的に定義されています。

#### 問題点
ただし、読者が **同じ「LE;CR の頻度」を異なる値で見ること** で混乱する可能性があります：
- Abstract で「1.6%」を見た読者が §3.1 Table 4 で「10.2%」を見ると違和感を覚える
- パッチ単位 vs インスタンス単位の違いは技術的には正しいが、Abstract の段階で「1.6% of training patches」と定義しても、通常の読者は「class distribution の比率」と混同しやすい

#### 推奨される表現精緻化（A 群への追加候補 A8 として）
1. Abstract の表現を「LE;CR appeared in only 1.6% of training patches (10.2% of total instances, but concentrated in few patches)」のように両方の尺度を併記する
2. または、§3.1 で 10.2% を導入する際に「LE;CR comprises 10.2% of total instances but appears in only 1.6% of training patches due to clustering」と関係性を説明する
3. Table 4 のキャプションに「Note: LE;CR instances cluster in fewer patches; only 132/8,055 = 1.6% of training patches contain at least one LE;CR annotation」を追加

---

## 3. Paper 2 の数値整合性

### ✅ TI 値の整合性
- line 84: "近似値 ~0.035 vs. 直接計測 ~0.14"
- line 410: "Median TI | ~0.035 | 0.133–0.144"
- line 421-423: 月次 TI = 0.146, 0.148, 0.137
- 0.14 は 0.133-0.144 の代表値、月次値もこの範囲内 → **整合**

### ✅ DEL 比率の整合性
- line 343: "DEL ratio (MM82 / NREL 5MW) | 0.258"（単一ケース）
- line 355-357: "Mean ratio | 0.263 | Std | 0.020"（全 40 条件）
- 単一ケース 0.258 と平均 0.263 は別物として整合的に説明されている → **整合**

### ✅ 重み較正の整合性
- line 318: "重み較正結果（NREL 5MW）: w_V = 0.810, w_TI = 0.190（R² = 0.926）"
- line 394: "MM82 では w_TI 0.190 → 0.275"
- Table（line 390 付近）: w_TI 0.190 vs 0.275
- Paper 3 line 134: "w_V/w_TI 較正（MM82: 0.725/0.275, R² = 0.943）" → MM82 値を引用
- すべて **整合**（Paper 2 の NREL 5MW 値と MM82 値が異なるが、それぞれ明示的に区別されている）

### ✅ スケーリング指数の整合性
- λ_R^2.3 (line 122): 採用値
- Fingersh: 2.9158 / 2.53
- Bak: 2.17 / 2.95
- 採用値 2.3 は範囲内中央付近として整合的説明あり → **整合**

---

## 4. Paper 3 の数値整合性

### ✅ Paper 1/2 からの引用数値の整合性

| Paper 3 表記 | 引用元 Paper | 整合性 |
|---|---|---|
| line 124: "mAP@0.5 = 0.58" | Paper 1 | ✅（Paper 1 では 0.58 / 0.581 / 0.561 が混在するが、Paper 3 では丸め値 0.58 のみ） |
| line 124: "5損傷クラスの検出" | Paper 1 | ✅ |
| line 124: "LE;CR検出不能（AP = 0.00）" | Paper 1 Table 2 | ✅ |
| line 134: "MM82: 0.725/0.275, R² = 0.943" | Paper 2 line 394 (Table) | ✅ |
| line 134: "8V × 5TI" DEL マトリクス | Paper 2 §4 | ✅ |
| line 130: "Paper 2 §5.4" 内部参照 | Paper 2 | ✅ |
| line 124: "Paper 1 §3.4" 内部参照 | Paper 1 | ✅ |

### ✅ 専門用語の表記
- "DEL: Damage Equivalent Load" (line 60) → 略語定義あり
- "Module A / B / C" → 各章で一貫した使用
- "fatigue_risk_score" / "image_risk_score" → snake_case で統一

---

## 5. 図表番号の整合性

### Paper 1
- 本文中の Table/Fig 参照と「図表一覧」(line 387-406) を照合
- Table 1-7, Fig 1-9 すべてリストに存在 → ✅ 整合

### Paper 2
- 本文中の Table/Fig 参照と参照表 (line 627-666) を照合 → ✅ 整合

### Paper 3
- Table 1-5 と図表参照 (line 206, 221) → ✅ 整合

---

## 6. B3 監査の総合結論

### 重大な問題: なし

### ⚠️ 改善推奨事項: 2件（Paper 1）

| # | 問題 | 影響度 | 対応案 |
|---|---|---|---|
| A7 | Table 1 (0.581) vs Table 2 (0.561) の「5-class mAP@0.5」値の不一致 | 中（査読で指摘される可能性あり） | Table 1 に脚注追加または計算方法の明記 |
| A8 | LE;CR 比率 1.6% (パッチ) vs 10.2% (インスタンス) の文脈表記 | 低（technically correct だが読者混乱を招きうる） | Abstract で両尺度併記、または §3.1 で関係性説明 |

### 引用スタイルの整合性: Paper 1 で著者名 + 番号のハイブリッド形式

学術慣行として許容されるが、ジャーナル投稿時の editorial review で番号引用形式への統一を求められる可能性あり。これは投稿先ジャーナルのスタイル要求次第。

### Paper 2 / Paper 3: 完全整合

数値・引用・図表番号すべて整合性に問題なし。

---

## 関連メモ

- `B1_crossref_audit_2026-04-29.md` — 書誌レベルの監査結果
- `B2_core_numerical_claims_2026-04-29.md` — 核心数値の引用箇所対応リスト
- `B5_incidental_findings_citation_candidates_2026-04-29.md` — 副次発見の引用候補集
