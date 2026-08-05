# Reglas de temporada — modelo de participación

> Síntesis citable. Cada afirmación cita su fuente. Lo que aquí está **acordado** puede convertirse en
> Requirement; lo que está **abierto** no se especifica todavía.
> Fuente principal: [hilo de reglas](../sources/2026-08-04-hilo-reglas-temporadas.md).

## Lo acordado

**Las temporadas son mensuales y el marcador se reinicia el día 1.** Votado en el canal, 6 a favor y
0 en contra ([fuente](../sources/2026-08-04-hilo-reglas-temporadas.md)).

**Una temporada son sus días laborables: de lunes a viernes.** Acordado con el dueño del proyecto el
2026-08-04 — **no votado en el canal**, a diferencia de la regla anterior. Sábado y domingo no fijan la
dificultad de un día, no cuentan para ningún umbral y no son días que un jugador pueda faltar. La regla
alcanza a **los tres ejes**: puntuación, medallas y álbum de figuras.

Los resultados de fin de semana **se siguen capturando y guardando**: la exclusión vive en el cálculo, no
en la ingesta, así que la decisión es reversible sin haber perdido nada.

Medido sobre el histórico, la regla es casi un no-op y arregla un fallo:

| Efecto | Medida |
|---|---|
| Volumen afectado | 13 resultados de 1533 (**0,85%**) en 10 jornadas; 9 de esas 10 son **un único jugador** |
| Dificultad del día, día imposible, superviviente, días de la temporada | **sin cambio**: ninguna jornada de fin de semana llega a los 5 jugadores del umbral de muestra |
| `Pleno` | **de 0 a 6** de 123 parejas jugador-mes. Ver abajo |

**Lo que arregla.** Los días de la temporada se derivan de los datos, así que mientras el fin de semana
contaba, **una sola persona jugando un domingo convertía ese domingo en día de la temporada y se lo
bloqueaba a todo el grupo**. Cinco de los nueve meses del histórico tienen una jornada así.

**El límite de la medida.** El efecto es casi nulo *porque hoy nadie juega en fin de semana* (1,3 jugadores
de media frente a 8,8 en laborable). Si el grupo empezara a jugar los sábados, esta regla pasaría de
formalidad a decisión con consecuencias. El 0,85% es de hoy, no una propiedad del juego.

**La participación se valora imputando resultado a los días no jugados**, en función de lo que el
grupo sufrió ese día. Acordado en conversación de diseño, sobre datos de producción.

## El modelo

La clasificación de una temporada no se calcula sobre las partidas jugadas sino sobre **los días de la
temporada**. Todo día tiene un número; si el jugador no participó, se le imputa:

```
imputado(día) = min( max( dificultad(día), media_personal ) + margen , 7 )

dificultad(día)  = media de intentos del grupo ese día
media_personal   = media del jugador en la temporada, contando SOLO sus días jugados
margen           = 0,5
```

`media_personal` se calcula solo con los días jugados **a propósito**: usar la media ya imputada
volvería la fórmula circular.

### Qué propiedades cumple, y por qué cada pieza está ahí

| Pieza | Qué garantiza |
|---|---|
| `dificultad(día)` | Faltar un día fácil apenas penaliza (se lee como "no pude"); faltar un día duro penaliza (se lee como "no quise ensuciar mi media"). Es el objetivo original de la regla |
| `max(…, media_personal)` | **Faltar nunca puede mejorar tu media.** Sin esta pieza, a un jugador con media peor que la dificultad del día le convenía ausentarse: medido sobre el histórico, ocurría en 9 ocasiones, con hasta −0,18 de "premio" por faltar 9 días |
| `margen` | Ausentarse nunca es mejor que publicar. Sin margen, el día imputado es neutro y dejar de publicar un mal resultado sigue teniendo premio |
| `min(…, 7)` | El tope es el fallo: ninguna ausencia puede penalizar más que la peor partida posible |
| media sobre días, no sobre partidas | El denominador es igual para todos, así que las medias son comparables sin mecanismos añadidos |

### Lo que el modelo hace innecesario

- **Un umbral mínimo de días para clasificar.** Existía para que un jugador de 3 días no ganase el mes;
  la imputación ya lo impide, y el jugador aparece en la tabla en el puesto que le corresponde, que es
  más informativo que no aparecer.
- **Una penalización separada de la media.** No hay dos números (media + castigo): hay uno.
- **Una regla de "lo avanzado del mes".** El peso decae por construcción: el día 3 una ausencia es un
  tercio de la nota, el día 23 es un veintitresavo. Consecuencia declarada: las ausencias tempranas
  pesan más que las tardías, y la tabla es volátil la primera semana.

### Parámetros y su calibración

| Parámetro | Valor | Evidencia |
|---|---|---|
| `margen` | 0,5 | Con 0,5 y con 1,0 el campeón es **el mismo en los 8 meses** del histórico; solo cambian las distancias. 0,5 mueve menos a quien juega a diario |
| muestra mínima para medir dificultad | 5 jugadores | Con menos, la media del día no calibra nada. Los días por debajo del mínimo no forman parte de la temporada |
| días que forman la temporada | los días **laborables** con muestra suficiente | Dos filtros independientes, y hacen falta los dos: el de día laborable excluye el fin de semana por regla, y el de muestra absorbe los laborables en que el grupo tampoco jugó (festivos, agosto). Antes solo estaba el segundo, y excluía los fines de semana **por accidente**: si un sábado jugaran cinco personas, contaría |

## Efecto medido sobre el histórico

Aplicado a los 8 meses con datos suficientes, el modelo **cambia el campeón en 6**. En cinco de los
seis casos, el campeón actual es alguien con **menos de la mitad de los días jugados** (tres casos con
3 días de más de 20). El sexto es un cambio entre jugadores habituales.

La lectura no es que el modelo sea severo, sino que **la clasificación actual la gana quien juega
poco**: al promediar solo las partidas jugadas, quien se ausenta compite con una media depurada de sus
peores días. Con el modelo, quien no falta ningún día deja de estar en desventaja.

## Lo que sigue abierto

Ninguna de estas líneas se especifica hasta que el grupo la cierre:

| Abierto | Qué falta decidir |
|---|---|
| Podios separados de intentos y de participación | Si conviven con la clasificación única o la sustituyen |
| Nota ponderada media + participación | Con este modelo, la participación **ya** está dentro de la media. Una ponderación adicional la contaría dos veces |
| Rachas (mejor y peor) | Qué es una racha: acertar N días seguidos, o mejorar N días seguidos |
| Mayor remontada | Respecto a qué: posición del mes anterior o dentro del propio mes |
| Cierre de la etapa actual el 31 de agosto | Si se corona un ganador del periodo completo y con qué criterio |
| Ausencias justificadas | Sin decisión del grupo. Encajaría excluyendo días del denominador de un jugador concreto, no cambiando la fórmula |

## Límite honesto del modelo

El comportamiento que la regla castiga —jugar, ver que sale mal y no publicar— **no es observable en
los datos**: no hay rastro de una partida no publicada. El modelo no lo detecta, lo *presume* a partir
de la dificultad del día. La presunción tiene base (en los días difíciles participan 8,6 jugadores de
media frente a 9,9 en los fáciles, correlación −0,207), pero es una presunción y se equivocará con
quien tuviera una reunión a primera hora. El `margen` es precisamente el precio que paga ese jugador
por una regla que el grupo acepta como aproximación.
