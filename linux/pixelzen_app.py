#!/usr/bin/env python3
"""Aplicación visual PixelZen Worlds Desktop Studio para Linux (GTK4 + Libadwaita).

Diseño y funcionalidades equivalentes a PixelZenMenu.ps1 (v1.2.1):
- Hub 2x2 estilo pixel-art oscuro (Elegir Tema, Pantallas, Widgets, Ajustes)
- Navegación lateral con sprites pixel-art y resumen en vivo
- Selector jerárquico Serie -> Mundo -> Escena visual por pantalla (M1, M2 y Bloqueo)
- Estudio en vivo a la derecha con simulación HUD de 9 tarjetas
- Clima real (Open-Meteo), rotación automática, eventos épicos y modo Solo Widgets
"""
import functools
import http.server
import json
import os
import shutil
import socketserver
import stat
import subprocess
import sys
import threading
import urllib.request

try:
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import Adw, Gdk, GdkPixbuf, Gio, GLib, Gtk  # noqa: E402
except Exception as exc:
    sys.stderr.write(
        'PixelZen Worlds necesita GTK 4 y Libadwaita (python3-gi, gir1.2-gtk-4.0, gir1.2-adw-1).\n'
        f'Detalle: {exc}\n'
    )
    sys.exit(1)

UUID = 'pixelzen@mosqui1988.github.io'
EXT_DIR = os.path.expanduser(f'~/.local/share/gnome-shell/extensions/{UUID}')
SCHEMA_DIR = os.path.join(EXT_DIR, 'schemas')
SCHEMA_ID = 'org.gnome.shell.extensions.pixelzen'
SVC_CICLO90 = 'pixelzen-ciclo90.service'
RELEASES_API = 'https://api.github.com/repos/davidlpizano/pixelzen-worlds/releases/latest'
RELEASES_URL = 'https://github.com/davidlpizano/pixelzen-worlds/releases'
WEB_URL_FALLBACK = 'https://davidlpizano.github.io/pixelzen-worlds/'
CLIMA_CACHE_PATH = os.path.expanduser('~/.config/pixelzen/clima_real.json')

MAPA_SERIE = {
    'fittoa': ('Mushoku Tensei', 'Región de Fittoa'),
    'continente-demoniaco': ('Mushoku Tensei', 'Continente Demoníaco'),
    'black-clover': ('Black Clover', 'Aldea de Hage'),
    'hunter-x-hunter': ('Hunter × Hunter', 'Isla Ballena'),
    'spiderman-miles-morales': ('Spider-Man: Miles Morales', 'Brooklyn y Manhattan'),
    'solo-leveling': ('Solo Leveling', 'Castillo del Monarca'),
    'demon-slayer': ('Demon Slayer', 'Tren Infinito'),
    'stranger-things': ('Stranger Things', 'Hawkins y el Revés'),
    'harry-potter': ('Harry Potter', 'Castillo de Hogwarts'),
    'naruto': ('Naruto', 'Konoha & Modo Baryon'),
    'jujutsu-kaisen': ('Jujutsu Kaisen', 'Expansión de Dominio'),
    'attack-on-titan': ('Attack on Titan', 'El Retumbar y la Muralla'),
    'one-piece': ('One Piece', 'Gear 5 & Onigashima'),
    'dragon-ball-z': ('Dragon Ball Z', 'Ultra Instinto en Namek'),
    'cyberpunk-edgerunners': ('Cyberpunk: Edgerunners', 'Night City & Sandevistan'),
}

FASES = [('dia', '☀️ Día'), ('dorado', '🌅 Dorado'), ('noche', '🌙 Noche')]
MODOS = [
    ('90m', '🌗 Ciclo suave — Día y noche cada 90 min (Recomendado)'),
    ('real', '🕒 Hora real — Igual que el reloj de tu sistema'),
    ('demo', '⚡ Paseo rápido — Cambia en 90 segundos para probar'),
    ('fija', '🔒 Momento fijo — Elige tú Día, Atardecer o Noche'),
]
MODOS_CORTO = {'90m': 'Ciclo 90m', 'real': 'Hora real', 'demo': 'Pase rápido', 'fija': 'Hora fija'}
CLIMAS = [
    ('normal', '✨ Despejado (Original del mundo)'),
    ('lluvia', '🌧️ Lluvia suave en tiempo real'),
    ('tormenta', '⛈️ Tormenta con relámpagos'),
    ('nieve', '❄️ Nevadas suaves de invierno'),
    ('niebla', '🌫️ Niebla nocturna misteriosa'),
    ('ceniza', '🌋 Ceniza volcánica / brasas'),
    ('auto', '🤖 Automático por universo y clima real'),
]
ROTACIONES = [
    (0, '🔒 Desactivado — Mantener mundo elegido'),
    (5, '⏱️ Rotar cada 5 minutos'),
    (15, '⏱️ Rotar cada 15 minutos'),
    (30, '⏱️ Rotar cada 30 minutos'),
    (60, '🕒 Rotar cada hora'),
]
VARIANTES = [('principal', 'Principal'), ('secundaria', 'Secundaria'), ('bloqueo', 'Bloqueo')]

STATS_META = [
    ('hud-tiempo', '🕒 Reloj, fecha y nombre del mundo', 'Muestra la hora grande, la fecha en español y el escenario activo.', '21:34 · Fittoa'),
    ('hud-clima', '☀️ Clima real y órbita solar', 'Temperatura real, viento, elevación solar y fase atmosférica.', '☀ SOL +18° · DESPEJADO'),
    ('hud-sistema', '💻 Rendimiento del PC (CPU, RAM, Temp, Disco)', 'Barras visuales en tiempo real para controlar la carga del equipo.', '❖ CPU 12% RAM 48%'),
    ('hud-gpu', '🎮 GPU y motor gráfico', 'Tarjeta gráfica detectada, FPS activos y carga visual.', '▣ GPU · 8 FPS'),
    ('hud-red', '🌐 Conexión e Internet (Wi-Fi / IP / Velocidad)', 'Muestra tu red activa, IP local y tráfico de subida/bajada.', '◈ ETH 192.168.1.38'),
    ('hud-audio', '🎵 Música y banda sonora del mundo', 'Reproductores activos (Spotify/MPRIS) o BSO acorde al universo.', '♪ MÚSICA / BSO EN VIVO'),
    ('hud-dev', '🛠️ Información técnica / Programador', 'Nombre del equipo, repositorios Git y runtimes detectados.', '⚔ DEV · main'),
    ('hud-foco', '⏱️ Temporizador Zen / Sesión (Pomodoro)', 'Cuenta atrás de 25 minutos por ciclos y tiempo de sesión activa.', '⧖ ZEN 25:00'),
    ('hud-grimorio', '📖 Frase del universo (Grimorio)', 'Citas icónicas de la serie que rotan automáticamente.', '«Frase del mundo...»'),
]


def _leer_version():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(app_dir)
    for vp in (os.path.join(app_dir, 'VERSION'), os.path.join(repo_root, 'VERSION')):
        if os.path.isfile(vp):
            try:
                txt = open(vp, 'r', encoding='utf-8').read().strip()
                if txt:
                    return txt
            except Exception:
                pass
    return '1.2.2'


def _cortar_serie_prefijo(txt):
    if not txt:
        return ''
    if ' · ' in txt:
        return txt.split(' · ', 1)[1].strip()
    return txt.strip()


def _cargar_temas():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bases = [
        os.path.join(repo_root, 'windows', 'lively', 'temas'),
        os.path.join(EXT_DIR, 'temas'),
        os.path.join(repo_root, 'escenas'),
    ]
    encontrados = {}
    for base in bases:
        if not os.path.isdir(base):
            continue
        for nombre_dir in sorted(os.listdir(base)):
            if nombre_dir.startswith('_') or nombre_dir in encontrados:
                continue
            tpath = os.path.join(base, nombre_dir)
            tj = os.path.join(tpath, 'tema.json')
            if not os.path.isfile(tj):
                continue
            anime = 'PixelZen'
            titulo = nombre_dir
            m1 = 'Escena principal'
            m2 = 'Continuación de la historia'
            m3 = 'Pantalla de bloqueo'
            raw = {}
            try:
                raw = json.loads(open(tj, 'r', encoding='utf-8').read())
                if raw.get('nombre'):
                    titulo = str(raw['nombre'])
                    if ' · ' in titulo:
                        partes = titulo.split(' · ', 1)
                        anime, titulo = partes[0].strip(), partes[1].strip()
                if raw.get('anime'):
                    anime = str(raw['anime'])
                m1 = str(raw.get('subtitulo') or raw.get('descripcion') or m1)
            except Exception:
                pass
            serie = str(raw.get('serie') or '')
            if nombre_dir in MAPA_SERIE:
                serie = serie or MAPA_SERIE[nombre_dir][0]
                titulo = MAPA_SERIE[nombre_dir][1]
            elif not serie:
                serie = anime

            sj = os.path.join(tpath, 'secundario', 'tema.json')
            if os.path.isfile(sj):
                try:
                    sraw = json.loads(open(sj, 'r', encoding='utf-8').read())
                    m2 = str(sraw.get('nombre') or sraw.get('subtitulo') or m2)
                except Exception:
                    pass
            bj = os.path.join(tpath, 'bloqueo', 'tema.json')
            if os.path.isfile(bj):
                try:
                    braw = json.loads(open(bj, 'r', encoding='utf-8').read())
                    m3 = str(braw.get('nombre') or braw.get('subtitulo') or m3)
                except Exception:
                    pass
            encontrados[nombre_dir] = {
                'id': nombre_dir,
                'serie': serie,
                'anime': serie,
                'titulo': titulo,
                'm1': m1,
                'm2': m2,
                'm3': m3,
            }
        if encontrados:
            break
    if not encontrados:
        return [{'id': 'fittoa', 'serie': 'Mushoku Tensei', 'anime': 'Mushoku Tensei', 'titulo': 'Región de Fittoa',
                 'm1': 'Aldea de Buena', 'm2': 'Reino de Asura', 'm3': 'Santuario del Teletransporte'}]
    return list(encontrados.values())


VERSION_ACTUAL = _leer_version()
TEMAS = _cargar_temas()
SERIES_ORDEN = []
SERIES_MAP = {}
for _t in TEMAS:
    if _t['serie'] not in SERIES_MAP:
        SERIES_MAP[_t['serie']] = []
        SERIES_ORDEN.append(_t['serie'])
    SERIES_MAP[_t['serie']].append(_t)


def _resolver_preview(tema_id, fase, variante='principal'):
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sub = 'secundario' if variante == 'secundaria' else ('bloqueo' if variante == 'bloqueo' else '')
    pref = 'm2-' if variante == 'secundaria' else ('m3-' if variante == 'bloqueo' else '')
    candidatos = [
        os.path.join(EXT_DIR, 'temas', tema_id, sub, 'preview', fase, 'v3.png'),
        os.path.join(repo_root, 'escenas', tema_id, sub, 'preview', fase, 'v3.png'),
        os.path.join(repo_root, 'docs', 'previews', tema_id, f'{pref}{fase}.png'),
        os.path.join(repo_root, 'windows', 'lively', 'temas', tema_id, sub, 'images', f'escena-{fase}.png'),
        os.path.join(EXT_DIR, 'temas', tema_id, sub, 'images', f'escena-{fase}.png'),
        os.path.join(EXT_DIR, 'temas', tema_id, sub, 'fondo.png'),
        os.path.join(repo_root, 'windows', 'lively', 'temas', tema_id, sub, 'fondo.png'),
        os.path.join(EXT_DIR, 'temas', tema_id, 'fondo.png'),
    ]
    for ruta in candidatos:
        if ruta and os.path.isfile(ruta):
            return ruta
    return None


def _cargar_settings():
    if os.path.isfile(os.path.join(SCHEMA_DIR, 'gschemas.compiled')):
        src = Gio.SettingsSchemaSource.new_from_directory(SCHEMA_DIR, None, False)
        schema = src.lookup(SCHEMA_ID, True)
        if schema is not None:
            return Gio.Settings.new_full(schema, None, None)
    return None


def _has_key(s, key):
    if not s:
        return False
    try:
        schema = s.props.settings_schema
        return bool(schema and schema.has_key(key))
    except Exception:
        return False


def _get_str(s, key, default):
    if not _has_key(s, key):
        return default
    try:
        return s.get_string(key)
    except Exception:
        return default


def _get_bool(s, key, default):
    if not _has_key(s, key):
        return default
    try:
        return s.get_boolean(key)
    except Exception:
        return default


def _get_int(s, key, default):
    if not _has_key(s, key):
        return default
    try:
        return s.get_int(key)
    except Exception:
        return default


def _set_safe(s, kind, key, val):
    if not _has_key(s, key):
        return
    try:
        if kind == 's':
            s.set_string(key, str(val))
        elif kind == 'b':
            s.set_boolean(key, bool(val))
        elif kind == 'i':
            s.set_int(key, int(val))
        elif kind == 'd':
            s.set_double(key, float(val))
    except Exception:
        pass


def _extension_instalada():
    return os.path.isdir(EXT_DIR) and os.path.isfile(os.path.join(SCHEMA_DIR, 'gschemas.compiled'))


def _extension_activa():
    try:
        out = subprocess.run(
            ['gnome-extensions', 'info', UUID],
            capture_output=True, text=True, check=False,
        ).stdout
        for linea in out.splitlines():
            if 'State:' in linea or 'Estado:' in linea:
                return ('ACTIVE' in linea.upper()) or ('ENABLED' in linea.upper()) or ('ACTIVA' in linea.upper())
    except Exception:
        pass
    return False


def _ciclo90_activo():
    try:
        res = subprocess.run(
            ['systemctl', '--user', 'is-active', SVC_CICLO90],
            capture_output=True, text=True, check=False,
        )
        return res.stdout.strip() == 'active'
    except Exception:
        return False


def _detectar_fase(modo, hora_fija):
    if modo == 'fija':
        h = float(hora_fija)
    else:
        import datetime
        now = datetime.datetime.now()
        h = now.hour + now.minute / 60.0
    if 8.0 <= h < 17.5:
        return 'dia'
    if (6.0 <= h < 8.0) or (17.5 <= h < 20.0):
        return 'dorado'
    return 'noche'


def _sincronizar_tema_en_ext(tema_id):
    tema_pack = os.path.join(EXT_DIR, 'temas', tema_id)
    if not os.path.isdir(os.path.join(tema_pack, 'images')):
        return
    dst_imgs = os.path.join(EXT_DIR, 'images')
    if os.path.isdir(dst_imgs):
        shutil.rmtree(dst_imgs, ignore_errors=True)
    shutil.copytree(os.path.join(tema_pack, 'images'), dst_imgs)
    for fn in ('datos.json', 'tema.json', 'fondo.png'):
        src_fn = os.path.join(tema_pack, fn)
        if os.path.isfile(src_fn):
            shutil.copy2(src_fn, os.path.join(EXT_DIR, fn))


def _aplicar_fondos_gnome(tema_id, fase, fp, fb, usar_bloqueo):
    bg_dir = os.path.expanduser('~/.local/share/backgrounds')
    os.makedirs(bg_dir, exist_ok=True)
    src_p = _resolver_preview(tema_id, fase, fp)
    if src_p and os.path.isfile(src_p):
        dst_p = os.path.join(bg_dir, 'pixelzen.png')
        shutil.copy2(src_p, dst_p)
        uri_p = f'file://{dst_p}'
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', uri_p], check=False)
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri-dark', uri_p], check=False)
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-options', 'zoom'], check=False)
    if usar_bloqueo:
        src_b = _resolver_preview(tema_id, fase, fb) or src_p
        if src_b and os.path.isfile(src_b):
            dst_b = os.path.join(bg_dir, 'pixelzen-lock.png')
            shutil.copy2(src_b, dst_b)
            uri_b = f'file://{dst_b}'
            subprocess.run(['gsettings', 'set', 'org.gnome.desktop.screensaver', 'picture-uri', uri_b], check=False)


