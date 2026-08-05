"""Canoniza la identidad de jugador: de nombre mostrado a identificador de Slack.

Slice: `identidad-canonica-de-jugador` (openspec/slices/identidad/identidad-canonica-de-jugador.md).

Ejecución manual y puntual:

    python3 tools/canonical_identity.py --dry-run    # ensayo obligatorio: cuenta sin escribir
    python3 tools/canonical_identity.py              # escribe y elimina

`canonizar()` recibe el directorio y la tabla **por parámetro**: es lo que permite verificar los siete
escenarios contra dobles en memoria, sin tocar Slack ni Supabase. Los adaptadores reales están al final y
son la parte que solo el ensayo contra producción puede validar.

**Va ANTES del slice del extractor.** Si el extractor emitiera identificadores primero, se duplicarían 32
de las 40 filas de la ventana de reprocesado.

`player_name` no se toca nunca: es la columna que lee la web publicada (ADR 0005).
"""

from __future__ import annotations

import argparse
import os
import re
import ssl
import sys
from dataclasses import dataclass

#: Un identificador de Slack es `U` seguido de mayúsculas, dígitos o guiones bajos. Deliberadamente más
#: estricto que `startswith("U")`: un nombre mostrado como "Ursula" empieza por U y no es un identificador.
IDENTIFICADOR_RE = re.compile(r"U[A-Z0-9_]+")


@dataclass
class Informe:
    """Recuento de una ejecución.

    Las cantidades **se solapan a propósito**: `cruzadas` cuenta detecciones y `fusionadas`/`resueltas`
    cuentan desenlaces, así que una fila cruzada que además duplica una partida ya registrada suma en
    `cruzadas` y en `fusionadas`. La única causa de que el censo baje es `fusionadas`.

    `conflictivas` no estaba en el análisis inicial y existe por seguridad: dos filas del mismo jugador y
    puzzle con **puntuación distinta** no son una fusión, y escribir el identificador violaría el índice
    único `idx_slack_user_wordle_unique` a mitad de la migración. Se cuentan y se dejan intactas para que
    el ensayo las saque a la luz antes de escribir nada.
    """

    resueltas: int = 0
    ya_canonicas: int = 0
    fusionadas: int = 0
    cruzadas: int = 0
    no_resueltas: int = 0
    conflictivas: int = 0
    bloqueadas: int = 0

    def __str__(self) -> str:
        return (
            f"resueltas={self.resueltas} ya_canonicas={self.ya_canonicas} "
            f"fusionadas={self.fusionadas} cruzadas={self.cruzadas} "
            f"no_resueltas={self.no_resueltas} conflictivas={self.conflictivas} "
            f"bloqueadas={self.bloqueadas}"
        )


def es_identificador(valor) -> bool:
    return bool(valor) and IDENTIFICADOR_RE.fullmatch(str(valor)) is not None


