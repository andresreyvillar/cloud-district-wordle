"""El meme del día: varias formas, y varias variantes dentro de cada forma.

Fixtures locales, nunca producción.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from refranero import MEMES
from voz import meme_del_dia

FALLO = 7


def _filas(notas: dict[str, int]) -> list[dict]:
    return [{"jugador": q, "nombre": q, "intentos": n} for q, n in notas.items()]


# El día de dos mundos: alguien resuelve bien y alguien falla. Es el caso genérico.
DOS_MUNDOS = {"Ana": 3, "Bea": 4, "Cris": 5, "Dan": FALLO}


# @scenarios el-meme-del-dia-necesita-que-pase-algo
def test_la_misma_forma_no_publica_siempre_la_misma_frase():
    """**El defecto que motivó esto.** `dia-de-dos-mundos` tenía una sola plantilla y era el 83% de los memes
    publicados: en agosto salió la misma frase cuatro veces en diez jornadas, y lo cazó el dueño leyéndolo.
    """
    salidas = {meme_del_dia(_filas(DOS_MUNDOS), j) for j in range(1, 40)}
    assert len(salidas) == len(MEMES["dia-de-dos-mundos"]), (
        f"la forma tiene {len(MEMES['dia-de-dos-mundos'])} variantes y salieron {len(salidas)}")
    assert all(s and "3" in s and "7" in s for s in salidas), "todas rellenan mejor y peor"


# @scenarios el-meme-del-dia-necesita-que-pase-algo
def test_cada_forma_tiene_varias_variantes():
    """Ninguna condición se queda con una sola plantilla: es lo que produjo la repetición."""
    flacas = {clave: len(v) for clave, v in MEMES.items() if len(v) < 4}
    assert not flacas, f"formas con menos de cuatro variantes: {flacas}"


# @scenarios el-meme-del-dia-necesita-que-pase-algo
def test_la_figura_del_fracaso_gana_al_dia_generico():
    """Quien falla y aun así deja un dibujo es más noticia que la horquilla del día."""
    filas = _filas(DOS_MUNDOS)
    generico = meme_del_dia(filas, 1)
    con_arte = meme_del_dia(filas, 1, figuras={"Dan": "🦜"}, cuadriculas=4)
    assert con_arte != generico, "la figura imposible debe ganar"
    assert "🦜" in con_arte and "Dan" in con_arte, con_arte


# @scenarios el-meme-del-dia-necesita-que-pase-algo
def test_el_empate_multitudinario_sale_con_tres_o_mas():
    # Horquilla corta a propósito: sin el empate esta jornada **no tiene meme**, así que la comparación es
    # contra `None` y no entre dos textos. Comparándolos, bajar el umbral a dos seguía dando textos distintos
    # y la mutación pasaba: el test no ejercitaba el umbral, solo el relleno.
    filas = _filas({"Ana": 3, "Bea": 4, "Cris": 5, "Dan": 6})
    assert meme_del_dia(filas, 1) is None, "la jornada sola no da meme"
    assert meme_del_dia(filas, 1, empatados_arriba=2) is None, "con dos empatados tampoco: no es asamblea"

    de_ese_registro = {p.format(cuantos=n) for p in MEMES["empate-multitudinario"] for n in range(2, 8)}
    for cuantos in (3, 4, 5):
        salida = meme_del_dia(filas, 1, empatados_arriba=cuantos)
        assert salida in de_ese_registro, f"con {cuantos} sí es asamblea: {salida}"
        assert str(cuantos) in salida, salida


# @scenarios sin-forma-reconocida-no-hay-meme
def test_no_se_dice_que_nadie_dibujo_cuando_no_hay_cuadriculas():
    """**La distinción que casi se publica mal.** Que no haya figuras es verdad tanto si nadie dibujó nada
    como si no se guardó ningún patrón, y 61 de las 80 partidas de agosto no lo tienen. Sin cuadrículas no se
    afirma nada.
    """
    from voz import _del_ciclo

    tranquilo = _filas({"Ana": 3, "Bea": 3, "Cris": 4, "Dan": 4})
    # Se compara contra el registro, no contra una palabra suelta: las variantes dicen «lienzos», «obra» o
    # «cuadrículas», así que buscar un literal daría rojo con el comportamiento correcto.
    de_ese_registro = set(MEMES["nadie-dibuja-nada"])

    sin_saber = meme_del_dia(tranquilo, 1, figuras={}, cuadriculas=0)
    plantillas_sin_saber = {p.format(total=n) for p in de_ese_registro for n in range(0, 10)}
    assert sin_saber is None or sin_saber not in plantillas_sin_saber, (
        f"sin cuadrículas no se afirma nada sobre dibujos: {sin_saber}")

    sabiendo = meme_del_dia(tranquilo, 1, figuras={}, cuadriculas=4)
    assert sabiendo == _del_ciclo(MEMES["nadie-dibuja-nada"], 1).format(total=4), (
        f"con cuadrículas y sin arte sí se dice: {sabiendo}")


# @scenarios sin-forma-reconocida-no-hay-meme
def test_una_jornada_sin_forma_sigue_sin_meme():
    """La horquilla corta y sin nada llamativo: no se fuerza un chiste."""
    assert meme_del_dia(_filas({"Ana": 3, "Bea": 4, "Cris": 4}), 1) is None