def _detectar_monitores():
    mons = []
    display = Gdk.Display.get_default()
    if display:
        ml = display.get_monitors()
        for i in range(ml.get_n_items()):
            m = ml.get_item(i)
            g = m.get_geometry()
            tag = 'Principal' if i == 0 else 'Secundario'
            mons.append(f'Pantalla {i + 1}: {tag} ({g.width}×{g.height})')
    return mons


def _sprite_texture(grid, pal_spec, scale=3):
    """Genera un Gdk.Texture Nearest-Neighbor nítido a partir de un sprite ASCII."""
    pal = {}
    for tok in pal_spec.split():
        if '=' in tok:
            k, v = tok.split('=', 1)
            v = v.lstrip('#')
            r = int(v[0:2], 16)
            g = int(v[2:4], 16)
            b = int(v[4:6], 16)
            a = int(v[6:8], 16) if len(v) >= 8 else 255
            pal[k] = (r, g, b, a)
    h = len(grid)
    w = max((len(r) for r in grid), default=1)
    buf = bytearray(w * h * 4)
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == '.' or ch not in pal:
                continue
            r, g, b, a = pal[ch]
            idx = (y * w + x) * 4
            buf[idx:idx + 4] = bytes((r, g, b, a))
    pb = GdkPixbuf.Pixbuf.new_from_data(bytes(buf), GdkPixbuf.Colorspace.RGB, True, 8, w, h, w * 4)
    if scale > 1:
        pb = pb.scale_simple(w * scale, h * scale, GdkPixbuf.InterpType.NEAREST)
    return Gdk.Texture.new_for_pixbuf(pb)


def _cargar_sprites():
    return {
        'bonsai_circle': _sprite_texture([
            '........oooooooo........',
            '......ooyyyyyyyyoo......',
            '....ooyyyyyyyyyyyyoo....',
            '...oyyyyGGGGGGGyyyyyo...',
            '..oyyyGGLLLLLLLGyyyyyo..',
            '..oyyyGLLllllllGyyyyyo..',
            '.oyyGGLLllGGGGGGGoooo...',
            '.oyGLLLllGLLLLLLLGGoo...',
            '.ooGllGGGGGllLLLLlGGo...',
            'oaaaGggggggGllllGGggao..',
            'oaaaaoGTTggggGGTTggaaao.',
            'oaaaaaaoTTTggTTTaaaaao..',
            'oaaaaaaaaoTTTTToaaaaao..',
            '.orrrrrrrroTTTorrrrro...',
            '.orrrrrrroTBBTTooooor...',
            '..ooooooTTBBBBTTooooo...',
            '..ogggooBBBBBBBBooggo...',
            '...oooPPPPPPPPPPPooo....',
            '...oopPPPPPPPPPPPpoo....',
            '....oopppppppppppoo.....',
            '.....ooooooooooooo......',
            '......oowwwwwwwwo.......',
            '........oooooooo........',
            '........................',
        ], 'o=#0A0D19 y=#F9CC52 a=#F08834 r=#C95427 G=#245E3B L=#459A54 l=#79CE6D g=#19442B T=#5D3723 B=#3F2215 P=#91543A p=#623421 w=#3E4B78', scale=4),
        'bonsai_pot': _sprite_texture([
            '............oooooooo............',
            '.........ooyyyyyyyyyyoo.........',
            '.......ooyyyyyyyyyyyyyyoo.......',
            '......oyyyyGGGGGGGGyyyyyyo......',
            '.....oyyyGGLLLLLLLLGyyyyyyo.....',
            '....oyyyGLLllllllllGGyyyyyyo....',
            '....oyyGGLLllGGGGGGGGGGyyyyo....',
            '...oyGGGllGGLLLLLLLLLLGGyyyo....',
            '...oGGLLllGGllllllGGGGllGGyo....',
            '..oyGLLllGGgggGGGGGllLLLLGyo....',
            '..oyGGGgGGTTggggGGGGGllGGayyo...',
            '..oaayyyoTTTTggTTTggggGaaaao....',
            '...oaaaayooTTTTTToGGTTggaaao....',
            '...orrrrryyoTTTToGLLllGrrrro....',
            '....orrrrrroTBBToGllGGrrrro.....',
            '.....ooooooTBBBTTooGooooo.......',
            '..........oTBBBBTo..............',
            '.........ooTBBBBBTTo............',
            '........oTTBBBBBBBBTo...........',
            '.......ooooooooooooooo..........',
            '......ooPPPPPPPPPPPPPPoo........',
            '......oPPPPPPPPPPPPPPPPo........',
            '.......ooPPPPPPPPPPPPoo.........',
            '.......oppppppppppppppo.........',
            '.......oppppppppppppppo.........',
            '........oooooooooooooo..........',
            '........oo..oooo..oooo..........',
            '................................',
        ], 'o=#0A0D19 y=#F8C54A a=#F08B33 r=#C8552A G=#235E3A L=#449852 l=#7BCE6C g=#174027 T=#6B3E26 B=#422415 P=#96563C p=#633422', scale=4),
        'star': _sprite_texture([
            '......o......',
            '.....oyo.....',
            '.....oYo.....',
            '.ooooYYGoooo.',
            'oYYYYYYYYYYGo',
            '.oYYYYYYYYGo.',
            '..oYYYYYYGo..',
            '..oYYooYYGo..',
            '.oYYo..oYYGo.',
            '.oGo....oGGo.',
            '.oo......oo..',
        ], 'o=#0A0D19 y=#FFF1A8 Y=#F7C63E G=#C98416', scale=2),
        'nav_home': _sprite_texture([
            '.......oo.......',
            '.....oorroo.....',
            '...oorRRRRroo...',
            '..orRRRRRRRroo..',
            '.oRRRRRRRRRRRro.',
            'oRooooooooooooRo',
            '..oWWWWWWWWWWo..',
            '..oWWooWWooWWo..',
            '..oWWbbWWCCWWo..',
            '..oWWbbWWCCWWo..',
            '..oWWbbWWWWWWo..',
            '..oWWbbWWWWWWo..',
            '..oooooooooooo..',
        ], 'o=#0A0D19 r=#EA6A5B R=#C74137 W=#F0E9DC b=#7A4C32 C=#72D8E6', scale=2),
        'nav_monitors': _sprite_texture([
            '................',
            '.oooooooooooooo.',
            'oCCCCCCCCCCCCCo.',
            'oCsssssssssssCo.',
            'oCsGGyyyyyyGGCo.',
            'oCsGGGGLLGGGGCo.',
            'oCsGGGGGGGGGGCo.',
            'oCCCCCCCCCCCCCo.',
            '.oooooooooooooo.',
            '......oSSo......',
            '....ooSSSSoo....',
            '....oooooooo....',
        ], 'o=#0A0D19 C=#8DA8D6 s=#1A2E52 G=#348C5E L=#6AD47E y=#F7C948 S=#5E739E', scale=2),
        'nav_save': _sprite_texture([
            '.ooooooooooooo..',
            'oBBBBMMMMMMBoBo.',
            'oBBBBMoMMMoBBBB.',
            'oBBBBMMMMMMBBBBo',
            'oBBBBBBBBBBBBBBo',
            'oBooooooooooooBo',
            'oBoWWWWWWWWWWoBo',
            'oBoRRRRRRRRRRoBo',
            'oBoYYYYYYYYYYoBo',
            'oBoCCCCCCCCCCoBo',
            'oBoWWWWWWWWWWoBo',
            'oooooooooooooooo',
        ], 'o=#0A0D19 B=#48649C M=#CFD8EA W=#F2EFE7 R=#D85555 Y=#ECC148 C=#49B5C4', scale=2),
        'gear': _sprite_texture([
            '........oooooo........',
            '........oLLLLo........',
            '....ooooLLLLLLoooo....',
            '..ooLLLLLLMMLLLLLLoo..',
            '.oLLLLooMMMMMMooLLLLo.',
            '.oLLLoMMDDDDDDMMoLLLo.',
            '..ooLMMDoMMMMoDDMLoo..',
            '..oLMMDoMooooMoDDMLo..',
            'ooLLMDoMo....oMoDDMLoo',
            'oLLLMDoMo....oMoDDMLLo',
            'oLLLMDoMo....oMoDDMLLo',
            'oLLLMDoMo....oMoDDMLLo',
            'ooLLMDoMo....oMoDDMLoo',
            '..oLMMDoMooooMoDDMLo..',
            '..ooLMMDoMMMMoDDMLoo..',
            '.oDDDoMMDDDDDDMMoDDDo.',
            '.oDDDDoMMMMMMMMoDDDDo.',
            '..ooDDDDDDMMDDDDDDoo..',
            '....ooooDDDDDDoooo....',
            '........oDDDDoo.......',
            '........oooooo........',
        ], 'o=#0A0D19 L=#E2EAF6 M=#9FB0CE D=#69799B', scale=3),
        'weather': _sprite_texture([
            '....o....o....o.......',
            '..o..o..ooo..o........',
            '...o.ooyyyyyoo........',
            '.ooooyYYYYYYYyo.......',
            '...ooyYYYYoYYYYo......',
            '..o.oyYYYooWWWWoo.....',
            '....ooyYoWWWWWWWWoo...',
            '.....ooWWWWWWWWWWWWoo.',
            '....oWWWWWWWWWWWWWWWWo',
            '...oWWWWWWWWWWWWWCCCCo',
            '...oWCCCCCCCCCCCCCCCCo',
            '....oBBBBBBBBBBBBBBBo.',
            '.....ooooooooooooooo..',
        ], 'o=#0A0D19 y=#FFE26A Y=#F7BA33 W=#FFFFFF C=#D7EEFA B=#94BED9', scale=3),
        'cat': _sprite_texture([
            '..oo......oo......',
            '.oOOo....oOOo.....',
            '.oOroo..oorOo.....',
            '.oOOOOOOOOOOo.....',
            '.oOOppOOppOOo.....',
            '.oOOwkoowkOOo..oo.',
            '.oOOBBkkBBOOo.oOOo',
            '.oOOBMMMMBBOo.oOOo',
            '..ooOOOOOOoo..oOro',
            '..oOBBBBBBOoooOOo.',
            '.oOOBMMMMBOOOOOo..',
            '.oOOBMMMMBOOOOOo..',
            '.oOOOOOOOOooooo...',
            '..oOOoOOo.........',
            '..oOOoOOo.........',
            '...oo..oo.........',
        ], 'o=#0A0D19 O=#F2983C r=#D26E22 p=#C8601E w=#FFFFFF k=#141826 B=#FFD598 M=#FFEAC8', scale=3),
        'plant_left': _sprite_texture([
            '....oo........',
            '...oLLo...oo..',
            '...oLGo..oLLo.',
            'oooLGoo..oLGo.',
            'oLLGGGo.oGGoo.',
            '.ooGGGGooGGo..',
            '...ooGGGGGGo..',
            '.....oGGGGoo..',
            '....ooGGGo....',
            '....oDDDDoo...',
            '...oooooooo...',
        ], 'o=#0A0D19 L=#78D872 G=#3C9C50 D=#276937', scale=2),
        'flower_right': _sprite_texture([
            '...oo....oo...',
            '..oPPo..oPPo..',
            '.oPYYPoPYYPo..',
            '..oPPooPPPo...',
            '...ooGGGGoo...',
            '....oGLLGo....',
            '..oooGGGGooo..',
            '.oLLGGGGGGLLo.',
            '..oooGGGGooo..',
            '.....oGGo.....',
        ], 'o=#0A0D19 P=#B878F2 Y=#F8D454 G=#3B9B4E L=#76D670', scale=2),
        'sprout': _sprite_texture([
            '...oooo...',
            '..oYYYYo..',
            '..oYyyYo..',
            '...oooo...',
            '.ooGooGoo.',
            'oLLGGGGLLo',
            '.ooGGGGoo.',
            '...oGGo...',
            '...oooo...',
        ], 'o=#0A0D19 Y=#FFE066 y=#F2AD29 G=#3FA354 L=#7CE678', scale=2),
    }


