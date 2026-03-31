# 実験ログ - Phase 1

## テンプレート

```
## 実験ID: EXP-001
- 日付: YYYY-MM-DD
- フェーズ: Phase 1
- 最終目標との接続: 画像由来損傷定量化（部品#1）
- 研究練習用 / 本命接続: 両方
- 目的:
- データ:
  - 種別: 一次 / 二次（原典：〇〇）
  - バージョン・取得日:
- 手法・設定:
  - モデル:
  - ハイパーパラメータ:
  - 分割方法:
- 結果:
  - 主要指標（mAP等）:
  - 補足:
- 考察:
  - うまくいったこと:
  - うまくいかなかったこと:
  - 仮説（仮説止まりを明示）:
- 次のアクション:
- 参照論文・URL（DOI付き）:
```

---

## W04 アノテーション調査メモ（2026-04-01）

### 判明した事実

**アノテーション形式**: COCO JSON（`bbox: [x_min, y_min, width, height]`）

**クラス定義（5クラス）**:

| COCO category_id | YOLO class_id | 名称 | 意味 |
|---|---|---|---|
| 0 | 0 | VG;MT | Vortex Generator Missing Teeth |
| 1 | 1 | LE;ER | Leading Edge Erosion ← 本研究の主要対象 |
| 2 | 2 | LR;DA | Lightning Receptor Damage |
| 3 | 3 | LE;CR | Leading Edge Crack |
| 4 | 4 | SF;PO | Surface Pockmark / Other |

**split構成（元画像ベース）**:
- train: 212枚、val: 44枚、test: 45枚（合計301枚）
- データリーク確認: splitをまたぐ元画像なし ✅
- 比率: 約70:15:15（Gohar et al. 2023に準拠）

**重要な気づき**:
- 元画像（5280×2970px）とアノテーション（1024×1024pxパッチ基準）の解像度が異なる
- YOLOv8学習前に `slice_images.py` でパッチ生成が必要
- アノテーションは Energies 2019（Shihavuddin）とは別の研究者（Gohar et al. 2023）が作成

**引用すべき文献**（アノテーション使用時）:
- Gohar et al. (2023), Machines, 11(10), 953. DOI: 10.3390/machines11100953

### 次のステップ（W05）
1. `slice_images.py` で元画像を1024pxパッチに変換
2. `coco_to_yolo.py` でアノテーションをYOLO形式に変換
3. YOLOv8でベースライン学習

---

## 実験記録

（最初の実験後にここに追記する）
