# dashboard — delta

## MODIFIED Requirements

### Requirement: La página de reglas explica el margen creciente y sus dos parámetros

La regla de imputación se explica con el margen que crece: qué cuesta la primera falta, cuánto sube cada
siguiente y por qué. Los dos parámetros —el margen base y el paso— aparecen con su valor y su origen en el
código, como el resto.

Se explica también **por qué** creció: con un margen igual para cada falta la regla premiaba no aparecer, y eso
es lo que el grupo necesita entender para juzgar si la regla le parece justa.

#### Scenario: la página de reglas explica el margen creciente
- **WHEN** se pinta la regla de imputación
- **THEN** dice que el margen crece con las ausencias y muestra sus dos parámetros
