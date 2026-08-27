# ranking — delta

## MODIFIED Requirements

### Requirement: El espejo reconocible gana a la flor desde el corte de reglas

A partir del corte, una cuadrícula que es un espejo reconocible se clasifica como geométrica **antes** de
comprobar la flor: un palíndromo perfecto es más difícil que unos pétalos.

Antes del corte se conserva el orden histórico, en el que el espejo se consulta en último lugar y por tanto
solo asciende abstractos. Esa invariante existía para no robarle la figura a flores ya jugadas, y el corte la
protege mejor de lo que la protegía el orden.

Un espejo **reconocible** exige un mínimo de filas de cuerpo, y es **el mismo mínimo que pide el logro**: con
umbrales distintos, un espejo de dos filas —simetría por casualidad— le quitaba la categoría a una flor
legítima. El predicado vive en un solo sitio.

#### Scenario: desde el corte el espejo gana a la flor
- **WHEN** una cuadrícula a partir del corte es un espejo reconocible y además cumple la regla de la flor
- **THEN** se clasifica como geométrica
- **AND** la misma cuadrícula antes del corte sigue siendo flor

#### Scenario: el espejo de una o dos filas no cuenta
- **WHEN** una cuadrícula simétrica tiene el cuerpo por debajo del mínimo
- **THEN** no se le reconoce el espejo, ni para la categoría ni para el logro
