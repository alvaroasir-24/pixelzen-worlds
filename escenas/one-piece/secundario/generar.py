#!/usr/bin/env python3
"""PixelZen Worlds - One Piece (Monitor 2): Thousand Sunny navegando el Nuevo Mundo."""
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
random.seed(1302)

PALETAS = {
    'noche': dict(
        sky=['#030816', '#061028', '#0a1a3c', '#102654', '#18346c', '#224486', '#2e589e', '#3e6eb6', '#5486cc', '#70a0e0'],
        hull=('#881c22', '#b82830', '#480c12', '#c88c52', '#8c582c'),
        sail=('#d8e2f0', '#f8fafc', '#94a3b8', '#0f172a'),
        lion=('#d97706', '#f59e0b', '#fbbf24', '#78350f'),
        agua='#0a1e44',
        olas=('#7dd3fc', '#38bdf8', '#0c4a6e'),
        reflejo=('#fef08a', '#bae6fd'),
        vig=0.72,
        nube=['#16264a', '#223868', '#304c86', '#4060a2', '#5678be', '#101a36'],
    ),
    'dorado': dict(
        sky=['#140c24', '#26163a', '#42224c', '#663454', '#8e4a4c', '#b66644', '#da8640', '#f6a84c', '#ffca68', '#ffe89c'],
        hull=('#9c2228', '#d2343c', '#541014', '#deb068', '#a06a34'),
        sail=('#f8f0e4', '#ffffff', '#c8b8a8', '#141220'),
        lion=('#ea580c', '#f59e0b', '#fde047', '#7c2d12'),
        agua='#1c284c',
        olas=('#fed7aa', '#fdba74', '#4338ca'),
        reflejo=('#fde68a', '#fca5a5'),
        vig=0.80,
        nube=['#442442', '#623250', '#864456', '#ac5a5a', '#d07660', '#321832'],
    ),
    'dia': dict(
        sky=['#144e98', '#2266b4', '#3480ce', '#4c9ce2', '#6ab6ee', '#8cccf6', '#aee0fa', '#cef0fc', '#e6f8fe', '#f6faf2'],
        hull=('#b82830', '#e43c44', '#681218', '#e6b874', '#ac743a'),
        sail=('#f1f5f9', '#ffffff', '#cbd5e1', '#1e293b'),
        lion=('#f59e0b', '#fbbf24', '#fef08a', '#92400e'),
        agua='#165c9c',
        olas=('#bae6fd', '#e0f2fe', '#0284c7'),
        reflejo=('#fff4c4', '#ffffff'),
        vig=0.88,
        nube=['#ffffff', '#eef6fc', '#deeffa', '#f8fcff', '#e4f0fb', '#c6ddf0'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#38bdf8', '#fde047'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#7dd3fc', base='#f8fafc', sombra='#cbd5e1', crater='#94a3b8', crater_hi='#b8c4d8'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe49e', centro='#fffef2', borde='#ffb448', rayo='#ffd88c'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffffff', '#bae6fd', '#fef08a'])

MX, MY, MR = 152, 68, 36
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#7dd3fc', base='#f8fafc', sombra='#cbd5e1', crater='#94a3b8', crater_hi='#b8c4d8')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 152, 118, 22, halo='#ff9860', centro='#fff2d8', borde='#ff562e', rayo='#ff824a')
    else:
        dibuja_sol_estandar(lz, 152, 74, 22, halo='#ffe49e', centro='#fffef2', borde='#ffb448', rayo='#ffd88c')

NUBES_DEF = [
    (68, 44, 76, PAL['nube'][1], 2),
    (298, 52, 88, PAL['nube'][2], 2),
    (438, 66, 72, PAL['nube'][3], 1),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)


def dibuja_thousand_sunny(cx, by):
    """El Thousand Sunny (cx=306, by=HOR=280) con mascarón de león, velas y Jolly Roger."""
    h0, h1, h2, wd, wd_dk = PAL['hull']
    s0, s1, s2, ink = PAL['sail']
    l0, l1, l2, l_dk = PAL['lion']

    # 1. Mástiles principal y mesana + nido de cuervo + bandera pirata
    for mx_p, m_top in ((cx - 32, 146), (cx + 18, 126)):
        for y in range(m_top, by - 30):
            for dx in range(-2, 3):
                put(mx_p + dx, y, wd_dk if abs(dx) == 2 else wd)
        # Vergas horizontales
        for y_v, vw in ((m_top + 18, 32), (m_top + 54, 42)):
            for dx in range(-vw, vw + 1):
                put(mx_p + dx, y_v, wd_dk)
                put(mx_p + dx, y_v + 1, wd)

    # Gran Vela Mayor hinchada con Jolly Roger de Luffy (cx+18, y=144..216)
    vx, vy = cx + 18, 144
    for dy in range(72):
        hw = int(34 + 8 * math.sin((dy / 71.0) * math.pi))
        bulge = int(10 * math.sin((dy / 71.0) * math.pi))
        for dx in range(-hw + bulge // 2, hw + bulge):
            col = s2 if abs(dx) >= hw - 3 + bulge // 2 else (s1 if dx < 0 else s0)
            put(vx + dx, vy + dy, col)
    # Jolly Roger: huesos cruzados + calavera + sombrero de paja sobre la vela
    cx_jr, cy_jr = vx + 5, vy + 36
    for k in range(-14, 15):
        put(cx_jr + k, cy_jr + k // 2, ink)
        put(cx_jr + k, cy_jr - k // 2, ink)
    disc(cx_jr, cy_jr, 8, ink)
    disc(cx_jr, cy_jr, 6, s1)
    put(cx_jr - 3, cy_jr, ink)
    put(cx_jr + 3, cy_jr, ink)
    for dx in range(-9, 10):
        put(cx_jr + dx, cy_jr - 5, l1)
    for dy in range(-9, -5):
        for dx in range(-6, 7):
            put(cx_jr + dx, cy_jr + dy, '#facc15' if dy < -6 else '#ef4444')

    # Vela secundaria izquierda
    vx2, vy2 = cx - 32, 164
    for dy in range(54):
        hw = int(24 + 6 * math.sin((dy / 53.0) * math.pi))
        for dx in range(-hw, hw + 1):
            put(vx2 + dx + 4, vy2 + dy, s2 if dy > 48 else (s1 if dx < 0 else s0))

    # 2. Casco icónico rojo/madera/césped del Thousand Sunny (y=226..280)
    for dy in range(54):
        y = by - 54 + dy
        u = dy / 53.0
        hw = int(84 - 18 * (u ** 1.8))
        for dx in range(-hw, hw + 1):
            col = h2 if (abs(dx) >= hw - 2 or dy > 46) else (wd if dy < 16 else (h1 if dy < 24 or dx < 0 else h0))
            if dy < 10 and -56 < dx < 28:
                col = '#22c55e' if (dx + dy) % 3 else '#15803d'
            put(cx + dx, y, col)
            # Ventanitas circulares del acuario y camarotes
            if 26 <= dy <= 34 and dx in (-42, -18, 8, 32):
                disc(cx + dx, y, 2, '#fef08a')
    # Barandilla blanca + naranjos de Nami en cubierta
    for dx in range(-72, 66):
        put(cx + dx, by - 55, s1 if (dx % 4) else h2)
    for nx in (cx - 46, cx - 34):
        for dy in range(10):
            put(nx, by - 56 - dy, wd_dk)
        disc(nx, by - 68, 7, '#15803d')
        disc(nx - 2, by - 70, 5, '#22c55e')
        put(nx - 2, by - 68, '#f97316')
        put(nx + 3, by - 67, '#f97316')

    # Mascarón de León (Figura de Proa derecha cx+86, cy=246)
    lx_f, ly_f = cx + 84, by - 36
    # Melena en forma de flor de 8 pétalos naranja/dorada
    for k in range(8):
        a = k * (math.pi / 4.0)
        disc(lx_f + int(round(math.cos(a) * 12)), ly_f + int(round(math.sin(a) * 12)), 5, l0 if k % 2 else l1)
    disc(lx_f, ly_f, 9, l2)
    disc(lx_f + 2, ly_f + 1, 6, '#fef3c7')
    put(lx_f + 1, ly_f - 2, l_dk)
    put(lx_f + 5, ly_f - 2, l_dk)
    put(lx_f + 3, ly_f + 1, '#9a3412')

    # Zoro (pelo verde + espadas) y Sanji (traje negro + Ifrit Jambe) en cubierta
    # Zoro (cx - 12, by - 55)
    for dy in range(-18, 0):
        for dx in range(-4, 5):
            put(cx - 12 + dx, by - 55 + dy, '#22c55e' if dy < -13 else ('#166534' if dy < -5 else '#0f172a'))
    # Sanji (cx + 10, by - 55)
    for dy in range(-18, 0):
        for dx in range(-4, 5):
            put(cx + 10 + dx, by - 55 + dy, '#facc15' if dy < -13 else ('#1e293b' if dy < -5 else '#0f172a'))
    if ANIM:
        FAROLES.append([cx - 12, by - 64, 7])
        FAROLES.append([cx + 10, by - 64, 7])
        RUNAS.append([cx + 18, by - 96])
    else:
        glow(cx - 12, by - 64, 8, '#22c55e', 0.45)
        glow(cx + 10, by - 64, 8, '#38bdf8', 0.45)


dibuja_thousand_sunny(304, HOR)

render_lago(lz, PAL['agua'], PAL['olas'], DESTELLOS, ANIM, mx=MX, hor=HOR, reflejo_cols=PAL['reflejo'])
aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
