// PixelZen para GNOME - fondo animado parametrizado por tema.json.
// Toda la escena vive en un lienzo de 640x400 escalado con NEAREST.

import GLib from 'gi://GLib';
import GdkPixbuf from 'gi://GdkPixbuf';
import Clutter from 'gi://Clutter';
import Cogl from 'gi://Cogl';
import St from 'gi://St';
import Cairo from 'cairo';

const W = 640, H = 400;

const cacheColor = new Map();
function hexA(hex) {
    const h = hex.replace('#', '');
    return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}
export function color(hex, alpha = 255) {
    const k = hex + alpha;
    if (cacheColor.has(k)) return cacheColor.get(k);
    const [red, green, blue] = hexA(hex);
    const C = Clutter.Color ?? Cogl.Color;
    const c = new C({red, green, blue, alpha});
    cacheColor.set(k, c);
    return c;
}

const clamp01 = v => v < 0 ? 0 : v > 1 ? 1 : v;
const op255 = v => Math.round(clamp01(v) * 255);

const cacheRgb = new Map();
function px(cr, hex, op, ax, ay, aw = 1, ah = 1) {
    if (op <= 0.004) return;
    let c = cacheRgb.get(hex);
    if (!c) { c = hexA(hex).map(v => v / 255); cacheRgb.set(hex, c); }
    cr.setSourceRGBA(c[0], c[1], c[2], op > 1 ? 1 : op);
    cr.rectangle(Math.round(ax), Math.round(ay), aw, ah);
    cr.fill();
}
function fija(a, op) {
    const o = op255(op);
    const v = o > 1;
    if (a.visible !== v) a.visible = v;
    if (v && a.opacity !== o) a.opacity = o;
    return v;
}

function contenido(pixbuf) {
    const c = St.ImageContent.new_with_preferred_size(pixbuf.width, pixbuf.height);
    const fmt = pixbuf.has_alpha ? Cogl.PixelFormat.RGBA_8888 : Cogl.PixelFormat.RGB_888;
    const bytes = pixbuf.read_pixel_bytes();
    try {
        c.set_bytes(bytes, fmt, pixbuf.width, pixbuf.height, pixbuf.rowstride);
    } catch (e) {
        const ctx = global.stage.context.get_backend().get_cogl_context();
        c.set_bytes(ctx, bytes, fmt, pixbuf.width, pixbuf.height, pixbuf.rowstride);
    }
    return c;
}
function imagen(padre, cont, w, h) {
    const a = new Clutter.Actor({width: w, height: h});
    a.set_content(cont);
    a.set_content_scaling_filters(Clutter.ScalingFilter.NEAREST, Clutter.ScalingFilter.NEAREST);
    padre.add_child(a);
    return a;
}

function lcg(seed) {
    let s = seed;
    return () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
}

const ALAS_GRULLA = [
    [[-5, -2], [-4, -2], [-3, -1], [-2, -1], [-1, 0], [0, 0], [1, 0], [2, -1], [3, -1], [4, -2], [5, -2]],
    [[-5, 1], [-4, 1], [-3, 1], [-2, 0], [-1, 0], [0, 0], [1, 0], [2, 0], [3, 1], [4, 1], [5, 1]],
    [[-5, 2], [-4, 1], [-3, 1], [-2, 0], [-1, 0], [0, 1], [1, 0], [2, 0], [3, 1], [4, 1], [5, 2]],
];
const ALAS_WYVERN = [
    [[-7, -3], [-6, -3], [-5, -2], [-4, -2], [-3, -1], [-2, -1], [-1, 0], [0, 0], [1, 0], [2, -1], [3, -1], [4, -2], [5, -2], [6, -3], [7, -3], [0, 2]],
    [[-7, 1], [-6, 1], [-5, 1], [-4, 0], [-3, 0], [-2, 0], [-1, 0], [0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 1], [6, 1], [7, 1], [0, 2]],
    [[-7, 3], [-6, 2], [-5, 2], [-4, 1], [-3, 1], [-2, 0], [-1, 0], [0, 1], [1, 0], [2, 0], [3, 1], [4, 1], [5, 2], [6, 2], [7, 3], [0, 2]],
];

