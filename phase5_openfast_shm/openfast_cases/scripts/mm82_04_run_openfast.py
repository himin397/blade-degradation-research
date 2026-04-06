"""
mm82_04_run_openfast.py
Phase I MM82: OpenFAST 並列実行 (240ケース)

実行前提:
  - mm82_02_run_turbsim.py 完了 (BTS ファイル生成済み)
  - mm82_03_gen_openfast.py 完了 (ケースディレクトリ生成済み)

出力: cases_mm82/{tag}/case.outb (バイナリ出力)
"""

import subprocess
import concurrent.futures
import time
from pathlib import Path

SCRIPT_DIR   = Path(__file__).parent
BASE_DIR     = SCRIPT_DIR.parent
CASES_MM82   = BASE_DIR / "cases_mm82"
OPENFAST_BIN = "/opt/anaconda3/envs/blade-phase3/bin/OpenFAST"

MAX_WORKERS  = 4


def run_openfast(case_dir):
    """単一 OpenFAST ケースを実行"""
    fst_path  = case_dir / "case.fst"
    outb_path = case_dir / "case.outb"

    if outb_path.exists():
        return (case_dir.name, "skipped", 0.0)

    t0 = time.time()
    result = subprocess.run(
        [OPENFAST_BIN, str(fst_path)],
        capture_output=True,
        text=True,
        cwd=case_dir,
    )
    elapsed = time.time() - t0

    if result.returncode != 0:
        # エラーログを保存
        (case_dir / "case.err").write_text(result.stderr + result.stdout)
        return (case_dir.name, "ERROR", elapsed)
    if not outb_path.exists():
        return (case_dir.name, "no_outb", elapsed)
    return (case_dir.name, "ok", elapsed)


if __name__ == "__main__":
    # ── 実行対象ケース収集 ────────────────────────────────────────────────────
    WIND_MM82 = BASE_DIR / "wind_mm82"

    all_cases = sorted(d for d in CASES_MM82.iterdir() if d.is_dir())
    # BTS が存在するケースのみ実行対象に含める
    pending   = [
        d for d in all_cases
        if not (d / "case.outb").exists()
        and (WIND_MM82 / f"{d.name}.bts").exists()
        and (WIND_MM82 / f"{d.name}.bts").stat().st_size > 0
    ]
    no_bts  = sum(1 for d in all_cases
                  if not (d / "case.outb").exists()
                  and (not (WIND_MM82 / f"{d.name}.bts").exists()
                       or (WIND_MM82 / f"{d.name}.bts").stat().st_size == 0))
    done      = sum(1 for d in all_cases if (d / "case.outb").exists())

    print(f"OpenFAST MM82: {len(all_cases)} total / {done} done / {len(pending)} ready to run / {no_bts} waiting for BTS")
    if not pending:
        print("全 .outb ファイル生成済み。スキップ。")
        exit(0)

    # ── 並列実行 ─────────────────────────────────────────────────────────────
    t_start = time.time()
    errors  = []
    n_ok    = 0

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(run_openfast, d): d for d in pending}
        for i, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            name, status, elapsed = fut.result()
            if status == "ok":
                n_ok += 1
                if i % 10 == 0 or i <= 5:
                    print(f"  [{i:3d}/{len(pending)}] {name}  {elapsed:.1f}s  ✓")
            elif status == "skipped":
                n_ok += 1
            else:
                errors.append((name, status))
                print(f"  [{i:3d}/{len(pending)}] {name}  {status}  !")

    total_t = time.time() - t_start
    outb_done = len(list(CASES_MM82.glob("*/case.outb")))
    print(f"\n完了: {n_ok}/{len(pending)}  エラー: {len(errors)}  経過時間: {total_t:.0f}s ({total_t/60:.1f}分)")
    print(f".outb ファイル: {outb_done}/{len(all_cases)}")
    if errors:
        print("エラー一覧 (最大10件):")
        for name, status in errors[:10]:
            print(f"  {name}: {status}")
