#!/usr/bin/env python3
"""Construye uno o todos los temas de escenas/ en pack/ y actualiza windows/lively/temas/."""
import concurrent.futures
import os
import shutil
import sys
import tempfile

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
ESCENAS_DIR = os.path.join(ROOT_DIR, 'escenas')
OUT_ROOT = os.path.abspath(os.environ.get('PZ_OUT_ROOT') or ROOT_DIR)
OUT_ESCENAS_DIR = os.path.join(OUT_ROOT, 'escenas')
WIN_TEMAS_DIR = os.path.join(OUT_ROOT, 'windows', 'lively', 'temas')
DOCS_DIR = os.path.join(OUT_ROOT, 'docs')

sys.path.insert(0, SRC_DIR)
import capas  # noqa: E402


def listar_temas():
    res = []
    for nombre in sorted(os.listdir(ESCENAS_DIR)):
        if nombre.startswith('_'):
            continue
        ruta = os.path.join(ESCENAS_DIR, nombre)
        if os.path.isdir(ruta) and os.path.isfile(os.path.join(ruta, 'generar.py')):
            res.append(nombre)
    return res


def _copia_arbol(src_dir, dst_dir):
    """Copia recursivamente archivos usando copyfile para evitar fallos de permisos en metadatos."""
    shutil.rmtree(dst_dir, ignore_errors=True)
    for raiz, _, archivos in os.walk(src_dir):
        rel = os.path.relpath(raiz, src_dir)
        dest_raiz = dst_dir if rel == '.' else os.path.join(dst_dir, rel)
        os.makedirs(dest_raiz, exist_ok=True)
        for archivo in archivos:
            shutil.copyfile(os.path.join(raiz, archivo), os.path.join(dest_raiz, archivo))


def _construye_con_tmp(ruta_escena, destino, preview_root=None):
    tmp = tempfile.mkdtemp(prefix='pz_tmp_')
    try:
        capas.construir_tema(ruta_escena, destino, tmp, SRC_DIR, preview_root=preview_root)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def sincroniza_canvas_js():
    src_js = os.path.join(SRC_DIR, 'pixelzen-canvas.js')
    if not os.path.isfile(src_js):
        return
    with open(src_js, 'rb') as f:
        src_bytes = f.read()
    for dst_dir in (os.path.join(OUT_ROOT, 'windows', 'lively'), DOCS_DIR):
        if os.path.isdir(dst_dir):
            dst_js = os.path.join(dst_dir, 'pixelzen-canvas.js')
            if os.path.isfile(dst_js):
                with open(dst_js, 'rb') as f:
                    if f.read() == src_bytes:
                        continue
            shutil.copyfile(src_js, dst_js)


def construye_tema(nombre):
    tema_dir = os.path.join(ESCENAS_DIR, nombre)
    out_tema_dir = os.path.join(OUT_ESCENAS_DIR, nombre)
    pack_dir = os.path.join(out_tema_dir, 'pack')
    prev_dir = os.path.join(out_tema_dir, 'preview')
    shutil.rmtree(pack_dir, ignore_errors=True)
    _construye_con_tmp(tema_dir, pack_dir, preview_root=prev_dir)

    sub_prevs = {}
    for sub_name in ('secundario', 'bloqueo'):
        sub_dir = os.path.join(tema_dir, sub_name)
        if os.path.isfile(os.path.join(sub_dir, 'generar.py')):
            sub_prev = os.path.join(out_tema_dir, sub_name, 'preview')
            _construye_con_tmp(sub_dir, os.path.join(pack_dir, sub_name), preview_root=sub_prev)
            sub_prevs[sub_name] = sub_prev

    win_dst = os.path.join(WIN_TEMAS_DIR, nombre)
    _copia_arbol(pack_dir, win_dst)
    print(f'  [{nombre}] sincronizado con windows/lively/temas/{nombre}', flush=True)

    doc_tema = os.path.join(DOCS_DIR, 'temas', nombre)
    _copia_arbol(pack_dir, doc_tema)
    doc_prev = os.path.join(DOCS_DIR, 'previews', nombre)
    os.makedirs(doc_prev, exist_ok=True)
    for fase in ('dia', 'dorado', 'noche'):
        shutil.copyfile(os.path.join(prev_dir, fase, 'v3.png'), os.path.join(doc_prev, f'{fase}.png'))
        for sub_name, pref in (('secundario', 'm2'), ('bloqueo', 'm3')):
            if sub_name in sub_prevs:
                sub_prev_png = os.path.join(sub_prevs[sub_name], fase, 'v3.png')
                if os.path.isfile(sub_prev_png):
                    shutil.copyfile(sub_prev_png, os.path.join(doc_prev, f'{pref}-{fase}.png'))
    print(f'  [{nombre}] sincronizado con docs/temas y docs/previews', flush=True)


def main():
    objetivos = sys.argv[1:] or listar_temas()
    for nombre in objetivos:
        if not os.path.isfile(os.path.join(ESCENAS_DIR, nombre, 'generar.py')):
            print(f'Error: tema "{nombre}" no encontrado en {ESCENAS_DIR}', file=sys.stderr)
            sys.exit(2)

    os.makedirs(WIN_TEMAS_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)
    sincroniza_canvas_js()

    if not objetivos:
        return
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(objetivos))) as pool:
        futs = [pool.submit(construye_tema, nombre) for nombre in objetivos]
        for fut in futs:
            fut.result()


if __name__ == '__main__':
    main()