const TEMA_DEFECTO = {
    cielo_fondo: '#0a0c24',
    modo_pajaros: 'grullas',
    color_pajaros: '#120c26',
    modo_particulas: 'hojas_mana',
    colores_hojas: ['#a4d86c', '#6ec05a', '#d8b45c', '#5cf2e4'],
    color_mana_halo: '#5cf2e4',
    color_mana_centro: '#b8fff6',
    color_fuegos_halo: ['#f0cf68', '#40e4dc'],
    color_fuegos_centro: ['#fff2b0', '#b2fff6'],
    color_ventanas: '#f4bc68',
    color_faroles_halo: '#f4bc68',
    color_faroles_centro: '#fff0c0',
    color_runas_halo: '#4bece2',
    color_runas_centro: '#9efcf4',
    color_humo_dia: '#e6ecf2',
    color_humo_noche: '#9aaec4',
    color_olas: ['#9cd4d8', '#5882b0'],
    color_reflejo_sol: '#ffe6a0',
    color_reflejo_luna: '#f4ead2',
    color_destello: '#fff6e2',
};

const MOTAS_MANA = [[70, 300], [95, 330], [130, 290], [565, 310], [590, 340], [20, 345], [470, 296], [160, 355], [248, 318], [520, 352]];

const MILES_FRAMES = [
    {
        hc: 22, hr: 0, rows: [
            '......................HR..', '.....................RRK..', '....................SSK...',
            '..........KSSK.....SSK....', '.........KSRWWWR..SSK.....', '.........KSKWWWWR.SSK.....',
            '.........KSKKWWWKSSK......', '..........KKKKKKSSK.......', '........SSKRRRRRKSS.......',
            '.......SSKKRRRRRKK........', '......SS..KKRRRKK.........', '.....SS...KKKKKK..KKKK....',
            '....HR....KKKKKKKKKKSSKK..', '....E....KKKKKK..KKK..KKK.', '........KKSSKK........SSK.',
            '.......KK..KK.........RRR.', '......KK..............RR..', '.....SS...................',
            '....RR....................', '....R.....................',
        ],
    },
    {
        hc: 18, hr: 0, rows: [
            '..................HR......', '.................RRK......', '................SSK.......',
            '........KSSK...SSK........', '.......KSRWWWRSSK.........', '.......KSKWWWWRSK.........',
            '.......KSKKWWWKSS.........', '........KKKKKKKSS.........', '......SSKRRRRRKSS.........',
            '.....SSKKRRRRRKK..........', '....SS..KKRRRKK...........', '...HR...KKKKKK..KKKK......',
            '...E...KKKKKKKKKKSSKK.....', '.......KKKKK...KKK.KKK....', '......KKSSK........RRR....',
            '.....KK..KK.........R.....', '....RR...RR...............', '....R.....................',
            '..........................', '..........................',
        ],
    },
    {
        hc: 14, hr: 0, rows: [
            '..............HR..........', '.............RRK..........', '............SSK...........',
            '............SSK.KSSK......', '...........SSK.KSRWWWR....', '...........SSKKKSKWWWWR...',
            '............SSKKKSKWWWK...', '...........SSKRRRRKKKK....', '..........SSKKRRRRKK......',
            '.........SS..KKRRKK.......', '........HR...KKKKK..KKKK..', '........E...KKKKKK.KKSSKK.',
            '...........KKSSK....KK.KK.', '..........KK..KK.......RRR', '.........KK............RR.',
            '........SS................', '.......RR.................', '..........................',
            '..........................', '..........................',
        ],
    },
    {
        hc: 14, hr: 7, rows: [
            '..........................', '..........................', '..........................',
            '..........KSSK............', '.........KSRWWWR..........', '.........KSKWWWWR.........',
            '.........KSKKWWWK.........', '..........KKKKKK..........', '........SSKRRRRRKSS.......',
            '.......SSKKRRRRKKKRR......', '......SS..KKRRKK..E.......', '.....HR...KKKKK.KKKK......',
            '..........KKKKKKKKSSKK....', '.........KKKKK....RRR.....', '........KKSSKK....R.......',
            '.......KK..KK.............', '......RR...RR.............', '..........................',
            '..........................', '..........................',
        ],
    },
];
const MILES_COLS = {
    K: '#0b0a14', S: '#2e3358', R: '#e61e3c', H: '#ff5470', W: '#ffffff', E: '#00e5ff',
};

