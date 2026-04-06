"""
penmanshiel_longitudinal.py
Penmanshiel 2016-2021 年次パワーカーブ縦断分析（候補K）

目的:
  - T01（基準タービン）の年次パワーカーブ推移を追う
  - 年ごとの Cp_max・AEP変化を定量化
  - 空力劣化（エロージョン由来のパワーロス）の兆候を探索

データ:
  - 2016: 部分年（9月稼働開始）→ 9-12月のみ有効
  - 2017-2021: 全年（欠損は運転停止・メンテ期間）

手法:
  - IEC 61400-12-1 準拠ビン（0.5 m/s）
  - 密度補正済み風速（Density adjusted wind speed）
  - カーテイルメント除去（ピッチ角基準）

出力:
  phase3_scada/longitudinal_power_curves.csv
  phase3_scada/longitudinal_cp_trend.png
  phase3_scada/longitudinal_aep_trend.png
  phase3_scada/longitudinal_power_curves.png
"""

from pathlib import Path
import csv
import io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.special import gamma
from scipy.stats import linregress

REPO_ROOT = Path(__file__).parent.parent
OUT_DIR   = REPO_ROOT / "phase3_scada"

# MM82 諸元
D_ROTOR   = 82.0
A_ROTOR   = np.pi * (D_ROTOR / 2) ** 2
RHO_REF   = 1.225
P_RATED   = 2050.0
BIN_WIDTH = 0.5
V_BINS_CTR = np.arange(1.0, 25.5, BIN_WIDTH)

YEARS = [2016, 2017, 2018, 2019, 2020, 2021]
YEAR_COLORS = {
    2016: "#d62728",
    2017: "#ff7f0e",
    2018: "#bcbd22",
    2019: "#2ca02c",
    2020: "#1f77b4",
    2021: "#9467bd",
}


# ─────────────────────────────────────────
# 1. データ読み込み（年ごと）
# ─────────────────────────────────────────

def find_t01_csv(year: int) -> object:
    """各年の T01 CSV ファイルを探す。"""
    scada_dir = REPO_ROOT / f"data/penmanshiel/scada_{year}"
    if not scada_dir.exists():
        return None
    matches = list(scada_dir.glob("Turbine_Data_Penmanshiel_01_*.csv"))
    return matches[0] if matches else None


def load_t01_year(year: int) -> object:
    """T01 の年次データを読み込む。"""
    csv_path = find_t01_csv(year)
    if csv_path is None:
        print(f"  [{year}] T01 CSV not found — skipping")
        return None

    with open(csv_path, encoding="utf-8-sig") as fh:
        for i, line in enumerate(fh):
            if i == 9:
                header_raw = line.strip().lstrip("# ")
                break

    cols = next(csv.reader(io.StringIO(header_raw)))

    df = pd.read_csv(csv_path, skiprows=10, header=None,
                     names=cols, na_values=["NaN", "nan", ""],
                     low_memory=False)
    df["Date and time"] = pd.to_datetime(df["Date and time"], errors="coerce")
    df = df.dropna(subset=["Date and time"])
    df = df.sort_values("Date and time").reset_index(drop=True)

    # 必要列だけ抽出
    col_map = {
        "Density adjusted wind speed (m/s)": "v_adj",
        "Wind speed (m/s)":                  "v_raw",
        "Power (kW)":                        "power_kw",
        "Turbine Power setpoint (kW)":       "power_setpoint",
        "Blade angle (pitch position) A (°)":"pitch_a",
        "Blade angle (pitch position) B (°)":"pitch_b",
        "Blade angle (pitch position) C (°)":"pitch_c",
        "Nacelle ambient temperature (°C)":  "nacelle_temp",
    }
    available = {k: v for k, v in col_map.items() if k in df.columns}
    out = df[["Date and time"] + list(available.keys())].rename(
        columns={"Date and time": "timestamp", **available}
    ).copy()
    out["year"]  = year
    out["month"] = out["timestamp"].dt.month

    pitch_cols = [c for c in ["pitch_a", "pitch_b", "pitch_c"] if c in out.columns]
    out["pitch_mean"] = out[pitch_cols].mean(axis=1) if pitch_cols else np.nan

    n_raw = len(out)
    n_months = out["month"].nunique()
    print(f"  [{year}] Loaded {n_raw:,} records, {n_months} months "
          f"({out['timestamp'].min().date()} – {out['timestamp'].max().date()})")
    return out


