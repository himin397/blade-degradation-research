#!/usr/bin/env python3
"""Stopフック：証拠の量を書かずに強い結論語を使った応答を検出し、書き直しを促す（注意喚起）。

CLAUDE.md「Proposal Policy」の「証拠の量と結論語」（2026-09-23 追加）の工程化。
背景：1〜2問の正解で「習得」、同日の少数サンプルで「確定」「解消」、数件の試験で「動作確認済み」と
書く癖が学習・音楽分析・ツール検証に共通して出ていた（himinさん指摘 2026-09-23）。

位置づけ（Codex レビュー 2026-09-23 で明記）：
- これは**限定的な注意喚起**。通過＝ルール適合の証拠ではない。基準充足の判定は /frp-check と本人が行う
- 一度だけ書き直しを促す。stop_hook_active（Stop フックで継続中）なら素通し＝ループ防止。
  引用文・ルール文の誤検知なら、そのまま再終了して通る。他フックの差し戻し後の応答も再検査しない（仕様上の限界）

動作:
- 最後の応答（last_assistant_message）を「単位」に分ける：表の行＝1単位、箇条書き項目＝1単位、本文＝段落
  コードブロック（``` と ~~~）と引用行（> ）は対象外
- 単位内で結論語を探す：確定／解消／習得／動作確認済／再現（した・済・級・を確認・できた）
  否定・未完了（未確定・していない・できない・するには 等）と複合語（確定申告・確定額・再現手順 等）は除外
- 結論語と同じ**文**（。区切り）の証拠の量を見る：n=、k/N（日付は除外）、N件・問・曲・回・例…（第N回は除外）、
  別日・別条件・別データ・事前登録（直後に「未」「せず」「していない」が続くものは無効）
  文に無ければ単位全体で見る
- 違反候補：①証拠の量が無い ②量の最大が2以下で修飾語も無く、強い語（確定・習得・解消・動作確認済）
  ③「習得」で件数が無い・最大が10未満・k/N<0.9
- 例外：不具合・バグ・エラーの「再現」は存在の確認なので1件でよい（強い語の検査を免除）
- 数字は6桁まで・応答は末尾6万字まで（性能上限）。型が想定外なら「検査不能」として通す（stderr に理由）
"""
import json
import re
import sys

MAX_CHARS = 60000

# 2026-10-01 改訂（四半期棚卸し・Codex レビュー反映）：差し戻し19回中17回が誤検知だったため、
#  ①段取りと分かる形（確定させる〔非過去〕・確定するまで・確定したら・確定次第 等）と否定（にしません・とは言えない 等）、
#    用語（確定結論）を外す。過去形の「確定させた」、「確定すると判断」、「確定した」「確定です」「確定できる」は検出する
#  ②かぎ括弧の中（ルール文・取説の引用）は外す。ただし括弧の中が結論語だけで、直後が「です」「だ」「。」「と判断」等なら検出する（強調）
#  ③語の並び（確認・確定・習得／確定／回答待ち／判断）は、並びに結論語でない語がある時だけ外す（読点は区切りにしない）
#  ④単位の中の文ごとに、外さなかった結論語だけで判定する
_PROCESS = (r"させる|させれ|させよ|させて(?!い)|するまで|するには|する前|するため|するなら|するべき|する予定|する必要|すること"
            r"|したら|すれば|次第|しません|にしない|にしません|とは言えない|とは言えません|とはいえない|ではない")
