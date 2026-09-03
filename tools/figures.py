"""El clasificador de figuras: una cuadrícula de emojis, una categoría.

Pack: `feat-calibracion-de-figuras` (Slice: N/A — paso 5.0 del roadmap).
Diseño: [ranking-de-figuras](../docs/context/briefs/ranking-de-figuras.md).

Función **pura**: entra el patrón, sale la categoría. Sin reloj, sin red y sin estado (§10 del protocolo),
que es lo que permite que las 31 etiquetas humanas funcionen como examen.

**La categoría no se almacena.** Se deriva del patrón crudo cada vez, así que recalibrar un umbral
reclasifica el histórico solo, sin migración. El precio declarado: cambiar un peso cambia el álbum de
todo el mundo, y por eso el conjunto dorado es lo que hace seguro tocarlo.

Calibrado contra **dos criterios independientes**, porque el primero solo no basta:

- **acuerdo**: 25 de las 31 etiquetas humanas (81%);
- **reparto** sobre los patrones reales: flores 47% · abstracto 32% · loro 13% · geometrico 7%,
  frente al 37/33/17/13 que etiquetó el humano.

El candidato anterior sacaba 83% de acuerdo y **55% de flores** en producción: acertaba el examen y no
generalizaba, porque su regla («una fila verde ancha y algún amarillo») se cumple más según crece la
cuadrícula. Se descartó por el segundo criterio, no por el primero. `tools/calibrate_figures.py` rehace
las dos medidas.

Los seis desacuerdos que quedan están listados en el brief. Ninguno es caro: el álbum no toca el ranking
de puntuación (decisión explícita), así que una figura mal puesta es una gracia perdida, no una injusticia.

El geométrico se reconoce por **dos vías**: poca tinta (`es_geometrico`) y la **simetría en espejo**, que se
consulta en último lugar. La segunda se añadió porque la primera dejaba fuera dibujos regulares con masa —un
arco de densidad 0,60 salía abstracto—, y porque medir escasez de tinta no es medir regularidad. Ver `figura`
para el orden, que es lo que hace el rasgo seguro.
"""

from __future__ import annotations

from dataclasses import dataclass

#: El vocabulario, fijado el 2026-08-05 con las etiquetas que el dueño usó de verdad. `caca` pasó a
#: `abstracto` y `escuadra` a `geometrico`: la categoría se le cuelga a un tercio de las partidas, así que
#: describe el dibujo en lugar de insultar al jugador.
LORO = "loro"
FLORES = "flores"
GEOMETRICO = "geometrico"
ABSTRACTO = "abstracto"

VOCABULARIO: dict[str, str] = {
    LORO: "🦜",
    FLORES: "🌷",
    GEOMETRICO: "📐",
    ABSTRACTO: "🌀",
}

#: Las que cuentan como figura reconocible. **`abstracto` no es una figura**: es su ausencia, y no existe
#: la categoría «ambiguo» (decisión del brief: o se reconoce algo, o es abstracto).
FIGURAS: tuple[str, ...] = (LORO, FLORES, GEOMETRICO)

VERDE, AMARILLO, VACIO = "G", "Y", "."

#: Columnas de una cuadrícula de Wordle. La usa el espejo para no concedérselo a una fila truncada, que
#: sería palíndroma por accidente. Los `range(5)` que ya había se dejan como estaban: unificarlos es un
#: refactor de código que funciona, y no es lo que se está cambiando aquí.
ANCHO = 5

#: Verde mínimo y máximo del loro. El mínimo (4) descarta una columna suelta sin cuerpo —eso es un tallo,
#: y va a geométrico—; el máximo (12) descarta las masas verdes grandes, que el humano etiquetó como
#: abstracto o geométrico. Los cinco loros del conjunto caen entre 4 y 12.
MINIMO_VERDE_DEL_LORO = 4
MAXIMO_VERDE_DEL_LORO = 12

