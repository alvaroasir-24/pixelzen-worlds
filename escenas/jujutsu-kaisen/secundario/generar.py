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
    render_cielo, render_estrellas, render_lago, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1102)

PALETAS = {
    'noche': dict(
        sky=['#040714', '#080e24', '#101836', '#18224a', '#222e60', '#2c3c76', '#384c8e', '#485ea4', '#5c72ba', '#7488d0'],
        bldg=('#111626', '#1c243a', '#090c16', '#283454'),
        cyl=('#242c48', '#38446c', '#161b2e', '#526296'),
        neon=('#38bdf8', '#f43f5e', '#a855f7', '#facc15'),
        cube=('#1e1628', '#382a48', '#68507c', '#e2e8f0', '#e11d48'),
        itadori=('#1a223c', '#e11d48', '#f6d2c0', '#fb7185', '#10121e'),
        megumi=('#182034', '#263250', '#f0cec0', '#161a26', '#38bdf8'),
        agua='#091022',
        olas=('#fb7185', '#60a5fa', '#1e3a8a'),
        reflejo=('#f472b6', '#93c5fd'),
        vig=0.74,
        nube=['#161f3a', '#212e52', '#2e3e6c', '#3c4e84', '#4c609c', '#10162c'],
    ),
    'dorado': dict(
        sky=['#141028', '#26183c', '#3e224e', '#5c2e5a', '#7c3e5e', '#a25458', '#c87250', '#e89650', '#ffba62', '#ffe094'],
        bldg=('#1e1a2c', '#302844', '#120f1c', '#44385c'),
        cyl=('#342a48', '#50406c', '#201a30', '#6e5894'),
        neon=('#38bdf8', '#fb7185', '#c084fc', '#fde047'),
        cube=('#261a30', '#443054', '#76588c', '#f8fafc', '#f43f5e'),
        itadori=('#1e2644', '#f43f5e', '#f8d6c4', '#fb7185', '#121420'),
        megumi=('#1e263c', '#2e3a58', '#f4d2c4', '#181c28', '#38bdf8'),
        agua='#1a1a36',
        olas=('#fda4af', '#818cf8', '#3730a3'),
        reflejo=('#fde68a', '#93c5fd'),
        vig=0.82,
        nube=['#402446', '#5a3254', '#7a425c', '#9e5662', '#c4726a', '#301a36'],
    ),
    'dia': dict(
        sky=['#1d4e92', '#2d64aa', '#407cc0', '#5a94d4', '#78aee4', '#96c6ee', '#b4dcf6', '#d0ecf8', '#e6f4fc', '#f4f8ee'],
        bldg=('#2d3852', '#425070', '#1d2438', '#5c6e94'),
        cyl=('#4c5c82', '#687ca8', '#323e5c', '#8ca2d0'),
        neon=('#0284c7', '#e11d48', '#9333ea', '#eab308'),
        cube=('#2e243a', '#4c3e5e', '#7c6892', '#ffffff', '#e11d48'),
        itadori=('#202b48', '#e11d48', '#f8d6c4', '#fb7185', '#141824'),
        megumi=('#202a42', '#324264', '#f4d2c4', '#181e2c', '#0ea5e9'),
        agua='#244c80',
        olas=('#bae6fd', '#fda4af', '#3b82f6'),
        reflejo=('#fff4c4', '#93c5fd'),
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

# Domo translúcido del Velo (Tobari) sobre Shibuya
for y in range(18, 195):
    t_v = max(0.0, 1.0 - abs(y - 68) / 135.0)
    arc_x = int(math.sin((y / 195.0) * math.pi) * 284)
    for x in range(max(0, 320 - arc_x), min(W, 320 + arc_x)):
        d_edge = abs(abs(x - 320) - arc_x)
        if d_edge < 4:
            over(x, y, '#818cf8' if (x + y) % 3 else '#c084fc', 0.44 * t_v)

MX, MY, MR = 320, 68, 36
NUBES_DEF = [
    (96, 52, 82, PAL['nube'][1], 2),
    (228, 68, 74, PAL['nube'][2], 1),
    (438, 56, 86, PAL['nube'][3], 2),
    (556, 72, 70, PAL['nube'][4], 1),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)


def dibuja_shibuya_109(cx):
    """Icónica torre cilíndrica Shibuya 109 al fondo izquierdo."""
    c0, c1, c2, c3 = PAL['cyl']
    for y in range(106, HOR):
        for dx in range(-32, 33):
            u = dx / 32.0
            sh = 0.5 + 0.5 * (-u * 0.7)
            col = c3 if sh > 0.75 else (c1 if sh > 0.45 else (c0 if sh > 0.2 else c2))
            if y < 132 and abs(dx) > 22:
                continue
            put(cx + dx, y, col)
            if y % 12 == 0 and abs(dx) < 30:
                put(cx + dx, y, c2)
            elif (y % 12 in (4, 5)) and (dx % 7 in (1, 2, 3)) and y > 138:
                wcol = PAL['neon'][0] if (cx + y) % 3 else PAL['neon'][1]
                put(cx + dx, y, wcol)
    # Rótulo circular luminoso 109 con dígitos limpios
    disc(cx, 164, 15, '#120820')
    for ang_i in range(48):
        a = (ang_i / 48.0) * 2 * math.pi
        put(cx + int(round(15 * math.cos(a))), 164 + int(round(15 * math.sin(a))), PAL['neon'][1])
    # '1'
    for dy in range(-5, 6):
        put(cx - 8, 164 + dy, '#fff0f5')
    # '0'
    for dy in range(-5, 6):
        for dx in range(-3, 4):
            if abs(dx) == 3 or abs(dy) == 5:
                put(cx + dx, 164 + dy, '#fff0f5')
    # '9'
    for dy in range(-5, 6):
        for dx in range(6, 11):
            if dy in (-5, 0, 5) or dx == 10 or (dy < 0 and dx == 6):
                put(cx + dx, 164 + dy, '#fff0f5')
    if ANIM:
        FAROLES.append([cx, 164, 9])
    else:
        glow(cx, 164, 12, PAL['neon'][1], 0.45)


def dibuja_calle_shibuya():
    """Edificios de Shibuya con carteles neón + paso de cebra sobre HOR=280."""
    b0, b1, b2, b3 = PAL['bldg']
    bloques = [
        (0, 74, 146, 0), (154, 58, 138, 1), (216, 46, 168, 2),
        (378, 50, 160, 3), (432, 66, 130, 0), (502, 64, 144, 1), (570, 70, 120, 2),
    ]
    for x0, bw, top_y, n_idx in bloques:
        for y in range(top_y, HOR):
            for x in range(x0, min(W, x0 + bw)):
                edge = (x == x0 or x == x0 + bw - 1 or y == top_y)
                is_floor = ((y - top_y) % 10 == 0)
                put(x, y, b2 if edge else (b1 if is_floor else b0))
                if (x - x0) > 4 and (x - x0) < bw - 4 and (x - x0) % 7 in (2, 3) and (y - top_y) > 8 and (y - top_y) % 10 == 4:
                    if ((x * 5 + y * 9) % 4) == 0:
                        nc = PAL['neon'][(n_idx + x) % 4]
                        put(x, y, nc)
                        if len(VENTANAS) < 42 and x % 2 == 0:
                            VENTANAS.append([x, y, 2])
        vx = x0 + bw - 8
        if 30 < vx < 460:
            for vy in range(top_y + 22, min(HOR - 16, top_y + 82)):
                for dx in range(-3, 4):
                    put(vx + dx, vy, '#100c1e' if abs(dx) == 3 else PAL['neon'][n_idx % 4])
            if ANIM:
                FAROLES.append([vx, top_y + 50, 6])

    # Acera devastada y cruce de Shibuya y=270..280
    for x in range(W):
        for y in range(271, HOR + 1):
            col = '#1a2032' if (y % 3) else '#26304a'
            if (x // 18) % 2 == 0 and 273 <= y <= 278:
                col = '#b8c4dc'
            if abs(x - 320) < 36 and y > 272:
                col = '#0b0e1a'
            put(x, y, col)


def dibuja_prision_confinadora(cx, cy):
    """Cubo de la Prisión Confinadora (Gokumonkyo) levitando sobre el cruce."""
    cb0, cb1, cb2, eye_w, blood = PAL['cube']
    r = 15
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            border = (abs(dx) >= r - 1 or abs(dy) >= r - 1 or abs(dx) == 5 or abs(dy) == 5)
            put(cx + dx, cy + dy, cb2 if border else (cb1 if (dx + dy) < 0 else cb0))
    for ex, ey in ((0, 0), (-9, -9), (9, -9), (-9, 9), (9, 9)):
        for ody in range(-2, 3):
            for odx in range(-3, 4):
                if odx * odx + ody * ody * 2 <= 8:
                    put(cx + ex + odx, cy + ey + ody, eye_w)
        put(cx + ex, cy + ey, blood)
        put(cx + ex, cy + ey + 3, blood)
    if ANIM:
        RUNAS.append([cx, cy])
    else:
        glow(cx, cy, 18, blood, 0.40)


def dibuja_itadori(cx, by):
    """Yuji Itadori en el cruce (by=278)."""
    u0, hd, sk, pk, dk = PAL['itadori']
    spr = [
        '......PPPPPPPP......',
        '.....PPPPPPPPPP.....',
        '....PPPPPPPPPPPP....',
        '....PPCCCCCCCCPP....',
        '....PPCKKCCKKCPP....',
        '....PPCCCCCCCCPP....',
        '.....KHHHHHHHHK.....',
        '....KHHHHHHHHHHK....',
        '...KHHUUUUUUUUHHK...',
        '..KCCKUUUUUUUUUUK...',
        '..KRRKUUUUGGUUUUK...',
        '...KK.UUUUUUUUUUK...',
        '......UUUUUUUUUUK...',
        '......UUUUUUUUUUK...',
        '......UUUUUUUUUUK...',
        '......UUUU11UUUU....',
        '......UUUU..UUUU....',
        '......UUUU..UUUU....',
        '.....UUUU....UUUU...',
        '.....UUUU....UUUU...',
        '.....HHHH....HHHH...',
        '.....HHHH....HHHH...',
    ]
    cmap = {'P': pk, 'C': sk, 'K': dk, 'H': hd, 'U': u0, '1': '#2b365e', 'G': '#facc15', 'R': '#ef4444'}
    pinta_sprite(lz, cx, by, spr, cmap)
    if ANIM:
        RUNAS.append([cx - 10, by - 12])
    else:
        glow(cx - 10, by - 12, 8, '#e11d48', 0.55)


def dibuja_megumi(cx, by):
    """Megumi Fushiguro y Perro Divino de sombra (by=278)."""
    u0, u1, sk, dk, sh = PAL['megumi']
    spr = [
        '....KKKKKKKKKKK.....',
        '...KKKKKKKKKKKKK....',
        '..KKKKKKKKKKKKKKK...',
        '...KKKCCCCCCCCKK....',
        '...KKCKKCCCCKKCK....',
        '....KKCCCCCCCCK.....',
        '.....KKKKKKKKK......',
        '....KKUUUUUUUUKK....',
        '...KUUUUUUUUUUUUK...',
        '..KUUUUGGGUUUUUUK...',
        '..KCCKUUUUUUUUUCK...',
        '...KK.UUUUUUUUUU....',
        '......UUUUUUUUUU....',
        '......UUUUUUUUUU....',
        '......UUUU11UUUU....',
        '......UUUU..UUUU....',
        '......UUUU..UUUU....',
        '.....UUUU....UUUU...',
        '.....UUUU....UUUU...',
        '.....KKKK....KKKK...',
        '.....KKKK....KKKK...',
    ]
    cmap = {'K': dk, 'C': sk, 'U': u0, '1': u1, 'G': '#fbbf24'}
    pinta_sprite(lz, cx, by, spr, cmap)
    for dy in range(-18, 1):
        for dx in range(-10, 11):
            wx, wy = cx + 22 + dx, by + dy
            in_w = (abs(dx) <= 7 - abs(dy + 6) // 3) or (dy < -12 and abs(dx) in (4, 5, 6))
            if in_w:
                put(wx, wy, '#0a0d16' if (dx + dy) % 3 else '#1e293b')
    put(cx + 19, by - 11, sh)
    put(cx + 25, by - 11, sh)
    if ANIM:
        RUNAS.append([cx + 22, by - 14])
    else:
        glow(cx + 22, by - 14, 7, sh, 0.45)


dibuja_shibuya_109(116)
dibuja_calle_shibuya()
dibuja_prision_confinadora(320, 246)
dibuja_itadori(216, 278)
dibuja_megumi(422, 278)

render_lago(lz, PAL['agua'], PAL['olas'], DESTELLOS, ANIM, mx=MX, hor=HOR, reflejo_cols=PAL['reflejo'], reflejo_astro=False)
aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR], con_astro=False,
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
