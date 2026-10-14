# Deltas de `dashboard` — feat-debate-de-reglas

## ADDED Requirements

### Requirement: Info tiene un apartado para debatir las reglas

Después de las reglas vigentes, Info enseña las votaciones —cada opción con sus votos y quién la votó— y las
propuestas aprobadas con su autor, y deja votar y proponer eligiendo quién eres con el selector del juego. Sin
nombre no se envía nada. Una votación cerrada enseña su resultado sin botones. Todo lo que escriben los jugadores
se pinta escapado. Si la base de datos no responde, el apartado lo dice y el resto de Info sigue.

#### Scenario: se vota eligiendo tu nombre
- GIVEN una votación abierta
- WHEN alguien elige su nombre y vota una opción
- THEN su voto se guarda y el recuento lo cuenta

#### Scenario: sin nombre no se vota
- WHEN alguien vota sin haber elegido su nombre
- THEN no se envía nada y se le pide que elija quién es

verified-by:
  - tests/slices/debate-de-reglas/debate.test.js
