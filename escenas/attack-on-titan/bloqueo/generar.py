#!/usr/bin/env python3
"""PixelZen Worlds - Attack on Titan (Bloqueo): Los Caminos, La Coordenada y Alas de la Libertad."""
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
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1203)

PALETAS = {
    'noche': dict(
        sky=['#02040e', '#04081a', '#08102a', '#0e1a3e', '#142656', '#1c346e', '#264688', '#345ba4', '#4674c0', '#5e90dc'],
        sand=('#18243c', '#2a3d60', '#0c1424', '#466294'),
        tree=('#d8f4ff', '#fef08a', '#7dd3fc'),
        tree_shiganshina='#090d16',
        vig=0.72,
        nube=['#0c162c', '#142240', '#1e3058', '#2a4272', '#38568e', '#081022'],
    ),
    'dorado': dict(
        sky=['#0a0b1c', '#161630', '#262244', '#3a3058', '#524068', '#705472', '#926c76', '#b88878', '#deaa82', '#ffe0a2'],
        sand=('#262840', '#404264', '#141624', '#686a94'),
        tree=('#fff4d4', '#fef08a', '#a5f3fc'),
        tree_shiganshina='#12101a',
        vig=0.80,
        nube=['#28223e', '#3c3254', '#52446a', '#6c5880', '#8a7098', '#1c1830'],
    ),
    'dia': dict(
        sky=['#143c7a', '#225496', '#326eb2', '#4888cc', '#64a2e0', '#84bce8', '#a8d4f4', '#cce6fa', '#e4f4fc', '#f4f8f0'],
        sand=('#687e9e', '#88a0c2', '#445674', '#b4cae4'),
        tree=('#ffffff', '#fef9c3', '#38bdf8'),
        tree_shiganshina='#1e2836',
        vig=0.88,
        nube=['#ffffff', '#eef6fc', '#dff0fa', '#f8fcff', '#e4f0fb', '#c8e0f0'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#22d3ee', '#fef08a'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#38bdf8', base='#f0f9ff', sombra='#bae6fd', crater='#7dd3fc', crater_hi='#a5f3fc'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#fef08a', centro='#ffffff', borde='#fbbf24', rayo='#fde047'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffffff', '#bae6fd', '#fef08a'])

MX, MY, MR = 320, 62, 32
NUBES_DEF = [
    (84, 46, 78, PAL['nube'][1], 2),
    (528, 58, 76, PAL['nube'][2], 1),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)


def dibuja_coordenada_astral(cx, by):
    """Gran Pilar/Árbol de Luz de la Coordenada ramificándose por todo el cielo."""
    c_core, c_gold, c_cyan = PAL['tree']
    # Pilar luminoso vertical (cx=320, y=126..268)
    for y in range(120, by + 2):
        hw = 3 + int(4 * (1.0 - (y - 120) / float(by - 120)))
        for dx in range(-hw - 8, hw + 9):
            ad = abs(dx)
            if ad <= hw:
                put(cx + dx, y, c_core if ad <= 2 else c_gold)
            elif dith(cx + dx, y, max(0.0, 0.72 * (1.0 - (ad - hw) / 8.0))):
                over(cx + dx, y, c_cyan, 0.55)

    # Haz astral de ramas fractales extendiéndose por el cielo sin invadir el HUD
    ramas = [
        (-0.35, 165, 1), (-0.75, 145, 2), (-1.15, 130, 1), (-1.55, 118, 2),
        (0.35, 140, 1), (0.72, 128, 2), (1.08, 112, 1),
    ]
    rng_r = random.Random(123)
    for ang_base, ln, depth in ramas:
        fx, fy = float(cx), 126.0
        for s in range(ln):
            u = s / float(ln)
            ang = ang_base - math.pi * 0.5 + 0.18 * math.sin(u * 5.0)
            fx += math.cos(ang) * 1.15
            fy += math.sin(ang) * 0.92
            ix, iy = int(round(fx)), int(round(fy))
            if iy < 4 or ix < 4 or ix > 470:
                break
            col = c_core if u < 0.35 else (c_gold if (s % 5) else c_cyan)
            over(ix, iy, col, max(0.25, 0.92 - 0.55 * u))
            if u < 0.5:
                over(ix + 1, iy, c_cyan, 0.50)
            if s > 20 and s % 28 == 0 and depth > 0:
                sub_ang = ang + rng_r.choice((-0.45, 0.45))
                sx, sy = fx, fy
                for k in range(36):
                    sx += math.cos(sub_ang) * 1.1
                    sy += math.sin(sub_ang) * 0.9
                    if int(sx) < 470 and int(sy) > 4:
                        over(int(sx), int(sy), c_cyan, max(0.18, 0.72 - k / 45.0))
    if ANIM:
        RUNAS.append([cx, 134])
        FAROLES.append([cx, 168, 12])
    else:
        glow(cx, 134, 34, c_cyan, 0.48)


def dibuja_desierto_caminos_y_memorial(cx):
    """Dunas luminiscentes en y=254..400 + Colina del árbol solitario + Espadas ODM & Bufanda."""
    sd0, sd1, sd2, sd3 = PAL['sand']
    r_d = Ruido(1233)

    # Colina + árbol gigante de Shiganshina en el flanco izquierdo (cx=128, top_y=198)
    for x in range(W):
        hill = int(258 - 22 * math.exp(-(((x - 128) / 72.0) ** 2)) + 6 * math.sin(x * 0.025))
        for y in range(hill, H):
            n = fbm(r_d, x * 0.03 + y * 0.05)
            wave = math.sin(x * 0.04 + y * 0.18) * 0.5 + 0.5
            col = sd3 if (wave > 0.65 and n > 0.46) else (sd1 if n > 0.42 else (sd0 if n > 0.22 else sd2))
            if y < hill + 3:
                col = PAL['tree'][0] if abs(x - cx) < 90 else sd3
            put(x, y, col)
    # Silueta del árbol en la colina
    lz.rama([(128, 240), (126, 214), (122, 194)], 6.0, 2.0, PAL['tree_shiganshina'], sd1)
    lz.rama([(126, 214), (108, 198), (94, 192)], 3.2, 1.0, PAL['tree_shiganshina'], sd1)
    lz.rama([(126, 210), (144, 196), (158, 192)], 3.2, 1.0, PAL['tree_shiganshina'], sd1)
    for dy in range(-22, 14):
        for dx in range(-34, 35):
            if (dx * dx) / 1150.0 + (dy * dy) / 360.0 <= 1.0 and dith(128 + dx, 186 + dy, 0.84):
                put(128 + dx, 186 + dy, PAL['tree_shiganshina'])

    # Memorial central en primer plano (cx=320, by=350): Piedra + Espadas ODM cruzadas + Capa Alas de la Libertad + Bufanda Roja
    for dy in range(-10, 14):
        hw = 40 + dy
        for dx in range(-hw, hw + 1):
            put(cx + dx, 340 + dy, '#162030' if (dy > 4 or abs(dx) > hw - 3) else '#2b3e5a')
    # Espadas ODM cruzadas clavadas en la piedra
    for side in (-1, 1):
        for k in range(38):
            bx = cx + side * int(k * 0.55)
            by_e = 338 - k
            put(bx, by_e, '#f8fafc')
            put(bx + 1, by_e, '#94a3b8')
        # Empuñadura metálica
        hx_e, hy_e = cx + side * 21, 300
        for t in range(-5, 6):
            put(hx_e + t, hy_e, '#475569')
        for k in range(8):
            put(hx_e + side * (k // 2), hy_e - k, '#1e293b')
    # Capa verde con Alas de la Libertad y bufanda carmesí envuelta en la base
    for dy in range(16):
        hw = 18 + dy // 2
        for dx in range(-hw, hw + 1):
            col = '#1e422a' if (dx % 4) else '#2e6440'
            if 4 <= dy <= 11 and (abs(abs(dx) - 6) <= 2):
                col = '#e2e8f0' if dy % 2 == 0 else '#38bdf8'
            put(cx + dx, 326 + dy, col)
    for k in range(44):
        sx = cx - 22 + k
        sy = 338 + int(4 * math.sin(k * 0.18))
        for t in range(-2, 3):
            put(sx, sy + t, '#dc2626' if t < 1 else '#991b1b')
    if ANIM:
        RUNAS.append([cx, 320])


dibuja_coordenada_astral(320, 260)
dibuja_desierto_caminos_y_memorial(320)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
