# Deltas de `dashboard` — feat-pestana-debate

## MODIFIED Requirements

### Requirement: Info tiene un apartado para debatir las reglas

El debate vive en su propia pestaña, `/debate`, en el menú. Info conserva un párrafo que lleva a ella, y el
primer enlace que se compartió, `/info#debate-de-reglas`, también.

#### Scenario: el debate tiene su pestaña
- **WHEN** se abre `/debate` o se pulsa la pestaña Debate
- **THEN** se ve el debate sin bajar por la página

#### Scenario: el enlace viejo lleva al debate
- **WHEN** alguien abre `/info#debate-de-reglas`
- **THEN** llega a la pestaña Debate y la barra dice `/debate`

verified-by:
  - tests/slices/debate-de-reglas/debate.test.js
