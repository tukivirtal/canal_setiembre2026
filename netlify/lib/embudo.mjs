// El embudo de la web del regalo: qué pasa entre que alguien llega a la página y deja el correo.
//
// Cada evento se guarda en Netlify Blobs (almacén «embudo») como una clave que lleva todo en el
// nombre:   día / evento / origen / país / dispositivo / sesión / detalle / azar
// Así dos visitas al mismo tiempo nunca pisan el mismo contador, y para sumar alcanza con listar
// las claves de cada día, sin abrirlas.
//
// No se guarda la IP, ni el correo, ni cookies. La sesión es un número al azar que vive en la
// pestaña (sessionStorage) y sirve para contar personas en vez de toques repetidos.
import { createHash, timingSafeEqual } from 'node:crypto';

export const ALMACEN = 'embudo';
export const ZONA = 'America/Argentina/Buenos_Aires';

// Los que manda la página. «guardado», «fallo» y «trampa» solo los registra el servidor.
export const EVENTOS_PAGINA = new Set([
  'visita', 'campo', 'correo-mal', 'clic', 'visita-regalo', 'muestra', 'muestra-fin',
  'noche-1', 'noche-2', 'noche-3', 'mitad-1', 'mitad-2', 'mitad-3', 'fin-1', 'fin-2', 'fin-3',
  'descarga', 'tarjeta', 'compartir', 'salida',
]);

export const ORIGENES = /^https:\/\/((www\.)?estudioarmonia\.com|([a-z0-9-]+--)?estudioarmonia\.netlify\.app)$/;
// Los robots casi nunca ejecutan JavaScript, pero los que sí (vistas previas de enlaces,
// revisores de anuncios) no son personas.
const ROBOTS = /bot[/\-_;)]|\bbot\b|adsbot|crawl|spider|slurp|preview|facebookexternalhit|headless|lighthouse|python|curl|wget|axios/i;

