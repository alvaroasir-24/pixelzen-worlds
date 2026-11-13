#!/usr/bin/env python3
"""PixelZen Worlds - Stranger Things (Bloqueo): Reloj de Pie de Creel y Grieta Escarlata."""
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
random.seed(1989)

PALETAS = {
    'noche': dict(
        sky=['#05020c', '#0b0416', '#160722', '#240b30', '#34103c', '#481646', '#5e1e4e', '#762654', '#8e305a', '#a63c62'],
        wood=('#382422', '#241616', '#120a0c', '#543632'),
        floor=('#120c14', '#1b121c', '#09060a'),
        rift=('#ff2848', '#ff7086', '#ffd4de', '#540a18'),
        brass='#e6bc58',
        vig=0.72,
        nube=['#36142e', '#4c1b3a', '#642444', '#7e2e4c', '#983a54', '#281024'],
    ),
    'dorado': dict(
        sky=['#14081e', '#240c2c', '#3c123c', '#5a1a46', '#7c2448', '#a03246', '#c44644', '#e06646', '#f48c54', '#ffc076'],
        wood=('#4a2e28', '#301c1a', '#180c0c', '#6e463c'),
        floor=('#1c1218', '#281920', '#0e080c'),
        rift=('#ff2e4e', '#ff788e', '#ffd8e2', '#640e20'),
        brass='#f2ca62',
        vig=0.80,
        nube=['#662442', '#86304e', '#a83e56', '#ca545a', '#e8745e', '#4c1c36'],
    ),
    'dia': dict(
        sky=['#1e3a6e', '#2c4e86', '#3c649e', '#527cb4', '#6c96c8', '#88b0da', '#a6c8e8', '#c4dcef', '#dce8ee', '#eef0e6'],
        wood=('#5c423c', '#3e2c28', '#201614', '#806056'),
        floor=('#28222a', '#362e38', '#161218'),
        rift=('#ff3252', '#ff7c92', '#ffdce4', '#6e1628'),
        brass='#ecc45e',
        vig=0.88,
        nube=['#dde4f0', '#eef2f8', '#cbd6ea', '#f6f8fc', '#dfe8f4', '#b8c8de'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#ff3458', '#8c3eff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 36, halo='#ff98b4', base='#fff2f4', sombra='#d8bec6', crater='#b69aa4', crater_hi='#ccb2bc'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe09c', centro='#fffef2', borde='#ffb85c', rayo='#ffdc98'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffd4dc', '#c8e0ff', '#a896d8'])

MX, MY, MR = 138, 76, 34
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#ff98b4', base='#fff2f4', sombra='#d8bec6', crater='#b69aa4', crater_hi='#ccb2bc')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 504, 174, 22, halo='#ff9668', centro='#ffece0', borde='#ff5844', rayo='#ff8058')
    else:
        dibuja_sol_estandar(lz, 496, 82, 22, halo='#ffe09c', centro='#fffef2', borde='#ffb85c', rayo='#ffdc98')

NUBES_DEF = [
    (84, 38, 140, PAL['nube'][0], 2),
    (526, 52, 155, PAL['nube'][1], 2),
    (176, 118, 160, PAL['nube'][2], 3),
    (468, 126, 145, PAL['nube'][3], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# Suelo de madera oscura agrietado (y=294..400) y zocalo en ruinas en y=268..296
W0, W1, W2, W_HI = PAL['wood']
FA, FB, FL = PAL['floor']
R0, R1, R2, R3 = PAL['rift']
for x in range(W):
    for y in range(270, 296):
        put(x, y, W_HI if y < 273 else (W0 if (x % 16 != 0) else W2))
for y in range(296, H):
    for x in range(W):
        c = FL if (y % 12 == 0 or (x + (y // 12) * 18) % 44 == 0) else (FA if (x // 44) % 2 == 0 else FB)
        put(x, y, c)

# Gran grieta dentada de Vecna abriendose detras y debajo del reloj (x=210..430)
r_vr = Ruido(1993)
for y in range(168, 374):
    t_r = (y - 168) / float(374 - 168)
    w_cr = max(3, int(38 * math.sin(t_r * math.pi) * (0.60 + 0.40 * fbm(r_vr, y * 0.14))))
    jag = int(8 * (fbm(r_vr, y * 0.09 + 5.0) - 0.5))
    for dx in range(-w_cr, w_cr + 1):
        d = abs(dx) / max(1.0, w_cr)
        c_g = R2 if d < 0.28 else (R1 if d < 0.60 else (R0 if d < 0.88 else R3))
        put(320 + jag + dx, y, c_g)
    if y % 36 == 0:
        if ANIM:
            RUNAS.append([320 + jag, y])
        else:
            glow(320 + jag, y, 10, R0, 0.52)
# Rayos carmesi saliendo desde los flancos de la grieta
for side_c in (-1, 1):
    for ry_c in (210, 258, 308):
        for k in range(26):
            cx_f = 320 + side_c * (22 + k)
            cy_f = ry_c + int((k if ry_c < 260 else -k) * 0.35 + 2 * math.sin(k * 0.7))
            put(cx_f, cy_f, R1 if k < 14 else R0)

# RELOJ DE PIE DE LA CASA CREEL anclado firmemente en y=366 (cx=320, altura 160..366)
for y in range(160, 368):
    if y < 182:
        hw = int(8 + (y - 160) * 0.8)
    elif y < 228:
        hw = 22
    elif y < 332:
        hw = 17
    else:
        hw = 23
    for dx in range(-hw, hw + 1):
        c_c = W_HI if dx == -hw else (W0 if dx < 4 else W2)
        if abs(dx) == hw:
            c_c = '#080508'
        put(320 + dx, y, c_c)

# Esfera del reloj iluminada + manecillas + pendulo dorado
for dy in range(-12, 13):
    for dx in range(-12, 13):
        if dx * dx + dy * dy <= 144:
            put(320 + dx, 204 + dy, '#e8dcc0' if dx * dx + dy * dy <= 100 else PAL['brass'])
for k in range(8):
    put(320, 204 - k, '#140c10')
    put(320 + k // 2, 204 - k // 2, '#140c10')
# Caja cristal pendulo
for y in range(236, 322):
    for dx in range(-9, 10):
        put(320 + dx, y, '#100c14' if abs(dx) < 8 else PAL['brass'])
for y in range(242, 304):
    put(320, y, PAL['brass'])
disc(320, 306, 5, PAL['brass'])

if ANIM:
    FAROLES.append([320, 204, 14])
else:
    glow(320, 204, 12, R0, 0.4)

# Enredaderas organicas ramificadas brotando de la base del reloj
for side in (-1, 1):
    for branch, by_base in enumerate((364, 356, 372)):
        for i in range(44 - branch * 10):
            vx = 320 + side * (22 + i * 3)
            vy = by_base + int((fbm(r_vr, i * 0.18 + branch) - 0.5) * 14) - (i // 7 if branch == 1 else 0)
            put(vx, vy, R3 if i > 18 else R0)
            put(vx, vy + 1, '#09050a')
            if i % 9 == 4:
                put(vx, vy - 1, R1)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
