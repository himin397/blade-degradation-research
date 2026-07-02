# B6: 監査全体の中間サマリ

**作成日**: 2026-04-29（コンパクト後の B 群一括実施完了時点）
**対象期間**: 2026-04-04 〜 2026-04-29（第1〜10バッチ第2ラウンド-A まで）
**目的**: 監査全体の進捗・成果・残作業を一目で把握できる集約ドキュメント

---

## 1. 監査の到達点

### バッチ別精読完了状況

| バッチ | 期間 | 対象論文 | 結果 |
|---|---|---|---|
| 第1〜9バッチ | 2026-04-04 〜 04-26 | 30本 | 主張駆動精読完了 |
| 第10バッチ第1ラウンド | 2026-04-27 | 3本（Akyon / Downing & Socie / Natarajan） | 完了、修正案①②③策定（③適用済） |
| 第10バッチ第2ラウンド-A | 2026-04-29（コンパクト前後） | 3本（Hu 2025 / Yang 2013 / Gohar 2025） | 完了、Paper 3 line 94/100/102 すべて完全整合 |
| **第10バッチ第2ラウンド-B** | **未実施** | **7本（WAKABA待ち）** | **取得待ち** |

合計：**精読完了 36本 / 取得済 41本**（41本のうち 5本は補助参照のみ精読、36本は主張駆動精読）

### Paper 別の改訂履歴

| Paper | 現バージョン | 主要修正 |
|---|---|---|
| Paper 1 | v9.2（2026-04-27） | 引用ハルシネーション 4 件（Bir & Jonkman / Shihavuddin / Malik / Mandell）+ Konovalenko/Deitsch 表現精緻化 |
| Paper 2 | **v9.5**（2026-04-27） | 引用ハルシネーション 5 件（Bir & Jonkman / Robertson / Hayman / Mandell / Colone / **Natarajan IEA Wind Task 42 → EUDP LifeWind**） |
| Paper 3 | v5.3（2026-04-27） | 引用ハルシネーション 3 件（Branlard タイトル / Pandit 引用文 / Maldonado-Correa 主旨） |

---

## 2. ハルシネーション分類別集約

### 2.1 重大ハルシネーション（修正済）

第1〜10バッチで発見された **重大引用ハルシネーション** は以下の 4 件：

| # | 発見バッチ | 論文 | ハルシネーション内容 | 適用済 Paper |
|---|---|---|---|---|
| 1 | 第8バッチ | Bir & Jonkman 2007 | NREL 5MW aeroelastic stability 論文に「スケーリング則の限界」「翼型空力データの機種固有性」「幾何スケーリング限界」の議論なし | Paper 2 v9.0（[11] 削除、参考文献繰り上げ） |
| 2 | 第9バッチ | Pandit 2023 | "正常挙動モデリング・異常検知・残余寿命推定の3段階を整理" → 本文に存在しない（実態は Regression vs Classification の2分類） | Paper 3 v5.2 |
| 3 | 第9バッチ | Colone 2018 | Article I（Ocean Engineering）は引用文の出典として不適切 → PhD thesis 全体に差し替え | Paper 2 v9.4（[11] 差し替え + 引用文修正） |
| 4 | 第10バッチ第1ラウンド | Natarajan 2020 LifeWind | "IEA Wind Task 42（寿命延長）" → 実態は **EUDP LifeWind project**（IEA Wind Task 42 への言及一切なし） | Paper 2 v9.5 |

#### パターン分類
- **論文主題ハルシネーション**: 1（Bir & Jonkman）
- **手法分類ハルシネーション**: 1（Pandit）
- **書誌差し替え**: 1（Colone Article I → PhD thesis）
- **プロジェクト名ハルシネーション**: 1（Natarajan IEA Wind Task 42 → EUDP LifeWind）

→ **新パターン「プロジェクト・スポンサー名ハルシネーション」**を 2026-04-27 に発見し、`memory/feedback_reference_verification.md` に記録済

### 2.2 軽微ハルシネーション・表現精緻化（修正済）

| # | 論文 | 内容 | 適用 |
|---|---|---|---|
| 1 | Shihavuddin 2019 | mAP=81.1% は IoU=0.3 / EasyInspect dataset / Inception-ResNet-V2 | Paper 1 v9 |
| 2 | Hayman 2012 | DEL正規化フレームワークと f^eq=1Hz, T_eq=600s の出典分離 | Paper 2 v9.3 |
| 3 | Mandell 1997 | b=0.10 と n=11.6 の数学的等価性ではなく独立支持として位置づけ | Paper 2 v9.2 |
| 4 | Robertson 2017 | OC5 Phase II は floating semisubmersible で onshore とは適用条件異なる | Paper 2 v9.1 |
| 5 | Malik & Bak 2025 | "experimentally" → "aeroelastic simulation" | Paper 1 v9.1 |
| 6 | Branlard 2020 | タイトル "real-time load and fatigue estimation" 完全形式 | Paper 3 v5.1 |
| 7 | Maldonado-Correa 2020 | "データ融合手法を整理" → "AIベース状態監視手法を体系的にレビュー" | Paper 3 v5.3 |
| 8 | Akyon 2022 SAHI（修正案①未適用） | 「Multi-scale patch augmentation has improved recall」表現 | Paper 1 v9.2（一部適用） |
| 9 | Downing & Socie 1982（修正案②未適用） | 「計算アルゴリズムを体系化」表現 | 未適用（A2 で判断待ち） |

