# Nicho de meditación y espiritualidad — análisis

Consulta puntual, fuera de la secuencia de los 7 pasos.

## Veredicto corto

**Es el perfil exactamente opuesto al canal de historia.** Facilísimo llegar a las
métricas, muy difícil convertirlas en dinero dentro de YouTube.

| Dimensión | Meditación | Historia cotidiana |
|---|---|---|
| Vistas y suscriptores | **Altísimo** | Medio |
| Velocidad a las 4.000 horas | **Semanas** | Meses |
| Costo de producción por video | **Casi cero** | Alto |
| RPM de AdSense | Bajo | Medio-alto |
| **Riesgo de desmonetización** | **Muy alto** | Bajo |
| Ingresos fuera de YouTube | Altos, pero **fuera de YouTube** | Medios |

## 1. Las métricas son espectaculares

Un video de ocho horas visto media hora aporta **media hora de watch time**. Con ese
formato, las 4.000 horas del YPP se alcanzan con unas pocas miles de reproducciones
parciales. Ningún otro nicho acumula horas tan rápido, y la producción por video es
casi gratis. Por eso el nicho atrae tanto.

## 2. Y ahí está exactamente el problema

Ese mismo formato —una pista larga, repetida, replicable a escala— **es la definición
literal de lo que YouTube desmonetiza**. La política de contenido de canal exige que el
contenido no sea "repetitivo, genérico, manipulador ni de producción masiva", y miles
de creadores recibieron el correo de *"tu canal ya no es apto para la monetización
debido a contenido repetitivo o reutilizado"*. Los canales de música relajante son el
caso de manual.

No es un riesgo teórico ni un caso raro: es el modo de fallo **típico** del nicho.

Y se agravó. La actualización que renombró esa política como **contenido no auténtico**
(la misma que condiciona todo el canal de historia, ver
[`01-nicho/analisis-subnichos.md`](../01-nicho/analisis-subnichos.md)) apunta
precisamente a lo producido en masa a partir de plantilla.

## 3. Segundo problema: los reclamos de copyright

Si la música no es tuya, Content ID puede reclamarla y **todos los ingresos del video
se desvían al reclamante**. Ocurre incluso con sonidos ambientales: hay casos
documentados de reclamos sobre grabaciones de lluvia y ruido.

Esto tiene una consecuencia de diseño que ordena todo lo demás:
**el audio tiene que ser tuyo, generado por vos, o el modelo de negocio no cierra.**

## 4. Sobre el RPM, honestamente

Las fuentes se contradicen. Algunas guías afirman CPM de 8-15 USD apuntando a audiencias
de países desarrollados; el consenso más extendido es que la música ambiental está entre
los nichos peor pagados. **No tengo un dato fiable para darte**, y desconfiaría de
cualquiera que te dé una cifra exacta.

Lo que **no** está en discusión es el riesgo de desmonetización, y ese pesa más que
cualquier RPM: un RPM alto sobre un canal desmonetizado vale cero.

## 5. Dónde está la plata de verdad en este nicho

Los proyectos de meditación que ganan dinero **no viven de AdSense**. Usan YouTube como
escaparate y facturan en otro lado:

| Vía | Cómo funciona |
|---|---|
| **Distribución a streaming** | Las mismas pistas en Spotify, Apple Music y YouTube Music vía DistroKid, Amuse o similar. Cobrás por reproducción, sin depender del YPP. **Es la vía principal** |
| Licencia a apps | Apps de sueño y meditación compran catálogos de audio |
| Producto propio | Packs descargables, app, membresía |
| Música de stock | Vender las pistas en bibliotecas de audio |

Un catálogo de pistas propias es un **activo que se explota en muchos sitios a la vez**.
El canal de YouTube pasa a ser un canal de captación, no la fuente de ingresos. Visto
así, el nicho tiene sentido; visto como "monetizar con AdSense", no.

## 6. ¿Se pueden crear los sonidos? Sí, y de tres maneras

### a) Síntesis procedural — la más limpia legalmente
Construir la onda desde cero con código. El audio es **inequívocamente tuyo**: sin
Content ID, sin licencias, sin depender de los términos de ningún proveedor.

Está implementado acá: [`generar_sonido.py`](generar_sonido.py)

```bash
python3 generar_sonido.py --listar
python3 generar_sonido.py --preset theta --minutos 60
```

Sin dependencias, solo Python 3. Genera:

