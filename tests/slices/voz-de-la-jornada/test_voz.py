"""Escenarios de la frase y el meme, de `voz-de-la-jornada` (Fase 2 — TDD rojo).

Pack: `feat-voz-de-la-jornada`. Fixtures sintéticos: ver la nota de `test_senales.py`.

**El diccionario no se comprueba frase a frase.** Pinchar el texto exacto en un test convertiría cada cambio
de una coma en un test rojo, y el diccionario está hecho para editarse. Lo que se comprueba es lo que tiene
que ser cierto de cualquier frase: que sale, que corresponde al registro, que no se repite y que el mismo
día da el mismo resultado.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from refranero import DIA_DURO, DIA_FACIL, DIA_NORMAL  # noqa: E402

MOTIVO = "TDD rojo — tools/voz.py no existe todavía"


def test_el_diccionario_tiene_el_tamano_declarado():
    """Quince por registro, que es lo que da más de un mes sin repetir. No depende de implementación."""
    assert len(DIA_FACIL) == 15
    assert len(DIA_NORMAL) == 15
    assert len(DIA_DURO) == 15


def test_ninguna_frase_de_dia_esta_repetida():
    """Una frase duplicada haría que el ciclo la sacase dos veces por vuelta sin que se note en el código."""
    for registro in (DIA_FACIL, DIA_NORMAL, DIA_DURO):
        assert len(set(registro)) == len(registro)


def test_las_frases_de_dia_no_llevan_hueco_de_jugador():
    """No nombran a nadie: son del día, no de una persona. Un `{jugador}` aquí saldría literal en el canal."""
    for registro in (DIA_FACIL, DIA_NORMAL, DIA_DURO):
        for frase in registro:
            assert "{" not in frase, f"hueco sin rellenar en una frase de día: {frase}"


# @scenarios siempre-hay-una-frase
def test_el_dia_sin_nada_que_contar_tiene_frase():
    from voz import frase_del_dia

    assert frase_del_dia(dificultad=3.9, jornada=1700).strip() != ""


# @scenarios el-registro-sale-de-la-dificultad
def test_el_registro_lo_elige_la_dificultad():
    from voz import frase_del_dia

    assert frase_del_dia(dificultad=5.2, jornada=1700) in DIA_DURO
    assert frase_del_dia(dificultad=2.8, jornada=1700) in DIA_FACIL
    assert frase_del_dia(dificultad=3.9, jornada=1700) in DIA_NORMAL


# @scenarios la-frase-no-se-repite-al-dia-siguiente
def test_dos_jornadas_seguidas_no_repiten_frase():
    from voz import frase_del_dia

    assert frase_del_dia(dificultad=3.9, jornada=1700) != frase_del_dia(dificultad=3.9, jornada=1701)


# @scenarios la-misma-jornada-da-la-misma-frase
def test_la_misma_jornada_da_la_misma_frase():
    """Sin reloj y sin azar: es lo que permite comprobar el mensaje entero y que dos cron publiquen igual."""
    from voz import frase_del_dia

    assert frase_del_dia(dificultad=3.9, jornada=1700) == frase_del_dia(dificultad=3.9, jornada=1700)


# @scenarios el-lider-del-marcador-tiene-su-pulla, el-lider-del-album-tiene-la-suya
def test_quien_manda_se_lleva_su_pulla():
    from voz import pullas_de_lideres

    p = pullas_de_lideres(lider_marcador="Ana", lider_album="Bea", jornada=1700)

    assert "Ana" in p["marcador"] and "Bea" in p["album"]
    assert p["marcador"] != p["album"]


# @scenarios sin-lider-no-se-inventa-pulla
def test_sin_lider_de_album_no_hay_pulla_de_album():
    from voz import pullas_de_lideres

    p = pullas_de_lideres(lider_marcador="Ana", lider_album=None, jornada=1700)

    assert "album" not in p


# @scenarios las-frases-no-se-pisan
def test_las_frases_de_un_mensaje_no_se_repiten():
    from voz import pullas_de_lideres

    p = pullas_de_lideres(lider_marcador="Ana", lider_album="Ana", jornada=1700)

    assert p["marcador"] != p["album"], "el mismo líder en los dos ejes no puede llevar dos veces la misma"


# @scenarios el-meme-del-dia-necesita-que-pase-algo
def test_la_jornada_con_forma_reconocible_tiene_meme():
    from voz import meme_del_dia

    solo_uno = [{"jugador": "U1", "nombre": "Ana", "intentos": 4}] + [
        {"jugador": f"U{i}", "nombre": f"J{i}", "intentos": 7} for i in range(2, 8)
    ]

    meme = meme_del_dia(solo_uno, jornada=1700, lider=None, ultimo=None)

    assert meme and "Ana" in meme


# @scenarios sin-forma-reconocida-no-hay-meme
def test_la_jornada_corriente_no_tiene_meme():
    """Un chiste que no encaja delata que lo pone una máquina, así que se prefiere no ponerlo."""
    from voz import meme_del_dia

    corriente = [{"jugador": f"U{i}", "nombre": f"J{i}", "intentos": n} for i, n in enumerate((3, 4, 4, 5), 1)]

    assert meme_del_dia(corriente, jornada=1700, lider=None, ultimo=None) is None


# @scenarios el-meme-es-texto-y-no-imagen
def test_el_meme_no_tiene_huecos_sin_rellenar():
    from voz import meme_del_dia

    todos_fallan = [{"jugador": f"U{i}", "nombre": f"J{i}", "intentos": 7} for i in range(1, 6)]

    meme = meme_del_dia(todos_fallan, jornada=1700, lider=None, ultimo=None)

    assert meme and "{" not in meme, f"hueco de plantilla sin rellenar: {meme}"


# @scenarios el-mensaje-no-crece-sin-limite
def test_el_mensaje_no_encadena_todo_el_material():
    """Sin tope, una jornada movida encadena doce bloques. Nadie lee doce líneas de bot."""
    from voz import anadidos, TOPE_DE_ANADIDOS

    salida = anadidos(
        meme="🎯 Meme del día: algo",
        menciones={"aplaudido": "💥 A", "comentado": "💬 B", "madrugador": "🐓 C",
                   "rezagado": "🌙 D", "ausente": "🫥 E"},
        frase="Jornada de oficina.",
    )

    assert len(salida) <= TOPE_DE_ANADIDOS == 3


# @scenarios la-frase-del-dia-es-el-ultimo-recurso
def test_la_frase_cede_el_sitio_cuando_hay_algo_mejor():
    from voz import anadidos

    salida = anadidos(
        meme="🎯 Meme del día: algo",
        menciones={"aplaudido": "💥 A", "comentado": "💬 B", "madrugador": "🐓 C"},
        frase="Jornada de oficina.",
    )

    assert "Jornada de oficina." not in salida


# @scenarios siempre-hay-una-frase, la-frase-del-dia-es-el-ultimo-recurso
def test_el_dia_sin_nada_conserva_su_frase():
    """El caso que motiva el slice: cero hechos, cero señales. Ese día la frase es lo único que hay."""
    from voz import anadidos

    salida = anadidos(meme=None, menciones={}, frase="Jornada de oficina.")

    assert "Jornada de oficina." in salida


# @scenarios el-lider-del-marcador-tiene-su-pulla, el-lider-del-album-tiene-la-suya
def test_el_mensaje_publicado_lleva_las_pullas_de_los_lideres():
    """**Comprobado sobre el mensaje, no sobre la función.**

    `pullas_de_lideres` estaba en verde y el mensaje no las llevaba: se me olvidó añadirlas a las secciones.
    Un test que prueba la función pero no su uso deja el escenario sin proteger, y esto lo cazó mirar el
    mensaje. La aserción va contra el texto que se publica.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "slices" / "resumen-diario-compuesto"))
    from resumen import resumen_del_dia

    hoy = "2026-03-02"
    filas = [
        {"slack_user_id": "U1", "player_name": "Ana", "wordle_id": 1000 + i, "score": 2,
         "date": hoy, "pattern": "Y...Y/..Y../GGGGG", "created_at": f"{hoy} 09:00:00+00"}
        for i in range(8)
    ] + [
        {"slack_user_id": "U2", "player_name": "Bea", "wordle_id": 1000 + i, "score": 5,
         "date": hoy, "pattern": "GG.GG/GGYG./GG.GG/GGGGG", "created_at": f"{hoy} 09:00:00+00"}
        for i in range(8)
    ]

    texto = resumen_del_dia(filas, "0", 1007)

    assert "Ana" in texto
    lineas_con_ana = [l for l in texto.splitlines() if "Ana" in l]
    assert len(lineas_con_ana) >= 2, f"el líder sale en su ranking y en su pulla: {lineas_con_ana}"


