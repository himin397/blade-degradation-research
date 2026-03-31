"""
Phase 1 W07: バウンディングボックス × 部位マッピングスクリプト

最終目標との接続: 画像由来の損傷状態定量化（部品#1）
前提: evaluate.py で学習済みモデルの推論結果が出力済みであること

部位定義: docs/blade_region_definition.md 参照

アプローチ: B（バウンディングボックスのx座標から前縁/後縁を推定）
"""

from pathlib import Path
from dataclasses import dataclass
import json


# ---- クラス定義 ----

CLASS_NAMES = {
    0: "VG;MT",
    1: "LE;ER",
    2: "LR;DA",
    3: "LE;CR",
    4: "SF;PO",
}

# クラス重み（docs/blade_region_definition.md 参照）
CLASS_WEIGHTS = {
    "LE;CR": 3.0,   # クラックは最重要
    "LE;ER": 2.0,   # 浸食
    "VG;MT": 1.5,
    "LR;DA": 1.5,
    "SF;PO": 1.0,
}

# 部位重み（docs/blade_region_definition.md 参照）
REGION_WEIGHTS = {
    "T-LE":   3.0,  # 翼端前縁：最高リスク
    "M-LE":   2.0,  # 中間前縁
    "R-LE":   1.5,  # 翼根前縁
    "T-Body": 1.5,  # 翼端胴体
    "M-Body": 1.0,  # 中間胴体
    "R-Body": 1.0,  # 翼根胴体
}


@dataclass
class Detection:
    """1つの検出結果を表すデータクラス。"""
    class_id: int
    class_name: str
    confidence: float
    cx: float   # 正規化済み中心x（0〜1）
    cy: float   # 正規化済み中心y（0〜1）
    w: float    # 正規化済み幅
    h: float    # 正規化済み高さ
    region: str = ""  # マッピング後に設定


def assign_chord_region(cx: float) -> str:
    """
    バウンディングボックスのx座標からコード方向の部位を推定。

    前提: ドローンがブレードの前縁側から撮影している場合、
    画像の左側（cx < 0.25）が前縁（LE）に対応する。
    ※この前提はDTUデータの撮影方向を確認後に調整が必要。

    Args:
        cx: 正規化済み中心x座標（0〜1）
    Returns:
        "LE" or "Body" or "TE"
    """
    if cx < 0.25:
        return "LE"
    elif cx > 0.75:
        return "TE"
    else:
        return "Body"


def assign_span_region(image_filename: str, total_images_in_sequence: int = None) -> str:
    """
    ファイル名・パッチ番号からスパン方向の部位を推定（アプローチA）。

    パッチ名の行インデックスが大きいほど画像の下部（翼端側）と仮定。
    ※DJI_XXXX_row_col.JPG の row が大きい → ブレード先端側の可能性。
    ※この仮定はDTU撮影方向の確認後に調整が必要。

    Args:
        image_filename: パッチファイル名（例: DJI_0058_1_3.JPG）
    Returns:
        "Root" or "Mid" or "Tip"
    """
    stem = Path(image_filename).stem
    parts = stem.split("_")
    if len(parts) >= 3:
        try:
            row = int(parts[2])
            if row == 0:
                return "Root"
            elif row == 1:
                return "Mid"
            else:
                return "Tip"
        except ValueError:
            pass
    return "Mid"  # 不明な場合はMidとする


def assign_region(detection: Detection, image_filename: str) -> str:
    """
    1つの検出結果に部位を割り当てる。

    Returns:
        部位ID（例: "T-LE", "M-Body" など）
    """
    chord = assign_chord_region(detection.cx)
    span = assign_span_region(image_filename)

    # TE（後縁）は今回の重み設定に含まれていないためBodyとして扱う
    if chord == "TE":
        chord = "Body"

    region = f"{span[0]}-{chord}"  # 例: "T-LE", "M-Body"
    return region


def calc_risk_score(detections: list[Detection]) -> dict:
    """
    検出結果のリストから部位別リスクスコアを算出する。

    スコア = Σ（信頼度 × 面積比率 × クラス重み × 部位重み）

    Returns:
        部位IDをキー、スコアを値とするdict
    """
    scores = {region: 0.0 for region in REGION_WEIGHTS}

    for det in detections:
        region = det.region
        if region not in REGION_WEIGHTS:
            continue

        area_ratio = det.w * det.h  # 正規化済み面積
        class_weight = CLASS_WEIGHTS.get(det.class_name, 1.0)
        region_weight = REGION_WEIGHTS[region]

        score = det.confidence * area_ratio * class_weight * region_weight
        scores[region] += score

    return scores


def format_score_report(scores: dict, image_name: str = "") -> str:
    """スコアを人間が読みやすい形式でフォーマットする。"""
    lines = [f"=== 部位別リスクスコア: {image_name} ==="]
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for region, score in sorted_scores:
        bar = "█" * int(score * 100)
        lines.append(f"  {region:8s}: {score:.4f}  {bar}")
    return "\n".join(lines)


if __name__ == "__main__":
    # 動作確認用のサンプルデータ
    sample_detections = [
        Detection(1, "LE;ER", 0.85, 0.10, 0.30, 0.05, 0.08),  # 前縁付近
        Detection(3, "LE;CR", 0.72, 0.15, 0.80, 0.04, 0.06),  # 前縁・下部
        Detection(0, "VG;MT", 0.91, 0.50, 0.50, 0.06, 0.04),  # 中央
    ]

    sample_filename = "DJI_0058_2_0.JPG"  # row=2 → Tip

    for det in sample_detections:
        det.region = assign_region(det, sample_filename)
        print(f"{det.class_name} → {det.region}")

    scores = calc_risk_score(sample_detections)
    print()
    print(format_score_report(scores, sample_filename))
