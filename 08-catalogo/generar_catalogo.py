"""
Genera el control de catálogo a partir del catálogo en markdown.

El markdown de 01-nicho es la ÚNICA fuente de verdad: si se añade una obra allí,
se regeneran el CSV y el Excel y todo queda sincronizado.

    python3 generar_catalogo.py            # CSV + Excel
    python3 generar_catalogo.py --csv      # solo el CSV (sin openpyxl)
    python3 generar_catalogo.py --xlsx     # solo el Excel

El CSV es el que lee lote.py para renderizar. No necesita dependencias.
El Excel es para trabajar a mano: estado, URLs y métricas.

CUIDADO: regenerar el Excel lo sobrescribe y se pierde lo rellenado a mano.
Para eso está --csv, que no lo toca.
"""
import csv as _csv
import os as _os
import sys as _sys
import re, hashlib
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

RAIZ_REPO = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
MD = _os.path.join(RAIZ_REPO, "01-nicho", "nicho-e-identidad.md")
OUT = _os.path.join(RAIZ_REPO, "08-catalogo", "catalogo_canal.xlsx")
OUT_CSV = _os.path.join(RAIZ_REPO, "08-catalogo", "catalogo.csv")

HACER_CSV = "--xlsx" not in _sys.argv
HACER_XLSX = "--csv" not in _sys.argv

# --- Parsear el catálogo ---
pilar_actual, obras = None, []
# Las intenciones. Desde el 23/09 el catálogo se ordena por lo que la obra
# acompaña, no por la técnica. Internamente sigue llamándose "pilar".
PILARES = {"Dormir": "Dormir", "Ansiedad": "Ansiedad", "Meditar": "Meditar",
           "Soltar": "Soltar", "Concentración": "Concentración"}
