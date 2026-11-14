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

function pintaDemonRengoku(cr, t, nf) {
    const imp = Math.pow(Math.max(0, Math.sin(t * 0.28)), 4);
    const clashTick = t % 24;
    const clash = clashTick < 5 ? 1 - clashTick / 5 : 0;
    const env = 0.65 + 0.35 * nf;

    px(cr, '#ff5820', (0.07 + 0.11 * imp) * env, 286, 266, 94, 46);
    px(cr, '#38d8ff', (0.07 + 0.11 * imp) * env, 404, 268, 96, 46);
    if (clash > 0.05) {
        const rC = Math.round(14 + (1 - clash) * 18);
        px(cr, '#ffe8a0', 0.16 * clash * env, 418 - rC, 284 - Math.round(rC * 0.7), rC * 2, Math.round(rC * 1.4));
    }
    for (let i = 0; i < 8; i++) {
        const fx = 306 + i * 3;
        const fy = 287 + Math.round(i * 0.3 + Math.sin(t * 0.55 + i * 0.85) * 1.8);
        const fh = 5 + ((Math.floor(t * 0.6) + i * 3) % 5);
        px(cr, '#ff3624', 0.82, fx, fy + fh - 3, 2, 3);
        px(cr, '#ff7e24', 0.88, fx, fy + 2, 2, 3);
        px(cr, '#ffd84c', 0.90, fx, fy, 2, 2);
    }
    for (let k = 0; k < 6; k++) {
        const lift = ((t * 1.6 + k * 7) % 18);
        const ax = 324 + ((k * 7) % 21) + Math.round(Math.sin(t * 0.4 + k) * 2);
        px(cr, k % 2 === 0 ? '#ffd84c' : '#ff5e24', Math.max(0.15, (1 - lift / 18) * 0.85), ax, 294 - Math.round(lift), 2, 2);
    }
    const bPos = (t * 2) % 20;
    px(cr, '#fff8d8', 0.95, 342 + bPos, 292 - Math.floor(bPos / 4), 3, 1);

    for (let step = 0; step < 19; step++) {
        const u = step / 18;
        const pulseU = ((t * 0.11 + u * 2.2) % 1.0);
        const bx = Math.round(356 + u * 64);
        const by = Math.round(288 - Math.sin(u * Math.PI * 0.85) * 18 + Math.sin(u * 9.0 - t * 0.65) * 3.2);
        const rad = 3 + ((step + Math.floor(t * 0.5)) % 3);
        px(cr, '#ff2a18', 0.42, bx - rad - 1, by - rad - 1, (rad + 1) * 2, (rad + 1) * 2);
        px(cr, '#ff7e24', 0.84, bx - rad, by - rad, rad * 2, rad * 2);
        px(cr, pulseU > 0.62 ? '#fff8c8' : '#ffd84c', 0.94, bx - 1, by - 1, 3, 3);
        const angR = t * 0.5 + step * 0.8;
        px(cr, '#ffe888', 0.80, bx + Math.round(Math.cos(angR) * 4), by + Math.round(Math.sin(angR) * 6), 2, 2);
    }
    const jaw = Math.sin(t * 0.45) > 0 ? 1 : 0;
    px(cr, '#fff8d0', 0.96, 417, 281 - jaw, 6, 3);
    px(cr, '#ff7e24', 0.92, 421, 278 - jaw, 5, 2);
    px(cr, '#ff3624', 0.90, 421, 286 + jaw, 5, 2);

    const rot = t * 0.065;
    for (let p = 0; p < 12; p++) {
        const ang = rot + (p * Math.PI * 2) / 12;
        const cA = Math.cos(ang), sA = Math.sin(ang);
        for (let r = 14; r <= 42; r += 4) {
            const rx = Math.round(456 + cA * r);
            const ry = Math.round(312 + sA * (r * 0.18));
            const esPunta = r >= 36;
            px(cr, esPunta ? '#ffffff' : (r >= 26 ? '#92f0ff' : '#38d8ff'), esPunta ? 0.95 : 0.78, rx, ry, esPunta ? 2 : 1, 1);
        }
    }
    px(cr, '#ffd84c', 0.95, 450, 284, 1, 1);
    px(cr, '#ffd84c', 0.95, 454, 284, 1, 1);
    for (let k = 0; k < 4; k++) {
        const prog = ((t * 0.13 + k * 0.25) % 1.0);
        const ax = Math.round(446 - prog * 28);
        const ay = Math.round(288 + ((k % 2 === 0 ? -1 : 1) * 5) + Math.sin(t * 0.4 + k) * 2);
        px(cr, '#38d8ff', 0.85, ax, ay - 3, 4, 7);
        px(cr, '#d8385c', 0.72, ax + 2, ay - 2, 3, 5);
        px(cr, '#ffffff', 0.95, ax - 1, ay - 1, 2, 3);
    }
    for (let rIdx = 0; rIdx < 2; rIdx++) {
        const rad = 4 + ((t * 2 + rIdx * 7) % 14);
        const opRing = Math.max(0.15, (1 - (rad - 4) / 14) * 0.9);
        for (let i = 0; i < 16; i++) {
            const a = (i * Math.PI * 2) / 16 + t * 0.08;
            const sx = Math.round(418 + Math.cos(a) * rad);
            const sy = Math.round(284 + Math.sin(a) * rad * 0.75);
            px(cr, sx < 418 ? '#ffd84c' : '#38d8ff', opRing, sx, sy, 2, 1);
        }
    }
    for (let b = 0; b < 6; b++) {
        if ((t + b) % 3 === 0) continue;
        const ba = t * 0.37 + b * 1.05;
        const bl = 7 + ((t * 3 + b * 5) % 10);
        const colB = b % 2 === 0 ? '#ffe898' : '#78ecff';
        for (let s = 2; s <= bl; s += 2) {
            px(cr, colB, 0.88, 418 + Math.round(Math.cos(ba) * s) + Math.round(Math.sin(s + t + b) * 1.4), 284 + Math.round(Math.sin(ba) * s * 0.8), 1, 1);
        }
    }
    if (clash > 0.2) px(cr, '#ffffff', 0.98 * clash, 416, 282, 5, 5);
    const fPulse = 0.7 + 0.3 * (0.5 + 0.5 * Math.sin(t * 0.22 + 0.4));
    px(cr, '#ff8438', 0.22 * fPulse * env, 141, 222, 14, 9);
    for (let i = 1; i <= 34; i += 2) {
        const rh = 1 + Math.floor(i / 6);
        px(cr, '#ffe898', Math.max(0.03, (0.36 - i * 0.009) * fPulse * env), 225 + i, 238 - rh, 2, rh * 2);
    }
}

