#!/usr/bin/env python3
"""PixelZen Worlds para Windows (standalone + multimonitor + servidor HUD).
Soporta:
  - Modo fondo de escritorio Windows por monitor (IDesktopWallpaper COM + desactiva Spotlight):
    * 1 monitor: aplica el tema principal en el monitor principal del sistema.
    * 2 monitores: monitor principal = escena base; 2.º monitor = continuación de la historia.
  - Renderizado suave con Pillow o vistas previas por fase solar (dia/dorado/noche).
  - Servidor local HTML5 (--servidor) con telemetría real en /api/stats.

Uso:
  python pixelzen_win.py --tema fittoa --monitores 2 --90m
  python pixelzen_win.py --tema spiderman-miles-morales --monitores 2 --real
  python pixelzen_win.py --servidor --puerto 8765
"""
import argparse
import ctypes
import datetime
import http.server
import json
import math
import os
import subprocess
import sys
import tempfile
import time
import urllib.parse

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
LIVELY_DIR = os.path.join(AQUI, 'lively')
_TEMAS_LIVELY = os.path.join(LIVELY_DIR, 'temas')
_TEMAS_LEGACY = os.path.join(AQUI, 'temas')
_TEMAS_DOCS = os.path.join(os.path.dirname(AQUI), 'docs', 'temas')
TEMAS_DIR = (
    _TEMAS_LIVELY if os.path.isdir(_TEMAS_LIVELY)
    else (_TEMAS_LEGACY if os.path.isdir(_TEMAS_LEGACY)
          else (_TEMAS_DOCS if os.path.isdir(_TEMAS_DOCS) else _TEMAS_LIVELY))
)
if os.path.isdir(_TEMAS_LIVELY) or os.path.isdir(_TEMAS_LEGACY):
    _DATA_DIR = os.path.join(os.environ.get('LOCALAPPDATA', AQUI), 'PixelZenWorlds')
    os.makedirs(_DATA_DIR, exist_ok=True)
    CONFIG_PATH = os.path.join(_DATA_DIR, 'config.json')
else:
    CONFIG_PATH = os.path.join(AQUI, 'config.json')

sys.path.insert(0, AQUI)
import datos_win  # noqa: E402


def listar_temas():
    if not os.path.isdir(TEMAS_DIR):
        return []
    return sorted(d for d in os.listdir(TEMAS_DIR) if os.path.isdir(os.path.join(TEMAS_DIR, d, 'images')))


def cargar_config():
    defecto = {
        'tema': 'fittoa',
        'monitores': 2,
        'modo': '90m',
        'horaFija': 21.5,
        'fps': 8,
        'hud': True,
        'stats': {
            'tiempo': True,
            'clima': True,
            'sistema': True,
            'gpu': True,
            'red': True,
            'audio': True,
            'dev': True,
            'foco': True,
            'grimorio': True,
        },
    }
    if os.path.isfile(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
            defecto.update(data)
        except Exception:
            pass
    return defecto


def guardar_config(cfg):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def elevacion_solar(fecha, lat=40.4, lon=-3.7):
    rad = math.pi / 180.0
    ts = fecha.timestamp()
    n = ts / 86400.0 + 2440587.5 - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360.0
    g = ((357.528 + 0.9856003 * n) % 360.0) * rad
    lam = (L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)) * rad
    eps = (23.439 - 0.0000004 * n) * rad
    ra = math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))
    dec = math.asin(math.sin(eps) * math.sin(lam))
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


