import sys
import re
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

# Configuración Supabase
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# CONSTANTES PARA CÁLCULO DE FECHAS
# Wordle #1485 fue el 2026-01-30
ANCHOR_ID = 1485
ANCHOR_DATE = datetime(2026, 1, 30).date()

if not URL or not KEY:
    print("Error: Credenciales de Supabase no encontradas.", file=sys.stderr)
    sys.exit(1)

supabase: Client = create_client(URL, KEY)

# Diccionario de usuarios conocidos para normalización
KNOWN_USERS = {
    "carlos.h": "Carlos H.",
    "Carlos": "Carlos H.",
    "ivan.antona": "Iván A.",
    "iria.dorado": "Iria Dorado",
    "Iria Dorado": "Iria Dorado",
    "Andres R": "Andrés R.",
    "Quique": "Quique",
    "Raquel": "Raquel",
    "Claire": "Claire",
    "Edu Noeda": "Edu N.",
    "Paula Granado": "Paula G.",
    "Luis": "Luis",
    "Cata": "Cata",
    "Nouha": "Nouha"
}

def clean_username(raw_name):
    cleaned = raw_name.strip()
    for handle, real_name in KNOWN_USERS.items():
        if handle.lower() in cleaned.lower():
            return real_name
    return cleaned

def calculate_wordle_date(wordle_id):
    """Calcula la fecha exacta basada en el número de Wordle"""
    diff_days = wordle_id - ANCHOR_ID
    real_date = ANCHOR_DATE + timedelta(days=diff_days)
    return real_date.strftime("%Y-%m-%d")

def parse_and_upload():
    print("Iniciando procesamiento de texto para Supabase...")
    
    # Leer todo el input de stdin
    input_text = sys.stdin.read()
    
    if not input_text:
        print("No se recibió texto de entrada.")
        return

    # Regex para detectar el encabezado de usuario: "Nombre  [HH:MM]"
    header_pattern = re.compile(r"^(.*?)  [[]\d{2}:\d{2}[]]", re.MULTILINE)
    
    # Regex para detectar resultados de Wordle: "La palabra del día #1320 3/6"
    wordle_pattern = re.compile(r"La palabra del día #(\d+) (X|\d)/6", re.IGNORECASE)
    
    new_entries = 0
    skipped_entries = 0
    current_user = "Unknown User"
    
    # Dividimos por líneas para procesar secuencialmente
    lines = input_text.split('\n')
    
    for line in lines:
        # 1. Intentar actualizar el usuario actual
        header_match = header_pattern.match(line)
        if header_match:
            user_part = header_match.group(1).strip()
            current_user = clean_username(user_part)
            continue

        # 2. Buscar resultado de Wordle en esta línea usando el usuario actual
        wordle_match = wordle_pattern.search(line)
        if wordle_match:
            wordle_num = int(wordle_match.group(1))
            score_str = wordle_match.group(2).upper()
            score = 7 if score_str == 'X' else int(score_str)
            
            # Verificar si ya existe en DB
            try:
                existing = supabase.table("wordle_results")\
                    .select("id")\
                    .eq("player_name", current_user)\
                    .eq("wordle_id", wordle_num)\
                    .execute()
                
                if existing.data and len(existing.data) > 0:
                    print(f"Saltando duplicado: {current_user} - #{wordle_num}")
                    skipped_entries += 1
                    continue
                
                # Insertar nuevo registro
                new_record = {
                    "player_name": current_user,
                    "wordle_id": wordle_num,
                    "score": score,
                    "date": calculate_wordle_date(wordle_num),
                    "raw_text": line[:200]
                }
                
                supabase.table("wordle_results").insert(new_record).execute()
                print(f"GUARDADO: {current_user} - #{wordle_num} ({score}/6)")
                new_entries += 1

            except Exception as e:
                print(f"Error procesando {current_user}: {e}", file=sys.stderr)

    print("------------------------------------------------")
    print(f"Proceso finalizado. Nuevos: {new_entries}, Saltados: {skipped_entries}")

if __name__ == "__main__":
    parse_and_upload()
