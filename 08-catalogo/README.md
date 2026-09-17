# Control de catálogo y flujo de trabajo

## Los archivos

| Archivo | Para qué |
|---|---|
| [`catalogo_canal.xlsx`](catalogo_canal.xlsx) | **Para trabajar a mano.** Estado, URLs, miniaturas y métricas |
| `catalogo.csv` | **Para las máquinas.** Lo lee `lote.py` para componer. Sin dependencias |
| [`generar_catalogo.py`](generar_catalogo.py) | Genera los dos desde el catálogo en markdown |

**La fuente de verdad es el markdown** de [`01-nicho/nicho-e-identidad.md`](../01-nicho/nicho-e-identidad.md).
Si se añade una obra allí, se regeneran CSV y Excel y todo queda sincronizado:

```bash
python3 08-catalogo/generar_catalogo.py --csv    # solo el CSV, NO toca el Excel
python3 08-catalogo/generar_catalogo.py          # ambos
```

> **Cuidado:** regenerar el Excel lo sobrescribe y se pierde lo rellenado a mano.
> Para el uso diario, `--csv`.

## El Excel

Tres hojas: **Catálogo** (40 obras × 19 columnas), **Resumen** (recuentos por estado y
pilar) y **Leyenda**.

Las **celdas amarillas son las únicas que se rellenan a mano**: `imagen_miniatura`,
`url_video`, `estado`, `fecha_publicacion`, `vistas` y `suscriptores`. Todo lo demás
viene generado o calculado.

Ya vienen escritos, obra por obra: el título con la fórmula de búsqueda, la descripción
bilingüe completa lista para pegar, el texto de miniatura, hashtags, etiquetas, los
parámetros de composición y **el comando exacto que regenera esa obra**.

`subs_por_1000` se calcula sola. Es la métrica que decide el canal: por debajo de 1, el
problema es la portada, no la música.

## Componer por lotes

```bash
python3 03-composicion/lote.py --listar              # qué falta
python3 03-composicion/lote.py --n 3                 # las 3 siguientes
python3 03-composicion/lote.py --pilar Frecuencias   # un pilar entero
```

Salta lo que ya existe, así que se puede interrumpir y relanzar sin perder trabajo.

### Lo que cuesta, en números

Medido en este proyecto: **28 minutos de CPU por hora de audio**, en un solo núcleo.

| Pilar | Obras | Audio | Cómputo |
|---|---|---|---|
| Frecuencias | 8 | 9,3 h | **4,3 h** |
| Sueño | 8 | 18,5 h | 8,6 h |
| Respiración | 8 | 2,8 h | 1,3 h |
| Cuencos | 8 | 6,1 h | 2,8 h |
| Foco | 8 | 17,0 h | 7,9 h |
| **Total** | **40** | **53,7 h** | **25,0 h** |

---

## ¿Conviene usar Codespaces?

**Sí, y por tres razones concretas.** Pero con dos trampas que hay que conocer antes.

### A favor

1. **`ffmpeg` viene instalado.** Lo necesitás para montar el video y para convertir los
   WAV, y en muchos equipos no está. En Codespaces está de serie.
2. **El lote corre sin tu máquina encendida.** Cuatro horas de cómputo para el pilar
   Frecuencias no bloquean tu portátil.
3. **Cero instalación.** El compositor es Python puro sin dependencias y el repo ya está
   en GitHub. Abrís el Codespace y funciona.

### Las dos trampas

**1 · El tiempo de inactividad mata el lote.** Por defecto un Codespace se detiene tras
**30 minutos de inactividad**, y un lote de cuatro horas no sobrevive a eso: no basta con
lanzarlo y cerrar la pestaña. Hay que **subir el tiempo de inactividad en los ajustes**
antes de lanzar nada largo, o el trabajo se pierde a media noche.

**2 · El almacenamiento se llena mucho antes que las horas.** La cuenta gratuita trae
**120 core-hours y 15 GB** al mes. Con esos números:

| Recurso | El catálogo completo | Cuota gratuita | ¿Entra? |
|---|---|---|---|
| Cómputo | 25 h en 1 núcleo ≈ **50 core-hours** en una máquina de 2 | 120 core-hours | **Sí, de sobra** |
| Almacenamiento en WAV | **34 GB** | 15 GB | **No, ni de lejos** |

El cómputo sobra; **el disco no llega**. Y el almacenamiento se consume aunque el
Codespace esté apagado.

**La consecuencia práctica, que es la regla de oro del flujo:**

> **Renderizar → montar el video → subir → borrar el WAV.** Nunca acumular audio.

No se pierde nada, porque **la semilla regenera cualquier obra idéntica**. El WAV es un
archivo temporal; el catálogo es el activo. Por eso `audio/`, `video/` y `portadas/`
están en `.gitignore`: **jamás se versionan**.

Un pilar por sesión entra sin problema: Frecuencias son 9,3 h de audio ≈ 5,9 GB, que
caben en los 15 GB con margen para el sistema.

### Flujo recomendado en Codespaces

```bash
# 1. Subir el tiempo de inactividad en los ajustes del Codespace, ANTES de nada
# 2. Componer un pilar
python3 03-composicion/lote.py --pilar Frecuencias

# 3. Montar cada video (ffmpeg ya está)
ffmpeg -loop 1 -i portadas/obra-001.png -i audio/OBRA-001_528_hirajoshi.wav \
  -c:v libx264 -tune stillimage -pix_fmt yuv420p -r 1 \
  -c:a aac -b:a 320k -shortest video/obra-001.mp4

# 4. Descargar el mp4, subirlo a YouTube, y borrar el WAV
rm audio/OBRA-001_528_hirajoshi.wav
```

Para distribución a streaming hace falta el WAV sin convertir: descargalo **antes** de
borrarlo, o regeneralo con la semilla cuando toque.

### Alternativa

Si el disco se vuelve un estorbo, cualquier máquina propia encendida de noche hace el
mismo trabajo sin cuota. Codespaces gana en comodidad y en tener `ffmpeg` listo; no en
capacidad.
