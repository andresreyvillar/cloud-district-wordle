"""Escenarios de `identidad-canonica-de-jugador` (Fase 2 — TDD rojo).

Los siete escenarios sobre dobles en memoria: un directorio falso (nombre → identificador) y una
tabla falsa que registra escrituras y borrados. Este slice reescribe la identidad de ~1235 filas y
elimina 12, así que su verificación no puede depender de producción.
"""

from __future__ import annotations

import pytest

MOTIVO = "TDD rojo — tools/canonical_identity.py no existe todavía"

# El directorio del workspace: nombre mostrado → identificador de Slack
DIRECTORIO = {
    "Carlos": "U_CARLOS",
    "Paula Granado": "U_PAULA",
    "Carlos H.": "U_CARLOSH",
    "Marcos Granado": "U_MARCOS",
    "marcos.granado": "U_MARCOS",  # la misma persona, con su nombre anterior
}


class TablaFalsa:
    def __init__(self, filas: list[dict]) -> None:
        self.filas = filas
        self.escrituras: list[tuple] = []
        self.borrados: list = []

    def todas(self) -> list[dict]:
        return list(self.filas)

    def actualizar(self, fila_id, campos: dict) -> None:
        self.escrituras.append((fila_id, campos))
        for f in self.filas:
            if f["id"] == fila_id:
                f.update(campos)

    def eliminar(self, fila_id) -> None:
        self.borrados.append(fila_id)
        self.filas = [f for f in self.filas if f["id"] != fila_id]

    def por_id(self, fila_id):
        return next((f for f in self.filas if f["id"] == fila_id), None)


def fila(id_, identidad, nombre, wordle, score=4, pattern=None):
    return {
        "id": id_,
        "slack_user_id": identidad,
        "player_name": nombre,
        "wordle_id": wordle,
        "score": score,
        "pattern": pattern,
    }


# @scenarios nombre-se-resuelve-a-id
@pytest.mark.skip(reason=MOTIVO)
def test_un_nombre_mostrado_se_convierte_en_identificador():
    from tools.canonical_identity import canonizar

    tabla = TablaFalsa([fila(1, "Carlos", "Carlos", 1600)])
    informe = canonizar(DIRECTORIO, tabla)

    assert informe.resueltas == 1
    assert tabla.por_id(1)["slack_user_id"] == "U_CARLOS"


# @scenarios id-existente-no-se-toca
@pytest.mark.skip(reason=MOTIVO)
def test_una_fila_ya_canonica_no_se_modifica_y_el_proceso_es_idempotente():
    from tools.canonical_identity import canonizar

    tabla = TablaFalsa([fila(1, "U_CARLOS", "Carlos", 1600)])

    primero = canonizar(DIRECTORIO, tabla)
    estado = [dict(f) for f in tabla.filas]
    segundo = canonizar(DIRECTORIO, tabla)

    assert primero.ya_canonicas == 1
    assert primero.resueltas == 0
    assert tabla.escrituras == []
    assert tabla.filas == estado
    assert segundo.ya_canonicas == 1


# @scenarios renombre-se-fusiona
@pytest.mark.skip(reason=MOTIVO)
def test_el_mismo_puzzle_bajo_dos_nombres_del_mismo_jugador_queda_en_una_fila():
    from tools.canonical_identity import canonizar

    tabla = TablaFalsa(
        [
            fila(1, "Marcos Granado", "Marcos Granado", 1586, score=4),
            fila(2, "marcos.granado", "marcos.granado", 1586, score=4),
        ]
    )
    informe = canonizar(DIRECTORIO, tabla)

    assert informe.fusionadas == 1
    del_jugador = [f for f in tabla.filas if f["slack_user_id"] == "U_MARCOS" and f["wordle_id"] == 1586]
    assert len(del_jugador) == 1


# @scenarios renombre-se-fusiona
@pytest.mark.skip(reason=MOTIVO)
def test_dos_puzzles_distintos_del_mismo_jugador_no_se_fusionan():
    from tools.canonical_identity import canonizar

    tabla = TablaFalsa(
        [
            fila(1, "Marcos Granado", "Marcos Granado", 1586),
            fila(2, "marcos.granado", "marcos.granado", 1587),
        ]
    )
    informe = canonizar(DIRECTORIO, tabla)

    assert informe.fusionadas == 0
    assert len(tabla.filas) == 2


# @scenarios atribucion-cruzada-se-elimina
@pytest.mark.skip(reason=MOTIVO)
def test_una_fila_cuyo_id_y_nombre_son_de_personas_distintas_se_elimina():
    """El caso real: 8 filas con el identificador de Paula y el nombre de Carlos H."""
    from tools.canonical_identity import canonizar

    tabla = TablaFalsa(
        [
            fila(1, "U_PAULA", "Paula Granado", 1477, score=4),
            fila(2, "U_PAULA", "Carlos H.", 1477, score=3),  # cruzada
        ]
    )
    informe = canonizar(DIRECTORIO, tabla)

    assert informe.cruzadas == 1
    assert tabla.borrados == [2]
    assert [f["id"] for f in tabla.filas] == [1]


# @scenarios nombre-desconocido-se-declara
@pytest.mark.skip(reason=MOTIVO)
def test_un_nombre_que_no_esta_en_el_directorio_se_conserva_y_se_declara():
    from tools.canonical_identity import canonizar

    tabla = TablaFalsa([fila(1, "Alguien Que Se Fue", "Alguien Que Se Fue", 1500)])
    informe = canonizar(DIRECTORIO, tabla)

    assert informe.no_resueltas == 1
    assert tabla.por_id(1)["slack_user_id"] == "Alguien Que Se Fue"
    assert tabla.borrados == []


# @scenarios nombre-mostrado-se-conserva
@pytest.mark.skip(reason=MOTIVO)
def test_el_nombre_mostrado_sobrevive_a_la_canonizacion():
    from tools.canonical_identity import canonizar

    tabla = TablaFalsa([fila(1, "Carlos", "Carlos", 1600)])
    canonizar(DIRECTORIO, tabla)

    assert tabla.por_id(1)["player_name"] == "Carlos"
    for _, campos in tabla.escrituras:
        assert set(campos) == {"slack_user_id"}


# @scenarios ensayo-no-escribe
@pytest.mark.skip(reason=MOTIVO)
def test_el_ensayo_cuenta_igual_pero_no_escribe_ni_borra():
    from tools.canonical_identity import canonizar

    filas = [
        fila(1, "Carlos", "Carlos", 1600),
        fila(2, "U_PAULA", "Carlos H.", 1477, score=3),
        fila(3, "Marcos Granado", "Marcos Granado", 1586),
        fila(4, "marcos.granado", "marcos.granado", 1586),
    ]
    ensayo = canonizar(DIRECTORIO, TablaFalsa([dict(f) for f in filas]))
    tabla = TablaFalsa([dict(f) for f in filas])
    solo_cuenta = canonizar(DIRECTORIO, tabla, dry_run=True)

    assert (solo_cuenta.resueltas, solo_cuenta.fusionadas, solo_cuenta.cruzadas) == (
        ensayo.resueltas,
        ensayo.fusionadas,
        ensayo.cruzadas,
    )
    assert tabla.escrituras == []
    assert tabla.borrados == []
    assert len(tabla.filas) == 4
