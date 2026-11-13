#!/usr/bin/env python3
"""PixelZen Worlds - Continente Demoníaco (Bloqueo): Puerta de Obsidiana de Rikarisu."""
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
random.seed(4109)

PALETAS = {
    'noche': dict(
        sky=['#090212', '#140624', '#220b38', '#34124a', '#4a1858', '#622060', '#7e2a62', '#9c3664', '#bc4868', '#da5c70'],
        mont=['#2e1638', '#22102c', '#160a1e', '#0e0614'],
        mist=['#72325c', '#58244a', '#3e1836', '#280e24'],
        rock=('#12081a', '#22102c', '#361c42', '#4c2a58'),
        crimson=('#82183c', '#d82c64', '#ff94b8'),
        lava=('#e84878', '#ff8c4a'), win='#ff8c4a',
        agua='#12061c', ola=('#e85888', '#783468', '#301032'),
        vig=0.72, nube=['#3e1c4a', '#562658', '#723262', '#8e406a', '#aa5272', '#32143e'],
    ),
    'dorado': dict(
        sky=['#1a0618', '#2c0a26', '#481034', '#6c183c', '#94243c', '#bc3638', '#dc5436', '#f2783c', '#ffa250', '#ffca74'],
        mont=['#4c1c2e', '#381424', '#280d1a', '#1a0812'],
        mist=['#dc644c', '#b44844', '#8c323c', '#642030'],
        rock=('#180a16', '#2a1222', '#421e32', '#5c2e44'),
        crimson=('#981c38', '#ec3860', '#ffa4b8'),
        lava=('#ff6848', '#ffb060'), win='#ffa85c',
        agua='#240c1e', ola=('#ffa478', '#963c5a', '#48162c'),
        vig=0.80, nube=['#66223c', '#8e3048', '#b6444c', '#da644e', '#f48c58', '#521a32'],
    ),
    'dia': dict(
        sky=['#3c2458', '#54366e', '#704a84', '#8e6298', '#ae7cac', '#ca98bc', '#e2b6ca', '#f2d0d4', '#fae4de', '#fff2e4'],
        mont=['#583e5e', '#462e4c', '#34203a', '#24142a'],
        mist=['#cca6bc', '#ae88a2', '#906a88', '#72506e'],
        rock=('#22162a', '#362440', '#4c3456', '#664870'),
        crimson=('#8e2444', '#dc406c', '#ffabc2'),
        lava=('#f0587c', '#ff9e68'), win='#ffc078',
        agua='#3c2848', ola=('#e8a4bc', '#8c5c84', '#4e3054'),
        vig=0.90, nube=['#f8e4ec', '#ebd2de', '#f6dce8', '#e2c4d4', '#fff0f4', '#d8b4c8'],
    ),
}
PAL = PALETAS[FASE]
ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#e84878', '#9e5cff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 42, halo='#e878a4', base='#ffeef4', sombra='#d4aab8', crater='#ae8092', crater_hi='#c498aa'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 24, halo='#ffb888', centro='#fff8e8', borde='#ff8048', rayo='#ffa468'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffd4e8', '#e2c4ff', '#ffa8c4'])

MX, MY = 320, 72
CX_ASTRO = MX if FASE == 'noche' else (MX + 45 if FASE == 'dorado' else MX - 45)
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, CX_ASTRO, MY, 42, halo='#e878a4', base='#ffeef4', sombra='#d4aab8', crater='#ae8092', crater_hi='#c498aa')
    else:
        dibuja_sol_estandar(lz, CX_ASTRO, MY + (12 if FASE == 'dorado' else -10), 24, halo='#ffb888', centro='#fff8e8', borde='#ff8048', rayo='#ffa468')

render_nubes(lz, [(85, 62, 175, PAL['nube'][0], 3), (360, 48, 155, PAL['nube'][1], 3), (535, 114, 145, PAL['nube'][2], 2)], NUBES, ANIM)

