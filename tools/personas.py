"""La forma gramatical con la que el mensaje se refiere a cada persona.

Slice: `concordancia-de-genero` (openspec/slices/publicacion/concordancia-de-genero.md).

**Es una tabla declarada, no una inferencia.** El castellano concuerda el género en adjetivos y participios
—«está sembrado» frente a «está sembrada»— y el sistema no tiene ese dato: la tabla solo guarda `player_name`
y `slack_user_id`. Antes de esto las frases usaban `@` («sembrad@»), que es un apaño tipográfico.

Deducirlo del nombre en el momento sería adivinar sobre compañeros identificables en un canal del trabajo, y
equivocarse ahí no es un fallo de concordancia: es dirigirse mal a alguien delante de todo el grupo. Así que
las formas **las declaró el dueño**, una por una, y las tres que no estaban claras —Cata, Gabi y Dani Sanchez—
se preguntaron antes de escribirlas.

Lo que la hace segura es que **es un dato en un solo sitio**: si alguna está mal, se corrige aquí y no en once
frases. Y quien no aparezca sale con la forma neutra, así que un jugador nuevo no hereda una suposición.
"""

from __future__ import annotations

#: Forma masculina.
MASCULINO = "o"
#: Forma femenina.
FEMENINO = "a"

#: La forma de cada persona, **declarada por el dueño** el 2026-09-09 sobre los 23 jugadores del histórico.
#:
#: Se indexa por `player_name`, que es lo que el mensaje usa para nombrar. Ojo: `slack_user_id` guarda
#: display names, así que un renombre en Slack crea una entrada nueva — y sin declarar sale neutra, que es el
#: comportamiento correcto para alguien de quien no se sabe.
FORMAS: dict[str, str] = {
    "Andrés R.": MASCULINO,
    "Edu Noeda": MASCULINO,
    "Paula Granado": FEMENINO,
    "Luis": MASCULINO,
    "Carlos": MASCULINO,
    "Raquel": FEMENINO,
    "Claire": FEMENINO,
    "Carlos H.": MASCULINO,
    "Cata": FEMENINO,
    "Juan (Kokuma)": MASCULINO,
    "Gabi": MASCULINO,
    "Dani Sanchez": MASCULINO,
    "Iván A.": MASCULINO,
    "Iria Dorado": FEMENINO,
    "Flavia Venturi": FEMENINO,
    "Quique": MASCULINO,
    "Clara C": FEMENINO,
    "Sandra": FEMENINO,
    "Joel": MASCULINO,
    "Carmen": FEMENINO,
    "Marcos Granado": MASCULINO,
    "marcos.granado": MASCULINO,
    "Javi Calvo": MASCULINO,
}

#: Lo que se escribe en la plantilla donde el género cambia la palabra: `sembrad{g}`, `anch{g}`.
HUECO = "{g}"

#: Con quién no está declarado. La `@` era lo que había antes y sigue siendo lo correcto para quien no
#: aparece: no se supone nada.
NEUTRO = "@"


def forma_de(nombre: str) -> str:
    """La terminación que le toca a un nombre, o la neutra si no está declarado.

    **Varios nombres a la vez dan la forma masculina**, que es lo que el castellano hace con un grupo mixto.
    Si todos los nombrados comparten forma, se usa esa: «Ana y Bea están sembradas» y no «sembrados».
    """
    return FORMAS.get(nombre, NEUTRO)


def forma_de_varios(nombres: list[str]) -> str:
    """La terminación de un grupo. Masculina salvo que **todas** las declaradas sean femeninas.

    Sin ninguna declarada sale la neutra: con un grupo de desconocidos tampoco se supone.
    """
    declaradas = [FORMAS[n] for n in nombres if n in FORMAS]
    if not declaradas:
        return NEUTRO
    return FEMENINO if all(f == FEMENINO for f in declaradas) else MASCULINO


def concuerda(plantilla: str, nombres: str | list[str]) -> str:
    """La plantilla con el hueco de género resuelto.

    `nombres` puede ser un nombre o una lista. Se acepta el texto ya unido —«Ana y Bea»— porque es lo que
    tienen a mano los compositores; en ese caso se parte por los separadores que el propio mensaje usa.
    """
    if isinstance(nombres, str):
        nombres = [parte.strip() for parte in nombres.replace(" y ", ", ").split(",") if parte.strip()]
    forma = forma_de(nombres[0]) if len(nombres) == 1 else forma_de_varios(nombres)
    return plantilla.replace(HUECO, forma)
