#!/usr/bin/env bash
# PixelZen para GNOME - controla la hora del fondo animado.
# Uso: ./hora.sh [real | 90m | demo | HH:MM]
set -euo pipefail
S="$HOME/.local/share/gnome-shell/extensions/pixelzen@mosqui1988.github.io/schemas"
SVC="pixelzen-ciclo90.service"
g() { gsettings --schemadir "$S" set org.gnome.shell.extensions.pixelzen "$@"; }
parar_ciclo90() { systemctl --user disable --now "$SVC" >/dev/null 2>&1 || true; }

case "${1:-real}" in
  real)
    parar_ciclo90
    g hora-simulada -1
    g ciclo-rapido false
    ;;
  demo|ciclo)
    parar_ciclo90
    g ciclo-duracion 90
    g hora-simulada -1
    g ciclo-rapido true
    ;;
  90m|ciclo90|ciclo-90m)
    g ciclo-duracion 5400
    g ciclo-rapido false
    systemctl --user enable --now "$SVC"
    ;;
  *)
    h=${1%%:*}; m=${1##*:}; [ "$h" = "$1" ] && m=0
    [[ "$h" =~ ^[0-9]{1,2}$ && "$m" =~ ^[0-9]{1,2}$ ]] || {
      echo "uso: hora.sh HH:MM | real | demo | 90m" >&2
      exit 2
    }
    parar_ciclo90
    g ciclo-rapido false
    g hora-simulada "$(python3 -c "print(int('$h') + int('$m') / 60)")"
    ;;
esac
echo "fondo: hora=${1:-real}"
