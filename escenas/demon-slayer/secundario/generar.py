#!/usr/bin/env python3
"""PixelZen Worlds - Demon Slayer (Monitor 2): Aldea de los Herreros, Tokito vs Gyokko."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, exporta_salida, exporta_sprites_si_aplica, fbm, mix, pinta_sprite,
    render_cielo, render_estrellas, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1109)

PALETAS = {
    'noche': dict(
        sky=['#040b18', '#081528', '#0e223c', '#163050', '#204064', '#2c5278', '#3a668a', '#4c7c9c', '#6092ac', '#76a8b8'],
        mont=('#1a2c38', '#12202a', '#0a141c'),
        pine=('#0b1a1c', '#142a2a', '#061012'),
        ground=('#12201c', '#1b2e26', '#0a1412', '#263c30'),
        path=('#2c2522', '#3c322c', '#1c1716', '#4a3e36'),
        wall=('#504c48', '#34312e'),
        roof=('#1a2232', '#263248', '#101420'),
        wood=('#3e2a20', '#261812', '#563c2e'),
        rock=('#262e38', '#181e26', '#0e1218', '#3c4856'),
        mist=('#74f0dc', '#d8fff8'),
        vase=('#c6d2e4', '#304878', '#e0b248'),
        gyokko=('#92a89c', '#ff4878', '#54e4d4'),
        vig=0.74,
        nube=['#1e3652', '#2a4868', '#385c7e', '#487092', '#5c84a6', '#182c44'],
    ),
    'dorado': dict(
        sky=['#161430', '#262044', '#3c2c58', '#5c3c64', '#824e66', '#a86462', '#cc7c58', '#e89a56', '#f8bc64', '#ffdc86'],
        mont=('#3a2a3e', '#281c2c', '#18101c'),
        pine=('#162020', '#24342e', '#0c1412'),
        ground=('#24261c', '#323626', '#141610', '#444832'),
        path=('#4e3c30', '#664e3e', '#32261e', '#7c624e'),
        wall=('#7c6e62', '#584c44'),
        roof=('#24283c', '#363c56', '#161826'),
        wood=('#523426', '#341e16', '#6e4836'),
        rock=('#3a323e', '#26202a', '#141016', '#564a5c'),
        mist=('#88f4e0', '#e4fff8'),
        vase=('#dce4f0', '#445e96', '#ecc058'),
        gyokko=('#a8beb2', '#ff5484', '#68ecd8'),
        vig=0.82,
        nube=['#583856', '#784862', '#9e5c68', '#c47868', '#e4986a', '#442a44'],
    ),
    'dia': dict(
        sky=['#22589c', '#326cb0', '#4682c4', '#5e9ad6', '#7ab2e4', '#98c8ee', '#b6dcf4', '#d0eaf8', '#e4f2f8', '#f2f6ee'],
        mont=('#48687e', '#365268', '#263c4e'),
        pine=('#1c4232', '#2a5e46', '#10281e'),
        ground=('#223c28', '#305234', '#142618', '#426842'),
        path=('#6c5846', '#887058', '#4a3c30', '#a0866a'),
        wall=('#c4bab0', '#968c82'),
        roof=('#2e3c52', '#425674', '#1e2838'),
        wood=('#6c4836', '#482e22', '#8a5e46'),
        rock=('#4e5864', '#363e48', '#20262c', '#6e7a88'),
        mist=('#68ecd8', '#e8fffc'),
        vase=('#eef4fc', '#385490', '#ecc25c'),
        gyokko=('#b4c8bc', '#ff4878', '#54e4d4'),
        vig=0.90,
        nube=['#ffffff', '#eef6fa', '#dcf0f8', '#f6fbfe', '#e4f2fa', '#c8e0f0'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#54e8cc', '#78a8ff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#9ef4e4', base='#f2fffb', sombra='#c4e0dc', crater='#9cbcb8', crater_hi='#b4d2ce'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe49c', centro='#fffef2', borde='#ffc45c', rayo='#ffe298'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#d8fff6', '#bce8ff', '#a2b8e8'])

MX, MY, MR = 384, 62, 36
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#9ef4e4', base='#f2fffb', sombra='#c4e0dc', crater='#9cbcb8', crater_hi='#b4d2ce')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, MX + 16, 152, 22, halo='#ffaa70', centro='#fff0dc', borde='#ff6c48', rayo='#ff8c60')
    else:
        dibuja_sol_estandar(lz, MX - 40, 72, 22, halo='#ffe49c', centro='#fffef2', borde='#ffc45c', rayo='#ffe298')

NUBES_DEF = [
    (74, 24, 150, PAL['nube'][0], 2),
    (254, 36, 165, PAL['nube'][1], 3),
    (430, 22, 145, PAL['nube'][2], 2),
    (166, 98, 160, PAL['nube'][3], 3),
    (360, 96, 130, PAL['nube'][4], 2),
    (526, 194, 110, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 1. Valle montanoso de cedros rodeando la Aldea de los Herreros (elevado en general)
rm = Ruido(1189)
M0, M1, M2 = PAL['mont']
for x in range(W):
    ramp = max(0.0, min(1.0, (x - 420) / 80.0))
    dip_r = int(28 * (0.5 - 0.5 * math.cos(math.pi * ramp)))
    ridge = int(166 + 28 * fbm(rm, x * 0.013 + 2.0) + dip_r)
    ridge = min(236, ridge)
    for y in range(ridge, 248):
        t = (y - ridge) / max(1, 248 - ridge)
        put(x, y, mix(M0, M2, t * 0.85))

P0, P1, P2 = PAL['pine']


def cedro(px, by, h):
    for i in range(h):
        y = by - h + i
        hw = max(0, int(i * 0.25) - (2 if i % 6 == 5 else 0))
        for dx in range(-hw, hw + 1):
            put(px + dx, y, P1 if dx < 0 else (P0 if dx < hw // 2 else P2))


for cx_c, cy_c, ch_c in (
    (14, 246, 66), (42, 244, 58), (186, 244, 56), (218, 242, 50), (254, 244, 46),
    (316, 242, 44), (380, 244, 48), (446, 244, 46), (492, 246, 52), (534, 244, 58),
    (578, 246, 62), (618, 246, 66),
):
    cedro(cx_c, cy_c, ch_c)

# 2. Suelo del claro del bosque y sendero serpenteante desde la casa del herrero (y = 238..400, sin lago)
rx_g = Ruido(1231)
ry_g = Ruido(1249)
G0, G1, G2, G3 = PAL['ground']
PT0, PT1, PT2, PT3 = PAL['path']


def path_center_y(x):
    return 268 + 36 * (1.0 / (1.0 + math.exp(-(x - 245) / 55.0))) + 6 * math.sin(x * 0.022)


def path_half_w(x):
    t_s = max(0.0, min(1.0, (x - 134) / 36.0))
    return (14 * t_s) + 18 * max(0.0, min(1.0, (x - 160) / 340.0))


for y in range(238, H):
    for x in range(W):
        n2 = 0.5 * fbm(rx_g, x * 0.038) + 0.5 * fbm(ry_g, y * 0.05 + 4.0) + 0.12 * math.sin(x * 0.07) * math.cos(y * 0.08)
        c = G3 if n2 > 0.64 else (G1 if n2 > 0.48 else (G0 if n2 > 0.34 else G2))
        if x > 134:
            py_c = path_center_y(x)
            hw_p = max(1.0, path_half_w(x))
            d_p = abs(y - py_c) / hw_p
            if d_p < 1.15:
                edge_j = (n2 - 0.5) * 0.45
                if d_p + edge_j < 0.85:
                    c = PT3 if n2 > 0.65 else (PT1 if n2 > 0.48 else (PT0 if n2 > 0.30 else PT2))
                    if (x * 13 + y * 19) % 41 == 0 and d_p < 0.72:
                        c = PT2  # piedrecillas del sendero
                elif d_p + edge_j < 1.02 and dith(x, y, 0.55):
                    c = mix(c, PT0, 0.55)
        put(x, y, c)

# Piedras y arbustos enmarcando los bordes del sendero
RK0, RK1, RK2, RK_HI = PAL['rock']
WD0, WD1, WD_HI = PAL['wood']
for sx_r, sy_r, sr_r in ((206, 260, 5), (244, 306, 6), (348, 286, 5), (412, 336, 7), (534, 282, 6), (576, 330, 8)):
    for dy in range(-sr_r // 2, sr_r // 2 + 1):
        for dx in range(-sr_r, sr_r + 1):
            if (dx / float(sr_r)) ** 2 + (dy / float(max(2, sr_r // 2))) ** 2 <= 1.0:
                put(sx_r + dx, sy_r + dy, RK_HI if dy < 0 and dx < 0 else (RK0 if dx < sr_r // 2 else RK2))

# 3. CASA DEL HERRERO asentada junto al inicio del sendero (x=28..164, base y=262)
RF0, RF1, RF2 = PAL['roof']
WL0, WL1 = PAL['wall']
# Sombra de la casa sobre el suelo
for x in range(26, 168):
    for y in range(260, 267):
        over(x, y, '#06080a', 0.45)
# Zocalo de piedra
for x in range(34, 158):
    for y in range(254, 263):
        put(x, y, RK1 if y < 258 else RK2)
# Paredes tradicionales de madera y estuco
for x in range(38, 154):
    for y in range(210, 255):
        c = WL0 if (x % 16 != 0) else WD1
        if 222 <= y <= 242 and ((x - 48) % 26) in range(4, 14):
            c = '#ffb84d'
            if ANIM and (x - 48) % 26 == 8 and y == 232:
                VENTANAS.append([x, y])
        put(x, y, c)
# Porche de madera (engawa) dando al sendero
for x in range(148, 170):
    for y in range(250, 257):
        put(x, y, WD_HI if y < 253 else WD0)
for px_e in (152, 166):
    for y in range(256, 263):
        put(px_e, y, WD1)
# Tejado japones curvo irimoya sobre el taller
for dy in range(28):
    y = 184 + dy
    hw = 30 + int(dy * 1.55)
    for dx in range(-hw, hw + 1):
        put(96 + dx, y, RF1 if dy < 10 else (RF0 if dx % 4 else RF2))
# Chimenea de forja humeante
for y in range(174, 194):
    for dx in range(-3, 4):
        put(126 + dx, y, RK0 if dx < 0 else RK2)
CHIMENEA = [126, 173]

# Valla rustica y farol Toro junto al sendero frente a la casa del herrero (x=184, y=264)
for vx_f in (172, 192, 212):
    for y in range(248, 262):
        put(vx_f, y, WD0)
        put(vx_f + 1, y, WD1)
for x in range(170, 216):
    put(x, 251, WD_HI)
    put(x, 256, WD0)
for y in range(242, 266):
    hw_l = 5 if y > 261 else (4 if y < 248 else 2)
    for dx in range(-hw_l, hw_l + 1):
        put(184 + dx, y, RK_HI if dx < 0 else RK2)
if ANIM:
    FAROLES.append([184, 245, 10])
else:
    put(184, 245, '#fff0b8')
    glow(184, 245, 8, '#ff9840', 0.6)

# 4. Niebla mistica flotando sobre el sendero del bosque (Respiracion de la Niebla)
for mx_m, my_m, mw_m in ((230, 314, 110), (355, 322, 130), (520, 308, 110)):
    for dy in range(-5, 6):
        hw_m = int(mw_m * 0.5 * (1 - abs(dy) / 6.5))
        for dx in range(-hw_m, hw_m + 1):
            if dith(mx_m + dx, my_m + dy, 0.36 * (1 - abs(dx) / (hw_m + 1))):
                over(mx_m + dx, my_m + dy, PAL['mist'][0], 0.30)


# 5. MUICHIRO TOKITO (Pilar de la Niebla, cx=278, by=304 - sobre el sendero del bosque)
def dibuja_tokito(cx, by):
    M0, M1 = PAL['mist']
    skin = '#ecc6ae' if FASE != 'noche' else '#c8a89a'
    unif = '#141624'
    unif_hi = '#2a3048'
    hair = '#111522'
    belt = '#e6eaf2'

    # Sombra en el sendero
    for dx in range(-18, 19):
        for dy in range(-2, 3):
            if (dx / 18.0) ** 2 + (dy / 2.5) ** 2 <= 1.0:
                over(cx + dx, by + dy, '#06080c', 0.72)

    # Melena larga recta negra con puntas menta/turquesa fluyendo tras la espalda
    for t_h in range(18):
        hx = cx - 3 - t_h
        hy_top = by - 26 + int(t_h * 0.45 + math.sin(t_h * 0.32) * 0.9)
        bh_h = max(2, 7 - t_h // 4)
        for dy in range(bh_h):
            c_h = M1 if t_h > 12 else (M0 if t_h > 8 else hair)
            put(hx, hy_top + dy, c_h)

    # Sprite pixel-art detallado de Muichiro Tokito (29 filas: by-28..by)
    spr = [
        '.......HHHHHH.........',
        '......HHHHHHHH........',
        '.....HHHSSSSHHH.......',
        '.....HHSSESSESH.......',
        '......HSSSSSSH........',
        '......HUUUUUUH........',
        '.....UUUUUUUUUU.......',
        '....UUUUUUUUUUUU......',
        '...UUUUUUBBUUUUUUU....',
        '..UUUUUUUUBUUUUUUUU...',
        '..MMUUUUUBBUUUUUUSS...',
        '..MM.UUUUUUUUUU.......',
        '.....UUUUUUUUUU.......',
        '....UUUUUUUUUUUU......',
        '....UUUUUUUUUUUU......',
        '...UUUUUU..UUUUUU.....',
        '...UUUUU....UUUUU.....',
        '...UUUU......UUUU.....',
        '..UUUU........UUUU....',
        '..UUU..........UUU....',
        '..KKK..........KKK....',
        '..KKK..........KKK....',
        '..KKK..........KKK....',
        '.BBBB..........BBBB...',
        '.BBBB..........BBBB...',
        '......................',
        '......................',
        '......................',
        '......................',
    ]
    spr = [
        '.......HHHHHH.........',
        '......HHHHHHHH........',
        '.....HHHSSSSHHH.......',
        '.....HHSSESSESH.......',
        '......HSSSSSSH........',
        '......HUUUUUUH........',
        '.....UUUUUUUUUU.......',
        '....UUUUUUUUUUUU......',
        '...UUUUUUBBUUUUUU.....',
        '..UUUUUUUBBUUUUUUU....',
        '..MMUUUUUBBUUUUUUSS...',
        '..MM.UUUUUUUUUU.......',
        '.....UUUUUUUUUU.......',
        '....UUUUUUUUUUUU......',
        '....UUUUUUUUUUUU......',
        '...UUUUUU..UUUUUU.....',
        '...UUUUU....UUUUU.....',
        '...UUUU......UUUU.....',
        '...UUUU......UUUU.....',
        '..UUUU........UUUU....',
        '..UUU..........UUU....',
        '..KKK..........KKK....',
        '..KKK..........KKK....',
        '..KKK..........KKK....',
        '..KKK..........KKK....',
        '.NNNN..........NNNN...',
        '.NNNN..........NNNN...',
        'NNNNNN........NNNNNN..',
        '......................',
    ]
    cmap = {
        'H': hair,
        'S': skin,
        'E': M1,
        'U': unif,
        'B': belt,
        'M': M0,
        'K': '#dfe4ee',
        'N': '#181a24',
    }
    pinta_sprite(lz, cx, by, spr, cmap)
    # Sombras/pliegues sutiles en el uniforme holgado de Tokito
    for ux, uy in ((-3, -15), (0, -14), (2, -16), (-2, -20)):
        put(cx + ux, by + uy, unif_hi)

    # Tsuba y katana Nichirin blanca/turquesa extendida hacia Gyokko
    put(cx + 8, by - 19, '#d8e4ec')
    put(cx + 8, by - 18, '#d8e4ec')
    for s in range(20):
        put(cx + 9 + s, by - 18 - s // 4, M1 if s > 10 else '#e4f6f8')

    # Estela amplia de la Respiracion de la Niebla naciendo de la hoja hacia Gyokko
    for k in range(44):
        u = k / 43.0
        sx = cx + 24 + int(u * 56)
        sy = by - 22 + int(math.sin(u * 4.6) * 10 - u * 4)
        r_m = 3 if 0.14 < u < 0.84 else 2
        for dy in range(-r_m, r_m + 1):
            for dx in range(-r_m, r_m + 1):
                if dx * dx + dy * dy <= r_m * r_m:
                    put(sx + dx, sy + dy, M1 if abs(dx) + abs(dy) <= 1 else M0)
        if k % 8 == 0:
            if ANIM:
                RUNAS.append([sx, sy])
            else:
                glow(sx, sy, 6, M0, 0.5)


dibuja_tokito(278, 304)


# 6. GYOKKO Y SU JARRON DEMONIACO (cx=468, by=308 - asentado en el sendero)
def dibuja_gyokko(cx, by):
    V_W, V_B, V_G = PAL['vase']
    G_S, G_E, G_W = PAL['gyokko']
    G_DK = '#566860' if FASE == 'noche' else '#74887c'

    # Sombra bajo el jarron en el sendero
    for dx in range(-18, 19):
        for dy in range(-2, 3):
            if (dx / 18.0) ** 2 + (dy / 2.5) ** 2 <= 1.0:
                over(cx + dx, by + dy, '#06080c', 0.72)

    # Tentaculos acuaticos demoniacos alrededor del jarron
    for side in (-1, 1):
        for t in range(32):
            u = t / 31.0
            tx = int(cx + side * (13 + t * 1.0))
            ty = int(by - 14 - math.sin(u * 3.8) * 15 - u * 10)
            r_t = 3 if u < 0.45 else (2 if u < 0.8 else 1)
            for dy in range(-r_t, r_t + 1):
                for dx in range(-r_t, r_t + 1):
                    if dx * dx + dy * dy <= r_t * r_t:
                        put(tx + dx, ty + dy, G_W if (dx + dy) == 0 else '#14222c')
        if ANIM:
            RUNAS.append([cx + side * 28, by - 24])

    # Jarron grande de porcelana blanca, azul y oro apoyado firme en by
    for dy in range(-21, 1):
        u = (dy + 21) / 21.0
        hw_v = int(7 + 9 * math.sin(u * math.pi * 0.85))
        if dy < -18:
            hw_v = 9  # boca acampanada
        for dx in range(-hw_v, hw_v + 1):
            if dy in (-19, -11, -3):
                c = V_G
            elif dx > hw_v // 3:
                c = V_B
            elif dy in (-15, -7) and abs(dx) % 4 < 2:
                c = V_B
            else:
                c = V_W
            put(cx + dx, by + dy, c)

    # Torso palido grotesco de Gyokko con multiples bracitos y ojos verticales (20 filas sobre el jarron)
    spr_g = [
        '.....DDDDDDDD.....',
        '....DDSSSSSSDD....',
        '....DSSSESSSSD....',  # Ojo vertical superior
        '....DSMMSSMMSSD...',
        '....DSSSSSSSSSD...',  # Bocas verdes en lugar de ojos
        '.....SSSESSSSS....',  # Ojo en la barbilla
        '....SSSSSSSSSS....',
        '..SSSDSSSSSSDSSS..',
        '.SS..SSSSSSSS..SS.',
        '...SS.SSSSSS.SS...',
        '..SS..SSSSSS..SS..',
        '......DDDDDD......',
        '.....DDDDDDDD.....',
        '......DDDDDD......',
        '......SSSSSS......',
        '.......SSSS.......',
    ]
    cmap_g = {
        'S': G_S,
        'D': G_DK,
        'E': G_E,
        'M': '#52d484',
    }
    pinta_sprite(lz, cx, by - 21, spr_g, cmap_g)
    if ANIM:
        RUNAS.append([cx, by - 34])
        FAROLES.append([cx, by - 32, 11])
    else:
        glow(cx, by - 33, 7, G_E, 0.55)


dibuja_gyokko(468, 308)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
