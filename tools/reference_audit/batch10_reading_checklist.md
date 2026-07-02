# 第10バッチ精読チェックリスト

**作成日**: 2026-04-27（待機作業 C）
**対象論文**: Vera-Tudela & Kühn (2017) ／ Dimitrov, Natarajan, Kelly (2015)
**目的**: PDF 取得後の精読を効率化し、Paper 2 line 126 / line 99 の最終再構成判断を確定する

---

## 0. 取得方法（himinさん用）

### Vera-Tudela & Kühn (2017)

| 項目 | 値 |
|---|---|
| タイトル | Analysing wind turbine fatigue load prediction: The impact of wind farm flow conditions |
| 著者 | Luis Vera-Tudela, Martin Kühn |
| 雑誌 | Renewable Energy |
| 巻/頁 | 107, 352–360（**約 9 頁**） |
| 年 | 2017 年 7 月 |
| DOI | 10.1016/j.renene.2017.01.065 |
| 出版社 | Elsevier ScienceDirect |
| OA 状態 | closed（OpenAlex / Unpaywall 確認済） |

**取得経路**：
1. **WAKABA → libproxy.ouj.ac.jp → ScienceDirect → DOI 検索 → 「Download PDF」 or 「View PDF」**（推奨）
2. ILL（文献複写依頼）— 1〜2週間
3. Read Online（ScienceDirect の Read Online 機能、ブラウザ表示のみ）

### Dimitrov, Natarajan, Kelly (2015)

| 項目 | 値 |
|---|---|
| タイトル | Model of wind shear conditional on turbulence and its impact on wind turbine loads |
| 著者 | Nikolay Dimitrov, Anand Natarajan, Mark Kelly |
| 雑誌 | Wind Energy |
| 巻/号/頁 | 18(11), 1917–1931（**約 15 頁**） |
| 年 | 2015 年 11 月 |
| DOI | 10.1002/we.1797 |
| 出版社 | Wiley Online Library |
| OA 状態 | closed（OpenAlex / Unpaywall 確認済） |

**取得経路**：
1. **WAKABA → libproxy.ouj.ac.jp → Wiley Online Library → DOI 検索 → 「PDF」**
   - ※ 既存の確認結果：Read Online は可能だが PDF DL 不可の可能性あり。WAKABA 経由で再確認が必要
2. ILL — 1〜2週間
3. Read Online のみ可能な場合：himinさん側で精読・要点抜粋

---

## 1. 検証対象：Paper 2 line 126 の主張分解

### 現状の引用文（v9.4 後）

> SCADAベースの風車状態監視は **Tautz-Weinert & Watson (2017)** [4] がレビューしている。
> SCADAからDELを推定するアプローチは、**DELマトリクスの機種依存性とTI計測精度の問題から限定的である**。
> **Vera-Tudela & Kühn (2017)** [20] は **SCADA信号からの疲労荷重予測を実証** し、
> **Dimitrov et al. (2015)** [12] は **乱流強度が荷重に与える影響を定量化** した。
> **Colone (2018)** [11] は wind farm scale で運用 SCADA（pitch alarm log）と aeroelastic simulation を組み合わせた fatigue load mapping の枠組みをPCE surrogate modelで構築し、turbulence と wake angle が blade root flapwise DEL の主要 driver であることをSobol感度解析で示した（v9.4で修正済 ✅）。
> **Herp et al. (2018)** [21] はベイズ推定による故障予測を試みている（第7バッチで確認済 ✅）。
> **IEA Wind Task 42（寿命延長）[19]** では、SCADAベースの荷重評価が寿命延長判断の重要な入力とされており、本研究はこの文脈に位置づけられる。

### 主張の分解と検証要件

| 主張 | 帰属先 | 検証ステータス | 第10バッチで確認すべきこと |
|---|---|---|---|
| **A.** SCADA ベース CM のレビュー | Tautz-Weinert 2017 [4] | ✅ 第7バッチで全頁精読・整合 | — |
| **B.** SCADA から DEL 推定の限定要因 = DELマトリクス機種依存性 ＋ TI計測精度 | （無帰属の一般論） | ⚠️ Tautz-Weinert 2017 には明示記述なし（候補1） | Vera-Tudela / Dimitrov に該当議論があれば帰属先として追加可能か判定 |
| **C.** SCADA 信号からの疲労荷重予測を「実証」 | Vera-Tudela & Kühn 2017 [20] | ❓ 未検証 | **Abstract レベルで「fatigue load prediction」が論文の主軸か確認**。現在の表現「実証」が論文の実態（モデル提案/検証/比較のいずれか）に合致するか |
| **D.** 乱流強度が荷重に与える影響を「定量化」 | Dimitrov et al. 2015 [12] | ⚠️ **Abstract レベルで疑義あり** | 詳細は §2 を参照 |
| **E.** Wind farm scale fatigue load mapping を PCE で構築・Sobol で turbulence/wake が blade root DEL 主要 driver | Colone 2018 [11] | ✅ 第9バッチ前半で全頁精読・確定 | — |
| **F.** ベイズ推定による故障予測 | Herp et al. 2018 [21] | ✅ 第7バッチで全頁精読・整合 | — |
| **G.** SCADA ベース荷重評価 = 寿命延長判断の重要入力 | IEA Wind Task 42 [19] | 未精読 | （対象外、別途検証） |

