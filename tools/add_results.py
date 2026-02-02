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

# Diccionario Maestro de Usuarios (Handle/ID -> Nombre Bonito)
KNOWN_USERS = {
    "U0797LY6G3H": "Cata",
    "U02U5EHPL3A": "Claire",
    "U09G8KLSE4Q": "Iván A.",
    "ivan.antona": "Iván A.",
    "carlos.h": "Carlos H.",
    "Carlos": "Carlos H.",
    "Andres R": "Andrés R.",
    "Edu Noeda": "Edu N.",
    "Paula Granado": "Paula G.",
    "Iria Dorado": "Iria Dorado",
    "Raquel": "Raquel",
    "Quique": "Quique",
    "Luis": "Luis"
}

def clean_username(raw_name):
    cleaned = raw_name.strip()
    # Si es un ID de Slack o un nombre conocido, mapearlo
    if cleaned in KNOWN_USERS:
        return KNOWN_USERS[cleaned]
    # Si no, intentar búsqueda parcial
    for handle, real_name in KNOWN_USERS.items():
        if handle.lower() in cleaned.lower():
            return real_name
    return cleaned

def calculate_wordle_date(wordle_id):
    diff_days = wordle_id - ANCHOR_ID
    real_date = ANCHOR_DATE + timedelta(days=diff_days)
    return real_date.strftime("%Y-%m-%d")

def parse_and_upload():
    print("Iniciando procesamiento robusto...")
    input_text = sys.stdin.read()
    if not input_text: return

    # Regex para el nuevo formato: USER_START|Nombre|Hora|Texto
    header_pattern = re.compile(r"^USER_START\|(.*?)\|(.*?)\|(.*)$")
    wordle_pattern = re.compile(r"La palabra del día #(\d+) (X|\d)/6", re.IGNORECASE)
    
    new_entries = 0
    current_user = "Unknown User"
    
    lines = input_text.split('\n')
    
    for line in lines:
        # 1. Detectar cambio de usuario
        header_match = header_pattern.match(line)
        if header_match:
            current_user = clean_username(header_match.group(1))
            # El texto del mensaje también puede estar en esta línea
            line_to_check = header_match.group(3)
        else:
            line_to_check = line

        # 2. Buscar Wordle
        wordle_match = wordle_pattern.search(line_to_check)
        if wordle_match:
            wordle_num = int(wordle_match.group(1))
            score_str = wordle_match.group(2).upper()
            score = 7 if score_str == 'X' else int(score_str)
            
            try:
                # Upsert para evitar duplicados sin fallar
                res = _supabase.table("wordle_results").upsert({
                    "player_name": current_user,
                    "wordle_id": wordle_num,
                    "score": score,
                    "date": calculate_wordle_date(wordle_num),
                    "raw_text": line_to_check[:200]
                }, on_conflict="player_name, wordle_id").execute()
                
                print(f"OK: {current_user} - #{wordle_num} ({score}/6)")
                new_entries += 1
            except Exception as e:
                print(f"Error con {current_user}: {e}")

    print(f"Finalizado. Procesados: {new_entries}")

if __name__ == "__main__":
    parse_and_upload()