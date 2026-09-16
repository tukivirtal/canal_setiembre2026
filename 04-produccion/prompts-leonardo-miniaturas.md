# Sistema visual de miniaturas — bajorrelieve táctil

Sistema derivado de las imágenes de referencia en Cloudinary: **piedra tallada, humo,
luz rasante**. Reemplaza el enfoque anterior de naturaleza muerta fotorrealista.

---

## 1. Por qué este sistema es mejor que el anterior

La prueba en Canva falló por una razón de fondo: al pedir una foto realista de un objeto
histórico, el generador devuelve **el objeto promedio de hoy** — un pan de masa madre
moderno en vez del *panis militaris* romano. Y una foto realista falsa **afirma algo
falso**: parece evidencia.

El bajorrelieve resuelve las dos cosas de un golpe:

| Problema | Cómo lo resuelve el relieve |
|---|---|
| El generador inventa objetos históricamente incorrectos | Un relieve es **interpretación tallada**, no fotografía. Nadie lo lee como documento |
| La miniatura contradecía al video | Un relieve no afirma detalle: sugiere |
| Seis miniaturas que no se parecen entre sí | Cualquier tema, de Egipto a la era victoriana, se talla en piedra. **Un solo lenguaje para todo el catálogo** |
| Distinguirse del canal faceless promedio | Nadie en el nicho hispano de historia está haciendo esto |

Y cumple lo que pediste: **se tiene que poder tocar**.

## 2. La receta técnica de lo táctil

Lo que hace que una superficie parezca tocable no es "realista" ni "8k". Son cuatro cosas
concretas, y la primera es la que más rinde:

### Luz rasante (*raking light*)
Luz lateral en ángulo muy bajo, que roza la superficie en vez de iluminarla de frente.
**Es literalmente como los museos fotografían los relieves**, porque revela cada
profundidad tallada. Sin esto, ninguna piedra parece tocable. En el prompt:
`raking side light grazing across the surface`.

### Marcas de proceso y de tiempo
La piedra perfecta parece plástico. Lo que la vuelve real es el defecto:
`visible chisel marks, chipped edges, fine surface pitting, weathered patina`.

### Dispersión subsuperficial
El mármol deja pasar algo de luz bajo la superficie. Es la diferencia entre mármol y
cemento pintado: `subsurface scattering in the marble`.

### Lenguaje de cámara, no de render
Pedir una **fotografía de una escultura** en vez de una ilustración de una:
`extreme close-up photograph of a real carved sculpture, shot on 85mm macro lens,
shallow depth of field, physically based rendering`.

## 3. Base común (va en los seis prompts)

```
extreme close-up photograph of a carved stone bas-relief depicting [SUJETO],
weathered marble with visible chisel marks, chipped edges and fine surface pitting,
raking side light grazing across the surface revealing every carved depth,
deep undercut shadows, subsurface scattering in the marble,
volumetric smoke drifting slowly across a deep black background,
one warm amber light source from the left, desaturated stone tones,
shot on 85mm macro lens, shallow depth of field, physically based rendering,
photograph of a real sculpture, not an illustration, hyper-tactile, 8k, 16:9
```

**Negative prompt (en los seis):**
```
smooth plastic, glossy, cgi render, cartoon, illustration, digital painting,
flat lighting, front lighting, text, letters, watermark, modern objects,
multiple subjects, cluttered background, blurry, distorted hands, extra fingers,
oversaturated, pastel colors
```

> **Usá tus referencias de Cloudinary como *style reference* en Leonardo.** Subir dos o
> tres de las 41 imágenes como referencia de estilo fija la estética mucho mejor que
> cualquier prompt escrito. El prompt define **qué** se ve; la referencia define **cómo**.

## 4. Los seis prompts

Cada uno reemplaza `[SUJETO]` en la base común.

**1 · Qué comía un soldado romano**
`a Roman legionary's hands breaking a flat round coarse loaf of bread, a rotary hand
quern of two flat stone discs beside it, scattered wheat grains carved into the stone`
→ Texto: **UN KILO AL DÍA**

**2 · Cómo se bañaba la gente en la Edad Media**
`a medieval wooden bathing tub with a figure seated inside, carved steam rising in
spiral curls, a servant pouring water from a jug`
→ Texto: **SÍ SE BAÑABAN**

**3 · Cuánto costaba vivir en 1650**
`a merchant's balance scale with stacked coins on one pan and a loaf of bread on the
other, a ledger and quill carved below`
→ Texto: **UN DÍA DE SUELDO**

