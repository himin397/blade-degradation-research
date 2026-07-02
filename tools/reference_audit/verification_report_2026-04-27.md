# Crossref / DataCite 一括検証レポート

**実施日**: 2026-04-27
**スクリプト**: `tools/reference_audit/crossref_bulk_verify.py`
**対象**: Paper 1 (16本) + Paper 2 (22本) + Paper 3 (25本) のうち DOI が存在する 38 件
**API**: Crossref `https://api.crossref.org/works/{DOI}` ＋ DataCite（Colone PhD thesis のみ）

## 集計

| 結果 | 件数 |
|---|---|
| ✅ OK（manuscript と Crossref/DataCite 完全整合） | 33 |
| ⚠️ 仕様上の差異（実害なし） | 4 |
| 🚨 検証 seed の誤り（manuscript には DOI 未記載のため manuscript 上の問題ではない） | 1 |
| ❌ Crossref に登録なし → DataCite で確認済 | 1（同一行を上記の 1 件と二重計上：実質 38 件中 38 件確定済み） |

## 重要な発見

### 🚨 検証 seed の誤り（Claude Code が誤って想定した DOI）— Herp 2018

- **状況**：原稿 Paper 2 [21] には DOI 未記載。Claude Code が検証スクリプトで「`10.1016/j.renene.2017.09.025`」を seed として置いたが、これは別論文（Rosa et al., UASB 廃水処理プラント論文）を指していた
- **正しい DOI**：`10.1016/j.renene.2017.02.069`（Crossref title-search で確認、著者・タイトル・巻号・ページすべて完全整合）
- **manuscript への影響**：原稿には DOI が記載されていないため、原稿側に修正は不要。ただし**第10バッチ後の最終ドラフト確定時に DOI を追記**すると findability が向上
- **Claude Code の反省点**：「DOI なし参考文献に対して訓練データの記憶から DOI を補完する」のは、過去の Dao 2018 / Robertson 2017 と同種のハルシネーション。今後は「原稿に DOI が無い場合は seed を空欄にし、Crossref title search で取得する」方針に変更

### ⚠️ 仕様上の差異（実害なし）

#### Zhao 2025 (Sci. Rep. 15:18667) — 著者順序の Crossref メタデータ不備

- Crossref は `family=Zhanfang, given=Zhao` と登録（中国姓「Zhao」と名「Zhanfang」が反転）
- 同様に `family=Tuo, given=Li`（Li Tuo の反転）
- これは **Crossref 側のメタデータ問題**で、Sci. Rep. の著者登録時の family/given 反転バグ。原稿 "Zhao Z. & Li T." は正しい
- 「page=18667」は実際には article-number。Crossref では `article-number=18667, page=None` と登録
- **manuscript への影響なし**

#### Zou 2025 (Sci. Rep. 15:5833) — article number vs page

- Crossref では `page=None, article-number=5833`
- Scientific Reports は article number 採用誌で、ページではなく article 番号を使う
- 原稿表記「5833」は article number として整合（編集スタイルに依存）
- **manuscript への影響なし**（必要なら "Article No. 5833" と明記して曖昧さ回避可）

#### Kandemir 2024 (Energy Informatics 7:68) — article number vs page

- 上記と同じパターン。Energy Informatics も article number 採用誌
- Crossref `page=None, article-number=68`
- **manuscript への影響なし**

### ✅ DataCite 経由で確認済み — Colone 2018 PhD thesis

- DOI `10.11581/DTU:00000033` は Crossref に登録なし（404）が、DataCite には登録あり
  - DataCite メタデータ：
    - DOI: 10.11581/dtu:00000033（小文字表記、case-insensitive）
    - Title: "Cost effective strategies"（タイトルは DataCite 上で短縮形だが本体タイトル「Cost-Effective Strategies for Wind Farm O&M: ...」と整合）
    - Creator: Colone, Lorenzo
    - Year: 2018
    - Publisher: Department of Wind Energy, Technical University of Denmark, Risø Campus
    - Type: text
- DTU 等の大学リポジトリの thesis DOI は **DataCite 登録**で Crossref には載らないのが通常運用
- **manuscript への影響なし**（v9.4 修正で採用したのは正しい DOI）

## 完全整合（33件）

