#!/usr/bin/env python3
"""PixelZen Worlds - Cyberpunk Edgerunners (Secundario): David & Lucy mirando la Luna sobre Night City."""
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
random.seed(1502)

PALETAS = {
    'noche': dict(
        sky=['#040614', '#080c24', '#0e1538', '#15204e', '#1e2c66', '#2a3a7e', '#3a4a96', '#4f5aae', '#6c68bc', '#327c9e'],
        moon=('#f0f9ff', '#cbd5e1', '#94a3b8', '#64748b', '#38bdf8'),
        skyline=('#0b1024', '#141d3c', '#060914'),
        roof=('#13192b', '#202a46', '#0a0e18', '#34446b'),
        ledge=('#1d263e', '#303f64', '#0e1320'),
        david=('#facc15', '#ca8a04', '#1e293b', '#0f172a', '#451a03'),
        lucy=('#f8fafc', '#cbd5e1', '#1e1b2e', '#38bdf8', '#f472b6'),
        vig=0.68,
        nube=['#1d274e', '#283668', '#354682', '#44589c', '#576db2', '#141c38'],
    ),
    'dorado': dict(
        sky=['#0c0a1e', '#161232', '#261c46', '#3a2658', '#543266', '#74406e', '#98506e', '#bc6868', '#de8662', '#f8b26a'],
        moon=('#fffbeb', '#e2e8f0', '#cbd5e1', '#94a3b8', '#fde047'),
        skyline=('#141028', '#221c40', '#0a0814'),
        roof=('#1a182c', '#2b2846', '#0e0c18', '#44406c'),
        ledge=('#25223c', '#3c3860', '#141222'),
        david=('#fde047', '#eab308', '#1e293b', '#0f172a', '#451a03'),
        lucy=('#f8fafc', '#cbd5e1', '#1e1b2e', '#38bdf8', '#fb7185'),
        vig=0.76,
        nube=['#3a2452', '#503066', '#6a3e78', '#864e86', '#a4648e', '#26183a'],
    ),
    'dia': dict(
        sky=['#152e60', '#1e4282', '#2a58a4', '#3b72c2', '#528ed8', '#72aae8', '#98c4f4', '#bfe0fc', '#e0d6ee', '#f6c8dc'],
        moon=('#ffffff', '#e2e8f0', '#cbd5e1', '#94a3b8', '#38bdf8'),
        skyline=('#1e2b4e', '#2e406e', '#121a32'),
        roof=('#24304c', '#36486e', '#141c2e', '#526ca0'),
        ledge=('#324264', '#485e8c', '#1e2840'),
        david=('#facc15', '#ca8a04', '#1e293b', '#0f172a', '#451a03'),
        lucy=('#ffffff', '#cbd5e1', '#1e1b2e', '#06b6d4', '#f43f5e'),
        vig=0.86,
        nube=['#eef2fc', '#dce4f4', '#cad4ec', '#fbfcfe', '#d8d6ec', '#b0bcd8'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#22d3ee', '#818cf8'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#22d3ee', base='#f0f9ff', sombra='#bae6fd', crater='#7dd3fc', crater_hi='#a5f3fc'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#fde68a', centro='#fff8f0', borde='#fbbf24', rayo='#fef3c7'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS)

# Gigantesca Luna cinematográfica en el centro del cielo (316, 92) R=50 usando cráteres reales sin bandas diagonales
mcx, mcy, mr = 316, 92, 50
m_hi, m_mid, m_sh, m_cr, m_rim = PAL['moon']
dibuja_luna_estandar(lz, mcx, mcy, mr, halo=m_rim, base=m_hi, sombra=m_mid, crater=m_cr, crater_hi=m_sh)

render_nubes(lz, [(86, 42, 84, PAL['nube'][1], 2), (218, 34, 76, PAL['nube'][2], 2), (416, 46, 82, PAL['nube'][3], 2)], NUBES, ANIM)

# Horizonte lejano de rascacielos de Night City (manteniendo x>=478, y<=220 despejado para el HUD)
sk_dk, sk_mid, sk_sh = PAL['skyline']
b_specs = [
    (0, 34, 154), (36, 40, 174), (80, 44, 138), (128, 38, 166), (170, 52, 148),
    (226, 36, 186), (266, 34, 198), (362, 38, 190), (404, 48, 152), (456, 22, 224),
    (482, 54, 228), (540, 100, 232),
]
rng_s = random.Random(1522)
for bx, bw, btop in b_specs:
    for y in range(btop, 264):
        for x in range(bx, bx + bw):
            if 0 <= x < W:
                put(x, y, sk_sh if x < bx + 3 else (sk_mid if x > bx + bw - 5 else sk_dk))
    # Pequeñas luces cian/ámbar de ventanas
    for vy in range(btop + 8, 250, 7):
        for vx in range(bx + 5, bx + bw - 5, 6):
            if rng_s.random() < 0.30 and not (vx >= 472 and vy <= 220):
                vc = '#38bdf8' if rng_s.random() < 0.5 else ('#f472b6' if rng_s.random() < 0.4 else '#fde047')
                put(vx, vy, vc)
                put(vx + 1, vy, vc)

# Viaducto del monorraíl NCART cruzando a media altura (y=222..236)
for y in range(226, 236):
    for x in range(W):
        put(x, y, '#0b1022' if y > 228 else '#1e2944')
for px in range(28, W, 68):
    for y in range(236, 264):
        for dx in range(-2, 3):
            put(px + dx, y, '#0c1122')
# Tren NCART iluminado pasando por el viaducto (x=96..226)
for car_i in range(4):
    tx0 = 96 + car_i * 33
    for dy in range(7):
        for dx in range(29):
            c_tr = '#38bdf8' if (dy in (2, 3) and dx % 4 != 0) else '#0f172a'
            put(tx0 + dx, 219 + dy, c_tr)
glow(162, 222, 18, '#38bdf8', 0.35)


# Terraza / Azotea en primer plano (y=262..400)
rf_dk, rf_mid, rf_sh, rf_rim = PAL['roof']
lg_dk, lg_hi, lg_sh = PAL['ledge']
r_rf = Ruido(1508)
for y in range(262, H):
    for x in range(W):
        tex = fbm(r_rf, x * 0.06 + y * 0.14)
        col = rf_sh if tex < 0.38 else (rf_dk if tex < 0.65 else rf_mid)
        put(x, y, col)
        # Juntas geométricas de hormigón en perspectiva
        if y in (264, 290, 326, 368):
            put(x, y, rf_rim if y == 264 else '#0b0e1c')

# Reflejo suave de la Luna en un charco de la azotea (x=282..354, y=336..380)
for y in range(336, 382):
    hw = int(32 * math.sin(((y - 336) / 46.0) * math.pi))
    for x in range(318 - hw, 318 + hw + 1):
        if (x + y) % 2 == 0 and fbm(r_rf, x * 0.08 + y * 0.2) > 0.38:
            over(x, y, '#bae6fd' if abs(x - 318) < 16 else '#38bdf8', 0.34)

# Unidad HVAC de azotea a la izquierda (x=26..96, y=248..296)
for y in range(250, 296):
    for x in range(28, 96):
        put(x, y, '#141a2c' if x > 82 else ('#283454' if y < 254 else '#1c243c'))
for vx in range(36, 78, 8):
    for vy in range(260, 286, 4):
        for dx in range(5):
            put(vx + dx, vy, '#0b0e18')
put(90, 256, '#4ade80')
glow(90, 256, 5, '#4ade80', 0.45)

# Balizas de seguridad del pretil de la azotea
for bx in (42, 148, 240, 396, 512, 608):
    for dy in range(4):
        put(bx, 260 + dy, '#334155')
    put(bx, 259, '#38bdf8' if bx % 2 == 0 else '#f472b6')
    if bx < 450:
        glow(bx, 259, 6, '#38bdf8' if bx % 2 == 0 else '#f472b6', 0.42)


# Banco / muro de hormigón central donde están sentados David y Lucy mirando la Luna
for y in range(292, 326):
    for x in range(248, 388):
        col = lg_hi if y < 296 else (lg_sh if y > 320 else lg_dk)
        put(x, y, col)
for x in range(252, 384):
    over(x, 293, '#bae6fd', 0.28)


def paint_seated_david_and_lucy():
    d_y, d_yd, d_k, d_k2, d_h = PAL['david']
    l_w, l_wd, l_k, l_c, l_p = PAL['lucy']
    # David sentado a la izquierda (cx=294, asiento en y=293, torso 252..293, piernas 293..318)
    for dy in range(40):
        py = 254 + dy
        if dy < 9:
            # Cabeza ligeramente girada mirando la Luna y a Lucy
            hw = 5 if dy in (0, 8) else (7 if dy in (1, 7) else 8)
            for dx in range(-hw, hw + 1):
                c = d_h if (dy < 5 or abs(dx) > 5) else '#f5cba7'
                put(294 + dx, py, c)
        elif dy < 36:
            # Chaqueta amarilla Edgerunners con cuello alto y línea verde/cian en la espalda
            hw = 10 if dy < 15 else (11 if dy < 28 else 9)
            for dx in range(-hw, hw + 1):
                col = d_k if (dy < 13 and abs(dx) <= 6) else (d_yd if abs(dx) >= hw - 2 else d_y)
                if dy in (18, 22, 26) and abs(dx) <= 2:
                    col = '#22d3ee'
                put(294 + dx, py, col)
        else:
            # Piernas colgando sobre el muro
            for legx in (-6, -5, -4, -3, 3, 4, 5, 6):
                for extray in range(22):
                    put(294 + legx, 293 + extray, '#0f172a' if extray < 18 else '#1e293b')

    # Brazo de David extendido suavemente sobre el muro hacia Lucy
    for dx in range(8, 21):
        for dy in range(4):
            put(294 + dx, 280 + dy, d_y if dx < 18 else '#f5cba7')

    # Lucy sentada al lado de David (cx=336, cabeza apoyándose ligeramente hacia él)
    for dy in range(38):
        py = 256 + dy
        if dy < 9:
            hw = 5 if dy in (0, 8) else 7
            for dx in range(-hw, hw + 1):
                c = l_w if (dy < 6 or dx > 3) else ('#fce7dc' if dx > -4 else l_c)
                put(336 + dx, py, c)
            if dy in (5, 6, 7):
                put(336 - hw, py, l_c)
                put(336 + hw, py, l_p)
        elif dy < 35:
            # Chaqueta corta blanca/oscura y silueta delgada
            hw = 8 if dy < 14 else 9
            for dx in range(-hw, hw + 1):
                col = l_w if abs(dx) > 4 else (l_k if dy > 22 else '#e2e8f0')
                put(336 + dx, py, col)
        else:
            for legx in (-5, -4, -3, 2, 3, 4):
                for extray in range(21):
                    put(336 + legx, 293 + extray, '#181826' if extray < 17 else '#0f172a')

    # Contorno brillante de luz lunar sobre ambos hombros y cabezas
    for dx in range(-7, 8):
        over(294 + dx, 253, '#e0f2fe', 0.65)
        over(336 + dx, 255, '#e0f2fe', 0.65)
    glow(315, 274, 24, '#38bdf8', 0.24 if FASE != 'dia' else 0.12)


paint_seated_david_and_lucy()

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[mcx, mcy, mr], con_astro=False,
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
