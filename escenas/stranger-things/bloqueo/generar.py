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
        sky=['#120308', '#1d050c', '#2c0813', '#3e0c1a', '#521121', '#691729', '#821e31', '#9c2839', '#b63544', '#cf4650'],
        wood=('#382422', '#241616', '#120a0c', '#543632'),
        floor=('#120c14', '#1b121c', '#09060a'),
        rift=('#ff2848', '#ff7086', '#ffd4de', '#540a18'),
        brass='#e6bc58',
        vig=0.72,
        nube=['#441220', '#5e1a2b', '#782235', '#922c3f', '#ad3848', '#300b17'],
    ),
    'dorado': dict(
        sky=['#1c050a', '#2e0810', '#460d18', '#621322', '#821b2a', '#a22730', '#c23836', '#dd523d', '#ef744b', '#fca062'],
        wood=('#4a2e28', '#301c1a', '#180c0c', '#6e463c'),
        floor=('#1c1218', '#281920', '#0e080c'),
        rift=('#ff2e4e', '#ff788e', '#ffd8e2', '#640e20'),
        brass='#f2ca62',
        vig=0.80,
        nube=['#621828', '#802234', '#9e2e3e', '#bc4048', '#d85c54', '#48111e'],
    ),
    'dia': dict(
        sky=['#381a28', '#4a2232', '#5e2b3d', '#753749', '#8d4555', '#a55662', '#bb6b71', '#cf8383', '#e09d98', '#eeb9af'],
        wood=('#5c423c', '#3e2c28', '#201614', '#806056'),
        floor=('#28222a', '#362e38', '#161218'),
        rift=('#ff3252', '#ff7c92', '#ffdce4', '#6e1628'),
        brass='#ecc45e',
        vig=0.88,
        nube=['#7a3c4a', '#964e5a', '#b0646e', '#c87e84', '#dda09e', '#622e3c'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#ff2848', '#a01c40'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 36, halo='#ff849c', base='#fff0f2', sombra='#d8b0bc', crater='#b68898', crater_hi='#cca2b0'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffb890', centro='#fff4ec', borde='#ff7a5c', rayo='#ffa880'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffd4dc', '#ffa8be', '#c88ea8'])

MX, MY, MR = 138, 64, 34
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#ff849c', base='#fff0f2', sombra='#d8b0bc', crater='#b68898', crater_hi='#cca2b0')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 504, 162, 22, halo='#ff8864', centro='#ffece0', borde='#ff4e40', rayo='#ff7054')
    else:
        dibuja_sol_estandar(lz, 496, 72, 22, halo='#ffb890', centro='#fff4ec', borde='#ff7a5c', rayo='#ffa880')

NUBES_DEF = [
    (84, 30, 140, PAL['nube'][0], 2),
    (526, 44, 155, PAL['nube'][1], 2),
    (176, 108, 160, PAL['nube'][2], 3),
    (468, 114, 145, PAL['nube'][3], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# Suelo de madera oscura agrietado (elevado: y=284..400) y zocalo en ruinas en y=258..286
W0, W1, W2, W_HI = PAL['wood']
FA, FB, FL = PAL['floor']
R0, R1, R2, R3 = PAL['rift']
for x in range(W):
    for y in range(258, 286):
        put(x, y, W_HI if y < 261 else (W0 if (x % 16 != 0) else W2))
for y in range(284, H):
    for x in range(W):
        c = FL if (y % 12 == 0 or (x + (y // 12) * 18) % 44 == 0) else (FA if (x // 44) % 2 == 0 else FB)
        put(x, y, c)

# Gran grieta dentada de Vecna abriendose detras y debajo del reloj (x=210..430)
r_vr = Ruido(1993)
for y in range(156, 362):
    t_r = (y - 156) / float(362 - 156)
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
    for ry_c in (198, 246, 296):
        for k in range(26):
            cx_f = 320 + side_c * (22 + k)
            cy_f = ry_c + int((k if ry_c < 248 else -k) * 0.35 + 2 * math.sin(k * 0.7))
            put(cx_f, cy_f, R1 if k < 14 else R0)

# RELOJ DE PIE DE LA CASA CREEL anclado firmemente en y=356 (cx=320, altura 150..356)
for y in range(150, 358):
    if y < 172:
        hw = int(8 + (y - 150) * 0.8)
    elif y < 218:
        hw = 22
    elif y < 322:
        hw = 17
    else:
        hw = 23
    for dx in range(-hw, hw + 1):
        c_c = W_HI if dx == -hw else (W0 if dx < 4 else W2)
        if abs(dx) == hw:
            c_c = '#080508'
        put(320 + dx, y, c_c)

# Esfera del reloj iluminada + manecillas + caja del pendulo (animado en JS cuando --anim)
for dy in range(-12, 13):
    for dx in range(-12, 13):
        if dx * dx + dy * dy <= 144:
            put(320 + dx, 194 + dy, '#e8dcc0' if dx * dx + dy * dy <= 100 else PAL['brass'])
for k in range(8):
    put(320, 194 - k, '#140c10')
    put(320 + k // 2, 194 - k // 2, '#140c10')
# Caja cristal pendulo
for y in range(226, 312):
    for dx in range(-9, 10):
        put(320 + dx, y, '#100c14' if abs(dx) < 8 else PAL['brass'])
if not ANIM:
    for y in range(232, 294):
        put(320, y, PAL['brass'])
    disc(320, 296, 5, PAL['brass'])

if ANIM:
    FAROLES.append([320, 194, 14])
else:
    glow(320, 194, 12, R0, 0.4)

# Enredaderas organicas ramificadas brotando de la base del reloj
for side in (-1, 1):
    for branch, by_base in enumerate((354, 346, 362)):
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
