"""
dlc13_05_compare_del.py
Phase 6: DLC 1.3 DEL算出 + DLC 1.2との比較

- DLC 1.3のDEL平均（6シード）を算出
- DLC 1.2のDEL平均（del_matrix_ms.csv）と比較
- DLC 1.3 / DLC 1.2 比率を出力
- 可視化: del_comparison_dlc12_vs_dlc13.png
"""
import numpy as np
import pandas as pd
import rainflow
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

try:
    from openfast_io.FAST_output_reader import FASTOutputFile
except ImportError:
    raise ImportError("blade-phase3 環境で実行してください。")

SCRIPT_DIR  = Path(__file__).parent
CASES_DLC13 = SCRIPT_DIR.parent / "cases_dlc13"
RESULTS     = SCRIPT_DIR.parent / "results"

DT     = 0.00625
M      = 10
TEQ    = 600.0
SKIP_S = 60.0
N_SEEDS = 6

V_LIST = [4, 6, 8, 10, 12, 14, 16, 18]


def del_standard_rainflow(signal, m=10, dt=0.00625, Teq=600.0):
    sig = np.asarray(signal, dtype=float)
    damage = 0.0
    for rng, count in rainflow.count_cycles(sig, nbins=None):
        damage += count * (rng ** m)
    T_actual = len(sig) * dt
    N_eq = Teq / T_actual
    if N_eq <= 0 or damage <= 0:
        return 0.0
    return float((damage / N_eq) ** (1.0 / m))


# DLC 1.3 DEL算出
print("=== DLC 1.3 DEL算出 ===")
skip_steps = int(SKIP_S / DT)
dlc13_records = []

for V in V_LIST:
    dels = []
    for s in range(1, N_SEEDS + 1):
        tag_full  = f"V{V:02d}_S{s:02d}"
        outb_path = CASES_DLC13 / tag_full / "case.outb"
        if not outb_path.exists():
            continue
        try:
            df = FASTOutputFile(str(outb_path)).toDataFrame()
            col = next((c for c in df.columns if "RootMyb1" in c), None)
            if col is None:
                continue
            signal  = df[col].values[skip_steps:]
            del_val = del_standard_rainflow(signal, m=M, dt=DT, Teq=TEQ)
            dels.append(del_val)
        except Exception as e:
            print(f"  ERROR {tag_full}: {e}")

    if dels:
        mean_del = float(np.mean(dels))
        std_del  = float(np.std(dels, ddof=1)) if len(dels) > 1 else 0.0
        cv_del   = std_del / mean_del if mean_del > 0 else 0.0
        print(f"  V{V:02d}: mean={mean_del:.1f}  std={std_del:.1f}  CV={cv_del*100:.1f}%  (n={len(dels)})")
        dlc13_records.append({"V": V, "DEL_dlc13_mean": mean_del, "DEL_dlc13_std": std_del,
                               "DEL_dlc13_cv": cv_del, "n_seeds": len(dels)})
    else:
        dlc13_records.append({"V": V, "DEL_dlc13_mean": np.nan, "DEL_dlc13_std": np.nan,
                               "DEL_dlc13_cv": np.nan, "n_seeds": 0})

dlc13_df = pd.DataFrame(dlc13_records)

# DLC 1.2 代表値（TI=14%: IEC Class B代表）との比較
ms_df = pd.read_csv(RESULTS / "del_matrix_ms.csv")
dlc12_rep = ms_df[ms_df["TI"] == 0.14][["V", "DEL_mean"]].rename(columns={"DEL_mean": "DEL_dlc12_ti14"})
dlc12_rep_low = ms_df[ms_df["TI"] == 0.08][["V", "DEL_mean"]].rename(columns={"DEL_mean": "DEL_dlc12_ti08"})

compare = dlc13_df.merge(dlc12_rep, on="V").merge(dlc12_rep_low, on="V")
compare["ratio_vs_ti14"] = compare["DEL_dlc13_mean"] / compare["DEL_dlc12_ti14"]
compare["ratio_vs_ti08"] = compare["DEL_dlc13_mean"] / compare["DEL_dlc12_ti08"]

print("\n=== DLC 1.3 vs DLC 1.2 比較 ===")
print("V    DLC1.3   DLC1.2(TI14%)  Ratio  DLC1.2(TI8%)  Ratio")
for _, row in compare.iterrows():
    print(f"V{int(row.V):02d}: {row.DEL_dlc13_mean:8.1f}  {row.DEL_dlc12_ti14:8.1f}  "
          f"  x{row.ratio_vs_ti14:.2f}  {row.DEL_dlc12_ti08:8.1f}  x{row.ratio_vs_ti08:.2f}")

# CSV保存
compare.to_csv(RESULTS / "del_comparison_dlc12_vs_dlc13.csv", index=False)

# 可視化
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

ax = axes[0]
ax.plot(compare["V"], compare["DEL_dlc13_mean"], "o-", color="#d62728", lw=2, ms=8, label="DLC 1.3 (ETM)")
ax.fill_between(compare["V"],
                compare["DEL_dlc13_mean"] - compare["DEL_dlc13_std"],
                compare["DEL_dlc13_mean"] + compare["DEL_dlc13_std"],
                alpha=0.2, color="#d62728")
ax.plot(compare["V"], compare["DEL_dlc12_ti14"], "s--", color="#ff7f0e", lw=2, ms=7, label="DLC 1.2 (NTM, TI=14%)")
ax.plot(compare["V"], compare["DEL_dlc12_ti08"], "^--", color="#1f77b4", lw=2, ms=7, label="DLC 1.2 (NTM, TI=8%)")
ax.set_xlabel("V (m/s)", fontsize=11)
ax.set_ylabel("DEL (kN-m)", fontsize=11)
ax.set_title("DLC 1.3 (ETM) vs DLC 1.2 (NTM): DEL Comparison", fontsize=11)
ax.legend(fontsize=9)
ax.grid(alpha=0.3)

ax = axes[1]
ax.bar(compare["V"] - 0.3, compare["ratio_vs_ti14"], 0.6,
       label="DLC1.3 / DLC1.2(TI=14%)", color="#d62728", alpha=0.7)
ax.bar(compare["V"] + 0.3, compare["ratio_vs_ti08"], 0.6,
       label="DLC1.3 / DLC1.2(TI=8%)", color="#ff7f0e", alpha=0.7)
ax.axhline(1.0, color="k", lw=1.5, ls="--")
ax.set_xlabel("V (m/s)", fontsize=11)
ax.set_ylabel("Ratio (DLC1.3 / DLC1.2)", fontsize=11)
ax.set_title("DEL Ratio: ETM / NTM", fontsize=11)
ax.legend(fontsize=9)
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
out = RESULTS / "del_comparison_dlc12_vs_dlc13.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"\nSaved: {out}")
print(f"Saved: {RESULTS / 'del_comparison_dlc12_vs_dlc13.csv'}")
print("\n=== DLC 1.3 解析完了 ===")
