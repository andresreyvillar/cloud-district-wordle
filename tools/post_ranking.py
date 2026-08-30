"""Publica en el canal la captura del ranking con su comentario.

Slices: `medallas-en-el-resumen-diario` (lo que dice el mensaje) y `captura-apunta-a-la-v2` (de dónde sale
la imagen y a dónde lleva el enlace).

**Este módulo escribe en Slack delante de todo el grupo.** Los tests no lo ejecutan: le pasan dobles.
"""

import asyncio
import os
import re
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
COLUMNAS = "slack_user_id,player_name,wordle_id,score,date,pattern,created_at"

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
        # Se fotografía **el titular y el podio**, no la página entera. El texto del mensaje ya lleva el
        # marcador y el álbum, así que capturar `.liga` los repetía —y una tira de marcador, logros, álbum
        # y estadísticas llega a Slack como una miniatura ilegible. El titular es lo que la imagen aporta:
        # quién lidera, por cuánto, y las tiras del podio de un vistazo.
        #
        # Se espera **al mismo selector que se fotografía**: esperar a uno y capturar otro deja la puerta
        # abierta a fotografiar algo a medio pintar.
        espera=".hero",
        captura=".hero",
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


#: Días que se leen del canal. **Treinta y no uno**, y no es por capricho: con la ventana del día solo se
#: puede decir «hoy ha abierto X», nunca «como de costumbre», porque una apertura suelta no dice nada de la
#: costumbre de nadie. Treinta días son unas dos páginas de `conversations.history` — barato para lo que
#: aporta— y **no se persiste nada**: los mensajes se descartan al publicar.
#:
#: Lo que es de hoy y lo que es histórico se separa **por el número de puzzle que declara cada mensaje**, no
#: por su fecha: `senales_del_dia` recibe la jornada y filtra.
VENTANA_EN_DIAS = 30


def leer_el_canal(jornada: int | None = None, cliente=None):
    """Los mensajes del día en el canal, para derivar las señales. **Best-effort: nunca lanza.**

    Slice: `voz-de-la-jornada`. Es el **borde** del sistema (§10): aquí se hace la red y se lee el reloj, y lo
    que sale de aquí va por parámetro a funciones puras.

    Un canal que no responde no puede impedir que se publique el marcador, así que cualquier fallo devuelve
    `None` y el resumen sale con lo que sepa la tabla. Se avisa por `stderr` para que quede en el log del
    workflow en lugar de desaparecer.
    """
    import datetime as dt

    from senales import senales_del_dia

    if not (SLACK_TOKEN and CHANNEL_ID):
        return None
    try:
        from extract_slack import contexto_tls

        ahora = dt.datetime.now(dt.timezone.utc)
        desde = (ahora - dt.timedelta(days=VENTANA_EN_DIAS)).timestamp()
        # La charla se acota al día; las aperturas usan la ventana entera. Sin esto, un hilo de hace tres
        # semanas se publicaba como «el hilo del día».
        desde_hoy = ahora.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        cli = cliente or WebClient(token=SLACK_TOKEN, ssl=contexto_tls())
        mensajes, cursor = [], None
        while True:
            respuesta = cli.conversations_history(
                channel=CHANNEL_ID, limit=200, cursor=cursor, oldest=str(desde)
            )
            mensajes += respuesta.get("messages", [])
            cursor = (respuesta.get("response_metadata") or {}).get("next_cursor")
            if not cursor:
                break
        return senales_del_dia(
            mensajes,
            bot=(cli.auth_test() or {}).get("user_id"),
            jornada=jornada,
            desde=desde_hoy,
        )
    except Exception as error:  # noqa: BLE001 — el resumen se publica igual, sea cual sea el fallo
        # **Solo el tipo de excepción.** Este repositorio es público, así que los logs de Actions también lo
        # son. El token viaja en una cabecera y no debería aparecer en el texto de un error, pero «no debería»
        # no es garantía suficiente cuando el coste de equivocarse es un token del bot expuesto para siempre.
        print(
            f"Aviso: no se han podido leer las señales del canal ({type(error).__name__}).",
            file=sys.stderr,
        )
        return None


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


