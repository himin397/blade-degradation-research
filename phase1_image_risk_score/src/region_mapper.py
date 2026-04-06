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

# 部位重み（スパン方向のみ・Phase 2改訂版）
# chord方向（LE/Body/TE）は撮影角度の非標準化により信頼性が低いため削除
# 確認済み根拠：LE;ERアノテーション229件のcx分布が0.004〜0.992に均一分布（2026-04-02）
REGION_WEIGHTS = {
    "Tip":  3.0,  # 翼端：最高リスク（himinさんの現場知識・文献と整合）
    "Mid":  2.0,  # 中間
    "Root": 1.0,  # 翼根
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

    【重要：Phase 1 検証済み制約（2026-04-02）】
    DTUデータセットではブレードが各パッチ内で斜め方向（左上→右下）に走るため、
    前縁（LE）の位置はパッチ内で一定ではなくrowによって変化する。
    アノテーション可視化（DJI_0615_0_2.JPG等）により、LE;ER損傷は
    cx=0.26, 0.43, 0.55, 0.75, 0.88 等、パッチ全域に分布することが確認された。

    → 固定cx閾値によるLE/Body/TE分類は信頼性が低い（Phase 2以降で幾何補正が必要）。
    　 現状は暫定実装として維持するが、分類結果の解釈に注意が必要。

    Args:
        cx: 正規化済み中心x座標（0〜1）
    Returns:
        "LE" or "Body" or "TE"（暫定・信頼性低）
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

    DTU撮影方向の確認結果（2026-04-02）:
    - ブレードは画像内で左上（先端）→右下（根元）方向に対角線状に走る
    - row=0（画像上部）= Tip（先端）：空のみ見える、地面なし
    - row=2（画像下部）= Root（根元）：地面・草原が見える、黒パディングあり
    - 確認方法: DJI_0615_0_2.JPG vs DJI_0615_2_2.JPG の目視比較、
               LE;ERアノテーションがrow=0に集中していることとhiminさんの
               現場知識（T-LE侵食が最も激しい）との整合性確認

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
                return "Tip"
            elif row == 1:
                return "Mid"
            else:
                return "Root"
        except ValueError:
            pass
    return "Mid"  # 不明な場合はMidとする


def assign_region(detection: Detection, image_filename: str) -> str:
    """
    1つの検出結果に部位を割り当てる。

    Phase 2改訂（2026-04-02）：
    chord方向（LE/Body/TE）の信頼性が低いことが確認されたため、
    スパン方向（Tip/Mid/Root）のみを返す。

    Returns:
        部位ID（"Tip", "Mid", "Root"）
    """
    return assign_span_region(image_filename)


def calc_risk_score(detections: list[Detection]) -> dict:
    """
    検出結果のリストからスパン部位別リスクスコアを算出する。

    スコア = Σ（信頼度 × 面積比率 × クラス重み × 部位重み）

    Returns:
        {"Tip": float, "Mid": float, "Root": float}
    """
    scores = {region: 0.0 for region in REGION_WEIGHTS}

    for det in detections:
        region = det.region
        if region not in REGION_WEIGHTS:
            continue

        area_ratio = det.w * det.h
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
