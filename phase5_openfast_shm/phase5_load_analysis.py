"""
Phase 5: ブレード荷重モデルによる疲労指標の物理的較正

目的:
    Phase 3で等重みとした疲労リスク代理指標（hrs_above_rated・mean_ti）に
    物理的な根拠を与える。

手法:
    OpenFAST本格シミュレーションの前段として、簡易解析モデルによって
    10分平均SCADA記録ごとにブレードフラップ方向DELプロキシを計算し、
    Phase 3指標との相関・重み較正を行う。

簡易荷重モデルの根拠（IEC 61400-1 / 標準疲労評価手法）:
    ブレードフラップ荷重の支配メカニズム:
    1. 平均荷重: M_flapwise ∝ ρ_air × A_rotor × V² × CT(V)
    2. 乱流変動: ΔM ∝ ∂M/∂V × σ_V = ∂M/∂V × V × TI
    3. 疲労損傷（SN則・Palmgren-Miner): D ∝ n_cycles × ΔM^m

    簡易化: fatigue_proxy_per_interval = (V/V_rated)^n × (1 + γ × TI)
    - n=3: 荷重(~V²) × 等価サイクル数(~V^1)の近似（IEC 61400-1 Annex H参考）
    - γ=5: 乱流による荷重変動増幅（Sutherland 1999 "On the Fatigue Analysis..."参考）

OpenFAST接続方針（Phase 5 将来実装）:
    1. NREL 5MW/DTU 10MW参照タービン入力ファイルを使用
    2. InflowWind: TurbSim生成の乱流風場（IEC Class B・η=0.14）
    3. AeroDyn15 + ElastoDyn によるブレード根元モーメント計算
    4. DEL算出: openfast_toolbox.postpro.DELs()
    5. 本スクリプトの (V, TI) → DEL マッピングと比較・較正

環境: conda env blade-phase3
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import curve_fit

REPO_ROOT = Path(__file__).parent.parent
RAW_DIR   = REPO_ROOT / "data" / "raw" / "scada"
OUT_DIR   = REPO_ROOT / "phase5_openfast_shm"
PHASE3_DIR = REPO_ROOT / "phase3_scada"
OUT_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────
# 1. タービン仕様（推定値）
# ─────────────────────────────────────────

# Kaggle T1.csv: トルコ・定格約3,600kW
# 類似機種: Siemens SWT-3.6-107 / Vestas V100-1.8MW... 3.6MWクラスから推定
TURBINE = {
    "rated_power_kw": 3600,
    "rated_wind_ms": 12.0,      # Phase 3パワーカーブから推定
    "cutin_wind_ms": 3.0,
    "cutout_wind_ms": 25.0,
    "rotor_radius_m": 52.0,     # 3.6MWクラス: 52〜54m（推定値）
    "hub_height_m": 80.0,
    "n_blades": 3,
    "air_density_kgm3": 1.225,
    # SN曲線パラメータ（GFRPブレード材料の典型値）
    "sn_exponent_m": 10.0,      # m=10 for fibre-reinforced composites (DNV GL 2016)
    # 簡易荷重モデルパラメータ
    "fatigue_wind_exponent_n": 3.0,  # 疲労損傷の風速指数
    "ti_amplification_gamma": 5.0,   # TI増幅係数（Sutherland 1999参考）
}


# ─────────────────────────────────────────
# 2. データ読み込み（Phase 3と同じ前処理）
# ─────────────────────────────────────────

def load_scada() -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / "T1.csv")
    df.columns = ["timestamp", "power_kw", "wind_speed_ms",
                  "theoretical_power_kwh", "wind_direction_deg"]
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%d %m %Y %H:%M")
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["month"] = df["timestamp"].dt.month

    # 物理異常値除去
    df = df[(df["power_kw"] >= 0) & (df["power_kw"] <= 3600)]
    df = df[(df["wind_speed_ms"] >= 0) & (df["wind_speed_ms"] <= 30)]

    # カーテイルメント除去
    curtailment_mask = (
        (df["theoretical_power_kwh"] > 0) &
        (df["power_kw"] / (df["theoretical_power_kwh"] + 1e-6) < 0.30) &
        (df["wind_speed_ms"] > 4.0)
    )
    df = df[~curtailment_mask].copy()
    print(f"SCADA前処理後: {len(df)}レコード")
    return df


# ─────────────────────────────────────────
# 3. 簡易ブレード荷重モデル
# ─────────────────────────────────────────

def calc_ct_curve(v: np.ndarray, v_rated: float) -> np.ndarray:
    """
    簡易スラスト係数 CT(V)。

    定格以下: CT ≈ 0.80（高揚力・低可変ピッチ）
    定格以上: CT ≈ CT_rated × (V_rated/V)²（ピッチ制御でスラスト一定化）
    カットイン以下・カットアウト以上: CT = 0
    """
    ct = np.where(v < 3.0, 0.0,
         np.where(v <= v_rated, 0.80,
                  0.80 * (v_rated / (v + 1e-9))**2))
    return ct


def calc_blade_load_index(v: np.ndarray, ti: np.ndarray, turbine: dict) -> np.ndarray:
    """
    10分間隔レコードごとの簡易ブレード疲労荷重指数を計算。

    定式:
        I_fatigue(V, TI) = (V / V_rated)^n × CT(V) × (1 + γ × TI)

    - 第1項: 空力荷重の風速依存性（V^n × CT(V)）
    - 第2項: 乱流による荷重変動増幅 (1 + γ × TI)
      → TI=0.14（IEC B級）時: 増幅率 = 1 + 5×0.14 = 1.70（70%増）

    単位は無次元（定格荷重に対する比）。
    """
    v_rated = turbine["rated_wind_ms"]
    n       = turbine["fatigue_wind_exponent_n"]
    gamma   = turbine["ti_amplification_gamma"]

    ct = calc_ct_curve(v, v_rated)
    i_load = (v / v_rated) ** n * ct * (1.0 + gamma * ti)
    return i_load


def assign_ti_to_records(df: pd.DataFrame) -> pd.DataFrame:
    """
    Phase 3と同じ方法でTIを各レコードに付与。
    風速ビン（1m/s幅, n>=5）ごとのσ/μを月別に計算。
    """
    df = df.copy()
    df["ti"] = 0.0
    df["ws_bin1"] = df["wind_speed_ms"].apply(lambda x: int(x))

    for month, grp in df.groupby("month"):
        sub = grp[grp["wind_speed_ms"] > 4.0].copy()
        bin_stats = sub.groupby("ws_bin1")["wind_speed_ms"].agg(["mean", "std", "count"])
        bin_stats = bin_stats[bin_stats["count"] >= 5]
        bin_stats["ti"] = bin_stats["std"] / (bin_stats["mean"] + 1e-9)
        ti_map = bin_stats["ti"].to_dict()
        df.loc[grp.index, "ti"] = grp["ws_bin1"].map(ti_map).fillna(0.0)

    return df


# ─────────────────────────────────────────
# 4. 月次DELプロキシ集計
# ─────────────────────────────────────────

def calc_monthly_del_proxy(df: pd.DataFrame, turbine: dict) -> pd.DataFrame:
    """
    月次DELプロキシを算出する。

    DEL ∝ (Σ I_fatigue^m)^(1/m) / N_ref^(1/m)
    ここでは m=10, N_ref=月総レコード数 で正規化。
    """
    df = df[df["wind_speed_ms"] > 0].copy()
    df = assign_ti_to_records(df)
    df["load_index"] = calc_blade_load_index(
        df["wind_speed_ms"].values, df["ti"].values, turbine
    )

    m = turbine["sn_exponent_m"]
    monthly_del = []

    for month, grp in df.groupby("month"):
        n_total = len(grp)
        # DEL: SN則による等価荷重
        # DEL = (Σ L_i^m / N_total)^(1/m)
        # ここではload_index^mの平均を取り、1/mべきを取る
        del_proxy = (grp["load_index"] ** m).mean() ** (1.0 / m)

        # 参照指標
        hrs_above_rated = (grp["wind_speed_ms"] > 12.0).sum() * (10 / 60)
        mean_ti = grp.loc[grp["wind_speed_ms"] > 4.0, "ti"].mean()
        mean_wind = grp["wind_speed_ms"].mean()

        monthly_del.append({
            "month": month,
            "del_proxy": del_proxy,
            "hrs_above_rated": hrs_above_rated,
            "mean_ti": float(mean_ti) if not pd.isna(mean_ti) else 0.0,
            "mean_wind_ms": mean_wind,
            "n_records": n_total,
        })

    mdf = pd.DataFrame(monthly_del)

    # 0-1正規化
    for col in ["del_proxy", "hrs_above_rated", "mean_ti"]:
        mn, mx = mdf[col].min(), mdf[col].max()
        mdf[f"{col}_norm"] = (mdf[col] - mn) / (mx - mn + 1e-9)

    return mdf


# ─────────────────────────────────────────
# 5. Phase 3代理指標との比較・重み較正
# ─────────────────────────────────────────

def compare_with_phase3(mdf: pd.DataFrame) -> dict:
    """
    DELプロキシと各Phase 3指標の相関を分析。
    重み較正: DELをターゲットとした回帰で最適重みを推定。
    """
    print("\n=== Phase 3指標 vs DELプロキシ 相関分析 ===")

    results = {}
    for col, label in [("hrs_above_rated_norm", "hrs_above_rated"),
                       ("mean_ti_norm", "mean_ti")]:
        r, p = stats.pearsonr(mdf[col], mdf["del_proxy_norm"])
        print(f"  {label} vs DEL proxy: r={r:.3f}, p={p:.3f}")
        results[f"r_{label}"] = r
        results[f"p_{label}"] = p

    # 重み較正: DEL = α × hrs_above_rated + β × mean_ti （制約: α+β=1）
    # ラグランジュ乗数→最小二乗で解く
    X = mdf[["hrs_above_rated_norm", "mean_ti_norm"]].values
    y = mdf["del_proxy_norm"].values

    # 単純OLS（制約なし）
    from numpy.linalg import lstsq
    A = np.column_stack([X, np.ones(len(y))])
    coeffs, _, _, _ = lstsq(A, y, rcond=None)
    alpha_raw, beta_raw = coeffs[0], coeffs[1]

    # 制約あり（α+β=1に正規化）
    ab_sum = max(alpha_raw + beta_raw, 1e-9)
    alpha_cal = max(0, alpha_raw) / max(abs(alpha_raw) + max(0, beta_raw), 1e-9)
    beta_cal = max(0, beta_raw) / max(max(0, alpha_raw) + abs(beta_raw), 1e-9)
    # シンプルに正規化
    if alpha_raw > 0 and beta_raw > 0:
        alpha_cal = alpha_raw / (alpha_raw + beta_raw)
        beta_cal = beta_raw / (alpha_raw + beta_raw)
    elif alpha_raw > 0:
        alpha_cal, beta_cal = 1.0, 0.0
    else:
        alpha_cal, beta_cal = 0.0, 1.0

    print(f"\n  較正重み: α(hrs_above_rated)={alpha_cal:.3f}, β(mean_ti)={beta_cal:.3f}")
    print(f"  比較: Phase 3等重み α=β=0.500")
    results["alpha_calibrated"] = alpha_cal
    results["beta_calibrated"] = beta_cal

    return results


# ─────────────────────────────────────────
# 6. 可視化
# ─────────────────────────────────────────

def plot_phase5_results(mdf: pd.DataFrame, weights: dict):
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    month_labels = ["Jan","Feb","Mar","Apr","May","Jun",
                    "Jul","Aug","Sep","Oct","Nov","Dec"]
    months = mdf["month"].values

    # パネル1: DELプロキシ月次推移
    ax = axes[0, 0]
    ax.bar(months, mdf["del_proxy"], color="#E53935", alpha=0.8)
    ax.set_title("Monthly DEL Proxy (blade flapwise)")
    ax.set_xlabel("Month"); ax.set_ylabel("DEL Proxy (normalized to rated)")
    ax.set_xticks(months); ax.set_xticklabels([month_labels[m-1] for m in months])
    ax.grid(axis="y", alpha=0.3)

    # パネル2: DELプロキシ vs hrs_above_rated
    ax = axes[0, 1]
    ax.scatter(mdf["hrs_above_rated_norm"], mdf["del_proxy_norm"],
               c=months, cmap="RdYlBu_r", s=60, zorder=3)
    r_hrs, _ = stats.pearsonr(mdf["hrs_above_rated_norm"], mdf["del_proxy_norm"])
    ax.set_xlabel("hrs_above_rated (normalized)")
    ax.set_ylabel("DEL Proxy (normalized)")
    ax.set_title(f"DEL vs hrs_above_rated\nr = {r_hrs:.3f}")
    for _, row in mdf.iterrows():
        ax.annotate(month_labels[int(row["month"])-1],
                    (row["hrs_above_rated_norm"], row["del_proxy_norm"]),
                    fontsize=7, ha="center", va="bottom")
    ax.grid(alpha=0.3)

    # パネル3: DELプロキシ vs mean_ti
    ax = axes[0, 2]
    ax.scatter(mdf["mean_ti_norm"], mdf["del_proxy_norm"],
               c=months, cmap="RdYlBu_r", s=60, zorder=3)
    r_ti, _ = stats.pearsonr(mdf["mean_ti_norm"], mdf["del_proxy_norm"])
    ax.set_xlabel("mean_ti (normalized)")
    ax.set_ylabel("DEL Proxy (normalized)")
    ax.set_title(f"DEL vs mean_ti\nr = {r_ti:.3f}")
    for _, row in mdf.iterrows():
        ax.annotate(month_labels[int(row["month"])-1],
                    (row["mean_ti_norm"], row["del_proxy_norm"]),
                    fontsize=7, ha="center", va="bottom")
    ax.grid(alpha=0.3)

    # パネル4: Phase 3等重みスコア vs DELプロキシ
    ax = axes[1, 0]
    p3 = pd.read_csv(PHASE3_DIR / "phase3_fatigue_proxy.csv")
    p3_norm = (p3["fatigue_risk_score"] - p3["fatigue_risk_score"].min()) / \
              (p3["fatigue_risk_score"].max() - p3["fatigue_risk_score"].min() + 1e-9)
    ax.plot(months, mdf["del_proxy_norm"].values, "o-", color="#E53935", label="DEL Proxy")
    ax.plot(p3["month"].values, p3_norm.values, "s--", color="#1E88E5", label="Phase 3 (equal-weight)")
    ax.set_xlabel("Month"); ax.set_ylabel("Normalized Risk Score")
    ax.set_title("DEL Proxy vs Phase 3 Fatigue Score")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax.set_xticks(months); ax.set_xticklabels([month_labels[m-1] for m in months])

    # パネル5: 較正後スコア vs DELプロキシ
    ax = axes[1, 1]
    alpha = weights["alpha_calibrated"]
    beta  = weights["beta_calibrated"]
    calibrated = alpha * mdf["hrs_above_rated_norm"] + beta * mdf["mean_ti_norm"]
    cal_norm = (calibrated - calibrated.min()) / (calibrated.max() - calibrated.min() + 1e-9)
    ax.plot(months, mdf["del_proxy_norm"].values, "o-", color="#E53935", label="DEL Proxy")
    ax.plot(months, cal_norm.values, "^-", color="#43A047", label=f"Calibrated (α={alpha:.2f}, β={beta:.2f})")
    ax.set_xlabel("Month"); ax.set_ylabel("Normalized Risk Score")
    ax.set_title("DEL Proxy vs Calibrated Score")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax.set_xticks(months); ax.set_xticklabels([month_labels[m-1] for m in months])

    # パネル6: 風速×TI ヒートマップ（DEL寄与）
    ax = axes[1, 2]
    v_grid = np.linspace(0, 25, 50)
    ti_grid = np.linspace(0.0, 0.20, 50)
    VV, TT = np.meshgrid(v_grid, ti_grid)
    del_heat = calc_blade_load_index(VV.ravel(), TT.ravel(), TURBINE).reshape(VV.shape)
    im = ax.contourf(VV, TT, del_heat, levels=20, cmap="hot_r")
    ax.axvline(TURBINE["rated_wind_ms"], color="cyan", ls="--", lw=1, label="Rated wind speed")
    ax.axhline(0.15, color="lime", ls="--", lw=1, label="TI=0.15 (high TI)")
    ax.axhline(0.10, color="yellow", ls="--", lw=1, label="TI=0.10 (erosion onset)")
    plt.colorbar(im, ax=ax)
    ax.set_xlabel("Wind Speed (m/s)"); ax.set_ylabel("Turbulence Intensity (TI)")
    ax.set_title("Blade Load Index: V × TI Space")
    ax.legend(fontsize=6, loc="upper left")

    plt.suptitle("Phase 5: Simplified Blade Fatigue Load Analysis\n"
                 "(Analytical DEL Proxy — Pre-OpenFAST Simulation Stage)",
                 fontsize=12, y=1.01)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "phase5_load_analysis.png", dpi=120, bbox_inches="tight")
    print("Phase 5可視化保存: phase5_openfast_shm/phase5_load_analysis.png")


# ─────────────────────────────────────────
# 7. OpenFASTパイプライン設計仕様書
# ─────────────────────────────────────────

def write_openfast_pipeline_spec():
    spec = """# OpenFAST統合パイプライン設計仕様

