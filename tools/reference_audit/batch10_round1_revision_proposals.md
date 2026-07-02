# 第10バッチ第1ラウンド精読 — Paper 1/2 修正案策定書

**作成日**: 2026-04-27（待機作業として取得済3本の精読完了後）
**対象**: Akyon 2022 SAHI / Downing & Socie 1982 / Natarajan 2020 LifeWind
**精読範囲**: 全頁（5p + 10p + 110p、合計125p）
**目的**: WAKABA 取得待ちの Vera-Tudela 2017 / Dimitrov 2015 / Hu 2025 / Yang 2013 が手元に届く前に、確定的な修正案を文面レベルで準備する

---

## 修正案① Paper 1 §2.2 line 58（Akyon 2022 SAHI 対比表現）

### 不一致の根拠

Paper 1 現状記述：
> "The SAHI framework (Akyon et al. 2022) provides a general-purpose slicing-aided inference pipeline for small object detection, enabling patch-based prediction with automatic merging of overlapping detections [16]. ... **Unlike SAHI, which modifies inference-time behavior, our pyramid approach augments training data at multiple scales while using standard single-scale inference.**"

論文実態（Akyon 2022 全5頁精読）：
- 論文タイトル：「Slicing Aided Hyper Inference **and Fine-Tuning** for Small Object Detection」
- Abstract 明記：「6.8% AP increase（推論のみ：SAHI alone）」 vs 「14.5% AP cumulative increase（SF + SAHI: 訓練 + 推論）」
- §3 で **2 手法を併立提案**：
  - **SF (Slicing Aided Fine-tuning)**：パッチ抽出による訓練データ augmentation（オリジナル＋拡張画像で fine-tuning）
  - **SAHI (Slicing Aided Hyper Inference)**：推論時の slicing + NMS merging
- 表1（VisDrone）：SF + SAHI の組み合わせが最高性能（FCOS 38.5%, VFNet 42.2%, TOOD 43.5% AP50）
- 表2（xView）：SF なしでは 2.10–2.20% AP で実用不可、SF を入れることで 15-20% AP まで改善

**問題点**：
1. Paper 1 の対比文「SAHI modifies inference-time behavior」は **SAHI 論文の半分（推論側）しか反映していない**
2. Paper 1 の pyramid approach は「訓練時のパッチ multi-scale 提示」だが、これは SAHI の SF（Slicing Aided Fine-tuning）と概念的に類似するため、差別化が曖昧
3. ただし詳細な相違は存在：
   - SAHI SF：パッチを extracted images として treat、width 800–1333 にリサイズして元画像と併用
   - Paper 1 pyramid：パッチを **複数の離散スケール**で同時提示（multi-scale presentation）

### 修正案

#### 案A（最小修正・正確性優先）

> "...The SAHI framework (Akyon et al. 2022) [16] proposes a generic pipeline that combines slicing-aided fine-tuning (training-time patch augmentation) with slicing-aided inference (test-time slicing followed by NMS merging of overlapping detections). Patch-based training has been applied to small-defect detection in industrial inspection contexts, including steel surface defect detection [7], photovoltaic cell crack classification [8], and concrete crack detection [9]. These findings motivate the pyramid patch approach adopted here: **input patches are presented at multiple discrete scales during training while preserving standard single-scale inference at deployment.** Our approach differs from SAHI's slicing-aided fine-tuning in that patches are explicitly presented at distinct scale levels rather than slice-and-resize augmentation, and we do not employ slicing-aided inference at test time."

**ポイント**：
- SAHI が SF + SAHI の二段構成であることを明示
- 差別化は (1) multi-scale 提示 vs slice-and-resize, (2) test-time slicing なし、で具体化

#### 案B（簡潔・主旨優先）

> "...The SAHI framework (Akyon et al. 2022) [16] combines slicing-aided fine-tuning with sliced inference, the latter providing automatic merging of overlapping detections via NMS. Patch-based training has been applied to small-defect detection in industrial inspection contexts [7][8][9]. These findings motivate the pyramid patch approach adopted here: **patches are presented at multiple discrete scales during training while inference uses the standard single-scale pipeline.** This differs from SAHI in that we present patches at predefined discrete scale levels and avoid sliced inference at deployment."

**ポイント**：
- 案A より短い
- 二段構成は「combines ... with ...」で一文に圧縮

