#!/usr/bin/env python3
"""PixelZen Worlds - Solo Leveling (Monitor 2): Isla de Jeju, Colmena de Hormigas y Rey Beru."""
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
        sky=['#040714', '#080e24', '#101836', '#18244a', '#242e5c', '#32386c', '#44407c', '#58488a', '#6e5094', '#865c9c'],
        mont=('#20263c', '#161a2c', '#0e101c'),
        ruin=('#1a1c2e', '#101220', '#2b2e46'),
        rock=('#2b263c', '#1c1828', '#0e0b16', '#443b5c'),
        grass=('#122420', '#1c3a2f', '#0a1614'),
        hive=('#38243c', '#26172a', '#150b18', '#523456'),
        cave_glow=('#a82468', '#ff488c', '#8e40ff'),
        agua='#090e20',
        ola=('#9278d8', '#483a7c', '#1d183e'),
        shad_core='#07050c',
        shad_rim='#7e3ee0',
        wing=('#1c1232', '#6e38c8'),
        eye='#ff3270',
        vig=0.75,
        nube=['#222c4e', '#303b64', '#404c7a', '#525c8e', '#666da0', '#1c2442'],
    ),
    'dorado': dict(
        sky=['#14102c', '#24183e', '#3a224c', '#582c56', '#7c3858', '#a44854', '#ca5c4e', '#e87a4e', '#fa9f5a', '#ffca7c'],
        mont=('#3c243a', '#2a182c', '#1a0e1e'),
        ruin=('#321e30', '#201220', '#4c2e48'),
        rock=('#442c3b', '#2d1c28', '#160d14', '#644254'),
        grass=('#1e2e20', '#2e462d', '#101a12'),
        hive=('#4c2638', '#341828', '#1c0c16', '#6e384e'),
        cave_glow=('#c42868', '#ff5490', '#9e44ff'),
        agua='#1e122c',
        ola=('#ffa284', '#8e4c72', '#3c2046'),
        shad_core='#09060e',
        shad_rim='#9a46ea',
        wing=('#281438', '#8642d4'),
        eye='#ff3c78',
        vig=0.82,
        nube=['#5c3054', '#7e3e62', '#a44e68', '#ca666a', '#ea8a6a', '#482444'],
    ),
    'dia': dict(
        sky=['#1e4688', '#2c5ca0', '#3e74b6', '#568eca', '#72a8da', '#90c0e6', '#aed4ee', '#c8e4f2', '#e0eef2', '#f0f4ea'],
        mont=('#485c78', '#384862', '#283448'),
        ruin=('#424c62', '#2c3446', '#626e86'),
        rock=('#4e4e5e', '#363644', '#1f1f2a', '#6e6e80'),
        grass=('#20482e', '#306640', '#122a1c'),
        hive=('#543c4e', '#3c2a3a', '#241824', '#74546c'),
        cave_glow=('#b62868', '#ff4c8c', '#8e44ff'),
        agua='#1d385a',
        ola=('#bce0f4', '#688cb8', '#324c78'),
        shad_core='#090812',
        shad_rim='#7e44d4',
        wing=('#201836', '#7244ca'),
        eye='#ff3270',
        vig=0.90,
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

MX, MY, MR = 148, 76, 36
CX_ASTRO = MX if FASE == 'noche' else (MX + 24 if FASE == 'dorado' else MX - 16)
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#b89cff', base='#f2f4ff', sombra='#c6cce8', crater='#a0a6cc', crater_hi='#b8bee0')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, MX + 24, 186, 22, halo='#ff9668', centro='#ffecd8', borde='#ff5e48', rayo='#ff805a')
    else:
        dibuja_sol_estandar(lz, MX - 16, 84, 22, halo='#ffe2a0', centro='#fffdf0', borde='#ffc060', rayo='#ffe098')

# 2. Nubes altas
NUBES_DEF = [
    (68, 34, 145, PAL['nube'][0], 2),
    (265, 48, 175, PAL['nube'][1], 3),
    (420, 32, 155, PAL['nube'][2], 2),
    (175, 118, 165, PAL['nube'][3], 3),
    (360, 108, 140, PAL['nube'][4], 2),
    (525, 224, 110, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 3. Cordillera volcanica costera y ruinas de la Ciudad de Jeju asentadas en tierra firme sobre el horizonte
rm = Ruido(731)
M0, M1, M2 = PAL['mont']
for x in range(W):
    dip_r = 34 if x > 470 else 0
    ridge = int(224 + 28 * fbm(rm, x * 0.014 + 1.2) + dip_r)
    ridge = min(HOR, ridge)
    for y in range(ridge, HOR + 1):
        t = (y - ridge) / max(1, HOR - ridge)
        put(x, y, mix(M0, M2, t * 0.85))

# Lengua costera solida en la bahia lejana (x=28..212, y=266..HOR) para anclar los edificios en tierra firme
R_HI, R_DK, R_RIM = PAL['ruin']
RK0, RK1, RK2, RK_HI = PAL['rock']
for x in range(26, 214):
    h_coast = int(10 * math.sin((x - 26) / 188.0 * math.pi))
    for y in range(HOR - h_coast, HOR + 1):
        put(x, y, RK1 if y < HOR - 2 else RK2)

for bx, bw, bh in ((54, 15, 42), (73, 14, 58), (94, 17, 36), (124, 15, 50), (162, 16, 40)):
    base_city = HOR - 5
    top_r = base_city - bh
    for y in range(top_r, base_city + 1):
        if y < top_r + 6 and (bx + y) % 3 == 0:
            continue
        for dx in range(bw):
            c = R_RIM if dx == 0 else (R_HI if dx < bw // 2 else R_DK)
            if y % 6 == 0 and 2 <= dx <= bw - 3 and dx % 3 == 0:
                c = '#080a16'
            put(bx + dx, y, c)

# 4. Bahia maritima de Jeju (debajo de HOR=278)
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
r_rock_bay = Ruido(411)
for sx, sy_base, sw, sh in ((56, 330, 22, 34), (126, 306, 16, 24)):
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

# 5. Peninsula rocosa de la Isla de Jeju con borde superior organico y ruido 2D natural
rx_noise = Ruido(883)
ry_noise = Ruido(947)
r_ridge = Ruido(313)
G0, G1, G_DK = PAL['grass']
for x in range(W):
    ridge_island = int(248 - 10 * fbm(r_ridge, x * 0.018) + (8 if x > 500 else 0))
    for y in range(ridge_island, H):
        shore_x = int(248 - 78 * (max(0, y - 254) / float(H - 254)) ** 0.72 + 10 * math.sin(y * 0.08))
        if x < shore_x:
            continue
        is_rim = (x - shore_x) < 9 and y >= 254
        n2d = 0.5 * fbm(rx_noise, x * 0.032) + 0.5 * fbm(ry_noise, y * 0.045 + 9.0) + 0.14 * math.sin(x * 0.05) * math.cos(y * 0.06)
        if is_rim:
            c = RK2 if (x + y) % 2 else RK1
        elif y < ridge_island + 4:
            c = G1 if n2d > 0.42 else RK0
        elif y < 316 and n2d > 0.46:
            c = G1 if dith(x, y, 0.52) else G0
        elif y < 342 and n2d > 0.58:
            c = G0 if dith(x, y, 0.45) else RK1
        else:
            c = RK_HI if n2d > 0.62 else (RK0 if n2d > 0.44 else RK1)
        if y > 348 and (x * 7 + y * 11) % 31 == 0:
            c = mix(c, RK2, 0.45)
        put(x, y, c)
for y in range(254, H):
    shore_x = int(248 - 78 * ((y - 254) / float(H - 254)) ** 0.72 + 10 * math.sin(y * 0.08))
    if 0 <= shore_x - 2 < W:
        over(shore_x - 1, y, PAL['ola'][0], 0.55)
        over(shore_x - 3, y, PAL['ola'][1], 0.30)


def dibuja_palmera(px, by, h=38, lean=-8):
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


for px_p, py_p, ph_p, pl_p in ((222, 304, 34, -9), (244, 294, 28, 7), (586, 296, 36, 8), (610, 314, 42, -6)):
    dibuja_palmera(px_p, py_p, ph_p, pl_p)

# 6. COLMENA GIGANTE DE LA REINA HORMIGA (sin rayado diagonal: textura organica quitinosa)
HV0, HV1, HV2, HV_HI = PAL['hive']
CG0, CG1, CG2 = PAL['cave_glow']
H_CX, H_BASE = 466, 356
for y in range(184, H_BASE + 1):
    t = (y - 184) / float(H_BASE - 184)
    rib_mod = 8 * math.sin(t * 14.0) * (1 - t * 0.4)
    hw = int(6 + 76 * (t ** 0.72) + rib_mod)
    if y > 318:
        hw += (y - 318) * 2
    for dx in range(-hw, hw + 1):
        # Nervaduras verticales curvas siguiendo la forma de la colmena
        rib_val = math.sin((dx / max(8.0, hw)) * 9.0 + math.sin(t * 4.0) * 0.6)
        col = HV_HI if dx < -hw // 3 else (HV0 if dx < 0 else (HV1 if dx < hw // 2 else HV2))
        if rib_val > 0.72:
            col = mix(col, HV2, 0.55)
        elif rib_val < -0.78 and dx < hw // 3:
            col = mix(col, HV_HI, 0.40)
        if abs(dx) > 26 and y > 246 and abs(rib_val) < 0.10 and (y % 5 != 0):
            col = mix(col, CG0, 0.42)
        put(H_CX + dx, y, col)

for sp_x, sp_top, sp_base, sp_w in ((416, 208, 336, 15), (514, 224, 338, 14), (446, 174, 260, 12)):
    for y in range(sp_top, sp_base + 1):
        t_s = (y - sp_top) / float(max(1, sp_base - sp_top))
        hw_s = max(1, int(sp_w * (t_s ** 0.78)))
        for dx in range(-hw_s, hw_s + 1):
            c_sp = HV_HI if dx < -hw_s // 3 else (HV0 if dx < hw_s // 3 else HV2)
            # Funde la base suavemente en el cuerpo de la colmena sin corte horizontal
            if y > sp_base - 14 and dith(sp_x + dx, y, (sp_base - y) / 14.0):
                put(sp_x + dx, y, c_sp)
            elif y <= sp_base - 14:
                put(sp_x + dx, y, c_sp)

# Caverna oscura central de la colmena
for y in range(278, H_BASE + 1):
    u_c = (y - 278) / float(H_BASE - 278)
    arch_w = int(32 * math.sin(min(1.0, u_c * 1.45) * math.pi * 0.5))
    for dx in range(-arch_w, arch_w + 1):
        d_in = 1.0 - abs(dx) / max(1.0, arch_w)
        c_cav = '#06030a' if d_in > 0.35 else HV2
        if y > 304 and d_in > 0.4 and dith(H_CX + dx, y, d_in * 0.55):
            c_cav = mix('#06030a', CG0, 0.45)
        put(H_CX + dx, y, c_cav)

for ex, ey, er in ((448, 346, 5), (460, 349, 4), (476, 345, 5), (488, 350, 4), (432, 351, 4)):
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
    FAROLES.append([H_CX, 326, 18])
else:
    glow(H_CX, 326, 26, CG0, 0.55)

# 7. Promontorio escarpado de roca basaltica (natural y dentado, sin franjas horizontales)
r_crag = Ruido(553)
for y in range(324, H):
    t_p = (y - 324) / float(H - 324)
    jag_l = int(9 * (fbm(r_crag, y * 0.11) - 0.5))
    jag_r = int(10 * (fbm(r_crag, y * 0.12 + 21) - 0.5))
    hw_l = int(40 + 44 * (t_p ** 0.82)) + jag_l
    hw_r = int(38 + 46 * (t_p ** 0.82)) + jag_r
    for dx in range(-hw_l, hw_r + 1):
        n_c = 0.5 * fbm(r_crag, (308 + dx) * 0.055) + 0.5 * fbm(ry_noise, y * 0.075) + 0.12 * math.sin(dx * 0.09) * math.cos(y * 0.08)
        if y < 328:
            c = RK_HI if n_c > 0.45 else G0
        elif dx < -hw_l + 6:
            c = RK_HI if n_c > 0.45 else RK0
        elif dx > hw_r - 8 or dx == hw_r:
            c = RK2
        elif n_c < 0.34:
            c = RK2
        else:
            c = RK0 if n_c > 0.52 else RK1
        put(308 + dx, y, c)


# 8. BERU (El Rey Hormiga de Jeju) - Silueta majestuosa e imponente, alas solidas oscuras con venas, garras y cuernos
def dibuja_beru(cx, by):
    SH_C, SH_R = PAL['shad_core'], PAL['shad_rim']
    W_BG, W_VN = PAL['wing']
    EYE = PAL['eye']

    # Alas insectoides afiladas y semitransparentes (solidas, sin rejilla)
    for side in (-1, 1):
        for t_w in range(32):
            u = t_w / 31.0
            wx = cx + side * (5 + t_w)
            wy_top = by - 36 - int(math.sin(u * 2.1) * 11)
            wy_bot = by - 25 + int((u ** 0.85) * 14)
            for yy in range(wy_top, wy_bot + 1):
                es_borde = (yy <= wy_top + 1 or yy >= wy_bot - 1 or t_w == 31)
                es_vena = (abs((yy - wy_top) - int(t_w * 0.35)) <= 0 or abs((yy - wy_top) - int(t_w * 0.72)) <= 0)
                if es_borde or es_vena:
                    over(wx, yy, W_VN, 0.88)
                else:
                    over(wx, yy, W_BG, 0.58)

    # Cola quitinosa arqueada tras Beru hasta apoyarse cerca de la roca
    for i in range(28):
        u = i / 27.0
        tx = int(cx + 8 + 19 * math.sin(u * 2.15))
        ty = int(by - 16 + u * 16)
        r_t = 2 if u < 0.72 else 1
        for dy in range(-r_t, r_t + 1):
            for dx in range(-r_t, r_t + 1):
                if dx * dx + dy * dy <= r_t * r_t:
                    put(tx + dx, ty + dy, SH_R if (i % 5 == 0 and dy < 0) else SH_C)

    # Sprite nítido de Beru (~32px alto + cuernos y alas = ~46px total)
    spr = [
        '........KK........KK.........',
        '.........KK......KK..........',
        '..........KKK..KKK...........',
        '..........KKKKKKKK...........',
        '.........KKKEKKEKKK..........',
        '.........KKKKKKKKKK..........',
        '..........KKK..KKK...........',
        '......KKKKKKKKKKKKKKKK.......',
        '....KKKKKKKKKKKKKKKKKKKK.....',
        '...KKKKKKKKKKKKKKKKKKKKKK....',
        '..KKKKK..KKKKKKKKKK..KKKKK...',
        '.KKKK....KKKKKKKKKK....KKKK..',
        'KKKK......KKKKKKKK......KKKK.',
        'KKK.......KKKKKKKK.......KKK.',
        'KK.........KKKKKK.........KK.',
        '...........KKKKKK............',
        '..........KKKKKKKK...........',
        '.........KKKKKKKKKK..........',
        '........KKKKKKKKKKKK.........',
        '........KKKKK..KKKKK.........',
        '.......KKKKK....KKKKK........',
        '.......KKKK......KKKK........',
        '......KKKK........KKKK.......',
        '......KKKK........KKKK.......',
        '.....KKKKK........KKKKK......',
        '....KKKKKK........KKKKKK.....',
    ]
    pinta_sprite(lz, cx, by, spr, {'K': SH_C, 'E': EYE})

    x0 = cx - len(spr[0]) // 2
    y0 = by - len(spr) + 1
    for ry, row in enumerate(spr):
        for rx, ch in enumerate(row):
            if ch == 'K' and (ry < 13 or rx < 4 or rx > len(row) - 5):
                if rx == 0 or row[rx - 1] == '.':
                    put(x0 + rx, y0 + ry, SH_R)

    if ANIM:
        RUNAS.append([cx - 2, by - 21])
        RUNAS.append([cx + 1, by - 21])
        RUNAS.append([cx - 13, by - 12])
        RUNAS.append([cx + 13, by - 12])
        FAROLES.append([cx, by - 24, 11])
    else:
        glow(cx, by - 21, 5, EYE, 0.45)


dibuja_beru(308, 328)


# 9. Hormigas Soldado de Jeju bien apoyadas sobre la roca (NINGUNA flotando en el aire)
def dibuja_hormiga_soldado(cx, by):
    SH_C, SH_R, EYE = PAL['shad_core'], PAL['shad_rim'], PAL['eye']
    spr = [
        '...K....K...',
        '....KKKK....',
        '....KEEK....',
        '..KKKKKKKK..',
        '.KK.KKKK.KK.',
        '.K..KKKK..K.',
        '....KKKK....',
        '...KK..KK...',
        '..KK....KK..',
    ]
    for side in (-1, 1):
        for k in range(7):
            over(cx + side * (2 + k), by - 8 - k // 2, PAL['wing'][1], 0.72)
            over(cx + side * (2 + k), by - 7 - k // 2, PAL['wing'][0], 0.65)
    pinta_sprite(lz, cx, by, spr, {'K': SH_C, 'E': EYE})
    if ANIM:
        RUNAS.append([cx, by - 6])


# Apoyadas firme en la roca al pie derecho y flanco izquierdo de la entrada a la colmena
dibuja_hormiga_soldado(536, 348)
dibuja_hormiga_soldado(398, 352)

# 10. Rocas oscuras en primer plano inferior
for rx, hw_r, h_r in ((204, 18, 10), (596, 36, 22)):
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
