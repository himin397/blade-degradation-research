"""
Phase 1 W09: ピラミッド拡張スクリプト

最終目標との接続: 画像由来の損傷状態定量化（部品#1）

背景:
  YOLOv8ベースラインでは、損傷の「見かけの大きさ」が1スケールのみ。
  ピラミッド拡張により同じ損傷を3スケールで学習させ、スケール不変性を向上させる。
  先行研究（Gohar et al. 2023）では+35%の改善報告あり（仮説止まり・本研究で検証する）。

処理概要:
  1024×1024pxのtrain用パッチ + YOLOアノテーションを入力とし、
  0.67× スケール版・0.33× スケール版を追加生成してtrainセットに加える。

スケール変換の詳細:
  スケール s（例: 0.67）のとき、
  - 元画像を s×1024 × s×1024 にリサイズ
  - 1024×1024 の黒キャンバス左上に配置
  - アノテーション座標（正規化済み）に s を乗算する

  理由: 正規化座標は「画像全体に対する比率」なので、
  内容がキャンバスの s 倍の領域に収まっていれば、
  各座標値も s 倍されなければならない。

使い方:
  python phase1_image_risk_score/src/pyramid_augment.py

  --dry_run オプション: 実際のファイルを生成せず、変換後の座標のみ確認できる

出力先:
  元のtrain画像・アノテーションはそのまま保持。
  追加生成ファイルは同じフォルダに _p67 / _p33 サフィックスで保存。

注意:
  - valとtestには適用しない（評価の公平性のため）
  - dry_runで座標変換が正しいことを確認してから本番実行を推奨
"""

from pathlib import Path
from PIL import Image
import argparse
import shutil


REPO_ROOT = Path(__file__).parent.parent.parent
PROCESSED = REPO_ROOT / "data" / "processed" / "yolo_dataset"

TRAIN_IMG_DIR = PROCESSED / "images" / "train"
TRAIN_LBL_DIR = PROCESSED / "labels" / "train"

CANVAS_SIZE = 1024  # px

# 追加するスケール一覧（1.0は元画像が既に存在するため含めない）
PYRAMID_SCALES = {
    "p67": 0.67,
    "p33": 0.33,
}


def scale_image(src: Path, dst: Path, scale: float, canvas: int = CANVAS_SIZE):
    """
    画像を scale 倍にリサイズして canvas×canvas の黒背景に貼り付ける。

    Args:
        src:    元画像パス（1024×1024px を前提）
        dst:    出力先パス
        scale:  縮小率（0.0 < scale <= 1.0）
        canvas: キャンバスサイズ（px）
    """
    img = Image.open(src).convert("RGB")
    new_size = int(canvas * scale)
    resized = img.resize((new_size, new_size), Image.LANCZOS)

    background = Image.new("RGB", (canvas, canvas), (0, 0, 0))
    background.paste(resized, (0, 0))
    background.save(dst, "JPEG", quality=95)


def scale_annotations(src_txt: Path, dst_txt: Path, scale: float):
    """
    YOLOアノテーション（正規化済みcx,cy,w,h）をスケール変換する。

    正規化座標はキャンバス全体（1024px）に対する比率なので、
    内容が scale 倍の領域にある場合、座標値も scale 倍する。

    Args:
        src_txt: 元アノテーションファイル（YOLO形式）
        dst_txt: 出力先ファイル
        scale:   スケール（0.0 < scale <= 1.0）
    """
    lines_out = []
    if src_txt.exists():
        for line in src_txt.read_text().strip().splitlines():
            if not line:
                continue
            parts = line.split()
            if len(parts) < 5:
                continue
            class_id = parts[0]
            cx, cy, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])

            cx_new = cx * scale
            cy_new = cy * scale
            w_new  = w  * scale
            h_new  = h  * scale

            # クリッピング（1.0超えは念のため防止）
            cx_new = min(cx_new, 1.0)
            cy_new = min(cy_new, 1.0)
            w_new  = min(w_new, 1.0)
            h_new  = min(h_new, 1.0)

            lines_out.append(f"{class_id} {cx_new:.6f} {cy_new:.6f} {w_new:.6f} {h_new:.6f}")

    dst_txt.write_text("\n".join(lines_out) + "\n" if lines_out else "")


