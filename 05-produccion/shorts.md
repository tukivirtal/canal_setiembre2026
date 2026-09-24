# Shorts para YouTube Shorts, TikTok y Reels

> Reemplaza el método anterior (escenas fijas de Leonardo y recorte en un cuenco).
> El canal ya no tiene cuencos ni imágenes fijas: tiene el mandala animado.

**5 Shorts por obra**, para YouTube Shorts y TikTok.

```bash
python3 05-produccion/shorts/hacer_short.py OBRA-012          # los 5
python3 05-produccion/shorts/hacer_short.py OBRA-012 --n 3    # solo el 3
```

Toma la obra ya montada (`produccion/<id>/video.mp4`, de `montar.py`), así que no
vuelve a componer. Deja `short-<n>.mp4` y `short-<n>.json` en la carpeta de la obra.

## La hoja de Shorts

`08-catalogo/shorts.csv` y la hoja **Shorts** del Excel: una fila por Short (200 para
las 40 obras), generadas por `shorts_catalogo.py` junto con el catálogo. Cada fila
tiene todo lo que se pega al publicar:

| Columna | Dónde va |
|---|---|
| `yt_titulo`, `yt_descripcion`, `yt_etiquetas` | YouTube Shorts |
| `yt_video_relacionado` | YouTube Studio → «Video relacionado»: el video largo |
| `tiktok_portada` | TikTok: el título de la portada, el que se ve en el perfil |
| `tiktok_descripcion` | TikTok: el texto que acompaña al video, con hashtags |
| `estado`, fechas, URLs | A mano, al publicar (amarillas) |

**En TikTok van dos textos distintos.** La portada es corta («639 Hz · calm») y es la
que ordena la cuadrícula del perfil; la descripción es otra frase con los hashtags.
Si algún día se programa con Metricool, **no se usa su campo de título de TikTok**
(lo estamparía sobre el video): solo la descripción, y la portada se pone a mano.

Lo publicado se anota en `08-catalogo/shorts_publicados.csv`
(`id_short,fecha_youtube,url_youtube,fecha_tiktok,url_tiktok`): el catálogo se regenera
desde cero y lo vuelve a aplicar.

## Cinco Shorts, cinco videos distintos

Dentro de una obra, cada Short cambia en todo lo que se ve y se oye:

| | S1 | S2 | S3 | S4 | S5 |
|---|---|---|---|---|---|
| Tramo de la obra | repartidos entre el segundo 90 y el final | | | | |
| Encuadre (zoom) | 1,0 | 1,15 | 1,3 | 1,08 | 1,22 |
| Instante del bucle | 0 s | 9,6 s | 19,2 s | 28,8 s | 38,4 s |
| Frase en pantalla | una de las cinco de la intención | | | | |

Cinco variantes de una plantilla es lo que YouTube penaliza como contenido
repetitivo y lo que TikTok entierra.

## Formato

| Parámetro | Valor | Por qué |
|---|---|---|
| Imagen | El mandala de la paleta de la obra, en vertical | Mismo color que el video largo: se reconocen como pareja |
| Tamaño | 1080 × 1920, 45 s | Vertical nativo; por debajo de 60 s en todas las plataformas |
| Tramos | Cinco, del segundo 90 al final | Pasada la entrada lenta del ambiente: la obra ya suena entera |
| Volumen | −18 LUFS | Se oye en el teléfono; la obra larga va a −22 |
| Fundidos | 1,5 s de entrada, 3 s de salida | Ni arranque ni corte en seco |
| Rótulo | «528 Hz» grande, la frase del Short, «Full piece · 10 min · on the channel» | Dentro de las zonas seguras de Shorts y TikTok |

El mandala vertical (`bucles/vertical-<paleta>.mp4`) se renderiza una vez por paleta
y se reutiliza. El rótulo es `shorts/rotulo.html`, una capa transparente encima.

## Al subirlo

En YouTube Studio, en el Short: **Video relacionado** → el video largo de la obra
(`yt_video_relacionado`). Es el enlace que aparece debajo del Short y lleva al oyente
a la obra completa.

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

## Subida automática a YouTube (Make)

Escenario **«Rin - Shorts a YouTube»** (Make, id 6384211), una vez por día a las 12:00:

```
[1] Google Sheets   Rin_Shorts: la primera fila con estado = pendiente
[2] HTTP            descarga url_archivo (short-<n>-web.mp4, rama «shorts»)
[3] YouTube         lo sube en PRIVADO: título, descripción, etiquetas, Música
[4] Google Sheets   estado = completado, url_youtube, fecha_youtube
```

Queda en privado a propósito: se mira en YouTube Studio, se pone el **video
relacionado** (la API no lo permite) y se pasa a público.

- **La hoja** `Rin_Shorts` (Google Drive de fcippollini): la genera
  `08-catalogo/cola_shorts.py OBRA-012 OBRA-015`. La pestaña se llama `Untitled`:
  no cambiarle el nombre, el escenario la busca así. El orden de las filas es el
  orden de subida.
- **Por qué la versión «-web».** El plan gratuito de Make no mueve archivos de más
  de 5 MB. `hacer_short.py` deja, además del Short de 17 MB, uno en HEVC de ~4,6 MB
  con la misma imagen: ese es el que sube Make. Para TikTok, a mano, el de 17 MB.
- **Dónde está el archivo.** En la rama `shorts` del repositorio (público), que
  solo tiene esos MP4: la URL `raw.githubusercontent.com/...` la descarga Make sin
  credenciales.
