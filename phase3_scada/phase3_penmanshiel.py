"""
phase3_penmanshiel.py
Penmanshiel SCADA データを用いた月次DEL推定パイプライン

Penmanshiel vs Kaggle SCADA の主な改善点:
  1. TI直接計測: 10分間の風速標準偏差列（col 2）から σ/V_mean で計算
     → Kaggle データでは bin 内σ/μ 代替が必要だったが不要に
  2. 14台の実運転データ（Senvion MM82, 2016-2021）
  3. 測定ノイズ・欠損が実データ由来で現実的

注意事項（重要）:
  - DELマトリクスはNREL 5MW基準タービンで算出（OpenFAST DLC 1.2相当）
  - Senvion MM82（2.05 MW, D=82m, hub=59m）とは設計が異なる
  - 絶対値比較には使えない。相対的な疲労負荷傾向の比較に限定する
  - 比較用途として「月次傾向・季節性・TIの影響」を主軸とする

入力:
  data/penmanshiel/scada_2020/Turbine_Data_Penmanshiel_0X_*.csv

出力:
  phase3_scada/penmanshiel_monthly_del.csv   … 月次DEL推定値（全タービン）
  phase3_scada/penmanshiel_ti_analysis.png   … TI分布・DEL月次推移
  phase3_scada/penmanshiel_summary.md        … サマリーレポート

環境: conda env blade-phase3
"""

from pathlib import Path
import csv
import io
import pandas as pd
import numpy as np
from scipy.interpolate import RegularGridInterpolator
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).parent.parent
SCADA_DIR = REPO_ROOT / "data/penmanshiel/scada_2020"
OUT_DIR   = REPO_ROOT / "phase3_scada"
# Phase I: MM82 スケーリング済み DEL マトリクスを優先使用
# (未生成の場合は NREL 5MW 拡張マトリクスにフォールバック)
_DEL_MM82_PATH    = REPO_ROOT / "phase5_openfast_shm/openfast_cases/results/del_matrix_mm82.csv"
_DEL_NREL5MW_PATH = REPO_ROOT / "phase5_openfast_shm/openfast_cases/results/del_matrix_ms_extended.csv"
DEL_MATRIX_PATH   = _DEL_MM82_PATH if _DEL_MM82_PATH.exists() else _DEL_NREL5MW_PATH
print(f"[DEL matrix] {DEL_MATRIX_PATH.name}")

# Senvion MM82 の運転範囲（Penmanshiel実測に基づく推奨値）
CUT_IN_V    = 3.5     # m/s
CUT_OUT_V   = 25.0    # m/s
RATED_V     = 13.0    # m/s（MM82の定格風速近似）
RATED_P_KW  = 2050.0  # kW

# Phase I MM82 DEL matrix で再較正した重み（2026-04-04）
# LinearRegression(positive=True, fit_intercept=False) on DEL_norm ~ V_norm + TI_norm
# R2=0.943, Pearson r=0.976（旧NREL 5MW: w_V=0.810/w_TI=0.190）
W_V  = 0.7253
W_TI = 0.2747


# ─────────────────────────────────────────
# 1. Penmanshiel CSV 読み込み
# ─────────────────────────────────────────

def read_penmanshiel_csv(path: Path) -> pd.DataFrame:
    """
    Greenbyte形式のPenmanshiel SCADAファイルを読み込む。

    フォーマット:
      - 行0-8: コメント行 (# で始まる)
      - 行9: カラム名行 (# Date and time,Wind speed,...)
      - 行10+: 10分間データ

    主要列:
      col[0]  Date and time
      col[1]  Wind speed (m/s)
      col[2]  Wind speed, Standard deviation (m/s)  ← TI計算に使用
      col[61] Power (kW)
      col[63] Power, Standard deviation (kW)
      col[211] Rotor speed (RPM)
    """
    # カラム名を行9から取得
    with open(path, encoding="utf-8-sig") as fh:
        for i, line in enumerate(fh):
            if i == 9:
                header_raw = line.strip().lstrip("# ")
                break

    reader = csv.reader(io.StringIO(header_raw))
    cols = next(reader)

    # データを行10以降から読む（header=None で列名を後付け）
    df = pd.read_csv(path, skiprows=10, header=None,
                     names=cols, na_values=["NaN", "nan", ""],
                     low_memory=False)

    # タイムスタンプ変換
    df["Date and time"] = pd.to_datetime(df["Date and time"], errors="coerce")
    df = df.dropna(subset=["Date and time"])
    df = df.sort_values("Date and time").reset_index(drop=True)
    df["month"] = df["Date and time"].dt.month

    return df