CONCLUSION = re.compile(
    r"(?<![未不])確定(?!申告|拠出|日|期限|値|額|的観察|版|結論|" + _PROCESS + r"|していない|していません|できない|できず|せず|しない|には)"
    r"|(?<![未不])解消(?!法|" + _PROCESS + r"|していない|していません|できない|できず|せず|しない|には)"
    r"|(?<![未不])習得(?!目標|候補|" + _PROCESS + r"|していない|していません|できない|できず|せず|しない|には|に向け)"
    r"|動作確認済"
    r"|再現(?=した|済|級|を確認|できた|と確認)"
)
QUOTE = re.compile(r"「[^「」\n]*」|『[^『』\n]*』|“[^“”\n]*”|\"[^\"\n]*\"")
EMPHASIS_AFTER = re.compile(r"\s*(です|でした|だ|である|。|$|と判断|と言え|と記録)")
ENUM_SEP = re.compile(r"[・／/]")
ENUM_STOP = set("。、，,\n（）()「」『』“”\"：:＝= 　|")
ENUM_REACH = 40   # 並びを探す範囲（前後の文字数）。長い連続文字で処理が重くならないよう上限を置く
STRONG = re.compile(r"確定|習得|解消|動作確認済")
BUG_EXISTENCE = re.compile(r"(バグ|不具合|エラー|欠陥|異常).{0,20}再現|再現.{0,20}(バグ|不具合|エラー|欠陥|異常)")
NUM = r"(?<![\d第])\d{1,6}(?!\d)"
EVIDENCE = re.compile(
    rf"n\s*[=＝]\s*(?P<n>{NUM})"
    rf"|(?P<k>{NUM})\s*[/／]\s*(?P<d>{NUM})(?!\s*(日|に|まで|〜|～|-|時))"
    rf"|(?P<c>{NUM})\s*(件|問|曲|回|例|セッション|試行|標本|サンプル|ケース)"
    r"|(?P<q>別日|別条件|別データ|事前登録)(?!\s*(は|も|を)?\s*(未|なし|無し|せず|していない|していません|しない|不要))"
)
FENCE = re.compile(r"^\s*(```|~~~)")


def units(text):
    """表の行・箇条書き項目は1行1単位、本文は段落（空行区切り）。コードと引用は除外。"""
    out, buf, fence = [], [], None
    for line in text.splitlines():
        m = FENCE.match(line)
        if m:
            if fence is None:
                fence = m.group(1)
            elif m.group(1) == fence:
                fence = None
            continue
        if fence is not None:
            continue
        s = line.strip()
        if s.startswith(">"):
            continue
        if s == "":
            if buf:
                out.append("\n".join(buf))
                buf = []
            continue
        if s.startswith("|") or re.match(r"^([-*+]|\d+[.)])\s", s):
            if buf:
                out.append("\n".join(buf))
                buf = []
            out.append(s)
        else:
            buf.append(line)
    if buf:
        out.append("\n".join(buf))
    return out


def evidence(text):
    nums, ratios, qual = [], [], False
    for e in EVIDENCE.finditer(text):
        if e.group("q"):
            qual = True
        elif e.group("n"):
            nums.append(int(e.group("n")))
        elif e.group("k"):
            k, d = int(e.group("k")), int(e.group("d"))
            if d > 0:
                nums.append(d)
                ratios.append((k, d))
        elif e.group("c"):
            nums.append(int(e.group("c")))
    return nums, ratios, qual


def quote_spans(unit):
    return [(q.start(), q.end()) for q in QUOTE.finditer(unit)]


def in_quote(spans, s, e):
    """spans は開始位置の昇順。s を含む引用を二分探索で探す。"""
    lo, hi = 0, len(spans)
    while lo < hi:
        mid = (lo + hi) // 2
        if spans[mid][0] < s:
            lo = mid + 1
        else:
            hi = mid
    k = lo - 1
    if k >= 0 and spans[k][0] < s and e <= spans[k][1]:
        return spans[k]
    return None


def enumerated(unit, m):
    """m が「語の並び」の1要素で、並びに結論語でない語があるか（確認・確定・習得／確定／回答待ち／判断）。"""
    s, e = m.start(), m.end()
    lo = s
    while lo > 0 and s - lo < ENUM_REACH and unit[lo - 1] not in ENUM_STOP:
        lo -= 1
    hi = e
    while hi < len(unit) and hi - e < ENUM_REACH and unit[hi] not in ENUM_STOP:
        hi += 1
    run = unit[lo:hi]
    parts, pos, mine = [], lo, None
    for tok in ENUM_SEP.split(run):
        if pos <= s < pos + len(tok):
            mine = len(parts)
        parts.append(tok)
        pos += len(tok) + 1
    if len(parts) < 2 or mine is None or parts[mine].strip() != m.group(0):
        return False
    return any(tok.strip() and not CONCLUSION.search(tok) for k, tok in enumerate(parts) if k != mine)


