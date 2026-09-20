# Escenario de Make — generar las escenas en Leonardo

Construido contra los campos reales del módulo `Leonardo.Ai`.

## Lo que resolvieron los pantallazos

**1 · Ultra y Alchemy son excluyentes.** El propio módulo lo dice bajo Ultra:
*"Only available for Phoenix models. **Cannot be used with Alchemy**."* La versión
anterior del JSON pedía las dos. Corregido.

**2 · Cinematic solo existe bajo PhotoReal.** El desplegable de Preset style agrupa los
estilos por modo: bajo *PhotoReal (enabled)* están Cinematic, Creative, Vibrant y None;
bajo *Alchemy (enabled)* aparecen Anime, Creative, Dynamic, Environment… **Cinematic no
está en esa segunda lista.** Como el encargo es realismo táctil y estilo cinematográfico,
la combinación queda fijada: **PhotoReal + Cinematic**, con Alchemy y Ultra en *No*.

**3 · Las dimensiones son válidas.** El módulo exige entre 32 y 1536 y múltiplo de 8.
**1472 = 184 × 8** y **832 = 104 × 8**, los dos por debajo de 1536: es el 16:9 más grande
que admite. Y avisa que si algún lado pasa de 768 el máximo de imágenes es 4 — usamos 1.

**4 · El modelo es un desplegable.** No hace falta UUID. En el pantallazo aparecía
*Leonardo Vision XL*; hay que cambiarlo a **Phoenix 0.9**, o Ultra ni siquiera estará
disponible.

## Dónde se guardan las imágenes

| | |
|---|---|
| **Los prompts** | **GitHub** — ya están. Es lo que hace rápido iterar el diseño |
| **Las imágenes** | **Drive** |

**Las imágenes no van al repositorio**, aunque sea tentador tenerlo todo junto: son
binarios y Git los guarda **para siempre en el historial**, incluso al borrarlos. Siete
escenas por 40 obras a ~2 MB son ~560 MB que el repo arrastraría en cada clon. El
`.gitignore` ya las excluye.

Lo que hace ágil la iteración no es tener las imágenes cerca: es que **el prompt esté
versionado**. Cambiás `estilo` en el JSON, Make lo recoge en la siguiente pasada, y `git
log` te dice qué versión del prompt produjo qué tanda.

## El escenario

```
[1] HTTP · Get a file
      https://raw.githubusercontent.com/tukivirtal/canal_setiembre2026/
      claude/clever-gates-03t347/05-produccion/prompts/escenas.json

[2] JSON · Parse JSON

[3] Iterator  →  escenas[]
      Para la primera prueba: Filter  id = "rin"

[4] Leonardo.Ai · Generate an image
      Prompt          "extreme close-up photograph of " + sujeto + ", " + base.estilo
      Negative prompt base.negative_prompt
      Model           Phoenix 0.9            ← desplegable, no UUID
      Width / Height  1472 / 832
      Num images      1
      PhotoReal       Yes
      Preset style    PhotoReal (enabled): Cinematic
      Alchemy         No                     ← choca con Ultra
      Ultra           No
      Prompt Magic    No
      Unzoom          No
      Contrast        4

[5] Sleep  ·  25 segundos
      La generación es asíncrona: el id vuelve al instante, la imagen no.

[6] Leonardo.Ai · Get a generation  →  id de [4]
      Si el estado no es COMPLETE, repetir [5]. Con un router que reintente
      hasta 4 veces se cubre de sobra.

[7] HTTP · Get a file  →  la URL de la imagen

[8] Google Drive · Upload a file
      Carpeta  Rin/OBRA-001/
      Nombre   escena-{{orden_obra_001}}.png
```

El campo `orden_obra_001` da el número de archivo, así que el nombre sale del propio
JSON y encaja con la convención de [`../almacenamiento.md`](../almacenamiento.md).

## La prueba que decide el modo

Una escena, dos configuraciones. Se decide con las dos imágenes al lado, no discutiendo:

| | A · PhotoReal | B · Ultra |
|---|---|---|
| PhotoReal | **Yes** | No |
| Preset style | **Cinematic** | None |
| Ultra | No | **Yes** |
| Alchemy | No | No |

**A es la apuesta:** PhotoReal es literalmente el modo de fotorrealismo, y Cinematic solo
existe ahí. **B es la alternativa:** Ultra da más resolución y detalle —solo en modelos
Phoenix— pero renuncia a Cinematic.

Alchemy queda fuera de las dos: choca con Ultra y no ofrece Cinematic.

Corré las dos sobre `rin`, compará contra un fotograma del fondo generativo, y fijá la
ganadora en el JSON. **Dos créditos para cerrar una decisión que afecta a las 40 obras.**
