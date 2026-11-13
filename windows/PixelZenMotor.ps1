param(
    [string]$Tema = 'fittoa',
    [int]$Monitores = 2,
    [ValidateSet('real', '90m', 'demo', 'fija')]
    [string]$Modo = '90m',
    [double]$Hora = 21.5,
    [int]$Fps = 8,
    [string]$FondoPrincipal = 'principal',
    [string]$FondoSecundario = 'secundaria'
)

$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName System.Drawing, System.Windows.Forms

$Aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
$Raiz = Split-Path -Parent $Aqui
$LogFile = Join-Path $env:TEMP 'pixelzen_motor.log'

function Write-MotorLog([string]$msg) {
    try {
        $ts = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
        Add-Content -Path $LogFile -Value "[$ts] $msg" -Encoding UTF8 -ErrorAction SilentlyContinue
    } catch {}
}
Set-Content -Path $LogFile -Value "=== PixelZenMotor inicio (PID=$PID) ===" -Encoding UTF8 -ErrorAction SilentlyContinue

$PidFile = Join-Path $env:TEMP 'pixelzen_motor.pid'
if (Test-Path $PidFile) {
    $old = Get-Content $PidFile -ErrorAction SilentlyContinue
    if ($old -and $old -ne $PID) {
        Stop-Process -Id ([int]$old) -Force -ErrorAction SilentlyContinue
    }
}
Set-Content -Path $PidFile -Value $PID -Encoding ASCII

$TemasBase = Join-Path $Aqui 'lively\temas'
$EsInstalada = Test-Path $TemasBase
if (-not $EsInstalada) {
    $altTemas = Join-Path $Aqui 'temas'
    if (Test-Path $altTemas) {
        $TemasBase = $altTemas
        $EsInstalada = $true
    } else {
        $TemasBase = Join-Path $Raiz 'windows\lively\temas'
    }
}

$DataDir = if ($EsInstalada) { Join-Path $env:LOCALAPPDATA 'PixelZenWorlds' } else { $Aqui }
$ConfigPath = Join-Path $DataDir 'config.json'

$csCode = @'
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.IO;
using System.Runtime.InteropServices;
using System.Windows.Forms;

public class PzmStar {
    public int X, Y, Bright;
    public Color Col;
}

public class PzmCloud {
    public int X, Y, W, H, SheetY;
}

public class PzmLight {
    public int X, Y, R;
}

public class PzmSceneData {
    public string TemaDir;
    public bool ConAstro;
    public PzmStar[] Estrellas = new PzmStar[0];
    public PzmStar[] Brillantes = new PzmStar[0];
    public PzmCloud[] Nubes = new PzmCloud[0];
    public int[] Chimenea = null;
    public PzmLight[] Ventanas = new PzmLight[0];
    public PzmLight[] Faroles = new PzmLight[0];
    public PzmLight[] Runas = new PzmLight[0];
    public Point[] Destellos = new Point[0];

    public bool ModoWyvern;
    public bool ModoMiles;
    public bool ModoBrasas;
    public Color ColorPajaros = Color.FromArgb(40, 48, 72);
    public Color ColorHumoDia = Color.FromArgb(220, 224, 232);
    public Color ColorHumoNoche = Color.FromArgb(148, 160, 188);
    public Color ColorVentanas = Color.FromArgb(255, 198, 92);
    public Color ColorFarolesHalo = Color.FromArgb(255, 196, 98);
    public Color ColorFarolesCentro = Color.FromArgb(255, 244, 200);
    public Color ColorRunasHalo = Color.FromArgb(100, 210, 255);
    public Color ColorRunasCentro = Color.FromArgb(215, 250, 255);
    public Color[] ColorOlas = new Color[] { Color.FromArgb(160, 186, 225), Color.FromArgb(110, 140, 188) };
    public Color ColorReflejoSol = Color.FromArgb(255, 218, 128);
    public Color ColorReflejoLuna = Color.FromArgb(215, 230, 255);
    public Color ColorDestello = Color.FromArgb(255, 248, 220);
    public Color ColorManaHalo = Color.FromArgb(88, 215, 255);
    public Color ColorManaCentro = Color.FromArgb(215, 252, 255);
    public Color[] ColoresHojas = new Color[] { Color.FromArgb(114, 196, 140), Color.FromArgb(230, 180, 90), Color.FromArgb(214, 118, 86), Color.FromArgb(84, 222, 212) };
    public Color[] ColorFuegosHalo = new Color[] { Color.FromArgb(84, 222, 212), Color.FromArgb(230, 180, 90) };
    public Color[] ColorFuegosCentro = new Color[] { Color.FromArgb(215, 255, 248), Color.FromArgb(255, 240, 185) };

    public Bitmap CieloNoche, CieloDorado, CieloDia;
    public Bitmap EscenaNoche, EscenaDorado, EscenaDia;
    public Bitmap NubesNoche, NubesDorado, NubesDia;
    public Bitmap Sol, Luna;

    public static Color ParseHex(string hex, Color fallback) {
        if (string.IsNullOrEmpty(hex)) return fallback;
        try { return ColorTranslator.FromHtml(hex); } catch { return fallback; }
    }

