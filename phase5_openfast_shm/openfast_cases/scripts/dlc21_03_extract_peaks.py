"""
dlc21_03_extract_peaks.py
DLC 2.1: ピーク荷重抽出（終局荷重評価）

DLC 2.1 は DEL ではなく最大荷重を評価する（IEC 61400-1 終局荷重）。
フォルト前の定常状態とフォルト後の過渡ピークを比較する。

出力:
  results/peak_loads_dlc21.csv   ... ケース別ピーク荷重
  results/dlc21_vs_dlc12.csv     ... DLC 1.2 対比表
  results/dlc21_peak_summary.md  ... サマリー
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
CASES_DLC21 = BASE_DIR / "cases_dlc21"
RESULTS     = BASE_DIR / "results"
RESULTS.mkdir(exist_ok=True)

DT      = 0.00625   # s
T_FAULT = 300.0     # フォルト時刻 [s]
T_PRE   = 60.0      # フォルト前の定常区間開始（過渡除去）
T_POST  = T_FAULT   # フォルト後の区間開始

V_LIST   = [8, 10, 12, 14, 16, 18]
TI_LIST  = [0.14]
N_SEEDS  = 6

print("=== DLC 2.1: ピーク荷重抽出 ===")

records = []
missing = 0

for V in V_LIST:
    for TI in TI_LIST:
        pre_peaks, post_peaks = [], []

        for s in range(1, N_SEEDS + 1):
            tag_full  = f"V{V:02d}_TI{int(TI*100):03d}_S{s:02d}"
            outb_path = CASES_DLC21 / tag_full / "case.outb"

            if not outb_path.exists():
                missing += 1
                continue

            try:
                df  = FASTOutputFile(str(outb_path)).toDataFrame()
                col = next((c for c in df.columns if "RootMyb1" in c), None)
                t_col = next((c for c in df.columns if "Time" in c), None)
                if col is None or t_col is None:
                    continue

                t = df[t_col].values
                y = df[col].values

                # フォルト前: T_PRE ～ T_FAULT
                mask_pre  = (t >= T_PRE) & (t < T_FAULT)
                # フォルト後: T_FAULT ～ 終端
                mask_post = (t >= T_POST)

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
df_out = pd.DataFrame(records)
out_csv = RESULTS / "peak_loads_dlc21.csv"
df_out.to_csv(out_csv, index=False)
print(f"\nCSV 保存: {out_csv}")

# ── DLC 1.2 DEL との対比 ─────────────────────────────────────────────────────
del_csv = RESULTS / "del_matrix_mm82.csv"
if del_csv.exists():
    df_del = pd.read_csv(del_csv)
    # TI=0.14 のみ
    df_del14 = df_del[df_del["TI"] == 0.14].copy()

    comp_rows = []
    for _, row in df_out.iterrows():
        v = int(row["V"])
        del_row = df_del14[df_del14["V"] == v]
        del_mean = float(del_row["DEL_mean"].values[0]) if len(del_row) > 0 else np.nan
        comp_rows.append({
            "V": v,
            "DLC12_DEL_kNm": round(del_mean, 1),
            "DLC21_pre_peak_kNm":  round(row["peak_pre_max"], 1) if not np.isnan(row["peak_pre_max"]) else np.nan,
            "DLC21_post_peak_kNm": round(row["peak_post_max"], 1) if not np.isnan(row["peak_post_max"]) else np.nan,
            "peak_ratio_post_pre": round(row["peak_ratio"], 3) if not np.isnan(row["peak_ratio"]) else np.nan,
        })
    df_comp = pd.DataFrame(comp_rows)
    comp_csv = RESULTS / "dlc21_vs_dlc12.csv"
    df_comp.to_csv(comp_csv, index=False)
    print(f"対比CSV: {comp_csv}")
    print("\n=== DLC 2.1 vs DLC 1.2 (TI=0.14) ===")
    print(df_comp.to_string(index=False))

# ── サマリー ──────────────────────────────────────────────────────────────────
valid = df_out.dropna(subset=["peak_post_max"])
if len(valid) > 0:
    max_post = valid["peak_post_max"].max()
    max_V    = int(valid.loc[valid["peak_post_max"].idxmax(), "V"])
    max_ratio = valid["peak_ratio"].max()

    summary = f"""# DLC 2.1: グリッド喪失 → 緊急停止 ピーク荷重解析

## 解析条件
- フォルト: t={T_FAULT:.0f}s にグリッド喪失 → 緊急ピッチ（8 deg/s → 90°）+ 発電機遮断
- 風況: NTM（DLC 1.2 と同一 BTS 再利用）, TI=0.14, V=8〜18 m/s
- ケース数: {len(valid)} 条件 × 6 seeds

## 結果

| V (m/s) | フォルト前 max (kN·m) | フォルト後 max (kN·m) | 比率 |
|:---:|---:|---:|:---:|
"""
    for _, row in valid.iterrows():
        summary += (f"| {int(row['V'])} | {row['peak_pre_max']:.0f} "
                    f"| {row['peak_post_max']:.0f} | {row['peak_ratio']:.2f}x |\n")

    summary += f"""
## 主要発見
- 最大ピーク荷重: {max_post:.0f} kN·m（V={max_V} m/s）
- 最大比率（フォルト後/フォルト前）: {max_ratio:.2f}x
- フォルト後の過渡荷重は定常荷重の {max_ratio:.1f}倍に達する

## 注意事項
- DEL（疲労荷重）との直接比較は不可（評価軸が異なる）
- 翼型プロキシ使用のため絶対値は参考値
- DLC 2.1 は IEC 61400-1 §7.4 終局荷重ケース（安全係数 γ_f × γ_m を別途適用）
"""
    out_md = RESULTS / "dlc21_peak_summary.md"
    out_md.write_text(summary, encoding="utf-8")
    print(f"\nサマリー: {out_md}")

print(f"\n欠落ケース: {missing}")
print("=== 完了 ===")
