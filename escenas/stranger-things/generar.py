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
        sky=['#120308', '#1d050c', '#2c0813', '#3e0c1a', '#521121', '#691729', '#821e31', '#9c2839', '#b63544', '#cf4650'],
        rift=('#ff2848', '#ff6e84', '#ffc8d4', '#4e0a1a'),
        hill=('#180d18', '#0f0710', '#070309'),
        pine=('#0e0d15', '#191420', '#07050b'),
        house=('#2c1d28', '#1c121b', '#0f0810', '#482e3d'),
        road=('#121018', '#1d1924', '#e2b64e', '#1e1c1a'),
        lamp=('#ffae48', '#fff0be'),
        shad='#07030a',
        vig=0.72,
        nube=['#441220', '#5e1a2b', '#782235', '#922c3f', '#ad3848', '#300b17'],
    ),
    'dorado': dict(
        sky=['#1c050a', '#2e0810', '#460d18', '#621322', '#821b2a', '#a22730', '#c23836', '#dd523d', '#ef744b', '#fca062'],
        rift=('#ff2e4e', '#ff788e', '#ffd4de', '#5e0e20'),
        hill=('#2a121c', '#1a0b12', '#10050a'),
        pine=('#1a1018', '#281822', '#0e070c'),
        house=('#44262e', '#2c171e', '#160b10', '#663a44'),
        road=('#1c141c', '#2a1e28', '#ecc058', '#2a1e1c'),
        lamp=('#ffb64c', '#fff2c4'),
        shad='#0b040a',
        vig=0.80,
        nube=['#621828', '#802234', '#9e2e3e', '#bc4048', '#d85c54', '#48111e'],
    ),
    'dia': dict(
        sky=['#381a28', '#4a2232', '#5e2b3d', '#753749', '#8d4555', '#a55662', '#bb6b71', '#cf8383', '#e09d98', '#eeb9af'],
        hill=('#3e2834', '#2c1c26', '#1c1118'),
        rift=('#ff3252', '#ff7c92', '#ffdce4', '#6e1628'),
        pine=('#222424', '#303432', '#141516'),
        house=('#58444e', '#3c2d36', '#22181e', '#7e626f'),
        road=('#28222a', '#362e38', '#e6be58', '#302a26'),
        lamp=('#ffb44c', '#fff2c4'),
        shad='#0e060e',
        vig=0.88,
        nube=['#7a3c4a', '#964e5a', '#b0646e', '#c87e84', '#dda09e', '#622e3c'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#ff2848', '#b81c42'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 36, halo='#ff849c', base='#fff0f2', sombra='#d8b0bc', crater='#b68898', crater_hi='#cca2b0'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffb890', centro='#fff4ec', borde='#ff7a5c', rayo='#ffa880'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffd4dc', '#ffa8be', '#c88ea8'])

MX, MY, MR = 420, 64, 34
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#ff849c', base='#fff0f2', sombra='#d8b0bc', crater='#b68898', crater_hi='#cca2b0')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 408, 166, 22, halo='#ff8864', centro='#ffece0', borde='#ff4e40', rayo='#ff7054')
    else:
        dibuja_sol_estandar(lz, 398, 76, 22, halo='#ffb890', centro='#fff4ec', borde='#ff7a5c', rayo='#ffa880')

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
    (96, 36, 155, PAL['nube'][0], 2),
    (254, 40, 165, PAL['nube'][1], 3),
    (412, 46, 130, PAL['nube'][2], 2),
    (168, 126, 175, PAL['nube'][3], 3),
    (360, 118, 135, PAL['nube'][4], 2),
    (526, 212, 110, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 1. EL AZOTAMENTES (Mind Flayer Titan) alzandose entre bruma tormentosa carmesi (cx=168, base=274)
SH = PAL['shad']
if not ANIM:
    glow(168, 168, 54, R0, 0.24)
# Cuerpo central tormentoso con corona alargada e irregularidades organicas de humo (y=118..204)
for dy in range(78):
    yy = 118 + dy
    jag = int(3 * math.sin(dy * 0.42))
    hw_mf = (8 + jag // 2) if dy < 16 else ((14 + jag) if dy < 34 else max(2, 11 - (dy - 34) // 4))
    for dx in range(-hw_mf, hw_mf + 1):
        es_borde = abs(dx) >= hw_mf - 1
        put(168 + dx, yy, '#6e162e' if (es_borde and (dx + yy) % 2 == 0) else SH)
# Zarcillos laterales sombrios emanando de la cabeza/hombros del Azotamentes
for side in (-1, 1):
    for t_w in range(18):
        wx_m = 168 + side * (10 + t_w)
        wy_m = 132 + int(math.sin(t_w * 0.45) * 4 - t_w * 0.25)
        put(wx_m, wy_m, SH)
        if t_w < 12:
            put(wx_m, wy_m + 1, '#581224' if t_w % 2 == 0 else SH)
# 6 gigantescas patas aracnidas curvadas con articulaciones sinuosas ancladas tras los arboles
for side in (-1, 1):
    for knee_dx, knee_dy, foot_dx in ((34, -30, 56), (50, 2, 86), (30, 32, 62)):
        pts = [(168 + side * 7, 166), (168 + side * knee_dx, 166 + knee_dy), (168 + side * foot_dx, 274)]
        for seg_idx, ((ax, ay), (bx, by)) in enumerate(zip(pts, pts[1:])):
            steps = max(1, max(abs(bx - ax), abs(by - ay)))
            for i in range(steps + 1):
                u_s = i / float(steps)
                wave = int(2.5 * math.sin(u_s * math.pi)) * side
                px_l = int(ax + (bx - ax) * u_s) + wave
                py_l = int(ay + (by - ay) * u_s)
                r_l = 3 if (seg_idx == 0 and i < steps // 2) else (2 if i < steps * 0.7 else 1)
                disc(px_l, py_l, r_l, SH)
                put(px_l - side, py_l - 1, R0 if dith(px_l, py_l, 0.38) else SH)

# 2. Colinas arboladas de Hawkins elevadas hasta HOR=284 (bajando suavemente en x>430 para HUD)
rh = Ruido(1984)
H0, H1, H2 = PAL['hill']
for x in range(W):
    ramp = max(0.0, min(1.0, (x - 420) / 80.0))
    dip_r = int(28 * (0.5 - 0.5 * math.cos(math.pi * ramp)))
    ridge = int(226 + 22 * fbm(rh, x * 0.014) + dip_r)
    for y in range(ridge, HOR + 10):
        put(x, y, mix(H0, H2, min(1.0, (y - ridge) / max(1, HOR + 10 - ridge))))

P0, P1, P2 = PAL['pine']


def pino(px, by, h):
    for i in range(h):
        y = by - h + i
        hw = max(0, int(i * 0.27) - (2 if i % 5 == 4 else 0))
        for dx in range(-hw, hw + 1):
            put(px + dx, y, P1 if dx < 0 else (P0 if dx < hw // 2 else P2))


for px_p, py_p, ph_p in ((18, 286, 62), (46, 284, 54), (78, 286, 48), (248, 282, 48), (274, 284, 56), (446, 284, 54), (484, 286, 46), (528, 286, 52), (576, 286, 56), (612, 286, 64)):
    pino(px_p, py_p, ph_p)

# 3. CASA CREEL anclada firmemente en la colina central-derecha (x=312..422, base y=286)
HS0, HS1, HS2, HS_HI = PAL['house']
for x in range(324, 412):
    for y in range(224, 286):
        put(x, y, HS_HI if x < 344 else (HS0 if x < 394 else HS1))
# Tejado victoriano a dos aguas + buhardilla central
for dy in range(30):
    y = 194 + dy
    hw = 8 + int(dy * 1.45)
    for dx in range(-hw, hw + 1):
        put(368 + dx, y, HS2 if dx > 0 else HS1)
# Torre/aguja lateral izquierda de Casa Creel
for dy in range(44):
    y = 180 + dy
    hw_t = max(1, int(dy * 0.65)) if dy < 17 else 11
    for dx in range(-hw_t, hw_t + 1):
        put(334 + dx, y, HS2 if dx > 0 else HS_HI)
# Porche frontal cubierto sostenido por columnas hasta suelo y=286
for y in range(254, 286):
    for px_c in (328, 348, 388, 408):
        put(px_c, y, HS_HI)
        put(px_c + 1, y, HS2)
for dx in range(-44, 45):
    put(368 + dx, 254, HS2)
    put(368 + dx, 255, HS_HI)
# Ventanas rojas tenebrosas de Casa Creel (incluyendo roseton del atico)
for wx, wy in ((342, 234), (368, 212), (390, 234), (356, 264), (380, 264)):
    for dy in range(8):
        for dx in range(-2, 3):
            put(wx + dx, wy + dy, R0)
    if ANIM:
        VENTANAS.append([wx, wy + 2])

# 4. Carretera asfaltada de Hawkins elevada (y = 282..400)
RD0, RD1, RD_Y, GR_BG = PAL['road']
rx_n, ry_n = Ruido(1985), Ruido(1986)
for y in range(282, H):
    road_top = 304
    road_bot = 372
    for x in range(W):
        n2 = 0.5 * fbm(rx_n, x * 0.04) + 0.5 * fbm(ry_n, y * 0.05 + 11.0)
        if road_top <= y <= road_bot:
            h_asph = ((x * 374761393 + y * 668265263) ^ (x * y)) & 255
            c = RD1 if h_asph < 16 else RD0
            # Linea central discontinua amarilla
            if 337 <= y <= 338 and (x % 34) < 18:
                c = RD_Y
        else:
            c = GR_BG if n2 > 0.45 else mix(GR_BG, H2, 0.5)
            # Enredaderas organicas oscuras del Upside Down en la cuneta inferior
            vine_wave = 387 + int(5 * math.sin(x * 0.07) + 3 * math.cos(x * 0.17))
            if abs(y - vine_wave) <= 2 and n2 > 0.42:
                c = R3 if abs(y - vine_wave) == 0 else R0
        put(x, y, c)

# Postes electricos y farolas ambar a lo largo de la carretera (x=76, 264, 514, ancladas en y=308)
for lx_p in (76, 264, 514):
    for y in range(246, 308):
        put(lx_p, y, HS2)
        put(lx_p + 1, y, HS1)
    for dx in range(8):
        put(lx_p + dx, 246, HS2)
    put(lx_p + 7, 248, PAL['lamp'][1])
    if ANIM:
        FAROLES.append([lx_p + 7, 249, 13])
    else:
        glow(lx_p + 7, 249, 14, PAL['lamp'][0], 0.65)
# Cables tendidos entre postes
for x in range(76, 515):
    sag = int(8 * math.sin(((x - 76) % 188) / 188.0 * math.pi))
    over(x, 250 + sag, HS2, 0.7)


# 5. LOS CHICOS EN BICICLETA (en estatico aqui; en --anim se mueven en el canvas)
def dibuja_chico_bici(cx, by, coat_col='#d83848', hat_col='#2458b8'):
    skin = '#ecc2a0' if FASE != 'noche' else '#cca288'
    # Ruedas con llanta metalica
    for wx in (cx - 6, cx + 6):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                d = dx * dx + dy * dy
                if 7 <= d <= 16:
                    put(wx + dx, by - 4 + dy, '#242834')
        put(wx, by - 4, '#9ea8be')
    # Cuadro, manillar y chico con mochila y chaqueta ochentera
    for dx in range(-6, 7):
        put(cx + dx, by - 6, '#3c4254')
    put(cx + 4, by - 10, '#7c8498')
    for y in range(by - 18, by - 6):
        for dx in range(-2, 3):
            if y < by - 14 and abs(dx) <= 2:
                put(cx + dx, y, hat_col if y < by - 16 else skin)
            elif by - 14 <= y < by - 8:
                put(cx + dx, y, '#1b1d28' if dx == -2 else coat_col)
    # Haz de luz del faro delantero hacia la derecha
    for i in range(1, 22):
        rad_beam = max(1, i // 5)
        for dy in range(-rad_beam + 1, rad_beam):
            over(cx + 7 + i, by - 9 + dy, '#fff0b8', max(0.05, 0.36 - i * 0.015))
    put(cx + 7, by - 9, '#fff6d0')


if not ANIM:
    for bx_k, by_k, cc_k, hc_k in (
        (128, 344, '#2c5ca8', '#e64242'),
        (170, 338, '#d43c44', '#1b2030'),
        (214, 346, '#e28832', '#263826'),
        (256, 340, '#3e8a5c', '#543884'),
    ):
        dibuja_chico_bici(bx_k, by_k, cc_k, hc_k)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
