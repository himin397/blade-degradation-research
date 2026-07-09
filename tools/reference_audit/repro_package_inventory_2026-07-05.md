# Paper 1 再現パッケージ棚卸し（2026-07-05）

Paper 1 §7 Reproducibility が「supplementary として含む」と主張する項目を、リポジトリ実体と照合した記録。実施者: Claude Code。

## 照合結果

| §7 の主張 | 実体 | 判定 |
|---|---|---|
| Dataset（公開 DOI + Gohar アノテーション） | data/raw・data/processed/yolo_dataset、DOI 10.17632/hd96prn3nc.2 | ✅ |
| Code: 前処理 | preprocess.py（分割 seed=42）・coco_to_yolo.py・slice_images.py・pyramid_augment.py | ✅ |
| Code: 学習 | **専用スクリプトなし**（ultralytics API/CLI 実行、完全な設定は各実験の args.yaml に保存） | ⚠️ §7 の記述を実態に合わせて修正済み（v9.9） |
| Code: 評価 | evaluate.py・eval_test_per_class.py・week1_analysis.py | ✅ |
| Code: 図生成 | generate_paper_figures.py | ✅ |
| Configuration | experiments/exp001〜004 の args.yaml（4実験とも存在。epochs=30, batch=8, imgsz=640, **学習 seed=0**） | ✅（§7 の「seed=42」は分割シードのみだったため、学習 seed=0 と分割 seed=42 を区別する記述に修正済み） |
| Trained weights | exp001/exp002 の best.pt・last.pt（2026-04-13 付、exp003/004 も存在） | ✅ |
| Risk scoring | risk_score.py | ✅ |
| requirements | requirements_phase1.txt（torch==2.11.0、**ultralytics==8.4.33** 等ピン止め済み） | ✅ |

## 発見した誤記と修正（Paper 1 v9.9 で適用）

1. **§3.3「ultralytics==8.3.x」は誤り → 8.4.33 に修正**
   - 根拠: (a) requirements_phase1.txt の git 履歴——2026-04-01 時点（f2abb07）では ultralytics のピンなし、学習（重み日付 2026-04-13）の3日後 2026-04-16（9552757）のフリーズで 8.4.33。(b) 現環境（8.4.33）での test 再評価が公表値と完全一致（mAP@0.5 0.560519、per-class 全一致）＝同一バージョン系での再現性の傍証
2. **§7「random seed (seed=42)」の精密化**: 42 は分割シード（preprocess.py）、学習シードは 0（args.yaml）。両方を明記する記述に修正
3. **§7「training scripts」の実態整合**: 学習専用スクリプトは存在しないため、「学習は ultralytics API/CLI で実行し、完全な設定は args.yaml に保存」と正確化

## 残る改善候補（任意・卒論提出/投稿前）

- 学習再現用の1行コマンド（`yolo train model=yolov8n.pt data=... epochs=30 ...` 相当）を README または §7 に記載すると再現手順が完全になる（args.yaml から復元可能なため必須ではない）
- data/processed は生成物なので、公開パッケージ化の際は「raw + 生成スクリプト」か「processed 同梱」かの方針決定が要る（himinさん 判断事項）
