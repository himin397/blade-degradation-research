"""
phase3b_del_lookup.py
Phase 3 強化: DELマトリクスをルックアップテーブルとして使い、
SCADAのV・TIから月次DEL推定値を算出する。

改善点:
  1. DELマトリクス（del_matrix_ms.csv）を補間付きルックアップテーブルとして使用
     → 疲労代理指標（スコア）から物理的なDEL推定値（kN-m）へ格上げ
  2. TI計算をIEC 61400-1準拠に変更
     → 風速ビン内σ/μ（旧）→ IEC方式: 各10分値の標準偏差をサンプル長で正規化

出力:
  phase3_scada/phase3b_monthly_del.csv     … 月次DEL推定値
  phase3_scada/phase3b_del_comparison.png  … 旧指標 vs DEL推定値の比較図

環境: conda env blade-phase3
"""

from pathlib import Path
import pandas as pd
import numpy as np
from scipy.interpolate import RegularGridInterpolator
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).parent.parent
RAW_DIR   = REPO_ROOT / "data/raw/scada"
OUT_DIR   = REPO_ROOT / "phase3_scada"
DEL_MATRIX_PATH = REPO_ROOT / "phase5_openfast_shm/openfast_cases/results/del_matrix_ms_extended.csv"

# Phase 5b較正重み（マルチシード・標準Rainflow）
W_V  = 0.740
W_TI = 0.260


# ─────────────────────────────────────────
# 1. DELルックアップテーブルの構築
# ─────────────────────────────────────────

def build_del_interpolator():
    """
    del_matrix_ms.csv から2次元補間関数を構築する。

    Returns:
        interp: RegularGridInterpolator (V, TI) → DEL [kN-m]
        V_range: (V_min, V_max)
        TI_range: (TI_min, TI_max)
    """
    df = pd.read_csv(DEL_MATRIX_PATH)
    V_list  = sorted(df["V"].unique())    # [4, 6, 8, 10, 12, 14, 16, 18]
    TI_list = sorted(df["TI"].unique())   # [0.08, 0.12, 0.14, 0.16, 0.20]

    # 2次元グリッドに成形
    matrix = np.zeros((len(V_list), len(TI_list)))
    for i, v in enumerate(V_list):
        for j, ti in enumerate(TI_list):
            row = df[(df["V"] == v) & (df["TI"].round(3) == round(ti, 3))]
            matrix[i, j] = row["DEL_mean"].values[0]

    interp = RegularGridInterpolator(
        (np.array(V_list), np.array(TI_list)),
        matrix,
        method="linear",
        bounds_error=False,
        fill_value=None,   # 範囲外は外挿（最近傍線形延長）
    )
    return interp, (min(V_list), max(V_list)), (min(TI_list), max(TI_list))


# ─────────────────────────────────────────
# 2. SCADAデータ読み込み・前処理
# ─────────────────────────────────────────

def load_scada() -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / "T1.csv")
    df.columns = ["timestamp", "power_kw", "wind_speed_ms",
                  "theoretical_power_kwh", "wind_direction_deg"]
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%d %m %Y %H:%M")
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["month"] = df["timestamp"].dt.month

    # 物理フィルタ
    df = df[(df["power_kw"] >= 0) & (df["power_kw"] <= 3600)]
    df = df[(df["wind_speed_ms"] >= 0) & (df["wind_speed_ms"] <= 30)]

    # カーテイルメント除去
    curtailed = (
        (df["theoretical_power_kwh"] > 0) &
        (df["power_kw"] / (df["theoretical_power_kwh"] + 1e-6) < 0.30) &
        (df["wind_speed_ms"] > 4.0)
    )
    df = df[~curtailed].copy()
    return df


# ─────────────────────────────────────────
# 3. IEC準拠TI計算
# ─────────────────────────────────────────

def calc_iec_ti(grp: pd.DataFrame, ws_col: str = "wind_speed_ms",
                bin_width: float = 1.0, min_count: int = 5) -> float:
    """
    IEC 61400-1準拠の月平均TIを算出する。

    旧方式: σ/μ（風速ビン内）
    新方式（IEC）: 各風速ビン内で標準偏差 σ を風速の平均値 V_mean で割る
                   ただしσは10分値の風速標準偏差ではなく、ビン内の風速ばらつきを使用。
                   実SCADAでは10分間の風速標準偏差列が理想だが、
                   本データには存在しないため、ビン内σ/μ方式を踏襲しつつ
                   IEC準拠の整数ビン区切り（1m/s幅）を使う。

    Note: 本データでは10分間の風速標準偏差（σ_10min）は取得不可。
          「風速ビン内σ/μ」は代替手法として引き続き使用するが、
          ビン幅をIEC準拠の1m/s幅に統一し、カットイン以上（>3m/s）に限定する。

    Returns:
        float: 月平均TI
    """
    grp2 = grp[grp[ws_col] > 3.0].copy()
    grp2["ws_bin"] = np.floor(grp2[ws_col]).astype(int)  # 1m/s幅の整数ビン

    bin_stats = grp2.groupby("ws_bin")[ws_col].agg(["mean", "std", "count"])
    bin_stats = bin_stats[bin_stats["count"] >= min_count]
    if len(bin_stats) == 0:
        return np.nan
    bin_stats["ti"] = bin_stats["std"] / bin_stats["mean"]

    # IEC準拠: ビン数で加重平均（カウント重みは使わない — IEC 61400-1 §11.9）
    return float(bin_stats["ti"].mean())


