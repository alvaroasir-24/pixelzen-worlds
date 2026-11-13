#!/usr/bin/env bash
# Descarga e instalación automática de PixelZen Worlds para Linux (GNOME Shell 46-50+).
# Uso:
#   bash -c "$(curl -fsSL https://raw.githubusercontent.com/davidlpizano/pixelzen-worlds/main/scripts/instalar.sh)"
# Opciones por entorno o argumentos:
#   PIXELZEN_DIR=~/pixelzen-worlds PIXELZEN_TEMA=spiderman-miles-morales
#   --tema=<id>   --dir=<ruta>   --real (sin ciclo 90m)
set -euo pipefail

REPO="davidlpizano/pixelzen-worlds"
DEST="${PIXELZEN_DIR:-$HOME/pixelzen-worlds}"
TEMA="${PIXELZEN_TEMA:-spiderman-miles-morales}"
MODO_90M=1

for arg in "$@"; do
  case "$arg" in
    --tema=*) TEMA="${arg#--tema=}" ;;
    --dir=*) DEST="${arg#--dir=}" ;;
    --real) MODO_90M=0 ;;
    --90m) MODO_90M=1 ;;
    -h|--help)
      sed -n '2,7p' "$0"
      exit 0
      ;;
    *)
      echo "Opción desconocida: $arg" >&2
      exit 2
      ;;
  esac
done

for cmd in git python3; do
  command -v "$cmd" >/dev/null || {
    echo "Falta '$cmd'. Instálalo antes de continuar." >&2
    exit 1
  }
done

if [ -d "$DEST/.git" ]; then
  echo "==> Actualizando repositorio en $DEST"
  git -C "$DEST" pull -4 --ff-only 2>/dev/null || git -C "$DEST" pull --ff-only
elif command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  echo "==> Clonando $REPO con GitHub CLI en $DEST"
  gh repo clone "$REPO" "$DEST"
else
  echo "==> Clonando $REPO en $DEST"
  git clone -4 "git@github.com:${REPO}.git" "$DEST" 2>/dev/null \
    || git clone -4 "https://github.com/${REPO}.git" "$DEST" 2>/dev/null \
    || git clone "https://github.com/${REPO}.git" "$DEST"
fi

echo "==> Instalando extensión GNOME (tema='$TEMA')"
cd "$DEST/linux"
if [ "$MODO_90M" = 1 ]; then
  ./instalar.sh --tema="$TEMA" --90m
else
  ./instalar.sh --tema="$TEMA"
fi

echo
echo "Listo. Puedes cambiar de mundo o ciclo desde:"
echo "  gnome-extensions prefs pixelzen@mosqui1988.github.io"
