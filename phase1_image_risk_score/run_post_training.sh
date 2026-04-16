#!/bin/bash
# 学習完了後の自動実行スクリプト

REPO=/Users/tsunekousei/Desktop/blade-degradation-research
PYTHON=/opt/anaconda3/envs/blade-phase1/bin/python
RESULTS=$REPO/runs/detect/phase1_image_risk_score/experiments/baseline_yolov8n/results.csv

cd $REPO

# 30エポック完了を待つ
echo "学習完了を待機中..."
while true; do
    EPOCHS=$(tail -1 $RESULTS 2>/dev/null | cut -d',' -f1)
    if [ "$EPOCHS" = "30" ]; then
        echo "30エポック完了を確認"
        break
    fi
    sleep 30
done

# W06: 評価・学習曲線
echo "=== W06: 評価スクリプト実行 ==="
$PYTHON phase1_image_risk_score/src/evaluate.py

# W07-08: 部位マッピング・リスクスコア（サンプルデータで動作確認）
echo "=== W07-08: リスクスコア動作確認 ==="
$PYTHON phase1_image_risk_score/src/region_mapper.py
$PYTHON phase1_image_risk_score/src/risk_score.py

echo "=== 完了 ==="
