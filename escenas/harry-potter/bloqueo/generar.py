#!/usr/bin/env python3
"""PixelZen Worlds - Harry Potter (Bloqueo): Anden 9 3/4 y Reliquias de la Muerte."""
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
random.seed(993)

PALETAS = {
    'noche': dict(
        sky=['#050612', '#0a0c20', '#121632', '#1b2046', '#262c5c', '#343a72', '#444a88', '#565c9e', '#6a70b2', '#7e84c4'],
        brick=('#542228', '#3c161c', '#240c10', '#703036'),
        iron=('#1a1e2a', '#2c3244', '#0c0e16'),
        floor=('#161622', '#202030', '#0c0c14'),
        gold=('#ffca48', '#fff4b8', '#b88224'),
        owl=('#eef4fc', '#b8c4d8'),
        vig=0.72,
        nube=['#222848', '#303860', '#404a78', '#525e8e', '#6672a4', '#1a203c'],
    ),
    'dorado': dict(
        sky=['#16102c', '#261a3e', '#3e2650', '#60345c', '#88445e', '#b0585a', '#d27254', '#ec9256', '#fac066', '#ffe08a'],
        brick=('#6c2a2c', '#4e1c20', '#2e1014', '#8e3c3c'),
        iron=('#26222c', '#3c3644', '#121018'),
        floor=('#221c24', '#2e2630', '#120e14'),
        gold=('#ffd250', '#fff6c2', '#c88c28'),
        owl=('#fff6f2', '#d2c2c6'),
        vig=0.80,
        nube=['#5c3252', '#7e4460', '#a45a66', '#ca7464', '#ea9666', '#462640'],
    ),
    'dia': dict(
        sky=['#2258a0', '#326eb6', '#4684ca', '#5e9cda', '#7ab4e6', '#98caf0', '#b6def4', '#d0ecf8', '#e6f4f8', '#f4f6ea'],
        brick=('#7e3436', '#5e2428', '#3a1418', '#a44848'),
        iron=('#2e3444', '#444c62', '#1a1e28'),
        floor=('#2c3040', '#3a4054', '#1a1c26'),
        gold=('#ffd04c', '#fff6c4', '#c48a24'),
        owl=('#ffffff', '#ced8e8'),
        vig=0.90,
        nube=['#ffffff', '#eef4fa', '#dce8f4', '#f6fafd', '#e4eef8', '#c8d8ec'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#ffd458', '#84d8ff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#ffe4b2', base='#fffcf2', sombra='#dcd6c0', crater='#bbb49e', crater_hi='#cfc8b4'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe49c', centro='#fffef2', borde='#ffc45c', rayo='#ffe298'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#fff4d8', '#bce8ff', '#b2b8e8'])

MX, MY, MR = 136, 74, 34
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#ffe4b2', base='#fffcf2', sombra='#dcd6c0', crater='#bbb49e', crater_hi='#cfc8b4')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 504, 174, 22, halo='#ffaa70', centro='#fff0dc', borde='#ff6646', rayo='#ff885e')
    else:
        dibuja_sol_estandar(lz, 496, 82, 22, halo='#ffe49c', centro='#fffef2', borde='#ffc45c', rayo='#ffe298')

NUBES_DEF = [
    (84, 38, 140, PAL['nube'][0], 2),
    (526, 52, 155, PAL['nube'][1], 2),
    (176, 118, 160, PAL['nube'][2], 3),
    (468, 126, 145, PAL['nube'][3], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# Muro bajo de ladrillo del anden de King's Cross cubriendo el horizonte (y=266..294)
BR0, BR1, BR2, BR_HI = PAL['brick']
IR0, IR1, IR2 = PAL['iron']
for y in range(266, 294):
    for x in range(W):
        if y < 269:
            put(x, y, IR1 if y == 266 else BR_HI)
        else:
            row_m = y // 5
            put(x, y, BR2 if (y % 5 == 0 or (x + (row_m % 2) * 6) % 12 == 0) else BR1)

# Plataforma de piedra de King's Cross (y=292..400)
FA, FB, FL = PAL['floor']
for y in range(292, H):
    ty = (y - 292) / float(H - 292)
    row_t = int((y - 292) / (3.0 + 5.0 * ty))
    for x in range(W):
        px_p = (x - 320) / (0.38 + 0.92 * ty)
        col_t = int(math.floor(px_p / 24.0))
        is_j = (abs(px_p - col_t * 24.0) < 1.2) or ((y - 292) % max(4, int(5 + 8 * ty)) == 0)
        put(x, y, FL if is_j else (FA if (col_t + row_t) % 2 == 0 else FB))

# Gran Arco de Ladrillo Victoriano de King's Cross anclado a la plataforma (x=220..420, base=326)
for x in range(224, 417):
    for y in range(180, 326):
        dx = x - 320
        # Hueco arqueado interior
        in_hole = abs(dx) < 58 and (y > 236 or (dx / 58.0) ** 2 + ((236 - y) / 48.0) ** 2 < 1.0)
        if in_hole:
            # Portal luminoso dorado dentro del arco 9 3/4
            d_c = math.hypot(dx / 58.0, (y - 266) / 60.0)
            put(x, y, mix('#100a14', PAL['gold'][0], max(0.0, (1.0 - d_c) * 0.42)))
        else:
            row_b = y // 6
            c = BR2 if (y % 6 == 0 or (x + (row_b % 2) * 7) % 14 == 0) else (BR_HI if dx < -30 else (BR0 if dx < 30 else BR1))
            put(x, y, c)

# Placa 9 3/4 y faroles dorados a ambos lados del arco
GD0, GD1, GD2 = PAL['gold']
for lx in (238, 402):
    for y in range(242, 326):
        put(lx, y, IR2)
    put(lx, 240, GD1)
    if ANIM:
        FAROLES.append([lx, 240, 12])
    else:
        glow(lx, 240, 10, GD0, 0.7)

# Simbolo brillante de las Reliquias de la Muerte en el centro del arco (cx=320, cy=254)
for k in range(36):
    # Triangulo vertical (Capa de Invisibilidad: vertice superior en 236, base en 272)
    t = k / 35.0
    lx_t = int(320 - 22 * (1 - t))
    rx_t = int(320 + 22 * (1 - t))
    yy_t = int(272 - 36 * t)
    put(lx_t, yy_t, GD1)
    put(rx_t, yy_t, GD1)
for dx in range(-22, 23):
    put(320 + dx, 272, GD1)
# Circulo inscrito (Piedra de la Resurreccion tangente a la base)
for a_deg in range(0, 360, 6):
    rad = math.radians(a_deg)
    put(int(320 + math.cos(rad) * 10), int(262 + math.sin(rad) * 10), GD0)
# Linea vertical central (Varita de Sauco)
for y in range(236, 273):
    put(320, y, GD1)

if ANIM:
    RUNAS.append([320, 260])
    FAROLES.append([320, 260, 14])
else:
    glow(320, 260, 14, GD0, 0.52)

# Baul de Hogwarts y lechuza blanca Hedwig en el suelo del anden (cx=292, by=346)
for x in range(274, 312):
    for y in range(330, 348):
        put(x, y, BR0 if y % 5 else GD2)
# Hedwig posada en la esquina del baul
OW0, OW1 = PAL['owl']
for dy in range(-10, 1):
    hw_o = 3 if dy > -8 else 2
    for dx in range(-hw_o, hw_o + 1):
        put(284 + dx, 330 + dy, OW0 if dx <= 0 else OW1)
put(283, 323, GD0)
put(285, 323, GD0)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