- **Pulso binaural**: un tono ligeramente distinto en cada oído; el cerebro percibe la
  diferencia como un pulso. Presets delta 2 Hz (sueño), theta 4 Hz (meditación),
  alpha 8 Hz (calma despierta). **Requiere auriculares.**
- **Ruido marrón**: ruido blanco integrado, que concentra la energía en los graves.
  Suena a lluvia lejana, no a estática.
- **Colchón armónico**: fundamental grave más su quinta justa.
- **Respiración de volumen** de un ciclo cada 12 s, para que el oído no se acostumbre
  y deje de percibir el sonido.
- Fundidos de entrada y salida de 4 s.

El parámetro `--semilla` fija el ruido: con la misma semilla se regenera exactamente el
mismo audio, lo que permite versionar las pistas sin guardar los WAV.

Verificado sobre una demo de 30 s: −19,5 dBFS RMS, **cero muestras con clipping**,
fundidos correctos y los dos canales genuinamente distintos (sin eso, no hay binaural).

**Rendimiento:** unos 2 s de cómputo por cada 30 s de audio en Python puro. Una hora de
pista tarda unos 4 minutos y ocupa ~635 MB en WAV: conviene convertir a FLAC o AAC
antes de subir.

### b) IA musical
Suno, Udio, Stable Audio o **ElevenLabs Music** — que ya pagás. **Verificá los derechos
comerciales de tu plan concreto antes de publicar**: varían por proveedor y por nivel de
suscripción, y es justo el punto donde un canal se queda sin poder monetizar.

### c) Grabación de campo
Grabar lluvia, viento o agua vos mismo. Tuyo por definición, y es lo que más diferencia
de los miles de canales que usan las mismas bibliotecas.

**Lo más sólido es combinar a y c:** base procedural + grabación propia encima.
Imposible de reclamar y distinto de todo lo demás.

## 7. Dos cautelas

1. **Cero afirmaciones médicas.** "Cura la ansiedad", "sana el ADN", "elimina el
   insomnio": son falsas, y pueden costarte el apto para anunciantes por
   desinformación médica. Describí el sonido, no prometas efectos clínicos.
2. **Cuidado con la espiritualidad como contenido**, distinta del sonido: entrar en
   afirmaciones sobre creencias ajenas cae en temas controvertidos. Es el mismo límite
   que ya aplica al pilar Fe cotidiana del canal de historia.

## 8. Recomendación

**No como canal principal, y no como reemplazo del de historia.** Pero sí tiene sentido
si se plantea bien:

- Como **segundo canal de bajo mantenimiento**, con el catálogo de audio distribuido a
  Spotify desde el primer día — o sea, con el ingreso **fuera** del YPP desde el diseño.
- Con **audio 100 % propio**, procedural o grabado. Nunca librerías de terceros.
- Sin esperar que AdSense sea la fuente de ingresos: si llega, es un extra.

Planteado como "subo pistas largas y monetizo con anuncios", el nicho está mucho más
cerca de la desmonetización que del ingreso.

---

## Fuentes

- [Políticas de monetización de canales de YouTube](https://support.google.com/youtube/answer/1311392?hl=es-419)
- [¿Es un canal de música para relajarse apto para la monetización? (Comunidad de YouTube)](https://support.google.com/youtube/thread/51420198/%C2%BFes-un-canal-de-m%C3%BAsica-para-relajarse-apto-para-la-monetizaci%C3%B3n-por-el-uso-de-m%C3%BAsica-repetitiva?hl=es)
- [Desmonetización por contenido repetitivo (Comunidad de YouTube)](https://support.google.com/youtube/thread/4840665?hl=es)
- [La purga algorítmica y la desmonetización de canales automatizados](https://www.puromarketing.com/123/217085/purga-algoritmica-pone-automatizacion-youtube-desmonetizacion-millones-canales)
- ["Ese ruido tiene derechos de autor" — reclamaciones sobre sonido ambiente (Xataka)](https://www.xataka.com/otros/ese-ruido-tiene-derechos-de-autor-y-otras-historias-de-reclamaciones-en-youtube-bajo-la-sombra-de-un-posible-negocio)
- [Por qué los canales de música de meditación ya no son buena opción para monetizar (Quora)](https://es.quora.com/Por-qu%C3%A9-los-canales-de-m%C3%BAsica-de-meditaci%C3%B3n-y-relax-ya-no-son-una-buena-opci%C3%B3n-en-Youtube-para-ganar-dinero-a-trav%C3%A9s-de-la-monetizaci%C3%B3n)
