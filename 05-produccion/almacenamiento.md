# Almacenamiento de recursos — Drive

**Decisión: Google Drive.** Cloudinary queda descartado.

## Por qué Drive gana

1. **Yo puedo verlo.** El conector de Drive funciona en esta sesión: puedo listar la
   carpeta, comprobar que están las siete escenas con el nombre correcto y detectar
   lo que falte. **Cloudinary está bloqueado por la red de la sesión** — no puedo
   verificar nada allí. Para trabajar juntos sobre el mismo material, esto lo decide.
2. **Un sistema menos.** Ya usás Drive para el catálogo. Meter Cloudinary añade una
   cuenta, un secreto de API y otro sitio donde algo puede faltar.
3. **Make lee Drive de forma nativa**, igual que lee Sheets.
4. **Sin secretos circulando.** No hace falta un `api_secret` en ningún lado.

## La estructura

Una carpeta por obra, con el `id` del catálogo como nombre:

```
Rin/
  OBRA-001/
    escena-1.png … escena-7.png
    portada.png
    OBRA-001.mp4
    shorts/
      short-1.mp4 … short-5.mp4
  OBRA-002/
    ...
```

**Reglas:** el nombre de la carpeta es exactamente el `id` del Excel (`OBRA-001`),
minúsculas y guiones en los archivos, sin tildes ni espacios. Una obra por carpeta.

Con eso, Make localiza cualquier recurso buscando por nombre dentro de la carpeta de
la obra, sin que haya que apuntar rutas a mano en el catálogo.

## La única pega, y hay que probarla pronto

Drive **no es un CDN**. Para publicar, Make tiene que **descargar el archivo de Drive y
pasárselo a YouTube**, o sea el MP4 atraviesa Make. Con Cloudinary se podía entregar por
URL directa sin que el archivo pasara por dentro.

Para las imágenes y los shorts da igual: pesan poco. **El riesgo está en los videos largos.**

| Obra | MP4 aprox. |
|---|---|
| 8 min | ~25 MB |
| 60 min | ~155 MB |
| **180 min (pilar Sueño)** | **~445 MB** |

**No tengo un dato fiable del límite de transferencia de Make**, y no te lo voy a inventar:
en su comunidad hay hilos de gente peleando con archivos de varios cientos de MB, así que
es un punto real de fricción, no un problema resuelto.

**Qué hacer:** cuando montes el escenario, **probá primero con una obra del pilar Sueño**,
que es la más pesada. Si pasa, pasa todo. Si falla, hay dos salidas:

- **Bajar el bitrate del audio** de 320k a 192k AAC: el MP4 de 3 horas baja de ~445 MB a
  ~270 MB. YouTube reencoda igual, así que la pérdida audible es mínima.
- **Subir a mano las cuatro o cinco obras más largas** y automatizar el resto. Son 8 de 40.

## Espacio

Drive gratuito son **15 GB compartidos con Gmail y Google Photos** — si el correo está
lleno, contá con menos.

Las imágenes son irrelevantes (unos pocos MB por obra). **Los MP4 sí ocupan**, así que la
regla no cambia: **subir, publicar, borrar**.

No se pierde nada: el audio se regenera idéntico con la semilla del catálogo y el video se
vuelve a montar con las portadas, que sí se conservan.
