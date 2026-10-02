# Deltas de `ranking` — feat-pestana-info

## ADDED Requirements

### Requirement: El catálogo de reglas incluye el SuperWordleBros y distingue las históricas

El catálogo (`tools/rules.py`) tiene un eje **`juego`** con las reglas del SuperWordleBros que ya se aplican:
puntos por puesto en cada nivel, las estrellas por delante del tiempo, cuándo se congela y se cierra cada nivel,
que solo los días que cuentan crean nivel, y que el nivel del último día laborable puntúa en el mes siguiente.
Sus números se leen de las constantes del cálculo (`juego.ESCALA`, `juego.PUNTOS_DESDE_EL_OCTAVO`,
`juego.HORA_DE_CONGELAR`, `seasons.MUESTRA_MINIMA_DEL_DIA`).

Cada regla lleva además `historica`: verdadera en las que solo valen para la temporada 0, para que la web pueda
dejarlas fuera de las vigentes sin borrarlas del catálogo. Las propuestas siguen en el catálogo como
`sin-decidir`, con lo que falta decidir.

`juego.HORA_DE_CONGELAR` es la misma hora que usa el cron (`v2/js/domain/superbros.js`), y un test comprueba
que coinciden.

#### Scenario: el juego tiene sus reglas con números del código
- GIVEN el catálogo
- WHEN se buscan las reglas del eje juego
- THEN están las cinco, aplicadas, y sus parámetros son los que usa el cálculo

#### Scenario: las de la temporada 0 son históricas
- GIVEN el catálogo
- WHEN se miran las reglas de la temporada 0
- THEN están marcadas como históricas, y ninguna otra lo está

#### Scenario: la hora es la misma que la del cron
- GIVEN la hora del catálogo y la del script del cron
- WHEN se comparan
- THEN son iguales

verified-by:
  - tests/slices/reglas-explicadas/test_reglas.py
