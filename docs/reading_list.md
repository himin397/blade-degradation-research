# ブレード劣化予測研究：推奨読書リスト

**作成日**: 2026-04-14
**目的**: Paper 1-3の理解深化、卒論・修士研究のための知識整備
**優先度基準**:
- ★★★：卒論までに必須
- ★★：修士までに読むと研究が深まる
- ★：博士以降または興味があれば

---

## A. 数学・統計（基礎）

| 書籍 | 優先度 | 用途 |
|---|---|---|
| **統計学入門（基礎統計学Ⅰ）**（東京大学出版会） | ★★★ | 平均・分散・分布・回帰。Paper 2のDEL統計で必要 |
| **線形代数入門**（東京大学出版会） | ★★★ | 機械学習の数式理解の基礎 |
| **数学ガール シリーズ**（結城浩） | ★★ | 数学への入門として読みやすい |
| **自然科学の統計学**（東京大学出版会） | ★★ | 統計学入門の次に読む中級書 |

---

## B. 機械学習・深層学習

| 書籍 | 優先度 | 用途 |
|---|---|---|
| **ゼロから作るDeep Learning**（斎藤康毅） | ★★★ | 日本語で最も読みやすい深層学習入門。CNN/YOLOの基礎理解に最適 |
| **Pattern Recognition and Machine Learning（PRML）**（Bishop） | ★★ | 機械学習の古典。必要な章（クラス分類、正則化等）だけ読めばよい |
| **Deep Learning**（Goodfellow, Bengio, Courville）[無料](https://www.deeplearningbook.org/) | ★★ | 深層学習の標準教科書。英語だが章ごとに読める |
| **深層学習**（岡谷貴之、機械学習プロフェッショナルシリーズ） | ★★ | 日本語の深層学習教科書 |
| **Neural Networks and Deep Learning: A Textbook**（Aggarwal） | ★ | 数学的厳密性が高い |
| **Hands-On Machine Learning**（Géron） | ★★ | 実装重視。scikit-learn、TensorFlow、Kerasを使う |

---

## C. コンピュータビジョン・物体検出

| 書籍 | 優先度 | 用途 |
|---|---|---|
| **Deep Learning for Computer Vision with Python**（Rosebrock） | ★★★ | 物体検出・YOLOの実装を学ぶのに直接役立つ |
| **Modern Computer Vision with PyTorch, 2nd Ed**（Ayyadevara, 2024） | ★★ | 2024年刊。transformers、GANs、zero-shot detection等の最新手法 |
| **コンピュータビジョン（放送大学テキスト、浅井紀久夫）** | ★★★ | **浅井先生の教科書**。面談前に目を通すべき |
| **ディープラーニングによる物体検出の基礎**（関連Qiita記事等） | ★★★ | 論文（YOLO, Faster R-CNN等）の原典を読むのが最も効率的 |

### 原論文（★★★、教科書より優先）

| 論文 | 内容 |
|---|---|
| **Redmon et al. (2016) "You Only Look Once"** | YOLO原論文 |
| **Ultralytics YOLOv8 Documentation** | YOLOv8の公式仕様 |
| **Lin et al. (2017) "Focal Loss"** | クラス不均衡対処。卒論テーマ案Aで使用 |
| **Akyon et al. (2022) "SAHI"** | パッチベース検出の枠組み |
| Paper 1の参考文献リスト全16件 | 既に整理済み |

---

## D. 風力工学・疲労・構造力学

| 書籍 | 優先度 | 用途 |
|---|---|---|
| **Wind Energy Handbook**（Burton et al., Wiley） | ★★★ | 風力工学の**決定版教科書**。ブレード、荷重、制御すべて網羅 |
| **Wind Turbine Aerodynamics and Vorticity-Based Methods**（Branlard） | ★★ | OpenFASTベースで空力を学ぶ |
| **Aerodynamics of Wind Turbines**（Hansen, M.O.L.） | ★★ | ブレード空力の標準教科書 |
| **IEC 61400-1:2019**（規格書） | ★★★ | **必読**。Paper 2の根拠。JIS版（JIS C 61400-1:2025）で日本語可 |
| **Fatigue of Materials**（Suresh） | ★ | 疲労工学の古典。必要箇所だけ |
| **日本型風力発電ガイドライン（NEDO）** | ★★ | 無料PDF。日本語で風力設計の概要が分かる |

### 原論文（★★★）

| 論文 | 内容 |
|---|---|
| **Jonkman et al. (2009) "Definition of a 5-MW Reference Wind Turbine"** | NREL 5MW定義。Paper 2の基盤 |
| **Hayman (2012) "MLife Theory Manual"** | DEL算出手法の原典 |
| **Malik & Bak (2025)** | エロージョンとAEP損失。Paper 1-3全てで引用 |

---

## E. SCADAとデータ解析

| 書籍 | 優先度 | 用途 |
|---|---|---|
| **Wind Turbine Condition Monitoring**（Tautz-Weinert の総説論文等） | ★★ | SCADA由来の状態監視の手法 |
| **pandas公式ドキュメント** | ★★★ | Penmanshiel SCADA処理で使用 |
| **Time Series Analysis with Python**（Brownlee） | ★★ | 時系列解析の基礎 |

---

## F. プログラミング・実装

| 書籍 | 優先度 | 用途 |
|---|---|---|
| **リーダブルコード**（Dustin Boswell） | ★★★ | コードの書き方の基礎 |
| **Python機械学習プログラミング**（Raschka） | ★★ | scikit-learn、PyTorchの実装 |
| **PyTorch公式チュートリアル**（無料） | ★★★ | YOLOv8の内部を理解するため |

---

## G. 研究方法論・論文執筆

| 書籍 | 優先度 | 用途 |
|---|---|---|
| **理科系の作文技術**（木下是雄） | ★★★ | 日本語の論理的文章作成 |
| **How to Write and Publish a Scientific Paper**（Day & Gastel） | ★★ | 英語論文の書き方 |
| **卒論・修論のためのパソコン活用術**（阿部圭一等） | ★★ | 論文執筆の実務 |

---

## H. デジタルツイン・統合パイプライン（将来方向）

| 書籍 | 優先度 | 用途 |
|---|---|---|
| **Digital Twin Development and Deployment**（Grieves） | ★ | デジタルツインの概念 |
| 該当分野のレビュー論文 | ★ | 教科書はまだ成熟していない。レビュー論文で追う |

---

## 推奨優先読書順（himinさんの状況に合わせて）

### Phase 1: 卒論テーマ決定前（〜2026年6月）
1. **浅井先生の「コンピュータビジョン」テキスト** ← 面談前必読
2. **ゼロから作るDeep Learning** の該当章（CNN）
3. **YOLOv8 公式ドキュメント**

### Phase 2: 卒論着手前（2026-2028年）
4. **Wind Energy Handbook** の該当章（ブレード・疲労）
5. **IEC 61400-1:2019**（必要な部分のみ）
6. **Paper 1-3 の参考文献全件** を通読

### Phase 3: 卒論執筆中（2028-2029年）
7. **理科系の作文技術**
8. **PRML または Deep Learning Book** の必要箇所

### 各Phaseで「読まないもの」
- 関数解析、圏論、組合せ最適化などの高度な数学 → 研究には不要
- コンパイラ、OS内部実装 → himinさんの研究には関係ない
- 強化学習の教科書 → ブレード劣化予測には使わない

---

## まとめ

| カテゴリ | 絶対に読むべき本 |
|---|---|
| 卒論までに（2年間） | **3〜5冊**（浅井先生テキスト、ゼロから作るDL、Wind Energy Handbookの抜粋、IEC規格の抜粋、理科系の作文技術） |
| 修士修了までに（5年間） | **+3〜5冊** |
| 博士まで行く場合 | さらに専門書を追加 |

津築氏のように100冊以上を読む必要はありません。**精選した5-10冊 + 関連原論文50本** で卒論・修士は成立します。

---

## 注意

このリストはClaude Codeの推測が含まれています。浅井先生との面談で「どの本を読むべきか」を直接聞くのが最も確実です。放送大学の情報コースの教員推薦書がある場合、それを優先すべきです。