    static Bitmap LoadPArgb(string path) {
        if (!File.Exists(path)) return null;
        using (var fs = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
        using (var raw = Image.FromStream(fs)) {
            var bmp = new Bitmap(raw.Width, raw.Height, PixelFormat.Format32bppPArgb);
            using (var g = Graphics.FromImage(bmp)) {
                g.CompositingMode = CompositingMode.SourceCopy;
                g.DrawImageUnscaled(raw, 0, 0);
            }
            return bmp;
        }
    }

    public void LoadImages() {
        DisposeImages();
        string imgDir = Path.Combine(TemaDir, "images");
        CieloNoche = LoadPArgb(Path.Combine(imgDir, "cielo-noche.png"));
        CieloDorado = LoadPArgb(Path.Combine(imgDir, "cielo-dorado.png"));
        CieloDia = LoadPArgb(Path.Combine(imgDir, "cielo-dia.png"));
        EscenaNoche = LoadPArgb(Path.Combine(imgDir, "escena-noche.png"));
        EscenaDorado = LoadPArgb(Path.Combine(imgDir, "escena-dorado.png"));
        EscenaDia = LoadPArgb(Path.Combine(imgDir, "escena-dia.png"));
        NubesNoche = LoadPArgb(Path.Combine(imgDir, "nubes-noche.png"));
        NubesDorado = LoadPArgb(Path.Combine(imgDir, "nubes-dorado.png"));
        NubesDia = LoadPArgb(Path.Combine(imgDir, "nubes-dia.png"));
        Sol = LoadPArgb(Path.Combine(imgDir, "sol.png"));
        Luna = LoadPArgb(Path.Combine(imgDir, "luna.png"));
    }

    public void DisposeImages() {
        Bitmap[] all = new Bitmap[] {
            CieloNoche, CieloDorado, CieloDia,
            EscenaNoche, EscenaDorado, EscenaDia,
            NubesNoche, NubesDorado, NubesDia,
            Sol, Luna
        };
        foreach (var b in all) if (b != null) b.Dispose();
        CieloNoche = CieloDorado = CieloDia = EscenaNoche = EscenaDorado = EscenaDia = null;
        NubesNoche = NubesDorado = NubesDia = Sol = Luna = null;
    }
}

public class PzmRenderer {
    static readonly int[][][] AlasGrulla = new int[][][] {
        new int[][] { new[]{-5,-2}, new[]{-4,-2}, new[]{-3,-1}, new[]{-2,-1}, new[]{-1,0}, new[]{0,0}, new[]{1,0}, new[]{2,-1}, new[]{3,-1}, new[]{4,-2}, new[]{5,-2} },
        new int[][] { new[]{-5,1}, new[]{-4,1}, new[]{-3,1}, new[]{-2,0}, new[]{-1,0}, new[]{0,0}, new[]{1,0}, new[]{2,0}, new[]{3,1}, new[]{4,1}, new[]{5,1} },
        new int[][] { new[]{-5,2}, new[]{-4,1}, new[]{-3,1}, new[]{-2,0}, new[]{-1,0}, new[]{0,1}, new[]{1,0}, new[]{2,0}, new[]{3,1}, new[]{4,1}, new[]{5,2} },
    };
    static readonly int[][][] AlasWyvern = new int[][][] {
        new int[][] { new[]{-7,-3}, new[]{-6,-3}, new[]{-5,-2}, new[]{-4,-2}, new[]{-3,-1}, new[]{-2,-1}, new[]{-1,0}, new[]{0,0}, new[]{1,0}, new[]{2,-1}, new[]{3,-1}, new[]{4,-2}, new[]{5,-2}, new[]{6,-3}, new[]{7,-3}, new[]{0,2} },
        new int[][] { new[]{-7,1}, new[]{-6,1}, new[]{-5,1}, new[]{-4,0}, new[]{-3,0}, new[]{-2,0}, new[]{-1,0}, new[]{0,0}, new[]{1,0}, new[]{2,0}, new[]{3,0}, new[]{4,0}, new[]{5,1}, new[]{6,1}, new[]{7,1}, new[]{0,2} },
        new int[][] { new[]{-7,3}, new[]{-6,2}, new[]{-5,2}, new[]{-4,1}, new[]{-3,1}, new[]{-2,0}, new[]{-1,0}, new[]{0,1}, new[]{1,0}, new[]{2,0}, new[]{3,1}, new[]{4,1}, new[]{5,2}, new[]{6,2}, new[]{7,3}, new[]{0,2} },
    };
    static readonly int[][] MotasMana = new int[][] {
        new[]{70,300}, new[]{95,330}, new[]{130,290}, new[]{565,310}, new[]{590,340},
        new[]{20,345}, new[]{470,296}, new[]{160,355}, new[]{248,318}, new[]{520,352},
    };
    static readonly string[][] MilesRows = new string[][] {
        new string[] {
            "......................WW..", ".....................WRR..", "....................RKK...",
            "...................KRR....", "..............KKKKKRK.....", ".............KRRRRKR......",
            "........KKKKKRRRRKK.......", "......KKKRRRRRKKRK........", ".....KKRRRRKRRRKK.........",
            "....KKRKKRRKKKKKKKK.......", "...KKK.KKRRKKKRRRRRKK.....", "..KK..KKRRK..KRRKK..KK....",
            "..K..KKKRR....KK.....K....", "....KKK.RK................", "...KK...K.................",
            "..KK......................", "..K.......................", ".........................."
        },
        new string[] {
            "..................WW......", ".................WRR......", "................RKK.......",
            "...............KKR........", "..........KKKKKKK.........", ".........KRRRRKKK.........",
            ".......KKKRRRRRKK.........", "......KKRRRRKKRRK.........", ".....KKRKKRRKKKKKKKK......",
            ".....KK.KKRRKKKRRRRKK.....", "....KK..KRRKK..KRRK.KK....", "....K...KKRR....KK...K....",
            ".......KK.RK..............", "......KK..KK..............", ".....KK...................",
            ".....K....................", "..........................", ".........................."
        },
        new string[] {
            "...............WW.........", "..............WRR.........", ".............KKR..........",
            ".......KKKKKKKR...........", "......KRRRRKKK............", ".....KKRRRRRKK............",
            "....KKRRRRKKRRK...........", "....KKRKKRRKKKKKKK........", "....KK.KKRRKKKRRRKK.......",
            "...KK..KRRKK..KRRK.KK.....", "...K...KKRR....KK...K.....", ".......KK.RK..............",
            "......KK..KK..............", ".....KK...................", ".....K....................",
            "..........................", "..........................", ".........................."
        },
        new string[] {
            "..........................", "..........KKKK............", ".........KRRRRK....WW.....",
            "........KKRRRRKK..WRR.....", ".......KKRRKRRRRKKRK......", "......KKKRRRRRKKRRK.......",
            ".....KKK.KKRRKKKK.........", "....KK..KKRRKKRRRKK.......", "...KK..KKRRK..KRRKKK......",
            "...K...KKRR....KK..KK.....", "......KK.RK.........K.....", ".....KK..KK...............",
            "....KK....................", "....K.....................", "..........................",
            "..........................", "..........................", ".........................."
        }
    };
    static readonly int[] MilesHc = new int[] { 22, 19, 16, 23 };
    static readonly int[] MilesHr = new int[] { 0, 0, 0, 3 };

    struct Ola { public int X, Y, W; public double Ph, Sp; public bool Light; }
    struct Hoja { public double X, Y, Vy, Vx, Ph; public int Tipo; }

    readonly Ola[] _olas = new Ola[44];
    readonly Hoja[] _hojas = new Hoja[42];
    readonly SolidBrush _brush = new SolidBrush(Color.White);
    readonly ImageAttributes _ia = new ImageAttributes();
    readonly ColorMatrix _cm = new ColorMatrix();
    public readonly Bitmap Frame = new Bitmap(640, 400, PixelFormat.Format32bppPArgb);

    public PzmRenderer() {
        long s = 7;
        for (int i = 0; i < _olas.Length; i++) {
            Func<double> r = () => { s = (s * 16807) % 2147483647; return (double)s / 2147483647.0; };
            _olas[i] = new Ola {
                X = 300 + (int)(r() * 260),
                Y = 286 + (int)(r() * 108),
                W = 3 + (int)(r() * 11),
                Ph = r() * 6.28,
                Sp = 0.03 + r() * 0.05,
                Light = r() < 0.35
            };
        }
        s = 21;
        for (int i = 0; i < _hojas.Length; i++) {
            Func<double> r = () => { s = (s * 16807) % 2147483647; return (double)s / 2147483647.0; };
            _hojas[i] = new Hoja {
                X = r() * 640,
                Y = r() * 400,
                Vy = 0.30 + r() * 0.42,
                Vx = 0.06 + r() * 0.12,
                Ph = r() * 6.28,
                Tipo = (int)(r() * 4)
            };
        }
    }

    static double Clamp01(double v) { return v < 0 ? 0 : (v > 1 ? 1 : v); }
    static double Suave(double t) { t = Clamp01(t); return t * t * (3.0 - 2.0 * t); }
    static double Osc(int t, double f, double p) { return 0.5 + 0.5 * Math.Sin(t * f + p); }

    void Px(Graphics g, Color c, double op, double ax, double ay, double aw = 1, double ah = 1) {
        op = Clamp01(op);
        if (op <= 0.004) return;
        int alpha = (int)Math.Round(op * c.A);
        if (alpha <= 1) return;
        _brush.Color = Color.FromArgb(alpha, c.R, c.G, c.B);
        g.FillRectangle(_brush, (int)Math.Round(ax), (int)Math.Round(ay), Math.Max(1, (int)Math.Round(aw)), Math.Max(1, (int)Math.Round(ah)));
    }

