#!/usr/bin/env python3
"""PixelZen Worlds - Fittoa (Bloqueo): Santuario del Teletransporte de Buena."""
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
FASE = os.environ.get('PZ_FASE', 'dorado')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(4079)

PALETAS = {
    'noche': dict(
        sky=['#05081a', '#0a102c', '#121a42', '#1c2658', '#2a366c', '#3c4880', '#505c92', '#6874a4', '#8490b8', '#a0acd0'],
        mont=['#243252', '#1a2540', '#121b30', '#0c1222'],
        mist=['#50648c', '#3e4e72', '#2c3a58', '#1c263c'],
        nieve=('#dce8ff', '#8ea6d0'), stone=('#141c2c', '#222c44', '#364462', '#526488'),
        roof=('#3c1c28', '#5e2c38', '#844048'),
        mana=('#24a89c', '#54f0e4', '#c8fff8'), win='#f4bc68',
        agua='#0a142a', ola=('#78d8d0', '#38628c', '#182c4c'),
        vig=0.76, nube=['#2c385e', '#3a4a74', '#4c5e8a', '#60749e', '#768ab2', '#263050'],
        pino=('#08101c', '#121e2e', '#324864'),
    ),
    'dorado': dict(
        sky=['#120e2c', '#1e1842', '#32245a', '#4e326e', '#724478', '#985878', '#be7070', '#de8e68', '#f2b068', '#ffd482'],
        mont=['#4e3858', '#3c2a44', '#2c1e34', '#1e1424'],
        mist=['#d88874', '#b66c68', '#92525c', '#6c3a4c'],
        nieve=('#fff0e4', '#cc9ea8'), stone=('#221c2c', '#362c40', '#50425c', '#746280'),
        roof=('#642428', '#923838', '#c05248'),
        mana=('#2ab6aa', '#5cf2e4', '#d4fffa'), win='#ffd078',
        agua='#1e1834', ola=('#f6b478', '#84587c', '#3e244c'),
        vig=0.82, nube=['#663c5e', '#8c5068', '#b46868', '#d88664', '#f2aa6c', '#52304e'],
        pino=('#141622', '#202434', '#685060'),
    ),
    'dia': dict(
        sky=['#1a4e96', '#2864ae', '#3c7cc4', '#5896d8', '#78b0e6', '#9ac8f0', '#b8dcf6', '#d4ebf8', '#eaf4fa', '#f6f8ec'],
        mont=['#547294', '#425c7c', '#324864', '#24344c'],
        mist=['#c4daf0', '#a8c2dc', '#8ea8c6', '#728cb0'],
        nieve=('#ffffff', '#cce0f6'), stone=('#283244', '#3c485e', '#586882', '#7a8ca8'),
        roof=('#7c3430', '#a84840', '#ce6458'),
        mana=('#24b4a8', '#68f4e8', '#e0fffa'), win='#ffe28a',
        agua='#245084', ola=('#b8e6f4', '#689cc4', '#365884'),
        vig=0.92, nube=['#ffffff', '#eef6fc', '#ffffff', '#e4f0fa', '#fafaf6', '#d8e8f4'],
        pino=('#142822', '#224034', '#467452'),
    ),
}
PAL = PALETAS[FASE]
ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE)
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#a8c4f4', base='#f6f4ec', sombra='#bcc4d8', crater='#9aa4bc', crater_hi='#b2bcd0'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe49c', centro='#fffef2', borde='#ffc45c', rayo='#ffdf8a'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS)

MX, MY = 468, 78
CX_ASTRO = MX if FASE == 'noche' else (MX - 32 if FASE == 'dorado' else MX - 64)
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, CX_ASTRO, MY, 38, halo='#a8c4f4', base='#f6f4ec', sombra='#bcc4d8', crater='#9aa4bc', crater_hi='#b2bcd0')
    else:
        dibuja_sol_estandar(lz, CX_ASTRO, MY - (14 if FASE == 'dia' else -18), 22, halo='#ffe49c', centro='#fffef2', borde='#ffc45c', rayo='#ffdf8a')

render_nubes(lz, [(95, 58, 175, PAL['nube'][0], 3), (300, 46, 160, PAL['nube'][1], 3), (520, 108, 145, PAL['nube'][2], 2), (185, 168, 180, PAL['nube'][3], 2)], NUBES, ANIM)

