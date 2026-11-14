#!/usr/bin/env python3
"""PixelZen Worlds - Jujutsu Kaisen (Monitor 2): Incidente de Shibuya, Prisión Confinadora, Itadori y Fushiguro."""
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
random.seed(1102)

PALETAS = {
    'noche': dict(
        sky=['#040612', '#080c20', '#0e1634', '#162048', '#202c60', '#2b3a76', '#384c8e', '#485ea4', '#5c72ba', '#7488d0'],
        bldg=('#101526', '#1c243c', '#080b14', '#2a3656'),
        cyl=('#222a46', '#364268', '#14192a', '#4e5f92'),
        neon=('#38bdf8', '#f43f5e', '#a855f7', '#facc15'),
        cube=('#1d1426', '#38294a', '#685080', '#f1f5f9', '#e11d48'),
        road=('#0f1320', '#181e30', '#080a12', '#262f48'),
        itadori=('#19223e', '#e11d48', '#f6d2c0', '#fb7185', '#0d101c'),
        megumi=('#172034', '#263454', '#f0cec0', '#141824', '#38bdf8'),
        vig=0.74,
        nube=['#161f3a', '#212e52', '#2e3e6c', '#3c4e84', '#4c609c', '#10162c'],
    ),
    'dorado': dict(
        sky=['#141028', '#26183c', '#3e224e', '#5c2e5a', '#7c3e5e', '#a25458', '#c87250', '#e89650', '#ffba62', '#ffe094'],
        bldg=('#1e1a2c', '#302844', '#120f1c', '#44385c'),
        cyl=('#342a48', '#50406c', '#201a30', '#6e5894'),
        neon=('#38bdf8', '#fb7185', '#c084fc', '#fde047'),
        cube=('#261a30', '#443054', '#76588c', '#f8fafc', '#f43f5e'),
        road=('#1a1828', '#282438', '#100e18', '#3c3650'),
        itadori=('#1e2644', '#f43f5e', '#f8d6c4', '#fb7185', '#10121e'),
        megumi=('#1e263c', '#2e3a58', '#f4d2c4', '#161a26', '#38bdf8'),
        vig=0.82,
        nube=['#402446', '#5a3254', '#7a425c', '#9e5662', '#c4726a', '#301a36'],
    ),
    'dia': dict(
        sky=['#1d4e92', '#2d64aa', '#407cc0', '#5a94d4', '#78aee4', '#96c6ee', '#b4dcf6', '#d0ecf8', '#e6f4fc', '#f4f8ee'],
        bldg=('#2d3852', '#425070', '#1d2438', '#5c6e94'),
        cyl=('#4c5c82', '#687ca8', '#323e5c', '#8ca2d0'),
        neon=('#0284c7', '#e11d48', '#9333ea', '#eab308'),
        cube=('#2e243a', '#4c3e5e', '#7c6892', '#ffffff', '#e11d48'),
        road=('#283244', '#38465e', '#1a202c', '#4e607c'),
        itadori=('#202b48', '#e11d48', '#f8d6c4', '#fb7185', '#141824'),
        megumi=('#202a42', '#324264', '#f4d2c4', '#161c2a', '#0ea5e9'),
        vig=0.88,
        nube=['#ffffff', '#eef6fc', '#deeffa', '#f8fcff', '#e4f0fb', '#c6ddf0'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#818cf8', '#f43f5e'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#818cf8', base='#f5f8ff', sombra='#bccbe8', crater='#8898c0', crater_hi='#a4b4d8'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe4a0', centro='#fffef2', borde='#ffb448', rayo='#ffd88c'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#e0e7ff', '#fbcfe8', '#bae6fd'])

# Cúpula del Velo (Tobari) sobre el distrito de Shibuya
for y in range(16, 200):
    t_v = max(0.0, 1.0 - abs(y - 72) / 138.0)
    arc_x = int(math.sin((y / 200.0) * math.pi) * 288)
    for x in range(max(0, 316 - arc_x), min(W, 316 + arc_x)):
        d_edge = abs(abs(x - 316) - arc_x)
        if d_edge < 4:
            over(x, y, '#818cf8' if (x + y) % 3 else '#c084fc', 0.48 * t_v)

MX, MY, MR = 316, 66, 36
NUBES_DEF = [
    (92, 48, 82, PAL['nube'][1], 2),
    (226, 62, 74, PAL['nube'][2], 1),
    (436, 54, 82, PAL['nube'][3], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)


def dibuja_shibuya_109(cx):
    """Torre cilíndrica Shibuya 109 sobre y=92..258."""
    c0, c1, c2, c3 = PAL['cyl']
    for y in range(92, 258):
        for dx in range(-36, 37):
            if y < 120 and abs(dx) > 24:
                continue
            u = dx / 36.0
            sh = 0.5 + 0.5 * (-u * 0.72)
            col = c3 if sh > 0.75 else (c1 if sh > 0.45 else (c0 if sh > 0.2 else c2))
            put(cx + dx, y, col)
            if y % 12 == 0 and abs(dx) < 34:
                put(cx + dx, y, c2)
            elif (y % 12 in (4, 5)) and (dx % 7 in (1, 2, 3)) and y > 126:
                put(cx + dx, y, PAL['neon'][0] if (cx + y) % 3 else PAL['neon'][1])
    # Rótulo circular luminoso 109
    cy_l = 152
    disc(cx, cy_l, 17, '#120820')
    for ang_i in range(60):
        a = (ang_i / 60.0) * 2 * math.pi
        put(cx + int(round(17 * math.cos(a))), cy_l + int(round(17 * math.sin(a))), PAL['neon'][1])
    for dy in range(-6, 7):
        put(cx - 9, cy_l + dy, '#fff0f5')
        for dx in range(-3, 4):
            if abs(dx) == 3 or abs(dy) == 6:
                put(cx + dx, cy_l + dy, '#fff0f5')
        for dx in range(6, 12):
            if dy in (-6, 0, 6) or dx == 11 or (dy < 0 and dx == 6):
                put(cx + dx, cy_l + dy, '#fff0f5')
    if ANIM:
        FAROLES.append([cx, cy_l, 10])
    else:
        glow(cx, cy_l, 14, PAL['neon'][1], 0.45)


def dibuja_skyline_shibuya():
    """Rascacielos y carteles de neón sobre y=116..258 (sin tapar HUD derecha)."""
    b0, b1, b2, b3 = PAL['bldg']
    bloques = [
        (0, 66, 134, 0), (150, 56, 126, 1), (210, 48, 152, 2),
        (376, 54, 146, 3), (434, 44, 156, 0), (482, 54, 212, 1), (540, 52, 218, 2), (594, 46, 222, 0),
    ]
    for x0, bw, top_y, n_idx in bloques:
        for y in range(top_y, 258):
            for x in range(x0, min(W, x0 + bw)):
                edge = (x == x0 or x == x0 + bw - 1 or y == top_y)
                is_floor = ((y - top_y) % 10 == 0)
                put(x, y, b2 if edge else (b1 if is_floor else b0))
                if (x - x0) > 4 and (x - x0) < bw - 4 and (x - x0) % 7 in (2, 3) and (y - top_y) > 8 and (y - top_y) % 10 == 4:
                    if ((x * 5 + y * 9) % 4) == 0:
                        nc = PAL['neon'][(n_idx + x) % 4]
                        put(x, y, nc)
                        if len(VENTANAS) < 40 and x % 2 == 0:
                            VENTANAS.append([x, y, 2])
        if bw >= 50 and top_y < 165:
            vx = x0 + bw - 9
            for vy in range(top_y + 20, min(244, top_y + 78)):
                for dx in range(-3, 4):
                    put(vx + dx, vy, '#0c081a' if abs(dx) == 3 else PAL['neon'][n_idx % 4])
            if ANIM:
                FAROLES.append([vx, top_y + 46, 6])
    # Entrada luminosa de la Estación de Shibuya en el centro-fondo (x=270..362, y=224..258)
    for y in range(224, 258):
        for x in range(268, 366):
            is_frame = (x < 274 or x > 360 or y < 232)
            put(x, y, b3 if is_frame else ('#1e293b' if y < 246 else '#070a14'))
    for x in range(278, 356, 3):
        put(x, 227, '#f8fafc' if (x % 6) else PAL['neon'][0])
        put(x, 228, PAL['neon'][0])


def dibuja_cruce_shibuya():
    """Cruce Scramble de Shibuya en perspectiva y=256..400 con pasos de cebra, charcos de neón y cráter central."""
    rd0, rd1, rd2, rd3 = PAL['road']
    r_p = Ruido(1122)
    for y in range(256, H):
        t = (y - 256) / float(H - 256)
        for x in range(W):
            n = fbm(r_p, x * 0.03 + y * 0.04)
            dx_c = x - 314
            # Acera en el fondo + pasos de cebra convergentes hacia el espectador
            if y < 268:
                col = rd3 if y < 260 else rd1
            else:
                zebra_left = (-180 * (0.4 + t * 0.85) < dx_c < -38 * (0.35 + t * 0.7)) and (((dx_c + int(y * 0.9)) // int(14 + 10 * t)) % 2 == 0) and (0.18 < t < 0.74)
                zebra_diag = (abs(dx_c) < 220 * (0.25 + t)) and ((y // int(8 + 6 * t)) % 2 == 0) and (0.76 < t < 0.94) and (abs(dx_c) > 24)
                if zebra_left or zebra_diag:
                    col = '#94a3b8' if n > 0.45 else '#64748b'
                else:
                    col = rd1 if n > 0.52 else (rd0 if n > 0.30 else rd2)
                # Reflejos húmedos de carteles de neón sobre el asfalto mojado
                if (x % 4 == 0) and (60 < x < 160) and n > 0.55 and y > 282:
                    col = mix(col, PAL['neon'][1], 0.42)
                elif (x % 4 == 0) and (440 < x < 560) and n > 0.55 and y > 282:
                    col = mix(col, PAL['neon'][0], 0.38)
            put(x, y, col)

    # Gran cráter radial donde se abrió Gokumonkyo (cx=314, cy=324)
    for dy in range(-28, 30):
        for dx in range(-86, 87):
            ell = math.hypot(dx / 86.0, dy / 28.0)
            if 0.72 <= ell <= 0.98 and dith(314 + dx, 324 + dy, 0.80):
                put(314 + dx, 324 + dy, rd3 if dy > 0 else '#475569')
            elif ell < 0.72:
                put(314 + dx, 324 + dy, '#050710' if ell < 0.45 else rd2)
                if ell > 0.45 and abs(dx) % 13 == 0:
                    over(314 + dx, 324 + dy, PAL['cube'][4], 0.55)


def dibuja_prision_confinadora_grande(cx, cy):
    """Prisión Confinadora (Gokumonkyo) 36x36 detallada sobre el cráter."""
    cb0, cb1, cb2, eye_w, blood = PAL['cube']
    r = 18
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            bdr = (abs(dx) >= r - 1 or abs(dy) >= r - 1 or abs(dx) == 6 or abs(dy) == 6)
            col = cb2 if bdr else (cb1 if (dx + dy) < -4 else (cb0 if (dx + dy) < 8 else '#120a18'))
            put(cx + dx, cy + dy, col)
    for ex, ey in ((0, 0), (-11, -11), (11, -11), (-11, 11), (11, 11)):
        for ody in range(-3, 4):
            for odx in range(-4, 5):
                if (odx * odx) / 16.0 + (ody * ody) / 9.0 <= 1.0:
                    put(cx + ex + odx, cy + ey + ody, eye_w)
        disc(cx + ex, cy + ey, 1, blood)
        put(cx + ex, cy + ey, '#1a0408')
        put(cx + ex, cy + ey + 3, blood)
        put(cx + ex, cy + ey + 4, blood)
    if ANIM:
        RUNAS.append([cx, cy])
    else:
        glow(cx, cy, 24, blood, 0.46)


def dibuja_itadori_hero(cx, by):
    """Yuji Itadori 46x34 descargando Destello Negro (Kokusen)."""
    u0, hd, sk, pk, dk = PAL['itadori']
    spr = [
        '............PPPPPPPPPP............',
        '..........PPPPPPPPPPPPPP..........',
        '.........PPPPPPPPPPPPPPPP.........',
        '........PPPPPPPPPPPPPPPPPP........',
        '........PPPKKKKKKKKKKKKPPP........',
        '.......PPPKCCCCCCCCCCCCKPPP.......',
        '.......PPKCCKKCCCCCCKKCCKPP.......',
        '.......PPKCCEECCCCCCEECCKPP.......',
        '........KKCCCCCCCCCCCCCCKK........',
        '........KKCCCCCCCCCCCCCCKK........',
        '.........KKKCCCCCCCCCCKKK.........',
        '........KKHHHHHHHHHHHHHHKK........',
        '.......KHHHHHHHHHHHHHHHHHHK.......',
        '......KHHUUUUUUUUUUUUUUUUHHK......',
        '......KHUUUUUUUUGGUUUUUUUUHK......',
        '.....KCCKUUUUUUUUUUUUUUUUKUU......',
        '....KCRRKUUUUUUUUUUUUUUUUKUU......',
        '...KCRRRRKUUUUUUGGUUUUUUUKUU......',
        '...KCRRRK.UUUUUUUUUUUUUUUKUU......',
        '....KKKK..KUUUUUUUUUUUUUUKCK......',
        '..........KUUUUUUUUUUUUUUKCC......',
        '.........KUUUUUUGGUUUUUUUUK.......',
        '.........KUUUUUUUUUUUUUUUUK.......',
        '........KUUUUUUUUUUUUUUUUUUK......',
        '........KUUUUUUUUUUUUUUUUUUK......',
        '........KUUUUUUU11UUUUUUUUUK......',
        '........KUUUUUUU..UUUUUUUUK.......',
        '........KUUUUUU....UUUUUUUK.......',
        '.......KUUUUUU......UUUUUUUK......',
        '.......KUUUUUU......UUUUUUUK......',
        '.......KUUUUU........UUUUUUK......',
        '......KUUUUUU........UUUUUUK......',
        '......KUUUUU..........UUUUUK......',
        '......UUUUUU..........UUUUUU......',
        '......UUUUU............UUUUU......',
        '.....UUUUUU............UUUUUU.....',
        '.....UUUUU..............UUUUU.....',
        '.....KKKKK..............KKKKK.....',
        '....KHHHHHK............KHHHHHK....',
        '....KHHHHHK............KHHHHHK....',
        '...KKKKKKKK............KKKKKKKK...',
        '...KKKKKKKK............KKKKKKKK...',
    ]
    cmap = {'P': pk, 'C': sk, 'K': dk, 'H': hd, 'U': u0, '1': '#2b3864', 'G': '#facc15', 'R': '#f43f5e', 'E': '#7c2d12'}
    pinta_sprite(lz, cx, by, spr, cmap)
    # Rayos de Destello Negro alrededor del puño adelantado (cx - 15, by - 25)
    fx, fy = cx - 15, by - 25
    if not ANIM:
        glow(fx, fy, 16, '#e11d48', 0.72)
        disc(fx, fy, 4, '#050208')
        disc(fx, fy, 2, '#fda4af')
    for dx0, dy0, dx1, dy1 in ((-14, -12, -4, -3), (-16, 4, -5, 1), (12, -14, 3, -4)):
        for k in range(10):
            px = fx + dx0 + ((dx1 - dx0) * k) // 10
            py = fy + dy0 + ((dy1 - dy0) * k) // 10
            put(px, py, '#090308' if k % 3 == 0 else '#f43f5e')
    if ANIM:
        RUNAS.append([fx, fy])


def dibuja_megumi_hero(cx, by):
    """Megumi Fushiguro 44x32 + Perro Divino: Totalidad."""
    u0, u1, sk, dk, sh = PAL['megumi']
    # Charco de Diez Sombras en el suelo bajo Megumi
    for dy in range(-5, 6):
        for dx in range(-44, 52):
            if (dx * dx) / 2200.0 + (dy * dy) / 25.0 <= 1.0:
                put(cx + 12 + dx, by + dy, '#050710' if abs(dy) < 3 else '#1e293b')

    spr = [
        '..........KKKKKKKKKKK...........',
        '........KKKKKKKKKKKKKKK.........',
        '......KKKKKKKKKKKKKKKKKKK.......',
        '.....KKKKKKKKKKKKKKKKKKKKK......',
        '.......KKKKCCCCCCCCCCKKKK.......',
        '......KKKCCCCCCCCCCCCCCKKK......',
        '......KKCCKKECCCCCCEKCCKK.......',
        '.......KCCCCCCCCCCCCCCCCK.......',
        '.......KKCCCCCCCCCCCCCCKK.......',
        '........KKKKKKKKKKKKKKKK........',
        '.......KKUUUUUUUUUUUUUUKK.......',
        '......KUUUUUUUUGGGUUUUUUUK......',
        '.....KUUUUUUUUUUUUUUUUUUUUK.....',
        '....KCCKUUUUUUUUUUUUUUUUKCCK....',
        '...KCCCKUUUUUUUGGGUUUUUUKCCCK...',
        '....KKK.KUUUUUUUUUUUUUUK.KKK....',
        '........KUUUUUUUUUUUUUUK........',
        '........KUUUUUUUUUUUUUUK........',
        '.......KUUUUUUUUUUUUUUUUK.......',
        '.......KUUUUUUU11UUUUUUUK.......',
        '.......KUUUUUUU..UUUUUUUK.......',
        '.......KUUUUUU....UUUUUUK.......',
        '......KUUUUUU......UUUUUUK......',
        '......KUUUUUU......UUUUUUK......',
        '......KUUUUU........UUUUUK......',
        '.....KUUUUUU........UUUUUUK.....',
        '.....KUUUUU..........UUUUUK.....',
        '.....UUUUUU..........UUUUUU.....',
        '.....UUUUU............UUUUU.....',
        '....UUUUUU............UUUUUU....',
        '....UUUUU..............UUUUU....',
        '....KKKKK..............KKKKK....',
        '...KKKKKKK............KKKKKKK...',
        '...KKKKKKK............KKKKKKK...',
    ]
    cmap = {'K': dk, 'C': sk, 'U': u0, '1': u1, 'G': '#fbbf24', 'E': '#0f4c5c'}
    pinta_sprite(lz, cx, by, spr, cmap)

    # Gran Perro Divino: Totalidad (Kon) junto a Megumi (cx + 42, by + 2)
    lobo = [
        '....KK.................KK.....',
        '...KDDK...............KDDK....',
        '..KDDDDK.............KDDDDK...',
        '..KDDDDDK...KKKKK...KDDDDDK...',
        '...KDDDDDKKKDDDDDKKKDDDDDK....',
        '...KDDDDDDDDDDDDDDDDDDDDDK....',
        '....KDDDDDDDDWWWDDDDDDDDK.....',
        '....KDDDDDDWWWWWWWDDDDDDK.....',
        '....KDDDRRKDDWWWDDKRRDDDK.....',
        '...KDDDDKKDDDDDDDDDKKDDDDK....',
        '...KDDDDDDDDKWWWWKDDDDDDDK....',
        '..KDDDDDDDDDKDDDDKDDDDDDDDK...',
        '..KDDDDDDDDDDKKKKDDDDDDDDDK...',
        '.KDDDDDDDDDDDDDDDDDDDDDDDDDK..',
        '.KDDDDDDDDDDWWWWWWDDDDDDDDDK..',
        '.KDDDDDDDDDWWWWWWWWDDDDDDDDK..',
        '..KDDDDDDDWWWWWWWWWWDDDDDDK...',
        '..KDDDDDDDWWWWWWWWWWDDDDDDK...',
        '...KDDDDDDWWWWWWWWWWDDDDDK....',
        '...KDDDDDDDWWWWWWWWDDDDDDK....',
        '....KDDDDDD.WWWWWW.DDDDDK.....',
        '....KDDDDDK..KKKK..KDDDDK.....',
        '....KDDDDK..........KDDDK.....',
        '...KDDDDK............KDDDK....',
        '...KWWWWK............KWWWWK...',
        '..KKWWWWKK..........KKWWWWKK..',
    ]
    pinta_sprite(lz, cx + 44, by + 2, lobo, {'K': '#05070e', 'D': '#182032', 'W': '#e2e8f0', 'R': sh})
    if ANIM:
        RUNAS.append([cx + 44, by - 16])
    else:
        glow(cx + 44, by - 16, 11, sh, 0.50)


dibuja_shibuya_109(106)
dibuja_skyline_shibuya()
dibuja_cruce_shibuya()
dibuja_prision_confinadora_grande(314, 282)
dibuja_itadori_hero(202, 348)
dibuja_megumi_hero(402, 348)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR], con_astro=False,
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
