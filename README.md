# blade-degradation-research

風車ブレード劣化予測モデル構築に向けた個人研究リポジトリ。

## 最終目標

風車ブレードの劣化進行予測モデルを構築し、O&M意思決定支援への接続を目指す。
現場・メーカー・発電事業者の3視点を持つ経験を研究に転化する。

## 研究フェーズ

| フェーズ | テーマ | 状態 |
|---|---|---|
| Phase 0 | 研究基盤整備（OpenOA / OpenFAST） | 進行中 |
| Phase 1 | 画像ベース損傷検出・部位別リスクスコア | 未着手 |
| Phase 2 | 時点差画像による損傷進行スコア化 | 未着手 |
| Phase 3 | SCADA時系列×疲労リスク代理指標 | 未着手 |
| Phase 4 | 画像スコア×運転データの統合 | 未着手 |
| Phase 5 | OpenFAST + SHM + デジタルツイン連携 | 未着手 |

## フォルダ構成

```
blade-degradation-research/
├── docs/              # ロードマップ・データソース一覧・用語定義
├── data/
│   ├── raw/           # 原データ（Git管理外）
│   ├── processed/     # 前処理済みデータ
│   └── data_dict.md   # データ辞書
├── phase0_setup/      # 環境整備メモ
├── phase1_image_risk_score/
│   ├── notebooks/
│   ├── src/
│   ├── experiments/   # 実験ログ
│   └── reports/
├── phase2_temporal/
├── phase3_scada/
├── phase4_fusion/
└── phase5_openfast_shm/
```

## 一次データソース

- 画像: [DTU Wind Turbine Inspection Images](https://data.mendeley.com/datasets/hd96prn3nc)
- 時系列基盤: [OpenOA](https://openoa.readthedocs.io/)
- シミュレーション: [OpenFAST](https://openfast.readthedocs.io/)
- SHM: [Zenodo ブレードSHM Dataset](https://zenodo.org/records/13692213)

## 参考論文

- Energies 2019: Wind Turbine Surface Damage Detection by Deep Learning
  https://www.mdpi.com/1996-1073/12/4/676