def comentario(seccion_medallas: str, objetivo: Objetivo, resultados=None, senales=None) -> str:
    """El texto que acompaña a la captura.

    El enlace es **el del objetivo que se ha fotografiado**: mandar una foto de una web y un enlace a otra
    es la forma más rápida de que nadie se fíe de ninguna de las dos.

    `resultados` es opcional para no romper a quien solo quiera la cabecera y el enlace; con ellos, el
    mensaje lleva además el resumen de la jornada (slice `resumen-diario-compuesto`).
    """
    partes = ["¡Aquí tenéis el ranking actualizado! 🔥"]
    if resultados and resumen_activo():
        jornada = max(fila["wordle_id"] for fila in resultados)
        cuerpo = resumen_del_dia(
            resultados, temporada_del_resumen(resultados), jornada, senales=senales
        )
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
        # Margen para que terminen de dibujarse los gráficos **y, en la v2, las animaciones de las cifras**.
        # Esto segundo no es un extra: medido, en el instante en que `.hero` aparece el podio muestra «3,48»
        # donde la instantánea dice «3,57», porque el contador está a mitad de subida. A los 200 ms ya son
        # correctas y la animación entera dura 900. Sin esta espera, el bot publicaría en el canal una imagen
        # con cifras que no existen. **No recortar por debajo de un segundo.**
        await asyncio.sleep(3)

        ruta = "ranking_snapshot.png"
        contenedor = await page.query_selector(objetivo.captura)
        if contenedor is None:
            # Sin esto, un selector que no encaja daba `AttributeError: 'NoneType' has no attribute
            # 'screenshot'`, que no dice qué faltaba ni en qué página.
            raise RuntimeError(
                f"no se encontró {objetivo.captura!r} en {objetivo.url} — nada que fotografiar"
            )
        await contenedor.screenshot(path=ruta)

        await browser.close()
        print("Captura realizada con éxito.")
        return ruta


#: El título de la captura **lleva la jornada**, y por eso se puede saber si ya se publicó.
#:
#: Es la señal más barata que existe aquí: no hace falta guardar estado en ninguna parte ni consultar el
#: reloj, basta con mirar si el canal ya tiene una captura de esta jornada. Se prefirió a comparar fechas
#: porque una publicación muy retrasada puede cruzar la medianoche UTC —el 26 de agosto el cron llegó con
#: 2h11m de retraso por una caída de Actions— y ahí la comparación por fecha diría que no se publicó.
TITULO_DE_LA_CAPTURA = "Ranking Wordle del Día 🏆 · #{jornada}"

#: Lo que se busca en el título para saber si ya se publicó. **No se compara el título entero.**
#:
#: Slack devuelve el emoji convertido a su código corto: se envía «Ranking Wordle del Día 🏆 · #1694» y
#: `conversations.history` devuelve «Ranking Wordle del Día :trophy: · #1694». Comparando el título completo
#: la igualdad nunca se cumplía, así que la guarda no detectaba nada y las tres ventanas del cron publicaban:
#: el grupo recibió el resumen **por triplicado** los días 28 y 29 de agosto de 2026.
#:
#: El test que debía cazarlo construía el mensaje falso llamando a `titulo_de`, así que coincidía por
#: construcción y nunca ejercitó la ida y vuelta real.
MARCA_DE_JORNADA = "· #{jornada}"


def titulo_de(jornada: int | None) -> str:
    """El título de la captura de una jornada. Sin jornada, el de siempre."""
    if jornada is None:
        return "Ranking Wordle del Día 🏆"
    return TITULO_DE_LA_CAPTURA.format(jornada=jornada)


