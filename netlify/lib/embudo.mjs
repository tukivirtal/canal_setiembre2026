// El embudo de la web del regalo: qué pasa entre que alguien llega a la página y deja el correo.
//
// Cada evento se guarda en Netlify Blobs (almacén «embudo») como una clave que lleva todo en el
// nombre:   día / evento / origen / país / dispositivo / sesión / detalle / hora y azar
// Así dos visitas al mismo tiempo nunca pisan el mismo contador, y para sumar alcanza con listar
// las claves de cada día, sin abrirlas. La hora es la del celular de la persona («h19-…»); las
// claves anteriores al 14/10 no la tienen.
//
// No se guarda la IP, ni el correo, ni cookies. La sesión es un número al azar que vive en la
// pestaña (sessionStorage) y sirve para contar personas en vez de toques repetidos.
import { createHash, timingSafeEqual } from 'node:crypto';
import { excel } from './excel.mjs';

export const ALMACEN = 'embudo';
export const ZONA = 'America/Argentina/Buenos_Aires';

// Los que manda la página. «guardado», «fallo» y «trampa» solo los registra el servidor.
// «muestra» y «muestra-fin» son de la landing anterior al 14/10 (la noche 1 ahora suena entera).
export const EVENTOS_PAGINA = new Set([
  'visita', 'escucha', 'escucha-minuto', 'escucha-mitad', 'escucha-fin',
  'campo', 'escribe', 'correo-mal', 'clic', 'visita-regalo', 'muestra', 'muestra-fin',
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

const horaValida = (h) => (Number.isInteger(h) && h >= 0 && h < 24 ? String(h).padStart(2, '0') : 'xx');

export function clave({ evento, origen, pais: p, disp, sesion, detalle, hora, fecha = new Date() }) {
  return [dia(fecha), limpio(evento, 16), limpio(origen, 24), limpio(p, 3), limpio(disp, 8),
    limpio(sesion, 16), limpio(detalle, 24), `h${horaValida(hora)}-${Math.random().toString(36).slice(2, 8)}`].join('/');
}

export function leer(k) {
  const [d, evento, origen, p, disp, sesion, detalle, azar = ''] = k.split('/');
  return { dia: d, evento, origen, pais: p, disp, sesion, detalle, hora: (/^h(\d\d)-/.exec(azar) || [])[1] || 'xx' };
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
    disp: dispositivo(ua), sesion: d.s, detalle: d.x, hora: d.h,
  });
  return new Response(null, { status: 204 });
}

// ── El tablero ─────────────────────────────────────────────────────────────────────────────

const ERRORES = [['vacio', 'sin escribir nada'], ['telefono', 'un teléfono'], ['sin-arroba', 'sin la @'],
  ['sin-punto', 'sin el final (.com)'], ['otro', 'otro error'], ['x', 'sin dato (antes del 14/10)']];
const PASOS = { escucha: 'escucha', minuto: 'escucha-minuto', campo: 'campo', escribe: 'escribe', clic: 'clic', guardado: 'guardado' };
const SEGUNDOS = [['s0', 'menos de 3 s'], ['s3', '3 a 10 s'], ['s10', '10 a 30 s'], ['s30', '30 s a 1,5 min'], ['s90', 'más de 1,5 min']];
const BAJARON = [['p0', 'no bajaron'], ['p25', 'un cuarto'], ['p50', 'la mitad'], ['p75', 'tres cuartos'], ['p100', 'hasta el final']];

