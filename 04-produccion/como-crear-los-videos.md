# Paso 5 — Cómo se crean los videos

Se adelanta al paso 4 porque condiciona qué se puede publicar.

La regla que gobierna todo el flujo: **la IA acelera la producción, nunca reemplaza la
verificación ni la voz.** Ese es el límite entre un canal asistido por IA y uno producido
en masa, que es la diferencia entre monetizar y no monetizar.

---

## 1. La voz: ElevenLabs

**Decisión tomada:** la locución se hace con ElevenLabs, con créditos ya contratados.

La política de contenido no auténtico no prohíbe la voz sintética: apunta al contenido
**producido en masa con plantilla**. Un canal con investigación propia por video,
gráficos hechos a mano y estructura variable no es eso, aunque la voz sea sintética.
Dicho esto, la voz sintética **mal usada** es la señal más visible de canal de bajo
esfuerzo, así que estas seis reglas no son opcionales.

### 1. Cloná tu propia voz
La opción más fuerte: un clon de tu voz gasta los mismos créditos que una voz de catálogo,
pero **no suena como ningún otro canal**. Las voces de catálogo en español las usan miles
de canales; la tuya no la tiene nadie. Resuelve identidad y política de una sola vez.
Si no clonás, elegí una voz poco frecuente y **no la cambies nunca**.

### 2. Escribí los números con letras
Es el error que más delata a un canal de TTS. En el guion:

| ❌ Se lee mal | ✅ Se lee bien |
|---|---|
| `900 g` | `novecientos gramos` |
| `2/3 de medimno` | `dos tercios de un medimno` |
| `s. II a.C.` | `siglo dos antes de Cristo` |
| `30-45 kg` | `de treinta a cuarenta y cinco kilos` |

### 3. Diccionario de pronunciación
Los términos que el modelo va a romper, cargados una vez y reutilizados en todos los videos:
*Polibio, bucellatum, contubernio, posca, medimno, panis militaris, Vindolanda, horreum.*
Si no usás la función de diccionario, escribilos fonéticamente en el guion
(`bucelátum`, `posca`) y guardá esa lista.

### 4. Renderizá por bloques, no el guion entero
Un bloque por sección del guion. Tres ventajas: la prosodia se reinicia en cada bloque y
no se vuelve monótona, podés repetir una sección mala sin gastar créditos en las buenas,
y controlás las pausas en el montaje.

### 5. Ajustes para narración documental
- **Estabilidad media-baja** (~40 %): más alta suena plana; más baja, errática.
- **Similitud alta** (~75 %).
- **Exageración de estilo baja**: el canal narra, no actúa.
- Modelo multilingüe de máxima calidad disponible para español.

### 6. Post-proceso obligatorio en el montaje
Lo que separa una voz sintética buena de una que suena a robot es lo que pasa **después**:

- Compresión suave y un realce leve en agudos.
- **Silencio de 0,4 s antes de cada cifra fuerte** — se agrega en el montaje, no en el render.
- Un fondo de ambiente muy bajo (sala, exterior suave). El silencio digital absoluto es
  lo que hace que una voz suene artificial.
- Escuchá el render completo antes de montar y repetí cualquier frase mal entonada.
  Una sola frase rara por video rompe la credibilidad.

## 2. La imagen: el verdadero cuello de botella

Buscar material es lo que más tiempo consume en un canal de historia. Se resuelve
construyendo **archivo propio reutilizable** desde el primer video.

### Fuentes de dominio público (la columna vertebral)

- **Wikimedia Commons** — pinturas, grabados, fotos de objetos de museo
- **Rijksmuseum** y **The Met (Open Access)** — altísima resolución, uso libre
- **Getty Open Content** y **British Library en Flickr Commons** — grabados e ilustración
- **Biblioteca Digital Hispánica** — manuscritos y material en español
- **Internet Archive** y **Europeana** — libros antiguos, láminas, mapas

### Video de stock
Pexels y Pixabay (gratis) para texturas, fuego, manos trabajando, paisajes.
Artgrid o Storyblocks si más adelante hay presupuesto.

### Lo que te diferencia: gráficos hechos por vos
Mapas simples animados, comparaciones de precios, diagramas de escala, líneas de tiempo.
**Ningún canal de bajo esfuerzo los hace**, y son justamente lo que la política de contenido
no auténtico premia: aporte propio y verificable.

### Imagen generada con IA: con pinzas
En un canal que vive del rigor, una imagen inventada históricamente incorrecta te cuesta
la credibilidad completa. Regla del canal:

- **Nunca** para algo presentado como evidencia (objetos, documentos, hallazgos).
- **Sí**, con moderación, para atmósfera abstracta o transiciones.
- Un objeto real de museo siempre gana contra una ilustración inventada.

### Organización del archivo
Carpetas por período y por tema (`roma/comida`, `medieval/oficios`, `victoriano/medicina`).
A partir del video 10 la mitad del material ya lo tenés. Ahí la producción se acelera de verdad.