function pintaMiles(cr, t, nf) {
    const P = 340, mitad = 170;
    const fase = ((t % P) + P) % P;
    const der = fase < mitad;
    const u = der ? fase / mitad : (fase - mitad) / mitad;
    const flip = !der;
    const x = der ? -24 + u * 688 : 664 - u * 688;
    const arcW = 688 / 3;
    const arcIdx = Math.min(2, Math.floor(u * 3));
    const su = u * 3 - arcIdx;
    const tieneRed = su >= 0.08 && su <= 0.86;
    const fIdx = !tieneRed ? 3 : su < 0.34 ? 0 : su < 0.64 ? 1 : 2;
    let y = (der ? 62 : 76) + 52 * Math.sin(su * Math.PI);
    if (!tieneRed) {
        const j = su > 0.86 ? (su - 0.86) / 0.22 : (su + 0.14) / 0.22;
        y -= 7 * Math.sin(Math.min(1, Math.max(0, j)) * Math.PI);
    }
    const mx = Math.round(x), my = Math.round(y);
    const fr = MILES_FRAMES[fIdx];

    if (tieneRed) {
        const arcStart = der ? -24 + arcIdx * arcW : 664 - arcIdx * arcW;
        const ax = Math.round(der ? arcStart + arcW * 0.62 : arcStart - arcW * 0.62);
        const hx = mx + (flip ? 13 - fr.hc : fr.hc - 13);
        const hy = my + fr.hr - 10;
        const steps = Math.max(1, Math.max(Math.abs(ax - hx), Math.abs(hy)));
        for (let i = 0; i <= steps; i++) {
            const wx = Math.round(hx + (ax - hx) * i / steps);
            const wy = Math.round(hy * (1 - i / steps));
            px(cr, '#dceaff', (i % 2 === 0 ? 0.88 : 0.68) * (1 - 0.12 * nf), wx, wy, 1, 1);
        }
    }

    for (let r = 0; r < fr.rows.length; r++) {
        const row = fr.rows[r];
        for (let c = 0; c < row.length; c++) {
            const ch = row[c];
            if (ch !== '.') px(cr, MILES_COLS[ch], 1, mx + (flip ? 13 - c : c - 13), my + r - 10, 1, 1);
        }
    }

    const tailDir = der ? -1 : 1;
    for (let k = 0; k < 3; k++) {
        if ((t + k) % 3 !== 0) continue;
        const sx = mx + tailDir * (10 + k * 4) + Math.round(Math.sin(t * 0.6 + k * 2) * 2);
        const sy = my + 2 + Math.round(Math.cos(t * 0.5 + k * 1.7) * 3);
        px(cr, k === 1 ? '#ffd840' : '#00e5ff', 0.85, sx, sy, 1, 1);
    }
}

function pintaFerry(cr, t, nf) {
    const P = 1800, mitad = 900;
    const f = ((t % P) + P) % P;
    const der = f < mitad;
    const u = der ? f / mitad : (f - mitad) / mitad;
    const fx = Math.round(der ? 180 + u * 320 : 500 - u * 320);
    const fy = 295 + (Math.sin(t * 0.08) > 0.6 ? 1 : 0);
    const dir = der ? 1 : -1;
    px(cr, '#141a2e', 0.95, fx - 10, fy, 20, 2);
    px(cr, '#e65c28', 0.95, fx - 9, fy - 1, 18, 1);
    px(cr, '#dce6f2', 0.95, fx - 7, fy - 3, 14, 2);
    px(cr, '#f0682c', 0.95, fx - 6, fy - 4, 12, 1);
    px(cr, '#dce6f2', 0.95, fx - 3, fy - 6, 6, 2);
    px(cr, '#1e2438', 0.95, fx - dir * 1, fy - 8, 2, 2);
    if (nf > 0.15) {
        for (let wx = -5; wx <= 5; wx += 2) px(cr, '#ffe088', 0.85 * nf, fx + wx, fy - 3, 1, 1);
        px(cr, '#ff3658', 0.9 * nf, fx - dir * 9, fy - 2, 1, 1);
        px(cr, '#54ff98', 0.9 * nf, fx + dir * 9, fy - 2, 1, 1);
    }
    for (let k = 1; k <= 7; k++) {
        if ((Math.floor(t / 2) + k) % 2 === 0) px(cr, '#d4ecff', 0.45 * (1 - k / 8), fx - dir * (10 + k * 2), fy + 1, 2, 1);
    }
}