def canonizar(directorio, tabla, dry_run: bool = False) -> Informe:
    """Canoniza la identidad de todas las filas. Idempotente.

    **Una atribución cruzada se declara y no se toca.** Cuando el identificador y el nombre señalan a
    personas distintas, ni se reatribuye ni se borra:

    - **Reatribuir fabrica partidas.** Se intentó, apoyándose en que el nombre parecía la señal fiable.
      El canal lo desmintió: de las tres filas cruzadas que no eran duplicados, dos correspondían a días
      en los que la persona del nombre **no publicó nada** y la tercera era copia exacta de la cuadrícula
      de otra. Reatribuir les dio partidas que nadie jugó.
    - **Borrar destruye datos por heurística.** Que un nombre no cuadre con un identificador no demuestra
      que la fila sea falsa; lo demostró el canal, y este cálculo no lo consulta.

    Así que se cuentan y se dejan quietas. Siguen ocupando su clave, lo que puede bloquear a su dueño
    legítimo — y eso también se declara (`bloqueadas`). Quien decida qué hacer con ellas tiene una prueba
    barata: **una fila sin mensaje en el canal se queda sin patrón** tras el backfill.

    Dos pasadas, y el orden importa. La primera decide el **objetivo** de cada fila sin escribir; la
    segunda agrupa por (objetivo, puzzle) y decide quién se queda. Hacerlo en una sola pasada escribiendo
    al vuelo tiene un fallo real: si una fila se resuelve al identificador de otra fila que **ya era
    canónica** y que aparece después, el update viola el índice único a mitad de la migración. Con dos
    pasadas se queda la que ya es canónica y la otra se fusiona sin escribir nada.
    """
    informe = Informe()
    grupos: dict[tuple, list[dict]] = {}

    for fila in tabla.todas():
        identidad = fila.get("slack_user_id")
        nombre = fila.get("player_name")
        resuelto = directorio.get(nombre) if nombre else None

        if es_identificador(identidad) and resuelto is not None and identidad != resuelto:
            # Atribución cruzada: se declara y se deja quieta. No entra en los grupos, así que no puede
            # ganarle la clave a nadie ni fusionar a nadie — pero sigue ocupándola en la tabla, y por eso
            # aparece en `ocupado` unas líneas más abajo.
            informe.cruzadas += 1
            continue

        if resuelto is not None:
            objetivo = resuelto
        elif es_identificador(identidad):
            # El nombre no dice quién es, pero la identidad ya es canónica: no hay nada que decidir, y
            # este comando nunca reatribuye ni borra por sospecha.
            objetivo = identidad
        else:
            informe.no_resueltas += 1
            continue

        grupos.setdefault((objetivo, fila["wordle_id"]), []).append(
            {**fila, "_objetivo": objetivo, "_ya": identidad == objetivo}
        )

    a_escribir: list[dict] = []
    a_borrar: list[dict] = []
    for miembros in grupos.values():
        # Se queda la que ya es canónica si hay alguna: así no hace falta escribirla. Si no hay ninguna,
        # la primera en el orden de entrada (determinista).
        se_queda = next((m for m in miembros if m["_ya"]), miembros[0])

        if se_queda["_ya"]:
            informe.ya_canonicas += 1
        else:
            a_escribir.append(se_queda)

        for miembro in miembros:
            if miembro["id"] == se_queda["id"]:
                continue
            if miembro.get("score") == se_queda.get("score"):
                a_borrar.append(miembro)
            else:
                informe.conflictivas += 1

    # Qué fila ocupa cada clave `(identidad, puzzle)` **ahora mismo**. El índice único de la tabla es
    # exactamente esa clave, así que una escritura solo es legal si su destino está libre.
    ocupado = {(f.get("slack_user_id"), f["wordle_id"]): f["id"] for f in tabla.todas()}

    # 1 · Borrar primero: cada fusión libera una clave que otra fila puede necesitar. Es el caso del
    # puzzle 1478 en producción, donde la fila de una jugadora necesita la clave que ocupa la cruzada
    # que está a punto de fusionarse.
    for victima in a_borrar:
        informe.fusionadas += 1
        ocupado.pop((victima.get("slack_user_id"), victima["wordle_id"]), None)
        if not dry_run:
            tabla.eliminar(victima["id"])

    # 2 · Escribir por punto fijo: en cada pasada se escribe lo que tenga el destino libre, lo que a su
    # vez libera claves para la siguiente. Evita tener que ordenar topológicamente las dependencias.
    pendientes = a_escribir
    while pendientes:
        siguiente, progreso = [], False
        for fila in pendientes:
            destino = (fila["_objetivo"], fila["wordle_id"])
            if ocupado.get(destino, fila["id"]) != fila["id"]:
                siguiente.append(fila)
                continue
            ocupado.pop((fila.get("slack_user_id"), fila["wordle_id"]), None)
            ocupado[destino] = fila["id"]
            informe.resueltas += 1
            progreso = True
            if not dry_run:
                tabla.actualizar(fila["id"], {"slack_user_id": fila["_objetivo"]})
        pendientes = siguiente
        if not progreso:
            break

    # Lo que queda está bloqueado por una fila que no se mueve —una conflictiva sentada en la clave que
    # otra necesita, como el puzzle 1481—. Ni se fuerza ni se borra: se declara y conserva su identidad.
    informe.bloqueadas = len(pendientes)
    return informe


# --- Adaptadores reales -------------------------------------------------------------------------
# macOS con Python de python.org no usa el almacén del sistema, así que slack_sdk falla por
# certificados; el arreglo correcto no es desactivar la verificación TLS —como hace
# extract_slack.py— sino apuntar al bundle de `certifi`.


def contexto_tls() -> ssl.SSLContext:
    """Contexto con verificación completa, usando el bundle de certifi."""
    import certifi

    return ssl.create_default_context(cafile=certifi.where())


