"""
dlc13_04_run_openfast.py
Phase 6: DLC 1.3 OpenFAST 48ケース実行
"""
import subprocess, concurrent.futures, time
from pathlib import Path

SCRIPT_DIR   = Path(__file__).parent
CASES_DLC13  = SCRIPT_DIR.parent / "cases_dlc13"
OPENFAST_BIN = "/opt/anaconda3/envs/blade-phase3/bin/OpenFAST"

case_dirs = sorted(CASES_DLC13.iterdir())
print(f"Found {len(case_dirs)} DLC 1.3 OpenFAST cases")


def run_openfast(case_dir):
    t0 = time.time()
    result = subprocess.run(
        [OPENFAST_BIN, str(case_dir / "case.fst")],
        cwd=str(case_dir),
        capture_output=True, text=True, timeout=3600
    )
    elapsed = time.time() - t0
    ok = (case_dir / "case.outb").exists()
    return case_dir.name, ok, elapsed, result.stderr[-200:] if result.stderr else ""


if __name__ == "__main__":
    print("Running DLC 1.3 OpenFAST (max_workers=4)...")
    t_start = time.time()
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as exe:
        futures = {exe.submit(run_openfast, d): d for d in case_dirs}
        for future in concurrent.futures.as_completed(futures):
            tag, ok, elapsed, err = future.result()
            print(f"  {tag}: {'OK' if ok else 'FAIL'} ({elapsed:.0f}s)")
            if not ok and err:
                print(f"    {err[:150]}")
            results.append((tag, ok))
    n_ok = sum(1 for _, ok in results if ok)
    total = time.time() - t_start
    print(f"\nCompleted: {n_ok}/{len(results)} OK  (total {total:.0f}s)")
