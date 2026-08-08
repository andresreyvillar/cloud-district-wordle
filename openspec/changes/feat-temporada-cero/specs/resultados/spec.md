# Deltas de `resultados` — feat-temporada-cero

## MODIFIED Requirements

### Requirement: Lo calculado se materializa aparte de lo crudo

Lo que el pipeline calcula de una temporada vive en `season_snapshots`, **nunca en `wordle_results`**. La
tabla cruda solo guarda lo que ocurrió; lo derivado se puede borrar y recalcular sin perder nada.

La clave es `temporada`, así que recalcular **actualiza** en lugar de acumular versiones. Se registra
`updated_at` para poder detectar una instantánea rancia.

**Hay una fila por temporada del modelo, no una por mes con datos.** Con las temporadas numeradas desde un
límite, todo el periodo anterior es **una sola fila** (`temporada = '0'`) en lugar de una por cada mes. Al
cambiar el límite hay que **borrar las filas que el modelo ya no reconoce** antes de rematerializar: una
instantánea huérfana se sigue leyendo desde la web y aparecería como una temporada fantasma.

Cada instantánea declara además **si su clasificación está imputada**, para que un consumidor no compare
como equivalentes la media de una temporada numerada y la de la 0.

```yaml
checks:
  - type: table
    name: season_snapshots
    columns: [temporada, payload, updated_at]
    rls: read-only-for-publishable-key
```

#### Scenario: materializar deja una fila por temporada del modelo
- GIVEN resultados repartidos en varios meses anteriores al límite
- WHEN se materializan las temporadas
- THEN existe **una sola** fila para todo ese periodo

#### Scenario: la instantánea declara su criterio
- GIVEN la instantánea de una temporada
- WHEN se inspecciona
- THEN dice si su clasificación está imputada

#### Scenario: materializar dos veces no duplica
- GIVEN una temporada ya materializada
- WHEN se vuelve a materializar
- THEN sigue habiendo una sola fila para ella, con la marca de tiempo actualizada

verified-by:
  - tests/slices/temporada-mensual/test_temporada_mensual.py
