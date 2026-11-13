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

MX, MY, MR = 326, 82, 40
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#ffdca8', base='#fffbf0', sombra='#d8d2be', crater='#b8b29e', crater_hi='#ccc6b2')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 360, 178, 22, halo='#ff9868', centro='#ffecd8', borde='#ff6042', rayo='#ff8058')
    else:
        dibuja_sol_estandar(lz, 310, 88, 22, halo='#ffe298', centro='#fffef2', borde='#ffbe54', rayo='#ffe090')

NUBES_DEF = [
    (92, 42, 165, PAL['nube'][0], 3),
    (256, 56, 150, PAL['nube'][1], 2),
    (418, 38, 140, PAL['nube'][2], 2),
    (168, 124, 175, PAL['nube'][3], 3),
    (380, 138, 135, PAL['nube'][4], 2),
    (536, 226, 110, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 1. Montanas y bosques oscuros tras el claro (bajando suavemente en x>430 para HUD)
rm = Ruido(1107)
M0, M1, M2 = PAL['mont']
for x in range(W):
    ramp = max(0.0, min(1.0, (x - 420) / 80.0))
    dip_h = int(28 * (0.5 - 0.5 * math.cos(math.pi * ramp)))
    ridge = int(214 + 28 * fbm(rm, x * 0.014) + dip_h)
    ridge = min(HOR + 4, ridge)
    for y in range(ridge, HOR + 22):
        t = (y - ridge) / max(1, (HOR + 22 - ridge))
        put(x, y, mix(M0, M2, min(1.0, t)))

P0, P1, P2 = PAL['pine']


def pino(px, by, h):
    for i in range(h):
        y = by - h + i
        hw = max(0, int(i * 0.28) - (2 if i % 5 == 4 else 0))
        for dx in range(-hw, hw + 1):
            put(px + dx, y, P1 if dx < 0 else (P0 if dx < hw // 2 else P2))


for px_t, py_t, ph_t in ((14, 298, 66), (42, 294, 58), (76, 296, 52), (242, 294, 48), (272, 296, 54), (496, 296, 44), (534, 298, 52), (576, 296, 56), (614, 298, 64)):
    pino(px_t, py_t, ph_t)

# 2. Pradera del claro del Tren Infinito con ruido 2D organico (y = 290..400)
rx_g = Ruido(1123)
ry_g = Ruido(1151)
G0, G1, G2, G3 = PAL['ground']
for y in range(290, H):
    for x in range(W):
        n2 = 0.5 * fbm(rx_g, x * 0.036) + 0.5 * fbm(ry_g, y * 0.048 + 7.0) + 0.14 * math.sin(x * 0.06) * math.cos(y * 0.07)
        c = G3 if n2 > 0.64 else (G1 if n2 > 0.48 else (G0 if n2 > 0.34 else G2))
        # Tierra removida alrededor del descarrilamiento (x < 245, y ~ 318..364)
        if x < 248 and 318 <= y <= 368 and (n2 > 0.42 or y > 334):
            c = mix(c, G2, 0.45)
        put(x, y, c)

# Traviesas de madera y rieles del Tren Infinito recorriendo todo el claro (x=0..640)
def rail_y(rx):
    return int(341 + 5 * math.sin(rx * 0.008) - (rx - 240) * 0.018 if rx > 240 else 341 + 4 * math.sin(rx * 0.02))


for tx in range(10, W, 16):
    ty = rail_y(tx)
    for dy in range(4):
        for dx in range(-5, 6):
            put(tx + dx, ty + dy, '#2a1d18' if dy < 2 else '#140d0a')
for x in range(W):
    ry_rail = rail_y(x)
    put(x, ry_rail - 1, '#7c8496')
    put(x, ry_rail, '#404656')
    put(x, ry_rail + 2, '#5a6070')

# 3. TREN INFINITO (locomotora a vapor + 2 vagones iluminados anclados en la via x=0..234)
TR_DK, TR_MD, TR_HI, TR_R, TR_GL = PAL['train']

# Vagon trasero y central (sobre las vias en y=338)
for vx0, vx1, tilt_v in ((0, 56, 0.02), (60, 128, 0.04)):
    for x in range(vx0, vx1):
        drop = int((x - vx0) * tilt_v)
        top_v = 278 + drop
        bot_v = 336 + drop // 2
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
    # Ruedas apoyadas en el terreno
    for wx in (vx0 + 14, vx1 - 14):
        disc(wx, 336, 6, TR_DK)
        disc(wx, 336, 3, TR_HI)

# Locomotora del Tren Infinito (x=132..234, ligeramente inclinada en el choque, firmemente apoyada en tierra)
for x in range(132, 224):
    drop = int((x - 132) * 0.08)
    is_cab = x < 164
    top_l = (264 if is_cab else 274) + drop
    bot_l = 334 + drop // 2
    for y in range(top_l, bot_l + 1):
        if y < top_l + 4:
            c = TR_HI
        elif is_cab and 140 <= x <= 156 and top_l + 8 <= y <= top_l + 20:
            c = TR_GL
        elif not is_cab and top_l + 14 <= y <= top_l + 18:
            c = TR_R  # franja carmesi caldera
        elif y > bot_l - 6:
            c = TR_DK
        else:
            c = TR_MD if x < 210 else TR_HI
        put(x, y, c)
# Chimenea de la locomotora (x=202)
for y in range(254, 282):
    hw_c = 5 if y < 260 else 3
    for dx in range(-hw_c, hw_c + 1):
        put(202 + dx, y, TR_HI if dx < 0 else TR_DK)
CHIMENEA = [202, 253]
# Deflector delantero (quitanieves) clavado en la tierra (x=222..238)
for y in range(318, 344):
    hw_f = (y - 318) // 2 + 2
    for dx in range(0, hw_f + 1):
        put(222 + dx, y, TR_HI if dx < 3 else TR_DK)
# Ruedas motrices grandes de la locomotora
for wx, wr in ((148, 8), (174, 10), (198, 10), (216, 7)):
    disc(wx, 338, wr, TR_DK)
    disc(wx, 338, wr - 3, TR_HI)
    disc(wx, 338, 2, TR_R)
# Faro frontal de la locomotora
if ANIM:
    FAROLES.append([225, 290, 12])
else:
    glow(225, 290, 12, TR_GL, 0.72)
put(224, 290, '#fff6c8')
put(225, 290, '#fff6c8')

# Humo suave y abombado en estatico
if not ANIM:
    smoke_c = '#262b3b' if FASE == 'noche' else '#687082'
    smoke_hi = '#3a4056' if FASE == 'noche' else '#8e96aa'
    for k in range(11):
        sx_s = 200 - k * 8 + int(math.sin(k * 0.9) * 3)
        sy_s = 248 - k * 3 - int(k ** 1.15 * 0.4)
        rr_s = 3 + min(6, k // 2)
        disc(sx_s, sy_s, rr_s, smoke_c)
        disc(sx_s - 1, sy_s - 1, max(1, rr_s - 2), smoke_hi)


# 4. DUELO ICONICO: KYOJURO RENGOKU vs AKAZA (cx=342 y cx=448, suelo y=358)
def dibuja_rengoku(cx, by):
    SH_C, SH_R = PAL['shad_core'], PAL['shad_rim']
    F0, F1, F2, F3 = PAL['flame']

    # Sombra en tierra
    for dx in range(-18, 19):
        for dy in range(-2, 3):
            if (dx / 18.0) ** 2 + (dy / 2.5) ** 2 <= 1.0:
                over(cx + dx, by + dy, '#05040a', 0.75)

    # Haori de llamas ondeando atras (blanco crema arriba fundiendo en llamas rojas/naranjas en el borde irregular)
    for t_c in range(22):
        cx_w = cx - 4 - t_c
        ty_w = by - 22 + int(t_c * 0.16 + math.sin(t_c * 0.25) * 1.4)
        bh_w = max(5, 16 - t_c // 2) + (2 if t_c % 4 == 0 else 0)
        for dy in range(bh_w):
            if dy < bh_w - 6:
                col_c = '#c6c9d6' if FASE == 'noche' else '#e2e4ee'
            elif dy < bh_w - 3:
                col_c = F1
            else:
                col_c = F0
            put(cx_w, ty_w + dy, col_c)

    # Silueta sombreada de Rengoku en postura ofensiva de katana
    spr = [
        '.......KKKKK........',
        '......KKKKKKK.......',
        '......KKFFKKK.......',
        '.......KKKKK........',
        '....KKKKKKKKKKK.....',
        '...KKKKKKKKKKKKKK...',
        '..KKK.KKKKKKKKKKKK..',
        '.KKK..KKKKKKKK......',
        '......KKKKKKKK......',
        '.....KKKKKKKKKK.....',
        '.....KKKKKKKKKK.....',
        '....KKKKK..KKKKK....',
        '....KKKK....KKKK....',
        '...KKKK......KKKK...',
        '..KKKK........KKKK..',
        '..KKK..........KKK..',
    ]
    # Pelo llameante dorado/carmesi caracteristico sobre la cabeza
    pinta_sprite(lz, cx, by, spr, {'K': SH_C, 'F': F2})
    for dx in range(-5, 6):
        put(cx + dx, by - 16, F2 if abs(dx) < 3 else F1)
        put(cx + dx, by - 17, F1 if dx % 2 == 0 else F0)
    for sx_h in (-4, -1, 2, 4):
        put(cx + sx_h, by - 18, F0)

    # Hoja de katana Nichirin carmesi extendida al frente
    for s in range(18):
        put(cx + 6 + s, by - 11 - s // 3, F1 if s < 12 else F3)
        put(cx + 6 + s, by - 10 - s // 3, F0)

    # Novena Postura: Rengoku! Torrente conectado en espiral de fuego desde su espada hacia Akaza
    for step in range(54):
        u = step / 53.0
        bx_f = int(cx + 12 + u * 56)
        by_f = int(by - 12 - math.sin(u * math.pi * 1.1) * 18 + math.sin(u * 9.0) * 3)
        r_f = 4 if 0.30 < u < 0.78 else (3 if u < 0.90 else 2)
        for dy in range(-r_f, r_f + 1):
            for dx in range(-r_f, r_f + 1):
                if dx * dx + dy * dy <= r_f * r_f:
                    d_norm = math.hypot(dx, dy) / max(1, r_f)
                    c_fl = F3 if d_norm < 0.35 else (F2 if d_norm < 0.65 else (F1 if u < 0.8 else F0))
                    put(bx_f + dx, by_f + dy, c_fl)
        if step % 9 == 0:
            if ANIM:
                FAROLES.append([bx_f, by_f, 10])
                RUNAS.append([bx_f, by_f])
            else:
                glow(bx_f, by_f, 7, F1, 0.50)


def dibuja_akaza(cx, by):
    SH_C, SH_R = PAL['shad_core'], PAL['shad_rim']
    AK_CY, AK_HI, AK_HR = PAL['akaza']

    # Tecnica de Despliegue: Brujula Destructiva (copo luminoso cian bajo sus pies)
    for dy in range(-7, 8):
        for dx in range(-36, 37):
            d = math.hypot(dx / 35.0, dy / 6.5)
            ang = math.atan2(dy / 6.5, dx / 35.0)
            rayo = abs(math.cos(ang * 6.0))
            if 0.86 <= d <= 1.0 or (d < 0.96 and rayo > 0.90):
                put(cx + dx, by + dy, AK_HI if d < 0.5 else AK_CY)
    for rx_c in (-28, -16, 0, 16, 28):
        if ANIM:
            RUNAS.append([cx + rx_c, by])
        else:
            glow(cx + rx_c, by, 5, AK_CY, 0.55)

    # Silueta sombreada musculosa en guardia Soryu mirando a la izquierda
    spr = [
        '.......KKKKK........',
        '......KKKKKKK.......',
        '......KKFFKKK.......',
        '.......KKKKK........',
        '....KKKKKKKKKK......',
        '..KKKKKKKKKKKKKK....',
        'KKKK..KKKKKKKKK.KK..',
        'KK....KKKKKKKKK..KK.',
        '......KKKKKKKKK.....',
        '.....KKKKKKKKKK.....',
        '.....KKKKKK.KKKK....',
        '....KKKKK....KKKK...',
        '...KKKKK......KKKK..',
        '...KKKK........KKKK.',
        '..KKKK..........KKKK',
    ]
    pinta_sprite(lz, cx, by, spr, {'K': SH_C, 'F': '#ffe066'})
    # Pelo corto puntiagudo carmesi de Akaza + marcas Soryu cian
    for sx_a in range(-4, 5, 2):
        put(cx + sx_a, by - 16, AK_HR)
        put(cx + sx_a, by - 17, AK_HR)
    for mx_s, my_s in ((-7, -9), (-4, -11), (2, -10), (5, -8)):
        put(cx + mx_s, by + my_s, AK_CY)

    # Onda de choque en el punto de impacto (x ~ 396, y ~ 334)
    if ANIM:
        RUNAS.append([cx - 26, by - 22])
        FAROLES.append([cx - 24, by - 22, 13])
    else:
        glow(cx - 24, by - 22, 11, AK_CY, 0.6)


dibuja_rengoku(344, 358)
dibuja_akaza(446, 360)

# Llamas en arboles lejanos/brasas por la batalla
for fx, fy in ((286, 362), (316, 368), (488, 366)):
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
