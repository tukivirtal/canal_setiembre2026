# Canal de meditación y ASMR sin riesgo de desmonetización

## El test real de la política

La política no dice "no subas música larga". Dice que el contenido no puede ser
**repetitivo, genérico, manipulador ni de producción masiva**, ni estar hecho con
plantilla, ni ser reutilizado de otros. Esos son cinco criterios distintos, y un canal
de meditación normal falla **cuatro**.

El diseño de abajo los ataca uno por uno.

| Criterio de la política | Cómo falla el canal típico | Cómo se resuelve acá |
|---|---|---|
| **Reutilizado** | Usa música y visuales de otros | Todo el audio se **sintetiza**. No hay fuente externa que reclamar |
| **Repetitivo** | El mismo bucle de 60 s × 480 | Cada obra tiene progresión, secciones y campanas distintas |
| **Hecho con plantilla** | Cambia el número del título y nada más | Cada pieza tiene raíz, escala y estructura propias |
| **Producción masiva** | 5 subidas por día | 2-3 por semana |
| **Manipulador** | "Cura la ansiedad", "sana el ADN" | Cero afirmaciones de salud |

## 1. El audio: construido, no tomado

[`componer_musica.py`](componer_musica.py) — compositor por síntesis aditiva, sin
dependencias.

```bash
python3 componer_musica.py --listar
python3 componer_musica.py --minutos 60 --raiz 528 --escala pentatonica
python3 componer_musica.py --minutos 45 --afinacion 432 --escala lidia --semilla 12
```

**Qué construye, capa por capa:**

- **Colchón armónico** — wavetable de armónicos impares con caída suave (timbre cálido
  tipo órgano; los pares sonarían nasales). Tres voces de la tríada, cada una con dos
  osciladores desafinados un 0,15 %: ese batido lento es lo que da el "ancho" de pad.
  Cada voz respira a distinto ritmo, así que **nunca se alinean**.
- **Sub** — senoidal grave sosteniendo por debajo.
- **Campanas** — parciales **inarmónicos** (1, 2, 2.41, 3, 4.52, 5.63) con decaimiento
  exponencial y los agudos cayendo más rápido. Lo inarmónico es lo que distingue una
  campana de una nota de órgano; la caída desigual es lo que la hace sonar a metal.
  Entran en posiciones irregulares — una rejilla regular suena a metrónomo.
- **Textura** — ruido marrón muy bajo, con los canales levemente descorrelacionados
  para abrir la imagen estéreo.

**Estructura:** secciones de 40-70 s encadenadas por una progresión de cuatro grados.
Suficiente para instalarse, corto para que la obra avance. Las escalas disponibles
(pentatónica, dórica, lidia, japonesa *in sen*) se eligieron porque ninguna produce
tensión sin resolver: nada que despierte al oyente.

**Reproducibilidad:** cada obra imprime su semilla. `--semilla 33 --raiz 528
--escala pentatonica` regenera exactamente ese archivo. Versionás el catálogo sin
guardar gigabytes de WAV.

### Verificado, no supuesto

Sobre una demo de 90 s: **−1,7 dBFS de pico, cero muestras con clipping**, −14,1 dBFS
RMS, imagen estéreo real.

Y la medición que importa para la política: **el RMS varía 1,63× entre tramos de
10 segundos**. Un bucle daría prácticamente el mismo valor en todos. Esta obra
evoluciona, y eso es demostrable con un número.

### Rendimiento, sin adornos

**0,27× tiempo real** en Python puro: una pista de 60 minutos tarda unos 16 minutos de
cómputo. Es lento, pero es coste único por obra y se puede dejar corriendo en segundo
plano mientras trabajás en otra cosa. Conviene generar por lotes de noche.

## 2. Sobre "alta frecuencia vibratoria", con honestidad

El compositor implementa afinación **432 Hz** y las frecuencias **solfeggio**
(396, 417, 528, 639, 741, 852) como raíz.

Ahora la parte que hay que decir: **no hay evidencia científica de que esas frecuencias
curen, sanen o reparen nada.** Son una **elección estética de afinación**, y como tal
son perfectamente legítimas: 432 Hz suena algo más grave y suave que 440, y a mucha
gente le gusta más. El público del nicho las busca y usarlas está bien.

Lo que **no** se puede hacer es prometer efectos clínicos. "Cura la ansiedad",
"sana el ADN", "elimina el insomnio" son afirmaciones falsas, y además te exponen por
desinformación médica y por el criterio de contenido "manipulador" de la propia política
de monetización.

**La formulación segura, que además es la honesta:**

| ❌ | ✅ |
|---|---|
| "528 Hz sana el ADN" | "Compuesta con raíz en 528 Hz" |
| "Cura la ansiedad en 10 minutos" | "Para acompañar una práctica de respiración" |
| "Frecuencia de la transformación" | "Afinación en 432 Hz, escala lidia" |

Describir el sonido, no prometer el efecto. No perdés audiencia: la ganás, porque suena
a alguien que sabe lo que hace.

## 3. El video: dónde está el valor añadido

El audio propio resuelve el reclamo de copyright, pero no basta para "no genérico".
El video tiene que mostrar intención:

- **Visual propio por obra.** No el mismo bucle de stock 40 veces. Un relieve generado,
  una textura, un plano fijo — pero **distinto en cada pieza**.
- **Título con nombre propio**, como un tema de un disco. `Cámara de sal · 432 Hz`,
  no `Música relajante #47`. El título numerado es la firma de la granja de contenido.
- **Descripción técnica**: afinación, escala, estructura, para qué sirve. Es
  literalmente la prueba de que hubo composición.
- **Capítulos marcando las secciones.** Una pista con capítulos reales **demuestra**
  que tiene estructura. Un bucle no puede tenerlos.
- **Duraciones variadas**: 20, 45, 60 min según la obra, no siempre lo mismo.

## 4. Sobre el ASMR específicamente

Dos avisos propios del formato:

1. **Cuidado con la etiqueta.** Buena parte del ASMR cae en anuncios limitados por
   deriva sugerente. Si el canal es de meditación, conviene posicionarlo como **sonido y
   sueño**, no colgarse de "ASMR" como reclamo.
2. **El ASMR sintetizable es el de textura**, no el de voz: lluvia, fuego, viento, agua
   se pueden construir con ruido filtrado más eventos granulares, igual que las
   campanas. Extender el compositor con esas capas es el paso natural, y mantiene la
   regla de que nada viene de fuera.

## 5. Cadencia y catálogo

- **2-3 obras por semana.** El volumen alto es en sí mismo la señal de granja.
- **Series con sentido**, no numeración: un ciclo de piezas por escala, o por hora del día.
- **Distribución a Spotify y Apple Music desde la primera obra**, vía DistroKid o Amuse.
  Ahí está el ingreso real del nicho, y no depende del YPP en absoluto.

## 6. El test que decide

Antes de subir, poné **dos de tus obras seguidas** y que alguien que no sabe nada las
escuche.

**Si no puede distinguir una de otra, YouTube tampoco.** Ese es exactamente el criterio
de la política, y es el único test que importa. Si las distingue —porque la armonía es
otra, porque las campanas caen distinto, porque una respira más lento— el canal está
del lado correcto.

---

## Fuentes

- [Políticas de monetización de canales de YouTube](https://support.google.com/youtube/answer/1311392?hl=es-419)
- [Lineamientos del contenido apto para anunciantes](https://support.google.com/youtube/answer/6162278?hl=es-419)
- [Desmonetización por contenido repetitivo (Comunidad de YouTube)](https://support.google.com/youtube/thread/4840665?hl=es)
