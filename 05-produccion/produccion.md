# Paso 5 — Producción

## 1. El flujo, por lote de 3 obras

| Etapa | Tiempo | Qué se hace |
|---|---|---|
| 1 · Selección | 20 min | Tres obras del catálogo. Nunca dos con la misma raíz y modo |
| 2 · Composición | **de noche** | `compositor.py` sin supervisión. ~21 min de cómputo por hora de audio |
| 3 · Verificación | 20 min | Pico, RMS, clipping, fundidos. Script de control abajo |
| 4 · Portada | 45 min | Leonardo, con las referencias propias como *style reference* |
| 5 · Video | 40 min | Imagen fija + audio, con `ffmpeg` |
| 6 · Publicación | 30 min | Título y descripción bilingües, capítulos, playlist |
| 7 · Distribución | 20 min | El mismo audio a Spotify y Apple Music |

**≈ 3 h de trabajo humano por lote de 3.** El cómputo pesado ocurre mientras dormís.

## 2. Verificación antes de publicar

Ninguna obra se sube sin pasar esto:

| Medida | Umbral |
|---|---|
| Pico | ≤ −3,0 dBFS |
| Clipping | **0 muestras** |
| RMS | entre −18 y −14 dBFS |
| DC offset | ≈ 0 |
| Primeras muestras | fundido de 8 s presente |
| Últimas muestras | fundido de 8 s presente |
| Variación de RMS entre tramos | **> 1,15×** (la prueba de que la obra evoluciona) |

Esa última fila es la que importa para la política: es la evidencia numérica de que la
obra no es un bucle.

## 3. Del WAV al video

Una hora de WAV son ~635 MB. Para subir:

```bash
# audio a AAC y video de imagen fija, con la imagen codificada una sola vez
ffmpeg -loop 1 -i portada.png -i obra.wav \
  -c:v libx264 -tune stillimage -pix_fmt yuv420p -r 1 \
  -c:a aac -b:a 320k -shortest obra.mp4
```

`-r 1` (un fotograma por segundo) reduce el archivo enormemente sin ninguna pérdida
perceptible: la imagen no se mueve.

Para distribución a streaming, el WAV original sin convertir.

## 4. La portada

El oyente mira **una sola cosa**: la portada, en el momento de elegir. Es la pieza que
convierte a suscriptor.

**Plantilla fija** con un solo elemento variable, igual que la música:

```
extreme close-up photograph of [SUJETO], isolated in empty dark space,
deep black background, volumetric mist drifting through the darkness,
ONE dominant subject filling 40% of the frame,
lit from the extreme left at a ten degree grazing angle, strong chiaroscuro,
the right side falling into deep shadow, weathered natural material,
shot on 85mm macro lens, shallow depth of field, hyper-tactile, 8k, 16:9
```

Sujetos por pilar: cuenco de bronce, piedra mojada, agua quieta, ceniza, humo sobre
madera oscura, tela plegada.

**Negative prompt:** `text, letters, watermark, people, faces, mandala, chakra symbols,
purple and pink gradients, lens flare, glossy, plastic, cartoon, busy composition`

> Los degradados morados y violetas y los símbolos de chakra son **la estética exacta del
> nicho saturado**. Evitarlos es la decisión visual más rentable del canal: la portada
> tiene que parecer un sello discográfico, no un vídeo de autoayuda.

**Tipografía:** el nombre de la obra en un serif fino, pequeño, en una esquina. Acá **sí**
va serif —al revés que en un canal de historia— porque no compite con nada: la portada es
oscura y vacía, y el objetivo es elegancia, no legibilidad a la fuerza.

**Prueba a 168 × 94 px** antes de publicar, que es el tamaño real en un móvil.

## 5. Plantilla de descripción

```
[Nombre de la obra] · [duración]

Compuesta con raíz en [X] Hz, en entonación justa, modo [modo].
Para acompañar una práctica de respiración.

Estructura: [N] secciones de 6 respiraciones.
Ciclo respiratorio: de [A] a [B] respiraciones por minuto, inhalar 40 % / exhalar 60 %.
Cuencos sintetizados cada 4 respiraciones.

Composición original, sintetizada desde cero. Ninguna muestra procede de terceros.

—
[English]
Composed with a root of [X] Hz in just intonation, [mode] mode.
To accompany a breathing practice.
...

Capítulos:
00:00 [sección 1]
...
```

**Nunca:** "cura", "sana", "elimina", "frecuencia milagrosa", "terapia".
**Siempre:** describir la obra.

## 6. Registro de producción

Un CSV con una fila por obra: nombre, raíz, modo, semilla, duración, fecha, enlace.

La semilla es lo que permite **regenerar cualquier obra idéntica** sin almacenar
gigabytes de WAV. El catálogo entero cabe en un archivo de texto.