export class Escena {
    constructor(dir, contenedor, settings) {
        this._dir = dir;
        this._cont = contenedor;
        this._settings = settings;
        this._monitores = [];
        this._timer = 0;
        this._pausa = false;
        this.tick = 0;
        this.lat = 40.4;
        this.lon = -3.7;

        let n = lcg(7);
        this.olas = [];
        for (let i = 0; i < 44; i++)
            this.olas.push([300 + Math.floor(n() * 260), 286 + Math.floor(n() * 108), 3 + Math.floor(n() * 11), n() * 6.28, 0.03 + n() * 0.05, n() < 0.35]);
        n = lcg(21);
        this.hojas = [];
        for (let i = 0; i < 42; i++)
            this.hojas.push([n() * 640, n() * 400, 0.30 + n() * 0.42, 0.06 + n() * 0.12, n() * 6.28, Math.floor(n() * 4)]);

        this._cargaDatosYTexturas();
        this._leeAjustes();
        this.recalcula();
    }

    _rutaTema() {
        const id = this._settings?.get_string('tema') || '';
        const sub = id ? `${this._dir}/temas/${id}` : '';
        if (sub && GLib.file_test(`${sub}/datos.json`, GLib.FileTest.EXISTS)) return sub;
        return this._dir;
    }

    _cargaPack(dir) {
        const D = JSON.parse(new TextDecoder().decode(
            GLib.file_get_contents(`${dir}/datos.json`)[1]));
        const brillantes = D.estrellas.filter(e => e[3] === 1);
        let T;
        try {
            const raw = JSON.parse(new TextDecoder().decode(
                GLib.file_get_contents(`${dir}/tema.json`)[1]));
            T = {...TEMA_DEFECTO, ...raw};
        } catch (e) {
            T = {...TEMA_DEFECTO};
        }

        const img = f => GdkPixbuf.Pixbuf.new_from_file(`${dir}/images/${f}.png`);
        const tex = {};
        for (const f of ['cielo-noche', 'cielo-dorado', 'cielo-dia', 'escena-noche', 'escena-dorado', 'escena-dia', 'sol', 'luna'])
            tex[f] = contenido(img(f));
        const texNubes = {};
        for (const fase of ['noche', 'dorado', 'dia']) {
            const hoja = img(`nubes-${fase}`);
            texNubes[fase] = D.nubes.map(nb => contenido(hoja.new_subpixbuf(0, nb[4], nb[2], nb[3]).copy()));
        }
        return {D, T, brillantes, tex, texNubes};
    }

    _cargaDatosYTexturas() {
        const dir = this._rutaTema();
        const prim = this._cargaPack(dir);
        this.D = prim.D;
        this.T = prim.T;
        this.brillantes = prim.brillantes;
        this.tex = prim.tex;
        this.texNubes = prim.texNubes;
        this._packPrim = prim;

        const secDir = `${dir}/secundario`;
        if (GLib.file_test(`${secDir}/datos.json`, GLib.FileTest.EXISTS)) {
            try {
                this._packSec = this._cargaPack(secDir);
            } catch (e) {
                logError(e, 'PixelZen carga secundario');
                this._packSec = null;
            }
        } else {
            this._packSec = null;
        }
    }

    recargaTema(monitores) {
        try {
            this._cargaDatosYTexturas();
            this.construye(monitores);
        } catch (e) {
            logError(e, 'PixelZen recargaTema');
        }
    }

    _leeAjustes() {
        const s = this._settings;
        this.animar = s.get_boolean('animar');
        this.fps = Math.max(2, Math.min(24, s.get_int('fps')));
        this.horaSim = s.get_double('hora-simulada');
        this.demo = s.get_boolean('ciclo-rapido');
        this.duracionCiclo = Math.max(10, s.get_int('ciclo-duracion'));
    }

    ajustesCambiados() {
        this._leeAjustes();
        this.recalcula();
        this.pinta();
        this._programa();
    }

