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
CASA=""; FONDO=1; CICLO90=0; ABRIR_APP=0

for a in "$@"; do case "$a" in
  --tema=*) TEMA="${a#--tema=}";;
  --casa=*) CASA="${a#--casa=}";;
  --sin-fondo) FONDO=0;;
  --90m) CICLO90=1;;
  --abrir-app) ABRIR_APP=1;;
  -h|--help) sed -n 2,7p "$0"; exit 0;;
  *) echo "opcion desconocida: $a" >&2; exit 2;;
esac; done

for c in gnome-shell python3 glib-compile-schemas gsettings fc-cache; do
  command -v "$c" >/dev/null || { echo "Falta '$c'. PixelZen para GNOME necesita GNOME Shell 46 o superior." >&2; exit 1; }
done
ver="$(gnome-shell --version | grep -oE '[0-9]+' | head -1)"
[ "${ver:-0}" -ge 46 ] || { echo "GNOME Shell $ver no soportado (minimo 46)." >&2; exit 1; }

if [ ! -d "$RAIZ/temas/$TEMA/images" ] && [ ! -d "$RAIZ/docs/temas/$TEMA/images" ] && [ ! -d "$RAIZ/windows/lively/temas/$TEMA/images" ] && [ ! -d "$RAIZ/escenas/$TEMA/pack/images" ]; then
  echo "==> Compilando tema '$TEMA'..."
  python3 "$RAIZ/src/construir.py" "$TEMA"
fi

echo "==> Copiando la extension a $EXT"
rm -rf "$EXT"; mkdir -p "$EXT/code" "$EXT/temas"
cp -a "$AQUI/$UUID/." "$EXT/"
cp "$RAIZ/src/ubicacion.py" "$EXT/code/"
cp "$RAIZ/src/datos.py" "$EXT/code/"
cp "$RAIZ/src/clima.py" "$EXT/code/"
cp "$RAIZ/src/worlds_meta.json" "$EXT/code/"
cp "$RAIZ/src/pixelzen-heroes.js" "$EXT/code/"
cp "$RAIZ/LICENSE" "$EXT/"

if [ -d "$RAIZ/temas" ]; then
  cp -a "$RAIZ/temas/." "$EXT/temas/"
elif [ -d "$RAIZ/docs/temas" ]; then
  cp -a "$RAIZ/docs/temas/." "$EXT/temas/"
elif [ -d "$RAIZ/windows/lively/temas" ]; then
  cp -a "$RAIZ/windows/lively/temas/." "$EXT/temas/"
fi

for d in "$RAIZ/escenas"/*/pack; do
  [ -d "$d/images" ] || continue
  id="$(basename "$(dirname "$d")")"
  mkdir -p "$EXT/temas/$id"
  cp -a "$d/." "$EXT/temas/$id/"
  if [ -d "$RAIZ/escenas/$id/preview" ]; then
    rm -rf "$EXT/temas/$id/preview"
    cp -a "$RAIZ/escenas/$id/preview" "$EXT/temas/$id/preview"
  fi
  if [ -d "$RAIZ/escenas/$id/secundario/preview" ]; then
    mkdir -p "$EXT/temas/$id/secundario"
    rm -rf "$EXT/temas/$id/secundario/preview"
    cp -a "$RAIZ/escenas/$id/secundario/preview" "$EXT/temas/$id/secundario/preview"
  fi
  if [ -d "$RAIZ/escenas/$id/bloqueo/preview" ]; then
    mkdir -p "$EXT/temas/$id/bloqueo"
    rm -rf "$EXT/temas/$id/bloqueo/preview"
    cp -a "$RAIZ/escenas/$id/bloqueo/preview" "$EXT/temas/$id/bloqueo/preview"
  fi
done

if [ -d "$EXT/temas/$TEMA/images" ]; then
  cp -a "$EXT/temas/$TEMA/images" "$EXT/images"
  for fn in datos.json tema.json fondo.png; do
    [ -f "$EXT/temas/$TEMA/$fn" ] && cp "$EXT/temas/$TEMA/$fn" "$EXT/$fn"
  done
elif [ -d "$RAIZ/escenas/$TEMA/pack" ]; then
  cp -a "$RAIZ/escenas/$TEMA/pack/." "$EXT/"
fi
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

echo "==> Instalando aplicación gráfica PixelZen Worlds en el menú de aplicaciones"
mkdir -p "$HOME/.local/share/pixelzen" "$HOME/.local/bin" \
         "$HOME/.local/share/applications" "$HOME/.local/share/icons/hicolor/256x256/apps"
cp "$AQUI/pixelzen_app.py" "$HOME/.local/share/pixelzen/pixelzen_app.py"
rm -rf "$HOME/.local/share/pixelzen/pz_app"
[ -d "$AQUI/pz_app" ] && cp -a "$AQUI/pz_app" "$HOME/.local/share/pixelzen/pz_app"
[ -f "$RAIZ/src/clima.py" ] && cp "$RAIZ/src/clima.py" "$HOME/.local/share/pixelzen/clima.py"
[ -f "$RAIZ/src/ubicacion.py" ] && cp "$RAIZ/src/ubicacion.py" "$HOME/.local/share/pixelzen/ubicacion.py"
cp "$AQUI/desinstalar.sh" "$HOME/.local/share/pixelzen/desinstalar.sh"
[ -f "$RAIZ/VERSION" ] && cp "$RAIZ/VERSION" "$HOME/.local/share/pixelzen/VERSION"
chmod +x "$HOME/.local/share/pixelzen/pixelzen_app.py" "$HOME/.local/share/pixelzen/desinstalar.sh"
if [ -f "$AQUI/pixelzen-worlds.png" ]; then
  cp "$AQUI/pixelzen-worlds.png" "$HOME/.local/share/icons/hicolor/256x256/apps/pixelzen-worlds.png"
fi

cat > "$HOME/.local/bin/pixelzen-worlds" <<'EOF'
#!/usr/bin/env bash
exec python3 "$HOME/.local/share/pixelzen/pixelzen_app.py" "$@"
EOF
chmod +x "$HOME/.local/bin/pixelzen-worlds"

cat > "$HOME/.local/share/applications/pixelzen-worlds.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=PixelZen Worlds
Comment=Fondos pixel art animados, multimonitor y panel HUD
Exec=$HOME/.local/bin/pixelzen-worlds
Icon=pixelzen-worlds
Terminal=false
Categories=Utility;DesktopSettings;GTK;
StartupNotify=true
EOF
update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
gtk-update-icon-cache -f "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true

echo
echo "Listo (tema='$TEMA')."
echo "  Abrir app visual:  pixelzen-worlds  (o busca 'PixelZen Worlds' en tus aplicaciones)"
echo "  Desinstalar:       $HOME/.local/share/pixelzen/desinstalar.sh"

if [ "$ABRIR_APP" = 1 ] && { [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; }; then
  nohup "$HOME/.local/bin/pixelzen-worlds" >/dev/null 2>&1 &
fi
