# Deltas de `dashboard` — feat-medallas-de-figuras

## ADDED Requirements

### Requirement: Las medallas de figura se ven con las demás

La vista de temporada muestra las doce medallas del catálogo, no siete, y cada una con su icono. La ficha de
jugador las pinta en su palmarés igual que las otras.

El icono sale del mismo sprite. **`Fontaner@` se renombra a `Abstract@` también en el sprite**: la categoría
dejó de llamarse `caca` y el chiste de fontanero se quedó sin referente, así que un símbolo con el nombre
viejo era la última copia de un vocabulario ya cambiado.

#### Scenario: las doce medallas aparecen en la temporada
- GIVEN una temporada calculada
- WHEN se pinta el bloque de logros
- THEN aparecen también las cinco de figuras, con su nombre y su regla

#### Scenario: cada medalla de figura tiene su icono
- GIVEN las cinco medallas de figuras
- WHEN se pintan
- THEN cada una referencia un símbolo que existe en el sprite

verified-by:
  - tests/slices/medallas-de-figuras/medallas.test.js
