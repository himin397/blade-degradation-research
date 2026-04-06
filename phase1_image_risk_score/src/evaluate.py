"""
Phase 1 W06: 学習済みモデルの評価・可視化スクリプト

最終目標との接続: 画像由来の損傷状態定量化（部品#1）
実行タイミング: YOLOv8学習完了後

使い方:
    python phase1_image_risk_score/src/evaluate.py                        # EXP-001（デフォルト）
    python phase1_image_risk_score/src/evaluate.py --exp pyramid_yolov8n  # EXP-002
"""

import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")  # 画面表示なし（ファイル保存のみ）

REPO_ROOT = Path(__file__).parent.parent.parent
REPORT_DIR = REPO_ROOT / "phase1_image_risk_score" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

CLASS_NAMES = ["VG;MT", "LE;ER", "LR;DA", "LE;CR", "SF;PO"]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--exp", default="baseline_yolov8n",
        help="実験フォルダ名（runs/detect/phase1_image_risk_score/experiments/ 以下）"
    )
    return parser.parse_args()


def plot_training_curves(results_csv: Path):
    """学習曲線（loss・mAP）をプロットして保存する。"""
    df = pd.read_csv(results_csv)
    df.columns = df.columns.str.strip()

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("YOLOv8n Baseline Training Curves\n(DTU Wind Turbine Dataset)", fontsize=13)

    # box loss
    axes[0, 0].plot(df["epoch"], df["train/box_loss"], label="train")
    axes[0, 0].plot(df["epoch"], df["val/box_loss"], label="val")
    axes[0, 0].set_title("Box Loss")
    axes[0, 0].set_xlabel("Epoch")
    axes[0, 0].legend()
    axes[0, 0].grid(True)

    # cls loss
    axes[0, 1].plot(df["epoch"], df["train/cls_loss"], label="train")
    axes[0, 1].plot(df["epoch"], df["val/cls_loss"], label="val")
    axes[0, 1].set_title("Classification Loss")
    axes[0, 1].set_xlabel("Epoch")
    axes[0, 1].legend()
    axes[0, 1].grid(True)

    # mAP50
    axes[1, 0].plot(df["epoch"], df["metrics/mAP50(B)"], color="green", label="mAP50")
    axes[1, 0].set_title("mAP@0.5")
    axes[1, 0].set_xlabel("Epoch")
    axes[1, 0].set_ylim(0, 1)
    axes[1, 0].legend()
    axes[1, 0].grid(True)

    # mAP50-95
    axes[1, 1].plot(df["epoch"], df["metrics/mAP50-95(B)"], color="orange", label="mAP50-95")
    axes[1, 1].set_title("mAP@0.5:0.95")
    axes[1, 1].set_xlabel("Epoch")
    axes[1, 1].set_ylim(0, 1)
    axes[1, 1].legend()
    axes[1, 1].grid(True)

    plt.tight_layout()
    out = REPORT_DIR / "training_curves.png"
    plt.savefig(out, dpi=120)
    print(f"学習曲線を保存: {out}")
    return df


def summarize_results(df: pd.DataFrame, exp_name: str = "baseline_yolov8n"):
    """最終エポックの結果をサマリーとして表示・保存する。"""
    last = df.iloc[-1]
    best_map50_epoch = df["metrics/mAP50(B)"].idxmax() + 1
    best_map50 = df["metrics/mAP50(B)"].max()

    summary = f"""
# 学習結果サマリー: {exp_name}

## 学習設定
- モデル: YOLOv8n（nanoサイズ）
- データ: DTU Wind Turbine Inspection Images
  - 一次ソース: DOI 10.17632/hd96prn3nc.2
  - アノテーション: github.com/imadgohar/DTU-annotations (Gohar et al. 2023)
- エポック数: {int(last['epoch'])}
- クラス数: 5 ({', '.join(CLASS_NAMES)})
- 入力サイズ: 640px
- デバイス: MPS（Apple Silicon GPU）

## 最終エポック結果
- mAP@0.5:       {last['metrics/mAP50(B)']:.4f}
- mAP@0.5:0.95:  {last['metrics/mAP50-95(B)']:.4f}
- Precision:     {last['metrics/precision(B)']:.4f}
- Recall:        {last['metrics/recall(B)']:.4f}

## ベスト結果
- 最良mAP@0.5: {best_map50:.4f}（エポック{best_map50_epoch}）

## 先行研究との比較
| 手法 | mAP@0.5 | 備考 |
|---|---|---|
| 本研究（YOLOv8n ベースライン） | {best_map50:.4f} | 30エポック・640px |
| Shihavuddin et al. 2019 | 0.8110 | Faster R-CNN + Inception-ResNet-V2 |

## 考察
（学習完了後に記入）

## 次のアクション（W07）
- 部位定義の設計（Leading Edge / Trailing Edge / 翼根 / 翼端）
- バウンディングボックス × 部位マッピングの実装
"""
    out = REPORT_DIR / "baseline_summary.md"
    out.write_text(summary)
    print(summary)
    print(f"サマリーを保存: {out}")


if __name__ == "__main__":
    args = parse_args()
    _base_exp_dir = REPO_ROOT / "runs" / "detect" / "phase1_image_risk_score" / "experiments"
    _nested_exp_dir = REPO_ROOT / "runs" / "detect" / "runs" / "detect" / "phase1_image_risk_score" / "experiments"
    if (_base_exp_dir / args.exp / "results.csv").exists():
        EXPERIMENT_DIR = _base_exp_dir / args.exp
    else:
        EXPERIMENT_DIR = _nested_exp_dir / args.exp
    results_csv = EXPERIMENT_DIR / "results.csv"
    if not results_csv.exists():
        print(f"まだ学習結果がありません: {results_csv}")
        print("学習完了後に実行してください。")
    else:
        df = plot_training_curves(results_csv)
        summarize_results(df, exp_name=args.exp)
