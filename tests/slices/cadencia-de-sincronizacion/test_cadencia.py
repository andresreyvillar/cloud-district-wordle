"""El criterio de cadencia. Fixtures locales; no consulta el reloj ni la red."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from cadencia import HUECO_MAXIMO_EN_HORAS, MINIMO_DIARIO, evalua, huecos_en_horas


def _cada(horas: float, cuantas: int, dia: str = "2026-09-10") -> list[str]:
    """`cuantas` ejecuciones separadas `horas`, empezando a medianoche."""
    salida = []
    for i in range(cuantas):
        total = int(i * horas * 60)
        salida.append(f"{dia}T{total // 60 % 24:02d}:{total % 60:02d}:00Z")
    return salida


#: El final del día de los fixtures. `hasta` entra por parámetro (§10): sin él el silencio de la cola no se
#: puede juzgar, porque no se distingue de un día que aún no ha terminado.
FIN_DEL_DIA = "2026-09-11T00:00:00Z"


# @scenarios la-cadencia-es-un-requisito-medible
def test_la_cadencia_se_cumple_con_el_minimo_justo():
    """Doce ejecuciones repartidas cada dos horas: el caso límite por los dos lados."""
    veredicto = evalua(_cada(HUECO_MAXIMO_EN_HORAS, MINIMO_DIARIO), FIN_DEL_DIA)
    assert veredicto["cumple"], veredicto
    assert veredicto["ejecuciones"] == MINIMO_DIARIO
    assert veredicto["hueco_maximo"] == HUECO_MAXIMO_EN_HORAS


# @scenarios la-cadencia-es-un-requisito-medible
def test_el_veredicto_no_depende_de_cuando_se_mire():
    """§10: sin reloj. El mismo histórico da siempre el mismo juicio."""
    marcas = _cada(1.5, 16)
    assert evalua(marcas, FIN_DEL_DIA) == evalua(marcas, FIN_DEL_DIA)
    fuente = (Path(__file__).resolve().parents[3] / "tools" / "cadencia.py").read_text(encoding="utf-8")
    assert "now(" not in fuente and "today(" not in fuente, "no puede leer el reloj"


# @scenarios un-dia-flojo-se-nombra
def test_un_dia_por_debajo_del_minimo_se_nombra():
    flojo = _cada(1, MINIMO_DIARIO - 1, dia="2026-09-11")
    bueno = _cada(1, MINIMO_DIARIO, dia="2026-09-12")
    veredicto = evalua(flojo + bueno, "2026-09-13T00:00:00Z")
    assert veredicto["dias_por_debajo"] == ["2026-09-11"], veredicto
    assert not veredicto["cumple"]


# @scenarios el-hueco-se-mide-entre-ejecuciones-consecutivas
def test_doce_agrupadas_no_cumplen_aunque_lleguen_al_minimo():
    """**El caso que distingue frecuencia de cadencia.** Doce ejecuciones en dos horas alcanzan el mínimo
    diario y dejan veintidós horas de silencio: eso no es la cadencia que se pidió.
    """
    agrupadas = _cada(1 / 6, MINIMO_DIARIO)  # doce en dos horas
    veredicto = evalua(agrupadas, FIN_DEL_DIA)
    assert not veredicto["dias_por_debajo"], "el mínimo diario sí se alcanza"
    assert not veredicto["cumple"], "y aun así no cumple: el mínimo solo no basta"


# @scenarios el-hueco-se-mide-entre-ejecuciones-consecutivas
def test_el_hueco_entre_dos_dias_tambien_cuenta():
    """Un silencio nocturno es un silencio: el hueco no se reinicia al cambiar de fecha."""
    marcas = ["2026-09-11T18:00:00Z", "2026-09-12T02:00:00Z"]
    huecos = huecos_en_horas(marcas)
    # El primer hueco es el tramo desde medianoche del día 11 hasta las 18:00; el segundo, el salto nocturno
    # de ocho horas. Cambiar de fecha no reinicia el conteo.
    assert 8.0 in huecos, huecos
    assert max(huecos) == 18.0, f"y el silencio previo también se ve: {huecos}"


# @scenarios sin-ejecuciones-no-se-inventa-un-veredicto
def test_sin_ejecuciones_no_se_afirma_nada():
    veredicto = evalua([])
    assert veredicto["ejecuciones"] == 0
    assert veredicto["hueco_maximo"] == 0.0, "no se inventa un hueco que no existe"
    assert veredicto["huecos_excesivos"] == 0
    assert not veredicto["cumple"], "y sin datos tampoco se afirma que se cumpla"


# @scenarios sin-ejecuciones-no-se-inventa-un-veredicto
def test_una_sola_ejecucion_no_tiene_huecos_pero_falta_al_minimo():
    veredicto = evalua(["2026-09-10T00:00:00Z"], FIN_DEL_DIA)
    assert veredicto["hueco_maximo"] == 24.0, "la ejecución sola deja el día entero en silencio"
    assert veredicto["dias_por_debajo"] == ["2026-09-10"]
    assert not veredicto["cumple"]


# @scenarios la-cadencia-es-un-requisito-medible
def test_el_dia_en_curso_no_se_suspende_por_estar_a_medias():
    """A las once de la mañana un día no puede llevar doce ejecuciones, y suspenderlo por eso haría el
    criterio inútil justo cuando más se consulta: hoy.
    """
    media_manana = _cada(HUECO_MAXIMO_EN_HORAS, 6)
    veredicto = evalua(media_manana, "2026-09-10T11:00:00Z")
    assert veredicto["dias_por_debajo"] == [], "el día de `hasta` se presume en curso"
    assert veredicto["cumple"], veredicto
    # Pero sus silencios sí cuentan: si en esas once horas hubo un parón, se ve.
    con_paron = ["2026-09-10T00:00:00Z", "2026-09-10T10:00:00Z"]
    assert not evalua(con_paron, "2026-09-10T11:00:00Z")["cumple"]


# @scenarios el-hueco-se-mide-entre-ejecuciones-consecutivas
def test_el_silencio_de_la_madrugada_cuenta():
    """Empezar a mediodía deja doce horas de silencio antes de la primera ejecución, y es silencio igual."""
    tarde = _cada(1, 12, dia="2026-09-10")
    desplazadas = [m.replace("T0", "T1") if m[11] == "0" else m for m in tarde]
    veredicto = evalua(desplazadas, FIN_DEL_DIA)
    assert veredicto["hueco_maximo"] >= 10, f"el tramo desde medianoche cuenta: {veredicto}"
