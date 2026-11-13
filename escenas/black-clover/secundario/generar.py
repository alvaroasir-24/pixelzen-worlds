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

# 5. Bastión / Terraza elevada de la TRÍADA OSCURA (x = 304..468, fuera de la zona HUD)
DX0, DX1, DY_TOP = 306, 466, HOR - 30
r_dais = Ruido(709)
for y in range(DY_TOP, HOR + 1):
    for x in range(DX0 - (y - DY_TOP) // 2, min(W, DX1 + (y - DY_TOP) // 2)):
        c = PAL['dais'][1] if r_dais(x * 0.16 + y * 0.22) > 0.46 else PAL['dais'][0]
        if (y - DY_TOP) % 9 == 0 and r_dais(x * 0.08) > 0.35:
            c = PAL['dais'][2]
        put(x, y, c)
for x in range(DX0, DX1 + 1):
    put(x, DY_TOP, PAL['dais'][2])
    if x % 8 < 4:
        put(x, DY_TOP - 1, PAL['nieve'][1])

# Pilares / monolitos oscuros ENTRE los miembros de la Tríada (para recortar nítidamente sus cabezas contra el cielo)
for px_t in (312, 360, 412, 460):
    for yy in range(DY_TOP - 46, DY_TOP):
        hw = 4 if yy > DY_TOP - 38 else max(1, 4 - (DY_TOP - 38 - yy) // 2)
        for dx in range(-hw, hw + 1):
            put(px_t + dx, yy, SP1 if dx < 0 else SP0)

def dibuja_zenon(cx, by):
    """Zenon Zogratis: abrigo alto oscuro, pelo alborotado, magia de Hueso blanco y Cubos Espaciales."""
    sp0, sp1, sp2 = PAL['spatial']
    bn0, bn1, bn2 = PAL['bone']
    # Abrigo largo negro-azulado con cuello alto y marca demoníaca
    for yy in range(by - 28, by):
        hw = 5 if yy < by - 14 else 7
        for dx in range(-hw, hw + 1):
            put(cx + dx, yy, SP1 if abs(dx) == hw else '#100e1c')
    # Cuello alto abierto en V
    for yy in range(by - 33, by - 26):
        for dx in (-4, -3, 3, 4):
            put(cx + dx, yy, '#22223a')
    # Cabeza y pelo oscuro alborotado
    for yy in range(by - 41, by - 31):
        for dx in range(-3, 4):
            put(cx + dx, yy, '#e8d8d0' if yy > by - 37 else '#141224')
    for dx, dh in ((-4, 3), (-2, 5), (0, 6), (2, 5), (4, 3)):
        for k in range(dh):
            put(cx + dx, by - 39 - k, '#161428')
    put(cx - 2, by - 34, sp1)  # marca demoníaca en mejilla
    put(cx - 1, by - 33, sp0)
    # Picos de Magia de Hueso blanco saliendo de hombros/espalda
    for sx, sy, ex, ey in ((cx - 5, by - 24, cx - 19, by - 37), (cx + 5, by - 22, cx + 18, by - 34), (cx - 4, by - 14, cx - 16, by - 18)):
        steps = 14
        for s in range(steps + 1):
            px = int(sx + (ex - sx) * s / steps)
            py = int(sy + (ey - sy) * s / steps)
            put(px, py, bn1 if s > steps // 2 else bn0)
            put(px, py + 1, bn2)
    # Cubos de Magia Espacial flotando alrededor
    for qx, qy, qr in ((cx - 16, by - 48, 5), (cx + 15, by - 49, 4)):
        for dy in range(-qr, qr + 1):
            for dx in range(-qr, qr + 1):
                if abs(dx) == qr or abs(dy) == qr:
                    put(qx + dx, qy + dy, sp2)
                else:
                    over(qx + dx, qy + dy, sp1, 0.45)
        if ANIM:
            RUNAS.append([qx, qy])
        else:
            glow(qx, qy, 7, sp1, 0.45)

def dibuja_dante(cx, by):
    """Dante Zogratis (centro): líder de la Tríada, corona dorada y esferas de Gravedad."""
    gr0, gr1, gr2 = PAL['grav']
    # Capa imperial ancha + cuerpo alto
    for yy in range(by - 32, by):
        hw = 7 + (yy - (by - 32)) // 6
        for dx in range(-hw, hw + 1):
            c = CR1 if abs(dx) >= hw - 1 else ('#160b18' if abs(dx) > 3 else '#2c182c')
            put(cx + dx, yy, c)
    # Hombreras doradas y cinturón real
    for dx in range(-8, 9):
        if abs(dx) >= 4:
            put(cx + dx, by - 31, GD0)
            put(cx + dx, by - 30, GD1)
        put(cx + dx, by - 17, GD1)
    # Espada oscura clavada al costado
    for yy in range(by - 30, by):
        put(cx + 9, yy, '#1a1420')
        put(cx + 10, yy, CR1)
    for dx in range(6, 14):
        put(cx + dx, by - 25, GD0)
    # Cabeza, barba oscura, pelo peinado atrás y corona
    for yy in range(by - 43, by - 33):
        for dx in range(-4, 5):
            if yy >= by - 35 and abs(dx) <= 3:
                put(cx + dx, yy, '#22141e')  # barba oscura
            else:
                put(cx + dx, yy, '#e6cfc2' if yy > by - 40 else '#22141e')
    for dx in (-4, -2, 0, 2, 4):
        put(cx + dx, by - 46, GD0)
        put(cx + dx, by - 45, CR2)
    for dx in range(-3, 4):
        put(cx + dx, by - 44, GD1)
    put(cx, by - 41, gr1)  # marca frontal
    # Esferas negras de Magia de Gravedad con halo carmesí + rocas flotando
    for gx, gy, gr_r in ((cx - 18, by - 42, 6), (cx + 17, by - 38, 5), (cx, by - 58, 4)):
        disc(gx, gy, gr_r, gr0)
        for ang in range(0, 360, 20):
            rad = math.radians(ang)
            put(int(gx + (gr_r + 1) * math.cos(rad)), int(gy + (gr_r + 1) * math.sin(rad)), gr1)
        if ANIM:
            RUNAS.append([gx, gy])
        else:
            glow(gx, gy, gr_r + 5, gr1, 0.55)

def dibuja_vanica(cx, by):
    """Vanica Zogratis: vestido gótico carmesí, coletas, parche y Magia de Sangre."""
    bl0, bl1, bl2 = PAL['blood']
    # Vestido gótico carmesí-negro
    for yy in range(by - 26, by):
        hw = 4 if yy < by - 16 else 4 + (yy - (by - 16)) // 3
        for dx in range(-hw, hw + 1):
            c = bl1 if yy > by - 14 and abs(dx) < hw - 1 else '#1a0a14'
            put(cx + dx, yy, c)
    # Cinta / faja roja
    for dx in range(-4, 5):
        put(cx + dx, by - 17, bl1)
    # Cabeza + coletas dobles visibles contra el cielo y parche en ojo derecho
    for yy in range(by - 37, by - 27):
        for dx in range(-3, 4):
            put(cx + dx, yy, '#eedad2' if yy > by - 34 else '#181022')
    # Coletas oscuras abiertas hacia los lados
    for dx_s in (-1, 1):
        for dy in range(10):
            put(cx + dx_s * (4 + dy // 4), by - 36 + dy, '#181022')
            put(cx + dx_s * (5 + dy // 4), by - 35 + dy, '#241832')
    put(cx + 1, by - 32, '#0a060c')  # parche
    put(cx - 1, by - 32, bl1)       # ojo rojo/marca
    # Espirales y orbes de Magia de Sangre carmesí
    for t in range(32):
        ang = t * 0.28
        sx = int(cx + math.cos(ang) * (10 + t * 0.3))
        sy = int(by - 12 - t * 1.15)
        put(sx, sy, bl1 if t % 3 else bl2)
        put(sx + 1, sy, bl0)
    for bx_s, by_s in ((cx - 13, by - 36), (cx + 14, by - 42)):
        disc(bx_s, by_s, 3, bl1)
        put(bx_s - 1, by_s - 1, bl2)
        if ANIM:
            RUNAS.append([bx_s, by_s])
        else:
            glow(bx_s, by_s, 6, bl0, 0.55)

dibuja_zenon(334, DY_TOP)
dibuja_dante(386, DY_TOP)
dibuja_vanica(438, DY_TOP)

# Runas/faroles en los bordes de la terraza
for fx in (312, 360, 412, 460):
    for yy in range(DY_TOP - 8, DY_TOP):
        put(fx, yy, SP0)
    if ANIM:
        FAROLES.append([fx, DY_TOP - 9, 9])
    else:
        put(fx, DY_TOP - 9, CR2)
        glow(fx, DY_TOP - 9, 6, CR1, 0.55)

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
