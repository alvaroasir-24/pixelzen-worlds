param(
    [string]$Tema = 'fittoa',
    [int]$Monitores = 2,
    [ValidateSet('real', '90m', 'demo', 'fija')]
    [string]$Modo = '90m',
    [double]$Hora = 21.5,
    [int]$Fps = 8,
    [string]$FondoPrincipal = 'principal',
    [string]$FondoSecundario = 'secundaria',
    [string]$Clima = 'normal',
    [string]$TemaSecundario = '',
    [int]$RotacionMinutos = 0,
    [bool]$PausaJuego = $true,
    [bool]$AudioReactivo = $true,
    [bool]$Hotkeys = $true
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
    public string ModoHeroe = "";
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
        if (!File.Exists(path) && !string.IsNullOrEmpty(path)) {
            string norm = path.Replace('/', '\\');
            int idx = norm.IndexOf(@"\temas\", StringComparison.OrdinalIgnoreCase);
            if (idx >= 0) {
                string fb = Path.Combine(@"C:\Users\david\.gemini\antigravity-cli\brain\8747b389-799a-4632-897a-f7f55a4233c0\scratch\out_root\windows\lively\temas", norm.Substring(idx + 7));
                if (File.Exists(fb)) path = fb;
            }
        }
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
    public string ClimaMode = "normal";
    public string TemaId = "fittoa";
    public bool AudioReactivo = true;
    public double AudioBoost = 0.0;
    public string EventoTipo = "";
    public int EventoInicioTick = -999;
    public int EventoDuracion = 96;

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

    void PintaTormentaStranger(Graphics g, int t, double nf, string modo) {
        double pulse = 0.04 + 0.05 * Osc(t, 0.08, 0.5);
        Px(g, Color.FromArgb(255, 30, 60), pulse * (0.6 + 0.4 * nf), 0, 0, 640, 276);
        int slot = t / 44;
        int age = t % 44;
        if (age >= 6) return;
        double alpha = (1.0 - age / 6.0) * (age % 2 == 0 ? 1.0 : 0.55);
        Px(g, Color.FromArgb(255, 42, 72), alpha * 0.14, 0, 0, 640, 272);
        int[] anchors = modo == "stranger_demogorgon"
            ? new int[] { 385, 428, 472, 340 }
            : (modo == "stranger_reloj"
                ? new int[] { 276, 364, 240, 400 }
                : new int[] { 132, 174, 212, 154 });
        int lx = anchors[slot % anchors.Length];
        int yIni = modo == "stranger_azotamentes" ? 54 : 26;
        Color cBoltOut = Color.FromArgb(255, 40, 72);
        Color cBoltCore = Color.FromArgb(255, 216, 226);
        Color cBoltBranch = Color.FromArgb(255, 52, 84);
        for (int i = 0; i < 120; i += 2) {
            int jit = Math.Sin(slot * 7.3 + i * 0.47) > 0.25 ? 2 : (Math.Cos(slot * 3.1 + i * 0.61) < -0.25 ? -2 : 0);
            lx += jit;
            int ly = yIni + i;
            if (ly > 268) break;
            Px(g, cBoltOut, alpha * 0.72, lx - 1, ly, 3, 2);
            Px(g, cBoltCore, alpha, lx, ly, 1, 2);
            if (i == 44 || i == 82) {
                int dir = (slot + i) % 2 == 0 ? 1 : -1;
                for (int b = 0; b < 22; b += 2) {
                    Px(g, cBoltBranch, alpha * 0.68, lx + dir * b, ly + b, 2, 2);
                }
            }
        }
    }

    void PintaStrangerPrincipal(Graphics g, int t, double nf) {
        Color cSpore = Color.FromArgb(255, 48, 76);
        Color cShadow = Color.FromArgb(42, 8, 20);
        for (int i = 0; i < 12; i++) {
            double ang = t * 0.07 + i * 0.52;
            int wx = 168 + (int)Math.Round(Math.Cos(ang) * (24 + (i % 4) * 14));
            int wy = 148 + (int)Math.Round(Math.Sin(ang * 0.8) * 32.0 - ((t * 0.4 + i * 5) % 18.0));
            Px(g, (i % 2 == 0) ? cSpore : cShadow, 0.48 + 0.35 * nf, wx, wy, 2, 2);
        }

        int[] oxs = new int[] { 0, -42, -84, -126 };
        int[] bys = new int[] { 344, 338, 346, 340 };
        Color[] coats = new Color[] {
            Color.FromArgb(44, 92, 168), Color.FromArgb(212, 60, 68),
            Color.FromArgb(226, 136, 50), Color.FromArgb(62, 138, 92)
        };
        Color[] hats = new Color[] {
            Color.FromArgb(230, 66, 66), Color.FromArgb(27, 32, 48),
            Color.FromArgb(38, 56, 38), Color.FromArgb(84, 56, 132)
        };
        Color cTire = Color.FromArgb(29, 32, 44);
        Color cSpoke = Color.FromArgb(168, 180, 204);
        Color cFrame = Color.FromArgb(58, 64, 82);
        Color cHandle = Color.FromArgb(124, 132, 152);
        Color cPack = Color.FromArgb(24, 26, 36);
        Color cSkin = Color.FromArgb(222, 178, 146);
        Color cBeam = Color.FromArgb(255, 240, 184);
        Color cLamp = Color.FromArgb(255, 248, 212);

        double leadX = ((t * 1.65) % 860.0) - 70.0;
        int spoke = (t / 2) % 2;
        for (int idx = 0; idx < 4; idx++) {
            int cx = (int)Math.Round(leadX + oxs[idx]);
            if (cx < -35 || cx > 665) continue;
            int by = bys[idx];
            int bob = Math.Sin(t * 0.45 + idx * 1.4) > 0.35 ? -1 : 0;
            for (int w = 0; w < 2; w++) {
                int wx = w == 0 ? cx - 6 : cx + 6;
                Px(g, cTire, 0.95, wx - 4, by - 7, 8, 2);
                Px(g, cTire, 0.95, wx - 4, by - 1, 8, 2);
                Px(g, cTire, 0.95, wx - 4, by - 6, 2, 6);
                Px(g, cTire, 0.95, wx + 2, by - 6, 2, 6);
                Px(g, cSpoke, 0.90, wx + (spoke != 0 ? 0 : -1), by - 4, 1, 1);
                Px(g, cSpoke, 0.85, wx + (spoke != 0 ? 1 : 0), by - 5, 1, 1);
            }
            Px(g, cFrame, 0.95, cx - 6, by - 6, 13, 1);
            Px(g, cHandle, 0.95, cx + 4, by - 10, 1, 4);
            Px(g, coats[idx], 0.96, cx - 2, by - 14 + bob, 5, 6);
            Px(g, cPack, 0.96, cx - 3, by - 13 + bob, 2, 4);
            Px(g, cSkin, 0.96, cx - 1, by - 16 + bob, 3, 2);
            Px(g, hats[idx], 0.96, cx - 2, by - 18 + bob, 5, 2);
            for (int i = 1; i <= 22; i += 2) {
                int rad = Math.Max(1, i / 5);
                double opBeam = Math.Max(0.04, (0.34 - i * 0.013) * (0.45 + 0.55 * nf));
                Px(g, cBeam, opBeam, cx + 7 + i, by - 9 - rad + 1, 2, rad * 2 - 1);
            }
            Px(g, cLamp, 0.95, cx + 6, by - 9, 2, 1);
        }
    }

    void PintaStrangerDemogorgon(Graphics g, int t, double nf) {
        double mawP = 0.45 + 0.55 * Osc(t, 0.14, 0.2);
        Px(g, Color.FromArgb(255, 36, 72), 0.22 * mawP, 412, 314, 13, 13);
        Px(g, Color.FromArgb(255, 200, 212), 0.65 * mawP, 417, 319, 3, 3);
        Color cSpA = Color.FromArgb(255, 58, 94);
        Color cSpB = Color.FromArgb(255, 208, 216);
        for (int i = 0; i < 10; i++) {
            int sx = 392 + ((i * 19 + (int)Math.Round(t * 0.5)) % 56);
            int sy = 342 - ((int)(t * 0.55 + i * 9) % 44);
            Px(g, (i % 2 == 0) ? cSpA : cSpB, 0.55, sx, sy, 1, 1);
        }
        Color[] cols = new Color[] {
            Color.FromArgb(255, 46, 106), Color.FromArgb(72, 232, 255),
            Color.FromArgb(255, 212, 72), Color.FromArgb(82, 255, 136)
        };
        int active = (t / 6) % 8;
        for (int i = 0; i < 8; i++) {
            int lx = 78 + i * 10;
            int ly = 292 + (i % 2) * 5;
            bool isLit = (i == active) || (((t / 14 + i) % 5) == 0);
            double op = (isLit ? 0.95 : 0.30) * (0.55 + 0.45 * nf);
            Color col = cols[i % 4];
            Px(g, col, 0.24 * op, lx - 1, ly - 1, 4, 3);
            Px(g, col, op, lx, ly, 2, 1);
        }
    }

    void PintaStrangerReloj(Graphics g, int t, double nf) {
        double ang = 0.14 * Math.Sin(t * 0.14);
        int px0 = 320, py0 = 232, len = 56;
        Color cRod = Color.FromArgb(230, 188, 88);
        Color cBob = Color.FromArgb(242, 202, 98);
        Color cHi = Color.FromArgb(255, 244, 190);
        for (int r = 0; r <= len; r += 2) {
            int rx = (int)Math.Round(px0 + Math.Sin(ang) * r);
            int ry = (int)Math.Round(py0 + Math.Cos(ang) * r);
            Px(g, cRod, 0.96, rx, ry, 1, 2);
        }
        int bx = (int)Math.Round(px0 + Math.Sin(ang) * len);
        int by = (int)Math.Round(py0 + Math.Cos(ang) * len);
        Px(g, cBob, 0.98, bx - 3, by - 3, 7, 7);
        Px(g, cHi, 0.90, bx - 1, by - 1, 3, 3);
        Color cRift = Color.FromArgb(255, 72, 104);
        for (int k = 0; k < 6; k++) {
            int cy = 172 + ((t * 2 + k * 33) % 180);
            int cx = 320 + (int)Math.Round(Math.Sin(cy * 0.15 + t * 0.08) * 14);
            Px(g, cRift, 0.55 + 0.35 * nf, cx, cy, 2, 2);
        }
    }

    void PintaDemonRengoku(Graphics g, int t, double nf) {
        double imp = Math.Pow(Math.Max(0, Math.Sin(t * 0.28)), 4);
        int clashTick = t % 24;
        double clash = clashTick < 5 ? 1.0 - clashTick / 5.0 : 0.0;
        double env = 0.65 + 0.35 * nf;

        Color cFlame0 = Color.FromArgb(255, 42, 24);
        Color cFlame1 = Color.FromArgb(255, 126, 36);
        Color cFlame2 = Color.FromArgb(255, 216, 76);
        Color cFlame3 = Color.FromArgb(255, 248, 200);
        Color cAkaza0 = Color.FromArgb(56, 216, 255);
        Color cAkaza1 = Color.FromArgb(146, 240, 255);
        Color cAkaza2 = Color.FromArgb(216, 56, 92);

        Px(g, Color.FromArgb(255, 88, 32), (0.07 + 0.11 * imp) * env, 286, 266, 94, 46);
        Px(g, cAkaza0, (0.07 + 0.11 * imp) * env, 404, 268, 96, 46);
        if (clash > 0.05) {
            int rC = (int)Math.Round(14 + (1.0 - clash) * 18);
            Px(g, Color.FromArgb(255, 232, 160), 0.16 * clash * env, 418 - rC, 284 - (int)Math.Round(rC * 0.7), rC * 2, (int)Math.Round(rC * 1.4));
        }

        for (int i = 0; i < 8; i++) {
            int fx = 306 + i * 3;
            double wave = Math.Sin(t * 0.55 + i * 0.85);
            int fy = 287 + (int)Math.Round(i * 0.3 + wave * 1.8);
            int fh = 5 + (((int)(t * 0.6) + i * 3) % 5);
            Px(g, cFlame0, 0.82, fx, fy + fh - 3, 2, 3);
            Px(g, cFlame1, 0.88, fx, fy + 2, 2, 3);
            Px(g, cFlame2, 0.90, fx, fy, 2, 2);
        }
        for (int k = 0; k < 6; k++) {
            double lift = ((t * 1.6 + k * 7) % 18.0);
            int ax = 324 + ((k * 7) % 21) + (int)Math.Round(Math.Sin(t * 0.4 + k) * 2);
            int ay = 294 - (int)Math.Round(lift);
            Px(g, (k % 2 == 0) ? cFlame2 : cFlame1, Math.Max(0.15, (1.0 - lift / 18.0) * 0.85), ax, ay, 2, 2);
        }
        int bPos = (t * 2) % 20;
        Px(g, cFlame3, 0.95, 342 + bPos, 292 - bPos / 4, 3, 1);

        for (int step = 0; step < 19; step++) {
            double u = step / 18.0;
            double pulseU = ((t * 0.11 + u * 2.2) % 1.0);
            int bx = (int)Math.Round(356 + u * 64);
            int by = (int)Math.Round(288 - Math.Sin(u * Math.PI * 0.85) * 18 + Math.Sin(u * 9.0 - t * 0.65) * 3.2);
            int rad = 3 + ((step + (int)(t * 0.5)) % 3);
            Px(g, cFlame0, 0.42, bx - rad - 1, by - rad - 1, (rad + 1) * 2, (rad + 1) * 2);
            Px(g, cFlame1, 0.84, bx - rad, by - rad, rad * 2, rad * 2);
            Px(g, pulseU > 0.62 ? cFlame3 : cFlame2, 0.94, bx - 1, by - 1, 3, 3);
            double angR = t * 0.5 + step * 0.8;
            Px(g, Color.FromArgb(255, 232, 136), 0.80, bx + (int)Math.Round(Math.Cos(angR) * 4), by + (int)Math.Round(Math.Sin(angR) * 6), 2, 2);
        }
        int jaw = Math.Sin(t * 0.45) > 0 ? 1 : 0;
        Px(g, cFlame3, 0.96, 417, 281 - jaw, 6, 3);
        Px(g, cFlame1, 0.92, 421, 278 - jaw, 5, 2);
        Px(g, cFlame0, 0.90, 421, 286 + jaw, 5, 2);

        double rot = t * 0.065;
        for (int p = 0; p < 12; p++) {
            double ang = rot + (p * Math.PI * 2.0) / 12.0;
            double cA = Math.Cos(ang), sA = Math.Sin(ang);
            for (int r = 14; r <= 42; r += 4) {
                int rx = (int)Math.Round(456 + cA * r);
                int ry = (int)Math.Round(312 + sA * (r * 0.18));
                bool esPunta = r >= 36;
                Px(g, esPunta ? Color.White : (r >= 26 ? cAkaza1 : cAkaza0), esPunta ? 0.95 : 0.78, rx, ry, esPunta ? 2 : 1, 1);
            }
        }
        Px(g, cFlame2, 0.95, 450, 284, 1, 1);
        Px(g, cFlame2, 0.95, 454, 284, 1, 1);
        for (int k = 0; k < 4; k++) {
            double prog = ((t * 0.13 + k * 0.25) % 1.0);
            int ax = (int)Math.Round(446 - prog * 28);
            int ay = (int)Math.Round(288 + (((k % 2 == 0) ? -1 : 1) * 5) + Math.Sin(t * 0.4 + k) * 2);
            Px(g, cAkaza0, 0.85, ax, ay - 3, 4, 7);
            Px(g, cAkaza2, 0.72, ax + 2, ay - 2, 3, 5);
            Px(g, Color.White, 0.95, ax - 1, ay - 1, 2, 3);
        }

        for (int rIdx = 0; rIdx < 2; rIdx++) {
            int rad = 4 + ((t * 2 + rIdx * 7) % 14);
            double opRing = Math.Max(0.15, (1.0 - (rad - 4) / 14.0) * 0.9);
            for (int i = 0; i < 16; i++) {
                double a = (i * Math.PI * 2.0) / 16.0 + t * 0.08;
                int sx = (int)Math.Round(418 + Math.Cos(a) * rad);
                int sy = (int)Math.Round(284 + Math.Sin(a) * rad * 0.75);
                Px(g, sx < 418 ? cFlame2 : cAkaza0, opRing, sx, sy, 2, 1);
            }
        }
        Color cBoltY = Color.FromArgb(255, 232, 152);
        Color cBoltC = Color.FromArgb(120, 236, 255);
        for (int b = 0; b < 6; b++) {
            if ((t + b) % 3 == 0) continue;
            double ba = t * 0.37 + b * 1.05;
            int bl = 7 + ((t * 3 + b * 5) % 10);
            Color colB = (b % 2 == 0) ? cBoltY : cBoltC;
            for (int s = 2; s <= bl; s += 2) {
                int jx = (int)Math.Round(Math.Sin(s + t + b) * 1.4);
                Px(g, colB, 0.88, 418 + (int)Math.Round(Math.Cos(ba) * s) + jx, 284 + (int)Math.Round(Math.Sin(ba) * s * 0.8), 1, 1);
            }
        }
        if (clash > 0.2) Px(g, Color.White, 0.98 * clash, 416, 282, 5, 5);

        double fPulse = 0.7 + 0.3 * Osc(t, 0.22, 0.4);
        Px(g, Color.FromArgb(255, 132, 56), 0.22 * fPulse * env, 141, 222, 14, 9);
        for (int i = 1; i <= 34; i += 2) {
            int rh = 1 + i / 6;
            Px(g, cBoltY, Math.Max(0.03, (0.36 - i * 0.009) * fPulse * env), 225 + i, 238 - rh, 2, rh * 2);
        }
    }

    void PintaDemonTokito(Graphics g, int t, double nf) {
        double env = 0.65 + 0.35 * nf;
        Color cMist0 = Color.FromArgb(84, 232, 204);
        Color cMist1 = Color.FromArgb(184, 255, 244);
        Color cMist2 = Color.FromArgb(232, 255, 252);
        Color cSea = Color.FromArgb(40, 152, 168);
        Color cGyPink = Color.FromArgb(255, 72, 120);

        for (int i = 0; i < 6; i++) {
            int span = 350;
            int bx = 185 + (((int)Math.Round(t * (1.2 + (i % 3) * 0.5)) + i * 64) % span);
            int by = 288 + (i % 3) * 11 + (int)Math.Round(Math.Sin(t * 0.12 + i) * 2);
            int bw = 28 + (i % 3) * 14;
            Px(g, cMist0, 0.16 * env, bx, by, bw, 3);
            Px(g, cMist1, 0.22 * env, bx + 6, by + 1, (int)Math.Round(bw * 0.6), 1);
        }

        Color cHair = Color.FromArgb(116, 240, 220);
        for (int h = 0; h < 5; h++) {
            int hx = 259 + h * 3;
            int hy = 283 + h + (int)Math.Round(Math.Sin(t * 0.45 + h) * 1.4);
            Px(g, h > 2 ? cMist2 : cHair, 0.85, hx, hy, 2, 2);
        }
        int bladeS = (t * 2) % 18;
        Px(g, cMist2, 0.95, 287 + bladeS, 285 - bladeS / 4, 3, 1);

        for (int a = 0; a < 3; a++) {
            double prog = ((t * 0.10 + a * 0.33) % 1.0);
            int sx = (int)Math.Round(304 + prog * 144);
            int sy = (int)Math.Round(284 + Math.Sin(prog * Math.PI * 2 + a) * 9);
            for (int dy = -6; dy <= 6; dy += 2) {
                int arch = (dy * dy) / 7;
                Px(g, cMist0, 0.72, sx - arch, sy + dy, 3, 2);
                if (Math.Abs(dy) <= 3) Px(g, cMist2, 0.92, sx - arch + 1, sy + dy, 2, 1);
            }
        }

        int flashTick = t % 28;
        if (flashTick < 9) {
            double fAl = 1.0 - flashTick / 9.0;
            Px(g, cMist0, 0.18 * fAl * env, 424, 260, 56, 42);
            Color cFlash = Color.FromArgb(116, 248, 232);
            for (int d = -14; d <= 14; d += 2) {
                Px(g, cFlash, 0.86 * fAl, 444 + d, 280 + (int)Math.Round(d * 0.65), 2, 2);
                Px(g, Color.White, 0.95 * fAl, 444 + d, 280 - (int)Math.Round(d * 0.65), 2, 2);
            }
        }

        for (int sIdx = 0; sIdx < 2; sIdx++) {
            int side = sIdx == 0 ? -1 : 1;
            for (int seg = 0; seg < 12; seg++) {
                double u = seg / 11.0;
                double wave = Math.Sin(t * 0.42 + u * 4.5 + side) * (2.5 + u * 3.5);
                int tx = (int)Math.Round(468 + side * (13 + seg * 2.5));
                int ty = (int)Math.Round(294 - Math.Sin(u * 3.6) * 14 - u * 9 + wave);
                int rt = u < 0.5 ? 2 : 1;
                Px(g, cSea, 0.75, tx - rt, ty - rt, rt * 2 + 1, rt * 2 + 1);
                Px(g, cMist1, 0.86, tx, ty, rt, rt);
            }
            if ((t + (side > 0 ? 1 : 0)) % 2 == 0) {
                int sxp = 468 + side * (36 + (t % 5));
                int syp = 266 + (int)Math.Round(Math.Cos(t * 0.5 + side) * 4);
                Px(g, cMist2, 0.88, sxp, syp, 2, 2);
            }
        }
        Px(g, cGyPink, 0.92, 467, 270, 2, 2);
        Px(g, Color.FromArgb(255, 216, 88), 0.90, 467, 275, 2, 1);

        for (int j = 0; j < 3; j++) {
            double gp = ((t * 0.12 + j * 0.33) % 1.0);
            int gx = (int)Math.Round(452 - gp * 60);
            int gy = (int)Math.Round(278 + (j - 1) * 5 + Math.Sin(t * 0.5 + j) * 2);
            Px(g, cMist0, 0.86, gx, gy, 5, 1);
            Px(g, cGyPink, 0.80, gx + 4, gy, 2, 1);
        }
        if (t % 3 != 0) {
            Px(g, Color.White, 0.90, 391, 279, 3, 3);
            Px(g, Color.FromArgb(255, 100, 148), 0.80, 394 + (t % 4) - 2, 275 + ((t * 2) % 6), 2, 2);
        }
    }

    void PintaDemonGlicinias(Graphics g, int t, double nf) {
        double env = 0.65 + 0.35 * nf;
        Color[] wCols = new Color[] {
            Color.FromArgb(200, 132, 255), Color.FromArgb(240, 216, 255),
            Color.FromArgb(146, 72, 232), Color.FromArgb(230, 184, 255)
        };
        for (int i = 0; i < 20; i++) {
            double speedY = 0.45 + (i % 4) * 0.18;
            double speedX = 0.25 + (i % 3) * 0.12;
            int py = 116 + (((int)Math.Round(t * speedY) + i * 19) % 218);
            int px0 = 36 + (((int)Math.Round(t * speedX + Math.Sin(t * 0.08 + i) * 14) + i * 31) % 568);
            bool horiz = ((t / 5 + i) % 2) == 0;
            Px(g, wCols[i % 4], 0.82 * env, px0, py, horiz ? 2 : 1, horiz ? 1 : 2);
        }
        Color cGlow = Color.FromArgb(240, 216, 255);
        for (int idxG = 0; idxG < 10; idxG++) {
            int gx = idxG < 4 ? (52 + idxG * 44) : (idxG < 8 ? (418 + (idxG - 4) * 44) : (276 + (idxG - 8) * 86));
            int gy = idxG < 8 ? (136 + (idxG % 3) * 14) : 150;
            double op = (0.35 + 0.65 * Osc(t, 0.16, idxG * 1.3)) * env;
            Px(g, cGlow, op, gx, gy, 2, 2);
        }

        double pulseF = 0.72 + 0.28 * Osc(t, 0.24, 0.7);
        Px(g, Color.FromArgb(255, 120, 40), 0.16 * pulseF * env, 300, 266, 50, 24);
        Color cB0 = Color.FromArgb(255, 56, 32);
        Color cB1 = Color.FromArgb(255, 148, 40);
        Color cB2 = Color.FromArgb(255, 244, 184);
        for (int k = 0; k < 9; k++) {
            int kx = 307 + k * 4;
            int kyBase = 285 - (k * 4 + 13) / 5;
            int fh = 3 + (((int)(t * 0.7) + k * 3) % 7);
            int sway = (int)Math.Round(Math.Sin(t * 0.5 + k * 0.9) * 1.2);
            Px(g, cB0, 0.78, kx + sway, kyBase - fh, 2, 3);
            Px(g, cB1, 0.88, kx, kyBase - Math.Max(2, fh - 2), 2, 3);
            Px(g, cB2, 0.95, kx, kyBase - 1, 2, 2);
        }
        Color cEmberG = Color.FromArgb(255, 232, 136);
        Color cEmberO = Color.FromArgb(255, 152, 56);
        for (int e = 0; e < 5; e++) {
            double rise = ((t * 1.2 + e * 9) % 34.0);
            int ex = 310 + ((e * 11) % 30) + (int)Math.Round(Math.Sin(t * 0.2 + e * 1.7) * 4);
            int ey = 280 - (int)Math.Round(rise);
            Px(g, (e % 2 == 0) ? cEmberG : cEmberO, Math.Max(0.1, (1.0 - rise / 34.0) * 0.88), ex, ey, 1, 2);
        }
    }

    void PintaNarutoBaryon(Graphics g, int t, double nf) {
        double env = 0.68 + 0.32 * nf;
        double kPulse = 0.5 + 0.5 * Math.Sin(t * 0.26);
        Color cRed = Color.FromArgb(255, 44, 24);
        Color cOrg = Color.FromArgb(255, 148, 48);
        Color cOrgB = Color.FromArgb(255, 124, 44);
        Color cGold = Color.FromArgb(255, 224, 136);
        Color cCream = Color.FromArgb(255, 240, 168);
        Color cCore = Color.FromArgb(255, 246, 220);
        Color cMag = Color.FromArgb(192, 68, 255);
        Color cMagL = Color.FromArgb(255, 184, 255);
        Color cMagD = Color.FromArgb(136, 40, 200);

        int[] eyes = new int[] { 121, 154 };
        for (int ei = 0; ei < eyes.Length; ei++) {
            int ex = eyes[ei];
            Px(g, cRed, 0.48 * kPulse * env, ex - 4, 173, 8, 5);
            Px(g, cOrg, 0.88, ex - 2, 174, 5, 3);
            Px(g, cCream, 0.96, ex, 174, 2, 2);
        }
        Color cBreath = Color.FromArgb(255, 90, 36);
        for (int w = 0; w < 4; w++) {
            int wy = 192 + w * 4 - ((t + w * 2) % 6);
            Px(g, cBreath, 0.36 * env, 130 + ((w * 7) % 16), wy, 2, 3);
        }

        Color cTip = Color.FromArgb(255, 208, 104);
        Color cTailR = Color.FromArgb(255, 60, 36);
        for (int k = 0; k < 9; k++) {
            double baseAng = -2.42 + k * 0.24;
            int len = 64 + (k % 3) * 18;
            for (int s = 2; s < 10; s++) {
                double u = s / 10.0;
                double sway = Math.Sin(t * 0.34 + k * 0.9 + u * 3.1) * (4.0 + u * 8.0);
                int tx = (int)Math.Round(192 + Math.Cos(baseAng) * (len * u) + sway * 0.45);
                int ty = (int)Math.Round(314 + Math.Sin(baseAng) * (len * u) + sway * 0.3);
                if (tx < 48 || tx > 258 || ty < 178 || ty > 342) continue;
                bool tip = s > 7;
                Color tc = tip ? cTip : (s % 2 == 0 ? cTailR : cOrgB);
                Px(g, tc, (0.28 + 0.36 * (1.0 - u)) * env, tx, ty, tip ? 2 : 3, 2);
            }
        }

        Color cOrgM = Color.FromArgb(255, 156, 56);
        for (int p = 0; p < 7; p++) {
            double rise = ((t * 1.7 + p * 5) % 28.0);
            int ax = 188 + ((p * 5) % 20) + (int)Math.Round(Math.Sin(t * 0.45 + p) * 2.0);
            int ay = 340 - (int)Math.Round(rise);
            Px(g, rise > 18 ? cRed : cOrgM, Math.Max(0.12, (1.0 - rise / 28.0) * 0.78), ax, ay, 2, 2);
        }
        Px(g, cGold, 0.85, 188, 300 + (t % 2), 1, 2);
        Px(g, cGold, 0.85, 204, 300 + ((t + 1) % 2), 1, 2);

        double rPulse = 0.65 + 0.35 * Math.Sin(t * 0.65);
        Px(g, Color.FromArgb(255, 64, 32), 0.35 * rPulse, 214, 314, 13, 13);
        Px(g, Color.FromArgb(255, 158, 60), 0.80, 217, 317, 7, 7);
        Px(g, cCore, 0.96, 219, 319, 3, 3);
        Color cOrbY = Color.FromArgb(255, 232, 152);
        Color cOrbR = Color.FromArgb(255, 76, 40);
        for (int r = 0; r < 4; r++) {
            double ra = t * 0.55 + r * (Math.PI / 2.0);
            int rx = 220 + (int)Math.Round(Math.Cos(ra) * 5.2);
            int ry = 320 + (int)Math.Round(Math.Sin(ra) * 5.2);
            Px(g, r % 2 == 0 ? cOrbY : cOrbR, 0.92, rx, ry, 2, 2);
        }

        if (t % 4 != 0) {
            int cxm = 258 + ((t * 7) % 48);
            int cym = 304 - (int)Math.Round((cxm - 258) * 0.4) + (int)Math.Round(Math.Sin(t * 0.9) * 5.0);
            Px(g, Color.FromArgb(255, 216, 120), 0.90, cxm, cym, 3, 1);
            Px(g, Color.FromArgb(255, 72, 40), 0.72, cxm - 2, cym + 1, 2, 1);
        }

        int[,] cubos = new int[,] { { 322, 280, 7 }, { 290, 294, 5 }, { 346, 266, 4 } };
        for (int i = 0; i < 3; i++) {
            int bob = (int)Math.Round(Math.Sin(t * 0.24 + i * 2.1) * 3.0);
            int cx = cubos[i, 0];
            int cy = cubos[i, 1] + bob;
            int sz = cubos[i, 2];
            bool flash = ((t + i * 11) % 36) < 4;
            Px(g, flash ? cMagL : cMag, (flash ? 0.78 : 0.46) * env, cx - sz, cy - sz, sz * 2, 1);
            Px(g, cMagD, 0.36 * env, cx - sz, cy + sz - 1, sz * 2, 1);
        }

        Color cWheelY = Color.FromArgb(255, 232, 120);
        for (int s = 0; s < 8; s++) {
            double wa = t * 0.14 + (s * Math.PI) / 4.0;
            int wx = (int)Math.Round(394 + Math.Cos(wa) * 23.0);
            int wy = (int)Math.Round(282 + Math.Sin(wa) * 23.0);
            Px(g, s % 2 == 0 ? cWheelY : Color.White, 0.75 * env, wx, wy, 2, 2);
        }
        Px(g, Color.FromArgb(200, 72, 255), 0.42 * kPulse * env, 387, 308, 5, 3);
    }

    void PintaNarutoKonoha(Graphics g, int t, double nf) {
        double env = 0.60 + 0.40 * nf;
        int flagBob = (int)Math.Round(Math.Sin(t * 0.35) * 1.2);
        Px(g, Color.FromArgb(216, 64, 48), 0.85, 220, 224 + flagBob, 5, 2);
        Px(g, Color.FromArgb(248, 232, 200), 0.65 * env, 217, 228, 3, 1);

        int sway = (int)Math.Round(Math.Sin(t * 0.22) * 1.1);
        Color cLant = Color.FromArgb(255, 82, 50);
        Color cLantG = Color.FromArgb(255, 232, 160);
        int[] lxs = new int[] { 46, 66, 88 };
        for (int i = 0; i < lxs.Length; i++) {
            Px(g, cLant, 0.75 * env, lxs[i] + sway, 255, 3, 4);
            Px(g, cLantG, 0.50 * env, lxs[i] + sway, 256, 1, 2);
        }
        Color cSteam = Color.FromArgb(240, 244, 248);
        for (int v = 0; v < 4; v++) {
            double vr = ((t * 1.1 + v * 6) % 20.0);
            Px(g, cSteam, Math.Max(0.08, (1.0 - vr / 20.0) * 0.42), 66 + (int)Math.Round(Math.Sin(t * 0.2 + v) * 2.0), 248 - (int)Math.Round(vr), 2, 2);
        }

        int cloakW = (int)Math.Round(Math.Sin(t * 0.30) * 1.4);
        Px(g, Color.FromArgb(255, 120, 40), 0.82, 338 + cloakW, 265, 3, 4);
        Px(g, Color.FromArgb(255, 244, 228), 0.78, 344 + cloakW, 261, 3, 3);
        Px(g, Color.FromArgb(56, 48, 88), 0.80, 372 - cloakW, 263, 3, 5);
        if (nf > 0.3) Px(g, Color.FromArgb(200, 112, 255), 0.70 * env, 368, 256, 1, 1);

        Color cLeafD = Color.FromArgb(116, 208, 92);
        Color cLeafS = Color.FromArgb(232, 152, 68);
        Color cLeafN = Color.FromArgb(76, 168, 104);
        for (int i = 0; i < 7; i++) {
            int lx = 36 + (((int)Math.Round(t * (1.3 + (i % 3) * 0.45)) + i * 59) % 404);
            int ly = 135 + (i % 4) * 32 + (int)Math.Round(Math.Sin(t * 0.18 + i * 1.4) * 7.0);
            Color lCol = nf > 0.55 ? cLeafN : (i % 2 == 0 ? cLeafD : cLeafS);
            Px(g, lCol, 0.72, lx, ly, 2, 2);
        }

        Color cWatN = Color.FromArgb(152, 200, 255);
        Color cWatD = Color.FromArgb(255, 240, 184);
        for (int r = 0; r < 10; r++) {
            if ((t + r) % 3 == 0) continue;
            int rx = 44 + ((r * 39 + t * 2) % 390);
            int ry = 287 + (r % 5) * 9;
            Px(g, nf > 0.55 ? cWatN : cWatD, 0.42 * env, rx, ry, 4 + (r % 3) * 2, 1);
        }
    }

    void PintaNarutoValle(Graphics g, int t, double nf) {
        double env = 0.65 + 0.35 * nf;
        Color cFoam = Color.FromArgb(184, 238, 255);
        Color cMist = Color.FromArgb(232, 251, 255);
        Color cRas = Color.FromArgb(72, 196, 255);
        Color cRasC = Color.FromArgb(216, 248, 255);
        Color cRasR = Color.FromArgb(128, 228, 255);
        Color cChi = Color.FromArgb(168, 212, 255);
        Color cChiP = Color.FromArgb(184, 176, 255);

        for (int l = 0; l < 6; l++) {
            int wx = 250 + l * 13;
            int off = (t * 4 + l * 21) % 120;
            for (int k = 0; k < 3; k++) {
                int wy = 154 + ((off + k * 42) % 120);
                Px(g, k == 0 ? Color.White : cFoam, 0.62 * env, wx, wy, 2, 6);
            }
        }
        for (int m = 0; m < 8; m++) {
            int mx = 242 + m * 11 + (int)Math.Round(Math.Sin(t * 0.25 + m) * 2.0);
            int my = 275 + ((t + m * 3) % 5);
            Px(g, cMist, 0.52 * env, mx, my, 5, 3);
        }

        double clash = 0.6 + 0.4 * Math.Sin(t * 0.6);
        Px(g, cRas, 0.32 * clash, 271, 242, 12, 12);
        Px(g, cRasC, 0.90, 275, 246, 5, 5);
        for (int s = 0; s < 4; s++) {
            double sa = t * 0.65 + s * (Math.PI / 2.0);
            Px(g, cRasR, 0.92, 277 + (int)Math.Round(Math.Cos(sa) * 4.0), 248 + (int)Math.Round(Math.Sin(sa) * 4.0), 2, 2);
        }

        Px(g, cChi, 0.32 * clash, 285, 241, 14, 14);
        for (int b = 0; b < 5; b++) {
            if ((t + b) % 3 == 0) continue;
            double ba = t * 0.48 + b * 1.25;
            int bl = 5 + ((t * 2 + b * 3) % 8);
            for (int d = 2; d <= bl; d += 2) {
                int j = (int)Math.Round(Math.Sin(d + t + b) * 1.4);
                Px(g, b % 2 == 0 ? Color.White : cChiP, 0.92, 291 + (int)Math.Round(Math.Cos(ba) * d) + j, 248 + (int)Math.Round(Math.Sin(ba) * d), 1, 1);
            }
        }

        Px(g, Color.White, 0.96 * clash, 282, 246, 5, 5);
        int ringR = 5 + ((t * 2) % 20);
        double ringAl = Math.Max(0.08, (1.0 - (ringR - 5) / 20.0) * 0.72);
        Color cRingB = Color.FromArgb(136, 232, 255);
        for (int a = 0; a < 12; a++) {
            double ang = (a * Math.PI * 2.0) / 12.0 + t * 0.1;
            Px(g, a % 2 == 0 ? cRingB : Color.White, ringAl, 284 + (int)Math.Round(Math.Cos(ang) * ringR), 248 + (int)Math.Round(Math.Sin(ang) * ringR * 0.8), 2, 2);
        }

        Px(g, Color.FromArgb(255, 152, 56), 0.65 * clash, 253, 255 - (t % 3), 2, 3);
        Px(g, Color.FromArgb(152, 128, 255), 0.65 * clash, 314, 255 - ((t + 1) % 3), 2, 3);

        int poolW = 10 + ((t * 2) % 18);
        Px(g, Color.FromArgb(144, 232, 255), 0.40 * clash, 284 - poolW, 315, poolW * 2, 2);
        Px(g, Color.White, 0.55 * clash, 279, 316, 10, 1);
    }

    void PintaJujutsu(Graphics g, int t, double nf) {
        double aB = AudioReactivo ? AudioBoost * 0.35 : 0.0;
        double al = Math.Min(1.0, 0.55 + 0.45 * nf + aB);
        double pulse = 0.72 + 0.28 * Math.Sin(t * 0.14);

        Color cCyan = Color.FromArgb(125, 211, 252);
        Color cPurp = Color.FromArgb(192, 132, 252);
        Color cPink = Color.FromArgb(251, 113, 133);
        Color cRed = Color.FromArgb(255, 40, 72);
        Color cCore = Color.FromArgb(232, 121, 249);
        Color cDarkP = Color.FromArgb(147, 51, 234);

        for (int a = 0; a < 10; a++) {
            double ang = (a * Math.PI * 2.0) / 10.0 + t * 0.05;
            double rX = 33 + Math.Round(Math.Sin(t * 0.1 + a) * 2.0);
            Px(g, a % 2 == 0 ? cCyan : cPurp, 0.65 * al, 452 + Math.Round(Math.Cos(ang) * rX), 162 + Math.Round(Math.Sin(ang) * 17), 2, 1);
        }
        Px(g, Color.White, 0.45 * al * pulse, 450, 161, 4, 2);

        double eyeAl = Math.Min(1.0, (0.55 + 0.45 * Math.Sin(t * 0.16)) * al);
        Px(g, cPink, 0.85 * eyeAl, 151, 217, 2, 2);
        Px(g, cPink, 0.85 * eyeAl, 159, 217, 2, 2);
        Px(g, cRed, 0.50 * al, 146, 260 + (t % 3 == 0 ? -1 : 0), 20, 2);
        for (int s = 0; s < 5; s++) {
            int sy = 200 + ((s * 17 + t * 3) % 68);
            int sx = 122 + ((s * 29) % 68);
            Px(g, s % 2 == 0 ? cRed : cPink, 0.7 * al, sx, sy, 6, 1);
        }

        Px(g, cPink, 0.55 * al, 244, 250 - (t % 3), 2, 4);
        Px(g, Color.FromArgb(239, 68, 68), 0.55 * al, 252, 247 - ((t + 1) % 3), 2, 4);
        for (int k = 0; k < 4; k++) {
            int prog = (t * 3 + k * 7) % 28;
            int sx0 = 264 + prog;
            int sy0 = 240 + ((k * 7) % 18) - (int)Math.Round(prog * 0.25);
            for (int d = 0; d < 7; d++) {
                Px(g, d > 4 ? Color.White : cRed, 0.88 * al, sx0 + d, sy0 + ((k % 2 == 0) ? (d / 2) : -(d / 2)), 1, 1);
            }
        }

        Px(g, Color.FromArgb(56, 189, 248), 0.65 * al, 374, 249 - ((t + 2) % 3), 2, 4);
        double rOrb = 9 + Math.Round(Math.Sin(t * 0.2) * 2.0);
        double rAng = t * 0.22;
        Px(g, cPink, 0.90 * al, 313 + Math.Round(Math.Cos(rAng) * rOrb), 248 + Math.Round(Math.Sin(rAng) * rOrb * 0.6), 3, 3);
        Px(g, Color.FromArgb(56, 189, 248), 0.90 * al, 313 - Math.Round(Math.Cos(rAng) * rOrb), 248 - Math.Round(Math.Sin(rAng) * rOrb * 0.6), 3, 3);

        int coreR = (int)Math.Round(4 + 3 * pulse + aB * 8);
        Px(g, cDarkP, 0.40 * al, 313 - coreR - 4, 248 - coreR - 2, coreR * 2 + 8, coreR * 2 + 4);
        Px(g, cCore, 0.72 * al, 313 - coreR, 248 - coreR, coreR * 2, coreR * 2);
        Px(g, Color.FromArgb(253, 244, 255), 0.96 * al, 311, 246, 5, 5);

        int wave = 8 + ((t * 2) % 22);
        double wAl = Math.Max(0.08, (1.0 - (wave - 8) / 22.0) * 0.75 * al);
        for (int a = 0; a < 12; a++) {
            double ang = (a * Math.PI * 2.0) / 12.0 + t * 0.08;
            Px(g, a % 2 == 0 ? cCore : cCyan, wAl, 313 + Math.Round(Math.Cos(ang) * wave), 248 + Math.Round(Math.Sin(ang) * wave * 0.7), 2, 2);
        }

        int rw = 10 + (int)Math.Round(4 * pulse);
        Px(g, cPurp, 0.42 * al, 313 - rw, 312, rw * 2, 2);
        Px(g, Color.FromArgb(244, 63, 94), 0.35 * al, 146, 314, 20, 2);
    }

    void PintaJujutsuSec(Graphics g, int t, double nf) {
        double aB = AudioReactivo ? AudioBoost * 0.35 : 0.0;
        double al = Math.Min(1.0, 0.58 + 0.42 * nf + aB);
        int bob = (int)Math.Round(Math.Sin(t * 0.12) * 2.0);

        Px(g, Color.FromArgb(234, 179, 8), 0.45 * al, 312, 238 + bob, 16, 16);
        if (t % 29 != 0) {
            Px(g, Color.FromArgb(255, 248, 232), 0.92 * al, 318, 244 + bob, 4, 4);
            Px(g, Color.FromArgb(225, 29, 72), 0.95 * al, 319, 245 + bob, 2, 2);
        }
        for (int c = 0; c < 4; c++) {
            double ang = c * Math.PI * 0.5 + t * 0.07;
            Px(g, Color.FromArgb(250, 204, 21), 0.78 * al, 320 + Math.Round(Math.Cos(ang) * 14), 246 + bob + Math.Round(Math.Sin(ang) * 11), 2, 2);
        }

        bool bfPulse = (t % 16) < 4;
        Px(g, Color.FromArgb(9, 9, 11), 0.90, 224, 247, 7, 7);
        Px(g, bfPulse ? Color.White : Color.FromArgb(251, 113, 133), 0.92 * al, 226, 249, 3, 3);
        for (int b = 0; b < 6; b++) {
            double ang = t * 0.45 + b * 1.05;
            int dist = 5 + ((t * 2 + b * 3) % 10);
            Px(g, b % 2 == 0 ? Color.FromArgb(225, 29, 72) : Color.FromArgb(17, 24, 39), 0.88, 227 + Math.Round(Math.Cos(ang) * dist), 250 + Math.Round(Math.Sin(ang) * dist), 2, 1);
        }

        for (int s = 0; s < 5; s++) {
            int sy = 272 - ((t * 2 + s * 6) % 24);
            int sx = 414 + (int)Math.Round(Math.Sin(t * 0.1 + s) * 8) + (s - 2) * 4;
            Px(g, s % 2 == 0 ? Color.FromArgb(56, 189, 248) : Color.FromArgb(30, 41, 59), 0.72 * al, sx, sy, 2, 2);
        }
        Px(g, Color.FromArgb(16, 185, 129), 0.90 * al, 434, 263, 2, 1);
    }

    void PintaJujutsuBloq(Graphics g, int t, double nf) {
        double aB = AudioReactivo ? AudioBoost * 0.35 : 0.0;
        double al = Math.Min(1.0, 0.58 + 0.42 * nf + aB);
        int sway = (int)Math.Round(Math.Sin(t * 0.09) * 1.5);
        int[] ofudas = new int[] { 298, 310, 330, 342 };
        for (int i = 0; i < ofudas.Length; i++) {
            int ox = ofudas[i];
            Px(g, Color.FromArgb(254, 243, 199), 0.88 * al, ox + sway, 157, 2, 5);
            Px(g, Color.FromArgb(239, 68, 68), 0.78 * al, ox + sway, 159, 1, 2);
        }

        double pulse = 0.65 + 0.35 * Math.Sin(t * 0.14);
        Px(g, Color.FromArgb(225, 29, 72), 0.36 * al * pulse, 313, 223, 14, 14);
        Px(g, Color.FromArgb(251, 113, 133), 0.85 * al * pulse, 318, 227 + (t % 6 < 3 ? 0 : -1), 4, 7);
        Px(g, Color.FromArgb(254, 242, 242), 0.88 * al, 319, 228, 2, 2);

        for (int w = 0; w < 6; w++) {
            double prog = (t * 1.2 + w * 9) % 44;
            int wx = 286 + w * 13 + (int)Math.Round(Math.Sin(t * 0.08 + w) * 3);
            int wy = 266 - (int)Math.Round(prog);
            Px(g, w % 2 == 0 ? Color.FromArgb(168, 85, 247) : Color.FromArgb(244, 63, 94), Math.Max(0.15, (1.0 - prog / 44.0) * 0.80 * al), wx, wy, 2, 2);
        }
        Px(g, Color.FromArgb(225, 29, 72), 0.35 * al * pulse, 312, 318, 16, 2);
    }

    public void TriggerEvento(string tipo, int tick) {
        string[] ops = new string[] { "cometa", "invocacion", "anomalia" };
        if (string.IsNullOrEmpty(tipo)) tipo = ops[Math.Abs(tick) % ops.Length];
        EventoTipo = tipo;
        EventoInicioTick = tick;
    }

    string ClimaEfectivo(DateTime fecha) {
        string m = string.IsNullOrEmpty(ClimaMode) ? "normal" : ClimaMode;
        if (m != "auto") return m;
        int h = fecha.Hour;
        if (TemaId == "spiderman-miles-morales" && (h >= 20 || h < 5)) return "lluvia";
        if (TemaId == "stranger-things" && (h % 2 == 1)) return "tormenta";
        if (TemaId == "demon-slayer" || TemaId == "harry-potter" || TemaId == "jujutsu-kaisen") return "niebla";
        if (TemaId == "fittoa" && (h < 7 || h >= 22)) return "niebla";
        return "normal";
    }

    void PintaEventoEspecial(Graphics g, int t) {
        if (string.IsNullOrEmpty(EventoTipo)) return;
        int age = t - EventoInicioTick;
        if (age < 0 || age > EventoDuracion) { EventoTipo = ""; return; }
        double p = (double)age / (double)EventoDuracion;
        double env = p < 0.15 ? p / 0.15 : (p > 0.8 ? (1.0 - p) / 0.2 : 1.0);

        if (EventoTipo == "cometa") {
            double cx = 60.0 + p * 520.0;
            double cy = 28.0 + p * 125.0 - Math.Sin(p * Math.PI) * 18.0;
            for (int k = 0; k < 18; k++) {
                double tx = cx - k * 3.6;
                double ty = cy - k * 1.1;
                double a = (1.0 - k / 18.0) * 0.85 * env;
                Color c = k < 4 ? Color.White : (k < 10 ? Color.FromArgb(253, 224, 71) : Color.FromArgb(56, 189, 248));
                Px(g, c, a, tx, ty, k < 5 ? 3 : 2, k < 5 ? 2 : 1);
            }
            Px(g, Color.White, 0.98 * env, cx - 1, cy - 1, 4, 4);
        } else if (EventoTipo == "invocacion") {
            Color cGold = Color.FromArgb(250, 204, 21);
            Color cCyan = Color.FromArgb(56, 189, 248);
            for (int a = 0; a < 16; a++) {
                double ang = (a * Math.PI * 2.0) / 16.0 + t * 0.08;
                Px(g, a % 2 == 0 ? cGold : cCyan, 0.82 * env, 320 + Math.Round(Math.Cos(ang) * 34), 224 + Math.Round(Math.Sin(ang) * 14), 2, 2);
            }
            int[] cols = new int[] { 302, 320, 338 };
            for (int i = 0; i < cols.Length; i++) {
                Px(g, cGold, 0.22 * env, cols[i] - 1, 56, 3, 224);
                Px(g, Color.White, 0.50 * env, cols[i], 76, 1, 204);
            }
            Px(g, cCyan, 0.35 * env, 296, 314, 48, 3);
        } else if (EventoTipo == "anomalia") {
            Color cRed = Color.FromArgb(225, 29, 72);
            Color cPurp = Color.FromArgb(168, 85, 247);
            for (int i = -24; i <= 24; i += 2) {
                int y = 148 + i;
                int x = 320 + (int)Math.Round(Math.Sin(i * 0.35 + t * 0.25) * 6);
                Px(g, Color.FromArgb(9, 9, 11), 0.85 * env, x - 2, y, 5, 2);
                Px(g, (i % 4 == 0) ? cRed : cPurp, 0.90 * env, x - 3, y, 2, 2);
                Px(g, Color.FromArgb(244, 63, 94), 0.90 * env, x + 2, y, 2, 2);
            }
            for (int r = 0; r < 10; r++) {
                double ang = r * 0.62 + t * 0.14;
                double rad = 14 + (age % 22);
                Px(g, r % 2 == 0 ? Color.FromArgb(244, 63, 94) : Color.FromArgb(192, 132, 252), 0.72 * env, 320 + Math.Round(Math.Cos(ang) * rad), 148 + Math.Round(Math.Sin(ang) * rad * 0.7), 2, 1);
            }
        }
    }

    void PintaClima(Graphics g, int t, double wB, double nf, DateTime fecha) {
        string modo = ClimaEfectivo(fecha);
        if (modo == "normal") return;
        double aB = AudioReactivo ? AudioBoost * 0.25 : 0.0;

        if (modo == "lluvia" || modo == "tormenta") {
            bool pesado = (modo == "tormenta");
            double wind = pesado ? -2.2 : -1.0;
            double vyBase = pesado ? 1.55 : 1.0;
            Color col = pesado ? Color.FromArgb(186, 230, 253) : Color.FromArgb(125, 211, 252);
            double alphaBase = (pesado ? 0.56 : 0.42) * (1.0 - 0.15 * wB) + aB;

            for (int i = 0; i < 84; i++) {
                if (!pesado && i % 3 == 2) continue;
                int x0 = (i * 53 + 17) % 640;
                int y0 = (i * 89 + 31) % 390;
                int len = (int)Math.Round((5 + (i % 4) * 2) * (pesado ? 1.35 : 1.0));
                int sp = 6 + (i % 3);
                double gx = (((x0 + t * wind * 2.2) % 640) + 640) % 640;
                double gy = (y0 + t * sp * vyBase) % 390;
                for (int d = 0; d < len; d++) {
                    Px(g, col, alphaBase * (1.0 - d * 0.08), gx + (wind < -1.5 ? -(int)(d * 0.4) : 0), gy + d, 1, 1);
                }
                if (gy > 282 && gy < 386 && i % 7 == 0) {
                    int rw = 2 + ((t + i) % 3);
                    Px(g, Color.FromArgb(224, 242, 254), 0.30 * alphaBase, gx - rw, gy + 1, rw * 2, 1);
                }
            }
            if (pesado) {
                int flash = (t * 17 + 13) % 131;
                if (flash < 2) {
                    Px(g, Color.FromArgb(224, 242, 254), flash == 0 ? 0.22 : 0.10, 0, 0, 640, 280);
                    int lx = 110 + ((t * 97) % 420);
                    for (int y = 8; y < 230; y += 4) {
                        int jx = lx + (int)Math.Round(Math.Sin(y * 0.18 + t) * 7);
                        Px(g, Color.White, 0.92, jx, y, 2, 4);
                        Px(g, col, 0.45, jx - 1, y, 4, 4);
                    }
                }
            }
        } else if (modo == "nieve") {
            double alphaBase = 0.72 + 0.20 * nf;
            for (int i = 0; i < 68; i++) {
                int x0 = (i * 61 + 29) % 640;
                int y0 = (i * 97 + 13) % 390;
                double sp = 0.75 + (i % 4) * 0.35;
                int sz = (i % 5 == 0) ? 2 : 1;
                double sx = (((x0 + Math.Sin(t * 0.04 + i * 0.7) * 14 + t * 0.15) % 640) + 640) % 640;
                double sy = (y0 + t * sp) % 394;
                Px(g, (i % 4 == 0) ? Color.FromArgb(224, 242, 254) : Color.White, alphaBase, sx, sy, sz, sz);
            }
        } else if (modo == "niebla") {
            Color col = wB > 0.5 ? Color.FromArgb(248, 250, 252) : Color.FromArgb(203, 213, 225);
            for (int i = 0; i < 6; i++) {
                double mx = (((i * 120 + t * (0.25 + (i % 3) * 0.12)) % 760) + 760) % 760 - 120;
                int my = 252 + i * 14;
                int mw = 95 + (i % 3) * 45;
                Px(g, col, 0.09 + 0.06 * nf, mx, my, mw, 5);
                Px(g, col, 0.05 + 0.04 * nf, mx + 16, my - 2, mw - 32, 2);
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

            if (S.ModoHeroe != null && S.ModoHeroe.StartsWith("stranger_")) {
                PintaTormentaStranger(g, t, nf, S.ModoHeroe);
            }

            DrawAlpha(g, S.EscenaNoche, 0, 0, 1.0);
            DrawAlpha(g, S.EscenaDorado, 0, 0, wA);
            DrawAlpha(g, S.EscenaDia, 0, 0, wB);

            if (S.ModoMiles) { PintaFerry(g, t, nf); PintaMiles(g, t, nf); }
            else if (S.ModoMilesColgado) { PintaFerry(g, t, nf); PintaMilesColgado(g, t, nf); }
            else if (S.ModoHeroe == "stranger_azotamentes") { PintaStrangerPrincipal(g, t, nf); }
            else if (S.ModoHeroe == "stranger_demogorgon") { PintaStrangerDemogorgon(g, t, nf); }
            else if (S.ModoHeroe == "stranger_reloj") { PintaStrangerReloj(g, t, nf); }
            else if (S.ModoHeroe == "demon_rengoku") { PintaDemonRengoku(g, t, nf); }
            else if (S.ModoHeroe == "demon_tokito") { PintaDemonTokito(g, t, nf); }
            else if (S.ModoHeroe == "demon_glicinias") { PintaDemonGlicinias(g, t, nf); }
            else if (S.ModoHeroe == "naruto_baryon") { PintaNarutoBaryon(g, t, nf); }
            else if (S.ModoHeroe == "naruto_konoha") { PintaNarutoKonoha(g, t, nf); }
            else if (S.ModoHeroe == "naruto_valle") { PintaNarutoValle(g, t, nf); }
            else if (S.ModoHeroe == "jujutsu") { PintaJujutsu(g, t, nf); }
            else if (S.ModoHeroe == "jujutsu_sec") { PintaJujutsuSec(g, t, nf); }
            else if (S.ModoHeroe == "jujutsu_bloq") { PintaJujutsuBloq(g, t, nf); }

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
            PintaEventoEspecial(g, t);
            PintaClima(g, t, wB, nf, fecha);
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

public static class PzmSystemGuard {
    [StructLayout(LayoutKind.Sequential)]
    struct GuardRect { public int Left, Top, Right, Bottom; }

    [DllImport("user32.dll")]
    static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    static extern bool GetWindowRect(IntPtr hWnd, out GuardRect lpRect);

    [DllImport("user32.dll")]
    static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    static extern int GetClassName(IntPtr hWnd, System.Text.StringBuilder lpClassName, int nMaxCount);

    [DllImport("user32.dll")]
    static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

    [DllImport("user32.dll")]
    static extern short GetAsyncKeyState(int vKey);

    static readonly int _selfPid = System.Diagnostics.Process.GetCurrentProcess().Id;
    static int _lastMask = 0;

    public static bool IsFullscreenAppActive() {
        try {
            IntPtr fg = GetForegroundWindow();
            if (fg == IntPtr.Zero || !IsWindowVisible(fg)) return false;
            uint pid;
            GetWindowThreadProcessId(fg, out pid);
            if ((int)pid == _selfPid) return false;
            var sb = new System.Text.StringBuilder(64);
            GetClassName(fg, sb, sb.Capacity);
            string cls = sb.ToString();
            if (cls == "Progman" || cls == "WorkerW" || cls == "Shell_TrayWnd" ||
                cls == "Shell_SecondaryTrayWnd" || cls == "NotifyIconOverflowWindow" ||
                cls == "Windows.UI.Core.CoreWindow") return false;
            GuardRect r;
            if (!GetWindowRect(fg, out r)) return false;
            Rectangle scr = Screen.FromHandle(fg).Bounds;
            return (r.Right - r.Left) >= (scr.Width - 2) && (r.Bottom - r.Top) >= (scr.Height - 2);
        } catch {
            return false;
        }
    }

    public static bool IsBatterySaver() {
        try {
            var ps = SystemInformation.PowerStatus;
            return ps.PowerLineStatus == PowerLineStatus.Offline && ps.BatteryLifePercent < 0.25f;
        } catch {
            return false;
        }
    }

    public static string PollHotkey() {
        bool ctrl = (GetAsyncKeyState(0x11) & 0x8000) != 0;
        bool alt  = (GetAsyncKeyState(0x12) & 0x8000) != 0;
        if (!ctrl || !alt) { _lastMask = 0; return ""; }

        int mask = 0;
        if ((GetAsyncKeyState(0x57) & 0x8000) != 0) mask |= 1;  // W
        if ((GetAsyncKeyState(0x48) & 0x8000) != 0) mask |= 2;  // H
        if ((GetAsyncKeyState(0x46) & 0x8000) != 0) mask |= 4;  // F
        if ((GetAsyncKeyState(0x50) & 0x8000) != 0) mask |= 8;  // P
        if ((GetAsyncKeyState(0x45) & 0x8000) != 0) mask |= 16; // E

        int newly = mask & (~_lastMask);
        _lastMask = mask;
        if ((newly & 1) != 0) return "W";
        if ((newly & 2) != 0) return "H";
        if ((newly & 4) != 0) return "F";
        if ((newly & 8) != 0) return "P";
        if ((newly & 16) != 0) return "E";
        return "";
    }
}
'@

$null = [System.Drawing.Bitmap]
$null = [System.Drawing.ColorTranslator]
$null = [System.Windows.Forms.Form]
$null = [System.Windows.Forms.Message]
$null = [System.Diagnostics.Process]
$null = [System.ComponentModel.Component]
$refAsms = [System.AppDomain]::CurrentDomain.GetAssemblies() |
    Where-Object {
        (-not $_.IsDynamic) -and $_.Location -and (
            $_.FullName -match '^(mscorlib|netstandard|System\.Runtime|System\.Drawing|System\.Windows\.Forms|System\.ComponentModel|System\.Diagnostics|System\.Private\.Windows|System\.Private\.CoreLib|System,|System\.Collections|System\.Threading)'
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
        $sd.ModoHeroe = if ($t.modo_heroe) { [string]$t.modo_heroe } else { "" }
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
    if ((Test-Path (Join-Path $cand 'images')) -or (Test-Path (Join-Path $cand 'tema.json'))) {
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
$script:climaAct = if ($Clima) { $Clima } else { 'normal' }
$script:temaSecAct = if ($TemaSecundario) { $TemaSecundario } else { 'igual' }
$script:rotacionMinAct = [int]$RotacionMinutos
$script:pausaJuegoAct = [bool]$PausaJuego
$script:audioAct = [bool]$AudioReactivo
$script:hotkeysAct = [bool]$Hotkeys
$script:pauseManual = $false
$script:autoPausado = $false
$script:eventoSeqAct = 0
$script:lastHourEv = -1
$script:ultimaRotacion = Get-Date

if (Test-Path $ConfigPath) {
    try {
        $initCfg = Get-Content $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($initCfg) {
            if ($initCfg.clima) { $script:climaAct = [string]$initCfg.clima }
            if ($initCfg.temaSecundario) { $script:temaSecAct = [string]$initCfg.temaSecundario }
            if ($null -ne $initCfg.rotacionMinutos) { $script:rotacionMinAct = [int]$initCfg.rotacionMinutos }
            if ($null -ne $initCfg.pausaJuego) { $script:pausaJuegoAct = [bool]$initCfg.pausaJuego }
            if ($null -ne $initCfg.audioReactivo) { $script:audioAct = [bool]$initCfg.audioReactivo }
            if ($null -ne $initCfg.hotkeys) { $script:hotkeysAct = [bool]$initCfg.hotkeys }
            if ($null -ne $initCfg.eventoSeq) { $script:eventoSeqAct = [int]$initCfg.eventoSeq }
        }
    } catch {}
}

$script:rendPrim = New-Object PzmRenderer
$script:rendSec = New-Object PzmRenderer
$script:scenePrim = $null
$script:sceneSec = $null
$script:forms = @()

function Obtener-TemasLista {
    if (-not (Test-Path $TemasBase)) { return @('fittoa') }
    $dirs = Get-ChildItem -Path $TemasBase -Directory -ErrorAction SilentlyContinue | Where-Object {
        (Test-Path (Join-Path $_.FullName 'images')) -or (Test-Path (Join-Path $_.FullName 'tema.json'))
    } | Select-Object -ExpandProperty Name | Sort-Object
    if ($dirs) { return @($dirs) }
    return @('fittoa')
}

function Actualizar-ConfigCampo([hashtable]$cambios) {
    try {
        $obj = @{}
        if (Test-Path $ConfigPath) {
            $raw = Get-Content $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($raw) {
                foreach ($p in $raw.PSObject.Properties) { $obj[$p.Name] = $p.Value }
            }
        }
        foreach ($k in $cambios.Keys) { $obj[$k] = $cambios[$k] }
        $dir = Split-Path -Parent $ConfigPath
        if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
        ($obj | ConvertTo-Json -Depth 5) | Set-Content -Path $ConfigPath -Encoding UTF8
        $script:lastCfgWrite = (Get-Item $ConfigPath).LastWriteTimeUtc
    } catch {}
}

function Siguiente-Mundo {
    $lista = Obtener-TemasLista
    if ($lista.Count -lt 2) { return }
    $idx = [Array]::IndexOf($lista, $script:temaAct)
    $sig = $lista[($idx + 1) % $lista.Count]
    $script:temaAct = $sig
    $script:ultimaRotacion = Get-Date
    Actualizar-ConfigCampo @{ tema = $sig }
    Recargar-Escenas
}

function Recargar-Escenas {
    $tDir = Join-Path $TemasBase $script:temaAct
    if (-not (Test-Path (Join-Path $tDir 'images')) -and -not (Test-Path (Join-Path $tDir 'tema.json'))) {
        Write-MotorLog "Recargar-Escenas: tema inexistente $tDir"
        return
    }
    if ($script:scenePrim) { $script:scenePrim.DisposeImages() }
    if ($script:sceneSec) { $script:sceneSec.DisposeImages() }

    $rPrim = Resolver-RutaVariante $tDir $script:fondoPrimAct
    $script:scenePrim = Cargar-SceneData $rPrim.Dir $rPrim.ConAstro
    $script:rendPrim.TemaId = $script:temaAct
    $script:rendPrim.ClimaMode = $script:climaAct
    $script:rendPrim.AudioReactivo = $script:audioAct

    $tSecId = if ($script:temaSecAct -and $script:temaSecAct -ne 'igual' -and $script:temaSecAct -ne $script:temaAct) { $script:temaSecAct } else { $script:temaAct }
    $tDirSec = Join-Path $TemasBase $tSecId
    if (-not (Test-Path (Join-Path $tDirSec 'images'))) { $tDirSec = $tDir; $tSecId = $script:temaAct }

    if ($script:monAct -ge 2) {
        $rSec = Resolver-RutaVariante $tDirSec $script:fondoSecAct
        $script:sceneSec = Cargar-SceneData $rSec.Dir $rSec.ConAstro
        $script:rendSec.TemaId = $tSecId
        $script:rendSec.ClimaMode = $script:climaAct
        $script:rendSec.AudioReactivo = $script:audioAct
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
    Write-MotorLog "Escenas cargadas: tema=$($script:temaAct) secTema=$tSecId mon=$($script:monAct) clima=$($script:climaAct)"
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

    if ($script:hotkeysAct) {
        $hk = [PzmSystemGuard]::PollHotkey()
        if ($hk -eq 'W') { Siguiente-Mundo }
        elseif ($hk -eq 'H') {
            $curHud = $true
            if (Test-Path $ConfigPath) {
                try {
                    $hc = Get-Content $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
                    if ($null -ne $hc.hud) { $curHud = [bool]$hc.hud }
                } catch {}
            }
            $nuevoHud = -not $curHud
            Actualizar-ConfigCampo @{ hud = $nuevoHud }
            if ($nuevoHud) {
                $hudScript = Join-Path $Aqui 'PixelZenHud.ps1'
                if (Test-Path $hudScript) {
                    $psBin = if ($PSVersionTable.PSEdition -eq 'Core') { 'pwsh' } else { 'powershell' }
                    Start-Process $psBin -ArgumentList @('-NoProfile','-WindowStyle','Hidden','-ExecutionPolicy','Bypass','-File',$hudScript) -WindowStyle Hidden
                }
            }
        }
        elseif ($hk -eq 'F') {
            $climas = @('normal', 'lluvia', 'tormenta', 'nieve', 'niebla', 'auto')
            $ci = [Array]::IndexOf($climas, $script:climaAct)
            $script:climaAct = $climas[($ci + 1) % $climas.Count]
            $script:rendPrim.ClimaMode = $script:climaAct
            $script:rendSec.ClimaMode = $script:climaAct
            Actualizar-ConfigCampo @{ clima = $script:climaAct }
        }
        elseif ($hk -eq 'P') {
            $script:pauseManual = -not $script:pauseManual
            Write-MotorLog "Hotkey P: pauseManual=$($script:pauseManual)"
        }
        elseif ($hk -eq 'E') {
            $script:rendPrim.TriggerEvento('', $t)
            $script:rendSec.TriggerEvento('', $t)
        }
    }

    if (($t % 8) -eq 0 -and (Test-Path $ConfigPath)) {
        try {
            $wt = (Get-Item $ConfigPath).LastWriteTimeUtc
            if ($wt -ne $script:lastCfgWrite) {
                $script:lastCfgWrite = $wt
                $nc = Get-Content $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($nc) {
                    $fp = if ($nc.fondoPrincipal) { [string]$nc.fondoPrincipal } else { $script:fondoPrimAct }
                    $fs = if ($nc.fondoSecundario) { [string]$nc.fondoSecundario } else { $script:fondoSecAct }
                    $ts = if ($nc.temaSecundario) { [string]$nc.temaSecundario } else { $script:temaSecAct }
                    $cambio = ($nc.tema -ne $script:temaAct) -or ([int]$nc.monitores -ne $script:monAct) -or ($fp -ne $script:fondoPrimAct) -or ($fs -ne $script:fondoSecAct) -or ($ts -ne $script:temaSecAct)
                    if ($nc.tema) { $script:temaAct = [string]$nc.tema }
                    if ($nc.monitores) { $script:monAct = [int]$nc.monitores }
                    $script:fondoPrimAct = $fp
                    $script:fondoSecAct = $fs
                    $script:temaSecAct = $ts
                    if ($nc.clima) {
                        $script:climaAct = [string]$nc.clima
                        $script:rendPrim.ClimaMode = $script:climaAct
                        $script:rendSec.ClimaMode = $script:climaAct
                    }
                    if ($null -ne $nc.rotacionMinutos) { $script:rotacionMinAct = [int]$nc.rotacionMinutos }
                    if ($null -ne $nc.pausaJuego) { $script:pausaJuegoAct = [bool]$nc.pausaJuego }
                    if ($null -ne $nc.audioReactivo) {
                        $script:audioAct = [bool]$nc.audioReactivo
                        $script:rendPrim.AudioReactivo = $script:audioAct
                        $script:rendSec.AudioReactivo = $script:audioAct
                    }
                    if ($null -ne $nc.hotkeys) { $script:hotkeysAct = [bool]$nc.hotkeys }
                    if ($null -ne $nc.eventoSeq -and ([int]$nc.eventoSeq -ne $script:eventoSeqAct)) {
                        $script:eventoSeqAct = [int]$nc.eventoSeq
                        $evT = if ($nc.eventoTipo) { [string]$nc.eventoTipo } else { '' }
                        $script:rendPrim.TriggerEvento($evT, $t)
                        $script:rendSec.TriggerEvento($evT, $t)
                    }
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

    if ($script:rotacionMinAct -gt 0 -and ((Get-Date) - $script:ultimaRotacion).TotalMinutes -ge $script:rotacionMinAct) {
        Siguiente-Mundo
    }

    if ($script:modoAct -eq 'real') {
        $nowDt = Get-Date
        if ($nowDt.Minute -eq 0 -and $nowDt.Second -lt 3 -and $script:lastHourEv -ne $nowDt.Hour) {
            $script:lastHourEv = $nowDt.Hour
            $script:rendPrim.TriggerEvento('', $t)
            $script:rendSec.TriggerEvento('', $t)
        }
    }

    if (($t % 8) -eq 0) {
        $nuevoPausa = $script:pausaJuegoAct -and ([PzmSystemGuard]::IsFullscreenAppActive() -or [PzmSystemGuard]::IsBatterySaver())
        if ($nuevoPausa -ne $script:autoPausado) {
            $script:autoPausado = $nuevoPausa
            Write-MotorLog "SmartPause cambiado: autoPausado=$($script:autoPausado)"
        }
    }

    if ($script:pauseManual -or $script:autoPausado) { return }

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
