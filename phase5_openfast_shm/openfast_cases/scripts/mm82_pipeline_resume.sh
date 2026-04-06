#!/bin/bash
# mm82_pipeline_resume.sh
# Phase I MM82 パイプライン再開スクリプト
# TurbSim/OpenFAST が途中停止した場合に再実行する

REPO=/Users/tsunekousei/Desktop/blade-degradation-research
SCRIPTS=$REPO/phase5_openfast_shm/openfast_cases/scripts

echo "=== MM82 Pipeline Status ==="
echo "BTS non-zero: $(ls -la $REPO/phase5_openfast_shm/openfast_cases/wind_mm82/*.bts 2>/dev/null | awk '$5 > 0' | wc -l) / 240"
echo "OpenFAST .outb: $(ls $REPO/phase5_openfast_shm/openfast_cases/cases_mm82/*/case.outb 2>/dev/null | wc -l) / 240"
echo ""

# Step 1: TurbSim 残りを実行（未完了のみスキップ）
echo "Step 1: TurbSim ..."
conda run -n blade-phase3 python $SCRIPTS/mm82_02_run_turbsim.py

# Step 2: OpenFAST 残りを実行（BTS があるケースのみ）
echo "Step 2: OpenFAST ..."
conda run -n blade-phase3 python $SCRIPTS/mm82_04_run_openfast.py

# Step 3: DEL 抽出
echo "Step 3: DEL 抽出 ..."
conda run -n blade-phase3 python $SCRIPTS/mm82_05_extract_del.py

echo "=== 完了 ==="
