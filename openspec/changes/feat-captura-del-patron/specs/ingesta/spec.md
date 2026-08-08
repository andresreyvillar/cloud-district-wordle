# Deltas de `ingesta` — feat-captura-del-patron

## ADDED Requirements

### Requirement: La cuadrícula del mensaje se extrae como patrón

Al procesar un mensaje de resultado, la ingesta extrae las filas de cuadrícula que lo acompañan. Una
fila de cuadrícula es una línea con **exactamente cinco** celdas de cuadrado y ninguna otra cosa; las
líneas que no cumplen eso no forman parte del patrón.

Las celdas se reconocen por su nombre en el mensaje del canal: verde y amarillo tienen un nombre cada
uno, y la celda de letra ausente tiene **dos** nombres posibles según el tema de quien publica. Los dos
se normalizan al mismo símbolo.

```yaml
checks:
  # Le faltaban `file:` y `pattern:`, así que el probe no podía decidir: lo cazó `checks-probe`.
  - type: regex
    file: tools/patterns.py
    pattern: 'CELDA_RE = re\.compile'
    describe: la fila de cuadrícula exige cinco celdas exactas
```

#### Scenario: se extraen todas las filas del mensaje
- GIVEN un mensaje de resultado con cinco filas de cuadrícula
- WHEN la ingesta lo procesa
- THEN el patrón resultante tiene cinco filas

#### Scenario: una línea con cuatro celdas no es una fila
- GIVEN un mensaje cuya cuadrícula incluye una línea con cuatro celdas
- WHEN la ingesta lo procesa
- THEN esa línea no aparece en el patrón

verified-by:
  - tests/slices/captura-del-patron/test_captura_del_patron.py

### Requirement: El patrón pertenece al resultado que lo precede

Las filas de cuadrícula llegan al parser como líneas independientes, después de la línea que declara el
resultado. Cada bloque de filas se asocia al último resultado reconocido; un resultado nuevo cierra el
bloque anterior.

#### Scenario: dos resultados seguidos no mezclan sus cuadrículas
- GIVEN dos mensajes de resultado consecutivos, cada uno con su cuadrícula
- WHEN la ingesta los procesa
- THEN cada fila queda con el patrón de su propio mensaje

#### Scenario: los emojis de una conversación no producen patrón
- GIVEN un mensaje de conversación con celdas de cuadrado y ningún resultado previo en el lote
- WHEN la ingesta lo procesa
- THEN no se almacena ningún patrón

verified-by:
  - tests/slices/captura-del-patron/test_captura_del_patron.py

### Requirement: La ausencia de cuadrícula no impide registrar el resultado

El patrón es información añadida. Si un mensaje de resultado no trae cuadrícula, o sus líneas no son
reconocibles, el resultado se registra igual con su puntuación y su fecha.

#### Scenario: resultado sin cuadrícula
- GIVEN un mensaje que solo contiene la línea del resultado
- WHEN la ingesta lo procesa
- THEN el resultado queda registrado y sin patrón

#### Scenario: un fallo también conserva su patrón
- GIVEN un resultado de fallo, cuya cuadrícula no termina en una fila de aciertos
- WHEN la ingesta lo procesa
- THEN el patrón se almacena con todas las filas del mensaje

verified-by:
  - tests/slices/captura-del-patron/test_captura_del_patron.py
