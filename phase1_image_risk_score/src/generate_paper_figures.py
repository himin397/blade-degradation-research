"""
generate_paper_figures.py
Phase 1 論文投稿用図表の生成（英語ラベル・高解像度）

出力:
  reports/fig_detection_examples_en.png  … TP/FP/FN 代表検出例（英語）
  reports/fig_sensitivity_bars_en.png    … 感度分析 棒グラフ（英語）

既存の week1_analysis.py の日本語版を英語化して再生成する。
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

# ---- パス設定（week1_analysis.py と同一） ----
REPO = Path(__file__).parent.parent.parent
DATA_TEST_IMG = REPO / "data/processed/yolo_dataset/images/test"
DATA_TEST_LBL = REPO / "data/processed/yolo_dataset/labels/test"
PRED_LBL_DIR  = REPO / "runs/detect/data/processed/exp002/predictions/labels"
REPORT_DIR    = REPO / "phase1_image_risk_score/reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

RAW_2017 = REPO / "data/raw/DTU - Drone inspection images of wind turbine/DTU - Drone inspection images of wind turbine/Nordtank 2017"

CLASS_NAMES    = ["VG;MT", "LE;ER", "LR;DA", "LE;CR", "SF;PO"]
CLASS_WEIGHTS  = {"LE;CR": 3.0, "LE;ER": 2.0, "VG;MT": 1.5, "LR;DA": 1.5, "SF;PO": 1.0}
REGION_WEIGHTS_BASE = {"Tip": 3.0, "Mid": 2.0, "Root": 1.0}
IOU_THRESH = 0.5
CONF_THRESH = 0.25


# ---- ユーティリティ ----

def load_labels(path: Path) -> list:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text().strip().split("\n"):
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 5:
            cid = int(parts[0])
            cx, cy, w, h = map(float, parts[1:5])
            conf = float(parts[5]) if len(parts) > 5 else 1.0
            rows.append((cid, cx, cy, w, h, conf))
    return rows


def iou(b1, b2) -> float:
    x1_min = b1[0] - b1[2]/2; x1_max = b1[0] + b1[2]/2
    y1_min = b1[1] - b1[3]/2; y1_max = b1[1] + b1[3]/2
    x2_min = b2[0] - b2[2]/2; x2_max = b2[0] + b2[2]/2
    y2_min = b2[1] - b2[3]/2; y2_max = b2[1] + b2[3]/2
    ix = max(0, min(x1_max, x2_max) - max(x1_min, x2_min))
    iy = max(0, min(y1_max, y2_max) - max(y1_min, y2_min))
    inter = ix * iy
    union = b1[2]*b1[3] + b2[2]*b2[3] - inter
    return inter / union if union > 0 else 0.0


def span_region(stem: str) -> str:
    parts = stem.split("_")
    try:
        row = int(parts[2])
        return "Tip" if row == 0 else ("Mid" if row == 1 else "Root")
    except (IndexError, ValueError):
        return "Mid"


def calc_scores(pred_labels: list, stem: str, rw: dict) -> dict:
    scores = {r: 0.0 for r in rw}
    region = span_region(stem)
    for cid, cx, cy, w, h, conf in pred_labels:
        cname = CLASS_NAMES[cid] if cid < len(CLASS_NAMES) else "unknown"
        cw = CLASS_WEIGHTS.get(cname, 1.0)
        area = w * h
        scores[region] += conf * area * cw * rw[region]
    return scores


# ==============================
# Fig 1: Detection Examples（英語）
# ==============================

def fig_detection_examples_en():
    print("=== Fig 1: Detection Examples (English) ===")
    test_imgs = sorted(DATA_TEST_IMG.glob("*.JPG"))

    tp_case = fp_case = fn_case = None

    for img_path in test_imgs:
        stem = img_path.stem
        gt   = load_labels(DATA_TEST_LBL / (stem + ".txt"))
        pred = [p for p in load_labels(PRED_LBL_DIR / (stem + ".txt")) if p[4] >= CONF_THRESH]

        if not gt and not pred:
            continue

        matched_gt = set()
        matched_pred = set()
        for pi, p in enumerate(pred):
            for gi, g in enumerate(gt):
                if p[0] == g[0] and iou(p[1:5], g[1:5]) >= IOU_THRESH:
                    if gi not in matched_gt and pi not in matched_pred:
                        matched_gt.add(gi)
                        matched_pred.add(pi)

        has_tp = len(matched_gt) > 0
        has_fp = any(pi not in matched_pred for pi in range(len(pred)))
        has_fn = any(gi not in matched_gt for gi in range(len(gt)))

        if tp_case is None and has_tp and not has_fp:
            tp_case = (img_path, gt, pred, "TP (True Positive)")
        if fp_case is None and has_fp and gt:
            fp_case = (img_path, gt, pred, "FP (False Positive)")
        if fn_case is None and has_fn and not pred:
            fn_case = (img_path, gt, pred, "FN (False Negative)")
        if tp_case and fp_case and fn_case:
            break

    cases = [c for c in [tp_case, fp_case, fn_case] if c]
    if not cases:
        print("  No representative examples found.")
        return

    color_gt   = "#2ca02c"   # green
    color_pred = "#1f77b4"   # blue

    fig, axes = plt.subplots(1, len(cases), figsize=(7 * len(cases), 6))
    if len(cases) == 1:
        axes = [axes]

    for ax, (img_path, gt, pred, label) in zip(axes, cases):
        img = Image.open(img_path)
        W, H = img.size
        ax.imshow(img)
        ax.set_title(label, fontsize=13, fontweight="bold")
        ax.axis("off")

        for g in gt:
            cid, cx, cy, w, h = g[:5]
            x = (cx - w/2) * W; y = (cy - h/2) * H
            rect = patches.Rectangle((x, y), w*W, h*H,
                                      linewidth=2, edgecolor=color_gt, facecolor="none")
            ax.add_patch(rect)
            ax.text(x, y - 3, f"GT: {CLASS_NAMES[cid]}",
                    color=color_gt, fontsize=7, backgroundcolor="white")

        for p in pred:
            cid, cx, cy, w, h, conf = p
            x = (cx - w/2) * W; y = (cy - h/2) * H
            rect = patches.Rectangle((x, y), w*W, h*H,
                                      linewidth=2, edgecolor=color_pred,
                                      facecolor="none", linestyle="--")
            ax.add_patch(rect)
            ax.text(x, y + h*H + 3, f"Pred: {CLASS_NAMES[cid]} ({conf:.2f})",
                    color=color_pred, fontsize=7, backgroundcolor="white")

    from matplotlib.lines import Line2D
    legend = [
        Line2D([0], [0], color=color_gt,   lw=2,        label="Ground Truth"),
        Line2D([0], [0], color=color_pred, lw=2, ls="--", label="Prediction (EXP-002)"),
    ]
    fig.legend(handles=legend, loc="lower center", ncol=2, fontsize=11)
    plt.suptitle("YOLOv8n EXP-002: Representative Detection Results (test set, IoU≥0.5, conf≥0.25)",
                 fontsize=12, fontweight="bold", y=1.01)
    plt.tight_layout()
    out = REPORT_DIR / "fig_detection_examples_en.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")
    for c in cases:
        print(f"  {c[3]}: {c[0].name}")


# ==============================
# Fig 2: Sensitivity Analysis（英語）
# ==============================

def fig_sensitivity_bars_en():
    print("=== Fig 2: Sensitivity Analysis (English) ===")

    all_stems = [p.stem for p in sorted(DATA_TEST_IMG.glob("*.JPG"))]
    # 論文 §4.3 Table と同条件: conf 閾値なし（全検出を使用）
    all_preds = {s: load_labels(PRED_LBL_DIR / (s + ".txt"))
                 for s in all_stems}

    def total_scores(rw: dict) -> dict:
        totals = {r: 0.0 for r in rw}
        for stem, pred in all_preds.items():
            s = calc_scores(pred, stem, rw)
            for r in rw:
                totals[r] += s[r]
        return totals

    base_scores = total_scores(REGION_WEIGHTS_BASE)
    base_rank   = sorted(base_scores, key=base_scores.get, reverse=True)

    # Region weight sensitivity
    scenarios = {}
    for region in REGION_WEIGHTS_BASE:
        for delta, label in [(+0.5, "×1.5"), (-0.5, "×0.5")]:
            rw_mod = {r: v * (1 + delta if r == region else 1.0)
                      for r, v in REGION_WEIGHTS_BASE.items()}
            key = f"RW:{region} {label}"
            scenarios[key] = total_scores(rw_mod)

    # Class weight sensitivity
    for delta, label in [(+0.5, "×1.5"), (-0.5, "×0.5")]:
        cw_mod = {k: v * (1 + delta) for k, v in CLASS_WEIGHTS.items()}
        def total_scores_cw(rw, cw=cw_mod):
            totals = {r: 0.0 for r in rw}
            for stem, pred in all_preds.items():
                region = span_region(stem)
                for cid, cx, cy, w, h, conf in pred:
                    cname = CLASS_NAMES[cid] if cid < len(CLASS_NAMES) else "unknown"
                    area = w * h
                    totals[region] += conf * area * cw.get(cname, 1.0) * rw[region]
            return totals
        key = f"CW:all {label}"
        scenarios[key] = total_scores_cw(REGION_WEIGHTS_BASE)

    regions = list(REGION_WEIGHTS_BASE.keys())
    base_vals = [base_scores[r] for r in regions]

    # 2パネル構成
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Left panel: grouped bar chart (region weight scenarios)
    ax = axes[0]
    rw_keys = [k for k in scenarios if k.startswith("RW:")]
    n = len(rw_keys)
    x = np.arange(len(regions))
    w = 0.55 / (n + 1)
    colors = plt.cm.tab10(np.linspace(0, 0.7, n))

    ax.bar(x, base_vals, w * 0.9, label="Baseline", color="black", alpha=0.5, zorder=3)
    for i, key in enumerate(rw_keys):
        vals = [scenarios[key][r] for r in regions]
        offset = (i - n / 2) * w + w
        rank = sorted(scenarios[key], key=scenarios[key].get, reverse=True)
        rank_changed = rank != base_rank
        lbl = key + (" ★" if rank_changed else "")
        ax.bar(x + offset, vals, w * 0.9, label=lbl, color=colors[i], alpha=0.8)

    for xi, v in zip(x, base_vals):
        ax.text(xi, v + max(base_vals) * 0.01, f"{v:.3f}",
                ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(regions, fontsize=12)
    ax.set_ylabel("Cumulative Risk Score (test set)", fontsize=11)
    ax.set_title("Region Weight Sensitivity (±50%)\n★ = rank inversion", fontsize=11)
    ax.legend(fontsize=8, loc="upper right", ncol=1)
    ax.grid(alpha=0.3, axis="y")

    # Right panel: class weight scenarios
    ax = axes[1]
    cw_keys = [k for k in scenarios if k.startswith("CW:")]
    n2 = len(cw_keys)
    w2 = 0.55 / (n2 + 1)
    colors2 = ["#e377c2", "#7f7f7f"]

    ax.bar(x, base_vals, w2 * 0.9, label="Baseline", color="black", alpha=0.5, zorder=3)
    for i, key in enumerate(cw_keys):
        vals = [scenarios[key][r] for r in regions]
        offset = (i - n2 / 2) * w2 + w2
        rank = sorted(scenarios[key], key=scenarios[key].get, reverse=True)
        rank_changed = rank != base_rank
        lbl = key + (" ★" if rank_changed else "")
        ax.bar(x + offset, vals, w2 * 0.9, label=lbl, color=colors2[i], alpha=0.8)

    for xi, v in zip(x, base_vals):
        ax.text(xi, v + max(base_vals) * 0.01, f"{v:.3f}",
                ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(regions, fontsize=12)
    ax.set_ylabel("Cumulative Risk Score (test set)", fontsize=11)
    ax.set_title("Class Weight Sensitivity (all classes ±50%)\n★ = rank inversion", fontsize=11)
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(alpha=0.3, axis="y")

    plt.suptitle(
        "Risk Score Sensitivity Analysis: Region Weight and Class Weight Perturbation (±50%)\n"
        "Baseline: Tip=3.0, Mid=2.0, Root=1.0 | Class weights: LE;CR=3.0, LE;ER=2.0, VG;MT=LR;DA=1.5, SF;PO=1.0",
        fontsize=11, fontweight="bold"
    )
    plt.tight_layout()
    out = REPORT_DIR / "fig_sensitivity_bars_en.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")

    # ランク変動サマリー
    print(f"\n  Baseline rank: {' > '.join(base_rank)}")
    print(f"  Baseline scores: { {r: f'{base_scores[r]:.3f}' for r in regions} }")
    print()
    for key, sc in scenarios.items():
        rank = sorted(sc, key=sc.get, reverse=True)
        changed = "RANK CHANGED ★" if rank != base_rank else "stable"
        print(f"  {key:25s}: {' > '.join(rank)}  [{changed}]")


# ==============================
# メイン
# ==============================

if __name__ == "__main__":
    print("=== Phase 1 Paper Figures (English) ===\n")
    fig_detection_examples_en()
    print()
    fig_sensitivity_bars_en()
    print("\n=== Done ===")
