# OpenFAST統合パイプライン設計仕様

## 目的
簡易解析モデル（phase5_load_analysis.py）で得た (V, TI) → DEL マッピングを、
OpenFASTの高精度シミュレーションで検証・較正する。

## 必要入力ファイル（参照タービン: NREL 5MW Land-Based）
```
NREL5MW/
├── NREL5MW.fst               # 主制御ファイル
├── NRELOffswtBsline5MW_Onshore_AeroDyn15.dat
├── NRELOffswtBsline5MW_BeamDyn_Blade.dat
├── NRELOffswtBsline5MW_ElastoDyn.dat
├── NRELOffswtBsline5MW_ElastoDyn_Blade.dat
├── NRELOffswtBsline5MW_ServoDyn.dat
├── wind/
│   ├── IEC_NTM_V8_TI14.bts   # TurbSim: V=8m/s, TI=14%(Class B)
│   ├── IEC_NTM_V12_TI14.bts
│   └── ...
```
取得: https://github.com/OpenFAST/r-test/tree/main/glue-codes/openfast/5MW_Land_DLL_WTurb

## TurbSim風場生成（IEC ETM）
```bash
TurbSim TurbSim_IEC_NTM.inp
```
風況クラス組み合わせ（DLC 1.2相当）:
- V = 4, 6, 8, 10, 12, 14, 16, 18 m/s
- TI = 0.08, 0.12, 0.14, 0.16, 0.20 (IEC Class C, B, A+)

## OpenFAST実行・DEL抽出（Python擬似コード）
```python
from openfast_toolbox.postpro import postProRows, DELs
import subprocess, os

for v in V_LIST:
    for ti in TI_LIST:
        # 入力ファイル修正（wind speed, TI）
        modify_inflow(v, ti)
        # 実行
        subprocess.run(['openfast', 'NREL5MW.fst'])
        # 結果読込
        result = postProRows('NREL5MW.outb')
        # DEL計算: ブレード根元フラップ方向 (RootMyb1)
        del_val = DELs(result, 'RootMyb1', m=10, Teq=600)
        del_matrix[v][ti] = del_val
```

## Phase 5本格実装の次ステップ
1. NREL 5MWリポジトリをクローン
2. TurbSimで風場生成（8×5=40ケース）
3. OpenFAST実行（各600秒シミュレーション）
4. DELマトリクス（V×TI）を抽出
5. 本スクリプトの簡易モデルと比較・較正
6. 較正済み重みでPhase 4統合スコアを更新
