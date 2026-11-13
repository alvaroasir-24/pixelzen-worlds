#!/usr/bin/env python3
"""PixelZen - Tema Black Clover (Mejorado): Aldea de Hage, Cráneo del Demonio, Iglesia y Torre de Grimorios."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, en_zona, exporta_salida, exporta_sprites_si_aplica, fbm, mix, render_cielo,
    render_estrellas, render_lago, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(47)

PALETAS = {
    'noche': dict(
        sky=['#05030e', '#0d071c', '#180d2e', '#261442', '#381c56', '#4e2464', '#682e6a', '#863b6a', '#a64d68', '#c4666c'],
        mont=['#2a1d3a', '#20162e', '#170f22', '#100a18', '#090610'],
        mist=['#644672', '#4f365c', '#3c2848', '#2a1c34', '#1a1122'],
        skull=('#4e465c', '#383044', '#221c2c', '#0d0914'),
        gold=('#ffd458', '#c89228'),
        isla=('#0e0a16', '#181224', '#281e38', '#382a4e'),
        stone=('#342d40', '#484058', '#625874'),
        wall=('#5a4e5c', '#443a48'),
        timber=('#18101c', '#261a2c'),
        roof=('#3c1420', '#581e2c', '#742838'),
        tower_roof=('#182038', '#243050', '#34446e'),
        ivy=('#14281e', '#1e3c2c'),
        agua='#0a0616',
        ola=('#e08ea0', '#684278', '#2c183c'),
        suelo=('#0c0814', '#1e1428', '#120c1c', '#2a1c36'),
        vig=0.72,
        nube=['#422a54', '#583868', '#704476', '#8e547c', '#aa6882', '#382448'],
        rama=('#140a12', '#261420'),
        hoja={'l': '#e04858', 'c': '#b43044', 'm': '#801e32', 'd': '#4c1020', 'x': '#240812'},
        anti=('#e83848', '#ff9ea8'),
        sword=('#1c1824', '#342e40', '#0c0910'),
    ),
    'dorado': dict(
        sky=['#1a0a24', '#2c1034', '#461642', '#6a1e48', '#922846', '#ba363e', '#da4e38', '#f0703a', '#fc9846', '#ffc668'],
        mont=['#4c2438', '#3a1b2c', '#2a1320', '#1d0d16', '#12070e'],
        mist=['#dc6a58', '#ba5250', '#923e48', '#6a2c3c', '#441c2c'],
        skull=('#82686c', '#624c54', '#40303a', '#1a1018'),
        gold=('#ffe068', '#d89c28'),
        isla=('#1c1018', '#2a1822', '#422632', '#5a3442'),
        stone=('#52404a', '#6c5662', '#8a707c'),
        wall=('#9a7a72', '#7a5e5a'),
        timber=('#241216', '#381e22'),
        roof=('#5e1820', '#84242c', '#aa3238'),
        tower_roof=('#242840', '#363c5e', '#4c5480'),
        ivy=('#262820', '#3c402c'),
        agua='#240e24',
        ola=('#ffaa7c', '#984c66', '#4c2040'),
        suelo=('#180a12', '#341620', '#1e0e16', '#461e2a'),
        vig=0.80,
        nube=['#7a3452', '#a2445a', '#ca5a5a', '#ea7a58', '#fca260', '#642a46'],
        rama=('#1c0c10', '#34161a'),
        hoja={'l': '#ff6a50', 'c': '#d8423c', 'm': '#a0262c', 'd': '#64141c', 'x': '#32080e'},
        anti=('#ff4050', '#ffc0c6'),
        sword=('#261e2c', '#42364a', '#120c14'),
    ),
    'dia': dict(
        sky=['#2458a8', '#366ebc', '#4c86ce', '#66a0de', '#84b8ea', '#a4ceef', '#c4e0f0', '#deecea', '#f2eed8', '#faf2c8'],
        mont=['#5c6684', '#4c5470', '#3c445c', '#2e3448', '#222636'],
        mist=['#b6c8dc', '#9cb2ca', '#829ab6', '#6880a0', '#4e6688'],
        skull=('#a8a2ac', '#88808e', '#645c6c', '#2c2634'),
        gold=('#ffe46a', '#cca02c'),
        isla=('#263228', '#344634', '#486044', '#5c7a52'),
        stone=('#726c7c', '#8e8898', '#aca6b6'),
        wall=('#dfd2c8', '#bfb0a6'),
        timber=('#36282e', '#4e3c44'),
        roof=('#78242e', '#9a303a', '#be404a'),
        tower_roof=('#2c3c5c', '#405680', '#5874a4'),
        ivy=('#264830', '#386442'),
        agua='#264062',
        ola=('#d8e6f4', '#7e98ba', '#3e5478'),
        suelo=('#202e20', '#385034', '#283826', '#4a6842'),
        vig=0.90,
        nube=['#ffffff', '#f2f4f8', '#ffffff', '#e8eef4', '#faf8f2', '#e0e8f2'],
        rama=('#281c1a', '#44302c'),
        hoja={'l': '#e45850', 'c': '#be3c3c', 'm': '#90262c', 'd': '#5e141c', 'x': '#2e080e'},
        anti=('#e83848', '#ffd0d4'),
        sword=('#322c3c', '#4e465c', '#18141e'),
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

# 1. Cielo del Reino del Trébol + aurora carmesí/dorada nocturna
render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#e85068', '#f0b848'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 46, halo='#f0b8d0', base='#fff2f4', sombra='#d8bcc6', crater='#b696a4', crater_hi='#ccb2be'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 24, halo='#ffe294', centro='#fffdf0', borde='#ffbe52', rayo='#ffe088'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffe4ec', '#ffecc4', '#cbb8f0'])

MX, MY, MR = 362, 84, 46
CX_ASTRO = MX if FASE == 'noche' else (MX + 40 if FASE == 'dorado' else MX - 50)
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#f0b8d0', base='#fff2f4', sombra='#d8bcc6', crater='#b696a4', crater_hi='#ccb2be')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, MX + 40, 206, 24, halo='#ffaa68', centro='#fff2d8', borde='#ff6a38', rayo='#ff9450')
    else:
        dibuja_sol_estandar(lz, MX - 50, 96, 24, halo='#ffe294', centro='#fffdf0', borde='#ffbe52', rayo='#ffe088')

# 2. Nubes
NUBES_DEF = [
    (185, 62, 180, PAL['nube'][0], 3),
    (360, 108, 150, PAL['nube'][1], 3),
    (110, 168, 200, PAL['nube'][2], 3),
    (290, 210, 160, PAL['nube'][3], 3),
    (550, 248, 125, PAL['nube'][4], 2),
    (415, 52, 95, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 3. Cráneo Gigante del Demonio de Hage (anclado en los acantilados tras la Torre de Grimorios, x ~ 292)
sx_c, sy_c = 292, 186
sk_hi, sk_mid, sk_lo, sk_dk = PAL['skull']

for yy in range(sy_c + 34, HOR + 1):
    t = (yy - (sy_c + 34)) / max(1, HOR - (sy_c + 34))
    hw = int(34 + 30 * t)
    for dx in range(-hw, hw + 1):
        c = sk_mid if dx < 0 else sk_lo
        if (dx + yy) % 6 == 0:
            c = mix(c, sk_dk, 0.3)
        put(sx_c + dx, yy, c)

for side in (-1, 1):
    for i in range(68):
        t = i / 67.0
        cx = int(sx_c + side * (26 + 34 * math.sin(t * 1.45) - 18 * (t ** 2.1)))
        cy = int(sy_c - 18 - i * 1.15)
        r = max(1, int(9 * (1 - t * 0.85)))
        for dx in range(-r, r + 1):
            for dy in range(-r // 2 - 1, r // 2 + 2):
                if dx * dx + dy * dy <= r * r:
                    c = sk_hi if dx < -r // 3 else (sk_mid if dx < r // 3 else sk_lo)
                    if (cy // 4) % 2 == 0 and abs(dx) < r:
                        c = mix(c, sk_dk, 0.25)
                    put(cx + dx, cy + dy, c)

for dy in range(-35, 48):
    for dx in range(-44, 45):
        if dy < -4:
            # Bóveda craneal algo más angulosa y estrecha en las sienes
            w_cr = 37 - max(0, (-dy - 14)) * 0.72
            in_skull = abs(dx) <= w_cr and dy >= -33 + abs(dx) * 0.18
        elif dy <= 14:
            # Pómulos salientes bajo el arco superciliar
            w_pom = 36 + (6 if 4 <= dy <= 12 else 2)
            in_skull = abs(dx) <= w_pom
        else:
            w_jaw = 33 - (dy - 14) * 0.45
            in_skull = abs(dx) <= w_jaw and dy < 44
        if not in_skull:
            continue
        c = sk_hi if dx < -10 and dy < 0 else (sk_mid if dx < 14 else sk_lo)
        if -9 <= dy <= -6 and abs(dx) < 28:
            c = sk_hi if dx < 8 else sk_mid  # arco superciliar prominente
        if (dx + dy * 2) % 9 == 0 and dith(sx_c + dx, sy_c + dy, 0.55):
            c = mix(c, sk_dk, 0.3)
        # Musgo antiguo trepando por el lado izquierdo del cráneo
        if dx < -18 and dy > -14 and (dx * 3 + dy * 5) % 7 < 2:
            c = PAL['ivy'][1]
        # Grieta diagonal antigua en la frente
        if -26 <= dy <= -10 and abs(dx - (dy + 18) // 2 + 8) <= 0:
            c = sk_dk
        # Cuencas oculares angulosas (inclinadas hacia el entrecejo)
        tilt = (14 - abs(dx)) * 0.32
        eye_l = -23 <= dx <= -5 and (-5 + tilt <= dy <= 10 + tilt * 0.4)
        eye_r = 5 <= dx <= 23 and (-5 + tilt <= dy <= 10 + tilt * 0.4)
        nose = abs(dx) <= max(1, (dy - 12) // 2) and 12 <= dy <= 24
        teeth = dy >= 31 and abs(dx) < 20 and dx % 5 == 0
        if eye_l or eye_r or nose or teeth:
            c = sk_dk
        put(sx_c + dx, sy_c + dy, c)

# Estatua del Primer Rey Mago (Lumiere Silvamillion Clover) sobre el cráneo del demonio
stx, sty = sx_c, sy_c - 34
# Pedestal esculpido apoyado en la bóveda craneal
for dx in range(-7, 8):
    put(stx + dx, sty, sk_mid if dx < 0 else sk_lo)
    put(stx + dx, sty - 1, sk_hi)
# Silueta heroica del Primer Rey Mago con capa ondeante a la derecha y corona real
for dy in range(-17, -1):
    w_st = 3 if dy > -7 else (4 if dy > -12 else 2)
    for dx in range(-w_st, w_st + 1):
        c_st = sk_hi if dx < 0 else sk_mid
        if -17 <= dy <= -15 and abs(dx) <= 2:
            c_st = PAL['gold'][1] if dx % 2 == 0 else sk_hi
        put(stx + dx, sty + dy, c_st)
for dy in range(-12, -2):
    span = (-dy - 2) // 2 + 2
    for dx in range(3, span + 4):
        if dx + dy > -8:
            put(stx + dx, sty + dy, sk_lo if dx > 5 else sk_mid)
# Gran Espada de Luz apuntando al cielo en su mano izquierda
for k in range(1, 14):
    put(stx - 5, sty - 9 - k, PAL['gold'][0] if k > 3 else sk_hi)
put(stx - 6, sty - 12, PAL['gold'][1]); put(stx - 4, sty - 12, PAL['gold'][1])
if ANIM:
    RUNAS.append([stx - 4, sty - 25])
else:
    put(stx - 4, sty - 25, PAL['gold'][0])
    glow(stx - 4, sty - 25, 7, PAL['gold'][0], 0.6)

# 4. Colinas de Hage + silueta del Castillo del Trébol al fondo derecho
def rampa(x):
    return 1.0 if x < 430 else max(0.35, 1.0 - (x - 430) / 85 * 0.65)

CAPAS = [
    (244, 62, 13, 0.015, PAL['mont'][0], PAL['mist'][0]),
    (256, 48, 27, 0.021, PAL['mont'][1], PAL['mist'][1]),
    (268, 34, 39, 0.029, PAL['mont'][2], PAL['mist'][2]),
    (277, 20, 51, 0.038, PAL['mont'][3], PAL['mist'][3]),
]
crestas = []
for base, amp, seed, fr, col, mist in CAPAS:
    r, ra = Ruido(seed * 19), Ruido(seed * 41 + 3)
    c = []
    for x in range(W):
        n = fbm(r, x * fr + seed)
        am = 0.45 + 0.85 * ra(x * 0.013 + seed)
        c.append(base - amp * rampa(x) * am * n)
    crestas.append(c)
    for x in range(W):
        top = int(c[x])
        for y in range(top, HOR + 1):
            d = y - top
            cc = mix(col, mist, 0.25 * (d / max(1, HOR - top)) ** 2.0)
            put(x, y, cc)
        for k in range(1, 16):
            if dith(x, top + k, (1 - k / 16) * 0.38):
                over(x, top + k, mist, 0.5)

# Cerro rocoso continuo hasta el borde derecho bajo el Castillo Real del Trébol (x = 452..640)
for x in range(452, W):
    t_h = max(0.0, 1.0 - max(0.0, (535 - x)) / 83.0)
    ridge_k = HOR - int(22 * min(1.0, t_h * 1.15) * (0.85 if x > 565 else 1.0))
    for yy in range(ridge_k, HOR + 1):
        put(x, yy, PAL['mont'][3] if yy < ridge_k + 4 else PAL['mont'][4])
for yy in range(HOR - 36, HOR - 18):
    for xx in range(506, 562):
        put(xx, yy, PAL['mont'][2] if xx < 534 else PAL['mont'][3])
for cx_k, h_k, w_k in ((512, 46, 9), (526, 58, 11), (542, 50, 9), (556, 40, 7)):
    for yy in range(HOR - h_k, HOR - 18):
        for dx in range(-w_k // 2, w_k // 2 + 1):
            put(cx_k + dx, yy, PAL['mont'][1] if dx <= 0 else PAL['mont'][3])
    for i in range(15):
        hw = max(0, int((w_k // 2 + 1) * (1 - i / 14.0)))
        for dx in range(-hw, hw + 1):
            put(cx_k + dx, HOR - h_k - i, PAL['mont'][0] if dx <= 0 else PAL['mont'][2])
    if FASE != 'dia':
        put(cx_k, HOR - h_k + 7, '#ffe090')

# Pinos oscuros puntiagudos en la base de las colinas
r_pin = random.Random(77)
for x in range(250, W, 6):
    if r_pin.random() < 0.72:
        by = int(crestas[3][x]) + 4
        ph = r_pin.randint(9, 17)
        for i in range(ph):
            hw = (i * 4) // max(1, ph)
            for dx in range(-hw, hw + 1):
                put(x + dx, by - ph + i, PAL['mont'][4])

# 5. Colina continua de la Aldea de Hage desde el borde izquierdo (x: 0..260)
ST0, ST1, ST2 = PAL['stone']
WL0, WL1 = PAL['wall']
TM0, TM1 = PAL['timber']
RF0, RF1, RF2 = PAL['roof']
TF0, TF1, TF2 = PAL['tower_roof']
WARM = '#ffb854'

for x in range(0, 260):
    if x < 72:
        top_y = HOR - 24 - int(8 * math.cos(x / 72.0 * 1.57))
    elif x < 218:
        top_y = HOR - 12
    else:
        top_y = HOR - 12 + int((x - 218) / 42.0 * 12)
    for y in range(top_y, HOR + 1):
        c = PAL['isla'][3] if y <= top_y + 2 else (PAL['isla'][2] if y <= top_y + 6 else (PAL['isla'][1] if (x + y) % 5 else PAL['isla'][0]))
        put(x, y, c)

# Iglesia Gótica de Hage (x ~ 86..162) con contrafuertes, rosetón y aguja
IX0, IW, IH = 86, 76, 34
IY0 = HOR - 12 - IH

for yy in range(IY0 - 18, IY0):
    for x in range(IX0 + 10, IX0 + 16):
        put(x, yy, ST0 if x > IX0 + 13 else ST1)
for x in range(IX0 + 9, IX0 + 17):
    put(x, IY0 - 19, ST2)
CHIMENEA = [IX0 + 13, IY0 - 20]

for yy in range(IY0, IY0 + IH):
    for x in range(IX0, IX0 + IW):
        if yy >= IY0 + IH - 10:
            c_s = ST1 if ((x * 5 + yy * 7) // 6) % 3 == 0 else ST0
            if (x + yy * 3) % 11 == 0:
                c_s = ST2
            put(x, yy, c_s)
        else:
            put(x, yy, WL0 if x < IX0 + IW // 2 else WL1)
# Contrafuertes laterales de piedra
for cx_b in (IX0 - 2, IX0 + IW - 2):
    for yy in range(IY0 + 6, HOR - 12):
        for dx in range(4):
            put(cx_b + dx, yy, ST2 if dx < 2 else ST0)

# Tejado rojizo + hastial central gótico con puerta arqueada y rosetón
for i in range(20):
    hw = max(2, int((IW // 2 + 5) * (1 - i / 19.0)))
    cx = IX0 + IW // 2
    yy = IY0 - i
    for x in range(cx - hw, cx + hw + 1):
        c = RF2 if x < cx - hw // 3 else (RF1 if x < cx + hw // 3 else RF0)
        put(x, yy, c)

# Campanario de la iglesia + rosetón central
bx_i, bw_i, bh_i = IX0 + IW // 2 - 9, 18, 24
by_i = IY0 - 16 - bh_i
for yy in range(by_i, by_i + bh_i):
    for x in range(bx_i, bx_i + bw_i):
        put(x, yy, WL0 if x < bx_i + bw_i // 2 else WL1)
for i in range(20):
    hw = max(0, int((bw_i // 2 + 2) * (1 - i / 19.0)))
    for x in range(bx_i + bw_i // 2 - hw, bx_i + bw_i // 2 + hw + 1):
        put(x, by_i - i, RF2 if x < bx_i + bw_i // 2 else RF0)
put(bx_i + bw_i // 2, by_i - 21, PAL['gold'][0])
put(bx_i + bw_i // 2 - 1, by_i - 20, PAL['gold'][0])
put(bx_i + bw_i // 2 + 1, by_i - 20, PAL['gold'][0])

# Puerta doble arqueada de la iglesia + rosetón gótico
dx_c = IX0 + IW // 2
for yy in range(HOR - 24, HOR - 12):
    for dx in range(-4, 5):
        put(dx_c + dx, yy, TM0 if dx == 0 else TM1)
for dy in range(-3, 4):
    for dx in range(-3, 4):
        if dx * dx + dy * dy <= 9:
            put(dx_c + dx, IY0 + 7 + dy, PAL['gold'][0] if (abs(dx) + abs(dy)) <= 1 else PAL['roof'][2])

# Vidrieras góticas de la iglesia
for vx in (IX0 + 10, IX0 + 22, IX0 + 52, IX0 + 64):
    wy = IY0 + 8
    if ANIM:
        VENTANAS.append([vx, wy])
    else:
        for dy in range(7):
            put(vx, wy + dy, WARM)
            put(vx + 1, wy + dy, WARM)
        glow(vx, wy + 3, 5, WARM, 0.42)

# Torre de Grimorios (x ~ 182..210) con hiedra oscura y círculo mágico superior
TX0, TW, TH = 182, 28, 62
TY0 = HOR - 12 - TH
for yy in range(TY0, TY0 + TH):
    for x in range(TX0, TX0 + TW):
        c = ST2 if x < TX0 + 8 else (ST1 if x < TX0 + 20 else ST0)
        if (x // 4 + yy // 4) % 3 == 0:
            c = mix(c, ST0, 0.25)
        # Hiedra trepadora
        if (x - TX0) < 7 and (yy + x * 2) % 7 < 3 and yy > TY0 + 18:
            c = PAL['ivy'][0 if (x + yy) % 2 else 1]
        put(x, yy, c)
for x in range(TX0 - 2, TX0 + TW + 2):
    put(x, TY0, TM0)
    put(x, TY0 + 1, TM1)

for wy in (TY0 + 10, TY0 + 27, TY0 + 44):
    vx = TX0 + TW // 2 - 1
    if ANIM:
        VENTANAS.append([vx, wy])
    else:
        for dy in range(5):
            put(vx, wy + dy, WARM)
            put(vx + 1, wy + dy, WARM)
        glow(vx, wy + 2, 4, WARM, 0.4)

for i in range(34):
    hw = max(0, int((TW // 2 + 4) * (1 - i / 33.0)))
    yy = TY0 - i
    cx = TX0 + TW // 2
    for x in range(cx - hw, cx + hw + 1):
        put(x, yy, TF2 if x < cx - hw // 3 else (TF1 if x < cx + hw // 3 else TF0))

gx_t, gy_t = TX0 + TW // 2, TY0 - 39
if ANIM:
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            RUNAS.append([gx_t + dx, gy_t + dy])
else:
    disc(gx_t, gy_t, 2, PAL['anti'][1])
    glow(gx_t, gy_t, 9, PAL['anti'][0], 0.65)

# Faroles de hierro en la aldea
for fx, fy in ((72, HOR - 12), (170, HOR - 12), (222, HOR - 10)):
    for yy in range(10):
        put(fx, fy - yy, TM0)
    if ANIM:
        FAROLES.append([fx, fy - 10, 7])
    else:
        put(fx, fy - 10, '#fff0c4')
        glow(fx, fy - 10, 8, '#f09c44', 0.65)

# 6. Lago oscuro con reflejo del Cráneo del Demonio y la aldea
render_lago(lz, PAL['agua'], PAL['ola'], DESTELLOS, ANIM, mx=CX_ASTRO)

# 7. Rama retorcida gótica con pétalos carmesí arriba izquierda (silueta espigada, distinta a las demás)
lz.rama([(0, 32), (38, 22), (76, 40), (118, 28), (156, 44)], 4.2, 1.2, PAL['rama'][0], PAL['rama'][1])
lz.rama([(38, 22), (62, 6), (92, 0)], 2.8, 1.0, PAL['rama'][0], PAL['rama'][1])
lz.rama([(14, 34), (36, 74), (48, 108)], 3.0, 1.0, PAL['rama'][0], PAL['rama'][1])

H_COLS = PAL['hoja']
r_ho = random.Random(88)
for cx, cy, rad in ((38, 20, 14), (76, 38, 13), (118, 26, 14), (156, 44, 12), (62, 8, 13), (44, 96, 12), (96, 32, 11)):
    for _ in range(rad * 18):
        a = r_ho.random() * 6.283
        d = r_ho.random() ** 0.7 * rad
        px_, py_ = int(cx + math.cos(a) * d), int(cy + math.sin(a) * d * 0.75)
        if not en_zona(px_, py_):
            put(px_, py_, H_COLS['l' if py_ < cy else ('c' if d < rad * 0.6 else 'm')])
if not ANIM:
    for px_p, py_p in ((82, 58), (132, 48), (64, 72), (104, 66), (48, 120)):
        put(px_p, py_p, H_COLS['l'])

# Orillas inferiores + roca con la Espada Matademonios de Asta y Grimorio flotante de 5 hojas
for cx_s in range(0, 106):
    h_s = int(28 * math.cos(cx_s / 106 * 1.57))
    for yy in range(H - h_s, H):
        put(cx_s, yy, PAL['suelo'][0] if (cx_s + yy) % 3 else PAL['suelo'][1])
for cx_s in range(W - 64, W):
    h_s = int(18 * math.cos((W - 1 - cx_s) / 64 * 1.57))
    for yy in range(H - h_s, H):
        put(cx_s, yy, PAL['suelo'][2] if (cx_s + yy) % 3 else PAL['suelo'][3])

# Roca + Espada Matademonios ancha de Asta (x ~ 46)
sw_d, sw_m, sw_dk = PAL['sword']
for dy in range(-12, 6):
    hw = 18 - abs(dy)
    for dx in range(-hw, hw + 1):
        put(46 + dx, H - 10 + dy, ST1 if dy < -2 else ST0)

for i in range(48):
    yy = H - 14 - i
    cx = 46 + int(i * 0.16)
    w_blade = 5 if i < 34 else 2
    if 34 <= i <= 36:
        w_blade = 11
    for dx in range(-w_blade, w_blade + 1):
        c = sw_m if dx < -1 else (sw_d if dx < w_blade else sw_dk)
        if abs(dx) <= 1 and i < 33:
            c = sw_dk
        if i >= 37 and abs(dx) <= 1:
            c = PAL['roof'][1]
        put(cx + dx, yy, c)
    if 6 <= i <= 28 and i % 5 == 0:
        if ANIM:
            RUNAS.append([cx, yy])
        else:
            put(cx, yy, PAL['anti'][1])
            glow(cx, yy, 3, PAL['anti'][0], 0.55)

# Atril de piedra + Grimorio abierto de Cinco Hojas junto a la espada (x ~ 78, y ~ H - 24)
gx_b, gy_b = 78, H - 24
for yy in range(gy_b + 4, H):
    for dx in range(-5, 6):
        put(gx_b + dx, yy, ST1 if dx < 0 else ST0)
for dy in range(-7, 5):
    tilt = abs(dy) // 4
    for dx in range(-9, 10):
        if abs(dx) >= 8:
            put(gx_b + dx, gy_b + dy + tilt, sw_dk)  # cubierta negra del grimorio
        elif abs(dx) == 0:
            put(gx_b + dx, gy_b + dy, sw_dk)  # lomo central
        elif abs(dy) == 6 or abs(dy) == 4 and dy > 0:
            put(gx_b + dx, gy_b + dy, PAL['gold'][0])
        else:
            put(gx_b + dx, gy_b + dy, '#e8dcc4' if abs(dx) < 7 else sw_m)
# Emblema carmesí del Trébol de 5 hojas sobre la página
for dx, dy in ((0, -2), (-2, -1), (2, -1), (-2, 1), (2, 1), (0, 2)):
    put(gx_b - 4 + dx, gy_b - 1 + dy, PAL['anti'][0])
if ANIM:
    RUNAS.append([gx_b, gy_b - 9])
else:
    glow(gx_b, gy_b - 2, 7, PAL['anti'][0], 0.55)

# Tréboles brillantes en las orillas inferiores
for tx, ty in ((16, H - 18), (90, H - 12), (W - 36, H - 14), (W - 20, H - 10)):
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        put(tx + dx, ty + dy, PAL['gold'][0])
    if ANIM:
        RUNAS.append([tx, ty])

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
             chimenea=CHIMENEA, destellos=DESTELLOS, barca=[196, HOR - 12], luna=[MX, MY, MR])
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
