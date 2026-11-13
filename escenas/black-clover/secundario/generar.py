#!/usr/bin/env python3
"""PixelZen Worlds - Black Clover (Monitor 2): Reino de Picas y Asta invocando la espada de su Grimorio."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, exporta_salida, exporta_sprites_si_aplica, fbm, mix, pinta_sprite, render_cielo,
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

# Risco helado amplio bajo TODO el Castillo de Picas (meseta plana en HOR-26 de x=96..316 hasta x=64..348 en HOR)
r_cliff = Ruido(701)
for y in range(HOR - 26, HOR + 1):
    t = (y - (HOR - 26)) / 26.0
    x_l = int(96 - t * 34)
    x_r = int(316 + t * 34)
    for x in range(max(0, x_l), min(W, x_r)):
        n = r_cliff(x * 0.14 + y * 0.21)
        c = CS2 if y < HOR - 23 else (CS1 if n > 0.48 else CS0)
        if y < HOR - 20 and r_cliff(x * 0.09) > 0.54:
            c = mix(c, PAL['nieve'][1], 0.55)
        put(x, y, c)

# Muralla exterior y almenas de Picas (hundida hasta HOR - 22 dentro del risco)
for x in range(114, 298):
    for yy in range(HOR - 60, HOR - 21):
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

# 5. Bastión / Terraza real de la TRÍADA OSCURA (x = 292..474, superficie firme sin nieve sobre las botas)
DX0, DX1, DY_TOP = 292, 476, HOR - 24
r_dais = Ruido(709)
for y in range(DY_TOP, HOR + 1):
    for x in range(DX0 - (y - DY_TOP) // 2, min(W, DX1 + (y - DY_TOP) // 2)):
        c = PAL['dais'][1] if r_dais(x * 0.16 + y * 0.22) > 0.46 else PAL['dais'][0]
        if (y - DY_TOP) % 8 == 0 and r_dais(x * 0.08) > 0.35:
            c = PAL['dais'][2]
        put(x, y, c)
for x in range(DX0, DX1 + 1):
    put(x, DY_TOP, PAL['dais'][2])
    if x % 10 < 3 and (x < 304 or x > 466):
        put(x, DY_TOP - 1, PAL['nieve'][1])


def dibuja_asta(cx, by):
    """Asta (Toro Negro): cabello ceniza en picos, cinta negra con emblema dorado, manto de los Toros Negros,
    grimorio de 5 hojas abierto en ángulo flotando a su lado y empuñando la gran espada Danma al sacarla."""
    cmap = {
        'O': '#0b0812',
        'H': '#dad4ce', 'h': '#f4f0ec', 'g': '#989290',
        'B': '#161420', 'G': '#f0c044',
        'S': '#f0cbb6', 's': '#c69a84', 'E': '#28b858',
        'K': '#1c1b28', 'k': '#2d2b3e', 'd': '#11101a',
        'R': '#c82038', 'r': '#881224',
        'T': '#302c3c',
    }
    spr = [
        "..............O..O...O..O.............",
        "...........OOOHhOOhOOhOOhOOO..........",
        "..........OHHHHHHHHHHHHHHHHHO.........",
        "...........OHhHHgHHHHHgHHhHO..........",
        "...........OBBBBBBGGBBBBBBO...........",
        "...........OHHSSSSSSSSSSHHO...........",
        "............OHSSEsSSsESSHO............",
        "............OSSSSSSSSSSSSO............",
        ".............OSSSSssSSSSO.............",
        "..........OOOOKKKKKKKKKKOOOO..........",
        ".........OKKkKGKKKKKKKKGKkKKO.........",
        "........OKKKKRRRRKKKKRRRRKKKKO........",
        ".....OOOOKKdKKKKKKKKKKKKKKKKdKKO......",
        "....OSSOKKKOOKKKKKKKKKKKKKKO.OSSO.....",
        ".....OO.OSSO.OKKRRRRRRRKKOO...OO......",
        ".............OKKRRRRRRRKKO............",
        ".............OKKKKKKKKKKKO............",
        ".............OTTTTOOTTTTTO............",
        "............OTTTTTOOTTTTTO............",
        "............OTTTTO..OTTTTO............",
        "............OKKKKO..OKKKKO............",
        "............OKkKKO..OKKkKO............",
        "............OKKKKO..OKKKKO............",
        "...........OKKKKRO..ORKKKKO...........",
        "...........OOOOOOO..OOOOOOO...........",
    ]
    w_max = max(len(r) for r in spr)
    spr = [r.ljust(w_max, '.') for r in spr]

    # Grimorio negro de 5 hojas abierto en perspectiva (V inclinada flotando junto a su mano)
    gx_g, gy_g = cx - 28, by - 18
    for dy in range(-8, 8):
        shift = abs(dy) // 3
        for dx in range(-10, 11):
            if abs(dx) > 9 - shift // 2:
                continue
            y_page = gy_g + dy - abs(dx) // 4
            if abs(dx) == 9 - shift // 2 or dy in (-8, 7):
                c_g = '#09070e'
            elif dx == 0:
                c_g = PAL['gold'][1]
            elif dx < 0:
                c_g = '#1c1526' if abs(dx) > 6 else '#e4dce8'
            else:
                c_g = '#1c1526' if dx > 6 else '#d6cedc'
            put(gx_g + dx, y_page, c_g)
    # Pequeño trébol carmesí de 5 hojas en el lomo/aura del grimorio
    for tx, ty in ((0, -2), (-2, -4), (2, -4), (-1, 0), (1, 0)):
        put(gx_g + tx, gy_g + ty, CR2)

    # Gran espada Danma saliendo desde el interior del grimorio directo a la mano izquierda extendida de Asta
    hx_s, hy_s = cx - 14, by - 11
    bx_tip, by_tip = gx_g - 14, gy_g - 26
    steps_sw = 28
    for k in range(steps_sw + 1):
        u_s = k / float(steps_sw)
        sx_p = int(round(hx_s + (bx_tip - hx_s) * u_s))
        sy_p = int(round(hy_s + (by_tip - hy_s) * u_s))
        bw_s = 1 if u_s > 0.90 else (3 if u_s > 0.18 else 2)
        for d_b in range(-bw_s, bw_s + 1):
            col_b = CR2 if abs(d_b) == bw_s else ('#38324a' if d_b == 0 else '#181522')
            if u_s < 0.14:
                col_b = '#9c8236' if abs(d_b) == 0 else '#14121c'
            put(sx_p + d_b, sy_p, col_b)
        if k % 4 == 0:
            over(sx_p + bw_s + 1, sy_p - 1, CR1, 0.7)

    pinta_sprite(lz, cx, by, spr, cmap)
    if ANIM:
        RUNAS.append([gx_g, gy_g - 2])
        FAROLES.append([bx_tip + 6, by_tip + 6, 11])
    else:
        glow(gx_g, gy_g - 2, 12, CR1, 0.58)
        glow(bx_tip + 6, by_tip + 6, 8, CR2, 0.45)


dibuja_asta(396, DY_TOP)

# Pequeños braseros rúnicos bajos en los extremos de la terraza
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
