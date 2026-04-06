"""
mm82_02_run_turbsim.py
Phase I MM82: TurbSim 並列実行 (240ケース → 240 BTS ファイル)

実行前提: mm82_01_gen_turbsim.py を実行済み
出力: wind_mm82/{case_tag}_S{seed}.bts
"""

import subprocess
import concurrent.futures
import time
from pathlib import Path

SCRIPT_DIR   = Path(__file__).parent
BASE_DIR     = SCRIPT_DIR.parent
WIND_MM82    = BASE_DIR / "wind_mm82"
TURBSIM_BIN  = "/opt/anaconda3/envs/blade-phase3/bin/TurbSim"

MAX_WORKERS  = 4   # 並列数 (CPU コア数に合わせて調整)


def run_turbsim(inp_path):
    """単一 TurbSim ケースを実行"""
    bts_path = inp_path.with_suffix(".bts")
    if bts_path.exists():
        return (inp_path.stem, "skipped", 0.0)

    t0 = time.time()
    result = subprocess.run(
        [TURBSIM_BIN, str(inp_path)],
        capture_output=True,
        text=True,
        cwd=inp_path.parent,
    )
    elapsed = time.time() - t0

    if result.returncode != 0:
        return (inp_path.stem, "ERROR", elapsed)
    if not bts_path.exists():
        return (inp_path.stem, "no_bts", elapsed)
    return (inp_path.stem, "ok", elapsed)


if __name__ == "__main__":
    # ── 未完了ケースを収集 ────────────────────────────────────────────────────
    inp_files = sorted(WIND_MM82.glob("*.inp"))
    pending   = [f for f in inp_files if not f.with_suffix(".bts").exists()]
    done      = len(inp_files) - len(pending)

    print(f"TurbSim MM82: {len(inp_files)} total / {done} already done / {len(pending)} to run")
    if not pending:
        print("全 BTS ファイル生成済み。スキップ。")
        exit(0)

    # ── 並列実行 ─────────────────────────────────────────────────────────────
    t_start  = time.time()
    errors   = []
    n_ok     = 0

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(run_turbsim, f): f for f in pending}
        for i, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            stem, status, elapsed = fut.result()
            if status == "ok":
                n_ok += 1
                print(f"  [{i:3d}/{len(pending)}] {stem}  {elapsed:.1f}s  ✓")
            elif status == "skipped":
                n_ok += 1
            else:
                errors.append((stem, status))
                print(f"  [{i:3d}/{len(pending)}] {stem}  {status}  !")

    total_t = time.time() - t_start
    print(f"\n完了: {n_ok}/{len(pending)}  エラー: {len(errors)}  経過時間: {total_t:.0f}s")
    if errors:
        print("エラー一覧:")
        for stem, status in errors:
            print(f"  {stem}: {status}")

    # ── BTS 完成数確認 ────────────────────────────────────────────────────────
    bts_done = len(list(WIND_MM82.glob("*.bts")))
    print(f"\nBTS ファイル: {bts_done}/{len(inp_files)}")
