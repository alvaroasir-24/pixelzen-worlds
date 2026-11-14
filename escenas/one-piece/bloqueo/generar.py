#!/usr/bin/env python3
"""PixelZen Worlds - One Piece (Bloqueo): Road Poneglyph, Sombrero de Paja y Fruta Nika."""
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
random.seed(1303)

PALETAS = {
    'noche': dict(
        sky=['#040714', '#080e26', '#0e183a', '#162452', '#1e326a', '#284284', '#34549c', '#4468b4', '#587ecc', '#7296e2'],
        sea=('#08142e', '#10244c', '#38bdf8'),
        rock=('#1c2030', '#2e344c', '#0e101a', '#444e70'),
        pon=('#68121a', '#961c26', '#3a080c', '#c82e38', '#fde68a'),
        hat=('#d97706', '#f59e0b', '#fef08a', '#dc2626'),
        fruit=('#7e22ce', '#a855f7', '#e9d5ff', '#22c55e'),
        vig=0.72,
        nube=['#162240', '#22325c', '#2e447a', '#3e5896', '#526eb2', '#101830'],
    ),
    'dorado': dict(
        sky=['#140d24', '#26183a', '#3e244c', '#5e3456', '#844856', '#ac604c', '#d27e46', '#f0a04c', '#ffc464', '#ffe294'],
        sea=('#1a1c38', '#2c3058', '#fdba74'),
        rock=('#2c2434', '#42364c', '#16121c', '#5e4e6e'),
        pon=('#7c161e', '#b0242e', '#460a0e', '#e23a46', '#fef08a'),
        hat=('#ea580c', '#f59e0b', '#fef08a', '#dc2626'),
        fruit=('#9333ea', '#c084fc', '#f3e8ff', '#4ade80'),
        vig=0.80,
        nube=['#442644', '#603452', '#82465a', '#a65c5e', '#ca7862', '#321a34'],
    ),
    'dia': dict(
        sky=['#184c92', '#2662ac', '#3a7cc2', '#5296d6', '#72b0e4', '#92c8ee', '#b2def6', '#ceeefa', '#e4f5fc', '#f4f8ef'],
        sea=('#1c4e82', '#2a70ac', '#bae6fd'),
        rock=('#4a5064', '#666e88', '#2a2e3a', '#8c96b4'),
        pon=('#8a1c22', '#c02c34', '#500e12', '#ea464c', '#fef08a'),
        hat=('#f59e0b', '#fbbf24', '#fef9c3', '#ef4444'),
        fruit=('#9333ea', '#c084fc', '#faf5ff', '#22c55e'),
        vig=0.88,
        nube=['#ffffff', '#eef6fc', '#dff0fa', '#f8fcff', '#e4f0fb', '#c8e0f0'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#ef4444', '#c084fc'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#bae6fd', base='#ffffff', sombra='#cbd5e1', crater='#94a3b8', crater_hi='#b4c2d8'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe49e', centro='#fffef2', borde='#ffb448', rayo='#ffd88c'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffffff', '#bae6fd', '#fde68a'])

MX, MY, MR = 326, 66, 38
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#bae6fd', base='#ffffff', sombra='#cbd5e1', crater='#94a3b8', crater_hi='#b4c2d8')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 326, 118, 22, halo='#ff9860', centro='#fff2d8', borde='#ff562e', rayo='#ff824a')
    else:
        dibuja_sol_estandar(lz, 326, 72, 22, halo='#ffe49e', centro='#fffef2', borde='#ffb448', rayo='#ffd88c')

NUBES_DEF = [
    (86, 48, 80, PAL['nube'][1], 2),
    (524, 62, 82, PAL['nube'][3], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# Océano lejano (y=220..280) con estelas suaves de luz lunar y acantilado en primer plano
s_dk, s_lt, s_hi = PAL['sea']
for y in range(220, 280):
    d = y - 220
    for x in range(W):
        moon_w = max(8, 36 - d // 3)
        moon_glint = abs(x - MX) < moon_w and (y % 4 == 0) and dith(x, y, 0.24 * (1.0 - abs(x - MX) / float(moon_w)))
        wave = (y % 5 == 0) and dith(x, y, 0.30)
        col = '#e2e8f0' if moon_glint else (s_lt if wave else s_dk)
        put(x, y, col)

rk0, rk1, rk2, rk3 = PAL['rock']
r_rk = Ruido(1331)
for x in range(W):
    cliff_y = int(272 + 12 * math.sin(x * 0.015) + 8 * fbm(r_rk, x * 0.03))
    for y in range(cliff_y, H):
        n = fbm(r_rk, x * 0.032 + y * 0.042)
        seam = ((x + y // 12 * 15) % 30 == 0) or (y % 14 == 0)
        col = rk2 if seam else (rk3 if n > 0.62 else (rk1 if n > 0.38 else rk0))
        if y < cliff_y + 4:
            col = rk3
        put(x, y, col)

# Monolítico Road Poneglyph rojo carmesí con glifos brillantes (cx=202, base_y=346)
pn0, pn1, pn2, pn3, gly = PAL['pon']
px, py_b = 202, 346
for y in range(py_b - 116, py_b + 1):
    # Cara frontal + bisel lateral derecho en perspectiva 3D
    for dx in range(-32, 33):
        is_side = (dx > 20)
        is_bdr = (dx in (-32, 20, 32) or y in (py_b - 116, py_b))
        col = pn2 if is_bdr else (pn0 if is_side else (pn3 if dx < -22 or y < py_b - 108 else pn1))
        put(px + dx, y, col)
# Cuadrícula de glifos dorados grabados en el Road Poneglyph
rng_g = random.Random(1399)
for gy in range(py_b - 102, py_b - 12, 9):
    for gx in range(px - 22, px + 14, 7):
        if rng_g.random() < 0.78:
            put(gx, gy, gly)
            put(gx + 1, gy, gly)
            put(gx + rng_g.choice((0, 2)), gy + 2, gly)
            put(gx + 1, gy + 3, gly)
if ANIM:
    RUNAS.append([px - 4, py_b - 58])
else:
    glow(px - 4, py_b - 58, 22, '#ef4444', 0.35)

# Pedestal rocoso en el centro-derecha (cx=366, by=354) con Sombrero de Paja + Fruta Gomu Gomu / Nika
for dy in range(-12, 16):
    hw = 58 + dy
    for dx in range(-hw, hw + 1):
        put(366 + dx, 344 + dy, rk2 if abs(dx) >= hw - 3 else (rk3 if dy < -6 else rk1))

# Sombrero de Paja de Luffy (cx=344, by=332)
hx, hy = 344, 332
ht0, ht1, ht2, ht_red = PAL['hat']
for dy in range(-15, 3):
    for dx in range(-22, 23):
        in_brim = (dy >= -3 and abs(dx) <= 22)
        in_crown = (-14 <= dy < -2 and (dx * dx) / 140.0 + ((dy + 2) * (dy + 2)) / 150.0 <= 1.0)
        if in_brim or in_crown:
            if -6 <= dy <= -3 and abs(dx) <= 12:
                col = ht_red
            else:
                col = ht2 if (dx < 0 and dy < -5) or dy == -2 else (ht1 if (dx + dy) % 3 else ht0)
            put(hx + dx, hy + dy, col)

# Fruta del Diablo Gomu Gomu / Nika (cx=404, by=326) con espirales + tallo verde
fx, fy = 404, 326
fr0, fr1, fr2, fr_st = PAL['fruit']
if not ANIM:
    glow(fx, fy - 8, 16, fr1, 0.55)
disc(fx, fy - 8, 10, fr0)
disc(fx - 2, fy - 10, 7, fr1)
for deg in range(0, 540, 12):
    a = math.radians(deg)
    rr = 2 + (deg / 540.0) * 6.5
    put(fx - 1 + int(round(math.cos(a) * rr)), fy - 8 + int(round(math.sin(a) * rr)), fr2)
for dy in range(7):
    put(fx + dy // 3, fy - 18 - dy, fr_st)
    put(fx + dy // 3 + 1, fy - 18 - dy, '#86efac' if dy > 4 else fr_st)
if ANIM:
    RUNAS.append([fx, fy - 8])
    FAROLES.append([hx, hy - 8, 7])

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
