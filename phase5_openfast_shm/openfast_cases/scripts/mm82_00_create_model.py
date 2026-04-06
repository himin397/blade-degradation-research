"""
mm82_00_create_model.py
Phase I: Senvion MM82 スケーリング済み OpenFAST モデル生成

NREL 5MW → MM82 幾何スケーリング:
  λ_R = 41/63 = 0.6508  (ブレード/ロータ)
  λ_H = 59/87.6 = 0.6735 (タワー/ハブ高さ)

  ブレード構造:
    BMassDen × λ_R^2.3 (経験的ブレード質量スケーリング)
    FlpStff, EdgStff × λ_R^4 (曲げ剛性: 断面二次モーメント ∝ R^4)
  タワー構造:
    TMassDen × λ_H^2 (断面積スケーリング)
    TwFAStif, TwSSStif × λ_H^4 (断面二次モーメントスケーリング)

出力: openfast_cases/template_mm82/
  MM82_Blade.dat, MM82_Tower.dat
  ElastoDyn.dat, AeroDyn.dat, MM82_AeroDyn_blade.dat
  DISCON.IN, ServoDyn.dat, Cp_Ct_Cq.NREL5MW.txt

注意: モードシェイプ多項式係数は非次元形状を記述するため変更なし。
      NREL 5MW 翼型データをプロキシとして使用（実Senvion翼型非公開のため）。
"""

import math
import re
import shutil
from pathlib import Path

# ── パス定義 ──────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
BASE_DIR     = SCRIPT_DIR.parent
RTEST_DIR    = BASE_DIR.parent / "r-test/glue-codes/openfast"
BASELINE_DIR = RTEST_DIR / "5MW_Baseline"
LAND_DIR     = RTEST_DIR / "5MW_Land_DLL_WTurb"
TMPL5MW      = BASE_DIR / "template"
TMPL_MM82    = BASE_DIR / "template_mm82"
TMPL_MM82.mkdir(exist_ok=True)

# ── スケーリング係数 ───────────────────────────────────────────────────────────
R_NREL  = 63.0
R_MM82  = 41.0
H_NREL  = 87.6
H_MM82  = 59.0
GB_NREL = 97.0
GB_MM82 = 105.0

LAM_R = R_MM82 / R_NREL        # ≈ 0.6508
LAM_H = H_MM82 / H_NREL        # ≈ 0.6735

SCALE_MASS  = LAM_R ** 2.3     # ≈ 0.3726  (BMassDen)
SCALE_STIFF = LAM_R ** 4       # ≈ 0.1793  (FlpStff, EdgStff)
SCALE_TMASS = LAM_H ** 2       # ≈ 0.4536  (TMassDen)
SCALE_TSTIF = LAM_H ** 4       # ≈ 0.2058  (TwFAStif, TwSSStif)

