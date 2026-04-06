"""
dlc21_01_gen_cases.py
DLC 2.1: グリッド喪失 → 緊急停止 (Emergency Stop) ケース生成

IEC 61400-1:3 DLC 2.1
  - 風況: NTM（Phase I と同じ BTS ファイルを再利用）
  - フォルト: t=300s にグリッド喪失
    → 発電機遮断 (TimGenOf=300s)
    → ブレード緊急ピッチ (TPitManS=300s, PitManRat=8 deg/s, BlPitchF=90 deg)
    → HSS ブレーキ展開 (THSSBrDp=300s)
  - 評価: ピーク荷重（DEL ではなく最大値）

条件: V=[8,10,12,14,16,18] m/s × TI=[0.14] × 6 seeds = 36 ケース
出力: cases_dlc21/{tag}/

前提: wind_mm82/ に対象 BTS が存在すること（Phase I で生成済み）
"""

import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
BASE_DIR   = SCRIPT_DIR.parent
TEMPLATE   = BASE_DIR / "template_mm82"
WIND_MM82  = BASE_DIR / "wind_mm82"
CASES_DLC21 = BASE_DIR / "cases_dlc21"

CASES_DLC21.mkdir(exist_ok=True)

V_LIST  = [8, 10, 12, 14, 16, 18]
TI_LIST = [0.14]
N_SEEDS = 6

# フォルト設定
T_FAULT        = 300.0   # グリッド喪失時刻 [s]
PIT_MAN_RATE   = 8.0     # 緊急ピッチ速度 [deg/s]
BLADE_PITCH_F  = 90.0    # フェザー角 [deg]
# MM82 HSS ブレーキトルク: NREL 5MW 28116N-m × (2.05/5) × (105/97) × (122.9/188) ≈ 8154 N-m
HSS_BR_TQ      = 8154.0  # N-m
HSS_BR_DT      = 0.6     # ブレーキ展開時間 [s]

# ── InflowWind テンプレート ────────────────────────────────────────────────────
inflow_tmpl = (BASE_DIR / "cases_mm82" / "V08_TI014_S01" / "InflowWind.dat").read_text()

def make_inflow(tag_full):
    lines = []
    for line in inflow_tmpl.splitlines():
        if "FileName_BTS" in line:
            bts = f"../../wind_mm82/{tag_full}.bts"
            lines.append(f'"{bts}"    FileName_BTS   - Name of the Full field wind file to use (.bts)')
        elif "WindVziList" in line:
            lines.append("         59   WindVziList    - List of heights (m)")
        else:
            lines.append(line)
    return "\n".join(lines) + "\n"

# ── ServoDyn: フォルトトリガー付き ────────────────────────────────────────────
servodyn_tmpl = (TEMPLATE / "ServoDyn.dat").read_text()

def make_servodyn_fault():
    replacements = {
        "9999.9   TPitManS(1)": f"{T_FAULT:.1f}   TPitManS(1)",
        "9999.9   TPitManS(2)": f"{T_FAULT:.1f}   TPitManS(2)",
        "9999.9   TPitManS(3)": f"{T_FAULT:.1f}   TPitManS(3)",
        "2   PitManRat(1)": f"{PIT_MAN_RATE:.1f}   PitManRat(1)",
        "2   PitManRat(2)": f"{PIT_MAN_RATE:.1f}   PitManRat(2)",
        "2   PitManRat(3)": f"{PIT_MAN_RATE:.1f}   PitManRat(3)",
        "0   BlPitchF(1)": f"{BLADE_PITCH_F:.1f}   BlPitchF(1)",
        "0   BlPitchF(2)": f"{BLADE_PITCH_F:.1f}   BlPitchF(2)",
        "0   BlPitchF(3)": f"{BLADE_PITCH_F:.1f}   BlPitchF(3)",
        "9999.9   TimGenOf": f"{T_FAULT:.1f}   TimGenOf",
        "0   HSSBrMode": f"1   HSSBrMode",
        "9999.9   THSSBrDp": f"{T_FAULT:.1f}   THSSBrDp",
        "28116.2   HSSBrTqF": f"{HSS_BR_TQ:.1f}   HSSBrTqF",
    }
    text = servodyn_tmpl
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

servodyn_fault = make_servodyn_fault()

# ── FST テンプレート ──────────────────────────────────────────────────────────
fst_tmpl = (BASE_DIR / "cases_mm82" / "V08_TI014_S01" / "case.fst").read_text()

# ── ケース生成 ────────────────────────────────────────────────────────────────
generated = []
missing_bts = []

for V in V_LIST:
    for TI in TI_LIST:
        for s in range(1, N_SEEDS + 1):
            tag_full = f"V{V:02d}_TI{int(TI*100):03d}_S{s:02d}"
            bts_path = WIND_MM82 / f"{tag_full}.bts"

            if not bts_path.exists() or bts_path.stat().st_size == 0:
                missing_bts.append(tag_full)
                continue

            case_dir = CASES_DLC21 / tag_full
            case_dir.mkdir(exist_ok=True)

            # FST: TMax=660s (t_fault=300 + 余裕360s)
            fst_text = fst_tmpl
            # .outb ファイルは同じ case.outb
            (case_dir / "case.fst").write_text(fst_text)

            # InflowWind
            (case_dir / "InflowWind.dat").write_text(make_inflow(tag_full))

            # ServoDyn（フォルト付き）
            (case_dir / "ServoDyn.dat").write_text(servodyn_fault)

            # その他テンプレートファイルをコピー
            for fname in ["ElastoDyn.dat", "AeroDyn.dat", "DISCON.IN",
                          "Cp_Ct_Cq.NREL5MW.txt", "MM82_Blade.dat",
                          "MM82_Tower.dat", "MM82_AeroDyn_blade.dat"]:
                src = TEMPLATE / fname
                if src.exists():
                    shutil.copy(src, case_dir / fname)

            generated.append(tag_full)

print(f"DLC 2.1 ケース生成: {len(generated)} ケース → {CASES_DLC21}")
if missing_bts:
    print(f"BTS なし（スキップ）: {len(missing_bts)} ケース")
    for t in missing_bts[:5]:
        print(f"  {t}")
print("\nフォルト設定:")
print(f"  t_fault      = {T_FAULT} s")
print(f"  PitManRat    = {PIT_MAN_RATE} deg/s")
print(f"  BlPitchF     = {BLADE_PITCH_F} deg")
print(f"  TimGenOf     = {T_FAULT} s")
print(f"  THSSBrDp     = {T_FAULT} s")
print(f"  HSSBrTqF     = {HSS_BR_TQ} N-m")
