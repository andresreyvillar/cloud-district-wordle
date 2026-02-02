import sys
import re
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# Wordle #1485 fue el 2026-01-30
ANCHOR_ID = 1485
ANCHOR_DATE = datetime(2026, 1, 30).date()

if not URL or not KEY:
    print("Error: Credenciales de Supabase no encontradas.", file=sys.stderr)
    sys.exit(1)

_supabase: Client = create_client(URL, KEY)

# DICCIONARIO MAESTRO DE IDENTIDAD (ID de Slack -> Nombre que queremos en la Web)
# Esto es la fuente de verdad absoluta.
USER_IDENTITY = {
    "U0797LY6G3H": "Cata",
    "U02U5EHPL3A": "Claire",
    "U09G8KLSE4Q": "Iván A.",
    "U09PH16T8HJ": "Carlos R.",  # Identificado por eliminación
    "U08KF6V12CB": "Carlos H.",  # Identificado por log
    "U08U27DFDL2": "Paula G.",
    "U08BCSARLSZ": "Quique",
    "U02TN4L9HEE": "Raquel",
    "U04JUF2EWLC": "Luis",
    "U1CKSFSSX": "Edu N.",
    "U08KF6V12CB": "Carlos H.",
}

# Mapping de emergencia para cuando el bot no da el ID pero sí el nombre
# (Útil para datos históricos o fallos de la API de Slack)
NAME_TO_ID = {
    "carlos.h": "U08KF6V12CB",
    "Carlos": "U08KF6V12CB",
    "ivan.antona": "U09G8KLSE4Q",
    "Andres R": "U09G8KLSE4Q", # Ajustar si Andrés tiene su propio ID
}

def get_user_info(slack_id_or_name):
    """Retorna (slack_id, display_name)"""
    sid = slack_id_or_name
    
    # Si recibimos un nombre en lugar de un ID, intentamos buscar su ID
    if not sid.startswith('U'):
        sid = NAME_TO_ID.get(sid, sid)
        
    name = USER_IDENTITY.get(sid, sid) # Si no lo conocemos, usamos el ID/Nombre tal cual
    return sid, name

def calculate_wordle_date(wordle_id):
    diff_days = wordle_id - ANCHOR_ID
    real_date = ANCHOR_DATE + timedelta(days=diff_days)
    return real_date.strftime("%Y-%m-%d")

def parse_and_upload():
    print("Iniciando procesamiento basado en ID...")
    input_text = sys.stdin.read()
    if not input_text: return

    header_pattern = re.compile(r"^USER_START\|(.*?)\|(.*?)\|(.*)$")
    wordle_pattern = re.compile(r"La palabra del día #(\d+) (X|\d)/6", re.IGNORECASE)
    
    new_entries = 0
    current_slack_id = "Unknown"
    current_display_name = "Unknown User"
    
    lines = input_text.split('\n')
    
    for line in lines:
        header_match = header_pattern.match(line)
        if header_match:
            raw_user = header_match.group(1).strip()
            current_slack_id, current_display_name = get_user_info(raw_user)
            line_to_check = header_match.group(3)
        else:
            line_to_check = line

        wordle_match = wordle_pattern.search(line_to_check)
        if wordle_match:
            wordle_num = int(wordle_match.group(1))
            score_str = wordle_match.group(2).upper()
            score = 7 if score_str == 'X' else int(score_str)
            
            try:
                # Insertar con slack_user_id
                _supabase.table("wordle_results").upsert({
                    "slack_user_id": current_slack_id,
                    "player_name": current_display_name,
                    "wordle_id": wordle_num,
                    "score": score,
                    "date": calculate_wordle_date(wordle_num),
                    "raw_text": line_to_check[:200]
                }, on_conflict="slack_user_id, wordle_id").execute()
                
                print(f"OK: {current_display_name} (#{current_slack_id}) - #{wordle_num}")
                new_entries += 1
            except Exception as e:
                print(f"Error con {current_display_name}: {e}")

    print(f"Finalizado. Procesados: {new_entries}")

if __name__ == "__main__":
    parse_and_upload()
