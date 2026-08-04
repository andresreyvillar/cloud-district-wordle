import os
import sys
import asyncio
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from supabase import create_client

from badges import texto_de_medallas

load_dotenv()

# Configuración
SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
WEB_URL = "https://cloud-district-wordle.andres-rey.workers.dev/" # URL de tu web

#: PostgREST devuelve 1000 filas por página: hay que paginar de forma explícita.
#: Contar sobre una sola página ya produjo una cifra falsa una vez (docs/lecciones.md).
PAGINA = 1000


def leer_resultados():
    """Todos los resultados, paginando. Devuelve [] si no hay credenciales de Supabase."""
    if not (SUPABASE_URL and SUPABASE_KEY):
        print("Aviso: sin credenciales de Supabase, el resumen va sin medallas.", file=sys.stderr)
        return []
    cliente = create_client(SUPABASE_URL, SUPABASE_KEY)
    filas, desplazamiento = [], 0
    while True:
        pagina = (
            cliente.table("wordle_results")
            .select("player_name,wordle_id,score,date")
            .order("wordle_id")
            .range(desplazamiento, desplazamiento + PAGINA - 1)
            .execute()
            .data
        )
        if not pagina:
            return filas
        filas.extend(pagina)
        if len(pagina) < PAGINA:
            return filas
        desplazamiento += PAGINA


def seccion_de_medallas(resultados):
    """La sección de medallas del mensaje, o cadena vacía.

    La jornada y la temporada se derivan **de los datos**, no del reloj: es el borde del sistema
    (§10 del protocolo), y así el texto es reproducible con los mismos resultados.
    """
    if not resultados:
        return ""
    jornada = max(fila["wordle_id"] for fila in resultados)
    temporada = next(str(f["date"])[:7] for f in resultados if f["wordle_id"] == jornada)
    return texto_de_medallas(resultados, temporada, jornada)


def comentario(seccion_medallas: str) -> str:
    """El texto que acompaña a la captura. Las medallas se añaden; el enlace no se toca."""
    partes = ["¡Aquí tenéis el ranking actualizado! 🔥"]
    if seccion_medallas:
        partes.append(seccion_medallas)
    partes.append(f"Podéis ver todas las estadísticas detalladas aquí:\n👉 {WEB_URL}")
    return "\n\n".join(partes)

async def capture_ranking():
    # Import diferido: la captura necesita un navegador, pero componer el mensaje no.
    from playwright.async_api import async_playwright

    print("Iniciando navegador para captura...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # Configurar un viewport Widescreen
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        
        print(f"Cargando {WEB_URL}...")
        await page.goto(WEB_URL)
        
        # Esperar a que el elemento del ranking esté visible y tenga datos
        await page.wait_for_selector(".summary-cards", timeout=15000)
        
        # Esperar un poco más para que las gráficas de Plotly se dibujen bien en panorámico
        await asyncio.sleep(3)
        
        # Hacer captura de la zona principal
        screenshot_path = "ranking_snapshot.png"
        
        # Capturamos la zona del contenedor principal
        container = await page.query_selector(".container")
        await container.screenshot(path=screenshot_path)
        
        await browser.close()
        print("Captura widescreen realizada con éxito.")
        return screenshot_path

def upload_to_slack(file_path, texto):
    client = WebClient(token=SLACK_TOKEN)
    try:
        print(f"Subiendo captura a Slack (Canal: {CHANNEL_ID})...")
        response = client.files_upload_v2(
            channel=CHANNEL_ID,
            file=file_path,
            title="Ranking Wordle del Día 🏆",
            initial_comment=texto
        )
        print("Imagen publicada correctamente.")
    except SlackApiError as e:
        print(f"Error subiendo a Slack: {e.response['error']}")

async def main():
    if not SLACK_TOKEN or not CHANNEL_ID:
        print("Error: Faltan credenciales en el .env")
        return

    try:
        medallas = seccion_de_medallas(leer_resultados())
        if medallas:
            print("Medallas de hoy:"); print(medallas)
        else:
            print("Hoy no hay medallas nuevas.")

        path = await capture_ranking()
        upload_to_slack(path, comentario(medallas))
        # Limpiar archivo temporal
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"Error en el proceso: {e}")

if __name__ == "__main__":
    asyncio.run(main())
