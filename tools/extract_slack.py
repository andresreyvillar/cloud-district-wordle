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

import os
import ssl
import sys
from datetime import datetime

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()

SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")

#: la ventana de la ejecución horaria. Cubre unos 5 días de resultados; ampliarla es la Fase 4.2.
VENTANA = 50

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

    hora = datetime.fromtimestamp(float(mensaje.get("ts", 0))).strftime("%H:%M")
    nombre = nombres.get(identificador, identificador)
    texto = mensaje.get("text", "")
    return CAMPO.join([MARCA, identificador, nombre, hora, texto])


def fetch_messages() -> str:
    """El lote de líneas del canal, en orden cronológico."""
    cli = cliente()
    nombres = directorio(cli)
    try:
        respuesta = cli.conversations_history(channel=CHANNEL_ID, limit=VENTANA)
    except SlackApiError as error:
        print(f"Error conectando a Slack: {error.response['error']}", file=sys.stderr)
        sys.exit(1)

    # Slack devuelve del más nuevo al más viejo; el orden cronológico importa porque las filas de la
    # cuadrícula se asocian al último resultado leído.
    lineas = [linea_de_mensaje(mensaje, nombres) for mensaje in reversed(respuesta["messages"])]
    return "\n".join(linea for linea in lineas if linea is not None)


if __name__ == "__main__":
    if not SLACK_TOKEN or not CHANNEL_ID:
        print(
            "Error: Debes configurar SLACK_BOT_TOKEN y SLACK_CHANNEL_ID en el archivo .env",
            file=sys.stderr,
        )
        raise SystemExit(1)
    print(fetch_messages())
