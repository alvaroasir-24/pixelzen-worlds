#!/usr/bin/env python3
"""PixelZen Worlds - Demon Slayer (Monitor 2): Aldea de los Herreros, Tokito vs Gyokko."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, exporta_salida, exporta_sprites_si_aplica, fbm, mix, pinta_sprite,
    render_cielo, render_estrellas, render_lago, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1109)

PALETAS = {
    'noche': dict(
        sky=['#040b18', '#081528', '#0e223c', '#163050', '#204064', '#2c5278', '#3a668a', '#4c7c9c', '#6092ac', '#76a8b8'],
        mont=('#1a2c38', '#12202a', '#0a141c'),
        pine=('#0b1a1c', '#142a2a', '#061012'),
        wall=('#484644', '#302e2c'),
        roof=('#1a2232', '#263248', '#101420'),
        wood=('#38261e', '#221610', '#4e362a'),
        rock=('#242c36', '#161c24', '#0c1016', '#384452'),
        agua='#091826',
        ola=('#78e4d8', '#327888', '#16384a'),
        mist=('#74f0dc', '#d8fff8'),
        vase=('#222844', '#3c4c78', '#d4a64a'),
        gyokko=('#201c2c', '#ff4878', '#54e4d4'),
        shad_core='#070810',
        shad_rim='#48d8c4',
        vig=0.74,
        nube=['#1e3652', '#2a4868', '#385c7e', '#487092', '#5c84a6', '#182c44'],
    ),
    'dorado': dict(
        sky=['#161430', '#262044', '#3c2c58', '#5c3c64', '#824e66', '#a86462', '#cc7c58', '#e89a56', '#f8bc64', '#ffdc86'],
        mont=('#3a2a3e', '#281c2c', '#18101c'),
        pine=('#162020', '#24342e', '#0c1412'),
        wall=('#76685e', '#524640'),
        roof=('#24283c', '#363c56', '#161826'),
        wood=('#4c3024', '#301c14', '#684434'),
        rock=('#3a323e', '#26202a', '#141016', '#564a5c'),
        agua='#1a2038',
        ola=('#ffd094', '#746c92', '#2e2a4a'),
        mist=('#88f4e0', '#e4fff8'),
        vase=('#2e3456', '#4e6094', '#e8ba58'),
        gyokko=('#2c2036', '#ff5484', '#68ecd8'),
        shad_core='#090812',
        shad_rim='#5ce4d0',
        vig=0.82,
        nube=['#583856', '#784862', '#9e5c68', '#c47868', '#e4986a', '#442a44'],
    ),
    'dia': dict(
        sky=['#22589c', '#326cb0', '#4682c4', '#5e9ad6', '#7ab2e4', '#98c8ee', '#b6dcf4', '#d0eaf8', '#e4f2f8', '#f2f6ee'],
        mont=('#48687e', '#365268', '#263c4e'),
        pine=('#1c4232', '#2a5e46', '#10281e'),
        wall=('#bab0a4', '#8e847a'),
        roof=('#2e3c52', '#425674', '#1e2838'),
        wood=('#684634', '#462e22', '#865c44'),
        rock=('#4e5864', '#363e48', '#20262c', '#6e7a88'),
        agua='#1d4868',
        ola=('#c2f0ec', '#5ea0b4', '#2c5c78'),
        mist=('#68ecd8', '#e8fffc'),
        vase=('#344268', '#566ca2', '#e8be5c'),
        gyokko=('#2c283c', '#ff4878', '#54e4d4'),
        shad_core='#090a14',
        shad_rim='#48d8c4',
        vig=0.90,
        nube=['#ffffff', '#eef6fa', '#dcf0f8', '#f6fbfe', '#e4f2fa', '#c8e0f0'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#54e8cc', '#78a8ff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#9ef4e4', base='#f2fffb', sombra='#c4e0dc', crater='#9cbcb8', crater_hi='#b4d2ce'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe49c', centro='#fffef2', borde='#ffc45c', rayo='#ffe298'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#d8fff6', '#bce8ff', '#a2b8e8'])

MX, MY, MR = 384, 72, 36
CX_ASTRO = MX if FASE == 'noche' else (MX + 16 if FASE == 'dorado' else MX - 40)
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#9ef4e4', base='#f2fffb', sombra='#c4e0dc', crater='#9cbcb8', crater_hi='#b4d2ce')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, MX + 16, 178, 22, halo='#ffaa70', centro='#fff0dc', borde='#ff6c48', rayo='#ff8c60')
    else:
        dibuja_sol_estandar(lz, MX - 40, 82, 22, halo='#ffe49c', centro='#fffef2', borde='#ffc45c', rayo='#ffe298')

NUBES_DEF = [
    (74, 34, 150, PAL['nube'][0], 2),
    (254, 48, 165, PAL['nube'][1], 3),
    (430, 32, 145, PAL['nube'][2], 2),
    (166, 118, 160, PAL['nube'][3], 3),
    (360, 114, 130, PAL['nube'][4], 2),
    (526, 224, 110, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 1. Valle montanoso de cedros rodeando la aldea (bajando suavemente en x>430 para HUD)
rm = Ruido(1189)
M0, M1, M2 = PAL['mont']
for x in range(W):
    ramp = max(0.0, min(1.0, (x - 420) / 80.0))
    dip_r = int(32 * (0.5 - 0.5 * math.cos(math.pi * ramp)))
    ridge = int(198 + 34 * fbm(rm, x * 0.013 + 2.0) + dip_r)
    ridge = min(HOR, ridge)
    for y in range(ridge, HOR + 1):
        t = (y - ridge) / max(1, HOR - ridge)
        put(x, y, mix(M0, M2, t * 0.85))

P0, P1, P2 = PAL['pine']


def cedro(px, by, h):
    for i in range(h):
        y = by - h + i
        hw = max(0, int(i * 0.25) - (2 if i % 6 == 5 else 0))
        for dx in range(-hw, hw + 1):
            put(px + dx, y, P1 if dx < 0 else (P0 if dx < hw // 2 else P2))


for cx_c, cy_c, ch_c in ((18, HOR, 68), (44, HOR, 58), (196, HOR, 54), (222, HOR, 46), (484, HOR, 44), (528, HOR, 52), (574, HOR, 58), (612, HOR, 62)):
    cedro(cx_c, cy_c, ch_c)

# 2. Estanque brumoso del valle reflejando cielo y luna
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

# 3. Terraplen izquierdo con Talleres Tradicionales de los Herreros (x=0..230, anclado hasta y=400)
RK0, RK1, RK2, RK_HI = PAL['rock']
WD0, WD1, WD_HI = PAL['wood']
rx_k = Ruido(1231)
ry_k = Ruido(1249)
for y in range(256, H):
    edge_l = int(218 - 44 * ((y - 256) / float(H - 256)) ** 0.75 + 6 * math.sin(y * 0.09))
    for x in range(0, min(W, edge_l)):
        n_rk = 0.5 * fbm(rx_k, x * 0.05) + 0.5 * fbm(ry_k, y * 0.09)
        if edge_l - x < 9:
            c = RK2 if n_rk < 0.55 else RK1
        elif y < 263:
            c = P1 if n_rk > 0.44 else RK_HI
        else:
            c = RK_HI if n_rk > 0.62 else (RK0 if n_rk > 0.36 else RK2)
        put(x, y, c)

# Casa principal del taller de herreria anclada firme en la terraza izquierda (x=34..156, base y=294)
RF0, RF1, RF2 = PAL['roof']
WL0, WL1 = PAL['wall']
for x in range(44, 148):
    for y in range(248, 296):
        c = WL0 if (x % 16 != 0) else WD1
        if 262 <= y <= 280 and ((x - 54) % 28) in range(4, 14):
            c = '#ffb84d'
            if ANIM and (x - 54) % 28 == 8 and y == 270:
                VENTANAS.append([x, y])
        put(x, y, c)
# Tejado japones curvo irimoya sobre el taller
for dy in range(26):
    y = 222 + dy
    hw = 28 + int(dy * 1.45)
    for dx in range(-hw, hw + 1):
        put(96 + dx, y, RF1 if dy < 10 else (RF0 if dx % 4 else RF2))
# Chimenea de forja humeante
for y in range(214, 232):
    for dx in range(-3, 4):
        put(124 + dx, y, RK0 if dx < 0 else RK2)
CHIMENEA = [124, 213]

# Puente/muelle de madera saliendo firme desde la terraza hasta x=316 donde lucha Tokito
for x in range(178, 326):
    for y in range(338, 348):
        put(x, y, WD_HI if y < 341 else (WD0 if y < 345 else WD1))
for px_p in (192, 232, 272, 312):
    for y in range(344, 384):
        for dx in (-2, -1, 0, 1):
            put(px_p + dx, y, WD0 if dx < 0 else WD1)
    # Farol calido en el primer poste
    if px_p == 192:
        for y in range(326, 340):
            put(px_p, y, WD1)
        if ANIM:
            FAROLES.append([px_p, 325, 10])
        else:
            put(px_p, 325, '#fff0b8')
            glow(px_p, 325, 8, '#ff9840', 0.6)

# 4. Promontorio rocoso en el estanque para Gyokko y su Jarron (cx=452, base y=346..400, anclado en el agua)
for y in range(342, H):
    t_r = (y - 342) / float(H - 342)
    hw_r = int(48 + 44 * t_r + 6 * math.sin(y * 0.14))
    for dx in range(-hw_r, hw_r + 1):
        c = RK_HI if (y < 347 or dx < -hw_r // 2) else (RK0 if dx < hw_r // 3 else RK2)
        put(452 + dx, y, c)

# Niebla mística sobre la superficie del estanque (Respiracion de la Niebla)
for mx_m, my_m, mw_m in ((265, 354, 110), (370, 362, 130), (520, 348, 110)):
    for dy in range(-5, 6):
        hw_m = int(mw_m * 0.5 * (1 - abs(dy) / 6.5))
        for dx in range(-hw_m, hw_m + 1):
            if dith(mx_m + dx, my_m + dy, 0.42 * (1 - abs(dx) / (hw_m + 1))):
                over(mx_m + dx, my_m + dy, PAL['mist'][0], 0.35)


# 5. MUICHIRO TOKITO (Pilar de la Niebla, cx=288, by=340 - apoyado en el muelle)
def dibuja_tokito(cx, by):
    SH_C, SH_R = PAL['shad_core'], PAL['shad_rim']
    M0, M1 = PAL['mist']

    # Melena larga oscura con puntas menta/turquesa ondeando atras
    for t_h in range(18):
        hx = cx - 4 - t_h
        hy = by - 25 + int(t_h * 0.55 + math.sin(t_h * 0.3) * 1.4)
        for dy in range(3):
            c_h = SH_R if t_h > 10 else SH_C
            put(hx, hy + dy, c_h)

    spr = [
        '.....KKKKK.....',
        '....KKKKKKK....',
        '....KKCKCKK....',
        '.....KKKKK.....',
        '..KKKKKKKKKKK..',
        '.KKKKKKKKKKKKK.',
        '.KK.KKKKKKK.KK.',
        '....KKKKKKK....',
        '...KKKKKKKKK...',
        '..KKKKKKKKKKK..',
        '..KKKKKKKKKKK..',
        '.KKKKKKKKKKKKK.',
        '.KKKKKK.KKKKKK.',
        '..KKKK...KKKK..',
        '..KKK.....KKK..',
    ]
    pinta_sprite(lz, cx, by, spr, {'K': SH_C, 'C': M1})

    # Estela amplia de la Respiracion de la Niebla (cintas turquesa/blancas desde la espada hacia Gyokko)
    for k in range(36):
        u = k / 35.0
        sx = cx + 8 + int(u * 48)
        sy = by - 14 + int(math.sin(u * 4.5) * 9 - u * 4)
        r_m = 2 if 0.15 < u < 0.85 else 1
        for dy in range(-r_m, r_m + 1):
            for dx in range(-r_m, r_m + 1):
                if dx * dx + dy * dy <= r_m * r_m:
                    put(sx + dx, sy + dy, M1 if abs(dx) + abs(dy) <= 1 else M0)
        if k % 7 == 0:
            if ANIM:
                RUNAS.append([sx, sy])
            else:
                glow(sx, sy, 6, M0, 0.5)


dibuja_tokito(288, 340)


# 6. GYOKKO Y SU JARRÓN DEMONÍACO (cx=452, by=344 - apoyado firme en la roca)
def dibuja_gyokko(cx, by):
    V0, V1, VG = PAL['vase']
    G_C, G_E, G_W = PAL['gyokko']
    SH_C = PAL['shad_core']

    # Jarron grande de porcelana apoyado sobre la roca en y=344
    for dy in range(-22, 1):
        u = (dy + 22) / 22.0
        hw_v = int(6 + 9 * math.sin(u * math.pi * 0.85))
        if dy < -18:
            hw_v = 8  # boca acampanada
        for dx in range(-hw_v, hw_v + 1):
            if dy in (-19, -11, -3):
                c = VG
            elif dx < -hw_v // 3:
                c = V1
            else:
                c = V0
            put(cx + dx, by + dy, c)

    # Tentaculos acuaticos demoniacos alrededor del jarron
    for side in (-1, 1):
        for t in range(28):
            u = t / 27.0
            tx = int(cx + side * (12 + t * 0.9))
            ty = int(by - 12 - math.sin(u * 3.8) * 14 - u * 8)
            r_t = 2 if u < 0.6 else 1
            for dy in range(-r_t, r_t + 1):
                for dx in range(-r_t, r_t + 1):
                    if dx * dx + dy * dy <= r_t * r_t:
                        put(tx + dx, ty + dy, G_W if (dx + dy) == 0 else SH_C)
        if ANIM:
            RUNAS.append([cx + side * 26, by - 22])

    # Torso sombreado y cabeza de Gyokko emergiendo del jarron (con ojos verticales brillantes)
    spr_g = [
        '....KKKKKK....',
        '...KKKKKKKK...',
        '...KKKEKKKK...',  # Ojo en frente
        '...KKKKKKKK...',
        '...KKKKEKKK...',  # Ojo/boca vertical caracteristico
        '....KKKKKK....',
        '..KKKKKKKKKK..',
        '.KK.KKKKKK.KK.',
        'KK..KKKKKK..KK',
        '....KKKKKK....',
        '....KKKKKK....',
        '.....KKKK.....',
    ]
    pinta_sprite(lz, cx, by - 22, spr_g, {'K': SH_C, 'E': G_E})
    if ANIM:
        RUNAS.append([cx, by - 30])
        FAROLES.append([cx, by - 28, 11])
    else:
        glow(cx, by - 30, 7, G_E, 0.55)


dibuja_gyokko(452, 344)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
