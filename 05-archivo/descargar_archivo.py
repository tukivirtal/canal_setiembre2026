#!/usr/bin/env python3
"""
Descarga imágenes de dominio público desde Wikimedia Commons y arma el catálogo
de atribución del canal.

Uso:
    python3 descargar_archivo.py                 # descarga todo lo definido en TEMAS
    python3 descargar_archivo.py roma/comida     # solo una carpeta
    python3 descargar_archivo.py --listar        # muestra los temas sin descargar

Salidas:
    imagenes/<tema>/*.jpg    los archivos
    catalogo.csv             una fila por imagen, con licencia y crédito listo para pegar
"""

import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"
# Wikimedia exige un User-Agent identificable o responde 403.
UA = "AsiSeVivia-ArchiveBot/1.0 (canal de divulgación histórica; contacto en el repo)"

RAIZ = os.path.dirname(os.path.abspath(__file__))
DIR_IMG = os.path.join(RAIZ, "imagenes")
CATALOGO = os.path.join(RAIZ, "catalogo.csv")

# Ancho al que se pide cada imagen. 2000 px sobra para 1080p y evita
# descargar originales de museo de 40 MB.
ANCHO = 2000
POR_TEMA = 12

# Licencias aceptadas. Se rechaza cualquier cosa que no encaje acá.
LICENCIAS_OK = ("public domain", "pd-", "cc0", "cc by", "cc-by", "cc pd")
LICENCIAS_NO = ("nc", "nd", "fair use", "non-free")


