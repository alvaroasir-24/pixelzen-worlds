#!/usr/bin/env python3
"""PixelZen Worlds - Naruto Shippuden (Monitor 2): Monte Hokage, Konoha y Puesto de Ramen Ichiraku."""
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
random.seed(921)

PALETAS = {
    'noche': dict(
        sky=['#050a18', '#091428', '#10203a', '#192e4e', '#243f62', '#325278', '#44688e', '#5880a4', '#7098b8', '#8ab0ca'],
        cliff=('#282a38', '#3c3f52', '#171824', '#565a70'),
        tree=('#0d1c16', '#162d22', '#07110e', '#224030'),
        roof=('#5e1c24', '#822832', '#3a1016', '#b83c38'),
        wall=('#66626a', '#48454e', '#88828a'),
        wood=('#3c281e', '#261812', '#563a2c'),
        agua='#0c1a30',
        olas=('#7498c8', '#486898', '#2c446c'),
        reflejo=('#ffd48c', '#7498c8'),
        lit='#ffba4c',
        vig=0.76,
        nube=['#1d314d', '#2b4464', '#39577c', '#4c6d92', '#6084a8', '#172840'],
    ),
    'dorado': dict(
        sky=['#18122c', '#2a1c3e', '#44284e', '#663858', '#8e4c56', '#b6644c', '#da8246', '#f2a24c', '#ffc662', '#ffe492'],
        cliff=('#58403c', '#7c5a50', '#332222', '#a87c6a'),
        tree=('#1a2818', '#2a3c22', '#0e180e', '#3c542e'),
        roof=('#7e2426', '#a83432', '#4c1418', '#d24c3e'),
        wall=('#9a887a', '#72645a', '#bea896'),
        wood=('#583828', '#3a2218', '#744c38'),
        agua='#24283e',
        olas=('#ffb478', '#a86c68', '#5e4664'),
        reflejo=('#ffe49c', '#ff9868'),
        lit='#ffc85c',
        vig=0.84,
        nube=['#58324c', '#7a4458', '#a0585c', '#c6745c', '#e69864', '#44243c'],
    ),
    'dia': dict(
        sky=['#1e5296', '#2e68ae', '#4280c4', '#5c9ad8', '#7ab4e6', '#98ccee', '#b6e0f6', '#d2eefb', '#e6f5fc', '#f4f8ef'],
        cliff=('#866c5a', '#ab8d76', '#564236', '#cfaea0'),
        tree=('#1e4a28', '#2e6a36', '#102e18', '#428848'),
        roof=('#9c2c2c', '#c83e3a', '#641a1c', '#e4584c'),
        wall=('#ded4c8', '#b4aa9e', '#f2ece2'),
        wood=('#744c36', '#523222', '#946448'),
        agua='#28588a',
        olas=('#bce6fc', '#7cb8e4', '#4e84ba'),
        reflejo=('#fff0b4', '#98d2f4'),
        lit='#ffce66',
        vig=0.90,
        nube=['#ffffff', '#eef6fc', '#dff0fa', '#f8fcff', '#e4f2fb', '#cae2f2'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = [66, 240]
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#ffb048', '#58c4ff'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 36, halo='#ffe2a8', base='#fffbf2', sombra='#d6d2c8', crater='#b6b0a6', crater_hi='#cac4ba'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffe49c', centro='#fffef2', borde='#ffc45c', rayo='#ffe298'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#fff4d8', '#d2ecff', '#c0c8ea'])

MX, MY, MR = 382, 58, 34
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#ffe2a8', base='#fffbf2', sombra='#d6d2c8', crater='#b6b0a6', crater_hi='#cac4ba')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 396, 146, 22, halo='#ffaa70', centro='#fff0dc', borde='#ff6c48', rayo='#ff8c60')
    else:
        dibuja_sol_estandar(lz, 344, 68, 22, halo='#ffe49c', centro='#fffef2', borde='#ffc45c', rayo='#ffe298')

NUBES_DEF = [
    (74, 20, 148, PAL['nube'][0], 2),
    (254, 30, 162, PAL['nube'][1], 3),
    (448, 18, 142, PAL['nube'][2], 2),
    (168, 74, 152, PAL['nube'][3], 2),
    (524, 96, 120, PAL['nube'][4], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

C0, C1, C2, C3 = PAL['cliff']
C_DEEP = mix(C2, '#0a0709', 0.42)
C_MIDHI = mix(C1, C3, 0.50)
C_SHMD = mix(C0, C2, 0.45)
T0, T1, T2, T3 = PAL['tree']
R0, R1, R2, R3 = PAL['roof']
W0, W1, W2 = PAL['wall']
WD0, WD1, WD2 = PAL['wood']


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


# 1. Monte Hokage sin bandas cebra: estratos orgánicos 2D y farallón amplificado (y ~ 80..226)
rx_c = Ruido(923)
ry_c = Ruido(937)
r_bl = Ruido(953)
RIDGE_Y = [0] * W
for x in range(W):
    if x < 442:
        ridge = int(84 + 6 * fbm(rx_c, x * 0.022) + 4 * math.sin(x * 0.013))
    else:
        ramp = min(1.0, (x - 442) / 105.0)
        ridge = int(90 + 116 * (0.5 - 0.5 * math.cos(math.pi * ramp)) + 8 * fbm(rx_c, x * 0.02))
    ridge = min(226, ridge)
    RIDGE_Y[x] = ridge
    canopy_top = ridge - int(6 + 5 * max(0.0, math.sin(x * 0.17) + 0.5 * math.cos(x * 0.31)))
    for y in range(canopy_top, 269):
        if y < ridge + 5:
            c = T3 if y < ridge - 1 and (x + y) % 3 == 0 else (T1 if y < ridge + 2 else T2)
            put(x, y, c)
            continue
        dy_wall = y - ridge
        # Relieve geológico 2D no periódico: bloques verticales facetados + estratos suaves horizontales
        wx = fbm(rx_c, x * 0.024 + 1.1 * fbm(r_bl, y * 0.032))
        wy = fbm(ry_c, y * 0.055 + 0.9 * fbm(rx_c, x * 0.019 + 7.3))
        strata = 0.07 * math.sin(y * 0.17 + 3.2 * wx)
        val = 0.52 * wx + 0.48 * wy + strata
        if dy_wall < 8:
            c = C2 if dy_wall < 4 else C_SHMD
        elif val > 0.68:
            c = C_MIDHI if dith(x, y, 0.45) else C1
        elif val > 0.48:
            c = C1 if dy_wall < 92 else C0
        elif val > 0.30:
            c = C0
        elif val > 0.18:
            c = C_SHMD
        else:
            c = C2
        put(x, y, c)


# 2. LOS 7 ROSTROS DEL MONTE HOKAGE ESCULPIDOS EN ALTO RELIEVE 3D (58x76 px cada uno, iluminación direccional)
def esculpe_hokage_relieve(idx, cx, cy):
    """Esculpe el busto monumental de cada Hokage en un buffer de profundidad (z) y normaliza luz/sombra."""
    pw, ph = 58, 76
    ox, oy = cx - pw // 2, cy - ph // 2
    z_buf = [[0.0] * pw for _ in range(ph)]
    kind_buf = [['cliff'] * pw for _ in range(ph)]
    grove_buf = [[0.0] * pw for _ in range(ph)]

    # Altura/profundidad local: (u, v) centrado en la cara (u=0 centro X, v=0 centro ojos/puente)
    for py in range(ph):
        v = py - 35
        for px in range(pw):
            u = px - pw // 2

            # A. Contorno base de cabeza / mandíbula (v = -20..+18)
            is_tsunade = (idx == 4)
            is_hiruzen = (idx == 2)
            face_w_top = 12.2 if is_tsunade else 13.4
            jaw_taper = 0.46 if is_tsunade else (0.34 if idx in (3, 5) else 0.28)

            in_face = False
            z_head = 0.0
            if -19 <= v <= 18:
                if v < -2:
                    r_el = (u / face_w_top) ** 2 + ((v + 4.0) / 15.0) ** 2
                    if r_el <= 1.0:
                        in_face = True
                        z_head = 2.4 * math.sqrt(max(0.0, 1.0 - r_el))
                else:
                    t_j = max(0.0, v / 18.0)
                    hw_v = face_w_top * (1.0 - jaw_taper * (t_j ** 1.35))
                    if abs(u) <= hw_v:
                        nx_f = u / max(1e-4, hw_v)
                        ny_f = (v - 2.0) / 16.5
                        in_face = True
                        z_head = 2.35 * math.sqrt(max(0.0, 1.0 - nx_f * nx_f * 0.88)) * math.sqrt(max(0.0, 1.0 - ny_f * ny_f * 0.72))

            # B. Hombros / cuello / base rocosa tallada en la pared (v = +17..+37)
            in_bust = False
            z_bust = 0.0
            if 15 <= v <= 37:
                # Cuello
                if abs(u) <= 7.8 and v <= 24:
                    in_bust = True
                    z_bust = 1.45 * math.sqrt(max(0.0, 1.0 - (u / 8.0) ** 2))
                # Pecho/hombros amplios que funden en el farallón
                sh_hw = 10.0 + (v - 18) * 1.15
                if v >= 20 and abs(u) <= min(26.5, sh_hw):
                    in_bust = True
                    z_bust = max(z_bust, 1.85 * math.sqrt(max(0.0, 1.0 - (u / min(27.0, sh_hw + 2.0)) ** 2)) * (1.0 - max(0, v - 32) * 0.14))

            # C. Volumen capilar, capuchas, happuri y peinados icónicos
            hair_z = 0.0
            in_hair = False
            kind_over = None

            if idx == 0:  # 1º Hashirama Senju: melena larga y lisa cayendo por ambos lados + flequillo recto
                if -24 <= v <= -9 and abs(u) <= 15.5 - max(0, (-18 - v) * 1.2):
                    in_hair = True
                    hair_z = 2.65
                if -14 <= v <= 26 and 10.5 <= abs(u) <= 17.5 - max(0, (v - 14) * 0.28):
                    in_hair = True
                    hair_z = 2.55 - abs(abs(u) - 13.5) * 0.12
                # Mechones frontales curvos sobre sienes
                if -12 <= v <= -3 and 10.0 <= abs(u) <= 14.0:
                    in_hair = True
                    hair_z = 2.75

            elif idx == 1:  # 2º Tobirama Senju: cresta densa y conectada + happuri metálico + cuello alto
                if -18 <= v <= -11 and abs(u) <= 13.8:
                    in_hair = True
                    hair_z = 2.45
                spikes = [
                    (-10, -14, -13, -22, 4.4), (-5, -14, -6, -24, 4.6),
                    (0, -14, 0, -25, 4.8), (5, -14, 6, -24, 4.6), (10, -14, 13, -22, 4.4),
                ]
                for ax, ay, bx, by, w_sp in spikes:
                    d_s = _seg_dist(u, v, ax, ay, bx, by)
                    rad_s = w_sp * (1.0 - _smoothstep(0, 12, math.hypot(u - ax, v - ay)) * 0.68)
                    if d_s <= rad_s:
                        in_hair = True
                        hair_z = max(hair_z, 2.55 - d_s * 0.12)
                if -15 <= v <= 3 and 11.2 <= abs(u) <= 15.0:
                    in_hair = True
                    hair_z = 2.35
                # Cuello alto integrado en la roca bajo las sienes (sin bloque blanco cuadrado artificial)
                if 17 <= v <= 26 and abs(u) <= 13.5 - max(0, (v - 22) * 0.8):
                    kind_over = 'fur_collar'
                    hair_z = 2.35 + 0.16 * math.sin(u * 0.7)

            elif idx == 2:  # 3º Hiruzen Sarutobi: capucha shinobi envolvente + protector visor + perilla
                r_hood = (u / 16.5) ** 2 + ((v + 3.0) / 21.5) ** 2
                if r_hood <= 1.0 and -24 <= v <= 21 and not (in_face and abs(u) <= 10.5 and -8 <= v <= 13):
                    in_hair = True
                    kind_over = 'hood'
                    hair_z = 2.45 * math.sqrt(max(0.0, 1.0 - r_hood * 0.65))
                if 11 <= v <= 21 and abs(u) <= 4.4 * (1.0 - (v - 11) / 13.0):
                    kind_over = 'beard'
                    hair_z = 2.65

            elif idx == 3:  # 4º Minato Namikaze: corona amplia de grandes mechones entrelazados + 2 mechones laterales
                if -19 <= v <= -11 and abs(u) <= 15.5:
                    in_hair = True
                    hair_z = 2.60
                spikes = [
                    (-10, -12, -21, -14, 5.2), (-8, -14, -17, -23, 5.4),
                    (-5, -15, -9, -27, 5.4), (0, -15, 0, -29, 5.6),
                    (5, -15, 9, -27, 5.4), (8, -14, 17, -23, 5.4), (10, -12, 21, -14, 5.2),
                ]
                for ax, ay, bx, by, w_sp in spikes:
                    d_s = _seg_dist(u, v, ax, ay, bx, by)
                    rad_s = w_sp * (1.0 - _smoothstep(0, 16, math.hypot(u - ax, v - ay)) * 0.72)
                    if d_s <= rad_s:
                        in_hair = True
                        hair_z = max(hair_z, 2.75 - d_s * 0.14)
                for sx in (-12.0, 12.0):
                    d_lock = _seg_dist(u, v, sx, -11, sx * 0.96, 15)
                    w_lock = 2.8 * (1.0 - max(0.0, (v - 2.0) / 16.0) * 0.6)
                    if d_lock <= w_lock and v >= -12:
                        in_hair = True
                        hair_z = max(hair_z, 2.85)

            elif idx == 4:  # 5ª Tsunade: raya al medio limpia + melena enmarcando rostro hasta los hombros
                if -23 <= v <= -11 and abs(u) <= 14.5 - max(0, (-17 - v) * 1.1):
                    in_hair = True
                    hair_z = 2.65
                for sign_x in (-1, 1):
                    d_arc = _seg_dist(u, v, 0.5 * sign_x, -17, 11.5 * sign_x, -6)
                    if d_arc <= 2.9:
                        in_hair = True
                        hair_z = max(hair_z, 2.75)
                for sx in (-11.5, 11.5):
                    d_l = _seg_dist(u, v, sx, -8, sx * 1.06, 26)
                    if d_l <= 3.1 - max(0, (v - 16) * 0.15):
                        in_hair = True
                        hair_z = max(hair_z, 2.70)

            elif idx == 5:  # 6º Kakashi Hatake: cresta asimétrica gruesa barriendo hacia la izquierda
                if -21 <= v <= -11 and -15 <= u <= 14:
                    in_hair = True
                    hair_z = 2.60
                spikes = [
                    (-8, -14, -18, -22, 5.4), (-4, -15, -11, -28, 5.8),
                    (0, -15, -3, -30, 6.0), (5, -15, 4, -27, 5.4),
                    (9, -13, 14, -22, 4.8), (11, -11, 17, -14, 4.0),
                ]
                for ax, ay, bx, by, w_sp in spikes:
                    d_s = _seg_dist(u, v, ax, ay, bx, by)
                    rad_s = w_sp * (1.0 - _smoothstep(0, 17, math.hypot(u - ax, v - ay)) * 0.72)
                    if d_s <= rad_s:
                        in_hair = True
                        hair_z = max(hair_z, 2.72 - d_s * 0.13)
                if -14 <= v <= 2 and abs(u) >= 10.5 and abs(u) <= 14.5:
                    in_hair = True
                    hair_z = max(hair_z, 2.45)

            elif idx == 6:  # 7º Naruto Uzumaki: puntas anchas y compactas sobre la banda frontal
                if -18 <= v <= -11 and abs(u) <= 13.8:
                    in_hair = True
                    hair_z = 2.55
                spikes = [
                    (-10, -12, -14, -19, 4.4), (-5, -13, -8, -23, 4.6),
                    (0, -14, 0, -24, 4.8), (5, -13, 8, -23, 4.6),
                    (10, -12, 14, -19, 4.4),
                ]
                for ax, ay, bx, by, w_sp in spikes:
                    d_s = _seg_dist(u, v, ax, ay, bx, by)
                    rad_s = w_sp * (1.0 - _smoothstep(0, 12, math.hypot(u - ax, v - ay)) * 0.68)
                    if d_s <= rad_s:
                        in_hair = True
                        hair_z = max(hair_z, 2.65 - d_s * 0.14)
                if -13 <= v <= 1 and 11.5 <= abs(u) <= 14.8:
                    in_hair = True
                    hair_z = max(hair_z, 2.40)

            # D. Protector frontal / Banda Konoha / Happuri
            is_headband = False
            is_plate = False
            if idx in (0, 2, 3, 6):
                if in_face and -13.0 <= v <= -7.2:
                    is_headband = True
                    if abs(u) <= 8.5 and -12.0 <= v <= -8.2:
                        is_plate = True
            elif idx == 1:  # Happuri de Tobirama rodeando frente + sienes + mejillas + barbilla
                top_hp = in_face and -13.0 <= v <= -7.2
                peak_hp = abs(u) <= max(0.0, 2.5 - (v + 7.2) * 0.9) and -7.2 <= v <= -4.5
                cheek_hp = (-8.0 <= v <= 12.0) and (8.8 <= abs(u) <= 13.8)
                chin_hp = (11.5 <= v <= 17.5) and (abs(u) <= 9.5) and in_face
                if top_hp or peak_hp or cheek_hp or chin_hp:
                    is_headband = True
                    is_plate = True
            elif idx == 5:  # Banda de Kakashi inclinada cubriendo su ojo izquierdo (u > 0)
                diag_v = v - (u * 0.24)
                if in_face and -11.5 <= diag_v <= -4.2 and (diag_v <= -5.5 or u > -1.0):
                    is_headband = True
                    if -2.5 <= u <= 11.0 and -10.5 <= diag_v <= -5.2:
                        is_plate = True
                    if 0.0 <= u <= 11.5 and -5.8 <= diag_v <= 1.2:
                        is_headband = True  # Tapa por completo el ojo derecho en pantalla (su izq.)

            # E. Nicho tallado alrededor del busto para contrastar la silueta
            if not (in_face or in_bust or in_hair or kind_over):
                # Verifica cercanía al busto para formar el rebaje de roca (nicho)
                rx_a, ry_a = (u / 23.0), ((v - 3.0) / 28.0)
                if rx_a * rx_a + ry_a * ry_a <= 1.15:
                    z_buf[py][px] = -0.95 * (1.0 - (rx_a * rx_a + ry_a * ry_a) * 0.72)
                    kind_buf[py][px] = 'alcove'
                continue

            # Selección de profundidad y tipo dominante en este píxel
            z_val = max(z_bust, z_head)
            kind = 'face' if in_face else 'bust'
            if kind_over is not None and hair_z >= z_val - 0.15:
                z_val = max(z_val, hair_z)
                kind = kind_over
            elif in_hair and (hair_z > z_val + 0.05 or not in_face):
                z_val = hair_z
                kind = 'hair'
            elif is_headband:
                z_val = max(z_val, z_head + (0.48 if is_plate else 0.34))
                kind = 'plate' if is_plate else 'cloth'

            # F. Relieve anatómico esculpido sobre el rostro visible
            if kind == 'face' and in_face:
                # 1) Arco superciliar (frente inferior elevada +0.42)
                brow_y = -4.2
                if -5.8 <= v <= -3.2 and 1.2 <= abs(u) <= 9.2:
                    z_val += 0.44 * math.exp(-((v - brow_y) / 1.1) ** 2)

                # 2) Cuencas orbitales + ojos tallados (para Kakashi solo el izquierdo u < -1)
                for side_e in (-1, 1):
                    if idx == 5 and side_e > 0:
                        continue  # Ojo cubierto por la banda diagonal
                    ex, ey = side_e * 5.2, -1.2
                    du_e, dv_e = (u - ex) / 3.4, (v - ey) / 2.2
                    r_sock = du_e * du_e + dv_e * dv_e
                    if r_sock < 1.0:
                        z_val -= 0.72 * (1.0 - r_sock)
                    # Globo ocular ligeramente abombado en el centro
                    du_b, dv_b = (u - ex) / 2.2, (v - ey + 0.1) / 1.2
                    if du_b * du_b + dv_b * dv_b < 1.0:
                        z_val += 0.36
                    # Surco fino del párpado superior e iris tallado (¡nunca manchas negras gigantes!)
                    lid_v = ey - 0.8 + 0.16 * (u - ex) ** 2
                    if abs(u - ex) <= 2.3 and abs(v - lid_v) <= 0.65:
                        grove_buf[py][px] = max(grove_buf[py][px], 0.78)
                    if abs(u - ex) <= 0.85 and abs(v - ey) <= 0.75:
                        grove_buf[py][px] = max(grove_buf[py][px], 0.90)

                # 3) Arrugas de sabiduría (Hiruzen) o cicatriz de Kakashi
                if idx == 2:
                    if abs(u) <= 6.5 and v in (-6,):
                        grove_buf[py][px] = max(grove_buf[py][px], 0.48)
                    if 8.2 <= abs(u) <= 10.2 and abs(v + 0.5) <= 1.2:
                        grove_buf[py][px] = max(grove_buf[py][px], 0.45)
                if idx == 5 and -7 <= u <= -4 and -3 <= v <= 2:
                    if abs((u + 5.2) - (v + 0.5) * 0.12) <= 0.55 and v in (-3, 0, 1):
                        grove_buf[py][px] = max(grove_buf[py][px], 0.55)

                # 4) Puente nasal 3D prominente + sombra bajo la punta
                if -2.4 <= v <= 5.2 and abs(u) <= 2.4:
                    w_n = 1.35 + max(0.0, (v - 1.5) * 0.32)
                    if abs(u) <= w_n:
                        z_val += 0.92 * (1.0 - (u / (w_n + 0.4)) ** 2) * _smoothstep(-2.4, 3.8, v)
                if 4.8 <= v <= 6.3 and abs(u) <= 2.2:
                    z_val -= 0.48
                    if abs(abs(u) - 1.5) <= 0.7 and abs(v - 5.2) <= 0.6:
                        grove_buf[py][px] = max(grove_buf[py][px], 0.58)

                # 5) Máscara facial de Kakashi vs boca y labios esculpidos
                if idx == 5:
                    mask_top = 0.6 + 0.18 * (u ** 2) * 0.08
                    if v >= mask_top:
                        kind = 'mask'
                        z_val += 0.32
                        # Pliegues suaves diagonales de la tela en piedra iluminada (no bloque negro)
                        if abs(v - (6.0 + abs(u) * 0.25)) <= 0.65:
                            grove_buf[py][px] = max(grove_buf[py][px], 0.40)
                else:
                    # Boca expresiva y labio inferior con volumen
                    mouth_curve = -0.07 * (u * u) * 0.22 if idx == 6 else (0.04 * (u * u) * 0.12 if idx == 1 else 0.0)
                    mv = 9.0 + mouth_curve
                    mw = 4.6 if idx == 6 else (3.3 if is_tsunade else 3.9)
                    if abs(u) <= mw and abs(v - mv) <= 0.60:
                        grove_buf[py][px] = max(grove_buf[py][px], 0.78)
                    if 9.8 <= v <= 12.2 and abs(u) <= mw * 0.85:
                        z_val += 0.38 * (1.0 - (abs(u) / (mw + 0.5)) ** 2)
                    if 12.2 <= v <= 14.0 and abs(u) <= mw * 0.7:
                        z_val -= 0.35

                # 6) Rasgos distintivos sutilmente grabados en piedra
                if idx == 4 and abs(u) + abs(v + 9.2) <= 2.4:
                    # Sello Byakugou (rombo) en la frente de Tsunade
                    grove_buf[py][px] = max(grove_buf[py][px], 0.85)
                    z_val += 0.15
                elif idx == 1 and v in (2, 3, 4) and (7.0 <= abs(u) <= 8.5):
                    # Marcas faciales Senju finas de Tobirama
                    grove_buf[py][px] = max(grove_buf[py][px], 0.55)
                elif idx == 6:
                    # Bigotes icónicos de Naruto (3 surcos finos 1px bien separados en cada mejilla)
                    for wy_k in (2.2, 4.6, 7.0):
                        if 5.2 <= abs(u) <= 9.6 and abs(v - wy_k - (abs(u) - 5.2) * 0.14) <= 0.45:
                            grove_buf[py][px] = max(grove_buf[py][px], 0.54)

            elif kind == 'hair':
                # Estrías suaves verticales siguiendo los mechones de piedra tallada
                z_val += 0.18 * math.sin(u * 0.85 + v * 0.18)

            z_buf[py][px] = z_val
            kind_buf[py][px] = kind

    # Pasada final: sombreado direccional (luz desde arriba-izquierda) sobre el lienzo
    c_hair_base = mix(C0, C2, 0.30)
    c_face_base = mix(C1, C0, 0.28)
    c_metal_base = mix(C1, C3, 0.25)
    c_mask_base = mix(C0, C1, 0.35)

    for py in range(1, ph - 1):
        gy = oy + py
        for px in range(1, pw - 1):
            gx = ox + px
            if not (0 <= gx < W and 0 <= gy < 252):
                continue
            k = kind_buf[py][px]
            if k == 'cliff':
                continue
            if k == 'alcove':
                over(gx, gy, C_SHMD, min(0.58, abs(z_buf[py][px]) * 0.55))
                continue

            # Permite que los mechones coronen de verdad sobre el cielo ligeramente por encima de RIDGE_Y[gx]
            if gy < RIDGE_Y[gx] - 12:
                continue

            # Gradiente de superficie 3D (luz superior-izquierda: dx+dy negativo -> iluminado)
            dx = z_buf[py][px + 1] - z_buf[py][px - 1]
            dy = z_buf[py + 1][px] - z_buf[py - 1][px]
            lit = 0.52 - dx * 0.55 - dy * 0.68
            lit = max(0.0, min(1.0, lit))

            if k == 'hair':
                base = mix(c_hair_base, C_MIDHI, lit * 0.62)
                if lit < 0.28:
                    base = mix(C2, c_hair_base, lit / 0.28)
            elif k == 'plate':
                base = mix(c_metal_base, C3, max(0.15, lit * 0.90))
            elif k == 'hood' or k == 'cloth':
                base = mix(C_SHMD, C1, lit * 0.72)
            elif k == 'mask':
                base = mix(C0, C1, 0.28 + lit * 0.65)
            elif k == 'beard':
                base = mix(C2, C1, lit * 0.72)
            elif k == 'fur_collar':
                base = mix(C0, C_MIDHI, lit * 0.78)
            elif k == 'bust':
                base = mix(C2, C1, lit * 0.68)
            else:  # 'face'
                base = mix(C2, C1, 0.28 + lit * 0.65)
                if lit > 0.74:
                    base = mix(base, C3, (lit - 0.74) / 0.26 * 0.85)

            g_amt = grove_buf[py][px]
            if g_amt > 0.0:
                base = mix(base, C_DEEP, min(0.76, g_amt * 0.68))

            # Funde suavemente la base inferior del busto en la roca del acantilado sin corte recto horizontal
            v_loc = py - 35
            if k == 'bust' and v_loc > 22:
                al_b = _smoothstep(36.0, 22.0, float(v_loc))
                if al_b < 0.99:
                    over(gx, gy, base, al_b)
                    continue

            put(gx, gy, base)


HOKAGE_CENTERS = [42, 102, 162, 222, 282, 342, 402]
for hi, h_cx in enumerate(HOKAGE_CENTERS):
    esculpe_hokage_relieve(hi, h_cx, 146)

# Vegetación densa en la base de los acantilados de Konoha y paseo peatonal junto al Río Naka
r_bush = Ruido(967)
for x in range(W):
    by_top = int(222 + 9 * math.sin(x * 0.05) + 8 * fbm(r_bush, x * 0.04))
    for y in range(by_top, 268):
        col = T3 if (x + y) % 7 == 0 and y < by_top + 4 else (T1 if fbm(r_bush, x * 0.08 + y * 0.06) > 0.48 else T0)
        put(x, y, col)
for y in range(268, HOR + 1):
    for x in range(W):
        c = C3 if y == 268 else (C2 if y >= HOR - 1 else (C0 if (x // 8 + y // 4) % 2 else C1))
        put(x, y, c)

# Casas shinobi de Konoha (izquierda y derecha del Edificio del Hokage)
casas = [
    (120, 270, 32, 24),
    (156, 270, 28, 20),
    (264, 270, 34, 26),
    (304, 270, 24, 21),
    (404, 270, 30, 22),
    (438, 270, 26, 19),
]
for bx, by, bw, bh in casas:
    for y in range(by - bh, by):
        for x in range(bx, bx + bw):
            put(x, y, W1 if x > bx + bw - 5 else W0)
    for i in range(9):
        for x in range(bx - 2 + i, bx + bw + 2 - i):
            put(x, by - bh - i, R0 if i % 2 == 0 else R1)
    for wx in range(bx + 5, bx + bw - 6, 8):
        if ANIM:
            VENTANAS.append([wx, by - bh + 7])
            put(wx, by - bh + 7, W1)
        else:
            for dy in range(4):
                for dx in range(3):
                    put(wx + dx, by - bh + 6 + dy, PAL['lit'] if FASE != 'dia' else '#5e88b0')
            if FASE != 'dia':
                glow(wx + 1, by - bh + 8, 4, PAL['lit'], 0.35)

# 4. EDIFICIO CENTRAL DEL HOKAGE (cúpula roja + símbolo de Fuego 火, cx=218, by=272)
HX, HB = 218, 272
for y in range(HB - 32, HB):
    for x in range(HX - 24, HX + 25):
        put(x, y, W2 if abs(x - HX) < 12 else (W1 if abs(x - HX) > 19 else W0))
for dy in range(0, 20):
    hw = int(28 * math.sqrt(max(0.0, 1.0 - ((20 - dy) / 21.0) ** 2))) + 2
    y = HB - 50 + dy
    for dx in range(-hw, hw + 1):
        c = R3 if dy < 5 else (R1 if dx < 0 else R0)
        put(HX + dx, y, c)
for dx in range(-28, 29):
    put(HX + dx, HB - 32, R2)
    put(HX + dx, HB - 31, '#e8b658')
disc(HX, HB - 40, 6, '#f6efe0')
for px_k, py_k in ((0, -3), (0, -2), (0, -1), (-2, -2), (2, -2), (0, 0), (-1, 1), (1, 1), (-2, 2), (2, 2)):
    put(HX + px_k, HB - 40 + py_k, '#d42c28')
for wx in (HX - 16, HX - 8, HX + 6, HX + 14):
    if ANIM:
        VENTANAS.append([wx, HB - 22])
    else:
        for dy in range(4):
            for dx in range(2):
                put(wx + dx, HB - 22 + dy, PAL['lit'] if FASE != 'dia' else '#6892bc')

# 5. PUESTO DE RAMEN ICHIRAKU (x=44..90, by=272) con cortinas noren y faroles rojos
IX, IW, IB = 44, 46, 272
for y in range(IB - 22, IB):
    for x in range(IX, IX + IW):
        put(x, y, WD0 if y > IB - 8 else '#261e1c')
for x in range(IX - 3, IX + IW + 4):
    put(x, IB - 24, R1)
    put(x, IB - 23, R0)
    put(x, IB - 22, R2)
for k in range(3):
    nx0 = IX + 5 + k * 13
    for y in range(IB - 21, IB - 12):
        for x in range(nx0, nx0 + 10):
            put(x, y, '#f8efe0' if y < IB - 13 else '#d8ccb8')
    put(nx0 + 4, IB - 17, '#d43028')
    put(nx0 + 5, IB - 17, '#d43028')
for fx, fy in ((IX + 2, IB - 18), (IX + IW - 2, IB - 18), (288, 266), (392, 266)):
    put(fx, fy, '#fff0c4')
    put(fx, fy + 1, '#ff6830')
    if ANIM:
        FAROLES.append([fx, fy, 8])
    elif FASE != 'dia':
        glow(fx, fy, 8, '#ff7830', 0.50)

# 6. MIRADOR DE KONOHA sobre el río (x=320..392): Plataforma y sprites nítidos de Naruto Hokage & Sasuke
for x in range(320, 392):
    put(x, 275, C3)
    put(x, 276, C1)
    put(x, 277, C2)
for px_b in (324, 356, 388):
    for dy in range(266, 278):
        put(px_b, dy, C2)
        put(px_b + 1, dy, C3)

# Naruto Séptimo Hokage (cx=342, by=274, 23 filas x 18 cols): capa blanca con llamas rojas y mechones rubios
nar_spr = [
    '......YY..YY......',
    '....YYYYYYYYYY....',
    '...YYYYYYYYYYYY...',
    '....YYHHHHHHYY....',
    '....YSSSSSSSSY....',
    '....YSSESSESSS....',
    '.....SSSSSSSS.....',
    '...RRRRWWWWWRR....',
    '..RRRRWWWWWWWRR...',
    '..WWWWWOOOOWWWWW..',
    '.WWWWWWOOOOOWWWWW.',
    '.WWWWWWOOOOOWWWWW.',
    '.WWWWWWOOOOWWWWW..',
    '.WWWWWWOOOOWWWWW..',
    '.WWWWWWOOOOWWWWW..',
    '.WRWWWWO..OWWWWR..',
    '.WRRWWWW..WWWRRW..',
    '.RRRRWW....WRRRR..',
    '..RRRRO....ORRR...',
    '......O....O......',
    '......O....O......',
    '.....KKK..KKK.....',
    '.....KKK..KKK.....',
]
nar_map = {
    'Y': '#ffd238', 'H': '#d0d8e4', 'S': '#f2c6a4', 'E': '#223866',
    'W': '#f6f2ea', 'R': '#d83824', 'O': '#ef6820', 'K': '#181c28',
}
pinta_sprite(lz, 342, 274, nar_spr, nar_map)

# Sasuke Uchiha (cx=370, by=274, 23 filas x 18 cols): flequillo oscuro sobre ojo, capa azul oscura y katana
sas_spr = [
    '.....KKKKKKKK.....',
    '....KKKKKKKKKK....',
    '...KKKKKKKKKKKK...',
    '...KKKSSSSKKKK....',
    '...KKKSESSSKKK....',
    '....KKKSSSSSS.....',
    '...KDDDDDDDDDDH...',
    '..DDDDDDDDDDDHH...',
    '..DDDDDDDDDDDHDD..',
    '.DDDDCCPPPPCCDDDD.',
    '.DDDDCCPPPPCCDDDD.',
    '.DDDDCCPPPPCCDDDD.',
    '.DDDDDDPPPPDDDDDD.',
    '.DDDDDDDDDDDDDDDD.',
    '.DDDDDDDDDDDDDDDD.',
    '.DDDDD.DDDD.DDDDD.',
    '..DDDD.DDDD.DDDD..',
    '..DDD..DDDD..DDD..',
    '.......D..D.......',
    '.......D..D.......',
    '.......D..D.......',
    '......KK..KK......',
    '......KK..KK......',
]
sas_map = {
    'K': '#161a2c', 'S': '#eed8ca', 'E': '#d83448', 'D': '#282d46',
    'C': '#484d68', 'P': '#7856b8', 'H': '#98a6c0',
}
pinta_sprite(lz, 370, 274, sas_spr, sas_map)

# 7. Reflejo del Río Naka bajo HOR=280
render_lago(lz, PAL['agua'], PAL['olas'], DESTELLOS, ANIM, mx=MX, hor=HOR, reflejo_cols=PAL['reflejo'], reflejo_astro=True)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