export function resumir(claves) {
  const eventos = claves.map(leer).filter((e) => e.sesion);
  const sesiones = new Map();
  for (const e of eventos) {
    let s = sesiones.get(e.sesion);
    if (!s) sesiones.set(e.sesion, (s = { id: e.sesion, eventos: new Set(), salidas: [], errores: new Set(), regalo: new Set() }));
    s.eventos.add(e.evento);
    // La sesión toma el origen, el país, el día y la hora de su primera visita a la landing.
    if (e.evento === 'visita' && !s.origen) Object.assign(s, { origen: e.origen, pais: e.pais, disp: e.disp, dia: e.dia, hora: e.hora });
    if (e.evento === 'salida') s.salidas.push(e.detalle);
    if (e.evento === 'correo-mal') s.errores.add(e.detalle);
    if (e.evento === 'visita-regalo') s.regalo.add(e.detalle);
  }
  for (const [id, s] of sesiones) {
    if (!s.origen) {
      const primero = eventos.find((e) => e.sesion === id);
      Object.assign(s, { origen: primero.origen, pais: primero.pais, disp: primero.disp, dia: primero.dia, hora: primero.hora });
    }
  }
  const lista = [...sesiones.values()];
  const con = (ev, grupo = lista) => grupo.filter((s) => s.eventos.has(ev)).length;
  const llegaron = lista.filter((s) => s.eventos.has('visita'));
  const regalo = eventos.filter((e) => e.evento === 'visita-regalo');
  const abrieron = new Set(regalo.filter((e) => e.detalle === 'form').map((e) => e.sesion)).size;
  const volvieron = new Set(regalo.filter((e) => e.detalle !== 'form').map((e) => e.sesion)).size;
  const pusieron = lista.filter((s) => ['noche-1', 'noche-2', 'noche-3'].some((n) => s.eventos.has(n))).length;

  // Desde el 14/10 la noche 1 suena en la landing sin dejar el correo; el correo es para recibir las 3.
  const embudo = [
    ['Llegaron a la página', llegaron.length],
    ['Pusieron la noche 1', con('escucha', llegaron)],
    ['La escucharon más de 1 minuto', con('escucha-minuto', llegaron)],
    ['Tocaron el campo del correo', con('campo', llegaron)],
    ['Empezaron a escribirlo', con('escribe', llegaron)],
    ['Lo mandaron bien escrito', con('clic', llegaron)],
    ['Su correo quedó guardado', con('guardado')],
  ];

  // Los que se fueron sin escuchar ni dejar el correo: cuánto se quedaron y cuánto bajaron.
  const seFueron = llegaron.filter((s) => !s.eventos.has('escucha') && !s.eventos.has('clic'));
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

  // Cada paso del camino por origen, país, dispositivo, día u hora (el tablero muestra tres; el Excel, todos).
  const agrupar = (campo) => {
    const m = new Map();
    for (const s of llegaron) {
      const g = m.get(s[campo]) || Object.fromEntries(['llegaron', ...Object.keys(PASOS)].map((k) => [k, 0]));
      g.llegaron++;
      for (const [k, ev] of Object.entries(PASOS)) if (s.eventos.has(ev)) g[k]++;
      m.set(s[campo], g);
    }
    return [...m.entries()].sort((a, b) => b[1].llegaron - a[1].llegaron);
  };

  const cuenta = (ev) => eventos.filter((e) => e.evento === ev).length;
  const fallos = eventos.filter((e) => e.evento === 'fallo').map((e) => e.detalle);
  // Qué tenía mal el correo, en personas (antes del 14/10 no se anotaba: «x»).
  const tipos = new Map();
  for (const s of lista) for (const t of s.errores) tipos.set(t, (tipos.get(t) || 0) + 1);

  return {
    embudo, sinDato, seFueron: seFueron.length,
    tiempo: SEGUNDOS.map(([k, t]) => [t, tiempo.get(k)]),
    scroll: BAJARON.map(([k, t]) => [t, scroll.get(k)]),
    origen: agrupar('origen'), pais: agrupar('pais'), disp: agrupar('disp'),
    porDia: agrupar('dia').sort((a, b) => (a[0] < b[0] ? 1 : -1)),
    hora: agrupar('hora').sort((a, b) => a[0].localeCompare(b[0])),
    landing: [con('escucha'), con('escucha-minuto'), con('escucha-mitad'), con('escucha-fin')],
    noches: [1, 2, 3].map((n) => [n, con(`noche-${n}`), con(`mitad-${n}`), con(`fin-${n}`)]),
    abrieron, pusieron, volvieron, descargas: cuenta('descarga'), tarjetas: cuenta('tarjeta'), compartir: con('compartir'),
    correoMal: con('correo-mal'), errores: ERRORES.map(([k, t]) => [t, tipos.get(k) || 0]).filter(([, n]) => n),
    fallos, trampas: cuenta('trampa'), eventos: eventos.length, personas: lista,
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
const REGIONES = (() => { try { return new Intl.DisplayNames(['es'], { type: 'region' }); } catch { return null; } })();
function nombrePais(k) {
  if (PAISES[k]) return PAISES[k];
  try { return REGIONES?.of(String(k).toUpperCase()) || String(k).toUpperCase(); } catch { return String(k).toUpperCase(); }
}
const nombreHora = (h) => (h === 'xx' ? 'Sin dato' : `${Number(h)} h`);
const fechaCorta = (d) => d.split('-').reverse().join('/');

function barras(filas, total) {
  return filas.map(([t, n]) => `<div class="fila"><span class="t">${esc(t)}</span><span class="n">${n}</span>` +
    `<span class="p">${pct(n, total)}</span><i style="width:${total ? Math.round((100 * n) / total) : 0}%"></i></div>`).join('');
}

function tabla(grupos, fmt = nombre) {
  if (!grupos.length) return '<p class="nada">Todavía sin visitas.</p>';
  return '<table><tr><th></th><th>Llegaron</th><th>Escucharon</th><th>Correo</th><th>%</th></tr>' +
    grupos.map(([k, g]) => `<tr><td>${esc(fmt(k))}</td><td>${g.llegaron}</td><td>${g.escucha}</td><td>${g.guardado}</td>` +
      `<td>${pct(g.guardado, g.llegaron)}</td></tr>`).join('') + '</table>';
}

export function pagina(r, { dias, clave: c, desde, hasta }) {
  const llegaron = r.embudo[0][1];
  const periodo = (d, t) => `<form method="post" action="/api/embudo"><input type="hidden" name="clave" value="${esc(c)}">` +
    `<input type="hidden" name="dias" value="${d}"><button${d === dias ? ' class="activo"' : ''}>${t}</button></form>`;
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
  .periodo button{color:var(--texto);background:none;border:1px solid var(--borde);border-radius:999px;padding:5px 14px;font:inherit;font-size:.9rem;cursor:pointer}
  .periodo button.activo{background:var(--oro);color:#17130a;border-color:var(--oro);font-weight:700}
  .excel button{margin-top:12px;color:var(--oro);background:none;border:1px solid var(--oro);border-radius:10px;padding:8px 14px;font:inherit;font-size:.9rem;cursor:pointer}
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
<form class="excel" method="post" action="/api/embudo"><input type="hidden" name="clave" value="${esc(c)}">
<input type="hidden" name="dias" value="${dias}"><input type="hidden" name="formato" value="xlsx"><button>Descargar Excel de este período</button></form>
<p class="suave">Del ${esc(fechaCorta(desde))} al ${esc(fechaCorta(hasta))}, en hora de Argentina. Personas, no toques: cada una cuenta una vez por paso.</p>

<h2>El camino</h2>
<div class="caja">${barras(r.embudo, llegaron)}</div>

<h2>Los que se fueron sin escuchar ni dejar el correo (${r.seFueron})</h2>
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

<h2>A qué hora llegan</h2>
<div class="caja">${tabla(r.hora, nombreHora)}</div>
<p class="suave">La hora del celular de cada persona (en México, tres horas menos que en Uruguay). Desde el 14/10.</p>

<h2>Las noches</h2>
<div class="caja"><table><tr><th></th><th>La pusieron</th><th>Pasaron la mitad</th><th>Hasta el final</th></tr>
<tr><td>Noche 1, en la página principal</td><td>${r.landing[0]}</td><td>${r.landing[2]}</td><td>${r.landing[3]}</td></tr>
${r.noches.map(([n, a, b, c2]) => `<tr><td style="white-space:nowrap">Noche ${n}</td><td>${a}</td><td>${b}</td><td>${c2}</td></tr>`).join('')}</table>
<p class="suave">Las noches 1, 2 y 3 son las de la página «Tus 3 primeras noches». La abrieron al dejar el correo: ${r.abrieron}.
Volvieron desde el correo: ${r.volvieron}. Pusieron alguna ahí: ${r.pusieron}. Descargaron audios: ${r.descargas}.
Guardaron tarjetas: ${r.tarjetas}. Compartieron: ${r.compartir}.</p></div>

<h2>Problemas</h2>
<div class="caja"><p>Mandaron el correo mal escrito: <b>${r.correoMal}</b>${r.errores.length ? ` <span class="suave">(${esc(r.errores.map(([t, n]) => `${t}: ${n}`).join(' · '))})</span>` : ''}</p>
<p${r.fallos.length ? ' class="alerta"' : ''}>No se pudo guardar el correo: <b>${r.fallos.length}</b>${r.fallos.length ? ` (${esc([...new Set(r.fallos)].join(', '))})` : ''}</p>
<p class="suave">Robots que cayeron en la trampa: ${r.trampas}. Eventos en el período: ${r.eventos}.</p></div>

<p class="suave" style="margin-top:24px">Sin cookies ni datos personales: no se guarda la IP ni el correo. Los números pueden tardar hasta un minuto en aparecer.</p>
</body></html>`;
}

// ── El Excel ──────────────────────────────────────────────────────────────────────────────
// Lo mismo que el tablero, y además una fila por persona y una por evento: para mirar todo sin capturas.

const QUE_ES = {
  visita: 'Llegó a la página principal',
  escucha: 'Puso la noche 1 en la página principal',
  'escucha-minuto': 'Pasó 1 minuto con la noche 1',
  'escucha-mitad': 'Pasó la mitad de la noche 1',
  'escucha-fin': 'Escuchó la noche 1 entera',
  muestra: 'Puso la muestra (página anterior al 14/10)',
  'muestra-fin': 'Escuchó la muestra entera (página anterior al 14/10)',
  campo: 'Tocó el campo del correo',
  escribe: 'Empezó a escribir el correo',
  'correo-mal': 'Mandó el correo mal escrito (detalle: qué le faltaba)',
  clic: 'Mandó el correo bien escrito',
  trampa: 'Un robot cayó en la trampa del formulario',
  guardado: 'Su correo quedó guardado en MailerLite',
  fallo: 'No se pudo guardar el correo (detalle: por qué)',
  'visita-regalo': 'Abrió la página de las noches (form: al dejar el correo; vuelve: desde el correo u otro enlace)',
  ...Object.fromEntries([1, 2, 3].flatMap((n) => [
    [`noche-${n}`, `Puso la noche ${n} en la página de las noches`],
    [`mitad-${n}`, `Pasó la mitad de la noche ${n}`],
    [`fin-${n}`, `Escuchó la noche ${n} entera`],
  ])),
  descarga: 'Descargó un audio (detalle: cuál)',
  tarjeta: 'Guardó una tarjeta (detalle: cuál)',
  compartir: 'Tocó «Pasarle estas noches»',
  salida: 'Se fue o pasó a otra app (detalle: l = página principal o r = noches, segundos y cuánto bajó)',
};
const ORDEN = Object.fromEntries(Object.keys(QUE_ES).map((k, i) => [k, i]));
const etiqueta = (lista, k) => (lista.find(([c]) => c === k) || [k, ''])[1];
const ahora = () => new Intl.DateTimeFormat('es-AR', { timeZone: ZONA, year: 'numeric', month: '2-digit', day: '2-digit',
  hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).format(new Date());

const PASOS_EXCEL = ['Llegaron', 'Pusieron la noche 1', 'Más de 1 minuto', 'Tocaron el campo', 'Empezaron a escribir',
  'Lo mandaron bien', 'Guardados', '% guardados'];
const porGrupo = (nombreHoja, titulo, grupos, fmt) => ({
  nombre: nombreHoja, fijarPrimera: true, anchos: [26, 10, 12, 12, 12, 12, 12, 11, 11],
  filas: [[titulo, ...PASOS_EXCEL].map((t) => ({ titulo: t })),
    ...grupos.map(([k, g]) => [fmt(k), g.llegaron, g.escucha, g.minuto, g.campo, g.escribe, g.clic, g.guardado,
      { pct: g.llegaron ? g.guardado / g.llegaron : NaN }])],
});

function filaPersona(s) {
  const si = (ev) => (s.eventos.has(ev) ? 1 : '');
  const [, seg, baj] = (s.salidas.find((x) => x.startsWith('l-')) || '').split('-');
  return [{ fecha: s.dia }, s.hora === 'xx' ? '' : Number(s.hora), nombre(s.origen), nombrePais(s.pais), nombre(s.disp),
    si('visita'), si('escucha'), si('escucha-minuto'), si('escucha-mitad'), si('escucha-fin'),
    si('campo'), si('escribe'), [...s.errores].map((t) => etiqueta(ERRORES, t)).join(', '), si('clic'), si('guardado'),
    etiqueta(SEGUNDOS, seg), baj === 'p0' ? 'no bajó' : etiqueta(BAJARON, baj),
    s.regalo.has('form') ? 1 : '', [...s.regalo].some((d) => d !== 'form') ? 1 : '',
    [1, 2, 3].filter((n) => s.eventos.has(`noche-${n}`)).join(', '), s.id];
}

export function libro(r, claves, { dias, desde, hasta }) {
  const llegaron = r.embudo[0][1];
  const parte = (n, total) => ({ pct: total ? n / total : NaN });
  const resumen = [
    [{ titulo: 'Embudo del regalo · estudioarmonia.com' }],
    ['Período', `Del ${fechaCorta(desde)} al ${fechaCorta(hasta)} (${dias} ${dias === 1 ? 'día' : 'días'}, hora de Argentina)`],
    ['Descargado', `${ahora()} (hora de Argentina)`],
    [],
    [{ titulo: 'El camino' }, { titulo: 'Personas' }, { titulo: '% de los que llegaron' }],
    ...r.embudo.map(([t, n]) => [t, n, parte(n, llegaron)]),
    [],
    [{ titulo: 'Se fueron sin escuchar ni dejar el correo' }, r.seFueron, parte(r.seFueron, llegaron)],
    [{ titulo: 'Cuánto se quedaron' }, { titulo: 'Personas' }, { titulo: '%' }],
    ...r.tiempo.map(([t, n]) => [t, n, parte(n, r.seFueron)]),
    [{ titulo: 'Cuánto bajaron en la página' }, { titulo: 'Personas' }, { titulo: '%' }],
    ...r.scroll.map(([t, n]) => [t, n, parte(n, r.seFueron)]),
    ['Sin dato de salida (la app cerró la página de golpe)', r.sinDato],
    [],
    [{ titulo: 'Problemas' }],
    ['Mandaron el correo mal escrito', r.correoMal],
    ...r.errores.map(([t, n]) => [`   ${t}`, n]),
    ['No se pudo guardar el correo', r.fallos.length, [...new Set(r.fallos)].join(', ')],
    ['Robots que cayeron en la trampa', r.trampas],
    ['Eventos en el período', r.eventos],
  ];
  const noches = [
    [{ titulo: 'Noche' }, { titulo: 'La pusieron' }, { titulo: 'Pasaron la mitad' }, { titulo: 'Hasta el final' }],
    ['Noche 1, en la página principal', r.landing[0], r.landing[2], r.landing[3]],
    ...r.noches.map(([n, a, b, c]) => [`Noche ${n}, en la página de las noches`, a, b, c]),
    [],
    ['Pasaron 1 minuto con la noche 1 en la página principal', r.landing[1]],
    ['Abrieron la página de las noches al dejar el correo', r.abrieron],
    ['Volvieron a las noches desde el correo', r.volvieron],
    ['Pusieron alguna noche en la página de las noches', r.pusieron],
    ['Descargaron audios', r.descargas],
    ['Guardaron tarjetas', r.tarjetas],
    ['Compartieron', r.compartir],
  ];
  const personas = [...r.personas].sort((a, b) => `${a.dia}${a.hora}`.localeCompare(`${b.dia}${b.hora}`));
  const eventos = claves.map(leer).filter((e) => e.sesion)
    .sort((a, b) => a.dia.localeCompare(b.dia) || a.sesion.localeCompare(b.sesion) || (ORDEN[a.evento] ?? 99) - (ORDEN[b.evento] ?? 99));
  return excel([
    { nombre: 'Resumen', anchos: [52, 12, 22], filas: resumen },
    porGrupo('Por día', 'Día', [...r.porDia].sort((a, b) => a[0].localeCompare(b[0])), (d) => ({ fecha: d })),
    porGrupo('Origen', 'Origen', r.origen, nombre),
    porGrupo('Países', 'País', r.pais, nombrePais),
    porGrupo('Dispositivos', 'Dispositivo', r.disp, nombre),
    porGrupo('Hora', 'Hora del celular', r.hora, nombreHora),
    { nombre: 'Noches', anchos: [52, 12, 16, 14], filas: noches },
    { nombre: 'Personas', fijarPrimera: true, anchos: [11, 6, 18, 16, 13, 8, 8, 8, 8, 8, 8, 8, 20, 8, 9, 15, 14, 9, 9, 10, 12],
      filas: [['Día', 'Hora', 'Origen', 'País', 'Dispositivo', 'Llegó a la página', 'Puso la noche 1', 'Más de 1 minuto',
        'La mitad', 'Entera', 'Tocó el campo', 'Escribió', 'Correo mal', 'Lo mandó bien', 'Guardado', 'Tiempo en la página',
        'Cuánto bajó', 'Abrió las noches', 'Volvió desde el correo', 'Noches que puso', 'Sesión'].map((t) => ({ titulo: t })),
      ...personas.map(filaPersona)] },
    { nombre: 'Eventos', fijarPrimera: true, anchos: [11, 6, 15, 52, 18, 16, 13, 18, 12],
      filas: [['Día', 'Hora', 'Evento', 'Qué es', 'Origen', 'País', 'Dispositivo', 'Detalle', 'Sesión'].map((t) => ({ titulo: t })),
        ...eventos.map((e) => [{ fecha: e.dia }, e.hora === 'xx' ? '' : Number(e.hora), e.evento, QUE_ES[e.evento] || '',
          nombre(e.origen), nombrePais(e.pais), nombre(e.disp), e.detalle === 'x' ? '' : e.detalle, e.sesion])] },
    { nombre: 'Guía', anchos: [18, 100], filas: [
      [{ titulo: 'Evento' }, { titulo: 'Qué es' }],
      ...Object.entries(QUE_ES),
      [],
      [{ titulo: 'Notas' }],
      ['Día', 'En hora de Argentina.'],
      ['Hora', 'La del celular de cada persona (en México, tres horas menos que en Uruguay). Desde el 14/10.'],
      ['Personas', 'Una fila por persona (una pestaña abierta). 1 = sí. «Llegó a la página» vacío: entró directo a la página de las noches.'],
      ['Sesión', 'Un número al azar que vive mientras la pestaña está abierta: sirve para contar personas, no toques. No es un dato personal.'],
      ['Privacidad', 'Sin cookies, sin IP y sin correos: del correo mal escrito solo se anota qué le faltaba.'],
    ] },
  ]);
}

function entrada(error = '') {
  return `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>Embudo · Estudio Armonía</title><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#0b0c0f;color:#ece4d2;font:17px/1.5 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;padding:48px 16px;max-width:420px;margin:0 auto}
  h1{font:600 1.6rem Georgia,serif;color:#f6e7b8}
  p{margin-top:8px;color:#a39b8b;font-size:.95rem}
  label{display:block;margin-top:26px;font-weight:600}
  input[type=password],input[type=text]{width:100%;margin-top:8px;min-height:52px;padding:0 14px;border-radius:12px;border:1px solid rgba(230,196,106,.4);
    background:#050608;color:#f6e7b8;font:inherit}
  .mostrar{display:flex;gap:8px;align-items:center;margin-top:10px;font-weight:400;font-size:.95rem;color:#a39b8b}
  button{margin-top:20px;width:100%;min-height:52px;border:0;border-radius:12px;background:#e6c46a;color:#17130a;font:700 1.05rem system-ui;cursor:pointer}
  .error{color:#f0a48c;margin-top:16px}
</style></head><body>
<h1>Embudo del regalo</h1>
<p>Escribe la clave que guardaste en Netlify (la variable EMBUDO_CLAVE).</p>
${error ? `<p class="error">${esc(error)}</p>` : ''}
<form method="post" action="/api/embudo">
  <input type="text" name="usuario" value="estudioarmonia" autocomplete="username" hidden>
  <label for="clave">Clave</label>
  <input id="clave" type="password" name="clave" autocomplete="current-password" autocapitalize="off" autocorrect="off" spellcheck="false" required autofocus>
  <label class="mostrar"><input type="checkbox" onclick="document.getElementById('clave').type=this.checked?'text':'password'"> Mostrar la clave</label>
  <input type="hidden" name="dias" value="7">
  <button>Entrar</button>
</form>
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

// La clave se compara sin espacios de más y con los acentos normalizados (el celular puede escribirlos distinto).
const normal = (t) => String(t ?? '').normalize('NFC').trim();
const iguales = (a, b) => timingSafeEqual(createHash('sha256').update(normal(a)).digest(), createHash('sha256').update(normal(b)).digest());

// /api/embudo: pide la clave en un formulario (también acepta ?clave=…). La clave vive en Netlify
// (variable EMBUDO_CLAVE), nunca en el repositorio.
export async function manejarEmbudo(req, store, claveEsperada) {
  const url = new URL(req.url);
  let dada = url.searchParams.get('clave');
  let diasPedidos = url.searchParams.get('dias');
  let formato = url.searchParams.get('formato');
  if (req.method === 'POST') {
    const f = new URLSearchParams(await req.text());
    dada = f.get('clave');
    diasPedidos = f.get('dias') ?? diasPedidos;
    formato = f.get('formato') ?? formato;
  }
  if (!claveEsperada) {
    return html(503, aviso('El tablero todavía no ve la variable EMBUDO_CLAVE. Si ya la creaste en Netlify ' +
      '(Project configuration → Environment variables), falta publicar de nuevo el sitio: ' +
      'Project overview → Deploys → Trigger deploy → Deploy project.'));
  }
  if (!normal(dada)) return html(200, entrada());
  // En la dirección, el «+» llega como espacio: se prueba también con «+».
  const valida = iguales(dada, claveEsperada) || (req.method !== 'POST' && iguales(dada.replace(/ /g, '+'), claveEsperada));
  if (!valida) return html(403, entrada('La clave no es correcta. Mayúsculas y minúsculas cuentan; prueba con «Mostrar la clave».'));
  const dias = Math.min(Math.max(parseInt(diasPedidos, 10) || 7, 1), 31);
  const ahora = Date.now();
  const fechas = [...new Set(Array.from({ length: dias }, (_, i) => dia(new Date(ahora - i * 864e5))))];
  const claves = [];
  for (const f of fechas) {
    const { blobs } = await store.list({ prefix: `${f}/` });
    for (const b of blobs) claves.push(b.key);
  }
  const rango = { dias, clave: dada, desde: fechas.at(-1), hasta: fechas[0] };
  if (formato === 'xlsx') {
    return new Response(libro(resumir(claves), claves, rango), {
      status: 200,
      headers: {
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'Content-Disposition': `attachment; filename="embudo-rin-${rango.hasta}-${dias}-dias.xlsx"`,
        'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex',
      },
    });
  }
  return html(200, pagina(resumir(claves), rango));
}
