"""
dlc22_01_gen_cases.py
DLC 2.2: ピッチ固着（Pitch Seizure） → 非対称緊急停止 ケース生成

IEC 61400-1:3 DLC 2.2
  - 風況: NTM（DLC 2.1 と同一 BTS 再利用）
  - フォルト: t=300s にグリッド喪失
    → Blade 1: ピッチ固着（TPitManS=9999.9 → 動かない）
    → Blade 2/3: 正常緊急ピッチ（8 deg/s → 90°）
    → 発電機遮断 (TimGenOf=300s)
    → HSS ブレーキ展開 (THSSBrDp=300s)
  - 評価: ピーク荷重（DLC 2.1 との比較で非対称荷重の増大を確認）

条件: V=[8,10,12,14,16,18] m/s × TI=[0.14] × 6 seeds = 36 ケース
出力: cases_dlc22/{tag}/
"""

import shutil
from pathlib import Path

SCRIPT_DIR  = Path(__file__).parent
BASE_DIR    = SCRIPT_DIR.parent
TEMPLATE    = BASE_DIR / "template_mm82"
WIND_MM82   = BASE_DIR / "wind_mm82"
CASES_DLC22 = BASE_DIR / "cases_dlc22"
CASES_DLC21 = BASE_DIR / "cases_dlc21"  # InflowWind / FST 参照元

CASES_DLC22.mkdir(exist_ok=True)

V_LIST  = [8, 10, 12, 14, 16, 18]
TI_LIST = [0.14]
N_SEEDS = 6

T_FAULT       = 300.0
PIT_MAN_RATE  = 8.0
BLADE_PITCH_F = 90.0
HSS_BR_TQ     = 8154.0
HSS_BR_DT     = 0.6

# ── ServoDyn: Blade1 固着・Blade2/3 正常緊急ピッチ ───────────────────────────
servodyn_tmpl = (TEMPLATE / "ServoDyn.dat").read_text()

def make_servodyn_seizure():
    """Blade 1 のみピッチ固着（TPitManS=9999.9 のまま）、Blade 2/3 は正常緊急ピッチ"""
    replacements = {
        # Blade 1: 固着（9999.9 のまま → 変更しない）
        # Blade 2/3: 緊急ピッチ
        "9999.9   TPitManS(2)": f"{T_FAULT:.1f}   TPitManS(2)",
        "9999.9   TPitManS(3)": f"{T_FAULT:.1f}   TPitManS(3)",
        "2   PitManRat(1)": f"{PIT_MAN_RATE:.1f}   PitManRat(1)",
        "2   PitManRat(2)": f"{PIT_MAN_RATE:.1f}   PitManRat(2)",
        "2   PitManRat(3)": f"{PIT_MAN_RATE:.1f}   PitManRat(3)",
        # Blade 1 の最終ピッチ: 固着なので現在角のまま（0° = fine pitch ≈ 定常運転角）
        # Blade 2/3: フェザー
        "0   BlPitchF(2)": f"{BLADE_PITCH_F:.1f}   BlPitchF(2)",
        "0   BlPitchF(3)": f"{BLADE_PITCH_F:.1f}   BlPitchF(3)",
        # 発電機・ブレーキ
        "9999.9   TimGenOf": f"{T_FAULT:.1f}   TimGenOf",
        "0   HSSBrMode": f"1   HSSBrMode",
        "9999.9   THSSBrDp": f"{T_FAULT:.1f}   THSSBrDp",
        "28116.2   HSSBrTqF": f"{HSS_BR_TQ:.1f}   HSSBrTqF",
    }
    text = servodyn_tmpl
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

servodyn_seizure = make_servodyn_seizure()

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

            case_dir = CASES_DLC22 / tag_full
            case_dir.mkdir(exist_ok=True)

            # FST: DLC 2.1 から流用（TMax=600s）
            src_fst = CASES_DLC21 / tag_full / "case.fst"
            if src_fst.exists():
                shutil.copy(src_fst, case_dir / "case.fst")

            # InflowWind: DLC 2.1 から流用（BTS パス同じ）
            src_inflow = CASES_DLC21 / tag_full / "InflowWind.dat"
            if src_inflow.exists():
                shutil.copy(src_inflow, case_dir / "InflowWind.dat")

            # ServoDyn: ピッチ固着設定
            (case_dir / "ServoDyn.dat").write_text(servodyn_seizure)

            # その他テンプレート
            for fname in ["ElastoDyn.dat", "AeroDyn.dat", "DISCON.IN",
                          "Cp_Ct_Cq.NREL5MW.txt", "MM82_Blade.dat",
                          "MM82_Tower.dat", "MM82_AeroDyn_blade.dat"]:
                src = TEMPLATE / fname
                if src.exists():
                    shutil.copy(src, case_dir / fname)

            generated.append(tag_full)

print(f"DLC 2.2 ケース生成: {len(generated)} ケース → {CASES_DLC22}")
if missing_bts:
    print(f"BTS なし（スキップ）: {len(missing_bts)}")

print("\nフォルト設定（ピッチ固着）:")
print(f"  Blade 1: 固着（ピッチ変化なし）")
print(f"  Blade 2/3: 緊急ピッチ {PIT_MAN_RATE} deg/s → {BLADE_PITCH_F}°")
print(f"  TimGenOf = {T_FAULT} s")
print(f"  THSSBrDp = {T_FAULT} s / HSSBrTqF = {HSS_BR_TQ} N-m")
