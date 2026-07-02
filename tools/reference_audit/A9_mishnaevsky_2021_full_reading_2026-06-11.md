# A9: Mishnaevsky Jr. et al. (2021) 全頁主張駆動精読結果

**実施日**: 2026-06-11
**目的**: A9（Mishnaevsky 2021 を Paper 1/2/3 に引用追加）の判断材料整備
**取得経路**: WebSearch で発見した wind-watch.org の OA PDF（docs.wind-watch.org/mishnaevsky2021.pdf）

---

## 1. 書誌情報

| 項目 | 内容 |
|---|---|
| Title | Leading edge erosion of wind turbine blades: Understanding, prevention and protection |
| Authors | Leon Mishnaevsky Jr., Charlotte Bay Hasager, Christian Bak, Anna-Maria Tilg, Jakob I. Bech, Saeed Doagou Rad, Søren Fæster |
| Affiliation | Department of Wind Energy, **Technical University of Denmark (DTU)**, Roskilde, Denmark |
| Journal | Renewable Energy 169 (2021) 953-969 |
| DOI | 10.1016/j.renene.2021.01.044 |
| Received | 11 May 2020 |
| Accepted | 7 January 2021 |
| Available online | 12 January 2021 |
| Pages | 17 頁（pp.953-969） |
| 取得元 URL | https://docs.wind-watch.org/mishnaevsky2021.pdf |
| ファイル配置 | `open_access/Mishnaevsky_2021_LE_Erosion_Understanding_Renew_Energy.pdf`（5.15 MB） |
| 助成 | Innovation Foundation of Denmark (DURALEDGE, EROSION), EUDP Denmark, Danish Agency for Science and Higher Education |

---

## 2. 論文構成

| 章 | 内容 |
|---|---|
| §1 Introduction | LEE 問題の総論、3 つの対策戦略（avoidance/repair/protection） |
| §2 LEE が aerodynamics に与える影響 | §2.1 LE roughness 法・効果、§2.2 Critical LE roughness |
| §3 AEP losses due to LEE | 経済損失の定量化 |
| §4 LEE: how it goes | 物理機序（rain droplet impact → wave → crack → debonding） |
| §5 Testing and mechanisms | §5.1 RET と SPIFT、§5.2 Microscopy |
| §6 Precipitation: meteorology role | §6.1 DSD 等パラメータ、§6.2 lifetime 予測、§6.3 地域差 |
| §7 Computational modelling of LEE | §7.1 rain 確率モデル、§7.2 drop/surface 相互作用、§7.3 fatigue modelling、§7.4 erosion → aerodynamics |
| §8 Anti-erosion coatings | §8.1 predictors、§8.2 optimization（PU/multilayer/reinforced/IPN/surface roughness） |
| §9 Erosion safe mode control | tip speed 削減による erosion mitigation |
| §10 Conclusions | multiscale multiphysics プロセスとしてのまとめ |

---

## 3. Paper 1/2/3 への引用候補

### 3.1 Paper 1 への引用候補（3 件）

#### P1-M-A: §1 Introduction（動機強化）

**引用箇所**: Paper 1 §1 Introduction 末尾または冒頭

**引用案**:
> "Leading edge erosion is a multiscale, multiphysics process involving meteorology, aerodynamics, materials science, and computational mechanics (Mishnaevsky et al. 2021 [新規]). Industry response by major operators—exemplified by Ørsted's repair campaign at the Anholt Offshore Wind Farm in 2016—underscores the operational urgency of detection-driven prioritization."

**根拠**:
- Mishnaevsky 2021 §1 で Anholt 2016 補修事例を明示
- §10 Conclusions で "multiscale multiphysics process" と総括

**効果**: himinさん の現場経験と研究動機を実際の産業事例で裏付け

#### P1-M-B: §2.3 Risk Scoring（重み根拠の物理的補強）

**引用箇所**: Paper 1 §2.3 line 62 付近、Malik & Bak 2025 引用の周辺

**引用案**:
> "Computational studies summarized in Mishnaevsky et al. (2021 [新規]) demonstrate that drop impact speed from 150 to 200 m/s increases peak stress by up to 35%, while surface roughening further amplifies local stress concentration (§7.2 of Mishnaevsky 2021). This physical mechanism supports the higher tip-region weight (3.0) used in our risk scoring framework, as tip regions experience higher relative wind velocity."

