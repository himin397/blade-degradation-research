"""
05ms_extract_del_multiseed.py
Phase 5b マルチシード + 標準Rainflow:
  1. ASTM E1049系 4点法 Rainflow（rainflow 3.2.0）でDEL算出
  2. 単一シード簡易版との誤差比較
  3. 各V-TI条件でDEL平均・標準偏差・変動係数（CV）を集計
  4. results/del_matrix_ms.csv に保存

DEL定義:
  DEL = ( Σ(n_i × ΔS_i^m) / N_eq )^(1/m)
  m=10（GFRP）, Teq=600s
"""

import numpy as np
import pandas as pd
import rainflow
from pathlib import Path

try:
    from openfast_io.FAST_output_reader import FASTOutputFile
except ImportError:
    raise ImportError("openfast_io が見つかりません。blade-phase3 環境で実行してください。")

SCRIPT_DIR  = Path(__file__).parent
CASES_MS    = SCRIPT_DIR.parent / "cases_ms"
CASES_DIR   = SCRIPT_DIR.parent / "cases"       # 単一シード結果（比較用）
RESULTS     = SCRIPT_DIR.parent / "results"
RESULTS.mkdir(exist_ok=True)

DT     = 0.00625   # s
M      = 10        # SN曲線指数（GFRP）
TEQ    = 600.0     # 等価時間 [s]
SKIP_S = 60.0      # 過渡除去

V_LIST    = [4, 6, 8, 10, 12, 14, 16, 18]
TI_LIST   = [0.08, 0.12, 0.14, 0.16, 0.20]
N_SEEDS   = 6


# ------------------------------------------------------------------ #
# DEL算出関数（標準Rainflow: ASTM E1049系 4点法）
# ------------------------------------------------------------------ #
def del_standard_rainflow(signal, m=10, dt=0.00625, Teq=600.0):
    """
    rainflow.count_cycles() を使用した ASTM E1049系 4点法 DEL算出。

    rainflow.count_cycles() はハーフサイクル・フルサイクルを正しく
    カウントし、各サイクルの range（振幅の2倍）と mean を返す。
    """
    sig = np.asarray(signal, dtype=float)

    # rainflow.count_cycles: (range, count) の反復子
    # count は 0.5（ハーフサイクル）または 1.0（フルサイクル）
    damage = 0.0
    for rng, count in rainflow.count_cycles(sig, nbins=None):
        damage += count * (rng ** m)

    T_actual = len(sig) * dt
    N_eq = Teq / T_actual  # ≈ 1.0 for 600s sim

    if N_eq <= 0 or damage <= 0:
        return 0.0
    DEL = (damage / N_eq) ** (1.0 / m)
    return float(DEL)


# ------------------------------------------------------------------ #
# 簡易版 Rainflow（単一シード比較用）
# ------------------------------------------------------------------ #
def del_simple_rainflow(signal, m=10, dt=0.00625, Teq=600.0):
    """ピーク・バレー抽出 + ハーフサイクルカウント（既存簡易版）"""
    sig = np.asarray(signal, dtype=float)
    diff = np.diff(sig)
    sign_change = np.where(np.diff(np.sign(diff)) != 0)[0] + 1
    extrema = np.concatenate([[0], sign_change, [len(sig) - 1]])
    peaks = sig[extrema]
    ranges = np.abs(np.diff(peaks))
    if len(ranges) == 0:
        return 0.0
    n_half = np.ones(len(ranges)) * 0.5
    T_actual = len(sig) * dt
    N_eq = Teq / T_actual
    damage = np.sum(n_half * (ranges ** m))
    DEL = (damage / N_eq) ** (1.0 / m)
    return float(DEL)


# ------------------------------------------------------------------ #
# 単一シード（既存）の再算出（標準Rainflowで）
# ------------------------------------------------------------------ #
print("=== Step 1: 単一シード再算出（標準Rainflow）===")
single_records = []
skip_steps = int(SKIP_S / DT)

