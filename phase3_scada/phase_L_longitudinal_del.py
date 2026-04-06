"""
phase_L_longitudinal_del.py
Phase L: Penmanshiel T01 縦断 DEL トレンド（2016-2021）

目的: 各年の疲労荷重（DEL推定値）の経年変化を追跡する。
     Phase K の縦断パワーカーブ（Cp_max増加傾向）と対比し、
     「性能は向上しているのに荷重は変化しているか」を確認する。

入力:
  data/penmanshiel/scada_{year}/Turbine_Data_Penmanshiel_01_*.csv  (2016-2021)
  phase5_openfast_shm/openfast_cases/results/del_matrix_mm82.csv

出力:
  phase3_scada/longitudinal_del_T01.csv      ... 年次・月次DEL集計
  phase3_scada/longitudinal_del_trend.png    ... 年次DELトレンド図
  phase3_scada/longitudinal_del_summary.md   ... サマリーレポート
"""

from pathlib import Path
import pandas as pd
import numpy as np
from scipy.interpolate import RegularGridInterpolator
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

REPO      = Path(__file__).parent.parent
SCADA_DIR = REPO / "data/penmanshiel"
OUT_DIR   = REPO / "phase3_scada"
DEL_CSV   = REPO / "phase5_openfast_shm/openfast_cases/results/del_matrix_mm82.csv"

CUT_IN_V  = 3.5
CUT_OUT_V = 25.0
W_V       = 0.7253
W_TI      = 0.2747

YEARS = [2016, 2017, 2018, 2019, 2020, 2021]


# ── DEL matrix 補間器 ─────────────────────────────────────────────────────────
def build_interpolator(del_csv):
    df = pd.read_csv(del_csv)
    V_vals  = sorted(df["V"].unique())
    TI_vals = sorted(df["TI"].unique())
    grid = np.zeros((len(V_vals), len(TI_vals)))
    for i, v in enumerate(V_vals):
        for j, ti in enumerate(TI_vals):
            row = df[(df["V"] == v) & (df["TI"] == ti)]
            grid[i, j] = row["DEL_mean"].values[0] if len(row) > 0 else np.nan
    interp = RegularGridInterpolator(
        (V_vals, TI_vals), grid,
        method="linear", bounds_error=False, fill_value=None
    )
    return interp, V_vals, TI_vals

def lookup_del(interp, V_vals, TI_vals, v, ti):
    v_clip  = float(np.clip(v,  min(V_vals),  max(V_vals)))
    ti_clip = float(np.clip(ti, min(TI_vals), max(TI_vals)))
    result = interp([[v_clip, ti_clip]])
    return float(np.asarray(result).ravel()[0])


# ── SCADA 読み込み ────────────────────────────────────────────────────────────
def find_t01_csv(year):
    d = SCADA_DIR / f"scada_{year}"
    if not d.exists():
        return None
    matches = sorted(d.glob("Turbine_Data_Penmanshiel_01_*.csv"))
    return matches[0] if matches else None


def load_scada(year):
    path = find_t01_csv(year)
    if path is None:
        return None, None

    df = pd.read_csv(
        path, skiprows=10, header=None,
        na_values=["NaN", "nan"],
        low_memory=False,
    )
    if df.shape[1] < 3:
        return None, None

    df.columns = ["datetime"] + [f"c{i}" for i in range(1, df.shape[1])]
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df = df.dropna(subset=["datetime"])
    df["V"]    = pd.to_numeric(df["c1"], errors="coerce")
    df["V_std"] = pd.to_numeric(df["c2"], errors="coerce")
    df["TI"] = df["V_std"] / df["V"]

    # QC
    df = df[df["V"] >= CUT_IN_V]
    df = df[df["V"] <= CUT_OUT_V]
    df = df[df["TI"] > 0]
    df = df[df["TI"] < 1.0]
    df = df.dropna(subset=["V", "TI"])

    # データ期間（実際の最初と最後の日付）
    period = (df["datetime"].min(), df["datetime"].max())
    return df, period


