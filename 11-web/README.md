# La web de Rin: el regalo de las 3 noches

*09/10/2026. Primer paso de `06-monetizacion/oferta-soltar-el-dia.md`.*

## Qué hay

| Dónde | Qué |
|---|---|
| `web/` | Lo que se publica: la landing (`/`), la página de las noches (`/tus-noches/`), los audios, las tarjetas y las tipografías |
| `05-produccion/noches/noches.py` | Los audios: el sonido de los TikToks, sin voz, con los golpes cada vez más espaciados y más suaves |
| `11-web/vetas.py` | La textura: negro mate con vetas azul noche y oro, con los colores del banner |
| `11-web/tarjetas.py` | Las tarjetas de cada noche (1080 × 1920) |
| `11-web/extras.py` | Las miniaturas, la imagen para compartir y los íconos |
| `11-web/correos.py` | Los 3 correos del regalo (ya cargados en MailerLite) |
| `11-web/carrusel.py` | El carrusel de fotos de TikTok: portada, las 3 tarjetas y el cierre (en `produccion/carrusel-regalo/`) |

Las tres noches: 1, «Dejar el trabajo en la puerta» (432 Hz); 2, «La lista de la almohada»
(396 Hz); 3, «Cuando la cabeza da vueltas» (417 Hz). Duran 12 minutos y están a -20 LUFS,
más bajas que los TikToks, porque son para la cama.

## Cómo funciona

```
TikTok → landing → la noche 1 suena ahí mismo, sin dejar ningún dato
                 → deja el correo → se abren las 3 noches al instante
                   (si la noche 1 está sonando, no la corta: confirma ahí mismo)
                       └→ MailerLite: grupo «Rin · Regalo 3 noches»
                            → correo 1 al instante, 2 y 3 con un día de espera
```

**Por qué la noche 1 va sin correo (14/10).** La promoción del 13/10 trajo 524 personas y
ninguna dejó el correo. Las 10 que tocaron el campo fueron las mismas 10 que tocaron el
botón sin un correo válido: la gente toca el botón, no el campo, y quiere el regalo ya. Ahora
el botón grande pone la noche 1 y el correo es para recibir las 3 («¿Prefieres escucharla en
la cama?»). Además, la página arregla sola errores de tipeo seguros (`.con`, `gmial.com`,
espacios) y dice qué le falta al correo en vez de un error genérico.

El correo se guarda con la función de Netlify `/api/suscribir` (`netlify/functions/suscribir.mjs`),
que lo agrega al grupo con la API de MailerLite. La clave está en Netlify, en la variable
`Web_Estudio_Armonia` (en MailerLite el token se llama «Rin»). La página abre las noches sin
esperar la respuesta, así la persona recibe el regalo aunque el guardado tarde o falle; si la
función no responde, prueba con el formulario integrado de MailerLite. Probado el 10/10: la
alta de prueba entró al grupo.

## Dónde está publicada

**https://estudioarmonia.com** (y `www`, que redirige). Estudio Armonía es la marca paraguas:
Rin es una línea adentro, y el dominio sirve para otros productos si este nicho no funciona.

