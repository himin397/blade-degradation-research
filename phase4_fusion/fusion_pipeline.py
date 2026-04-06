"""
Phase 4: 画像リスクスコア × SCADA疲労指標 統合パイプライン（型実装）

設計方針：
    現時点では画像データ（DTU・デンマーク）とSCADAデータ（Kaggle・トルコ）は
    別タービンのため、直接の統合は統計的に無効。
    本スクリプトは「自社データが揃った時に即動作できる型（パイプライン構造）」として実装する。

    仮データ（合成）で全パイプラインが動作することを確認済み。
    自社データへの差し替えは data_loader.py のインターフェースを変更するだけでよい。

パイプライン構造：
    ┌─────────────────────────────────────────────────┐
    │ 入力A: 画像リスクスコア（スパン別・タービンID・月）  │
    │         ← Phase 1/2 の出力を想定                   │
    └──────────────────┬──────────────────────────────┘
                       │
    ┌──────────────────▼──────────────────────────────┐
    │ 入力B: SCADA疲労代理指標（タービンID・月）          │
    │         ← Phase 3 の出力を想定                     │
    └──────────────────┬──────────────────────────────┘
                       │ merge on [turbine_id, month]
    ┌──────────────────▼──────────────────────────────┐
    │ 統合テーブル                                       │
    │ 相関分析・可視化・リスク統合スコア算出              │
    └─────────────────────────────────────────────────┘

環境: conda env blade-phase3
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

REPO_ROOT = Path(__file__).parent.parent
OUT_DIR   = REPO_ROOT / "phase4_fusion"
OUT_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────
# データローダー（インターフェース定義）
# ─────────────────────────────────────────

def load_image_risk_scores(use_real: bool = False) -> pd.DataFrame:
    """
    画像リスクスコアを読み込む。

    本番（use_real=True）では Phase 1/2 の出力CSVを読む。
    現状（use_real=False）では合成データを返す。

    Returns:
        DataFrame with columns: [turbine_id, month, tip_score, mid_score, root_score, image_risk_composite]
    """
    if use_real:
        # TODO: Phase 1/2 の出力CSVパスに変更
        # df = pd.read_csv(REPO_ROOT / "phase2_temporal" / "scores_by_year.json")
        raise NotImplementedError("実データへの切り替えは TODO: パスを設定してください")

    # 合成データ：12ヶ月 × 5タービン
    np.random.seed(42)
    rows = []
    for tid in range(1, 6):
        for month in range(1, 13):
            # 仮説に基づく季節変動を付与（冬季・夏季に損傷リスク高）
            seasonal = 0.3 * np.sin((month - 3) * np.pi / 6) + 0.5
            tip   = max(0, np.random.normal(seasonal * 1.5, 0.2))
            mid   = max(0, np.random.normal(seasonal * 1.0, 0.15))
            root  = max(0, np.random.normal(seasonal * 0.5, 0.1))
            composite = (tip * 3 + mid * 2 + root * 1) / 6
            rows.append({
                "turbine_id": f"T{tid:02d}",
                "month": month,
                "tip_score": tip,
                "mid_score": mid,
                "root_score": root,
                "image_risk_composite": composite,
            })
    return pd.DataFrame(rows)


def load_fatigue_proxy(use_real: bool = False) -> pd.DataFrame:
    """
    SCADA疲労代理指標を読み込む。

    優先順位:
        1. Phase 3b (phase3b_monthly_del.csv) が存在する場合:
           DEL_est_kNm を全タービン横断で 0-1 正規化し fatigue_risk_score とする。
           これにより疲労指標が物理量（kN-m）に基づく。
           ※ 実サイト TI（0.03〜0.04）がシミュレーション行列下限（0.08）を下回るため、
             現状 DEL は V 単変数補間として機能（TI クリッピング制約）。
        2. Phase 3 (phase3_fatigue_proxy.csv) のみ存在する場合:
           hrs_above_rated × 0.740 + mean_ti × 0.260 加重和（フォールバック）。
        3. どちらも存在しない場合: 完全合成データ。

    Returns:
        DataFrame with columns:
            [turbine_id, month, hrs_above_rated, mean_ti, DEL_est_kNm, fatigue_risk_score]
        DEL_est_kNm: Phase 3b が存在しない場合は NaN
        fatigue_risk_score: 0-1 正規化済み複合疲労指標
    """
    phase3b_path = REPO_ROOT / "phase3_scada" / "phase3b_monthly_del.csv"
    phase3_path  = REPO_ROOT / "phase3_scada" / "phase3_fatigue_proxy.csv"

    # ── 優先: Phase 3b DEL ルックアップ ──────────────────────────────────
    if use_real and phase3b_path.exists():
        df3b = pd.read_csv(phase3b_path)
        dfs = []
        for tid in range(1, 6):
            tmp = df3b[["month", "hrs_above_rated", "TI_iec", "DEL_est_kNm"]].copy()
            tmp = tmp.rename(columns={"TI_iec": "mean_ti"})
            # タービンごとにランダムノイズで多様性を表現（型確認用・実機では不要）
            np.random.seed(tid * 10)
            tmp["hrs_above_rated"] *= np.random.uniform(0.8, 1.2, len(tmp))
            tmp["DEL_est_kNm"] *= np.random.uniform(0.85, 1.15, len(tmp))
            tmp["turbine_id"] = f"T{tid:02d}"
            dfs.append(tmp)
        merged = pd.concat(dfs, ignore_index=True)
        # DEL_est_kNm を全タービン横断で 0-1 正規化 → fatigue_risk_score
        mn, mx = merged["DEL_est_kNm"].min(), merged["DEL_est_kNm"].max()
        merged["fatigue_risk_score"] = (merged["DEL_est_kNm"] - mn) / (mx - mn + 1e-9)
        print("  [Phase 3b] DEL_est_kNm (kN-m) → fatigue_risk_score（全タービン横断正規化）")
        print(f"  DEL範囲: {mn:.0f}〜{mx:.0f} kN-m")
        return merged

    # ── フォールバック: Phase 3 疲労代理指標 ─────────────────────────────
    if use_real and phase3_path.exists():
        df = pd.read_csv(phase3_path)
        dfs = []
        for tid in range(1, 6):
            tmp = df[["month", "hrs_above_rated", "mean_ti", "fatigue_risk_score"]].copy()
            np.random.seed(tid * 10)
            tmp["hrs_above_rated"] *= np.random.uniform(0.8, 1.2, len(tmp))
            tmp["mean_ti"] *= np.random.uniform(0.9, 1.1, len(tmp))
            # 重み: OpenFAST DLC1.2 マルチシード・標準Rainflow較正済み (Phase 5b)
            tmp["fatigue_risk_score"] = (
                (tmp["hrs_above_rated"] - tmp["hrs_above_rated"].min()) /
                (tmp["hrs_above_rated"].max() - tmp["hrs_above_rated"].min() + 1e-9) * 0.7400 +
                (tmp["mean_ti"] - tmp["mean_ti"].min()) /
                (tmp["mean_ti"].max() - tmp["mean_ti"].min() + 1e-9) * 0.2600
            )
            tmp["DEL_est_kNm"] = np.nan  # Phase 3b なし
            tmp["turbine_id"] = f"T{tid:02d}"
            dfs.append(tmp)
        print("  [Phase 3 fallback] hrs_above_rated × 0.740 + mean_ti × 0.260 加重和を使用")
        return pd.concat(dfs, ignore_index=True)

    # ── 完全合成データ ────────────────────────────────────────────────────
    np.random.seed(0)
    rows = []
    for tid in range(1, 6):
        for month in range(1, 13):
            hrs = max(0, np.random.normal(60, 30))
            ti  = np.random.uniform(0.02, 0.05)
            score = (hrs / 200 + (ti - 0.02) / 0.03) / 2
            rows.append({"turbine_id": f"T{tid:02d}", "month": month,
                         "hrs_above_rated": hrs, "mean_ti": ti,
                         "DEL_est_kNm": np.nan,
                         "fatigue_risk_score": score})
    return pd.DataFrame(rows)


# ─────────────────────────────────────────
# 統合・分析
# ─────────────────────────────────────────

def merge_datasets(img_df: pd.DataFrame, scada_df: pd.DataFrame) -> pd.DataFrame:
    """タービンID・月でマージ。"""
    merged = pd.merge(img_df, scada_df,
                      on=["turbine_id", "month"], suffixes=("_img", "_scada"))
    print(f"統合テーブル: {len(merged)}行 × {len(merged.columns)}列")
    return merged


def calc_integrated_risk(merged: pd.DataFrame) -> pd.DataFrame:
    """
    統合リスクスコアを算出する。

    統合リスク = α × 画像リスク + β × 疲労リスク
    現状は等重み（α=β=0.5）。将来的にはデータ駆動で重みを最適化する。
    """
    alpha, beta = 0.5, 0.5
    merged["integrated_risk"] = (
        alpha * merged["image_risk_composite"] +
        beta  * merged["fatigue_risk_score"]
    )
    # 0-1正規化
    mn, mx = merged["integrated_risk"].min(), merged["integrated_risk"].max()
    merged["integrated_risk_norm"] = (merged["integrated_risk"] - mn) / (mx - mn + 1e-9)
    return merged


def analyze_correlation(merged: pd.DataFrame):
    """画像リスクスコアと疲労リスクスコアの相関を分析する。"""
    r, p = stats.pearsonr(merged["image_risk_composite"],
                          merged["fatigue_risk_score"])
    print(f"Pearson相関: r={r:.4f}, p={p:.4f}")

    r_sp, p_sp = stats.spearmanr(merged["image_risk_composite"],
                                  merged["fatigue_risk_score"])
    print(f"Spearman相関: r={r_sp:.4f}, p={p_sp:.4f}")
    return {"pearson_r": r, "pearson_p": p, "spearman_r": r_sp, "spearman_p": p_sp}


def plot_fusion_results(merged: pd.DataFrame):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # パネル1：画像リスク vs 疲労リスクの散布図
    ax = axes[0]
    for tid, grp in merged.groupby("turbine_id"):
        ax.scatter(grp["fatigue_risk_score"], grp["image_risk_composite"],
                   alpha=0.6, label=tid, s=30)
    ax.set_xlabel("Fatigue Risk Score (SCADA)")
    ax.set_ylabel("Image Risk Score (composite)")
    ax.set_title("Image vs Fatigue Risk")
    ax.legend(fontsize=7)
    r, _ = stats.pearsonr(merged["fatigue_risk_score"],
                           merged["image_risk_composite"])
    ax.text(0.05, 0.95, f"r = {r:.3f}", transform=ax.transAxes,
            va="top", fontsize=10, color="red")
    ax.grid(alpha=0.3)

    # パネル2：月次統合リスクスコア（全タービン平均）
    ax = axes[1]
    monthly_avg = merged.groupby("month")["integrated_risk_norm"].mean()
    ax.bar(monthly_avg.index, monthly_avg.values, color="#1E88E5")
    ax.set_xlabel("Month")
    ax.set_ylabel("Integrated Risk Score (normalized)")
    ax.set_title("Monthly Integrated Risk (avg across turbines)")
    ax.grid(axis="y", alpha=0.3)

    # パネル3：タービン別統合リスクスコア（年平均）
    ax = axes[2]
    turbine_avg = merged.groupby("turbine_id")["integrated_risk_norm"].mean().sort_values(ascending=False)
    colors = ["#E53935" if v > turbine_avg.mean() + turbine_avg.std() else "#1E88E5"
              for v in turbine_avg.values]
    ax.bar(turbine_avg.index, turbine_avg.values, color=colors)
    ax.axhline(turbine_avg.mean(), color="gray", ls="--", lw=1, label="Average")
    ax.set_xlabel("Turbine ID")
    ax.set_ylabel("Integrated Risk Score (normalized)")
    ax.set_title("Annual Integrated Risk by Turbine")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)

    plt.suptitle("Phase 4: Image × SCADA Fusion Pipeline (synthetic data)", fontsize=13, y=1.02)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "fusion_results.png", dpi=120, bbox_inches="tight")
    print("統合結果可視化: phase4_fusion/fusion_results.png")


# ─────────────────────────────────────────
# メイン
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("=== Phase 4: 統合パイプライン（型実装・合成データ） ===\n")

    print("--- 1. データ読み込み ---")
    img_df   = load_image_risk_scores(use_real=False)
    scada_df = load_fatigue_proxy(use_real=True)   # Phase 3実出力を使用
    print(f"画像リスクスコア: {len(img_df)}行")
    print(f"SCADA疲労指標: {len(scada_df)}行")

    print("\n--- 2. マージ ---")
    merged = merge_datasets(img_df, scada_df)

    print("\n--- 3. 統合リスクスコア算出 ---")
    merged = calc_integrated_risk(merged)

    print("\n--- 4. 相関分析 ---")
    corr = analyze_correlation(merged)

    print("\n--- 5. 可視化 ---")
    plot_fusion_results(merged)

    print("\n--- 6. CSV出力 ---")
    merged.to_csv(OUT_DIR / "fusion_results.csv", index=False)
    print("CSV保存: phase4_fusion/fusion_results.csv")

    # 上位リスクタービン
    top = merged.groupby("turbine_id")["integrated_risk_norm"].mean().sort_values(ascending=False)
    print("\n=== タービン別年間統合リスクランキング ===")
    for tid, score in top.items():
        flag = " ← 要注意" if score > top.mean() + top.std() else ""
        print(f"  {tid}: {score:.4f}{flag}")

    print("\n=== Phase 4 完了 ===")
