"""
A-9 検証: 月次集計点補間（現行実装）vs 10分レコード別補間（§3.7 記述）の DEL 差
=================================================================================
目的:
  Paper 2 §3.7 は「各10分レコードに bilinear 補間 → 月次集計」と記述するが、
  実装（phase3_scada/phase3_penmanshiel.py calc_monthly_del_penmanshiel）は
  月次集計点 (V_mean, TI_median) で一回だけ補間している。
  DEL は V に対して凸のため、Jensen の不等式により
  DEL(E[V]) <= E[DEL(V)] （集計点補間はレコード別平均を過小評価）が予想される。
  本スクリプトはそのバイアス量を実データで定量化する。

再現条件（phase3_penmanshiel.py と同一）:
  - QC: 0 <= V <= 25, -50 <= P <= 2152.5, V >= 3.5, P >= 0, 0.005 <= TI <= 0.50
  - TI = wind_speed_std / wind_speed（V > 0.5 のみ）
  - DEL マトリクス: del_matrix_mm82.csv (8V x 5TI, DEL_mean)
  - 補間: RegularGridInterpolator(linear), 集計点は clip して評価
  - レコード別も同じ clip（グリッド範囲 [4,18]x[0.08,0.20] へ）を適用

実行: python3 tools/reference_audit/a9_jensen_bias_check.py  （リポジトリルートから）
出力: tools/reference_audit/a9_jensen_bias_results.csv + 標準出力サマリ
作成: Claude Code（研究補助者）2026-07-02
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator

ROOT = Path(__file__).resolve().parents[2]
SCADA_DIR = ROOT / "data" / "penmanshiel" / "scada_2020"
DEL_MATRIX = ROOT / "phase5_openfast_shm" / "openfast_cases" / "results" / "del_matrix_mm82.csv"
MONTHLY_CSV = ROOT / "phase3_scada" / "penmanshiel_monthly_del.csv"
OUT_CSV = Path(__file__).parent / "a9_jensen_bias_results.csv"

CUT_IN_V = 3.5
CUT_OUT_V = 25.0
RATED_P_KW = 2050.0

TURBINES = ["01", "02", "04", "05", "06"]


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


def load_turbine(tid: str) -> pd.DataFrame:
    files = list(SCADA_DIR.glob(f"Turbine_Data_Penmanshiel_{tid}_*.csv"))
    assert len(files) == 1, f"T{tid}: expected 1 file, got {files}"
    df = pd.read_csv(files[0], skiprows=9, low_memory=False)
    df.columns = [c.lstrip("# ").strip() for c in df.columns]
    df["timestamp"] = pd.to_datetime(df["Date and time"])
    df["month"] = df["timestamp"].dt.month
    out = pd.DataFrame({
        "month": df["month"],
        "V": pd.to_numeric(df["Wind speed (m/s)"], errors="coerce"),
        "V_std": pd.to_numeric(df["Wind speed, Standard deviation (m/s)"], errors="coerce"),
        "P": pd.to_numeric(df["Power (kW)"], errors="coerce"),
    })
    out["TI"] = np.where(out["V"] > 0.5, out["V_std"] / out["V"], np.nan)
    # QC（phase3_penmanshiel.py apply_qc_filter と同一）
    out = out[
        (out["V"] >= 0) & (out["V"] <= CUT_OUT_V)
        & out["P"].between(-50, RATED_P_KW * 1.05)
        & (out["V"] >= CUT_IN_V) & (out["P"] >= 0)
        & out["TI"].between(0.005, 0.50, inclusive="both")
    ].copy()
    return out


def main():
    interp, v_rng, ti_rng = build_interpolator()
    ref = pd.read_csv(MONTHLY_CSV)
    rows = []
    for tid in TURBINES:
        df = load_turbine(tid)
        for month, grp in df.groupby("month"):
            # 方法B（現行実装）: 月次集計点で一回補間
            v_mean = float(grp["V"].mean())
            ti_med = float(grp["TI"].median())
            v_c = np.clip(v_mean, *v_rng)
            ti_c = np.clip(ti_med, *ti_rng)
            del_b = float(interp([[v_c, ti_c]])[0])
            # 方法A（§3.7 記述）: レコード別補間 → 月次平均
            v_rec = np.clip(grp["V"].to_numpy(), *v_rng)
            ti_rec = np.clip(grp["TI"].to_numpy(), *ti_rng)
            del_a = float(interp(np.column_stack([v_rec, ti_rec])).mean())
            # 公表値（penmanshiel_monthly_del.csv）との照合
            pub = ref[(ref["turbine_id"] == f"T{tid}") & (ref["month"] == month)]
            del_pub = float(pub["DEL_est_kNm"].iloc[0]) if len(pub) else np.nan
            rows.append({
                "turbine": f"T{tid}", "month": month, "n_records": len(grp),
                "DEL_pointinterp_B": round(del_b, 1),
                "DEL_published": del_pub,
                "DEL_perrecord_A": round(del_a, 1),
                "bias_pct_B_vs_A": round((del_b - del_a) / del_a * 100, 2),
            })
    res = pd.DataFrame(rows)
    res.to_csv(OUT_CSV, index=False)

    print("=== 方法B 再現性チェック（公表値との差, %）===")
    res["repro_diff_pct"] = (res["DEL_pointinterp_B"] - res["DEL_published"]) / res["DEL_published"] * 100
    print(f"max |diff| = {res['repro_diff_pct'].abs().max():.2f}%")

    print("\n=== T01 月別（B=集計点補間 / A=レコード別補間）===")
    print(res[res["turbine"] == "T01"][
        ["month", "DEL_pointinterp_B", "DEL_perrecord_A", "bias_pct_B_vs_A"]
    ].to_string(index=False))

    print("\n=== タービン別 年間平均 ===")
    for tid, grp in res.groupby("turbine"):
        b = grp["DEL_pointinterp_B"].mean()
        a = grp["DEL_perrecord_A"].mean()
        print(f"{tid}: B(現行) {b:,.0f}  A(レコード別) {a:,.0f}  bias {(b-a)/a*100:+.2f}%")

    print("\n=== 全体サマリ ===")
    print(f"月次バイアス: mean {res['bias_pct_B_vs_A'].mean():+.2f}%  "
          f"range [{res['bias_pct_B_vs_A'].min():+.2f}%, {res['bias_pct_B_vs_A'].max():+.2f}%]")


if __name__ == "__main__":
    main()
