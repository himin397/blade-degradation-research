"""
week3_figures.py
Week 3: Phase 5b 不足図表4点の一括生成

出力:
  results/fig_del_heatmap.png         … DELマトリクス ヒートマップ（V×TI）
  results/fig_rainflow_comparison.png … Rainflow比較 棒グラフ（風速別誤差）
  results/fig_cv_boxplot.png          … CV分布 ボックスプロット（Vビン別）
  results/fig_lifetime_del_sensitivity.png … 長期DEL感度図（IECクラス×TI折れ線）
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

RESULTS = Path(__file__).parent.parent / "results"

# ==============================
# Figure 1: DELマトリクス ヒートマップ
# ==============================

def fig_del_heatmap():
    df = pd.read_csv(RESULTS / "del_matrix_ms.csv")

    V_list  = sorted(df["V"].unique())
    TI_list = sorted(df["TI"].unique())

    matrix = np.zeros((len(V_list), len(TI_list)))
    for i, v in enumerate(V_list):
        for j, ti in enumerate(TI_list):
            row = df[(df["V"] == v) & (df["TI"].round(3) == round(ti, 3))]
            matrix[i, j] = row["DEL_mean"].values[0] if len(row) else np.nan

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto", origin="lower")
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("DEL (kN-m)", fontsize=11)

    ax.set_xticks(range(len(TI_list)))
    ax.set_xticklabels([f"{int(ti*100)}%" for ti in TI_list], fontsize=10)
    ax.set_yticks(range(len(V_list)))
    ax.set_yticklabels([f"{v} m/s" for v in V_list], fontsize=10)
    ax.set_xlabel("Turbulence Intensity (TI)", fontsize=11)
    ax.set_ylabel("Wind Speed V (m/s)", fontsize=11)
    ax.set_title("DEL Matrix: DLC 1.2 (NREL 5MW, Multi-seed Mean, Standard Rainflow)\n"
                 "RootMyb1, m=10, Teq=600s", fontsize=11)

    for i in range(len(V_list)):
        for j in range(len(TI_list)):
            val = matrix[i, j]
            color = "white" if val > matrix.max() * 0.65 else "black"
            ax.text(j, i, f"{val:.0f}", ha="center", va="center",
                    fontsize=8, color=color, fontweight="bold")

    plt.tight_layout()
    out = RESULTS / "fig_del_heatmap.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"保存: {out}")


# ==============================
# Figure 2: Rainflow比較 棒グラフ
# ==============================

def fig_rainflow_comparison():
    df = pd.read_csv(RESULTS / "del_single_rainflow_comparison.csv")

    V_list = sorted(df["V"].unique())
    TI_list = sorted(df["TI"].unique())
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(TI_list)))

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: DEL絶対値比較
    ax = axes[0]
    x = np.arange(len(V_list))
    w = 0.8 / (len(TI_list) * 2 + 1)
    for j, (ti, c) in enumerate(zip(TI_list, colors)):
        sub = df[df["TI"].round(3) == round(ti, 3)].sort_values("V")
        ax.bar(x + j * w * 2,     sub["DEL_standard"].values, w * 1.8,
               color=c, label=f"Standard TI={int(ti*100)}%")
        ax.bar(x + j * w * 2 + w, sub["DEL_simple"].values,   w * 1.8,
               color=c, alpha=0.4, hatch="//")

    ax.set_xticks(x + w * len(TI_list))
    ax.set_xticklabels([f"{v} m/s" for v in V_list], fontsize=9)
    ax.set_ylabel("DEL (kN-m)", fontsize=11)
    ax.set_title("Standard vs. Simplified Rainflow: DEL Comparison\n(Solid=Standard, Hatched=Simplified)", fontsize=10)
    ax.legend(fontsize=7, loc="upper left", ncol=2)
    ax.grid(alpha=0.3, axis="y")

    # Right: 誤差率（風速ビン平均）
    ax = axes[1]
    err_by_v = df.groupby("V")["err_pct"].agg(["mean", "std"]).reset_index()
    bars = ax.bar(range(len(V_list)), err_by_v["mean"].values,
                  color="steelblue", alpha=0.8, yerr=err_by_v["std"].values,
                  capsize=4, error_kw={"elinewidth": 1.5})
    ax.axhline(y=df["err_pct"].mean(), color="tomato", ls="--", lw=2,
               label=f"Overall mean: {df['err_pct'].mean():.1f}%")
    ax.set_xticks(range(len(V_list)))
    ax.set_xticklabels([f"{v} m/s" for v in V_list], fontsize=9)
    ax.set_ylabel("Underestimation Error (%)", fontsize=11)
    ax.set_title("Simplified Rainflow Underestimation Error by Wind Speed\n"
                 "(error = (Standard - Simplified) / Standard × 100)", fontsize=10)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3, axis="y")

    for bar, val in zip(bars, err_by_v["mean"].values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=9)

    plt.suptitle("Rainflow Counting: Standard (ASTM E1049) vs. Simplified (Peak-Valley Half-Cycle)",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    out = RESULTS / "fig_rainflow_comparison.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"保存: {out}")


# ==============================
# Figure 3: CV分布 ボックスプロット
# ==============================

def fig_cv_boxplot():
    df = pd.read_csv(RESULTS / "del_matrix_ms.csv")
    V_list = sorted(df["V"].unique())

    cv_by_v = [df[df["V"] == v]["DEL_cv"].values * 100 for v in V_list]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: ボックスプロット
    ax = axes[0]
    bp = ax.boxplot(cv_by_v, patch_artist=True, notch=False,
                    medianprops={"color": "black", "lw": 2})
    colors = plt.cm.RdYlGn_r(np.linspace(0.1, 0.9, len(V_list)))
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.axhline(y=10, color="tomato", ls="--", lw=1.5, label="10% threshold")
    ax.set_xticks(range(1, len(V_list)+1))
    ax.set_xticklabels([f"{v} m/s" for v in V_list], fontsize=9)
    ax.set_ylabel("CV (%)", fontsize=11)
    ax.set_title("DEL Coefficient of Variation by Wind Speed\n(6 seeds per condition)", fontsize=11)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3, axis="y")

    # 各ボックスに中央値を表示
    for i, cvs in enumerate(cv_by_v):
        ax.text(i + 1, np.median(cvs) + 0.5, f"{np.median(cvs):.1f}%",
                ha="center", va="bottom", fontsize=8)

    # Right: CV vs V 散布図（TI別色分け）
    ax = axes[1]
    TI_list = sorted(df["TI"].unique())
    ti_colors = plt.cm.viridis(np.linspace(0, 1, len(TI_list)))
    for ti, tc in zip(TI_list, ti_colors):
        sub = df[df["TI"].round(3) == round(ti, 3)].sort_values("V")
        ax.plot(sub["V"], sub["DEL_cv"]*100, "o-", color=tc,
                label=f"TI={int(ti*100)}%", lw=1.5, ms=6)

    ax.axhline(y=10, color="tomato", ls="--", lw=1.5, label="10% threshold")
    ax.set_xlabel("Wind Speed V (m/s)", fontsize=11)
    ax.set_ylabel("CV (%)", fontsize=11)
    ax.set_title("CV by Wind Speed and TI\n(V=4 m/s: high variability due to low TSR)", fontsize=11)
    ax.legend(fontsize=8, ncol=2)
    ax.grid(alpha=0.3)

    plt.suptitle("Multi-seed DEL Variability: Coefficient of Variation (CV = std/mean)",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    out = RESULTS / "fig_cv_boxplot.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"保存: {out}")


# ==============================
# Figure 4: 長期DEL感度図
# ==============================

def fig_lifetime_del_sensitivity():
    df2 = pd.read_csv(RESULTS / "lifetime_del_stage2.csv", index_col=0)
    df3 = pd.read_csv(RESULTS / "lifetime_del_stage3.csv", index_col=0)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Stage 2 — TI固定でのWeibullクラス別長期DEL
    ax = axes[0]
    iec_classes = df2.columns.tolist()
    ti_labels   = df2.index.tolist()  # TI values as strings
    x = np.arange(len(ti_labels))
    w = 0.25
    class_colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    offsets = [-w, 0, w]

    for i, (col, color, off) in enumerate(zip(iec_classes, class_colors, offsets)):
        bars = ax.bar(x + off, df2[col].values / 1000, w * 0.9,
                      label=col, color=color, alpha=0.8)

    ax.set_xticks(x)
    ti_nums = [t.replace("TI ", "TI=").replace("%", "") for t in ti_labels] if "TI" in str(ti_labels[0]) else [f"TI={float(t)*100:.0f}%" for t in ti_labels]
    ax.set_xticklabels(ti_nums, fontsize=9, rotation=30)
    ax.set_ylabel("Lifetime DEL (MN-m)", fontsize=11)
    ax.set_title("Stage 2: Weibull-Weighted Lifetime DEL\n(Fixed TI, varying IEC Wind Class)", fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3, axis="y")
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))

    # Right: Stage 3 — V-TI joint分布（IECクラス×IEC風速クラス）
    ax = axes[1]
    iec_turb_classes = df3.index.tolist()  # IEC Class A/B/C
    iec_wind_classes = df3.columns.tolist()

    x = np.arange(len(iec_turb_classes))
    wind_colors = ["#d62728", "#ff7f0e", "#1f77b4"]  # Class I, II, III

    for i, (col, color) in enumerate(zip(iec_wind_classes, wind_colors)):
        off = (i - 1) * 0.28
        bars = ax.bar(x + off, df3[col].values / 1000, 0.25,
                      label=col, color=color, alpha=0.8)
        for bar, val in zip(bars, df3[col].values / 1000):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    f"{val:.1f}", ha="center", va="bottom", fontsize=7.5)

    ax.set_xticks(x)
    ax.set_xticklabels(iec_turb_classes, fontsize=9)
    ax.set_ylabel("Lifetime DEL (MN-m)", fontsize=11)
    ax.set_title("Stage 3: V-TI Joint Distribution Lifetime DEL\n"
                 "(IEC NTM TI model, Weibull k=2)", fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3, axis="y")

    # 参考ライン: 対象SCADAサイト推定値（IEC Class C / Class II ≈ 9.0 MN-m）
    ax.axhline(y=8.965, color="gray", ls=":", lw=1.5,
               label="Target site estimate (Class C/II)")
    ax.legend(fontsize=8)

    plt.suptitle("Lifetime DEL Sensitivity: Wind Class and Turbulence Class\n"
                 "(NREL 5MW / DLC 1.2 / Standard Rainflow / 240 cases)",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    out = RESULTS / "fig_lifetime_del_sensitivity.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"保存: {out}")


if __name__ == "__main__":
    print("=== Week 3: Phase 5b 図表生成 ===\n")
    fig_del_heatmap()
    fig_rainflow_comparison()
    fig_cv_boxplot()
    fig_lifetime_del_sensitivity()
    print("\n=== 完了 ===")
