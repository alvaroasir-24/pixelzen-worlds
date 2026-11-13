#!/usr/bin/env python3
"""PixelZen Worlds - Spider-Man Miles Morales (Bloqueo): Azotea de Harlem sobre Manhattan."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, exporta_salida, exporta_sprites_si_aplica, fbm, mix, pinta_sprite, render_cielo,
    render_estrellas, render_lago, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1610)

PALETAS = {
    'noche': dict(
        sky=['#040614', '#080c24', '#101638', '#1a224e', '#263066', '#36427c', '#4a5692', '#646ea6', '#828aba', '#a4a6cc'],
        bldg=('#0b0e20', '#141a34', '#222b4c', '#344068'),
        roof=('#121422', '#202438', '#343a54', '#4e5676'),
        neon=('#ff2e4c', '#00e5ff', '#ffd840'), win='#ffd478',
        agua='#090d22', ola=('#64c8f0', '#38548a', '#162044'),
        vig=0.72, nube=['#222c52', '#303e6a', '#425282', '#56689a', '#6e80b2', '#1c2444'],
    ),
    'dorado': dict(
        sky=['#140824', '#240e38', '#3a164c', '#5a225c', '#803262', '#a8485e', '#ce6456', '#ea8652', '#faae60', '#ffd680'],
        bldg=('#1c1228', '#2a1c38', '#3e2a4e', '#563c68'),
        roof=('#1c1422', '#2e2236', '#483650', '#664e6e'),
        neon=('#ff3658', '#48f0ff', '#ffe066'), win='#ffca68',
        agua='#1e122c', ola=('#ffa270', '#845074', '#381e42'),
        vig=0.80, nube=['#5c2c52', '#823c5c', '#aa5260', '#d0725c', '#f09a64', '#4a2244'],
    ),
    'dia': dict(
        sky=['#1e529e', '#2e68b6', '#4482cc', '#609cde', '#80b6ec', '#a2cef4', '#c0e2f8', '#daf0fc', '#ecf6fc', '#f8faee'],
        bldg=('#22304c', '#324468', '#48608a', '#6480ae'),
        roof=('#242a3c', '#384058', '#525e7c', '#7282a4'),
        neon=('#ff3658', '#00d8f0', '#ffd440'), win='#fff09e',
        agua='#24548a', ola=('#c4ecfc', '#6ea2d0', '#365e8c'),
        vig=0.90, nube=['#ffffff', '#eef6fc', '#ffffff', '#e4f0fa', '#fafaf8', '#d8e8f4'],
    ),
}
PAL = PALETAS[FASE]
ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE)
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#a8c4ff', base='#f8f8f0', sombra='#bec6dc', crater='#9aa4be', crater_hi='#b2bcd4'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe49c', centro='#fffef4', borde='#ffc45c', rayo='#ffe088'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS)

MX, MY = 480, 74
CX_ASTRO = MX if FASE == 'noche' else (MX - 32 if FASE == 'dorado' else MX - 60)
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, CX_ASTRO, MY, 38, halo='#a8c4ff', base='#f8f8f0', sombra='#bec6dc', crater='#9aa4be', crater_hi='#b2bcd4')
    else:
        dibuja_sol_estandar(lz, CX_ASTRO, MY - (10 if FASE == 'dia' else -14), 22, halo='#ffe49c', centro='#fffef4', borde='#ffc45c', rayo='#ffe088')

render_nubes(lz, [(95, 58, 175, PAL['nube'][0], 3), (320, 48, 160, PAL['nube'][1], 3), (520, 114, 150, PAL['nube'][2], 2)], NUBES, ANIM)

B0, B1, B2, B3 = PAL['bldg']
# Skyline denso de Manhattan (izquierda a derecha) con retranqueos y malecón continuo en HOR
edificios = [
    (6, 168, 42, False), (52, 204, 36, False), (92, 134, 46, True), (144, 186, 40, False),
    (190, 106, 48, True), (244, 198, 38, False), (288, 156, 44, False), (338, 182, 36, False),
    (380, 92, 52, True), (438, 172, 42, False), (486, 196, 38, False), (530, 146, 46, True), (582, 184, 50, False),
]
for bx, top_y, bw, aguja in edificios:
    if aguja:
        # Retranqueo escalonado clásico Art-Deco bajo la aguja
        cw = max(14, bw - 14)
        cx_t = bx + (bw - cw) // 2
        for y in range(top_y - 12, top_y):
            for x in range(cx_t, cx_t + cw):
                put(x, y, B3 if x < cx_t + 3 else (B2 if x < cx_t + cw - 3 else B1))
    for y in range(top_y, HOR - 6):
        for x in range(bx, bx + bw):
            c = B3 if x < bx + 5 else (B2 if x < bx + bw // 2 else (B1 if x < bx + bw - 5 else B0))
            if (y - top_y) % 16 == 0:
                c = B0
            put(x, y, c)
    # Remate / cornisa superior
    for x in range(bx, bx + bw):
        put(x, top_y, B3)
    if aguja:
        ax = bx + bw // 2
        spire_top = top_y - 36
        for y in range(spire_top, top_y - 12):
            for dx in range(-1, 2):
                put(ax + dx, y, B2 if dx == 0 else B0)
        if ANIM:
            FAROLES.append([ax, spire_top - 1, 7])
        else:
            put(ax, spire_top - 1, PAL['neon'][0])
    for wy in range(top_y + 10, HOR - 14, 11):
        for wx in range(bx + 7, bx + bw - 7, 10):
            if (wx + wy) % 7 != 0:
                if ANIM and FASE != 'dia':
                    VENTANAS.append([wx, wy])
                else:
                    win_c = B1 if FASE == 'dia' else PAL['win']
                    for dy in range(4):
                        for dx in range(2):
                            put(wx + dx, wy + dy, win_c)

# Malecón continuo del río Hudson anclando todo el skyline (x = 0..W, y = HOR-6..HOR)
for y in range(HOR - 6, HOR + 1):
    for x in range(W):
        c = B3 if y == HOR - 6 else (B2 if (x // 6 + y) % 2 == 0 else B0)
        put(x, y, c)
for fx_m in range(18, W - 12, 34):
    put(fx_m, HOR - 7, B0)
    put(fx_m, HOR - 8, B2)
    if FASE != 'dia':
        put(fx_m, HOR - 9, PAL['win'])

# Reflejo urbano en el río Hudson antes de dibujar la cornisa del primer plano
render_lago(lz, PAL['agua'], PAL['ola'], DESTELLOS, ANIM, mx=CX_ASTRO, reflejo_cols=('#ffe49c', '#88d8ff'))

# Cornisa y azotea de piedra en primer plano (parte inferior y laterales para no tapar el lago central)
RF0, RF1, RF2, RF3 = PAL['roof']
for y in range(342, H):
    for x in range(W):
        put(x, y, RF3 if y < 347 else (RF2 if y < 354 else (RF1 if (x + y) % 11 else RF0)))
for y in range(298, 342):
    for x in range(24, 152):
        c = RF2 if x < 140 else RF0
        if y % 8 == 0 or (x + (y // 8) * 10) % 18 == 0:
            c = RF1 if x < 140 else RF0
        put(x, y, c)
for x in range(20, 156):
    for y in range(292, 299):
        put(x, y, RF3 if y < 295 else RF1)

# Miles Morales sentado/agachado en la esquina del pretil izquierdo vigilando Manhattan (Spider-Verse hoodie + Jordans)
MILES_PERCH = [
    "..............OOOOOOOO............",
    "............OOKKKKKKKKOO..........",
    "...........OKKKKKKKKKKKKO.........",
    "..........OKKKKKKKrKKKKKKO........",
    "..........OKWWKKKKrKKWWKKO........",
    "..........OKWWWKKKrKWWWKKO........",
    "...........OKWWKKKrKKWWKO.........",
    "............OKKKKKKKKKKO..........",
    "............OORRRRRRRROO..........",
    "..........OOORRRRRRRRRROOO........",
    ".........ORRRRRKKKKKKRRRRRO.......",
    "........ORRRRRKKRRRRKKRRRRRO......",
    ".......ORRRRKKKRRRRRRKKKRRRRO.....",
    "......ORRRKKKKKKRRRRKKKKKKRRRO....",
    ".....OSSOOKKKKKKKRRKKKKKKKOOSSO...",
    "....OSS..ORRKKKKKKKKKKKKRRO..SSO..",
    "...OO....ORRRKKKKKKKKKKRRRO...OO..",
    ".........ORRRRRKKKKKKRRRRRO.......",
    ".........OORRRRKKKKKKRRRROO.......",
    "..........OKKKKKKKKKKKKKKO........",
    ".........OKKKKKOOOOOOKKKKKO.......",
    "........OKKKKKO......OKKKKKO......",
    "........OKKKKO........OKKKKO......",
    ".......OKSSSKO........OKSSSKO.....",
    ".......OKKKKO..........OKKKKO.....",
    "......OKKKKO............OKKKKO....",
    ".....ORRRRRO............ORRRRRO...",
    ".....ORWWWRRO..........ORRRWWRO...",
    ".....OWWWWWWO..........OWWWWWWO...",
    "......OOOOOO............OOOOOO....",
]
w_mp = max(len(r) for r in MILES_PERCH)
MILES_PERCH = [r.ljust(w_mp, '.') for r in MILES_PERCH]
miles_cmap = {
    'O': '#090a10',
    'K': '#161826',
    'S': '#2b304c',
    'R': '#cc2034',
    'r': '#7c1424',
    'W': '#f2f7ff',
}
pinta_sprite(lz, 88, 297, MILES_PERCH, miles_cmap)
put(69, 282, PAL['neon'][1])
put(67, 284, PAL['neon'][2])
put(71, 285, PAL['neon'][1])
if not ANIM:
    glow(69, 283, 5, PAL['neon'][1], 0.55)
else:
    RUNAS.append([69, 283])

# Letrero neón con emblema de araña en el tejado derecho + depósito de agua neoyorquino con refuerzos
for rx_n in range(472, 518):
    for ry_n in range(304, 326):
        c_s = PAL['neon'][0] if ry_n in (304, 325) or rx_n in (472, 517) else '#0c0d18'
        put(rx_n, ry_n, c_s)
for px_p in (480, 510):
    for py_p in range(326, 343):
        put(px_p, py_p, RF0)
put(495, 315, PAL['neon'][0])
for dx_s, dy_s in ((-4, -2), (-2, -1), (2, -1), (4, -2), (-4, 2), (-2, 1), (2, 1), (4, 2), (0, -2), (0, 2)):
    put(495 + dx_s, 315 + dy_s, PAL['neon'][0])

for sx in (546, 586):
    for y in range(266, 343):
        for dx in range(4):
            put(sx + dx, y, RF0)
for y in range(272, 342):
    t_b = (y - 272) / 70.0
    bx_l = int(548 + 40 * t_b)
    bx_r = int(588 - 40 * t_b)
    put(bx_l, y, RF1)
    put(bx_l + 1, y, RF0)
    put(bx_r, y, RF1)
    put(bx_r + 1, y, RF0)
for y in range(222, 268):
    for x in range(538, 598):
        c_wt = RF3 if x < 554 else (RF2 if x < 582 else RF1)
        if y in (234, 250):
            c_wt = RF0
        put(x, y, c_wt)
for y in range(208, 224):
    hw = 34 * (y - 208) // 16
    for x in range(568 - hw, 568 + hw + 1):
        put(x, y, RF2 if x < 568 else RF0)
for fx, c_n in ((524, PAL['neon'][0]), (608, PAL['neon'][1]), (146, PAL['neon'][2])):
    if ANIM:
        FAROLES.append([fx, 290 if fx < 200 else 248, 9])
    else:
        put(fx, 290 if fx < 200 else 248, c_n)
        glow(fx, 290 if fx < 200 else 248, 7, c_n, 0.55)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS, destellos=DESTELLOS, luna=[MX, MY, 38])
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
