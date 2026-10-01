# Textos del canal

Todo listo para pegar en **YouTube Studio → Personalización**.

## Descripción del canal

Cambiada el 01/10 para ganar suscriptores por la psicología: **identidad** («para las
noches en que la cabeza no para»: la persona se reconoce) y **ritual** («una obra nueva
cada semana»: hay motivo para volver). La gente no se suscribe a una música, se suscribe
a una promesa.

**En inglés.** Límite 1.000 caracteres; los primeros ~150 son los que aparecen en la
búsqueda.

```
For the nights your mind won't stop. Original sleep music and calming music for anxiety, with a dark screen that won't keep you awake.

🌙 A new 3-hour sleep piece every week: gentle rain, distant ocean, theta waves.
🌿 Shorter pieces for anxious moments in the middle of the day.
🎧 Pieces with theta waves: use headphones for the best experience.

Rin (鈴) is the Japanese name of the singing bowl. Every piece is composed from scratch: no loops, no borrowed sounds. Just intonation, and a breathing cycle written into the music that slows you down, little by little.

We don't promise to heal anything. We compose music to keep you company tonight.

Subscribe, and come back tomorrow night.
```

### La traducción al español

Va aparte, como traducción del canal: **Studio → Configuración → Canal → Información
básica → Agregar idioma → Español**. Quien tenga YouTube en español ve esta:

```
Para las noches en que la cabeza no para. Música original para dormir y para calmar la ansiedad, con pantalla oscura para que la luz no te despierte.

🌙 Una obra nueva de 3 horas para dormir cada semana: lluvia suave, mar lejano, ondas theta.
🌿 Obras más cortas para los momentos de ansiedad en medio del día.
🎧 Obras con ondas theta: usa auriculares para una mejor experiencia.

Rin (鈴) es el nombre japonés del cuenco cantor. Cada obra se compone desde cero: sin loops ni sonidos prestados. Entonación justa y un ciclo de respiración escrito en la música, que te va bajando el ritmo de a poco.

No prometemos curar nada. Componemos música para acompañarte esta noche.

Suscríbete, y vuelve mañana a la noche.
```

## Palabras clave del canal

**Studio → Configuración → Canal → Palabras clave.** En inglés, límite 500 caracteres.
El campo las toma sueltas: se pegan separadas por coma, sin comillas.

```
sleep music, meditation music, relaxing music, calming music, music for anxiety, focus music, study music, deep sleep, ocean waves, rain sounds, nature sounds, zen music, tibetan bowls, 528 Hz, 432 Hz, solfeggio frequencies, ambient music, yoga music, Rin
```

Pesan poco para posicionar: posicionan el título y la descripción de cada obra. Ayudan a
que YouTube entienda de qué va el canal cuando todavía no tiene videos.

## Títulos y descripciones de cada obra

El catálogo (`08-catalogo/catalogo_canal.xlsx`) trae cada obra en los dos idiomas:

- `titulo` y `descripcion_optimizada` → en inglés, se cargan al subir el video.
- `titulo_es` y `descripcion_es` → **Studio → Subtítulos → elegir el video → Agregar
  idioma: Español → Título y descripción**. Quien tenga YouTube en español ve esos.

## Imágenes

Generadas con `python3 09-canal/render_identidad.py` en `09-canal/export/`:

| Archivo | Dónde va | Medida |
|---|---|---|
| `banner-2560x1440.png` | Personalización → Marca → Imagen del banner | 2560×1440. Nombre y lema dentro de la zona segura de 1546×423, que es lo único que se ve en el celular |
| `perfil-800x800.png` | Personalización → Marca → Imagen | 800×800. YouTube la muestra en círculo; se lee hasta en 48 px |
| `marca-agua-150x150.png` | Personalización → Marca → Marca de agua del video | 150×150, fondo transparente |

`vista-dispositivos.png` muestra cómo recorta YouTube el banner en TV, escritorio y móvil.

## La marca de agua: sí, conviene

No es decoración. **Es un botón de suscripción que aparece sobre todos los videos**: quien
pasa el mouse o toca la marca, se suscribe sin salir del video. En este canal los
suscriptores son el cuello de botella (el oyente pone la obra y apaga la pantalla), así
que cualquier atajo para suscribirse cuenta.

