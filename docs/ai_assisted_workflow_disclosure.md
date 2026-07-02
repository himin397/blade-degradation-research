# AI-Assisted Research Workflow 開示文テンプレート

最終更新：2026-05-03
用途：Paper 1/2/3 およびその後の論文・研究計画書での AI 使用開示
位置づけ：`paper_plan.md` の補助文書

このドキュメントは、論文・研究計画書において **AI（Claude Code、Codex/GPT-5.5、その他LLM）の使用範囲を学術的に適切な形で開示する** ための標準テンプレートです。Codex 独立レビューの指摘「『AI協働者』という表現は大学院文脈では強すぎる」に対応し、`AI-assisted research workflow` という中立表現を採用します。

---

## 1. 用語の選択

### 推奨用語（学術文脈）
- **AI-assisted research workflow**（AI 支援型研究ワークフロー）
- **AI-supported analysis**（AI 支援分析）
- **Computational tools including LLMs**（LLM を含む計算ツール）

### 避ける用語
- ~~AI collaborator~~（AI 協働者）：AI に主体的役割を与える印象が強い
- ~~AI co-author~~（AI 共著者）：学術倫理上問題（多くのジャーナルが AI を著者として認めない）
- ~~AI-driven~~：AI が主導している印象、実際の判断は人間が担う場合に不正確

### 理由
- 学術出版業界では、AI を「ツール」として位置づけ、判断・結論の責任は人間（著者）が負うのが標準
- ICMJE、Nature、Science の方針：AI は著者になれない（責任を負えないため）
- Asai 先生への提出時にも、AI を「自分の判断を補助する道具」として扱う表現が無難

---

## 2. 開示文の標準テンプレート

### A. 短縮版（Acknowledgments セクション末尾）

英語：
```
The authors used large language model (LLM) tools for code generation,
literature organization, figure drafting, and writing assistance. All research
questions, methodological decisions, results interpretation, and conclusions
are the authors' own. The authors take full responsibility for the content of
this paper.
```

日本語（研究計画書・国内発表用）：
```
本研究では、コード生成、文献整理、図表作成、文章化の支援に大規模言語モデル
（LLM）ツールを使用しました。研究の問い、手法の選定、結果の解釈、および結論
は著者自身の判断によるものです。本論文の内容について、著者が全責任を負います。
```

注：具体的なモデル名（Claude Opus 4.7、GPT-5.5 等）は本文に記載せず、内部記録（判断ログ・MEMORY.md）にバージョンを残す。投稿時点でモデルが旧バージョン化していると不自然になるため。

### B. 詳細版（Methods セクション内 or 別セクション「AI Usage Statement」）

英語：
```
AI Usage Statement

This research employed an AI-assisted workflow using large language model (LLM)
tools throughout the project. The specific scope of AI assistance was as
follows:

- Code generation and refactoring (Python, OpenFAST configuration).
- Literature organization and reference management. All cited references were
  independently verified by the author. Full-text review was conducted for
  references whose claims directly inform the methods, results, or conclusions
  of this paper.
- Figure drafting (matplotlib, Mermaid) with manual review and adjustment.
- Writing assistance (Japanese-to-English translation, structural editing).

The author retained full responsibility for the following:
- Definition of research questions and hypotheses
- Selection of methods and evaluation criteria
- Interpretation of results
- Determination of claim strength and uncertainty representation
- Final decisions on inclusion/exclusion of content

No AI tool was used to generate fabricated data, fabricated references, or
fabricated experimental results. The authors take full responsibility for the
content of this paper.
```

日本語版（同等内容）：
```
AI 使用に関する声明

本研究は、大規模言語モデル（LLM）ツールを用いた AI 支援型ワークフローで
実施されました。AI の使用範囲は以下の通りです：

- コード生成・リファクタリング（Python、OpenFAST 設定）
- 文献整理・参考文献管理：すべての引用文献は著者が独立に検証。手法・結果・
  結論に直接影響を与える主張については本文精読を実施
- 図表作成（matplotlib、Mermaid）、手動レビューと調整を実施
- 文章化支援（日英翻訳、構造編集）

以下については著者が全責任を負います：
- 研究の問い・仮説の設定
- 手法・評価基準の選定
- 結果の解釈
- 主張の強さ・不確実性表現の決定
- 内容の採否の最終判断

捏造データ・架空の参考文献・架空の実験結果の生成に AI を使用していません。
本論文の内容について、著者が全責任を負います。
```

---

## 3. 配置位置の選択

