# publicacion — delta

## MODIFIED Requirements

### Requirement: El meme del día remite a algo reconocible

El registro de memes está poblado con referencias de cine, series, videojuegos, televisión e internet,
**adaptadas al juego** en lugar de citadas literalmente. Un meme que no remite a nada no es un meme.

Las plantillas con referencia van **intercaladas** con las genéricas, no añadidas al final: la variante se
elige por número de jornada, así que apiladas al final los índices bajos seguirían dando siempre las
genéricas y las referencias no llegarían a publicarse.

#### Scenario: el meme cita algo reconocible
- **WHEN** se publica el meme del día
- **THEN** una parte sustancial del registro de cada forma remite a algo identificable
- **AND** las referenciadas están repartidas por el ciclo, no agrupadas al final

### Requirement: Los ausentes se nombran por orden de clasificación

Cuando faltan más personas de las que caben, los nombrados son los **mejor clasificados** de entre los
ausentes: la ausencia de quien va segundo es más noticia que la de quien va decimoquinto. Antes se ordenaba
por nombre, así que salía nombrado quien tuviera la inicial más baja.

#### Scenario: los ausentes se nombran por orden de clasificación
- **WHEN** faltan más personas de las que se pueden nombrar
- **THEN** se nombran los mejor clasificados, en ese orden
- **AND** no se nombran por orden alfabético
