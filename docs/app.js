(() => {
  const canvas = document.getElementById('lienzo');
  const loadingEl = document.getElementById('canvas-loading');
  const sliderEl = document.getElementById('hora-slider');
  const horaLabelEl = document.getElementById('hora-label');

  const renderer = window.PixelZenCanvas.createRenderer(canvas, {
    initialState: {
      tema: 'fittoa',
      modoHora: 3, // 0=real, 1=90m, 2=demo90s, 3=fija
      horaFija: 18.75,
      fps: 10,
      mostrarHud: true,
      inicioHora: 18.75,
    },
    onTemaLoaded(tema) {
      document.getElementById('canvas-wrap').style.background = tema.cielo_fondo || '#060814';
      loadingEl.classList.add('is-hidden');
      renderer.render();
    },
    onRender(fecha, T) {
      const p2 = v => String(v).padStart(2, '0');
      horaLabelEl.textContent = `${p2(fecha.getHours())}:${p2(fecha.getMinutes())}`;
      if (renderer.state.modoHora !== 3) {
        sliderEl.value = (fecha.getHours() + fecha.getMinutes() / 60).toFixed(2);
      }
      renderer.actualizaHud(fecha, T, { quoteIntervalMs: 15000 });
    },
  });

  const { state } = renderer;

  function seleccionaYCarga(id) {
    loadingEl.classList.remove('is-hidden');
    renderer.cargarTema(id);
  }

  function seleccionarTema(id) {
    state.tema = id;
    document.querySelectorAll('.pill[data-tema]').forEach(b => {
      b.classList.toggle('is-active', b.dataset.tema === id);
    });
    seleccionaYCarga(id);
  }

  function limpiarModos() {
    document.querySelectorAll('.btn-mode, .btn-phase').forEach(b => b.classList.remove('is-active'));
  }

  document.querySelectorAll('.pill[data-tema]').forEach(btn => {
    btn.addEventListener('click', () => seleccionarTema(btn.dataset.tema));
  });

  document.querySelectorAll('.btn-mode').forEach(btn => {
    btn.addEventListener('click', () => {
      limpiarModos();
      btn.classList.add('is-active');
      const m = btn.dataset.modo;
      if (m === '90m') {
        state.modoHora = 1;
        state.inicioMs = Date.now();
        state.inicioHora = parseFloat(sliderEl.value) || 12;
      } else if (m === 'demo') {
        state.modoHora = 2;
      } else {
        state.modoHora = 0;
      }
      renderer.render();
    });
  });

  document.querySelectorAll('.btn-phase').forEach(btn => {
    btn.addEventListener('click', () => {
      limpiarModos();
      btn.classList.add('is-active');
      state.modoHora = 3;
      state.horaFija = parseFloat(btn.dataset.hora);
      sliderEl.value = state.horaFija;
      renderer.render();
    });
  });

  sliderEl.addEventListener('input', () => {
    limpiarModos();
    state.modoHora = 3;
    state.horaFija = parseFloat(sliderEl.value);
    renderer.render();
  });

  const btnHud = document.getElementById('btn-hud');
  btnHud.addEventListener('click', () => {
    state.mostrarHud = !state.mostrarHud;
    btnHud.textContent = `HUD: ${state.mostrarHud ? 'ON' : 'OFF'}`;
    renderer.render();
  });

  document.getElementById('btn-fullscreen').addEventListener('click', () => {
    const wrap = document.getElementById('canvas-wrap');
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else if (wrap.requestFullscreen) {
      wrap.requestFullscreen();
    }
  });

  document.querySelectorAll('.world-card').forEach(card => {
    const id = card.dataset.world;
    const img = card.querySelector('.world-media img');
    card.querySelectorAll('.phase-switch button').forEach(btn => {
      btn.addEventListener('click', () => {
        card.querySelectorAll('.phase-switch button').forEach(b => b.classList.remove('is-active'));
        btn.classList.add('is-active');
        img.src = `previews/${id}/${btn.dataset.fase}.png`;
      });
    });
    const tryBtn = card.querySelector('.btn-try');
    if (tryBtn) {
      tryBtn.addEventListener('click', () => {
        seleccionarTema(id);
        document.getElementById('visor').scrollIntoView({ behavior: 'smooth' });
      });
    }
  });

  document.querySelectorAll('.os-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.os-tab').forEach(t => t.classList.remove('is-active'));
      document.querySelectorAll('.os-pane').forEach(p => p.classList.remove('is-active'));
      tab.classList.add('is-active');
      document.querySelector(`.os-pane[data-pane="${tab.dataset.os}"]`).classList.add('is-active');
    });
  });

  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(btn.dataset.copy);
        const orig = btn.textContent;
        btn.textContent = '¡Copiado!';
        setTimeout(() => { btn.textContent = orig; }, 1400);
      } catch {
        btn.textContent = 'Usa Ctrl+C';
      }
    });
  });

  setInterval(() => { state.tick++; renderer.render(); }, 100);
  seleccionaYCarga(state.tema);
})();
