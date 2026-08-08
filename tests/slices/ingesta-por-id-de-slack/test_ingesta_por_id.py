"""Escenarios de `ingesta-por-id-de-slack` (Fase 2 — TDD rojo).

Lotes de líneas construidos a mano y un doble de la tabla. Nada de Slack, nada de Supabase.

El doble **impone la clave del upsert** `(slack_user_id, wordle_id)`, que es el índice único de la tabla
real. Un doble más permisivo que producción ya dejó pasar un fallo que reventó una migración a mitad
(docs/lecciones.md, 2026-08-05): si acepta lo que la tabla rechaza, no prueba nada sobre la tabla.
"""

from __future__ import annotations

import datetime

import pytest

MOTIVO = "TDD rojo — la ingesta todavía emite el nombre mostrado"

#: el directorio del workspace tal como lo devuelve `users.list`: identificador → nombre visible
NOMBRES = {
    "U1CKSFSSX": "carlos.h",        # muestra un handle: necesita etiqueta
    "U0ZGXL725": "Luis",            # muestra un nombre legible
    "U02TN4L9HEE": "Claire",        # el diccionario viejo la llamaba "Raquel", que es otra persona
    "U0B1LT5T406": "Marcos Granado",
}

CUADRICULA = [
    ":large_yellow_square::black_large_square::large_green_square::black_large_square::large_yellow_square:",
    ":large_green_square::large_green_square::large_green_square::large_green_square::large_green_square:",
]


class TablaFalsa:
    """Doble con la semántica del `upsert` real: la clave decide si inserta o actualiza."""

    def __init__(self) -> None:
        self.por_clave: dict[tuple, dict] = {}

    def upsert(self, fila: dict, clave: tuple[str, ...]) -> None:
        self.por_clave[tuple(fila[columna] for columna in clave)] = fila

    @property
    def filas(self) -> list[dict]:
        return list(self.por_clave.values())


def encabezado(identificador: str, nombre: str, texto: str, hora: str = "09:15") -> str:
    """La línea de encabezado del lote, con el formato que este slice introduce."""
    return f"USER_START|{identificador}|{nombre}|{hora}|{texto}"


def lote(identificador: str, numero: int, marcador: str = "3", con_cuadricula: bool = False) -> list[str]:
    nombre = NOMBRES.get(identificador, identificador)
    lineas = [encabezado(identificador, nombre, f"La palabra del día #{numero} {marcador}/6")]
    if con_cuadricula:
        lineas += CUADRICULA
    return lineas


# @scenarios resultado-guarda-el-identificador
def test_la_fila_guarda_el_identificador_como_identidad():
    from tools.add_results import filas_a_escribir

    filas, _ = filas_a_escribir(lote("U0ZGXL725", 1672))

    assert len(filas) == 1
    assert filas[0]["slack_user_id"] == "U0ZGXL725"


# @scenarios nombre-mostrado-se-guarda-legible
def test_el_nombre_guardado_es_legible_y_no_el_identificador():
    from tools.add_results import filas_a_escribir

    filas, _ = filas_a_escribir(lote("U0ZGXL725", 1672))

    assert filas[0]["player_name"] == "Luis"
    assert filas[0]["player_name"] != filas[0]["slack_user_id"]


# @scenarios nombre-mostrado-se-guarda-legible
def test_el_diccionario_viejo_no_renombra_a_nadie():
    """Regresión concreta: aplicar `USER_IDENTITY` por identificador llamaba "Raquel" a Clara.

    Medido contra la tabla, ese diccionario renombraría a seis personas. El nombre correcto es el que la
    persona muestra en Slack, salvo etiqueta acordada.
    """
    from tools.add_results import filas_a_escribir

    filas, _ = filas_a_escribir(lote("U02TN4L9HEE", 1672))

    assert filas[0]["player_name"] == "Claire"


# @scenarios etiqueta-acordada-gana-al-handle
def test_la_etiqueta_acordada_gana_al_handle_de_slack():
    from tools.add_results import ETIQUETAS, filas_a_escribir, nombre_para

    assert ETIQUETAS["U1CKSFSSX"] == "Carlos H."
    assert nombre_para("U1CKSFSSX", "carlos.h") == "Carlos H."

    filas, _ = filas_a_escribir(lote("U1CKSFSSX", 1672))
    assert filas[0]["player_name"] == "Carlos H."
    assert filas[0]["slack_user_id"] == "U1CKSFSSX"


