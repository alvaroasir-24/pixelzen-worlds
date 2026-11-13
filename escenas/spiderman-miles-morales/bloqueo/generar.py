#!/usr/bin/env python3
"""PixelZen Worlds - Miles Morales (Bloqueo): Azotea de Brooklyn frente a Manhattan."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    exporta_salida, exporta_sprites_si_aplica, mix, render_cielo,
    render_estrellas, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(6109)

PALETAS = {
    'noche': dict(
        sky=['#050410', '#0a071c', '#120c2c', '#1e1240', '#2d1852', '#3f1e62', '#562670', '#70307a', '#8e3c82', '#ae4c88'],
        city=('#0c0b18', '#151428', '#222140', '#34325c'),
        brick=('#2e1a28', '#422638', '#563448'),
        roof=('#181726', '#242336', '#34324c'),
        red='#ff2a55', cyan='#00e5ff', win='#ffd26a',
        vig=0.72, nube=['#2c1c48', '#3c245a', '#522c6c', '#6a387c', '#86488a', '#24163a'],
    ),
    'dorado': dict(
        sky=['#1a0826', '#2c0e38', '#461448', '#6a1c50', '#92264e', '#ba3642', '#dc4e36', '#f27038', '#fc9848', '#ffc464'],
        city=('#1c1428', '#2c203c', '#423056', '#5c4674'),
        brick=('#4c2632', '#6a3642', '#864852'),
        roof=('#261e32', '#362c44', '#4a3e5c'),
        red='#ff3864', cyan='#48e8ff', win='#ffde84',
        vig=0.80, nube=['#66284a', '#8c3656', '#b44858', '#da6656', '#f48e60', '#50203c'],
    ),
    'dia': dict(
        sky=['#1b4e96', '#2a64ae', '#3e7cc4', '#5896d8', '#78b0e6', '#9ac6f0', '#b8daf4', '#d4eaf8', '#eaf4fa', '#f6f8ec'],
        city=('#24344e', '#364c6c', '#4e6a90', '#6c8bb2'),
        brick=('#5e3842', '#7c4c56', '#9a646e'),
        roof=('#384458', '#4c5c74', '#647690'),
        red='#ff2a55', cyan='#00c8e8', win='#fff2a8',
        vig=0.92, nube=['#ffffff', '#eef6fc', '#ffffff', '#e4f0fa', '#fafaf8', '#dbe8f4'],
    ),
}
PAL = PALETAS[FASE]
ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#ff2a55', '#00e5ff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#ff78a8', base='#fff4fa', sombra='#dcc4d8', crater='#b89eb8', crater_hi='#ccb4ca'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe2a8', centro='#fffef2', borde='#ffc45c', rayo='#ffdf8a'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffd8e8', '#b8f4ff', '#e4c8ff'])

MX, MY = 420, 72
CX_ASTRO = MX if FASE == 'noche' else (MX - 30 if FASE == 'dorado' else MX - 60)
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, CX_ASTRO, MY, 38, halo='#ff78a8', base='#fff4fa', sombra='#dcc4d8', crater='#b89eb8', crater_hi='#ccb4ca')
    else:
        dibuja_sol_estandar(lz, CX_ASTRO, MY - (12 if FASE == 'dia' else -14), 22, halo='#ffe2a8', centro='#fffef2', borde='#ffc45c', rayo='#ffdf8a')

render_nubes(lz, [(105, 58, 175, PAL['nube'][0], 3), (305, 48, 165, PAL['nube'][1], 3), (505, 110, 150, PAL['nube'][2], 2)], NUBES, ANIM)

C0, C1, C2, C3 = PAL['city']
# Relleno continuo del cielo inferior entre rascacielos (y = HOR..304)
if SKYM == 'normal':
    for y in range(HOR, 305):
        for x in range(W):
            put(x, y, PAL['sky'][-1])
# Cañón profundo de rascacielos de Manhattan extendiéndose hasta detrás de la azotea (y=305)
torres = [
    (6, 176, 46, 0), (54, 198, 40, 0), (96, 116, 54, 26), (152, 166, 46, 0),
    (200, 92, 58, 34), (260, 184, 44, 0), (306, 138, 52, 0), (360, 162, 44, 0),
    (406, 78, 56, 32), (464, 152, 48, 0), (514, 176, 44, 0), (560, 120, 52, 24), (614, 158, 30, 0),
]
for bx, top_y, bw, spire in torres:
    for y in range(top_y, 312):
        for x in range(bx, min(W, bx + bw)):
            col = C3 if x < bx + 5 else (C2 if x < bx + bw - 8 else C0)
            if y % 12 == 0:
                col = mix(col, C1, 0.5)
            put(x, y, col)
    if spire:
        sx = bx + bw // 2
        for y in range(top_y - spire, top_y):
            put(sx, y, C3)
        if ANIM:
            FAROLES.append([sx, top_y - spire - 1, 7])
        else:
            put(sx, top_y - spire - 1, PAL['red'])
    for wy in range(top_y + 10, 294, 10):
        for wx in range(bx + 8, min(W - 4, bx + bw - 8), 10):
            if (wx * 7 + wy * 13) % 5 != 0:
                if ANIM:
                    VENTANAS.append([wx, wy])
                else:
                    for dy in range(3):
                        for dx in range(2):
                            put(wx + dx, wy + dy, PAL['win'])

# SÓLIDA AZOTEA DE LADRILLO DE BROOKLYN EN PRIMER PLANO (y = 294..400, sin lago ni tiras flotantes)
BR0, BR1, BR2 = PAL['brick']
RF0, RF1, RF2 = PAL['roof']
# Muro frontal/pretil superior de la azotea (y = 294..326) y suelo plano de grava/asfalto (y = 326..400)
for x in range(W):
    for y in range(294, 300):
        put(x, y, RF2 if y < 296 else C0)
    for y in range(300, 328):
        brick_seam = (y % 4 == 0) or ((x + (y // 4) * 5) % 10 == 0)
        put(x, y, BR0 if brick_seam else (BR2 if x < 240 else BR1))
    for y in range(328, H):
        strip = ((x + y * 2) % 19 == 0)
        put(x, y, RF0 if (y == 328 or strip) else (RF1 if y < 362 else RF2))

# Claraboya / ventilación en el techo y chimenea derecha bien apoyadas en la azotea
for y in range(334, 356):
    for x in range(214, 272):
        put(x, y, C0 if (y == 334 or x == 214 or x == 271) else (C3 if y < 342 else C2))
for y in range(310, 344):
    for x in range(336, 366):
        put(x, y, BR0 if (y % 4 == 0) else BR1)

# Cartel neón Araña apoyado con patas metálicas sobre la losa de la azotea (y = 266..318)
for px in (466, 514):
    for y in range(296, 318):
        put(px, y, C0)
        put(px + 1, y, C3)
for y in range(266, 297):
    for x in range(460, 522):
        edge = (x in (460, 461, 520, 521) or y in (266, 267, 295, 296))
        put(x, y, PAL['red'] if edge else C0)
for dx in range(-8, 9):
    for dy in range(-5, 6):
        if abs(dx) + abs(dy) * 2 <= 9 or (abs(dx) == abs(dy) * 2 and abs(dx) <= 6):
            put(491 + dx, 281 + dy, PAL['red'])
if ANIM:
    RUNAS.extend([[491, 281], [462, 268], [519, 268]])

# Depósito de agua neoyorquino con patas firmes clavadas en el pretil y cubierta (x = 540..610, y = 212..342)
for x in range(548, 602):
    for y in range(228, 274):
        c_t = C3 if x < 562 else (C2 if x < 588 else C0)
        if y in (240, 256, 272):
            c_t = C0
        put(x, y, c_t)
for dy in range(18):
    hw = 28 - dy * 28 // 18
    for dx in range(-hw, hw + 1):
        put(575 + dx, 228 - dy, C3 if dx < 0 else C1)
# Vigas y patas de acero bajando solidamente sobre zapatas en el techo (y=274..340)
for lx in (554, 594):
    for y in range(274, 340):
        put(lx, y, C0); put(lx + 1, y, C2)
    for dx in range(-4, 6):
        put(lx + dx, 340, C0); put(lx + dx, 339, C3)
for t in range(34):
    put(555 + t * 39 // 34, 278 + t, C1)
    put(594 - t * 39 // 34, 278 + t, C1)

# MILES MORALES agachado en postura atlética sobre el pretil izquierdo (cx = 104, pie firme en y = 294)
MX_H, BY_H = 104, 294
# Sombra de apoyo sobre el pretil
for dx in range(-9, 10):
    over(MX_H + dx, BY_H, '#05040a', 0.65)
# Zapatillas rojas/blancas y piernas flexionadas en cuclillas
for sx in (-8, -7, -6, 6, 7, 8):
    put(MX_H + sx, BY_H, '#f0f4fc')
    put(MX_H + sx, BY_H - 1, '#e62448')
for dx, dy in ((-7, -2), (-6, -3), (-5, -4), (-4, -5), (-3, -6), (7, -2), (6, -3), (5, -4), (4, -5), (3, -6)):
    put(MX_H + dx, BY_H + dy, '#11111d')
    put(MX_H + dx - (1 if dx > 0 else -1), BY_H + dy, '#1a192c')
# Torso inclinado hacia adelante con V roja y emblema
for dy in range(-12, -5):
    hw = 4 if dy > -10 else 5
    for dx in range(-hw, hw + 1):
        col = '#0e0e19'
        if dy in (-11, -10) and abs(dx) >= 3:
            col = '#ff2a55'
        elif dy in (-9, -8, -7) and abs(dx) <= 1:
            col = '#ff2a55'
        put(MX_H + dx, BY_H + dy, col)
# Brazos apoyados en las rodillas / pretil
for k in range(1, 6):
    put(MX_H - 5 - k // 2, BY_H - 10 + k * 2, '#141422')
    put(MX_H + 5 + k // 2, BY_H - 10 + k * 2, '#141422')
# Cabeza inclinada con capucha/máscara y lentes blancos rasgados
for dy in range(-20, -12):
    hw = 4 if dy in (-20, -13, -12) else 5
    for dx in range(-hw, hw + 1):
        put(MX_H + dx, BY_H + dy, '#10101c')
for ex in (-3, 2):
    put(MX_H + ex, BY_H - 16, '#ffffff')
    put(MX_H + ex + (0 if ex < 0 else 1), BY_H - 17, '#ffffff')
    put(MX_H + ex + (1 if ex < 0 else 0), BY_H - 16, '#ffb8c8')
if ANIM:
    RUNAS.extend([[MX_H - 10, BY_H - 8], [MX_H + 10, BY_H - 8]])

aplica_vineta(lz, PAL['vig'])
out = ARGS[0] if ARGS else '.'
datos = dict(W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS, destellos=DESTELLOS, luna=[MX, MY, 38])
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