print("=== Phase I: Senvion MM82 OpenFAST モデル生成 ===")
print(f"  λ_R = {LAM_R:.4f}  (R={R_NREL}m → {R_MM82}m)")
print(f"  λ_H = {LAM_H:.4f}  (H={H_NREL}m → {H_MM82}m)")
print(f"  BMassDen scale: ×{SCALE_MASS:.4f}")
print(f"  FlpStff/EdgStff scale: ×{SCALE_STIFF:.4f}")
print(f"  TMassDen scale: ×{SCALE_TMASS:.4f}")
print(f"  TwFAStif/TwSSStif scale: ×{SCALE_TSTIF:.4f}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. ブレード構造ファイル: MM82_Blade.dat
# ─────────────────────────────────────────────────────────────────────────────
def scale_blade_file():
    src = BASELINE_DIR / "NRELOffshrBsline5MW_Blade.dat"
    dst = TMPL_MM82 / "MM82_Blade.dat"

    lines = src.read_text(encoding="utf-8").splitlines()

    # 数値データ行を検出 (BlFract PitchAxis StrcTwst BMassDen FlpStff EdgStff)
    # 先頭がE表記の浮動小数点で始まる6列の行を対象とする
    float_re = re.compile(
        r"^\s*([\dE+\-\.]+)\s+([\dE+\-\.]+)\s+([\dE+\-\.]+)\s+"
        r"([\dE+\-\.]+)\s+([\dE+\-\.]+)\s+([\dE+\-\.]+)\s*$",
        re.IGNORECASE,
    )

    out_lines = []
    data_count = 0
    for line in lines:
        m = float_re.match(line)
        if m:
            bf   = float(m.group(1))   # BlFract      (変更なし)
            pa   = float(m.group(2))   # PitchAxis    (変更なし)
            st   = float(m.group(3))   # StrcTwst     (変更なし)
            bmd  = float(m.group(4))   # BMassDen     (× λ_R^2.3)
            flp  = float(m.group(5))   # FlpStff      (× λ_R^4)
            edg  = float(m.group(6))   # EdgStff      (× λ_R^4)

            bmd_new = bmd * SCALE_MASS
            flp_new = flp * SCALE_STIFF
            edg_new = edg * SCALE_STIFF

            out_lines.append(
                f"{bf:.7E}  {pa:.7E}  {st:.7E}  "
                f"{bmd_new:.7E}  {flp_new:.7E}  {edg_new:.7E}"
            )
            data_count += 1
        else:
            # ヘッダー・コメント行: タイトルを更新
            if "NREL 5.0 MW" in line:
                out_lines.append(line.replace("NREL 5.0 MW", "Senvion MM82 (NREL 5MW scaled proxy)"))
            else:
                out_lines.append(line)

    dst.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"\n[1] MM82_Blade.dat 作成完了 (data rows={data_count})")
    print(f"    保存先: {dst}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. タワー構造ファイル: MM82_Tower.dat
# ─────────────────────────────────────────────────────────────────────────────
def scale_tower_file():
    src = LAND_DIR / "NRELOffshrBsline5MW_Onshore_ElastoDyn_Tower.dat"
    dst = TMPL_MM82 / "MM82_Tower.dat"

    lines = src.read_text(encoding="utf-8").splitlines()

    # HtFract TMassDen TwFAStif TwSSStif の4列行を検出
    float_re = re.compile(
        r"^\s*([\dE+\-\.]+)\s+([\dE+\-\.]+)\s+([\dE+\-\.]+)\s+([\dE+\-\.]+)\s*$",
        re.IGNORECASE,
    )

    out_lines = []
    data_count = 0
    for line in lines:
        m = float_re.match(line)
        if m:
            hf   = float(m.group(1))   # HtFract      (変更なし)
            tmd  = float(m.group(2))   # TMassDen     (× λ_H^2)
            tfa  = float(m.group(3))   # TwFAStif     (× λ_H^4)
            tss  = float(m.group(4))   # TwSSStif     (× λ_H^4)

            tmd_new = tmd * SCALE_TMASS
            tfa_new = tfa * SCALE_TSTIF
            tss_new = tss * SCALE_TSTIF

            out_lines.append(
                f"{hf:.7E}  {tmd_new:.7E}  {tfa_new:.7E}  {tss_new:.7E}  "
            )
            data_count += 1
        else:
            if "NREL 5.0 MW" in line:
                out_lines.append(line.replace("NREL 5.0 MW", "Senvion MM82 (NREL 5MW scaled proxy)"))
            else:
                out_lines.append(line)

    dst.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"\n[2] MM82_Tower.dat 作成完了 (data rows={data_count})")
    print(f"    保存先: {dst}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. AeroDyn ブレードファイル: MM82_AeroDyn_blade.dat
# ─────────────────────────────────────────────────────────────────────────────
def scale_aerodyn_blade():
    src = BASELINE_DIR / "NRELOffshrBsline5MW_AeroDyn_blade.dat"
    dst = TMPL_MM82 / "MM82_AeroDyn_blade.dat"

    lines = src.read_text(encoding="utf-8").splitlines()

    # BlSpn BlCrvAC BlSwpAC BlCrvAng BlTwist BlChord BlAFID BlCb BlCenBn BlCenBt
    # (m)   (m)     (m)     (deg)    (deg)   (m)     (-)    (-) (m)     (m)
    # 10列: 先頭3列(m) × λ_R, 列4(deg) 変更なし, 列5(deg) 変更なし,
    #       列6(m) × λ_R, 列7-10 変更なし
    float_10_re = re.compile(
        r"^\s*([\dE+\-\.]+)"    # BlSpn
        r"\s+([\dE+\-\.]+)"    # BlCrvAC
        r"\s+([\dE+\-\.]+)"    # BlSwpAC
        r"\s+([\dE+\-\.]+)"    # BlCrvAng
        r"\s+([\dE+\-\.]+)"    # BlTwist
        r"\s+([\dE+\-\.]+)"    # BlChord
        r"\s+(\d+)"            # BlAFID (integer)
        r"\s+([\dE+\-\.]+)"    # BlCb
        r"\s+([\dE+\-\.]+)"    # BlCenBn
        r"\s+([\dE+\-\.]+)"   # BlCenBt
        r"\s*$",
        re.IGNORECASE,
    )

    out_lines = []
    data_count = 0
    for line in lines:
        m = float_10_re.match(line)
        if m:
            blspn   = float(m.group(1))  * LAM_R
            blcrv   = float(m.group(2))  * LAM_R
            blswp   = float(m.group(3))  * LAM_R
            blcrvang= float(m.group(4))             # deg: 変更なし
            bltwist = float(m.group(5))             # deg: 変更なし
            blchord = float(m.group(6))  * LAM_R
            blafid  = int(m.group(7))               # integer
            blcb    = float(m.group(8))
            blcenbn = float(m.group(9))
            blcentbt= float(m.group(10))

            out_lines.append(
                f"{blspn:.7E}  {blcrv:.7E}  {blswp:.7E}  "
                f"{blcrvang:.7E}  {bltwist:.7E}  {blchord:.7E}  "
                f"      {blafid}      {blcb:.1f}      {blcenbn:.1f}       {blcentbt:.1f}"
            )
            data_count += 1
        else:
            if "NREL 5.0 MW" in line:
                out_lines.append(line.replace("NREL 5.0 MW", "Senvion MM82 (NREL 5MW scaled proxy)"))
            else:
                out_lines.append(line)

    dst.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"\n[3] MM82_AeroDyn_blade.dat 作成完了 (data rows={data_count})")
    print(f"    保存先: {dst}")


