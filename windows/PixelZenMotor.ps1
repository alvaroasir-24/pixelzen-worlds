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
    public bool ModoMilesColgado;
    public bool ModoBrasas;
    public bool SinLago;
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
            "......................RRK.", ".....................RRKK.", "....................KKK...",
            "..........KKKKKK...KKK....", ".........KKKKKKKK.KKK.....", "........KKWWKKWWKKKR......",
            "........KKWWKKWWKKK.......", ".........KKKKKKKKK........", "......KKKKKRRRRKK.........",
            ".....KKRRKKRRRRK..........", "....KKR.KKRKKRRKKKKKKKK...", "...KKK..KKRRRRKKKKKKSSK...",
            "..KK....KKRRKK...KKK..KK..", "..K.....KK.KK.....KK....K.", ".......KK...KK............",
            "......KK.....RR...........", ".....RR......WW...........", ".....WW..................."
        },
        new string[] {
            "..................RRK.....", ".................RRKK.....", "................KKK.......",
            ".........KKKKKK.KKK.......", "........KKKKKKKKKK........", ".......KKWWKKWWKKK........",
            ".......KKWWKKWWKKK........", "........KKKKKKKKK.........", ".....KKKKKKRRRKK..........",
            "....KKRKKRRRRRKK..........", "....KK.KKRKKRRKKKKKKKK....", "...KK..KKRRRRKKKKKKSSK....",
            "...K...KKRRKK...KKK..KK...", "......KK..KK.....KK.......", ".....KK....RR.............",
            "....RRR....WW.............", "....WWW...................", ".........................."
        },
        new string[] {
            "...............RRK........", "..............RRKK........", ".............KKK..........",
            ".......KKKKKKKR...........", "......KKKKKKKKK...........", ".....KKWWKKWWKKK..........",
            ".....KKWWKKWWKKK..........", "......KKKKKKKKK...........", "....KKKKKRRRKK............",
            "...KKRKKRRRRKK............", "...KK.KKRKKRRKKKKKKK......", "..KK..KKRRRRKKKKSSKK......",
            "..K...KKRRKK..KKK..KK.....", ".....KK..KK....KK.........", "....KK....RR..............",
            "...RRR....WW..............", "...WWW....................", ".........................."
        },
        new string[] {
            ".........KKKKKK...........", "........KKKKKKKK..........", ".......KKWWKKWWKKK..RRK...",
            ".......KKWWKKWWKKK.RRKK...", "........KKKKKKKKK.KKK.....", "......KKKKKKKKKKK.KK......",
            ".....KKRRKKRRRRKKKK.......", "....KKR.KKRKKRRKKRRKK.....", "...KKK..KKRRRRKK..SSKK....",
            "...KK...KKRRKK.....KK.K...", ".......KK..KK.............", "......KK....RR............",
            ".....RRR....WW............", ".....WWW..................", "..........................",
            "..........................", "..........................", ".........................."
        }
    };
    static readonly int[] MilesHc = new int[] { 23, 19, 16, 22 };
    static readonly int[] MilesHr = new int[] { 0, 0, 0, 2 };

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

    static readonly string[][] MilesHangRows = new string[][] {
        new string[] {
            "......BRB......", ".....BKKKB.....", "....BKK.KKB....", "...BKK...KKB...",
            "...BRK...KRB...", "....BKKKKKB....", "...BKKRRRKKB...", "..BKKRRRRRKKB..",
            "..BRKRRRRRKRB..", ".BKK.KKKKK.KKB.", ".BK...KRK...KB.", "....BKKKKKB....",
            "...BKKKKKKKB...", "..BKKWKKKWKKB..", "..BKWWKKKWWKB..", "..BKKWKKKWKKB..",
            "...BKKRRRKKB...", "....BKKKKKB....",
        },
        new string[] {
            "......BRB......", ".....BKKKB.....", "....BKK.KKB....", "...BKK...KKB...",
            "...BRK...KRB...", "....BKKKKKB....", "...BKKRRRKKB...", "..BKKRRRRRKKB..",
            "..BRKRRRRRKRB..", "..BK.KKKKK.KKB.", ".....BKRK...KB.", "....BKKKKKB....",
            "...BKKKKKKKB...", "..BKKKKKKKKKB..", "..BKKWKKKWKKB..", "..BKKKKKKKKKB..",
            "...BKKRRRKKB...", "....BKKKKKB....",
        },
    };

    void PintaMilesColgado(Graphics g, int t, double nf) {
        int CYCLE = 220;
        int[] xs = new int[] { 108, 224, 348, 418, 162, 578 };
        int[] dropYs = new int[] { 96, 82, 108, 88, 76, 94 };
        int slot = (int)Math.Floor((double)t / CYCLE);
        int idx = ((slot % xs.Length) + xs.Length) % xs.Length;
        double u = (double)(((t % CYCLE) + CYCLE) % CYCLE) / CYCLE;
        if (u < 0.14 || u >= 0.88) return;

        int anchorX = xs[idx], targetY = dropYs[idx];
        int yTop;
        double swayAmp;
        if (u < 0.30) {
            double p = (u - 0.14) / 0.16;
            double ease = 1.0 - (1.0 - p) * (1.0 - p);
            yTop = (int)Math.Round(-20.0 + (targetY + 20) * ease + Math.Sin(p * Math.PI) * 5.0);
            swayAmp = 1.0;
        } else if (u < 0.72) {
            yTop = (int)Math.Round(targetY + Math.Sin(t * 0.22));
            swayAmp = 2.0;
        } else {
            double p = (u - 0.72) / 0.16;
            yTop = (int)Math.Round(targetY - (targetY + 22) * (p * p));
            swayAmp = 1.0;
        }

        int mx = anchorX + (int)Math.Round(Math.Sin(t * 0.14) * swayAmp);
        int footY = yTop + 1;
        if (footY > 0) {
            int steps = Math.Max(1, footY);
            Color wc = Color.FromArgb(220, 234, 255);
            for (int i = 0; i <= steps; i++) {
                int wx = (int)Math.Round(anchorX + (mx - anchorX) * (double)i / steps);
                int wy = (int)Math.Round(footY * (double)i / steps);
                if (wy >= 0) Px(g, wc, ((i % 2 == 0) ? 0.86 : 0.64) * (1.0 - 0.12 * nf), wx, wy, 1, 1);
            }
        }

        int fIdx = (u >= 0.30 && u < 0.72 && (t % 64) < 5) ? 1 : 0;
        string[] rows = MilesHangRows[fIdx];
        Color cK = Color.FromArgb(21, 21, 33);
        Color cR = Color.FromArgb(235, 45, 60);
        Color cW = Color.FromArgb(228, 238, 255);
        Color cB = Color.FromArgb(74, 82, 122);
        for (int r = 0; r < rows.Length; r++) {
            int ry = yTop + r;
            if (ry < 0) continue;
            string row = rows[r];
            for (int c = 0; c < row.Length; c++) {
                char ch = row[c];
                if (ch == '.') continue;
                Color col = ch == 'K' ? cK : (ch == 'R' ? cR : (ch == 'W' ? cW : cB));
                Px(g, col, 1.0, mx + c - 7, ry, 1, 1);
            }
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
                    double v = 0.11 + (i % 4) * 0.035;
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
            else if (S.ModoMilesColgado) { PintaFerry(g, t, nf); PintaMilesColgado(g, t, nf); }

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

            if (!S.SinLago) {
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

public class PzmDCompHost : IDisposable {
    [DllImport("d3d11.dll")]
    static extern int D3D11CreateDevice(IntPtr pAdapter, int DriverType, IntPtr Software, uint Flags,
        [In] int[] pFeatureLevels, uint FeatureLevels, uint SDKVersion,
        out IntPtr ppDevice, out int pFeatureLevel, out IntPtr ppImmediateContext);

    [DllImport("dcomp.dll")]
    static extern int DCompositionCreateDevice(IntPtr dxgiDevice, ref Guid iid, out IntPtr dcompositionDevice);

    [StructLayout(LayoutKind.Sequential)] struct DXGI_SAMPLE_DESC { public uint Count, Quality; }
    [StructLayout(LayoutKind.Sequential)] struct DXGI_SWAP_CHAIN_DESC1 {
        public uint Width, Height, Format;
        public int Stereo;
        public DXGI_SAMPLE_DESC SampleDesc;
        public uint BufferUsage, BufferCount, Scaling, SwapEffect, AlphaMode, Flags;
    }

    [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate int FnQI(IntPtr obj, ref Guid riid, out IntPtr ppv);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate uint FnRel(IntPtr obj);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate int FnGetAdapter(IntPtr obj, out IntPtr adapter);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate int FnGetParent(IntPtr obj, ref Guid riid, out IntPtr parent);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate int FnCreateSwapForComp(IntPtr factory2, IntPtr dev, ref DXGI_SWAP_CHAIN_DESC1 desc, IntPtr restrictOut, out IntPtr sc);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate int FnDCompCommit(IntPtr dcomp);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate int FnCreateTarget(IntPtr dcomp, IntPtr hwnd, int topmost, out IntPtr target);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate int FnCreateVisual(IntPtr dcomp, out IntPtr visual);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate int FnSetRoot(IntPtr target, IntPtr visual);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate int FnSetContent(IntPtr visual, IntPtr content);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate int FnGetBuffer(IntPtr sc, uint buf, ref Guid riid, out IntPtr surf);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate int FnPresent(IntPtr sc, uint sync, uint flags);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)] delegate void FnUpdateSub(IntPtr ctx, IntPtr dst, uint sub, IntPtr box, IntPtr src, uint rowPitch, uint depthPitch);

    static T VFn<T>(IntPtr comObj, int slot) where T : class {
        IntPtr vtbl = Marshal.ReadIntPtr(comObj);
        IntPtr fnPtr = Marshal.ReadIntPtr(vtbl, slot * IntPtr.Size);
        return Marshal.GetDelegateForFunctionPointer(fnPtr, typeof(T)) as T;
    }

    public IntPtr Dev, Ctx, DxgiDev, Adapter, Factory2, DComp;
    public int FeatureLevel;
    public bool Ready;
    public string InitDiag = "none";
    public int LastCommitHr;
    private static readonly Guid IidTex2D = new Guid("6f15aaf2-d208-4e89-9ab4-489535d34f9c");

    public PzmDCompHost() {
        try {
            int[] fls = new int[] { 0xb000, 0xa100, 0xa000 };
            int hr = D3D11CreateDevice(IntPtr.Zero, 1, IntPtr.Zero, 0x20, fls, 3, 7, out Dev, out FeatureLevel, out Ctx);
            string drv = "hw";
            if (hr != 0) {
                drv = "warp";
                hr = D3D11CreateDevice(IntPtr.Zero, 5, IntPtr.Zero, 0x20, fls, 3, 7, out Dev, out FeatureLevel, out Ctx);
            }
            if (hr != 0) { InitDiag = string.Format("d3d11=0x{0:X8}", hr); Dispose(); return; }

            Guid iidDxgi = new Guid("54ec77fa-1377-44e6-8c32-88fd5f44c84c");
            hr = VFn<FnQI>(Dev, 0)(Dev, ref iidDxgi, out DxgiDev);
            if (hr != 0) { InitDiag = string.Format("qidxgi=0x{0:X8}", hr); Dispose(); return; }

            hr = VFn<FnGetAdapter>(DxgiDev, 7)(DxgiDev, out Adapter);
            if (hr != 0) { InitDiag = string.Format("adapter=0x{0:X8}", hr); Dispose(); return; }

            Guid iidFac2 = new Guid("50c83a1c-e072-4c48-87b0-3630fa36a6d0");
            hr = VFn<FnGetParent>(Adapter, 6)(Adapter, ref iidFac2, out Factory2);
            if (hr != 0) { InitDiag = string.Format("fac2=0x{0:X8}", hr); Dispose(); return; }

            Guid iidDc = new Guid("C37EA93A-E7AA-450D-B16F-9746CB0407F3");
            hr = DCompositionCreateDevice(DxgiDev, ref iidDc, out DComp);
            if (hr != 0) { InitDiag = string.Format("dcomp=0x{0:X8}", hr); Dispose(); return; }

            Ready = true;
            InitDiag = string.Format("{0}/0x{1:X}", drv, FeatureLevel);
        } catch (Exception ex) {
            InitDiag = "ex:" + ex.Message;
            Dispose();
        }
    }

    public bool BindWindow(IntPtr hwnd, int w, int h, out IntPtr target, out IntPtr visual, out IntPtr swapChain, out string err) {
        target = IntPtr.Zero; visual = IntPtr.Zero; swapChain = IntPtr.Zero; err = "ok";
        if (!Ready || hwnd == IntPtr.Zero || w <= 0 || h <= 0) { err = "not-ready"; return false; }
        int hr = VFn<FnCreateTarget>(DComp, 6)(DComp, hwnd, 0, out target);
        if (hr != 0) { err = string.Format("target=0x{0:X8}", hr); return false; }

        hr = VFn<FnCreateVisual>(DComp, 7)(DComp, out visual);
        if (hr != 0) { err = string.Format("visual=0x{0:X8}", hr); ReleaseBind(ref target, ref visual, ref swapChain); return false; }

        hr = VFn<FnSetRoot>(target, 3)(target, visual);
        if (hr != 0) { err = string.Format("setroot=0x{0:X8}", hr); ReleaseBind(ref target, ref visual, ref swapChain); return false; }

        var desc = new DXGI_SWAP_CHAIN_DESC1 {
            Width = (uint)w, Height = (uint)h, Format = 87, Stereo = 0,
            SampleDesc = new DXGI_SAMPLE_DESC { Count = 1, Quality = 0 },
            BufferUsage = 0x20, BufferCount = 2, Scaling = 0, SwapEffect = 4, AlphaMode = 3, Flags = 0
        };
        hr = VFn<FnCreateSwapForComp>(Factory2, 24)(Factory2, Dev, ref desc, IntPtr.Zero, out swapChain);
        if (hr != 0) { err = string.Format("sc=0x{0:X8}", hr); ReleaseBind(ref target, ref visual, ref swapChain); return false; }

        hr = VFn<FnSetContent>(visual, 15)(visual, swapChain);
        if (hr != 0) { err = string.Format("content=0x{0:X8}", hr); ReleaseBind(ref target, ref visual, ref swapChain); return false; }

        LastCommitHr = VFn<FnDCompCommit>(DComp, 3)(DComp);
        return LastCommitHr >= 0;
    }

    public int PresentPixels(IntPtr swapChain, int[] pixels, int w) {
        if (!Ready || swapChain == IntPtr.Zero) return -1;
        IntPtr tex;
        Guid iid = IidTex2D;
        int hr = VFn<FnGetBuffer>(swapChain, 9)(swapChain, 0, ref iid, out tex);
        if (hr != 0) return hr;
        GCHandle pin = GCHandle.Alloc(pixels, GCHandleType.Pinned);
        try {
            VFn<FnUpdateSub>(Ctx, 48)(Ctx, tex, 0, IntPtr.Zero, pin.AddrOfPinnedObject(), (uint)(w * 4), 0);
        } finally {
            pin.Free();
            VFn<FnRel>(tex, 2)(tex);
        }
        return VFn<FnPresent>(swapChain, 8)(swapChain, 0, 0);
    }

    public void Commit() {
        if (Ready && DComp != IntPtr.Zero) {
            LastCommitHr = VFn<FnDCompCommit>(DComp, 3)(DComp);
        }
    }

    public static void ReleaseBind(ref IntPtr target, ref IntPtr visual, ref IntPtr swapChain) {
        if (swapChain != IntPtr.Zero) { VFn<FnRel>(swapChain, 2)(swapChain); swapChain = IntPtr.Zero; }
        if (visual != IntPtr.Zero) { VFn<FnRel>(visual, 2)(visual); visual = IntPtr.Zero; }
        if (target != IntPtr.Zero) { VFn<FnRel>(target, 2)(target); target = IntPtr.Zero; }
    }

    public void Dispose() {
        Ready = false;
        IntPtr[] ptrs = new IntPtr[] { DComp, Factory2, Adapter, DxgiDev, Ctx, Dev };
        DComp = Factory2 = Adapter = DxgiDev = Ctx = Dev = IntPtr.Zero;
        foreach (var p in ptrs) { if (p != IntPtr.Zero) { try { VFn<FnRel>(p, 2)(p); } catch {} } }
    }
}

public class PzmWallForm : Form {
    public Bitmap FrameRef;
    public Rectangle ScreenBounds { get; set; }
    public PzmDCompHost DCompHost;
    public bool UseDComp = false;
    public int PaintCount = 0;
    public bool LastUlwOk = false;
    public int LastUlwErr = 0;
    public int LastPresentHr = 0;
    public string BindErr = "none";
    private bool _fallbackGdi = false;

    private IntPtr _dcTarget = IntPtr.Zero;
    private IntPtr _dcVisual = IntPtr.Zero;
    private IntPtr _dcSwap = IntPtr.Zero;
    private int _dcW = 0, _dcH = 0;
    private int[] _srcBuf = new int[640 * 400];
    private int[] _dstBuf = null;
    private int[] _xMap = null;
    private int[] _yMap = null;

    private IntPtr _memDc = IntPtr.Zero;
    private IntPtr _hDib = IntPtr.Zero;
    private IntPtr _oldBmp = IntPtr.Zero;
    private int _dibW = 0;
    private int _dibH = 0;

    [StructLayout(LayoutKind.Sequential)] private struct WPOINT { public int X, Y; }
    [StructLayout(LayoutKind.Sequential)] private struct WSIZE { public int cx, cy; }
    [StructLayout(LayoutKind.Sequential, Pack=1)] private struct BLENDFUNCTION { public byte BlendOp, BlendFlags, SourceConstantAlpha, AlphaFormat; }
    [StructLayout(LayoutKind.Sequential)] private struct BITMAPINFOHEADER {
        public int biSize, biWidth, biHeight;
        public short biPlanes, biBitCount;
        public int biCompression, biSizeImage, biXPelsPerMeter, biYPelsPerMeter, biClrUsed, biClrImportant;
    }

    [DllImport("user32.dll", SetLastError=true)] private static extern bool UpdateLayeredWindow(IntPtr hwnd, IntPtr hdcDst, IntPtr pptDst, ref WSIZE psize, IntPtr hdcSrc, ref WPOINT pptSrc, uint crKey, ref BLENDFUNCTION pblend, uint dwFlags);
    [DllImport("user32.dll")] private static extern bool SetLayeredWindowAttributes(IntPtr hwnd, uint crKey, byte bAlpha, uint dwFlags);
    [DllImport("user32.dll")] private static extern int GetWindowLong(IntPtr hWnd, int nIndex);
    [DllImport("user32.dll")] private static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);
    [DllImport("user32.dll")] private static extern IntPtr GetDC(IntPtr hWnd);
    [DllImport("user32.dll")] private static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);
    [DllImport("gdi32.dll")] private static extern IntPtr CreateCompatibleDC(IntPtr hdc);
    [DllImport("gdi32.dll")] private static extern bool DeleteDC(IntPtr hdc);
    [DllImport("gdi32.dll")] private static extern IntPtr SelectObject(IntPtr hdc, IntPtr h);
    [DllImport("gdi32.dll")] private static extern bool DeleteObject(IntPtr ho);
    [DllImport("gdi32.dll")] private static extern IntPtr CreateDIBSection(IntPtr hdc, ref BITMAPINFOHEADER pbmi, uint iUsage, out IntPtr ppvBits, IntPtr hSection, uint dwOffset);

    public PzmWallForm(Rectangle bounds, PzmDCompHost dcomp) {
        ScreenBounds = bounds;
        DCompHost = dcomp;
        UseDComp = (dcomp != null && dcomp.Ready);
        FormBorderStyle = FormBorderStyle.None;
        ShowInTaskbar = false;
        Enabled = false;
        SetStyle(ControlStyles.AllPaintingInWmPaint | ControlStyles.UserPaint | ControlStyles.Opaque, true);
        BackColor = Color.FromArgb(10, 12, 36);
        StartPosition = FormStartPosition.Manual;
        Bounds = bounds;
    }

    protected override bool ShowWithoutActivation { get { return true; } }

    protected override CreateParams CreateParams {
        get {
            var cp = base.CreateParams;
            // DirectComposition: WS_EX_NOREDIRECTIONBITMAP | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TRANSPARENT
            // Layered fallback: WS_EX_LAYERED | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TRANSPARENT
            int modeEx = UseDComp ? 0x00200000 : 0x00080000;
            cp.ExStyle |= 0x08000000 | 0x00000080 | 0x00000020 | modeEx;
            return cp;
        }
    }

    protected override void WndProc(ref Message m) {
        if (m.Msg == 0x0014) { m.Result = (IntPtr)1; return; } // WM_ERASEBKGND
        if (m.Msg == 0x0084) { m.Result = (IntPtr)(-1); return; } // WM_NCHITTEST -> HTTRANSPARENT
        base.WndProc(ref m);
    }

    private void ReleaseDib() {
        if (_memDc != IntPtr.Zero) {
            if (_oldBmp != IntPtr.Zero) { SelectObject(_memDc, _oldBmp); _oldBmp = IntPtr.Zero; }
            if (_hDib != IntPtr.Zero) { DeleteObject(_hDib); _hDib = IntPtr.Zero; }
            DeleteDC(_memDc);
            _memDc = IntPtr.Zero;
        }
        _dibW = 0; _dibH = 0;
    }

    private bool EnsureDib(int w, int h) {
        if (_memDc != IntPtr.Zero && _dibW == w && _dibH == h) return true;
        ReleaseDib();
        IntPtr screenDc = GetDC(IntPtr.Zero);
        try {
            _memDc = CreateCompatibleDC(screenDc);
            if (_memDc == IntPtr.Zero) return false;
            var bi = new BITMAPINFOHEADER {
                biSize = Marshal.SizeOf(typeof(BITMAPINFOHEADER)),
                biWidth = w,
                biHeight = -h, // top-down DIB
                biPlanes = 1,
                biBitCount = 32,
                biCompression = 0
            };
            IntPtr bits;
            _hDib = CreateDIBSection(screenDc, ref bi, 0, out bits, IntPtr.Zero, 0);
            if (_hDib == IntPtr.Zero) { ReleaseDib(); return false; }
            _oldBmp = SelectObject(_memDc, _hDib);
            _dibW = w; _dibH = h;
            return true;
        } finally {
            ReleaseDC(IntPtr.Zero, screenDc);
        }
    }

    private void ComputeSourceCrop(int w, int h, out float srcX, out float srcY, out float srcW, out float srcH, out double scale) {
        scale = Math.Max((double)w / 640.0, (double)h / 400.0);
        srcW = (float)(w / scale);
        srcH = (float)(h / scale);
        srcX = (float)((640.0 - srcW) * 0.5);
        srcY = (float)Math.Round((400.0 - srcH) * 0.55);
        if (srcY < 0) srcY = 0;
        if (srcY + srcH > 400f) srcY = 400f - srcH;
    }

    private bool EnsureDCompBuffers(int w, int h) {
        if (_dcSwap != IntPtr.Zero && _dcW == w && _dcH == h) return true;
        PzmDCompHost.ReleaseBind(ref _dcTarget, ref _dcVisual, ref _dcSwap);
        _dcW = 0; _dcH = 0;
        string err;
        if (!DCompHost.BindWindow(this.Handle, w, h, out _dcTarget, out _dcVisual, out _dcSwap, out err)) {
            BindErr = err;
            return false;
        }
        BindErr = "ok";
        _dcW = w; _dcH = h;
        _dstBuf = new int[w * h];
        _xMap = new int[w];
        _yMap = new int[h];
        float srcX, srcY, srcW, srcH;
        double scale;
        ComputeSourceCrop(w, h, out srcX, out srcY, out srcW, out srcH, out scale);
        for (int x = 0; x < w; x++) {
            int sx = (int)(srcX + (x + 0.5) / scale);
            _xMap[x] = sx < 0 ? 0 : (sx > 639 ? 639 : sx);
        }
        for (int y = 0; y < h; y++) {
            int sy = (int)(srcY + (y + 0.5) / scale);
            _yMap[y] = sy < 0 ? 0 : (sy > 399 ? 399 : sy);
        }
        return true;
    }

    private void SwitchToLayeredFallback() {
        UseDComp = false;
        PzmDCompHost.ReleaseBind(ref _dcTarget, ref _dcVisual, ref _dcSwap);
        int ex = GetWindowLong(this.Handle, -20);
        ex = (ex & ~0x00200000) | 0x00080000;
        SetWindowLong(this.Handle, -20, ex);
    }

    public void PushFrame() {
        var f = FrameRef;
        if (f == null || !IsHandleCreated) return;
        int w = ScreenBounds.Width, h = ScreenBounds.Height;
        if (w <= 0 || h <= 0) return;

        if (UseDComp && DCompHost != null && DCompHost.Ready) {
            if (EnsureDCompBuffers(w, h)) {
                var bd = f.LockBits(new Rectangle(0, 0, 640, 400), ImageLockMode.ReadOnly, PixelFormat.Format32bppPArgb);
                try {
                    if (bd.Stride == 640 * 4) {
                        Marshal.Copy(bd.Scan0, _srcBuf, 0, 640 * 400);
                    } else {
                        for (int r = 0; r < 400; r++) Marshal.Copy(IntPtr.Add(bd.Scan0, r * bd.Stride), _srcBuf, r * 640, 640);
                    }
                } finally {
                    f.UnlockBits(bd);
                }
                int prevSy = -1;
                int prevRowOff = 0;
                for (int y = 0; y < h; y++) {
                    int sy = _yMap[y];
                    int rowOff = y * w;
                    if (sy == prevSy) {
                        Array.Copy(_dstBuf, prevRowOff, _dstBuf, rowOff, w);
                    } else {
                        int srcOff = sy * 640;
                        for (int x = 0; x < w; x++) _dstBuf[rowOff + x] = _srcBuf[srcOff + _xMap[x]];
                        prevSy = sy;
                        prevRowOff = rowOff;
                    }
                }
                int hrP = DCompHost.PresentPixels(_dcSwap, _dstBuf, w);
                LastPresentHr = hrP;
                if (hrP >= 0) {
                    PaintCount++;
                    return;
                }
                BindErr = string.Format("pres=0x{0:X8}", hrP);
            }
            SwitchToLayeredFallback();
        }

        if (_fallbackGdi) {
            Invalidate();
            return;
        }
        if (!EnsureDib(w, h)) {
            _fallbackGdi = true;
            try { SetLayeredWindowAttributes(this.Handle, 0, 255, 0x02); } catch {}
            Invalidate();
            return;
        }
        float srcX, srcY, srcW, srcH;
        double scale;
        ComputeSourceCrop(w, h, out srcX, out srcY, out srcW, out srcH, out scale);
        using (var g = Graphics.FromHdc(_memDc)) {
            g.InterpolationMode = InterpolationMode.NearestNeighbor;
            g.PixelOffsetMode = PixelOffsetMode.Half;
            g.CompositingMode = CompositingMode.SourceCopy;
            g.DrawImage(f, new Rectangle(0, 0, w, h), srcX, srcY, srcW, srcH, GraphicsUnit.Pixel);
        }
        IntPtr screenDc = GetDC(IntPtr.Zero);
        try {
            var sz = new WSIZE { cx = w, cy = h };
            var ptSrc = new WPOINT { X = 0, Y = 0 };
            var blend = new BLENDFUNCTION { BlendOp = 0, BlendFlags = 0, SourceConstantAlpha = 255, AlphaFormat = 0 };
            bool ok = UpdateLayeredWindow(this.Handle, screenDc, IntPtr.Zero, ref sz, _memDc, ref ptSrc, 0, ref blend, 0x00000002);
            LastUlwOk = ok;
            LastUlwErr = ok ? 0 : Marshal.GetLastWin32Error();
            if (ok) {
                PaintCount++;
            } else {
                _fallbackGdi = true;
                try { SetLayeredWindowAttributes(this.Handle, 0, 255, 0x02); } catch {}
                Invalidate();
            }
        } finally {
            ReleaseDC(IntPtr.Zero, screenDc);
        }
    }

    protected override void OnPaint(PaintEventArgs e) {
        if (!_fallbackGdi) return;
        PaintCount++;
        var f = FrameRef;
        if (f == null) return;
        int w = ClientSize.Width, h = ClientSize.Height;
        if (w <= 0 || h <= 0) return;
        float srcX, srcY, srcW, srcH;
        double scale;
        ComputeSourceCrop(w, h, out srcX, out srcY, out srcW, out srcH, out scale);

        var g = e.Graphics;
        g.InterpolationMode = InterpolationMode.NearestNeighbor;
        g.PixelOffsetMode = PixelOffsetMode.Half;
        g.CompositingMode = CompositingMode.SourceCopy;
        g.DrawImage(f, new Rectangle(0, 0, w, h), srcX, srcY, srcW, srcH, GraphicsUnit.Pixel);
    }

    protected override void Dispose(bool disposing) {
        PzmDCompHost.ReleaseBind(ref _dcTarget, ref _dcVisual, ref _dcSwap);
        ReleaseDib();
        base.Dispose(disposing);
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
    [DllImport("user32.dll")] public static extern IntPtr GetWindow(IntPtr hWnd, uint uCmd);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassNameW(IntPtr hWnd, System.Text.StringBuilder sb, int maxCount);
    [DllImport("user32.dll")] public static extern bool IsWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
    [DllImport("user32.dll")] public static extern bool ScreenToClient(IntPtr hWnd, ref POINT lpPoint);
    [DllImport("user32.dll", SetLastError=true)] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
    [DllImport("user32.dll")] public static extern int GetWindowLong(IntPtr hWnd, int nIndex);
    [DllImport("user32.dll")] public static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);
    [DllImport("user32.dll")] public static extern bool SetLayeredWindowAttributes(IntPtr hwnd, uint crKey, byte bAlpha, uint dwFlags);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool RedrawWindow(IntPtr hWnd, IntPtr lprcUpdate, IntPtr hrgnUpdate, uint flags);
    [DllImport("user32.dll")] public static extern IntPtr SetProcessDpiAwarenessContext(IntPtr value);
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();

    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X, Y; }

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

        IntPtr workerChild = FindWindowExW(progman, IntPtr.Zero, "WorkerW", null);
        targetParent = progman;
        insertAfter = shellView;
        workerBelow = workerChild;
        modeDesc = (workerChild != IntPtr.Zero) ? "raised-progman-layered" : "progman-direct";
        return true;
    }

    public static bool AttachForm(PzmWallForm form, IntPtr targetParent, IntPtr insertAfter) {
        if (form == null || targetParent == IntPtr.Zero || !IsWindow(targetParent)) return false;
        IntPtr h = form.Handle;
        int style = GetWindowLong(h, -16);
        style = (style & ~unchecked((int)0x80000000)) | 0x40000000 | 0x10000000 | 0x04000000; // WS_CHILD | WS_VISIBLE | WS_CLIPSIBLINGS
        SetWindowLong(h, -16, style);

        int exStyle = GetWindowLong(h, -20);
        exStyle = (exStyle & ~(0x00040000 | 0x00010000 | 0x00080000 | 0x00200000))
                | 0x08000000 | 0x00000080 | 0x00000020
                | (form.UseDComp ? 0x00200000 : 0x00080000);
        SetWindowLong(h, -20, exStyle);

        SetParent(h, targetParent);

        Rectangle sb = form.ScreenBounds;
        POINT pt = new POINT { X = sb.Left, Y = sb.Top };
        ScreenToClient(targetParent, ref pt);
        bool okPos = SetWindowPos(h, insertAfter, pt.X, pt.Y, sb.Width, sb.Height, 0x0010 | 0x0040 | 0x0020);
        ShowWindow(h, 8);
        return okPos;
    }

    public static void PushWorkersBelow(IntPtr progman, IntPtr insertAfterForm) {
        if (progman == IntPtr.Zero || insertAfterForm == IntPtr.Zero || !IsWindow(insertAfterForm)) return;
        IntPtr cur = IntPtr.Zero;
        for (int guard = 0; guard < 16; guard++) {
            cur = FindWindowExW(progman, cur, "WorkerW", null);
            if (cur == IntPtr.Zero) break;
            SetWindowPos(cur, insertAfterForm, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010 | 0x4000);
        }
    }

    public static string DescribeChildren(IntPtr parent) {
        var sb = new System.Text.StringBuilder();
        IntPtr cur = GetWindow(parent, 5); // GW_CHILD
        var cls = new System.Text.StringBuilder(64);
        int idx = 0;
        while (cur != IntPtr.Zero && idx < 16) {
            cls.Clear();
            GetClassNameW(cur, cls, 64);
            RECT r; GetWindowRect(cur, out r);
            int ex = GetWindowLong(cur, -20);
            sb.AppendFormat("#{0}:{1}({2}) vis={3} ex={4:X} [{5},{6},{7}x{8}] | ",
                idx, cur, cls.ToString(), IsWindowVisible(cur), ex, r.Left, r.Top, r.Right - r.Left, r.Bottom - r.Top);
            cur = GetWindow(cur, 2); // GW_HWNDNEXT
            idx++;
        }
        return sb.ToString();
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
        $sd.ModoMilesColgado = ($t.modo_heroe -eq 'miles_colgado')
        $sd.ModoBrasas = ($t.modo_particulas -eq 'brasas_mana')
        $sd.SinLago = [bool]($t.sin_lago)
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

$script:dcomp = New-Object PzmDCompHost
Write-MotorLog "DComp init: ready=$($script:dcomp.Ready) diag=$($script:dcomp.InitDiag)"

$curAfter = $script:desktopAfter
foreach ($scr in [System.Windows.Forms.Screen]::AllScreens) {
    $form = New-Object PzmWallForm($scr.Bounds, $script:dcomp)
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
    [PzmDesktopHost]::PushWorkersBelow($script:desktopParent, $script:forms[-1].Form.Handle)
}

Recargar-Escenas
Write-MotorLog ("Tree t0: " + [PzmDesktopHost]::DescribeChildren($script:desktopParent))

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
        $fItem.Form.PushFrame()
    }
    if ($script:dcomp -and $script:dcomp.Ready) { $script:dcomp.Commit() }
}

