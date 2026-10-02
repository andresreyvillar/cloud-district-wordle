# Deltas de `identidad` — fix-nombre-de-autores-externos

## ADDED Requirements

### Requirement: Un autor externo se identifica por su id de Slack, como cualquier otro

Que un autor no esté en el directorio del workspace no cambia su identidad: su fila guarda su id de Slack
en `slack_user_id`. Completar el directorio solo le da nombre; no lo une ni lo separa de nadie.

#### Scenario: el autor externo conserva su id como identidad
- GIVEN un resultado de un usuario externo de Slack Connect
- WHEN se extrae y se guarda
- THEN su identidad es su id de Slack, y su nombre el de su perfil

verified-by:
  - tests/slices/ingesta-por-id-de-slack/test_ingesta_por_id.py
