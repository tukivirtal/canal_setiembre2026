/* Rin · formulario del regalo, muestra de audio y página de las noches.
   El formulario guarda el correo en MailerLite (por la función /api/suscribir de Netlify) y
   abre las noches enseguida: la persona recibe el regalo aunque el guardado tarde o falle.
   También mide el camino (función /api/evento): sin cookies ni datos personales. */
var RIN = {
  mailerlite: { cuenta: '1921447', formulario: '200892869569939404' },
  noches: '/tus-noches/'
};

(function () {
  var CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var INICIO = Date.now();
  var esRegalo = location.pathname.indexOf(RIN.noches) === 0;

  // ── Medición ──────────────────────────────────────────────────────────────────────────────
  // La sesión es un número al azar que vive mientras la pestaña esté abierta (sessionStorage):
  // sirve para contar personas, no toques, y para unir la landing con la página de las noches.
  var memoria = {};
  function recordar(k, v) {
    try {
      if (v !== undefined) sessionStorage.setItem(k, v);
      var x = sessionStorage.getItem(k);
      if (x !== null) return x;
    } catch (e) { /* navegador sin sessionStorage */ }
    if (v !== undefined) memoria[k] = v;
    return memoria[k];
  }

  // De dónde llegó: ?o= en el enlace (por ejemplo ?o=promo), el clic de un anuncio de TikTok
  // (ttclid), el navegador de la app o la página anterior.
  function calcularOrigen() {
    var q = new URLSearchParams(location.search), ua = navigator.userAgent, r = '';
    try { r = document.referrer ? new URL(document.referrer).hostname.replace(/^www\./, '') : ''; } catch (e) {}
    if (r === location.hostname.replace(/^www\./, '')) r = '';
    return q.get('o') || q.get('utm_source') || (q.get('ttclid') ? 'tiktok-promo' : '') ||
      (/musical_ly|bytedancewebview|tiktok|trill_/i.test(ua) ? 'tiktok' : '') ||
      (/instagram/i.test(ua) ? 'instagram' : '') || (/FBAN|FBAV|FB_IAB/.test(ua) ? 'facebook' : '') ||
      r || 'directo';
  }

  var SESION = recordar('rin-s') || recordar('rin-s', Math.random().toString(36).slice(2, 12));
  var ORIGEN = recordar('rin-o') || recordar('rin-o', calcularOrigen());

  function medir(evento, detalle) {
    try {
      var cuerpo = JSON.stringify({ e: evento, s: SESION, o: ORIGEN, x: detalle || '' });
      if (navigator.sendBeacon && navigator.sendBeacon('/api/evento', new Blob([cuerpo], { type: 'text/plain' }))) return;
      fetch('/api/evento', { method: 'POST', body: cuerpo, keepalive: true }).catch(function () {});
    } catch (e) { /* medir nunca rompe la página */ }
  }
  var yaMedido = {};
  function unaVez(evento, detalle) {
    var k = evento + '|' + (detalle || '');
    if (yaMedido[k]) return;
    yaMedido[k] = true;
    medir(evento, detalle);
  }

  medir(esRegalo ? 'visita-regalo' : 'visita',
    esRegalo ? (/[?&]bienvenida=1/.test(location.search) ? 'form' : 'vuelve') : '');

  // Cuánto se quedó y cuánto bajó, al irse (o al pasar a otra app).
  var bajo = 0;
  function medirScroll() {
    var alto = document.documentElement.scrollHeight - window.innerHeight;
    var p = alto > 0 ? window.scrollY / alto : 1;
    if (p > bajo) bajo = p;
  }
  window.addEventListener('scroll', medirScroll, { passive: true });
  medirScroll();
  var salio = false;
  function salida() {
    if (salio) return;
    salio = true;
    var s = (Date.now() - INICIO) / 1000;
    var seg = s < 3 ? 's0' : s < 10 ? 's3' : s < 30 ? 's10' : s < 90 ? 's30' : 's90';
    var p = bajo >= 0.95 ? 'p100' : bajo >= 0.75 ? 'p75' : bajo >= 0.5 ? 'p50' : bajo >= 0.25 ? 'p25' : 'p0';
    medir('salida', (esRegalo ? 'r' : 'l') + '-' + seg + '-' + p);
  }
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') salida();
  });
  window.addEventListener('pagehide', salida);

  // ── El formulario ─────────────────────────────────────────────────────────────────────────
  // Respaldo: el formulario integrado de MailerLite, si la función no responde bien.
  function respaldo(correo) {
    var url = 'https://assets.mailerlite.com/jsonp/' + RIN.mailerlite.cuenta + '/forms/' +
      RIN.mailerlite.formulario + '/subscribe';
    var datos = new FormData();
    datos.append('fields[email]', correo);
    datos.append('ml-submit', '1');
    datos.append('anticsrf', 'true');
    if (navigator.sendBeacon) navigator.sendBeacon(url, datos);
  }

  function suscribir(correo, trampa) {
    var guardado = fetch('/api/suscribir', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ correo: correo, sitio_web: trampa, s: SESION, o: ORIGEN }),
      keepalive: true
    }).then(function (r) { return r.json(); }).then(function (d) {
      if (!d || !d.ok) throw new Error('sin guardar');
    }).catch(function () { respaldo(correo); });
    return Promise.race([guardado, new Promise(function (r) { setTimeout(r, 3500); })]);
  }

  document.querySelectorAll('form[data-regalo]').forEach(function (f) {
    var campo = f.querySelector('input[type=email]');
    var boton = f.querySelector('button');
    var error = f.querySelector('.error');
    campo.addEventListener('focus', function () { unaVez('campo'); });
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var correo = campo.value.trim();
      if (!CORREO.test(correo)) {
        medir('correo-mal');
        error.textContent = 'Revisa tu correo: parece que falta algo.';
        campo.focus();
        return;
      }
      medir('clic');
      error.textContent = '';
      boton.disabled = true;
      boton.textContent = 'Abriendo tus noches…';
      var trampa = (f.querySelector('input[name=sitio_web]') || {}).value || '';
      suscribir(correo, trampa).then(function () {
        setTimeout(function () { location.href = RIN.noches + '?bienvenida=1'; }, 250);
      });
    });
  });

  // ── La muestra de la landing: un botón que reproduce y pausa, con una barra de avance ───
  document.querySelectorAll('[data-muestra]').forEach(function (caja) {
    var audio = caja.querySelector('audio');
    var boton = caja.querySelector('.reproducir');
    var barra = caja.querySelector('.barra i');
    var iconos = {
      play: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M8 5.5v13l11-6.5z"/></svg>',
      pausa: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z"/></svg>'
    };
    function pintar() {
      boton.innerHTML = audio.paused ? iconos.play : iconos.pausa;
      boton.setAttribute('aria-label', audio.paused ? 'Escuchar la muestra' : 'Pausar la muestra');
    }
    boton.addEventListener('click', function () { audio.paused ? audio.play() : audio.pause(); });
    audio.addEventListener('play', function () { pintar(); unaVez('muestra'); });
    audio.addEventListener('pause', pintar);
    audio.addEventListener('ended', function () { unaVez('muestra-fin'); audio.currentTime = 0; pintar(); });
    audio.addEventListener('timeupdate', function () {
      if (audio.duration) barra.style.width = (100 * audio.currentTime / audio.duration) + '%';
    });
    pintar();
  });

  // ── Página de las noches: bienvenida, una sola noche sonando a la vez y datos para la
  //    pantalla bloqueada ────────────────────────────────────────────────────────────────────
  if (/[?&]bienvenida=1/.test(location.search)) {
    var b = document.querySelector('.bienvenida');
    if (b) b.hidden = false;
  }
  var audios = document.querySelectorAll('audio[data-titulo]');
  audios.forEach(function (a) {
    var n = ((a.getAttribute('src') || '').match(/noche-(\d)/) || [])[1] || '0';
    a.addEventListener('play', function () {
      unaVez('noche-' + n);
      audios.forEach(function (otro) { if (otro !== a) otro.pause(); });
      if ('mediaSession' in navigator && window.MediaMetadata) {
        navigator.mediaSession.metadata = new MediaMetadata({
          title: a.dataset.titulo, artist: 'Rin', album: 'Las 3 primeras noches',
          artwork: [{ src: a.dataset.tapa, sizes: '1080x1920', type: 'image/jpeg' }]
        });
      }
    });
    a.addEventListener('timeupdate', function () {
      if (a.duration && a.currentTime / a.duration >= 0.5) unaVez('mitad-' + n);
    });
    a.addEventListener('ended', function () { unaVez('fin-' + n); });
  });

  document.querySelectorAll('a[download]').forEach(function (a) {
    a.addEventListener('click', function () {
      var href = a.getAttribute('href') || '';
      var n = (href.match(/noche-(\d)/) || [])[1] || '0';
      medir(/\.mp3$/.test(href) ? 'descarga' : 'tarjeta', 'noche-' + n);
    });
  });

  document.querySelectorAll('[data-compartir]').forEach(function (boton) {
    boton.addEventListener('click', function () {
      medir('compartir');
      var datos = { title: 'Tres noches para soltar el día', text: 'Para cuando te acuestas y la cabeza no para.', url: location.origin + '/' };
      if (navigator.share) { navigator.share(datos).catch(function () {}); return; }
      if (navigator.clipboard) {
        navigator.clipboard.writeText(datos.url).then(function () { boton.textContent = 'Enlace copiado'; });
      }
    });
  });
})();
