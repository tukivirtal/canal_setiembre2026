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

## Publicar: Netlify, una sola vez

Primero se probó Cloudflare Pages (no cobra la descarga), pero su panel empuja a crear
Workers y no se encontró la opción de Pages. Se publica en Netlify, que Fátima ya usa para
Tu Catálogo Vende. `netlify.toml` ya dice qué carpeta publicar y hace que solo se republique
cuando cambia `web/`.

1. En Netlify: **Add new site → Import an existing project → GitHub** →
   `tukivirtal/canal_setiembre2026`.
2. **Branch to deploy:** `claude/clever-gates-03t347`. El resto queda como viene
   (`netlify.toml` pone `web` como carpeta de publicación).
3. **Deploy.**
4. **Site configuration → Change site name** → `rin-pausas`. La dirección queda
   `https://rin-pausas.netlify.app`, que es la que llevan los correos.

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
2. **Automatización «Rin · Regalo 3 noches»: el remitente.** Hoy sale como
   «SilentClarity» desde `contact@emotionalvaults.com`, la dirección verificada de la cuenta.
   En cada correo, el nombre tiene que ser **Rin**. Las respuestas a «¿Cómo te fue anoche?»
   llegan a esa dirección.
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

## Pendiente cuando esté la dirección definitiva

- `og:image` de `web/index.html` con la dirección completa (algunas apps no leen la
  relativa).
- Si cambia la dirección: los enlaces de `11-web/correos.py` y de los 3 correos en
  MailerLite (hoy apuntan a `rin-pausas.netlify.app`).
