# Shorts para TikTok, Reels y YouTube Shorts

**4-5 shorts por obra**, extraídos automáticamente.
Herramienta: [`03-composicion/extraer_shorts.py`](../03-composicion/extraer_shorts.py)

```bash
python3 03-composicion/extraer_shorts.py audio/OBRA-001.wav \
  --raiz 528 --modo hirajoshi --semilla 454078 --minutos 60 --n 5
```

## Por qué no corta al azar

El script **le pregunta al compositor en qué segundo cae cada cuenco** — con la misma
semilla, los instantes son exactamente los de la obra— y empieza el recorte **1,2 segundos
antes de uno**.

Eso importa por una razón concreta: en TikTok y en Reels, **el primer segundo decide**. Un
short de música ambiente que arranca con un fundido no retiene a nadie. Arrancando justo
antes de un cuenco, lo primero que se oye es un golpe de metal con su cola.

Medido en los cinco shorts de la obra de prueba: **el golpe cae dentro de los 3 primeros
segundos en los cinco**, y en dos de ellos ese golpe **es el pico de todo el short**.

Los cuencos elegidos se **reparten a lo largo de la obra**, no se toman los primeros: cinco
shorts del mismo minuto sonarían los cinco igual.

## Formato

| Parámetro | Valor | Por qué |
|---|---|---|
| Duración | **45 s** | Suficiente para que el cuenco decaiga entero; por debajo de 60 s en todas las plataformas |
| Entrada | 0,8 s | Corta, para no comerse el ataque |
| Salida | 3,5 s | Larga, para no cortar en seco |
| Formato | 1080 × 1920 (9:16) | Vertical nativo |
| Audio | AAC 256 kbps | — |

### El truco del fondo negro

Las escenas son un objeto aislado sobre **negro absoluto**. Eso permite convertir el 16:9
en 9:16 **rellenando arriba y abajo con negro**: como el fondo ya es negro, el relleno es
invisible.

```bash
ffmpeg -loop 1 -i portadas/escena1.png -i shorts/obra_short1.wav \
  -vf "scale=1080:-1,pad=1080:1920:0:(1920-ih)/2:black" \
  -c:v libx264 -tune stillimage -pix_fmt yuv420p -r 1 \
  -c:a aac -b:a 256k -shortest shorts/obra_short1.mp4
```

No hace falta generar imágenes verticales aparte. Es una consecuencia directa de la
decisión visual de fondo negro, y ahorra la mitad de los créditos de Leonardo.

## La regla que no se puede saltar

> **Un short, una escena distinta.**

Cinco shorts con la misma imagen son cinco variantes de una plantilla — exactamente lo que
penaliza la política de contenido no auténtico, y exactamente lo que TikTok entierra por
repetitivo. Como la obra tiene 7 escenas y se sacan 5 shorts, siempre hay material para
que cada uno sea distinto.

Tampoco se publican los cinco el mismo día: uno cada dos o tres días, alternando obras.

## Para qué sirven realmente

**No para las horas de visualización.** Las vistas del feed de Shorts **no cuentan** para
las 4.000 horas del YPP.

Sirven para lo otro, que es el cuello de botella real del canal: **conseguir suscriptores**
(ver [`../04-algoritmo/crecimiento.md`](../04-algoritmo/crecimiento.md)). El oyente de una
obra larga apaga la pantalla y no se suscribe nunca; el espectador de un short está
mirando.

Por plataforma:

| Plataforma | Qué aporta | Nota |
|---|---|---|
| **YouTube Shorts** | Suscriptores al mismo canal | El más directo. Enlazar la obra larga |
| **TikTok** | Alcance nuevo | El público de sueño y estudio está ahí. Enlace en la biografía, no en el video |
| **Instagram Reels** | Alcance y guardados | Secundario: menos tráfico saliente que TikTok |

## Texto en pantalla

Una sola línea, abajo, tipografía fina:

```
528 Hz · entonación justa
```

**Nunca** una promesa de efecto. La misma regla que en el canal: describir la obra.
Lo que engancha acá es el sonido y la imagen, no el texto.

## Descripción tipo

```
Fragmento de «[nombre de la obra]», compuesta con raíz en [X] Hz
en entonación justa.
Obra completa de [duración] en el canal.

#[frecuencia]Hz #MúsicaRelajante #Meditación
```