**4 · Qué comía la gente en tiempos de Jesús**
`flat round loaves, two fish and a clay cup arranged on a low stone table, a fishing
net carved along the lower edge, early Christian relief style`
→ Texto: **PAN Y PESCADO**

**5 · Qué se hacía sin anestesia**
`a row of antique surgical instruments — saw, scalpel, forceps — laid out in strict
order on folded cloth, no blood, no figures, clinical and cold`
→ Texto: **90 SEGUNDOS**

**6 · Un día en la vida de una mujer egipcia**
`an Egyptian woman kneeling and grinding grain on a saddle quern, Egyptian sunken
relief style, hieroglyph column carved to one side`
→ Texto: **SU DÍA COMPLETO**

> El video 6 es el más fácil: el relieve **es** el medio nativo del arte egipcio.
> Conviene producirlo primero, para calibrar el sistema con el caso más favorable.

## 5. Tipografía

Investigada, no elegida al azar. El consenso de las guías de 2026 es unánime en una cosa:
**los pesos pesados ganan siempre**, porque la miniatura se ve a tamaño de sello.

### La decisión

| Uso | Tipografía | Por qué |
|---|---|---|
| **Texto de miniatura** | **Anton** | Sans condensada ultra pesada, gratis en Google Fonts. Es el "titular documental": el mismo registro que usa Veritasium. Máxima legibilidad por píxel |
| Alternativa | Bebas Neue | Más estilizada y algo más fina. Segunda opción si Anton se ve demasiado brutal sobre la piedra |
| **Nombre del canal / cierre** | Cinzel | Serif romana con gravedad histórica. **Solo** para el logo y la pantalla final |

### Por qué Anton y no una serif histórica

Es contraintuitivo, pero es la decisión correcta: **el relieve ya aporta toda la gravedad
histórica**. Si encima ponés una serif romana como Cinzel, el texto se funde con la piedra
y desaparece. El texto tiene el trabajo contrario: **contraste brutal contra la textura**.
Una sans condensada pesada sobre mármol tallado se lee; una serif sobre mármol tallado
es mármol.

Cinzel sirve para el logo, donde hay tiempo de mirar. No para el texto que tiene que
leerse en la barra lateral de un móvil en medio segundo.

### Especificación fija

- **Mayúsculas siempre**, 2-4 palabras, nunca el título repetido.
- **Blanco puro** con contorno oscuro de 3-4 px y sombra suave. Sobre piedra gris, el
  blanco es el único color con contraste garantizado.
- Alineado a un lado, **nunca tapando el foco tallado**.
- Un solo color de acento permitido, y solo para una palabra: ámbar cálido, el mismo
  de la luz del prompt.
- Nada de degradados, biseles ni sombras largas: rompen el tono documental.

### El test que no se puede saltear

**Exportá la miniatura y miralas a 168 × 94 píxeles.** Ese es el tamaño real en un móvil.

Si a ese tamaño no se distingue el objeto tallado o no se lee el texto de un vistazo,
la miniatura no sirve — no importa lo bien que se vea a tamaño completo. Es el único
test que importa, y es donde se pierde el dinero.

## 6. Flujo de trabajo

1. Generar en Leonardo con la base + el sujeto + tus referencias de Cloudinary como estilo.
2. Descartar todo lo que tenga superficie lisa o luz frontal: falló lo táctil.
3. Exportar a 1280 × 720.
4. Agregar el texto en Photopea con la especificación fija (Anton, blanco, contorno).
5. **Mirar a 168 × 94.**
6. Dos versiones por video para la prueba A/B del paso 3: una con el objeto tallado
   centrado, otra con figura humana tallada.
7. Guardar el prompt que funcionó. La plantilla se construye acumulando aciertos.

---

## Fuentes

- [Mejores fuentes para miniaturas de YouTube 2026 (Figma)](https://www.figma.com/resource-library/best-fonts-for-thumbnails/)
- [Best YouTube thumbnail fonts for higher CTR 2026 (1of10)](https://1of10.com/blog/best-youtube-thumbnail-fonts/)
- [Best fonts for YouTube thumbnails 2026 (ThumbnailCreator)](https://www.thumbnailcreator.com/blog/best-fonts-for-youtube-thumbnails)
- [YouTube thumbnail fonts: what top creators use (Thumix)](https://www.thumix.com/blog/youtube-thumbnail-fonts)
