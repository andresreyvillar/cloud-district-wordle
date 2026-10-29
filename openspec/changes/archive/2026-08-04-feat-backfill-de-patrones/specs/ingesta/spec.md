# Deltas de `ingesta` — feat-backfill-de-patrones

## ADDED Requirements

### Requirement: El recorrido del histórico agota todas las páginas

La lectura del canal para recuperar patrones antiguos continúa mientras la respuesta indique que queda
histórico. No se detiene en la primera página: el histórico completo son más de mil quinientos
resultados y una página devuelve como máximo unos cientos de mensajes.

```yaml
checks:
  - type: slack-api
    method: conversations.history
    describe: el recorrido sigue el cursor de paginación hasta agotarlo
```

#### Scenario: el histórico ocupa varias páginas
- GIVEN un histórico que la API devuelve en tres páginas
- WHEN el comando recorre el canal
- THEN procesa los mensajes de las tres páginas

#### Scenario: sin más histórico el recorrido termina
- GIVEN una respuesta sin cursor de continuación
- WHEN el comando la recibe
- THEN termina el recorrido sin pedir más páginas

verified-by:
  - tests/slices/backfill-de-patrones/test_backfill_de_patrones.py

### Requirement: La extracción del patrón antiguo usa las mismas reglas que la ingesta

El patrón que se recupera del histórico es idéntico al que la ingesta habría producido con ese mismo
mensaje: mismas celdas reconocidas, misma normalización del tema claro y oscuro, mismo formato de
filas. No hay una segunda implementación de la extracción.

#### Scenario: un mensaje antiguo produce el mismo patrón que produciría hoy
- GIVEN un mensaje del histórico con su cuadrícula
- WHEN el backfill extrae su patrón
- THEN el resultado es igual al que produce la extracción de la ingesta para ese texto

verified-by:
  - tests/slices/backfill-de-patrones/test_backfill_de_patrones.py

### Requirement: El backfill no registra resultados

El recorrido puede encontrar resultados publicados en el canal que nunca llegaron a la tabla. El
comando **no los inserta**: informa de cuántos ha visto y sigue. Recuperar resultados perdidos es un
comportamiento distinto, con sus propias causas (mensajes en hilos, ventana de ingesta corta) y su
propio slice.

#### Scenario: un resultado del canal que no está en la tabla
- GIVEN un mensaje de resultado sin fila correspondiente
- WHEN el comando lo procesa
- THEN no se crea ninguna fila y el mensaje consta en el recuento de resultados sin registrar

verified-by:
  - tests/slices/backfill-de-patrones/test_backfill_de_patrones.py
