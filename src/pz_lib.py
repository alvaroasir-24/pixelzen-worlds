#!/usr/bin/env python3
"""PixelZen Mushoku - librería compartida de dibujo pixel art en Python puro (sin dependencias externas)."""
import json
import math
import os
import pickle
import random
import struct
import sys
import zlib

W, H, HOR, SCALE = 640, 400, 280, 3
ZX0, ZX1, ZY0, ZY1 = 478, 632, 10, 215
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def hx(c):
    """Convierte '#rrggbb' o tupla RGB a tupla (r, g, b)."""
    if isinstance(c, tuple):
        return c
    c = c.lstrip('#')
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))


def mix(a, b, t):
    """Mezcla lineal entre dos colores RGB."""
    a, b = hx(a), hx(b)
    return (
        int(a[0] * (1 - t) + b[0] * t),
        int(a[1] * (1 - t) + b[1] * t),
        int(a[2] * (1 - t) + b[2] * t),
    )


def dith(x, y, t):
    """Tramado ordenado Bayer 4x4."""
    return (BAYER[y % 4][x % 4] + 0.5) / 16 < t


def en_zona(x, y, m=6):
    """Indica si (x, y) cae en la zona reservada para el panel HUD derecho."""
    return ZX0 - m <= x <= ZX1 + m and ZY0 - m <= y <= ZY1 + m


class Ruido:
    """Ruido 1D suave por interpolación cúbica."""

    def __init__(self, seed, n=96):
        r = random.Random(seed)
        self.v = [r.random() for _ in range(n)]

    def __call__(self, x):
        i = int(x)
        f = x - i
        f = f * f * (3 - 2 * f)
        a, b = self.v[i % len(self.v)], self.v[(i + 1) % len(self.v)]
        return a + (b - a) * f


def fbm(r, x):
    """Ruido fractal de 3 octavas."""
    return 0.55 * r(x) + 0.28 * r(x * 2.1 + 7) + 0.17 * r(x * 4.3 + 3)


class Lienzo:
    """Lienzo pixel art 640x400 con primitivas básicas y exportación."""

    def __init__(self, w=W, h=H):
        self.w = w
        self.h = h
        self.px = [[(0, 0, 0)] * w for _ in range(h)]

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = hx(c)

    def over(self, x, y, c, a):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = mix(self.px[y][x], c, a)

    def get(self, x, y):
        return self.px[y][x] if 0 <= x < self.w and 0 <= y < self.h else (0, 0, 0)

    def disc(self, cx, cy, r, c, plot=None):
        fn = plot or self.put
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                if x * x + y * y <= r * r + r // 2:
                    fn(cx + x, cy + y, c)

    def glow(self, cx, cy, r, c, fuerza=0.7):
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                d = math.hypot(x, y)
                if d < r and dith(cx + x, cy + y, ((1 - d / r) ** 2) * fuerza):
                    self.over(cx + x, cy + y, c, 0.75)

    def rama(self, pts, r0, r1, col, hi):
        n = sum(max(abs(b[0] - a[0]), abs(b[1] - a[1])) for a, b in zip(pts, pts[1:])) or 1
        i = 0
        for a, b in zip(pts, pts[1:]):
            m = max(abs(b[0] - a[0]), abs(b[1] - a[1])) or 1
            for k in range(m + 1):
                r = r0 + (r1 - r0) * (i / n)
                i += 1
                cx = a[0] + (b[0] - a[0]) * k // m
                cy = a[1] + (b[1] - a[1]) * k // m
                self.disc(cx, cy, max(1, round(r)), col)
                if r > 2:
                    self.put(cx - round(r) + 1, cy - round(r) + 1, hi)
            i -= 1


def render_cielo(lz, sky_pal, skym, fase, hor=HOR, aurora_cols=('#72d8d0', '#a896e4')):
    """Pinta el degradado del cielo y una aurora sutil nocturna."""
    for y in range(hor):
        t = (y / hor) ** 1.45 * (len(sky_pal) - 1)
        i = int(t)
        f = t - i
        for x in range(lz.w):
            if skym == 'negro':
                lz.put(x, y, (0, 0, 0))
            elif skym == 'blanco':
                lz.put(x, y, (255, 255, 255))
            else:
                lz.put(x, y, sky_pal[min(i + 1, len(sky_pal) - 1)] if dith(x, y, f) else sky_pal[i])

    if fase == 'noche' and skym == 'normal':
        rl = Ruido(5)
        for x in range(lz.w):
            for y in range(0, 195):
                d = abs(y - (112 + (x - 50) * -0.40)) / 36.0
                if d < 1 and not en_zona(x, y, 22):
                    dens = (1 - d) ** 2 * (0.4 + 0.6 * rl(x * 0.06 + y * 0.05))
                    if dith(x, y, dens * 0.30):
                        col_aur = aurora_cols[0] if rl(x * 0.03 + 12) > 0.56 else aurora_cols[1]
                        lz.over(x, y, col_aur, 0.42)
                    if random.random() < dens * 0.016:
                        lz.put(x, y, '#e8f6ff')

    if os.environ.get('PZ_SKYONLY'):
        pickle.dump([r[:] for r in lz.px], open(os.environ['PZ_SKYONLY'], 'wb'))
        sys.exit(0)


