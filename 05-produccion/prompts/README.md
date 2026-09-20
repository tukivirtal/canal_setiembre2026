# Prompts de imagen — generación vía Make

## Por qué no se generan a mano en la web

**La API de Leonardo y la interfaz web no son lo mismo**, y la diferencia es
exactamente el problema de los créditos:

| | Interfaz web | API (vía Make) |
|---|---|---|
| Créditos | Consume los **tokens gratuitos diarios** | Consume los **créditos de API** |
| Modelo | El que tenga seleccionado la interfaz | **El `modelId` que mandás, siempre el mismo** |
| Parámetros | Los defaults de la UI | **Exactos**: alchemy, presetStyle, guidance, tamaño |
| Repetibilidad | Ninguna | Total |

Por eso entrar a la web daba resultados distintos: no era el prompt, era **otro
modelo con otros parámetros**. La API respeta lo que le mandás.

> **A verificar en tu cuenta:** Leonardo separa los créditos de plataforma de los
> de API, y comprar en la web no siempre habilita la API. Si el módulo falla por
> saldo, es ahí donde hay que mirar, no en el escenario.

## Los archivos

| | |
|---|---|
| [`escenas.json`](escenas.json) | **La fuente de verdad.** Lo lee Make desde GitHub |
| [`armar_prompt.py`](armar_prompt.py) | Valida el JSON y muestra el prompt final |
| [`leonardo-obra-001.txt`](leonardo-obra-001.txt) | Las 7 escenas en texto plano, por si hay que pegar a mano |
| [`leonardo-escenas-leonardo.txt`](leonardo-escenas-leonardo.txt) | Las 4 de objeto real, con la colorimetría explicada |

### El prompt no está escrito entero

Se arma como `"extreme close-up photograph of " + sujeto + ", " + base.estilo`.

Así **el estilo del canal vive en un solo sitio**: cambiar `base.estilo` cambia las
siete escenas a la vez. Make hace la misma concatenación en el módulo.

```bash
python3 armar_prompt.py           # valida y lista las 7
python3 armar_prompt.py koro      # el prompt completo de una
```

La validación comprueba ids únicos, campos obligatorios y que ningún prompt pase de
1.500 caracteres. Los siete están entre 1.020 y 1.114, con holgura.

## Modelo y ajustes

**Phoenix 0.9**, y la razón es una sola: **acepta el juego completo de parámetros sobre
el que está construido este JSON** — `negative_prompt`, `contrast`, `alchemy`,
`presetStyle`. El negative prompt hace la mitad del trabajo acá (nada de blancos
quemados, nada de oro vivo, nada de degradados morados), así que un modelo que lo ignore
obliga a rehacer el enfoque entero.

**Nano Banana** es Gemini 2.5 Flash Image. Su ventaja real es la **consistencia entre
imágenes de una misma serie** y la edición conversacional — para siete escenas que deben
parecer la misma habitación, eso no es poca cosa. Su problema es que los modelos Gemini
**no aceptan negative prompt**. Si el conjunto no cuaja con Phoenix, es el plan B, pero
hay que reescribir el negative en positivo antes.

> **Sin verificar:** no pude leer `docs.leonardo.ai` — la red de esta sesión la bloquea.
> Que Phoenix acepta `contrast` y `alchemy` está confirmado por la documentación citada
> en búsqueda. Lo del negative prompt en Nano Banana es una propiedad conocida de los
> modelos Gemini, pero **compruébalo en el módulo de Make** antes de depender de ello.

### Los tres ajustes que explicaban la inconsistencia

| Ajuste | Estaba | Debe estar | Por qué |
|---|---|---|---|
| **Prompt Enhance** | `Auto` | **OFF** | **Este es el grande.** Reescribe tu prompt antes de generar, y cada vez lo reescribe distinto. Destruye la repetibilidad y pisa alegremente un "saturation never above 35%" |
| **Dimensiones** | `1:1 896×896` | **16:9** | Un cuadrado para un video 16:9 obliga a recortar o rellenar |
| **Generation Mode** | `Fast` | **Quality** | Son siete imágenes que definen el canal. El escalón de créditos vale la pena |
| Contrast | `Medium` | **4.0** | La paleta pide claroscuro extremo, no contraste medio |

Prompt Enhance en Auto es, por sí solo, explicación suficiente de por qué dos
generaciones con el mismo prompt salían distintas.

## El escenario de Make

Detalle completo, campo por campo, en [`escenario-make.md`](escenario-make.md).

```
[1] HTTP · Get a file
      https://raw.githubusercontent.com/tukivirtal/canal_setiembre2026/
      claude/clever-gates-03t347/05-produccion/prompts/escenas.json

[2] JSON · Parse JSON

[3] Iterator  →  sobre  escenas[]
      Filtro opcional: pilares contiene "Cuencos" o "Respiración"

[4] Leonardo.Ai · Generate new images
      prompt          "extreme close-up photograph of " + sujeto + ", " + base.estilo
      negativePrompt  base.negative_prompt
      modelId         base.modelId
      width / height  base.width / base.height
      alchemy         true
      presetStyle     CINEMATIC
      numImages       1

[5] Espera + Leonardo.Ai · Get a generation
      La generación es asíncrona: el id vuelve enseguida, la imagen no.
      Si el módulo no espera solo, meter un Sleep de 20-30 s y reintentar
      hasta que el estado sea COMPLETE.

[6] HTTP · Get a file   →  la URL de la imagen generada

[7] Google Drive · Upload a file
      Carpeta  Rin/{obra}/
      Nombre   escena-{orden_obra_001}.png
```

El campo `orden_obra_001` del JSON da directamente el número de archivo, así que el
nombre sale solo y encaja con la convención de
[`../almacenamiento.md`](../almacenamiento.md).

**Empezá con el iterador limitado a una escena.** Cuando esa salga como querés,
soltá las siete. Una pasada mala son siete créditos tirados.

## Los riesgos, escena por escena

El JSON marca cada escena con su riesgo conocido. Cuatro de las siete lo tienen:

| Escena | Riesgo |
|---|---|
| `chawan` | El oro de catálogo sale saturado y rompe la regla de saturación |
| `koro` | Sin `UPRIGHT AND VERTICAL` la varilla sale tumbada |
| `piedras` | Salen secas: el brillo del agua es media sensación táctil |
| `karesansui` | La arena blanca tiende a quemarse por encima del techo del 72 % |

## El control de aceptación

Mirá el histograma, no la miniatura:

- **¿Toca el extremo derecho?** Hay blanco quemado. Descartar.
- **¿La mitad izquierda concentra el histograma?** Correcto.
- **¿El pico es amarillo saturado?** Descartar, sobre todo en `chawan`.

Y la prueba final: al lado de un fotograma del fondo generativo. Si una parece más
clara o más dorada, **el corte se va a notar en el video**.
