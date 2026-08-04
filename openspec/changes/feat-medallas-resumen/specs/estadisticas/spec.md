# Deltas de `estadisticas` — feat-medallas-resumen

## ADDED Requirements

### Requirement: Una medalla es una función de los resultados, no un dato almacenado

Las medallas se calculan a partir de los resultados cada vez que se necesitan. No hay tabla, columna ni
caché de medallas.

La consecuencia buscada: cambiar un umbral recalcula el palmarés histórico completo sin migrar nada. La
consecuencia aceptada: el cálculo se repite en cada consumidor.

```yaml
checks:
  - type: cli-command
    describe: el cálculo no consulta ninguna tabla de medallas
```

#### Scenario: dos cálculos sobre los mismos datos coinciden
- GIVEN un conjunto de resultados y una temporada
- WHEN se calculan las medallas dos veces
- THEN el resultado es idéntico

#### Scenario: el orden de las filas no altera el resultado
- GIVEN los mismos resultados en distinto orden
- WHEN se calculan las medallas
- THEN el resultado es el mismo

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py

### Requirement: El cálculo de medallas es determinista y sin reloj

La temporada entra **por parámetro**, igual que los resultados. El cálculo no lee la fecha del sistema, y
por eso se puede verificar con datos fijos (§10 del protocolo).

#### Scenario: la temporada se pasa como argumento
- GIVEN unos resultados que abarcan varios meses
- WHEN se calculan las medallas de una temporada concreta
- THEN solo se consideran los resultados de esa temporada para las medallas de temporada

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py

### Requirement: Las medallas tienen dos alcances, y el alcance determina la ventana

Cada medalla es **de temporada** o **permanente**:

- Las de temporada se evalúan sobre los resultados de una temporada y se pueden ganar en varias.
- Las permanentes se evalúan sobre **todo el histórico** y no se repiten: la gesta ya está hecha.

| Medalla | Alcance | Condición | Nivel |
|---|---|---|---|
| Suertud@ | permanente | resolver en un intento | legendario |
| El día imposible | permanente | resolver en ≤4 un día cuya media del grupo sea ≥5,5 | legendario |
| Superviviente | temporada | resolver en ≤4 tres días de media ≥4,5 | legendario |
| Pleno | temporada | no faltar ningún día de la temporada (mínimo 10 días) | raro |
| Verdugo | temporada | ser el mejor del día cinco veces | común |
| Impecable | temporada | ninguna partida fallada, con 10 partidas mínimo | común |
| Fondista | temporada | 15 partidas o más | común |

Los umbrales están calibrados contra el histórico y su rareza medida está en
[el brief](../../../../docs/context/briefs/medallas.md). Un día con menos de cinco jugadores no cuenta
como difícil: su media no es fiable.

#### Scenario: una medalla de temporada se puede ganar dos veces
- GIVEN un jugador que cumple la misma medalla en dos temporadas
- WHEN se calcula su palmarés
- THEN la medalla aparece con dos repeticiones

#### Scenario: una permanente se gana una sola vez
- GIVEN un jugador que resolvió en un intento dos veces
- WHEN se calcula su palmarés
- THEN la medalla aparece una vez

#### Scenario: el umbral se cumple con igualdad
- GIVEN un jugador con exactamente 15 partidas en la temporada
- WHEN se calculan sus medallas
- THEN obtiene Fondista

#### Scenario: quedarse a uno del umbral no otorga
- GIVEN un jugador con 14 partidas en la temporada
- WHEN se calculan sus medallas
- THEN no obtiene Fondista

#### Scenario: el día imposible exige las dos condiciones
- GIVEN un jugador que resuelve en 3 un día cuya media fue 3,0, y otro que resuelve en 6 un día cuya media fue 5,8
- WHEN se calculan sus medallas
- THEN ninguno obtiene El día imposible

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py
