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
PUBLICADAS = _os.path.join(RAIZ_REPO, "08-catalogo", "publicadas.csv")
TONOS_CSV = _os.path.join(RAIZ_REPO, "08-catalogo", "tonos.csv")
# Giro de matiz del mandala, en grados. Cada obra de un mismo ambiente toma el
# siguiente de la lista, así dos videos del mismo ambiente no se ven iguales.
# Una vez asignado queda guardado en tonos.csv y no cambia más.
TONOS = [0, 110, -70, 180, 35, -110, 70, 150, -35, -150, 55]
OUT = _os.path.join(RAIZ_REPO, "08-catalogo", "catalogo_canal.xlsx")
OUT_CSV = _os.path.join(RAIZ_REPO, "08-catalogo", "catalogo.csv")
OUT_SHORTS = _os.path.join(RAIZ_REPO, "08-catalogo", "shorts.csv")

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
assert len(obras) == 51, f"se esperaban 51 obras, se encontraron {len(obras)}"

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
    # Pájaros y campanitas de viento, con el mar muy lejos: lo «asiático sutil»
    # que pidió la escucha del 26/09, para la ansiedad
    "jardin":        ("Pájaros y campanas del templo", "Birds and Temple Bells", "jardin",
                      "--fondo mar --nivel-fondo -8 --nivel-capa 0"),
    # Lluvia sola, sin tambor ni capa: para dormir (29/09)
    "lluvia":        ("Lluvia suave", "Gentle Rain", None, "--fondo lluvia"),
    # Mar lejano y ondas theta que bajan a delta, para dormir con auriculares (30/09)
    # Guqin y xiao (tao_largo.py) sobre lluvia, para dormir (03/10). La obra
    # manda: en el TikTok aprobado los instrumentos van 12,7 dB sobre la
    # lluvia; acá ~8, y la lluvia gana terreno a medida que la música se retira.
    "guqin":         ("Guqin y lluvia", "Guqin & Rain", None,
                      "--fondo lluvia --nivel-obra 0 --nivel-fondo -6 --entrada-obra 6"),
    "theta":         ("Mar lejano y ondas theta", "Distant Ocean & Theta Waves", "theta",
                      "--fondo mar --nivel-fondo -4 --nivel-capa -11"),
    # Ruidos de color (04/10), lo más buscado para dormir. Manda el ruido: la
    # obra queda como un drone muy lejano y la capa zen, pocas campanas.
    "marron":        ("Ruido marrón y campanas lejanas", "Brown Noise & Distant Temple Bells", "zen",
                      "--fondo marron --nivel-obra -24 --nivel-capa -9 --entrada-obra 4"),
    "delta":         ("Ruido rosa y ondas delta", "Pink Noise & Delta Waves", "delta",
                      "--fondo rosa --nivel-fondo -1 --nivel-obra -22 --nivel-capa -13 --entrada-obra 4"),
}
DENSIDAD_CAPA = {"selva": " --densidad 2", "zen": " --densidad 1.4", "marron": " --densidad 0.6"}

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
    "jardin":        ["birdsong", "wind chimes", "zen garden"],
    "lluvia":        ["rain sounds", "rain sounds for sleeping", "gentle rain"],
    "theta":         ["theta waves", "binaural beats", "ocean waves"],
    "guqin":         ["guqin", "chinese music", "rain sounds"],
    "marron":        ["brown noise", "brown noise for sleeping", "temple bells"],
    "delta":         ["pink noise", "delta waves", "binaural beats"],
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

