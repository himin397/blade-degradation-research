
# ベースライン学習結果サマリー

## 学習設定
- モデル: YOLOv8n（nanoサイズ）
- データ: DTU Wind Turbine Inspection Images
  - 一次ソース: DOI 10.17632/hd96prn3nc.2
  - アノテーション: github.com/imadgohar/DTU-annotations (Gohar et al. 2023)
- エポック数: 30
- クラス数: 5 (VG;MT, LE;ER, LR;DA, LE;CR, SF;PO)
- 入力サイズ: 640px
- デバイス: MPS（Apple Silicon GPU）

## 最終エポック結果
- mAP@0.5:       0.3362
- mAP@0.5:0.95:  0.1616
- Precision:     0.7529
- Recall:        0.2836

## ベスト結果
- 最良mAP@0.5: 0.3476（エポック28）

## 先行研究との比較
| 手法 | mAP@0.5 | 備考 |
|---|---|---|
| 本研究（YOLOv8n ベースライン） | 0.3476 | 30エポック・640px |
| Shihavuddin et al. 2019 | 0.8110 | Faster R-CNN + Inception-ResNet-V2 |

## 考察
（学習完了後に記入）

## 次のアクション（W07）
- 部位定義の設計（Leading Edge / Trailing Edge / 翼根 / 翼端）
- バウンディングボックス × 部位マッピングの実装