function pintaDemonTokito(cr, t, nf) {
    const env = 0.65 + 0.35 * nf;
    for (let i = 0; i < 6; i++) {
        const bx = 185 + ((Math.round(t * (1.2 + (i % 3) * 0.5)) + i * 64) % 350);
        const by = 288 + (i % 3) * 11 + Math.round(Math.sin(t * 0.12 + i) * 2);
        const bw = 28 + (i % 3) * 14;
        px(cr, '#54e8cc', 0.16 * env, bx, by, bw, 3);
        px(cr, '#b8fff4', 0.22 * env, bx + 6, by + 1, Math.round(bw * 0.6), 1);
    }
    for (let h = 0; h < 5; h++) {
        px(cr, h > 2 ? '#d8fff8' : '#74f0dc', 0.85, 259 + h * 3, 283 + h + Math.round(Math.sin(t * 0.45 + h) * 1.4), 2, 2);
    }
    const bladeS = (t * 2) % 18;
    px(cr, '#e8fffc', 0.95, 287 + bladeS, 285 - Math.floor(bladeS / 4), 3, 1);
    for (let a = 0; a < 3; a++) {
        const prog = ((t * 0.10 + a * 0.33) % 1.0);
        const sx = Math.round(304 + prog * 144);
        const sy = Math.round(284 + Math.sin(prog * Math.PI * 2 + a) * 9);
        for (let dy = -6; dy <= 6; dy += 2) {
            const arch = Math.round((dy * dy) / 7);
            px(cr, '#54e8cc', 0.72, sx - arch, sy + dy, 3, 2);
            if (Math.abs(dy) <= 3) px(cr, '#e8fffc', 0.92, sx - arch + 1, sy + dy, 2, 1);
        }
    }
    const flashTick = t % 28;
    if (flashTick < 9) {
        const fAl = 1 - flashTick / 9;
        px(cr, '#54e8cc', 0.18 * fAl * env, 424, 260, 56, 42);
        for (let d = -14; d <= 14; d += 2) {
            px(cr, '#74f8e8', 0.86 * fAl, 444 + d, 280 + Math.round(d * 0.65), 2, 2);
            px(cr, '#ffffff', 0.95 * fAl, 444 + d, 280 - Math.round(d * 0.65), 2, 2);
        }
    }
    for (const side of [-1, 1]) {
        for (let seg = 0; seg < 12; seg++) {
            const u = seg / 11;
            const wave = Math.sin(t * 0.42 + u * 4.5 + side) * (2.5 + u * 3.5);
            const tx = Math.round(468 + side * (13 + seg * 2.5));
            const ty = Math.round(294 - Math.sin(u * 3.6) * 14 - u * 9 + wave);
            const rt = u < 0.5 ? 2 : 1;
            px(cr, '#2898a8', 0.75, tx - rt, ty - rt, rt * 2 + 1, rt * 2 + 1);
            px(cr, '#98fff0', 0.86, tx, ty, rt, rt);
        }
        if ((t + (side > 0 ? 1 : 0)) % 2 === 0) {
            px(cr, '#d8fffc', 0.88, 468 + side * (36 + (t % 5)), 266 + Math.round(Math.cos(t * 0.5 + side) * 4), 2, 2);
        }
    }
    px(cr, '#ff4878', 0.92, 467, 270, 2, 2);
    px(cr, '#ffd858', 0.90, 467, 275, 2, 1);
    for (let j = 0; j < 3; j++) {
        const gp = ((t * 0.12 + j * 0.33) % 1.0);
        const gx = Math.round(452 - gp * 60);
        const gy = Math.round(278 + (j - 1) * 5 + Math.sin(t * 0.5 + j) * 2);
        px(cr, '#54e4d4', 0.86, gx, gy, 5, 1);
        px(cr, '#ff5488', 0.80, gx + 4, gy, 2, 1);
    }
    if (t % 3 !== 0) {
        px(cr, '#ffffff', 0.90, 391, 279, 3, 3);
        px(cr, '#ff6494', 0.80, 394 + (t % 4) - 2, 275 + ((t * 2) % 6), 2, 2);
    }
}