---

## 2. 重要な事前疑義：Dimitrov et al. 2015 の主張帰属

### Abstract から確定済の事実（Crossref 取得）

> "Model of wind shear conditional on turbulence and its impact on wind turbine loads"
>
> "We analyse high-frequency wind velocity measurements from two test stations over a period of several years and at heights ranging from 60 to 200 m, with the objective to validate **wind shear predictions** as used in load simulations for wind turbine design."
>
> "An essential contribution is the **conditioning of wind shear on the 90% quantile of wind turbulence**, such that the appropriate magnitude of the design fatigue load is achieved."
>
> "The fatigue loads over different turbine components are evaluated under the full wind measurements..."
>
> "...the effect of wind shear is most pronounced on the **blade flap loads**."
>
> "...under moderate wind turbulence, the **wind shear exponents may be over-specified in the design standards**..."

### Abstract レベルで判明する論文の主題

- **主題**: 「**wind shear** モデルを turbulence の 90% quantile で条件付けし、IEC 61400-1 ed.3 の wind shear 仕様より精度の高い疲労荷重予測を達成」
- **モデルの中心変数**: wind shear exponent α（条件付き分布）
- **TI の役割**: wind shear モデルの **conditioning variable**（TI 自体を直接モデリングするわけではない）
- **DEL/荷重の評価対象**: blade flap loads が最も影響を受ける
- **Wöhler exponent (m) の感度評価**: 含まれる

### Paper 2 line 126 現状表現「乱流強度が荷重に与える影響を定量化した」の判定

⚠️ **Abstract レベルで以下の点が不正確の可能性**：
- Dimitrov 2015 は **TI 自体ではなく、TI で条件付けられた wind shear** が荷重に与える影響を定量化している
- 「TI が荷重に与える影響」は副次的な結果（wind shear のモジュレーション経由）
- より正確な表現候補：「Dimitrov et al. (2015) [12] は **wind shear を turbulence quantile で条件付ける**ことで、特に blade flap loads に対する設計荷重予測の精度を改善する確率モデルを提案した」

→ **第10バッチでの全頁精読時の検証ポイント①（最重要）**：上記の精緻化候補が論文中の実態と一致するか確認

---

## 3. 検証対象：Paper 2 line 99 の代替引用先候補

### 現状（v9.4 後）

> **bin-averaged vs. 直接計測TIの実データ差異**: 約4倍の差を実サイトデータで確認（既存文献での同種指摘の有無は第10バッチで Vera-Tudela & Kühn 2017 / Dimitrov et al. 2015 を全頁精読後に確定）

### 適合性チェック項目

| 観点 | Vera-Tudela 2017 | Dimitrov 2015 |
|---|---|---|
| **TI の算出方法**（IEC 準拠 / bin-averaged / 直接計測 / 他） | ❓ 要確認 | ❓ 要確認（Abstract に明示なし） |
| **TI 計測精度に関する議論の有無** | ❓ 要確認 | ❓ 要確認 |
| **bin-averaged vs 10分値直接計測の比較記述** | ❓ 要確認 | ❓ 要確認（Abstract から見て可能性は低い） |
| **TI 算出方法論の DEL 推定への影響** | ❓ 要確認 | ❓ 要確認 |
| **実機 SCADA データ使用の有無** | ❓ 要確認 | ✅ "high-frequency wind velocity measurements from two test stations" — 実測データだが SCADA かは要確認 |

### 想定される結論パターン

| パターン | 内容 | line 99 の修正 |
|---|---|---|
| **P1**：両論文とも該当議論あり | bin近似 vs 直接計測の比較を実施 | Vera-Tudela / Dimitrov のいずれか/両方を line 99 引用先に追加 |
| **P2**：片方のみに該当議論あり | 例：Vera-Tudela に "TI computation method affects load prediction" 記述 | 該当論文を line 99 引用先に追加 |
| **P3**：両論文とも該当議論なし | TI 計測の方法論差異は本研究独自の知見として記述 | 「既存文献に同種の定量化なし、本研究独自の発見」と表現変更（誇張なし） |

→ **第10バッチでの全頁精読時の検証ポイント②**：上記いずれのパターンに該当するか確定

