#!/usr/bin/env python3
"""Aplicación visual de escritorio PixelZen Worlds para Linux (GTK4 + Libadwaita).

Permite al usuario final elegir mundo con miniaturas y vista previa M1/M2,
configurar 1 o 2 monitores, elegir modo solar/ciclo y personalizar el panel HUD
sin tener que usar la terminal ni editar archivos.
"""
import os
import shutil
import subprocess
import sys

try:
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    from gi.repository import Adw, Gdk, Gio, GLib, Gtk  # noqa: E402
except Exception as exc:
    sys.stderr.write(
        'PixelZen Worlds necesita GTK 4 y Libadwaita (python3-gi, gir1.2-gtk-4.0, gir1.2-adw-1).\n'
        f'Detalle: {exc}\n'
    )
    sys.exit(1)

UUID = 'pixelzen@mosqui1988.github.io'
EXT_DIR = os.path.expanduser(f'~/.local/share/gnome-shell/extensions/{UUID}')
SCHEMA_DIR = os.path.join(EXT_DIR, 'schemas')
SCHEMA_ID = 'org.gnome.shell.extensions.pixelzen'
SVC_CICLO90 = 'pixelzen-ciclo90.service'

TEMAS = [
    {
        'id': 'fittoa',
        'anime': 'Mushoku Tensei',
        'titulo': 'Región de Fittoa',
        'm1': 'Aldea de Buena, Mansión Greyrat y Gran Roble',
        'm2': 'Reino de Asura y Base de Perugius (Chaos Breaker)',
    },
    {
        'id': 'continente-demoniaco',
        'anime': 'Mushoku Tensei',
        'titulo': 'Continente Demoníaco',
        'm1': 'Ciudadela de Rikarisu y Cristales Carmesí',
        'm2': 'Castillo de Atofe y Atoferatofe Raibaku',
    },
    {
        'id': 'hunter-x-hunter',
        'anime': 'Hunter × Hunter',
        'titulo': 'Isla Ballena',
        'm1': 'Cabaña de Mito-san, Gon pescando y Árbol del Mundo',
        'm2': 'Greed Island (Anillo G.I., Book! y Cartas)',
    },
    {
        'id': 'black-clover',
        'anime': 'Black Clover',
        'titulo': 'Aldea de Hage',
        'm1': 'Iglesia de Hage, Cráneo del Demonio y Antimagia',
        'm2': 'Reino de Picas y la Tríada Oscura',
    },
    {
        'id': 'spiderman-miles-morales',
        'anime': 'Marvel Spider-Man',
        'titulo': 'Brooklyn & Manhattan',
        'm1': 'Brooklyn, Puente, Estatua de la Libertad y Miles',
        'm2': 'Midtown Manhattan, Metro Elevado y Harlem',
    },
]

FASES = [('dia', 'Día'), ('dorado', 'Atardecer'), ('noche', 'Noche')]
MODOS = [
    ('real', 'Hora real del sistema'),
    ('90m', 'Ciclo completo (24 h en 90 min)'),
    ('demo', 'Demo rápida (24 h en 90 s)'),
    ('fija', 'Hora fija manual'),
]
STATS_META = [
    ('hud-tiempo', 'Reloj y fase lunar', 'Hora actual, fecha, mundo activo y modo del cielo'),
    ('hud-sistema', 'Sistema (CPU / RAM / Temp)', 'Uso del procesador, memoria, temperatura y batería'),
    ('hud-red', 'Red y tráfico', 'Interfaz activa, IP local y velocidad de subida/bajada'),
    ('hud-dev', 'Desarrollo', 'Repositorio Git, runtimes y estado de servicios'),
    ('hud-grimorio', 'Citas del grimorio', 'Frases y lore del anime elegido'),
]


def _resolver_preview(tema_id, fase, secundario=False):
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sub = 'secundario' if secundario else ''
    candidatos = [
        os.path.join(EXT_DIR, 'temas', tema_id, sub, 'preview', fase, 'v3.png'),
        os.path.join(repo_root, 'escenas', tema_id, sub, 'preview', fase, 'v3.png'),
        os.path.join(EXT_DIR, 'temas', tema_id, sub, 'fondo.png'),
        os.path.join(repo_root, 'windows', 'lively', 'temas', tema_id, sub, 'fondo.png'),
        os.path.join(EXT_DIR, 'temas', tema_id, 'fondo.png'),
    ]
    for ruta in candidatos:
        if ruta and os.path.isfile(ruta):
            return ruta
    return None