#: Amarillos que admite un loro: el pico, y a lo sumo dos. Con tres el dibujo ya es de pétalos.
MAXIMO_AMARILLO_DEL_LORO = 2

#: Tinta máxima de un geométrico, en fracción de celdas del cuerpo. «Pocas celdas y forma limpia»: un
#: tallo, una pirámide. Por encima de esto el dibujo ya tiene masa y deja de ser limpio — que es
#: precisamente lo que dejaba fuera dibujos regulares, y por lo que existe la vía del espejo.
DENSIDAD_MAXIMA_DEL_GEOMETRICO = 0.4

#: Primera jornada que se clasifica con la geometría por delante del loro.
#:
#: **El cambio no es retroactivo, por decisión del dueño.** Las cuadrículas anteriores conservan la categoría
#: que tenían cuando se jugaron, igual que la temporada 0 se rige por las reglas que estaban en vigor entonces
#: (`seasons.dias_de_temporada`). Lo contrario reescribiría el álbum de todo el mundo hacia atrás: medido, el
#: reorden mueve 42 de las 1.706 cuadrículas del histórico, todas de loro a geométrico, y como el geométrico
#: vale 3 puntos y el loro 2, subiría la puntuación de quien las tenga en partidas ya jugadas y comentadas.
PRIMERA_JORNADA_DEL_ORDEN_NUEVO = 1694


#: Filas de cuerpo que ha de tener un espejo para **clasificarse** como geométrico.
#:
#: **Dos, y es un umbral distinto del que pide el logro.** Los dos vivieron un tiempo compartidos, porque con
#: umbrales distintos y sin corte de reglas un espejo de dos filas le robaba la categoría a flores legítimas
#: del histórico —lo cazaron los tests del álbum, cuyo fixture de flor resulta ser simétrico—. Con el corte de
#: `PRIMERA_JORNADA_DEL_ORDEN_NUEVO` esa objeción desaparece: el histórico ya no se reclasifica, así que bajar
#: este umbral solo afecta a lo que se juegue de aquí en adelante. Medido: **cambia una cuadrícula de 1.758**.
#:
#: Se bajó por decisión del dueño, sobre un caso concreto: `.Y.Y./G.Y.G/GGGGG`, dos filas y palíndromo
#: perfecto en las dos, se etiquetaba «flores» porque `.Y.Y.` cumple además la regla de la flor.
CUERPO_MINIMO_DEL_ESPEJO = 2


def es_espejo_reconocible(r: Rasgos) -> bool:
    """Un espejo con cuerpo suficiente para **clasificarse** como geométrico.

    El logro del espejo perfecto pide más cuerpo y tiene su propio umbral (`badges.CUERPO_MINIMO_DEL_LOGRO`):
    reconocer un dibujo y considerarlo una gesta son dos decisiones distintas, y el dueño las separó a
    propósito. Que divergan está fijado por un test, para que no vuelvan a juntarse por descuido.
    """
    return r.espejo and r.alto >= CUERPO_MINIMO_DEL_ESPEJO


def orden_nuevo(jornada: int | None) -> bool:
    """Si a esta jornada le toca el orden nuevo. Sin jornada, el histórico.

    Se llama así y no `geometria_primero` porque el corte gobierna ya **dos** cambios de orden: la geometría
    por delante del loro, y el espejo por delante de la flor.
    """
    return jornada is not None and jornada >= PRIMERA_JORNADA_DEL_ORDEN_NUEVO


#: Amarillos mínimos de una flor: dos pétalos. Con uno solo no hay flor, hay un amarillo.
MINIMO_AMARILLO_DE_LA_FLOR = 2

#: Pétalos libres que bastan por sí solos para que sea flor, sin necesitar una fila limpia de amarillos.
#: Tres amarillos flotando en negro son una flor aunque compartan fila con verde.
MINIMO_PETALOS_LIBRES = 3