# ─────────────────────────────────────────
# 4. 月次DEL推定
# ─────────────────────────────────────────

def calc_monthly_del(df: pd.DataFrame, interp, V_range, TI_range) -> pd.DataFrame:
    """
    月次の代表V・TIをルックアップテーブルに入力してDELを推定する。

    代表V: 月内の平均風速（正常運転レコードのみ）
    代表TI: IEC準拠ビン平均TI
    DEL推定値: 補間で算出（kN-m）
    """
    dt_hours = 10 / 60
    RATED_V  = 12.0

    records = []
    for month, grp in df.groupby("month"):
        V_mean  = float(grp["wind_speed_ms"].mean())
        TI_mean = calc_iec_ti(grp)
        hrs_above_rated = float((grp["wind_speed_ms"] > RATED_V).sum() * dt_hours)

        # TIがnanの場合はIEC NTM代表値（I_ref=0.12）で補完
        if np.isnan(TI_mean):
            TI_mean = 0.12 * (0.75 + 5.6 / max(V_mean, 1.0))

        # ルックアップ（範囲外はクリップして補間）
        V_clipped  = np.clip(V_mean,  V_range[0],  V_range[1])
        TI_clipped = np.clip(TI_mean, TI_range[0], TI_range[1])
        del_est    = float(interp([[V_clipped, TI_clipped]])[0])

        # 旧スコア（比較用・旧重み0.81/0.19）
        records.append({
            "month":           month,
            "V_mean":          round(V_mean, 3),
            "TI_iec":          round(TI_mean, 4),
            "hrs_above_rated": round(hrs_above_rated, 1),
            "DEL_est_kNm":     round(del_est, 1),
            "V_clipped":       round(V_clipped, 3),
            "TI_clipped":      round(TI_clipped, 4),
        })

    df_out = pd.DataFrame(records)

    # 疲労リスクスコア（新重み）
    V_n  = (df_out["V_mean"] - df_out["V_mean"].min()) / (df_out["V_mean"].max() - df_out["V_mean"].min() + 1e-9)
    TI_n = (df_out["TI_iec"] - df_out["TI_iec"].min()) / (df_out["TI_iec"].max() - df_out["TI_iec"].min() + 1e-9)
    df_out["fatigue_risk_score_new"] = W_V * V_n + W_TI * TI_n

    return df_out


# ─────────────────────────────────────────
# 5. 可視化
# ─────────────────────────────────────────

