# dashboard — delta

## MODIFIED Requirements

### Requirement: La página de reglas enumera todas las categorías del álbum

La regla del álbum dice cuántas categorías hay y las nombra con su emoji, y la de ponderación dice qué vale
cada una. Las dos se escriben a partir del catálogo real, no de una lista fija: añadir una categoría sin tocar
este texto dejaría al grupo leyendo que hay cuatro cuando hay cinco.

Se explica además **por qué** la categoría más rara no vale más que el geométrico, porque es la clase de cosa
que el grupo pregunta.

#### Scenario: la página de reglas enumera todas las categorías
- **WHEN** se pinta la regla del álbum
- **THEN** nombra todas las categorías vigentes con su emoji y su valor
