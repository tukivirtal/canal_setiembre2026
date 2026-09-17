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
PILARES = {"Frecuencias": "Frecuencias", "Sueño": "Sueño", "Respiración": "Respiración",
           "Cuencos": "Cuencos", "Foco": "Foco"}
for linea in open(MD, encoding="utf-8"):
    m = re.match(r"^### (\w+[\wáéíóúñ]*)", linea.strip())
    if m and m.group(1) in PILARES:
        pilar_actual = PILARES[m.group(1)]
        continue
    m = re.match(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*(\w+)\s*\|\s*(\d+) min\s*\|", linea)
    if m and pilar_actual:
        obras.append({"n": int(m.group(1)), "nombre": m.group(2), "raiz": int(m.group(3)),
                      "modo": m.group(4), "dur": int(m.group(5)), "pilar": pilar_actual})
assert len(obras) == 40, f"se esperaban 40 obras, se encontraron {len(obras)}"

# --- Derivar los campos ---
CLAVE = {  # palabra clave de búsqueda por pilar, en los dos idiomas
    "Frecuencias": ("Música de meditación", "Meditation music"),
    "Sueño":       ("Música para dormir", "Sleep music"),
    "Respiración": ("Música para meditar", "Meditation music"),
    "Cuencos":     ("Cuencos tibetanos", "Singing bowls"),
    "Foco":        ("Música para concentrarse", "Focus music"),
}
RESP = {"Frecuencias": (6.0, 4.5), "Sueño": (4.5, 3.5), "Respiración": (6.0, 4.5),
        "Cuencos": (5.5, 4.5), "Foco": (6.0, 5.5)}
ETIQ_BASE = ["música relajante", "meditación", "relajación", "entonación justa",
             "composición original", "meditation music", "relaxing music", "sleep music",
             "singing bowls", "just intonation"]

def dur_txt(m):
    if m >= 60 and m % 60 == 0:
        h = m // 60
        return f"{h} hora" if h == 1 else f"{h} horas"
    return f"{m} minutos"

def semilla(o):
    """Semilla estable derivada del nombre: la misma obra da siempre el mismo audio."""
    return int(hashlib.sha256(o["nombre"].encode()).hexdigest()[:6], 16) % 999_999 + 1

def miniatura(o):
    if o["pilar"] == "Frecuencias":
        return f'{o["raiz"]} HZ'
    if o["pilar"] == "Respiración":
        return f'{o["dur"]} MIN'
    if o["pilar"] == "Cuencos":
        return "CUENCOS"
    h = o["dur"] // 60
    return f"{h} HORAS" if h > 1 else f'{o["dur"]} MIN'

def descripcion(o):
    ri, rf = RESP[o["pilar"]]
    return (
        f'{o["nombre"]} · {dur_txt(o["dur"])}\n\n'
        f'Compuesta con raíz en {o["raiz"]} Hz, en entonación justa, modo {o["modo"]}.\n'
        f'Para acompañar una práctica de respiración.\n\n'
        f'Ciclo respiratorio: de {ri:.1f} a {rf:.1f} respiraciones por minuto, '
        f'inhalar 40 % / exhalar 60 %.\n'
        f'Cuencos sintetizados cada 4 respiraciones.\n'
        f'Composición original, sintetizada desde cero. '
        f'Ninguna muestra procede de terceros.\n\n'
        f'— English —\n'
        f'Composed with a root of {o["raiz"]} Hz in just intonation, {o["modo"]} mode.\n'
        f'To accompany a breathing practice.\n'
        f'Original composition, synthesized from scratch. No third-party samples.\n\n'
        f'Capítulos:\n00:00 [completar tras el montaje]'
    )

def etiquetas(o):
    e = [f'{o["raiz"]} hz', f'música {o["raiz"]} hz', CLAVE[o["pilar"]][0].lower(),
         CLAVE[o["pilar"]][1].lower(), o["pilar"].lower(), o["modo"]] + ETIQ_BASE
    return ", ".join(dict.fromkeys(e))

def hashtags(o):
    base = {"Frecuencias": "#Meditación", "Sueño": "#MúsicaParaDormir",
            "Respiración": "#Respiración", "Cuencos": "#CuencosTibetanos",
            "Foco": "#Concentración"}[o["pilar"]]
    # dict.fromkeys quita duplicados conservando el orden: sin esto, el pilar
    # Frecuencias repetía la etiqueta de la raíz dos veces.
    return " ".join(dict.fromkeys([base, "#MúsicaRelajante", f'#{o["raiz"]}Hz']))

COLS = [
    ("id", 11), ("titulo", 52), ("tema", 13), ("descripcion_optimizada", 60),
    ("titulo_miniatura", 17), ("hashtags", 34), ("etiquetas", 60),
    ("imagen_miniatura", 24), ("url_video", 30),
    ("raiz_hz", 9), ("modo", 12), ("semilla", 10), ("duracion_min", 13),
    ("comando_regeneracion", 62), ("estado", 13), ("fecha_publicacion", 18),
    ("vistas", 10), ("suscriptores", 13), ("subs_por_1000", 14),
]
LLENAR = {"imagen_miniatura", "url_video", "estado", "fecha_publicacion",
          "vistas", "suscriptores"}

# --- Construir las filas una sola vez, para CSV y Excel ---
def construir_filas():
    filas = []
    for o in sorted(obras, key=lambda x: x["n"]):
        s = semilla(o)
        filas.append({
            "id": f'OBRA-{o["n"]:03d}',
            "titulo": f'{CLAVE[o["pilar"]][0]} · {o["raiz"]} Hz · {o["nombre"]} · {dur_txt(o["dur"])}',
            "tema": o["pilar"],
            "descripcion_optimizada": descripcion(o),
            "titulo_miniatura": miniatura(o),
            "hashtags": hashtags(o),
            "etiquetas": etiquetas(o),
            "imagen_miniatura": "", "url_video": "",
            "raiz_hz": o["raiz"], "modo": o["modo"], "semilla": s, "duracion_min": o["dur"],
            "comando_regeneracion": (f'python3 03-composicion/compositor.py --minutos {o["dur"]} '
                                     f'--raiz {o["raiz"]} --modo {o["modo"]} --semilla {s}'),
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
            c = ws.cell(fila, i, f'=IFERROR(R{fila}/Q{fila}*1000,"")')
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
    f = (f"=COUNTA(Catálogo!A2:A{ult})" if val is None
         else f'=COUNTIF(Catálogo!O2:O{ult},"{val}")')
    c = rs.cell(i, 2, f); c.font = negro

tit(8, "Por pilar")
for i, et in enumerate(["Pilar", "Obras", "Publicadas", "Minutos totales"], start=1):
    c = rs.cell(9, i, et); c.font = Font(name=ARIAL, size=10, bold=True)
for i, p in enumerate(["Frecuencias", "Sueño", "Respiración", "Cuencos", "Foco"], start=10):
    rs.cell(i, 1, p).font = negro
    rs.cell(i, 2, f'=COUNTIF(Catálogo!C2:C{ult},A{i})').font = negro
    rs.cell(i, 3, f'=COUNTIFS(Catálogo!C2:C{ult},A{i},Catálogo!O2:O{ult},"publicada")').font = negro
    rs.cell(i, 4, f'=SUMIF(Catálogo!C2:C{ult},A{i},Catálogo!M2:M{ult})').font = negro
rs.cell(15, 1, "TOTAL").font = Font(name=ARIAL, size=10, bold=True)
for col, letra in ((2, "B"), (3, "C"), (4, "D")):
    c = rs.cell(15, col, f"=SUM({letra}10:{letra}14)")
    c.font = Font(name=ARIAL, size=10, bold=True)

tit(17, "Rendimiento")
rs.cell(18, 1, "Vistas totales").font = negro
rs.cell(18, 2, f"=SUM(Catálogo!Q2:Q{ult})").font = negro
rs.cell(19, 1, "Suscriptores totales").font = negro
rs.cell(19, 2, f"=SUM(Catálogo!R2:R{ult})").font = negro
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
    ("tema", "Pilar de contenido. Determina la palabra clave y el ciclo respiratorio."),
    ("descripcion_optimizada", "Descripción bilingüe lista para pegar. Solo falta añadir los capítulos tras el montaje."),
    ("titulo_miniatura", "Texto de la miniatura: 2-4 palabras que COMPLETAN el título, nunca lo repiten."),
    ("hashtags", "Tres, al final de la descripción."),
    ("etiquetas", "Etiquetas del video, separadas por coma."),
    ("imagen_miniatura", "AMARILLA. Ruta o URL de la portada una vez generada."),
    ("url_video", "AMARILLA. URL de YouTube una vez publicado."),
    ("raiz_hz / modo / semilla", "Parámetros de composición. La semilla regenera la obra idéntica."),
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
