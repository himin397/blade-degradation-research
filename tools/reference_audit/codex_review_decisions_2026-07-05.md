# Codex 独立レビュー記録：判断6件適用（Paper 1 v9.7 / Paper 2 v10.2 / Paper 3 v5.7）

- **日付**: 2026-07-05
- **レビュアー**: Codex CLI 0.142.5（gpt-5.5）、読み取り専用（ファイル変更なし・スクリプト実行なし）
- **依頼主体**: Claude Code（CLAUDE.md 自主実行条件1「データ解釈を変える変更」＝mAP 主指標の val→test 切替＋新規評価数値の転記、に該当と判断して自主実行）
- **レビュー対象**: コミット e25f6fa 以後の未コミット変更（判断待ち6件の適用一式）＋新規ファイル（eval_test_per_class.py、table_class_ap_exp001/exp002 CSV）
- **反映先**: Paper 1 **v9.8**・Paper 2 **v10.3**（全指摘採用）
- **原文ログ**: /tmp/codex_decisions_review.md（揮発）→ 要点は本記録が恒久版

## 問題なし確認（コア検証）

1. Paper 1 の test 主指標化に、意図的な val 併記箇所以外の消し忘れなし
2. EXP-001/EXP-002 の AP・mAP 転記は CSV と一致
3. `eval_test_per_class.py` の評価条件は `week1_analysis.py::task2_class_ap()` と一致（dataset.yaml / split=test / imgsz=640 / conf=0.25 / iou=0.5）
4. Paper 3 本文の mAP 3箇所は test 0.56 へ修正済み
5. Paper 3 §7.3 の可視化レイヤー追記は限定つきで主張過大でない

## 指摘5件と採否（全件採用）

| # | 重大度 | 内容 | 対応（Claude Code） |
|---|---|---|---|
| 1 | 中 | Table 1 の P/R（0.424/0.285、0.691/0.425）が成果物 CSV から独立検証できない | eval_test_per_class.py に P/R 列を追加（クラス別 = results.box.p/r、全体 = mp/mr）し両 CSV を再生成。**再生成後の mp/mr が本文 Table 1 と一致することを確認**（exp001: 0.4236/0.2848、exp002: 0.6911/0.4247）。AP 値は再実行でも不変（決定論性再確認） |
| 2 | 中 | Paper 2 §4.4 で単一ケース 6.5% の直後に使用可能判断があり B-3（統計版主体）と衝突 | 6.5% を「代表条件での補助確認」に位置づけ直し、使用可能性の判断文を Table 8b の後へ移して「全40条件平均 −4.6% に基づく」に変更（v10.3） |
| 3 | 低 | 「これらのアルゴリズム」の指示対象が曖昧 | 指示語を排し「ASTM E1049-85 はRainflow計数を含むサイクル計数法を業界標準として整理した規格」に書き換え（Codex 案の「Algorithm I/II を含む」は E1049 の実態に対して過剰特定のため、Claude Code 判断で表現を調整） |
| 4 | 低 | LE;CR の「confirmed ... root cause」は介入実験なしには強い（Proposal Policy） | §5.2・Conclusion 2 を「most supported explanation（代替仮説3件は消去済み、介入による確認は future work）」に較正（v9.8） |
| 5 | 低 | Abstract の「6 of 8」に自明性の言及なし | Abstract・1文主張・貢献に「実質は部位重み個別6中4（クラス重み一括2件は自明保存）」を併記（v9.8） |

## Claude Code の採否判断メモ

- 指摘1は「数値の正しさ」ではなく「検証可能性（provenance）」の指摘。数値自体はコンソール出力から転記済みで正しかったが、成果物からの独立突合を可能にする改善として採用
- 指摘3のみ Codex 提案文をそのまま使わず表現を調整（理由は表内に記載）。他4件は提案趣旨どおり適用
- 指摘4は CLAUDE.md Proposal Policy（観察/仮説/確定の区別)との整合そのもので、Codex が方針文書を正しく参照した指摘
