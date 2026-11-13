#!/usr/bin/env python3
"""Construye uno o todos los temas de escenas/ en pack/ y actualiza windows/lively/temas/."""
import os
import shutil
import sys
import tempfile

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
ESCENAS_DIR = os.path.join(ROOT_DIR, 'escenas')
WIN_TEMAS_DIR = os.path.join(ROOT_DIR, 'windows', 'lively', 'temas')
DOCS_DIR = os.path.join(ROOT_DIR, 'docs')

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


def sincroniza_canvas_js():
    src_js = os.path.join(SRC_DIR, 'pixelzen-canvas.js')
    if not os.path.isfile(src_js):
        return
    for dst_dir in (os.path.join(ROOT_DIR, 'windows', 'lively'), DOCS_DIR):
        if os.path.isdir(dst_dir):
            shutil.copy2(src_js, os.path.join(dst_dir, 'pixelzen-canvas.js'))


def main():
    objetivos = sys.argv[1:] or listar_temas()
    os.makedirs(WIN_TEMAS_DIR, exist_ok=True)
    sincroniza_canvas_js()

    for nombre in objetivos:
        tema_dir = os.path.join(ESCENAS_DIR, nombre)
        if not os.path.isfile(os.path.join(tema_dir, 'generar.py')):
            print(f'Error: tema "{nombre}" no encontrado en {ESCENAS_DIR}', file=sys.stderr)
            sys.exit(2)
        pack_dir = os.path.join(tema_dir, 'pack')
        shutil.rmtree(pack_dir, ignore_errors=True)
        with tempfile.TemporaryDirectory() as tmp:
            capas.construir_tema(tema_dir, pack_dir, tmp, SRC_DIR)
            for sub_name in ('secundario', 'bloqueo'):
                sub_dir = os.path.join(tema_dir, sub_name)
                if os.path.isfile(os.path.join(sub_dir, 'generar.py')):
                    with tempfile.TemporaryDirectory() as tmp_sub:
                        capas.construir_tema(sub_dir, os.path.join(pack_dir, sub_name), tmp_sub, SRC_DIR)

        win_dst = os.path.join(WIN_TEMAS_DIR, nombre)
        shutil.rmtree(win_dst, ignore_errors=True)
        shutil.copytree(pack_dir, win_dst)
        print(f'  [{nombre}] sincronizado con windows/lively/temas/{nombre}', flush=True)

        if os.path.isdir(DOCS_DIR):
            doc_tema = os.path.join(DOCS_DIR, 'temas', nombre)
            shutil.rmtree(doc_tema, ignore_errors=True)
            shutil.copytree(pack_dir, doc_tema)
            doc_prev = os.path.join(DOCS_DIR, 'previews', nombre)
            os.makedirs(doc_prev, exist_ok=True)
            for fase in ('dia', 'dorado', 'noche'):
                shutil.copy(os.path.join(tema_dir, 'preview', fase, 'v3.png'), os.path.join(doc_prev, f'{fase}.png'))
                for sub_name, pref in (('secundario', 'm2'), ('bloqueo', 'm3')):
                    sub_prev = os.path.join(tema_dir, sub_name, 'preview', fase, 'v3.png')
                    if os.path.isfile(sub_prev):
                        shutil.copy(sub_prev, os.path.join(doc_prev, f'{pref}-{fase}.png'))
            print(f'  [{nombre}] sincronizado con docs/temas y docs/previews', flush=True)


if __name__ == '__main__':
    main()
