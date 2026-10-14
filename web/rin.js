/* Rin · la landing, el formulario del regalo y la página de las noches.
   En la landing, la noche 1 suena ahí mismo, sin dejar ningún dato; el correo es para recibir las 3.
   El formulario guarda el correo en MailerLite (por la función /api/suscribir de Netlify) y, si no
   hay nada sonando, abre las noches enseguida: la persona recibe el regalo aunque el guardado
   tarde o falle. Si la noche 1 está sonando, no la corta: confirma ahí mismo.
   También mide el camino (función /api/evento): sin cookies ni datos personales. */
var RIN = {
  mailerlite: { cuenta: '1921447', formulario: '200892869569939404' },
  noches: '/tus-noches/'
};

(function () {
  var CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var INICIO = Date.now();
  var esRegalo = location.pathname.indexOf(RIN.noches) === 0;
  var ua = navigator.userAgent;
  var APP = /musical_ly|bytedancewebview|trill_/i.test(ua) ? 'TikTok' : /instagram/i.test(ua) ? 'Instagram' :
    /FBAN|FBAV|FB_IAB/.test(ua) ? 'Facebook' : '';
  var ICONOS = {
    play: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M8 5.5v13l11-6.5z"/></svg>',
    pausa: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z"/></svg>'
  };

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
    var q = new URLSearchParams(location.search), r = '';
    try { r = document.referrer ? new URL(document.referrer).hostname.replace(/^www\./, '') : ''; } catch (e) {}
    if (r === location.hostname.replace(/^www\./, '')) r = '';
    return q.get('o') || q.get('utm_source') || (q.get('ttclid') ? 'tiktok-promo' : '') ||
      (/musical_ly|bytedancewebview|tiktok|trill_/i.test(ua) ? 'tiktok' : '') ||
      (/instagram/i.test(ua) ? 'instagram' : '') || (/FBAN|FBAV|FB_IAB/.test(ua) ? 'facebook' : '') ||
      r || 'directo';
  }

  var SESION = recordar('rin-s') || recordar('rin-s', Math.random().toString(36).slice(2, 12));
  var ORIGEN = recordar('rin-o') || recordar('rin-o', calcularOrigen());

  // «h» es la hora del celular de la persona: dice si llegan a la hora de acostarse.
  function medir(evento, detalle) {
    try {
      var cuerpo = JSON.stringify({ e: evento, s: SESION, o: ORIGEN, x: detalle || '', h: new Date().getHours() });
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

  // Título y tarjeta en la pantalla bloqueada.
  function metadatos(a) {
    if (!('mediaSession' in navigator) || !window.MediaMetadata) return;
    navigator.mediaSession.metadata = new MediaMetadata({
      title: a.dataset.titulo, artist: 'Rin', album: 'Las 3 primeras noches',
      artwork: [{ src: a.dataset.tapa, sizes: '1080x1920', type: 'image/jpeg' }]
    });
  }

  // ── La noche 1 en la landing: un botón que la pone ahí mismo, sin dejar ningún dato ───────
  var reproductor = document.querySelector('[data-escucha]');
  var audioLanding = reproductor ? reproductor.querySelector('audio') : null;
  if (reproductor) {
    var botonEscucha = reproductor.querySelector('.boton');
    var barra = reproductor.querySelector('.barra i');
    var reloj = reproductor.querySelector('.reloj');
    var estado = reproductor.querySelector('.estado');
    var enApp = APP ? 'Dentro de ' + APP + ', deja la pantalla encendida: si la bloqueas, el sonido se corta.' : '';
    var minutos = function (s) {
      s = Math.max(0, Math.floor(s || 0));
      return Math.floor(s / 60) + ':' + ('0' + (s % 60)).slice(-2);
    };
    var pintar = function () {
      var sonando = !audioLanding.paused;
      var texto = sonando ? 'Pausar' : audioLanding.ended ? 'Escuchar de nuevo' :
        audioLanding.currentTime > 0 ? 'Seguir escuchando' : 'Escuchar la noche 1';
      botonEscucha.innerHTML = (sonando ? ICONOS.pausa : ICONOS.play) + '<span>' + texto + '</span>';
    };
    var poner = function () {
      var promesa = audioLanding.play();
      if (promesa && promesa.catch) {
        promesa.catch(function () {
          estado.textContent = 'No se pudo poner el sonido. Revisa la conexión y toca de nuevo.';
          pintar();
        });
      }
    };
    botonEscucha.addEventListener('click', function () {
      if (audioLanding.paused) poner(); else audioLanding.pause();
    });
    audioLanding.addEventListener('play', function () {
      reproductor.classList.add('empezo');
      pintar();
      unaVez('escucha');
      metadatos(audioLanding);
    });
    audioLanding.addEventListener('waiting', function () { estado.textContent = 'Cargando el sonido…'; });
    audioLanding.addEventListener('playing', function () { estado.textContent = enApp; });
    audioLanding.addEventListener('pause', pintar);
    audioLanding.addEventListener('timeupdate', function () {
      var t = audioLanding.currentTime, d = audioLanding.duration;
      if (d) {
        barra.style.width = (100 * t / d) + '%';
        reloj.textContent = minutos(t) + ' / ' + minutos(d);
      }
      if (t >= 60) unaVez('escucha-minuto');
      if (d && t / d >= 0.5) unaVez('escucha-mitad');
    });
    audioLanding.addEventListener('ended', function () { unaVez('escucha-fin'); pintar(); });
    pintar();

    // «Escucha la noche 1 ahora», al final de la página: sube al reproductor y la pone.
    document.querySelectorAll('[data-escuchar]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        reproductor.scrollIntoView({ behavior: 'smooth', block: 'center' });
        if (audioLanding.paused) poner();
      });
    });
  }

  // ── El formulario ─────────────────────────────────────────────────────────────────────────
  // Errores de tipeo que se arreglan solos: no existe «.con», y nadie usa «gmail.co».
  var ARREGLOS = [
    [/\.con$/, '.com'],
    [/@(gmial|gmal|gamil|gmai|gnail|gmaill)\.com$/, '@gmail.com'], [/@gmail\.co$/, '@gmail.com'],
    [/@(hotmal|hotmial|hotmai|homail|hotmaill|hormail)\.com$/, '@hotmail.com'], [/@hotmail\.co$/, '@hotmail.com'],
    [/@outlok\.com$/, '@outlook.com']
  ];
  function arreglar(texto) {
    var correo = texto.replace(/\s+/g, '').toLowerCase();
    ARREGLOS.forEach(function (a) { correo = correo.replace(a[0], a[1]); });
    return correo;
  }
  // Qué le falta al correo (se mide el tipo de error, nunca lo que escribió).
  function problema(correo) {
    if (!correo) return 'vacio';
    if (/^\+?[\d().-]{6,}$/.test(correo)) return 'telefono';
    if (correo.indexOf('@') < 0) return 'sin-arroba';
    if (correo.indexOf('@') === correo.lastIndexOf('@') && !/\.[^@.]{2,}$/.test(correo.split('@')[1])) return 'sin-punto';
    return 'otro';
  }
  var AYUDA = {
    vacio: 'Escribe tu correo y te mando las 3 noches.',
    telefono: 'Eso parece un teléfono. Aquí va un correo, como nombre@gmail.com.',
    'sin-arroba': 'A tu correo le falta la @, como en nombre@gmail.com.',
    'sin-punto': 'A tu correo le falta el final, como .com.',
    otro: 'Revisa tu correo: parece que falta algo.'
  };

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

  // Con la noche 1 sonando, el formulario se cambia por la confirmación y el sonido sigue.
  function confirmar(f, correo) {
    var p = document.createElement('p');
    p.className = 'listo';
    p.setAttribute('role', 'status');
    p.appendChild(document.createTextNode('Listo. En un minuto te llegan las 3 noches a '));
    var b = document.createElement('b');
    b.textContent = correo;
    p.appendChild(b);
    p.appendChild(document.createTextNode('. Si no lo ves, búscalo en Promociones.'));
    p.appendChild(document.createElement('br'));
    var a = document.createElement('a');
    a.href = RIN.noches + '?bienvenida=1';
    a.textContent = 'Ver las 3 noches ahora';
    p.appendChild(a);
    f.parentNode.replaceChild(p, f);
  }

  document.querySelectorAll('form[data-regalo]').forEach(function (f) {
    var campo = f.querySelector('input[type=email]');
    var boton = f.querySelector('button');
    var error = f.querySelector('.error');
    // El foco que pone la página después de un error no es «tocaron el campo»; tocarlo o escribir, sí.
    var porCodigo = false;
    var tocar = function () { if (!porCodigo) unaVez('campo'); };
    campo.addEventListener('focus', tocar);
    campo.addEventListener('pointerdown', tocar);
    campo.addEventListener('input', function () { unaVez('campo'); unaVez('escribe'); error.textContent = ''; });
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var correo = arreglar(campo.value);
      if (!CORREO.test(correo)) {
        var p = problema(correo);
        medir('correo-mal', p);
        error.textContent = AYUDA[p];
        porCodigo = true;
        campo.focus();
        porCodigo = false;
        return;
      }
      campo.value = correo;
      medir('clic');
      error.textContent = '';
      boton.disabled = true;
      boton.textContent = audioLanding && !audioLanding.paused ? 'Guardando…' : 'Abriendo tus noches…';
      var trampa = (f.querySelector('input[name=sitio_web]') || {}).value || '';
      suscribir(correo, trampa).then(function () {
        if (audioLanding && !audioLanding.paused) return confirmar(f, correo);
        setTimeout(function () { location.href = RIN.noches + '?bienvenida=1'; }, 250);
      });
    });
  });

  // ── Página de las noches: bienvenida, una sola noche sonando a la vez y datos para la
  //    pantalla bloqueada ────────────────────────────────────────────────────────────────────
  if (/[?&]bienvenida=1/.test(location.search)) {
    var b = document.querySelector('.bienvenida');
    if (b) b.hidden = false;
  }
  var audios = esRegalo ? document.querySelectorAll('audio[data-titulo]') : [];
  audios.forEach(function (a) {
    var n = ((a.getAttribute('src') || '').match(/noche-(\d)/) || [])[1] || '0';
    a.addEventListener('play', function () {
      unaVez('noche-' + n);
      audios.forEach(function (otro) { if (otro !== a) otro.pause(); });
      metadatos(a);
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
