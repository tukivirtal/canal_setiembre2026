# Paso 3 — Sistema de composición

El equivalente al paso 3 del método original ("guiones, hooks y miniaturas"): acá el
producto no es un guion, es **la obra**. Este documento explica por qué suena como suena.

Implementación: [`compositor.py`](compositor.py) · sin dependencias, solo Python 3.

---

## 1. Entonación justa: la decisión que separa caro de barato

La música de meditación es **drone sostenido**. Un acorde que dura cuarenta segundos
expone cualquier impureza de afinación, y ahí es donde casi todo el nicho suena
sintético sin saber por qué.

### El cálculo

Sobre una raíz de **528 Hz**, la tercera mayor:

| | Frecuencia | Desviación |
|---|---|---|
| Temperamento igual (2^(4/12)) | **665,2 Hz** | 400,00 centésimas |
| Entonación justa (5/4) | **660,0 Hz** | 386,31 centésimas |

La diferencia es de **13,7 centésimas**. Parece nada. Ahora miremos los armónicos:

- 5.º armónico de la raíz: 528 × 5 = **2640,0 Hz**
- 4.º armónico de la tercera justa: 660 × 4 = **2640,0 Hz** → **coinciden exactamente**
- 4.º armónico de la tercera temperada: 665,2 × 4 = **2661,0 Hz** → **batido de 21 Hz**

Veintiún batidos por segundo en la región de 2,6 kHz, donde el oído es más sensible. En
una nota corta no se nota. En un drone de cuarenta segundos es una aspereza constante
que **cansa** — exactamente lo contrario de lo que busca la pieza.

En entonación justa los parciales se superponen y las voces dejan de ser tres notas:
se funden en **un solo cuerpo sonoro**. Esa fusión es la sensación de "instrumento real".

### Y además sale gratis

Como todos los intervalos son razones de enteros, **el acorde completo es periódico**.
Para el modo hirajoshi las voces son 1/2, 1/1, 6/5 y 8/5: el mínimo común múltiplo de
los denominadores es 10, así que el acorde entero se repite a 528/10 = **52,8 Hz**, o sea
cada 18,9 ms.

Eso permite sintetizar **un solo período** en una tabla y leerla con un único puntero,
en lugar de calcular cinco osciladores por muestra. La misma propiedad que da la pureza
da un cómputo cinco veces más barato. Esas cosas no suelen coincidir.

## 2. La respiración como estructura

La obra no tiene compás ni tempo. Tiene **ciclo respiratorio**.

| Parámetro | Valor | Cálculo |
|---|---|---|
| Ritmo inicial | 6,0 resp/min | ciclo de **10,00 s** |
| Ritmo final | 4,5 resp/min | ciclo de **13,33 s** |
| Inhalar / exhalar | 40 % / 60 % | 4,0 s dentro, 6,0 s fuera |
| Sección | 6 respiraciones | 60 s al inicio, 80 s al final |
| Cuenco | cada 4 respiraciones | 40 s al inicio, 53 s al final |

**Por qué exhalar más largo:** es el patrón que toda práctica de relajación usa. La
envolvente lo respeta, así que quien respira con la música cae en él sin que nadie se lo
explique.

**Por qué desacelera:** la obra empieza a un ritmo cómodo y va bajando. Quien acompaña la
música va detrás. Es **intención compositiva**, no una afirmación clínica: no se promete
ningún efecto fisiológico, se construye una pieza que invita a un ritmo.

**Por qué todo cae en múltiplos enteros del ciclo:** secciones y cuencos coinciden con la
respiración, así que nada llega a destiempo. Sin esto los cuencos sonarían encima de una
inhalación y romperían justo lo que la pieza intenta sostener.

**Verificado:** en la obra de prueba se detectaron 17 ciclos de envolvente, pasando de
**9,2 s al principio a 12,0 s al final**. La desaceleración no es una intención escrita
en un documento: está en la onda y se mide.

## 3. El timbre

### El pad
Armónicos **impares** con caída 1/n^1,6 — (1, 0.26, 0.11, 0.05, 0.025). Los impares dan
cuerpo de órgano; los pares sonarían nasales. La caída pronunciada elimina el brillo
metálico que delata al sintetizador barato. Las fases de cada parcial se dispersan al
azar, lo que baja el factor de cresta y permite más nivel sin saturar.

### El cuenco
Dos detalles hacen toda la diferencia frente a una campana genérica:

