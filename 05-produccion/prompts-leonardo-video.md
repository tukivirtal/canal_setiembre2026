# Prompts de Leonardo — video de 8 minutos

Sistema visual del video, alineado con la composición: **una escena por sección musical**.

La obra `528 · hirajoshi · semilla 42` tiene 7 secciones, así que el video tiene
**7 escenas**. Los cortes caen exactamente donde cambia el acorde, que es donde el oído
ya espera algo. Eso vuelve el montaje invisible — y da los capítulos de la descripción
sin inventarlos.

| Escena | Desde | Dura | Acorde | Sujeto |
|---|---|---|---|---|
| 1 | 0:00 | 60,0 s | 1/1 tónica | Cuenco de bronce |
| 2 | 1:00 | 61,9 s | 9/8 | Piedras apiladas mojadas |
| 3 | 2:03 | 64,1 s | 9/8 | Agua quieta con una onda |
| 4 | 3:06 | 66,4 s | 1/1 tónica | Arena rastrillada |
| 5 | 4:13 | 69,1 s | 3/2 | Bambú entre niebla |
| 6 | 5:22 | 72,1 s | 6/5 | Humo de incienso |
| 7 | 6:34 | 86,4 s | 1/1 tónica | Lino plegado |

Las escenas 1, 4 y 7 son la tónica: **el mismo material vuelve** (bronce, piedra, tela
en el mismo tono cálido). La imagen sigue la armonía.

---

## Base común

Va en los siete prompts. Es lo que hace que las siete escenas se reconozcan como un
mismo video:

```
extreme close-up photograph of [SUJETO], isolated in empty dark space,
deep black background with strong vignette, volumetric mist drifting slowly
through the darkness, ONE dominant subject filling 45% of the frame,
lit ONLY from the extreme left at a ten degree grazing angle, no fill light,
the entire right half of the subject in complete darkness,
only the left edge catching the light, extreme chiaroscuro,
weathered natural material with visible relief, surface pitting and fine grain,
subsurface light in the material, desaturated warm stone and bronze tones,
shot on 85mm macro lens, shallow depth of field, physically based rendering,
photograph of a real object, not an illustration, hyper-tactile, you could touch it,
8k, 16:9
```

**Negative prompt (en los siete):**
```
purple gradient, pink gradient, neon, mandala, chakra symbols, lotus clipart,
glowing orbs, text, letters, watermark, people, faces, hands,
smooth plastic, glossy, cgi render, cartoon, illustration, digital painting,
flat lighting, front lighting, even lighting, busy composition, multiple subjects,
oversaturated, pastel, lens flare, bokeh circles
```

> La primera línea del negative prompt es la más importante del documento. **Los
> degradados morados y violetas, los mandalas y las flores de loto son la estética exacta
> del nicho saturado.** Evitarlos es lo que hace que el canal parezca un sello
> discográfico y no un video de autoayuda. Es la decisión visual más rentable del proyecto.

---

## Los siete sujetos

**1 · Cuenco de bronce** — *0:00, tónica*
```
a single weathered bronze singing bowl seen from a low angle, deep patina,
hammered surface with visible dents and tarnish, a wooden mallet resting beside it
```

**2 · Piedras apiladas** — *1:00*
```
four wet river stones stacked in balance, water beading on the dark surfaces,
one stone slightly out of alignment
```

**3 · Agua quieta** — *2:03*
```
the surface of still black water with a single expanding ripple ring,
reflecting one distant point of warm light
```

**4 · Arena rastrillada** — *3:06, tónica*
```
raked sand in a dry zen garden, deep parallel grooves curving around a single
dark stone, low sun raking across the ridges
```

**5 · Bambú entre niebla** — *4:13*
```
three bamboo stalks with visible nodes and weathered green-grey skin,
thick mist between them, dark forest depth behind
```

**6 · Humo de incienso** — *5:22*
```
a single incense stick with a glowing ember tip, a thick ribbon of smoke rising
and curling, ash fallen on dark stone below
```

**7 · Lino plegado** — *6:34, tónica*
```
heavy folded linen cloth with deep creases and visible weave texture,
one fold catching the light, the rest falling into shadow
```

---

## El movimiento

**El punto clave que hay que entender antes de gastar créditos:** Leonardo Motion genera
clips de pocos segundos. Una escena de esta obra dura **60-86 segundos**. No se cubre con
un clip.

Tres maneras de resolverlo, de menos a más trabajo:

### a) Ken Burns sobre la imagen fija — la más segura
Zoom lentísimo (del 100 % al 106 % en 70 segundos) más una deriva horizontal mínima.
Se hace en el montaje, sin gastar un crédito, y **para este contenido es suficiente**:
el espectador casi no mira la pantalla.

```
ffmpeg -loop 1 -i escena1.png -vf "zoompan=z='min(zoom+0.00015,1.06)':d=1750:s=1920x1080:fps=25" -t 70 escena1.mp4
```

### b) Clip de Leonardo Motion en bucle de vaivén — la recomendada
Se genera el clip de movimiento, y en el montaje se reproduce hacia delante y hacia
atrás alternadamente. **El vaivén no tiene punto de corte visible**, porque el final de
una pasada es exactamente el principio de la siguiente. Un clip de 5 s cubre 70 s con
siete idas y vueltas, y nadie detecta el bucle.

