#!/usr/bin/env python3
"""PixelZen Worlds - Harry Potter (Monitor Principal): Castillo de Hogwarts, Lago Negro y Quidditch."""
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
random.seed(934)

PALETAS = {
    'noche': dict(
        sky=['#040714', '#081024', '#0e1a36', '#16264c', '#203462', '#2c4478', '#3a548c', '#4a66a0', '#5c78b2', '#708cc2'],
        mont=('#1a2236', '#121828', '#0a0e18'),
        cliff=('#2a2634', '#1c1824', '#0e0c14', '#423c52'),
        wall=('#464254', '#2e2a3a', '#1b1824', '#666078'),
        roof=('#142034', '#1e2e4a', '#0c1220'),
        win=('#ffca58', '#ffeaa4'),
        agua='#091326',
        ola=('#ffd88c', '#42608c', '#182848'),
        pine=('#0b181a', '#142624', '#060e10'),
        wood=('#342218', '#1e120c'),
        shad='#07060c',
        vig=0.72,
        nube=['#223052', '#30426a', '#405482', '#526696', '#667aaa', '#1c2846'],
    ),
    'dorado': dict(
        sky=['#161230', '#261e44', '#3e2c58', '#623a64', '#8c4c64', '#b4625e', '#d67c56', '#ee9c56', '#fbc066', '#ffe08a'],
        mont=('#3c283e', '#2a1a2c', '#180e1c'),
        cliff=('#44343e', '#2e222a', '#181016', '#644e5a'),
        wall=('#76625c', '#524240', '#322626', '#9a8278'),
        roof=('#222a40', '#344060', '#141826'),
        win=('#ffd25e', '#fff0b2'),
        agua='#1e1c38',
        ola=('#ffd090', '#7e6c96', '#32284c'),
        pine=('#18221e', '#26342a', '#0c1410'),
        wood=('#4c3020', '#2c1a10'),
        shad='#09070e',
        vig=0.82,
        nube=['#5c3656', '#7e4862', '#a45e68', '#ca7866', '#ea9a68', '#462844'],
    ),
    'dia': dict(
        sky=['#2258a0', '#326eb6', '#4684ca', '#5e9cda', '#7ab4e6', '#98caf0', '#b6def4', '#d0ecf8', '#e6f4f8', '#f4f6ea'],
        mont=('#4a5e7c', '#384a66', '#28364e'),
        cliff=('#545664', '#3c3e4a', '#242630', '#767888'),
        wall=('#a29a94', '#78726e', '#4e4a48', '#c6beb6'),
        roof=('#263c5a', '#3a567e', '#18263a'),
        win=('#ffd268', '#fff4c8'),
        agua='#1d446a',
        ola=('#d8eef8', '#668eb8', '#2c547e'),
        pine=('#1e442c', '#2c603c', '#12281a'),
        wood=('#62402c', '#3e261a'),
        shad='#0a0912',
        vig=0.90,
        nube=['#ffffff', '#eef4fa', '#dce8f4', '#f6fafd', '#e4eef8', '#c8d8ec'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#88e6ff', '#ffc858'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 40, halo='#ffe6b4', base='#fffcf2', sombra='#dcd6c0', crater='#bbb49e', crater_hi='#cfc8b4'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe49c', centro='#fffef2', borde='#ffc45c', rayo='#ffe298'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#fff4d8', '#b8e8ff', '#b4b8f0'])

MX, MY, MR = 382, 74, 38
CX_ASTRO = MX if FASE == 'noche' else (MX + 12 if FASE == 'dorado' else MX - 36)
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#ffe6b4', base='#fffcf2', sombra='#dcd6c0', crater='#bbb49e', crater_hi='#cfc8b4')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, MX + 12, 178, 22, halo='#ffaa70', centro='#fff0dc', borde='#ff6646', rayo='#ff885e')
    else:
        dibuja_sol_estandar(lz, MX - 36, 84, 22, halo='#ffe49c', centro='#fffef2', borde='#ffc45c', rayo='#ffe298')

NUBES_DEF = [
    (74, 38, 150, PAL['nube'][0], 2),
    (254, 48, 160, PAL['nube'][1], 3),
    (430, 34, 140, PAL['nube'][2], 2),
    (168, 118, 160, PAL['nube'][3], 3),
    (360, 122, 130, PAL['nube'][4], 2),
    (526, 224, 110, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 1. Montanas de Escocia al horizonte (x=0..640, bajando suavemente en x>430 para HUD)
rm = Ruido(934)
M0, M1, M2 = PAL['mont']
for x in range(W):
    ramp = max(0.0, min(1.0, (x - 420) / 80.0))
    dip_r = int(34 * (0.5 - 0.5 * math.cos(math.pi * ramp)))
    ridge = int(208 + 30 * fbm(rm, x * 0.013 + 1.5) + dip_r)
    ridge = min(HOR, ridge)
    for y in range(ridge, HOR + 1):
        put(x, y, mix(M0, M2, (y - ridge) / max(1, HOR - ridge)))

# 2. Acantilado rocoso de Hogwarts anclado firme en el agua (x=68..438, base HOR=280)
CL_HI, CL_MD, CL_DK, CL_RIM = PAL['cliff']
rc = Ruido(941)
rc_y = Ruido(943)
for x in range(64, 444):
    u = (x - 64) / 380.0
    arch_cliff = int(42 * math.sin(u * math.pi) + 8 * fbm(rc, x * 0.04))
    top_c = HOR - arch_cliff
    for y in range(top_c, HOR + 1):
        n_c = 0.5 * fbm(rc, x * 0.06 + 3.0) + 0.5 * fbm(rc_y, y * 0.08)
        c = CL_RIM if y < top_c + 3 else (CL_HI if x < 176 else (CL_MD if n_c > 0.45 else CL_DK))
        put(x, y, c)

# 3. CASTILLO DE HOGWARTS (Gran Salon, Torre de Astronomia, torreones anclados en el acantilado)
W_HI, W_MD, W_DK, W_RIM = PAL['wall']
RF0, RF1, RF2 = PAL['roof']
WN0, WN1 = PAL['win']


def torre_hogwarts(cx, hw, top_y, base_y, con_h=34, wins=()):
    # Tejado conico de pizarra
    for dy in range(con_h):
        yy = top_y - con_h + dy
        w_c = max(0, int(hw * (dy / max(1, con_h))))
        for dx in range(-w_c, w_c + 1):
            put(cx + dx, yy, RF1 if dx < 0 else RF2)
    # Torre cilindrica anclada en la roca hasta base_y
    for yy in range(top_y, base_y + 1):
        for dx in range(-hw, hw + 1):
            c = W_RIM if dx == -hw else (W_HI if dx < 0 else (W_DK if dx > hw // 2 or yy % 8 == 0 else W_MD))
            put(cx + dx, yy, c)
    for vy in wins:
        if vy + 8 < base_y:
            for dy in range(7):
                for dx in range(-1, 2):
                    put(cx + dx, vy + dy, WN0 if FASE != 'dia' else '#5e7698')
            if ANIM:
                VENTANAS.append([cx, vy + 2])


# Torres y alas conectadas sin huecos flotantes
torre_hogwarts(124, 11, 166, 256, 30, wins=(184, 212))
torre_hogwarts(154, 14, 148, 254, 34, wins=(166, 198, 226))

# Gran Salon central (x=176..268, base y=254)
for x in range(176, 268):
    for y in range(198, 254):
        put(x, y, W_HI if x < 210 else (W_MD if y % 7 != 0 else W_DK))
# Tejado a dos aguas del Gran Salon + campanario central
for dy in range(22):
    y = 176 + dy
    hw_gh = int(dy * 2.1)
    for dx in range(-hw_gh, hw_gh + 1):
        put(222 + dx, y, RF1 if dx < 0 else RF2)
torre_hogwarts(222, 5, 160, 184, 18)
# Grandes ventanales ojivales del Gran Salon iluminados en oro
for wx in range(186, 260, 14):
    for dy in range(22):
        for dx in range(-2, 3):
            if dy > 2 or abs(dx) <= 1:
                put(wx + dx, 210 + dy, WN0 if FASE != 'dia' else '#5e7698')
    if ANIM:
        VENTANAS.append([wx, 218])

# Torre de Astronomia (alta) + Torre Ravenclaw + puente de piedra hasta la derecha del risco
torre_hogwarts(284, 16, 126, 252, 42, wins=(142, 174, 206))
# Puentes de piedra con 4 arcos uniendo Torre Astronomia (298) con Torre Este (364)
for x in range(298, 366):
    for y in range(214, 252):
        # Arcos vacios bajo el puente encima de la roca
        in_arch = y > 224 and ((x - 302) % 16) in range(4, 12) and y < 246
        if not in_arch:
            put(x, y, W_HI if y < 220 else W_MD)

torre_hogwarts(368, 12, 164, 258, 32, wins=(180, 210))
torre_hogwarts(398, 10, 188, 264, 26, wins=(204,))

# Cobertizo de Barcas al pie izquierdo del acantilado sobre la orilla (x=76..112, base=HOR)
for x in range(78, 110):
    for y in range(256, HOR + 1):
        put(x, y, PAL['wood'][0] if x < 98 else PAL['wood'][1])
for dy in range(12):
    hw_b = 4 + int(dy * 1.3)
    for dx in range(-hw_b, hw_b + 1):
        put(94 + dx, 244 + dy, RF1 if dx < 0 else RF2)
put(104, 266, WN1)
if ANIM:
    FAROLES.append([104, 266, 9])
else:
    glow(104, 266, 8, WN0, 0.65)

# 4. Lago Negro reflejando Hogwarts y la luna
render_lago(
    lz,
    PAL['agua'],
    PAL['ola'],
    DESTELLOS,
    ANIM,
    mx=CX_ASTRO,
    hor=HOR,
    reflejo_cols=(PAL['ola'][0], PAL['ola'][1]),
)

# Reflejo dorado calido sutil de las ventanas del Gran Salon en el agua
if FASE != 'dia':
    for dy in range(4, 52, 2):
        for wx in range(186, 260, 14):
            sx = wx + int(2 * math.sin(dy * 0.4 + wx))
            if (dy + wx) % 3 != 0:
                over(sx, HOR + dy, WN0, max(0.08, 0.34 - dy * 0.005))

# 5. Barcas de primer año cruzando el Lago Negro con faroles dorados (x=184, 294, 412)
for bx_b, by_b in ((184, 336), (294, 348), (408, 332)):
    for dx in range(-12, 13):
        put(bx_b + dx, by_b, PAL['wood'][0] if abs(dx) < 9 else PAL['wood'][1])
    for dx in range(-10, 11):
        put(bx_b + dx, by_b + 1, PAL['wood'][1])
    # Siluetas sentadas en la barca
    for px_s in (-4, 2):
        for dy in range(-5, 0):
            for dx in (-1, 0, 1):
                put(bx_b + px_s + dx, by_b + dy, PAL['shad'])
    # Farol en la proa
    put(bx_b + 9, by_b - 2, '#fff4c8')
    if ANIM:
        FAROLES.append([bx_b + 9, by_b - 2, 10])
    else:
        glow(bx_b + 9, by_b - 2, 9, WN0, 0.65)

# 6. Harry Potter volando en la Saeta de Fuego tras la Snitch Dorada en el cielo nocturno (cx=238, cy=88)
hx_q, hy_q = 232, 88
# Palo de la escoba + cerdas atras
for dx in range(-14, 13):
    put(hx_q + dx, hy_q + 4 - dx // 8, PAL['wood'][0])
for dy in range(-2, 3):
    for dx in range(-20, -13):
        put(hx_q + dx, hy_q + 5 + dy, '#7a5a30')
# Harry agachado + capa Gryffindor ondeando atras
spr_h = [
    '......KKKKK.....',
    '.....KKKKKKK....',
    '..KKKKKKKKKKK...',
    '.KKKKKKKKKKKKK..',
    'KKKK..KKKKKKKK..',
    '......KKKKKKKK..',
    '.......KKKKKK...',
]
pinta_sprite(lz, hx_q, hy_q + 3, spr_h, {'K': PAL['shad']})
# Bufanda escarlata al viento
for k in range(8):
    put(hx_q - 4 - k, hy_q - 1 + (k % 2), '#b82032')
# Snitch Dorada brillante delante de Harry (hx_q+32, hy_q-4)
sx_sn, sy_sn = hx_q + 30, hy_q - 5
put(sx_sn, sy_sn, '#fff29c')
put(sx_sn + 1, sy_sn, '#ffcf48')
put(sx_sn - 2, sy_sn - 2, '#fff8dc')
put(sx_sn + 3, sy_sn - 2, '#fff8dc')
if ANIM:
    RUNAS.append([sx_sn, sy_sn])
else:
    glow(sx_sn, sy_sn, 6, '#ffd458', 0.7)

# 7. Pinos del Bosque Prohibido en el margen izquierdo enmarcando el Lago (x=0..64)
P0, P1, P2 = PAL['pine']
for px_p, py_p, ph_p in ((14, 332, 76), (38, 316, 62), (58, 304, 50)):
    for i in range(ph_p):
        y = py_p - ph_p + i
        hw = max(0, int(i * 0.28) - (2 if i % 5 == 4 else 0))
        for dx in range(-hw, hw + 1):
            put(px_p + dx, y, P1 if dx < 0 else (P0 if dx < hw // 2 else P2))

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