#### 案C（最小限の差し替え・既存構造を温存）

現状の最後の対比文のみ差し替え：

> "...These findings motivate the pyramid patch approach adopted here: input patches are presented at multiple scales during training, without modifying the network architecture. **Unlike SAHI's slicing-aided inference, which performs sliced prediction at test time, our pyramid approach uses standard single-scale inference. Our training-time augmentation also differs from SAHI's slicing-aided fine-tuning by presenting patches at predefined discrete scale levels rather than slice-and-resize.**"

**ポイント**：
- 既存記述の最後の1文のみ書き換え（修正範囲最小）
- SAHI の SF と SAHI 両方に対する差別化を明示

### himinさん判断要件
- 案A〜Cのいずれを採用するか
- 「差別化が曖昧」のリスクを率直に書くか、それとも positive な差別化軸として書くか
- §5.4 Limitation 9-11 への追記が必要か（"our pyramid approach overlaps conceptually with SAHI's SF" の限界明示）

---

## 修正案② Paper 2 §2 line 118（Downing & Socie 1982 表現精緻化）

### 不一致の根拠

Paper 2 現状記述：
> "Hayman (2012) はMLifeツールによるDEL算出手法（Downing & Socie (1982) のone-pass Rainflow計数、等価サイクル数正規化）を体系化した [10]。Rainflow計数法の原理はMatsuishi & Endo (1968) [13] に遡り、**Downing & Socie (1982) [14] が計算アルゴリズムを体系化した**。"

論文実態（Downing & Socie 1982 全10頁精読）：
- 論文タイトル：「**Simple** rainflow counting algorithms」
- Abstract：「Two **simple** algorithms for performing rainflow counting are presented in this paper. The second algorithm is suitable for **microcomputer devices** that are placed in vehicles to record field data.」
- §INTRODUCTION：「Several algorithms are available to perform the counting, however, they all require that the entire load history be known before the counting process starts.」 — 先行アルゴリズムの存在を著者自身が明示
- 引用文献：Wetzel 1971（availability matrix）、Okamura 1979（half-cycle 修正）、Matsuishi & Endo 1968 等を引用
- Algorithm I（rearranged history 用）と Algorithm II（One-Pass、real-time 処理可能）の **2 つを提示**
- 主旨：「The 'one-pass' rainflow counting algorithm described later overcomes this limitation and identifies the same cycles as the first algorithm」

**問題点**：
- 「**体系化**」（comprehensive systematization）は表現が強すぎる
- 論文の自己定義は「**simple algorithms for processing field data**」
- 寄与の中心は「One-Pass 計算による real-time 実装可能化」であり、Rainflow 計数法そのものの体系化ではない

### 修正案

#### 案A（軽微修正・主旨保持）

> "Rainflow計数法の原理はMatsuishi & Endo (1968) [13] に遡り、**Downing & Socie (1982) [14] が現場データ処理向けの one-pass 実用アルゴリズム（Algorithm II）を提示した**。"

**ポイント**：
- 「体系化」→「現場データ処理向けの one-pass 実用アルゴリズム提示」で論文実態に整合
- 既存文の前後文脈（ASTM E1049-85 への接続）を維持

#### 案B（より詳細・寄与の特異性を明示）

> "Rainflow計数法の原理はMatsuishi & Endo (1968) [13] に遡り、Wetzel (1971) や Okamura et al. (1979) などにより複数のアルゴリズムが提案されたが、いずれも荷重履歴全体が既知である必要があった。**Downing & Socie (1982) [14] は real-time 処理可能な one-pass アルゴリズムを提示し、この制約を解消した**。ASTM E1049-85 [規格番号は§3.4で参照] はこれらのアルゴリズムを業界標準として整理した規格であり、本研究は同規格準拠のPython `rainflow` 3.2.0 [22] を使用する。"

**ポイント**：
- 先行研究（Wetzel, Okamura）への言及を追加
- D&S 1982 の特異性（real-time 処理可能化）を明示
- ASTM E1049-85 が「これらのアルゴリズム」を整理した、という記述で正確化

#### 案C（最小修正・1語のみ差し替え）

> "...Downing & Socie (1982) [14] が **one-pass 計算アルゴリズムを提示した**。"

