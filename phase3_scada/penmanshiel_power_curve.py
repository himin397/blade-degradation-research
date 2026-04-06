"""
penmanshiel_power_curve.py
Penmanshiel 2020 パワーカーブ分析（候補J）

目的:
  - T01〜T06（全年）の密度補正済みパワーカーブを構築
  - タービン間比較により性能差（パワー低下機台）を特定
  - 月次パワーカーブ推移で季節変動・劣化の兆候を探索
  - Cp分析で空力性能を評価

手法:
  - IEC 61400-12-1 準拠: 0.5 m/s 幅ビン、密度補正済み風速を使用
  - カーテイルメント除去: ピッチ角スレッシュ方式
  - 参照: Senvion MM82 仕様（D=82m, P_rated=2050kW）

出力:
  phase3_scada/penmanshiel_power_curves.csv      … ビン別パワー統計
  phase3_scada/penmanshiel_power_curve_fleet.png … 台間比較図
  phase3_scada/penmanshiel_power_curve_monthly.png … 月次推移図
  phase3_scada/penmanshiel_cp_curve.png          … Cp 曲線比較
  phase3_scada/penmanshiel_performance_summary.csv … 性能指標サマリー
"""

from pathlib import Path
import csv
import io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT  = Path(__file__).parent.parent
SCADA_DIR  = REPO_ROOT / "data/penmanshiel/scada_2020"
OUT_DIR    = REPO_ROOT / "phase3_scada"

# Senvion MM82 諸元
D_ROTOR    = 82.0          # m
A_ROTOR    = np.pi * (D_ROTOR / 2) ** 2   # 5,281 m²
RHO_REF    = 1.225         # kg/m³ (ISO 2533 標準大気)
P_RATED    = 2050.0        # kW
V_CUTIN    = 3.5           # m/s
V_CUTOUT   = 25.0          # m/s
V_RATED    = 13.0          # m/s （近似）

# パワーカーブビン設定（IEC 61400-12-1）
BIN_WIDTH  = 0.5           # m/s
V_BINS_CTR = np.arange(1.0, 25.5, BIN_WIDTH)   # ビン中心: 1.0, 1.5, ..., 25.0

# フル年データを持つタービン（検証済み）
FULL_YEAR_TURBINES = ["T01", "T02", "T04", "T05", "T06"]


# ─────────────────────────────────────────
# 1. データ読み込み（phase3_penmanshiel.py と共通）
# ─────────────────────────────────────────

def read_penmanshiel_csv(path: Path) -> pd.DataFrame:
    with open(path, encoding="utf-8-sig") as fh:
        for i, line in enumerate(fh):
            if i == 9:
                header_raw = line.strip().lstrip("# ")
                break
    reader = csv.reader(io.StringIO(header_raw))
    cols = next(reader)
    df = pd.read_csv(path, skiprows=10, header=None,
                     names=cols, na_values=["NaN", "nan", ""],
                     low_memory=False)
    df["Date and time"] = pd.to_datetime(df["Date and time"], errors="coerce")
    df = df.dropna(subset=["Date and time"])
    return df.sort_values("Date and time").reset_index(drop=True)


def extract_pc_cols(df: pd.DataFrame, turbine_id: str) -> pd.DataFrame:
    """パワーカーブ分析に必要な列を抽出・整形する。"""
    col_map = {
        "Date and time":                        "timestamp",
        "Density adjusted wind speed (m/s)":    "v_adj",     # IEC準拠ビンに使用
        "Wind speed (m/s)":                     "v_raw",     # 参照用
        "Wind speed, Standard deviation (m/s)": "v_std",
        "Power (kW)":                           "power_kw",
        "Power, Standard deviation (kW)":       "power_std",
        "Turbine Power setpoint (kW)":          "power_setpoint",
        "Blade angle (pitch position) A (°)":   "pitch_a",
        "Blade angle (pitch position) B (°)":   "pitch_b",
        "Blade angle (pitch position) C (°)":   "pitch_c",
        "Nacelle ambient temperature (°C)":     "nacelle_temp",
    }
    available = {k: v for k, v in col_map.items() if k in df.columns}
    out = df[list(available.keys())].rename(columns=available).copy()
    out["turbine_id"] = turbine_id
    out["month"] = out["timestamp"].dt.month
    out["season"] = out["month"].map({
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Spring", 4: "Spring", 5: "Spring",
        6: "Summer", 7: "Summer", 8: "Summer",
        9: "Autumn", 10: "Autumn", 11: "Autumn",
    })

    # ピッチ角平均（3ブレード）
    pitch_cols = [c for c in ["pitch_a", "pitch_b", "pitch_c"] if c in out.columns]
    if pitch_cols:
        out["pitch_mean"] = out[pitch_cols].mean(axis=1)
    else:
        out["pitch_mean"] = np.nan

    return out