def extract_key_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    必要な列だけを抽出してリネームする。
    TI = σ_ws / V_ws (IEC 61400-1: 10分間の風速標準偏差 / 平均風速)
    """
    key = {
        "Date and time":                          "timestamp",
        "Wind speed (m/s)":                       "wind_speed_ms",
        "Wind speed, Standard deviation (m/s)":   "wind_speed_std",
        "Power (kW)":                             "power_kw",
        "Power, Standard deviation (kW)":         "power_std",
        "Nacelle ambient temperature (°C)":       "nacelle_temp_c",
        "Rotor speed (RPM)":                      "rotor_rpm",
        "Blade angle (pitch position) A (°)":     "pitch_a_deg",
    }
    available = {k: v for k, v in key.items() if k in df.columns}
    out = df[list(available.keys())].rename(columns=available).copy()
    out["month"] = df["month"]

    # TI直接計算（IEC準拠: 10分間の標準偏差 / 平均風速）
    out["TI_direct"] = np.where(
        out["wind_speed_ms"] > 0.5,
        out["wind_speed_std"] / out["wind_speed_ms"],
        np.nan
    )

    return out


# ─────────────────────────────────────────
# 2. 品質フィルタ
# ─────────────────────────────────────────

def apply_qc_filter(df: pd.DataFrame) -> pd.DataFrame:
    """
    物理的に妥当な運転状態のレコードだけを残す。
    カーテイルメント（低出力異常）は除外しない（MM82用の理論出力列がないため）。
    """
    before = len(df)

    # 物理範囲フィルタ
    df = df[
        (df["wind_speed_ms"] >= 0) &
        (df["wind_speed_ms"] <= CUT_OUT_V) &
        (df["power_kw"].between(-50, RATED_P_KW * 1.05))
    ].copy()

    # カットイン以上・正常発電のみ
    df = df[
        (df["wind_speed_ms"] >= CUT_IN_V) &
        (df["power_kw"] >= 0)
    ].copy()

    # TI物理範囲（0 < TI < 0.5）
    df = df[
        df["TI_direct"].between(0.005, 0.50, inclusive="both")
    ].copy()

    after = len(df)
    print(f"    QC filter: {before:,} → {after:,} records "
          f"({100*(before-after)/max(before,1):.1f}% removed)")
    return df.reset_index(drop=True)


# ─────────────────────────────────────────
# 3. DEL補間器の構築（phase3b と共通）
# ─────────────────────────────────────────

def build_del_interpolator():
    df = pd.read_csv(DEL_MATRIX_PATH)
    V_list  = sorted(df["V"].unique())
    TI_list = sorted(df["TI"].unique())

    matrix = np.zeros((len(V_list), len(TI_list)))
    for i, v in enumerate(V_list):
        for j, ti in enumerate(TI_list):
            row = df[(df["V"] == v) & (df["TI"].round(3) == round(ti, 3))]
            if len(row) > 0:
                matrix[i, j] = row["DEL_mean"].values[0]

    interp = RegularGridInterpolator(
        (np.array(V_list), np.array(TI_list)),
        matrix,
        method="linear",
        bounds_error=False,
        fill_value=None,
    )
    return interp, (min(V_list), max(V_list)), (min(TI_list), max(TI_list))


# ─────────────────────────────────────────
# 4. 月次DEL推定
# ─────────────────────────────────────────

def calc_monthly_del_penmanshiel(df: pd.DataFrame, turbine_id: str,
                                  interp, V_range, TI_range) -> pd.DataFrame:
    """
    月次代表V・TI（直接計測）からDELを推定する。

    Penmanshiel の優位点: TI_direct は10分間の実測σから計算するため、
    Kaggle SCADA の bin内σ/μ 代替よりも高精度。
    """
    records = []
    for month, grp in df.groupby("month"):
        V_mean     = float(grp["wind_speed_ms"].mean())
        TI_mean    = float(grp["TI_direct"].median())     # medianで外れ値に頑健に
        TI_std     = float(grp["TI_direct"].std())
        n_records  = len(grp)
        avail_frac = n_records / (6 * 30)                # 10min × 6/hr × ~30 days

        # NaN 補完（IEC NTM: Iref=0.12）
        if np.isnan(TI_mean):
            TI_mean = 0.12 * (0.75 + 5.6 / max(V_mean, 1.0))

        # ルックアップ
        V_clipped  = np.clip(V_mean,  V_range[0], V_range[1])
        TI_clipped = np.clip(TI_mean, TI_range[0], TI_range[1])
        del_est    = float(interp([[V_clipped, TI_clipped]])[0])

        records.append({
            "turbine_id":     turbine_id,
            "month":          month,
            "n_records":      n_records,
            "V_mean":         round(V_mean,  3),
            "TI_direct_med":  round(TI_mean, 4),
            "TI_direct_std":  round(TI_std,  4),
            "V_clipped":      round(V_clipped,  3),
            "TI_clipped":     round(TI_clipped, 4),
            "DEL_est_kNm":    round(del_est, 1),
            "avail_approx":   round(avail_frac, 3),
        })

    df_out = pd.DataFrame(records)

    # 疲労リスクスコア（較正済み重み）
    V_n  = (df_out["V_mean"] - df_out["V_mean"].min()) / (df_out["V_mean"].max() - df_out["V_mean"].min() + 1e-9)
    TI_n = (df_out["TI_direct_med"] - df_out["TI_direct_med"].min()) / (df_out["TI_direct_med"].max() - df_out["TI_direct_med"].min() + 1e-9)
    df_out["fatigue_risk_score"] = W_V * V_n + W_TI * TI_n

    return df_out


# ─────────────────────────────────────────
# 5. 可視化
# ─────────────────────────────────────────

def plot_ti_distribution(all_df: pd.DataFrame, monthly_all: pd.DataFrame):
    """TI分布とDEL月次推移を4パネルで表示する。"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    turbines = all_df["turbine_id"].unique() if "turbine_id" in all_df.columns else ["T01"]
    colors = plt.cm.tab10(np.linspace(0, 0.6, len(turbines)))

    # Panel 1: TI 分布（ヒストグラム）
    ax = axes[0, 0]
    for tid, col in zip(turbines, colors):
        sub = all_df[all_df["turbine_id"] == tid]["TI_direct"]
        ax.hist(sub.dropna(), bins=50, alpha=0.6, color=col, label=tid,
                density=True, range=(0, 0.3))
    ax.axvline(0.08, color="red", ls="--", lw=2, label="Matrix lower (TI=0.08)")
    ax.axvline(0.04, color="orange", ls="--", lw=1.5, label="Extended lower (TI=0.04)")
    ax.set_xlabel("Turbulence Intensity (TI)")
    ax.set_ylabel("Density")
    ax.set_title("TI Distribution (10-min direct measurement)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # Panel 2: 月次TI中央値の推移
    ax = axes[0, 1]
    for tid, col in zip(turbines, colors):
        sub = monthly_all[monthly_all["turbine_id"] == tid]
        ax.plot(sub["month"], sub["TI_direct_med"], "o-", color=col, label=tid, lw=2)
    ax.set_xlabel("Month")
    ax.set_ylabel("Monthly Median TI (direct)")
    ax.set_title("Monthly TI Trend by Turbine")
    ax.set_xticks(range(1, 13))
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # Panel 3: 月次 DEL 推定値
    ax = axes[1, 0]
    for tid, col in zip(turbines, colors):
        sub = monthly_all[monthly_all["turbine_id"] == tid]
        ax.plot(sub["month"], sub["DEL_est_kNm"], "s-", color=col, label=tid, lw=2)
    ax.set_xlabel("Month")
    ax.set_ylabel("DEL Estimate (kN-m) [NREL 5MW proxy]")
    ax.set_title("Monthly DEL Estimate (Penmanshiel 2020)\n[Note: NREL 5MW matrix — relative trend only]")
    ax.set_xticks(range(1, 13))
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # Panel 4: V vs TI スキャッタ（TI範囲の視覚化）
    ax = axes[1, 1]
    for tid, col in zip(turbines, colors):
        sub = all_df[all_df["turbine_id"] == tid].sample(min(3000, len(all_df)), random_state=42)
        ax.scatter(sub["wind_speed_ms"], sub["TI_direct"], alpha=0.15, s=5, color=col, label=tid)
    ax.axhline(0.08, color="red", ls="--", lw=1.5, label="Matrix lower bound (0.08)")
    ax.axhline(0.04, color="orange", ls="--", lw=1.5, label="Extended lower bound (0.04)")
    ax.set_xlabel("Wind Speed (m/s)")
    ax.set_ylabel("TI (direct)")
    ax.set_title("Wind Speed vs TI Scatter\n(Penmanshiel 2020 operating data)")
    ax.set_xlim(0, 25)
    ax.set_ylim(0, 0.35)
    ax.legend(fontsize=8, markerscale=3)
    ax.grid(alpha=0.3)

    plt.suptitle(
        "Penmanshiel SCADA 2020 — TI Direct Measurement & DEL Estimation\n"
        "Turbine: Senvion MM82 (2.05 MW) | DEL matrix: NREL 5MW proxy (relative trend only)",
        fontsize=11, fontweight="bold"
    )
    plt.tight_layout()
    out = OUT_DIR / "penmanshiel_ti_analysis.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")


