# ranking — delta

## MODIFIED Requirements

### Requirement: Al cerrar un mes su instantánea se actualiza

Una ejecución normal del pipeline materializa la temporada en curso **y la última que se cerró**.

Hace falta porque el estado —«en curso» o «cerrada»— viaja dentro de la instantánea y no se calcula al
pintarla: una temporada que sale del filtro de «en curso» sin volver a escribirse conserva para siempre el
estado del último día que lo estuvo, y la web la anuncia abierta después de haber cerrado.

Basta con la última cerrada: las anteriores ya se escribieron estando cerradas. El histórico completo sigue
detrás de una opción explícita, porque recalcularlo cada hora son 181 jornadas para arreglar una etiqueta.

#### Scenario: al cerrar un mes su instantánea se actualiza
- **WHEN** una temporada deja de estar en curso porque empieza la siguiente
- **THEN** se rematerializa también ella
- **AND** las temporadas cerradas anteriores no se recalculan
