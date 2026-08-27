# resultados — delta

## MODIFIED Requirements

### Requirement: La categoría de un resultado depende de cuándo se jugó

La figura de una cuadrícula ya no se deriva solo del patrón: se deriva del patrón **y de su jornada**, porque
las reglas de clasificación cambian con el tiempo y los cambios no se aplican hacia atrás.

Consecuencia práctica: dos cuadrículas idénticas jugadas a distinto lado de un cambio de reglas pueden tener
categorías distintas, y eso es correcto — cada partida se juzga con las reglas que estaban en vigor cuando se
jugó, igual que la temporada 0 conserva las suyas.

Consecuencia para quien consuma esto: **el patrón por sí solo no basta** para saber la categoría. Todo cálculo
que clasifique resultados tiene que llevar la jornada consigo; si no la lleva, obtiene el orden histórico, que
es lo correcto para reproducir el pasado y lo incorrecto para una partida de hoy.

#### Scenario: la categoría se deriva del patrón y de la jornada
- **WHEN** se clasifica el resultado de una jornada
- **THEN** se aplican las reglas vigentes en esa jornada, no las últimas
- **AND** un resultado anterior a un cambio de reglas conserva su categoría original