for V in V_LIST:
    for TI in TI_LIST:
        case_tag = f"V{V:02d}_TI{int(TI * 100):03d}"
        outb_path = CASES_DIR / case_tag / "case.outb"
        if not outb_path.exists():
            continue
        try:
            df = FASTOutputFile(str(outb_path)).toDataFrame()
            col = next((c for c in df.columns if "RootMyb1" in c), None)
            if col is None:
                continue
            signal = df[col].values[skip_steps:]
            del_std  = del_standard_rainflow(signal, m=M, dt=DT, Teq=TEQ)
            del_simp = del_simple_rainflow(signal, m=M, dt=DT, Teq=TEQ)
            err_pct  = abs(del_std - del_simp) / del_std * 100 if del_std > 0 else 0
            single_records.append({
                "V": V, "TI": TI, "case_tag": case_tag,
                "DEL_standard": del_std,
                "DEL_simple":   del_simp,
                "err_pct":      err_pct,
            })
            print(f"  {case_tag}: std={del_std:.1f}  simple={del_simp:.1f}  err={err_pct:.1f}%")
        except Exception as e:
            print(f"  ERROR {case_tag}: {e}")

single_df = pd.DataFrame(single_records)
single_df.to_csv(RESULTS / "del_single_rainflow_comparison.csv", index=False)
print(f"\nRainflow比較誤差 平均={single_df['err_pct'].mean():.1f}%  最大={single_df['err_pct'].max():.1f}%")


# ------------------------------------------------------------------ #
# マルチシード DEL算出
# ------------------------------------------------------------------ #
print("\n=== Step 2: マルチシード DEL算出 ===")
ms_records = []

for V in V_LIST:
    for TI in TI_LIST:
        case_tag = f"V{V:02d}_TI{int(TI * 100):03d}"
        dels = []
        for s in range(1, N_SEEDS + 1):
            tag_full  = f"{case_tag}_S{s:02d}"
            outb_path = CASES_MS / tag_full / "case.outb"
            if not outb_path.exists():
                print(f"  SKIP (no .outb): {tag_full}")
                continue
            try:
                df = FASTOutputFile(str(outb_path)).toDataFrame()
                col = next((c for c in df.columns if "RootMyb1" in c), None)
                if col is None:
                    continue
                signal = df[col].values[skip_steps:]
                del_val = del_standard_rainflow(signal, m=M, dt=DT, Teq=TEQ)
                dels.append(del_val)
            except Exception as e:
                print(f"  ERROR {tag_full}: {e}")

        if len(dels) == 0:
            ms_records.append({
                "V": V, "TI": TI, "case_tag": case_tag,
                "DEL_mean": np.nan, "DEL_std": np.nan, "DEL_cv": np.nan,
                "n_seeds": 0,
            })
            continue

        dels_arr = np.array(dels)
        mean_del = float(dels_arr.mean())
        std_del  = float(dels_arr.std(ddof=1)) if len(dels_arr) > 1 else 0.0
        cv_del   = std_del / mean_del if mean_del > 0 else 0.0

        ms_records.append({
            "V": V, "TI": TI, "case_tag": case_tag,
            "DEL_mean": mean_del,
            "DEL_std":  std_del,
            "DEL_cv":   cv_del,
            "n_seeds":  len(dels),
        })
        print(f"  {case_tag}: mean={mean_del:.1f}  std={std_del:.1f}  CV={cv_del*100:.1f}%  (n={len(dels)})")

ms_df = pd.DataFrame(ms_records)
ms_df.to_csv(RESULTS / "del_matrix_ms.csv", index=False)

# ------------------------------------------------------------------ #
# 集計サマリー表示
# ------------------------------------------------------------------ #
print(f"\n=== DEL平均マトリクス（kN-m, マルチシード） ===")
pivot_mean = ms_df.pivot(index="V", columns="TI", values="DEL_mean")
print(pivot_mean.round(1).to_string())

print(f"\n=== DEL変動係数マトリクス（CV%） ===")
pivot_cv = ms_df.pivot(index="V", columns="TI", values="DEL_cv") * 100
print(pivot_cv.round(1).to_string())

valid = ms_df.dropna(subset=["DEL_mean"])
print(f"\n全体CV: 平均={valid['DEL_cv'].mean()*100:.1f}%  最大={valid['DEL_cv'].max()*100:.1f}%")
print(f"\nSaved: {RESULTS / 'del_matrix_ms.csv'}")
print(f"Saved: {RESULTS / 'del_single_rainflow_comparison.csv'}")
