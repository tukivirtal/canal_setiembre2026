# Textos del canal

Todo listo para pegar en **YouTube Studio → Personalización**.

## Descripción del canal

Límite 1.000 caracteres. Los primeros ~150 son los que aparecen en la búsqueda y en la
vista previa del canal: por eso arrancan con lo que la gente busca.

```
Música para dormir, meditar, calmar la ansiedad y concentrarte. Obras largas de música de meditación con olas del mar, lluvia, selva tropical y templo zen.

Rin (鈴) es el nombre japonés del cuenco cantor. Cada obra se compone desde cero: nada de bibliotecas ni sonidos prestados. Entonación justa, un pulso que acompaña una respiración lenta y ambientes naturales sintetizados sonido por sonido.

Cada obra tiene su propio nombre y su propio ambiente, pensada para acompañar algo concreto: dormir, una pausa cuando la cabeza no para, una práctica de meditación o horas de trabajo y estudio.

No prometemos curar nada. Componemos música para acompañarte.

— English —
Sleep music, meditation music, relaxing music and focus music. Long original pieces with ocean waves, rain, rainforest and zen temple ambiences, composed from scratch in just intonation.

Suscríbete para recibir cada obra nueva.
```

## Palabras clave del canal

**Studio → Configuración → Canal → Palabras clave.** Límite 500 caracteres; las de
varias palabras van entre comillas.

```
"música para dormir" "música para meditar" "música relajante" "música de meditación" "música para la ansiedad" "música para concentrarse" "música para estudiar" "sonidos del mar" "sonido de lluvia" "música zen" "528 Hz" "432 Hz" "meditation music" "sleep music" "relaxing music" "focus music" "zen music" Rin
```

Las palabras clave del canal pesan poco para posicionar: posicionan los títulos y las
descripciones de cada obra, que ya vienen escritos en el catálogo. Estas ayudan a que
YouTube entienda de qué va el canal cuando todavía no tiene videos.

## Imágenes

Generadas con `python3 09-canal/render_identidad.py` en `09-canal/export/`:

| Archivo | Dónde va | Medida |
|---|---|---|
| `banner-2560x1440.png` | Personalización → Marca → Imagen del banner | 2560×1440. Nombre y lema dentro de la zona segura de 1546×423, que es lo único que se ve en el celular |
| `perfil-800x800.png` | Personalización → Marca → Imagen | 800×800. YouTube la muestra en círculo; se lee hasta en 48 px |
| `marca-agua-150x150.png` | Personalización → Marca → Marca de agua del video | 150×150, fondo transparente |

`vista-dispositivos.png` muestra cómo recorta YouTube el banner en TV, escritorio y móvil.

## La marca de agua: sí, conviene

No es decoración. **Es un botón de suscripción que aparece sobre todos los videos**: quien
pasa el mouse o toca la marca, se suscribe sin salir del video. En este canal los
suscriptores son el cuello de botella (el oyente pone la obra y apaga la pantalla), así
que cualquier atajo para suscribirse cuenta.

Configurarla con **"Hora de visualización: Todo el video"**. Aparece abajo a la derecha;
el mandala lleva la firma "Rin" abajo a la izquierda, así que no se pisan.
