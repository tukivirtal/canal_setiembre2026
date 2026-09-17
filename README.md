# Cuenco — canal de música de meditación

Canal de YouTube de música de meditación **compuesta desde cero**, construido siguiendo
los 7 pasos del PDF *"Armado canal YouTube"* aplicados a este nicho.

> **Compuesta con raíz en 528 Hz. Para acompañar una práctica de respiración.**
> No se promete curar nada. Se compone música de calidad para relajarse.

## Las tres reglas del proyecto

1. **Nada viene de fuera.** Cada obra se sintetiza desde la onda: entonación justa,
   estructura respiratoria, cuencos construidos parcial a parcial. Sin bibliotecas, sin
   muestras, sin riesgo de Content ID — y con el máster en propiedad, que es lo que
   permite distribuir a streaming.
2. **Cero afirmaciones de salud, y evidencia citada.** El canal no afirma que la música
   produzca un efecto: describe cómo está construida y cita la investigación sobre las
   técnicas que usa, separando lo bien respaldado de lo preliminar y de lo que no tiene
   evidencia. Ver [base científica](03-composicion/base-cientifica.md).
3. **Cada obra es distinta.** Es la defensa frente a la desmonetización por contenido
   repetitivo, y se verifica con una medida, no con una intención.

## Los 7 pasos

| Paso | Contenido |
|---|---|
| — | [Los 7 prompts originales del PDF](00-prompts/los-7-prompts.md) |
| **2** | [Nicho, identidad y catálogo de 40 obras](01-nicho/nicho-e-identidad.md) |
| **1** | [Plan completo de canal](02-plan/plan-canal.md) |
| **3** | [Sistema de composición](03-composicion/sistema-composicion.md) · [base científica](03-composicion/base-cientifica.md) · [`compositor.py`](03-composicion/compositor.py) |
| **4** | [Algoritmo y crecimiento](04-algoritmo/crecimiento.md) |
| **5** | [Producción](05-produccion/produccion.md) · [prompts de video en Leonardo](05-produccion/prompts-leonardo-video.md) · [publicación automatizada](05-produccion/publicacion-automatizada.md) |
| **6** | [Monetización](06-monetizacion/monetizacion.md) |
| **7** | [Analítica](07-analitica/analitica.md) |
| — | [Control de catálogo, lotes y Codespaces](08-catalogo/README.md) · [Excel](08-catalogo/catalogo_canal.xlsx) |

> El paso 1 se escribe después del 2 porque pide analizar "mi nicho".

## El compositor

```bash
python3 03-composicion/compositor.py --listar
python3 03-composicion/compositor.py --minutos 60 --raiz 528 --modo hirajoshi
```

Sin dependencias, solo Python 3. Tres decisiones lo separan del ambient sintético común,
y están explicadas con los cálculos en
[`sistema-composicion.md`](03-composicion/sistema-composicion.md):

- **Entonación justa** — los intervalos son razones exactas de enteros, así que los
  parciales coinciden en vez de batir. Sobre un drone sostenido es la diferencia audible
  entre "sintetizador" e "instrumento".
- **Pulso respiratorio** — la obra no tiene compás: tiene respiración, que desacelera de
  6 a 4,5 por minuto a lo largo de la pieza.
- **Espacio** — reverberación larga con amortiguación de agudos. Sin ruido de fondo, que
  enmascara justo la cola de reverb que hace que una pieza suene cara.

**Verificado en cada obra:** pico −3,0 dBFS, cero clipping, y variación de RMS entre
tramos que demuestra que la obra evoluciona en lugar de repetirse.

## Las dos cuentas que definen el canal

**Los suscriptores son el cuello, no las horas.** Al revés que en cualquier otro canal:
el oyente pone la pista, apaga la pantalla y consume cuarenta minutos sin ver un
fotograma. Las 4.000 horas llegan solas; los 1.000 suscriptores hay que ganarlos con la
portada, el nombre de la obra y la descripción.

**YouTube es el escaparate, no la caja.** El ingreso real del nicho es la distribución a
Spotify y Apple Music del mismo catálogo — posible únicamente porque el máster es propio.