# Títulos y descripciones con la PROMESA primero (análisis del 27/09: quien
# llega desde la búsqueda mira el 86 %, y el título descriptivo «Music for
# Anxiety · Zen Temple · …» no promete nada). Palabras clave de la búsqueda en
# EE. UU. (vidIQ): calming music, music for anxiety, calm your nervous system.
# Las obras sin entrada acá siguen con el formato de siempre.
PROMESA = {
    41: dict(
        titulo="Stop Overthinking 🌿 Calming Music for Anxiety · Birdsong & Temple Bells · 432 Hz · 1 Hour",
        gancho=("One hour to stop overthinking. Calming music for anxiety with birdsong and soft temple bells, and a slower breath.",
                "The music slows from 6 to 4.5 breaths per minute: breathe out longer than you breathe in, and let it lead."),
        uso="🎧 Headphones, low volume. You don't have to solve anything tonight. Just listen.",
        hashtags="#calmingmusic #musicforanxiety #432hz",
        etiquetas=["stop overthinking", "stop overthinking music", "calming music", "music for anxiety",
                   "calming music for anxiety", "anxiety relief", "stress relief music", "calm your nervous system",
                   "nervous system regulation", "relaxing music", "meditation music", "calm music", "birdsong",
                   "birds singing", "temple bells", "wind chimes", "zen garden", "432 hz", "432 hz music", "rin",
                   "música para la ansiedad"]),
    42: dict(
        titulo="Calm Your Nervous System 🌿 Zen Temple Bells · 528 Hz · Music for Anxiety & Sleep · 3 Hours",
        gancho=("Three hours of calm for an anxious mind and a restless night. Soft zen temple bells over a warm, steady drone.",
                "The music slows from 6 to 4.5 breaths per minute: breathe out longer than you breathe in, and let your body follow."),
        uso="🌙 Play it low while you rest, read, work or fall asleep.",
        hashtags="#calmingmusic #sleepmusic #528hz",
        etiquetas=["calm your nervous system", "nervous system regulation", "calming music", "music for anxiety",
                   "anxiety relief", "sleep music", "meditation for sleep", "deep sleep music", "stress relief music",
                   "zen music", "zen temple", "temple bells", "528 hz", "528 hz music", "relaxing music",
                   "meditation music", "3 hours", "rin", "música para la ansiedad"]),
    # 29/09: lo que más crece en el nicho. «dark screen sleep music» +269 % en un
    # mes, 54 % EE. UU., competencia baja; «black screen sleep music» 110 mil
    # búsquedas; «sleeping music for deep sleeping» 905 mil. Los que explotan en
    # canales chicos de EE. UU. son pantalla negra, lluvia y «fall asleep fast».
    43: dict(
        titulo="Dark Screen Sleep Music 🌙 Gentle Rain for Deep Sleep · Fall Asleep Fast · 432 Hz · 3 Hours",
        gancho=("Three hours of dark screen sleep music: gentle rain and a slow, warm drone for deep sleep.",
                "The screen fades to black after 3 minutes, so no light keeps you awake. The music slows to 3.5 breaths per minute: let your breathing follow it down."),
        uso="🌙 Lights off, phone face down, volume low. Nothing else to do tonight.",
        hashtags="#sleepmusic #darkscreen #432hz",
        oscura=3,
        comentario="How long did the rain take to put you to sleep? 🌧️ Tell us in minutes. "
                   "If you're reading this awake: lights off, phone face down, and press play again.",
        etiquetas=["dark screen sleep music", "black screen sleep music", "sleep music", "deep sleep music",
                   "sleeping music for deep sleeping", "fall asleep fast", "rain sounds for sleeping",
                   "gentle rain", "sleep music for anxiety", "insomnia", "cortisol reset",
                   "relaxing sleep music", "music for sleep", "432 hz", "432 hz sleep music", "3 hours",
                   "rin", "música para dormir"]),
    # 30/09: la idea que dio YouTube Studio para el canal («pantalla oscura con
    # ondas theta para dormir mejor») y su título más atractivo, con la
    # palabra clave que crece (dark screen) adentro.
    44: dict(
        titulo="Deep Sleep Theta Waves 🌙 Turn Off Your Thoughts · Dark Screen · Fall Asleep Fast · 3 Hours",
        gancho=("Three hours of theta waves for deep sleep, over a distant ocean and a slow, warm drone. 🎧 Use headphones for the best experience.",
                "With headphones, each ear hears a slightly different tone, 6 Hz apart. Over the hours the difference slows from theta (6 Hz, drifting off) to delta (2 Hz, deep sleep). The screen fades to black after 3 minutes."),
        uso="🌙 Lights off, phone face down, volume low. Let your thoughts go quiet.",
        hashtags="#thetawaves #sleepmusic #darkscreen",
        oscura=3,
        comentario="Headphones or speaker? 🎧 Tell us which, and how far into the theta waves you got "
                   "before falling asleep.",
        etiquetas=["theta waves", "theta waves sleep", "deep sleep theta waves", "binaural beats",
                   "binaural beats for sleep", "delta waves", "dark screen sleep music",
                   "black screen sleep music", "deep sleep music", "fall asleep fast",
                   "turn off your thoughts", "stop overthinking", "sleep meditation", "ocean waves",
                   "432 hz", "3 hours", "rin", "música para dormir"]),
    # 03/10: la versión larga del TikTok «Woke up at 3 AM again?». Dolor (despertarse
    # a las 3), solución (el reloj chino del cuerpo y la exhalación «xū») y
    # música (guqin en modo yu). La tendencia: «Chinamaxxing» (2026).
    45: dict(
        titulo="Woke Up at 3 AM? 🌙 Chinese Guqin & Rain to Fall Back Asleep · Dark Screen · 3 Hours",
        gancho=("Woke up at 3 AM again? Three hours of guqin, xiao flute and gentle rain to fall back asleep.",
                "In the Chinese body clock, 1 to 3 AM is the liver's hour: the hour of what you couldn't let go of. Don't check the time. Breathe out slowly through your lips, \"shhh\" (xū), six times, and let the strings take it from there. The screen fades to black after 3 minutes."),
        uso="🌙 Phone face down, volume low. The music thins out over the hours, until only the rain is left.",
        hashtags="#sleepmusic #guqin #chinesemusic",
        oscura=3,
        motor="tao",
        nota="The yu scale is the one Chinese five-element music keeps for the night. A 2,000-year-old tradition, not medical advice.",
        comentario="What time did you wake up tonight? 🌙 Tell us, then press play and breathe out slowly: shhh.",
        etiquetas=["woke up at 3am", "fall back asleep", "music to fall back asleep", "chinese sleep music",
                   "guqin", "guqin music", "chinese meditation music", "chinese music for sleep",
                   "rain sounds for sleeping", "dark screen sleep music", "black screen sleep music",
                   "deep sleep music", "sleep music", "traditional chinese medicine", "chinamaxxing",
                   "3 hours", "rin", "música para dormir"]),
    # 04/10 · calendario de 15 días, un video por día, alternando corto y largo.
    # Lo que dicen los datos: los cortos con promesa concreta traen el 65 % de las
    # vistas; las campanas y los pájaros son lo que más retiene (18:33 en «Stop
    # Overthinking»); el templo zen, lo más visto en Shorts.
    46: dict(
        titulo="3 AM Reset 🌙 10 Minutes of Guqin & Rain to Fall Back Asleep · Chinese Sleep Music",
        gancho=("Woke up at 3 AM? Ten minutes of guqin, xiao flute and gentle rain to fall back asleep.",
                "Don't check the time. Breathe out slowly through your lips, \"shhh\", six times, and let the strings take it from there."),
        uso="🌙 Phone face down, volume low. If you're still awake at the end, the full 3 hours are on the channel.",
        hashtags="#sleepmusic #guqin #3am",
        motor="tao",
        nota="The yu scale is the one Chinese five-element music keeps for the night. A 2,000-year-old tradition, not medical advice.",
        comentario="What time did you wake up tonight? 🌙 Tell us, then breathe out slowly: shhh.",
        etiquetas=["3am reset", "fall back asleep", "woke up at 3am", "music to fall back asleep", "guqin",
                   "chinese sleep music", "10 minute sleep music", "rain sounds for sleeping", "sleep music",
                   "chinese meditation music", "rin", "música para dormir"]),
    47: dict(
        titulo="5-Minute Nervous System Reset 🔔 Zen Temple Bells to Calm Anxiety Fast · 528 Hz",
        gancho=("Five minutes to calm your nervous system: zen temple bells over a warm, slow drone.",
                "Drop your shoulders. Breathe out longer than you breathe in, and let the bells keep you company until the end."),
        uso="🎧 Use it between meetings, before a hard conversation, or whenever your chest feels tight.",
        hashtags="#nervoussystemreset #anxietyrelief #528hz",
        comentario="Where are you listening from right now? 🔔 Work, bed, car? Tell us.",
        etiquetas=["nervous system reset", "5 minute nervous system reset", "calm anxiety fast", "anxiety relief",
                   "5 minute meditation", "zen temple bells", "temple bells", "calming music", "528 hz",
                   "nervous system regulation", "quick calm", "rin", "música para la ansiedad"]),
    48: dict(
        titulo="Zen Temple Bells for Deep Sleep 🌙 Dark Screen · Calm Your Mind · 432 Hz · 3 Hours",
        gancho=("Three hours of soft zen temple bells over a distant ocean, for deep sleep.",
                "The bells grow sparse as the night goes on. The screen fades to black after 3 minutes, so no light keeps you awake."),
        uso="🌙 Lights off, phone face down, volume low.",
        hashtags="#sleepmusic #templebells #darkscreen",
        oscura=3,
        comentario="Do bells help you sleep, or do you prefer rain? 🔔🌧️ Tell us, it shapes the next piece.",
        etiquetas=["zen temple bells", "temple bells sleep", "zen sleep music", "dark screen sleep music",
                   "black screen sleep music", "deep sleep music", "sleep music", "calm your mind",
                   "zen music", "meditation music", "432 hz", "3 hours", "rin", "música para dormir"]),
    49: dict(
        titulo="Stop Overthinking in 10 Minutes 🌿 Birdsong & Temple Bells · Calming Music · 432 Hz",
        gancho=("Ten minutes to stop overthinking: birdsong, soft temple bells and a slower breath.",
                "You don't have to solve it now. Breathe out longer than you breathe in, and just listen to the birds."),
        uso="🌿 Headphones on, eyes closed if you can.",
        hashtags="#stopoverthinking #calmingmusic #432hz",
        comentario="What's the thought that won't leave you alone today? 🌿 Write one word. Then let it go.",
        etiquetas=["stop overthinking", "stop overthinking music", "10 minute meditation", "calming music",
                   "music for anxiety", "birdsong", "temple bells", "anxiety relief", "calm your mind",
                   "432 hz", "rin", "música para la ansiedad"]),
    # 04/10 · ruidos de color (01-nicho/tendencias-sonidos-2026-10.md). El título
    # y la primera línea dicen exactamente qué es, como se busca.
    50: dict(
        titulo="Brown Noise for Deep Sleep 🌙 Distant Temple Bells · Black Screen · Fall Asleep Fast · 3 Hours",
        gancho=("Brown noise and pink noise are the most searched sounds for sleep. This is brown noise: low, warm and steady, with distant temple bells.",
                "Like heavy rain on a faraway roof. No beat, no melody to follow, nothing to listen for. The screen fades to black after 3 minutes."),
        uso="🌙 Lights off, phone face down, volume low. Let it cover the noise.",
        hashtags="#brownnoise #sleepsounds #darkscreen",
        oscura=3,
        comentario="Brown noise or rain: which one puts you to sleep faster? 🌙 Tell us.",
        etiquetas=["brown noise", "brown noise for sleeping", "brown noise sleep", "brown noise black screen",
                   "brown noise 3 hours", "deep sleep", "sleep sounds", "black screen sleep",
                   "dark screen sleep music", "fall asleep fast", "temple bells", "noise for sleeping",
                   "rin", "ruido marrón para dormir"]),
    51: dict(
        titulo="Pink Noise + Delta Waves for Deep Sleep 🌙 Binaural Beats · Black Screen · 3 Hours",
        gancho=("Pink noise and brown noise are the most searched sounds for sleep, and pink noise with delta waves is the pairing sleep apps use in their sleep category. 🎧 Use headphones for the best experience.",
                "Pink noise is soft and even, like steady rain. Underneath, each ear hears a slightly different tone: the difference starts at 3 Hz and slows to 1.5 Hz, the rhythm of deep sleep. The screen fades to black after 3 minutes."),
        uso="🌙 Headphones on, lights off, volume low.",
        hashtags="#pinknoise #deltawaves #deepsleep",
        oscura=3,
        nota="Delta waves are the brain's slowest rhythm, the one of deep sleep. Not medical advice.",
        comentario="Headphones or speaker? 🎧 Tell us how far you got before falling asleep.",
        etiquetas=["pink noise", "pink noise for sleeping", "delta waves", "delta waves sleep",
                   "pink noise delta waves", "binaural beats", "binaural beats for sleep", "deep sleep",
                   "black screen sleep", "sleep sounds", "fall asleep fast", "3 hours", "rin",
                   "ruido rosa para dormir"]),
}


