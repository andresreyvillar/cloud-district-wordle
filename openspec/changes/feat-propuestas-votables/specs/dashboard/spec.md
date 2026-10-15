# Deltas de `dashboard` — feat-propuestas-votables

## MODIFIED Requirements

### Requirement: Info tiene un apartado para debatir las reglas

Las propuestas se publican al enviarlas y cada una se vota a favor o en contra, eligiendo quién eres: un voto
por persona y propuesta, cambiable, con el recuento y los nombres a la vista. Una propuesta rechazada por el dueño
no se ve.

#### Scenario: las propuestas se votan
- **WHEN** alguien elige su nombre y vota una propuesta a favor o en contra
- **THEN** su voto se guarda y la propuesta enseña cuántos y quiénes están a favor y en contra

#### Scenario: una propuesta se publica al momento
- **WHEN** alguien envía una propuesta
- **THEN** se le dice que está publicada y aparece en el debate

verified-by:
  - tests/slices/debate-de-reglas/debate.test.js
