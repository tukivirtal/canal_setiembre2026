# Prompts de Leonardo — miniaturas del lote de prueba

Doce prompts: dos por video (versión **objeto** y versión **rostro**) para la prueba A/B
definida en el paso 3.

## Base común

Estas líneas van en **todos** los prompts. Son las que hacen que las seis miniaturas se
reconozcan como el mismo canal:

```
cinematic museum still life, single subject centered, dramatic side lighting,
warm ochre and earth tone palette, deep dark background, shallow depth of field,
photorealistic, high detail, 16:9
```

**Negative prompt (en todos):**
```
text, letters, watermark, logo, modern objects, plastic, cartoon, illustration,
cluttered background, multiple subjects, blurry, distorted hands, extra fingers
```

**Configuración:** 16:9 · modelo fotorrealista · exportar a 1280×720 ·
el texto se agrega después en Photopea o Canva, nunca en el prompt.

---

## 1 · Qué comía un soldado romano

**A — objeto** *(prompt corregido tras la prueba en Canva, ver más abajo)*
```
A flat dense dark round loaf of ancient Roman panis militaris, coarse wholegrain,
low and heavy, scored into radial wedges, NOT a modern crusty sourdough boule,
resting on rough wood beside a Roman rotary hand quern made of two flat circular
stone discs with a wooden handle, NOT a mortar and pestle, scattered wheat grains,
cinematic museum still life, single subject centered, dramatic side lighting,
warm ochre and earth tone palette, deep dark background, shallow depth of field,
photorealistic, high detail, 16:9
```
Texto a superponer: **UN KILO AL DÍA**

> **Mejor aún:** para este video concreto, la imagen ganadora no se genera.
> El **pan carbonizado de Pompeya** es un objeto real, está fotografiado en dominio
> público, tiene esas marcas radiales inconfundibles y es muchísimo más llamativo que
> cualquier hogaza generada. Lo trae el script del archivo con la búsqueda
> `carbonized bread Pompeii`. Un objeto real que parece imposible le gana a una
> ilustración perfecta.

**B — rostro**
```
Weathered profile of a Roman legionary in iron helmet, stern expression, looking right,
a dark broken loaf of bread out of focus in the foreground, cinematic museum lighting,
warm ochre and earth tones, deep dark background, photorealistic, high detail, 16:9
```
Texto: **SU RACIÓN REAL**

## 2 · Cómo se bañaba la gente en la Edad Media

**A — objeto**
```
A large wooden bathing tub with steam rising, linen cloth draped over the edge,
inside a dim medieval chamber lit by a single window, cinematic still life,
warm ochre palette, deep shadows, photorealistic, high detail, 16:9
```
Texto: **SÍ SE BAÑABAN**

**B — rostro**
```
Medieval woman seen from behind in a wooden bathing tub, steam and candlelight,
head turned slightly toward the viewer, dim stone room, warm earth tones,
deep dark background, photorealistic, modest and historical, high detail, 16:9
```
Texto: **EL MITO**

## 3 · Cuánto costaba vivir en 1650

**A — objeto**
```
A small pile of tarnished 17th century silver coins resting on a handwritten
account ledger with quill ink, candlelight from the side, cinematic still life,
warm ochre and earth tones, deep dark background, photorealistic, high detail, 16:9
```
Texto: **EL PAN**

**B — rostro**
```
A 17th century Dutch merchant in dark clothing and white collar, weighing coins on
a small brass balance, Vermeer style side window light, warm earth palette,
deep dark background, photorealistic, high detail, 16:9
```
Texto: **UN DÍA DE SUELDO**

## 4 · Qué comía la gente en tiempos de Jesús

**A — objeto**
```
Flatbread, dried fish, olives and a clay cup arranged on a rough stone surface,
first century Galilee, cinematic museum still life, single group centered,
dramatic side lighting, warm ochre palette, deep dark background,
photorealistic, high detail, 16:9
```
Texto: **PAN Y PESCADO**