**根拠**:
- §7.2: "increasing the drop contact speed from 150 to 200 m/s leads to 35% increase in the peak stress values"
- §7.2: "surface roughness increases the local stress concentration"
- §2.2 critical roughness 閾値: c^0.5 〜 c^0.8

**効果**: practitioner-informed priors の物理的根拠を強化（v8 で訂正された「general aerodynamics + practitioner priors」の物理的層を補強）

#### P1-M-C: §5.3 O&M Discussion（産業意義）

**引用箇所**: Paper 1 §5.3 Discussion

**引用案**:
> "Mishnaevsky et al. (2021 [新規]) report that loss of AEP from blade leading edge erosion accounts for €56-75 million per year across the European offshore wind energy sector, with AEP losses ranging from 1.8% (mild) to 7.1% (severe) under realistic erosion configurations [Kruse cited in Mishnaevsky 2021]. This economic scale motivates the detection-driven prioritization framework proposed here."

**根拠**:
- §3: "loss in AEP from blade leading edge erosion accounts for a loss in productivity with between €56 million and €75 million a year across the European offshore wind energy sector" (引用 [39])
- §3: Kruse [41] AEP losses 1.8% and 7.1% on three fictive LER configurations

**効果**: Paper 1 の応用意義を欧州オフショアの経済影響で裏付け

---

### 3.2 Paper 2 への引用候補（2 件）

#### P2-M-A: §1 Introduction（疲労研究の動機強化）

**引用箇所**: Paper 2 §1 Introduction

**引用案**:
> "Mishnaevsky et al. (2021 [新規]) identify the relationship between erosion-induced surface roughness and fatigue loading as a key open question in wind turbine blade lifetime estimation. Computational studies of LEE often employ fatigue degradation prediction codes combining critical plane models, Miner-Palmer rule, and rainflow counting (e.g., Douagou-Rad and Mishnaevsky Jr., cited in Mishnaevsky 2021 §7.3), aligning with the rainflow-based DEL estimation framework applied here."

**根拠**:
- §7.3: "Douagou-Rad and Mishnaevsky Jr. developed a fatigue degradation prediction code, based on the critical plane models... Miner-Palmer fatigue rule and the rainflow counting"

**効果**: Paper 2 の rainflow + DEL アプローチを LE erosion 研究の同種手法と接続

#### P2-M-B: §2 Related Work（疲労 modelling 補強）

**引用箇所**: Paper 2 §2 Related Work（既存の Downing & Socie [14] 引用周辺）

**引用案**:
> "In the context of LEE-driven blade lifetime modelling, computational fatigue models based on rainflow counting and Miner-Palmer rule have been developed for coating degradation prediction (Mishnaevsky et al. 2021 [新規], §7.3). The present study applies the same rainflow methodology at the blade root flapwise bending moment scale, complementing surface-level erosion studies."

**根拠**:
- §7.3 で fatigue modelling of erosion を詳述
- Paper 2 の rainflow + S-N curve approach と方法論的整合

**効果**: Paper 2 を materials science 側の erosion 研究と接続

---

### 3.3 Paper 3 への引用候補（3 件）

#### P3-M-A: §1 Introduction（統合パイプラインの動機）

**引用箇所**: Paper 3 §1 Introduction 末尾

**引用案**:
> "Mishnaevsky et al. (2021 [新規]) describe leading edge erosion as a multiscale multiphysics process whose mitigation requires understanding the interactions between meteorology (precipitation), aerodynamics (LE roughness effect on AEP), materials science (coating microstructure), and computational mechanics. The integrated pipeline proposed here addresses this multi-domain challenge by combining image-derived damage state (Paper 1), SCADA-derived fatigue loading (Paper 2), and meteorological data—directly aligned with the multi-aspect understanding called for in the recent literature."

**根拠**:
- §10 Conclusions: "Surface degradation of wind turbine blades is a complex multiscale and multiphysical process"
- §1 Introduction: "The idea is that the solution of the LEE problem lies in understanding of all aspects"

**効果**: 統合パイプライン の研究意義を「分野横断の必然性」として外部視点で裏付け

#### P3-M-B: §2 Related Work（気象データ統合の物理根拠）

**引用箇所**: Paper 3 §2 Related Work

