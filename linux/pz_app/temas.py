"""Catálogo de mundos, resolución de vistas previas y aplicación de fondos GNOME."""
import datetime
import json
import os
import shutil
import subprocess

from .constantes import EXT_DIR, REPO_ROOT


def cortar_serie_prefijo(txt):
    if not txt:
        return ''
    if ' · ' in txt:
        return txt.split(' · ', 1)[1].strip()
    return txt.strip()


def cargar_temas():
    """Carga los metadatos de los mundos desde tema.json sin mapas hardcodeados."""
    bases = [
        os.path.join(REPO_ROOT, 'docs', 'temas'),
        os.path.join(EXT_DIR, 'temas'),
        os.path.join(REPO_ROOT, 'windows', 'lively', 'temas'),
        os.path.join(REPO_ROOT, 'escenas'),
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
                if raw.get('titulo'):
                    titulo = str(raw['titulo'])
                m1 = str(raw.get('subtitulo') or raw.get('descripcion') or m1)
            except Exception:
                pass
            serie = str(raw.get('serie') or anime or 'PixelZen')

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


TEMAS = cargar_temas()
SERIES_ORDEN = []
SERIES_MAP = {}
for _t in TEMAS:
    if _t['serie'] not in SERIES_MAP:
        SERIES_MAP[_t['serie']] = []
        SERIES_ORDEN.append(_t['serie'])
    SERIES_MAP[_t['serie']].append(_t)


def resolver_preview(tema_id, fase, variante='principal'):
    sub = 'secundario' if variante == 'secundaria' else ('bloqueo' if variante == 'bloqueo' else '')
    pref = 'm2-' if variante == 'secundaria' else ('m3-' if variante == 'bloqueo' else '')
    candidatos = [
        os.path.join(EXT_DIR, 'temas', tema_id, sub, 'preview', fase, 'v3.png'),
        os.path.join(REPO_ROOT, 'escenas', tema_id, sub, 'preview', fase, 'v3.png'),
        os.path.join(REPO_ROOT, 'docs', 'previews', tema_id, f'{pref}{fase}.png'),
        os.path.join(REPO_ROOT, 'docs', 'temas', tema_id, sub, 'images', f'escena-{fase}.png'),
        os.path.join(EXT_DIR, 'temas', tema_id, sub, 'images', f'escena-{fase}.png'),
        os.path.join(EXT_DIR, 'temas', tema_id, sub, 'fondo.png'),
        os.path.join(REPO_ROOT, 'docs', 'temas', tema_id, sub, 'fondo.png'),
        os.path.join(EXT_DIR, 'temas', tema_id, 'fondo.png'),
    ]
    for ruta in candidatos:
        if ruta and os.path.isfile(ruta):
            return ruta
    return None


def detectar_fase(modo, hora_fija):
    if modo == 'fija':
        h = float(hora_fija)
    else:
        now = datetime.datetime.now()
        h = now.hour + now.minute / 60.0
    if 8.0 <= h < 17.5:
        return 'dia'
    if (6.0 <= h < 8.0) or (17.5 <= h < 20.0):
        return 'dorado'
    return 'noche'


def sincronizar_tema_en_ext(tema_id):
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


def aplicar_fondos_gnome(tema_id, fase, fp, fb, usar_bloqueo):
    bg_dir = os.path.expanduser('~/.local/share/backgrounds')
    os.makedirs(bg_dir, exist_ok=True)
    src_p = resolver_preview(tema_id, fase, fp)
    if src_p and os.path.isfile(src_p):
        dst_p = os.path.join(bg_dir, 'pixelzen.png')
        shutil.copy2(src_p, dst_p)
        uri_p = f'file://{dst_p}'
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri', uri_p], check=False)
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-uri-dark', uri_p], check=False)
        subprocess.run(['gsettings', 'set', 'org.gnome.desktop.background', 'picture-options', 'zoom'], check=False)
    if usar_bloqueo:
        src_b = resolver_preview(tema_id, fase, fb) or src_p
        if src_b and os.path.isfile(src_b):
            dst_b = os.path.join(bg_dir, 'pixelzen-lock.png')
            shutil.copy2(src_b, dst_b)
            uri_b = f'file://{dst_b}'
            subprocess.run(['gsettings', 'set', 'org.gnome.desktop.screensaver', 'picture-uri', uri_b], check=False)
