# Deltas de `ingesta` — feat-ingesta-por-id

## ADDED Requirements

### Requirement: La ingesta transporta el identificador del autor, no su nombre

La línea que el extractor pasa al cargador lleva **el identificador de Slack del autor** y, aparte, su
nombre visible. El identificador es lo que identifica; el nombre es solo para mostrar.

Los dos scripts se ejecutan encadenados en la misma invocación, así que el formato de la línea es un
contrato interno y cambia de golpe: no hace falta ventana de compatibilidad.

```yaml
checks:
  - type: cli-command
    describe: extract_slack.py emite el identificador del autor en la línea de encabezado
```

#### Scenario: el encabezado lleva identificador y nombre
- GIVEN un mensaje de resultado de una persona del workspace
- WHEN el extractor lo emite
- THEN la línea contiene su identificador de Slack y su nombre visible, en campos distintos

#### Scenario: la cuadrícula se sigue asociando a su resultado
- GIVEN un mensaje con su resultado y las filas de emojis
- WHEN se procesa el lote con el formato nuevo
- THEN el patrón capturado es el mismo que con el formato anterior

#### Scenario: un mensaje sin autor no se guarda
- GIVEN una línea de resultado sin autor
- WHEN se procesa el lote
- THEN no se escribe ninguna fila para ese resultado y el recuento lo declara

verified-by:
  - tests/slices/ingesta-por-id-de-slack/test_ingesta_por_id.py