# ─────────────────────────────────────────────────────────────────────────────
# 4. ElastoDyn.dat (MM82 パラメータ更新)
# ─────────────────────────────────────────────────────────────────────────────
def create_elastodyn():
    src  = TMPL5MW / "ElastoDyn.dat"
    dst  = TMPL_MM82 / "ElastoDyn.dat"
    text = src.read_text(encoding="utf-8")

    # MM82 質量・慣性パラメータ
    # HubMass: 56780 → 14000 kg (Senvion MM82 実測値)
    # HubIner: 115926 → 12100 kg·m² (R^5 スケーリング近似)
    # GenIner: 534.116 → 290 kg·m² (P^(2/3) スケーリング)
    # NacMass: 240000 → 65000 kg (Senvion MM82 仕様)
    # NacYIner: 2607890 → 300000 kg·m² (NacMass × R^2 スケーリング)
    hub_mass  = 14000
    hub_iner  = int(115926 * (R_MM82/R_NREL)**5)           # ≈ 13527 → 13500
    gen_iner  = 290.0
    nac_mass  = 65000
    nac_yiner = int(2607890 * (nac_mass/240000) * LAM_R**2)  # ≈ 299000 → 299000

    # OverHang (R スケール), ShftGagL (R スケール), Twr2Shft (R スケール)
    overhang  = -5.0191 * LAM_R   # ≈ -3.268
    shftgagl  =  1.912  * LAM_R   # ≈  1.245
    nacmx     =  1.9    * LAM_R   # ≈  1.237
    nacmz     =  1.75   * LAM_R   # ≈  1.139
    ncimux    = -3.09528* LAM_R   # ≈ -2.015
    ncimuz    =  2.23336* LAM_R   # ≈  1.454
    twr2shft  =  1.96256* LAM_R   # ≈  1.278
    dttor_spr = 8.67637e8 * SCALE_STIFF   # ≈ 1.556E+08
    dttor_dmp = 6.215e6   * SCALE_STIFF   # ≈ 1.114E+06

    # 置換マッピング: (古い値文字列, 新しい値文字列, パラメータ名)
    replacements = [
        # TURBINE CONFIGURATION
        (r"^\s*63\s+(TipRad)",    f"         {R_MM82}   TipRad"),
        (r"^\s*1\.5\s+(HubRad)",  f"       {R_MM82*1.5/R_NREL:.2f}   HubRad"),
        (r"^\s*12\.1\s+(RotSpeed)", f"       {17.1}   RotSpeed"),
        (r"^\s*87\.6\s+(TowerHt)", f"       {H_MM82}   TowerHt"),
        (r"^\s*-5\.0191\s+(OverHang)", f"    {overhang:.4f}   OverHang"),
        (r"^\s*1\.912\s+(ShftGagL)", f"      {shftgagl:.3f}   ShftGagL"),
        (r"^\s*1\.9\s+(NacCMxn)", f"        {nacmx:.3f}   NacCMxn"),
        (r"^\s*1\.75\s+(NacCMzn)", f"       {nacmz:.3f}   NacCMzn"),
        (r"^\s*-3\.09528\s+(NcIMUxn)", f"   {ncimux:.4f}   NcIMUxn"),
        (r"^\s*2\.23336\s+(NcIMUzn)", f"    {ncimuz:.4f}   NcIMUzn"),
        (r"^\s*1\.96256\s+(Twr2Shft)", f"   {twr2shft:.4f}   Twr2Shft"),
        # MASS AND INERTIA
        (r"^\s*56780\s+(HubMass)",    f"      {hub_mass}   HubMass"),
        (r"^\s*115926\s+(HubIner)",   f"     {hub_iner}   HubIner"),
        (r"^\s*534\.116\s+(GenIner)", f"    {gen_iner}   GenIner"),
        (r"^\s*240000\s+(NacMass)",   f"      {nac_mass}   NacMass"),
        (r"^\s*2\.60789E\+06\s+(NacYIner)", f"{nac_yiner:.5E}   NacYIner"),
        # DRIVETRAIN
        (r"^\s*97\s+(GBRatio)",       f"        {int(GB_MM82)}   GBRatio"),
        (r"^\s*8\.67637E\+08\s+(DTTorSpr)", f"{dttor_spr:.5E}   DTTorSpr"),
        (r"^\s*6\.215E\+06\s+(DTTorDmp)",   f"  {dttor_dmp:.3E}   DTTorDmp"),
    ]

    lines = text.splitlines()
    out_lines = []
    for line in lines:
        replaced = False
        for pattern, new_prefix in replacements:
            m = re.match(pattern, line, re.IGNORECASE)
            if m:
                # パラメータ名以降（コメント含む）を保持
                param_name = m.group(1)
                # 元の行のパラメータ名以降を切り出す
                idx = line.find(param_name)
                suffix = line[idx:]
                out_lines.append(f"    {new_prefix}      {suffix}" if False else f"{new_prefix}      {suffix}")
                replaced = True
                break
        if not replaced:
            out_lines.append(line)

    # BldFile パスを template_mm82 相対パスに更新
    # cases_mm82/V04.../  からの相対パス: ../../template_mm82/MM82_Blade.dat
    new_text = "\n".join(out_lines)
    new_text = re.sub(
        r'"[^"]*NRELOffshrBsline5MW_Blade\.dat"(\s+BldFile)',
        r'"MM82_Blade.dat"\1',
        new_text,
    )
    # TwrFile を MM82_Tower.dat に更新
    new_text = re.sub(
        r'"[^"]*NRELOffshrBsline5MW_Onshore_ElastoDyn_Tower\.dat"(\s+TwrFile)',
        r'"MM82_Tower.dat"\1',
        new_text,
    )

    dst.write_text(new_text, encoding="utf-8")
    print(f"\n[4] ElastoDyn.dat 作成完了")
    print(f"    保存先: {dst}")


