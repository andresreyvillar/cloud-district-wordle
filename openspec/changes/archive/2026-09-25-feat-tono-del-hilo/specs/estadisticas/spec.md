# Deltas de `estadisticas` — feat-tono-del-hilo

## MODIFIED Requirements

### Requirement: El recuento de respuestas no es, por sí solo, un reconocimiento

Las respuestas que cuelgan del mensaje de un jugador se cuentan igual que antes, y siguen eligiendo el hilo
del día. Lo que cambia es cómo se **lee** esa cifra: un recuento alto deja de valer por sí mismo como mérito.

Medido sobre la jornada que motivó el cambio: el resultado más comentado acumuló 26 respuestas y **cero
reacciones**, mientras el resto del día repartía 46 reacciones y ni un solo hilo. Las dos señales apuntaban en
direcciones opuestas y la mención solo miraba una, así que el mensaje coronó como triunfador a quien el grupo
estaba acusando.

Cuando la clasificación del hilo dice que aquello fue una acusación, a quien lo abrió no se le nombra como si
el recuento fuera un premio.

#### Scenario: un hilo de acusaciones no corona a nadie
- GIVEN el hilo más comentado de la jornada, clasificado como acusación
- WHEN se componen las menciones del mensaje
- THEN a quien lo abrió no se le nombra como si el recuento de respuestas fuera un reconocimiento

#### Scenario: un hilo sin acusación mantiene la mención de siempre
- GIVEN un hilo comentado y no clasificado como acusación
- WHEN se componen las menciones
- THEN la mención del hilo es la que había

verified-by:
  - tests/slices/voz-de-la-jornada/test_tono.py
