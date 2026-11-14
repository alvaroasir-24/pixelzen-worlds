@echo off
title PixelZen Worlds - Instalador Windows
color 0B
echo.
echo   ============================================================
echo     PIXELZEN WORLDS - Instalador nativo para Windows 10/11
echo     9 Mundos x 3 Escenas (27 paisajes) + 9 Tarjetas HUD
echo   ============================================================
echo.
set "PS_SCRIPT=%~dp0Instalar-PixelZenWorlds.ps1"
if exist "%PS_SCRIPT%" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%"
) else (
    echo Descargando instalador oficial desde GitHub...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm 'https://raw.githubusercontent.com/davidlpizano/pixelzen-worlds/main/scripts/instalar.ps1' | iex"
)
if errorlevel 1 (
    echo.
    echo [!] Se produjo un error durante la instalacion.
    pause
)