    void DrawAlpha(Graphics g, Bitmap bmp, int x, int y, double op) {
        if (bmp == null || op <= 0.01) return;
        if (op >= 0.99) {
            g.DrawImageUnscaled(bmp, x, y);
            return;
        }
        _cm.Matrix33 = (float)op;
        _ia.SetColorMatrix(_cm, ColorMatrixFlag.Default, ColorAdjustType.Bitmap);
        g.DrawImage(bmp, new Rectangle(x, y, bmp.Width, bmp.Height), 0, 0, bmp.Width, bmp.Height, GraphicsUnit.Pixel, _ia);
    }

    void DrawCrop(Graphics g, Bitmap bmp, int dx, int dy, int sx, int sy, int sw, int sh, double op) {
        if (bmp == null || op <= 0.01) return;
        if (op >= 0.99) {
            g.DrawImage(bmp, new Rectangle(dx, dy, sw, sh), sx, sy, sw, sh, GraphicsUnit.Pixel);
            return;
        }
        _cm.Matrix33 = (float)op;
        _ia.SetColorMatrix(_cm, ColorMatrixFlag.Default, ColorAdjustType.Bitmap);
        g.DrawImage(bmp, new Rectangle(dx, dy, sw, sh), sx, sy, sw, sh, GraphicsUnit.Pixel, _ia);
    }