# @scenarios renombre-no-crea-jugador-nuevo
def test_un_renombre_no_parte_al_jugador_en_dos():
    """El fallo que este slice cierra: la identidad no depende del nombre, así que renombrarse no crea
    un jugador nuevo."""
    from tools.add_results import CLAVE_DE_CONFLICTO, escribir, filas_a_escribir

    tabla = TablaFalsa()
    antes, _ = filas_a_escribir(lote("U0B1LT5T406", 1672))
    escribir(antes, tabla)

    # la misma persona, con otro nombre mostrado, en otro puzzle
    despues, _ = filas_a_escribir(
        [encabezado("U0B1LT5T406", "marcos.granado", "La palabra del día #1673 4/6")]
    )
    escribir(despues, tabla)

    identidades = {fila["slack_user_id"] for fila in tabla.filas}
    assert identidades == {"U0B1LT5T406"}
    assert len(tabla.filas) == 2
    assert CLAVE_DE_CONFLICTO == ("slack_user_id", "wordle_id")


# @scenarios reprocesar-la-ventana-no-duplica
def test_procesar_dos_veces_el_mismo_mensaje_deja_una_sola_fila():
    """La ventana de 50 mensajes reprocesa lo mismo cada hora."""
    from tools.add_results import escribir, filas_a_escribir

    tabla = TablaFalsa()
    for _ in range(2):
        filas, _ = filas_a_escribir(lote("U0ZGXL725", 1672))
        escribir(filas, tabla)

    assert len(tabla.filas) == 1

    # Y la clave incluye al jugador: dos personas distintas en el MISMO puzzle son dos filas. Sin esta
    # comprobación, una clave que fuese solo el puzzle pasaría el test de arriba sin problema.
    otros, _ = filas_a_escribir(lote("U1CKSFSSX", 1672))
    escribir(otros, tabla)

    assert len(tabla.filas) == 2
    assert {fila["slack_user_id"] for fila in tabla.filas} == {"U0ZGXL725", "U1CKSFSSX"}


# @scenarios mensaje-sin-autor-no-inventa-identidad
def test_un_resultado_sin_autor_no_se_guarda_con_identidad_de_relleno():
    from tools.add_results import filas_a_escribir

    # una línea de resultado suelta, sin encabezado que diga quién la escribió
    filas, descartadas = filas_a_escribir(["La palabra del día #1672 3/6"])

    assert filas == []
    assert len(descartadas) == 1


# @scenarios mensaje-sin-autor-no-inventa-identidad
def test_el_extractor_no_emite_linea_para_un_mensaje_sin_autor():
    from tools.extract_slack import linea_de_mensaje

    assert linea_de_mensaje({"text": "La palabra del día #1672 3/6", "ts": "1785830232.0"}, NOMBRES) is None


# @scenarios resultado-guarda-el-identificador
def test_el_extractor_emite_identificador_y_nombre_en_campos_distintos():
    from tools.extract_slack import linea_de_mensaje

    linea = linea_de_mensaje(
        {"user": "U1CKSFSSX", "text": "La palabra del día #1672 3/6", "ts": "1785830232.0"}, NOMBRES
    )

    campos = linea.split("|")
    assert campos[0] == "USER_START"
    assert campos[1] == "U1CKSFSSX"
    assert campos[2] == "carlos.h"
    assert campos[-1] == "La palabra del día #1672 3/6"


# @scenarios patron-se-sigue-capturando
def test_el_patron_se_captura_igual_con_el_formato_nuevo():
    """El formato de la línea cambia; la captura del patrón no puede cambiar con él."""
    from tools.add_results import filas_a_escribir

    filas, _ = filas_a_escribir(lote("U0ZGXL725", 1672, con_cuadricula=True))

    assert filas[0]["pattern"] == "Y.G.Y/GGGGG"


# @scenarios patron-se-sigue-capturando
def test_la_fila_no_lleva_columnas_que_no_le_corresponden():
    from tools.add_results import filas_a_escribir

    filas, _ = filas_a_escribir(lote("U0ZGXL725", 1672, con_cuadricula=True))

    assert set(filas[0]) == {
        "slack_user_id",
        "player_name",
        "wordle_id",
        "score",
        "date",
        "raw_text",
        "pattern",
    }


# ── la ventana de ingesta ───────────────────────────────────────────────────────────────────────
#
# Doble del cliente de Slack. Imita lo que importa de `conversations.history`: que devuelve del más nuevo
# al más viejo, que pagina con cursor, y que respeta `oldest` como corte.


class SlackFalso:
    """Un canal con mensajes fechados, paginado como lo hace Slack de verdad."""

    def __init__(self, mensajes: list[dict], por_pagina: int = 100, falla_en: int | None = None) -> None:
        #: del más nuevo al más viejo, que es el orden en que la API los devuelve
        self.mensajes = sorted(mensajes, key=lambda m: float(m["ts"]), reverse=True)
        self.por_pagina = por_pagina
        self.falla_en = falla_en  # número de página (1-indexado) en la que revienta
        self.llamadas = 0

    def conversations_history(self, channel: str, limit: int = 100, cursor=None, oldest=None, **resto):
        self.llamadas += 1
        if self.falla_en is not None and self.llamadas == self.falla_en:
            from slack_sdk.errors import SlackApiError

            raise SlackApiError("boom", {"error": "ratelimited"})

        visibles = [m for m in self.mensajes if oldest is None or float(m["ts"]) >= float(oldest)]
        desde = int(cursor or 0)
        pagina = visibles[desde : desde + min(limit, self.por_pagina)]
        siguiente = desde + len(pagina)
        hay_mas = siguiente < len(visibles)
        return {
            "messages": pagina,
            "response_metadata": {"next_cursor": str(siguiente) if hay_mas else ""},
        }


