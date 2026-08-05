"""Escenarios de `medallas-en-el-resumen-diario` (Fase 2 — TDD rojo).

Fixtures construidos a mano, con el mínimo de filas que hace verdadera cada condición: así el test
explica el umbral en lugar de esconderlo. Nada de producción, nada de Slack.

La temporada y la jornada entran por parámetro: el cálculo no lee el reloj (§10 del protocolo).
"""

from __future__ import annotations

import calendar
import datetime

import pytest

MOTIVO = "TDD rojo — la regla de días laborables no está implementada todavía"

TEMPORADA = "2026-08"
#: cinco jugadores de relleno hacen que un día tenga muestra suficiente para medir su dificultad
RELLENO = ["r1", "r2", "r3", "r4", "r5"]


def _dias(mes: str, laborables: bool) -> list[int]:
    año, m = (int(parte) for parte in mes.split("-"))
    return [
        dia
        for dia in range(1, calendar.monthrange(año, m)[1] + 1)
        if (datetime.date(año, m, dia).isoweekday() <= 5) is laborables
    ]


def dia_laborable(n: int, mes: str = TEMPORADA) -> int:
    """El día del mes del n-ésimo laborable (n empieza en 0).

    Los fixtures que cuentan partidas necesitan días que cuenten: agosto de 2026 empieza en sábado, así
    que numerar del 1 al 15 metía cinco fines de semana en un fixture de "quince partidas".
    """
    return _dias(mes, laborables=True)[n]


def dia_de_finde(n: int, mes: str = TEMPORADA) -> int:
    """El día del mes del n-ésimo sábado o domingo (n empieza en 0)."""
    return _dias(mes, laborables=False)[n]


def r(jugador: str, wordle: int, score: int, mes: str = TEMPORADA, dia: int | None = None) -> dict:
    if dia is None:
        dia = dia_laborable(0, mes)
    return {"player_name": jugador, "wordle_id": wordle, "score": score, "date": f"{mes}-{dia:02d}"}


def jornada_con(
    wordle: int, scores_relleno: list[int], mes: str = TEMPORADA, dia: int | None = None
) -> list[dict]:
    """Un día con cinco jugadores de relleno, para fijar su dificultad media."""
    return [r(j, wordle, s, mes, dia) for j, s in zip(RELLENO, scores_relleno)]


# @scenarios medalla-nueva-se-anuncia
def test_la_medalla_alcanzada_en_esta_jornada_se_anuncia():
    from tools.badges import texto_de_medallas

    # la 15ª partida es la de la jornada 1614: ahí cruza el umbral de Fondista
    filas = [r("Fondista Total", 1600 + i, 4, dia=dia_laborable(i)) for i in range(15)]
    texto = texto_de_medallas(filas, TEMPORADA, jornada=1614)

    assert "Fondista Total" in texto
    assert "Fondista" in texto


# @scenarios medalla-ya-anunciada-no-se-repite
def test_una_medalla_ganada_ayer_no_se_repite_hoy():
    from tools.badges import texto_de_medallas

    filas = [r("Veterano", 1600 + i, 4, dia=dia_laborable(i)) for i in range(15)]
    filas.append(r("Veterano", 1615, 4, dia=dia_laborable(15)))   # una partida más, al día siguiente

    assert "Veterano" in texto_de_medallas(filas, TEMPORADA, jornada=1614)
    assert texto_de_medallas(filas, TEMPORADA, jornada=1615) == ""


# @scenarios sin-medallas-no-hay-seccion
def test_una_jornada_sin_novedades_no_produce_seccion():
    from tools.badges import texto_de_medallas

    filas = [r("Casual", 1600, 4), r("Casual", 1601, 5)]
    assert texto_de_medallas(filas, TEMPORADA, jornada=1601) == ""


# @scenarios umbral-exacto-otorga
def test_quince_partidas_exactas_otorgan_fondista():
    from tools.badges import medallas_de_temporada

    filas = [r("Justo", 1600 + i, 4, dia=dia_laborable(i)) for i in range(15)]
    assert "fondista" in medallas_de_temporada(filas, TEMPORADA)["Justo"]


# @scenarios umbral-por-debajo-no-otorga
def test_catorce_partidas_no_otorgan_fondista():
    from tools.badges import medallas_de_temporada

    filas = [r("Casi", 1600 + i, 4, dia=dia_laborable(i)) for i in range(14)]
    assert "fondista" not in medallas_de_temporada(filas, TEMPORADA).get("Casi", [])


# @scenarios medalla-nueva-se-anuncia, medalla-ya-anunciada-no-se-repite
def test_la_gesta_de_hoy_se_anuncia_y_la_de_ayer_no():
    from tools.badges import texto_de_medallas

    lunes, martes = dia_laborable(0), dia_laborable(1)
    filas = [r("Afortunada", 1610, 1, dia=lunes)] + jornada_con(1610, [4, 4, 5, 4, 4], dia=lunes)
    siguiente = jornada_con(1611, [3, 4, 4, 3, 4], dia=martes)
    hoy = texto_de_medallas(filas, TEMPORADA, jornada=1610)
    mañana = texto_de_medallas(filas + siguiente, TEMPORADA, jornada=1611)

    assert "Afortunada" in hoy
    assert "Afortunada" not in mañana