### Paper 1（画像損傷検出）
- **推奨**：Methods セクション末尾に「AI Usage Statement」サブセクション
- 理由：YOLOv8 自体が AI モデルなので、研究で使う AI ツールと混同を避ける必要

### Paper 2（DEL 推定）
- **推奨**：Acknowledgments セクション末尾に短縮版
- 理由：物理シミュレーション中心で AI 使用範囲が限定的

### Paper 3（統合パイプライン・予備研究）
- **推奨**：別セクション「AI Usage Statement」を独立配置
- 理由：予備研究として方法論的透明性を強調する文書

### 修論
- **推奨**：序章末尾または独立章で詳細版を提示
- 浅井先生へ別途、AI 使用に関する説明資料を準備

### 研究計画書（大学院出願用）
- **推奨**：方法論セクション内で短く明示
- 浅井先生との面談で口頭でも補足

---

## 4. 注意事項

### 投稿前のジャーナルポリシー確認（必須手順）

論文投稿の都度、以下を確認する：

1. ジャーナルの著者ガイドラインで AI 使用に関する記述を検索（"AI", "artificial intelligence", "generative", "LLM", "ChatGPT" 等のキーワード）
2. 開示の有無・配置（Acknowledgments / Methods / 専用セクション / カバーレター）の指定を確認
3. 開示すべき内容の範囲（ツール名・モデル名・使用場面）を確認
4. AI を著者として認めない方針（ICMJE、Elsevier、Springer Nature 等の主要出版社で標準）に準拠
5. 既存の本テンプレートをジャーナル指定に合わせて修正

主要出版社の方針（2026年5月時点・参考）：
- **ICMJE**：AI は著者になれない、Acknowledgments で使用範囲を明示
- **Nature**：使用したツールと範囲の明示、生成 AI のテキストは引用とせず
- **Elsevier**：Methods 内 or Statement での開示、AI を著者リストに含めない
- **IEEE**：使用ツール明示、AI は著者になれない、責任は人間著者

最新方針は投稿時に必ず原文確認すること（変動する領域）。

### 過剰開示を避ける
- 全ての小修正を記録する必要はない
- 主要なワークフローでの使用範囲を概括的に示せば十分
- 細かな履歴は別途 `MEMORY.md` の `feedback_ai_authorship_process.md` で管理

### 過小開示も避ける
- 「使っていない」と書かない（事実と異なる）
- 「ChatGPT を一度使っただけ」と矮小化しない（実際の使用範囲に応じて記述）

### バージョン情報の記録
- AI ツールのバージョン（例：Claude Opus 4.7、GPT-5.5）は **内部記録**（判断ログ、MEMORY.md）に残す
- 論文本文には具体的バージョン名を記載しない（投稿時点で旧バージョン化していると不自然になるため）
- ジャーナルが具体名を要求する場合のみ、その指示に従う

### 引用の精読範囲（実態に即した表現）
- 「すべての引用を精読」と書くことは、実態と一致する場合のみ
- 一般的には「直接的に主張を支える引用は精読」「文脈引用は確認のみ」を区別する
- テンプレート B の英語版は「Full-text review was conducted for references whose claims directly inform the methods, results, or conclusions」という段階表現を採用

### 査読者への対応準備
- 「AI を使ったが結論は自分が出した」ことを示す材料を準備
- 例：判断ログ（`claude1/AIノート/AI協働_個人原則.md` の判断ログ）、独立検証の記録

---

## 5. 関連ドキュメント

- 研究方針本体：`paper_plan.md`
- AI 時代版研究ロードマップ：`ai_era_research_roadmap.md`
- 個人 AI 原則（claude1/AIノート/）：`AI協働_個人原則.md`
- AI 使用方針（自動メモリ）：`feedback_ai_authorship_process.md`
- 参考文献の完全精読ルール（自動メモリ）：`feedback_reference_verification.md`
- 情報源の明示ルール（自動メモリ）：`feedback_information_source_disclosure.md`

---

## 6. 適用ステータス

| 文書 | 開示文の適用 | 状態 |
|---|---|---|
| Paper 1（v7.0） | 未適用 | 投稿前に詳細版または短縮版を追加 |
| Paper 2（v7.0） | 未適用 | 投稿前に短縮版を追加 |
| Paper 3（v5.0） | 未適用 | 投稿前に詳細版を追加 |
| 修論（未着手） | — | 修論執筆時に詳細版を含める |
| 研究計画書（草稿段階） | 未適用 | 浅井先生提出前に短縮版を含める |

このテンプレートは草稿であり、実際の論文投稿時にはジャーナル固有の AI 使用ポリシーを確認してから採用してください。
