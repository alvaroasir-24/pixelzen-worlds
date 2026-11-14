#!/usr/bin/env python3
"""PixelZen Worlds - Jujutsu Kaisen (Principal): Santuario Malevolente (Sukuna) vs Vacío Infinito (Gojo)."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, exporta_salida, exporta_sprites_si_aplica, fbm, mix, pinta_sprite,
    render_cielo, render_estrellas, render_lago, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1101)

PALETAS = {
    'noche': dict(
        sky=['#0a030a', '#160612', '#260a1a', '#3b1022', '#521528', '#6e1b2d', '#8c2432', '#aa303a', '#c44248', '#de5c5a'],
        void=['#040614', '#080e28', '#101b48', '#1d2d6e', '#2e4698', '#466ee0', '#70a8ff', '#cce8ff'],
        ruin=('#140d1c', '#20162c', '#0b0712'),
        shrine_wood=('#240d14', '#3c141d', '#14060a', '#5c1e2a'),
        shrine_roof=('#1a101a', '#2c1c2c', '#0e0810', '#482e46'),
        bone=('#d8ccb8', '#b8aa96', '#7e7062', '#f2e8d8'),
        agua='#100a1c',
        olas=('#c084fc', '#f43f5e', '#4c1d95'),
        reflejo=('#f5d0fe', '#38bdf8'),
        sukuna=('#f2eadc', '#c8bba8', '#241620', '#ff6488', '#ff2848'),
        gojo=('#181c2c', '#2c3450', '#f0f6ff', '#cbd8ee', '#38d8ff'),
        vig=0.72,
        nube=['#2a1226', '#401b32', '#5a243e', '#76304c', '#923f5a', '#1e0b1c'],
    ),
    'dorado': dict(
        sky=['#140612', '#260c1e', '#40142a', '#5e1e34', '#802838', '#a4383a', '#c6503a', '#e46e3c', '#f89448', '#ffc268'],
        void=['#080a20', '#12183a', '#1e2c64', '#30448e', '#4866ba', '#6a90e6', '#94c0ff', '#e0f0ff'],
        ruin=('#241422', '#382032', '#140a14'),
        shrine_wood=('#34121a', '#541e28', '#1c080d', '#7a2b36'),
        shrine_roof=('#261624', '#3e2438', '#140b14', '#603854'),
        bone=('#e8dcc6', '#c6b69e', '#8e7c6c', '#fff4e2'),
        agua='#1e1024',
        olas=('#fda4af', '#a855f7', '#581c87'),
        reflejo=('#ffe49c', '#93c5fd'),
        sukuna=('#f6eee0', '#d2c4b0', '#2a1822', '#ff7092', '#ff3454'),
        gojo=('#1e2234', '#343c5c', '#f6faff', '#d2deef', '#4ae2ff'),
        vig=0.80,
        nube=['#441a2e', '#62263c', '#843448', '#aa4652', '#cf605e', '#321222'],
    ),
    'dia': dict(
        sky=['#183668', '#244b84', '#3462a0', '#487cb8', '#6296ce', '#82b2e0', '#a4ccf0', '#c8e2f8', '#e8dcf0', '#f6c8cc'],
        void=['#10204c', '#1a3272', '#2a4c9e', '#3e6bc6', '#5c90e8', '#86b6fc', '#b8daff', '#e8f4ff'],
        ruin=('#383448', '#4e4860', '#242030'),
        shrine_wood=('#4a1c24', '#6c2a34', '#2c1016', '#923a46'),
        shrine_roof=('#32283c', '#4c3e58', '#1e1624', '#6a587a'),
        bone=('#ece4d8', '#c6bcb0', '#92887c', '#ffffff'),
        agua='#263868',
        olas=('#e9d5ff', '#93c5fd', '#5b21b6'),
        reflejo=('#fff0c8', '#a5f3fc'),
        sukuna=('#faf4e8', '#d6cab8', '#2a1a24', '#ff7494', '#ef2342'),
        gojo=('#202638', '#384262', '#ffffff', '#dce6f4', '#22d3ee'),
        vig=0.88,
        nube=['#f4eef6', '#e6dce8', '#d8cce0', '#fbf8fc', '#e2d4dc', '#bfb4c8'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#f43f5e', '#a855f7'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#a855f7', base='#f5f3ff', sombra='#c4b5fd', crater='#9370db', crater_hi='#b49cf0'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#fda4af', centro='#fff8f0', borde='#fb7185', rayo='#fecdd3'),
)

# Cielo partido: Mitad derecha transformada en Vacío Infinito (cielo abismal cósmico)
vc = PAL['void']
r_split = Ruido(42)
r_neb = Ruido(91)
for y in range(HOR):
    ridge = 312 + int(18 * math.sin(y * 0.036) + 12 * (fbm(r_split, y * 0.05) - 0.5))
    for x in range(max(0, ridge - 18), W):
        t_split = max(0.0, min(1.0, (x - ridge + 18) / 28.0))
        d_horizon = y / float(HOR)
        idx = min(len(vc) - 2, int((1.0 - d_horizon) * (len(vc) - 3) + 0.5))
        c_v = mix(vc[idx], vc[idx + 1], (y % 18) / 18.0)
        neb = fbm(r_neb, x * 0.022 + y * 0.031)
        if neb > 0.58:
            c_v = mix(c_v, '#a855f7' if (x + y) % 5 else '#38bdf8', (neb - 0.58) * 1.1)
        if t_split >= 0.99 or dith(x, y, t_split):
            put(x, y, c_v)

render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#e0f2fe', '#e9d5ff', '#fbcfe8'])

MX, MY, MR = 312, 58, 34
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#a855f7', base='#f5f3ff', sombra='#c4b5fd', crater='#9370db', crater_hi='#b49cf0')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 312, 118, 22, halo='#fda4af', centro='#fff5f5', borde='#f43f5e', rayo='#fda4af')
    else:
        dibuja_sol_estandar(lz, 312, 68, 22, halo='#bae6fd', centro='#ffffff', borde='#7dd3fc', rayo='#bae6fd')

NUBES_DEF = [
    (78, 42, 82, PAL['nube'][0], 2),
    (196, 62, 88, PAL['nube'][2], 2),
    (442, 46, 86, PAL['nube'][3], 2),
    (562, 66, 74, PAL['nube'][4], 1),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)


def dibuja_vacio_infinito_esfera(cx, cy):
    """Horizonte de sucesos de Vacío Infinito flotando en el cielo derecho."""
    vc = PAL['void']
    for dy in range(-52, 53):
        for dx in range(-52, 53):
            r = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            if r < 13:
                put(cx + dx, cy + dy, '#040510')
            elif r < 17:
                put(cx + dx, cy + dy, '#e0f2fe' if r < 15.2 else '#38bdf8')
            elif r < 50:
                wave = 0.5 + 0.5 * math.sin(r * 0.44 - ang * 2.0)
                fade = max(0.0, 1.0 - (r - 17) / 33.0)
                col = mix(vc[4], '#c084fc' if wave > 0.5 else '#38bdf8', fade * 0.82)
                if dith(cx + dx, cy + dy, fade * 0.72 + wave * 0.25):
                    over(cx + dx, cy + dy, col, min(0.88, fade * 0.9))
    for t in range(-64, 65):
        ew = int(10 * math.sqrt(max(0.0, 1.0 - (t / 64.0) ** 2)))
        for s in range(-2, 3):
            over(cx + t, cy + int(s * 0.5 + (ew // 4) * (1 if t > 0 else -1) * 0.22), '#bae6fd' if abs(s) <= 1 else '#a855f7', 0.68)
    for rx, ry, rw, rh in ((392, 138, 7, 5), (496, 122, 8, 6), (512, 198, 6, 4), (404, 212, 5, 5), (470, 224, 7, 4)):
        for dy in range(rh):
            for dx in range(rw):
                put(rx + dx, ry + dy, PAL['ruin'][0] if dx == 0 or dy == 0 else PAL['ruin'][2])


def dibuja_skyline_shinjuku():
    """Rascacielos partidos de Shinjuku sobre el horizonte (y<=HOR=280)."""
    r0, r1, r2 = PAL['ruin']
    edificios = [
        (0, 32, 168), (34, 28, 186), (64, 26, 158), (254, 34, 196),
        (290, 36, 214), (330, 30, 194), (364, 32, 174),
        (518, 34, 158), (556, 38, 146), (598, 42, 164),
    ]
    for x0, bw, top_y in edificios:
        seed_b = x0 * 13 + top_y
        cut_slope = ((seed_b % 3) - 1) * 0.25
        for x in range(x0, min(W, x0 + bw)):
            ty = int(top_y + (x - x0) * cut_slope)
            for y in range(ty, HOR):
                is_edge = (x == x0 or x == x0 + bw - 1 or y == ty)
                is_floor = ((y - ty) % 10 == 0)
                col = r2 if is_edge else (r1 if is_floor else r0)
                put(x, y, col)
                if (x - x0) % 6 == 3 and (y - ty) > 6 and (y - ty) % 10 == 4 and ((x * 7 + y * 11) % 4 == 0):
                    wcol = '#fb7185' if x < 312 else '#60a5fa'
                    put(x, y, wcol)
                    put(x + 1, y, wcol)
                    if len(VENTANAS) < 40 and x % 2 == 0:
                        VENTANAS.append([x, y, 2])


def dibuja_santuario_malevolente(cx, by):
    """Santuario Malevolente (Fukuma Mizushi) completo encima de by=HOR (280)."""
    wd0, wd1, wd2, wd3 = PAL['shrine_wood']
    rf0, rf1, rf2, rf3 = PAL['shrine_roof']
    bn0, bn1, bn2, bn3 = PAL['bone']

    # Base de piedra/huesos (y = by-16 .. by)
    for dy in range(16):
        y = by - 15 + dy
        hw = 58 + int(dy * 0.7)
        for dx in range(-hw, hw + 1):
            put(cx + dx, y, wd2 if abs(dx) > hw - 3 else (wd0 if dy % 4 else wd1))
    for step in range(4):
        sy = by - 12 + step * 3
        sw = 16 + step * 3
        for dx in range(-sw, sw + 1):
            put(cx + dx, sy, wd3 if dx % 2 == 0 else wd1)
            put(cx + dx, sy + 1, wd2)

    # Columnas y altar oscuro (y = by-66 .. by-15)
    for px in (-42, -21, 21, 42):
        for y in range(by - 66, by - 15):
            for dx in range(-3, 4):
                put(cx + px + dx, y, wd3 if dx < 0 else (wd1 if dx == 0 else wd2))
    for y in range(by - 62, by - 16):
        for dx in range(-21, 22):
            put(cx + dx, y, '#070206' if abs(dx) < 16 else wd0)

    # Doble tejado curvo (sori) conectado claramente a la estructura
    for tier_y, hw_r, h_r in ((by - 66, 66, 18), (by - 92, 50, 20)):
        for x_off in range(-hw_r, hw_r + 1):
            u = abs(x_off) / float(hw_r)
            lift = int(9 * (u ** 2.3))
            y_bot = tier_y - lift
            y_top = tier_y - h_r + int(h_r * (u ** 1.35)) - lift // 2
            for y in range(y_top, y_bot + 1):
                if y == y_top or y == y_bot:
                    col = rf2
                elif (y - y_top) <= 2:
                    col = rf3
                elif (x_off % 5 == 0):
                    col = rf1
                else:
                    col = rf0
                put(cx + x_off, y, col)
            if abs(x_off) >= hw_r - 5:
                put(cx + x_off, y_top - 1, PAL['sukuna'][4])
    # Cuerpo intermedio entre ambos tejados
    for y in range(by - 92, by - 82):
        for dx in range(-22, 23):
            put(cx + dx, y, wd2 if abs(dx) > 19 else wd0)

    # Chapitel Sorin (y = by-134 .. by-110)
    for y in range(by - 134, by - 110):
        w_sp = 1 if y < by - 122 else 2
        for dx in range(-w_sp, w_sp + 1):
            put(cx + dx, y, rf3 if (y % 4 == 0) else wd3)
    disc(cx, by - 135, 2, PAL['sukuna'][4])

    # Cráneo demoníaco cornudo en relieve 3D (cy = by - 54)
    scy = by - 54
    for dy in range(-15, 17):
        for dx in range(-14, 15):
            nx, ny = dx / 13.5, dy / 14.5
            in_skull = (nx * nx + ny * ny <= 1.0) if dy < 5 else (abs(dx) <= 8 - (dy - 5) // 3)
            if in_skull:
                n = math.sqrt(max(0.05, 1.0 - min(0.95, nx * nx + ny * ny)))
                lum = (-nx * 0.4 - ny * 0.4 + n * 0.7)
                l_eye1 = math.hypot(dx + 5, dy - 1) <= 2.7
                r_eye1 = math.hypot(dx - 5, dy - 1) <= 2.7
                l_eye2 = math.hypot(dx + 8, dy - 6) <= 2.0
                r_eye2 = math.hypot(dx - 8, dy - 6) <= 2.0
                nose = (abs(dx) <= 1 and 3 <= dy <= 6)
                teeth = (dy >= 11 and abs(dx) <= 6 and dx % 2 == 0)
                if l_eye1 or r_eye1 or l_eye2 or r_eye2 or nose:
                    col = '#120308'
                elif teeth:
                    col = bn2
                elif lum > 0.56:
                    col = bn3
                elif lum > 0.28:
                    col = bn0
                elif lum > 0.06:
                    col = bn1
                else:
                    col = bn2
                put(cx + dx, scy + dy, col)
                if (l_eye1 or r_eye1) and dx % 2 == 0 and abs(dy - 1) <= 1:
                    put(cx + dx, scy + dy, PAL['sukuna'][4])
    for side in (-1, 1):
        for k in range(15):
            hx = cx + side * (11 + k)
            hy = scy - 5 - int(k * 0.85 - (k * k) * 0.025)
            for t in range(-2, 3):
                if abs(t) <= max(0, 2 - k // 6):
                    put(hx, hy + t, bn1 if t > 0 else bn3)

    # Cráneos apilados + faroles rituales a los lados del altar
    for sx_b, sy_b in ((-50, by - 18), (-44, by - 23), (44, by - 18), (50, by - 23)):
        disc(cx + sx_b, sy_b, 3, bn1)
        disc(cx + sx_b - 1, sy_b - 1, 2, bn3)
        put(cx + sx_b - 1, sy_b, '#120308')
        put(cx + sx_b + 1, sy_b, '#120308')
    for fx, fy in ((cx - 56, by - 30), (cx + 56, by - 30)):
        put(fx, fy - 1, bn2)
        if ANIM:
            FAROLES.append([fx, fy, 7])
        else:
            glow(fx, fy, 7, PAL['sukuna'][4], 0.55)
            disc(fx, fy, 2, '#ffe4e6')


def dibuja_pasarela_ruinas():
    """Pasarela de escombros en la línea del horizonte y=274..280."""
    r0, r1, r2 = PAL['ruin']
    for x in range(195, 428):
        bump = int(2 * math.sin(x * 0.06))
        for y in range(275 + bump, HOR + 1):
            put(x, y, r1 if y == 275 + bump else (r0 if x % 3 else r2))
    # Cortes carmesí cerca de Sukuna
    for sx0, sy0, dx_s, dy_s in ((210, 275, 16, -4), (266, 276, 14, -4)):
        for k in range(12):
            put(sx0 + (dx_s * k) // 12, sy0 + (dy_s * k) // 12, PAL['sukuna'][4])


def dibuja_sukuna(cx, by):
    """Ryomen Sukuna encima de la pasarela (by=278)."""
    w0, s0, t0, pk, cr = PAL['sukuna']
    spr = [
        '..........PPPP..........',
        '........PPPPPPPP........',
        '.......PPPPPPPPPP.......',
        '......PPPPPPPPPPPP......',
        '......PPCCCCCCCCPP......',
        '......PPKCKKKKCKPP......',
        '......PPCCCCCCCCPP......',
        '.......PKCWWWWCKP.......',
        '.......KCCCCCCCCK.......',
        '......KWWWWKKWWWWK......',
        '.....KWWWWKTTKWWWWK.....',
        '....KKWWWKKTTKKWWWKK....',
        '...CRKWWWKKKKKKWWWKRC...',
        '...CCKWWWWWWWWWWWWKCC...',
        '....KKWWWWWWWWWWWWKK....',
        '.....KWWWWWWWWWWWWK.....',
        '.....KWWKKKKKKKKWWK.....',
        '.....KWWKSSSSSSKWWK.....',
        '.....KWWKKKKKKKKWWK.....',
        '....KWWWWKKKKKKKKWWK....',
        '....KWWWWK......KWWK....',
        '...KWWWWKK......KWWWK...',
        '...KWWWK.........KWWK...',
        '...KWWK...........KWWK..',
        '..KKKK.............KKKK.',
        '..KKKK.............KKKK.',
    ]
    cmap = {'P': pk, 'C': '#f4d2c4', 'K': '#120810', 'W': w0, 'S': s0, 'T': t0, 'R': cr}
    pinta_sprite(lz, cx, by, spr, cmap)
    if ANIM:
        RUNAS.append([cx + 12, by - 14])
    else:
        glow(cx + 12, by - 14, 7, cr, 0.50)


def dibuja_gojo(cx, by):
    """Satoru Gojo encima de la pasarela (by=278)."""
    b0, b1, h0, h1, ey = PAL['gojo']
    spr = [
        '........HHHHHHHH........',
        '......HHHHHHHHHHHH......',
        '.....HHHHHHHHHHHHHH.....',
        '....HHHHHHHHHHHHHHHH....',
        '.....HHHHCCCCCCCHHH.....',
        '.....HHHCCEECEECCHH.....',
        '......HHCCCCCCCCCH......',
        '.......KCCCCCCCCK.......',
        '......KKBBBBBBBBKK......',
        '...VVVKKBBBBBBBBKK......',
        '..VVRVKKBBBGGGBBKK......',
        '..VVVVBBBBBBBBBBBB......',
        '......BBBBBBBBBBBB......',
        '......BBBBBBBBBBBB......',
        '......BBBB1111BBBB......',
        '......BBBBBBBBBBBB......',
        '......BBBBBBBBBBBB......',
        '.....BBBBBB..BBBBBB.....',
        '.....BBBBBB..BBBBBB.....',
        '.....BBBBBB..BBBBBB.....',
        '.....BBBBBB..BBBBBB.....',
        '.....BBBBBB..BBBBBB.....',
        '....BBBBBB....BBBBBB....',
        '....BBBBBB....BBBBBB....',
        '...KKKKKK......KKKKKK...',
        '...KKKKKK......KKKKKK...',
    ]
    cmap = {'H': h0, 'C': '#f6d8cc', 'E': ey, 'K': '#0c0e18', 'B': b0, '1': b1, 'G': '#d4af37', 'V': '#a855f7', 'R': '#38bdf8'}
    pinta_sprite(lz, cx, by, spr, cmap)
    if ANIM:
        RUNAS.append([cx - 11, by - 17])
    else:
        glow(cx - 11, by - 17, 7, '#38bdf8', 0.50)


dibuja_vacio_infinito_esfera(452, 162)
dibuja_skyline_shinjuku()
dibuja_santuario_malevolente(156, HOR)
dibuja_pasarela_ruinas()
dibuja_sukuna(248, 278)
dibuja_gojo(378, 278)

# Esfera de choque Púrpura Vacío entre Sukuna y Gojo (cy=248 bien encima del horizonte)
if not ANIM:
    glow(313, 248, 24, '#9333ea', 0.65)
    glow(313, 248, 12, '#e879f9', 0.78)
    disc(313, 248, 5, '#fdf4ff')
    disc(294, 252, 3, '#fb7185')
    disc(332, 244, 3, '#38bdf8')
else:
    RUNAS.append([313, 248])

render_lago(lz, PAL['agua'], PAL['olas'], DESTELLOS, ANIM, mx=MX, hor=HOR, reflejo_cols=PAL['reflejo'])
aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
