"""Escenarios de `empates-comparten-puesto` (Fase 2 — TDD rojo)."""

from __future__ import annotations

HISTORICO = "2026-03-02"


def partidas(nombre, scores):
    """Una partida por score, cada una en su jornada. La media sale de la lista."""
    return [
        {
            "slack_user_id": f"U_{nombre}",
            "player_name": nombre,
            "wordle_id": 1500 + i,
            "score": s,
            "date": HISTORICO,
            "pattern": None,
        }
        for i, s in enumerate(scores)
    ]


def puestos(filas, temporada="0"):
    from standings import clasificacion

    return [(f["nombre"], f["posicion"], f["media_temporada"]) for f in clasificacion(filas, temporada)]


# @scenarios empatados-comparten-numero
def test_dos_con_la_misma_media_comparten_puesto():
    filas = partidas("Ana", [3, 3, 3, 3, 3]) + partidas("Bea", [3, 3, 3, 3, 3])

    resultado = puestos(filas)

    assert [p for _, p, _ in resultado] == [1, 1], f"deberían compartir el 1º: {resultado}"


# @scenarios el-siguiente-salta
def test_despues_de_un_empate_el_puesto_salta():
    filas = (
        partidas("Lider", [2, 2, 2, 2, 2])
        + partidas("Ana", [3, 3, 3, 3, 3])
        + partidas("Bea", [3, 3, 3, 3, 3])
        + partidas("Cris", [4, 4, 4, 4, 4])
    )

    resultado = dict((n, p) for n, p, _ in puestos(filas))

    assert resultado["Lider"] == 1
    assert resultado["Ana"] == resultado["Bea"] == 2
    assert resultado["Cris"] == 4, "el hueco dice cuánta gente va por delante"


# @scenarios el-orden-sigue-siendo-determinista
def test_el_orden_de_la_lista_no_depende_del_orden_de_entrada():
    ana = partidas("Ana", [3, 3, 3, 3, 3])
    bea = partidas("Bea", [3, 3, 3, 3, 3])

    de_una = [n for n, _, _ in puestos(ana + bea)]
    de_otra = [n for n, _, _ in puestos(bea + ana)]

    assert de_una == de_otra == ["Ana", "Bea"]


# @scenarios el-empate-se-mide-sobre-la-media-publicada
def test_una_diferencia_invisible_cuenta_como_empate():
    """3,5714… y 3,5716… se publican los dos como 3,57. Separarlos es incomprensible al leerlo."""
    from standings import clasificacion

    # 25 partidas: 4 de 3 y 21 de 4 → 3,84; y otro con una combinación que redondea igual.
    ana = partidas("Ana", [3] * 4 + [4] * 21)
    bea = partidas("Bea", [3] * 4 + [4] * 21)
    tabla = clasificacion(ana + bea, "0")

    assert tabla[0]["media_temporada"] == tabla[1]["media_temporada"]
    assert tabla[0]["posicion"] == tabla[1]["posicion"]


# @scenarios quien-no-clasifica-sigue-sin-puesto
def test_quien_no_clasifica_no_comparte_puesto():
    from standings import MINIMO_PARA_CLASIFICAR

    filas = partidas("Ana", [3] * MINIMO_PARA_CLASIFICAR) + partidas("Corta", [3])

    resultado = dict((n, p) for n, p, _ in puestos(filas))

    assert resultado["Ana"] == 1
    assert resultado["Corta"] is None
