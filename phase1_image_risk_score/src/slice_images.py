"""
Phase 1 W04: 高解像度画像を1024pxパッチにスライスするスクリプト

背景:
  DTU原画像は5280×2970pxの高解像度。
  アノテーション（DTU-annotations）は1024×1024pxパッチ基準で作られている。
  YOLOv8学習には画像とアノテーションの解像度を合わせる必要がある。

パッチ命名規則（DTU-annotationsに準拠）:
  元ファイル: DJI_0058.JPG
  パッチ例:   DJI_0058_0_0.JPG, DJI_0058_0_1.JPG, ...
              （_行インデックス_列インデックス）

データリーク防止:
  元画像単位でtrain/val/testを分割し、
  同一元画像のパッチが異なるsplitに入らないようにする。
"""

from pathlib import Path
from PIL import Image
import json


REPO_ROOT = Path(__file__).parent.parent.parent
DATA_RAW = REPO_ROOT / "data" / "raw"
DATA_PROCESSED = REPO_ROOT / "data" / "processed"

IMAGE_DIR = DATA_RAW / "DTU - Drone inspection images of wind turbine" / \
            "DTU - Drone inspection images of wind turbine"
ANNO_DIR  = DATA_RAW / "DTU-annotations" / "annotations"

PATCH_SIZE = 1024


def get_base_name(filename: str) -> str:
    """
    パッチファイル名から元画像名を取得する。
    例: DJI_0058_1_3.JPG → DJI_0058
    """
    stem = Path(filename).stem
    parts = stem.split("_")
    # DJI_XXXX_row_col → DJI_XXXX
    return "_".join(parts[:2])


def collect_split_base_names(anno_dir: Path) -> dict:
    """
    各splitに含まれる元画像名（ベース名）を収集する。
    データリーク確認に使用。
    """
    splits = {}
    for split in ["train", "val", "test"]:
        json_file = anno_dir / f"{split}1024-s.json" if split != "test" else anno_dir / "test1024-s.json"
        if split == "train":
            json_file = anno_dir / "train1024-s.json"
        elif split == "val":
            json_file = anno_dir / "val1024-s.json"
        else:
            json_file = anno_dir / "test1024-s.json"

        with open(json_file) as f:
            data = json.load(f)

        base_names = set()
        for img in data["images"]:
            base_names.add(get_base_name(img["file_name"]))
        splits[split] = base_names

    return splits


def check_data_leak(splits: dict):
    """splitをまたぐ元画像がないかチェック。"""
    print("=== データリーク確認 ===")
    all_splits = list(splits.keys())
    leak_found = False

    for i, s1 in enumerate(all_splits):
        for s2 in all_splits[i+1:]:
            overlap = splits[s1] & splits[s2]
            if overlap:
                print(f"  警告: {s1}と{s2}に重複あり: {overlap}")
                leak_found = True

    if not leak_found:
        print("  OK: splitをまたぐ元画像なし")

    for split, names in splits.items():
        print(f"  {split}: 元画像{len(names)}枚")


def slice_image(img_path: Path, output_dir: Path, patch_size: int = PATCH_SIZE):
    """
    1枚の高解像度画像を patch_size×patch_size のパッチにスライスする。
    DTU-annotationsのパッチ命名規則に従う。
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    img = Image.open(img_path)
    W, H = img.size
    stem = img_path.stem

    patches = []
    row = 0
    y = 0
    while y < H:
        col = 0
        x = 0
        while x < W:
            x2 = min(x + patch_size, W)
            y2 = min(y + patch_size, H)
            patch = img.crop((x, y, x2, y2))

            # 端パッチはpatch_sizeに満たないのでパディング
            if patch.size != (patch_size, patch_size):
                padded = Image.new("RGB", (patch_size, patch_size), (0, 0, 0))
                padded.paste(patch, (0, 0))
                patch = padded

            patch_name = f"{stem}_{row}_{col}.JPG"
            patch.save(output_dir / patch_name, "JPEG", quality=95)
            patches.append(patch_name)
            col += 1
            x += patch_size
        row += 1
        y += patch_size

    return patches


if __name__ == "__main__":
    print("=== データリーク確認 ===")
    splits = collect_split_base_names(ANNO_DIR)
    check_data_leak(splits)

    print()
    print("スライス処理を実行するには slice_image() を呼び出してください。")
    print("（処理時間がかかるため、必要なsplitのみ実行を推奨）")