function pintaDemonGlicinias(cr, t, nf) {
    const env = 0.65 + 0.35 * nf;
    const wCols = ['#c884ff', '#f0d8ff', '#9248e8', '#e6b8ff'];
    for (let i = 0; i < 20; i++) {
        const py = 116 + ((Math.round(t * (0.45 + (i % 4) * 0.18)) + i * 19) % 218);
        const px0 = 36 + ((Math.round(t * (0.25 + (i % 3) * 0.12) + Math.sin(t * 0.08 + i) * 14) + i * 31) % 568);
        const horiz = (Math.floor(t / 5) + i) % 2 === 0;
        px(cr, wCols[i % 4], 0.82 * env, px0, py, horiz ? 2 : 1, horiz ? 1 : 2);
    }
    for (let g = 0; g < 10; g++) {
        const gx = g < 4 ? (52 + g * 44) : g < 8 ? (418 + (g - 4) * 44) : (276 + (g - 8) * 86);
        const gy = g < 8 ? (136 + (g % 3) * 14) : 150;
        px(cr, '#f0d8ff', (0.35 + 0.65 * (0.5 + 0.5 * Math.sin(t * 0.16 + g * 1.3))) * env, gx, gy, 2, 2);
    }
    const pulseF = 0.72 + 0.28 * (0.5 + 0.5 * Math.sin(t * 0.24 + 0.7));
    px(cr, '#ff7828', 0.16 * pulseF * env, 300, 266, 50, 24);
    for (let k = 0; k < 9; k++) {
        const kx = 307 + k * 4;
        const kyBase = 285 - Math.floor((k * 4 + 13) / 5);
        const fh = 3 + ((Math.floor(t * 0.7) + k * 3) % 7);
        const sway = Math.round(Math.sin(t * 0.5 + k * 0.9) * 1.2);
        px(cr, '#ff3820', 0.78, kx + sway, kyBase - fh, 2, 3);
        px(cr, '#ff9428', 0.88, kx, kyBase - Math.max(2, fh - 2), 2, 3);
        px(cr, '#fff4b8', 0.95, kx, kyBase - 1, 2, 2);
    }
    for (let e = 0; e < 5; e++) {
        const rise = ((t * 1.2 + e * 9) % 34);
        px(cr, e % 2 === 0 ? '#ffe888' : '#ff9838', Math.max(0.1, (1 - rise / 34) * 0.88),
            310 + ((e * 11) % 30) + Math.round(Math.sin(t * 0.2 + e * 1.7) * 4), 280 - Math.round(rise), 1, 2);
    }
}

function pintaNarutoBaryon(cr, t, nf) {
    const env = 0.68 + 0.32 * nf;
    const kPulse = 0.5 + 0.5 * Math.sin(t * 0.26);

    for (const ex of [121, 154]) {
        px(cr, '#ff2c18', 0.48 * kPulse * env, ex - 4, 173, 8, 5);
        px(cr, '#ff9430', 0.88, ex - 2, 174, 5, 3);
        px(cr, '#fff0a8', 0.96, ex, 174, 2, 2);
    }
    for (let w = 0; w < 4; w++) {
        const wy = 192 + w * 4 - ((t + w * 2) % 6);
        px(cr, '#ff5a24', 0.36 * env, 130 + ((w * 7) % 16), wy, 2, 3);
    }

    for (let k = 0; k < 9; k++) {
        const baseAng = -2.42 + k * 0.24;
        const len = 64 + (k % 3) * 18;
        for (let s = 2; s < 10; s++) {
            const u = s / 10;
            const sway = Math.sin(t * 0.34 + k * 0.9 + u * 3.1) * (4 + u * 8);
            const tx = Math.round(192 + Math.cos(baseAng) * (len * u) + sway * 0.45);
            const ty = Math.round(314 + Math.sin(baseAng) * (len * u) + sway * 0.3);
            if (tx < 48 || tx > 258 || ty < 178 || ty > 342) continue;
            const tip = s > 7;
            px(cr, tip ? '#ffd068' : (s % 2 === 0 ? '#ff3c24' : '#ff7c2c'), (0.28 + 0.36 * (1 - u)) * env, tx, ty, tip ? 2 : 3, 2);
        }
    }

    for (let p = 0; p < 7; p++) {
        const rise = ((t * 1.7 + p * 5) % 28);
        const ax = 188 + ((p * 5) % 20) + Math.round(Math.sin(t * 0.45 + p) * 2);
        const ay = 340 - Math.round(rise);
        px(cr, rise > 18 ? '#ff2c1c' : '#ff9c38', Math.max(0.12, (1 - rise / 28) * 0.78), ax, ay, 2, 2);
    }
    px(cr, '#ffe088', 0.85, 188, 300 + (t % 2), 1, 2);
    px(cr, '#ffe088', 0.85, 204, 300 + ((t + 1) % 2), 1, 2);

    const rPulse = 0.65 + 0.35 * Math.sin(t * 0.65);
    px(cr, '#ff4020', 0.35 * rPulse, 214, 314, 13, 13);
    px(cr, '#ff9e3c', 0.80, 217, 317, 7, 7);
    px(cr, '#fff6dc', 0.96, 219, 319, 3, 3);
    for (let r = 0; r < 4; r++) {
        const ra = t * 0.55 + r * (Math.PI / 2);
        px(cr, r % 2 === 0 ? '#ffe898' : '#ff4c28', 0.92,
            220 + Math.round(Math.cos(ra) * 5.2), 320 + Math.round(Math.sin(ra) * 5.2), 2, 2);
    }

    if (t % 4 !== 0) {
        const cxm = 258 + ((t * 7) % 48);
        const cym = 304 - Math.round((cxm - 258) * 0.4) + Math.round(Math.sin(t * 0.9) * 5);
        px(cr, '#ffd878', 0.90, cxm, cym, 3, 1);
        px(cr, '#ff4828', 0.72, cxm - 2, cym + 1, 2, 1);
    }

    const cubos = [[322, 280, 7], [290, 294, 5], [346, 266, 4]];
    for (let i = 0; i < cubos.length; i++) {
        const bob = Math.round(Math.sin(t * 0.24 + i * 2.1) * 3);
        const cx = cubos[i][0];
        const cy = cubos[i][1] + bob;
        const sz = cubos[i][2];
        const flash = ((t + i * 11) % 36) < 4;
        px(cr, flash ? '#ffb8ff' : '#c044ff', (flash ? 0.78 : 0.46) * env, cx - sz, cy - sz, sz * 2, 1);
        px(cr, '#8828c8', 0.36 * env, cx - sz, cy + sz - 1, sz * 2, 1);
    }

    for (let s = 0; s < 8; s++) {
        const wa = t * 0.14 + (s * Math.PI) / 4;
        px(cr, s % 2 === 0 ? '#ffe878' : '#ffffff', 0.75 * env,
            Math.round(394 + Math.cos(wa) * 23), Math.round(282 + Math.sin(wa) * 23), 2, 2);
    }
    px(cr, '#c848ff', 0.42 * kPulse * env, 387, 308, 5, 3);
}