# ─────────────────────────────────────────
# 2. QCフィルタ（パワーカーブ用）
# ─────────────────────────────────────────

def apply_pc_qc(df: pd.DataFrame) -> pd.DataFrame:
    """
    IEC 61400-12-1 準拠のデータフィルタ。

    除外条件:
      1. 風速範囲外（<1 または >25 m/s）
      2. パワー異常値（< -50 kW または > P_rated × 1.1）
      3. カーテイルメント除去:
         - パワー指令値が定格の 95% 未満かつ風速 > 8 m/s
         - ピッチ角 > 15° かつ 風速 4〜12 m/s（部分負荷域で異常ピッチ）
      4. 着氷疑い: 周囲温度 < -3°C
    """
    n0 = len(df)

    # 物理範囲
    df = df[df["v_adj"].between(1.0, V_CUTOUT) &
            df["power_kw"].between(-50, P_RATED * 1.1)].copy()

    # カーテイルメント（パワー指令値ベース）
    if "power_setpoint" in df.columns:
        curtailed = (
            (df["power_setpoint"] < P_RATED * 0.95) &
            (df["v_adj"] > 8.0) &
            df["power_setpoint"].notna()
        )
        df = df[~curtailed].copy()

    # カーテイルメント（ピッチ角ベース: 部分負荷域で高ピッチ = 制御介入）
    if "pitch_mean" in df.columns:
        pitch_curtailed = (
            (df["pitch_mean"] > 15.0) &
            (df["v_adj"].between(4.0, 12.0))
        )
        df = df[~pitch_curtailed].copy()

    # 着氷除外
    if "nacelle_temp" in df.columns:
        df = df[~(df["nacelle_temp"] < -3.0)].copy()

    n1 = len(df)
    print(f"    PC QC: {n0:,} → {n1:,} records ({100*(n0-n1)/n0:.1f}% removed)")
    return df.reset_index(drop=True)


# ─────────────────────────────────────────
# 3. パワーカーブ（ビン別統計）
# ─────────────────────────────────────────

def bin_power_curve(df: pd.DataFrame, turbine_id: str,
                    month: int = None) -> pd.DataFrame:
    """
    0.5 m/s ビンで平均パワーとCpを計算する（IEC 61400-12-1）。

    Args:
        df: QC済みSCADAデータ
        turbine_id: タービンID
        month: 指定した場合は該当月のみ使用

    Returns:
        ビン別統計DataFrame
    """
    sub = df[df["turbine_id"] == turbine_id].copy()
    if month is not None:
        sub = sub[sub["month"] == month].copy()

    if len(sub) == 0:
        return pd.DataFrame()

    # ビン割り当て
    sub["v_bin"] = pd.cut(sub["v_adj"],
                          bins=V_BINS_CTR - BIN_WIDTH / 2,
                          labels=V_BINS_CTR[:-1] + BIN_WIDTH / 2,
                          right=True)
    sub["v_bin"] = sub["v_bin"].astype(float)

    # ビン統計
    stats = sub.groupby("v_bin").agg(
        n_records   = ("power_kw", "count"),
        power_mean  = ("power_kw", "mean"),
        power_std   = ("power_kw", "std"),
        power_p10   = ("power_kw", lambda x: x.quantile(0.10)),
        power_p90   = ("power_kw", lambda x: x.quantile(0.90)),
        v_mean      = ("v_adj",    "mean"),
    ).reset_index()

    # Cp 計算（密度補正済みV を使用するとCp = P / (0.5×ρ_ref×A×V_adj³)）
    stats["Cp"] = np.where(
        stats["v_bin"] > 0.5,
        (stats["power_mean"] * 1000) /
        (0.5 * RHO_REF * A_ROTOR * stats["v_bin"] ** 3),
        np.nan
    )
    # 物理的上限（Betz=0.593）を超えるものはマスク
    stats["Cp"] = stats["Cp"].where(stats["Cp"].between(0, 0.65))

    stats["turbine_id"] = turbine_id
    if month is not None:
        stats["month"] = month

    # 最小サンプル数（IEC: 3件以上推奨）
    stats = stats[stats["n_records"] >= 3]
    return stats


