# Bak 2013 DTU Wind Energy Report-I-0092 全頁完全精読レポート

**実施日**: 2026-04-27（待機作業 D）
**対象**: DTU Wind Energy Report-I-0092「Description of the DTU 10 MW Reference Wind Turbine」
**著者**: C. Bak, F. Zahle, R. Bitsche, T. Kim, A. Yde, L.C. Henriksen, A. Natarajan, M.H. Hansen
**発行**: 2013年7月
**仕様**: 138 pages, 69 tables, 62 figures, 41 references
**精読方式**: 戦略 A（主張駆動完全精読）、1セッション分割なし

---

## 0. 取得経路

- DTU GitLab repository（公開）: `https://gitlab.windenergy.dtu.dk/rwts/dtu-10mw-rwt/-/raw/master/docs/DTU_Wind_Energy_Report-I-0092.pdf`
- Curl で取得成功（138頁、12 MB）
- 配置先: `docs/references/open_access/Bak_2013_DTU10MW_Report-I-0092_FullText.pdf`
- 既存の `Bak_2013_DTU10MW_Reference.pdf`（22頁プレゼン版）と並置

---

## 1. 章別精読結果

| 章 | 頁 | 主題 | 結果 |
|---|---|---|---|
| Title + Abstract | 1-4 | 138p Technical Report、Light Rotor project / EUDP2010-I funded、Vestas協力 | ✅ |
| Contents | 5-6 | §1-§7 + Appendix A-E | ✅ |
| §1 Introduction | 7-10 | "Mass increases with cube of rotor radius with linear upscaling" / Light Rotor project (DTU + Vestas) / NREL 5MW [1] inspired / How to Refer / Data Repository / Version 1.0 (2013-07-03) | ✅ Mass~R³ 直接記述 |
| §2 Overall Dimensions | 11-13 | **§2.1 Upscaling Procedure**: Eq 2.1 m∝sf³, Eq 2.2 P∝sf², Eq 2.3 L∝sf, Eq 2.4 I₁∝sf⁴, Eq 2.5 I₂∝sf⁵, Eq 2.6 sf=√(10/5)=√2 / **§2.2 Key Parameters**: Table 2.1 D=178.3 m, HH=119 m, P=10 MW, IEC 1A | ✅ Mass~D³ 数式裏付け |
| §3 Aerodynamic Design | 15-36 | §3.1 FFA-W3-xxx airfoil series / §3.2 Rotor Design (R=89.166m, TSR=7.5) / §3.3 BEM via HAWTOPT / §3.4 3D Blade Geometry / §3.5 CFD vs HAWCStab2 比較 | ✅ |
| §4 Structural Design | 37-62 | **§4.1.1 Material**: glass fiber + epoxy + balsa wood（**carbon fiber未使用**）/ §4.1.2 Internal layup (caps/webs/panels) / §4.1.3 BECAS Cross Section（Tables 4.9, 4.10）/ §4.1.4 Strength Analysis / §4.1.5 Buckling / §4.2 Tower (steel S355) | ✅ Material は glass fiber + balsa（carbon fiber は基本材料に使われていない） |
| §5 Control | 63-64 | Basic DTU Wind Energy Controller (proportional-integral) / TSR=7.5 / 0.05 Hz partial / 0.06 Hz full load | ✅ |
| §6 Aero-Servo-Elastic Design | 65-83 | §6.1-§6.2 Components / §6.3 DLC list / §6.4.1 Eigenvalue / §6.4.2 Statistic (DLC1.1) / §6.4.3 Ultimate (DLC1.3 driving for blade flapwise) / **§6.4.4 Fatigue (DLC1.2): Eq 6.1 DEL formula、Wöhler m=10 (blade), m=3 (steel)、N_ref=10⁷ cycles, 20 yr life** / §6.4.5 Tower Clearance (DLC1.3 driving, 32% margin) / §6.4.6 Vibration / §6.4.7 Run-Away | ✅ **m=10 (blade) 直接記述** |
| §7 Conclusions | 85 | Light Rotor project / EUDP / Reasonable design (not lightest, not best performing) / Edgewise vibrations / Reynolds 10M uncertainty | ✅ |
| Acknowledgements | 87 | EUDP2010-I funded / Vestas (Vronsky, Heinen) / CRES / GL-GarradHassan via InnWind | ✅ |
| Bibliography | 89-91 | 41 references including [1] Jonkman 5MW, [27] DOE/MSU fatigue DB (Mandell), [34] IEC 61400-1, [37] HAWC2 manual | ✅ |
| Appendix A Cubic Splines | 93-100 | Tables A.1-A.6: chord, relative thickness, twist, pitch axis–LE distance, cap center position, cap width all as cubic spline coefficients | ✅ 数値データのみ |
| Appendix B Geometry | 101-102 | File listing of 3D blade / nacelle / spinner / tower coordinates | ✅ |
| Appendix C CFD Data | 103-105 | 2D CFD mesh files for FFA-W3-224/301/336GF/348GF/360GF + 3D rotor mesh | ✅ |
| Appendix D Load Cases | 107-109 | Table D.1: IEC 61400-1 DLC 1.1〜7.1 with safety factors | ✅ 標準DLC |
| Appendix E Extreme Loads | 111-138 | Tables E.1〜E.27: 27 blade cross sections × 14 load components extreme load tabulation（DLC1.3 driving for blade root flapwise extremes） | ✅ 数値データのみ |

