#!/usr/bin/env python3
"""PixelZen Mushoku - Tema 2 (Rediseñado): Continente Demoníaco · Ciudadela de Rikarisu."""
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
random.seed(29)

PALETAS = {
    'noche': dict(
        sky=['#060310', '#0d061d', '#16092b', '#220d39', '#311246', '#431750', '#581d58', '#6f255e', '#883062', '#a23f64', '#bc5268', '#d46b70', '#e68b7c'],
        mont=['#3c1f48', '#2f173c', '#22102f', '#170a23', '#0e0518'],
        mist=['#8a4c78', '#703b66', '#562b52', '#3c1e3e', '#26122b'],
        cristal=('#ff78aa', '#982c64'), filo='#f4aac6',
        espina1='#120618', espina2='#1d0b24', espinarim='#522450',
        cliff=('#160a1e', '#24122e', '#3a1e46', '#542c5c'),
        basalt=('#1c1126', '#2a1b38', '#3e2952'),
        adobe=('#321c34', '#462848', '#5e385c'),
        dome=('#3a1428', '#5c2038', '#84304c'),
        bruma='#784870', agua='#0b0416',
        ola=('#e06ea0', '#7e3672', '#3c1848'),
        suelo=('#0c0514', '#22102c', '#100718', '#30183a'),
        vig=0.72,
        nube=['#4e285c', '#6c386e', '#8c4476', '#b85676', '#cf6e78', '#442454'],
        mana=('#ff5e9c', '#a82262'),
        hongo=('#5ef2e4', '#b4fff6', '#228c88', '#14444a'),
        shroom_stem=('#241832', '#3c284e'),
    ),
    'dorado': dict(
        sky=['#1b082c', '#2b0e3e', '#41154e', '#5e1c58', '#80235a', '#a42c54', '#c63b4c', '#e25244', '#f47044', '#fc904c', '#ffb25c', '#ffd076', '#ffe69e'],
        mont=['#6d2c4f', '#562141', '#401733', '#2c0f24', '#1b0817'],
        mist=['#e87868', '#c85862', '#a0425c', '#763052', '#4c2042'],
        cristal=('#ffa478', '#b84058'), filo='#ffc496',
        espina1='#1c0a16', espina2='#2c1220', espinarim='#6e2e3e',
        cliff=('#24101e', '#381a2c', '#54283e', '#743a50'),
        basalt=('#321b2c', '#482840', '#683c58'),
        adobe=('#6e4048', '#8c545a', '#ae6e6e'),
        dome=('#621a28', '#8c2834', '#b83c44'),
        bruma='#d47c78', agua='#28102c',
        ola=('#f49e84', '#a44c6c', '#542048'),
        suelo=('#180a14', '#3c1c28', '#1e0e18', '#4c2432'),
        vig=0.80,
        nube=['#8c426a', '#ba586e', '#e07268', '#f6986a', '#ffb878', '#74385c'],
        mana=('#ff78ac', '#c0306c'),
        hongo=('#78f8e6', '#d8fff8', '#2ea89c', '#185458'),
        shroom_stem=('#382238', '#563652'),
    ),
    'dia': dict(
        sky=['#382854', '#4b3668', '#62467a', '#7c568a', '#966894', '#af7c9a', '#c6929c', '#daa89c', '#eabc9c', '#f2cba0', '#f6d8ac', '#fae4bc', '#fcedcc'],
        mont=['#7e587c', '#68466a', '#523556', '#3e2644', '#2a1832'],
        mist=['#dbb2a8', '#c49698', '#a8788c', '#885c7c', '#684268'],
        cristal=('#f4a4c4', '#a45484'), filo='#ffe4d4',
        espina1='#221224', espina2='#321b34', espinarim='#6a3c5e',
        cliff=('#2e1a30', '#442846', '#603a60', '#7e4e7a'),
        basalt=('#48344c', '#604664', '#826284'),
        adobe=('#a87e78', '#c89e92', '#e2bcb0'),
        dome=('#7a2c3c', '#a23c4a', '#c8565e'),
        bruma='#d4a6a8', agua='#3e204c',
        ola=('#ecc0c6', '#a4688c', '#5e3264'),
        suelo=('#201020', '#48283e', '#261426', '#5a344e'),
        vig=0.90,
        nube=['#f6dcd8', '#f0c8ca', '#fae4dc', '#ffe8d4', '#f8d8d6', '#e0b8c4'],
        mana=('#ff6aa4', '#b82868'),
        hongo=('#78f4e8', '#d4fffc', '#34a8a2', '#1e5860'),
        shroom_stem=('#46324a', '#684c6c'),
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

# 1. Cielo demoníaco + sprites de luna carmesí y sol ámbar
render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#e060a8', '#5cd8c8'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 46, halo='#e878a8', base='#fde4ea', sombra='#d89eb4', crater='#b67490', crater_hi='#cca0b4'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 24, halo='#ff9860', centro='#fff4d6', borde='#ff7840', rayo='#ffb870'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffd6e8', '#d6b8ff', '#a890d8'])

MX, MY, MR = 368, 84, 46
CX_ASTRO = MX if FASE == 'noche' else (MX + 70 if FASE == 'dorado' else MX - 55)
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#e878a8', base='#fde4ea', sombra='#d89eb4', crater='#b67490', crater_hi='#cca0b4')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, MX + 70, 208, 24, halo='#ff9860', centro='#fff4d6', borde='#ff7840', rayo='#ffb870')
    else:
        dibuja_sol_estandar(lz, MX - 55, 96, 24, halo='#ff9860', centro='#fff4d6', borde='#ff7840', rayo='#ffb870')

# 2. Nubes
NUBES_DEF = [
    (160, 62, 185, PAL['nube'][0], 3),
    (380, 106, 150, PAL['nube'][1], 3),
    (105, 168, 200, PAL['nube'][2], 3),
    (285, 208, 160, PAL['nube'][3], 3),
    (550, 248, 125, PAL['nube'][4], 2),
    (430, 52, 95, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 3. Cordilleras volcánicas afiladas + cristales gigantes de maná
def rampa(x):
    return 1.0 if x < 430 else max(0.32, 1.0 - (x - 430) / 85 * 0.68)

def cristal_gigante(cx, by, h, w, incl, c_hi, c_lo):
    c_mid = mix(c_hi, c_lo, 0.45)
    c_tip = mix(c_hi, '#ffffff', 0.45)
    for i in range(h):
        t = i / max(1, h - 1)
        if t < 0.72:
            hw = max(2, int(w * (0.95 - t * 0.15)))
        else:
            hw = max(1, int(w * 0.84 * (1.0 - (t - 0.72) / 0.28)))
        ox = int(i * incl)
        yy = by - i
        if yy > HOR:
            continue
        for dx in range(-hw, hw + 1):
            if dx < -hw // 3:
                col = c_tip if t > 0.68 else c_hi
            elif dx < hw // 3:
                col = c_mid if t < 0.78 else c_hi
            else:
                col = c_lo
            if abs(dx) == hw:
                col = mix(col, '#100418', 0.45)
            put(cx + ox + dx, yy, col)


def cristal_racimo(cx, by, h, w, incl, c_hi, c_lo):
    """Dibuja un cristal prismático ancho con brotes menores anclados en su base."""
    cristal_gigante(cx, by, h, w, incl, c_hi, c_lo)
    cristal_gigante(cx - w - 2, by + 4, int(h * 0.56), max(3, int(w * 0.58)), incl - 0.22, c_hi, c_lo)
    cristal_gigante(cx + w + 2, by + 5, int(h * 0.48), max(3, int(w * 0.52)), incl + 0.24, c_hi, c_lo)
    if not ANIM:
        glow(cx + int(h * incl), by - h + 2, 6, c_hi, 0.45)

CAPAS = [
    (234, 118, 11, 0.015, PAL['mont'][0], PAL['mist'][0]),
    (248, 96, 17, 0.020, PAL['mont'][1], PAL['mist'][1]),
    (260, 78, 23, 0.027, PAL['mont'][2], PAL['mist'][2]),
    (272, 54, 31, 0.036, PAL['mont'][3], PAL['mist'][3]),
]
crestas = []
for idx_capa, (base, amp, seed, fr, col, mist) in enumerate(CAPAS):
    r, ra = Ruido(seed * 19), Ruido(seed * 47 + 3)
    c = []
    for x in range(W):
        n = fbm(r, x * fr * 1.6 + seed)
        agudo = (1 - abs(2 * n - 1)) ** 1.4
        am = 0.35 + 1.0 * ra(x * 0.013 + seed) ** 1.2
        c.append(base - amp * rampa(x) * am * (0.76 * agudo + 0.24 * n))
    crestas.append(c)
    for x in range(W):
        top = int(c[x])
        pend = c[min(W - 1, x + 2)] - c[max(0, x - 2)]
        for y in range(top, HOR + 1):
            d = y - top
            cc = mix(col, mist, 0.24 * (d / max(1, HOR - top)) ** 2.0)
            if d < 2:
                cc = mix(cc, PAL['filo'], 0.32 if pend < 0 else 0.08)
            put(x, y, cc)
        for k in range(1, 20):
            if dith(x, top + k, (1 - k / 20) * 0.42):
                over(x, top + k, mist, 0.55)
    if idx_capa == 0:
        cristal_racimo(332, HOR, int(HOR - c[332]) + 28, 11, 0.14, PAL['cristal'][0], PAL['cristal'][1])
        cristal_racimo(356, HOR, int(HOR - c[356]) + 20, 7, -0.13, PAL['cristal'][0], PAL['cristal'][1])
    elif idx_capa == 1:
        cristal_racimo(422, HOR, int(HOR - c[422]) + 18, 8, -0.12, PAL['cristal'][0], PAL['cristal'][1])

# Árboles espinosos petrificados en las lomas lejanas
def espino(x, by, h, col, rim):
    for i in range(h):
        y = by - h + i
        put(x, y, col)
        if i % 3 == 1 and i > 2:
            span = max(1, (h - i) // 3)
            for dx in range(1, span + 1):
                put(x - dx, y - dx // 2, col)
                put(x + dx, y - dx // 2, rim if dx == span else col)

r5 = random.Random(91)
for x in range(260, W, 7):
    if r5.random() < 0.7:
        espino(x + r5.randint(-1, 1), int(crestas[3][x]) + 4, r5.randint(8, 16), PAL['espina1'], PAL['espinarim'])

# 4. Meseta de basalto escalonada a la izquierda (x: 0..278) con la Ciudadela Demoníaca de Rikarisu
# Acantilado continuo desde el borde izquierdo hasta x=275 (no es una isla flotante)
WARM = '#ff8c4a'
MANA_HI, MANA_LO = PAL['mana']
CL0, CL1, CL2, CL3 = PAL['cliff']
BS0, BS1, BS2 = PAL['basalt']
AD0, AD1, AD2 = PAL['adobe']
DM0, DM1, DM2 = PAL['dome']

r_cliff = Ruido(73)
for x in range(0, 282):
    # Terraza continua a HOR-24 bajo toda la ciudadela y torre (0..234), bajando hacia el muelle/portal (234..282)
    if x < 234:
        top_c = HOR - 24
    elif x < 268:
        top_c = HOR - 14
    else:
        top_c = HOR - 14 + int((x - 268) * 0.9)
    for y in range(min(HOR, top_c), HOR + 1):
        d_c = y - top_c
        estrato = int(r_cliff(x * 0.14 + d_c * 0.22) * 3)
        if d_c == 0:
            c = CL3
        elif d_c == 1:
            c = CL2
        elif (x * 7 + y * 3) % 29 == 0 or d_c > 16:
            c = CL0
        elif estrato == 2 and (y % 5 < 2):
            c = CL2
        else:
            c = CL1 if (x + y // 3) % 7 != 0 else CL0
        put(x, y, c)
    # Grietas sutiles de maná volcánico en la pared de basalto
    if 18 <= x <= 230 and (x % 47) < 6 and top_c + 6 < HOR - 3:
        vy_f = top_c + 7 + (x % 6)
        put(x, vy_f, MANA_LO if FASE == 'dia' else MANA_HI)

# Muralla almenada en la terraza continua
for x in range(60, 236):
    y_m = HOR - 23
    for yy in range(y_m - 8, y_m):
        put(x, yy, BS1 if (x // 4 + yy // 2) % 2 else BS0)
    if x % 7 < 4:
        put(x, y_m - 9, BS2)
        put(x, y_m - 10, BS2)

def zigurat_demoniaco(x0, y_base, w, h, pisos=2):
    """Edificio escalonado estilo Rikarisu con cúpula o cuernos de obsidiana."""
    for p in range(pisos):
        pw = int(w * (1 - p * 0.26))
        ph = h // pisos
        px0 = x0 + (w - pw) // 2
        py0 = y_base - (p + 1) * ph
        for yy in range(py0, py0 + ph):
            for x in range(px0, px0 + pw):
                c = AD2 if x < px0 + pw // 3 else (AD1 if x < px0 + 2 * pw // 3 else AD0)
                if yy == py0 or yy == py0 + ph - 1:
                    c = BS0
                put(x, yy, c)
        # Ventanas estrechas estilo ciudadela demoníaca
        wy = py0 + ph // 3
        for vx in range(px0 + 6, px0 + pw - 6, 9):
            if ANIM:
                VENTANAS.append([vx, wy])
            else:
                for dy in range(4):
                    put(vx, wy + dy, WARM)
                    put(vx + 1, wy + dy, WARM)
                glow(vx, wy + 2, 4, WARM, 0.35)
    # Cúpula bulbosa carmesí arriba
    top_w = int(w * (1 - (pisos - 1) * 0.26))
    cx = x0 + w // 2
    cy_base = y_base - pisos * (h // pisos)
    dome_h = max(12, top_w // 2)
    for i in range(dome_h):
        t = i / max(1, dome_h - 1)
        hw = max(1, int((top_w * 0.45) * math.cos(t * 1.45)))
        yy = cy_base - i
        for x in range(cx - hw, cx + hw + 1):
            c = DM2 if x < cx - hw // 3 else (DM1 if x < cx + hw // 3 else DM0)
            put(x, yy, c)
    # Espiga / cuernos sobre la cúpula
    for yy in range(cy_base - dome_h - 7, cy_base - dome_h + 1):
        put(cx, yy, BS2)
    for side in (-1, 1):
        for k in range(5):
            put(cx + side * (top_w // 2 + k), cy_base - k, BS2)

# Tres estructuras demoníacas escalonadas formando la ciudadela de Rikarisu (ancladas en HOR-23)
zigurat_demoniaco(72, HOR - 26, 54, 42, pisos=2)   # Bastión occidental
zigurat_demoniaco(124, HOR - 26, 62, 54, pisos=3)  # Ciudadela central de Rikarisu (con chimenea humeante)
CHIMENEA = [132, HOR - 88]
for yy in range(HOR - 86, HOR - 62):
    for x in range(130, 135):
        put(x, yy, BS0 if x > 132 else BS1)

# Torre aguja de obsidiana (x ~ 196..220) bien asentada en la terraza HOR-23
for yy in range(HOR - 78, HOR - 21):
    t = (yy - (HOR - 78)) / 57.0
    hw = int(6 + 7 * t)
    for dx in range(-hw, hw + 1):
        put(208 + dx, yy, BS2 if dx < -hw // 3 else (BS1 if dx < hw // 3 else BS0))
for wy in (HOR - 66, HOR - 50, HOR - 34):
    if ANIM:
        VENTANAS.append([207, wy])
    else:
        for dy in range(4):
            put(207, wy + dy, WARM)
            put(208, wy + dy, WARM)
        glow(207, wy + 2, 4, WARM, 0.4)
# Baliza de cristal flotante en la aguja
if ANIM:
    for dy in range(-2, 3):
        for dx in range(-1, 2):
            if abs(dx) + abs(dy) <= 2:
                RUNAS.append([208 + dx, HOR - 85 + dy])
else:
    disc(208, HOR - 85, 2, MANA_HI)
    glow(208, HOR - 85, 9, MANA_HI, 0.65)

# Viaducto / muelle de piedra sólido desde la terraza (x ~ 234..322) con tajamares en el agua
for yy in range(HOR - 12, HOR + 2):
    for xx in range(288, 322):
        put(xx, yy, CL1 if (xx + yy) % 4 else CL0)
for ax in (254, 276, 298):
    for yy in range(HOR - 12, HOR + 3):
        hw_p = 3 if yy > HOR - 4 else 2
        for dx in range(-hw_p, hw_p + 1):
            put(ax + dx, yy, BS0 if dx > 0 else BS1)
for x in range(234, 320):
    put(x, HOR - 13, BS2)
    put(x, HOR - 12, BS1)

# Ruina del Portal de Teletransporte fracturado en la terraza derecha (x = 302)
ax_p, ay_p = 302, HOR - 13
for side in (-1, 1):
    for yy in range(ay_p - 26, ay_p):
        for dx in (-2, -1, 0, 1):
            put(ax_p + side * 12 + dx, yy, BS2 if dx < 0 else BS0)
for k in range(-12, 13):
    if abs(k) < 2:
        continue  # grieta fracturada en la clave del arco
    dy = int(math.sqrt(max(0, 144 - k * k)) * 0.7)
    for t in range(4):
        put(ax_p + k, ay_p - 25 - dy + t, BS1 if t < 2 else BS0)
if ANIM:
    for dx, dy in ((0, -16), (-12, -14), (12, -14), (-8, -28), (8, -28)):
        RUNAS.append([ax_p + dx, ay_p + dy])
else:
    disc(ax_p, ay_p - 16, 2, MANA_HI)
    glow(ax_p, ay_p - 16, 8, MANA_HI, 0.65)

# Braseros en la muralla
for bx_f, by_f in ((88, HOR - 30), (170, HOR - 30), (242, HOR - 21), (312, HOR - 13)):
    for yy in range(8):
        put(bx_f, by_f - yy, BS0)
    if ANIM:
        FAROLES.append([bx_f, by_f - 9, 7])
    else:
        put(bx_f, by_f - 9, '#ffd6e8')
        glow(bx_f, by_f - 9, 7, '#e84878', 0.65)

# 5. Río de obsidiana y reflejo
render_lago(lz, PAL['agua'], PAL['ola'], DESTELLOS, ANIM, mx=CX_ASTRO)

# 6. HONGOS BIOLUMINISCENTES GIGANTES sustituyendo por completo la rama de árbol (esquina sup. izq.) y abajo
# Dos árboles-hongo gigantes del Continente Demoníaco colgando desde un peñasco izquierdo (x: 0..145)
sh0, sh1 = PAL['shroom_stem']
hg_hi, hg_core, hg_mid, hg_lo = PAL['hongo']

# Peñasco volcánico superior izquierdo con bordes escarpados
for x in range(0, 62):
    h_r = int(76 * (1 - x / 62.0) ** 0.72 + 4 * math.sin(x * 0.35))
    for y in range(0, h_r):
        c = CL2 if y > h_r - 3 else (CL1 if (x * 3 + y * 5) % 11 > 4 else CL0)
        put(x, y, c)
    # Grietas sutiles de maná volcánico en la pared de basalto
    if 18 <= x <= 230 and (x % 47) < 6 and top_c + 6 < HOR - 3:
        vy_f = top_c + 7 + (x % 6)
        put(x, vy_f, MANA_LO if FASE == 'dia' else MANA_HI)

def seta_gigante(bx, by, tx, ty, rx, ry):
    """Dibuja un hongo bioluminiscente orgánico con sombrero acampanado, láminas y esporas."""
    steps = max(20, int(math.hypot(tx - bx, ty - by)))
    for i in range(steps + 1):
        t = i / steps
        cx = int(bx + (tx - bx) * t + 7 * math.sin(t * 3.14))
        cy = int(by + (ty - by) * t)
        r = max(1, int(4.2 - t * 2.0))
        for dx in range(-r, r + 1):
            put(cx + dx, cy, sh1 if dx <= 0 else sh0)
    # Sombrero bioluminiscente abombado con lunares brillantes
    for dy in range(-ry, 4):
        for dx in range(-rx, rx + 1):
            if dy <= 0:
                d = (dx / rx) ** 2 + (dy / ry) ** 2
                in_cap = d <= 1.0
            else:
                # Borde inferior acampanado suave
                hw_b = rx * (1.0 - dy * 0.08)
                in_cap = abs(dx) <= hw_b and dy <= 2
                d = (dx / rx) ** 2
            if not in_cap:
                continue
            if dy >= 1:
                c = hg_core if (dx % 3 == 0) else hg_hi
            else:
                norm_y = -dy / max(1, ry)
                c = hg_mid if norm_y < 0.45 else (hg_hi if norm_y < 0.75 else hg_lo)
                if dx < -rx // 3 and norm_y > 0.25:
                    c = hg_hi
                if (dx * 5 + dy * 7) % 17 == 0 and d < 0.65:
                    c = hg_core
            put(tx + dx, ty + dy, c)
    # Esporas descendentes suaves bajo el sombrero
    if not ANIM and rx >= 16:
        for sx_e, sy_e in ((-rx // 2, 5), (0, 8), (rx // 2, 6), (-rx // 4, 12)):
            put(tx + sx_e, ty + sy_e, hg_core)
    if ANIM:
        RUNAS.append([tx, ty + 1])
    else:
        glow(tx, ty, rx // 2, hg_hi, 0.42)

seta_gigante(16, 48, 80, 32, 30, 16)
seta_gigante(12, 60, 140, 60, 24, 13)
seta_gigante(10, 70, 44, 114, 20, 11)

# Orillas rocosas inferiores + cristales y hongos pequeños en primer plano
for cx_s in range(0, 82):
    h_s = int(26 * math.cos(cx_s / 82 * 1.57))
    for yy in range(H - h_s, H):
        put(cx_s, yy, PAL['suelo'][0] if (cx_s + yy) % 3 else PAL['suelo'][1])
for cx_s in range(W - 76, W):
    h_s = int(22 * math.cos((W - 1 - cx_s) / 76 * 1.57))
    for yy in range(H - h_s, H):
        put(cx_s, yy, PAL['suelo'][2] if (cx_s + yy) % 3 else PAL['suelo'][3])

cristal_gigante(64, H - 4, 24, 5, 0.22, PAL['cristal'][0], PAL['cristal'][1])
cristal_gigante(W - 58, H - 3, 22, 4, -0.20, PAL['cristal'][0], PAL['cristal'][1])
seta_gigante(26, H - 12, 26, H - 34, 12, 5)
seta_gigante(W - 26, H - 10, W - 26, H - 28, 10, 4)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
             chimenea=CHIMENEA, destellos=DESTELLOS, barca=[208, HOR - 20], luna=[MX, MY, MR])
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
