# Publicación automatizada — montar.py, Drive y Metricool

> Reemplaza la versión anterior (Leonardo + Make). El video ya no es una imagen fija:
> es el mandala animado, y eso cambia el peso de los archivos y, con él, la herramienta.

## Cómo se monta hoy (desde el 24/09)

En **GitHub Actions**, no en la sesión de Claude: `.github/workflows/montar.yml`.
Se lanza con *Actions → Montar una obra → Run workflow → OBRA-020* (o subiendo
`05-produccion/pedidos/OBRA-020.txt`) y en ~1 hora deja una **Release** con el id de
la obra:

    https://github.com/tukivirtal/canal_setiembre2026/releases/tag/OBRA-020

con el video largo, la miniatura, los 5 Shorts y `textos.txt` (todo lo que se pega).
Una Release admite archivos de hasta 2 GB; el repositorio, 100 MB. El repositorio
es público, así que los minutos de Actions no se cobran. Los Shorts livianos van
solos a la rama `shorts`, de donde los sube Make.

El video largo se sigue publicando a mano desde YouTube Studio.

## El flujo previsto (con Metricool)

```
montar.py OBRA-012           →  produccion/OBRA-012/
                                   video.mp4        obra + ambiente + mandala, 1080p
                                   miniatura.jpg    1280×720
                                   metadatos.json   título, descripción, etiquetas,
                                                    categoría, traducción al español
        │
        ▼
Google Drive  Rin/OBRA-012/    el video y la miniatura
        │
        ▼
Metricool     programa el video en YouTube: título, descripción, etiquetas,
              categoría Música, "no es para niños", miniatura, fecha y hora
        │
        ▼
catálogo      url_video, estado = publicada, fecha_publicacion
```

## Por qué Metricool y no Make

| | Make (plan actual) | Metricool |
|---|---|---|
| Tamaño máximo de archivo | **5 MB** (plan Free) | El de YouTube |
| Mueve el video por dentro | Sí: el MP4 atraviesa Make | No: lo toma de Drive o de una URL |
| App verificada por YouTube | Sí | Sí |
| Miniatura personalizada | Módulo aparte | Campo del mismo post |
| Programar fecha y hora | Con `publishAt` | Nativo, con calendario |
| Conectado a esta sesión | Sí | Sí: puedo programar yo cada video |

El límite de 5 MB lo dice la licencia de la organización de Make (`fslimit: 5242880`),
y además el módulo *Upload a Video* de la versión 4 solo acepta el archivo, no una URL.
Un video de 10 minutos con el mandala ya supera ese límite por mucho. Make queda para lo
que ya hace en stoicreset; para Rin no sirve sin pasar a un plan de pago.

**Una app verificada importa.** Si la subida se hiciera con un proyecto propio de Google
Cloud sin auditar, YouTube deja los videos **bloqueados en privado**. Metricool, como Make,
es una app auditada: el video sale público o programado.

## Lo que tiene que hacer la dueña del canal, una sola vez

1. **Conectar YouTube (el canal Rin) en Metricool.**
   `app.metricool.com → Conexiones → YouTube`. Te lleva a la página oficial de Google
   para autorizar; elegís la cuenta de Google dueña de @rinchanneloficial y el canal Rin.
   Nunca se escribe una contraseña en un chat ni en otro sitio que no sea Google.
2. **Vincular Google Drive en Metricool**, con la misma pantalla de conexiones. Así
   Metricool toma el video directamente de la carpeta de Drive.
3. **Verificar el canal por teléfono** en `youtube.com/verify`. Sin esto YouTube no acepta
   miniaturas personalizadas, y el video sale con un fotograma automático.

## Lo que sigue siendo manual (y por qué)

- **La traducción al español de cada video.** Metricool no escribe las traducciones de
  título y descripción de YouTube. Están en `metadatos.json` (`localizations.es`) y en
  el catálogo (`titulo_es`, `descripcion_es`); pegarlas en YouTube Studio →
  *Subtítulos/Traducciones* lleva un minuto por video. Es opcional: el canal ya tiene la
  traducción general al español.
- **El primer video, entero a mano.** Ver abajo.

## Antes de automatizar: el primer video a mano

Se sube la obra de prueba (OBRA-012, 10 minutos) desde YouTube Studio, pegando título,
descripción y etiquetas de su `metadatos.json` y subiendo `miniatura.jpg`. Sirve para
confirmar tres cosas con un solo video y no con cuarenta:

- que el video se ve y se oye bien una vez que YouTube lo procesa;
- que la miniatura se acepta (canal verificado);
- que YouTube no marca nada raro en el audio sintetizado (derechos, avisos).

A partir del segundo, cada video se programa por Metricool.

## Límites que conviene saber

- **Cadencia.** YouTube pone un tope diario de subidas por API a cada app; con 2–3 obras
  por semana no se roza.
- **Peso.** El video de una obra de 3 horas es grande (el bucle del mandala a 1080p más
  el audio). Se mide con la primera obra de Dormir montada; si hiciera falta, se sube el
  `--crf` del mandala o se baja a 720p.
- **Qué se borra y cuándo.** En cuanto YouTube confirma la subida se borra el MP4 de
  Drive. No se pierde nada: `montar.py` lo regenera idéntico con la semilla del catálogo.