# El comentario fijado (01/10): una pregunta fácil de contestar. Quien contesta
# vuelve a ver la respuesta, se siente parte y el video suma comentarios. Las
# obras con PROMESA pueden traer el suyo.
COMENTARIO = {
    "Dormir": "What keeps you awake at night? 🌙 Write it here and leave it with us. "
              "Then press play and let it go. A new sleep piece every week.",
    "Ansiedad": "What's on your mind right now? 🌿 Write it here and leave it with us. "
                "Sometimes saying it is enough to set it down.",
    "Meditar": "Where are you listening from today? 🌿 A new piece every week.",
    "Soltar": "What are you letting go of today? 🌿 Write one word.",
    "Concentración": "What are you working on? ✍️ Tell us, and we'll keep you company.",
}


def descripcion_promesa(o, p):
    raiz = (f'{o["raiz"] * FACTOR["grave"]:g} Hz, the low octave of {o["raiz"]} Hz'
            if REGISTRO[o["pilar"]] == "grave" and p.get("motor") != "tao" else f'{o["raiz"]} Hz')
    return (f'{p["gancho"][0]}\n{p["gancho"][1]}\n\n'
            f'{p["uso"]}\n'
            f'🌿 Subscribe for a new calm piece every week: {SUSCRIBIR}\n\n'
            f'Original composition by Rin, synthesized from scratch in just intonation around '
            f'{raiz}, {o["modo"]} mode. No samples.'
            + (f' {p["nota"]}' if p.get("nota") else '') + '\n\n'
            f'{p["hashtags"]}')