#: Etiquetas escritas a mano que **no existen como nombre en Slack**: salen del `USER_IDENTITY` de
#: `tools/add_results.py`, que es su fuente de verdad, y están en las filas que ya guardan un
#: identificador. No se importa ese diccionario porque su módulo abre una conexión a Supabase al
#: importarse, y no se invierte entero **a propósito**: contiene un error de etiquetado
#: (`U02TN4L9HEE: "Raquel"`, que es Clara) y una inversión completa atribuiría a Clara las 111 filas de
#: Raquel Lorenzo. Aquí solo van las tres etiquetas que aparecen de verdad en la tabla.
#:
#: Se aplica como **relleno**, nunca por encima de `users.list`: la resolución por nombre de Slack es
#: evidencia del workspace y esto es una lista escrita a mano.
CURADO: dict[str, str] = {
    "Carlos H.": "U1CKSFSSX",   # Carlos Henestrosa · sin esta entrada las 8 cruzadas no se detectan
    "Andrés R.": "U08U27DFDL2",  # Andres Rey
    "Iván A.": "U09G8KLSE4Q",   # Ivan Antona
}


def resolver_formas(
    candidatos: dict[str, set], autores=frozenset(), curado: dict | None = None
) -> tuple[dict[str, str], list[str]]:
    """De `forma → {identificadores}` a `forma → identificador`, más las formas que quedan ambiguas.

    Función aparte del adaptador **a propósito**: es la lógica de precedencia, y su línea peligrosa es el
    relleno curado. Dentro del adaptador solo se podía verificar hablando con Slack, y un mutante que
    convertía el relleno en override sobrevivía al gate: con el diccionario curado por encima del
    workspace, las 111 filas de Raquel Lorenzo se atribuían a otra persona por un error de etiquetado
    heredado.
    """
    publican = set(autores)
    formas: dict[str, str] = {}
    ambiguas: list[str] = []

    for forma, identificadores in candidatos.items():
        if len(identificadores) == 1:
            formas[forma] = next(iter(identificadores))
            continue
        jugadores = identificadores & publican
        if len(jugadores) == 1:
            formas[forma] = next(iter(jugadores))
        else:
            ambiguas.append(forma)

    # Relleno, no override: lo que ya resolvió el workspace es evidencia; el curado es una lista a mano.
    for forma, identificador in (CURADO if curado is None else curado).items():
        formas.setdefault(forma, identificador)

    return formas, sorted(f for f in ambiguas if f not in formas)


class DirectorioSlack(dict):
    """Nombre mostrado → identificador, construido con `users.list`.

    Tres decisiones, y las tres salen de medir contra los datos reales:

    1. Se indexan **todas** las formas del nombre (handle, real_name, display_name), porque la columna de
       identidad guarda unas u otras según cuándo se ingirió la fila: hay `marcos.granado` y hay
       `Marcos Granado`, y son la misma persona.
    2. Se **incluyen los usuarios desactivados**. Es lo contrario de lo que parece razonable, y filtrarlos
       dejó 110 filas sin resolver en el primer ensayo: tres de los jugadores del histórico ya salieron del
       workspace, y `users.list` sigue devolviendo su nombre y su identificador. Un jugador que se fue jugó
       de verdad, y su identificador no se reasigna nunca.
    3. Si dos personas comparten una forma, gana **la que ha publicado en el canal**. Resuelve los dos
       casos reales sin poner nombres a mano: dos cuentas de la misma persona con el mismo display name
       (una vieja sin publicar nada, 145 mensajes la actual) y dos personas distintas que comparten nombre
       de pila (5 mensajes una, 0 la otra). Se usa "ha publicado" y no "es miembro del canal" por dos
       razones: es la señal pertinente —quien aparece en la tabla es quien juega— y `conversations.members`
       exige el scope `channels:read`, que el bot no tiene. Si el empate persiste, la forma se descarta y
       sus filas salen como no resueltas: la ambigüedad se declara, no se adivina.
    """

    def __init__(self, token: str, autores=frozenset(), curado: dict | None = None) -> None:
        super().__init__()
        from slack_sdk import WebClient

        cliente = WebClient(token=token, ssl=contexto_tls())
        candidatos: dict[str, set] = {}
        cursor = None
        while True:
            respuesta = cliente.users_list(limit=200, cursor=cursor)
            for usuario in respuesta["members"]:
                if usuario.get("is_bot") or usuario["id"] == "USLACKBOT":
                    continue
                perfil = usuario.get("profile") or {}
                formas = {
                    usuario.get("name"),
                    usuario.get("real_name"),
                    perfil.get("real_name"),
                    perfil.get("display_name"),
                    perfil.get("real_name_normalized"),
                    perfil.get("display_name_normalized"),
                }
                for forma in formas:
                    if forma:
                        candidatos.setdefault(forma, set()).add(usuario["id"])
            cursor = (respuesta.get("response_metadata") or {}).get("next_cursor")
            if not cursor:
                break

        formas_resueltas, self.ambiguas = resolver_formas(candidatos, autores=autores, curado=curado)
        self.update(formas_resueltas)


