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
    print("Error: Credenciales no encontradas.")
    sys.exit(1)

supabase: Client = create_client(URL, KEY)

def fix_migration():
    print("Iniciando reparación de datos faltantes...")
    
    with open('data/data.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # 1. Limpieza previa en memoria (Deduplicación)
    # Usamos un diccionario para quedarnos solo con la ÚLTIMA versión de cada resultado
    unique_data = {}
    for entry in raw_data:
        try:
            wordle_id = int(entry.get("num", 0))
            user = entry.get("user")
            
            # Clave única
            key = f"{user}_{wordle_id}"
            unique_data[key] = entry
        except:
            continue

    print(f"Total registros en JSON: {len(raw_data)}")
    print(f"Registros únicos a procesar: {len(unique_data)}")

    added_count = 0
    skipped_count = 0
    error_count = 0

    # 2. Inserción Robusta (Uno a uno para evitar fallos en cadena)
    # Esto es más lento pero 100% seguro para reparar huecos
    for key, entry in unique_data.items():
        try:
            wordle_id = int(entry.get("num"))
            raw_score = entry.get("score")
            score = 7 if str(raw_score).upper() == "X" else int(raw_score)
            
            row = {
                "date": entry.get("date"),
                "player_name": entry.get("user"),
                "wordle_id": wordle_id,
                "score": score
            }

            # Intentamos insertar. Si existe, no hacemos nada (ignore_duplicates=True no está disponible en py client direct)
            # Así que usamos upsert pero ignoramos si no cambia nada.
            try:
                # Upsert insertará si no existe, o actualizará si existe.
                # Al estar limpios de duplicados internos, esto no fallará.
                supabase.table("wordle_results").upsert(row, on_conflict="player_name, wordle_id").execute()
                # print(f"Procesado: {row['player_name']} - {wordle_id}")
                added_count += 1
            except Exception as e:
                # Si falla uno, lo reportamos pero seguimos con el siguiente
                print(f"Error en registro {key}: {e}")
                error_count += 1

        except Exception as e:
            print(f"Error procesando datos locales: {entry} -> {e}")

    print("------------------------------------------------")
    print(f"Reparación finalizada.")
    print(f"Registros procesados/asegurados: {added_count}")
    print(f"Errores: {error_count}")

if __name__ == "__main__":
    fix_migration()
