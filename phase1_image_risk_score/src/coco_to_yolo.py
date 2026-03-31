"""
Phase 1 W04: COCOアノテーション → YOLOv8形式変換スクリプト

データソース（一次ソース）:
  画像: DTU/Mendeley DOI: 10.17632/hd96prn3nc.2
  アノテーション: github.com/imadgohar/DTU-annotations

アノテーション形式:
  入力: COCO JSON (bbox: [x_min, y_min, width, height])
  出力: YOLO txt (class cx cy w h、すべて正規化済み)

クラス定義（5クラス）:
  0: VG;MT  - Vortex Generator Missing Teeth
  1: LE;ER  - Leading Edge Erosion  ← 本研究の主要対象
  2: LR;DA  - Lightning Receptor Damage
  3: LE;CR  - Leading Edge Crack
  4: SF;PO  - Surface Pockmark/Other

注意: COCOのcategory_id と YOLOのclass_idは別物。
     このスクリプトで正しくマッピングする。
"""

import json
from pathlib import Path
import shutil


# パス定義（リポジトリルートからの相対パス）
REPO_ROOT = Path(__file__).parent.parent.parent
DATA_RAW = REPO_ROOT / "data" / "raw"
DATA_PROCESSED = REPO_ROOT / "data" / "processed"

ANNO_DIR = DATA_RAW / "DTU-annotations" / "annotations"
IMAGE_DIR = DATA_RAW / "DTU - Drone inspection images of wind turbine" / "DTU - Drone inspection images of wind turbine"

# COCO category_id → YOLO class_id のマッピング
# （COCOのidは0,1,2,3,4が飛び番になっているため明示的に定義）
CATEGORY_MAP = {
    0: {"yolo_id": 0, "name": "VG;MT"},
    1: {"yolo_id": 1, "name": "LE;ER"},
    2: {"yolo_id": 2, "name": "LR;DA"},
    3: {"yolo_id": 3, "name": "LE;CR"},
    4: {"yolo_id": 4, "name": "SF;PO"},
}

CLASS_NAMES = ["VG;MT", "LE;ER", "LR;DA", "LE;CR", "SF;PO"]


def coco_bbox_to_yolo(bbox, img_width, img_height):
    """
    COCO形式のbbox → YOLO形式に変換。

    COCO: [x_min, y_min, width, height]（ピクセル絶対値）
    YOLO: [center_x, center_y, width, height]（0〜1に正規化）
    """
    x_min, y_min, w, h = bbox
    cx = (x_min + w / 2) / img_width
    cy = (y_min + h / 2) / img_height
    nw = w / img_width
    nh = h / img_height
    return cx, cy, nw, nh


def convert_coco_to_yolo(json_path: Path, output_dir: Path):
    """
    COCOアノテーションJSONをYOLO形式のtxtファイル群に変換する。
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(json_path) as f:
        data = json.load(f)

    # image_id → image情報 の辞書
    img_dict = {img["id"]: img for img in data["images"]}

    # image_id → annotations のリスト辞書
    ann_dict = {}
    for ann in data["annotations"]:
        iid = ann["image_id"]
        ann_dict.setdefault(iid, []).append(ann)

    converted = 0
    skipped = 0

    for img_id, img_info in img_dict.items():
        file_name = img_info["file_name"]
        img_w = img_info["width"]
        img_h = img_info["height"]

        txt_name = Path(file_name).stem + ".txt"
        txt_path = output_dir / txt_name

        annotations = ann_dict.get(img_id, [])
        lines = []
        for ann in annotations:
            cat_id = ann["category_id"]
            if cat_id not in CATEGORY_MAP:
                skipped += 1
                continue
            yolo_id = CATEGORY_MAP[cat_id]["yolo_id"]
            cx, cy, w, h = coco_bbox_to_yolo(ann["bbox"], img_w, img_h)
            lines.append(f"{yolo_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")

        txt_path.write_text("\n".join(lines))
        converted += 1

    print(f"  変換完了: {converted}件, スキップ: {skipped}件")
    return converted


def create_dataset_yaml(output_dir: Path):
    """YOLOv8用のdataset.yamlを生成する。"""
    yaml_content = f"""# YOLOv8 Dataset Configuration
# 画像データ: DTU/Mendeley DOI: 10.17632/hd96prn3nc.2
# アノテーション: github.com/imadgohar/DTU-annotations (Gohar et al. 2023)

path: {output_dir.resolve()}
train: images/train
val: images/val
test: images/test

nc: {len(CLASS_NAMES)}
names: {CLASS_NAMES}
"""
    (output_dir / "dataset.yaml").write_text(yaml_content)
    print(f"  dataset.yaml を作成しました: {output_dir / 'dataset.yaml'}")


if __name__ == "__main__":
    print("=== COCO → YOLO 変換開始 ===")
    print()

    splits = {
        "train": ANNO_DIR / "train1024-s.json",
        "val":   ANNO_DIR / "val1024-s.json",
        "test":  ANNO_DIR / "test1024-s.json",
    }

    output_base = DATA_PROCESSED / "yolo_dataset"

    for split_name, json_path in splits.items():
        print(f"[{split_name}] {json_path.name}")
        label_dir = output_base / "labels" / split_name
        convert_coco_to_yolo(json_path, label_dir)

    create_dataset_yaml(output_base)
    print()
    print("=== 完了 ===")
    print(f"出力先: {output_base}")
    print()
    print("次のステップ: パッチ画像の生成（slice_images.py）が必要です。")
    print("アノテーションは1024pxパッチ基準のため、元画像をスライスしてください。")
