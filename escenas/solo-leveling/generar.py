#!/usr/bin/env python3
"""PixelZen Worlds - Solo Leveling (Monitor Principal): Castillo del Monarca de las Sombras, Igris y Ejercito Sombra."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, en_zona, exporta_salida, exporta_sprites_si_aplica, fbm, mix, pinta_sprite,
    render_cielo, render_estrellas, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(701)

PALETAS = {
    'noche': dict(
        sky=['#04020c', '#090518', '#110a28', '#1b103a', '#26174e', '#341f64', '#44287c', '#563292', '#683ea4', '#7a4cb6'],
        cliff=('#1c152c', '#120e1e', '#090612'),
        castle_hi='#362b4d',
        castle_mid='#221a34',
        castle_dk='#120d1e',
        castle_rim='#5a467e',
        floor_a='#110c1e',
        floor_b='#19132b',
        floor_line='#080510',
        floor_hi='#2b2044',
        step_top='#30244a',
        step_rise='#100b1b',
        carpet=('#481020', '#781832', '#b08232'),
        throne=('#2d2244', '#181228', '#090610', '#8c1c38'),
        aura=('#6f2cff', '#a864ff', '#54e4ff'),
        plume=('#781028', '#c01c42', '#ff3d68'),
        shad_core='#07050e',
        shad_mid='#160f2b',
        shad_rim='#6438bc',
        vig=0.72,
        nube=['#281844', '#38225a', '#4a2e72', '#5c3c8a', '#6e4ca0', '#201438'],
    ),
    'dorado': dict(
        sky=['#160824', '#260e38', '#3c144a', '#5a1c56', '#7e265a', '#a43456', '#c6484e', '#e2684c', '#f49058', '#ffc078'],
        cliff=('#2e1830', '#1e1022', '#100814'),
        castle_hi='#563652',
        castle_mid='#3a223b',
        castle_dk='#1d1022',
        castle_rim='#8e5874',
        floor_a='#1a1020',
        floor_b='#26172d',
        floor_line='#0d0712',
        floor_hi='#42284a',
        step_top='#4c2e50',
        step_rise='#180e20',
        carpet=('#5c1222', '#941e36', '#d69c38'),
        throne=('#402746', '#25152c', '#100816', '#ac2442'),
        aura=('#8c3eff', '#c478ff', '#6cf0ff'),
        plume=('#8e142c', '#d02046', '#ff4872'),
        shad_core='#0a0612',
        shad_mid='#1d1330',
        shad_rim='#7b44cc',
        vig=0.80,
        nube=['#582852', '#783462', '#9a4468', '#be5c68', '#de7c6a', '#462044'],
    ),
    'dia': dict(
        sky=['#1a2d5a', '#263e70', '#365288', '#4868a0', '#5e80b6', '#7898c8', '#94b2d8', '#b0cae4', '#cadce9', '#e2ebf0'],
        cliff=('#383e54', '#262b3c', '#161926'),
        castle_hi='#60647e',
        castle_mid='#42465e',
        castle_dk='#242738',
        castle_rim='#8e92ae',
        floor_a='#242638',
        floor_b='#2f3248',
        floor_line='#141522',
        floor_hi='#4a4e6c',
        step_top='#545878',
        step_rise='#202234',
        carpet=('#5a1828', '#86223a', '#cc9e42'),
        throne=('#444864', '#282b40', '#131522', '#98243e'),
        aura=('#7a3eff', '#ad72ff', '#58e4ff'),
        plume=('#8a1834', '#c2244a', '#f2446c'),
        shad_core='#090814',
        shad_mid='#1b1734',
        shad_rim='#6f4ac2',
        vig=0.88,
        nube=['#cad6ea', '#dce4f2', '#eef2fa', '#c2cee4', '#e4eaf6', '#b0bed8'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

# 1. Cielo tormentoso del Monarca + aurora violeta/cian nocturna
render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#8a42ff', '#54d8ff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 44, halo='#a888ff', base='#eef2ff', sombra='#bec6e8', crater='#9aa2cc', crater_hi='#b2bae0'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#c8b8ff', centro='#f8f6ff', borde='#a898f8', rayo='#cbb8ff'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#d8c8ff', '#a8e8ff', '#9c88e0'])

MX, MY, MR = 294, 78, 42
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#a888ff', base='#eef2ff', sombra='#bec6e8', crater='#9aa2cc', crater_hi='#b2bae0')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 236, 174, 22, halo='#ff9678', centro='#ffece0', borde='#f45e58', rayo='#ff8268')
    else:
        dibuja_sol_estandar(lz, 246, 86, 22, halo='#d8d8ff', centro='#fafaff', borde='#b8c4f8', rayo='#cfd8ff')

# 2. Nubes de tormenta sombria
NUBES_DEF = [
    (95, 42, 165, PAL['nube'][0], 3),
    (270, 52, 150, PAL['nube'][1], 2),
    (430, 88, 130, PAL['nube'][2], 2),
    (160, 136, 185, PAL['nube'][3], 3),
    (360, 152, 145, PAL['nube'][4], 2),
    (525, 228, 110, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 3. Riscos basalticos de fondo anclados al horizonte (bajando hacia la derecha para liberar zona HUD)
rc = Ruido(719)
cl_hi, cl_mid, cl_dk = PAL['cliff']
for x in range(W):
    hud_dip = 30 if x > 460 else 0
    ridge = int(218 + 26 * fbm(rc, x * 0.015) + hud_dip + (14 if 215 < x < 375 else 0))
    ridge = min(HOR + 4, ridge)
    for y in range(ridge, HOR + 24):
        t = (y - ridge) / max(1, (HOR + 24 - ridge))
        col = mix(cl_hi, cl_mid, min(1.0, t * 1.1))
        if dith(x, y, t * 0.45):
            col = cl_dk
        put(x, y, col)

# 4. Ciudadela Gotica del Cambio de Clase (sin fragmentos flotantes: arcos continuos unidos a los pilares)
C_HI, C_MID, C_DK, C_RIM = PAL['castle_hi'], PAL['castle_mid'], PAL['castle_dk'], PAL['castle_rim']


def dibuja_torre_gotica(cx, half_w, top_y, base_y, spire_h=46, con_ventana=True):
    for dy in range(spire_h):
        yy = top_y - spire_h + dy
        hw = max(0, int((half_w * 0.72) * (dy / max(1, spire_h))))
        for dx in range(-hw, hw + 1):
            col = C_RIM if dx == -hw else (C_HI if dx < 0 else (C_DK if dx > hw // 2 else C_MID))
            put(cx + dx, yy, col)
    for bx in range(cx - half_w - 2, cx + half_w + 3, 6):
        for dy in range(-5, 0):
            for dx in range(4):
                put(bx + dx, top_y + dy, C_HI if dx == 0 else C_DK)
    for yy in range(top_y, base_y + 1):
        flare = int(4 * ((yy - top_y) / max(1, base_y - top_y)) ** 2)
        hw = half_w + flare
        row_b = yy // 7
        for dx in range(-hw, hw + 1):
            if dx <= -hw + 1:
                c = C_RIM
            elif dx > hw - 3:
                c = C_DK
            elif yy % 7 == 0 or (dx + (row_b % 2) * 5) % 10 == 0:
                c = C_DK
            elif dx < -2 and ((dx // 5 + row_b) % 3 == 0):
                c = C_HI
            else:
                c = C_MID
            put(cx + dx, yy, c)
    if con_ventana and half_w >= 10:
        for vy in (top_y + 22, top_y + 56):
            if vy + 18 < base_y - 12:
                for dy in range(16):
                    vw = 2 if dy < 4 else 3
                    for dx in range(-vw, vw + 1):
                        put(cx + dx, vy + dy, '#070410')
                if ANIM:
                    VENTANAS.append([cx - 1, vy + 5])
                else:
                    for dy in range(4, 13):
                        for dx in range(-1, 2):
                            over(cx + dx, vy + dy, PAL['aura'][1], 0.75)


def dibuja_muro_almenado(x0, x1, top_y, base_y, slit_xs=()):
    for x in range(x0, x1 + 1):
        merlon = ((x - x0) % 14) < 8
        y_ini = top_y - 6 if merlon else top_y
        for y in range(y_ini, base_y + 1):
            row_b = y // 7
            if y == y_ini:
                c = C_RIM
            elif y > base_y - 8 or y % 7 == 0 or (x + (row_b % 2) * 6) % 12 == 0:
                c = C_DK
            elif ((x // 12 + row_b) % 4 == 0):
                c = C_HI
            else:
                c = C_MID
            put(x, y, c)
    for sx in slit_xs:
        for dy in range(12):
            put(sx, top_y + 14 + dy, '#070410')
            if not ANIM and dy % 2 == 0:
                over(sx, top_y + 14 + dy, PAL['aura'][0], 0.7)
        if ANIM:
            VENTANAS.append([sx, top_y + 18])


dibuja_torre_gotica(46, 22, 146, 316, spire_h=52, con_ventana=True)
dibuja_muro_almenado(0, 128, 250, 316, slit_xs=(18, 92, 114))
dibuja_torre_gotica(146, 16, 184, 314, spire_h=38, con_ventana=True)
dibuja_muro_almenado(162, 224, 258, 314, slit_xs=(182, 204))

# Dos grandes Pilares Goticos con capiteles con pinaculos coronados y arcos rotos soldados directamente a la columna
for side in (-1, 1):
    px_c = 294 + side * 70
    # Aguja/capitel gotico sobre cada pilar (continuo, nada flotando)
    for dy in range(28):
        yy = 136 - 28 + dy
        hw_sp = max(0, int(9 * (dy / 28.0)))
        for dx in range(-hw_sp, hw_sp + 1):
            put(px_c + dx, yy, C_RIM if dx == -hw_sp else (C_HI if dx < 0 else C_DK))
    # Cuerpo del pilar hasta el suelo y=314
    for y in range(136, 314):
        hw_col = 11 if y < 144 else 9
        for dx in range(-hw_col, hw_col + 1):
            c = C_RIM if dx == -hw_col else (C_HI if dx < -2 else (C_DK if dx > 4 or y % 8 == 0 else C_MID))
            put(px_c + dx, y, c)
    # Contrafuerte escalonado anclado al pie del pilar
    for y in range(218, 314):
        hw_b = 4 + (y - 218) // 16
        for dx in range(-hw_b, hw_b + 1):
            put(px_c + side * (9 + abs(dx)), y, C_DK if side > 0 else C_HI)

    # Arrancadero del arco ojival roto soldado sin grieta al capitel (angle 0 -> 44 deg)
    for step in range(44):
        rad = math.radians(step)
        ax = int(px_c - side * 66 * (1.0 - math.cos(rad)))
        ay = int(146 - 58 * math.sin(rad))
        r_stone = max(3, 7 - step // 9)
        for dy in range(-r_stone, r_stone + 1):
            for dx in range(-r_stone, r_stone + 1):
                if dx * dx + dy * dy <= r_stone * r_stone:
                    put(ax + dx, ay + dy, C_HI if dy < 0 else (C_DK if dy > 2 else C_MID))

dibuja_torre_gotica(424, 16, 198, 314, spire_h=34, con_ventana=True)
dibuja_muro_almenado(370, 474, 256, 314, slit_xs=(392, 448))
dibuja_muro_almenado(474, W - 1, 272, 314, slit_xs=(514, 566))

# Estandartes carmesi rasgados colgando en pilares internos
for bx in (224, 364):
    for dy in range(46):
        w_ban = 5 if dy < 34 else max(1, 5 - (dy - 34) // 2)
        sway = int(math.sin(dy * 0.14) * 1.4)
        for dx in range(-w_ban, w_ban + 1):
            col_b = PAL['carpet'][2] if abs(dx) == w_ban else (PAL['carpet'][1] if dx < 0 else PAL['carpet'][0])
            put(bx + dx + sway, 174 + dy, col_b)

# 5. Patio de losas de obsidiana en perspectiva (y = 308..400)
FA, FB, FL, FHI = PAL['floor_a'], PAL['floor_b'], PAL['floor_line'], PAL['floor_hi']
for y in range(308, H):
    ty = (y - 308) / float(H - 308)
    tile_y = int((y - 308) / (3.2 + 5.5 * ty))
    for x in range(W):
        persp_x = (x - 294) / (0.35 + 0.95 * ty)
        tile_x = int(math.floor(persp_x / 24.0))
        is_joint = (abs(persp_x - tile_x * 24.0) < 1.2) or ((y - 308) % max(4, int(5 + 9 * ty)) == 0)
        if is_joint:
            c = FL
        else:
            c = FA if (tile_x + tile_y) % 2 == 0 else FB
            if (x * 13 + y * 7) % 29 == 0:
                c = mix(c, FHI, 0.35)
        dist_th = abs(x - 294)
        if dist_th < 140 and y < 378 and dith(x, y, 0.28 * (1 - dist_th / 140)):
            c = mix(c, PAL['aura'][0], 0.18)
        put(x, y, c)

# 6. Gran Estrado Escalonado (4 peldanos solidos de y=294 a y=344) y Trono Gotico del Monarca (cx=294)
ST_TOP, ST_RISE = PAL['step_top'], PAL['step_rise']
CR0, CR1, CR_G = PAL['carpet']
tiers = [
    (294, 306, 48),
    (306, 318, 60),
    (318, 331, 74),
    (331, 344, 88),
]
for y0, y1, hw in tiers:
    for y in range(y0, y1):
        es_borde = (y - y0) <= 2
        for x in range(294 - hw, 294 + hw + 1):
            if abs(x - 294) <= 18:
                c = CR_G if abs(x - 294) >= 16 else (CR1 if es_borde else CR0)
            else:
                c = ST_TOP if es_borde else (C_MID if y - y0 < 5 else ST_RISE)
                if abs(x - 294) == hw:
                    c = FL
            put(x, y, c)
    for x in range(294 - hw - 3, 294 + hw + 4):
        over(x, y1, '#04020a', 0.55)

# Trono Gotico de Obsidiana y Carmesi sentado sobre el estrado en y=296 (cx=294)
TH_HI, TH_MID, TH_DK, TH_RED = PAL['throne']
for y in range(218, 296):
    t = (y - 218) / 78.0
    hw_t = 6 if y < 234 else int(15 + 6 * math.sin(t * 2.2))
    if y < 232:
        for px_s in (294, 294 - 12, 294 + 12):
            w_sp = max(0, 2 - (232 - y) // 5)
            for dx in range(-w_sp, w_sp + 1):
                put(px_s + dx, y, TH_HI if dx <= 0 else TH_DK)
    else:
        for dx in range(-hw_t, hw_t + 1):
            if abs(dx) >= hw_t - 2:
                c = TH_HI if dx < 0 else TH_DK
            elif abs(dx) <= hw_t - 5 and y > 242:
                c = TH_RED if (dx + y) % 3 else mix(TH_RED, TH_DK, 0.35)
            else:
                c = TH_MID
            put(294 + dx, y, c)
for y in range(274, 298):
    for side in (-1, 1):
        for dx in range(-4, 5):
            put(294 + side * 20 + dx, y, TH_HI if dx < 0 else TH_DK)
for y in range(284, 298):
    for dx in range(-19, 20):
        put(294 + dx, y, TH_MID if y < 290 else TH_DK)

# 7. Cuatro pilares con braseros de fuego sombra anclados al suelo
for bx, by_floor, col_h in ((132, 342, 68), (194, 336, 62), (394, 336, 62), (466, 344, 66)):
    for y in range(by_floor - col_h, by_floor + 1):
        hw_p = 5 if y < by_floor - 6 else 7
        for dx in range(-hw_p, hw_p + 1):
            c = C_RIM if dx == -hw_p else (C_HI if dx < 0 else C_DK)
            if y % 9 == 0:
                c = C_DK
            put(bx + dx, y, c)
    for dx in range(-8, 9):
        put(bx + dx, by_floor - col_h - 1, TH_HI if abs(dx) < 5 else TH_DK)
        put(bx + dx, by_floor - col_h - 2, TH_DK)
    if ANIM:
        FAROLES.append([bx, by_floor - col_h - 5, 11])
    else:
        for fy in range(-8, 0):
            fw = max(1, 5 - (-fy) // 2)
            for dx in range(-fw, fw + 1):
                put(bx + dx, by_floor - col_h - 2 + fy, PAL['aura'][2] if abs(dx) <= 1 else PAL['aura'][1])
        glow(bx, by_floor - col_h - 5, 16, PAL['aura'][0], 0.55)


# 8. SUNG JIN-WOO (Monarca de las Sombras, cx=294, by=323 - presencia imponente, abrigo largo y aura sombra)
def dibuja_jin_woo(cx, by):
    spr = [
        '............KKKKKK.............',
        '...........KKKKKKKK............',
        '..........KKKKKKKKKK...........',
        '..........KCKKKKKCKK...........',
        '...........KKKKKKKK............',
        '............KKKKKK.............',
        '........KKKKKKKKKKKKKK.........',
        '.......KKKKKKKKKKKKKKKK........',
        '......KKKKKKKKKKKKKKKKKK.......',
        '.....KKK.KKKKKKKKKKKK.KKK......',
        '....KKK..KKKKKKKKKKKK..KKK.....',
        '...KKK...KKKKKKKKKKKK...KKR....',
        '..KKK....KKKKKKKKKKKK....RKR...',
        '..KK.....KKKKKKKKKKKK.....R....',
        '.KK......KKKKKKKKKKKK..........',
        '.K.......KKKKKKKKKKKK..........',
        '........KKKKKKKKKKKKKK.........',
        '.......KKKKKKKKKKKKKKKK........',
        '.......KKKKKKKKKKKKKKKK........',
        '......KKKKKKKKKKKKKKKKKK.......',
        '......KKKKKKKKKKKKKKKKKK.......',
        '.....KKKKKKKKKKKKKKKKKKKK......',
        '.....KKKKKKKKKKKKKKKKKKKK......',
        '....KKKKKKKKKKKKKKKKKKKKKK.....',
        '....KKKKKKK.KKKKKK.KKKKKKK.....',
        '...KKKKKKK..KKKKKK..KKKKKKK....',
        '...KKKKKK...KKKKKK...KKKKKK....',
        '..KKKKKK....KKKKKK....KKKKKK...',
        '..KKKKK.....KKK.KK.....KKKKK...',
        '..KKKK......KKK.KKK.....KKKK...',
        '..KKK.......KKK.KKK......KKK...',
        '............KKK.KKK............',
        '............KKK.KKK............',
        '............KKK.KKK............',
        '............KKK.KKK............',
        '...........KKKK.KKKK...........',
    ]
    SH_C, SH_M, SH_R = PAL['shad_core'], PAL['shad_mid'], PAL['shad_rim']
    A0, A1, A2 = PAL['aura']
    cmap = {'K': SH_C, 'C': A2, 'R': A1}

    # Charco de invocacion sombra bajo Jin-Woo
    for dx in range(-26, 27):
        for dy in range(-2, 4):
            if (dx / 26.0) ** 2 + (dy / 3.8) ** 2 <= 1.0:
                over(cx + dx, by + dy, A0 if abs(dx) > 16 else SH_C, 0.78)

    # Flujo continuo de aura sombra alzandose detras del abrigo de Jin-Woo
    rng_a = random.Random(901)
    for _ in range(120):
        ax = cx + rng_a.randint(-21, 21)
        ay = by - rng_a.randint(4, 48)
        if abs(ax - cx) > 6 or ay < by - 32:
            over(ax, ay, A1 if rng_a.random() < 0.45 else A0, 0.45)

    pinta_sprite(lz, cx, by, spr, cmap)
    x0 = cx - len(spr[0]) // 2
    y0 = by - len(spr) + 1
    for ry, row in enumerate(spr):
        for rx, ch in enumerate(row):
            if ch == 'K' and (rx == 0 or row[rx - 1] == '.'):
                put(x0 + rx, y0 + ry, SH_R)
            elif ch == 'K' and (rx == len(row) - 1 or row[rx + 1] == '.'):
                put(x0 + rx, y0 + ry, SH_M)

    # Daga sombria en mano izquierda
    for i in range(13):
        put(cx - 13 - i // 3, by - 19 + i, A2 if i > 8 else SH_R)

    if ANIM:
        RUNAS.append([cx - 3, by - 32])
        RUNAS.append([cx + 2, by - 32])
        RUNAS.append([cx + 14, by - 24])
        FAROLES.append([cx + 14, by - 27, 10])
    else:
        glow(cx + 14, by - 27, 11, A1, 0.75)
        glow(cx, by - 32, 7, A2, 0.48)


dibuja_jin_woo(294, 323)


# 9. IGRIS EL ROJO CARMESI EN FORMA DE SOMBRA (cx=366, by=347, mas grande y nitido junto al estrado)
def dibuja_igris(cx, by):
    spr = [
        '.............KKK.............',
        '............KKKKK............',
        '...........KKKKKKK...........',
        '...........KKVVKKK...........',
        '............KKKKK............',
        '.........KKKKKKKKKK..........',
        '.......KKKKKKKKKKKKKK........',
        '......KKKKKKKKKKKKKKKK.......',
        '.....KKKKKKKKKKKKKKKKKK......',
        '....KKKKK.KKKKKKKK.KKKKK.....',
        '...KKKKK..KKKKKKKK..KKKKK....',
        '..KKKK....KKKKKKKK....KKKK...',
        '..KKK.....KKKKKKKK.....KKK...',
        '..........KKKKKKKK...........',
        '.........KKKKKKKKKK..........',
        '........KKKKKKKKKKKK.........',
        '.......KKKKKKKKKKKKKK........',
        '......KKKKKKKKKKKKKKKK.......',
        '......KKKKKK.KKKK.KKKKKK.....',
        '.....KKKKKK..KKKK..KKKKKK....',
        '.....KKKKK...KKKK...KKKKK....',
        '....KKKKK....KKKK....KKKKK...',
        '....KKKK.....KKKK.....KKKK...',
        '............KKKKKK...........',
        '...........KKK..KKK..........',
        '...........KKK..KKK..........',
        '...........KKK..KKK..........',
        '...........KKK..KKK..........',
        '..........KKKK..KKKK.........',
        '..........KKKK..KKKK.........',
        '.........KKKK....KKKK........',
    ]
    SH_C, SH_R = PAL['shad_core'], PAL['shad_rim']
    P0, P1, P2 = PAL['plume']
    A0, A1 = PAL['aura'][0], PAL['aura'][1]

    for dx in range(-22, 23):
        for dy in range(-2, 3):
            if (dx / 22.0) ** 2 + (dy / 3.0) ** 2 <= 1.0:
                over(cx + dx, by + dy, A0 if abs(dx) > 14 else SH_C, 0.78)

    # Penacho carmesi largo y majestuoso ondeando tras el yelmo de Igris
    for t_p in range(32):
        px_p = cx + 2 + t_p
        py_p = by - 33 + int(t_p * 0.42 + 2.8 * math.sin(t_p * 0.24))
        r_p = 3 if t_p < 10 else (2 if t_p < 22 else 1)
        for dy in range(-r_p, r_p + 1):
            c = P2 if dy < 0 else (P1 if dy == 0 else P0)
            put(px_p, py_p + dy, c)

    # Mandoble largo de Igris clavado verticalmente hasta y=by
    sx_sw = cx - 11
    for y in range(by - 44, by + 1):
        hw_s = 1 if y < by - 33 or y > by - 5 else (5 if y == by - 30 else 1)
        for dx in range(-hw_s, hw_s + 1):
            c = '#dce0f8' if dx == 0 else (A1 if y > by - 29 and abs(dx) == 1 else SH_R)
            put(sx_sw + dx, y, c)

    pinta_sprite(lz, cx, by, spr, {'K': SH_C, 'V': P2})
    # Cuernos altos del yelmo + hombreras
    for k in range(7):
        put(cx - 4 - k // 2, by - 31 - k, SH_R)
        put(cx + 3 + k // 2, by - 31 - k, SH_R)
    for dx in (-7, -6, 6, 7):
        put(cx + dx, by - 22, SH_R)

    if ANIM:
        RUNAS.append([cx - 1, by - 27])
        RUNAS.append([cx + 14, by - 25])
    else:
        glow(cx - 1, by - 27, 6, P2, 0.55)
        glow(cx + 14, by - 25, 6, P1, 0.45)


dibuja_igris(366, 347)


# 10. EJERCITO DE SOLDADOS DE SOMBRA (figuras claramente legibles de 22-26px en formacion a ambos lados)
def dibuja_soldado_sombra(cx, by, tipo='lanza', flip=False, escala=1):
    SH_C, SH_R = PAL['shad_core'], PAL['shad_rim']
    A0, A1, A2 = PAL['aura']
    eye_col = A2 if tipo != 'mago' else A1

    for dx in range(-14, 15):
        for dy in range(-2, 3):
            if (dx / 14.0) ** 2 + (dy / 2.6) ** 2 <= 1.0:
                over(cx + dx, by + dy, A0 if abs(dx) > 8 else SH_C, 0.78)

    if tipo == 'mago':
        spr = [
            '.....KKKKK.....',
            '....KKKKKKK....',
            '....KKVKVKK....',
            '.....KKKKK.....',
            '..KKKKKKKKKKK..',
            '.KKKKKKKKKKKKK.',
            '.KKKKKKKKKKKKK.',
            '.KKKKKKKKKKKKK.',
            '..KKKKKKKKKKK..',
            '..KKKKKKKKKKK..',
            '.KKKKKKKKKKKKK.',
            '.KKKKKKKKKKKKK.',
            '.KKKKKKKKKKKKK.',
            '.KKKKKKKKKKKKK.',
            '.KKKKKKKKKKKKK.',
            '..KKKKK.KKKKK..',
            '..KKKK...KKKK..',
            '..KKKK...KKKK..',
        ]
        st_x = cx + (-8 if flip else 8)
        for y in range(by - 28, by + 1):
            put(st_x, y, SH_C)
        put(st_x, by - 29, A1)
        put(st_x + 1, by - 29, A1)
        if ANIM:
            RUNAS.append([st_x, by - 29])
        else:
            glow(st_x, by - 29, 5, A1, 0.5)
    else:
        spr = [
            '.....KKKKK.....',
            '....KKKKKKK....',
            '....KKVKVKK....',
            '.....KKKKK.....',
            '..KKKKKKKKKKK..',
            '.KKKKKKKKKKKKK.',
            '.KKK.KKKKK.KKK.',
            '.KK..KKKKK..KK.',
            '.....KKKKK.....',
            '....KKKKKKK....',
            '....KKKKKKK....',
            '...KKKKKKKKK...',
            '...KKKK.KKKK...',
            '...KKK...KKK...',
            '...KKK...KKK...',
            '...KKK...KKK...',
            '..KKKK...KKKK..',
        ]
        wp_x = cx + (-9 if flip else 9)
        for y in range(by - 32, by + 1):
            put(wp_x, y, SH_R if y < by - 24 else SH_C)
        if tipo == 'escudo':
            sh_x = cx + (8 if flip else -8)
            for sy in range(by - 15, by - 2):
                for sdx in range(-3, 4):
                    put(sh_x + sdx, sy, SH_R if abs(sdx) == 0 else SH_C)

    pinta_sprite(lz, cx, by, spr, {'K': SH_C, 'V': eye_col})
    x0 = cx - len(spr[0]) // 2
    y0 = by - len(spr) + 1
    for ry, row in enumerate(spr):
        for rx, ch in enumerate(row):
            if ch == 'K' and ry < 9 and (rx == 0 or row[rx - 1] == '.'):
                put(x0 + rx, y0 + ry, SH_R)
    for k in range(4):
        put(cx + (-1 if flip else 1), by - len(spr) - k, SH_R)
    if ANIM:
        RUNAS.append([cx, by - 14])
    else:
        glow(cx, by - 14, 4, eye_col, 0.45)


soldados = [
    (46, 384, 'escudo', False),
    (92, 366, 'lanza', False),
    (138, 388, 'mago', False),
    (178, 356, 'escudo', False),
    (218, 372, 'lanza', False),
    (412, 372, 'lanza', True),
    (456, 358, 'escudo', True),
    (502, 386, 'mago', True),
    (548, 366, 'lanza', True),
    (594, 384, 'escudo', True),
]
for sx, sy, st, fl in soldados:
    dibuja_soldado_sombra(sx, sy, st, fl)

# 11. Escombros de piedra en esquinas inferiores
for cx_r, hw_r, h_r in ((14, 18, 12), (622, 20, 14)):
    for dy in range(-h_r, 1):
        w_cur = int(hw_r * (1 - (-dy) / (h_r + 2)))
        for dx in range(-w_cur, w_cur + 1):
            put(cx_r + dx, H + dy - 1, C_HI if dx < 0 else C_DK)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
