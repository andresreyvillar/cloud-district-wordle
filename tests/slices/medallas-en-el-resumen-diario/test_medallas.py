"""Escenarios de `medallas-en-el-resumen-diario` (Fase 2 — TDD rojo).

Fixtures construidos a mano, con el mínimo de filas que hace verdadera cada condición: así el test
explica el umbral en lugar de esconderlo. Nada de producción, nada de Slack.

La temporada y la jornada entran por parámetro: el cálculo no lee el reloj (§10 del protocolo).
"""

from __future__ import annotations

import pytest

MOTIVO = "TDD rojo — tools/badges.py no existe todavía"

TEMPORADA = "2026-08"
#: cinco jugadores de relleno hacen que un día tenga muestra suficiente para medir su dificultad
RELLENO = ["r1", "r2", "r3", "r4", "r5"]


def r(jugador: str, wordle: int, score: int, mes: str = TEMPORADA, dia: int = 1) -> dict:
    return {"player_name": jugador, "wordle_id": wordle, "score": score, "date": f"{mes}-{dia:02d}"}


def jornada_con(wordle: int, scores_relleno: list[int], mes: str = TEMPORADA, dia: int = 1) -> list[dict]:
    """Un día con cinco jugadores de relleno, para fijar su dificultad media."""
    return [r(j, wordle, s, mes, dia) for j, s in zip(RELLENO, scores_relleno)]


# @scenarios medalla-nueva-se-anuncia
def test_la_medalla_alcanzada_en_esta_jornada_se_anuncia():
    from tools.badges import texto_de_medallas

    # la 15ª partida es la de la jornada 1614: ahí cruza el umbral de Fondista
    filas = [r("Fondista Total", 1600 + i, 4, dia=(i % 28) + 1) for i in range(15)]
    texto = texto_de_medallas(filas, TEMPORADA, jornada=1614)

    assert "Fondista Total" in texto
    assert "Fondista" in texto


# @scenarios medalla-ya-anunciada-no-se-repite
def test_una_medalla_ganada_ayer_no_se_repite_hoy():
    from tools.badges import texto_de_medallas

    filas = [r("Veterano", 1600 + i, 4, dia=(i % 28) + 1) for i in range(15)]
    filas.append(r("Veterano", 1615, 4, dia=16))          # una partida más, al día siguiente

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

    filas = [r("Justo", 1600 + i, 4, dia=(i % 28) + 1) for i in range(15)]
    assert "fondista" in medallas_de_temporada(filas, TEMPORADA)["Justo"]


# @scenarios umbral-por-debajo-no-otorga
def test_catorce_partidas_no_otorgan_fondista():
    from tools.badges import medallas_de_temporada

    filas = [r("Casi", 1600 + i, 4, dia=(i % 28) + 1) for i in range(14)]
    assert "fondista" not in medallas_de_temporada(filas, TEMPORADA).get("Casi", [])


# @scenarios medalla-nueva-se-anuncia, medalla-ya-anunciada-no-se-repite
def test_la_gesta_de_hoy_se_anuncia_y_la_de_ayer_no():
    from tools.badges import texto_de_medallas

    filas = [r("Afortunada", 1610, 1, dia=2)] + jornada_con(1610, [4, 4, 5, 4, 4], dia=2)
    hoy = texto_de_medallas(filas, TEMPORADA, jornada=1610)
    mañana = texto_de_medallas(filas + jornada_con(1611, [3, 4, 4, 3, 4], dia=3), TEMPORADA, jornada=1611)

    assert "Afortunada" in hoy
    assert "Afortunada" not in mañana


# @scenarios dia-imposible-exige-las-dos-condiciones
def test_ni_resolver_rapido_en_dia_facil_ni_lento_en_dia_duro_dan_la_medalla():
    from tools.badges import medallas_permanentes

    # día fácil (media 3.0) resuelto rápido → no cuenta
    facil = jornada_con(1620, [3, 3, 3, 3, 3], dia=4) + [r("Rapido", 1620, 3, dia=4)]
    # día duro (media 5.8) resuelto lento → no cuenta
    duro = jornada_con(1621, [6, 6, 6, 5, 6], dia=5) + [r("Lento", 1621, 6, dia=5)]

    permanentes = medallas_permanentes(facil + duro)
    assert "dia-imposible" not in permanentes.get("Rapido", [])
    assert "dia-imposible" not in permanentes.get("Lento", [])


# @scenarios dia-imposible-exige-las-dos-condiciones
def test_resolver_rapido_un_dia_duro_si_da_la_medalla():
    from tools.badges import medallas_permanentes

    duro = jornada_con(1622, [6, 6, 6, 6, 6], dia=6) + [r("Heroína", 1622, 4, dia=6)]
    assert "dia-imposible" in medallas_permanentes(duro)["Heroína"]


# @scenarios repeticion-se-cuenta
def test_la_misma_medalla_en_dos_temporadas_cuenta_dos_veces():
    from tools.badges import medallas_de_temporada

    julio = [r("Constante", 1500 + i, 4, mes="2026-07", dia=(i % 28) + 1) for i in range(15)]
    agosto = [r("Constante", 1600 + i, 4, mes="2026-08", dia=(i % 28) + 1) for i in range(15)]
    filas = julio + agosto

    assert "fondista" in medallas_de_temporada(filas, "2026-07")["Constante"]
    assert "fondista" in medallas_de_temporada(filas, "2026-08")["Constante"]


# @scenarios calculo-determinista
def test_el_calculo_no_depende_del_orden_ni_del_reloj():
    from tools.badges import medallas_de_temporada

    filas = [r("Orden", 1600 + i, 4, dia=(i % 28) + 1) for i in range(15)]
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
    filas = [r("Adelantado", 1600 + i, 4, dia=(i % 28) + 1) for i in range(20)]

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
        r("Solitario", 1630, 4, dia=7),
        r("Acompañante", 1630, 7, dia=7),
    ]
    assert "dia-imposible" not in medallas_permanentes(filas).get("Solitario", [])

    # y con muestra suficiente, la misma media sí la concede
    con_muestra = filas + [r(f"relleno{i}", 1630, 7, dia=7) for i in range(3)]
    assert "dia-imposible" in medallas_permanentes(con_muestra)["Solitario"]


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
