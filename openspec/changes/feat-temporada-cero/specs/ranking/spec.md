# Deltas de `ranking` — feat-temporada-cero

## MODIFIED Requirements

### Requirement: Las temporadas están numeradas desde un límite, y antes del límite todo es la temporada 0

Existe una fecha límite. **Todo lo jugado antes es la temporada 0**, un solo bloque con todo el histórico.
Desde el límite, cada mes natural es una temporada y lleva su número de orden: el mes del límite es la 1, el
siguiente la 2.

El número de orden **se deriva** del límite, no se almacena, así que no puede desincronizarse del modelo.

El identificador de un mes sigue siendo `AAAA-MM`, para que un enlace compartido en el canal diga de qué mes
habla; el de la temporada 0 es `0`.

#### Scenario: lo anterior al límite es la temporada 0
- GIVEN un resultado con fecha anterior al límite
- WHEN se determina su temporada
- THEN es la temporada 0, sea de qué mes sea

#### Scenario: el mes del límite es la temporada 1
- GIVEN un resultado del mes del límite
- WHEN se determina su temporada y su número de orden
- THEN es ese mes, y su número de orden es 1

#### Scenario: la temporada 0 es un solo bloque
- GIVEN resultados repartidos en varios meses anteriores al límite
- WHEN se listan las temporadas
- THEN aparece **una sola** entrada para todo ese periodo, no una por mes

verified-by:
  - tests/slices/temporada-mensual/test_temporada_mensual.py

## ADDED Requirements

### Requirement: La temporada 0 se rige por las reglas que estaban en vigor cuando se jugó

La clasificación de la temporada 0 replica las reglas de la v1 (`js/script.js`):

| Regla | Temporada 0 (legacy) | Temporada numerada |
|---|---|---|
| Jornadas que cuentan | **todas** las que tengan algún resultado | laborables con ≥5 jugadores |
| Media | de las partidas jugadas | con las ausencias imputadas |
| Mínimo para clasificar | **5 partidas** (`MIN_GAMES_FOR_BEST_AVG`) | ninguno: la imputación ya lo hace |

Aplicar hacia atrás las reglas nuevas cambiaría el resultado de un partido ya jugado. Y está medido lo que
pasaría: de los 159 días que quedarían filtrando, **siete de veinte jugadores tendrían más del 70% de la
temporada imputada** —a quien se incorporó el 22 de julio se le contarían 156 ausencias desde noviembre—, lo
que produce un artefacto y no una clasificación.

**Única desviación del legacy, y es deliberada:** se agrupa por **identidad de Slack** y no por nombre
mostrado. El legacy agrupaba por nombre, lo que partía en dos a quien se hubiera renombrado — y con los datos
reales eso coronaba a la mitad de una identidad partida (9 partidas de un lado, 6 del otro). El arreglo de
identidad es una corrección de datos, no un cambio de regla.

La instantánea **declara que no está imputada**, para que la vista no presente su media como comparable con
la de las numeradas.

#### Scenario: la temporada 0 no imputa ausencias
- GIVEN un jugador que solo jugó unos pocos días del periodo anterior al límite
- WHEN se calcula la clasificación de la temporada 0
- THEN su media es la de sus partidas jugadas, y no se le añade ninguna ausencia

#### Scenario: la temporada 0 no filtra jornadas
- GIVEN una jornada de fin de semana y otra con dos jugadores, las dos anteriores al límite
- WHEN se determinan los días de la temporada 0
- THEN las dos cuentan, como hacía la v1

#### Scenario: por debajo del mínimo del legacy no se clasifica
- GIVEN un jugador con menos de cinco partidas en la temporada 0
- WHEN se calcula la clasificación
- THEN aparece en la tabla sin puesto, aunque su media sea la mejor

#### Scenario: la instantánea declara el criterio
- GIVEN la instantánea de la temporada 0
- WHEN se inspecciona
- THEN dice que su clasificación no está imputada

#### Scenario: una temporada numerada sí imputa
- GIVEN una temporada posterior al límite con un jugador que faltó un día
- WHEN se calcula su clasificación
- THEN ese día se le imputa

verified-by:
  - tests/slices/temporada-mensual/test_temporada_mensual.py
  - tests/slices/clasificacion-de-temporada/test_clasificacion.py
