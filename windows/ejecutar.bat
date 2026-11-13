@echo off
chcp 65001 >nul
title PixelZen Mushoku - Windows
cd /d "%~dp0"

echo ==========================================
echo   PixelZen Mushoku - Selector Windows
echo ==========================================
echo   1. Fittoa (Ciclo 24h en 90 minutos)
echo   2. Continente Demoniaco (Ciclo 24h en 90 minutos)
echo   3. Hunter x Hunter (Ciclo 24h en 90 minutos)
echo   4. Black Clover (Ciclo 24h en 90 minutos)
echo   5. Spider-Man Miles Morales (Ciclo 24h en 90 minutos)
echo   6. Fittoa (Hora real)
echo   7. Continente Demoniaco (Hora real)
echo   8. Hunter x Hunter (Hora real)
echo   9. Black Clover (Hora real)
echo   10. Spider-Man Miles Morales (Hora real)
echo   11. Abrir vista previa animada en navegador
echo ==========================================
set /p op="Elige una opcion [1-11]: "

if "%op%"=="1" python pixelzen_win.py --tema fittoa --90m
if "%op%"=="2" python pixelzen_win.py --tema continente-demoniaco --90m
if "%op%"=="3" python pixelzen_win.py --tema hunter-x-hunter --90m
if "%op%"=="4" python pixelzen_win.py --tema black-clover --90m
if "%op%"=="5" python pixelzen_win.py --tema spiderman-miles-morales --90m
if "%op%"=="6" python pixelzen_win.py --tema fittoa --real
if "%op%"=="7" python pixelzen_win.py --tema continente-demoniaco --real
if "%op%"=="8" python pixelzen_win.py --tema hunter-x-hunter --real
if "%op%"=="9" python pixelzen_win.py --tema black-clover --real
if "%op%"=="10" python pixelzen_win.py --tema spiderman-miles-morales --real
if "%op%"=="11" start "" "%~dp0lively\index.html"