function pintaNarutoKonoha(cr, t, nf) {
    const env = 0.60 + 0.40 * nf;
    const flagBob = Math.round(Math.sin(t * 0.35) * 1.2);
    px(cr, '#d84030', 0.85, 220, 224 + flagBob, 5, 2);
    px(cr, '#f8e8c8', 0.65 * env, 217, 228, 3, 1);

    const sway = Math.round(Math.sin(t * 0.22) * 1.1);
    for (const lx of [46, 66, 88]) {
        px(cr, '#ff5232', 0.75 * env, lx + sway, 255, 3, 4);
        px(cr, '#ffe8a0', 0.50 * env, lx + sway, 256, 1, 2);
    }
    for (let v = 0; v < 4; v++) {
        const vr = ((t * 1.1 + v * 6) % 20);
        px(cr, '#f0f4f8', Math.max(0.08, (1 - vr / 20) * 0.42),
            66 + Math.round(Math.sin(t * 0.2 + v) * 2), 248 - Math.round(vr), 2, 2);
    }

    const cloakW = Math.round(Math.sin(t * 0.30) * 1.4);
    px(cr, '#ff7828', 0.82, 338 + cloakW, 265, 3, 4);
    px(cr, '#fff4e4', 0.78, 344 + cloakW, 261, 3, 3);
    px(cr, '#383058', 0.80, 372 - cloakW, 263, 3, 5);
    if (nf > 0.3) px(cr, '#c870ff', 0.70 * env, 368, 256, 1, 1);

    for (let i = 0; i < 7; i++) {
        const lx = 36 + ((Math.round(t * (1.3 + (i % 3) * 0.45)) + i * 59) % 404);
        const ly = 135 + (i % 4) * 32 + Math.round(Math.sin(t * 0.18 + i * 1.4) * 7);
        const lCol = nf > 0.55 ? '#4ca868' : (i % 2 === 0 ? '#74d05c' : '#e89844');
        px(cr, lCol, 0.72, lx, ly, 2, 2);
    }

    for (let r = 0; r < 10; r++) {
        if ((t + r) % 3 === 0) continue;
        const rx = 44 + ((r * 39 + t * 2) % 390);
        const ry = 287 + (r % 5) * 9;
        px(cr, nf > 0.55 ? '#98c8ff' : '#fff0b8', 0.42 * env, rx, ry, 4 + (r % 3) * 2, 1);
    }
}

function pintaNarutoValle(cr, t, nf) {
    const env = 0.65 + 0.35 * nf;

    for (let l = 0; l < 6; l++) {
        const wx = 250 + l * 13;
        const off = (t * 4 + l * 21) % 120;
        for (let k = 0; k < 3; k++) {
            const wy = 154 + ((off + k * 42) % 120);
            px(cr, k === 0 ? '#ffffff' : '#b8eeff', 0.62 * env, wx, wy, 2, 6);
        }
    }
    for (let m = 0; m < 8; m++) {
        const mx = 242 + m * 11 + Math.round(Math.sin(t * 0.25 + m) * 2);
        const my = 275 + ((t + m * 3) % 5);
        px(cr, '#e8fbff', 0.52 * env, mx, my, 5, 3);
    }

    const clash = 0.6 + 0.4 * Math.sin(t * 0.6);
    px(cr, '#48c4ff', 0.32 * clash, 271, 242, 12, 12);
    px(cr, '#d8f8ff', 0.90, 275, 246, 5, 5);
    for (let s = 0; s < 4; s++) {
        const sa = t * 0.65 + s * (Math.PI / 2);
        px(cr, '#80e4ff', 0.92, 277 + Math.round(Math.cos(sa) * 4), 248 + Math.round(Math.sin(sa) * 4), 2, 2);
    }

    px(cr, '#a8d4ff', 0.32 * clash, 285, 241, 14, 14);
    for (let b = 0; b < 5; b++) {
        if ((t + b) % 3 === 0) continue;
        const ba = t * 0.48 + b * 1.25;
        const bl = 5 + ((t * 2 + b * 3) % 8);
        for (let d = 2; d <= bl; d += 2) {
            const j = Math.round(Math.sin(d + t + b) * 1.4);
            px(cr, b % 2 === 0 ? '#ffffff' : '#b8b0ff', 0.92,
                291 + Math.round(Math.cos(ba) * d) + j, 248 + Math.round(Math.sin(ba) * d), 1, 1);
        }
    }

    px(cr, '#ffffff', 0.96 * clash, 282, 246, 5, 5);
    const ringR = 5 + ((t * 2) % 20);
    const ringAl = Math.max(0.08, (1 - (ringR - 5) / 20) * 0.72);
    for (let a = 0; a < 12; a++) {
        const ang = (a * Math.PI * 2) / 12 + t * 0.1;
        px(cr, a % 2 === 0 ? '#88e8ff' : '#ffffff', ringAl,
            284 + Math.round(Math.cos(ang) * ringR), 248 + Math.round(Math.sin(ang) * ringR * 0.8), 2, 2);
    }

    px(cr, '#ff9838', 0.65 * clash, 253, 255 - (t % 3), 2, 3);
    px(cr, '#9880ff', 0.65 * clash, 314, 255 - ((t + 1) % 3), 2, 3);

    const poolW = 10 + ((t * 2) % 18);
    px(cr, '#90e8ff', 0.40 * clash, 284 - poolW, 315, poolW * 2, 2);
    px(cr, '#ffffff', 0.55 * clash, 279, 316, 10, 1);
}

