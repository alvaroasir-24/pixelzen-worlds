#!/usr/bin/env python3
"""Verificación automática de integridad, sintaxis, paridad y renderizado de PixelZen Worlds."""
import datetime
import filecmp
import json
import os
import py_compile
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMAS = [
    'fittoa',
    'continente-demoniaco',
    'hunter-x-hunter',
    'black-clover',
    'spiderman-miles-morales',
]
IMAGENES_REQUERIDAS = (
    'cielo-dia.png', 'cielo-dorado.png', 'cielo-noche.png',
    'escena-dia.png', 'escena-dorado.png', 'escena-noche.png',
    'nubes-dia.png', 'nubes-dorado.png', 'nubes-noche.png',
    'sol.png', 'luna.png',
)


def check_python():
    py_files = []
    for base in ('src', 'windows', 'linux', 'escenas', 'tests'):
        ruta_base = os.path.join(ROOT, base)
        for dirpath, _, filenames in os.walk(ruta_base):
            if '__pycache__' in dirpath or '/pack' in dirpath:
                continue
            for fn in filenames:
                if fn.endswith('.py'):
                    py_files.append(os.path.join(dirpath, fn))
    for path in sorted(py_files):
        py_compile.compile(path, doraise=True)
    print(f'[OK] py_compile ({len(py_files)} archivos Python)')


def check_shell():
    sh_files = [
        os.path.join(ROOT, 'linux', fn)
        for fn in sorted(os.listdir(os.path.join(ROOT, 'linux')))
        if fn.endswith('.sh')
    ]
    for path in sh_files:
        subprocess.run(['bash', '-n', path], check=True)
    print(f'[OK] bash -n ({len(sh_files)} scripts shell)')


def check_js_sync():
    src_js = os.path.join(ROOT, 'src', 'pixelzen-canvas.js')
    win_js = os.path.join(ROOT, 'windows', 'lively', 'pixelzen-canvas.js')
    doc_js = os.path.join(ROOT, 'docs', 'pixelzen-canvas.js')
    for dst in (win_js, doc_js):
        assert os.path.isfile(dst), f'Falta {dst}'
        assert filecmp.cmp(src_js, dst, shallow=False), f'Desincronizado: {dst} != {src_js}'

    gjs = shutil.which('gjs')
    if gjs:
        ext_dir = os.path.join(ROOT, 'linux', 'pixelzen@mosqui1988.github.io')
        for fn in ('escena.js', 'hud.js', 'extension.js', 'prefs.js'):
            ruta = os.path.join(ext_dir, fn)
            assert os.path.isfile(ruta), f'Falta {ruta}'
            code_ext = (
                "const GLib = imports.gi.GLib; "
                f"const [, b] = GLib.file_get_contents({json.dumps(ruta)}); "
                "const s = new TextDecoder().decode(b)"
                ".replace(/^import\\b.*$/gm, '')"
                ".replace(/\\bexport\\s+default\\s+class\\b/g, 'class')"
                ".replace(/\\bexport\\s+(function|class)\\b/g, '$1'); "
                "new Function(s);"
            )
            subprocess.run([gjs, '-c', code_ext], check=True)
        # Validar que el JS compartido parsea correctamente en SpiderMonkey/GJS
        for js_path in (src_js, os.path.join(ROOT, 'windows', 'lively', 'escena-web.js'), os.path.join(ROOT, 'docs', 'app.js')):
            code = (
                "const window = { addEventListener() {}, location: { search: '' } }; "
                "const document = { getElementById: () => null, querySelectorAll: () => [], body: { style: {} } }; "
                "const navigator = {}; "
                "const GLib = imports.gi.GLib; "
                f"const [ok, bytes] = GLib.file_get_contents({json.dumps(js_path)}); "
                "new Function(new TextDecoder().decode(bytes));"
            )
            subprocess.run([gjs, '-c', code], check=True)
    print('[OK] Sincronización y parseo JS')


def check_temas_y_packs():
    campos_req = ('id', 'nombre', 'citas', 'modo_pajaros', 'modo_particulas')
    for tema in TEMAS:
        tjson = os.path.join(ROOT, 'escenas', tema, 'tema.json')
        with open(tjson, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for campo in campos_req:
            assert campo in data and data[campo], f'Falta "{campo}" en {tjson}'

        for base_rel in (os.path.join('windows', 'lively', 'temas', tema), os.path.join('docs', 'temas', tema)):
            bdir = os.path.join(ROOT, base_rel)
            for req in ('datos.json', 'tema.json', 'fondo.png'):
                assert os.path.isfile(os.path.join(bdir, req)), f'Falta {base_rel}/{req}'
            for img in IMAGENES_REQUERIDAS:
                assert os.path.isfile(os.path.join(bdir, 'images', img)), f'Falta {base_rel}/images/{img}'

        for fase in ('dia', 'dorado', 'noche'):
            p1 = os.path.join(ROOT, 'escenas', tema, 'preview', fase, 'v3.png')
            p2 = os.path.join(ROOT, 'docs', 'previews', tema, f'{fase}.png')
            assert os.path.isfile(p1), f'Falta {p1}'
            assert os.path.isfile(p2), f'Falta {p2}'
            assert filecmp.cmp(p1, p2, shallow=False), f'Preview desincronizada: {p2}'
    print(f'[OK] Esquema y paridad de {len(TEMAS)} temas')


def check_windows_renderer():
    sys.path.insert(0, os.path.join(ROOT, 'windows'))
    import pixelzen_win  # noqa: E402

    for hora in (13, 18, 23):
        dt = datetime.datetime(2026, 6, 21, hora, 30, 0)
        sol = pixelzen_win.elevacion_solar(dt)
        assert 'e' in sol and 'az' in sol

    try:
        from PIL import Image
    except ImportError:
        print('[SKIP] Pillow no disponible para render_frame_pillow')
        return

    with tempfile.TemporaryDirectory() as tmp:
        out_png = os.path.join(tmp, 'frame.png')
        tema_dir = os.path.join(ROOT, 'windows', 'lively', 'temas', 'spiderman-miles-morales')
        pixelzen_win.render_frame_pillow(tema_dir, datetime.datetime(2026, 6, 21, 18, 45, 0), out_png)
        with Image.open(out_png) as im:
            assert im.size == (1920, 1200), f'Tamaño inesperado: {im.size}'
    print('[OK] windows/pixelzen_win.py (cálculo solar + render Pillow con nubes)')


def main():
    check_python()
    check_shell()
    check_js_sync()
    check_temas_y_packs()
    check_windows_renderer()
    print('TODAS LAS VERIFICACIONES PASARON.')


if __name__ == '__main__':
    main()
