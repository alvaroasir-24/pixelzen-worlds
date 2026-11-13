param(
    [string]$Tema = 'fittoa',
    [int]$Monitores = 2,
    [ValidateSet('real', '90m', 'demo', 'fija')]
    [string]$Modo = '90m',
    [double]$Hora = 21.5,
    [string]$FondoPrincipal = 'principal',
    [string]$FondoSecundario = 'secundaria'
)

$ErrorActionPreference = 'SilentlyContinue'
Add-Type -AssemblyName System.Drawing

$Aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
$Raiz = Split-Path -Parent $Aqui
$PidFile = Join-Path $env:TEMP 'pixelzen_win.pid'
if (Test-Path $PidFile) {
    $old = Get-Content $PidFile -ErrorAction SilentlyContinue
    if ($old -and $old -ne $PID) {
        Stop-Process -Id ([int]$old) -Force -ErrorAction SilentlyContinue
    }
}
Set-Content -Path $PidFile -Value $PID -Encoding ASCII

$TemasBase = Join-Path $Aqui 'lively\temas'
if (-not (Test-Path $TemasBase)) {
    $TemasBase = Join-Path $Aqui 'temas'
}
if (-not (Test-Path $TemasBase)) {
    $TemasBase = Join-Path $Raiz 'windows\lively\temas'
}
$TemaDir = Join-Path $TemasBase $Tema
if (-not (Test-Path (Join-Path $TemaDir 'images'))) {
    exit 1
}

$code = @'
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.IO;
using System.Runtime.InteropServices;

[StructLayout(LayoutKind.Sequential)]
public struct PzcRect { public int Left, Top, Right, Bottom; }