# @scenarios dia-imposible-exige-las-dos-condiciones
def test_ni_resolver_rapido_en_dia_facil_ni_lento_en_dia_duro_dan_la_medalla():
    from tools.badges import medallas_permanentes

    # día fácil (media 3.0) resuelto rápido → no cuenta
    facil = jornada_con(1620, [3, 3, 3, 3, 3], dia=dia_laborable(1)) + [
        r("Rapido", 1620, 3, dia=dia_laborable(1))
    ]
    # día duro (media 5.8) resuelto lento → no cuenta
    duro = jornada_con(1621, [6, 6, 6, 5, 6], dia=dia_laborable(2)) + [
        r("Lento", 1621, 6, dia=dia_laborable(2))
    ]

    permanentes = medallas_permanentes(facil + duro)
    assert "dia-imposible" not in permanentes.get("Rapido", [])
    assert "dia-imposible" not in permanentes.get("Lento", [])


# @scenarios dia-imposible-exige-las-dos-condiciones
def test_resolver_rapido_un_dia_duro_si_da_la_medalla():
    from tools.badges import medallas_permanentes

    duro = jornada_con(1622, [6, 6, 6, 6, 6], dia=dia_laborable(3)) + [
        r("Heroína", 1622, 4, dia=dia_laborable(3))
    ]
    assert "dia-imposible" in medallas_permanentes(duro)["Heroína"]


# @scenarios repeticion-se-cuenta
def test_la_misma_medalla_en_dos_temporadas_cuenta_dos_veces():
    from tools.badges import medallas_de_temporada

    julio = [r("Constante", 1500 + i, 4, mes="2026-07", dia=dia_laborable(i, "2026-07")) for i in range(15)]
    agosto = [r("Constante", 1600 + i, 4, mes="2026-08", dia=dia_laborable(i, "2026-08")) for i in range(15)]
    filas = julio + agosto

    assert "fondista" in medallas_de_temporada(filas, "2026-07")["Constante"]
    assert "fondista" in medallas_de_temporada(filas, "2026-08")["Constante"]


# @scenarios calculo-determinista
def test_el_calculo_no_depende_del_orden_ni_del_reloj():
    from tools.badges import medallas_de_temporada

    filas = [r("Orden", 1600 + i, 4, dia=dia_laborable(i)) for i in range(15)]
    directo = medallas_de_temporada(filas, TEMPORADA)
    invertido = medallas_de_temporada(list(reversed(filas)), TEMPORADA)

    assert directo == invertido
    assert medallas_de_temporada(filas, TEMPORADA) == directo


# @scenarios medalla-ya-anunciada-no-se-repite
def test_las_jornadas_posteriores_no_cuentan_como_ganadas_hoy():
    """El fixture tiene futuro a propósito.

    Sin datos posteriores a la jornada evaluada, comparar contra "todos los resultados" y contra
    "hasta hoy" da lo mismo, y un cálculo que mira el futuro pasa desapercibido. Con futuro, no.
    """
    from tools.badges import texto_de_medallas

    # cruza el umbral de Fondista en la jornada 1614, y sigue jugando después
    filas = [r("Adelantado", 1600 + i, 4, dia=dia_laborable(i)) for i in range(20)]

    # en la jornada 1605 todavía no la tiene: el mensaje no debe anunciarla
    assert texto_de_medallas(filas, TEMPORADA, jornada=1605) == ""
    # en la 1614 sí
    assert "Adelantado" in texto_de_medallas(filas, TEMPORADA, jornada=1614)
    # y en la 1615 ya no es novedad
    assert texto_de_medallas(filas, TEMPORADA, jornada=1615) == ""


# @scenarios dia-con-poca-muestra-no-cuenta
def test_un_dia_de_dos_jugadores_no_es_un_dia_dificil():
    """Con dos personas, una media de 6 no dice que el día fuera duro: dice que no hay datos."""
    from tools.badges import medallas_permanentes

    # media 5.5 — justo en el umbral del día imposible — con uno resolviendo en 4:
    # lo ÚNICO que impide la medalla es que solo hay dos jugadores.
    filas = [
        r("Solitario", 1630, 4, dia=dia_laborable(4)),
        r("Acompañante", 1630, 7, dia=dia_laborable(4)),
    ]
    assert "dia-imposible" not in medallas_permanentes(filas).get("Solitario", [])

    # y con muestra suficiente, la misma media sí la concede
    con_muestra = filas + [r(f"relleno{i}", 1630, 7, dia=dia_laborable(4)) for i in range(3)]
    assert "dia-imposible" in medallas_permanentes(con_muestra)["Solitario"]


