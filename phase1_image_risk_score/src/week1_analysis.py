"""
week1_analysis.py
Week 1: Phase 1 不足図表・分析の一括生成

出力:
  reports/fig_detection_examples.png  … 正解/誤検出/見逃し 代表例
  reports/table_class_ap.csv          … クラス別AP（EXP-002）
  reports/table_risk_scores_by_year.csv … 部位別リスクスコア（2017/2018）
  reports/fig_risk_scores_by_year.png
  reports/table_sensitivity.csv       … 感度分析（±50%重み変動）
  reports/fig_sensitivity.png
"""

import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

# ---- パス設定 ----
REPO = Path(__file__).parent.parent.parent
DATA_TEST_IMG  = REPO / "data/processed/yolo_dataset/images/test"
DATA_TEST_LBL  = REPO / "data/processed/yolo_dataset/labels/test"
PRED_LBL_DIR   = REPO / "runs/detect/data/processed/exp002/predictions/labels"
MODEL_PATH     = REPO / "runs/detect/runs/detect/phase1_image_risk_score/experiments/pyramid_yolov8n/weights/best.pt"
DATASET_YAML   = REPO / "data/processed/yolo_dataset/dataset.yaml"
REPORT_DIR     = REPO / "phase1_image_risk_score/reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

RAW_2017 = REPO / "data/raw/DTU - Drone inspection images of wind turbine/DTU - Drone inspection images of wind turbine/Nordtank 2017"
RAW_2018 = REPO / "data/raw/DTU - Drone inspection images of wind turbine/DTU - Drone inspection images of wind turbine/Nordtank 2018"

CLASS_NAMES = ["VG;MT", "LE;ER", "LR;DA", "LE;CR", "SF;PO"]
CLASS_WEIGHTS = {"LE;CR": 3.0, "LE;ER": 2.0, "VG;MT": 1.5, "LR;DA": 1.5, "SF;PO": 1.0}
REGION_WEIGHTS_BASE = {"Tip": 3.0, "Mid": 2.0, "Root": 1.0}

IOU_THRESH = 0.5
CONF_THRESH = 0.25

# ---- ユーティリティ ----

def get_year(stem: str) -> str:
    """パッチファイル名（例: DJI_0578_0_2）の年を返す。"""
    ids_2017 = {f.stem.split("(")[0] for f in RAW_2017.glob("*.JPG")}
    ids_2017 = {s for s in ids_2017 if not s.endswith(")")}
    base = "_".join(stem.split("_")[:2])  # DJI_0578
    return "2017" if base in ids_2017 else "2018"


def load_labels(path: Path) -> list:
    """YOLO形式ラベルを読み込む。[(class_id, cx, cy, w, h, conf), ...]"""
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
    """(cx,cy,w,h) 形式のIoUを計算する。"""
    x1_min = b1[0] - b1[2] / 2; x1_max = b1[0] + b1[2] / 2
    y1_min = b1[1] - b1[3] / 2; y1_max = b1[1] + b1[3] / 2
    x2_min = b2[0] - b2[2] / 2; x2_max = b2[0] + b2[2] / 2
    y2_min = b2[1] - b2[3] / 2; y2_max = b2[1] + b2[3] / 2
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
# タスク1: 代表検出画像
# ==============================

