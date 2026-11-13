#!/usr/bin/env python3
"""PixelZen Worlds - Stranger Things (Monitor 2): Bosque de Hawkins, Cabana Byers y Demogorgon."""
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
random.seed(1986)

PALETAS = {
    'noche': dict(
        sky=['#040610', '#090d1c', '#10162c', '#18203e', '#222a50', '#2e3662', '#3c4476', '#4c548a', '#5e649e', '#7276b0'],
        pine=('#0b141a', '#142228', '#050a0e'),
        ground=('#121a18', '#1b2620', '#0a0f0e', '#2a362a'),
        cabin=('#322624', '#221818', '#140e10', '#4a3834'),
        demo=('#08060c', '#1e1622', '#ff3458', '#ffa8b8'),
        neon=('#ff2e6a', '#48e8ff', '#ffd448', '#52ff88'),
        vig=0.74,
        nube=['#1e2646', '#2a345c', '#384472', '#485488', '#5a669e', '#18203c'],
    ),
    'dorado': dict(
        sky=['#140c24', '#241436', '#3a1c46', '#582850', '#7c3654', '#a24652', '#c45c4c', '#e07a4e', '#f49e5c', '#ffc67c'],
        pine=('#141818', '#222826', '#0a0e0c'),
        ground=('#221c18', '#322822', '#120e0c', '#463830'),
        cabin=('#4a342c', '#32221e', '#1c1210', '#6a4c3e'),
        demo=('#0a060e', '#281826', '#ff3c62', '#ffb4c4'),
        neon=('#ff3672', '#58ecff', '#ffdc54', '#5eff94'),
        vig=0.82,
        nube=['#582c4e', '#783c5c', '#9e4e64', '#c26866', '#e28868', '#44223e'],
    ),
    'dia': dict(
        sky=['#224c8c', '#3260a2', '#4676b8', '#5e8ece', '#78a8e0', '#96c0ea', '#b4d6f0', '#cee6f4', '#e4eff2', '#f2f4ea'],
        pine=('#1a3426', '#284c36', '#102016'),
        ground=('#283c26', '#385232', '#182418', '#4c6a42'),
        cabin=('#644c40', '#46342c', '#2a1e1a', '#866858'),
        demo=('#0a0810', '#241c2c', '#ff3258', '#ffb0c0'),
        neon=('#ff2e6a', '#48e8ff', '#ffd448', '#52ff88'),
        vig=0.90,
        nube=['#eef2fa', '#dce6f4', '#f8fbfe', '#cedaf0', '#e4eef8', '#becce6'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#78a8ff', '#ff3858'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#c2d4ff', base='#f4f8ff', sombra='#c8d2ec', crater='#a4aec8', crater_hi='#bcc4dc'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe29c', centro='#fffef2', borde='#ffc05c', rayo='#ffe098'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#e4f0ff', '#ffc4d4', '#a8b8e8'])

MX, MY, MR = 304, 72, 36
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#c2d4ff', base='#f4f8ff', sombra='#c8d2ec', crater='#a4aec8', crater_hi='#bcc4dc')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 332, 174, 22, halo='#ffaa70', centro='#fff0de', borde='#ff6646', rayo='#ff885e')
    else:
        dibuja_sol_estandar(lz, 292, 82, 22, halo='#ffe29c', centro='#fffef2', borde='#ffc05c', rayo='#ffe098')

NUBES_DEF = [
    (74, 36, 145, PAL['nube'][0], 2),
    (265, 48, 165, PAL['nube'][1], 3),
    (430, 32, 145, PAL['nube'][2], 2),
    (165, 118, 160, PAL['nube'][3], 3),
    (360, 114, 130, PAL['nube'][4], 2),
    (526, 224, 110, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 1. Colinas boscosas y pinos de Mirkwood (y=248..292 para evitar corte plano en HOR=280)
r_h = Ruido(1991)
for x in range(W):
    ramp = max(0.0, min(1.0, (x - 420) / 80.0))
    dip_r = int(20 * (0.5 - 0.5 * math.cos(math.pi * ramp)))
    ridge = int(244 + 16 * fbm(r_h, x * 0.015) + dip_r)
    for y in range(ridge, 294):
        put(x, y, mix(PAL['pine'][2], PAL['ground'][2], min(1.0, (y - ridge) / 36.0)))

P0, P1, P2 = PAL['pine']


def pino(px, by, h):
    for i in range(h):
        y = by - h + i
        hw = max(0, int(i * 0.28) - (2 if i % 5 == 4 else 0))
        for dx in range(-hw, hw + 1):
            put(px + dx, y, P1 if dx < 0 else (P0 if dx < hw // 2 else P2))


for px_p, py_p, ph_p in ((18, 300, 74), (48, 298, 64), (192, 296, 58), (226, 298, 66), (264, 296, 56), (308, 298, 60), (356, 296, 54), (488, 298, 46), (528, 298, 54), (576, 298, 60), (614, 298, 68)):
    pino(px_p, py_p, ph_p)

# 2. Claro del bosque con ruido organico 2D (y=288..400)
rx_n, ry_n = Ruido(1987), Ruido(1988)
G0, G1, G2, G3 = PAL['ground']
for y in range(288, H):
    for x in range(W):
        n2 = 0.5 * fbm(rx_n, x * 0.036) + 0.5 * fbm(ry_n, y * 0.048 + 5.0) + 0.14 * math.sin(x * 0.06) * math.cos(y * 0.07)
        c = G3 if n2 > 0.62 else (G1 if n2 > 0.46 else (G0 if n2 > 0.34 else G2))
        if y > 350 and n2 > 0.69 and (x % 5 == 0 and y % 5 == 0):
            c = mix(c, '#ff3458', 0.45)
        put(x, y, c)

# 3. CABANA BYERS anclada firme a la izquierda (x=44..186, base y=336) con luces navideñas multicolor
CB0, CB1, CB2, CB_HI = PAL['cabin']
for x in range(54, 176):
    for y in range(280, 338):
        put(x, y, CB_HI if y % 4 == 0 else (CB0 if x < 140 else CB1))
# Tejado de madera
for dy in range(26):
    y = 254 + dy
    hw = 12 + int(dy * 2.2)
    for dx in range(-hw, hw + 1):
        put(115 + dx, y, CB2 if dx > 0 else CB1)
# Chimenea de ladrillo
for y in range(242, 266):
    for dx in range(-4, 5):
        put(82 + dx, y, CB_HI if dx < 0 else CB2)
CHIMENEA = [82, 241]

# Porche y gran ventana con guirnalda de luces navideñas del alfabeto
for x in range(72, 158):
    for y in range(296, 322):
        put(x, y, '#1c1414' if (x % 18 == 0 or y == 296 or y == 321) else '#3e2e20')
for i, col_l in enumerate(PAL['neon'] * 2):
    lx_n = 78 + i * 10
    ly_n = 304 + (i % 2) * 5
    put(lx_n, ly_n, col_l)
    put(lx_n + 1, ly_n, col_l)
    if ANIM:
        RUNAS.append([lx_n, ly_n])
    else:
        glow(lx_n, ly_n, 4, col_l, 0.5)
# Farol en porche
if ANIM:
    FAROLES.append([166, 304, 11])
else:
    put(166, 304, '#fff2be')
    glow(166, 304, 10, '#ff9840', 0.6)


# 4. EL DEMOGORGON en silueta sombreada al claro del bosque (cx=418, by=354)
def dibuja_demogorgon(cx, by):
    DM_C, DM_R, DM_M, DM_T = PAL['demo']

    # Sombra/enredaderas del Upside Down bajo sus pies
    for dx in range(-22, 23):
        for dy in range(-2, 4):
            if (dx / 22.0) ** 2 + (dy / 3.2) ** 2 <= 1.0:
                over(cx + dx, by + dy, '#5a0e22' if abs(dx) > 14 else DM_C, 0.78)

    # Silueta humanoide larga y delgada de garras afiladas
    spr = [
        '........KKKKKKKKKK........',
        '.......KKKKKKKKKKKK.......',
        '.......KKMMMMMMMMKK.......',
        '.......KKKKKKKKKKKK.......',
        '........KKKKKKKKKK........',
        '.....KKKKKKKKKKKKKKKK.....',
        '...KKKKKKKKKKKKKKKKKKKK...',
        '..KKKK..KKKKKKKKKK..KKKK..',
        '.KKK....KKKKKKKKKK....KKK.',
        'KKK......KKKKKKKK......KKK',
        'KK.......KKKKKKKK.......KK',
        'K.........KKKKKK.........K',
        '..........KKKKKK..........',
        '.........KKKKKKKK.........',
        '........KKKK..KKKK........',
        '.......KKKK....KKKK.......',
        '.......KKK......KKK.......',
        '......KKK........KKK......',
        '......KKK........KKK......',
        '.....KKK..........KKK.....',
        '....KKK............KKK....',
    ]
    pinta_sprite(lz, cx, by, spr, {'K': DM_C, 'M': DM_M})

    # Petalos abiertos dentados caracteristicos del Demogorgon coronando la cabeza
    hy_c = by - len(spr) + 2
    for ang_deg in (-140, -90, -40, 20, 160):
        rad = math.radians(ang_deg)
        for t_p in range(3, 12):
            px_d = int(cx + math.cos(rad) * t_p)
            py_d = int(hy_c + math.sin(rad) * t_p)
            w_p = 2 if t_p < 8 else 1
            for dy in range(-w_p + 1, w_p):
                for dx in range(-w_p + 1, w_p):
                    c_p = DM_T if (t_p % 3 == 0 and abs(dx) + abs(dy) == 0) else (DM_M if t_p < 8 else DM_C)
                    put(px_d + dx, py_d + dy, c_p)

    # Ribete purpura-carmesi sutil en hombros y brazos largos
    x0 = cx - len(spr[0]) // 2
    y0 = by - len(spr) + 1
    for ry, row in enumerate(spr):
        for rx, ch in enumerate(row):
            if ch == 'K' and (rx == 0 or row[rx - 1] == '.'):
                put(x0 + rx, y0 + ry, DM_R)

    if ANIM:
        RUNAS.append([cx, hy_c])
        FAROLES.append([cx, hy_c, 10])
    else:
        glow(cx, hy_c, 8, DM_M, 0.5)


dibuja_demogorgon(418, 354)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