# ─────────────────────────────────────────
# 2. QCフィルタ（パワーカーブ用）
# ─────────────────────────────────────────

def apply_pc_qc(df: pd.DataFrame) -> pd.DataFrame:
    n0 = len(df)
    df = df[df["v_adj"].between(1.0, 25.0) &
            df["power_kw"].between(-50, P_RATED * 1.1)].copy()

    if "power_setpoint" in df.columns:
        mask = (df["power_setpoint"] < P_RATED * 0.95) & \
               (df["v_adj"] > 8.0) & df["power_setpoint"].notna()
        df = df[~mask].copy()

    if "pitch_mean" in df.columns:
        mask = (df["pitch_mean"] > 15.0) & df["v_adj"].between(4.0, 12.0)
        df = df[~mask].copy()

    if "nacelle_temp" in df.columns:
        df = df[~(df["nacelle_temp"] < -3.0)].copy()

    n1 = len(df)
    print(f"    QC: {n0:,} → {n1:,} ({100*(n0-n1)/max(n0,1):.1f}% removed)")
    return df.reset_index(drop=True)


# ─────────────────────────────────────────
# 3. パワーカーブ・Cp計算
# ─────────────────────────────────────────

def bin_power_curve(df: pd.DataFrame, year: int) -> pd.DataFrame:
    df["v_bin"] = pd.cut(df["v_adj"],
                         bins=V_BINS_CTR - BIN_WIDTH / 2,
                         labels=V_BINS_CTR[:-1] + BIN_WIDTH / 2,
                         right=True).astype(float)

    stats = df.groupby("v_bin").agg(
        n_records  = ("power_kw", "count"),
        power_mean = ("power_kw", "mean"),
        power_std  = ("power_kw", "std"),
        power_p25  = ("power_kw", lambda x: x.quantile(0.25)),
        power_p75  = ("power_kw", lambda x: x.quantile(0.75)),
    ).reset_index()

    stats["Cp"] = np.where(
        stats["v_bin"] > 0.5,
        (stats["power_mean"] * 1000) / (0.5 * RHO_REF * A_ROTOR * stats["v_bin"]**3),
        np.nan
    )
    stats["Cp"] = stats["Cp"].where(stats["Cp"].between(0, 0.65))
    stats["year"] = year
    return stats[stats["n_records"] >= 3]


def estimate_aep_from_pc(pc: pd.DataFrame, v_mean: float) -> float:
    k = 2.0
    c = v_mean / gamma(1 + 1 / k)
    from scipy.stats import weibull_min
    aep = 0.0
    for _, row in pc.iterrows():
        v = row["v_bin"]
        p = row["power_mean"]
        if np.isnan(p) or p < 0:
            continue
        prob = weibull_min.pdf(v, k, scale=c) * BIN_WIDTH
        aep += p * prob * 8760.0
    return aep / 1000  # MWh


# ─────────────────────────────────────────
# 4. 可視化
# ─────────────────────────────────────────

