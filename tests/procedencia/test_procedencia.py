"""La procedencia de un cálculo: con qué versión se hizo, y si esa versión era vieja.

Existe por el incidente del 2026-08-13: la instantánea de agosto apareció con el álbum calculado con la regla
del día anterior, porque alguien ejecutó `local_stack.py` desde una copia por detrás de `main`. Los tres cron
de esa mañana habían escrito bien. Averiguar de dónde venía ese payload costó media docena de consultas.

**Los tests no consultan git de verdad.** Se le pasan dobles: si dependieran del estado real del repositorio
darían un resultado distinto según quién los ejecute y cuándo, que es lo contrario de un test.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))


def test_la_version_marca_el_arbol_sucio():
    """`88cc1b7+sucio` avisa de que el payload no corresponde a ningún commit del repositorio.

    Es el caso de quien está probando algo a medias, y el sufijo importa tanto como el SHA.
    """
    import procedencia

    respuestas = {("rev-parse", "--short", "HEAD"): "88cc1b7", ("status", "--porcelain"): " M tools/album.py"}
    procedencia._git = lambda *args, **kwargs: respuestas.get(args)

    assert procedencia.version() == "88cc1b7+sucio"


def test_la_version_limpia_es_solo_el_sha():
    import procedencia

    respuestas = {("rev-parse", "--short", "HEAD"): "88cc1b7", ("status", "--porcelain"): ""}
    procedencia._git = lambda *args, **kwargs: respuestas.get(args)

    assert procedencia.version() == "88cc1b7"


def test_sin_git_la_version_es_vacia_y_no_estalla():
    """En CI el checkout puede ser superficial. Un fallo de git no puede impedir materializar."""
    import procedencia

    procedencia._git = lambda *args, **kwargs: None

    assert procedencia.version() == ""


def test_se_detecta_que_la_copia_esta_por_detras():
    import procedencia

    procedencia._git = lambda *args, **kwargs: "2" if args[0] == "rev-list" else ""

    detras, detalle = procedencia.por_detras_de_origen()

    assert detras is True
    assert "2 commits" in detalle


def test_una_copia_al_dia_no_avisa():
    import procedencia

    procedencia._git = lambda *args, **kwargs: "0" if args[0] == "rev-list" else ""

    detras, _ = procedencia.por_detras_de_origen()

    assert detras is False


def test_sin_remoto_no_se_afirma_que_este_por_detras():
    """Un aviso aproximado es mejor que ninguno, pero inventarse un veredicto es peor que callar."""
    import procedencia

    procedencia._git = lambda *args, **kwargs: None

    detras, detalle = procedencia.por_detras_de_origen()

    assert detras is False
    assert "no se ha podido comparar" in detalle


def test_la_instantanea_guarda_con_que_version_se_calculo():
    """Sin esto, un payload escrito con código viejo es indistinguible de uno bueno."""
    from seasons import instantanea

    filas = [
        {
            "slack_user_id": "U1",
            "player_name": "Ana",
            "wordle_id": 1500 + i,
            "score": 4,
            "date": "2026-03-02",
            "pattern": None,
        }
        for i in range(5)
    ]

    assert instantanea(filas, "0", "88cc1b7")["calculado_con"] == "88cc1b7"
    # Y sin saberla se declara vacía, en lugar de inventarse un valor.
    assert instantanea(filas, "0")["calculado_con"] == ""


def test_la_instantanea_sigue_siendo_determinista():
    """La versión entra **por parámetro**: si `instantanea` leyera git, dejaría de dar lo mismo con lo mismo."""
    from seasons import instantanea

    filas = [
        {
            "slack_user_id": "U1",
            "player_name": "Ana",
            "wordle_id": 1500 + i,
            "score": 4,
            "date": "2026-03-02",
            "pattern": None,
        }
        for i in range(5)
    ]

    assert instantanea(filas, "0", "abc") == instantanea(filas, "0", "abc")


def test_materializar_desde_una_copia_vieja_aborta():
    """Materializar desde una copia vieja no recalcula: **retrocede**. Y nada lo avisaba."""
    import local_stack
    import procedencia

    procedencia._git = lambda *args, **kwargs: "3" if args[0] == "rev-list" else ""

    with pytest.raises(SystemExit) as fallo:
        local_stack._exige_estar_al_dia()

    assert "ALTO" in str(fallo.value) and "git pull" in str(fallo.value)


def test_se_puede_insistir_para_comparar_contra_el_calculo_viejo():
    """A veces se quiere justamente eso. Lo que no puede pasar es hacerlo sin darse cuenta."""
    import local_stack
    import procedencia

    procedencia._git = lambda *args, **kwargs: "3" if args[0] == "rev-list" else ""

    local_stack._exige_estar_al_dia(insiste=True)  # no levanta


def test_el_materializador_rellena_la_procedencia(monkeypatch):
    """**Sobre el materializador, no sobre `instantanea`.** La prueba de mutación cazó que quitar `version()`
    de la llamada dejaba la suite en verde: la función guardaba lo que le pasaran y nadie comprobaba que se le
    pasara algo.
    """
    import datetime

    import materialize_seasons as mat
    import procedencia

    monkeypatch.setattr(procedencia, "_git", lambda *a, **k: "abc1234" if a[0] == "rev-parse" else "")

    escritas = []

    class TablaDoble:
        def upsert(self, fila, clave):
            escritas.append(fila)

    filas = [
        {
            "slack_user_id": "U1",
            "player_name": "Ana",
            "wordle_id": 1500 + i,
            "score": 4,
            "date": "2026-03-02",
            "pattern": None,
        }
        for i in range(5)
    ]

    mat.materializar(filas, ["0"], TablaDoble(), datetime.datetime(2026, 8, 13, tzinfo=datetime.timezone.utc))

    assert escritas, "no ha escrito nada"
    assert escritas[0]["payload"]["calculado_con"] == "abc1234"


def test_calcular_no_materializa_desde_una_copia_vieja(monkeypatch):
    """**Sobre `calcular`, no sobre la comprobación.** Desactivar el enganche dejaba la suite en verde.

    Es el enganche lo que importa: la función que avisa no sirve de nada si nadie la llama antes de escribir.
    """
    import local_stack
    import materialize_seasons as mat
    import procedencia

    monkeypatch.setattr(mat, "leer_resultados", lambda url, clave: [
        {
            "slack_user_id": "U1",
            "player_name": "Ana",
            "wordle_id": 1500 + i,
            "score": 4,
            "date": "2026-03-02",
            "pattern": None,
        }
        for i in range(5)
    ])
    monkeypatch.setattr(procedencia, "_git", lambda *a, **k: "4" if a[0] == "rev-list" else "")

    def no_debe_llegar(*args, **kwargs):
        raise AssertionError("ha creado la tabla: iba a escribir con una copia vieja")

    monkeypatch.setattr(mat, "TablaSupabase", no_debe_llegar)

    with pytest.raises(SystemExit) as fallo:
        local_stack.calcular("url", "clave", seco=False, temporadas_objetivo=["0"])

    assert "ALTO" in str(fallo.value)
