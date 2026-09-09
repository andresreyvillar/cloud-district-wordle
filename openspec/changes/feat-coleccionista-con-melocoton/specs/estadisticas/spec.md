# estadisticas — delta

## MODIFIED Requirements

### Requirement: El Coleccionista colecciona lo que se ha dibujado en su temporada

La medalla se concede a quien tenga al menos una partida de **cada categoría que haya aparecido en esa
temporada**, no de una lista fija de categorías.

La lista fija se quedaba desfasada al añadir una categoría, y exigirla hacia atrás **quita medallas ya
concedidas**: medido al añadir el melocotón, 25 personas la habrían perdido por una regla que no existía
cuando jugaron. Derivarlo de lo que ha salido lo evita sin necesidad de un corte de fechas, y hace que la
medalla signifique lo que su nombre promete.

Si no se sabe qué ha salido, se cae a las categorías con umbral propio en lugar de dar la medalla por buena:
la condición de «todas» sobre un conjunto vacío se cumple siempre, y eso la concedería a cualquiera.

#### Scenario: el coleccionista se ajusta a lo que ha salido
- **WHEN** una categoría nueva aparece en una temporada
- **THEN** el Coleccionista la exige en esa temporada
- **AND** no la exige en las temporadas donde no apareció
- **AND** sin saber qué ha salido, no se concede a quien no tiene variedad
