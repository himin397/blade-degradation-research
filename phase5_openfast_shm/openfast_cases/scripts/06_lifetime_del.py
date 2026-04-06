"""
06_lifetime_del.py
Phase 5b 第4フェーズ: 長期DEL算出（3段階）

Stage 1: 条件別DEL統計（mean, std, CV） ← マルチシード結果から読み込み
Stage 2: Weibull風速重み付き長期DEL
Stage 3: V-TI同時分布（独立近似）による長期DEL

Weibull分布: f(V) = (k/c) × (V/c)^(k-1) × exp(-(V/c)^k)
  k=2 (形状パラメータ, IEC 61400-1 Class II参照)
  c=2/sqrt(π) × Vave （スケールパラメータ）
  Vave = 8.5 m/s (IEC Class II: Vave=8.5 m/s, Class I: 10 m/s, Class III: 7.5 m/s)

TI分布（IEC NTM 61400-1 Ed.4）:
  σ_1 = I_ref × (0.75V + b), b=5.6 m/s
  TI(V) = σ_1 / V = I_ref × (0.75 + 5.6/V)
  I_ref = 0.12 (IEC Class C), 0.14 (Class B), 0.16 (Class A)
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
RESULTS    = SCRIPT_DIR.parent / "results"
RESULTS.mkdir(exist_ok=True)

# ------------------------------------------------------------------ #
# データ読み込み
# ------------------------------------------------------------------ #
ms_csv = RESULTS / "del_matrix_ms.csv"
if not ms_csv.exists():
    raise FileNotFoundError(f"{ms_csv} が見つかりません。05ms_extract_del_multiseed.py を先に実行してください。")

ms_df = pd.read_csv(ms_csv)
print(f"Loaded multi-seed DEL matrix: {len(ms_df)} conditions")

V_BINS  = np.array([4, 6, 8, 10, 12, 14, 16, 18], dtype=float)
TI_BINS = np.array([0.08, 0.12, 0.14, 0.16, 0.20])

M = 10  # SN曲線指数


# ------------------------------------------------------------------ #
# Stage 1: 条件別DEL統計サマリー（マルチシード）
# ------------------------------------------------------------------ #
print("\n=== Stage 1: 条件別DEL統計 ===")
pivot_mean = ms_df.pivot(index="V", columns="TI", values="DEL_mean")
pivot_cv   = ms_df.pivot(index="V", columns="TI", values="DEL_cv") * 100

print("DEL平均（kN-m）:")
print(pivot_mean.round(1).to_string())
print("\nDEL変動係数（CV%）:")
print(pivot_cv.round(1).to_string())

valid = ms_df.dropna(subset=["DEL_mean"])
print(f"\nCV統計: 平均={valid['DEL_cv'].mean()*100:.1f}%  最大={valid['DEL_cv'].max()*100:.1f}%  中央値={valid['DEL_cv'].median()*100:.1f}%")


# ------------------------------------------------------------------ #
# Stage 2: Weibull風速重み付き長期DEL
# ------------------------------------------------------------------ #
print("\n=== Stage 2: Weibull重み付き長期DEL ===")


def weibull_pdf(V, k, c):
    """Weibull確率密度関数"""
    return (k / c) * (V / c) ** (k - 1) * np.exp(-(V / c) ** k)


def weibull_c_from_vave(Vave, k=2):
    """Vave（年平均風速）からスケールパラメータcを計算"""
    from scipy.special import gamma
    return Vave / gamma(1 + 1 / k)


def lifetime_del_weibull(del_means, V_bins, Vave=8.5, k=2, m=10, V_min=0, V_max=25):
    """
    Weibull分布で重み付けした長期DEL算出。

    del_means: 各V_binでのDEL平均（TI代表値で評価）[kN-m]
    V_bins: 風速ビン中心値 [m/s]
    """
    c = weibull_c_from_vave(Vave, k)

    # 各ビンの確率質量（ビン幅=2 m/s で近似）
    bin_width = np.diff(np.concatenate([[V_min], V_bins, [V_max]]))
    bin_width = np.array([2.0] * len(V_bins))  # 全ビン等幅2m/s

    # ビン中心のWeibull PDF
    weights = np.array([weibull_pdf(V, k, c) * bw for V, bw in zip(V_bins, bin_width)])
    weights = weights / weights.sum()  # 正規化

    # DELが存在するビンのみ使用
    valid_mask = ~np.isnan(del_means)
    if not valid_mask.any():
        return np.nan

    # 長期DEL = (Σ w_i × DEL_i^m)^(1/m)
    del_arr = np.where(valid_mask, del_means, 0.0)
    lifetime = (np.sum(weights * (del_arr ** m))) ** (1.0 / m)
    return float(lifetime)


# Vaveの設定（IEC クラス別・サイト依存性確認用）
Vave_scenarios = {
    "IEC Class I (Vave=10.0)": 10.0,
    "IEC Class II (Vave=8.5)": 8.5,
    "IEC Class III (Vave=7.5)": 7.5,
}

# 各TIビン別に長期DELを算出
results_stage2 = {}
for TI in TI_BINS:
    ti_data = ms_df[ms_df["TI"] == TI].set_index("V")
    del_means = np.array([ti_data.loc[V, "DEL_mean"] if V in ti_data.index else np.nan for V in V_BINS])
    results_stage2[TI] = {}
    for scenario, Vave in Vave_scenarios.items():
        lt_del = lifetime_del_weibull(del_means, V_BINS, Vave=Vave, k=2, m=M)
        results_stage2[TI][scenario] = lt_del

# TI代表値（IEC NTMの期待値）で統合した長期DEL
print("\n各TIビン × Vaveシナリオ別 長期DEL（kN-m）:")
stage2_df = pd.DataFrame(results_stage2).T
stage2_df.index.name = "TI"
print(stage2_df.round(1).to_string())


# ------------------------------------------------------------------ #
# Stage 3: V-TI同時分布（独立近似）
# ------------------------------------------------------------------ #
print("\n=== Stage 3: V-TI同時分布による長期DEL（独立近似）===")


def iec_ti_from_v(V, I_ref=0.12):
    """IEC 61400-1 Ed.4 NTM: TI(V) = I_ref × (0.75 + 5.6/V)"""
    return I_ref * (0.75 + 5.6 / np.maximum(V, 0.1))


def lifetime_del_joint(ms_df, V_bins, TI_bins, Vave=8.5, k=2, I_ref=0.12, m=10):
    """
    V-TI独立近似の同時分布による長期DEL。

    P(V, TI) ≈ P(V) × δ(TI - TI_NTM(V))
    つまり各Vビンで代表TI（IEC NTM）を使用。
    """
    c = weibull_c_from_vave(Vave, k)

    damage_sum = 0.0
    weight_sum = 0.0
    for V in V_bins:
        # Weibull重み
        w_V = weibull_pdf(V, k, c) * 2.0  # ビン幅2 m/s

        # そのVでのIEC NTM代表TI
        ti_rep = iec_ti_from_v(V, I_ref)

        # DEL補間（TIビン間で線形補間）
        ti_data = ms_df[ms_df["V"] == V].set_index("TI")
        ti_vals = np.array([ti_data.loc[TI, "DEL_mean"]
                            if TI in ti_data.index and not np.isnan(ti_data.loc[TI, "DEL_mean"])
                            else np.nan for TI in TI_bins])
        valid_ti = TI_bins[~np.isnan(ti_vals)]
        valid_del = ti_vals[~np.isnan(ti_vals)]

        if len(valid_ti) < 2:
            continue

        del_rep = np.interp(ti_rep, valid_ti, valid_del,
                            left=valid_del[0], right=valid_del[-1])

        damage_sum += w_V * (del_rep ** m)
        weight_sum += w_V

    if weight_sum <= 0:
        return np.nan
    lifetime = (damage_sum / weight_sum) ** (1.0 / m)
    return float(lifetime)


print("\nV-TI同時分布（独立近似）長期DEL（kN-m）:")
joint_results = {}
for I_ref_label, I_ref in [("IEC Class C (I_ref=0.12)", 0.12),
                             ("IEC Class B (I_ref=0.14)", 0.14),
                             ("IEC Class A (I_ref=0.16)", 0.16)]:
    row = {}
    for scenario, Vave in Vave_scenarios.items():
        lt_del = lifetime_del_joint(ms_df, V_BINS, TI_BINS, Vave=Vave, k=2, I_ref=I_ref, m=M)
        row[scenario] = lt_del
    joint_results[I_ref_label] = row
    print(f"  {I_ref_label}: {row}")

joint_df = pd.DataFrame(joint_results).T
joint_df.index.name = "IEC_class"
print("\n")
print(joint_df.round(1).to_string())


# ------------------------------------------------------------------ #
# 可視化
# ------------------------------------------------------------------ #
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Panel 1: DEL平均マトリクス（ヒートマップ）
ax = axes[0]
data = pivot_mean.values
im = ax.imshow(data, cmap="YlOrRd", aspect="auto")
ax.set_xticks(range(len(TI_BINS)))
ax.set_xticklabels([f"{int(ti*100)}%" for ti in TI_BINS])
ax.set_yticks(range(len(V_BINS)))
ax.set_yticklabels([f"{int(v)}" for v in V_BINS])
ax.set_xlabel("TI")
ax.set_ylabel("V (m/s)")
ax.set_title("DEL Mean (kN-m)")
plt.colorbar(im, ax=ax)
for i in range(len(V_BINS)):
    for j in range(len(TI_BINS)):
        val = data[i, j] if not np.isnan(data[i, j]) else 0
        ax.text(j, i, f"{val:.0f}", ha='center', va='center', fontsize=7,
                color='white' if val > data[~np.isnan(data)].max() * 0.6 else 'black')

# Panel 2: CV%マトリクス
ax = axes[1]
data_cv = pivot_cv.values
im2 = ax.imshow(data_cv, cmap="Blues", aspect="auto", vmin=0, vmax=20)
ax.set_xticks(range(len(TI_BINS)))
ax.set_xticklabels([f"{int(ti*100)}%" for ti in TI_BINS])
ax.set_yticks(range(len(V_BINS)))
ax.set_yticklabels([f"{int(v)}" for v in V_BINS])
ax.set_xlabel("TI")
ax.set_ylabel("V (m/s)")
ax.set_title("DEL CV (%) - Seed Variability")
plt.colorbar(im2, ax=ax)
for i in range(len(V_BINS)):
    for j in range(len(TI_BINS)):
        val = data_cv[i, j] if not np.isnan(data_cv[i, j]) else 0
        ax.text(j, i, f"{val:.1f}", ha='center', va='center', fontsize=7)

# Panel 3: Weibull重み付き長期DEL（Vaveシナリオ比較）
ax = axes[2]
x = np.arange(len(Vave_scenarios))
width = 0.15
ti_labels = [f"TI={int(ti*100)}%" for ti in TI_BINS]
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
for idx, TI in enumerate(TI_BINS):
    vals = [results_stage2[TI][sc] for sc in Vave_scenarios]
    ax.bar(x + idx * width, vals, width, label=ti_labels[idx], color=colors[idx])
ax.set_xticks(x + width * 2)
ax.set_xticklabels(list(Vave_scenarios.keys()), fontsize=8, rotation=10)
ax.set_ylabel("Lifetime DEL (kN-m)")
ax.set_title("Weibull-weighted Lifetime DEL")
ax.legend(fontsize=7)
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
out_png = RESULTS / "lifetime_del_analysis.png"
fig.savefig(out_png, dpi=150, bbox_inches="tight")
print(f"\nSaved: {out_png}")

# CSV保存
stage2_df.to_csv(RESULTS / "lifetime_del_stage2.csv")
joint_df.to_csv(RESULTS / "lifetime_del_stage3.csv")
print(f"Saved: {RESULTS / 'lifetime_del_stage2.csv'}")
print(f"Saved: {RESULTS / 'lifetime_del_stage3.csv'}")
print("\n=== 長期DEL算出完了 ===")
