"""
low_ti_extension_pipeline.py
Phase 3 Priority 2: 低TI域拡張パイプライン（統合・全5ステップ）

背景:
    実SCADAサイトのIEC TI（0.030〜0.044）が既存シミュレーション行列の
    下限（TI=0.08）を大幅に下回り、phase3b_del_lookup.py で全月
    TI=0.08クリップが発生している。
    本スクリプトは TI=0.02, 0.04, 0.06 を追加し、DEL行列を低TI域に拡張する。

処理フロー（全自動）:
    Step 1: TurbSim 入力ファイル生成（wind_loti/）
    Step 2: TurbSim 並列実行（max_workers=4）
    Step 3: OpenFAST 入力ファイル生成（cases_loti/）
    Step 4: OpenFAST 並列実行（max_workers=4）
    Step 5: DEL抽出（標準Rainflow）+ del_matrix_ms_extended.csv 生成

新ケース数: V(8) × TI(3) × Seed(6) = 144ケース
出力: results/del_matrix_ms_extended.csv（既存40条件 + 新24条件 = 64条件）

環境: conda env blade-phase3
"""

from pathlib import Path
import subprocess
import concurrent.futures
import time
import shutil
import numpy as np
import pandas as pd

try:
    import rainflow
except ImportError:
    raise ImportError("rainflow が見つかりません。blade-phase3 環境で実行してください。")

try:
    from openfast_io.FAST_output_reader import FASTOutputFile
except ImportError:
    raise ImportError("openfast_io が見つかりません。blade-phase3 環境で実行してください。")


# ─────────────────────────────────────────────────────────────
# パス定義
# ─────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
BASE_DIR     = SCRIPT_DIR.parent
RESULTS      = BASE_DIR / "results"
WIND_LOTI    = BASE_DIR / "wind_loti"
CASES_LOTI   = BASE_DIR / "cases_loti"
RESULTS.mkdir(exist_ok=True)
WIND_LOTI.mkdir(exist_ok=True)
CASES_LOTI.mkdir(exist_ok=True)

TURBSIM_BIN  = "/opt/anaconda3/envs/blade-phase3/bin/TurbSim"
OPENFAST_BIN = "/opt/anaconda3/envs/blade-phase3/bin/OpenFAST"

TEMPLATE_INP = BASE_DIR.parent / "r-test/glue-codes/openfast/5MW_Baseline/Wind/90m_12mps_twr.inp"
FST_ORIG     = BASE_DIR.parent / "r-test/glue-codes/openfast/5MW_Land_DLL_WTurb/5MW_Land_DLL_WTurb.fst"
INFLOW_TMPL  = BASE_DIR.parent / "r-test/glue-codes/openfast/5MW_Baseline/NRELOffshrBsline5MW_InflowWind_12mps.dat"
TEMPLATE     = BASE_DIR / "template"

# 低TI拡張グリッド
V_LIST       = [4, 6, 8, 10, 12, 14, 16, 18]
TI_LIST_EXT  = [0.02, 0.04, 0.06]
N_SEEDS      = 6

# DEL算出パラメータ
DT   = 0.00625
M    = 10
TEQ  = 600.0
SKIP = 60.0


# ─────────────────────────────────────────────────────────────
# Step 1: TurbSim 入力ファイル生成
# ─────────────────────────────────────────────────────────────

def get_param_name(line):
    stripped = line.strip()
    if not stripped or stripped.startswith("!") or stripped.startswith("-") or stripped.startswith("="):
        return None
    tokens = stripped.split()
    return tokens[1] if len(tokens) >= 2 else None


def modify_turbsim_inp(lines, V, TI, seed):
    analysis_time = max(660, int(600 + 145 / V) + 10)
    ti_pct = TI * 100
    result = []
    for line in lines:
        param = get_param_name(line)
        if param == "RandSeed1":
            result.append(f"   {seed:8d}   RandSeed1       - First random seed  (-2147483648 to 2147483647)")
        elif param == "WrADTWR":
            result.append("False         WrADTWR         - Output tower time-series data? (Generates RootName.twr)")
        elif param == "AnalysisTime":
            result.append(f"   {analysis_time:8d}   AnalysisTime    - Length of analysis time series [seconds]")
        elif param == "UsableTime":
            result.append(f"        600   UsableTime      - Usable length of output time series [seconds]")
        elif param == "IECturbc":
            result.append(f'"{ti_pct:.1f}"         IECturbc        - IEC turbulence characteristic (turbulence intensity in percent)')
        elif param == "URef":
            result.append(f"      {V:6.1f}   URef            - Mean (total) velocity at the reference height [m/s]")
        else:
            result.append(line)
    return "\n".join(result) + "\n"


