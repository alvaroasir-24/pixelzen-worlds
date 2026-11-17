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
const IS_LE = new Uint8Array(new Uint32Array([0x11223344]).buffer)[0] === 0x44;
let _coglCtx = null;

function _getRgb(hex) {
    let c = cacheRgb.get(hex);
    if (!c) {
        const [r, g, b] = hexA(hex);
        c = [r, g, b, (b << 16) | (g << 8) | r];
        cacheRgb.set(hex, c);
    }
    return c;
}

function px(buf, hex, op, ax, ay, aw = 1, ah = 1) {
    if (op <= 0.004) return;
    const sa = op >= 1 ? 255 : Math.round(op * 255);
    if (sa <= 0) return;
    const c = _getRgb(hex);
    const x0 = Math.round(ax);
    const y0 = Math.round(ay);
    const rw = aw <= 1 ? (aw > 0 ? 1 : 0) : Math.round(aw);
    const rh = ah <= 1 ? (ah > 0 ? 1 : 0) : Math.round(ah);
    if (rw <= 0 || rh <= 0) return;
    const xStart = x0 < 0 ? 0 : x0;
    const yStart = y0 < 0 ? 0 : y0;
    const xEnd = x0 + rw > W ? W : x0 + rw;
    const yEnd = y0 + rh > H ? H : y0 + rh;
    if (xStart >= xEnd || yStart >= yEnd) return;

    if (IS_LE && sa === 255) {
        const col32 = ((255 << 24) | c[3]) >>> 0;
        for (let y = yStart; y < yEnd; y++) {
            const row = y * W;
            for (let x = xStart; x < xEnd; x++) buf[row + x] = col32;
        }
        return;
    }

    const sr = c[0], sg = c[1], sb = c[2];
    const colOpaque = IS_LE ? (((sa << 24) | c[3]) >>> 0) : 0;
    const inv = 255 - sa;
    for (let y = yStart; y < yEnd; y++) {
        const row = y * W;
        for (let x = xStart; x < xEnd; x++) {
            const idx = row + x;
            const dst = buf[idx];
            if (dst === 0 && IS_LE) {
                buf[idx] = colOpaque;
                continue;
            }
            if (IS_LE) {
                const da = dst >>> 24;
                if (da === 0 || sa === 255) {
                    buf[idx] = ((sa << 24) | c[3]) >>> 0;
                } else {
                    const dr = dst & 0xff;
                    const dg = (dst >>> 8) & 0xff;
                    const db = (dst >>> 16) & 0xff;
                    if (da === 255) {
                        const r = (sr * sa + dr * inv + 127) / 255 | 0;
                        const g = (sg * sa + dg * inv + 127) / 255 | 0;
                        const b = (sb * sa + db * inv + 127) / 255 | 0;
                        buf[idx] = (0xff000000 | (b << 16) | (g << 8) | r) >>> 0;
                    } else {
                        const aTmp = (da * inv + 127) / 255 | 0;
                        const outA = sa + aTmp;
                        const r = ((sr * sa + dr * aTmp) / outA) | 0;
                        const g = ((sg * sa + dg * aTmp) / outA) | 0;
                        const b = ((sb * sa + db * aTmp) / outA) | 0;
                        buf[idx] = ((outA << 24) | (b << 16) | (g << 8) | r) >>> 0;
                    }
                }
            }
        }
    }
}

function _setContentBytes(cont, bytes, w, h, stride) {
    if (_coglCtx) {
        cont.set_bytes(_coglCtx, bytes, Cogl.PixelFormat.RGBA_8888, w, h, stride);
        return;
    }
    try {
        cont.set_bytes(bytes, Cogl.PixelFormat.RGBA_8888, w, h, stride);
    } catch (_e) {
        _coglCtx = global.stage.context.get_backend().get_cogl_context();
        cont.set_bytes(_coglCtx, bytes, Cogl.PixelFormat.RGBA_8888, w, h, stride);
    }
}

function _pixbufToU32(pb) {
    const w = pb.get_width(), h = pb.get_height(), rs = pb.get_rowstride(), nc = pb.get_n_channels();
    const src = pb.get_pixels();
    const out = new Uint32Array(w * h);
    if (IS_LE && nc === 4 && rs === w * 4 && src.byteOffset % 4 === 0) {
        out.set(new Uint32Array(src.buffer, src.byteOffset, w * h));
        return out;
    }
    let idx = 0;
    for (let y = 0; y < h; y++) {
        let p = y * rs;
        for (let x = 0; x < w; x++) {
            const r = src[p], g = src[p + 1], b = src[p + 2], a = nc === 4 ? src[p + 3] : 255;
            out[idx++] = ((a << 24) | (b << 16) | (g << 8) | r) >>> 0;
            p += nc;
        }
    }
    return out;
}

