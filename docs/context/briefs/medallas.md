# Medallas — sistema de logros

> Síntesis citable. Fuente: propuesta en conversación (2026-08-04), calibrada contra los 1533
> resultados y los 1228 patrones recuperados del canal.
> Relacionado: [ranking-de-figuras](ranking-de-figuras.md) · [reglas-temporadas](reglas-temporadas.md)

## Qué es

Un tercer eje de juego, independiente del ranking de puntuación y del álbum de figuras: **logros que se
ganan por hacer algo concreto**, con nombre propio y emoji. No cambian la clasificación; se acumulan en
el palmarés del jugador.

## El problema que hay que resolver primero: la calibración

Un logro solo significa algo si es difícil de conseguir **y** alcanzable. Los dos fallos posibles:

- **Inalcanzable** → nadie lo tiene, nadie lo intenta. La propuesta inicial de "más de 10 loros en un
  mes" es de este tipo: el máximo histórico en un mes es **6**, la media es **1,1**, y ningún par
  jugador-mes de los 123 medidos llega a 10 en ninguna categoría de figura.
- **Trivial** → todos lo tienen y deja de distinguir. "Mes sin ningún fallo" lo logra el 41%.

El techo estructural manda: la **mediana de partidas por jugador-mes es 14**. Cualquier umbral mensual
por encima de eso es imposible por construcción, y uno de 10 exige que el 71% de las partidas del mes
caigan en la misma categoría.

## Los tres niveles de rareza

Medidos sobre 123 pares jugador-mes con datos:

| Nivel | Frecuencia | Qué significa |
|---|---|---|
| **Legendario** | menos del 5% | pasa un par de veces al año en todo el grupo |
| **Raro** | 5-15% | un buen mes de alguien concreto |
| **Común** | más del 20% | reconoce constancia, no excepcionalidad |

Un sistema sano tiene de los tres: los comunes dan entrada a todos, los legendarios dan algo que
perseguir.

## Catálogo calibrado

### Rendimiento

| Medalla | Condición | Logran | Nivel |
|---|---|---|---|
| **Suertud@** | resolver en **un** intento | 2 personas en 9 meses (0,13% de partidas) | legendario |
| **El día imposible** | resolver en ≤4 un día cuya media del grupo sea ≥5,5 | 2 personas, una vez | legendario |
| **Superviviente** | resolver en ≤4 tres días difíciles (media ≥4,5) en el mismo mes | 4% | legendario |
| **Verdugo** | ser el mejor del día cinco veces en el mes | 34% | común |
| **Impecable** | un mes sin ningún fallo, con 10 partidas mínimo | 41% | común |

### Constancia

| Medalla | Condición | Logran | Nivel |
|---|---|---|---|
| **Pleno** | no faltar ni un solo día del mes | 12% | raro |
| **Fondista** | 15 partidas o más en el mes | 48% | común |

### Figuras

Umbrales **provisionales**: dependen del clasificador, que todavía no está calibrado (ver el límite al
final). Los porcentajes son con el clasificador actual.

| Medalla | Condición | Logran | Nivel |
|---|---|---|---|
| **Ornitólog@** | 4 loros en un mes | 3% | legendario |
| **Arquitect@** | 4 escuadras en un mes | 2% | legendario |
| **Florista** | 5 flores en un mes | 8% | raro |
| **Coleccionista** | las cuatro figuras en el mismo mes | 32% | común |
| **Abstract@** | 12 cacas en un mes | 24% | común |

El máximo histórico observado por categoría y mes: loro 6, flor 8, escuadra 6, caca 18. Los umbrales
están puestos justo por debajo de lo que alguien ha llegado a hacer, que es donde un logro es difícil sin
ser imposible.

## Reglas del sistema

**Ámbito.** Dos clases, y la diferencia importa:

- **De temporada**: se evalúan al cierre del mes y se pueden ganar muchas veces. Se muestran con
  contador (`🦜 Ornitólog@ ×3`). Todas las de figuras y constancia son de este tipo.
- **Permanentes**: se ganan en el momento en que ocurren y no se repiten. `Suertud@` y `El día imposible`
  son de este tipo: la gesta ya está hecha.

**No se pierden nunca.** Una medalla ganada queda en el palmarés con el mes en que se logró. Un sistema
que quita logros castiga por dejar de jugar, y eso ya lo hace el ranking.

**Cuándo se evalúan.** Las permanentes, el mismo día, y se anuncian en el resumen. Las de temporada, al
cierre del mes, junto al ganador.

**Dónde se ven.** En la ficha de jugador como palmarés, y en el resumen diario cuando alguien gana una
—que es el momento en que tienen gracia—. En la clasificación no: ahí competirían con la información
que esa vista tiene que dar.

**Derivadas, no almacenadas.** Una medalla es una función de los resultados, así que se calcula, no se
guarda. Eso permite recalibrar un umbral y que el palmarés histórico se recalcule solo. Si algún día se
quiere congelar el palmarés, será una decisión con su propio ADR.

## Lo que sigue abierto

| Abierto | Qué falta decidir |
|---|---|
| Los nombres | `Suertud@`, `Ornitólog@`, `Florista`, `Arquitect@` vienen de la propuesta. `Abstract@`, `Verdugo`, `Pleno`, `Fondista`, `Superviviente`, `El día imposible` y `Coleccionista` son propuestas a falta de bautizo del grupo |
| Medallas de racha | Dependen de que se cierre qué es una racha (abierto en [reglas-temporadas](reglas-temporadas.md)) |
| Medallas de remontada | Mismo bloqueo |
| Medallas negativas | El grupo pidió un "muro de la vergüenza". `Abstract@` ya va por ahí, pero conviene decidir si se quieren logros explícitamente malos o solo irónicos |
| ¿Se anuncian todas? | Anunciar las comunes cada mes puede saturar el resumen. Quizá solo legendarias y raras |

## Límite honesto

**Los umbrales de las medallas de figuras no son fiables todavía.** Salen del clasificador sin calibrar,
que manda el 69% de los patrones a caca y falla en el único patrón etiquetado a mano. Cuando la
calibración cambie, estos cinco umbrales hay que volver a medirlos — y por eso las medallas se calculan
en vez de guardarse.

Los de rendimiento y constancia sí son firmes: no dependen del clasificador, solo de puntuaciones y
fechas, que están verificadas.