# ─────────────────────────────────────────
# 4. AEP概算（Weibull分布）
# ─────────────────────────────────────────

def estimate_aep(pc: pd.DataFrame, k: float = 2.0, c: float = None,
                 v_mean: float = None) -> float:
    """
    パワーカーブと Weibull 分布から AEP（MWh/year）を概算する。

    Args:
        pc: ビン別パワーカーブ（power_mean 列必須）
        k: Weibull 形状係数（IEC Class II: k≈2.0）
        c: Weibull スケール係数（指定なければ v_mean から計算）
        v_mean: 年平均風速（c未指定時に使用）
    """
    from scipy.stats import weibull_min
    from scipy.special import gamma

    if c is None and v_mean is not None:
        # c = v_mean / Γ(1 + 1/k)
        c = v_mean / gamma(1 + 1 / k)
    elif c is None:
        c = 8.0 / gamma(1 + 1 / 2.0)  # default: v_mean=8 m/s

    aep = 0.0
    hours_per_year = 8760.0
    for _, row in pc.iterrows():
        v = row["v_bin"]
        p = row["power_mean"]
        if np.isnan(p) or p < 0:
            continue
        # ビン幅内の発生確率（PDF × BIN_WIDTH）
        prob = weibull_min.pdf(v, k, scale=c) * BIN_WIDTH
        aep += p * prob * hours_per_year  # kWh

    return aep / 1000  # MWh


# ─────────────────────────────────────────
# 5. 可視化
# ─────────────────────────────────────────

COLORS = {
    "T01": "#1f77b4", "T02": "#ff7f0e", "T04": "#2ca02c",
    "T05": "#d62728", "T06": "#9467bd", "T07": "#8c564b",
}


