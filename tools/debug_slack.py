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
    print("Error: Configura SLACK_BOT_TOKEN y SLACK_CHANNEL_ID en .env")
    sys.exit(1)

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

client = WebClient(token=SLACK_TOKEN, ssl=ssl_context)

def debug_fetch():
    try:
        print(f"--- Conectando al canal: {CHANNEL_ID} ---")
        result = client.conversations_history(channel=CHANNEL_ID, limit=20)
        messages = result["messages"]
        
        print(f"Se han recuperado {len(messages)} mensajes.\n")
        
        for i, msg in enumerate(messages):
            user = msg.get("user", "SISTEMA/BOT")
            text = msg.get("text", "--- SIN TEXTO ---").replace("\n", " ")[:80]
            subtype = msg.get("subtype", "N/A")
            ts = msg.get("ts")
            dt = datetime.fromtimestamp(float(ts)).strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"[{i}] {dt} | User: {user} | Subtype: {subtype}")
            print(f"    Text: {text}...")
            print("-" * 50)

    except SlackApiError as e:
        print(f"Error: {e.response['error']}")

if __name__ == "__main__":
    debug_fetch()
