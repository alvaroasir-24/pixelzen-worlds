#!/usr/bin/env python3
"""PixelZen Worlds - Jujutsu Kaisen (Bloqueo): Torii Sagrado, Sellos Ofuda y Dedo de Ryomen Sukuna."""
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
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1103)

PALETAS = {
    'noche': dict(
        sky=['#050712', '#0a0f22', '#101836', '#18244a', '#22325e', '#2e4274', '#3c548a', '#4e68a0', '#6480b6', '#7e9ac8'],
        tree=('#0a1514', '#132422', '#060c0c', '#1e3632'),
        stone=('#242838', '#383e54', '#141822', '#525c78'),
        torii=('#8a1c24', '#b82832', '#4c0c12', '#dc4248'),
        pagoda=('#181a28', '#282c42', '#0d0e16', '#f59e0b'),
        ofuda=('#e8dec4', '#b8ac94', '#dc2626'),
        agua='#091224',
        olas=('#f87171', '#a855f7', '#3b0764'),
        reflejo=('#fecaca', '#c4b5fd'),
        vig=0.72,
        nube=['#16223c', '#223254', '#2e426c', '#3c5484', '#4e689c', '#10182e'],
    ),
    'dorado': dict(
        sky=['#140e24', '#26183a', '#3e244c', '#5e3456', '#844856', '#ac604c', '#d27e46', '#f0a04c', '#ffc464', '#ffe294'],
        tree=('#141e18', '#223226', '#0a100c', '#324a36'),
        stone=('#342c38', '#4c4252', '#1e1822', '#6e6074'),
        torii=('#a42028', '#d4343c', '#5a1014', '#f25856'),
        pagoda=('#241e2e', '#382e46', '#14101c', '#fbbf24'),
        ofuda=('#f4ead4', '#c8b89e', '#ef4444'),
        agua='#1e1c36',
        olas=('#fca5a5', '#c084fc', '#4c1d95'),
        reflejo=('#fde68a', '#f9a8d4'),
        vig=0.80,
        nube=['#442644', '#603452', '#82465a', '#a65c5e', '#ca7862', '#321a34'],
    ),
    'dia': dict(
        sky=['#1a4e92', '#2864ac', '#3c7cc2', '#5696d6', '#74b0e4', '#94c8ee', '#b2def6', '#ceeefa', '#e4f5fc', '#f4f8ef'],
        tree=('#1c422c', '#2c603e', '#10281a', '#3e7c52'),
        stone=('#525a6c', '#707a90', '#343a48', '#96a2ba'),
        torii=('#b8282c', '#e43c3c', '#6e1418', '#ff645c'),
        pagoda=('#2e3446', '#444c66', '#1c202c', '#f59e0b'),
        ofuda=('#fcf6e8', '#d4cab4', '#dc2626'),
        agua='#225288',
        olas=('#bae6fd', '#fca5a5', '#4f46e5'),
        reflejo=('#fff4c4', '#fecaca'),
        vig=0.88,
        nube=['#ffffff', '#eef6fc', '#dff0fa', '#f8fcff', '#e4f0fb', '#c8e0f0'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#ef4444', '#a855f7'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#c084fc', base='#faf5ff', sombra='#d4c4f0', crater='#9a86c8', crater_hi='#b8a4e0'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe49e', centro='#fffef2', borde='#ffb448', rayo='#ffd88c'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#f3e8ff', '#e0f2fe', '#ffe4e6'])

MX, MY, MR = 320, 68, 36
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#c084fc', base='#faf5ff', sombra='#d4c4f0', crater='#9a86c8', crater_hi='#b8a4e0')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 320, 128, 22, halo='#ff9860', centro='#fff2d8', borde='#ff562e', rayo='#ff824a')
    else:
        dibuja_sol_estandar(lz, 320, 72, 22, halo='#ffe49e', centro='#fffef2', borde='#ffb448', rayo='#ffd88c')

NUBES_DEF = [
    (96, 48, 80, PAL['nube'][1], 2),
    (528, 56, 86, PAL['nube'][3], 2),
    (184, 88, 62, PAL['nube'][2], 1),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)


def dibuja_laderas_y_pagoda():
    """Cedros montañosos con valle suave central y pagoda apoyada en la orilla izquierda."""
    tr0, tr1, tr2, tr3 = PAL['tree']
    r_tr = Ruido(77)
    for x in range(W):
        valley = 82.0 * math.exp(-(((x - 320) / 86.0) ** 2))
        tree_h = int(148 + 26 * math.cos(x * 0.015) + 10 * math.sin(x * 0.055) + valley)
        for y in range(min(HOR, tree_h), HOR):
            n = fbm(r_tr, x * 0.11 + (y // 6) * 1.37)
            canopy = 0.5 + 0.5 * math.sin(x * 0.32 + (y // 4) * 1.9) * math.cos(y * 0.27)
            sh = (y - tree_h) / float(max(1, HOR - tree_h))
            col = tr3 if (n > 0.64 and canopy > 0.52 and sh < 0.42) else (tr1 if (n * 0.6 + canopy * 0.4 > 0.50) else (tr0 if sh < 0.78 else tr2))
            put(x, y, col)

    # Pagoda apoyada firmemente sobre su terraza de piedra en HOR=280 (cx=128)
    pg0, pg1, pg2, pgl = PAL['pagoda']
    s0, s1, s2, _ = PAL['stone']
    px = 128
    for dx in range(-40, 41):
        for y in range(HOR - 12, HOR + 1):
            put(px + dx, y, s2 if abs(dx) >= 38 else (s1 if y == HOR - 12 else s0))
    for tier, (ty, tw) in enumerate(((166, 18), (196, 26), (228, 34))):
        y_end = HOR - 12 if tier == 2 else ty + 30
        for y in range(ty, y_end):
            for dx in range(-(tw - 8), tw - 7):
                put(px + dx, y, pg2 if abs(dx) >= tw - 9 else pg0)
            if y == ty + 14:
                for wx in (-4, 4):
                    put(px + wx, y, pgl)
                    put(px + wx + 1, y, pgl)
        for dx in range(-tw, tw + 1):
            u = abs(dx) / float(tw)
            lift = int(5 * (u ** 2.2))
            for k in range(7):
                put(px + dx, ty - 2 + k - lift, pg2 if k == 0 else pg1)
    for y in range(140, 166):
        put(px, y, pg1)


def dibuja_torii_y_altar(cx, by):
    """Puerta Torii bermellón con talismanes Ofuda y Dedo de Sukuna sobre HOR=280."""
    t0, t1, t2, t3 = PAL['torii']
    s0, s1, s2, s3 = PAL['stone']
    of0, of1, of_r = PAL['ofuda']

    # Escalinata ceremonial en la base (y = by-26 .. by)
    for step in range(6):
        sy = by - 25 + step * 4
        sw = 62 + step * 9
        for dx in range(-sw, sw + 1):
            col = s2 if abs(dx) >= sw - 2 else (s3 if step % 2 == 0 and abs(dx) < sw - 4 else (s1 if (dx + step) % 5 else s0))
            for k in range(4):
                put(cx + dx, sy + k, col if k < 3 else s2)

    # Pilares del Torii (y = 128 .. by-24)
    for px_o in (-56, 56):
        px = cx + px_o
        for y in range(128, by - 22):
            w_col = 6 if y < by - 40 else 8
            for dx in range(-w_col, w_col + 1):
                if y >= by - 40:
                    put(px + dx, y, s2 if abs(dx) == w_col else s0)
                else:
                    put(px + dx, y, t2 if abs(dx) >= w_col - 1 else (t3 if dx < -1 else (t1 if dx < 2 else t0)))

    # Travesaños del Torii (Nuki y Kasagi)
    for dx in range(-72, 73):
        for dy in range(-4, 5):
            put(cx + dx, 158 + dy, t2 if abs(dy) == 4 else (t1 if dy < 0 else t0))
    for dx in range(-86, 87):
        u = abs(dx) / 86.0
        lift = int(12 * (u ** 2.3))
        for dy in range(-6, 7):
            y_k = 128 + dy - lift
            col = '#1a1622' if dy < -3 else (t2 if abs(dy) == 6 else (t3 if dy < 0 else t1))
            put(cx + dx, y_k, col)
    for dy in range(-11, 12):
        for dx in range(-7, 8):
            put(cx + dx, 143 + dy, t2 if abs(dx) >= 6 or abs(dy) >= 10 else '#120c14')

    # Soga Shimenawa y 4 sellos Ofuda
    for dx in range(-50, 51):
        sag = int(6 * (1.0 - (dx / 50.0) ** 2))
        put(cx + dx, 162 + sag, '#d4b888')
        put(cx + dx, 163 + sag, '#9e845a')
    for ox in (-36, -18, 18, 36):
        oy0 = 164 + int(6 * (1.0 - (ox / 50.0) ** 2))
        for dy in range(18):
            for dx in range(-2, 3):
                col = of1 if abs(dx) == 2 else (of_r if (dx == 0 and dy % 3 == 1 and 2 <= dy <= 14) else of0)
                put(cx + ox + dx, oy0 + dy, col)

    # Linternas de piedra japonesas Toro junto al Torii sobre HOR=280
    for lx in (cx - 98, cx + 98):
        for y in range(by - 48, by):
            hw = 5 if y > by - 16 else (4 if y < by - 36 else 3)
            for dx in range(-hw, hw + 1):
                put(lx + dx, y, s2 if abs(dx) == hw else s1)
        for dx in range(-8, 9):
            put(lx + dx, by - 48 - max(0, 4 - abs(dx) // 2), s2)
        if ANIM:
            FAROLES.append([lx, by - 38, 8])
        else:
            glow(lx, by - 38, 7, '#fbbf24', 0.55)
            disc(lx, by - 38, 2, '#fef3c7')

    # Cofre ritual + Dedo maldito de Sukuna levitando en el centro (cy = by - 50)
    for dy in range(14):
        for dx in range(-14, 15):
            put(cx + dx, by - 32 + dy, '#1a121c' if abs(dx) >= 12 or dy in (0, 13) else '#4c2c24')
            if abs(dx) <= 4 and dy > 2:
                put(cx + dx, by - 32 + dy, of0 if dy % 2 else of_r)
    fx, fy = cx, by - 50
    for dy in range(-10, 9):
        curve = int(2 * math.sin((dy + 10) * 0.24))
        for dx in range(-2, 3):
            col = '#5c141c' if dy > 1 else ('#c0846c' if dx < 0 else '#7e483c')
            if dy <= -7 and dx == 0:
                col = '#140c14'
            put(fx + curve + dx, fy + dy, col)
    if ANIM:
        RUNAS.append([fx, fy])
    else:
        glow(fx, fy, 12, '#dc2626', 0.58)
        glow(fx, fy, 5, '#e879f9', 0.65)


dibuja_laderas_y_pagoda()
dibuja_torii_y_altar(320, HOR)

render_lago(lz, PAL['agua'], PAL['olas'], DESTELLOS, ANIM, mx=MX, hor=HOR, reflejo_cols=PAL['reflejo'])
aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
