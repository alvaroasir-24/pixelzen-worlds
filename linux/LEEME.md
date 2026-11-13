# PixelZen Worlds para Linux (GNOME Shell 46–50+)

Extensión de GNOME Shell + aplicación visual GTK4 (**PixelZen Worlds**) que dibuja el paisaje animado según el sol (o ciclo de 90 min), soporte multimonitor con continuación de historia y panel HUD.

## Descarga e instalación para usuarios finales (1 solo archivo)

Descarga **`PixelZenWorlds-Linux-Setup.run`** desde [GitHub Releases](https://github.com/davidlpizano/pixelzen-worlds/releases/latest) y ejecútalo:

```bash
chmod +x PixelZenWorlds-Linux-Setup.run
./PixelZenWorlds-Linux-Setup.run
```

Después abre **PixelZen Worlds** desde tu menú de aplicaciones de GNOME (o ejecutando `pixelzen-worlds`) para elegir mundo con vista previa, 1 o 2 monitores, modo de hora y cajitas HUD.

## Desde el repositorio de desarrollo

```bash
cd linux
./instalar.sh --90m                         # instala app visual + extensión con Fittoa y ciclo 90m
./tema.sh --listar
./tema.sh continente-demoniaco
./hora.sh 90m | real | demo | 21:30
~/.local/share/pixelzen/desinstalar.sh      # desinstala extensión, fuentes y app visual
```
