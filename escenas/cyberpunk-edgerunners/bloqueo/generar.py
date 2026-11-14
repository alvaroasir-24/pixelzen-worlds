#!/usr/bin/env python3
"""PixelZen Worlds - Cyberpunk Edgerunners (Bloqueo): Callejón Afterlife · Mural ER & Apogee Sandevistan."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))
from pz_lib import (  # noqa: E402
    Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, exporta_salida, exporta_sprites_si_aplica, fbm, mix,
    render_cielo, render_estrellas, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1503)

PALETAS = {
    'noche': dict(
        sky=['#050410', '#0a081d', '#120d2c', '#1c1540', '#2b1e54', '#3d286a', '#523480', '#694092', '#18424a', '#165a52'],
        wall=('#121520', '#1d2234', '#090b12', '#2d354e'),
        floor=('#070810', '#101422', '#04050a', '#1b2238'),
        emblem=('#4ade80', '#facc15', '#22c55e', '#fef08a'),
        bench=('#1e2638', '#303c58', '#0e121c'),
        implant=('#94a3b8', '#e2e8f0', '#334155', '#22d3ee', '#4ade80'),
        vig=0.72,
        nube=['#1e1938', '#2a224c', '#382c62', '#493878', '#5c468c', '#15102a'],
    ),
    'dorado': dict(
        sky=['#12081a', '#200f2a', '#34163a', '#4e204a', '#6d2e56', '#903f5c', '#b65458', '#dc7450', '#f5a050', '#fed074'],
        wall=('#181422', '#262036', '#0d0a14', '#38304e'),
        floor=('#100c18', '#1c162c', '#08060e', '#2e2444'),
        emblem=('#4ade80', '#fde047', '#22c55e', '#fef9c3'),
        bench=('#242034', '#383250', '#12101c'),
        implant=('#cbd5e1', '#f8fafc', '#475569', '#38bdf8', '#4ade80'),
        vig=0.80,
        nube=['#3e1e3e', '#58284e', '#74365a', '#944864', '#b45e68', '#2c142c'],
    ),
    'dia': dict(
        sky=['#162d5a', '#22427a', '#325a98', '#4674b6', '#6092d0', '#80b0e2', '#a4cef0', '#c8e4fc', '#e2daf0', '#f4c8dc'],
        wall=('#242a3c', '#343c54', '#141824', '#4a5678'),
        floor=('#1c2234', '#2a344e', '#101420', '#3e4c70'),
        emblem=('#22c55e', '#eab308', '#16a34a', '#fef08a'),
        bench=('#2e3852', '#445276', '#181e2c'),
        implant=('#cbd5e1', '#ffffff', '#475569', '#06b6d4', '#22c55e'),
        vig=0.88,
        nube=['#eef0fa', '#dce0f0', '#cacce4', '#f8f9fc', '#dad4ea', '#b6b4cc'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#4ade80', '#22d3ee'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#4ade80', base='#ecfdf5', sombra='#a7f3d0', crater='#6ee7b7', crater_hi='#a7f3d0'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#fde68a', centro='#fff8f0', borde='#f59e0b', rayo='#fef3c7'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS)
MX, MY, MR = 340, 56, 36
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#4ade80', base='#ecfdf5', sombra='#a7f3d0', crater='#6ee7b7', crater_hi='#a7f3d0')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 340, 108, 22, halo='#fde68a', centro='#fff8f0', borde='#f59e0b', rayo='#fef3c7')
    else:
        dibuja_sol_estandar(lz, 340, 62, 22, halo='#fde68a', centro='#ffffff', borde='#f59e0b', rayo='#fef08a')

render_nubes(lz, [(84, 38, 84, PAL['nube'][1], 2), (222, 32, 76, PAL['nube'][2], 2), (414, 44, 80, PAL['nube'][3], 2)], NUBES, ANIM)

# Siluetas de edificios laterales enmarcando el callejón (dejando x>=478, y<=220 libre para el HUD)
w_dk, w_mid, w_sh, w_rim = PAL['wall']
for y in range(74, 268):
    for x in range(0, 74):
        put(x, y, w_sh if x > 66 else (w_mid if x < 10 else w_dk))
for bx, bw, by0 in ((412, 54, 112), (470, 56, 222), (532, 108, 228)):
    for y in range(by0, 268):
        for x in range(bx, bx + bw):
            if x < W:
                put(x, y, w_sh if x < bx + 3 else w_dk)

# Muro principal de hormigón del callejón Afterlife (x=74..446, y=132..268)
r_wall = Ruido(1533)
for y in range(132, 268):
    for x in range(74, 446):
        n_w = fbm(r_wall, x * 0.05 + y * 0.12)
        col = w_sh if n_w < 0.36 else (w_dk if n_w < 0.68 else w_mid)
        if y in (132, 133, 265, 266) or x % 62 == 0:
            col = w_rim if y < 135 else '#070910'
        put(x, y, col)

# Tuberías y conductos industriales por encima del muro (x=76..444)
for py in (144, 152, 250):
    for x in range(76, 444):
        put(x, py, '#334155')
        put(x, py + 1, '#0f172a')
        if py == 144 and x % 48 in (12, 13, 14):
            put(x, py, '#22d3ee')
            put(x, py + 1, '#22d3ee')

# Cartel de neón AFTERLIFE a la izquierda del muro (x=94..166, y=166..196)
for y in range(166, 198):
    for x in range(94, 170):
        col = '#f43f5e' if (y in (166, 197) or x in (94, 169)) else '#090612'
        put(x, y, col)
# Pequeña copa/calavera Afterlife pixel art dentro del cartel
for dy in range(18):
    hw = max(1, 8 - dy // 2) if dy < 12 else (1 if dy < 16 else 5)
    for dx in range(-hw, hw + 1):
        c_af = '#4ade80' if dy < 10 else '#22d3ee'
        put(132 + dx, 172 + dy, c_af)
glow(132, 182, 22, '#f43f5e', 0.34 if FASE != 'dia' else 0.14)

# Emblema monumental Edgerunners (anillo circular + letra E/R esténcil + calavera central) en (320, 200)
em_gr, em_yl, em_gd, em_hi = PAL['emblem']
ecx, ecy = 320, 198
glow(ecx, ecy, 52, em_gr, 0.32 if FASE != 'dia' else 0.14)
# Anillo exterior verde neón y segmentos rotos tipo graffiti
for deg in range(360):
    if 65 < deg < 92 or 248 < deg < 275:
        continue
    ang = math.radians(deg)
    for rr in (34, 35, 36, 37):
        px = int(round(ecx + math.cos(ang) * rr))
        py = int(round(ecy + math.sin(ang) * rr))
        put(px, py, em_hi if rr == 35 else em_gr)
# Puntos y chorretones de spray bajo el anillo
for sx_d, sy_ln in ((296, 12), (308, 18), (332, 15), (344, 10)):
    for dy in range(sy_ln):
        put(sx_d, 232 + dy, em_gd if dy > sy_ln // 2 else em_gr)
# Monograma estilizado "ER" en amarillo ácido dentro del círculo
# Letra E izquierda (x=298..315, y=180..216)
for y in range(180, 217):
    for x in range(298, 304):
        put(x, y, em_yl)
    if y in range(180, 186) or y in range(195, 201) or y in range(211, 217):
        for x in range(304, 317):
            put(x, y, em_hi if y in (181, 196, 212) else em_yl)
# Letra R derecha (x=322..343, y=180..216)
for y in range(180, 217):
    for x in range(322, 328):
        put(x, y, em_yl)
    if y in range(180, 186) or y in range(195, 201):
        for x in range(328, 340):
            put(x, y, em_hi if y in (181, 196) else em_yl)
    if 184 <= y <= 197:
        for x in range(336, 342):
            put(x, y, em_yl)
    if y >= 200:
        lx = 328 + (y - 200)
        for dx in range(5):
            put(lx + dx, y, em_yl)


# Suelo del callejón húmedo con charcos reflejando el mural ER (y=266..400)
fl_dk, fl_mid, fl_sh, fl_rim = PAL['floor']
r_fl = Ruido(1555)
for y in range(266, H):
    for x in range(W):
        tex = fbm(r_fl, x * 0.055 + y * 0.14)
        col = fl_sh if tex < 0.38 else (fl_dk if tex < 0.65 else fl_mid)
        put(x, y, col)
        # Reflejos neón verde/amarillo/fucsia en los charcos húmedos
        if tex > 0.56 and (x + y) % 2 == 0:
            if 280 <= x <= 360 and 272 <= y <= 316:
                over(x, y, '#4ade80' if x % 3 else '#facc15', 0.34)
            elif 96 <= x <= 168 and 272 <= y <= 324:
                over(x, y, '#f43f5e', 0.30)

# Banco técnico / maletín en primer plano con el Apogee Sandevistan (cx=320, y=312..354)
b_dk, b_hi, b_sh = PAL['bench']
for y in range(328, 356):
    for x in range(248, 392):
        put(x, y, b_hi if y < 332 else (b_sh if y > 350 else b_dk))
for x in range(256, 384):
    put(x, 329, '#22d3ee' if x % 8 < 4 else '#4ade80')

# Maletín abierto e implante espinal Apogee Sandevistan (y=302..330, x=276..364)
im_m, im_hi, im_dk, im_cy, im_gr = PAL['implant']
for y in range(304, 330):
    for x in range(274, 366):
        col = im_dk if (y in (304, 329) or x in (274, 365)) else '#090d16'
        put(x, y, col)

# Vértebras cromadas y nodos de flujo cian-esmeralda del Sandevistan
for seg in range(7):
    vx = 286 + seg * 11
    for dy in range(-5, 6):
        for dx in range(-4, 5):
            if abs(dx) + abs(dy) <= 6:
                c_v = im_hi if dy < -2 else (im_dk if dy > 2 else im_m)
                put(vx + dx, 317 + dy, c_v)
    # Núcleo energético brillante entre vértebras
    for dy in range(-2, 3):
        put(vx, 317 + dy, im_cy if seg % 2 == 0 else im_gr)
    put(vx + 5, 317, '#a5f3fc')
glow(320, 317, 26, '#22d3ee', 0.38 if FASE != 'dia' else 0.16)

# Expendedor de bebidas / caja neón a la izquierda para dar profundidad (x=14..58, y=240..336)
for y in range(242, 336):
    for x in range(16, 56):
        put(x, y, '#141a2e' if x > 48 else '#1e2846')
for y in range(250, 294):
    for x in range(22, 46):
        put(x, y, '#0ea5e9' if (y // 6) % 2 == 0 else '#f43f5e')
glow(34, 272, 16, '#0ea5e9', 0.30 if FASE != 'dia' else 0.12)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
