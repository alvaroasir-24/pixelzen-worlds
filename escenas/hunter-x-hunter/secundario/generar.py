#!/usr/bin/env python3
"""PixelZen Worlds - Hunter x Hunter (Monitor 2): Praderas de Greed Island y Torre de Eta/Elena."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    exporta_salida, exporta_sprites_si_aplica, fbm, mix, render_cielo,
    render_estrellas, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1711)

PALETAS = {
    'noche': dict(
        sky=['#060d1c', '#0b182c', '#12263f', '#1a3654', '#244868', '#305c7a', '#3d708a', '#4d849a', '#5e96a8', '#72a8b4'],
        mont=['#2b4c5a', '#1e3844', '#162b34'],
        grass_far='#2d5a3e',
        grass_mid='#214c30',
        grass_near='#183c24',
        grass_hi='#3b744c',
        grass_sh='#102818',
        dirt=('#484c38', '#343828', '#5c6048'),
        pond=('#386e82', '#649cb0'),
        roof_hi='#5c5e66',
        roof_mid='#3e4048',
        roof_lo='#24262e',
        roof_line='#181a20',
        bowl_hi='#6e3a3e',
        bowl_mid='#52282c',
        bowl_lo='#34181c',
        tile_g='#325838',
        tile_y='#786832',
        tile_o='#703c2a',
        tile_d='#1e2024',
        pillar=('#60646c', '#3c4048', '#22242a'),
        shadow='#091810',
        vig=0.80,
        nube=['#2b4a68', '#3a5d7c', '#4c7290', '#6088a2', '#789eb4', '#26425c'],
        nen=('#48f09c', '#b8ffe0'),
        ball=('#f49048', '#ffe49c'),
    ),
    'dorado': dict(
        sky=['#1e2e58', '#304470', '#485b86', '#686e96', '#908098', '#b8908e', '#da9e80', '#f4b476', '#ffcb80', '#ffe29c'],
        mont=['#6c768e', '#58607a', '#485068'],
        grass_far='#7ba468',
        grass_mid='#649448',
        grass_near='#4c7e34',
        grass_hi='#8eb864',
        grass_sh='#325624',
        dirt=('#a89a70', '#867854', '#c4b68a'),
        pond=('#8eb4c0', '#d8d6c8'),
        roof_hi='#a69c94',
        roof_mid='#7e746e',
        roof_lo='#544c48',
        roof_line='#383030',
        bowl_hi='#b8685c',
        bowl_mid='#8e463e',
        bowl_lo='#5e2a28',
        tile_g='#5c8444',
        tile_y='#cca446',
        tile_o='#bc6238',
        tile_d='#2e2824',
        pillar=('#9a9694', '#6e6a68', '#464242'),
        shadow='#1e3418',
        vig=0.88,
        nube=['#b8889a', '#daa094', '#f2b88e', '#ffd09c', '#ffe4b4', '#9e7488'],
        nen=('#60f8a8', '#dcffec'),
        ball=('#ff8438', '#ffe69a'),
    ),
    'dia': dict(
        sky=['#529cd4', '#68addd', '#80bee6', '#98ceee', '#aedcf4', '#c2e6f8', '#d4eefb', '#e2f4fc', '#edf8fe', '#f4fbff'],
        mont=['#8ab4c8', '#7ca6bc', '#729ab0'],
        grass_far='#8ac684',
        grass_mid='#6db852',
        grass_near='#54a238',
        grass_hi='#90d26c',
        grass_sh='#3a7a28',
        dirt=('#c2ba90', '#9ea278', '#ded6b0'),
        pond=('#a8d8ec', '#e8f6fc'),
        roof_hi='#aca8a2',
        roof_mid='#84807a',
        roof_lo='#5a5856',
        roof_line='#3e3c3a',
        bowl_hi='#b26260',
        bowl_mid='#8e4646',
        bowl_lo='#622c2e',
        tile_g='#608e4a',
        tile_y='#d0ac48',
        tile_o='#c0643a',
        tile_d='#2c2c2c',
        pillar=('#a6aaae', '#7a7e84', '#4e5258'),
        shadow='#22441e',
        vig=0.95,
        nube=['#ffffff', '#f6fbfe', '#ffffff', '#edf6fc', '#f8fdff', '#e4f2fa'],
        nen=('#48f09c', '#d8fff0'),
        ball=('#f6782e', '#ffe88e'),
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

# 1. Cielo alto de Greed Island + astro (horizonte alto alrededor de y ~ 118)
render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#48f09c', '#54b8ff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 44, halo='#7ee8d8', base='#f2fcf8', sombra='#c6e0dc', crater='#9ec0be', crater_hi='#b8d6d4'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 24, halo='#ffe498', centro='#fffef0', borde='#ffd05c', rayo='#ffe89c'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#d8fff0', '#bce8ff', '#98c8f0'])

MX, MY, MR = 365, 58, 34
NUBES_DEF = [
    (60, 26, 130, PAL['nube'][0], 2),
    (245, 36, 150, PAL['nube'][1], 2),
    (430, 22, 185, PAL['nube'][2], 3),
    (535, 52, 145, PAL['nube'][3], 3),
    (155, 64, 120, PAL['nube'][4], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 2. Suave cordillera azulada en el horizonte lejano (y ~ 102..120)
r_mont = Ruido(773)
for x in range(W):
    ridge_y = int(106 + 7 * fbm(r_mont, x * 0.012 + 3.1) - (3 if x > 420 else 0))
    for y in range(ridge_y, 124):
        t = (y - ridge_y) / max(1, 124 - ridge_y)
        put(x, y, mix(PAL['mont'][0], PAL['mont'][2], 0.35 + 0.45 * t))

# 3. Vastas praderas esmeralda y lima de Greed Island (y = 114..400, sin lago)
r_grass = Ruido(404)
r_patch = Ruido(819)
for y in range(114, H):
    t_y = (y - 114) / float(H - 114)
    if t_y < 0.32:
        col_base = mix(PAL['grass_far'], PAL['grass_mid'], t_y / 0.32)
    else:
        col_base = mix(PAL['grass_mid'], PAL['grass_near'], (t_y - 0.32) / 0.68)
    for x in range(W):
        horizon_wave = int(115 + 2.5 * math.sin(x * 0.015 + 0.6) + 2.0 * fbm(r_grass, x * 0.02))
        if y < horizon_wave:
            continue
        c = col_base
        # Suaves franjas onduladas de luz solar sobre la llanura
        band = math.sin(y * 0.065 + x * 0.004 + 1.8 * fbm(r_grass, x * 0.012 + y * 0.031))
        if band > 0.35:
            c = mix(c, PAL['grass_hi'], 0.22 * (band - 0.35))
        elif band < -0.45:
            c = mix(c, PAL['grass_sh'], 0.16 * (-band - 0.45))

        # Textura sutil de hierba y manchitas de tierra seca/guijarros en primer plano
        n_loc = fbm(r_patch, x * 0.055 + y * 0.143)
        if t_y > 0.12 and n_loc > 0.67:
            c = mix(c, PAL['dirt'][1], min(0.75, (n_loc - 0.67) * 2.2))
        elif (x * 13 + y * 29) % 41 == 0 and t_y > 0.10:
            c = mix(c, PAL['grass_sh'], 0.28)
        elif (x * 7 + y * 19) % 53 == 0 and t_y > 0.16:
            c = mix(c, PAL['grass_hi'], 0.25)

        # Neblina atmosferica junto al horizonte lejano
        if y < 146:
            c = mix(PAL['mont'][0], c, (y - 113) / 33.0)
        put(x, y, c)

# Dos diminutos estanques y arbolitos lejanos en el extremo izquierdo (fieles a la captura)
for px, py, pw in ((18, 162, 26), (10, 186, 36)):
    for dy in range(-2, 3):
        span = int(pw * math.sqrt(max(0.0, 1.0 - (dy / 2.6) ** 2)))
        for dx in range(-span, span + 1):
            put(px + dx, py + dy, PAL['pond'][1] if (abs(dx) < span * 0.55 and dy == 0) else PAL['pond'][0])

for tx, ty, tr in ((16, 146, 5), (27, 148, 4), (58, 152, 3)):
    for y in range(ty + tr - 1, ty + tr + 4):
        put(tx, y, PAL['grass_sh'])
    for dy in range(-tr, tr + 1):
        for dx in range(-tr, tr + 1):
            if dx * dx + dy * dy <= tr * tr:
                put(tx + dx, ty + dy, PAL['grass_sh'] if dy > 0 else PAL['grass_mid'])

# Pequeños guijarros claros salpicados por la llanura
for _ in range(42):
    px = random.randint(25, 395)
    py = random.randint(170, 388)
    rw = 1 + int((py - 160) / 110)
    for dx in range(-rw, rw + 1):
        put(px + dx, py, PAL['dirt'][2] if dx <= 0 else PAL['dirt'][0])
    if rw >= 2:
        put(px, py - 1, PAL['dirt'][2])

# 4. Sombra larga proyectada por la Torre de Eta/Elena hacia la esquina inferior derecha
shadow_poly_y = lambda x: (342 + (x - 420) * 0.34, 376 + (x - 420) * 0.42)
for x in range(408, W):
    y_min_line, y_max_line = shadow_poly_y(x)
    # Ancho extra bajo la torre principal y brazo de sombra de la torreta derecha
    cx_m = 472 + (x - 472) * 0.15
    y_top = int(max(340, 344 + max(0, x - 465) * 0.18))
    y_bot = int(min(H - 1, 368 + max(0, x - 418) * 0.48))
    for y in range(y_top, y_bot + 1):
        in_main = (y - 344) >= (x - 515) * 0.35 and (y - 352) <= (x - 406) * 0.52 and x >= 412
        in_wing = (535 <= x <= 628) and (354 + (x - 540) * 0.15 <= y <= 382 + (x - 540) * 0.25)
        if in_main or in_wing:
            edge = 0.68
            over(x, y, PAL['shadow'], edge)

# 5. Torre de Recepción de Eta y Elena en la derecha (cx = 472) + puente + torreta anexa (cx = 582)
def pinta_tambor_mosaico(x0, y0, w_d, h_d, rows=4, cols=7):
    cell_h = max(6, h_d // rows)
    cell_w = max(8, w_d // cols)
    for yy in range(y0, y0 + h_d):
        row = min(rows - 1, (yy - y0) // cell_h)
        ry = (yy - y0) - row * cell_h
        for xx in range(x0, x0 + w_d):
            col = min(cols - 1, (xx - x0) // cell_w)
            rx = (xx - x0) - col * cell_w
            u = (xx - x0) / max(1.0, w_d - 1.0)
            shade = max(0.0, (u - 0.42) * 1.1)
            # Borde de rejilla geométrica y diagonales tipo mosaico Greed Island
            diag1 = abs(rx / max(1.0, cell_w - 1.0) - ry / max(1.0, cell_h - 1.0)) < 0.11
            diag2 = abs((1.0 - rx / max(1.0, cell_w - 1.0)) - ry / max(1.0, cell_h - 1.0)) < 0.11
            if ry == 0 or rx == 0 or yy == y0 + h_d - 1 or xx == x0 + w_d - 1 or diag1 or diag2:
                base_c = PAL['tile_d']
            else:
                up_tri = (rx / max(1.0, cell_w - 1.0) + ry / max(1.0, cell_h - 1.0)) < 1.0
                up_tri2 = (rx / max(1.0, cell_w - 1.0) - ry / max(1.0, cell_h - 1.0)) > 0.0
                if up_tri and up_tri2:
                    base_c = PAL['tile_y'] if (row + col) % 2 == 0 else PAL['tile_o']
                elif (not up_tri) and (not up_tri2):
                    base_c = PAL['tile_o'] if (row + col) % 2 == 0 else PAL['tile_y']
                else:
                    base_c = PAL['tile_g']
            put(xx, yy, mix(base_c, PAL['tile_d'], min(0.62, shade)))

def pinta_cuenco_terracota(cx, y_top, y_bot, w_top, w_bot, ribs=12):
    for y in range(y_top, y_bot + 1):
        t = (y - y_top) / max(1.0, float(y_bot - y_top))
        # Perfil ligeramente acampanado hacia dentro
        curve = math.sin(t * math.pi * 0.5)
        hw = int(round((w_top * (1.0 - curve * 0.92) + w_bot * (curve * 0.92)) * 0.5))
        for x in range(cx - hw, cx + hw + 1):
            u = (x - (cx - hw)) / max(1.0, 2.0 * hw)
            if y in (y_top, y_bot):
                put(x, y, PAL['roof_line'])
            else:
                c = PAL['bowl_hi'] if u < 0.36 else (PAL['bowl_mid'] if u < 0.72 else PAL['bowl_lo'])
                if t > 0.78:
                    c = mix(c, PAL['bowl_lo'], 0.45)
                rib_pos = u * ribs
                if abs(rib_pos - round(rib_pos)) < 0.09:
                    c = mix(c, PAL['roof_line'], 0.65)
                put(x, y, c)

def pinta_tejado_conico(cx, y_apex, y_eave, hw_eave):
    for y in range(y_apex, y_eave + 1):
        t = (y - y_apex) / max(1.0, float(y_eave - y_apex))
        # Ligera campana elegante como en el diseño original
        hw = max(1, int(round(hw_eave * (t ** 0.90))))
        row_shingle = (y - y_apex) // 5
        for x in range(cx - hw, cx + hw + 1):
            u = (x - (cx - hw)) / max(1.0, 2.0 * hw)
            if y == y_eave or abs(x - cx) == hw:
                put(x, y, PAL['roof_line'])
                continue
            c = PAL['roof_hi'] if u < 0.38 else (PAL['roof_mid'] if u < 0.68 else PAL['roof_lo'])
            # Tejas escalonadas de pizarra
            shingle_x = ((x - cx) + (row_shingle % 2) * 3) % 6
            shingle_y = (y - y_apex) % 5
            if shingle_y == 4 or shingle_x == 0:
                c = mix(c, PAL['roof_line'], 0.48)
            elif shingle_y == 1 and ((x * 7 + y * 13) % 5 == 0):
                c = mix(c, PAL['roof_hi'], 0.35)
            put(x, y, c)

# Puente elevado y torreta derecha (dibujados antes del cuerpo principal para que queden bien encajados)
for y in range(214, 240):
    t = (y - 214) / 26.0
    for x in range(520, 566):
        c = PAL['tile_g'] if ((x // 6 + y // 6) % 2 == 0) else PAL['tile_y']
        if y in (214, 239) or y == 222:
            c = PAL['roof_line']
        put(x, y, mix(c, PAL['tile_d'], 0.25 + 0.35 * t))

# Torreta anexa derecha (cx = 582)
pinta_tambor_mosaico(562, 212, 40, 38, rows=3, cols=4)
pinta_cuenco_terracota(582, 198, 213, 52, 40, ribs=7)
pinta_tejado_conico(582, 134, 199, 28)

# Pilares y escalinata central de la torre principal (plantados sobre el césped en y = 356..362)
# Escalera interior bajo el tambor
for y in range(304, 356):
    t = (y - 304) / 52.0
    for x in range(456, 490):
        step = ((y - 304) % 5) == 0
        col = PAL['roof_line'] if (x < 462 or x > 484 or y < 312) else (PAL['pillar'][2] if step else PAL['pillar'][1])
        put(x, y, mix(col, PAL['shadow'], 0.35 * (1.0 - t)))

# 4 pilares gruesos de piedra
for px, pw, py_bot in ((426, 9, 356), (446, 8, 352), (492, 8, 353), (509, 9, 358)):
    for y in range(304, py_bot + 1):
        for x in range(px, px + pw):
            u = (x - px) / max(1.0, pw - 1.0)
            c = PAL['pillar'][0] if u < 0.40 else (PAL['pillar'][1] if u < 0.78 else PAL['pillar'][2])
            if y < 310:
                c = mix(c, PAL['shadow'], 0.55)
            put(x, y, c)
    # Matitas de hierba rodeando la base del pilar para integrarlo al suelo
    for dx in range(-3, pw + 3):
        if (dx * 3 + py_bot) % 2 == 0:
            put(px + dx, py_bot, PAL['grass_sh'])
            put(px + dx, py_bot - 1, PAL['grass_near'])

# Tambor de mosaico, cuenco terracota y gran tejado cónico principal
pinta_tambor_mosaico(420, 234, 104, 70, rows=4, cols=7)
pinta_cuenco_terracota(472, 196, 235, 146, 104, ribs=13)
pinta_tejado_conico(472, 64, 197, 84)
RUNAS.extend([(442, 250), (472, 266), (502, 250), (582, 226)])

# 6. GON y KILLUA jugando sobre la pradera (cx_gon = 205, cx_killua = 272, pie en y = 328)
def sombra_suelo(cx, by, rx=13, ry=3):
    for dy in range(-ry, ry + 1):
        for dx in range(-rx, rx + 1):
            if (dx / float(rx)) ** 2 + (dy / float(ry)) ** 2 <= 1.0:
                over(cx + dx, by + dy, PAL['shadow'], 0.55)

def dibuja_gon_jugando(cx, by):
    sombra_suelo(cx + 1, by, 13, 3)
    for (x, y) in ((-5, -1), (-4, -1), (-3, -1), (2, -1), (3, -1), (4, -1), (-4, -2), (3, -2)):
        put(cx + x, by + y, '#102418')
    for x in (-4, -3, 2, 3):
        for y in (-3, -4, -5):
            put(cx + x, by + y, '#dfb494')
    for dy in range(-10, -5):
        for dx in range(-5, 6):
            if abs(dx) < 5 or dy > -9:
                put(cx + dx, by + dy, '#1e7844' if dx <= 0 else '#145832')
    for dy in range(-21, -10):
        for dx in range(-5, 6):
            if abs(dx) == 5 and dy == -21:
                continue
            put(cx + dx, by + dy, '#249450' if dx < 1 else '#186c3a')
    for dy in (-21, -20, -16, -15):
        for dx in range(-4, 5):
            put(cx + dx, by + dy, '#f05a30')
    for k in range(1, 10):
        put(cx + 5 + k // 2, by - 19 - k, '#f2c8a4')
        put(cx + 4 + k // 2, by - 19 - k, '#249450' if k < 4 else '#f2c8a4')
    for k in range(1, 7):
        put(cx - 5 - k // 2, by - 17 + k // 2, '#f2c8a4')
    for dy in range(-31, -21):
        hw = 5 if dy > -29 else 4
        for dx in range(-hw, hw + 1):
            put(cx + dx, by + dy, '#f4c8a6')
    put(cx - 2, by - 26, '#14181e')
    put(cx + 2, by - 26, '#14181e')
    put(cx - 1, by - 23, '#a04e3c'); put(cx, by - 23, '#a04e3c'); put(cx + 1, by - 23, '#a04e3c')
    for dy in range(-40, -29):
        hw = 6 if dy < -32 else 7
        for dx in range(-hw, hw + 1):
            if dy < -36 and abs(dx) in (1, 4):
                continue
            if dy >= -32 and abs(dx) < 5:
                continue
            put(cx + dx, by + dy, '#0d2218' if (dx + dy) % 3 else '#1e5838')
    for sx in (-5, -2, 0, 2, 5):
        put(cx + sx, by - 41, '#123624')
        put(cx + sx, by - 42, '#0d2218')

def dibuja_killua_jugando(cx, by):
    sombra_suelo(cx, by + 1, 14, 3)
    for dx in range(-8, 9):
        put(cx + dx, by - 1, '#5844b4' if abs(dx) < 6 else '#e4b848')
    for (x, y) in ((-5, -3), (-4, -3), (-3, -3), (2, -3), (3, -3), (4, -3), (-4, -4), (3, -4)):
        put(cx + x, by + y, '#283878' if abs(x) != 3 else '#f4f6fc')
    for x in (-4, -3, 2, 3):
        for y in (-5, -6, -7):
            put(cx + x, by + y, '#f4d8c8')
    for dy in range(-12, -7):
        for dx in range(-5, 6):
            put(cx + dx, by + dy, '#4a527c' if dx <= 0 else '#363c62')
    for dy in range(-23, -12):
        for dx in range(-5, 6):
            c = '#eef2fa' if (dy < -16 or abs(dx) < 4) else '#d0d8ea'
            if abs(dx) <= 2 and dy < -18:
                c = '#38468c'
            put(cx + dx, by + dy, c)
    for k in range(1, 9):
        put(cx - 5 - k // 2, by - 21 - k // 2, '#f6dacc')
        put(cx + 5 + k // 2, by - 20 + k // 3, '#f6dacc')
    for dy in range(-33, -23):
        hw = 5 if dy > -31 else 4
        for dx in range(-hw, hw + 1):
            put(cx + dx, by + dy, '#f6dacc')
    put(cx - 2, by - 28, '#2864b8'); put(cx + 2, by - 28, '#2864b8')
    for dy in range(-41, -31):
        hw = 7 if dy > -39 else 5
        for dx in range(-hw, hw + 1):
            if dy >= -34 and abs(dx) < 5:
                continue
            if dy < -38 and abs(dx) in (2, 5):
                continue
            put(cx + dx, by + dy, '#e4ecf6' if (dx < 2) else '#c2cce0')
    for sx, sy in ((-6, -35), (-4, -42), (-1, -43), (3, -42), (6, -36)):
        put(cx + sx, by + sy, '#f4f8ff')

dibuja_gon_jugando(208, 326)
dibuja_killua_jugando(274, 326)

# Pelota luminosa de Nen en el aire entre Gon y Killua
bx, by_ball = 240, 290
glow(bx, by_ball, 13, PAL['nen'][0], 0.34)
disc(bx, by_ball, 4, PAL['ball'][0])
disc(bx - 1, by_ball - 1, 2, PAL['ball'][1])
RUNAS.extend([(bx, by_ball), (bx - 5, by_ball + 2), (bx + 5, by_ball - 2)])

aplica_vineta(lz, PAL['vig'])
out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=None, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
