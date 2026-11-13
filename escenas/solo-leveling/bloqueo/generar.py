#!/usr/bin/env python3
"""PixelZen Worlds - Solo Leveling (Bloqueo): Porton Dimensional Rango S, Obeliscos y Dagas Sombra."""
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
random.seed(715)

PALETAS = {
    'noche': dict(
        sky=['#04030e', '#08061a', '#0f0b2c', '#181240', '#231a54', '#302268', '#3e2c7c', '#4e3690', '#5e42a4', '#7050b8'],
        stone=('#342d4c', '#201a32', '#100c1c', '#584a7c'),
        floor=('#0f0c1c', '#18132a', '#07050e'),
        portal=('#54e4ff', '#8a48ff', '#e4f8ff', '#2c2878'),
        dag=('Kasaka', '#7c48ff', '#c8a8ff', '#54e4ff'),
        shad_core='#07050e',
        shad_rim='#6c38d8',
        vig=0.72,
        nube=['#221a44', '#30245a', '#403070', '#523e88', '#664ea0', '#1a1436'],
    ),
    'dorado': dict(
        sky=['#140a24', '#221036', '#341648', '#4c1e56', '#6c285e', '#90345c', '#b44656', '#d66254', '#ef865c', '#ffb67a'],
        stone=('#4e364c', '#322034', '#180e1c', '#7c5674'),
        floor=('#180f20', '#24172e', '#0c0712'),
        portal=('#64e8ff', '#9e54ff', '#ebfaff', '#3c2e82'),
        dag=('Kasaka', '#9454ff', '#dbb8ff', '#68ecff'),
        shad_core='#0a0612',
        shad_rim='#8846e6',
        vig=0.80,
        nube=['#4e264c', '#6c325a', '#8e4062', '#b05666', '#d0746a', '#3c1e3e'],
    ),
    'dia': dict(
        sky=['#1a2d5e', '#263e76', '#365490', '#4a6ca8', '#6286be', '#7ea0d0', '#9abadd', '#b6d0e6', '#d0e2ec', '#e8eef2'],
        stone=('#5a5e78', '#3c4056', '#202232', '#8288a6'),
        floor=('#222638', '#2e334a', '#131522'),
        portal=('#54e4ff', '#8248ff', '#f0fcff', '#323884'),
        dag=('Kasaka', '#7c48ff', '#ceb2ff', '#54e4ff'),
        shad_core='#0a0814',
        shad_rim='#6a40c8',
        vig=0.88,
        nube=['#cad6ea', '#dce6f4', '#eef4fa', '#c0cee4', '#e4ecf6', '#b0c0d8'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#54d8ff', '#8a42ff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 42, halo='#9cb8ff', base='#eef6ff', sombra='#c0cee8', crater='#9aa8cc', crater_hi='#b2c0e0'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#d8c8ff', centro='#faf8ff', borde='#a8b0ff', rayo='#d0d8ff'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#d8f4ff', '#c8b8ff', '#8ea8e8'])

MX, MY, MR = 132, 74, 34
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#9cb8ff', base='#eef6ff', sombra='#c0cee8', crater='#9aa8cc', crater_hi='#b2c0e0')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 504, 174, 22, halo='#ff9878', centro='#fff0e2', borde='#f46658', rayo='#ff8468')
    else:
        dibuja_sol_estandar(lz, 496, 82, 22, halo='#dce4ff', centro='#ffffff', borde='#b8ccff', rayo='#d4e0ff')

NUBES_DEF = [
    (90, 40, 140, PAL['nube'][0], 2),
    (530, 56, 155, PAL['nube'][1], 2),
    (160, 118, 165, PAL['nube'][2], 3),
    (470, 128, 150, PAL['nube'][3], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# Horizonte montanoso + muralla baja del santuario dimensional anclada
rc = Ruido(755)
ST_HI, ST_MID, ST_DK, ST_RIM = PAL['stone']
for x in range(W):
    ridge = int(244 + 20 * fbm(rc, x * 0.016))
    for y in range(ridge, HOR + 28):
        t = (y - ridge) / max(1, (HOR + 28 - ridge))
        put(x, y, mix(ST_MID, ST_DK, min(1.0, t)))

# Almenas bajas tras la explanada (y=268..298)
for x in range(W):
    top_w = 270 if (x % 18) < 10 else 276
    for y in range(top_w, 298):
        put(x, y, ST_RIM if y == top_w else (ST_DK if y % 7 == 0 else ST_MID))

# Explanada ceremonial de losas oscuras (y = 296..400)
FA, FB, FL = PAL['floor']
for y in range(296, H):
    ty = (y - 296) / float(H - 296)
    row_t = int((y - 296) / (3.0 + 5.0 * ty))
    for x in range(W):
        px_p = (x - 320) / (0.38 + 0.92 * ty)
        col_t = int(math.floor(px_p / 24.0))
        is_j = (abs(px_p - col_t * 24.0) < 1.2) or ((y - 296) % max(4, int(5 + 8 * ty)) == 0)
        put(x, y, FL if is_j else (FA if (col_t + row_t) % 2 == 0 else FB))

# Sello de invocacion circular en la plataforma (cx=320, cy=358)
P0, P1, P2, P3 = PAL['portal']
for dy in range(-20, 21):
    for dx in range(-96, 97):
        dist = math.hypot(dx / 94.0, dy / 19.0)
        if 0.86 <= dist <= 1.0 or 0.56 <= dist <= 0.64:
            put(320 + dx, 358 + dy, P1 if dist < 0.7 else P0)
for rx_r, ry_r in ((244, 358), (396, 358), (282, 344), (358, 344), (282, 372), (358, 372)):
    if ANIM:
        RUNAS.append([rx_r, ry_r])
    else:
        glow(rx_r, ry_r, 5, P0, 0.65)

# Gran Porton Dimensional Rango S con base anclada al pedestal/suelo
for y in range(160, 316):
    for x in range(256, 385):
        nx = (x - 320) / 56.0
        ny = (y - 238) / 74.0
        d = math.hypot(nx, ny)
        if d <= 1.05:
            swirl = math.sin(d * 10.0 + math.atan2(ny, nx) * 3.0)
            if d > 0.88:
                c_p = P1 if dith(x, y, (1.05 - d) * 5.0) else P3
                over(x, y, c_p, 0.78)
            elif d > 0.62:
                put(x, y, P0 if swirl > 0 else P1)
            elif d > 0.28:
                put(x, y, P2 if swirl > 0.35 else P0)
            else:
                put(x, y, P2 if d < 0.14 else P0)

if ANIM:
    FAROLES.append([320, 238, 18])
else:
    glow(320, 238, 28, P0, 0.45)

# Dos Obeliscos Runicos con capiteles anclados firmemente en y=328
for ox in (218, 422):
    for y in range(146, 329):
        hw = max(2, int(12 - max(0, (176 - y)) * 0.28))
        if y > 312:
            hw += (y - 312) // 2
        for dx in range(-hw, hw + 1):
            c = ST_RIM if dx == -hw else (ST_HI if dx < 0 else ST_DK)
            if abs(dx) <= 1 and 188 <= y <= 298 and y % 12 < 6:
                c = P0 if y % 24 < 12 else P1
            put(ox + dx, y, c)
    if ANIM:
        RUNAS.append([ox, 210])
        RUNAS.append([ox, 260])

# Pedestal de obsidiana + Dagas Gemelas cruzadas de Sung Jin-Woo clavadas en la piedra
for y in range(340, 368):
    hw = 24 + (y - 340) // 3
    for dx in range(-hw, hw + 1):
        put(320 + dx, y, ST_HI if dx < -hw // 2 else (ST_MID if dx < hw // 2 else ST_DK))

for side, col_edge in ((-1, PAL['dag'][1]), (1, PAL['dag'][3])):
    for i in range(46):
        cx_d = 320 + side * int(i * 0.48)
        cy_d = 344 - i
        bw = 2 if i < 29 else (5 if i == 30 else 1)
        for dx in range(-bw, bw + 1):
            c_d = '#e6f6ff' if dx == 0 else col_edge
            if i > 31:
                c_d = ST_DK if abs(dx) > 0 else PAL['dag'][2]
            put(cx_d + dx, cy_d, c_d)
    if ANIM:
        RUNAS.append([320 + side * 12, 318])

# Dos Caballeros Sombra arrodillados (~22px alto, presencia nítida en el primer plano lateral)
spr_guardia = [
    '......KKKKK......',
    '.....KKKKKKK.....',
    '.....KKVKVKK.....',
    '......KKKKK......',
    '..KKKKKKKKKKKKK..',
    '.KKKKKKKKKKKKKKK.',
    'KKK.KKKKKKKKK.KKK',
    'KK..KKKKKKKKK..KK',
    '....KKKKKKKKK....',
    '...KKKKKKKKKKK...',
    '..KKKKKKKKKKKKK..',
    '..KKKKK...KKKKK..',
    '.KKKKK.....KKKKK.',
    '.KKKK.......KKKK.',
    '.KKKK.......KKKK.',
]
for gx, flip in ((144, False), (496, True)):
    for dx in range(-18, 19):
        for dy in range(-2, 3):
            if (dx / 18.0) ** 2 + (dy / 2.6) ** 2 <= 1.0:
                over(gx + dx, 368 + dy, P1, 0.58)
    # Lanza apoyada junto al caballero
    wx = gx + (-10 if flip else 10)
    for y in range(338, 369):
        put(wx, y, PAL['shad_rim'] if y < 346 else PAL['shad_core'])
    pinta_sprite(lz, gx, 368, spr_guardia, {'K': PAL['shad_core'], 'V': P0})
    if ANIM:
        RUNAS.append([gx, 356])
    else:
        glow(gx, 356, 4, P0, 0.5)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
