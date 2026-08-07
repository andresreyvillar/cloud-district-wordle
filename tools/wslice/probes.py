"""Probes de los `checks:` de un Requirement: comprobaciones mecánicas contra el repositorio.

Hasta ahora **todos** los probes devolvían `indeterminate` (§4, «en v1 del harness todos los probes son
indeterminate»), así que un `checks:` no verificaba nada y todo el peso lo llevaba `verified-by`.

Aquí se implementan los tipos que se pueden decidir **sin red y sin credenciales**, leyendo el propio
repositorio. No es una elección de comodidad: son justo los que habrían cazado dos fallos reales de esta
semana, los dos silenciosos y los dos encontrados a mano días después.

| Tipo | Qué comprueba | El fallo que habría cazado |
|---|---|---|
| `workflow` | que un workflow existe y ejecuta un comando | — |
| `cron` | que un workflow declara esa expresión de cron | — |
| `env-var` | que un paso de un workflow recibe una variable | `post_ranking.yml` no pasaba `SUPABASE_URL`, así que **el resumen diario nunca llevó medallas** |
| `config-key` | que un fichero de configuración tiene esa clave, con ese valor | — |
| `dom-selector` | que un selector existe en las fuentes de una surface | la captura esperaba `.summary-cards`, que **no existe en la v2** |

Los tipos que necesitan la base de datos (`column`, `table`, `constraint`, `rls-policy`) siguen devolviendo
`indeterminate` **con el motivo escrito**: sin credenciales no se pueden decidir, y un probe que dijera
`pass` sin mirar sería peor que no tenerlo.

Cada probe devuelve un `Veredicto`, nunca lanza: un `checks:` mal escrito es `indeterminate` con su motivo,
no una excepción que tumbe el `verify` entero.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .workspace import Workspace

#: Los tipos reservados en §4 que necesitan la base de datos. Se declaran aquí para poder decir *por qué*
#: son indeterminados en lugar de tratarlos como desconocidos.
TIPOS_CON_BASE_DE_DATOS = ("column", "table", "constraint", "rls-policy")

PASS, FAIL, INDETERMINADO = "pass", "fail", "indeterminate"


@dataclass(frozen=True)
class Veredicto:
    tipo: str
    estado: str
    detalle: str


def _texto(ws: Workspace, relativo: str) -> str | None:
    ruta = ws.abs(relativo)
    if not ruta.is_file():
        return None
    return ruta.read_text(encoding="utf-8")


def _workflows(ws: Workspace) -> dict[str, str]:
    """Los workflows del repo, por nombre de fichero. Se leen como texto: basta para lo que se comprueba."""
    directorio = ws.abs(".github/workflows")
    if not directorio.is_dir():
        return {}
    return {
        ruta.name: ruta.read_text(encoding="utf-8")
        for ruta in sorted(directorio.iterdir())
        if ruta.suffix in (".yml", ".yaml")
    }


def _probe_workflow(ws: Workspace, check: dict) -> Veredicto:
    nombre = check.get("workflow") or check.get("file")
    if not nombre:
        return Veredicto("workflow", INDETERMINADO, "el check no dice qué workflow (`workflow:`)")
    contenido = _workflows(ws).get(nombre)
    if contenido is None:
        return Veredicto("workflow", FAIL, f"no existe .github/workflows/{nombre}")
    comando = check.get("runs")
    if comando and comando not in contenido:
        return Veredicto("workflow", FAIL, f"{nombre} no ejecuta {comando!r}")
    return Veredicto("workflow", PASS, f"{nombre} existe" + (f" y ejecuta {comando!r}" if comando else ""))


def _probe_cron(ws: Workspace, check: dict) -> Veredicto:
    expresion = check.get("schedule") or check.get("cron")
    if not expresion:
        return Veredicto("cron", INDETERMINADO, "el check no dice qué cron (`schedule:`)")
    for nombre, contenido in _workflows(ws).items():
        if expresion in contenido:
            return Veredicto("cron", PASS, f"{nombre} declara cron {expresion!r}")
    return Veredicto("cron", FAIL, f"ningún workflow declara cron {expresion!r}")


def _bloque_del_paso(contenido: str, paso: str) -> str | None:
    """El texto de un paso de workflow, desde su `- name:` hasta el siguiente.

    Se hace por texto y no con un parser de YAML a propósito: lo que importa es qué recibe **ese** paso, y
    la estructura anidada de un workflow hace que un `env` global y uno de paso se lean igual en un dict.
    """
    inicio = contenido.find(f"- name: {paso}")
    if inicio == -1:
        return None
    siguiente = contenido.find("- name: ", inicio + 1)
    return contenido[inicio:] if siguiente == -1 else contenido[inicio:siguiente]


def _probe_env_var(ws: Workspace, check: dict) -> Veredicto:
    """Que un paso de un workflow recibe una variable.

    **Este es el probe que justifica el módulo.** `post_ranking.yml` no pasaba `SUPABASE_URL` al paso que
    publica, así que `leer_resultados()` devolvía vacío y el mensaje diario salió sin medallas durante dos
    días sin que nada fallara. Un probe de dos líneas lo habría dicho el primer día.
    """
    variable = check.get("name") or check.get("var")
    nombre = check.get("workflow")
    paso = check.get("step")
    if not (variable and nombre):
        return Veredicto("env-var", INDETERMINADO, "el check necesita `name:` y `workflow:`")
    contenido = _workflows(ws).get(nombre)
    if contenido is None:
        return Veredicto("env-var", FAIL, f"no existe .github/workflows/{nombre}")

    ambito = contenido
    if paso:
        ambito = _bloque_del_paso(contenido, paso)
        if ambito is None:
            return Veredicto("env-var", FAIL, f"{nombre} no tiene un paso llamado {paso!r}")
    if re.search(rf"^\s*{re.escape(variable)}\s*:", ambito, re.M):
        donde = f"el paso {paso!r} de {nombre}" if paso else nombre
        return Veredicto("env-var", PASS, f"{donde} recibe {variable}")
    donde = f"el paso {paso!r} de {nombre}" if paso else nombre
    return Veredicto("env-var", FAIL, f"{donde} NO recibe {variable}")


def _probe_config_key(ws: Workspace, check: dict) -> Veredicto:
    fichero = check.get("file")
    clave = check.get("key")
    if not (fichero and clave):
        return Veredicto("config-key", INDETERMINADO, "el check necesita `file:` y `key:`")
    contenido = _texto(ws, fichero)
    if contenido is None:
        return Veredicto("config-key", FAIL, f"no existe {fichero}")

    # Los .jsonc del proyecto llevan comentarios de línea; se quitan para poder parsearlos.
    limpio = re.sub(r"^\s*//.*$", "", contenido, flags=re.M)
    try:
        datos = json.loads(limpio)
    except json.JSONDecodeError as error:
        return Veredicto("config-key", INDETERMINADO, f"{fichero} no es JSON parseable ({error.msg})")

    actual: object = datos
    for tramo in str(clave).split("."):
        if not isinstance(actual, dict) or tramo not in actual:
            return Veredicto("config-key", FAIL, f"{fichero} no tiene la clave {clave}")
        actual = actual[tramo]

    esperado = check.get("value")
    if esperado is not None and actual != esperado:
        return Veredicto("config-key", FAIL, f"{fichero}:{clave} vale {actual!r}, se esperaba {esperado!r}")
    return Veredicto("config-key", PASS, f"{fichero}:{clave} = {actual!r}")


def _fuentes(ws: Workspace, directorio: str) -> list[Path]:
    base = ws.abs(directorio)
    if not base.is_dir():
        return []
    return [
        ruta
        for ruta in sorted(base.rglob("*"))
        if ruta.is_file() and ruta.suffix in (".js", ".html", ".css", ".svg")
    ]


def _probe_dom_selector(ws: Workspace, check: dict) -> Veredicto:
    """Que un selector existe de verdad en las fuentes de una surface.

    El otro fallo que este módulo habría cazado: la captura diaria esperaba `.summary-cards`, que existe en
    la v1 y **no en la v2**, así que apuntar la URL a la v2 dejaba el workflow esperando quince segundos un
    elemento inexistente y el resumen sin publicar.
    """
    selector = check.get("selector")
    directorio = check.get("in") or check.get("surface")
    if not (selector and directorio):
        return Veredicto("dom-selector", INDETERMINADO, "el check necesita `selector:` y `in:`")
    fuentes = _fuentes(ws, directorio)
    if not fuentes:
        return Veredicto("dom-selector", FAIL, f"no hay fuentes en {directorio}")

    # Se busca la clase o el id sin el prefijo: en el marcado aparece como `class="fila"`, no como `.fila`.
    aguja = selector.lstrip(".#").split()[-1].lstrip(".#") if selector.strip() else ""
    for ruta in fuentes:
        if aguja and aguja in ruta.read_text(encoding="utf-8"):
            return Veredicto("dom-selector", PASS, f"{selector} aparece en {ws.rel(ruta)}")
    return Veredicto("dom-selector", FAIL, f"{selector} no aparece en ninguna fuente de {directorio}")


def _probe_regex(ws: Workspace, check: dict) -> Veredicto:
    """Que un patrón aparece en un fichero. `file:` y `pattern:` son obligatorios."""
    fichero = check.get("file")
    patron = check.get("pattern")
    if not (fichero and patron):
        return Veredicto("regex", INDETERMINADO, "el check necesita `file:` y `pattern:`")
    contenido = _texto(ws, fichero)
    if contenido is None:
        return Veredicto("regex", FAIL, f"no existe {fichero}")
    try:
        encaje = re.search(patron, contenido, re.M)
    except re.error as error:
        return Veredicto("regex", INDETERMINADO, f"patrón inválido: {error}")
    if encaje:
        return Veredicto("regex", PASS, f"{fichero} contiene {patron!r}")
    return Veredicto("regex", FAIL, f"{fichero} NO contiene {patron!r}")


def _probe_index(ws: Workspace, check: dict, contexto: dict | None = None) -> Veredicto:
    """Que **el doble de la tabla imita el índice** que el delta declara.

    Es el destino de la lección del 2026-08-05: diez tests en verde, seis mutantes muertos, y la migración
    real reventó a mitad con `duplicate key value violates unique constraint`. El doble no imponía el índice
    único, así que aceptaba escrituras que la tabla rechaza — y ningún mutante puede cazar eso, porque el
    hueco está en el test y no en el código.

    Lo que este probe **no** hace: comprobar que el índice existe en la base de datos. Eso necesita
    credenciales. Comprueba la mitad que se puede comprobar desde el repositorio, que además es la mitad que
    falló.
    """
    columnas = check.get("columns") or []
    nombre = check.get("name", "?")
    if not columnas:
        return Veredicto("index", INDETERMINADO, "el check no declara `columns:`")
    tests_root = (contexto or {}).get("tests_root")
    if not tests_root:
        return Veredicto("index", INDETERMINADO, f"{nombre}: sin tests_root no se puede mirar el doble")

    base = ws.abs(tests_root)
    if not base.is_dir():
        return Veredicto("index", FAIL, f"{nombre}: no existe {tests_root}")

    for ruta in sorted(base.rglob("*.py")):
        texto = ruta.read_text(encoding="utf-8")
        if all(str(columna) in texto for columna in columnas) and "raise" in texto:
            return Veredicto("index", PASS, f"{nombre}: {ws.rel(ruta)} impone {tuple(columnas)} y lanza")
    return Veredicto(
        "index",
        FAIL,
        f"{nombre}: ningún doble de {tests_root} impone {tuple(columnas)} lanzando — "
        "un doble más permisivo que la tabla acepta escrituras que producción rechaza",
    )


PROBES = {
    "regex": _probe_regex,
    "workflow": _probe_workflow,
    "cron": _probe_cron,
    "env-var": _probe_env_var,
    "config-key": _probe_config_key,
    "dom-selector": _probe_dom_selector,
}


def ejecutar(ws: Workspace, check: dict, contexto: dict | None = None) -> Veredicto:
    """El veredicto de un `check:`. Nunca lanza.

    `contexto` lleva lo que algunos probes necesitan del slice —hoy solo `tests_root`, para el de índice—.
    """
    tipo = str(check.get("type", "")) or "?"
    if tipo == "index":
        try:
            return _probe_index(ws, check, contexto)
        except Exception as error:  # noqa: BLE001
            return Veredicto(tipo, INDETERMINADO, f"el probe ha fallado: {error}")
    if tipo in TIPOS_CON_BASE_DE_DATOS:
        return Veredicto(
            tipo,
            INDETERMINADO,
            f"{tipo} necesita credenciales de la base de datos: no se decide desde el repositorio",
        )
    probe = PROBES.get(tipo)
    if probe is None:
        return Veredicto(tipo, INDETERMINADO, f"no hay probe para el tipo {tipo!r}")
    try:
        return probe(ws, check)
    except Exception as error:  # noqa: BLE001 — un check mal escrito no puede tumbar el verify
        return Veredicto(tipo, INDETERMINADO, f"el probe ha fallado: {error}")


def resumen(veredictos: list[Veredicto]) -> str:
    """El estado agregado de una lista: `fail` manda, luego `indeterminate`, y si no `pass`."""
    estados = {v.estado for v in veredictos}
    if FAIL in estados:
        return FAIL
    if INDETERMINADO in estados or not veredictos:
        return INDETERMINADO
    return PASS
