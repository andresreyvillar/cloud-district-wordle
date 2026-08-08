"""Publica en el canal la captura del ranking con su comentario.

Slices: `medallas-en-el-resumen-diario` (lo que dice el mensaje) y `captura-apunta-a-la-v2` (de dónde sale
la imagen y a dónde lleva el enlace).

**Este módulo escribe en Slack delante de todo el grupo.** Los tests no lo ejecutan: le pasan dobles.
"""

import asyncio
import os
import sys
from dataclasses import dataclass

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from supabase import create_client

from badges import texto_de_medallas
from resumen import resumen_del_dia
from seasons import temporada_de

load_dotenv()

#: Las columnas que necesita el resumen. `pattern` entra porque sin ella ninguna medalla de figura podría
#: anunciarse jamás: el dato no llegaría y el fallo sería silencioso.
COLUMNAS = "slack_user_id,player_name,wordle_id,score,date,pattern"

# Configuración
SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")


@dataclass(frozen=True)
class Objetivo:
    """De dónde se saca la captura: **los tres datos van juntos a propósito**.

    Cambiar solo la URL dejaba el workflow esperando quince segundos un `.summary-cards` que la v2 no tiene,
    y el resumen sin publicar. Yendo juntos, el estado roto —URL de una web con selectores de la otra— deja
    de ser expresable.
    """

    nombre: str
    url: str
    espera: str   # el selector que confirma que la página ya tiene datos
    captura: str  # el que se fotografía


#: El subdominio de Workers. **Es de la cuenta de Cloudflare, no de cada Worker**: cambiarlo renombra el
#: host de todos los Workers de la cuenta a la vez y **la URL anterior deja de resolver**, sin redirección.
#: Está aquí, una sola vez, porque el renombrado tiene que poder hacerse sin dejarse una URL a medias — que
#: es la forma en que este proyecto se ha equivocado ya tres veces (docs/lecciones.md, 2026-08-07).
SUBDOMINIO = "clouddistrict"


def _url(worker: str) -> str:
    return f"https://{worker}.{SUBDOMINIO}.workers.dev/"


OBJETIVOS: dict[str, Objetivo] = {
    "v1": Objetivo(
        nombre="v1",
        url=_url("cloud-district-wordle"),
        espera=".summary-cards",
        captura=".container",
    ),
    "v2": Objetivo(
        nombre="v2",
        # La v2 no es otro host: es /2/ del mismo Worker (decisión del 2026-08-07, ver worker/index.js).
        url=_url("cloud-district-wordle") + "2/",
        espera=".liga .fila",
        captura=".liga",
    ),
}

#: El objetivo por defecto es **lo que está desplegado**. El corte a la v2 lo decide esta variable de
#: entorno, no un despliegue de código: `CAPTURA_OBJETIVO=v2` y el grupo deja de ver la v1.
OBJETIVO_POR_DEFECTO = "v1"


def resumen_activo() -> bool:
    """Si el mensaje lleva el resumen compuesto.

    **Apagado por defecto, y a propósito.** Mergear a `main` cambia lo que el cron ejecuta esa misma tarde,
    así que un resumen encendido por defecto significaría que el grupo ve un mensaje nuevo sin que nadie lo
    haya decidido. El interruptor sigue el patrón que ya usa `CAPTURA_OBJETIVO`: se enciende cambiando una
    variable del repositorio, no desplegando código.

        RESUMEN_COMPUESTO=1   el mensaje lleva jugador del día, obra, top 5, álbum y comentarios
    """
    return os.environ.get("RESUMEN_COMPUESTO", "").strip().lower() in ("1", "true", "si", "sí")