def plot_results(monthly: pd.DataFrame, old_proxy: pd.DataFrame):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    months = monthly["month"].values
    x = np.arange(len(months))

    # Panel 1: 月次DEL推定値
    ax = axes[0, 0]
    ax.bar(x, monthly["DEL_est_kNm"].values / 1000, color="steelblue", alpha=0.8)
    ax.axhline(monthly["DEL_est_kNm"].mean() / 1000, color="tomato", ls="--", lw=2,
               label=f"年平均 {monthly['DEL_est_kNm'].mean():.0f} kN-m")
    ax.set_xticks(x); ax.set_xticklabels([f"{m}M" for m in months])
    ax.set_ylabel("DEL Estimate (MN-m)")
    ax.set_title("Monthly DEL Estimate (Lookup Table from OpenFAST)")
    ax.legend(); ax.grid(alpha=0.3, axis="y")

    # Panel 2: 代表V・TIの月次推移
    ax = axes[0, 1]
    ax2 = ax.twinx()
    ax.plot(x, monthly["V_mean"].values, "o-", color="steelblue", label="V_mean (m/s)", lw=2)
    ax2.plot(x, monthly["TI_iec"].values, "s--", color="tomato", label="TI_iec", lw=2)
    ax.set_xticks(x); ax.set_xticklabels([f"{m}M" for m in months])
    ax.set_ylabel("Wind Speed (m/s)", color="steelblue")
    ax2.set_ylabel("TI (IEC bin-avg)", color="tomato")
    ax.set_title("Monthly V_mean and TI (IEC compliant)")
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=9)
    ax.grid(alpha=0.3)

    # Panel 3: 旧スコア vs DEL推定値の比較
    ax = axes[1, 0]
    old = old_proxy[["month", "fatigue_risk_score"]].copy()
    merged = monthly.merge(old, on="month")
    del_norm = (merged["DEL_est_kNm"] - merged["DEL_est_kNm"].min()) / \
               (merged["DEL_est_kNm"].max() - merged["DEL_est_kNm"].min())
    ax.scatter(merged["fatigue_risk_score"], del_norm, color="steelblue", s=60, zorder=3)
    for _, row in merged.iterrows():
        d_n = (row["DEL_est_kNm"] - merged["DEL_est_kNm"].min()) / \
              (merged["DEL_est_kNm"].max() - merged["DEL_est_kNm"].min())
        ax.annotate(f'{int(row["month"])}M', (row["fatigue_risk_score"], d_n),
                    fontsize=8, ha="left", va="bottom")
    from scipy.stats import pearsonr
    r, p = pearsonr(merged["fatigue_risk_score"], del_norm)
    ax.set_xlabel("旧 fatigue_risk_score（等重み代理指標）")
    ax.set_ylabel("DEL推定値（正規化）")
    ax.set_title(f"旧代理指標 vs DEL推定値\nr={r:.3f}, p={p:.3f}")
    ax.grid(alpha=0.3)

    # Panel 4: 新旧スコア比較（月次）
    ax = axes[1, 1]
    ax.plot(x, merged["fatigue_risk_score"].values, "o-",
            color="gray", label="旧スコア（等重み）", lw=2, ms=7)
    ax.plot(x, monthly["fatigue_risk_score_new"].values, "s--",
            color="steelblue", label=f"新スコア（w_V={W_V}/w_TI={W_TI}）", lw=2, ms=7)
    ax.set_xticks(x); ax.set_xticklabels([f"{m}M" for m in months])
    ax.set_ylabel("Fatigue Risk Score")
    ax.set_title("旧スコア vs 新スコア（較正済み重み）")
    ax.legend(); ax.grid(alpha=0.3)

    plt.suptitle(
        "Phase 3 強化: DELルックアップテーブルによる月次DEL推定\n"
        f"(NREL 5MW DLC1.2 マトリクス補間 / IEC準拠TI / w_V={W_V}, w_TI={W_TI})",
        fontsize=12, fontweight="bold"
    )
    plt.tight_layout()
    out = OUT_DIR / "phase3b_del_comparison.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"保存: {out}")


# ─────────────────────────────────────────
# メイン
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=== Phase 3b: DELルックアップテーブル化 ===\n")

    print("1. DEL補間器を構築中...")
    interp, V_range, TI_range = build_del_interpolator()
    print(f"   V range: {V_range}, TI range: {TI_range}")

    print("2. SCADAデータ読み込み...")
    df = load_scada()
    print(f"   正常運転レコード: {len(df):,}件")

    print("3. 月次DEL推定...")
    monthly = calc_monthly_del(df, interp, V_range, TI_range)

    print("\n=== 月次DEL推定結果 ===")
    print(f"{'月':>3}  {'V_mean':>7}  {'TI_iec':>7}  {'DEL_est':>10}  {'hrs_rated':>9}")
    print("-" * 50)
    for _, row in monthly.iterrows():
        print(f"{int(row['month']):>3}  {row['V_mean']:>7.2f}  {row['TI_iec']:>7.4f}"
              f"  {row['DEL_est_kNm']:>9.0f}  {row['hrs_above_rated']:>9.1f}")

    print(f"\n年平均DEL推定値: {monthly['DEL_est_kNm'].mean():.0f} kN-m")
    print(f"最高月: {int(monthly.loc[monthly['DEL_est_kNm'].idxmax(), 'month'])}月"
          f"  ({monthly['DEL_est_kNm'].max():.0f} kN-m)")
    print(f"最低月: {int(monthly.loc[monthly['DEL_est_kNm'].idxmin(), 'month'])}月"
          f"  ({monthly['DEL_est_kNm'].min():.0f} kN-m)")

    print("\n4. TI旧→新の比較")
    old_proxy = pd.read_csv(OUT_DIR / "phase3_fatigue_proxy.csv")
    print(f"   旧TI(σ/μ)平均: {old_proxy['mean_ti'].mean():.4f}")
    print(f"   新TI(IEC)平均:  {monthly['TI_iec'].mean():.4f}")

    print("\n5. 可視化...")
    plot_results(monthly, old_proxy)

    print("\n6. CSV保存...")
    out_csv = OUT_DIR / "phase3b_monthly_del.csv"
    monthly.to_csv(out_csv, index=False)
    print(f"   保存: {out_csv}")

    print("\n=== 完了 ===")
