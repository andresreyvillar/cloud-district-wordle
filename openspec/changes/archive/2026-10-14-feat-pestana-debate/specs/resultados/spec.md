# Deltas de `resultados` — feat-pestana-debate

## MODIFIED Requirements

### Requirement: El debate vive en tablas aditivas que solo escriben sus funciones

Sin cambios de esquema: la pestaña lee y escribe las mismas tablas y funciones que el apartado de Info. Con la
clave pública se leen y no se escriben; las únicas escrituras son `votar_regla` y `proponer_regla`.

#### Scenario: la clave pública no escribe en las tablas
- **WHEN** se intenta insertar, cambiar, borrar o vaciar las tablas del debate con la clave pública
- **THEN** Postgres lo rechaza

verified-by:
  - tests/slices/debate-de-reglas/test_debate_sql.py
