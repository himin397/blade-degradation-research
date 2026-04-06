"""
dlc13_02_run_turbsim.py
Phase 6: DLC 1.3 TurbSim 48ケース実行（8V × 6seeds）
"""
import subprocess, concurrent.futures, time
from pathlib import Path

SCRIPT_DIR  = Path(__file__).parent
WIND_DLC13  = SCRIPT_DIR.parent / "wind_dlc13"
TURBSIM_BIN = "/opt/anaconda3/envs/blade-phase3/bin/TurbSim"

all_inp   = sorted(WIND_DLC13.glob("*.inp"))
inp_files = [f for f in all_inp
             if not (f.with_suffix(".bts").exists() and f.with_suffix(".bts").stat().st_size > 0)]
print(f"Found {len(all_inp)} total, {len(inp_files)} need to run")


def run_turbsim(inp_path):
    result = subprocess.run(
        [TURBSIM_BIN, str(inp_path)],
        cwd=str(inp_path.parent),
        capture_output=True, text=True, timeout=600
    )
    bts = inp_path.with_suffix(".bts")
    ok  = bts.exists() and bts.stat().st_size > 0
    return inp_path.stem, ok, result.stderr[-200:] if result.stderr else ""


if __name__ == "__main__":
    print("Running DLC 1.3 TurbSim (max_workers=4)...")
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as exe:
        futures = {exe.submit(run_turbsim, f): f for f in inp_files}
        for future in concurrent.futures.as_completed(futures):
            tag, ok, err = future.result()
            print(f"  {tag}: {'OK' if ok else 'FAIL'}")
            results.append((tag, ok))
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\nCompleted: {n_ok}/{len(results)} OK")