def step1_generate_turbsim_inputs():
    print("\n=== Step 1: TurbSim 入力ファイル生成 ===")
    template_lines = TEMPLATE_INP.read_text().splitlines()
    seeds = [12345 + i * 1000 for i in range(N_SEEDS)]
    generated = []
    for V in V_LIST:
        for TI in TI_LIST_EXT:
            tag = f"V{V:02d}_TI{int(TI * 100):03d}"
            for s_idx, seed in enumerate(seeds):
                tag_full = f"{tag}_S{s_idx + 1:02d}"
                out_path = WIND_LOTI / f"{tag_full}.inp"
                if not out_path.exists():
                    content = modify_turbsim_inp(template_lines, V, TI, seed)
                    out_path.write_text(content)
                generated.append(out_path)
    print(f"  生成: {len(generated)} ファイル → wind_loti/")
    return generated


# ─────────────────────────────────────────────────────────────
# Step 2: TurbSim 並列実行
# ─────────────────────────────────────────────────────────────

def run_turbsim(inp_path):
    bts = inp_path.with_suffix(".bts")
    if bts.exists() and bts.stat().st_size > 0:
        return inp_path.stem, 0, True, 0.0, ""
    t0 = time.time()
    res = subprocess.run(
        [TURBSIM_BIN, str(inp_path)],
        cwd=str(inp_path.parent),
        capture_output=True, text=True, timeout=600
    )
    elapsed = time.time() - t0
    ok = bts.exists() and bts.stat().st_size > 0
    return inp_path.stem, res.returncode, ok, elapsed, res.stderr[-200:] if res.stderr else ""


def step2_run_turbsim():
    print("\n=== Step 2: TurbSim 並列実行 ===")
    inp_files = sorted(WIND_LOTI.glob("*.inp"))
    to_run = [f for f in inp_files if not (f.with_suffix(".bts").exists()
                                           and f.with_suffix(".bts").stat().st_size > 0)]
    print(f"  {len(inp_files)} 入力中、{len(to_run)} 件を実行（スキップ: {len(inp_files) - len(to_run)}）")
    if not to_run:
        print("  全件スキップ（既存BTSあり）")
        return True
    t_start = time.time()
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as exe:
        futures = {exe.submit(run_turbsim, f): f for f in to_run}
        for future in concurrent.futures.as_completed(futures):
            tag, rc, ok, elapsed, err = future.result()
            print(f"  {tag}: {'OK' if ok else f'FAIL(rc={rc})'} ({elapsed:.0f}s)")
            results.append((tag, ok))
    n_ok = sum(1 for _, ok in results if ok)
    print(f"  完了: {n_ok}/{len(results)} OK  (経過: {time.time() - t_start:.0f}s)")
    return n_ok == len(results)


# ─────────────────────────────────────────────────────────────
# Step 3: OpenFAST 入力ファイル生成
# ─────────────────────────────────────────────────────────────

def make_base_fst(lines):
    result = []
    for line in lines:
        if "TMax" in line and "Total run" in line:
            result.append("        600   TMax            - Total run time (s)")
        elif "SumPrint" in line:
            result.append("False         SumPrint        - Print summary data to \"<RootName>.sum\" (flag)")
        elif "OutFileFmt" in line:
            result.append("          2   OutFileFmt      - Format for tabular output {1:text, 2:binary(.outb), 3:both, 4:uncompressed binary}")
        elif "EDFile" in line and "BDBldFile" not in line:
            result.append('"ElastoDyn.dat"    EDFile          - Name of file containing ElastoDyn input parameters (quoted string)')
        elif "AeroFile" in line:
            result.append('"AeroDyn.dat"    AeroFile        - Name of file containing aerodynamic input parameters (quoted string)')
        elif "ServoFile" in line:
            result.append('"ServoDyn.dat"    ServoFile       - Name of file containing control and electrical-drive input parameters (quoted string)')
        elif "InflowFile" in line:
            result.append('"InflowWind.dat"    InflowFile      - Name of file containing inflow wind input parameters (quoted string)')
        else:
            result.append(line)
    return "\n".join(result) + "\n"


def make_inflow_dat(lines, tag_full):
    bts_path = f"../../wind_loti/{tag_full}.bts"
    result = []
    for line in lines:
        if "FileName_BTS" in line:
            result.append(f'"{bts_path}"    FileName_BTS   - Name of the Full field wind file to use (.bts)')
        else:
            result.append(line)
    return "\n".join(result) + "\n"