def _cargar_settings():
    if os.path.isfile(os.path.join(SCHEMA_DIR, 'gschemas.compiled')):
        src = Gio.SettingsSchemaSource.new_from_directory(SCHEMA_DIR, None, False)
        schema = src.lookup(SCHEMA_ID, True)
        if schema is not None:
            return Gio.Settings.new_full(schema, None, None)
    return None


def _extension_activa():
    try:
        out = subprocess.run(
            ['gnome-extensions', 'info', UUID],
            capture_output=True, text=True, check=False,
        ).stdout
        for linea in out.splitlines():
            if 'State:' in linea or 'Estado:' in linea:
                return ('ACTIVE' in linea.upper()) or ('ENABLED' in linea.upper()) or ('ACTIVA' in linea.upper())
    except Exception:
        pass
    return False


def _ciclo90_activo():
    try:
        res = subprocess.run(
            ['systemctl', '--user', 'is-active', SVC_CICLO90],
            capture_output=True, text=True, check=False,
        )
        return res.stdout.strip() == 'active'
    except Exception:
        return False


def _sincronizar_tema_en_ext(tema_id):
    tema_pack = os.path.join(EXT_DIR, 'temas', tema_id)
    if not os.path.isdir(os.path.join(tema_pack, 'images')):
        return
    dst_imgs = os.path.join(EXT_DIR, 'images')
    if os.path.isdir(dst_imgs):
        shutil.rmtree(dst_imgs, ignore_errors=True)
    shutil.copytree(os.path.join(tema_pack, 'images'), dst_imgs)
    for fn in ('datos.json', 'tema.json', 'fondo.png'):
        src_fn = os.path.join(tema_pack, fn)
        if os.path.isfile(src_fn):
            shutil.copy2(src_fn, os.path.join(EXT_DIR, fn))
    bg_dir = os.path.expanduser('~/.local/share/backgrounds')
    if os.path.isdir(bg_dir) and os.path.isfile(os.path.join(tema_pack, 'fondo.png')):
        shutil.copy2(os.path.join(tema_pack, 'fondo.png'), os.path.join(bg_dir, 'pixelzen.png'))


class PixelZenWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title='PixelZen Worlds')
        self.set_default_size(1040, 720)
        self.set_size_request(820, 600)

        self.settings = _cargar_settings()
        self.tema_sel = self.settings.get_string('tema') if self.settings else 'fittoa'
        if not any(t['id'] == self.tema_sel for t in TEMAS):
            self.tema_sel = 'fittoa'
        self.fase_sel = 'dorado'
        self._botones_tema = {}
        self._switches_hud = {}

        css = Gtk.CssProvider()
        css.load_from_data(b"""
        .pz-card {
            background: alpha(@card_bg_color, 0.92);
            border: 1px solid alpha(@borders, 0.9);
            border-radius: 12px;
            padding: 10px;
        }
        .pz-card-active {
            border: 2px solid #54ded4;
            background: alpha(#54ded4, 0.08);
        }
        .pz-pill {
            border-radius: 99px;
            padding: 2px 10px;
            font-size: 11px;
            background: alpha(#54ded4, 0.16);
            color: #54ded4;
            font-weight: bold;
        }
        .pz-preview-frame {
            border-radius: 10px;
            border: 1px solid alpha(@borders, 0.9);
            background: #070a17;
            padding: 8px;
        }
        """)
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(display, css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(root_box)

        header = Adw.HeaderBar()
        title_widget = Adw.WindowTitle(
            title='PixelZen Worlds',
            subtitle='Elige tu mundo, monitores y estadísticas sin tocar código',
        )
        header.set_title_widget(title_widget)

        self.btn_aplicar = Gtk.Button(label='Aplicar cambios')
        self.btn_aplicar.add_css_class('suggested-action')
        self.btn_aplicar.connect('clicked', self._on_aplicar)
        header.pack_end(self.btn_aplicar)
        root_box.append(header)

        self.banner = Adw.Banner()
        self.banner.set_button_label('Activar extensión')
        self.banner.connect('button-clicked', self._on_activar_ext)
        root_box.append(self.banner)
        self._comprobar_estado_extension()

        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        root_box.append(scroll)

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        main.set_margin_top(16)
        main.set_margin_bottom(20)
        main.set_margin_start(18)
        main.set_margin_end(18)
        scroll.set_child(main)

        # Sección 1: Vista previa M1 + M2
        prev_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        prev_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        lbl_prev = Gtk.Label(label='Vista previa de tus pantallas')
        lbl_prev.add_css_class('title-4')
        lbl_prev.set_halign(Gtk.Align.START)
        lbl_prev.set_hexpand(True)
        prev_top.append(lbl_prev)

        fase_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        fase_box.add_css_class('linked')
        first_fase = None
        self._fase_btns = {}
        for fid, fnombre in FASES:
            b = Gtk.ToggleButton(label=fnombre)
            if first_fase is None:
                first_fase = b
            else:
                b.set_group(first_fase)
            b.set_active(fid == self.fase_sel)
            b.connect('toggled', self._on_fase_toggled, fid)
            self._fase_btns[fid] = b
            fase_box.append(b)
        prev_top.append(fase_box)
        prev_box.append(prev_top)

        screens_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12, homogeneous=True)
        self.frame_m1, self.pic_m1, self.lbl_m1_desc = self._crear_panel_preview('Monitor 1 · Principal')
        self.frame_m2, self.pic_m2, self.lbl_m2_desc = self._crear_panel_preview('Monitor 2 · Continuación de la historia')
        screens_row.append(self.frame_m1)
        screens_row.append(self.frame_m2)
        prev_box.append(screens_row)

        self.lbl_hud_resumen = Gtk.Label()
        self.lbl_hud_resumen.add_css_class('dim-label')
        self.lbl_hud_resumen.set_halign(Gtk.Align.START)
        prev_box.append(self.lbl_hud_resumen)
        main.append(prev_box)

        # Sección 2: Galería de mundos
        lbl_mundos = Gtk.Label(label='1. Elige el mundo de fondo')
        lbl_mundos.add_css_class('title-4')
        lbl_mundos.set_halign(Gtk.Align.START)
        main.append(lbl_mundos)

        flow = Gtk.FlowBox()
        flow.set_selection_mode(Gtk.SelectionMode.NONE)
        flow.set_min_children_per_line(2)
        flow.set_max_children_per_line(3)
        flow.set_column_spacing(10)
        flow.set_row_spacing(10)
        for tema in TEMAS:
            card = self._crear_tarjeta_tema(tema)
            flow.append(card)
        main.append(flow)

        # Sección 3: Monitores, Ciclo solar y Estadísticas HUD
        cols = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16, homogeneous=True)

        # Columna izquierda: Monitores + Ciclo solar
        grp_entorno = Adw.PreferencesGroup(title='2. Monitores y ciclo del sol')
        self.combo_mon = Adw.ComboRow(
            title='Pantallas activas',
            subtitle='En 2 monitores se muestra la continuación de la historia',
            model=Gtk.StringList.new([
                '1 monitor (solo principal)',
                '2 monitores (principal + continuación)',
            ]),
        )
        self.combo_mon.connect('notify::selected', lambda *_: self._actualizar_preview())
        grp_entorno.add(self.combo_mon)

        self.combo_modo = Adw.ComboRow(
            title='Modo de hora / ciclo solar',
            subtitle='Controla cómo avanza el cielo durante el día',
            model=Gtk.StringList.new([nombre for _, nombre in MODOS]),
        )
        self.combo_modo.connect('notify::selected', lambda *_: self._actualizar_controles_hora())
        grp_entorno.add(self.combo_modo)

        self.row_hora = Adw.SpinRow.new_with_range(0.0, 23.75, 0.5)
        self.row_hora.set_title('Hora fija (0 – 23.5 h)')
        self.row_hora.set_digits(2)
        grp_entorno.add(self.row_hora)

        self.row_animar = Adw.SwitchRow(
            title='Animación continua (nubes, aves y partículas)',
            subtitle='Desactívalo si solo quieres que cambie con el sol',
        )
        self.row_animar.connect('notify::active', lambda *_: self._actualizar_controles_hora())
        grp_entorno.add(self.row_animar)

        self.row_fps = Adw.SpinRow.new_with_range(2, 24, 1)
        self.row_fps.set_title('Fluidez de animación (FPS)')
        grp_entorno.add(self.row_fps)
        cols.append(grp_entorno)

        # Columna derecha: Estadísticas HUD
        grp_hud = Adw.PreferencesGroup(title='3. Estadísticas en escritorio (HUD)')
        self.row_hud = Adw.SwitchRow(
            title='Mostrar panel de datos sobre el escritorio',
            subtitle='Activa o apaga todas las cajitas de información',
        )
        self.row_hud.connect('notify::active', lambda *_: self._actualizar_controles_hud())
        grp_hud.add(self.row_hud)

        for clave, titulo, subtitulo in STATS_META:
            sw = Adw.SwitchRow(title=titulo, subtitle=subtitulo)
            sw.connect('notify::active', lambda *_: self._actualizar_resumen_hud())
            self._switches_hud[clave] = sw
            grp_hud.add(sw)
        cols.append(grp_hud)

        main.append(cols)

        # Barra inferior de estado
        self.lbl_status = Gtk.Label(label='Listo.')
        self.lbl_status.add_css_class('dim-label')
        self.lbl_status.set_halign(Gtk.Align.START)
        main.append(self.lbl_status)

        self._cargar_estado_inicial()
        self._actualizar_tarjetas()
        self._actualizar_preview()

    def _crear_panel_preview(self, titulo):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.add_css_class('pz-preview-frame')
        lbl_top = Gtk.Label(label=titulo)
        lbl_top.add_css_class('heading')
        lbl_top.set_halign(Gtk.Align.START)
        box.append(lbl_top)

        pic = Gtk.Picture()
        pic.set_size_request(320, 185)
        pic.set_can_shrink(True)
        pic.set_content_fit(Gtk.ContentFit.COVER)
        box.append(pic)

        lbl_desc = Gtk.Label()
        lbl_desc.add_css_class('caption')
        lbl_desc.set_wrap(True)
        lbl_desc.set_halign(Gtk.Align.START)
        box.append(lbl_desc)
        return box, pic, lbl_desc

    def _crear_tarjeta_tema(self, tema):
        btn = Gtk.Button()
        btn.add_css_class('flat')
        btn.connect('clicked', self._on_tema_elegido, tema['id'])

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        card.add_css_class('pz-card')
        card.set_size_request(270, -1)

        pic = Gtk.Picture()
        pic.set_size_request(250, 125)
        pic.set_can_shrink(True)
        pic.set_content_fit(Gtk.ContentFit.COVER)
        ruta = _resolver_preview(tema['id'], 'dorado', secundario=False) or _resolver_preview(tema['id'], 'noche', secundario=False)
        if ruta:
            pic.set_filename(ruta)
        card.append(pic)

        row_t = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        lbl = Gtk.Label(label=tema['titulo'])
        lbl.add_css_class('heading')
        lbl.set_halign(Gtk.Align.START)
        lbl.set_hexpand(True)
        badge = Gtk.Label(label=tema['anime'])
        badge.add_css_class('pz-pill')
        row_t.append(lbl)
        row_t.append(badge)
        card.append(row_t)

        sub = Gtk.Label(label=f"M1: {tema['m1']}\nM2: {tema['m2']}")
        sub.add_css_class('caption')
        sub.set_wrap(True)
        sub.set_halign(Gtk.Align.START)
        card.append(sub)

        btn.set_child(card)
        self._botones_tema[tema['id']] = card
        return btn

    def _cargar_estado_inicial(self):
        if not self.settings:
            self.combo_mon.set_selected(1)
            self.combo_modo.set_selected(0)
            self.row_hora.set_value(21.5)
            self.row_animar.set_active(True)
            self.row_fps.set_value(8)
            self.row_hud.set_active(True)
            for sw in self._switches_hud.values():
                sw.set_active(True)
            return

        s = self.settings
        self.combo_mon.set_selected(1 if s.get_int('num-monitores') >= 2 else 0)
        if _ciclo90_activo():
            modo_idx = 1
        elif s.get_boolean('ciclo-rapido'):
            modo_idx = 2
        elif s.get_double('hora-simulada') >= 0:
            modo_idx = 3
        else:
            modo_idx = 0
        self.combo_modo.set_selected(modo_idx)
        hv = s.get_double('hora-simulada')
        self.row_hora.set_value(hv if hv >= 0 else 21.5)
        self.row_animar.set_active(s.get_boolean('animar'))
        self.row_fps.set_value(s.get_int('fps'))
        self.row_hud.set_active(s.get_boolean('hud'))
        for clave, sw in self._switches_hud.items():
            sw.set_active(s.get_boolean(clave))
        self._actualizar_controles_hora()
        self._actualizar_controles_hud()

    def _comprobar_estado_extension(self):
        if self.settings is None:
            self.banner.set_title('La extensión de GNOME no está instalada todavía (ejecuta linux/instalar.sh).')
            self.banner.set_revealed(True)
            self.btn_aplicar.set_sensitive(False)
        elif not _extension_activa():
            self.banner.set_title('La extensión PixelZen Worlds está instalada pero desactivada en GNOME.')
            self.banner.set_revealed(True)
        else:
            self.banner.set_revealed(False)

    def _on_activar_ext(self, *_args):
        subprocess.run(['gnome-extensions', 'enable', UUID], check=False)
        self._comprobar_estado_extension()
        self.lbl_status.set_text('Extensión activada en GNOME Shell.')

    def _on_tema_elegido(self, _btn, tema_id):
        self.tema_sel = tema_id
        self._actualizar_tarjetas()
        self._actualizar_preview()

    def _on_fase_toggled(self, btn, fid):
        if btn.get_active():
            self.fase_sel = fid
            self._actualizar_preview()

    def _actualizar_tarjetas(self):
        for tid, card in self._botones_tema.items():
            if tid == self.tema_sel:
                card.add_css_class('pz-card-active')
            else:
                card.remove_css_class('pz-card-active')

    def _actualizar_preview(self):
        meta = next((t for t in TEMAS if t['id'] == self.tema_sel), TEMAS[0])
        p1 = _resolver_preview(self.tema_sel, self.fase_sel, secundario=False)
        p2 = _resolver_preview(self.tema_sel, self.fase_sel, secundario=True)
        if p1:
            self.pic_m1.set_filename(p1)
        if p2:
            self.pic_m2.set_filename(p2)
        self.lbl_m1_desc.set_text(f"{meta['titulo']}: {meta['m1']}")
        self.lbl_m2_desc.set_text(f"Continuación: {meta['m2']}")
        self.frame_m2.set_visible(self.combo_mon.get_selected() == 1)
        self._actualizar_resumen_hud()

    def _actualizar_controles_hora(self):
        es_fija = self.combo_modo.get_selected() == 3
        self.row_hora.set_sensitive(es_fija)
        self.row_fps.set_sensitive(self.row_animar.get_active())

    def _actualizar_controles_hud(self):
        on = self.row_hud.get_active()
        for sw in self._switches_hud.values():
            sw.set_sensitive(on)
        self._actualizar_resumen_hud()

    def _actualizar_resumen_hud(self):
        if not self.row_hud.get_active():
            self.lbl_hud_resumen.set_text('HUD en escritorio: desactivado (solo fondo limpio).')
            return
        activas = [tit.split(' ')[0] for k, tit, _ in STATS_META if self._switches_hud[k].get_active()]
        resumen = ', '.join(activas) if activas else 'ninguna tarjeta marcada'
        self.lbl_hud_resumen.set_text(f'Tarjetas HUD activas sobre Monitor 1: {resumen}.')

    def _on_aplicar(self, *_args):
        if not self.settings:
            return
        s = self.settings
        n_mon = 2 if self.combo_mon.get_selected() == 1 else 1
        s.set_int('num-monitores', n_mon)
        s.set_boolean('todos-monitores', n_mon >= 2)

        modo_id = MODOS[self.combo_modo.get_selected()][0]
        if modo_id == '90m':
            s.set_int('ciclo-duracion', 5400)
            s.set_boolean('ciclo-rapido', False)
            s.set_double('hora-simulada', -1.0)
            subprocess.run(['systemctl', '--user', 'enable', '--now', SVC_CICLO90], check=False)
        else:
            subprocess.run(['systemctl', '--user', 'disable', '--now', SVC_CICLO90], check=False)
            if modo_id == 'demo':
                s.set_int('ciclo-duracion', 90)
                s.set_double('hora-simulada', -1.0)
                s.set_boolean('ciclo-rapido', True)
            elif modo_id == 'fija':
                s.set_boolean('ciclo-rapido', False)
                s.set_double('hora-simulada', float(self.row_hora.get_value()))
            else:
                s.set_boolean('ciclo-rapido', False)
                s.set_double('hora-simulada', -1.0)

        s.set_boolean('animar', self.row_animar.get_active())
        s.set_int('fps', int(self.row_fps.get_value()))
        s.set_boolean('hud', self.row_hud.get_active())
        for clave, sw in self._switches_hud.items():
            s.set_boolean(clave, sw.get_active())

        _sincronizar_tema_en_ext(self.tema_sel)
        s.set_string('tema', self.tema_sel)
        rev = s.get_int('tema-revision') + 1
        s.set_int('tema-revision', rev)
        Gio.Settings.sync()

        meta = next((t for t in TEMAS if t['id'] == self.tema_sel), TEMAS[0])
        self.lbl_status.set_text(
            f"✅ Aplicado '{meta['titulo']}' · {n_mon} monitor(es) · modo {modo_id}."
        )


class PixelZenApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='io.github.mosqui1988.PixelZenWorlds')

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = PixelZenWindow(self)
        win.present()


def main():
    app = PixelZenApp()
    return app.run(sys.argv)


if __name__ == '__main__':
    sys.exit(main())
