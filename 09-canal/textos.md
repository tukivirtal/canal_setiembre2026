# Textos del canal

Todo listo para pegar en **YouTube Studio → Personalización**.

## Descripción del canal

**Idioma principal: inglés** (decidido el 23/09), con el español abajo. Límite 1.000
caracteres; los primeros ~150 son los que aparecen en la búsqueda.

```
Sleep music, meditation music, calming music for anxious moments and focus music. Long original pieces with ocean waves, rain on leaves, tropical rainforest and zen temple ambiences.

Rin (鈴) is the Japanese name of the singing bowl. Every piece is composed from scratch — no loops, no borrowed sounds. Just intonation, a slow breathing pulse, and natural ambiences synthesized sound by sound.

Each piece has its own name and its own purpose: sleep, a pause when your mind won't stop, a meditation practice, or long hours of work and study.

We don't promise to heal anything. We compose music to keep you company.

— Español —
Música para dormir, meditar, calmar la ansiedad y concentrarte, compuesta desde cero. Cada obra también tiene su título y descripción en español.

Subscribe for every new piece.
```

## Palabras clave del canal

**Studio → Configuración → Canal → Palabras clave.** Límite 500 caracteres.

```
"sleep music" "meditation music" "relaxing music" "music for anxiety" "focus music" "study music" "ocean waves" "rain sounds" "zen music" "528 Hz" "432 Hz" "música para dormir" "música para meditar" "música relajante" "música zen" Rin
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