# ─────────────────────────────────────────
# 6. サマリーレポート
# ─────────────────────────────────────────

def write_summary(all_raw: pd.DataFrame, monthly_all: pd.DataFrame,
                  V_range, TI_range):
    """分析サマリーをMarkdownで書き出す。"""
    turbines = monthly_all["turbine_id"].unique()
    lines = [
        "# Penmanshiel SCADA 2020 — Phase 3 Analysis Summary",
        "",
        "## Dataset",
        f"- Turbines analyzed: {', '.join(turbines)}",
        f"- Year: 2020 (366 days)",
        f"- Turbine: Senvion MM82, 2.05 MW, D=82m, hub=59m",
        f"- Total operating records: {len(all_raw):,}",
        "",
        "## TI Measurement (Direct, IEC-compliant)",
        f"- Method: σ_10min / V_10min (from SCADA 'Wind speed, Std' column)",
        f"- Site TI range: {all_raw['TI_direct'].quantile(0.05):.3f} – {all_raw['TI_direct'].quantile(0.95):.3f} (5th–95th pct)",
        f"- Site TI median: {all_raw['TI_direct'].median():.4f}",
        f"- DEL matrix lower bound (extended): {TI_range[0]:.2f}",
        "",
        "## DEL Estimation",
        "**Important**: DEL matrix was built for NREL 5MW reference turbine.",
        "Penmanshiel uses Senvion MM82 (2.05 MW). Absolute values are not comparable.",
        "Use for relative trend analysis only.",
        "",
        "| Turbine | Month | V_mean (m/s) | TI_med | DEL_est (kN-m) |",
        "|---------|-------|:------------:|:------:|:--------------:|",
    ]
    for _, row in monthly_all.iterrows():
        lines.append(
            f"| {row['turbine_id']} | {int(row['month'])} | "
            f"{row['V_mean']:.2f} | {row['TI_direct_med']:.4f} | "
            f"{row['DEL_est_kNm']:.0f} |"
        )

    lines += [
        "",
        "## Comparison with Previous Phase 3b (Kaggle SCADA)",
        "| Metric | Kaggle (T1) | Penmanshiel (T01) |",
        "|--------|:-----------:|:-----------------:|",
        f"| TI computation | bin σ/μ approx | direct σ/V (IEC) |",
        f"| Site TI (median) | ~0.035 (synthetic) | {all_raw['TI_direct'].median():.4f} (real) |",
        "| Turbine | Kaggle T1 (unknown) | Senvion MM82 2.05MW |",
        "| Data quality | Kaggle dataset | Zenodo CC-BY-4.0 |",
        "",
        "## Key Finding",
        f"Penmanshiel TI (median = {all_raw['TI_direct'].median():.3f}) falls in the"
        f" extended matrix range (TI ≥ {TI_range[0]:.2f}).",
        "The Low-TI extension (Phase 5b) is essential for accurate DEL lookup.",
    ]

    out = OUT_DIR / "penmanshiel_summary.md"
    out.write_text("\n".join(lines))
    print(f"  Saved: {out}")


