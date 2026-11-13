#!/usr/bin/env python3
"""PixelZen - extrae las capas del fondo animado (cielo, escena RGBA, nubes, sol, luna, datos.json y fondo.png) para cualquier tema."""
import json
import os
import pickle
import shutil
import struct
import subprocess
import sys
import zlib

W, H, HOR = 640, 400, 280


def png(ruta, filas, w, h, rgba):
    raw = bytearray()
    for f in filas:
        raw += b'\x00' + b''.join(bytes(p) for p in f)

    def ch(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)

    with open(ruta, 'wb') as out:
        out.write(
            b'\x89PNG\r\n\x1a\n'
            + ch(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6 if rgba else 2, 0, 0, 0))
            + ch(b'IDAT', zlib.compress(bytes(raw), 9))
            + ch(b'IEND', b'')
        )


def matte(neg, bla):
    """Recorte alfa exacto por diferencia entre fondo negro y blanco."""
    out = []
    for fn, fb in zip(neg, bla):
        fila = []
        for cn, cb in zip(fn, fb):
            a = 1 - sum(cb[i] - cn[i] for i in range(3)) / 765.0
            a = max(0.0, min(1.0, a))
            if a < 0.02:
                fila.append((0, 0, 0, 0))
            else:
                fila.append(tuple(min(255, int(cn[i] / a + 0.5)) for i in range(3)) + (int(a * 255 + 0.5),))
        out.append(fila)
    return out


def corre(gen_script, src_dir, env, *args):
    e = dict(os.environ, **env)
    prev_pp = e.get('PYTHONPATH', '')
    e['PYTHONPATH'] = src_dir + (os.pathsep + prev_pp if prev_pp else '')
    subprocess.run([sys.executable, gen_script, *args], env=e, check=True, stdout=subprocess.DEVNULL)


def construir_tema(tema_dir, destino_dir, tmp_dir, src_dir):
    """Genera imágenes animadas, datos.json, tema.json y fondo.png para un tema concreto."""
    gen_script = os.path.join(tema_dir, 'generar.py')
    tema_json = os.path.join(tema_dir, 'tema.json')
    if not os.path.isfile(gen_script):
        raise FileNotFoundError(f'Falta {gen_script}')

    img_dir = os.path.join(destino_dir, 'images')
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(tmp_dir, exist_ok=True)

    for fase in ('noche', 'dorado', 'dia'):
        print(f'  [{os.path.basename(tema_dir)}] fase {fase}', flush=True)
        corre(gen_script, src_dir, {'PZ_FASE': fase, 'PZ_SKYONLY': os.path.join(tmp_dir, f'cielo-{fase}.pkl')}, tmp_dir, '--anim')
        with open(os.path.join(tmp_dir, f'cielo-{fase}.pkl'), 'rb') as f:
            cielo = pickle.load(f)
        for y in range(HOR, H):
            cielo[y] = cielo[HOR - 1]
        png(os.path.join(img_dir, f'cielo-{fase}.png'), cielo, W, H, False)

        for modo in ('negro', 'blanco'):
            corre(
                gen_script,
                src_dir,
                {'PZ_FASE': fase, 'PZ_SKY': modo, 'PZ_DUMP': os.path.join(tmp_dir, f'{modo}-{fase}.pkl')},
                tmp_dir,
                '--anim',
            )
        with open(os.path.join(tmp_dir, f'negro-{fase}.pkl'), 'rb') as f:
            n = pickle.load(f)
        with open(os.path.join(tmp_dir, f'blanco-{fase}.pkl'), 'rb') as f:
            b = pickle.load(f)
        png(os.path.join(img_dir, f'escena-{fase}.png'), matte(n, b), W, H, True)
        shutil.move(os.path.join(tmp_dir, f'nubes-{fase}.png'), os.path.join(img_dir, f'nubes-{fase}.png'))

        if fase == 'noche':
            with open(os.path.join(tmp_dir, 'datos.js')) as f:
                js = f.read()
            datos = json.loads(js[js.index('{'):js.rindex('}') + 1])
            with open(os.path.join(destino_dir, 'datos.json'), 'w') as out:
                json.dump(datos, out)

    corre(gen_script, src_dir, {'PZ_SPRITES': os.path.join(tmp_dir, 'sprites.pkl')}, tmp_dir, '--anim')
    with open(os.path.join(tmp_dir, 'sprites.pkl'), 'rb') as f:
        sprites = pickle.load(f)
    for nombre, (neg, bla) in sprites.items():
        png(os.path.join(img_dir, f'{nombre}.png'), matte(neg, bla), 208, 208, True)

    # Vistas previas estáticas (dia, dorado, noche) y fondo.png
    preview_root = os.path.join(tema_dir, 'preview')
    for fase in ('dia', 'dorado', 'noche'):
        pdir = os.path.join(preview_root, fase)
        os.makedirs(pdir, exist_ok=True)
        corre(gen_script, src_dir, {'PZ_FASE': fase}, pdir)

    shutil.copy(os.path.join(preview_root, 'dia', 'v3.png'), os.path.join(destino_dir, 'fondo.png'))
    if os.path.isfile(tema_json):
        shutil.copy(tema_json, os.path.join(destino_dir, 'tema.json'))
    print(f'  [{os.path.basename(tema_dir)}] pack listo en {destino_dir}', flush=True)
