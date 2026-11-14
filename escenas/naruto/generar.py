#!/usr/bin/env python3
"""PixelZen Worlds - Naruto Shippuden (Principal): Naruto Modo Baryon vs Isshiki Otsutsuki."""
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
random.seed(909)

PALETAS = {
    'noche': dict(
        sky=['#06020d', '#110619', '#220b24', '#38122b', '#521a30', '#702432', '#923030', '#b4422e', '#d45a2c', '#ed7a32'],
        mont=('#1d0f1b', '#140a14', '#0b050c'),
        pillar=('#241422', '#170c17', '#3a2034', '#0d060e'),
        ground=('#180e16', '#24141e', '#0e070e', '#321b26'),
        baryon=('#df2418', '#ff6418', '#ffd448', '#16050a', '#fff0a4'),
        kurama=('#8a1612', '#d43618', '#ff9824'),
        isshiki=('#ece9f4', '#b8b2ca', '#781834', '#221c2c', '#ffbe2c'),
        vig=0.72,
        nube=['#2b1224', '#401a2c', '#582434', '#743038', '#903e3c', '#200c1a'],
    ),
    'dorado': dict(
        sky=['#140818', '#281022', '#441a2a', '#68282c', '#903a28', '#b84e24', '#da6a26', '#f28c30', '#ffb244', '#ffd878'],
        mont=('#2b1622', '#1e0f18', '#120810'),
        pillar=('#361d28', '#23111c', '#522c38', '#140910'),
        ground=('#26161c', '#361f24', '#160c12', '#4a2a2e'),
        baryon=('#e42818', '#ff6e1c', '#ffe052', '#18060a', '#fff6b8'),
        kurama=('#981b14', '#e8401c', '#ffaa2c'),
        isshiki=('#f4f0fa', '#c8c0da', '#8c1e3e', '#261e30', '#ffc838'),
        vig=0.80,
        nube=['#4e1e2c', '#6e2832', '#923832', '#ba4e34', '#de6c3a', '#3b1622'],
    ),
    'dia': dict(
        sky=['#1a4278', '#285894', '#3870b0', '#4e88c8', '#68a2dc', '#88bce8', '#aad2f0', '#cce4f4', '#e8ecd8', '#f6dcba'],
        mont=('#483c54', '#362d42', '#262030'),
        pillar=('#52465e', '#3c3248', '#6c5c78', '#282032'),
        ground=('#3c2c34', '#4d383f', '#2a1e24', '#63484c'),
        baryon=('#e82c1a', '#ff741e', '#ffe458', '#1a070b', '#fff8c4'),
        kurama=('#a42014', '#ec4a1c', '#ffb632'),
        isshiki=('#faf8ff', '#cfcadf', '#8e1e40', '#2b2238', '#ffc430'),
        vig=0.88,
        nube=['#f6f2f6', '#ebe2e8', '#dfd0dc', '#fbf8fa', '#e8d8de', '#c4b8ca'],
    ),
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
CHIMENEA = None
lz = Lienzo()
put, over, disc, glow = lz.put, lz.over, lz.disc, lz.glow

render_cielo(lz, PAL['sky'], SKYM, FASE, aurora_cols=('#ff4824', '#ffb838'))
exporta_sprites_si_aplica(
    lz,
    lambda: dibuja_luna_estandar(lz, 104, 104, 38, halo='#ff9868', base='#fff4e8', sombra='#e0c4be', crater='#be9e98', crater_hi='#d2b4ae'),
    lambda: dibuja_sol_estandar(lz, 104, 104, 22, halo='#ffd488', centro='#fffdf0', borde='#ffb448', rayo='#ffd88c'),
)
render_estrellas(lz, FASE, ANIM, ESTRELLAS, colors=['#ffe4c8', '#ffc4a8', '#d8cce8'])

MX, MY, MR = 322, 66, 38
if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, MX, MY, MR, halo='#ff9868', base='#fff4e8', sombra='#e0c4be', crater='#be9e98', crater_hi='#d2b4ae')
    elif FASE == 'dorado':
        dibuja_sol_estandar(lz, 348, 152, 22, halo='#ff8852', centro='#ffecd0', borde='#ff4e28', rayo='#ff7040')
    else:
        dibuja_sol_estandar(lz, 310, 74, 22, halo='#ffd488', centro='#fffdf0', borde='#ffb448', rayo='#ffd88c')