function pintaJujutsu(cr, t, nf) {
    const al = 0.55 + 0.45 * nf;
    const pulse = 0.72 + 0.28 * Math.sin(t * 0.14);

    for (let a = 0; a < 10; a++) {
        const ang = (a * Math.PI * 2) / 10 + t * 0.06;
        const rX = 36 + Math.round(Math.sin(t * 0.1 + a) * 2);
        px(cr, a % 2 === 0 ? '#7dd3fc' : '#c084fc', 0.68 * al, 446 + Math.round(Math.cos(ang) * rX), 146 + Math.round(Math.sin(ang) * 12), 2, 1);
    }
    px(cr, '#ffffff', 0.42 * al * pulse, 444, 145, 4, 2);

    const eyeAl = (0.55 + 0.45 * Math.sin(t * 0.16)) * al;
    px(cr, '#fb7185', 0.88 * eyeAl, 125, 189, 2, 2);
    px(cr, '#fb7185', 0.88 * eyeAl, 139, 189, 2, 2);
    px(cr, '#ff2848', 0.55 * al, 120, 232 + (t % 3 === 0 ? -1 : 0), 24, 2);
    for (let s = 0; s < 5; s++) {
        const sy = 188 + ((s * 17 + t * 3) % 68);
        const sx = 98 + ((s * 29) % 68);
        px(cr, s % 2 === 0 ? '#ff4468' : '#fda4af', 0.72 * al, sx, sy, 5, 1);
    }

    px(cr, '#fb7185', 0.60 * al, 214, 314 - (t % 3), 2, 4);
    px(cr, '#ef4444', 0.60 * al, 224, 318 - ((t + 1) % 3), 2, 4);
    for (let k = 0; k < 4; k++) {
        const prog = ((t * 3 + k * 7) % 36);
        const sx0 = 242 + prog;
        const sy0 = 294 + ((k * 7) % 18) - Math.round(prog * 0.18);
        for (let d = 0; d < 7; d++) {
            px(cr, d > 4 ? '#ffffff' : '#ff3355', 0.88 * al, sx0 + d, sy0 + (k % 2 === 0 ? d >> 1 : -(d >> 1)), 1, 1);
        }
    }

    px(cr, '#38bdf8', 0.68 * al, 396, 316 - ((t + 2) % 3), 2, 4);
    const rOrb = 10 + Math.round(Math.sin(t * 0.2) * 2);
    const rAng = t * 0.22;
    px(cr, '#fb7185', 0.90 * al, 306 + Math.round(Math.cos(rAng) * rOrb), 298 + Math.round(Math.sin(rAng) * rOrb * 0.6), 3, 3);
    px(cr, '#38bdf8', 0.90 * al, 306 - Math.round(Math.cos(rAng) * rOrb), 298 - Math.round(Math.sin(rAng) * rOrb * 0.6), 3, 3);

    const coreR = Math.round(4 + 3 * pulse);
    px(cr, '#9333ea', 0.40 * al, 306 - coreR - 4, 298 - coreR - 2, coreR * 2 + 8, coreR * 2 + 4);
    px(cr, '#e879f9', 0.72 * al, 306 - coreR, 298 - coreR, coreR * 2, coreR * 2);
    px(cr, '#fdf4ff', 0.96 * al, 304, 296, 5, 5);

    const wave = 8 + ((t * 2) % 24);
    const wAl = Math.max(0.08, (1 - (wave - 8) / 24) * 0.75 * al);
    for (let a = 0; a < 12; a++) {
        const ang = (a * Math.PI * 2) / 12 + t * 0.08;
        px(cr, a % 2 === 0 ? '#e879f9' : '#7dd3fc', wAl, 306 + Math.round(Math.cos(ang) * wave), 298 + Math.round(Math.sin(ang) * wave * 0.7), 2, 2);
    }

    const rw = 12 + Math.round(4 * pulse);
    px(cr, '#c084fc', 0.42 * al, 306 - rw, 342, rw * 2, 2);
}

