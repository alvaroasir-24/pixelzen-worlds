#!/usr/bin/env python3
"""PixelZen Worlds - Stranger Things (Monitor Principal): Grieta del Upside Down, Azotamentes, Casa Creel y Chicos en Bici."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, exporta_salida, exporta_sprites_si_aplica, fbm, mix, pinta_sprite,
    render_cielo, render_estrellas, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1983)

PALETAS = {
    'noche': dict(
        sky=['#04020a', '#0a0514', '#14081e', '#200c2a', '#2e1036', '#3e1640', '#501c48', '#66224e', '#7c2854', '#92305a'],
        rift=('#ff2848', '#ff6e84', '#ffc8d4', '#4e0a1a'),
        hill=('#141020', '#0c0914', '#06040c'),
        pine=('#0b1018', '#141c28', '#06080e'),
        house=('#262232', '#171420', '#0b0912', '#3c364c'),
        road=('#12121a', '#1d1e28', '#e2b64e', '#1a241e'),
        lamp=('#ffae48', '#fff0be'),
        shad='#07050c',
        vig=0.72,
        nube=['#36142e', '#4c1b3a', '#642444', '#7e2e4c', '#983a54', '#281024'],
    ),
    'dorado': dict(
        sky=['#14081e', '#240c2c', '#3c123c', '#5a1a46', '#7c2448', '#a03246', '#c44644', '#e06646', '#f48c54', '#ffc076'],
        rift=('#ff2e4e', '#ff788e', '#ffd4de', '#5e0e20'),
        hill=('#261624', '#180e18', '#0e070e'),
        pine=('#16141e', '#221e2e', '#0c0a10'),
        house=('#3e2c3a', '#281c28', '#140d14', '#5c4454'),
        road=('#1a1620', '#282230', '#ecc058', '#262820'),
        lamp=('#ffb64c', '#fff2c4'),
        shad='#0b0610',
        vig=0.80,
        nube=['#662442', '#86304e', '#a83e56', '#ca545a', '#e8745e', '#4c1c36'],
    ),
    'dia': dict(
        sky=['#1e3a6e', '#2c4e86', '#3c649e', '#527cb4', '#6c96c8', '#88b0da', '#a6c8e8', '#c4dcef', '#dce8ee', '#eef0e6'],
        hill=('#364458', '#263040', '#18202c'),
        rift=('#ff3252', '#ff7c92', '#ffdce4', '#6e1628'),
        pine=('#1b2e26', '#284436', '#101c16'),
        house=('#4e5266', '#343848', '#1e202c', '#727890'),
        road=('#262834', '#343844', '#e6be58', '#2a3c28'),
        lamp=('#ffb44c', '#fff2c4'),
        shad='#0c0e18',
        vig=0.88,
        nube=['#dde4f0', '#eef2f8', '#cbd6ea', '#f6f8fc', '#dfe8f4', '#b8c8de'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#ff3458', '#6844c8'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 36, halo='#ff98b4', base='#fff2f4', sombra='#d8bec6', crater='#b69aa4', crater_hi='#ccb2bc'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe09c', centro='#fffdf0', borde='#ffb85c', rayo='#ffdc98'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffd4dc', '#c8e0ff', '#a896d8'])

MX, MY, MR = 420, 74, 34
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#ff98b4', base='#fff2f4', sombra='#d8bec6', crater='#b69aa4', crater_hi='#ccb2bc')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 408, 178, 22, halo='#ff9668', centro='#ffece0', borde='#ff5844', rayo='#ff8058')
    else:
        dibuja_sol_estandar(lz, 398, 84, 22, halo='#ffe09c', centro='#fffdf0', borde='#ffb85c', rayo='#ffdc98')

# Grieta Dimensional Escarlata del Mundo del Reves rasgando el cielo izquierdo (x=66..244, y=28..148)
R0, R1, R2, R3 = PAL['rift']
rift_pts = [(74, 134), (104, 118), (128, 122), (160, 92), (186, 98), (218, 62), (242, 46)]
for seg_i, ((ax, ay), (bx, by)) in enumerate(zip(rift_pts, rift_pts[1:])):
    steps = max(abs(bx - ax), abs(by - ay))
    for i in range(steps + 1):
        u_seg = i / float(max(1, steps))
        gx = int(ax + (bx - ax) * u_seg)
        gy = int(ay + (by - ay) * u_seg + 2 * math.sin(i * 0.35 + seg_i))
        u_all = (seg_i + u_seg) / float(len(rift_pts) - 1)
        w_rift = max(1, int(5.5 * math.sin(u_all * math.pi) + 1.2))
        for dy in range(-w_rift, w_rift + 1):
            for dx in range(-w_rift, w_rift + 1):
                d = math.hypot(dx, dy)
                if d <= w_rift:
                    c = R2 if d < w_rift * 0.28 else (R1 if d < w_rift * 0.56 else (R0 if d < w_rift * 0.82 else R3))
                    put(gx + dx, gy + dy, c)
    # Ramas secundarias de la grieta
    if seg_i in (1, 3):
        for k in range(18):
            bx_r = bx + (-k if seg_i == 1 else k)
            by_r = by + k + int(2 * math.sin(k * 0.6))
            put(bx_r, by_r, R0 if k < 10 else R3)
    if ANIM:
        RUNAS.append([bx, by])
    else:
        glow(bx, by, 12, R0, 0.45)

# Relampagos rojos ramificados descendiendo irregularmente desde la grieta
rng_l = random.Random(1984)
for rx_b, ry_b, len_b in ((118, 122, 66), (176, 96, 78), (218, 68, 72)):
    cx_b = rx_b
    for k in range(len_b):
        if k % 5 == 0:
            cx_b += rng_l.choice((-2, -1, 0, 1, 2))
        cy_b = ry_b + k
        put(cx_b, cy_b, R2 if k % 7 == 0 else R0)
        if k == len_b // 2:
            for b_k in range(16):
                put(cx_b + b_k, cy_b + b_k, R0 if b_k < 9 else R3)

NUBES_DEF = [
    (96, 44, 155, PAL['nube'][0], 2),
    (254, 48, 165, PAL['nube'][1], 3),
    (412, 54, 130, PAL['nube'][2], 2),
    (168, 136, 175, PAL['nube'][3], 3),
    (360, 128, 135, PAL['nube'][4], 2),
    (526, 224, 110, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 1. EL AZOTAMENTES (Mind Flayer Titan) alzandose en el cielo tormentoso sobre la colina izquierda (cx=168, base=282)
SH = PAL['shad']
# Cuerpo central y cabeza alargada entre y=132..214
for dy in range(72):
    yy = 132 + dy
    hw_mf = 7 if dy < 16 else (12 if dy < 32 else max(3, 10 - (dy - 32) // 4))
    for dx in range(-hw_mf, hw_mf + 1):
        put(168 + dx, yy, SH)
# 6 gigantescas patas aracnidas curvadas ancladas detras de la linea de arboles (y=282)
for side in (-1, 1):
    for knee_dx, knee_dy, foot_dx in ((34, -28, 56), (48, 4, 84), (28, 34, 62)):
        pts = [(168 + side * 6, 178), (168 + side * knee_dx, 178 + knee_dy), (168 + side * foot_dx, 282)]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            steps = max(1, max(abs(bx - ax), abs(by - ay)))
            for i in range(steps + 1):
                px_l = int(ax + (bx - ax) * i / steps)
                py_l = int(ay + (by - ay) * i / steps)
                r_l = 3 if i < steps // 2 else 2
                disc(px_l, py_l, r_l, SH)
                put(px_l - side, py_l - 1, R0 if dith(px_l, py_l, 0.35) else SH)

# 2. Colinas arboladas de Hawkins ancladas hasta HOR=290 (bajando suavemente en x>430 para HUD)
rh = Ruido(1984)
H0, H1, H2 = PAL['hill']
for x in range(W):
    ramp = max(0.0, min(1.0, (x - 420) / 80.0))
    dip_r = int(28 * (0.5 - 0.5 * math.cos(math.pi * ramp)))
    ridge = int(238 + 22 * fbm(rh, x * 0.014) + dip_r)
    for y in range(ridge, HOR + 18):
        put(x, y, mix(H0, H2, min(1.0, (y - ridge) / max(1, HOR + 18 - ridge))))

P0, P1, P2 = PAL['pine']


def pino(px, by, h):
    for i in range(h):
        y = by - h + i
        hw = max(0, int(i * 0.27) - (2 if i % 5 == 4 else 0))
        for dx in range(-hw, hw + 1):
            put(px + dx, y, P1 if dx < 0 else (P0 if dx < hw // 2 else P2))


for px_p, py_p, ph_p in ((18, 298, 62), (46, 296, 54), (78, 298, 48), (248, 294, 48), (274, 296, 56), (446, 296, 54), (484, 298, 46), (528, 298, 52), (576, 298, 56), (612, 298, 64)):
    pino(px_p, py_p, ph_p)

# 3. CASA CREEL anclada firmemente en la colina central-derecha (x=312..422, base y=296)
HS0, HS1, HS2, HS_HI = PAL['house']
for x in range(324, 412):
    for y in range(236, 298):
        put(x, y, HS_HI if x < 344 else (HS0 if x < 394 else HS1))
# Tejado victoriano a dos aguas + buhardilla central
for dy in range(30):
    y = 206 + dy
    hw = 8 + int(dy * 1.45)
    for dx in range(-hw, hw + 1):
        put(368 + dx, y, HS2 if dx > 0 else HS1)
# Torre/aguja lateral izquierda de Casa Creel
for dy in range(44):
    y = 192 + dy
    hw_t = max(1, int(dy * 0.65)) if dy < 17 else 11
    for dx in range(-hw_t, hw_t + 1):
        put(334 + dx, y, HS2 if dx > 0 else HS_HI)
# Porche frontal cubierto sostenido por columnas hasta suelo y=298
for y in range(266, 298):
    for px_c in (328, 348, 388, 408):
        put(px_c, y, HS_HI)
        put(px_c + 1, y, HS2)
for dx in range(-44, 45):
    put(368 + dx, 266, HS2)
    put(368 + dx, 267, HS_HI)
# Ventanas rojas tenebrosas de Casa Creel (incluyendo roseton del atico)
for wx, wy in ((342, 246), (368, 224), (390, 246), (356, 276), (380, 276)):
    for dy in range(8):
        for dx in range(-2, 3):
            put(wx + dx, wy + dy, R0 if FASE != 'dia' else '#5e6a88')
    if ANIM:
        VENTANAS.append([wx, wy + 2])

# 4. Carretera asfaltada de Hawkins con hierba y enredaderas del Upside Down (y = 294..400)
RD0, RD1, RD_Y, GR_BG = PAL['road']
rx_n, ry_n = Ruido(1985), Ruido(1986)
for y in range(294, H):
    road_top = 316
    road_bot = 382
    for x in range(W):
        n2 = 0.5 * fbm(rx_n, x * 0.04) + 0.5 * fbm(ry_n, y * 0.05 + 11.0)
        if road_top <= y <= road_bot:
            h_asph = ((x * 374761393 + y * 668265263) ^ (x * y)) & 255
            c = RD1 if h_asph < 16 else RD0
            # Linea central discontinua amarilla
            if 348 <= y <= 349 and (x % 34) < 18:
                c = RD_Y
        else:
            c = GR_BG if n2 > 0.45 else mix(GR_BG, H2, 0.5)
            # Zarcillos oscuros del Upside Down en los bordes inferiores
            if y > 384 and n2 > 0.66 and (y > 391 or x % 7 < 3):
                c = R3 if n2 < 0.72 else R0
        put(x, y, c)

# Postes electricos y farolas ambar a lo largo de la carretera (x=76, 264, 514, ancladas en y=318)
for lx_p in (76, 264, 514):
    for y in range(258, 320):
        put(lx_p, y, HS2)
        put(lx_p + 1, y, HS1)
    for dx in range(8):
        put(lx_p + dx, 258, HS2)
    put(lx_p + 7, 260, PAL['lamp'][1])
    if ANIM:
        FAROLES.append([lx_p + 7, 261, 13])
    else:
        glow(lx_p + 7, 261, 14, PAL['lamp'][0], 0.65)
# Cables tendidos entre postes
for x in range(76, 515):
    sag = int(8 * math.sin(((x - 76) % 188) / 188.0 * math.pi))
    over(x, 262 + sag, HS2, 0.7)


# 5. LOS CHICOS EN BICICLETA (4 siluetas en fila sobre el asfalto y=346..358 con faros)
def dibuja_chico_bici(cx, by, flip=False):
    # Dos ruedas apoyadas en y=by
    for wx in (cx - 6, cx + 6):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                d = dx * dx + dy * dy
                if 7 <= d <= 16:
                    put(wx + dx, by - 4 + dy, '#1e202c')
    # Cuadro de la bici + silueta del chico con gorra/mochila
    for dx in range(-6, 7):
        put(cx + dx, by - 6, '#141620')
    for y in range(by - 18, by - 5):
        for dx in range(-2, 3):
            if y < by - 14 and abs(dx) <= 2:
                put(cx + dx, y, SH)
            elif by - 14 <= y < by - 8:
                put(cx + dx, y, SH)
    # Haz de luz del faro delantero hacia la derecha
    for i in range(1, 22):
        rad_beam = max(1, i // 5)
        for dy in range(-rad_beam + 1, rad_beam):
            over(cx + 7 + i, by - 9 + dy, '#fff0b8', max(0.05, 0.36 - i * 0.015))
    if ANIM:
        FAROLES.append([cx + 7, by - 9, 8])
    else:
        put(cx + 7, by - 9, '#fff6d0')


for bx_k, by_k in ((128, 356), (170, 350), (214, 358), (256, 352)):
    dibuja_chico_bici(bx_k, by_k)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
