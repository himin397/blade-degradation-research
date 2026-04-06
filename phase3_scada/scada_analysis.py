"""
Phase 3: SCADAデータ分析
- 前処理・データ品質確認
- パワーカーブ分析
- ブレード疲労リスク代理指標の算出

データ: Kaggle Wind Turbine SCADA Dataset (T1.csv)
        10分間隔、2018年1年間、トルコの風車1基
環境: conda env blade-phase3
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats

REPO_ROOT = Path(__file__).parent.parent
RAW_DIR   = REPO_ROOT / "data" / "raw" / "scada"
OUT_DIR   = REPO_ROOT / "phase3_scada"
OUT_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────
# 1. 読み込み・前処理
# ─────────────────────────────────────────

def load_and_preprocess() -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / "T1.csv")
    df.columns = ["timestamp", "power_kw", "wind_speed_ms",
                  "theoretical_power_kwh", "wind_direction_deg"]

    # タイムスタンプ変換
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%d %m %Y %H:%M")
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["month"] = df["timestamp"].dt.month
    df["hour"]  = df["timestamp"].dt.hour

    # 物理的に異常な値を除去（定格出力3600kWを上限、負値も除外）
    df = df[(df["power_kw"] >= 0) & (df["power_kw"] <= 3600)]
    df = df[(df["wind_speed_ms"] >= 0) & (df["wind_speed_ms"] <= 30)]

    # カーテイルメント除去: 実測/理論値が30%以下かつ風速>4m/s（停止または制御中）
    # theoretical_power_kwh は実際にはkW単位（列名は誤り）
    curtailment_mask = (df["theoretical_power_kwh"] > 0) & \
                       (df["power_kw"] / (df["theoretical_power_kwh"] + 1e-6) < 0.30) & \
                       (df["wind_speed_ms"] > 4.0)
    df["is_curtailed"] = curtailment_mask

    print(f"総レコード数: {len(df)}")
    print(f"カーテイルメント推定: {curtailment_mask.sum()}件 ({curtailment_mask.mean()*100:.1f}%)")
    return df


# ─────────────────────────────────────────
# 2. パワーカーブ分析
# ─────────────────────────────────────────

def analyze_power_curve(df: pd.DataFrame):
    normal = df[~df["is_curtailed"]].copy()

    # 風速ビン（0.5m/s幅）ごとの中央値パワー
    bins = np.arange(0, 25.5, 0.5)
    labels = (bins[:-1] + bins[1:]) / 2
    normal["ws_bin"] = pd.cut(normal["wind_speed_ms"], bins=bins, labels=labels)
    curve = normal.groupby("ws_bin", observed=True)["power_kw"].agg(
        median="median", q25=lambda x: x.quantile(0.25), q75=lambda x: x.quantile(0.75), n="count"
    ).reset_index()
    curve["ws_bin"] = curve["ws_bin"].astype(float)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.fill_between(curve["ws_bin"], curve["q25"], curve["q75"],
                    alpha=0.3, color="#2196F3", label="IQR (25-75%)")
    ax.plot(curve["ws_bin"], curve["median"], color="#1565C0", lw=2, label="Median power")
    ax.plot(normal["wind_speed_ms"], normal["theoretical_power_kwh"] * 6,
            ".", alpha=0.03, color="gray", markersize=2, label="Theoretical (scaled)")
    ax.set_xlabel("Wind Speed (m/s)")
    ax.set_ylabel("Active Power (kW)")
    ax.set_title("Power Curve (curtailment removed)")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "power_curve.png", dpi=120)
    print("パワーカーブ保存: phase3_scada/power_curve.png")
    return curve


# ─────────────────────────────────────────
# 3. 疲労リスク代理指標の設計・算出
# ─────────────────────────────────────────

def calc_fatigue_proxy(df: pd.DataFrame) -> pd.DataFrame:
    """
    ブレード疲労リスクの代理指標を月次で算出する。

    指標の根拠：
    - 高風速曝露時間 (hrs_above_rated):
        定格風速（約12m/s）超での運転時間。
        高風速＝高荷重→疲労蓄積の代理指標。
    - 乱流強度 TI (turbulence_intensity):
        同一風速ビン内の標準偏差/平均。
        TI高＝荷重変動大→エロージョン感応域（9-13m/s）での影響が大きい。
        参考：Malik & Bak 2025（DOI: 10.5194/wes-10-227-2025）
    - 高乱流時間 (hrs_high_ti):
        TI > 0.15 かつ wind_speed > 4m/s の時間（荷重変動の激しい運転）
    - 疲労リスクスコア (fatigue_risk_score):
        正規化した3指標の加重和（暫定重み：等重み）
    """
    normal = df[~df["is_curtailed"]].copy()
    dt_hours = 10 / 60  # 10分間隔 → 時間単位

    # 月次集計
    monthly = []
    for month, grp in normal.groupby("month"):
        hrs_above_rated = (grp["wind_speed_ms"] > 12.0).sum() * dt_hours

        # TI：風速ビン（1m/s幅）ごとにσ/μを計算して平均
        grp2 = grp[grp["wind_speed_ms"] > 4.0].copy()
        grp2["ws_bin1"] = grp2["wind_speed_ms"].apply(lambda x: int(x))
        # ビンごとのTIを計算（n>=5のビンのみ）
        bin_stats = grp2.groupby("ws_bin1")["wind_speed_ms"].agg(["mean","std","count"])
        bin_stats = bin_stats[bin_stats["count"] >= 5]
        bin_stats["ti"] = bin_stats["std"] / bin_stats["mean"]
        mean_ti = bin_stats["ti"].mean() if len(bin_stats) > 0 else 0.0

        # 各レコードにビンTIを付与して高TI時間を算出
        ti_map = bin_stats["ti"].to_dict()
        grp2["ti"] = grp2["ws_bin1"].map(ti_map).fillna(0.0)
        hrs_high_ti = (grp2["ti"] > 0.15).sum() * dt_hours

        monthly.append({
            "month": month,
            "hrs_above_rated": hrs_above_rated,
            "mean_ti": mean_ti,
            "hrs_high_ti": hrs_high_ti,
            "n_records": len(grp),
        })

    mdf = pd.DataFrame(monthly)

    # 各指標を0-1正規化して等重みで合算（暫定）
    for col in ["hrs_above_rated", "mean_ti", "hrs_high_ti"]:
        mn, mx = mdf[col].min(), mdf[col].max()
        mdf[f"{col}_norm"] = (mdf[col] - mn) / (mx - mn + 1e-9)

    mdf["fatigue_risk_score"] = (
        mdf["hrs_above_rated_norm"] +
        mdf["mean_ti_norm"] +
        mdf["hrs_high_ti_norm"]
    ) / 3.0

    return mdf


def plot_fatigue_proxy(mdf: pd.DataFrame):
    months = mdf["month"].values
    month_labels = ["Jan","Feb","Mar","Apr","May","Jun",
                    "Jul","Aug","Sep","Oct","Nov","Dec"]

    fig, axes = plt.subplots(4, 1, figsize=(12, 14), sharex=True)

    axes[0].bar(months, mdf["hrs_above_rated"], color="#E53935")
    axes[0].set_ylabel("Hours above rated\nwind speed (>12 m/s)")
    axes[0].set_title("Blade Fatigue Risk Proxy Indicators (Monthly, 2018)")
    axes[0].grid(axis="y", alpha=0.3)

    axes[1].bar(months, mdf["mean_ti"], color="#FB8C00")
    axes[1].set_ylabel("Mean Turbulence\nIntensity (TI)")
    axes[1].axhline(0.15, color="red", ls="--", lw=1, label="TI=0.15 threshold")
    axes[1].legend(fontsize=8)
    axes[1].grid(axis="y", alpha=0.3)

    axes[2].bar(months, mdf["hrs_high_ti"], color="#8E24AA")
    axes[2].set_ylabel("Hours with\nTI > 0.15")
    axes[2].grid(axis="y", alpha=0.3)

    axes[3].bar(months, mdf["fatigue_risk_score"], color="#1E88E5")
    axes[3].set_ylabel("Fatigue Risk Score\n(normalized composite)")
    axes[3].set_xlabel("Month")
    axes[3].set_xticks(months)
    axes[3].set_xticklabels([month_labels[m-1] for m in months])
    axes[3].grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUT_DIR / "fatigue_proxy_monthly.png", dpi=120)
    print("疲労リスク指標保存: phase3_scada/fatigue_proxy_monthly.png")


# ─────────────────────────────────────────
# 4. データ辞書出力
# ─────────────────────────────────────────

def save_data_dict(df: pd.DataFrame, mdf: pd.DataFrame):
    txt = """# Phase 3 データ辞書

