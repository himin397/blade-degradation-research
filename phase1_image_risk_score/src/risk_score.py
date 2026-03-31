"""
Phase 1 W08: 部位別リスクスコア集計・可視化スクリプト

最終目標との接続: 画像由来の損傷状態定量化（部品#1）
前提:
  - region_mapper.py の関数を使用
  - YOLOv8の推論結果（YOLO txt形式）が data/processed/predictions/ に存在

出力:
  - 部位別リスクスコアの棒グラフ（PNG）
  - スコアサマリーCSV
  - ブレード展開図へのスコア投影（簡易版）
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib
matplotlib.use("Agg")

from region_mapper import (
    Detection, CLASS_NAMES, REGION_WEIGHTS,
    assign_region, calc_risk_score, format_score_report
)

REPO_ROOT = Path(__file__).parent.parent.parent
REPORT_DIR = REPO_ROOT / "phase1_image_risk_score" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def load_yolo_predictions(pred_dir: Path, image_list: list) -> dict:
    """
    YOLO形式の推論結果txtを読み込む。

    Args:
        pred_dir: 推論結果txtが入ったフォルダ
        image_list: 対象画像ファイル名のリスト
    Returns:
        {image_name: [Detection, ...]} の辞書
    """
    results = {}
    for img_name in image_list:
        txt_name = Path(img_name).stem + ".txt"
        txt_path = pred_dir / txt_name
        detections = []
        if txt_path.exists():
            for line in txt_path.read_text().strip().split("\n"):
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 6:
                    class_id = int(parts[0])
                    conf = float(parts[5]) if len(parts) > 5 else 1.0
                    cx, cy, w, h = map(float, parts[1:5])
                    det = Detection(
                        class_id=class_id,
                        class_name=CLASS_NAMES.get(class_id, "unknown"),
                        confidence=conf,
                        cx=cx, cy=cy, w=w, h=h,
                    )
                    det.region = assign_region(det, img_name)
                    detections.append(det)
        results[img_name] = detections
    return results


def aggregate_scores(all_detections: dict) -> pd.DataFrame:
    """
    全画像のリスクスコアを集計してDataFrameにまとめる。
    """
    rows = []
    for img_name, detections in all_detections.items():
        scores = calc_risk_score(detections)
        row = {"image": img_name}
        row.update(scores)
        rows.append(row)
    return pd.DataFrame(rows)


def plot_region_scores(df: pd.DataFrame, title: str = "部位別リスクスコア（全画像合計）"):
    """部位別スコアの棒グラフを保存する。"""
    region_cols = list(REGION_WEIGHTS.keys())
    totals = df[region_cols].sum()

    # リスク順にソート
    totals = totals.sort_values(ascending=False)

    colors = ["#d62728" if r.endswith("LE") else "#1f77b4" for r in totals.index]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(totals.index, totals.values, color=colors)
    ax.set_title(title, fontsize=13)
    ax.set_xlabel("部位")
    ax.set_ylabel("累積リスクスコア")
    ax.grid(axis="y", alpha=0.3)

    legend = [
        mpatches.Patch(color="#d62728", label="前縁（LE）"),
        mpatches.Patch(color="#1f77b4", label="胴体（Body）"),
    ]
    ax.legend(handles=legend)

    for bar, val in zip(bars, totals.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.001,
                f"{val:.3f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    out = REPORT_DIR / "region_risk_scores.png"
    plt.savefig(out, dpi=120)
    print(f"棒グラフを保存: {out}")


def plot_blade_heatmap(df: pd.DataFrame):
    """
    ブレード展開図（簡易版）にリスクスコアを投影する。

    縦軸: スパン方向（Root→Tip）
    横軸: コード方向（LE→Body）
    """
    region_cols = list(REGION_WEIGHTS.keys())
    totals = df[region_cols].sum()

    # 3×2のグリッドに配置
    grid = {
        (0, 0): totals.get("R-LE", 0),
        (0, 1): totals.get("R-Body", 0),
        (1, 0): totals.get("M-LE", 0),
        (1, 1): totals.get("M-Body", 0),
        (2, 0): totals.get("T-LE", 0),
        (2, 1): totals.get("T-Body", 0),
    }

    import numpy as np
    data = np.array([
        [grid[(2, 0)], grid[(2, 1)]],  # Tip
        [grid[(1, 0)], grid[(1, 1)]],  # Mid
        [grid[(0, 0)], grid[(0, 1)]],  # Root
    ])

    fig, ax = plt.subplots(figsize=(6, 8))
    im = ax.imshow(data, cmap="Reds", aspect="auto")
    plt.colorbar(im, ax=ax, label="リスクスコア")

    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Leading Edge", "Body"])
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["Tip（翼端）", "Mid（中間）", "Root（翼根）"])
    ax.set_title("ブレード部位別リスクヒートマップ", fontsize=13)

    for (row, col), val in [
        ((0, 0), data[0, 0]), ((0, 1), data[0, 1]),
        ((1, 0), data[1, 0]), ((1, 1), data[1, 1]),
        ((2, 0), data[2, 0]), ((2, 1), data[2, 1]),
    ]:
        ax.text(col, row, f"{val:.3f}", ha="center", va="center",
                fontsize=12, color="black")

    plt.tight_layout()
    out = REPORT_DIR / "blade_heatmap.png"
    plt.savefig(out, dpi=120)
    print(f"ヒートマップを保存: {out}")


if __name__ == "__main__":
    # サンプルデータで動作確認
    import numpy as np
    rng = np.random.default_rng(42)

    region_cols = list(REGION_WEIGHTS.keys())
    dummy_data = {"image": [f"DJI_{i:04d}_0_0.JPG" for i in range(20)]}
    for r in region_cols:
        # T-LEが高くなるようなダミースコア
        base = 0.05 if r == "T-LE" else 0.01
        dummy_data[r] = rng.uniform(base, base * 3, 20)

    df = pd.DataFrame(dummy_data)

    plot_region_scores(df)
    plot_blade_heatmap(df)

    csv_out = REPORT_DIR / "risk_scores.csv"
    df.to_csv(csv_out, index=False)
    print(f"CSVを保存: {csv_out}")
    print("動作確認完了")
