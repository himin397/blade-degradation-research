"""
04ms_run_openfast.py
Phase 5b マルチシード: OpenFAST 240ケースを並列実行する
"""

import subprocess
import concurrent.futures
from pathlib import Path
import time

SCRIPT_DIR   = Path(__file__).parent
CASES_MS     = SCRIPT_DIR.parent / "cases_ms"
OPENFAST_BIN = "/opt/anaconda3/envs/blade-phase3/bin/OpenFAST"

case_dirs = sorted(CASES_MS.iterdir())
print(f"Found {len(case_dirs)} OpenFAST multi-seed cases")


def run_openfast(case_dir):
    fst_file = case_dir / "case.fst"
    t0 = time.time()
    result = subprocess.run(
        [OPENFAST_BIN, str(fst_file)],
        cwd=str(case_dir),
        capture_output=True,
        text=True,
        timeout=3600
    )
    elapsed = time.time() - t0
    outb = case_dir / "case.outb"
    ok = outb.exists()
    return case_dir.name, result.returncode, ok, elapsed, result.stderr[-300:] if result.stderr else ""


if __name__ == "__main__":
    print("Running OpenFAST multi-seed (max_workers=4)... This will take ~60-120 minutes total.")
    t_start = time.time()
    results = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as exe:
        futures = {exe.submit(run_openfast, d): d for d in case_dirs}
        for future in concurrent.futures.as_completed(futures):
            tag, rc, ok, elapsed, err = future.result()
            status = f"OK ({elapsed:.0f}s)" if ok else f"FAIL(rc={rc}, {elapsed:.0f}s)"
            print(f"  {tag}: {status}")
            if not ok and err:
                print(f"    STDERR: {err[:200]}")
            results.append((tag, ok))

    total_elapsed = time.time() - t_start
    n_ok   = sum(1 for _, ok in results if ok)
    n_fail = len(results) - n_ok
    print(f"\nCompleted: {n_ok}/{len(results)} OK, {n_fail} failed  (total {total_elapsed:.0f}s)")
    if n_fail > 0:
        print("Failed cases:")
        for tag, ok in sorted(results):
            if not ok:
                print(f"  {tag}")
