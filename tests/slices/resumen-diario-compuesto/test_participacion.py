"""La participación de la jornada, de `resumen-diario-compuesto` (Fase 2 — TDD rojo).

Pack: `feat-participacion-y-album-al-arrancar`. Septiembre de cinco jugadores fijos, y el día 16 se suman
nuevos. Los nombres son sintéticos: el repositorio es público.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fixtures_mes import FLOR, TEMPORADA, fila, jornada_de, mes  # noqa: E402

HOY = "2026-09-16"
NUEVOS = ("Fede", "Gus", "Hugo", "Iris", "Juan")


def con_nuevos(nuevos=NUEVOS, hoy=HOY):
    return mes(hoy) + [fila(n, hoy, 4, FLOR) for n in nuevos]


def participacion(filas, hoy=HOY):
    from resumen import bloque_participacion

    return bloque_participacion(filas, jornada_de(hoy))


# @scenarios la-participacion-se-comenta-si-es-noticia
def test_un_record_con_debutantes_dice_cuantos_y_cuanto_es_lo_normal():
    texto = participacion(con_nuevos())

    assert "10 jugadores" in texto
    assert "récord" in texto.lower()
    assert "lo normal: 5" in texto


# @scenarios la-participacion-se-comenta-si-es-noticia
def test_la_coletilla_rota_por_jornada_y_es_siempre_la_misma_para_la_misma_jornada():
    from resumen import COLETILLAS_DE_PARTICIPACION

    hoy, manana = participacion(con_nuevos()), participacion(con_nuevos(hoy="2026-09-17"), hoy="2026-09-17")
    coletilla = lambda texto: next(c for c in COLETILLAS_DE_PARTICIPACION if c in texto)  # noqa: E731

    assert coletilla(hoy) != coletilla(manana)
    assert participacion(con_nuevos()) == hoy


# @scenarios la-participacion-se-comenta-si-es-noticia
def test_mucha_mas_gente_de_lo_normal_es_noticia_aunque_no_haya_debutantes_ni_record():
    # Lo normal son 5 (la mayoría de las jornadas anteriores) y el día 16 juegan 10: mucho más de lo normal.
    # No es récord porque el 31 de agosto jugaron 12, y no hay debutantes porque los cinco extra ya jugaron.
    agosto = [fila(n, "2026-08-31", 4, FLOR) for n in ("Ana", "Bea", "Cris", "Dani", "Eva", "Fede", "Gus", "Hugo", "Iris", "Juan", "Kai", "Leo")]
    fijos = [f for f in mes("2026-09-15")] + [fila(n, d, 4, FLOR) for d in ("2026-09-14", "2026-09-15") for n in ("Fede", "Gus", "Hugo")]
    hoy = [f for f in mes(HOY) if f["date"] == HOY] + [fila(n, HOY, 4, FLOR) for n in ("Fede", "Gus", "Hugo", "Iris", "Juan")]

    texto = participacion(agosto + fijos + hoy)

    assert "10 jugadores" in texto and "récord" not in texto.lower()
    assert "debut" not in texto.lower()


# @scenarios un-dia-normal-no-habla-de-participacion
def test_un_dia_como_los_demas_no_saca_el_bloque():
    assert participacion(mes(HOY)) == ""


# @scenarios un-dia-normal-no-habla-de-participacion
def test_sin_jornadas_anteriores_no_hay_record_ni_bienvenida():
    primer_dia = mes("2026-09-01")

    assert participacion(primer_dia, hoy="2026-09-01") == ""


# @scenarios los-debutantes-se-nombran
def test_con_mas_de_tres_debutantes_se_nombran_tres_y_se_resume_el_resto():
    texto = participacion(con_nuevos())

    assert "Debutan 5" in texto
    assert "Fede, Gus, Hugo y 2 más" in texto
    assert "Iris" not in texto and "Juan" not in texto


# @scenarios los-debutantes-se-nombran
def test_pocos_debutantes_se_nombran_todos_y_concuerda_la_bienvenida():
    texto = participacion(con_nuevos(nuevos=("Fede", "Gus", "Hugo")))

    assert "Fede, Gus y Hugo" in texto
    assert "Bienvenid" in texto


# @scenarios los-debutantes-se-nombran
def test_el_bloque_va_tras_la_jornada_en_el_resumen():
    from resumen import resumen_del_dia

    texto = resumen_del_dia(con_nuevos(), TEMPORADA, jornada_de(HOY))

    assert "10 jugadores" in texto
    assert texto.index("10 jugadores") < texto.index("📊 *Marcador")


def _jornada(fecha: str, nombres) -> list[dict]:
    return [fila(n, fecha, 4, FLOR) for n in nombres]


GENTE = tuple(f"P{i:02d}" for i in range(40))


# @scenarios la-participacion-se-comenta-si-es-noticia
def test_lo_normal_es_la_mediana_de_verdad_aunque_las_jornadas_sean_pares():
    # Referencias 5, 5, 8, 8: la mediana es 6,5 y el umbral 8,1, así que 9 jugadores son noticia. Con la
    # mediana superior (8) el umbral era 10 y no salía. Un récord antiguo en agosto evita que sea récord.
    filas = _jornada("2026-08-31", GENTE[:12])
    for fecha, cuantos in (("2026-09-01", 5), ("2026-09-02", 5), ("2026-09-03", 8), ("2026-09-04", 8)):
        filas += _jornada(fecha, GENTE[:cuantos])
    filas = [f for f in filas if f["date"] != "2026-08-31"] + _jornada("2026-08-30", GENTE[:12])  # domingo
    filas += _jornada("2026-09-07", GENTE[:9])

    texto = participacion(filas, hoy="2026-09-07")

    assert "9 jugadores" in texto and "récord" not in texto.lower()
    assert "lo normal: 7" in texto, texto


# @scenarios la-participacion-se-comenta-si-es-noticia
def test_un_fin_de_semana_o_un_dia_sin_muestra_no_cambia_lo_normal():
    # El domingo 13 juegan 20 y el jueves 10 solo 3: ninguno es jornada de temporada, así que lo normal sigue
    # siendo 5 y no 6.
    filas = mes("2026-09-15") + _jornada("2026-09-13", GENTE[:20])
    filas = [f for f in filas if f["date"] != "2026-09-10"] + _jornada("2026-09-10", GENTE[:3])
    filas += _jornada(HOY, GENTE[:8])

    assert "lo normal: 5" in participacion(filas)


# @scenarios la-participacion-se-comenta-si-es-noticia
def test_lo_normal_mira_solo_las_ultimas_jornadas():
    # Agosto entero con 20 jugadores y septiembre con 5: lo normal del 16 de septiembre son las últimas
    # veinte jornadas, ya casi todas de 5, no la media del verano.
    import datetime

    filas, dia = [], datetime.date(2026, 8, 3)
    while dia < datetime.date(2026, 9, 1):
        if dia.weekday() < 5:
            filas += _jornada(dia.isoformat(), GENTE[:20])
        dia += datetime.timedelta(days=1)
    filas += [f for f in mes("2026-09-15")] + _jornada(HOY, ("Ana", "Bea", "Cris", "Dani", "Eva", "P00", "P01", "P02", "P03"))

    texto = participacion(filas)

    assert "lo normal: 5" in texto, texto


# @scenarios los-debutantes-se-nombran
def test_quien_cambia_de_nombre_no_debuta():
    filas = mes(HOY)
    for f in filas:
        if f["slack_user_id"] == "U_Ana" and f["date"] == HOY:
            f["player_name"] = "Ana Renombrada"
    filas += [fila(n, HOY, 4, FLOR) for n in ("Fede", "Gus", "Hugo")]

    texto = participacion(filas)

    assert "Ana Renombrada" not in texto
    assert "Debutan 3" in texto


# @scenarios el-mensaje-no-crece-con-el-grupo
def test_treinta_debutantes_no_alargan_el_bloque():
    texto = participacion(con_nuevos(nuevos=GENTE[:30]))

    assert len(texto.splitlines()) == 3
    assert "y 27 más" in texto