export const limpio = (v, max = 32) =>
  String(v ?? '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, max) || 'x';

export const dia = (fecha = new Date()) =>
  new Intl.DateTimeFormat('en-CA', { timeZone: ZONA, year: 'numeric', month: '2-digit', day: '2-digit' }).format(fecha);

export function dispositivo(ua = '') {
  if (/iphone|ipad|ipod/i.test(ua)) return 'ios';
  if (/android/i.test(ua)) return 'android';
  if (/mobile/i.test(ua)) return 'movil';
  return 'compu';
}

// El navegador de cada app se delata en su «user agent».
export function origenPorNavegador(ua = '') {
  if (/musical_ly|bytedancewebview|tiktok|trill_/i.test(ua)) return 'tiktok';
  if (/instagram/i.test(ua)) return 'instagram';
  if (/fban|fbav|fb_iab/i.test(ua)) return 'facebook';
  return 'web';
}

export const pais = (context) => context?.geo?.country?.code || 'xx';

export function clave({ evento, origen, pais: p, disp, sesion, detalle, fecha = new Date() }) {
  return [dia(fecha), limpio(evento, 16), limpio(origen, 24), limpio(p, 3), limpio(disp, 8),
    limpio(sesion, 16), limpio(detalle, 24), Math.random().toString(36).slice(2, 8)].join('/');
}

export function leer(k) {
  const [d, evento, origen, p, disp, sesion, detalle] = k.split('/');
  return { dia: d, evento, origen, pais: p, disp, sesion, detalle };
}

// Medir nunca puede romper el regalo: si falla, se anota en el registro y sigue.
export async function registrar(store, datos) {
  try {
    await store.set(clave(datos), '1');
    return true;
  } catch (e) {
    console.error('No se pudo registrar', datos.evento, e?.message);
    return false;
  }
}

// POST /api/evento, desde la página (con sendBeacon). Responde 204 y nada más.
export async function manejarEvento(req, context, store) {
  if (req.method !== 'POST') return new Response(null, { status: 405 });
  const origenWeb = req.headers.get('origin');
  if (origenWeb && !ORIGENES.test(origenWeb)) return new Response(null, { status: 403 });
  const ua = req.headers.get('user-agent') || '';
  if (ROBOTS.test(ua)) return new Response(null, { status: 204 });
  const texto = await req.text();
  if (texto.length > 1500) return new Response(null, { status: 413 });
  let d;
  try { d = JSON.parse(texto); } catch { return new Response(null, { status: 400 }); }
  if (!d || !EVENTOS_PAGINA.has(d.e)) return new Response(null, { status: 400 });
  await registrar(store, {
    evento: d.e, origen: d.o || origenPorNavegador(ua), pais: pais(context),
    disp: dispositivo(ua), sesion: d.s, detalle: d.x,
  });
  return new Response(null, { status: 204 });
}

// ── El tablero ─────────────────────────────────────────────────────────────────────────────

const SEGUNDOS = [['s0', 'menos de 3 s'], ['s3', '3 a 10 s'], ['s10', '10 a 30 s'], ['s30', '30 s a 1,5 min'], ['s90', 'más de 1,5 min']];
const BAJARON = [['p0', 'no bajaron'], ['p25', 'un cuarto'], ['p50', 'la mitad'], ['p75', 'tres cuartos'], ['p100', 'hasta el final']];

export function resumir(claves) {
  const eventos = claves.map(leer).filter((e) => e.sesion);
  const sesiones = new Map();
  for (const e of eventos) {
    let s = sesiones.get(e.sesion);
    if (!s) sesiones.set(e.sesion, (s = { eventos: new Set(), salidas: [] }));
    s.eventos.add(e.evento);
    // La sesión toma el origen, el país y el día de su primera visita a la landing.
    if (e.evento === 'visita' && !s.origen) Object.assign(s, { origen: e.origen, pais: e.pais, disp: e.disp, dia: e.dia });
    if (e.evento === 'salida') s.salidas.push(e.detalle);
  }
  for (const [id, s] of sesiones) {
    if (!s.origen) {
      const primero = eventos.find((e) => e.sesion === id);
      Object.assign(s, { origen: primero.origen, pais: primero.pais, disp: primero.disp, dia: primero.dia });
    }
  }
  const lista = [...sesiones.values()];
  const con = (ev, grupo = lista) => grupo.filter((s) => s.eventos.has(ev)).length;
  const llegaron = lista.filter((s) => s.eventos.has('visita'));
  const regalo = eventos.filter((e) => e.evento === 'visita-regalo');
  const abrieron = new Set(regalo.filter((e) => e.detalle === 'form').map((e) => e.sesion)).size;
  const volvieron = new Set(regalo.filter((e) => e.detalle !== 'form').map((e) => e.sesion)).size;
  const pusieron = lista.filter((s) => ['noche-1', 'noche-2', 'noche-3'].some((n) => s.eventos.has(n))).length;

  const embudo = [
    ['Llegaron a la página', llegaron.length],
    ['Tocaron el campo del correo', con('campo', llegaron)],
    ['Tocaron «Quiero mis 3 noches»', con('clic', llegaron)],
    ['Su correo quedó guardado', con('guardado')],
    ['Abrieron las noches', abrieron],
    ['Pusieron una noche', pusieron],
  ];

  // Los que se fueron sin tocar el botón: cuánto se quedaron y cuánto bajaron.
  const seFueron = llegaron.filter((s) => !s.eventos.has('clic'));
  const tiempo = new Map(SEGUNDOS.map(([k]) => [k, 0]));
  const scroll = new Map(BAJARON.map(([k]) => [k, 0]));
  let sinDato = 0;
  for (const s of seFueron) {
    const d = s.salidas.find((x) => x.startsWith('l-'));
    if (!d) { sinDato++; continue; }
    const [, seg, baj] = d.split('-');
    if (tiempo.has(seg)) tiempo.set(seg, tiempo.get(seg) + 1);
    if (scroll.has(baj)) scroll.set(baj, scroll.get(baj) + 1);
  }

  const agrupar = (campo) => {
    const m = new Map();
    for (const s of llegaron) {
      const g = m.get(s[campo]) || { llegaron: 0, clic: 0, guardado: 0 };
      g.llegaron++;
      if (s.eventos.has('clic')) g.clic++;
      if (s.eventos.has('guardado')) g.guardado++;
      m.set(s[campo], g);
    }
    return [...m.entries()].sort((a, b) => b[1].llegaron - a[1].llegaron);
  };

  const cuenta = (ev) => eventos.filter((e) => e.evento === ev).length;
  const fallos = eventos.filter((e) => e.evento === 'fallo').map((e) => e.detalle);

  return {
    embudo, sinDato, seFueron: seFueron.length,
    tiempo: SEGUNDOS.map(([k, t]) => [t, tiempo.get(k)]),
    scroll: BAJARON.map(([k, t]) => [t, scroll.get(k)]),
    origen: agrupar('origen'), pais: agrupar('pais'), disp: agrupar('disp'),
    porDia: agrupar('dia').sort((a, b) => (a[0] < b[0] ? 1 : -1)),
    noches: [1, 2, 3].map((n) => [n, con(`noche-${n}`), con(`mitad-${n}`), con(`fin-${n}`)]),
    muestra: [con('muestra'), con('muestra-fin')],
    volvieron, descargas: cuenta('descarga'), tarjetas: cuenta('tarjeta'), compartir: con('compartir'),
    correoMal: con('correo-mal'), fallos, trampas: cuenta('trampa'), eventos: eventos.length,
  };
}

const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const pct = (a, b) => (b ? `${Math.round((100 * a) / b)} %` : '—');
const NOMBRES = {
  tiktok: 'TikTok', 'tiktok-promo': 'TikTok (promoción)', promo: 'Promoción', bio: 'Biografía de TikTok',
  instagram: 'Instagram', facebook: 'Facebook', web: 'Navegador (sin app)', directo: 'Directo',
  ios: 'iPhone', android: 'Android', movil: 'Otro celular', compu: 'Computadora', xx: 'Sin dato',
};
const nombre = (k) => NOMBRES[k] || k;
const PAISES = {
  ar: 'Argentina', mx: 'México', cl: 'Chile', uy: 'Uruguay', co: 'Colombia', pe: 'Perú', es: 'España',
  us: 'Estados Unidos', ve: 'Venezuela', ec: 'Ecuador', py: 'Paraguay', bo: 'Bolivia', cr: 'Costa Rica',
  gt: 'Guatemala', do: 'Rep. Dominicana', pa: 'Panamá', hn: 'Honduras', sv: 'El Salvador', ni: 'Nicaragua',
  pr: 'Puerto Rico', br: 'Brasil', xx: 'Sin dato',
};
const nombrePais = (k) => PAISES[k] || String(k).toUpperCase();
const fechaCorta = (d) => d.split('-').reverse().join('/');

function barras(filas, total) {
  return filas.map(([t, n]) => `<div class="fila"><span class="t">${esc(t)}</span><span class="n">${n}</span>` +
    `<span class="p">${pct(n, total)}</span><i style="width:${total ? Math.round((100 * n) / total) : 0}%"></i></div>`).join('');
}

function tabla(grupos, fmt = nombre) {
  if (!grupos.length) return '<p class="nada">Todavía sin visitas.</p>';
  return '<table><tr><th></th><th>Llegaron</th><th>Botón</th><th>Correo</th><th>%</th></tr>' +
    grupos.map(([k, g]) => `<tr><td>${esc(fmt(k))}</td><td>${g.llegaron}</td><td>${g.clic}</td><td>${g.guardado}</td>` +
      `<td>${pct(g.guardado, g.llegaron)}</td></tr>`).join('') + '</table>';
}

export function pagina(r, { dias, clave: c, desde, hasta }) {
  const llegaron = r.embudo[0][1];
  const periodo = (d, t) => `<a${d === dias ? ' class="activo"' : ''} href="?clave=${encodeURIComponent(c)}&dias=${d}">${t}</a>`;
  return `<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>Embudo · Estudio Armonía</title><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
  :root{--oro:#e6c46a;--crema:#f6e7b8;--texto:#ece4d2;--suave:#a39b8b;--borde:rgba(230,196,106,.22)}
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#0b0c0f;color:var(--texto);font:16px/1.45 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;padding:18px 16px 40px;max-width:640px;margin:0 auto}
  h1{font:600 1.5rem Georgia,serif;color:var(--crema)}
  h2{font:600 .78rem system-ui;letter-spacing:.14em;text-transform:uppercase;color:var(--oro);margin:26px 0 10px}
  .periodo{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}
  .periodo a{color:var(--texto);text-decoration:none;border:1px solid var(--borde);border-radius:999px;padding:4px 12px;font-size:.9rem}
  .periodo a.activo{background:var(--oro);color:#17130a;border-color:var(--oro);font-weight:700}
  .suave{color:var(--suave);font-size:.85rem;margin-top:6px}
  .caja{border:1px solid var(--borde);border-radius:14px;padding:12px 14px;background:rgba(255,255,255,.02)}
  .fila{position:relative;display:flex;gap:10px;align-items:baseline;padding:7px 0;border-bottom:1px solid rgba(255,255,255,.05)}
  .fila:last-child{border-bottom:0}
  .fila .t{flex:1}.fila .n{font-weight:700;color:var(--crema);min-width:38px;text-align:right}.fila .p{color:var(--suave);min-width:44px;text-align:right;font-size:.9rem}
  .fila i{position:absolute;left:0;bottom:0;height:2px;background:var(--oro);opacity:.7}
  table{width:100%;border-collapse:collapse;font-size:.92rem}
  th{color:var(--suave);font-weight:600;font-size:.78rem;text-align:right;padding:4px 0 6px 10px;vertical-align:bottom}
  td{padding:6px 0 6px 10px;border-top:1px solid rgba(255,255,255,.05);text-align:right;white-space:nowrap}
  th:first-child,td:first-child{text-align:left;padding-left:0;white-space:normal}
  .nada{color:var(--suave)}
  .alerta{color:#f0a48c}
</style></head><body>
<h1>Embudo del regalo</h1>
<div class="periodo">${periodo(1, 'Hoy')}${periodo(7, '7 días')}${periodo(30, '30 días')}</div>
<p class="suave">Del ${esc(fechaCorta(desde))} al ${esc(fechaCorta(hasta))}, en hora de Argentina. Personas, no toques: cada una cuenta una vez por paso.</p>

<h2>El camino</h2>
<div class="caja">${barras(r.embudo, llegaron)}</div>

<h2>Los que se fueron sin tocar el botón (${r.seFueron})</h2>
<div class="caja"><p class="suave" style="margin:0 0 4px">Cuánto se quedaron</p>${barras(r.tiempo, r.seFueron)}</div>
<div class="caja" style="margin-top:10px"><p class="suave" style="margin:0 0 4px">Cuánto bajaron en la página</p>${barras(r.scroll, r.seFueron)}</div>
${r.sinDato ? `<p class="suave">${r.sinDato} sin dato de salida (la app cerró la página de golpe).</p>` : ''}

<h2>De dónde llegan</h2>
<div class="caja">${tabla(r.origen)}</div>

<h2>Países</h2>
<div class="caja">${tabla(r.pais, nombrePais)}</div>

<h2>Dispositivos</h2>
<div class="caja">${tabla(r.disp)}</div>

<h2>Por día</h2>
<div class="caja">${tabla(r.porDia, fechaCorta)}</div>

<h2>Las noches</h2>
<div class="caja"><table><tr><th></th><th>La pusieron</th><th>Pasaron la mitad</th><th>Hasta el final</th></tr>
${r.noches.map(([n, a, b, c2]) => `<tr><td style="white-space:nowrap">Noche ${n}</td><td>${a}</td><td>${b}</td><td>${c2}</td></tr>`).join('')}</table>
<p class="suave">Muestra de la landing: la escucharon ${r.muestra[0]}, entera ${r.muestra[1]}. Volvieron a las noches desde el correo: ${r.volvieron}.
Descargaron audios: ${r.descargas}. Guardaron tarjetas: ${r.tarjetas}. Compartieron: ${r.compartir}.</p></div>

<h2>Problemas</h2>
<div class="caja"><p>Escribieron mal el correo: <b>${r.correoMal}</b></p>
<p${r.fallos.length ? ' class="alerta"' : ''}>No se pudo guardar el correo: <b>${r.fallos.length}</b>${r.fallos.length ? ` (${esc([...new Set(r.fallos)].join(', '))})` : ''}</p>
<p class="suave">Robots que cayeron en la trampa: ${r.trampas}. Eventos en el período: ${r.eventos}.</p></div>

<p class="suave" style="margin-top:24px">Sin cookies ni datos personales: no se guarda la IP ni el correo. Los números pueden tardar hasta un minuto en aparecer.</p>
</body></html>`;
}

function aviso(texto) {
  return `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>Embudo</title></head>
<body style="background:#0b0c0f;color:#ece4d2;font:17px/1.5 system-ui,sans-serif;padding:24px">${esc(texto)}</body></html>`;
}

const html = (estado, cuerpo) => new Response(cuerpo, {
  status: estado,
  headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex' },
});

const iguales = (a, b) => timingSafeEqual(createHash('sha256').update(a).digest(), createHash('sha256').update(b).digest());

// GET /api/embudo?clave=…&dias=7. La clave vive en Netlify (variable EMBUDO_CLAVE), nunca en el repositorio.
export async function manejarEmbudo(req, store, claveEsperada) {
  const url = new URL(req.url);
  const dada = url.searchParams.get('clave') || '';
  if (!claveEsperada) {
    return html(503, aviso('Falta la variable EMBUDO_CLAVE en Netlify (Project configuration → Environment variables). ' +
      'Después de crearla, publica de nuevo el sitio (Deploys → Trigger deploy).'));
  }
  if (!iguales(dada, claveEsperada)) return html(403, aviso('La clave no es correcta.'));
  const dias = Math.min(Math.max(parseInt(url.searchParams.get('dias'), 10) || 7, 1), 31);
  const ahora = Date.now();
  const fechas = [...new Set(Array.from({ length: dias }, (_, i) => dia(new Date(ahora - i * 864e5))))];
  const claves = [];
  for (const f of fechas) {
    const { blobs } = await store.list({ prefix: `${f}/` });
    for (const b of blobs) claves.push(b.key);
  }
  return html(200, pagina(resumir(claves), { dias, clave: dada, desde: fechas.at(-1), hasta: fechas[0] }));
}
