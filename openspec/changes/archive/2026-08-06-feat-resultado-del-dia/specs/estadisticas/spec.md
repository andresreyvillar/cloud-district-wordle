# Deltas de `estadisticas` — feat-resultado-del-dia

## ADDED Requirements

### Requirement: La jornada en curso se puede mirar, y dice si cuenta todavía

La vista del día muestra la **última jornada con resultados** —derivada de los datos, no del reloj—, quién ha
jugado con sus intentos, quién falta, y cómo se ha dado la palabra comparada con la media de la temporada.

Y declara si esa jornada **cuenta ya para la temporada**. Un día entra si es laborable y lo juegan al menos
la muestra mínima, así que a media mañana la jornada existe, tiene resultados y todavía no puntúa. Sin
decirlo, alguien mira su nota, la ve cambiar y concluye que el sistema miente.

#### Scenario: la jornada en curso se deriva de los datos
- GIVEN resultados de varias jornadas
- WHEN se abre la vista del día
- THEN muestra la jornada más alta con resultados, no la que diga el reloj del navegador

#### Scenario: quien ha jugado aparece con su resultado
- GIVEN resultados de la jornada
- WHEN se muestran
- THEN aparece cada jugador con sus intentos, del mejor al peor, y el fallo se distingue de un 6

#### Scenario: quien falta aparece contado
- GIVEN un jugador de la temporada sin resultado en la jornada
- WHEN se muestra el día
- THEN aparece entre quien falta, con su nombre y contado

#### Scenario: el día se compara con la temporada
- GIVEN al menos un resultado en la jornada
- WHEN se muestra el día
- THEN se ve su media y si ha salido más dura o más fácil que la de la temporada, con la diferencia

#### Scenario: una jornada por debajo de la muestra mínima lo declara
- GIVEN una jornada con menos resultados que la muestra mínima
- WHEN se muestra
- THEN declara que aún no cuenta y cuántos faltan para que cuente

#### Scenario: un día no laborable no cuenta aunque tenga muestra
- GIVEN una jornada en sábado jugada por todo el grupo
- WHEN se muestra
- THEN los resultados aparecen y la vista declara que ese día no puntúa

#### Scenario: sin resultados no hay jornada
- GIVEN ningún resultado
- WHEN se abre la vista del día
- THEN lo declara en lugar de inventar una jornada

verified-by:
  - tests/slices/resultado-del-dia/dia.test.js
