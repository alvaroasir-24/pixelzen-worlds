#!/usr/bin/env python3
"""PixelZen Worlds - Dragon Ball Z (Bloqueo): Kame House, Nube Kinto y Esfera de 4 Estrellas."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, exporta_salida, exporta_sprites_si_aplica, fbm, mix, pinta_sprite,
    render_cielo, render_estrellas, render_lago, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'dorado')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1403)

PALETAS = {
    'noche': dict(
        sky=['#040818', '#08122c', '#0e1e42', '#162c5c', '#203c76', '#2e5090', '#4266aa', '#587ec4', '#7498da', '#96b4ee'],
        sand=('#7c6448', '#a4865e', '#4c3c28', '#c8a678'),
        wall=('#c8767e', '#e89ca4', '#7a424a', '#f8fafc'),
        roof=('#981b22', '#dc2626', '#580e12', '#f87171'),
        palm=('#0d4a26', '#16743c', '#062814', '#22c55e'),
        agua='#09244c',
        olas=('#7dd3fc', '#fde047', '#0c4a6e'),
        reflejo=('#fef08a', '#bae6fd'),
        vig=0.72,
        nube=['#1c2a4a', '#2a3e68', '#3a5486', '#4c6ca4', '#6484be', '#141e38'],
    ),
    'dorado': dict(
        sky=['#140c24', '#28163a', '#44244a', '#683652', '#904e4c', '#b86c44', '#dc8c40', '#f6ae4c', '#ffce68', '#ffec9c'],
        sand=('#a88456', '#d4ab74', '#6a5032', '#f0cb90'),
        wall=('#e08a92', '#f8b4bc', '#8c4c54', '#ffffff'),
        roof=('#b82028', '#ef4444', '#681014', '#fca5a5'),
        palm=('#155e30', '#228e48', '#0a361a', '#4ade80'),
        agua='#1a345c',
        olas=('#fde68a', '#fb923c', '#3730a3'),
        reflejo=('#fef08a', '#fed7aa'),
        vig=0.80,
        nube=['#442442', '#623250', '#864456', '#ac5a5a', '#d07660', '#321832'],
    ),
    'dia': dict(
        sky=['#0c56a4', '#1870be', '#288ad6', '#3ea6e8', '#5cc0f2', '#82d6f8', '#aae8fc', '#ccf4fe', '#e6fafe', '#f8fcf4'],
        sand=('#c69e66', '#ecd098', '#86663c', '#fff0c4'),
        wall=('#ec98a2', '#ffc2ca', '#9e5862', '#ffffff'),
        roof=('#cc242c', '#f43f5e', '#761218', '#fda4af'),
        palm=('#15803d', '#22c55e', '#0c4a24', '#86efac'),
        agua='#0e68ac',
        olas=('#bae6fd', '#ffffff', '#0284c7'),
        reflejo=('#fff4c4', '#ffffff'),
        vig=0.88,
        nube=['#ffffff', '#eef8ff', '#dcf0fc', '#ffffff', '#e4f4fc', '#c2e0f4'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#fbbf24', '#38bdf8'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 36, halo='#fde68a', base='#fffbeb', sombra='#cbd5e1', crater='#94a3b8', crater_hi='#b8c4d8'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe49e', centro='#fffef2', borde='#ffb448', rayo='#ffd88c'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffffff', '#fef08a', '#bae6fd'])

MX, MY, MR = 344, 68, 34
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#fde68a', base='#fffbeb', sombra='#cbd5e1', crater='#94a3b8', crater_hi='#b8c4d8')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 344, 118, 22, halo='#ff9860', centro='#fff2d8', borde='#ff562e', rayo='#ff824a')
    else:
        dibuja_sol_estandar(lz, 344, 72, 22, halo='#ffe49e', centro='#fffef2', borde='#ffb448', rayo='#ffd88c')

NUBES_DEF = [
    (96, 48, 82, PAL['nube'][1], 2),
    (524, 56, 84, PAL['nube'][3], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)


def dibuja_kame_house_isla():
    """Isla tropical + icónica Kame House rosa y roja + palmeras + Nube Kinto + Esfera 4 Estrellas."""
    sd0, sd1, sd2, sd3 = PAL['sand']
    wl0, wl1, wl2, wh = PAL['wall']
    rf0, rf1, rf2, rf3 = PAL['roof']
    pm0, pm1, pm2, pm3 = PAL['palm']

    # Isla arenosa a la izquierda-centro (cx=186, HOR=280)
    for x in range(62, 314):
        u = (x - 188) / 126.0
        if abs(u) <= 1.0:
            h_i = int(14 * math.sqrt(max(0.0, 1.0 - u * u)))
            for y in range(HOR - h_i, HOR + 1):
                put(x, y, sd3 if y < HOR - h_i + 3 else (sd1 if (x + y) % 5 else sd0))

    # Kame House (x=148..224, base_y=270)
    hx = 186
    for y in range(214, 270):
        for x in range(hx - 36, hx + 37):
            col = wl2 if x in (hx - 36, hx + 36) else (wl1 if y % 4 != 0 else wl0)
            put(x, y, col)
    # Tejado rojo a dos aguas + buhardilla
    for dy in range(26):
        hw = 22 + int(dy * 0.85)
        for dx in range(-hw, hw + 1):
            put(hx + dx, 190 + dy, rf2 if abs(dx) >= hw - 1 else (rf3 if dy < 4 else (rf1 if dy % 4 else rf0)))
    # Puerta, ventanas con luz cálida y letrero KAME amarillo
    for dy in range(20):
        for dx in range(-7, 8):
            put(hx + dx, 250 + dy, '#78350f' if abs(dx) < 6 else wh)
    for wx in (hx - 23, hx + 23):
        for dy in range(-7, 7):
            for dx in range(-7, 8):
                put(wx + dx, 238 + dy, wh if (abs(dx) >= 6 or abs(dy) >= 5 or dx == 0 or dy == 0) else '#fef08a')
    for dx in range(-14, 15):
        for dy in range(-4, 5):
            put(hx + dx, 224 + dy, '#0f172a' if abs(dx) == 14 or abs(dy) == 4 else '#facc15')
    if ANIM:
        VENTANAS.append([hx - 23, 238, 2])
        VENTANAS.append([hx + 23, 238, 2])

    # Chimenea + humo
    for y in range(180, 196):
        for dx in range(-4, 5):
            put(hx + 20 + dx, y, '#64748b' if dx < 0 else '#334155')
    global CHIMENEA
    CHIMENEA = [hx + 20, 178]

    # Palmeras tropicales junto a Kame House (cx=128, 248)
    for px_p, dir_p in ((124, -1), (252, 1)):
        for k in range(56):
            tx = px_p + dir_p * int((k * k) * 0.005)
            ty = 272 - k
            for dx in range(-2, 3):
                put(tx + dx, ty, '#78350f' if (k % 5) else '#451a03')
        top_x = px_p + dir_p * 15
        top_y = 216
        for ang_d in (-150, -110, -40, 10, 145):
            a = math.radians(ang_d)
            for k in range(22):
                lx_f = int(top_x + math.cos(a) * k)
                ly_f = int(top_y + math.sin(a) * k * 0.65 + (k * k) * 0.025)
                disc(lx_f, ly_f, 2 if k < 14 else 1, pm3 if k % 3 == 0 else pm1)

    # Isla rocosa derecha con la Esfera de 4 Estrellas gigante brillando (cx=420, by=HOR=280)
    for x in range(382, 464):
        u = (x - 422) / 41.0
        h_r = int(16 * math.sqrt(max(0.0, 1.0 - u * u)))
        for y in range(HOR - h_r, HOR + 1):
            put(x, y, sd2 if (x + y) % 5 == 0 else sd0)
    bx, by_b = 422, 256
    if not ANIM:
        glow(bx, by_b, 24, '#f59e0b', 0.65)
    disc(bx, by_b, 14, '#ea580c')
    disc(bx - 2, by_b - 2, 11, '#f59e0b')
    disc(bx - 3, by_b - 3, 8, '#fbbf24')
    disc(bx - 6, by_b - 6, 3, '#fffbeb')
    for sx, sy in ((-4, -3), (4, -3), (-3, 4), (4, 4)):
        disc(bx + sx, by_b + sy, 1, '#dc2626')
    if ANIM:
        RUNAS.append([bx, by_b])
        FAROLES.append([bx, by_b, 12])

    # Nube Voladora Kinto en el cielo con silueta dorada (cx=238, cy=124)
    kx, ky = 242, 128
    if not ANIM:
        glow(kx, ky, 22, '#fde047', 0.45)
    for ox_c, oy_c, rc in ((-14, 2, 7), (-4, -1, 9), (8, 0, 8), (18, 2, 6)):
        disc(kx + ox_c, ky + oy_c, rc, '#f59e0b')
        disc(kx + ox_c - 1, ky + oy_c - 2, max(2, rc - 2), '#fef08a')
    for k in range(36):
        put(kx - 20 - k, ky + 3 + int(math.sin(k * 0.4)), '#fde047' if k < 18 else '#f97316')
    # Niño Goku encima de la nube Kinto
    for dy in range(-14, -2):
        for dx in range(-3, 4):
            put(kx + 2 + dx, ky + dy, '#1e1b2e' if dy < -9 else ('#ef4444' if dy < -5 else '#1e293b'))


dibuja_kame_house_isla()

render_lago(lz, PAL['agua'], PAL['olas'], DESTELLOS, ANIM, mx=MX, hor=HOR, reflejo_cols=PAL['reflejo'])
aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