def objetivo_de_captura() -> Objetivo:
    """El objetivo configurado. Uno desconocido **aborta**.

    Caer en el objetivo por defecto ante una errata dejaría el bot publicando la web vieja indefinidamente
    sin que nadie se entere, que es la clase de fallo silencioso que esta fase existe para quitar.
    """
    nombre = os.environ.get("CAPTURA_OBJETIVO", OBJETIVO_POR_DEFECTO)
    if nombre not in OBJETIVOS:
        print(
            f"Error: CAPTURA_OBJETIVO={nombre!r} no existe. Objetivos: {', '.join(OBJETIVOS)}",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return OBJETIVOS[nombre]

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
            .select(COLUMNAS)
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


def temporada_del_resumen(resultados) -> str:
    """La temporada a la que pertenece la última jornada, **según el modelo**.

    Recortar la fecha (`str(fecha)[:7]`) funciona solo mientras toda temporada sea un `AAAA-MM`. Con la
    temporada 0 devuelve un identificador que no existe, y las medallas del día salen calculadas sobre una
    temporada vacía.

    Es la **tercera** aparición de esta causa raíz: ya mordió en `badges._de_la_temporada` —181 jornadas sin
    una sola medalla— y en la web, donde `/datos` decía que contaban 70 de 1543 filas. `seasons.temporada_de`
    es la única definición.
    """
    jornada = max(fila["wordle_id"] for fila in resultados)
    fecha = next(f["date"] for f in resultados if f["wordle_id"] == jornada)
    return temporada_de(fecha)


def seccion_de_medallas(resultados):
    """La sección de medallas del mensaje, o cadena vacía.

    La jornada y la temporada se derivan **de los datos**, no del reloj: es el borde del sistema
    (§10 del protocolo), y así el texto es reproducible con los mismos resultados.
    """
    if not resultados:
        return ""
    jornada = max(fila["wordle_id"] for fila in resultados)
    return texto_de_medallas(resultados, temporada_del_resumen(resultados), jornada)


def comentario(seccion_medallas: str, objetivo: Objetivo, resultados=None) -> str:
    """El texto que acompaña a la captura.

    El enlace es **el del objetivo que se ha fotografiado**: mandar una foto de una web y un enlace a otra
    es la forma más rápida de que nadie se fíe de ninguna de las dos.

    `resultados` es opcional para no romper a quien solo quiera la cabecera y el enlace; con ellos, el
    mensaje lleva además el resumen de la jornada (slice `resumen-diario-compuesto`).
    """
    partes = ["¡Aquí tenéis el ranking actualizado! 🔥"]
    if resultados and resumen_activo():
        jornada = max(fila["wordle_id"] for fila in resultados)
        cuerpo = resumen_del_dia(resultados, temporada_del_resumen(resultados), jornada)
        if cuerpo:
            partes.append(cuerpo)
    # Las medallas NO van tras el interruptor. Se intentó, y rompía dos tests de
    # `medallas-en-el-resumen-diario`: son comportamiento especificado de un slice aceptado, y apagarlas por
    # la puerta de atrás sería cambiar una spec sin cambiarla. Consecuencia declarada: al mergear, las
    # medallas empiezan a salir en el canal — que es el fallo que ese slice arregla.
    if seccion_medallas:
        partes.append(seccion_medallas)
    partes.append(f"Podéis ver todas las estadísticas detalladas aquí:\n👉 {objetivo.url}")
    return "\n\n".join(partes)

async def capture_ranking(objetivo: Objetivo) -> str:
    """La captura del objetivo. Cada objetivo trae sus selectores."""
    # Import diferido: la captura necesita un navegador, pero componer el mensaje no.
    from playwright.async_api import async_playwright

    print(f"Iniciando navegador para captura de {objetivo.nombre}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        print(f"Cargando {objetivo.url}...")
        await page.goto(objetivo.url)

        # El selector confirma que la página ya tiene datos, no solo que ha cargado.
        await page.wait_for_selector(objetivo.espera, timeout=15000)
        await asyncio.sleep(3)  # margen para que terminen de dibujarse los gráficos

        ruta = "ranking_snapshot.png"
        contenedor = await page.query_selector(objetivo.captura)
        await contenedor.screenshot(path=ruta)

        await browser.close()
        print("Captura realizada con éxito.")
        return ruta


def upload_to_slack(file_path: str, texto: str) -> bool:
    """Sube la captura. Devuelve si se ha publicado: el que llama decide qué hacer con el fallo."""
    client = WebClient(token=SLACK_TOKEN)
    try:
        print(f"Subiendo captura a Slack (Canal: {CHANNEL_ID})...")
        client.files_upload_v2(
            channel=CHANNEL_ID,
            file=file_path,
            title="Ranking Wordle del Día 🏆",
            initial_comment=texto,
        )
        print("Imagen publicada correctamente.")
        return True
    except SlackApiError as e:
        print(f"Error subiendo a Slack: {e.response['error']}", file=sys.stderr)
        return False


async def publicar(capturar=capture_ranking, subir=upload_to_slack, resultados=None) -> int:
    """El flujo de publicación, con la captura y la subida por parámetro para poder doblarlas.

    **Devuelve el código de salida.** Antes cualquier fallo se imprimía y la ejecución terminaba bien: el
    grupo dejaba de recibir el resumen y en Actions estaba todo verde.
    """
    objetivo = objetivo_de_captura()
    filas = leer_resultados() if resultados is None else resultados
    medallas = seccion_de_medallas(filas)
    print("Medallas de hoy:" if medallas else "Hoy no hay medallas nuevas.")
    if medallas:
        print(medallas)

    try:
        ruta = await capturar(objetivo)
    except Exception as error:  # noqa: BLE001 — cualquier fallo de navegador es un fallo de publicación
        print(f"Error capturando {objetivo.nombre}: {error}", file=sys.stderr)
        return 1

    publicado = subir(ruta, comentario(medallas, objetivo, filas))
    if os.path.exists(ruta):
        os.remove(ruta)
    return 0 if publicado else 1


async def main() -> int:
    if not SLACK_TOKEN or not CHANNEL_ID:
        print("Error: Faltan credenciales en el .env", file=sys.stderr)
        return 1
    return await publicar()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
