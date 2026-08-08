"""Escenarios de `backfill-de-patrones` (Fase 2 — TDD rojo).

Los seis escenarios sobre dobles en memoria: un canal falso que devuelve páginas preparadas y una
tabla falsa que registra las escrituras. Ningún test toca Slack ni Supabase — este slice hace la
única escritura masiva del proyecto sobre datos reales, así que su verificación no puede depender
de producción.
"""

from __future__ import annotations

import pytest

VERDE = ":large_green_square:"
AMARILLO = ":large_yellow_square:"
NEGRO = ":black_large_square:"

def mensaje(numero: int, intentos: str, autor: str, filas: list[str] | None = None) -> dict:
    cuerpo = [f"La palabra del día #{numero} {intentos}/6", ""]
    cuerpo += filas or []
    return {"autor": autor, "texto": "\n".join(cuerpo)}


CUADRICULA_TRES = [
    NEGRO * 3 + AMARILLO * 2,
    NEGRO + VERDE + NEGRO + AMARILLO * 2,
    VERDE * 5,
]


class CanalFalso:
    """Devuelve el histórico en páginas, como la API real."""

    def __init__(self, paginas: list[list[dict]]) -> None:
        self.paginas = paginas
        self.paginas_servidas = 0

    def paginar(self):
        for pagina in self.paginas:
            self.paginas_servidas += 1
            yield pagina


class TablaFalsa:
    """Filas en memoria; registra cada escritura para poder afirmar sobre ellas."""

    def __init__(self, filas: list[dict]) -> None:
        self.filas = filas
        self.escrituras: list[tuple[int, dict]] = []

    def sin_patron(self):
        return [f for f in self.filas if not f.get("pattern")]

    def buscar(self, wordle_id: int, autor: str):
        for f in self.filas:
            if f["wordle_id"] == wordle_id and f["autor"] == autor:
                return f
        return None

    def actualizar(self, fila_id: int, campos: dict) -> None:
        self.escrituras.append((fila_id, campos))
        for f in self.filas:
            if f["id"] == fila_id:
                f.update(campos)


# @scenarios rellena-filas-sin-patron
def test_rellena_una_fila_que_no_tenia_patron():
    from tools.backfill_patterns import rellenar

    canal = CanalFalso([[mensaje(1671, "3", "uno", CUADRICULA_TRES)]])
    tabla = TablaFalsa([{"id": 1, "wordle_id": 1671, "autor": "uno", "pattern": None, "score": 3}])

    informe = rellenar(canal, tabla)

    assert informe.rellenadas == 1
    assert tabla.filas[0]["pattern"] == "...YY/.G.YY/GGGGG"


# @scenarios no-modifica-filas-con-patron
def test_una_fila_con_patron_queda_intacta_y_el_relleno_es_idempotente():
    from tools.backfill_patterns import rellenar

    canal = CanalFalso([[mensaje(1671, "3", "uno", CUADRICULA_TRES)]])
    tabla = TablaFalsa([{"id": 1, "wordle_id": 1671, "autor": "uno", "pattern": "YA/ESTABA", "score": 3}])

    primero = rellenar(canal, tabla)
    estado_intermedio = [dict(f) for f in tabla.filas]
    segundo = rellenar(CanalFalso([[mensaje(1671, "3", "uno", CUADRICULA_TRES)]]), tabla)

    assert primero.intactas == 1
    assert primero.rellenadas == 0
    assert tabla.escrituras == []
    assert tabla.filas == estado_intermedio
    assert segundo.intactas == 1


# @scenarios no-inserta-resultados-nuevos
def test_un_resultado_del_canal_sin_fila_no_crea_fila():
    from tools.backfill_patterns import rellenar

    canal = CanalFalso([[mensaje(1500, "4", "fantasma", CUADRICULA_TRES)]])
    tabla = TablaFalsa([{"id": 1, "wordle_id": 1671, "autor": "uno", "pattern": None, "score": 3}])

    informe = rellenar(canal, tabla)

    assert len(tabla.filas) == 1
    assert informe.resultados_sin_registrar == 1
    assert informe.rellenadas == 0


# @scenarios recorre-todo-el-historico
def test_recorre_todas_las_paginas_del_historico():
    from tools.backfill_patterns import rellenar

    canal = CanalFalso(
        [
            [mensaje(1671, "3", "uno", CUADRICULA_TRES)],
            [mensaje(1670, "3", "dos", CUADRICULA_TRES)],
            [mensaje(1669, "3", "tres", CUADRICULA_TRES)],
        ]
    )
    tabla = TablaFalsa(
        [
            {"id": 1, "wordle_id": 1671, "autor": "uno", "pattern": None, "score": 3},
            {"id": 2, "wordle_id": 1670, "autor": "dos", "pattern": None, "score": 3},
            {"id": 3, "wordle_id": 1669, "autor": "tres", "pattern": None, "score": 3},
        ]
    )

    informe = rellenar(canal, tabla)

    assert canal.paginas_servidas == 3
    assert informe.rellenadas == 3