## 目的
簡易解析モデル（phase5_load_analysis.py）で得た (V, TI) → DEL マッピングを、
OpenFASTの高精度シミュレーションで検証・較正する。

## 必要入力ファイル（参照タービン: NREL 5MW Land-Based）
```
NREL5MW/
├── NREL5MW.fst               # 主制御ファイル
├── NRELOffswtBsline5MW_Onshore_AeroDyn15.dat
├── NRELOffswtBsline5MW_BeamDyn_Blade.dat
├── NRELOffswtBsline5MW_ElastoDyn.dat
├── NRELOffswtBsline5MW_ElastoDyn_Blade.dat
├── NRELOffswtBsline5MW_ServoDyn.dat
├── wind/
│   ├── IEC_NTM_V8_TI14.bts   # TurbSim: V=8m/s, TI=14%(Class B)
│   ├── IEC_NTM_V12_TI14.bts
│   └── ...
```
取得: https://github.com/OpenFAST/r-test/tree/main/glue-codes/openfast/5MW_Land_DLL_WTurb

## TurbSim風場生成（IEC ETM）
```bash
TurbSim TurbSim_IEC_NTM.inp
```
風況クラス組み合わせ（DLC 1.2相当）:
- V = 4, 6, 8, 10, 12, 14, 16, 18 m/s
- TI = 0.08, 0.12, 0.14, 0.16, 0.20 (IEC Class C, B, A+)

