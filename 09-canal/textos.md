# Textos del canal

Todo listo para pegar en **YouTube Studio → Personalización**.

## Descripción del canal

**En inglés.** Límite 1.000 caracteres; los primeros ~150 son los que aparecen en la
búsqueda.

```
Sleep music, meditation music, calming music for anxious moments and focus music. Long original pieces with ocean waves, rain on leaves, tropical rainforest and zen temple ambiences.

Rin (鈴) is the Japanese name of the singing bowl. Every piece is composed from scratch: no loops, no borrowed sounds. Just intonation, a slow breathing pulse, and natural ambiences synthesized sound by sound.

Each piece has its own name and its own purpose: sleep, a pause when your mind won't stop, a meditation practice, or long hours of work and study.

We don't promise to heal anything. We compose music to keep you company.

Subscribe for every new piece.
```

### La traducción al español

Va aparte, como traducción del canal: **Studio → Configuración → Canal → Información
básica → Agregar idioma → Español**. Quien tenga YouTube en español ve esta:

```
Música para dormir, música para meditar, música para calmar momentos de ansiedad y música para concentrarte. Obras largas y originales con ambientes de olas del mar, lluvia sobre hojas, selva tropical y templo zen.

Rin (鈴) es el nombre japonés del cuenco cantor. Cada obra se compone desde cero: sin loops ni sonidos prestados. Entonación justa, un pulso de respiración lenta y ambientes naturales sintetizados sonido por sonido.

Cada obra tiene su nombre y su propósito: dormir, una pausa cuando la cabeza no para, una práctica de meditación o largas horas de trabajo y estudio.

No prometemos curar nada. Componemos música para acompañarte.

Suscríbete para recibir cada obra nueva.
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