def _ps_oculto(script):
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.run(
        ['powershell', '-NoProfile', '-NonInteractive', '-Command', script],
        check=True,
        startupinfo=si,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def set_windows_wallpapers(ruta_prim, ruta_sec=None):
    """Aplica fondo principal al monitor primario del sistema y continuación al secundario."""
    ruta_prim = os.path.abspath(ruta_prim)
    ruta_sec = os.path.abspath(ruta_sec) if ruta_sec else None
    if sys.platform != 'win32':
        print(f'[simulación Linux] monitor principal -> {ruta_prim}')
        if ruta_sec:
            print(f'[simulación Linux] monitor secundario -> {ruta_sec}')
        return

    prim_esc = ruta_prim.replace("'", "''")
    sec_esc = (ruta_sec or ruta_prim).replace("'", "''")
    mismo = 'true' if not ruta_sec else 'false'

    ps_script = f"""
Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Wallpapers' -Name 'BackgroundType' -Value 0 -Type DWord -ErrorAction SilentlyContinue
$code = @'
using System;
using System.Runtime.InteropServices;

[StructLayout(LayoutKind.Sequential)]
public struct RECT {{ public int Left, Top, Right, Bottom; }}

[ComImport, Guid("B92B56A9-8B55-4E14-9A89-0199BBB6F93B"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IDesktopWallpaper {{
    void SetWallpaper([MarshalAs(UnmanagedType.LPWStr)] string monitorID, [MarshalAs(UnmanagedType.LPWStr)] string wallpaper);
    [return: MarshalAs(UnmanagedType.LPWStr)]
    string GetWallpaper([MarshalAs(UnmanagedType.LPWStr)] string monitorID);
    [return: MarshalAs(UnmanagedType.LPWStr)]
    string GetMonitorDevicePathAt(uint monitorIndex);
    uint GetMonitorDevicePathCount();
    RECT GetMonitorRECT([MarshalAs(UnmanagedType.LPWStr)] string monitorID);
}}

[ComImport, Guid("C2CF3110-460E-4fc1-B9D0-8A1C0C9CC4BD")]
public class DesktopWallpaperClass {{}}

public class PzWallMulti {{
    [DllImport("user32.dll", CharSet=CharSet.Unicode)]
    public static extern int SystemParametersInfoW(int uAction, int uParam, string lpvParam, int fuWinIni);

    public static void Apply(string primPath, string secPath, bool soloUno) {{
        var dw = (IDesktopWallpaper)new DesktopWallpaperClass();
        uint count = dw.GetMonitorDevicePathCount();
        int primIdx = 0;
        for (uint i = 0; i < count; i++) {{
            string id = dw.GetMonitorDevicePathAt(i);
            RECT r = dw.GetMonitorRECT(id);
            if (r.Left == 0 && r.Top == 0) {{ primIdx = (int)i; break; }}
        }}
        for (uint i = 0; i < count; i++) {{
            string id = dw.GetMonitorDevicePathAt(i);
            if (i == (uint)primIdx) {{
                dw.SetWallpaper(id, primPath);
            }} else if (!soloUno) {{
                dw.SetWallpaper(id, secPath);
            }} else {{
                dw.SetWallpaper(id, primPath);
            }}
        }}
        if (count == 0) {{ SystemParametersInfoW(20, 0, primPath, 3); }}
    }}
}}
'@
Add-Type -TypeDefinition $code -ErrorAction SilentlyContinue
[PzWallMulti]::Apply('{prim_esc}', '{sec_esc}', ${mismo})
"""
    try:
        _ps_oculto(ps_script)
    except Exception:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, ruta_prim, 3)