def buscar(termino, limite=POR_TEMA):
    """Consulta la API de Commons y devuelve la lista de imageinfo."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": termino,
        "gsrnamespace": "6",           # 6 = File:
        "gsrlimit": str(limite),
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|size|mime",
        "iiurlwidth": str(ANCHO),
        "format": "json",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def licencia_valida(licencia):
    """True solo si la licencia permite uso comercial sin restricción."""
    txt = (licencia or "").lower()
    if any(mal in txt for mal in LICENCIAS_NO):
        return False
    return any(ok in txt for ok in LICENCIAS_OK)


def limpiar(html):
    """Los campos de extmetadata vienen con HTML. Se deja texto plano."""
    if not html:
        return ""
    fuera, dentro = [], False
    for c in html:
        if c == "<":
            dentro = True
        elif c == ">":
            dentro = False
        elif not dentro:
            fuera.append(c)
    return " ".join("".join(fuera).split())


def extraer(respuesta):
    """Convierte la respuesta de la API en filas normalizadas y filtradas."""
    filas = []
    paginas = respuesta.get("query", {}).get("pages", {})
    for pagina in paginas.values():
        info = (pagina.get("imageinfo") or [{}])[0]
        if not info.get("url"):
            continue
        if not str(info.get("mime", "")).startswith("image/"):
            continue
        meta = info.get("extmetadata", {})
        licencia = limpiar(meta.get("LicenseShortName", {}).get("value"))
        if not licencia_valida(licencia):
            continue
        filas.append({
            "titulo": pagina.get("title", "").replace("File:", ""),
            "autor": limpiar(meta.get("Artist", {}).get("value")) or "desconocido",
            "fecha": limpiar(meta.get("DateTimeOriginal", {}).get("value")),
            "licencia": licencia,
            # thumburl es la versión reescalada; si no existe, el original
            "descarga": info.get("thumburl") or info["url"],
            "pagina": info.get("descriptionurl", ""),
        })
    return filas


def nombre_archivo(titulo):
    base = "".join(c if c.isalnum() or c in "-_." else "_" for c in titulo)
    if not base.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff")):
        base += ".jpg"
    return base[:120]


def descargar(fila, destino):
    ruta = os.path.join(destino, nombre_archivo(fila["titulo"]))
    if os.path.exists(ruta):
        return ruta, True
    req = urllib.request.Request(fila["descarga"], headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r, open(ruta, "wb") as f:
        f.write(r.read())
    return ruta, False


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--listar" in sys.argv:
        for tema, terminos in TEMAS.items():
            print(f"{tema:28} {len(terminos)} búsquedas")
        return

    temas = {k: v for k, v in TEMAS.items() if not args or k in args}
    if not temas:
        print(f"Tema no encontrado. Disponibles: {', '.join(TEMAS)}")
        sys.exit(1)

    os.makedirs(DIR_IMG, exist_ok=True)
    catalogo, total, saltados = [], 0, 0

    for tema, terminos in temas.items():
        destino = os.path.join(DIR_IMG, tema)
        os.makedirs(destino, exist_ok=True)
        print(f"\n=== {tema} ===")
        for termino in terminos:
            try:
                filas = extraer(buscar(termino))
            except Exception as e:
                print(f"  ! '{termino}': {e}")
                continue
            print(f"  {termino}: {len(filas)} con licencia válida")
            for fila in filas:
                try:
                    ruta, ya_estaba = descargar(fila, destino)
                except Exception as e:
                    print(f"    ! {fila['titulo'][:50]}: {e}")
                    continue
                if ya_estaba:
                    saltados += 1
                else:
                    total += 1
                catalogo.append({
                    "tema": tema,
                    "busqueda": termino,
                    "archivo": os.path.relpath(ruta, RAIZ),
                    "titulo": fila["titulo"],
                    "autor": fila["autor"],
                    "fecha": fila["fecha"],
                    "licencia": fila["licencia"],
                    "pagina": fila["pagina"],
                    "credito": f'{fila["titulo"]} — {fila["autor"]} ({fila["licencia"]}), Wikimedia Commons',
                })
                time.sleep(0.4)   # cortesía con la API

    columnas = ["tema", "busqueda", "archivo", "titulo", "autor",
                "fecha", "licencia", "pagina", "credito"]
    nuevo = not os.path.exists(CATALOGO)
    with open(CATALOGO, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columnas)
        if nuevo:
            w.writeheader()
        w.writerows(catalogo)

    print(f"\nDescargadas: {total} · ya estaban: {saltados}")
    print(f"Catálogo: {CATALOGO}")
    print("\nPegá la columna 'credito' en la descripción de cada video.")


# ---------------------------------------------------------------------------
# Curaduría: qué buscar para cada tema. Los términos van en inglés porque es
# donde Commons tiene mejor indexado su material.
# ---------------------------------------------------------------------------

TEMAS = {
    # --- Video 1: qué comía un soldado romano ---
    "roma/comida": [
        "Roman quern stone mill",
        "carbonized bread Pompeii",
        "Roman military bread",
        "Roman amphora food",
        "Roman kitchen utensils archaeology",
        "Roman granary horreum",
    ],
    "roma/ejercito": [
        "Trajan's Column relief soldiers",
        "Roman legionary reenactment",
        "Roman marching equipment",
        "Roman military fort reconstruction",
        "Roman army camp plan",
    ],
    "roma/vindolanda": [
        "Vindolanda tablets",
        "Vindolanda fort",
        "Roman writing tablet ink",
    ],

    # --- Video 2: cómo se bañaba la gente en la Edad Media ---
    "medieval/higiene": [
        "medieval bathhouse woodcut",
        "medieval bathing manuscript illumination",
        "wooden bathing tub medieval",
        "medieval soap making",
    ],

    # --- Video 3: cuánto costaba vivir en 1650 ---
    "moderna/mercado": [
        "Dutch golden age market scene painting",
        "17th century still life bread",
        "17th century silver coins",
        "merchant scales 17th century",
        "17th century account book manuscript",
    ],

    # --- Video 4: qué comía la gente en tiempos de Jesús ---
    "siglo1/galilea": [
        "first century Galilee archaeology",
        "ancient Galilee fishing boat",
        "Herodian pottery vessel",
        "ancient olive press",
        "ancient flatbread archaeology",
        "Sea of Galilee landscape",
    ],

    # --- Video 5: qué se hacía sin anestesia ---
    "medicina/cirugia": [
        "antique surgical instruments",
        "Victorian operating theatre",
        "19th century amputation kit",
        "history of anaesthesia ether",
        "medical illustration 19th century surgery",
    ],

    # --- Video 6: un día en la vida de una mujer egipcia ---
    "egipto/cotidiano": [
        "ancient Egyptian tomb painting daily life",
        "Egyptian woman grinding grain statuette",
        "ancient Egyptian bread baking model",
        "Egyptian household objects museum",
        "Egyptian tomb painting agriculture",
    ],

    # --- Transversales: sirven en casi cualquier video ---
    "general/mapas": [
        "historical map Roman Empire",
        "old world map engraving",
        "antique map Europe 17th century",
    ],
    "general/manuscritos": [
        "medieval manuscript page",
        "illuminated manuscript marginalia",
        "ancient papyrus document",
    ],
}

if __name__ == "__main__":
    main()
