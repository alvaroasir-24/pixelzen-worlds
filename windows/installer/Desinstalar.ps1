Add-Type -AssemblyName PresentationFramework

$res = [System.Windows.MessageBox]::Show(
    "¿Seguro que quieres desinstalar PixelZen Worlds?`nSe cerrarán las cajitas/ciclo activo y se quitarán los accesos directos.",
    "Desinstalar PixelZen Worlds",
    [System.Windows.MessageBoxButton]::YesNo,
    [System.Windows.MessageBoxImage]::Question
)
if ($res -ne [System.Windows.MessageBoxResult]::Yes) { exit 0 }

foreach ($pf in @('pixelzen_app.pid', 'pixelzen_hud.pid', 'pixelzen_win.pid', 'pixelzen_srv.pid')) {
    $p = Join-Path $env:TEMP $pf
    if (Test-Path $p) {
        $id = Get-Content $p -ErrorAction SilentlyContinue
        if ($id) { Stop-Process -Id ([int]$id) -Force -ErrorAction SilentlyContinue }
        Remove-Item $p -Force -ErrorAction SilentlyContinue
    }
}

Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'PixelZenWorlds' -ErrorAction SilentlyContinue
Remove-Item -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\PixelZenWorlds' -Recurse -Force -ErrorAction SilentlyContinue

$deskLnk = Join-Path ([Environment]::GetFolderPath('Desktop')) 'PixelZen Worlds.lnk'
$startLnk = Join-Path ([Environment]::GetFolderPath('Programs')) 'PixelZen Worlds.lnk'
Remove-Item $deskLnk, $startLnk -Force -ErrorAction SilentlyContinue

$root = Join-Path $env:LOCALAPPDATA 'PixelZenWorlds'
Start-Process -FilePath 'cmd.exe' -ArgumentList "/c ping 127.0.0.1 -n 3 >nul & rmdir /s /q `"$root`"" -WindowStyle Hidden
[System.Windows.MessageBox]::Show(
    "PixelZen Worlds ha sido desinstalado correctamente.",
    "PixelZen Worlds",
    [System.Windows.MessageBoxButton]::OK,
    [System.Windows.MessageBoxImage]::Information
) | Out-Null
