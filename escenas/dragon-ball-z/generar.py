#!/usr/bin/env python3
"""PixelZen Worlds - Dragon Ball Z (Principal): Namek en Destrucción, Goku Ultra Instinto vs Freezer."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, exporta_salida, exporta_sprites_si_aplica, fbm, mix, pinta_sprite,
    render_cielo, render_estrellas, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1401)

PALETAS = {
    'noche': dict(
        sky=['#030a0c', '#07161a', '#0c2428', '#123638', '#1c4a46', '#2c5e4e', '#46744c', '#6e8444', '#a47838', '#dc602c'],
        crag=('#18141c', '#2a222e', '#0d0a10', '#423446'),
        lava=('#dc2626', '#f97316', '#facc15', '#fff7ed'),
        sea=('#0c3838', '#145a56', '#2dd4bf'),
        goku=('#f8fafc', '#cbd5e1', '#f97316', '#1e3a8a', '#38bdf8'),
        frieza=('#facc15', '#eab308', '#a855f7', '#7e22ce', '#1e1b2e'),
        vig=0.72,
        nube=['#162a2c', '#243e40', '#385452', '#566858', '#846244', '#101e20'],
    ),
    'dorado': dict(
        sky=['#120810', '#241016', '#3c181a', '#5c241c', '#82341c', '#aa481c', '#d06220', '#ee8228', '#ffab3c', '#ffd874'],
        crag=('#261a22', '#3c2832', '#140c12', '#583c48'),
        lava=('#ef4444', '#fb923c', '#fde047', '#ffffff'),
        sea=('#144a48', '#22726a', '#5eead4'),
        goku=('#ffffff', '#e2e8f0', '#fb923c', '#1d4ed8', '#38bdf8'),
        frieza=('#fde047', '#f59e0b', '#c084fc', '#9333ea', '#201a30'),
        vig=0.80,
        nube=['#422026', '#602c28', '#863c28', '#ae5228', '#d67032', '#30141c'],
    ),
    'dia': dict(
        sky=['#0a4854', '#126470', '#1e828c', '#32a0a6', '#50bcba', '#78d2cc', '#a4e4dc', '#caf2e8', '#e6f8dc', '#fbe2a8'],
        crag=('#3c3648', '#544c64', '#24202c', '#746a88'),
        lava=('#ef4444', '#f97316', '#fde047', '#ffffff'),
        sea=('#0d7a74', '#14b8a6', '#99f6e4'),
        goku=('#ffffff', '#cbd5e1', '#f97316', '#1d4ed8', '#22d3ee'),
        frieza=('#fef08a', '#f59e0b', '#c084fc', '#7e22ce', '#1e1b2e'),
        vig=0.88,
        nube=['#eefcf8', '#dcf6ee', '#caeede', '#ffffff', '#e4f6ec', '#a8d4ca'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#38bdf8', '#c084fc'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 36, halo='#5eead4', base='#f0fdfa', sombra='#99f6e4', crater='#5eead4', crater_hi='#ccfbf1'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#fef08a', centro='#ffffff', borde='#f97316', rayo='#fde047'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffffff', '#bae6fd', '#fef08a'])

MX, MY, MR = 278, 60, 34
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#5eead4', base='#f0fdfa', sombra='#99f6e4', crater='#5eead4', crater_hi='#ccfbf1')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 290, 114, 22, halo='#ffb85c', centro='#fff8e4', borde='#f97316', rayo='#fed7aa')
    else:
        dibuja_sol_estandar(lz, 290, 68, 22, halo='#fef08a', centro='#ffffff', borde='#f59e0b', rayo='#fde047')
# Segundo sol lejano de Namek (rasgo único del planeta, cx=126, cy=86)
disc(126, 86, 12, '#fef08a')
glow(126, 86, 20, '#fb923c', 0.40)

NUBES_DEF = [
    (72, 42, 82, PAL['nube'][1], 2),
    (412, 48, 88, PAL['nube'][2], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)


def dibuja_namek_en_destruccion():
    """Pilares namekianos rotos, árboles Ajisa quemados y suelo volcánico con grietas de magma."""
    cr0, cr1, cr2, cr3 = PAL['crag']
    lv0, lv1, lv2, lv3 = PAL['lava']
    s0, s1, s2 = PAL['sea']
    r_m = Ruido(1401)

    # Mesetas rocosas escarpadas de Namek en el horizonte (perfil irregular erosionado)
    for px, pw, top_y in ((26, 36, 144), (82, 26, 174), (160, 28, 184), (356, 30, 172), (434, 28, 190)):
        for y in range(top_y, 244):
            u = (y - top_y) / float(max(1, 244 - top_y))
            n_edge = int(4 * (fbm(r_m, px * 0.09 + y * 0.08) - 0.5))
            hw = max(6, int(pw * (0.42 + 0.62 * u)) + n_edge)
            for dx in range(-hw, hw + 1):
                strata = (y % 9 == 0) and dith(px + dx, y, 0.45)
                col_p = cr2 if (dx > hw - 3 or strata) else (cr3 if dx < -hw + 3 else (cr1 if fbm(r_m, (px + dx) * 0.06 + y * 0.08) > 0.5 else cr0))
                put(px + dx, y, col_p)
    # Árbol Ajisa inclinado en el lado izquierdo
    for k in range(28):
        put(118 + k // 4, 242 - k, '#5e4c36')
    disc(124, 210, 11, s0)
    disc(122, 208, 8, s1)
    disc(120, 206, 4, s2)

    # Mar turquesa hirviente lejano con olas naturales (y=238..254)
    for y in range(238, 255):
        for x in range(W):
            nw = fbm(r_m, x * 0.04 + y * 0.25)
            col = s2 if (nw > 0.64 and dith(x, y, 0.55)) else (s1 if nw > 0.44 else s0)
            put(x, y, col)

    for y in range(252, H):
        for x in range(W):
            n = fbm(r_m, x * 0.03 + y * 0.04)
            col = cr3 if n > 0.65 else (cr1 if n > 0.42 else (cr0 if n > 0.22 else cr2))
            if y < 258:
                col = mix(col, s2, 0.35)
            put(x, y, col)

    # Grietas de lava incandescente y cráter de choque en primer plano
    for lx0, ly0, dx_s, dy_s, steps in ((48, 368, 96, -34, 48), (470, 376, -86, -32, 44), (240, 392, 130, -18, 52)):
        for k in range(steps):
            u = k / float(steps)
            px = int(lx0 + dx_s * u + math.sin(u * 12.0) * 6)
            py = int(ly0 + dy_s * u + math.cos(u * 9.0) * 3)
            for t in range(-2, 3):
                put(px, py + t, lv3 if t == 0 else (lv1 if abs(t) == 1 else lv0))

    # Ondas sísmicas concéntricas en el suelo bajo Goku y Freezer
    for dy in range(-18, 20):
        for dx in range(-94, 95):
            ell = math.hypot(dx / 94.0, dy / 18.0)
            if 0.72 <= ell <= 0.96 and dith(304 + dx, 344 + dy, 0.80):
                over(304 + dx, 344 + dy, '#38bdf8' if dx < 0 else '#facc15', 0.48)


def dibuja_goku_ui_hero(cx, by):
    """Son Goku Ultra Instinto Dominado (48x38) con aura cósmica y Kamehameha Divino."""
    h0, h1, pant, boot, aura = PAL['goku']
    if not ANIM:
        glow(cx, by - 26, 30, aura, 0.42)
        glow(cx, by - 26, 18, '#c084fc', 0.30)

    spr = [
        '..........HHH........HHH..............',
        '........HHHHH......HHHHHH.............',
        '.......HHHHHHH....HHHHHHHH...HHH......',
        '......HHHHHHHHHHHHHHHHHHHHH.HHHH......',
        '.....HHHHHHH11111111HHHHHHHHHHH.......',
        '......HHHHH1111111111HHHHHHHH.........',
        '.......HHHCCCCCCCCCCCC11HHH...........',
        '.......HHCCKKCCCCCCKKCCHH.............',
        '.......HHCCEECCCCCCEECCHH.............',
        '........KCCCCCCCCCCCCCCK..............',
        '........KCCCCKKCCKKCCCCK..............',
        '.........KKCCCCCCCCCCKK...............',
        '........KKCCCCCCCCCCCCKK..............',
        '.......KCCCCCCssCCssCCCCK.............',
        '......KCCCCCCCssCCssCCCCCK............',
        '......KCCssCCCCCCCCCCssCCK............',
        '.....KCCCKssCCCCCCCCssKCCC............',
        '.....KCCK.KssCCCCCCssK.KKCA...........',
        '....KCCCK..KCCCCCCCCK...AAA...........',
        '....KCCK...KBBBBBBBBK..AAAA...........',
        '.....KK....KBBBB11BBK.KCCAA...........',
        '..........KPPPPPPPPPPKCCCA............',
        '..........KPPPPPPPPPPKKKK.............',
        '.........KPPPPPPPPPPPPPK..............',
        '.........KPPPPPPPPPPPPPK..............',
        '........KPPPPPP11PPPPPPPK.............',
        '........KPPPPPP..PPPPPPPK.............',
        '........KPPPPP....PPPPPPK.............',
        '.......KPPPPPP....PPPPPPPK............',
        '.......KPPPPP......PPPPPPK............',
        '.......KPPPPP......PPPPPPK............',
        '......KPPPPP........PPPPPPK...........',
        '......KPPPPP........PPPPPPK...........',
        '.....KPPPPP..........PPPPPPK..........',
        '.....BBBBBB..........BBBBBBB..........',
        '.....BBBBBB..........BBBBBBB..........',
        '....BBBBBBBB........BBBBBBBB..........',
        '....BBBBBBBB........BBBBBBBB..........',
        '....BBBB11BB........BBBB11BB..........',
        '....KKKKKKKK........KKKKKKKK..........',
    ]
    cmap = {'H': h0, '1': h1, 'C': '#f4cfb8', 's': '#d29c7c', 'K': '#101422', 'E': '#e2e8f0', 'B': boot, 'P': pant, 'A': aura}
    pinta_sprite(lz, cx, by, spr, cmap)
    if ANIM:
        RUNAS.append([cx, by - 26])
        FAROLES.append([cx + 18, by - 22, 10])
    else:
        glow(cx + 18, by - 22, 14, aura, 0.75)
        disc(cx + 18, by - 22, 5, '#ffffff')


def dibuja_freezer_hero(cx, by):
    """Golden Freezer (Forma Final) 44x32 con cola larga y Supernova incandescente."""
    g0, g1, p0, p1, ink = PAL['frieza']
    lv0, lv1, lv2, lv3 = PAL['lava']
    # Cola dorada-púrpura curvándose a la derecha detrás de Freezer
    for s in range(38):
        u = s / 37.0
        tx = int(cx + 8 + s * 1.15)
        ty = int(by - 14 + math.sin(u * 4.5) * 8)
        for dy in range(-2, 3):
            put(tx, ty + dy, g1 if dy >= 0 else g0)

    spr = [
        '...........KKKKKK..KKKKKK.............',
        '..........KGGGGGGKKGGGGGGK............',
        '..........KGGPPPPPPPPPPGGK............',
        '..........KGPPPPPPPPPPPPGK............',
        '...........KGGGGPPPPGGGGK.............',
        '...........KGGKKGGGGKKGGK.............',
        '...........KGGRRGGGGRRGGK.............',
        '............KGGGGGGGGGGK..............',
        '............KGGKKKKKKGGK..............',
        '.............KKGGGGGGKK...............',
        '........PPPP.KGGPPPPGGK.PPPP..........',
        '.......PPPPPKGGGGGGGGGGKPPPPP.........',
        '......KGGGKKGGGGPPPPGGGGKKGGGK........',
        '.....KGGGGKGGGGPPPPPPGGGGKGGGGK.......',
        '....KGGGGG.KGGGGGGGGGGGGK.GGGGGK......',
        '....KGGGKK..KGGGG11GGGGK..GGGGGK......',
        '...KKKK.....KGGGGGGGGGGK...GGGGK......',
        '............KPPPPPPPPPPK....KKKK......',
        '............KPPPP11PPPPK..............',
        '...........KGGGGGGGGGGGGK.............',
        '...........KGGGGGGGGGGGGK.............',
        '...........KGGGG11GGGGGGK.............',
        '...........KGGGG..GGGGGGK.............',
        '..........KGGGG....GGGGGGK............',
        '..........KGGGG....GGGGGGK............',
        '.........KGGGG......GGGGGGK...........',
        '.........KPPPP......PPPPPPK...........',
        '.........KPPPP......PPPPPPK...........',
        '........KGGGGG......GGGGGGGK..........',
        '........KGGGGG......GGGGGGGK..........',
        '.......KGGGKKK......KKKGGGGGK.........',
        '.......KKK..KK......KK...KKK..........',
    ]
    cmap = {'K': ink, 'G': g0, '1': g1, 'P': p0, 'R': '#dc2626'}
    pinta_sprite(lz, cx, by, spr, cmap)

    # Colosal Supernova incandescente flotando sobre su dedo índice (cx - 18, by - 46)
    sx, sy = cx - 18, by - 48
    if not ANIM:
        glow(sx, sy, 22, lv0, 0.72)
    disc(sx, sy, 10, lv1)
    disc(sx - 2, sy - 2, 7, lv2)
    disc(sx - 3, sy - 3, 3, lv3)
    if ANIM:
        FAROLES.append([sx, sy, 12])
        RUNAS.append([cx, by - 20])


dibuja_namek_en_destruccion()
dibuja_goku_ui_hero(202, 348)
dibuja_freezer_hero(404, 344)

# Choque de haces Kamehameha (cian-blanco) vs Bola de la Muerte / Supernova (oro-rojo) en (306, 304)
for k in range(74):
    px = 224 + k
    py = 318 - int(k * 0.28)
    rad = 4 if k < 66 else 8
    for dy in range(-rad, rad + 1):
        put(px, py + dy, '#ffffff' if abs(dy) <= 1 else ('#38bdf8' if px < 304 else '#f97316'))
if not ANIM:
    glow(304, 298, 28, '#ffffff', 0.75)
    disc(304, 298, 8, '#fef08a')
    disc(304, 298, 5, '#ffffff')
else:
    RUNAS.append([304, 298])

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
