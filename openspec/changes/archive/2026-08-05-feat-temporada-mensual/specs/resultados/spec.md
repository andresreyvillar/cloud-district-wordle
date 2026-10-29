# Deltas de `resultados` — feat-temporada-mensual

## ADDED Requirements

### Requirement: Lo calculado se materializa aparte de lo crudo

Lo que el pipeline calcula de una temporada vive en `season_snapshots`, **nunca en `wordle_results`**. La
tabla cruda solo guarda lo que ocurrió; lo derivado se puede borrar y recalcular sin perder nada.

```yaml
checks:
  - type: table
    name: season_snapshots
    columns: [temporada, payload, updated_at]
    rls: read-only-for-publishable-key
```

La clave es `temporada`, así que recalcular **actualiza** en lugar de acumular versiones. Se registra
`updated_at` para poder detectar una instantánea rancia: es la mitigación declarada de introducir estado
derivado ([ADR 0008](../../../decisions/0008-donde-vive-el-calculo.md)).

#### Scenario: materializar deja una fila por temporada
- GIVEN una temporada calculada
- WHEN se materializa
- THEN existe una fila con su carga útil y su marca de tiempo

#### Scenario: materializar dos veces no duplica
- GIVEN una temporada ya materializada
- WHEN se vuelve a materializar
- THEN sigue habiendo una sola fila para ella, con la marca de tiempo actualizada

#### Scenario: el ensayo no escribe
- GIVEN el comando en modo ensayo
- WHEN se ejecuta
- THEN informa de lo que haría y no escribe ninguna fila

verified-by:
  - tests/slices/temporada-mensual/test_temporada_mensual.py