    public static void Solar(DateTime dt, double lat, double lon, out double elev, out double az, out double H, out double H0) {
        double rad = Math.PI / 180.0;
        double ts = new DateTimeOffset(dt).ToUnixTimeMilliseconds() / 1000.0;
        double n = ts / 86400.0 + 2440587.5 - 2451545.0;
        double L = (280.460 + 0.9856474 * n) % 360.0; if (L < 0) L += 360.0;
        double gd = (357.528 + 0.9856003 * n) % 360.0; if (gd < 0) gd += 360.0;
        double g = gd * rad;
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

    void PintaFerry(Graphics g, int t, double nf) {
        int P = 1800, mitad = 900;
        int f = ((t % P) + P) % P;
        bool der = f < mitad;
        double u = der ? (double)f / mitad : (double)(f - mitad) / mitad;
        int fx = (int)Math.Round(der ? 180 + u * 320 : 500 - u * 320);
        int fy = 295 + (Math.Sin(t * 0.08) > 0.6 ? 1 : 0);
        int dir = der ? 1 : -1;
        Px(g, Color.FromArgb(20, 26, 46), 0.95, fx - 10, fy, 20, 2);
        Px(g, Color.FromArgb(230, 92, 40), 0.95, fx - 9, fy - 1, 18, 1);
        Px(g, Color.FromArgb(220, 230, 242), 0.95, fx - 7, fy - 3, 14, 2);
        Px(g, Color.FromArgb(240, 104, 44), 0.95, fx - 6, fy - 4, 12, 1);
        Px(g, Color.FromArgb(220, 230, 242), 0.95, fx - 3, fy - 6, 6, 2);
        Px(g, Color.FromArgb(30, 36, 56), 0.95, fx - dir, fy - 8, 2, 2);
        if (nf > 0.15) {
            for (int wx = -5; wx <= 5; wx += 2) Px(g, Color.FromArgb(255, 224, 136), 0.85 * nf, fx + wx, fy - 3, 1, 1);
            Px(g, Color.FromArgb(255, 54, 88), 0.9 * nf, fx - dir * 9, fy - 2, 1, 1);
            Px(g, Color.FromArgb(84, 255, 152), 0.9 * nf, fx + dir * 9, fy - 2, 1, 1);
        }
        for (int k = 1; k <= 7; k++) {
            if ((t / 2 + k) % 2 == 0) Px(g, Color.FromArgb(212, 236, 255), 0.45 * (1 - k / 8.0), fx - dir * (10 + k * 2), fy + 1, 2, 1);
        }
    }

    void PintaMiles(Graphics g, int t, double nf) {
        int P = 340, mitad = 170;
        int fase = ((t % P) + P) % P;
        bool der = fase < mitad;
        double u = der ? (double)fase / mitad : (double)(fase - mitad) / mitad;
        bool flip = !der;
        double x = der ? -24 + u * 688 : 664 - u * 688;
        double arcW = 688.0 / 3.0;
        int arcIdx = Math.Min(2, (int)Math.Floor(u * 3));
        double su = u * 3 - arcIdx;
        bool tieneRed = su >= 0.08 && su <= 0.86;
        int fIdx = !tieneRed ? 3 : (su < 0.34 ? 0 : (su < 0.64 ? 1 : 2));
        double y = (der ? 62 : 76) + 52 * Math.Sin(su * Math.PI);
        if (!tieneRed) {
            double j = su > 0.86 ? (su - 0.86) / 0.22 : (su + 0.14) / 0.22;
            y -= 7 * Math.Sin(Clamp01(j) * Math.PI);
        }
        int mx = (int)Math.Round(x), my = (int)Math.Round(y);
        string[] rows = MilesRows[fIdx];
        int hc = MilesHc[fIdx], hr = MilesHr[fIdx];

        if (tieneRed) {
            double arcStart = der ? -24 + arcIdx * arcW : 664 - arcIdx * arcW;
            int ax = (int)Math.Round(der ? arcStart + arcW * 0.62 : arcStart - arcW * 0.62);
            int hx = mx + (flip ? 13 - hc : hc - 13);
            int hy = my + hr - 10;
            int steps = Math.Max(1, Math.Max(Math.Abs(ax - hx), Math.Abs(hy)));
            Color wc = Color.FromArgb(220, 234, 255);
            for (int i = 0; i <= steps; i++) {
                int wx = (int)Math.Round(hx + (ax - hx) * (double)i / steps);
                int wy = (int)Math.Round(hy * (1.0 - (double)i / steps));
                Px(g, wc, ((i % 2 == 0) ? 0.88 : 0.68) * (1 - 0.12 * nf), wx, wy, 1, 1);
            }
        }
        Color cK = Color.FromArgb(21, 21, 33);
        Color cR = Color.FromArgb(235, 45, 60);
        Color cW = Color.FromArgb(228, 238, 255);
        for (int r = 0; r < rows.Length; r++) {
            string row = rows[r];
            for (int c = 0; c < row.Length; c++) {
                char ch = row[c];
                if (ch == '.') continue;
                Color col = ch == 'K' ? cK : (ch == 'R' ? cR : cW);
                Px(g, col, 1.0, mx + (flip ? 13 - c : c - 13), my + r - 10, 1, 1);
            }
        }
        int tailDir = der ? -1 : 1;
        for (int k = 0; k < 3; k++) {
            if ((t + k) % 3 != 0) continue;
            int sx = mx + tailDir * (10 + k * 4) + (int)Math.Round(Math.Sin(t * 0.6 + k * 2) * 2);
            int sy = my + 2 + (int)Math.Round(Math.Cos(t * 0.5 + k * 1.7) * 3);
            Px(g, k == 1 ? Color.FromArgb(255, 216, 64) : Color.FromArgb(0, 229, 255), 0.85, sx, sy, 1, 1);
        }
    }

    public void Render(PzmSceneData S, DateTime fecha, int t) {
        if (S == null || S.CieloNoche == null || S.EscenaNoche == null) return;
        double e, az, H, H0;
        Solar(fecha, 40.4, -3.7, out e, out az, out H, out H0);
        double wA = e <= -14 ? 0 : (e >= 0 ? 1 : Suave((e + 14) / 14));
        double wB = e <= 0 ? 0 : (e >= 16 ? 1 : Suave(e / 16));
        double nf = Clamp01((4 - e) / 10);
        double ef = Clamp01((-6 - e) / 8);
        double solX = Math.Max(30, Math.Min(610, 320 + (az - 180) * 2.3));
        double solY = Math.Max(24, 272 - Math.Max(e, -9) * 3.6);
        double solOp = Clamp01((e + 6) / 6);
        double f = -1;
        if (H >= H0) f = (H - H0) / (2 * Math.PI - 2 * H0);
        else if (H <= -H0) f = (H + 2 * Math.PI - H0) / (2 * Math.PI - 2 * H0);
        double lunaX = f >= 0 ? 110 + f * 420 : 320;
        double lunaY = f >= 0 ? 272 - 56 * Math.Sin(Math.PI * f) * 3.6 : 300;
        double lunaOp = f >= 0 ? Clamp01((-e - 1) / 5) : 0;
        double cuerpoX = e > -1 ? solX : lunaX;
        double cuerpoOp = e > -1 ? Clamp01((e + 2) / 6) : lunaOp;

        using (var g = Graphics.FromImage(Frame)) {
            g.InterpolationMode = InterpolationMode.NearestNeighbor;
            g.PixelOffsetMode = PixelOffsetMode.Half;

            g.CompositingMode = CompositingMode.SourceCopy;
            g.DrawImageUnscaled(S.CieloNoche, 0, 0);
            g.CompositingMode = CompositingMode.SourceOver;
            DrawAlpha(g, S.CieloDorado, 0, 0, wA);
            DrawAlpha(g, S.CieloDia, 0, 0, wB);

            if (ef > 0.01 && S.Estrellas != null) {
                for (int i = 0; i < S.Estrellas.Length; i++) {
                    var st = S.Estrellas[i];
                    double o = (i % 3 == 0) ? 0.3 + 0.7 * Osc(t, 0.10 + (i % 7) * 0.02, i * 1.3) : 1.0;
                    Px(g, st.Col, ef * o, st.X, st.Y);
                }
                Color haloStar = Color.FromArgb(199, 204, 255);
                for (int i = 0; i < S.Brillantes.Length; i++) {
                    var st = S.Brillantes[i];
                    double o = ef * 0.8 * Math.Max(0, Osc(t, 0.07 + (i % 5) * 0.01, i * 2.1) - 0.55) / 0.45;
                    if (o <= 0.004) continue;
                    Px(g, haloStar, o, st.X - 1, st.Y);
                    Px(g, haloStar, o, st.X + 1, st.Y);
                    Px(g, haloStar, o, st.X, st.Y - 1);
                    Px(g, haloStar, o, st.X, st.Y + 1);
                }
            }

            var alasSet = S.ModoWyvern ? AlasWyvern : AlasGrulla;
            int cuadro = new int[] { 0, 1, 2, 1 }[(t / 5) % 4];
            var birdPos = new double[,] {
                { ((t * 0.22 + 40) % 760) - 60, 126 + 4 * Math.Sin(t * 0.03) },
                { ((t * 0.22 + 22) % 760) - 60, 116 + 4 * Math.Sin(t * 0.03 + 1) },
                { ((t * 0.20 + 5) % 760) - 60, 138 + 4 * Math.Sin(t * 0.025 + 2) }
            };
            for (int b = 0; b < 3; b++) {
                double bx = birdPos[b, 0], by = birdPos[b, 1];
                foreach (var pt in alasSet[cuadro]) Px(g, S.ColorPajaros, 1.0, bx + pt[0], by + pt[1]);
                Px(g, S.ColorPajaros, 1.0, bx, by + 1);
            }

            if (S.ConAstro && solOp > 0.01) DrawAlpha(g, S.Sol, (int)Math.Round(solX - 104), (int)Math.Round(solY - 104), solOp);
            if (S.ConAstro && lunaOp > 0.01) DrawAlpha(g, S.Luna, (int)Math.Round(lunaX - 104), (int)Math.Round(lunaY - 104), lunaOp);

            if (S.Nubes != null) {
                bool noche = e < 0;
                double[] opNub = new double[] { noche ? 1 - wA : 0, noche ? wA : 1 - wB, wB };
                Bitmap[] imgNub = new Bitmap[] { S.NubesNoche, S.NubesDorado, S.NubesDia };
                for (int i = 0; i < S.Nubes.Length; i++) {
                    var nb = S.Nubes[i];
                    double v = 0.035 + (i % 4) * 0.012;
                    int cx = (int)Math.Round(((nb.X + nb.W + t * v) % (640 + nb.W)) - nb.W);
                    for (int k = 0; k < 3; k++) {
                        if (opNub[k] > 0.01 && imgNub[k] != null) {
                            DrawCrop(g, imgNub[k], cx, nb.Y, 0, nb.SheetY, nb.W, nb.H, opNub[k]);
                        }
                    }
                }
            }

            DrawAlpha(g, S.EscenaNoche, 0, 0, 1.0);
            DrawAlpha(g, S.EscenaDorado, 0, 0, wA);
            DrawAlpha(g, S.EscenaDia, 0, 0, wB);

            if (S.ModoMiles) { PintaFerry(g, t, nf); PintaMiles(g, t, nf); }

            if (S.Chimenea != null && S.Chimenea.Length >= 2) {
                int hx = S.Chimenea[0], hy = S.Chimenea[1];
                Color hc = wB > 0.5 ? S.ColorHumoDia : S.ColorHumoNoche;
                for (int i = 0; i < 9; i++) {
                    double fase = ((t * 0.25 + i * 5) % 45) / 45.0;
                    double sx = hx + Math.Sin(t * 0.06 + i * 1.4) * (1.5 + fase * 5) + fase * 4;
                    double sy = hy - fase * 26;
                    int sz = fase < 0.35 ? 2 : 3;
                    Px(g, hc, (1 - fase) * (0.28 + 0.16 * nf), sx, sy, sz, sz - 1);
                }
            }

            if (nf > 0.02) {
                for (int i = 0; i < S.Ventanas.Length; i++) {
                    var v = S.Ventanas[i];
                    double p = nf * (((t / 24 + i) % 13 == 0) ? 0.25 : 0.7 + 0.3 * Math.Sin(t * 0.09 * (1 + (i % 4) * 0.15) + i * 2.1));
                    Px(g, S.ColorVentanas, 0.12 * p, v.X - 1, v.Y - 1, 4, 6);
                    Px(g, S.ColorVentanas, p, v.X, v.Y, 2, 4);
                }
                for (int i = 0; i < S.Faroles.Length; i++) {
                    var fr = S.Faroles[i];
                    double p = nf * (0.65 + 0.35 * Math.Sin(t * 0.11 + i * 1.7));
                    int gr = Math.Max(2, (int)Math.Round(fr.R / 3.0));
                    Px(g, S.ColorFarolesHalo, 0.06 * p, fr.X - gr * 2, fr.Y - gr * 2, gr * 4 + 1, gr * 4 + 1);
                    Px(g, S.ColorFarolesHalo, 0.14 * p, fr.X - gr, fr.Y - gr, gr * 2 + 1, gr * 2 + 1);
                    Px(g, S.ColorFarolesCentro, p, fr.X, fr.Y, 1, 2);
                }
                if (S.Runas.Length > 0) {
                    double pr = (0.35 + 0.65 * nf) * (0.65 + 0.35 * Math.Sin(t * 0.08));
                    for (int i = 0; i < S.Runas.Length; i++) {
                        var rn = S.Runas[i];
                        double pulse = pr * (0.75 + 0.25 * Math.Sin(t * 0.12 + i * 0.4));
                        Px(g, S.ColorRunasHalo, 0.14 * pulse, rn.X - 1, rn.Y - 1, 3, 3);
                        Px(g, S.ColorRunasCentro, pulse, rn.X, rn.Y, 1, 1);
                    }
                }
            }

            foreach (var o in _olas) {
                Px(g, o.Light ? S.ColorOlas[0] : S.ColorOlas[1 % S.ColorOlas.Length],
                    (0.08 + 0.55 * Math.Max(0, Math.Sin(t * 0.04 + o.Ph))) * (1 - 0.6 * wB),
                    o.X + 6 * Math.Sin(t * o.Sp + o.Ph), o.Y, o.W, 1);
            }

            if (S.ConAstro && cuerpoOp > 0.02) {
                Color col = e > -1 ? S.ColorReflejoSol : S.ColorReflejoLuna;
                for (int i = 0; i < 38; i++) {
                    double d = 8 + i * 3, w = Math.Max(3, 46 - d * 0.30);
                    Px(g, col, cuerpoOp * (0.75 - d * 0.005) * Osc(t, 0.07, i * 1.7),
                        cuerpoX - w / 2 + 3 * Math.Sin(t * 0.05 + i * 1.3), 280 + d,
                        w * (0.45 + 0.55 * Osc(t, 0.09, i * 2.2)), 1);
                }
                double dx = cuerpoX - 352;
                for (int i = 0; i < S.Destellos.Length; i++) {
                    var ds = S.Destellos[i];
                    double op = cuerpoOp * Math.Pow(Math.Max(0, Math.Sin(t * 0.16 + i * 0.9)), 3);
                    if (op > 0.004) Px(g, S.ColorDestello, op, ds.X + dx, ds.Y, 2, 1);
                }
            }

            for (int i = 0; i < _hojas.Length; i++) {
                var p = _hojas[i];
                bool esMana = p.Tipo == 3;
                double ax = (p.X + t * p.Vx + 18 * Math.Sin(t * 0.03 + p.Ph)) % 660 - 10;
                double dirY = (esMana || S.ModoBrasas) ? -p.Vy * 0.45 : p.Vy;
                double ay = ((p.Y + t * dirY) % 420 + 420) % 420 - 10;
                if (ay >= 395) continue;
                if (esMana) {
                    double mOp = (0.25 + 0.75 * nf) * (0.45 + 0.55 * Math.Sin(t * 0.11 + i));
                    Px(g, S.ColorManaHalo, 0.25 * mOp, ax - 1, ay - 1, 3, 3);
                    Px(g, S.ColorManaCentro, mOp, ax, ay, 1, 1);
                } else if (S.ModoBrasas) {
                    double bOp = (0.35 + 0.65 * nf) * (0.5 + 0.5 * Math.Sin(t * 0.13 + i));
                    Px(g, S.ColoresHojas[p.Tipo % S.ColoresHojas.Length], bOp, ax, ay, 1, 1);
                } else {
                    bool hh = ((t / 7 + i) % 2) != 0;
                    Px(g, S.ColoresHojas[p.Tipo % S.ColoresHojas.Length], 0.92, ax, ay, hh ? 2 : 1, hh ? 1 : 2);
                }
            }

            if (nf > 0.25) {
                for (int i = 0; i < MotasMana.Length; i++) {
                    var lc = MotasMana[i];
                    double fx = lc[0] + 9 * Math.Sin(t * (0.021 + i * 0.002) + i * 2.3);
                    double fy = lc[1] + 5 * Math.Sin(t * (0.017 + i * 0.0015) + i * 1.1);
                    double b = nf * Math.Pow(Math.Max(0, Math.Sin(t * (0.05 + i * 0.004) + i * 1.9)), 2);
                    Px(g, S.ColorFuegosHalo[i % S.ColorFuegosHalo.Length], 0.28 * b, fx - 1, fy - 1, 3, 3);
                    Px(g, S.ColorFuegosCentro[i % S.ColorFuegosCentro.Length], 0.2 + 0.8 * b, fx, fy, 1, 1);
                }
            }
        }
    }
}

public class PzmWallForm : Form {
    public Bitmap FrameRef;
    public Rectangle ScreenBounds { get; set; }

