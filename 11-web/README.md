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

Las tres noches: 1, «Dejar el trabajo en la puerta» (432 Hz); 2, «La lista de la almohada»
(396 Hz); 3, «Cuando la cabeza da vueltas» (417 Hz). Duran 12 minutos y están a -20 LUFS,
más bajas que los TikToks, porque son para la cama.

## Cómo funciona

```
TikTok (biografía) → landing → deja el correo → se abren las 3 noches al instante
                                   └→ MailerLite: grupo «Rin · Regalo 3 noches»
                                        → correo 1 al instante, 2 y 3 con un día de espera
```

El formulario manda el correo a MailerLite y abre las noches sin esperar la respuesta.
Así la persona recibe el regalo aunque MailerLite tarde o falle.

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

## MailerLite: tres cosas en el panel

1. **Formulario «Rin · Regalo 3 noches (landing)»: apagar la doble confirmación.** La
   persona ya recibe el regalo en la página. Con doble confirmación, solo recibirían los
   correos quienes confirmen. Si el formulario pide un diseño, se elige cualquier plantilla
   y se guarda: no se usa, porque la página tiene el suyo.
2. **Automatización «Rin · Regalo 3 noches»: el remitente.** Salía como «SilentClarity»
   desde `contact@emotionalvaults.com`, pero ese dominio dejó de estar autenticado y la
   automatización quedó marcada como rota. El remitente nuevo: **Rin**, desde
   `hola@estudioarmonia.com` (hay que autenticar el dominio en MailerLite y darle una casilla
   que reenvíe a Gmail, para verificarla y para leer las respuestas a «¿Cómo te fue anoche?»).
3. **Activarla** cuando la página esté publicada y la prueba de abajo haya salido bien.

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

## Hecho con la dirección definitiva

- `og:image`, `og:url` y `canonical` de `web/index.html` con `https://estudioarmonia.com`.
- Los enlaces de `11-web/correos.py` y de los 3 correos en MailerLite apuntan a
  `https://estudioarmonia.com`. El texto plano de los correos todavía dice la dirección vieja:
  MailerLite no deja editarlo hasta que el remitente esté verificado.
