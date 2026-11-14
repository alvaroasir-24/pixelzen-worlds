#!/usr/bin/env python3
"""PixelZen Worlds - Cyberpunk Edgerunners (Principal): Corpo Plaza · David Martinez & Lucy."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))
from pz_lib import (  # noqa: E402
    Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, exporta_salida, exporta_sprites_si_aplica, fbm, mix, pinta_sprite,
    render_cielo, render_estrellas, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1501)

PALETAS = {
    'noche': dict(
        sky=['#050410', '#0a081d', '#110d2c', '#1a133c', '#261a50', '#362264', '#4d2b78', '#68348a', '#8c3b8e', '#1a6884'],
        bldg1=('#0a0b1a', '#141730', '#05060f'),
        bldg2=('#120d26', '#1e163d', '#090614'),
        neon=['#22d3ee', '#f43f5e', '#facc15', '#4ade80', '#e879f9'],
        road=('#080914', '#101428', '#04050b', '#1c2444'),
        car=('#141c2c', '#24324d', '#080c14', '#ef4444', '#38bdf8'),
        david=('#facc15', '#ca8a04', '#1e293b', '#0f172a', '#22d3ee', '#4ade80'),
        lucy=('#f8fafc', '#cbd5e1', '#181826', '#22d3ee', '#f43f5e', '#fb7185'),
        vig=0.72,
        nube=['#221640', '#312058', '#422a70', '#583686', '#724498', '#181030'],
    ),
    'dorado': dict(
        sky=['#12081c', '#200f2c', '#34163c', '#4e1f4c', '#6e2a58', '#92385e', '#ba4c5c', '#df6c52', '#f6984e', '#fecb6e'],
        bldg1=('#161024', '#261a3c', '#0b0814'),
        bldg2=('#221430', '#342048', '#110a18'),
        neon=['#38bdf8', '#fb7185', '#fde047', '#34d399', '#f472b6'],
        road=('#120c1e', '#201634', '#080610', '#342450'),
        car=('#1c2234', '#2e3854', '#0c101a', '#f43f5e', '#38bdf8'),
        david=('#fde047', '#eab308', '#1e293b', '#0f172a', '#38bdf8', '#4ade80'),
        lucy=('#f8fafc', '#cbd5e1', '#1c192b', '#38bdf8', '#fb7185', '#fda4af'),
        vig=0.80,
        nube=['#441c42', '#602652', '#7e345e', '#a04664', '#c26068', '#2e1230'],
    ),
    'dia': dict(
        sky=['#162c58', '#224076', '#325894', '#4672b2', '#6090cc', '#80aee0', '#a4ccf0', '#c8e4fc', '#e2d8ee', '#f6c2da'],
        bldg1=('#222a44', '#344064', '#141828'),
        bldg2=('#2c2444', '#423664', '#1a1428'),
        neon=['#06b6d4', '#e11d48', '#eab308', '#10b981', '#c026d3'],
        road=('#1c243a', '#2c3856', '#101424', '#405078'),
        car=('#243048', '#384a6c', '#141a28', '#e11d48', '#06b6d4'),
        david=('#facc15', '#ca8a04', '#1e293b', '#0f172a', '#06b6d4', '#22c55e'),
        lucy=('#ffffff', '#cbd5e1', '#1e1b2e', '#06b6d4', '#e11d48', '#fb7185'),
        vig=0.88,
        nube=['#edeef8', '#dcdaf0', '#cbc6e4', '#f8f8fc', '#d8cce4', '#b4aec8'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#22d3ee', '#f43f5e'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#22d3ee', base='#f0f9ff', sombra='#bae6fd', crater='#7dd3fc', crater_hi='#a5f3fc'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#fda4af', centro='#fff8f0', borde='#f43f5e', rayo='#fecdd3'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS)
MX, MY, MR = 374, 58, 38
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#22d3ee', base='#f0f9ff', sombra='#bae6fd', crater='#7dd3fc', crater_hi='#a5f3fc')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 368, 118, 22, halo='#fda4af', centro='#fff8f0', borde='#f43f5e', rayo='#fecdd3')
    else:
        dibuja_sol_estandar(lz, 368, 66, 22, halo='#fde68a', centro='#ffffff', borde='#f59e0b', rayo='#fef08a')

NUBES_DEF = [
    (74, 42, 86, PAL['nube'][1], 2),
    (226, 36, 78, PAL['nube'][2], 2),
    (412, 48, 80, PAL['nube'][3], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# Polución luminosa cian-magenta en la base de las torres (lejos de zona HUD 478..632)
glow(185, 240, 120, '#9333ea', 0.24 if FASE != 'dia' else 0.12)
glow(325, 244, 105, '#06b6d4', 0.22 if FASE != 'dia' else 0.12)


def draw_megatower(x0, w, y_top, y_bot, col_t, neon_col, step_tier=False, beacon=False, kanji=False):
    c_dk, c_mid, c_sh = col_t
    for y in range(y_top, y_bot):
        w_cur = w
        x_cur = x0
        if step_tier and y < y_top + 26:
            trim = (y_top + 26 - y) // 4
            x_cur = x0 + trim
            w_cur = max(10, w - trim * 2)
        for x in range(x_cur, x_cur + w_cur):
            if 0 <= x < W:
                is_edge = x < x_cur + 2 or x >= x_cur + w_cur - 2
                col = c_sh if is_edge else (c_mid if x < x_cur + w_cur // 2 else c_dk)
                put(x, y, col)
    # Tiras verticales de neón en fachada
    for y in range(y_top + 8, y_bot - 6):
        if y % 3 != 0 and x0 + 4 < W:
            put(x0 + 4, y, neon_col)
        if x0 + w - 5 < W and (y % 8 < 5):
            over(x0 + w - 5, y, neon_col, 0.72)
    # Rejilla de ventanas iluminadas
    rng_b = random.Random(x0 * 37 + y_top)
    for vy in range(y_top + 14, y_bot - 12, 7):
        for vx in range(x0 + 9, x0 + w - 9, 6):
            if rng_b.random() < 0.42:
                vc = neon_col if rng_b.random() < 0.25 else ('#fde047' if rng_b.random() < 0.5 else '#67e8f9')
                for dy in range(3):
                    for dx in range(3):
                        over(vx + dx, vy + dy, vc, 0.75)
                if not ANIM and FASE != 'dia' and rng_b.random() < 0.22:
                    VENTANAS.append([vx, vy])
    # Cartel vertical kanji neón
    if kanji:
        kx = x0 + w // 2 - 4
        ky0 = y_top + 24
        for dy in range(34):
            for dx in range(9):
                put(kx + dx, ky0 + dy, '#0a0814')
        for r in range(3):
            gy = ky0 + 4 + r * 10
            for dx in range(2, 7):
                put(kx + dx, gy, neon_col)
                put(kx + dx, gy + 4, neon_col)
            for dy in range(7):
                put(kx + 4, gy + dy, neon_col)
        glow(kx + 4, ky0 + 17, 14, neon_col, 0.36 if FASE != 'dia' else 0.16)
    if beacon:
        bx = x0 + w // 2
        for dy in range(18):
            put(bx, y_top - dy, '#334155')
        put(bx, y_top - 18, '#fb7185')
        glow(bx, y_top - 18, 6, '#f43f5e', 0.45)


# Megatorres de Night City (manteniendo x>=478, y<=220 libre para el HUD)
draw_megatower(8, 52, 88, 258, PAL['bldg2'], '#22d3ee', step_tier=True, beacon=True, kanji=True)
draw_megatower(68, 44, 118, 258, PAL['bldg1'], '#f43f5e', kanji=False)
# Torre Arasaka principal con banda carmesí y logotipo rojo
draw_megatower(124, 72, 42, 258, PAL['bldg1'], '#f43f5e', step_tier=True, beacon=True, kanji=False)
for y in range(66, 98):
    for x in range(148, 174):
        put(x, y, '#0c050c')
    # Logotipo Arasaka pixel art estilizado (3 barras verticales con círculo arriba)
    if 72 <= y <= 78:
        for x in range(154, 168):
            if (x - 160) ** 2 + (y - 75) ** 2 <= 9:
                put(x, y, '#ef4444')
    if 80 <= y <= 94:
        for bx in (154, 160, 166):
            put(bx, y, '#ef4444')
            put(bx + 1, y, '#fb7185')
glow(160, 82, 22, '#ef4444', 0.40 if FASE != 'dia' else 0.18)

draw_megatower(206, 48, 110, 258, PAL['bldg2'], '#facc15', kanji=True)
draw_megatower(264, 58, 86, 258, PAL['bldg1'], '#e879f9', step_tier=True, beacon=True)
draw_megatower(334, 62, 102, 258, PAL['bldg2'], '#4ade80', kanji=True)
draw_megatower(406, 52, 128, 258, PAL['bldg1'], '#22d3ee', beacon=False)
# Siluetas bajas al extremo derecho por debajo de ZY1=215 para no estorbar el HUD
draw_megatower(470, 56, 222, 258, PAL['bldg1'], '#f43f5e', kanji=False)
draw_megatower(536, 98, 228, 258, PAL['bldg2'], '#22d3ee', kanji=False)

# AVs corporativos volando en el cielo nocturno
for avx, avy, col_av in ((92, 116, '#38bdf8'), (296, 134, '#fb7185')):
    for dx in range(-9, 10):
        put(avx + dx, avy, '#1e293b')
        if abs(dx) < 7:
            put(avx + dx, avy - 1, '#334155')
            put(avx + dx, avy + 1, '#0f172a')
    for kx in range(-4, 5):
        put(avx + kx, avy - 1, col_av)
    put(avx - 8, avy + 1, '#fb7185')
    put(avx + 8, avy + 1, '#22d3ee')
    glow(avx, avy + 1, 7, col_av, 0.35)


# Calle húmeda de Corpo Plaza en perspectiva (y=254..400)
cr_dk, cr_mid, cr_sh, cr_rim = PAL['road']
r_wet = Ruido(1509)
for y in range(254, H):
    t = (y - 254) / float(H - 254)
    for x in range(W):
        wet = fbm(r_wet, x * 0.045 + y * 0.14)
        base = cr_sh if wet < 0.38 else (cr_dk if wet < 0.62 else cr_mid)
        put(x, y, base)
        # Bordillo e iluminación lateral de acera
        if 254 <= y <= 261:
            put(x, y, cr_rim if y == 256 else '#161b30')
        # Líneas amarillas/cian discontinuas de la calzada en perspectiva
        lx_line = 316 + int((y - 254) * 0.36)
        if 272 <= y < 394 and abs(x - lx_line) <= 1 and ((y // 16) % 2 == 0):
            put(x, y, '#facc15')
        # Reflejos verticales de neón en charcos húmedos
        if wet > 0.56 and y > 268 and ((x + y) % 2 == 0):
            if 118 <= x <= 205:
                over(x, y, '#f43f5e', 0.30)
            elif 215 <= x <= 325:
                over(x, y, '#22d3ee', 0.28)
            elif 345 <= x <= 440:
                over(x, y, '#e879f9', 0.26)
            elif 45 <= x <= 115:
                over(x, y, '#facc15', 0.22)

# Pasos de cebra en perspectiva (x=238..395, y=268..288)
for stripe in range(7):
    sx = 236 + stripe * 24
    for dy in range(18):
        skew = int(dy * 0.45)
        for dx in range(10):
            over(sx + dx - skew, 268 + dy, '#94a3b8', 0.55)


# Quadra Turbo-R V-Tech aparcado a la izquierda (x=28..146, by=326)
def draw_quadra(x0, by):
    c_body, c_hi, c_sh, c_tail, c_glass = PAL['car']
    # Sombra bajo el chasis + neón underglow
    for dx in range(-4, 114):
        for dy in range(4):
            over(x0 + dx, by + dy, '#02040a', 0.72)
        if dx % 2 == 0:
            over(x0 + dx, by + 2, '#22d3ee', 0.65)
            over(x0 + dx, by + 5, '#06b6d4', 0.35)
    # Carrocería baja en cuña
    for dy in range(-18, 1):
        for dx in range(0, 108):
            if dy < -10 and (dx < 16 or dx > 86):
                continue
            if dy == -18 and (dx < 24 or dx > 72):
                continue
            if dy in (-17, -16) and (dx < 20 or dx > 78):
                continue
            col = c_hi if dy in (-16, -9) else (c_sh if dy > -4 else c_body)
            put(x0 + dx, by + dy, col)
    # Parabrisas y ventanilla inclinada
    for dy in range(-15, -10):
        for dx in range(26 + (-15 - dy), 68 - (-15 - dy)):
            put(x0 + dx, by + dy, c_glass)
    # Tira LED trasera roja Quadra (muy icónica)
    for dx in range(2, 16):
        put(x0 + dx, by - 7, '#ef4444')
        put(x0 + dx, by - 6, '#fda4af')
    glow(x0 + 9, by - 6, 10, '#ef4444', 0.52)
    # Faros frontales cian
    for dx in range(98, 107):
        put(x0 + dx, by - 7, '#a5f3fc')
    glow(x0 + 104, by - 7, 8, '#22d3ee', 0.45)
    # Ruedas con llanta iluminada
    for wx in (22, 86):
        for dy in range(-7, 4):
            for dx in range(-7, 8):
                d2 = dx * dx + (dy + 2) * (dy + 2)
                if d2 <= 44:
                    put(x0 + wx + dx, by + dy, '#05070e' if d2 > 14 else ('#22d3ee' if d2 > 6 else '#e2e8f0'))


draw_quadra(32, 326)


# ============================================================
# PERSONAJES PRINCIPALES (~46 filas): DAVID MARTINEZ & LUCY
# ============================================================
# David Martinez: 30 cols x 46 rows
SPR_DAVID = [
    '............hhhhhh............',
    '...........hhhhhhhh...........',
    '..........hhhhhhhhhh..........',
    '..........hhsssssshh..........',
    '..........hssssssssh..........',
    '..........hseessseeh..........',
    '..........hsssssssss..........',
    '...........sssmmmss...........',
    '...........KKssssKK...........',
    '..........KKbbbbbbKK..........',
    '.........KKYYYYYYYYKK.........',
    '........KKYYYYGGYYYYKK........',
    '........KYYYYGGGGYYYYK........',
    '.......KKYYYGGCCGGYYYKK.......',
    '.......KYYYYYGGGGYYYYYK.......',
    '......KKYYYYCCGGCCYYYYKK......',
    '......KYYYYYYCCCCYYYYYYK......',
    '......KYYYYYKKbbKKYYYYYK......',
    '.....KKYYYYYKKKKKKYYYYYKK.....',
    '.....KYYYYYYKKKKKKYYYYYYK.....',
    '.....KYYssYYKKKKKKYYssYYK.....',
    '.....KYYssYYKKKKKKYYssYYK.....',
    '......KKssKKKKKKKKKKssKK......',
    '.......KKK..KKKKKK..KKK.......',
    '...........KKKKKKKK...........',
    '..........KKKKKKKKKK..........',
    '.........KKKKK..KKKKK.........',
    '.........KKKK....KKKK.........',
    '........KKKKK....KKKKK........',
    '........KKKK......KKKK........',
    '.......KKKKK......KKKKK.......',
    '.......KKKK........KKKK.......',
    '.......KKKK........KKKK.......',
    '......KKKK..........KKKK......',
    '......KKKK..........KKKK......',
    '......KKKK..........KKKK......',
    '......BBBB..........BBBB......',
    '.....BBBBBB........BBBBBB.....',
    '.....BBBBBB........BBBBBB.....',
]
d_y0, d_y1, d_b1, d_b2, d_c1, d_c2 = PAL['david']
CMAP_DAVID = {
    'h': '#451a03',
    's': '#f5cba7',
    'e': '#1e293b',
    'm': '#c27d58',
    'K': d_b2,
    'b': d_b1,
    'Y': d_y0,
    'y': d_y1,
    'G': d_y1,
    'C': d_c1,
    'B': '#0f172a',
}

# 3 estelas cromáticas del Sandevistan detrás de David (verde -> cian -> magenta)
for idx_s, (sx_off, s_col, s_alp) in enumerate([(-48, '#4ade80', 0.34), (-32, '#22d3ee', 0.48), (-16, '#f43f5e', 0.62)]):
    cmap_ghost = {k: s_col for k in CMAP_DAVID}
    # Estela simplificada con alpha sobre el fondo
    h_sp = len(SPR_DAVID)
    w_sp = len(SPR_DAVID[0])
    for ry, row in enumerate(SPR_DAVID):
        py = 348 - h_sp + 1 + ry
        for rx, ch in enumerate(row):
            if ch != '.':
                px = (228 + sx_off) - w_sp // 2 + rx
                over(px, py, s_col, s_alp)
    # Línea cromática de velocidad horizontal desde la columna vertebral
    for ly in (314, 318, 323):
        for lx in range(228 + sx_off - 10, 228):
            over(lx, ly, s_col, 0.35)

pinta_sprite(lz, 228, 348, SPR_DAVID, CMAP_DAVID)
# Detalles de la cruz verde/amarilla del cuello EMT + brillo Sandevistan
for dy in range(-1, 2):
    put(228 + dy, 319, '#4ade80')
    put(228, 319 + dy, '#4ade80')
glow(228, 322, 16, '#22d3ee', 0.42 if FASE != 'dia' else 0.20)


# Lucy (Lucyna Kushinada): 30 cols x 39 rows
SPR_LUCY = [
    '...........wwwwwww............',
    '..........wwwwwwwww...........',
    '.........wwwccccwwwm..........',
    '........wwwssssssssww.........',
    '........wwssrsrrrssww.........',
    '........wwsssssssssww.........',
    '.........wwsssmmssww..........',
    '..........w..ssss..w..........',
    '............KKKKKK............',
    '..........KKWWWWWWKK..........',
    '.........KKWWWWWWWWKK.........',
    '........KKWWKKKKKKKKWW........',
    '........KWKKWWWWWWWWKWK.......',
    '.......KKWKKWWWWWWWWKWKK......',
    '.......KWWKKKWWWWWWKKKWWK.....',
    '......ssWWKKKKWWWWKKKKWWss....',
    '.....ss.WKKKKKKWWKKKKKKW.ss...',
    '....ss...KKKKKKKKKKKKKK...ss..',
    '...rs.....KKKKKKKKKKKK........',
    '..........KKKKKKKKKKKK........',
    '..........KKKK....KKKK........',
    '..........KKK......KKK........',
    '.........KKKK......KKKK.......',
    '.........KKK........KKK.......',
    '........KKKK........KKKK......',
    '........KKKK........KKKK......',
    '........KKKK........KKKK......',
    '.......KKKKK........KKKKK.....',
    '.......KKKK..........KKKK.....',
    '.......KKKK..........KKKK.....',
    '.......KKKK..........KKKK.....',
    '......KKKK............KKKK....',
    '......KKKK............KKKK....',
    '......BBBB............BBBB....',
    '.....BBBBBB..........BBBBBB...',
]
l_w0, l_w1, l_dk, l_cy, l_rd, l_pk = PAL['lucy']
CMAP_LUCY = {
    'w': l_w0,
    'c': l_cy,
    'm': l_pk,
    's': '#fce7dc',
    'r': l_rd,
    'K': l_dk,
    'W': '#f1f5f9',
    'B': '#0f172a',
}
pinta_sprite(lz, 386, 348, SPR_LUCY, CMAP_LUCY)

# Monofilo incandescente desde la mano derecha de Lucy hasta x=292..368
for t_i in range(85):
    u = t_i / 84.0
    mx = int(371 - u * 86)
    my = int(328 - math.sin(u * math.pi * 1.35) * 26)
    put(mx, my, '#fde047' if t_i % 3 == 0 else '#fb7185')
    if t_i % 2 == 0:
        over(mx, my + 1, '#f43f5e', 0.65)
glow(328, 308, 14, '#fb7185', 0.36 if FASE != 'dia' else 0.16)

# Reflejos sutiles de ambos bajo los pies sobre el asfalto húmedo
for dy in range(1, 14):
    a_r = 0.24 * (1.0 - dy / 14.0)
    for dx in range(-8, 9):
        over(228 + dx, 348 + dy, '#facc15', a_r)
        over(386 + dx, 348 + dy, '#e2e8f0', a_r)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
