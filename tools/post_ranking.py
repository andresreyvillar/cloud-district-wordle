import os
import sys
import asyncio
from playwright.async_api import async_playwright
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

# Configuración
SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")
WEB_URL = "https://cloud-district-wordle.andres-rey.workers.dev/" # URL de tu web

async def capture_ranking():
    print("Iniciando navegador para captura...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # Configurar un viewport similar a un móvil para que el ranking salga bien
        page = await browser.new_page(viewport={'width': 500, 'height': 800})
        
        print(f"Cargando {WEB_URL}...")
        await page.goto(WEB_URL)
        
        # Esperar a que el elemento del ranking esté visible y tenga datos
        # (Ajustamos el selector según tu HTML)
        await page.wait_for_selector(".summary-cards", timeout=10000)
        
        # Esperar un segundo extra para que Plotly/Supabase terminen de pintar
        await asyncio.sleep(2)
        
        # Hacer captura de los elementos principales (Ranking y Resumen)
        screenshot_path = "ranking_snapshot.png"
        
        # Podemos capturar toda la página o solo un área
        container = await page.query_selector(".container")
        await container.screenshot(path=screenshot_path)
        
        await browser.close()
        print("Captura realizada con éxito.")
        return screenshot_path

def upload_to_slack(file_path):
    client = WebClient(token=SLACK_TOKEN)
    try:
        print(f"Subiendo captura a Slack (Canal: {CHANNEL_ID})...")
        response = client.files_upload_v2(
            channel=CHANNEL_ID,
            file=file_path,
            title="Ranking Wordle del Día 🏆",
            initial_comment=f"¡Aquí tenéis el ranking actualizado! 🔥\n\nPodéis ver todas las estadísticas detalladas aquí:\n👉 {WEB_URL}"
        )
        print("Imagen publicada correctamente.")
    except SlackApiError as e:
        print(f"Error subiendo a Slack: {e.response['error']}")

async def main():
    if not SLACK_TOKEN or not CHANNEL_ID:
        print("Error: Faltan credenciales en el .env")
        return

    try:
        path = await capture_ranking()
        upload_to_slack(path)
        # Limpiar archivo temporal
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"Error en el proceso: {e}")

if __name__ == "__main__":
    asyncio.run(main())
