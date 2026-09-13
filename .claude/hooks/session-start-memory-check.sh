#!/bin/bash
# SessionStart フック：CLAUDE.md「セッション開始時の確認ルール」の工程化
# stdout はセッション冒頭のコンテキストに注入される
# プロジェクトのメモリパスは CLAUDE_PROJECT_DIR から導出する（Claude Code は "/" を "-" に置換した名前で projects/ 配下に置く）
PROJ="${CLAUDE_PROJECT_DIR:-$(pwd)}"
MEM="$HOME/.claude/projects/$(printf '%s' "$PROJ" | tr '/' '-')/memory/MEMORY.md"
if [ -f "$MEM" ]; then
  mtime=$(stat -f "%Sm" -t "%Y-%m-%d" "$MEM" 2>/dev/null)
  now=$(date +%s)
  mts=$(stat -f "%m" "$MEM" 2>/dev/null)
  days=$(( (now - mts) / 86400 ))
  echo "[SessionStartフック] ブレード劣化予測研究フォルダのセッション開始確認（CLAUDE.md）："
  echo "- MEMORY.md を実態と照合し、ズレがあれば更新する（最終更新: ${mtime}・${days}日前）"
  echo "- 研究方針の正は docs/paper_plan.md。論文の版・監査進捗はメモリの「論文監査進捗」が正"
  echo "- 論文・規格を根拠にする時は実物PDFを精読してから（アブストラクト・検索サマリーで断定しない）"
  echo "- 主張の強さは Proposal Policy の段階を超えない。himinさんが「仮説」と書いた箇所を強めない"
  echo "- 勤務先由来のデータ・点検記録は守秘区分を確認してから読む（公開データセットは D）"
else
  echo "[SessionStartフック] 警告: MEMORY.md が見つかりません（${MEM}）。パスの変更・移動がないか確認してください。"
fi
# 改善提案箱（追記専用。親 claude1 が /sync-rules で回収し、処理状態は親の台帳が持つ）
INBOX="$PROJ/docs/改善提案.md"
LEDGER="/Users/tsunekousei/Desktop/claude1/AIノート/共有知見台帳.md"
if [ -f "$INBOX" ]; then
  n=0
  while IFS= read -r id; do
    [ -z "$id" ] && continue
    grep -qF "$id" "$LEDGER" 2>/dev/null || n=$((n + 1))
  done < <(grep -oE '^## ID: [a-z0-9-]+-[0-9]{8}-[0-9]{3}' "$INBOX" 2>/dev/null | sed 's/^## ID: //')
  echo "- 運用の改善点・失敗事例に気づいたら docs/改善提案.md に /propose で追記（守秘区分Dの汎用知見のみ）。親の回収待ち: ${n} 件"
fi
exit 0
