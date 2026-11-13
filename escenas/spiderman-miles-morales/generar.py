#!/usr/bin/env python3
"""PixelZen - Tema Spider-Man: Miles Morales (Brooklyn, Puente de Brooklyn, Estatua de la Libertad y Manhattan)."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, en_zona, exporta_salida, exporta_sprites_si_aplica, mix, render_cielo,
    render_estrellas, render_lago, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1610)

PALETAS = {
    'noche': dict(
        sky=['#04030e', '#0a071d', '#120b2e', '#1e1042', '#2d1656', '#401c68', '#582472', '#742e76', '#943c76', '#b85076'],
        sky_far=('#16142c', '#201d3c', '#2d2952'),
        sky_mid=('#100e22', '#181530', '#262146'),
        brick=('#3a1b24', '#4e242e', '#261018'),
        concrete=('#282638', '#3a3752', '#1a1826'),
        steel=('#161824', '#282c40'),
        bridge=('#382e40', '#4f4058', '#221b2a'),
        liberty=('#4ec4a8', '#308d7c', '#184e4a'),
        pedestal=('#444054', '#2c2a3a', '#1a1826'),
        neon_r='#ff2a55',
        neon_c='#00e5ff',
        neon_y='#ffd840',
        agua='#060818',
        ola=('#5ce0ff', '#ff4a88', '#262456'),
        suelo=('#0c0a16', '#1c182c', '#120e20', '#26203a'),
        vig=0.72,
        nube=['#382854', '#4e366e', '#684480', '#8a5488', '#a6688c', '#302248'],
        web='#b4c8e2',
        suit=('#0d0b14', '#e0243c'),
    ),
    'dorado': dict(
        sky=['#140826', '#240c3a', '#3b124e', '#5a1a5e', '#802464', '#aa325e', '#d24852', '#ee6a48', '#fc9246', '#ffc266'],
        sky_far=('#3a2444', '#4c3056', '#664270'),
        sky_mid=('#261630', '#362042', '#4c305a'),
        brick=('#5c2428', '#7c3234', '#3c161a'),
        concrete=('#403044', '#5a445e', '#2a1e2e'),
        steel=('#241a2a', '#3c2c42'),
        bridge=('#543a48', '#745264', '#362430'),
        liberty=('#6ec4a6', '#468a7c', '#26504e'),
        pedestal=('#6e5864', '#4e3c48', '#30242e'),
        neon_r='#ff3660',
        neon_c='#24ecff',
        neon_y='#ffe058',
        agua='#1a102a',
        ola=('#ff9884', '#70b8e0', '#382a58'),
        suelo=('#160c1a', '#2c182c', '#1c1020', '#3a2038'),
        vig=0.80,
        nube=['#6e325c', '#984266', '#c65864', '#ea7a5e', '#fca266', '#5a284e'],
        web='#f6dce6',
        suit=('#100a14', '#ea2840'),
    ),
    'dia': dict(
        sky=['#1a52a8', '#2868bc', '#3c80ce', '#5498de', '#72b0ea', '#94c6f0', '#b6daf4', '#d4e8f2', '#eceee4', '#faf0d2'],
        sky_far=('#5c7296', '#728aa8', '#8ea6c2'),
        sky_mid=('#3e5070', '#506488', '#687ea2'),
        brick=('#7c3638', '#9c4848', '#582426'),
        concrete=('#686e82', '#848aa0', '#4c5264'),
        steel=('#32384a', '#4e566c'),
        bridge=('#786e76', '#948a92', '#564e56'),
        liberty=('#84dcd0', '#54b4a2', '#32786e'),
        pedestal=('#a4aab8', '#7e8494', '#585e6c'),
        neon_r='#ff2a55',
        neon_c='#00d2ee',
        neon_y='#ffca38',
        agua='#1c486e',
        ola=('#bfe8f8', '#5c94be', '#2a5680'),
        suelo=('#1e222e', '#32384a', '#242a38', '#3e465a'),
        vig=0.90,
        nube=['#ffffff', '#f2f6fa', '#ffffff', '#e6eff6', '#faf8f2', '#dce8f4'],
        web='#f0f6fc',
        suit=('#12101a', '#e8243c'),
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

# 1. Cielo urbano Spider-Verse + aurora neón nocturna
render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#ff2a55', '#00e5ff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 44, halo='#8ec8f4', base='#f6f8ff', sombra='#cad8ec', crater='#a2b4ce', crater_hi='#bacae0'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 24, halo='#ffd888', centro='#fffdf0', borde='#ffb84c', rayo='#ffe088'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffdce8', '#cceeff', '#e0d4ff'])

MX, MY, MR = 368, 80, 44
CX_ASTRO = MX if FASE == 'noche' else (MX + 44 if FASE == 'dorado' else MX - 45)
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#8ec8f4', base='#f6f8ff', sombra='#cad8ec', crater='#a2b4ce', crater_hi='#bacae0')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, MX + 44, 202, 24, halo='#ffaa70', centro='#fff2d8', borde='#ff6a42', rayo='#ff9a5a')
    else:
        dibuja_sol_estandar(lz, MX - 45, 94, 24, halo='#ffd888', centro='#fffdf0', borde='#ffb84c', rayo='#ffe088')

# 2. Nubes volumétricas
NUBES_DEF = [
    (180, 52, 175, PAL['nube'][0], 3),
    (360, 96, 150, PAL['nube'][1], 3),
    (100, 152, 190, PAL['nube'][2], 3),
    (280, 194, 155, PAL['nube'][3], 3),
    (550, 244, 125, PAL['nube'][4], 2),
    (420, 44, 95, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)


# 3. Skyline de Lower Manhattan (x: 180..422, dejando bahía abierta x: 424..490 para la Estatua de la Libertad)
def rect(x0, y0, w, h, c):
    for yy in range(max(0, y0), min(HOR + 1, y0 + h)):
        for xx in range(max(0, x0), min(W, x0 + w)):
            put(xx, yy, c)


def _dibuja_ventana_urbana(wx, wy, w_v, h_v, c_hi, r_w, col_alt='#b8ecff'):
    if en_zona(wx, wy):
        return
    if ANIM and r_w.random() < 0.25:
        VENTANAS.append([wx, wy])
        return
    if FASE == 'dia':
        col_w = mix(c_hi, '#d8f0ff', 0.35) if r_w.random() < 0.35 else c_hi
    else:
        col_w = col_alt if r_w.random() < 0.16 else '#ffe088'
    for dy in range(h_v):
        for dx in range(w_v):
            put(wx + dx, wy + dy, col_w)


def edificio(x0, w, h, cols, win_prob=0.5, spire=0, neon=None, style='grid', crown=None):
    y0 = HOR - h
    c_dk, c_md, c_hi = cols
    for yy in range(y0, HOR + 1):
        for xx in range(x0, x0 + w):
            c = c_hi if xx < x0 + 3 else (c_md if xx < x0 + w - 4 else c_dk)
            if style == 'vertical' and (xx - x0) % 4 == 0:
                c = mix(c, c_dk, 0.28)
            put(xx, yy, c)

    # Remates arquitectónicos icónicos de Nueva York
    if crown == 'wtc':
        # Facetas biseladas + corona luminosa estilo One WTC
        for i in range(10):
            inset = i // 3
            for xx in range(x0 + inset, x0 + w - inset):
                put(xx, y0 - i, c_hi if xx < x0 + w // 2 else c_md)
        for xx in range(x0 + 3, x0 + w - 3):
            put(xx, y0 - 10, PAL['neon_c'] if FASE != 'dia' else c_hi)
        top_y = y0 - 10
    elif crown == 'empire':
        # Retranqueos Art-Deco escalonados estilo Empire State
        w1 = max(8, w - 8)
        x1 = x0 + (w - w1) // 2
        rect(x1, y0 - 12, w1, 12, c_md)
        for yy in range(y0 - 12, y0):
            put(x1, yy, c_hi)
            put(x1 + w1 - 1, yy, c_dk)
        w2 = max(4, w1 - 6)
        x2 = x0 + (w - w2) // 2
        rect(x2, y0 - 20, w2, 8, c_hi)
        if FASE != 'dia':
            for xx in range(x2, x2 + w2):
                put(xx, y0 - 14, PAL['neon_y'])
        top_y = y0 - 20
    elif crown == 'chrysler':
        # Arcos Art-Deco plateados escalonados estilo Chrysler Building
        for tier, (tw, th) in enumerate(((w - 4, 6), (w - 10, 6), (w - 16, 5))):
            if tw >= 4:
                tx = x0 + (w - tw) // 2
                ty = y0 - (tier * 5) - th
                rect(tx, ty, tw, th, mix(c_hi, '#d4e2f4', 0.35 if FASE != 'dia' else 0.5))
                if FASE != 'dia':
                    for xx in range(tx + 1, tx + tw - 1, 2):
                        put(xx, ty + 1, '#fff4cc')
        top_y = y0 - 17
    elif crown == 'stepped':
        w1 = max(6, w - 6)
        rect(x0 + (w - w1) // 2, y0 - 6, w1, 6, c_md)
        top_y = y0 - 6
    else:
        top_y = y0

    if spire > 0:
        sx = x0 + w // 2
        for yy in range(top_y - spire, top_y):
            put(sx, yy, c_hi if yy < top_y - spire // 2 else c_md)
        if ANIM:
            RUNAS.append([sx, top_y - spire])
        else:
            put(sx, top_y - spire, PAL['neon_r'])
            glow(sx, top_y - spire, 3, PAL['neon_r'], 0.6)

    if neon:
        for xx in range(x0 + 2, x0 + w - 2):
            put(xx, y0 + 2, neon)
        if ANIM:
            RUNAS.append([x0 + w // 2, y0 + 2])

    # Ventanitas urbanas variadas
    r_w = random.Random(x0 * 13 + h)
    if style == 'strip':
        for wy in range(y0 + 7, HOR - 8, 5):
            if r_w.random() < win_prob + 0.15 and not en_zona(x0 + 4, wy):
                for wx in range(x0 + 3, x0 + w - 4, 3):
                    if r_w.random() < 0.72:
                        _dibuja_ventana_urbana(wx, wy, 2, 1, c_hi, r_w)
    else:
        for wy in range(y0 + 7, HOR - 8, 6):
            for wx in range(x0 + 3, x0 + w - 4, 4):
                if r_w.random() < win_prob:
                    _dibuja_ventana_urbana(wx, wy, 2, 1, c_hi, r_w)


# Capa trasera de rascacielos de Manhattan (x: 180..422)
FAR = PAL['sky_far']
MID = PAL['sky_mid']
edificio(182, 22, 86, FAR, 0.35, spire=10, style='grid', crown='stepped')
edificio(206, 18, 66, FAR, 0.30, style='strip')
edificio(226, 28, 120, FAR, 0.42, spire=28, style='vertical', crown='wtc')        # One World Trade Center
edificio(257, 20, 78, FAR, 0.35, style='strip')
edificio(280, 30, 104, FAR, 0.42, spire=16, style='grid', crown='empire')       # Empire State Building
edificio(313, 22, 74, FAR, 0.35, style='vertical')
edificio(338, 26, 90, FAR, 0.40, spire=14, neon=PAL['neon_r'], style='grid', crown='chrysler')  # Torre Art-Deco Chrysler
edificio(367, 20, 68, FAR, 0.32, style='strip')
edificio(390, 24, 82, FAR, 0.38, style='grid', crown='stepped')

# Sector derecho bajo el HUD (x: 492..640, altura <= 58 px para respetar y >= 222 bajo el HUD)
edificio(494, 24, 52, FAR, 0.38, style='strip')
edificio(521, 28, 56, FAR, 0.42, spire=8, crown='stepped')
edificio(552, 22, 44, FAR, 0.35, neon=PAL['neon_c'], style='grid')
edificio(577, 28, 54, FAR, 0.40, style='vertical', crown='stepped')
edificio(608, 30, 46, FAR, 0.36, spire=6, style='strip')
# Depósitos y grúa portuaria en el sector derecho bajo el HUD
rect(584, HOR - 66, 12, 6, PAL['sky_mid'][1])
for yy in range(HOR - 52, HOR - 48):
    for xx in range(500, 510):
        put(xx, yy, PAL['sky_mid'][0])
for yy in range(HOR - 60, HOR - 44):
    put(562, yy, PAL['sky_mid'][0])
for xx in range(554, 570):
    put(xx, HOR - 60, PAL['sky_mid'][1])
if not ANIM:
    put(535, HOR - 64, PAL['neon_r'])
    put(623, HOR - 52, PAL['neon_c'])

# Capa media de rascacielos de Manhattan (x: 196..418)
edificio(196, 24, 64, MID, 0.45, style='strip')
edificio(248, 20, 54, MID, 0.40, style='grid')
edificio(344, 22, 58, MID, 0.45, neon=PAL['neon_c'], style='vertical')
edificio(398, 22, 52, MID, 0.40, style='grid')

# Bruma atmosférica sutil y malecón/muelle sólido en la base del skyline de Manhattan y sector derecho
sky_bot = PAL['sky'][-1]
for yy in range(HOR - 14, HOR - 5):
    dens = (1.0 - (HOR - 5 - yy) / 10.0) * 0.22
    for xx in range(180, 424):
        if dith(xx, yy, dens):
            over(xx, yy, sky_bot, 0.28)
CN_M0, CN_M1, CN_M2 = PAL['concrete']
for sx0, sx1 in ((176, 426), (488, W)):
    for yy in range(HOR - 6, HOR + 1):
        for xx in range(sx0, sx1):
            c = CN_M1 if yy == HOR - 6 else (CN_M2 if (xx // 8 + yy) % 2 == 0 else CN_M0)
            put(xx, yy, c)
    for xx in range(sx0 + 4, sx1 - 2, 16):
        put(xx, HOR - 7, CN_M2)
        put(xx, HOR - 8, PAL['steel'][0])
        if FASE != 'dia':
            put(xx, HOR - 9, PAL['neon_y'])
            if not ANIM:
                glow(xx, HOR - 9, 2, PAL['neon_y'], 0.35)

# 3b. ESTATUA DE LA LIBERTAD en Liberty Island (bahía abierta x ~ 456, 100% libre del HUD x >= 478)
LX = 456
LB0, LB1, LB2 = PAL['liberty']
PD0, PD1, PD2 = PAL['pedestal']

# Isla de la Libertad / Muralla estrellada de Fort Wood (x: 438..474, y: HOR-7..HOR)
for yy in range(HOR - 7, HOR + 1):
    hw = 15 + (yy - (HOR - 7)) // 2
    for dx in range(-hw, hw + 1):
        c = PD0 if dx < -hw // 3 else (PD1 if dx < hw // 3 else PD2)
        if yy == HOR - 7:
            c = PD0
        put(LX + dx, yy, c)
if FASE != 'dia':
    for fx_i in (LX - 13, LX + 13):
        put(fx_i, HOR - 8, PAL['neon_y'])

# Pedestal de granito escalonado (y: HOR-38..HOR-7)
for yy in range(HOR - 12, HOR - 7):
    for dx in range(-10, 11):
        put(LX + dx, yy, PD0 if dx < -3 else (PD1 if dx < 4 else PD2))
for yy in range(HOR - 34, HOR - 12):
    for dx in range(-8, 9):
        c = PD0 if dx < -3 else (PD1 if dx < 3 else PD2)
        if HOR - 32 <= yy <= HOR - 28 and abs(dx) in (2, 5):
            c = PD2  # columnata superior del pedestal
        put(LX + dx, yy, c)
for yy in range(HOR - 38, HOR - 34):
    hw = 10 if yy == HOR - 37 else 9
    for dx in range(-hw, hw + 1):
        put(LX + dx, yy, PD0 if yy == HOR - 38 or dx < -3 else (PD1 if dx < 4 else PD2))
# Reflectores cálidos iluminando la base del pedestal de noche
if FASE != 'dia':
    for fx_p in (LX - 7, LX + 7):
        put(fx_p, HOR - 38, '#ffd890')
        if not ANIM:
            glow(fx_p, HOR - 39, 4, '#ffbe60', 0.35)

# Túnica / toga de cobre oxidado (y: HOR-82..HOR-38 -> 242..198)
for i in range(44):
    yy = HOR - 39 - i
    t = i / 43.0
    if t < 0.72:
        hw = int(7 - 2.2 * (t / 0.72))
    else:
        hw = int(5 + 1.5 * ((t - 0.72) / 0.28))
    cx_s = LX
    for dx in range(-hw, hw + 1):
        pliegue = (dx + i // 4) % 3 == 0
        if dx < -1:
            c = LB0 if not pliegue else LB1
        elif dx < 2:
            c = LB1 if not pliegue else LB0
        else:
            c = LB2 if not pliegue else LB1
        put(cx_s + dx, yy, c)
# Banda diagonal del manto sobre el pecho
for k in range(-4, 6):
    put(LX + k, HOR - 76 + k // 2, LB0)

# Brazo izquierdo y Tabula Ansata (tablilla de la ley en la derecha del espectador: LX+5..LX+9)
for yy in range(HOR - 79, HOR - 65):
    for dx in range(5, 9):
        c = LB0 if dx == 5 or yy == HOR - 79 else (LB1 if dx < 8 else LB2)
        put(LX + dx, yy, c)

# Cabeza y cuello (y: HOR-91..HOR-83)
for yy in range(HOR - 85, HOR - 82):
    for dx in (-1, 0, 1):
        put(LX + dx, yy, LB1 if dx <= 0 else LB2)
for dy in range(-4, 3):
    hw = 3 if abs(dy) <= 2 else 2
    for dx in range(-hw, hw + 1):
        put(LX + dx, HOR - 88 + dy, LB0 if dx < 0 else (LB1 if dx == 0 else LB2))

# Diadema y corona radiante de 7 rayos
for dx in range(-3, 4):
    put(LX + dx, HOR - 91, LB2)
    put(LX + dx, HOR - 92, '#ffe898' if (FASE != 'dia' and dx % 2 == 0) else LB0)
for ang_deg in (-66, -44, -22, 0, 22, 44, 66):
    ang = math.radians(ang_deg - 90)
    for step in range(4, 15):
        r_sp = step * 0.5
        sx_r = round(LX + math.cos(ang) * r_sp)
        sy_r = round((HOR - 90) + math.sin(ang) * r_sp)
        put(sx_r, sy_r, LB0 if ang_deg <= 0 else LB1)

# Brazo derecho alzado (hacia arriba a la izquierda: LX-5..LX-9, y: HOR-105..HOR-80) sosteniendo la Antorcha
for k in range(25):
    t = k / 24.0
    ax = round(LX - 5 - t * 4.2)
    ay = HOR - 80 - k
    put(ax, ay, LB0)
    put(ax + 1, ay, LB1 if t < 0.7 else LB2)
    if k < 10:
        put(ax - 1, ay, LB0)

# Balcón dorado y copa de la antorcha (x = LX - 9, y = HOR - 109..HOR - 105)
tx_l, ty_l = LX - 9, HOR - 108
for dx in range(-2, 3):
    put(tx_l + dx, ty_l + 2, '#e8b44c' if dx <= 0 else '#9c6c24')
    put(tx_l + dx, ty_l + 3, '#c89030')
put(tx_l, ty_l + 4, '#9c6c24')
# Llama de la antorcha
if ANIM:
    put(tx_l, ty_l, '#ffd460')
    put(tx_l, ty_l + 1, '#ff9830')
    FAROLES.append([tx_l, ty_l, 8])
else:
    put(tx_l, ty_l - 2, '#fffbe0')
    put(tx_l, ty_l - 1, '#fff2a8')
    put(tx_l - 1, ty_l, '#ffc048')
    put(tx_l, ty_l, '#fff4b8')
    put(tx_l + 1, ty_l, '#ff9830')
    put(tx_l, ty_l + 1, '#ff8828')
    glow(tx_l, ty_l - 1, 9, '#ffb844', 0.72)

# 3c. Puente de Brooklyn cruzando el East River (x: 214..418, torres en x=268 y x=370)
BR0, BR1, BR2 = PAL['bridge']
y_deck = HOR - 24

# Estribos y viaductos de piedra en ambos extremos (anclaje sólido en Brooklyn y Manhattan)
for ax0, ax1 in ((214, 236), (398, 418)):
    for yy in range(y_deck - 2, HOR + 1):
        for xx in range(ax0, ax1 + 1):
            # Arcos de descarga bajo el tablero del viaducto
            rel_x = (xx - ax0) % 8
            es_arco = (yy >= y_deck + 7) and (2 <= rel_x <= 5) and (yy >= y_deck + 10 or rel_x in (3, 4))
            if yy >= HOR - 4:
                es_arco = False
            if es_arco:
                put(xx, yy, mix(BR2, '#080610', 0.45))
            else:
                c = BR1 if xx < ax0 + 3 or yy == y_deck - 2 else (BR0 if xx < ax1 - 3 else BR2)
                if (xx // 4 + yy // 3) % 3 == 0:
                    c = mix(c, BR2, 0.22)
                put(xx, yy, c)
    # Base del muelle en la línea de agua
    for xx in range(ax0 - 2, ax1 + 3):
        put(xx, HOR - 2, BR1)
        put(xx, HOR - 1, BR0)
        put(xx, HOR, BR2)

# Tablero con celosía metálica (4 px de canto) y farolas de calzada
for x in range(214, 419):
    put(x, y_deck, BR1)
    put(x, y_deck + 1, BR0)
    put(x, y_deck + 2, BR2 if (x % 4) else BR0)
    put(x, y_deck + 3, BR2)
    if x % 11 == 0 and FASE != 'dia':
        put(x, y_deck - 1, PAL['neon_y'])

for tx_b in (268, 370):
    # Tajamar / muelle de cimentación escalonado en el río (bien visible hasta el agua)
    for yy in range(HOR - 14, HOR + 1):
        hw_p = 11 if yy < HOR - 7 else 13
        for dx in range(-hw_p, hw_p + 1):
            c = BR1 if dx < -hw_p // 2 or yy == HOR - 14 else (BR0 if dx < hw_p // 2 else BR2)
            if yy >= HOR - 1:
                c = mix(BR2, '#04040c', 0.4)
            put(tx_b + dx, yy, c)
    # Torre de granito con dos arcos góticos
    for yy in range(HOR - 82, HOR - 14):
        for dx in range(-8, 9):
            is_arch = (HOR - 68 <= yy <= HOR - 30) and (2 <= abs(dx) <= 5)
            if not is_arch:
                c = BR1 if dx < -2 else (BR0 if dx < 4 else BR2)
                if yy in (HOR - 70, HOR - 50, HOR - 26):
                    c = BR1
                put(tx_b + dx, yy, c)
    for dx in range(-9, 10):
        put(tx_b + dx, HOR - 82, BR1)
        put(tx_b + dx, HOR - 81, BR2)
    if ANIM:
        RUNAS.append([tx_b, HOR - 84])
    else:
        put(tx_b, HOR - 84, PAL['neon_r'])
    # Tirantes diagonales en abanico característicos del Puente de Brooklyn
    for target_x in range(tx_b - 36, tx_b + 37, 9):
        if 220 <= target_x <= 412 and abs(target_x - tx_b) > 8:
            steps_s = max(abs(target_x - tx_b), 56)
            for k in range(steps_s + 1):
                sx_c = round(tx_b + (target_x - tx_b) * k / steps_s)
                sy_c = round((HOR - 80) + (y_deck - (HOR - 80)) * k / steps_s)
                if k % 2 == 0:
                    over(sx_c, sy_c, BR1, 0.62)

# Cables de suspensión parabólicos anclados en los estribos (x=224..408) y péndolas verticales
for x in range(224, 409):
    if x < 268:
        yc = int(HOR - 80 + ((268 - x) / 44.0) ** 1.45 * 55)
    elif x <= 370:
        t = (x - 268) / 102.0
        yc = int(HOR - 80 + 48 * (1 - ((2 * t - 1) ** 2)))
    else:
        yc = int(HOR - 80 + ((x - 370) / 38.0) ** 1.45 * 55)
    if yc < y_deck:
        put(x, yc, BR1)
        put(x, yc + 1, BR0)
        if x % 14 == 0 and FASE != 'dia':
            put(x, yc - 1, PAL['neon_y'])
        if x % 5 == 0:
            for yy in range(yc + 1, y_deck):
                put(x, yy, BR2)

# 4. Barrio de Brooklyn a la izquierda (x: 0..226): edificios de ladrillo, escaleras de incendios y depósitos
BK0, BK1, BK2 = PAL['brick']
CN0, CN1, CN2 = PAL['concrete']
ST0, ST1 = PAL['steel']

# Paseo de piedra en la orilla de Brooklyn
for x in range(0, 232):
    for yy in range(HOR - 8, HOR + 1):
        c = CN0 if ((x * 3 + yy * 5) // 4) % 2 else CN2
        if yy == HOR - 8:
            c = CN1
        put(x, yy, c)


def edificio_brooklyn(x0, w, h, cols, fire_escape=False, water_tower=False):
    y0 = HOR - 8 - h
    c0, c1, c2 = cols
    for yy in range(y0, HOR - 8):
        for xx in range(x0, x0 + w):
            c = c1 if xx < x0 + w // 3 else (c0 if xx < x0 + 2 * w // 3 else c2)
            if yy % 4 == 0 and (xx + yy // 4) % 3 == 0:
                c = mix(c, c2, 0.25)
            put(xx, yy, c)
    # Cornisa superior escalonada
    for xx in range(x0 - 1, x0 + w + 1):
        put(xx, y0, CN1)
        put(xx, y0 + 1, CN2)
        put(xx, y0 + 2, c2)
    # Ventanas cálidas de apartamento (algunas apagadas o con brillo frío de TV)
    r_b = random.Random(x0 * 7 + h)
    for wy in range(y0 + 8, HOR - 16, 10):
        for wx in range(x0 + 6, x0 + w - 7, 10):
            roll = r_b.random()
            if roll < 0.18:
                for dy in range(4):
                    put(wx, wy + dy, c2)
                    put(wx + 1, wy + dy, c2)
            elif ANIM and roll < 0.72:
                VENTANAS.append([wx, wy])
            else:
                if FASE == 'dia':
                    col_v = CN1
                else:
                    col_v = '#88dcff' if roll > 0.88 else '#ffd26a'
                for dy in range(4):
                    put(wx, wy + dy, col_v)
                    put(wx + 1, wy + dy, col_v)
            for dx in range(-1, 3):
                put(wx + dx, wy - 1, CN2)
                put(wx + dx, wy + 4, CN1)
            # Pequeño aparato de aire acondicionado ocasional en el alféizar
            if r_b.random() < 0.14:
                put(wx + 2, wy + 2, ST0)
                put(wx + 2, wy + 3, ST1)
                put(wx + 3, wy + 2, ST1)
                put(wx + 3, wy + 3, ST0)
    # Escalera de incendios en zigzag con barandilla
    if fire_escape:
        fx0, fw = x0 + 8, max(14, w - 16)
        for fy in range(y0 + 12, HOR - 14, 10):
            for xx in range(fx0, fx0 + fw):
                put(xx, fy, ST0)
                put(xx, fy - 2, ST1)
            for xx in range(fx0, fx0 + fw, 3):
                put(xx, fy - 1, ST0)
            for k in range(10):
                lx = fx0 + (k * fw // 10 if (fy // 10) % 2 == 0 else fw - k * fw // 10)
                put(lx, fy + k, ST1)
    # Depósito de agua clásico de NYC en la azotea
    if water_tower:
        wx_t = x0 + w // 2
        for lx in (wx_t - 5, wx_t + 5):
            for yy in range(y0 - 8, y0):
                put(lx, yy, ST0)
        for yy in range(y0 - 20, y0 - 8):
            for dx in range(-6, 7):
                c_wt = c0 if dx < 0 else c2
                if yy in (y0 - 17, y0 - 12):
                    c_wt = ST0
                put(wx_t + dx, yy, c_wt)
        for i in range(6):
            hw = 7 - i
            for dx in range(-hw, hw + 1):
                put(wx_t + dx, y0 - 20 - i, ST1 if dx < 0 else ST0)


edificio_brooklyn(4, 56, 78, (BK0, BK1, BK2), fire_escape=True, water_tower=True)
edificio_brooklyn(62, 46, 60, (CN0, CN1, CN2), fire_escape=False, water_tower=False)
edificio_brooklyn(110, 62, 88, (BK0, BK1, BK2), fire_escape=True, water_tower=True)
edificio_brooklyn(174, 46, 54, (CN0, CN1, CN2), fire_escape=False, water_tower=False)

# Antena de TV en el edificio izquierdo y chimenea humeante en el edificio alto
for yy in range(HOR - 102, HOR - 86):
    put(22, yy, ST1)
for dx in range(-4, 5):
    put(22 + dx, HOR - 99, ST0)
    put(22 + dx // 2, HOR - 94, ST0)

CHIMENEA = [160, HOR - 106]
for yy in range(HOR - 105, HOR - 96):
    for xx in range(158, 163):
        put(xx, yy, CN2)

# Cartel / grafiti neón estilo Miles Morales en el edificio derecho de Brooklyn (x ~ 179..215)
for xx in range(181, 213):
    for yy in range(HOR - 44, HOR - 30):
        put(xx, yy, '#181024')
for xx in range(183, 211):
    put(xx, HOR - 42, PAL['neon_r'] if xx % 2 else PAL['neon_c'])
    put(xx, HOR - 32, PAL['neon_c'] if xx % 2 else PAL['neon_r'])
# Pequeña araña Spider-Verse dentro del cartel neón
disc(197, HOR - 37, 2, PAL['neon_r'])
for dx, dy in ((-3, -2), (3, -2), (-3, 2), (3, 2), (-4, 0), (4, 0)):
    put(197 + dx, HOR - 37 + dy, PAL['neon_r'])
if ANIM:
    RUNAS.append([197, HOR - 37])

# Farolas urbanas cálidas a lo largo del muelle de Brooklyn
for fx in (30, 90, 148, 224):
    fy = HOR - 8
    for yy in range(11):
        put(fx, fy - yy, ST0)
    put(fx + 1, fy - 11, ST0)
    if ANIM:
        FAROLES.append([fx + 2, fy - 10, 7])
    else:
        put(fx + 2, fy - 10, '#fff0c8')
        glow(fx + 2, fy - 10, 8, '#ff9e44', 0.65)

# 5. Reflejo del East River y Bahía de Nueva York + olas + destellos neón
render_lago(lz, PAL['agua'], PAL['ola'], DESTELLOS, ANIM, mx=CX_ASTRO)

# Ferry clásico de Staten Island navegando por la bahía (en ANIM lo dibuja el motor en movimiento)
if not ANIM:
    fx_f, fy_f = 324, 295
    for dx in range(-10, 10):
        put(fx_f + dx, fy_f, '#141a2e')
        put(fx_f + dx, fy_f + 1, '#141a2e')
    for dx in range(-9, 9):
        put(fx_f + dx, fy_f - 1, '#e65c28')
    for dx in range(-7, 7):
        put(fx_f + dx, fy_f - 3, '#dce6f2')
        put(fx_f + dx, fy_f - 2, '#dce6f2')
    for dx in range(-6, 6):
        put(fx_f + dx, fy_f - 4, '#f0682c')
    for dx in range(-3, 3):
        put(fx_f + dx, fy_f - 6, '#dce6f2')
        put(fx_f + dx, fy_f - 5, '#dce6f2')
    for yy in (fy_f - 8, fy_f - 7):
        put(fx_f - 1, yy, '#1e2438')
        put(fx_f, yy, '#1e2438')
    if FASE != 'dia':
        for wx_f in range(-5, 6, 2):
            put(fx_f + wx_f, fy_f - 3, '#ffe088')
        put(fx_f - 9, fy_f - 2, '#ff3658')
        put(fx_f + 9, fy_f - 2, '#54ff98')
    for k in range(1, 7):
        over(fx_f - 10 - k * 2, fy_f + 1, '#d4ecff', 0.45 * (1 - k / 8.0))

# 6. Vista previa estática / fondo.png: Miles Morales en pleno balanceo con telaraña (en ANIM lo dibuja el motor en movimiento)
if not ANIM:
    MILES_SWING = [
        "..........................RRK.",
        ".........................RRKK.",
        "........................KKK...",
        ".......................KKK....",
        "...........KKKKKK.....KKK.....",
        "..........KKKKKKKK...KKK......",
        ".........KKWWKKWWKK.KKK.......",
        ".........KKWWKKWWKKSSK........",
        "..........KKKKKKKKSSK.........",
        ".........KKKKKKKKKSK..........",
        "........KKRRKKKRRKK...........",
        ".......SSKRRRRRRKK............",
        "......SSKKRKKRRKKK..KKKK......",
        ".....SS.KKRRRRKKKKKKKSSKK.....",
        "....RR..KKKKRKKKKKKK...KKK....",
        "....RE...KKSSKK.........SSK...",
        "........KKK..KKK........RRR...",
        ".......KKK....KK........WWW...",
        "......KKK.....................",
        "......KKK.....................",
        ".....RRR......................",
        ".....WWW......................",
    ]
    w_m = max(len(r) for r in MILES_SWING)
    MILES_SWING = [r.ljust(w_m, '.') for r in MILES_SWING]
    su_b, su_r = PAL['suit']
    col_map = {
        'K': su_b,
        'S': '#282d4c',
        'R': su_r,
        'W': '#f4f8ff',
        'E': PAL['neon_c'],
    }
    mx_s, my_s = 166, 92
    hx, hy = mx_s + (27 - 15), my_s + (0 - 11)
    ax_top, ay_top = mx_s + 60, 0
    steps = max(abs(ax_top - hx), abs(ay_top - hy))
    for i in range(steps + 1):
        wx = int(round(hx + (ax_top - hx) * i / steps))
        wy = int(round(hy + (ay_top - hy) * i / steps))
        over(wx, wy, PAL['web'], 0.88 if i % 2 == 0 else 0.72)
    for r_idx, row in enumerate(MILES_SWING):
        for c_idx, ch in enumerate(row):
            if ch != '.':
                put(mx_s + c_idx - 15, my_s + r_idx - 11, col_map[ch])
    glow(mx_s - 11, my_s + 4, 4, PAL['neon_c'], 0.45)
    put(mx_s - 12, my_s + 5, PAL['neon_y'])

# Barandilla urbana en primer plano (esquinas inferiores)
for cx_s in range(0, 74):
    h_s = int(20 * math.cos(cx_s / 74 * 1.57))
    for yy in range(H - h_s, H):
        put(cx_s, yy, PAL['suelo'][0] if (cx_s + yy) % 3 else PAL['suelo'][1])
for cx_s in range(W - 68, W):
    h_s = int(18 * math.cos((W - 1 - cx_s) / 68 * 1.57))
    for yy in range(H - h_s, H):
        put(cx_s, yy, PAL['suelo'][2] if (cx_s + yy) % 3 else PAL['suelo'][3])

# Chispas Venom bioeléctricas en las esquinas inferiores
for vx_e, vy_e in ((24, H - 14), (48, H - 10), (W - 42, H - 12)):
    if ANIM:
        RUNAS.append([vx_e, vy_e])
    else:
        put(vx_e, vy_e, PAL['neon_y'])
        glow(vx_e, vy_e, 4, PAL['neon_c'], 0.55)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
             chimenea=CHIMENEA, destellos=DESTELLOS, barca=[197, HOR - 8], luna=[MX, MY, MR])
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
