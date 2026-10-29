# Deltas de `estadisticas` — feat-ficha-de-jugador

## ADDED Requirements

### Requirement: Un jugador puede ver de qué se compone su media de temporada

La media de temporada de un jugador **incluye jornadas que no jugó**, porque el modelo imputa las
ausencias. Un número así no se sostiene sin poder mirarse dentro: la ficha desglosa la temporada jornada a
jornada, distingue lo jugado de lo imputado y publica **la diferencia entre las dos medias**, que es
exactamente lo que le costó faltar.

Nada de esto se recalcula en la vista: todo está en la instantánea que publica el bot
([ADR 0008](../../../decisions/0008-donde-vive-el-calculo.md)), así que la ficha y el canal no pueden
divergir.

#### Scenario: la ficha resume la temporada del jugador
- GIVEN un jugador con resultados en una temporada
- WHEN se abre su ficha
- THEN muestra su puesto, su media de temporada, su media de las partidas jugadas, las jornadas que jugó de
  las que la temporada tiene, y su mejor y su peor partida

#### Scenario: el desglose distingue lo jugado de lo imputado
- GIVEN una temporada con jornadas imputadas al jugador
- WHEN se mira el desglose
- THEN cada jornada aparece con su nota, su fecha y su número, y las imputadas se distinguen de las jugadas

#### Scenario: la ficha publica el coste de faltar
- GIVEN un jugador con al menos una jornada imputada
- WHEN se abre su ficha
- THEN dice cuántas ausencias tiene y cuánto separan su media de temporada de la de sus partidas jugadas

#### Scenario: una temporada sin imputación no inventa un coste
- GIVEN una temporada que no imputa ausencias
- WHEN se abre la ficha de uno de sus jugadores
- THEN la ficha declara que esa temporada no imputa, en lugar de publicar un coste de cero

#### Scenario: la distribución de intentos cuadra con lo jugado
- GIVEN un jugador con partidas en la temporada
- WHEN se mira su distribución por número de intentos
- THEN suma exactamente sus partidas jugadas, con el fallo como último cajón

verified-by:
  - tests/slices/ficha-de-jugador/ficha.test.js
