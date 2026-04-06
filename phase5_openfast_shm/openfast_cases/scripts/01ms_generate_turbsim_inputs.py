"""
01ms_generate_turbsim_inputs.py
Phase 5b マルチシード: TurbSim入力ファイルを 40条件×6シード=240ケース分生成する
出力先: wind_ms/{case_tag}_S{seed_idx:02d}.inp

IEC 61400-1推奨: 各V-TI条件につき6種子以上のDEL平均を使用
"""

from pathlib import Path

SCRIPT_DIR   = Path(__file__).parent
BASE_DIR     = SCRIPT_DIR.parent
TEMPLATE_INP = BASE_DIR.parent / "r-test/glue-codes/openfast/5MW_Baseline/Wind/90m_12mps_twr.inp"
WIND_MS_DIR  = BASE_DIR / "wind_ms"
WIND_MS_DIR.mkdir(exist_ok=True)

V_LIST    = [4, 6, 8, 10, 12, 14, 16, 18]
TI_LIST   = [0.08, 0.12, 0.14, 0.16, 0.20]
N_SEEDS   = 6

template_lines = TEMPLATE_INP.read_text().splitlines()


def get_param_name(line):
    stripped = line.strip()
    if not stripped or stripped.startswith('!') or stripped.startswith('-') or stripped.startswith('='):
        return None
    tokens = stripped.split()
    if len(tokens) < 2:
        return None
    return tokens[1]


def modify_turbsim_inp(lines, V, TI, seed):
    analysis_time = max(660, int(600 + 145 / V) + 10)
    usable_time   = 600
    ti_val        = TI * 100

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
        case_tag  = f"V{V:02d}_TI{int(TI * 100):03d}"
        # シードは条件ごとに独立したブロックを確保（既存単一シードとは異なる空間）
        base_seed = (vi * len(TI_LIST) + ti_i) * 100000 + 10000
        for s in range(N_SEEDS):
            seed     = base_seed + s * 1000 + 7
            tag_full = f"{case_tag}_S{s+1:02d}"
            modified = modify_turbsim_inp(template_lines, V, TI, seed)
            out_path = WIND_MS_DIR / f"{tag_full}.inp"
            out_path.write_text(modified)
            generated.append((tag_full, V, TI, seed))

print(f"Generated {len(generated)} TurbSim input files in: {WIND_MS_DIR}")
print(f"  ({len(V_LIST)} V × {len(TI_LIST)} TI × {N_SEEDS} seeds = {len(generated)} cases)")
