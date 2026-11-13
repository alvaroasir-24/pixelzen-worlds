#!/usr/bin/env python3
"""PixelZen Worlds - Hunter x Hunter (Monitor 2): Greed Island."""
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
random.seed(1711)

PALETAS = {
    'noche': dict(
        sky=['#040914', '#081326', '#0d2038', '#122f4b', '#19405e', '#225370', '#2d6880', '#3d7d90', '#50939c', '#68a6a6'],
        mont=['#1d3d4a', '#15303c', '#0f2530', '#0a1b24', '#07131a'],
        mist=['#3b7b84', '#2e6470', '#234e5a', '#193b46', '#102832'],
        isla=('#0a1e18', '#123024', '#1d4c36', '#2a6848'),
        sand=('#7a6c4e', '#584c36'),
        wall=('#7c6e54', '#584e3c'),
        roof=('#14402c', '#1e5c40', '#2c7e54'),
        gold=('#f4ce5c', '#a88224', '#fff4b0'),
        ring=('#4a5c6c', '#7c94a8', '#2c3844'),
        card=('#e8eed8', '#226458', '#f4ce5c', '#54b8ff'),
        agua='#061824',
        ola=('#6ee0cc', '#2e7c90', '#143c52'),
        vig=0.76,
        nube=['#2e5472', '#3c6886', '#4a7a98', '#6090aa', '#78a6ba', '#284a66'],
        rama=('#160e0a', '#2c1c14'),
        hoja={'l': '#5ee080', 'c': '#3ab860', 'm': '#248c48', 'd': '#145a30', 'x': '#0c341c'},
        nen=('#48f09c', '#b8ffe0'),
        elec=('#54b8ff', '#d4f4ff'),
    ),
    'dorado': dict(
        sky=['#141e3c', '#223054', '#38446c', '#58587e', '#826882', '#ae787a', '#d6886c', '#f29e5e', '#ffba5e', '#ffd87e'],
        mont=['#4c5468', '#3c4256', '#2e3346', '#222636', '#171a28'],
        mist=['#dc9678', '#c07e70', '#9c6668', '#744e5e', '#4e384e'],
        isla=('#1e2e20', '#2c442a', '#406038', '#587c44'),
        sand=('#d8ae74', '#a47c50'),
        wall=('#c8a882', '#9a7e5c'),
        roof=('#1e543a', '#2c744e', '#3e9664'),
        gold=('#ffdc68', '#c48a24', '#fff8c4'),
        ring=('#726e7e', '#b6a8b2', '#443e4c'),
        card=('#fff8e6', '#2a7864', '#ffcf54', '#58c4ff'),
        agua='#1e3c4c',
        ola=('#ffd29c', '#88a0a8', '#3c586c'),
        vig=0.84,
        nube=['#a87088', '#d48a84', '#f2a47e', '#ffc288', '#ffe09e', '#8e5e78'],
        rama=('#22140c', '#3e2416'),
        hoja={'l': '#a8e468', 'c': '#72be4c', 'm': '#468e38', 'd': '#285e26', 'x': '#163616'},
        nen=('#60f8a8', '#dcffec'),
        elec=('#68d0ff', '#e4f8ff'),
    ),
    'dia': dict(
        sky=['#155cb8', '#2272ca', '#3488da', '#4c9ee6', '#6ab4ee', '#8cc8f4', '#aedcf8', '#cdeafa', '#e6f4f6', '#f8f6e0'],
        mont=['#4e809a', '#3e6e88', '#305c74', '#244b60', '#1a3a4c'],
        mist=['#b2deec', '#96cce0', '#7ab8d2', '#5ea2c0', '#448aa8'],
        isla=('#1e482c', '#2c6438', '#3e8448', '#56a65a'),
        sand=('#f2d89c', '#c8aa74'),
        wall=('#efe2c4', '#cbb896'),
        roof=('#226846', '#2e845a', '#40a070'),
        gold=('#ffe46a', '#c89a28', '#fffce0'),
        ring=('#8ea4b8', '#d6e6f2', '#52687c'),
        card=('#ffffff', '#26846c', '#ffd448', '#38a8ff'),
        agua='#166a82',
        ola=('#d2faf6', '#66b8cc', '#287690'),
        vig=0.92,
        nube=['#ffffff', '#f0f8fc', '#ffffff', '#e4f2fa', '#f6fcff', '#dcf0fa'],
        rama=('#2c1c10', '#4a2e1a'),
        hoja={'l': '#8ee868', 'c': '#5ac448', 'm': '#369434', 'd': '#1e6222', 'x': '#103a14'},
        nen=('#48f09c', '#d8fff0'),
        elec=('#54b8ff', '#e0f8ff'),
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

# 1. Cielo + astro
render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#48f09c', '#54b8ff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 44, halo='#7ee8d8', base='#f2fcf8', sombra='#c6e0dc', crater='#9ec0be', crater_hi='#b8d6d4'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 24, halo='#ffe498', centro='#fffef0', borde='#ffd05c', rayo='#ffe89c'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#d8fff0', '#bce8ff', '#98c8f0'])

MX, MY, MR = 408, 80, 40
CX_ASTRO = MX if FASE == 'noche' else (MX + 22 if FASE == 'dorado' else MX - 36)
# Monitor 2 comparte cielo con Monitor 1: no duplicar sol/luna aquí

NUBES_DEF = [
    (115, 64, 165, PAL['nube'][0], 3),
    (320, 48, 155, PAL['nube'][1], 3),
    (520, 114, 160, PAL['nube'][2], 3),
    (215, 168, 180, PAL['nube'][3], 2),
    (445, 208, 145, PAL['nube'][4], 2),
    (75, 238, 115, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 2. Montañas y archipiélago de Greed Island en el horizonte (descenso suave desde x = 115)
for base, amp, seed, col, mist in (
    (242, 62, 31, PAL['mont'][0], PAL['mist'][0]),
    (258, 46, 32, PAL['mont'][1], PAL['mist'][1]),
    (272, 30, 33, PAL['mont'][2], PAL['mist'][2]),
):
    r = Ruido(seed * 19)
    for x in range(115, W):
        t_ramp = max(0.0, min(1.0, (x - 115) / 130.0))
        ramp = (t_ramp * t_ramp * (3.0 - 2.0 * t_ramp)) * (1.0 if x < 450 else 0.72)
        top = int(HOR - (HOR - base + amp * fbm(r, x * 0.018 + seed)) * ramp)
        for y in range(top, HOR + 1):
            put(x, y, mix(col, mist, 0.28 * ((y - top) / max(1, HOR - top)) ** 1.8))

# 3. ISLA CENTRAL DE GREED ISLAND: mesetas planas bajo Masadora, Portal y Castillo de Limeiro (x = 194..470)
IS0, IS1, IS2, IS3 = PAL['isla']
for x in range(194, 470):
    if x < 232:
        t_l = (x - 194) / 38.0
        elev = int(32 * (t_l ** 0.75))
    elif x <= 426:
        elev = 32
    else:
        t_r = (470 - x) / 44.0
        elev = int(32 * (t_r ** 0.75))
    for y in range(HOR - elev, HOR + 1):
        c = IS3 if y < HOR - elev + 4 else (IS2 if y < HOR - 6 else PAL['sand'][0])
        if y >= HOR - 3:
            c = PAL['sand'][1]
        put(x, y, c)

# Peñón natural + cascada cristalina tras el Castillo de Limeiro (x ~ 414..450)
r_peak = Ruido(413)
for x in range(398, 456):
    t_p = 1.0 - abs(x - 428) / 30.0
    if t_p <= 0:
        continue
    top_p = int(HOR - 26 - 48 * (t_p ** 0.85) * (0.75 + 0.35 * r_peak(x * 0.18)))
    for yy in range(top_p, HOR - 18):
        c = IS2 if yy < top_p + 5 else (IS1 if r_peak(x * 0.2 + yy * 0.15) > 0.45 else IS0)
        put(x, yy, c)
# Cascada de Greed Island cayendo desde el peñón hasta el mar
for yy in range(HOR - 54, HOR + 1):
    for dx in (-2, -1, 0, 1):
        if dx == 0 or (yy + dx) % 3:
            put(436 + dx, yy, PAL['ola'][0] if dx <= 0 else PAL['ola'][1])
# Castillo blanco/verde de Limeiro (anclado en terraza elev=32 hasta HOR - 28)
for x in range(358, 418):
    for yy in range(HOR - 54, HOR - 28):
        put(x, yy, PAL['wall'][0] if x < 388 else PAL['wall'][1])
def torre_limeiro(cx, tw, th, sh):
    y0 = HOR - 54 - th
    for yy in range(y0, HOR - 52):
        for x in range(cx - tw // 2, cx + tw // 2 + 1):
            put(x, yy, PAL['wall'][0] if x < cx else PAL['wall'][1])
    for wy in range(y0 + 6, HOR - 56, 10):
        if ANIM:
            VENTANAS.append([cx - 1, wy])
        else:
            put(cx - 1, wy, '#ffd074')
            put(cx, wy, '#ffd074')
    for i in range(sh):
        hw = max(0, int((tw // 2 + 2) * (1 - i / max(1, sh - 1))))
        for x in range(cx - hw, cx + hw + 1):
            put(x, y0 - i, PAL['roof'][2] if x < cx else PAL['roof'][0])
    put(cx, y0 - sh - 2, PAL['gold'][0])

torre_limeiro(368, 12, 22, 12)
torre_limeiro(388, 18, 36, 18)
torre_limeiro(408, 12, 24, 12)

# Ciudad inicial de Masadora bien cimentada sobre la terraza plana (x = 236..312)
for cx_m, cw, ch in ((238, 22, 16), (266, 24, 20), (294, 18, 14)):
    hy0 = HOR - 30 - ch
    for yy in range(hy0, HOR - 28):
        for x in range(cx_m, cx_m + cw):
            put(x, yy, PAL['wall'][0] if x < cx_m + cw // 2 else PAL['wall'][1])
    for i in range(10):
        hw = max(1, cw // 2 + 2 - i)
        for x in range(cx_m + cw // 2 - hw, cx_m + cw // 2 + hw + 1):
            put(x, hy0 - i, PAL['roof'][1] if x < cx_m + cw // 2 else PAL['roof'][0])
    if ANIM:
        VENTANAS.append([cx_m + 6, hy0 + 6])
        VENTANAS.append([cx_m + cw - 8, hy0 + 6])
CHIMENEA = [272, HOR - 58]

# 4. GRAN ANILLO / PUERTA ARCANO DE GREED ISLAND ("G.I." Ring Portal, cx = 318, cy = 148)
AX, AY, AR_OUT, AR_IN = 318, 152, 42, 31
# Pilares base del portal en la isla
for px_p in (AX - 36, AX + 36):
    for yy in range(AY + 10, HOR - 26):
        for dx in range(-4, 5):
            put(px_p + dx, yy, PAL['ring'][1] if dx < 0 else PAL['ring'][0])
# Anillo circular metálico de Greed Island (con la esmeralda superior como el Anillo oficial)
for y in range(AY - AR_OUT - 2, AY + AR_OUT + 3):
    for x in range(AX - AR_OUT - 2, AX + AR_OUT + 3):
        d = math.hypot(x - AX, y - AY)
        if AR_IN <= d <= AR_OUT:
            c = PAL['ring'][1] if x < AX and y < AY else (PAL['ring'][0] if d < AR_OUT - 2 else PAL['ring'][2])
            if abs(d - (AR_IN + AR_OUT) * 0.5) < 1.3 and ((x + y) % 5 == 0):
                c = PAL['nen'][0]
            put(x, y, c)
# Joya / piedra central superior del Anillo ("G.I." Gemstone) + letras "G I" dentro del aura
for dy in range(-6, 7):
    hw = 6 - abs(dy) // 2
    for dx in range(-hw, hw + 1):
        put(AX + dx, AY - AR_OUT + dy, PAL['nen'][1] if (abs(dx) < 3 and dy < 0) else PAL['nen'][0])
if ANIM:
    RUNAS.append([AX, AY - AR_OUT])
else:
    glow(AX, AY - AR_OUT, 10, PAL['nen'][0], 0.65)
# Halo suave Nen interior del portal + sigilo G.I. sutil
for y in range(AY - AR_IN + 3, AY + AR_IN - 2):
    for x in range(AX - AR_IN + 3, AX + AR_IN - 2):
        d = math.hypot(x - AX, y - AY)
        if d < AR_IN - 3 and dith(x, y, 0.25 * (1 - d / AR_IN)):
            over(x, y, PAL['nen'][0], 0.4)

# 5. CARTAS DE HECHIZO DE GREED ISLAND FLOTANDO EN EL CIELO (Spell Cards con aura Nen!)
def dibuja_carta_gi(cx, cy, w_c, h_c, acento, tipo='estrella'):
    """Dibuja una carta de hechizo pixel art de Greed Island con marco dorado y símbolo."""
    x0, y0 = cx - w_c // 2, cy - h_c // 2
    c_bg, _, c_gold, c_cyan = PAL['card']
    # Aura Nen envolvente
    if not ANIM:
        glow(cx, cy, max(w_c, h_c), acento, 0.42)
    # Cuerpo y borde dorado de la carta
    for yy in range(y0, y0 + h_c):
        for xx in range(x0, x0 + w_c):
            borde = (xx in (x0, x0 + w_c - 1) or yy in (y0, y0 + h_c - 1))
            inner = (xx in (x0 + 2, x0 + w_c - 3) or yy in (y0 + 2, y0 + h_c - 3))
            if borde:
                put(xx, yy, c_gold)
            elif inner and y0 + 2 <= yy <= y0 + h_c - 3 and x0 + 2 <= xx <= x0 + w_c - 3:
                put(xx, yy, acento)
            else:
                put(xx, yy, c_bg)
    # Banda superior de título (nombre + rango) y recuadro de ilustración
    for xx in range(x0 + 3, x0 + w_c - 3):
        put(xx, y0 + 4, PAL['gold'][1])
        put(xx, y0 + 5, c_gold)
    # Ilustración central según el hechizo
    icy = cy + 2
    if tipo == 'estrella':  # Ruler's Blessing N°000
        for dy in range(-5, 6):
            hw = 5 - abs(dy) if abs(dy) > 1 else 6
            for dx in range(-hw, hw + 1):
                if abs(dx) + abs(dy) <= 6 or abs(dx) == 0 or abs(dy) == 0:
                    put(cx + dx, icy + dy, c_gold if abs(dx) + abs(dy) > 2 else PAL['gold'][2])
    elif tipo == 'ala':  # Angel's Breath
        for sgn in (-1, 1):
            for t in range(6):
                put(cx + sgn * (1 + t), icy - t // 2, c_cyan)
                put(cx + sgn * (1 + t), icy - t // 2 + 1, acento)
    elif tipo == 'brújula':  # Accompany
        for d_a in (-4, -3, -2, -1, 0, 1, 2, 3, 4):
            put(cx + d_a, icy, acento)
            put(cx, icy + d_a, acento)
        put(cx, icy, c_gold)
    else:  # Gain / Nen
        for dy in range(-4, 5):
            hw = 4 - abs(dy)
            for dx in range(-hw, hw + 1):
                put(cx + dx, icy + dy, acento)
    if ANIM:
        RUNAS.append([cx, y0 - 2])

# 4 cartas icónicas flotando sobre el mar y la isla (todas en x=96..452, fuera del HUD!)
dibuja_carta_gi(102, 118, 22, 30, PAL['card'][3], 'brújula')   # Accompany
dibuja_carta_gi(178, 86, 26, 36, PAL['card'][2], 'estrella')   # Ruler's Blessing 000
dibuja_carta_gi(248, 124, 22, 30, PAL['nen'][0], 'gain')       # Gain
dibuja_carta_gi(426, 178, 22, 30, PAL['card'][3], 'ala')       # Angel's Breath

# 6. PROMONTORIO IZQUIERDO PLANO (x = 0..176): Pedestal "BOOK!" + GON y KILLUA jugando juntos
r_grass = Ruido(617)
for x in range(0, 176):
    if x <= 146:
        ridge = HOR - 36
    else:
        t_down = (x - 146) / 30.0
        ridge = HOR - 36 + int((t_down * t_down) * 36)
    for y in range(max(0, ridge), HOR + 1):
        d_y = y - ridge
        n_g = r_grass(x * 0.16 + y * 0.22)
        c = IS3 if d_y < 4 else (IS2 if n_g > 0.45 else (IS1 if n_g > 0.25 else IS0))
        if d_y == 2 and x % 19 == 0:
            c = PAL['gold'][0]
        put(x, y, c)

# Pedestal con el Libro de Cartas ("BOOK!" Binder abierto) a la izquierda (x = 28)
PX_B, PY_B = 28, HOR - 35
for yy in range(PY_B - 12, PY_B + 1):
    for dx in range(-8, 9):
        put(PX_B + dx, yy, PAL['ring'][0] if dx > 0 else PAL['ring'][1])
for dy in range(-6, 1):
    for dx in range(-11, 12):
        if abs(dx) == 11 or dy in (-6, 0):
            put(PX_B + dx, PY_B - 12 + dy, PAL['rama'][0])
        elif dx == 0:
            put(PX_B + dx, PY_B - 12 + dy, PAL['gold'][1])
        else:
            put(PX_B + dx, PY_B - 12 + dy, PAL['card'][0] if dy > -4 else PAL['nen'][1])
if ANIM:
    FAROLES.append([PX_B, PY_B - 20, 12])
else:
    glow(PX_B, PY_B - 18, 9, PAL['nen'][0], 0.48)


def dibuja_gon_jugando(cx, by):
    """Gon Freecss en pose dinámica de juego (brazos alzados lanzando/recibiendo pelota, sonrisa entusiasta)."""
    cmap = {
        'O': '#0a0f0c',
        'H': '#0e1b14', 'E': '#1a4c2e', 'L': '#26683e',
        'S': '#f4d2ba', 's': '#d2aa90', 'I': '#2a1810',
        'W': '#f2f6ee',
        'G': '#248c46', 'g': '#176632', 'd': '#104622',
        'R': '#ec6a2c', 'B': '#164626', 'b': '#0d2b16',
    }
    spr = [
        "....OO.......OO...........",
        "...OLLO.....OLLO..........",
        "...OEEO..OO.OEEO..OO......",
        "..OEHHEOOEEOOEHHOOEEO.....",
        "..OHHHHOEHHHOHHHHEHHO.....",
        "..OHHHHHHHHHHHHHHHHHO.....",
        "...OHHHHHHHHHHHHHHHO..OO..",
        "...OHHSSSSSSSSSSSHHO.OSSO.",
        "....OHSSISSSISSSSHOO.OSSO.",
        "....OSSSSSSSSSSSSOOOOSSO..",
        ".....OSSSSsSSSSSSOOOGGO...",
        "......OOSSSSSSSOOOGGGO....",
        ".......ORRWGGGWRGGGO......",
        "...OOOOORWWWWWWWGGGO......",
        "..OSSOOGGWWWWWWWWGO.......",
        "..OSSO.OGGGGGGGGGGO.......",
        "...OO..OGGGggGGGGO........",
        ".......ORRRRRRRRRO........",
        "......OGGGGGGGGGGO........",
        "......OGGggOOggGGO........",
        "......OSSO....OSSO........",
        ".....OSSO......OSSO.......",
        "....OBBO........OBBO......",
        "....OBbO........OBbO......",
        "...OBbBO........OBbBO.....",
        "...OOOOO........OOOOO.....",
    ]
    assert len({len(r) for r in spr}) == 1
    pinta_sprite(lz, cx, by, spr, cmap)


def dibuja_killua_jugando(cx, by):
    """Killua Zoldyck sobre su patineta amarilla jugando con Gon y lanzando chispas Nen."""
    cmap = {
        'O': '#101424',
        'H': '#eef4ff', 'h': '#c2d2ee', 'g': '#90a6cc',
        'S': '#f8e2d6', 's': '#d8bcb0', 'E': '#2264d8',
        'B': '#1e2c64', 'W': '#f4f6fc', 'w': '#cfd8ea',
        'P': '#222240', 'p': '#16162c',
        'K': '#3e3a88', 'Z': '#e8eef8',
        'Y': '#ffd238', 'y': '#d48c1c',  # Patineta clásica de Killua
    }
    spr = [
        "......OO..OO..OO..........",
        "....OOHHOOHHOOHHOO........",
        "...OHHHHHHHHHHHHHHO.......",
        "..OHhHHHHHHHhHHHHHhO......",
        ".OHggHHHHHHHHHHHggHHO.....",
        ".OOghHHSSSSSSSSSHHhgO.....",
        ".OSSOHSSESSSESSSSHHO......",
        ".OSSOOSSSsSSSsSSSSO.......",
        "..OSSOOSSSSSSSSSSO........",
        "...OGGGOOBBBBBBOO.........",
        "....OGGWWBBBBBBWWO........",
        "....OWWWWWBBBBWWWWO.......",
        "....OWWWwWWWWWWwWWWO......",
        ".....OWWWOWWWWWO..OSSO....",
        "......OBBBBBBBBO...OO.....",
        "......OPPPPPPPPO..........",
        ".....OPPPppOOppPO.........",
        ".....OSSO....OSSO.........",
        "....OSSO......OSSO........",
        "...OKKO........OKKO.......",
        "...OZZO........OZZO.......",
        "..OYYYYYYYYYYYYYYYYO......",
        "..OyyyyyyyyyyyyyyyyO......",
        "...OO.OO......OO.OO.......",
    ]
    assert len({len(r) for r in spr}) == 1
    pinta_sprite(lz, cx, by, spr, cmap)


# Gon (izq) y Killua (der) pasándose un balón de Nen / Dodgeball brillante entre sí
dibuja_gon_jugando(70, HOR - 36)
dibuja_killua_jugando(132, HOR - 36)

# Pelota de Dodgeball de Greed Island en pleno vuelo + estela de juego entre ambos
BX_B, BY_B = 102, HOR - 66
disc(BX_B, BY_B, 5, '#ff4c58')
disc(BX_B - 1, BY_B - 1, 3, '#ffd858')
put(BX_B - 2, BY_B - 2, '#ffffff')
for k_arc in range(-12, 13, 4):
    ax_p = BX_B + k_arc
    ay_p = BY_B + (k_arc * k_arc) // 18 + 3
    over(ax_p, ay_p, PAL['elec'][1], 0.72)
if ANIM:
    RUNAS.append([BX_B, BY_B])
    RUNAS.append([120, HOR - 54])
else:
    glow(BX_B, BY_B, 7, '#ffaa44', 0.45)
    glow(120, HOR - 54, 5, PAL['elec'][0], 0.50)

# Pequeño farol en el muelle de Masadora
for xx_m in range(190, 224):
    put(xx_m, HOR - 5, PAL['wall'][1])
for px_d in (194, 210):
    for yy in range(HOR - 9, HOR + 1):
        put(px_d, yy, PAL['rama'][0])
if ANIM:
    FAROLES.append([194, HOR - 11, 9])

# 7. Reflejo en el mar turquesa de Greed Island (sin columna duplicada de sol/luna)
render_lago(lz, PAL['agua'], PAL['ola'], DESTELLOS, ANIM, mx=CX_ASTRO, reflejo_cols=(PAL['nen'][1], PAL['ola'][0]), reflejo_astro=False)

# 8. Rama tropical orgánica en esquina superior derecha (sin interferir con el HUD ni tapar islas)
lz.rama([(644, 32), (608, 44), (572, 54), (546, 60)], 6, 1.4, PAL['rama'][0], PAL['rama'][1])
lz.rama([(600, 46), (588, 76)], 3.5, 1, PAL['rama'][0], PAL['rama'][1])
HOJA = PAL['hoja']
for cx, cy, R in ((626, 30, 24), (590, 42, 22), (558, 52, 18), (586, 70, 16)):
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
