"""Escenarios de `clasificacion-de-temporada` (Fase 2 — TDD rojo).

Fixtures a mano, con el mínimo de filas que hace verdadera cada condición. Las fechas se calculan porque
agosto de 2026 empieza en sábado: numerar del 1 en adelante metería fines de semana en la temporada.
"""

from __future__ import annotations

import calendar
import datetime

import pytest

MOTIVO = "TDD rojo — tools/standings.py no existe todavía"

MES = "2026-09"  # posterior al límite de temporadas: es una temporada numerada


def laborables(mes: str = MES) -> list[int]:
    año, m = (int(p) for p in mes.split("-"))
    return [
        d
        for d in range(1, calendar.monthrange(año, m)[1] + 1)
        if datetime.date(año, m, d).isoweekday() <= 5
    ]


def r(jugador: str, jornada: int, intentos: int, dia_indice: int, mes: str = MES) -> dict:
    return {
        "slack_user_id": f"U_{jugador.upper()}",
        "player_name": jugador,
        "wordle_id": jornada,
        "score": intentos,
        "date": f"{mes}-{laborables(mes)[dia_indice]:02d}",
    }


def jornada(indice: int, base: int, scores: dict[str, int]) -> list[dict]:
    """Una jornada con un resultado por jugador. Cinco o más para que el día cuente."""
    return [r(nombre, base + indice, intentos, indice) for nombre, intentos in scores.items()]


RELLENO = {"r1": 4, "r2": 4, "r3": 4, "r4": 4}


# @scenarios clasificacion-ordena-por-media-imputada
def test_la_tabla_se_ordena_por_media_imputada_de_menor_a_mayor():
    from tools.standings import clasificacion

    filas = jornada(0, 1600, {"bueno": 2, "medio": 4, "malo": 6, **RELLENO})
    filas += jornada(1, 1600, {"bueno": 2, "medio": 4, "malo": 6, **RELLENO})

    tabla = clasificacion(filas, MES)
    orden = [fila["nombre"] for fila in tabla]

    # los cuatro de relleno empatan con "medio" en 4,0, así que solo el primero y el último son fijos
    assert orden[0] == "bueno"
    assert orden[-1] == "malo"
    # Los puestos ya NO son correlativos: quien empata comparte número y el siguiente salta
    # (slice `empates-comparten-puesto`). Lo que sigue en pie es que no bajan nunca al recorrer la lista.
    posiciones = [fila["posicion"] for fila in tabla]
    assert posiciones[0] == 1
    assert posiciones == sorted(posiciones)
    assert max(posiciones) <= len(tabla)
    medias = [fila["media_temporada"] for fila in tabla]
    assert medias == sorted(medias)


# @scenarios faltar-nunca-mejora-la-media
def test_faltar_nunca_mejora_la_media():
    """Sin el `max(dificultad, media_personal)`, a quien tiene mala media le convenía ausentarse."""
    from tools.standings import clasificacion

    # dos jornadas fáciles para el grupo (media 3) y un jugador cuya media es 6
    facil = {"r1": 3, "r2": 3, "r3": 3, "r4": 3, "r5": 3}
    jugando = jornada(0, 1600, {"malo": 6, **facil}) + jornada(1, 1600, {"malo": 6, **facil})
    faltando = jornada(0, 1600, {"malo": 6, **facil}) + jornada(1, 1600, facil)

    con = next(f for f in clasificacion(jugando, MES) if f["nombre"] == "malo")
    sin = next(f for f in clasificacion(faltando, MES) if f["nombre"] == "malo")

    assert sin["media_temporada"] >= con["media_temporada"], "faltar le ha mejorado la media"


# @scenarios ausencia-en-dia-dificil-penaliza-mas
def test_la_ausencia_en_un_dia_dificil_penaliza_mas_que_en_uno_facil():
    from tools.standings import clasificacion

    facil = {"r1": 3, "r2": 3, "r3": 3, "r4": 3, "r5": 3}
    duro = {"r1": 6, "r2": 6, "r3": 6, "r4": 6, "r5": 6}

    # jornada 0 fácil, jornada 1 dura, jornada 2 la juegan los dos con un 4.
    # `ausente_el_duro` no aparece en la jornada 1; `ausente_el_facil` no aparece en la 0.
    filas = jornada(0, 1600, {"ausente_el_facil_no": 4, "ausente_el_duro": 4, **facil})
    filas += jornada(1, 1600, {"ausente_el_facil": 4, **duro})
    filas += jornada(2, 1600, {"ausente_el_facil": 4, "ausente_el_duro": 4, **facil})

    tabla = {f["nombre"]: f for f in clasificacion(filas, MES)}

    assert tabla["ausente_el_duro"]["media_temporada"] > tabla["ausente_el_facil"]["media_temporada"], (
        "faltar el día duro tiene que penalizar más que faltar el fácil"
    )


# @scenarios jugar-poco-no-da-ventaja
def test_jugar_pocos_dias_con_buena_media_no_adelanta_a_quien_juega_todos():
    """El diagnóstico que justifica el modelo: hoy el ranking lo gana quien juega poco."""
    from tools.standings import clasificacion

    base = {"r1": 4, "r2": 4, "r3": 4, "r4": 4, "r5": 4}
    filas: list[dict] = []
    for i in range(5):
        scores = {"constante": 3, **base}
        if i == 0:
            scores["esporadico"] = 2  # una sola partida, y buenísima
        filas += jornada(i, 1600, scores)

    tabla = {f["nombre"]: f for f in clasificacion(filas, MES)}

    assert tabla["esporadico"]["media_jugada"] < tabla["constante"]["media_jugada"], "el fixture no vale"
    assert tabla["constante"]["posicion"] < tabla["esporadico"]["posicion"]


