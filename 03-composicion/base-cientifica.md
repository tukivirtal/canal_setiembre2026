# Base científica del canal

Este documento existe para que **cada decisión de composición esté respaldada por algo
comprobable**, y para que quede escrito con precisión qué está respaldado y qué no.

## La regla que lo gobierna todo

> **El canal no afirma que la música produzca un efecto. El canal describe cómo está
> construida y cita la investigación sobre las técnicas que usa.**

La diferencia parece sutil y lo es todo:

| ❌ Afirmación de efecto | ✅ Descripción de diseño |
|---|---|
| "Esta música reduce la ansiedad" | "Construida sobre un ciclo de 6 a 4,5 respiraciones por minuto, el rango que la investigación sobre respiración lenta documenta" |
| "528 Hz repara el ADN" | "Compuesta con raíz en 528 Hz" |
| "Verificada por neurólogos" | "Afinada en entonación justa para evitar la aspereza de los batidos dentro de la banda crítica" |

La segunda columna es **verificable**, no promete nada, mantiene el canal apto para
anunciantes, y es mucho más persuasiva para el público que de verdad paga: profesores de
yoga, practicantes y gente que ya distingue el marketing esotérico de lo serio.

**Sobre "verificado por neurólogos":** no se puede escribir si no ha ocurrido. Si en algún
momento querés esa credencial de verdad, el camino legítimo existe: encargar una revisión
a un profesional cualificado que acepte ser nombrado, o colaborar con alguien del área.
Una credencial real, con nombre y apellido, vale; un sello genérico no, y además es el
tipo de frase que YouTube clasifica como manipuladora.

---

## Nivel A — Evidencia sólida

### A1. Respiración lenta a 0,1 Hz

**Es el parámetro central del canal, y el mejor respaldado de todo el proyecto.**

La respiración pausada, en el rango de **4,5 a 6 respiraciones por minuto**, está asociada
en revisiones sistemáticas y metaanálisis a un aumento de la variabilidad de la frecuencia
cardíaca por refuerzo vagal. Los **0,1 Hz** —seis respiraciones por minuto— es el valor
más usado en los protocolos, porque coincide con el pico de actividad vagal y de
sensibilidad barorrefleja, y maximiza la resonancia barorrefleja.

**Cómo lo implementa el compositor:** la envolvente de amplitud recorre exactamente
**6,0 → 4,5 respiraciones por minuto** a lo largo de la obra, con inhalación al 40 % y
exhalación al 60 %. Las secciones y los cuencos caen en múltiplos enteros del ciclo.

**Lo que se puede decir:** que la obra está construida sobre ese ritmo y por qué se eligió.
**Lo que no:** que escuchar la obra produzca el efecto. El efecto documentado es de
**respirar** a ese ritmo, no de oír música construida sobre él. La obra **acompaña una
práctica**; no la sustituye. Por eso la frase del canal es *"para acompañar una práctica
de respiración"* — es literalmente exacta.

### A2. La música reduce el estrés (en general)

Un metaanálisis de **104 ensayos controlados aleatorizados con 9.617 participantes**
encontró que las intervenciones musicales reducen marcadores de estrés fisiológicos y
psicológicos.

**Importante:** el resultado es sobre **música**, no sobre frecuencias concretas. Respalda
la categoría entera, no ninguna afirmación particular de este canal.

### A3. Aspereza sensorial y banda crítica

Psicoacústica establecida desde **Plomp y Levelt (1965)**: cuando dos componentes
simultáneos difieren en menos que la banda crítica (del 10 al 20 % de la frecuencia
central), se produce modulación de amplitud que se percibe como batido o como **aspereza**,
y la aspereza se percibe como desagradable. El máximo de disonancia aparece en torno a un
cuarto de la banda crítica.

**Esto justifica directamente la entonación justa.** Con raíz en 528 Hz, la tercera del
temperamento igual coloca su 4.º armónico en 2661 Hz contra el 5.º de la raíz en 2640 Hz:
**21 Hz de diferencia**, justo en el umbral en que los batidos dejan de oírse como pulsos
y empiezan a oírse como aspereza — y muy dentro de la banda crítica a esa frecuencia
(unos 400 Hz). En entonación justa ambos caen en 2640 Hz exactos y la aspereza desaparece.

**Lo que se puede decir:** que la obra está afinada en entonación justa para evitar esa
aspereza. Es un hecho acústico verificable con un analizador de espectro.

### A4. Reflejo de sobresalto acústico

Neurofisiología de manual: un inicio sonoro **brusco** dispara el reflejo de sobresalto.
Es la razón de los **fundidos de 8 segundos** al principio y al final de cada obra, y de
la prohibición absoluta de picos de nivel dentro de la pieza.

En contenido de sueño esto no es un detalle estético: un corte seco al final despierta a
quien se durmió.

---

## Nivel B — Evidencia preliminar o mixta

### B1. Pulsos binaurales

**Lo favorable:** un metaanálisis de 2025 sobre **15 ensayos aleatorizados** en contexto
perioperatorio encontró reducción significativa de ansiedad, dolor postoperatorio, presión
sistólica y frecuencia cardíaca, superando a la música no binaural. Una revisión de
**9 ensayos** en odontología llegó a conclusiones similares. Los tamaños de efecto
reportados rondan **0,3-0,6**.

**Lo desfavorable:** una revisión de 2024 evaluó la calidad de la evidencia como
**muy baja a baja** según GRADE, con la mayoría de estudios en alto riesgo de sesgo. Hay
resultados nulos publicados.

**Conclusión honesta:** prometedor, no establecido.

