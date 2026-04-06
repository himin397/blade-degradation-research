"""
mm82_05_extract_del.py
Phase I MM82: DEL 抽出 → del_matrix_mm82.csv

ASTM E1049 準拠 rainflow (標準 4 点法) で RootMyb1 DEL を算出。
マルチシード平均・標準偏差・変動係数を集計する。

出力: results/del_matrix_mm82.csv
  V, TI, case_tag, DEL_mean, DEL_std, DEL_cv, n_seeds
"""

import numpy as np
import pandas as pd
import rainflow
from pathlib import Path

try:
    from openfast_io.FAST_output_reader import FASTOutputFile
except ImportError:
    raise ImportError("openfast_io が見つかりません。blade-phase3 環境で実行してください。")

SCRIPT_DIR = Path(__file__).parent
BASE_DIR   = SCRIPT_DIR.parent
CASES_MM82 = BASE_DIR / "cases_mm82"
RESULTS    = BASE_DIR / "results"
RESULTS.mkdir(exist_ok=True)

DT     = 0.00625   # s (OpenFAST デフォルト dt)
M      = 10        # SN 曲線指数 (GFRP)
TEQ    = 600.0     # 等価時間 [s]
SKIP_S = 60.0      # 過渡除去秒数

V_LIST   = [4, 6, 8, 10, 12, 14, 16, 18]
TI_LIST  = [0.08, 0.12, 0.14, 0.16, 0.20]
N_SEEDS  = 6


def del_standard_rainflow(signal, m=10, dt=0.00625, Teq=600.0):
    """ASTM E1049 系 4 点法 rainflow DEL 算出"""
    sig = np.asarray(signal, dtype=float)
    damage = 0.0
    for rng, count in rainflow.count_cycles(sig, nbins=None):
        damage += count * (rng ** m)
    T_actual = len(sig) * dt
    N_eq     = Teq / T_actual
    if N_eq <= 0 or damage <= 0:
        return 0.0
    return float((damage / N_eq) ** (1.0 / m))


# ─────────────────────────────────────────────────────────────────────────────
print("=== Phase I MM82: DEL 抽出 ===")

skip_steps = int(SKIP_S / DT)
records    = []
missing    = 0

for V in V_LIST:
    for TI in TI_LIST:
        case_tag = f"V{V:02d}_TI{int(TI * 100):03d}"
        dels = []

        for s in range(1, N_SEEDS + 1):
            tag_full  = f"{case_tag}_S{s:02d}"
            outb_path = CASES_MM82 / tag_full / "case.outb"

            if not outb_path.exists():
                missing += 1
                continue

            try:
                df  = FASTOutputFile(str(outb_path)).toDataFrame()
                col = next((c for c in df.columns if "RootMyb1" in c), None)
                if col is None:
                    print(f"  WARNING: RootMyb1 列なし: {tag_full}")
                    continue
                signal  = df[col].values[skip_steps:]
                del_val = del_standard_rainflow(signal, m=M, dt=DT, Teq=TEQ)
                dels.append(del_val)
            except Exception as e:
                print(f"  ERROR {tag_full}: {e}")

        if not dels:
            records.append({
                "V": V, "TI": TI, "case_tag": case_tag,
                "DEL_mean": np.nan, "DEL_std": np.nan, "DEL_cv": np.nan, "n_seeds": 0,
            })
            continue

        arr      = np.array(dels)
        mean_del = float(arr.mean())
        std_del  = float(arr.std(ddof=1)) if len(arr) > 1 else 0.0
        cv_del   = std_del / mean_del if mean_del > 0 else 0.0

        records.append({
            "V": V, "TI": TI, "case_tag": case_tag,
            "DEL_mean": mean_del, "DEL_std": std_del, "DEL_cv": cv_del, "n_seeds": len(dels),
        })
        print(f"  {case_tag}: mean={mean_del:.1f}  std={std_del:.1f}  CV={cv_del*100:.1f}%  (n={len(dels)})")

# ─────────────────────────────────────────────────────────────────────────────
# 出力
out_path = RESULTS / "del_matrix_mm82.csv"
df = pd.DataFrame(records)
df.to_csv(out_path, index=False)

valid = df.dropna(subset=["DEL_mean"])
print(f"\n=== 集計 ===")
print(f"有効ケース: {len(valid)}/{len(records)}  .outb 欠落: {missing}")
if len(valid) > 0:
    print(f"DEL 範囲: {valid['DEL_mean'].min():.1f} 〜 {valid['DEL_mean'].max():.1f} kN·m")
    print(f"CV 平均: {valid['DEL_cv'].mean()*100:.1f}%")

# ── 平均 DEL マトリクス表示 ──────────────────────────────────────────────────
print("\n=== DEL 平均マトリクス (kN-m, MM82 プロキシ) ===")
pivot = df.pivot(index="V", columns="TI", values="DEL_mean")
print(pivot.round(1).to_string())

print(f"\n保存: {out_path}")