def autores_del_canal(token: str, canal_id: str) -> set[str]:
    """Quién ha publicado en el canal. Es el desempate de las formas de nombre compartidas.

    Recorre el histórico completo con `conversations.history`, que es el scope que el bot tiene.
    """
    from slack_sdk import WebClient

    cliente = WebClient(token=token, ssl=contexto_tls())
    ids: set[str] = set()
    cursor = None
    while True:
        respuesta = cliente.conversations_history(channel=canal_id, limit=200, cursor=cursor)
        ids.update(m["user"] for m in respuesta["messages"] if m.get("user"))
        cursor = (respuesta.get("response_metadata") or {}).get("next_cursor")
        if not cursor:
            return ids


class TablaSupabase:
    """Las filas de `wordle_results`, cargadas una vez y escritas de una en una.

    La lectura pagina de forma explícita: PostgREST devuelve 1000 filas por página y contar sobre una
    sola página ya produjo una cifra equivocada una vez (docs/lecciones.md).
    """

    PAGINA = 1000
    COLUMNAS = "id,wordle_id,player_name,slack_user_id,score"

    def __init__(self, url: str, clave: str) -> None:
        from supabase import create_client

        self.cliente = create_client(url, clave)
        self.filas = self._cargar()

    def _cargar(self) -> list[dict]:
        filas, desplazamiento = [], 0
        while True:
            pagina = (
                self.cliente.table("wordle_results")
                .select(self.COLUMNAS)
                .order("id")  # orden estable: de él depende quién se queda en una fusión
                .range(desplazamiento, desplazamiento + self.PAGINA - 1)
                .execute()
                .data
            )
            if not pagina:
                return filas
            filas.extend(pagina)
            if len(pagina) < self.PAGINA:
                return filas
            desplazamiento += self.PAGINA

    def todas(self) -> list[dict]:
        return list(self.filas)

    def actualizar(self, fila_id, campos: dict) -> None:
        # Se envía SOLO la columna de identidad: nunca un objeto que pudiera pisar puntuación o fecha.
        self.cliente.table("wordle_results").update(campos).eq("id", fila_id).execute()
        for fila in self.filas:
            if fila["id"] == fila_id:
                fila.update(campos)

    def eliminar(self, fila_id) -> None:
        self.cliente.table("wordle_results").delete().eq("id", fila_id).execute()
        self.filas = [f for f in self.filas if f["id"] != fila_id]


def main(argv: list[str] | None = None) -> int:
    from dotenv import load_dotenv

    load_dotenv()

    analizador = argparse.ArgumentParser(
        description="Canoniza la identidad de jugador a identificador de Slack."
    )
    analizador.add_argument(
        "--dry-run", action="store_true", help="cuenta lo que haría sin escribir ni eliminar"
    )
    argumentos = analizador.parse_args(argv)

    token = os.environ.get("SLACK_BOT_TOKEN")
    canal_id = os.environ.get("SLACK_CHANNEL_ID")
    url = os.environ.get("SUPABASE_URL")
    clave = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not all([token, canal_id, url, clave]):
        print("Faltan credenciales en el entorno (.env)", file=sys.stderr)
        return 1

    print("Recorriendo el canal para saber quién juega...")
    autores = autores_del_canal(token, canal_id)

    print("Cargando el directorio del workspace...")
    directorio = DirectorioSlack(token, autores=autores)
    print(f"  {len(directorio)} formas resolubles · {len(autores)} personas han publicado")
    if directorio.ambiguas:
        print(f"  ⚠ {len(directorio.ambiguas)} formas ambiguas sin desempatar: se dejan sin resolver")

    print("Cargando filas de la tabla...")
    tabla = TablaSupabase(url, clave)
    print(f"  {len(tabla.filas)} filas")

    informe = canonizar(directorio, tabla, dry_run=argumentos.dry_run)

    print()
    print("ENSAYO (no se ha escrito nada)" if argumentos.dry_run else "EJECUCIÓN REAL")
    print(f"  {informe}")
    if informe.conflictivas:
        print(
            "  ⚠ HAY FILAS CONFLICTIVAS: mismo jugador y puzzle con puntuación distinta.",
            file=sys.stderr,
        )
        print("     No se han tocado. Revisar antes de la ejecución real.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