# @scenarios fila-sin-mensaje-se-reporta
def test_una_fila_sin_mensaje_en_el_canal_queda_sin_patron_y_se_reporta():
    from tools.backfill_patterns import rellenar

    canal = CanalFalso([[mensaje(1671, "3", "uno", CUADRICULA_TRES)]])
    tabla = TablaFalsa(
        [
            {"id": 1, "wordle_id": 1671, "autor": "uno", "pattern": None, "score": 3},
            {"id": 2, "wordle_id": 1400, "autor": "antiguo", "pattern": None, "score": 4},
        ]
    )

    informe = rellenar(canal, tabla)

    assert informe.no_resueltas == 1
    assert tabla.buscar(1400, "antiguo")["pattern"] is None


# @scenarios recuento-final
def test_el_informe_distingue_rellenadas_intactas_y_no_resueltas():
    from tools.backfill_patterns import rellenar

    canal = CanalFalso([[mensaje(1671, "3", "uno", CUADRICULA_TRES), mensaje(1670, "3", "dos", CUADRICULA_TRES)]])
    tabla = TablaFalsa(
        [
            {"id": 1, "wordle_id": 1671, "autor": "uno", "pattern": None, "score": 3},
            {"id": 2, "wordle_id": 1670, "autor": "dos", "pattern": "YA/ESTABA", "score": 3},
            {"id": 3, "wordle_id": 1400, "autor": "antiguo", "pattern": None, "score": 4},
        ]
    )

    informe = rellenar(canal, tabla)

    assert (informe.rellenadas, informe.intactas, informe.no_resueltas) == (1, 1, 1)


# @scenarios ensayo-no-escribe
def test_el_ensayo_cuenta_igual_pero_no_escribe():
    """El ensayo obligatorio antes de la escritura masiva: mismo recuento, cero escrituras."""
    from tools.backfill_patterns import rellenar

    canal = CanalFalso([[mensaje(1671, "3", "uno", CUADRICULA_TRES)]])
    tabla = TablaFalsa([{"id": 1, "wordle_id": 1671, "autor": "uno", "pattern": None, "score": 3}])

    informe = rellenar(canal, tabla, dry_run=True)

    assert informe.rellenadas == 1
    assert tabla.escrituras == []
    assert tabla.filas[0]["pattern"] is None


# @scenarios correspondencia-por-identificador
def test_el_autor_de_una_entrada_es_el_identificador_no_el_nombre():
    """El acoplamiento que rompió el backfill tras canonizar la identidad.

    Los siete escenarios de `rellenar()` reciben el autor por parámetro y les da igual si es un nombre o un
    identificador, así que pasaban en verde mientras la ejecución real resolvía 0 de 299 filas. El
    emparejamiento tiene que mirar lo mismo que la tabla guarda.
    """
    from tools.backfill_patterns import entrada_de_mensaje

    entrada = entrada_de_mensaje(
        {"user": "U0ZGXL725", "text": "La palabra del día #1671 3/6"}
    )

    assert entrada["autor"] == "U0ZGXL725"
    assert entrada["texto"] == "La palabra del día #1671 3/6"


# @scenarios correspondencia-por-identificador
def test_un_mensaje_sin_autor_o_de_sistema_no_entra_en_el_recorrido():
    from tools.backfill_patterns import entrada_de_mensaje

    assert entrada_de_mensaje({"text": "sin autor"}) is None
    assert entrada_de_mensaje({"user": "U0ZGXL725", "subtype": "channel_join", "text": ""}) is None


# @scenarios correspondencia-por-identificador
def test_el_indice_localiza_la_fila_por_puzzle_e_identificador():
    """Dos jugadores en el mismo puzzle y el mismo jugador en dos puzzles: la clave necesita las dos partes."""
    from tools.backfill_patterns import indexar

    filas = [
        {"id": 1, "wordle_id": 1671, "slack_user_id": "U_UNO"},
        {"id": 2, "wordle_id": 1671, "slack_user_id": "U_DOS"},
        {"id": 3, "wordle_id": 1670, "slack_user_id": "U_UNO"},
    ]
    indice = indexar(filas)

    assert indice[(1671, "U_UNO")]["id"] == 1
    assert indice[(1671, "U_DOS")]["id"] == 2
    assert indice[(1670, "U_UNO")]["id"] == 3
    assert len(indice) == 3
