# Deltas de `estadisticas` — feat-solo-dias-laborables

## ADDED Requirements

### Requirement: Una temporada son sus días laborables

Solo cuentan los resultados de **lunes a viernes**. Sábado y domingo no forman parte de ninguna temporada:
no fijan la dificultad de un día, no cuentan para ningún umbral y no son días que un jugador pueda faltar.

Las partidas de fin de semana **se siguen capturando y guardando**. La exclusión vive en el cálculo, no en
la ingesta: así la regla es reversible sin haber perdido nada.

La regla **no depende del umbral de muestra**. Hoy los dos coinciden por accidente —ninguna de las 10
jornadas de fin de semana del histórico llega a cinco jugadores— pero un sábado con seis jugadores tampoco
contaría.

El día de la semana se deriva de la **fecha de la fila**, nunca del reloj: el cálculo sigue siendo
reproducible con datos fijos (§10 del protocolo).

```yaml
checks:
  - type: cli-command
    describe: el día de la semana sale de la fecha de la fila, no de la fecha del sistema
```

#### Scenario: una partida de sábado no cuenta para un umbral
- GIVEN un jugador con 15 partidas de las que una cae en sábado
- WHEN se calculan sus medallas de la temporada
- THEN no obtiene Fondista, porque solo tiene 14 partidas que cuenten

#### Scenario: un fin de semana con muestra suficiente tampoco fija dificultad
- GIVEN un domingo que juegan cinco personas con media 5,8, y alguien que resuelve en 4
- WHEN se calculan las medallas permanentes
- THEN no obtiene El día imposible

#### Scenario: el cálculo no lee el reloj para saber qué día es
- GIVEN los mismos resultados con sus fechas
- WHEN se calculan las medallas dos veces
- THEN el resultado es idéntico, y depende solo de las fechas de las filas

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py

## MODIFIED Requirements

### Requirement: Las medallas tienen dos alcances, y el alcance determina la ventana

Cada medalla es **de temporada** o **permanente**:

- Las de temporada se evalúan sobre los resultados de una temporada y se pueden ganar en varias.
- Las permanentes se evalúan sobre **todo el histórico** y no se repiten: la gesta ya está hecha.

En los dos casos la ventana contiene **solo días laborables**.

| Medalla | Alcance | Condición | Nivel |
|---|---|---|---|
| Suertud@ | permanente | resolver en un intento | legendario |
| El día imposible | permanente | resolver en ≤4 un día cuya media del grupo sea ≥5,5 | legendario |
| Superviviente | temporada | resolver en ≤4 tres días de media ≥4,5 | legendario |
| Pleno | temporada | no faltar **ningún día laborable** de la temporada (mínimo 10 días) | raro |
| Verdugo | temporada | ser el mejor del día cinco veces | común |
| Impecable | temporada | ninguna partida fallada, con 10 partidas mínimo | común |
| Fondista | temporada | 15 partidas o más | común |

Los umbrales están calibrados contra el histórico y su rareza medida está en
[el brief](../../../../docs/context/briefs/medallas.md). Un día con menos de cinco jugadores no cuenta
como difícil: su media no es fiable.

**`Pleno` exige lo que dice porque antes no lo hacía.** Los días de la temporada se derivan de los datos, y
mientras el fin de semana contaba, una sola persona jugando un domingo se lo bloqueaba a todo el grupo:
0 de 123 parejas jugador-mes lo lograban. Con días laborables, 6.

#### Scenario: una medalla de temporada se puede ganar dos veces
- GIVEN un jugador que cumple la misma medalla en dos temporadas
- WHEN se calcula su palmarés
- THEN la medalla aparece con dos repeticiones

#### Scenario: una permanente se gana una sola vez
- GIVEN un jugador que resolvió en un intento dos veces
- WHEN se calcula su palmarés
- THEN la medalla aparece una vez

#### Scenario: el umbral se cumple con igualdad
- GIVEN un jugador con exactamente 15 partidas laborables en la temporada
- WHEN se calculan sus medallas
- THEN obtiene Fondista

#### Scenario: quedarse a uno del umbral no otorga
- GIVEN un jugador con 14 partidas laborables en la temporada
- WHEN se calculan sus medallas
- THEN no obtiene Fondista

#### Scenario: el día imposible exige las dos condiciones
- GIVEN un jugador que resuelve en 3 un día cuya media fue 3,0, y otro que resuelve en 6 un día cuya media fue 5,8
- WHEN se calculan sus medallas
- THEN ninguno obtiene El día imposible

#### Scenario: el Pleno no lo bloquea un día de fin de semana
- GIVEN un jugador que juega todos los días laborables de la temporada, y otra persona que además jugó un domingo
- WHEN se calculan las medallas de la temporada
- THEN obtiene Pleno

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py