### 2.3 ハルシネーション率の評価（更新版）

| バッチ範囲 | 精読本数 | 重大件数 | 軽微件数 | 重大率 |
|---|---|---|---|---|
| 第1〜9バッチ後 | 30本 | 3件（Bir & Jonkman / Pandit / Colone） | 7件 | 10% |
| **第10バッチ完了後（第2ラウンド-B 取得前）** | **36本** | **4件**（+ Natarajan） | **9件** | **11%** |

→ ハルシネーション率は依然として 10% 程度。第10バッチ第2ラウンド-B（7本）の精読により最終的な率が確定する見込み。

---

## 3. B 群作業の成果（2026-04-29 一括実施）

### B1: Crossref 自己監査結果

- **対象**: 31本の DOI 保有引用
- **完全整合**: 30/31本（97%）
- **🚨 修正候補 1件**: **Paper 2 [21] Herp 2018 に DOI 追加**（正しい DOI: `10.1016/j.renene.2017.02.069`）

→ B1 結果は `B1_crossref_audit_2026-04-29.md` に詳述

### B4: 第10R2-B 7本の書誌最終確認

- 全 7 本（Vera-Tudela / Dimitrov / Cha / Dao / Liu / Nielsen / Yeter）の Crossref 書誌情報を確認
- すべて Paper 内引用と整合
- 取得後すぐ精読に入れる状態

### B5: 副次発見の引用候補集

第10バッチで発見された Paper 1/2/3 への引用候補を整理：

| 候補 | 該当 Paper | 優先度 | 内容 |
|---|---|---|---|
| P1-A | Paper 1 §2.2 | 中 | Gohar 2025 §3.4 SAHI 位置づけ引用（修正案①と統合） |
| P1-B | Paper 1 §1 | **高** | Natarajan 2020 IEC 61400-28 推奨（産業意義） |
| P3-A | Paper 3 §1/§6 | **高** | Hu 2025 §4 Limitations 1（fatigue gap）→ 研究意義裏付け |
| P3-B | Paper 3 §2.2 | 中 | Yang 2013 fault detection vs degradation prediction 対比 |
| P3-C | Paper 3 §6 | 中 | Gohar 2025 §5 Future Directions（few-shot, multi-labelling） |
| P3-D | Paper 3 §1 | **高** | Natarajan 2020 IEC 61400-28 推奨 |

→ B5 結果は `B5_incidental_findings_citation_candidates_2026-04-29.md` に詳述

### B2: 既精読論文 41本の核心数値リスト化

Paper 1/2/3 で外部論文から引用している数値・式・表番号を引用箇所と引用元の対応で整理。**将来の細部精読フェーズの準備として活用可能**。

| Paper | 数値引用グループ | 高優先度（細部精読対象） |
|---|---|---|
| Paper 1 | 7 グループ | なし（v9 で精緻化済） |
| Paper 2 | 9 グループ | **P2-N1 Mandell 1997**（9個の数値・式・図表番号）、**P2-N6 IEC 61400-1:2019**（規格項番複数） |
| Paper 3 | 4 グループ | なし（既に精緻化済） |

→ B2 結果は `B2_core_numerical_claims_2026-04-29.md` に詳述

### B3: 内部自己整合性チェック

| 区分 | 結果 |
|---|---|
| Paper 2 | ✅ 完全整合 |
| Paper 3 | ✅ 完全整合 |
| Paper 1 | ⚠️ 改善推奨 2 件 |

#### Paper 1 の改善推奨

| # | 問題 | 影響度 |
|---|---|---|
| A7 | Table 1 (0.581) vs Table 2 (0.561) の「5-class mAP@0.5」値の不一致 | 中（査読で指摘されうる） |
| A8 | LE;CR 比率 1.6% (パッチ) vs 10.2% (インスタンス) の文脈表記 | 低（technically correct だが読者混乱を招きうる） |

→ B3 結果は `B3_internal_consistency_check_2026-04-29.md` に詳述

---

## 4. A 群（himinさん判断待ち）の現状

### 既存の A1-A5 + 新規 A6-A8

