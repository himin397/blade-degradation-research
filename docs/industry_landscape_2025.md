# 業界動向：ドローン点検・標準化・デジタルツイン（2025-2026調査）

調査日: 2026-04-02

---

## 1. 標準化の現状

**結論：ドローン点検プロトコル専用のIEC規格は2026年4月時点で存在しない。**

| 規格 | 内容 | ドローン点検との関係 |
|---|---|---|
| IEC 61400-5:2020 | ブレード設計・製造・品質管理 | 点検義務の根拠になるが「どう撮るか」は規定しない |
| IEC 61400-24 | 避雷システム点検 | LPS点検で直接参照される |
| DNV-ST-0376（2024改訂） | ブレード設計・製造・信頼性 | 26社参加のJIPで策定。damage tolerance概念を導入。点検プロトコルではない |

複数のレビュー論文が「損傷分類・データフォーマットの業界統一規格が欠如している」と明示的に指摘している（MDPI Electronics 2025、IEEE Access 2024）。

---

## 2. 「同一箇所の年次比較」問題への技術的アプローチ

現在最もアクティブな研究領域。3系統のアプローチが存在する。

### (A) LiDAR搭載ドローンによる空間参照
- 各フレームの空間座標をLiDARで確定し、損傷位置を3D座標として記録
- 商用実装：Sulzer Schmid 3DX Platform（2024年RESが買収）
- 再現可能な飛行パスにより年次比較が可能
- 参考：Castelar Wembers et al. (2024), *Journal of Field Robotics*, DOI: 10.1002/rob.22309

### (B) 画像スティッチングによる2D全体マップ化
- U-Net + Sobelエッジ検出 + 等幅特徴マッチングで物理位置とピクセルを紐づけ
- 誤差5%以内で実証済み
- 参考：Fan et al. (2025), *Measurement*, DOI: 10.1016/j.measurement.2025.119032

### (C) 3D再構成（SfM / Gaussian Splatting）
- 単眼深度推定 + 密集画像マッチングの組み合わせ
- 既存ツールより38%以上の再投影誤差削減
- 参考：Sterckx et al. (2025), *Automation in Construction*, DOI: 10.1016/j.autcon.2025.106153

---

## 3. デジタルツインアプローチ（2024-2025 注目論文）

### Hu et al. (2025) — 商用レベルに最も近い
- RDSS-YOLOカスタムアーキテクチャ（検出＋セマンティックセグメンテーション統合）
- **mAP 95.7%、Recall 96.8%**
- 3風力発電所で実運用実績
- ブレードクラック寸法誤差7.24%、前縁エロージョン誤差13.06%
- DOI: 10.1016/j.renene.2024.124005

### von Benzon et al. (2025) — 「同一箇所比較」問題に最も直接的に取り組んだ論文
- ドローン2D画像 → 3Dモデルへの損傷マッピング手法
- AI + カラー閾値セグメンテーション
- 複合材ロータブレードの層間剥離を3D CADモデルに紐づける
- DTU ReliaBlade-2プロジェクトの成果
- DOI: 10.1002/eng2.12837

---

## 4. 注目企業・研究グループ

| 組織 | 取り組み |
|---|---|
| Sulzer Schmid / RES | 3DX Platformで業界最も完成度の高い商用システム。2024年RESが買収 |
| DTU ReliaBlade-2 | ブレード個体デジタルツイン研究。2024年JEC Innovation Award受賞 |
| Heriot-Watt大学 + Fraunhofer | BladeViewシステム（自動飛行パス計算、9,239件の実地フライトで検証済み）IEEE掲載 |
| vHive | 「Digital Standard」でオペレーター非依存の画質・カバレッジ均一化 |

---

## 5. 本研究（himinさん Phase 1-2）との関係

### Phase 1で直面した問題と業界課題の対応
| 本研究の問題 | 業界での位置づけ |
|---|---|
| chord方向（前縁位置）が斜め撮影で特定困難 | 撮影プロトコル非標準化が根本原因。業界全体の課題 |
| 2017/2018の同一箇所対応付けが不可能 | 現在研究中の領域（LiDAR・SfM・スティッチング） |
| mAP 58%（EXP-002）と先行研究95.7%の差 | データ品質・モデルサイズ・撮影条件の違いが主因 |

### 研究的含意
- himinさんが直面した限界は、研究の失敗ではなく**業界の未解決課題を正確に反映している**
- Phase 2で「探索的・仮説生成的」として進める方針は、業界文脈と整合している
- 将来的には (B) 画像スティッチングまたは (C) 3D再構成との統合が、本研究の発展方向として候補になる

---

## 参考文献

- MDPI Electronics 2025 review: https://www.mdpi.com/2079-9292/14/2/227
- IEEE Access 2024 review: https://ieeexplore.ieee.org/document/10453577/
- Castelar Wembers et al. 2024: DOI 10.1002/rob.22309
- Fan et al. 2025: DOI 10.1016/j.measurement.2025.119032
- Sterckx et al. 2025: DOI 10.1016/j.autcon.2025.106153
- Hu et al. 2025: DOI 10.1016/j.renene.2024.124005
- von Benzon et al. 2025: DOI 10.1002/eng2.12837
- DNV-ST-0376 2024: https://www.dnv.com/news/2024/dnv-leads-wind-energy-development-with-industry-standard-for-next-generation-blades/
- DTU ReliaBlade-2: https://reliablade.dtu.dk/
