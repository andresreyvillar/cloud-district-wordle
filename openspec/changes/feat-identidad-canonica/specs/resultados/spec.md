# Deltas de `resultados` — feat-identidad-canonica

## ADDED Requirements

### Requirement: El censo de partidas solo cambia por causas declaradas

Una canonización de identidad puede reducir el número de filas, pero **solo** por dos motivos, y los dos
se informan con su cantidad:

1. **Fusión por renombre**: dos filas que son la misma partida registrada bajo dos nombres del mismo
   jugador pasan a ser una.
2. **Atribución cruzada**: una fila cuyo identificador pertenece a una persona distinta de la que indica
   su nombre mostrado se elimina.

Cualquier otra variación del censo es un fallo. La suma es verificable:
`filas_después = filas_antes − fusionadas − eliminadas`.

```yaml
checks:
  - type: index
    table: wordle_results
    name: idx_slack_user_wordle_unique
    kind: unique
    columns: [slack_user_id, wordle_id]
```

#### Scenario: el censo cuadra con lo declarado
- GIVEN una tabla con N filas
- WHEN la canonización informa de F fusiones y E eliminaciones
- THEN la tabla queda con N − F − E filas

#### Scenario: una partida legítima nunca se pierde
- GIVEN dos filas del mismo jugador con puzzles distintos
- WHEN se ejecuta la canonización
- THEN las dos siguen existiendo

verified-by:
  - tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py

### Requirement: Las filas con atribución cruzada se eliminan y se declaran

Una fila cuyo identificador pertenece a una persona y cuyo nombre mostrado indica otra no es una partida:
es el resto de un cruce de mapeo. Se elimina, y el recuento la declara aparte de las fusiones para que
la diferencia sea auditable.

Se elimina en lugar de reasignarse porque no hay forma de saber a quién pertenece de verdad: el
identificador dice una persona, el nombre dice otra, y las dos afirmaciones tienen el mismo peso.

#### Scenario: identificador y nombre señalan a personas distintas
- GIVEN una fila cuyo identificador pertenece a un jugador y cuyo nombre mostrado es de otro
- WHEN se ejecuta la canonización
- THEN la fila se elimina y consta en el recuento de atribuciones cruzadas

verified-by:
  - tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py

### Requirement: Toda migración de identidad admite ensayo

El comando se puede ejecutar en modo ensayo: recorre, resuelve y cuenta exactamente lo que haría, sin
escribir ni eliminar nada. El recuento del ensayo y el de la ejecución real coinciden.

#### Scenario: el ensayo no modifica la tabla
- GIVEN una tabla con filas pendientes de canonizar
- WHEN se ejecuta el comando en modo ensayo
- THEN el recuento es el de la ejecución real y ninguna fila cambia

verified-by:
  - tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py
