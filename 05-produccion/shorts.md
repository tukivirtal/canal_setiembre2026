# Shorts para YouTube Shorts, TikTok y Reels

> Reemplaza el método anterior (escenas fijas de Leonardo y recorte en un cuenco).
> El canal ya no tiene cuencos ni imágenes fijas: tiene el mandala animado.

```bash
python3 05-produccion/shorts/hacer_short.py OBRA-012              # el Short 1
python3 05-produccion/shorts/hacer_short.py OBRA-012 --inicio 300 --n 2
```

Toma la obra ya montada (`produccion/<id>/video.mp4`, de `montar.py`), así que no
vuelve a componer. Deja `short-<n>.mp4` y `short-<n>.json` (título, descripción,
etiquetas y el video largo al que enlaza) en la carpeta de la obra.

## Formato

| Parámetro | Valor | Por qué |
|---|---|---|
| Imagen | El mandala de la paleta de la obra, en vertical | Mismo color que el video largo: se reconocen como pareja |
| Tamaño | 1080 × 1920, 45 s | Vertical nativo; por debajo de 60 s en todas las plataformas |
| Recorte | Por defecto, al 40 % de la obra | Pasada la entrada lenta del ambiente: la obra ya suena entera |
| Volumen | −18 LUFS | Se oye en el teléfono; la obra larga va a −22 |
| Fundidos | 1,5 s de entrada, 3 s de salida | Ni arranque ni corte en seco |
| Rótulo | «528 Hz» grande, la intención en una línea, «Full piece · 10 min · on the channel» | Dentro de las zonas seguras de la interfaz de Shorts |

El mandala vertical (`bucles/vertical-<paleta>.mp4`) se renderiza una vez por paleta
y se reutiliza. El rótulo es `shorts/rotulo.html`, una capa transparente encima.

## Al subirlo

En YouTube Studio, en el Short: **Video relacionado** → el video largo de la obra
(está en `short-<n>.json` como `related_video`). Es el enlace que aparece debajo del
Short y lleva al oyente a la obra completa.

Tampoco se publican varios el mismo día: uno cada dos o tres días, alternando obras.

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
