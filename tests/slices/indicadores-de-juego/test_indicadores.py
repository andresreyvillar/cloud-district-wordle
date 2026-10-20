"""Los indicadores de juego, de `indicadores-de-juego`.

Pack: `feat-indicadores-de-juego`. Sin red: la lista de soluciones es sintética y entra por parámetro. Los
jugadores son sintéticos: el repositorio es público.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "tools"))

import indicadores as ind  # noqa: E402

# ── Una lista de soluciones sintética ─────────────────────────────────────────────────────────────────
#
# Treinta palabras de cinco letras; la jornada `i` tiene la solución `PALABRAS[i - 1]`. Dos de ellas con tilde y
# una con Ñ, como la lista de verdad.
PALABRAS = [
    "casar", "casas", "casan", "perro", "gatos", "lápiz", "señal", "mundo", "verde", "nubes",
    "plaza", "tigre", "cuero", "salto", "ruido", "brisa", "llave", "monte", "barco", "fuego",
    "papel", "dulce", "golpe", "huevo", "jamón", "karma", "limón", "nieve", "ostra", "quema",
]
FUTURA = "zzzzz"


def lista(hasta_futura: bool = True) -> list[dict]:
    entradas = [{"id": i + 1, "solution": w} for i, w in enumerate(PALABRAS)]
    if hasta_futura:
        entradas.append({"id": len(PALABRAS) + 1, "solution": FUTURA})
    return entradas


# ── Las piezas puras ──────────────────────────────────────────────────────────────────────────────────

# @scenarios la-suerte-son-aciertos-reales-menos-esperados
def test_los_colores_siguen_las_reglas_del_juego_con_tildes_y_letras_repetidas():
    # La segunda «e» de «pelea» es verde y la primera no cuenta: «papel» solo tiene una.
    assert ind.colores("pelea", "papel") == "G.YGY"
    # La tilde no cuenta al jugar; la Ñ es otra letra.
    assert ind.colores(ind.normaliza("lápiz"), ind.normaliza("lapiz")) == "GGGGG"
    assert ind.colores(ind.normaliza("señal"), ind.normaliza("senal")) == "GG.GG"


# @scenarios la-suerte-son-aciertos-reales-menos-esperados
def test_un_dos_de_seis_con_muchas_candidatas_suma_suerte_y_un_fallo_resta():
    dos_de_seis = ind.suerte_de_partida([".Y...", "GGGGG"], [100, 34])
    fallo = ind.suerte_de_partida([".Y..."] * 6, [100, 20, 5, 3, 2, 2])

    assert dos_de_seis == pytest.approx((0 - 1 / 100) + (1 - 1 / 34))
    assert fallo == pytest.approx(-(1 / 100 + 1 / 20 + 1 / 5 + 1 / 3 + 1 / 2 + 1 / 2))
    assert fallo < 0 < dos_de_seis


# @scenarios acertar-sabiendo-la-palabra-no-es-suerte
def test_el_intento_ganador_con_una_sola_candidata_suma_cero():
    sabiendo = ind.suerte_de_partida(["Y....", ".GG..", "GGGGG"], [100, 5, 1])
    sin_el_ultimo = ind.suerte_de_partida(["Y....", ".GG.."], [100, 5])

    assert sabiendo == pytest.approx(sin_el_ultimo), "el intento con una candidata no suma ni resta"


# @scenarios la-suerte-son-aciertos-reales-menos-esperados
def test_las_candidatas_antes_de_cada_intento_salen_de_los_colores():
    universo = ["casar", "casas", "casan", "perro"]

    # Tras «GGGG.», con «casas» o con «casan» como intento, quedan dos: la respuesta y la otra.
    assert ind.candidatas_antes(["GGGG.", "GGGGG"], "casar", universo, semilla=1) == [4, 2]
    assert ind.candidatas_antes(["GGGGG"], "casar", universo, semilla=1) == [4]


# @scenarios una-cuadricula-incompatible-se-descarta
def test_una_fila_que_ninguna_palabra_produce_descarta_la_partida():
    assert ind.candidatas_antes(["YYYYY", "GGGGG"], "casar", ["casar", "casas", "perro"], semilla=1) is None


# @scenarios una-cuadricula-incompatible-se-descarta
@pytest.mark.parametrize("filas", [
    ["GGGGY"],                      # una sola fila imposible: la última también se valida
    ["....Y", "GGGGY"],             # última fila imposible contra la respuesta
    ["GGGGG", "GGGGG"],             # un acierto a mitad de partida
    ["abc", "GGGGG"],               # caracteres que no son colores
    ["GGGG", "GGGGG"],              # fila corta
])
def test_toda_fila_ilegible_descarta_la_partida(filas):
    assert ind.candidatas_antes(filas, "casar", ["casar", "casas", "casan", "perro"], semilla=1) is None


# @scenarios sin-lista-no-hay-indicadores, una-cuadricula-incompatible-se-descarta
def test_una_solucion_que_no_es_de_cinco_letras_no_tumba_la_materializacion():
    """Una caída aquí bloquearía todas las instantáneas: la lista viene de fuera y puede cambiar de forma."""
    from seasons import instantanea

    rara = lista() + [{"id": 32, "solution": "sol"}, "no-es-un-dict", {"id": "x"}]
    filas = temporada() + [fila("U_ANA", 16, ["perro", PALABRAS[15]]) | {"wordle_id": 32, "date": "2026-11-09"}]

    carga = instantanea(filas, "2026-11", soluciones=rara)

    assert carga["clasificacion"], "la instantánea sale"
    assert "indicadores" in carga, "las entradas raras se ignoran; las buenas cuentan"


# @scenarios sin-lista-no-hay-indicadores
def test_si_los_indicadores_fallan_la_instantanea_sale_sin_ellos(monkeypatch):
    import indicadores
    from seasons import instantanea

    def roto(*_a, **_k):
        raise RuntimeError("cualquier fallo del cálculo")

    monkeypatch.setattr(indicadores, "indicadores", roto)
    carga = instantanea(temporada(), "2026-11", soluciones=lista())

    assert "indicadores" not in carga
    assert carga["clasificacion"]


# @scenarios la-apertura-cuenta-cuantas-quedan-tras-cada-intento
def test_la_apertura_es_la_mediana_de_candidatas_tras_el_primer_y_el_segundo_intento():
    partidas = [
        {"candidatas": [30, 10, 2, 1]},
        {"candidatas": [30, 20, 4]},
        {"candidatas": [30, 40]},          # resuelta en 2: no tiene «tras el segundo»
        {"candidatas": [30]},              # resuelta a la primera: no tiene ninguna
    ]

    assert ind.apertura_de(partidas) == [20, 3]


# @scenarios el-acierto-mas-milagroso-es-el-de-mas-candidatas
def test_el_milagro_es_la_partida_con_mas_candidatas_y_el_empate_va_a_la_mas_antigua():
    partidas = [
        {"jornada": 12, "intentos": 3, "resuelta": True, "candidatas": [30, 9, 7]},
        {"jornada": 10, "intentos": 2, "resuelta": True, "candidatas": [30, 7]},
        {"jornada": 11, "intentos": 6, "resuelta": False, "candidatas": [30, 9, 9, 9, 9, 9]},
        {"jornada": 13, "intentos": 4, "resuelta": True, "candidatas": [30, 9, 2, 1]},
    ]

    assert ind.milagro_de(partidas) == {"jornada": 10, "intentos": 2, "candidatas": 7}
    assert ind.milagro_de([partidas[3]]) == {"jornada": 13, "intentos": 4, "candidatas": 1}
    assert ind.milagro_de([partidas[2]]) is None, "una partida fallada no tiene acierto"


# ── La temporada entera ───────────────────────────────────────────────────────────────────────────────

#: Cinco laborables de una temporada sintética, uno por jornada (las jornadas son ids de la lista). Sus respuestas
#: no son ninguna de las palabras de prueba: con una, la cuadrícula tendría un acierto a mitad de partida.
DIAS = {12: "2026-11-02", 13: "2026-11-03", 14: "2026-11-04", 15: "2026-11-05", 16: "2026-11-06"}
HASTA = 16
JUGADORES = ["U_ANA", "U_BEA", "U_CRIS", "U_DANI", "U_EVA"]


def fila(jugador, jornada, intentos_de_palabras):
    respuesta = ind.normaliza(PALABRAS[jornada - 1])
    filas = [ind.colores(ind.normaliza(w), respuesta) for w in intentos_de_palabras]
    resuelta = filas[-1] == "GGGGG"
    return {
        "slack_user_id": jugador, "player_name": jugador[2:].title(), "wordle_id": jornada,
        "score": len(filas) if resuelta else 7, "date": DIAS[jornada], "pattern": "/".join(filas),
    }


def temporada(sin_cuadricula=()):
    filas = []
    for jornada in DIAS:
        respuesta = PALABRAS[jornada - 1]
        for i, jugador in enumerate(JUGADORES):
            if (jugador, jornada) in sin_cuadricula:
                filas.append({**fila(jugador, jornada, ["perro", respuesta]), "pattern": None})
                continue
            # Ana acierta a la segunda; los demás tantean más.
            intentos = ["perro", respuesta] if jugador == "U_ANA" else ["perro", "gatos", "plaza"][: 1 + i % 3] + [respuesta]
            filas.append(fila(jugador, jornada, intentos))
    return filas


# @scenarios la-eficiencia-se-compara-con-el-optimo-y-con-el-grupo, el-acierto-mas-milagroso-es-el-de-mas-candidatas
def test_la_eficiencia_lleva_la_media_del_jugador_la_del_grupo_y_la_del_solucionador():
    resultado = ind.indicadores(temporada(), "2026-11", lista(), hasta=HASTA)

    ana = resultado["jugadores"]["U_ANA"]
    assert resultado["referencia"] == ind.MEDIA_DEL_SOLUCIONADOR == 3.41
    assert ana["media"] == 2.0
    assert resultado["grupo"]["media"] > ana["media"]
    assert ana["partidas"] == 5
    assert ana["milagro"]["intentos"] == 2
    assert set(ana) >= {"media", "apertura", "suerte", "suerte_por_partida", "milagro", "partidas"}


# @scenarios con-pocas-partidas-no-hay-conclusiones, una-cuadricula-incompatible-se-descarta
def test_por_debajo_del_minimo_no_hay_cifras_sino_cuantas_faltan():
    sin = {("U_BEA", 12), ("U_BEA", 13), ("U_BEA", 14)}

    bea = ind.indicadores(temporada(sin_cuadricula=sin), "2026-11", lista(), hasta=HASTA)["jugadores"]["U_BEA"]

    assert bea == {"partidas": 2, "faltan": ind.MINIMO_DE_PARTIDAS - 2}


# @scenarios el-calculo-es-determinista
def test_el_calculo_no_depende_del_proceso_ni_de_la_semilla_de_hash():
    """Llamar dos veces en el mismo proceso solo prueba idempotencia. La reproducibilidad entre ejecuciones del
    cron se prueba en procesos distintos con `PYTHONHASHSEED` distinto: un sorteo sembrado con `hash()` cambia."""
    programa = (
        "import json, sys; sys.path.insert(0, 'tools'); sys.path.insert(0, 'tests/slices/indicadores-de-juego');"
        "import test_indicadores as t, indicadores as ind;"
        "print(json.dumps(ind.indicadores(t.temporada(), '2026-11', t.lista(), hasta=t.HASTA), sort_keys=True))"
    )
    salidas = {
        subprocess.run([sys.executable, "-B", "-c", programa], cwd=RAIZ, capture_output=True, text=True,
                       env={**os.environ, "PYTHONHASHSEED": semilla}, check=True).stdout
        for semilla in ("1", "2", "3")
    }

    assert len(salidas) == 1, "tres procesos, tres resultados distintos"


# @scenarios el-calculo-es-determinista
def test_el_sorteo_se_siembra_con_la_jornada(monkeypatch):
    """La regla, no el síntoma: con un fixture pequeño cualquier sorteo da las mismas medianas, así que comparar
    salidas no caza una semilla que cambie entre ejecuciones. La semilla tiene que ser la jornada, en texto."""
    import random as azar

    semillas = []
    original = azar.Random

    class Espia(original):
        def __init__(self, semilla=None):
            semillas.append(semilla)
            super().__init__(semilla)

    monkeypatch.setattr(ind.random, "Random", Espia)
    ind.indicadores(temporada(), "2026-11", lista(), hasta=HASTA)

    assert semillas, "las candidatas se estiman con un sorteo"
    assert set(semillas) == {f"jornada-{j}" for j in DIAS}, semillas[:5]


# @scenarios la-instantanea-no-lleva-palabras
def test_la_instantanea_no_contiene_palabras_ni_pasa_de_la_ultima_jornada():
    leidas = []

    class Entrada(dict):
        def __getitem__(self, clave):
            if clave == "solution":
                leidas.append(dict.__getitem__(self, "id"))
            return dict.__getitem__(self, clave)

        def get(self, clave, defecto=None):
            return self[clave] if clave in self else defecto

    entradas = [Entrada(e) for e in lista()]
    texto = json.dumps(ind.indicadores(temporada(), "2026-11", entradas, hasta=HASTA), ensure_ascii=False)

    for palabra in PALABRAS + [FUTURA]:
        assert ind.normaliza(palabra) not in texto and palabra not in texto, palabra
    assert leidas and max(leidas) <= HASTA, f"se leyó una solución posterior a la última jornada: {max(leidas)}"


# @scenarios sin-lista-no-hay-indicadores
def test_sin_lista_la_instantanea_sale_sin_el_bloque():
    from seasons import instantanea

    con = instantanea(temporada(), "2026-11", soluciones=lista())
    sin = instantanea(temporada(), "2026-11", soluciones=None)

    assert "indicadores" in con
    assert "indicadores" not in sin
    assert sin["clasificacion"], "el resto de la instantánea sale igual"


# @scenarios sin-lista-no-hay-indicadores
def test_si_la_descarga_o_el_descifrado_fallan_el_borde_devuelve_nada(monkeypatch):
    """El borde que falla se prueba haciéndolo fallar, no pasando `None` a la función pura."""
    import materialize_seasons
    import palabra

    monkeypatch.setattr(palabra, "descarga_soluciones", lambda *a, **k: None)
    assert materialize_seasons.leer_soluciones() is None

    def roto(_):
        raise ValueError("formato nuevo")

    monkeypatch.setattr(palabra, "descarga_soluciones", lambda *a, **k: b"basura")
    monkeypatch.setattr(palabra, "descifra", roto)
    assert materialize_seasons.leer_soluciones() is None