def render_frame_pillow(tema_dir, fecha, out_path, scale=3, con_astro=True):
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
    if con_astro and solOp > 0.01:
        sol_im = Image.open(os.path.join(img_dir, 'sol.png')).convert('RGBA')
        if solOp < 0.99:
            a = sol_im.split()[3].point(lambda p: int(p * solOp))
            sol_im.putalpha(a)
        base.alpha_composite(sol_im, (int(solX - 104), int(solY - 104)))
    if con_astro and lunaOp > 0.01:
        luna_im = Image.open(os.path.join(img_dir, 'luna.png')).convert('RGBA')
        if lunaOp < 0.99:
            a = luna_im.split()[3].point(lambda p: int(p * lunaOp))
            luna_im.putalpha(a)
        base.alpha_composite(luna_im, (int(lunaX - 104), int(lunaY - 104)))

    datos_path = os.path.join(tema_dir, 'datos.json')
    if os.path.isfile(datos_path):
        with open(datos_path, 'r', encoding='utf-8') as f:
            nubes_meta = json.load(f).get('nubes', [])
        noche = s['e'] < 0
        op_nub = (1.0 - wA if noche else 0.0, wA if noche else 1.0 - wB, wB)
        fases_n = ('nubes-noche.png', 'nubes-dorado.png', 'nubes-dia.png')
        hojas_n = [Image.open(os.path.join(img_dir, fn)).convert('RGBA') if op > 0.01 else None
                   for fn, op in zip(fases_n, op_nub)]
        for nb in nubes_meta:
            x_n, y_n, w_n, h_n, ys_n = int(nb[0]), int(nb[1]), int(nb[2]), int(nb[3]), int(nb[4])
            box = (0, ys_n, w_n, ys_n + h_n)
            for hoja, op in zip(hojas_n, op_nub):
                if hoja is None or op <= 0.01:
                    continue
                crop = hoja.crop(box)
                if op < 0.99:
                    a = crop.split()[3].point(lambda p, f=op: int(p * f))
                    crop.putalpha(a)
                base.alpha_composite(crop, (x_n, y_n))

    escena = blend_3('escena')
    base.alpha_composite(escena)
    rgb = base.convert('RGB')
    try:
        out_im = rgb.resize((640 * scale, 400 * scale), Image.Resampling.NEAREST)
    except SystemError:
        out_im = rgb.resize((640 * scale, 400 * scale), Image.Resampling.BOX)
    out_im.save(out_path, 'PNG')


def _preview_por_fase(tema, fase, secundario=False):
    for base in (
        os.path.join(TEMAS_DIR, tema, 'secundario' if secundario else '', 'preview', fase, 'v3.png'),
        os.path.join(RAIZ, 'escenas', tema, 'secundario' if secundario else '', 'preview', fase, 'v3.png'),
        os.path.join(TEMAS_DIR, tema, 'secundario' if secundario else '', 'fondo.png'),
    ):
        if os.path.isfile(base):
            return base
    return os.path.join(TEMAS_DIR, tema, 'fondo.png')


def modo_wallpaper(args, tema_dir):
    try:
        import PIL  # noqa: F401
        tiene_pil = True
    except ImportError:
        tiene_pil = False
        if not args.una_vez:
            print('Aviso: Pillow no instalado (pip install pillow). Usando vistas estáticas por fase.')

    sec_dir = os.path.join(tema_dir, 'secundario')
    tiene_sec = args.monitores >= 2 and os.path.isdir(os.path.join(sec_dir, 'images'))

    ahora = datetime.datetime.now()
    hora_ini = ahora.hour + ahora.minute / 60.0 + ahora.second / 3600.0
    t0 = time.monotonic()
    tmp_prim = os.path.join(tempfile.gettempdir(), f'pixelzen_{args.tema}_m1.png')
    tmp_sec = os.path.join(tempfile.gettempdir(), f'pixelzen_{args.tema}_m2.png')
    intervalo = 2.0 if args.demo else (5.0 if args.c90 else 60.0)

    if not args.una_vez:
        print(f'PixelZen Windows activo | tema={args.tema} | monitores={args.monitores} | ciclo={"90m" if args.c90 else ("demo90s" if args.demo else ("fija" if args.hora is not None else "real"))}')
    try:
        while True:
            d = datetime.datetime.now()
            if args.hora is not None:
                h = args.hora % 24.0
                d = d.replace(hour=int(h), minute=int((h % 1) * 60), second=0, microsecond=0)
            elif args.c90:
                h = (hora_ini + ((time.monotonic() - t0) / 5400.0) * 24.0) % 24.0
                d = d.replace(hour=int(h), minute=int((h % 1) * 60), second=int((h * 3600) % 60), microsecond=0)
            elif args.demo:
                h = ((time.monotonic() - t0) % 90.0) / 90.0 * 24.0
                d = d.replace(hour=int(h), minute=int((h % 1) * 60), second=int((h * 3600) % 60), microsecond=0)

            if tiene_pil:
                render_frame_pillow(tema_dir, d, tmp_prim)
                if tiene_sec:
                    render_frame_pillow(sec_dir, d, tmp_sec, con_astro=False)
                    set_windows_wallpapers(tmp_prim, tmp_sec)
                else:
                    set_windows_wallpapers(tmp_prim, None)
            else:
                el = elevacion_solar(d)['e']
                fase = 'noche' if el < -4 else ('dorado' if el < 8 else 'dia')
                p1 = _preview_por_fase(args.tema, fase, secundario=False)
                p2 = _preview_por_fase(args.tema, fase, secundario=True) if args.monitores >= 2 else None
                set_windows_wallpapers(p1, p2)

            if args.una_vez:
                break
            time.sleep(intervalo)
    except KeyboardInterrupt:
        print('\nPixelZen detenido.')