## 元データ：T1.csv（Kaggle Wind Turbine SCADA Dataset）

| 列名（変換後） | 元列名 | 単位 | 説明 |
|---|---|---|---|
| timestamp | Date/Time | - | 10分間隔タイムスタンプ（2018年） |
| power_kw | LV ActivePower (kW) | kW | 発電機有効電力 |
| wind_speed_ms | Wind Speed (m/s) | m/s | ナセル風速計計測値 |
| theoretical_power_kwh | Theoretical_Power_Curve (KWh) | kWh | メーカー提供理論パワーカーブ値 |
| wind_direction_deg | Wind Direction (°) | 度 | 風向 |

## 前処理

- 除外条件：power_kw < 0 または > 3600kW、wind_speed > 30m/s
- カーテイルメント判定：理論値の30%以下かつ風速 > 4m/s
- タービン定格出力：約3,600kW（パワーカーブより推定）
- 定格風速：約12m/s（パワーカーブより推定）

## 算出特徴量（月次）：phase3_fatigue_proxy.csv

| 列名 | 単位 | 説明 |
|---|---|---|
| hrs_above_rated | 時間 | 定格風速（>12m/s）超での運転時間 |
| mean_ti | 無次元 | 月平均乱流強度（風速ビン内σ/μの平均） |
| hrs_high_ti | 時間 | TI > 0.15 かつ wind_speed > 4m/s の時間 |
| fatigue_risk_score | 0〜1 | 上記3指標の正規化加重和（等重み・暫定） |

