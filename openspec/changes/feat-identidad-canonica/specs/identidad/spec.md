# Deltas de `identidad` — feat-identidad-canonica

## ADDED Requirements

### Requirement: El identificador canónico de un jugador es su ID de Slack

La identidad de un jugador es el identificador que Slack le asigna, no el nombre que muestra. El
identificador no cambia nunca; el nombre sí, y cambia sin avisar.

La columna `slack_user_id` de `wordle_results` contiene ese identificador. Un valor que no tiene forma de
identificador de Slack indica una fila pendiente de canonizar, no una identidad alternativa.

```yaml
checks:
  - type: column
    table: wordle_results
    column: slack_user_id
    describe: contiene identificadores de Slack, no nombres mostrados
```

#### Scenario: una fila con nombre se canoniza
- GIVEN una fila cuya identidad es un nombre mostrado que corresponde a una persona del workspace
- WHEN se ejecuta la canonización
- THEN la fila guarda el identificador de Slack de esa persona

#### Scenario: una fila ya canónica no se modifica
- GIVEN una fila cuya identidad ya es un identificador de Slack
- WHEN se ejecuta la canonización
- THEN la fila no cambia

verified-by:
  - tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py

### Requirement: Un cambio de nombre no crea un jugador nuevo

Dos filas que pertenecen a la misma persona son del mismo jugador aunque su nombre mostrado difiera. Si
el nombre cambió entre dos partidas, las dos siguen siendo del mismo jugador.

Cuando dos identidades resuelven al mismo identificador y coinciden en puzzle y puntuación, son la misma
partida registrada dos veces y queda una sola fila.

#### Scenario: el mismo puzzle registrado bajo dos nombres
- GIVEN dos filas del mismo puzzle con la misma puntuación, cuyas identidades resuelven al mismo identificador
- WHEN se ejecuta la canonización
- THEN queda una sola fila para ese jugador y ese puzzle

#### Scenario: dos partidas distintas del mismo jugador no se fusionan
- GIVEN dos filas del mismo jugador con puzzles distintos
- WHEN se ejecuta la canonización
- THEN las dos filas se conservan

verified-by:
  - tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py

### Requirement: El nombre mostrado es un atributo, no la identidad

`player_name` guarda el nombre con el que se muestra al jugador. La canonización **no lo toca**: es la
columna que lee la web publicada, y cambiarla rompería la v1
([ADR 0005](../../../../decisions/0005-hosting-y-convivencia-v1-v2.md)).

Un nombre que no corresponde a ninguna persona del workspace no invalida la fila: la deja pendiente y se
declara. Un jugador que se marchó de la empresa jugó de verdad.

#### Scenario: el nombre mostrado sobrevive a la canonización
- GIVEN una fila con su nombre mostrado
- WHEN la canonización le escribe el identificador
- THEN el nombre mostrado conserva el valor que tenía

#### Scenario: un nombre desconocido se declara en lugar de borrarse
- GIVEN una fila cuyo nombre no corresponde a nadie del workspace
- WHEN se ejecuta la canonización
- THEN la fila conserva su identidad y se cuenta como no resuelta

verified-by:
  - tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py
