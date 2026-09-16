# Lote de prueba — 6 videos

Decisión tomada: antes de invertir 15 días de producción, se producen **6 videos** para
medir CTR y retención reales. El lote no es una muestra al azar: **cada video prueba una
hipótesis distinta**, para saber qué funciona antes de escalar.

## Los 6 videos y qué prueba cada uno

| # | Video | Pilar | Hipótesis que pone a prueba |
|---|---|---|---|
| 1 | Qué comía un soldado romano todos los días | `[CASA]` | El formato base: ¿la curiosidad cotidiana sola sostiene un video? |
| 2 | Cómo se bañaba la gente en la Edad Media | `[CASA]` | El *mito desmentido*: ¿el hook de "no es lo que te contaron" sube el CTR? |
| 3 | Cuánto costaba vivir en 1650 | `[$]` | El ángulo dinero: ¿la audiencia de precios y salarios aparece y retiene? |
| 4 | Qué comía la gente en tiempos de Jesús | `[FE]` | El pilar religioso: ¿llega el público 55+ y se queda? |
| 5 | Qué se hacía sin anestesia | `[CUE]` | Curiosidad incómoda: ¿retiene más, y con qué costo de monetización? |
| 6 | Un día completo en la vida de una mujer egipcia | `[CASA]` | El formato largo narrativo "un día en la vida" frente al formato pregunta-respuesta |

Publicación: **2 por semana durante 3 semanas**, alternando pilares para no darle al
algoritmo una señal temática falsa.

## Qué se mide y cuándo

Medición a los **14 días** de publicado cada video (no antes: la cola de impresiones
distorsiona las primeras 48 h).

| Métrica | Malo | Aceptable | Bueno |
|---|---|---|---|
| CTR de impresiones | < 3 % | 4-5 % | > 6 % |
| Retención media | < 35 % | 40-50 % | > 55 % |
| Retención a 30 s | < 60 % | 70 % | > 80 % |
| Duración media vista | < 3 min | 4-5 min | > 6 min |
| Suscriptores por 1.000 vistas | < 2 | 3-5 | > 6 |

## Cómo se lee el resultado

- **CTR bajo + retención alta** → el contenido sirve, fallan título y miniatura. Se
  corrige en el paso 3, no se cambia de nicho.
- **CTR alto + retención baja** → la miniatura promete algo que el video no da. Problema
  de guion: el hook no se paga en los primeros 30 segundos.
- **Los dos bajos en un solo pilar** → ese pilar se reduce de peso, no se elimina.
- **Los dos bajos en los 6** → el problema es de ejecución (locución, ritmo, imagen),
  no de nicho. Un nicho no se descarta con 6 videos.
- **Video 5 con buena retención pero anuncios limitados** → el pilar `[CUE]` se conserva
  por retención, pero se mantiene bajo el 10 % del catálogo.

## Regla de decisión

Si **al menos 2 de los 6** llegan a la columna "Bueno" en CTR o retención, se escala:
se pasa al buffer de producción con el pilar ganador sobreponderado.
Si ninguno llega, se rehace el lote corrigiendo ejecución antes de tocar el nicho.

## Lo que hay que tener listo antes de grabar

Se define en los pasos 3 y 5, pero se adelanta acá porque condiciona el lote:

- Identidad visual única (mismo tratamiento de color, tipografía y plantilla de miniatura).
- Voz elegida y fija: la voz es el rostro del canal.
- Una fuente citada por video.
- Cada guion escrito con estructura propia — no la misma plantilla seis veces.
