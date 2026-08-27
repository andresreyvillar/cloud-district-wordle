# ranking — delta

## ADDED Requirements

### Requirement: El orden de las reglas de figura está versionado por jornada

La geometría se comprueba antes que el loro y, si acierta, no se avanza: una pirámide con un amarillo suelto
es un geométrico y no un loro.

El cambio **no es retroactivo**. Rige a partir de una jornada determinada, inclusive, y las cuadrículas
anteriores conservan la categoría que tenían cuando se jugaron — igual que la temporada 0 se rige por las
reglas que estaban en vigor entonces.

El motivo es que el geométrico puntúa más que el loro: aplicarlo hacia atrás subiría la puntuación de quien
tenga esas partidas ya jugadas y ya comentadas, reescribiendo un álbum que el grupo ya ha visto. Medido, el
reorden movería 42 de las 1.706 cuadrículas del histórico.

Clasificar un patrón **sin jornada** usa el orden histórico, porque las herramientas que lo hacen fuera de
contexto —la calibración contra el etiquetado humano— se hicieron con las reglas de entonces.

#### Scenario: la geometría se decide antes que el loro
- **WHEN** se clasifica una cuadrícula de una jornada a partir de la que rige el orden nuevo
- **THEN** si es geométrica se devuelve geométrico sin comprobar el loro

#### Scenario: el cambio de orden no es retroactivo
- **WHEN** se clasifica una cuadrícula anterior a esa jornada
- **THEN** conserva la categoría del orden antiguo
- **AND** clasificar sin jornada también usa el orden antiguo
