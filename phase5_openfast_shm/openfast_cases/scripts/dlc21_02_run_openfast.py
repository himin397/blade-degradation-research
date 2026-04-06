"""
dlc21_02_run_openfast.py
DLC 2.1: OpenFAST 並列実行（36 ケース）
"""

import subprocess
import concurrent.futures
import time
from pathlib import Path

SCRIPT_DIR   = Path(__file__).parent
BASE_DIR     = SCRIPT_DIR.parent
CASES_DLC21  = BASE_DIR / "cases_dlc21"
OPENFAST_BIN = "/opt/anaconda3/envs/blade-phase3/bin/OpenFAST"
MAX_WORKERS  = 4


def run_openfast(case_dir):
    fst_path  = case_dir / "case.fst"
    outb_path = case_dir / "case.outb"
    if outb_path.exists():
        return (case_dir.name, "skipped", 0.0)
    t0 = time.time()
    result = subprocess.run(
        [OPENFAST_BIN, str(fst_path)],
        capture_output=True, text=True, cwd=case_dir,
    )
    elapsed = time.time() - t0
    if result.returncode != 0:
        (case_dir / "case.err").write_text(result.stderr + result.stdout)
        return (case_dir.name, "ERROR", elapsed)
    if not outb_path.exists():
        return (case_dir.name, "no_outb", elapsed)
    return (case_dir.name, "ok", elapsed)


if __name__ == "__main__":
    all_cases = sorted(d for d in CASES_DLC21.iterdir() if d.is_dir())
    pending   = [d for d in all_cases if not (d / "case.outb").exists()]
    done      = len(all_cases) - len(pending)
    print(f"DLC 2.1 OpenFAST: {len(all_cases)} total / {done} done / {len(pending)} pending")

    if not pending:
        print("全ケース完了済み。")
        exit(0)

    t_start = time.time()
    errors, n_ok = [], 0

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(run_openfast, d): d for d in pending}
        for i, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            name, status, elapsed = fut.result()
            if status in ("ok", "skipped"):
                n_ok += 1
                if i % 6 == 0 or i <= 5:
                    print(f"  [{i:2d}/{len(pending)}] {name}  {elapsed:.0f}s  ✓")
            else:
                errors.append((name, status))
                print(f"  [{i:2d}/{len(pending)}] {name}  {status}  !")

    total_t = time.time() - t_start
    outb_done = len(list(CASES_DLC21.glob("*/case.outb")))
    print(f"\n完了: {n_ok}/{len(pending)}  エラー: {len(errors)}  経過: {total_t/60:.1f}分")
    print(f".outb: {outb_done}/{len(all_cases)}")
    if errors:
        for name, status in errors[:5]:
            print(f"  ERROR: {name}: {status}")
