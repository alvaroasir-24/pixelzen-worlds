#!/usr/bin/env python3
"""Ciclo de 24 horas en 90 minutos (5400 s) para PixelZen GNOME."""
import datetime
import os
import signal
import sys
import time
from gi.repository import Gio

DURACION_S = 5400.0
INTERVALO_S = 10.0
SCHEMA_DIR = os.path.expanduser(
    '~/.local/share/gnome-shell/extensions/pixelzen@mosqui1988.github.io/schemas'
)
SCHEMA_ID = 'org.gnome.shell.extensions.pixelzen'


def get_settings():
    src = Gio.SettingsSchemaSource.new_from_directory(
        SCHEMA_DIR, Gio.SettingsSchemaSource.get_default(), False
    )
    schema = src.lookup(SCHEMA_ID, True)
    if schema is None:
        raise RuntimeError(f'No se encontró el esquema {SCHEMA_ID} en {SCHEMA_DIR}')
    return Gio.Settings.new_full(schema, None, None)


def main():
    duracion = float(sys.argv[1]) if len(sys.argv) > 1 else DURACION_S
    settings = get_settings()
    settings.set_boolean('ciclo-rapido', False)

    ahora = datetime.datetime.now()
    hora_inicio = ahora.hour + ahora.minute / 60.0 + ahora.second / 3600.0
    t0 = time.monotonic()

    parar = False

    def manejar_senal(_sig, _frame):
        nonlocal parar
        parar = True

    signal.signal(signal.SIGTERM, manejar_senal)
    signal.signal(signal.SIGINT, manejar_senal)

    while not parar:
        transcurrido = time.monotonic() - t0
        hora = (hora_inicio + (transcurrido / duracion) * 24.0) % 24.0
        settings.set_double('hora-simulada', round(hora, 4))

        fin = time.monotonic() + INTERVALO_S
        while not parar and time.monotonic() < fin:
            time.sleep(min(0.5, max(0.0, fin - time.monotonic())))


if __name__ == '__main__':
    main()
