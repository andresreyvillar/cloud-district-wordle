import sys
import re
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

# Configuración Supabase
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not URL or not KEY:
    # Fallback silencioso si no hay credenciales (para no romper en local sin .env)
    # Pero en producción (GitHub Actions) debería fallar si faltan.
    print("Error: Credenciales de Supabase no encontradas.", file=sys.stderr)
    sys.exit(1)

supabase: Client = create_client(URL, KEY)

# Diccionario de usuarios conocidos para normalización
# (Puedes mover esto a una tabla 'players' en el futuro si quieres)
KNOWN_USERS = {
    "carlos.h": "Carlos H.",
    "ivan.antona": "Iván A.",
    "iria.dorado": "Iria Dorado",
    # Añade aquí más mapeos si es necesario
}

def clean_username(raw_name):
    """
    Intenta limpiar el nombre de usuario.
    1. Busca coincidencias exactas en KNOWN_USERS.
    2. Si no, limpia caracteres extraños.
    """
    # Normalización básica
    cleaned = raw_name.strip()
    
    # Check directo en conocidos
    for handle, real_name in KNOWN_USERS.items():
        if handle.lower() in cleaned.lower():
            return real_name
            
    return cleaned

def parse_and_upload():
    print("Iniciando procesamiento de texto para Supabase...")
    
    # Leer todo el input de stdin
    input_text = sys.stdin.read()
    
    if not input_text:
        print("No se recibió texto de entrada.")
        return

    # Regex para detectar resultados de Wordle
    # Formato esperado: "La palabra del día #1320 3/6"
    pattern = re.compile(r"La palabra del día #(\d+) (X|\d)/6", re.IGNORECASE)
    
    # Separar por líneas (o bloques si vienen pegados)
    # Asumimos que el input viene del script extract_slack.py que formatea así:
    # "User Name  [HH:MM]Mensaje..."
    
    new_entries = 0
    skipped_entries = 0
    
    # Dividimos por saltos de línea que inserta extract_slack.py
    lines = input_text.split('\n')
    
    for line in lines:
        match = pattern.search(line)
        if match:
            wordle_num = int(match.group(1))
            score_str = match.group(2).upper()
            score = 7 if score_str == 'X' else int(score_str)
            
            # Intentar extraer usuario del principio de la línea
            # Formato esperado: "Nombre Usuario  [HH:MM]..."
            user_part = line.split("  [")[0].strip()
            
            # Si la línea no cumple el formato estricto, usamos un default o intentamos limpiar
            if "  [" in line:
                user = clean_username(user_part)
            else:
                # Fallback si el formato no es el de extract_slack
                user = "Unknown User"

            # Verificar si ya existe en DB
            # Consultamos si hay un registro para este usuario y wordle_id
            try:
                existing = supabase.table("wordle_results")\
                    .select("id")\
                    .eq("player_name", user)\
                    .eq("wordle_id", wordle_num)\
                    .execute()
                
                if existing.data and len(existing.data) > 0:
                    print(f"Saltando duplicado: {user} - #{wordle_num}")
                    skipped_entries += 1
                    continue
                
                # Insertar nuevo registro
                new_record = {
                    "player_name": user,
                    "wordle_id": wordle_num,
                    "score": score,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "raw_text": line[:200] # Guardamos un trozo por si acaso
                }
                
                supabase.table("wordle_results").insert(new_record).execute()
                print(f"GUARDADO: {user} - #{wordle_num} ({score}/6)")
                new_entries += 1

            except Exception as e:
                print(f"Error insertando {user}: {e}", file=sys.stderr)

    print("------------------------------------------------")
    print(f"Proceso finalizado. Nuevos: {new_entries}, Saltados: {skipped_entries}")

if __name__ == "__main__":
    parse_and_upload()