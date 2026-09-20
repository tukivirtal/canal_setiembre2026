#!/usr/bin/env python3
"""
Valida escenas.json y muestra el prompt final que recibirá Leonardo.

El prompt completo NO está escrito entero en el JSON: se arma como
"extreme close-up photograph of {sujeto}, {base.estilo}". Así el estilo del
canal vive en un solo sitio y cambiarlo cambia las siete escenas a la vez.

Make hace exactamente la misma concatenación en el módulo de Leonardo.

    python3 armar_prompt.py              # valida y lista todo
    python3 armar_prompt.py koro         # el prompt completo de una escena
"""

import json
import os
import sys

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "escenas.json")
PREFIJO = "extreme close-up photograph of "


def armar(base, escena):
    return PREFIJO + escena["sujeto"] + ", " + base["estilo"]


def main():
    with open(RUTA, encoding="utf-8") as f:
        d = json.load(f)

    base, escenas = d["base"], d["escenas"]

    # --- Validación ---
    fallos = []
    ids = [e["id"] for e in escenas]
    if len(ids) != len(set(ids)):
        fallos.append("hay ids repetidos")
    for e in escenas:
        for campo in ("id", "nombre", "pilares", "sujeto", "movimiento"):
            if not e.get(campo):
                fallos.append(f'{e.get("id", "?")}: falta {campo}')
        # El prompt no puede superar el límite práctico de Leonardo.
        n = len(armar(base, e))
        if n > 1500:
            fallos.append(f'{e["id"]}: prompt de {n} caracteres, demasiado largo')
    if fallos:
        print("FALLOS:")
        for f_ in fallos:
            print("  ·", f_)
        sys.exit(1)

    pedido = sys.argv[1] if len(sys.argv) > 1 else None
    if pedido:
        e = next((x for x in escenas if x["id"] == pedido), None)
        if not e:
            print(f'No existe "{pedido}". Hay: {", ".join(ids)}')
            sys.exit(1)
        print(f'--- {e["nombre"]} ---\n')
        print("PROMPT:\n" + armar(base, e) + "\n")
        print("NEGATIVE:\n" + base["negative_prompt"] + "\n")
        print(f'MOVIMIENTO: {e["movimiento"]}')
        if e.get("riesgo"):
            print(f'\nRIESGO: {e["riesgo"]}')
        return

    print(f'{len(escenas)} escenas · modelo {base["modelNombre"]} · '
          f'{base["width"]}x{base["height"]} · alchemy {base["alchemy"]}\n')
    for e in escenas:
        n = len(armar(base, e))
        marca = "⚠" if e.get("riesgo") else " "
        print(f'  {marca} {e["id"]:14} {n:5} car.  {"/".join(e["pilares"])}')
    print(f'\nnegative: {len(base["negative_prompt"])} caracteres')
    print("\nTodo válido. `armar_prompt.py <id>` para ver un prompt completo.")


if __name__ == "__main__":
    main()