1. **Parciales inarmónicos**: 1 : 2,75 : 5,38 : 8,90. Una serie armónica sonaría a
   órgano golpeado, no a metal.
2. **Cada modo desdoblado un 0,35 %.** Para un cuenco de 528 Hz eso son dos parciales a
   528,0 y 529,85 Hz, que baten a **1,85 Hz**. Ese bamboleo lento **es** el sonido del
   cuenco cantor. Sin él, cualquier síntesis suena a plástico.

Los agudos decaen más rápido que los graves (velocidades 0,9 / 1,5 / 2,4 / 3,6), que es
lo que hace que el golpe suene a metal y no a nota sostenida.

### El espacio
Reverberación de Schroeder: cuatro peines en paralelo con retardos primos entre sí (para
que las reflexiones no se agrupen en eco) y tres paso-todo en serie.

Realimentación calculada para el RT60 pedido: **g = 10^(−3·T/RT60)**. Con un retardo de
1557 muestras (35,3 ms) y RT60 de 6 s → g = 0,960.

La **amortiguación de agudos (0,42)** es lo decisivo: sin ella la cola brilla y silba, que
es el sonido inconfundible del reverb barato. Con ella, la cola se oscurece al alejarse,
como en una sala real.

## 4. Por qué se quitó el ruido de fondo

Tenías razón, y la razón técnica es el **enmascaramiento**.

El ruido marrón tiene energía repartida por todo el espectro. Lo que enmascara primero
es lo más débil: **la cola de la reverberación y el final del decaimiento del cuenco**.
Y eso es exactamente lo que hace que una pieza suene cara — el espacio, la profundidad,
el modo en que un sonido se va.

Poner ruido de fondo es pagar por una reverberación de seis segundos y después taparla.

Ahora está en **0 por defecto**. La opción `--aire` existe para un hilo de aire muy tenue,
con el aviso escrito de que por encima de 0,02 ensucia el drone.

## 5. Niveles

| Medida | Valor | Criterio |
|---|---|---|
| Pico | **−3,0 dBFS** | Normalizado exacto, sin limitador |
| RMS | **−16,5 dBFS** | Factor de cresta de 13,5 dB |
| Clipping | **0 muestras** | Verificado en cada obra |
| DC offset | **0,0** | — |

**No se masteriza fuerte, y es deliberado.** La música de meditación tiene que ser
silenciosa y dinámica: el oyente pone el volumen donde quiere, normalmente bajo y de
noche. Comprimir hasta −9 dBFS, que es lo normal en música comercial, destruiría el
swell respiratorio — que es la pieza entera.

## 6. Cómo se compone un video

La pregunta importante: **¿un video es una mezcla de composiciones?**

**No. Un video es UNA composición continua.** Y conviene separar tres cosas que en
castellano se llaman igual "mezcla", porque una de las tres es justo la que hunde canales.

| Sentido de "mezcla" | ¿Se hace? | Qué es |
|---|---|---|
| **Mezclar capas** | **Sí, siempre** | Colchón + sub + cuencos + reverb suenan a la vez. Es mezcla de audio, y es como se construye cada obra |
| **Mezclar fragmentos entre videos** | **Nunca** | Tener una biblioteca de trozos y recombinarlos. **Es exactamente lo que la política penaliza**: si el video A y el B comparten material, no son dos obras, son dos variantes de una plantilla |
| **Encadenar obras distintas** | Sí, en obras largas | Un video de 3 horas puede ser tres obras de una hora con fundidos cruzados. Es un disco, no un bucle — siempre que cada obra sea única de ese video |

La regla de fondo: **una obra no se reutiliza jamás entre videos.** El compositor genera
material nuevo cada vez, así que no hay biblioteca que recombinar. Es lo que mantiene el
catálogo del lado correcto sin esfuerzo.

### Un video de 8 minutos, sección a sección

`--plan` imprime la estructura sin sintetizar, para poder revisarla antes de gastar
minutos de cómputo:

```bash
python3 compositor.py --plan --minutos 8 --raiz 528 --modo hirajoshi --semilla 42
```

```
 #    desde    dura  resp/min    grado                 acorde (Hz)
 1    0.00'   60.0s      6.00      1/1   264.0  528.0  633.6  844.8
 2    1.00'   61.9s      5.81      9/8   297.0  594.0  792.0  528.0
 3    2.03'   64.1s      5.62      9/8   297.0  594.0  792.0  528.0
 4    3.10'   66.4s      5.42      1/1   264.0  528.0  633.6  844.8
 5    4.21'   69.1s      5.21      3/2   396.0  792.0  528.0  633.6
 6    5.36'   72.1s      5.00      6/5   316.8  633.6  844.8  594.0
 7    6.56'   86.4s      4.77      1/1   264.0  528.0  633.6  844.8

7 secciones · 42 respiraciones · 10 cuencos
```

