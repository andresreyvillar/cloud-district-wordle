# Deltas de `dashboard` — feat-figuras-de-la-jornada

## ADDED Requirements

### Requirement: La jornada en curso enseña lo que ha dibujado cada uno

La vista `/hoy` muestra, junto a los intentos de cada participante, **el emoji de la figura que dibujó**.

La categoría **llega calculada** en la instantánea. El navegador no interpreta la cuadrícula: portar el
clasificador a JavaScript crearía una segunda verdad que divergiría en la primera recalibración.

Consecuencia declarada del reparto: quien publique **después de la última materialización** aparece con su
puntuación y sin figura. La vista lo dice —llega con la siguiente actualización— en lugar de dejar un hueco
sin explicar.

Una instantánea que no traiga las figuras se pinta como hasta ahora.

#### Scenario: cada participante lleva su figura
- GIVEN una jornada cuyas figuras están publicadas
- WHEN se pinta la vista de hoy
- THEN cada participante que dibujó aparece con su emoji

#### Scenario: quien llegó tarde no tiene figura, y se explica
- GIVEN un participante cuyo resultado es posterior a la última materialización
- WHEN se pinta la vista
- THEN aparece sin figura y la vista explica que llega con la siguiente actualización

#### Scenario: el emoji sale de la instantánea
- GIVEN una instantánea cuyo catálogo asigna otro emoji a una categoría
- WHEN se pinta la vista de hoy
- THEN se usa el emoji publicado, no uno fijo en la web

#### Scenario: sin figuras publicadas la vista no cambia
- GIVEN una instantánea sin las figuras de la jornada
- WHEN se pinta la vista de hoy
- THEN se pinta igual que antes, sin emojis y sin errores

verified-by:
  - tests/slices/figuras-de-la-jornada/hoy.test.js