**精読範囲**: 全138頁完全精読（ただし Appendix E のうち §3-4 の主張に関連しない数値表 pp.116-138 はスキャン読み）

---

## 2. Paper 2 [3] 引用主張との照合

### 現状の Paper 2 §2.2 line 122 の引用文

> "Bak et al. (2013) はDTU 10MW参照タービンの設計にあたり、**幾何スケーリングの背景（Mass ~ Diameter^3 の古典的関係）を紹介した [3]**。... Bak et al. (2013) も**glass fiber: Mass = 0.0023 × Length^2.17、carbon fiber: Mass = 9×10^-5 × Length^2.95 を報告している [3]**。"

両 [3] とも「DTU Wind Energy Report-I-0092」を指している。

### 主張駆動検証結果

| 主張 | Report-I-0092 内の対応箇所 | 結果 |
|---|---|---|
| **A. Mass ~ Diameter³ の古典的関係** | §1 Introduction p.7: "Upscaling causes a challenge because **the mass of the turbine increases with the cube of the rotor radius with linear upscaling**" / §2.1 Eq 2.1: m ∝ sf³, Eq 2.3: L ∝ sf¹（Mass ∝ Length³ ⇔ Mass ∝ Diameter³） | ✅ **完全裏付け** |
| **B. glass fiber: Mass = 0.0023 × Length^2.17** | **138頁全体に該当する数式は存在しない**。§4.1.1 で blade material が glass fiber + epoxy + balsa wood と確認できるのみ。Length-Mass の経験式は本 Report 内では提示されていない | ❌ **本文書内には不在** |
| **C. carbon fiber: Mass = 9×10^-5 × Length^2.95** | **138頁全体に該当する数式は存在しない**。さらに §4.1.1 で確認した通り、DTU 10MW 参照ブレードは glass fiber 設計であり、**carbon fiber は基本材料として使われていない** | ❌ **本文書内には不在**、carbon fiber は DTU 10MW 設計対象外 |

### 重要な発見：Length^2.17 / Length^2.95 の出典は「プレゼン版」

第3バッチ（2026-04-26）で精読した **22頁プレゼン版**（`Bak_2013_DTU10MW_Reference.pdf`、Sound/Visual production digital, Danish Wind Power Research 2013）には、p.3 / p.14 に Mass-Length 散布図と回帰式が記載されており、これが Length^2.17 / Length^2.95 の出典です。

