#!/usr/bin/env python3
"""PixelZen Worlds - Demon Slayer (Monitor Principal): Tren Infinito, Rengoku vs Akaza."""
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
random.seed(1101)

PALETAS = {
    'noche': dict(
        sky=['#040614', '#080c22', '#101634', '#182248', '#22305c', '#2e3e72', '#3c4e86', '#4c6098', '#5e72aa', '#7286ba'],
        mont=('#182036', '#101628', '#0a0d18'),
        pine=('#0c141c', '#14222c', '#070c12'),
        ground=('#151a1e', '#1e2628', '#0c1014', '#2a3030'),
        train=('#12131c', '#222432', '#34384a', '#522026', '#ffd278'),
        flame=('#ff3624', '#ff7e24', '#ffd84c', '#fff6b8'),
        akaza=('#38d8ff', '#92f0ff', '#d8385c'),
        shad_core='#07060d',
        shad_rim='#4a3e6c',
        vig=0.72,
        nube=['#222c4e', '#303e66', '#40507c', '#506290', '#6274a2', '#1c2442'],
    ),
    'dorado': dict(
        sky=['#140a24', '#241236', '#3c1846', '#5e2250', '#843050', '#aa404a', '#ce5846', '#ea7846', '#fa9e54', '#ffc676'],
        mont=('#342038', '#241428', '#140b18'),
        pine=('#161420', '#241e2e', '#0c0a12'),
        ground=('#261c1e', '#362828', '#140e10', '#4a3836'),
        train=('#18141e', '#2c2432', '#42364a', '#6e242a', '#ffe088'),
        flame=('#ff3c24', '#ff8828', '#ffe052', '#fff8c4'),
        akaza=('#48e0ff', '#a8f4ff', '#e84068'),
        shad_core='#09070e',
        shad_rim='#6a4674',
        vig=0.80,
        nube=['#5c2e4e', '#7e3c5c', '#a44e64', '#ca6664', '#ea8864', '#482442'],
    ),
    'dia': dict(
        sky=['#1e4890', '#2e5ea6', '#4276bc', '#5a90d0', '#76aae0', '#94c2ea', '#b2d6f0', '#cee6f4', '#e4eff2', '#f2f4e8'],
        mont=('#445674', '#34445e', '#263248'),
        pine=('#1b3228', '#284a38', '#102018'),
        ground=('#283c26', '#385432', '#182418', '#4c6a42'),
        train=('#1a1c26', '#2e3240', '#444a5c', '#74282e', '#ffdc78'),
        flame=('#ff4228', '#ff8c2c', '#ffe258', '#fff8c8'),
        akaza=('#38d8ff', '#98f2ff', '#d8385c'),
        shad_core='#090810',
        shad_rim='#48567c',
        vig=0.90,
        nube=['#ffffff', '#eef4fa', '#dce8f4', '#f6fafd', '#e4eef8', '#c8d8ec'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#ff7a38', '#44d4ff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 42, halo='#ffdca8', base='#fffbf0', sombra='#d8d2be', crater='#b8b29e', crater_hi='#ccc6b2'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe298', centro='#fffef2', borde='#ffbe54', rayo='#ffe090'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffe4c8', '#b8e8ff', '#b2a8e8'])

MX, MY, MR = 326, 68, 40
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#ffdca8', base='#fffbf0', sombra='#d8d2be', crater='#b8b29e', crater_hi='#ccc6b2')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 360, 152, 22, halo='#ff9868', centro='#ffecd8', borde='#ff6042', rayo='#ff8058')
    else:
        dibuja_sol_estandar(lz, 310, 74, 22, halo='#ffe298', centro='#fffef2', borde='#ffbe54', rayo='#ffe090')

NUBES_DEF = [
    (92, 28, 165, PAL['nube'][0], 3),
    (256, 42, 150, PAL['nube'][1], 2),
    (418, 24, 140, PAL['nube'][2], 2),
    (168, 104, 175, PAL['nube'][3], 3),
    (380, 118, 135, PAL['nube'][4], 2),
    (536, 196, 110, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 1. Montanas y bosques oscuros tras el claro (bajando suavemente en x>430 para HUD)
rm = Ruido(1107)
M0, M1, M2 = PAL['mont']
for x in range(W):
    ramp = max(0.0, min(1.0, (x - 420) / 80.0))
    dip_h = int(24 * (0.5 - 0.5 * math.cos(math.pi * ramp)))
    ridge = int(170 + 24 * fbm(rm, x * 0.014) + dip_h)
    ridge = min(236, ridge)
    for y in range(ridge, 246):
        t = (y - ridge) / max(1, (246 - ridge))
        put(x, y, mix(M0, M2, min(1.0, t)))

P0, P1, P2 = PAL['pine']


def pino(px, by, h):
    for i in range(h):
        y = by - h + i
        hw = max(0, int(i * 0.28) - (2 if i % 5 == 4 else 0))
        for dx in range(-hw, hw + 1):
            put(px + dx, y, P1 if dx < 0 else (P0 if dx < hw // 2 else P2))


for px_t, py_t, ph_t in ((14, 246, 62), (42, 242, 54), (76, 244, 48), (242, 242, 46), (272, 244, 52), (496, 244, 42), (534, 246, 50), (576, 244, 54), (614, 246, 60)):
    pino(px_t, py_t, ph_t)

# Traviesas de madera y doble riel del Tren Infinito con balasto de grava (x=0..640)
def rail_y(rx):
    curve = max(0.0, rx - 250) * 0.012
    return int(288 + 3 * math.sin(rx * 0.012) - curve)


# 2. Pradera del claro del Tren Infinito con ruido 2D organico (y = 238..400)
rx_g = Ruido(1123)
ry_g = Ruido(1151)
G0, G1, G2, G3 = PAL['ground']
for y in range(238, H):
    for x in range(W):
        n2 = 0.5 * fbm(rx_g, x * 0.036) + 0.5 * fbm(ry_g, y * 0.048 + 7.0) + 0.14 * math.sin(x * 0.06) * math.cos(y * 0.07)
        c = G3 if n2 > 0.64 else (G1 if n2 > 0.48 else (G0 if n2 > 0.34 else G2))
        dy_rail = y - rail_y(x)
        if -5 <= dy_rail <= 6:
            # Terraplen de grava triturada bajo la via
            edge_dist = max(0.0, abs(dy_rail - 0.5) - 3.0)
            if edge_dist == 0.0 or dith(x, y, 0.85 - edge_dist * 0.25):
                gravel_h = (((x * 374761393 + y * 668265263) ^ (x * y)) & 255) / 255.0
                c = '#525660' if gravel_h > 0.72 else ('#3c3f48' if gravel_h > 0.36 else '#2a2c34')
        put(x, y, c)

# Traviesas de madera en perspectiva con inclinacion y placas de sujecion
for tx in range(6, W, 10):
    ty = rail_y(tx)
    for dy in range(-3, 4):
        sx = tx + dy // 2
        wood = '#4a3225' if dy < 0 else ('#342219' if dy < 2 else '#1c120d')
        for dx in range(-1, 3):
            put(sx + dx, ty + dy, wood)
    # Clavos / placas metalicas en el cruce con ambos rieles
    put(tx - 1, ty - 2, '#2d323e')
    put(tx + 1, ty + 1, '#2d323e')

# Doble riel paralelo (riel lejano y riel cercano con brillo metalico)
for x in range(W):
    ry_rail = rail_y(x)
    put(x, ry_rail - 3, '#444b5c')
    put(x, ry_rail - 2, '#7d889e' if (x % 7) else '#96a2b8')
    put(x, ry_rail + 1, '#b0bad0' if (x % 5) else '#8e98ae')
    put(x, ry_rail + 2, '#4a5264')
    put(x, ry_rail + 3, '#202430')

# 3. TREN INFINITO (locomotora a vapor + 2 vagones iluminados anclados sobre la via x=0..236)
TR_DK, TR_MD, TR_HI, TR_R, TR_GL = PAL['train']

# Enganches entre vagones y locomotora
for cx_link in range(55, 62):
    ly_k = rail_y(cx_link) - 10
    put(cx_link, ly_k, TR_DK)
    put(cx_link, ly_k + 1, TR_HI)
for cx_link in range(127, 134):
    ly_k = rail_y(cx_link) - 10
    put(cx_link, ly_k, TR_DK)
    put(cx_link, ly_k + 1, TR_HI)

# Vagon trasero y central apoyados sobre los rieles
for vx0, vx1, tilt_v in ((0, 56, 0.02), (60, 128, 0.03)):
    for x in range(vx0, vx1):
        drop = int((x - vx0) * tilt_v)
        top_v = 226 + drop
        bot_v = rail_y(x) - 6
        for y in range(top_v, bot_v + 1):
            if y < top_v + 4 or y == top_v + 8:
                c = TR_HI
            elif y > bot_v - 4:
                c = TR_DK
            else:
                c = TR_HI if (x - vx0) % 16 == 0 else TR_MD
            put(x, y, c)
        # Ventanas iluminadas del vagon
        if (x - vx0) % 16 in range(4, 11):
            for wy in range(top_v + 12, top_v + 24):
                put(x, wy, TR_GL if FASE != 'dia' else '#5e7ea8')
                if ANIM and x % 16 == 6 and wy == top_v + 16:
                    VENTANAS.append([x, wy])
    # Ruedas apoyadas exactamente sobre el riel cercano (ry+1)
    for wx in (vx0 + 14, vx1 - 14):
        wy = rail_y(wx) - 4
        disc(wx, wy, 5, TR_DK)
        disc(wx, wy, 2, TR_HI)

# Locomotora del Tren Infinito (x=132..224, apoyada firmemente sobre las vias)
for x in range(132, 224):
    drop = int((x - 132) * 0.06)
    is_cab = x < 164
    top_l = (212 if is_cab else 222) + drop
    bot_l = rail_y(x) - 6
    for y in range(top_l, bot_l + 1):
        if y < top_l + 4:
            c = TR_HI
        elif is_cab and 140 <= x <= 156 and top_l + 8 <= y <= top_l + 20:
            c = TR_GL
        elif not is_cab and top_l + 13 <= y <= top_l + 17:
            c = TR_R  # franja carmesi caldera
        elif y > bot_l - 6:
            c = TR_DK
        else:
            c = TR_MD if x < 210 else TR_HI
        put(x, y, c)
# Chimenea de la locomotora (x=202)
for y in range(202, 230):
    hw_c = 5 if y < 208 else 3
    for dx in range(-hw_c, hw_c + 1):
        put(202 + dx, y, TR_HI if dx < 0 else TR_DK)
CHIMENEA = [202, 201]
# Deflector delantero (quitanieves) rozando la via (x=222..238)
rail_front = rail_y(228)
for y in range(rail_front - 22, rail_front + 2):
    hw_f = (y - (rail_front - 22)) // 2 + 2
    for dx in range(0, hw_f + 1):
        put(222 + dx, y, TR_HI if dx < 3 else TR_DK)
# Ruedas motrices grandes de la locomotora apoyadas sobre el riel
for wx, wr in ((148, 7), (174, 9), (198, 9), (216, 6)):
    wy = rail_y(wx) - wr + 1
    disc(wx, wy, wr, TR_DK)
    disc(wx, wy, max(2, wr - 3), TR_HI)
    disc(wx, wy, 2, TR_R)
# Faro frontal de la locomotora
if ANIM:
    FAROLES.append([225, 238, 12])
else:
    glow(225, 238, 12, TR_GL, 0.72)
put(224, 238, '#fff6c8')
put(225, 238, '#fff6c8')

# Humo suave y abombado en estatico
if not ANIM:
    smoke_c = '#262b3b' if FASE == 'noche' else '#687082'
    smoke_hi = '#3a4056' if FASE == 'noche' else '#8e96aa'
    for k in range(11):
        sx_s = 200 - k * 8 + int(math.sin(k * 0.9) * 3)
        sy_s = 196 - k * 3 - int(k ** 1.15 * 0.4)
        rr_s = 3 + min(6, k // 2)
        disc(sx_s, sy_s, rr_s, smoke_c)
        disc(sx_s - 1, sy_s - 1, max(1, rr_s - 2), smoke_hi)


# 4. DUELO ICONICO: KYOJURO RENGOKU vs AKAZA (personajes detallados, cx=334 y cx=456, suelo y=310..312)
def dibuja_rengoku(cx, by):
    F0, F1, F2, F3 = PAL['flame']
    skin = '#ecc09c' if FASE != 'noche' else '#cfa68d'
    skin_sh = '#be8d6c' if FASE != 'noche' else '#9c7564'
    unif = '#161826'
    unif_hi = '#2c3048'
    belt = '#e4e8f0'
    haori_w = '#f4efe2' if FASE != 'noche' else '#d4d0c8'
    haori_sh = '#c6c0b2' if FASE != 'noche' else '#9ea0ae'

    # Sombra en tierra
    for dx in range(-22, 23):
        for dy in range(-2, 4):
            if (dx / 22.0) ** 2 + (dy / 3.2) ** 2 <= 1.0:
                over(cx + dx, by + dy, '#05040a', 0.72)

    # Haori de llamas ondeando desde los hombros (by-21) hacia atras
    for t_c in range(24):
        cx_w = cx - 4 - t_c
        ty_w = by - 21 + int(t_c * 0.14 + math.sin(t_c * 0.26) * 1.2)
        bh_w = max(6, 17 - t_c // 3) + (2 if t_c % 4 == 0 else 0)
        for dy in range(bh_w):
            if dy < bh_w - 7:
                col_c = haori_w if dy < 3 else haori_sh
            elif dy < bh_w - 4:
                col_c = F2
            elif dy < bh_w - 2:
                col_c = F1
            else:
                col_c = F0
            put(cx_w, ty_w + dy, col_c)

    # Sprite pixel-art detallado de Kyojuro Rengoku (31 filas: by-30..by)
    spr = [
        '........RRYYYYYRR.........',
        '.......RRYYYYYYYRR........',
        '......RYYYYYYYYYYYR.......',
        '......RYYYSSSSSSYYR.......',
        '.......YYSSSEESSSY........',
        '.......YYSSSSSSSSY........',
        '........YSSSHHSSY.........',
        '........UUUUUUUU..........',
        '.....WWUUUUUUUUUU.........',
        '....WWWUUGUUUUGUUU........',
        '...WWWWUUUUUUUUUUUU.......',
        '..WWWWUUUUUUGUUUUUUU......',
        '..WWW..UUUUUUUUUSSSS......',
        '.WWW...UUUUUBBBBB.........',
        '.FF....UUUUUUUUUU.........',
        '.......UUUUUUUUUU.........',
        '.......UUUUUUUUUU.........',
        '......UUUUU..UUUUU........',
        '......UUUU....UUUU........',
        '.....UUUU......UUUU.......',
        '.....UUU........UUU.......',
        '....UUU..........UUU......',
        '....KKK..........KKK......',
        '...KKKK..........KKKK.....',
        '...KRK............KRK.....',
        '...KKK............KKK.....',
        '...KKK............KKK.....',
        '..bbbb............bbbb....',
        '..bbbb............bbbb....',
        '.bbbbbb..........bbbbbb...',
        '..........................',
    ]
    cmap = {
        'Y': F2,
        'R': F0,
        'S': skin,
        'H': skin_sh,
        'E': '#c82a1c',
        'U': unif,
        'G': '#e8c454',
        'B': belt,
        'W': haori_w,
        'F': F1,
        'K': '#ececf4',
        'b': '#1a1822',
    }
    pinta_sprite(lz, cx, by, spr, cmap)
    # Puntas dorsales del cabello llameante
    for sx_h in (-5, -2, 1, 4):
        put(cx + sx_h, by - 31, F0)

    # Tsuba dorada de llama y hoja de katana Nichirin carmesi extendida al frente
    put(cx + 7, by - 19, F2)
    put(cx + 7, by - 18, F2)
    put(cx + 7, by - 17, F2)
    for s in range(22):
        put(cx + 8 + s, by - 18 - s // 4, F3 if s > 15 else F1)
        put(cx + 8 + s, by - 17 - s // 4, F0)

    # Novena Postura: Rengoku! Dragon de fuego brotando de su espada hacia el choque con Akaza
    for step in range(60):
        u = step / 59.0
        bx_f = int(cx + 22 + u * 64)
        by_f = int(by - 22 - math.sin(u * math.pi * 0.85) * 18 + math.sin(u * 8.5) * 3.0)
        r_f = 5 if 0.22 < u < 0.80 else (4 if u < 0.92 else 5)
        for dy in range(-r_f, r_f + 1):
            for dx in range(-r_f, r_f + 1):
                if dx * dx + dy * dy <= r_f * r_f:
                    d_norm = math.hypot(dx, dy) / max(1, r_f)
                    c_fl = F3 if d_norm < 0.36 else (F2 if d_norm < 0.66 else (F1 if u < 0.86 else F0))
                    put(bx_f + dx, by_f + dy, c_fl)
        if step % 10 == 0:
            if ANIM:
                FAROLES.append([bx_f, by_f, 11])
                RUNAS.append([bx_f, by_f])
            else:
                glow(bx_f, by_f, 8, F1, 0.50)
    # Fauces del dragon de llamas en la punta del ataque
    for dx_d, dy_d, cd in ((88, -26, F3), (90, -28, F2), (91, -29, F0), (88, -20, F2), (90, -19, F0)):
        put(cx + dx_d, by + dy_d, cd)


def dibuja_akaza(cx, by):
    AK_CY, AK_HI, AK_HR = PAL['akaza']
    skin = '#e2e6f0' if FASE != 'noche' else '#bcc4d8'
    skin_sh = '#9ea8be' if FASE != 'noche' else '#76809c'
    vest = '#9e2046'
    vest_dk = '#5e1028'
    pants = '#e8ecf4' if FASE != 'noche' else '#bcc4d6'
    pants_sh = '#9ca6bc' if FASE != 'noche' else '#78829a'

    # Tecnica de Despliegue: Brujula Destructiva (copo luminoso cian bajo sus pies)
    for dy in range(-8, 9):
        for dx in range(-42, 43):
            d = math.hypot(dx / 41.0, dy / 7.5)
            ang = math.atan2(dy / 7.5, dx / 41.0)
            rayo = abs(math.cos(ang * 6.0))
            if 0.86 <= d <= 1.0 or (0.32 <= d < 0.96 and rayo > 0.90):
                put(cx + dx, by + dy, AK_HI if d < 0.55 else AK_CY)
    for rx_c in (-32, -18, 0, 18, 32):
        if ANIM:
            RUNAS.append([cx + rx_c, by])
        else:
            glow(cx + rx_c, by, 5, AK_CY, 0.55)

    # Sprite pixel-art detallado de Akaza en postura Soryu mirando a la izquierda (31 filas: by-30..by)
    spr = [
        '........R.R.R.R.R.........',
        '.......RRRRRRRRRRR........',
        '.......RRRRRRRRRRR........',
        '.......RRSSSSSSSRR........',
        '........SSEESSSES.........',
        '........SSSTTTTSS.........',
        '.........SSSHHSS..........',
        '.......VVSSSSSSSSV........',
        '......VVVSSTTTTSSVV.......',
        '....SSVVVSSSTTSSSVVVS.....',
        '...SSSVVVSSSTTSSSVVVSS....',
        '..SSSTTVVSSSTTSSSVVTSSS...',
        '..SSS..VVSSSSSSSSV..SSS...',
        '........VSSSSSSSSV........',
        '........SSSTTTTSSS........',
        '.......PPPPPPPPPPP........',
        '......PPPPPPPPPPPPP.......',
        '......PPPPPP.PPPPPP.......',
        '.....PPPPPP...PPPPPP......',
        '.....PPPPP.....PPPPP......',
        '....PPPPP.......PPPPP.....',
        '....pppp.........pppp.....',
        '...pppp...........pppp....',
        '...SSS.............SSS....',
        '...RRR.............RRR....',
        '...SSS.............SSS....',
        '..SSSS.............SSSS...',
        '..........................',
        '..........................',
        '..........................',
        '..........................',
    ]
    # Reajustar patas hasta by-1 (ultimas filas)
    spr = [
        '........R.R.R.R.R.........',
        '.......RRRRRRRRRRR........',
        '.......RRRRRRRRRRR........',
        '.......RRSSSSSSSRR........',
        '........SSEESSSES.........',
        '........SSTSSSSTS.........',
        '.........SSSHHSS..........',
        '.......VVSSSSSSSSV........',
        '......VVVSSTTTTSSVV.......',
        '....SSVVVSSSTTSSSVVVS.....',
        '...SSSVVVSSSTTSSSVVVSS....',
        '..SSSTTVVSSSTTSSSVVTSSS...',
        '..SSS..VVSSSSSSSSV..SSS...',
        '........VSSSSSSSSV........',
        '........SSSTTTTSSS........',
        '.......PPPPPPPPPPP........',
        '......PPPPPPPPPPPPP.......',
        '......PPPPPP.PPPPPP.......',
        '.....PPPPPP...PPPPPP......',
        '.....PPPPP.....PPPPP......',
        '....PPPPP.......PPPPP.....',
        '....PPPPP.......PPPPP.....',
        '...ppppp.........ppppp....',
        '...ppppp.........ppppp....',
        '...SSSS...........SSSS....',
        '...RRRR...........RRRR....',
        '...SSSS...........SSSS....',
        '...SSSS...........SSSS....',
        '..SSSSS...........SSSSS...',
        '..SSSSS...........SSSSS...',
        '..........................',
    ]
    cmap = {
        'R': AK_HR,
        'S': skin,
        'H': skin_sh,
        'E': '#ffd84c',
        'T': '#288ad8',
        'V': vest,
        'P': pants,
        'p': pants_sh,
    }
    pinta_sprite(lz, cx, by, spr, cmap)
    # Sombra interior en el chaleco de Akaza y marcas Soryu brillantes en brazos/pecho
    for mx_s, my_s in ((-9, -19), (-7, -18), (-1, -21), (2, -19), (8, -19)):
        put(cx + mx_s, by + my_s, AK_CY)
    for vx_s in (-6, 5):
        put(cx + vx_s, by - 22, vest_dk)
        put(cx + vx_s, by - 20, vest_dk)

    # Onda de choque de Aire Destructivo desde su puno adelantado (x ~ 420, y ~ by-21)
    if ANIM:
        RUNAS.append([cx - 32, by - 23])
        FAROLES.append([cx - 30, by - 23, 14])
    else:
        glow(cx - 30, by - 23, 12, AK_CY, 0.70)
    for r_i in range(-5, 6):
        put(cx - 30 + abs(r_i) // 2, by - 23 + r_i, AK_HI if abs(r_i) < 3 else AK_CY)
    for dx_o, dy_o in ((-26, -23), (-24, -23), (-33, -25), (-33, -21)):
        put(cx + dx_o, by + dy_o, AK_HI)


dibuja_rengoku(334, 310)
dibuja_akaza(456, 312)

# Llamas y brasas en el claro por la batalla
for fx, fy in ((282, 314), (312, 320), (496, 318)):
    if ANIM:
        RUNAS.append([fx, fy])
    else:
        glow(fx, fy, 4, PAL['flame'][1], 0.5)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
