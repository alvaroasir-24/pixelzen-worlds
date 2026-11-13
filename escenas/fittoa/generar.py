#!/usr/bin/env python3
"""PixelZen Mushoku - Tema 1 (Mejorado): Región de Fittoa y Aldea de Buena."""
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
random.seed(11)

PALETAS = {
    'noche': dict(
        sky=['#050717', '#090c24', '#0f1336', '#181c46', '#242557', '#332d68', '#463878', '#5c4382', '#784e84', '#975e85', '#b57288', '#d28e88', '#e5ab92'],
        mont=['#433d73', '#343364', '#262852', '#191d3e', '#0e132a'],
        mist=['#8a78a8', '#70669c', '#53528a', '#3a3d74', '#262b5c'],
        nieve=('#e4e0f4', '#a8b0d8'), filo='#c4e2ec',
        pino1='#08101c', pino2='#111d2c', pinorim='#263c52',
        isla=('#0a101e', '#131d30', '#2a3e54'),
        stone=('#192136', '#242e48', '#394868'),
        plaster=('#2b324e', '#3a4262'),
        timber=('#0e1222', '#171c32'),
        roof=('#141c38', '#1f2b50', '#384b7a'),
        roof2=('#261a34', '#382444', '#56395e'),
        bruma='#6884a8', agua='#070c22',
        ola=('#8ac6cc', '#4e6fa0', '#2d3b70'),
        cana=('#060b18', '#192a3e', '#080e1c', '#22344a'),
        vig=0.72, boat='#080b1c', arch_ref='#1d4a60',
        nube=['#4e5090', '#6d6ea8', '#866898', '#ba7e8e', '#cc8c8e', '#434886'],
        rama=('#0a1018', '#1a2738'),
        hoja={'l': '#488c82', 'c': '#2f6866', 'm': '#1c474c', 'd': '#112f38', 'x': '#091b24'},
        arch=('#1a2438', '#27354e', '#3d5172'),
        mana=('#5ef2e4', '#28b4b8'),
        cascada=('#7cb8d4', '#b8e8f4'),
        loto=('#18363e', '#d8a8c8'),
    ),
    'dorado': dict(
        sky=['#121d4e', '#1e2c68', '#303e82', '#4c4c94', '#72569a', '#985c98', '#be6290', '#dc6e80', '#f0826c', '#fb9f60', '#ffc06c', '#ffd988', '#ffecad'],
        mont=['#8a5988', '#6f487c', '#54396b', '#3c2b54', '#261c3a'],
        mist=['#f2a288', '#d88088', '#b06688', '#80507c', '#523c66'],
        nieve=('#fff2e2', '#e4b8c4'), filo='#ffdca8',
        pino1='#1c1824', pino2='#2c2434', pinorim='#543c4e',
        isla=('#1e1928', '#2e2638', '#644a58'),
        stone=('#342a3e', '#4a3c54', '#6e586e'),
        plaster=('#9a786e', '#c69e86'),
        timber=('#241624', '#3c2432'),
        roof=('#2c3258', '#3e4876', '#6674a2'),
        roof2=('#6e323c', '#944248', '#be6058'),
        bruma='#dca098', agua='#2b224c',
        ola=('#f2c098', '#a0729a', '#4c3e76'),
        cana=('#1a141e', '#4c3648', '#1e1824', '#5c4254'),
        vig=0.82, boat='#181224', arch_ref='#38425e',
        nube=['#b888a6', '#e49c98', '#f2ab8a', '#ffca98', '#ffd89c', '#9276a4'],
        rama=('#1c121e', '#3a2632'),
        hoja={'l': '#e6d27a', 'c': '#b8ad56', 'm': '#7c8240', 'd': '#4c5630', 'x': '#2c3422'},
        arch=('#342c44', '#4e425e', '#766480'),
        mana=('#72f6e6', '#3ac2c4'),
        cascada=('#e8b8a8', '#fff0d8'),
        loto=('#363c32', '#f4b8c0'),
    ),
    'dia': dict(
        sky=['#1a58b2', '#2668c4', '#387ad2', '#4c8cde', '#649ee6', '#7eb2ec', '#98c4f2', '#b0d4f4', '#c6e0f2', '#d8eae8', '#e6f0e4', '#f0f3dc', '#f6f2d4'],
        mont=['#789cc0', '#5e87ae', '#477294', '#345c72', '#224a52'],
        mist=['#d8eaf4', '#c2dced', '#a6cadc', '#86b4c6', '#689aa8'],
        nieve=('#ffffff', '#d6e8f4'), filo='#ffffff',
        pino1='#123828', pino2='#1b4d36', pinorim='#3e7854',
        isla=('#1c4430', '#2b5e40', '#548c60'),
        stone=('#525e6e', '#6d7c8e', '#94a4b4'),
        plaster=('#dfd4b8', '#f2ead4'),
        timber=('#3a281c', '#583d2a'),
        roof=('#2c4a76', '#3d6498', '#6892c2'),
        roof2=('#8c3c36', '#b04e44', '#d46e5e'),
        bruma='#cbe2ee', agua='#1d5d8e',
        ola=('#d2ebf8', '#7ab6dc', '#3878a8'),
        cana=('#0e3020', '#2e6442', '#123826', '#427a52'),
        vig=0.92, boat='#2c1e16', arch_ref='#285e7c',
        nube=['#ffffff', '#f5f9ff', '#ffffff', '#fff8ee', '#ffffff', '#e8f2fc'],
        rama=('#241812', '#422e22'),
        hoja={'l': '#b4df7c', 'c': '#7bc05e', 'm': '#49924c', 'd': '#2b6438', 'x': '#183e26'},
        arch=('#526070', '#6d7d90', '#96a8b8'),
        mana=('#68f4e8', '#2cb8c0'),
        cascada=('#9ed8f2', '#ffffff'),
        loto=('#2c6e48', '#f8d2dc'),
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

# 1. Cielo + sprites
render_cielo(lz, PAL['sky'], SKYM, FASE)
exporta_sprites_si_aplica(lz, lambda: dibuja_luna_estandar(lz, 104, 104, 46), lambda: dibuja_sol_estandar(lz, 104, 104, 24))
render_estrellas(lz, FASE, ANIM, ESTRELLAS)

MX, MY, MR = 352, 84, 46
CX_ASTRO = MX if FASE == 'noche' else (MX + 90 if FASE == 'dorado' else MX - 70)
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR)
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, MX + 90, 210, 24)
    else:
        dibuja_sol_estandar(lz, MX - 70, 95, 24)