def render_estrellas(lz, fase, anim, stars_out, count=430, hor=HOR, colors=None):
    """Genera estrellas o las registra en stars_out para animación."""
    cols = colors or ['#cfe8ff', '#a8d6ec', '#8590cc']
    for _ in range(count):
        x, y = random.randrange(lz.w), random.randrange(int(hor * 0.62))
        if en_zona(x, y) and random.random() < 0.85:
            continue
        b = random.random()
        col_e = '#f6efe0' if b > 0.7 else random.choice(cols)
        if anim:
            stars_out.append([x, y, col_e, 1 if (b > 0.965 and not en_zona(x, y)) else 0])
            continue
        if fase != 'noche':
            continue
        lz.put(x, y, col_e)
        if b > 0.965 and not en_zona(x, y):
            for k in (1, 2):
                for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
                    lz.over(x + dx, y + dy, '#bfe6ff', 0.8 / k)


def dibuja_luna_estandar(lz, mx, my, mr=46, halo='#9ed4e2', base='#f8f2e0', sombra='#e2d8be', crater='#ccc4a8', crater_hi='#ded6bc'):
    """Dibuja la luna con cráteres y halo dithered."""
    for y in range(my - 110, my + 110):
        for x in range(mx - 110, mx + 110):
            d = math.hypot(x - mx, y - my)
            if mr < d < 104 and 0 <= y < HOR and dith(x, y, ((104 - d) / (104 - mr)) ** 2.4 * 0.40):
                lz.over(x, y, halo, 0.82)
    rm = Ruido(9)
    for y in range(my - mr, my + mr + 1):
        for x in range(mx - mr, mx + mr + 1):
            d = math.hypot(x - mx, y - my)
            if d <= mr:
                c = mix(base, sombra, min(1, max(0, ((x - mx) * 0.55 + (y - my) * 0.8) / mr * 0.5 + 0.2)))
                n = rm(x * 0.09) * 0.6 + rm(y * 0.11 + 40) * 0.4
                if n > 0.56 and d < mr - 3:
                    c = mix(c, crater, 0.55 if n > 0.62 else (0.3 if dith(x, y, 0.5) else 0.0))
                if d > mr - 3:
                    c = mix(c, '#fff9ea', 0.5) if (x - mx) < 0 else mix(c, crater, 0.4)
                lz.put(x, y, c)
    for cx, cy, r in ((-17, -14, 7), (11, -22, 5), (18, 15, 9), (-21, 13, 5), (-3, 25, 4), (28, -6, 4), (-8, 2, 3), (4, 8, 2)):
        lz.disc(mx + cx, my + cy, r, crater)
        lz.disc(mx + cx - 1, my + cy - 1, max(1, r - 2), crater_hi)
        for k in range(-r, r):
            if dith(k, r, 0.5):
                lz.over(mx + cx + k, my + cy + r, '#fff8e2', 0.5)


def dibuja_sol_estandar(lz, cx, cy, r=24, halo='#ffd890', centro='#fffbe0', borde='#ffcf60', rayo='#ffe08a'):
    """Dibuja el sol con halo y rayos pixel art."""
    for y in range(cy - 104, cy + 104):
        for x in range(cx - 104, cx + 104):
            d = math.hypot(x - cx, y - cy)
            if r < d < 100 and dith(x, y, ((100 - d) / (100 - r)) ** 2.2 * 0.55):
                lz.over(x, y, halo, 0.9)
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                c = mix(centro, borde, (d / r) ** 1.4)
                if d > r - 2:
                    c = '#ffb040' if dith(x, y, 0.6) else borde
                lz.put(x, y, c)
    for k in range(16):
        a = k / 16 * 2 * math.pi
        for t in range(r + 5, r + (16 if k % 2 == 0 else 11)):
            if t % 2 == 0:
                lz.put(round(cx + math.cos(a) * t), round(cy + math.sin(a) * t), rayo)


def exporta_sprites_si_aplica(lz, fn_luna, fn_sol):
    """Si PZ_SPRITES está definido, genera sprites sobre fondo negro y blanco para matte."""
    if not os.environ.get('PZ_SPRITES'):
        return
    res = {}
    for nombre_, fn_ in (('luna', fn_luna), ('sol', fn_sol)):
        bufs = []
        for fondo_ in ((0, 0, 0), (255, 255, 255)):
            for yy_ in range(208):
                for xx_ in range(208):
                    lz.px[yy_][xx_] = fondo_
            fn_()
            bufs.append([row_[:208] for row_ in lz.px[:208]])
        res[nombre_] = bufs
    pickle.dump(res, open(os.environ['PZ_SPRITES'], 'wb'))
    sys.exit(0)


