import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not URL or not KEY:
    print("Error: Credenciales no encontradas.")
    sys.exit(1)

supabase: Client = create_client(URL, KEY)

# Mapa de UNIFICACIÓN: "Nombre Antiguo": "Nombre Nuevo"
MAPPING = {
    "Andres R": "Andrés R.",
    "Carlos": "Carlos H.",
    "carlos.h": "Carlos H.",
    "Edu Noeda": "Edu N.",
    "ivan.antona": "Iván A.",
    "Paula Granado": "Paula G.",
    "Unknown User": "Eliminar" # Opcional: podemos marcarlos para revisión o eliminarlos
}

def cleanup():
    print("Iniciando unificación de nombres en la base de datos...")
    
    for old_name, new_name in MAPPING.items():
        if new_name == "Eliminar":
            print(f"Borrando registros de '{old_name}'...")
            supabase.table("wordle_results").delete().eq("player_name", old_name).execute()
            continue

        print(f"Unificando '{old_name}' -> '{new_name}'...")
        
        # 1. Obtener registros con el nombre antiguo
        res = supabase.table("wordle_results").select("*").eq("player_name", old_name).execute()
        records = res.data
        
        for rec in records:
            # Intentar actualizar el nombre
            # Nota: Usamos upsert o manejamos el error si ya existe el resultado para el nombre nuevo
            try:
                supabase.table("wordle_results").update({"player_name": new_name}).eq("id", rec["id"]).execute()
            except Exception as e:
                # Si falla (ej. duplicado de wordle_id para el mismo usuario), borramos el antiguo
                if "duplicate key value" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"  Registro duplicado detectado para {new_name} en Wordle #{rec['wordle_id']}. Borrando antiguo.")
                    supabase.table("wordle_results").delete().eq("id", rec["id"]).execute()
                else:
                    print(f"  Error actualizando {rec['id']}: {e}")

    print("------------------------------------------------")
    print("Unificación completada.")

if __name__ == "__main__":
    cleanup()
