# Carácter, fondos y capas

Lo que cambió después de la primera prueba de escucha (23/09/2026), y por qué.

## Lo que dijo la escucha

La primera obra (OBRA-020, 10 min) **sobresaltaba**: "retumba mi oído", "el cuenco
suena fuerte y barato", "se nota de golpe cuando entra". Las mediciones de pico y
clipping daban bien; el problema era de percepción, y ninguna medición lo detectaba
por sí sola.

Lo que se encontró, en orden:

1. **El volumen general era de música pop**: −13,9 LUFS. Para meditar, −20 a −24.
2. **El fondo entero "bombeaba"**: el pulso respiratorio movía 5,2 dB todo el fondo
   cada ~10 s. Eran los picos que molestaban, no los cuencos.
3. **El tono sintetizado queda expuesto** al entrar, al cambiar de sección y al salir.
   Solo no tranquiliza; escondido bajo un ambiente natural, sí.
4. **El cuenco sintetizado suena barato.** Se suavizó, pero sigue siendo el punto débil.

## Las tres piezas nuevas

### `compositor.py --caracter`

| Carácter | Ataque del cuenco | Parciales agudos | Nivel del cuenco | Respiración | Entrada |
|---|---|---|---|---|---|
| `original` | 12 ms | enteros | 1,00 | 5,2 dB | 8 s |
| **`suave`** (por defecto) | 650 ms | bajados | 0,28 | 1,7 dB | 25 s |
| `sin-cuenco` | — | — | 0 | 1,7 dB | 25 s |
| `muy-suave` | 320 ms | muy bajados | 0,45 | 0,9 dB | 40 s |

`original` reproduce exactamente las obras anteriores al 22/09.

### `ambiente.py` — el fondo natural

```bash
python3 03-composicion/ambiente.py obra.wav final.wav --fondo mar
python3 03-composicion/ambiente.py obra.wav final.wav --fondo selva --capa capa-aves.wav --nivel-capa -2
python3 03-composicion/ambiente.py obra.wav final.wav --fondo mar --nivel-fondo -7 --capa capa-zen.wav --nivel-capa 2
```

- **20 s de naturaleza sola** antes de que entre la obra, y 20 s al final.
- La obra entra **en 50 s, en curva exponencial**, y 16 dB por debajo del fondo.
- Volumen final **fijo, en dos pasadas** (−22 LUFS). El ajuste dinámico hacía que el
  mar bajara de golpe cuando llegaba el tono.
- Fondos: **`mar`** (oleaje + viento), **`selva`** (aire húmedo + agua cercana, que en
  la escucha sonó más a cascada que a arroyo) y **`fuego`** (rumor de hoguera + zumbido
  tipo didgeridoo en 66 Hz, que entra a los 25 s). Alternar el fondo entre obras suma
  a la regla 3: cada obra distinta.

### `capas.py` — lo que se oye encima

```bash
python3 03-composicion/capas.py aves 160 capa-aves.wav --densidad 2
python3 03-composicion/capas.py zen  160 capa-zen.wav  --densidad 1.4
```

- **`aves`**: trinos cortos y silbidos, más densos en los primeros 20 s.
- **`zen`**: racimos de campanitas tipo *furin* afinadas en hirajoshi, y tres golpes
  lentos de bloque de madera (*mokugyo*).
- **`ancestral`**: chasquidos de leña desde el primer segundo, tambor chamánico como un
  latido (entra a los 20 s y baja de 62 a 54 por minuto, nunca exactamente a tiempo) y
  un palo de lluvia cada 40-60 s. Se usa con `--fondo fuego`.

Todo se sintetiza desde ruido y ondas: **no hay grabaciones ajenas**, el máster sigue
siendo propio.

## Lo que aprobó la escucha

| Prueba | Veredicto |
|---|---|
| Mar + tono bajo y lento | "Percibo la tranquilidad del mar" |
| **Zen sobre mar lejano** | **"Muy bien"** — identidad del canal |
| Selva, primera versión | Descartada: "suena a batidora". Tenía modulaciones rápidas y periódicas (arroyo a ~4 Hz, grillos a 26 Hz); lo periódico y rápido se oye como un motor |

## Ancestral: cuidado con los graves

La primera mezcla ancestral tenía casi toda la energía por debajo de 100 Hz, entre el
tambor, el zumbido y el rumor del fuego. Es lo que produce la presión de "retumba el
oído" con auriculares. Se bajaron el tambor (0,55 → 0,38) y el zumbido (0,12 → 0,06), y
el rumor del fuego se cortó por debajo de 110 Hz. Aun así el tambor lleva graves por
naturaleza: es la capa a vigilar en la escucha.

## Reglas que salieron de esto

- **Nada periódico y rápido en un fondo.** Si se repite más de una vez por segundo, suena a máquina.
- **Nada agudo al frente.** Lo que pasa de ~5 kHz va bajo, lejano o no va.
- **Nada grave de más.** Los graves sostenidos presionan el oído: lo que está por debajo
  de 100 Hz se mide en cada mezcla.
- **Las mediciones no reemplazan la escucha.** Pico, clipping y RMS daban bien en la
  versión que sobresaltaba.
