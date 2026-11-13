#!/usr/bin/env python3
"""PixelZen Worlds - Black Clover (Bloqueo): Altar del Grimorio de Cinco Hojas."""
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
random.seed(6119)

PALETAS = {
    'noche': dict(
        sky=['#04020a', '#0a0518', '#140a2a', '#22103c', '#34164c', '#4a1c58', '#62225e', '#7e2a62', '#9c3664', '#b84868'],
        mont=['#2a2442', '#201b34', '#161224', '#0e0b18'],
        mist=['#644a7c', '#503966', '#3d2a52', '#2b1c3c'],
        stone=('#100d1a', '#1c172c', '#2e2644', '#463a64'),
        crimson=('#741424', '#c8203c', '#ff6480'),
        gold=('#ffd458', '#c88c24'), sword=('#8c94ae', '#ced6ec', '#222030'),
        agua='#080614', ola=('#d86c92', '#4e3878', '#22143a'),
        vig=0.72, nube=['#382650', '#4c3264', '#663e72', '#824c78', '#9e5c7e', '#2e1e42'],
    ),
    'dorado': dict(
        sky=['#160822', '#260d34', '#3e1244', '#601a4a', '#862248', '#ae303e', '#d24636', '#eb6838', '#fa9046', '#ffc064'],
        mont=['#4c283e', '#3a1e32', '#2a1524', '#1c0e1a'],
        mist=['#dc7462', '#ba5858', '#924050', '#6a2c44'],
        stone=('#1a0e1a', '#2a182a', '#402640', '#5a3a58'),
        crimson=('#8c1624', '#dc283c', '#ff7c88'),
        gold=('#ffe068', '#d49624'), sword=('#9c98a8', '#e2dce4', '#2e1a28'),
        agua='#1e0c22', ola=('#ffa47e', '#884266', '#401838'),
        vig=0.80, nube=['#6e3252', '#94405c', '#bc545c', '#de725a', '#f69862', '#582644'],
    ),
    'dia': dict(
        sky=['#1f4d94', '#2e62aa', '#4278be', '#5c90d0', '#7aa8de', '#9ac0ea', '#b8d6f0', '#d4e6f2', '#e8eff2', '#f4f0dc'],
        mont=['#546282', '#44506e', '#36405a', '#283046'],
        mist=['#c4d6e8', '#a8bed4', '#8ca4c0', '#708aa8'],
        stone=('#1e2234', '#2e344e', '#444e70', '#606c90'),
        crimson=('#821c2a', '#cc2e44', '#ff7a8c'),
        gold=('#ffe46a', '#cca02c'), sword=('#96a2be', '#eef4ff', '#283044'),
        agua='#223c60', ola=('#d8e6f4', '#7492ba', '#385076'),
        vig=0.90, nube=['#ffffff', '#eef4fa', '#ffffff', '#e4eef8', '#f8f8f6', '#dbe6f2'],
    ),
}
PAL = PALETAS[FASE]
ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#e82848', '#7c48ff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 42, halo='#e87098', base='#fff0f4', sombra='#d4b4c4', crater='#ae8ca0', crater_hi='#c6a8b8'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 24, halo='#ffe2a8', centro='#fffef2', borde='#ffc464', rayo='#ffe49c'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffe4ec', '#e0d0ff', '#a8d4ff'])

MX, MY = 136, 76
CX_ASTRO = MX if FASE == 'noche' else (MX + 38 if FASE == 'dorado' else MX - 20)
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, CX_ASTRO, MY, 42, halo='#e87098', base='#fff0f4', sombra='#d4b4c4', crater='#ae8ca0', crater_hi='#c6a8b8')
    else:
        dibuja_sol_estandar(lz, CX_ASTRO, MY - (8 if FASE == 'dia' else -14), 24, halo='#ffe2a8', centro='#fffef2', borde='#ffc464', rayo='#ffe49c')

render_nubes(lz, [(105, 58, 165, PAL['nube'][0], 3), (320, 48, 160, PAL['nube'][1], 3), (520, 108, 150, PAL['nube'][2], 2)], NUBES, ANIM)

