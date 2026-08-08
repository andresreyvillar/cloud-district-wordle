# Deltas de `estadisticas` — feat-comentarios-por-la-hora

## MODIFIED Requirements

### Requirement: Los hechos notables de una jornada se detectan, no se narran

Una jornada produce **hechos**: quién resolvió muy rápido un día duro, quién quedó muy por encima o por
debajo de la media, quién no apareció el día difícil, y —esto es lo nuevo— **cuándo** publicó cada uno.

Un hecho sigue siendo un dato, no una frase.

Se añaden tres, y los tres por su rareza medida sobre las 186 jornadas que cuentan:

| Hecho | Disparador | Frecuencia |
|---|---|---|
| acertar a la primera | 1 intento | 0,01 |
| llegar el último **y** con nota muy por encima de la media | último, 4h+ de hueco, tarde, y ventaja | 0,06 |
| llegar el último | último, 4h+ de hueco, y con el día avanzado | 0,24 |

La hora **solo se usa si es utilizable**: si la marca de registro cae el mismo día que el puzzle. Las filas
del backfill se insertaron todas de golpe en otra fecha.

Y la notabilidad ordena por esa frecuencia: cuando alguien dispara dos hechos, sale por el más raro.

#### Scenario: la hora entra en la detección
- GIVEN una jornada con marcas de registro utilizables
- WHEN se detectan los hechos
- THEN quien publica muy por detrás del resto produce un hecho

#### Scenario: una hora no utilizable no produce hechos
- GIVEN resultados cuya marca de registro es de otro día
- WHEN se detectan los hechos
- THEN ninguno depende de la hora

#### Scenario: el más raro gana cuando coinciden
- GIVEN alguien que acierta a la primera en un día duro, que dispara dos hechos
- WHEN se detectan los hechos
- THEN sale por el más raro de los dos

verified-by:
  - tests/slices/comentarios-de-la-jornada/test_comentarios.py