# Picos escarpados de basalto rojo/púrpura
for base, amp, seed, col, mist in ((238, 92, 31, PAL['mont'][0], PAL['mist'][0]), (256, 68, 43, PAL['mont'][1], PAL['mist'][1]), (270, 42, 57, PAL['mont'][2], PAL['mist'][2])):
    r = Ruido(seed * 19)
    for x in range(W):
        n = fbm(r, x * 0.021 + seed)
        ag = (1 - abs(2 * n - 1)) ** 1.25
        top = int(base - amp * ag)
        for y in range(top, HOR + 1):
            d = y - top
            cc = mix(col, mist, 0.25 * (d / max(1, HOR - top)) ** 1.7)
            if d < 2:
                cc = mix(cc, PAL['crimson'][1], 0.30)
            put(x, y, cc)

R0, R1, R2, R3 = PAL['rock']
CR0, CR1, CR2 = PAL['crimson']

# Dos acantilados negros y torres gemelas de la Puerta de Obsidiana (x=196 y x=402)
for x0, x1 in ((0, 224), (416, 640)):
    for y in range(HOR - 22, HOR + 6):
        for x in range(x0, x1):
            put(x, y, R1 if (x + y) % 7 == 0 else R0)

for cx in (202, 438):
    for y in range(118, HOR - 18):
        hw = 22 if y > 170 else max(4, 22 - (170 - y) * 18 // 52)
        for dx in range(-hw, hw + 1):
            put(cx + dx, y, R3 if dx < -hw + 5 else (R2 if dx < 4 else R0))
    for i in range(4):
        wy = 160 + i * 24
        if ANIM:
            VENTANAS.append([cx - 1, wy])
        else:
            for dy in range(4):
                put(cx - 1, wy + dy, PAL['win'])
                put(cx, wy + dy, PAL['win'])

# Arco dentado superior uniendo las torres + puente colgante abajo
for x in range(204, 437):
    arch = int(16 * math.sin((x - 204) / 233.0 * math.pi))
    for y in range(162 - arch, 178 - arch):
        put(x, y, R1 if y > 168 - arch else R3)
    if (x - 210) % 24 == 0:
        for dy in range(10):
            put(x, 152 - arch + dy, CR1 if dy < 3 else R2)
    if ANIM and (x - 216) % 22 == 0 and x < 428:
        RUNAS.append([x, 170 - arch])
    elif not ANIM and (x - 216) % 22 == 0 and x < 428:
        put(x, 170 - arch, CR2)

# Puente de piedra sobre el abismo de agua/magma
for x in range(224, 417):
    sag = int(6 * math.sin((x - 224) / 192.0 * math.pi))
    by = HOR - 18 + sag
    for y in range(by, by + 9):
        put(x, y, R3 if y == by else R1)
    if x % 16 == 0:
        for y in range(by - 8, by):
            put(x, y, R2)

# Monolitos gigantes de cristal de maná en primer plano izquierdo/derecho
for mx, mh in ((46, 56), (82, 42), (558, 46), (594, 62)):
    for dy in range(mh):
        y = HOR - 18 - dy
        hw = max(2, 10 - dy * 8 // mh)
        for dx in range(-hw, hw + 1):
            put(mx + dx, y, CR2 if dx < 0 and dy % 5 == 0 else (CR1 if dx < 1 else CR0))
    if ANIM:
        RUNAS.append([mx, HOR - 18 - mh // 2])
    elif not ANIM:
        glow(mx, HOR - 18 - mh // 2, 7, CR1, 0.45)

for fx in (194, 232, 408, 446):
    for y in range(HOR - 26, HOR - 18):
        put(fx, y, R1)
    if ANIM:
        FAROLES.append([fx, HOR - 27, 9])
    else:
        put(fx, HOR - 27, CR2)
        glow(fx, HOR - 27, 7, PAL['lava'][1], 0.55)

render_lago(lz, PAL['agua'], PAL['ola'], DESTELLOS, ANIM, mx=CX_ASTRO, reflejo_cols=(CR2, PAL['lava'][1]))
aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS, destellos=DESTELLOS, luna=[MX, MY, 42])
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
