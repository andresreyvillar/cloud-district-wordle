# Deltas de `publicacion` — feat-medallas-resumen

## ADDED Requirements

### Requirement: El resumen anuncia las medallas nuevas de la jornada, no el estado acumulado

El texto que acompaña al resumen lleva una sección con las medallas que alguien ha **ganado en esa
jornada**: las de temporada que no tenía antes y las permanentes conseguidas ese día.

No lleva el estado acumulado del mes. Medido sobre julio, el acumulado produce líneas de diez nombres que
se repetirían idénticas veinte días seguidos, porque las tres medallas comunes las tiene entre el 34% y el
48% del grupo. El estado completo es información de la ficha de jugador, no del mensaje diario.

La sección **solo aparece si hay al menos una medalla nueva**. Una sección vacía ocupa espacio y no dice nada.

```yaml
checks:
  - type: slack-api
    method: files_upload_v2
    describe: el initial_comment incluye la sección de medallas cuando hay alguna
```

#### Scenario: una medalla ganada hoy se anuncia
- GIVEN un jugador que alcanza el umbral de una medalla en la jornada que se publica
- WHEN se compone el texto del resumen
- THEN el texto contiene el nombre de la medalla y del jugador

#### Scenario: una medalla que ya tenía no se repite
- GIVEN un jugador que alcanzó el umbral en una jornada anterior
- WHEN se compone el texto de hoy
- THEN el texto no menciona esa medalla

#### Scenario: sin novedades, no hay sección
- GIVEN una jornada en la que nadie gana ninguna medalla nueva
- WHEN se compone el texto del resumen
- THEN el texto no menciona las medallas

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py

### Requirement: Una medalla permanente se anuncia una sola vez

Una medalla permanente se anuncia en el resumen de la jornada en la que se consigue, y no vuelve a
anunciarse. El resto de jornadas el mensaje no la repite.

#### Scenario: la gesta del día se anuncia
- GIVEN un jugador que resuelve en un intento en la jornada que se publica
- WHEN se compone el texto
- THEN el mensaje anuncia su medalla permanente

#### Scenario: una gesta antigua no se repite
- GIVEN un jugador que resolvió en un intento en una jornada anterior
- WHEN se compone el texto de hoy
- THEN el mensaje no vuelve a anunciarla

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py

### Requirement: El resumen conserva lo que ya publicaba

Añadir las medallas no altera el resto del mensaje: la captura se sigue adjuntando y el enlace a la web
sigue estando. La sección se añade, no sustituye.

#### Scenario: el enlace sigue en el mensaje
- GIVEN cualquier composición del texto del resumen
- WHEN se compone
- THEN el texto sigue conteniendo el enlace a la web

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py
