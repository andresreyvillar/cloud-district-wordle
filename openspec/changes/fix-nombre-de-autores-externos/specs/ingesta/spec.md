# Deltas de `ingesta` — fix-nombre-de-autores-externos

## ADDED Requirements

### Requirement: Un autor que no está en el directorio se nombra por su perfil

El extractor completa el directorio de `users.list` con los autores de la ventana que no aparecen en él
—los usuarios externos de Slack Connect—: su nombre sale del `user_profile` del mensaje y, si no viene, de
`users.info`, una consulta por autor y ejecución. Solo si Slack no da nombre se emite el identificador.

#### Scenario: un autor externo se nombra por su perfil
- GIVEN un resultado de alguien que no está en `users.list`, con su perfil en el mensaje
- WHEN se extrae la ventana
- THEN la línea lleva el nombre de su perfil y no su identificador
