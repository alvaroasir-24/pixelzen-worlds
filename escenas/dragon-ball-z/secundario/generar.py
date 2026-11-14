#!/usr/bin/env python3
"""PixelZen Worlds - Dragon Ball Z (Monitor 2): Planeta Namek, 7 Esferas y Dragón Sagrado."""
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
random.seed(1402)

PALETAS = {
    'noche': dict(
        sky=['#02080a', '#051416', '#0a2220', '#10342e', '#18483c', '#24604a', '#367856', '#4e9260', '#70aa6a', '#9cc278'],
        land=('#0f3836', '#1c5a50', '#061a1b', '#368270'),
        house=('#cbd5e1', '#f8fafc', '#64748b', '#94a3b8'),
        dragon=('#166534', '#22c55e', '#052e16', '#86efac', '#facc15'),
        agua='#092826',
        olas=('#5eead4', '#fbbf24', '#064e3b'),
        reflejo=('#fef08a', '#6ee7b7'),
        vig=0.72,
        nube=['#102826', '#1c3e3a', '#2c564e', '#407064', '#5c8c78', '#0a1c1a'],
    ),
    'dorado': dict(
        sky=['#0a0e1a', '#161c2e', '#262e42', '#3a4254', '#565860', '#7c6e5c', '#a88652', '#d2a24a', '#f2c054', '#ffe484'],
        land=('#184842', '#267264', '#0a2422', '#469e88'),
        house=('#e2e8f0', '#ffffff', '#64748b', '#cbd5e1'),
        dragon=('#15803d', '#4ade80', '#052e16', '#bbf7d0', '#fde047'),
        agua='#123a36',
        olas=('#fde047', '#5eead4', '#0f766e'),
        reflejo=('#fef08a', '#99f6e4'),
        vig=0.80,
        nube=['#283044', '#3c465a', '#565e6e', '#76787e', '#9c9288', '#1c2232'],
    ),
    'dia': dict(
        sky=['#0a485a', '#14667a', '#228698', '#36a6b4', '#54c4cc', '#7edcde', '#aaeefa', '#cef6f4', '#e8faf2', '#f6fbee'],
        land=('#147868', '#24a88e', '#0a443c', '#5eead4'),
        house=('#f1f5f9', '#ffffff', '#94a3b8', '#cbd5e1'),
        dragon=('#16a34a', '#4ade80', '#14532d', '#bbf7d0', '#facc15'),
        agua='#10786c',
        olas=('#a7f3d0', '#fef08a', '#047857'),
        reflejo=('#fef9c3', '#ffffff'),
        vig=0.88,
        nube=['#ffffff', '#eefcf8', '#daf6ee', '#f8fffd', '#e4faf4', '#b8dcd4'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#facc15', '#22c55e'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 36, halo='#5eead4', base='#f0fdfa', sombra='#99f6e4', crater='#5eead4', crater_hi='#ccfbf1'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#fef08a', centro='#ffffff', borde='#f59e0b', rayo='#fde047'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffffff', '#fef08a', '#99f6e4'])

MX, MY, MR = 112, 68, 32
NUBES_DEF = [
    (96, 48, 80, PAL['nube'][1], 2),
    (412, 54, 88, PAL['nube'][2], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)


def dibuja_islas_namek():
    """Islas azul-verdosas, árboles Ajisa esféricos y casas namekianas redondeadas en HOR=280."""
    ln0, ln1, ln2, ln3 = PAL['land']
    hs0, hs1, hs2, hs3 = PAL['house']

    # Islas en el horizonte izquierdo y centro-derecha
    for x in range(W):
        if x > 475:
            h_top = 264
        else:
            h_top = int(244 - 16 * math.sin(x * 0.014) - 8 * math.cos(x * 0.04))
        for y in range(h_top, HOR + 1):
            put(x, y, ln3 if y < h_top + 4 else (ln1 if (x + y) % 5 else (ln2 if y > HOR - 5 else ln0)))

    # Árboles Ajisa esféricos azul-verdosos (cx=62, 162, 418, 466)
    for ax, ay_b, ar in ((54, 248, 16), (168, 250, 14), (416, 256, 15), (464, 260, 13)):
        for y in range(ay_b - ar, ay_b + 8):
            for dx in range(-4, 5):
                put(ax + dx, y, '#645238' if dx < 1 else '#423424')
        disc(ax, ay_b - ar - 4, ar, ln2)
        disc(ax - 2, ay_b - ar - 6, ar - 3, ln1)
        disc(ax - 4, ay_b - ar - 9, max(3, ar - 7), ln3)

    # Casas namekianas blancas hemisféricas con antenas (cx=114, 376)
    for hx_c, hy_b, hr in ((114, 258, 22), (376, 262, 18)):
        for dy in range(-hr, 2):
            for dx in range(-hr, hr + 1):
                if dx * dx + dy * dy <= hr * hr:
                    put(hx_c + dx, hy_b + dy, hs1 if dx < -hr // 4 else (hs0 if dx < hr // 3 else hs2))
        for dy in range(-8, 1):
            for dx in range(-4, 5):
                put(hx_c + dx, hy_b + dy, '#1e293b')
        for side in (-1, 1):
            for k in range(12):
                put(hx_c + side * (6 + k // 2), hy_b - hr - k + 4, hs3)


def dibuja_dragon_sagrado_y_esferas(cx, by):
    """Gran Dragón Sagrado (Shenron / Porunga) verde-esmeralda y las 7 Esferas del Dragón brillantes."""
    dr0, dr1, dr2, dr3, gold = PAL['dragon']

    # Columna de luz dorada emergiendo de las 7 Esferas del Dragón hacia el Dragón (cx=288, by=HOR=280)
    for y in range(132, by):
        hw = int(8 + 20 * (1.0 - (y - 132) / float(by - 132)))
        for dx in range(-hw, hw + 1):
            if dith(cx + dx, y, 0.45 * (1.0 - abs(dx) / float(max(1, hw)))):
                over(cx + dx, y, gold, 0.36)

    # Relámpagos dorados irradiando del cielo
    for lx_r in (cx - 72, cx + 68):
        for seg in range(10):
            rx = lx_r + int(math.sin(seg * 1.3) * 10)
            ry = 20 + seg * 12
            for k in range(12):
                over(rx, ry + k, gold if k % 2 else '#ffffff', 0.80)

    # Cuerpo serpentino monumental del Dragón Sagrado (cx=288, de y=268 hasta y=92)
    for s in range(120):
        u = s / 119.0
        px = int(round(cx + math.sin(u * math.pi * 2.2) * 38))
        py = int(round(268 - u * 168))
        rad = max(6, int(round(14 * (1.0 - 0.35 * u))))
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                if dx * dx + dy * dy <= rad * rad:
                    col = dr2 if dx > rad // 2 else (dr3 if dx < -rad // 2 else (dr1 if (dx + s) % 3 else dr0))
                    if abs(dx) < rad // 2 and dy > 0:
                        col = gold if (s % 4) else '#b45309'
                    put(px + dx, py + dy, col)

    # Gran Cabeza del Dragón en y=104 con cuernos dorados, melena, bigotes y ojos rojos brillantes
    hx, hy = cx - 8, 98
    for dy in range(-14, 16):
        for dx in range(-20, 18):
            if (dx * dx) / 380.0 + (dy * dy) / 180.0 <= 1.0:
                put(hx + dx, hy + dy, dr1 if dy < 2 else (dr2 if dy > 9 else dr0))
    # Ojos rojos brillantes + cuernos ramificados marrones/oro
    put(hx - 8, hy - 4, '#ef4444')
    put(hx - 7, hy - 4, '#fef08a')
    for k in range(20):
        put(hx + 4 + k // 2, hy - 12 - k, gold)
        put(hx + 10 + k // 2, hy - 10 - k, '#d97706')
    for k in range(28):
        put(hx - 16 - k, hy + 4 + int(5 * math.sin(k * 0.25)), gold)

    # Las 7 Esferas del Dragón brillantes en arco frente al horizonte (by=275)
    for i, ox in enumerate((-48, -32, -16, 0, 16, 32, 48)):
        bx = cx + ox
        by_s = by - 5 - (1 if i % 2 else 0)
        if not ANIM:
            glow(bx, by_s, 7, gold, 0.65)
        disc(bx, by_s, 4, '#ea580c')
        disc(bx - 1, by_s - 1, 3, gold)
        put(bx, by_s, '#dc2626')
    if ANIM:
        RUNAS.append([cx, by - 8])
        FAROLES.append([hx - 6, hy - 4, 8])


dibuja_islas_namek()
dibuja_dragon_sagrado_y_esferas(288, HOR)

render_lago(lz, PAL['agua'], PAL['olas'], DESTELLOS, ANIM, mx=MX, hor=HOR, reflejo_cols=PAL['reflejo'])
aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
