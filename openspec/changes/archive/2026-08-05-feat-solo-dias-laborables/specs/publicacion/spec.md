# Deltas de `publicacion` — feat-solo-dias-laborables

## MODIFIED Requirements

### Requirement: El resumen anuncia las medallas nuevas de la jornada, no el estado acumulado

El texto que acompaña al resumen lleva una sección con las medallas que alguien ha **ganado en esa
jornada**: las de temporada que no tenía antes y las permanentes conseguidas ese día.

No lleva el estado acumulado del mes. Medido sobre julio, el acumulado produce líneas de diez nombres que
se repetirían idénticas veinte días seguidos, porque las tres medallas comunes las tiene entre el 34% y el
48% del grupo. El estado completo es información de la ficha de jugador, no del mensaje diario.

La sección **solo aparece si hay al menos una medalla nueva**. Una sección vacía ocupa espacio y no dice nada.

**En sábado y domingo nunca hay sección**, porque en un día que no cuenta no se gana nada.

Dos mecanismos independientes, y hacen falta los dos. El cron pasa a **lunes-viernes**, así que en fin de
semana no se publica resumen: sin él, un cron dominical republicaría la jornada del viernes con sus
medallas, porque la jornada se deriva de `max(wordle_id)` y en fin de semana no llegan filas nuevas. Y el
cálculo filtra igualmente, para el caso en que el workflow se dispare a mano (`workflow_dispatch`) o alguien
publique un resultado en sábado.

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

#### Scenario: una jornada de fin de semana no anuncia medallas
- GIVEN una jornada que cae en sábado o domingo, con resultados publicados
- WHEN se compone el texto del resumen
- THEN el texto no incluye sección de medallas, y conserva el saludo y el enlace

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py
