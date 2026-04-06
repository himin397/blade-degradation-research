#!/bin/bash
# mm82_auto_finish.sh
# .outb が 240 本揃ったら DEL 抽出 → penmanshiel 再実行

REPO=/Users/tsunekousei/Desktop/blade-degradation-research
SCRIPTS=$REPO/phase5_openfast_shm/openfast_cases/scripts
CASES=$REPO/phase5_openfast_shm/openfast_cases/cases_mm82

echo "[auto_finish] 監視開始: $(date)"

# 240本揃うまで60秒ごとにポーリング
# mm82_04 が終了していたら都度再起動（TurbSim が BTS を追加生成するため）
while true; do
    n=$(ls $CASES/*/case.outb 2>/dev/null | wc -l | tr -d ' ')
    bts=$(ls -la $REPO/phase5_openfast_shm/openfast_cases/wind_mm82/*.bts 2>/dev/null | awk '$5 > 0' | wc -l | tr -d ' ')
    echo "[auto_finish] $(date '+%H:%M:%S')  .outb: $n / 240  BTS: $bts / 240"
    if [ "$n" -ge 240 ]; then
        echo "[auto_finish] 240ケース完了確認"
        break
    fi
    # mm82_04 が動いていなければ再起動
    if ! pgrep -f "mm82_04_run_openfast.py" > /dev/null 2>&1; then
        echo "[auto_finish] mm82_04 が停止中 → 再起動"
        conda run -n blade-phase3 python $SCRIPTS/mm82_04_run_openfast.py &
        sleep 10
    fi
    sleep 60
done

# Step 3: DEL 抽出
echo ""
echo "=== Step 3: DEL 抽出 ==="
conda run -n blade-phase3 python $SCRIPTS/mm82_05_extract_del.py
echo "DEL 抽出完了: $(date)"

# Step 4: Penmanshiel 再実行
echo ""
echo "=== Step 4: phase3_penmanshiel.py ==="
conda run -n blade-phase3 python $REPO/phase3_scada/phase3_penmanshiel.py
echo "Penmanshiel 完了: $(date)"

echo ""
echo "=== 全工程完了: $(date) ==="