**Cómo lo implementa el compositor:** **desactivado por defecto**, disponible con
`--binaural 4`. Portadora grave (264 Hz con raíz 528), nivel bajo, y sigue la envolvente
respiratoria para no sonar como una capa pegada encima.

**Requiere auriculares**, y eso limita su utilidad: buena parte de la audiencia de sueño
escucha por altavoz, donde el efecto binaural sencillamente no existe. Por eso es una
opción y no la base del canal.

**Lo que se puede decir:** "incluye un pulso binaural de 4 Hz; escuchar con auriculares".
**Lo que no:** que induzca ningún estado cerebral concreto.

---

## Nivel C — Sin evidencia creíble

### C1. Las frecuencias solfeggio y el 528 Hz

**No existe investigación revisada por pares que demuestre que el 528 Hz repare el ADN,
ni que los números del sistema solfeggio tengan efectos fisiológicos propios.**

La afirmación del ADN procede de un solo autor y **no tiene ningún trabajo experimental
que la respalde**. Y hay un argumento físico que la cierra: una onda de 528 Hz en el aire
mide unos **65 cm** de longitud de onda; una molécula de ADN mide unos **2 nanómetros**.
Son ocho órdenes de magnitud. No existe el mecanismo.

Lo único que suele citarse es un estudio piloto de **nueve personas** sobre cortisol y
oxitocina, sin réplica. Nueve personas no sostienen nada.

### C2. 432 Hz frente a 440 Hz

No hay evidencia convincente de que el 432 Hz tenga propiedades neurológicas o
terapéuticas distintas del 440 Hz ni de cualquier afinación cercana.

### Entonces, ¿por qué el canal las usa?

Por dos razones legítimas, y ninguna es terapéutica:

1. **Son una elección estética de afinación.** Una raíz en 528 Hz da un centro tonal
   concreto y coherente. Es una decisión de compositor, igual que elegir una tonalidad.
2. **Son el principal término de búsqueda del nicho.** "Música 528 Hz" tiene volumen alto
   y constante. El pilar Frecuencias existe por eso.

Usarlas como afinación y como palabra clave es correcto. Usarlas como promesa de curación
es falso, y además es exactamente lo que el comprador serio detecta y descarta.

---

## Resumen: qué respalda cada decisión

| Decisión de composición | Nivel | Qué la respalda |
|---|---|---|
| Ciclo respiratorio 6 → 4,5/min | **A** | Metaanálisis de respiración lenta y VFC |
| Exhalación más larga que inhalación | **A** | Patrón estándar de las prácticas de relajación |
| Entonación justa | **A** | Plomp y Levelt: aspereza dentro de la banda crítica |
| Fundidos de 8 s, sin picos | **A** | Reflejo de sobresalto acústico |
| Música lenta, predecible, sin sorpresas | **A** | Metaanálisis de 104 ECA sobre música y estrés |
| Pulso binaural opcional | **B** | 15 ECA favorables; calidad GRADE baja |
| Raíz en 528 / 432 Hz | **C** | Ninguna. Es afinación y palabra clave de búsqueda |

**Ese cuadro es el plus.** No "lo aprobó un neurólogo", sino: *esto es exactamente lo que
hace la obra, esto es lo que la respalda, y esto es lo que no puedo afirmar*. Es lo que
ningún canal del nicho publica, y es comprobable línea por línea.

---

## Fuentes

**Respiración lenta y VFC**
- [Effects of voluntary slow breathing on heart rate and heart rate variability: a systematic review and meta-analysis](https://www.sciencedirect.com/science/article/abs/pii/S0149763422002007)
- [Heart rate variability and slow-paced breathing: when coherence meets resonance](https://www.sciencedirect.com/science/article/abs/pii/S0149763422000653)
- [Pulmonary afferent activity during slow, deep breathing and the neural induction of relaxation](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6753868/)
- [Effects of slow breathing rate on HRV and baroreflex sensitivity](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6392805/)

**Psicoacústica de la consonancia**
- [Register impacts perceptual consonance through roughness and sharpness](https://pmc.ncbi.nlm.nih.gov/articles/PMC9166839/)
- [Differential processing of consonance and dissonance in the human superior temporal gyrus](https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2016.00154/full)
- [The pleasantness of sensory dissonance is mediated by musical style and expertise](https://www.nature.com/articles/s41598-018-35873-8)

**Pulsos binaurales**
- [Binaural beats for perioperative anxiety and pain: systematic review and meta-analysis (2025)](https://www.sciencedirect.com/science/article/pii/S096522992500175X)
- [Effectiveness of binaural beats in reducing dental pain and anxiety: systematic review and meta-analysis](https://pmc.ncbi.nlm.nih.gov/articles/PMC12451561/)
- [Is non-clinical, personal use of binaural beats an effective stress-management strategy? Systematic review of RCTs](https://www.tandfonline.com/doi/full/10.1080/18387357.2024.2374759)
- [Music and binaural beat interventions for young adults (Acta Neuropsychiatrica)](https://www.cambridge.org/core/journals/acta-neuropsychiatrica/article/music-and-binaural-beat-interventions-for-young-adults-a-systematic-review-of-effects-on-anxiety-sleep-and-cognition/4282E1152FD3EACA5DF8304935165202)

**Frecuencias solfeggio: las afirmaciones frente a la evidencia**
- [Solfeggio frequencies: the claims vs. the science](https://www.soundmedicineacademy.com/pages/sound-healing-blog/solfeggio-frequencies)
- [Do solfeggio frequencies work? 528 Hz and the honest evidence](https://www.voxsoma.com/blog/solfeggio-frequencies-528hz)
- [432 Hz, 528 Hz and "healing frequencies": what's real and what isn't](https://www.frequencysoundgenerator.com/blog/healing-frequencies-432hz-528hz)