| Pieza | Dónde | Detalle |
|---|---|---|
| Sitio | Netlify, proyecto `estudioarmonia` (`estudioarmonia.netlify.app`) | Conectado al repo, rama `claude/clever-gates-03t347`. `netlify.toml` publica `web/` y solo republica cuando cambia la web |
| Dominio | Comprado en Vercel (equipo «Fátima Cippollini's projects»), renueva solo el 9/10 de cada año | Solo el registro del nombre: la web no está en Vercel |
| DNS (en Vercel) | `A @ 75.2.60.5` (balanceador de Netlify) · `CNAME www → estudioarmonia.netlify.app` | Vercel deja además unos registros automáticos (ALIAS a Vercel) que la API no permite borrar; si algún día el dominio abre una página de Vercel, hay que borrarlos desde su panel |

Primero se probó Cloudflare Pages (no cobra la descarga), pero su panel empuja a crear
Workers y no se encontró la opción de Pages.

**El cuidado con los créditos.** Si la cuenta de Netlify está en el plan gratis nuevo (con
créditos, cuentas creadas desde septiembre de 2025), cada GB de descarga y cada publicación
gastan créditos, y cuando se acaban **se pausan todos los sitios de la cuenta**, también Tu
Catálogo Vende. Se ve en **Team settings → Billing / Usage**. Las cuentas anteriores
tienen 100 GB por mes y no pausan. Con el tráfico de las primeras semanas alcanza; si el
consumo se acerca al tope, los audios (lo que más pesa) se mudan a otro lado.

## MailerLite y el correo del dominio

- **Remitente de los 3 correos:** Rin, `hola@estudioarmonia.com` (también como «responder a»).
  Antes salían como «SilentClarity» desde `contact@emotionalvaults.com`, que dejó de estar
  autenticado.
- **Dominio autenticado en MailerLite** (10/10): `CNAME litesrv._domainkey →
  litesrv._domainkey.mlsend.com` (DKIM), `TXT @ mailerlite-domain-verification=…` y el SPF
  compartido `v=spf1 include:spf.improvmx.com include:_spf.mlsend.com ~all`.
- **Casilla `hola@`:** ImprovMX (cuenta de `rinchanneloficial@gmail.com`) reenvía
  `hola@estudioarmonia.com` al Gmail de Rin, para leer las respuestas a «¿Cómo te fue
  anoche?». Registros: `MX mx1.improvmx.com (10)`, `MX mx2.improvmx.com (20)` y el TXT
  `436bb718._improvmx` de la transferencia entre cuentas (se puede borrar).
- **Formulario «Rin · Regalo 3 noches (landing)»:** doble confirmación apagada. La persona ya
  recibe el regalo en la página.
- **Automatización «Rin · Regalo 3 noches»:** remitente nuevo y texto plano con los enlaces
  de `estudioarmonia.com`. Se activa a mano en el panel.

Hoy hay 31 contactos en la cuenta. Según las fuentes, el tope del plan gratis bajó a 250 o
500 contactos desde julio de 2026. Cuando se acerque, se decide si se paga MailerLite, se
pasa a otra plataforma o se usa la planilla.

## La prueba que no se saltea

- [ ] Abrir la página en el celular, en Chrome o Safari.
- [ ] Dejar un correo propio (por ejemplo `silentclarityfem+prueba@gmail.com`).
- [ ] Se abre «Tus 3 primeras noches».
- [ ] Poner la noche 1 y bloquear el celular: tiene que seguir sonando.
- [ ] En MailerLite, el correo aparece en el grupo y llega el correo 1.
- [ ] Repetirlo desde el enlace de la biografía de TikTok.

Recién ahí, el enlace va a la biografía.

## El embudo: qué pasa en la página

Desde el 11/10 la web mide el camino completo, sin cookies ni datos personales (no guarda la IP
ni el correo; la «sesión» es un número al azar que vive mientras la pestaña está abierta).

| Qué | Dónde |
|---|---|
| La página manda cada paso a `/api/evento` (`netlify/functions/evento.mjs`) | `web/rin.js` |
| La función del correo anota si se guardó o falló, y por qué | `netlify/functions/suscribir.mjs` |
| Todo se guarda en Netlify Blobs, almacén `embudo`, una clave por evento | `netlify/lib/embudo.mjs` |
| El tablero | `https://estudioarmonia.com/api/embudo`: pide la clave en un campo (`netlify/functions/tablero.mjs`) |

Lo que muestra el tablero (hoy, 7 o 30 días, en hora de Argentina): cuántas personas llegaron,
pusieron la noche 1 en la landing y la escucharon más de un minuto, tocaron el campo del
correo (el foco que pone la página después de un error no cuenta), empezaron a escribirlo, lo
mandaron bien escrito y quedaron guardadas; cuánto se quedaron y cuánto bajaron los que se
fueron sin escuchar ni dejar el correo; de dónde llegan (TikTok, promoción, Instagram…),
países, dispositivos, días y la hora del celular de cada persona (desde el 14/10); las noches
escuchadas hasta la mitad y hasta el final, en la landing y en la página de las noches; las
descargas, las veces que compartieron, y los problemas (qué le faltaba al correo mal escrito,
fallos al guardar, robots).

- **La clave** es la variable `EMBUDO_CLAVE` de Netlify (Project configuration → Environment
  variables). Nunca va en el repositorio, que es público. Después de crearla o cambiarla hay
  que publicar de nuevo (Deploys → Trigger deploy).
- **Para separar una promoción**, en la dirección del sitio de la promoción va
  `https://estudioarmonia.com/?o=promo` (o `?o=promo-noche1`). Sin eso, la visita queda como
  «TikTok» si viene de la app, o «TikTok (promoción)» si el anuncio agrega `ttclid`.
- **El costo:** cada paso es una llamada a una función de Netlify. Con el tráfico de ahora es
  poco, pero conviene mirar el consumo de créditos la primera semana.

## Hecho con la dirección definitiva

- `og:image`, `og:url` y `canonical` de `web/index.html` con `https://estudioarmonia.com`.
- Los enlaces de `11-web/correos.py` y de los 3 correos en MailerLite (HTML y texto plano)
  apuntan a `https://estudioarmonia.com`.