def plot_annual_power_curves(all_pc: pd.DataFrame, annual_stats: pd.DataFrame):
    """年次パワーカーブの重ね合わせ（3パネル）。"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    years_avail = sorted(all_pc["year"].unique())

    # Panel 1: パワーカーブ重ね合わせ
    ax = axes[0]
    for yr in years_avail:
        sub = all_pc[all_pc["year"] == yr]
        ax.plot(sub["v_bin"], sub["power_mean"] / 1000,
                lw=2, color=YEAR_COLORS.get(yr, "gray"), label=str(yr))
    ax.axhline(P_RATED / 1000, color="black", ls=":", lw=1.2, label=f"Rated {P_RATED/1000:.2f}MW")
    ax.set_xlabel("Density-Adjusted Wind Speed (m/s)")
    ax.set_ylabel("Power (MW)")
    ax.set_title("Annual Power Curves — T01 (2016–2021)")
    ax.legend(fontsize=9)
    ax.set_xlim(0, 22)
    ax.set_ylim(-0.05, 2.3)
    ax.grid(alpha=0.3)

    # Panel 2: Cp カーブ重ね合わせ
    ax = axes[1]
    for yr in years_avail:
        sub = all_pc[(all_pc["year"] == yr) & all_pc["v_bin"].between(4, 14)]
        ax.plot(sub["v_bin"], sub["Cp"],
                lw=2, color=YEAR_COLORS.get(yr, "gray"), label=str(yr))
    ax.axhline(16/27, color="red", ls=":", lw=1.2, label="Betz (0.593)")
    ax.set_xlabel("Density-Adjusted Wind Speed (m/s)")
    ax.set_ylabel("Power Coefficient Cp")
    ax.set_title("Annual Cp Curve — T01 (2016–2021)")
    ax.legend(fontsize=9)
    ax.set_ylim(0.1, 0.65)
    ax.grid(alpha=0.3)

    # Panel 3: 部分負荷域のパワー差（対 2016or最古年）
    ax = axes[2]
    base_year = years_avail[0]
    base_pc = all_pc[all_pc["year"] == base_year].set_index("v_bin")["power_mean"]

    for yr in years_avail[1:]:
        sub = all_pc[(all_pc["year"] == yr) & all_pc["v_bin"].between(4, 14)].set_index("v_bin")
        delta = ((sub["power_mean"] - base_pc) / P_RATED * 100).dropna()
        ax.plot(delta.index, delta.values,
                lw=2, color=YEAR_COLORS.get(yr, "gray"), label=f"{yr} vs {base_year}")

    ax.axhline(0, color="black", lw=1.5)
    ax.axhspan(-3, 0, alpha=0.06, color="red")
    ax.set_xlabel("Wind Speed (m/s)")
    ax.set_ylabel(f"ΔPower vs {base_year} (% of rated)")
    ax.set_title(f"Power Change Relative to {base_year}\n(negative = degradation)")
    ax.legend(fontsize=9)
    ax.set_xlim(3, 15)
    ax.grid(alpha=0.3)

    plt.suptitle("Penmanshiel T01 — Longitudinal Power Curve Analysis (2016–2021)\n"
                 "Senvion MM82 | IEC 61400-12-1 bins | Curtailment filtered",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    out = OUT_DIR / "longitudinal_power_curves.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")


def plot_trend_charts(annual_stats: pd.DataFrame):
    """Cp_max・AEP の年次推移と回帰線（2パネル）。"""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    years = annual_stats["year"].values
    colors = [YEAR_COLORS.get(y, "gray") for y in years]

    # Panel 1: Cp_max 年次推移
    ax = axes[0]
    cp_vals = annual_stats["Cp_max"].values
    ax.scatter(years, cp_vals, c=colors, s=100, zorder=5)
    for y, cp, col in zip(years, cp_vals, colors):
        ax.annotate(f"{cp:.4f}", (y, cp), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=9, color=col)

    # 回帰線（2016が部分年なら除外）
    fit_years = annual_stats[annual_stats["n_months"] >= 10]["year"].values
    fit_cp    = annual_stats[annual_stats["n_months"] >= 10]["Cp_max"].values
    if len(fit_years) >= 3:
        slope, intercept, r, p, _ = linregress(fit_years, fit_cp)
        x_fit = np.array([fit_years.min(), fit_years.max()])
        ax.plot(x_fit, intercept + slope * x_fit, "k--", lw=1.5,
                label=f"Trend: {slope*1000:.2f}×10⁻³/yr (p={p:.3f})")
        total_drop = slope * (fit_years.max() - fit_years.min())
        ax.set_title(f"Cp_max Annual Trend — T01\n"
                     f"Total change over {fit_years.max()-fit_years.min()}yr: "
                     f"{total_drop*100:+.2f}%pts")
    else:
        ax.set_title("Cp_max Annual Trend — T01")

    ax.set_xlabel("Year")
    ax.set_ylabel("Cp_max (V=5–10 m/s)")
    ax.set_xticks(YEARS)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_ylim(0.38, 0.52)

    # Panel 2: AEP 年次推移
    ax = axes[1]
    aep_vals = annual_stats["AEP_MWh"].values
    ax.scatter(years, aep_vals, c=colors, s=100, zorder=5)
    for y, aep, col in zip(years, aep_vals, colors):
        ax.annotate(f"{aep:.0f}", (y, aep), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=9, color=col)

    fit_aep = annual_stats[annual_stats["n_months"] >= 10]["AEP_MWh"].values
    if len(fit_years) >= 3:
        slope_a, intercept_a, r_a, p_a, _ = linregress(fit_years, fit_aep)
        ax.plot(x_fit, intercept_a + slope_a * x_fit, "k--", lw=1.5,
                label=f"Trend: {slope_a:+.0f} MWh/yr (p={p_a:.3f})")
        ax.set_title(f"AEP Estimate Annual Trend — T01\n"
                     f"Trend: {slope_a:+.0f} MWh/year")
    else:
        ax.set_title("AEP Estimate Annual Trend — T01")

    ax.set_xlabel("Year")
    ax.set_ylabel("AEP Estimate (MWh/year, Weibull k=2)")
    ax.set_xticks(YEARS)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    # 2016 注記（部分年）
    for ax in axes:
        ax.axvline(2016.2, color="orange", ls=":", lw=1.2, alpha=0.7)
        ax.text(2016.3, ax.get_ylim()[0] + (ax.get_ylim()[1]-ax.get_ylim()[0])*0.05,
                "2016=partial\n(Sep–Dec)", fontsize=7, color="orange")

    plt.suptitle("Penmanshiel T01 — Cp and AEP Degradation Trend (2016–2021)\n"
                 "[Note: Year-to-year variability includes wind resource differences]",
                 fontsize=11, fontweight="bold")
    plt.tight_layout()
    out = OUT_DIR / "longitudinal_cp_trend.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")


# ─────────────────────────────────────────
# メイン
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=== Penmanshiel Longitudinal Analysis (Phase K) ===\n")
    print("Processing T01 for years 2016–2021...\n")

    all_pc_frames = []
    annual_records = []

    for year in YEARS:
        print(f"\n[{year}]")
        df = load_t01_year(year)
        if df is None:
            continue

        df = apply_pc_qc(df)
        pc = bin_power_curve(df, year)

        v_mean = df["v_adj"].mean()
        aep    = estimate_aep_from_pc(pc, v_mean)
        cp_max = pc[pc["v_bin"].between(5, 10)]["Cp"].max()
        n_months = df["month"].nunique()

        annual_records.append({
            "year":     year,
            "n_months": n_months,
            "v_mean":   round(v_mean, 3),
            "Cp_max":   round(cp_max, 4),
            "AEP_MWh":  round(aep, 0),
        })
        print(f"    V_mean={v_mean:.2f} m/s, Cp_max={cp_max:.4f}, "
              f"AEP≈{aep:.0f} MWh ({n_months} months)")

        all_pc_frames.append(pc)

    if not all_pc_frames:
        print("No data found. Please run downloads first.")
        exit(1)

    all_pc = pd.concat(all_pc_frames, ignore_index=True)
    annual_stats = pd.DataFrame(annual_records)

    print("\n=== Annual Summary (T01) ===")
    print(f"{'Year':>5}  {'Months':>6}  {'V_mean':>7}  {'Cp_max':>7}  {'AEP(MWh)':>10}")
    print("-" * 45)
    for _, row in annual_stats.iterrows():
        flag = " ← partial" if row["n_months"] < 10 else ""
        print(f"{int(row['year']):>5}  {int(row['n_months']):>6}  "
              f"{row['v_mean']:>7.3f}  {row['Cp_max']:>7.4f}  "
              f"{row['AEP_MWh']:>10.0f}{flag}")

    # 全年Cp_max範囲
    full_years = annual_stats[annual_stats["n_months"] >= 10]
    if len(full_years) >= 2:
        cp_range = full_years["Cp_max"].max() - full_years["Cp_max"].min()
        aep_range = full_years["AEP_MWh"].max() - full_years["AEP_MWh"].min()
        print(f"\nFull-year span (≥10 months):")
        print(f"  Cp_max range:  {full_years['Cp_max'].min():.4f} – "
              f"{full_years['Cp_max'].max():.4f}  (Δ={cp_range:.4f})")
        print(f"  AEP range:     {full_years['AEP_MWh'].min():.0f} – "
              f"{full_years['AEP_MWh'].max():.0f} MWh  (Δ={aep_range:.0f} MWh)")

    print("\nGenerating plots...")
    plot_annual_power_curves(all_pc, annual_stats)
    plot_trend_charts(annual_stats)

    all_pc.to_csv(OUT_DIR / "longitudinal_power_curves.csv", index=False)
    annual_stats.to_csv(OUT_DIR / "longitudinal_annual_summary.csv", index=False)
    print("  Saved: longitudinal_power_curves.csv")
    print("  Saved: longitudinal_annual_summary.csv")

    print("\n=== Done ===")