    [DllImport("user32.dll")] private static extern bool SetLayeredWindowAttributes(IntPtr hwnd, uint crKey, byte bAlpha, uint dwFlags);

    public PzmWallForm(Rectangle bounds) {
        ScreenBounds = bounds;
        FormBorderStyle = FormBorderStyle.None;
        ShowInTaskbar = false;
        Enabled = false;
        DoubleBuffered = true;
        SetStyle(ControlStyles.AllPaintingInWmPaint | ControlStyles.UserPaint | ControlStyles.OptimizedDoubleBuffer | ControlStyles.Opaque, true);
        BackColor = Color.FromArgb(10, 12, 36);
        StartPosition = FormStartPosition.Manual;
        Bounds = bounds;
    }

    protected override bool ShowWithoutActivation { get { return true; } }

    protected override CreateParams CreateParams {
        get {
            var cp = base.CreateParams;
            // WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_LAYERED (requerido bajo Progman con WS_EX_NOREDIRECTIONBITMAP en Win11 24H2/26H2)
            cp.ExStyle |= 0x08000000 | 0x00000080 | 0x00080000;
            return cp;
        }
    }

    protected override void OnHandleCreated(EventArgs e) {
        base.OnHandleCreated(e);
        try { SetLayeredWindowAttributes(this.Handle, 0, 255, 0x02); } catch {}
    }

    protected override void WndProc(ref Message m) {
        if (m.Msg == 0x0014) { m.Result = (IntPtr)1; return; } // WM_ERASEBKGND
        if (m.Msg == 0x0084) { m.Result = (IntPtr)(-1); return; } // WM_NCHITTEST -> HTTRANSPARENT
        base.WndProc(ref m);
    }

