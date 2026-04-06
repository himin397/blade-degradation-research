"""
mm82_01_gen_turbsim.py
Phase I MM82: TurbSim 入力ファイル生成 (HH=59m, 240ケース)

NREL 5MW テンプレート (HH=90m) を MM82 用 (HH=59m) に変更:
  HubHt:       90  → 59 m
  GridHeight:  145 → 100 m  (D=82m をカバー、±50m)
  GridWidth:   145 → 100 m
  RefHt:        90 → 59 m

V × TI × Seed = 8 × 5 × 6 = 240 ケース
出力先: wind_mm82/{case_tag}_S{seed}.inp
"""

from pathlib import Path

SCRIPT_DIR   = Path(__file__).parent
BASE_DIR     = SCRIPT_DIR.parent
TEMPLATE_INP = BASE_DIR.parent / "r-test/glue-codes/openfast/5MW_Baseline/Wind/90m_12mps_twr.inp"
WIND_MM82    = BASE_DIR / "wind_mm82"
WIND_MM82.mkdir(exist_ok=True)

V_LIST   = [4, 6, 8, 10, 12, 14, 16, 18]
TI_LIST  = [0.08, 0.12, 0.14, 0.16, 0.20]
N_SEEDS  = 6

HUB_HT      = 59      # m  (MM82 ハブ高さ)
GRID_SIZE   = 100     # m  (グリッド高さ・幅: D=82m + マージン)

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
    ti_val        = TI * 100   # パーセント表記

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
        elif param == "HubHt":
            result.append(f"   {HUB_HT:8d}   HubHt           - Hub height [m] (should be > 0.5*GridHeight)")
        elif param == "GridHeight":
            result.append(f"   {GRID_SIZE:8d}   GridHeight      - Grid height [m]")
        elif param == "GridWidth":
            result.append(f"   {GRID_SIZE:8d}   GridWidth       - Grid width [m] (should be >= 2*(RotorRadius+ShaftLength))")
        elif param == "RefHt":
            result.append(f"   {HUB_HT:8d}   RefHt           - Height of the reference velocity (URef) [m]")
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
        base_seed = (vi * len(TI_LIST) + ti_i) * 100000 + 20000   # MM82 専用シード空間
        for s in range(N_SEEDS):
            seed     = base_seed + s * 1000 + 3
            tag_full = f"{case_tag}_S{s+1:02d}"
            modified = modify_turbsim_inp(template_lines, V, TI, seed)
            out_path = WIND_MM82 / f"{tag_full}.inp"
            out_path.write_text(modified)
            generated.append((tag_full, V, TI, seed))

print(f"Generated {len(generated)} TurbSim input files in: {WIND_MM82}")
print(f"  ({len(V_LIST)} V × {len(TI_LIST)} TI × {N_SEEDS} seeds = {len(generated)} cases)")
print(f"  HubHt={HUB_HT}m, GridSize={GRID_SIZE}×{GRID_SIZE}m")