    static suave(t) { t = clamp01(t); return t * t * (3 - 2 * t); }
    sol(fecha) {
        const rad = Math.PI / 180;
        const n = fecha.getTime() / 86400000 + 2440587.5 - 2451545.0;
        const L = (280.460 + 0.9856474 * n) % 360;
        const g = ((357.528 + 0.9856003 * n) % 360) * rad;
        const lam = (L + 1.915 * Math.sin(g) + 0.020 * Math.sin(2 * g)) * rad;
        const eps = (23.439 - 0.0000004 * n) * rad;
        const ra = Math.atan2(Math.cos(eps) * Math.sin(lam), Math.cos(lam));
        const dec = Math.asin(Math.sin(eps) * Math.sin(lam));
        const gmst = (18.697374558 + 24.06570982441908 * n) % 24;
        let Hh = (gmst * 15 + this.lon) * rad - ra;
        Hh = Math.atan2(Math.sin(Hh), Math.cos(Hh));
        const phi = this.lat * rad;
        const e = Math.asin(Math.sin(phi) * Math.sin(dec) + Math.cos(phi) * Math.cos(dec) * Math.cos(Hh));
        const A = Math.atan2(Math.sin(Hh), Math.cos(Hh) * Math.sin(phi) - Math.tan(dec) * Math.cos(phi)) + Math.PI;
        const c0 = Math.max(-1, Math.min(1, -Math.tan(phi) * Math.tan(dec)));
        return {e: e / rad, az: A / rad % 360, H: Hh, H0: Math.acos(c0)};
    }
    fechaEfectiva() {
        const d = new Date();
        if (this.demo) {
            const dur = this.duracionCiclo || 90;
            const h = (Date.now() / 1000 % dur) / dur * 24;
            d.setHours(Math.floor(h), Math.floor(h % 1 * 60), Math.floor(h * 3600 % 60), 0);
        } else if (this.horaSim >= 0) {
            d.setHours(Math.floor(this.horaSim), Math.round(this.horaSim % 1 * 60), 0, 0);
        }
        return d;
    }
    recalcula() {
        const s = this.sol(this.fechaEfectiva());
        const su = Escena.suave;
        this.elev = s.e;
        this.wA = s.e <= -14 ? 0 : s.e >= 0 ? 1 : su((s.e + 14) / 14);
        this.wB = s.e <= 0 ? 0 : s.e >= 16 ? 1 : su(s.e / 16);
        this.nocheF = clamp01((4 - s.e) / 10);
        this.estrellaF = clamp01((-6 - s.e) / 8);
        this.solX = Math.max(30, Math.min(610, 320 + (s.az - 180) * 2.3));
        this.solY = Math.max(24, 272 - Math.max(s.e, -9) * 3.6);
        this.solOp = clamp01((s.e + 6) / 6);
        const H0 = s.H0;
        let f = -1;
        if (s.H >= H0) f = (s.H - H0) / (2 * Math.PI - 2 * H0);
        else if (s.H <= -H0) f = (s.H + 2 * Math.PI - H0) / (2 * Math.PI - 2 * H0);
        if (f >= 0) { this.lunaX = 110 + f * 420; this.lunaY = 272 - 56 * Math.sin(Math.PI * f) * 3.6; }
        else if (this.lunaX === undefined) { this.lunaX = 320; this.lunaY = 300; }
        this.lunaOp = f >= 0 ? clamp01((-s.e - 1) / 5) : 0;
        this.cuerpoX = this.elev > -1 ? this.solX : this.lunaX;
        this.cuerpoOp = this.elev > -1 ? clamp01((this.elev + 2) / 6) : this.lunaOp;
    }
    ponUbicacion(lat, lon) {
        this.lat = lat; this.lon = lon;
        this.recalcula();
        this.pinta();
    }
    osc(f, p) { return 0.5 + 0.5 * Math.sin(this.tick * f + p); }

    construye(monitores) {
        this.destruyeMonitores();
        if (!monitores.length) return;
        this._lienzo = this._creaLienzo(this._packPrim);
        this._lienzo2 = (monitores.length > 1 && this._packSec) ? this._creaLienzo(this._packSec) : null;
        monitores.forEach((mon, i) => this._monitores.push(this._creaMonitor(mon, i === 0)));
        this.pinta();
        this._programa();
    }

    _creaLienzo(pack) {
        const D = pack.D, T = pack.tex, TN = pack.texNubes;
        const l = {pack};
        const raiz = new Clutter.Actor({width: W, height: H});
        l.raiz = raiz;
        const area = fn => {
            const a = new St.DrawingArea({width: W, height: H});
            a.set_content_scaling_filters(Clutter.ScalingFilter.NEAREST, Clutter.ScalingFilter.NEAREST);
            a.connect('repaint', ar => {
                const cr = ar.get_context();
                try {
                    const [sw] = ar.get_surface_size();
                    cr.scale(sw / W, sw / W);
                    cr.setAntialias(Cairo.Antialias.NONE);
                    fn(cr);
                } catch (e) {
                    logError(e, 'PixelZen escena');
                } finally {
                    cr.$dispose();
                }
            });
            raiz.add_child(a);
            return a;
        };

        l.cielo = ['noche', 'dorado', 'dia'].map(f => imagen(raiz, T[`cielo-${f}`], W, H));
        l.atras = area(cr => this._pintaAtras(cr, pack));
        l.sol = imagen(raiz, T.sol, 208, 208);
        l.luna = imagen(raiz, T.luna, 208, 208);
        l.nubes = D.nubes.map((nb, i) => ['noche', 'dorado', 'dia'].map(f => {
            const a = imagen(raiz, TN[f][i], nb[2], nb[3]);
            a.y = nb[1];
            return a;
        }));
        l.escena = ['noche', 'dorado', 'dia'].map(f => imagen(raiz, T[`escena-${f}`], W, H));
        l.delante = area(cr => this._pintaDelante(cr, pack));
        return l;
    }

