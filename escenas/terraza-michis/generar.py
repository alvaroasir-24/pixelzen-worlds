#!/usr/bin/env python3
"""PixelZen Worlds - Terraza de los Michis (Principal): Siesta en el Césped."""
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
random.seed(1601)

PALETAS = {
    'noche': dict(
        sky=['#050a16', '#0a1428', '#101f3a', '#182c4e', '#213c62', '#2c4d76', '#3a608a', '#4c759d', '#628cb0', '#27536a'],
        hills=('#0b1622', '#122234', '#070e18'),
        fence=('#1d1512', '#2d211b', '#120d0b', '#3f2e25'),
        grass=('#183614', '#224a1b', '#2e6022', '#11270e', '#3d742b'),
        wood=('#3c2416', '#563420', '#27170e', '#70452b'),
        mat=('#0b0e14', '#161c26', '#05070a'),
        sisal=('#705a3c', '#927852', '#52402a', '#ab9068'),
        gray_cat=('#363c46', '#4d5563', '#23272e', '#656f80', '#e6ecf5', '#cbd5e1', '#f59e0b', '#fde047', '#f4a4b8'),
        cream_cat=('#8b786c', '#a89486', '#69594f', '#c2afa2', '#eee6dc', '#d8cec2', '#f4a4b8', '#463832'),
        vig=0.72,
        nube=['#1a2a46', '#24385a', '#304870', '#3f5a86', '#526f9c', '#132038'],
    ),
    'dorado': dict(
        sky=['#131838', '#252654', '#46346c', '#74487c', '#a65c7a', '#d67468', '#f2985e', '#fbbc5c', '#fde07e', '#fff4ba'],
        hills=('#232036', '#362e4c', '#161424'),
        fence=('#362218', '#4e3122', '#22150e', '#6c4430'),
        grass=('#2e5816', '#3e741e', '#528e26', '#20400f', '#6ca832'),
        wood=('#5d341c', '#7c4727', '#3c2010', '#9c5c34'),
        mat=('#12151e', '#202634', '#090b10'),
        sisal=('#9c7b4a', '#c29c62', '#755a34', '#dcb67a'),
        gray_cat=('#444954', '#5e6674', '#2c3038', '#788292', '#f4efe6', '#d8d0c4', '#f59e0b', '#fef08a', '#f9a8b8'),
        cream_cat=('#a98e78', '#c6aa92', '#826b59', '#dec4ad', '#fbf4ea', '#e4d8ca', '#f49aa8', '#5c4638'),
        vig=0.82,
        nube=['#543456', '#724264', '#945670', '#b8707a', '#dc9286', '#3a2240'],
    ),
    'dia': dict(
        sky=['#1a4e9c', '#2966b8', '#3c80d0', '#549ae2', '#72b4ee', '#94ccf6', '#b8e0fa', '#daf0fc', '#eff8fc', '#fcf8e4'],
        hills=('#2a4e68', '#3c6884', '#1d384c'),
        fence=('#3c291e', '#553a2b', '#261912', '#6e4d3a'),
        grass=('#386e18', '#4a8c20', '#5ea62a', '#285210', '#78be38'),
        wood=('#683b20', '#8a502c', '#452614', '#aa6538'),
        mat=('#141822', '#222836', '#0a0c12'),
        sisal=('#aa8a56', '#ceb074', '#82673e', '#e4c88c'),
        gray_cat=('#484e5a', '#626a7a', '#30343c', '#7c8698', '#f8fafc', '#dce4ee', '#f59e0b', '#fde047', '#f9a8b8'),
        cream_cat=('#b29c8a', '#ccb6a4', '#8c7767', '#e2cebe', '#fcf8f2', '#e4dcd0', '#f49aa8', '#5e4a3d'),
        vig=0.90,
        nube=['#eef5fc', '#dceaf8', '#cadcf0', '#ffffff', '#e4eef8', '#b8cce2'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#4ade80', '#fde047'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#93c5fd', base='#f8fafc', sombra='#cbd5e1', crater='#94a3b8', crater_hi='#cbd5e1'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 24, halo='#fde68a', centro='#fffbeb', borde='#f59e0b', rayo='#fef08a'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, hor=212)

if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, 360, 62, 38, halo='#93c5fd', base='#f8fafc', sombra='#cbd5e1', crater='#94a3b8', crater_hi='#cbd5e1')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 344, 134, 24, halo='#fde68a', centro='#fffbeb', borde='#f59e0b', rayo='#fef08a')
    else:
        dibuja_sol_estandar(lz, 344, 68, 24, halo='#fde68a', centro='#ffffff', borde='#f59e0b', rayo='#fef08a')

NUBES_DEF = [
    (66, 40, 86, PAL['nube'][1], 2),
    (210, 34, 78, PAL['nube'][2], 2),
    (392, 52, 74, PAL['nube'][3], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)


def ellipse(cx, cy, rx, ry, col, alpha=1.0):
    rx2, ry2 = max(1.0, float(rx * rx)), max(1.0, float(ry * ry))
    for dy in range(-int(ry) - 1, int(ry) + 2):
        for dx in range(-int(rx) - 1, int(rx) + 2):
            if (dx * dx) / rx2 + (dy * dy) / ry2 <= 1.0:
                if alpha >= 0.99:
                    put(int(round(cx + dx)), int(round(cy + dy)), col)
                else:
                    over(int(round(cx + dx)), int(round(cy + dy)), col, alpha)


def rot_ellipse(cx, cy, rx, ry, ang_deg, col, edge_col=None):
    rad = math.radians(ang_deg)
    ca, sa = math.cos(rad), math.sin(rad)
    m = int(max(rx, ry)) + 2
    rx2, ry2 = max(1.0, float(rx * rx)), max(1.0, float(ry * ry))
    for dy in range(-m, m + 1):
        for dx in range(-m, m + 1):
            u = dx * ca + dy * sa
            v = -dx * sa + dy * ca
            d = (u * u) / rx2 + (v * v) / ry2
            if d <= 1.0:
                c = edge_col if (edge_col and d > 0.78) else col
                put(int(round(cx + dx)), int(round(cy + dy)), c)


# 1. Silueta lejana de copas de arboles y tejados tranquilos sobre el horizonte (y=170..226)
r_sky = Ruido(41, 64)
h_dk, h_md, h_sh = PAL['hills']
for x in range(W):
    hy = int(196 - 18 * fbm(r_sky, x * 0.015) - 7 * math.sin(x * 0.04))
    for y in range(hy, 232):
        put(x, y, h_sh if y < hy + 3 else (h_md if (x + y) % 5 == 0 else h_dk))

# 2. Valla de listones oscuros / canizo de terraza (y=212..262) con postes y luz calida
f_dk, f_md, f_sh, f_hi = PAL['fence']
for y in range(214, 263):
    for x in range(W):
        if x % 6 == 0:
            put(x, y, f_sh)
        elif x % 6 == 1:
            put(x, y, f_hi if y % 7 != 0 else f_md)
        elif x % 6 == 5:
            put(x, y, f_dk)
        else:
            put(x, y, f_md if (x + y) % 3 else f_dk)
# Travesaños horizontales de madera
for ry in (220, 256):
    for x in range(W):
        put(x, ry, f_sh)
        put(x, ry + 1, f_hi)
        put(x, ry + 2, f_dk)

# Guirnalda de lucecitas calidas sobre la valla (fuera de zona HUD x>=478, y<=220)
bulb_xs = [24, 62, 100, 138, 176, 214, 252, 290, 328, 366, 404, 442]
for idx in range(len(bulb_xs) - 1):
    x0, x1 = bulb_xs[idx], bulb_xs[idx + 1]
    for x in range(x0, x1 + 1):
        u = (x - x0) / float(max(1, x1 - x0))
        cy = int(round(215 + math.sin(u * math.pi) * 6))
        put(x, cy, '#1a1512')
for bx in bulb_xs:
    by = 216
    put(bx, by, '#fbbf24' if FASE != 'dia' else '#fef08a')
    put(bx, by + 1, '#fffbeb')
    if FASE != 'dia':
        glow(bx, by + 1, 7, '#f59e0b', 0.42 if FASE == 'noche' else 0.28)
        if not ANIM:
            FAROLES.append([bx, by + 1, 7])

# 3. Cesped artificial exuberante de la terraza (y=262..399) con briznas y textura pixel
g_dk, g_md, g_hi, g_sh, g_bt = PAL['grass']
rng_g = random.Random(1609)
for y in range(262, H):
    prof = (y - 262) / float(H - 262)
    for x in range(W):
        n = rng_g.random()
        if y < 267:
            c = g_sh if n < 0.65 else g_dk
        elif n < 0.14 * (0.5 + prof):
            c = g_bt
        elif n < 0.42:
            c = g_hi if dith(x, y, 0.35 + prof * 0.35) else g_md
        elif n < 0.78:
            c = g_md
        else:
            c = g_dk
        put(x, y, c)
        # Briznas verticales en primer plano
        if prof > 0.25 and (x * 13 + y * 7) % 19 == 0 and y > 266:
            put(x, y - 1, g_bt)
            if prof > 0.65:
                put(x, y - 2, g_hi)

# 4. Tarima de listones de madera en esquina inferior izquierda (x=0..112, y=322..400)
w_dk, w_md, w_sh, w_hi = PAL['wood']
for y in range(324, H):
    for x in range(0, 128):
        # Borde diagonal como en la foto
        diag_x = int(96 + (y - 324) * 0.34)
        if x > diag_x:
            continue
        if x >= diag_x - 2 or y <= 325:
            put(x, y, w_sh)
            continue
        plank_h = (y - 324) % 14
        if plank_h == 0:
            put(x, y, w_sh)
        elif plank_h == 1:
            put(x, y, w_hi)
        else:
            grain = ((x + (y // 14) * 19) % 11 == 0)
            put(x, y, w_dk if grain else w_md)
        # Tornillos/juntas
        if (x % 42 == 0 or x % 42 == 1) and (plank_h in (3, 11)):
            put(x, y, w_sh)

# 5. Alfombrilla negra y rascador de sisal arriba a la derecha (x=454..610, y=224..288)
m_dk, m_md, m_sh = PAL['mat']
for y in range(254, 294):
    for x in range(458, 598):
        dx = (x - 528) / 68.0
        dy = (y - 274) / 18.0
        if dx * dx + dy * dy <= 1.0:
            edge = dx * dx + dy * dy > 0.85
            put(x, y, m_sh if edge else (m_md if (x + y) % 4 == 0 else m_dk))

s_dk, s_md, s_sh, s_hi = PAL['sisal']
# Poste de cuerda sisal enrollada (x=514..544, y=222..276)
for y in range(224, 276):
    for x in range(516, 542):
        if x == 516 or x == 541:
            put(x, y, s_sh)
        elif y % 3 == 0:
            put(x, y, s_sh if x > 534 else s_dk)
        else:
            put(x, y, s_hi if x < 525 else s_md)
# Base superior del rascador
ellipse(529, 224, 22, 7, s_dk)
ellipse(529, 223, 20, 5, m_md)

# 6. Marco inferior derecho de puerta corredera de cristal (x=430..640, y=380..400)
for y in range(382, H):
    for x in range(430, W):
        diag_y = 398 - int((x - 430) * 0.08)
        if y >= diag_y:
            if y == diag_y or y == diag_y + 1:
                put(x, y, '#64748b' if FASE == 'dia' else '#334155')
            elif y <= diag_y + 4:
                put(x, y, '#94a3b8' if FASE == 'dia' else '#475569')
            else:
                put(x, y, '#1e293b')
if FASE != 'dia':
    glow(550, 392, 65, '#fbbf24', 0.18 if FASE == 'noche' else 0.12)

# 7. Pelotita multicolor de fieltro (centro en x=112, y=296, radio 9, bien separada de la cabeza)
ellipse(113, 303, 10, 4, '#091208', 0.42)  # sombra
ball_cols = ['#ef4444', '#facc15', '#22c55e', '#ec4899', '#3b82f6', '#fb923c']
for dy in range(-9, 10):
    for dx in range(-9, 10):
        d2 = dx * dx + dy * dy
        if d2 <= 80:
            patch_idx = ((dx + 9) // 5 + ((dy + 9) // 5) * 2) % len(ball_cols)
            col = ball_cols[patch_idx]
            if d2 > 62 or dy > 4:
                col = mix(col, '#111827', 0.35)
            elif dx < -2 and dy < -2:
                col = mix(col, '#ffffff', 0.25)
            put(112 + dx, 296 + dy, col)

# 8. MICHI CREMA Y BLANCO (panza arriba, estirado diagonalmente en x=136..278, y=295..382)
c_dk, c_md, c_sh, c_hi, c_wh, c_whs, c_pink, c_eye = PAL['cream_cat']
# Sombra suave semitransparente bajo el gato crema
for dy in range(-28, 30):
    for dx in range(-66, 66):
        rad = math.radians(22)
        u = dx * math.cos(rad) + dy * math.sin(rad)
        v = -dx * math.sin(rad) + dy * math.cos(rad)
        if (u * u) / (64.0 * 64.0) + (v * v) / (24.0 * 24.0) <= 1.0:
            over(202 + dx, 344 + dy, '#081407', 0.42)

# Cola esponjosa crema curvada suavemente tras la cadera
for i in range(16):
    u = i / 15.0
    tx = int(238 + u * 24)
    ty = int(336 - math.sin(u * 1.8) * 10)
    ellipse(tx, ty, 6, 5, c_dk if i % 2 == 0 else c_md)

# Patitas traseras estiradas hacia la derecha-abajo (pose comoda en V)
rot_ellipse(250, 344, 18, 8, 12, c_md, c_sh)
rot_ellipse(266, 347, 8, 6, 12, c_wh, c_whs)     # calcetin blanco pata sup
rot_ellipse(228, 366, 18, 8, 56, c_md, c_sh)
rot_ellipse(238, 378, 8, 6, 56, c_wh, c_whs)     # calcetin blanco pata inf

# Torso mullido panza arriba
rot_ellipse(196, 336, 42, 23, 24, c_md, c_sh)
rot_ellipse(188, 343, 33, 15, 24, c_dk)
# Gran panza blanca esponjosa
rot_ellipse(196, 332, 31, 15, 24, c_wh, c_whs)
rot_ellipse(174, 322, 17, 12, 24, c_wh)
rot_ellipse(216, 343, 15, 10, 20, c_wh, c_whs)

# Patitas delanteras recogidas sobre el pecho (pose zen!)
rot_ellipse(160, 328, 10, 7, -25, c_hi, c_md)
rot_ellipse(155, 332, 6, 5, -20, c_wh, c_whs)
rot_ellipse(173, 314, 10, 7, 15, c_hi, c_md)
rot_ellipse(177, 317, 6, 5, 15, c_wh, c_whs)

# Cabeza redonda British Shorthair crema (x=146, y=312)
for ex, ey in ((133, 300), (149, 294)):
    for oy in range(10):
        we = max(1, (oy + 1) // 2)
        for dx in range(-we, we + 1):
            put(ex + dx, ey - 5 + oy, c_sh if abs(dx) == we else c_md)
        if oy > 3:
            for dx in range(-max(0, we - 2), max(1, we - 1)):
                put(ex + dx, ey - 5 + oy, c_pink)
ellipse(146, 312, 16, 14, c_md)
ellipse(146, 310, 14, 11, c_hi)
ellipse(148, 316, 8, 5, c_wh)
put(147, 314, c_pink)
put(148, 314, c_pink)
# Ojitos cerrados felices (^ ^)
for ox in (140, 152):
    put(ox - 1, 309, c_eye)
    put(ox, 308, c_eye)
    put(ox + 1, 308, c_eye)
    put(ox + 2, 309, c_eye)
# Bigotitos blancos
for bx, by in ((138, 315), (137, 317), (156, 314), (157, 316)):
    put(bx, by, '#f8fafc')

# 9. MICHI GRIS Y BLANCO (tumbado de lado mirando arriba, x=300..445, y=256..360)
g1, g2, g0, g3, gw, gws, ge1, ge2, gpk = PAL['gray_cat']
ellipse(368, 336, 54, 18, '#081407', 0.42)

# Cola larga gris esponjosa curvada abajo a la derecha
for i in range(34):
    u = i / 33.0
    tx = int(414 + u * 28 - math.sin(u * math.pi) * 5)
    ty = int(316 + u * 34)
    ellipse(tx, ty, 6 if u < 0.7 else 5, 5, g1 if u < 0.5 else g0)
    if i % 3 == 0:
        put(tx - 1, ty - 1, g2)

# Pata trasera blanca estirada (como en la foto!)
rot_ellipse(344, 331, 22, 9, -8, gw, gws)
ellipse(324, 334, 7, 5, gw)
put(321, 334, gpk)

# Cuerpo grueso y atigrado sutil British Shorthair gris
rot_ellipse(382, 310, 42, 25, -10, g1, g0)
rot_ellipse(378, 304, 34, 18, -10, g2)
for s in range(5):
    sx = 360 + s * 11
    for dy in range(-11, 7):
        if (sx + dy) % 2 == 0:
            put(sx + (dy // 4), 302 + dy, g0)
# Pecho / babero blanco integrado al cuerpo
ellipse(350, 300, 15, 14, gw)
ellipse(352, 304, 11, 9, gws)

# Patas delanteras descansando suavemente sobre el cesped
rot_ellipse(332, 300, 15, 6, 12, g1, g0)
ellipse(318, 297, 7, 5, gw)
put(316, 296, gpk)
put(317, 298, '#1e1b18')

rot_ellipse(326, 314, 17, 6, 4, g2, g0)
ellipse(310, 314, 8, 5, gw)

# Cabeza redonda gris con orejas puntiagudas British Shorthair (x=354, y=276)
for ox_off in (-10, 10):
    for oy in range(11):
        w_e = max(1, (oy + 1) // 2)
        for dx in range(-w_e, w_e + 1):
            put(354 + ox_off + dx, 254 + oy, g0 if abs(dx) == w_e else g1)
        if oy > 3:
            for dx in range(-max(0, w_e - 2), max(1, w_e - 1)):
                put(354 + ox_off + dx, 254 + oy, '#fca5a5' if FASE != 'noche' else '#9d6b76')

ellipse(354, 276, 17, 15, g1)
ellipse(354, 274, 15, 12, g2)
ellipse(354, 268, 11, 6, g3)
ellipse(353, 282, 9, 6, gw)
ellipse(353, 279, 4, 3, gw)
put(353, 279, gpk)
put(352, 279, gpk)
for ex in (346, 360):
    ellipse(ex, 273, 3, 3, ge1)
    put(ex, 273, '#111827')
    put(ex - 1, 272, ge2)
    put(ex + 1, 272, '#ffffff')
for wy in (280, 282):
    for wx in range(334, 344, 2):
        put(wx, wy, '#f8fafc')
    for wx in range(363, 373, 2):
        put(wx, wy, '#f8fafc')

# Detalles adicionales y registro de luces
try:
    import pz_detalles
    pz_detalles.enriquecer_post_escena(lz)
except ImportError:
    pass

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
             chimenea=CHIMENEA, destellos=DESTELLOS, barca=None, luna=[360, 62, 38])
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