## OpenFAST実行・DEL抽出（Python擬似コード）
```python
from openfast_toolbox.postpro import postProRows, DELs
import subprocess, os

for v in V_LIST:
    for ti in TI_LIST:
        # 入力ファイル修正（wind speed, TI）
        modify_inflow(v, ti)
        # 実行
        subprocess.run(['openfast', 'NREL5MW.fst'])
        # 結果読込
        result = postProRows('NREL5MW.outb')
        # DEL計算: ブレード根元フラップ方向 (RootMyb1)
        del_val = DELs(result, 'RootMyb1', m=10, Teq=600)
        del_matrix[v][ti] = del_val
```

## Phase 5本格実装の次ステップ
1. NREL 5MWリポジトリをクローン
2. TurbSimで風場生成（8×5=40ケース）
3. OpenFAST実行（各600秒シミュレーション）
4. DELマトリクス（V×TI）を抽出
5. 本スクリプトの簡易モデルと比較・較正
6. 較正済み重みでPhase 4統合スコアを更新
"""
    (OUT_DIR / "openfast_pipeline_spec.md").write_text(spec)
    print("OpenFASTパイプライン仕様書保存: phase5_openfast_shm/openfast_pipeline_spec.md")


# ─────────────────────────────────────────
# メイン
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=== Phase 5: ブレード荷重モデルによる疲労指標較正 ===\n")

    print("--- 1. SCADAデータ読み込み ---")
    df = load_scada()

    print("\n--- 2. 月次DELプロキシ算出 ---")
    mdf = calc_monthly_del_proxy(df, TURBINE)
    print(mdf[["month", "del_proxy", "hrs_above_rated", "mean_ti", "del_proxy_norm"]].to_string(index=False))

    print("\n--- 3. Phase 3指標との比較・重み較正 ---")
    weights = compare_with_phase3(mdf)

    print("\n--- 4. 可視化 ---")
    plot_phase5_results(mdf, weights)

    print("\n--- 5. DELプロキシCSV保存 ---")
    mdf.to_csv(OUT_DIR / "phase5_del_proxy.csv", index=False)
    print("CSV保存: phase5_openfast_shm/phase5_del_proxy.csv")

    print("\n--- 6. OpenFASTパイプライン仕様書 ---")
    write_openfast_pipeline_spec()

    print("\n=== Phase 5 完了（簡易解析段階） ===")
    print(f"\n  較正重み: α(hrs_above_rated)={weights['alpha_calibrated']:.3f}, "
          f"β(mean_ti)={weights['beta_calibrated']:.3f}")
    print(f"  Phase 3等重み: α=β=0.500")
    print("\n  次ステップ: NREL 5MW参照タービン入力ファイルでOpenFASTシミュレーション実行")