def mensaje(ts: float, texto: str = "La palabra del día #1700 3/6", usuario: str = "U0ZGXL725") -> dict:
    return {"ts": f"{ts:.6f}", "user": usuario, "text": texto}


AHORA = datetime.datetime(2026, 8, 7, 12, 0, tzinfo=datetime.timezone.utc)


def hace(dias: float) -> float:
    return (AHORA - datetime.timedelta(days=dias)).timestamp()


# @scenarios la-ventana-se-mide-en-dias-no-en-mensajes
def test_la_ventana_es_una_fecha_de_corte_y_no_un_numero_de_mensajes():
    """El canal tiene mediana de 10 mensajes al día y máximo 27: contar mensajes hace que la cobertura
    dependa de lo hablador que esté el grupo. La peor racha de tres días son 52 mensajes."""
    from tools.extract_slack import VENTANA_EN_DIAS, corte_de_la_ventana

    corte = corte_de_la_ventana(AHORA)

    assert float(corte) == pytest.approx(hace(VENTANA_EN_DIAS), abs=1)
    assert VENTANA_EN_DIAS >= 7, "menos de una semana no sobrevive a un puente con el cron caído"


# @scenarios la-fecha-de-corte-entra-por-parametro
def test_el_corte_no_lee_el_reloj():
    from tools.extract_slack import corte_de_la_ventana

    otra = datetime.datetime(2025, 1, 15, 8, 30, tzinfo=datetime.timezone.utc)

    assert corte_de_la_ventana(AHORA) != corte_de_la_ventana(otra)
    assert corte_de_la_ventana(AHORA) == corte_de_la_ventana(AHORA)


# @scenarios la-ventana-pagina-hasta-cubrir-los-dias
def test_la_ventana_pagina_hasta_el_corte():
    """120 mensajes en la ventana no caben en una página: sin paginar se perderían los más viejos."""
    from tools.extract_slack import mensajes_de_la_ventana

    canal = SlackFalso([mensaje(hace(i * 0.05), f"#{1700 + i}") for i in range(120)], por_pagina=50)

    mensajes = mensajes_de_la_ventana(canal, "C1", AHORA)

    assert len(mensajes) == 120, f"se han quedado {120 - len(mensajes)} mensajes sin leer"
    assert canal.llamadas >= 3, "con 50 por página hacen falta al menos tres llamadas"
    tiempos = [float(m["ts"]) for m in mensajes]
    assert tiempos == sorted(tiempos), "el orden cronológico importa: la cuadrícula sigue al resultado"


# @scenarios la-ventana-se-mide-en-dias-no-en-mensajes
def test_lo_anterior_al_corte_no_entra():
    from tools.extract_slack import VENTANA_EN_DIAS, mensajes_de_la_ventana

    canal = SlackFalso(
        [mensaje(hace(1)), mensaje(hace(VENTANA_EN_DIAS - 1)), mensaje(hace(VENTANA_EN_DIAS + 30))]
    )

    mensajes = mensajes_de_la_ventana(canal, "C1", AHORA)

    assert len(mensajes) == 2, "el de hace más de la ventana no entra"


# @scenarios la-ventana-se-mide-en-dias-no-en-mensajes
def test_un_dia_muy_hablador_no_desplaza_a_los_dias_anteriores():
    """El fallo que la ventana por mensajes tenía: un día con 27 mensajes se comía los días previos."""
    from tools.extract_slack import mensajes_de_la_ventana

    ruido = [mensaje(hace(0.1 + i * 0.001), "vaya palabra") for i in range(60)]
    resultado_viejo = mensaje(hace(4), "La palabra del día #1669 4/6")
    canal = SlackFalso(ruido + [resultado_viejo], por_pagina=50)

    mensajes = mensajes_de_la_ventana(canal, "C1", AHORA)

    assert any(m["text"].startswith("La palabra del día #1669") for m in mensajes), (
        "60 mensajes de charla en un día no pueden tapar un resultado de hace cuatro"
    )


# @scenarios un-fallo-a-mitad-de-la-paginacion-no-emite-un-lote-a-medias
def test_un_fallo_en_la_segunda_pagina_aborta_en_lugar_de_emitir_medio_lote():
    from slack_sdk.errors import SlackApiError

    from tools.extract_slack import mensajes_de_la_ventana

    canal = SlackFalso([mensaje(hace(i * 0.05)) for i in range(120)], por_pagina=50, falla_en=2)

    with pytest.raises(SlackApiError):
        mensajes_de_la_ventana(canal, "C1", AHORA)
