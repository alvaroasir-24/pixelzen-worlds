# PixelZen Worlds para Windows 10/11

## Opción recomendada para usuarios: Instalador único (`PixelZenWorlds-Setup.exe`)

Descarga **`PixelZenWorlds-Setup.exe`** desde [GitHub Releases](https://github.com/davidlpizano/pixelzen-worlds/releases/latest) y ejecútalo. Instala todo silenciosamente en `%LOCALAPPDATA%\PixelZenWorlds` sin requerir Python y crea tu acceso directo **PixelZen Worlds** en el Escritorio y Menú Inicio.

*(Para compilar ese instalador desde este repositorio, ejecuta `powershell -ExecutionPolicy Bypass -File scripts\empaquetar_windows.ps1`.)*

---

## Opciones desde el repositorio de desarrollo

## Opción 1 (Recomendada · Animación completa + HUD): Lively Wallpaper

1. Instala **[Lively Wallpaper](https://www.rocksdanister.com/lively/)** (gratis y open-source, disponible en Microsoft Store o web oficial).
2. Arrastra o añade el archivo `windows\lively\index.html` dentro de Lively Wallpaper.
3. En Lively, haz clic derecho sobre el fondo -> **Personalizar**:
   - **Escena / Paisaje**: `fittoa`, `continente-demoniaco`, `hunter-x-hunter`, `black-clover` o `spiderman-miles-morales`.
   - **Modo de tiempo**: `Hora real`, `Ciclo 24h en 90 minutos`, `Demo rápida (90s)` o `Hora fija`.
   - **FPS** y **HUD** configurables.

> También puedes abrir `windows\lively\index.html` directamente en cualquier navegador (con `?tema=continente-demoniaco&modo=90m` si quieres) para probarlo al instante.

## Opción 2 (App completa de escritorio + HUD, sin apps externas)

Ejecuta con doble clic `windows\AbrirMenu.bat` (o `windows\PixelZenApp.vbs`) para abrir el panel visual donde podrás elegir mundo, 1 o 2 pantallas (con continuación de historia en el 2.º monitor), modo día/noche y qué tarjetitas mostrar en el escritorio.

También puedes lanzarlo por línea de comandos:

```bat
python pixelzen_win.py --tema fittoa --monitores 2 --90m
python pixelzen_win.py --tema continente-demoniaco --monitores 2 --90m
python pixelzen_win.py --tema continente-demoniaco --monitores 2 --real
```
