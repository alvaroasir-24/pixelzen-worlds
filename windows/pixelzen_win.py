#!/usr/bin/env python3
"""PixelZen Mushoku para Windows (standalone).
Soporta:
  - Modo fondo de escritorio Windows (SystemParametersInfoW) con transición suave cada pocos segundos
    (requiere Pillow para mezclar capas en tiempo real; sin Pillow alterna entre día/dorado/noche).
  - Modo animado tras los iconos de Windows (Win32 WorkerW + Tkinter) o vista previa local.

Uso:
  python pixelzen_win.py --tema fittoa --90m
  python pixelzen_win.py --tema continente-demoniaco --real
  python pixelzen_win.py --tema continente-demoniaco --demo --animado
"""
import argparse
import ctypes
import datetime
import json
import math
import os
import sys
import tempfile
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
TEMAS_DIR = os.path.join(AQUI, 'lively', 'temas')


def listar_temas():
    if not os.path.isdir(TEMAS_DIR):
        return []
    return sorted(d for d in os.listdir(TEMAS_DIR) if os.path.isdir(os.path.join(TEMAS_DIR, d, 'images')))


def elevacion_solar(fecha, lat=40.4, lon=-3.7):
    rad = math.pi / 180.0
    ts = fecha.timestamp()
    n = ts / 86400.0 + 2440587.5 - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360.0
    g = ((357.528 + 0.9856003 * n) % 360.0) * rad
    lam = (L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)) * rad
    eps = (23.439 - 0.0000004 * n) * rad
    ra = math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))
    dec = math.asin(math.sin(eps) * Math.sin(lam))
    gmst = (18.697374558 + 24.06570982441908 * n) % 24.0
    Hh = (gmst * 15.0 + lon) * rad - ra
    Hh = math.atan2(math.sin(Hh), math.cos(Hh))
    phi = lat * rad
    e = math.asin(math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.cos(Hh))
    A = math.atan2(math.sin(Hh), math.cos(Hh) * math.sin(phi) - math.tan(dec) * math.cos(phi)) + math.pi
    c0 = max(-1.0, min(1.0, -math.tan(phi) * math.tan(dec)))
    return {'e': e / rad, 'az': (A / rad) % 360.0, 'H': Hh, 'H0': math.acos(c0)}


def suave(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def set_windows_wallpaper(ruta_img):
    if sys.platform != 'win32':
        print(f'[simulación Linux] wallpaper -> {ruta_img}')
        return
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, os.path.abspath(ruta_img), SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )


def render_frame_pillow(tema_dir, fecha, out_path, scale=3):
    from PIL import Image

    img_dir = os.path.join(tema_dir, 'images')
    s = elevacion_solar(fecha)
    wA = 0.0 if s['e'] <= -14 else (1.0 if s['e'] >= 0 else suave((s['e'] + 14) / 14))
    wB = 0.0 if s['e'] <= 0 else (1.0 if s['e'] >= 16 else suave(s['e'] / 16))
    solX = max(30, min(610, 320 + (s['az'] - 180) * 2.3))
    solY = max(24, 272 - max(s['e'], -9) * 3.6)
    solOp = max(0.0, min(1.0, (s['e'] + 6) / 6))

    f = -1.0
    if s['H'] >= s['H0']:
        f = (s['H'] - s['H0']) / (2 * math.pi - 2 * s['H0'])
    elif s['H'] <= -s['H0']:
        f = (s['H'] + 2 * math.pi - s['H0']) / (2 * math.pi - 2 * s['H0'])
    lunaX = 110 + f * 420 if f >= 0 else 320
    lunaY = 272 - 56 * math.sin(math.pi * f) * 3.6 if f >= 0 else 300
    lunaOp = max(0.0, min(1.0, (-s['e'] - 1) / 5)) if f >= 0 else 0.0

    def blend_3(prefix):
        im_n = Image.open(os.path.join(img_dir, f'{prefix}-noche.png')).convert('RGBA')
        im_g = Image.open(os.path.join(img_dir, f'{prefix}-dorado.png')).convert('RGBA')
        im_d = Image.open(os.path.join(img_dir, f'{prefix}-dia.png')).convert('RGBA')
        res = Image.blend(im_n, im_g, wA) if wA > 0 else im_n
        if wB > 0:
            res = Image.blend(res, im_d, wB)
        return res

    base = blend_3('cielo')
    if solOp > 0.01:
        sol_im = Image.open(os.path.join(img_dir, 'sol.png')).convert('RGBA')
        if solOp < 0.99:
            a = sol_im.split()[3].point(lambda p: int(p * solOp))
            sol_im.putalpha(a)
        base.alpha_composite(sol_im, (int(solX - 104), int(solY - 104)))
    if lunaOp > 0.01:
        luna_im = Image.open(os.path.join(img_dir, 'luna.png')).convert('RGBA')
        if lunaOp < 0.99:
            a = luna_im.split()[3].point(lambda p: int(p * lunaOp))
            luna_im.putalpha(a)
        base.alpha_composite(luna_im, (int(lunaX - 104), int(lunaY - 104)))

    escena = blend_3('escena')
    base.alpha_composite(escena)
    out_im = base.resize((640 * scale, 400 * scale), Image.Resampling.NEAREST).convert('RGB')
    out_im.save(out_path, 'PNG')