| Paper | Ref | DOI | First Author | Year |
|---|---|---|---|---|
| P1 | 1 | 10.3390/en12040676 | Shihavuddin | 2019 |
| P1 | 2 | 10.3390/machines11100953 | Gohar | 2023 |
| P1 | 3 | 10.5194/wes-10-227-2025 | Malik | 2025 |
| P1 | 7 | 10.3390/machines10050327 | Konovalenko | 2022 |
| P1 | 8 | 10.1016/j.solener.2019.02.067 | Deitsch | 2019 |
| P1 | 9 | 10.1111/mice.12263 | Cha | 2017 |
| P1 | 10 | 10.1109/ACCESS.2024.3371493 | Memari | 2024 |
| P1 | 11 | 10.1109/ACCESS.2025.3569799 | Masita | 2025 |
| P1 | 13 | 10.3390/app16031333 | Shi | 2026 |
| P1 | 14 | 10.3390/app14198763 | Zou | 2024 |
| P1 | 16 | 10.1109/ICIP46576.2022.9897990 | Akyon | 2022 |
| P2 | 4 | 10.1049/iet-rpg.2016.0248 | Tautz-Weinert | 2017 |
| P2 | 8 | 10.5194/wes-10-227-2025 | Malik | 2025 (P1-3 と同一) |
| P2 | 9 | 10.5194/wes-7-53-2022 | Abbas | 2022 |
| P2 | 12 | 10.1002/we.1797 | Dimitrov | 2015 |
| P2 | 16 | 10.1016/j.egypro.2017.10.333 | Robertson | 2017 |
| P2 | 18 | 10.2172/578635 | Mandell | 1997 |
| P2 | 20 | 10.1016/j.renene.2017.01.065 | Vera-Tudela | 2017 |
| P3 | 9 | 10.1177/0309524X221124031 | Pandit | 2023 |
| P3 | 10 | 10.3390/en7042595 | Tchakoua | 2014 |
| P3 | 12 | 10.1016/j.renene.2020.07.145 | García Márquez | 2020 |
| P3 | 13 | 10.1016/j.renene.2018.10.047 | Stetco | 2019 |
| P3 | 14 | 10.1016/j.renene.2017.06.089 | Dao | 2018 |
| P3 | 15 | 10.1016/j.engappai.2024.109970 | Gohar | 2025 |
| P3 | 16 | 10.1016/j.aei.2023.102292 | Liu | 2024 |
| P3 | 17 | 10.1016/j.renene.2012.11.030 | Yang | 2013 |
| P3 | 18 | 10.1016/j.egyr.2024.06.041 | Castellani | 2024 |
| P3 | 19 | 10.3390/en13123132 | Maldonado-Correa | 2020 |
| P3 | 21 | 10.1088/1742-6596/1618/2/022030 | Branlard | 2020 |
| P3 | 22 | 10.1016/j.renene.2024.122332 | Hu | 2025 |
| P3 | 23 | 10.1016/j.ress.2010.07.007 | Nielsen | 2011 |
| P3 | 24 | 10.1016/j.egypro.2017.10.349 | Florian | 2017 |
| P3 | 25 | 10.1016/j.ress.2020.107062 | Yeter | 2020 |

## 結論

- **manuscript 内の DOI 記載で重大ハルシネーション 0 件**（過去の Dao 2018 / Robertson 2017 のような「DOI だけ別論文」型は本検証では見つからなかった）
- 実体的差異は すべて article-number-vs-page の表記差 か Crossref メタデータの著者順序バグ
- Colone 2018 PhD thesis は DataCite で確認済み（v9.4 修正の DOI 登録は妥当）
- Claude Code 自身の検証スクリプト seed には Herp 2018 の DOI ハルシネーションがあった → 過去パターンを踏襲してしまった反省点。**「manuscript に DOI 未記載の場合は seed を空欄→ title search で取得」を今後の standard procedure とする**

## 推奨対応

| 対象 | アクション | 優先度 |
|---|---|---|
| Paper 2 [21] Herp 2018 | DOI `10.1016/j.renene.2017.02.069` を最終ドラフト時に追記（findability 向上） | 中 |
| Paper 1 [12] Zhao 2025 / Paper 1 [15] Zou 2025 / Paper 3 [20] Kandemir 2024 | "Article No." 表記の統一を検討（ジャーナルガイドライン次第） | 低 |
| 全 33 件の完全整合 entry | 追加修正なし | — |

## 依然として手元にない論文

第10バッチで取得予定（Vera-Tudela 2017 は DOI/書誌は完全整合済 + Dimitrov 2015 も同様）
- Vera-Tudela & Kühn 2017 (Renewable Energy 107:352-360) — Crossref 整合 ✅、本文未読 → 第10バッチ精読対象
- Dimitrov, Natarajan & Kelly 2015 (Wind Energy 18(11):1917-1931) — Crossref 整合 ✅、本文未読 → 第10バッチ精読対象
