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
        sky=['#0e0308', '#18050d', '#260814', '#380d1d', '#4d1326', '#641a30', '#7c223a', '#952b44', '#ae374f', '#c6465a'],
        pine=('#110d14', '#1d141e', '#080509'),
        ground=('#181316', '#241b1e', '#0d090c', '#36262a'),
        cabin=('#382424', '#261718', '#150c0e', '#523432'),
        demo=('#12090e', '#422630', '#ff284c', '#ffe4e8'),
        neon=('#ff2e6a', '#48e8ff', '#ffd448', '#52ff88'),
        vig=0.74,
        nube=['#3c1220', '#54192a', '#6d2234', '#862c3e', '#9f3748', '#2a0c16'],
    ),
    'dorado': dict(
        sky=['#1c060c', '#2e0a14', '#46101e', '#621828', '#822232', '#a4303a', '#c44242', '#df5e48', '#f28056', '#ffb06c'],
        pine=('#191216', '#261a20', '#0d080a'),
        ground=('#261a1a', '#382522', '#140c0d', '#4c322e'),
        cabin=('#4e302b', '#351e1c', '#1c100f', '#70463d'),
        demo=('#160a10', '#4c2b34', '#ff3458', '#ffe8ec'),
        neon=('#ff3672', '#58ecff', '#ffdc54', '#5eff94'),
        vig=0.82,
        nube=['#641b2a', '#822636', '#a23442', '#c0464c', '#dc6256', '#48131f'],
    ),
    'dia': dict(
        sky=['#3b1d2c', '#4d2638', '#633144', '#7a3e51', '#924d5f', '#aa5f6d', '#c0747d', '#d38c90', '#e4a6a5', '#f0c0ba'],
        pine=('#242224', '#342e32', '#151215'),
        ground=('#342a2a', '#463836', '#1e1618', '#5c4642'),
        cabin=('#684a44', '#4a322e', '#2c1c1a', '#8a645b'),
        demo=('#180d12', '#52303a', '#ff3054', '#ffeaee'),
        neon=('#ff2e6a', '#48e8ff', '#ffd448', '#52ff88'),
        vig=0.90,
        nube=['#7e404d', '#98525e', '#b26872', '#ca8086', '#dfa0a0', '#64323e'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#ff2848', '#9e1c3e'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#ff90a8', base='#fff0f3', sombra='#d8b6c2', crater='#b68e9c', crater_hi='#cca4b2'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffb890', centro='#fff4ec', borde='#ff7a5c', rayo='#ffa880'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffd4dc', '#ffa8be', '#c88ea8'])

MX, MY, MR = 304, 62, 36
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#ff90a8', base='#fff0f3', sombra='#d8b6c2', crater='#b68e9c', crater_hi='#cca4b2')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 332, 162, 22, halo='#ff9068', centro='#ffede0', borde='#ff5244', rayo='#ff7654')
    else:
        dibuja_sol_estandar(lz, 292, 72, 22, halo='#ffb890', centro='#fff4ec', borde='#ff7a5c', rayo='#ffa880')

NUBES_DEF = [
    (74, 28, 145, PAL['nube'][0], 2),
    (265, 38, 165, PAL['nube'][1], 3),
    (430, 24, 145, PAL['nube'][2], 2),
    (165, 108, 160, PAL['nube'][3], 3),
    (360, 104, 130, PAL['nube'][4], 2),
    (526, 212, 110, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 1. Colinas boscosas y pinos de Mirkwood (elevados a y=234..284)
r_h = Ruido(1991)
for x in range(W):
    ramp = max(0.0, min(1.0, (x - 420) / 80.0))
    dip_r = int(20 * (0.5 - 0.5 * math.cos(math.pi * ramp)))
    ridge = int(234 + 16 * fbm(r_h, x * 0.015) + dip_r)
    for y in range(ridge, 286):
        put(x, y, mix(PAL['pine'][2], PAL['ground'][2], min(1.0, (y - ridge) / 36.0)))

P0, P1, P2 = PAL['pine']


def pino(px, by, h):
    for i in range(h):
        y = by - h + i
        hw = max(0, int(i * 0.27) - (2 if i % 5 == 4 else 0))
        for dx in range(-hw, hw + 1):
            put(px + dx, y, P1 if dx < 0 else (P0 if dx < hw // 2 else P2))


for px_p, py_p, ph_p in ((18, 288, 74), (48, 286, 64), (192, 284, 58), (226, 286, 66), (264, 284, 56), (308, 286, 60), (356, 284, 54), (488, 286, 46), (528, 286, 54), (576, 286, 60), (614, 286, 68)):
    pino(px_p, py_p, ph_p)

# 2. Claro del bosque con ruido organico 2D (elevado: y=276..400)
rx_n, ry_n = Ruido(1987), Ruido(1988)
G0, G1, G2, G3 = PAL['ground']
for y in range(276, H):
    for x in range(W):
        n2 = 0.5 * fbm(rx_n, x * 0.036) + 0.5 * fbm(ry_n, y * 0.048 + 5.0) + 0.14 * math.sin(x * 0.06) * math.cos(y * 0.07)
        c = G3 if n2 > 0.62 else (G1 if n2 > 0.46 else (G0 if n2 > 0.34 else G2))
        if y > 338 and n2 > 0.69 and (x % 5 == 0 and y % 5 == 0):
            c = mix(c, '#ff3458', 0.45)
        put(x, y, c)

# 3. CABANA BYERS anclada firme a la izquierda (x=44..186, base y=326) con luces navidenas multicolor
CB0, CB1, CB2, CB_HI = PAL['cabin']
for x in range(54, 176):
    for y in range(268, 326):
        put(x, y, CB_HI if y % 4 == 0 else (CB0 if x < 140 else CB1))
# Tejado de madera
for dy in range(26):
    y = 242 + dy
    hw = 12 + int(dy * 2.2)
    for dx in range(-hw, hw + 1):
        put(115 + dx, y, CB2 if dx > 0 else CB1)
# Chimenea de ladrillo
for y in range(230, 254):
    for dx in range(-4, 5):
        put(82 + dx, y, CB_HI if dx < 0 else CB2)
CHIMENEA = [82, 229]

# Porche y gran ventana con guirnalda de luces navidenas del alfabeto
for x in range(72, 158):
    for y in range(284, 310):
        put(x, y, '#1c1414' if (x % 18 == 0 or y == 284 or y == 309) else '#3e2e20')
for i, col_l in enumerate(PAL['neon'] * 2):
    lx_n = 78 + i * 10
    ly_n = 292 + (i % 2) * 5
    put(lx_n, ly_n, col_l)
    put(lx_n + 1, ly_n, col_l)
    if ANIM:
        RUNAS.append([lx_n, ly_n])
    else:
        glow(lx_n, ly_n, 4, col_l, 0.5)
# Farol en porche
if ANIM:
    FAROLES.append([166, 292, 11])
else:
    put(166, 292, '#fff2be')
    glow(166, 292, 10, '#ff9840', 0.6)


# 4. EL DEMOGORGON esculpido al claro del bosque (cx=418, by=350 - mas alto, anatomia alien y fauces nitidas)
def dibuja_demogorgon(cx, by):
    DM_C, DM_R, DM_M, DM_T = PAL['demo']

    # Sombra/enredaderas del Upside Down bajo sus pies
    for dx in range(-28, 29):
        for dy in range(-2, 4):
            if (dx / 28.0) ** 2 + (dy / 3.6) ** 2 <= 1.0:
                over(cx + dx, by + dy, '#681026' if abs(dx) > 18 else DM_C, 0.78)

    if not ANIM:
        glow(cx, by - 28, 18, DM_M, 0.34)

    # Silueta humanoide alta y delgada (~30px torso/piernas + fauces de petalo)
    spr = [
        '..........RRRRRRRRRR..........',
        '.........RRCCCCCCCCRR.........',
        '.........RCCHMMMMHCCR.........',
        '.........RCCCCCCCCCCR.........',
        '..........RCCCCCCCCR..........',
        '.......RRRRCCCCCCCCRRRR.......',
        '....RRRCCCCHHHHHHHHCCCCRRR....',
        '...RCCCK..CCCHHHHCCC..KCCCR...',
        '..RCCK....CCCHHHHCCC....KCCR..',
        '.RCKK......CCCCCCCC......KKCR.',
        '.KKK.......CCHHHHCC.......KKK.',
        'KKK........CCHHHHCC........KKK',
        'WK..........CCCCCC..........KW',
        'W...........CCCCCC...........W',
        '...........RCCCCCCCR..........',
        '..........RCCC..CCCR..........',
        '..........RCCC..CCCR..........',
        '.........RCCC....CCCR.........',
        '.........RCC......CCR.........',
        '........RCCC......CCCR........',
        '........RCC........CCR........',
        '.......RCCC........CCCR.......',
        '.......RCC..........CCR.......',
        '......RCCC..........CCCR......',
        '.....KKKK............KKKK.....',
    ]
    pinta_sprite(lz, cx, by, spr, {
        'K': DM_C,
        'C': DM_R,
        'H': '#70424e',
        'R': '#945462',
        'M': DM_M,
        'W': '#ffe0e6',
    })

    # 5 petalos abiertos dentados carmesi rodeando las fauces del Demogorgon
    hy_c = by - len(spr)
    for ang_deg in (-145, -90, -35, 22, 158):
        rad = math.radians(ang_deg)
        perp = rad + math.pi * 0.5
        for t_p in range(3, 13):
            w_p = 2 if t_p < 9 else 1
            for s in range(-w_p, w_p + 1):
                px_d = int(cx + math.cos(rad) * t_p + math.cos(perp) * s * 0.65)
                py_d = int(hy_c + math.sin(rad) * t_p + math.sin(perp) * s * 0.65)
                if abs(s) == w_p and t_p % 2 == 1:
                    c_p = DM_T
                elif t_p < 8 and abs(s) < w_p:
                    c_p = DM_M
                else:
                    c_p = '#7c142a'
                put(px_d, py_d, c_p)
    disc(cx, hy_c, 2, '#ff1e42')
    put(cx, hy_c, '#400612')

    if ANIM:
        RUNAS.append([cx, hy_c])
        FAROLES.append([cx, hy_c, 10])
    else:
        glow(cx, hy_c, 9, DM_M, 0.55)


dibuja_demogorgon(418, 350)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
