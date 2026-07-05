"""
Phase 1: test セット per-class AP 評価（EXP-001 / EXP-002 共通）

week1_analysis.py の task2_class_ap() と同一条件（split="test", imgsz=640,
conf=0.25, iou=0.5）で任意の重みを評価し、per-class AP50 / AP50-95 を CSV 保存する。

背景: mAP 提示方法の案a（test を主指標化）採用に伴い、EXP-001 ベースラインの
test 評価が必要になった（監査記録 A-2/A-3/D 項参照）。exp002 の再評価が
reports/table_class_ap.csv（0.5605）を再現することを先に確認してから使う。

使い方:
    python phase1_image_risk_score/src/eval_test_per_class.py --exp exp001_baseline_yolov8n
    python phase1_image_risk_score/src/eval_test_per_class.py --exp exp002_pyramid_yolov8n
"""

import argparse
from pathlib import Path
import pandas as pd

REPO = Path(__file__).parent.parent.parent
DATASET_YAML = REPO / "data/processed/yolo_dataset/dataset.yaml"
REPORT_DIR = REPO / "phase1_image_risk_score" / "reports"
CLASS_NAMES = ["VG;MT", "LE;ER", "LR;DA", "LE;CR", "SF;PO"]
IOU_THRESH = 0.5
CONF_THRESH = 0.25


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp", required=True,
                        help="experiments/ 以下の実験フォルダ名")
    args = parser.parse_args()

    from ultralytics import YOLO

    weights = REPO / "experiments" / args.exp / "weights" / "best.pt"
    if not weights.exists():
        raise FileNotFoundError(weights)

    model = YOLO(str(weights))
    results = model.val(
        data=str(DATASET_YAML),
        split="test",
        imgsz=640,
        conf=CONF_THRESH,
        iou=IOU_THRESH,
        verbose=False,
        save=False,
    )

    ap50_per_class = results.box.ap50
    ap_per_class = results.box.ap
    p_per_class = results.box.p   # F1最適点のクラス別Precision（ultralytics仕様）
    r_per_class = results.box.r

    rows = []
    for i, name in enumerate(CLASS_NAMES):
        rows.append({
            "class": name,
            "AP50": float(ap50_per_class[i]) if i < len(ap50_per_class) else float("nan"),
            "AP50-95": float(ap_per_class[i]) if i < len(ap_per_class) else float("nan"),
            "P": float(p_per_class[i]) if i < len(p_per_class) else float("nan"),
            "R": float(r_per_class[i]) if i < len(r_per_class) else float("nan"),
        })
    df = pd.DataFrame(rows).sort_values("AP50", ascending=False)
    df.loc[len(df)] = {"class": "mAP（平均）",
                       "AP50": float(results.box.map50),
                       "AP50-95": float(results.box.map),
                       "P": float(results.box.mp),
                       "R": float(results.box.mr)}

    out_csv = REPORT_DIR / f"table_class_ap_{args.exp}.csv"
    df.to_csv(out_csv, index=False)
    print(df.to_string(index=False))
    print(f"保存: {out_csv}")


if __name__ == "__main__":
    main()
