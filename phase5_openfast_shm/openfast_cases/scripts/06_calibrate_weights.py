"""
06_calibrate_weights.py
Phase 5b: OpenFAST DELマトリクス vs 簡易モデルの比較・重み較正
結果を phase4_weights_calibrated.json として保存し、
Phase 4 fusion_pipeline.py の重みを更新する
"""

import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import LinearRegression

SCRIPT_DIR = Path(__file__).parent
RESULTS    = SCRIPT_DIR.parent / "results"
PHASE4_DIR = Path(__file__).parents[4] / "phase4_fusion"
PHASE5_CSV = Path(__file__).parents[3] / "phase5_del_proxy.csv"

# ------------------------------------------------------------------ #
# 1. OpenFAST DELマトリクス読み込み
# ------------------------------------------------------------------ #
del_df = pd.read_csv(RESULTS / "del_matrix.csv")
del_df = del_df.dropna(subset=["DEL_kNm"])
print(f"Loaded DEL matrix: {len(del_df)} valid cases")

# ------------------------------------------------------------------ #
# 2. 簡易モデル（Phase 5）の再計算
# ------------------------------------------------------------------ #
V_RATED = 11.4   # m/s (NREL 5MW rated wind speed)
N_EXP   = 3      # 風速指数
GAMMA   = 5      # TI増幅係数
M_SN    = 10     # SN曲線指数

def del_proxy(V, TI):
    CT = 0.80 if V <= V_RATED else 0.80 * (V_RATED / V) ** 2
    I  = (V / V_RATED) ** N_EXP * CT * (1 + GAMMA * TI)
    return I

del_df["DEL_proxy"] = del_df.apply(lambda r: del_proxy(r["V"], r["TI"]), axis=1)

# ------------------------------------------------------------------ #
# 3. 正規化して比較
# ------------------------------------------------------------------ #
def normalize(s):
    mn, mx = s.min(), s.max()
    return (s - mn) / (mx - mn) if mx > mn else s * 0

del_df["DEL_norm"]       = normalize(del_df["DEL_kNm"])
del_df["DEL_proxy_norm"] = normalize(del_df["DEL_proxy"])

r_pearson, p_pearson = pearsonr(del_df["DEL_norm"], del_df["DEL_proxy_norm"])
r_spearman, p_spearman = spearmanr(del_df["DEL_norm"], del_df["DEL_proxy_norm"])
print(f"\n簡易モデル vs OpenFAST DEL:")
print(f"  Pearson  r={r_pearson:.3f}  p={p_pearson:.4f}")
print(f"  Spearman r={r_spearman:.3f}  p={p_spearman:.4f}")

# ------------------------------------------------------------------ #
# 4. 偏回帰で V重み (w_V) と TI重み (w_TI) を較正
# ------------------------------------------------------------------ #
del_df["V_norm"]  = normalize(del_df["V"])
del_df["TI_norm"] = normalize(del_df["TI"])

X = del_df[["V_norm", "TI_norm"]].values
y = del_df["DEL_norm"].values

lr = LinearRegression(positive=True).fit(X, y)
coef_sum = lr.coef_.sum()
w_V  = float(lr.coef_[0] / coef_sum)
w_TI = float(lr.coef_[1] / coef_sum)

r2 = lr.score(X, y)
print(f"\n偏回帰結果 (R²={r2:.3f}):")
print(f"  w_V (hrs_above_rated weight) = {w_V:.3f}")
print(f"  w_TI (mean_ti weight)        = {w_TI:.3f}")

# ------------------------------------------------------------------ #
# 5. 可視化
# ------------------------------------------------------------------ #
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# 5-1: DELヒートマップ (OpenFAST)
pivot = del_df.pivot(index="V", columns="TI", values="DEL_kNm")
im = axes[0].imshow(pivot.values, aspect="auto", cmap="YlOrRd",
                    origin="lower")
axes[0].set_xticks(range(len(pivot.columns)))
axes[0].set_xticklabels([f"{ti:.2f}" for ti in pivot.columns])
axes[0].set_yticks(range(len(pivot.index)))
axes[0].set_yticklabels(pivot.index.astype(int))
axes[0].set_xlabel("TI")
axes[0].set_ylabel("V (m/s)")
axes[0].set_title("OpenFAST DEL (kN-m)")
plt.colorbar(im, ax=axes[0])

