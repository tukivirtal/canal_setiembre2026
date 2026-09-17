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

## 6. Uso

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

## 7. Lo que se dice y lo que no

| ✅ Se dice | ❌ Nunca |
|---|---|
| "Compuesta con raíz en 528 Hz" | "528 Hz sana el ADN" |
| "Para acompañar una práctica de respiración" | "Cura la ansiedad" |
| "Entonación justa, modo hirajoshi" | "Frecuencia de la transformación" |
| "Diseñada para la relajación" | "Elimina el insomnio" |

Describir la obra, no prometer el efecto. Es lo honesto, es lo que mantiene el canal apto
para anunciantes, y suena mejor: a alguien que sabe lo que hace.
