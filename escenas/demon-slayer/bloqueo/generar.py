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

MX, MY, MR = 136, 62, 34
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#dfb8ff', base='#fbf4ff', sombra='#d0c4e8', crater='#ae9ecc', crater_hi='#c4b6e0')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 502, 148, 22, halo='#ffaa72', centro='#fff0de', borde='#ff6a48', rayo='#ff8a62')
    else:
        dibuja_sol_estandar(lz, 496, 68, 22, halo='#ffe29c', centro='#fffef2', borde='#ffc05c', rayo='#ffe098')

NUBES_DEF = [
    (84, 24, 140, PAL['nube'][0], 2),
    (526, 36, 155, PAL['nube'][1], 2),
    (176, 98, 160, PAL['nube'][2], 3),
    (468, 104, 145, PAL['nube'][3], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

rm = Ruido(1199)
M0, M1, M2 = PAL['mont']
for x in range(W):
    ridge = int(196 + 22 * fbm(rm, x * 0.015))
    for y in range(ridge, 254):
        put(x, y, mix(M0, M2, min(1.0, (y - ridge) / max(1, (254 - ridge)))))

# Terraza y escalinata de piedra (y = 246..400)
ST_HI, ST_MD, ST_DK, ST_RIM = PAL['stone']
for y in range(246, H):
    for x in range(W):
        put(x, y, ST_DK if (y % 14 == 0 or (x + (y // 14) * 18) % 36 == 0) else (ST_MD if y < 296 else ST_HI))

# Gran Torii bermellon anclado sobre pedestales en y=258..276
TR0, TR1, TR_DK = PAL['torii']
for sx in (244, 396):
    # Pedestal de piedra
    for y in range(258, 276):
        for dx in range(-11, 12):
            put(sx + dx, y, ST_RIM if y < 261 else ST_DK)
    # Columna bermellon
    for y in range(136, 260):
        for dx in range(-7, 8):
            put(sx + dx, y, TR1 if dx < 0 else TR0)
# Dinteles superiores del Torii
for y in range(126, 138):
    hw = 114 - (y - 126) // 2
    for dx in range(-hw, hw + 1):
        put(320 + dx, y, TR_DK if y < 129 else TR1)
for y in range(152, 160):
    for dx in range(-96, 97):
        put(320 + dx, y, TR0 if y < 157 else TR_DK)

# Faroles de piedra japoneses (Toro) flanqueando el Torii (x=176, 464)
for lx_t in (176, 464):
    for y in range(234, 280):
        hw_l = 8 if y > 270 else (6 if y < 246 else 4)
        for dx in range(-hw_l, hw_l + 1):
            put(lx_t + dx, y, ST_HI if dx < 0 else ST_DK)
    put(lx_t, 240, '#fff0b8')
    if ANIM:
        FAROLES.append([lx_t, 240, 10])
    else:
        glow(lx_t, 240, 8, '#ff9840', 0.6)

# Arboles de glicinia organicos a izquierda y derecha con ramas curvas sobre el claro
tr_bark = '#1c1220'
tr_bark_hi = '#2f2036'
tr_leaf = '#192a24'
tr_leaf_hi = '#263d34'
rng_w = random.Random(1129)
W0, W1, W2, W3 = PAL['wist']

for trunk_x, dir_t in ((14, 1), (W - 14, -1)):
    pts_tr = [
        (trunk_x - dir_t * 4, 272),
        (trunk_x + dir_t * 4, 214),
        (trunk_x + dir_t * 18, 160),
        (trunk_x + dir_t * 58, 122),
        (trunk_x + dir_t * 128, 108),
        (trunk_x + dir_t * 204, 118),
    ]
    lz.rama(pts_tr, 9, 2.2, tr_bark, tr_bark_hi)
    # Rama secundaria arqueada mas alta
    pts_b2 = [
        (trunk_x + dir_t * 36, 140),
        (trunk_x + dir_t * 94, 102),
        (trunk_x + dir_t * 164, 102),
    ]
    lz.rama(pts_b2, 5, 1.5, tr_bark, tr_bark_hi)
    # Follaje organico denso en la copa de las glicinias
    for fx_c, fy_c, fr_c in (
        (trunk_x + dir_t * 38, 122, 16),
        (trunk_x + dir_t * 68, 110, 17),
        (trunk_x + dir_t * 98, 100, 20),
        (trunk_x + dir_t * 132, 100, 19),
        (trunk_x + dir_t * 164, 106, 17),
        (trunk_x + dir_t * 194, 116, 14),
    ):
        for _ in range(20):
            ox = rng_w.randint(-fr_c // 2, fr_c // 2)
            oy = rng_w.randint(-fr_c // 3, fr_c // 3)
            rr = rng_w.randint(4, 7)
            for dy in range(-rr, rr + 1):
                for dx in range(-rr, rr + 1):
                    d_f = math.hypot(dx, dy)
                    if d_f <= rr * 0.72 or (d_f <= rr and dith(fx_c + ox + dx, fy_c + oy + dy, 0.55)):
                        put(fx_c + ox + dx, fy_c + oy + dy, tr_leaf_hi if (oy + dy) < -2 else tr_leaf)
    # Raices y alcorque de piedra donde nacen los troncos sobre la terraza
    bx_root = trunk_x - dir_t * 4
    for y in range(268, 283):
        hw_rt = 15 + (y - 268) // 2
        for dx in range(-hw_rt, hw_rt + 1):
            put(bx_root + dx, y, ST_RIM if y < 271 else (ST_HI if dx < 0 else ST_DK))

# Racimos colgantes naturales de Glicinias purpuras (longitudes y separaciones organicas)
racimos = []
for side_x, dir_t in ((22, 1), (W - 22, -1)):
    x_cur = side_x
    while (x_cur < 236) if dir_t > 0 else (x_cur > W - 236):
        dx_edge = abs(x_cur - side_x)
        y_start = int(120 - 14 * math.sin(dx_edge / 130.0 * math.pi * 0.65) + rng_w.randint(-4, 6))
        len_w = rng_w.randint(24, 66) if dx_edge < 150 else rng_w.randint(18, 42)
        racimos.append((x_cur, y_start, len_w))
        x_cur += dir_t * rng_w.randint(11, 18)

# Pequenos racimos en el dintel del Torii
for bx_t in range(254, 388, 19):
    racimos.append((bx_t + rng_w.randint(-2, 2), 138, rng_w.randint(14, 26)))

for idx_r, (bx_w, y_start, len_w) in enumerate(racimos):
    for dy in range(len_w):
        t_w = dy / float(len_w)
        w_cl = max(1, int(3.2 * (1.0 - t_w * 0.80)))
        sway = int(math.sin(dy * 0.30 + bx_w * 0.2) * 1.1)
        for dx in range(-w_cl, w_cl + 1):
            if abs(dx) == w_cl and (dy + idx_r) % 3 == 0:
                continue
            c_w = W3 if (dx == 0 and dy % 5 == 0) else (W2 if dy % 2 == 0 and dx <= 0 else (W1 if dx <= 0 else W0))
            put(bx_w + dx + sway, y_start + dy, c_w)
    if idx_r % 3 == 0 and ANIM:
        RUNAS.append([bx_w, y_start + len_w // 2])

# Altar central de piedra (cx=320, base=316) y Katana Nichirin de la Llama sobre soporte
for y in range(292, 316):
    hw = 30 + (y - 292) // 2
    for dx in range(-hw, hw + 1):
        put(320 + dx, y, ST_RIM if y < 295 else (ST_HI if dx < 0 else ST_DK))
# Soportes del katana-kake sobre el altar
for sx_k in (304, 336):
    for y in range(286, 293):
        put(sx_k, y, TR_DK)
        put(sx_k + 1, y, TR0)
B0, B1, B2 = PAL['blade']
# Empunadura (tsuka), guarda (tsuba) y hoja llameante Nichirin
for i in range(50):
    bx = 294 + i
    by = 288 - i // 5
    if i < 12:
        put(bx, by, '#201826' if i % 3 else TR1)
        put(bx, by + 1, '#120d16')
    elif i == 12:
        for gd in range(-2, 3):
            put(bx, by + gd, B2)
    else:
        put(bx, by, B2 if i > 36 else B1)
        put(bx, by + 1, B0)
if ANIM:
    RUNAS.append([326, 282])
else:
    glow(326, 282, 8, B1, 0.55)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