@dataclass(frozen=True)
class Rasgos:
    """Lo que se mide de una cuadrícula, sin interpretarlo todavía.

    Todo se mide sobre el **cuerpo**: la cuadrícula sin la banda verde final. La banda es el suelo del
    dibujo, no parte de él, y mezclarla falsea los tres rasgos que deciden.
    """

    resuelto: bool
    alto: int
    amarillos: int
    verdes: int
    densidad: float
    petalos_libres: int
    filas_de_petalos: int
    lineas_aisladas: tuple[int, ...]
    espejo: bool


def rejilla(patron: str) -> list[str]:
    """El patrón normalizado a filas de `G`/`Y`/`.`.

    Acepta las dos formas que existen de verdad: **emoji**, como se ve en el canal y como está etiquetado
    el conjunto dorado, y **`G/Y/.` separado por barras**, que es como la ingesta lo guarda. Si cada una
    entrara por su lado, el examen mediría una cosa y producción haría otra.
    """
    normalizado = (
        (patron or "")
        .replace("🟩", VERDE)
        .replace("🟨", AMARILLO)
        .replace("⬛", VACIO)
        .replace("⬜", VACIO)  # modo claro de Slack
        .replace("/", "\n")
    )
    return [fila.strip() for fila in normalizado.split("\n") if fila.strip()]


def _lineas_verticales_aisladas(cuerpo: list[str]) -> tuple[int, ...]:
    """Los largos de las líneas verdes verticales que se ven **como línea**, no como parte de una masa.

    Una línea cuenta si en casi todas sus filas los dos vecinos horizontales no son verdes. Se admite una
    fila pegada a propósito: el cuello del loro se une al cuerpo por abajo, y exigir aislamiento total
    dejaba fuera la ficha 18, que el humano ve clarísima.
    """
    largos: list[int] = []
    for columna in range(5):
        fila = 0
        while fila < len(cuerpo):
            if _celda(cuerpo, fila, columna) != VERDE:
                fila += 1
                continue
            final = fila
            while _celda(cuerpo, final + 1, columna) == VERDE:
                final += 1
            largo = final - fila + 1
            if largo >= 2:
                libres = sum(
                    1
                    for f in range(fila, final + 1)
                    if _celda(cuerpo, f, columna - 1) != VERDE
                    and _celda(cuerpo, f, columna + 1) != VERDE
                )
                if libres >= largo - 1:
                    largos.append(largo)
            fila = final + 1
    return tuple(largos)


def _es_espejo(cuerpo: list[str]) -> bool:
    """Si cada fila del cuerpo es igual leída al revés — el espejo respecto a la columna central.

    **Es exacto: una sola celda rota lo niega.** Se midió la alternativa de admitir un defecto y se
    descartó, porque lleva la cobertura del 1,1% al 7,7% de los patrones reales y cuesta una ficha del
    conjunto dorado. Es el mismo canje que tumbó al primer candidato de la calibración: mejor reparto a
    cambio de acertar menos.

    Se mide **sobre el cuerpo**, no sobre la cuadrícula entera. La banda verde final es simétrica en toda
    partida resuelta, así que incluirla convertiría el rasgo en «¿ha resuelto?», que ya se sabe por otro
    camino. Un cuerpo vacío —un 1/6— no es un espejo: no hay nada que reflejar.

    **Exige las cinco columnas.** No es paranoia sobre datos que no existen —las 6202 filas de producción
    miden cinco—, es hacia dónde falla si algún día dejan de medirlas: una fila truncada como `GG` es
    palíndroma por accidente, y sin esta condición un patrón corrupto pasaría de `abstracto` (0 puntos) a
    `geometrico` (3, el máximo). Lo cazó la auditoría adversarial del gate 4d.
    """
    return bool(cuerpo) and all(len(fila) == ANCHO and fila == fila[::-1] for fila in cuerpo)


