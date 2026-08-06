"""El catálogo de reglas del juego, para que el grupo pueda leerlas.

Slice: `reglas-explicadas` (openspec/slices/dashboard/reglas-explicadas.md).

**Los parámetros no se escriben aquí: se importan de donde viven.** Cada uno declara su `fuente` —el módulo
y la constante que el cálculo usa de verdad— y su valor se lee de ahí en tiempo de ejecución. Un test
comprueba que lo publicado es lo aplicado.

Sin eso, esta página miente en cuanto alguien recalibre un umbral: diría "quince partidas" cuando el código
exige catorce. Una explicación falsa en la que el grupo confía es peor que no tener página.

Que la prosa viva en un módulo de Python no es bonito. La alternativa —tenerla en el brief y copiarla a la
web— reintroduce exactamente el desfase que este módulo existe para evitar, así que se acepta el feo.

**Dos marcadores independientes por regla**, y la diferencia es el aporte de esta página:

- `estado`: si el cálculo la usa (`aplicada`), si está decidida y sin implementar (`acordada-sin-aplicar`),
  o si el grupo la tiene sobre la mesa (`sin-decidir`);
- `votada`: si el grupo la aprobó en el canal.

Hoy hay reglas **aplicadas y no votadas**. Esconderlo sería el peor uso posible de esta página.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

import badges
import calendario
import seasons
import standings

EJES = ("temporada", "clasificacion", "medallas", "figuras", "datos")

APLICADA = "aplicada"
ACORDADA_SIN_APLICAR = "acordada-sin-aplicar"
SIN_DECIDIR = "sin-decidir"


@dataclass(frozen=True)
class Parametro:
    """Un número de una regla, leído de la constante que el cálculo usa.

    `fuente` es la ruta `modulo.CONSTANTE`, y existe para que un test pueda comprobar la coherencia sin
    confiar en que alguien recuerde actualizar los dos sitios.
    """

    nombre: str
    valor: object
    fuente: str
    unidad: str = ""


@dataclass(frozen=True)
class Regla:
    id: str
    eje: str
    titulo: str
    que_hace: str
    por_que: str
    estado: str
    votada: bool = False
    falta_decidir: str = ""
    parametros: tuple[Parametro, ...] = field(default_factory=tuple)


def _p(nombre: str, valor, fuente: str, unidad: str = "") -> Parametro:
    return Parametro(nombre=nombre, valor=valor, fuente=fuente, unidad=unidad)


def catalogo() -> tuple[Regla, ...]:
    """Todas las reglas, en el orden en que conviene leerlas."""
    return (
        # ── el eje del tiempo ────────────────────────────────────────────────────────────────────
        Regla(
            id="temporada-mensual",
            eje="temporada",
            titulo="Cada mes es una temporada y el marcador se reinicia el día 1",
            que_hace=(
                "La clasificación cuenta solo el mes en curso. El día 1 empieza de cero: un resultado de "
                "ese día pertenece ya a la temporada nueva, sin periodo de gracia."
            ),
            por_que=(
                "Un marcador que acumula todo el histórico premia a quien lleva más tiempo y deja sin "
                "sentido la pregunta de quién va ganando. Con temporadas, cualquiera puede ganar un mes."
            ),
            estado=APLICADA,
            votada=True,
        ),
        Regla(
            id="temporada-cero",
            eje="temporada",
            titulo="Todo lo jugado antes de agosto de 2026 es la temporada 0",
            que_hace=(
                "El histórico entero —de noviembre de 2025 a julio de 2026— es una sola temporada, la 0. "
                "Desde agosto, cada mes es una temporada numerada: agosto es la 1, septiembre la 2. Y la "
                "temporada 0 se ordena por la media de las partidas que jugaste, sin imputar ausencias."
            ),
            por_que=(
                "Las reglas nuevas no estaban en vigor entonces, así que aplicarlas hacia atrás cambiaría "
                "el resultado de un partido ya jugado. Y medido: de los 159 días válidos de ese periodo, "
                "siete de veinte jugadores tendrían más del 70% imputado porque se incorporaron a lo largo "
                "del camino. A quien entró el 22 de julio se le contarían 156 ausencias desde noviembre, "
                "que es castigar por no jugar antes de estar."
            ),
            estado=APLICADA,
            votada=False,
            parametros=(
                _p("la temporada 1 empieza", seasons.INICIO_TEMPORADAS, "seasons.INICIO_TEMPORADAS"),
            ),
        ),
        Regla(
            id="solo-dias-laborables",
            eje="temporada",
            titulo="Solo cuentan los días de lunes a viernes",
            que_hace=(
                "Sábado y domingo no forman parte de la temporada: no cuentan para la clasificación, no "
                "fijan la dificultad de un día y no son días que puedas faltar. Tu resultado de fin de "
                "semana se guarda y se puede mirar, pero no puntúa."
            ),
            por_que=(
                "El fin de semana casi nadie juega —1,3 personas de media frente a 8,8 en laborable—, así "
                "que penalizar una ausencia de sábado sería castigar por no estar donde no había nadie."
            ),
            estado=APLICADA,
            votada=True,
        ),
        Regla(
            id="dia-con-muestra-minima",
            eje="temporada",
            titulo="Un día con menos de cinco jugadores no cuenta",
            que_hace=(
                "Si un día laborable lo juegan menos de cinco personas, ese día no forma parte de la "
                "temporada: no penaliza a quien faltó y no entra en ninguna media."
            ),
            por_que=(
                "Con cuatro personas, la media del día no dice si la palabra fue dura o si simplemente era "
                "un puente. Y sin ese filtro, faltar un día en que el grupo tampoco jugó penalizaría igual."
            ),
            estado=APLICADA,
            votada=False,
            parametros=(
                _p("jugadores mínimos", seasons.MUESTRA_MINIMA_DEL_DIA, "seasons.MUESTRA_MINIMA_DEL_DIA",
                   "personas"),
            ),
        ),
        Regla(
            id="fecha-del-puzzle",
            eje="temporada",
            titulo="Tu resultado cuenta el día del puzzle, no el día que lo publicas",
            que_hace=(
                "La fecha sale del número del wordle. Si publicas el de ayer esta mañana, cuenta como ayer."
            ),
            por_que=(
                "Que llegues tarde al canal no cambia el día que jugaste. Y así un puzzle del 31 no se "
                "cuela en la temporada siguiente por publicarlo el 1."
            ),
            estado=APLICADA,
            votada=False,
        ),
        Regla(
            id="identidad-por-id-de-slack",
            eje="datos",
            titulo="Eres tu cuenta de Slack, no tu nombre",
            que_hace=(
                "Tus resultados se guardan con tu identificador de Slack. Si te cambias el nombre, siguen "
                "siendo tuyos."
            ),
            por_que=(
                "Antes la identidad era el nombre mostrado, así que un renombre te convertía en dos "
                "jugadores y repartía tus días entre los dos. Le pasó a alguien de verdad."
            ),
            estado=APLICADA,
            votada=False,
        ),
        Regla(
            id="fallo-cuenta-como-siete",
            eje="clasificacion",
            titulo="Un fallo cuenta como siete intentos",
            que_hace="Una partida sin resolver (X/6) entra en las medias como un 7.",
            por_que=(
                "Necesita un número para promediar, y siete es el siguiente al peor acierto posible: "
                "castiga el fallo sin convertirlo en una catástrofe."
            ),
            estado=APLICADA,
            votada=False,
            parametros=(_p("valor de un fallo", badges.FALLO, "badges.FALLO", "intentos"),),
        ),
        # ── la clasificación ─────────────────────────────────────────────────────────────────────
        Regla(
            id="imputacion-por-dificultad",
            eje="clasificacion",
            titulo="Faltar un día tiene nota, y depende de lo dura que fuera la palabra",
            que_hace=(
                "La clasificación se calcula sobre los días de la temporada, no sobre las partidas que "
                "jugaste. A cada día que faltas se le pone una nota: la peor entre la dificultad de ese día "
                "y tu propia media, más medio intento, con el tope en el fallo."
            ),
            por_que=(
                "Sin esto gana quien juega poco: promediar solo lo jugado depura tus peores días. Medido "
                "sobre el histórico, el campeón cambia en 6 de 8 meses, y en cinco de esos seis el campeón "
                "actual jugó menos de la mitad de los días. El medio intento de margen impide que callarse "
                "un mal resultado salga mejor que publicarlo."
            ),
            estado=ACORDADA_SIN_APLICAR,
            votada=False,
            parametros=(
                _p("margen", 0.5, "rules.MARGEN_DE_IMPUTACION", "intentos"),
                _p("tope", badges.FALLO, "badges.FALLO", "intentos"),
            ),
        ),
        Regla(
            id="minimo-en-la-temporada-cero",
            eje="clasificacion",
            titulo="La temporada 0 se rige por las reglas con las que se jugó",
            que_hace=(
                "Cuentan todas las jornadas, fines de semana incluidos y sin mínimo de jugadores por día. "
                "La media es la de las partidas jugadas, sin imputar. Y hacen falta cinco partidas para "
                "clasificar: quien no llega aparece en la tabla, pero sin puesto."
            ),
            por_que=(
                "Son las reglas que la web tenía cuando se jugó ese periodo, incluido el mínimo de cinco "
                "partidas para coronar la mejor media. Aplicar hacia atrás las reglas nuevas cambiaría el "
                "resultado de un partido ya jugado; y sin el mínimo la lideraría quien apenas jugó."
            ),
            estado=APLICADA,
            votada=False,
            parametros=(
                _p("partidas mínimas", standings.MINIMO_PARA_CLASIFICAR,
                   "standings.MINIMO_PARA_CLASIFICAR", "partidas"),
            ),
        ),
        Regla(
            id="sin-minimo-para-clasificar",
            eje="clasificacion",
            titulo="No hay mínimo de días para salir en la tabla",
            que_hace="Con una sola partida ya apareces, en el puesto que te corresponda.",
            por_que=(
                "La imputación ya impide que jugar tres días gane el mes, así que un umbral sobraría. Y "
                "verte en tu puesto informa más que no verte."
            ),
            estado=ACORDADA_SIN_APLICAR,
            votada=False,
        ),
        # ── las medallas ─────────────────────────────────────────────────────────────────────────
        Regla(
            id="medallas-no-cambian-la-tabla",
            eje="medallas",
            titulo="Las medallas no tocan la clasificación",
            que_hace="Son un eje aparte: se acumulan en tu palmarés y no suman ni restan en la tabla.",
            por_que=(
                "Mezclarlas convertiría el ranking en una suma de cosas incomparables. Separadas, "
                "reconocen lo que la media no ve: constancia, un día heroico, acertar a la primera."
            ),
            estado=APLICADA,
            votada=False,
        ),
        Regla(
            id="medallas-se-calculan-no-se-guardan",
            eje="medallas",
            titulo="Tu palmarés se recalcula cada vez",
            que_hace="Ninguna medalla se almacena: se deducen de los resultados cuando hacen falta.",
            por_que=(
                "Permite recalibrar un umbral y que el palmarés histórico se ajuste solo. Tiene un precio "
                "declarado: si una regla cambia, tu pasado cambia con ella."
            ),
            estado=APLICADA,
            votada=False,
        ),
        Regla(
            id="fondista",
            eje="medallas",
            titulo="Fondista: quince partidas en el mes",
            que_hace="Se gana al llegar a quince partidas en días válidos de la temporada.",
            por_que=(
                "Reconoce constancia, no excepcionalidad. Está puesta donde la logra casi la mitad del "
                "grupo: una medalla que nadie gana no la intenta nadie."
            ),
            estado=APLICADA,
            votada=False,
            parametros=(
                _p("partidas", badges.MINIMO_FONDISTA, "badges.MINIMO_FONDISTA", "partidas"),
            ),
        ),
        Regla(
            id="metronomo",
            eje="medallas",
            titulo="Metrónom@: no faltar ni un día laborable",
            que_hace=(
                "Se gana jugando todos los días válidos de la temporada, y solo se evalúa si el mes tiene "
                "al menos diez."
            ),
            por_que=(
                "Es la medalla de la constancia absoluta. El mínimo de días evita regalarla en un mes con "
                "tres jornadas."
            ),
            estado=APLICADA,
            votada=False,
            parametros=(
                _p("días mínimos del mes", badges.MINIMO_DIAS_PARA_METRONOMO,
                   "badges.MINIMO_DIAS_PARA_METRONOMO", "días"),
            ),
        ),
        Regla(
            id="dia-imposible",
            eje="medallas",
            titulo="El día imposible: resolver rápido el día que el grupo se atasca",
            que_hace=(
                "Se gana resolviendo en cuatro intentos o menos un día cuya media del grupo llegue a 5,5."
            ),
            por_que=(
                "Es la gesta más difícil del catálogo: ha ocurrido dos veces en nueve meses. No se repite "
                "porque una gesta ya está hecha."
            ),
            estado=APLICADA,
            votada=False,
            parametros=(
                _p("media del día", badges.UMBRAL_DIA_IMPOSIBLE, "badges.UMBRAL_DIA_IMPOSIBLE", "intentos"),
                _p("tus intentos", badges.RESOLVER_RAPIDO, "badges.RESOLVER_RAPIDO", "intentos o menos"),
            ),
        ),
        # ── las figuras ──────────────────────────────────────────────────────────────────────────
        Regla(
            id="album-de-figuras",
            eje="figuras",
            titulo="La cuadrícula de emojis dibuja una figura, y se colecciona",
            que_hace=(
                "Cada partida deja un dibujo que se clasifica en loro, flores, geométrico o abstracto, y "
                "se acumula en tu álbum. Todavía no está activo."
            ),
            por_que=(
                "Es un segundo eje que premia a quien sufre: la figura sale de las partidas que salen mal, "
                "así que quien gana el mes casi nunca gana el álbum."
            ),
            estado=SIN_DECIDIR,
            votada=False,
            falta_decidir=(
                "El clasificador automático no está calibrado. Hay 30 cuadrículas etiquetadas a mano para "
                "medirlo, y hasta que acierte lo suficiente los umbrales de sus medallas no se publican."
            ),
        ),
        Regla(
            id="figuras-no-puntuan",
            eje="figuras",
            titulo="El álbum no influye en la clasificación",
            que_hace="Las figuras no suman ni restan en el ranking de puntuación.",
            por_que="Decisión explícita: son dos juegos distintos y mezclarlos estropearía los dos.",
            estado=SIN_DECIDIR,
            votada=False,
            falta_decidir="Si algún día el álbum tiene su propio podio, y con qué criterio se ordena.",
        ),
        # ── lo que el grupo tiene sobre la mesa ──────────────────────────────────────────────────
        Regla(
            id="podios-separados",
            eje="clasificacion",
            titulo="Podios separados de intentos y de participación",
            que_hace="Habría dos podios en lugar de uno.",
            por_que="Salió en el hilo del canal: reconocer por separado quién acierta y quién no falla.",
            estado=SIN_DECIDIR,
            votada=False,
            falta_decidir=(
                "Cuál sería el podio principal. Y con la imputación, la participación ya está dentro de la "
                "media, así que un podio aparte la contaría dos veces."
            ),
        ),
        Regla(
            id="rachas",
            eje="clasificacion",
            titulo="Rachas, mejor y peor",
            que_hace="Reconocería series de días seguidos.",
            por_que="Salió en el hilo del canal.",
            estado=SIN_DECIDIR,
            votada=False,
            falta_decidir="Qué es una racha: acertar N días seguidos, o mejorar N días seguidos.",
        ),
        Regla(
            id="remontada",
            eje="clasificacion",
            titulo="Mayor remontada",
            que_hace="Reconocería a quien más suba.",
            por_que="Salió en el hilo del canal.",
            estado=SIN_DECIDIR,
            votada=False,
            falta_decidir="Respecto a qué se mide: la posición del mes anterior, o el arranque del propio mes.",
        ),
        Regla(
            id="ausencias-justificadas",
            eje="clasificacion",
            titulo="Ausencias justificadas",
            que_hace="Permitiría no puntuar un día concreto por un motivo.",
            por_que=(
                "El modelo de imputación presume que faltar un día duro es evitarlo, y se equivocará con "
                "quien tuviera una reunión a primera hora."
            ),
            estado=SIN_DECIDIR,
            votada=False,
            falta_decidir="Quién la concede y con qué criterio, para que no sea una puerta abierta.",
        ),
    )


#: El margen del modelo de imputación. Vive aquí porque el modelo todavía no está implementado; cuando
#: `clasificacion-de-temporada` lo implemente, esta constante se muda a su módulo y la regla apuntará allí.
MARGEN_DE_IMPUTACION = 0.5


def busca(identificador: str) -> Regla:
    """La regla con ese identificador. Lanza si no existe, que es lo que quieres en un test."""
    for regla in catalogo():
        if regla.id == identificador:
            return regla
    raise KeyError(f"no hay regla {identificador!r}")


def por_eje(reglas: tuple[Regla, ...]) -> dict[str, list[Regla]]:
    """Las reglas agrupadas por eje, en el orden declarado en `EJES`."""
    agrupadas: dict[str, list[Regla]] = {}
    for eje in EJES:
        del_eje = [regla for regla in reglas if regla.eje == eje]
        if del_eje:
            agrupadas[eje] = del_eje
    return agrupadas


def como_json(reglas: tuple[Regla, ...]) -> list[dict]:
    """Las reglas en tipos serializables, listas para la carga útil JSONB y para la web."""
    return [asdict(regla) for regla in reglas]
