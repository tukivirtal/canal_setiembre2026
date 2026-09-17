#!/usr/bin/env python3
"""
Extrae shorts verticales de una obra ya compuesta.

No corta al azar: pregunta al compositor **en qué segundo cae cada cuenco** y
empieza el recorte justo antes de uno. Así el short arranca con un golpe en vez
de con un fundido, que es lo único que retiene en TikTok y Reels: el primer
segundo tiene que sonar a algo.

    python3 extraer_shorts.py audio/OBRA-001.wav --raiz 528 --modo hirajoshi \\
        --semilla 454078 --minutos 60 --n 5

Genera los WAV recortados y escribe el comando de ffmpeg para el video vertical.
Sin dependencias: solo Python 3.
"""

import argparse
import array
import math
import os
import wave

from compositor import planificar

SR = 44100


def cargar(ruta):
    with wave.open(ruta) as w:
        if w.getframerate() != SR or w.getnchannels() != 2:
            raise SystemExit(f"Se esperaba estéreo a {SR} Hz")
        d = array.array("h")
        d.frombytes(w.readframes(w.getnframes()))
        return d


def elegir_cuencos(eventos, segundos, n, margen=6.0):
    """
    Reparte n cuencos a lo largo de la obra, evitando el principio y el final.

    Se reparten en vez de tomar los n primeros: cinco shorts del primer minuto
    sonarían todos igual, que es justo lo que no se quiere.
    """
    validos = [e for e in eventos if margen < e[0] < segundos - margen - 50]
    if not validos:
        raise SystemExit("La obra es demasiado corta para extraer shorts")
    if len(validos) <= n:
        return validos
    paso = (len(validos) - 1) / (n - 1) if n > 1 else 0
    return [validos[round(i * paso)] for i in range(n)]


def recortar(datos, inicio_s, dur_s, ruta):
    i0 = int(inicio_s * SR) * 2
    n = int(dur_s * SR)
    trozo = array.array("h", datos[i0:i0 + n * 2])
    if len(trozo) < n * 2:
        n = len(trozo) // 2

    # Entrada corta para no perder el golpe; salida larga para no cortar en seco.
    f_in, f_out = int(0.8 * SR), int(3.5 * SR)
    for i in range(min(f_in, n)):
        g = i / f_in
        trozo[i * 2] = int(trozo[i * 2] * g)
        trozo[i * 2 + 1] = int(trozo[i * 2 + 1] * g)
    for i in range(min(f_out, n)):
        g = i / f_out
        j = (n - 1 - i) * 2
        trozo[j] = int(trozo[j] * g)
        trozo[j + 1] = int(trozo[j + 1] * g)

    with wave.open(ruta, "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(trozo.tobytes())
    return n / SR


def main():
    p = argparse.ArgumentParser(description="Extrae shorts verticales de una obra")
    p.add_argument("wav", help="la obra ya compuesta")
    p.add_argument("--raiz", type=float, required=True)
    p.add_argument("--modo", required=True)
    p.add_argument("--semilla", type=int, required=True)
    p.add_argument("--minutos", type=float, required=True)
    p.add_argument("--n", type=int, default=5, help="cuántos shorts")
    p.add_argument("--duracion", type=float, default=45.0, help="segundos por short")
    p.add_argument("--resp", default="6,4.5")
    p.add_argument("--dir", default="shorts")
    args = p.parse_args()

    segundos = args.minutos * 60
    resp = tuple(float(x) for x in args.resp.split(","))
    # Misma semilla y mismos parámetros -> mismos instantes de cuenco que en la obra.
    _, eventos, _ = planificar(segundos, args.modo, args.semilla, args.raiz, resp)

    datos = cargar(args.wav)
    dur_real = len(datos) / 2 / SR
    print(f"{os.path.basename(args.wav)} · {dur_real/60:.1f} min · "
          f"{len(eventos)} cuencos en la obra")

    elegidos = elegir_cuencos(eventos, segundos, args.n)
    os.makedirs(args.dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(args.wav))[0]

    print(f"\n{len(elegidos)} shorts de {args.duracion:g} s:\n")
    for i, (t, frec, vol, pan) in enumerate(elegidos, 1):
        # Arrancar 1,2 s antes del golpe: se oye el ataque, no el silencio previo.
        inicio = max(0.0, t - 1.2)
        ruta = os.path.join(args.dir, f"{base}_short{i}.wav")
        real = recortar(datos, inicio, args.duracion, ruta)
        print(f"  {i}  desde {inicio/60:5.2f}'  cuenco de {frec:6.1f} Hz  "
              f"{real:.0f} s  ->  {ruta}")

    print(f"""
Video vertical (9:16). El fondo de las escenas es negro, así que basta
rellenar los lados: el relleno es invisible y no hace falta generar imágenes
verticales aparte.

  ffmpeg -loop 1 -i portadas/escena1.png -i {args.dir}/{base}_short1.wav \\
    -vf "scale=1080:-1,pad=1080:1920:0:(1920-ih)/2:black" \\
    -c:v libx264 -tune stillimage -pix_fmt yuv420p -r 1 \\
    -c:a aac -b:a 256k -shortest {args.dir}/{base}_short1.mp4

Un short por escena distinta: cinco shorts con la misma imagen son cinco
variantes de una plantilla, que es justo lo que penaliza la política.
""")


if __name__ == "__main__":
    main()