def modo_servidor(puerto):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=LIVELY_DIR, **kw)

        def translate_path(self, path):
            rel = urllib.parse.urlparse(path).path.lstrip('/')
            if rel.startswith('temas/'):
                return os.path.join(TEMAS_DIR, *rel.split('/')[1:])
            return super().translate_path(path)

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path == '/api/stats':
                payload = json.dumps(datos_win.recolectar(RAIZ), ensure_ascii=False).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Cache-Control', 'no-store')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            if parsed.path == '/api/config':
                payload = json.dumps(cargar_config(), ensure_ascii=False).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            super().do_GET()

        def log_message(self, fmt, *args):
            pass

    srv = http.server.ThreadingHTTPServer(('127.0.0.1', puerto), Handler)
    print(f'Servidor PixelZen activo en http://127.0.0.1:{puerto}/ (Ctrl+C para cerrar)')
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


def main():
    cfg = cargar_config()
    p = argparse.ArgumentParser(description='PixelZen Worlds para Windows')
    p.add_argument('--tema', default=cfg.get('tema', 'fittoa'), help='Tema a usar')
    p.add_argument('--monitores', type=int, default=int(cfg.get('monitores', 2)), choices=(1, 2), help='1 = solo principal, 2 = principal + continuación')
    p.add_argument('--90m', dest='c90', action='store_true', help='Ciclo completo de 24 horas en 90 minutos')
    p.add_argument('--demo', action='store_true', help='Demo rápida de 24 horas en 90 segundos')
    p.add_argument('--real', action='store_true', help='Seguir la hora real del reloj')
    p.add_argument('--hora', type=float, default=None, help='Hora fija (ej. 18.75)')
    p.add_argument('--una-vez', action='store_true', help='Aplica el fondo una sola vez y sale')
    p.add_argument('--listar', action='store_true', help='Listar temas disponibles')
    p.add_argument('--servidor', action='store_true', help='Inicia servidor web local con /api/stats')
    p.add_argument('--puerto', type=int, default=8765, help='Puerto del servidor local')
    args = p.parse_args()

    if args.listar:
        print('Temas disponibles:', ', '.join(listar_temas()))
        return

    if args.servidor:
        modo_servidor(args.puerto)
        return

    tema_dir = os.path.join(TEMAS_DIR, args.tema)
    if not os.path.isdir(tema_dir):
        print(f'Error: tema "{args.tema}" no encontrado en {TEMAS_DIR}', file=sys.stderr)
        sys.exit(2)

    modo_wallpaper(args, tema_dir)


if __name__ == '__main__':
    main()
