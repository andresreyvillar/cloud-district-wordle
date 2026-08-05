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


class ViolacionDeIndiceUnico(Exception):
    """Lo que lanza Postgres con el código 23505."""


class TablaFalsa:
    """Doble de `wordle_results` que **impone el índice único** `(slack_user_id, wordle_id)`.

    La primera versión no lo imponía, y por eso los diez tests pasaban mientras la migración real
    reventaba a mitad: el doble era más permisivo que producción. Un doble que acepta lo que la tabla
    rechaza no prueba nada sobre la tabla.
    """

    def __init__(self, filas: list[dict]) -> None:
        self.filas = filas
        self.escrituras: list[tuple] = []
        self.borrados: list = []

    def todas(self) -> list[dict]:
        return list(self.filas)

    def actualizar(self, fila_id, campos: dict) -> None:
        if "clave" not in campos and "slack_user_id" in campos:
            propia = self.por_id(fila_id)
            destino = (campos["slack_user_id"], propia["wordle_id"])
            for otra in self.filas:
                if otra["id"] != fila_id and (otra["slack_user_id"], otra["wordle_id"]) == destino:
                    raise ViolacionDeIndiceUnico(
                        f'duplicate key value violates unique constraint: {destino} already exists'
                    )
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
def test_un_nombre_mostrado_se_convierte_en_identificador():
    from tools.canonical_identity import canonizar

    tabla = TablaFalsa([fila(1, "Carlos", "Carlos", 1600)])
    informe = canonizar(DIRECTORIO, tabla)

    assert informe.resueltas == 1
    assert tabla.por_id(1)["slack_user_id"] == "U_CARLOS"


# @scenarios id-existente-no-se-toca
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


# @scenarios atribucion-cruzada-se-declara-y-no-se-toca
def test_una_fila_cuyo_id_y_nombre_son_de_personas_distintas_se_declara_y_se_deja_quieta():
    """El caso real: 8 filas con el identificador de una persona y el nombre de otra.

    Ni se reatribuyen ni se borran. **Reatribuir se intentó y fabricó partidas**: el canal demostró que
    dos de esas filas correspondían a días en los que la persona del nombre no publicó nada, y una tercera
    era copia exacta de la cuadrícula de otra jugadora. Borrar, en cambio, destruiría datos apoyándose en
    que un nombre no cuadra, que no es prueba de nada.
    """
    from tools.canonical_identity import canonizar

    tabla = TablaFalsa(
        [
            fila(1, "U_PAULA", "Paula Granado", 1477, score=4),
            fila(2, "U_PAULA", "Carlos H.", 1477, score=3),  # cruzada
        ]
    )
    informe = canonizar(DIRECTORIO, tabla)

    assert informe.cruzadas == 1
    assert tabla.borrados == []
    assert tabla.escrituras == []
    assert tabla.por_id(2)["slack_user_id"] == "U_PAULA"  # intacta: no se le da a nadie
    assert tabla.por_id(1)["slack_user_id"] == "U_PAULA"


# @scenarios atribucion-cruzada-se-declara-y-no-se-toca
def test_una_cruzada_no_se_fusiona_con_la_partida_del_dueno_del_nombre():
    """Aunque coincida en puzzle y puntuación con una fila de la persona del nombre.

    Esa coincidencia es lo que hizo creer que eran duplicados suyos, y en cinco de ocho casos lo eran —
    pero en los otros tres no, y el cálculo no puede distinguirlos. Quien lo distingue es el canal.
    """
    from tools.canonical_identity import canonizar

    tabla = TablaFalsa(
        [
            fila(1, "U_CARLOSH", "Carlos H.", 1478, score=4),
            fila(2, "U_PAULA", "Carlos H.", 1478, score=4),
        ]
    )
    informe = canonizar(DIRECTORIO, tabla)

    assert informe.cruzadas == 1
    assert informe.fusionadas == 0
    assert tabla.borrados == []
    assert [f["id"] for f in tabla.filas] == [1, 2]


# @scenarios nombre-desconocido-se-declara
def test_un_nombre_que_no_esta_en_el_directorio_se_conserva_y_se_declara():
    from tools.canonical_identity import canonizar

    tabla = TablaFalsa([fila(1, "Alguien Que Se Fue", "Alguien Que Se Fue", 1500)])
    informe = canonizar(DIRECTORIO, tabla)

    assert informe.no_resueltas == 1
    assert tabla.por_id(1)["slack_user_id"] == "Alguien Que Se Fue"
    assert tabla.borrados == []


