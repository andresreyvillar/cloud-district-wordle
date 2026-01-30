import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not URL or not KEY:
    print("Error: Credenciales no encontradas.")
    sys.exit(1)

supabase: Client = create_client(URL, KEY)

# CONSTANTES DE REFERENCIA
# Usamos el dato correcto de hoy como ancla
ANCHOR_ID = 1485
ANCHOR_DATE = datetime(2026, 1, 30).date()

def calculate_date(wordle_id):
    """Calcula la fecha correcta basada en el ID del Wordle"""
    diff_days = wordle_id - ANCHOR_ID
    return ANCHOR_DATE + timedelta(days=diff_days)

def fix_dates():
    print("Iniciando corrección de fechas...")
    
    # Obtener todos los resultados
    # Nota: Si tienes miles de registros, esto debería paginarse. 
    # Para ~300 registros funciona bien de una vez.
    response = supabase.table("wordle_results").select("*").execute()
    records = response.data
    
    updates = 0
    
    for record in records:
        current_id = record['id']
        wordle_num = record['wordle_id']
        db_date_str = record['date']
        
        # Calcular fecha real
        real_date = calculate_date(wordle_num)
        real_date_str = real_date.strftime("%Y-%m-%d")
        
        # Si la fecha está mal, corregirla
        if db_date_str != real_date_str:
            print(f"Corrigiendo {record['player_name']} Wordle #{wordle_num}: {db_date_str} -> {real_date_str}")
            
            supabase.table("wordle_results")\
                .update({"date": real_date_str})\
                .eq("id", current_id)\
                .execute()
            updates += 1

    print("------------------------------------------------")
    print(f"Proceso finalizado. Fechas corregidas: {updates}")

if __name__ == "__main__":
    fix_dates()
