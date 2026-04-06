"""
01_generate_turbsim_inputs.py
Phase 5b: TurbSim入力ファイルを40ケース分生成する
V = [4, 6, 8, 10, 12, 14, 16, 18] m/s
TI = [0.08, 0.12, 0.14, 0.16, 0.20]
"""

import re
from pathlib import Path

# パス設定
SCRIPT_DIR   = Path(__file__).parent
BASE_DIR     = SCRIPT_DIR.parent
TEMPLATE_INP = BASE_DIR.parent / "r-test/glue-codes/openfast/5MW_Baseline/Wind/90m_12mps_twr.inp"
WIND_DIR     = BASE_DIR / "wind"
WIND_DIR.mkdir(exist_ok=True)

V_LIST  = [4, 6, 8, 10, 12, 14, 16, 18]
TI_LIST = [0.08, 0.12, 0.14, 0.16, 0.20]

template_lines = TEMPLATE_INP.read_text().splitlines()

# TurbSim入力ファイルのパラメータ行を正確に識別するユーティリティ
# 書式: [spaces][value][spaces][ParamName][spaces]-[description]
# valueは数値、引用符付き文字列、True/Falseなど
def get_param_name(line):
    """行のパラメータ名（2トークン目）を返す。コメント・ヘッダ行はNone。"""
    stripped = line.strip()
    if not stripped or stripped.startswith('!') or stripped.startswith('-') or stripped.startswith('='):
        return None
    tokens = stripped.split()
    if len(tokens) < 2:
        return None
    return tokens[1]

def modify_turbsim_inp(lines, V, TI, seed):
    """テンプレート行リストを受け取り、V/TI/seed を上書きして返す"""
    # AnalysisTime: V=4 m/s のとき GridWidth(145m)/V = 36s → 660s で十分
    analysis_time = max(660, int(600 + 145 / V) + 10)
    usable_time   = 600
    ti_val        = TI * 100  # 8.0, 12.0, etc.

    result = []
    for line in lines:
        param = get_param_name(line)

        if param == "RandSeed1":
            result.append(f"   {seed:8d}   RandSeed1       - First random seed  (-2147483648 to 2147483647)")
        elif param == "WrADTWR":
            result.append("False         WrADTWR         - Output tower time-series data? (Generates RootName.twr)")
        elif param == "AnalysisTime":
            result.append(f"   {analysis_time:8d}   AnalysisTime    - Length of analysis time series [seconds]")
        elif param == "UsableTime":
            result.append(f"   {usable_time:8d}   UsableTime      - Usable length of output time series [seconds]")
        elif param == "IECturbc":
            result.append(f'"{ti_val:.1f}"         IECturbc        - IEC turbulence characteristic (turbulence intensity in percent)')
        elif param == "URef":
            result.append(f"      {V:6.1f}   URef            - Mean (total) velocity at the reference height [m/s]")
        else:
            result.append(line)
    return "\n".join(result) + "\n"


generated = []
for vi, V in enumerate(V_LIST):
    for ti_i, TI in enumerate(TI_LIST):
        case_tag = f"V{V:02d}_TI{int(TI * 100):03d}"
        seed = (vi * len(TI_LIST) + ti_i) * 1000 + 42

        modified = modify_turbsim_inp(template_lines, V, TI, seed)

        out_path = WIND_DIR / f"{case_tag}.inp"
        out_path.write_text(modified)
        generated.append((case_tag, V, TI, seed))

print(f"Generated {len(generated)} TurbSim input files in: {WIND_DIR}")
for tag, V, TI, seed in generated:
    print(f"  {tag}  V={V:2d} m/s  TI={TI:.2f}  seed={seed}")
