#!/usr/bin/env python3
"""
Compositor de música de meditación — entonación justa y pulso respiratorio.

Tres decisiones lo separan del ambient sintético corriente:

1. ENTONACIÓN JUSTA. Los intervalos son razones de enteros exactas (3/2, 5/4, 9/8),
   no las aproximaciones del temperamento igual. Sobre un drone sostenido, la tercera
   del temperamento igual está 14 centésimas alta y produce un batido áspero de ~21 Hz
   entre parciales agudos. En entonación justa los parciales coinciden exactamente y el
   acorde se funde en un solo cuerpo sonoro. Es la diferencia audible entre "sintetizador"
   y "instrumento".

2. PULSO RESPIRATORIO. La obra no tiene compás: tiene respiración. La amplitud sigue un
   ciclo asimétrico (inhalar 40 %, exhalar 60 %) que empieza a 6 respiraciones por minuto
   y baja gradualmente a 4,5. Las secciones y los cuencos caen en múltiplos enteros del
   ciclo, así que nada llega a destiempo.

3. ESPACIO. Reverberación larga y oscura (RT60 configurable, ~6 s por defecto) con
   amortiguación de agudos. Es el factor que más separa una mezcla cara de una barata.

El ruido de fondo está DESACTIVADO por defecto: ensucia el drone y no aporta nada.

Uso:
    python3 compositor.py --listar
    python3 compositor.py --minutos 3 --raiz 528 --modo hirajoshi
    python3 compositor.py --minutos 60 --raiz 528 --modo yo --semilla 7

Sin dependencias: solo Python 3.
"""

import argparse
import array
import math
import random
import wave

SR = 44100
TABLA = 8192

# --- Escalas en ENTONACIÓN JUSTA. Cada grado es una razón exacta de enteros. ---
# Se eligieron modos pentatónicos: sin semitonos no hay tensión que resolver,
# que es justo lo que se busca en música de meditación.
MODOS = {
    # Pentatónica mayor: luminosa, abierta.
    "yo":        [(1, 1), (9, 8), (5, 4), (3, 2), (5, 3)],
    # Hirajoshi, escala japonesa de koto: contemplativa, con la segunda menor justa.
    "hirajoshi": [(1, 1), (9, 8), (6, 5), (3, 2), (8, 5)],
    # Pentatónica menor: grave, introspectiva.
    "kumoi":     [(1, 1), (6, 5), (4, 3), (3, 2), (9, 5)],
    # Drone puro: solo la serie armónica baja. Lo más estable posible.
    "shin":      [(1, 1), (3, 2), (2, 1)],
}

SOLFEGGIO = {"396": 396.0, "417": 417.0, "528": 528.0,
             "639": 639.0, "741": 741.0, "852": 852.0}

# Espectro del pad: armónicos impares con caída 1/n^1.6.
# Los impares dan cuerpo tipo órgano; la caída pronunciada evita el brillo
# metálico que delata al sintetizador barato.
ESPECTRO_PAD = [(1, 1.00), (3, 0.26), (5, 0.11), (7, 0.05), (9, 0.025)]

# Respiración: 6 resp/min al inicio, 4,5 al final. Descenso gradual.
# El rango 4,5-6 no es arbitrario: es el que la investigación sobre respiración
# lenta documenta como asociado a mayor variabilidad de la frecuencia cardíaca,
# con 0,1 Hz (6 por minuto) como el valor más usado en los protocolos.
# Ver base-cientifica.md. Configurable con --respiracion.
RESP_POR_SECCION = 6
RESP_INICIAL = 6.0
RESP_FINAL = 4.5
FRAC_INHALAR = 0.40      # inhalar más corto que exhalar: patrón de relajación

NIVEL_PAD = 0.55
NIVEL_CUENCO = 0.42
NIVEL_AVE = 0.085

# Transposición por octavas. El registro por defecto (medio) deja el sub en
# raiz/2: con raíz 528 Hz son 264 Hz, dos octavas por encima de donde vive un
# drone de sueño (60-120 Hz). Para las obras del pilar Sueño hace falta "grave".
REGISTROS = {"grave": 0.5, "medio": 1.0, "brillante": 2.0}
REVERB_WET = 0.42


def mcm(a, b):
    return a * b // math.gcd(a, b)


