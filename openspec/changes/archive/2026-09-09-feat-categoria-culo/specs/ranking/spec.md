# ranking — delta

## ADDED Requirements

### Requirement: La forma de las tres filas de abajo tiene su propia categoría

Una cuadrícula cuyas tres últimas filas dibujan un verde central entre dos huecos, sobre `G.G.G` y sobre el
suelo, se clasifica en una categoría propia con su emoji, y puntúa como el geométrico.

Se reconoce **por el patrón y no por los rasgos**, porque no es una propiedad agregada —cuántos verdes, cuánta
densidad— sino una forma concreta en un sitio concreto. Los extremos de la fila de arriba son libres: lo que da
la silueta es el verde central entre sus dos huecos.

Se comprueba **después del espejo**, así que una cuadrícula que sea las dos cosas se queda en geométrico. Eso
deja la categoría en minoría a propósito: de las cinco cuadrículas del histórico que dibujan la forma, dos son
espejos.

#### Scenario: el culo es su propia categoría
- **WHEN** las tres últimas filas dibujan la forma
- **THEN** se clasifica en su categoría, cuenta como figura reconocible y puntúa como el geométrico
- **AND** los extremos de la fila de arriba no cambian el veredicto
- **AND** la fila del medio y el suelo sí se exigen

#### Scenario: el espejo gana al culo
- **WHEN** una cuadrícula es a la vez espejo reconocible y dibuja la forma
- **THEN** se clasifica como geométrico
