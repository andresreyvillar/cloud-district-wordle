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

Todas las cifras remedidas el 2026-08-04 **con la regla de días laborables aplicada**
([reglas-temporadas](reglas-temporadas.md)), ejecutando el catálogo real contra las 123 parejas
jugador-mes. Dos de las cifras anteriores estaban mal: ver más abajo.

### Rendimiento

| Medalla | Condición | Logran | Nivel |
|---|---|---|---|
| **Suertud@** | resolver en **un** intento | 2 personas en 9 meses (0,13% de partidas) | legendario |
| **El día imposible** | resolver en ≤4 un día cuya media del grupo sea ≥5,5 | 4 personas, en 2 días | legendario |
| **Superviviente** | resolver en ≤4 tres días difíciles (media ≥4,5) en el mismo mes | 4,1% | legendario |
| **Verdugo** | ser el mejor del día cinco veces en el mes | 32,5% | común |
| **Impecable** | un mes sin ningún fallo, con 10 partidas mínimo | 41,5% | común |

### Constancia

| Medalla | Condición | Logran | Nivel |
|---|---|---|---|
| **Metrónom@** | no faltar ni un solo **día laborable** del mes | 4,9% | raro |
| **Fondista** | 15 partidas o más en el mes | 47,2% | común |

### Nombres reconciliados con el diseño de la liga arcade

El [diseño](../sources/2026-08-05-diseno-liga-arcade.md) trae nombres propios, y el brief ya declaraba los
nombres como abiertos. Se adoptan los suyos **salvo cuando adoptarlos redefiniría una regla existente**:

| Antes | Ahora | Por qué |
|---|---|---|
| `Pleno` | **`Metrónom@`** | El nombre estaba abierto y el de la maqueta dice mejor lo que premia |
| `Abstract@` | **`Abstract@`** (vuelve atrás) | Se había adoptado `Fontaner@` de la maqueta, que es un chiste de fontanero sobre las cacas. Al fijar el vocabulario de figuras el mismo día —`caca` pasa a `abstracto`— el chiste se queda sin referente y `Abstract@` vuelve a ser el nombre coherente. **Segundo renombrado de la misma medalla en una sesión**, que es la señal de que los nombres deberían cerrarse con el grupo y no a base de iteraciones |
| `Impecable` | **`Impecable`** (sin cambio) | La maqueta llama `Superviviente` al mes sin fallo, pero ese nombre **ya está** en otra regla (resolver en ≤4 tres días duros). Adoptarlo dejaría dos reglas distintas con el mismo nombre, así que se rechaza |

Pendiente de la maqueta y **no adoptado todavía**: `Rajad@` (tres o más ausencias en los días duros), que
sería el primer logro explícitamente negativo — el "muro de la vergüenza" que el grupo pidió entre bromas.
Necesita que lo confirmen, porque señala a una persona por no jugar.

### Dos cifras que estaban mal

| Medalla | Decía | Es | Por qué |
|---|---|---|---|
| **Pleno** | 12% | **4,9%** | Se midió con una definición de "día del mes" distinta de la que implementa el código. Con la regla anterior el valor real era **0**: los días de la temporada salen de los datos, así que una sola persona jugando un domingo se lo bloqueaba a todo el grupo. La medalla era inganable |
| **El día imposible** | 2 personas, una vez | **4 personas, en 2 días** | Se contó un solo día (2025-12-15, media 5,67) y hay otro (2026-03-24, media 6,00). Verificado por SQL y por el catálogo, que coinciden |

`Pleno` sigue siendo exactamente lo que se buscaba —4,9% cae en la banda de *raro*— pero por una razón
distinta a la que el brief creía. Y `Verdugo` baja del 34% al 32,5% porque diez de sus créditos históricos
salían de días de fin de semana en los que jugaba **una sola persona**, y ser el mejor del día era
automático.

### Figuras

Umbrales **provisionales**: dependen del clasificador, que todavía no está calibrado (ver el límite al
final). Los porcentajes son con el clasificador actual, y **medidos antes de la regla de días laborables**:
hay que rehacerlos junto a la calibración, no por separado.

| Medalla | Condición | Logran | Nivel |
|---|---|---|---|
| **Ornitólog@** | 4 loros en un mes | 3% | legendario |
| **Arquitect@** | 4 escuadras en un mes | 2% | legendario |
| **Florista** | 5 flores en un mes | 8% | raro |
| **Coleccionista** | las cuatro figuras en el mismo mes | 32% | común |
| **Abstract@** | 12 abstractos en un mes | 24% | común |

**Los umbrales son los calibrados, no los de la maqueta de diseño.** El
[diseño de la liga arcade](../sources/2026-08-05-diseno-liga-arcade.md) pide "más de 10" en cada figura, que
es la propuesta original y **no la logra nadie**: máximo histórico 6, media 1,1, cero de 123 parejas
jugador-mes. Decisión del usuario el 2026-08-05: se asumen los calibrados. Los nombres sí se toman de la
maqueta donde tienen referente; `Abstract@` conserva el suyo porque la categoría se llama `abstracto`.

El máximo histórico observado por categoría y mes: loro 6, flores 8, geometrico 6, abstracto 18. **Medido con el clasificador desmentido**, así que hay que remedirlo con el calibrado. Los umbrales
están puestos justo por debajo de lo que alguien ha llegado a hacer, que es donde un logro es difícil sin
ser imposible.

## Reglas del sistema

**Solo cuentan los días laborables.** Sábado y domingo no otorgan nada, ni una medalla permanente. Las
partidas de fin de semana se siguen guardando; la exclusión vive en el cálculo
([reglas-temporadas](reglas-temporadas.md)).

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
| **¿"El mejor del día" exige muestra mínima?** | `Verdugo` da el crédito aunque ese día jugasen dos personas. Medido: **25 de los 447 créditos históricos** salen de días con menos de cinco jugadores, y la regla de días laborables solo tapa 10 de esos 25. Los otros 15 son laborables con poca gente (festivos, agosto). Aplicar aquí el mismo umbral de 5 que la dificultad sería coherente, pero es una regla nueva y la decide el grupo |

## Límite honesto

**Los umbrales de las medallas de figuras no son fiables todavía.** Salen del clasificador sin calibrar, que
mandaba el 69% de los patrones a la papelera contando filas — criterio que las 30 etiquetas humanas
desmintieron ([brief de figuras](ranking-de-figuras.md)). El reparto humano es abstracto 33% y flores 37%,
casi el inverso. Cuando el clasificador esté calibrado, estos cinco umbrales hay que **volver a medirlos**, y
por eso las medallas se calculan en vez de guardarse.

Los de rendimiento y constancia sí son firmes: no dependen del clasificador, solo de puntuaciones y
fechas, que están verificadas.
