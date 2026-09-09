# dashboard — delta

## MODIFIED Requirements

### Requirement: La regla del Coleccionista no nombra un número de categorías

El texto que el grupo lee dice **qué** hay que coleccionar y no **cuántas** cosas son: «una de cada figura que
haya salido en la temporada». Un número escrito a mano se queda desfasado cada vez que se añade una categoría,
y entonces la página explica una regla que el sistema ya no aplica.

#### Scenario: la regla del coleccionista no nombra un número
- **WHEN** se pinta la tarjeta del Coleccionista
- **THEN** su regla describe la condición sin fijar cuántas categorías hay
