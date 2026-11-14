#!/usr/bin/env python3
"""PixelZen Worlds - One Piece (Principal): Onigashima, Luffy Gear 5 (Nika) vs Kaido Dragón."""
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
random.seed(1301)

PALETAS = {
    'noche': dict(
        sky=['#040612', '#080e24', '#101a38', '#182850', '#243668', '#344880', '#485c98', '#6074ae', '#7c90c6', '#9cb0dc'],
        skull=('#1c2032', '#2e3450', '#0e101c', '#485278'),
        roof=('#141624', '#242840', '#0a0c14', '#384064'),
        kaido=('#0e5a88', '#2296cc', '#072c48', '#7dd3fc', '#9333ea'),
        nika=('#ffffff', '#e2e8f0', '#94a3b8', '#a855f7', '#0f172a'),
        fire=('#dc2626', '#f97316', '#facc15', '#fff7ed'),
        vig=0.72,
        nube=['#1c2440', '#2a365c', '#3b4b7a', '#4e6298', '#647bb6', '#141a30'],
    ),
    'dorado': dict(
        sky=['#12081c', '#24102c', '#3e1a3a', '#5e2842', '#823a44', '#aa5240', '#ce703c', '#ea9242', '#ffb854', '#ffe088'],
        skull=('#2a2034', '#40324e', '#16101e', '#5e4c72'),
        roof=('#20182a', '#342842', '#100c18', '#4e3c62'),
        kaido=('#126898', '#2eb0e0', '#0a3654', '#a5f3fc', '#a855f7'),
        nika=('#ffffff', '#f1f5f9', '#cbd5e1', '#c084fc', '#141222'),
        fire=('#ef4444', '#fb923c', '#fde047', '#ffffff'),
        vig=0.80,
        nube=['#42203e', '#5e2e4a', '#804054', '#a4565a', '#ca7260', '#30162e'],
    ),
    'dia': dict(
        sky=['#164488', '#245ba2', '#3474bc', '#4a90d4', '#66aae4', '#86c4ee', '#a8daf4', '#caeefa', '#e6f6fc', '#f4f8ee'],
        skull=('#464e64', '#626c88', '#2a3040', '#8694b6'),
        roof=('#363c50', '#4c5670', '#202432', '#6c789a'),
        kaido=('#1878aa', '#38bdf8', '#0c4466', '#e0f2fe', '#7e22ce'),
        nika=('#ffffff', '#f8fafc', '#cbd5e1', '#9333ea', '#1e293b'),
        fire=('#ef4444', '#f97316', '#fde047', '#ffffff'),
        vig=0.88,
        nube=['#ffffff', '#eef6fc', '#deeffa', '#f8fcff', '#e4f0fb', '#c6ddf0'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#ffffff', '#ef4444'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 40, halo='#e2e8f0', base='#ffffff', sombra='#cbd5e1', crater='#94a3b8', crater_hi='#b8c4d8'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 24, halo='#fde68a', centro='#ffffff', borde='#f59e0b', rayo='#fef08a'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffffff', '#bae6fd', '#fde68a'])

MX, MY, MR = 296, 60, 42
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#e2e8f0', base='#ffffff', sombra='#cbd5e1', crater='#94a3b8', crater_hi='#b8c4d8')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 304, 120, 24, halo='#ffb860', centro='#fff8e8', borde='#f97316', rayo='#fed7aa')
    else:
        dibuja_sol_estandar(lz, 304, 68, 24, halo='#fef08a', centro='#ffffff', borde='#f59e0b', rayo='#fde047')

NUBES_DEF = [
    (82, 42, 90, PAL['nube'][1], 2),
    (426, 48, 86, PAL['nube'][2], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)


def dibuja_onigashima_fondo():
    """Colosal Cúpula Calavera de Onigashima, cuernos gigantes y espada colosal al horizonte."""
    sk0, sk1, sk2, sk3 = PAL['skull']
    # Espada gigante clavada detrás de la calavera izquierda (x=54..72, y=118..252)
    for y in range(120, 254):
        for dx in range(-5, 6):
            put(62 + dx, y, sk3 if dx < 0 else (sk1 if dx < 3 else sk2))
    for dx in range(-16, 17):
        put(62 + dx, 148, sk2)
        put(62 + dx, 149, sk3)
    # Cuernos gigantes curvándose desde el cráneo hacia el cielo (izq x=40..150, der x=390..492)
    for side, ox in ((-1, 154), (1, 378)):
        for k in range(86):
            u = k / 85.0
            hx = int(ox + side * (k * 0.90 - (k * k) * 0.004))
            hy = int(218 - k * 1.15 - 14 * math.sin(u * math.pi))
            rad = max(2, int(11 * (1.0 - 0.72 * u)))
            for dy in range(-rad, rad + 1):
                for dx in range(-rad, rad + 1):
                    if dx * dx + dy * dy <= rad * rad and hy + dy < 258:
                        if hx + dx > 475 and hy + dy < 205:
                            continue
                        put(hx + dx, hy + dy, sk3 if dy < -rad // 3 else (sk0 if dx * side < 0 else sk2))
    # Bóveda de Calavera de Onigashima centrada al fondo (cx=266, y=148..256)
    scx, scy = 266, 206
    for y in range(148, 256):
        dy = y - scy
        hw = 92 if dy < 14 else max(48, 92 - (dy - 14) // 2)
        for dx in range(-hw, hw + 1):
            nx, ny = dx / 92.0, dy / 58.0
            if nx * nx + ny * ny <= 1.0 or dy > 0:
                cr = ((scx + dx + y) % 13 == 0)
                col = sk2 if (nx > 0.65 or cr) else (sk3 if ny < -0.55 and nx < 0.2 else (sk1 if nx < 0 else sk0))
                # Cuencas oculares cavernosas (arcos oscuros con brillo interior cálido)
                if math.hypot(abs(dx) - 34, dy - 4) < 18:
                    col = '#1a0c18' if abs(dx - (34 if dx > 0 else -34)) < 14 else '#2e1a2a'
                    if math.hypot(abs(dx) - 34, dy - 6) < 4:
                        col = '#f97316'
                elif abs(dx) <= 7 and 18 <= dy <= 34:
                    col = '#140a14'
                elif 38 <= dy <= 50 and abs(dx) <= 46:
                    col = sk3 if (dx % 12 > 2) else '#1a0e18'
                put(scx + dx, y, col)
    # Silueta del gran Torii de acceso al patio sobre la cresta (cx=128)
    for px_t in (110, 146):
        for y in range(214, 254):
            for dx in range(-3, 4):
                put(px_t + dx, y, '#7f1d1d' if dx < 0 else '#450a0a')
    for dx in range(-28, 29):
        put(128 + dx, 214, '#991b1b')
        put(128 + dx, 215, '#7f1d1d')
        put(128 + dx, 224, '#7f1d1d')


def dibuja_cupula_onigashima():
    """Techo empedrado de la cúpula de Onigashima en primer plano (y=252..400)."""
    rf0, rf1, rf2, rf3 = PAL['roof']
    r_g = Ruido(1305)
    for y in range(252, H):
        ridge = 252 + int(6 * math.sin(y * 0.1))
        for x in range(W):
            n = fbm(r_g, x * 0.03 + y * 0.04)
            seam = (y % 12 == 0) or ((x + (y // 12) * 16) % 32 == 0)
            col = rf2 if seam else (rf3 if n > 0.62 else (rf1 if n > 0.38 else rf0))
            if y < ridge + 3:
                col = rf3
            put(x, y, col)
    # Onda de impacto de choque Haki del Conquistador en el centro del tejado (cx=306, cy=344)
    for dy in range(-18, 20):
        for dx in range(-96, 97):
            ell = math.hypot(dx / 96.0, dy / 18.0)
            if 0.74 <= ell <= 0.96 and dith(306 + dx, 344 + dy, 0.80):
                over(306 + dx, 344 + dy, '#ef4444' if (dx + dy) % 2 else '#ffffff', 0.48)


def dibuja_kaido_dragon(cx, by):
    """Colosal Kaido Forma Dragón Azul serpenteando desde el cielo derecho (y=124..304)."""
    k0, k1, k2, k_hi, mane = PAL['kaido']
    f0, f1, f2, f3 = PAL['fire']

    # Nubes de llamas (Homuragumo) envolviendo el cuerpo de Kaido
    for lx_n, ly_n, r_n in ((412, 232, 18), (452, 198, 16), (368, 250, 14), (446, 266, 17)):
        glow(lx_n, ly_n, r_n + 6, f0, 0.55)
        disc(lx_n, ly_n, r_n - 4, f1)
        disc(lx_n - 3, ly_n - 3, max(2, r_n - 9), f2)

    # Cuerpo serpentino grueso en S con escamas, cresta dorsal y vientre dorado/pálido
    for s in range(132):
        u = s / 131.0
        px = int(round(366 + math.sin(u * math.pi * 2.1) * 48 + u * 78))
        py = int(round(142 + u * 144))
        if px > 475 and py < 210:
            continue
        rad = max(5, int(round(14 * math.sin(u * math.pi * 0.85 + 0.25))))
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                if dx * dx + dy * dy <= rad * rad:
                    scale_pat = ((s + dx + dy) % 4 == 0)
                    col = k_hi if dy < -rad // 2 else (k2 if scale_pat else (k1 if dx < 0 else k0))
                    if dy > rad // 2 and abs(dx) < rad // 2:
                        col = '#fde68a'
                    put(px + dx, py + dy, col)
        # Púas dorsales violeta-púrpura
        if s % 4 == 0:
            for sp in range(5):
                put(px - rad // 2, py - rad - sp, mane if sp > 1 else k2)

    # Gran Cabeza de Dragón de Kaido mirando a Luffy (cx=358, cy=204)
    hx, hy = 358, 204
    for dy in range(-18, 20):
        for dx in range(-22, 24):
            if (dx * dx) / 480.0 + (dy * dy) / 320.0 <= 1.0:
                if dy > 6 and dx < -4:
                    continue  # Boca abierta rugiendo
                col = k1 if dy < 0 else (k0 if dx > 0 else k_hi)
                put(hx + dx, hy + dy, col)
    # Fauces abiertas con dientes blancos y fuego Bolo Breath
    for dy in range(4, 15):
        for dx in range(-22, -2):
            put(hx + dx, hy + dy, f0 if dy < 12 else k2)
    for tx in range(-20, -4, 4):
        put(hx + tx, hy + 4, '#ffffff')
        put(hx + tx, hy + 13, '#ffffff')
    # Ojo feroz amarillo y cuernos negros curvados
    put(hx - 6, hy - 5, '#fef08a')
    put(hx - 5, hy - 5, '#dc2626')
    for k in range(20):
        put(hx + 6 + k, hy - 14 - int(k * 0.9), '#0f172a')
        put(hx + 7 + k, hy - 14 - int(k * 0.9), '#334155')
    # Bigotes largos dorados
    for k in range(26):
        wx = hx - 18 - k
        wy = hy + int(6 * math.sin(k * 0.28))
        put(wx, wy, '#fef08a')

    # Chorros de aliento Bolo Breath hacia el choque central (308, 276)
    for k in range(42):
        u = k / 41.0
        bx = int(hx - 20 + (308 - (hx - 20)) * u)
        by_b = int(hy + 10 + (276 - (hy + 10)) * u)
        r_b = int(3 + 6 * u)
        disc(bx, by_b, r_b, f0 if u < 0.7 else f1)
        disc(bx, by_b, max(1, r_b - 2), f2 if u < 0.5 else f3)


def dibuja_luffy_gear5_hero(cx, by):
    """Monkey D. Luffy Gear 5 (Dios del Sol Nika) 48x38 px + Bufanda Hagoromo + Bajrang Gun."""
    w0, w1, sh, sash, ink = PAL['nika']
    f0, f1, f2, _ = PAL['fire']

    # Bufanda/cinta divina Hagoromo de nube blanca ondulando detrás de los hombros
    for s in range(44):
        u = s / 43.0
        px = int(cx - 32 + u * 64)
        py = int(by - 34 + 12 * math.sin(u * math.pi * 1.4))
        rad = 4 if (0.15 < u < 0.85) else 2
        disc(px, py, rad, w1)
        disc(px - 1, py - 1, max(1, rad - 1), w0)

    if not ANIM:
        glow(cx, by - 26, 26, w0, 0.36)

    spr = [
        '........WWWW.......WWWW........WWWW...',
        '.......WWWWWW....WWWWWW......WWWWWW...',
        '......WWWWWWWW..WWWWWWWW....WWWWWWWW..',
        '......WWWWWWWWWWWWWWWWWW....WWWWWWWW..',
        '.......WWWWW11111111WWWWWWWWWWWWWW....',
        '.......WWWWCCCCCCCCCC11WWWWWWWW.......',
        '.......WWWCCKKCCCCKKCC1WWWW...........',
        '.......WWWCCCCCCCCCCCCWWWW............',
        '........KKCCWWWWWWWWCCKK..............',
        '........KKCCWWWWWWWWCCKK..............',
        '.........KKCCCCCCCCCCKK...............',
        '........WWWWWWWWWWWWWWWW..............',
        '.......WWWCCCXXXXXXCCCWWW.............',
        '......WWWWCCCCXCCXCCCCWWWW............',
        '.....KWWKKCCCXXXXXXCCCWWWK............',
        '.....KWWK.CCCCCCCCCCCCKWWK............',
        '....KWWWK.CCCCCCCCCCCCKWWWK...........',
        '....KWWK..CCCSSCCSSCCCKWWWK...........',
        '...KWWWK..CCCCCCCCCCCCKWWWK...........',
        '...KWWK...KPPPPPPPPPPKKWWWW...........',
        '....KK....KPPPPPPPPPPK.WWWW...........',
        '..........KPPPP11PPPPK................',
        '..........KWWWWWWWWWWK................',
        '.........KWWWWWWWWWWWWK...............',
        '.........KWWWWW11WWWWWK...............',
        '.........KWWWWWWWWWWWWK...............',
        '.........KWWWWW..WWWWWK...............',
        '........KWWWWW....WWWWWK..............',
        '........KWWWWW....WWWWWK..............',
        '........WWWWWW....WWWWWW..............',
        '........CCCCCC....CCCCCC..............',
        '.......CCCCCC......CCCCCC.............',
        '.......CCCCCC......CCCCCC.............',
        '......CCCCCC........CCCCCC............',
        '......CCCCCC........CCCCCC............',
        '.....CCCCCC..........CCCCCC...........',
        '.....CCCCCC..........CCCCCC...........',
        '.....CCCCCC..........CCCCCC...........',
        '....CCCCCCC..........CCCCCCC..........',
        '....CCCCCC............CCCCCC..........',
    ]
    cmap = {'W': w0, '1': w1, 'C': '#f6d4c2', 'K': ink, 'X': '#d45a5a', 'S': '#dfb49e', 'P': sash}
    pinta_sprite(lz, cx, by, spr, cmap)

    # Puño colosal Haki Gear 5 cargando impacto arriba-derecha de Luffy (cx+32, by-38 -> 238, 310)
    gx, gy = cx + 32, by - 42
    glow(gx, gy, 18, f0, 0.65)
    disc(gx, gy, 10, '#1e1b2e')
    disc(gx - 2, gy - 2, 8, '#475569')
    disc(gx - 3, gy - 3, 4, '#cbd5e1')

    # Rayos negros y carmesí de Haki del Conquistador irradiando de Luffy
    for ang_d in (-135, -75, -20, 25, 145):
        a = math.radians(ang_d)
        for k in range(28):
            rx = int(cx + math.cos(a) * (14 + k) + math.sin(k * 0.8) * 3)
            ry = int(by - 26 + math.sin(a) * (14 + k) + math.cos(k * 0.8) * 2)
            put(rx, ry, '#050208' if k % 3 == 0 else '#ef4444')
    if ANIM:
        RUNAS.append([cx, by - 26])
        RUNAS.append([308, 276])


dibuja_onigashima_fondo()
dibuja_cupula_onigashima()
dibuja_kaido_dragon(404, 344)
dibuja_luffy_gear5_hero(204, 348)

# Choque central explosivo entre Bajrang Gun y Bolo Breath (308, 276)
if not ANIM:
    glow(308, 276, 30, '#ef4444', 0.65)
    glow(308, 276, 16, '#fef08a', 0.85)
    disc(308, 276, 7, '#ffffff')

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
