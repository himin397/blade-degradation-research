"""
03_generate_openfast_inputs.py
Phase 5b: OpenFAST 40ケース分の入力ファイルセットを cases/ 以下に生成する

各ケースフォルダに配置するファイル:
  case.fst        - メイン入力ファイル（TMax=600, InflowWind.dat参照）
  InflowWind.dat  - ケース固有のBTSファイルを参照
  ElastoDyn.dat   - テンプレートからコピー
  AeroDyn.dat     - テンプレートからコピー
  ServoDyn.dat    - テンプレートからコピー
  DISCON.IN       - テンプレートからコピー
"""

import shutil
from pathlib import Path

SCRIPT_DIR  = Path(__file__).parent
BASE_DIR    = SCRIPT_DIR.parent
TEMPLATE    = BASE_DIR / "template"
CASES_DIR   = BASE_DIR / "cases"
WIND_DIR    = BASE_DIR / "wind"
FST_ORIG    = BASE_DIR.parent / "r-test/glue-codes/openfast/5MW_Land_DLL_WTurb/5MW_Land_DLL_WTurb.fst"  # v3.5.1 tag
INFLOW_TMPL = BASE_DIR.parent / "r-test/glue-codes/openfast/5MW_Baseline/NRELOffshrBsline5MW_InflowWind_12mps.dat"  # v3.5.1 tag

CASES_DIR.mkdir(exist_ok=True)

V_LIST  = [4, 6, 8, 10, 12, 14, 16, 18]
TI_LIST = [0.08, 0.12, 0.14, 0.16, 0.20]

# --- FST テンプレートを base.fst として修正済みコピーを作成 ---
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

# InflowWind テンプレート読み込み
inflow_lines = INFLOW_TMPL.read_text().splitlines()

def make_inflow_dat(lines, case_tag):
    """ケース固有の InflowWind.dat を生成（BTSファイルパスのみ変更）"""
    bts_path = f"../../wind/{case_tag}.bts"
    result = []
    for line in lines:
        if "FileName_BTS" in line:
            result.append(f'"{bts_path}"    FileName_BTS   - Name of the Full field wind file to use (.bts)')
        else:
            result.append(line)
    return "\n".join(result) + "\n"

# --- 各ケースのファイルセット生成 ---
generated = []
for V in V_LIST:
    for TI in TI_LIST:
        case_tag = f"V{V:02d}_TI{int(TI * 100):03d}"
        case_dir = CASES_DIR / case_tag
        case_dir.mkdir(exist_ok=True)

        # case.fst
        (case_dir / "case.fst").write_text(base_fst_text)

        # InflowWind.dat（ケース固有）
        (case_dir / "InflowWind.dat").write_text(make_inflow_dat(inflow_lines, case_tag))

        # テンプレートファイルをコピー
        for fname in ["ElastoDyn.dat", "AeroDyn.dat", "ServoDyn.dat", "DISCON.IN", "Cp_Ct_Cq.NREL5MW.txt"]:
            shutil.copy(TEMPLATE / fname, case_dir / fname)

        generated.append(case_tag)

print(f"Generated {len(generated)} OpenFAST case directories under: {CASES_DIR}")
for tag in generated:
    bts_exists = (WIND_DIR / f"{tag}.bts").exists()
    print(f"  {tag}  bts={'OK' if bts_exists else 'MISSING'}")