**ポイント**：
- 「体系化した」→「one-pass 計算アルゴリズムを提示した」で1語修正のみ
- 修正範囲を最小化

### himinさん判断要件
- 案A〜Cのいずれを採用するか
- 案Bの先行研究言及（Wetzel 1971, Okamura 1979）は新規参考文献追加を要するか、それとも本文記述のみで参考文献リストへは追加しないか

---

## 修正案③ Paper 2 §2.3 line 126（Natarajan 2020 IEA Wind Task 42 誤帰属）

### 不一致の根拠（**重大ハルシネーション**）

Paper 2 現状記述：
> "**IEA Wind Task 42（寿命延長）[19]** では、SCADAベースの荷重評価が寿命延長判断の重要な入力とされており、本研究はこの文脈に位置づけられる。"

論文実態（Natarajan 2020 全110頁精読）：
- 表紙：「Demonstration of Requirements for Life Extension of Wind Turbines Beyond Their Design Life (**LifeWind**)」
- p.1 Project information：「Project no 64017-05114」「Funded by the **Energy Technology Development and Demonstration Programme (EUDP)**」（デンマーク国家ファンド）
- §5.3 Conclusions (p.68)：「The major **EUDP Lifewind contributions** to the load based lifetime assessment have been...」
- §8 Summary Recommendation：策定中の **IEC 61400-28 標準** への入力資料として推奨事項を提示
- **全110頁で IEA Wind Task 42 の言及は一切なし**
- References セクション（pp.107-109）：IEC 61400-1, IEC 61400-26, ISO 13822, ISO 2394, JCSS, NORSOK, DNVGL-ST/SE-026X, Bureau Veritas, NPR 8400, UL 4143 等を引用するが **IEA Wind Task XX への参照は皆無**

**事実関係**：
- IEA Wind Task 42 は実在し（"Lifetime Extension Assessment of Wind Turbines"）、DTU も参画している
- しかし本論文 [19] は IEA Wind Task 42 の output ではなく、独立した EUDP 国家プロジェクト（LifeWind）の成果報告書
- 主題（寿命延長）の重複と DTU 著者ゆえ、AI が訓練データから誤接続した典型的なプロジェクト名ハルシネーション

### 修正案

#### 案A（最小修正・プロジェクト名のみ差し替え）

> "**EUDP LifeWind project (Natarajan et al. 2020) [19]** では、SCADAベースの荷重評価が寿命延長判断の重要な入力とされており、本研究はこの文脈に位置づけられる。"

**ポイント**：
- プロジェクト名のみ修正
- 既存文の他部分（位置づけ）は維持

#### 案B（簡潔・本研究との位置関係を明確化）

> "DTU 主導の **EUDP LifeWind project (Natarajan et al. 2020) [19]** は、SCADA + aeroelastic + ML を組み合わせた寿命延長評価の体系化を行い、策定中の **IEC 61400-28 標準** への入力資料となっている。本研究は同方法論的文脈に位置づけられる。"

**ポイント**：
- LifeWind の方法論的特徴（SCADA + aeroelastic + ML）を明示
- IEC 61400-28（実際に策定中の国際標準）への接続を明示
- 「IEA Wind Task 42」誤帰属の完全置換

#### 案C（詳細版・LifeWind の主要寄与を明示）

> "DTU 主導の **EUDP LifeWind project (Natarajan et al. 2020) [19]** は、運用 SCADA データと aeroelastic デザインベースを組み合わせて wind farm 内の各タービンの DEL を ML で予測する手法を体系化した。同プロジェクトは Horns Rev 1（80×V80, 3年データ）と Krauschwitz（7×Enercon E66, 7年データ）で検証を行い、策定中の **IEC 61400-28 標準（寿命延長）** への入力推奨資料として位置づけられている。本研究は SCADA ベースの荷重評価という同方法論的文脈に位置づけられる。"

**ポイント**：
- LifeWind の方法論詳細を明示（NN 3 hidden layers, R²=0.92 individual turbine power 等の数値含意）
- 検証データセットも明示（Horns Rev 1, Krauschwitz）
- ただし冗長になり得る（line 126 のスタイルに対して長すぎる可能性）

### 補足修正候補（同 line 126 の他文との整合）

