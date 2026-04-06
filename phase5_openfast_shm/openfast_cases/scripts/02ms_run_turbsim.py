"""
02ms_run_turbsim.py
Phase 5b マルチシード: TurbSim 240ケースを並列実行して .bts ファイルを生成する
"""

import subprocess
import concurrent.futures
from pathlib import Path

SCRIPT_DIR  = Path(__file__).parent
WIND_MS_DIR = SCRIPT_DIR.parent / "wind_ms"
TURBSIM_BIN = "/opt/anaconda3/envs/blade-phase3/bin/TurbSim"

# 既存の有効BTS（size > 0）をスキップして未完了ケースのみ実行
all_inp = sorted(WIND_MS_DIR.glob("*.inp"))
inp_files = []
for f in all_inp:
    bts = f.with_suffix(".bts")
    if bts.exists() and bts.stat().st_size > 0:
        pass  # skip
    else:
        inp_files.append(f)
print(f"Found {len(all_inp)} total, {len(inp_files)} need to run (skipping {len(all_inp)-len(inp_files)} existing)")


def run_turbsim(inp_path):
    result = subprocess.run(
        [TURBSIM_BIN, str(inp_path)],
        cwd=str(inp_path.parent),
        capture_output=True,
        text=True,
        timeout=600
    )
    bts_path = inp_path.with_suffix(".bts")
    ok = bts_path.exists()
    return inp_path.stem, result.returncode, ok, result.stderr[-200:] if result.stderr else ""


if __name__ == "__main__":
    print("Running TurbSim multi-seed (max_workers=4)...")
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as exe:
        futures = {exe.submit(run_turbsim, f): f for f in inp_files}
        for future in concurrent.futures.as_completed(futures):
            tag, rc, ok, err = future.result()
            status = "OK" if ok else f"FAIL(rc={rc})"
            print(f"  {tag}: {status}")
            results.append((tag, ok))

    n_ok   = sum(1 for _, ok in results if ok)
    n_fail = len(results) - n_ok
    print(f"\nCompleted: {n_ok}/{len(results)} OK, {n_fail} failed")
    if n_fail > 0:
        for tag, ok in sorted(results):
            if not ok:
                print(f"  FAILED: {tag}")