# @scenarios nombre-mostrado-se-conserva
def test_el_nombre_mostrado_sobrevive_a_la_canonizacion():
    from tools.canonical_identity import canonizar

    tabla = TablaFalsa([fila(1, "Carlos", "Carlos", 1600)])
    canonizar(DIRECTORIO, tabla)

    assert tabla.por_id(1)["player_name"] == "Carlos"
    for _, campos in tabla.escrituras:
        assert set(campos) == {"slack_user_id"}


# @scenarios ensayo-no-escribe
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


# @scenarios nombre-se-resuelve-a-id
def test_el_mapeo_curado_rellena_pero_no_pisa_al_workspace():
    """La línea más peligrosa del módulo, y un mutante sobrevivió a ella.

    El diccionario curado hereda un error de etiquetado del repo: una etiqueta apunta a otra persona.
    Aplicado por encima de `users.list` en lugar de como relleno, las 111 filas de Raquel Lorenzo se
    atribuirían a Clara. El workspace es evidencia; el curado es una lista escrita a mano.
    """
    from tools.canonical_identity import resolver_formas

    formas, ambiguas = resolver_formas(
        {"Raquel": {"U_RAQUEL"}},                                   # lo que dice el workspace
        curado={"Raquel": "U_CLARA", "Carlos H.": "U_CARLOSH"},     # la lista a mano, con su error
    )

    assert formas["Raquel"] == "U_RAQUEL"       # gana el workspace
    assert formas["Carlos H."] == "U_CARLOSH"   # y el curado rellena lo que Slack no conoce
    assert ambiguas == []


# @scenarios nombre-compartido-lo-desempata-quien-juega
def test_una_forma_compartida_por_dos_personas_la_gana_quien_ha_publicado():
    from tools.canonical_identity import resolver_formas

    formas, ambiguas = resolver_formas({"Sandra": {"U_UNA", "U_OTRA"}}, autores={"U_OTRA"}, curado={})

    assert formas["Sandra"] == "U_OTRA"
    assert ambiguas == []


# @scenarios nombre-compartido-lo-desempata-quien-juega
def test_si_las_dos_han_publicado_la_forma_se_declara_ambigua():
    """Sin desempate no se elige: la forma se descarta y sus filas salen como no resueltas."""
    from tools.canonical_identity import resolver_formas

    formas, ambiguas = resolver_formas(
        {"Sandra": {"U_UNA", "U_OTRA"}}, autores={"U_UNA", "U_OTRA"}, curado={}
    )

    assert "Sandra" not in formas
    assert ambiguas == ["Sandra"]


# @scenarios clave-ocupada-se-declara-y-no-se-fuerza
def test_una_fusion_libera_la_clave_que_otra_fila_necesita():
    """La forma que reventó la migración real: se borra antes de escribir.

    La fila que se queda necesita una clave que, en ese instante, ocupa la que va a fusionarse. Escribir
    primero violaba el índice único a mitad de la migración.
    """
    from tools.canonical_identity import canonizar

    tabla = TablaFalsa(
        [
            # dos identidades del mismo jugador; la segunda ya es canónica y ocupa la clave destino
            fila(1, "Marcos Granado", "Marcos Granado", 1586, score=4),
            fila(2, "U_MARCOS", "Marcos Granado", 1586, score=4),
        ]
    )
    informe = canonizar(DIRECTORIO, tabla)

    assert informe.fusionadas == 1
    assert informe.bloqueadas == 0
    assert [f["id"] for f in tabla.filas] == [2]


# @scenarios clave-ocupada-se-declara-y-no-se-fuerza
def test_una_cruzada_que_ocupa_la_clave_de_su_dueno_la_bloquea_y_se_declara():
    """La forma del puzzle 1481, que ningún orden de escritura puede resolver.

    La fila cruzada se queda donde está por diseño, y donde está es la clave que necesita su dueña
    legítima. Ni se fuerza ni se borra nada: la fila de Paula conserva su identidad y el informe declara
    las dos cosas, la cruzada y el bloqueo. Lo prudente no es neutral, y por eso se dice.
    """
    from tools.canonical_identity import canonizar

    tabla = TablaFalsa(
        [
            fila(1, "Paula Granado", "Paula Granado", 1481, score=5),
            fila(2, "U_PAULA", "Carlos H.", 1481, score=5),  # cruzada, ocupa la clave de Paula
        ]
    )
    informe = canonizar(DIRECTORIO, tabla)

    assert informe.cruzadas == 1
    assert informe.bloqueadas == 1
    assert informe.fusionadas == 0
    assert tabla.borrados == []
    assert tabla.escrituras == []
    assert tabla.por_id(1)["slack_user_id"] == "Paula Granado"  # intacta, no forzada
