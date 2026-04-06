"""
03ms_generate_openfast_inputs.py
Phase 5b マルチシード: OpenFAST 240ケース分の入力ファイルセットを cases_ms/ 以下に生成する

BTSパス: ../../wind_ms/{case_tag}_S{s:02d}.bts
"""

import shutil
from pathlib import Path

SCRIPT_DIR  = Path(__file__).parent
BASE_DIR    = SCRIPT_DIR.parent
TEMPLATE    = BASE_DIR / "template"
CASES_MS    = BASE_DIR / "cases_ms"
WIND_MS_DIR = BASE_DIR / "wind_ms"
FST_ORIG    = BASE_DIR.parent / "r-test/glue-codes/openfast/5MW_Land_DLL_WTurb/5MW_Land_DLL_WTurb.fst"
INFLOW_TMPL = BASE_DIR.parent / "r-test/glue-codes/openfast/5MW_Baseline/NRELOffshrBsline5MW_InflowWind_12mps.dat"

CASES_MS.mkdir(exist_ok=True)

V_LIST   = [4, 6, 8, 10, 12, 14, 16, 18]
TI_LIST  = [0.08, 0.12, 0.14, 0.16, 0.20]
N_SEEDS  = 6

fst_lines = FST_ORIG.read_text().splitlines()


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


base_fst_text = make_base_fst(fst_lines)
inflow_lines  = INFLOW_TMPL.read_text().splitlines()


def make_inflow_dat(lines, tag_full):
    bts_path = f"../../wind_ms/{tag_full}.bts"
    result = []
    for line in lines:
        if "FileName_BTS" in line:
            result.append(f'"{bts_path}"    FileName_BTS   - Name of the Full field wind file to use (.bts)')
        else:
            result.append(line)
    return "\n".join(result) + "\n"


generated = []
for V in V_LIST:
    for TI in TI_LIST:
        case_tag = f"V{V:02d}_TI{int(TI * 100):03d}"
        for s in range(N_SEEDS):
            tag_full = f"{case_tag}_S{s+1:02d}"
            case_dir = CASES_MS / tag_full
            case_dir.mkdir(exist_ok=True)

            (case_dir / "case.fst").write_text(base_fst_text)
            (case_dir / "InflowWind.dat").write_text(make_inflow_dat(inflow_lines, tag_full))

            for fname in ["ElastoDyn.dat", "AeroDyn.dat", "ServoDyn.dat", "DISCON.IN", "Cp_Ct_Cq.NREL5MW.txt"]:
                shutil.copy(TEMPLATE / fname, case_dir / fname)

            generated.append(tag_full)

print(f"Generated {len(generated)} OpenFAST case directories under: {CASES_MS}")
missing = [t for t in generated if not (WIND_MS_DIR / f"{t}.bts").exists()]
print(f"  BTS missing: {len(missing)} / {len(generated)}")
if missing:
    print("  First missing:", missing[0])