# 5-2: 簡易モデル vs OpenFAST 散布図
axes[1].scatter(del_df["DEL_proxy_norm"], del_df["DEL_norm"], alpha=0.7, color="steelblue")
lim = [0, 1.05]
axes[1].plot(lim, lim, "k--", lw=1, label="1:1")
axes[1].set_xlabel("簡易モデル DEL (正規化)")
axes[1].set_ylabel("OpenFAST DEL (正規化)")
axes[1].set_title(f"簡易モデル vs OpenFAST\nPearson r={r_pearson:.3f}")
axes[1].legend()

# 5-3: 重み比較棒グラフ
labels = ["hrs_above_rated\n(V重み)", "mean_ti\n(TI重み)"]
phase5_weights = [0.50, 0.50]
calibrated     = [w_V, w_TI]
x = np.arange(len(labels))
width = 0.35
axes[2].bar(x - width/2, phase5_weights, width, label="Phase 5等重み", color="gray", alpha=0.7)
axes[2].bar(x + width/2, calibrated,     width, label="OpenFAST較正", color="steelblue")
axes[2].set_xticks(x)
axes[2].set_xticklabels(labels)
axes[2].set_ylabel("重み")
axes[2].set_title("Phase 4重み: 等重み vs OpenFAST較正")
axes[2].legend()
axes[2].set_ylim(0, 1.1)

plt.tight_layout()
fig.savefig(RESULTS / "model_comparison.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"\nSaved: {RESULTS / 'model_comparison.png'}")

# ------------------------------------------------------------------ #
# 6. 較正済み重みを保存
# ------------------------------------------------------------------ #
weights = {
    "w_V":  w_V,
    "w_TI": w_TI,
    "source":   "OpenFAST DLC1.2 NREL 5MW",
    "method":   "LinearRegression(positive=True) on DEL_norm ~ V_norm + TI_norm",
    "R2":       round(r2, 4),
    "Pearson_r_proxy_vs_openfast": round(r_pearson, 4),
    "note": "このサイト(低TI環境)ではV重みが支配的。IEC-A/Bサイトでは再較正が必要。"
}
out_json = RESULTS / "phase4_weights_calibrated.json"
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(weights, f, ensure_ascii=False, indent=2)
print(f"Saved: {out_json}")

# ------------------------------------------------------------------ #
# 7. Phase 4 fusion_pipeline.py の重みを更新
# ------------------------------------------------------------------ #
fusion_py = PHASE4_DIR / "fusion_pipeline.py"
if fusion_py.exists():
    code = fusion_py.read_text()
    # 等重みの行を較正済み重みに置換
    old_line = 'tmp["fatigue_risk_score"] = (\n        tmp["hrs_above_rated_norm"] * 0.5 +\n        tmp["mean_ti_norm"] * 0.5\n    )'
    new_line = (
        f'# 重み: OpenFAST DLC1.2較正済み (Phase 5b)\n'
        f'    tmp["fatigue_risk_score"] = (\n'
        f'        tmp["hrs_above_rated_norm"] * {w_V:.4f} +\n'
        f'        tmp["mean_ti_norm"] * {w_TI:.4f}\n'
        f'    )'
    )
    if old_line in code:
        updated = code.replace(old_line, new_line)
        fusion_py.write_text(updated)
        print(f"\nUpdated Phase 4 weights in: {fusion_py}")
    else:
        print(f"\nINFO: Could not auto-patch fusion_pipeline.py (pattern not found).")
        print(f"  → 手動で w_V={w_V:.4f}, w_TI={w_TI:.4f} に更新してください。")
else:
    print(f"\nINFO: {fusion_py} not found. JSON weights saved for manual update.")

print("\n=== Phase 5b 完了 ===")
print(f"DEL matrix : {RESULTS / 'del_matrix.csv'}")
print(f"Comparison : {RESULTS / 'model_comparison.png'}")
print(f"Weights    : {out_json}")
