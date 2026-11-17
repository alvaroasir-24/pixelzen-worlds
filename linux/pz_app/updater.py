"""Comprobación y descarga segura (con verificación SHA-256) de actualizaciones en Linux."""
import hashlib
import json
import os
import shutil
import stat
import subprocess
import tempfile
import urllib.request

from .constantes import RELEASES_API, RELEASES_URL, UPDATE_CACHE_DIR, VERSION_ACTUAL


def parse_ver(txt):
    nums = []
    for parte in str(txt).lstrip('vV').split('.'):
        try:
            nums.append(int(parte))
        except ValueError:
            nums.append(0)
    return tuple(nums)


def parsear_sha256sums(texto, nombre_archivo):
    """Extrae el hash SHA-256 esperado para nombre_archivo desde un fichero SHA256SUMS.txt."""
    for linea in str(texto).splitlines():
        partes = linea.strip().split()
        if len(partes) >= 2 and partes[-1].lstrip('*') == nombre_archivo:
            cand = partes[0].lower()
            if len(cand) == 64 and all(c in '0123456789abcdef' for c in cand):
                return cand
    return None


def sha256_archivo(ruta):
    h = hashlib.sha256()
    with open(ruta, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def consultar_ultima_release():
    """Consulta GitHub Releases y devuelve (mensaje, tag, url_descarga, url_sha256)."""
    req = urllib.request.Request(RELEASES_API, headers={'User-Agent': 'PixelZenWorlds'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        rel = json.loads(resp.read().decode('utf-8'))
    tag = str(rel.get('tag_name', '')).lstrip('vV')
    if parse_ver(tag) <= parse_ver(VERSION_ACTUAL):
        return f'✅ Ya tienes la última versión (v{VERSION_ACTUAL}).', None, None, None
    assets = rel.get('assets', [])
    asset_url = next((a['browser_download_url'] for a in assets if a.get('name') == 'PixelZenWorlds-Linux-Setup.run'), None)
    sha_url = next((a['browser_download_url'] for a in assets if a.get('name') == 'SHA256SUMS.txt'), None)
    return (
        f'✨ Nueva versión v{tag} disponible.',
        tag,
        asset_url or rel.get('html_url', RELEASES_URL),
        sha_url,
    )


def descargar_y_lanzar_instalador(url, sha_url=None):
    """Descarga el instalador .run a un temporal privado, verifica SHA-256 si existe y lo ejecuta."""
    os.makedirs(UPDATE_CACHE_DIR, exist_ok=True)
    fd, dst = tempfile.mkstemp(prefix='PixelZenWorlds-Linux-Setup-', suffix='.run', dir=UPDATE_CACHE_DIR)
    os.close(fd)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'PixelZenWorlds'})
        with urllib.request.urlopen(req, timeout=60) as resp, open(dst, 'wb') as f:
            shutil.copyfileobj(resp, f)

        if sha_url:
            sreq = urllib.request.Request(sha_url, headers={'User-Agent': 'PixelZenWorlds'})
            with urllib.request.urlopen(sreq, timeout=15) as sresp:
                sums_txt = sresp.read().decode('utf-8', errors='replace')
            esperado = parsear_sha256sums(sums_txt, 'PixelZenWorlds-Linux-Setup.run')
            if esperado:
                obtenido = sha256_archivo(dst)
                if obtenido != esperado:
                    raise ValueError(f'Hash SHA-256 inválido ({obtenido[:12]} != {esperado[:12]})')

        os.chmod(dst, os.stat(dst).st_mode | stat.S_IXUSR)
        subprocess.Popen([dst], start_new_session=True)
        return dst
    except Exception:
        if os.path.isfile(dst):
            try:
                os.remove(dst)
            except OSError:
                pass
        raise