## 3. Montaje

**DaVinci Resolve** — gratis, sin marca de agua, profesional. Alternativa rápida: CapCut.

Técnicas que sostienen la retención definida en el paso 3:

- **Corte en cada final de idea.** Plano nuevo cuando termina la frase, no cuando se acaba el clip.
- **Ken Burns** sobre las imágenes fijas: movimiento lento y constante. Una fija quieta más
  de 3 segundos es una invitación a irse.
- **Silencio de 0,4 s** antes de cada cifra fuerte.
- **Texto en pantalla solo para cifras**, nunca para frases completas.
- Música de fondo **muy** baja: bajo la voz, nunca compitiendo.

**Música y sonido:** Biblioteca de Audio de YouTube (gratis y segura). Epidemic Sound si
hay presupuesto. Nunca música comercial, ni "libre de derechos" de origen dudoso: un
reclamo de copyright desvía todos los ingresos del video.

## 4. Miniaturas: Leonardo

**Decisión tomada:** las miniaturas se generan en Leonardo, con créditos ya contratados.

Acá la imagen generada **sí** es válida, y conviene tener clara la distinción:
la miniatura es **empaque**, no evidencia. Nadie la toma como documento histórico.
Dentro del video la regla sigue siendo la contraria: objeto real de museo, nunca ilustración
inventada.

Los seis prompts del lote de prueba están en
[`prompts-leonardo-miniaturas.md`](prompts-leonardo-miniaturas.md).

**Reglas para que las seis se vean del mismo canal:**

- Misma paleta en todos los prompts: ocre, tierra, rojo apagado, fondo oscuro.
- Misma luz: lateral, dura, tipo naturaleza muerta de museo.
- **Un solo objeto** ocupando 40 % del cuadro o más.
- Relación 16:9, exportar a 1280×720.
- El **texto se agrega después**, nunca en el prompt: los generadores todavía escriben mal
  y el texto tiene que ser idéntico en todos los videos. Photopea o Canva, gratis.
- Dos versiones por video, objeto y rostro, para la prueba A/B del paso 3.

## 5. El flujo real, por lote de dos videos

| Etapa | Tiempo (los 2) | Qué se hace |
|---|---|---|
| 1 · Investigación | 3 h | Lectura, notas, cifras. Las dudas se marcan con ⚠️ |
| 2 · Guion | 2 h | Borrador asistido + **reescritura propia** |
| 3 · Verificación | 1 h | Se resuelve cada ⚠️. **Ningún ⚠️ abierto llega a la grabación** |
| 4 · Locución | 1 h | Render por bloques en ElevenLabs + repetición de las frases mal entonadas |
| 5 · Imagen | 2 h | Selección + descarga + carpetas del archivo |
| 6 · Gráficos | 1 h | Mapas y comparativas propias |
| 7 · Montaje | 4 h | Corte, ritmo, música, texto de cifras |
| 8 · Miniatura | 1 h | Leonardo: dos versiones por video + texto agregado aparte |
| 9 · Publicación | 0,5 h | Título, descripción con fuentes, capítulos, programación |

**Total ≈ 16 h por lote de 2 videos**, en línea con el calendario semanal del paso 1.
A partir del video 10 baja a 11-12 h porque el archivo ya está armado.

## 6. Dónde entra la IA y dónde no

| ✅ Sí | ❌ No |
|---|---|
| Ordenar la investigación y proponer ángulos | Dar por buenos los datos que devuelve, sin verificar |
| Borrador del guion, que después reescribís | Publicar ese borrador tal cual |
| Variantes de título y de miniatura | Usar una voz de catálogo que ya usan mil canales |
| Términos de búsqueda de archivo | Generar "evidencia" visual inventada |
| Traducción al inglés en la fase 2 | La misma plantilla repetida en todos los videos |
| Transcripción, capítulos, descripciones | Decidir qué es cierto |

## 7. Presupuesto

| Nivel | Costo | Qué incluye |
|---|---|---|
| **El que ya tenés** | créditos de ElevenLabs + Leonardo | Sin micrófono ni equipo. Resolve, dominio público, Biblioteca de Audio y Photopea son gratis |
| Cómodo | +15-30 USD/mes | Epidemic Sound + stock de pago |
| Innecesario al principio | — | Cámara, luces, set, suscripciones de IA premium |

Con ElevenLabs y Leonardo ya contratados, **el canal no necesita ninguna compra adicional** para empezar.

## 8. Los tres errores que hunden canales faceless

1. **Voz de catálogo + plantilla fija.** Es el perfil exacto que la revisión del YPP
   está filtrando. La voz sintética no es el problema; la voz sintética *idéntica a la de
   otros mil canales*, sobre una plantilla repetida, sí.
2. **Música con reclamo de copyright.** Trabajás gratis para el reclamante.
3. **Empezar sin plantilla visual.** Los primeros diez videos quedan sin identidad común
   y el canal no se reconoce en la barra lateral.
