# Codex 独立レビュー記録: Paper 2 v10.0（レコード別補間移行）

**実施日**: 2026-07-03
**レビュアー**: OpenAI Codex CLI 0.142.5（gpt-5.5、read-only sandbox、reasoning effort: high）
**依頼者**: Claude Code（CLAUDE.md 自主実行トリガー1「データ解釈を変える変更」該当）
**対象**: Paper 2 v10.0 の全変更（docs/paper2_fatigue_load_estimation.md、penmanshiel_del_perrecord.py、v2 CSV 4本）
**採否と反映**: 全5指摘（高2・中2・低1）を採用し Paper 2 v10.1 で反映（詳細は Paper 2 改訂履歴 v10.1 と監査記録 A-10）。
**Claude Code による指摘の独立検証**: クリップ率 19.2% 再計算一致 / V-TI 相関 r=+0.11 実測（v10.0 の負相関仮説は不成立と判明し訂正）/ m=10 べき平均 +84.5% 定量化（T01 2020）。
**追補**: Codex サンドボックスでブロックされた実行検証は Claude Code が代替実施（再実行で 4 CSV MD5 完全一致・paper2_figures.py 実行成功）。

---

## Codex 最終所見（原文）

himinさん、読み取り専用で確認しました。ファイル変更はしていません。

**レビュー結果**

- [[phase3_scada/penmanshiel_del_perrecord.py:101](/Users/tsunekousei/Desktop/blade-degradation-research/phase3_scada/penmanshiel_del_perrecord.py:101)] 月次DELを算術平均している点は、DELという語の標準的解釈と衝突する可能性があります。
  1. **主張の強さ / 方法定義**: §3.7のD1定義とは一致していますが、疲労損傷等価荷重として月次・年次DELを集約するなら、通常は `mean(DEL^m)^(1/m)` 型の損傷等価平均が候補になります。現在の値は「QC通過10分レコードDELの平均値」と読むのが安全です。
  2. **優先度: 高**
  3. **推奨修正案**: D1を維持するなら、本文で「damage-equivalent monthly DEL」ではなく「mean 10-min DEL proxy」相当の定義であることを明示するのがよいです。真に月次DELと呼ぶなら、m=10のべき平均で感度確認する必要があります。

- [[phase5_openfast_shm/openfast_cases/scripts/paper2_figures.py:45](/Users/tsunekousei/Desktop/blade-degradation-research/phase5_openfast_shm/openfast_cases/scripts/paper2_figures.py:45)] 旧CSVを読む図表再生成スクリプトが残っています。
  1. **副作用 / 再現性**: `paper2_figures.py` は `penmanshiel_monthly_del.csv` と `longitudinal_del_T01.csv` を読みます。これを実行すると、v10.0のFigure 6/7が旧法の値で上書きされる可能性があります。本文の再現性表では同スクリプトを「全Figure再生成」としているため、ここは実害があります。
  2. **優先度: 高**
  3. **推奨修正案**: `paper2_figures.py` をv2 CSV参照に更新するか、本文の再現性表でFigure 6/7は `penmanshiel_del_perrecord.py` が生成すると明記するのがよいです。

- [[docs/paper2_fatigue_load_estimation.md:582](/Users/tsunekousei/Desktop/blade-degradation-research/docs/paper2_fatigue_load_estimation.md:582)] 「風況変動が主因」はやや強いです。
  1. **主張の強さ過剰**: §4.7と§5.3では「V_mean/TI_medと連動」は観察として妥当ですが、「主因」は因果帰属です。風況正規化を未実施と書いているため、Proposal Policy上は「仮説」または「整合的」に留める方が安全です。
  2. **優先度: 中**
  3. **推奨修正案**: Abstract/Conclusionの「風況変動が主因」を「風況変動と整合的」「風況変動で説明可能な仮説が支持される」に弱めるのがよいです。

- [[docs/paper2_fatigue_load_estimation.md:259](/Users/tsunekousei/Desktop/blade-degradation-research/docs/paper2_fatigue_load_estimation.md:259)] クリップ開示はありますが、量的開示が不足しています。
  1. **出典不足 / 方法限界**: 直接確認では、2020年5台で少なくとも一方の軸がクリップされるQC通過レコードは約19.2%、T01縦断では約17.5%でした。これは無視できない比率です。本文の「許容可能」という判断には、クリップ率の概数がある方が査読耐性が上がります。
  2. **優先度: 中**
  3. **推奨修正案**: §3.7またはLimitation 5に「2020年5台ではQC通過レコードの約19%が少なくとも一軸で境界クリップ」と一文追加するのがよいです。

- [[docs/paper2_fatigue_load_estimation.md:469](/Users/tsunekousei/Desktop/blade-degradation-research/docs/paper2_fatigue_load_estimation.md:469)] §4.6.4の原因説明は仮説表示されており大枠は適切ですが、実測補助があるとより堅いです。
  1. **仮説表示は適切**: 「複合効果と考えられる（仮説）」としており、強さは過剰ではありません。ただしV-TI負相関やクリップ寄与は本文内で数値提示されていません。
  2. **優先度: 低**
  3. **推奨修正案**: 可能ならV-TI相関係数、またはクリップ率を括弧で添えると、説明が単なる後付けに見えにくくなります。

**問題なし**

- `penmanshiel_del_perrecord.py` のQC条件は旧 `phase3_penmanshiel.py` と一致していました。`V >= 3.5`, `P >= 0`, `TI 0.005–0.50` の本文記述とも整合しています。
- レコード別補間、境界クリップ、月次groupby、フリート平均、年間平均の実装は、§3.7で明示されたD1〜D3定義とは一致しています。
- Table 12/13/14の主要DEL値はv2 CSVと一致していました。例: Table 13は T01 1,422 / T02 1,431 / T04 1,413 / T05 1,424 / T06 1,393 と一致します。
- 旧法参照列 `DEL_pointinterp_kNm` は旧 `penmanshiel_monthly_del.csv` と完全一致していました。
- §4.6.4の「月次 +1.4〜+14.8%、平均 +6.9%」は、タービン別月次60点で見ると一致します。フリート月次だけなら +2.0〜+12.3% なので、必要なら「タービン別月次値で」と補うと明確です。
