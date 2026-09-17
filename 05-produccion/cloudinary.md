# Cloudinary — convención de nombres

## Qué no puedo hacer, y por qué

**No puedo subir las imágenes a Cloudinary desde aquí.** Dos motivos:

1. **La red de esta sesión bloquea Cloudinary** — `api.cloudinary.com`, `res.cloudinary.com`
   y la consola, igual que bloqueó Wikimedia. Comprobado.
2. Subir por API necesita `cloud_name`, `api_key` y `api_secret`. **El secreto no debe
   pegarse en un chat**, y tampoco hace falta: las imágenes las genera Leonardo en tu
   cuenta y salen de ahí.

Así que **las subís vos**. Lo que aporto es la convención de nombres, que es lo que hace
que Make encuentre cada archivo sin buscarlo.

## La estructura

```
rin/
  obras/
    OBRA-001/
      escena-1 … escena-7      las siete imágenes
      portada                  la miniatura de YouTube
      video                    el MP4 final
  shorts/
    OBRA-001/
      short-1 … short-5
```

El `public_id` de cada recurso es la ruta completa sin extensión:

```
rin/obras/OBRA-001/escena-3
rin/obras/OBRA-001/portada
rin/shorts/OBRA-001/short-2
```

## Por qué importa: la URL se calcula, no se busca

Con esta convención, la URL de cualquier recurso sale de la columna `id` del catálogo:

```
https://res.cloudinary.com/<cloud_name>/image/upload/rin/obras/{id}/portada.png
https://res.cloudinary.com/<cloud_name>/video/upload/rin/obras/{id}/video.mp4
```

Eso **elimina un módulo entero del escenario de Make**: no hace falta consultar Cloudinary
para obtener la URL, se construye con la fórmula a partir del `id`. Menos operaciones, menos
puntos de fallo, y funciona igual para las 40 obras.

Reglas:

- **Minúsculas y guiones**, nunca espacios ni tildes en el `public_id`.
- **El `id` del catálogo manda.** `OBRA-001` en el Excel es `OBRA-001` en Cloudinary.
- **Una carpeta por obra.** Mezclar obras en una carpeta rompe la fórmula.

## Ciclo de vida del MP4

El video se sube a Cloudinary solo para que Make lo tome por URL y lo publique.
**En cuanto YouTube confirma, se borra de Cloudinary.**

El almacenamiento se cobra aunque el archivo no se use, y el catálogo completo en WAV son
34 GB frente a los 15 GB del plan gratuito. Las imágenes sí se conservan: pesan poco y
sirven para los shorts.

No se pierde nada: el video se rehace desde la semilla y las portadas.