Render-MotorFrame 0

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

    if ((($t -eq 12) -or (($t % 24) -eq 0)) -and $script:forms.Count -gt 0) {
        $f0 = $script:forms[0].Form
        $zMal = ($script:desktopAfter -ne [IntPtr]::Zero) -and ([PzmDesktopHost]::GetWindow($script:desktopAfter, 2) -ne $f0.Handle)
        if ((-not [PzmDesktopHost]::IsWindow($script:desktopParent)) -or ([PzmDesktopHost]::GetParent($f0.Handle) -ne $script:desktopParent) -or $zMal) {
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
            [PzmDesktopHost]::PushWorkersBelow($script:desktopParent, $script:forms[-1].Form.Handle)
        }
        if ($t -eq 12) {
            $pc = ($script:forms | ForEach-Object { $_.Form.PaintCount }) -join ','
            $pres = ($script:forms | ForEach-Object { ('0x{0:X}' -f $_.Form.LastPresentHr) }) -join ','
            $bnds = ($script:forms | ForEach-Object { "$($_.Form.UseDComp)/$($_.Form.BindErr)" }) -join ','
            $ulw = ($script:forms | ForEach-Object { "$($_.Form.LastUlwOk)/$($_.Form.LastUlwErr)" }) -join ','
            $cm = if ($script:dcomp) { '0x{0:X}' -f $script:dcomp.LastCommitHr } else { 'none' }
            Write-MotorLog ("Tree t12: paints=[$pc] dc=[$bnds] pres=[$pres] cm=$cm ulw=[$ulw] " + [PzmDesktopHost]::DescribeChildren($script:desktopParent))
        }
    }

    Render-MotorFrame $t
})

$timer.Start()
[System.Windows.Forms.Application]::Run()
