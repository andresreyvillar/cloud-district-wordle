# resultados — delta

## MODIFIED Requirements

### Requirement: Una forma puede ser propiedad de la palabra y no del jugador

Algunas cuadrículas se parecen entre sí porque **la palabra del día las obliga**, no porque quien jugó hiciera
algo particular. En la jornada que originó la categoría del melocotón, 8 de los 10 jugadores terminaron con la
misma penúltima fila: las letras impares eran fáciles y las pares difíciles, así que el grupo entero convergió
en el mismo esqueleto.

Consecuencia para quien lea el álbum: **una categoría puede aparecer en racimo**, varios el mismo día y
ninguno en meses. No es un fallo del clasificador ni una casualidad sospechosa; es la palabra repartiendo la
misma forma a todos.

Y consecuencia para quien añada categorías: una forma frecuente **dentro de un solo día** puede ser rarísima
en el histórico. Elegir el umbral o la puntuación mirando un día induce a error; hay que medir sobre el
histórico completo.

#### Scenario: una forma puede repetirse el mismo día en varios jugadores
- **WHEN** la palabra del día tiene un esqueleto de letras fáciles y difíciles muy marcado
- **THEN** varios jugadores terminan con la misma forma, y todos reciben la misma categoría