    _creaMonitor(mon, principal) {
        const raiz = new Clutter.Actor({x: mon.x, y: mon.y, width: mon.width, height: mon.height, clip_to_allocation: true});
        raiz.set_background_color(color(this.T.cielo_fondo));
        this._cont.add_child(raiz);

        const u = Math.max(mon.width / W, mon.height / H);
        const arte = new Clutter.Actor({width: W, height: H});
        arte.set_scale(u, u);
        arte.set_position(Math.round((mon.width - W * u) / 2), Math.round((mon.height - H * u) / 2));
        raiz.add_child(arte);
        if (principal) {
            arte.add_child(this._lienzo.raiz);
        } else if (this._lienzo2) {
            arte.add_child(this._lienzo2.raiz);
        } else {
            arte.add_child(new Clutter.Clone({source: this._lienzo.raiz, width: W, height: H}));
        }

        const r = Math.max(480, mon.width * 0.26);
        const velo = new St.DrawingArea({width: r, height: r});
        velo.connect('repaint', area => {
            const cr = area.get_context();
            const [w] = area.get_surface_size();
            const g = new Cairo.RadialGradient(0, 0, 0, 0, 0, w);
            g.addColorStopRGBA(0.0, 0.04, 0.03, 0.09, 0.82);
            g.addColorStopRGBA(0.5, 0.04, 0.03, 0.09, 0.62);
            g.addColorStopRGBA(1.0, 0.04, 0.03, 0.09, 0.0);
            cr.setSource(g);
            cr.rectangle(0, 0, w, w);
            cr.fill();
            cr.$dispose();
        });
        raiz.add_child(velo);
        return {raiz};
    }

    destruyeMonitores() {
        for (const m of this._monitores.slice().reverse()) m.raiz.destroy();
        this._monitores = [];
        this._lienzo = null;
        this._lienzo2 = null;
    }

    _programa() {
        if (this._timer) { GLib.source_remove(this._timer); this._timer = 0; }
        if (this._pausa || !this._lienzo) return;
        const ms = this.animar ? Math.round(1000 / this.fps) : 60000;
        this._timer = GLib.timeout_add(GLib.PRIORITY_DEFAULT, ms, () => {
            if (this.animar) {
                this.tick++;
                if (this.demo || this.tick % this.fps === 0) this.recalcula();
            } else {
                this.recalcula();
            }
            this.pinta();
            return GLib.SOURCE_CONTINUE;
        });
    }

    _pintaLienzo(l) {
        if (!l) return;
        const t = this.tick;
        const noche = this.elev < 0;
        const opNub = [noche ? 1 - this.wA : 0, noche ? this.wA : 1 - this.wB, this.wB];

        fija(l.cielo[1], this.wA); fija(l.cielo[2], this.wB);
        fija(l.escena[1], this.wA); fija(l.escena[2], this.wB);

        const conAstro = l === this._lienzo;
        l.sol.set_position(Math.round(this.solX - 104), Math.round(this.solY - 104));
        fija(l.sol, conAstro ? this.solOp : 0);
        l.luna.set_position(Math.round(this.lunaX - 104), Math.round(this.lunaY - 104));
        fija(l.luna, conAstro ? this.lunaOp : 0);

        l.pack.D.nubes.forEach((nb, i) => {
            const v = 0.035 + (i % 4) * 0.012;
            const cx = Math.round(((nb[0] + nb[2] + t * v) % (640 + nb[2])) - nb[2]);
            for (let k = 0; k < 3; k++) {
                const a = l.nubes[i][k];
                if (fija(a, opNub[k]) && a.x !== cx) a.x = cx;
            }
        });

        l.atras.queue_repaint();
        l.delante.queue_repaint();
    }

    pinta() {
        this._pintaLienzo(this._lienzo);
        this._pintaLienzo(this._lienzo2);
    }