```
ffmpeg -i clip.mp4 -filter_complex "[0]reverse[r];[0][r]concat=n=2" vaiven.mp4
```

### c) Mezcla: movimiento real + Ken Burns encima
El vaivén de (b) con un zoom lento superpuesto. El zoom desfasa el bucle y lo vuelve
indetectable incluso en escenas largas. Es lo que conviene para las escenas 5 y 6, donde
la niebla y el humo se mueven de verdad.

### Prompts de movimiento, por escena

Leonardo Motion pide describir **qué se mueve**. Para este video la respuesta es
casi siempre: muy poco.

| Escena | Prompt de movimiento | Intensidad |
|---|---|---|
| 1 · Cuenco | `almost imperceptible drift of mist, the bowl completely still` | mínima |
| 2 · Piedras | `a single drop of water slides down the stone, mist drifts` | mínima |
| 3 · Agua | `the ripple ring expands slowly outward across the water` | baja |
| 4 · Arena | `mist crawls low across the sand, grooves perfectly still` | mínima |
| 5 · Bambú | `thick mist rolls slowly between the stalks, a faint sway` | media |
| 6 · Humo | `the smoke ribbon rises and curls continuously` | media |
| 7 · Lino | `the mist drifts, the cloth completely still` | mínima |

**Regla de oro:** si el movimiento se nota, es demasiado. En un video de meditación,
cualquier movimiento que llame la atención rompe lo que la música construye — y el
espectador que estaba bajando el ritmo, vuelve a subirlo.

Nada de movimiento de cámara brusco, nada de rotaciones, nada de destellos.

---

## Transiciones

**Fundidos cruzados de 4 segundos**, centrados en el cambio de sección musical: dos
segundos antes y dos después. La imagen cambia mientras el acorde cambia, así que el
corte no se percibe como corte.

**Nunca:** cortes secos, barridos, destellos, negro entre escenas. Un negro momentáneo en
un video de sueño hace que el espectador crea que se cortó y toque el teléfono.

---

## Montaje final

```bash
# 1. Cada escena a su duración exacta
ffmpeg -i vaiven1.mp4 -t 62 -vf "fade=in:0:50,fade=out:1500:50" e1.mp4

# 2. Concatenar con fundidos cruzados de 4 s
ffmpeg -i e1.mp4 -i e2.mp4 -filter_complex \
  "[0][1]xfade=transition=fade:duration=4:offset=58" video.mp4

# 3. Unir con el audio (que manda: el video se corta a la duración del audio)
ffmpeg -i video.mp4 -i obra8.wav \
  -c:v libx264 -pix_fmt yuv420p -crf 20 \
  -c:a aac -b:a 320k -shortest final.mp4
```

El audio manda siempre. Si el video queda corto, se alarga la última escena; nunca se
recorta la obra.

---

## Portada

La portada **no es** ninguna de las siete escenas. Se genera aparte, con el mismo sistema
y el cuenco como sujeto, pero con más aire alrededor para que el título respire.

El nombre de la obra en serif fino y pequeño, en una esquina. Acá sí serif —al revés que
en un canal de historia— porque no compite con nada: el fondo es oscuro y vacío, y lo que
se busca es elegancia, no legibilidad a la fuerza.

**Prueba a 168 × 94 px antes de publicar.** Es el tamaño real en un móvil.


---

## Prueba de la escena 1

Se generó el cuenco con este sistema antes de gastar créditos. Resultado:

**Lo que salió bien, y es casi todo:**

- **El fondo negro marcado, con viñeta.** El sujeto recortado contra la oscuridad, que es
  lo que pedía la referencia.
- **El relieve está.** Bronce martillado con abolladuras visibles, pátina, grano. Se
  puede tocar.
- **La niebla funciona**: un hilo de humo subiendo, volumétrico, sin llamar la atención.
- **Parece un objeto real fotografiado**, no una ilustración.
- **El negative prompt hizo su trabajo**: ni un degradado morado, ni un mandala, ni una
  flor de loto. Nada de la estética del nicho saturado.

**Lo que falló, y es el mismo fallo de siempre:**

La **luz salió más frontal que rasante**. Se pidió un ángulo de diez grados desde la
izquierda y devolvió una iluminación bastante pareja. El objeto tiene forma, pero no el
claroscuro extremo del sistema.

Es exactamente el mismo comportamiento que apareció al probar los relieves: **los
generadores se resisten a la luz rasante extrema**, porque su promedio de entrenamiento
es producto bien iluminado.

**La corrección, ya aplicada a la base:** no basta con describir de dónde viene la luz.
Hay que **describir la sombra**:

```
lit ONLY from the extreme left at a ten degree grazing angle, no fill light,
the entire right half of the subject in complete darkness,
only the left edge catching the light, extreme chiaroscuro
```

`no fill light` y `the entire right half in complete darkness` son las dos frases que
mueven la aguja. Describir la ausencia de luz funciona mejor que describir su ángulo.

**Conclusión:** el sistema de objeto zen sobre negro funciona mejor que el de relieve
tallado para este contenido. Más tactilidad, más elegancia, y cero riesgo de parecer
autoayuda.
