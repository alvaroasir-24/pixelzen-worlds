#!/usr/bin/env python3
"""PixelZen Worlds - Hunter x Hunter (Bloqueo): Torre Celestial y Dirigible Cazador."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, exporta_salida, exporta_sprites_si_aplica, fbm, mix, render_cielo,
    render_estrellas, render_lago, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(5023)

PALETAS = {
    'noche': dict(
        sky=['#030818', '#08122c', '#101e44', '#182c5c', '#243c74', '#344e8c', '#4862a4', '#607abc', '#7c96d2', '#9ab4e6'],
        mont=['#223254', '#182440', '#10182e', '#0a1020'],
        mist=['#4e6896', '#3a5078', '#2a3a5a', '#1c2840'],
        twr=('#141c34', '#222e4e', '#36466e', '#526894'),
        gold=('#f4c454', '#ffe89a'), win='#ffe084', cyan='#54ded4',
        agua='#0a1834', ola=('#88c8f4', '#3c689c', '#1a3058'),
        vig=0.76, nube=['#2a3a64', '#384c7c', '#4a6294', '#6078aa', '#7890c0', '#243256'],
    ),
    'dorado': dict(
        sky=['#120c2c', '#221442', '#381e58', '#562a66', '#783c6a', '#9e5466', '#c27060', '#e0925c', '#f4b668', '#ffd888'],
        mont=['#463052', '#342240', '#24162e', '#180e20'],
        mist=['#d8866c', '#b46a62', '#8e5058', '#68384a'],
        twr=('#1c182c', '#2e2642', '#463a5c', '#665680'),
        gold=('#ffd462', '#fff0a8'), win='#ffd474', cyan='#78e8dc',
        agua='#1e1634', ola=('#f6b274', '#84587e', '#3c224c'),
        vig=0.82, nube=['#663c5e', '#8e5066', '#b66866', '#da8864', '#f4ae6c', '#52304c'],
    ),
    'dia': dict(
        sky=['#1b529c', '#2a68b4', '#4080ca', '#5c9adc', '#7eb4ea', '#9eccf4', '#bce0f8', '#d6eefc', '#ebf6fe', '#f6faee'],
        mont=['#4e7298', '#3c5c80', '#2c4666', '#1e344e'],
        mist=['#c4def4', '#a8c6e0', '#8caece', '#7092b8'],
        twr=('#223048', '#364a6a', '#506a90', '#7290ba'),
        gold=('#f6c858', '#fff0a4'), win='#ffea96', cyan='#4ad4c8',
        agua='#265890', ola=('#ccf0fc', '#6ea4d0', '#386090'),
        vig=0.92, nube=['#ffffff', '#eef6fc', '#ffffff', '#e4f0fa', '#fafaf8', '#d8e8f4'],
    ),
}
PAL = PALETAS[FASE]
ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE)
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#a8ccff', base='#f8f6ee', sombra='#bcc6dc', crater='#9aa4bc', crater_hi='#b2bcd4'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe49c', centro='#fffef4', borde='#ffc45c', rayo='#ffe088'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS)

MX, MY = 190, 78
CX_ASTRO = MX if FASE == 'noche' else (MX + 34 if FASE == 'dorado' else MX - 20)
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, CX_ASTRO, MY, 38, halo='#a8ccff', base='#f8f6ee', sombra='#bcc6dc', crater='#9aa4bc', crater_hi='#b2bcd4')
    else:
        dibuja_sol_estandar(lz, CX_ASTRO, MY - (10 if FASE == 'dia' else -14), 22, halo='#ffe49c', centro='#fffef4', borde='#ffc45c', rayo='#ffe088')

render_nubes(lz, [(80, 66, 165, PAL['nube'][0], 3), (440, 56, 175, PAL['nube'][1], 3), (235, 138, 155, PAL['nube'][2], 2)], NUBES, ANIM)

# Colinas lejanas tras la bahía
for base, amp, seed, col, mist in ((246, 52, 61, PAL['mont'][0], PAL['mist'][0]), (262, 36, 73, PAL['mont'][1], PAL['mist'][1])):
    r = Ruido(seed * 13)
    for x in range(W):
        n = fbm(r, x * 0.015 + seed)
        top = int(base - amp * n)
        for y in range(top, HOR + 1):
            put(x, y, mix(col, mist, 0.25 * ((y - top) / max(1, HOR - top))))

T0, T1, T2, T3 = PAL['twr']
# Horizonte urbano flanqueando la bahía
skyline = [(14, 228, 34), (52, 206, 40), (96, 236, 32), (132, 214, 38), (176, 242, 36), (424, 234, 36), (464, 208, 42), (510, 228, 34), (548, 212, 40), (594, 238, 36)]
for bx, top_y, bw in skyline:
    for y in range(top_y, HOR + 1):
        for x in range(bx, bx + bw):
            put(x, y, T2 if x < bx + 5 else (T1 if x < bx + bw - 6 else T0))
    for wy in range(top_y + 10, HOR - 12, 12):
        for wx in (bx + 8, bx + bw - 12):
            if ANIM:
                VENTANAS.append([wx, wy])
            else:
                for dy in range(4):
                    for dx in range(2):
                        put(wx + dx, wy + dy, PAL['win'])

# Monumental Torre Celestial (Heavens Arena) centrada en x=320
# Basamento amplio + fuste escalonado + cúpula dorada y aguja hasta y=40
for x0, x1, y0, y1 in ((256, 384, 250, HOR + 2), (274, 366, 152, 250), (288, 352, 96, 152), (304, 336, 68, 96)):
    for y in range(y0, y1):
        for x in range(x0, x1):
            col = T3 if x < x0 + 6 else (T2 if x < x1 - 10 else T0)
            if y % 18 == 0:
                col = mix(col, PAL['cyan'], 0.35)
            put(x, y, col)
for y in range(40, 68):
    for dx in range(-2, 3):
        put(320 + dx, y, PAL['gold'][0] if abs(dx) <= 1 else T2)
if ANIM:
    FAROLES.append([320, 39, 12])
else:
    put(320, 39, PAL['gold'][1])
    glow(320, 39, 9, PAL['gold'][0], 0.65)

# Ventanas simétricas de la Torre Celestial
for ty in range(106, 244, 14):
    for wx in (296, 319, 342):
        if ANIM:
            VENTANAS.append([wx, ty])
        else:
            for dy in range(4):
                for dx in range(2):
                    put(wx + dx, ty + dy, PAL['win'])

# Dirigible del Examen de Cazador (x=470..556, y=104..134)
ACX, ACY = 508, 114
for dy in range(-12, 13):
    hw = int(38 * math.sqrt(max(0.0, 1.0 - (dy / 12.5) ** 2)))
    for dx in range(-hw, hw + 1):
        c = T3 if dy < -4 else (T2 if dy < 4 else T1)
        if dy == 0:
            c = PAL['gold'][0]
        put(ACX + dx, ACY + dy, c)
for y in range(ACY + 12, ACY + 18):
    for dx in range(-14, 15):
        put(ACX + dx, y, T0)
for gx in (ACX - 10, ACX, ACX + 10):
    if ANIM:
        FAROLES.append([gx, ACY + 16, 6])
    else:
        put(gx, ACY + 16, PAL['gold'][1])

# Malecón frente al agua con faroles del paseo
for y in range(HOR - 5, HOR + 2):
    for x in range(W):
        put(x, y, T1 if y > HOR - 3 else T3)
for fx in range(48, 600, 72):
    if 256 <= fx <= 384:
        continue
    for y in range(HOR - 12, HOR - 5):
        put(fx, y, T0)
    if ANIM:
        FAROLES.append([fx, HOR - 13, 6])
    else:
        put(fx, HOR - 13, PAL['cyan'])

render_lago(lz, PAL['agua'], PAL['ola'], DESTELLOS, ANIM, mx=CX_ASTRO, reflejo_cols=('#ffe498', '#c8e8ff'))
aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS, destellos=DESTELLOS, luna=[MX, MY, 38])
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