line 126 第2文「SCADAからDELを推定するアプローチは、DELマトリクスの機種依存性とTI計測精度の問題から限定的である。」は：
- Tautz-Weinert 2017 全頁精読では本論文に明示記述なし（候補1）
- Natarajan 2020 全頁精読でも DEL マトリクス機種依存性 / TI 計測精度の問題への直接的議論はない（§5.1.2 で turbine size scaling は議論されるが、機種依存性の問題というより scaling 法の提案）
- → Vera-Tudela 2017 / Dimitrov 2015 精読後に再評価

### himinさん判断要件
- 案A〜Cのいずれを採用するか
- IEC 61400-28 への接続を明示するか（Paper 2 の主旨：本研究は寿命延長判断のための SCADA ベース DEL 評価を提案、と一致するなら明示が望ましい）
- line 126 の他文（line 99 / 第2文 / Vera-Tudela / Dimitrov）と統合的に再構成するかは Vera-Tudela / Dimitrov 精読後に確定

---

## ボーナス：Paper 1 / Paper 3 への引用候補

Natarajan 2020 全110頁精読で、himinさんの研究主題への直接的支援材料として以下を発見：

### §8 IEC 61400-28 推奨（p.106）
> "A plan for inspections should be made for the period of lifetime extension, which includes relevant structural elements. The turbine service plans shall be extended to include the number of years of life extension with relevant updates to the inspection plan. **Special focus should be made to: Leading edge erosion of blades.**"

### §3.1.1 (p.13) Inspection findings
> "**Almost all blades show erosion. Inspections show that erosion on leading edge needs further focus. The bigger wind turbines/blades the bigger problem.** There are different design repairs and solutions. None of these solutions show satisfying results. Therefore, these blade repairs need to be performed in a higher quality and method."

### 引用候補

#### Paper 1 §1 Introduction または §2.3 Risk Scoring
> "Recent industry recommendations toward the upcoming IEC 61400-28 lifetime extension standard explicitly identify leading edge erosion as a special focus area for blade inspection during life extension (EUDP LifeWind project, Natarajan et al. 2020) [REF]. This aligns with the present study's focus on detection-driven prioritization of blade erosion damage."

#### Paper 3 §1 Introduction または §2.X 産業意義
> "EUDP LifeWind project (Natarajan et al. 2020) [REF] における IEC 61400-28（寿命延長標準）への推奨事項では、ブレード前縁エロージョンを最重要点検項目として明示的に挙げている。これは本研究が提案する SCADA × 画像 × 気象データ統合パイプラインの産業意義を裏付ける。"

### himinさん判断要件
- Paper 1 / Paper 3 への引用追加を行うか（参考文献リストへの新規追加が必要）
- どの場所（Introduction / Industry relevance / Discussion）に挿入するか

---

## まとめ：修正案の確度と緊急度

| # | 修正対象 | 確度 | 緊急度 | 修正規模 |
|---|---|---|---|---|
| ① | Paper 1 §2.2 line 58 SAHI 対比 | 高（軽微〜中） | 中 | 1〜3文 |
| ② | Paper 2 §2 line 118 D&S 体系化 | 中（軽微） | 低 | 1語〜1文 |
| ③ | Paper 2 §2.3 line 126 Natarajan IEA Task 42 | **高（重大）** | **高** | 1文 |
| Bonus | Paper 1 / 3 LifeWind 引用追加 | 中 | 低（任意） | 1〜2文新規追加 |

**緊急度高（修正必須）**：③ Natarajan IEA Wind Task 42 誤帰属（重大ハルシネーション）

**WAKABA 取得待ち4本（Vera-Tudela 2017 / Dimitrov 2015 / Hu 2025 / Yang 2013）の精読後に統合確定するもの**：
- line 126 第2文「DEL マトリクス機種依存性・TI 計測精度」の最終再構成（Tautz-Weinert 候補1）
- line 99「bin-averaged vs 直接計測 TI」の引用先確定（パターン P1/P2/P3）
- Hu 2025 / Yang 2013 の引用統合判断

---

## 次のステップ

1. himinさんが取得待ち4本を入手したら、本ファイルの修正案を踏まえて Paper 2 v9.5 の統合修正案を策定
2. 緊急度の高い修正③（Natarajan）は、4本待たずに先行適用することも可能（独立した修正）
3. Paper 1 修正案①（SAHI）も独立適用可能
