#!/usr/bin/env python3
"""PixelZen Worlds - Attack on Titan (Monitor 2): Shiganshina y Titán Colosal."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, Ruido, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    dith, exporta_salida, exporta_sprites_si_aplica, fbm, mix, pinta_sprite,
    render_cielo, render_estrellas, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'dorado')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1202)

PALETAS = {
    'noche': dict(
        sky=['#090612', '#140c22', '#221434', '#341e44', '#4a2a4c', '#66384c', '#864a46', '#a86042', '#cc7a44', '#ee9a52'],
        wall=('#26222c', '#3a3442', '#141118', '#524a5e'),
        flesh=('#7a1c1c', '#a82e28', '#3c0b0c', '#d4483a', '#f5e8d8'),
        house=('#221c22', '#382c32', '#120d10', '#d8cab8', '#7e2a24'),
        vig=0.72,
        nube=['#241c34', '#382a46', '#4e3858', '#684866', '#845a72', '#1a1226'],
    ),
    'dorado': dict(
        sky=['#140b18', '#261426', '#421e30', '#642a32', '#8a3c2c', '#b25426', '#d67226', '#f29430', '#ffb848', '#ffdc7c'],
        wall=('#382c32', '#524048', '#1e161a', '#705862'),
        flesh=('#8e201c', '#c6362c', '#460c0b', '#eb5842', '#faf0e0'),
        house=('#2c2224', '#463436', '#161012', '#e8dac8', '#9c362c'),
        vig=0.80,
        nube=['#4e242c', '#6e3232', '#944434', '#ba5a36', '#de7842', '#381822'],
    ),
    'dia': dict(
        sky=['#1d4e92', '#2d64aa', '#407cc0', '#5a94d4', '#78aee4', '#96c6ee', '#b4dcf6', '#d0ecf8', '#e6f4fc', '#f4f8ee'],
        wall=('#5a5460', '#787080', '#3a3640', '#9a90a2'),
        flesh=('#9e2824', '#d64438', '#521010', '#f46852', '#ffffff'),
        house=('#3e3438', '#5c4c50', '#241e20', '#f4ece2', '#b44234'),
        vig=0.88,
        nube=['#ffffff', '#eef6fc', '#deeffa', '#f8fcff', '#e4f0fb', '#c6ddf0'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#facc15', '#f97316'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#fbbf24', base='#fff4e8', sombra='#ddc4b8', crater='#b4988e', crater_hi='#cab0a6'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe49e', centro='#fffef2', borde='#ffb448', rayo='#ffd88c'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#fef3c7', '#fed7aa', '#e2e8f0'])

MX, MY, MR = 380, 62, 34
NUBES_DEF = [
    (82, 42, 84, PAL['nube'][0], 2),
    (386, 52, 92, PAL['nube'][2], 2),
    (520, 68, 72, PAL['nube'][3], 1),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# Relámpago dorado de transformación cayendo sobre el Titán Colosal (cx=202)
lx_c = 202
for seg in range(18):
    y0_b = seg * 8
    x0_b = lx_c + int(math.sin(seg * 1.4) * 14) - (18 - seg) // 2
    for dy in range(9):
        px = x0_b + int(math.cos(seg + dy * 0.4) * 2)
        py = y0_b + dy
        if 0 <= py < 146:
            put(px, py, '#ffffff')
            over(px - 1, py, '#facc15', 0.85)
            over(px + 1, py, '#facc15', 0.85)
if not ANIM:
    glow(202, 104, 42, '#facc15', 0.45)

# Colosal cabeza y hombros del Titán Colosal asomando sobre Muralla María (cx=202, y=78..212)
fl0, fl1, fl2, fl3, te = PAL['flesh']
# Hombros y trapecio masivos agarrando el borde del muro
for y in range(154, 214):
    hw = int(42 + (y - 154) * 0.9)
    for dx in range(-hw, hw + 1):
        u = dx / float(max(1, hw))
        bundle = ((dx + int(4 * math.sin(y * 0.14))) % 6 == 0)
        col = fl2 if (abs(dx) >= hw - 2 or bundle) else (fl3 if abs(dx) < 16 and y % 5 == 0 else (fl1 if u < 0.1 else fl0))
        put(202 + dx, y, col)
# Cráneo anatómico sin piel del Titán Colosal (cx=202, cy=120)
for dy in range(-44, 46):
    for dx in range(-32, 33):
        nx, ny = dx / 31.0, dy / 43.0
        if dy > 14:
            in_h = abs(dx) <= 21 - (dy - 14) // 2
        else:
            in_h = (nx * nx + ny * ny <= 1.0)
        if in_h:
            arc = ((dx * dx + dy * 5) % 9 == 0) or (abs(dx) > 17 and dy > 10 and (dy % 4 == 0))
            col = fl2 if (arc or nx * nx + ny * ny > 0.86) else (fl3 if ny < -0.25 and nx < 0.25 else (fl1 if nx < 0 else fl0))
            # Cuenca ocular profunda + brasa ocular
            if math.hypot(abs(dx) - 11, dy + 4) < 6.8:
                col = '#140305'
                if math.hypot(abs(dx) - 11, dy + 4) < 2.8:
                    col = '#fef08a'
            elif abs(dx) <= 2 and 4 <= dy <= 10:
                col = '#160406'
            elif 14 <= dy <= 34 and abs(dx) <= 13:
                # Mandíbula desollada y dentadura más orgánica con encía muscular
                gum_curve = 23 + int(2 * math.cos(dx * 0.2))
                if abs(dy - gum_curve) <= 1:
                    col = '#26080b'
                elif 17 <= dy <= 29 and (abs(dx) % 4 != 0) and abs(dx) <= 11:
                    col = te if abs(dy - 22) < 4 else '#d6c3ac'
                elif abs(dx) > 11:
                    col = fl2
            put(202 + dx, 120 + dy, col)
if ANIM:
    FAROLES.append([191, 116, 7])
    FAROLES.append([213, 116, 7])

# Gran Muralla María de 50 metros en y=194..268 con almenas y cañones
w0, w1, w2, w3 = PAL['wall']
for y in range(194, 268):
    for x in range(W):
        if y < 200 and (x // 16) % 2 == 1 and x not in range(148, 258):
            continue
        block = ((x + (y // 7) * 10) % 20 == 0) or (y % 7 == 0)
        col = w2 if block else (w3 if y < 206 else (w1 if (x % 9 == 0) else w0))
        put(x, y, col)
# Dedos enormes de ambas manos agarrándose al borde de la Muralla María
for hx_m in (124, 280):
    for f_i in range(-2, 3):
        fx_k = hx_m + f_i * 5
        for dy in range(-7, 10):
            for dx in range(-2, 3):
                put(fx_k + dx, 198 + dy, fl2 if (dx == 2 or dy > 6) else (fl3 if dy < -4 else fl1))
# Cañones sobre la muralla
for cx_g in (74, 344, 412):
    for dx in range(-8, 9):
        for dy in range(-5, 3):
            put(cx_g + dx, 192 + dy, '#18181b' if abs(dx) < 5 else '#475569')

# Distrito de Shiganshina en primer plano (y=264..400): suelo empedrado y tejados variados
hs0, hs1, hs2, wall_c, rf_c = PAL['house']
for y in range(264, H):
    for x in range(W):
        seam = (y % 9 == 0) or ((x + (y // 9) * 12) % 24 == 0)
        put(x, y, hs2 if seam else (hs1 if (x + y) % 8 == 0 else '#14121b'))

# Casas Fachwerk variadas de Shiganshina (enlucido claro, vigas de roble, tejas y ventanas cálidas)
casas = [(8, 122, 244, 38), (140, 106, 264, 32), (258, 120, 250, 36), (388, 108, 266, 32), (508, 124, 248, 38)]
for idx_c, (x0, cw, top_y, rf_h) in enumerate(casas):
    plaster = '#cfc4b2' if idx_c % 2 == 0 else '#bfb29e'
    plaster_sh = '#9e907e'
    beam_c = '#38221a'
    # Chimenea lateral de ladrillo en algunas casas
    if idx_c in (0, 2, 4):
        ch_x = x0 + cw // 4
        for dy in range(top_y - 12, top_y + 20):
            for dx in range(-4, 5):
                put(ch_x + dx, dy, '#4a352c' if dx < 2 else '#2a1d17')
    for y in range(top_y + rf_h - 2, 388):
        for x in range(x0 + 8, x0 + cw - 8):
            rx = x - (x0 + 8)
            rw = cw - 16
            ry = y - (top_y + rf_h - 2)
            # Entramado medieval horizontal, vertical y diagonales en esquinas
            timber = (
                ry < 3 or ry in (28, 29, 58, 59) or
                rx < 3 or rx >= rw - 3 or abs(rx - rw // 2) <= 1 or
                (ry < 28 and abs(rx - ry) <= 1) or
                (ry < 28 and abs((rw - rx) - ry) <= 1)
            )
            col = beam_c if timber else (plaster_sh if (rx > rw - 14 or (x + y) % 11 == 0) else plaster)
            put(x, y, col)
    # Ventanas cálidas con marco de madera (2 pisos, 2-3 ventanas limpias)
    for wx in (x0 + cw // 4 - 4, x0 + (3 * cw) // 4 - 4):
        for wy in (top_y + rf_h + 10, top_y + rf_h + 40):
            for dy in range(11):
                for dx in range(9):
                    is_fr = (dy in (0, 5, 10) or dx in (0, 4, 8))
                    vc = '#1c100d' if is_fr else ('#fef08a' if (idx_c + wy) % 3 else '#fb923c')
                    put(wx + dx, wy + dy, vc)
            glow(wx + 4, wy + 5, 8, '#f59e0b', 0.24 if FASE != 'dia' else 0.08)
    # Tejado terracota a dos aguas con alero
    mid_x = x0 + cw // 2
    for dy in range(rf_h):
        hw = int((cw * 0.56) * (dy / float(max(1, rf_h - 1)))) + 4
        for dx in range(-hw, hw + 1):
            shingle = ((dy % 4 == 0) or ((dx + dy // 2) % 6 == 0))
            col_r = beam_c if abs(dx) >= hw - 1 else (mix(rf_c, '#0e0808', 0.28) if (shingle or dx > hw // 3) else rf_c)
            put(mid_x + dx, top_y + dy, col_r)

# Dos soldados del Cuerpo de Exploración observando en un tejado central (cx=316, by=292)
for sx in (310, 336):
    for dy in range(-22, 1):
        for dx in range(-5, 6):
            if abs(dx) <= (3 if dy < -14 else (5 if dy < -5 else 3)):
                put(sx + dx, 294 + dy, '#1e422a' if -14 <= dy < -5 else ('#f4d2be' if dy < -14 else '#261c18'))
    if ANIM:
        RUNAS.append([sx, 276])

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR], con_astro=False,
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
