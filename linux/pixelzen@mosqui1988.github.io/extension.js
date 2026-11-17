// PixelZen para GNOME Shell: fondo pixel art animado que sigue al sol + panel de datos.
// Port del tema PixelZen de KDE Plasma 6 (https://github.com/mosqui1988/pixelzen). GPL-3.0-or-later.

import GLib from 'gi://GLib';
import Gio from 'gi://Gio';
import Clutter from 'gi://Clutter';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

function _modUri(dir, nombre) {
    const f = Gio.File.new_for_path(`${dir}/${nombre}`);
    let ver = '';
    try {
        const info = f.query_info('time::modified,time::modified-usec', Gio.FileQueryInfoFlags.NONE, null);
        ver = `?v=${info.get_attribute_uint64('time::modified')}_${info.get_attribute_uint32('time::modified-usec')}`;
    } catch (_e) { /* sin mtime */ }
    return `${f.get_uri()}${ver}`;
}

export default class PixelZenExtension extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._ids = [];
        this._timerRot = 0;
        this._activo = true;
        const token = (this._enableToken = (this._enableToken || 0) + 1);
        this._grupo = Main.layoutManager._backgroundGroup;

        this._raiz = new Clutter.Actor({reactive: false});
        this._grupo.add_child(this._raiz);

        this._escena = null;
        this._hud = null;
        this._HudCls = null;

        this._programaRotacion();
        this._timerUbi = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 1800, () => { this._ubicacion(); return GLib.SOURCE_CONTINUE; });
        this._inicia(token);

        const con = (obj, sig, fn) => this._ids.push([obj, obj.connect(sig, fn)]);
        con(Main.layoutManager, 'monitors-changed', () => this._construye());
        con(global.display, 'workareas-changed', () => this._colocaHud());
        con(this._grupo, 'child-added', (_g, hijo) => {
            if (hijo !== this._raiz) this._grupo.set_child_above_sibling(this._raiz, null);
        });
        con(global.display, 'in-fullscreen-changed', () => this._actualizaPausa());
        con(Main.sessionMode, 'updated', () => this._actualizaPausa());
        con(this._settings, 'changed', (_s, clave) => {
            if (clave === 'tema' || clave === 'tema-revision' || clave === 'fondo-principal' || clave === 'fondo-secundario' || clave === 'tema-secundario') {
                this._escena?.recargaTema(this._monitores().filter(Boolean));
                this._hud?.recargaTema();
                this._colocaHud();
                this._grupo.set_child_above_sibling(this._raiz, null);
                if (this._hud) this._raiz.set_child_above_sibling(this._hud.actor, null);
            } else if (clave === 'solo-widgets') {
                this._escena?.ocultar(this._settings.get_boolean('solo-widgets'));
                this._hud?.recargaTema();
                this._colocaHud();
            } else if (clave === 'evento-seq') {
                this._escena?.disparaEvento('');
            } else if (clave === 'rotacion-minutos') {
                this._programaRotacion();
            } else if (clave === 'hud' || clave === 'hud-monitor' || clave === 'todos-monitores' || clave === 'num-monitores') {
                this._construye();
            } else if (clave.startsWith('hud-')) {
                this._hud?.ajustesCambiados?.();
                this._colocaHud();
                this._hud?.actor?.queue_repaint();
            } else if (clave === 'clima') {
                this._escena?.ajustesCambiados();
                this._hud?.ajustesCambiados?.();
                this._colocaHud();
                this._hud?.actor?.queue_repaint();
            } else if (clave === 'hora-simulada') {
                this._escena?.actualizaHoraSimulada();
            } else {
                this._escena?.ajustesCambiados();
            }
        });
        this._actualizaPausa();
    }

    async _inicia(token) {
        try {
            const [{Escena}, {Hud}] = await Promise.all([
                import(_modUri(this.path, 'escena.js')),
                import(_modUri(this.path, 'hud.js')),
            ]);
            if (!this._activo || token !== this._enableToken) return;
            this._HudCls = Hud;
            try {
                this._escena = new Escena(this.path, this._raiz, this._settings);
            } catch (e) {
                logError(e, 'PixelZen: no encuentro las capas del fondo; ejecuta linux/instalar.sh');
                this._escena = null;
            }
            this._construye();
            this._ubicacion();
            this._actualizaPausa();
        } catch (e) {
            logError(e, 'PixelZen: error cargando módulos');
        }
    }

    _monitores() {
        const lm = Main.layoutManager;
        const primary = lm.primaryMonitor;
        const numMon = this._settings.get_int('num-monitores');
        const todos = this._settings.get_boolean('todos-monitores');
        if (!todos || numMon <= 1) return [primary];
        const otros = lm.monitors.filter(m => m && m !== primary);
        return [primary, ...otros].slice(0, Math.max(1, numMon));
    }

    _construye() {
        this._escena?.construye(this._monitores().filter(Boolean));
        const soloW = this._settings.get_boolean('solo-widgets');
        this._escena?.ocultar(soloW);
        this._grupo.set_child_above_sibling(this._raiz, null);

        const quiereHud = this._settings.get_boolean('hud');
        if (quiereHud && !this._hud && this._HudCls) {
            this._hud = new this._HudCls(this.path, this._settings);
            this._raiz.add_child(this._hud.actor);
        } else if (!quiereHud && this._hud) {
            this._hud.destroy();
            this._hud = null;
        }
        if (this._hud) {
            this._raiz.set_child_above_sibling(this._hud.actor, null);
            this._colocaHud();
        }
    }

    _colocaHud() {
        if (!this._hud) return;
        const lm = Main.layoutManager;
        let i = this._settings.get_int('hud-monitor');
        if (i < 0 || i >= lm.monitors.length) i = lm.primaryIndex;
        const mon = lm.monitors[i] ?? lm.primaryMonitor;
        this._hud.coloca(lm.getWorkAreaForMonitor(i), mon);
    }

    _actualizaPausa() {
        const bloqueada = Main.sessionMode.isLocked || Main.sessionMode.isGreeter;
        const lm = Main.layoutManager;
        let completa = false;
        for (let i = 0; i < lm.monitors.length; i++) {
            if (global.display.get_monitor_in_fullscreen(i)) {
                completa = true;
                break;
            }
        }
        const pausado = bloqueada || completa;
        this._escena?.pausa(pausado);
        this._hud?.pausa?.(pausado);
    }

    _programaRotacion() {
        if (this._timerRot) { GLib.source_remove(this._timerRot); this._timerRot = 0; }
        let mins = 0;
        try { mins = this._settings.get_int('rotacion-minutos'); } catch (_e) { mins = 0; }
        if (mins <= 0) return;
        this._timerRot = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, mins * 60, () => {
            if (!this._settings.get_boolean('solo-widgets')) this._rotarSiguienteTema();
            return GLib.SOURCE_CONTINUE;
        });
    }

    _rotarSiguienteTema() {
        try {
            const temasDir = `${this.path}/temas`;
            if (!GLib.file_test(temasDir, GLib.FileTest.IS_DIR)) return;
            const ids = [];
            const dir = Gio.File.new_for_path(temasDir);
            const it = dir.enumerate_children('standard::name,standard::type', Gio.FileQueryInfoFlags.NONE, null);
            let info;
            while ((info = it.next_file(null)) !== null) {
                if (info.get_file_type() !== Gio.FileType.DIRECTORY) continue;
                const n = info.get_name();
                if (!n.startsWith('_') && GLib.file_test(`${temasDir}/${n}/datos.json`, GLib.FileTest.EXISTS)) ids.push(n);
            }
            ids.sort();
            if (ids.length < 2) return;
            const cur = this._settings.get_string('tema');
            const idx = ids.indexOf(cur);
            const sig = ids[(idx + 1) % ids.length];
            this._settings.set_string('tema', sig);
            this._settings.set_int('tema-revision', this._settings.get_int('tema-revision') + 1);
        } catch (_e) { /* ignorar */ }
    }

    _ubicacion() {
        if (!this._escena) return;
        try {
            const p = Gio.Subprocess.new(['python3', '-I', `${this.path}/code/ubicacion.py`],
                Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_SILENCE);
            p.communicate_utf8_async(null, null, (proc, res) => {
                try {
                    const [, out] = proc.communicate_utf8_finish(res);
                    const r = JSON.parse(out);
                    this._escena?.ponUbicacion(r.lat, r.lon);
                    this._hud?.ponUbicacion(r.lat, r.lon);
                } catch (_e) { /* se queda la ubicacion anterior */ }
            });
        } catch (_e) { /* sin python3: Madrid por defecto */ }
    }

    disable() {
        this._activo = false;
        this._HudCls = null;
        for (const [obj, id] of this._ids) obj.disconnect(id);
        this._ids = [];
        if (this._timerUbi) GLib.source_remove(this._timerUbi);
        this._timerUbi = 0;
        if (this._timerRot) GLib.source_remove(this._timerRot);
        this._timerRot = 0;
        this._hud?.destroy();
        this._hud = null;
        this._escena?.destroy();
        this._escena = null;
        this._raiz?.destroy();
        this._raiz = null;
        this._settings = null;
        this._grupo = null;
    }
}
