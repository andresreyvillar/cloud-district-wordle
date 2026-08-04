import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

from patterns import bloques_de_resultado

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
USER_IDENTITY = {
    "U0797LY6G3H": "Cata",
    "U02U5EHPL3A": "Carlos R.",  # Confirmado Carlos Rodriguez
    "U1CKSFSSX": "Carlos H.",    # Confirmado Carlos Henestrosa
    "U09G8KLSE4Q": "Iván A.",    # Confirmado Ivan Antona
    "U08U27DFDL2": "Andrés R.",  # Confirmado Andres Rey
    "U08KF6V12CB": "Paula G.",   # Confirmado Paula Granado
    "U08BCSARLSZ": "Edu N.",     # Confirmado Edu Noeda
    "U02TN4L9HEE": "Raquel",     # Confirmado Clara/Raquel (Clara González en Slack)
    "U04JUF2EWLC": "Raquel",     # Confirmado Raquel Lorenzo
    "U09PH16T8HJ": "Iria Dorado",# Confirmado Iria Dorado
    "U09Q60LNVT9": "Enrique L.", # Enrique Lopez
    "U04JUF2EWLC": "Raquel L.",
}

# Mapping de emergencia (Nombre/Handle -> ID)
NAME_TO_ID = {
    "carlos.h": "U1CKSFSSX",
    "ivan.antona": "U09G8KLSE4Q",
    "Andres R": "U08U27DFDL2",
}

def get_user_info(slack_id_or_name):
    sid = slack_id_or_name
    if not sid.startswith('U'):
        sid = NAME_TO_ID.get(sid, sid)
    name = USER_IDENTITY.get(sid, sid)
    return sid, name

def calculate_wordle_date(wordle_id):
    diff_days = wordle_id - ANCHOR_ID
    real_date = ANCHOR_DATE + timedelta(days=diff_days)
    return real_date.strftime("%Y-%m-%d")

def parse_and_upload():
    print("Iniciando procesamiento basado en ID verificado...")
    input_text = sys.stdin.read()
    if not input_text: return

    new_entries = 0

    # Las filas de la cuadrícula llegan como líneas sueltas después de su resultado, así que el
    # lote se agrupa en bloques (resultado + filas) antes de escribir. Ver tools/patterns.py.
    for bloque in bloques_de_resultado(input_text.split('\n')):
        if bloque.usuario is None:
            slack_id, display_name = "Unknown", "Unknown User"
        else:
            slack_id, display_name = get_user_info(bloque.usuario)

        try:
            _supabase.table("wordle_results").upsert({
                "slack_user_id": slack_id,
                "player_name": display_name,
                "wordle_id": bloque.numero,
                "score": bloque.score,
                "date": calculate_wordle_date(bloque.numero),
                "raw_text": bloque.texto_resultado[:200],
                "pattern": bloque.patron
            }, on_conflict="slack_user_id, wordle_id").execute()

            dibujo = bloque.patron if bloque.patron else "sin patrón"
            print(f"OK: {display_name} (#{slack_id}) - #{bloque.numero} [{dibujo}]")
            new_entries += 1
        except Exception as e:
            print(f"Error con {display_name}: {e}")

    print(f"Finalizado. Procesados: {new_entries}")

if __name__ == "__main__":
    parse_and_upload()