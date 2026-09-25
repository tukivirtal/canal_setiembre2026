"""
La hoja de Shorts: 5 por obra, cada uno con lo necesario para publicarlo en
YouTube Shorts y en TikTok. La importa generar_catalogo.py.

Cada Short de una obra se distingue de los otros cuatro en todo lo que se ve y
se oye: otro tramo de la obra, otro encuadre del mandala, otro instante del
bucle y otra frase en pantalla. Cinco copias de una plantilla es justo lo que
YouTube penaliza como contenido repetitivo y lo que TikTok entierra.

En TikTok van DOS textos distintos, y no se mezclan:
  tiktok_portada       el título de la portada, el que se ve en la cuadrícula del
                       perfil. Corto. Se escribe a mano al elegir la portada.
  tiktok_descripcion   el texto que acompaña al video, con los hashtags.
Si se programa con Metricool, NO se usa su campo de título de TikTok: estamparía
el título en el video. Solo la descripción.
"""
import csv, os

N_SHORTS = 5
DURACION = 45                                   # segundos
ZOOM = [1.0, 1.15, 1.3, 1.08, 1.22]             # encuadre del mandala vertical
DESFASE = [0, 9.6, 19.2, 28.8, 38.4]            # instante del bucle de 48 s

# La frase que va en pantalla, debajo de la frecuencia. Describe el momento,
# nunca promete un efecto.
FRASE = {
    "Dormir": ["to fall asleep", "let the day go quiet", "lights off, breathe slower",
               "for the hour before sleep", "the house is asleep"],
    "Ansiedad": ["for when your mind won't stop", "breathe out longer than you breathe in",
                 "a pause, just for you", "slow down, one breath at a time",
                 "before you begin"],
    "Meditar": ["for a quiet meditation", "sit, listen, breathe",
                "follow the sound until it fades", "nothing to do but listen",
                "one breath, then the next"],
    "Soltar": ["to let go of the day", "drop your shoulders", "unclench your jaw",
               "breathe out what you carried today", "let the tension go with the sound"],
    "Concentración": ["for deep focus", "one task, nothing else", "put it on and start",
                      "quiet sound for deep work", "stay with it a little longer"],
}
# La portada de TikTok: dos o tres palabras tras la frecuencia.
PORTADA = {
    "Dormir": ["sleep", "night", "rest", "dark room", "drift off"],
    "Ansiedad": ["calm", "exhale", "pause", "breathe", "slow down"],
    "Meditar": ["meditate", "stillness", "listen", "sit", "silence"],
    "Soltar": ["let go", "unwind", "release", "soften", "rest"],
    "Concentración": ["focus", "deep work", "study", "flow", "one task"],
}
# El texto que acompaña al video: distinto de la frase y de la portada.
LEYENDA = {
    "Dormir": ["Save this for tonight.", "Lights off, volume low.",
               "Stay until your breathing slows.", "The quiet hour before sleep.",
               "Send this to someone who can't sleep."],
    "Ansiedad": ["Save this for the next hard moment.", "Headphones on. Exhale slowly.",
                 "Stay for one full breath.", "A small pause in the middle of the day.",
                 "Send this to someone who needs a pause."],
    "Meditar": ["Save this for your next sit.", "Close your eyes for 45 seconds.",
                "Listen until the sound fades.", "A minute of stillness.",
                "Send this to someone who meditates."],
    "Soltar": ["Save this for the end of the day.", "Drop your shoulders. Breathe out.",
               "Let this one play twice.", "Leave the day at the door.",
               "Send this to someone who needs to unwind."],
    "Concentración": ["Save this for your next work session.", "Start the task now.",
                      "Play it, then begin.", "Quiet sound for deep work.",
                      "Send this to someone studying tonight."],
}
HASHTAGS = {
    "Dormir": ["#sleepmusic", "#sleep", "#relaxingmusic"],
    "Ansiedad": ["#anxietyrelief", "#calm", "#relaxingmusic"],
    "Meditar": ["#meditationmusic", "#meditation", "#mindfulness"],
    "Soltar": ["#stressrelief", "#relaxingmusic", "#calm"],
    "Concentración": ["#focusmusic", "#studymusic", "#deepwork"],
}
ETIQUETAS = {
    "Dormir": ["sleep music", "deep sleep"],
    "Ansiedad": ["anxiety relief", "calming music"],
    "Meditar": ["meditation music", "mindfulness"],
    "Soltar": ["stress relief", "relaxing music"],
    "Concentración": ["focus music", "study music"],
}

