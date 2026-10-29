# Deltas de `resultados` — feat-backfill-de-patrones

## ADDED Requirements

### Requirement: El relleno de patrones solo escribe donde falta

Una operación de relleno escribe `pattern` únicamente en las filas que lo tienen vacío. Las filas con
patrón quedan intactas, de modo que la operación es idempotente: ejecutarla dos veces produce el mismo
estado que ejecutarla una.

```yaml
checks:
  - type: column
    table: wordle_results
    column: pattern
```

#### Scenario: una fila con patrón no se modifica
- GIVEN una fila cuyo `pattern` ya tiene contenido
- WHEN se ejecuta el relleno
- THEN el valor de `pattern` de esa fila es el mismo antes y después

#### Scenario: dos ejecuciones seguidas dejan el mismo estado
- GIVEN un conjunto de filas parcialmente rellenado
- WHEN el relleno se ejecuta dos veces
- THEN el estado de la tabla tras la segunda ejecución es idéntico al de la primera

verified-by:
  - tests/slices/backfill-de-patrones/test_backfill_de_patrones.py

### Requirement: El relleno no altera el censo de resultados

Una operación de relleno de patrones no crea ni elimina filas, y no modifica ninguna columna que no sea
`pattern`. El número de resultados por jugador y por puzzle es idéntico antes y después.

#### Scenario: el número de filas no cambia
- GIVEN la tabla con N filas
- WHEN se ejecuta el relleno completo
- THEN la tabla sigue teniendo N filas

#### Scenario: la puntuación y la fecha no se tocan
- GIVEN una fila con su puntuación y su fecha
- WHEN el relleno escribe su patrón
- THEN la puntuación y la fecha conservan el valor que tenían

verified-by:
  - tests/slices/backfill-de-patrones/test_backfill_de_patrones.py

### Requirement: Las filas sin mensaje localizable quedan declaradas

Cuando una fila sin patrón no tiene mensaje correspondiente en el histórico del canal, la fila
permanece sin patrón y la operación la cuenta como no resuelta. El recuento final distingue tres
cantidades: filas rellenadas, filas intactas y filas no resueltas.

#### Scenario: fila sin mensaje en el canal
- GIVEN una fila sin patrón cuyo mensaje no aparece en el histórico
- WHEN termina el relleno
- THEN la fila sigue sin patrón y aparece en el recuento de no resueltas

verified-by:
  - tests/slices/backfill-de-patrones/test_backfill_de_patrones.py