# ── 月次DEL計算 ───────────────────────────────────────────────────────────────
def compute_monthly_del(df, year, interp, V_vals, TI_vals):
    df = df.copy()
    df["year"]  = df["datetime"].dt.year
    df["month"] = df["datetime"].dt.month

    records = []
    for month in range(1, 13):
        sub = df[df["month"] == month]
        if len(sub) < 10:
            continue
        v_mean  = sub["V"].mean()
        ti_med  = sub["TI"].median()
        del_est = lookup_del(interp, V_vals, TI_vals, v_mean, ti_med)
        records.append({
            "year": year,
            "month": month,
            "n_records": len(sub),
            "V_mean": round(v_mean, 3),
            "TI_med": round(ti_med, 4),
            "DEL_est_kNm": round(del_est, 1),
        })
    return pd.DataFrame(records)


# ── メイン ────────────────────────────────────────────────────────────────────
print("=== Phase L: 縦断 DEL トレンド（T01, 2016-2021） ===")
print(f"DEL matrix: {DEL_CSV.name}")

interp, V_vals, TI_vals = build_interpolator(DEL_CSV)

all_monthly = []
annual_rows = []

for year in YEARS:
    df, period = load_scada(year)
    if df is None:
        print(f"  {year}: データなし")
        continue

    monthly = compute_monthly_del(df, year, interp, V_vals, TI_vals)
    if monthly.empty:
        print(f"  {year}: 有効月なし")
        continue

    all_monthly.append(monthly)

    # 年次集計（12ヶ月分の月平均）
    v_annual  = df["V"].mean()
    ti_annual = df["TI"].median()
    del_annual = monthly["DEL_est_kNm"].mean()
    n_months   = len(monthly)
    n_records  = len(df)

    start_str = period[0].strftime("%Y-%m-%d") if period else "?"
    end_str   = period[1].strftime("%Y-%m-%d") if period else "?"

    annual_rows.append({
        "year": year,
        "n_months": n_months,
        "n_records": n_records,
        "period_start": start_str,
        "period_end": end_str,
        "V_mean": round(v_annual, 3),
        "TI_med": round(ti_annual, 4),
        "DEL_annual_kNm": round(del_annual, 1),
    })
    print(f"  {year}: V={v_annual:.2f} m/s  TI={ti_annual:.3f}  "
          f"DEL={del_annual:.0f} kN·m  ({n_months}ヶ月)")

all_monthly_df = pd.concat(all_monthly, ignore_index=True)
annual_df      = pd.DataFrame(annual_rows)

# ── CSV 保存 ──────────────────────────────────────────────────────────────────
out_csv = OUT_DIR / "longitudinal_del_T01.csv"
all_monthly_df.to_csv(out_csv, index=False)
print(f"\n月次CSV保存: {out_csv}")

# ── プロット ──────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(10, 12))

# (1) 年次DELトレンド
ax = axes[0]
ax.bar(annual_df["year"], annual_df["DEL_annual_kNm"], color="steelblue", alpha=0.8)
ax.plot(annual_df["year"], annual_df["DEL_annual_kNm"], "o-", color="navy", linewidth=2)
ax.set_xlabel("Year")
ax.set_ylabel("Annual mean DEL (kN·m)")
ax.set_title("Phase L: T01 Annual DEL Trend (MM82 proxy, 2016-2021)")
ax.set_xticks(annual_df["year"])
for _, row in annual_df.iterrows():
    ax.annotate(f"{row['DEL_annual_kNm']:.0f}",
                xy=(row["year"], row["DEL_annual_kNm"]),
                ha="center", va="bottom", fontsize=9)

# (2) 月次DEL時系列（全年）
ax = axes[1]
colors = plt.cm.viridis(np.linspace(0, 1, len(YEARS)))
year_color = {y: c for y, c in zip(YEARS, colors)}
for year in YEARS:
    sub = all_monthly_df[all_monthly_df["year"] == year]
    if sub.empty:
        continue
    ax.plot(sub["month"], sub["DEL_est_kNm"],
            "o-", label=str(year), color=year_color.get(year, "gray"), linewidth=1.5)
