# Codex レビュー一次記録 01（無加工）: CLAUDE.md・.claude/ 新設 2026-09-04

- 実行: codex exec --sandbox read-only（codex-cli 0.145.0）、-C はスクラッチパッド複製（リポジトリ本体は渡していない）
- 投入物: CLAUDE.md・AGENTS.md・.claude/（settings・hooks・agents・frp-check・codex-fleet・investigate）・AIノート/判断ログ.md（いずれも区分D。japanese-tech-writing・docs/・tools/ は除外）

## 依頼文

あなたは独立レビュアーです。ファイルは変更せず、指摘のみ返してください。

## 目的
風車ブレード劣化予測研究（個人研究・論文3本・卒論）用の Claude Code プロジェクト設定を新設した。素材は利用者の個人用プロジェクトの CLAUDE.md・工程（エージェント・フック・スキル）で、方針は「検証・批判的視点（Neutrality・FRP・Codex 独立レビュー・実物精査）はそのまま持ち込み、私的情報（資産・性格・心理・キャリア戦略・勤務先の内部情報）だけを除外する」。変更主体：Claude Code。

## ファイル（このディレクトリ配下のみ読むこと）
- CLAUDE.md：本体（新設）
- AGENTS.md：既存の Codex 向け指示書（冒頭に CLAUDE.md へのポインタを1行追記しただけ）。CLAUDE.md と矛盾がないかの比較対象
- .claude/settings.json：権限（前置き形 allow・フック登録）
- .claude/hooks/*：SessionStart フック・一人称チェック
- .claude/agents/*.md：collector / deep-collector / pdf-reader
- .claude/skills/frp-check, codex-fleet
- .claude/commands/investigate.md
- AIノート/判断ログ.md（雛形＋移管1件）

## 実行済み確認
- settings.json の JSON 構文チェック通過。~/.claude.json に trust 承認を設定済み
- メモリ側（別ディレクトリ・投入していない）は、私的情報キーワードの grep で残留ゼロを確認済み

## 見てほしい観点（重大／推奨／任意の3段階で、根拠のファイル・行を付けて）
1. **情報分離**：CLAUDE.md・エージェント・スキルに、資産・性格・心理・キャリア戦略・勤務先の内部情報（社名・社内プロジェクト・データの出所）を推測させる記述が残っていないか。逆に、研究に必要な情報（データソース・研究動機・卒論接続）を削りすぎていないか
2. **AGENTS.md との整合**：Role・Proposal Policy・参考文献ルール・情報源の明示で、CLAUDE.md と AGENTS.md の間に食い違い・表現差があれば列挙（Codex と Claude Code が別の規範で動くことを防ぐ）
3. **守秘区分**：研究特有の境界（勤務先由来 SCADA・点検記録、公開データセット、有料論文、非公開現場メモ）が A〜D で漏れなく分類できるか。「公開データ軸で完結」と「勤務先データは保険」の関係が読み手に伝わるか
4. **Neutrality と研究補助者の役割の両立**：反論先出しと「主張の強さを勝手に上げない」「判断は himinさん」が矛盾なく読めるか。反論先出しが論文執筆の実務（文章化作業）を止める副作用がないか
5. **FRP・参考文献ルールの実効性**：宣言ルール止まりの箇所（例：完全精読ルール・情報源明示）に対し、既存の `tools/reference_audit/`・フック・スキルで機械的に担保される部分と、されない部分を分けて指摘。工程化の案があれば
6. **設定・フック・スキルの参照パス**（$CLAUDE_PROJECT_DIR 等）の誤り、git 関連の allow（add/commit 許可・push はフック）の妥当性
7. **用語の残留**：勤務先用（設備・点検）や広告事業用の表現が研究向けに不適合なまま残っていないか

## Codex 返答（無加工）

himinさん、指摘のみ返します。ファイル変更はしていません。

**重大**
- [`.claude/settings.json:47`] Codex 連携の allow が `codex --version` だけです。  
  1. `.claude/skills/codex-fleet/SKILL.md:60` と `CLAUDE.md:123` は `codex exec --sandbox read-only ...` の自主実行を前提にしていますが、settings 上は自動実行できません。  
  2. 優先度：重大  
  3. `Bash(codex exec:*)` を許可するか、Codex 実行を承認対象にする方針へ CLAUDE.md 側を寄せる必要があります。

- [`CLAUDE.md:78`] `tools/reference_audit/` が実体として存在しません。  
  1. CLAUDE.md は引用の精読・照合結果を `tools/reference_audit/` に残すとしていますが、この提出ディレクトリ内では `tools/reference_audit/` がありません。FRP・完全精読ルールの機械的担保が「宣言」に寄っています。  
  2. 優先度：重大  
  3. 監査ツールを同梱するか、現時点では「未実装。代替は判断ログ／読解ノート」と明示するとよいです。

- [`CLAUDE.md:108`] サブエージェントの守秘ゲートが pdf-reader 以外に実装されていません。  
  1. `pdf-reader` は未記載・A・未確認Cを開かない規定があります（`.claude/agents/pdf-reader.md:14`）が、`collector` と `deep-collector` には同等の入力必須チェックがありません（`.claude/agents/collector.md:4`, `.claude/agents/deep-collector.md:4`）。親の委譲文ミスで A/C を読ませる余地があります。  
  2. 優先度：重大  
  3. collector / deep-collector にも「守秘区分必須、未記載・A・未確認CはRead/Grep/Glob/Bash/Web送信前に差し戻す」を入れるべきです。

**推奨**
- [`CLAUDE.md:4`] 正とする `docs/paper_plan.md` が提出物内にありません。  
  1. AGENTS.md も同じ参照です（`AGENTS.md:3`, `AGENTS.md:119`）。この状態では、研究動機・データソース・卒論接続を削りすぎていないか検証できません。  
  2. 優先度：推奨  
  3. レビュー対象に `docs/paper_plan.md`、`docs/data_sources.md`、`docs/external_datasets_inventory.md` を含めるか、CLAUDE.md に最低限の要約を置くとよいです。

- [`AGENTS.md:3`] 「Role・Proposal・Neutrality・参考文献ルールは共通」とありますが、実際は差分があります。  
  1. CLAUDE.md には相関用途・効果量ルール（`CLAUDE.md:46-47`）、FRP（`CLAUDE.md:56-71`）、監査記録（`CLAUDE.md:78`）がありますが、AGENTS.md にはありません。Codex と Claude Code が異なる厳しさでレビューする可能性があります。  
  2. 優先度：推奨  
  3. AGENTS.md に「CLAUDE.md の当該節を準用」と明示するか、共通節を同期してください。

- [`CLAUDE.md:32`] 有料論文・会員限定資料の扱いがやや混ざっています。  
  1. C区分では「利用条件に制限のある有料論文・会員限定資料」としつつ、`CLAUDE.md:77` と `AGENTS.md:81` では libproxy 経由でアクセス可能と書いています。アクセス可能性と、AI投入・保存・要約の可否は別問題です。  
  2. 優先度：推奨  
  3. 「読むだけ可」「AI投入可」「本文保存可」「引用要約可」を分けると安全です。

- [`CLAUDE.md:35`] 「公開データ軸で完結、勤務先データは保険」の関係が明文化されていません。  
  1. D区分の公開データセット（`CLAUDE.md:33`）と実データは himinさん側接続（`CLAUDE.md:35`）から推測できますが、研究計画の主軸が公開データで完結するとは読み切れません。  
  2. 優先度：推奨  
  3. 「原則Dのみで論文を成立させ、勤務先由来データは許可・匿名化・必要性が揃う場合の補助検証に限る」と一文追加すると境界が明確です。

- [`CLAUDE.md:50`] 反論先出しが全タスクにかかるように読めます。  
  1. 文章化作業（`CLAUDE.md:19`, `CLAUDE.md:94`）でも毎回反論から入ると、単純な整文・図表作成の進行を止める副作用があります。  
  2. 優先度：推奨  
  3. 「判断・解釈・主張強度に関わる場合」と条件を付け、純粋な整形・転記では簡潔に実行する、と分けるとよいです。

- [`AGENTS.md:91-95`] 研究動機の3層構造に、個人背景を推測させる語が残っています。  
  1. 「作業員の安全とメンタル」「現場経験＋発注者視点」は研究動機として有用ですが、職務経験・心理領域・発注者側の立場を推測させます。社名や内部情報ではないため重大ではありません。  
  2. 優先度：推奨  
  3. 「保守作業の安全性」「実務上の意思決定に接続できる点」程度に抽象化すると、研究価値を残して私的推測を減らせます。

- [`CLAUDE.md:149`] `/japanese-tech-writing` が索引にありますが、提出物内にスキル実体がありません。  
  1. `.claude/skills/` には `frp-check` と `codex-fleet` だけです。参照切れだと、論文・技術文書の文章規範が工程化されません。  
  2. 優先度：推奨  
  3. スキルを同梱するか、索引から外すべきです。

**任意**
- [`.claude/settings.json:48`] `Read(//private/tmp/claude-501/**)` は temp パス固定かつ二重スラッシュです。  
  1. 実プロジェクトへ移した時に読み取り許可が効かない可能性があります。  
  2. 優先度：任意  
  3. 実配置の `/Users/tsunekousei/Desktop/blade-degradation-research/**` に合わせて確認するとよいです。

- [`.claude/hooks/check-first-person.py:52`] 一人称フックは「私」検出だけです。  
  1. CLAUDE.md は「Claude Code」を必ず使う、です・ます調、誇張禁止、指示詞「あの」禁止まで求めています（`CLAUDE.md:9-16`）が、機械検出は一部だけです。  
  2. 優先度：任意  
  3. 重要なのは一人称なので現状でも妥当ですが、他ルールは未機械化と割り切って明示するとよいです。

- [`AIノート/判断ログ.md:31`] 移管1件の根拠粒度が本文精読ルールと完全には揃っていません。  
  1. 「レビュー2本精読」とありますが、文献名・DOI・精読範囲・保存ノートへの参照がありません。判断ログとしては有用ですが、後日の再監査にはやや弱いです。  
  2. 優先度：任意  
  3. 参照先ノート、検索日、実物確認ステータスを足すとFRP運用に接続しやすいです。