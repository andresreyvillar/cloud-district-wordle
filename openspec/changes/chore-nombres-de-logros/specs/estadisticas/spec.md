# Deltas de `estadisticas` — chore-nombres-de-logros

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
| **Metrónom@** | temporada | no faltar **ningún día laborable** de la temporada (mínimo 10 días) | raro |
| Verdugo | temporada | ser el mejor del día cinco veces | común |
| Impecable | temporada | ninguna partida fallada, con 10 partidas mínimo | común |
| Fondista | temporada | 15 partidas o más | común |

`Metrónom@` se llamaba `Pleno`. El nombre estaba declarado abierto en
[el brief](../../../../docs/context/briefs/medallas.md) y se adopta el del
[diseño de la liga arcade](../../../../docs/context/sources/2026-08-05-diseno-liga-arcade.md). **La regla no
cambia.**

`Impecable` **no** pasa a llamarse `Superviviente` aunque el diseño lo proponga: ese nombre ya está en la
regla de los tres días duros, y dos medallas distintas no pueden llamarse igual.

#### Scenario: el umbral se cumple con igualdad
- GIVEN un jugador con exactamente 15 partidas laborables en la temporada
- WHEN se calculan sus medallas
- THEN obtiene Fondista

#### Scenario: no faltar ningún día laborable otorga Metrónom@
- GIVEN un jugador que juega todos los días laborables de una temporada de al menos diez días
- WHEN se calculan las medallas de la temporada
- THEN obtiene Metrónom@

#### Scenario: dos medallas nunca comparten nombre
- GIVEN el catálogo de medallas
- WHEN se listan sus nombres
- THEN no hay dos iguales

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py
