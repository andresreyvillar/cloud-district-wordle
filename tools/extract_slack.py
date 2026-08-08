"""Lee los últimos mensajes del canal y los emite para `add_results.py`.

Slice: `ingesta-por-id-de-slack` (openspec/slices/ingesta/ingesta-por-id-de-slack.md).

Formato de la línea, un contrato interno con `add_results.py` (los dos corren encadenados):

    USER_START|<identificador>|<nombre>|<hora>|<texto>

El **identificador** va primero porque es lo que identifica al jugador: no cambia y no se reasigna. El
nombre solo se muestra. Antes se emitía únicamente el nombre, y por eso un renombre en Slack partía a un
jugador en dos.

`linea_de_mensaje()` es pura y se verifica sin red. El cliente de Slack se crea dentro de las funciones que
lo necesitan: creado al importar, el módulo no se podía importar en un test.
"""

import datetime as dt
import os
import ssl
import sys

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")

#: La ventana de la ejecución horaria, **en días**. No en mensajes: medido sobre el histórico, el canal
#: tiene una mediana de 10 mensajes al día y un máximo de 27, así que una ventana de 50 mensajes cubre cinco
#: días de media y **no cubre tres** en la peor racha (52 mensajes). Contar mensajes hace que la cobertura
#: dependa de lo hablador que esté el grupo, que es lo contrario de lo que se le pide a una red de seguridad.
#:
#: Catorce días cubren la peor racha de siete del histórico (79 mensajes) con margen, y sobreviven a un
#: puente con Actions caído. Reingerir lo mismo no duplica —el upsert va por `(slack_user_id, wordle_id)`—,
#: así que el único coste de una ventana ancha son un par de páginas más de API.
VENTANA_EN_DIAS = 14

#: Mensajes por página. Es el máximo cómodo de `conversations.history`.
POR_PAGINA = 100

CAMPO = "|"
MARCA = "USER_START"


def contexto_tls() -> ssl.SSLContext:
    """Contexto con verificación completa, usando el bundle de certifi.

    Este archivo usaba `ssl.CERT_NONE` para esquivar el problema de certificados de macOS, y eso mandaba
    el token del bot por una conexión sin verificar. El arreglo correcto es apuntar al bundle de certifi,
    como ya hacen `backfill_patterns.py` y `canonical_identity.py`.
    """
    import certifi

    return ssl.create_default_context(cafile=certifi.where())


def cliente() -> WebClient:
    return WebClient(token=SLACK_TOKEN, ssl=contexto_tls())


def nombre_visible(usuario: dict) -> str:
    """El nombre que la persona muestra, con la jerarquía de Slack. Último recurso: su identificador."""
    perfil = usuario.get("profile") or {}
    return (
        perfil.get("display_name")
        or perfil.get("real_name")
        or usuario.get("real_name")
        or usuario.get("name")
        or usuario["id"]
    )


def directorio(cli: WebClient | None = None) -> dict:
    """Identificador → nombre visible, paginando.

    Incluye a los **desactivados**: tres jugadores del histórico ya salieron del workspace y sus
    resultados son reales. Sin ellos, sus filas se quedarían sin nombre legible.
    """
    cli = cli or cliente()
    mapa: dict[str, str] = {}
    cursor = None
    try:
        while True:
            respuesta = cli.users_list(limit=200, cursor=cursor)
            for usuario in respuesta["members"]:
                mapa[usuario["id"]] = nombre_visible(usuario)
            cursor = (respuesta.get("response_metadata") or {}).get("next_cursor")
            if not cursor:
                return mapa
    except SlackApiError as error:
        print(
            f"Aviso: no se pudo obtener el directorio ({error.response['error']}). "
            "Se emitirá el identificador como nombre.",
            file=sys.stderr,
        )
        return mapa


def linea_de_mensaje(mensaje: dict, nombres: dict) -> str | None:
    """La línea del lote para un mensaje, o `None` si no debe emitirse.

    Devuelve `None` cuando el mensaje no trae autor: sin autor no hay identidad, y este pipeline no
    inventa una. Los mensajes de sistema (con `subtype`) tampoco se emiten.
    """
    if mensaje.get("subtype") is not None:
        return None
    identificador = mensaje.get("user")
    if not identificador:
        return None

    hora = dt.datetime.fromtimestamp(float(mensaje.get("ts", 0))).strftime("%H:%M")
    nombre = nombres.get(identificador, identificador)
    texto = mensaje.get("text", "")
    return CAMPO.join([MARCA, identificador, nombre, hora, texto])


def corte_de_la_ventana(ahora: dt.datetime, dias: int = VENTANA_EN_DIAS) -> str:
    """El `oldest` de la ventana, como marca de tiempo de Slack.

    `ahora` entra por parámetro: sin eso el corte no se puede verificar con una fecha fija (§10).
    """
    return f"{(ahora - dt.timedelta(days=dias)).timestamp():.6f}"


def mensajes_de_la_ventana(cli, canal: str, ahora: dt.datetime) -> list[dict]:
    """Todos los mensajes del canal desde el corte, en orden cronológico, paginando.

    **Si una página falla, se propaga el error.** Devolver lo que ya se había leído emitiría un lote
    incompleto que se ingiere sin ruido y deja huecos que nadie ve; un fallo lo reporta el workflow.
    """
    oldest = corte_de_la_ventana(ahora)
    mensajes: list[dict] = []
    cursor = None

    while True:
        respuesta = cli.conversations_history(
            channel=canal, limit=POR_PAGINA, cursor=cursor, oldest=oldest
        )
        mensajes += respuesta["messages"]
        cursor = (respuesta.get("response_metadata") or {}).get("next_cursor")
        if not cursor:
            break

    # Slack devuelve del más nuevo al más viejo; el orden cronológico importa porque las filas de la
    # cuadrícula se asocian al último resultado leído.
    return sorted(mensajes, key=lambda m: float(m["ts"]))


def fetch_messages(ahora: dt.datetime | None = None) -> str:
    """El lote de líneas del canal, en orden cronológico.

    `ahora` se resuelve aquí, que es el borde del sistema: de aquí para dentro la fecha viaja por parámetro.
    """
    ahora = ahora or dt.datetime.now(dt.timezone.utc)
    cli = cliente()
    nombres = directorio(cli)
    try:
        mensajes = mensajes_de_la_ventana(cli, CHANNEL_ID, ahora)
    except SlackApiError as error:
        print(f"Error conectando a Slack: {error.response['error']}", file=sys.stderr)
        sys.exit(1)

    lineas = [linea_de_mensaje(mensaje, nombres) for mensaje in mensajes]
    return "\n".join(linea for linea in lineas if linea is not None)


if __name__ == "__main__":
    if not SLACK_TOKEN or not CHANNEL_ID:
        print(
            "Error: Debes configurar SLACK_BOT_TOKEN y SLACK_CHANNEL_ID en el archivo .env",
            file=sys.stderr,
        )
        raise SystemExit(1)
    print(fetch_messages())
