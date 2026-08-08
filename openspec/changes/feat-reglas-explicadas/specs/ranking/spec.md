# Deltas de `ranking` — feat-reglas-explicadas

## ADDED Requirements

### Requirement: Un parámetro publicado es el mismo que usa el cálculo

Cuando una regla se enuncia con un número —cinco jugadores de muestra mínima, quince partidas para Fondista,
margen de 0,5— ese número **se lee de la constante que el cálculo usa**, nunca de una copia.

Es lo único que impide que la página de reglas mienta: un umbral recalibrado en el código y no en el texto
produciría una explicación falsa en la que el grupo confiaría.

```yaml
checks:
  - type: cli-command
    describe: cada parámetro del catálogo coincide con la constante que documenta
```

#### Scenario: el parámetro mostrado es el del cálculo
- GIVEN una regla con un umbral
- WHEN se compara el valor publicado con la constante que usa el cálculo
- THEN son el mismo valor

#### Scenario: recalibrar un umbral cambia lo publicado
- GIVEN un umbral que cambia en el código
- WHEN se vuelve a materializar
- THEN la regla publicada muestra el valor nuevo sin tocar su texto

verified-by:
  - tests/slices/reglas-explicadas/test_reglas.py

### Requirement: Las reglas viajan con la temporada

La instantánea de una temporada incluye las reglas con las que se calculó, así que una temporada cerrada
conserva las suyas aunque las de hoy hayan cambiado.

#### Scenario: una temporada cerrada conserva sus reglas
- GIVEN una temporada materializada con unos parámetros
- WHEN los parámetros cambian y se materializa otra temporada
- THEN la instantánea de la primera sigue mostrando los parámetros con los que se calculó

verified-by:
  - tests/slices/reglas-explicadas/test_reglas.py
