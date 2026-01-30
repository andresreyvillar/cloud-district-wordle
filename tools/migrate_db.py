import json
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not URL or not KEY:
    print("Error: Faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en el archivo .env", file=sys.stderr)
    sys.exit(1)

# Iniciar cliente de Supabase
supabase: Client = create_client(URL, KEY)

def migrate():
    print("Iniciando migración de data/data.json a Supabase...")
    
    try:
        with open('data/data.json', 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print("Error: No se encuentra data/data.json")
        sys.exit(1)

    print(f"Se han encontrado {len(raw_data)} registros en el JSON.")
    
    batch = []
    batch_size = 100
    count = 0
    errors = 0

    for entry in raw_data:
        try:
            # Transformar datos
            # num: "1419" -> 1419
            # score: "4" -> 4, "X" -> 7
            
            try:
                wordle_id = int(entry.get("num", 0))
            except ValueError:
                # Si por alguna razón hay texto raro, lo saltamos o ponemos 0
                print(f"Saltando registro con ID inválido: {entry}")
                continue

            raw_score = entry.get("score")
            if str(raw_score).upper() == "X":
                score = 7
            else:
                score = int(raw_score)

            row = {
                "date": entry.get("date"),
                "player_name": entry.get("user"),
                "wordle_id": wordle_id,
                "score": score,
                # Guardamos raw_text vacío por ahora, ya que el JSON antiguo no lo tiene
                "raw_text": None 
            }
            batch.append(row)

            # Insertar en lotes
            if len(batch) >= batch_size:
                data, count = supabase.table("wordle_results").upsert(batch, on_conflict="player_name, wordle_id").execute()
                print(f"Insertados {len(batch)} registros...")
                batch = []

        except Exception as e:
            print(f"Error procesando registro: {entry} -> {e}")
            errors += 1

    # Insertar los restantes
    if batch:
        try:
            data, count = supabase.table("wordle_results").upsert(batch, on_conflict="player_name, wordle_id").execute()
            print(f"Insertados {len(batch)} registros finales.")
        except Exception as e:
            print(f"Error insertando lote final: {e}")
            errors += 1

    print("------------------------------------------------")
    print(f"Migración completada.")
    if errors > 0:
        print(f"Hubo {errors} errores.")
    else:
        print("Todo perfecto, sin errores.")

if __name__ == "__main__":
    migrate()
