"""Paper 2 用追加図表生成スクリプト"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
from pathlib import Path

RESULTS = Path(__file__).parent.parent / "results"
SCADA_DIR = Path(__file__).parent.parent.parent.parent / "phase3_scada"
OUT = RESULTS  # 出力先

# ── 1. MM82 DEL Heatmap ──────────────────────────────────
def fig_mm82_heatmap():
    df = pd.read_csv(RESULTS / "del_matrix_mm82.csv")
    pivot = df.pivot_table(index="V", columns="TI", values="DEL_mean")

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(pivot.values, aspect="auto", origin="lower", cmap="YlOrRd")

    # Axis labels
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([f"{t:.0%}" for t in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([f"{v}" for v in pivot.index])
    ax.set_xlabel("Turbulence Intensity (TI)")
    ax.set_ylabel("Wind Speed V (m/s)")
    ax.set_title("MM82 Proxy — Blade Root Flapwise DEL (kN·m)\nDLC 1.2, 240 cases, ASTM E1049 Rainflow")

    # Value annotations
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            color = "white" if val > pivot.values.max() * 0.6 else "black"
            ax.text(j, i, f"{val:.0f}", ha="center", va="center", fontsize=9, color=color)

    cbar = fig.colorbar(im, ax=ax, label="DEL (kN·m)")
    fig.tight_layout()
    fig.savefig(OUT / "fig_del_heatmap_mm82.png", dpi=200)
    plt.close()
    print(f"Saved: {OUT / 'fig_del_heatmap_mm82.png'}")

# ── 2. Penmanshiel Monthly DEL (MM82 basis) ─────────────
def fig_penmanshiel_monthly_mm82():
    df = pd.read_csv(SCADA_DIR / "penmanshiel_monthly_del_v2.csv")  # v10.0: per-record interpolation
    # Filter to main turbines (full year 2020 data)
    main_turbines = ["T01", "T02", "T04", "T05", "T06"]
    df = df[df["turbine_id"].isin(main_turbines)]

    # Monthly average across turbines
    monthly = df.groupby("month")["DEL_est_kNm"].agg(["mean", "std"]).reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    bars = ax.bar(monthly["month"], monthly["mean"],
                  yerr=monthly["std"], capsize=3,
                  color="#2196F3", alpha=0.85, edgecolor="white")

    # Highlight peak month
    peak_idx = monthly["mean"].idxmax()
    bars[peak_idx].set_color("#F44336")

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(months)
    ax.set_ylabel("Estimated DEL (kN·m)")
    ax.set_title("Penmanshiel Wind Farm — Monthly Mean DEL (MM82 Proxy, per-record interpolation)\n5 Turbines (T01-T06), 2020, Error bars = inter-turbine σ")
    ax.set_ylim(0, ax.get_ylim()[1] * 1.15)

    # Add value labels
    for bar, val in zip(bars, monthly["mean"]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                f"{val:.0f}", ha="center", va="bottom", fontsize=8)

    fig.tight_layout()
    fig.savefig(OUT / "fig_penmanshiel_monthly_del_mm82.png", dpi=200)
    plt.close()
    print(f"Saved: {OUT / 'fig_penmanshiel_monthly_del_mm82.png'}")

# ── 3. NREL 5MW vs MM82 DEL Scaling Comparison ──────────
def fig_scaling_comparison():
    df_nrel = pd.read_csv(RESULTS / "del_matrix_ms_extended.csv")
    df_mm82 = pd.read_csv(RESULTS / "del_matrix_mm82.csv")

    # Merge on V, TI
    merged = df_nrel.merge(df_mm82, on=["V", "TI"], suffixes=("_nrel", "_mm82"))
    merged["ratio"] = merged["DEL_mean_mm82"] / merged["DEL_mean_nrel"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Panel (a): DEL scatter
    for ti, grp in merged.groupby("TI"):
        ax1.scatter(grp["DEL_mean_nrel"], grp["DEL_mean_mm82"],
                   label=f"TI={ti:.0%}", s=40, alpha=0.8)

    # Reference line: theoretical ratio 0.276
    x_range = np.array([0, merged["DEL_mean_nrel"].max() * 1.1])
    ax1.plot(x_range, x_range * 0.276, "k--", alpha=0.5, label="Theoretical (R³ = 0.276)")
    ax1.set_xlabel("NREL 5MW DEL (kN·m)")
    ax1.set_ylabel("MM82 Proxy DEL (kN·m)")
    ax1.set_title("(a) DEL Scaling: NREL 5MW vs MM82")
    ax1.legend(fontsize=8)
    ax1.set_xlim(0, None)
    ax1.set_ylim(0, None)

    # Panel (b): Ratio by wind speed
    pivot_ratio = merged.pivot_table(index="V", columns="TI", values="ratio")
    for ti in pivot_ratio.columns:
        ax2.plot(pivot_ratio.index, pivot_ratio[ti], "o-", label=f"TI={ti:.0%}", markersize=5)
    ax2.axhline(0.276, color="k", linestyle="--", alpha=0.5, label="Theoretical (0.276)")
    ax2.set_xlabel("Wind Speed V (m/s)")
    ax2.set_ylabel("DEL Ratio (MM82 / NREL 5MW)")
    ax2.set_title("(b) DEL Ratio by Wind Speed")
    ax2.legend(fontsize=8)
    ax2.set_ylim(0, 0.5)

    fig.tight_layout()
    fig.savefig(OUT / "fig_scaling_validation.png", dpi=200)
    plt.close()
    print(f"Saved: {OUT / 'fig_scaling_validation.png'}")

# ── 4. Longitudinal DEL + Cp Combined ───────────────────
def fig_longitudinal_combined():
    del_df = pd.read_csv(SCADA_DIR / "longitudinal_del_T01_v2.csv")  # v10.0: per-record interpolation
    ann_df = pd.read_csv(SCADA_DIR / "longitudinal_annual_summary.csv")

    # Annual DEL
    annual_del = del_df.groupby("year")["DEL_est_kNm"].mean().reset_index()
    annual_del.columns = ["year", "DEL_annual"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

    # Panel (a): Annual DEL
    ax1.bar(annual_del["year"], annual_del["DEL_annual"], color="#2196F3", alpha=0.8, width=0.6)
    ax1.set_ylabel("Annual Mean DEL (kN·m)")
    ax1.set_title("Penmanshiel T01 — Longitudinal Trends (2016–2021, per-record interpolation)")
    for _, row in annual_del.iterrows():
        ax1.text(row["year"], row["DEL_annual"] + 20, f"{row['DEL_annual']:.0f}",
                ha="center", fontsize=9)

    # Panel (b): Cp_max
    ax2.plot(ann_df["year"], ann_df["Cp_max"], "o-", color="#4CAF50", markersize=8, linewidth=2)
    ax2.set_ylabel("Cp_max")
    ax2.set_xlabel("Year")
    ax2.set_ylim(0.40, 0.46)

    for _, row in ann_df.iterrows():
        ax2.text(row["year"], row["Cp_max"] + 0.002, f"{row['Cp_max']:.4f}",
                ha="center", fontsize=8)

    fig.tight_layout()
    fig.savefig(OUT / "fig_longitudinal_combined.png", dpi=200)
    plt.close()
    print(f"Saved: {OUT / 'fig_longitudinal_combined.png'}")

if __name__ == "__main__":
    fig_mm82_heatmap()
    fig_penmanshiel_monthly_mm82()
    fig_scaling_comparison()
    fig_longitudinal_combined()
    print("\nAll Paper 2 figures generated.")
