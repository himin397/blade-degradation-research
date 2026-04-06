"""
mm82_post_pipeline.py
Phase I 完了後処理: del_matrix_mm82.csv の結果で統合レポート §16 を更新する
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
import datetime

REPO = Path("/Users/tsunekousei/Desktop/blade-degradation-research")
DEL_CSV  = REPO / "phase5_openfast_shm/openfast_cases/results/del_matrix_mm82.csv"
REPORT   = REPO / "docs/integrated_research_report.md"
ROADMAP  = REPO / "docs/research_roadmap.md"

# ── DEL matrix 読み込み ────────────────────────────────────────────────────────
print("=== Phase I 後処理: レポート更新 ===")
df = pd.read_csv(DEL_CSV)
valid = df.dropna(subset=["DEL_mean"])

del_min  = valid["DEL_mean"].min()
del_max  = valid["DEL_mean"].max()
cv_mean  = valid["DEL_cv"].mean() * 100
n_valid  = len(valid)
n_seeds  = int(valid["n_seeds"].mean())

# pivot table (V x TI)
pivot = df.pivot(index="V", columns="TI", values="DEL_mean").round(1)
pivot_str = pivot.to_string()

print(f"有効ケース: {n_valid}/40")
print(f"DEL 範囲: {del_min:.1f} 〜 {del_max:.1f} kN·m")
print(f"CV 平均: {cv_mean:.1f}%")
print(f"\nDEL マトリクス:\n{pivot_str}")

# ── 統合レポート §16 更新 ─────────────────────────────────────────────────────
report_text = REPORT.read_text(encoding="utf-8")

today = datetime.date.today().strftime("%Y-%m-%d")

# "実行中" プレースホルダーを実績値に差し替え
replacements = [
    (
        r"(?m)^(\*\*実行計画\*\*.*?240 ケース.*?)\n",
        f"**実行結果** (完了: {today}): 240ケース TurbSim + OpenFAST 完了\n"
    ),
]

# §16 の「実行中」ラベルを「完了」に変更
report_text = re.sub(
    r"Phase I（MM82 OpenFAST）.*?実行中",
    f"Phase I（MM82 OpenFAST）: 完了（{today}）",
    report_text
)

# DEL range / CV の実績を追記するブロックを探して置換
del_summary_block = f"""
#### DEL マトリクス結果（MM82 プロキシ, kN-m）

```
{pivot_str}
```

- **DEL 範囲**: {del_min:.0f} 〜 {del_max:.0f} kN·m（V=4〜18 m/s, TI=0.08〜0.20）
- **CV 平均**: {cv_mean:.1f}%（シード間再現性）
- **有効ケース**: {n_valid} / 40 グリッド点（各 {n_seeds} シード平均）
"""

# プレースホルダー行を実績ブロックに差し替え
report_text = re.sub(
    r"\*\*DEL 範囲\*\*: 実行中.*?\n",
    f"**DEL 範囲**: {del_min:.0f} 〜 {del_max:.0f} kN·m\n",
    report_text
)
report_text = re.sub(
    r"\*\*CV 平均\*\*: 実行中.*?\n",
    f"**CV 平均**: {cv_mean:.1f}%\n",
    report_text
)
report_text = re.sub(
    r"\*\*有効ケース\*\*: 実行中.*?\n",
    f"**有効ケース**: {n_valid}/40 グリッド点（各 {n_seeds} シード平均）\n",
    report_text
)

# v1.7 → v1.8
report_text = report_text.replace(
    "# 統合研究レポート v1.7",
    "# 統合研究レポート v1.8"
)

REPORT.write_text(report_text, encoding="utf-8")
print(f"\n統合レポート更新: v1.8 → {REPORT}")

# ── research_roadmap.md 更新 ──────────────────────────────────────────────────
roadmap_text = ROADMAP.read_text(encoding="utf-8")

# Phase I 進行中 → 完了
roadmap_text = re.sub(
    r"Phase I（MM82 OpenFAST）.*?実行中（2026-04-03〜）.*?\n",
    f"- **Phase I（MM82 OpenFAST）**: 完了（{today}）― MM82スケーリング、240ケース完了、DEL {del_min:.0f}〜{del_max:.0f} kN-m、CV平均{cv_mean:.1f}%\n",
    roadmap_text
)

ROADMAP.write_text(roadmap_text, encoding="utf-8")
print(f"ロードマップ更新 → {ROADMAP}")

print("\n=== 後処理完了 ===")