def step3_generate_openfast_inputs():
    print("\n=== Step 3: OpenFAST 入力ファイル生成 ===")
    fst_lines     = FST_ORIG.read_text().splitlines()
    base_fst_text = make_base_fst(fst_lines)
    inflow_lines  = INFLOW_TMPL.read_text().splitlines()

    generated = []
    for V in V_LIST:
        for TI in TI_LIST_EXT:
            case_tag = f"V{V:02d}_TI{int(TI * 100):03d}"
            for s in range(N_SEEDS):
                tag_full = f"{case_tag}_S{s + 1:02d}"
                case_dir = CASES_LOTI / tag_full
                if case_dir.exists() and (case_dir / "case.outb").exists():
                    generated.append(case_dir)
                    continue
                case_dir.mkdir(exist_ok=True)
                # template ファイル群をコピー
                for src in TEMPLATE.iterdir():
                    shutil.copy2(src, case_dir / src.name)
                # .fst
                (case_dir / "case.fst").write_text(base_fst_text)
                # InflowWind.dat
                inflow_text = make_inflow_dat(inflow_lines, tag_full)
                (case_dir / "InflowWind.dat").write_text(inflow_text)
                generated.append(case_dir)
    print(f"  準備完了: {len(generated)} ケースディレクトリ → cases_loti/")
    return generated


# ─────────────────────────────────────────────────────────────
# Step 4: OpenFAST 並列実行
# ─────────────────────────────────────────────────────────────

def run_openfast(case_dir):
    fst_file = case_dir / "case.fst"
    outb     = case_dir / "case.outb"
    if outb.exists() and outb.stat().st_size > 0:
        return case_dir.name, 0, True, 0.0, ""
    t0  = time.time()
    res = subprocess.run(
        [OPENFAST_BIN, str(fst_file)],
        cwd=str(case_dir),
        capture_output=True, text=True, timeout=3600
    )
    elapsed = time.time() - t0
    ok = outb.exists() and outb.stat().st_size > 0
    return case_dir.name, res.returncode, ok, elapsed, res.stderr[-300:] if res.stderr else ""


def step4_run_openfast():
    print("\n=== Step 4: OpenFAST 並列実行 ===")
    case_dirs = sorted(CASES_LOTI.iterdir())
    to_run = [d for d in case_dirs if not ((d / "case.outb").exists()
                                           and (d / "case.outb").stat().st_size > 0)]
    print(f"  {len(case_dirs)} ケース中、{len(to_run)} 件を実行（スキップ: {len(case_dirs) - len(to_run)}）")
    if not to_run:
        print("  全件スキップ（既存 .outb あり）")
        return True
    print(f"  推定所要時間: {len(to_run) // 4 * 1.5:.0f}〜{len(to_run) // 4 * 2:.0f} 分（4並列）")
    t_start = time.time()
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as exe:
        futures = {exe.submit(run_openfast, d): d for d in to_run}
        for future in concurrent.futures.as_completed(futures):
            tag, rc, ok, elapsed, err = future.result()
            print(f"  {tag}: {'OK' if ok else f'FAIL(rc={rc})'} ({elapsed:.0f}s)")
            if not ok and err:
                print(f"    STDERR: {err[:200]}")
            results.append((tag, ok))
    n_ok = sum(1 for _, ok in results if ok)
    print(f"  完了: {n_ok}/{len(results)} OK  (経過: {time.time() - t_start:.0f}s)")
    return n_ok == len(results)


# ─────────────────────────────────────────────────────────────
# Step 5: DEL抽出 + 行列統合
# ─────────────────────────────────────────────────────────────

def del_standard_rainflow(signal, m=10, dt=DT, Teq=TEQ):
    sig = np.asarray(signal, dtype=float)
    damage = 0.0
    for rng, count in rainflow.count_cycles(sig, nbins=None):
        damage += count * (rng ** m)
    T_actual = len(sig) * dt
    N_eq = Teq / T_actual
    if N_eq <= 0 or damage <= 0:
        return 0.0
    return float((damage / N_eq) ** (1.0 / m))


def extract_del_from_outb(outb_path):
    try:
        f = FASTOutputFile(str(outb_path))
        df = f.toDataFrame()
        t = df["Time_[s]"].values
        skip_idx = np.searchsorted(t, SKIP)
        signal = df["RootMyb1_[kN-m]"].values[skip_idx:]
        if len(signal) < 100:
            return np.nan
        return del_standard_rainflow(signal)
    except Exception as e:
        print(f"    警告: {outb_path.parent.name} DEL抽出失敗: {e}")
        return np.nan


