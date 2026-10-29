# Deltas de `ranking` — feat-clasificacion-de-temporada

## ADDED Requirements

### Requirement: La clasificación se calcula sobre los días de la temporada, no sobre las partidas jugadas

Todo día válido de la temporada tiene una nota para cada jugador. Si jugó, la suya; si no:

```
imputado(día) = min( max( dificultad(día), media_personal ) + margen , 7 )
```

donde `dificultad(día)` es la media del grupo ese día y `media_personal` la media del jugador contando
**solo sus días jugados** — usar la ya imputada volvería la fórmula circular.

Cada pieza responde a un fallo medido: `dificultad` hace que faltar un día fácil apenas penalice;
`max(…, media_personal)` impide que faltar mejore la media, que ocurría en 9 ocasiones del histórico;
`margen` impide que callarse un mal resultado salga mejor que publicarlo; `min(…, 7)` pone el tope en el
fallo.

El denominador es el mismo para todos, así que las medias se comparan sin reglas añadidas y **no hace falta
un umbral mínimo de días para clasificar**.

#### Scenario: los jugadores se ordenan por su media imputada
- GIVEN una temporada con varios jugadores
- WHEN se calcula la clasificación
- THEN salen ordenados por media imputada de menor a mayor

#### Scenario: faltar nunca mejora la media
- GIVEN un jugador cuya media personal es peor que la dificultad de un día
- WHEN falta ese día
- THEN su media final no baja respecto a haberlo jugado con su media habitual

#### Scenario: la ausencia en un día difícil penaliza más
- GIVEN dos jugadores idénticos que faltan un día cada uno, uno fácil y otro difícil
- WHEN se calcula la clasificación
- THEN el que faltó el día difícil queda por detrás

#### Scenario: jugar poco no da ventaja
- GIVEN un jugador con muy buena media que solo juega unos pocos días
- WHEN se calcula la clasificación
- THEN no adelanta a quien jugó todos los días con media parecida

#### Scenario: el empate se rompe por participación
- GIVEN dos jugadores con la misma media imputada
- WHEN se ordena la tabla
- THEN va delante el que jugó más días

verified-by:
  - tests/slices/clasificacion-de-temporada/test_clasificacion.py

### Requirement: La imputación es auditable

Cada fila de la clasificación publica sus **días jugados** y su **media real** además de la imputada, y el
detalle por jornada dice si esa nota se jugó o se imputó.

Sin eso la tabla es una caja negra: el grupo no podría comprobar de dónde sale la diferencia entre lo que
jugó y lo que puntúa.

#### Scenario: cada fila muestra lo jugado y lo imputado
- GIVEN una clasificación calculada
- WHEN se inspecciona una fila
- THEN incluye días jugados, media real, media imputada y el detalle por jornada marcando lo imputado

verified-by:
  - tests/slices/clasificacion-de-temporada/test_clasificacion.py