def test_el_nombre_que_acaba_en_punto_no_duplica_la_puntuacion():
    """«Andrés R.» + una plantilla que acaba en punto daba «Andrés R..». Varios del grupo acaban en punto."""
    from voz import con_nombre

    assert con_nombre("Hoy se ha hablado de {jugador}.", "Andrés R.") == "Hoy se ha hablado de Andrés R."
    assert con_nombre("Manda {jugador} hoy.", "Cata") == "Manda Cata hoy."


# @scenarios el-mas-aplaudido-se-nombra
def test_las_menciones_del_canal_concuerdan_con_dos_personas():
    """Se publicó «Lo de Gabi, Sandra ha levantado al canal»: sin la «y» y con el verbo en singular.

    Las frases se reescribieron para que el verbo no dependa del número, así que una sola plantilla vale para
    uno o para dos. Es lo que el resto del diccionario ya hacía y a las menciones no llegó.
    """
    from voz import menciones

    dos = menciones(
        reacciones={"U1": 5, "U2": 5}, respuestas={}, publicacion={},
        nombres={"U1": "Gabi", "U2": "Sandra"}, jornada=1680,
    )
    uno = menciones(
        reacciones={"U1": 5}, respuestas={}, publicacion={}, nombres={"U1": "Gabi"}, jornada=1680,
    )

    assert "Gabi y Sandra" in dos["aplaudido"], dos["aplaudido"]
    assert ", Sandra" not in dos["aplaudido"], f"enumeración cortada: {dos['aplaudido']}"
    assert "Gabi" in uno["aplaudido"]