def run_pyramid_augmentation(dry_run: bool = False):
    """
    trainセットの全画像に対してピラミッド拡張を実行する。

    Args:
        dry_run: True の場合、ファイルを生成せず変換内容のみ表示する
    """
    if not TRAIN_IMG_DIR.exists():
        print(f"エラー: {TRAIN_IMG_DIR} が存在しません。")
        print("slice_images.py と coco_to_yolo.py を先に実行してください。")
        return

    img_files = sorted(TRAIN_IMG_DIR.glob("*.JPG")) + sorted(TRAIN_IMG_DIR.glob("*.jpg"))
    print(f"元のtrain画像数: {len(img_files)}")

    generated = 0
    skipped = 0

    for img_path in img_files:
        # _p67 / _p33 サフィックスが既についているものはスキップ（元ファイルのみ対象）
        if any(img_path.stem.endswith(f"_{suffix}") for suffix in PYRAMID_SCALES):
            skipped += 1
            continue

        lbl_path = TRAIN_LBL_DIR / (img_path.stem + ".txt")

        for suffix, scale in PYRAMID_SCALES.items():
            dst_img = TRAIN_IMG_DIR / f"{img_path.stem}_{suffix}.JPG"
            dst_lbl = TRAIN_LBL_DIR / f"{img_path.stem}_{suffix}.txt"

            if dry_run:
                # 座標変換のサンプル表示
                if lbl_path.exists():
                    first_line = lbl_path.read_text().strip().splitlines()
                    if first_line:
                        parts = first_line[0].split()
                        cx, cy = float(parts[1]), float(parts[2])
                        print(f"[DRY-RUN] {img_path.name} scale={scale:.2f}: "
                              f"cx {cx:.3f}→{cx*scale:.3f}, cy {cy:.3f}→{cy*scale:.3f}")
                        break  # 1ファイルのみ表示
            else:
                if dst_img.exists() and dst_lbl.exists():
                    skipped += 1
                    continue
                scale_image(img_path, dst_img, scale)
                scale_annotations(lbl_path, dst_lbl, scale)
                generated += 1

    if dry_run:
        print("\n[DRY-RUN] 完了。--dry_run を外して本番実行してください。")
    else:
        print(f"\n完了: 新規生成={generated}ファイルペア、スキップ={skipped}")
        new_total = len(list(TRAIN_IMG_DIR.glob("*.JPG")) + list(TRAIN_IMG_DIR.glob("*.jpg")))
        print(f"train画像総数（拡張後）: {new_total}")


def verify_scale_transform(scale: float):
    """
    スケール変換の数値が正しいことを確認する単体テスト。

    正規化座標 (cx=0.5, cy=0.5, w=0.1, h=0.1) に対して
    scale=0.67 を適用すると (cx=0.335, cy=0.335, w=0.067, h=0.067) になるべき。
    """
    cx, cy, w, h = 0.5, 0.5, 0.1, 0.1
    cx_new = cx * scale
    cy_new = cy * scale
    w_new  = w  * scale
    h_new  = h  * scale
    print(f"[検証] scale={scale}")
    print(f"  cx: {cx} → {cx_new:.4f}  (期待値: {cx*scale:.4f})")
    print(f"  cy: {cy} → {cy_new:.4f}")
    print(f"  w:  {w}  → {w_new:.4f}")
    print(f"  h:  {h}  → {h_new:.4f}")
    assert abs(cx_new - cx * scale) < 1e-9, "変換エラー"
    print("  ✓ OK")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ピラミッド拡張: 3スケール版をtrainセットに追加")
    parser.add_argument("--dry_run", action="store_true",
                        help="ファイルを生成せず、座標変換の確認のみ実行")
    parser.add_argument("--verify", action="store_true",
                        help="スケール変換の数値検証のみ実行")
    args = parser.parse_args()

    if args.verify:
        for scale in PYRAMID_SCALES.values():
            verify_scale_transform(scale)
    else:
        run_pyramid_augmentation(dry_run=args.dry_run)