# Cordillera nevada y torres del Reino del Trébol al fondo
for base, amp, seed, col, mist in ((240, 82, 71, PAL['mont'][0], PAL['mist'][0]), (256, 56, 83, PAL['mont'][1], PAL['mist'][1])):
    r = Ruido(seed * 17)
    for x in range(W):
        n = fbm(r, x * 0.017 + seed)
        ag = 1 - abs(2 * n - 1)
        top = int(base - amp * ag)
        for y in range(top, HOR + 1):
            put(x, y, mix(col, mist, 0.25 * ((y - top) / max(1, HOR - top))))

ST0, ST1, ST2, ST3 = PAL['stone']
CR0, CR1, CR2 = PAL['crimson']

# Torres góticas laterales en segundo plano
for tx, top_y in ((58, 174), (556, 168)):
    for y in range(top_y, HOR + 1):
        for x in range(tx, tx + 28):
            put(x, y, ST2 if x < tx + 8 else ST0)
    for dy in range(26):
        hw = max(1, dy * 14 // 26)
        for dx in range(-hw, hw + 1):
            put(tx + 14 + dx, top_y - 26 + dy, ST1 if dx < 0 else ST0)
    if ANIM:
        VENTANAS.append([tx + 13, top_y + 22])
    else:
        for dy in range(4):
            put(tx + 13, top_y + 22 + dy, PAL['gold'][0])

# Santuario gótico central en la terraza del lago (x=196..444)
for y in range(HOR - 16, HOR + 4):
    pad = (HOR + 4 - y)
    for x in range(186 + pad, 454 - pad):
        put(x, y, ST1 if y > HOR - 12 else ST3)

# Dos pilares góticos labrados y arco ojival superior
for px in (212, 404):
    for y in range(126, HOR - 16):
        for dx in range(24):
            put(px + dx, y, ST3 if dx < 5 else (ST2 if dx < 16 else ST0))
        if ANIM and y % 12 == 0 and 140 < y < HOR - 24:
            RUNAS.append([px + 12, y])
        elif not ANIM and y % 12 == 0 and 140 < y < HOR - 24:
            put(px + 12, y, CR2)

for x in range(208, 433):
    oj = int(28 * math.sin((x - 208) / 225.0 * math.pi))
    for y in range(114 - oj, 132 - oj):
        put(x, y, ST3 if y < 120 - oj else ST1)

# Altar central con la Espada Anti-Magia clavada y aureola del grimorio
for y in range(HOR - 36, HOR - 16):
    hw = 28 + (y - (HOR - 36)) // 2
    for x in range(320 - hw, 320 + hw + 1):
        put(x, y, ST3 if y == HOR - 36 else (ST2 if x < 330 else ST1))
# Hoja ancha de la espada + empuñadura cruzada
for y in range(178, HOR - 36):
    for dx in range(-3, 4):
        put(320 + dx, y, PAL['sword'][1] if dx < 0 else (PAL['sword'][2] if dx > 1 else PAL['sword'][0]))
for dx in range(-14, 15):
    put(320 + dx, 186, CR1)
    put(320 + dx, 187, PAL['gold'][0])
for y in range(162, 186):
    for dx in range(-2, 3):
        put(320 + dx, y, CR2 if y < 167 else PAL['sword'][2])

# Símbolo rúnico brillante sobre el altar
for y in range(152, 232):
    for x in range(290, 351):
        dist = math.hypot(x - 320, y - 196)
        if 24.5 < dist < 26.2 and (x + y) % 2 == 0:
            if ANIM and (x + y) % 14 == 0:
                RUNAS.append([x, y])
            elif not ANIM:
                over(x, y, CR2, 0.55)

for fx in (256, 384, 166, 474):
    for y in range(HOR - 24, HOR - 16):
        put(fx, y, ST0)
    if ANIM:
        FAROLES.append([fx, HOR - 25, 9])
    else:
        put(fx, HOR - 25, CR2)
        glow(fx, HOR - 25, 7, CR1, 0.55)

render_lago(lz, PAL['agua'], PAL['ola'], DESTELLOS, ANIM, mx=CX_ASTRO, reflejo_cols=(CR2, PAL['ola'][0]))
aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS, destellos=DESTELLOS, luna=[MX, MY, 42])
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
