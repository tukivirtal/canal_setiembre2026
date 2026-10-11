// Guarda el correo del regalo en MailerLite, en el grupo «Rin · Regalo 3 noches».
// La clave de la API vive en Netlify (variable Web_Estudio_Armonia), nunca en el repositorio.
// Además anota en el embudo si se guardó o no (netlify/lib/embudo.mjs), sin el correo.
import { ALMACEN, ORIGENES, dispositivo, origenPorNavegador, pais, registrar } from '../lib/embudo.mjs';

const GRUPO = '200892866020509036';
const CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

const respuesta = (cuerpo, estado = 200) =>
  new Response(JSON.stringify(cuerpo), { status: estado, headers: { 'Content-Type': 'application/json' } });

// Si el almacén del embudo no está disponible, el correo se guarda igual.
async function medir(req, context, datos, evento, detalle = '') {
  try {
    const { getStore } = await import('@netlify/blobs');
    const ua = req.headers.get('user-agent') || '';
    await registrar(getStore(ALMACEN), {
      evento, origen: datos.o || origenPorNavegador(ua), pais: pais(context),
      disp: dispositivo(ua), sesion: datos.s, detalle,
    });
  } catch (e) {
    console.error('Sin medición:', e?.message);
  }
}

export default async (req, context) => {
  if (req.method !== 'POST') return respuesta({ ok: false, error: 'metodo' }, 405);
  const origen = req.headers.get('origin');
  if (origen && !ORIGENES.test(origen)) return respuesta({ ok: false, error: 'origen' }, 403);
  let datos = {};
  try { datos = await req.json(); } catch { /* cuerpo vacío o roto */ }
  if (!datos || typeof datos !== 'object') datos = {};
  // Trampa para robots: el campo oculto solo lo llena un programa.
  if (datos.sitio_web) {
    await medir(req, context, datos, 'trampa');
    return respuesta({ ok: true });
  }
  const correo = String(datos.correo || '').trim().toLowerCase();
  if (correo.length > 254 || !CORREO.test(correo)) return respuesta({ ok: false, error: 'correo' }, 400);
  const token = process.env.Web_Estudio_Armonia || process.env.MAILERLITE_TOKEN;
  if (!token) {
    await medir(req, context, datos, 'fallo', 'configuracion');
    return respuesta({ ok: false, error: 'configuracion' }, 500);
  }
  let r;
  try {
    r = await fetch('https://connect.mailerlite.com/api/subscribers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ email: correo, groups: [GRUPO] }),
    });
  } catch (e) {
    console.error('MailerLite no respondió', e?.message);
    await medir(req, context, datos, 'fallo', 'red');
    return respuesta({ ok: false, error: 'red' }, 502);
  }
  if (!r.ok) {
    console.error('MailerLite respondió', r.status, (await r.text()).slice(0, 300));
    await medir(req, context, datos, 'fallo', `mailerlite-${r.status}`);
    return respuesta({ ok: false, error: 'mailerlite' }, 502);
  }
  await medir(req, context, datos, 'guardado');
  return respuesta({ ok: true });
};

export const config = { path: '/api/suscribir' };
