#!/usr/bin/env python3
"""PixelZen Worlds - Spider-Man: Miles Morales (Monitor 2): Midtown, Metro Elevado y Harlem."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    exporta_salida, exporta_sprites_si_aplica, render_cielo,
    render_estrellas, render_lago, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(16102)

PALETAS = {
    'noche': dict(
        sky=['#04030e', '#0a071d', '#120b2e', '#1e1042', '#2d1656', '#401c68', '#582472', '#742e76', '#943c76', '#b85076'],
        sky_far=('#16142c', '#201d3c', '#2d2952'),
        sky_mid=('#100e22', '#181530', '#262146'),
        brick=('#3a1b24', '#4e242e', '#261018'),
        concrete=('#282638', '#3a3752', '#1a1826'),
        steel=('#161824', '#282c40'),
        neon_r='#ff2a55',
        neon_c='#00e5ff',
        neon_y='#ffd840',
        agua='#060818',
        ola=('#5ce0ff', '#ff4a88', '#262456'),
        vig=0.72,
        nube=['#382854', '#4e366e', '#684480', '#8a5488', '#a6688c', '#302248'],
    ),
    'dorado': dict(
        sky=['#140826', '#240c3a', '#3b124e', '#5a1a5e', '#802464', '#aa325e', '#d24852', '#ee6a48', '#fc9246', '#ffc266'],
        sky_far=('#3a2444', '#4c3056', '#664270'),
        sky_mid=('#261630', '#362042', '#4c305a'),
        brick=('#5c2428', '#7c3234', '#3c161a'),
        concrete=('#403044', '#5a445e', '#2a1e2e'),
        steel=('#241a2a', '#3c2c42'),
        neon_r='#ff3660',
        neon_c='#24ecff',
        neon_y='#ffe058',
        agua='#1a102a',
        ola=('#ff9884', '#70b8e0', '#382a58'),
        vig=0.80,
        nube=['#6e325c', '#984266', '#c65864', '#ea7a5e', '#fca266', '#5a284e'],
    ),
    'dia': dict(
        sky=['#1a52a8', '#2868bc', '#3c80ce', '#5498de', '#72b0ea', '#94c6f0', '#b6daf4', '#d4e8f2', '#eceee4', '#faf0d2'],
        sky_far=('#5c7296', '#728aa8', '#8ea6c2'),
        sky_mid=('#3e5070', '#506488', '#687ea2'),
        brick=('#7c3638', '#9c4848', '#582426'),
        concrete=('#686e82', '#848aa0', '#4c5264'),
        steel=('#32384a', '#4e566c'),
        neon_r='#ff2a55',
        neon_c='#00d2ee',
        neon_y='#ffca38',
        agua='#1c486e',
        ola=('#bfe8f8', '#5c94be', '#2a5680'),
        vig=0.90,
        nube=['#ffffff', '#f2f6fa', '#ffffff', '#e6eff6', '#faf8f2', '#dce8f4'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#ff2a55', '#00e5ff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 44, halo='#8ec8f4', base='#f6f8ff', sombra='#cad8ec', crater='#a2b4ce', crater_hi='#bacae0'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 24, halo='#ffd888', centro='#fffdf0', borde='#ffb84c', rayo='#ffe088'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffdce8', '#cceeff', '#e0d4ff'])

MX, MY, MR = 294, 80, 44
CX_ASTRO = MX if FASE == 'noche' else (MX + 44 if FASE == 'dorado' else MX - 45)
# Monitor 2 comparte cielo con Monitor 1: no duplicar sol/luna aquí

NUBES_DEF = [
    (120, 56, 170, PAL['nube'][0], 3),
    (340, 92, 155, PAL['nube'][1], 3),
    (520, 146, 165, PAL['nube'][2], 3),
    (220, 190, 175, PAL['nube'][3], 3),
    (460, 236, 130, PAL['nube'][4], 2),
    (80, 244, 110, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 3. Rascacielos lejanos de Midtown (x = 40..420)
WARM = '#ffd26a'
def torre(x0, w_t, h_t, cols, con_aguja=False):
    y0 = HOR - h_t
    for yy in range(y0, HOR + 1):
        for x in range(x0, x0 + w_t):
            c = cols[2] if x < x0 + w_t // 4 else (cols[1] if x < x0 + 3 * w_t // 4 else cols[0])
            put(x, yy, c)
    for wy in range(y0 + 8, HOR - 16, 10):
        for wx in range(x0 + 4, x0 + w_t - 4, 7):
            if (wx + wy) % 3 == 0:
                if ANIM:
                    VENTANAS.append([wx, wy])
                else:
                    put(wx, wy, WARM)
                    put(wx + 1, wy, WARM)
    if con_aguja:
        cx = x0 + w_t // 2
        for i in range(14):
            hw = max(2, w_t // 2 - i // 2)
            for x in range(cx - hw, cx + hw + 1):
                put(x, y0 - i, cols[2])
        for yy in range(y0 - 38, y0 - 14):
            put(cx, yy, cols[2])
        if ANIM:
            RUNAS.append([cx, y0 - 39])
        else:
            put(cx, y0 - 39, PAL['neon_r'])
            glow(cx, y0 - 39, 5, PAL['neon_r'], 0.65)

# Capa lejana
for bx, bw, bh, ag in ((44, 24, 92, False), (76, 30, 128, True), (118, 22, 84, False), (150, 36, 146, True), (196, 26, 102, False), (234, 34, 118, False), (280, 28, 96, False), (322, 38, 134, True)):
    torre(bx, bw, bh, PAL['sky_far'], ag)

# Capa media
for bx, bw, bh, ag in ((58, 28, 76, False), (104, 32, 98, False), (178, 34, 112, True), (254, 30, 88, False), (356, 32, 106, False)):
    torre(bx, bw, bh, PAL['sky_mid'], ag)

# 4. Viaducto del Metro Elevado de Harlem (y = 228..238, x = 220..640)
ST0, ST1 = PAL['steel']
for x in range(220, W):
    for yy in range(228, 236):
        put(x, yy, ST1 if yy in (228, 235) else ST0)
    if x % 36 == 0:
        for yy in range(236, HOR + 1):
            for dx in (-2, -1, 0, 1, 2):
                put(x + dx, yy, ST0 if dx >= 0 else ST1)

# Tren elevado iluminado sobre el viaducto (x = 270..410)
for cx_car in (280, 326, 372):
    for yy in range(214, 228):
        for x in range(cx_car, cx_car + 40):
            put(x, yy, PAL['concrete'][1] if yy < 217 else PAL['concrete'][0])
    for x in range(cx_car + 2, cx_car + 38):
        put(x, 221, PAL['neon_c'])
    for wx in range(cx_car + 5, cx_car + 36, 7):
        if ANIM:
            VENTANAS.append([wx, 217])
        else:
            put(wx, 217, WARM)
            put(wx + 1, 217, WARM)
if ANIM:
    FAROLES.append([279, 222, 9])

# 5. Edificios Brownstone de Harlem (derecha, x = 448..640)
BR0, BR1, BR2 = PAL['brick']
for bx, bw, bh in ((452, 46, 128), (500, 52, 146), (554, 48, 134), (604, 36, 152)):
    by0 = HOR - bh
    for yy in range(by0, HOR + 1):
        for x in range(bx, min(W, bx + bw)):
            c = BR1 if (x // 4 + yy // 3) % 2 == 0 else BR0
            if yy < by0 + 4:
                c = PAL['concrete'][1]
            put(x, yy, c)
    for wy in range(by0 + 12, HOR - 18, 16):
        for wx in range(bx + 7, min(W - 4, bx + bw - 6), 11):
            if ANIM:
                VENTANAS.append([wx, wy])
            else:
                for dy in range(4):
                    put(wx, wy + dy, WARM)
                    put(wx + 1, wy + dy, WARM)

# Cartel neón Spider-Verse en azotea de Harlem (x = 508..548, y = 116..134)
for yy in range(114, 134):
    for x in range(506, 548):
        put(x, yy, '#120e1e')
for x in range(506, 548):
    put(x, 114, PAL['neon_r'])
    put(x, 133, PAL['neon_c'])
# Emblema araña pixel art dentro del cartel
for dx, dy in ((0, -3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (-1, -1), (1, -1), (-2, -2), (2, -2), (-3, -3), (3, -3), (-2, 1), (2, 1), (-3, 2), (3, 2), (-4, 3), (4, 3)):
    put(527 + dx, 124 + dy, PAL['neon_r'])
if ANIM:
    RUNAS.append([508, 116])
    RUNAS.append([545, 131])
    FAROLES.append([486, 150, 9])
CHIMENEA = [616, HOR - 166]

# Depósito de agua en azotea (x = 468)
for yy in range(HOR - 146, HOR - 128):
    for x in range(466, 480):
        put(x, yy, BR2 if x < 473 else BR0)
for yy in range(HOR - 152, HOR - 146):
    hw = 7 - (HOR - 146 - yy)
    for x in range(473 - hw, 473 + hw + 1):
        put(x, yy, BR1)

# 6. Reflejo en el East River (sin columna duplicada de sol/luna)
render_lago(lz, PAL['agua'], PAL['ola'], DESTELLOS, ANIM, mx=CX_ASTRO, reflejo_cols=(PAL['neon_c'], PAL['neon_r']), reflejo_astro=False)

aplica_vineta(lz, PAL['vig'])
out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
