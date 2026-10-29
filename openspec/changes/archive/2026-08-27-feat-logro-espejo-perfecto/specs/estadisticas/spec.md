# estadisticas — delta

## ADDED Requirements

### Requirement: El espejo perfecto es un logro permanente

Una cuadrícula simétrica fila a fila y con cuerpo suficiente concede un logro permanente, que se anuncia el
día que ocurre.

El umbral de cuerpo es lo que hace el logro. Medido sobre 1.706 cuadrículas: sin umbral hay 19 espejos y los
tendría el 43% del grupo, porque siete son de una sola fila y simétricos por accidente; con tres filas quedan
siete espejos de siete personas distintas, uno cada cinco meses.

Se concede mirando **el rasgo de simetría y no la categoría**: en la clasificación el espejo se consulta en
último lugar, así que una cuadrícula simétrica puede acabar etiquetada como flor, y el logro se perdería justo
en el mejor dibujo.

#### Scenario: el espejo perfecto tiene su logro
- **WHEN** alguien deja una cuadrícula simétrica fila a fila con cuerpo suficiente
- **THEN** gana el logro y se anuncia ese día
- **AND** una cuadrícula simétrica de una sola fila no lo gana
- **AND** una cuadrícula alta pero asimétrica tampoco

#### Scenario: el logro mira el rasgo y no la categoría
- **WHEN** la cuadrícula simétrica está clasificada como flor o como loro
- **THEN** el logro se concede igualmente
