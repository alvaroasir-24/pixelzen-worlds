#!/usr/bin/env python3
"""PixelZen Worlds - Demon Slayer (Bloqueo): Santuario de Glicinias y Katana Nichirin."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, exporta_salida, exporta_sprites_si_aplica, fbm, mix, render_cielo,
    render_estrellas, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1117)

PALETAS = {
    'noche': dict(
        sky=['#060412', '#0d0822', '#170f36', '#22174a', '#302060', '#402c78', '#523890', '#6648a6', '#7a5aba', '#906ece'],
        mont=('#201834', '#161026', '#0d0918'),
        stone=('#342e48', '#221d32', '#120e1c', '#524a6e'),
        torii=('#5c1622', '#821e2e', '#1a0a12'),
        wist=('#9248e8', '#c884ff', '#f0d8ff', '#582898'),
        blade=('#ff4828', '#ff9838', '#ffe888'),
        vig=0.74,
        nube=['#281e4a', '#362a62', '#463878', '#584890', '#6c5aa6', '#20183e'],
    ),
    'dorado': dict(
        sky=['#160a24', '#261238', '#3e1a4a', '#5e2454', '#823458', '#a84654', '#ca5e4e', '#e67e4e', '#f6a45c', '#ffc87e'],
        mont=('#3a2038', '#281428', '#180c18'),
        stone=('#4e3c4c', '#342634', '#1a121c', '#745a70'),
        torii=('#6e1824', '#9a2432', '#200a10'),
        wist=('#a654f0', '#d896ff', '#f6e2ff', '#6a30a8'),
        blade=('#ff4e28', '#ffa23e', '#fff098'),
        vig=0.82,
        nube=['#5c2c50', '#7e3c5e', '#a44e66', '#ca6866', '#ea8c68', '#482240'],
    ),
    'dia': dict(
        sky=['#224a94', '#3460ac', '#4878c2', '#6092d4', '#7aace4', '#98c4ee', '#b6daf4', '#d2e8f6', '#e6f2f6', '#f4f6ea'],
        mont=('#4e5274', '#3c405c', '#2a2e44'),
        stone=('#68667c', '#4a485a', '#2c2a38', '#8c8aa4'),
        torii=('#7e202c', '#a82c3a', '#260e14'),
        wist=('#9a54e8', '#cf94ff', '#f8e6ff', '#62349e'),
        blade=('#ff4828', '#ff9838', '#ffe888'),
        vig=0.90,
        nube=['#eef2fa', '#dce4f4', '#f8fafe', '#cedaf0', '#e4ecf8', '#becce6'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#b868ff', '#ff9e48'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 40, halo='#dfb8ff', base='#fbf4ff', sombra='#d0c4e8', crater='#ae9ecc', crater_hi='#c4b6e0'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe29c', centro='#fffef2', borde='#ffc05c', rayo='#ffe098'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#f0d8ff', '#ffdca8', '#b8b8f0'])

MX, MY, MR = 136, 74, 34
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#dfb8ff', base='#fbf4ff', sombra='#d0c4e8', crater='#ae9ecc', crater_hi='#c4b6e0')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 502, 174, 22, halo='#ffaa72', centro='#fff0de', borde='#ff6a48', rayo='#ff8a62')
    else:
        dibuja_sol_estandar(lz, 496, 82, 22, halo='#ffe29c', centro='#fffef2', borde='#ffc05c', rayo='#ffe098')

NUBES_DEF = [
    (84, 38, 140, PAL['nube'][0], 2),
    (526, 52, 155, PAL['nube'][1], 2),
    (176, 118, 160, PAL['nube'][2], 3),
    (468, 126, 145, PAL['nube'][3], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

rm = Ruido(1199)
M0, M1, M2 = PAL['mont']
for x in range(W):
    ridge = int(242 + 24 * fbm(rm, x * 0.015))
    for y in range(ridge, HOR + 24):
        put(x, y, mix(M0, M2, min(1.0, (y - ridge) / max(1, (HOR + 24 - ridge)))))

# Terraza y escalinata de piedra (y = 292..400)
ST_HI, ST_MD, ST_DK, ST_RIM = PAL['stone']
for y in range(292, H):
    for x in range(W):
        put(x, y, ST_DK if (y % 14 == 0 or (x + (y // 14) * 18) % 36 == 0) else (ST_MD if y < 340 else ST_HI))

# Gran Torii bermellon anclado sobre pedestales en y=318
TR0, TR1, TR_DK = PAL['torii']
for sx in (244, 396):
    # Pedestal de piedra
    for y in range(304, 322):
        for dx in range(-11, 12):
            put(sx + dx, y, ST_RIM if y < 307 else ST_DK)
    # Columna bermellon
    for y in range(182, 306):
        for dx in range(-7, 8):
            put(sx + dx, y, TR1 if dx < 0 else TR0)
# Dinteles superiores del Torii
for y in range(172, 184):
    hw = 114 - (y - 172) // 2
    for dx in range(-hw, hw + 1):
        put(320 + dx, y, TR_DK if y < 175 else TR1)
for y in range(198, 206):
    for dx in range(-96, 97):
        put(320 + dx, y, TR0 if y < 203 else TR_DK)

# Faroles de piedra japoneses (Toro) flanqueando el Torii (x=176, 464)
for lx_t in (176, 464):
    for y in range(280, 326):
        hw_l = 8 if y > 316 else (6 if y < 292 else 4)
        for dx in range(-hw_l, hw_l + 1):
            put(lx_t + dx, y, ST_HI if dx < 0 else ST_DK)
    put(lx_t, 286, '#fff0b8')
    if ANIM:
        FAROLES.append([lx_t, 286, 10])
    else:
        glow(lx_t, 286, 8, '#ff9840', 0.6)

# Arboles de glicinia nudosos a izquierda y derecha sosteniendo una pergola superior sobre el claro
tr_bark = '#1c1220'
tr_leaf = '#192a24'
for trunk_x, dir_t in ((18, 1), (W - 18, -1)):
    for y in range(138, 316):
        hw_t = 12 if y > 260 else (8 if y > 180 else 6)
        cx_t = trunk_x + dir_t * int(14 * math.sin((316 - y) / 140.0))
        for dx in range(-hw_t, hw_t + 1):
            put(cx_t + dx, y, tr_bark if dx < 0 else '#120b16')
    # Ramas gruesas arqueadas conectando hacia el centro superior (y=154..174)
    for bx_br in range(16, 250):
        px_b = bx_br if dir_t > 0 else W - 1 - bx_br
        by_b = int(156 + math.sin(bx_br * 0.024) * 6 + (bx_br / 250.0) * 14)
        for dy in range(-3, 5):
            put(px_b, by_b + dy, tr_bark if dy < 1 else tr_leaf)
            if (bx_br + dy) % 5 == 0:
                put(px_b, by_b - 5 + (dy % 3), tr_leaf)

# Racimos colgantes de Glicinias purpuras (naciendo directamente de ramas superiores o dinteles del Torii)
W0, W1, W2, W3 = PAL['wist']
for bx_w in range(24, W - 24, 18):
    if 244 < bx_w < 396:
        y_start = 182
        len_w = 18 + (bx_w % 12)
    else:
        dx_edge = bx_w if bx_w < W // 2 else (W - 1 - bx_w)
        y_start = int(158 + math.sin(dx_edge * 0.024) * 6 + (dx_edge / 250.0) * 14)
        len_w = 32 + (bx_w * 7) % 34
    for dy in range(len_w):
        t_w = dy / float(len_w)
        w_cl = max(1, int(3.4 * (1.0 - t_w * 0.82)))
        sway = int(math.sin(dy * 0.35 + bx_w) * 0.9)
        for dx in range(-w_cl, w_cl + 1):
            if abs(dx) == w_cl and dy % 3 == 0:
                continue
            c_w = W3 if (dx == 0 and dy % 5 == 0) else (W2 if dy % 2 == 0 and dx <= 0 else (W1 if dx <= 0 else W0))
            put(bx_w + dx + sway, y_start + dy, c_w)
    if bx_w % 36 == 24 and ANIM:
        RUNAS.append([bx_w, y_start + len_w // 2])

# Altar central de piedra y Katana Nichirin de la Llama apoyada en su soporte (cx=320, base=364)
for y in range(342, 366):
    hw = 28 + (y - 342) // 2
    for dx in range(-hw, hw + 1):
        put(320 + dx, y, ST_RIM if y < 345 else (ST_HI if dx < 0 else ST_DK))
B0, B1, B2 = PAL['blade']
for i in range(44):
    bx = 298 + i
    by = 340 - i // 4
    put(bx, by, B2 if i > 12 else TR1)
    put(bx, by + 1, B0 if i > 12 else '#18141e')
if ANIM:
    RUNAS.append([326, 332])
else:
    glow(326, 332, 7, B1, 0.5)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
