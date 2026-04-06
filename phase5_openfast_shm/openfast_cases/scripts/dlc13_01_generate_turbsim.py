"""
dlc13_01_generate_turbsim.py
Phase 6: DLC 1.3（ETM: Extreme Turbulence Model）TurbSim入力生成

IEC 61400-1 Ed.4 式 6.3:
  σ_1 = c × I_ref × (0.072 × (Vave/c + 3) × (V/c - 4) + 10)
  c = 2 m/s

DLC 1.2 と比較するため同一8風速ビンを使用。
TI指定は不要（ETMでは IECturbc="A"/"B"/"C" を使わず ETM式で決まる）。
→ IEC_WindType = "1ETM" を使用（IEC Class 1 turbine）

出力: wind_dlc13/{V_tag}.inp, wind_dlc13/{V_tag}.bts
"""

from pathlib import Path

SCRIPT_DIR   = Path(__file__).parent
BASE_DIR     = SCRIPT_DIR.parent
TEMPLATE_INP = BASE_DIR.parent / "r-test/glue-codes/openfast/5MW_Baseline/Wind/90m_12mps_twr.inp"
WIND_DLC13   = BASE_DIR / "wind_dlc13"
WIND_DLC13.mkdir(exist_ok=True)

V_LIST  = [4, 6, 8, 10, 12, 14, 16, 18]
N_SEEDS = 6  # DLC 1.3もIEC推奨の6シード

template_lines = TEMPLATE_INP.read_text().splitlines()


def get_param_name(line):
    stripped = line.strip()
    if not stripped or stripped.startswith('!') or stripped.startswith('-') or stripped.startswith('='):
        return None
    tokens = stripped.split()
    return tokens[1] if len(tokens) >= 2 else None


def modify_turbsim_dlc13(lines, V, seed):
    """DLC 1.3（ETM）TurbSim入力生成"""
    analysis_time = max(660, int(600 + 145 / V) + 10)
    usable_time   = 600

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
            # ETMではIECturcbにTI数値ではなくクラス記号を使用
            result.append('"A"           IECturbc        - IEC turbulence characteristic (Class A for ETM)')
        elif param == "IEC_WindType":
            # 1ETM = IEC Class 1 Extreme Turbulence Model
            result.append('"1ETM"        IEC_WindType    - IEC turbulence type (1ETM = Class 1 Extreme Turbulence Model)')
        elif param == "URef":
            result.append(f"      {V:6.1f}   URef            - Mean (total) velocity at the reference height [m/s]")
        else:
            result.append(line)
    return "\n".join(result) + "\n"


generated = []
for vi, V in enumerate(V_LIST):
    base_seed = vi * 100000 + 50000
    for s in range(N_SEEDS):
        seed     = base_seed + s * 1000 + 13  # 13 = DLC 1.3
        tag_full = f"V{V:02d}_S{s+1:02d}"
        modified = modify_turbsim_dlc13(template_lines, V, seed)
        out_path = WIND_DLC13 / f"{tag_full}.inp"
        out_path.write_text(modified)
        generated.append((tag_full, V, seed))

print(f"Generated {len(generated)} DLC 1.3 TurbSim input files in: {WIND_DLC13}")
print(f"  ({len(V_LIST)} V × {N_SEEDS} seeds = {len(generated)} cases)")
