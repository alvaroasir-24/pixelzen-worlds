#!/usr/bin/env python3
"""PixelZen Worlds - Harry Potter (Monitor 2): Hogsmeade nevado, Viaducto del Expreso y Patronus."""
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
random.seed(972)

PALETAS = {
    'noche': dict(
        sky=['#050918', '#091128', '#101d3c', '#182b52', '#223a68', '#2e4a7e', '#3c5c94', '#4c6ea8', '#5e82ba', '#7296ca'],
        mont=('#202b44', '#161f34', '#0e1424'),
        snow=('#8da2c4', '#6d82a8', '#4c5e84', '#b8cce6'),
        stone=('#343848', '#222634', '#141620', '#50566c'),
        wall=('#4c4242', '#322a2c', '#1c161a'),
        roof=('#182032', '#242e48', '#9cb2d6'),
        train=('#7c1824', '#a82230', '#16161e', '#e2b64e'),
        win=('#ffca58', '#fff0b2'),
        pat=('#58e8ff', '#b8faff', '#ffffff'),
        pine=('#0c1820', '#162830', '#060e14'),
        vig=0.74,
        nube=['#223254', '#30446c', '#405684', '#526a9a', '#667eae', '#1c2a48'],
    ),
    'dorado': dict(
        sky=['#161230', '#261e44', '#3e2c58', '#623a64', '#8c4c64', '#b4625e', '#d67c56', '#ee9c56', '#fbc066', '#ffe08a'],
        mont=('#48324a', '#322238', '#1e1424'),
        snow=('#c6b4c8', '#9e8ca6', '#72627e', '#ead8e6'),
        stone=('#4e404e', '#342a36', '#1e1620', '#705e70'),
        wall=('#765c52', '#523e38', '#302220'),
        roof=('#24283c', '#363c5a', '#dfcce0'),
        train=('#8e1a26', '#bc2636', '#1c1620', '#ecc058'),
        win=('#ffd05e', '#fff2b6'),
        pat=('#68ecff', '#c6fbff', '#ffffff'),
        pine=('#1a2424', '#283634', '#0e1414'),
        vig=0.82,
        nube=['#5c3656', '#7e4862', '#a45e68', '#ca7866', '#ea9a68', '#462844'],
    ),
    'dia': dict(
        sky=['#2258a0', '#326eb6', '#4684ca', '#5e9cda', '#7ab4e6', '#98caf0', '#b6def4', '#d0ecf8', '#e6f4f8', '#f4f6ea'],
        mont=('#566c8e', '#445878', '#32425e'),
        snow=('#d8e6f4', '#b6cce2', '#8ea8c6', '#ffffff'),
        stone=('#686e80', '#4c5262', '#303440', '#8c94a8'),
        wall=('#b09c8e', '#88766a', '#5a4c44'),
        roof=('#2e3e58', '#42587c', '#f4f8fe'),
        train=('#981e2a', '#c62c3a', '#1e202a', '#ecc258'),
        win=('#ffd268', '#fff4c8'),
        pat=('#48d8f8', '#b8f8ff', '#ffffff'),
        pine=('#1e4430', '#2c6042', '#12281c'),
        vig=0.90,
        nube=['#ffffff', '#eef4fa', '#dce8f4', '#f6fafd', '#e4eef8', '#c8d8ec'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#78ecff', '#ffd468'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#d8eeff', base='#f8fcff', sombra='#cedaee', crater='#aab6d0', crater_hi='#c2cce2'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe49c', centro='#fffef2', borde='#ffc45c', rayo='#ffe298'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#e4f4ff', '#ffe8bc', '#a8b8e8'])

MX, MY, MR = 290, 72, 36
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#d8eeff', base='#f8fcff', sombra='#cedaee', crater='#aab6d0', crater_hi='#c2cce2')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 340, 174, 22, halo='#ffaa70', centro='#fff0dc', borde='#ff6646', rayo='#ff885e')
    else:
        dibuja_sol_estandar(lz, 286, 82, 22, halo='#ffe49c', centro='#fffef2', borde='#ffc45c', rayo='#ffe298')

NUBES_DEF = [
    (74, 36, 145, PAL['nube'][0], 2),
    (254, 48, 165, PAL['nube'][1], 3),
    (430, 32, 145, PAL['nube'][2], 2),
    (165, 118, 160, PAL['nube'][3], 3),
    (360, 114, 130, PAL['nube'][4], 2),
    (526, 224, 110, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 1. Montanas nevadas escocesas (bajando suavemente en x>420 para limpiar arcos y HUD)
rm = Ruido(977)
M0, M1, M2 = PAL['mont']
SN0, SN1, SN2, SN_HI = PAL['snow']
for x in range(W):
    ramp = max(0.0, min(1.0, (x - 400) / 100.0))
    dip_r = int(44 * (0.5 - 0.5 * math.cos(math.pi * ramp)))
    ridge = int(198 + 28 * fbm(rm, x * 0.013) + dip_r)
    ridge = min(HOR + 4, ridge)
    for y in range(ridge, HOR + 20):
        t = (y - ridge) / max(1, HOR + 20 - ridge)
        c = SN_HI if (t < 0.14 and x < 395) else mix(M0, M2, min(1.0, t))
        put(x, y, c)

# 2. VIADUCTO DE GLENFINNAN (6 arcos de piedra solidamente anclados en el valle en x=230..640, y=224..294)
ST_HI, ST_MD, ST_DK, ST_RIM = PAL['stone']
rx_st, ry_st = Ruido(985), Ruido(987)
for x in range(230, W):
    for y in range(226, 296):
        local_x = (x - 236) % 68
        if y >= 244 and 10 <= local_x <= 58:
            dx_a = local_x - 34
            if y >= 260 or (dx_a * dx_a) / (24.0 * 24.0) + ((260 - y) / 18.0) ** 2 <= 1.0:
                continue
        n_st = 0.5 * fbm(rx_st, x * 0.08) + 0.5 * fbm(ry_st, y * 0.09)
        c = ST_RIM if y < 229 else (ST_DK if (y > 282 or y % 7 == 0) else (ST_HI if (n_st > 0.58 or x % 14 == 0) else ST_MD))
        put(x, y, c)

# EXPRESO DE HOGWARTS (locomotora roja escarlata + 3 vagones sobre el viaducto y=194..226)
EX0, EX1, EX_BK, EX_GD = PAL['train']
WN0, WN1 = PAL['win']
# Locomotora encabezando hacia la izquierda (x=310..366)
for x in range(314, 366):
    top_l = 196 if x > 346 else 204
    for y in range(top_l, 226):
        if x > 350 and 202 <= y <= 210:
            put(x, y, WN0)
        elif y == 216:
            put(x, y, EX_GD)
        elif y > 220 or x < 320:
            put(x, y, EX_BK)
        else:
            put(x, y, EX1 if y < 210 else EX0)
for y in range(190, 206):
    for dx in (-2, -1, 0, 1, 2):
        put(326 + dx, y, EX_BK)
CHIMENEA = [326, 189]
if ANIM:
    FAROLES.append([312, 214, 10])
else:
    put(312, 214, WN1)
    glow(312, 214, 8, WN0, 0.65)
# Vagones escarlata (x=370..620)
for cx0, cx1 in ((370, 444), (448, 522), (526, 600)):
    for x in range(cx0, cx1):
        for y in range(200, 226):
            if y < 204:
                put(x, y, ST_DK)
            elif 207 <= y <= 215 and ((x - cx0) % 14) in range(3, 10):
                put(x, y, WN0)
                if ANIM and (x - cx0) % 14 == 6 and y == 211:
                    VENTANAS.append([x, y])
            elif y > 221:
                put(x, y, EX_BK)
            else:
                put(x, y, EX1 if y < 212 else EX0)

# 3. Valle nevado de Hogsmeade con suelo organico 2D (y=282..400)
rx_s, ry_s = Ruido(982), Ruido(983)
for y in range(282, H):
    for x in range(W):
        n2 = 0.5 * fbm(rx_s, x * 0.036) + 0.5 * fbm(ry_s, y * 0.048 + 7.0)
        c = SN_HI if n2 > 0.64 else (SN0 if n2 > 0.45 else (SN1 if n2 > 0.30 else SN2))
        put(x, y, c)

# Pinos nevados en el lindero del Bosque Prohibido (derecha y centro-fondo)
P0, P1, P2 = PAL['pine']
for px_p, py_p, ph_p in ((256, 304, 48), (284, 300, 54), (546, 316, 62), (576, 330, 72), (610, 322, 66)):
    for i in range(ph_p):
        y = py_p - ph_p + i
        hw = max(0, int(i * 0.28) - (2 if i % 5 == 4 else 0))
        for dx in range(-hw, hw + 1):
            c_p = SN_HI if (i % 5 == 0 and dx <= 0) else (P1 if dx < 0 else P2)
            put(px_p + dx, y, c_p)

# 4. CABANAS NEVADAS DE HOGSMEADE (x=24..226, base firme y=344..358)
WL0, WL1, WL2 = PAL['wall']
RF0, RF1, RF_SN = PAL['roof']
for hx, hw_c, hy_base, ch_h in ((72, 34, 344, 46), (154, 38, 352, 52)):
    top_w = hy_base - ch_h
    for x in range(hx - hw_c, hx + hw_c + 1):
        for y in range(top_w, hy_base + 1):
            c = WL2 if (x % 14 == 0 or y == hy_base) else (WL0 if x < hx else WL1)
            put(x, y, c)
    # Tejado inclinado cubierto de gruesa capa de nieve (sin bandas diagonales)
    for dy in range(28):
        y = top_w - 28 + dy
        hw_r = 6 + int(dy * (hw_c + 4) / 28.0)
        for dx in range(-hw_r, hw_r + 1):
            c = RF_SN if (dy < 9 + int(2 * math.sin(dx * 0.2))) else (RF1 if (dx < 0 and dy % 4 != 0) else RF0)
            put(hx + dx, y, c)
    # Chimenea
    for y in range(top_w - 36, top_w - 14):
        for dx in (-3, -2, -1, 0, 1, 2):
            put(hx + hw_c // 2 + dx, y, WL1 if dx < 0 else WL2)
    # Ventanas calidas doradas
    for wx in (hx - hw_c // 2, hx + hw_c // 2):
        for dy in range(11):
            for dx in range(-4, 5):
                put(wx + dx, top_w + 14 + dy, WL2 if (dx == 0 or dy == 5) else WN0)
        if ANIM:
            VENTANAS.append([wx - 1, top_w + 17])
# Faroles de calle en Hogsmeade (x=114, 210)
for fx_h in (114, 210):
    for y in range(304, 354):
        put(fx_h, y, EX_BK)
        put(fx_h + 1, y, ST_MD)
    put(fx_h, 302, WN1)
    if ANIM:
        FAROLES.append([fx_h, 302, 11])
    else:
        glow(fx_h, 302, 10, WN0, 0.7)

# 5. CIERVO PATRONUS LUMINOSO en el claro nevado (cx=458, by=358)
PT0, PT1, PT2 = PAL['pat']
px_c, py_c = 458, 358
spr_ciervo = [
    '...............KKK...',
    '..............KKKKK..',
    '............KKKKKK...',
    '....KKKKKKKKKKKKK....',
    '..KKKKKKKKKKKKKK.....',
    '.KKKKKKKKKKKKKK......',
    '.KKKKKKKKKKKKK.......',
    '.KK.KKKKKKKK.........',
    '.K..KK...KK..........',
    '....KK...KK..........',
    '...KK.....KK.........',
    '...K.......K.........',
]
pinta_sprite(lz, px_c, py_c, spr_ciervo, {'K': PT0})
# Cornamenta ramificada brillante
for side in (-1, 1):
    for k in range(11):
        ax = px_c + 7 + side * (k // 2)
        ay = py_c - 12 - k
        put(ax, ay, PT2 if k % 2 == 0 else PT1)
        if k in (4, 8):
            put(ax + side * 2, ay - 2, PT2)
            put(ax + side * 3, ay - 3, PT1)
# Halo Patronus suave en nieve y aire
if ANIM:
    RUNAS.append([px_c + 5, py_c - 12])
    RUNAS.append([px_c - 2, py_c - 6])
    FAROLES.append([px_c + 2, py_c - 8, 16])
else:
    glow(px_c + 2, py_c - 8, 18, PT0, 0.55)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