COLS = [
    ("id_short", 15), ("obra", 11), ("n", 4), ("archivo", 22),
    ("inicio_s", 9), ("zoom", 7), ("desfase_s", 9), ("frase_en_pantalla", 34),
    ("yt_titulo", 60), ("yt_descripcion", 60), ("yt_etiquetas", 40), ("yt_video_relacionado", 30),
    ("tiktok_portada", 20), ("tiktok_descripcion", 60),
    ("estado", 12), ("fecha_youtube", 13), ("url_youtube", 30),
    ("fecha_tiktok", 13), ("url_tiktok", 30),
]
LLENAR = {"estado", "fecha_youtube", "url_youtube", "fecha_tiktok", "url_tiktok"}
PUBLICADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shorts_publicados.csv")


def dur_corta(minutos):
    m = int(minutos)
    return f"{m // 60} h" if m >= 60 and m % 60 == 0 else f"{m} min"


def inicios(duracion_min):
    """Cinco tramos repartidos por la obra: pasada la entrada lenta del ambiente
    (la obra aparece entera hacia los 70 s) y antes de la salida."""
    total = duracion_min * 60 + 40                  # 20 s de entrada y 20 de salida
    a, b = 90, total - DURACION - 20
    return [round(a + (b - a) * k / (N_SHORTS - 1)) for k in range(N_SHORTS)]


def filas_shorts(obras):
    """obras: las filas del catálogo (con titulo, tema, raiz_hz, url_video...)."""
    publicados = {}
    if os.path.exists(PUBLICADOS):
        with open(PUBLICADOS, encoding="utf-8") as f:
            publicados = {p["id_short"]: p for p in csv.DictReader(f)}
    filas = []
    for o in obras:
        tema, hz = o["tema"], o["raiz_hz"]
        amb = o["titulo"].split(" · ")[1]
        dur = dur_corta(o["duracion_min"])
        tags = " ".join(HASHTAGS[tema] + [f"#{hz}hz"])
        for k, ini in enumerate(inicios(int(o["duracion_min"]))):
            n = k + 1
            ids = f'{o["id"]}-S{n}'
            frase = FRASE[tema][k]
            fila = {
                "id_short": ids, "obra": o["id"], "n": n, "archivo": f"short-{n}.mp4",
                "inicio_s": ini, "zoom": ZOOM[k], "desfase_s": DESFASE[k],
                "frase_en_pantalla": frase,
                "yt_titulo": f"{frase[0].upper()}{frase[1:]} · {hz} Hz · {amb}",
                "yt_descripcion": (f"{LEYENDA[tema][k]}\n"
                                   f"Full piece ({dur}): {o['titulo']}\n"
                                   + (f"{o['url_video']}\n" if o.get("url_video") else "")
                                   + f"\n{tags} #shorts"),
                "yt_etiquetas": ", ".join(ETIQUETAS[tema] + [f"{hz} hz", amb.lower(), "Rin"]),
                "yt_video_relacionado": o.get("url_video", ""),
                "tiktok_portada": f"{hz} Hz · {PORTADA[tema][k]}",
                "tiktok_descripcion": (f"{LEYENDA[tema][k]} Full {dur} piece on YouTube: "
                                       f"Rin.\n" + " ".join(dict.fromkeys(tags.split() + ["#meditation"]))),
                "estado": "pendiente", "fecha_youtube": "", "url_youtube": "",
                "fecha_tiktok": "", "url_tiktok": "",
            }
            if ids in publicados:
                p = publicados[ids]
                fila.update({c: p.get(c, "") for c in
                             ("fecha_youtube", "url_youtube", "fecha_tiktok", "url_tiktok")})
                fila["estado"] = "publicado"
            filas.append(fila)
    return filas