Lo que hay que leer en esa tabla:

- **Las secciones se alargan solas**: 60,0 s → 86,4 s. No es una decisión estética, es
  consecuencia de que cada sección son siempre **6 respiraciones** y la respiración se
  va ralentizando. La estructura la dicta el cuerpo, no un reloj.
- **El acorde se mueve y vuelve.** Secciones 1, 4 y 7 son la tónica (1/1); entre medias
  se va a 9/8, 3/2 y 6/5. Hay ida y regreso — o sea, hay forma.
- **Los cuencos también se espacian**: del minuto 0,67 al 1,35 hay 41 s; del 6,61 al 7,45
  hay 50 s. Siempre cada 4 respiraciones.
- **La última sección absorbe el resto** (86,4 s en vez de 75,5 + un muñón de 11 s). Un
  cambio de acorde diez segundos antes del fundido final se oye como un error.

### Por qué 8 minutos concretamente

Es el **umbral de los anuncios intermedios**: por debajo de 8 minutos YouTube no permite
mid-rolls. Un video de 8 minutos es el más corto que puede llevar más de un anuncio.

Dicho eso, para este nicho 8 minutos es corto. Encaja bien en el pilar Respiración —una
práctica guiada breve— pero el catálogo se apoya en obras de 45 a 180 minutos, que es
donde se acumulan las horas. Los 8 minutos sirven como **puerta de entrada**: alguien
prueba una pieza corta y de ahí pasa a las largas.

### Encadenar obras en un video largo

Para un video de 3 horas hay dos caminos válidos:

1. **Una sola obra de 180 minutos.** El compositor la genera entera: ~63 min de cómputo.
   Las secciones siguen alargándose y la respiración baja hasta el final.
2. **Tres obras de 60 minutos encadenadas** con fundidos cruzados de 20-30 s. Más variedad
   armónica, y cada obra con su propia raíz o modo.

La segunda es mejor para sueño, porque una obra de tres horas sobre un solo recorrido
respiratorio termina demasiado lenta. La condición sigue siendo la misma: **esas tres
obras se componen para ese video y no reaparecen en ningún otro.**

## 7. Registro: la altura de la obra

El registro por defecto deja el sub en **raíz / 2**. Con raíz 528 Hz eso son **264 Hz**, y
ahí está el problema: un drone de sueño vive entre **60 y 120 Hz**. El canal, tal como
estaba, sonaba **dos octavas por encima** de donde debería sonar la música de dormir.

```bash
--registro grave       # ×0,5 — raíz 264 Hz, sub en 132 Hz
--registro medio       # ×1   — por defecto
--registro brillante   # ×2
```

Medido comparando la misma obra en los dos registros:

| Registro | Energía bajo 200 Hz | Energía sobre 2 kHz |
|---|---|---|
| medio (528 Hz) | −9,4 dB | −10,6 dB |
| **grave (264 Hz)** | **−3,9 dB** | **−16,2 dB** |

**+5,5 dB de graves y −5,6 dB de agudos.** No es una impresión: es otra música.

### Qué registro lleva cada pilar

| Pilar | Registro | Por qué |
|---|---|---|
| **Sueño** | **grave** | Se escucha de noche, a volumen bajo y con la pantalla apagada |
| **Foco** | grave o medio | Tiene que desaparecer del primer plano |
| **Respiración** | medio | Se escucha despierto y con atención |
| **Cuencos** | medio | El cuenco necesita su registro natural |
| **Frecuencias** | medio | La raíz anunciada es el producto |

> **Y una nota de honestidad en la descripción:** si una obra usa `--registro grave` con
> raíz 528, la raíz real es **264 Hz**. Lo correcto es escribir *"raíz en 264 Hz, octava
> grave de 528 Hz"*. Poner "528 Hz" a secas sería inexacto, y la exactitud es el argumento
> del canal.

## 8. Aves

```bash
--aves 1.5     # 0 = ninguna · 1 = dispersas · 2 = más
```

