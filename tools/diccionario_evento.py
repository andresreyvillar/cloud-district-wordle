"""Genera el diccionario de palabras válidas de 5 letras del juego del evento.

    python3 tools/diccionario_evento.py es_ES.dic es_ES.aff

Parte del diccionario ortográfico del español de LibreOffice (proyecto RLA-ES), que sigue la norma de la RAE y se
distribuye con triple licencia GPL v3+ / LGPL v3+ / MPL 1.1+ (https://github.com/sbosio/rla-es). El diccionario de la
RAE no tiene una licencia que permita copiarlo, y este repositorio es público.

Hunspell guarda cada palabra con sus reglas de afijos (`casa/S` → «casa», «casas»), así que aquí se expanden: cada
entrada con sus sufijos y prefijos, y los sufijos encadenados. Se quedan las formas en minúscula (fuera nombres
propios y siglas), sin tildes ni diéresis, con la ñ como letra propia, y de exactamente 5 letras.

Escribe dos ficheros a partir de la misma lista:
- `v2/assets/evento/palabras.txt` — la web la usa para avisar al momento de una palabra que no vale.
- `supabase/migrations/20261112130000_load_event_words.sql` — el servidor, que es quien decide de verdad.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
LISTA = RAIZ / "v2" / "assets" / "evento" / "palabras.txt"
MIGRACION = RAIZ / "supabase" / "migrations" / "20261112130000_load_event_words.sql"
LARGO = 5
PALABRA = re.compile(r"^[a-zñ]{5}$")


class Afijo:
    def __init__(self, tipo: str, quita: str, pone: str, condicion: str, continuacion: str):
        self.tipo = tipo
        self.quita = "" if quita == "0" else quita
        self.pone = "" if pone == "0" else pone
        self.continuacion = continuacion
        patron = "." if condicion in ("", ".") else condicion
        self.condicion = re.compile(f"{patron}$" if tipo == "SFX" else f"^{patron}")

    def aplica(self, palabra: str) -> str | None:
        if not self.condicion.search(palabra):
            return None
        if self.tipo == "SFX":
            if self.quita and not palabra.endswith(self.quita):
                return None
            base = palabra[: len(palabra) - len(self.quita)] if self.quita else palabra
            return base + self.pone
        if self.quita and not palabra.startswith(self.quita):
            return None
        return self.pone + palabra[len(self.quita):]


def leer_afijos(ruta: Path) -> tuple[dict[str, list[Afijo]], dict[str, bool]]:
    reglas: dict[str, list[Afijo]] = defaultdict(list)
    cruzables: dict[str, bool] = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        partes = linea.split()
        if len(partes) < 4 or partes[0] not in ("PFX", "SFX"):
            continue
        tipo, bandera = partes[0], partes[1]
        if len(partes) == 4 and partes[3].isdigit():  # cabecera: SFX A Y 12
            cruzables[bandera] = partes[2] == "Y"
            continue
        quita, pone = partes[2], partes[3]
        condicion = partes[4] if len(partes) > 4 else "."
        pone, _, continuacion = pone.partition("/")
        reglas[bandera].append(Afijo(tipo, quita, pone, condicion, continuacion))
    return reglas, cruzables


def formas(palabra: str, banderas: str, reglas, cruzables, profundidad: int = 0) -> set[str]:
    """La palabra y todo lo que sus banderas generan, con un nivel de sufijos encadenados y prefijo × sufijo."""
    resultado = {palabra}
    sufijadas = {palabra}
    for bandera in banderas:
        for afijo in reglas.get(bandera, []):
            if afijo.tipo != "SFX":
                continue
            nueva = afijo.aplica(palabra)
            if nueva:
                resultado.add(nueva)
                if cruzables.get(bandera):
                    sufijadas.add(nueva)
                if afijo.continuacion and profundidad == 0:
                    resultado |= formas(nueva, afijo.continuacion, reglas, cruzables, 1)
    for bandera in banderas:
        for afijo in reglas.get(bandera, []):
            if afijo.tipo != "PFX":
                continue
            bases = sufijadas if cruzables.get(bandera) else {palabra}
            for base in bases:
                nueva = afijo.aplica(base)
                if nueva:
                    resultado.add(nueva)
    return resultado


def normaliza(palabra: str) -> str:
    """Sin tildes ni diéresis; la ñ se queda."""
    sin = "".join(
        c for c in unicodedata.normalize("NFD", palabra.replace("ñ", "\0")) if unicodedata.category(c) != "Mn"
    )
    return sin.replace("\0", "ñ")


def palabras_de_cinco(dic: Path, aff: Path) -> list[str]:
    reglas, cruzables = leer_afijos(aff)
    todas: set[str] = set()
    for linea in dic.read_text(encoding="utf-8").splitlines()[1:]:
        entrada = linea.split("\t")[0].split(" ")[0]
        palabra, _, banderas = entrada.partition("/")
        if not palabra or palabra[0].isupper():  # nombres propios y siglas fuera
            continue
        for forma in formas(palabra, banderas, reglas, cruzables):
            limpia = normaliza(forma)
            if PALABRA.match(limpia):
                todas.add(limpia)
    return sorted(todas)


CABECERA_SQL = """-- Las palabras válidas de 5 letras del juego del evento. GENERADO por tools/diccionario_evento.py: no editar a mano.
--
-- Fuente: diccionario ortográfico del español de LibreOffice (proyecto RLA-ES, https://github.com/sbosio/rla-es),
-- que sigue la norma de la RAE. Triple licencia GPL v3+ / LGPL v3+ / MPL 1.1+; esta lista derivada se usa bajo MPL.
-- Sin tildes ni diéresis y con la ñ como letra propia, como se juega.

create table public.event_words (palabra text primary key check (palabra ~ '^[a-zñ]{5}$'));
alter table public.event_words enable row level security;
-- La lista no es secreta (la web la tiene entera), pero la tabla no se lee ni se escribe con la clave pública:
-- solo la consulta `intentar_palabra`.
revoke all on public.event_words from anon, authenticated;

insert into public.event_words (palabra) values
"""


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    analizador = argparse.ArgumentParser(description="Genera el diccionario de 5 letras del evento.")
    analizador.add_argument("dic", type=Path)
    analizador.add_argument("aff", type=Path)
    argumentos = analizador.parse_args(argv)

    palabras = palabras_de_cinco(argumentos.dic, argumentos.aff)
    LISTA.parent.mkdir(parents=True, exist_ok=True)
    LISTA.write_text("\n".join(palabras) + "\n", encoding="utf-8")
    valores = ",\n".join(f"  ('{p}')" for p in palabras)
    MIGRACION.write_text(CABECERA_SQL + valores + ";\n", encoding="utf-8")
    print(f"{len(palabras)} palabras → {LISTA.relative_to(RAIZ)} y {MIGRACION.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
