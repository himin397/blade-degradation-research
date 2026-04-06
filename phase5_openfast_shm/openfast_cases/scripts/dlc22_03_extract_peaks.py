"""
dlc22_03_extract_peaks.py
DLC 2.2: ピーク荷重抽出 + DLC 2.1 対比

ピッチ固着（Blade 1 固着 / Blade 2-3 正常ピッチ）による
非対称荷重の増大を DLC 2.1（全ブレード正常）と比較する。

出力:
  results/peak_loads_dlc22.csv
  results/dlc22_vs_dlc21.csv
  results/dlc22_peak_summary.md
"""

import numpy as np
import pandas as pd
from pathlib import Path

try:
    from openfast_io.FAST_output_reader import FASTOutputFile
except ImportError:
    raise ImportError("openfast_io が見つかりません。blade-phase3 環境で実行してください。")

SCRIPT_DIR  = Path(__file__).parent
BASE_DIR    = SCRIPT_DIR.parent
CASES_DLC22 = BASE_DIR / "cases_dlc22"
RESULTS     = BASE_DIR / "results"

DT      = 0.00625
T_FAULT = 300.0
T_PRE   = 60.0

V_LIST  = [8, 10, 12, 14, 16, 18]
TI_LIST = [0.14]
N_SEEDS = 6

print("=== DLC 2.2: ピーク荷重抽出（ピッチ固着） ===")

records = []
missing = 0

for V in V_LIST:
    for TI in TI_LIST:
        pre_peaks, post_peaks = [], []

        for s in range(1, N_SEEDS + 1):
            tag_full  = f"V{V:02d}_TI{int(TI*100):03d}_S{s:02d}"
            outb_path = CASES_DLC22 / tag_full / "case.outb"

            if not outb_path.exists():
                missing += 1
                continue

            try:
                df    = FASTOutputFile(str(outb_path)).toDataFrame()
                col   = next((c for c in df.columns if "RootMyb1" in c), None)
                t_col = next((c for c in df.columns if "Time" in c), None)
                if col is None or t_col is None:
                    continue

                t = df[t_col].values
                y = df[col].values

                mask_pre  = (t >= T_PRE)  & (t < T_FAULT)
                mask_post = (t >= T_FAULT)

                if mask_pre.sum() < 100 or mask_post.sum() < 100:
                    continue

                pre_peaks.append(np.max(np.abs(y[mask_pre])))
                post_peaks.append(np.max(np.abs(y[mask_post])))

            except Exception as e:
                print(f"  ERROR {tag_full}: {e}")

        if not pre_peaks:
            records.append({
                "V": V, "TI": TI,
                "peak_pre_mean": np.nan, "peak_pre_max": np.nan,
                "peak_post_mean": np.nan, "peak_post_max": np.nan,
                "peak_ratio": np.nan, "n_seeds": 0,
            })
            continue

        pre_arr  = np.array(pre_peaks)
        post_arr = np.array(post_peaks)
        ratio    = post_arr.max() / pre_arr.mean() if pre_arr.mean() > 0 else np.nan

        records.append({
            "V": V, "TI": TI,
            "peak_pre_mean":  float(pre_arr.mean()),
            "peak_pre_max":   float(pre_arr.max()),
            "peak_post_mean": float(post_arr.mean()),
            "peak_post_max":  float(post_arr.max()),
            "peak_ratio":     float(ratio),
            "n_seeds": len(pre_peaks),
        })
        print(f"  V={V:2d}m/s TI={TI:.2f}: "
              f"pre_max={pre_arr.max():.0f}  post_max={post_arr.max():.0f}  "
              f"ratio={ratio:.2f}  (n={len(pre_peaks)})")

# ── CSV 保存 ──────────────────────────────────────────────────────────────────
df22 = pd.DataFrame(records)
out_csv = RESULTS / "peak_loads_dlc22.csv"
df22.to_csv(out_csv, index=False)
print(f"\nCSV: {out_csv}")

