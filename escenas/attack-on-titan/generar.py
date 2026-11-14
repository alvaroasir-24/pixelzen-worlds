#!/usr/bin/env python3
"""PixelZen Worlds - Attack on Titan (Principal): Muralla María, El Retumbar, Mikasa y Levi."""
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
FASE = os.environ.get('PZ_FASE', 'dorado')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1201)

PALETAS = {
    'noche': dict(
        sky=['#090408', '#14080e', '#240e14', '#381418', '#4e1c1b', '#68261d', '#843420', '#a44624', '#c45c2c', '#e27838'],
        wall=('#201920', '#322630', '#120d12', '#4c3a46'),
        bone=('#dfd4c4', '#b8aa98', '#786c60', '#f6efe4'),
        colossal=('#5a1414', '#8e2420', '#300a0b', '#ff8c3a'),
        roof=('#3c1a16', '#5c2820', '#200c0b', '#7a382c'),
        road=('#1a1418', '#282026', '#0e0a0d', '#3a2e36'),
        scouts=('#1b3c28', '#2c5a3e', '#523426', '#b82028', '#e2e8f0'),
        vig=0.72,
        nube=['#2c141c', '#421e24', '#5c2a2a', '#7c3a30', '#9e4c36', '#200e14'],
    ),
    'dorado': dict(
        sky=['#160708', '#2c0d0e', '#461512', '#642014', '#862e16', '#aa4018', '#cc581c', '#ea7424', '#fc9834', '#ffc458'],
        wall=('#302226', '#463236', '#1c1216', '#66484c'),
        bone=('#eee2ce', '#c6b6a0', '#847466', '#fff8ec'),
        colossal=('#721a16', '#b22e24', '#3a0c0a', '#ffa242'),
        roof=('#56241a', '#7e3626', '#2c100c', '#a24a34'),
        road=('#281c1e', '#3a282c', '#140e10', '#523c40'),
        scouts=('#204830', '#346a46', '#623e2c', '#cc242e', '#f1f5f9'),
        vig=0.80,
        nube=['#4e1c1a', '#6e2820', '#923824', '#b84c28', '#dc6a32', '#381214'],
    ),
    'dia': dict(
        sky=['#1c4476', '#2a5a92', '#3b72b0', '#508ac8', '#6ca4dc', '#8cbce8', '#aed2f0', '#cee4f4', '#ebe6d2', '#f8d2b2'],
        wall=('#504a52', '#6c6470', '#343038', '#8c8290'),
        bone=('#eee6d8', '#c8beb2', '#90867a', '#ffffff'),
        colossal=('#8c2824', '#c24034', '#4a1210', '#ff983c'),
        roof=('#783428', '#9e4838', '#421a14', '#bc5e4a'),
        road=('#3e3840', '#544c56', '#262228', '#6e6470'),
        scouts=('#265438', '#3c7a52', '#704a34', '#dc2626', '#ffffff'),
        vig=0.88,
        nube=['#f6f2f6', '#ebe2e8', '#dfd0dc', '#fbf8fa', '#e8d8de', '#c4b8ca'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#f97316', '#ef4444'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#fb923c', base='#fff4e8', sombra='#ddc0b8', crater='#b8948e', crater_hi='#ccb0a8'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ff9848', centro='#fff8ea', borde='#ff4e20', rayo='#ff7838'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffe4c4', '#fecaca', '#fed7aa'])

MX, MY, MR = 340, 62, 36
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#fb923c', base='#fff4e8', sombra='#ddc0b8', crater='#b8948e', crater_hi='#ccb0a8')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 342, 134, 24, halo='#ff843c', centro='#fff2d8', borde='#ff461e', rayo='#ff6a30')
    else:
        dibuja_sol_estandar(lz, 324, 72, 22, halo='#ffd488', centro='#fffdf0', borde='#ffb448', rayo='#ffd88c')

NUBES_DEF = [
    (88, 36, 94, PAL['nube'][0], 2),
    (248, 52, 110, PAL['nube'][2], 2),
    (422, 42, 86, PAL['nube'][3], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)


def dibuja_fundador_y_colosales():
    """Gigantesco Titán Fundador esquelético de Eren + fila de Titanes Colosales + Muralla María (y=74..258)."""
    bn0, bn1, bn2, bn3 = PAL['bone']
    cl0, cl1, cl2, cl_em = PAL['colossal']
    w0, w1, w2, w3 = PAL['wall']

    # 1. Columnas de vapor blanco-caliente detrás de los Colosales (izquierda y centro)
    for cx_s, top_s in ((42, 118), (112, 108), (186, 100), (264, 108), (356, 116), (434, 132)):
        for y in range(top_s, 254):
            u = (y - top_s) / max(1, 254 - top_s)
            hw = int(12 + 14 * (1.0 - u) + 4 * math.sin(y * 0.14 + cx_s))
            for dx in range(-hw, hw + 1):
                if abs(dx) < hw and dith(cx_s + dx, y, 0.42 * (0.4 + 0.6 * math.sin(y * 0.08 + dx * 0.1))):
                    over(cx_s + dx, y, '#fef3c7' if dx < 0 else '#cbd5e1', 0.24)

    # 2. Enorme Arco de Costillas del Titán Fundador de Eren (cx=184, top_y=74 .. y=252)
    fx, fy = 178, 78
    for rib_i in range(-6, 7):
        rib_spread = rib_i * 18
        for k in range(136):
            u = k / 135.0
            rx = int(fx + rib_spread + rib_i * u * 8 + math.sin(u * math.pi) * (8 if rib_i >= 0 else -8))
            ry = fy + int(u * 172)
            thick = max(1, int(3 - abs(rib_i) * 0.18))
            for t in range(-thick, thick + 1):
                put(rx + t, ry, bn3 if t < 0 else (bn0 if t == 0 else bn2))
    # Espina dorsal arqueada superior + Cabeza suspendida del Fundador (cx=292, cy=124)
    for k in range(120):
        u = k / 119.0
        sx = int(60 + u * 232)
        sy = int(112 - 36 * math.sin(u * math.pi * 0.92))
        for t in range(-3, 4):
            put(sx, sy + t, bn3 if (k % 8 < 4 and t < 0) else (bn2 if t > 1 else bn1))
    # Cráneo colgante del Titán Fundador con pelo largo oscuro, pómulos hundidos y ojos verde esmeralda
    hx, hy = 294, 134
    for dy in range(-14, 18):
        for dx in range(-12, 13):
            in_cranium = (dx * dx / 92.0 + dy * dy / 196.0 <= 1.0) and (dy < 6 or abs(dx) <= 9 - (dy - 6) // 2)
            if in_cranium:
                col_f = bn2 if (abs(dx) > 7 or dy > 8) else (bn3 if dy < -2 else bn0)
                if math.hypot(abs(dx) - 4, dy) < 2.4:
                    col_f = '#12080a'
                elif abs(dx) <= 1 and 2 <= dy <= 5:
                    col_f = '#1a0c0e'
                elif 7 <= dy <= 12 and abs(dx) <= 5:
                    col_f = bn3 if (dx + dy) % 2 == 0 else '#241418'
                put(hx + dx, hy + dy, col_f)
    # Cabellera larga y oscura cayendo a ambos lados + vértebras cervicales
    for dy in range(-18, 22):
        sway = int(math.sin(dy * 0.25) * 2)
        for dx in (-11, -10, -9, 9, 10, 11):
            if abs(dx) >= 9 or dy < -8:
                put(hx + dx + (sway if dy > 0 else 0), hy + dy, '#0d090d' if dy > 0 else '#1a121a')
    for dx in (-4, 4):
        put(hx + dx, hy, '#4ade80')
        put(hx + dx + (1 if dx > 0 else -1), hy, '#22c55e')
    if ANIM:
        RUNAS.append([hx, hy])

    # 3. Titanes Colosales anatómicos marchando entre columnas de vapor en el horizonte
    for tx, ty, sc in ((48, 174, 0.92), (124, 168, 1.04), (218, 172, 0.96), (376, 178, 0.88), (450, 192, 0.78)):
        th = int(78 * sc)
        for y in range(ty, min(256, ty + th)):
            u = (y - ty) / float(th)
            if u < 0.20:
                lu = u / 0.20
                hw = max(3, int(9 * sc * math.sin(max(0.2, lu) * math.pi * 0.85)))
            elif u < 0.28:
                hw = int(7 * sc)
            elif u < 0.44:
                lu = (u - 0.28) / 0.16
                hw = int((11 + 12 * math.sin(lu * math.pi * 0.5)) * sc)
            else:
                lu = (u - 0.44) / 0.56
                hw = int((23 - 6 * lu) * sc)
            for dx in range(-hw, hw + 1):
                norm_x = dx / float(max(1, hw))
                # Separación sutil brazos / torso en la parte media-baja
                if u > 0.44 and 0.62 < abs(norm_x) < 0.74:
                    continue
                fib = ((dx * dx + y * 3) % 7 == 0)
                is_rib = (0.36 <= u <= 0.68 and abs(norm_x) < 0.56 and (y % 4 == 0))
                is_em = (abs(dx) < hw // 2 and u > 0.34 and (dx % 5 == 0) and dith(tx + dx, y, 0.55))
                if is_em:
                    col = cl_em
                elif is_rib:
                    col = '#e5d4be' if dx % 2 else cl1
                else:
                    col = cl2 if (fib or norm_x > 0.72) else (cl1 if norm_x < -0.25 else cl0)
                put(tx + dx, y, col)
        # Cuencas oscuras y ojos brasa
        ey = ty + int(th * 0.10)
        ex_off = max(2, int(3 * sc))
        for ex in (tx - ex_off, tx + ex_off):
            put(ex - 1, ey, '#1a0608')
            put(ex, ey, '#fef08a')
            put(ex, ey + 1, '#f97316')
        # Volutas de vapor espeso envolviendo cintura y piernas
        for st_dx, st_dy in ((-12, -16), (0, -10), (12, -18), (-6, -24), (8, -22)):
            for sy in range(-5, 6):
                for sx in range(-7, 8):
                    if sx * sx / 49.0 + sy * sy / 25.0 <= 1.0 and dith(tx + st_dx + sx, 250 + st_dy + sy, 0.52):
                        over(tx + st_dx + sx, 250 + st_dy + sy, '#fde68a' if sy < 0 else '#cbd5e1', 0.34)
        if ANIM and sc > 0.9:
            FAROLES.append([tx, ey, 6])

    # 4. Muralla María rota en tramos laterales y centro-derecha (y=214..258)
    for wx0, wx1 in ((0, 96), (240, 344), (484, 640)):
        for y in range(218, 258):
            if y < 226 and (wx0 == 0 and x_brk(wx0, wx1, y) if False else False):
                pass
            for x in range(wx0, wx1):
                if (x in range(74, 96) or x in range(240, 260)) and y < 228 + (x % 9):
                    continue
                brick = ((x + (y // 6) * 8) % 16 == 0) or (y % 6 == 0)
                put(x, y, w2 if brick else (w3 if y < 224 else (w1 if (x % 7 == 0) else w0)))


def dibuja_shiganshina_primer_plano():
    """Tejados de teja terracota y calle empedrada de Shiganshina en y=254..400."""
    rf0, rf1, rf2, rf3 = PAL['roof']
    rd0, rd1, rd2, rd3 = PAL['road']
    w0, w1, w2, w3 = PAL['wall']
    r_g = Ruido(1209)

    for y in range(254, H):
        for x in range(W):
            n = fbm(r_g, x * 0.04 + y * 0.05)
            seam = (y % 9 == 0) or ((x + (y // 9) * 11) % 22 == 0)
            col = rd2 if seam else (rd3 if n > 0.62 else (rd1 if n > 0.40 else rd0))
            put(x, y, col)

    # Casas y tejados inclinados laterales donde luchan Mikasa y Levi (izquierda x=0..158, derecha x=470..640)
    for hx0, hx1, hy_top, slant in ((0, 148, 300, 0.14), (486, 640, 304, -0.14)):
        for x in range(hx0, hx1):
            yt = int(hy_top + (x - hx0) * slant) if slant > 0 else int(hy_top + (hx1 - x) * (-slant))
            for y in range(yt, H):
                if y < yt + 36:
                    tile = ((y - yt) % 5 == 0) or ((x + y) % 8 == 0)
                    put(x, y, rf2 if tile else (rf3 if y < yt + 6 else (rf1 if x % 3 else rf0)))
                else:
                    # Pared con entramado de madera Fachwerk
                    beam = (abs(y - yt - 36) <= 2) or (x % 26 in (0, 1))
                    put(x, y, rf2 if beam else (w3 if x % 5 else w1))

    # Grietas sísmicas ardientes en la calzada del Retumbar
    for rx in (188, 256, 338, 434):
        for k in range(18):
            gx = rx + int(math.sin(k * 0.7) * 5)
            gy = 356 + k * 2
            put(gx, gy, PAL['colossal'][3] if k % 3 == 0 else '#0c0608')
            put(gx + 1, gy, '#0c0608')


def dibuja_mikasa_hero(cx, by):
    """Mikasa Ackerman 46x34 con bufanda roja al viento, Alas de la Libertad y dobles hojas ODM."""
    g0, g1, br, red, steel = PAL['scouts']
    spr = [
        '............KKKKKKKKKK............',
        '..........KKKKKKKKKKKKKK..........',
        '.........KKKKKKKKKKKKKKKK.........',
        '........KKKKKKKKKKKKKKKKKK........',
        '.......KKKKKCCCCCCCCCCKKKKK.......',
        '.......KKKKCCCCCCCCCCCCKKKK.......',
        '.......KKKCCKKCCCCCCKKCCKKK.......',
        '........KCCCCCCCCCCCCCCCCK........',
        '........KCCRRRRRRRRRRRRCCK........',
        '....RRRRRRRRRRRRRRRRRRRRRK........',
        '..RRRRRRRRRRRRRRRRRRRRRRR.........',
        '.RRRRR..GGGGGGGGGGGGGGGG..........',
        '........GGGGGGGGGGGGGGGGGG........',
        '.......GGGGGGWGGGGWWGGGGGG........',
        '......GGGGGWWWWGGWWWWGGGGGG.......',
        '.....GGGGGBBBBBBBBBBBBGGGGGG......',
        '....KSSKKGBBBBBBBBBBBBGKKSSK......',
        '...KSSSKKBBBBGGGGGGGBBBKKSSSK.....',
        '..SSSSSKBBBBBBBBBBBBBBBBKSSSSS....',
        '.SSSSS.KBBBCCCCCCCCCCBBBK.SSSSS...',
        'SSSS...KKBBCCCCCCCCCCBBKK...SSSS..',
        '........KBBBBBBBBBBBBBBK..........',
        '........KBBKKBBBBBBKKBBK..........',
        '........KKKKKKKKKKKKKKKK..........',
        '........KKKKWWWWWWWWKKKK..........',
        '.......KKKKWWWWWWWWWWKKKK.........',
        '.......KSSSWWWWWWWWWWSSSK.........',
        '.......KSSSWWWW..WWWWSSSK.........',
        '........KKKWWWW..WWWWKKK..........',
        '..........WWWW....WWWW............',
        '..........WWWW....WWWW............',
        '.........WWWW......WWWW...........',
        '.........BBBB......BBBB...........',
        '........BBBBBB....BBBBBB..........',
        '........BBBBBB....BBBBBB..........',
        '........BBBBBB....BBBBBB..........',
        '.......BBBBBBB....BBBBBBB.........',
        '.......KKKKKKK....KKKKKKK.........',
        '......KKKKKKKK....KKKKKKKK........',
        '......KKKKKKKK....KKKKKKKK........',
    ]
    cmap = {'K': '#0e1018', 'C': '#f4d2be', 'R': red, 'G': g0, 'W': steel, 'B': br, 'S': '#cbd5e1'}
    pinta_sprite(lz, cx, by, spr, cmap)
    # Cables ODM tensos disparados hacia la derecha-arriba
    for ox_c, oy_c, tx_c, ty_c in ((-10, -24, cx - 58, by - 78), (10, -24, cx + 56, by - 82)):
        for k in range(28):
            u = k / 27.0
            px = int(cx + ox_c + (tx_c - (cx + ox_c)) * u)
            py = int(by + oy_c + (ty_c - (by + oy_c)) * u)
            over(px, py, '#e2e8f0', 0.72)


def dibuja_levi_hero(cx, by):
    """Capitán Levi Ackerman 46x34 en pose de corte giratorio con capa verde y estela de cuchillas."""
    g0, g1, br, red, steel = PAL['scouts']
    spr = [
        '............KKKKKKKKKK............',
        '..........KKKKKKKKKKKKKK..........',
        '.........KKKKKKKKKKKKKKKK.........',
        '........KKKKKKKKKKKKKKKKKK........',
        '........KKKCCCCCCCCCCCCKKK........',
        '........KKCCKKCCCCCCKKCCKK........',
        '........KKCCCCCCCCCCCCCCKK........',
        '.........KCCCCCCCCCCCCCCK.........',
        '.........KKWWWWWWWWWWWWKK.........',
        '........GGGGWWWWWWWWWWGGGG........',
        '......GGGGGGGGGGGGGGGGGGGGGG......',
        '....GGGGGG11GGGGGGWWGGGGGGGGGG....',
        '...GGGGGG11GGGGGGWWWWGGGGGGGGGG...',
        '..GGGGGGGGGGBBBBBBBBBBBBGGGGGG....',
        '.GGGGGGGGGBBBBBBBBBBBBBBBBGGGGG...',
        'GGGGGGGGKKBBBBWWWWWWWWBBBBKKSSSSS.',
        '.GGGGGGKSSKBBBBBBBBBBBBBBKSSSSSSS.',
        '..GGGG..KKKBBBBBBBBBBBBBBKKSSSSSS.',
        '..........KBBBBGGGGGGGBBBK........',
        '.........KBBBBBBBBBBBBBBBBK.......',
        '........KKBBBBBBBBBBBBBBBBKK......',
        '........KSSSKWWWWWWWWWWKSSSK......',
        '........KSSSKWWWWWWWWWWKSSSK......',
        '.........KKKKWWWW..WWWWKKKK.......',
        '..........KKKWWWW..WWWWKKK........',
        '..........WWWWWW....WWWWWW........',
        '.........WWWWWW......WWWWWW.......',
        '........WWWWWW........WWWWWW......',
        '........BBBBBB........BBBBBB......',
        '.......BBBBBBB........BBBBBBB.....',
        '.......BBBBBB..........BBBBBB.....',
        '......BBBBBBB..........BBBBBBB....',
        '......KKKKKKK..........KKKKKKK....',
        '.....KKKKKKKK..........KKKKKKKK...',
    ]
    cmap = {'K': '#0c0e16', 'C': '#f0ceba', 'W': steel, 'G': g0, '1': g1, 'B': br, 'S': '#f8fafc'}
    pinta_sprite(lz, cx, by, spr, cmap)
    # Arco plateado de corte giratorio alrededor de Levi
    for deg in range(-55, 195, 4):
        a = math.radians(deg)
        for rad in (24, 25):
            ax = cx + int(round(math.cos(a) * rad))
            ay = (by - 18) + int(round(math.sin(a) * rad * 0.72))
            over(ax, ay, '#ffffff' if rad == 25 else '#93c5fd', 0.85)
    if ANIM:
        RUNAS.append([cx, by - 22])
    else:
        glow(cx, by - 22, 14, '#38bdf8', 0.35)


dibuja_fundador_y_colosales()
dibuja_shiganshina_primer_plano()
dibuja_mikasa_hero(210, 350)
dibuja_levi_hero(392, 344)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
