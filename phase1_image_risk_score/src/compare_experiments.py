"""
Phase 1: 実験比較スクリプト

EXP-001（ベースライン）と EXP-002（ピラミッド拡張）の学習結果を並べて比較する。

使い方:
    python phase1_image_risk_score/src/compare_experiments.py
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

REPO_ROOT = Path(__file__).parent.parent.parent
EXP_DIR = REPO_ROOT / "runs" / "detect" / "phase1_image_risk_score" / "experiments"
REPORT_DIR = REPO_ROOT / "phase1_image_risk_score" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

EXP_DIR_002 = REPO_ROOT / "runs" / "detect" / "runs" / "detect" / "phase1_image_risk_score" / "experiments"

EXPERIMENTS = {
    "EXP-001 ベースライン": EXP_DIR / "baseline_yolov8n",
    "EXP-002 ピラミッド拡張": EXP_DIR_002 / "pyramid_yolov8n",
}


def load_results(exp_dir: Path) -> pd.DataFrame:
    csv = exp_dir / "results.csv"
    if not csv.exists():
        return None
    df = pd.read_csv(csv)
    df.columns = df.columns.str.strip()
    return df


def print_summary_table(dfs: dict):
    """各実験のベストmAP50・最終Precision・Recallを表示する。"""
    print("\n=== 実験比較サマリー ===\n")
    print(f"{'実験':<25} {'mAP@0.5（ベスト）':>16} {'Precision（最終）':>16} {'Recall（最終）':>14}")
    print("-" * 75)
    for name, df in dfs.items():
        if df is None:
            print(f"{name:<25} {'学習未完了':>16}")
            continue
        best_map50 = df["metrics/mAP50(B)"].max()
        best_epoch = df["metrics/mAP50(B)"].idxmax() + 1
        last = df.iloc[-1]
        print(f"{name:<25} {best_map50:>14.4f}（ep{best_epoch:02d}）"
              f" {last['metrics/precision(B)']:>16.4f}"
              f" {last['metrics/recall(B)']:>14.4f}")
    print()


def plot_comparison(dfs: dict):
    """mAP50・Precision・Recallの学習曲線を実験間で比較する。"""
    metrics = [
        ("metrics/mAP50(B)", "mAP@0.5"),
        ("metrics/precision(B)", "Precision"),
        ("metrics/recall(B)", "Recall"),
    ]
    colors = ["#1f77b4", "#d62728"]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle("EXP-001 vs EXP-002: ピラミッド拡張の効果", fontsize=13)

    for ax, (col, label) in zip(axes, metrics):
        for (name, df), color in zip(dfs.items(), colors):
            if df is None:
                continue
            ax.plot(df["epoch"], df[col], label=name, color=color)
        ax.set_title(label)
        ax.set_xlabel("Epoch")
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)

    plt.tight_layout()
    out = REPORT_DIR / "experiment_comparison.png"
    plt.savefig(out, dpi=120)
    print(f"比較グラフを保存: {out}")


def print_delta(dfs: dict):
    """EXP-001を基準にしたEXP-002の改善量を表示する。"""
    names = list(dfs.keys())
    if len(names) < 2 or dfs[names[1]] is None:
        print("EXP-002がまだ完了していないため、差分は計算できません。")
        return

    df1 = dfs[names[0]]
    df2 = dfs[names[1]]

    map1 = df1["metrics/mAP50(B)"].max()
    map2 = df2["metrics/mAP50(B)"].max()
    recall1 = df1.iloc[-1]["metrics/recall(B)"]
    recall2 = df2.iloc[-1]["metrics/recall(B)"]

    print("=== EXP-001 → EXP-002 変化量 ===\n")
    print(f"  mAP@0.5:  {map1:.4f} → {map2:.4f}  ({map2 - map1:+.4f})")
    print(f"  Recall:   {recall1:.4f} → {recall2:.4f}  ({recall2 - recall1:+.4f})")
    print()

    if map2 > map1:
        print("  ✓ ピラミッド拡張によりmAP50が改善")
    else:
        print("  △ mAP50は改善せず（考察が必要）")

    if recall2 > recall1:
        print("  ✓ Recallが改善（小さい損傷の見逃しが減った可能性）")
    else:
        print("  △ Recallは改善せず")


if __name__ == "__main__":
    dfs = {name: load_results(path) for name, path in EXPERIMENTS.items()}

    print_summary_table(dfs)
    plot_comparison(dfs)
    print_delta(dfs)