def ya_publicada(mensajes: list[dict], jornada: int | None) -> bool:
    """Si el canal ya tiene la captura de esta jornada, buscando **la marca** y no el título entero.

    **Función pura**: entran los mensajes y la jornada, sale un sí o un no. Lo que la hace verificable sin
    tocar Slack, y lo que permite fijar en un test que no se republica.

    Existe porque el 26 de agosto el grupo recibió el mismo resumen dos veces: se lanzó a mano al ver que el
    cron de las 17:00 no había corrido, y el programado llegó 26 minutos después. La protección tiene que
    estar aquí y no en el criterio de quien lo lanza.
    """
    if jornada is None:
        return False
    # La marca no puede ir seguida de otra cifra: `· #1694` es prefijo de `· #16940`, y una búsqueda por
    # subcadena daría por publicada una jornada que no lo está. Lo cazó su propio test.
    marca = re.compile(re.escape(MARCA_DE_JORNADA.format(jornada=jornada)) + r"(?!\d)")
    for mensaje in mensajes:
        if not mensaje.get("bot_id"):
            continue
        for fichero in mensaje.get("files") or []:
            if marca.search(fichero.get("title") or ""):
                return True
    return False


def mensajes_recientes(limite: int = 30, cliente=None) -> list[dict]:
    """Los últimos mensajes del canal, para saber si ya se publicó. Un fallo de lectura devuelve vacío.

    El cliente entra por parámetro para poder doblarlo: sin eso, el repliegue ante un fallo de Slack era
    código sin cubrir —el test de arriba dobla `leer_mensajes` entero, así que nunca pasaba por aquí— y la
    prueba de mutación lo destapó.

    Devolver vacío ante un fallo significa **publicar**: entre no publicar el resumen del día y arriesgar un
    duplicado si además el canal no responde, se elige publicar. Un canal caído no puede dejar al grupo sin
    mensaje.
    """
    try:
        cli = cliente if cliente is not None else WebClient(token=SLACK_TOKEN)
        respuesta = cli.conversations_history(channel=CHANNEL_ID, limit=limite)
        return respuesta.get("messages") or []
    except SlackApiError as error:
        print(f"No se pudo leer el canal para comprobar duplicados: {error}", file=sys.stderr)
        return []


def upload_to_slack(file_path: str, texto: str, titulo: str) -> bool:
    """Sube la captura. Devuelve si se ha publicado: el que llama decide qué hacer con el fallo."""
    client = WebClient(token=SLACK_TOKEN)
    try:
        print(f"Subiendo captura a Slack (Canal: {CHANNEL_ID})...")
        client.files_upload_v2(
            channel=CHANNEL_ID,
            file=file_path,
            title=titulo,
            initial_comment=texto,
        )
        print("Imagen publicada correctamente.")
        return True
    except SlackApiError as e:
        print(f"Error subiendo a Slack: {e.response['error']}", file=sys.stderr)
        return False


async def publicar(
    capturar=capture_ranking, subir=upload_to_slack, resultados=None, leer_mensajes=mensajes_recientes
) -> int:
    """El flujo de publicación, con la captura y la subida por parámetro para poder doblarlas.

    **Devuelve el código de salida.** Antes cualquier fallo se imprimía y la ejecución terminaba bien: el
    grupo dejaba de recibir el resumen y en Actions estaba todo verde.
    """
    objetivo = objetivo_de_captura()
    filas = leer_resultados() if resultados is None else resultados
    jornada = max(fila["wordle_id"] for fila in filas) if filas else None

    # **La comprobación va antes de la captura**, que es el paso caro: abrir un navegador para descubrir
    # después que no hay que publicar sería tirar medio minuto y un runner.
    # Sin jornada no se lee el canal: no hay nada que comparar, y una lectura de más es una llamada de red
    # que además metía a Slack dentro de los tests.
    if jornada is not None and ya_publicada(leer_mensajes(), jornada):
        print(f"La jornada {jornada} ya está publicada en el canal: no se republica.")
        return 0

    medallas = seccion_de_medallas(filas)
    print("Medallas de hoy:" if medallas else "Hoy no hay medallas nuevas.")
    if medallas:
        print(medallas)

    try:
        ruta = await capturar(objetivo)
    except Exception as error:  # noqa: BLE001 — cualquier fallo de navegador es un fallo de publicación
        print(f"Error capturando {objetivo.nombre}: {error}", file=sys.stderr)
        return 1

    # Las señales se leen **después** de la captura: es lo último que se necesita y lo más frágil, así que si
    # el canal no responde ya está todo lo demás listo para publicar.
    publicado = subir(
        ruta,
        comentario(medallas, objetivo, filas, senales=leer_el_canal(jornada)),
        titulo_de(jornada),
    )
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
