"""La tendencia del liderazgo: el contexto del mes pegado al relevo, y el dominio como su opuesto.

Fixtures locales, nunca producción. Los `wordle_id` son de una temporada inventada.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from resumen import RACHA_PARA_DOMINIO, bloque_relevo, historia_del_liderazgo

TEMPORADA = "2099-01"

#: Una temporada numerada solo cuenta los días laborables con al menos cinco jugadores (`seasons`), así que
#: cada jornada del fixture lleva tres jugadores de relleno que nunca pelean por la cabeza.
RELLENO = {"Dani": 5, "Eva": 5, "Fran": 5}

#: Laborables reales de enero de 2099 — el filtro de `es_laborable` los comprueba de verdad. Hacen falta
#: bastantes: `_del_ciclo` elige la frase por `jornada % len(registro)`, así que para ejercitar una frase
#: concreta hay que llegar a su jornada.
DIAS = ["2099-01-05", "2099-01-06", "2099-01-07", "2099-01-08", "2099-01-09",
        "2099-01-12", "2099-01-13", "2099-01-14", "2099-01-15", "2099-01-16",
        "2099-01-19", "2099-01-20", "2099-01-21", "2099-01-22", "2099-01-23",
        "2099-01-26", "2099-01-27", "2099-01-28", "2099-01-29", "2099-01-30"]


def _fila(jornada: int, nombre: str, score: int, dia: str) -> dict:
    return {
        "wordle_id": jornada,
        "player_name": nombre,
        "slack_user_id": nombre,
        "score": score,
        "date": dia,
        "pattern": None,
    }


def _temporada(notas_por_jornada: list[dict[str, int]]) -> list[dict]:
    """Una entrada por jornada con `{jugador: score}`; el relleno se añade solo."""
    return [
        _fila(j, quien, score, DIAS[j - 1])
        for j, notas in enumerate(notas_por_jornada, start=1)
        for quien, score in {**notas, **RELLENO}.items()
    ]


#: Ana manda las cuatro primeras, la pierde en la quinta y en la sexta la coge Cris.
GUION = [
    {"Ana": 1, "Bea": 2, "Cris": 3},
    {"Ana": 1, "Bea": 2, "Cris": 3},
    {"Ana": 1, "Bea": 2, "Cris": 3},
    {"Ana": 1, "Bea": 2, "Cris": 3},
    {"Ana": 7, "Bea": 2, "Cris": 3},
    {"Ana": 7, "Bea": 7, "Cris": 1},
]


# @scenarios el-dominio-en-cabeza-se-cuenta
def test_el_dominio_se_dice_cuando_nadie_le_quita_la_cabeza():
    manda_ana = [GUION[0]] * RACHA_PARA_DOMINIO
    filas = _temporada(manda_ana)
    linea = bloque_relevo(filas, TEMPORADA, RACHA_PARA_DOMINIO)
    assert "Ana" in linea
    assert str(RACHA_PARA_DOMINIO) in linea, f"no dice cuántas jornadas lleva: {linea!r}"


# @scenarios el-dominio-en-cabeza-se-cuenta
def test_el_dominio_no_se_dice_de_dos_empatados():
    filas = _temporada([{"Ana": 3, "Bea": 3}] * RACHA_PARA_DOMINIO)
    historia = historia_del_liderazgo(filas, TEMPORADA, RACHA_PARA_DOMINIO)
    assert len(historia["lideres"]) == 2, "el fixture debe tener la cabeza compartida"
    assert historia["racha"] >= RACHA_PARA_DOMINIO, "el fixture debe llegar a la racha"
    assert bloque_relevo(filas, TEMPORADA, RACHA_PARA_DOMINIO) == ""


# @scenarios el-dominio-en-cabeza-se-cuenta
def test_el_dominio_cuenta_jornadas_seguidas_y_no_el_total():
    """Ana lidera 5 jornadas, la pierde, la recupera: al recuperarla lleva 1 seguida, no 6.

    Es el defecto que traía la primera versión: publicaba «lleva 7 jornadas mandando» mezclando el total
    acumulado con la racha, y lo decía de quien ya no mandaba.
    """
    filas = _temporada(GUION[:5])
    historia = historia_del_liderazgo(filas, TEMPORADA, 5)
    assert historia["jornadas"]["Ana"] >= 4, f"Ana acumula jornadas arriba: {historia}"
    assert historia["racha"] == 1, f"la racha se reinicia con el cambio: {historia}"
    assert "jornadas seguidas" not in bloque_relevo(filas, TEMPORADA, 5)


# @scenarios la-tendencia-del-mes-acompana-al-relevo
def test_con_un_solo_cambio_el_relevo_no_lleva_tendencia():
    filas = _temporada(GUION[:5])
    historia = historia_del_liderazgo(filas, TEMPORADA, 5)
    assert historia["cambios"] == 1, f"el fixture debe tener un solo cambio: {historia}"
    linea = bloque_relevo(filas, TEMPORADA, 5)
    assert linea, "el relevo sí se anuncia"
    assert "cambios" not in linea, f"no debe añadir tendencia con un cambio: {linea!r}"


# @scenarios la-tendencia-del-mes-acompana-al-relevo
def test_con_varios_cambios_el_relevo_lleva_el_recuento_del_mes():
    filas = _temporada(GUION)
    historia = historia_del_liderazgo(filas, TEMPORADA, 6)
    assert historia["cambios"] == 2, f"el fixture debe tener dos cambios: {historia}"
    linea = bloque_relevo(filas, TEMPORADA, 6)
    assert "2" in linea, f"debe decir cuántos cambios van: {linea!r}"


# @scenarios la-tendencia-del-mes-acompana-al-relevo
def test_el_reparto_nombra_a_los_dos_del_relevo_y_no_al_top_acumulado():
    """Con un tercero que acumula más jornadas que quien acaba de coger la cabeza, el reparto sigue siendo
    de los dos del relevo. Es el defecto que se vio simulando: el top-2 acumulado dejaba fuera al nuevo líder.
    """
    filas = _temporada(GUION)
    historia = historia_del_liderazgo(filas, TEMPORADA, 6)
    assert historia["lideres"] == ["Cris"], f"Cris coge la cabeza en la última: {historia}"
    assert historia["jornadas"]["Ana"] > historia["jornadas"]["Cris"], (
        f"Ana acumula más jornadas arriba que el nuevo líder: {historia}")
    linea = bloque_relevo(filas, TEMPORADA, 6)
    assert "Cris" in linea, f"el nuevo líder debe estar en el reparto: {linea!r}"
    assert "Ana" not in linea, f"el reparto no es el top acumulado: {linea!r}"


# @scenarios la-tendencia-del-mes-acompana-al-relevo
def test_el_recuento_cuenta_solo_los_relevos_anunciables():
    """El número que se publica es el de relevos **anunciados**, no el de veces que cambió la cabeza.

    Con datos reales de agosto la primera versión decía «3 cambios de cabeza» el día del primer relevo
    anunciado, porque contaba también el empate alternando entre dos igualados —que a propósito no se
    anuncia—. El grupo habría leído un número que no corresponde a nada que se le haya contado.
    """
    # Ana y Bea se alternan la cabeza empatando, que es lo que `hay_relevo` no anuncia.
    alterna = [
        {"Ana": 1, "Bea": 3},  # manda Ana
        {"Ana": 3, "Bea": 1},  # empatan
        {"Ana": 1, "Bea": 3},
        {"Ana": 3, "Bea": 1},
        {"Ana": 3, "Bea": 1},
    ]
    filas = _temporada(alterna)
    anunciados = sum(1 for j in range(1, 6) if "Relevo" in bloque_relevo(_temporada(alterna[:j]), TEMPORADA, j))
    historia = historia_del_liderazgo(filas, TEMPORADA, 5)
    assert historia["cambios"] == anunciados, (
        f"cuenta {historia['cambios']} y se anunciaron {anunciados}: {historia}")


# @scenarios la-tension-sube-cuando-el-empate-se-repite
def test_la_tension_escala_con_las_veces_que_se_repite_el_empate():
    """Tres registros distintos según cuántas veces haya empatado la misma pareja.

    Escala por **recurrencia y no por duración**: medido, los empates consecutivos casi no existen (los cinco
    de agosto duran una jornada), pero la misma pareja llega a empatar cuatro veces en jornadas salteadas.
    """
    from resumen import EMPATES_PARA_INSISTIR, EMPATES_PARA_TENSION, bloque_rivalidad

    # Empates **salteados**: se intercambian las notas, así que las sumas coinciden en las jornadas pares y
    # en las impares manda Ana. La media es acumulada, así que alternar notas sin más no vuelve a igualarlas.
    guion = [{"Ana": 1, "Bea": 5} if j % 2 else {"Ana": 5, "Bea": 1} for j in range(1, 9)]

    lineas = []
    for j in range(1, len(guion) + 1):
        historia = historia_del_liderazgo(_temporada(guion[:j]), TEMPORADA, j)
        if len(historia["lideres"]) == 2:
            lineas.append((historia["veces_esta_cabeza"], bloque_rivalidad(_temporada(guion[:j]), TEMPORADA, j)))

    veces = [v for v, _ in lineas]
    assert veces[: EMPATES_PARA_TENSION] == list(range(1, EMPATES_PARA_TENSION + 1)), (
        f"el fixture debe encadenar empates salteados: {veces}")
    primera, insistente, tensa = lineas[0][1], lineas[EMPATES_PARA_INSISTIR - 1][1], lineas[EMPATES_PARA_TENSION - 1][1]
    assert primera != insistente != tensa, "los tres niveles deben decir cosas distintas"
    assert str(EMPATES_PARA_INSISTIR) in insistente, f"el segundo empate dice cuántos van: {insistente!r}"
    assert str(EMPATES_PARA_TENSION) in tensa, f"el cuarto empate dice cuántos van: {tensa!r}"


# @scenarios la-pelea-por-el-primer-puesto-se-cuenta
def test_la_rivalidad_no_publica_el_punto_doble():
    """«separan a Claire de Andrés R.. Nada» es lo que salía antes: los nombres acaban en punto.

    **El test tiene que llegar a la frase.** `_del_ciclo` elige por `jornada % len(registro)`, y la primera
    versión de este test miraba las jornadas 1 y 2, que no seleccionan ninguna de las nueve frases que ponen
    el nombre justo antes del punto: quitar el colapso no lo ponía en rojo. Los índices afectados son 2, 4 y 6
    de `RIVALIDAD_PELEA`, 4, 5 y 7 de `RIVALIDAD_EMPATE_OTRA_VEZ` y 0, 4 y 6 de `RIVALIDAD_EMPATE_TENSION`.
    """
    from resumen import bloque_rivalidad

    def revisa(guion: list[dict[str, int]], hasta: int) -> list[str]:
        vistas = []
        for j in range(1, hasta + 1):
            linea = bloque_rivalidad(_temporada(guion[:j]), TEMPORADA, j)
            if linea:
                assert ".." not in linea, f"punto doble en la jornada {j}: {linea!r}"
                vistas.append(linea)
        return vistas

    # Empatados todas las jornadas menos la última, donde Bea se descuelga por un solo punto en catorce
    # jornadas (0,07 de diferencia): así se recorren el registro de tensión y el de pelea.
    empatados = [{"Ana R.": 3, "Bea H.": 3} for _ in range(13)] + [{"Ana R.": 3, "Bea H.": 4}]
    # Empates **salteados**, para que en la jornada 4 lleven solo 2 y toque el registro insistente.
    salteados = [{"Ana R.": 1, "Bea H.": 5} if j % 2 else {"Ana R.": 5, "Bea H.": 1} for j in range(1, 9)]

    lineas = revisa(empatados, 14) + revisa(salteados, 8)
    assert any("Bea H." in linea and "Ana R." in linea for linea in lineas), "los nombres deben salir"
    assert len(lineas) >= 10, f"pocas frases ejercitadas: {len(lineas)}"


# @scenarios los-ausentes-se-nombran-por-orden-de-clasificacion
def test_los_ausentes_se_nombran_por_orden_de_clasificacion():
    """**Los tres nombrados son los tres mejor situados que faltan**, no los tres primeros del alfabeto.

    Antes se ordenaba con `sorted()` sobre los nombres, así que quien tuviera la inicial más baja salía
    nombrado y el líder ausente podía quedar escondido en «y otros 3». Decisión del dueño: la ausencia de
    quien va primero es más noticia.
    """
    from types import SimpleNamespace

    from resumen import AUSENTES_NOMBRADOS, _linea_de_ausentes

    # Zoe va primera y Ana última: alfabéticamente sería justo al contrario.
    por_puesto = ["Zoe", "Yago", "Xan", "Bea", "Ana"]
    nombres = {j: j for j in por_puesto}
    # Nadie ha publicado: faltan todos, así que la coleta se activa.
    senales = SimpleNamespace(publicacion={})
    assert _linea_de_ausentes(senales, por_puesto, nombres, 1) == "", "sin señales no se afirma nada"

    # Con señales de otro jugador, los cinco de la tabla cuentan como ausentes.
    senales = SimpleNamespace(publicacion={"Otro": 1})
    linea = _linea_de_ausentes(senales, por_puesto, nombres, 1)
    nombrados = [n for n in por_puesto if n in linea]
    assert nombrados == por_puesto[:AUSENTES_NOMBRADOS], (
        f"deben salir los {AUSENTES_NOMBRADOS} mejor clasificados y en su orden: {linea!r}")
    assert "Ana" not in linea, f"el último clasificado no se nombra: {linea!r}"