def plot_fleet_comparison(all_pc: pd.DataFrame, raw_all: pd.DataFrame):
    """台間パワーカーブ比較（4パネル）。"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 11))

    turbines = [t for t in FULL_YEAR_TURBINES if t in all_pc["turbine_id"].unique()]

    # ─ Panel 1: パワーカーブ（全台）
    ax = axes[0, 0]
    for tid in turbines:
        sub = all_pc[all_pc["turbine_id"] == tid]
        ax.plot(sub["v_bin"], sub["power_mean"] / 1000,
                "-o", ms=4, lw=2, color=COLORS.get(tid, "gray"), label=tid)
        ax.fill_between(sub["v_bin"],
                        sub["power_p10"] / 1000, sub["power_p90"] / 1000,
                        alpha=0.08, color=COLORS.get(tid, "gray"))

    # 定格ライン
    ax.axhline(P_RATED / 1000, color="black", ls=":", lw=1.2, label=f"Rated {P_RATED/1000:.2f} MW")
    ax.axvline(V_RATED, color="gray", ls="--", lw=1.0, alpha=0.5)
    ax.set_xlabel("Density-Adjusted Wind Speed (m/s)")
    ax.set_ylabel("Power (MW)")
    ax.set_title("Power Curve — Fleet Comparison (2020 annual)\n[shaded: 10th–90th percentile]")
    ax.legend(fontsize=9, ncol=2)
    ax.set_xlim(0, 22)
    ax.set_ylim(-0.05, 2.3)
    ax.grid(alpha=0.3)

    # ─ Panel 2: Cp カーブ（全台）
    ax = axes[0, 1]
    for tid in turbines:
        sub = all_pc[(all_pc["turbine_id"] == tid) & (all_pc["v_bin"].between(4, 14))]
        ax.plot(sub["v_bin"], sub["Cp"],
                "-o", ms=4, lw=2, color=COLORS.get(tid, "gray"), label=tid)

    ax.axhline(16/27, color="red", ls=":", lw=1.2, label="Betz limit (0.593)")
    ax.set_xlabel("Density-Adjusted Wind Speed (m/s)")
    ax.set_ylabel("Power Coefficient Cp")
    ax.set_title("Cp Curve — Fleet Comparison (partial load region)")
    ax.legend(fontsize=9, ncol=2)
    ax.set_ylim(0, 0.65)
    ax.grid(alpha=0.3)

    # ─ Panel 3: パワー差分（対フリート平均）
    ax = axes[1, 0]
    fleet_mean = all_pc[all_pc["turbine_id"].isin(turbines)].groupby("v_bin")["power_mean"].mean()

    for tid in turbines:
        sub = all_pc[all_pc["turbine_id"] == tid].set_index("v_bin")
        delta = ((sub["power_mean"] - fleet_mean) / P_RATED * 100).dropna()
        ax.plot(delta.index, delta.values,
                "-o", ms=4, lw=2, color=COLORS.get(tid, "gray"), label=tid)

    ax.axhline(0, color="black", lw=1.5)
    ax.axhspan(-3, 3, alpha=0.08, color="green", label="±3% band")
    ax.set_xlabel("Density-Adjusted Wind Speed (m/s)")
    ax.set_ylabel("ΔPower vs Fleet Mean (% of rated)")
    ax.set_title("Power Deviation from Fleet Mean\n(positive = above fleet average)")
    ax.legend(fontsize=9, ncol=2)
    ax.set_xlim(2, 20)
    ax.grid(alpha=0.3)

    # ─ Panel 4: AEP推定・可用率・Cp_max 比較（バーチャート）
    ax = axes[1, 1]
    summary_data = []
    for tid in turbines:
        sub_pc = all_pc[all_pc["turbine_id"] == tid]
        sub_raw = raw_all[raw_all["turbine_id"] == tid]
        v_mean = sub_raw["v_adj"].mean()
        aep = estimate_aep(sub_pc, v_mean=v_mean)
        cp_max = sub_pc.loc[sub_pc["v_bin"].between(5, 10), "Cp"].max()
        summary_data.append({"turbine_id": tid, "AEP_MWh": aep, "Cp_max": cp_max,
                              "v_mean": v_mean})

    df_sum = pd.DataFrame(summary_data)
    x = np.arange(len(df_sum))
    bars = ax.bar(x, df_sum["AEP_MWh"],
                  color=[COLORS.get(t, "gray") for t in df_sum["turbine_id"]])
    ax.set_xticks(x)
    ax.set_xticklabels(df_sum["turbine_id"], fontsize=11)
    fleet_aep = df_sum["AEP_MWh"].mean()
    ax.axhline(fleet_aep, color="black", ls="--", lw=2,
               label=f"Fleet mean: {fleet_aep:.0f} MWh")
    for bar, (_, row) in zip(bars, df_sum.iterrows()):
        diff_pct = (row["AEP_MWh"] / fleet_aep - 1) * 100
        sign = "+" if diff_pct >= 0 else ""
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + fleet_aep * 0.005,
                f"{sign}{diff_pct:.1f}%",
                ha="center", va="bottom", fontsize=9, fontweight="bold",
                color="green" if diff_pct >= 0 else "red")
    ax.set_ylabel("Estimated AEP (MWh/year)")
    ax.set_title("AEP Estimate by Turbine\n(Weibull k=2.0, V_mean=site actual)")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3, axis="y")

    plt.suptitle(
        "Penmanshiel 2020 — Power Curve Fleet Analysis\n"
        "Senvion MM82 (2.05 MW, D=82m) | IEC 61400-12-1 bins (0.5 m/s) | "
        "Curtailment filtered",
        fontsize=12, fontweight="bold"
    )
    plt.tight_layout()
    out = OUT_DIR / "penmanshiel_power_curve_fleet.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")
    return df_sum


def plot_monthly_curves(monthly_pc: pd.DataFrame, turbine_focus: str = "T01"):
    """選択タービンの月次パワーカーブ推移。"""
    sub = monthly_pc[monthly_pc["turbine_id"] == turbine_focus]
    months = sorted(sub["month"].unique())

    fig, axes = plt.subplots(3, 4, figsize=(18, 12), sharex=True, sharey=True)
    axes = axes.flatten()

    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    # 全月の fleet mean をベースライン として使用
    all_monthly = monthly_pc[monthly_pc["turbine_id"] == turbine_focus]
    annual = all_monthly.groupby("v_bin")["power_mean"].mean()

    for idx, m in enumerate(range(1, 13)):
        ax = axes[idx]
        m_data = sub[sub["month"] == m]

        # 年間平均をグレーで
        ax.plot(annual.index, annual.values / 1000,
                color="lightgray", lw=2, ls="--", label="Annual avg")

        if len(m_data) > 0:
            ax.plot(m_data["v_bin"], m_data["power_mean"] / 1000,
                    color=plt.cm.RdYlBu_r((m - 1) / 11),
                    lw=2, marker="o", ms=3, label=f"{month_names[m-1]}")

        ax.axhline(P_RATED / 1000, color="black", ls=":", lw=0.8)
        ax.set_title(month_names[m - 1], fontsize=10)
        ax.set_xlim(0, 22)
        ax.set_ylim(-0.05, 2.3)
        ax.grid(alpha=0.25)
        if idx % 4 == 0:
            ax.set_ylabel("Power (MW)", fontsize=8)
        if idx >= 8:
            ax.set_xlabel("V_adj (m/s)", fontsize=8)

    plt.suptitle(
        f"Penmanshiel {turbine_focus} — Monthly Power Curve (2020)\n"
        f"Gray dashed: annual average | Colored: monthly curve",
        fontsize=12, fontweight="bold"
    )
    plt.tight_layout()
    out = OUT_DIR / f"penmanshiel_power_curve_monthly_{turbine_focus}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")


def plot_cp_comparison(all_pc: pd.DataFrame):
    """Cp曲線の台間比較（部分負荷域に集中）。"""
    fig, ax = plt.subplots(figsize=(10, 6))
    turbines = [t for t in FULL_YEAR_TURBINES if t in all_pc["turbine_id"].unique()]

    cp_peaks = {}
    for tid in turbines:
        sub = all_pc[(all_pc["turbine_id"] == tid) & all_pc["v_bin"].between(4, 14)]
        ax.plot(sub["v_bin"], sub["Cp"],
                "-o", ms=5, lw=2, color=COLORS.get(tid, "gray"), label=tid)
        if len(sub) > 0:
            cp_max_val = sub["Cp"].max()
            v_at_cp_max = sub.loc[sub["Cp"].idxmax(), "v_bin"]
            cp_peaks[tid] = (cp_max_val, v_at_cp_max)
            ax.annotate(f"{cp_max_val:.3f}",
                        xy=(v_at_cp_max, cp_max_val),
                        xytext=(v_at_cp_max + 0.3, cp_max_val + 0.01),
                        fontsize=8, color=COLORS.get(tid, "gray"))

    ax.axhline(16/27, color="red", ls=":", lw=1.5, label="Betz limit (0.593)")
    ax.set_xlabel("Density-Adjusted Wind Speed (m/s)", fontsize=12)
    ax.set_ylabel("Power Coefficient Cp", fontsize=12)
    ax.set_title("Cp Curve Comparison — Penmanshiel Fleet 2020\n"
                 "(values annotated = Cp_max per turbine)", fontsize=11)
    ax.legend(fontsize=10)
    ax.set_ylim(0.1, 0.65)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    out = OUT_DIR / "penmanshiel_cp_curve.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")
    return cp_peaks


# ─────────────────────────────────────────
# メイン
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=== Penmanshiel Power Curve Analysis (Phase J) ===\n")

    csv_files = sorted(SCADA_DIR.glob("Turbine_Data_Penmanshiel_*.csv"))
    # 全年データのみ処理
    target_files = [f for f in csv_files
                    if any(f"_{tid}_" in f.name for tid in FULL_YEAR_TURBINES)]

    all_raw_frames = []
    all_pc_frames  = []
    monthly_pc_frames = []

    print("1. Loading and processing turbines...")
    for csv_path in csv_files:
        parts = csv_path.stem.split("_")
        turbine_id = f"T{parts[3]}"
        if turbine_id not in FULL_YEAR_TURBINES:
            print(f"   Skipping {turbine_id} (partial year)")
            continue

        print(f"\n  [{turbine_id}]")
        raw = read_penmanshiel_csv(csv_path)
        df  = extract_pc_cols(raw, turbine_id)
        df  = apply_pc_qc(df)

        # 年間パワーカーブ
        pc_annual = bin_power_curve(df, turbine_id)
        v_mean = df["v_adj"].mean()
        aep = estimate_aep(pc_annual, v_mean=v_mean)
        print(f"    V_mean: {v_mean:.2f} m/s")
        print(f"    AEP estimate: {aep:.0f} MWh/year")
        print(f"    Cp_max: {pc_annual[pc_annual['v_bin'].between(5,10)]['Cp'].max():.4f}")

        # 月次パワーカーブ
        for m in sorted(df["month"].unique()):
            pc_m = bin_power_curve(df, turbine_id, month=m)
            if len(pc_m) > 0:
                monthly_pc_frames.append(pc_m)

        all_raw_frames.append(df)
        all_pc_frames.append(pc_annual)

    all_raw = pd.concat(all_raw_frames, ignore_index=True)
    all_pc  = pd.concat(all_pc_frames, ignore_index=True)
    monthly_pc = pd.concat(monthly_pc_frames, ignore_index=True)

    # ─────────────────────────────────────
    print("\n2. Fleet power curve comparison...")
    df_summary = plot_fleet_comparison(all_pc, all_raw)

    print("\n=== Performance Summary ===")
    fleet_aep = df_summary["AEP_MWh"].mean()
    print(f"{'Turbine':>7}  {'V_mean':>7}  {'Cp_max':>7}  {'AEP(MWh)':>10}  {'vs Fleet':>9}")
    print("-" * 52)
    for _, row in df_summary.iterrows():
        diff = (row["AEP_MWh"] / fleet_aep - 1) * 100
        sign = "+" if diff >= 0 else ""
        print(f"{row['turbine_id']:>7}  {row['v_mean']:>7.2f}  "
              f"{row['Cp_max']:>7.4f}  {row['AEP_MWh']:>10.0f}  "
              f"{sign}{diff:>7.1f}%")
    print(f"{'Fleet':>7}  {'':>7}  {'':>7}  {fleet_aep:>10.0f}  {'(mean)':>9}")

    # ─────────────────────────────────────
    print("\n3. Monthly power curve (T01)...")
    plot_monthly_curves(monthly_pc, turbine_focus="T01")

    # ─────────────────────────────────────
    print("\n4. Cp comparison...")
    cp_peaks = plot_cp_comparison(all_pc)
    print("\n  Cp_max by turbine:")
    for tid, (cp_val, v_val) in sorted(cp_peaks.items()):
        print(f"    {tid}: Cp_max={cp_val:.4f} at V={v_val:.1f} m/s")

    # ─────────────────────────────────────
    print("\n5. Saving CSVs...")
    all_pc.to_csv(OUT_DIR / "penmanshiel_power_curves.csv", index=False)
    df_summary.to_csv(OUT_DIR / "penmanshiel_performance_summary.csv", index=False)
    print(f"  Saved: penmanshiel_power_curves.csv")
    print(f"  Saved: penmanshiel_performance_summary.csv")

    print("\n=== Done ===")