ax.set_xlabel("Month")
ax.set_ylabel("DEL estimate (kN·m)")
ax.set_title("Monthly DEL by Year")
ax.set_xticks(range(1, 13))
ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun",
                     "Jul","Aug","Sep","Oct","Nov","Dec"])
ax.legend(loc="upper right", fontsize=8)

# (3) 年次 V_mean / TI_med トレンド（DEL変動の要因確認）
ax = axes[2]
ax2 = ax.twinx()
l1 = ax.plot(annual_df["year"], annual_df["V_mean"], "s-",
             color="tomato", label="V_mean (m/s)", linewidth=2)
l2 = ax2.plot(annual_df["year"], annual_df["TI_med"], "^--",
              color="green", label="TI_med", linewidth=2)
ax.set_xlabel("Year")
ax.set_ylabel("V_mean (m/s)", color="tomato")
ax2.set_ylabel("TI_med", color="green")
ax.set_title("Annual V_mean and TI_med (T01)")
ax.set_xticks(annual_df["year"])
lines = l1 + l2
ax.legend(lines, [l.get_label() for l in lines], loc="upper left", fontsize=8)

plt.tight_layout()
out_png = OUT_DIR / "longitudinal_del_trend.png"
plt.savefig(out_png, dpi=150, bbox_inches="tight")
plt.close()
print(f"図保存: {out_png}")

# ── サマリーレポート ──────────────────────────────────────────────────────────
del_min_y = annual_df["DEL_annual_kNm"].min()
del_max_y = annual_df["DEL_annual_kNm"].max()
del_change = annual_df["DEL_annual_kNm"].iloc[-1] - annual_df["DEL_annual_kNm"].iloc[0]
del_pct    = del_change / annual_df["DEL_annual_kNm"].iloc[0] * 100

summary_lines = [
    "# Phase L: Penmanshiel T01 縦断 DEL トレンド",
    "",
    "## データ概要",
    f"- タービン: T01（Senvion MM82, 2.05 MW, D=82m）",
    f"- 期間: {annual_df['period_start'].iloc[0]} 〜 {annual_df['period_end'].iloc[-1]}",
    f"- DEL matrix: MM82プロキシ（Phase I, 240ケース）",
    f"- 較正重み: w_V={W_V}, w_TI={W_TI}",
    "",
    "## 年次DEL集計",
    "",
    "| 年 | 期間 | V_mean (m/s) | TI_med | DEL (kN·m) | ヶ月数 |",
    "|:---:|---|:---:|:---:|---:|:---:|",
]
for _, row in annual_df.iterrows():
    summary_lines.append(
        f"| {int(row['year'])} | {row['period_start']}〜{row['period_end']} "
        f"| {row['V_mean']:.2f} | {row['TI_med']:.3f} "
        f"| {row['DEL_annual_kNm']:.0f} | {int(row['n_months'])} |"
    )

summary_lines += [
    "",
    "## 主要発見",
    f"- DEL範囲（年平均）: {del_min_y:.0f} 〜 {del_max_y:.0f} kN·m",
    f"- 初年→最終年変化: {del_change:+.0f} kN·m ({del_pct:+.1f}%)",
    "",
    "## Phase K（Cpトレンド）との比較",
    "- Phase K: T01の Cp_max は 2017→2020 で増加傾向（0.4275→0.4513）— 劣化なし",
    "- Phase L: DELトレンドと気象条件（V_mean/TI）の変動を対比し、",
    "  荷重増加が「風況の年変動」によるものか「機体状態の変化」によるものかを判断する材料とする。",
    "",
    "## 注意事項",
    "- 2016年は2016-06-06から（半年分）のため年平均DELは過小評価の可能性",
    "- 2021年は2021-07-01まで（半年分）のため同様",
    "- DELは絶対値ではなく相対トレンドの比較に限定（翼型プロキシ使用）",
]

summary_text = "\n".join(summary_lines) + "\n"
out_md = OUT_DIR / "longitudinal_del_summary.md"
out_md.write_text(summary_text, encoding="utf-8")
print(f"サマリー保存: {out_md}")

print("\n=== Phase L 完了 ===")
print(annual_df[["year","V_mean","TI_med","DEL_annual_kNm","n_months"]].to_string(index=False))