def _celda(cuerpo: list[str], fila: int, columna: int) -> str:
    """La celda, o vacío si cae fuera. Evita repartir comprobaciones de límites por todo el módulo."""
    if not (0 <= fila < len(cuerpo)) or not (0 <= columna < len(cuerpo[fila])):
        return VACIO
    return cuerpo[fila][columna]


def rasgos(patron: str) -> Rasgos:
    """Los rasgos de una cuadrícula."""
    filas = rejilla(patron)
    resuelto = bool(filas) and set(filas[-1]) == {VERDE}
    cuerpo = filas[:-1] if resuelto else filas

    amarillos = sum(fila.count(AMARILLO) for fila in cuerpo)
    verdes = sum(fila.count(VERDE) for fila in cuerpo)
    celdas = len(cuerpo) * 5

    # Pétalos libres: amarillos que no tocan verde **dentro del cuerpo**. La banda final no cuenta como
    # vecina a propósito: si contara, todo amarillo de la fila de abajo tocaría verde y la señal de pétalo
    # desaparecería justo donde el humano la ve.
    libres = 0
    for fila in range(len(cuerpo)):
        for columna in range(5):
            if _celda(cuerpo, fila, columna) != AMARILLO:
                continue
            vecinos = (
                _celda(cuerpo, fila - 1, columna),
                _celda(cuerpo, fila + 1, columna),
                _celda(cuerpo, fila, columna - 1),
                _celda(cuerpo, fila, columna + 1),
            )
            if VERDE not in vecinos:
                libres += 1

    return Rasgos(
        resuelto=resuelto,
        alto=len(cuerpo),
        amarillos=amarillos,
        verdes=verdes,
        densidad=(amarillos + verdes) / celdas if celdas else 0.0,
        petalos_libres=libres,
        filas_de_petalos=sum(1 for fila in cuerpo if AMARILLO in fila and VERDE not in fila),
        lineas_aisladas=_lineas_verticales_aisladas(cuerpo),
        espejo=_es_espejo(cuerpo),
    )


def es_loro(r: Rasgos) -> bool:
    """Columna verde vertical, un segundo elemento verde y un amarillo de pico.

    **El amarillo tiene que tocar el cuerpo.** Es el rasgo que decidió la calibración: un amarillo
    flotando en negro es un pétalo, no un pico, y sin esta condición el loro se comía dos flores del
    conjunto. Con un solo amarillo la condición se relaja —un amarillo suelto en un dibujo de columnas es
    el pico igualmente—; con dos, ninguno puede flotar, porque dos pétalos ya son una flor.
    """
    if not r.lineas_aisladas:
        return False
    if not MINIMO_VERDE_DEL_LORO <= r.verdes <= MAXIMO_VERDE_DEL_LORO:
        return False
    if not 1 <= r.amarillos <= MAXIMO_AMARILLO_DEL_LORO:
        return False
    return r.amarillos == 1 or r.petalos_libres == 0


def es_geometrico(r: Rasgos) -> bool:
    """Poca tinta y a lo sumo un amarillo: un tallo, una pirámide.

    **No cubre la escalera**, aunque sea la forma más geométrica que existe: cuatro escalones dan densidad
    0,50 y el techo está en 0,40. Antes esta docstring la prometía y la regla no la cumplía. La escalera
    tampoco la rescata el espejo —es regular respecto a la diagonal, no al eje vertical—, así que sigue
    saliendo abstracta. Es una limitación conocida, y arreglarla pide otra señal y otra medición.

    Esta es **una** de las dos vías del geométrico; la otra es el espejo, que se consulta al final. Ver
    `figura`.
    """
    return r.densidad <= DENSIDAD_MAXIMA_DEL_GEOMETRICO and r.amarillos <= 1