def modo_wallpaper(args, tema_dir):
    try:
        import PIL  # noqa: F401
        tiene_pil = True
    except ImportError:
        tiene_pil = False
        print('Aviso: Pillow no instalado (pip install pillow). Usando vistas estáticas por fase.')

    ahora = datetime.datetime.now()
    hora_ini = ahora.hour + ahora.minute / 60.0 + ahora.second / 3600.0
    t0 = time.monotonic()
    tmp_png = os.path.join(tempfile.gettempdir(), f'pixelzen_{args.tema}.png')
    intervalo = 2.0 if args.demo else (5.0 if args.c90 else 60.0)

    print(f'PixelZen Windows activo | tema={args.tema} | ciclo={"90m" if args.c90 else ("demo90s" if args.demo else "real")}')
    try:
        while True:
            d = datetime.datetime.now()
            if args.c90:
                h = (hora_ini + ((time.monotonic() - t0) / 5400.0) * 24.0) % 24.0
                d = d.replace(hour=int(h), minute=int((h % 1) * 60), second=int((h * 3600) % 60), microsecond=0)
            elif args.demo:
                h = ((time.monotonic() - t0) % 90.0) / 90.0 * 24.0
                d = d.replace(hour=int(h), minute=int((h % 1) * 60), second=int((h * 3600) % 60), microsecond=0)

            if tiene_pil:
                render_frame_pillow(tema_dir, d, tmp_png)
                set_windows_wallpaper(tmp_png)
            else:
                el = elevacion_solar(d)['e']
                fase = 'noche' if el < -4 else ('dorado' if el < 8 else 'dia')
                prev = os.path.join(os.path.dirname(AQUI), 'escenas', args.tema, 'preview', fase, 'v3.png')
                if not os.path.isfile(prev):
                    prev = os.path.join(tema_dir, 'fondo.png')
                set_windows_wallpaper(prev)

            time.sleep(intervalo)
    except KeyboardInterrupt:
        print('\nPixelZen detenido.')


def main():
    p = argparse.ArgumentParser(description='PixelZen Mushoku para Windows')
    p.add_argument('--tema', default='fittoa', help='Tema a usar (fittoa | continente-demoniaco | hunter-x-hunter | black-clover | spiderman-miles-morales)')
    p.add_argument('--90m', dest='c90', action='store_true', help='Ciclo completo de 24 horas en 90 minutos')
    p.add_argument('--demo', action='store_true', help='Demo rápida de 24 horas en 90 segundos')
    p.add_argument('--real', action='store_true', help='Seguir la hora real del reloj')
    p.add_argument('--listar', action='store_true', help='Listar temas disponibles')
    args = p.parse_args()

    if args.listar:
        print('Temas disponibles:', ', '.join(listar_temas()))
        return

    tema_dir = os.path.join(TEMAS_DIR, args.tema)
    if not os.path.isdir(tema_dir):
        print(f'Error: tema "{args.tema}" no encontrado en {TEMAS_DIR}', file=sys.stderr)
        sys.exit(2)

    modo_wallpaper(args, tema_dir)


if __name__ == '__main__':
    main()