つまり、**プレゼン版と本体 Technical Report は同じ Bak グループの出力物だが、内容が一部異なる**：
- プレゼン版（22p）：商用ブレードの Mass-Length 散布図 + 回帰式（Length^2.17 glass / Length^2.95 carbon）+ DTU 10MW を比較プロット
- 本体 Report-I-0092（138p）：DTU 10MW 設計の詳細記述。プレゼン版の散布図・回帰式は**含まれていない**

### Paper 2 [3] の引用構造の問題

Paper 2 [3] は明示的に "DTU Wind Energy Report-I-0092" のみを書誌情報に記載している。しかし、Length^2.17 / Length^2.95 の数式は Report-I-0092 内に存在せず、プレゼン版にのみ記載されている。これは**引用と書誌情報の不一致**であり、過去の Bir & Jonkman 2007 / Pandit 2023 / Colone 2018 のような重大ハルシネーションとは異なるが、**書誌情報精度の問題**として扱うべき。

### 副次的発見：m=10 の独立支持

Report-I-0092 §6.4.4 Fatigue Load Analyses (p.74) は、DEL 計算に **Wöhler exponent m=10 (blade), m=3 (steel)** を明示使用：

> "For the blade loads a Wöhler exponent of m = 10 has been used. Other components are assumed to be steel, m = 3."

これは Paper 2 §3.4 の m=10 採用根拠（DNVGL-ST-0376 + Mandell 1997 b=0.10）に対する**独立な実例支持**となる。ただし Paper 2 §3.4 はすでに DNVGL-ST-0376 と Mandell 1997 を引用済みなので、追加引用は必須ではない。

---

## 3. Paper 2 修正提案（v9.5 候補）

### 修正案 α（推奨：書誌精度向上）

Paper 2 [3] を **2件に分割**し、出典を明確化する：

- **新 [3a]**: Bak, C., Zahle, F., Bitsche, R., Kim, T., Yde, A., Henriksen, L.C., Natarajan, A., Hansen, M.H. (2013). Description of the DTU 10 MW Reference Wind Turbine. **DTU Wind Energy Report-I-0092**. Technical University of Denmark.
- **新 [3b]**: Bak, C. (2013). The DTU 10-MW Reference Wind Turbine. Sound/Visual production (digital), Danish Wind Power Research 2013, 28 May 2013. DTU Orbit (open access).

§2.2 line 122 の修正：
- 「Mass ~ Diameter³ の古典的関係を紹介した [3a]」（Report-I-0092 §1 / §2.1 を典拠に）
- 「glass fiber: Mass = 0.0023 × Length^2.17、carbon fiber: Mass = 9×10⁻⁵ × Length^2.95 を報告している [3b]」（プレゼン版を典拠に）

**メリット**：書誌精度が向上、過去のハルシネーション修正基準と整合
**デメリット**：参考文献リストの番号が1つ増える（軽微）

### 修正案 β（最小修正：表現の精緻化のみ）

Paper 2 [3] は Report-I-0092 のまま維持し、Length^2.17 / Length^2.95 の主張を Report 本体の主旨により近づけて再表現する：

- 旧: 「Bak et al. (2013) もglass fiber: Mass = 0.0023 × Length^2.17、carbon fiber: Mass = 9×10⁻⁵ × Length^2.95 を報告している [3]」
- 新: 「Bak et al. (2013) [3] は DTU 10MW 参照ブレードを **glass fiber + epoxy + balsa wood** で設計し、Mass ∝ sf³（Length ∝ sf¹）の幾何相似スケーリングを採用した（§2.1 Eq 2.1, §4.1.1）」

そして §5.4 Limitation 2 で λ_R^2.3 の根拠説明から Length^2.17 / Length^2.95 の参照を削除し、Fingersh 2006 の数値範囲（baseline 2.92 / advanced 2.53）と「商用ブレードの市場データに基づく経験則」一般論で代替する。