def _forma_nube(cx, cy, w, col, gr):
    """Genera un sprite RGBA de nube pixel art volumétrica con cúpulas asimétricas, luces y sombras."""
    h = max(14, min(30, gr * 8 + 6))
    buf = [[(0, 0, 0, 0)] * w for _ in range(h)]
    r_c, g_c, b_c = hx(col)
    hi_r, hi_g, hi_b = mix(col, '#ffffff', 0.38)
    sh_r, sh_g, sh_b = mix(col, '#0c0c20', 0.26)

    rng = random.Random(cx * 41 + w * 17 + gr)
    n_puffs = max(4, min(7, w // 24))
    puffs = []
    # Lóbulo dominante descentrado para evitar una cápsula simétrica plana
    peak_t = rng.uniform(0.34, 0.66)
    for idx in range(n_puffs):
        t = (idx + 0.5) / n_puffs
        px_c = w * (0.13 + 0.74 * t) + rng.uniform(-w * 0.035, w * 0.035)
        dist_peak = abs(t - peak_t)
        dome = max(0.0, 1.0 - dist_peak * 1.85)
        rx = max(10.0, w * (0.12 + 0.11 * dome) + rng.uniform(-2.0, 3.0))
        ry = max(5.0, h * (0.24 + 0.48 * (dome ** 1.15)) + rng.uniform(-1.5, 2.5))
        base_lift = rng.uniform(0.0, 2.5) if idx not in (0, n_puffs - 1) else 0.0
        py_c = h - 3.5 - ry * 0.68 - base_lift
        puffs.append((px_c, py_c, rx, ry))

    for yy in range(h):
        for xx in range(w):
            if yy >= h - 1:
                continue
            d_min = 9.0
            best_dy = 0.0
            for px_c, py_c, rx, ry in puffs:
                dy_s = (yy - py_c) / ry
                if yy > h - 5:
                    dy_s *= 1.55
                d = ((xx - px_c) / rx) ** 2 + dy_s ** 2
                if d < d_min:
                    d_min = d
                    best_dy = dy_s
            if d_min <= 0.96:
                edge_fade = 1.0 - abs(xx - w / 2) / (w / 2 + 1)
                if d_min > 0.72 and not dith(cx - w // 2 + xx, cy + yy, (1.0 - d_min) * 3.4 + edge_fade * 0.30):
                    continue
                if best_dy < -0.42 or (d_min > 0.54 and best_dy < 0.05):
                    buf[yy][xx] = (hi_r, hi_g, hi_b, 226)
                elif yy >= h - 5 or best_dy > 0.48:
                    buf[yy][xx] = (sh_r, sh_g, sh_b, 210)
                else:
                    buf[yy][xx] = (r_c, g_c, b_c, 222)
    return buf, h


def render_nubes(lz, nubes_def, nubes_out, anim):
    """Pinta nubes en modo estático o las registra para spritesheet animado."""
    for cx, cy, w, col, grosor in nubes_def:
        if anim:
            nubes_out.append([cx, cy, w, col, grosor])
            continue
        buf, h = _forma_nube(cx, cy, w, col, grosor)
        x0 = cx - w // 2
        for yy in range(h):
            for xx in range(w):
                r_, g_, b_, a_ = buf[yy][xx]
                if a_ > 0:
                    lz.over(x0 + xx, cy + yy, (r_, g_, b_), a_ / 255.0)


def render_lago(lz, agua_col, olas_pal, destellos_out, anim, mx=352, hor=HOR, reflejo_cols=('#f4e8ce', '#8ac6cc'), reflejo_astro=True):
    """Refleja el paisaje superior sobre el agua y añade oleaje y destellos."""
    copia = [list(r) for r in lz.px[:hor + 1]]
    for y in range(hor + 1, lz.h):
        d = y - hor
        src = hor - 1 - int(d * 1.12)
        for x in range(lz.w):
            ond = int((1.0 + d * 0.018) * math.sin(d * 0.48 + x * 0.028)) + (1 if (d // 4) % 2 else -1)
            sx = (x + ond) % lz.w
            k = max(0.14, 0.70 - d * 0.0046)
            lz.put(x, y, mix(agua_col, copia[max(src, 0)][sx], k))
    # Brillo sutil en la línea de horizonte del agua
    for x in range(lz.w):
        if dith(x, hor + 1, 0.45):
            lz.over(x, hor + 1, olas_pal[0], 0.25)
    rr = random.Random(21)
    for y in range(hor + 2, lz.h, 3):
        d = y - hor
        for _ in range(24):
            x = rr.randrange(lz.w)
            l = rr.randint(3, 8 + d // 8)
            c = olas_pal[0] if d < 38 else (olas_pal[1] if d < 80 else olas_pal[2])
            for k in range(l):
                if k < 2 or dith(x + k, y, 0.78 - (k / l) * 0.35):
                    lz.over(x + k, y, c, max(0.18, 0.50 - d * 0.0022))
    if reflejo_astro:
        for d in (range(8, 120, 3) if not anim else ()):
            ww = int(46 - d * 0.30)
            if ww < 3:
                break
            for x in range(mx - ww // 2, mx + ww // 2):
                if rr.random() < 0.55 - d * 0.003:
                    lz.put(x, hor + d, reflejo_cols[0] if d < 50 else reflejo_cols[1])
        for _ in range(220):
            x, y = rr.randrange(300, 410), hor + rr.randrange(6, 100)
            if anim:
                destellos_out.append([x, y])
                continue
            lz.put(x, y, '#fff6e0')
            lz.over(x + 1, y, '#fff6e0', 0.6)


def aplica_vineta(lz, vig):
    """Aplica viñeta dithered sutil en las esquinas."""
    for y in range(lz.h):
        for x in range(lz.w):
            d = math.hypot((x - lz.w / 2) / (lz.w / 2), (y - lz.h / 2) / (lz.h / 2))
            if d > 0.82 and dith(x, y, (d - 0.82) * 0.95):
                r, g, b = lz.px[y][x]
                lz.px[y][x] = (int(r * vig), int(g * vig), int(b * min(1.0, vig + 0.06)))


def guarda_png_escalado(ruta, buf, w=W, h=H, scale=SCALE):
    """Guarda el buffer RGB escalado por entero (nearest-neighbor) como PNG."""
    raw = bytearray()
    for y in range(h):
        fila = b''.join(bytes(buf[y][x]) * scale for x in range(w))
        raw += (b'\x00' + fila) * scale

    def ch(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)

    with open(ruta, 'wb') as f:
        f.write(
            b'\x89PNG\r\n\x1a\n'
            + ch(b'IHDR', struct.pack('>IIBBBBB', w * scale, h * scale, 8, 2, 0, 0, 0))
            + ch(b'IDAT', zlib.compress(bytes(raw), 9))
            + ch(b'IEND', b'')
        )


def exporta_salida(lz, out, fase, anim, nubes_out, datos):
    """Exporta las capas animadas (nubes + datos.js + PZ_DUMP) o el PNG estático v3.png."""
    os.makedirs(out, exist_ok=True)
    if anim:
        filas_n, sprites, y0 = [], [], 0
        for cx, cy, w, col, gr in nubes_out:
            buf, h = _forma_nube(cx, cy, w, col, gr)
            sprites.append([cx - w // 2, cy, w, h, y0])
            filas_n += buf
            y0 += h
        sw = max((n[2] for n in nubes_out), default=1)
        raw = bytearray()
        for fila in filas_n:
            fila = list(fila) + [(0, 0, 0, 0)] * (sw - len(fila))
            raw += b'\x00' + b''.join(bytes(p) for p in fila)

        def chk(t, d):
            c = struct.pack('>I', len(d)) + t + d
            return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)

        with open(os.path.join(out, f'nubes-{fase}.png'), 'wb') as f:
            f.write(
                b'\x89PNG\r\n\x1a\n'
                + chk(b'IHDR', struct.pack('>IIBBBBB', sw, len(filas_n), 8, 6, 0, 0, 0))
                + chk(b'IDAT', zlib.compress(bytes(raw), 9))
                + chk(b'IEND', b'')
            )
        datos_full = dict(datos, nubes=sprites, nubes_w=sw)
        with open(os.path.join(out, 'datos.js'), 'w') as f:
            f.write('.pragma library\nvar D = ' + json.dumps(datos_full) + ';\n')
        if os.environ.get('PZ_DUMP'):
            pickle.dump([r_[:] for r_ in lz.px], open(os.environ['PZ_DUMP'], 'wb'))
        return

    guarda_png_escalado(os.path.join(out, 'v3.png'), lz.px, lz.w, lz.h, SCALE)


def pinta_sprite(lz, cx, by, spr, cmap, off_x=0):
    """Pinta una matriz pixel-art centrada en cx+off_x apoyando la fila inferior exactamente en y=by."""
    sw = len(spr[0])
    assert all(len(r) == sw for r in spr), f"Sprite filas desiguales: {[len(r) for r in spr]}"
    x0 = cx - sw // 2 + off_x
    y0 = by - len(spr) + 1
    for ry, row in enumerate(spr):
        for rx, ch in enumerate(row):
            col = cmap.get(ch)
            if col is not None:
                lz.put(x0 + rx, y0 + ry, col)
    return x0, y0

