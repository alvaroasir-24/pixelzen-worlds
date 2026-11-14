#!/usr/bin/env python3
"""PixelZen Worlds - Jujutsu Kaisen (Bloqueo): Calzada Ceremonial, Torii Bermellón, Sellos Ofuda y Dedo de Sukuna."""
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
random.seed(1103)

PALETAS = {
    'noche': dict(
        sky=['#050712', '#0a0f22', '#101836', '#18244a', '#22325e', '#2e4274', '#3c548a', '#4e68a0', '#6480b6', '#7e9ac8'],
        tree=('#0a1514', '#132422', '#060c0c', '#1e3632'),
        stone=('#222636', '#363c52', '#121620', '#505a76'),
        torii=('#8a1c24', '#bc2a34', '#4a0c12', '#e0464c'),
        pagoda=('#181a28', '#282c42', '#0d0e16', '#f59e0b'),
        ofuda=('#eadec4', '#b8ac94', '#dc2626'),
        water=('#0a1224', '#162442'),
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
        water=('#1c1a32', '#2e2a50'),
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
        water=('#204878', '#3468a4'),
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

MX, MY, MR = 320, 66, 36
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#c084fc', base='#faf5ff', sombra='#d4c4f0', crater='#9a86c8', crater_hi='#b8a4e0')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 320, 122, 22, halo='#ff9860', centro='#fff2d8', borde='#ff562e', rayo='#ff824a')
    else:
        dibuja_sol_estandar(lz, 320, 70, 22, halo='#ffe49e', centro='#fffef2', borde='#ffb448', rayo='#ffd88c')

NUBES_DEF = [
    (96, 48, 80, PAL['nube'][1], 2),
    (528, 56, 86, PAL['nube'][3], 2),
    (184, 88, 62, PAL['nube'][2], 1),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)


def dibuja_laderas_y_pagoda():
    """Cedros montañosos en el horizonte y pagoda de 3 pisos a la izquierda."""
    tr0, tr1, tr2, tr3 = PAL['tree']
    r_tr = Ruido(77)
    for x in range(W):
        valley = 84.0 * math.exp(-(((x - 320) / 92.0) ** 2))
        tree_h = int(142 + 24 * math.cos(x * 0.015) + 10 * math.sin(x * 0.055) + valley)
        for y in range(min(262, tree_h), 262):
            n = fbm(r_tr, x * 0.11 + (y // 6) * 1.37)
            canopy = 0.5 + 0.5 * math.sin(x * 0.32 + (y // 4) * 1.9) * math.cos(y * 0.27)
            sh = (y - tree_h) / float(max(1, 262 - tree_h))
            col = tr3 if (n > 0.64 and canopy > 0.52 and sh < 0.42) else (tr1 if (n * 0.6 + canopy * 0.4 > 0.50) else (tr0 if sh < 0.78 else tr2))
            put(x, y, col)

    pg0, pg1, pg2, pgl = PAL['pagoda']
    s0, s1, s2, _ = PAL['stone']
    px = 118
    for dx in range(-44, 45):
        for y in range(250, 263):
            put(px + dx, y, s2 if abs(dx) >= 42 else (s1 if y == 250 else s0))
    for tier, (ty, tw) in enumerate(((152, 20), (182, 28), (214, 36))):
        y_end = 250 if tier == 2 else ty + 30
        for y in range(ty, y_end):
            for dx in range(-(tw - 9), tw - 8):
                put(px + dx, y, pg2 if abs(dx) >= tw - 10 else pg0)
            if y == ty + 14:
                for wx in (-5, 4):
                    put(px + wx, y, pgl)
                    put(px + wx + 1, y, pgl)
        for dx in range(-tw, tw + 1):
            u = abs(dx) / float(tw)
            lift = int(6 * (u ** 2.2))
            for k in range(7):
                put(px + dx, ty - 2 + k - lift, pg2 if k == 0 else pg1)
    for y in range(126, 152):
        put(px, y, pg1)


def dibuja_torii_y_calzada(cx):
    """Calzada de piedra en perspectiva y=260..400 + Torii monumental + Dedo de Sukuna."""
    s0, s1, s2, s3 = PAL['stone']
    t0, t1, t2, t3 = PAL['torii']
    of0, of1, of_r = PAL['ofuda']
    wt0, wt1 = PAL['water']
    r_st = Ruido(1131)

    # 1. Estanque lateral y calzada central empedrada en perspectiva (y=260..400)
    for y in range(260, H):
        t = (y - 260) / float(H - 260)
        path_hw = int(66 + t * 140)
        row_band = int(y * (1.0 - 0.35 * t)) // 10
        for x in range(W):
            dx = x - cx
            n = fbm(r_st, x * 0.04 + y * 0.05)
            if abs(dx) <= path_hw:
                # Calzada de losas en perspectiva
                is_curb = abs(dx) >= path_hw - 4
                is_seam_y = ((y - 260) % max(5, int(6 + t * 14)) == 0)
                is_seam_x = ((int(dx / (0.4 + t * 0.9)) + row_band * 14) % 28 == 0)
                if is_curb:
                    col = s3 if (y % 6 < 3) else s1
                elif is_seam_y or is_seam_x:
                    col = s2
                else:
                    col = s3 if n > 0.65 else (s1 if n > 0.40 else s0)
            else:
                # Estanque oscuro reflejando los pilares del Torii y el santuario
                col = wt1 if (abs(dx - 64) < 18 or abs(dx + 64) < 18) and (y % 4 != 0) else wt0
                if (abs(dx - 64) < 10 or abs(dx + 64) < 10) and (y % 5 == 0) and dith(x, y, 0.55):
                    col = mix(col, t1, 0.45)
            put(x, y, col)

    # Escalinata superior bajo el Torii (y=244..266)
    for step in range(6):
        sy = 242 + step * 4
        sw = 62 + step * 8
        for dx in range(-sw, sw + 1):
            col = s2 if abs(dx) >= sw - 2 else (s3 if step % 2 == 0 and abs(dx) < sw - 4 else (s1 if (dx + step) % 5 else s0))
            for k in range(4):
                put(cx + dx, sy + k, col if k < 3 else s2)

    # 2. Gran Puerta Torii Bermellón (y=114..250)
    for px_o in (-62, 62):
        px = cx + px_o
        for y in range(116, 246):
            w_col = 7 if y < 224 else 9
            for dx in range(-w_col, w_col + 1):
                if y >= 224:
                    put(px + dx, y, s2 if abs(dx) == w_col else s0)
                else:
                    put(px + dx, y, t2 if abs(dx) >= w_col - 1 else (t3 if dx < -1 else (t1 if dx < 2 else t0)))
    for dx in range(-80, 81):
        for dy in range(-5, 6):
            put(cx + dx, 150 + dy, t2 if abs(dy) == 5 else (t1 if dy < 0 else t0))
    for dx in range(-96, 97):
        u = abs(dx) / 96.0
        lift = int(14 * (u ** 2.3))
        for dy in range(-7, 8):
            y_k = 118 + dy - lift
            col = '#181420' if dy < -3 else (t2 if abs(dy) == 7 else (t3 if dy < 0 else t1))
            put(cx + dx, y_k, col)
    for dy in range(-12, 13):
        for dx in range(-8, 9):
            put(cx + dx, 134 + dy, t2 if abs(dx) >= 7 or abs(dy) >= 11 else '#120c14')

    # Soga Shimenawa + 6 talismanes Ofuda
    for dx in range(-56, 57):
        sag = int(7 * (1.0 - (dx / 56.0) ** 2))
        put(cx + dx, 154 + sag, '#d4b888')
        put(cx + dx, 155 + sag, '#9e845a')
    for ox in (-44, -26, -12, 12, 26, 44):
        oy0 = 156 + int(7 * (1.0 - (ox / 56.0) ** 2))
        for dy in range(20):
            for dx in range(-2, 3):
                col = of1 if abs(dx) == 2 else (of_r if (dx == 0 and dy % 3 == 1 and 2 <= dy <= 16) else of0)
                put(cx + ox + dx, oy0 + dy, col)

    # 3. Linternas Toro en perspectiva a ambos lados de la calzada
    for lx, ly_base, sc in ((cx - 92, 268, 1.0), (cx + 92, 268, 1.0), (cx - 138, 344, 1.35), (cx + 138, 344, 1.35)):
        lh = int(42 * sc)
        for dy in range(lh):
            y = ly_base - lh + dy
            hw = int((6 if dy > lh - 12 else (5 if dy < 14 else 3)) * sc)
            for dx in range(-hw, hw + 1):
                put(lx + dx, y, s2 if abs(dx) == hw else (s3 if dx < 0 else s1))
        for dx in range(-int(8 * sc), int(9 * sc)):
            put(lx + dx, ly_base - lh - max(0, int(4 * sc) - abs(dx) // 2), s2)
        fy = ly_base - lh + int(10 * sc)
        if ANIM:
            FAROLES.append([lx, fy, int(8 * sc)])
        else:
            glow(lx, fy, int(8 * sc), '#fbbf24', 0.60)
            disc(lx, fy, int(2 * sc), '#fef3c7')

    # 4. Altar en primer plano + Relicario abierto + Dedo de Ryomen Sukuna a gran tamaño (cx=320, cy=304)
    for dy in range(26):
        y = 330 + dy
        hw = 34 + dy // 3
        for dx in range(-hw, hw + 1):
            put(cx + dx, y, s2 if abs(dx) >= hw - 2 else (s3 if dy < 4 else (s1 if (dx + dy) % 5 else s0)))
    # Caja relicario de madera con talismán Ofuda abierto
    for dy in range(18):
        for dx in range(-20, 21):
            put(cx + dx, 314 + dy, '#181018' if abs(dx) >= 18 or dy in (0, 17) else '#4e2a22')
            if abs(dx) <= 6 and dy > 3:
                put(cx + dx, 314 + dy, of0 if dy % 2 else of_r)
    # Dedo maldito grande (28 px alto, nudillos, vendas rojas rotas y garra negra curva)
    fx, fy = cx, 290
    if not ANIM:
        glow(fx, fy, 26, '#dc2626', 0.62)
        glow(fx, fy, 12, '#e879f9', 0.72)
    for dy in range(-14, 15):
        curve = int(3.0 * math.sin((dy + 14) * 0.16))
        rad = 4 if dy > 6 else (3 if dy > -8 else max(1, 3 - (-8 - dy) // 3))
        for dx in range(-rad, rad + 1):
            if dy <= -9:
                col = '#120810' if dx < 1 else '#382230'
            elif dy in (-3, 4):
                col = '#38121c'
            elif dy > 4:
                col = '#7a1c24' if dx >= 0 else '#b8323e'
            else:
                col = '#dcb096' if dx < 0 else ('#a87058' if dx < rad else '#4a2622')
            put(fx + curve + dx, fy + dy, col)
    if ANIM:
        RUNAS.append([fx, fy])


dibuja_laderas_y_pagoda()
dibuja_torii_y_calzada(320)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