# 2. Nubes y grullas lejanas
NUBES_DEF = [
    (160, 62, 190, PAL['nube'][0], 3),
    (380, 100, 150, PAL['nube'][1], 3),
    (90, 170, 210, PAL['nube'][2], 3),
    (270, 215, 170, PAL['nube'][3], 3),
    (560, 250, 120, PAL['nube'][4], 2),
    (430, 56, 90, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)
if not ANIM:
    for gx, gy in ((300, 128), (318, 118), (334, 134), (292, 150)):
        for k in range(5):
            put(gx - k, gy + k // 2 - (k // 3), '#121028')
            put(gx + k, gy + k // 2 - (k // 3), '#121028')
        put(gx, gy + 1, '#121028')

# 3. Cordillera del Dragón Rojo + cascada lejana
def rampa(x):
    return 1.0 if x < 420 else max(0.3, 1.0 - (x - 420) / 90 * 0.7)

CAPAS = [
    (236, 116, 1, 0.011, PAL['mont'][0], PAL['mist'][0], True),
    (249, 98, 2, 0.015, PAL['mont'][1], PAL['mist'][1], False),
    (260, 82, 3, 0.020, PAL['mont'][2], PAL['mist'][2], False),
    (270, 62, 4, 0.027, PAL['mont'][3], PAL['mist'][3], False),
    (279, 39, 5, 0.036, PAL['mont'][4], PAL['mist'][4], False),
]
crestas = []
for base, amp, seed, fr, col, mist, nieve in CAPAS:
    r, ra, rt = Ruido(seed * 17), Ruido(seed * 53 + 1), Ruido(seed * 31)
    c = []
    for x in range(W):
        n = fbm(r, x * fr * 1.5 + seed)
        agudo = 1 - abs(2 * n - 1)
        am = 0.30 + 0.95 * ra(x * 0.011 + seed) ** 1.3
        c.append(base - amp * rampa(x) * am * (0.62 * agudo + 0.38 * n))
    crestas.append(c)
    for x in range(W):
        top = int(c[x])
        pend = c[min(W - 1, x + 2)] - c[max(0, x - 2)]
        for y in range(top, HOR + 1):
            d = y - top
            cc = mix(col, mist, 0.26 * (d / max(1, (HOR - top))) ** 2.2)
            if nieve and top < base - amp * 0.50 * rampa(x) and d < (base - amp * 0.50 * rampa(x) - top) * 0.62 + (3 if dith(x, y, 0.5) else 0) - 2 * abs(rt(x * 0.2) - 0.5) * 6:
                cc = mix(PAL['nieve'][0], PAL['nieve'][1], min(1, d / 14.0))
            elif d > 5 and (x + 2 * y) % 11 == 0 and dith(x, y, 0.8):
                cc = mix(cc, '#000010', 0.18)
            elif d > 8 and (y // 9 + (x // 23)) % 5 == 0 and dith(x, y, 0.35):
                cc = mix(cc, mist, 0.13)
            if d < 2:
                cc = mix(cc, PAL['filo'], 0.30 if pend < 0 else 0.07)
            put(x, y, cc)
        for k in range(1, 26):
            if dith(x, top + k, (1 - k / 26) * 0.5):
                over(x, top + k, mist, 0.65)
    by = int(base + 2)
    for x in range(W):
        for k in range(-5, 6):
            if dith(x, by + k, (1 - abs(k) / 6) * 0.30):
                over(x, by + k, mist, 0.5)

# Cascada orgánica en el desfiladero distante (x ~ 358) cayendo hacia la bruma
CAS_X = 358
cas_top = int(crestas[2][CAS_X]) + 10
for yy in range(cas_top, HOR - 1):
    prog = (yy - cas_top) / max(1, HOR - cas_top)
    desv = int(math.sin(prog * 4.5) * 1.4)
    w_c = 1 + int(prog * 3)
    for dx in range(-w_c, w_c + 1):
        es_espuma = (yy + dx * 3) % 4 == 0 or yy > HOR - 9 or abs(dx) == w_c
        over(CAS_X + desv + dx, yy, PAL['cascada'][1] if es_espuma else PAL['cascada'][0], 0.62 if abs(dx) < w_c else 0.35)
for dx in range(-10, 11):
    for dy in range(-4, 2):
        if dith(CAS_X + dx, HOR + dy, 0.50 * (1 - abs(dx) / 11)):
            over(CAS_X + dx, HOR + dy, PAL['cascada'][1], 0.58)

# Pinos de Fittoa
def pino(x, by, h, col, rim):
    for i in range(h):
        y = by - h + i
        hw = max(0, int(i * 0.33) - (2 if i % 5 == 4 else 0))
        for dx in range(-hw, hw + 1):
            put(x + dx, y, col)
        if hw > 1 and i % 5 != 4:
            over(x - hw, y, rim, 0.55)
    for i in range(4):
        put(x, by + i, col)

r5 = random.Random(77)
for x in range(0, W, 4):
    if r5.random() < 0.8:
        pino(x + r5.randint(-1, 1), int(crestas[4][x]) + 6, r5.randint(9, 20), PAL['pino1'], PAL['pinorim'])
for x in range(0, W, 7):
    if r5.random() < 0.6:
        pino(x, int(crestas[3][x]) + 5, r5.randint(7, 13), PAL['pino2'], PAL['pinorim'])

# 4. Colina de Buena / Mansión Greyrat, Torre de Ranoa y muelle
WARM = '#f4bc68'
MANA_HI, MANA_LO = PAL['mana']
ST0, ST1, ST2 = PAL['stone']
PL0, PL1 = PAL['plaster']
TM0, TM1 = PAL['timber']
RF0, RF1, RF2 = PAL['roof']
RT0, RT1, RT2 = PAL['roof2']

for y in range(HOR - 36, HOR + 1):
    t = (HOR - y) / 36.0
    ww = int(236 * (1 - t ** 1.7) / 2)
    for x in range(205 - ww, 205 + ww):
        c = PAL['isla'][0] if (x + y) % 5 else PAL['isla'][1]
        if (HOR - y) > 33:
            c = PAL['isla'][2]
        put(x, y, c)

# Muelle de piedra bajo la mansión + enredaderas de musgo
for x in range(134, 278):
    for yy in range(HOR - 10, HOR + 1):
        c = ST1 if ((x // 5 + yy // 3) % 2 == 0) else ST0
        if yy == HOR - 10:
            c = ST2
        if (x * 7 + yy * 3) % 19 == 0 and yy > HOR - 8:
            c = PAL['isla'][2]
        put(x, yy, c)

def tejado_dos_aguas(cx, y_base, w, h, cols):
    c0, c1, c2 = cols
    for i in range(h):
        t = i / max(1, h - 1)
        hw = max(1, int((w / 2) * (1 - t)))
        yy = y_base - i
        for x in range(cx - hw, cx + hw + 1):
            c = c2 if x < cx - hw // 3 else (c1 if x < cx + hw // 3 else c0)
            if (x // 3 + yy // 2) % 3 == 0 and i > 1:
                c = mix(c, c0, 0.30)
            if i == h - 1:
                c = c2
            put(x, yy, c)
    for x in range(cx - w // 2 - 2, cx + w // 2 + 3):
        put(x, y_base + 1, TM0)
        if x % 2 == 0:
            put(x, y_base, c2)

def fachada_entramado(x0, y0, w, h, stone_h=10, win_rows=1):
    for yy in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if yy >= y0 + h - stone_h:
                put(x, yy, ST1 if (x // 4 + yy // 3) % 2 else ST0)
            else:
                put(x, yy, PL1 if x < x0 + w // 2 else PL0)
    for x in (x0, x0 + w - 1, x0 + w // 2):
        for yy in range(y0, y0 + h - stone_h):
            put(x, yy, TM0)
    for yy in (y0, y0 + h - stone_h):
        for x in range(x0, x0 + w):
            put(x, yy, TM0)
    if w >= 24 and h - stone_h >= 12:
        for d in range(min(w // 2 - 2, h - stone_h - 2)):
            put(x0 + 2 + d, y0 + 2 + d, TM1)
            put(x0 + w - 3 - d, y0 + 2 + d, TM1)
    cols_v = list(range(x0 + 5, x0 + w - 5, 10))
    for r in range(win_rows):
        wy = y0 + 4 + r * 11
        if wy + 5 >= y0 + h - stone_h + 4:
            break
        for vx in cols_v:
            if abs(vx - (x0 + w // 2)) <= 2:
                continue
            if ANIM:
                VENTANAS.append([vx, wy])
            else:
                for dy in range(4):
                    put(vx, wy + dy, WARM)
                    put(vx + 1, wy + dy, WARM)
                glow(vx, wy + 2, 4, WARM, 0.35)
            for dx_ in range(-1, 3):
                put(vx + dx_, wy - 1, TM0)

# Mansión Greyrat
MX0, MW, MH = 162, 68, 36
MY0 = HOR - 10 - MH
for yy in range(MY0 - 24, MY0 - 2):
    for x in range(MX0 + 10, MX0 + 17):
        put(x, yy, ST0 if x > MX0 + 13 else ST1)
for x in range(MX0 + 9, MX0 + 18):
    put(x, MY0 - 25, ST2)
CHIMENEA = [MX0 + 13, MY0 - 26]
fachada_entramado(MX0, MY0, MW, MH, stone_h=12, win_rows=2)
# Portón de roble con dintel de piedra
for yy in range(HOR - 19, HOR - 10):
    for dx in range(-3, 4):
        put(MX0 + MW // 2 + dx, yy, TM0 if dx in (-3, 0, 3) else TM1)
for dx in range(-4, 5):
    put(MX0 + MW // 2 + dx, HOR - 20, ST2)
tejado_dos_aguas(MX0 + MW // 2, MY0, MW + 10, 22, (RT0, RT1, RT2))
fachada_entramado(MX0 + MW // 2 - 9, MY0 - 11, 18, 12, stone_h=0, win_rows=1)
tejado_dos_aguas(MX0 + MW // 2, MY0 - 11, 22, 10, (RT0, RT1, RT2))

# Torre del mago / observatorio (con óculo mágico superior)
TX0, TW, TH = 232, 24, 54
TY0 = HOR - 10 - TH
for yy in range(TY0, TY0 + TH):
    for x in range(TX0, TX0 + TW):
        c = ST2 if x < TX0 + 6 else (ST1 if x < TX0 + 16 else ST0)
        if (x // 4 + yy // 4) % 3 == 0:
            c = mix(c, ST0, 0.25)
        put(x, yy, c)
for x in range(TX0 - 2, TX0 + TW + 2):
    put(x, TY0, TM0)
    put(x, TY0 + 1, TM1)
for wy in (TY0 + 7, TY0 + 23, TY0 + 37):
    vx = TX0 + TW // 2 - 1
    if ANIM:
        VENTANAS.append([vx, wy])
    else:
        for dy in range(4):
            put(vx, wy + dy, WARM)
            put(vx + 1, wy + dy, WARM)
        glow(vx, wy + 2, 4, WARM, 0.4)
# Óculo rúnico de la torre
if ANIM:
    RUNAS.append([TX0 + TW // 2, TY0 - 10])
else:
    disc(TX0 + TW // 2, TY0 - 10, 2, MANA_HI)
    glow(TX0 + TW // 2, TY0 - 10, 5, MANA_LO, 0.45)

for i in range(29):
    hw = max(0, int((TW // 2 + 4) * (1 - i / 28)))
    yy = TY0 - i
    for x in range(TX0 + TW // 2 - hw, TX0 + TW // 2 + hw + 1):
        put(x, yy, RF2 if x < TX0 + TW // 2 - hw // 3 else (RF1 if x < TX0 + TW // 2 + hw // 3 else RF0))
for yy in range(TY0 - 35, TY0 - 28):
    put(TX0 + TW // 2, yy, '#d8b058')
put(TX0 + TW // 2, TY0 - 36, '#fff0b0')

# Cabaña izquierda + noria + embarcadero de madera en el lago
CX0, CW, CH = 114, 42, 24
CY0 = HOR - 10 - CH
fachada_entramado(CX0, CY0, CW, CH, stone_h=8, win_rows=1)
tejado_dos_aguas(CX0 + CW // 2, CY0, CW + 8, 15, (RF0, RF1, RF2))
WX, WY, WR = 104, HOR - 8, 9
for a in range(24):
    ang = a * math.pi * 2 / 24
    put(WX + round(math.cos(ang) * WR), WY + round(math.sin(ang) * WR), TM1)
for dx in range(-WR, WR + 1):
    put(WX + dx, WY, TM0)
for dy in range(-WR, WR + 1):
    put(WX, WY + dy, TM0)
disc(WX, WY, 2, ST2)

# Pequeño embarcadero extendiéndose desde el muro (x: 266..294) + barriles
for x in range(264, 294):
    put(x, HOR - 3, TM1)
    put(x, HOR - 2, TM0)
for px_p in (270, 282, 292):
    for yy in range(HOR - 5, HOR + 4):
        put(px_p, yy, TM0)
for bx_c, bw_c, bh_c in ((274, 4, 4), (279, 3, 3)):
    for yy in range(HOR - 3 - bh_c, HOR - 3):
        for xx in range(bx_c, bx_c + bw_c):
            put(xx, yy, TM1 if xx == bx_c else TM0)
# Farol en la punta del embarcadero
def farol_pie(x, y):
    for yy in range(10):
        put(x, y - yy, TM0)
    for xx in range(-2, 3):
        put(x + xx, y - 11, TM0)
    if ANIM:
        FAROLES.append([x, y - 9, 6])
        return
    put(x, y - 9, WARM)
    put(x, y - 10, WARM)
    glow(x, y - 9, 6, WARM, 0.5)

farol_pie(156, HOR - 10)
farol_pie(228, HOR - 10)
farol_pie(292, HOR - 3)

for yy in range(HOR - 10, HOR):
    for x in range(MX0 + 26 - (HOR - yy) // 2, MX0 + 38 + (HOR - yy) // 2):
        if (x + yy) % 3 == 0:
            over(x, yy, ST2, 0.7)
for x0, ww in ((64, 22), (306, 26)):
    for _ in range(ww * 3):
        put(x0 + random.randint(-ww, ww), HOR - random.randint(0, 6), PAL['isla'][0])

for y in range(HOR - 22, HOR + 1):
    for x in range(W):
        if dith(x, y, ((y - (HOR - 22)) / 22.0) ** 1.6 * 0.34):
            over(x, y, PAL['bruma'], 0.55)

# 5. Lago
render_lago(lz, PAL['agua'], PAL['ola'], DESTELLOS, ANIM, mx=CX_ASTRO)

# 6. Arco rúnico antiguo de los Seis Mundos (con enredaderas y gema flotante)
AX, ABY = 435, 340
AR0, AR1, AR2 = PAL['arch']

def arco_runico(cx, by, plot, record_runes=False):
    h, sep = 50, 42
    for dx in (-sep // 2, sep // 2):
        for yy in range(by - h, by):
            for t in range(-4, 5):
                c = AR2 if t <= -2 else (AR0 if t >= 2 else AR1)
                if (yy + t) % 7 == 0 and t in (-1, 0, 1):
                    c = AR0
                plot(cx + dx + t, yy, c)
        for yy in range(by - h - 2, by - h + 1):
            for t in range(-6, 7):
                plot(cx + dx + t, yy, AR2 if yy == by - h - 2 else AR0)
        for ry in range(by - h + 7, by - 9, 7):
            for rx, rry in ((cx + dx, ry), (cx + dx - 1, ry + 1), (cx + dx + 1, ry + 1), (cx + dx, ry + 2)):
                if record_runes:
                    if ANIM:
                        RUNAS.append([rx, rry])
                    else:
                        plot(rx, rry, MANA_HI)
                else:
                    plot(rx, rry, MANA_LO)
    r_ext, r_int = sep // 2 + 6, sep // 2 - 4
    cy_a = by - h + 2
    for dy in range(-r_ext, 3):
        for dx in range(-r_ext, r_ext + 1):
            d = math.hypot(dx, dy * 1.15)
            if r_int <= d <= r_ext:
                c = AR2 if d > r_ext - 2 else (AR0 if d < r_int + 2 else AR1)
                if (dx + dy) % 6 == 0:
                    c = AR0
                plot(cx + dx, cy_a + dy, c)
    for dx in (-sep // 2, sep // 2):
        for yy in range(by - h - 7, by - h - 2):
            hw = 3 - (by - h - 2 - yy) // 2
            for t in range(-hw, hw + 1):
                plot(cx + dx + t, yy, AR2 if t < 0 else AR0)
    ky = cy_a - r_ext + 2
    for dy in range(-4, 5):
        hw = 4 - abs(dy)
        for dx in range(-hw, hw + 1):
            col = MANA_HI if (abs(dx) + abs(dy) <= 2) else AR0
            if record_runes and abs(dx) + abs(dy) <= 2:
                if ANIM:
                    RUNAS.append([cx + dx, ky + dy])
                else:
                    plot(cx + dx, ky + dy, MANA_HI)
            else:
                plot(cx + dx, ky + dy, col)
    # Cristal central suspendido dentro del arco
    if record_runes:
        cy_c = by - h + 14
        if not ANIM:
            for dy in range(-4, 5):
                hw = max(0, 2 - abs(dy) // 2)
                for dx in range(-hw, hw + 1):
                    plot(cx + dx, cy_c + dy, MANA_HI)
            glow(cx, cy_c, 10, MANA_HI, 0.55)
        else:
            for dy in range(-2, 3):
                for dx in range(-1, 2):
                    if abs(dx) + abs(dy) <= 2:
                        RUNAS.append([cx + dx, cy_c + dy])
    if not ANIM and record_runes:
        glow(cx, ky, 9, MANA_HI, 0.5)

mask = {}
arco_runico(AX, ABY, lambda x, y, c: mask.__setitem__((x, y), lz.get(x, y) if False else (int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)) if isinstance(c, str) else c), record_runes=False)
for dy in range(0, 76):
    if dy % 4 == 3:
        continue
    sh = 1 if (dy // 2) % 2 else -1
    a = max(0.1, 0.62 - dy * 0.006)
    for (x, y), c in mask.items():
        if y == ABY - 1 - dy and 0 <= x + sh < W and ABY + dy < H:
            over(x + sh, ABY + dy, mix(c, PAL['arch_ref'], 0.35), a)
for dx in (-21, 21):
    for yy in range(ABY - 5, ABY + 1):
        for x in range(AX + dx - 9, AX + dx + 10):
            put(x, yy, AR2 if yy == ABY - 5 else (AR1 if yy == ABY - 4 else AR0))
    for x in range(AX + dx - 15, AX + dx + 16):
        if abs(x - (AX + dx)) > 8 and dith(x, ABY + 1, 0.6):
            over(x, ABY + 1, '#78c4c8', 0.75)
arco_runico(AX, ABY - 5, put, record_runes=True)

# 7. Barca con viajero mago (guiño Roxy/Rudeus)
BX, BY = 300, 318
for i in range(40):
    t = i / 39.0
    for k in range(0, 4):
        put(BX - 20 + i, BY + k + int((2 * t - 1) ** 2 * -3), PAL['boat'])
for i in range(-20, 21):
    put(BX + i, BY + 4 - int((i / 20.0) ** 2 * 3), PAL['boat'])
for x in range(BX - 8, BX + 6):
    put(x, BY - 1, PAL['boat'])
for yy in range(BY - 16, BY - 1):
    put(BX + 12, yy, PAL['boat'])
if ANIM:
    FAROLES.append([BX + 12, BY - 17, 11])
else:
    for ox, oy in ((0, 0), (0, -1), (-1, 0), (1, 0)):
        put(BX + 12 + ox, BY - 17 + oy, WARM)
    glow(BX + 12, BY - 17, 11, WARM, 0.75)
for yy in range(BY - 9, BY - 1):
    for dx in range(-4 + (BY - 1 - yy) // 3, 3 - (BY - 1 - yy) // 4):
        put(BX - 3 + dx, yy, PAL['boat'])
for x in range(BX - 8, BX + 3):
    put(x, BY - 10, PAL['boat'])
for k in range(1, 6):
    for x in range(BX - 6 + k // 2, BX + 1 - k // 2):
        put(x, BY - 10 - k, PAL['boat'])
# Remo inclinado hacia el agua
for k in range(1, 9):
    put(BX - 1 - k, BY - 3 + k, PAL['boat'])
for d in range(5, 60, 2):
    for x in range(BX + 12 - (3 if d < 30 else 5), BX + 12 + (3 if d < 30 else 5)):
        if dith(x, BY + 6 + d, 0.8 - d * 0.012):
            over(x + (1 if (d // 2) % 2 else -1), BY + 6 + d, WARM, 0.8 - d * 0.01)
for x in range(BX - 24, BX + 26):
    if x % 3:
        over(x, BY + 8, '#203652', 0.7)

# 8. Cañas, rocas, nenúfares y fuegos fatuos
rcn = random.Random(5)
def cana(x, h, curva, col, borde):
    for i in range(h):
        xx = x + int(curva * (i / h) ** 2 * 10)
        put(xx, H - 1 - i, col)
        if i % 2 == 0:
            put(xx + 1, H - 1 - i, col)
        if i > 4:
            over(xx - 1, H - 1 - i, borde, 0.5)
    if h > 40:
        for k in range(8):
            put(x + int(curva * 10), H - h - k, '#2a221c')
            put(x + int(curva * 10) + 1, H - h - k, '#2a221c')

for x in list(range(0, 150, 3)) + list(range(520, 640, 4)):
    if rcn.random() < 0.8:
        cana(x + rcn.randint(-2, 2), rcn.randint(20, 90) - (30 if x > 440 else 0), rcn.uniform(-1, 1), PAL['cana'][0], PAL['cana'][1])
for cx0, ww in ((40, 60), (610, 40)):
    for x in range(cx0 - ww, cx0 + ww):
        t = (x - cx0) / ww
        hh = int(18 * (1 - t * t) ** 0.8)
        for k in range(hh):
            put(x, H - 1 - k, PAL['cana'][2] if k < hh - 2 else PAL['cana'][3])

# Nenúfares sobre el agua
for lx, ly, lr in ((174, 344, 5), (192, 356, 4), (492, 368, 5), (508, 354, 4)):
    for dx in range(-lr, lr + 1):
        put(lx + dx, ly, PAL['loto'][0])
        if abs(dx) < lr - 1:
            put(lx + dx, ly + 1, PAL['loto'][0])
    put(lx, ly - 1, PAL['loto'][1])
    put(lx - 1, ly - 1, PAL['loto'][1])

for fx, fy in ((70, 300), (95, 330), (130, 290), (565, 310), (590, 340), (20, 345), (470, 296), (160, 355)):
    if not ANIM:
        put(fx, fy, '#8ef8ec')
        glow(fx, fy, 6, '#3cd4cc', 0.7)

# 9. Gran Roble de Fittoa + lianas + búho nocturno + farol colgante
RAMA, RAMA2 = PAL['rama']
lz.rama([(-10, 26), (24, 38), (64, 50), (104, 56), (146, 56), (186, 70), (236, 70)], 7, 1.5, RAMA, RAMA2)
lz.rama([(64, 50), (78, 86), (92, 112), (78, 150)], 5, 1.2, RAMA, RAMA2)
lz.rama([(146, 56), (168, 26), (204, 12)], 3.5, 1, RAMA, RAMA2)
lz.rama([(186, 70), (200, 104), (214, 128)], 3.5, 1, RAMA, RAMA2)
lz.rama([(24, 38), (38, 12), (44, -2)], 3.5, 1, RAMA, RAMA2)
lz.rama([(104, 56), (122, 88), (138, 110)], 2.5, 1, RAMA, RAMA2)
lz.rama([(236, 70), (262, 66), (282, 74)], 1.5, 1, RAMA, RAMA2)

# Búho posado en la rama
for dy, w_o in ((-5, 1), (-4, 2), (-3, 2), (-2, 2), (-1, 1)):
    for dx in range(-w_o, w_o + 1):
        put(254 + dx, 65 + dy, RAMA)
put(253, 61, WARM if FASE == 'noche' else RAMA2)
put(255, 61, WARM if FASE == 'noche' else RAMA2)

for yy in range(110, 122):
    put(138, yy, RAMA)
if ANIM:
    FAROLES.append([138, 123, 8])
else:
    put(138, 123, WARM)
    put(138, 124, WARM)
    glow(138, 123, 8, WARM, 0.55)

HOJA = PAL['hoja']
def racimo_hojas(cx, cy, R):
    cells = {}
    for _ in range(int(R * 1.1) + 6):
        ox, oy = random.randint(-R // 2, R // 2), random.randint(-R // 2, R // 2)
        rr = random.randint(2, max(4, R // 3))
        for dy in range(-rr, rr + 1):
            for dx in range(-rr, rr + 1):
                d = math.hypot(dx, dy)
                if d <= rr and (d < rr * 0.72 or random.random() < 0.55):
                    cells[(cx + ox + dx, cy + oy + dy)] = 1
    for (x, y) in cells:
        if (x * 3 + y * 5) % 19 == 0 and random.random() < 0.35:
            continue
        v = ((x - cx) + (y - cy)) / (2.0 * R) + random.uniform(-0.24, 0.24)
        tono = 'l' if v < -0.32 else ('c' if v < 0.05 else ('m' if v < 0.42 else ('d' if v < 0.72 else 'x')))
        put(x, y, HOJA[tono])
    for _ in range(max(5, R // 2)):
        a = random.random() * 6.28
        rr_ = R * 0.6 + random.random() * 7
        put(int(cx + math.cos(a) * rr_), int(cy + math.sin(a) * rr_), random.choice((HOJA['l'], HOJA['c'], HOJA['m'])))

for cx, cy, R in (
    (14, 30, 26), (56, 46, 24), (100, 54, 28), (146, 54, 28), (180, 38, 20), (210, 14, 20), (186, 72, 24), (236, 70, 18),
    (74, 98, 22), (82, 136, 20), (210, 112, 20), (136, 100, 18), (44, 8, 20), (270, 70, 14), (110, 80, 14), (20, 70, 12),
    (120, 52, 16), (162, 64, 14), (90, 58, 14), (36, 40, 14),
):
    racimo_hojas(cx, cy, R)

# Zarcillos colgantes floridos desde la copa del roble
for zx, zl in ((58, 18), (116, 22), (168, 24), (206, 18)):
    for k in range(zl):
        if k % 2 == 0 or random.random() < 0.75:
            put(zx + (k // 7 % 2), 68 + k, HOJA['l'] if k > zl - 5 else HOJA['c'])

for _ in range(48):
    x, y = random.randrange(20, 350), random.randrange(20, 260)
    if not ANIM and not en_zona(x, y):
        c = random.choice((HOJA['l'], HOJA['c'], MANA_HI))
        put(x, y, c)
        put(x + 1, y + 1, HOJA['m'])

# 10. Viñeta + salida
aplica_vineta(lz, PAL['vig'])
out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, barca=[BX, BY], luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