# --------------------------------------------------------------------------
# Wavetable del acorde completo
# --------------------------------------------------------------------------

def tabla_acorde(voces):
    """
    Construye UNA wavetable con el acorde entero.

    Esto sólo es posible gracias a la entonación justa: como todas las voces son
    razones de enteros respecto de la raíz, el acorde completo es periódico, con
    un período común igual al de una frecuencia fundamental grave. Se sintetiza
    un único período y después basta una lectura de tabla por muestra, en lugar
    de una por voz.

    La pureza armónica y el coste de cómputo mejoran por el mismo motivo.

    Devuelve (tabla, divisor) donde la frecuencia de lectura es raiz/divisor.
    """
    L = 1
    for _, den in voces:
        L = mcm(L, den)

    parciales = {}
    for i, (num, den) in enumerate(voces):
        k = num * (L // den)                  # la voz es el armónico k de raiz/L
        peso = 1.0 / (1.0 + 0.45 * i)         # las voces agudas, más discretas
        for h, amp in ESPECTRO_PAD:
            idx = k * h
            if idx * (1.0 / L) > 17:          # recorte suave de agudos
                continue
            parciales[idx] = parciales.get(idx, 0.0) + amp * peso

    tabla = array.array("d", [0.0]) * TABLA
    for idx, amp in parciales.items():
        w = 2.0 * math.pi * idx / TABLA
        fase = random.uniform(0, 2 * math.pi)   # fases dispersas: baja el factor de cresta
        for i in range(TABLA):
            tabla[i] += amp * math.sin(w * i + fase)

    pico = max(abs(v) for v in tabla) or 1.0
    for i in range(TABLA):
        tabla[i] /= pico
    return tabla, L


def tabla_seno():
    """Seno puro, para las portadoras binaurales. Una lectura en vez de un math.sin."""
    return array.array("d", [math.sin(2.0 * math.pi * i / TABLA) for i in range(TABLA)])


def tabla_respiracion():
    """
    Un ciclo de respiración, como envolvente de amplitud.
    Inhalar 40 % / exhalar 60 %, con curvas de coseno elevado para que no haya
    ninguna esquina: una esquina en la envolvente se oye como un clic.
    """
    n = 4096
    t = array.array("d", [0.0]) * n
    corte = int(n * FRAC_INHALAR)
    for i in range(n):
        if i < corte:
            x = i / corte
            v = 0.5 - 0.5 * math.cos(math.pi * x)          # sube
        else:
            x = (i - corte) / (n - corte)
            v = 0.5 + 0.5 * math.cos(math.pi * x)          # baja, más lento
        t[i] = 0.55 + 0.45 * (v ** 1.4)
    return t


# --------------------------------------------------------------------------
# Cuenco tibetano
# --------------------------------------------------------------------------

def cuenco(frecuencia, duracion=24.0):
    """
    Cuenco cantor sintetizado.

    Dos detalles hacen la diferencia frente a una campana genérica:

    - Parciales INARMÓNICOS (1 : 2.75 : 5.38 : 8.9), medidos típicamente en cuencos
      de metal. Una serie armónica sonaría a órgano, no a metal.
    - Cada modo se desdobla en dos parciales separados un 0,35 %. Ese par produce
      un batido lento de ~1,8 Hz que es EXACTAMENTE el bamboleo característico
      del cuenco. Sin él suena a sintetizador.
    """
    n = int(duracion * SR)
    buf = array.array("d", [0.0]) * n
    modos = [(1.00, 1.00, 0.9), (2.75, 0.42, 1.5),
             (5.38, 0.18, 2.4), (8.90, 0.07, 3.6)]
    ataque = int(0.012 * SR)

    for ratio, amp, veloc in modos:
        for desdoble in (1.0, 1.0035):        # el par que produce el batido
            w = 2.0 * math.pi * frecuencia * ratio * desdoble / SR
            decaim = veloc * 3.0 / n
            for i in range(n):
                buf[i] += amp * 0.5 * math.sin(w * i) * math.exp(-decaim * i)

    pico = max(abs(v) for v in buf) or 1.0
    for i in range(n):
        env = min(1.0, i / ataque)
        buf[i] = buf[i] / pico * env
    return buf


# --------------------------------------------------------------------------
# Aves
# --------------------------------------------------------------------------

def gorjeo(f_ini, f_fin, dur):
    """
    Un gorjeo: un tono que se desliza de una frecuencia a otra en menos de
    un quinto de segundo. Es la forma básica de casi todo canto de pájaro —
    un barrido rápido, no una nota sostenida.
    """
    n = int(dur * SR)
    buf = array.array("d", [0.0]) * n
    fase = 0.0
    for i in range(n):
        x = i / n
        f = f_ini + (f_fin - f_ini) * x
        fase += 2.0 * math.pi * f / SR
        # Envolvente: ataque casi instantáneo, caída suave. Y el segundo
        # armónico da el timbre metálico característico.
        env = min(1.0, i / (0.004 * SR)) * math.exp(-3.2 * x)
        buf[i] = (math.sin(fase) + 0.3 * math.sin(2 * fase)) * env
    return buf


def frase_ave(rnd):
    """
    Una frase de canto: dos a cinco gorjeos con silencios entre ellos.
    Cada frase es distinta, así que ningún pájaro se repite jamás.
    """
    gorjeos = []
    n_g = rnd.randint(2, 5)
    base = rnd.uniform(2100, 4200)
    for _ in range(n_g):
        f0 = base * rnd.uniform(0.85, 1.15)
        # Dirección del barrido al azar: subida, bajada o casi plano.
        f1 = f0 * rnd.choice([1.45, 1.25, 0.72, 0.85, 1.0])
        gorjeos.append((gorjeo(f0, f1, rnd.uniform(0.06, 0.17)),
                        rnd.uniform(0.05, 0.19)))

    total = sum(len(g) + int(p * SR) for g, p in gorjeos)
    buf = array.array("d", [0.0]) * total
    pos = 0
    for g, pausa in gorjeos:
        for i, v in enumerate(g):
            buf[pos + i] += v
        pos += len(g) + int(pausa * SR)

    # Paso bajo de un polo: quita el filo. Un gorjeo crudo a 4 kHz es
    # penetrante, y lo que se busca es un pájaro LEJOS, no uno en la ventana.
    a = 1.0 - math.exp(-2.0 * math.pi * 2600.0 / SR)
    y = 0.0
    for i in range(total):
        y += a * (buf[i] - y)
        buf[i] = y

    pico = max(abs(v) for v in buf) or 1.0
    for i in range(total):
        buf[i] /= pico
    return buf


# --------------------------------------------------------------------------
# Reverberación
# --------------------------------------------------------------------------

class Reverb:
    """
    Reverberación de Schroeder: cuatro filtros peine en paralelo, dos paso-todo
    en serie. Los retardos son primos entre sí para que las reflexiones no se
    agrupen en un eco audible.

    La amortiguación es lo importante acá: sin ella la cola brilla y silba, que
    es el sonido inconfundible del reverb barato.
    """

    def __init__(self, rt60=6.0, damp=0.42, ancho=23):
        self.combs = []
        for d in (1557, 1617, 1491, 1422):
            for canal, off in ((0, 0), (1, ancho)):
                largo = d + off
                # Realimentación para el RT60 pedido: g = 10^(-3·T/RT60)
                fb = 10 ** (-3.0 * (largo / SR) / rt60)
                self.combs.append({
                    "buf": array.array("d", [0.0]) * largo,
                    "i": 0, "fb": fb, "filtro": 0.0, "canal": canal,
                })
        self.aps = []
        for d in (225, 556, 341):
            for canal, off in ((0, 0), (1, 11)):
                self.aps.append({
                    "buf": array.array("d", [0.0]) * (d + off),
                    "i": 0, "canal": canal,
                })
        self.damp = damp

    def procesar(self, izq, der):
        húmedo = [0.0, 0.0]
        entrada = (izq + der) * 0.5
        for c in self.combs:
            b, i = c["buf"], c["i"]
            y = b[i]
            c["filtro"] = y * (1.0 - self.damp) + c["filtro"] * self.damp
            b[i] = entrada + c["filtro"] * c["fb"]
            c["i"] = (i + 1) % len(b)
            húmedo[c["canal"]] += y
        húmedo[0] *= 0.25
        húmedo[1] *= 0.25
        for a in self.aps:
            b, i = a["buf"], a["i"]
            ch = a["canal"]
            y = b[i]
            b[i] = húmedo[ch] + y * 0.5
            a["i"] = (i + 1) % len(b)
            húmedo[ch] = y - húmedo[ch]
        return húmedo[0], húmedo[1]


# --------------------------------------------------------------------------
# Composición
# --------------------------------------------------------------------------

def planificar(segundos, modo, semilla, raiz, resp):
    """
    Decide la ESTRUCTURA de la obra: dónde empieza cada sección, sobre qué grado,
    y en qué instante cae cada cuenco. No sintetiza nada.

    Está separado de la síntesis para poder inspeccionar una obra antes de
    invertir minutos de cómputo en renderizarla (ver --plan).
    """
    random.seed(semilla)
    grados = MODOS[modo]
    resp_ini, resp_fin = resp

    def rpm_en(t):
        prog = (t / segundos) if segundos else 0.0
        return resp_ini + (resp_fin - resp_ini) * prog

    # Secciones: siempre un número ENTERO de respiraciones, así que su duración
    # crece sola a medida que la respiración se ralentiza.
    secciones = []
    t = 0.0
    idx = 0
    while t < segundos - 0.5:
        completa = RESP_POR_SECCION * 60.0 / rpm_en(t)
        restante = segundos - t
        # Si lo que queda no da para media sección, se absorbe en la actual en
        # lugar de dejar un muñón: un cambio de acorde de diez segundos justo
        # antes del fundido final se oye como un error, no como una sección.
        dur = restante if restante < completa * 1.5 else completa
        grado = 0 if idx % 3 == 0 else random.choice([1, 2, 3, 4]) % len(grados)
        secciones.append((t, dur, grado))
        t += dur
        idx += 1

    # Cuencos: cada 4 respiraciones. También se espacian solos.
    eventos = []
    t = 0.0
    while t < segundos - 8.0:
        ciclo = 60.0 / rpm_en(t)
        if t > 4.0:
            num, den = random.choice(grados)
            octava = random.choice([0.5, 1.0, 1.0])
            eventos.append((t, raiz * num / den * octava,
                            random.uniform(0.55, 1.0), random.uniform(0.3, 0.7)))
        t += ciclo * 4

    return secciones, eventos, rpm_en


def planificar_aves(segundos, semilla, densidad, eventos_cuenco):
    """
    Dónde canta un pájaro.

    Usa un generador aleatorio PROPIO, sembrado aparte. Si compartiera el de
    las secciones y los cuencos, activar las aves cambiaría toda la obra y las
    semillas ya publicadas dejarían de reproducir el mismo audio.

    Nunca a menos de 3 s de un cuenco: los dos son transitorios agudos y, si
    coinciden, el pájaro le roba el golpe al cuenco.
    """
    if densidad <= 0:
        return []
    rnd = random.Random(semilla * 7919 + 13)
    intervalo = 48.0 / densidad
    tiempos, t = [], rnd.uniform(10.0, 25.0)
    while t < segundos - 12.0:
        if all(abs(t - e[0]) > 3.0 for e in eventos_cuenco):
            tiempos.append((t, rnd.uniform(0.15, 0.85), rnd.uniform(0.55, 1.0)))
        t += intervalo * rnd.uniform(0.55, 1.6)
    return [(t, pan, vol, rnd) for t, pan, vol in tiempos]


def imprimir_plan(segundos, raiz, modo, semilla, resp):
    """Muestra la estructura de la obra sin sintetizarla."""
    secciones, eventos, rpm_en = planificar(segundos, modo, semilla, raiz, resp)
    grados = MODOS[modo]

    print(f"\nOBRA DE {segundos/60:g} MINUTOS")
    print(f"raíz {raiz:.1f} Hz · modo {modo} · semilla {semilla}")
    print(f"respiración {resp[0]:.1f} → {resp[1]:.1f} por minuto\n")
    print(f"{'#':>2}  {'desde':>7}  {'dura':>6}  {'resp/min':>8}  "
          f"{'grado':>7}  {'acorde (Hz)':>26}")
    print("-" * 70)

    for i, (ini, dur, grado) in enumerate(secciones, 1):
        rpm = rpm_en(ini)
        base = grados[grado]
        voces = [(base[0], base[1] * 2)]
        for k in (0, 2, 4):
            voces.append(grados[(grado + k) % len(grados)])
        hz = " ".join(f"{raiz*n/d:6.1f}" for n, d in voces)
        razon = f"{base[0]}/{base[1]}"
        print(f"{i:>2}  {ini/60:6.2f}'  {dur:5.1f}s  {rpm:8.2f}  "
              f"{razon:>7}  {hz:>26}")

    print(f"\n{len(eventos)} cuencos:")
    for i, (t, f, vol, pan) in enumerate(eventos, 1):
        lado = "izq" if pan < 0.45 else ("der" if pan > 0.55 else "centro")
        print(f"  {i:>2}  {t/60:6.2f}'  {f:7.1f} Hz  vol {vol:.2f}  {lado}")

    total_resp = sum(RESP_POR_SECCION for _ in secciones)
    print(f"\n{len(secciones)} secciones · {total_resp} respiraciones · "
          f"{len(eventos)} cuencos")
    print(f"cómputo estimado: ~{segundos/60*21/60:.1f} min")


def componer(ruta, segundos, raiz, modo, semilla, aire, rt60,
             binaural=0.0, resp=(RESP_INICIAL, RESP_FINAL), aves=0.0,
             verbose=True):
    grados = MODOS[modo]
    total = int(segundos * SR)
    resp_ini, resp_fin = resp

    # Portadora binaural: se baja el root por octavas hasta 150-300 Hz. El efecto
    # binaural se documenta mejor con portadoras graves, por debajo de ~500 Hz.
    # Nivel bajo: acompaña la obra, no la protagoniza.
    portadora = raiz
    while portadora > 300:
        portadora /= 2.0
    t_seno = tabla_seno() if binaural > 0 else None
    fase_bi_i = fase_bi_d = 0.0
    paso_bi_i = (portadora - binaural / 2.0) * TABLA / SR
    paso_bi_d = (portadora + binaural / 2.0) * TABLA / SR
    NIVEL_BI = 0.09

    secciones, eventos, _ = planificar(segundos, modo, semilla, raiz, resp)

    if verbose:
        print(f"  {len(secciones)} secciones de {RESP_POR_SECCION} respiraciones")
        print(f"  respiración {resp_ini:.1f} → {resp_fin:.1f} por minuto")
        if binaural:
            print(f"  binaural {binaural:.1f} Hz sobre portadora de {portadora:.1f} Hz "
                  f"(requiere auriculares)")

    t_resp = tabla_respiracion()
    rev = Reverb(rt60=rt60)

    # Aves
    aves_ev = planificar_aves(segundos, semilla, aves, eventos)
    if verbose and aves_ev:
        print(f"  {len(aves_ev)} frases de ave")

    cache = {}
    for _, f, _, _ in eventos:
        k = round(f, 1)
        if k not in cache:
            cache[k] = cuenco(f)
    if verbose:
        print(f"  {len(eventos)} cuencos · {len(cache)} timbres sintetizados")

    # --- Síntesis por bloques, para no cargar la obra entera en memoria ---
    BLOQUE = SR
    cola = int(26.0 * SR)
    pend_i = array.array("d", [0.0]) * (BLOQUE + cola)
    pend_d = array.array("d", [0.0]) * (BLOQUE + cola)

    muestras = array.array("h")
    fundido = int(8.0 * SR)
    ev_i = 0
    fase_tabla = 0.0
    fase_resp = 0.0
    tabla, divisor, paso_tabla = None, None, None
    sec_i = -1
    pico_global = 0.0
    salida = []

    for inicio_bloque in range(0, total, BLOQUE):
        n = min(BLOQUE, total - inicio_bloque)

        # Volcar los cuencos que empiezan en este bloque
        while ev_i < len(eventos) and eventos[ev_i][0] * SR < inicio_bloque + n:
            t_ev, frec, vol, pan = eventos[ev_i]
            buf = cache[round(frec, 1)]
            off = int(t_ev * SR) - inicio_bloque
            g = NIVEL_CUENCO * vol
            for i in range(min(len(buf), len(pend_i) - off)):
                v = buf[i] * g
                pend_i[off + i] += v * (1.0 - pan)
                pend_d[off + i] += v * pan
            ev_i += 1

        # Volcar las frases de ave que empiezan en este bloque
        while aves_ev and aves_ev[0][0] * SR < inicio_bloque + n:
            t_av, pan, vol, rnd = aves_ev.pop(0)
            buf = frase_ave(rnd)
            off = int(t_av * SR) - inicio_bloque
            g = NIVEL_AVE * vol
            for i in range(min(len(buf), len(pend_i) - off)):
                v = buf[i] * g
                pend_i[off + i] += v * (1.0 - pan)
                pend_d[off + i] += v * pan

        bloque_i = array.array("d", [0.0]) * n
        bloque_d = array.array("d", [0.0]) * n

        for i in range(n):
            pos = inicio_bloque + i
            t_seg = pos / SR

            # ¿Cambió la sección? Reconstruir la tabla del acorde.
            # Se avanza el índice al cruzar el límite, en vez de buscarlo en cada
            # muestra: con una hora de obra la búsqueda costaría más que la síntesis.
            if sec_i + 1 < len(secciones) and t_seg >= secciones[sec_i + 1][0]:
                sec_i += 1
                nueva_seccion = True
            elif sec_i < 0:
                sec_i = 0
                nueva_seccion = True
            else:
                nueva_seccion = False
            if nueva_seccion:
                s = sec_i
                _, _, grado = secciones[s]
                base = grados[grado]
                voces = [(base[0], base[1] * 2)]          # sub, una octava abajo
                for k in (0, 2, 4):
                    g2 = grados[(grado + k) % len(grados)]
                    voces.append(g2)
                tabla, divisor = tabla_acorde(voces)
                paso_tabla = (raiz / divisor) * TABLA / SR

            # Envolvente respiratoria, con la frecuencia descendiendo
            prog = t_seg / segundos if segundos else 0.0
            rpm = resp_ini + (resp_fin - resp_ini) * prog
            fase_resp += (rpm / 60.0) * 4096.0 / SR
            if fase_resp >= 4096.0:
                fase_resp -= 4096.0
            env_resp = t_resp[int(fase_resp)]

            # Lectura de la tabla del acorde con interpolación lineal
            i0 = int(fase_tabla)
            frac = fase_tabla - i0
            a = tabla[i0 % TABLA]
            b = tabla[(i0 + 1) % TABLA]
            pad = (a + (b - a) * frac) * NIVEL_PAD * env_resp
            fase_tabla += paso_tabla
            if fase_tabla >= TABLA:
                fase_tabla -= TABLA

            seco_i = pad + pend_i[i]
            seco_d = pad + pend_d[i]

            if binaural > 0:
                # Dos portadoras a distinta frecuencia, una por oído. La diferencia
                # es el pulso percibido. Sigue la envolvente respiratoria para que
                # no aparezca como una capa ajena a la obra.
                g_bi = NIVEL_BI * env_resp
                seco_i += t_seno[int(fase_bi_i) % TABLA] * g_bi
                seco_d += t_seno[int(fase_bi_d) % TABLA] * g_bi
                fase_bi_i += paso_bi_i
                fase_bi_d += paso_bi_d
                if fase_bi_i >= TABLA:
                    fase_bi_i -= TABLA
                if fase_bi_d >= TABLA:
                    fase_bi_d -= TABLA
            if aire:
                seco_i += random.uniform(-1, 1) * aire
                seco_d += random.uniform(-1, 1) * aire

            h_i, h_d = rev.procesar(seco_i, seco_d)
            vi = seco_i * (1 - REVERB_WET) + h_i * REVERB_WET
            vd = seco_d * (1 - REVERB_WET) + h_d * REVERB_WET

            env = min(1.0, pos / fundido, (total - pos) / fundido)
            vi *= env
            vd *= env
            bloque_i[i] = vi
            bloque_d[i] = vd
            pico_global = max(pico_global, abs(vi), abs(vd))

        salida.append((bloque_i, bloque_d))

        # Desplazar la cola de los cuencos
        resto = len(pend_i) - n
        for i in range(resto):
            pend_i[i] = pend_i[i + n]
            pend_d[i] = pend_d[i + n]
        for i in range(resto, len(pend_i)):
            pend_i[i] = 0.0
            pend_d[i] = 0.0

    # --- Normalización a -3 dBFS de pico. Sin limitador, sin saturación. ---
    objetivo = 10 ** (-3.0 / 20.0)
    g = objetivo / pico_global if pico_global else 1.0
    for bi, bd in salida:
        for i in range(len(bi)):
            muestras.append(int(max(-1.0, min(1.0, bi[i] * g)) * 32767))
            muestras.append(int(max(-1.0, min(1.0, bd[i] * g)) * 32767))

    with wave.open(ruta, "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(muestras.tobytes())

    return len(secciones), len(eventos)


def main():
    p = argparse.ArgumentParser(description="Compositor de música de meditación")
    p.add_argument("--minutos", type=float, default=1.0)
    p.add_argument("--raiz", default="528")
    p.add_argument("--modo", default="hirajoshi", choices=list(MODOS))
    p.add_argument("--semilla", type=int, default=None)
    p.add_argument("--rt60", type=float, default=6.0, help="cola de reverb en segundos")
    p.add_argument("--registro", default="medio", choices=list(REGISTROS),
                   help="grave baja una octava (pilar Sueño), brillante sube una")
    p.add_argument("--aves", type=float, default=0.0,
                   help="densidad de canto de pájaro (0 = ninguno, 1 = disperso, 2 = más)")
    p.add_argument("--aire", type=float, default=0.0,
                   help="ruido de fondo (0 = ninguno). Por encima de 0,02 ensucia el drone")
    p.add_argument("--binaural", type=float, default=0.0,
                   help="pulso binaural en Hz (0 = ninguno). Evidencia preliminar, "
                        "requiere auriculares. Ver base-cientifica.md")
    p.add_argument("--respiracion", default=None,
                   help="ritmo inicial,final en resp/min. Por defecto 6,4.5")
    p.add_argument("--salida", default=None)
    p.add_argument("--listar", action="store_true")
    p.add_argument("--plan", action="store_true",
                   help="imprime la estructura de la obra sin sintetizarla")
    a = p.parse_args()

    if a.listar:
        print("Modos (entonación justa, razones exactas):\n")
        for nombre, grados in MODOS.items():
            r = "  ".join(f"{n}/{d}" for n, d in grados)
            hz = "  ".join(f"{528.0*n/d:.1f}" for n, d in grados)
            print(f"  {nombre:11} {r}")
            print(f"  {'':11} {hz}  Hz sobre raíz 528\n")
        print("Raíces solfeggio:", "  ".join(SOLFEGGIO))
        return

    raiz = SOLFEGGIO.get(a.raiz) or float(a.raiz)
    semilla = a.semilla if a.semilla is not None else random.randrange(1, 10 ** 6)
    ruta = a.salida or f"obra_{a.raiz}_{a.modo}_{semilla}.wav"

    if a.respiracion:
        ini, fin = (float(x) for x in a.respiracion.split(","))
    else:
        ini, fin = RESP_INICIAL, RESP_FINAL

    factor = REGISTROS[a.registro]
    raiz_real = raiz * factor
    if factor != 1.0:
        print(f"Registro {a.registro}: raíz {raiz_real:.1f} Hz "
              f"(octava {'grave' if factor < 1 else 'aguda'} de {raiz:.0f} Hz) "
              f"· sub en {raiz_real/2:.0f} Hz")
    raiz = raiz_real

    if a.plan:
        imprimir_plan(a.minutos * 60, raiz, a.modo, semilla, (ini, fin))
        return

    print(f"Componiendo {a.minutos:g} min · raíz {raiz:.1f} Hz · modo {a.modo} "
          f"· semilla {semilla}")
    componer(ruta, a.minutos * 60, raiz, a.modo, semilla, a.aire, a.rt60,
             binaural=a.binaural, resp=(ini, fin), aves=a.aves)
    print(f"{ruta}")
    # El comando tiene que llevar TODOS los parámetros que afectan al audio,
    # o no reproduce la misma obra.
    extras = ""
    if a.registro != "medio":
        extras += f" --registro {a.registro}"
    if a.aves:
        extras += f" --aves {a.aves:g}"
    if a.binaural:
        extras += f" --binaural {a.binaural:g}"
    if a.aire:
        extras += f" --aire {a.aire:g}"
    if a.rt60 != 6.0:
        extras += f" --rt60 {a.rt60:g}"
    if a.respiracion:
        extras += f" --respiracion {a.respiracion}"
    print(f"Repetir esta obra: --minutos {a.minutos:g} --raiz {a.raiz} "
          f"--modo {a.modo} --semilla {semilla}{extras}")


if __name__ == "__main__":
    main()