for linea in open(MD, encoding="utf-8"):
    m = re.match(r"^### (\w+[\wáéíóúñ]*)", linea.strip())
    if m and m.group(1) in PILARES:
        pilar_actual = PILARES[m.group(1)]
        continue
    m = re.match(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*(\w+)\s*\|\s*(\d+) min\s*\|\s*([\w-]+)\s*\|", linea)
    if m and pilar_actual:
        obras.append({"n": int(m.group(1)), "nombre": m.group(2), "name": m.group(3),
                      "raiz": int(m.group(4)), "modo": m.group(5), "dur": int(m.group(6)),
                      "pilar": pilar_actual, "ambiente": m.group(7)})
assert len(obras) == 40, f"se esperaban 40 obras, se encontraron {len(obras)}"

# --- Derivar los campos ---
# Idioma principal: INGLÉS (23/09). El español va como traducción del título y
# la descripción, que YouTube muestra a quien tiene el idioma en español.
CLAVE = {  # palabra clave de búsqueda por intención, en los dos idiomas
    "Dormir":        ("Música para dormir", "Sleep Music"),
    "Ansiedad":      ("Música para momentos de ansiedad", "Music for Anxiety"),
    "Meditar":       ("Música para meditar", "Meditation Music"),
    "Soltar":        ("Música para soltar tensión", "Music to Release Tension"),
    "Concentración": ("Música para concentrarse", "Focus Music"),
}
RESP = {"Dormir": (4.5, 3.5), "Ansiedad": (6.0, 4.5), "Meditar": (5.5, 4.5),
        "Soltar": (6.0, 4.5), "Concentración": (6.0, 5.5)}

# Los cinco ambientes aprobados en escucha: cómo se llaman en el título y con
# qué parámetros se arma cada uno (ver 03-composicion/sonido-ambiente.md).
AMBIENTES = {
    "mar":           ("Olas del mar", "Ocean Waves", None, "--fondo mar"),
    "mar-aves":      ("Mar y pájaros", "Ocean and Birds", "aves", "--fondo mar --nivel-capa -4"),
    "zen":           ("Templo zen", "Zen Temple", "zen",
                      "--fondo mar --nivel-fondo -7 --nivel-capa 2"),
    "selva":         ("Selva tropical", "Tropical Rainforest", "aves",
                      "--fondo selva --nivel-capa -2"),
    "lluvia-tambor": ("Lluvia sobre hojas", "Rain on Leaves", "ancestral",
                      "--fondo fuego --nivel-capa 0 --nivel-obra -20"),
}
DENSIDAD_CAPA = {"selva": " --densidad 2", "zen": " --densidad 1.4"}

# Registro por intención. Dormir y Concentración bajan una octava: el sub pasa de 264 a
# 132 Hz, que es donde vive un drone de dormir. Ver sistema-composicion.md.
REGISTRO = {"Dormir": "grave", "Ansiedad": "medio", "Meditar": "medio",
            "Soltar": "medio", "Concentración": "grave"}
FACTOR = {"grave": 0.5, "medio": 1.0, "brillante": 2.0}

# Para qué es cada obra. Decir "práctica de respiración" en una pieza de
# estudio de dos horas sería copiar y pegar, no describir.
PROPOSITO = {
    "Dormir": "Para acompañar el sueño.",
    "Ansiedad": "Para acompañar un momento de pausa cuando la cabeza no para.",
    "Meditar": "Para acompañar una práctica de meditación.",
    "Soltar": "Para acompañar un rato de soltar la tensión del día.",
    "Concentración": "Para acompañar el trabajo o el estudio.",
}
PROPOSITO_EN = {
    "Dormir": "To accompany sleep.",
    "Ansiedad": "To accompany a pause when your mind won't stop.",
    "Meditar": "To accompany a meditation practice.",
    "Soltar": "To accompany some time to let go of the day's tension.",
    "Concentración": "To accompany work or study.",
}
# Las etiquetas van en inglés, como títulos y descripciones; la palabra clave
# en español va al final, para la búsqueda de Latinoamérica.
ETIQ_BASE = ["relaxing music", "meditation music", "calming music", "ambient music",
             "just intonation", "original composition", "Rin"]
ETIQ_PILAR = {
    "Dormir":        ["deep sleep", "sleep music", "insomnia"],
    "Ansiedad":      ["anxiety relief", "stress relief", "calming music"],
    "Meditar":       ["mindfulness", "zen music", "yoga music"],
    "Soltar":        ["stress relief", "let go", "healing music"],
    "Concentración": ["study music", "deep focus", "work music"],
}
ETIQ_AMBIENTE = {
    "mar":           ["ocean waves", "sea sounds"],
    "mar-aves":      ["ocean waves", "birdsong", "nature sounds"],
    "zen":           ["zen temple", "temple bells", "wind chimes"],
    "selva":         ["rainforest sounds", "birdsong", "nature sounds"],
    "lluvia-tambor": ["rain sounds", "rain on leaves", "shamanic drum"],
}
SUSCRIBIR = "https://www.youtube.com/@rinchanneloficial?sub_confirmation=1"

def dur_txt(m):
    if m >= 60 and m % 60 == 0:
        h = m // 60
        return f"{h} hora" if h == 1 else f"{h} horas"
    return f"{m} minutos"

def dur_en(m):
    if m >= 60 and m % 60 == 0:
        h = m // 60
        return f"{h} Hour" if h == 1 else f"{h} Hours"
    return f"{m} Minutes"

def semilla(o):
    """Semilla estable derivada del nombre: la misma obra da siempre el mismo audio."""
    return int(hashlib.sha256(o["nombre"].encode()).hexdigest()[:6], 16) % 999_999 + 1

def miniatura(o):
    if o["pilar"] == "Soltar":
        return f'{o["raiz"]} HZ'
    if o["pilar"] in ("Ansiedad", "Meditar"):
        return f'{o["dur"]} MIN'
    h = o["dur"] // 60
    return f"{h} HOURS" if h > 1 else f'{o["dur"]} MIN'

def descripcion_es(o):
    """La traducción al español. Se carga en YouTube como traducción del video."""
    ri, rf = RESP[o["pilar"]]
    reg = REGISTRO[o["pilar"]]
    raiz_real = o["raiz"] * FACTOR[reg]
    # En registro grave la raíz REAL no es la nominal. Decir "528 Hz" a
    # secas sería inexacto, y la exactitud es el argumento del canal.
    afinacion = (f'raíz en {round(raiz_real, 1):g} Hz, la octava grave de {o["raiz"]} Hz'
                 if reg == "grave" else f'raíz en {o["raiz"]} Hz')
    return (
        f'{o["nombre"]} · {dur_txt(o["dur"])}\n\n'
        f'{PROPOSITO[o["pilar"]]}\n'
        f'Ambiente: {AMBIENTES[o["ambiente"]][0].lower()}.\n\n'
        f'Compuesta con {afinacion}, en entonación justa, modo {o["modo"]}.\n'
        f'Ciclo respiratorio: de {ri:.1f} a {rf:.1f} respiraciones por minuto, '
        f'inhalar 40 % / exhalar 60 %.\n'
        f'Composición original, sintetizada desde cero: el ambiente también. '
        f'Ninguna muestra procede de terceros.\n\n'
        f'Mejor a volumen bajo.\n'
        f'Suscríbete para las próximas obras: {SUSCRIBIR}\n\n'
        f'{hashtags(o)}'
    )

def descripcion(o):
    """La descripción principal, en inglés."""
    ri, rf = RESP[o["pilar"]]
    reg = REGISTRO[o["pilar"]]
    raiz_real = o["raiz"] * FACTOR[reg]
    tuning = (f'root of {round(raiz_real, 1):g} Hz, the low octave of {o["raiz"]} Hz'
              if reg == "grave" else f'root of {o["raiz"]} Hz')
    return (
        f'{o["name"]} · {dur_en(o["dur"])}\n\n'
        f'{PROPOSITO_EN[o["pilar"]]}\n'
        f'Ambience: {AMBIENTES[o["ambiente"]][1].lower()}.\n\n'
        f'Composed around a {tuning}, in just intonation, {o["modo"]} mode.\n'
        f'Breathing cycle: from {ri:.1f} down to {rf:.1f} breaths per minute, '
        f'40 % inhale / 60 % exhale.\n'
        f'Original composition, synthesized from scratch, ambience included. '
        f'No third-party samples.\n\n'
        f'Best at low volume.\n'
        f'Subscribe for new pieces: {SUSCRIBIR}\n\n'
        f'{hashtags(o)}'
    )

def etiquetas(o):
    e = ([CLAVE[o["pilar"]][1].lower(), f'{o["raiz"]} hz', f'{o["raiz"]} hz music']
         + ETIQ_PILAR[o["pilar"]] + ETIQ_AMBIENTE[o["ambiente"]] + ETIQ_BASE
         + [CLAVE[o["pilar"]][0].lower()])
    return ", ".join(dict.fromkeys(e))

def hashtags(o):
    base = {"Dormir": "#SleepMusic", "Ansiedad": "#RelaxingMusic",
            "Meditar": "#MeditationMusic", "Soltar": "#RelaxingMusic",
            "Concentración": "#FocusMusic"}[o["pilar"]]
    # dict.fromkeys quita duplicados conservando el orden: sin esto, el pilar
    # Frecuencias repetía la etiqueta de la raíz dos veces.
    return " ".join(dict.fromkeys([base, "#Meditation", f'#{o["raiz"]}Hz']))

COLS = [
    ("id", 11), ("titulo", 70), ("titulo_es", 70), ("tema", 13), ("ambiente", 14),
    ("descripcion_optimizada", 60), ("descripcion_es", 60),
    ("titulo_miniatura", 17), ("hashtags", 34), ("etiquetas", 60),
    ("imagen_miniatura", 24), ("url_video", 30),
    ("raiz_hz", 9), ("modo", 12), ("registro", 11), ("semilla", 10),
    ("duracion_min", 13),
    ("comando_regeneracion", 62), ("comando_ambiente", 62),
    ("estado", 13), ("fecha_publicacion", 18),
    ("vistas", 10), ("suscriptores", 13), ("subs_por_1000", 14),
]
LLENAR = {"imagen_miniatura", "url_video", "estado", "fecha_publicacion",
          "vistas", "suscriptores"}

def comando_ambiente(o, s):
    """El segundo paso: envolver la obra en su ambiente. La capa dura la obra
    más los 20 s de entrada y los 20 de salida que agrega ambiente.py."""
    _, _, capa, params = AMBIENTES[o["ambiente"]]
    base = f'OBRA-{o["n"]:03d}'
    obra = f'audio/{base}_{o["raiz"]}_{o["modo"]}.wav'     # como la guarda lote.py
    cmd = ""
    if capa:
        cmd = (f'python3 03-composicion/capas.py {capa} {o["dur"] * 60 + 40} '
               f'audio/{base}_capa.wav --semilla {s}{DENSIDAD_CAPA.get(o["ambiente"], "")} && ')
    return (cmd + f'python3 03-composicion/ambiente.py {obra} '
                  f'audio/{base}_final.wav {params}'
                  + (f' --capa audio/{base}_capa.wav' if capa else ""))


# --- Construir las filas una sola vez, para CSV y Excel ---
def construir_filas():
    filas = []
    for o in sorted(obras, key=lambda x: x["n"]):
        s = semilla(o)
        filas.append({
            "id": f'OBRA-{o["n"]:03d}',
            "titulo": (f'{CLAVE[o["pilar"]][1]} · {AMBIENTES[o["ambiente"]][1]} · '
                       f'{o["raiz"]} Hz · {o["name"]} · {dur_en(o["dur"])}'),
            "titulo_es": (f'{CLAVE[o["pilar"]][0]} · {AMBIENTES[o["ambiente"]][0]} · '
                          f'{o["raiz"]} Hz · {o["nombre"]} · {dur_txt(o["dur"])}'),
            "tema": o["pilar"],
            "ambiente": o["ambiente"],
            "descripcion_optimizada": descripcion(o),
            "descripcion_es": descripcion_es(o),
            "titulo_miniatura": miniatura(o),
            "hashtags": hashtags(o),
            "etiquetas": etiquetas(o),
            "imagen_miniatura": "", "url_video": "",
            "raiz_hz": o["raiz"], "modo": o["modo"],
            "registro": REGISTRO[o["pilar"]], "semilla": s,
            "duracion_min": o["dur"],
            # Sin cuenco hasta que haya uno que pase la escucha.
            "comando_regeneracion": (
                f'python3 03-composicion/compositor.py --minutos {o["dur"]} '
                f'--raiz {o["raiz"]} --modo {o["modo"]} --semilla {s} '
                f'--caracter sin-cuenco'
                + (f' --registro {REGISTRO[o["pilar"]]}'
                   if REGISTRO[o["pilar"]] != "medio" else "")),
            "comando_ambiente": comando_ambiente(o, s),
            "estado": "pendiente", "fecha_publicacion": "",
            "vistas": "", "suscriptores": "", "subs_por_1000": "",
        })
    return filas


FILAS = construir_filas()

if HACER_CSV:
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = _csv.DictWriter(f, fieldnames=[c for c, _ in COLS])
        w.writeheader()
        w.writerows(FILAS)
    print(f"{OUT_CSV} · {len(FILAS)} obras")

if not HACER_XLSX:
    raise SystemExit

# Letras de columna derivadas de COLS: al añadir una columna, las fórmulas
# siguen apuntando al sitio correcto sin tocarlas una por una.
L = {nombre: get_column_letter(i) for i, (nombre, _) in enumerate(COLS, 1)}

wb = Workbook()
ws = wb.active
ws.title = "Catálogo"

ARIAL = "Arial"
azul = Font(name=ARIAL, size=10, color="0000FF")
negro = Font(name=ARIAL, size=10)
cab = Font(name=ARIAL, size=10, bold=True, color="FFFFFF")
relleno_cab = PatternFill("solid", fgColor="1F3B4D")
relleno_llenar = PatternFill("solid", fgColor="FFFF00")
borde = Border(bottom=Side(style="thin", color="BBBBBB"))

for i, (nombre, ancho) in enumerate(COLS, 1):
    c = ws.cell(1, i, nombre)
    c.font, c.fill = cab, relleno_cab
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.column_dimensions[get_column_letter(i)].width = ancho

for fila, valores in enumerate(FILAS, start=2):
    for i, (nombre, _) in enumerate(COLS, 1):
        if nombre == "subs_por_1000":
            # Se guarda el denominador para no dividir por cero antes de publicar.
            c = ws.cell(fila, i,
                        f'=IFERROR({L["suscriptores"]}{fila}/'
                        f'{L["vistas"]}{fila}*1000,"")')
            c.number_format = "0.0"
        else:
            c = ws.cell(fila, i, valores[nombre])
        c.font = azul if nombre in LLENAR else negro
        if nombre in LLENAR:
            c.fill = relleno_llenar
        c.alignment = Alignment(vertical="top", wrap_text=nombre in
                                {"descripcion_optimizada", "etiquetas", "titulo",
                                 "comando_regeneracion"})
        c.border = borde

ws.freeze_panes = "B2"
ws.auto_filter.ref = f"A1:{get_column_letter(len(COLS))}{len(obras)+1}"
for fila in range(2, len(obras) + 2):
    ws.row_dimensions[fila].height = 58

# --- Resumen ---
rs = wb.create_sheet("Resumen")
rs.column_dimensions["A"].width = 26
for col in "BCDE":
    rs.column_dimensions[col].width = 14
ult = len(obras) + 1

def tit(f, t):
    c = rs.cell(f, 1, t); c.font = Font(name=ARIAL, size=11, bold=True)

tit(1, "Estado del catálogo")
for i, (et, val) in enumerate([("Total de obras", None), ("Pendientes", "pendiente"),
                               ("Compuestas", "compuesta"), ("Montadas", "montada"),
                               ("Publicadas", "publicada")], start=2):
    rs.cell(i, 1, et).font = negro
    f = (f'=COUNTA(Catálogo!{L["id"]}2:{L["id"]}{ult})' if val is None
         else f'=COUNTIF(Catálogo!{L["estado"]}2:{L["estado"]}{ult},"{val}")')
    c = rs.cell(i, 2, f); c.font = negro

tit(8, "Por intención")
for i, et in enumerate(["Intención", "Obras", "Publicadas", "Minutos totales"], start=1):
    c = rs.cell(9, i, et); c.font = Font(name=ARIAL, size=10, bold=True)
for i, p in enumerate(list(PILARES), start=10):
    rs.cell(i, 1, p).font = negro
    T, E, D = L["tema"], L["estado"], L["duracion_min"]
    rs.cell(i, 2, f'=COUNTIF(Catálogo!{T}2:{T}{ult},A{i})').font = negro
    rs.cell(i, 3, f'=COUNTIFS(Catálogo!{T}2:{T}{ult},A{i},'
                  f'Catálogo!{E}2:{E}{ult},"publicada")').font = negro
    rs.cell(i, 4, f'=SUMIF(Catálogo!{T}2:{T}{ult},A{i},'
                  f'Catálogo!{D}2:{D}{ult})').font = negro
rs.cell(15, 1, "TOTAL").font = Font(name=ARIAL, size=10, bold=True)
for col, letra in ((2, "B"), (3, "C"), (4, "D")):
    c = rs.cell(15, col, f"=SUM({letra}10:{letra}14)")
    c.font = Font(name=ARIAL, size=10, bold=True)

tit(17, "Rendimiento")
rs.cell(18, 1, "Vistas totales").font = negro
rs.cell(18, 2, f'=SUM(Catálogo!{L["vistas"]}2:{L["vistas"]}{ult})').font = negro
rs.cell(19, 1, "Suscriptores totales").font = negro
rs.cell(19, 2, f'=SUM(Catálogo!{L["suscriptores"]}2:'
               f'{L["suscriptores"]}{ult})').font = negro
rs.cell(20, 1, "Subs por 1.000 vistas").font = negro
c = rs.cell(20, 2, '=IFERROR(B19/B18*1000,"")'); c.number_format = "0.00"; c.font = negro
rs.cell(20, 3, "← la métrica que decide el canal").font = Font(name=ARIAL, size=9, italic=True)

# --- Leyenda ---
lg = wb.create_sheet("Leyenda")
lg.column_dimensions["A"].width = 26
lg.column_dimensions["B"].width = 94
texto = [
    ("Cómo se usa esta hoja", None),
    ("", None),
    ("Celdas amarillas", "Las únicas que se rellenan a mano. Todo lo demás está calculado o generado."),
    ("Texto azul", "Dato de entrada. El texto negro no se toca."),
    ("", None),
    ("id", "Identificador fijo de la obra. No cambia nunca."),
    ("titulo", "Título de YouTube: palabra clave · raíz · nombre propio · duración."),
    ("titulo / descripcion_optimizada", "En inglés, el idioma principal del canal."),
    ("titulo_es / descripcion_es", "La traducción al español. Se carga en YouTube Studio → Subtítulos → Título y descripción."),
    ("tema", "Intención: qué acompaña la obra. Determina la palabra clave y el ciclo respiratorio."),
    ("ambiente", "Ambiente aprobado en escucha: mar, mar-aves, zen, selva o lluvia-tambor."),
    ("comando_ambiente", "Segundo paso: envuelve la obra compuesta en su ambiente."),
    ("descripcion_optimizada", "Descripción bilingüe lista para pegar. Solo falta añadir los capítulos tras el montaje."),
    ("titulo_miniatura", "Texto de la miniatura: 2-4 palabras que COMPLETAN el título, nunca lo repiten."),
    ("hashtags", "Tres, al final de la descripción."),
    ("etiquetas", "Etiquetas del video, separadas por coma."),
    ("imagen_miniatura", "AMARILLA. Ruta o URL de la portada una vez generada."),
    ("url_video", "AMARILLA. URL de YouTube una vez publicado."),
    ("raiz_hz / modo / registro / semilla", "Parámetros de composición. El registro grave baja una octava (Dormir y Concentración). La semilla regenera la obra idéntica."),
    ("comando_regeneracion", "Comando exacto. Copiar, pegar y ejecutar: devuelve el mismo audio bit a bit."),
    ("estado", "AMARILLA. pendiente / compuesta / montada / publicada"),
    ("fecha_publicacion", "AMARILLA. Formato AAAA-MM-DD."),
    ("vistas / suscriptores", "AMARILLA. Copiar de YouTube Studio a los 14 días de publicar."),
    ("subs_por_1000", "Calculada. Es la métrica que decide el canal: por debajo de 1, el problema es la portada, no la música."),
    ("", None),
    ("Ejemplo de fila rellenada", "imagen_miniatura: portadas/obra-001.png | url_video: https://youtu.be/XXXXXXXXXXX | estado: publicada | fecha_publicacion: 2026-10-07 | vistas: 4820 | suscriptores: 11"),
]
for i, (a, b) in enumerate(texto, start=1):
    ca = lg.cell(i, 1, a)
    ca.font = Font(name=ARIAL, size=11, bold=True) if b is None else Font(name=ARIAL, size=10, bold=True)
    if b:
        cb = lg.cell(i, 2, b); cb.font = negro
        cb.alignment = Alignment(wrap_text=True, vertical="top")

wb.save(OUT)
print(f"{OUT} · {len(obras)} obras · {len(COLS)} columnas · 3 hojas")
