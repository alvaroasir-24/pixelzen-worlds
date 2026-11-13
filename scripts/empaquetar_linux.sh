#!/usr/bin/env bash
# Empaqueta PixelZen Worlds para Linux en un único instalador autoextraíble:
#   dist/PixelZenWorlds-Linux-Setup.run
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-$RAIZ/dist}"
mkdir -p "$OUT_DIR"

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
PKG="$STAGE/pixelzen-linux"
mkdir -p "$PKG/linux" "$PKG/src" "$PKG/fuentes" "$PKG/temas"

echo "==> Copiando archivos de runtime para Linux (sin carpetas de desarrollo)..."
cp -a "$RAIZ/linux/." "$PKG/linux/"
rm -f "$PKG/linux/LEEME.md"
cp "$RAIZ/src/ubicacion.py" "$PKG/src/"
cp "$RAIZ/src/datos.py" "$PKG/src/"
cp "$RAIZ/fuentes/DepartureMono-Regular.otf" "$PKG/fuentes/"
cp "$RAIZ/LICENSE" "$PKG/"
[ -f "$RAIZ/VERSION" ] && cp "$RAIZ/VERSION" "$PKG/"

if [ -d "$RAIZ/windows/lively/temas" ]; then
  cp -a "$RAIZ/windows/lively/temas/." "$PKG/temas/"
fi

for d in "$RAIZ/escenas"/*/pack; do
  [ -d "$d/images" ] || continue
  id="$(basename "$(dirname "$d")")"
  mkdir -p "$PKG/temas/$id"
  cp -a "$d/." "$PKG/temas/$id/"
  if [ -d "$RAIZ/escenas/$id/preview" ]; then
    rm -rf "$PKG/temas/$id/preview"
    cp -a "$RAIZ/escenas/$id/preview" "$PKG/temas/$id/preview"
  fi
  if [ -d "$RAIZ/escenas/$id/secundario/preview" ]; then
    mkdir -p "$PKG/temas/$id/secundario"
    rm -rf "$PKG/temas/$id/secundario/preview"
    cp -a "$RAIZ/escenas/$id/secundario/preview" "$PKG/temas/$id/secundario/preview"
  fi
done

TAR_PATH="$STAGE/payload.tar.gz"
tar -C "$PKG" -czf "$TAR_PATH" .

OUT_RUN="$OUT_DIR/PixelZenWorlds-Linux-Setup.run"
cat > "$OUT_RUN" <<'HEADER'
#!/usr/bin/env bash
set -euo pipefail

echo "✦ Instalador de PixelZen Worlds para Linux (GNOME 46+)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

ARCHIVE_LINE="$(awk '/^__ARCHIVE_BELOW__$/{print NR + 1; exit 0; }' "$0")"
tail -n+"$ARCHIVE_LINE" "$0" | tar -xz -C "$TMP_DIR"

chmod +x "$TMP_DIR/linux/instalar.sh" "$TMP_DIR/linux/desinstalar.sh" "$TMP_DIR/linux/hora.sh" "$TMP_DIR/linux/tema.sh"
"$TMP_DIR/linux/instalar.sh" --abrir-app "$@"
exit 0
__ARCHIVE_BELOW__
HEADER

cat "$TAR_PATH" >> "$OUT_RUN"
chmod +x "$OUT_RUN"
echo "✅ Instalador Linux generado: $OUT_RUN ($(du -h "$OUT_RUN" | cut -f1))"
