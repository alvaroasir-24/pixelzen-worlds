#!/usr/bin/env python3
"""PixelZen Worlds - Jujutsu Kaisen (Principal): Sagrario Malevolente vs Vacío Infinito · Sukuna vs Gojo."""
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
random.seed(1101)

PALETAS = {
    'noche': dict(
        sky=['#090208', '#14040e', '#240816', '#380c1c', '#501022', '#6c1626', '#8a1e2a', '#a82a30', '#c43b3b', '#df524c'],
        void=['#030512', '#070c24', '#0e1844', '#1a2b6e', '#2c469a', '#466ee2', '#6ea8ff', '#cce8ff'],
        ruin=('#140d1b', '#221830', '#0a060f'),
        shrine_wood=('#240a10', '#3e121b', '#140508', '#5e1a28'),
        shrine_roof=('#19101a', '#2c1d2e', '#0d070e', '#4c324e'),
        bone=('#dfd3be', '#bfb09a', '#827362', '#f7efe0'),
        ground_l=('#16060b', '#260a12', '#0c0306', '#420f1a'),
        ground_r=('#090c1c', '#121a38', '#050712', '#263872'),
        sukuna=('#f4ece0', '#ccc0ae', '#140910', '#f47296', '#ef2348'),
        gojo=('#141928', '#28324c', '#f4f8ff', '#c8d6ec', '#38d8ff'),
        vig=0.72,
        nube=['#2a1020', '#3f172b', '#582036', '#742d42', '#903b4e', '#1e0a18'],
    ),
    'dorado': dict(
        sky=['#14050e', '#280a18', '#421222', '#601a2a', '#82242e', '#a63430', '#c84a32', '#e46836', '#f88e44', '#ffc066'],
        void=['#070a1c', '#10183a', '#1c2b64', '#2e4490', '#4868bc', '#6e94e8', '#98c2ff', '#e4f2ff'],
        ruin=('#241422', '#3a2236', '#140a14'),
        shrine_wood=('#341018', '#561c26', '#1c070c', '#7c2a36'),
        shrine_roof=('#261624', '#40263a', '#140b14', '#623a56'),
        bone=('#ece0c8', '#c8b89e', '#907e6c', '#fff6e4'),
        ground_l=('#220a10', '#361018', '#120508', '#561822'),
        ground_r=('#0e1226', '#1c264c', '#080a16', '#324888'),
        sukuna=('#f8f0e4', '#d4c6b2', '#180a12', '#fb7ca0', '#f43252'),
        gojo=('#1b2032', '#323c5a', '#f8fbff', '#d2dff2', '#4ae2ff'),
        vig=0.80,
        nube=['#441a28', '#622434', '#843240', '#aa444a', '#cf5e56', '#32121e'],
    ),
    'dia': dict(
        sky=['#1a3668', '#264b84', '#3662a0', '#4a7cb8', '#6496ce', '#84b2e0', '#a6ccf0', '#cae2f8', '#e8dce8', '#f6c4c6'],
        void=['#0f1e4a', '#193070', '#284a9c', '#3c6ac4', '#5c90e6', '#88b8fc', '#badcff', '#eaf6ff'],
        ruin=('#383448', '#4e4862', '#242030'),
        shrine_wood=('#4c1c24', '#702a34', '#2e1016', '#963b48'),
        shrine_roof=('#32283c', '#4c3e5a', '#1e1624', '#6c5a7e'),
        bone=('#eee6d8', '#c8beb2', '#948a7e', '#ffffff'),
        ground_l=('#32141a', '#481c24', '#1e0b10', '#682832'),
        ground_r=('#1c2848', '#2c4070', '#121a30', '#4866a8'),
        sukuna=('#fcf6ea', '#d8ccb8', '#1c0c14', '#fb7ca0', '#e81e3f'),
        gojo=('#1e2638', '#364262', '#ffffff', '#dce6f4', '#22d3ee'),
        vig=0.88,
        nube=['#f4eef6', '#e6dce8', '#d8cce0', '#fbf8fc', '#e2d4dc', '#bfb4c8'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#f43f5e', '#a855f7'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#a855f7', base='#f5f3ff', sombra='#c4b5fd', crater='#9370db', crater_hi='#b49cf0'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#fda4af', centro='#fff8f0', borde='#fb7185', rayo='#fecdd3'),
)

# Cielo partido en x~312: Izquierda Sagrario Malevolente, Derecha Vacío Infinito cósmico
vc = PAL['void']
r_split = Ruido(42)
r_neb = Ruido(91)
for y in range(256):
    ridge = 308 + int(22 * math.sin(y * 0.032) + 14 * (fbm(r_split, y * 0.05) - 0.5))
    for x in range(max(0, ridge - 20), W):
        t_split = max(0.0, min(1.0, (x - ridge + 20) / 30.0))
        d_hor = min(1.0, y / 256.0)
        idx = min(len(vc) - 2, int((1.0 - d_hor) * (len(vc) - 3) + 0.5))
        c_v = mix(vc[idx], vc[idx + 1], (y % 18) / 18.0)
        neb = fbm(r_neb, x * 0.020 + y * 0.033)
        if neb > 0.56:
            c_v = mix(c_v, '#a855f7' if (x + y) % 4 else '#38bdf8', min(0.85, (neb - 0.56) * 1.4))
        if t_split >= 0.99 or dith(x, y, t_split):
            put(x, y, c_v)

render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#e0f2fe', '#e9d5ff', '#fbcfe8'])

MX, MY, MR = 310, 56, 34
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#a855f7', base='#f5f3ff', sombra='#c4b5fd', crater='#9370db', crater_hi='#b49cf0')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 310, 110, 22, halo='#fda4af', centro='#fff5f5', borde='#f43f5e', rayo='#fda4af')
    else:
        dibuja_sol_estandar(lz, 310, 64, 22, halo='#bae6fd', centro='#ffffff', borde='#7dd3fc', rayo='#bae6fd')

NUBES_DEF = [
    (74, 34, 88, PAL['nube'][0], 2),
    (204, 52, 92, PAL['nube'][2], 2),
    (438, 40, 82, PAL['nube'][3], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)


def dibuja_vacio_infinito_esfera(cx, cy):
    """Singularidad de Vacío Infinito en el cielo derecho (fuera del HUD)."""
    vc_p = PAL['void']
    for dy in range(-58, 59):
        for dx in range(-58, 59):
            r = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            if r < 16:
                put(cx + dx, cy + dy, '#03040c')
            elif r < 21:
                put(cx + dx, cy + dy, '#e0f2fe' if r < 18.5 else '#38bdf8')
            elif r < 56:
                wave = 0.5 + 0.5 * math.sin(r * 0.42 - ang * 3.0)
                fade = max(0.0, 1.0 - (r - 21) / 35.0)
                col = mix(vc_p[4], '#c084fc' if wave > 0.48 else '#38bdf8', fade * 0.85)
                if dith(cx + dx, cy + dy, fade * 0.78 + wave * 0.22):
                    over(cx + dx, cy + dy, col, min(0.90, fade * 0.92))
    # Disco de acreción inclinado y ondas neuronales de Vacío Infinito
    for t in range(-76, 77):
        ew = int(12 * math.sqrt(max(0.0, 1.0 - (t / 76.0) ** 2)))
        for s in range(-2, 3):
            yy = cy + int(s * 0.6 - t * 0.14 + (ew // 4) * (1 if s >= 0 else -1) * 0.18)
            over(cx + t, yy, '#e0f2fe' if abs(s) <= 1 else '#a855f7', 0.72)


def dibuja_skyline_shinjuku():
    """Rascacielos partidos de Shinjuku en y=130..258 (respetando zona HUD superior derecha)."""
    r0, r1, r2 = PAL['ruin']
    edificios = [
        (0, 34, 146), (222, 36, 174), (262, 38, 192), (304, 34, 178),
        (342, 36, 158), (528, 36, 208), (568, 34, 214), (606, 34, 218),
    ]
    for x0, bw, top_y in edificios:
        cut_slope = -0.32 if x0 < 312 else 0.28
        for x in range(x0, min(W, x0 + bw)):
            ty = int(top_y + (x - x0) * cut_slope)
            for y in range(ty, 260):
                is_edge = (x == x0 or x == x0 + bw - 1 or abs(y - ty) <= 1)
                is_floor = ((y - ty) % 10 == 0)
                col = r2 if is_edge else (r1 if is_floor else r0)
                put(x, y, col)
                if (x - x0) % 6 == 3 and (y - ty) > 6 and (y - ty) % 10 == 4 and ((x * 7 + y * 11) % 4 == 0):
                    wcol = '#fb7185' if x < 312 else '#60a5fa'
                    put(x, y, wcol)
                    put(x + 1, y, wcol)
                    if len(VENTANAS) < 36 and x % 2 == 0:
                        VENTANAS.append([x, y, 2])
    # Bloques flotando por la gravedad del Vacío Infinito
    for rx, ry, rw, rh in ((392, 128, 9, 6), (496, 186, 8, 6), (416, 202, 7, 5), (506, 224, 9, 5)):
        for dy in range(rh):
            for dx in range(rw):
                put(rx + dx, ry + dy, r1 if (dx == 0 or dy == 0) else r2)


def dibuja_sagrario_malevolente(cx, by):
    """Monumental Sagrario Malevolente (Fukuma Mizushi) ~160 px de altura apoyado en by=266."""
    wd0, wd1, wd2, wd3 = PAL['shrine_wood']
    rf0, rf1, rf2, rf3 = PAL['shrine_roof']
    bn0, bn1, bn2, bn3 = PAL['bone']

    # Basamento de piedra y peldaños (by-20 .. by)
    for dy in range(21):
        y = by - 20 + dy
        hw = 78 + int(dy * 0.75)
        for dx in range(-hw, hw + 1):
            put(cx + dx, y, wd2 if abs(dx) > hw - 3 else (wd0 if dy % 4 else wd1))
    for step in range(5):
        sy = by - 17 + step * 3
        sw = 22 + step * 4
        for dx in range(-sw, sw + 1):
            put(cx + dx, sy, wd3 if dx % 2 == 0 else wd1)
            put(cx + dx, sy + 1, wd2)

    # 4 pilares gruesos y boca demoníaca abismal en la cámara central (by-90 .. by-20)
    for px in (-60, -34, 34, 60):
        for y in range(by - 92, by - 20):
            for dx in range(-4, 5):
                put(cx + px + dx, y, wd3 if dx < -1 else (wd1 if dx <= 1 else wd2))
    # Cámara central oscura + fauces dentadas del Sagrario
    for y in range(by - 88, by - 20):
        for dx in range(-32, 33):
            col = '#060104'
            # Arcada de dientes superiores e inferiores en los bordes de la entrada
            if abs(dx) <= 26:
                tooth_x = abs(dx) % 7
                if y < by - 76 + (4 - abs(tooth_x - 3)):
                    col = bn0 if y < by - 79 else bn3
                elif y > by - 31 - (4 - abs(tooth_x - 3)):
                    col = bn1 if y > by - 28 else bn3
                elif y > by - 34 and abs(dx) < 14:
                    col = PAL['sukuna'][4]
            else:
                col = wd0
            put(cx + dx, y, col)

    # Doble tejado japonés curvo (irimoya) masivo con adornos carmesí
    for tier_y, hw_r, h_r in ((by - 92, 92, 22), (by - 126, 70, 24)):
        for x_off in range(-hw_r, hw_r + 1):
            u = abs(x_off) / float(hw_r)
            lift = int(12 * (u ** 2.3))
            y_bot = tier_y - lift
            y_top = tier_y - h_r + int(h_r * (u ** 1.32)) - lift // 2
            for y in range(y_top, y_bot + 1):
                if y == y_top or y == y_bot:
                    col = rf2
                elif (y - y_top) <= 3:
                    col = rf3
                elif (x_off % 6 == 0):
                    col = rf1
                else:
                    col = rf0
                put(cx + x_off, y, col)
            if abs(x_off) >= hw_r - 7:
                put(cx + x_off, y_top - 1, PAL['sukuna'][4])
                put(cx + x_off, y_top - 2, '#fca5a5' if abs(x_off) > hw_r - 3 else PAL['sukuna'][4])

    # Friso entre tejados + chapitel sorin
    for y in range(by - 126, by - 112):
        for dx in range(-34, 35):
            put(cx + dx, y, wd2 if abs(dx) > 30 else wd0)
    for y in range(by - 172, by - 146):
        w_sp = 1 if y < by - 158 else 2
        for dx in range(-w_sp, w_sp + 1):
            put(cx + dx, y, rf3 if (y % 4 == 0) else wd3)
    disc(cx, by - 173, 3, PAL['sukuna'][4])

    # Enorme Cráneo Demoníaco Cornudo en relieve en el centro superior (cy = by - 98)
    scy = by - 98
    for dy in range(-19, 21):
        for dx in range(-18, 19):
            nx, ny = dx / 17.5, dy / 18.0
            in_skull = (nx * nx + ny * ny <= 1.0) if dy < 6 else (abs(dx) <= 10 - (dy - 6) // 3)
            if in_skull:
                n = math.sqrt(max(0.05, 1.0 - min(0.95, nx * nx + ny * ny)))
                lum = (-nx * 0.42 - ny * 0.40 + n * 0.72)
                e1 = math.hypot(abs(dx) - 6.5, dy - 1) <= 3.1
                e2 = math.hypot(abs(dx) - 10.5, dy - 7) <= 2.3
                nose = (abs(dx) <= 2 and 4 <= dy <= 8)
                teeth = (dy >= 13 and abs(dx) <= 8 and dx % 3 != 0)
                if e1 or e2 or nose:
                    col = '#120308'
                elif teeth:
                    col = bn3 if dx % 2 == 0 else bn1
                elif lum > 0.56:
                    col = bn3
                elif lum > 0.30:
                    col = bn0
                elif lum > 0.08:
                    col = bn1
                else:
                    col = bn2
                put(cx + dx, scy + dy, col)
                if (e1 or e2) and abs(dy - (1 if e1 else 7)) <= 1:
                    put(cx + dx, scy + dy, PAL['sukuna'][4])
    # Cuernos curvos largos del cráneo
    for side in (-1, 1):
        for k in range(22):
            hx = cx + side * (14 + k)
            hy = scy - 6 - int(k * 0.95 - (k * k) * 0.022)
            thick = max(0, 3 - k // 6)
            for t in range(-thick, thick + 1):
                put(hx, hy + t, bn1 if t > 0 else (bn3 if t < 0 else bn0))

    # Cráneos apilados y braseros rituales junto al Sagrario
    for sx_b, sy_b, rr in ((-72, by - 4, 4), (-62, by - 7, 4), (-52, by - 3, 3), (52, by - 3, 3), (62, by - 7, 4), (72, by - 4, 4)):
        disc(cx + sx_b, sy_b, rr, bn1)
        disc(cx + sx_b - 1, sy_b - 1, max(1, rr - 1), bn3)
        put(cx + sx_b - 1, sy_b, '#120308')
        put(cx + sx_b + 1, sy_b, '#120308')
    for fx, fy in ((cx - 82, by - 26), (cx + 82, by - 26)):
        for dy in range(22):
            put(fx, fy + dy, wd2)
            put(fx + 1, fy + dy, wd1)
        if ANIM:
            FAROLES.append([fx, fy, 8])
        else:
            glow(fx, fy, 8, PAL['sukuna'][4], 0.58)
            disc(fx, fy, 2, '#ffe4e6')


def dibuja_terreno_dominios():
    """Suelo de choque de dominios (y=252..400): mar de sangre/cráneos vs abismo Vacío Infinito."""
    gl0, gl1, gl2, gl3 = PAL['ground_l']
    gr0, gr1, gr2, gr3 = PAL['ground_r']
    bn0, bn1, bn2, bn3 = PAL['bone']
    r_fl = Ruido(1107)

    for y in range(252, H):
        t_y = (y - 252) / float(H - 252)
        seam_x = 308 + int(16 * math.sin(y * 0.06) + 8 * (fbm(r_fl, y * 0.09) - 0.5))
        for x in range(W):
            n = fbm(r_fl, x * 0.028 + y * 0.04)
            is_seam = (abs(x - seam_x) < 10)
            if x < seam_x - 3 or (is_seam and dith(x, y, 0.5 - (x - seam_x) / 20.0)):
                # Mitad Sukuna: aguas someras carmesí + losas oscuras del santuario
                ripple = math.sin(x * 0.08 + y * 0.42) * 0.5 + 0.5
                tile = ((x // 24 + y // 14) % 2 == 0) and y < 358
                col = gl3 if (n > 0.62 and ripple > 0.65) else (gl1 if (tile or n > 0.45) else (gl0 if n > 0.25 else gl2))
                if abs(y - 256) <= 1 or abs(y - 344) <= 1 and n > 0.6:
                    col = gl3
                put(x, y, col)
            else:
                # Mitad Gojo: plano abismal estrellado + ondas de perspectiva infinita
                wave = math.sin(math.hypot(x - 398, (y - 332) * 2.1) * 0.26)
                grid_x = ((x - 398) % 26 == 0)
                grid_y = ((y - 252) % 16 == 0)
                if grid_x or grid_y:
                    col = mix(gr1, gr3, 0.45 * t_y)
                elif wave > 0.72 and n > 0.48:
                    col = gr3
                else:
                    col = gr1 if n > 0.50 else (gr0 if n > 0.28 else gr2)
                put(x, y, col)
            if abs(x - seam_x) <= 2 and (y % 4 != 0):
                over(x, y, '#c084fc' if y % 2 else '#f43f5e', 0.65)

    # Costillas vertebrales gigantes del dominio emergiendo a la izquierda (x=8..54)
    for idx_r, (bx_r, by_r, height_r, bend) in enumerate(((12, 398, 128, 34), (42, 392, 102, 26), (72, 384, 74, 18))):
        for k in range(height_r):
            u = k / float(height_r)
            rx = int(bx_r + bend * math.sin(u * math.pi * 0.65))
            ry = by_r - k
            thick = max(2, int(6 * (1.0 - 0.55 * u)))
            for dx in range(-thick, thick + 1):
                col = bn3 if dx < -thick // 2 else (bn0 if dx < thick // 2 else bn2)
                put(rx + dx, ry, col)

    # Cráneos esparcidos en el primer plano izquierdo sobre la orilla roja
    for sx, sy, sr in ((96, 366, 5), (124, 376, 6), (146, 364, 4), (176, 382, 5), (242, 378, 4)):
        disc(sx, sy, sr, bn1)
        disc(sx - 1, sy - 1, max(1, sr - 1), bn3)
        put(sx - 1, sy, '#100308')
        put(sx + 1, sy, '#100308')

    # Gran cráter de impacto entre Sukuna y Gojo (cx=306, cy=344)
    for dy in range(-20, 22):
        for dx in range(-92, 93):
            ell = math.hypot(dx / 92.0, dy / 20.0)
            if 0.72 <= ell <= 0.96 and dith(306 + dx, 344 + dy, 0.78):
                over(306 + dx, 344 + dy, '#e879f9' if dx > 0 else '#f43f5e', 0.42)
            elif ell < 0.72 and dith(306 + dx, 344 + dy, 0.35):
                over(306 + dx, 344 + dy, '#05020a', 0.48)


def dibuja_sukuna_hero(cx, by):
    """Ryomen Sukuna a escala heroica (48 filas x 36 cols) haciendo sello Enmaten."""
    w0, s0, dk, pk, cr = PAL['sukuna']
    spr = [
        '............PPPPPPPPPP..............',
        '..........PPPPPPPPPPPPPP............',
        '.........PPPPPPPPPPPPPPPP...........',
        '........PPPPPPPPPPPPPPPPPP..........',
        '........PPPKKKKKKKKKKKKPPP..........',
        '.......PPPKCCCCCCCCCCCCKPPP.........',
        '.......PPKCCKKCCCCCCKKCCKPP.........',
        '.......PPKCCTTCCCCCCCTTCCKP.........',
        '........KCCRRCCCCCCCCRRCCK..........',
        '........KCCRRCCCCCCCCRRCCK..........',
        '........KCCKKTTCCCCKKTTCCK..........',
        '.........KCCCCCCCCCCCCCCK...........',
        '.........KTTTCCCCCCCCCTTK...........',
        '..........KKCCCCCCCCCCKK............',
        '.........KKKCCCTTTCCCWKKK...........',
        '.......KKWWWWCCTTTCCWWWWKK..........',
        '......KWWWWWWCTTTTTCWWWWWWK.........',
        '.....KWWWWWWWWCKKKKCWWWWWWWWK.......',
        '....KWWWKWWWWWCTTTCWWWWWWKWWWK......',
        '....KWWWKWWWWWKKKKKWWWWWWKWWWK......',
        '...KWWWWKWWWWWCCCCWWWWWWWKWWWWK.....',
        '...KWWWWKWWWWCCCCCCWWWWWWKWWWWK.....',
        '..KWWWWWKKWWCCCCCCCCWWKKWWWWWWK.....',
        '..KWWWWWKWWWCCTTTTCCWWWKWWWWWWK.....',
        '..KWWWWWKWWWCCCCCCCCWWWKWWWWWWK.....',
        '..KWWSSWKWWWKCCCCCCKWWWKWWSSWWK.....',
        '...KKWWWKWWWKKKKKKKKWWWKWWWKK.......',
        '....KKKKKWWWDDDDDDDDWWWKWWWW........',
        '......KKWWWWDDDDDDDDWWWWKK..........',
        '.....KWWWWWWDDDDDDDDWWWWWWK.........',
        '.....KWWWWWDDDDDDDDDDWWWWWK.........',
        '....KWWWWWWDDDDDDDDDDWWWWWWK........',
        '....KWWWWWDDDDDDDDDDDDWWWWWK........',
        '...KWWWWWWDDDDDDDDDDDDWWWWWWK.......',
        '...KWWWWSSDDDDDDDDDDDDSSWWWWK.......',
        '..KWWWWWSSDDDDDDDDDDDDSSWWWWWK......',
        '..KWWSSSSSDDDDD..DDDDDSSSSSWWK......',
        '..KKKKKK..DDDDD..DDDDD..KKKKKK......',
        '..........DDDDD..DDDDD..............',
        '.........DDDDDD..DDDDDD.............',
        '.........DDDDDD..DDDDDD.............',
        '.........DDDDD....DDDDD.............',
        '........DDDDDD....DDDDDD............',
        '........DDDDDD....DDDDDD............',
        '........DDDDD......DDDDD............',
        '........KKKKK......KKKKK............',
        '.......KKKKKK......KKKKKK...........',
        '.......KKKKKK......KKKKKK...........',
    ]
    cmap = {'P': pk, 'C': '#f4d2c4', 'K': dk, 'T': '#1b0f18', 'W': w0, 'S': s0, 'D': '#16111c', 'R': cr}
    if not ANIM:
        glow(cx, by - 26, 26, cr, 0.36)
    pinta_sprite(lz, cx, by, spr, cmap)
    # Tajos luminosos Clivar y Desmantelar rodeando a Sukuna
    for sx0, sy0, dx_s, dy_s in ((cx - 44, by - 46, 24, -8), (cx - 38, by - 18, 22, -6), (cx + 26, by - 42, 24, 6)):
        for k in range(20):
            u = k / 19.0
            px = int(sx0 + dx_s * u)
            py = int(sy0 + dy_s * u)
            put(px, py, '#fff1f2' if 0.25 < u < 0.75 else cr)
            over(px, py - 1, cr, 0.65)
            over(px, py + 1, cr, 0.65)
    if ANIM:
        RUNAS.append([cx + 16, by - 26])
    else:
        glow(cx + 20, by - 28, 10, cr, 0.62)


def dibuja_gojo_hero(cx, by):
    """Satoru Gojo a escala heroica (48 filas x 36 cols) cargando Azul + Rojo -> Púrpura Vacío."""
    b0, b1, h0, h1, ey = PAL['gojo']
    spr = [
        '............HHHHHHHHHHHH............',
        '..........HHHHHHHHHHHHHHHH..........',
        '........HHHHHHHHHHHHHHHHHHHH........',
        '.......HHHHHHHHH111HHHHHHHHHH.......',
        '......HHHHHHH11HHHHHH11HHHHHHH......',
        '.......HHHHHHCCCCCCCCCCCHHHHH.......',
        '........HHHHCCCCCCCCCCCCCHHH........',
        '........HHHCCKKECCKKEECCCHHH........',
        '.........HHCCEEEECCEEECCHH..........',
        '.........HHCCCCCCCCCCCCCHH..........',
        '..........KCCCCCCCCCCCCCK...........',
        '...........KKCCCCCCCCCKK............',
        '...........KKKBBBBBBBKKK............',
        '..........KKBBBBBBBBBBBKK...........',
        '....RRR..KKBBBBGGGGGBBBBKK..AAA.....',
        '...RRRRR.KBBBBBBBBBBBBBBBK.AAAAA....',
        '..RRRRRRKBBBBBBBBBBBBBBBBBKAAAAAA...',
        '...RRRRR.KBBBBBB111BBBBBBK.AAAAA....',
        '....RRR..KBBBBBB111BBBBBBK..AAA.....',
        '.........KBBBBBBBBBBBBBBBK..........',
        '.........KBBBBBB111BBBBBBK..........',
        '.........KBBBBBBBBBBBBBBBK..........',
        '........KBBBBBBBBBBBBBBBBBK.........',
        '........KBBBBBBB111BBBBBBBK.........',
        '........KBBBBBBBBBBBBBBBBBK.........',
        '.......KBBBBBBBBBBBBBBBBBBBK........',
        '.......KBBBBBBBB111BBBBBBBBK........',
        '.......KBBBBBBBBBBBBBBBBBBBK........',
        '.......KBBBBBBBBBBBBBBBBBBBK........',
        '........KBBBBBBB..BBBBBBBBK.........',
        '........BBBBBBBB..BBBBBBBB..........',
        '........BBBBBBBB..BBBBBBBB..........',
        '........BBBBBBBB..BBBBBBBB..........',
        '........BBBBBBB....BBBBBBB..........',
        '........BBBBBBB....BBBBBBB..........',
        '.......BBBBBBB......BBBBBBB.........',
        '.......BBBBBBB......BBBBBBB.........',
        '.......BBBBBBB......BBBBBBB.........',
        '.......BBBBBB........BBBBBB.........',
        '......BBBBBBB........BBBBBBB........',
        '......BBBBBB..........BBBBBB........',
        '......BBBBBB..........BBBBBB........',
        '......BBBBBB..........BBBBBB........',
        '.....BBBBBB............BBBBBB.......',
        '.....KKKKKK............KKKKKK.......',
        '.....KKKKKK............KKKKKK.......',
        '....KKKKKKK............KKKKKKK......',
        '....KKKKKKK............KKKKKKK......',
    ]
    cmap = {
        'H': h0, '1': h1, 'C': '#f6d8cc', 'E': ey, 'K': '#090b14',
        'B': b0, 'G': '#d4af37', 'R': '#f43f5e', 'A': '#38bdf8',
    }
    if not ANIM:
        glow(cx, by - 26, 26, ey, 0.34)
    pinta_sprite(lz, cx, by, spr, cmap)
    # Esferas Rojo (mano izq) y Azul (mano der) orbitando hacia el Púrpura Vacío central
    disc(cx - 15, by - 32, 4, '#f43f5e')
    disc(cx - 15, by - 32, 2, '#ffe4e6')
    disc(cx + 15, by - 32, 4, '#38bdf8')
    disc(cx + 15, by - 32, 2, '#e0f2fe')
    if ANIM:
        RUNAS.append([cx - 15, by - 32])
        RUNAS.append([cx + 15, by - 32])
    else:
        glow(cx - 15, by - 32, 9, '#f43f5e', 0.60)
        glow(cx + 15, by - 32, 9, '#38bdf8', 0.60)


dibuja_vacio_infinito_esfera(446, 146)
dibuja_skyline_shinjuku()
dibuja_sagrario_malevolente(132, 266)
dibuja_terreno_dominios()
dibuja_sukuna_hero(214, 348)
dibuja_gojo_hero(398, 348)

# Colosal Púrpura Vacío (Hollow Purple) convergiendo entre Sukuna y Gojo (cx=306, cy=298)
if not ANIM:
    glow(306, 298, 42, '#7e22ce', 0.68)
    glow(306, 298, 24, '#e879f9', 0.85)
    disc(306, 298, 10, '#f5d0fe')
    disc(306, 298, 6, '#ffffff')
    # Orbitals Azul y Rojo chocando en los costados de Púrpura
    glow(274, 304, 10, '#f43f5e', 0.72)
    disc(274, 304, 4, '#ffe4e6')
    glow(338, 292, 10, '#38bdf8', 0.72)
    disc(338, 292, 4, '#e0f2fe')
else:
    FAROLES.append([306, 298, 16])
    RUNAS.append([306, 298])

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
