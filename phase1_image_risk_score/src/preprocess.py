"""
Phase 1: 前処理スクリプト
DTU原データをYOLOv8学習用に整備する

データ: DTU / Mendeley (DOI: 10.17632/hd96prn3nc.2) ← 一次ソース
"""

from pathlib import Path
import shutil
import random
import json
from PIL import Image


# パス定義（リポジトリルートからの相対パス）
REPO_ROOT = Path(__file__).parent.parent.parent
DATA_RAW = REPO_ROOT / "data" / "raw"
DATA_PROCESSED = REPO_ROOT / "data" / "processed"


def check_data_structure(data_dir: Path) -> dict:
    """
    データフォルダの構成を確認する。
    ダウンロード後に最初に実行する。
    """
    image_files = list(data_dir.rglob("*.jpg")) + list(data_dir.rglob("*.png"))

    summary = {
        "total_images": len(image_files),
        "by_year": {},
        "formats": {},
    }

    for f in image_files:
        # 年別カウント
        for year in ["2017", "2018"]:
            if year in str(f):
                summary["by_year"][year] = summary["by_year"].get(year, 0) + 1

        # 形式別カウント
        ext = f.suffix.lower()
        summary["formats"][ext] = summary["formats"].get(ext, 0) + 1

    return summary


def split_dataset(
    image_files: list,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    seed: int = 42,
) -> dict:
    """
    データセットをtrain/val/testに分割する。

    注意: 同一年・同一ブレードの画像が分割をまたがないよう
    year単位でstratifiedに分割することを推奨。
    """
    random.seed(seed)
    files = list(image_files)
    random.shuffle(files)

    n = len(files)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)

    return {
        "train": files[:n_train],
        "val": files[n_train:n_train + n_val],
        "test": files[n_train + n_val:],
    }


def create_yolo_dataset_yaml(output_dir: Path, class_names: list) -> Path:
    """
    YOLOv8学習用のdataset.yamlを作成する。
    """
    yaml_content = f"""# YOLOv8 Dataset Configuration
# データ: DTU Drone Inspection Images (DOI: 10.17632/hd96prn3nc.2)

path: {output_dir.resolve()}
train: images/train
val: images/val
test: images/test

nc: {len(class_names)}
names: {class_names}
"""
    yaml_path = output_dir / "dataset.yaml"
    yaml_path.write_text(yaml_content)
    return yaml_path


if __name__ == "__main__":
    print("DTUデータ構造確認:")
    summary = check_data_structure(DATA_RAW)
    print(f"  総画像数: {summary['total_images']}")
    print(f"  年別: {summary['by_year']}")
    print(f"  形式: {summary['formats']}")
