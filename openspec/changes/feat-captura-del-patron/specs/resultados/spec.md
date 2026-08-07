# Deltas de `resultados` — feat-captura-del-patron

## ADDED Requirements

### Requirement: La tabla almacena el patrón de la cuadrícula

`wordle_results` tiene una columna `pattern` de texto, opcional. Contiene el camino de emojis del
resultado; vacía cuando el mensaje no traía cuadrícula o cuando la fila es anterior al backfill.

La columna es **aditiva**: no altera ni sustituye a `player_name`, `wordle_id`, `score`, `date` ni
`raw_text`, que son las que lee la v1 de la web
([ADR 0005](../../../../decisions/0005-hosting-y-convivencia-v1-v2.md)).

```yaml
checks:
  - type: column
    table: wordle_results
    column: pattern
    nullable: true
```

#### Scenario: una fila sin cuadrícula sigue siendo válida
- GIVEN un resultado cuyo mensaje no incluye cuadrícula
- WHEN se registra en la tabla
- THEN la fila existe con su puntuación y su fecha, y `pattern` queda vacía

#### Scenario: la v1 sigue funcionando con la columna nueva
- GIVEN la columna `pattern` añadida a la tabla
- WHEN la web v1 consulta los resultados
- THEN recibe las columnas que ya leía y funciona sin cambios

verified-by:
  - tests/slices/captura-del-patron/test_captura_del_patron.py

### Requirement: El patrón se almacena en forma normalizada y reversible

El patrón se guarda como una cadena de filas separadas por `/`, cada fila con exactamente cinco
caracteres: `G` acierto en posición, `Y` letra presente en otra posición, `.` letra ausente.

Ejemplo: un resultado en tres intentos se almacena como `...YY/.G.YY/GGGGG`.

El formato es **reversible**: a partir de la cadena se reconstruye la cuadrícula tal como se publicó,
salvo el tema claro u oscuro de quien la publicó, que es información de presentación y no de juego.
Guardar el patrón y no una categoría ya calculada es deliberado: el clasificador de figuras se
recalibrará, y un veredicto persistido haría irrecuperable el histórico en cada ajuste.

```yaml
checks:
  # Era un `config-key` sin `file:`, así que no verificaba nada — lo cazó el gate `checks-probe` el
  # 2026-08-07. Y el tipo era el equivocado: no es una clave de configuración, es una constante de Python.
  - type: regex
    file: tools/patterns.py
    pattern: '^PATTERN_ROW_SEPARATOR = "/"$'
    describe: el separador de filas del patrón es la barra
```

#### Scenario: el patrón conserva el orden de los intentos
- GIVEN una cuadrícula de cuatro filas
- WHEN se almacena el patrón
- THEN la cadena tiene cuatro grupos separados por `/` en el mismo orden que el mensaje

#### Scenario: dos caminos idénticos con temas distintos producen el mismo patrón
- GIVEN dos resultados con el mismo camino, uno publicado en tema claro y otro en tema oscuro
- WHEN se almacenan
- THEN las dos cadenas son idénticas

verified-by:
  - tests/slices/captura-del-patron/test_captura_del_patron.py

### Requirement: El patrón no participa en la identidad de la fila

La unicidad de un resultado sigue siendo la pareja jugador–puzzle. El patrón es un atributo: cambiarlo
no crea una fila nueva, y una reejecución de la ingesta sobre el mismo mensaje deja una sola fila con un
solo patrón.

La unicidad la garantiza un **índice único**, no una constraint — verificado contra el esquema:
`idx_slack_user_wordle_unique` sobre `(slack_user_id, wordle_id)`. Es lo que hace funcionar el
`on_conflict` del upsert. La clave primaria es `id` (uuid).

El **doble que imita ese índice** no vive aquí: los tests de este slice solo parsean patrones y no escriben
en ninguna tabla. Vive en los slices que escriben —`ingesta-por-id-de-slack` e
`identidad-canonica-de-jugador`—, y ahí es donde el `checks:` de tipo `index` está declarado. Lo que este
slice puede demostrar por su cuenta es que el upsert usa esa pareja como clave de conflicto, y eso es lo que
declara:

```yaml
# Antes había aquí un `checks: - type: index`, y el gate `checks-probe` lo tumbó el 2026-08-07 con razón:
# reclamaba un doble que impusiera el índice en un tests_root donde no se escribe nada. La invariante es
# cierta, pero este slice no es quien la demuestra.
checks:
  - type: regex
    file: tools/add_results.py
    pattern: '^CLAVE_DE_CONFLICTO = \("slack_user_id", "wordle_id"\)$'
    describe: el upsert usa la pareja jugador-puzzle como clave de conflicto
```

**Límite conocido de esa unicidad:** `slack_user_id` es nullable, y en Postgres dos `NULL` no colisionan
en un índice único. Dos filas con `slack_user_id` nulo y el mismo puzzle no violarían el índice. Hoy no
hay ninguna fila con ese valor nulo (verificado: 0 de 1532), así que el riesgo es teórico; deja de serlo
el día que la resolución de identidad devuelva nulo en lugar de un nombre.

#### Scenario: reprocesar un mensaje no duplica la fila
- GIVEN un resultado ya registrado con su patrón
- WHEN la ingesta procesa el mismo mensaje otra vez
- THEN sigue existiendo una sola fila para ese jugador y ese puzzle

verified-by:
  - tests/slices/captura-del-patron/test_captura_del_patron.py
