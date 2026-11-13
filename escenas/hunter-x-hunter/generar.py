#!/usr/bin/env python3
"""PixelZen - Tema Hunter x Hunter (Mejorado): Isla Ballena, Árbol del Mundo y Muelle de Gon."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, en_zona, exporta_salida, exporta_sprites_si_aplica, fbm, mix, render_cielo,
    render_estrellas, render_lago, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(17)

PALETAS = {
    'noche': dict(
        sky=['#040914', '#081326', '#0d2038', '#122f4b', '#19405e', '#225370', '#2d6880', '#3d7d90', '#50939c', '#68a6a6'],
        mont=['#1d3d4a', '#15303c', '#0f2530', '#0a1b24', '#07131a'],
        mist=['#3b7b84', '#2e6470', '#234e5a', '#193b46', '#102832'],
        tree_sil=('#0a1a22', '#132c34', '#1d4448'),
        isla=('#0a1e18', '#123024', '#1d4c36', '#2a6848'),
        wood=('#3c2418', '#563422', '#26150e'),
        wall=('#70604c', '#544636'),
        roof=('#143628', '#1d4c38', '#2a684c'),
        fol=('#36a85a', '#268446', '#185e32', '#0e3c20'),
        agua='#061824',
        ola=('#6ee0cc', '#2e7c90', '#143c52'),
        suelo=('#081812', '#163626', '#0c2218', '#224a34'),
        vig=0.76,
        nube=['#2e5472', '#3c6886', '#4a7a98', '#6090aa', '#78a6ba', '#284a66'],
        rama=('#160e0a', '#2c1c14'),
        hoja={'l': '#5ee080', 'c': '#3ab860', 'm': '#248c48', 'd': '#145a30', 'x': '#0c341c'},
        nen=('#48f09c', '#b8ffe0'),
        hunter=('#d83848', '#f2eee4'),
        blimp=('#2c3a4c', '#445870', '#182230'),
        sail=('#8ea4b8', '#5e768c'),
    ),
    'dorado': dict(
        sky=['#141e3c', '#223054', '#38446c', '#58587e', '#826882', '#ae787a', '#d6886c', '#f29e5e', '#ffba5e', '#ffd87e'],
        mont=['#4c5468', '#3c4256', '#2e3346', '#222636', '#171a28'],
        mist=['#dc9678', '#c07e70', '#9c6668', '#744e5e', '#4e384e'],
        tree_sil=('#2a283c', '#3c344c', '#52445a'),
        isla=('#1e2e20', '#2c442a', '#406038', '#587c44'),
        wood=('#5c3622', '#7e4c30', '#381e12'),
        wall=('#c4a47e', '#987c5c'),
        roof=('#1e4e38', '#2a684a', '#3a8660'),
        fol=('#5ec868', '#429c4c', '#2a7036', '#1a4824'),
        agua='#1e3c4c',
        ola=('#ffd29c', '#88a0a8', '#3c586c'),
        suelo=('#182418', '#2c4426', '#20301e', '#3e5e32'),
        vig=0.84,
        nube=['#a87088', '#d48a84', '#f2a47e', '#ffc288', '#ffe09e', '#8e5e78'],
        rama=('#22140c', '#3e2416'),
        hoja={'l': '#a8e468', 'c': '#72be4c', 'm': '#468e38', 'd': '#285e26', 'x': '#163616'},
        nen=('#60f8a8', '#dcffec'),
        hunter=('#e84452', '#fff6ec'),
        blimp=('#666276', '#8a8296', '#424052'),
        sail=('#f4d2b4', '#b88c7e'),
    ),
    'dia': dict(
        sky=['#155cb8', '#2272ca', '#3488da', '#4c9ee6', '#6ab4ee', '#8cc8f4', '#aedcf8', '#cdeafa', '#e6f4f6', '#f8f6e0'],
        mont=['#4e809a', '#3e6e88', '#305c74', '#244b60', '#1a3a4c'],
        mist=['#b2deec', '#96cce0', '#7ab8d2', '#5ea2c0', '#448aa8'],
        tree_sil=('#2c5c66', '#3c747a', '#4e8e8e'),
        isla=('#1e482c', '#2c6438', '#3e8448', '#56a65a'),
        wood=('#724628', '#965e36', '#4a2c18'),
        wall=('#e8d8b8', '#c6b494'),
        roof=('#226846', '#2e845a', '#40a070'),
        fol=('#7ce06c', '#52ba4c', '#348c38', '#1e5c24'),
        agua='#166a82',
        ola=('#d2faf6', '#66b8cc', '#287690'),
        suelo=('#1c4224', '#346c36', '#24522a', '#468c44'),
        vig=0.92,
        nube=['#ffffff', '#f0f8fc', '#ffffff', '#e4f2fa', '#f6fcff', '#dcf0fa'],
        rama=('#2c1c10', '#4a2e1a'),
        hoja={'l': '#8ee868', 'c': '#5ac448', 'm': '#369434', 'd': '#1e6222', 'x': '#103a14'},
        nen=('#48f09c', '#d8fff0'),
        hunter=('#e83848', '#ffffff'),
        blimp=('#9aaec0', '#c4d6e6', '#6a7e90'),
        sail=('#ffffff', '#c8dce8'),
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

# 1. Cielo + aurora Nen nocturna
render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#48f09c', '#54b8ff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 44, halo='#7ee8d8', base='#f2fcf8', sombra='#c6e0dc', crater='#9ec0be', crater_hi='#b8d6d4'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 24, halo='#ffe498', centro='#fffef0', borde='#ffd05c', rayo='#ffe89c'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#d8fff0', '#bce8ff', '#98c8f0'])

MX, MY, MR = 362, 86, 44
CX_ASTRO = MX if FASE == 'noche' else (MX + 60 if FASE == 'dorado' else MX - 45)
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#7ee8d8', base='#f2fcf8', sombra='#c6e0dc', crater='#9ec0be', crater_hi='#b8d6d4')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, MX + 60, 206, 24, halo='#ffd080', centro='#fffbe6', borde='#ff9a44', rayo='#ffbe68')
    else:
        dibuja_sol_estandar(lz, MX - 45, 96, 24, halo='#ffe498', centro='#fffef0', borde='#ffd05c', rayo='#ffe89c')

# 2. Nubes y Dirigible de la Asociación de Cazadores
NUBES_DEF = [
    (175, 68, 175, PAL['nube'][0], 3),
    (365, 110, 145, PAL['nube'][1], 3),
    (115, 168, 195, PAL['nube'][2], 3),
    (285, 208, 155, PAL['nube'][3], 3),
    (550, 248, 125, PAL['nube'][4], 2),
    (410, 56, 95, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

bx, by = 418, 72
b_lo, b_hi, b_dk = PAL['blimp']
for dy in range(-8, 9):
    hw = int(26 * math.sqrt(max(0.0, 1.0 - (dy / 8.2) ** 2)))
    for dx in range(-hw, hw + 1):
        c = b_hi if dy < -2 else (b_lo if dy < 3 else b_dk)
        if dy == 0 and abs(dx) < hw - 2:
            c = PAL['hunter'][0]
        put(bx + dx, by + dy, c)
for dx in range(20, 29):
    for dy in range(-11, -4):
        if dx - 20 <= -dy - 2:
            put(bx + dx, by + dy, b_dk)
    for dy in range(5, 11):
        if dx - 20 <= dy - 2:
            put(bx + dx, by + dy, b_dk)
for dx in range(-9, 8):
    for dy in range(9, 13):
        c = '#ffcf70' if (dy == 10 and dx % 3 == 0 and FASE != 'dia') else b_dk
        put(bx + dx, by + dy, c)

# 3. Colosal Árbol del Mundo al fondo (x ~ 274)
wt_x = 274
wt_d, wt_m, wt_l = PAL['tree_sil']
for y in range(72, HOR + 1):
    t = (y - 72) / (HOR - 72)
    hw = int(9 + 20 * (t ** 2.1) + 2.2 * math.sin(y * 0.08))
    for dx in range(-hw, hw + 1):
        c = wt_l if dx < -hw // 3 else (wt_m if dx < hw // 3 else wt_d)
        if (dx * 3 + y // 4) % 7 == 0:
            c = mix(c, wt_d, 0.30)
        put(wt_x + dx, y, c)
# Ramas principales visibles bajo la copa del Árbol del Mundo
for side in (-1, 1):
    for k in range(28):
        bx_r = wt_x + side * (4 + k)
        by_r = 96 - int(k * 0.55)
        for dy in range(0, max(1, 3 - k // 12)):
            put(bx_r, by_r + dy, wt_m if side < 0 else wt_d)
# Neblina de gran altitud cruzando el tronco medio
for yy in range(134, 152):
    for xx in range(wt_x - 24, wt_x + 25):
        dist_m = abs(yy - 143) / 9.0
        if dith(xx, yy, (1.0 - dist_m) * 0.42):
            over(xx, yy, PAL['mist'][0], 0.48)
for cx, cy, rx, ry in (
    (wt_x, 76, 62, 16),
    (wt_x - 32, 62, 42, 14),
    (wt_x + 34, 64, 44, 14),
    (wt_x - 16, 46, 40, 14),
    (wt_x + 18, 48, 38, 13),
    (wt_x, 30, 34, 12),
    (wt_x - 4, 18, 22, 9),
):
    for dy in range(-ry, ry + 1):
        for dx in range(-rx, rx + 1):
            d = (dx / rx) ** 2 + (dy / ry) ** 2
            if d < 1.0 and (d < 0.72 or dith(cx + dx, cy + dy, (1.0 - d) * 2.8)):
                c = wt_l if dy < -ry // 4 or (dx < -rx // 3 and dy < ry // 4) else (wt_m if dy < ry // 3 else wt_d)
                put(cx + dx, cy + dy, c)

# 4. Acantilados verdes de Isla Ballena y Roca Aleta de Ballena
def rampa(x):
    return 1.0 if x < 430 else max(0.35, 1.0 - (x - 430) / 90 * 0.65)

CAPAS = [
    (242, 74, 31, 0.013, PAL['mont'][0], PAL['mist'][0]),
    (254, 58, 43, 0.018, PAL['mont'][1], PAL['mist'][1]),
    (264, 44, 55, 0.024, PAL['mont'][2], PAL['mist'][2]),
    (274, 28, 67, 0.032, PAL['mont'][3], PAL['mist'][3]),
]
crestas = []
for base, amp, seed, fr, col, mist in CAPAS:
    r, ra = Ruido(seed * 17), Ruido(seed * 31 + 5)
    c = []
    for x in range(W):
        n = fbm(r, x * fr + seed)
        am = 0.45 + 0.85 * ra(x * 0.012 + seed)
        c.append(base - amp * rampa(x) * am * n)
    crestas.append(c)
    for x in range(W):
        top = int(c[x])
        for y in range(top, HOR + 1):
            d = y - top
            cc = mix(col, mist, 0.28 * (d / max(1, HOR - top)) ** 1.9)
            if d < 2:
                cc = mix(cc, PAL['fol'][0], 0.18)
            put(x, y, cc)
        for k in range(1, 18):
            if dith(x, top + k, (1 - k / 18) * 0.38):
                over(x, top + k, mist, 0.5)

# Roca con forma de aleta de ballena a la derecha del puerto (x ~ 410)
rx0, ry0 = 410, HOR
for i in range(48):
    t = i / 47.0
    w_fin = max(2, int(24 * (1 - t ** 0.85)))
    ox = int(14 * (t ** 1.4))
    yy = ry0 - i
    for dx in range(-w_fin // 2, w_fin // 2 + 1):
        c = PAL['mont'][1] if dx < 0 else PAL['mont'][3]
        put(rx0 + ox + dx, yy, c)

# Vegetación tropical orgánica y variada en las lomas
r_veg = random.Random(33)
for x in range(244, W, 7):
    if r_veg.random() < 0.65:
        by = int(crestas[3][x]) + 4
        rad_x = r_veg.randint(4, 9)
        rad_y = r_veg.randint(3, 6)
        for dy in range(-rad_y, 2):
            for dx in range(-rad_x, rad_x + 1):
                d = (dx / rad_x) ** 2 + (dy / rad_y) ** 2
                if d <= 1.0 and (d < 0.78 or dith(x + dx, by + dy, (1.0 - d) * 3.0)):
                    c = PAL['fol'][0] if dy < -rad_y // 2 else (PAL['fol'][1] if dy < 0 else PAL['fol'][2])
                    put(x + dx, by + dy, c)

# 5. Litoral continuo de Isla Ballena desde la izquierda (x: 0..256) bajando en terraza al mar
WD0, WD1, WDK = PAL['wood']
WL0, WL1 = PAL['wall']
RF0, RF1, RF2 = PAL['roof']
WARM = '#ffd074'

for x in range(0, 256):
    # Colina verde alta a la izquierda (0..90), explanada de la casa (90..195), descenso al muelle (195..256)
    if x < 90:
        top_y = HOR - 28 - int(10 * math.cos(x / 90.0 * 1.57))
    elif x < 195:
        top_y = HOR - 14
    else:
        top_y = HOR - 14 + int((x - 195) / 61.0 * 14)
    for y in range(top_y, HOR + 1):
        d_s = y - top_y
        if d_s <= 2:
            c = PAL['isla'][3]
        elif d_s <= 6:
            c = PAL['isla'][2] if (x + d_s) % 7 else PAL['isla'][3]
        elif d_s > 18:
            c = PAL['isla'][0]
        else:
            c = PAL['isla'][1] if (x * 5 + y * 3) % 13 > 3 else PAL['isla'][0]
        put(x, y, c)
    # Flores silvestres ocasionales sobre la hierba
    if x < 110 and x % 17 == 3:
        put(x, top_y - 1, PAL['fol'][0])
        if x % 34 == 3:
            put(x + 1, top_y - 1, '#f8e690')

# Molino de viento rústico en la colina izquierda (x ~ 54)
mx_w, my_w = 54, HOR - 30
for yy in range(my_w - 28, my_w):
    t = (yy - (my_w - 28)) / 28.0
    hw = int(4 + 4 * t)
    for dx in range(-hw, hw + 1):
        put(mx_w + dx, yy, WL0 if dx < 0 else WL1)
for i in range(9):
    hw = max(0, 6 - i // 2)
    for dx in range(-hw, hw + 1):
        put(mx_w + dx, my_w - 28 - i, RF1 if dx < 0 else RF0)
# Aspas del molino
for ang in (0.4, 1.97, 3.54, 5.11):
    for k in range(1, 14):
        ax = int(mx_w + math.cos(ang) * k)
        ay = int(my_w - 22 + math.sin(ang) * k)
        put(ax, ay, WD0)
        put(ax + 1, ay, WD1)

# Casa de madera de Mito-san (x ~ 112..182, terraza y = HOR - 14)
CX0, CW, CH = 112, 70, 36
CY0 = HOR - 14 - CH
for yy in range(CY0 - 20, CY0):
    for x in range(CX0 + 12, CX0 + 18):
        put(x, yy, WDK if x > CX0 + 15 else WD0)
for x in range(CX0 + 11, CX0 + 19):
    put(x, CY0 - 21, WD1)
CHIMENEA = [CX0 + 15, CY0 - 22]

for yy in range(CY0, CY0 + CH):
    for x in range(CX0, CX0 + CW):
        if yy >= CY0 + CH - 10:
            put(x, yy, WD0 if (x // 4 + yy // 2) % 2 else WDK)
        else:
            put(x, yy, WL0 if x < CX0 + CW // 2 else WL1)
for x in (CX0, CX0 + CW - 1, CX0 + CW // 2):
    for yy in range(CY0, CY0 + CH):
        put(x, yy, WDK)
for yy in (CY0, CY0 + CH - 10):
    for x in range(CX0, CX0 + CW):
        put(x, yy, WDK)
# Puerta de madera de la casa de Mito-san
for yy in range(CY0 + CH - 12, CY0 + CH):
    for dx in range(-3, 4):
        put(CX0 + CW // 2 + dx, yy, WD0 if dx in (-3, 0, 3) else WDK)
for dx in range(-4, 5):
    put(CX0 + CW // 2 + dx, CY0 + CH - 13, WD1)

# Porche con barandilla delante y a la derecha
for x in range(CX0 + CW, CX0 + CW + 14):
    put(x, CY0 + 16, RF1)
    put(x, CY0 + 17, WDK)
    if x == CX0 + CW + 12:
        for yy in range(CY0 + 18, HOR - 14):
            put(x, yy, WD0)
for x in range(CX0 - 8, CX0 + CW + 14, 4):
    for yy in range(HOR - 18, HOR - 14):
        put(x, yy, WD1)
for x in range(CX0 - 8, CX0 + CW + 14):
    put(x, HOR - 17, WD0)

# Ventanas cálidas + buhardilla
for wy in (CY0 + 5, CY0 + 15):
    for vx in (CX0 + 9, CX0 + 23, CX0 + 44, CX0 + 58):
        if ANIM:
            VENTANAS.append([vx, wy])
        else:
            for dy in range(4):
                put(vx, wy + dy, WARM)
                put(vx + 1, wy + dy, WARM)
            glow(vx, wy + 2, 4, WARM, 0.35)
        for dx_ in (-1, 0, 1, 2):
            put(vx + dx_, wy - 1, WDK)

for i in range(21):
    hw = max(2, int((CW // 2 + 6) * (1 - i / 20.0)))
    cx = CX0 + CW // 2
    yy = CY0 - i
    for x in range(cx - hw, cx + hw + 1):
        c = RF2 if x < cx - hw // 3 else (RF1 if x < cx + hw // 3 else RF0)
        if (x + yy) % 4 == 0 and i > 1:
            c = mix(c, RF0, 0.3)
        put(x, yy, c)

# Monolito del Cazador junto al sendero (x = 224) con doble rombo rojo/blanco
mx_h, my_h = 224, HOR - 7
for yy in range(my_h - 18, my_h):
    for dx in range(-4, 5):
        put(mx_h + dx, yy, WD0 if dx < 0 else WDK)
h_red, h_wht = PAL['hunter']
for dy in range(-4, 5):
    for dx in range(-3, 4):
        if abs(dx) + abs(dy) <= 3:
            put(mx_h + dx, my_h - 11 + dy, h_red if abs(dx) + abs(dy) > 1 else h_wht)
if ANIM:
    RUNAS.append([mx_h, my_h - 11])

# Muelle largo de madera donde Gon pesca (x = 248..354)
for x in range(248, 354):
    put(x, HOR - 4, WD1)
    put(x, HOR - 3, WD0)
    put(x, HOR - 2, WDK)
for px_m in (256, 276, 296, 316, 336, 352):
    for yy in range(HOR - 5, HOR + 4):
        put(px_m, yy, WDK)

# Velero pesquero amarrado junto al muelle (x ~ 292)
bx_s, by_s = 294, HOR + 8
for dy in range(4):
    hw = 10 - dy * 2
    for dx in range(-hw, hw + 1):
        put(bx_s + dx, by_s + dy, WDK if dy > 1 else WD0)
for yy in range(by_s - 20, by_s):
    put(bx_s, yy, WDK)
for i in range(16):
    for dx in range(1, 13 - i * 12 // 16):
        put(bx_s + dx, by_s - 3 - i, PAL['sail'][0] if dx < 6 else PAL['sail'][1])

# Silueta de Gon pescando en la punta del muelle + caña
gx, gy = 344, HOR - 5
for dy in range(-5, 0):
    put(gx, gy + dy, '#12241a')
    put(gx + 1, gy + dy, '#183424')
disc(gx, gy - 6, 2, '#0c1c14')
for k in range(1, 18):
    put(gx + 2 + k, gy - 4 - k // 2, '#644428')
for k in range(1, 14):
    if k % 2 == 0:
        put(gx + 19, gy - 12 + k, '#c8e8f0')

# Faroles cálidos
def farol_puerto(x, y):
    for yy in range(10):
        put(x, y - yy, WDK)
    if ANIM:
        FAROLES.append([x, y - 10, 7])
        return
    put(x, y - 10, '#fff4cc')
    glow(x, y - 10, 8, '#ffb84c', 0.65)

farol_puerto(206, HOR - 11)
farol_puerto(258, HOR - 5)
farol_puerto(336, HOR - 5)

# 6. Reflejo de la bahía turquesa + olas + destellos
render_lago(lz, PAL['agua'], PAL['ola'], DESTELLOS, ANIM, mx=CX_ASTRO)

# 7. Frondas tropicales plumosas de palmera en la esquina superior izquierda
H_COLS = PAL['hoja']
def palma(bx, by, tx, ty, arc=14):
    steps = max(28, int(math.hypot(tx - bx, ty - by)))
    for i in range(steps + 1):
        t = i / steps
        cx = int(bx + (tx - bx) * t)
        cy = int(by + (ty - by) * t - arc * math.sin(t * 3.14))
        put(cx, cy, PAL['rama'][0])
        put(cx, cy + 1, PAL['rama'][1])
        # Hojuelas sueltas separadas cada 4 pasos (silueta plumosa real de palmera)
        if i > 4 and i % 4 == 0 and t < 0.94:
            fl = max(4, int(19 * math.sin(t * 2.8)))
            for dy in range(1, fl + 1):
                curv = int((dy * dy) * 0.055)
                c = H_COLS['l'] if dy < 4 else (H_COLS['c'] if dy < 10 else (H_COLS['m'] if dy < 15 else H_COLS['d']))
                put(cx + curv, cy + dy, c)
                if dy < fl - 2:
                    put(cx + curv + 1, cy + dy, H_COLS['d'] if dy > 6 else H_COLS['c'])
            if 0.15 < t < 0.78:
                fl_up = max(2, fl // 3)
                for dy in range(1, fl_up + 1):
                    put(cx + dy // 2, cy - dy, H_COLS['l'] if dy < fl_up else H_COLS['c'])

# Tronco / corona de palmera asomando en la esquina superior izquierda
for yy in range(0, 38):
    hw = max(3, 9 - yy // 5)
    for xx in range(0, hw):
        put(xx, yy, PAL['rama'][0] if (xx + yy // 3) % 2 else PAL['rama'][1])

palma(2, 16, 152, 34, arc=16)
palma(2, 22, 114, 76, arc=14)
palma(2, 8, 188, 14, arc=12)
palma(2, 30, 68, 122, arc=12)

# Helechos y flores Nen en las esquinas inferiores
for cx_s in range(0, 72):
    h_s = int(22 * math.cos(cx_s / 72 * 1.57))
    for yy in range(H - h_s, H):
        put(cx_s, yy, PAL['suelo'][0] if (cx_s + yy) % 3 else PAL['suelo'][1])
for cx_s in range(W - 64, W):
    h_s = int(18 * math.cos((W - 1 - cx_s) / 64 * 1.57))
    for yy in range(H - h_s, H):
        put(cx_s, yy, PAL['suelo'][2] if (cx_s + yy) % 3 else PAL['suelo'][3])

for fx in (16, 36, 54, W - 48, W - 26):
    for k in range(1, 16):
        put(fx + int(math.sin(k * 0.25) * 2), H - 8 - k, PAL['suelo'][3])
    if ANIM:
        RUNAS.append([fx + 1, H - 24])
    else:
        put(fx + 1, H - 24, PAL['nen'][1])
        glow(fx + 1, H - 24, 4, PAL['nen'][0], 0.5)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
             chimenea=CHIMENEA, destellos=DESTELLOS, barca=[344, HOR - 5], luna=[MX, MY, MR])
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