STUDIO_CSS = b"""
window, .pz-root {
    background-color: #0A0D19;
    color: #F4F0E4;
}
.pz-header {
    background: linear-gradient(to bottom, #2B345E, #21284B);
    border-bottom: 3px solid #0A0D19;
    padding: 4px 10px;
    min-height: 44px;
}
.pz-title-text {
    color: #F6F2E8;
    font-weight: 800;
    font-size: 13.5px;
    text-shadow: 1px 1px 0px #0A0D19;
}
.pz-mon-info {
    color: #8FA7CE;
    font-size: 11px;
}
.pz-badge-ok {
    background: #102924;
    border: 1.5px solid #2E8B6B;
    border-radius: 5px;
    padding: 2px 8px;
    color: #72E6AE;
    font-size: 10px;
    font-weight: 800;
}
.pz-badge-solo {
    background: #122A38;
    border: 1.5px solid #54DED4;
    border-radius: 5px;
    padding: 2px 8px;
    color: #7CF6EE;
    font-size: 10px;
    font-weight: 800;
}
.pz-badge-warn {
    background: #261E12;
    border: 1.5px solid #7D6230;
    border-radius: 5px;
    padding: 2px 8px;
    color: #E6B45A;
    font-size: 10px;
    font-weight: 800;
}
.pz-sidebar {
    background: #19203C;
    border-right: 3px solid #0A0D19;
}
.pz-logo-ring {
    background: #0A0D19;
    border-radius: 99px;
    padding: 4px;
}
.pz-brand {
    color: #F6F2E8;
    font-size: 22px;
    font-weight: 800;
    text-shadow: 2px 2px 0px #0A0D19;
}
.pz-nav-btn {
    background: transparent;
    border: none;
    border-top: 1px solid transparent;
    border-bottom: 1px solid transparent;
    border-radius: 0px;
    padding: 9px 18px;
    color: #B8C7E2;
    font-size: 13.5px;
    font-weight: 700;
}
.pz-nav-btn:hover {
    background: #20325A;
    color: #FFFFFF;
}
.pz-nav-active {
    background: #243966;
    border-top: 1px solid #4F7ED4;
    border-bottom: 1px solid #4F7ED4;
    color: #FFFFFF;
}
.pz-resumen-box {
    background: #11172D;
    border: 1.5px solid #2A3A66;
    border-radius: 7px;
    padding: 8px 10px;
    color: #B4C6E4;
    font-size: 10.5px;
}
.pz-center {
    background: #141A32;
}
.pz-topbar {
    background: #1B2547;
    border: 1.5px solid #3C528A;
    border-radius: 9px;
    padding: 8px 12px;
}
.pz-pill-btn {
    background: #243560;
    color: #F3EFE4;
    border: 1.5px solid #5B78B4;
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 12px;
    font-weight: 700;
}
.pz-pill-btn:hover {
    background: #314880;
    border-color: #7CF6EE;
}
.pz-pill-cyan {
    background: #18364A;
    color: #7CF6EE;
    border: 1.5px solid #3C8D96;
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 12px;
    font-weight: 700;
}
.pz-pill-green {
    background: #36895B;
    color: #FFFFFF;
    border: 1.5px solid #6FD498;
    border-radius: 6px;
    padding: 6px 20px;
    font-size: 12.5px;
    font-weight: 800;
}
.pz-pill-green:hover {
    background: #3EA06A;
}
.pz-cta-btn {
    background: linear-gradient(to right, #47DBD0, #6CF7EE);
    color: #061217;
    border: 1.5px solid #88FFF4;
    border-radius: 7px;
    padding: 7px 18px;
    font-size: 12.5px;
    font-weight: 800;
}
.pz-cta-btn:hover {
    background: linear-gradient(to right, #6BF2E8, #A2FFF9);
}
.pz-footer {
    background: #1A2240;
    border-top: 3px solid #0A0D19;
    padding: 9px 14px;
}
.pz-hub-outer {
    background: #0A0D19;
    border-radius: 14px;
    padding: 3px;
    margin-top: 12px;
}
.pz-hub-blue {
    background: linear-gradient(to bottom, #203B6B, #162A4F);
    border: 2.5px solid #498CC8;
    border-radius: 11px;
    padding: 24px 12px 10px 12px;
}
.pz-hub-green {
    background: linear-gradient(to bottom, #194B3E, #12382F);
    border: 2.5px solid #48AD74;
    border-radius: 11px;
    padding: 24px 12px 10px 12px;
}
.pz-hub-purple {
    background: linear-gradient(to bottom, #471E54, #31143B);
    border: 2.5px solid #B44D92;
    border-radius: 11px;
    padding: 24px 12px 10px 12px;
}
.pz-hub-ocean {
    background: linear-gradient(to bottom, #1B3960, #132846);
    border: 2.5px solid #3B90C2;
    border-radius: 11px;
    padding: 24px 12px 10px 12px;
}
.pz-hub-hdr-blue {
    background: #31679E;
    border: 2px solid #67A9E6;
    border-radius: 8px;
    padding: 3px 20px;
    color: #FFFFFF;
    font-size: 14.5px;
    font-weight: 800;
    text-shadow: 1.5px 1.5px 0px #0A0D19;
}
.pz-hub-hdr-green {
    background: #35865A;
    border: 2px solid #6CD096;
    border-radius: 8px;
    padding: 3px 22px;
    color: #FFFFFF;
    font-size: 14.5px;
    font-weight: 800;
    text-shadow: 1.5px 1.5px 0px #0A0D19;
}
.pz-hub-hdr-purple {
    background: #8E326F;
    border: 2px solid #CE67A8;
    border-radius: 8px;
    padding: 3px 24px;
    color: #FFFFFF;
    font-size: 14.5px;
    font-weight: 800;
    text-shadow: 1.5px 1.5px 0px #0A0D19;
}
.pz-hub-hdr-ocean {
    background: #2A7AA6;
    border: 2px solid #61B7E6;
    border-radius: 8px;
    padding: 3px 24px;
    color: #FFFFFF;
    font-size: 14.5px;
    font-weight: 800;
    text-shadow: 1.5px 1.5px 0px #0A0D19;
}
.pz-slot-frame {
    background: #0A0D19;
    border: 2px solid #4C74B2;
    border-radius: 7px;
    padding: 2px;
}
.pz-slot-frame-active {
    background: #F6C84C;
    border: 2px solid #FFE896;
    border-radius: 7px;
    padding: 2px;
}
.pz-slot-caption {
    background: alpha(#080D1B, 0.85);
    color: #F6F2E8;
    font-size: 10px;
    font-weight: 700;
    padding: 2px 4px;
}
.pz-tile-bezel {
    background: #747DA4;
    border: 2px solid #A6B0DA;
    border-radius: 7px;
    padding: 5px;
}
.pz-tile-screen {
    background: #111A2B;
    border: 2px solid #0A0D19;
    border-radius: 4px;
    padding: 10px 6px;
}
.pz-tile-weather {
    background: linear-gradient(to bottom, #4DA6DF, #3279B4);
    border: 2px solid #88D2FA;
    border-radius: 7px;
    padding: 6px;
}
.pz-tile-cat {
    background: #5E2964;
    border: 2px solid #A652AC;
    border-radius: 7px;
    padding: 6px;
}
.pz-hub-row {
    background: #10213D;
    border: 1.5px solid #284B7A;
    border-radius: 6px;
    padding: 6px 10px;
}
.pz-hub-row:hover {
    border-color: #7CF6EE;
    background: #162E54;
}
.pz-studio-panel {
    background: #10172F;
    border: 1.5px solid #2B3E6E;
    border-radius: 10px;
    padding: 12px;
}
.pz-prev-box {
    background: #040711;
    border: 1.5px solid #49C8C0;
    border-radius: 7px;
}
.pz-prev-box-m2 {
    background: #040711;
    border: 1.5px solid #8A6E44;
    border-radius: 7px;
}
.pz-prev-box-lock {
    background: #040711;
    border: 1.5px solid #4C6FA8;
    border-radius: 7px;
}
.pz-mock-card {
    background: alpha(#090F20, 0.86);
    border: 1px solid #8A6E44;
    border-radius: 3px;
    padding: 2px 5px;
    font-family: monospace;
    font-size: 9px;
}
.pz-card-item {
    background: #0E1730;
    border: 1.5px solid #263759;
    border-radius: 10px;
    padding: 10px;
}
.pz-card-item:hover {
    border-color: #7CF6EE;
}
.pz-card-item-active {
    background: #152346;
    border: 2px solid #54DED4;
    border-radius: 10px;
    padding: 10px;
}
.pz-section-card {
    background: #111C38;
    border: 1.5px solid #2B4270;
    border-radius: 10px;
    padding: 12px;
}
.pz-solo-card {
    background: #16264C;
    border: 1.5px solid #54DED4;
    border-radius: 10px;
    padding: 12px;
}
.pz-picker-card {
    background: #091024;
    border: 1.5px solid #24365C;
    border-radius: 8px;
    padding: 5px;
}
.pz-picker-card-active {
    background: #15284F;
    border: 2px solid #54DED4;
    border-radius: 8px;
    padding: 5px;
}
.pz-active-badge {
    background: #183E46;
    border: 1px solid #54DED4;
    border-radius: 4px;
    padding: 1px 6px;
    color: #54DED4;
    font-size: 9.5px;
    font-weight: 800;
}
.pz-seg-btn {
    background: #080D1B;
    color: #9AB0CE;
    border: 1px solid #283B66;
    border-radius: 6px;
    padding: 3px 9px;
    font-size: 11px;
    font-weight: 700;
}
.pz-seg-btn:checked {
    background: #163549;
    color: #7CF6EE;
    border-color: #54DED4;
}
"""


class PixelZenWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title=f'Pixelzen - Fondos & Widgets v{VERSION_ACTUAL}')
        self.set_default_size(1160, 720)
        self.set_size_request(920, 620)

        Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        css = Gtk.CssProvider()
        css.load_from_data(STUDIO_CSS)
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.settings = _cargar_settings()
        self.sprites = _cargar_sprites()
        self._syncing = False
        self._web_server = None
        self._web_port = None

        self.tema_sel = _get_str(self.settings, 'tema', 'fittoa')
        if not any(t['id'] == self.tema_sel for t in TEMAS):
            self.tema_sel = TEMAS[0]['id']
        init_obj = next((t for t in TEMAS if t['id'] == self.tema_sel), TEMAS[0])
        self.serie_sel = init_obj['serie']
        self.fase_sel = 'dorado'
        self.tab_actual = 'hub'
        self.vista_mundo = 'series'
        self.hub_page_idx = max(0, next((i for i, t in enumerate(TEMAS) if t['id'] == self.tema_sel), 0) // 3)
        self.hub_slot_ids = ['', '', '']
        self.clima_real = None

        self._nav_btns = {}
        self._series_cards = {}
        self._world_cards = {}
        self._picker_items = []
        self._switches_hud = {}
        self._mock_cards = {}
        self._fase_btns = {}

        self._build_ui()
        self._cargar_estado_inicial()
        self._comprobar_estado_extension()
        self._actualiza_vista()
        self._cargar_clima_async()

        GLib.timeout_add_seconds(20, self._tick_reloj)

    def _img_sprite(self, name, w, h):
        pic = Gtk.Picture.new_for_paintable(self.sprites[name])
        pic.set_size_request(w, h)
        pic.set_can_shrink(True)
        pic.set_content_fit(Gtk.ContentFit.CONTAIN)
        return pic

    def _build_ui(self):
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        root.add_css_class('pz-root')
        self.set_content(root)

        # Headerbar estilo Desktop Studio
        header = Adw.HeaderBar()
        header.add_css_class('pz-header')
        left_hdr = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        left_hdr.set_valign(Gtk.Align.CENTER)
        left_hdr.append(self._img_sprite('bonsai_circle', 22, 22))
        lbl_t = Gtk.Label(label=f'Pixelzen - Fondos & Widgets v{VERSION_ACTUAL}')
        lbl_t.add_css_class('pz-title-text')
        left_hdr.append(lbl_t)

        self.lbl_motor_badge = Gtk.Label(label='● MOTOR GNOME')
        self.lbl_motor_badge.add_css_class('pz-badge-ok')
        left_hdr.append(self.lbl_motor_badge)

        mons = _detectar_monitores()
        self.lbl_mon_info = Gtk.Label(label='  ·  '.join(mons) if mons else 'Pantalla 1')
        self.lbl_mon_info.add_css_class('pz-mon-info')
        left_hdr.append(self.lbl_mon_info)
        header.pack_start(left_hdr)

        self.btn_update = Gtk.Button(label='🔄 Actualizar')
        self.btn_update.add_css_class('pz-pill-btn')
        self.btn_update.connect('clicked', self._on_buscar_actualizacion)
        header.pack_end(self.btn_update)
        root.append(header)

        # Banner de extensión si falta o está desactivada
        self.banner = Adw.Banner()
        self.banner.set_button_label('Activar extensión')
        self.banner.connect('button-clicked', self._on_activar_ext)
        root.append(self.banner)

        # Cuerpo principal: Sidebar | Área central
        body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        body.set_vexpand(True)
        root.append(body)

        body.append(self._build_sidebar())

        center_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        center_col.add_css_class('pz-center')
        center_col.set_hexpand(True)
        body.append(center_col)

        # Área de trabajo (Subpáginas + Estudio Derecho)
        work_area = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        work_area.set_margin_top(10)
        work_area.set_margin_bottom(8)
        work_area.set_margin_start(12)
        work_area.set_margin_end(12)
        work_area.set_vexpand(True)
        center_col.append(work_area)

        # Columna izquierda (BarDetalleTop + Stack)
        left_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_col.set_hexpand(True)
        work_area.append(left_col)

        self.bar_detalle_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.bar_detalle_top.add_css_class('pz-topbar')
        btn_volver_hub = Gtk.Button(label='← Volver al Menú Principal')
        btn_volver_hub.add_css_class('pz-pill-btn')
        btn_volver_hub.connect('clicked', lambda *_: self._cambia_pestana('hub'))
        self.bar_detalle_top.append(btn_volver_hub)
        self.lbl_detalle_title = Gtk.Label(label='Explorar Mundos')
        self.lbl_detalle_title.set_halign(Gtk.Align.START)
        self.lbl_detalle_title.add_css_class('pz-title-text')
        self.bar_detalle_top.append(self.lbl_detalle_title)
        self.bar_detalle_top.set_visible(False)
        left_col.append(self.bar_detalle_top)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_vexpand(True)
        left_col.append(self.stack)

        self.stack.add_named(self._build_page_hub(), 'hub')
        self.stack.add_named(self._build_page_mundos(), 'mundos')
        self.stack.add_named(self._build_page_pantallas(), 'pantallas')
        self.stack.add_named(self._build_page_hud(), 'hud')
        self.stack.add_named(self._build_page_sistema(), 'sistema')

        # Estudio Derecho en vivo
        self.studio_panel = self._build_studio_preview()
        self.studio_panel.set_visible(False)
        work_area.append(self.studio_panel)

        # Barra Inferior de Acciones
        center_col.append(self._build_footer())

    def _build_sidebar(self):
        side = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        side.add_css_class('pz-sidebar')
        side.set_size_request(196, -1)

        top_logo = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        top_logo.set_margin_top(14)
        top_logo.set_margin_bottom(8)
        top_logo.set_halign(Gtk.Align.CENTER)
        ring = Gtk.Box()
        ring.add_css_class('pz-logo-ring')
        ring.set_halign(Gtk.Align.CENTER)
        ring.append(self._img_sprite('bonsai_circle', 80, 80))
        top_logo.append(ring)
        lbl_brand = Gtk.Label(label='Pixelzen')
        lbl_brand.add_css_class('pz-brand')
        top_logo.append(lbl_brand)
        side.append(top_logo)

        nav_items = [
            ('hub', 'Inicio', self._img_sprite('nav_home', 22, 20)),
            ('mundos', 'Mundos', self._img_sprite('nav_monitors', 22, 18)),
            ('pantallas', 'Pantallas', Gtk.Label(label='🖥')),
            ('hud', 'Widgets', self._img_sprite('nav_save', 22, 18)),
            ('sistema', 'Ajustes', self._img_sprite('gear', 20, 20)),
        ]
        for tab_id, label, icon_w in nav_items:
            btn = Gtk.Button()
            btn.add_css_class('pz-nav-btn')
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            icon_w.set_size_request(24, -1)
            row.append(icon_w)
            lbl = Gtk.Label(label=label)
            lbl.set_halign(Gtk.Align.START)
            row.append(lbl)
            btn.set_child(row)
            btn.connect('clicked', lambda _b, tid=tab_id: self._on_nav_click(tid))
            self._nav_btns[tab_id] = btn
            side.append(btn)

        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        side.append(spacer)

        bot = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        bot.set_margin_start(10)
        bot.set_margin_end(10)
        bot.set_margin_bottom(10)
        bot_img = self._img_sprite('bonsai_pot', 112, 98)
        bot_img.set_halign(Gtk.Align.CENTER)
        bot.append(bot_img)
        res_box = Gtk.Box()
        res_box.add_css_class('pz-resumen-box')
        self.lbl_resumen = Gtk.Label(label='')
        self.lbl_resumen.set_wrap(True)
        self.lbl_resumen.set_halign(Gtk.Align.START)
        res_box.append(self.lbl_resumen)
        bot.append(res_box)
        side.append(bot)
        return side

    def _wrap_hub_card(self, card_inner, css_inner, title_txt, hdr_css, star_tip, star_cb, extra_tl=None):
        overlay = Gtk.Overlay()
        outer = Gtk.Box()
        outer.add_css_class('pz-hub-outer')
        outer.set_hexpand(True)
        outer.set_vexpand(True)

        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        inner.add_css_class(css_inner)
        inner.set_hexpand(True)
        inner.set_vexpand(True)
        inner.append(card_inner)
        outer.append(inner)
        overlay.set_child(outer)

        hdr = Gtk.Label(label=title_txt)
        hdr.add_css_class(hdr_css)
        hdr.set_halign(Gtk.Align.CENTER)
        hdr.set_valign(Gtk.Align.START)
        overlay.add_overlay(hdr)

        if extra_tl is not None:
            extra_tl.set_halign(Gtk.Align.START)
            extra_tl.set_valign(Gtk.Align.START)
            extra_tl.set_margin_top(20)
            extra_tl.set_margin_start(14)
            overlay.add_overlay(extra_tl)

        star_btn = Gtk.Button()
        star_btn.add_css_class('flat')
        star_btn.set_child(self._img_sprite('star', 19, 17))
        star_btn.set_tooltip_text(star_tip)
        star_btn.set_halign(Gtk.Align.END)
        star_btn.set_valign(Gtk.Align.START)
        star_btn.set_margin_top(16)
        star_btn.set_margin_end(10)
        star_btn.connect('clicked', star_cb)
        overlay.add_overlay(star_btn)
        return overlay

    def _build_page_hub(self):
        grid = Gtk.Grid(row_spacing=14, column_spacing=14, row_homogeneous=True, column_homogeneous=True)
        grid.set_margin_top(4)
        grid.set_margin_bottom(4)

        # --- TARJETA 1: ELEGIR TEMA ---
        t1_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        t1_box.set_vexpand(True)
        carousel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        carousel.set_vexpand(True)
        btn_prev = Gtk.Button(label='◀')
        btn_prev.add_css_class('pz-pill-btn')
        btn_prev.set_valign(Gtk.Align.CENTER)
        btn_prev.connect('clicked', lambda *_: self._hub_move_page(-1))
        carousel.append(btn_prev)

        slots_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, homogeneous=True)
        slots_box.set_hexpand(True)
        self._hub_slots = []
        for idx in range(3):
            slot_btn = Gtk.Button()
            slot_btn.add_css_class('flat')
            frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            frame.add_css_class('pz-slot-frame')
            ov = Gtk.Overlay()
            pic = Gtk.Picture()
            pic.set_can_shrink(True)
            pic.set_content_fit(Gtk.ContentFit.COVER)
            pic.set_size_request(90, 105)
            ov.set_child(pic)
            cap = Gtk.Label(label='')
            cap.add_css_class('pz-slot-caption')
            cap.set_valign(Gtk.Align.END)
            cap.set_ellipsize(3)  # Pango.EllipsizeMode.END
            ov.add_overlay(cap)
            frame.append(ov)
            slot_btn.set_child(frame)
            slot_btn.connect('clicked', self._on_hub_slot_click, idx)
            slots_box.append(slot_btn)
            self._hub_slots.append({'frame': frame, 'pic': pic, 'lbl': cap})
        carousel.append(slots_box)

        btn_next = Gtk.Button(label='▶')
        btn_next.add_css_class('pz-pill-btn')
        btn_next.set_valign(Gtk.Align.CENTER)
        btn_next.connect('clicked', lambda *_: self._hub_move_page(1))
        carousel.append(btn_next)
        t1_box.append(carousel)

        self.btn_hub_temas_lista = Gtk.Button(label='Temas: Fittoa, Konoha, Jujutsu...')
        self.btn_hub_temas_lista.add_css_class('flat')
        self.btn_hub_temas_lista.connect('clicked', lambda *_: self._ir_mundos_series())
        t1_box.append(self.btn_hub_temas_lista)

        card1 = self._wrap_hub_card(
            t1_box, 'pz-hub-blue', 'ELEGIR TEMA', 'pz-hub-hdr-blue',
            'Ver los 15 mundos', lambda *_: self._ir_mundos_series()
        )
        grid.attach(card1, 0, 0, 1, 1)

        # --- TARJETA 2: PANTALLAS ---
        t2_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        t2_box.set_vexpand(True)
        t2_cols = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, homogeneous=True)
        t2_cols.set_vexpand(True)

        btn_anim = Gtk.Button()
        btn_anim.add_css_class('flat')
        box_anim = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        fr_anim = Gtk.Box()
        fr_anim.add_css_class('pz-slot-frame')
        self.pic_hub_anim = Gtk.Picture()
        self.pic_hub_anim.set_can_shrink(True)
        self.pic_hub_anim.set_content_fit(Gtk.ContentFit.COVER)
        self.pic_hub_anim.set_size_request(110, 90)
        fr_anim.append(self.pic_hub_anim)
        box_anim.append(fr_anim)
        lbl_a1 = Gtk.Label(label='ANIMADOS')
        lbl_a1.set_markup('<span foreground="#F6C84C" weight="bold">ANIMADOS</span>')
        box_anim.append(lbl_a1)
        self.lbl_hub_anim_sub = Gtk.Label(label='2 Pantallas')
        self.lbl_hub_anim_sub.add_css_class('caption')
        box_anim.append(self.lbl_hub_anim_sub)
        btn_anim.set_child(box_anim)
        btn_anim.connect('clicked', self._on_hub_toggle_monitores)
        t2_cols.append(btn_anim)

        btn_est = Gtk.Button()
        btn_est.add_css_class('flat')
        box_est = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        fr_est = Gtk.Box()
        fr_est.add_css_class('pz-slot-frame')
        self.pic_hub_est = Gtk.Picture()
        self.pic_hub_est.set_can_shrink(True)
        self.pic_hub_est.set_content_fit(Gtk.ContentFit.COVER)
        self.pic_hub_est.set_size_request(110, 90)
        fr_est.append(self.pic_hub_est)
        box_est.append(fr_est)
        lbl_e1 = Gtk.Label()
        lbl_e1.set_markup('<span foreground="#F4F0E4" weight="bold">ESTÁTICOS</span>')
        box_est.append(lbl_e1)
        self.lbl_hub_est_sub = Gtk.Label(label='Noche / Bloqueo')
        self.lbl_hub_est_sub.add_css_class('caption')
        box_est.append(self.lbl_hub_est_sub)
        btn_est.set_child(box_est)
        btn_est.connect('clicked', self._on_hub_ciclar_fase)
        t2_cols.append(btn_est)
        t2_box.append(t2_cols)

        t2_bot = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        t2_bot.append(self._img_sprite('plant_left', 26, 22))
        btn_expl = Gtk.Button(label='Explorar')
        btn_expl.add_css_class('pz-pill-green')
        btn_expl.set_hexpand(True)
        btn_expl.set_halign(Gtk.Align.CENTER)
        btn_expl.connect('clicked', lambda *_: self._ir_mundos_imagenes())
        t2_bot.append(btn_expl)
        t2_bot.append(self._img_sprite('flower_right', 26, 20))
        t2_box.append(t2_bot)

        card2 = self._wrap_hub_card(
            t2_box, 'pz-hub-green', 'PANTALLAS', 'pz-hub-hdr-green',
            'Configurar pantallas y ciclos', lambda *_: self._cambia_pestana('pantallas')
        )
        grid.attach(card2, 1, 0, 1, 1)

        # --- TARJETA 3: WIDGETS ---
        t3_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        t3_box.set_vexpand(True)
        t3_tiles = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, homogeneous=True)
        t3_tiles.set_vexpand(True)

        # Mosaico 1: Reloj monitor
        btn_clk = Gtk.Button()
        btn_clk.add_css_class('flat')
        clk_wrap = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        clk_wrap.set_valign(Gtk.Align.CENTER)
        bezel = Gtk.Box()
        bezel.add_css_class('pz-tile-bezel')
        scr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        scr.add_css_class('pz-tile-screen')
        scr.set_hexpand(True)
        self.lbl_hub_clock = Gtk.Label(label='12:34')
        self.lbl_hub_clock.set_markup('<span foreground="#66F4EA" size="xx-large" weight="bold" font_family="monospace">12:34</span>')
        self.lbl_hub_clock_status = Gtk.Label(label='HUD ON')
        self.lbl_hub_clock_status.add_css_class('caption')
        scr.append(self.lbl_hub_clock)
        scr.append(self.lbl_hub_clock_status)
        bezel.append(scr)
        clk_wrap.append(bezel)
        btn_clk.set_child(clk_wrap)
        btn_clk.set_tooltip_text('Clic para activar o desactivar widgets HUD')
        btn_clk.connect('clicked', lambda *_: self._on_toggle_hud_ahora())
        t3_tiles.append(btn_clk)

        # Mosaico 2: Clima real
        btn_wth = Gtk.Button()
        btn_wth.add_css_class('flat')
        wth_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        wth_box.add_css_class('pz-tile-weather')
        wth_box.set_valign(Gtk.Align.CENTER)
        wth_img = self._img_sprite('weather', 60, 36)
        wth_img.set_halign(Gtk.Align.CENTER)
        wth_box.append(wth_img)
        self.lbl_hub_weather = Gtk.Label()
        self.lbl_hub_weather.set_markup('<span foreground="#FFFFFF" size="x-large" weight="bold">--°C</span>')
        wth_box.append(self.lbl_hub_weather)
        self.lbl_hub_weather_sub = Gtk.Label(label='DESPEJADO')
        self.lbl_hub_weather_sub.set_ellipsize(3)
        self.lbl_hub_weather_sub.add_css_class('caption')
        wth_box.append(self.lbl_hub_weather_sub)
        btn_wth.set_child(wth_box)
        btn_wth.set_tooltip_text('Clic para cambiar el clima atmosférico')
        btn_wth.connect('clicked', self._on_hub_ciclar_clima)
        t3_tiles.append(btn_wth)

        # Mosaico 3: Gato / Tarjetas HUD
        btn_cat = Gtk.Button()
        btn_cat.add_css_class('flat')
        cat_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        cat_box.add_css_class('pz-tile-cat')
        cat_box.set_valign(Gtk.Align.CENTER)
        cat_img = self._img_sprite('cat', 56, 50)
        cat_img.set_halign(Gtk.Align.CENTER)
        cat_box.append(cat_img)
        self.lbl_hub_cat_badge = Gtk.Label(label='9 TARJETAS')
        self.lbl_hub_cat_badge.add_css_class('caption')
        cat_box.append(self.lbl_hub_cat_badge)
        btn_cat.set_child(cat_box)
        btn_cat.set_tooltip_text('Clic para personalizar las 9 tarjetas HUD')
        btn_cat.connect('clicked', lambda *_: self._cambia_pestana('hud'))
        t3_tiles.append(btn_cat)
        t3_box.append(t3_tiles)

        btn_w_sub = Gtk.Button(label='Relojes, Clima, Mascotas y más')
        btn_w_sub.add_css_class('flat')
        btn_w_sub.connect('clicked', lambda *_: self._cambia_pestana('hud'))
        t3_box.append(btn_w_sub)

        card3 = self._wrap_hub_card(
            t3_box, 'pz-hub-purple', 'WIDGETS', 'pz-hub-hdr-purple',
            'Personalizar widgets HUD', lambda *_: self._cambia_pestana('hud'),
            extra_tl=self._img_sprite('sprout', 18, 16)
        )
        grid.attach(card3, 0, 1, 1, 1)

        # --- TARJETA 4: AJUSTES ---
        t4_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        t4_box.set_vexpand(True)

        t4_left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        t4_left.set_valign(Gtk.Align.CENTER)
        t4_left.set_size_request(112, -1)
        t4_gear = self._img_sprite('gear', 72, 68)
        t4_gear.set_halign(Gtk.Align.CENTER)
        t4_left.append(t4_gear)
        btn_ir_aj = Gtk.Button(label='Ajustes')
        btn_ir_aj.add_css_class('pz-pill-btn')
        btn_ir_aj.set_halign(Gtk.Align.CENTER)
        btn_ir_aj.connect('clicked', lambda *_: self._cambia_pestana('sistema'))
        t4_left.append(btn_ir_aj)
        t4_box.append(t4_left)

        t4_right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
        t4_right.set_hexpand(True)
        t4_right.set_valign(Gtk.Align.CENTER)

        self.lbl_hub_gen_val = self._add_hub_row(t4_right, 'General', 'Ciclo 90m', self._on_hub_ciclar_modo)
        self.lbl_hub_rend_val = self._add_hub_row(t4_right, 'Animación', 'Activa 8 FPS', self._on_hub_toggle_anim)
        self.lbl_hub_ev_val = self._add_hub_row(t4_right, 'Evento Épico', '✦ Disparar', lambda *_: self._on_evento_ahora())

        sld_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        btn_menos = Gtk.Button(label='-')
        btn_menos.add_css_class('pz-pill-btn')
        btn_menos.connect('clicked', lambda *_: self._nudge_hora(-1.5))
        sld_box.append(btn_menos)
        self.scl_hub_hora = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.0, 23.75, 0.25)
        self.scl_hub_hora.set_draw_value(False)
        self.scl_hub_hora.set_hexpand(True)
        self.scl_hub_hora.connect('value-changed', self._on_hub_slider_hora)
        sld_box.append(self.scl_hub_hora)
        btn_mas = Gtk.Button(label='+')
        btn_mas.add_css_class('pz-pill-btn')
        btn_mas.connect('clicked', lambda *_: self._nudge_hora(1.5))
        sld_box.append(btn_mas)
        t4_right.append(sld_box)
        t4_box.append(t4_right)

        card4 = self._wrap_hub_card(
            t4_box, 'pz-hub-ocean', 'AJUSTES', 'pz-hub-hdr-ocean',
            'Ajustes del sistema', lambda *_: self._cambia_pestana('sistema')
        )
        grid.attach(card4, 1, 1, 1, 1)
        return grid

    def _add_hub_row(self, parent, title, init_val, cb):
        btn = Gtk.Button()
        btn.add_css_class('pz-hub-row')
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        l1 = Gtk.Label(label=title)
        l1.set_halign(Gtk.Align.START)
        l1.set_hexpand(True)
        l2 = Gtk.Label(label=init_val)
        l2.set_halign(Gtk.Align.END)
        l2.set_markup(f'<span foreground="#54DED4" weight="bold">{GLib.markup_escape_text(init_val)}</span>')
        box.append(l1)
        box.append(l2)
        btn.set_child(box)
        btn.connect('clicked', cb)
        parent.append(btn)
        return l2

    def _build_page_mundos(self):
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        self.mundos_scroll = scroll

        self.mundos_stack = Gtk.Stack()
        self.mundos_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        scroll.set_child(self.mundos_stack)

        # Vista 1: Series
        v_series = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        t1 = Gtk.Label(label='Elige tu Serie o Universo')
        t1.add_css_class('title-4')
        t1.set_halign(Gtk.Align.START)
        v_series.append(t1)
        sub1 = Gtk.Label(label='Selecciona un anime o universo. Si incluye varios escenarios podrás elegir mundo; si solo tiene uno pasarás directo a asignar escenas.')
        sub1.add_css_class('dim-label')
        sub1.set_wrap(True)
        sub1.set_halign(Gtk.Align.START)
        v_series.append(sub1)

        lista_series = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        for s_name in SERIES_ORDEN:
            s_temas = SERIES_MAP[s_name]
            rep = next((x for x in s_temas if x['id'] == self.tema_sel), s_temas[0])
            titulos = ' · '.join(x['titulo'] for x in s_temas)
            sub_txt = f"{len(s_temas)} escenarios: {titulos}" if len(s_temas) > 1 else f"Escenario único: {s_temas[0]['titulo']}"
            hint_txt = 'Explorar los mundos de esta serie →' if len(s_temas) > 1 else 'Elegir escenas de pantallas y bloqueo →'
            btn_s, (card, badge) = self._crear_card_lista(
                rep['id'], s_name, [sub_txt, hint_txt],
                lambda _b, sn=s_name: self._on_serie_click(sn),
            )
            self._series_cards[s_name] = (card, badge)
            lista_series.append(btn_s)
        v_series.append(lista_series)
        self.mundos_stack.add_named(v_series, 'series')

        # Vista 2: Mundos de la serie
        v_temas = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        hdr2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_back_s = Gtk.Button(label='← Series')
        btn_back_s.add_css_class('pz-pill-btn')
        btn_back_s.connect('clicked', lambda *_: self._cambia_vista_mundo('series'))
        hdr2.append(btn_back_s)
        self.lbl_serie_titulo = Gtk.Label(label='Mushoku Tensei')
        self.lbl_serie_titulo.add_css_class('title-4')
        hdr2.append(self.lbl_serie_titulo)
        v_temas.append(hdr2)

        lista_temas = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        for tm in TEMAS:
            btn_w, (card, badge) = self._crear_card_lista(
                tm['id'], tm['titulo'],
                [f"1 · {tm['m1']}", f"2 · {tm['m2']}", f"3 · Bloqueo: {tm['m3']}"],
                lambda _b, tid=tm['id']: self._on_mundo_click(tid),
            )
            self._world_cards[tm['id']] = (card, badge, tm['serie'])
            lista_temas.append(btn_w)
        v_temas.append(lista_temas)
        self.mundos_stack.add_named(v_temas, 'temas')

        # Vista 3: Selector visual 3x3 por pantalla
        v_imgs = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        hdr3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_back_m = Gtk.Button(label='← Volver')
        btn_back_m.add_css_class('pz-pill-btn')
        btn_back_m.connect('clicked', self._on_volver_de_imagenes)
        hdr3.append(btn_back_m)
        self.lbl_tema_imgs_titulo = Gtk.Label(label='Región de Fittoa')
        self.lbl_tema_imgs_titulo.add_css_class('title-4')
        self.lbl_tema_imgs_titulo.set_ellipsize(3)
        hdr3.append(self.lbl_tema_imgs_titulo)
        v_imgs.append(hdr3)

        sub3 = Gtk.Label(label='Asigna libremente cualquiera de las 3 escenas a cada monitor y a la pantalla de bloqueo:')
        sub3.add_css_class('dim-label')
        sub3.set_wrap(True)
        sub3.set_halign(Gtk.Align.START)
        v_imgs.append(sub3)

        presets = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        btn_p_cl = Gtk.Button(label='✦ Clásica (1·2·3)')
        btn_p_cl.add_css_class('pz-pill-cyan')
        btn_p_cl.connect('clicked', lambda *_: self._aplicar_preset_escenas('clasica'))
        presets.append(btn_p_cl)
        self.btn_rep_p = Gtk.Button(label='✨ Todas: Escena 1')
        self.btn_rep_p.add_css_class('pz-pill-btn')
        self.btn_rep_p.connect('clicked', lambda *_: self._aplicar_preset_escenas('principal'))
        presets.append(self.btn_rep_p)
        self.btn_rep_s = Gtk.Button(label='✨ Todas: Escena 2')
        self.btn_rep_s.add_css_class('pz-pill-btn')
        self.btn_rep_s.connect('clicked', lambda *_: self._aplicar_preset_escenas('secundaria'))
        presets.append(self.btn_rep_s)
        self.btn_rep_b = Gtk.Button(label='✨ Todas: Escena 3')
        self.btn_rep_b.add_css_class('pz-pill-btn')
        self.btn_rep_b.connect('clicked', lambda *_: self._aplicar_preset_escenas('bloqueo'))
        presets.append(self.btn_rep_b)
        v_imgs.append(presets)

        self.box_picker_m1 = self._build_picker_section('🖥️ MONITOR PRINCIPAL', 'principal', '#54DED4')
        v_imgs.append(self.box_picker_m1)
        self.box_picker_m2 = self._build_picker_section('🖥️ MONITOR SECUNDARIO', 'secundaria', '#F6C84C')
        v_imgs.append(self.box_picker_m2)
        self.box_picker_bloq = self._build_picker_section('🔒 PANTALLA DE BLOQUEO DE GNOME', 'bloqueo', '#88C8FF', con_check=True)
        v_imgs.append(self.box_picker_bloq)

        btn_ir_pant = Gtk.Button(label='⚙️ Ajustar monitores, clima y ciclo horario de luz →')
        btn_ir_pant.add_css_class('pz-pill-btn')
        btn_ir_pant.set_halign(Gtk.Align.START)
        btn_ir_pant.connect('clicked', lambda *_: self._cambia_pestana('pantallas'))
        v_imgs.append(btn_ir_pant)

        self.mundos_stack.add_named(v_imgs, 'imagenes')
        return scroll

    def _crear_card_lista(self, preview_tema_id, titulo, lineas, on_click):
        btn = Gtk.Button()
        btn.add_css_class('flat')
        btn.connect('clicked', on_click)

        card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        card.add_css_class('pz-card-item')
        pic = Gtk.Picture()
        pic.set_size_request(142, 86)
        pic.set_can_shrink(True)
        pic.set_content_fit(Gtk.ContentFit.COVER)
        ruta = _resolver_preview(preview_tema_id, 'dorado', 'principal') or _resolver_preview(preview_tema_id, 'noche', 'principal')
        if ruta:
            pic.set_filename(ruta)
        card.append(pic)

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        info.set_hexpand(True)
        info.set_valign(Gtk.Align.CENTER)
        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        lbl_t = Gtk.Label(label=titulo)
        lbl_t.set_halign(Gtk.Align.START)
        lbl_t.set_hexpand(True)
        lbl_t.add_css_class('heading')
        badge = Gtk.Label(label='ACTIVO')
        badge.add_css_class('pz-active-badge')
        top.append(lbl_t)
        top.append(badge)
        info.append(top)

        for idx, txt in enumerate(lineas):
            l = Gtk.Label(label=txt)
            l.set_halign(Gtk.Align.START)
            l.set_ellipsize(3)
            l.add_css_class('caption' if idx > 0 else 'dim-label')
            info.append(l)

        card.append(info)
        btn.set_child(card)
        return btn, (card, badge)

    def _build_picker_section(self, titulo, rol, color_hex, con_check=False):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.add_css_class('pz-section-card')
        if con_check:
            self.chk_bloq_menu = Gtk.CheckButton(label=titulo)
            self.chk_bloq_menu.connect('toggled', self._on_bloq_menu_toggled)
            box.append(self.chk_bloq_menu)
        else:
            lbl = Gtk.Label()
            lbl.set_markup(f'<span foreground="{color_hex}" weight="bold">{GLib.markup_escape_text(titulo)}</span>')
            lbl.set_halign(Gtk.Align.START)
            box.append(lbl)

        grid = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, homogeneous=True)
        for esc_id, _esc_nom in VARIANTES:
            b = Gtk.Button()
            b.add_css_class('flat')
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            card.add_css_class('pz-picker-card')
            ov = Gtk.Overlay()
            pic = Gtk.Picture()
            pic.set_size_request(110, 68)
            pic.set_can_shrink(True)
            pic.set_content_fit(Gtk.ContentFit.COVER)
            ov.set_child(pic)
            chk_lbl = Gtk.Label(label='✓')
            chk_lbl.add_css_class('pz-active-badge')
            chk_lbl.set_halign(Gtk.Align.END)
            chk_lbl.set_valign(Gtk.Align.START)
            chk_lbl.set_margin_top(4)
            chk_lbl.set_margin_end(4)
            ov.add_overlay(chk_lbl)
            card.append(ov)
            lbl = Gtk.Label(label=esc_id)
            lbl.set_ellipsize(3)
            lbl.add_css_class('caption')
            card.append(lbl)
            b.set_child(card)
            b.connect('clicked', self._on_picker_click, rol, esc_id)
            grid.append(b)
            self._picker_items.append({'rol': rol, 'escena': esc_id, 'card': card, 'pic': pic, 'lbl': lbl, 'chk': chk_lbl})
        box.append(grid)
        return box

    def _build_page_pantallas(self):
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_bottom(12)
        scroll.set_child(box)

        grp_mon = Adw.PreferencesGroup(
            title='Disposición de Pantallas',
            description='En modo 2 pantallas, tu monitor principal muestra la escena base y el segundo continúa la historia.',
        )
        self.combo_mon = Adw.ComboRow(
            title='Pantallas activas',
            model=Gtk.StringList.new(['Solo 1 Pantalla (Únicamente monitor principal)', '2 Pantallas (Principal + Continuación extendida)']),
        )
        self.combo_mon.connect('notify::selected', lambda *_: self._actualiza_vista())
        grp_mon.add(self.combo_mon)
        box.append(grp_mon)

        grp_esc = Adw.PreferencesGroup(title='Escena por Pantalla y Bloqueo')
        self.combo_fp = Adw.ComboRow(title='🖥️ Pantalla Principal', model=Gtk.StringList.new([n for _, n in VARIANTES]))
        self.combo_fp.connect('notify::selected', lambda *_: self._actualiza_vista() if not self._syncing else None)
        grp_esc.add(self.combo_fp)

        self.combo_fs = Adw.ComboRow(title='🖥️ Pantalla Secundaria', model=Gtk.StringList.new([n for _, n in VARIANTES]))
        self.combo_fs.connect('notify::selected', lambda *_: self._actualiza_vista() if not self._syncing else None)
        grp_esc.add(self.combo_fs)

        sec_temas = ['🔗 Mismo mundo que Monitor 1 (continuación)'] + [f"{t['anime']} · {t['titulo']}" for t in TEMAS]
        self.combo_ts = Adw.ComboRow(title='🌍 Mundo independiente en Monitor 2', model=Gtk.StringList.new(sec_temas))
        self.combo_ts.connect('notify::selected', lambda *_: self._actualiza_vista() if not self._syncing else None)
        grp_esc.add(self.combo_ts)

        self.row_bloq = Adw.SwitchRow(title='🔒 Aplicar fondo a la Pantalla de Bloqueo de GNOME')
        self.row_bloq.connect('notify::active', self._on_row_bloq_toggled)
        grp_esc.add(self.row_bloq)

        self.combo_fb = Adw.ComboRow(title='Escena de bloqueo', model=Gtk.StringList.new([n for _, n in VARIANTES]))
        self.combo_fb.connect('notify::selected', lambda *_: self._actualiza_vista() if not self._syncing else None)
        grp_esc.add(self.combo_fb)
        box.append(grp_esc)

        grp_luz = Adw.PreferencesGroup(title='Ciclo de Luz del Cielo')
        self.combo_modo = Adw.ComboRow(title='Modo horario', model=Gtk.StringList.new([n for _, n in MODOS]))
        self.combo_modo.connect('notify::selected', self._on_modo_changed)
        grp_luz.add(self.combo_modo)

        self.row_hora = Adw.SpinRow.new_with_range(0.0, 23.75, 0.25)
        self.row_hora.set_title('Hora fija (0 – 23.75 h)')
        self.row_hora.set_digits(2)
        self.row_hora.connect('notify::value', self._on_hora_spin_changed)
        grp_luz.add(self.row_hora)

        preset_hora = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        preset_hora.set_margin_top(4)
        for label, hv, f_id in [('☀️ Día (13:00)', 13.0, 'dia'), ('🌅 Atardecer (18:30)', 18.5, 'dorado'), ('🌙 Noche (22:00)', 22.0, 'noche')]:
            b = Gtk.Button(label=label)
            b.add_css_class('pz-pill-btn')
            b.connect('clicked', self._on_fijar_hora_preset, hv, f_id)
            preset_hora.append(b)
        grp_luz.add(preset_hora)

        self.row_animar = Adw.SwitchRow(title='Animación continua (nubes, aves y partículas)')
        self.row_animar.connect('notify::active', lambda *_: self._actualiza_vista())
        grp_luz.add(self.row_animar)

        self.row_fps = Adw.SpinRow.new_with_range(2, 24, 1)
        self.row_fps.set_title('Fluidez de animación (FPS)')
        grp_luz.add(self.row_fps)
        box.append(grp_luz)

        grp_clima = Adw.PreferencesGroup(title='Clima Dinámico &amp; Rotación Automática')
        self.combo_clima = Adw.ComboRow(title='🌦️ Clima atmosférico', model=Gtk.StringList.new([n for _, n in CLIMAS]))
        self.combo_clima.connect('notify::selected', lambda *_: self._actualiza_vista())
        grp_clima.add(self.combo_clima)

        self.combo_rot = Adw.ComboRow(title='🔀 Playlist — Cambio automático de mundo', model=Gtk.StringList.new([n for _, n in ROTACIONES]))
        grp_clima.add(self.combo_rot)
        box.append(grp_clima)
        return scroll

    def _build_page_hud(self):
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_bottom(12)
        scroll.set_child(box)

        grp_top = Adw.PreferencesGroup(
            title='Tarjetas Flotantes (HUD)',
            description='Transparentes al ratón en el lateral derecho de tu escritorio.',
        )
        self.row_hud = Adw.SwitchRow(title='Mostrar panel de datos sobre el escritorio')
        self.row_hud.connect('notify::active', lambda *_: self._actualiza_vista())
        grp_top.add(self.row_hud)
        box.append(grp_top)

        # Solo Widgets card
        solo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        solo_box.add_css_class('pz-solo-card')
        solo_txt = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        solo_txt.set_hexpand(True)
        self.chk_solo_widgets = Gtk.CheckButton(label='🧩 Modo Solo Widgets (Usar con tu propio fondo de GNOME)')
        self.chk_solo_widgets.connect('toggled', lambda *_: self._actualiza_vista() if not self._syncing else None)
        solo_txt.append(self.chk_solo_widgets)
        lbl_sw_sub = Gtk.Label(label='Superpone las tarjetas HUD sobre tu fondo actual sin reemplazar el wallpaper de GNOME.')
        lbl_sw_sub.add_css_class('caption')
        lbl_sw_sub.set_wrap(True)
        lbl_sw_sub.set_halign(Gtk.Align.START)
        solo_txt.append(lbl_sw_sub)
        solo_box.append(solo_txt)
        btn_solo_go = Gtk.Button(label='⚡ Activar Solo Widgets')
        btn_solo_go.add_css_class('pz-cta-btn')
        btn_solo_go.set_valign(Gtk.Align.CENTER)
        btn_solo_go.connect('clicked', lambda *_: self._activar_solo_widgets())
        solo_box.append(btn_solo_go)
        box.append(solo_box)

        presets = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        for label, mode in [('✦ Mostrar todas (9)', 'all'), ('Modo limpio (Reloj + Frase)', 'min'), ('Solo Reloj', 'clock')]:
            b = Gtk.Button(label=label)
            b.add_css_class('pz-pill-btn')
            b.connect('clicked', self._on_hud_preset, mode)
            presets.append(b)
        box.append(presets)

        grp_opts = Adw.PreferencesGroup()
        self.row_compacto = Adw.SwitchRow(title='🗜️ Modo HUD compacto + paleta adaptada al mundo')
        self.row_compacto.connect('notify::active', lambda *_: self._actualiza_vista())
        grp_opts.add(self.row_compacto)
        box.append(grp_opts)

        grp_cards = Adw.PreferencesGroup(title='9 Tarjetas Disponibles')
        for clave, titulo, subtitulo, _mock in STATS_META:
            sw = Adw.SwitchRow(title=titulo, subtitle=subtitulo)
            sw.connect('notify::active', lambda *_: self._actualiza_vista())
            self._switches_hud[clave] = sw
            grp_cards.add(sw)
        box.append(grp_cards)
        return scroll

    def _build_page_sistema(self):
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_bottom(12)
        scroll.set_child(box)

        ev_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        ev_box.add_css_class('pz-section-card')
        lbl_ev = Gtk.Label()
        lbl_ev.set_markup('<span foreground="#F6C84C" weight="bold">Eventos Épicos en Tiempo Real</span>')
        lbl_ev.set_halign(Gtk.Align.START)
        ev_box.append(lbl_ev)
        lbl_ev_sub = Gtk.Label(label='Dispara un cometa, círculo de invocación o anomalía dimensional sobre tu escritorio GNOME.')
        lbl_ev_sub.add_css_class('dim-label')
        lbl_ev_sub.set_wrap(True)
        lbl_ev_sub.set_halign(Gtk.Align.START)
        ev_box.append(lbl_ev_sub)
        btn_ev = Gtk.Button(label='✦ Disparar evento épico ahora')
        btn_ev.add_css_class('pz-pill-btn')
        btn_ev.set_halign(Gtk.Align.START)
        btn_ev.connect('clicked', lambda *_: self._on_evento_ahora())
        ev_box.append(btn_ev)
        box.append(ev_box)

        sc_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        sc_box.add_css_class('pz-section-card')
        lbl_sc = Gtk.Label()
        lbl_sc.set_markup('<span foreground="#F6C84C" weight="bold">Acceso directo e Integración GNOME</span>')
        lbl_sc.set_halign(Gtk.Align.START)
        sc_box.append(lbl_sc)
        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_desk = Gtk.Button(label='📌 Crear acceso directo en Escritorio')
        btn_desk.add_css_class('pz-pill-cyan')
        btn_desk.connect('clicked', self._on_crear_acceso_directo)
        btn_row.append(btn_desk)
        btn_ext_en = Gtk.Button(label='🔌 Activar extensión GNOME')
        btn_ext_en.add_css_class('pz-pill-btn')
        btn_ext_en.connect('clicked', self._on_activar_ext)
        btn_row.append(btn_ext_en)
        sc_box.append(btn_row)
        box.append(sc_box)

        diag_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        diag_box.add_css_class('pz-section-card')
        lbl_dg = Gtk.Label()
        lbl_dg.set_markup('<span foreground="#F6C84C" weight="bold">Estado del sistema y actualizaciones</span>')
        lbl_dg.set_halign(Gtk.Align.START)
        diag_box.append(lbl_dg)
        self.lbl_diag = Gtk.Label(label='')
        self.lbl_diag.set_wrap(True)
        self.lbl_diag.set_halign(Gtk.Align.START)
        diag_box.append(self.lbl_diag)
        act_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_upd = Gtk.Button(label='🔄 Buscar actualización')
        btn_upd.add_css_class('pz-pill-cyan')
        btn_upd.connect('clicked', self._on_buscar_actualizacion)
        act_row.append(btn_upd)
        btn_rst = Gtk.Button(label='Restablecer recomendados')
        btn_rst.add_css_class('pz-pill-btn')
        btn_rst.connect('clicked', self._on_restaurar)
        act_row.append(btn_rst)
        diag_box.append(act_row)
        box.append(diag_box)
        return scroll

    def _build_studio_preview(self):
        panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        panel.add_css_class('pz-studio-panel')
        panel.set_size_request(368, -1)

        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        lbl = Gtk.Label()
        lbl.set_markup('<span foreground="#54DED4" weight="bold">ESCRITORIO EN VIVO</span>')
        lbl.set_halign(Gtk.Align.START)
        lbl.set_hexpand(True)
        top.append(lbl)

        fase_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        first = None
        for fid, fnom in FASES:
            b = Gtk.ToggleButton(label=fnom)
            b.add_css_class('pz-seg-btn')
            if first is None:
                first = b
            else:
                b.set_group(first)
            b.set_active(fid == self.fase_sel)
            b.connect('toggled', self._on_fase_toggled, fid)
            self._fase_btns[fid] = b
            fase_box.append(b)
        top.append(fase_box)
        panel.append(top)

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scroll.set_child(inner)
        panel.append(scroll)

        # Pantalla 1 + Mock HUD
        h1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.lbl_prev1_title = Gtk.Label(label='PANTALLA 1')
        self.lbl_prev1_title.set_halign(Gtk.Align.START)
        self.lbl_prev1_title.set_hexpand(True)
        self.lbl_prev1_title.set_ellipsize(3)
        b1 = Gtk.Label(label='PRINCIPAL')
        b1.add_css_class('pz-active-badge')
        h1.append(self.lbl_prev1_title)
        h1.append(b1)
        inner.append(h1)

        ov1 = Gtk.Overlay()
        ov1.add_css_class('pz-prev-box')
        self.pic_prev1 = Gtk.Picture()
        self.pic_prev1.set_size_request(320, 148)
        self.pic_prev1.set_can_shrink(True)
        self.pic_prev1.set_content_fit(Gtk.ContentFit.COVER)
        ov1.set_child(self.pic_prev1)

        self.mock_hud_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        self.mock_hud_box.set_halign(Gtk.Align.END)
        self.mock_hud_box.set_valign(Gtk.Align.START)
        self.mock_hud_box.set_margin_top(4)
        self.mock_hud_box.set_margin_end(5)
        for clave, _tit, _sub, mock_txt in STATS_META:
            lbl_m = Gtk.Label(label=mock_txt)
            lbl_m.add_css_class('pz-mock-card')
            lbl_m.set_halign(Gtk.Align.END)
            self._mock_cards[clave] = lbl_m
            self.mock_hud_box.append(lbl_m)
        ov1.add_overlay(self.mock_hud_box)
        inner.append(ov1)

        # Pantalla 2
        self.box_prev2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        h2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.lbl_prev2_title = Gtk.Label(label='PANTALLA 2')
        self.lbl_prev2_title.set_halign(Gtk.Align.START)
        self.lbl_prev2_title.set_hexpand(True)
        self.lbl_prev2_title.set_ellipsize(3)
        b2 = Gtk.Label(label='MONITOR 2')
        b2.add_css_class('pz-active-badge')
        h2.append(self.lbl_prev2_title)
        h2.append(b2)
        self.box_prev2.append(h2)
        fr2 = Gtk.Box()
        fr2.add_css_class('pz-prev-box-m2')
        self.pic_prev2 = Gtk.Picture()
        self.pic_prev2.set_size_request(320, 114)
        self.pic_prev2.set_can_shrink(True)
        self.pic_prev2.set_content_fit(Gtk.ContentFit.COVER)
        fr2.append(self.pic_prev2)
        self.box_prev2.append(fr2)
        inner.append(self.box_prev2)

        # Pantalla de Bloqueo
        self.box_prev_bloq = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        h3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.lbl_prev_bloq_title = Gtk.Label(label='🔒 BLOQUEO')
        self.lbl_prev_bloq_title.set_halign(Gtk.Align.START)
        self.lbl_prev_bloq_title.set_hexpand(True)
        self.lbl_prev_bloq_title.set_ellipsize(3)
        b3 = Gtk.Label(label='GNOME LOCK')
        b3.add_css_class('pz-active-badge')
        h3.append(self.lbl_prev_bloq_title)
        h3.append(b3)
        self.box_prev_bloq.append(h3)
        ov3 = Gtk.Overlay()
        ov3.add_css_class('pz-prev-box-lock')
        self.pic_prev_bloq = Gtk.Picture()
        self.pic_prev_bloq.set_size_request(320, 96)
        self.pic_prev_bloq.set_can_shrink(True)
        self.pic_prev_bloq.set_content_fit(Gtk.ContentFit.COVER)
        ov3.set_child(self.pic_prev_bloq)
        lock_clk = Gtk.Label()
        lock_clk.set_markup('<span foreground="#F6F4EA" size="x-large" weight="bold">21:34</span>')
        lock_clk.set_halign(Gtk.Align.CENTER)
        lock_clk.set_valign(Gtk.Align.START)
        lock_clk.set_margin_top(10)
        ov3.add_overlay(lock_clk)
        self.box_prev_bloq.append(ov3)
        inner.append(self.box_prev_bloq)
        return panel

    def _build_footer(self):
        foot = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        foot.add_css_class('pz-footer')

        btn_web = Gtk.Button(label='🎬 Visor Web')
        btn_web.add_css_class('pz-pill-cyan')
        btn_web.connect('clicked', self._on_visor_web)
        foot.append(btn_web)

        self.btn_toggle_hud = Gtk.Button(label='👁️ Ocultar HUD')
        self.btn_toggle_hud.add_css_class('pz-pill-btn')
        self.btn_toggle_hud.connect('clicked', lambda *_: self._on_toggle_hud_ahora())
        foot.append(self.btn_toggle_hud)

        self.btn_solo_bar = Gtk.Button(label='🧩 Solo Widgets')
        self.btn_solo_bar.add_css_class('pz-pill-cyan')
        self.btn_solo_bar.connect('clicked', self._on_solo_bar_click)
        foot.append(self.btn_solo_bar)

        self.lbl_status = Gtk.Label(label='Listo — Elige un tema y pulsa Aplicar.')
        self.lbl_status.set_halign(Gtk.Align.START)
        self.lbl_status.set_hexpand(True)
        self.lbl_status.set_ellipsize(3)
        foot.append(self.lbl_status)

        self.btn_guardar = Gtk.Button(label='💾 Guardar')
        self.btn_guardar.add_css_class('pz-pill-btn')
        self.btn_guardar.connect('clicked', lambda *_: self._on_guardar_solo())
        foot.append(self.btn_guardar)

        self.btn_aplicar = Gtk.Button(label='✦ APLICAR A MI ESCRITORIO')
        self.btn_aplicar.add_css_class('pz-cta-btn')
        self.btn_aplicar.connect('clicked', lambda *_: self._on_aplicar())
        foot.append(self.btn_aplicar)
        return foot

    def _cargar_estado_inicial(self):
        self._syncing = True
        try:
            s = self.settings
            n_mon = _get_int(s, 'num-monitores', 2)
            self.combo_mon.set_selected(1 if n_mon >= 2 else 0)

            fp = _get_str(s, 'fondo-principal', 'principal')
            fs = _get_str(s, 'fondo-secundario', 'secundaria')
            fb = _get_str(s, 'fondo-bloqueo', 'bloqueo')
            self.combo_fp.set_selected(max(0, next((i for i, (k, _) in enumerate(VARIANTES) if k == fp), 0)))
            self.combo_fs.set_selected(max(0, next((i for i, (k, _) in enumerate(VARIANTES) if k == fs), 1)))
            self.combo_fb.set_selected(max(0, next((i for i, (k, _) in enumerate(VARIANTES) if k == fb), 2)))

            ts = _get_str(s, 'tema-secundario', 'igual')
            ts_idx = 0
            if ts != 'igual':
                for idx, tm in enumerate(TEMAS, start=1):
                    if tm['id'] == ts:
                        ts_idx = idx
                        break
            self.combo_ts.set_selected(ts_idx)
            bloq_on = _get_bool(s, 'usar-bloqueo', True)
            self.row_bloq.set_active(bloq_on)
            self.chk_bloq_menu.set_active(bloq_on)

            if _ciclo90_activo():
                modo_idx = 0
            elif _get_bool(s, 'ciclo-rapido', False):
                modo_idx = 0 if _get_int(s, 'ciclo-duracion', 90) >= 3600 else 2
            elif s and s.get_double('hora-simulada') >= 0:
                modo_idx = 3
            else:
                modo_idx = 1
            self.combo_modo.set_selected(modo_idx)
            hv = s.get_double('hora-simulada') if s else -1.0
            hv_eff = hv if hv >= 0 else 21.5
            self.row_hora.set_value(hv_eff)
            self.scl_hub_hora.set_value(hv_eff)
            self.row_animar.set_active(_get_bool(s, 'animar', True))
            self.row_fps.set_value(_get_int(s, 'fps', 8))

            cl_id = _get_str(s, 'clima', 'normal')
            self.combo_clima.set_selected(max(0, next((i for i, (k, _) in enumerate(CLIMAS) if k == cl_id), 0)))
            rot_v = _get_int(s, 'rotacion-minutos', 0)
            self.combo_rot.set_selected(max(0, next((i for i, (v, _) in enumerate(ROTACIONES) if v == rot_v), 0)))

            self.row_hud.set_active(_get_bool(s, 'hud', True))
            self.chk_solo_widgets.set_active(_get_bool(s, 'solo-widgets', False))
            self.row_compacto.set_active(_get_bool(s, 'hud-compacto', False))
            for clave, sw in self._switches_hud.items():
                sw.set_active(_get_bool(s, clave, True))

            modo_id = MODOS[modo_idx][0]
            self.fase_sel = _detectar_fase(modo_id, hv_eff)
            if self.fase_sel in self._fase_btns:
                self._fase_btns[self.fase_sel].set_active(True)
        finally:
            self._syncing = False

    def _comprobar_estado_extension(self):
        if not _extension_instalada():
            self.banner.set_title('La extensión de GNOME no está instalada todavía (ejecuta linux/instalar.sh).')
            self.banner.set_revealed(True)
            self.btn_aplicar.set_sensitive(False)
            self.btn_guardar.set_sensitive(False)
        elif not _extension_activa():
            self.banner.set_title('La extensión PixelZen Worlds está instalada pero desactivada en GNOME.')
            self.banner.set_revealed(True)
            self.btn_aplicar.set_sensitive(True)
            self.btn_guardar.set_sensitive(True)
        else:
            self.banner.set_revealed(False)
            self.btn_aplicar.set_sensitive(True)
            self.btn_guardar.set_sensitive(True)

    def _on_activar_ext(self, *_args):
        subprocess.run(['gnome-extensions', 'enable', UUID], check=False)
        self._comprobar_estado_extension()
        self._actualiza_vista()
        self.lbl_status.set_text('Extensión activada en GNOME Shell.')

    def _cambia_pestana(self, tab_id):
        self.tab_actual = tab_id
        self.stack.set_visible_child_name(tab_id)
        for k, btn in self._nav_btns.items():
            if k == tab_id:
                btn.add_css_class('pz-nav-active')
            else:
                btn.remove_css_class('pz-nav-active')
        titles = {
            'mundos': f'Explorar Mundos y Escenas ({len(TEMAS)} Universos)',
            'pantallas': 'Disposición de Pantallas, Bloqueo, Clima y Luz',
            'hud': 'Widgets y Tarjetas Flotantes (HUD)',
            'sistema': 'Ajustes del Sistema y Eventos',
        }
        es_hub = (tab_id == 'hub')
        self.bar_detalle_top.set_visible(not es_hub)
        self.studio_panel.set_visible(not es_hub)
        if not es_hub:
            self.lbl_detalle_title.set_text(titles.get(tab_id, 'PixelZen'))

    def _on_nav_click(self, tab_id):
        self._cambia_pestana(tab_id)
        if tab_id == 'mundos':
            self._cambia_vista_mundo('series')

    def _cambia_vista_mundo(self, vista):
        self.vista_mundo = vista
        self.mundos_stack.set_visible_child_name(vista)
        if vista == 'temas':
            self.lbl_serie_titulo.set_text(self.serie_sel)
            for _tid, (card, _badge, serie) in self._world_cards.items():
                card.get_parent().set_visible(serie == self.serie_sel)
        elif vista == 'imagenes':
            tmeta = next((t for t in TEMAS if t['id'] == self.tema_sel), TEMAS[0])
            self.lbl_tema_imgs_titulo.set_text(f"{tmeta['serie']} · {tmeta['titulo']}")

    def _ir_mundos_series(self):
        self._cambia_pestana('mundos')
        self._cambia_vista_mundo('series')

    def _ir_mundos_imagenes(self):
        self._cambia_pestana('mundos')
        self._cambia_vista_mundo('imagenes')

    def _on_serie_click(self, serie_name):
        self.serie_sel = serie_name
        lista = SERIES_MAP.get(serie_name, TEMAS)
        if len(lista) > 1:
            if not any(t['id'] == self.tema_sel for t in lista):
                self.tema_sel = lista[0]['id']
            self._cambia_vista_mundo('temas')
        else:
            self.tema_sel = lista[0]['id']
            self._cambia_vista_mundo('imagenes')
        self._actualiza_vista()

    def _on_mundo_click(self, tid):
        self.tema_sel = tid
        tmeta = next((t for t in TEMAS if t['id'] == tid), TEMAS[0])
        self.serie_sel = tmeta['serie']
        self._cambia_vista_mundo('imagenes')
        self._actualiza_vista()

    def _on_volver_de_imagenes(self, *_args):
        lista = SERIES_MAP.get(self.serie_sel, [])
        self._cambia_vista_mundo('temas' if len(lista) > 1 else 'series')

    def _on_picker_click(self, _btn, rol, esc_id):
        self._syncing = True
        try:
            idx = next((i for i, (k, _) in enumerate(VARIANTES) if k == esc_id), 0)
            if rol == 'principal':
                self.combo_fp.set_selected(idx)
            elif rol == 'secundaria':
                self.combo_fs.set_selected(idx)
            elif rol == 'bloqueo':
                self.row_bloq.set_active(True)
                self.chk_bloq_menu.set_active(True)
                self.combo_fb.set_selected(idx)
        finally:
            self._syncing = False
        self._actualiza_vista()

    def _aplicar_preset_escenas(self, cual):
        self._syncing = True
        try:
            self.row_bloq.set_active(True)
            self.chk_bloq_menu.set_active(True)
            if cual == 'clasica':
                self.combo_fp.set_selected(0)
                self.combo_fs.set_selected(1)
                self.combo_fb.set_selected(2)
            else:
                idx = next((i for i, (k, _) in enumerate(VARIANTES) if k == cual), 0)
                self.combo_fp.set_selected(idx)
                self.combo_fs.set_selected(idx)
                self.combo_fb.set_selected(idx)
        finally:
            self._syncing = False
        self._actualiza_vista()

    def _on_bloq_menu_toggled(self, chk):
        if self._syncing:
            return
        self._syncing = True
        self.row_bloq.set_active(chk.get_active())
        self._syncing = False
        self._actualiza_vista()

    def _on_row_bloq_toggled(self, *_args):
        if self._syncing:
            return
        self._syncing = True
        self.chk_bloq_menu.set_active(self.row_bloq.get_active())
        self._syncing = False
        self._actualiza_vista()

    def _on_modo_changed(self, *_args):
        if self._syncing:
            return
        modo_id = MODOS[self.combo_modo.get_selected()][0]
        if modo_id == 'fija':
            self.fase_sel = _detectar_fase('fija', self.row_hora.get_value())
            if self.fase_sel in self._fase_btns:
                self._fase_btns[self.fase_sel].set_active(True)
        self._actualiza_vista()

    def _on_hora_spin_changed(self, *_args):
        if self._syncing:
            return
        self.fase_sel = _detectar_fase('fija', self.row_hora.get_value())
        if self.fase_sel in self._fase_btns:
            self._fase_btns[self.fase_sel].set_active(True)
        self._actualiza_vista()

    def _on_fijar_hora_preset(self, _btn, hv, f_id):
        self._syncing = True
        self.combo_modo.set_selected(3)
        self.row_hora.set_value(hv)
        self.scl_hub_hora.set_value(hv)
        self.fase_sel = f_id
        if f_id in self._fase_btns:
            self._fase_btns[f_id].set_active(True)
        self._syncing = False
        self._actualiza_vista()

    def _on_fase_toggled(self, btn, fid):
        if btn.get_active():
            self.fase_sel = fid
            self._actualiza_vista()

    def _hub_move_page(self, delta):
        total = max(1, (len(TEMAS) + 2) // 3)
        self.hub_page_idx = (self.hub_page_idx + delta) % total
        self._actualiza_vista()

    def _on_hub_slot_click(self, _btn, slot_idx):
        tid = self.hub_slot_ids[slot_idx]
        if tid:
            self.tema_sel = tid
            tmeta = next((t for t in TEMAS if t['id'] == tid), TEMAS[0])
            self.serie_sel = tmeta['serie']
            self._syncing = True
            self.chk_solo_widgets.set_active(False)
            self._syncing = False
            self._on_aplicar()

    def _on_hub_toggle_monitores(self, *_args):
        self.combo_mon.set_selected(0 if self.combo_mon.get_selected() == 1 else 1)
        self._on_aplicar()

    def _on_hub_ciclar_fase(self, *_args):
        orden = ['dia', 'dorado', 'noche']
        sig = orden[(orden.index(self.fase_sel) + 1) % 3] if self.fase_sel in orden else 'dorado'
        self.fase_sel = sig
        if sig in self._fase_btns:
            self._fase_btns[sig].set_active(True)
        self._actualiza_vista()
        self._on_aplicar()

    def _on_hub_ciclar_clima(self, *_args):
        nxt = (self.combo_clima.get_selected() + 1) % len(CLIMAS)
        self.combo_clima.set_selected(nxt)
        cl_id = CLIMAS[nxt][0]
        _set_safe(self.settings, 's', 'clima', cl_id)
        if self.settings:
            Gio.Settings.sync()
        self._actualiza_vista()
        self.lbl_status.set_text(f'🌦️ Clima cambiado a: {cl_id}')

    def _on_hub_ciclar_modo(self, *_args):
        nxt = (self.combo_modo.get_selected() + 1) % len(MODOS)
        self.combo_modo.set_selected(nxt)
        self._actualiza_vista()

    def _on_hub_toggle_anim(self, *_args):
        self.row_animar.set_active(not self.row_animar.get_active())
        _set_safe(self.settings, 'b', 'animar', self.row_animar.get_active())
        if self.settings:
            Gio.Settings.sync()
        self._actualiza_vista()

    def _on_hub_slider_hora(self, scl):
        if self._syncing:
            return
        hv = scl.get_value()
        self._syncing = True
        self.combo_modo.set_selected(3)
        self.row_hora.set_value(hv)
        self.fase_sel = _detectar_fase('fija', hv)
        if self.fase_sel in self._fase_btns:
            self._fase_btns[self.fase_sel].set_active(True)
        self._syncing = False
        self._actualiza_vista()

    def _nudge_hora(self, delta):
        v = max(0.0, min(23.75, self.scl_hub_hora.get_value() + delta))
        self.scl_hub_hora.set_value(v)

    def _on_hud_preset(self, _btn, mode):
        self._syncing = True
        self.row_hud.set_active(True)
        for k, sw in self._switches_hud.items():
            if mode == 'all':
                sw.set_active(True)
            elif mode == 'min':
                sw.set_active(k in ('hud-tiempo', 'hud-grimorio'))
            else:
                sw.set_active(k == 'hud-tiempo')
        self._syncing = False
        self._actualiza_vista()

    def _on_toggle_hud_ahora(self):
        nuevo = not self.row_hud.get_active()
        self.row_hud.set_active(nuevo)
        _set_safe(self.settings, 'b', 'hud', nuevo)
        if self.settings:
            Gio.Settings.sync()
        self._actualiza_vista()
        self.lbl_status.set_text('✅ Tarjetas HUD mostradas.' if nuevo else 'Cajitas HUD ocultadas del escritorio.')

    def _activar_solo_widgets(self):
        self._syncing = True
        self.chk_solo_widgets.set_active(True)
        self.row_hud.set_active(True)
        self._syncing = False
        self._on_aplicar()

    def _on_solo_bar_click(self, *_args):
        if not self.chk_solo_widgets.get_active():
            self._activar_solo_widgets()
        else:
            self._syncing = True
            self.chk_solo_widgets.set_active(False)
            self._syncing = False
            self._on_aplicar()

    def _on_evento_ahora(self):
        if self.settings:
            seq = _get_int(self.settings, 'evento-seq', 0) + 1
            _set_safe(self.settings, 'i', 'evento-seq', seq)
            Gio.Settings.sync()
        self.lbl_status.set_text('✦ Evento épico enviado al fondo de escritorio.')

    def _on_crear_acceso_directo(self, *_args):
        src = os.path.expanduser('~/.local/share/applications/pixelzen-worlds.desktop')
        desk = None
        for cand in ('Desktop', 'Escritorio'):
            p = os.path.expanduser(f'~/{cand}')
            if os.path.isdir(p):
                desk = p
                break
        if not desk or not os.path.isfile(src):
            self.lbl_status.set_text('ℹ️ Ejecuta linux/instalar.sh para registrar el lanzador primero.')
            return
        dst = os.path.join(desk, 'pixelzen-worlds.desktop')
        shutil.copy2(src, dst)
        os.chmod(dst, os.stat(dst).st_mode | stat.S_IXUSR)
        self.lbl_status.set_text(f'✅ Acceso directo creado en {dst}')

    def _on_restaurar(self, *_args):
        self._syncing = True
        try:
            self.tema_sel = 'fittoa'
            self.serie_sel = 'Mushoku Tensei'
            self.combo_mon.set_selected(1)
            self.combo_fp.set_selected(0)
            self.combo_fs.set_selected(1)
            self.combo_fb.set_selected(2)
            self.combo_ts.set_selected(0)
            self.row_bloq.set_active(True)
            self.chk_bloq_menu.set_active(True)
            self.combo_modo.set_selected(0)
            self.row_animar.set_active(True)
            self.row_fps.set_value(8)
            self.combo_clima.set_selected(0)
            self.combo_rot.set_selected(0)
            self.row_hud.set_active(True)
            self.chk_solo_widgets.set_active(False)
            self.row_compacto.set_active(False)
            for sw in self._switches_hud.values():
                sw.set_active(True)
        finally:
            self._syncing = False
        self._actualiza_vista()
        self.lbl_status.set_text('Valores recomendados cargados. Pulsa Aplicar a mi escritorio.')

    def _tick_reloj(self):
        import datetime
        self.lbl_hub_clock.set_markup(
            f'<span foreground="#66F4EA" size="xx-large" weight="bold" font_family="monospace">{datetime.datetime.now().strftime("%H:%M")}</span>'
        )
        return GLib.SOURCE_CONTINUE

    def _cargar_clima_async(self):
        if os.path.isfile(CLIMA_CACHE_PATH):
            try:
                self.clima_real = json.loads(open(CLIMA_CACHE_PATH, 'r', encoding='utf-8').read())
                self._actualiza_vista()
            except Exception:
                pass

        def _worker():
            app_dir = os.path.dirname(os.path.abspath(__file__))
            repo_root = os.path.dirname(app_dir)
            for cand in (os.path.join(app_dir, 'clima.py'), os.path.join(repo_root, 'src', 'clima.py'), os.path.join(EXT_DIR, 'code', 'clima.py')):
                if os.path.isfile(cand):
                    try:
                        out = subprocess.run([sys.executable, cand], capture_output=True, text=True, timeout=6).stdout
                        data = json.loads(out)
                        if isinstance(data, dict):
                            GLib.idle_add(self._on_clima_listo, data)
                    except Exception:
                        pass
                    break

        threading.Thread(target=_worker, daemon=True).start()

    def _on_clima_listo(self, data):
        self.clima_real = data
        self._actualiza_vista()

    def _actualiza_vista(self):
        tmeta = next((t for t in TEMAS if t['id'] == self.tema_sel), TEMAS[0])
        active_serie = tmeta['serie']
        dos_mon = (self.combo_mon.get_selected() == 1)
        usar_bloq = self.row_bloq.get_active()
        fp_tag = VARIANTES[self.combo_fp.get_selected()][0]
        fs_tag = VARIANTES[self.combo_fs.get_selected()][0]
        fb_tag = VARIANTES[self.combo_fb.get_selected()][0]
        ts_idx = self.combo_ts.get_selected()
        ts_id = 'igual' if ts_idx == 0 else TEMAS[ts_idx - 1]['id']
        modo_id = MODOS[self.combo_modo.get_selected()][0]
        hud_on = self.row_hud.get_active()
        solo_w = self.chk_solo_widgets.get_active()

        # Series y mundos activos
        for s_name, (card, badge) in self._series_cards.items():
            on = (s_name == active_serie)
            badge.set_visible(on)
            card.remove_css_class('pz-card-item-active' if not on else 'pz-card-item')
            card.add_css_class('pz-card-item-active' if on else 'pz-card-item')

        for tid, (card, badge, _ser) in self._world_cards.items():
            on = (tid == self.tema_sel)
            badge.set_visible(on)
            card.remove_css_class('pz-card-item-active' if not on else 'pz-card-item')
            card.add_css_class('pz-card-item-active' if on else 'pz-card-item')

        self.combo_fs.set_sensitive(dos_mon)
        self.combo_ts.set_sensitive(dos_mon)
        self.combo_fb.set_sensitive(usar_bloq)
        self.box_picker_m2.set_visible(dos_mon)
        self.row_hora.set_sensitive(modo_id == 'fija')
        self.row_fps.set_sensitive(self.row_animar.get_active())

        # Selector visual 3x3
        var_names = {
            'principal': _cortar_serie_prefijo(tmeta['m1']),
            'secundaria': _cortar_serie_prefijo(tmeta['m2']),
            'bloqueo': _cortar_serie_prefijo(tmeta['m3']),
        }
        self.btn_rep_p.set_label(f"✨ Todas: {var_names['principal'][:18]}")
        self.btn_rep_s.set_label(f"✨ Todas: {var_names['secundaria'][:18]}")
        self.btn_rep_b.set_label(f"✨ Todas: {var_names['bloqueo'][:18]}")
        prev_cache = {v: _resolver_preview(self.tema_sel, self.fase_sel, v) for v, _ in VARIANTES}
        sel_map = {'principal': fp_tag, 'secundaria': fs_tag, 'bloqueo': fb_tag}
        for pi in self._picker_items:
            p = prev_cache.get(pi['escena'])
            if p:
                pi['pic'].set_filename(p)
            pi['lbl'].set_text(var_names.get(pi['escena'], pi['escena']))
            es_sel = (sel_map[pi['rol']] == pi['escena']) and (pi['rol'] != 'bloqueo' or usar_bloq)
            pi['chk'].set_visible(es_sel)
            pi['card'].remove_css_class('pz-picker-card-active' if not es_sel else 'pz-picker-card')
            pi['card'].add_css_class('pz-picker-card-active' if es_sel else 'pz-picker-card')

        # Estudio en vivo (columna derecha)
        if prev_cache.get(fp_tag):
            self.pic_prev1.set_filename(prev_cache[fp_tag])
        self.lbl_prev1_title.set_text(f"PANTALLA 1 · {var_names.get(fp_tag, fp_tag)}")

        tid_sec = ts_id if (ts_id != 'igual' and ts_id != self.tema_sel) else self.tema_sel
        p2 = _resolver_preview(tid_sec, self.fase_sel, fs_tag)
        if p2:
            self.pic_prev2.set_filename(p2)
        tsec_meta = next((t for t in TEMAS if t['id'] == tid_sec), None) if tid_sec != self.tema_sel else None
        self.lbl_prev2_title.set_text(f"PANTALLA 2 · {tsec_meta['titulo']}" if tsec_meta else f"PANTALLA 2 · {var_names.get(fs_tag, fs_tag)}")
        self.box_prev2.set_visible(dos_mon)

        if prev_cache.get(fb_tag):
            self.pic_prev_bloq.set_filename(prev_cache[fb_tag])
        self.lbl_prev_bloq_title.set_text(f"🔒 BLOQUEO · {var_names.get(fb_tag, fb_tag)}")
        self.box_prev_bloq.set_visible(usar_bloq)

        # Mock HUD sobre Pantalla 1
        self.mock_hud_box.set_visible(hud_on)
        n_stats = sum(1 for k, sw in self._switches_hud.items() if sw.get_active())
        for k, sw in self._switches_hud.items():
            sw.set_sensitive(hud_on and not (k == 'hud-grimorio' and solo_w))
            self._mock_cards[k].set_visible(sw.get_active() and not (k == 'hud-grimorio' and solo_w))
        self._mock_cards['hud-tiempo'].set_text(f"21:34 · {'FONDO EXTERNO' if solo_w else tmeta['titulo']}")

        # Botones barra inferior y badge cabecera
        self.btn_toggle_hud.set_label('👁️ Ocultar HUD' if hud_on else '👁️ Mostrar HUD')
        if solo_w:
            self.btn_solo_bar.set_label('🧩 Solo Widgets ON')
            self.btn_aplicar.set_label('✦ APLICAR SOLO WIDGETS')
            self.lbl_motor_badge.set_text('● MODO SOLO WIDGETS')
            self.lbl_motor_badge.set_css_classes(['pz-badge-solo'])
        elif _extension_activa():
            self.btn_solo_bar.set_label('🧩 Solo Widgets')
            self.btn_aplicar.set_label('✦ APLICAR A MI ESCRITORIO')
            self.lbl_motor_badge.set_text('● EXTENSIÓN ACTIVA')
            self.lbl_motor_badge.set_css_classes(['pz-badge-ok'])
        else:
            self.btn_solo_bar.set_label('🧩 Solo Widgets')
            self.btn_aplicar.set_label('✦ APLICAR A MI ESCRITORIO')
            self.lbl_motor_badge.set_text('● EN ESPERA')
            self.lbl_motor_badge.set_css_classes(['pz-badge-warn'])

        # Resumen sidebar
        modo_txt = MODOS_CORTO.get(modo_id, 'Ciclo 90m')
        if modo_id == 'fija':
            hv = self.row_hora.get_value()
            modo_txt = f"Fija {int(hv):02d}:{int(round((hv % 1) * 60)):02d}"
        hud_txt = f'{n_stats} activas' if hud_on else 'Desactivado'
        self.lbl_resumen.set_text(
            f"Modo Solo Widgets\nFondo externo · HUD: {hud_txt}" if solo_w
            else f"{tmeta['titulo']}\n{'2 pant.' if dos_mon else '1 pant.'} · {modo_txt} · HUD: {hud_txt}"
        )

        # Sincronizar Hub 2x2
        total_pages = max(1, (len(TEMAS) + 2) // 3)
        self.hub_page_idx %= total_pages
        start = self.hub_page_idx * 3
        vis_names = []
        for si in range(3):
            tm_item = TEMAS[(start + si) % len(TEMAS)]
            self.hub_slot_ids[si] = tm_item['id']
            vis_names.append(tm_item['serie'])
            p = _resolver_preview(tm_item['id'], self.fase_sel, 'principal') or _resolver_preview(tm_item['id'], 'noche', 'principal')
            if p:
                self._hub_slots[si]['pic'].set_filename(p)
            self._hub_slots[si]['lbl'].set_text(tm_item['titulo'])
            fr = self._hub_slots[si]['frame']
            is_sel = (tm_item['id'] == self.tema_sel)
            fr.set_css_classes(['pz-slot-frame-active' if is_sel else 'pz-slot-frame'])
        self.btn_hub_temas_lista.set_label(f"Temas: {', '.join(vis_names)}  ({self.hub_page_idx + 1}/{total_pages})")

        if prev_cache.get(fp_tag):
            self.pic_hub_anim.set_filename(prev_cache[fp_tag])
        self.lbl_hub_anim_sub.set_text(f"{'2 Pantallas' if dos_mon else '1 Pantalla'} · {tmeta['titulo']}")
        p_est = _resolver_preview(self.tema_sel, 'noche', fb_tag if usar_bloq else fp_tag)
        if p_est:
            self.pic_hub_est.set_filename(p_est)
        f_nom = {'dia': 'Día', 'dorado': 'Dorado', 'noche': 'Noche'}.get(self.fase_sel, 'Noche')
        self.lbl_hub_est_sub.set_text(f"Fase: {f_nom} · {'Bloqueo ON' if usar_bloq else 'Solo Escritorio'}")

        self._tick_reloj()
        self.lbl_hub_clock_status.set_text('HUD OFF' if not hud_on else ('SOLO WIDGETS' if solo_w else f'HUD ON ({n_stats})'))

        cl_id = CLIMAS[self.combo_clima.get_selected()][0]
        cl_r = self.clima_real
        if cl_r and cl_r.get('ok'):
            self.lbl_hub_weather.set_markup(f'<span foreground="#FFFFFF" size="x-large" weight="bold">{round(float(cl_r["temp"]))}°C</span>')
            modo_lbl = cl_r.get('desc', 'DESPEJADO').upper() if cl_id in ('normal', 'auto') else cl_id.upper()
            self.lbl_hub_weather_sub.set_text(f"{str(cl_r.get('city', '')).upper()} · {modo_lbl}")
        else:
            self.lbl_hub_weather.set_markup('<span foreground="#FFFFFF" size="x-large" weight="bold">--°C</span>')
            self.lbl_hub_weather_sub.set_text(cl_id.upper())
        self.lbl_hub_cat_badge.set_text('COMPACTO' if self.row_compacto.get_active() else f'{n_stats} TARJETAS')

        self.lbl_hub_gen_val.set_markup(f'<span foreground="#54DED4" weight="bold">{GLib.markup_escape_text(modo_txt)}</span>')
        anim_txt = f"Activa {int(self.row_fps.get_value())} FPS" if self.row_animar.get_active() else 'Solo sol (60s)'
        self.lbl_hub_rend_val.set_markup(f'<span foreground="#72E6AE" weight="bold">{GLib.markup_escape_text(anim_txt)}</span>')

        mons = _detectar_monitores()
        cl_diag = f"{cl_r['city']} ({cl_r['temp']}°C, {cl_r['desc']})" if (cl_r and cl_r.get('ok')) else 'Sin datos en caché'
        ext_diag = 'Activa en GNOME Shell' if _extension_activa() else ('Instalada (desactivada)' if _extension_instalada() else 'No instalada')
        self.lbl_diag.set_text(
            f"ℹ️ Versión instalada: v{VERSION_ACTUAL}\n"
            f"✅ {len(mons) or 1} pantalla(s) detectadas.\n"
            f"✅ {len(TEMAS)} mundos × 3 pantallas listos.\n"
            f"🌦️ Clima local: {cl_diag}\n"
            f"🧩 Extensión GNOME: {ext_diag}"
        )

    def _guardar_en_settings(self):
        if not self.settings:
            return '90m', 1, 'principal', 'bloqueo', True, False
        s = self.settings
        n_mon = 2 if self.combo_mon.get_selected() == 1 else 1
        _set_safe(s, 'i', 'num-monitores', n_mon)
        _set_safe(s, 'b', 'todos-monitores', n_mon >= 2)

        fp = VARIANTES[self.combo_fp.get_selected()][0]
        fs = VARIANTES[self.combo_fs.get_selected()][0]
        fb = VARIANTES[self.combo_fb.get_selected()][0]
        ts_idx = self.combo_ts.get_selected()
        ts = 'igual' if ts_idx == 0 else TEMAS[ts_idx - 1]['id']
        usar_bloq = self.row_bloq.get_active()
        _set_safe(s, 's', 'fondo-principal', fp)
        _set_safe(s, 's', 'fondo-secundario', fs)
        _set_safe(s, 's', 'fondo-bloqueo', fb)
        _set_safe(s, 's', 'tema-secundario', ts)
        _set_safe(s, 'b', 'usar-bloqueo', usar_bloq)

        modo_id = MODOS[self.combo_modo.get_selected()][0]
        if modo_id == '90m':
            _set_safe(s, 'i', 'ciclo-duracion', 5400)
            _set_safe(s, 'b', 'ciclo-rapido', False)
            _set_safe(s, 'd', 'hora-simulada', -1.0)
            subprocess.run(['systemctl', '--user', 'enable', '--now', SVC_CICLO90], check=False)
        else:
            subprocess.run(['systemctl', '--user', 'disable', '--now', SVC_CICLO90], check=False)
            if modo_id == 'demo':
                _set_safe(s, 'i', 'ciclo-duracion', 90)
                _set_safe(s, 'd', 'hora-simulada', -1.0)
                _set_safe(s, 'b', 'ciclo-rapido', True)
            elif modo_id == 'fija':
                _set_safe(s, 'b', 'ciclo-rapido', False)
                _set_safe(s, 'd', 'hora-simulada', float(self.row_hora.get_value()))
            else:
                _set_safe(s, 'b', 'ciclo-rapido', False)
                _set_safe(s, 'd', 'hora-simulada', -1.0)

        _set_safe(s, 'b', 'animar', self.row_animar.get_active())
        _set_safe(s, 'i', 'fps', int(self.row_fps.get_value()))
        _set_safe(s, 's', 'clima', CLIMAS[self.combo_clima.get_selected()][0])
        _set_safe(s, 'i', 'rotacion-minutos', ROTACIONES[self.combo_rot.get_selected()][0])

        solo_w = self.chk_solo_widgets.get_active()
        _set_safe(s, 'b', 'solo-widgets', solo_w)
        _set_safe(s, 'b', 'hud', self.row_hud.get_active())
        _set_safe(s, 'b', 'hud-compacto', self.row_compacto.get_active())
        for clave, sw in self._switches_hud.items():
            _set_safe(s, 'b', clave, sw.get_active())

        _sincronizar_tema_en_ext(self.tema_sel)
        _set_safe(s, 's', 'tema', self.tema_sel)
        _set_safe(s, 'i', 'tema-revision', _get_int(s, 'tema-revision', 0) + 1)
        Gio.Settings.sync()
        return modo_id, n_mon, fp, fb, usar_bloq, solo_w

    def _on_guardar_solo(self):
        self._guardar_en_settings()
        self.lbl_status.set_text('💾 Opciones guardadas en GNOME GSettings.')

    def _on_aplicar(self):
        if not self.settings:
            return
        modo_id, n_mon, fp, fb, usar_bloq, solo_w = self._guardar_en_settings()
        fase = _detectar_fase(modo_id, self.row_hora.get_value())
        if not solo_w:
            _aplicar_fondos_gnome(self.tema_sel, fase, fp, fb, usar_bloq)
        self._actualiza_vista()
        tmeta = next((t for t in TEMAS if t['id'] == self.tema_sel), TEMAS[0])
        if solo_w:
            self.lbl_status.set_text('✨ ¡Listo! Modo Solo Widgets activo por encima de tu fondo de GNOME.')
        else:
            bloq_s = ' + bloqueo' if usar_bloq else ''
            self.lbl_status.set_text(f"✨ ¡Listo! '{tmeta['titulo']}' aplicado ({n_mon} pantalla(s){bloq_s}, modo {modo_id}).")

    def _on_visor_web(self, *_args):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        lively_dir = os.path.join(repo_root, 'windows', 'lively')
        docs_dir = os.path.join(repo_root, 'docs')
        serve_dir = lively_dir if os.path.isfile(os.path.join(lively_dir, 'index.html')) else (docs_dir if os.path.isfile(os.path.join(docs_dir, 'index.html')) else None)
        if not serve_dir:
            Gio.AppInfo.launch_default_for_uri(WEB_URL_FALLBACK, None)
            self.lbl_status.set_text('🎬 Abriendo visor web oficial en tu navegador.')
            return

        if self._web_server is None:
            handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=serve_dir)
            socketserver.TCPServer.allow_reuse_address = True
            srv = socketserver.TCPServer(('127.0.0.1', 0), handler)
            self._web_server = srv
            self._web_port = srv.server_address[1]
            threading.Thread(target=srv.serve_forever, daemon=True).start()

        modo_id = MODOS[self.combo_modo.get_selected()][0]
        hv = self.row_hora.get_value()
        hud_f = '1' if self.row_hud.get_active() else '0'
        url = f"http://127.0.0.1:{self._web_port}/?tema={self.tema_sel}&pantalla=principal&modo={modo_id}&hora={hv:.2f}&hud={hud_f}"
        Gio.AppInfo.launch_default_for_uri(url, None)
        self.lbl_status.set_text(f'🎬 Visor animado abierto en http://127.0.0.1:{self._web_port}')

    @staticmethod
    def _parse_ver(txt):
        nums = []
        for parte in str(txt).lstrip('vV').split('.'):
            try:
                nums.append(int(parte))
            except ValueError:
                nums.append(0)
        return tuple(nums)

    def _on_buscar_actualizacion(self, *_args):
        self.btn_update.set_sensitive(False)
        self.lbl_status.set_text('🔄 Buscando actualizaciones en GitHub Releases...')

        def _worker():
            try:
                req = urllib.request.Request(RELEASES_API, headers={'User-Agent': 'PixelZenWorlds'})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    rel = json.loads(resp.read().decode('utf-8'))
                tag = str(rel.get('tag_name', '')).lstrip('vV')
                if self._parse_ver(tag) <= self._parse_ver(VERSION_ACTUAL):
                    GLib.idle_add(self._fin_check_update, f'✅ Ya tienes la última versión (v{VERSION_ACTUAL}).', None, None)
                    return
                asset_url = next(
                    (a['browser_download_url'] for a in rel.get('assets', []) if a.get('name') == 'PixelZenWorlds-Linux-Setup.run'),
                    None,
                )
                GLib.idle_add(self._fin_check_update, f'✨ Nueva versión v{tag} disponible.', tag, asset_url or rel.get('html_url', RELEASES_URL))
            except Exception:
                GLib.idle_add(self._fin_check_update, '⚠️ No se pudo comprobar automáticamente. Abriendo Releases...', 'web', RELEASES_URL)

        threading.Thread(target=_worker, daemon=True).start()

    def _fin_check_update(self, msg, tag, url):
        self.btn_update.set_sensitive(True)
        self.lbl_status.set_text(msg)
        if not tag or not url:
            return
        if tag == 'web' or not url.endswith('.run'):
            Gio.AppInfo.launch_default_for_uri(url, None)
            return
        dlg = Adw.AlertDialog(
            heading=f'Actualización disponible (v{tag})',
            body=f'Tu versión actual es v{VERSION_ACTUAL}. ¿Quieres descargar e instalar PixelZen Worlds v{tag}? Tus ajustes de GNOME se conservarán.',
        )
        dlg.add_response('cancel', 'Más tarde')
        dlg.add_response('install', 'Descargar e instalar')
        dlg.set_response_appearance('install', Adw.ResponseAppearance.SUGGESTED)
        dlg.connect('response', lambda _d, r: self._ejecutar_update_linux(url) if r == 'install' else None)
        dlg.present(self)

    def _ejecutar_update_linux(self, url):
        self.lbl_status.set_text('⬇️ Descargando actualización...')

        def _dl():
            try:
                dst = '/tmp/PixelZenWorlds-Linux-Setup.run'
                req = urllib.request.Request(url, headers={'User-Agent': 'PixelZenWorlds'})
                with urllib.request.urlopen(req, timeout=60) as resp, open(dst, 'wb') as f:
                    shutil.copyfileobj(resp, f)
                os.chmod(dst, os.stat(dst).st_mode | stat.S_IXUSR)
                subprocess.Popen([dst], start_new_session=True)
                GLib.idle_add(self.get_application().quit)
            except Exception as exc:
                GLib.idle_add(self.lbl_status.set_text, f'❌ Error al actualizar: {exc}')

        threading.Thread(target=_dl, daemon=True).start()


class PixelZenApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='io.github.mosqui1988.PixelZenWorlds')

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = PixelZenWindow(self)
        win.present()


def main():
    app = PixelZenApp()
    return app.run(sys.argv)


if __name__ == '__main__':
    sys.exit(main())
