#!/usr/bin/env python3
"""PixelZen Worlds - Continente Demoníaco (Monitor 2): Castillo de Atofe y Atoferatofe Raibaku."""
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
random.seed(2911)

PALETAS = {
    'noche': dict(
        sky=['#060310', '#0d061d', '#16092b', '#220d39', '#311246', '#431750', '#581d58', '#6f255e', '#883062', '#a23f64', '#bc5268', '#d46b70', '#e68b7c'],
        mont=['#3c1f48', '#2f173c', '#22102f', '#170a23', '#0e0518'],
        mist=['#8a4c78', '#703b66', '#562b52', '#3c1e3e', '#26122b'],
        filo='#f4aac6',
        cliff=('#14081c', '#22102c', '#361c42', '#4e2858'),
        castle=('#180e22', '#261734', '#38244a', '#4e3462'),
        dome=('#3a1026', '#621a38', '#8e2a4e'),
        armor=('#0d0914', '#1d1628', '#342946', '#9a8ca8'),
        wing=('#090610', '#181026', '#4a1c42'),
        hair=('#c8c2d8', '#8e84a4'),
        cape=('#621428', '#922038'),
        lava=('#e8385c', '#ff9468'),
        agua='#0b0416',
        ola=('#e06ea0', '#7e3672', '#3c1848'),
        vig=0.72,
        nube=['#4e285c', '#6c386e', '#8c4476', '#b85676', '#cf6e78', '#442454'],
        mana=('#ff4c94', '#a81e5c'),
        hongo=('#5ef2e4', '#b4fff6', '#228c88', '#14444a'),
        shroom_stem=('#241832', '#3c284e'),
    ),
    'dorado': dict(
        sky=['#1b082c', '#2b0e3e', '#41154e', '#5e1c58', '#80235a', '#a42c54', '#c63b4c', '#e25244', '#f47044', '#fc904c', '#ffb25c', '#ffd076', '#ffe69e'],
        mont=['#6d2c4f', '#562141', '#401733', '#2c0f24', '#1b0817'],
        mist=['#e87868', '#c85862', '#a0425c', '#763052', '#4c2042'],
        filo='#ffc496',
        cliff=('#220e1c', '#36182a', '#52263c', '#70384e'),
        castle=('#241222', '#361c32', '#4e2a46', '#683a5a'),
        dome=('#5e1624', '#8e2432', '#bc3844'),
        armor=('#140b14', '#281826', '#422a3e', '#c0a2b4'),
        wing=('#0e0810', '#241424', '#6c2240'),
        hair=('#e2d2dc', '#a68ca4'),
        cape=('#7c1826', '#b42838'),
        lava=('#ff5050', '#ffb868'),
        agua='#28102c',
        ola=('#f49e84', '#a44c6c', '#542048'),
        vig=0.80,
        nube=['#8c426a', '#ba586e', '#e07268', '#f6986a', '#ffb878', '#74385c'],
        mana=('#ff6aa4', '#b82868'),
        hongo=('#78f8e6', '#d8fff8', '#2ea89c', '#185458'),
        shroom_stem=('#382238', '#563652'),
    ),
    'dia': dict(
        sky=['#382854', '#4b3668', '#62467a', '#7c568a', '#966894', '#af7c9a', '#c6929c', '#daa89c', '#eabc9c', '#f2cba0', '#f6d8ac', '#fae4bc', '#fcedcc'],
        mont=['#7e587c', '#68466a', '#523556', '#3e2644', '#2a1832'],
        mist=['#dbb2a8', '#c49698', '#a8788c', '#885c7c', '#684268'],
        filo='#ffe4d4',
        cliff=('#2c182c', '#422642', '#5e385c', '#7c4c76'),
        castle=('#301e36', '#462c4e', '#62406a', '#825888'),
        dome=('#762638', '#a43848', '#cc545c'),
        armor=('#1a1222', '#2e223a', '#48385a', '#d8c8de'),
        wing=('#140d1c', '#2c1e38', '#78345a'),
        hair=('#f2e8f4', '#b8a4c2'),
        cape=('#8a2034', '#be3448'),
        lava=('#ff5868', '#ffbe78'),
        agua='#3e204c',
        ola=('#ecc0c6', '#a4688c', '#5e3264'),
        vig=0.90,
        nube=['#f6dcd8', '#f0c8ca', '#fae4dc', '#ffe8d4', '#f8d8d6', '#e0b8c4'],
        mana=('#ff5c9c', '#b42262'),
        hongo=('#78f4e8', '#d4fffc', '#34a8a2', '#1e5860'),
        shroom_stem=('#46324a', '#684c6c'),
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

# 1. Cielo volcánico-púrpura + astro
render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#e04898', '#ff7c50'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 46, halo='#e878a8', base='#fde4ea', sombra='#d89eb4', crater='#b67490', crater_hi='#cca0b4'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 24, halo='#ff9860', centro='#fff4d6', borde='#ff7840', rayo='#ffb870'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffd6e8', '#d6b8ff', '#a890d8'])

MX, MY, MR = 368, 82, 44
CX_ASTRO = MX if FASE == 'noche' else (MX + 35 if FASE == 'dorado' else MX - 35)
# Monitor 2 comparte cielo con Monitor 1: no duplicar sol/luna aquí

NUBES_DEF = [
    (120, 68, 175, PAL['nube'][0], 3),
    (315, 50, 155, PAL['nube'][1], 3),
    (520, 118, 160, PAL['nube'][2], 3),
    (220, 170, 180, PAL['nube'][3], 3),
    (445, 214, 150, PAL['nube'][4], 2),
    (75, 244, 110, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 2. Cordilleras afiladas y picos volcánicos del Continente Demoníaco
def rampa(x):
    return 1.0 if x < 430 else max(0.32, 1.0 - (x - 430) / 140.0 * 0.68)

for base, amp, seed, fr, col, mist in (
    (238, 104, 21, 0.012, PAL['mont'][0], PAL['mist'][0]),
    (252, 84, 22, 0.017, PAL['mont'][1], PAL['mist'][1]),
    (264, 62, 23, 0.023, PAL['mont'][2], PAL['mist'][2]),
    (274, 44, 24, 0.031, PAL['mont'][3], PAL['mist'][3]),
):
    r, ra = Ruido(seed * 17), Ruido(seed * 41 + 2)
    for x in range(W):
        n = fbm(r, x * fr * 1.4 + seed)
        agudo = 1 - abs(2 * n - 1)
        am = 0.32 + 0.90 * ra(x * 0.013 + seed) ** 1.25
        top = int(base - amp * rampa(x) * am * (0.68 * agudo + 0.32 * n))
        for y in range(top, HOR + 1):
            d = y - top
            cc = mix(col, mist, 0.24 * (d / max(1, HOR - top)) ** 2.0)
            if d < 2:
                cc = mix(cc, PAL['filo'], 0.22)
            put(x, y, cc)

# Grietas volcánicas luminosas en el pico izquierdo distante
for dx_v in range(-12, 13, 6):
    for yy in range(215, HOR - 38):
        put(42 + dx_v + ((yy // 5) % 2), yy, PAL['lava'][0] if yy % 3 else PAL['lava'][1])

# 3. Acantilado y CASTILLO DE ATOFE (x = 58..318)
CL0, CL1, CL2, CL3 = PAL['cliff']
CS0, CS1, CS2, CS3 = PAL['castle']
DM0, DM1, DM2 = PAL['dome']
AR0, AR1, AR2, AR3 = PAL['armor']
MANA_HI, MANA_LO = PAL['mana']
WARM = '#ff7848'

# Acantilado escarpado base del castillo con textura orgánica volcánica
r_rock = Ruido(803)
for x in range(24, 336):
    if x < 64:
        ridge = HOR - 18 - int((x - 24) * 0.7)
    elif x < 292:
        ridge = HOR - 46 + int(4 * math.sin(x * 0.08))
    else:
        ridge = HOR - 46 + int((x - 292) * 0.85)
    for y in range(max(0, ridge), HOR + 1):
        c = CL2 if y < ridge + 4 else (CL1 if r_rock(x * 0.14 + y * 0.22) > 0.48 else CL0)
        if (y - ridge) % 10 == 0 and r_rock(x * 0.09) > 0.42:
            c = CL2
        if y == ridge:
            c = CL3
        put(x, y, c)

# Muralla principal del Castillo de Atofe (x = 80..294)
for x in range(80, 294):
    for yy in range(HOR - 76, HOR - 42):
        c = CS2 if x < 186 else CS1
        if (yy % 7 == 0) or (x % 14 == 0 and (yy // 7) % 2 == 0):
            c = CS0
        put(x, yy, c)
    # Almenas puntiagudas en forma de colmillos
    if x % 8 < 4:
        put(x, HOR - 78, CS3)
        put(x, HOR - 79, DM1 if x % 8 in (1, 2) else CS2)

# Gran Puerta Demoníaca arqueada con emblema de cuernos sobre el dintel
PX_G, PY_G = 186, HOR - 44
for dy in range(-22, 1):
    hw = 14 if dy > -10 else int(14 * math.sqrt(max(0, 1 - ((-dy - 10) / 12.0) ** 2)))
    for dx in range(-hw, hw + 1):
        put(PX_G + dx, PY_G + dy, '#0a0410' if abs(dx) < hw - 1 else CS3)
# Fuego/sello demoníaco en el umbral y sobre la puerta
for sx_r in (PX_G - 17, PX_G + 17):
    for yy in range(PY_G - 18, PY_G):
        put(sx_r, yy, AR1)
    if ANIM:
        FAROLES.append([sx_r, PY_G - 19, 10])
    else:
        disc(sx_r, PY_G - 19, 2, MANA_HI)
        glow(sx_r, PY_G - 19, 7, MANA_LO, 0.65)
# Emblema de cráneo con cuernos de Atofe sobre la puerta
disc(PX_G, HOR - 80, 4, AR3)
for sgn in (-1, 1):
    for t in range(8):
        put(PX_G + sgn * (4 + t), HOR - 82 - t // 2, DM2)

# Torreones del Castillo de Atofe con cúpulas y cuernos curvados
def torre_atofe(cx, tw, th, sh, central=False):
    y0 = HOR - 74 - th
    for yy in range(y0, HOR - 72):
        for x in range(cx - tw // 2, cx + tw // 2 + 1):
            c = CS3 if x < cx - tw // 4 else (CS2 if x < cx + tw // 4 else CS0)
            put(x, yy, c)
    # Ventanas llameantes
    for wy in range(y0 + 10, HOR - 80, 13):
        if ANIM:
            VENTANAS.append([cx - 2, wy])
            if central:
                VENTANAS.append([cx + 2, wy])
        else:
            put(cx - 2, wy, WARM)
            put(cx - 1, wy, WARM)
            if central:
                put(cx + 2, wy, WARM)
                put(cx + 3, wy, WARM)
    # Tejado cónico demoníaco
    for i in range(sh):
        hw = max(0, int((tw // 2 + 4) * (1 - i / max(1, sh - 1)) ** 1.1))
        for x in range(cx - hw, cx + hw + 1):
            put(x, y0 - i, DM2 if x < cx else DM0)
    # Cuernos laterales curvados en la cornisa de cada torre
    for sgn in (-1, 1):
        for t in range(11 if central else 8):
            put(cx + sgn * (tw // 2 + 2 + t // 2), y0 - t, AR3 if t > 4 else DM2)
    if central:
        if ANIM:
            RUNAS.append([cx, y0 - sh - 3])
        else:
            put(cx, y0 - sh - 3, MANA_HI)
            glow(cx, y0 - sh - 3, 7, MANA_LO, 0.7)
    return y0 - sh

top_t1 = torre_atofe(112, 24, 48, 28)
top_tc = torre_atofe(186, 40, 74, 42, central=True)
top_t2 = torre_atofe(260, 26, 52, 30)
CHIMENEA = [112, top_t1]

# Puente fortificado hacia el promontorio de Atofe (x = 294..364)
for x in range(294, 366):
    for yy in range(HOR - 42, HOR - 35):
        put(x, yy, AR1 if yy == HOR - 42 else CS0)
    if x % 14 == 0:
        for yy in range(HOR - 35, HOR + 1):
            put(x, yy, CS1)
            put(x + 1, yy, CS0)
# Dos caballeros de la Guardia Real Negra en el puente
for gx_k in (312, 338):
    for yy in range(HOR - 54, HOR - 42):
        for dx in (-2, -1, 0, 1, 2):
            put(gx_k + dx, yy, AR1 if abs(dx) < 2 else AR0)
    disc(gx_k, HOR - 56, 2, AR2)
    put(gx_k, HOR - 58, DM2)  # penacho/cuerno del casco
    for yy in range(HOR - 64, HOR - 42):
        put(gx_k + 4, yy, AR3 if yy < HOR - 58 else AR1)  # lanza

# 4. Promontorio derecho (x = 342..470) con ATOFERATOFE RAIBAKU (Atofe) fiel al diseño original
PX0, PX1, PY_TOP = 344, 468, HOR - 38
for y in range(PY_TOP, HOR + 1):
    d_y = y - PY_TOP
    for x in range(max(0, PX0 - d_y // 2), min(W, PX1 + d_y)):
        c = CL2 if d_y < 4 else (CL1 if r_rock(x * 0.14 + y * 0.22) > 0.48 else CL0)
        if d_y % 10 == 0 and r_rock(x * 0.09) > 0.45:
            c = CL2
        put(x, y, c)

def dibuja_atofe(cx, by):
    """Atoferatofe Raibaku: piel azul cobalto, cuerno central único, melena blanca voluminosa,
    alas carmesí pequeñas tras los hombros, armadura gris oscuro y espadón rojo horizontal."""
    # Paleta fiel a la referencia (adaptada sutilmente a la fase del cielo)
    skin = mix('#5c72b8', PAL['filo'], 0.08 if FASE == 'dia' else 0.0)
    skin_d = '#3e4f8e'
    skin_h = '#7d95dc'
    hair = mix('#ece9df', PAL['filo'], 0.06 if FASE != 'noche' else 0.0)
    hair_m = '#c8c4b8'
    hair_d = '#969288'
    horn = '#243062'
    horn_h = '#4658a4'
    wing_m = '#a81e30'
    wing_d = '#6e101e'
    arm_h = '#58607a'
    arm_m = '#383d4f'
    arm_d = '#212533'
    scab = '#981e2c'
    scab_d = '#66121d'
    sil = '#dcdce6'
    out = '#100c18'
    eye = '#ff4c24'
    eye_h = '#ffb844'

    # Sprite pixel art exacto (59x69 px): cada caracter mapea a un color nítido
    # . = transparente, O = contorno oscuro
    cmap = {
        'O': out,
        'H': hair, 'h': hair_m, 'g': hair_d,
        'N': horn, 'n': horn_h,
        'S': skin, 's': skin_d, 'L': skin_h,
        'E': eye, 'e': eye_h,
        'W': wing_m, 'w': wing_d,
        'A': arm_h, 'M': arm_m, 'D': arm_d,
        'R': scab, 'r': scab_d, 'G': sil,
    }

    # Espada horizontal detrás de la cintura + vaina roja con detalles plateados
    # Se dibuja primero para quedar detrás del cuerpo y brazos igual que en la referencia
    # Capa oscura interior detrás de las piernas (como en la referencia)
    spr = [
        "............................OO.............................",
        ".........................OOOHHOOO..........................",
        ".......................OOHHHNHHHHOO........................",
        "...............O......OOHHHHNNHHHHHO......O................",
        "..............OWO....OOHHHHHNNHHHHHHO....OWO...............",
        ".............OWwWO...OOHHHHHNNHHHHHHO...OWwWO..............",
        "............OWwwwWO..OOHHHHNNnHHHHHHO..OWwwwWO.............",
        "...........OWwwwwwWO.OOHHHHSSSHHHHHHO.OWwwwwwWO............",
        "...........OWWwwwwwWOOOHHLSSsSSLHHHHOOOWwwwwwWWO...........",
        "............OWWWwwwwWOHHHSESsSsSESHHHOWwwwwWWWWO...........",
        "............OWWWWWwwWOHHHSeSsSsSeSHHHOWwwWWWWWO............",
        ".............OWWWWWwWOHHHHSSsSsSSHHHHOWwWWWWWO.............",
        "..............OWWWWWWOOOHHHHSSSHHHHHOOWWWWWWO..............",
        ".............OHhOWWWWO.OOHODMMMDDOHO.OWWWWOOhHO............",
        "............OHHHhOOWOOOMMMMAAMMDDMOOOOOWOOhHHHHO...........",
        "...........OHHHHHhOOOMMMMMMAMMMAMMMMMMOOOhHHHHHHO..........",
        "..........OHHHHHHhOOAMMMSMMMMMMMMMSMMMAOOOhHHHHHHO.........",
        ".........OHHHHHHHhOOAMMMSsMAAMMAAMsSMMAOOOhHHHHHHHO........",
        "........OHHHHHHHHhOOAMMsSMMMMMMMMMMsMMAOOOhHHHHHHHHO.......",
        ".......OHHHHHHHHhhOODMMsSMMMMMMMMMMsMMDDOOhHHHHHHHHHO......",
        "........OHHHHHHHhhOODMsSDMMMAMAMMMDsSDDOOOhHHHHHHHHO.......",
        ".......OHHHHHHHHhhOOOMsSDMMMAMAMMMDMsMOOOOhHHHHHHHHO.......",
        "......OHHHHHHHHhhhOOOMMDMMMMAMAMMMMDMMOOOOhhhhhhhhhHO......",
        ".......OOHHHHHhhhhOOOMMMDDDDGGDDDDMMMOOOOhhhhhHHHOO........",
        "........OOHHHHhhhhOOOMMMMMMMMMMMMMMMMOOOOhhhhhHOO..........",
        ".........OOHhhggggOOMMMMMDMMMMMMDMMMMOOggggghOO............",
        "...........OOOOOOO.OMMMMMDMMMMMMDMMMMO.OOOOOO..............",
        "..................OOMMMDDDDDDDDDDMMMMOO....................",
        "..................OMMDDDDMDMMMDMDDMMMO.....................",
        "....OO............OMMDDMMMMMMMMDDMMMO................OOOO..",
        "...OGGOOOOO..OOO..OMDDMMMDMMMDDMMMDDMO......OOOOOOOOGGRGGO.",
        "..OGGGGGGGGGGGGGOOOMDMMMDMMMMMDMMMDDMO...OOORRRRRRRGGGGGGGO",
        "...OGGOOOOOOMMMGGOOMDMMDMODDDOMDMMMDMOOORRRRRRRRRGGGGGRGGO.",
        "....OO......OOGGGOMDMMDOO...OODMMMDMOOORRRRRRRRGRGGGGGO....",
        "..................OMDMMO.OSSBO.OMMMDMO.ORRRRGGGGGGGOOO.....",
        "..................OMMDMO.OSSBO.OMMDMMO..OOOOOOOOOO.........",
        "..................OOMDMOOSSSOOSSSOOMDOO....................",
        "...................OOMDOOSSsO.OsSSOMDO.....................",
        "....................OO.OODDD...DDDO.OO.....................",
        ".......................OOSSs...sSSOO.......................",
        ".......................OODDD...DDDOO.......................",
        ".......................OOSSs...sSSOO.......................",
        ".......................OODDD...DDDOO.......................",
        ".......................OOSSs...sSSOO.......................",
        ".......................OAMMMO.OMMMAO.......................",
        ".......................OAMMMO.OMMMAO.......................",
        ".......................OADDDO.ODDDDO.......................",
        ".......................OMMDMO.OMDMMO.......................",
        "......................OAMMDMO.OMDMMAO......................",
        "......................OAMMDMO.OMDMMAO......................",
        "......................OMMDDMO.OMDDMMO......................",
        "......................OMMDDMO.OMDDMMO......................",
        "......................ODDDDO...ODDDDO......................",
        "......................OMMMMO...OMMMMO......................",
        "......................ODDDDO...ODDDDO......................",
        ".....................OAMMDO.....ODMMAo.....................",
        ".....................ODDDDO.....ODDDDO.....................",
        "....................OAMMDO.......ODMMAo....................",
        "....................ODDDDO.......ODDDDO....................",
        "...................OAMMDO.........ODMMAo...................",
        "...................ODDDDO.........ODDDDO...................",
        "..................OADDDDO.........ODDDDAO..................",
        "..................OOOOOO...........OOOOOO..................",
    ]
    cmap['B'] = '#0d0a12'
    cmap['o'] = out

    sw = len(spr[0])
    sh = len(spr)
    x0 = cx - sw // 2
    y0 = by - sh + 1

    # Faldón negro interior detrás entre las piernas (como la capa oscura de su armadura)
    for dy in range(36, 56):
        hw = 7 + (dy - 36) // 5
        for dx in range(-hw, hw + 1):
            if dy > 50 and ((dx + dy) % 3 == 0):
                continue
            put(cx + dx, y0 + dy, '#12131e')

    for ry, row in enumerate(spr):
        for rx, ch in enumerate(row):
            col = cmap.get(ch)
            if col:
                put(x0 + rx, y0 + ry, col)

    # Reflejo brillante en ojos rojo-naranja
    put(x0 + 27, y0 + 9, eye_h)
    put(x0 + 31, y0 + 9, eye_h)

    if ANIM:
        RUNAS.append([cx, y0 + 5])
    else:
        glow(cx, y0 + 6, 8, MANA_LO, 0.25)

dibuja_atofe(406, PY_TOP)

# 5. Reflejo en el mar de obsidiana (sin duplicar astro en Monitor 2)
render_lago(lz, PAL['agua'], PAL['ola'], DESTELLOS, ANIM, mx=CX_ASTRO, reflejo_cols=(PAL['filo'], PAL['ola'][0]), reflejo_astro=False)

# 6. Hongos bioluminiscentes del Continente Demoníaco en primer plano
for hx_m, hy_m, hr in ((36, 376, 8), (60, 384, 5), (596, 372, 9), (620, 382, 6)):
    for yy in range(hy_m, min(H, hy_m + 18)):
        for dx in range(-2, 3):
            put(hx_m + dx, yy, PAL['shroom_stem'][0 if dx >= 0 else 1])
    for dy in range(-hr, 2):
        hw = int(hr * math.sqrt(max(0, 1 - (dy / hr) ** 2)))
        for dx in range(-hw, hw + 1):
            put(hx_m + dx, hy_m + dy, PAL['hongo'][1] if dy < -hr // 2 else PAL['hongo'][0])
    if not ANIM:
        glow(hx_m, hy_m - 2, hr + 3, PAL['hongo'][2], 0.45)

aplica_vineta(lz, PAL['vig'])
out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
