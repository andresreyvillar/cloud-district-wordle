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

### Requirement: Las filas con atribución cruzada se declaran y no se tocan

Una fila cuyo identificador pertenece a una persona y cuyo nombre mostrado indica otra **no la resuelve
este comando**. Se cuenta aparte y se deja exactamente como está.

**Ninguna de las dos señales basta, y las dos alternativas se probaron:**

- *Reatribuir al dueño del nombre* **fabrica partidas**. Se implementó y se ejecutó, apoyándose en que cinco
  de las seis filas cruzadas que el dueño del nombre ya tenía registradas coincidían en puntuación exacta.
  El canal desmintió la inferencia: de las tres restantes, dos correspondían a días en los que esa persona
  **no publicó nada** y la tercera era copia byte a byte de la cuadrícula de otra jugadora.
- *Eliminarlas* destruye datos apoyándose en que un nombre no cuadra con un identificador, que no es prueba
  de que la fila sea falsa.

Lo que las delata es **el canal**, y este cálculo no lo consulta. Por eso las declara y para. Hay una prueba
barata para quien decida: tras el backfill de patrones, **una fila sin mensaje en el canal se queda sin
patrón**.

Consecuencia declarada: la fila cruzada sigue ocupando su clave `(identificador, puzzle)`, así que puede
bloquear la canonización de su dueño legítimo. Ese bloqueo también se informa.

#### Scenario: identificador y nombre señalan a personas distintas
- GIVEN una fila cuyo identificador pertenece a un jugador y cuyo nombre mostrado es de otro
- WHEN se ejecuta la canonización
- THEN la fila queda intacta y consta en el recuento de atribuciones cruzadas

#### Scenario: una cruzada no se fusiona con la partida del dueño del nombre
- GIVEN una fila cruzada que coincide en puzzle y puntuación con una fila de la persona del nombre
- WHEN se ejecuta la canonización
- THEN las dos filas siguen existiendo

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