def descripcion_es(o):
    """La traducción al español. Se carga en YouTube como traducción del video."""
    ri, rf = RESP[o["pilar"]]
    reg = REGISTRO[o["pilar"]] if PROMESA.get(o["n"], {}).get("motor") != "tao" else "medio"
    raiz_real = o["raiz"] * FACTOR[reg]
    # En registro grave la raíz REAL no es la nominal. Decir "528 Hz" a
    # secas sería inexacto, y la exactitud es el argumento del canal.
    afinacion = (f'raíz en {round(raiz_real, 1):g} Hz, la octava grave de {o["raiz"]} Hz'
                 if reg == "grave" else f'raíz en {o["raiz"]} Hz')
    return (
        f'{o["nombre"]} · {dur_txt(o["dur"])}\n\n'
        f'{PROPOSITO[o["pilar"]]}\n'
        f'Ambiente: {AMBIENTES[o["ambiente"]][0].lower()}.\n'
        + ('🎧 Usa auriculares para una mejor experiencia: cada oído escucha un tono apenas '
           'distinto y la diferencia baja de theta (6 Hz) a delta (2 Hz).\n'
           if o["ambiente"] == "theta" else '')
        + f'\nCompuesta con {afinacion}, en entonación justa, modo {o["modo"]}.\n'
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
    # En minúscula: así se escriben en el canal (y en TikTok).
    return " ".join(dict.fromkeys([base, "#Meditation", f'#{o["raiz"]}Hz'])).lower()

COLS = [
    ("id", 11), ("titulo", 70), ("titulo_es", 70), ("tema", 13), ("ambiente", 14),
    ("descripcion_optimizada", 60), ("descripcion_es", 60),
    ("titulo_miniatura", 17), ("hashtags", 34), ("etiquetas", 60),
    ("imagen_miniatura", 24), ("url_video", 30),
    ("raiz_hz", 9), ("modo", 12), ("registro", 11), ("semilla", 10), ("tono", 6),
    ("duracion_min", 13), ("pantalla_oscura_min", 12), ("comentario_fijado", 40),
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
               f'audio/{base}_capa.wav --semilla {s} --raiz {o["raiz"]}{DENSIDAD_CAPA.get(o["ambiente"], "")} && ')
    return (cmd + f'python3 03-composicion/ambiente.py {obra} '
                  f'audio/{base}_final.wav {params}'
                  + (f' --capa audio/{base}_capa.wav' if capa else ""))


def asignar_tonos():
    """El tono de cada obra: el guardado en tonos.csv, o el siguiente libre de su
    ambiente (por orden de id) para las que todavía no tienen."""
    tonos = {}
    if _os.path.exists(TONOS_CSV):
        tonos = {r["id"]: int(r["tono"]) for r in _csv.DictReader(open(TONOS_CSV, encoding="utf-8"))}
    for o in sorted(obras, key=lambda x: x["n"]):
        i = f'OBRA-{o["n"]:03d}'
        if i in tonos:
            continue
        usados = [tonos[f'OBRA-{p["n"]:03d}'] for p in obras
                  if p["ambiente"] == o["ambiente"] and f'OBRA-{p["n"]:03d}' in tonos]
        libres = [t for t in TONOS if t not in usados] or TONOS
        tonos[i] = libres[0] if len(usados) < len(TONOS) else TONOS[len(usados) % len(TONOS)]
    with open(TONOS_CSV, "w", newline="", encoding="utf-8") as f:
        w = _csv.writer(f); w.writerow(["id", "tono"])
        for i in sorted(tonos):
            w.writerow([i, tonos[i]])
    return tonos


# --- Construir las filas una sola vez, para CSV y Excel ---
def construir_filas():
    tonos = asignar_tonos()
    filas = []
    for o in sorted(obras, key=lambda x: x["n"]):
        s = semilla(o)
        p = PROMESA.get(o["n"])
        filas.append({
            "id": f'OBRA-{o["n"]:03d}',
            "titulo": (f'{CLAVE[o["pilar"]][1]} · {AMBIENTES[o["ambiente"]][1]} · '
                       f'{o["raiz"]} Hz · {o["name"]} · {dur_en(o["dur"])}'),
            "titulo_es": (f'{CLAVE[o["pilar"]][0]} · {AMBIENTES[o["ambiente"]][0]} · '
                          f'{o["raiz"]} Hz · {o["nombre"]} · {dur_txt(o["dur"])}'),
            "tema": o["pilar"],
            "ambiente": o["ambiente"],
            "descripcion_optimizada": descripcion_promesa(o, p) if p else descripcion(o),
            "descripcion_es": descripcion_es(o),
            "titulo_miniatura": miniatura(o),
            "hashtags": p["hashtags"] if p else hashtags(o),
            "etiquetas": ", ".join(p["etiquetas"]) if p else etiquetas(o),
            "imagen_miniatura": "", "url_video": "",
            "raiz_hz": o["raiz"], "modo": o["modo"],
            "registro": REGISTRO[o["pilar"]], "semilla": s,
            "tono": tonos[f'OBRA-{o["n"]:03d}'],
            "duracion_min": o["dur"],
            # Minutos de mandala antes de que la pantalla se apague (0: nunca)
            "pantalla_oscura_min": (p or {}).get("oscura", 0),
            "comentario_fijado": (p or {}).get("comentario", COMENTARIO[o["pilar"]]),
            # Sin cuenco hasta que haya uno que pase la escucha.
            "comando_regeneracion": (
                f'python3 03-composicion/tao_largo.py --minutos {o["dur"]} --raiz {o["raiz"]} '
                f'--modo {o["modo"]} --semilla {s}'
                if (p or {}).get("motor") == "tao" else
                f'python3 03-composicion/compositor.py --minutos {o["dur"]} '
                f'--raiz {o["raiz"]} --modo {o["modo"]} --semilla {s} '
                f'--caracter sin-cuenco'
                + (f' --registro {REGISTRO[o["pilar"]]}'
                   if REGISTRO[o["pilar"]] != "medio" else "")),
            "comando_ambiente": comando_ambiente(o, s),
            "estado": "pendiente", "fecha_publicacion": "",
            "vistas": "", "suscriptores": "", "subs_por_1000": "",
        })
        if p:
            filas[-1]["titulo"] = p["titulo"]
    # Lo publicado vive en publicadas.csv: si se escribiera solo en el catálogo,
    # regenerarlo lo borraría.
    for p in _csv.DictReader(open(PUBLICADAS, encoding="utf-8")):
        for f in filas:
            if f["id"] == p["id"]:
                f.update(url_video=p["url_video"], fecha_publicacion=p["fecha_publicacion"],
                         estado="publicada")
    return filas


FILAS = construir_filas()
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import shorts_catalogo as SH
SHORTS = SH.filas_shorts(FILAS)

if HACER_CSV:
    with open(OUT_SHORTS, "w", newline="", encoding="utf-8") as f:
        w = _csv.DictWriter(f, fieldnames=[c for c, _ in SH.COLS])
        w.writeheader()
        w.writerows(SHORTS)
    print(f"{OUT_SHORTS} · {len(SHORTS)} shorts")
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

# --- Shorts: 5 por obra, con lo necesario para YouTube y TikTok ---
sh = wb.create_sheet("Shorts")
for i, (nombre, ancho) in enumerate(SH.COLS, 1):
    c = sh.cell(1, i, nombre)
    c.font, c.fill = cab, relleno_cab
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    sh.column_dimensions[get_column_letter(i)].width = ancho
for fila, valores in enumerate(SHORTS, start=2):
    for i, (nombre, _) in enumerate(SH.COLS, 1):
        c = sh.cell(fila, i, valores[nombre])
        c.font = azul if nombre in SH.LLENAR else negro
        if nombre in SH.LLENAR:
            c.fill = relleno_llenar
        c.alignment = Alignment(vertical="top", wrap_text=nombre in
                                {"yt_descripcion", "tiktok_descripcion", "yt_titulo"})
        c.border = borde
    sh.row_dimensions[fila].height = 58
sh.freeze_panes = "B2"
sh.auto_filter.ref = f"A1:{get_column_letter(len(SH.COLS))}{len(SHORTS)+1}"

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
    ("ambiente", "Ambiente aprobado en escucha: mar, mar-aves, zen, selva, lluvia-tambor, jardin, lluvia, theta, guqin, marron o delta."),
    ("comando_ambiente", "Segundo paso: envuelve la obra compuesta en su ambiente."),
    ("comentario_fijado", "Comentario para escribir y fijar apenas se publica: una pregunta fácil de contestar."),
    ("pantalla_oscura_min", "Minutos de mandala antes de que la pantalla se funda a negro (videos para dormir). 0: el mandala dura todo el video."),
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
    ("Hoja Shorts", "5 por obra. Cada uno cambia de tramo de la obra, encuadre, instante del mandala y frase."),
    ("tiktok_portada", "El título de la portada en TikTok (el que se ve en el perfil). Distinto de la descripción."),
    ("tiktok_descripcion", "El texto que acompaña al video en TikTok, con hashtags. En Metricool, nunca en el campo título."),
    ("yt_video_relacionado", "El video largo. En YouTube Studio va en «Video relacionado» del Short."),
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
print(f"{OUT} · {len(obras)} obras · {len(SHORTS)} shorts · 4 hojas")