Configurarla con **"Hora de visualización: Todo el video"**. Aparece abajo a la derecha;
el mandala lleva la firma "Rin" abajo a la izquierda, así que no se pisan.

El banner va en inglés: *"Meditation music, composed — not assembled"* y
*SLEEP · CALM · MEDITATE · RELEASE · FOCUS*.

## TikTok, Instagram y Facebook

Todo en inglés, como el canal. La foto de perfil es la misma en todas:
`export/perfil-800x800.png`.

### TikTok

- **Nombre:** `Rin · Meditation Music`
- **Biografía** (máximo 80 caracteres, esta tiene 73):

```
Original meditation music 🌙 sleep · calm · focus
Full pieces on YouTube ↓
```

La flecha apunta al enlace, que TikTok muestra con 1.000 seguidores. Mientras tanto,
el canal se encuentra por el nombre.

### Instagram: cuenta profesional de tipo **Empresa**

Profesional porque sin eso no se puede anunciar ni ver estadísticas. Empresa y no
Creador porque da las herramientas de anuncios y de tienda; la ventaja de Creador es la
biblioteca de música con licencia, y Rin usa su propia música.

- **Nombre** (Instagram lo usa en la búsqueda): `Rin · Meditation Music`
- **Categoría:** Músico/banda
- **Biografía** (máximo 150 caracteres, esta tiene 109):

```
Meditation music, composed — not assembled.
Sleep · calm · meditate · release · focus
New pieces every week ↓
```

### Facebook: una **página**, no el perfil personal

Los anuncios de Meta salen de una página. La página se crea desde tu perfil personal
(que queda como administrador y no se muestra en ningún lado) y es sin cara.

- **Nombre:** `Rin · Meditation Music`
- **Categorías:** Músico/banda · Creador digital
- **Presentación** (máximo 101 caracteres, esta tiene 86):

```
Original meditation music for sleep, calm and focus. New pieces every week on YouTube.
```

- **Descripción larga** (sección «Información»):

```
Rin composes meditation music from scratch: every piece is written for one intention — sleep, calm, meditation, release or focus — tuned in just intonation and shaped around a slow breathing cycle. Ocean, birds, rain on leaves and temple bells are synthesized too. No samples, no loops.

New pieces every week on YouTube: youtube.com/@rinchanneloficial
```

- **Portada:** `export/portada-facebook-1640x924.png`. El texto queda en la franja que
  Facebook muestra en escritorio y lejos de la foto de perfil (ver
  `export/vista-facebook.png`).
- **Conectar la cuenta de Instagram** a la página (Configuración → Cuentas vinculadas):
  es lo que permite anunciar en las dos desde un solo lugar.

## Listas de reproducción

**Studio → Contenido → Listas → Nueva lista.** Encadenan un video tras otro: es la señal
más fuerte para que YouTube recomiende el canal. Un video puede estar en las dos.

**1. Deep Sleep Music 🌙 Fall Asleep Fast** (pública)
```
3-hour sleep music with a dark screen after 3 minutes: gentle rain, distant ocean and theta waves. Lights off, phone face down, volume low. A new piece every week.
```
Orden: Dark Screen Sleep Music (lluvia) · Deep Sleep Theta Waves · Calm Your Nervous System (3 h) · Deep Sleep Music, ocean waves (90 min).

**2. Calm Your Anxious Mind 🌿** (pública)
```
Calming music for anxiety, from a 10-minute reset to three hours. Breathe out longer than you breathe in, and let the music slow you down.
```
Orden: 10-Minute Anxiety Reset · Calm Your Nervous System in 15 Minutes · Quiet Your Mind (30 min) · Stop Overthinking (1 h) · Calm Your Nervous System (3 h).

**Después, en Personalización → Diseño:**
- **Video destacado para quienes no están suscritos:** Dark Screen Sleep Music (lluvia).
- **Secciones:** agregar las dos listas, debajo de «Videos».

## El día fijo

Una obra larga por semana, **el domingo a las 21:00 de Uruguay** (20:00 en Nueva York,
la hora en que se busca música para dormir). Desde el 2 de noviembre, cuando EE. UU.
atrasa la hora, pasa a las 22:00 de Uruguay. El ritual le enseña al público, y al
algoritmo, cuándo volver.