[ComImport, Guid("B92B56A9-8B55-4E14-9A89-0199BBB6F93B"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IPzcDesktopWallpaper {
    void SetWallpaper([MarshalAs(UnmanagedType.LPWStr)] string monitorID, [MarshalAs(UnmanagedType.LPWStr)] string wallpaper);
    [return: MarshalAs(UnmanagedType.LPWStr)]
    string GetWallpaper([MarshalAs(UnmanagedType.LPWStr)] string monitorID);
    [return: MarshalAs(UnmanagedType.LPWStr)]
    string GetMonitorDevicePathAt(uint monitorIndex);
    uint GetMonitorDevicePathCount();
    PzcRect GetMonitorRECT([MarshalAs(UnmanagedType.LPWStr)] string monitorID);
}

[ComImport, Guid("C2CF3110-460E-4fc1-B9D0-8A1C0C9CC4BD")]
public class PzcDesktopWallpaperClass {}

public static class PzcRenderer {
    [DllImport("user32.dll", CharSet=CharSet.Unicode)]
    public static extern int SystemParametersInfoW(int uAction, int uParam, string lpvParam, int fuWinIni);

    static double Suave(double t) {
        if (t < 0) t = 0; if (t > 1) t = 1;
        return t * t * (3.0 - 2.0 * t);
    }

    public static void Solar(DateTime dt, double lat, double lon, out double elev, out double az, out double H, out double H0) {
        double rad = Math.PI / 180.0;
        double ts = new DateTimeOffset(dt).ToUnixTimeMilliseconds() / 1000.0;
        double n = ts / 86400.0 + 2440587.5 - 2451545.0;
        double L = (280.460 + 0.9856474 * n) % 360.0; if (L < 0) L += 360.0;
        double gdeg = (357.528 + 0.9856003 * n) % 360.0; if (gdeg < 0) gdeg += 360.0;
        double g = gdeg * rad;
        double lam = (L + 1.915 * Math.Sin(g) + 0.020 * Math.Sin(2 * g)) * rad;
        double eps = (23.439 - 0.0000004 * n) * rad;
        double ra = Math.Atan2(Math.Cos(eps) * Math.Sin(lam), Math.Cos(lam));
        double dec = Math.Asin(Math.Sin(eps) * Math.Sin(lam));
        double gmst = (18.697374558 + 24.06570982441908 * n) % 24.0;
        if (gmst < 0) gmst += 24.0;
        double Hh = (gmst * 15.0 + lon) * rad - ra;
        Hh = Math.Atan2(Math.Sin(Hh), Math.Cos(Hh));
        double phi = lat * rad;
        double e = Math.Asin(Math.Sin(phi) * Math.Sin(dec) + Math.Cos(phi) * Math.Cos(dec) * Math.Cos(Hh));
        double A = Math.Atan2(Math.Sin(Hh), Math.Cos(Hh) * Math.Sin(phi) - Math.Tan(dec) * Math.Cos(phi)) + Math.PI;
        double c0 = Math.Max(-1.0, Math.Min(1.0, -Math.Tan(phi) * Math.Tan(dec)));
        elev = e / rad;
        az = ((A / rad) % 360.0 + 360.0) % 360.0;
        H = Hh;
        H0 = Math.Acos(c0);
    }

    static void DrawAlpha(Graphics g, Image img, int x, int y, double opacity) {
        if (opacity <= 0.01 || img == null) return;
        if (opacity >= 0.99) {
            g.DrawImage(img, x, y, img.Width, img.Height);
            return;
        }
        using (var ia = new ImageAttributes()) {
            var cm = new ColorMatrix { Matrix33 = (float)opacity };
            ia.SetColorMatrix(cm, ColorMatrixFlag.Default, ColorAdjustType.Bitmap);
            g.DrawImage(img, new Rectangle(x, y, img.Width, img.Height), 0, 0, img.Width, img.Height, GraphicsUnit.Pixel, ia);
        }
    }

    static void DrawAlphaCrop(Graphics g, Image img, int dx, int dy, int sx, int sy, int sw, int sh, double opacity) {
        if (opacity <= 0.01 || img == null) return;
        using (var ia = new ImageAttributes()) {
            if (opacity < 0.99) {
                var cm = new ColorMatrix { Matrix33 = (float)opacity };
                ia.SetColorMatrix(cm, ColorMatrixFlag.Default, ColorAdjustType.Bitmap);
            }
            g.DrawImage(img, new Rectangle(dx, dy, sw, sh), sx, sy, sw, sh, GraphicsUnit.Pixel, ia);
        }
    }

    static Image LoadCached(string path) {
        if (!File.Exists(path)) return null;
        using (var fs = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite)) {
            return Image.FromStream(fs);
        }
    }

    public static void RenderFrame(string temaDir, DateTime dt, double elapsedSec, string outPath, int[][] nubes, bool conAstro) {
        string imgDir = Path.Combine(temaDir, "images");
        double e, az, H, H0;
        Solar(dt, 40.4, -3.7, out e, out az, out H, out H0);

        double wA = (e <= -14) ? 0.0 : ((e >= 0) ? 1.0 : Suave((e + 14.0) / 14.0));
        double wB = (e <= 0) ? 0.0 : ((e >= 16) ? 1.0 : Suave(e / 16.0));
        double solX = Math.Max(30, Math.Min(610, 320 + (az - 180) * 2.3));
        double solY = Math.Max(24, 272 - Math.Max(e, -9) * 3.6);
        double solOp = Math.Max(0.0, Math.Min(1.0, (e + 6.0) / 6.0));

        double f = -1.0;
        if (H >= H0) f = (H - H0) / (2 * Math.PI - 2 * H0);
        else if (H <= -H0) f = (H + 2 * Math.PI - H0) / (2 * Math.PI - 2 * H0);
        double lunaX = (f >= 0) ? (110 + f * 420) : 320;
        double lunaY = (f >= 0) ? (272 - 56 * Math.Sin(Math.PI * f) * 3.6) : 300;
        double lunaOp = (f >= 0) ? Math.Max(0.0, Math.Min(1.0, (-e - 1.0) / 5.0)) : 0.0;

        using (var canvas = new Bitmap(640, 400, PixelFormat.Format32bppArgb))
        using (var g = Graphics.FromImage(canvas)) {
            g.InterpolationMode = InterpolationMode.NearestNeighbor;
            g.PixelOffsetMode = PixelOffsetMode.Half;

            using (var cn = LoadCached(Path.Combine(imgDir, "cielo-noche.png")))
            using (var cg = LoadCached(Path.Combine(imgDir, "cielo-dorado.png")))
            using (var cd = LoadCached(Path.Combine(imgDir, "cielo-dia.png"))) {
                DrawAlpha(g, cn, 0, 0, 1.0);
                DrawAlpha(g, cg, 0, 0, wA);
                DrawAlpha(g, cd, 0, 0, wB);
            }

            if (conAstro && solOp > 0.01) {
                using (var sol = LoadCached(Path.Combine(imgDir, "sol.png"))) {
                    DrawAlpha(g, sol, (int)(solX - 104), (int)(solY - 104), solOp);
                }
            }
            if (conAstro && lunaOp > 0.01) {
                using (var luna = LoadCached(Path.Combine(imgDir, "luna.png"))) {
                    DrawAlpha(g, luna, (int)(lunaX - 104), (int)(lunaY - 104), lunaOp);
                }
            }

            if (nubes != null && nubes.Length > 0) {
                bool noche = e < 0;
                double[] opNub = new double[] { noche ? (1.0 - wA) : 0.0, noche ? wA : (1.0 - wB), wB };
                string[] fnNub = new string[] { "nubes-noche.png", "nubes-dorado.png", "nubes-dia.png" };
                Image[] hojas = new Image[3];
                try {
                    for (int i = 0; i < 3; i++) {
                        if (opNub[i] > 0.01) hojas[i] = LoadCached(Path.Combine(imgDir, fnNub[i]));
                    }
                    int idx = 0;
                    foreach (var nb in nubes) {
                        if (nb.Length < 5) continue;
                        double vel = 3.5 + (idx % 3) * 1.4;
                        int nx = ((int)Math.Round(nb[0] + elapsedSec * vel)) % (640 + nb[2]);
                        int drawX = nx - nb[2];
                        for (int i = 0; i < 3; i++) {
                            if (hojas[i] != null) {
                                DrawAlphaCrop(g, hojas[i], drawX, nb[1], 0, nb[4], nb[2], nb[3], opNub[i]);
                            }
                        }
                        idx++;
                    }
                } finally {
                    for (int i = 0; i < 3; i++) if (hojas[i] != null) hojas[i].Dispose();
                }
            }

            using (var en = LoadCached(Path.Combine(imgDir, "escena-noche.png")))
            using (var eg = LoadCached(Path.Combine(imgDir, "escena-dorado.png")))
            using (var ed = LoadCached(Path.Combine(imgDir, "escena-dia.png"))) {
                DrawAlpha(g, en, 0, 0, 1.0);
                DrawAlpha(g, eg, 0, 0, wA);
                DrawAlpha(g, ed, 0, 0, wB);
            }

            using (var scaled = new Bitmap(1920, 1200, PixelFormat.Format24bppRgb))
            using (var gs = Graphics.FromImage(scaled)) {
                gs.InterpolationMode = InterpolationMode.NearestNeighbor;
                gs.PixelOffsetMode = PixelOffsetMode.Half;
                gs.DrawImage(canvas, new Rectangle(0, 0, 1920, 1200), new Rectangle(0, 0, 640, 400), GraphicsUnit.Pixel);
                scaled.Save(outPath, ImageFormat.Png);
            }
        }
    }

    public static void ApplyWallpapers(string p1, string p2, bool soloUno) {
        var dw = (IPzcDesktopWallpaper)new PzcDesktopWallpaperClass();
        uint count = dw.GetMonitorDevicePathCount();
        int primIdx = 0;
        for (uint i = 0; i < count; i++) {
            string id = dw.GetMonitorDevicePathAt(i);
            PzcRect r = dw.GetMonitorRECT(id);
            if (r.Left == 0 && r.Top == 0) { primIdx = (int)i; break; }
        }
        for (uint i = 0; i < count; i++) {
            string id = dw.GetMonitorDevicePathAt(i);
            if ((int)i == primIdx || soloUno) dw.SetWallpaper(id, p1);
            else dw.SetWallpaper(id, p2);
        }
        if (count == 0) SystemParametersInfoW(20, 0, p1, 3);
    }
}
'@

Add-Type -TypeDefinition $code -ReferencedAssemblies 'System.Drawing'

function Leer-Nubes([string]$dir) {
    $dp = Join-Path $dir 'datos.json'
    if (-not (Test-Path $dp)) { return ,@() }
    try {
        $j = Get-Content $dp -Raw -Encoding UTF8 | ConvertFrom-Json
        if (-not $j.nubes) { return ,@() }
        $arr = @()
        foreach ($n in $j.nubes) {
            $arr += ,([int[]]@($n[0], $n[1], $n[2], $n[3], $n[4]))
        }
        return ,$arr
    } catch {
        return ,@()
    }
}

function Resolver-CicloVariante([string]$variante) {
    $sub = switch ($variante) {
        'secundaria' { 'secundario' }
        'bloqueo'    { 'bloqueo' }
        default      { '' }
    }
    $cand = if ($sub) { Join-Path $TemaDir $sub } else { $TemaDir }
    if (Test-Path (Join-Path $cand 'images')) {
        return @{ Dir = $cand; ConAstro = ($variante -ne 'secundaria') }
    }
    return @{ Dir = $TemaDir; ConAstro = $true }
}

$rPrim = Resolver-CicloVariante $FondoPrincipal
$PrimDir = $rPrim.Dir
$PrimAstro = $rPrim.ConAstro
$nubesPrim = Leer-Nubes $PrimDir

$rSec = Resolver-CicloVariante $FondoSecundario
$SecDir = $rSec.Dir
$SecAstro = $rSec.ConAstro
$TieneSec = ($Monitores -ge 2) -and (Test-Path (Join-Path $SecDir 'images'))
$nubesSec = if ($TieneSec) { Leer-Nubes $SecDir } else { ,@() }

$ahoraIni = Get-Date
$horaIni = $ahoraIni.Hour + ($ahoraIni.Minute / 60.0) + ($ahoraIni.Second / 3600.0)
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$intervaloMs = if ($Modo -eq 'demo') { 1000 } elseif ($Modo -eq '90m') { 3000 } else { 30000 }
$slot = 0

while ($true) {
    $elapsed = $sw.Elapsed.TotalSeconds
    $d = Get-Date
    if ($Modo -eq 'fija') {
        $hv = $Hora % 24.0
        $hh = [int][Math]::Floor($hv)
        $mm = [int][Math]::Floor(($hv - $hh) * 60)
        $d = [DateTime]::new($d.Year, $d.Month, $d.Day, $hh, $mm, 0)
    } elseif ($Modo -eq '90m') {
        $hv = ($horaIni + ($elapsed / 5400.0) * 24.0) % 24.0
        $hh = [int][Math]::Floor($hv)
        $rem = ($hv - $hh) * 60.0
        $mm = [int][Math]::Floor($rem)
        $ss = [int][Math]::Floor(($rem - $mm) * 60.0)
        $d = [DateTime]::new($d.Year, $d.Month, $d.Day, $hh, $mm, [Math]::Min(59, $ss))
    } elseif ($Modo -eq 'demo') {
        $hv = (($elapsed % 90.0) / 90.0) * 24.0
        $hh = [int][Math]::Floor($hv)
        $rem = ($hv - $hh) * 60.0
        $mm = [int][Math]::Floor($rem)
        $ss = [int][Math]::Floor(($rem - $mm) * 60.0)
        $d = [DateTime]::new($d.Year, $d.Month, $d.Day, $hh, $mm, [Math]::Min(59, $ss))
    }

    $suf = if (($slot % 2) -eq 0) { 'a' } else { 'b' }
    $slot++
    $TmpPrim = Join-Path $env:TEMP "pixelzen_${Tema}_m1_${suf}.png"
    $TmpSec = Join-Path $env:TEMP "pixelzen_${Tema}_m2_${suf}.png"

    [PzcRenderer]::RenderFrame($PrimDir, $d, $elapsed, $TmpPrim, $nubesPrim, $PrimAstro)
    if ($TieneSec) {
        [PzcRenderer]::RenderFrame($SecDir, $d, $elapsed, $TmpSec, $nubesSec, $SecAstro)
        [PzcRenderer]::ApplyWallpapers($TmpPrim, $TmpSec, $false)
    } else {
        [PzcRenderer]::ApplyWallpapers($TmpPrim, $TmpPrim, $true)
    }

    if ($Modo -eq 'fija') { break }
    Start-Sleep -Milliseconds $intervaloMs
}
