#!/usr/bin/env python3
"""
El mismo compositor (compositor.py), con las cuentas hechas de a bloques en
numpy en lugar de una muestra por vez en Python. Unas 20 veces más rápido.

No cambia ninguna decisión musical: usa planificar(), tabla_respiracion() y las
mismas constantes de compositor.py, consume el azar en el mismo orden (la
misma semilla da los mismos acordes, cuencos y pájaros) y cada filtro hace las
mismas operaciones que el original. Lo único que puede diferir es el redondeo
de la última cifra decimal de algunas fases, muy por debajo de lo audible:
probar_igualdad() compara las dos versiones muestra por muestra.

Lo usa compositor.py con --motor rapido (el de siempre si numpy está instalado).
No cubre --aire ni --binaural: con esos, compositor.py usa el motor original.
"""
import math, os, random, tempfile, wave
import numpy as np
from scipy.signal import lfilter

import compositor as C

SR, TABLA = C.SR, C.TABLA


def tabla_acorde(voces):
    """compositor.tabla_acorde, vectorizada: mismo orden de parciales y de fases."""
    L = 1
    for _, den in voces:
        L = C.mcm(L, den)
    parciales = {}
    for i, (num, den) in enumerate(voces):
        k = num * (L // den)
        peso = 1.0 / (1.0 + 0.45 * i)
        for h, amp in C.ESPECTRO_PAD:
            idx = k * h
            if idx * (1.0 / L) > 17:
                continue
            parciales[idx] = parciales.get(idx, 0.0) + amp * peso
    tabla = np.zeros(TABLA)
    i = np.arange(TABLA)
    for idx, amp in parciales.items():
        w = 2.0 * math.pi * idx / TABLA
        fase = random.uniform(0, 2 * math.pi)
        tabla += amp * np.sin(w * i + fase)
    pico = np.max(np.abs(tabla)) or 1.0
    return tabla / pico, L


def cuenco(frecuencia, duracion=24.0, caracter="suave"):
    perfil = C.CARACTERES[caracter]
    n = int(duracion * SR)
    buf = np.zeros(n)
    i = np.arange(n)
    modos = [(1.00, 1.00, 0.9), (2.75, 0.42, 1.5), (5.38, 0.18, 2.4), (8.90, 0.07, 3.6)]
    modos = [(r, a * peso, v) for (r, a, v), peso in zip(modos, perfil["parciales"])]
    ataque = int(perfil["ataque"] * SR)
    for ratio, amp, veloc in modos:
        for desdoble in (1.0, 1.0035):
            w = 2.0 * math.pi * frecuencia * ratio * desdoble / SR
            decaim = veloc * 3.0 / n
            buf += amp * 0.5 * np.sin(w * i) * np.exp(-decaim * i)
    pico = np.max(np.abs(buf)) or 1.0
    x = np.minimum(1.0, i / ataque)
    env = x if perfil["curva_ataque"] == "recta" else x * x * (3.0 - 2.0 * x)
    return buf / pico * env


def gorjeo(f_ini, f_fin, dur):
    n = int(dur * SR)
    i = np.arange(n)
    x = i / n
    f = f_ini + (f_fin - f_ini) * x
    fase = np.cumsum(2.0 * math.pi * f / SR)
    env = np.minimum(1.0, i / (0.004 * SR)) * np.exp(-3.2 * x)
    return (np.sin(fase) + 0.3 * np.sin(2 * fase)) * env


def frase_ave(rnd):
    """compositor.frase_ave: las mismas llamadas a rnd, en el mismo orden."""
    gorjeos = []
    n_g = rnd.randint(2, 5)
    base = rnd.uniform(2100, 4200)
    for _ in range(n_g):
        f0 = base * rnd.uniform(0.85, 1.15)
        f1 = f0 * rnd.choice([1.45, 1.25, 0.72, 0.85, 1.0])
        gorjeos.append((gorjeo(f0, f1, rnd.uniform(0.06, 0.17)), rnd.uniform(0.05, 0.19)))
    total = sum(len(g) + int(p * SR) for g, p in gorjeos)
    buf = np.zeros(total)
    pos = 0
    for g, pausa in gorjeos:
        buf[pos:pos + len(g)] += g
        pos += len(g) + int(pausa * SR)
    # el paso bajo de un polo, con la misma cuenta que el original (y += a·(x − y))
    a = 1.0 - math.exp(-2.0 * math.pi * 2600.0 / SR)
    y, out = 0.0, buf.tolist()
    for i in range(total):
        y += a * (out[i] - y)
        out[i] = y
    buf = np.array(out)
    pico = np.max(np.abs(buf)) or 1.0
    return buf / pico


class Reverb:
    """compositor.Reverb procesando de a bloques. Un peine con retardo L sólo
    depende de lo que entró hace L muestras, así que un tramo de hasta L
    muestras se calcula entero de una vez; el filtro de amortiguación es un
    polo, que lfilter hace con las mismas operaciones que el original."""

    def __init__(self, rt60=6.0, damp=0.42, ancho=23):
        self.damp = damp
        self.combs = []
        for d in (1557, 1617, 1491, 1422):
            for canal, off in ((0, 0), (1, ancho)):
                largo = d + off
                fb = 10 ** (-3.0 * (largo / SR) / rt60)
                self.combs.append({"hist": np.zeros(largo), "L": largo, "fb": fb,
                                   "filtro": 0.0, "canal": canal})
        self.aps = []
        for d in (225, 556, 341):
            for canal, off in ((0, 0), (1, 11)):
                self.aps.append({"hist": np.zeros(d + off), "L": d + off, "canal": canal})

    def procesar(self, izq, der):
        entrada = (izq + der) * 0.5
        n = len(entrada)
        hum = [np.zeros(n), np.zeros(n)]
        b, a = [1.0 - self.damp], [1.0, -self.damp]
        for c in self.combs:
            L, fb = c["L"], c["fb"]
            y_all = np.empty(n)
            k = 0
            while k < n:
                m = min(L, n - k)
                y = c["hist"][:m].copy()
                f, zf = lfilter(b, a, y, zi=[self.damp * c["filtro"]])
                c["filtro"] = f[-1]
                w = entrada[k:k + m] + f * c["fb"]
                c["hist"] = np.concatenate([c["hist"][m:], w])
                y_all[k:k + m] = y
                k += m
            hum[c["canal"]] += y_all
        hum[0] *= 0.25
        hum[1] *= 0.25
        for ap in self.aps:
            L, ch = ap["L"], ap["canal"]
            h = hum[ch]
            out = np.empty(n)
            k = 0
            while k < n:
                m = min(L, n - k)
                y = ap["hist"][:m].copy()
                hs = h[k:k + m]
                ap["hist"] = np.concatenate([ap["hist"][m:], hs + y * 0.5])
                out[k:k + m] = y - hs
                k += m
            hum[ch] = out
        return hum[0], hum[1]


def componer(ruta, segundos, raiz, modo, semilla, rt60, caracter="suave",
             resp=(C.RESP_INICIAL, C.RESP_FINAL), aves=0.0, verbose=True):
    grados = C.MODOS[modo]
    total = int(segundos * SR)
    resp_ini, resp_fin = resp
    secciones, eventos, _ = C.planificar(segundos, modo, semilla, raiz, resp)
    if verbose:
        print(f"  {len(secciones)} secciones de {C.RESP_POR_SECCION} respiraciones")
        print(f"  respiración {resp_ini:.1f} → {resp_fin:.1f} por minuto")
    t_resp = np.array(C.tabla_respiracion(C.CARACTERES[caracter]["piso_respiracion"]))
    rev = Reverb(rt60=rt60)
    aves_ev = C.planificar_aves(segundos, semilla, aves, eventos)
    if verbose and aves_ev:
        print(f"  {len(aves_ev)} frases de ave")
    cache = {}
    for _, f, _, _ in eventos:
        k = round(f, 1)
        if k not in cache:
            cache[k] = cuenco(f, caracter=caracter)
    if verbose:
        print(f"  {len(eventos)} cuencos · {len(cache)} timbres sintetizados")
    perfil = C.CARACTERES[caracter]
    fundido = int(perfil["fundido"] * SR)

    # Dónde empieza cada sección: la primera muestra con pos/SR >= inicio,
    # como la comparación que hace el original muestra por muestra.
    limites = [0]
    for ini, _, _ in secciones[1:]:
        p = max(0, int(math.ceil(ini * SR)) - 2)
        while p / SR < ini:
            p += 1
        limites.append(p)
    tablas = []
    for _, _, grado in secciones:          # en orden: el azar se consume igual
        base = grados[grado]
        voces = [(base[0], base[1] * 2)] + [grados[(grado + k) % len(grados)] for k in (0, 2, 4)]
        tablas.append((grado, voces))

    # Los eventos (cuencos y aves) se suman en el orden en que los vuelca el
    # original: por bloque de un segundo, primero los cuencos y después las aves.
    evs = []
    for j, (t_ev, frec, vol, pan) in enumerate(eventos):
        evs.append((int(t_ev * SR // SR), 0, j, t_ev, ('c', frec, vol, pan)))
    for j, (t_av, pan, vol, rnd) in enumerate(aves_ev):
        evs.append((int(t_av * SR // SR), 1, j, t_av, ('a', pan, vol, rnd)))
    evs.sort(key=lambda e: (e[0], e[1], e[2]))

    BLOQUE = 30 * SR
    COLA = int(26.0 * SR)
    fd, tmpname = tempfile.mkstemp(suffix='.f64', dir=os.path.dirname(os.path.abspath(ruta)) or '.')
    os.close(fd)
    mm = np.memmap(tmpname, dtype='f8', mode='w+', shape=(total, 2))
    carry = np.zeros((2, COLA))
    fase_resp, fase_tabla = 0.0, 0.0
    sec_i, tabla_act, paso_act = -1, None, None
    tabla_de = {}
    pico_global = 0.0
    e_i = 0
    for c0 in range(0, total, BLOQUE):
        n = min(BLOQUE, total - c0)
        c1 = c0 + n
        pend = np.zeros((2, n + COLA))
        pend[:, :COLA] += carry[:, :min(COLA, n + COLA)]
        # los eventos que empiezan en este tramo
        while e_i < len(evs) and evs[e_i][3] * SR < c1:
            _, _, _, t_ev, ev = evs[e_i]
            if ev[0] == 'c':
                _, frec, vol, pan = ev
                buf = cache[round(frec, 1)]
                g = C.NIVEL_CUENCO * perfil["nivel_cuenco"] * vol
            else:
                _, pan, vol, rnd = ev
                buf = frase_ave(rnd)
                g = C.NIVEL_AVE * vol
            off = int(t_ev * SR) - c0
            m = min(len(buf), n + COLA - off)
            v = buf[:m] * g
            pend[0, off:off + m] += v * (1.0 - pan)
            pend[1, off:off + m] += v * pan
            e_i += 1

        pos = np.arange(c0, c1)
        t_seg = pos / SR
        prog = t_seg / segundos if segundos else 0.0
        rpm = resp_ini + (resp_fin - resp_ini) * prog
        fr = np.mod(fase_resp + np.cumsum((rpm / 60.0) * 4096.0 / SR), 4096.0)
        fase_resp = fr[-1]
        env_resp = t_resp[fr.astype(np.int64)]

        # el pad, tramo por tramo de sección
        pad = np.empty(n)
        k = 0
        while k < n:
            p = c0 + k
            while sec_i + 1 < len(secciones) and p >= limites[sec_i + 1]:
                sec_i += 1
                grado, voces = tablas[sec_i]
                tabla_act, divisor = tabla_acorde(voces)
                paso_act = (raiz / divisor) * TABLA / SR
            fin = limites[sec_i + 1] - c0 if sec_i + 1 < len(secciones) else n
            fin = min(fin, n)
            m = fin - k
            lectura = np.mod(fase_tabla + paso_act * np.arange(m), TABLA)
            fase_tabla = math.fmod(fase_tabla + paso_act * m, TABLA)
            i0 = lectura.astype(np.int64)
            frac = lectura - i0
            a_ = tabla_act[i0 % TABLA]
            b_ = tabla_act[(i0 + 1) % TABLA]
            pad[k:fin] = (a_ + (b_ - a_) * frac) * C.NIVEL_PAD * env_resp[k:fin]
            k = fin

        seco_i = pad + pend[0, :n]
        seco_d = pad + pend[1, :n]
        h_i, h_d = rev.procesar(seco_i, seco_d)
        W = C.REVERB_WET
        env = np.minimum(1.0, np.minimum(pos / fundido, (total - pos) / fundido))
        vi = (seco_i * (1 - W) + h_i * W) * env
        vd = (seco_d * (1 - W) + h_d * W) * env
        mm[c0:c1, 0] = vi
        mm[c0:c1, 1] = vd
        pico_global = max(pico_global, float(np.max(np.abs(vi))), float(np.max(np.abs(vd))))
        carry = pend[:, n:n + COLA]
        if verbose:
            print(f"  {c1 / SR / 60:5.1f} / {total / SR / 60:.1f} min", end='\r', flush=True)

    objetivo = 10 ** (-3.0 / 20.0)
    g = objetivo / pico_global if pico_global else 1.0
    with wave.open(ruta, "w") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        for c0 in range(0, total, BLOQUE):
            x = np.asarray(mm[c0:c0 + BLOQUE])
            q = np.trunc(np.clip(x * g, -1.0, 1.0) * 32767).astype('<i2')
            w.writeframes(q.tobytes())
    del mm
    os.remove(tmpname)
    if verbose:
        print()
    return len(secciones), len(eventos)