    protected override void OnPaint(PaintEventArgs e) {
        var f = FrameRef;
        if (f == null) return;
        int w = ClientSize.Width, h = ClientSize.Height;
        if (w <= 0 || h <= 0) return;
        double scale = Math.Max((double)w / 640.0, (double)h / 400.0);
        float srcW = (float)(w / scale);
        float srcH = (float)(h / scale);
        float srcX = (float)((640.0 - srcW) * 0.5);
        float srcY = (float)Math.Round((400.0 - srcH) * 0.55);
        if (srcY < 0) srcY = 0;
        if (srcY + srcH > 400f) srcY = 400f - srcH;

        var g = e.Graphics;
        g.InterpolationMode = InterpolationMode.NearestNeighbor;
        g.PixelOffsetMode = PixelOffsetMode.Half;
        g.CompositingMode = CompositingMode.SourceCopy;
        g.DrawImage(f, new Rectangle(0, 0, w, h), srcX, srcY, srcW, srcH, GraphicsUnit.Pixel);
    }
}

public static class PzmDesktopHost {
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr FindWindowW(string cls, string win);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr FindWindowExW(IntPtr parent, IntPtr childAfter, string cls, string win);
    [DllImport("user32.dll")] public static extern IntPtr SendMessageTimeoutW(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam, uint flags, uint timeout, out IntPtr result);
    [DllImport("user32.dll")] public static extern IntPtr SetParent(IntPtr hWndChild, IntPtr hWndNewParent);
    [DllImport("user32.dll")] public static extern IntPtr GetParent(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool IsWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
    [DllImport("user32.dll")] public static extern int GetWindowLong(IntPtr hWnd, int nIndex);
    [DllImport("user32.dll")] public static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);
    [DllImport("user32.dll")] public static extern bool SetLayeredWindowAttributes(IntPtr hwnd, uint crKey, byte bAlpha, uint dwFlags);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern IntPtr SetProcessDpiAwarenessContext(IntPtr value);
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left, Top, Right, Bottom; }

    public static void InitDpi() {
        try { SetProcessDpiAwarenessContext(new IntPtr(-4)); } catch {}
        try { SetProcessDPIAware(); } catch {}
    }

    public static bool ResolveParent(out IntPtr targetParent, out IntPtr insertAfter, out IntPtr workerBelow, out string modeDesc) {
        targetParent = IntPtr.Zero;
        insertAfter = IntPtr.Zero;
        workerBelow = IntPtr.Zero;
        modeDesc = "none";

        IntPtr progman = FindWindowW("Progman", null);
        if (progman == IntPtr.Zero) progman = FindWindowW("Progman", "Program Manager");
        if (progman == IntPtr.Zero) return false;

        IntPtr res;
        // 0x052C con wParam=0xD,lParam=0x1 prepara WorkerW en Win10 y Win11 Raised Desktop; fallback classic 0,0
        SendMessageTimeoutW(progman, 0x052C, new IntPtr(0xD), new IntPtr(0x1), 0x0002, 1000, out res);

        IntPtr defOwner = IntPtr.Zero;
        IntPtr shellView = IntPtr.Zero;
        EnumWindows((top, lp) => {
            IntPtr sv = FindWindowExW(top, IntPtr.Zero, "SHELLDLL_DefView", null);
            if (sv != IntPtr.Zero) {
                defOwner = top;
                shellView = sv;
                return false;
            }
            return true;
        }, IntPtr.Zero);

        if (defOwner != IntPtr.Zero && defOwner != progman) {
            IntPtr behind = FindWindowExW(IntPtr.Zero, defOwner, "WorkerW", null);
            if (behind != IntPtr.Zero) {
                targetParent = behind;
                modeDesc = "split-workerw";
                return true;
            }
        }

        // Win11 24H2/26H2 Raised desktop with layered ShellView:
        // SHELLDLL_DefView vive dentro de Progman junto a un WorkerW hijo (fondo estatico).
        // Debemos colgar los formularios WS_EX_LAYERED directamente de Progman justo debajo de SHELLDLL_DefView
        // y empujar ese WorkerW hijo debajo de nuestros formularios.
        IntPtr workerChild = FindWindowExW(progman, IntPtr.Zero, "WorkerW", null);
        targetParent = progman;
        insertAfter = shellView;
        workerBelow = workerChild;
        modeDesc = (workerChild != IntPtr.Zero) ? "raised-progman-layered" : "progman-direct";
        return true;
    }

    public static bool AttachForm(PzmWallForm form, IntPtr targetParent, IntPtr insertAfter) {
        if (form == null || targetParent == IntPtr.Zero || !IsWindow(targetParent)) return false;
        if (!form.Visible) form.Show();
        int style = GetWindowLong(form.Handle, -16);
        style = (style & ~unchecked((int)0x80000000)) | 0x40000000 | 0x10000000; // WS_CHILD | WS_VISIBLE
        SetWindowLong(form.Handle, -16, style);

        int exStyle = GetWindowLong(form.Handle, -20);
        exStyle = (exStyle & ~0x00040000) | 0x08000000 | 0x00000080 | 0x00080000; // -WS_EX_APPWINDOW + NOACTIVATE|TOOLWINDOW|LAYERED
        SetWindowLong(form.Handle, -20, exStyle);

        SetParent(form.Handle, targetParent);
        SetLayeredWindowAttributes(form.Handle, 0, 255, 0x02);

        RECT pr; GetWindowRect(targetParent, out pr);
        Rectangle sb = form.ScreenBounds;
        int lx = sb.Left - pr.Left;
        int ly = sb.Top - pr.Top;
        SetWindowPos(form.Handle, insertAfter, lx, ly, sb.Width, sb.Height, 0x0010 | 0x0040 | 0x0020);
        ShowWindow(form.Handle, 8); // SW_SHOWNA
        return true;
    }