**引用案**:
> "The importance of precipitation characteristics—specifically drop-size distribution (DSD) at hub height—for LEE prediction has been emphasized by Mishnaevsky et al. (2021 [新規], §6). The Risø field site, for instance, deploys Ott Parsivel² disdrometers at both ground level and 123 m height to enable DSD comparison across vertical scales (Mishnaevsky et al. 2021 §6.2). This precipitation-focused perspective complements the SCADA + image fusion approach of the present integration pipeline."

**根拠**:
- §6.1-6.3: DSD の重要性、Risø 観測網、地域差
- Hub height 100m での DSD と地表 DSD の違い

**効果**: 気象データ統合の物理的・観測的根拠を確立

#### P3-M-C: §6 Future Work（erosion-safe operation との接続）

**引用箇所**: Paper 3 §6 Future Work / Conclusion

**引用案**:
> "An emerging research direction is erosion-safe mode control (Mishnaevsky et al. 2021 [新規], §9), where tip speed reduction during heavy precipitation events mitigates LEE. Skrzypiński et al. (cited in Mishnaevsky 2021) demonstrated that 88% of profit loss due to LEE can be saved through such control on the IEA 15 MW Reference Turbine. The integrated pipeline proposed here could in principle inform this control strategy by predicting degradation progression from SCADA and image inputs."

**根拠**:
- §9: "preventing the blade erosion by reducing the tip speed during heavy precipitation events allows saving the costs"
- §9: Skrzypiński et al. "88% of the overall profit loss due to the leading edge erosion could be saved by using the erosion-safe operation"

**効果**: Paper 3 の将来研究方向（O&M 実務応用）を最新の制御戦略と接続

---

## 4. 副次発見（取得候補 + 知識補強）

### 4.1 Mishnaevsky 2021 経由で発見された関連研究

| # | 論文（引用元 Ref 番号） | 関連性 |
|---|---|---|
| 1 | **Sareen et al. [36]** "Effects of leading-edge protection tape on wind turbine blade performance" Wind Energy 36 (2012) | DU96-W-180 erosion テスト原典、AEP losses 5-25% の根拠 |
| 2 | **Bak et al. [37]** "The Influence of LE Roughness on AEP" (2020 EAWE Torque Conference) | NACA63₃-418 airfoil 上 AEP losses 1-4% の原典 |
| 3 | **Schramm et al. [30]** "The influence of eroded blades on wind turbine performance" Energies 10 (2017) | 数値シミュレーション AEP 2-3.7% loss |
| 4 | **Kruse [41] [49]** PhD Thesis (Risø, 2019) | AEP losses 1.8-7.1%、LER 影響評価 |
| 5 | **Herring et al. [7]** "Increasing importance of LEE and protection coatings" Renew. Sustain. Energy Rev. 115 (2019) | €56-75M/year 経済損失の原典 |
| 6 | **Skrzypiński et al. [137]** "Optimization of the Erosion-Safe Operation of IEA 15MW" (2020) | Erosion-safe control の経済モデル |
| 7 | **Bech et al. [3]** "Extending the life of LEE by reducing tip speed during precipitation" Wind Energy Sci. | Erosion-safe operation の戦略提唱 |
| 8 | **Hasager et al. [83]** "Assessment of rain and wind climate with focus on offshore wind farms" Renew. Energy (2019) | DSD と offshore erosion の関係 |
| 9 | **Letson et al. [138]** "Radar-derived precipitation climatology for wind turbine blade leading edge erosion" Wind Energy Sci. 5 (2020) | 気象データ統合の方法論先行例 |
| 10 | **Tilg et al. [139]** "Brief communication: Nowcasting of precipitation for LEE-safe mode" Wind Energy Sci. 5 (2020) | 気象予報による LEE-safe 制御 |

これらは Paper 1/2/3 へ追加引用するかは判断保留。Mishnaevsky 2021 のレビュー文脈で「経由引用」する形が多くの場合適切。

### 4.2 Douagou-Rad & Mishnaevsky 2017 の特別位置

§7.3 で言及される **Douagou-Rad and Mishnaevsky Jr.** の fatigue degradation prediction code:
- Critical plane models
- Miner-Palmer fatigue rule
- Rainflow counting

→ **Paper 2 [14] Downing & Socie 1982 と同種のアプローチ** を coating degradation に適用した先行例。Paper 2 の方法論を materials science 側に橋渡しする引用素材。

---

## 5. 推定優先度の評価

### Claude Code の推奨