function pintaJujutsuSec(cr, t, nf) {
    const al = 0.58 + 0.42 * nf;
    const bob = Math.round(Math.sin(t * 0.12) * 2);

    px(cr, '#eab308', 0.45 * al, 306, 274 + bob, 16, 16);
    if (t % 29 !== 0) {
        px(cr, '#fff8e8', 0.92 * al, 312, 280 + bob, 4, 4);
        px(cr, '#e11d48', 0.95 * al, 313, 281 + bob, 2, 2);
    }
    for (let c = 0; c < 4; c++) {
        const ang = c * Math.PI * 0.5 + t * 0.07;
        px(cr, '#facc15', 0.78 * al, 314 + Math.round(Math.cos(ang) * 14), 282 + bob + Math.round(Math.sin(ang) * 11), 2, 2);
    }

    const bfPulse = (t % 16) < 4;
    px(cr, '#09090b', 0.90, 184, 320, 7, 7);
    px(cr, bfPulse ? '#ffffff' : '#fb7185', 0.92 * al, 186, 322, 3, 3);
    for (let b = 0; b < 6; b++) {
        const ang = t * 0.45 + b * 1.05;
        const dist = 5 + ((t * 2 + b * 3) % 10);
        px(cr, b % 2 === 0 ? '#e11d48' : '#111827', 0.88, 187 + Math.round(Math.cos(ang) * dist), 323 + Math.round(Math.sin(ang) * dist), 2, 1);
    }

    for (let s = 0; s < 5; s++) {
        const sy = 342 - ((t * 2 + s * 6) % 24);
        const sx = 398 + Math.round(Math.sin(t * 0.1 + s) * 8) + (s - 2) * 4;
        px(cr, s % 2 === 0 ? '#38bdf8' : '#1e293b', 0.72 * al, sx, sy, 2, 2);
    }
    px(cr, '#38bdf8', 0.90 * al, 446, 314, 2, 1);
    if ((t % 14) < 3) px(cr, '#bae6fd', 0.86 * al, 388 + (t % 5), 202, 2, 14);
}

function pintaJujutsuBloq(cr, t, nf) {
    const al = 0.58 + 0.42 * nf;
    const sway = Math.round(Math.sin(t * 0.09) * 1.5);

    for (const ox of [284, 298, 312, 328, 342, 356]) {
        px(cr, '#fef3c7', 0.88 * al, ox + sway, 162, 2, 5);
        px(cr, '#ef4444', 0.78 * al, ox + sway, 164, 1, 2);
    }

    const pulse = 0.65 + 0.35 * Math.sin(t * 0.14);
    px(cr, '#e11d48', 0.38 * al * pulse, 313, 283, 14, 14);
    px(cr, '#fb7185', 0.88 * al * pulse, 318, 287 + (t % 6 < 3 ? 0 : -1), 4, 7);
    px(cr, '#fef2f2', 0.88 * al, 319, 288, 2, 2);

    for (let w = 0; w < 6; w++) {
        const prog = (t * 1.2 + w * 9) % 42;
        const wx = 290 + w * 12 + Math.round(Math.sin(t * 0.08 + w) * 3);
        const wy = 306 - Math.round(prog);
        px(cr, w % 2 === 0 ? '#a855f7' : '#f43f5e', Math.max(0.15, (1 - prog / 42) * 0.80 * al), wx, wy, 2, 2);
    }
    for (const [fx, fy] of [[228, 236], [412, 236], [182, 310], [458, 310]]) {
        px(cr, '#fef08a', 0.65 * al * (0.7 + 0.3 * Math.sin(t * 0.2 + fx)), fx - 1, fy - 1, 3, 3);
    }
}

function pintaAotRumbling(cr, t, nf) {
    const al = 0.58 + 0.42 * nf;
    const pulse = 0.70 + 0.30 * Math.sin(t * 0.14);
    px(cr, '#4ade80', 0.92 * al * pulse, 289, 134, 2, 2);
    px(cr, '#4ade80', 0.92 * al * pulse, 297, 134, 2, 2);
    const txs = [48, 124, 218, 376, 450, 174];
    for (let i = 0; i < 6; i++) {
        const py = 248 - ((t * 2 + i * 11) % 52);
        const pxX = txs[i] + Math.round(Math.sin(t * 0.08 + i) * 6);
        px(cr, i % 2 === 0 ? '#fb923c' : '#cbd5e1', 0.55 * al, pxX, py, 3, 2);
    }
    for (let a = 0; a < 8; a++) {
        const ang = (a * Math.PI * 2) / 8 + t * 0.42;
        px(cr, a % 2 === 0 ? '#f8fafc' : '#38bdf8', 0.85 * al, 392 + Math.round(Math.cos(ang) * 18), 322 + Math.round(Math.sin(ang) * 14), 3, 2);
    }
    px(cr, '#ef4444', 0.85 * al, 206 + (t % 3) - 1, 315, 6, 2);
}

function pintaAotShiganshina(cr, t, nf) {
    const al = 0.60 + 0.40 * nf;
    const pulse = 0.65 + 0.35 * Math.sin(t * 0.18);
    px(cr, '#fef08a', 0.92 * al * pulse, 190, 116, 3, 2);
    px(cr, '#fef08a', 0.92 * al * pulse, 212, 116, 3, 2);
    if ((t % 18) < 5) {
        for (let k = 0; k < 8; k++) {
            px(cr, k % 2 === 0 ? '#fef08a' : '#f97316', 0.88 * al, 200 + Math.round(Math.sin(t + k) * 6), 24 + k * 9, 2, 7);
        }
    }
    for (let s = 0; s < 5; s++) {
        const sy = 194 - ((t + s * 9) % 34);
        px(cr, '#e2e8f0', 0.40 * al, 148 + s * 28 + Math.round(Math.sin(t * 0.06 + s) * 4), sy, 6, 3);
    }
    px(cr, '#ef4444', 0.80 * al, 320 + Math.round(Math.sin(t * 0.2) * 3), 270 - (t % 8), 2, 4);
}