NUBES_DEF = [
    (82, 26, 158, PAL['nube'][0], 3),
    (248, 38, 150, PAL['nube'][1], 2),
    (412, 22, 138, PAL['nube'][2], 2),
    (168, 102, 168, PAL['nube'][3], 3),
    (368, 114, 132, PAL['nube'][4], 2),
    (524, 192, 112, PAL['nube'][5], 2),
]
render_nubes(lz, NUBES_DEF, NUBES, ANIM)

# 1. Cordilleras oscuras y monolitos flotantes de la Dimensión Otsutsuki (bajando suavemente en x>440 por HUD)
rm = Ruido(911)
M0, M1, M2 = PAL['mont']
for x in range(W):
    ramp = max(0.0, min(1.0, (x - 435) / 80.0))
    dip_h = int(28 * (0.5 - 0.5 * math.cos(math.pi * ramp)))
    ridge = int(174 + 26 * fbm(rm, x * 0.015) + dip_h)
    ridge = min(246, ridge)
    for y in range(ridge, 260):
        t = (y - ridge) / max(1, 260 - ridge)
        put(x, y, mix(M0, M2, min(1.0, t)))

P0, P1, P2, P3 = PAL['pillar']
for px0, pw, top_y, bot_y, slant in (
    (16, 22, 118, 262, -0.08),
    (52, 16, 146, 258, 0.06),
    (256, 14, 154, 252, -0.05),
    (448, 18, 186, 262, 0.05),
):
    for y in range(top_y, bot_y):
        u = (y - top_y) / max(1, bot_y - top_y)
        cx_p = int(px0 + (y - top_y) * slant)
        hw = int(pw * (0.55 + 0.45 * (1.0 - abs(u - 0.5) * 0.4)) / 2)
        if y < top_y + 10:
            hw = max(2, int(hw * ((y - top_y + 2) / 12.0)))
        for dx in range(-hw, hw + 1):
            xx = cx_p + dx
            if 0 <= xx < W:
                c = P2 if dx <= -hw + 2 else (P0 if dx < 1 else (P1 if dx < hw - 1 else P3))
                put(xx, y, c)
    if top_y < 160:
        put(px0, (top_y + bot_y) // 2, PAL['baryon'][2])

# 2. Terreno volcánico del cráter dimensional (y = 250..400)
rx_g = Ruido(947)
ry_g = Ruido(971)
G0, G1, G2, G3 = PAL['ground']
BR_R, BR_O, BR_Y, BR_K, BR_W = PAL['baryon']
for y in range(250, H):
    for x in range(W):
        n2 = 0.5 * fbm(rx_g, x * 0.032) + 0.5 * fbm(ry_g, y * 0.044 + 4.0) + 0.12 * math.sin(x * 0.05) * math.cos(y * 0.06)
        c = G3 if n2 > 0.64 else (G1 if n2 > 0.47 else (G0 if n2 > 0.32 else G2))
        dx_c = (x - 294) / 148.0
        dy_c = (y - 340) / 38.0
        ring = math.sqrt(dx_c * dx_c + dy_c * dy_c)
        if 0.78 <= ring <= 0.86 and dith(x, y, 0.75):
            c = mix(c, G3, 0.55)
        elif 0.86 < ring <= 0.94 and dith(x, y, 0.60):
            c = mix(c, G2, 0.50)
        put(x, y, c)


# 3. Busto espectral feroz de KURAMA rugiendo tras Naruto (x ~ 66..204, y ~ 126..276)
def dibuja_kurama_espectral(cx, base_y):
    K_DK, K_MD, K_HI = PAL['kurama']
    # Busto espectral feroz de Kurama (52x41): hocico afilado de zorro, colmillos afilados y pelaje en llamas
    kurama_spr = [
        'H..................................................H',
        '.HH..............................................HH.',
        '.HDH............................................HDH.',
        '..HDHH........................................HHDH..',
        '..HDDHH......................................HHDDH..',
        '...HDDDH............HHHHHHHHHHHH............HDDDH...',
        '...HMMDDDHH......HHHHHMMMMMMMMHHHHH......HHDDDMMH...',
        '....HMMDDDDHH..HHHMMMMMMMMMMMMMMMMMMHHH..HHDDDDMMH..',
        '....HMMMDDDDHHHHMMMMMMMMMMMMMMMMMMMMMMHHHHDDDDMMMH..',
        '.....HMMMMMMHHHMMMMDDDDDDMMMMDDDDDDMMMMHHHMMMMMMH...',
        '..HH..HMMMMMMMDDDDDDDDDDDMMMMDDDDDDDDDDDMMMMMMMH..HH',
        '.HHHMMHMMMMMDDDDKKKKKKDDDDMMDDDDKKKKKKDDDDMMMMMHMMHH',
        '..HHMMMMMMMDDDDKKWWWWKKDDMMMMDDKKWWWWKKDDDDMMMMMMMHH',
        '...HHMMMMMMMDDDKWEELKWKKDMMMMDKKWKLLEWKDDDDMMMMMMHH.',
        '..HHHMMMMMMMMMMKWEELKWKKKMMMMKKKWKLLEWKMMMMMMMMMMHHH',
        '...HHHMMMMMMMDDKKKKKKKKDDMMMMDDKKKKKKKKDDMMMMMMMHHH.',
        '....HHHMMMMMMDDDDDDDDDDMMHHHHMMDDDDDDDDDDMMMMMMHHH..',
        '.....HHHMMMMMMDDDDDDDDDMMHHHHMMDDDDDDDDDMMMMMMHHH...',
        '......HHHMMMMMMDDDDDDDDKKKKKKKKDDDDDDDDMMMMMMHHH....',
        '.......HHHMMMMMMDDDDDDKKKKKKKKKKDDDDDDMMMMMMHHH.....',
        '........HHHMMMMDDDDDMMKKKKKKKKKKMMDDDDDMMMMHHH......',
        '.........HHMMMDDDDDMMKKKKKKKKKKKKMMDDDDDMMMHH.......',
        '..........HMMMDDDDDKKWKKDDDDDDKKWKKDDDDDMMMH........',
        '...........HMMDDDDDKWWKKDDDDDDKKWWKDDDDDMMH.........',
        '............HMMDDDDKKWWKKKKKKKKWWKKDDDDMMH..........',
        '............FMMMDDDDDDKKKKKKKKKKDDDDDDMMMF..........',
        '...........FFMMMMDDDDDDDDDDDDDDDDDDDDMMMMFF.........',
        '..........FFF.MMMMMMDDDDDDDDDDDDDDMMMMMM.FFF........',
        '.........FFF...MMMMMMMMDDDDDDDDMMMMMMMM...FFF.......',
        '........FFF.....MMMMMMM.MMMMMM.MMMMMMM.....FFF......',
        '.......FF........MMMMM...MMMM...MMMMM........FF.....',
        '......FF..........MMM.....MM.....MMM..........FF....',
        '.....F.............M..............M............F....',
    ]
    sw = len(kurama_spr[0])
    sh = len(kurama_spr)
    assert all(len(r) == sw for r in kurama_spr)
    x0 = cx - sw // 2
    y0 = base_y - 106 - sh // 2
    scale = 2
    for ry, row in enumerate(kurama_spr):
        fade = 1.0 if ry < 24 else max(0.22, 1.0 - (ry - 24) / 10.0)
        for rx, ch in enumerate(row):
            if ch == '.':
                continue
            if ch == 'H':
                col, al = K_HI, 0.72 * fade
            elif ch == 'M':
                col, al = K_MD, 0.56 * fade
            elif ch == 'D':
                col, al = K_DK, 0.54 * fade
            elif ch == 'F':
                col, al = BR_O, 0.42 * fade
            elif ch == 'K':
                col, al = '#180508', 0.74 * fade
            elif ch == 'E':
                col, al = BR_O, 0.94
            elif ch == 'W':
                col, al = BR_W, 0.92
            else:  # 'L' núcleo brillante pupila/colmillo
                col, al = BR_Y, 0.96
            px_b = x0 + rx * scale - sw // 2
            py_b = y0 + ry * scale - sh // 2
            for sy in range(scale):
                for sx in range(scale):
                    over(px_b + sx, py_b + sy, col, al)


# 4. NARUTO UZUMAKI - MODO BARYON (cx=198, by=344) con 9 colas de fusión chakra
def dibuja_naruto_baryon(cx, by):
    # A. 9 Colas Baryon ondeando en abanico fluido tras Naruto (ox=cx-12, oy=by-34)
    ox, oy = cx - 12, by - 34
    colas = [
        (-2.96, 102, -0.32),
        (-2.64, 118, -0.24),
        (-2.32, 130, -0.15),
        (-2.00, 138, -0.07),
        (-1.68, 138, 0.04),
        (-1.34, 132, 0.13),
        (-1.02, 122, 0.21),
        (-0.70, 106, 0.27),
        (-3.22, 86, -0.34),
    ]
    for idx_c, (ang, length, curve) in enumerate(colas):
        steps = length // 2
        for s in range(steps + 1):
            u = s / float(steps)
            a = ang + curve * (u * 1.15) + 0.11 * math.sin(u * 6.5 + idx_c)
            px = int(round(ox + math.cos(a) * (u * length)))
            py = int(round(oy + math.sin(a) * (u * length * 0.82)))
            rad = max(1, int(round(4.4 * (1.0 - 0.70 * u) + 1.2 * math.sin(u * math.pi))))
            for dy in range(-rad, rad + 1):
                for dx in range(-rad, rad + 1):
                    d2 = dx * dx + dy * dy
                    if d2 > rad * rad + 1:
                        continue
                    if u > 0.82:
                        c = BR_W if d2 <= 1 else BR_Y
                    elif d2 <= max(1, (rad - 2) ** 2) and u < 0.58:
                        c = BR_K
                    elif d2 <= max(1, (rad - 1) ** 2):
                        c = BR_R
                    else:
                        c = BR_O if u < 0.72 else BR_Y
                    put(px + dx, py + dy, c)
        if ANIM and idx_c % 2 == 0:
            tip_a = ang + curve * 1.15
            tx = int(round(ox + math.cos(tip_a) * (length * 0.92)))
            ty = int(round(oy + math.sin(tip_a) * (length * 0.92 * 0.82)))
            RUNAS.append([tx, ty])

    # B. Halo oscuro de contraste detras de Naruto para separarlo limpiamente de las colas
    if not ANIM:
        glow(cx, by - 32, 34, BR_K, 0.68)
        glow(cx, by - 32, 22, BR_O, 0.34)

    # C. Manto trasero bifido largo de Modo Baryon ondeando hacia atras-abajo
    for step in range(34):
        u = step / 33.0
        for tail_idx, (dy_off, thick_m) in enumerate(((-4, 5), (8, 6))):
            tx = int(round(cx - 7 - step * 1.25))
            ty = int(round(by - 32 + dy_off + step * 0.70 + math.sin(u * 4.5 + tail_idx) * 2.6))
            th = max(1, int(round(thick_m * (1.0 - 0.55 * u))))
            for dy_t in range(-th, th + 1):
                col = BR_O if abs(dy_t) == th else (BR_K if abs(dy_t) <= 1 and u < 0.6 else BR_R)
                put(tx, ty + dy_t, col)

    # D. Sprite heroico de Naruto Modo Baryon (50 filas x 40 columnas)
    # Cuernos de chakra zorro + pelo rubio + banda Konoha + marcas faciales Baryon/bigotes + manto con magatamas
    spr = [
        '........KKK................KKK..........',
        '........KORK..............KROK..........',
        '.......KORRK......LL......KRROK.........',
        '.......KORKYY....LYYL....YYKROK.........',
        '......KORKYYYY..LYYYYL..YYYYKROK........',
        '......KORKYYYYYYLYYYYL.YYYYYYROK........',
        '.......KKYYYYYYYYYYYYYYYYYYYYKK.........',
        '.......KYYYYYYDDDDDDDDDDYYYYYYK.........',
        '......KYYYYYYDHHHHHHHHHHDYYYYYYK........',
        '......KYYYYYDDHHHHDDHHHHDDYYYYYK........',
        '......KYYYYSDDDDDDDDDDDDDDSYYYYK........',
        '......KYYSSSDDKSSSSSSSKDDSSSYYSK........',
        '......KYSSSDESSSSDDDSSSSEDDSSsSK........',
        '.......SSSDDDSSSSSDDDSSSDDDSSss.........',
        '.......SSsSSKKSSSDDDSSKKSSsSs...........',
        '........SKKSSSSSSSSSSSSSSKKs............',
        '........DDDSSSSDDDDDDSSSSDDD............',
        '.......KOOODDDDDDDDDDDDDDOOOK...........',
        '......KRRRRDDDDGGGGGGDDDRRRRRK..........',
        '.....KRRRRRDDDGGDDDDGGDDDRRRRRK.........',
        '....KRRRRRRDDGGGDDDDGGGDDDRRRRRK........',
        '....KRRRRRRDDGGGGGGGGGGDDDRRRRRRK.......',
        '...KRRRRRRD..DDDDGGGGDDD..DRRRRRRK......',
        '...KRRRRRD...DDKGGGGGKDD...DRRRRRKO.....',
        '..KRRRRRD...KDDDDDDDDDDDK...DRRRROGYO...',
        '..KRRRRD....KDDKDDDDDKDDK....DOOGGGYYO..',
        '..KRRRD.....KDDDDDDDDDDDK.....OOGGYYYO..',
        '..KRRD......KDDKDDDDDKDDK......OOYYYYO..',
        '...KD.......DRRRGGGGGGGRD.......OGGYO...',
        '............DRRRRRRRRRRRD........OOO....',
        '...........KDRRRRRRRRRRRDK..............',
        '..........KDRRRRDDDDDRRRRDK.............',
        '.........KORRRRRDDDDDRRRRROK............',
        '.........KORRRRRDDDDDRRRRROK............',
        '........KORRRRRRDDDDDRRRRRROK...........',
        '........KORRRRR..DDD..RRRRROK...........',
        '.......KORRRRR...DDD...RRRRROK..........',
        '.......KORRRR....DDD....RRRROK..........',
        '......KORRRR.....PPP.....RRRROK.........',
        '......KRRRR......PPP......RRRRK.........',
        '.....KRRR.......PP.PP.......RRRK........',
        '................PP.PP...................',
        '...............PPP.PPP..................',
        '...............PPP.PPP..................',
        '...............PPP.PPP..................',
        '...............DDD.DDD..................',
        '..............KDDK.KDDK.................',
    ]
    cmap = {
        'Y': '#ffd438',
        'L': '#fff6a4',
        'K': BR_K,
        'R': BR_R,
        'O': BR_O,
        'G': BR_Y,
        'D': '#16080d',
        'H': '#d2dce8',
        'S': '#f4c8a6',
        's': '#ce9878',
        'E': '#ffa818',
        'P': '#22141a',
    }
    pinta_sprite(lz, cx, by, spr, cmap)

    # Marcas nitidas de bigotes Baryon en las mejillas de Naruto
    for wy_b in (by - 35, by - 33):
        put(cx - 5, wy_b, '#14060a')
        put(cx - 4, wy_b, '#14060a')
        put(cx + 3, wy_b, '#14060a')
        put(cx + 4, wy_b, '#14060a')

    # Esfera Baryon Rasengan ardiente en la mano adelantada (cx+22, by-24 => 220, 320)
    rx_b, ry_b = cx + 22, by - 24
    if ANIM:
        FAROLES.append([rx_b, ry_b, 16])
        RUNAS.append([rx_b, ry_b])
    else:
        glow(rx_b, ry_b, 15, BR_O, 0.78)
    disc(rx_b, ry_b, 5, BR_R)
    disc(rx_b, ry_b, 3, BR_O)
    disc(rx_b, ry_b, 2, BR_Y)
    put(rx_b, ry_b, BR_W)


# 5. ISSHIKI OTSUTSUKI + RUEDA DHARMACHAKRA + CUBOS DAIKOKUTEN (cx=392, by=344)
def dibuja_isshiki(cx, by):
    W_CL, W_SH, R_TR, DK_C, G_EY = PAL['isshiki']

    # Rueda dorada del Dharma (Dharmachakra, 8 radios) centrada detrás de Isshiki (cx+2, by-62)
    wx_d, wy_d = cx + 2, by - 62
    rad_d = 23
    if not ANIM:
        glow(wx_d, wy_d, 21, G_EY, 0.30)
    for deg in range(0, 360, 4):
        a = math.radians(deg)
        for r_ring in (rad_d - 1, rad_d):
            put(int(round(wx_d + math.cos(a) * r_ring)), int(round(wy_d + math.sin(a) * r_ring)),
                G_EY if deg % 45 != 0 else '#fff2a8')
    for sp in range(8):
        a = sp * (math.pi / 4.0)
        for step in range(4, rad_d + 6):
            put(int(round(wx_d + math.cos(a) * step)), int(round(wy_d + math.sin(a) * step)),
                '#fff0a4' if step > rad_d else G_EY)
    disc(wx_d, wy_d, 3, G_EY)

    # Sprite grande y nitido de Isshiki Otsutsuki (45 filas x 32 cols: cuerno curvo asimetrico, ojo Dharmagan dorado + Byakugan, abrigo blanco/vino + magatamas)
    spr = [
        '....................KKKKKK......',
        '................KKKKKKKK........',
        '.............KKKKK..............',
        '...........KKKPPPPPP............',
        '..........KPPPPPPPPPP...........',
        '.........KPPPPPPPPPPPP..........',
        '.........PPPKKPPPPPPPP..........',
        '........PPPPKKPPPPPPPPP.........',
        '........PPPGGPPPLLLPPPP.........',
        '........PPPSSPPPSSSPPPP.........',
        '.........PPPPPPPPPPPPP..........',
        '.........PPPPSSPPPPPP...........',
        '..........PPPPPPPPPP............',
        '.........VVVWWWWWWVVV...........',
        '........VVVWWWWWWWWVVV..........',
        '.......VVWWWWWPDDPWWWVV.........',
        '......VVWWWWWPPDDPPWWWVV........',
        '.....KVVWWWWWWPPPPWWWWWWVV......',
        '....KPWWWWWWVVWWWWWWVVWWWWV.....',
        '...KPPWWWWWWVWWWWWWWWVWWWWV.....',
        '...KP.WWWWWWVWWWWWWWWVWWWWV.....',
        '......WWWWWWVKWWWWWWKVWWWW......',
        '......WWWWWWVWWWWWWWWVWWWW......',
        '.......WWWWWWVVVVVVVVWWWW.......',
        '.......DDDDDDDDDDDDDDDDDD.......',
        '.......DDDDDDDDDDDDDDDDDD.......',
        '.......DDDDDDDDDDDDDDDDDD.......',
        '.......WWWWWWWVVWWVVWWWW........',
        '......WWWWWWWWVVWWVVWWWWW.......',
        '......WWWWWWWWVVWWVVWWWWW.......',
        '......WWWWWWW.VV..VV.WWWW.......',
        '.....WWWHHHWW........WWWHWW.....',
        '.....WWWHHWW..........WWHWW.....',
        '.....WWWHWW............WHWW.....',
        '......DDDD..............DDDD....',
        '......DDDD..............DDDD....',
        '......DDDD..............DDDD....',
        '......DDDD..............DDDD....',
        '......DDDD..............DDDD....',
        '......DDDD..............DDDD....',
        '.....KKKKKK............KKKKKK...',
        '.....KKKKKK............KKKKKK...',
    ]
    cmap = {
        'K': '#120e1a',
        'P': '#e0daee',
        'S': '#b4acc6',
        'G': G_EY,
        'L': '#f2eeff',
        'V': R_TR,
        'W': W_CL,
        'H': W_SH,
        'D': DK_C,
    }
    pinta_sprite(lz, cx, by, spr, cmap)
    if ANIM:
        RUNAS.append([cx - 3, by - 35])

    # Cubos oscuros Daikokuten y varas negras flotando frente a Isshiki
    for bx, by_c, s_c in ((322, by - 64, 7), (290, by - 50, 5), (346, by - 78, 4)):
        for dy in range(-s_c, s_c + 1):
            for dx in range(-s_c, s_c + 1):
                col = '#383048' if (dx < -s_c + 2 or dy < -s_c + 2) else ('#100d18' if dx > s_c - 2 or dy > s_c - 2 else '#1c1728')
                put(bx + dx, by_c + dy, col)
        if ANIM:
            RUNAS.append([bx, by_c])
    # Estacas Sukunahikona biseladas clavadas en el suelo bajo Isshiki
    for rx0, ry0, dx_s, h_r in ((346, by - 1, -1, 11), (362, by + 2, -1, 13), (376, by + 1, 1, 9)):
        for k in range(h_r):
            px_r = rx0 + (k * dx_s) // 2
            py_r = ry0 - k
            put(px_r, py_r, '#14101c')
            put(px_r + 1, py_r, '#6e6488' if k > h_r - 3 else '#3a324c')
        over(rx0, ry0 + 1, BR_R, 0.55)


dibuja_kurama_espectral(136, 286)
dibuja_naruto_baryon(198, 344)
dibuja_isshiki(392, 344)

for fx, fy in ((152, 350), (226, 344), (264, 342), (344, 346)):
    if ANIM:
        RUNAS.append([fx, fy])
    else:
        glow(fx, fy, 4, BR_O, 0.50)

aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(
    W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
    chimenea=CHIMENEA, destellos=DESTELLOS, luna=[MX, MY, MR],
)
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
