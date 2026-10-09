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

## Publicar: Cloudflare Pages, una sola vez

**Por qué Cloudflare y no Netlify:** en el plan gratis nuevo de Netlify (300 créditos por
mes), cada GB de descarga gasta créditos. Cuando se acaban, **se pausan todos los sitios de
la cuenta**, y eso incluye Tu Catálogo Vende. Los audios pesan 11 MB cada uno. El plan gratis
de Cloudflare Pages no cobra la descarga de archivos.

1. Entrar a **dash.cloudflare.com** (la cuenta es gratis).
2. **Workers y Pages → Crear → Pages → Conectar a Git** → autorizar GitHub → elegir
   `tukivirtal/canal_setiembre2026`.
3. Configurar:

   | Campo | Valor |
   |---|---|
   | Nombre del proyecto | `rin-pausas` (queda `rin-pausas.pages.dev`) |
   | Rama de producción | `claude/clever-gates-03t347` |
   | Framework | Ninguno |
   | Comando de compilación | *(vacío)* |
   | **Directorio de salida** | **`web`** |

4. **Guardar y desplegar.**
5. En **Configuración → Compilaciones → Rutas de observación de compilación**, incluir
   `web/*`. Así solo se republica cuando cambia la web, no con cada cambio del canal.

Si el nombre `rin-pausas` está tomado, Cloudflare da otra dirección. En ese caso hay que
cambiar los enlaces de los correos y la imagen para compartir.

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
  MailerLite.
