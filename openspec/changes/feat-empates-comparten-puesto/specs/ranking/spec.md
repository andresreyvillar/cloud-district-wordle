# Deltas de `ranking` — feat-empates-comparten-puesto

## ADDED Requirements

### Requirement: Los empates comparten puesto

Dos jugadores con la misma media de temporada ocupan **el mismo puesto**, y el siguiente salta tantos
números como gente haya empatada por delante.

El desempate interno —más días jugados, luego el nombre— **sigue existiendo** y decide el orden en que se
listan, porque el resultado tiene que ser el mismo en cada ejecución. Lo que deja de hacer es fabricar una
diferencia de puesto que no existe.

Dos medias cuentan como iguales cuando coinciden **con los decimales que se publican**: si a la vista son el
mismo número, separarlas es incomprensible para quien lee.

#### Scenario: dos con la misma media comparten puesto
- GIVEN dos jugadores con idéntica media de temporada
- WHEN se calcula la clasificación
- THEN los dos tienen el mismo número de puesto

#### Scenario: después de un empate, el puesto salta
- GIVEN dos jugadores empatados en el segundo puesto
- WHEN se calcula la clasificación
- THEN el siguiente ocupa el cuarto

#### Scenario: el orden de la lista sigue siendo determinista
- GIVEN dos jugadores empatados
- WHEN se calcula la clasificación dos veces con las filas en distinto orden
- THEN se listan en el mismo orden las dos veces

#### Scenario: una diferencia invisible es un empate
- GIVEN dos medias que solo difieren por debajo de los decimales publicados
- WHEN se calcula la clasificación
- THEN comparten puesto

#### Scenario: quien no clasifica no comparte puesto
- GIVEN alguien por debajo del mínimo para clasificar
- WHEN se calcula la clasificación
- THEN sigue sin puesto

verified-by:
  - tests/slices/empates-comparten-puesto/test_empates.py

## MODIFIED Requirements

### Requirement: El desempate ordena la lista, no reparte puestos

Cuando dos jugadores tienen la misma media, el desempate —más días jugados, luego el nombre— **decide en qué
orden se listan** y ya no en qué puesto quedan.

Antes decidía las dos cosas, y eso fabricaba una diferencia que no existe: quien juega un día más no ha
hecho una temporada mejor que quien empata con él, ha jugado más. Si esa participación tiene que valer, lo
hace la imputación, que ya está dentro de la media.

El desempate sigue siendo obligatorio: sin él, el orden de la lista dependería del orden en que la base de
datos devuelve las filas, y dos ejecuciones darían resultados distintos.

#### Scenario: el desempate ordena
- GIVEN dos jugadores con la misma media y distinto número de días jugados
- WHEN se calcula la clasificación
- THEN va antes en la lista el que jugó más días

#### Scenario: pero comparten puesto
- GIVEN esos mismos dos jugadores
- WHEN se mira su número de puesto
- THEN es el mismo para los dos

verified-by:
  - tests/slices/empates-comparten-puesto/test_empates.py
  - tests/slices/clasificacion-de-temporada/test_clasificacion.py
