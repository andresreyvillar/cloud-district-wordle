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


#: Los títulos de los tres podios. Se buscan por título y no por posición: así un cambio de orden solo tumba
#: el test del orden, y una línea del bloque de recta final que nombre al juego no se confunde con su podio.
MARCADOR, JUEGO, FIGURAS = "📊 *Marcador", "🎮 *SuperWordleBros*", "🎨 *Ranking de figuras*"


def podio_tras(texto: str, titulo: str) -> str:
    """El bloque de código que sigue al título de un podio."""
    return texto.split(titulo, 1)[1].split("```")[1]


def podio(puestos, titulo="📊 *Marcador*"):
    from podios import podio_de_texto

    return podio_de_texto(titulo, puestos)


# @scenarios podio-del-marcador
def test_el_marcador_sale_como_podio_de_bloques_con_el_primero_en_el_centro():
    texto = resumen()
    marcador = podio_tras(texto, MARCADOR)

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

    linea = next(l for l in texto.splitlines() if l.startswith(JUEGO))
    assert f"#{jornada_de(AYER)}" in linea
    assert "Cris" in linea and "0:31.20" in linea and "3 jugadores" in linea
    juego = podio_tras(texto, JUEGO)
    assert "Cris" in juego and "10" in juego, "el podio del mes con los puntos"


# @scenarios podio-de-figuras
def test_las_figuras_salen_como_podio_con_su_puntuacion_media():
    figuras = podio_tras(resumen(), FIGURAS)

    assert "Bea" in figuras and "Ana" in figuras, "geométrico y loro puntúan"
    assert "█" in figuras


# @scenarios los-podios-van-en-orden
def test_los_podios_van_marcador_juego_figuras():
    texto = resumen()

    assert texto.index(MARCADOR) < texto.index(JUEGO) < texto.index(FIGURAS)


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

    assert JUEGO not in texto
    assert len(bloques_de_codigo(texto)) == 2
    assert texto.index(MARCADOR) < texto.index(FIGURAS)


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


# @scenarios podio-del-juego
def test_con_dos_ganadores_del_nivel_el_orden_no_depende_de_las_filas():
    empate = [marca(AYER, "Eva", 31.2), marca(AYER, "Cris", 31.2)]

    lineas = {next(l for l in resumen(marcas=m).splitlines() if l.startswith(JUEGO)) for m in (empate, empate[::-1])}

    assert len(lineas) == 1, lineas
    assert "Cris y Eva" in lineas.pop()


# @scenarios el-podio-cabe-en-el-movil
def test_un_nombre_con_acentos_graves_no_cierra_el_bloque_de_codigo():
    texto = podio([{"posicion": 1, "nombre": "Ana```x", "cifra": "3,00"}])

    assert texto.count("```") == 2, texto


# @scenarios un-nombre-no-puede-avisar-a-todo-el-canal
def test_lo_que_sube_el_bot_se_escapa_para_slack(monkeypatch):
    """El borde de verdad: se dobla el cliente de Slack y se mira qué recibe `initial_comment`."""
    import post_ranking

    enviado = {}

    class Cliente:
        def __init__(self, token):
            pass

        def files_upload_v2(self, **argumentos):
            enviado.update(argumentos)

    monkeypatch.setattr(post_ranking, "WebClient", Cliente)
    filas = mes(HOY)
    for fila in filas:
        if fila["player_name"] == "Ana":
            fila["player_name"] = "<!channel> & <https://malo.example|pincha>"
    texto = resumen(filas=filas)

    assert post_ranking.upload_to_slack("captura.png", texto, "título")
    assert "<!channel>" not in enviado["initial_comment"]
    assert "<https://" not in enviado["initial_comment"]
    assert "&lt;!channel&gt;" in enviado["initial_comment"]


# @scenarios un-nombre-no-puede-avisar-a-todo-el-canal
def test_un_mensaje_sin_caracteres_especiales_sale_igual():
    from post_ranking import para_slack

    texto = resumen()

    assert "<" not in texto and "&" not in texto
    assert para_slack(texto) == texto
