#!/usr/bin/env python3
"""PixelZen Worlds - Black Clover (Monitor 2): Reino de Picas y la Tríada Oscura."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, exporta_salida, exporta_sprites_si_aplica, fbm, mix, render_cielo,
    render_estrellas, render_lago, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(4708)

PALETAS = {
    'noche': dict(
        sky=['#04020a', '#0a0518', '#140a2a', '#22103c', '#34164c', '#4a1c58', '#62225e', '#7e2a62', '#9c3664', '#b84868'],
        mont=['#2a2442', '#201b34', '#161224', '#0e0b18', '#080610'],
        mist=['#644a7c', '#503966', '#3d2a52', '#2b1c3c', '#1c122a'],
        nieve=('#dce4f8', '#8a96bc'), filo='#9cc4e8',
        castle=('#100d1a', '#1b162a', '#2b2442', '#3c3458'),
        spire=('#090710', '#161224', '#26203a'),
        crimson=('#741424', '#a81e34', '#dc2c48'),
        gold=('#ffd458', '#c88c24'),
        grav=('#08040e', '#e82848', '#ff94a8'),
        blood=('#8c1028', '#e82848', '#ff88a0'),
        spatial=('#2a4898', '#48a4ff', '#bceeff'),
        bone=('#cbd2e4', '#f2f6ff', '#8a92aa'),
        dais=('#141020', '#201a32', '#302848'),
        agua='#080614',
        ola=('#d86c92', '#4e3878', '#22143a'),
        vig=0.72,
        nube=['#382650', '#4c3264', '#663e72', '#824c78', '#9e5c7e', '#2e1e42'],
        pino=('#07060e', '#100e1c', '#384664'),
    ),
    'dorado': dict(
        sky=['#160822', '#260d34', '#3e1244', '#601a4a', '#862248', '#ae303e', '#d24636', '#eb6838', '#fa9046', '#ffc064'],
        mont=['#4c283e', '#3a1e32', '#2a1524', '#1c0e1a', '#120810'],
        mist=['#dc7462', '#ba5858', '#924050', '#6a2c44', '#461c34'],
        nieve=('#ffe8df', '#c698a4'), filo='#ffc898',
        castle=('#180e18', '#261826', '#3c263a', '#523650'),
        spire=('#100812', '#201220', '#341e32'),
        crimson=('#8c1624', '#c42434', '#f43c4c'),
        gold=('#ffe068', '#d49624'),
        grav=('#0c040c', '#ff3450', '#ffaa98'),
        blood=('#9e1424', '#f03048', '#ff949c'),
        spatial=('#3458b0', '#58b4ff', '#d4f4ff'),
        bone=('#e0d8e0', '#fff8f4', '#9e92a0'),
        dais=('#1e121e', '#2e1c2e', '#442a42'),
        agua='#1e0c22',
        ola=('#ffa47e', '#884266', '#401838'),
        vig=0.80,
        nube=['#6e3252', '#94405c', '#bc545c', '#de725a', '#f69862', '#582644'],
        pino=('#120a14', '#1e1020', '#6a485a'),
    ),
    'dia': dict(
        sky=['#1f4d94', '#2e62aa', '#4278be', '#5c90d0', '#7aa8de', '#9ac0ea', '#b8d6f0', '#d4e6f2', '#e8eff2', '#f4f0dc'],
        mont=['#546282', '#44506e', '#36405a', '#283046', '#1c2234'],
        mist=['#c4d6e8', '#a8bed4', '#8ca4c0', '#708aa8', '#567090'],
        nieve=('#ffffff', '#c8daf0'), filo='#ffffff',
        castle=('#1c2032', '#2a3048', '#3e4664', '#545e80'),
        spire=('#121624', '#22283c', '#343c58'),
        crimson=('#821c2a', '#b6283a', '#e03c4e'),
        gold=('#ffe46a', '#cca02c'),
        grav=('#0d0816', '#e82848', '#ffb4be'),
        blood=('#98182e', '#e82c48', '#ff98a4'),
        spatial=('#2858b0', '#48b2ff', '#d8f6ff'),
        bone=('#dce2ee', '#ffffff', '#9aa4b8'),
        dais=('#222638', '#323850', '#48506e'),
        agua='#223c60',
        ola=('#d8e6f4', '#7492ba', '#385076'),
        vig=0.90,
        nube=['#ffffff', '#eef4fa', '#ffffff', '#e4eef8', '#f8f8f6', '#dbe6f2'],
        pino=('#141c2c', '#202c40', '#7a94b4'),
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

# 1. Cielo invernal + aurora abisal de la Tríada
render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#e82848', '#7c48ff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 44, halo='#e87098', base='#fff0f4', sombra='#d4b4c4', crater='#ae8ca0', crater_hi='#c6a8b8'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 24, halo='#ffe2a8', centro='#fffef2', borde='#ffc464', rayo='#ffe49c'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffe4ec', '#e0d0ff', '#a8d4ff'])

MX, MY, MR = 382, 74, 40
CX_ASTRO = MX if FASE == 'noche' else (MX + 28 if FASE == 'dorado' else MX - 32)
# Monitor 2 comparte cielo con Monitor 1: no duplicar sol/luna aquí

NUBES_DEF = [
    (110, 62, 165, PAL['nube'][0], 3),
    (290, 48, 155, PAL['nube'][1], 3),
    (525, 114, 155, PAL['nube'][2], 3),
    (205, 162, 170, PAL['nube'][3], 2),
    (445, 206, 145, PAL['nube'][4], 2),
    (75, 236, 115, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 2. Cordillera helada del Reino de Picas (más baja en x > 460 para dejar despejado el HUD)
def rampa_picas(x):
    return 1.0 if x < 420 else max(0.35, 1.0 - (x - 420) / 140.0 * 0.65)

for base, amp, seed, col, mist, con_nieve in (
    (242, 92, 51, PAL['mont'][0], PAL['mist'][0], True),
    (254, 72, 52, PAL['mont'][1], PAL['mist'][1], True),
    (266, 52, 53, PAL['mont'][2], PAL['mist'][2], False),
    (275, 34, 54, PAL['mont'][3], PAL['mist'][3], False),
):
    r, ra = Ruido(seed * 17), Ruido(seed * 41 + 5)
    for x in range(W):
        n = fbm(r, x * 0.017 + seed)
        agudo = 1 - abs(2 * n - 1)
        am = 0.35 + 0.90 * ra(x * 0.013 + seed) ** 1.2
        top = int(base - amp * rampa_picas(x) * am * (0.68 * agudo + 0.32 * n))
        for y in range(top, HOR + 1):
            d = y - top
            cc = mix(col, mist, 0.24 * (d / max(1, HOR - top)) ** 1.9)
            if con_nieve and top < base - amp * 0.45 * rampa_picas(x) and d < (base - amp * 0.45 * rampa_picas(x) - top) * 0.52:
                cc = mix(PAL['nieve'][0], PAL['nieve'][1], min(1.0, d / 12.0))
            elif d < 2:
                cc = mix(cc, PAL['filo'], 0.25)
            put(x, y, cc)

# 3. Silueta colosal del Demonio Ancestral congelado al fondo izquierdo (x ~ 66, y ~ 196)
DMX, DMY = 66, 198
disc(DMX, DMY, 16, PAL['spire'][0])
for yy in range(DMY + 10, HOR - 12):
    hw = 16 + (yy - DMY - 10) // 2
    for dx in range(-hw, hw + 1):
        put(DMX + dx, yy, PAL['spire'][0] if dx < 4 else PAL['castle'][0])
# Cuernos curvos del demonio ancestral
for sgn in (-1, 1):
    for t in range(28):
        hx = DMX + sgn * (12 + int(t * 0.85))
        hy = DMY - 6 - int(math.sin(t / 27.0 * math.pi * 0.85) * 26)
        disc(hx, hy, max(1, 3 - t // 10), PAL['spire'][1] if sgn < 0 else PAL['spire'][0])
# Ojos demoníacos tenues
for ex in (DMX - 6, DMX + 5):
    put(ex, DMY - 2, PAL['crimson'][2])
    put(ex + 1, DMY - 2, PAL['crimson'][1])

# 4. Fortaleza Real del Reino de Picas (izquierda-centro, x = 104..304)
CS0, CS1, CS2, CS3 = PAL['castle']
SP0, SP1, SP2 = PAL['spire']
CR0, CR1, CR2 = PAL['crimson']
GD0, GD1 = PAL['gold']

# Risco helado base del castillo con textura orgánica de roca y nieve
r_cliff = Ruido(701)
for y in range(HOR - 36, HOR + 1):
    t = (HOR - y) / 36.0
    ww = int(124 * (1 - t ** 1.35))
    for x in range(max(0, 206 - ww), 206 + ww):
        n = r_cliff(x * 0.14 + y * 0.21)
        c = CS2 if y < HOR - 33 else (CS1 if n > 0.48 else CS0)
        if y < HOR - 30 and r_cliff(x * 0.09) > 0.56:
            c = mix(c, PAL['nieve'][1], 0.55)
        put(x, y, c)

# Muralla exterior y almenas de Picas
for x in range(114, 298):
    for yy in range(HOR - 60, HOR - 24):
        put(x, yy, CS2 if x < 206 else CS1)
    if x % 6 < 3:
        put(x, HOR - 62, CS3)
        put(x, HOR - 61, PAL['nieve'][0])

# Torres y agujas góticas del Reino de Picas
def torre_picas(cx, tw, th, sh):
    y0 = HOR - 58 - th
    for yy in range(y0, HOR - 56):
        for x in range(cx - tw // 2, cx + tw // 2 + 1):
            c = CS3 if x < cx - tw // 4 else (CS2 if x < cx + tw // 4 else CS0)
            if yy % 10 == 0 and x % 3 == 0:
                c = SP0
            put(x, yy, c)
    # Ventanas verticales carmesí de la fortaleza
    for wy in range(y0 + 10, HOR - 62, 13):
        if ANIM:
            VENTANAS.append([cx - 1, wy])
        else:
            for dy in range(4):
                put(cx - 1, wy + dy, CR2)
                put(cx, wy + dy, CR1)
    # Aguja gótica afilada + nieve en arista izquierda
    for i in range(sh):
        hw = max(0, int((tw // 2 + 3) * (1 - i / max(1, sh - 1)) ** 1.25))
        for x in range(cx - hw, cx + hw + 1):
            put(x, y0 - i, SP2 if x < cx else SP0)
        if hw >= 1:
            put(cx - hw, y0 - i, PAL['nieve'][1])
    return y0 - sh

top_izq = torre_picas(142, 18, 46, 36)
top_cen = torre_picas(206, 34, 72, 48)
top_der = torre_picas(270, 20, 48, 36)

# Gran Emblema de la Pica Negra (♠) en el torreón central
for dy in range(-8, 7):
    if dy < -3:
        hw = max(0, (dy + 9) // 2 + 1)
    elif dy < 3:
        hw = 7 - max(0, (dy - 1))
    else:
        hw = 2 if dy < 5 else 4
    for dx in range(-hw, hw + 1):
        c = GD0 if (abs(dx) == hw or dy == -8 or dy == 6) else SP0
        put(206 + dx, HOR - 92 + dy, c)

# Estandartes carmesíes de Picas colgando de la muralla
for bx in (164, 248):
    for yy in range(HOR - 54, HOR - 32):
        for dx in range(-4, 5):
            if yy > HOR - 38 and abs(dx) > (HOR - 32 - yy):
                continue
            put(bx + dx, yy, CR1 if abs(dx) < 3 else CR0)
        put(bx, yy, SP0 if HOR - 48 <= yy <= HOR - 40 else CR2)

# Sello del Qliphoth / Portal ritual de la Tríada sobre la aguja central (cx = 206, cy = 86)
Q_CX, Q_CY = 206, top_cen - 22
for r_ring, col_r in ((24, CR1), (17, PAL['grav'][1]), (10, PAL['spatial'][1])):
    for ang in range(0, 360, 5):
        rad = math.radians(ang)
        rx = int(Q_CX + r_ring * math.cos(rad))
        ry = int(Q_CY + r_ring * 0.85 * math.sin(rad))
        put(rx, ry, col_r)
        if ang % 45 == 0:
            if ANIM:
                RUNAS.append([rx, ry])
            else:
                put(rx, ry, PAL['grav'][2])
                glow(rx, ry, 4, CR1, 0.45)
if not ANIM:
    glow(Q_CX, Q_CY, 12, CR0, 0.35)

# 5. Bastión / Terraza real de la TRÍADA OSCURA (x = 292..474, despejada para apreciar sus siluetas)
DX0, DX1, DY_TOP = 294, 472, HOR - 24
r_dais = Ruido(709)
for y in range(DY_TOP, HOR + 1):
    for x in range(DX0 - (y - DY_TOP) // 2, min(W, DX1 + (y - DY_TOP) // 2)):
        c = PAL['dais'][1] if r_dais(x * 0.16 + y * 0.22) > 0.46 else PAL['dais'][0]
        if (y - DY_TOP) % 8 == 0 and r_dais(x * 0.08) > 0.35:
            c = PAL['dais'][2]
        put(x, y, c)
for x in range(DX0, DX1 + 1):
    put(x, DY_TOP, PAL['dais'][2])
    if x % 8 < 4:
        put(x, DY_TOP - 1, PAL['nieve'][1])


def _pinta_sprite(cx, by, spr, cmap, off_x=0):
    """Pinta una matriz pixel-art centrada en cx+off_x con base en by."""
    assert len({len(r) for r in spr}) == 1, f"Sprite filas desiguales: {[len(r) for r in spr]}"
    sw = len(spr[0])
    sh = len(spr)
    x0 = cx - sw // 2 + off_x
    y0 = by - sh + 1
    for ry, row in enumerate(spr):
        for rx, ch in enumerate(row):
            col = cmap.get(ch)
            if col:
                put(x0 + rx, y0 + ry, col)
    return x0, y0


def dibuja_zenon(cx, by):
    """Zenon Zogratis (fiel al sprite ZENON): pelo corto oscuro, piel pálida fría con marca frontal,
    cuello de piel gris claro, capa negra larga, túnica granate con cinturón y picos de Magia de Hueso."""
    bn0, bn1, bn2 = PAL['bone']

    # Picos afilados de Magia de Hueso blanco saliendo diagonalmente hacia fuera (ZENON IDLE 3/4)
    for sx, sy, ex, ey, th in (
        (cx - 10, by, cx - 22, by - 21, 2),
        (cx + 10, by, cx + 22, by - 21, 2),
        (cx - 14, by - 2, cx - 26, by - 13, 1),
        (cx + 14, by - 2, cx + 26, by - 13, 1),
        (cx - 9, by - 31, cx - 22, by - 43, 1),
        (cx + 9, by - 31, cx + 22, by - 43, 1),
    ):
        steps = 18
        for s in range(steps + 1):
            t = s / steps
            px = int(sx + (ex - sx) * t)
            py = int(sy + (ey - sy) * t)
            w_cur = max(0, int(th * (1 - t * 0.92)))
            for d_w in range(-w_cur - 1, w_cur + 2):
                if abs(d_w) == w_cur + 1:
                    put(px + d_w, py, '#0b0a12')
                else:
                    put(px + d_w, py, bn1 if d_w <= 0 else bn0)
            if s == steps:
                put(px, py - 1, bn2)

    cmap = {
        'O': '#0b0a12',
        'H': '#1c1e2a', 'h': '#32364a',
        'S': '#d4cee0', 's': '#a8a0b8',
        'M': '#221c34', 'e': '#1a1526',
        'F': '#d8dae4', 'f': '#9fa4b6', 'W': '#eff1f8',
        'K': '#222430', 'k': '#343848', 'd': '#14151e',
        'V': '#6c202c', 'v': '#922e3e', 'u': '#4a141e',
        'B': '#5a3a24', 'G': '#eab844',
        'P': '#222534', 'p': '#151722',
    }
    # 33x51 px
    spr = [
        "............OOOOOOOO.............",
        "...........OHHHHHHHHO............",
        "..........OHHhHHHHHhHO...........",
        "..........OHHHHHHHHHHO...........",
        "..........OHHHhHHhHHHO...........",
        "..........OHSSSSSSSSHO...........",
        "..........OSSSSMMSSSSO...........",
        "..........OSSeSMMSeSSO...........",
        "...........OSSSSSSSSO............",
        "............OOSssSOO.............",
        ".............OSSSSO..............",
        "........OOOOOOWFFWOOOOOO.........",
        ".......OOWWFFFFWWFFFFWWOO........",
        "......OWFFFFWFFFFFFWFFFFWO.......",
        ".....OOFfFFFFfFFFFfFFFFfFO.......",
        ".....OKOOffffVVVVVVffffOOKO......",
        "....OKKKOOKOVVVvvVVVOKOKKKKO.....",
        "....OKkkKOKOVVvvvvVVOKOKkkKO.....",
        "...OKKKdKOKOVVVvvVVVOKOKdKKKO....",
        "...OKKKdKOKOVVVVVVVVOKOKdKKKO....",
        "...OKKdKKOKOBBBBBBBKOKOKKdKKO....",
        "...OKKdKKOKOBBBGGGBKOKOKKdKKO....",
        "...OKKdKKOKOVVVVVVVVOKOKKdKKO....",
        "..OKKKdKKOKOVVVvvVVVOKOKKdKKKO...",
        "..OKKdKKdOKOVVvvvvVVOKOKdKKdKO...",
        "..OKKdKSSOOKOVVVVVVOKOOSSKdKKO...",
        "..OKKddOO.OKOVVuuVVOK..OOddKKO...",
        "..OKKdO...OKOVVuuVVOK....OdKKO...",
        "..OKKdO...OKOVVuuVVOK....OdKKO...",
        "..OKdO....OKOVVOOOVOK.....OdKO...",
        "..OKdO....OKOPPOOOPPO.....OdKO...",
        "..OKdO....OKOPPpOppPO.....OdKO...",
        "..OKdO....OKOPPpOppPO.....OdKO...",
        "..OKdO....OKOPPpOppPO.....OdKO...",
        "..OKdO....OKOPPpOppPO.....OdKO...",
        "..OKdO....OKOPPpOppPO.....OdKO...",
        "..OKdO....OKOPPpOppPO.....OdKO...",
        "..OKdO....OKOPPpOppPO.....OdKO...",
        "..OKdO....OOOPPpOppPO.....OdKO...",
        "..OKdO......OKKOOOKKO.....OdKO...",
        "..OKOO......OKKOOOKKO.....OOKO...",
        "..OO........OKkOOOkKO.......OO...",
        "............OKkOOOkKO............",
        "............OKkOOOkKO............",
        "............OKkOOOkKO............",
        "............OKdOOOdKO............",
        "............OKdOOOdKO............",
        "............OKdOOOdKO............",
        "...........OKKdOOOdKKO...........",
        "..........OKKKdOOOdKKKO..........",
        "..........OOOOO...OOOOO..........",
    ]
    _pinta_sprite(cx, by, spr, cmap)
    if ANIM:
        RUNAS.append([cx, by - 46])


def dibuja_dante(cx, by):
    """Dante Zogratis (fiel al sprite IDLE 0/1): corona dorada alta con picos, cabello castaño oscuro,
    cuello de piel claro, capa negra amplia, túnica granate con cinturón, botas marrón-oliva
    y mano izquierda alzada sosteniendo esfera negro-púrpura de Gravedad."""
    cmap = {
        'O': '#0b0812',
        'G': '#f0c044', 'g': '#b2821e', 'y': '#ffe07a',
        'H': '#3a2420', 'h': '#563630',
        'S': '#e6c6b6', 's': '#be9a8c',
        'M': '#281624', 'e': '#1c1218',
        'F': '#d8dae4', 'f': '#9fa4b6', 'W': '#eff1f8',
        'K': '#222430', 'k': '#343848', 'd': '#14151e',
        'V': '#6c202c', 'v': '#922e3e', 'u': '#4a141e',
        'B': '#5a3a24',
        'P': '#222534', 'p': '#151722',
        'T': '#6e5a28', 't': '#4c3e18',
    }
    # 45x51 px (centro del cuerpo en col 18; mano izquierda extendida a col 36)
    spr = [
        ".............O...O...O...O...................",
        "............OyO.OGOOOGOOOyO..................",
        "............OGGOGGGOOGGGOGGO.................",
        "............OGGGGyGGGGyGGGGO.................",
        "............OGGGGGGGGGGGGGGO.................",
        "............OggggggggggggggO.................",
        "............OHHHHHHHHHHHHHHO.................",
        "...........OHhHHHHHHHHHHHHhHO................",
        "...........OHHHSSSSSSSSSSHHHO................",
        "...........OHHSSSeSSMMSSSeSHO................",
        "............OSSSSSSSSSSSSSSO.................",
        ".............OSSSSssssSSSSO..................",
        ".............OOSSSHHHHSSSOO..................",
        ".............OOHHHHHHHHHHOO..................",
        "........OOOOOOWWFFFFFFFWWOOOOO...............",
        ".......OOWFFFFFWWFFFFFWWFFFFFWOO.............",
        "......OWFFFFfFFFFFWFFWFFFFFfFFFWO............",
        "......OOFfffFFFFfFFFFFFfFFFFfffFO............",
        ".....OKKOOOfffOKKVVvvVVKKOfffOOKKO...........",
        "....OKKKdKKOOOOKOVVvvVVOKOOOOOKKKKO..........",
        "....OKKdKKKKKKOKOVVvvVVOKOKKKKKdKKO..........",
        "...OKKKdKKKKKKOKOVVvvVVOKOKKKKKKdKKO.........",
        "...OKKdKKKKKKdOKOVVVVVVOKOKKKKKKdKKO.........",
        "...OKKdKKKKKKdOKOBBBBBBBKOKKKKKKdKKO.........",
        "...OKKdKKKKdKdOKOBBGGGBBKOKKKKKKKSSOO........",
        "..OKKKdKKKKdKdOKOVVVVVVOKOKKKKOOOOSSO........",
        "..OKKdKKKSSOOKOKOVVvvVVOKOKKKO....OO.........",
        "..OKKdKKSSOO.OKOVVvvvvVVOKOKKO...............",
        "..OKKdKKOO...OKOVVVuuVVVOKOKKO...............",
        "..OKKdKO.....OKOVVVuuVVVOKOKKO...............",
        "..OKKdKO.....OKOVVVuuVVVOKOKKO...............",
        "..OKKdO......OKOVVVuuVVVOKOdKO...............",
        "..OKdKO......OKOVVOOOOVVOKOdKO...............",
        "..OKdKO......OKOPPPOOOPPPOOdKO...............",
        "..OKdKO......OKOPPpOOOpPPOOdKO...............",
        "..OKdKO......OKOPPpOOOpPPOOdKO...............",
        "..OKdO.......OKOPPpOOOpPPOOdKO...............",
        "..OKdO.......OKOPPpOOOpPPOOdKO...............",
        "..OKdO.......OKOPPpOOOpPPOOdKO...............",
        "..OKdO.......OOOPPpOOOpPPdOKOO...............",
        "..OKdO.........OPPpOOOpPPO.OO................",
        "..OKOO.........OTTO...OTTO...................",
        "..OO...........OTtO...OTtO...................",
        "...............OTtO...OTtO...................",
        "...............OTtO...OTtO...................",
        "...............OTtO...OTtO...................",
        "...............OTtO...OTtO...................",
        "...............OTTO...OTTO...................",
        "..............OTTtO...OTttO..................",
        ".............OTTTtO...OTttTO.................",
        ".............OOOOOO...OOOOOO.................",
    ]
    x0, y0 = _pinta_sprite(cx, by, spr, cmap, off_x=4)

    # Esfera negro-púrpura de Magia de Gravedad flotando sobre su palma extendida (IDLE 0)
    orb_x = x0 + 35
    orb_y = y0 + 18
    disc(orb_x, orb_y, 5, '#090412')
    for ang in range(0, 360, 18):
        rad = math.radians(ang)
        put(int(orb_x + 5.2 * math.cos(rad)), int(orb_y + 5.2 * math.sin(rad)), '#8c3cf0')
        if ang % 54 == 0:
            put(int(orb_x + 6.2 * math.cos(rad)), int(orb_y + 6.2 * math.sin(rad)), '#d69cff')
    if ANIM:
        RUNAS.append([orb_x, orb_y])
    else:
        glow(orb_x, orb_y, 9, '#8c3cf0', 0.55)


def dibuja_vanica(cx, by):
    """Vanica Zogratis (fiel al sprite VANICA): coronita dorada, cabello oscuro con flequillo
    sobre su parche negro en ojo derecho, sonrisa entusiasta, cuello de piel claro, capa negra,
    túnica/falda corta granate con cinturón, botas altas y aura de Magia de Sangre carmesí."""
    bl0, bl1, bl2 = PAL['blood']

    # Trazos dinámicos sinuosos de Magia de Sangre carmesí-negra alrededor (VANICA IDLE 4/5)
    for t in range(34):
        ang = t * 0.25
        sx = int(cx - 2 + math.cos(ang) * (13 + t * 0.25))
        sy = int(by - 8 - t * 1.15)
        put(sx, sy, bl1 if t % 3 else bl2)
        put(sx + 1, sy, '#18050c' if t % 2 else bl0)
    if ANIM:
        RUNAS.append([cx + 15, by - 32])
    else:
        glow(cx + 14, by - 30, 8, bl0, 0.45)

    cmap = {
        'O': '#0b0812',
        'G': '#f0c044', 'g': '#b2821e',
        'H': '#221a2a', 'h': '#3a2c48',
        'S': '#f0d4ce', 's': '#c8a6a0',
        'P': '#0d0912', 'E': '#1a1220',
        'R': '#b81c30', 'W': '#f8eef0',
        'F': '#d8dae4', 'f': '#9fa4b6', 'Z': '#eff1f8',
        'K': '#20222e', 'k': '#323646', 'd': '#14151e',
        'V': '#6c202c', 'v': '#922e3e', 'u': '#4a141e',
        'B': '#5a3a24',
    }
    # 35x42 px
    spr = [
        "..............O..O..O..............",
        ".............OGOGGGOGO.............",
        ".............OGGGGGGGGO............",
        "............OOOHHHHHHOOO...........",
        "...........OHHHhHHHHhHHHO..........",
        "..........OHHHHHHHHHHHHHHO.........",
        "..........OHHHhHHHhHHHHHHO.........",
        "..........OHHHSSSHHHHHHHHO.........",
        "..........OHHSeSSPPPHHHHHO.........",
        "..........OHHSSSSPPPSHHHHO.........",
        "..........OOHSSSWWWRSSSHHO.........",
        "...........OOHSSRRRSSSHHO..........",
        "............OOSSSSSSSOOO...........",
        "........OOOOOZZFFFFFZZOOOO.........",
        ".......OOZFFFFZFFFFFZFFFFZOO.......",
        "......OZFFFFfFFFFZFFFFFfFFFZO......",
        "......OOFfffFFFFFFFFFFFfffFO.......",
        ".....OKKOOOffOVVVvvVVVOffOOKKO.....",
        "....OKKKdKKOOOVVvvvvVVOOOOKdKKO....",
        "...OKKKdKKKKOKOVVVvvVVOKOKKKKdKO...",
        "...OKKdKKSSOKKOVVVVVVVOKKKSSKdKO...",
        "...OKKdKKOO..OKOBBBBBBBKOKOOOdKO...",
        "...OKKdKO....OKOBGGGBBBKOK...OdO...",
        "..OKKKdO.....OKOVVVVVVVKO..........",
        "..OKKdKO.....OKOVVvvvVVKO..........",
        "..OKKdO......OKOVVVvvVVKO..........",
        "..OKdKO......OKOVVuuuVVKO..........",
        "..OKdO.......OOOVVVVVVVOO..........",
        "..OKdO........OSSSSOSSSSO..........",
        "..OKdO........OSSSSOSSSSO..........",
        "..OKdO.......OOKKKO.OKKKOO.........",
        "..OKOO.......OKkKKO.OKKkKO.........",
        "..OO.........OKKKKO.OKKKKO.........",
        "............OKKKdKO.OKdKKKO........",
        "............OKKKdKO.OKdKKKO........",
        "............OKKdKKO.OKKdKKO........",
        "............OKKdKO...OKdKKO........",
        "............OKKdKO...OKdKKO........",
        "............OKKdKO...OKdKKO........",
        "...........OKKKdKO...OKdKKKO.......",
        "..........OKKKKdKO...OKdKKKKO......",
        "..........OOOOOOOO...OOOOOOOO......",
    ]
    _pinta_sprite(cx, by, spr, cmap)


dibuja_zenon(326, DY_TOP)
dibuja_dante(386, DY_TOP)
dibuja_vanica(446, DY_TOP)

# Pequeños braseros rúnicos bajos en los extremos de la terraza (sin tapar a la Tríada)
for fx in (300, 468):
    for yy in range(DY_TOP - 7, DY_TOP):
        put(fx, yy, SP0)
    if ANIM:
        FAROLES.append([fx, DY_TOP - 8, 9])
    else:
        put(fx, DY_TOP - 8, CR2)
        glow(fx, DY_TOP - 8, 6, CR1, 0.55)

CHIMENEA = [142, top_izq - 1]

# 6. Reflejo en el lago helado de Picas (sin astro duplicado en Monitor 2)
render_lago(lz, PAL['agua'], PAL['ola'], DESTELLOS, ANIM, mx=CX_ASTRO, reflejo_cols=(PAL['crimson'][2], PAL['ola'][0]), reflejo_astro=False)

# Grietas de hielo en las orillas inferiores del lago
r_ice = random.Random(71)
for hx_i in range(0, 120, 8):
    for dy in range(4, 18):
        if r_ice.random() < 0.6:
            over(hx_i + (dy % 3), HOR + dy, PAL['nieve'][1], 0.45)

# 7. Pinos nevados enmarcando los bordes extremos (sin invadir la escena)
def pino_nevado(px, by, h):
    p0, p1, sn = PAL['pino']
    for i in range(h):
        y = by - h + i
        hw = max(0, int(i * 0.32) - (2 if i % 5 == 4 else 0))
        for dx in range(-hw, hw + 1):
            put(px + dx, y, p0 if dx >= 0 else p1)
        if hw > 1 and i % 5 == 0:
            for dx in range(-hw, 1):
                over(px + dx, y, sn, 0.72)

for px, ph in ((14, 52), (34, 44), (54, 34), (590, 44), (612, 58), (630, 48)):
    pino_nevado(px, HOR + 2, ph)

aplica_vineta(lz, PAL['vig'])
out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
