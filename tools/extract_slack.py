import os
import sys
import ssl
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")

if not SLACK_TOKEN or not CHANNEL_ID:
    print("Error: Debes configurar SLACK_BOT_TOKEN y SLACK_CHANNEL_ID en el archivo .env", file=sys.stderr)
    sys.exit(1)

# Fix para errores de certificado SSL en macOS
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

client = WebClient(token=SLACK_TOKEN, ssl=ssl_context)

def get_user_map():
    """Crea un mapa de ID de usuario -> Nombre real para mostrar nombres legibles"""
    try:
        # Nota: En workspaces muy grandes esto podría ser lento y requerir paginación
        result = client.users_list()
        user_map = {}
        for u in result["members"]:
            # Jerarquía de nombres para evitar Unknown User
            profile = u.get("profile", {})
            name = (
                profile.get("display_name") or 
                profile.get("real_name") or 
                u.get("real_name") or 
                u.get("name") or 
                u.get("id") # Último recurso: el ID de Slack
            )
            user_map[u["id"]] = name
        return user_map
    except SlackApiError as e:
        print(f"Aviso: No se pudo obtener la lista de usuarios ({e.response['error']}). Se usarán IDs de Slack.", file=sys.stderr)
        return {}

def fetch_messages():
    try:
        # Obtenemos mapa de usuarios para traducir IDs a Nombres (opcional)
        user_map = get_user_map()
        
        # Obtenemos historial (últimos 100 mensajes para cubrir varios días o mucha charla)
        result = client.conversations_history(channel=CHANNEL_ID, limit=100)
        messages = result["messages"]
        
        # Slack devuelve del más nuevo al más viejo. Invertimos para orden cronológico.
        output_buffer = []
        
        for msg in reversed(messages):
            # Ignorar mensajes de sistema (join, leave, etc)
            if "subtype" in msg:
                continue
            
            user_id = msg.get("user")
            text = msg.get("text", "")
            ts = float(msg.get("ts", 0))
            
            # Formatear hora como HH:MM
            time_str = datetime.fromtimestamp(ts).strftime("%H:%M")
            
            # Obtener nombre legible o ID como fallback
            user_name = user_map.get(user_id, user_id)
            
            # Generar formato compatible con add_results.py
            # Usamos un delimitador muy específico para evitar que el texto del usuario lo rompa
            line = f"USER_START|{user_name}|{time_str}|{text}"
            output_buffer.append(line)
            
        return "\n".join(output_buffer)

    except SlackApiError as e:
        print(f"Error conectando a Slack: {e.response['error']}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    content = fetch_messages()
    print(content)