# @scenarios partida-de-fin-de-semana-no-cuenta-para-umbrales
def test_una_partida_de_sabado_no_cuenta_para_el_umbral():
    """Quince partidas de las que una es de sábado son catorce que cuentan."""
    from tools.badges import medallas_de_temporada

    filas = [r("Casi Fondista", 1600 + i, 4, dia=dia_laborable(i)) for i in range(14)]
    filas.append(r("Casi Fondista", 1620, 4, dia=dia_de_finde(0)))

    assert "fondista" not in medallas_de_temporada(filas, TEMPORADA).get("Casi Fondista", [])


# @scenarios fin-de-semana-no-fija-dificultad
def test_un_domingo_con_muestra_suficiente_tampoco_es_un_dia_dificil():
    """La regla no se apoya en que el fin de semana tenga poca muestra.

    El día del fixture cumple TODO lo que exige la medalla —seis jugadores, media 5,67 por encima del
    umbral de 5,5, y alguien resolviendo en 4—. Lo único que se lo impide es que es domingo. El control
    con el mismo día en laborable es lo que demuestra que no la deniega otra condición.
    """
    from tools.badges import medallas_permanentes

    domingo = dia_de_finde(1)
    en_domingo = jornada_con(1650, [6, 6, 6, 6, 6], dia=domingo) + [
        r("Dominguera", 1650, 4, dia=domingo)
    ]
    assert "dia-imposible" not in medallas_permanentes(en_domingo).get("Dominguera", [])

    laborable = dia_laborable(0)
    en_laborable = jornada_con(1651, [6, 6, 6, 6, 6], dia=laborable) + [
        r("Dominguera", 1651, 4, dia=laborable)
    ]
    assert "dia-imposible" in medallas_permanentes(en_laborable)["Dominguera"]


# @scenarios metronomo-solo-exige-los-dias-laborables
def test_el_metronomo_no_lo_bloquea_el_domingo_de_otra_persona():
    """El fallo que la regla arregla: los días de la temporada salen de los datos.

    Mientras el fin de semana contaba, una sola persona jugando un domingo convertía ese domingo en día
    de la temporada y se lo bloqueaba a todos los demás. Medido en producción: 0 de 123 parejas
    jugador-mes.
    """
    from tools.badges import medallas_de_temporada

    # diez días laborables jugados: el mínimo para que Metrónom@ se evalúe
    filas = [r("Constante", 1600 + i, 4, dia=dia_laborable(i)) for i in range(10)]
    filas.append(r("Dominguero", 1620, 4, dia=dia_de_finde(1)))

    assert "metronomo" in medallas_de_temporada(filas, TEMPORADA)["Constante"]


# @scenarios jornada-de-fin-de-semana-no-anuncia-medallas
def test_una_jornada_de_sabado_no_anuncia_nada_y_el_mensaje_queda_intacto():
    from tools.badges import texto_de_medallas
    from post_ranking import comentario

    # cruzaría Fondista justo en la jornada del sábado
    filas = [r("Sabatino", 1600 + i, 4, dia=dia_laborable(i)) for i in range(14)]
    filas.append(r("Sabatino", 1620, 4, dia=dia_de_finde(0)))

    seccion = texto_de_medallas(filas, TEMPORADA, jornada=1620)
    assert seccion == ""

    # y el resumen del sábado sigue saliendo, solo que sin medallas
    mensaje = comentario(seccion)
    assert "ranking actualizado" in mensaje
    assert "workers.dev" in mensaje


# @scenarios el-resumen-conserva-lo-que-ya-publicaba
def test_el_mensaje_conserva_el_saludo_y_el_enlace():
    """Las medallas se añaden al mensaje; no lo sustituyen."""
    from post_ranking import comentario

    con = comentario("🏅 *Medallas de hoy*\n💪 Fondista — Alguien")
    sin = comentario("")

    for texto in (con, sin):
        assert "ranking actualizado" in texto
        assert "workers.dev" in texto
    assert "Fondista" in con
    assert "Medallas" not in sin

    # y sin medallas el mensaje no deja un hueco donde iría la sección
    assert "\n\n\n" not in sin
    assert sin.count("\n\n") == 1


# @scenarios umbral-exacto-otorga
def test_dos_medallas_nunca_comparten_nombre():
    """El diseño de la liga arcade propuso llamar `Superviviente` al mes sin fallo.

    Ese nombre ya estaba en otra regla —resolver en ≤4 tres días duros—, así que adoptarlo habría dejado dos
    medallas distintas llamadas igual. Se rechazó, y este test impide que vuelva a colarse.
    """
    from tools.badges import CATALOGO

    nombres = [medalla.nombre for medalla in CATALOGO]
    claves = [medalla.clave for medalla in CATALOGO]

    assert len(set(nombres)) == len(nombres), f"nombres repetidos: {nombres}"
    assert len(set(claves)) == len(claves), f"claves repetidas: {claves}"
