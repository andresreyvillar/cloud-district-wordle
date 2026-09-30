"""Los tres podios del resumen diario, de `resumen-diario-compuesto` (Fase 2 — TDD rojo).

Pack: `feat-resumen-con-podios`. Sin red: niveles y marcas del juego entran por parámetro.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fixtures_mes import TEMPORADA, jornada_de, marca, mes, nivel  # noqa: E402


HOY = "2026-09-16"
AYER = "2026-09-15"
NIVELES = [nivel(AYER)]
MARCAS = [marca(AYER, "Cris", 31.2), marca(AYER, "Ana", 35.0), marca(AYER, "Eva", 40.5)]


def resumen(niveles=NIVELES, marcas=MARCAS, filas=None):
    from resumen import resumen_del_dia

    return resumen_del_dia(filas or mes(HOY), TEMPORADA, jornada_de(HOY), niveles=niveles, marcas=marcas)


def bloques_de_codigo(texto: str) -> list[str]:
    return texto.split("```")[1::2]


def podio(puestos, titulo="📊 *Marcador*"):
    from podios import podio_de_texto

    return podio_de_texto(titulo, puestos)


# @scenarios podio-del-marcador
def test_el_marcador_sale_como_podio_de_bloques_con_el_primero_en_el_centro():
    texto = resumen()
    marcador = bloques_de_codigo(texto)[0]

    assert "█" in marcador
    lineas = marcador.strip("\n").splitlines()
    # Ana y Bea empatan con 3,00: comparten el escalón central, el más alto.
    fila_del_primero = next(i for i, l in enumerate(lineas) if "Ana" in l)
    fila_del_tercero = next(i for i, l in enumerate(lineas) if "Cris" in l)
    assert fila_del_primero < fila_del_tercero, "el primero está más arriba"
    columna_de_ana = lineas[fila_del_primero].index("Ana")
    assert 8 <= columna_de_ana <= 22, "el primero va en la columna central"
    assert "3,00" in marcador


# @scenarios podio-del-juego
def test_el_juego_lleva_el_ganador_del_nivel_del_dia_y_su_podio():
    texto = resumen()

    linea = next(l for l in texto.splitlines() if "SuperWordleBros" in l)
    assert f"#{jornada_de(AYER)}" in linea
    assert "Cris" in linea and "0:31.20" in linea and "3 jugadores" in linea
    juego = bloques_de_codigo(texto)[1]
    assert "Cris" in juego and "10" in juego, "el podio del mes con los puntos"


# @scenarios podio-de-figuras
def test_las_figuras_salen_como_podio_con_su_puntuacion_media():
    figuras = bloques_de_codigo(resumen())[2]

    assert "Bea" in figuras and "Ana" in figuras, "geométrico y loro puntúan"
    assert "█" in figuras


# @scenarios los-podios-van-en-orden
def test_los_podios_van_marcador_juego_figuras():
    texto = resumen()

    marcador = texto.index("Marcador")
    juego = texto.index("SuperWordleBros")
    figuras = texto.index("figuras")
    assert marcador < juego < figuras


# @scenarios el-empate-comparte-escalon
def test_dos_empatados_comparten_el_escalon_central_y_cinco_en_el_tercero_se_resumen():
    puestos = [
        {"posicion": 1, "nombre": "Ana", "cifra": "3,00"},
        {"posicion": 1, "nombre": "Bea", "cifra": "3,00"},
        *({"posicion": 3, "nombre": n, "cifra": "4,00"} for n in ("Cris", "Dani", "Eva", "Fede", "Gus")),
    ]

    texto = podio(puestos)

    assert "Ana" in texto and "Bea" in texto
    assert "y 2 más" in texto
    assert "Fede" not in texto and "Gus" not in texto


# @scenarios el-podio-cabe-en-el-movil
def test_ninguna_linea_pasa_de_32_caracteres_aunque_los_nombres_sean_largos():
    puestos = [
        {"posicion": 1, "nombre": "Maximiliano Largo", "cifra": "3,05"},
        {"posicion": 2, "nombre": "Juan (Kokuma)", "cifra": "3,10"},
        {"posicion": 3, "nombre": "Flavia Venturi", "cifra": "3,20"},
    ]

    texto = podio(puestos)

    for linea in bloques_de_codigo(texto)[0].splitlines():
        assert len(linea) <= 32, f"{len(linea)}: {linea!r}"


# @scenarios un-ranking-sin-datos-no-pinta-podio
def test_sin_marcas_no_hay_podio_del_juego_y_los_demas_siguen_en_orden():
    texto = resumen(niveles=[], marcas=[])

    assert "SuperWordleBros" not in texto
    assert len(bloques_de_codigo(texto)) == 2
    assert texto.index("Marcador") < texto.index("figuras")


# @scenarios un-ranking-sin-datos-no-pinta-podio
def test_si_la_lectura_del_juego_falla_el_resumen_sale_sin_su_podio(monkeypatch):
    """El borde que falla se prueba haciéndolo fallar, no pasando listas vacías a la función pura."""
    import post_ranking

    def caida(*_):
        raise ConnectionError("Supabase no responde")

    monkeypatch.setattr(post_ranking, "SUPABASE_URL", "https://ejemplo.supabase.co")
    monkeypatch.setattr(post_ranking, "SUPABASE_KEY", "clave-de-prueba")
    monkeypatch.setattr(post_ranking, "create_client", caida)

    assert post_ranking.leer_juego() == ([], [])


# @scenarios podio-del-marcador
def test_entre_el_titulo_y_el_podio_hay_una_linea_en_blanco():
    """Aire por encima del podio, a petición del dueño: título, línea vacía y el bloque de código."""
    lineas = podio([{"posicion": 1, "nombre": "Ana", "cifra": "3,00"}], titulo="📊 *Marcador*").splitlines()

    assert lineas[:3] == ["📊 *Marcador*", "", "```"]
