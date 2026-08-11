"""Escenarios de las señales del canal, de `voz-de-la-jornada` (Fase 2 — TDD rojo).

Pack: `feat-voz-de-la-jornada`.

**Los fixtures son sintéticos y tienen que seguir siéndolo.** No se copian mensajes reales del canal al
repositorio, ni siquiera anonimizados: el repositorio es público y el canal tiene conversaciones de
compañeros identificables.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

MOTIVO = "TDD rojo — tools/senales.py no existe todavía"

#: Un mensaje del canal, con la forma que devuelve `conversations.history`.
def mensaje(usuario: str, ts: float, texto: str, reacciones: int = 0, respuestas: int = 0) -> dict:
    fila = {"user": usuario, "ts": f"{ts:.6f}", "text": texto}
    if reacciones:
        fila["reactions"] = [{"name": "boom", "count": reacciones}]
    if respuestas:
        fila["reply_count"] = respuestas
    return fila


RESULTADO = "La palabra del día #1700 4/6\n🟩🟩🟩🟩🟩"
CHARLA = "jajaja qué palabra"

#: 2026-09-01, en marcas de tiempo de Slack. Fijas: el determinismo es contrato (§10).
MANANA = 1788249600.0   # 08:00
MEDIODIA = 1788264000.0  # 12:00
TARDE = 1788278400.0     # 16:00


# @scenarios la-hora-real-sale-del-canal
def test_la_hora_de_publicacion_es_la_del_mensaje():
    from senales import senales_del_dia

    s = senales_del_dia([mensaje("U1", MANANA, RESULTADO)], bot="UBOT")

    assert s.publicacion["U1"] == pytest.approx(MANANA)


# @scenarios del-canal-solo-salen-numeros
def test_del_canal_no_sale_texto():
    """La comprobación que impide que una conversación del grupo acabe dentro del sistema."""
    from senales import senales_del_dia

    s = senales_del_dia(
        [mensaje("U1", MANANA, RESULTADO, reacciones=3), mensaje("U2", MEDIODIA, CHARLA)],
        bot="UBOT",
    )

    entero = repr(s)
    assert "jajaja" not in entero and "palabra" not in entero, (
        f"el texto de un mensaje ha salido en las señales: {entero}"
    )


# @scenarios quien-falto-sale-del-canal-no-de-la-tabla
def test_la_charla_no_cuenta_como_publicar():
    from senales import senales_del_dia

    s = senales_del_dia([mensaje("U2", MEDIODIA, CHARLA)], bot="UBOT")

    assert "U2" not in s.publicacion, "escribir en el canal no es publicar un resultado"


# @scenarios el-mas-aplaudido-se-nombra
def test_el_mas_aplaudido_es_el_de_mas_reacciones():
    from senales import senales_del_dia

    s = senales_del_dia(
        [mensaje("U1", MANANA, RESULTADO, reacciones=8), mensaje("U2", MEDIODIA, RESULTADO, reacciones=2)],
        bot="UBOT",
    )

    assert s.reacciones["U1"] == 8 and s.reacciones["U2"] == 2


# @scenarios el-mas-aplaudido-se-nombra
def test_el_bot_no_compite_en_su_propio_resumen():
    """El bot publica todas las tardes y sería siempre el más aplaudido y el más comentado de su mensaje.

    **La comprobación va sobre el hilo, y eso importa.** La primera versión de este test le daba al bot un
    mensaje con reacciones pero sin formato de resultado, así que `ES_RESULTADO` ya lo descartaba por otro
    camino y el filtro del bot no protegía nada: quitarlo dejaba la suite en verde. Lo cazó la mutación. Las
    respuestas del hilo se cuentan **antes** de ese filtro, y ahí el filtro del bot es lo único que lo excluye.
    """
    from senales import senales_del_dia

    s = senales_del_dia(
        [mensaje("UBOT", TARDE, "¡Aquí tenéis el ranking!", reacciones=20, respuestas=12),
         mensaje("U1", MANANA, RESULTADO, reacciones=1, respuestas=1)],
        bot="UBOT",
    )

    assert "UBOT" not in s.reacciones
    assert "UBOT" not in s.respuestas, "el hilo del propio bot no lo convierte en el más comentado"


# @scenarios el-que-mas-conversacion-levanta-se-nombra
def test_se_cuentan_las_respuestas_del_hilo_no_su_contenido():
    from senales import senales_del_dia

    s = senales_del_dia([mensaje("U1", MANANA, RESULTADO, respuestas=14)], bot="UBOT")

    assert s.respuestas["U1"] == 14


# @scenarios el-canal-caido-no-tumba-el-resumen
def test_un_canal_vacio_da_senales_vacias_sin_estallar():
    from senales import senales_del_dia

    s = senales_del_dia([], bot="UBOT")

    assert s.publicacion == {} and s.reacciones == {}


# @scenarios el-canal-caido-no-tumba-el-resumen
def test_un_mensaje_malformado_no_se_lleva_las_senales_del_dia():
    """Lo encontró la auditoría adversarial del gate 4d.

    Un `ts` que no es un número o un `count` nulo hacían estallar la derivación entera. El envoltorio del
    borde lo capturaba y el resumen se publicaba, pero **sin ninguna mención**: fallo total donde tenía que
    haber degradación. Un mensaje raro se salta; los demás siguen contando.
    """
    from senales import senales_del_dia

    s = senales_del_dia(
        [
            {"user": "U9", "ts": "no-es-un-numero", "text": RESULTADO},
            {"user": "U8", "ts": "1.0", "text": RESULTADO, "reactions": [{"name": "x"}]},
            mensaje("U1", MANANA, RESULTADO, reacciones=3),
        ],
        bot="UBOT",
    )

    assert s.publicacion["U1"] == pytest.approx(MANANA), "el mensaje bueno sigue contando"
    assert "U9" not in s.publicacion, "el del ts inválido se salta, no tumba el resto"
    assert s.reacciones["U8"] == 0, "una reacción sin count vale cero, no revienta"


# @scenarios el-que-mas-conversacion-levanta-se-nombra
def test_la_charla_vieja_no_es_el_hilo_de_hoy():
    """La ventana del canal es de treinta días para poder contar aperturas, y eso trajo un efecto raro.

    Sin acotar la charla, un hilo de hace tres semanas se publicaba como «el hilo del día». Lo delató el
    mensaje compuesto al ampliar la ventana, no un test.
    """
    from senales import senales_del_dia

    viejo = mensaje("U9", MANANA - 20 * 86400, "una conversación de hace tres semanas", respuestas=40)
    de_hoy = mensaje("U1", MANANA, RESULTADO, respuestas=2)

    s = senales_del_dia([viejo, de_hoy], bot="UBOT", jornada=1700, desde=MANANA - 3600)

    assert "U9" not in s.respuestas, "un hilo de hace tres semanas no es el hilo de hoy"
    assert s.respuestas["U1"] == 2


# @scenarios quien-abre-por-costumbre-se-distingue-de-quien-abre-un-dia
def test_las_aperturas_se_cuentan_por_jornada_declarada():
    """Por el número de puzzle del mensaje, no por su fecha: quien publica el de ayer a medianoche abrió ayer."""
    from senales import veces_que_abrio

    mensajes = [
        {"user": "U1", "ts": "100", "text": "La palabra del día #1700 3/6"},
        {"user": "U2", "ts": "200", "text": "La palabra del día #1700 4/6"},
        {"user": "U2", "ts": "300", "text": "La palabra del día #1701 3/6"},
        {"user": "U1", "ts": "400", "text": "La palabra del día #1701 5/6"},
    ]

    primeros, vistas = veces_que_abrio(mensajes, bot="UBOT")

    assert vistas == 2
    assert primeros == {"U1": 1, "U2": 1}
