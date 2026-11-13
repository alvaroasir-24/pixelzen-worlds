# PixelZen Worlds para Windows 10/11

## Opción recomendada para usuarios (sin `.exe` · compatible con Control inteligente de Windows 11)

En Windows PowerShell (sin Git ni Python ni archivos `.exe` sin firmar):

```powershell
irm https://raw.githubusercontent.com/davidlpizano/pixelzen-worlds/main/scripts/instalar.ps1 | iex
```

O descarga **`PixelZenWorlds-Windows.zip`** desde [GitHub Releases](https://github.com/davidlpizano/pixelzen-worlds/releases/latest), descomprímelo y abre `Instalar.bat`.

*(También se incluye `PixelZenWorlds-Setup.exe` en Releases, pero al no tener firma digital comercial Windows 11 con **Control inteligente de aplicaciones** lo bloquea.)*

Instala todo limpio en `%LOCALAPPDATA%\PixelZenWorlds\app` y crea el acceso directo **PixelZen Worlds** en el Escritorio y Menú Inicio.

*(Para empaquetar desde este repositorio, ejecuta `powershell -ExecutionPolicy Bypass -File scripts\empaquetar_windows.ps1`.)*

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
