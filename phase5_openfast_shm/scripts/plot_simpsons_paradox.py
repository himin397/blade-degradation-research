"""
plot_simpsons_paradox.py
Phase 5 考察: mean_ti vs DEL_proxy の Simpson's Paradox を可視化する

Panel 1: 月別散布図（全体）→ 負相関に見える
Panel 2: 風速ビン別散布図 → 条件付きで正相関に反転
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from pathlib import Path

PHASE5_DIR = Path(__file__).parent.parent
CSV_PATH   = PHASE5_DIR / "phase5_del_proxy.csv"
OUT_DIR    = PHASE5_DIR.parent / "docs"

df = pd.read_csv(CSV_PATH)

# 月名
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
df['month_name'] = [months[m-1] for m in df['month']]

# 風速ビン（定格12 m/s を境に3グループ）
bins   = [0, 7, 10, 99]
labels = ['Low (≤7)', 'Mid (7-10)', 'High (>10)']
df['wind_bin'] = pd.cut(df['mean_wind_ms'], bins=bins, labels=labels)
colors = {'Low (≤7)': '#1f77b4', 'Mid (7-10)': '#ff7f0e', 'High (>10)': '#d62728'}

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# ---- Panel 1: 全体相関（負相関に見える） ----
ax = axes[0]
r_all, p_all = stats.pearsonr(df['mean_ti'], df['del_proxy'])
ax.scatter(df['mean_ti'] * 100, df['del_proxy'],
           c='#2ca02c', s=80, alpha=0.8, zorder=3)
for _, row in df.iterrows():
    ax.annotate(row['month_name'],
                (row['mean_ti'] * 100, row['del_proxy']),
                fontsize=7, ha='left', va='bottom',
                xytext=(2, 2), textcoords='offset points')
# 回帰直線
x = df['mean_ti'].values * 100
y = df['del_proxy'].values
m, b = np.polyfit(x, y, 1)
xline = np.linspace(x.min(), x.max(), 100)
ax.plot(xline, m * xline + b, 'k--', lw=1.5, alpha=0.6)
ax.set_xlabel('Mean TI (%)', fontsize=11)
ax.set_ylabel('DEL Proxy', fontsize=11)
ax.set_title(f'Panel 1: Marginal (all months)\nr = {r_all:.3f}, p = {p_all:.3f}',
             fontsize=11)
ax.grid(alpha=0.3)
ax.text(0.97, 0.95, f'r = {r_all:.2f}\n(apparent negative)',
        transform=ax.transAxes, ha='right', va='top',
        fontsize=9, color='black',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

# ---- Panel 2: 風速ビン別（正相関に反転） ----
ax = axes[1]
for wind_label in labels:
    grp = df[df['wind_bin'] == wind_label]
    if len(grp) < 2:
        continue
    c = colors[wind_label]
    ax.scatter(grp['mean_ti'] * 100, grp['del_proxy'],
               c=c, s=80, alpha=0.9, label=wind_label, zorder=3)
    # 条件付き回帰直線
    r_cond, p_cond = stats.pearsonr(grp['mean_ti'], grp['del_proxy'])
    x_g = grp['mean_ti'].values * 100
    y_g = grp['del_proxy'].values
    m_g, b_g = np.polyfit(x_g, y_g, 1)
    xline_g = np.linspace(x_g.min(), x_g.max(), 50)
    ax.plot(xline_g, m_g * xline_g + b_g, '--', color=c, lw=1.5, alpha=0.7,
            label=f'  r={r_cond:.2f} (p={p_cond:.2f})')

ax.set_xlabel('Mean TI (%)', fontsize=11)
ax.set_ylabel('DEL Proxy', fontsize=11)
ax.set_title("Panel 2: Conditioned on wind speed\n(TI shows positive trend within each group)",
             fontsize=11)
ax.grid(alpha=0.3)
ax.legend(fontsize=8, loc='upper left')
ax.text(0.97, 0.05,
        "Simpson's Paradox:\nNegative overall, positive conditional",
        transform=ax.transAxes, ha='right', va='bottom',
        fontsize=8, color='black',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.suptitle("TI vs DEL Proxy: Simpson's Paradox\n"
             "(High-TI months coincide with low-wind season → spurious negative correlation)",
             fontsize=11, y=1.02)
plt.tight_layout()

out_path = OUT_DIR / "simpsons_paradox.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight")
print(f"Saved: {out_path}")