| # | 案件 | 状態 | 工数 |
|---|---|---|---|
| A1 | 修正案①（Paper 1 §2.2 Akyon SAHI 対比表現、A/B/C 案策定済） | 判断待ち | 小 |
| A2 | 修正案②（Paper 2 §2 Downing & Socie 「体系化」表現、A/B/C 案策定済） | 判断待ち | 小 |
| A3 | Paper 1/3 への IEC 61400-28（Natarajan 2020）引用追加 | 判断待ち | 中（書誌追加要） |
| A4 | Paper 1/3 への Gohar 2025 副次発見引用追加（P1-A, P3-A, P3-B, P3-C） | 判断待ち | 小 |
| A5 | Paper 2 line 99 引用先確定（bin-averaged vs 直接計測 TI） | 過去から保留 | 中 |
| **A6（新）** | **Paper 2 [21] Herp 2018 に DOI 追加**（B1 で発見） | **判断待ち** | 小 |
| **A7（新）** | **Paper 1 Table 1 (0.581) vs Table 2 (0.561) の脚注追加**（B3 で発見） | **判断待ち** | 小 |
| **A8（新）** | **Paper 1 LE;CR 比率 1.6% / 10.2% の関係性説明追加**（B3 で発見） | **判断待ち** | 小 |

---

## 5. 残作業（B 群完了後の次ステップ）

### 第10バッチ完了に必要な作業

1. **第10R2-B 7本の取得**（WAKABA 取得待ち）
   - Vera-Tudela & Kühn 2017
   - Dimitrov 2015
   - Cha 2017
   - Dao 2018
   - Liu 2024
   - Nielsen & Sørensen 2011
   - Yeter 2020

2. **取得後の主張駆動完全精読**
   - 各論文の Paper 内引用箇所との整合性検証
   - 副次発見があれば B5 に追記

### 第10バッチ完了後の作業

3. Paper 2 v9.6 統合修正案策定（A1-A8 の選択結果に基づく）
4. Paper 2 line 99 引用先確定（A5）
5. Tautz-Weinert 候補1 の最終再評価（保留中）

### 投稿準備フェーズ

6. **論文取得完了 + himinさん希望時**: 主要先行研究 5〜10 本の核心数値細部精読（B2 リスト活用）
7. **投稿前**: 番号引用スタイル統一（Paper 1 のハイブリッド形式 → 統一形式へ移行検討）

---

## 6. 監査全体の信頼性評価（Claude Code の自己評価）

### 信頼性が高い領域

| 領域 | 評価 | 根拠 |
|---|---|---|
| 書誌情報（著者・年・ジャーナル・DOI） | 高 | Crossref 30/31本完全整合（B1）、第10R2-B 7本も整合（B4） |
| 引用文の論理整合性 | 中〜高 | 主張駆動精読で重大ハルシネーション 4 件発見・修正済。10% 残存リスク |
| Paper 内部の数値整合性 | 高（Paper 2/3）/ 中（Paper 1） | Paper 1 で 2 件の改善推奨事項 |
| 図表番号・章番号の整合性 | 高 | すべて整合 |

### 信頼性に留保がある領域

| 領域 | 評価 | 根拠・対応 |
|---|---|---|
| 引用文中の細かい数値（mAP/精度の桁数等） | 中 | 画像認識ベースの精読は誤認余地あり。B2 リストで細部精読の準備済 |
| 引用していない関連分野の最新研究の網羅性 | 中 | `project_literature_review_schedule.md` で半年ごとの更新計画あり |
| 第10R2-B の 7 本 | 未検証 | 取得後に主張駆動精読が必要 |

---

## 7. 関連ドキュメント

| ドキュメント | 用途 |
|---|---|
| `B1_crossref_audit_2026-04-29.md` | 書誌レベルの監査結果（DOI 検証） |
| `B2_core_numerical_claims_2026-04-29.md` | 核心数値の引用箇所対応リスト |
| `B3_internal_consistency_check_2026-04-29.md` | Paper 内部の整合性チェック結果 |
| `B5_incidental_findings_citation_candidates_2026-04-29.md` | 副次発見の引用候補集 |
| `batch10_round1_revision_proposals.md` | 第10バッチ第1ラウンド修正案 |
| `batch10_round2A_progress_2026-04-29.md` | 第10バッチ第2ラウンド-A 精読記録 |
| `acquisition_status_2026-04-29.md` | 参考文献取得状況 |
| `memory/project_blade_paper_audit_progress.md` | 監査全体の進捗（memory） |
| `memory/feedback_reference_verification.md` | 参考文献検証ルール |
| `memory/reference_iec61400_28_blade_erosion.md` | IEC 61400-28 推奨記録 |

---

## 8. 結論

第1〜10バッチ第2ラウンド-A までの監査により、**Paper 1/2/3 の書誌レベルおよび論理レベルでの整合性は概ね確保**されています。

**残存課題**:
- 第10R2-B 7本の取得・精読
- A 群 8 件（A1-A8）の判断
- 投稿前の細部数値精読（任意、希望時）

**Claude Code の役割**:
- 取得後の主張駆動精読は実施可能
- A 群判断は himinさん の判断（Claude Code が判断すべきでない）
- 細部精読は himinさんの指示があれば即実施可能（B2 リスト準備済）
