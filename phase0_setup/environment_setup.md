# Phase 0：環境整備メモ

作成日: 2026-03-31
ステータス: W02 進行中

---

## 1. OpenOA

### 概要

NREL（米国国立再生可能エネルギー研究所）が開発した、風力発電所の運用実績データを分析するためのPythonライブラリ。
Wind Plant Performance Prediction（WP3）Benchmarkプロジェクトの一環として開発。

**本研究での位置づけ**：Phase 3（SCADA時系列解析）の共通解析基盤。時系列データのQC・前処理・分析の標準ワークフローとして使う。

### 主な機能

| 機能 | 内容 |
|---|---|
| MonteCarloAEP | 短期運転データから長期年間発電量（AEP）と不確実性を推定 |
| TurbineLongTermGrossEnergy | ウェイク損失は考慮し、停止は除外したタービン発電量を算出 |
| ElectricalLosses | タービン発電量とグリッド受電量の差（送電損失）を定量化 |
| EYAGapAnalysis | 建設前予測値と実績値の乖離を分析 |
| WakeLosses | ウェイク損失とその不確実性を評価 |
| StaticYawMisalignment | ヨー角ずれの検出 |

### データ形式

**PlantDataスキーマ**：複数データソースをPandas DataFrameで統合する中心的データ構造。

受け付けるデータ：
- 風車SCADAデータ
- 気象観測塔（Met tower）データ
- 売電メーターデータ
- 再解析データ（ERA5、MERRA-2など）

### インストール

```bash
pip install openoa
```

Python 3.9〜3.12 対応。

```bash
# 開発・例題込みでインストールする場合
pip install "openoa[develop,examples]"
```

### 本研究での使い方（予定）

- Phase 3：公開SCADAデータのQC・前処理・基本統計分析
- Phase 3：正常運転ベースラインの構築
- Phase 4：画像スコアと統合する際の時系列特徴量生成

### 参考リンク

| 名称 | URL |
|---|---|
| 公式ドキュメント | https://openoa.readthedocs.io/ |
| GitHubリポジトリ | https://github.com/NREL/OpenOA |
| JOSS論文 | https://www.theoj.org/joss-papers/joss.02171/10.21105.joss.02171.pdf |

---

## 2. OpenFAST

### 概要

NRELが開発した、風車の挙動を物理モデルで再現する多目的シミュレーションツール。
旧FAST v8の後継。空力・水力・制御・構造を統合した時間領域シミュレーションが可能。

**本研究での位置づけ**：Phase 5（シミュレーション・デジタルツイン連携）の工学的基盤。
Phase 1〜4では直接使わないが、将来の疲労負荷推定・デジタルツイン接続に必要なため概要把握を優先。

### 主な機能

| モジュール | 内容 |
|---|---|
| 空力モデル | ブレード要素運動量理論（BEM）・動的失速・ウェイク効果 |
| 構造モデル | タワー・ナセル・ロータの弾性変形・振動解析 |
| 制御モデル | ピッチ制御・トルク制御・ヨー制御のシミュレーション |
| 水力モデル | 洋上風車の波浪・海流荷重（洋上案件向け） |
| FAST.Farm | 複数タービンのウェイク干渉を含む風力発電所シミュレーション |

### 出力データ

- 時系列の荷重・発電量・構造応答・制御状態
- 自然振動数・減衰比・モード形状（線形化解析）
- VTKファイル（3D可視化：Paraviewで閲覧可能）

### 本研究での使い方（予定）

- Phase 5：ブレードの疲労荷重推定の工学的根拠として使う
- Phase 5：デジタルツイン連携の入り口として使う
- 当面の目標：読める・少し動かせる状態にする

### インストール

```bash
# Pythonバインディング（openfast-toolbox）
pip install openfast-toolbox

# 本体のビルドはCMakeが必要（Phase 5時点で対応）
```

### 参考リンク

| 名称 | URL |
|---|---|
| 公式ドキュメント | https://openfast.readthedocs.io/ |
| GitHubリポジトリ | https://github.com/OpenFAST/openfast |
| ユーザーガイド | https://openfast.readthedocs.io/en/dev/source/user/index.html |

---

## 3. 両ツールの比較

| 観点 | OpenOA | OpenFAST |
|---|---|---|
| 主な用途 | 実運転データの分析・性能評価 | 物理モデルによる風車挙動シミュレーション |
| 入力データ | SCADA・気象データ（実測値） | 風況条件・タービンパラメータ |
| 出力データ | AEP・損失分析・性能ギャップ | 時系列荷重・発電量・構造応答 |
| 本研究での登場フェーズ | Phase 3〜4 | Phase 5 |

---

## 4. Python仮想環境の構築手順

Phase 1（YOLOv8）とPhase 3（OpenOA）で必要なパッケージが異なるため、フェーズ別に環境を分けることを推奨。

### Phase 1用（画像解析環境）

```bash
conda create -n blade-phase1 python=3.11
conda activate blade-phase1
pip install ultralytics opencv-python matplotlib pandas numpy
```

### Phase 3用（SCADA時系列環境）

```bash
conda create -n blade-phase3 python=3.11
conda activate blade-phase3
pip install openoa pandas numpy matplotlib seaborn jupyterlab
```

### requirements.txtの管理

各環境のパッケージは以下で書き出す。

```bash
pip freeze > requirements_phase1.txt
pip freeze > requirements_phase3.txt
```

---

## 5. 進捗

- [x] OpenOA概要把握（2026-03-31）
- [x] OpenFAST概要把握（2026-03-31）
- [ ] Python仮想環境の構築（Phase 1用）
- [ ] DTU原データの取得確認（W03）
