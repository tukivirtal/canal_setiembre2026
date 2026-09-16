# Archivo de imagen histórica

Sistema para construir el banco de imágenes del canal, con la licencia y el crédito
resueltos desde el principio.

> **Por qué esto no se descargó acá:** la sesión donde se armó este repo tiene bloqueado
> por política de red el acceso a Wikimedia, el Rijksmuseum, el Met y Pexels. En lugar de
> pegar una lista de enlaces escritos de memoria —que se rompen y no se pueden verificar—
> queda el script, que trae los archivos reales y comprueba la licencia de cada uno.

## Uso

```bash
cd 05-archivo
python3 descargar_archivo.py --listar        # ver los temas disponibles
python3 descargar_archivo.py                 # descargar todo
python3 descargar_archivo.py roma/comida     # descargar un solo tema
```

Sin dependencias: solo Python 3.

## Qué hace

1. Consulta la API de Wikimedia Commons con los términos curados en `TEMAS`.
2. **Descarta todo lo que no sea reutilizable comercialmente**: rechaza CC BY-NC, CC BY-ND,
   *fair use* y cualquier licencia que no reconozca.
3. Pide cada imagen reescalada a 2000 px — de sobra para 1080p, y evita bajar originales
   de museo de 40 MB.
4. Guarda en `imagenes/<tema>/` y escribe `catalogo.csv`.

## El catálogo

Una fila por imagen, con `titulo`, `autor`, `licencia`, `pagina` y una columna **`credito`**
ya formateada para pegar en la descripción del video.

Esto no es burocracia: las licencias CC BY y CC BY-SA **exigen atribución**. Sin el crédito,
el uso es una infracción. Con el catálogo, la descripción se arma copiando una columna.

## Organización

```
imagenes/
  roma/comida/          roma/ejercito/       roma/vindolanda/
  medieval/higiene/     moderna/mercado/     siglo1/galilea/
  medicina/cirugia/     egipto/cotidiano/
  general/mapas/        general/manuscritos/
```

Los temas `general/` sirven en casi cualquier video: se descargan una vez y se reutilizan
siempre. Ahí está el ahorro real de tiempo.

## Cómo crece

Cada video nuevo agrega su tema al diccionario `TEMAS` del script, con 4-6 búsquedas.
Los términos van **en inglés**: es donde Commons tiene mejor indexado su material,
aunque el canal sea en español.

Para el video 10, la mitad del material de cualquier tema nuevo ya está descargado.

## Reglas de uso de la imagen

1. **Dominio público y CC BY/BY-SA solamente.** El script ya lo filtra.
2. **Crédito en la descripción** para todo lo que sea CC.
3. **La imagen generada con IA no entra en el cuerpo del video** como evidencia:
   ni objetos, ni documentos, ni hallazgos. Un objeto real de museo siempre gana.
   En la miniatura sí — la miniatura es empaque, no evidencia.
4. **Nada de capturas de documentales ajenos.** Es la vía más rápida a un reclamo.

## Otras fuentes (búsqueda manual)

Cuando Commons no alcance:

| Fuente | Qué tiene |
|---|---|
| Rijksmuseum | Pintura y grabado en altísima resolución, uso libre |
| The Met, Open Access | Objetos de museo fotografiados, CC0 |
| Getty Open Content | Fotografía de obra y objeto |
| British Library en Flickr Commons | Ilustración de libro antiguo |
| Biblioteca Digital Hispánica | Manuscritos y material en español |
| Internet Archive / Europeana | Libros antiguos, láminas, mapas |
| Pexels / Pixabay | Video de stock para texturas y ambiente |