# ─────────────────────────────────────────────────────────────────────────────
# 5. AeroDyn.dat (ADBlFile パス更新)
# ─────────────────────────────────────────────────────────────────────────────
def create_aerodyn():
    src  = TMPL5MW / "AeroDyn.dat"
    dst  = TMPL_MM82 / "AeroDyn.dat"
    text = src.read_text(encoding="utf-8")

    # ADBlFile パスを MM82 ブレードファイルに変更
    text = re.sub(
        r'"[^"]*NRELOffshrBsline5MW_AeroDyn_blade\.dat"(\s+ADBlFile)',
        r'"MM82_AeroDyn_blade.dat"\1',
        text,
    )

    dst.write_text(text, encoding="utf-8")
    print(f"\n[5] AeroDyn.dat 作成完了")
    print(f"    保存先: {dst}")


# ─────────────────────────────────────────────────────────────────────────────
# 6. DISCON.IN (MM82 定格条件更新)
# ─────────────────────────────────────────────────────────────────────────────
def create_discon():
    src  = TMPL5MW / "DISCON.IN"
    dst  = TMPL_MM82 / "DISCON.IN"
    text = src.read_text(encoding="utf-8")

    # MM82 ドライブトレイン定格値計算
    # ω_LSS_rated = 17.1 RPM
    # ω_HSS_rated = 17.1 × 105 × (2π/60)
    omega_lss_rated = 17.1 * 2 * math.pi / 60.0          # ≈ 1.7907 rad/s
    omega_hss_rated = omega_lss_rated * GB_MM82           # ≈ 187.92 rad/s

    gen_eff = 0.944
    p_rated_w = 2050000.0                                  # W (電力)
    p_mech_w  = p_rated_w / gen_eff                        # W (機械出力)
    torque_rated = p_mech_w / omega_hss_rated             # ≈ 11556 Nm (HSS)

    # Region 2 K 係数: K × ω²
    # K_MM82 = K_5MW × (R_MM82/R_NREL)^5 × (GB_NREL/GB_MM82)^3
    k_5mw  = 2.31055
    k_mm82 = k_5mw * (R_MM82/R_NREL)**5 * (GB_NREL/GB_MM82)**3

    # 最小動作速度: TSR_opt × V_cutin / R_MM82 × GB_MM82
    tsr_opt = 7.5
    v_cutin = 3.5
    omega_min_hss = tsr_opt * v_cutin / R_MM82 * GB_MM82  # ≈ 67.2 rad/s

    # 全体慣性モーメント (LSS 等価)
    # 簡易スケーリング: (R_MM82/R_NREL)^5 × (GB_MM82/GB_NREL)^-2
    j_5mw  = 43702538.05700
    j_mm82 = j_5mw * (R_MM82/R_NREL)**5 * (GB_NREL/GB_MM82)**2  # ≈ 14M

    print(f"\n[6] DISCON.IN MM82 パラメータ:")
    print(f"    ω_HSS_rated = {omega_hss_rated:.3f} rad/s")
    print(f"    VS_RtPwr    = {p_rated_w:.0f} W")
    print(f"    VS_RtTq     = {torque_rated:.1f} Nm")
    print(f"    VS_Rgn2K    = {k_mm82:.5f}")
    print(f"    VS_MinOMSpd = {omega_min_hss:.2f} rad/s")
    print(f"    WE_Jtot     = {j_mm82:.1f} kg·m²")

    # 置換テーブル: (タグ文字列, 新しい数値)
    replacements = {
        "PC_RefSpd": f"{omega_hss_rated:.10f}",
        "VS_ArSatTq": f"{torque_rated:.5e}",
        "VS_MaxRat":  f"{torque_rated * 0.9:.5e}",     # ≈ rated × 0.9
        "VS_MaxTq":   f"{torque_rated * 1.1:.5e}",     # ≈ rated × 1.1
        "VS_RtPwr":   f"{p_rated_w:.5e}",
        "VS_RtTq":    f"{torque_rated:.5e}",
        "VS_RefSpd":  f"{omega_hss_rated:.5f}",
        "VS_Rgn2K":   f"{k_mm82:.5e}",
        "VS_MinOMSpd": f"{omega_min_hss:.5f}",
        "WE_BladeRadius": f"{R_MM82:.3f}",
        "WE_GearboxRatio": f"{GB_MM82:.1f}",
        "WE_Jtot":    f"{j_mm82:.5f}",
    }

    lines = text.splitlines()
    out_lines = []
    for line in lines:
        replaced = False
        for tag, new_val in replacements.items():
            # パターン: 数値 + 空白 + "! TAG"
            pattern = rf'^(\s*)([\d.eE+\-]+)(\s+)(!\s+{re.escape(tag)}\s*)(.*)'
            m = re.match(pattern, line)
            if m:
                out_lines.append(f"{m.group(1)}{new_val}{m.group(3)}{m.group(4)}{m.group(5)}")
                replaced = True
                break
        if not replaced:
            out_lines.append(line)

    dst.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"    保存先: {dst}")


# ─────────────────────────────────────────────────────────────────────────────
# 7. ServoDyn.dat と Cp_Ct_Cq テーブルをコピー
# ─────────────────────────────────────────────────────────────────────────────
def copy_static_files():
    for fname in ["ServoDyn.dat", "Cp_Ct_Cq.NREL5MW.txt"]:
        src = TMPL5MW / fname
        dst = TMPL_MM82 / fname
        shutil.copy(src, dst)
    print(f"\n[7] ServoDyn.dat, Cp_Ct_Cq.NREL5MW.txt コピー完了")


# ─────────────────────────────────────────────────────────────────────────────
# メイン実行
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    scale_blade_file()
    scale_tower_file()
    scale_aerodyn_blade()
    create_elastodyn()
    create_aerodyn()
    create_discon()
    copy_static_files()

    print(f"\n=== 全ファイル生成完了 ===")
    print(f"出力ディレクトリ: {TMPL_MM82}")
    for f in sorted(TMPL_MM82.iterdir()):
        print(f"  {f.name}  ({f.stat().st_size:,} bytes)")
