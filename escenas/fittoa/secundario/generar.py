#!/usr/bin/env python3
"""PixelZen Worlds - Fittoa (Monitor 2): Base de Perugius (Chaos Breaker) y Reino de Asura."""
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
random.seed(1119)

PALETAS = {
    'noche': dict(
        sky=['#050717', '#090c24', '#0f1336', '#181c46', '#242557', '#332d68', '#463878', '#5c4382', '#784e84', '#975e85', '#b57288', '#d28e88', '#e5ab92'],
        mont=['#433d73', '#343364', '#262852', '#191d3e', '#0e132a'],
        mist=['#8a78a8', '#70669c', '#53528a', '#3a3d74', '#262b5c'],
        nieve=('#e4e0f4', '#a8b0d8'), filo='#c4e2ec',
        pino1='#08101c', pino2='#111d2c', pinorim='#263c52',
        isla=('#0a101e', '#142032', '#263e52'),
        marble=('#8b96b6', '#667194', '#464e6c'),
        gold=('#f0c858', '#a8822c', '#fff0a4'),
        roof=('#1a284e', '#263c6e', '#3c5c9c'),
        rock_sky=('#282d46', '#3d4466', '#566088'),
        stone=('#192136', '#26304c', '#3b4a6c'),
        timber=('#0e1222', '#171c32'),
        agua='#070c22',
        ola=('#8ac6cc', '#4e6fa0', '#2d3b70'),
        cana=('#060b18', '#192a3e', '#080e1c', '#22344a'),
        vig=0.72,
        nube=['#4e5090', '#6d6ea8', '#866898', '#ba7e8e', '#cc8c8e', '#434886'],
        rama=('#0a1018', '#1a2738'),
        hoja={'l': '#488c82', 'c': '#2f6866', 'm': '#1c474c', 'd': '#112f38', 'x': '#091b24'},
        mana=('#5ef2e4', '#28b4b8'),
        loto=('#18363e', '#d8a8c8'),
    ),
    'dorado': dict(
        sky=['#121d4e', '#1e2c68', '#303e82', '#4c4c94', '#72569a', '#985c98', '#be6290', '#dc6e80', '#f0826c', '#fb9f60', '#ffc06c', '#ffd988', '#ffecad'],
        mont=['#8a5988', '#6f487c', '#54396b', '#3c2b54', '#261c3a'],
        mist=['#f2a288', '#d88088', '#b06688', '#80507c', '#523c66'],
        nieve=('#fff2e2', '#e4b8c4'), filo='#ffdca8',
        pino1='#1c1824', pino2='#2c2434', pinorim='#543c4e',
        isla=('#1e1928', '#2e2a38', '#5e4c56'),
        marble=('#f2dac8', '#c6a49c', '#967478'),
        gold=('#ffda68', '#c48c28', '#fff8c4'),
        roof=('#2c3a68', '#42568c', '#6880b8'),
        rock_sky=('#463854', '#664e6c', '#886882'),
        stone=('#342a3e', '#4a3c54', '#6e586e'),
        timber=('#241624', '#3c2432'),
        agua='#2b224c',
        ola=('#f2c098', '#a0729a', '#4c3e76'),
        cana=('#1a141e', '#4c3648', '#1e1824', '#5c4254'),
        vig=0.82,
        nube=['#b888a6', '#e49c98', '#f2ab8a', '#ffca98', '#ffd89c', '#9276a4'],
        rama=('#1c121e', '#3a2632'),
        hoja={'l': '#e6d27a', 'c': '#b8ad56', 'm': '#7c8240', 'd': '#4c5630', 'x': '#2c3422'},
        mana=('#72f6e6', '#3ac2c4'),
        loto=('#363c32', '#f4b8c0'),
    ),
    'dia': dict(
        sky=['#1a58b2', '#2668c4', '#387ad2', '#4c8cde', '#649ee6', '#7eb2ec', '#98c4f2', '#b0d4f4', '#c6e0f2', '#d8eae8', '#e6f0e4', '#f0f3dc', '#f6f2d4'],
        mont=['#789cc0', '#5e87ae', '#477294', '#345c72', '#224a52'],
        mist=['#d8eaf4', '#c2dced', '#a6cadc', '#86b4c6', '#689aa8'],
        nieve=('#ffffff', '#d6e8f4'), filo='#ffffff',
        pino1='#123828', pino2='#1b4d36', pinorim='#3e7854',
        isla=('#1c482c', '#2b663a', '#4e9256'),
        marble=('#ffffff', '#dce4f0', '#aab8cc'),
        gold=('#ffdf68', '#cca02c', '#fffbe0'),
        roof=('#264c82', '#3868aa', '#5c94d4'),
        rock_sky=('#5c667c', '#7c889e', '#9eacc0'),
        stone=('#525e6e', '#6d7c8e', '#94a4b4'),
        timber=('#3a281c', '#583d2a'),
        agua='#1d5d8e',
        ola=('#d2ebf8', '#7ab6dc', '#3878a8'),
        cana=('#0e3020', '#2e6442', '#123826', '#427a52'),
        vig=0.92,
        nube=['#ffffff', '#f5f9ff', '#ffffff', '#fff8ee', '#ffffff', '#e8f2fc'],
        rama=('#241812', '#422e22'),
        hoja={'l': '#b4df7c', 'c': '#7bc05e', 'm': '#49924c', 'd': '#2b6438', 'x': '#183e26'},
        mana=('#68f4e8', '#2cb8c0'),
        loto=('#2c6e48', '#f8d2dc'),
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

# 1. Cielo + astro (desplazado hacia el centro-derecha x~385 para dejar el cielo izquierdo libre para Chaos Breaker)
render_cielo(lz, PAL['sky'], SKYM, FASE)
exporta_sprites_si_aplica(lz, lambda: dibuja_luna_estandar(lz, 104, 104, 46), lambda: dibuja_sol_estandar(lz, 104, 104, 24))
render_estrellas(lz, FASE, ANIM, ESTRELLAS)

MX, MY, MR = 392, 82, 42
CX_ASTRO = MX if FASE == 'noche' else (MX + 34 if FASE == 'dorado' else MX - 28)
# Monitor 2 comparte cielo con Monitor 1: no duplicar sol/luna aquí

NUBES_DEF = [
    (80, 62, 150, PAL['nube'][0], 3),
    (320, 48, 165, PAL['nube'][1], 3),
    (520, 118, 155, PAL['nube'][2], 3),
    (220, 174, 185, PAL['nube'][3], 3),
    (445, 212, 145, PAL['nube'][4], 2),
    (75, 240, 115, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 2. Cordilleras verdes/nevadas del Reino de Asura
def rampa(x):
    return 0.55 + 0.45 * min(1.0, x / 220.0) if x < 220 else (1.0 if x < 440 else 0.72)

CAPAS = [
    (240, 104, 11, 0.012, PAL['mont'][0], PAL['mist'][0], True),
    (252, 84, 12, 0.016, PAL['mont'][1], PAL['mist'][1], False),
    (264, 64, 13, 0.021, PAL['mont'][2], PAL['mist'][2], False),
    (274, 44, 14, 0.028, PAL['mont'][3], PAL['mist'][3], False),
]
crestas = []
for base, amp, seed, fr, col, mist, nieve in CAPAS:
    r, ra = Ruido(seed * 19), Ruido(seed * 47 + 3)
    c = []
    for x in range(W):
        n = fbm(r, x * fr * 1.4 + seed)
        agudo = 1 - abs(2 * n - 1)
        am = 0.35 + 0.90 * ra(x * 0.012 + seed) ** 1.25
        c.append(base - amp * rampa(x) * am * (0.60 * agudo + 0.40 * n))
    crestas.append(c)
    for x in range(W):
        top = int(c[x])
        for y in range(top, HOR + 1):
            d = y - top
            cc = mix(col, mist, 0.25 * (d / max(1, HOR - top)) ** 2.1)
            if nieve and top < base - amp * 0.50 * rampa(x) and d < (base - amp * 0.50 * rampa(x) - top) * 0.55:
                cc = mix(PAL['nieve'][0], PAL['nieve'][1], min(1, d / 13.0))
            elif d < 2:
                cc = mix(cc, PAL['filo'], 0.24)
            put(x, y, cc)

# Pinos de las llanuras de Fittoa/Asura
def pino(x, by, h, col, rim):
    for i in range(h):
        y = by - h + i
        hw = max(0, int(i * 0.33) - (2 if i % 5 == 4 else 0))
        for dx in range(-hw, hw + 1):
            put(x + dx, y, col)
        if hw > 1 and i % 5 != 4:
            over(x - hw, y, rim, 0.52)

r5 = random.Random(91)
for x in range(0, W, 6):
    if r5.random() < 0.72:
        pino(x + r5.randint(-1, 1), int(crestas[3][x]) + 6, r5.randint(8, 17), PAL['pino1'], PAL['pinorim'])

WARM = '#f4bc68'
MANA_HI, MANA_LO = PAL['mana']
MB0, MB1, MB2 = PAL['marble']
GD0, GD1, GD2 = PAL['gold']
RF0, RF1, RF2 = PAL['roof']
RK0, RK1, RK2 = PAL['rock_sky']
ST0, ST1, ST2 = PAL['stone']

# 3. BASE DE PERUGIUS: CHAOS BREAKER (Fortaleza Flotante en el cielo izquierdo-central, cx = 192, cy_deck = 114)
CBX, CBY = 192, 114

# Halo de maná bajo la fortaleza flotante y partículas levitantes
if not ANIM:
    glow(CBX, CBY + 24, 34, MANA_LO, 0.30)

# Anillo arcano de teletransporte girando debajo de la base rocosa
for ang in range(0, 360, 6):
    rad = math.radians(ang)
    rx = int(CBX + 76 * math.cos(rad))
    ry = int(CBY + 22 + 9 * math.sin(rad))
    put(rx, ry, MANA_HI if ang % 24 == 0 else MANA_LO)
    if ang % 45 == 0:
        if ANIM:
            RUNAS.append([rx, ry])
        else:
            glow(rx, ry, 4, MANA_LO, 0.5)

# Base cónica de roca flotante de Chaos Breaker + cristales de maná incrustados
r_cb = Ruido(509)
for dy in range(0, 34):
    t = dy / 34.0
    hw = int(74 * (1 - t ** 1.15) + 4 * math.sin(dy * 0.6))
    for dx in range(-hw, hw + 1):
        # Estratos orgánicos facetados
        n_cb = r_cb(dx * 0.16 + dy * 0.24)
        if dx < -hw // 3:
            c = RK2 if n_cb > 0.35 else RK1
        elif dx < hw // 4:
            c = RK1 if n_cb > 0.48 else RK0
        else:
            c = RK0 if n_cb > 0.3 else mix(RK0, '#0a0e1e', 0.25)
        if dy == 0 or (abs(dx) > hw - 3 and dy < 8):
            c = MB1
        put(CBX + dx, CBY + dy, c)
# Estalactita / cristal central de levitación en la quilla
for dy in range(28, 44):
    hw = max(0, (44 - dy) // 4)
    for dx in range(-hw, hw + 1):
        put(CBX + dx, CBY + dy, MANA_HI if dx <= 0 else MANA_LO)

# Plataforma superior de mármol blanco y oro
for x in range(CBX - 76, CBX + 77):
    put(x, CBY - 3, GD0 if abs(x - CBX) < 74 else GD1)
    put(x, CBY - 2, MB0)
    put(x, CBY - 1, MB1)
    if x % 5 < 3:
        put(x, CBY - 4, MB0)

# Ciudadela alada de Chaos Breaker: 12 torres menores + Salón del Trono central con cúpula dorada
def torre_sky(tx, tw, th, h_cup):
    y0 = CBY - 3 - th
    for yy in range(y0, CBY - 3):
        for x in range(tx - tw // 2, tx + tw // 2 + 1):
            put(x, yy, MB0 if x < tx else MB1)
    # Cúpula / tejado con remate dorado
    for i in range(h_cup):
        hw = max(0, int((tw // 2 + 2) * math.sqrt(max(0.0, 1.0 - (i / max(1, h_cup)) ** 2))))
        for x in range(tx - hw, tx + hw + 1):
            put(x, y0 - i, GD2 if x < tx - 1 else (GD0 if x <= tx + 1 else GD1))
    for dy in range(-5, 0):
        put(tx, y0 - h_cup + dy, GD2)
    if ANIM:
        VENTANAS.append([tx, y0 + th // 2])
    else:
        put(tx, y0 + th // 2, WARM)
        put(tx, y0 + th // 2 + 1, WARM)

# Alas arquitectónicas escalonadas (pilares exteriores de los espíritus)
for dx_t, tw_t, th_t, hc_t in (
    (-62, 8, 16, 8), (-46, 10, 24, 10), (-30, 12, 30, 12),
    (30, 12, 30, 12), (46, 10, 24, 10), (62, 8, 16, 8),
):
    torre_sky(CBX + dx_t, tw_t, th_t, hc_t)

# Puentes celestes conectando las torres externas con la gran cúpula
for yy in (CBY - 16, CBY - 15):
    for x in range(CBX - 58, CBX + 59):
        if yy == CBY - 16 or x % 4:
            put(x, yy, MB1 if yy == CBY - 15 else GD0)

# Gran Torreón y Cúpula del Trono de Perugius (centro)
for yy in range(CBY - 34, CBY - 3):
    for x in range(CBX - 18, CBX + 19):
        c = MB0 if x < CBX - 4 else (MB1 if x < CBX + 6 else MB2)
        if abs(x - CBX) in (8, 16):
            c = GD1
        put(x, yy, c)
for wy in (CBY - 26, CBY - 16):
    for wx in (CBX - 11, CBX, CBX + 10):
        if ANIM:
            VENTANAS.append([wx, wy])
        else:
            put(wx, wy, WARM)
            put(wx + 1, wy, WARM)
# Gran cúpula imperial blanca/azul con nervios de oro
for i in range(18):
    hw = max(0, int(19 * math.sqrt(max(0.0, 1.0 - (i / 18.0) ** 1.8))))
    for x in range(CBX - hw, CBX + hw + 1):
        c = RF2 if x < CBX - 2 else (RF1 if x <= CBX + 4 else RF0)
        if abs(x - CBX) in (0, 6, 12):
            c = GD0
        put(x, CBY - 34 - i, c)
for dy in range(-9, 1):
    put(CBX, CBY - 52 + dy, GD2 if dy < -4 else GD0)
if ANIM:
    RUNAS.append([CBX, CBY - 62])
else:
    put(CBX, CBY - 62, MANA_HI)
    glow(CBX, CBY - 62, 6, MANA_LO, 0.65)

# Siluetas de 2 espíritus familiares / dragones alados patrullando Chaos Breaker
for sx_d, sy_d in ((CBX - 90, CBY - 32), (CBX + 86, CBY - 26)):
    for dx in range(-4, 5):
        put(sx_d + dx, sy_d - abs(dx) // 2, PAL['nieve'][0])
    put(sx_d, sy_d + 1, MANA_HI)

# 4. REINO DE ASURA: Meseta firme y amurallada para el Palacio Blanco (x = 204..496, fuera de HUD)
for y in range(HOR - 15, HOR + 1):
    t = (HOR - y) / 15.0
    ww = int(146 - t * 24)
    for x in range(max(198, 350 - ww), min(W, 350 + ww)):
        c_is = PAL['isla'][2] if y <= HOR - 13 else (PAL['isla'][1] if (x + y) % 4 else PAL['isla'][0])
        put(x, y, c_is)
for x in range(226, 472):
    for yy in range(HOR - 16, HOR - 12):
        put(x, yy, ST1 if (x // 4 + yy) % 2 else ST0)

# Muralla imperial de la Capital de Ars con contrafuertes y gran puerta real arqueada
for x in range(236, 462):
    for yy in range(HOR - 36, HOR - 12):
        c = MB0 if x < 348 else MB1
        if yy == HOR - 36:
            c = GD0
        elif yy > HOR - 17:
            c = MB2 if x >= 348 else MB1
        elif x % 16 in (0, 1):
            c = MB2
        elif yy % 8 == 0 and x % 4 == 0:
            c = mix(c, MB2, 0.4)
        put(x, yy, c)
    if x % 6 < 3:
        put(x, HOR - 38, MB0)
# Arco de la Puerta Real de Ars en el centro de la muralla
for dy in range(-14, 1):
    hw = 8 if dy > -7 else int(8 * math.sqrt(max(0, 1 - ((-dy - 7) / 7.0) ** 2)))
    for dx in range(-hw, hw + 1):
        put(348 + dx, HOR - 12 + dy, ST0 if abs(dx) < hw - 1 else GD1)

# Palacio Blanco / Plateado de Asura (torres reales + gran cúpula imperial dorada)
def torre_asura(cx, tw, th, sh, oro_dome=False):
    y0 = HOR - 36 - th
    for yy in range(y0, HOR - 34):
        for x in range(cx - tw // 2, cx + tw // 2 + 1):
            put(x, yy, MB0 if x < cx - 2 else (MB1 if x < cx + tw // 3 else MB2))
    for wy in range(y0 + 7, HOR - 40, 10):
        vx = cx - 1
        if ANIM:
            VENTANAS.append([vx, wy])
        else:
            for dy in range(3):
                put(vx, wy + dy, WARM)
                put(vx + 1, wy + dy, WARM)
    if oro_dome:
        # Cúpula real dorada + aguja alta
        dome_h = tw // 2 + 2
        for i in range(dome_h):
            hw = max(0, int((tw // 2 + 2) * math.sqrt(max(0.0, 1.0 - (i / max(1, dome_h)) ** 1.7))))
            for x in range(cx - hw, cx + hw + 1):
                put(x, y0 - i, GD2 if x < cx else GD0)
        for yy in range(y0 - dome_h - sh, y0 - dome_h):
            put(cx, yy, GD2)
    else:
        for i in range(sh):
            hw = max(0, int((tw // 2 + 2) * (1 - i / max(1, sh - 1))))
            for x in range(cx - hw, cx + hw + 1):
                put(x, y0 - i, RF2 if x < cx else RF0)
        for dy in range(-5, 0):
            put(cx, y0 - sh + dy, GD0)
    # Estandarte azul y oro del Reino de Asura
    for dx in range(1, 6):
        put(cx + dx, y0 - sh - (10 if oro_dome else 3), RF1 if dx < 4 else GD0)

torre_asura(260, 16, 30, 18)
torre_asura(298, 22, 42, 22)
torre_asura(348, 34, 58, 18, oro_dome=True)  # Gran Palacio Real de Ars
torre_asura(398, 22, 42, 22)
torre_asura(436, 16, 30, 18)

# 5. Puente Imperial arqueado sobre el Lago de Asura (x = 68..238) con estribos sólidos
for ax0, ax1 in ((64, 78), (228, 240)):
    for yy in range(HOR - 14, HOR + 1):
        for xx in range(ax0, ax1 + 1):
            put(xx, yy, ST1 if (xx + yy) % 3 else ST0)
for x in range(74, 238):
    arch_y = HOR - 12
    for yy in range(arch_y, HOR + 1):
        en_arco = False
        for cx_a in (110, 160, 210):
            dx = abs(x - cx_a)
            if dx < 17:
                lim = HOR - int(8 * math.sqrt(max(0, 1 - (dx / 17.0) ** 2)))
                if yy >= lim:
                    en_arco = True
        if not en_arco:
            put(x, yy, MB0 if yy == arch_y else (MB1 if (x // 4 + yy // 3) % 2 == 0 else MB2))
    put(x, arch_y - 2, GD0 if x % 8 == 0 else MB0)
    put(x, arch_y - 1, MB1)

for fx in (90, 136, 184, 228):
    for yy in range(HOR - 20, HOR - 13):
        put(fx, yy, PAL['timber'][0])
    if ANIM:
        FAROLES.append([fx, HOR - 21, 10])
    else:
        put(fx, HOR - 21, WARM)
        glow(fx, HOR - 21, 7, WARM, 0.55)

# Carromato viajero entrando hacia el Reino de Asura (x ~ 154)
CX_CAR = 154
for yy in range(HOR - 20, HOR - 14):
    for x in range(CX_CAR - 9, CX_CAR + 9):
        if yy < HOR - 17 and abs(x - CX_CAR) > 6:
            continue
        put(x, yy, MB0 if yy < HOR - 17 else PAL['timber'][1])
for wx in (CX_CAR - 5, CX_CAR + 5):
    disc(wx, HOR - 14, 3, PAL['timber'][0])

# Promontorio izquierdo plano bajo la posada (x = 6..84) para evitar esquinas colgantes
for y in range(HOR - 18, HOR + 1):
    d_m = HOR - y
    x_l = max(0, 8 + d_m // 2)
    x_r = min(84, 82 - d_m)
    for x in range(x_l, x_r):
        put(x, y, PAL['isla'][2] if y <= HOR - 16 else (PAL['isla'][1] if (x + y) % 3 else PAL['isla'][0]))
for yy in range(HOR - 36, HOR - 14):
    for x in range(24, 54):
        put(x, yy, MB1 if yy < HOR - 24 else ST1)
CHIMENEA = [29, HOR - 46]
for yy in range(HOR - 45, HOR - 35):
    for x in range(27, 32):
        put(x, yy, ST0)
for i in range(11):
    hw = max(1, int(17 * (1 - i / 10)))
    for x in range(39 - hw, 39 + hw + 1):
        put(x, HOR - 36 - i, RF1 if x < 39 else RF0)
if ANIM:
    VENTANAS.append([38, HOR - 30])
else:
    put(38, HOR - 30, WARM)
    put(39, HOR - 30, WARM)

# 6. Reflejo en el lago real (sin columna del sol/luna para no duplicar con Monitor 1)
render_lago(lz, PAL['agua'], PAL['ola'], DESTELLOS, ANIM, mx=CX_ASTRO, reflejo_cols=(PAL['filo'], PAL['ola'][0]), reflejo_astro=False)

# 7. Cañas y nenúfares en las orillas
rcn = random.Random(88)
for x in list(range(0, 82, 4)) + list(range(525, 640, 3)):
    if rcn.random() < 0.78:
        h_c = rcn.randint(20, 76) - (20 if x < 100 else 0)
        curva = rcn.uniform(-1, 1)
        for i in range(h_c):
            xx = x + int(curva * (i / h_c) ** 2 * 10)
            put(xx, H - 1 - i, PAL['cana'][0])
            if i > 4:
                over(xx - 1, H - 1 - i, PAL['cana'][1], 0.48)

for lx, ly, lr in ((165, 344, 5), (295, 360, 4), (420, 338, 5)):
    for dx in range(-lr, lr + 1):
        put(lx + dx, ly, PAL['loto'][0])
    put(lx, ly - 1, PAL['loto'][1])

# 8. Rama decorativa orgánica en esquina superior derecha
RAMA, RAMA2 = PAL['rama']
lz.rama([(646, 28), (608, 42), (572, 52), (546, 58)], 6, 1.4, RAMA, RAMA2)
lz.rama([(602, 44), (590, 74)], 3.5, 1, RAMA, RAMA2)
HOJA = PAL['hoja']
for cx, cy, R in ((626, 26, 24), (592, 38, 22), (558, 48, 18), (588, 68, 16)):
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
        v = ((x - cx) + (y - cy)) / (2.0 * R) + random.uniform(-0.24, 0.24)
        put(x, y, HOJA['l' if v < -0.32 else ('c' if v < 0.05 else ('m' if v < 0.42 else ('d' if v < 0.72 else 'x')))])

aplica_vineta(lz, PAL['vig'])
out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