# ── DLC 2.1 対比 ──────────────────────────────────────────────────────────────
dlc21_csv = RESULTS / "peak_loads_dlc21.csv"
if dlc21_csv.exists():
    df21 = pd.read_csv(dlc21_csv)
    comp_rows = []
    for _, row22 in df22.iterrows():
        v = int(row22["V"])
        row21 = df21[df21["V"] == v]
        p21 = float(row21["peak_post_max"].values[0]) if len(row21) > 0 else np.nan
        p22 = row22["peak_post_max"]
        amp  = (p22 / p21) if (not np.isnan(p21) and p21 > 0) else np.nan
        comp_rows.append({
            "V": v,
            "DLC21_post_peak_kNm": round(p21, 1) if not np.isnan(p21) else np.nan,
            "DLC22_post_peak_kNm": round(p22, 1) if not np.isnan(p22) else np.nan,
            "amplification_22vs21": round(float(amp), 3) if not np.isnan(amp) else np.nan,
        })
    df_comp = pd.DataFrame(comp_rows)
    comp_csv = RESULTS / "dlc22_vs_dlc21.csv"
    df_comp.to_csv(comp_csv, index=False)
    print(f"\n=== DLC 2.2 vs DLC 2.1 ピーク荷重対比（TI=0.14） ===")
    print(df_comp.to_string(index=False))

# ── サマリー ──────────────────────────────────────────────────────────────────
valid = df22.dropna(subset=["peak_post_max"])
if len(valid) > 0:
    max_post = valid["peak_post_max"].max()
    max_V    = int(valid.loc[valid["peak_post_max"].idxmax(), "V"])
    max_ratio = valid["peak_ratio"].max()

    summary = f"""# DLC 2.2: ピッチ固着 → 非対称緊急停止 ピーク荷重解析

## 解析条件
- フォルト: t={T_FAULT:.0f}s にグリッド喪失
  - Blade 1: ピッチ固着（フォルト時ピッチ角を維持）
  - Blade 2/3: 正常緊急ピッチ（8 deg/s → 90°）
  - 発電機遮断・HSS ブレーキ展開（DLC 2.1 と同条件）
- 風況: NTM, TI=0.14, V=8〜18 m/s（DLC 2.1 と同一 BTS）
- ケース数: {len(valid)} 条件 × 6 seeds

## 結果

| V (m/s) | フォルト前 max (kN·m) | フォルト後 max (kN·m) | 比率 |
|:---:|---:|---:|:---:|
"""
    for _, row in valid.iterrows():
        summary += (f"| {int(row['V'])} | {row['peak_pre_max']:.0f} "
                    f"| {row['peak_post_max']:.0f} | {row['peak_ratio']:.2f}x |\n")

    if dlc21_csv.exists():
        summary += "\n## DLC 2.2 vs DLC 2.1 フォルト後ピーク対比\n\n"
        summary += "| V (m/s) | DLC 2.1 (kN·m) | DLC 2.2 (kN·m) | 増幅率 |\n"
        summary += "|:---:|---:|---:|:---:|\n"
        for _, row in df_comp.iterrows():
            summary += (f"| {int(row['V'])} | {row['DLC21_post_peak_kNm']:.0f} "
                        f"| {row['DLC22_post_peak_kNm']:.0f} "
                        f"| {row['amplification_22vs21']:.2f}x |\n")

    summary += f"""
## 主要発見
- 最大ピーク荷重: {max_post:.0f} kN·m（V={max_V} m/s）
- 最大比率（フォルト後/フォルト前）: {max_ratio:.2f}x
- DLC 2.1 対比: ピッチ固着による荷重増大を確認（上表参照）

## 注意事項
- 翼型プロキシ使用のため絶対値は参考値
- IEC 61400-1 終局荷重ケース（安全係数 γ_f × γ_m を別途適用）
- Blade 1 の固着角は 0°（定格以下）を想定。定格以上では実際の固着角は異なる
"""
    out_md = RESULTS / "dlc22_peak_summary.md"
    out_md.write_text(summary, encoding="utf-8")
    print(f"\nサマリー: {out_md}")

print(f"\n欠落ケース: {missing}")
print("=== 完了 ===")