def es_flor(r: Rasgos) -> bool:
    """El suelo verde con pétalos encima.

    Dos vías, y las dos son de pétalos: una **fila limpia de amarillos** (sin verde), que es la forma en
    que el humano describe la flor, o **tres pétalos libres** aunque compartan fila con verde.

    Ninguna de las dos crece con el tamaño de la cuadrícula, y eso es el punto: la regla que se descartó
    —«hay una fila verde ancha y algún amarillo»— se cumplía cada vez más según se alargaba la partida, y
    convertía en flor el 55% de producción.
    """
    if r.amarillos >= MINIMO_AMARILLO_DE_LA_FLOR and r.filas_de_petalos >= 1:
        return True
    return r.petalos_libres >= MINIMO_PETALOS_LIBRES


def figura(patron: str, jornada: int | None = None) -> str:
    """La categoría de una cuadrícula. Siempre devuelve una: `abstracto` es la respuesta por defecto.

    `jornada` decide **qué orden de reglas se aplica**, porque el orden cambió y el cambio no es retroactivo
    (ver `PRIMERA_JORNADA_DEL_ORDEN_NUEVO`). Sin jornada se usa el orden histórico: es lo que quieren las
    herramientas que clasifican un patrón fuera de contexto, como la calibración contra el etiquetado humano,
    que se hizo con las reglas de entonces.

    El orden de las reglas es parte de la calibración y no es cosmético: el loro se decide antes que la
    flor porque comparten el amarillo, y el geométrico antes que la flor porque una pirámide con un
    amarillo suelto no es un ramo.

    **El espejo va en último lugar**, y ahí está lo que hace el rasgo seguro. Unos pétalos son simétricos
    por naturaleza, así que un espejo consultado antes de la flor le robaría la categoría a flores
    legítimas — se midió, y eran cinco. Puesto al final solo puede **ascender abstractos**: ninguna
    cuadrícula que ya tiene figura la pierde, y eso es un invariante que los tests comprueban en lugar de
    darlo por hecho.
    """
    r = rasgos(patron)

    # Sin banda verde final no hay suelo, y sin suelo no hay dibujo que reconocer: las tres cuadrículas
    # falladas del conjunto dorado son abstracto. Un cuerpo vacío es un 1/6: acertó a la primera y no dejó
    # lienzo, así que tampoco hay figura.
    if not r.resuelto or r.alto == 0:
        return ABSTRACTO

    # **El orden cambia a partir de una jornada, y no hacia atrás.** Con el orden nuevo la geometría se
    # decide primero y ya no se avanza: una pirámide con un amarillo suelto es un geométrico, no un loro.
    # Medido, mueve 42 de 1.706 cuadrículas, todas de loro a geométrico, y ninguna flor.
    if orden_nuevo(jornada):
        if es_geometrico(r):
            return GEOMETRICO
        if es_loro(r):
            return LORO
        # **El espejo por delante de la flor**, y solo desde el corte. La invariante «el espejo solo asciende
        # abstractos» existía para no robarle la categoría a flores del histórico; con el corte, el histórico
        # queda intocado y la invariante deja de hacer falta. Medido: cambia **una** cuadrícula de 1.706 —la
        # simétrica de cuatro filas de la jornada #1694, que se etiquetaba «flores»—; retroactivo movería 47.
        if es_espejo_reconocible(r):
            return GEOMETRICO
    else:
        if es_loro(r):
            return LORO
        if es_geometrico(r):
            return GEOMETRICO

    if es_flor(r):
        return FLORES
    # Última oportunidad antes de rendirse, **y solo en el orden histórico**: en el nuevo el espejo ya se ha
    # consultado más arriba. Un dibujo regular con demasiada masa para el techo de densidad —un arco, una
    # diana— es geométrico igualmente. La forma es lo que lo hace geométrico; la escasez de tinta era un
    # sustituto de la regularidad, y no la mide.
    if r.espejo:
        return GEOMETRICO
    return ABSTRACTO


def emoji(categoria: str) -> str:
    """El emoji de una categoría, para la tira del álbum."""
    return VOCABULARIO[categoria]
