#!/usr/bin/env bash
# PixelZen para GNOME (Ubuntu 24.04+): fondo animado que sigue al sol + panel de datos.
#   ./instalar.sh                                  instala con tema fittoa
#   ./instalar.sh --tema=continente-demoniaco      instala otro tema de escenas/
#   ./instalar.sh --casa=39.5,-0.4,"Mi ciudad"     fija tu ubicacion
#   ./instalar.sh --90m                            activa ciclo de 24 h en 90 min
#   ./instalar.sh --sin-fondo                      no cambia el fondo estatico de GNOME
set -euo pipefail

UUID="pixelzen@mosqui1988.github.io"
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(dirname "$AQUI")"
EXT="$HOME/.local/share/gnome-shell/extensions/$UUID"
CFG="$HOME/.config/pixelzen"
TEMA="fittoa"
CASA=""; FONDO=1; CICLO90=0

for a in "$@"; do case "$a" in
  --tema=*) TEMA="${a#--tema=}";;
  --casa=*) CASA="${a#--casa=}";;
  --sin-fondo) FONDO=0;;
  --90m) CICLO90=1;;
  -h|--help) sed -n 2,7p "$0"; exit 0;;
  *) echo "opcion desconocida: $a" >&2; exit 2;;
esac; done

for c in gnome-shell python3 glib-compile-schemas gsettings fc-cache; do
  command -v "$c" >/dev/null || { echo "Falta '$c'. PixelZen para GNOME necesita GNOME Shell 46 o superior." >&2; exit 1; }
done
ver="$(gnome-shell --version | grep -oE '[0-9]+' | head -1)"
[ "${ver:-0}" -ge 46 ] || { echo "GNOME Shell $ver no soportado (minimo 46)." >&2; exit 1; }

if [ ! -d "$RAIZ/escenas/$TEMA/pack/images" ]; then
  echo "==> Compilando tema '$TEMA'..."
  python3 "$RAIZ/src/construir.py" "$TEMA"
fi

echo "==> Copiando la extension a $EXT"
rm -rf "$EXT"; mkdir -p "$EXT/code"
cp -a "$AQUI/$UUID/." "$EXT/"
cp "$RAIZ/src/ubicacion.py" "$EXT/code/"
cp "$RAIZ/src/datos.py" "$EXT/code/"
cp "$RAIZ/LICENSE" "$EXT/"
cp -a "$RAIZ/escenas/$TEMA/pack/." "$EXT/"
if [ -d "$RAIZ/windows/lively/temas" ]; then
  rm -rf "$EXT/temas"
  cp -a "$RAIZ/windows/lively/temas" "$EXT/temas"
fi
for d in "$RAIZ/escenas"/*/pack; do
  [ -d "$d/images" ] || continue
  id="$(basename "$(dirname "$d")")"
  mkdir -p "$EXT/temas/$id"
  cp -a "$d/." "$EXT/temas/$id/"
done
glib-compile-schemas "$EXT/schemas"
gsettings --schemadir "$EXT/schemas" set org.gnome.shell.extensions.pixelzen tema "$TEMA"

echo "==> Instalando fuente Departure Mono para el panel HUD"
mkdir -p "$HOME/.local/share/fonts/pixelzen"
cp "$RAIZ/fuentes/DepartureMono-Regular.otf" "$HOME/.local/share/fonts/pixelzen/"
fc-cache -f "$HOME/.local/share/fonts/pixelzen" >/dev/null

echo "==> Instalando script de ciclo 90m"
mkdir -p "$HOME/.local/share/pixelzen" "$HOME/.config/systemd/user"
cp "$AQUI/ciclo90.py" "$HOME/.local/share/pixelzen/ciclo90.py"
chmod +x "$HOME/.local/share/pixelzen/ciclo90.py"
cat > "$HOME/.config/systemd/user/pixelzen-ciclo90.service" <<EOF
[Unit]
Description=PixelZen GNOME - ciclo completo de 24 horas en 90 minutos
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 %h/.local/share/pixelzen/ciclo90.py 5400
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF
systemctl --user daemon-reload >/dev/null 2>&1 || true

if [ -n "$CASA" ]; then
  IFS=',' read -r lat lon nombre <<<"$CASA"; tz="$(timedatectl show -p Timezone --value 2>/dev/null || echo '')"
  mkdir -p "$CFG"
  printf '{\n  "casa": {"nombre": "%s", "lat": %s, "lon": %s, "tz": "%s"}\n}\n' "${nombre:-casa}" "$lat" "$lon" "$tz" > "$CFG/ubicacion.json"
  echo "==> Ubicacion de casa guardada en $CFG/ubicacion.json"
fi

if [ "$FONDO" = 1 ]; then
  echo "==> Fondo estatico de GNOME (Actividades y pantalla de bloqueo)"
  mkdir -p "$CFG" "$HOME/.local/share/backgrounds"
  if [ ! -f "$CFG/gnome-fondo-anterior" ]; then
    { echo "picture-uri=$(gsettings get org.gnome.desktop.background picture-uri)"
      echo "picture-uri-dark=$(gsettings get org.gnome.desktop.background picture-uri-dark)"
      echo "picture-options=$(gsettings get org.gnome.desktop.background picture-options)"
      echo "screensaver-picture-uri=$(gsettings get org.gnome.desktop.screensaver picture-uri)"
    } > "$CFG/gnome-fondo-anterior"
  fi
  cp "$EXT/fondo.png" "$HOME/.local/share/backgrounds/pixelzen.png"
  uri="file://$HOME/.local/share/backgrounds/pixelzen.png"
  gsettings set org.gnome.desktop.background picture-uri "$uri"
  gsettings set org.gnome.desktop.background picture-uri-dark "$uri"
  gsettings set org.gnome.desktop.background picture-options zoom
  gsettings set org.gnome.desktop.screensaver picture-uri "$uri"
fi

echo "==> Activando la extension"
if ! gnome-extensions enable "$UUID" 2>/dev/null; then
  python3 -I - <<EOF
import ast, subprocess
cur = subprocess.run(['gsettings', 'get', 'org.gnome.shell', 'enabled-extensions'], capture_output=True, text=True).stdout.strip()
l = ast.literal_eval(cur.replace('@as ', '')) if cur else []
if '$UUID' not in l:
    l.append('$UUID')
    subprocess.run(['gsettings', 'set', 'org.gnome.shell', 'enabled-extensions', str(l)], check=True)
EOF
fi

if [ "$CICLO90" = 1 ]; then
  "$AQUI/hora.sh" 90m
fi

echo
echo "Listo (tema='$TEMA')."
echo "  Cambiar tema: $AQUI/tema.sh fittoa | continente-demoniaco"
echo "  Cambiar hora: $AQUI/hora.sh 90m | real | demo | 21:30"
