# Fondo mandala — caleidoscopio en movimiento

Pedido tras ver los fondos de Meditative Mind: mandalas densos que giran despacio.

- [`mandala.html`](mandala.html) — el diseño, dibujado por código
- [`render_mandala.py`](render_mandala.py) — lo lleva a un video de 48 s que empalma consigo mismo

```bash
python3 05-produccion/fondo-mandala/render_mandala.py          # 1920x1080, 24 fps
ffmpeg -stream_loop -1 -i mandala_bucle.mp4 -i obra_final.wav \
  -c:v copy -c:a aac -b:a 320k -shortest video.mp4
```

## Cómo está hecho

Dieciséis anillos concéntricos de motivos (pétalos, burbujas doradas, festones, hojas)
que llenan la pantalla hasta las esquinas, en turquesa y oro sobre azul noche. Cada anillo
gira **exactamente un paso de su motivo por bucle**, y los vecinos giran al revés: eso da
el efecto hipnótico sin que nada se mueva rápido. Todo "respira" cuatro veces por bucle,
el mismo pulso de la música.

48 s = cuatro respiraciones a 5 por minuto, el mismo bucle que el campo de motas. Como
todo lo que se mueve es periódico en 48 s, el último fotograma empalma con el primero y
el video se repite con `-stream_loop` sin recodificar: una obra de 3 horas se monta en
segundos.

## Por qué no Leonardo ni IA de video

Es geometría calculada: **tuya sin matices**, sin créditos y sin clips de pocos segundos.

## Cuánto tarda

~0,9 s por fotograma en este contenedor: el bucle de 1.152 fotogramas son unos 20-30
minutos, **una sola vez**. Después se reutiliza para todas las obras que lleven este fondo.
