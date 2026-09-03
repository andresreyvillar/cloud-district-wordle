# ranking — delta

## MODIFIED Requirements

### Requirement: Reconocer un espejo y premiarlo piden cuerpos distintos

Una cuadrícula simétrica de **dos filas de cuerpo** se clasifica como geométrica, pero **no** se lleva el logro
del espejo perfecto, que exige más.

Son dos decisiones separadas: la categoría dice «esto es un espejo» y el logro dice «esto casi no pasa nunca».
Con el umbral del logro bajado a dos lo tendrían nueve de veintitrés jugadores y dejaría de distinguir a nadie.

Una sola fila de cuerpo no cuenta para ninguna de las dos cosas: una banda sobre el suelo es palíndroma por
casualidad y no por dibujo, y son siete de los veinte espejos del histórico.

#### Scenario: el espejo de una fila no cuenta
- **WHEN** una cuadrícula simétrica tiene una sola fila de cuerpo
- **THEN** no se le reconoce el espejo

#### Scenario: reconocer un espejo y premiarlo piden cuerpos distintos
- **WHEN** una cuadrícula simétrica tiene dos filas de cuerpo
- **THEN** se clasifica como geométrica
- **AND** no se lleva el logro del espejo perfecto