---

## 4. Tautz-Weinert 2017 候補1 再評価

### 現状（候補1 = 軽微な精緻化候補）

Paper 2 line 126 第2文「SCADA から DEL を推定するアプローチは、**DEL マトリクスの機種依存性と TI 計測精度** の問題から限定的である」は、Tautz-Weinert 2017 全頁精読の結果、**本論文に明示記述なし**と確定済（第7バッチ、2026-04-27）。

### 第10バッチで再評価する判断軸

- Vera-Tudela 2017 / Dimitrov 2015 のいずれかに「DEL マトリクス機種依存性」「TI 計測精度」の議論が明確にあれば、**それらを帰属先として line 126 第2文を再構成**できる
- 両論文とも該当議論がない場合、**line 126 第2文を一般論として保持**（無帰属）するか、**削除して Paper 2 §3.5 や §5.2 の本研究独自の発見**として組み替えるかを判断

### 候補1 の最終処理パターン

| パターン | 内容 |
|---|---|
| **Q1**：Vera-Tudela / Dimitrov のいずれかに該当議論あり | 帰属先を追加（line 126 第2文の出典明示） |
| **Q2**：該当議論が両論文とも見当たらない | 一般論として保持 or 削除（第10バッチ後に確定） |

---

## 5. 章単位の精読チェックリスト

### Vera-Tudela & Kühn (2017) — 約 9 頁

| 章 | 推定頁数 | 重点確認項目 | 該当する Paper 2 主張 |
|---|---|---|---|
| Abstract + Keywords | 0.5 | 主題・主要寄与の確認 | 主張 C / D 全般 |
| §1 Introduction | 1–1.5 | wind farm flow conditions の文献レビュー、本論文のスコープ | コンテキスト把握 |
| §2 Methodology | 2–3 | 使用データセット、TI 算出方法、wind farm flow modeling、fatigue load 計算アルゴリズム | **TI 算出方法論**（line 99 候補） |
| §3 Results | 2–3 | fatigue load prediction の検証結果、wind farm flow conditions の影響定量化 | 主張 C「予測を実証」 |
| §4 Discussion | 1 | TI 計測精度・DEL 機種依存性に関する議論 | **候補1 の代替帰属候補** |
| §5 Conclusions | 0.5 | 主要結論 | 主張全般 |
| References | 0.5 | （副次） | — |

### Dimitrov, Natarajan, Kelly (2015) — 約 15 頁

| 章 | 推定頁数 | 重点確認項目 | 該当する Paper 2 主張 |
|---|---|---|---|
| Abstract + Keywords | 0.5 | 主題・主要寄与の確認（既に取得済） | 主張 D の精緻化 |
| §1 Introduction | 1.5 | wind shear modeling の先行研究、本論文のスコープ | — |
| §2 Wind measurements and data | 2 | 2 test stations、measurement heights 60–200 m、サンプル長 | TI 計測の実態 |
| §3 Wind shear model | 3–4 | wind shear exponent α の確率モデル、turbulence quantile 条件付け | **主張 D の主軸** |
| §4 Load simulations | 2–3 | aeroelastic simulation 設定、IEC 61400-1 ed.3 比較、Wöhler exponent | DEL 評価対象 |
| §5 Results | 2–3 | blade flap loads / tower base / monopile への影響、wind shear exponent の妥当性 | **主張 D の核心** |
| §6 Conclusions | 0.5–1 | 設計標準との比較、design fatigue load への含意 | line 126 引用文修正の根拠 |
| References | 0.5 | （副次） | — |

---

## 6. 完全精読ルール準拠の確認手順

himinさんの指示（`feedback_reference_verification.md`「完全精読ルール」項）：
- ページ数に関わらず**全頁精読**（戦略 A）
- **主張駆動**：引用文の各主張を分解 → 論文中の対応箇所を特定 → 完全一致を検証
- **検証粒度を明示**：「全頁精読・主張駆動」「Abstract確認のみ」を区別して報告

### 第10バッチ精読時の手順

1. **Step 1**：両論文の Abstract / Conclusions を最初に読み、主題と本論文の主軸を確認
2. **Step 2**：本論文 §1 Methodology / §2 Wind measurements 等 → 使用データ・TI 算出方法を確認
3. **Step 3**：Results / Discussion → 上記 §1〜4 の検証要件と照合
4. **Step 4**：本論文の主張と Paper 2 line 126 / line 99 の現状記述を**1対1で対応付け**
5. **Step 5**：精緻化候補 / ハルシネーション疑義をリスト化
6. **Step 6**：Paper 2 v9.5 修正案を策定（複数案を提示してhiminさん判断）

### 報告フォーマット