# Cordilleras de Fittoa con cumbres nevadas
for base, amp, seed, col, mist, nv in ((236, 84, 11, PAL['mont'][0], PAL['mist'][0], True), (252, 62, 19, PAL['mont'][1], PAL['mist'][1], True), (268, 42, 27, PAL['mont'][2], PAL['mist'][2], False)):
    r, ra = Ruido(seed * 17), Ruido(seed * 31 + 3)
    for x in range(W):
        n = fbm(r, x * 0.016 + seed)
        ag = 1 - abs(2 * n - 1)
        top = int(base - amp * (0.4 + 0.85 * ra(x * 0.012)) * (0.65 * ag + 0.35 * n))
        for y in range(top, HOR + 1):
            d = y - top
            cc = mix(col, mist, 0.25 * (d / max(1, HOR - top)) ** 1.8)
            if nv and top < base - amp * 0.42 and d < (base - amp * 0.42 - top) * 0.48:
                cc = mix(PAL['nieve'][0], PAL['nieve'][1], min(1.0, d / 11.0))
            put(x, y, cc)

# Orilla boscosa y cabaña del guardabosques a la izquierda
ST0, ST1, ST2, ST3 = PAL['stone']
for x in range(0, 210):
    gy = HOR - 16 + int(math.sin(x * 0.03) * 5) + max(0, (x - 165) // 2)
    for y in range(gy, HOR + 4):
        put(x, y, PAL['pino'][1] if (x + y) % 3 else PAL['pino'][0])

# Cabaña rústica con tejado a dos aguas y chimenea
for y in range(240, 272):
    for x in range(62, 114):
        put(x, y, ST2 if x < 98 else ST1)
for y in range(224, 242):
    hw = 30 - (241 - y) * 14 // 17
    for x in range(88 - hw, 88 + hw + 1):
        put(x, y, PAL['roof'][2] if (y % 3 == 0) else PAL['roof'][1])
for y in range(214, 232):
    for x in range(100, 107):
        put(x, y, ST1)
CHIMENEA = [103, 213]
for wx, wy in ((70, 248), (82, 248), (94, 248), (76, 258)):
    if ANIM:
        VENTANAS.append([wx, wy])
    else:
        for dy in range(4):
            for dx in range(2):
                put(wx + dx, wy + dy, PAL['win'])

# Promontorio central con Altar del Monolito de Teletransporte (x=250..390)
for y in range(HOR - 10, HOR + 6):
    pad = (HOR + 6 - y)
    for x in range(246 + pad, 394 - pad):
        put(x, y, ST1 if (y % 4 == 0 or (x + y) % 9 == 0) else ST0)
for step, sx0, sx1, sy in ((0, 268, 372, HOR - 14), (1, 282, 358, HOR - 19)):
    for y in range(sy, sy + 5):
        for x in range(sx0, sx1):
            put(x, y, ST3 if y == sy else ST2)

# Dos pilares rúnicos y dintel curvo + cristal de maná flotante en el centro
for px in (294, 336):
    for y in range(178, HOR - 19):
        for dx in range(11):
            put(px + dx, y, ST3 if dx < 3 else (ST2 if dx < 8 else ST1))
        if ANIM and y % 9 == 4 and 188 < y < HOR - 24:
            RUNAS.append([px + 5, y])
        elif not ANIM and y % 9 == 4 and 188 < y < HOR - 24:
            put(px + 5, y, PAL['mana'][1])

for y in range(160, 180):
    hw = 34 - max(0, (172 - y) * 2)
    for x in range(320 - hw, 320 + hw + 1):
        put(x, y, ST3 if y < 165 else ST2)

# Cristal flotante de teletransporte (x=320, y=206..228)
for y in range(198, 232):
    r_c = max(1, 6 - abs(y - 215) * 6 // 17)
    for dx in range(-r_c, r_c + 1):
        col = PAL['mana'][2] if abs(dx) <= 1 else (PAL['mana'][1] if dx < 2 else PAL['mana'][0])
        put(320 + dx, y, col)
        if ANIM and y in (208, 215, 222) and dx == 0:
            RUNAS.append([320, y])
if not ANIM:
    glow(320, 215, 16, PAL['mana'][1], 0.45)

# Faroles de piedra junto al santuario
for fx, fy in ((274, HOR - 21), (366, HOR - 21), (132, 264)):
    for yy in range(fy, fy + 8):
        put(fx, yy, ST1)
    if ANIM:
        FAROLES.append([fx, fy - 1, 8])
    else:
        put(fx, fy - 1, PAL['win'])
        glow(fx, fy - 1, 6, PAL['win'], 0.55)

# Pinos enmarcando izquierda y derecha
def pino(px, by, h):
    for i in range(h):
        y = by - h + i
        hw = max(0, int(i * 0.34) - (2 if i % 6 == 5 else 0))
        for dx in range(-hw, hw + 1):
            put(px + dx, y, PAL['pino'][0] if dx >= 0 else PAL['pino'][1])

for px, ph in ((16, 60), (38, 48), (156, 44), (566, 46), (594, 62), (620, 52)):
    pino(px, HOR + 2, ph)

render_lago(lz, PAL['agua'], PAL['ola'], DESTELLOS, ANIM, mx=CX_ASTRO, reflejo_cols=('#ffe6a0', '#f4ead2'))
aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS, chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, 38])
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
