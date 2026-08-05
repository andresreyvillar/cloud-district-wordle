# Deltas de `resultados` — feat-identidad-canonica

## ADDED Requirements

### Requirement: El censo de partidas solo baja por fusión

Una canonización de identidad puede reducir el número de filas, y **solo** por un motivo, que se informa
con su cantidad: **la fusión de dos filas que son la misma partida**. Una fusión exige que las dos filas
coincidan en jugador resuelto, puzzle y puntuación; con puntuación distinta no se fusiona, se declara
conflictiva y se deja intacta.

Nada se elimina por ningún otro motivo. En particular, una atribución cruzada **no** se elimina: se
reatribuye (ver el Requirement siguiente), y solo desaparece si al reatribuirse resulta ser una partida ya
registrada — es decir, por fusión.

Cualquier otra variación del censo es un fallo. La suma es verificable:
`filas_después = filas_antes − fusionadas`.

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
- WHEN la canonización informa de F fusiones
- THEN la tabla queda con N − F filas

#### Scenario: una partida legítima nunca se pierde
- GIVEN dos filas del mismo jugador con puzzles distintos
- WHEN se ejecuta la canonización
- THEN las dos siguen existiendo

verified-by:
  - tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py

### Requirement: Las filas con atribución cruzada se reatribuyen y se declaran

Una fila cuyo identificador pertenece a una persona y cuyo nombre mostrado indica otra **es una partida
jugada** con el identificador equivocado. Se reatribuye a quien dice el nombre, y el recuento la declara
aparte para que el cambio sea auditable.

**El nombre mostrado pesa más que el identificador**, y no por simetría sino por evidencia. Las ocho filas
cruzadas del histórico llevan el identificador de una persona y el nombre de otra; de las seis que el dueño
que indica el nombre ya tenía registradas, **cinco coinciden en puntuación exacta**, lo que no es
casualidad. El identificador de esas filas vino de un mapeo defectuoso; el nombre vino del mensaje.

La versión anterior de este Requirement decía eliminarlas. El ensayo contra producción demostró que eso
**perdía dos partidas**: dos de las ocho no existen bajo el identificador correcto, así que su única copia
era la fila cruzada.

#### Scenario: identificador y nombre señalan a personas distintas
- GIVEN una fila cuyo identificador pertenece a un jugador y cuyo nombre mostrado es de otro
- WHEN se ejecuta la canonización
- THEN la fila pasa a tener el identificador de quien dice el nombre, y consta en el recuento de
  atribuciones cruzadas

#### Scenario: reatribuir no puede duplicar una partida
- GIVEN una fila cruzada cuyo dueño real ya tiene ese puzzle con la misma puntuación
- WHEN se ejecuta la canonización
- THEN queda una sola fila para ese jugador y ese puzzle

#### Scenario: una cruzada con puntuación distinta se declara y no se toca
- GIVEN una fila cruzada cuyo dueño real ya tiene ese puzzle con **otra** puntuación
- WHEN se ejecuta la canonización
- THEN la fila queda intacta y consta en el recuento de conflictivas, porque elegir una de las dos
  puntuaciones sería inventar el dato

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