第10バッチ完了報告は、これまでのバッチと同形式：
- 章別精読結果テーブル（章 / ページ / 主題 / 結果）
- 主張駆動検証結果テーブル（主張 / 結果 / 根拠）
- ハルシネーション診断（重大 / 軽微 / 候補）
- Paper 2 v9.5 修正案

---

## 7. 第10バッチ着手時の即時アクション

PDF 取得確認後、以下の順で着手します：

1. ✅ 両論文のファイル配置確認（`docs/references/need_ouj_remote/` または同等パス）
2. ✅ 本チェックリストを開いて検証要件を再確認
3. → **Vera-Tudela 2017** から精読開始（短い・ 9 頁）
4. → **Dimitrov 2015** 精読（長め・ 15 頁、Abstract 取得済）
5. → 検証結果を本ファイルに追記（章別結果テーブル）
6. → Paper 2 v9.5 修正案策定 → himinさん判断 → 適用
7. → memory `project_blade_paper_audit_progress.md` 更新

### Read Online のみで進める場合の補助

himinさんが Wiley などで Read Online 抜粋を行う場合：
- **章単位で章タイトル＋主要図表＋結論段落の写経**を上記 §5 のチェックリスト順に行えば、Claude Code が同じ精読粒度で検証可能
- 本ファイル §5 のチェック項目を直接コメントとしてhiminさんが記入する形でも進行可

---

## 第10バッチ準備完了チェックリスト

- [x] Vera-Tudela 2017 / Dimitrov 2015 の Crossref 書誌完全整合確認（待機作業 A）
- [x] 取得方法の整理（WAKABA / ILL / Read Online）
- [x] Paper 2 line 126 の主張分解（A〜G、7主張）
- [x] Dimitrov 2015 の Abstract レベル疑義抽出（精緻化候補③）
- [x] Paper 2 line 99 の3パターン（P1/P2/P3）想定
- [x] Tautz-Weinert 候補1 の再評価軸（Q1/Q2）整理
- [x] 章単位の精読チェックリスト（両論文、全頁分）
- [x] 完全精読ルール準拠の手順
- [x] **第1ラウンド先行精読 3本完了（取得済）**：
  - Akyon 2022 SAHI 全5頁 ⚠️ Paper 1 line 58 対比文不正確 → `batch10_round1_revision_proposals.md` 案①
  - Downing & Socie 1982 全10頁 ⚠️ Paper 2 line 118「体系化」表現強すぎ → 案②
  - Natarajan 2020 LifeWind 全110頁 ❌ **Paper 2 line 126 重大ハルシネーション**（IEA Wind Task 42 → EUDP LifeWind project）→ 案③（緊急修正必須）
- [x] 取得待ち4本の Crossref 書誌再検証（2026-04-27）：
  - Vera-Tudela 2017 [20]：DOI `10.1016/j.renene.2017.01.065` 整合 ✅
  - Dimitrov 2015 [12]：DOI `10.1002/we.1797` 整合 ✅、OpenAlex から Abstract 完全取得済
  - Hu 2025 [TBD]：DOI `10.1016/j.renene.2024.122332` 整合 ✅、Abstract 未取得（要 WAKABA）
  - Yang 2013 [P3-17]：DOI `10.1016/j.renene.2012.11.030` 整合 ✅、Abstract 未取得（要 WAKABA）
- [ ] PDF 取得（himinさん作業中、2026-04-27）
- [ ] 第10バッチ第2ラウンド精読実施（取得後）
- [ ] Paper 2 v9.5 統合修正案策定・適用（第2ラウンド完了後）

## 第1ラウンド完了状況（2026-04-27）

### 取得済3本の精読結果サマリ

| 論文 | 頁 | 結果 | Paper 修正必要度 |
|---|---|---|---|
| Akyon 2022 SAHI | 5 | ⚠️ 軽微〜中 | Paper 1 §2.2 line 58（差別化表現） |
| Downing & Socie 1982 | 10 | ⚠️ 軽微 | Paper 2 §2 line 118（語彙精緻化） |
| Natarajan 2020 LifeWind | 110 | ❌ **重大** | **Paper 2 §2.3 line 126（プロジェクト名修正必須）** |

### 重要な副次成果

- **新ハルシネーションパターン発見**：「プロジェクト・ファンド名ハルシネーション」（Natarajan 2020：書誌は正しいが「IEA Wind Task 42」は完全な誤帰属、実態は「EUDP LifeWind project」）。Crossref API では検出不可能。`feedback_reference_verification.md` に新パターンとして記録済み
- **Paper 1/3 への引用候補発見**：Natarajan 2020 §8 IEC 61400-28 推奨で「Special focus should be made to: **Leading edge erosion of blades**」と明示。Industry relevance 強化材料として Paper 1/3 で引用可能