| 引用箇所 | 推定優先度 | 理由 |
|---|---|---|
| **P1-M-A**（Paper 1 §1 Anholt 2016 + multiscale process） | **🔴 高** | 研究動機を産業事例 + 物理機序で裏付け |
| **P1-M-C**（Paper 1 §5.3 €56-75M/year + 1.8-7.1% AEP） | **🔴 高** | 経済意義を強力な数値で裏付け |
| **P3-M-A**（Paper 3 §1 multiscale multi-domain） | **🔴 高** | 統合パイプライン の研究意義を「分野横断の必然性」で正当化 |
| **P3-M-B**（Paper 3 §2 DSD / 気象統合の物理根拠） | **🟡 中-高** | Paper 3 の気象データ統合の物理的根拠 |
| **P2-M-A**（Paper 2 §1 erosion-fatigue 結合） | 🟡 中 | Paper 2 の動機補強（任意） |
| **P2-M-B**（Paper 2 §2 rainflow + critical plane 接続） | 🟡 中 | Paper 2 の Downing & Socie [14] 引用と並列補強 |
| **P1-M-B**（Paper 1 §2.3 重み根拠の物理補強） | 🟢 中 | practitioner-informed priors の補強（任意） |
| **P3-M-C**（Paper 3 §6 erosion-safe control 接続） | 🟢 中 | Future Work の方向性提示 |

### 最低限の推奨適用範囲

**最も価値の高い 3 件**:
1. **P1-M-A** + **P1-M-C**（Paper 1 動機 + 経済）
2. **P3-M-A**（Paper 3 統合の正当化）

これだけで Paper 1/3 の「**LE erosion 物理理解の深さ**」が大幅に向上。

---

## 6. 書誌追加のコスト

Mishnaevsky 2021 を引用する場合：

| Paper | 参考文献追加 | 必要番号 |
|---|---|---|
| Paper 1 | 追加必要 | 例: [17] |
| Paper 2 | 追加必要（適用する場合） | 例: [23] |
| Paper 3 | 追加必要 | 例: [26] |

---

## 7. ファイル整理状況

| ファイル | 配置 |
|---|---|
| `Mishnaevsky_2021_LE_Erosion_Understanding_Renew_Energy.pdf` | `open_access/`（5.15 MB, 17 頁） |

---

## 8. Aird 2023 / Law 2020 の取得状況

| 論文 | OA status | 取得経路試行 | 結果 |
|---|---|---|---|
| Aird & Barthelmie 2023 | gold (MDPI Energies, CC-BY) | MDPI 直接 / OSTI / ResearchGate | **すべて失敗**（bot blocking）|
| Law & Koutsos 2020 | hybrid (Wind Energy, CC-BY) | Edinburgh repo / Wiley 直接 | **失敗**（Cloudflare challenge）|

両論文とも OA でありながら自動取得は困難。himinさん による手動取得が必要：
- Aird 2023: ブラウザで `https://www.mdpi.com/1996-1073/16/6/2820` にアクセス → "Download PDF" ボタン
- Law 2020: ブラウザで `https://www.research.ed.ac.uk/files/158543005/Wind_Energy_Manuscript_V2.pdf` にアクセス（Cloudflare チャレンジを通過）

ただし、これらは Paper 1/2/3 への引用候補としては **Mishnaevsky 2021 より優先度低い**（Aird 2023 は LE erosion 画像定量化の先行例、Law 2020 は実機運用評価）。

---

## 9. 関連メモ

- `tools/reference_audit/B5_incidental_findings_citation_candidates_2026-04-29.md` — 副次発見の引用候補集
- `tools/reference_audit/batch10_round2B_part1_progress_2026-04-29.md` — Vera-Tudela 2017 / Heo & Na 2025 精読結果
- `memory/project_blade_paper_audit_progress.md` — 監査全体の進捗

---

## 10. 次のステップ

1. ✅ Mishnaevsky 2021 精読 + ドキュメント化（本ファイル）
2. ⏸ himinさん による P1-M-A〜C、P2-M-A〜B、P3-M-A〜C の採用判断
3. ⏸ Aird 2023 / Law 2020 の手動取得（任意・優先度低）
4. ⏸ Vera-Tudela 2017 と Heo & Na 2025 を `data/` から `open_access/` に整理移動
5. ⏸ memory / URL_INDEX.md 更新