    public static void PushWorkerBelow(IntPtr progman, IntPtr workerChild, IntPtr insertAfterForm) {
        if (progman == IntPtr.Zero || workerChild == IntPtr.Zero || insertAfterForm == IntPtr.Zero) return;
        if (!IsWindow(workerChild) || !IsWindow(insertAfterForm)) return;
        RECT pr; GetWindowRect(progman, out pr);
        Rectangle vs = SystemInformation.VirtualScreen;
        SetWindowPos(workerChild, insertAfterForm, vs.Left - pr.Left, vs.Top - pr.Top, vs.Width, vs.Height, 0x0010 | 0x0040 | 0x0001);
    }
}
'@

$null = [System.Drawing.Bitmap]
$null = [System.Drawing.ColorTranslator]
$null = [System.Windows.Forms.Form]
$null = [System.Windows.Forms.Message]
$refAsms = [System.AppDomain]::CurrentDomain.GetAssemblies() |
    Where-Object {
        (-not $_.IsDynamic) -and $_.Location -and (
            $_.FullName -match '^(mscorlib|netstandard|System\.Runtime|System\.Drawing|System\.Windows\.Forms|System\.ComponentModel|System\.Private\.Windows|System\.Private\.CoreLib|System,|System\.Collections|System\.Threading)'
        )
    } |
    Select-Object -ExpandProperty Location -Unique
try {
    Add-Type -TypeDefinition $csCode -ReferencedAssemblies $refAsms -ErrorAction Stop
} catch {
    Write-MotorLog "ERROR Add-Type: $($_.Exception.Message)"
    exit 1
}
[PzmDesktopHost]::InitDpi()

function Cargar-SceneData([string]$dir, [bool]$conAstro) {
    $sd = New-Object PzmSceneData
    $sd.TemaDir = $dir
    $sd.ConAstro = $conAstro

    $datosPath = Join-Path $dir 'datos.json'
    if (Test-Path $datosPath) {
        $d = Get-Content $datosPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $stars = New-Object 'System.Collections.Generic.List[PzmStar]'
        $bright = New-Object 'System.Collections.Generic.List[PzmStar]'
        foreach ($st in $d.estrellas) {
            $ps = New-Object PzmStar
            $ps.X = [int]$st[0]; $ps.Y = [int]$st[1]
            $ps.Col = [PzmSceneData]::ParseHex([string]$st[2], [System.Drawing.Color]::White)
            $ps.Bright = [int]$st[3]
            $stars.Add($ps)
            if ($ps.Bright -eq 1) { $bright.Add($ps) }
        }
        $sd.Estrellas = $stars.ToArray()
        $sd.Brillantes = $bright.ToArray()

        $clouds = New-Object 'System.Collections.Generic.List[PzmCloud]'
        foreach ($nb in $d.nubes) {
            $pc = New-Object PzmCloud
            $pc.X = [int]$nb[0]; $pc.Y = [int]$nb[1]; $pc.W = [int]$nb[2]; $pc.H = [int]$nb[3]; $pc.SheetY = [int]$nb[4]
            $clouds.Add($pc)
        }
        $sd.Nubes = $clouds.ToArray()

        if ($d.chimenea) { $sd.Chimenea = [int[]]@([int]$d.chimenea[0], [int]$d.chimenea[1]) }

        $wins = New-Object 'System.Collections.Generic.List[PzmLight]'
        foreach ($v in $d.ventanas) {
            $pl = New-Object PzmLight; $pl.X = [int]$v[0]; $pl.Y = [int]$v[1]; $pl.R = 0
            $wins.Add($pl)
        }
        $sd.Ventanas = $wins.ToArray()

        $lants = New-Object 'System.Collections.Generic.List[PzmLight]'
        foreach ($fr in $d.faroles) {
            $pl = New-Object PzmLight; $pl.X = [int]$fr[0]; $pl.Y = [int]$fr[1]; $pl.R = if ($fr.Count -ge 3) { [int]$fr[2] } else { 6 }
            $lants.Add($pl)
        }
        $sd.Faroles = $lants.ToArray()

        $runes = New-Object 'System.Collections.Generic.List[PzmLight]'
        if ($d.runas) {
            foreach ($rn in $d.runas) {
                $pl = New-Object PzmLight; $pl.X = [int]$rn[0]; $pl.Y = [int]$rn[1]; $pl.R = 1
                $runes.Add($pl)
            }
        }
        $sd.Runas = $runes.ToArray()

        $dest = New-Object 'System.Collections.Generic.List[System.Drawing.Point]'
        foreach ($ds in $d.destellos) {
            $dest.Add((New-Object System.Drawing.Point([int]$ds[0], [int]$ds[1])))
        }
        $sd.Destellos = $dest.ToArray()
    }

    $temaPath = Join-Path $dir 'tema.json'
    if (Test-Path $temaPath) {
        $t = Get-Content $temaPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $sd.ModoWyvern = ($t.modo_pajaros -eq 'wyverns')
        $sd.ModoMiles = ($t.modo_heroe -eq 'miles_morales')
        $sd.ModoBrasas = ($t.modo_particulas -eq 'brasas_mana')
        $sd.ColorPajaros = [PzmSceneData]::ParseHex($t.color_pajaros, $sd.ColorPajaros)
        $sd.ColorHumoDia = [PzmSceneData]::ParseHex($t.color_humo_dia, $sd.ColorHumoDia)
        $sd.ColorHumoNoche = [PzmSceneData]::ParseHex($t.color_humo_noche, $sd.ColorHumoNoche)
        $sd.ColorVentanas = [PzmSceneData]::ParseHex($t.color_ventanas, $sd.ColorVentanas)
        $sd.ColorFarolesHalo = [PzmSceneData]::ParseHex($t.color_faroles_halo, $sd.ColorFarolesHalo)
        $sd.ColorFarolesCentro = [PzmSceneData]::ParseHex($t.color_faroles_centro, $sd.ColorFarolesCentro)
        $sd.ColorRunasHalo = [PzmSceneData]::ParseHex($t.color_runas_halo, $sd.ColorRunasHalo)
        $sd.ColorRunasCentro = [PzmSceneData]::ParseHex($t.color_runas_centro, $sd.ColorRunasCentro)
        $sd.ColorReflejoSol = [PzmSceneData]::ParseHex($t.color_reflejo_sol, $sd.ColorReflejoSol)
        $sd.ColorReflejoLuna = [PzmSceneData]::ParseHex($t.color_reflejo_luna, $sd.ColorReflejoLuna)
        $sd.ColorDestello = [PzmSceneData]::ParseHex($t.color_destello, $sd.ColorDestello)
        $sd.ColorManaHalo = [PzmSceneData]::ParseHex($t.color_mana_halo, $sd.ColorManaHalo)
        $sd.ColorManaCentro = [PzmSceneData]::ParseHex($t.color_mana_centro, $sd.ColorManaCentro)
        if ($t.color_olas) { $sd.ColorOlas = @($t.color_olas | ForEach-Object { [PzmSceneData]::ParseHex($_, $sd.ColorOlas[0]) }) }
        if ($t.colores_hojas) { $sd.ColoresHojas = @($t.colores_hojas | ForEach-Object { [PzmSceneData]::ParseHex($_, $sd.ColoresHojas[0]) }) }
        if ($t.color_fuegos_halo) { $sd.ColorFuegosHalo = @($t.color_fuegos_halo | ForEach-Object { [PzmSceneData]::ParseHex($_, $sd.ColorFuegosHalo[0]) }) }
        if ($t.color_fuegos_centro) { $sd.ColorFuegosCentro = @($t.color_fuegos_centro | ForEach-Object { [PzmSceneData]::ParseHex($_, $sd.ColorFuegosCentro[0]) }) }
    }

    $sd.LoadImages()
    return $sd
}

function Resolver-RutaVariante([string]$temaDir, [string]$variante) {
    $sub = switch ($variante) {
        'secundaria' { 'secundario' }
        'bloqueo'    { 'bloqueo' }
        default      { '' }
    }
    $cand = if ($sub) { Join-Path $temaDir $sub } else { $temaDir }
    if (Test-Path (Join-Path $cand 'images')) {
        return @{ Dir = $cand; ConAstro = ($variante -ne 'secundaria') }
    }
    return @{ Dir = $temaDir; ConAstro = $true }
}

$script:desktopParent = [IntPtr]::Zero
$script:desktopAfter = [IntPtr]::Zero
$script:desktopWorkerBelow = [IntPtr]::Zero
$script:desktopMode = 'none'
if (-not [PzmDesktopHost]::ResolveParent([ref]$script:desktopParent, [ref]$script:desktopAfter, [ref]$script:desktopWorkerBelow, [ref]$script:desktopMode)) {
    Write-MotorLog "ResolveParent fallo: no hay Progman visible en esta sesion"
    exit 0
}
Write-MotorLog "ResolveParent OK: modo=$($script:desktopMode) parent=$($script:desktopParent) after=$($script:desktopAfter) workerBelow=$($script:desktopWorkerBelow)"

$script:temaAct = $Tema
$script:modoAct = $Modo
$script:horaAct = $Hora
$script:monAct = $Monitores
$script:fondoPrimAct = if ($FondoPrincipal) { $FondoPrincipal } else { 'principal' }
$script:fondoSecAct = if ($FondoSecundario) { $FondoSecundario } else { 'secundaria' }

$script:rendPrim = New-Object PzmRenderer
$script:rendSec = New-Object PzmRenderer
$script:scenePrim = $null
$script:sceneSec = $null
$script:forms = @()

function Recargar-Escenas {
    $tDir = Join-Path $TemasBase $script:temaAct
    if (-not (Test-Path (Join-Path $tDir 'images'))) {
        Write-MotorLog "Recargar-Escenas: tema inexistente $tDir"
        return
    }
    if ($script:scenePrim) { $script:scenePrim.DisposeImages() }
    if ($script:sceneSec) { $script:sceneSec.DisposeImages() }

    $rPrim = Resolver-RutaVariante $tDir $script:fondoPrimAct
    $script:scenePrim = Cargar-SceneData $rPrim.Dir $rPrim.ConAstro

    if ($script:monAct -ge 2) {
        $rSec = Resolver-RutaVariante $tDir $script:fondoSecAct
        $script:sceneSec = Cargar-SceneData $rSec.Dir $rSec.ConAstro
    } else {
        $script:sceneSec = $null
    }

    foreach ($fItem in $script:forms) {
        if ($fItem.EsSecundario -and $script:sceneSec) {
            $fItem.Form.FrameRef = $script:rendSec.Frame
        } else {
            $fItem.Form.FrameRef = $script:rendPrim.Frame
        }
    }
    Write-MotorLog "Escenas cargadas: tema=$($script:temaAct) mon=$($script:monAct) prim=$($script:fondoPrimAct) sec=$($script:fondoSecAct)"
}

$curAfter = $script:desktopAfter
foreach ($scr in [System.Windows.Forms.Screen]::AllScreens) {
    $form = New-Object PzmWallForm($scr.Bounds)
    $okAttach = [PzmDesktopHost]::AttachForm($form, $script:desktopParent, $curAfter)
    if ($curAfter -ne [IntPtr]::Zero -or $script:desktopMode -ne 'split-workerw') {
        $curAfter = $form.Handle
    }
    Write-MotorLog "Monitor Primary=$($scr.Primary) Bounds=$($scr.Bounds) hwnd=$($form.Handle) attach=$okAttach"
    $script:forms += [pscustomobject]@{
        Form = $form
        EsSecundario = (-not $scr.Primary)
    }
}
if ($script:desktopWorkerBelow -ne [IntPtr]::Zero -and $script:forms.Count -gt 0) {
    [PzmDesktopHost]::PushWorkerBelow($script:desktopParent, $script:desktopWorkerBelow, $script:forms[-1].Form.Handle)
}

Recargar-Escenas

$script:tick = 0
$script:ahoraIni = Get-Date
$script:horaIni = $script:ahoraIni.Hour + ($script:ahoraIni.Minute / 60.0) + ($script:ahoraIni.Second / 3600.0)
$script:sw = [System.Diagnostics.Stopwatch]::StartNew()
$script:lastCfgWrite = if (Test-Path $ConfigPath) { (Get-Item $ConfigPath).LastWriteTimeUtc } else { [DateTime]::MinValue }

function Render-MotorFrame([int]$t) {
    $elapsed = $script:sw.Elapsed.TotalSeconds
    $d = Get-Date
    if ($script:modoAct -eq 'fija') {
        $hv = $script:horaAct % 24.0
        $hh = [int][Math]::Floor($hv)
        $mm = [int][Math]::Floor(($hv - $hh) * 60)
        $d = [DateTime]::new($d.Year, $d.Month, $d.Day, $hh, $mm, 0)
    } elseif ($script:modoAct -eq '90m') {
        $hv = ($script:horaIni + ($elapsed / 5400.0) * 24.0) % 24.0
        $hh = [int][Math]::Floor($hv)
        $rem = ($hv - $hh) * 60.0
        $mm = [int][Math]::Floor($rem)
        $ss = [int][Math]::Floor(($rem - $mm) * 60.0)
        $d = [DateTime]::new($d.Year, $d.Month, $d.Day, $hh, $mm, [Math]::Min(59, $ss))
    } elseif ($script:modoAct -eq 'demo') {
        $hv = (($elapsed % 90.0) / 90.0) * 24.0
        $hh = [int][Math]::Floor($hv)
        $rem = ($hv - $hh) * 60.0
        $mm = [int][Math]::Floor($rem)
        $ss = [int][Math]::Floor(($rem - $mm) * 60.0)
        $d = [DateTime]::new($d.Year, $d.Month, $d.Day, $hh, $mm, [Math]::Min(59, $ss))
    }

    if ($script:scenePrim) { $script:rendPrim.Render($script:scenePrim, $d, $t) }
    if ($script:sceneSec)  { $script:rendSec.Render($script:sceneSec, $d, $t) }
    foreach ($fItem in $script:forms) {
        $fItem.Form.Invalidate()
    }
}

Render-MotorFrame 0
foreach ($fItem in $script:forms) { $fItem.Form.Update() }

$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = [Math]::Max(42, [int](1000 / [Math]::Max(2, [Math]::Min(24, $Fps))))

$timer.Add_Tick({
    $script:tick++
    $t = $script:tick

    if (($t % 8) -eq 0 -and (Test-Path $ConfigPath)) {
        try {
            $wt = (Get-Item $ConfigPath).LastWriteTimeUtc
            if ($wt -ne $script:lastCfgWrite) {
                $script:lastCfgWrite = $wt
                $nc = Get-Content $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($nc) {
                    $fp = if ($nc.fondoPrincipal) { [string]$nc.fondoPrincipal } else { $script:fondoPrimAct }
                    $fs = if ($nc.fondoSecundario) { [string]$nc.fondoSecundario } else { $script:fondoSecAct }
                    $cambio = ($nc.tema -ne $script:temaAct) -or ([int]$nc.monitores -ne $script:monAct) -or ($fp -ne $script:fondoPrimAct) -or ($fs -ne $script:fondoSecAct)
                    if ($nc.tema) { $script:temaAct = [string]$nc.tema }
                    if ($nc.monitores) { $script:monAct = [int]$nc.monitores }
                    $script:fondoPrimAct = $fp
                    $script:fondoSecAct = $fs
                    if ($nc.modo -and $nc.modo -ne $script:modoAct) {
                        $script:modoAct = [string]$nc.modo
                        $script:ahoraIni = Get-Date
                        $script:horaIni = $script:ahoraIni.Hour + ($script:ahoraIni.Minute / 60.0) + ($script:ahoraIni.Second / 3600.0)
                        $script:sw.Restart()
                    }
                    if ($null -ne $nc.horaFija) { $script:horaAct = [double]$nc.horaFija }
                    if ($cambio) { Recargar-Escenas }
                }
            }
        } catch {}
    }

    if (($t % 40) -eq 0 -and $script:forms.Count -gt 0) {
        $f0 = $script:forms[0].Form
        if ((-not [PzmDesktopHost]::IsWindow($script:desktopParent)) -or ([PzmDesktopHost]::GetParent($f0.Handle) -ne $script:desktopParent)) {
            if ([PzmDesktopHost]::ResolveParent([ref]$script:desktopParent, [ref]$script:desktopAfter, [ref]$script:desktopWorkerBelow, [ref]$script:desktopMode)) {
                $curA = $script:desktopAfter
                foreach ($fItem in $script:forms) {
                    $null = [PzmDesktopHost]::AttachForm($fItem.Form, $script:desktopParent, $curA)
                    if ($curA -ne [IntPtr]::Zero -or $script:desktopMode -ne 'split-workerw') {
                        $curA = $fItem.Form.Handle
                    }
                }
            }
        }
        if ($script:desktopWorkerBelow -ne [IntPtr]::Zero) {
            [PzmDesktopHost]::PushWorkerBelow($script:desktopParent, $script:desktopWorkerBelow, $script:forms[-1].Form.Handle)
        }
    }

    Render-MotorFrame $t
})

$timer.Start()
[System.Windows.Forms.Application]::Run()