    _pintaAtras(cr, pack = this._packPrim) {
        const t = this.tick, D = pack.D, T = pack.T, brillantes = pack.brillantes, ef = this.estrellaF;
        cr.setOperator(Cairo.Operator.CLEAR); cr.paint(); cr.setOperator(Cairo.Operator.OVER);
        if (ef > 0.01) {
            D.estrellas.forEach((e, i) => {
                const o = i % 3 === 0 ? 0.3 + 0.7 * this.osc(0.10 + (i % 7) * 0.02, i * 1.3) : 1;
                px(cr, e[2], ef * o, e[0], e[1]);
            });
            brillantes.forEach((e, i) => {
                const o = ef * 0.8 * Math.max(0, this.osc(0.07 + (i % 5) * 0.01, i * 2.1) - 0.55) / 0.45;
                if (o <= 0.004) return;
                px(cr, '#c7ccff', o, e[0] - 1, e[1]); px(cr, '#c7ccff', o, e[0] + 1, e[1]);
                px(cr, '#c7ccff', o, e[0], e[1] - 1); px(cr, '#c7ccff', o, e[0], e[1] + 1);
            });
        }
        const alas = T.modo_pajaros === 'wyverns' ? ALAS_WYVERN : ALAS_GRULLA;
        const cuadro = [0, 1, 2, 1][Math.floor(t / 5) % 4];
        for (const [cx, cy] of [
            [((t * 0.22 + 40) % 760) - 60, 126 + 4 * Math.sin(t * 0.03)],
            [((t * 0.22 + 22) % 760) - 60, 116 + 4 * Math.sin(t * 0.03 + 1)],
            [((t * 0.20 + 5) % 760) - 60, 138 + 4 * Math.sin(t * 0.025 + 2)],
        ]) {
            for (const [dx, dy] of alas[cuadro]) px(cr, T.color_pajaros, 1, cx + dx, cy + dy);
            px(cr, T.color_pajaros, 1, cx, cy + 1);
        }
        const periodo = this.fps * 38;
        const ciclo = Math.floor(t / periodo), fase = t % periodo;
        if (fase < 14 && ef > 0.5) {
            const x0 = 60 + ((ciclo * 137) % 300), y0 = 20 + ((ciclo * 53) % 70);
            for (let i = 0; i < 7; i++)
                px(cr, i === 0 ? '#fff8e6' : '#c7ccff', 1 - i / 8, x0 + (fase - i) * 5, y0 + (fase - i) * 2.4);
        }
    }

