/* Rin · formulario del regalo, muestra de audio y página de las noches.
   El formulario guarda el correo en MailerLite (por la función /api/suscribir de Netlify) y
   abre las noches enseguida: la persona recibe el regalo aunque el guardado tarde o falle. */
var RIN = {
  mailerlite: { cuenta: '1921447', formulario: '200892869569939404' },
  noches: '/tus-noches/'
};

(function () {
  var CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

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
      body: JSON.stringify({ correo: correo, sitio_web: trampa }),
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
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var correo = campo.value.trim();
      if (!CORREO.test(correo)) {
        error.textContent = 'Revisa tu correo: parece que falta algo.';
        campo.focus();
        return;
      }
      error.textContent = '';
      boton.disabled = true;
      boton.textContent = 'Abriendo tus noches…';
      var trampa = (f.querySelector('input[name=sitio_web]') || {}).value || '';
      suscribir(correo, trampa).then(function () {
        setTimeout(function () { location.href = RIN.noches + '?bienvenida=1'; }, 250);
      });
    });
  });

  // Muestra de la landing: un botón que reproduce y pausa, con una barra de avance.
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
    audio.addEventListener('play', pintar);
    audio.addEventListener('pause', pintar);
    audio.addEventListener('ended', function () { audio.currentTime = 0; pintar(); });
    audio.addEventListener('timeupdate', function () {
      if (audio.duration) barra.style.width = (100 * audio.currentTime / audio.duration) + '%';
    });
    pintar();
  });

  // Página de las noches: bienvenida, una sola noche sonando a la vez y datos para la pantalla bloqueada.
  if (/[?&]bienvenida=1/.test(location.search)) {
    var b = document.querySelector('.bienvenida');
    if (b) b.hidden = false;
  }
  var audios = document.querySelectorAll('audio[data-titulo]');
  audios.forEach(function (a) {
    a.addEventListener('play', function () {
      audios.forEach(function (otro) { if (otro !== a) otro.pause(); });
      if ('mediaSession' in navigator && window.MediaMetadata) {
        navigator.mediaSession.metadata = new MediaMetadata({
          title: a.dataset.titulo, artist: 'Rin', album: 'Las 3 primeras noches',
          artwork: [{ src: a.dataset.tapa, sizes: '1080x1920', type: 'image/jpeg' }]
        });
      }
    });
  });

  document.querySelectorAll('[data-compartir]').forEach(function (boton) {
    boton.addEventListener('click', function () {
      var datos = { title: 'Tres noches para soltar el día', text: 'Para cuando te acuestas y la cabeza no para.', url: location.origin + '/' };
      if (navigator.share) { navigator.share(datos).catch(function () {}); return; }
      if (navigator.clipboard) {
        navigator.clipboard.writeText(datos.url).then(function () { boton.textContent = 'Enlace copiado'; });
      }
    });
  });
})();