## 注意事項・限界

- このタービンはトルコの1基。DTU画像データ（デンマーク）とは別タービン
- 疲労リスク代理指標は物理モデル（疲労累積則・S-Nカーブ）ではなく統計的近似
- TIは風速計1点計測のため、ブレード面全体のTIとは異なる可能性がある
- Phase 4での統合は「型（パイプライン構造）」として実装する（異タービン統合の限界のため）
"""
    (OUT_DIR / "data_dict.md").write_text(txt)
    print("データ辞書保存: phase3_scada/data_dict.md")


# ─────────────────────────────────────────
# メイン
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=== Phase 3: SCADA分析 ===\n")

    print("--- 1. 前処理 ---")
    df = load_and_preprocess()

    print("\n--- 2. パワーカーブ分析 ---")
    curve = analyze_power_curve(df)

    print("\n--- 3. 疲労リスク代理指標算出 ---")
    mdf = calc_fatigue_proxy(df)
    print(mdf[["month","hrs_above_rated","mean_ti","hrs_high_ti","fatigue_risk_score"]].to_string(index=False))
    plot_fatigue_proxy(mdf)

    print("\n--- 4. データ辞書・CSV出力 ---")
    mdf.to_csv(OUT_DIR / "phase3_fatigue_proxy.csv", index=False)
    save_data_dict(df, mdf)
    print("CSV保存: phase3_scada/phase3_fatigue_proxy.csv")

    print("\n=== Phase 3 完了 ===")
