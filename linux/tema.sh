#!/usr/bin/env bash
# PixelZen para GNOME - cambia el tema/paisaje activo.
# Uso: ./tema.sh [fittoa | continente-demoniaco | --listar]
set -euo pipefail
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(dirname "$AQUI")"
UUID="pixelzen@mosqui1988.github.io"
EXT="$HOME/.local/share/gnome-shell/extensions/$UUID"
S="$EXT/schemas"

if [ "${1:-}" = "--listar" ] || [ -z "${1:-}" ]; then
  echo "Temas disponibles:"
  for d in "$RAIZ/escenas"/*/; do
    id="$(basename "$d")"
    [ "${id#_}" != "$id" ] && continue
    [ -f "$d/generar.py" ] && echo "  - $id"
  done
  exit 0
fi

TEMA="$1"
TEMA_DIR="$RAIZ/escenas/$TEMA"
PACK="$TEMA_DIR/pack"
if [ ! -f "$TEMA_DIR/generar.py" ]; then
  echo "Tema desconocido: $TEMA (usa --listar para ver los disponibles)" >&2
  exit 2
fi

if [ ! -d "$PACK/images" ]; then
  echo "==> Compilando tema '$TEMA'..."
  python3 "$RAIZ/src/construir.py" "$TEMA"
fi

echo "==> Aplicando tema '$TEMA' a $EXT"
rm -rf "$EXT/images"
cp -a "$PACK/images" "$EXT/images"
cp "$PACK/datos.json" "$EXT/datos.json"
cp "$PACK/tema.json" "$EXT/tema.json"
cp "$PACK/fondo.png" "$EXT/fondo.png"
mkdir -p "$HOME/.local/share/backgrounds"
cp "$PACK/fondo.png" "$HOME/.local/share/backgrounds/pixelzen.png"

rev="$(gsettings --schemadir "$S" get org.gnome.shell.extensions.pixelzen tema-revision 2>/dev/null || echo 0)"
rev="$((rev + 1))"
gsettings --schemadir "$S" set org.gnome.shell.extensions.pixelzen tema "$TEMA"
gsettings --schemadir "$S" set org.gnome.shell.extensions.pixelzen tema-revision "$rev"

echo "Tema activo cambiado a '$TEMA'."