def excluded(unit, m, spans):
    """結論語の出現を検査から外すか。"""
    q = in_quote(spans, m.start(), m.end())
    if q is not None:
        inner = unit[q[0] + 1:q[1] - 1].strip()
        if inner == m.group(0) and EMPHASIS_AFTER.match(unit[q[1]:q[1] + 6]):
            return False   # 「習得」です＝強調。検査する
        return True        # ルール文・取説などの引用
    return enumerated(unit, m)


def find_violations(text):
    hits = []
    for unit in units(text[-MAX_CHARS:]):
        spans = quote_spans(unit)
        valid = [x for x in CONCLUSION.finditer(unit) if not excluded(unit, x, spans)]
        if not valid:
            continue
        snippet = unit.replace("\n", " ")
        pos = 0
        for sent in re.split(r"(?<=[。\n])", unit):
            in_sent = [x for x in valid if pos <= x.start() < pos + len(sent)]
            pos += len(sent)
            if not in_sent:
                continue
            words = [x.group(0) for x in in_sent]
            m = in_sent[0]
            nums, ratios, qual = evidence(sent)
            if not nums and not qual:
                nums, ratios, qual = evidence(unit)
            i = max(0, m.start() - 25)
            show = snippet[i:m.end() + 15].strip()
            strong = any(STRONG.search(w) for w in words) and not BUG_EXISTENCE.search(sent)
            if not nums and not qual:
                hits.append("量なし: " + show)
            elif strong and not qual and nums and max(nums) <= 2:
                hits.append("単発で強い語: " + show)
            elif any("習得" in w for w in words):
                if not nums:
                    hits.append("習得に件数なし: " + show)
                elif max(nums) < 10:
                    hits.append(f"習得の基準未満（最大 {max(nums)} 件・10 未満）: " + show)
                elif ratios:
                    k, d = max(ratios, key=lambda r: r[1])
                    if k / d < 0.9:
                        hits.append(f"習得の基準未満（{k}/{d}）: " + show)
    return hits


def load_text(data):
    """検査対象の応答文字列。特定できなければ None（検査不能）。"""
    if "last_assistant_message" in data:
        v = data.get("last_assistant_message")
        return v if isinstance(v, str) else None
    path = data.get("transcript_path")
    if not isinstance(path, str):
        return None
    last = None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(rec, dict) or rec.get("type") != "assistant":
                    continue
                msg = rec.get("message")
                if not isinstance(msg, dict) or not isinstance(msg.get("content"), list):
                    continue
                parts = [c.get("text") for c in msg["content"]
                         if isinstance(c, dict) and c.get("type") == "text" and isinstance(c.get("text"), str)]
                if parts:
                    last = "\n".join(parts)
    except (OSError, UnicodeError):
        return None
    return last


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    if not isinstance(data, dict) or data.get("stop_hook_active"):
        return
    text = load_text(data)
    if text is None:
        print("check-evidence-claims: 検査対象を特定できないため通過", file=sys.stderr)
        return
    hits = find_violations(text)
    if hits:
        reason = (
            "Proposal Policy「証拠の量と結論語」違反の可能性（注意喚起・通過は適合の証拠ではない）："
            f"証拠の量（n・k/N・日付・条件）を同じ文に書かずに強い結論語を使っています（{len(hits)}件・例: "
            + " ／ ".join(hits[:3]) + "）。全称命題は1件の反例で崩れ、存在は1件で確認できるが、"
            "習得・成功率・一般化は1件では書けない。証拠の量を添えるか、語を「観察」「傾向」に落として"
            "書き直してから終了してください。引用文・ルール文中の語の誤検知であればそのまま再終了して構いません。"
        )
        print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # 実装不具合で応答を止めない。診断は stderr へ
        print(f"check-evidence-claims: 内部エラーのため通過: {e!r}", file=sys.stderr)
    sys.exit(0)
