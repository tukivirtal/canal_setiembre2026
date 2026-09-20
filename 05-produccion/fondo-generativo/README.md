# Fondo generativo — campo de motas

Fondo de video calculado, no generado por un modelo de imagen.

- [`campo-motas.html`](campo-motas.html) — la animación
- [`render_bucle.js`](render_bucle.js) — la lleva a fotogramas PNG

## Por qué existe

| | Leonardo | Campo de motas |
|---|---|---|
| Duración del movimiento | clips de pocos segundos | **infinito, por construcción** |
| Coste | créditos por imagen | **cero** |
| Propiedad | imagen generada | **geometría calculada, tuya sin matices** |
| Sincronía con la música | ninguna | **respira con la misma envolvente del compositor** |

**Conviven.** El fondo generativo va en **Sueño y Foco**, donde nadie mira la pantalla.
Las escenas de Leonardo van en **Respiración y Cuencos**, donde el objeto real aporta.

## El bucle

**48 segundos exactos = 4 respiraciones a 5/min = un intervalo de cuenco.**

Cada mota recorre un número entero de ciclos en ese tiempo y las ondas nacen una por
bucle, así que el último fotograma empalma con el primero **sin costura**. No es un
fundido disimulado: es periodicidad real.

Por eso el render son 1.200 fotogramas y no 12.000: el bucle se repite con
`-stream_loop` y cubre 8 minutos o 3 horas igual de bien.

## Las luces

Un punto de luz **no es un degradado suave**. Es un núcleo diminuto que se quema a
blanco, rodeado de un halo tenue que lleva el color. El sprite se construye pixel a
pixel con una caída de potencia (`gamma` 2 → 7,5) y el centro tira a blanco mientras el
ámbar aparece al alejarse: así se fotografía una luz cálida de verdad.

El control **Nitidez** recorre esa curva. Y a más nitidez, la mota se dibuja **más
pequeña** — un sprite grande a baja opacidad es exactamente lo que se ve como mancha.

Los **destellos en cruz** (púas de difracción) solo aparecen en las motas grandes del
plano cercano y solo en su pico de brillo: tres o cuatro a la vez. Uno en cada punto
convierte el polvo en un campo de estrellas de ciencia ficción, que es lo contrario
de lo que busca el canal.

## Uso

```bash
npm i playwright
node render_bucle.js                          # 25 fps, 1920x1080, 1200 fotogramas
node render_bucle.js --nitidez 0.85 --dens 200
node render_bucle.js --fps 30 --marca false   # sin el sello, para los shorts
```

El script **no depende del reloj**: le pide a la página que pinte un instante concreto,
así que los fotogramas son deterministas y el bucle cierra al milisegundo. Detecta solo
el Chromium ya instalado (`PLAYWRIGHT_BROWSERS_PATH`) para no descargar 150 MB de más.

Después:

```bash
ffmpeg -framerate 25 -i frames/f%05d.png \
  -c:v libx264 -crf 18 -pix_fmt yuv420p -preset slow bucle48.mp4

ffmpeg -stream_loop -1 -i bucle48.mp4 -i audio/OBRA-001.wav \
  -c:v copy -c:a aac -b:a 320k -shortest video/OBRA-001.mp4
```

**`-c:v copy` es lo que abarata todo:** el video no se recodifica, solo se repite. Una
obra de tres horas se monta en segundos en lugar de en una hora.

Para los shorts, el mismo bucle recortado a 9:16 — y como el fondo es negro, el relleno
lateral es invisible:

```bash
ffmpeg -stream_loop -1 -i bucle48.mp4 -i shorts/OBRA-001_short1.wav \
  -vf "scale=1080:-1,pad=1080:1920:0:(1920-ih)/2:black" \
  -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac -b:a 256k -shortest \
  shorts/OBRA-001_short1.mp4
```
