"""
Penmanshiel サイト DEL 推定 v2（レコード別補間・案b 実装）
==========================================================
Paper 2 v10.0 用。§3.7 の記述どおり「QC 通過の各10分レコードに bilinear 補間
→ 月次集計」を実装する。旧実装（月次集計点で一回補間）との差は A-9 監査
（tools/reference_audit/paper123_consistency_audit_2026-07-02.md）で定量化済み。

確定した集計定義（2026-07-03 himinさん 承認、D1〜D3）:
  D1: 月次（タービン別）= 当月 QC 通過レコードの DEL 単純平均。
      フリート月次（Table 12）= 5 タービンの月次値の単純平均（タービン等価重み）。
      年間 = 利用可能な月次値の単純平均（月等価重み）。
  D2: グリッド範囲外レコードは補間前に clip する（V → [4, 18] m/s、TI → [0.08, 0.20]）。
      カットイン 3.5 m/s とグリッド下限 4 m/s の間のレコードは V=4 として評価される。
  D3: 旧実装（月次集計点補間）の値も参照列として併記し、頑健性注記（§4.6.4）に使用。

QC（旧実装 phase3_penmanshiel.py と同一）:
  0 <= V <= 25, -50 <= P <= 2152.5, V >= 3.5, P >= 0, 0.005 <= TI <= 0.50

出力:
  penmanshiel_monthly_del_v2.csv    … タービン別月次（2020, T01/T02/T04/T05/T06）
  penmanshiel_fleet_monthly_v2.csv  … フリート月次（Table 12 用）
  longitudinal_del_T01_v2.csv       … T01 月次（2016-2021）
  longitudinal_annual_del_v2.csv    … T01 年次（Table 14 用）
  fig_penmanshiel_monthly_del_mm82.png / fig_longitudinal_combined.png（再生成）

作成: Claude Code（研究補助者）2026-07-03
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "penmanshiel"
OUT_DIR = Path(__file__).parent
FIG_DIR = ROOT / "phase5_openfast_shm" / "openfast_cases" / "results"
DEL_MATRIX = FIG_DIR / "del_matrix_mm82.csv"

CUT_IN_V = 3.5
CUT_OUT_V = 25.0
RATED_P_KW = 2050.0
W_V, W_TI = 0.725, 0.275  # Paper 2 §4.5 較正済み重み（fatigue_risk_score 用）

FLEET = ["01", "02", "04", "05", "06"]
FLEET_YEAR = 2020
LONGI_TID = "01"
LONGI_YEARS = [2016, 2017, 2018, 2019, 2020, 2021]


def build_interpolator():
    df = pd.read_csv(DEL_MATRIX)
    v_list = sorted(df["V"].unique())
    ti_list = sorted(df["TI"].unique())
    matrix = np.zeros((len(v_list), len(ti_list)))
    for i, v in enumerate(v_list):
        for j, ti in enumerate(ti_list):
            row = df[(df["V"] == v) & (df["TI"].round(3) == round(ti, 3))]
            matrix[i, j] = row["DEL_mean"].values[0]
    interp = RegularGridInterpolator(
        (np.array(v_list), np.array(ti_list)), matrix,
        method="linear", bounds_error=False, fill_value=None,
    )
    return interp, (min(v_list), max(v_list)), (min(ti_list), max(ti_list))


def load_turbine_year(tid: str, year: int) -> pd.DataFrame:
    """1タービン・1年分の 10 分値を読み込み、QC を適用して返す。"""
    files = list((DATA / f"scada_{year}").glob(f"Turbine_Data_Penmanshiel_{tid}_*.csv"))
    assert len(files) == 1, f"T{tid} {year}: expected 1 file, got {len(files)}"
    df = pd.read_csv(files[0], skiprows=9, low_memory=False)
    df.columns = [c.lstrip("# ").strip() for c in df.columns]
    out = pd.DataFrame({
        "timestamp": pd.to_datetime(df["Date and time"]),
        "V": pd.to_numeric(df["Wind speed (m/s)"], errors="coerce"),
        "V_std": pd.to_numeric(df["Wind speed, Standard deviation (m/s)"], errors="coerce"),
        "P": pd.to_numeric(df["Power (kW)"], errors="coerce"),
    })
    out["month"] = out["timestamp"].dt.month
    out["TI"] = np.where(out["V"] > 0.5, out["V_std"] / out["V"], np.nan)
    out = out[
        (out["V"] >= 0) & (out["V"] <= CUT_OUT_V)
        & out["P"].between(-50, RATED_P_KW * 1.05)
        & (out["V"] >= CUT_IN_V) & (out["P"] >= 0)
        & out["TI"].between(0.005, 0.50, inclusive="both")
    ].copy()
    return out


def monthly_del(df: pd.DataFrame, interp, v_rng, ti_rng) -> pd.DataFrame:
    """月次 DEL（レコード別補間＝主法、集計点補間＝参照列）を算出する。"""
    records = []
    for month, grp in df.groupby("month"):
        # 主法: レコード別補間 → 月平均（D2: 補間前に clip）
        v_rec = np.clip(grp["V"].to_numpy(), *v_rng)
        ti_rec = np.clip(grp["TI"].to_numpy(), *ti_rng)
        del_pr = float(interp(np.column_stack([v_rec, ti_rec])).mean())
        # 参照: 旧実装（月次集計点で一回補間）
        v_mean = float(grp["V"].mean())
        ti_med = float(grp["TI"].median())
        del_pt = float(interp([[np.clip(v_mean, *v_rng), np.clip(ti_med, *ti_rng)]])[0])
        records.append({
            "month": int(month),
            "n_records": len(grp),
            "V_mean": round(v_mean, 3),
            "TI_direct_med": round(ti_med, 4),
            "TI_direct_std": round(float(grp["TI"].std()), 4),
            "DEL_est_kNm": round(del_pr, 1),
            "DEL_pointinterp_kNm": round(del_pt, 1),
        })
    return pd.DataFrame(records).sort_values("month").reset_index(drop=True)


def main():
    interp, v_rng, ti_rng = build_interpolator()

    # ── 1) フリート 2020（Table 12/13 用）─────────────────────
    monthly_all = []
    for tid in FLEET:
        df = load_turbine_year(tid, FLEET_YEAR)
        m = monthly_del(df, interp, v_rng, ti_rng)
        m.insert(0, "turbine_id", f"T{tid}")
        # fatigue_risk_score（旧実装と同一式・タービン内 min-max、V/TI ベースのため方法非依存）
        v_n = (m["V_mean"] - m["V_mean"].min()) / (m["V_mean"].max() - m["V_mean"].min() + 1e-9)
        ti_n = (m["TI_direct_med"] - m["TI_direct_med"].min()) / (
            m["TI_direct_med"].max() - m["TI_direct_med"].min() + 1e-9)
        m["fatigue_risk_score"] = W_V * v_n + W_TI * ti_n
        monthly_all.append(m)
    monthly_all = pd.concat(monthly_all, ignore_index=True)
    monthly_all.to_csv(OUT_DIR / "penmanshiel_monthly_del_v2.csv", index=False)

    # フリート月次（D1: タービン別月次値の単純平均）
    fleet = monthly_all.groupby("month").agg(
        V_mean=("V_mean", "mean"),
        TI_med=("TI_direct_med", "mean"),
        DEL_est_kNm=("DEL_est_kNm", "mean"),
        DEL_pointinterp_kNm=("DEL_pointinterp_kNm", "mean"),
        n_turbines=("turbine_id", "count"),
    ).round({"V_mean": 1, "TI_med": 3, "DEL_est_kNm": 0, "DEL_pointinterp_kNm": 0}).reset_index()
    fleet.to_csv(OUT_DIR / "penmanshiel_fleet_monthly_v2.csv", index=False)

    # ── 2) 縦断 T01 2016-2021（Table 14 用）───────────────────
    longi_rows, annual_rows = [], []
    for year in LONGI_YEARS:
        df = load_turbine_year(LONGI_TID, year)
        m = monthly_del(df, interp, v_rng, ti_rng)
        m.insert(0, "year", year)
        longi_rows.append(m)
        annual_rows.append({
            "year": year,
            "n_months": len(m),
            "V_mean_records": round(float(df["V"].mean()), 2),
            "TI_med_records": round(float(df["TI"].median()), 4),
            "DEL_annual_kNm": round(float(m["DEL_est_kNm"].mean()), 0),
            "DEL_annual_pointinterp_kNm": round(float(m["DEL_pointinterp_kNm"].mean()), 0),
        })
    longi = pd.concat(longi_rows, ignore_index=True)
    longi.to_csv(OUT_DIR / "longitudinal_del_T01_v2.csv", index=False)
    annual = pd.DataFrame(annual_rows)
    annual.to_csv(OUT_DIR / "longitudinal_annual_del_v2.csv", index=False)

    # ── 3) 図の再生成（旧スタイル踏襲）─────────────────────────
    months_lbl = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    mstat = monthly_all.groupby("month")["DEL_est_kNm"].agg(["mean", "std"]).reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(mstat["month"], mstat["mean"], yerr=mstat["std"], capsize=3,
                  color="#2196F3", alpha=0.85, edgecolor="white")
    bars[int(mstat["mean"].idxmax())].set_color("#F44336")
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(months_lbl)
    ax.set_ylabel("Estimated DEL (kN·m)")
    ax.set_title("Penmanshiel Wind Farm — Monthly Mean DEL (MM82 Proxy, per-record interpolation)\n"
                 "5 Turbines (T01-T06), 2020, Error bars = inter-turbine σ")
    ax.set_ylim(0, ax.get_ylim()[1] * 1.15)
    for bar, val in zip(bars, mstat["mean"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
                f"{val:.0f}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_penmanshiel_monthly_del_mm82.png", dpi=200)
    plt.close()

    ann_summary = pd.read_csv(OUT_DIR / "longitudinal_annual_summary.csv")  # Cp_max（方法非依存・既存）
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    ax1.bar(annual["year"], annual["DEL_annual_kNm"], color="#2196F3", alpha=0.8, width=0.6)
    ax1.set_ylabel("Annual Mean DEL (kN·m)")
    ax1.set_title("Penmanshiel T01 — Longitudinal Trends (2016–2021, per-record interpolation)")
    for _, row in annual.iterrows():
        ax1.text(row["year"], row["DEL_annual_kNm"] + 20, f"{row['DEL_annual_kNm']:.0f}",
                 ha="center", fontsize=9)
    ax2.plot(ann_summary["year"], ann_summary["Cp_max"], "o-", color="#4CAF50",
             markersize=8, linewidth=2)
    ax2.set_ylabel("Cp_max")
    ax2.set_xlabel("Year")
    ax2.set_ylim(0.40, 0.46)
    for _, row in ann_summary.iterrows():
        ax2.text(row["year"], row["Cp_max"] + 0.002, f"{row['Cp_max']:.4f}",
                 ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig_longitudinal_combined.png", dpi=200)
    plt.close()

    # ── 4) 検証出力 ────────────────────────────────────────────
    print("=== Table 13 相当（2020 年間平均、レコード別）===")
    ann13 = monthly_all.groupby("turbine_id")["DEL_est_kNm"].mean().round(0)
    print(ann13.to_string())
    print("\n=== Table 12 相当（フリート月次）===")
    print(fleet[["month", "V_mean", "TI_med", "DEL_est_kNm"]].to_string(index=False))
    print("\n=== Table 14 相当（T01 縦断）===")
    print(annual.to_string(index=False))
    print("\n=== トレンド検証 ===")
    d17 = annual.loc[annual.year == 2017, "DEL_annual_kNm"].iloc[0]
    d20 = annual.loc[annual.year == 2020, "DEL_annual_kNm"].iloc[0]
    print(f"2017→2020: {d17:.0f} → {d20:.0f} kN·m ({(d20 - d17) / d17 * 100:+.1f}%)")
    print("\n=== 方法差（年間、point/per-record − 1）===")
    for _, r in annual.iterrows():
        diff = (r["DEL_annual_pointinterp_kNm"] / r["DEL_annual_kNm"] - 1) * 100
        print(f"{int(r['year'])}: {diff:+.1f}%")


if __name__ == "__main__":
    main()
