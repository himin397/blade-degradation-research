#!/usr/bin/env python3
"""Stopフック：応答テキストの一人称「私」を検出して書き直しを促す。

CLAUDE.md Communication Style（一人称は「Claude Code」必須・例外なし）の工程化。
2026-08-11 の違反（長セッション後半で「私」に逸脱）を受けて導入。
誇張語チェックは 2026-08-05 Codex レビューで誤検知過多として見送り済みのため含めない。

動作:
- 最後のアシスタント応答テキストから 私[はがもをにのと] パターンを検出
- 検出時は decision:block で理由を返す → Claude Code が書き直してから終了する
- stop_hook_active（差し戻し後の再終了）では再ブロックしない＝無限ループ防止。
  引用文中の「私」等の誤検知は、書き直し判断の段階で Claude Code が無視できる
"""
import json
import re
import sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

if data.get("stop_hook_active"):  # 差し戻し済み＝2周目は素通し（ループ防止）
    sys.exit(0)

# 公式仕様の last_assistant_message を第一候補にする（Codexレビュー2026-08-11・高）。
# transcript 走査はフォールバック（長セッションでの全走査タイムアウト対策も兼ねる）
last_text = data.get("last_assistant_message") or ""
if not last_text:
    path = data.get("transcript_path")
    if not path:
        sys.exit(0)
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("type") != "assistant":
                    continue
                msg = rec.get("message") or {}
                parts = [c.get("text", "") for c in (msg.get("content") or [])
                         if isinstance(c, dict) and c.get("type") == "text"]
                if parts:
                    last_text = "\n".join(parts)
    except OSError:
        sys.exit(0)

# 「私です/私だ/私、/文末の私」も検出しつつ「私有・公私」等の複合語は除外（Codexレビュー・中）。
# 直前が漢字なら複合語（公私・滅私等）とみなして除外する
hits = re.findall(r"(?<![一-龥])(私たち|私(?=$|[はがのもをにとでだなか、。．，.,!?！？\s]))",
                  last_text)
if hits:
    reason = (f"CLAUDE.md違反の可能性：応答に一人称「私」を検出（{len(hits)}件・例: "
              f"{'、'.join(hits[:3])}）。一人称は「Claude Code」必須（例外なし）。"
              "応答を書き直してから終了してください。引用文・曲名等の誤検知であれば"
              "そのまま再終了して構いません。")
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
sys.exit(0)
