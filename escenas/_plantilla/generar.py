#!/usr/bin/env python3
"""Plantilla mínima para añadir un nuevo fondo pixel art a PixelZen."""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src'))
from pz_lib import (  # noqa: E402
    HOR, Lienzo, W, H, aplica_vineta, dibuja_luna_estandar, dibuja_sol_estandar,
    exporta_salida, exporta_sprites_si_aplica, render_cielo, render_estrellas,
    render_lago, render_nubes,
)

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
ANIM = '--anim' in sys.argv
FASE = os.environ.get('PZ_FASE', 'noche')
SKYM = os.environ.get('PZ_SKY', 'normal')
random.seed(1)

PALETAS = {
    'noche': {'sky': ['#050717', '#181c46', '#463878', '#b57288'], 'agua': '#070c22', 'ola': ('#8ac6cc', '#4e6fa0', '#2d3b70'), 'nube': '#6d6ea8', 'vig': 0.75},
    'dorado': {'sky': ['#121d4e', '#72569a', '#f0826c', '#ffecad'], 'agua': '#2b224c', 'ola': ('#f2c098', '#a0729a', '#4c3e76'), 'nube': '#e49c98', 'vig': 0.85},
    'dia': {'sky': ['#1a58b2', '#649ee6', '#b0d4f4', '#f6f2d4'], 'agua': '#1d5d8e', 'ola': ('#d2ebf8', '#7ab6dc', '#3878a8'), 'nube': '#ffffff', 'vig': 0.92},
}
PAL = PALETAS[FASE]

ESTRELLAS, VENTANAS, FAROLES, RUNAS, DESTELLOS, NUBES = [], [], [], [], [], []
lz = Lienzo()

render_cielo(lz, PAL['sky'], SKYM, FASE)
exporta_sprites_si_aplica(lz, lambda: dibuja_luna_estandar(lz, 104, 104, 46), lambda: dibuja_sol_estandar(lz, 104, 104, 24))
render_estrellas(lz, FASE, ANIM, ESTRELLAS)

if not ANIM:
    if FASE == 'noche':
        dibuja_luna_estandar(lz, 352, 84, 46)
    else:
        dibuja_sol_estandar(lz, 320, 120, 24)

render_nubes(lz, [(160, 70, 180, PAL['nube'], 3), (380, 110, 140, PAL['nube'], 2)], NUBES, ANIM)
render_lago(lz, PAL['agua'], PAL['ola'], DESTELLOS, ANIM)
aplica_vineta(lz, PAL['vig'])

out = ARGS[0] if ARGS else '.'
datos = dict(W=W, H=H, estrellas=ESTRELLAS, ventanas=VENTANAS, faroles=FAROLES, runas=RUNAS,
             chimenea=None, destellos=DESTELLOS, barca=[300, 318], luna=[352, 84, 46])
exporta_salida(lz, out, FASE, ANIM, NUBES, datos)
