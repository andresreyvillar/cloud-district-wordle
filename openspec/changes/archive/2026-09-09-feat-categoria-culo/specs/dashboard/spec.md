# dashboard — delta

## MODIFIED Requirements

### Requirement: La página de reglas enumera todas las categorías del álbum

La regla del álbum dice cuántas categorías hay y las nombra con su emoji, y la de ponderación dice qué vale
cada una. Añadir una categoría sin tocar este texto dejaría al grupo leyendo que hay cuatro cuando hay cinco.

#### Scenario: la página de reglas enumera todas las categorías
- **WHEN** se pinta la regla del álbum
- **THEN** nombra todas las categorías vigentes con su emoji y su valor

## ADDED Requirements

### Requirement: La pestaña de temporada explica qué es cada dibujo

Debajo de los logros hay un glosario con cada categoría del álbum: su emoji, qué forma la define, cuántos
puntos vale y cuántos han salido en el mes.

**Sale del catálogo publicado en la instantánea**, no de una lista escrita en la vista, así que una categoría
nueva en el pipeline aparece sola. Las descripciones sí viven en la vista, porque son texto de interfaz y no
dato del cálculo; una categoría sin descripción sale con su nombre, su valor y su recuento en lugar de
desaparecer, porque esa es la información que hay.

Sin catálogo el glosario no se pinta, en lugar de pintarse vacío.

#### Scenario: el glosario explica cada dibujo
- **WHEN** se pinta la pestaña de temporada
- **THEN** aparece cada categoría del catálogo con su emoji, sus puntos y cuántos han salido
- **AND** una categoría sin descripción sale con lo que se sepa de ella
- **AND** sin catálogo no se pinta nada
