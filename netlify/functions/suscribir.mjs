// Guarda el correo del regalo en MailerLite, en el grupo «Rin · Regalo 3 noches».
// La clave de la API vive en Netlify (variable MAILERLITE_TOKEN), nunca en el repositorio.
const GRUPO = '200892866020509036';
const CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const ORIGENES = /^https:\/\/((www\.)?estudioarmonia\.com|([a-z0-9-]+--)?estudioarmonia\.netlify\.app)$/;

const respuesta = (cuerpo, estado = 200) =>
  new Response(JSON.stringify(cuerpo), { status: estado, headers: { 'Content-Type': 'application/json' } });

export default async (req) => {
  if (req.method !== 'POST') return respuesta({ ok: false, error: 'metodo' }, 405);
  const origen = req.headers.get('origin');
  if (origen && !ORIGENES.test(origen)) return respuesta({ ok: false, error: 'origen' }, 403);
  let datos = {};
  try { datos = await req.json(); } catch { /* cuerpo vacío o roto */ }
  // Trampa para robots: el campo oculto solo lo llena un programa.
  if (datos.sitio_web) return respuesta({ ok: true });
  const correo = String(datos.correo || '').trim().toLowerCase();
  if (correo.length > 254 || !CORREO.test(correo)) return respuesta({ ok: false, error: 'correo' }, 400);
  const token = process.env.MAILERLITE_TOKEN;
  if (!token) return respuesta({ ok: false, error: 'configuracion' }, 500);
  const r = await fetch('https://connect.mailerlite.com/api/subscribers', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ email: correo, groups: [GRUPO] }),
  });
  if (!r.ok) {
    console.error('MailerLite respondió', r.status, (await r.text()).slice(0, 300));
    return respuesta({ ok: false, error: 'mailerlite' }, 502);
  }
  return respuesta({ ok: true });
};

export const config = { path: '/api/suscribir' };