# @scenarios empate-se-rompe-por-participacion
def test_el_empate_en_media_lo_rompe_quien_ha_jugado_mas_dias():
    from tools.standings import clasificacion

    # El empate hay que construirlo con cuidado: el margen de 0,5 impide que quien falta iguale a quien
    # juega con la misma media, así que el que falta tiene que ser MEJOR en lo que juega.
    #
    #   jornada 0 (5 jugadores):  zoe 4 · ana 3 · r1..r3 4                    → media 3,8
    #   jornada 1 (6 jugadores):  zoe 4 · r1 4 · r2 5 · r3 5 · r4 5 · r5 4     → media 4,5
    #
    #   zoe: (4 + 4) / 2                                       = 4,0
    #   ana: (3 + min(max(4,5 ; 3) + 0,5 ; 7)) / 2 = (3 + 5)/2 = 4,0   ← empate
    #
    # Los nombres NO son decorativos: "ana" va antes que "zoe" alfabéticamente, y "ana" es la que jugó
    # menos. Así, si el desempate por participación desapareciese, el orden alfabético daría el resultado
    # CONTRARIO y el test caería. Con los nombres al revés el test pasaba por casualidad, y un mutante que
    # quitaba el desempate sobrevivía.
    filas = jornada(0, 1600, {"zoe": 4, "ana": 3, "r1": 4, "r2": 4, "r3": 4})
    filas += jornada(1, 1600, {"zoe": 4, "r1": 4, "r2": 5, "r3": 5, "r4": 5, "r5": 4})

    tabla = clasificacion(filas, MES)
    orden = [f["nombre"] for f in tabla]
    posiciones = {f["nombre"]: f["posicion"] for f in tabla}
    medias = {f["nombre"]: f["media_temporada"] for f in tabla}
    jugados = {f["nombre"]: f["jugados"] for f in tabla}

    assert medias["zoe"] == medias["ana"], f"el fixture no produce empate: {medias}"
    assert jugados["zoe"] > jugados["ana"]
    # El desempate ORDENA la lista, y ya no reparte puestos: empatar en la media es haber hecho la misma
    # temporada, y quien juega un día más no la ha hecho mejor —si esa participación tiene que valer, lo
    # hace la imputación, que ya está dentro de la media. Cambio de regla del slice
    # `empates-comparten-puesto`, no un test debilitado: el desempate se sigue comprobando, sobre el orden.
    assert orden.index("zoe") < orden.index("ana"), "el desempate por participación no ordena"
    assert posiciones["zoe"] == posiciones["ana"], "empatados en media, mismo puesto"


# @scenarios la-tabla-hace-auditable-la-imputacion
def test_cada_fila_publica_lo_jugado_lo_imputado_y_el_detalle_por_jornada():
    from tools.standings import clasificacion

    base = {"r1": 4, "r2": 4, "r3": 4, "r4": 4, "r5": 4}
    filas = jornada(0, 1600, {"parcial": 3, **base}) + jornada(1, 1600, base)

    fila = next(f for f in clasificacion(filas, MES) if f["nombre"] == "parcial")

    assert fila["jugados"] == 1
    assert fila["dias"] == 2
    assert fila["media_jugada"] == 3.0
    assert fila["media_temporada"] > fila["media_jugada"], "la ausencia tiene que pesar"
    assert [d["imputado"] for d in fila["por_dia"]] == [False, True]
    assert all("jornada" in d and "intentos" in d for d in fila["por_dia"])


# @scenarios temporada-sin-dias-lo-dice
def test_una_temporada_sin_dias_validos_no_da_clasificacion():
    from tools.standings import clasificacion

    # tres jugadores: por debajo de la muestra mínima, así que el día no cuenta
    filas = jornada(0, 1600, {"a": 3, "b": 4, "c": 5})

    assert clasificacion(filas, MES) == []


# @scenarios calculo-determinista
def test_el_calculo_no_depende_del_orden_de_las_filas():
    from tools.standings import clasificacion

    filas = jornada(0, 1600, {"a": 2, "b": 4, "c": 6, "r1": 4, "r2": 4})
    filas += jornada(1, 1600, {"a": 3, "b": 5, "r1": 4, "r2": 4, "r3": 4})

    assert clasificacion(filas, MES) == clasificacion(list(reversed(filas)), MES)


# @scenarios la-vista-dice-cuando-se-calculo
def test_la_instantanea_trae_la_clasificacion_y_el_contexto_de_la_vista():
    from tools.seasons import instantanea

    base = {"r1": 4, "r2": 4, "r3": 4, "r4": 5, "r5": 3}
    filas = jornada(0, 1600, {"lider": 2, **base}) + jornada(1, 1600, {"lider": 3, **base})

    carga = instantanea(filas, MES)

    assert carga["clasificacion"], "la vista necesita la tabla en la instantánea"
    assert carga["clasificacion"][0]["nombre"] == "lider"
    assert carga["dificultad"], "la vista pinta la dificultad por jornada"
    assert carga["mas_dificil"] and carga["mas_facil"]
    assert isinstance(carga["media_grupo"], float)


# @scenarios la-vista-dice-cuando-se-calculo
def test_la_carga_util_sigue_siendo_serializable():
    import json

    from tools.seasons import instantanea

    base = {"r1": 4, "r2": 4, "r3": 4, "r4": 5, "r5": 3}
    json.dumps(instantanea(jornada(0, 1600, {"lider": 2, **base}), MES))