def task1_detection_examples():
    print("=== Task 1: 代表検出画像 ===")
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
                        matched_gt.add(gi); matched_pred.add(pi)

        has_tp = len(matched_gt) > 0
        has_fp = any(pi not in matched_pred for pi in range(len(pred)))
        has_fn = any(gi not in matched_gt for gi in range(len(gt)))

        if tp_case is None and has_tp and not has_fp:
            tp_case = (img_path, gt, pred, "TP（正解）")
        if fp_case is None and has_fp and gt:
            fp_case = (img_path, gt, pred, "FP（誤検出）")
        if fn_case is None and has_fn and not pred:
            fn_case = (img_path, gt, pred, "FN（見逃し）")
        if tp_case and fp_case and fn_case:
            break

    cases = [c for c in [tp_case, fp_case, fn_case] if c]
    if not cases:
        print("  代表例が見つかりませんでした")
        return

    colors = {"GT": "#2ca02c", "Pred-Match": "#1f77b4", "Pred-Miss": "#d62728", "GT-Missed": "#ff7f0e"}

    fig, axes = plt.subplots(1, len(cases), figsize=(7 * len(cases), 6))
    if len(cases) == 1:
        axes = [axes]

    for ax, (img_path, gt, pred, label) in zip(axes, cases):
        img = Image.open(img_path)
        W, H = img.size
        ax.imshow(img)
        ax.set_title(label, fontsize=12, fontweight="bold")
        ax.axis("off")

        # GT boxes（緑）
        for g in gt:
            cid, cx, cy, w, h = g[:5]
            x = (cx - w/2) * W; y = (cy - h/2) * H
            rect = patches.Rectangle((x, y), w*W, h*H,
                                      linewidth=2, edgecolor=colors["GT"],
                                      facecolor="none")
            ax.add_patch(rect)
            ax.text(x, y - 3, f"GT:{CLASS_NAMES[cid]}", color=colors["GT"],
                    fontsize=7, backgroundcolor="white")

        # Pred boxes（青）
        for p in pred:
            cid, cx, cy, w, h, conf = p
            x = (cx - w/2) * W; y = (cy - h/2) * H
            rect = patches.Rectangle((x, y), w*W, h*H,
                                      linewidth=2, edgecolor=colors["Pred-Match"],
                                      facecolor="none", linestyle="--")
            ax.add_patch(rect)
            ax.text(x, y + h*H + 3, f"Pred:{CLASS_NAMES[cid]}({conf:.2f})",
                    color=colors["Pred-Match"], fontsize=7, backgroundcolor="white")

    from matplotlib.lines import Line2D
    legend = [
        Line2D([0], [0], color=colors["GT"], lw=2, label="GT（正解ラベル）"),
        Line2D([0], [0], color=colors["Pred-Match"], lw=2, ls="--", label="Pred（モデル出力）"),
    ]
    fig.legend(handles=legend, loc="lower center", ncol=2, fontsize=10)
    plt.suptitle("YOLOv8 EXP-002 代表検出結果（test set）", fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    out = REPORT_DIR / "fig_detection_examples.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"  保存: {out}")
    for c in cases:
        print(f"  {c[3]}: {c[0].name}")


# ==============================
# タスク2: クラス別AP（EXP-002）
# ==============================

def task2_class_ap():
    print("=== Task 2: クラス別AP ===")
    try:
        from ultralytics import YOLO
    except ImportError:
        print("  ultralytics が見つかりません。blade-phase1 環境で実行してください。")
        return

    model = YOLO(str(MODEL_PATH))
    results = model.val(
        data=str(DATASET_YAML),
        split="test",
        imgsz=640,
        conf=CONF_THRESH,
        iou=IOU_THRESH,
        verbose=False,
        save=False,
    )

    # per-class AP50
    ap50_per_class = results.box.ap50  # shape: (n_classes,)
    ap_per_class   = results.box.ap    # AP50-95

    rows = []
    for i, name in enumerate(CLASS_NAMES):
        rows.append({
            "class": name,
            "AP50": float(ap50_per_class[i]) if i < len(ap50_per_class) else float("nan"),
            "AP50-95": float(ap_per_class[i]) if i < len(ap_per_class) else float("nan"),
        })
    df = pd.DataFrame(rows).sort_values("AP50", ascending=False)
    df.loc[len(df)] = {"class": "mAP（平均）",
                       "AP50": float(results.box.map50),
                       "AP50-95": float(results.box.map)}

    out_csv = REPORT_DIR / "table_class_ap.csv"
    df.to_csv(out_csv, index=False)
    print(df.to_string(index=False))
    print(f"  保存: {out_csv}")
    return df


# ==============================
# タスク3: 部位別リスクスコア（2017/2018）
# ==============================

def task3_risk_scores_by_year():
    print("=== Task 3: 部位別リスクスコア（2017/2018）===")

    # 2017の元画像IDセットを構築
    ids_2017 = set()
    for f in RAW_2017.glob("*.JPG"):
        stem = f.stem.split("(")[0].strip()
        ids_2017.add(stem)

    records = []
    for img_path in sorted(DATA_TEST_IMG.glob("*.JPG")):
        stem = img_path.stem
        base = "_".join(stem.split("_")[:2])
        year = "2017" if base in ids_2017 else "2018"
        pred = load_labels(PRED_LBL_DIR / (stem + ".txt"))
        scores = calc_scores(pred, stem, REGION_WEIGHTS_BASE)
        records.append({"stem": stem, "year": year, **scores})

    df = pd.DataFrame(records)
    agg = df.groupby("year")[list(REGION_WEIGHTS_BASE.keys())].sum().reset_index()
    agg["n_patches"] = df.groupby("year").size().values

    out_csv = REPORT_DIR / "table_risk_scores_by_year.csv"
    agg.to_csv(out_csv, index=False)
    print(agg.to_string(index=False))

    # 可視化
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    regions = list(REGION_WEIGHTS_BASE.keys())
    x = np.arange(len(regions))
    w = 0.35
    colors17 = "#1f77b4"; colors18 = "#ff7f0e"

    row17 = agg[agg["year"] == "2017"].iloc[0]
    row18 = agg[agg["year"] == "2018"].iloc[0]
    n17 = int(row17["n_patches"]); n18 = int(row18["n_patches"])

    # 絶対値
    axes[0].bar(x - w/2, [row17[r] for r in regions], w, label=f"2017 (n={n17})", color=colors17)
    axes[0].bar(x + w/2, [row18[r] for r in regions], w, label=f"2018 (n={n18})", color=colors18)
    axes[0].set_xticks(x); axes[0].set_xticklabels(regions)
    axes[0].set_ylabel("累積リスクスコア")
    axes[0].set_title("部位別リスクスコア（累積）")
    axes[0].legend(); axes[0].grid(alpha=0.3, axis="y")

    # パッチ数正規化
    axes[1].bar(x - w/2, [row17[r]/n17 for r in regions], w, label=f"2017", color=colors17)
    axes[1].bar(x + w/2, [row18[r]/n18 for r in regions], w, label=f"2018", color=colors18)
    axes[1].set_xticks(x); axes[1].set_xticklabels(regions)
    axes[1].set_ylabel("リスクスコア / パッチ数")
    axes[1].set_title("部位別リスクスコア（パッチ数正規化）")
    axes[1].legend(); axes[1].grid(alpha=0.3, axis="y")

    plt.suptitle("部位別リスクスコア：2017年 vs 2018年（EXP-002, test set）", fontsize=13)
    plt.tight_layout()
    out_png = REPORT_DIR / "fig_risk_scores_by_year.png"
    plt.savefig(out_png, dpi=150, bbox_inches="tight")
    print(f"  保存: {out_csv}\n  保存: {out_png}")
    return agg


# ==============================
# タスク4: 感度分析（重み±50%）
# ==============================

def task4_sensitivity():
    print("=== Task 4: 感度分析（重み±50%）===")

    # 全テスト画像のスコアを基準重みで計算
    all_stems = [p.stem for p in sorted(DATA_TEST_IMG.glob("*.JPG"))]
    all_preds = {s: load_labels(PRED_LBL_DIR / (s + ".txt")) for s in all_stems}

    def total_scores(rw: dict) -> dict:
        totals = {r: 0.0 for r in rw}
        for stem, pred in all_preds.items():
            s = calc_scores(pred, stem, rw)
            for r in rw:
                totals[r] += s[r]
        return totals

    base_scores = total_scores(REGION_WEIGHTS_BASE)
    base_rank   = sorted(base_scores, key=base_scores.get, reverse=True)

    # --- region_weight感度 ---
    rw_scenarios = {}
    for region in REGION_WEIGHTS_BASE:
        for delta, label in [(+0.5, "+50%"), (-0.5, "-50%")]:
            rw_mod = {r: v * (1 + delta if r == region else 1.0)
                      for r, v in REGION_WEIGHTS_BASE.items()}
            scenario = f"RW:{region}{label}"
            rw_scenarios[scenario] = total_scores(rw_mod)

    # --- class_weight感度（全クラス同率変化）---
    for delta, label in [(+0.5, "+50%"), (-0.5, "-50%")]:
        cw_mod = {k: v * (1 + delta) for k, v in CLASS_WEIGHTS.items()}
        # class_weightをcalc_scoresに渡すため一時的に外部からパラメータとして渡す版を作る
        def total_scores_cw(rw, cw):
            totals = {r: 0.0 for r in rw}
            for stem, pred in all_preds.items():
                region = span_region(stem)
                for cid, cx, cy, w, h, conf in pred:
                    cname = CLASS_NAMES[cid] if cid < len(CLASS_NAMES) else "unknown"
                    area = w * h
                    totals[region] += conf * area * cw.get(cname, 1.0) * rw[region]
            return totals
        scenario = f"CW:all{label}"
        rw_scenarios[scenario] = total_scores_cw(REGION_WEIGHTS_BASE, cw_mod)

    rows = []
    for scenario, scores in rw_scenarios.items():
        rank = sorted(scores, key=scores.get, reverse=True)
        rank_changed = rank != base_rank
        rows.append({
            "scenario": scenario,
            **{f"score_{r}": scores[r] for r in REGION_WEIGHTS_BASE},
            "rank_order": " > ".join(rank),
            "rank_changed": rank_changed,
        })

    df = pd.DataFrame(rows)
    out_csv = REPORT_DIR / "table_sensitivity.csv"
    df.to_csv(out_csv, index=False)

    print(f"  基準ランク: {' > '.join(base_rank)}")
    print(f"  基準スコア: {base_scores}")
    print()
    rank_stable = all(not r for r in df["rank_changed"])
    print(f"  ランク変動なし: {rank_stable}")
    for _, row in df.iterrows():
        changed = "★変動" if row["rank_changed"] else "安定"
        print(f"  {row['scenario']:30s}: {row['rank_order']}  [{changed}]")

    # 可視化（スコア変動の棒グラフ）
    regions = list(REGION_WEIGHTS_BASE.keys())
    base_vals = [base_scores[r] for r in regions]

    fig, ax = plt.subplots(figsize=(14, 6))
    n_scenarios = len(df)
    x = np.arange(len(regions))
    width = 0.6 / (n_scenarios + 1)
    colors = plt.cm.tab20(np.linspace(0, 1, n_scenarios))

    ax.bar(x, base_vals, width * 0.8, label="基準", color="black", alpha=0.5, zorder=3)
    for i, (_, row) in enumerate(df.iterrows()):
        vals = [row[f"score_{r}"] for r in regions]
        offset = (i - n_scenarios/2) * width
        label_str = row["scenario"] + ("★" if row["rank_changed"] else "")
        ax.bar(x + offset + width, vals, width * 0.8,
               label=label_str, color=colors[i], alpha=0.7)

    ax.set_xticks(x + width/2)
    ax.set_xticklabels(regions, fontsize=11)
    ax.set_ylabel("累積リスクスコア（test set）")
    ax.set_title("感度分析：region_weight / class_weight ±50% 変動時のスコア変動\n★=ランク変動あり")
    ax.legend(fontsize=7, loc="upper right", ncol=2)
    ax.grid(alpha=0.3, axis="y")

    # 基準スコアのテキスト
    for xi, v in zip(x, base_vals):
        ax.text(xi + width/2, v + max(base_vals)*0.01, f"{v:.3f}",
                ha="center", va="bottom", fontsize=8, fontweight="bold")

    plt.tight_layout()
    out_png = REPORT_DIR / "fig_sensitivity.png"
    plt.savefig(out_png, dpi=150, bbox_inches="tight")
    print(f"\n  保存: {out_csv}\n  保存: {out_png}")
    return df


# ==============================
# メイン
# ==============================

if __name__ == "__main__":
    print("=== Week 1 Analysis ===\n")
    task1_detection_examples()
    print()
    task2_class_ap()
    print()
    task3_risk_scores_by_year()
    print()
    task4_sensitivity()
    print("\n=== 完了 ===")