# ─────────────────────────────────────────
# メイン
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=== Phase 3: Penmanshiel SCADA Pipeline ===\n")

    # DEL補間器
    print("1. Building DEL interpolator...")
    interp, V_range, TI_range = build_del_interpolator()
    print(f"   V range: {V_range}, TI range: {TI_range}")

    # 利用可能なCSVを自動検出
    csv_files = sorted(SCADA_DIR.glob("Turbine_Data_Penmanshiel_*.csv"))
    print(f"\n2. Found {len(csv_files)} turbine file(s):")
    for f in csv_files:
        print(f"   {f.name}")

    all_raw_frames   = []
    monthly_frames   = []

    print("\n3. Processing turbines...")
    for csv_path in csv_files:
        # タービンIDをファイル名から抽出（_0X_ の部分）
        parts = csv_path.stem.split("_")
        turbine_id = f"T{parts[3]}"   # e.g. "T01", "T11"
        print(f"\n  [{turbine_id}] {csv_path.name}")

        # 読み込み・列抽出
        raw = read_penmanshiel_csv(csv_path)
        print(f"    Raw records: {len(raw):,}")
        df  = extract_key_cols(raw)

        # タービンIDを付加
        df["turbine_id"] = turbine_id

        # QCフィルタ
        df = apply_qc_filter(df)

        # TI基本統計
        ti_med = df["TI_direct"].median()
        ti_q05 = df["TI_direct"].quantile(0.05)
        ti_q95 = df["TI_direct"].quantile(0.95)
        print(f"    TI (direct): median={ti_med:.4f}, "
              f"5th-95th=[{ti_q05:.4f}, {ti_q95:.4f}]")
        below_matrix = (df["TI_direct"] < TI_range[0]).mean() * 100
        print(f"    TI < {TI_range[0]:.2f} (original matrix lower): {below_matrix:.1f}% of records")
        below_extended = (df["TI_direct"] < 0.04).mean() * 100
        print(f"    TI < 0.04 (extended lower): {below_extended:.1f}% of records")

        # 月次DEL
        monthly = calc_monthly_del_penmanshiel(df, turbine_id, interp, V_range, TI_range)
        print(f"    Annual avg DEL: {monthly['DEL_est_kNm'].mean():.0f} kN-m")
        print(f"    Peak month: {int(monthly.loc[monthly['DEL_est_kNm'].idxmax(), 'month'])}M "
              f"({monthly['DEL_est_kNm'].max():.0f} kN-m)")

        all_raw_frames.append(df)
        monthly_frames.append(monthly)

    # 全タービン結合
    all_raw    = pd.concat(all_raw_frames, ignore_index=True)
    monthly_all = pd.concat(monthly_frames, ignore_index=True)

    print(f"\n4. Total operating records: {len(all_raw):,}")
    print(f"   Overall TI median: {all_raw['TI_direct'].median():.4f}")
    print(f"   Overall TI mean:   {all_raw['TI_direct'].mean():.4f}")

    # 月次サマリー表示
    print("\n=== Monthly DEL Summary (all turbines) ===")
    print(f"{'Turb':>4}  {'Month':>5}  {'V_mean':>7}  {'TI_med':>7}  {'DEL(kNm)':>9}")
    print("-" * 45)
    for _, row in monthly_all.iterrows():
        print(f"{row['turbine_id']:>4}  {int(row['month']):>5}  "
              f"{row['V_mean']:>7.2f}  {row['TI_direct_med']:>7.4f}  "
              f"{row['DEL_est_kNm']:>9.0f}")

    print("\n5. Plotting...")
    plot_ti_distribution(all_raw, monthly_all)

    print("\n6. Saving CSV...")
    out_csv = OUT_DIR / "penmanshiel_monthly_del.csv"
    monthly_all.to_csv(out_csv, index=False)
    print(f"   Saved: {out_csv}")

    print("\n7. Writing summary report...")
    write_summary(all_raw, monthly_all, V_range, TI_range)

    print("\n=== Done ===")
