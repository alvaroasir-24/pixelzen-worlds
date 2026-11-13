(() => {
  const TEMAS_DISPONIBLES = ['fittoa', 'continente-demoniaco', 'hunter-x-hunter', 'black-clover', 'spiderman-miles-morales'];
  const params = new URLSearchParams(window.location.search);
  const canvas = document.getElementById('lienzo');
  const d = new Date();

  const renderer = window.PixelZenCanvas.createRenderer(canvas, {
    initialState: {
      tema: params.get('tema') || 'fittoa',
      modoHora: params.get('modo') === 'real' ? 0 : (params.get('modo') === 'demo' ? 2 : 1),
      horaFija: parseFloat(params.get('hora') || '21.5'),
      fps: parseInt(params.get('fps') || '8', 10),
      mostrarHud: params.get('hud') !== '0',
      inicioHora: d.getHours() + d.getMinutes() / 60 + d.getSeconds() / 3600,
    },
    onTemaLoaded(tema) {
      document.body.style.background = tema.cielo_fondo || '#0a0c24';
    },
    onRender(fecha, T) {
      renderer.actualizaHud(fecha, T, { quoteIntervalMs: 90000 });
    },
  });

  const { state } = renderer;
  let timer = null;
  function reprogramar() {
    if (timer) clearInterval(timer);
    timer = setInterval(() => { state.tick++; renderer.render(); }, Math.round(1000 / Math.max(2, Math.min(24, state.fps))));
  }

  window.livelyPropertyListener = (name, val) => {
    if (name === 'tema') {
      const nuevo = TEMAS_DISPONIBLES[val] || TEMAS_DISPONIBLES[0];
      if (nuevo !== state.tema) { renderer.cargarTema(nuevo).then(renderer.render); }
    } else if (name === 'modoHora') {
      state.modoHora = val;
      if (val === 1) {
        state.inicioMs = Date.now();
        const now = new Date();
        state.inicioHora = now.getHours() + now.getMinutes() / 60 + now.getSeconds() / 3600;
      }
    } else if (name === 'horaFija') state.horaFija = val;
    else if (name === 'fps') { state.fps = val; reprogramar(); }
    else if (name === 'mostrarHud') state.mostrarHud = !!val;
    renderer.render();
  };

  renderer.cargarTema(state.tema).then(() => { renderer.render(); reprogramar(); });
})();
