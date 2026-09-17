# Publicación automatizada — Leonardo, Cloudinary y Make

## Qué es prueba y qué es producción

| Pieza | Estado | Nota |
|---|---|---|
| Compositor | **Producción** | Verificado: −3,0 dBFS, sin clipping, respiración medible |
| Obra de 8 min | **Producción** | Generada y comprobada. Se regenera con la semilla |
| Catálogo de 40 obras, Excel y CSV | **Producción** | Títulos, descripciones, etiquetas listos |
| Prompts de las 7 escenas | **Producción** | Corregidos tras dos rondas de prueba |
| **Las imágenes generadas hasta ahora** | **Solo prueba** | Hechas en Canva a 595 px para validar el prompt. **No se usan** |
| Montaje y publicación | **Pendiente** | Es lo que define este documento |

Las dos portadas que se generaron sirvieron para **corregir los prompts** —la orientación
de los sujetos, y descartar Canva como herramienta—, no como material publicable.
La imagen de producción sale de Leonardo a 1920 × 1080.

## El stack

| Herramienta | Para qué | Estado |
|---|---|---|
| ~~ElevenLabs~~ | — | **Fuera.** Este canal no tiene voz: la música se sintetiza |
| `compositor.py` | El audio | Propio, sin dependencias, sin coste |
| **Leonardo** | Las 7 escenas y la portada | Créditos ya contratados |
| **Cloudinary** | Almacenar y servir el MP4 y las portadas por URL | — |
| **Make** | Orquestar la subida a YouTube y escribir el resultado al catálogo | — |
| `ffmpeg` | Montar el video | Gratis. Viene en Codespaces |

Que desaparezca ElevenLabs no es un detalle: era el único coste recurrente por minuto de
salida. Ahora el audio es gratis e ilimitado.

## Dónde se monta el video — y por qué no en Cloudinary

Cloudinary **puede** componer video, pero para este catálogo no sale a cuenta. Los números
del plan gratuito son 25 créditos al mes, donde 1 crédito equivale a 1 GB de
almacenamiento, 1 GB de tráfico, o **250 segundos de video HD transformado**.

| Uso de Cloudinary | Coste del catálogo completo (53,7 h) | Cuota |
|---|---|---|
| **Montar** el video con transformaciones | 193.200 s HD ÷ 250 = **773 créditos** | 25 |
| **Almacenar y servir** el MP4 ya montado | 7,7 GB + 7,7 GB ≈ **15 créditos** | 25 |

Montarlo allí cuesta **31 veces la cuota mensual entera**. Almacenarlo y servirlo entra.
Además, la transformación de video tiene un límite de **30 minutos** para MP4 progresivo,
lo que deja fuera de entrada todas las obras del pilar Sueño.

> **La decisión: montar con `ffmpeg`, guardar en Cloudinary, publicar con Make.**
> Cloudinary es el disco y la URL, no el taller.

**Y una consecuencia que ahorra créditos:** en cuanto YouTube confirma la subida, se borra
el MP4 de Cloudinary. El almacenamiento se cobra mientras el archivo esté ahí. No se pierde
nada: el video se rehace desde la semilla y las portadas.

### Tamaños reales

Con audio AAC a 320 kbps y video de imagen fija a 1 fps:

| Duración | MP4 aproximado |
|---|---|
| 8 min | ~25 MB |
| 60 min | ~155 MB |
| 180 min | ~445 MB |

Casi todo el peso es el audio. El video de imagen fija a 1 fps apenas suma.

## El escenario de Make

```
[1] Trigger            Programado, o manual por obra
[2] Google Sheets      Buscar la primera fila con estado = "montada"
[3] YouTube            Upload a Video  ← con URL directa, no con el archivo
[4] YouTube            Set Thumbnail   ← URL de la portada
[5] Google Sheets      Escribir url_video, estado = "publicada", fecha
[6] Cloudinary         Borrar el MP4 (ya está en YouTube)

Las URLs de [3] y [4] **no se consultan**: se construyen con la columna `id`
siguiendo la convención de nombres (ver cloudinary.md). Eso ahorra un módulo
entero y un punto de fallo.
```

**El módulo clave es el [3].** La versión 1.1 de *Upload a Video* de Make admite
**subida directa desde una URL de video, con bajo consumo de transferencia**. Eso es lo
que hace viable el flujo: el archivo **no pasa por dentro de Make**, que es donde se
atascan los videos grandes. Si se usa el módulo en modo archivo, un MP4 de 445 MB del
pilar Sueño es un problema; por URL, no.

Los campos del [3] salen tal cual del catálogo:

| Campo de YouTube | Columna del Excel |
|---|---|
| Title | `titulo` |
| Description | `descripcion_optimizada` |
| Tags | `etiquetas` |
| Category | Música |
| Privacy | (ver la trampa 1) |

### El Excel tiene que ser una hoja de Google, no un .xlsx

El archivo subido a Drive está como **`.xlsx`**, no como hoja de Google nativa. Los módulos
de Google Sheets de Make **no leen un .xlsx guardado en Drive**: necesitan una hoja nativa.

Se arregla en diez segundos: abrir el archivo en Drive y usar
**Archivo → Guardar como Hojas de cálculo de Google**. Eso crea una copia nativa, que es la
que apunta Make. El .xlsx original puede quedarse o borrarse.

## Los cuatro puntos donde esto se rompe

**1 · El video puede quedar bloqueado en privado.** La API de YouTube restringe a privado
las subidas hechas desde proyectos no verificados. Si se usa la **conexión propia de Make
con YouTube**, normalmente no aplica, porque es una aplicación ya auditada; si se crea un
proyecto propio en Google Cloud, sí. **Es lo primero que hay que comprobar con un solo
video**, antes de automatizar cuarenta.

**2 · La miniatura exige canal verificado.** Poner miniatura personalizada requiere tener
el canal verificado por teléfono. Sin eso, el módulo [5] falla y el video sale con un
fotograma automático.

**3 · La cuota diaria de la API.** Una subida consume del orden de **1.600 unidades** de
las 10.000 diarias por defecto: unas **6 subidas al día**. Con una cadencia de 3 obras por
semana sobra, pero descarta de plano cualquier idea de subir el catálogo entero en un día.

**4 · Los créditos de Cloudinary se van en silencio.** El almacenamiento se cobra aunque
el archivo no se use. Sin el paso [7] —borrar tras publicar—, la cuota se agota sola en
dos meses.

## Antes de automatizar nada

**Publicá una obra entera a mano.** Las siete escenas en Leonardo, el montaje con ffmpeg,
la subida manual a YouTube.

Sirve para dos cosas: confirmar que el resultado se ve y se oye como debe, y descubrir
las trampas 1 y 2 con un video en lugar de con cuarenta. Automatizar un proceso que
todavía no diste por bueno es la forma más rápida de producir cuarenta videos con el
mismo defecto.

Una vez publicada la primera y validado el resultado, el escenario de Make convierte las
39 restantes en un trámite.