function pintaAotPaths(cr, t, nf) {
    const al = 0.60 + 0.40 * nf;
    const pulse = 0.70 + 0.30 * Math.sin(t * 0.11);
    px(cr, '#e0f2fe', 0.45 * al * pulse, 316, 134, 8, 120);
    for (let i = 0; i < 8; i++) {
        const gy = 250 - ((t * 2 + i * 16) % 140);
        const gx = 320 + Math.round(Math.sin(t * 0.09 + i * 1.3) * (gy < 140 ? 38 : 7));
        px(cr, i % 2 === 0 ? '#fde047' : '#67e8f9', 0.82 * al, gx, gy, 2, 2);
    }
    px(cr, '#f8fafc', 0.72 * al * pulse, 319, 312, 2, 6);
}

function pintaOpGear5(cr, t, nf) {
    const al = 0.60 + 0.40 * nf;
    const pulse = 0.68 + 0.32 * Math.sin(t * 0.16);
    for (let h = 0; h < 6; h++) {
        const ang = t * 0.32 + h * 1.04;
        const dist = 8 + ((t * 2 + h * 4) % 16);
        px(cr, h % 2 === 0 ? '#f43f5e' : '#09090b', 0.90 * al, 212 + Math.round(Math.cos(ang) * dist), 322 + Math.round(Math.sin(ang) * dist), 2, 2);
    }
    const rC = Math.round(5 + 3 * pulse);
    px(cr, '#fb923c', 0.65 * al, 308 - rC, 276 - rC, rC * 2, rC * 2);
    px(cr, '#ffffff', 0.94 * al, 306, 274, 4, 4);
    px(cr, '#fef08a', 0.90 * al * pulse, 352, 199, 2, 2);
    for (let f = 0; f < 5; f++) {
        const u = ((t * 0.12 + f * 0.2) % 1.0);
        px(cr, u < 0.5 ? '#ef4444' : '#fde047', 0.88 * al, Math.round(338 - u * 30), Math.round(214 + u * 62), 3, 3);
    }
}

function pintaOpSunny(cr, t, nf) {
    const al = 0.55 + 0.45 * nf;
    const bob = Math.round(Math.sin(t * 0.08));
    for (const lx of [276, 332]) px(cr, '#fef08a', 0.78 * al, lx - 1, 233 + bob, 3, 3);
    px(cr, '#4ade80', 0.85 * al, 291, 215 + bob, 3, 3);
    px(cr, '#38bdf8', 0.85 * al, 313, 215 + bob, 3, 3);
    px(cr, '#e0f2fe', 0.50 * al, 256 + ((t * 2) % 92), 282, 12, 1);
}

function pintaOpPoneglyph(cr, t, nf) {
    const al = 0.58 + 0.42 * nf;
    for (let g = 0; g < 6; g++) {
        const idx = (t + g * 5) % 24;
        px(cr, '#fde047', 0.85 * al, 180 + (idx % 5) * 7, 248 + Math.floor(idx / 5) * 14, 2, 2);
    }
    for (let m = 0; m < 4; m++) {
        const ang = t * 0.16 + m * 1.57;
        px(cr, '#e879f9', 0.82 * al, 404 + Math.round(Math.cos(ang) * 13), 318 + Math.round(Math.sin(ang) * 9), 2, 2);
    }
}

function pintaDbzUi(cr, t, nf) {
    const al = 0.62 + 0.38 * nf;
    const pulse = 0.70 + 0.30 * Math.sin(t * 0.2);
    for (let u = 0; u < 6; u++) {
        const uy = 344 - ((t * 2 + u * 7) % 36);
        px(cr, u % 2 === 0 ? '#e0f2fe' : '#38bdf8', 0.85 * al, 202 + Math.round(Math.sin(t * 0.25 + u) * 14), uy, 2, 3);
    }
    px(cr, '#38bdf8', 0.78 * al * pulse, 232 + (t % 12) * 5, 315 - (t % 12) * 1.4, 8, 3);
    const sr = Math.round(5 + 3 * pulse);
    px(cr, '#f97316', 0.65 * al, 386 - sr, 296 - sr, sr * 2, sr * 2);
    px(cr, '#fef08a', 0.92 * al * pulse, 302, 296, 5, 5);
}

function pintaDbzNamek(cr, t, nf) {
    const al = 0.58 + 0.42 * nf;
    const activeIdx = Math.floor(t / 4) % 7;
    for (let b = 0; b < 7; b++) {
        px(cr, b === activeIdx ? '#ffffff' : '#fde047', (b === activeIdx ? 0.95 : 0.55) * al, 239 + b * 16, 274, 3, 3);
    }
    px(cr, '#ef4444', 0.90 * al, 282, 120, 2, 2);
    for (let k = 0; k < 5; k++) {
        const ky = 250 - ((t * 3 + k * 24) % 160);
        px(cr, '#fde047', 0.72 * al, 278 + Math.round(Math.sin(t * 0.1 + k) * 18), ky, 2, 5);
    }
}