**Sintetizadas, no grabadas.** Un canto de pájaro es, en el fondo, un **barrido rápido de
frecuencia**: un tono que se desliza de 3.000 a 4.300 Hz en 120 milisegundos. Eso se
construye. Cada frase junta de dos a cinco gorjeos con silencios entre ellos, con la
dirección del barrido al azar, así que **ningún pájaro se repite jamás**.

Tres detalles hacen que suenen a pájaro lejano y no a sintetizador:

1. **El segundo armónico al 30 %** da el timbre metálico del canto real.
2. **Un paso bajo a 2,6 kHz** les quita el filo. Un gorjeo crudo es penetrante; lo que se
   busca es un pájaro *lejos*, no uno en la ventana.
3. **Pasan por la misma reverberación** que el resto, así que comparten sala con los
   cuencos en vez de sonar pegados encima.

### Activadas por defecto, en todas las obras

Decisión del canal: **todas las obras llevan canto de ave**. Aporta una armonía distinta
y descansa el oído del drone sostenido.

**Y se rarifican solas.** El intervalo entre frases crece a lo largo de la obra y el
volumen baja: al final cantan **cuatro veces menos** que al principio y un 55 % más bajo.

Medido en una obra de 60 minutos: **16 frases en el primer tercio, 7 en el segundo,
6 en el último**, con el volumen cayendo de 0,77 a 0,39.

Es el mundo que se va quedando en silencio mientras la respiración se hace más lenta. Y
resuelve solo la única objeción que tenía ponerlas en todas partes: en una obra de dormir
**hay pájaros, pero ya se han ido** para cuando el oyente se duerme. El canto del atardecer,
no el de las tres de la mañana.

### La otra regla

**Nunca a menos de 3 segundos de un cuenco.** Los dos son transitorios agudos: si
coinciden, el pájaro le roba el golpe al cuenco, que es lo que marca la respiración.
El planificador lo impone.

### Por qué no se usan grabaciones

Una grabación de biblioteca rompe las dos reglas que sostienen el canal: deja de ser
íntegramente propio —con el riesgo de reclamo de Content ID que eso implica, documentado
incluso sobre sonido ambiente— y **cierra la puerta a la distribución a streaming**, que
es la vía de ingresos real del nicho.

La alternativa legítima es **grabarlos vos mismo**. Si algún día lo hacés, entra sin
problema: sería tuyo.

### Sobre la reproducibilidad

Las aves usan un **generador aleatorio propio**, sembrado aparte del de las secciones y
los cuencos. Si compartieran el mismo, activar las aves cambiaría la obra entera y las
semillas ya publicadas dejarían de reproducir el mismo audio. Comprobado: el plan de una
semilla dada es idéntico antes y después de añadir esta función.

## 9. Uso

```bash
python3 compositor.py --listar
python3 compositor.py --minutos 60 --raiz 528 --modo hirajoshi
python3 compositor.py --minutos 45 --raiz 432 --modo kumoi --semilla 7 --rt60 8
```

| Modo | Razones | Carácter |
|---|---|---|
| `yo` | 1/1 9/8 5/4 3/2 5/3 | Pentatónica mayor: luminosa, abierta |
| `hirajoshi` | 1/1 9/8 6/5 3/2 8/5 | Japonesa de koto: contemplativa |
| `kumoi` | 1/1 6/5 4/3 3/2 9/5 | Pentatónica menor: grave, introspectiva |
| `shin` | 1/1 3/2 2/1 | Drone puro: lo más estable posible |

Ninguna tiene semitonos entre grados consecutivos: **no hay tensión que resolver**, que
es la condición para que una pieza se pueda escuchar una hora sin fatiga.

**Reproducibilidad:** cada obra imprime su semilla. Con `--raiz`, `--modo` y `--semilla`
se regenera idéntica, así que el catálogo se versiona sin guardar los WAV.

**Rendimiento:** ~0,47× tiempo real. Una hora de obra son unos 21 minutos de cómputo.
Conviene generar por lotes de noche.

## 10. Lo que se dice y lo que no

| ✅ Se dice | ❌ Nunca |
|---|---|
| "Compuesta con raíz en 528 Hz" | "528 Hz sana el ADN" |
| "Para acompañar una práctica de respiración" | "Cura la ansiedad" |
| "Entonación justa, modo hirajoshi" | "Frecuencia de la transformación" |
| "Diseñada para la relajación" | "Elimina el insomnio" |

Describir la obra, no prometer el efecto. Es lo honesto, es lo que mantiene el canal apto
para anunciantes, y suena mejor: a alguien que sabe lo que hace.
