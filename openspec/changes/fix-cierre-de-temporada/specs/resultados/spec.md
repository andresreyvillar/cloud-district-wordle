# resultados — delta

## MODIFIED Requirements

### Requirement: Un resultado publicado deja de ser cierto cuando cambia su contexto

Lo que la web enseña de una temporada no se recalcula al pintarlo: sale de una instantánea escrita antes. Eso
la hace rápida y consistente con lo que publica el bot, y tiene un precio que hay que administrar: **una
instantánea es cierta solo mientras nada de lo que la rodea cambie**.

El caso que lo demostró no fue un dato mal calculado, sino un dato que **envejeció**: el estado de una
temporada depende de si existe otra posterior, así que empezar un mes nuevo vuelve falsa la instantánea del
anterior sin tocarla.

De ahí la regla: cuando un hecho de una temporada dependa de algo externo a ella, hay que **reescribirla
cuando ese algo cambie**, no confiar en que se calculará al leer.

#### Scenario: la instantánea de un mes cerrado no se queda con el estado viejo
- **WHEN** empieza una temporada nueva
- **THEN** la anterior se reescribe, porque su estado dependía de que no hubiera ninguna posterior
