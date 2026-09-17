#!/usr/bin/env python3
"""
Renderizado por lotes del catálogo.

Lee 08-catalogo/catalogo.csv y compone las obras que falten, una detrás de otra.
Pensado para dejarlo corriendo de noche o en un Codespace: componer una hora de
audio cuesta unos 28 minutos de CPU, así que un lote de tres obras largas es
una madrugada entera.

    python3 lote.py --listar              # qué falta por componer
    python3 lote.py --n 3                 # las 3 primeras que falten
    python3 lote.py --id OBRA-001         # una concreta
    python3 lote.py --pilar Frecuencias   # un pilar entero

Salta lo que ya existe en audio/, así que se puede interrumpir y relanzar sin
perder trabajo. Sin dependencias: solo Python 3.
"""

import argparse
import csv
import os
import subprocess
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(RAIZ, "08-catalogo", "catalogo.csv")
COMPOSITOR = os.path.join(RAIZ, "03-composicion", "compositor.py")
DIR_AUDIO = os.path.join(RAIZ, "audio")

# Medido en este proyecto: ~28 min de CPU por hora de audio.
MIN_CPU_POR_MIN_AUDIO = 28 / 60


def cargar():
    with open(CSV, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ruta_salida(fila):
    return os.path.join(DIR_AUDIO, f'{fila["id"]}_{fila["raiz_hz"]}_{fila["modo"]}.wav')


def pendientes(filas, args):
    fuera = []
    for fila in filas:
        if args.id and fila["id"] != args.id:
            continue
        if args.pilar and fila["tema"].lower() != args.pilar.lower():
            continue
        if os.path.exists(ruta_salida(fila)) and not args.rehacer:
            continue
        fuera.append(fila)
    return fuera


def formato(minutos):
    h, m = divmod(int(minutos), 60)
    return f"{h}h {m:02d}m" if h else f"{m}m"


def main():
    p = argparse.ArgumentParser(description="Renderizado por lotes del catálogo")
    p.add_argument("--n", type=int, default=0, help="cuántas obras componer (0 = todas)")
    p.add_argument("--id", help="una obra concreta, p. ej. OBRA-001")
    p.add_argument("--pilar", help="Frecuencias, Sueño, Respiración, Cuencos o Foco")
    p.add_argument("--rehacer", action="store_true",
                   help="recomponer aunque el archivo ya exista")
    p.add_argument("--listar", action="store_true")
    args = p.parse_args()

    filas = cargar()
    cola = pendientes(filas, args)
    if args.n:
        cola = cola[: args.n]

    if not cola:
        print("No queda nada por componer.")
        return

    total_audio = sum(int(f["duracion_min"]) for f in cola)
    estimado = total_audio * MIN_CPU_POR_MIN_AUDIO

    print(f"{len(cola)} obras · {formato(total_audio)} de audio")
    print(f"cómputo estimado: {formato(estimado)}\n")
    for f in cola:
        print(f'  {f["id"]}  {f["duracion_min"]:>3} min  {f["raiz_hz"]:>3} Hz  '
              f'{f["modo"]:<10} {f["titulo"][:52]}')

    if args.listar:
        return

    os.makedirs(DIR_AUDIO, exist_ok=True)
    print()
    inicio_lote = time.time()
    hechas, fallidas = 0, []

    for i, fila in enumerate(cola, 1):
        salida = ruta_salida(fila)
        print(f'[{i}/{len(cola)}] {fila["id"]} · {fila["duracion_min"]} min · '
              f'{fila["raiz_hz"]} Hz {fila["modo"]}', flush=True)
        t0 = time.time()
        cmd = [sys.executable, COMPOSITOR,
               "--minutos", fila["duracion_min"],
               "--raiz", fila["raiz_hz"],
               "--modo", fila["modo"],
               "--semilla", fila["semilla"],
               "--salida", salida]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"    ERROR: {r.stderr.strip().splitlines()[-1] if r.stderr else 'sin detalle'}")
            fallidas.append(fila["id"])
            continue
        tam = os.path.getsize(salida) / 2 ** 20
        print(f"    {os.path.basename(salida)} · {tam:.0f} MiB · "
              f"{formato((time.time() - t0) / 60)}", flush=True)
        hechas += 1

    print(f"\n{hechas} compuestas en {formato((time.time() - inicio_lote) / 60)}")
    if fallidas:
        print(f"fallaron: {', '.join(fallidas)}")
        sys.exit(1)
    print(f"\nLos WAV están en audio/ y NO se versionan (ver .gitignore).")
    print("Si se pierden, se regeneran idénticos con la semilla del catálogo.")


if __name__ == "__main__":
    main()
