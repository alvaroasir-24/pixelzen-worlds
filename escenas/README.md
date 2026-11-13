# Cómo añadir un nuevo fondo a PixelZen

La arquitectura es modular: cada fondo vive en su propia carpeta dentro de `escenas/<id>/` y funciona automáticamente tanto en **Linux (GNOME)** como en **Windows**.

## Pasos

1. **Copia la plantilla**:
   ```bash
   cp -r escenas/_plantilla escenas/mi-nuevo-fondo
   ```
2. **Edita `escenas/mi-nuevo-fondo/tema.json`**:
   - Cambia `id`, `nombre`, `subtitulo`, `citas`.
   - Elige `modo_pajaros` (`"grullas"` o `"wyverns"`), `modo_particulas` (`"hojas_mana"` o `"brasas_mana"`) y la paleta de luces/runas/olas.
3. **Dibuja tu paisaje en `escenas/mi-nuevo-fondo/generar.py`**:
   - Usa las utilidades compartidas de `src/pz_lib.py` (`Lienzo`, `render_cielo`, `render_estrellas`, `render_nubes`, `render_lago`, `aplica_vineta`, `exporta_sprites_si_aplica`, `exporta_salida`).
   - Respeta la zona del HUD (`x: 478..632, y: 10..215`) o usa `en_zona(x, y)` para mantener el panel legible.
4. **Compila el tema para Linux y Windows**:
   ```bash
   python3 src/construir.py mi-nuevo-fondo
   ```
5. **Úsalo**:
   - En **Linux**: `./linux/tema.sh mi-nuevo-fondo`
   - En **Windows**: selecciónalo en Lively Wallpaper o ejecuta `windows\ejecutar.bat` con `--tema mi-nuevo-fondo`.
