#!/usr/bin/env python3
"""PixelZen Worlds - Naruto Shippuden (Bloqueo): Valle del Fin, Estatuas de Hashirama y Madara, Rasengan vs Chidori."""
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
random.seed(933)

PALETAS = {
    'noche': dict(
        sky=['#040814', '#081024', '#0e1a36', '#16264a', '#1e345e', '#284672', '#345a88', '#46709c', '#5e88b0', '#7aa2c4'],
        cliff=('#1a2030', '#2a3248', '#0e121c', '#3c4862'),
        statue=('#2f384e', '#485572', '#171d2c', '#6c7e9e'),
        water_f=('#1d5284', '#3886bf', '#98dcff'),
        agua='#09182e',
        olas=('#6cb8f0', '#3e72a8', '#224270'),
        reflejo=('#b8e6ff', '#62a4dc'),
        rasen=('#2894ff', '#78dcff', '#ffffff'),
        chido=('#5468ff', '#a890ff', '#ffffff'),
        vig=0.72,
        nube=['#1c2d48', '#294060', '#38547a', '#4c6c92', '#6284a8', '#15233a'],
    ),
    'dorado': dict(
        sky=['#141028', '#261a3c', '#40264e', '#62385a', '#8a4c5a', '#b46450', '#d88248', '#f0a450', '#ffc668', '#ffe498'],
        cliff=('#2e2838', '#463c52', '#1a1622', '#685876'),
        statue=('#484052', '#695d76', '#241e2c', '#9888a6'),
        water_f=('#295884', '#528ec0', '#b8e8ff'),
        agua='#1a243e',
        olas=('#b4dcfa', '#6e8cb8', '#3c4c78'),
        reflejo=('#ffe498', '#86c0ec'),
        rasen=('#34a2ff', '#86e2ff', '#ffffff'),
        chido=('#6678ff', '#b69cff', '#ffffff'),
        vig=0.80,
        nube=['#4e2e4c', '#6e4058', '#965460', '#be7060', '#e09266', '#3a2238'],
    ),
    'dia': dict(
        sky=['#1e5298', '#2e68b0', '#4280c6', '#5c9ad8', '#7ab4e6', '#98ccee', '#b6e0f6', '#d2eefb', '#e6f5fc', '#f4f8ef'],
        cliff=('#3c4c60', '#54687e', '#24303e', '#72889e'),
        statue=('#5c687a', '#8090a4', '#36404e', '#b2c2d4'),
        water_f=('#2c6ea4', '#56a6dc', '#c6f0ff'),
        agua='#245c90',
        olas=('#c8ecff', '#84c6f0', '#4e8cc4'),
        reflejo=('#fff0be', '#9ee0fc'),
        rasen=('#2494ff', '#78dcff', '#ffffff'),
        chido=('#586eff', '#ab94ff', '#ffffff'),
        vig=0.88,
        nube=['#ffffff', '#eef6fc', '#dff0fa', '#f8fcff', '#e4f2fb', '#cae2f2'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#54b8ff', '#a878ff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#b8e4ff', base='#f4fbff', sombra='#c4d4e4', crater='#9cb0c4', crater_hi='#b4c6d8'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe49c', centro='#fffef2', borde='#ffc45c', rayo='#ffe298'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#d8f0ff', '#b8d8ff', '#a8b8e8'])

MX, MY, MR = 284, 54, 36
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#b8e4ff', base='#f4fbff', sombra='#c4d4e4', crater='#9cb0c4', crater_hi='#b4c6d8')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 284, 136, 22, halo='#ffaa70', centro='#fff0dc', borde='#ff6c48', rayo='#ff8c60')
    else:
        dibuja_sol_estandar(lz, 284, 62, 22, halo='#ffe49c', centro='#fffef2', borde='#ffc45c', rayo='#ffe298')

NUBES_DEF = [
    (68, 22, 146, PAL['nube'][0], 2),
    (244, 28, 152, PAL['nube'][1], 2),
    (438, 20, 142, PAL['nube'][2], 2),
    (160, 88, 148, PAL['nube'][3], 2),
    (496, 102, 118, PAL['nube'][4], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

CL0, CL1, CL2, CL3 = PAL['cliff']
CL_WET = mix(CL2, '#081220', 0.36)
ST0, ST1, ST2, ST3 = PAL['statue']
ST_DEEP = mix(ST2, '#070910', 0.50)
ST_MIDHI = mix(ST1, ST3, 0.48)
WF0, WF1, WF2 = PAL['water_f']


def _smoothstep(edge0, edge1, val):
    t = max(0.0, min(1.0, (val - edge0) / max(1e-6, edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def _seg_dist(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    denom = vx * vx + vy * vy
    t = 0.0 if denom < 1e-6 else max(0.0, min(1.0, (wx * vx + wy * vy) / denom))
    dx, dy = px - (ax + t * vx), py - (ay + t * vy)
    return math.sqrt(dx * dx + dy * dy)


# 1. Cañón del Valle del Fin sin rayas verticales cebra + labio escalonado natural en la cascada
rx_c = Ruido(937)
ry_c = Ruido(941)
r_lf = Ruido(959)
for x in range(W):
    if 244 <= x <= 324:
        # Borde suavemente arqueado en vez de corte rectangular rígido
        edge_t = abs(x - 284) / 40.0
        ridge = int(149 + 5 * (edge_t ** 2) + 3 * math.sin(x * 0.16))
    elif 234 <= x < 244:
        t_lip = (x - 234) / 10.0
        ridge_base = int(124 + 12 * fbm(rx_c, x * 0.02))
        ridge = int(ridge_base + (152 - ridge_base) * (t_lip ** 1.5))
    elif 324 < x <= 334:
        t_lip = (334 - x) / 10.0
        ridge_base = int(126 + 12 * fbm(rx_c, x * 0.02))
        ridge = int(ridge_base + (152 - ridge_base) * (t_lip ** 1.5))
    elif x < 234:
        ridge = int(124 + 12 * fbm(rx_c, x * 0.02))
    elif x < 455:
        ridge = int(126 + 12 * fbm(rx_c, x * 0.02))
    else:
        ramp = min(1.0, (x - 455) / 85.0)
        ridge = int(132 + 95 * (0.5 - 0.5 * math.cos(math.pi * ramp)) + 10 * fbm(rx_c, x * 0.02))
    ridge = min(244, ridge)

    for y in range(ridge, HOR + 1):
        if 244 <= x <= 324:
            # Cortina vertical de cascada con textura fina y espuma suave en labio superior/inferior
            nx_w = math.sin(x * 0.68 + y * 0.05) + math.cos(x * 1.28 + y * 0.08)
            is_crest = y < ridge + 5 or y > HOR - 8 or x in (244, 245, 323, 324)
            if is_crest:
                c = WF2 if (x + y) % 2 == 0 else WF1
            elif nx_w > 0.95 and (x + y * 2) % 5 == 0:
                c = WF2
            elif nx_w > 0.0:
                c = WF1
            else:
                c = WF0
            put(x, y, c)
        else:
            wx = fbm(rx_c, x * 0.024 + 1.1 * fbm(r_lf, y * 0.032))
            wy = fbm(ry_c, y * 0.056 + 0.9 * fbm(rx_c, x * 0.019 + 5.7))
            n_r = 0.52 * wx + 0.48 * wy + 0.07 * math.sin(y * 0.18 + 2.8 * wx)
            near_falls = (240 <= x < 244) or (324 < x <= 328)
            if y < ridge + 5:
                c = CL3
            elif near_falls and n_r < 0.42:
                c = CL_WET if n_r < 0.30 else CL2
            elif n_r > 0.68:
                c = CL3 if dith(x, y, 0.5) else CL1
            elif n_r > 0.46:
                c = CL1
            elif n_r > 0.27:
                c = CL0
            else:
                c = CL2
            put(x, y, c)

# Peñascos húmedos integrados en el borde del salto superior y niebla en la base (y=268..280)
for rx_b, ry_b, rad_b in ((242, 151, 3), (326, 151, 3)):
    for dy in range(-rad_b, rad_b + 1):
        for dx in range(-rad_b, rad_b + 1):
            if dx * dx + dy * dy <= rad_b * rad_b:
                put(rx_b + dx, ry_b + dy, CL1 if dy < 0 else CL2)
for fx in range(230, 339, 2):
    fy = HOR - 2 - int(4 * abs(math.sin(fx * 0.16)))
    over(fx, fy, WF2, 0.76)
    over(fx + 1, fy - 2, WF1, 0.52)


# 2. COLOSALES ESTATUAS DE HASHIRAMA SENJU (cx=154, ->) Y MADARA UCHIHA (cx=414, <-) ESCULPIDAS EN 3D
def dibuja_estatua_monumental(cx, side):
    """Esculpe la estatua completa con armadura Sengoku, Sello de Confrontación y perfil 3/4 icónico en piedra."""
    is_madara = (side < 0)
    # Caja local desde y=96 (corona/puntas) hasta y=HOR (280): width=164 (dx en [-82, +81]), height=186
    pw, ph = 164, 188
    ox = cx - pw // 2
    oy = HOR - ph + 1
    z_buf = [[0.0] * pw for _ in range(ph)]
    kind_buf = [['none'] * pw for _ in range(ph)]
    grv_buf = [[0.0] * pw for _ in range(ph)]

    for py in range(ph):
        gy = oy + py
        v = gy - (HOR - 144)  # v ~ 0 en el cuello/hombro superior, v=-30 cima cabeza, v=+144 base
        for px in range(pw):
            dx = (ox + px) - cx
            u_f = dx * side  # >0 hacia el centro de la cascada, <0 hacia la espalda

            z_val = 0.0
            k = 'none'
            g_val = 0.0

            # A. Pedestal rocoso monumental (v = +110..+144, gy = 246..280)
            if v >= 110:
                hw_p = 30.0 + (v - 110) * 0.34
                if abs(u_f) <= hw_p:
                    t_x = u_f / hw_p
                    step_v = ((v - 110) // 10) * 0.15
                    z_val = 2.6 * math.sqrt(max(0.0, 1.0 - t_x * t_x * 0.75)) + step_v
                    k = 'plinth'
                    if (v - 110) % 10 == 0:
                        g_val = max(g_val, 0.45)

            # B. Túnica inferior / faldas de armadura kusazuri y hakama (v = +44..+112)
            if 44 <= v <= 112:
                u_t = (v - 44) / 68.0
                hw_l = 22.0 + 7.5 * _smoothstep(0.0, 1.0, u_t)
                if abs(u_f) <= hw_l:
                    nx_l = u_f / hw_l
                    # Pliegues verticales esculpidos en piedra + faldón laminado lateral
                    fold = 0.45 * math.cos(u_f * 0.45)
                    z_skirt = 2.4 * math.sqrt(max(0.0, 1.0 - nx_l * nx_l * 0.78)) + fold
                    if z_skirt > z_val:
                        z_val = z_skirt
                        k = 'robe'
                    if v in (46, 52, 68, 88) and abs(u_f) > 8:
                        g_val = max(g_val, 0.42)

            # C. Peto Sengoku, faja y amplios hombros sode (v = -4..+48)
            if -4 <= v <= 48:
                u_c = (v + 4) / 52.0
                hw_c = 25.5 - 3.5 * u_c + 4.5 * math.sin(u_c * math.pi)
                if abs(u_f) <= hw_c:
                    nx_c = u_f / hw_c
                    z_tor = 2.7 * math.sqrt(max(0.0, 1.0 - nx_c * nx_c * 0.72))
                    # Hombreras cuadradas Sengoku (sode) en los laterales
                    if 0 <= v <= 30 and abs(u_f) > hw_c - 10.5:
                        z_tor += 0.55
                        if v % 7 == 0:
                            g_val = max(g_val, 0.52)
                    # Solapa cruzada del manto y placas pectorales
                    if 2 <= v <= 44 and abs(u_f) <= 13:
                        if abs(u_f - (v - 20) * 0.38) <= 1.1:
                            g_val = max(g_val, 0.58)
                        elif v in (38, 42):
                            g_val = max(g_val, 0.55)
                    # Cuello alto alzado de Madara vs escote armadura Hashirama
                    if is_madara and -8 <= v <= 8 and (-13 <= u_f <= 8):
                        z_tor += 0.65
                    if z_tor > z_val:
                        z_val = z_tor
                        k = 'armor'

            # D. Brazo esculpido con manga y Sello de Confrontación (2 dedos erguidos hacia el centro)
            d_arm = _seg_dist(u_f, v, 10.0, 14.0, 56.0, 22.0)
            w_arm = 7.5 - max(0.0, (u_f - 18.0) / 40.0) * 2.4
            if d_arm <= w_arm and 10.0 <= u_f <= 59.0:
                z_arm = 2.95 * math.sqrt(max(0.0, 1.0 - (d_arm / w_arm) ** 2))
                if 28 <= u_f <= 48 and abs(v - 18) < 4:
                    # Pliegues horizontales suaves de la manga hacia el puño
                    z_arm += 0.16 * math.sin(u_f * 0.5)
                if z_arm >= z_val - 0.1:
                    z_val = max(z_val, z_arm)
                    k = 'armor'
            # Puño + dedos índice y corazón erguidos en vertical
            if 55.0 <= u_f <= 64.0 and 12.0 <= v <= 26.0:
                z_val = max(z_val, 3.1)
                k = 'armor'
            if 57.5 <= u_f <= 62.5 and -4.0 <= v <= 13.0:
                z_val = max(z_val, 3.0)
                k = 'armor'
                if abs(u_f - 60.0) <= 0.6 and v < 9.5:
                    g_val = max(g_val, 0.85)  # División limpia entre dedos

            # E. Manto dorsal y MELENA ICÓNICA (Hashirama liso en cascada vs Madara puntas salvajes)
            if is_madara:
                if -22 <= v <= 26 and -18 <= u_f <= -3:
                    z_val = max(z_val, 2.55)
                    k = 'hair'
                madara_spikes = [
                    (-4, -22, -26, -30, 6.4),
                    (-6, -16, -32, -16, 6.8),
                    (-8, -9, -35, -2, 7.2),
                    (-8, -2, -33, 12, 6.8),
                    (-7, 6, -28, 25, 6.2),
                    (-6, 15, -22, 34, 5.6),
                    (2, -24, -14, -36, 5.8),
                ]
                for ax, ay, bx, by, ws in madara_spikes:
                    ds = _seg_dist(u_f, v, ax, ay, bx, by)
                    rad = ws * (1.0 - _smoothstep(0, 26, math.hypot(u_f - ax, v - ay)) * 0.72)
                    if ds <= rad:
                        zh = 2.65 - ds * 0.13
                        if zh > z_val - 0.1:
                            z_val = max(z_val, zh)
                            k = 'hair'
            else:
                # Hashirama: larga melena recta cayendo por detrás hasta media espalda
                if -26 <= v <= 36 and -24 <= u_f <= -3:
                    t_back = max(0.0, (v + 26) / 62.0)
                    u_back_lim = -21.0 + 3.0 * t_back
                    if u_f >= u_back_lim and u_f <= -2:
                        zh = 2.55 + 0.18 * math.cos(u_f * 0.7)
                        if v >= 24:
                            zh *= max(0.0, 1.0 - (v - 24) / 13.0)
                        if zh > z_val - 0.1:
                            z_val = max(z_val, zh)
                            k = 'hair'

            # F. Cabeza y Rostro en 3/4 mirando hacia la cascada (v = -32..0, u_f = -10..+16)
            # Cráneo y mandíbula en 3/4
            vc = v + 14  # centro del rostro en v = -14 -> vc en [-18, +14]
            r_cr = ((u_f - 1.5) / 12.2) ** 2 + ((vc + 3.0) / 14.5) ** 2
            jaw_edge = 12.6 - max(0, vc) * 0.26
            in_face_34 = (r_cr <= 1.0) or (-2 <= vc <= 13 and -10 <= u_f <= jaw_edge)
            if in_face_34 and -18 <= vc <= 14:
                zf = 3.15 * math.sqrt(max(0.0, 1.0 - min(0.95, r_cr * 0.72)))
                # Protector frontal grabado encima de las cejas
                if -11 <= vc <= -6 and u_f >= -7:
                    zf += 0.35
                # Arco superciliar firme proyectando sobre el ojo hacia el centro
                if -5.5 <= vc <= -2.5 and 3.0 <= u_f <= 12.5:
                    zf += 0.45
                # Cuenca ocular + ojo tallado
                if ((u_f - 8.2) / 2.6) ** 2 + ((vc + 1.0) / 1.8) ** 2 <= 1.0:
                    zf -= 0.55
                    if abs(vc + 1.2) <= 0.65 and 6.8 <= u_f <= 9.8:
                        g_val = max(g_val, 0.80)
                # Perfil sobresaliente de nariz recta hacia la cascada (u_f = +9..+14.5, vc = -2..+4)
                if -2 <= vc <= 4.5 and 8.0 <= u_f <= 14.2:
                    t_n = (vc + 2.0) / 6.5
                    nose_reach = 11.2 + 3.0 * t_n
                    if u_f <= nose_reach:
                        zf += 0.95 * (1.0 - max(0.0, nose_reach - u_f) / 6.5)
                if 4.5 <= vc <= 5.8 and 9.0 <= u_f <= 13.0:
                    zf -= 0.45  # Sombra bajo la punta nasal
                # Labios y mentón firme
                if abs(vc - 8.2) <= 0.60 and 6.5 <= u_f <= 11.8:
                    g_val = max(g_val, 0.75)
                if 9.0 <= vc <= 12.5 and 6.0 <= u_f <= 11.5:
                    zf += 0.30
                # Flequillo delantero sobre la sien para ambos
                if (-18 <= vc <= -10 and u_f <= 11.0) or (-14 <= vc <= 4 and -12 <= u_f <= 3.5):
                    zf = max(zf, 3.05)
                    k_f = 'hair'
                else:
                    k_f = 'face'
                if zf >= z_val - 0.15:
                    z_val = zf
                    k = k_f

            z_buf[py][px] = z_val
            kind_buf[py][px] = k
            grv_buf[py][px] = g_val

    # Pasada de render direccional (luz superior-izquierda -> sombra derecha-abajo)
    c_hair = mix(ST0, ST2, 0.30)
    c_robe = mix(ST0, ST1, 0.25)
    for py in range(1, ph - 1):
        gy = oy + py
        if not (0 <= gy <= HOR):
            continue
        for px in range(1, pw - 1):
            k = kind_buf[py][px]
            if k == 'none':
                continue
            gx = ox + px
            if not (0 <= gx < W):
                continue
            dzx = z_buf[py][px + 1] - z_buf[py][px - 1]
            dzy = z_buf[py + 1][px] - z_buf[py - 1][px]
            lit = max(0.0, min(1.0, 0.50 - dzx * 0.52 - dzy * 0.65))

            if k == 'hair':
                col = mix(ST2, c_hair, lit * 0.85)
                if lit > 0.68:
                    col = mix(col, ST1, 0.45)
            elif k == 'face':
                col = mix(ST2, ST1, 0.28 + lit * 0.64)
                if lit > 0.78 and grv_buf[py][px] == 0.0:
                    col = mix(col, ST3, (lit - 0.78) / 0.22 * 0.55)
            elif k == 'plinth':
                col = mix(ST_DEEP, ST0, 0.30 + lit * 0.62)
                if gy > HOR - 14:
                    col = mix(col, WF0, 0.22)
            else:  # 'armor' / 'robe'
                col = mix(ST2, c_robe, 0.20 + lit * 0.72)
                if lit > 0.72:
                    col = mix(col, ST_MIDHI, (lit - 0.72) / 0.28 * 0.75)

            if grv_buf[py][px] > 0.0:
                col = mix(col, ST_DEEP, min(0.84, grv_buf[py][px] * 0.78))
            put(gx, gy, col)


dibuja_estatua_monumental(154, +1)  # Hashirama Senju
dibuja_estatua_monumental(414, -1)  # Madara Uchiha

# 3. CHOQUE FINAL: NARUTO (Rasengan) vs SASUKE (Chidori) saltando frente a frente (cx=284, cy=248)
RS0, RS1, RS2 = PAL['rasen']
CH0, CH1, CH2 = PAL['chido']

# Contraste sutil sobre la espuma de la cascada para destacar el choque aéreo
if not ANIM:
    glow(284, 248, 30, '#0c2648', 0.48)
    glow(274, 248, 18, RS0, 0.58)
    glow(294, 248, 18, CH0, 0.58)
    glow(284, 248, 12, '#ffffff', 0.78)
else:
    FAROLES.append([284, 248, 16])
    RUNAS.append([284, 248])

# Naruto Uzumaki Shippuden lanzándose desde la izquierda (cx=254, by=268, 19 filas x 26 cols)
nar_valle = [
    '.......KYYYYYYK...........',
    '......KYYYYYYYYK..........',
    '..KKKKYHHHHHHHHYK.........',
    '.KKK..YHHDDDDHHYK.........',
    '......KSSSSSSSK...........',
    '.....KKSSSESSSK...........',
    '.....KOODDDDDOOK..........',
    '....KOOODDDDDOOOSSSS......',
    '...KOOOODDDDDDOOOSSs......',
    '...KOOOOOOOOOODK..........',
    '..KOOODDDDDDDDDK..........',
    '..KOOODDDDDDDDK...........',
    '..KOO..KKKKKKK............',
    '..KO...KDDK.KDDK..........',
    '......KDDK...KDDK.........',
    '.....KDDK.....KDDK........',
    '....KDDK.......KDDK.......',
    '...KOOK.........KOOK......',
    '..KKKK...........KKKK.....',
]
pinta_sprite(lz, 254, 268, nar_valle, {
    'K': '#14141c', 'Y': '#ffd438', 'H': '#243a68', 'D': '#1c1d28',
    'S': '#f2c6a4', 's': '#d8a484', 'E': '#ff8818', 'O': '#ef6420',
})

# Sasuke Uchiha Shippuden lanzándose desde la derecha (cx=314, by=268, 19 filas x 26 cols)
sas_valle = [
    '...........KSSSSK.........',
    '..........KKKKKKKK........',
    '.........KKKKKKKKKK.KKK...',
    '.........KKSSSSSSKKKKKK...',
    '.........KSSSESSSKKKK.....',
    '.........KCCCCCCCK........',
    '....SSSSCCCCCCCCCCK.......',
    '....sSSCCPPPPPPPCCCK......',
    '........KPPPPPPPK.........',
    '........KPPPPPPPKKK.......',
    '........KDDDDDDDDKK.......',
    '........KDDDDDDDK.........',
    '.......KDDK..KDDK.........',
    '......KDDK....KDDK........',
    '.....KDDK......KDDK.......',
    '....KDDK........KDDK......',
    '...KDDK..........KDDK.....',
    '..KKKK............KKKK....',
    '..KKKK............KKKK....',
]
pinta_sprite(lz, 314, 268, sas_valle, {
    'K': '#141622', 'S': '#eed4c2', 's': '#cfa898', 'E': '#e82438',
    'C': '#eae8f0', 'P': '#724eb2', 'D': '#20263c',
})

# Esfera Rasengan & Chidori + relámpagos chocando en (284, 248)
disc(277, 248, 6, RS0)
disc(277, 248, 3, RS1)
disc(291, 248, 6, CH0)
disc(291, 248, 3, CH1)
disc(284, 248, 4, '#ffffff')
for lx, ly in ((298, 240), (301, 245), (296, 256), (271, 241), (269, 253)):
    put(lx, ly, CH1 if lx > 284 else RS1)
    put(lx + 1, ly + 1, '#ffffff')

# 4. Lago del Valle del Fin reflejando estatuas, cascada y el choque Rasengan-Chidori
render_lago(lz, PAL['agua'], PAL['olas'], DESTELLOS, ANIM, mx=MX, hor=HOR, reflejo_cols=PAL['reflejo'], reflejo_astro=True)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
