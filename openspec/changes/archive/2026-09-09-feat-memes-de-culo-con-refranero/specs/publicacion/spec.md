# publicacion — delta

## MODIFIED Requirements

### Requirement: El meme del día de varios culos se apoya en el refranero

Las frases de ese registro se construyen sobre **expresiones hechas reales**, cada una usada con su
significado: el chiste ya está en el refranero que el grupo tiene en la cabeza, así que la frase solo tiene que
traerlo al marcador. Una frase inventada tiene que ser graciosa por sí sola; una que se apoya en una expresión
conocida ya lo es.

Ninguna expresión se repite más de dos veces en el registro: uno que gira sobre una sola suena a una sola
broma, que es el defecto que ya tuvo el registro de la sospecha con su molde repetido.

El registro es coloquial y vulgar, y **habla de la jornada y no de nadie**: usa el recuento y el total, nunca
un nombre. Los sujetos son personas identificables y el mensaje se publica en un canal del trabajo.

#### Scenario: el registro de culos va sobre expresiones hechas
- **WHEN** se publica el meme de un día de varios culos
- **THEN** la frase se apoya en una expresión hecha usada con su significado
- **AND** ninguna expresión domina el registro


### Requirement: El comentario de la obra del día usa el registro de su categoría

Cuando la obra del día es de una categoría con material propio, el comentario sale de ese registro y no del
genérico, con el nombre de quien la firmó. Los comentarios de dibujo llevan nombre desde siempre, así que es
ahí donde el chiste tiene sentido.

Todas las frases de un registro de categoría llevan **la palabra de esa categoría**: si el chiste está solo en
el emoji, el registro no aporta nada sobre el genérico.

Y ninguna comenta **el cuerpo de quien juega**. La broma va sobre el dibujo, la suerte y la palabra: los
sujetos son personas identificables, el mensaje lo publica un bot en un canal del trabajo, y una expresión
sobre la mala suerte y una que atribuye un acto sexual a alguien con nombre no cuestan lo mismo.

#### Scenario: el comentario del dibujo lleva la broma de su categoría
- **WHEN** la obra del día es de una categoría con registro propio
- **THEN** el comentario sale de ese registro, con el nombre de quien la firmó
- **AND** todas sus frases llevan la palabra de la categoría
- **AND** ninguna comenta el cuerpo de quien juega
