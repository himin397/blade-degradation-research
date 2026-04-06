"""
mm82_03_gen_openfast.py
Phase I MM82: OpenFAST ケースディレクトリ生成 (240ケース)

各ケースディレクトリに配置するファイル:
  case.fst        (メイン FST、BTS パス + MM82 パラメータ)
  InflowWind.dat  (HubHt=59m、BTS ファイルパス)
  ElastoDyn.dat   → template_mm82/ からコピー (BldFile/TwrFile は相対パス)
  AeroDyn.dat     → template_mm82/ からコピー (ADBlFile は相対パス)
  ServoDyn.dat    → template_mm82/ からコピー
  DISCON.IN       → template_mm82/ からコピー
  Cp_Ct_Cq.NREL5MW.txt → template_mm82/ からコピー
  MM82_Blade.dat  → template_mm82/ からコピー (ElastoDyn の BldFile)
  MM82_Tower.dat  → template_mm82/ からコピー (ElastoDyn の TwrFile)
  MM82_AeroDyn_blade.dat → template_mm82/ からコピー (AeroDyn の ADBlFile)
"""

import shutil
from pathlib import Path

SCRIPT_DIR  = Path(__file__).parent
BASE_DIR    = SCRIPT_DIR.parent
TMPL_MM82   = BASE_DIR / "template_mm82"
CASES_MM82  = BASE_DIR / "cases_mm82"
WIND_MM82   = BASE_DIR / "wind_mm82"
CASES_MM82.mkdir(exist_ok=True)

# オリジナル FST ベース
FST_ORIG   = BASE_DIR.parent / "r-test/glue-codes/openfast/5MW_Land_DLL_WTurb/5MW_Land_DLL_WTurb.fst"
INFLOW_TMPL = BASE_DIR.parent / "r-test/glue-codes/openfast/5MW_Baseline/NRELOffshrBsline5MW_InflowWind_12mps.dat"

V_LIST   = [4, 6, 8, 10, 12, 14, 16, 18]
TI_LIST  = [0.08, 0.12, 0.14, 0.16, 0.20]
N_SEEDS  = 6

HUB_HT_MM82 = 59   # m

fst_lines    = FST_ORIG.read_text().splitlines()
inflow_lines = INFLOW_TMPL.read_text().splitlines()


def make_base_fst(lines):
    """FST ファイルを MM82 用に変換"""
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
    """InflowWind.dat を MM82 ハブ高さ + BTS パス用に変換"""
    bts_path = f"../../wind_mm82/{tag_full}.bts"
    result = []
    for line in lines:
        if "FileName_BTS" in line:
            result.append(f'"{bts_path}"    FileName_BTS   - Name of the Full field wind file to use (.bts)')
        elif "WindVziList" in line:
            # ハブ高さで風速を出力するために更新
            result.append(f"        {HUB_HT_MM82}   WindVziList    - List of coordinates in the inertial Z direction (m)")
        else:
            result.append(line)
    return "\n".join(result) + "\n"


base_fst_text = make_base_fst(fst_lines)

# MM82 テンプレートからコピーするファイル一覧
template_files = [
    "ElastoDyn.dat",
    "AeroDyn.dat",
    "ServoDyn.dat",
    "DISCON.IN",
    "Cp_Ct_Cq.NREL5MW.txt",
    "MM82_Blade.dat",
    "MM82_Tower.dat",
    "MM82_AeroDyn_blade.dat",
]

generated = []
skipped   = 0
for V in V_LIST:
    for TI in TI_LIST:
        case_tag = f"V{V:02d}_TI{int(TI * 100):03d}"
        for s in range(N_SEEDS):
            tag_full = f"{case_tag}_S{s+1:02d}"
            case_dir = CASES_MM82 / tag_full
            case_dir.mkdir(exist_ok=True)

            # メイン FST
            (case_dir / "case.fst").write_text(base_fst_text)

            # InflowWind.dat (HH=59m + BTS パス)
            (case_dir / "InflowWind.dat").write_text(make_inflow_dat(inflow_lines, tag_full))

            # template_mm82 からテンプレートファイルをコピー
            for fname in template_files:
                shutil.copy(TMPL_MM82 / fname, case_dir / fname)

            # BTS の存在チェック
            bts_exists = (WIND_MM82 / f"{tag_full}.bts").exists()
            if not bts_exists:
                skipped += 1

            generated.append(tag_full)

print(f"Generated {len(generated)} OpenFAST case directories: {CASES_MM82}")
print(f"  BTS 欠落: {skipped}/{len(generated)}")
if skipped > 0:
    print("  ※ TurbSim を先に実行してください: mm82_02_run_turbsim.py")