    _pintaDelante(cr, pack = this._packPrim) {
        const t = this.tick, D = pack.D, T = pack.T, nf = this.nocheF;
        cr.setOperator(Cairo.Operator.CLEAR); cr.paint(); cr.setOperator(Cairo.Operator.OVER);

        if (T.modo_heroe === 'miles_morales') {
            pintaFerry(cr, t, nf);
            pintaMiles(cr, t, nf);
        }

        if (D.chimenea) {
            const [hx, hy] = D.chimenea;
            for (let i = 0; i < 9; i++) {
                const fase = ((t * 0.25 + i * 5) % 45) / 45;
                const sx = hx + Math.sin(t * 0.06 + i * 1.4) * (1.5 + fase * 5) + fase * 4;
                const sy = hy - fase * 26;
                const sz = fase < 0.35 ? 2 : 3;
                const op = (1 - fase) * (0.28 + 0.16 * nf);
                px(cr, this.wB > 0.5 ? T.color_humo_dia : T.color_humo_noche, op, sx, sy, sz, sz - 1);
            }
        }

        if (nf > 0.02) {
            D.ventanas.forEach((v, i) => {
                const p = nf * (((Math.floor(t / 24) + i) % 13 === 0) ? 0.25
                    : 0.7 + 0.3 * Math.sin(t * 0.09 * (1 + (i % 4) * 0.15) + i * 2.1));
                px(cr, T.color_ventanas, 0.12 * p, v[0] - 1, v[1] - 1, 4, 6);
                px(cr, T.color_ventanas, p, v[0], v[1], 2, 4);
            });
            D.faroles.forEach((fr, i) => {
                const p = nf * (0.65 + 0.35 * Math.sin(t * 0.11 + i * 1.7));
                const g = Math.max(2, Math.round(fr[2] / 3));
                px(cr, T.color_faroles_halo, 0.06 * p, fr[0] - g * 2, fr[1] - g * 2, g * 4 + 1, g * 4 + 1);
                px(cr, T.color_faroles_halo, 0.14 * p, fr[0] - g, fr[1] - g, g * 2 + 1, g * 2 + 1);
                px(cr, T.color_faroles_centro, p, fr[0], fr[1], 1, 2);
            });
            if (D.runas) {
                const pr = (0.35 + 0.65 * nf) * (0.65 + 0.35 * Math.sin(t * 0.08));
                for (let i = 0; i < D.runas.length; i++) {
                    const rn = D.runas[i];
                    const pulse = pr * (0.75 + 0.25 * Math.sin(t * 0.12 + i * 0.4));
                    px(cr, T.color_runas_halo, 0.14 * pulse, rn[0] - 1, rn[1] - 1, 3, 3);
                    px(cr, T.color_runas_centro, pulse, rn[0], rn[1], 1, 1);
                }
            }
        }
        for (const o of this.olas) {
            px(cr, o[5] ? T.color_olas[0] : T.color_olas[1],
                (0.08 + 0.55 * Math.max(0, Math.sin(t * 0.04 + o[3]))) * (1 - 0.6 * this.wB),
                o[0] + 6 * Math.sin(t * o[4] + o[3]), o[1], o[2], 1);
        }
        const conAstro = !this._packSec || pack !== this._packSec;
        const co = this.cuerpoOp;
        if (conAstro && co > 0.02) {
            const col = this.elev > -1 ? T.color_reflejo_sol : T.color_reflejo_luna;
            for (let i = 0; i < 38; i++) {
                const d = 8 + i * 3, w = Math.max(3, 46 - d * 0.30);
                px(cr, col, co * (0.75 - d * 0.005) * this.osc(0.07, i * 1.7),
                    this.cuerpoX - w / 2 + 3 * Math.sin(t * 0.05 + i * 1.3), 280 + d, w * (0.45 + 0.55 * this.osc(0.09, i * 2.2)), 1);
            }
            const dx = this.cuerpoX - 352;
            D.destellos.forEach((ds, i) => {
                const o = co * Math.pow(Math.max(0, Math.sin(t * 0.16 + i * 0.9)), 3);
                if (o > 0.004) px(cr, T.color_destello, o, ds[0] + dx, ds[1], 2, 1);
            });
        }
        const esBrasas = T.modo_particulas === 'brasas_mana';
        this.hojas.forEach((p, i) => {
            const esMana = p[5] === 3;
            const ax = (p[0] + t * p[3] + 18 * Math.sin(t * 0.03 + p[4])) % 660 - 10;
            const dirY = (esMana || esBrasas) ? -p[2] * 0.45 : p[2];
            const ay = ((p[1] + t * dirY) % 420 + 420) % 420 - 10;
            if (ay >= 395) return;
            if (esMana) {
                const mOp = (0.25 + 0.75 * nf) * (0.45 + 0.55 * Math.sin(t * 0.11 + i));
                px(cr, T.color_mana_halo, 0.25 * mOp, ax - 1, ay - 1, 3, 3);
                px(cr, T.color_mana_centro, mOp, ax, ay, 1, 1);
            } else if (esBrasas) {
                const bOp = (0.35 + 0.65 * nf) * (0.5 + 0.5 * Math.sin(t * 0.13 + i));
                px(cr, T.colores_hojas[p[5] % T.colores_hojas.length], bOp, ax, ay, 1, 1);
            } else {
                const h = Math.floor(t / 7 + i) % 2;
                px(cr, T.colores_hojas[p[5] % T.colores_hojas.length], 0.92, ax, ay, h ? 2 : 1, h ? 1 : 2);
            }
        });
        if (nf > 0.25) {
            MOTAS_MANA.forEach((lc, i) => {
                const fx = lc[0] + 9 * Math.sin(t * (0.021 + i * 0.002) + i * 2.3);
                const fy = lc[1] + 5 * Math.sin(t * (0.017 + i * 0.0015) + i * 1.1);
                const b = nf * Math.pow(Math.max(0, Math.sin(t * (0.05 + i * 0.004) + i * 1.9)), 2);
                const halo = T.color_fuegos_halo[i % T.color_fuegos_halo.length];
                const core = T.color_fuegos_centro[i % T.color_fuegos_centro.length];
                px(cr, halo, 0.28 * b, fx - 1, fy - 1, 3, 3);
                px(cr, core, 0.2 + 0.8 * b, fx, fy, 1, 1);
            });
        }
    }

    pausa(p) {
        if (p === this._pausa) return;
        this._pausa = p;
        if (!p) { this.recalcula(); this.pinta(); }
        this._programa();
    }

    destroy() {
        if (this._timer) GLib.source_remove(this._timer);
        this._timer = 0;
        this.destruyeMonitores();
    }
}