function _blendLayersU32(dst, base, o1, a255, o2, b255) {
    const n = dst.length;
    const use1 = a255 > 1;
    const use2 = b255 > 1;
    for (let i = 0; i < n; i++) {
        let p = base[i];
        if (use1) {
            const q = o1[i];
            const qa0 = q >>> 24;
            if (qa0 > 0) {
                const sa = a255 >= 254 ? qa0 : ((qa0 * a255 + 127) / 255 | 0);
                if (sa >= 255) {
                    p = (0xff000000 | (q & 0x00ffffff)) >>> 0;
                } else if (sa > 0) {
                    const da = p >>> 24;
                    const sr = q & 0xff, sg = (q >>> 8) & 0xff, sb = (q >>> 16) & 0xff;
                    if (da === 0) {
                        p = ((sa << 24) | (q & 0x00ffffff)) >>> 0;
                    } else if (da === 255) {
                        const inv = 255 - sa;
                        const r = (sr * sa + (p & 0xff) * inv + 127) / 255 | 0;
                        const g = (sg * sa + ((p >>> 8) & 0xff) * inv + 127) / 255 | 0;
                        const b = (sb * sa + ((p >>> 16) & 0xff) * inv + 127) / 255 | 0;
                        p = (0xff000000 | (b << 16) | (g << 8) | r) >>> 0;
                    } else {
                        const aTmp = (da * (255 - sa) + 127) / 255 | 0;
                        const outA = sa + aTmp;
                        const r = ((sr * sa + (p & 0xff) * aTmp) / outA) | 0;
                        const g = ((sg * sa + ((p >>> 8) & 0xff) * aTmp) / outA) | 0;
                        const b = ((sb * sa + ((p >>> 16) & 0xff) * aTmp) / outA) | 0;
                        p = ((outA << 24) | (b << 16) | (g << 8) | r) >>> 0;
                    }
                }
            }
        }
        if (use2) {
            const q = o2[i];
            const qa0 = q >>> 24;
            if (qa0 > 0) {
                const sa = b255 >= 254 ? qa0 : ((qa0 * b255 + 127) / 255 | 0);
                if (sa >= 255) {
                    p = (0xff000000 | (q & 0x00ffffff)) >>> 0;
                } else if (sa > 0) {
                    const da = p >>> 24;
                    const sr = q & 0xff, sg = (q >>> 8) & 0xff, sb = (q >>> 16) & 0xff;
                    if (da === 0) {
                        p = ((sa << 24) | (q & 0x00ffffff)) >>> 0;
                    } else if (da === 255) {
                        const inv = 255 - sa;
                        const r = (sr * sa + (p & 0xff) * inv + 127) / 255 | 0;
                        const g = (sg * sa + ((p >>> 8) & 0xff) * inv + 127) / 255 | 0;
                        const b = (sb * sa + ((p >>> 16) & 0xff) * inv + 127) / 255 | 0;
                        p = (0xff000000 | (b << 16) | (g << 8) | r) >>> 0;
                    } else {
                        const aTmp = (da * (255 - sa) + 127) / 255 | 0;
                        const outA = sa + aTmp;
                        const r = ((sr * sa + (p & 0xff) * aTmp) / outA) | 0;
                        const g = ((sg * sa + ((p >>> 8) & 0xff) * aTmp) / outA) | 0;
                        const b = ((sb * sa + ((p >>> 16) & 0xff) * aTmp) / outA) | 0;
                        p = ((outA << 24) | (b << 16) | (g << 8) | r) >>> 0;
                    }
                }
            }
        }
        dst[i] = p;
    }
}

function _subPixbufToU32(pb, sx, sy, w, h) {
    const rs = pb.get_rowstride(), nc = pb.get_n_channels();
    const src = pb.get_pixels();
    const out = new Uint32Array(w * h);
    let idx = 0;
    for (let y = 0; y < h; y++) {
        let p = (sy + y) * rs + sx * nc;
        for (let x = 0; x < w; x++) {
            const r = src[p], g = src[p + 1], b = src[p + 2], a = nc === 4 ? src[p + 3] : 255;
            out[idx++] = ((a << 24) | (b << 16) | (g << 8) | r) >>> 0;
            p += nc;
        }
    }
    return out;
}

function _packSpriteU32(u32, w, h) {
    let n = 0;
    for (let i = 0; i < u32.length; i++) {
        if ((u32[i] >>> 24) > 0) n++;
    }
    const sx = new Int16Array(n);
    const sy = new Int16Array(n);
    const col = new Uint32Array(n);
    let k = 0;
    for (let y = 0; y < h; y++) {
        const row = y * w;
        for (let x = 0; x < w; x++) {
            const p = u32[row + x];
            if ((p >>> 24) > 0) {
                sx[k] = x;
                sy[k] = y;
                col[k] = p;
                k++;
            }
        }
    }
    return {w, h, n, sx, sy, col};
}

function _blitSpriteOpaqueDst(dst, sp, dx, dy, op255Mul) {
    if (op255Mul <= 1 || sp.n === 0) return;
    const ox = Math.round(dx), oy = Math.round(dy);
    const n = sp.n, sx = sp.sx, sy = sp.sy, col = sp.col;
    const fullOp = op255Mul >= 254;
    for (let k = 0; k < n; k++) {
        const x = ox + sx[k];
        if (x < 0 || x >= W) continue;
        const y = oy + sy[k];
        if (y < 0 || y >= H) continue;
        const idx = y * W + x;
        const q = col[k];
        const qa = q >>> 24;
        const sa = fullOp ? qa : ((qa * op255Mul + 127) / 255 | 0);
        if (sa >= 255) {
            dst[idx] = (0xff000000 | (q & 0x00ffffff)) >>> 0;
        } else if (sa > 0) {
            const p = dst[idx];
            const inv = 255 - sa;
            const r = ((q & 0xff) * sa + (p & 0xff) * inv + 127) / 255 | 0;
            const g = (((q >>> 8) & 0xff) * sa + ((p >>> 8) & 0xff) * inv + 127) / 255 | 0;
            const b = (((q >>> 16) & 0xff) * sa + ((p >>> 16) & 0xff) * inv + 127) / 255 | 0;
            dst[idx] = (0xff000000 | (b << 16) | (g << 8) | r) >>> 0;
        }
    }
}

function _compileOpaqueMask(u32) {
    const len = u32.length;
    const runs = [];
    let alphaCnt = 0;
    let inRun = false, runStart = 0;
    for (let i = 0; i < len; i++) {
        const a = u32[i] >>> 24;
        if (a === 255) {
            if (!inRun) { inRun = true; runStart = i; }
        } else {
            if (inRun) { runs.push(runStart, i); inRun = false; }
            if (a > 0) alphaCnt++;
        }
    }
    if (inRun) runs.push(runStart, len);
    const opaqueRuns = new Int32Array(runs);
    const aIdx = new Int32Array(alphaCnt);
    const aR = new Uint8Array(alphaCnt);
    const aG = new Uint8Array(alphaCnt);
    const aB = new Uint8Array(alphaCnt);
    const aSa = new Uint8Array(alphaCnt);
    const aInv = new Uint8Array(alphaCnt);
    let k = 0;
    for (let i = 0; i < len; i++) {
        const p = u32[i];
        const a = p >>> 24;
        if (a > 0 && a < 255) {
            aIdx[k] = i;
            aR[k] = p & 0xff;
            aG[k] = (p >>> 8) & 0xff;
            aB[k] = (p >>> 16) & 0xff;
            aSa[k] = a;
            aInv[k] = 255 - a;
            k++;
        }
    }
    return {src: u32, opaqueRuns, aIdx, aR, aG, aB, aSa, aInv, alphaCnt};
}