**メリット**：書誌情報の整合性が完全に保たれる（[3] = Report-I-0092 の内容と一致）
**デメリット**：Paper 2 §5.4 Limitation 2 の数値根拠が単一文献（Fingersh）に縮小

### 修正案 γ（最終投稿時のみ）

第10バッチ（Vera-Tudela / Dimitrov）完了後、Paper 2 v9.5 へ昇格する際に修正案 α を適用する。本待機作業 D ではメモリ記録のみとし、本文修正は次回バッチに委ねる。

**メリット**：第10バッチ修正と同時に整理できる、修正回数を抑える
**デメリット**：判定が先送りになる

---

## 4. 推奨

**修正案 α** を推奨します。理由：
- 過去のハルシネーション修正（Dao 2018 DOI修正、Robertson 2017 DOI修正、Colone 2018 [11] 差し替え等）と同じ精度基準
- プレゼン版の DTU Orbit OA URL は既に確認済み（DTU Orbit 55645274）であり、書誌情報の補完が容易
- 修正案 β は λ_R^2.3 の根拠説明が弱まり、§5.4 Limitation 2 の論理が脆くなる
- 修正案 γ は遅延を生むだけで本質的解決にならない

ただし、適用タイミングは **修正案 γ 流（次回バッチで一括）** が効率的。本作業 D ではメモリに記録のみ行い、第10バッチ完了時に v9.5 として α を適用する形にします。

---

## 5. 副次成果

### 副-1：DEL 公式の独立確認

§6.4.4 Eq 6.1:
```
DEL = (1/N_ref · Σ_i (T_life,i / T_sim,i · Σ_k N_i,k S_i,k^m))^(1/m)
```

これは Paper 2 §3.4 の DEL 公式と完全等価で、Hayman 2012 MLife Theory Eq 30 とも整合する。N_ref = 10⁷ cycles, 20年寿命は IEC 61400-1 慣行と整合。

### 副-2：DTU 10MW の正確な書誌情報

- 報告書番号: DTU Wind Energy Report-I-0092
- 発行年月: 2013年7月
- 著者順: Christian Bak, Frederik Zahle, Robert Bitsche, Taeseong Kim, Anders Yde, Lars Christian Henriksen, Anand Natarajan, Morten Hartvig Hansen（**Paper 2 [3] は "Bak, C., Zahle, F., Bitsche, R., et al." と簡略化表記**）
- 言及スタイル: §1.1 で公式の "How to Refer" 案内あり（「C. Bak; F. Zahle; R. Bitsche; T. Kim; A. Yde; L.C. Henriksen; P.B. Andersen; A. Natarajan, M.H. Hansen; "Design and performance of a 10 MW wind turbine", J. Wind Energy, To be accepted」）

### 副-3：Bibliography 内の他文献

- [1] Jonkman 2009 NREL 5MW（Paper 2 [2] と同じ）
- [27] DOE/MSU Composite Material Fatigue Database（Paper 2 [18] Mandell の対応）
- [34] IEC 61400-1（Paper 2 [7] と同じ規格）

これらは Paper 2 が引用する文献を Report-I-0092 も同じく引用しており、研究コミュニティとしての文献経路の一貫性が確認できる。

---

## 6. ハルシネーション率（37本中、第10バッチ前）

待機作業 D により Bak 2013 の引用に **書誌精度の軽微な問題1件** を新規発見：
- 重大ハルシネーション 3本（変更なし）
- 軽微な問題 7本（変更なし、すべて修正済）
- 軽微な精緻化候補 1件（Tautz-Weinert、第10バッチで再評価）
- **新規：書誌精度問題 1件**（Bak 2013 [3]、Length^2.17 / Length^2.95 がプレゼン版にのみ存在、Paper 2 v9.5 で修正案 α 適用予定）

完全整合の論文が大半を占めることを再確認。