**B — rostro**
```
Ancient clay vessel and a coiled fishing net on stone, soft dawn light from the side,
Sea of Galilee blurred in the far background, warm ochre and earth tones,
photorealistic, high detail, 16:9
```
Texto: **LA MESA REAL**

> Nota: en este video no se genera ninguna figura religiosa identificable.
> Comida y objetos. Es lo que mantiene el video en terreno histórico y fuera de la polémica.

## 5 · Qué se hacía sin anestesia

**A — objeto**
```
Antique 19th century surgical instruments laid out in a row on folded white cloth,
steel catching the light, cinematic museum still life, dramatic side lighting,
warm ochre and earth tone palette, deep dark background, photorealistic,
high detail, clean and clinical, no blood, 16:9
```
Texto: **90 SEGUNDOS**

**B — rostro**
```
Victorian surgeon in dark frock coat standing in a wooden operating theatre,
tiered seating in shadow behind him, gas lamp light from above, warm earth tones,
deep dark background, photorealistic, no blood, no patient, high detail, 16:9
```
Texto: **SIN ANESTESIA**

> Sin sangre, sin paciente, sin detalle gráfico. La miniatura tiene que dar intriga,
> no impresión: es lo que mantiene el video apto para anunciantes.

## 6 · Un día en la vida de una mujer egipcia

**A — objeto**
```
Ancient Egyptian tomb painting fragment showing a woman grinding grain on a stone
saddle quern, faded ochre and red pigment on plaster, cracked surface, museum lighting,
warm earth palette, deep dark background, photorealistic, high detail, 16:9
```
Texto: **AMANECER**

**B — rostro**
```
Profile of an ancient Egyptian woman with black wig and simple linen dress,
painted in tomb fresco style, warm ochre and deep red pigments, cracked plaster texture,
orange dawn sky behind, photorealistic texture, high detail, 16:9
```
Texto: **SU DÍA COMPLETO**

---

## Después de generar

1. Exportar a **1280×720**.
2. Agregar el texto en Photopea o Canva: una sola tipografía condensada pesada,
   blanca con contorno oscuro, 2-4 palabras.
3. **Mirar la miniatura al 20 % de tamaño.** Si a ese tamaño no se distingue el objeto
   ni se lee el texto, no sirve: así es como la ve el espectador en el móvil.
4. Guardar el archivo del prompt que funcionó. La plantilla del canal se construye
   acumulando prompts que dieron resultado, no reinventándolos cada vez.


---

## Lo que aprendimos probando en Canva

Se generó la miniatura 1 en Canva con el prompt original, para comparar. Resultado:

**Lo que salió bien:** la paleta, la luz lateral dura, el fondo oscuro y el tono
documental salieron exactamente como los define el sistema. El objeto quedó centrado
y dominante, y a tamaño chico se lee sin problema.

**Los tres fallos, y son instructivos:**

1. **No puso el texto.** Se pidió "UN KILO AL DÍA" y devolvió solo la imagen.
   Confirma la regla: **el texto se agrega siempre aparte**, nunca en el prompt.
2. **La hogaza es moderna.** Devolvió un pan artesanal de masa madre, alto, crujiente
   y claro. El *panis militaris* romano era bajo, denso y oscuro. El guion del video
   dice literalmente "nada parecido a una hogaza blanca de hoy" — y la miniatura
   mostraba exactamente eso. **La miniatura contradecía al video.**
3. **Cambió el molino por un mortero.** Se pidió una piedra de molino de mano y
   devolvió un mortero con su mano. Herramienta equivocada.

**La lección, que vale para Leonardo igual que para Canva:** un generador de imagen no
sabe historia, sabe estética. Produce el objeto *promedio* que coincide con la palabra,
y el promedio de "pan" es el pan de hoy. Por eso:

- Todo prompt histórico necesita **negaciones explícitas** (`NOT a modern crusty boule`,
  `NOT a mortar and pestle`) además de la descripción.
- Y por eso la regla del canal se sostiene: **la imagen generada es empaque, no
  evidencia.** Sirve de miniatura. Dentro del video, objeto real de museo.