function pintaDbzKame(cr, t, nf) {
    const al = 0.55 + 0.45 * nf;
    px(cr, '#fef3c7', 0.78 * al, 185, 213, 4, 4);
    px(cr, '#fde047', 0.85 * al * (0.6 + 0.4 * Math.sin(t * 0.14)), 421, 255, 3, 3);
    px(cr, '#fce7f3', Math.max(0.15, (1 - (t % 20) / 20) * 0.50), 206 + Math.round(Math.sin(t * 0.2) * 3), 176 - (t % 20), 3, 2);
    px(cr, '#fde68a', 0.65 * al, 234 + (t % 16), 130, 2, 2);
}

function pintaCyberSandevistan(cr, t, nf) {
    const al = 0.60 + 0.40 * nf;
    const cols = ['#4ade80', '#22d3ee', '#f43f5e'];
    for (let s = 0; s < 3; s++) px(cr, cols[s], 0.52 * al, 178 + s * 16 - ((t + s) % 3), 314, 10, 14);
    px(cr, '#22d3ee', 0.90 * al, 227, 316 + (t % 4), 2, 6);
    const mU = ((t * 3) % 40) / 40;
    px(cr, '#fde047', 0.92 * al, Math.round(370 - mU * 82), Math.round(328 - Math.sin(mU * Math.PI * 1.35) * 26), 3, 2);
    px(cr, '#ef4444', 0.80 * al * (0.7 + 0.3 * Math.sin(t * 0.25)), 40, 319, 6, 2);
    px(cr, '#38bdf8', 0.82 * al, (92 + (t * 2)) % 460, 116, 4, 2);
}

function pintaCyberMoon(cr, t, nf) {
    const al = 0.58 + 0.42 * nf;
    px(cr, '#38bdf8', 0.85 * al, ((96 + t * 2) % 440), 221, 18, 3);
    for (const bx of [42, 148, 240, 396]) px(cr, (t + bx) % 16 < 8 ? '#38bdf8' : '#f472b6', 0.88 * al, bx, 259, 2, 2);
    for (let p = 0; p < 4; p++) px(cr, '#bae6fd', 0.72 * al, 300 + p * 10 + Math.round(Math.sin(t * 0.1 + p) * 4), 290 - ((t + p * 8) % 30), 2, 2);
}

function pintaCyberBloq(cr, t, nf) {
    const al = 0.60 + 0.40 * nf;
    const activeSeg = Math.floor(t / 2) % 7;
    for (let s = 0; s < 7; s++) {
        px(cr, s === activeSeg ? '#ffffff' : (s % 2 === 0 ? '#22d3ee' : '#4ade80'), (s === activeSeg ? 0.96 : 0.68) * al, 285 + s * 11, 315, 3, 5);
    }
    if ((t % 19) !== 0) px(cr, '#f43f5e', 0.78 * al, 96, 166, 72, 1);
    px(cr, '#4ade80', 0.60 * al * (0.6 + 0.4 * Math.sin(t * 0.15)), 316, 194, 8, 8);
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
        } else if (T.modo_heroe === 'demon_rengoku') {
            pintaDemonRengoku(cr, t, nf);
        } else if (T.modo_heroe === 'demon_tokito') {
            pintaDemonTokito(cr, t, nf);
        } else if (T.modo_heroe === 'demon_glicinias') {
            pintaDemonGlicinias(cr, t, nf);
        } else if (T.modo_heroe === 'naruto_baryon') {
            pintaNarutoBaryon(cr, t, nf);
        } else if (T.modo_heroe === 'naruto_konoha') {
            pintaNarutoKonoha(cr, t, nf);
        } else if (T.modo_heroe === 'naruto_valle') {
            pintaNarutoValle(cr, t, nf);
        } else if (T.modo_heroe === 'jujutsu') {
            pintaJujutsu(cr, t, nf);
        } else if (T.modo_heroe === 'jujutsu_sec') {
            pintaJujutsuSec(cr, t, nf);
        } else if (T.modo_heroe === 'jujutsu_bloq') {
            pintaJujutsuBloq(cr, t, nf);
        } else if (T.modo_heroe === 'aot_rumbling') {
            pintaAotRumbling(cr, t, nf);
        } else if (T.modo_heroe === 'aot_shiganshina') {
            pintaAotShiganshina(cr, t, nf);
        } else if (T.modo_heroe === 'aot_paths') {
            pintaAotPaths(cr, t, nf);
        } else if (T.modo_heroe === 'op_gear5') {
            pintaOpGear5(cr, t, nf);
        } else if (T.modo_heroe === 'op_sunny') {
            pintaOpSunny(cr, t, nf);
        } else if (T.modo_heroe === 'op_poneglyph') {
            pintaOpPoneglyph(cr, t, nf);
        } else if (T.modo_heroe === 'dbz_ui') {
            pintaDbzUi(cr, t, nf);
        } else if (T.modo_heroe === 'dbz_namek') {
            pintaDbzNamek(cr, t, nf);
        } else if (T.modo_heroe === 'dbz_kame') {
            pintaDbzKame(cr, t, nf);
        } else if (T.modo_heroe === 'cyber_sandevistan') {
            pintaCyberSandevistan(cr, t, nf);
        } else if (T.modo_heroe === 'cyber_moon') {
            pintaCyberMoon(cr, t, nf);
        } else if (T.modo_heroe === 'cyber_bloq') {
            pintaCyberBloq(cr, t, nf);
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
