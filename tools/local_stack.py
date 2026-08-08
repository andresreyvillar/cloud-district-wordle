"""Levanta la v2.0 en local corriendo la misma secuencia que los cron de producción.

    python3 tools/local_stack.py                    # calcula, materializa y sirve la web
    python3 tools/local_stack.py --seco             # no escribe nada, ni la instantánea
    python3 tools/local_stack.py --con-ingesta      # además ingiere del canal (escribe filas reales)
    python3 tools/local_stack.py --sin-web          # solo el pipeline, sin servidor

Apunta a **la Supabase de producción**, igual que los cron, porque es donde están los datos reales. Lo que
decide el riesgo no es local-contra-remoto, es qué escribe cada paso:

| Paso                      | Escribe en                    | Por defecto |
|---------------------------|-------------------------------|-------------|
| ingesta del canal         | `wordle_results` (el registro) | **apagada** |
| materializar temporadas   | `season_snapshots` (derivada)  | encendida   |
| resumen diario            | Slack                          | **siempre en seco** |
| servir la web             | nada                           | encendida   |

`season_snapshots` es derivada: se puede borrar y recalcular sin perder nada, y es justo la pieza que se
quiere recalcular veinte veces mientras se afina un umbral. Por eso materializar va encendido.

La ingesta va apagada porque es la única que toca el registro real de partidas de personas. No hace falta
para probar: el cron ya la ejecuta cada hora, así que los datos están ahí.

Y el resumen **nunca publica**. Compone el texto y lo imprime; publicar es lo único que no se deshace.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import datetime
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
PUERTO = 8788

load_dotenv()


def aviso(titulo: str) -> None:
    print(f"\n\033[1m── {titulo}\033[0m")


def credenciales() -> tuple[str, str]:
    url = os.environ.get("SUPABASE_URL")
    clave = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not (url and clave):
        print("Faltan credenciales de Supabase en el .env", file=sys.stderr)
        raise SystemExit(1)
    return url, clave


def declarar(argumentos) -> None:
    """Dice en voz alta qué va a tocar. Una herramienta que escribe en producción no puede ser sigilosa."""
    print("\033[1mv2.0 en local, contra la Supabase de producción\033[0m")
    escribe = []
    no_escribe = ["el resumen diario NO se publica en Slack (solo se imprime)"]
    if argumentos.con_ingesta and not argumentos.seco:
        escribe.append("wordle_results — ingiere del canal, escribe filas reales")
    else:
        no_escribe.append("la ingesta está apagada (--con-ingesta para activarla)")
    if argumentos.seco:
        no_escribe.append("modo seco: NO se escribe la instantánea")
    else:
        escribe.append("season_snapshots — derivada: borrable y recalculable")

    for linea in escribe:
        print(f"  \033[33m escribe \033[0m {linea}")
    for linea in no_escribe:
        print(f"  \033[32m intacto \033[0m {linea}")


def ingerir() -> None:
    aviso("1 · Ingesta del canal  (extract_slack | add_results)")
    extraer = subprocess.run(
        [sys.executable, "-B", "tools/extract_slack.py"], cwd=RAIZ, capture_output=True, text=True
    )
    if extraer.returncode != 0:
        print(extraer.stderr[-800:], file=sys.stderr)
        raise SystemExit("la extracción falló")
    cargar = subprocess.run(
        [sys.executable, "-B", "tools/add_results.py"],
        cwd=RAIZ,
        input=extraer.stdout,
        capture_output=True,
        text=True,
    )
    print(cargar.stdout.strip()[-1200:] or cargar.stderr.strip()[-600:])


def calcular(url: str, clave: str, seco: bool, temporadas_objetivo: list[str] | None) -> dict:
    """Materializa las instantáneas y devuelve las cargas útiles calculadas."""
    sys.path.insert(0, str(RAIZ / "tools"))
    import materialize_seasons as mat
    import seasons

    aviso("2 · Cálculo y materialización")
    resultados = mat.leer_resultados(url, clave)
    lista = seasons.temporadas(resultados)
    print(f"  {len(resultados)} resultados · {len(lista)} temporadas")

    objetivo = temporadas_objetivo or [e["temporada"] for e in lista]
    desconocidas = [t for t in objetivo if t not in {e["temporada"] for e in lista}]
    if desconocidas:
        raise SystemExit(f"no hay datos de {', '.join(desconocidas)}")

    for entrada in lista:
        marca = "◀ en curso" if entrada["estado"] == seasons.EN_CURSO else ""
        elegida = "·" if entrada["temporada"] in objetivo else " "
        print(f"  {elegida} {entrada['temporada']}  {entrada['dias']:2} días  {marca}")

    tabla = None if seco else mat.TablaSupabase(url, clave)
    informe = mat.materializar(
        resultados, objetivo, tabla, datetime.datetime.now(datetime.timezone.utc), dry_run=seco
    )
    print(f"  {'(seco, sin escribir)' if seco else 'escritas'}: {informe}")
    return {t: seasons.instantanea(resultados, t) for t in objetivo}


def resumen(url: str, clave: str) -> None:
    """El texto que el bot publicaría hoy. No publica: eso es lo único que no se deshace."""
    aviso("3 · Resumen diario  (en seco, no se publica)")
    sys.path.insert(0, str(RAIZ / "tools"))
    from post_ranking import comentario, leer_resultados, objetivo_de_captura, seccion_de_medallas

    filas = leer_resultados()
    medallas = seccion_de_medallas(filas)
    # El comentario nombra la web de la que sale la captura, así que necesita el objetivo configurado
    # (`CAPTURA_OBJETIVO`). Esta llamada se quedó atrás cuando el objetivo pasó a ser configurable.
    objetivo = objetivo_de_captura()
    print("  ┌" + "─" * 76)
    for linea in comentario(medallas, objetivo).splitlines():
        print(f"  │ {linea}")
    print("  └" + "─" * 76)
    if not medallas:
        print("  (hoy no hay medallas nuevas, así que el mensaje va sin esa sección)")


def servir(puerto: int) -> None:
    aviso("4 · La web")
    print(f"  http://localhost:{puerto}   ·   Ctrl+C para parar")
    print("  la web lee las instantáneas de Supabase, así que ve lo que se acaba de materializar")
    print(f"    /                    temporada en curso")
    print(f"    /t/2026-07           una temporada cerrada")
    print(f"    /reglas              las reglas que se aplican")
    print(f"    /dev/iconos.html     los iconos de logros")
    subprocess.run([sys.executable, "-B", "tools/serve_v2.py", "--puerto", str(puerto)], cwd=RAIZ)


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(
        description="Levanta la v2.0 en local con la secuencia de los cron de producción."
    )
    analizador.add_argument("--seco", action="store_true", help="no escribe nada, ni la instantánea")
    analizador.add_argument(
        "--con-ingesta", action="store_true", help="ingiere del canal: ESCRIBE filas reales"
    )
    analizador.add_argument("--sin-web", action="store_true", help="solo el pipeline")
    analizador.add_argument("--sin-resumen", action="store_true", help="no compone el resumen")
    analizador.add_argument(
        "--temporada", action="append", help="limita el cálculo a esta temporada (repetible)"
    )
    analizador.add_argument("--puerto", type=int, default=PUERTO)
    argumentos = analizador.parse_args(argv)

    url, clave = credenciales()
    declarar(argumentos)

    if argumentos.con_ingesta and not argumentos.seco:
        ingerir()
    calcular(url, clave, argumentos.seco, argumentos.temporada)
    if not argumentos.sin_resumen:
        resumen(url, clave)
    if not argumentos.sin_web:
        servir(argumentos.puerto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