def step5_extract_and_merge():
    print("\n=== Step 5: DEL抽出 + 行列統合 ===")

    # 新ケースのDEL抽出
    rows = []
    for V in V_LIST:
        for TI in TI_LIST_EXT:
            case_tag = f"V{V:02d}_TI{int(TI * 100):03d}"
            del_vals = []
            for s in range(N_SEEDS):
                tag_full = f"{case_tag}_S{s + 1:02d}"
                outb_path = CASES_LOTI / tag_full / "case.outb"
                if outb_path.exists():
                    del_val = extract_del_from_outb(outb_path)
                    if not np.isnan(del_val):
                        del_vals.append(del_val)
            if del_vals:
                rows.append({
                    "V": V,
                    "TI": TI,
                    "case_tag": case_tag,
                    "DEL_mean": np.mean(del_vals),
                    "DEL_std": np.std(del_vals, ddof=1) if len(del_vals) > 1 else 0.0,
                    "DEL_cv": (np.std(del_vals, ddof=1) / np.mean(del_vals)
                               if len(del_vals) > 1 and np.mean(del_vals) > 0 else 0.0),
                    "n_seeds": len(del_vals),
                })
            else:
                print(f"  警告: {case_tag} — 有効シードなし（スキップ）")

    if not rows:
        print("  エラー: 新規DEL結果が0件です。OpenFASTが正常完了しているか確認してください。")
        return

    df_new = pd.DataFrame(rows)
    print(f"\n  新規DEL結果: {len(df_new)} 条件")
    print(df_new[["V", "TI", "DEL_mean", "DEL_cv", "n_seeds"]].to_string(index=False))

    # 既存行列と統合
    orig_path = RESULTS / "del_matrix_ms.csv"
    if orig_path.exists():
        df_orig = pd.read_csv(orig_path)
        df_ext  = pd.concat([df_orig, df_new], ignore_index=True)
        df_ext  = df_ext.sort_values(["V", "TI"]).reset_index(drop=True)
    else:
        df_ext = df_new

    out_path = RESULTS / "del_matrix_ms_extended.csv"
    df_ext.to_csv(out_path, index=False)
    print(f"\n  保存: results/del_matrix_ms_extended.csv")
    print(f"  行列サイズ: {len(df_ext)} 条件（TI範囲: {df_ext['TI'].min():.2f}〜{df_ext['TI'].max():.2f}）")

    # サマリー表
    print("\n  拡張DEL行列（新規TI点のみ）:")
    print(f"  {'V':>4}  {'TI':>6}  {'DEL_mean':>10}  {'CV':>7}  {'n':>3}")
    print("  " + "-" * 40)
    for _, row in df_new.iterrows():
        print(f"  {int(row['V']):>4}  {row['TI']:>6.3f}  {row['DEL_mean']:>10.1f}  "
              f"{row['DEL_cv'] * 100:>6.1f}%  {int(row['n_seeds']):>3}")


# ─────────────────────────────────────────────────────────────
# メイン
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Phase 3 Priority 2: 低TI域拡張パイプライン")
    print(f"  新TI点: {TI_LIST_EXT}")
    print(f"  V点数: {V_LIST}")
    print(f"  シード数: {N_SEEDS}")
    print(f"  新ケース数: {len(V_LIST)} × {len(TI_LIST_EXT)} × {N_SEEDS} = "
          f"{len(V_LIST) * len(TI_LIST_EXT) * N_SEEDS}")
    print("=" * 60)

    t_total = time.time()

    step1_generate_turbsim_inputs()
    ok_ts = step2_run_turbsim()
    if not ok_ts:
        print("\n警告: TurbSim に失敗したケースがあります。続行します。")

    step3_generate_openfast_inputs()
    ok_of = step4_run_openfast()
    if not ok_of:
        print("\n警告: OpenFAST に失敗したケースがあります。続行します。")

    step5_extract_and_merge()

    print(f"\n{'=' * 60}")
    print(f"低TI域拡張パイプライン 完了  (総経過時間: {(time.time() - t_total) / 60:.1f} 分)")
    print(f"{'=' * 60}")
    print("\n次のステップ:")
    print("  phase3b_del_lookup.py の interpolator を")
    print("  del_matrix_ms_extended.csv に切り替えてください。")
