#!/usr/bin/env python3
"""PixelZen Worlds - Solo Leveling (Monitor 2): Isla de Jeju, Colmena de Hormigas y Rey Beru (Aura Farming)."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, exporta_salida, exporta_sprites_si_aplica, fbm, mix, pinta_sprite,
    render_cielo, render_estrellas, render_lago, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(709)

PALETAS = {
    'noche': dict(
        sky=['#030510', '#070b1e', '#0f1430', '#181e44', '#242656', '#332e66', '#453676', '#593e84', '#704890', '#8a549a'],
        mont=('#202238', '#141626', '#0b0c16'),
        caldera_glow='#8e2cff',
        ruin=('#1a1c2e', '#101220', '#2b2e46'),
        rock=('#2b253c', '#1b1628', '#0c0914', '#483d62'),
        grass=('#122420', '#1c3a2f', '#0a1614'),
        hive=('#38243c', '#26172a', '#150b18', '#523456'),
        cave_glow=('#b6246e', '#ff448a', '#9640ff'),
        agua='#080c1c',
        ola=('#9278d8', '#483a7c', '#1d183e'),
        shad_core='#05030a',
        shad_body='#160d2a',
        shad_hi='#36225c',
        shad_rim='#8c38ff',
        aura_outer='#1a0736',
        aura_mid='#7424f0',
        aura_hot='#d83498',
        aura_cyan='#58e8ff',
        wing=('#190b2e', '#6c34d8', '#46d8ff'),
        eye='#ff2e6c',
        vig=0.74,
        nube=['#202848', '#2e375e', '#3e4874', '#505888', '#646a9c', '#1a203e'],
    ),
    'dorado': dict(
        sky=['#14102c', '#24183e', '#3a224c', '#582c56', '#7c3858', '#a44854', '#ca5c4e', '#e87a4e', '#fa9f5a', '#ffca7c'],
        mont=('#3c243a', '#2a182c', '#1a0e1e'),
        caldera_glow='#b838d8',
        ruin=('#321e30', '#201220', '#4c2e48'),
        rock=('#442c3b', '#2d1c28', '#160d14', '#644254'),
        grass=('#1e2e20', '#2e462d', '#101a12'),
        hive=('#4c2638', '#341828', '#1c0c16', '#6e384e'),
        cave_glow=('#c42868', '#ff5490', '#9e44ff'),
        agua='#1e122c',
        ola=('#ffa284', '#8e4c72', '#3c2046'),
        shad_core='#07040e',
        shad_body='#1c1032',
        shad_hi='#422868',
        shad_rim='#a244f4',
        aura_outer='#280c44',
        aura_mid='#8830f2',
        aura_hot='#ff3c88',
        aura_cyan='#68ecff',
        wing=('#241038', '#8640dc', '#5ee4ff'),
        eye='#ff3c78',
        vig=0.80,
        nube=['#5c3054', '#7e3e62', '#a44e68', '#ca666a', '#ea8a6a', '#482444'],
    ),
    'dia': dict(
        sky=['#1e4688', '#2c5ca0', '#3e74b6', '#568eca', '#72a8da', '#90c0e6', '#aed4ee', '#c8e4f2', '#e0eef2', '#f0f4ea'],
        mont=('#485c78', '#384862', '#283448'),
        caldera_glow='#9444ea',
        ruin=('#424c62', '#2c3446', '#626e86'),
        rock=('#4e4e5e', '#363644', '#1f1f2a', '#6e6e80'),
        grass=('#20482e', '#306640', '#122a1c'),
        hive=('#543c4e', '#3c2a3a', '#241824', '#74546c'),
        cave_glow=('#b62868', '#ff4c8c', '#8e44ff'),
        agua='#1d385a',
        ola=('#bce0f4', '#688cb8', '#324c78'),
        shad_core='#080612',
        shad_body='#1a1430',
        shad_hi='#3b2c68',
        shad_rim='#8844e4',
        aura_outer='#1e1040',
        aura_mid='#7434e4',
        aura_hot='#d83892',
        aura_cyan='#58e4ff',
        wing=('#201438', '#7440d4', '#50dcff'),
        eye='#ff3270',
        vig=0.88,
        nube=['#eef4fa', '#dce8f4', '#f8fbfe', '#cfdfef', '#e6f0f8', '#c0d2e8'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

# 1. Cielo de la Isla de Jeju
render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#a844ff', '#ff4884'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#b89cff', base='#f2f4ff', sombra='#c6cce8', crater='#a0a6cc', crater_hi='#b8bee0'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffd498', centro='#fffaf0', borde='#ffb464', rayo='#ffd898'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ead8ff', '#b8e8ff', '#a298e0'])

MX, MY, MR = 148, 62, 36
CX_ASTRO = MX if FASE == 'noche' else (MX + 24 if FASE == 'dorado' else MX - 16)
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#b89cff', base='#f2f4ff', sombra='#c6cce8', crater='#a0a6cc', crater_hi='#b8bee0')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, MX + 24, 172, 22, halo='#ff9668', centro='#ffecd8', borde='#ff5e48', rayo='#ff805a')
    else:
        dibuja_sol_estandar(lz, MX - 16, 72, 22, halo='#ffe2a0', centro='#fffdf0', borde='#ffc060', rayo='#ffe098')

# 2. Nubes altas y tormentosas
NUBES_DEF = [
    (68, 26, 145, PAL['nube'][0], 2),
    (265, 38, 175, PAL['nube'][1], 3),
    (420, 24, 155, PAL['nube'][2], 2),
    (175, 106, 165, PAL['nube'][3], 3),
    (360, 96, 140, PAL['nube'][4], 2),
    (525, 208, 110, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 3. Caldera volcanica de Jeju (enmarcando a Beru en el centro) + Ruinas de la Ciudad de Jeju
rm = Ruido(731)
M0, M1, M2 = PAL['mont']
CG_CALD = PAL['caldera_glow']
R_HI, R_DK, R_RIM = PAL['ruin']
RK0, RK1, RK2, RK_HI = PAL['rock']

for x in range(W):
    # Pico de caldera volcanica centrado detras de Beru (x ~ 306) con depresion del crater
    dx_cal = abs(x - 306)
    caldera_bump = 0
    if dx_cal < 145:
        prof = 1.0 - dx_cal / 145.0
        caldera_bump = int(-42 * (prof ** 1.35))
        if dx_cal < 24:
            # Crater dentado en la cima
            caldera_bump += int(11 * (1.0 - (dx_cal / 24.0) ** 2))
    dip_r = 26 if x > 500 else 0
    ridge = int(214 + 24 * fbm(rm, x * 0.014 + 1.2) + caldera_bump + dip_r)
    ridge = max(146, min(HOR, ridge))
    for y in range(ridge, HOR + 1):
        t = (y - ridge) / max(1, HOR - ridge)
        col = mix(M0, M2, t * 0.88)
        if dx_cal < 28 and t < 0.16 and (x + y) % 5 == 0:
            col = mix(col, CG_CALD, 0.25 * (1.0 - t * 6.0))
        put(x, y, col)

# Lengua costera solida en la bahia lejana (x=24..216) para anclar los edificios en ruinas
for x in range(24, 218):
    h_coast = int(11 * math.sin((x - 24) / 194.0 * math.pi))
    for y in range(HOR - h_coast, HOR + 1):
        put(x, y, RK1 if y < HOR - 2 else RK2)

for bx, bw, bh in ((50, 15, 44), (70, 14, 62), (92, 18, 38), (122, 15, 52), (160, 16, 42)):
    base_city = HOR - 5
    top_r = base_city - bh
    for y in range(top_r, base_city + 1):
        if y < top_r + 7 and (bx + y) % 3 == 0:
            continue
        for dx in range(bw):
            c = R_RIM if dx == 0 else (R_HI if dx < bw // 2 else R_DK)
            if y % 6 == 0 and 2 <= dx <= bw - 3 and dx % 3 == 0:
                c = '#080a16'
            put(bx + dx, y, c)
    if bh >= 50 and not ANIM:
        glow(bx + bw // 2, top_r + 2, 3, PAL['eye'], 0.45)

# 4. Bahia maritima de Jeju (debajo de HOR=280)
render_lago(
    lz,
    PAL['agua'],
    PAL['ola'],
    DESTELLOS,
    ANIM,
    mx=CX_ASTRO,
    hor=HOR,
    reflejo_cols=(PAL['ola'][0], PAL['ola'][1]),
)

# Farallones volcanicos dentados en la bahia izquierda
for sx, sy_base, sw, sh in ((56, 332, 22, 36), (126, 308, 16, 26)):
    for dy in range(-sh, 4):
        prog = (dy + sh) / float(sh + 4)
        jag = int(3 * math.sin(dy * 0.4 + sx))
        hw = max(1, int(sw * (0.20 + 0.80 * prog)) + jag)
        for dx in range(-hw, hw + 1):
            c = RK_HI if dx < -hw // 3 else (RK0 if dx < hw // 3 else RK2)
            put(sx + dx, sy_base + dy, c)
    for dx in range(-sw - 4, sw + 5):
        if (dx + sx) % 3 != 0:
            over(sx + dx, sy_base + 3, PAL['ola'][0], 0.45)

# 5. Peninsula rocosa de la Isla de Jeju
rx_noise = Ruido(883)
ry_noise = Ruido(947)
r_ridge = Ruido(313)
G0, G1, G_DK = PAL['grass']
for x in range(W):
    ridge_island = int(242 - 9 * fbm(r_ridge, x * 0.018) + (8 if x > 515 else 0))
    for y in range(ridge_island, H):
        shore_x = int(238 - 76 * (max(0, y - 246) / float(H - 246)) ** 0.72 + 10 * math.sin(y * 0.08))
        if x < shore_x:
            continue
        is_rim = (x - shore_x) < 9 and y >= 246
        n2d = 0.5 * fbm(rx_noise, x * 0.032) + 0.5 * fbm(ry_noise, y * 0.045 + 9.0) + 0.14 * math.sin(x * 0.05) * math.cos(y * 0.06)
        if is_rim:
            c = RK2 if (x + y) % 2 else RK1
        elif y < ridge_island + 4:
            c = G1 if n2d > 0.42 else RK0
        elif y < 306 and n2d > 0.46:
            c = G1 if dith(x, y, 0.52) else G0
        elif y < 330 and n2d > 0.58:
            c = G0 if dith(x, y, 0.45) else RK1
        else:
            c = RK_HI if n2d > 0.62 else (RK0 if n2d > 0.44 else RK1)
        if y > 336 and (x * 7 + y * 11) % 31 == 0:
            c = mix(c, RK2, 0.45)
        put(x, y, c)
for y in range(246, H):
    shore_x = int(238 - 76 * ((y - 246) / float(H - 246)) ** 0.72 + 10 * math.sin(y * 0.08))
    if 0 <= shore_x - 2 < W:
        over(shore_x - 1, y, PAL['ola'][0], 0.55)
        over(shore_x - 3, y, PAL['ola'][1], 0.30)


def dibuja_palmera(px, by, h=36, lean=-8):
    for i in range(h):
        u = i / float(h)
        tx = int(px + lean * (u ** 1.4))
        ty = by - i
        put(tx, ty, G_DK)
        put(tx + 1, ty, G0)
    top_x, top_y = int(px + lean), by - h
    for ang_deg, l_f in ((-155, 16), (-120, 18), (-45, 17), (-15, 15), (15, 12), (160, 13)):
        rad = math.radians(ang_deg)
        for t in range(1, l_f):
            fx = int(top_x + math.cos(rad) * t)
            fy = int(top_y + math.sin(rad) * t + 0.08 * t * t)
            put(fx, fy, G1 if t < l_f // 2 else G0)
            put(fx, fy + 1, G_DK)


for px_p, py_p, ph_p, pl_p in ((222, 294, 34, -9), (242, 286, 26, 7), (594, 286, 36, 8), (618, 304, 40, -6)):
    dibuja_palmera(px_p, py_p, ph_p, pl_p)

# 6. COLMENA GIGANTE DE LA REINA HORMIGA (lado derecho, y=178..354)
HV0, HV1, HV2, HV_HI = PAL['hive']
CG0, CG1, CG2 = PAL['cave_glow']
H_CX, H_BASE = 486, 354
for y in range(178, H_BASE + 1):
    t = (y - 178) / float(H_BASE - 178)
    rib_mod = 8 * math.sin(t * 14.0) * (1 - t * 0.4)
    hw = int(6 + 72 * (t ** 0.72) + rib_mod)
    if y > 318:
        hw += (y - 318) * 2
    for dx in range(-hw, hw + 1):
        if y > 322 and abs(dx) > hw - 14 and not dith(H_CX + dx, y, (hw - abs(dx)) / 14.0):
            continue
        rib_val = math.sin((dx / max(8.0, hw)) * 9.0 + math.sin(t * 4.0) * 0.6)
        col = HV_HI if dx < -hw // 3 else (HV0 if dx < 0 else (HV1 if dx < hw // 2 else HV2))
        if rib_val > 0.72:
            col = mix(col, HV2, 0.55)
        elif rib_val < -0.78 and dx < hw // 3:
            col = mix(col, HV_HI, 0.40)
        if abs(dx) > 24 and y > 240 and abs(rib_val) < 0.10 and (y % 5 != 0):
            col = mix(col, CG0, 0.42)
        put(H_CX + dx, y, col)

for sp_x, sp_top, sp_base, sp_w in ((436, 200, 330, 14), (532, 214, 332, 13), (468, 168, 254, 11)):
    for y in range(sp_top, sp_base + 1):
        t_s = (y - sp_top) / float(max(1, sp_base - sp_top))
        hw_s = max(1, int(sp_w * (t_s ** 0.78)))
        for dx in range(-hw_s, hw_s + 1):
            c_sp = HV_HI if dx < -hw_s // 3 else (HV0 if dx < hw_s // 3 else HV2)
            if y > sp_base - 14 and dith(sp_x + dx, y, (sp_base - y) / 14.0):
                put(sp_x + dx, y, c_sp)
            elif y <= sp_base - 14:
                put(sp_x + dx, y, c_sp)

# Agujas cristalinas bioluminiscentes en la entrada de la colmena
for cx_cr, cy_cr, ch_cr, cw_cr, lean_c in ((422, 344, 22, 4, -4), (548, 340, 26, 5, 5), (562, 348, 16, 3, 2)):
    for i in range(ch_cr):
        u_cr = i / float(ch_cr)
        rx_c = int(cx_cr + lean_c * u_cr)
        ry_c = cy_cr - i
        hw_c = max(1, int(cw_cr * (1.0 - u_cr * 0.85)))
        for dx in range(-hw_c, hw_c + 1):
            c_cr = CG1 if dx == 0 else (CG2 if dx < 0 else CG0)
            over(rx_c + dx, ry_c, c_cr, 0.85)

# Caverna oscura central de la colmena
for y in range(274, H_BASE + 1):
    u_c = (y - 274) / float(H_BASE - 274)
    arch_w = int(30 * math.sin(min(1.0, u_c * 1.45) * math.pi * 0.5))
    for dx in range(-arch_w, arch_w + 1):
        d_in = 1.0 - abs(dx) / max(1.0, arch_w)
        c_cav = '#06030a' if d_in > 0.35 else HV2
        if y > 298 and d_in > 0.4 and dith(H_CX + dx, y, d_in * 0.55):
            c_cav = mix('#06030a', CG0, 0.45)
        put(H_CX + dx, y, c_cav)

for ex, ey, er in ((468, 342, 5), (480, 346, 4), (496, 341, 5), (508, 347, 4), (452, 348, 4)):
    for dy in range(-er - 1, er + 1):
        for dx in range(-er + 1, er):
            if (dx / float(er)) ** 2 + (dy / float(er + 1)) ** 2 <= 1.0:
                c_eg = CG1 if (dx < 0 and dy < 0) else (CG0 if dy <= 1 else HV2)
                put(ex + dx, ey + dy, c_eg)
    if ANIM:
        RUNAS.append([ex, ey - 1])
    else:
        glow(ex, ey - 1, 7, CG0, 0.55)

if ANIM:
    FAROLES.append([H_CX, 322, 18])
else:
    glow(H_CX, 322, 26, CG0, 0.55)

# 7. Promontorio volcanico de primer plano centrado bajo Beru (cx=306, cima y=334..H)
BERU_CX, BERU_BY = 306, 340
r_crag = Ruido(553)
for y in range(335, H):
    t_p = (y - 335) / float(H - 335)
    jag_l = int(10 * (fbm(r_crag, y * 0.11) - 0.5))
    jag_r = int(10 * (fbm(r_crag, y * 0.12 + 21) - 0.5))
    hw_l = int(58 + 44 * (t_p ** 0.78)) + jag_l
    hw_r = int(56 + 46 * (t_p ** 0.78)) + jag_r
    for dx in range(-hw_l, hw_r + 1):
        n_c = 0.5 * fbm(r_crag, (BERU_CX + dx) * 0.055) + 0.5 * fbm(ry_noise, y * 0.075) + 0.12 * math.sin(dx * 0.09) * math.cos(y * 0.08)
        if y < 340:
            c = RK_HI if n_c > 0.42 else RK0
        elif dx < -hw_l + 8:
            c = RK_HI if n_c > 0.45 else RK0
        elif dx > hw_r - 9 or dx == hw_r:
            c = RK2
        elif n_c < 0.34:
            c = RK2
        else:
            c = RK0 if n_c > 0.52 else RK1
        put(BERU_CX + dx, y, c)

# Fisuras de mana violeta/cian resquebrajando la roca hacia los pies de Beru
for f_ang, f_len in ((-0.75, 42), (-0.35, 34), (0.35, 34), (0.78, 42), (-1.15, 28), (1.15, 28)):
    fx_cur, fy_cur = float(BERU_CX), float(BERU_BY + 1)
    for step in range(f_len):
        fx_cur += math.sin(f_ang) * 1.15 + 0.45 * math.sin(step * 0.65 + f_ang * 4.0)
        fy_cur += math.cos(f_ang) * 0.62
        px_f, py_f = int(round(fx_cur)), int(round(fy_cur))
        if 0 <= px_f < W and 335 <= py_f < H:
            alpha_f = max(0.20, 1.0 - step / float(f_len))
            over(px_f, py_f, PAL['aura_mid'], 0.85 * alpha_f)
            if step < f_len * 0.55:
                over(px_f, py_f, PAL['aura_cyan'], 0.72 * alpha_f)


# 8. BERU (El Rey Hormiga de las Sombras, cx=306, by=340) — Pose "Aura Farming" imponente
def dibuja_beru(cx, by):
    SH_C = PAL['shad_core']
    SH_B = PAL['shad_body']
    SH_H = PAL['shad_hi']
    SH_R = PAL['shad_rim']
    A_OUT = PAL['aura_outer']
    A_MID = PAL['aura_mid']
    A_HOT = PAL['aura_hot']
    A_CY = PAL['aura_cyan']
    W_BG, W_VN, W_HI = PAL['wing']
    EYE = PAL['eye']

    # --- A) Anillos concentricos de presion/aura en la roca bajo Beru ---
    for r_x, r_y, col_r, op_r in (
        (48, 8, A_OUT, 0.88),
        (43, 7, SH_R, 0.82),
        (33, 5, A_HOT, 0.78),
        (22, 3, A_CY, 0.90),
    ):
        for ang_i in range(200):
            ang = ang_i * 6.283185 / 200.0
            rx_p = int(round(cx + math.cos(ang) * r_x))
            ry_p = int(round(by + math.sin(ang) * r_y))
            over(rx_p, ry_p, col_r, op_r)

    # --- B) Llamarada organica de aura ascendente (afilada en lenguas de fuego sin corte recto arriba) ---
    for dx in range(-42, 43):
        abs_x = abs(dx)
        core_profile = math.exp(-(abs_x / 20.0) ** 1.7)
        tongue_h = (
            12.0 * max(0.0, math.sin(dx * 0.34 + 0.4))
            + 9.0 * max(0.0, math.cos(dx * 0.62 - 0.9))
            + 6.0 * max(0.0, math.sin(dx * 1.05))
        )
        peak_dy = int(20 + 54 * core_profile + tongue_h * (0.38 + 0.62 * core_profile))
        for dy in range(0, peak_dy):
            u_h = dy / float(max(1, peak_dy))
            sway = int(round(math.sin(dy * 0.14 + dx * 0.09) * (1.2 + u_h * 2.2)))
            px_a = cx + dx + sway
            py_a = by - dy
            wisp = 0.5 + 0.5 * math.sin(dx * 0.45 - dy * 0.25 + math.cos(dy * 0.17) * 1.4)
            # Afina las lenguas de humo negro-purpura al acercarse a la punta superior
            if u_h > 0.68 and wisp < (u_h - 0.55) * 1.5:
                continue
            fade = max(0.0, 1.0 - (u_h ** 1.35))
            if abs_x < 10 and dy > 16 and dy < 44 and fade > 0.28:
                col_a = A_CY if (wisp > 0.62 and abs_x < 6) else A_MID
                op_a = 0.40 * fade
            elif abs_x < 22 and fade > 0.18:
                col_a = A_HOT if wisp > 0.72 else (A_MID if wisp > 0.36 else SH_R)
                op_a = 0.62 * fade
            else:
                col_a = A_OUT if wisp < 0.62 else SH_R
                op_a = 0.72 * fade
            over(px_a, py_a, col_a, op_a)

    # --- C) 4 Alas insectoides oscuras con borde violeta nitido barridas hacia atras ---
    for side in (-1, 1):
        # Ala superior: sale de la espalda (dx=+-8, dy=32) hacia arriba-afuera
        for step in range(30):
            u = step / 29.0
            wx = cx + side * int(7 + u * 29)
            w_center = by - 31 - int(u * 21 - 4 * (u ** 2))
            half_blade = max(1, int(4.5 * math.sin(u * math.pi * 0.88)))
            for off_y in range(-half_blade, half_blade + 1):
                yy = w_center + off_y
                is_edge = (off_y == -half_blade or off_y == half_blade or step > 26)
                is_vein = (off_y == 0 and step < 24 and step % 2 == 0)
                if is_edge:
                    over(wx, yy, W_VN if step < 22 else W_HI, 0.88)
                elif is_vein:
                    over(wx, yy, W_HI, 0.65)
                else:
                    over(wx, yy, W_BG, 0.72)
        # Ala inferior: mas corta y angulada hacia atras
        for step in range(21):
            u = step / 20.0
            wx = cx + side * int(6 + u * 21)
            w_center = by - 24 - int(u * 8)
            half_blade = max(1, int(3.2 * math.sin(u * math.pi * 0.85)))
            for off_y in range(-half_blade, half_blade + 1):
                yy = w_center + off_y
                is_edge = (off_y == -half_blade or off_y == half_blade or step > 18)
                if is_edge:
                    over(wx, yy, W_VN, 0.84)
                else:
                    over(wx, yy, W_BG, 0.70)

    # --- D) Cola quitinosa segmentada arqueada hacia la derecha ---
    for i in range(28):
        u = i / 27.0
        tx = int(cx + 6 + 17 * math.sin(u * 2.1))
        ty = int(by - 16 + u * 15)
        r_t = 2 if u < 0.70 else 1
        for dy_t in range(-r_t, r_t + 1):
            for dx_t in range(-r_t, r_t + 1):
                if dx_t * dx_t + dy_t * dy_t <= r_t * r_t:
                    c_t = SH_R if (i % 5 == 0 and dy_t < 0) else (SH_H if dy_t < 0 else SH_C)
                    put(tx + dx_t, ty + dy_t, c_t)

    # --- E) Cuerpo esculpido de Beru (45px alto, 41px ancho, silueta oscura solida) ---
    rows_spec = (
        ('.......RR...........', '.'),
        ('........RRK.........', '.'),
        ('.........RBR........', '.'),
        ('..........RBR.......', '.'),
        ('...........RBR......', '.'),
        ('............RBK.....', '.'),
        ('.............RBR....', 'R'),
        ('.............RBBK..R', 'H'),
        ('..............RBBBBK', 'H'),
        ('.............RBBKKKB', 'B'),
        ('............RBBKKKKB', 'K'),
        ('............RBKKEEEK', 'K'),
        ('............RBKKEWWK', 'K'),
        ('............RBBKBBWK', 'K'),
        ('............RKKKBMWM', 'W'),
        ('.............RKWWK.K', 'M'),
        ('.............RKRKR.R', 'K'),
        ('.......RRR...RBBKRKB', 'C'),
        ('......RBHBR.RBBKKKKB', 'C'),
        ('.....RBBHBRRBBKKKHHB', 'W'),
        ('....RBBKHBRRBBKKHHCB', 'C'),
        ('....RBBKBB.RBBKKKHHB', 'B'),
        ('...RBBK.BB..RBBKKKHB', 'R'),
        ('...RBK..RB..RBBKBBKB', 'B'),
        ('..RCBK..RB...RBBKKHB', 'C'),
        ('..RBK...RK...RBBKKKB', 'K'),
        ('..RHK...RK....RBBKKB', 'R'),
        ('.RCB...........RBBKB', 'K'),
        ('.RBK..........RBBHKB', 'B'),
        ('.RHK..........RBBK.B', 'K'),
        ('RCKR.........RBBK..R', '.'),
        ('RCW..........RBBK...', '.'),
        ('WCW.........RBBH....', '.'),
        ('W.W.........RBBK....', '.'),
        ('..W........RBBK.....', '.'),
        ('...........RBBH.....', '.'),
        ('..........RCHB......', '.'),
        ('..........RBBK......', '.'),
        ('.........RBBH.......', '.'),
        ('.........RBBK.......', '.'),
        ('.........RBB........', '.'),
        ('........RBBK........', '.'),
        ('........RBB.........', '.'),
        ('.......RRBBK........', '.'),
        ('......RCWKKR........', '.'),
    )
    spr_tall = [left + mid + left[::-1] for left, mid in rows_spec]

    pinta_sprite(lz, cx, by, spr_tall, {
        'K': SH_C,
        'B': SH_B,
        'H': SH_H,
        'R': SH_R,
        'C': A_CY,
        'W': '#f2f8ff',
        'E': EYE,
        'M': A_HOT,
    })

    # Estela luminosa en los ojos (aura eye trail caracteristica de Beru) + brillo en garras
    for side in (-1, 1):
        for k in range(1, 6):
            over(cx + side * (5 + k), by - 33 - k // 2, EYE if k < 3 else A_HOT, 0.88 - k * 0.14)
        over(cx + side * 19, by - 12, A_CY, 0.90)
        over(cx + side * 20, by - 11, '#ffffff', 0.78)

    # --- F) Arcos de relampago y chispas de aura subiendo alrededor de Beru ---
    arcs = [
        (-21, 5, -27, 17, -20, 29, -26, 42),
        (21, 7, 28, 19, 21, 31, 27, 44),
        (-13, 38, -19, 49, -14, 60, -18, 69),
        (13, 40, 19, 51, 14, 62, 18, 70),
    ]
    for x0, y0, x1, y1, x2, y2, x3, y3 in arcs:
        pts = ((x0, y0), (x1, y1), (x2, y2), (x3, y3))
        for idx in range(len(pts) - 1):
            ax0, ay0 = pts[idx]
            ax1, ay1 = pts[idx + 1]
            steps = max(abs(ax1 - ax0), abs(ay1 - ay0), 1)
            for s in range(steps + 1):
                u_s = s / float(steps)
                lx_a = cx + int(round(ax0 + (ax1 - ax0) * u_s))
                ly_a = by - int(round(ay0 + (ay1 - ay0) * u_s))
                over(lx_a, ly_a, A_CY if (s % 2 == 0) else A_MID, 0.78)

    for ox_e, oy_e, col_e in (
        (-30, 10, A_MID), (-34, 24, A_CY), (-27, 42, A_HOT), (-19, 58, A_CY),
        (30, 12, A_CY), (35, 26, A_MID), (28, 44, A_HOT), (20, 60, A_CY),
        (-8, 68, A_HOT), (9, 71, A_CY), (0, 76, A_MID),
    ):
        over(cx + ox_e, by - oy_e, col_e, 0.90)
        over(cx + ox_e, by - oy_e - 1, '#ffffff', 0.42)

    # Registro de puntos animados para el motor vivo (ojo + nucleo + corona de aura)
    if ANIM:
        RUNAS.append([cx - 3, by - 33])
        RUNAS.append([cx + 3, by - 33])
        RUNAS.append([cx, by - 25])
        RUNAS.append([cx - 19, by - 13])
        RUNAS.append([cx + 19, by - 13])
        RUNAS.append([cx - 24, by - 34])
        RUNAS.append([cx + 24, by - 34])
        RUNAS.append([cx - 14, by - 51])
        RUNAS.append([cx + 14, by - 51])
        FAROLES.append([cx, by - 25, 20])
        FAROLES.append([cx, by - 40, 14])
    else:
        glow(cx, by - 33, 6, EYE, 0.42)
        glow(cx, by - 24, 14, A_MID, 0.25)


dibuja_beru(BERU_CX, BERU_BY)


# 9. Hormigas Soldado de Jeju arrodilladas/inclinadas hacia el aura de Beru (facing left)
def dibuja_hormiga_soldado(cx, by):
    SH_C, SH_B, SH_H, SH_R, EYE = PAL['shad_core'], PAL['shad_body'], PAL['shad_hi'], PAL['shad_rim'], PAL['eye']
    for k in range(10):
        over(cx + 2 + k, by - 9 - k // 2, PAL['wing'][1], 0.78)
        over(cx + 2 + k, by - 8 - k // 2, PAL['wing'][0], 0.65)
    # Pose inclinada hacia la izquierda (reverencia ante el Rey Beru)
    spr = [
        '..R...R........',
        '...RBBBR.......',
        '..REEEBBR......',
        '..RBBBBBBBR....',
        '.RBK.RHHHBBBR..',
        'RKR...RBBBBBR..',
        '.......RBB..BR.',
        '......RBB...BBR',
        '.....RKK.....KR',
    ]
    pinta_sprite(lz, cx, by, spr, {
        'K': SH_C,
        'B': SH_B,
        'H': SH_H,
        'R': SH_R,
        'E': EYE,
    })
    if ANIM:
        RUNAS.append([cx - 2, by - 6])


# Apoyadas firme en los escalones rocosos derechos mirando hacia Beru
dibuja_hormiga_soldado(408, 352)
dibuja_hormiga_soldado(528, 348)

# 10. Rocas oscuras en primer plano inferior
for rx, hw_r, h_r in ((198, 20, 12), (596, 36, 22)):
    for dy in range(-h_r, 1):
        wc = int(hw_r * (1 - (-dy) / (h_r + 2)))
        for dx in range(-wc, wc + 1):
            put(rx + dx, H + dy - 1, RK0 if dx < 0 else RK2)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
