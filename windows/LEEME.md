# PixelZen Worlds para Windows 10/11

Tienes **dos formas** de usar estos fondos dinámicos en Windows, ambas usando los mismos temas de `escenas/` (`fittoa`, `continente-demoniaco`, `hunter-x-hunter`, `black-clover` y `spiderman-miles-morales`):

## Opción 1 (Recomendada · Animación completa + HUD): Lively Wallpaper

1. Instala **[Lively Wallpaper](https://www.rocksdanister.com/lively/)** (gratis y open-source, disponible en Microsoft Store o web oficial).
2. Arrastra o añade el archivo `windows\lively\index.html` dentro de Lively Wallpaper.
3. En Lively, haz clic derecho sobre el fondo -> **Personalizar**:
   - **Escena / Paisaje**: `fittoa`, `continente-demoniaco`, `hunter-x-hunter`, `black-clover` o `spiderman-miles-morales`.
   - **Modo de tiempo**: `Hora real`, `Ciclo 24h en 90 minutos`, `Demo rápida (90s)` o `Hora fija`.
   - **FPS** y **HUD** configurables.

> También puedes abrir `windows\lively\index.html` directamente en cualquier navegador (con `?tema=continente-demoniaco&modo=90m` si quieres) para probarlo al instante.

## Opción 2 (Sin apps externas): Script Python standalone

Requiere Python 3 (y opcionalmente `pip install pillow` para mezcla suave continua entre horas):

```bat
cd windows
ejecutar.bat
```

O por línea de comandos:

```bat
python pixelzen_win.py --tema fittoa --90m
python pixelzen_win.py --tema continente-demoniaco --90m
python pixelzen_win.py --tema continente-demoniaco --real
```
