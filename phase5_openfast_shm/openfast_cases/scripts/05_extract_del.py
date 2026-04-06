"""
05_extract_del.py
Phase 5b: OpenFAST出力(.outb)からRainflow counting → DEL(RootMyb1)を算出し
del_matrix.csv として保存する

DEL定義:
  DEL = ( Σ(n_i * ΔS_i^m) / N_eq )^(1/m)
  m = 10 (GFRPブレード, IEC 61400-1 Annex H)
  Teq = 600s → N_eq = Teq / T_step = 600 / 0.00625 = 96000
"""

import numpy as np
import pandas as pd
from pathlib import Path

try:
    from openfast_io.FAST_output_reader import FASTOutputFile
except ImportError:
    raise ImportError("openfast_io が見つかりません。pip install openfast-io を実行してください。")

SCRIPT_DIR = Path(__file__).parent
CASES_DIR  = SCRIPT_DIR.parent / "cases"
RESULTS    = SCRIPT_DIR.parent / "results"
RESULTS.mkdir(exist_ok=True)

DT    = 0.00625   # s (OpenFASTのDT)
M     = 10        # SN曲線指数（GFRP）
TEQ   = 600.0     # 等価時間 [s]
SKIP_S = 60.0     # 過渡除去：最初60秒をスキップ


def rainflow_del(signal, m=10, dt=0.00625, Teq=600.0):
    """
    簡易Rainflow counting → DEL算出
    レンジペアカウント法（ピーク・バレー抽出 → サイクル数え）
    """
    # ピーク・バレー抽出
    sig = np.asarray(signal, dtype=float)
    diff = np.diff(sig)
    # 符号変化点 = ピーク or バレー
    sign_change = np.where(np.diff(np.sign(diff)) != 0)[0] + 1
    extrema = np.concatenate([[0], sign_change, [len(sig) - 1]])
    peaks = sig[extrema]

    # レンジ = |peak(i+1) - peak(i)|（簡易ハーフサイクルカウント）
    ranges = np.abs(np.diff(peaks))
    if len(ranges) == 0:
        return 0.0

    # ハーフサイクル → カウント0.5
    n_half = np.ones(len(ranges)) * 0.5

    T_actual = len(sig) * dt
    N_eq = Teq / T_actual  # ≈ 1.0 for 600s sim

    damage = np.sum(n_half * (ranges ** m))
    DEL = (damage / N_eq) ** (1.0 / m)
    return float(DEL)


V_LIST  = [4, 6, 8, 10, 12, 14, 16, 18]
TI_LIST = [0.08, 0.12, 0.14, 0.16, 0.20]

records = []
skip_steps = int(SKIP_S / DT)

for V in V_LIST:
    for TI in TI_LIST:
        case_tag = f"V{V:02d}_TI{int(TI * 100):03d}"
        outb_path = CASES_DIR / case_tag / "case.outb"

        if not outb_path.exists():
            print(f"  SKIP (no .outb): {case_tag}")
            records.append({"V": V, "TI": TI, "DEL_kNm": np.nan, "case_tag": case_tag})
            continue

        try:
            outfile = FASTOutputFile(str(outb_path))
            df = outfile.toDataFrame()

            # RootMyb1 列を取得
            col = next((c for c in df.columns if "RootMyb1" in c), None)
            if col is None:
                print(f"  WARN: RootMyb1 not found in {case_tag}")
                records.append({"V": V, "TI": TI, "DEL_kNm": np.nan, "case_tag": case_tag})
                continue

            signal = df[col].values[skip_steps:]   # 過渡除去
            del_val = rainflow_del(signal, m=M, dt=DT, Teq=TEQ)

            print(f"  {case_tag}: DEL={del_val:.1f} kN-m  (n_steps={len(signal)})")
            records.append({"V": V, "TI": TI, "DEL_kNm": del_val, "case_tag": case_tag})

        except Exception as e:
            print(f"  ERROR {case_tag}: {e}")
            records.append({"V": V, "TI": TI, "DEL_kNm": np.nan, "case_tag": case_tag})

# CSV保存
del_df = pd.DataFrame(records)
out_csv = RESULTS / "del_matrix.csv"
del_df.to_csv(out_csv, index=False)
print(f"\nSaved: {out_csv}")
print(del_df.pivot(index="V", columns="TI", values="DEL_kNm").round(1).to_string())