function _applyOpaqueMask(dst, mask) {
    const runs = mask.opaqueRuns, src = mask.src;
    for (let r = 0; r < runs.length; r += 2) {
        const s = runs[r], e = runs[r + 1];
        dst.set(src.subarray(s, e), s);
    }
    const cnt = mask.alphaCnt;
    if (cnt === 0) return;
    const idxArr = mask.aIdx, rArr = mask.aR, gArr = mask.aG, bArr = mask.aB, saArr = mask.aSa, invArr = mask.aInv;
    for (let k = 0; k < cnt; k++) {
        const idx = idxArr[k];
        const p = dst[idx];
        const sa = saArr[k], inv = invArr[k];
        const r = (rArr[k] * sa + (p & 0xff) * inv + 127) / 255 | 0;
        const g = (gArr[k] * sa + ((p >>> 8) & 0xff) * inv + 127) / 255 | 0;
        const b = (bArr[k] * sa + ((p >>> 16) & 0xff) * inv + 127) / 255 | 0;
        dst[idx] = (0xff000000 | (b << 16) | (g << 8) | r) >>> 0;
    }
}

function _blend3CloudU32(n0, op0, n1, op1, n2, op2, w, h) {
    const len = w * h;
    const out = new Uint32Array(len);
    const u0 = op0 > 1, u1 = op1 > 1, u2 = op2 > 1;
    const f0 = op0 >= 254, f1 = op1 >= 254, f2 = op2 >= 254;
    if (u0 && f0 && !u1 && !u2) return _packSpriteU32(n0, w, h);
    if (u1 && f1 && !u0 && !u2) return _packSpriteU32(n1, w, h);
    if (u2 && f2 && !u0 && !u1) return _packSpriteU32(n2, w, h);
    for (let i = 0; i < len; i++) {
        let rr = 0, gg = 0, bb = 0, aa = 0;
        if (u0) {
            const p = n0[i], a = f0 ? (p >>> 24) : (((p >>> 24) * op0 + 127) / 255 | 0);
            if (a > 0) { rr += (p & 0xff) * a; gg += ((p >>> 8) & 0xff) * a; bb += ((p >>> 16) & 0xff) * a; aa += a; }
        }
        if (u1) {
            const p = n1[i], a = f1 ? (p >>> 24) : (((p >>> 24) * op1 + 127) / 255 | 0);
            if (a > 0) { rr += (p & 0xff) * a; gg += ((p >>> 8) & 0xff) * a; bb += ((p >>> 16) & 0xff) * a; aa += a; }
        }
        if (u2) {
            const p = n2[i], a = f2 ? (p >>> 24) : (((p >>> 24) * op2 + 127) / 255 | 0);
            if (a > 0) { rr += (p & 0xff) * a; gg += ((p >>> 8) & 0xff) * a; bb += ((p >>> 16) & 0xff) * a; aa += a; }
        }
        if (aa > 0) {
            const oa = aa > 255 ? 255 : aa;
            const r = Math.min(255, (rr / aa) | 0);
            const g = Math.min(255, (gg / aa) | 0);
            const b = Math.min(255, (bb / aa) | 0);
            out[i] = ((oa << 24) | (b << 16) | (g << 8) | r) >>> 0;
        }
    }
    return _packSpriteU32(out, w, h);
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

const _TEMA_DEFECTO_FB = {
    cielo_fondo: '#0a0c24', modo_pajaros: 'grullas', color_pajaros: '#120c26',
    modo_particulas: 'hojas_mana', colores_hojas: ['#a4d86c', '#6ec05a', '#d8b45c', '#5cf2e4'],
    color_mana_halo: '#5cf2e4', color_mana_centro: '#b8fff6',
    color_fuegos_halo: ['#f0cf68', '#40e4dc'], color_fuegos_centro: ['#fff2b0', '#b2fff6'],
    color_ventanas: '#f4bc68', color_faroles_halo: '#f4bc68', color_faroles_centro: '#fff0c0',
    color_runas_halo: '#4bece2', color_runas_centro: '#9efcf4',
    color_humo_dia: '#e6ecf2', color_humo_noche: '#9aaec4',
    color_olas: ['#9cd4d8', '#5882b0'], color_reflejo_sol: '#ffe6a0',
    color_reflejo_luna: '#f4ead2', color_destello: '#fff6e2',
};

function _cargarTemaDefecto(dir) {
    for (const p of [`${dir}/code/worlds_meta.json`, `${dir}/../../src/worlds_meta.json`]) {
        try {
            if (GLib.file_test(p, GLib.FileTest.EXISTS)) {
                const raw = JSON.parse(new TextDecoder().decode(GLib.file_get_contents(p)[1]));
                if (raw && raw.tema_defecto) return {..._TEMA_DEFECTO_FB, ...raw.tema_defecto};
            }
        } catch (_e) { /* respaldo minimo */ }
    }
    return _TEMA_DEFECTO_FB;
}

function _cargarHeroes(dir) {
    for (const p of [`${dir}/code/pixelzen-heroes.js`, `${dir}/../../src/pixelzen-heroes.js`]) {
        try {
            if (GLib.file_test(p, GLib.FileTest.EXISTS)) {
                const src = new TextDecoder().decode(GLib.file_get_contents(p)[1]);
                const factory = new Function(`${src}\nreturn createPixelZenHeroes;`)();
                return factory(px);
            }
        } catch (e) {
            logError(e, 'PixelZen heroes');
        }
    }
    return {ALAS_GRULLA: [], ALAS_WYVERN: [], MOTAS_MANA: [], pintaHeroeAtras: () => {}, pintaHeroe: () => {}};
}

export class Escena {
    constructor(dir, contenedor, settings) {
        this._dir = dir;
        this._cont = contenedor;
        this._settings = settings;
        this._monitores = [];
        this._timer = 0;
        this._pausa = false;
        this._oculta = false;
        this.tick = 0;
        this.lat = 40.4;
        this.lon = -3.7;
        this.climaMode = 'normal';
        this.realClimaEfecto = '';
        this.eventoTipo = '';
        this.eventoInicioTick = -999;
        this.eventoDuracion = 96;
        this._ultimaHoraEvento = -1;
        this._lastClimaCheck = 0;

        let n = lcg(7);
        this.olas = [];
        for (let i = 0; i < 44; i++)
            this.olas.push([300 + Math.floor(n() * 260), 286 + Math.floor(n() * 108), 3 + Math.floor(n() * 11), n() * 6.28, 0.03 + n() * 0.05, n() < 0.35]);
        n = lcg(21);
        this.hojas = [];
        for (let i = 0; i < 42; i++)
            this.hojas.push([n() * 640, n() * 400, 0.30 + n() * 0.42, 0.06 + n() * 0.12, n() * 6.28, Math.floor(n() * 4)]);

        this._temaDefecto = _cargarTemaDefecto(dir);
        this._heroes = _cargarHeroes(dir);
        this._cargaDatosYTexturas();
        this._leeAjustes();
        this._leeClimaCache();
        this.recalcula();
    }

    _resuelveVarianteDir(temaId, variante) {
        const id = temaId || 'fittoa';
        const base = `${this._dir}/temas/${id}`;
        if (!GLib.file_test(`${base}/datos.json`, GLib.FileTest.EXISTS)) return this._dir;
        const sub = variante === 'secundaria' ? 'secundario' : (variante === 'bloqueo' ? 'bloqueo' : '');
        if (sub && GLib.file_test(`${base}/${sub}/datos.json`, GLib.FileTest.EXISTS)) {
            return `${base}/${sub}`;
        }
        return base;
    }

    _leeClimaCache() {
        const ahora = Date.now();
        if (ahora - this._lastClimaCheck < 60000) return;
        this._lastClimaCheck = ahora;
        try {
            const p = GLib.build_filenamev([GLib.get_user_config_dir(), 'pixelzen', 'clima_real.json']);
            if (GLib.file_test(p, GLib.FileTest.EXISTS)) {
                const raw = JSON.parse(new TextDecoder().decode(GLib.file_get_contents(p)[1]));
                if (raw && raw.ok && raw.efecto) this.realClimaEfecto = String(raw.efecto);
            }
        } catch (_e) { /* sin cache */ }
    }

    _cargaPack(dir) {
        const D = JSON.parse(new TextDecoder().decode(
            GLib.file_get_contents(`${dir}/datos.json`)[1]));
        const brillantes = D.estrellas.filter(e => e[3] === 1);
        let T;
        try {
            const raw = JSON.parse(new TextDecoder().decode(
                GLib.file_get_contents(`${dir}/tema.json`)[1]));
            T = {...this._temaDefecto, ...raw};
        } catch (e) {
            T = {...this._temaDefecto};
        }

        const img = f => GdkPixbuf.Pixbuf.new_from_file(`${dir}/images/${f}.png`);
        const pxLayers = {};
        for (const f of ['cielo-noche', 'cielo-dorado', 'cielo-dia', 'escena-noche', 'escena-dorado', 'escena-dia']) {
            pxLayers[f] = _pixbufToU32(img(f));
        }
        const solPb = img('sol');
        const lunaPb = img('luna');
        const solSp = _packSpriteU32(_pixbufToU32(solPb), solPb.get_width(), solPb.get_height());
        const lunaSp = _packSpriteU32(_pixbufToU32(lunaPb), lunaPb.get_width(), lunaPb.get_height());

        const nubesPx = {};
        for (const fase of ['noche', 'dorado', 'dia']) {
            const hoja = img(`nubes-${fase}`);
            nubesPx[fase] = D.nubes.map(nb => _subPixbufToU32(hoja, 0, nb[4], nb[2], nb[3]));
        }
        const escenaMasks = {
            noche: _compileOpaqueMask(pxLayers['escena-noche']),
            dorado: _compileOpaqueMask(pxLayers['escena-dorado']),
            dia: _compileOpaqueMask(pxLayers['escena-dia']),
        };
        return {D, T, brillantes, pxLayers, solSp, lunaSp, nubesPx, escenaMasks};
    }

    _cargaDatosYTexturas() {
        const s = this._settings;
        const temaId = s?.get_string('tema') || 'fittoa';
        const fp = s?.get_string('fondo-principal') || 'principal';
        const fs = s?.get_string('fondo-secundario') || 'secundaria';
        const ts = s?.get_string('tema-secundario') || 'igual';
        const temaSec = (ts && ts !== 'igual') ? ts : temaId;

        const dirPrim = this._resuelveVarianteDir(temaId, fp);
        const prim = this._cargaPack(dirPrim);
        this.D = prim.D;
        this.T = prim.T;
        this.brillantes = prim.brillantes;
        this._packPrim = prim;

        const dirSec = this._resuelveVarianteDir(temaSec, fs);
        if (dirSec !== dirPrim && GLib.file_test(`${dirSec}/datos.json`, GLib.FileTest.EXISTS)) {
            try {
                this._packSec = this._cargaPack(dirSec);
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
        this.fps = Math.max(4, Math.min(30, s.get_int('fps')));
        this.horaSim = s.get_double('hora-simulada');
        this.demo = s.get_boolean('ciclo-rapido');
        this.duracionCiclo = Math.max(10, s.get_int('ciclo-duracion'));
        try {
            this.climaMode = s.get_string('clima') || 'normal';
        } catch (_e) {
            this.climaMode = 'normal';
        }
    }

    ajustesCambiados() {
        const prevAnim = this.animar;
        const prevFps = this.fps;
        this._leeAjustes();
        this.recalcula();
        if (!this.animar || !prevAnim || prevFps !== this.fps) {
            this.pinta();
            this._programa();
        }
    }

    actualizaHoraSimulada() {
        this.horaSim = this._settings.get_double('hora-simulada');
        this.recalcula();
        if (!this.animar) this.pinta();
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
    osc(f, p) { return 0.5 + 0.5 * Math.sin((this.tickFloat ?? this.tick) * f + p); }

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
        const l = {pack};
        const raiz = new Clutter.Actor({width: W, height: H});
        l.raiz = raiz;
        l.frameU8 = new Uint8Array(W * H * 4);
        l.frameU32 = new Uint32Array(l.frameU8.buffer);
        l.frameCont = St.ImageContent.new_with_preferred_size(W, H);
        l.frameActor = imagen(raiz, l.frameCont, W, H);
        l.cieloStarsU32 = new Uint32Array(W * H);
        l.escenaDynU32 = new Uint32Array(W * H);
        l.escenaDynMask = null;
        l.lastSkyKey = '';
        l.lastEscKey = '';
        l.lastNubKey = '';
        l.nubesSprites = [];
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
        if (this._oculta) raiz.visible = false;
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
        if (this._pausa || this._oculta || !this._lienzo) return;
        if (!this._t0Us) {
            this._t0Us = GLib.get_monotonic_time();
            this._lastSlowUs = this._t0Us;
        }
        if (!this.animar) {
            this._timer = GLib.timeout_add(GLib.PRIORITY_DEFAULT, 60000, () => {
                this.recalcula();
                this.pinta();
                return GLib.SOURCE_CONTINUE;
            });
            return;
        }
        const intervalUs = Math.round(1000000 / this.fps);
        let nextUs = GLib.get_monotonic_time() + intervalUs;
        const step = () => {
            this._timer = 0;
            if (this._pausa || this._oculta || !this._lienzo || !this.animar) return GLib.SOURCE_REMOVE;
            const nowUs = GLib.get_monotonic_time();
            this.tickFloat = (nowUs - this._t0Us) * 10.0 / 1000000.0;
            this.tick = Math.floor(this.tickFloat);
            if (this.demo || (nowUs - this._lastSlowUs) >= 1000000) {
                this._lastSlowUs = nowUs;
                this.recalcula();
                this._leeClimaCache();
                const dNow = new Date();
                if (dNow.getMinutes() === 0 && dNow.getSeconds() < 3 && this._ultimaHoraEvento !== dNow.getHours()) {
                    this._ultimaHoraEvento = dNow.getHours();
                    this.disparaEvento('');
                }
            }
            this.pinta();
            const afterUs = GLib.get_monotonic_time();
            nextUs += intervalUs;
            if (nextUs < afterUs) nextUs = afterUs + intervalUs;
            const delayMs = Math.max(4, Math.round((nextUs - afterUs) / 1000));
            this._timer = GLib.timeout_add(GLib.PRIORITY_DEFAULT, delayMs, step);
            return GLib.SOURCE_REMOVE;
        };
        this._timer = GLib.timeout_add(GLib.PRIORITY_DEFAULT, Math.max(4, Math.round(intervalUs / 1000)), step);
    }

    disparaEvento(tipo = '') {
        const ops = ['cometa', 'invocacion', 'anomalia'];
        this.eventoTipo = tipo || ops[Math.abs(this.tick) % ops.length];
        this.eventoInicioTick = this.tick;
        this.pinta();
    }

    _climaEfectivo(fecha) {
        const m = this.climaMode || 'normal';
        if (m !== 'auto') return m;
        if (this.realClimaEfecto) return this.realClimaEfecto;
        const temaId = this._settings?.get_string('tema') || 'fittoa';
        const h = fecha.getHours();
        if ((temaId === 'spiderman-miles-morales' && (h >= 20 || h < 5)) || temaId === 'cyberpunk-edgerunners') return 'lluvia';
        if (temaId === 'stranger-things' && (h % 2 === 1)) return 'tormenta';
        if (temaId === 'dragon-ball-z' && (h % 3 === 0)) return 'tormenta';
        if (temaId === 'attack-on-titan') return 'ceniza';
        if (temaId === 'demon-slayer' || temaId === 'harry-potter' || temaId === 'jujutsu-kaisen') return 'niebla';
        if (temaId === 'fittoa' && (h < 7 || h >= 22)) return 'niebla';
        return 'normal';
    }

    _pintaEventoEspecial(cr, t) {
        if (!this.eventoTipo) return;
        const age = t - this.eventoInicioTick;
        if (age < 0 || age > this.eventoDuracion) { this.eventoTipo = ''; return; }
        const p = age / this.eventoDuracion;
        const env = p < 0.15 ? p / 0.15 : (p > 0.8 ? (1.0 - p) / 0.2 : 1.0);
        if (this.eventoTipo === 'cometa') {
            const cx = 60 + p * 520;
            const cy = 28 + p * 125 - Math.sin(p * Math.PI) * 18;
            for (let k = 0; k < 18; k++) {
                const tx = cx - k * 3.6;
                const ty = cy - k * 1.1;
                const a = (1 - k / 18) * 0.85 * env;
                const c = k < 4 ? '#ffffff' : (k < 10 ? '#fde047' : '#38bdf8');
                px(cr, c, a, tx, ty, k < 5 ? 3 : 2, k < 5 ? 2 : 1);
            }
            px(cr, '#ffffff', 0.98 * env, cx - 1, cy - 1, 4, 4);
        } else if (this.eventoTipo === 'invocacion') {
            for (let a = 0; a < 16; a++) {
                const ang = (a * Math.PI * 2) / 16 + t * 0.08;
                px(cr, a % 2 === 0 ? '#facc15' : '#38bdf8', 0.82 * env, 320 + Math.round(Math.cos(ang) * 34), 224 + Math.round(Math.sin(ang) * 14), 2, 2);
            }
            for (const colX of [302, 320, 338]) {
                px(cr, '#facc15', 0.22 * env, colX - 1, 56, 3, 224);
                px(cr, '#ffffff', 0.50 * env, colX, 76, 1, 204);
            }
            px(cr, '#38bdf8', 0.35 * env, 296, 314, 48, 3);
        } else if (this.eventoTipo === 'anomalia') {
            for (let i = -24; i <= 24; i += 2) {
                const y = 148 + i;
                const x = 320 + Math.round(Math.sin(i * 0.35 + t * 0.25) * 6);
                px(cr, '#09090b', 0.85 * env, x - 2, y, 5, 2);
                px(cr, i % 4 === 0 ? '#e11d48' : '#a855f7', 0.90 * env, x - 3, y, 2, 2);
                px(cr, '#f43f5e', 0.90 * env, x + 2, y, 2, 2);
            }
            for (let r = 0; r < 10; r++) {
                const ang = r * 0.62 + t * 0.14;
                const rad = 14 + (age % 22);
                px(cr, r % 2 === 0 ? '#f43f5e' : '#c084fc', 0.72 * env, 320 + Math.round(Math.cos(ang) * rad), 148 + Math.round(Math.sin(ang) * rad * 0.7), 2, 1);
            }
        }
    }

    _pintaClima(cr, t, wB, nf, fecha) {
        const modo = this._climaEfectivo(fecha);
        if (modo === 'normal') return;
        if (modo === 'lluvia' || modo === 'tormenta') {
            const pesado = modo === 'tormenta';
            const wind = pesado ? -2.2 : -1.0;
            const vyBase = pesado ? 1.55 : 1.0;
            const col = pesado ? '#bae6fd' : '#7dd3fc';
            const alphaBase = (pesado ? 0.56 : 0.42) * (1.0 - 0.15 * wB);
            for (let i = 0; i < 84; i++) {
                if (!pesado && i % 3 === 2) continue;
                const x0 = (i * 53 + 17) % 640;
                const y0 = (i * 89 + 31) % 390;
                const len = Math.round((5 + (i % 4) * 2) * (pesado ? 1.35 : 1.0));
                const sp = 6 + (i % 3);
                const gx = (((x0 + t * wind * 2.2) % 640) + 640) % 640;
                const gy = (y0 + t * sp * vyBase) % 390;
                for (let d = 0; d < len; d++) {
                    px(cr, col, alphaBase * (1.0 - d * 0.08), gx + (wind < -1.5 ? -Math.floor(d * 0.4) : 0), gy + d, 1, 1);
                }
                if (gy > 282 && gy < 386 && i % 7 === 0) {
                    const rw = 2 + (((t | 0) + i) % 3);
                    px(cr, '#e0f2fe', 0.30 * alphaBase, gx - rw, gy + 1, rw * 2, 1);
                }
            }
            if (pesado) {
                const ti = t | 0;
                const flash = (ti * 17 + 13) % 131;
                if (flash < 2) {
                    px(cr, '#e0f2fe', flash === 0 ? 0.22 : 0.10, 0, 0, 640, 280);
                    const lx = 110 + ((ti * 97) % 420);
                    for (let y = 8; y < 230; y += 4) {
                        const jx = lx + Math.round(Math.sin(y * 0.18 + t) * 7);
                        px(cr, '#ffffff', 0.92, jx, y, 2, 4);
                        px(cr, col, 0.45, jx - 1, y, 4, 4);
                    }
                }
            }
        } else if (modo === 'nieve') {
            const alphaBase = 0.72 + 0.20 * nf;
            for (let i = 0; i < 68; i++) {
                const x0 = (i * 61 + 29) % 640;
                const y0 = (i * 97 + 13) % 390;
                const sp = 0.75 + (i % 4) * 0.35;
                const sz = (i % 5 === 0) ? 2 : 1;
                const sx = (((x0 + Math.sin(t * 0.04 + i * 0.7) * 14 + t * 0.15) % 640) + 640) % 640;
                const sy = (y0 + t * sp) % 394;
                px(cr, i % 4 === 0 ? '#e0f2fe' : '#ffffff', alphaBase, sx, sy, sz, sz);
            }
        } else if (modo === 'ceniza') {
            const alphaBase = 0.64 + 0.25 * nf;
            for (let i = 0; i < 68; i++) {
                const x0 = (i * 61 + 29) % 640;
                const y0 = (i * 97 + 13) % 390;
                const sp = 0.75 + (i % 4) * 0.35;
                const sz = (i % 5 === 0) ? 2 : 1;
                const sx = (((x0 + t * 0.45 + Math.sin(t * 0.05 + i * 0.7) * 10) % 640) + 640) % 640;
                const sy = (((y0 - t * sp * 0.85) % 394) + 394) % 394;
                const cc = (i % 5 === 0) ? '#fb923c' : ((i % 2 === 0) ? '#fed7aa' : '#94a3b8');
                px(cr, cc, alphaBase, sx, sy, sz, 1);
            }
        } else if (modo === 'niebla') {
            const col = wB > 0.5 ? '#f8fafc' : '#cbd5e1';
            for (let i = 0; i < 6; i++) {
                const mx = (((i * 120 + t * (0.25 + (i % 3) * 0.12)) % 760) + 760) % 760 - 120;
                const my = 252 + i * 14;
                const mw = 95 + (i % 3) * 45;
                px(cr, col, 0.09 + 0.06 * nf, mx, my, mw, 5);
                px(cr, col, 0.05 + 0.04 * nf, mx + 16, my - 2, mw - 32, 2);
            }
        }
    }

    _pintaLienzo(l) {
        if (!l) return;
        const P = l.pack, D = P.D, L = P.pxLayers;
        const t = this.tick, tf = this.tickFloat ?? t, ef = this.estrellaF;
        const noche = this.elev < 0;
        const a255 = op255(this.wA);
        const b255 = op255(this.wB);
        const efKey = ef > 0.01 ? Math.round(ef * 255) : 0;

        // 1) Cachear cielo + estrellas estáticas cuando cambia fase solar o efKey
        const skyKey = `${a255}:${b255}:${efKey}`;
        if (l.lastSkyKey !== skyKey) {
            l.lastSkyKey = skyKey;
            if (b255 >= 254) l.cieloStarsU32.set(L['cielo-dia']);
            else if (a255 >= 254 && b255 <= 1) l.cieloStarsU32.set(L['cielo-dorado']);
            else if (a255 <= 1 && b255 <= 1) l.cieloStarsU32.set(L['cielo-noche']);
            else _blendLayersU32(l.cieloStarsU32, L['cielo-noche'], L['cielo-dorado'], a255, L['cielo-dia'], b255);

            if (efKey > 0) {
                const est = D.estrellas;
                for (let i = 0; i < est.length; i++) {
                    if (i % 3 !== 0) {
                        const e = est[i];
                        px(l.cieloStarsU32, e[2], ef, e[0], e[1]);
                    }
                }
            }
        }

        // 2) Cachear máscara de escena cuando cambia fase solar
        const escKey = `${a255}:${b255}`;
        if (l.lastEscKey !== escKey) {
            l.lastEscKey = escKey;
            if (b255 >= 254) l.escenaMask = P.escenaMasks.dia;
            else if (a255 >= 254 && b255 <= 1) l.escenaMask = P.escenaMasks.dorado;
            else if (a255 <= 1 && b255 <= 1) l.escenaMask = P.escenaMasks.noche;
            else {
                _blendLayersU32(l.escenaDynU32, L['escena-noche'], L['escena-dorado'], a255, L['escena-dia'], b255);
                l.escenaMask = _compileOpaqueMask(l.escenaDynU32);
            }
        }

        // 3) Cachear sprites de nubes mezclados por fase solar
        const o0 = op255(noche ? 1 - this.wA : 0);
        const o1 = op255(noche ? this.wA : 1 - this.wB);
        const o2 = op255(this.wB);
        const nubKey = `${o0}:${o1}:${o2}`;
        if (l.lastNubKey !== nubKey) {
            l.lastNubKey = nubKey;
            const NP = P.nubesPx;
            const list = new Array(D.nubes.length);
            for (let i = 0; i < D.nubes.length; i++) {
                const nb = D.nubes[i];
                list[i] = _blend3CloudU32(NP.noche[i], o0, NP.dorado[i], o1, NP.dia[i], o2, nb[2], nb[3]);
            }
            l.nubesSprites = list;
        }

        // 4) Ensamblar el cuadro completo en 1 único buffer RGBA opaco
        const dst = l.frameU32;
        dst.set(l.cieloStarsU32);
        this._pintaAtras(dst, P);

        const conAstro = l === this._lienzo;
        if (conAstro) {
            const sop = op255(this.solOp);
            if (sop > 1) _blitSpriteOpaqueDst(dst, P.solSp, this.solX - 104, this.solY - 104, sop);
            const lop = op255(this.lunaOp);
            if (lop > 1) _blitSpriteOpaqueDst(dst, P.lunaSp, this.lunaX - 104, this.lunaY - 104, lop);
        }

        const nubes = D.nubes;
        const nSp = l.nubesSprites;
        for (let i = 0; i < nubes.length; i++) {
            const nb = nubes[i];
            const v = 0.08 + (i % 4) * 0.025;
            const cx = Math.round(((nb[0] + nb[2] + tf * v) % (640 + nb[2])) - nb[2]);
            _blitSpriteOpaqueDst(dst, nSp[i], cx, nb[1], 255);
        }

        this._heroes.pintaHeroeAtras(dst, P.T.modo_heroe, tf, this.nocheF);
        _applyOpaqueMask(dst, l.escenaMask);
        this._pintaDelante(dst, P);
        _setContentBytes(l.frameCont, GLib.Bytes.new(l.frameU8), W, H, W * 4);
    }

    pinta() {
        this._pintaLienzo(this._lienzo);
        this._pintaLienzo(this._lienzo2);
    }

    _pintaAtras(cr, pack = this._packPrim) {
        const t = this.tick, tf = this.tickFloat ?? t, D = pack.D, T = pack.T, brillantes = pack.brillantes, ef = this.estrellaF;
        if (ef > 0.01) {
            const est = D.estrellas;
            for (let i = 0; i < est.length; i += 3) {
                const e = est[i];
                const o = 0.3 + 0.7 * this.osc(0.10 + (i % 7) * 0.02, i * 1.3);
                px(cr, e[2], ef * o, e[0], e[1]);
            }
            for (let i = 0; i < brillantes.length; i++) {
                const e = brillantes[i];
                const o = ef * 0.8 * Math.max(0, this.osc(0.07 + (i % 5) * 0.01, i * 2.1) - 0.55) / 0.45;
                if (o <= 0.004) continue;
                px(cr, '#c7ccff', o, e[0] - 1, e[1]); px(cr, '#c7ccff', o, e[0] + 1, e[1]);
                px(cr, '#c7ccff', o, e[0], e[1] - 1); px(cr, '#c7ccff', o, e[0], e[1] + 1);
            }
        }
        const alas = T.modo_pajaros === 'wyverns' ? this._heroes.ALAS_WYVERN : this._heroes.ALAS_GRULLA;
        const cuadro = [0, 1, 2, 1][Math.floor(t / 5) % 4];
        const b0x = Math.round(((tf * 0.22 + 40) % 760) - 60), b0y = Math.round(126 + 4 * Math.sin(tf * 0.03));
        const b1x = Math.round(((tf * 0.22 + 22) % 760) - 60), b1y = Math.round(116 + 4 * Math.sin(tf * 0.03 + 1));
        const b2x = Math.round(((tf * 0.20 + 5) % 760) - 60), b2y = Math.round(138 + 4 * Math.sin(tf * 0.025 + 2));
        const alasF = alas[cuadro];
        const bCoords = [[b0x, b0y], [b1x, b1y], [b2x, b2y]];
        for (let b = 0; b < 3; b++) {
            const cx = bCoords[b][0], cy = bCoords[b][1];
            for (let k = 0; k < alasF.length; k++) px(cr, T.color_pajaros, 1, cx + alasF[k][0], cy + alasF[k][1]);
            px(cr, T.color_pajaros, 1, cx, cy + 1);
        }
        const periodo = 380;
        const ciclo = Math.floor(t / periodo), fase = t % periodo;
        if (fase < 14 && ef > 0.5) {
            const x0 = 60 + ((ciclo * 137) % 300), y0 = 20 + ((ciclo * 53) % 70);
            for (let i = 0; i < 7; i++)
                px(cr, i === 0 ? '#fff8e6' : '#c7ccff', 1 - i / 8, x0 + (fase - i) * 5, y0 + (fase - i) * 2.4);
        }
    }

    _pintaDelante(cr, pack = this._packPrim) {
        const t = this.tick, tf = this.tickFloat ?? t, D = pack.D, T = pack.T, nf = this.nocheF;

        this._heroes.pintaHeroe(cr, T.modo_heroe, tf, nf, 0);

        if (D.chimenea) {
            const [hx, hy] = D.chimenea;
            for (let i = 0; i < 9; i++) {
                const fase = ((tf * 0.25 + i * 5) % 45) / 45;
                const sx = hx + Math.sin(tf * 0.06 + i * 1.4) * (1.5 + fase * 5) + fase * 4;
                const sy = hy - fase * 26;
                const sz = fase < 0.35 ? 2 : 3;
                const op = (1 - fase) * (0.28 + 0.16 * nf);
                px(cr, this.wB > 0.5 ? T.color_humo_dia : T.color_humo_noche, op, sx, sy, sz, sz - 1);
            }
        }

        if (nf > 0.02) {
            const vens = D.ventanas;
            for (let i = 0; i < vens.length; i++) {
                const v = vens[i];
                const p = nf * (((Math.floor(t / 24) + i) % 13 === 0) ? 0.25
                    : 0.7 + 0.3 * Math.sin(tf * 0.09 * (1 + (i % 4) * 0.15) + i * 2.1));
                px(cr, T.color_ventanas, 0.12 * p, v[0] - 1, v[1] - 1, 4, 6);
                px(cr, T.color_ventanas, p, v[0], v[1], 2, 4);
            }
            const fars = D.faroles;
            for (let i = 0; i < fars.length; i++) {
                const fr = fars[i];
                const p = nf * (0.65 + 0.35 * Math.sin(tf * 0.11 + i * 1.7));
                const g = Math.max(2, Math.round(fr[2] / 3));
                px(cr, T.color_faroles_halo, 0.06 * p, fr[0] - g * 2, fr[1] - g * 2, g * 4 + 1, g * 4 + 1);
                px(cr, T.color_faroles_halo, 0.14 * p, fr[0] - g, fr[1] - g, g * 2 + 1, g * 2 + 1);
                px(cr, T.color_faroles_centro, p, fr[0], fr[1], 1, 2);
            }
            if (D.runas) {
                const pr = (0.35 + 0.65 * nf) * (0.65 + 0.35 * Math.sin(tf * 0.08));
                for (let i = 0; i < D.runas.length; i++) {
                    const rn = D.runas[i];
                    const pulse = pr * (0.75 + 0.25 * Math.sin(tf * 0.12 + i * 0.4));
                    px(cr, T.color_runas_halo, 0.14 * pulse, rn[0] - 1, rn[1] - 1, 3, 3);
                    px(cr, T.color_runas_centro, pulse, rn[0], rn[1], 1, 1);
                }
            }
        }
        const olas = this.olas;
        const olaDay = 1 - 0.6 * this.wB;
        for (let i = 0; i < olas.length; i++) {
            const o = olas[i];
            px(cr, o[5] ? T.color_olas[0] : T.color_olas[1],
                (0.08 + 0.55 * Math.max(0, Math.sin(tf * 0.04 + o[3]))) * olaDay,
                o[0] + 6 * Math.sin(tf * o[4] + o[3]), o[1], o[2], 1);
        }
        const conAstro = !this._packSec || pack !== this._packSec;
        const co = this.cuerpoOp;
        if (conAstro && co > 0.02) {
            const col = this.elev > -1 ? T.color_reflejo_sol : T.color_reflejo_luna;
            for (let i = 0; i < 38; i++) {
                const d = 8 + i * 3, w = Math.max(3, 46 - d * 0.30);
                px(cr, col, co * (0.75 - d * 0.005) * this.osc(0.07, i * 1.7),
                    this.cuerpoX - w / 2 + 3 * Math.sin(tf * 0.05 + i * 1.3), 280 + d, w * (0.45 + 0.55 * this.osc(0.09, i * 2.2)), 1);
            }
            const dx = this.cuerpoX - 352;
            const dest = D.destellos;
            for (let i = 0; i < dest.length; i++) {
                const ds = dest[i];
                const o = co * Math.pow(Math.max(0, Math.sin(tf * 0.16 + i * 0.9)), 3);
                if (o > 0.004) px(cr, T.color_destello, o, ds[0] + dx, ds[1], 2, 1);
            }
        }
        const esBrasas = T.modo_particulas === 'brasas_mana';
        const hojas = this.hojas;
        for (let i = 0; i < hojas.length; i++) {
            const p = hojas[i];
            const esMana = p[5] === 3;
            const ax = (p[0] + tf * p[3] + 18 * Math.sin(tf * 0.03 + p[4])) % 660 - 10;
            const dirY = (esMana || esBrasas) ? -p[2] * 0.45 : p[2];
            const ay = ((p[1] + tf * dirY) % 420 + 420) % 420 - 10;
            if (ay >= 395) continue;
            if (esMana) {
                const mOp = (0.25 + 0.75 * nf) * (0.45 + 0.55 * Math.sin(tf * 0.11 + i));
                px(cr, T.color_mana_halo, 0.25 * mOp, ax - 1, ay - 1, 3, 3);
                px(cr, T.color_mana_centro, mOp, ax, ay, 1, 1);
            } else if (esBrasas) {
                const bOp = (0.35 + 0.65 * nf) * (0.5 + 0.5 * Math.sin(tf * 0.13 + i));
                px(cr, T.colores_hojas[p[5] % T.colores_hojas.length], bOp, ax, ay, 1, 1);
            } else {
                const h = Math.floor(t / 7 + i) % 2;
                px(cr, T.colores_hojas[p[5] % T.colores_hojas.length], 0.92, ax, ay, h ? 2 : 1, h ? 1 : 2);
            }
        }
        if (nf > 0.25) {
            const motas = this._heroes.MOTAS_MANA;
            for (let i = 0; i < motas.length; i++) {
                const lc = motas[i];
                const fx = lc[0] + 9 * Math.sin(tf * (0.021 + i * 0.002) + i * 2.3);
                const fy = lc[1] + 5 * Math.sin(tf * (0.017 + i * 0.0015) + i * 1.1);
                const b = nf * Math.pow(Math.max(0, Math.sin(tf * (0.05 + i * 0.004) + i * 1.9)), 2);
                const halo = T.color_fuegos_halo[i % T.color_fuegos_halo.length];
                const core = T.color_fuegos_centro[i % T.color_fuegos_centro.length];
                px(cr, halo, 0.28 * b, fx - 1, fy - 1, 3, 3);
                px(cr, core, 0.2 + 0.8 * b, fx, fy, 1, 1);
            }
        }
        this._pintaEventoEspecial(cr, tf);
        this._pintaClima(cr, tf, this.wB, nf, this.fechaEfectiva());
    }

    ocultar(o) {
        this._oculta = !!o;
        for (const m of this._monitores) m.raiz.visible = !this._oculta;
        if (!this._oculta && !this._pausa) { this.recalcula(); this.pinta(); }
        this._programa();
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
