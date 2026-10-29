# publicacion — delta

## MODIFIED Requirements

### Requirement: La comprobación de duplicados alcanza los días que el disparador corre

Cuánto historial hay que leer para saber si algo ya se publicó **depende de qué se busca**: un mensaje diario
se reconoce minutos después de publicarse, pero uno mensual puede llevar días en el canal cuando se comprueba.

El cierre de mes lee el canal **por fecha**: todo lo publicado desde una semana antes del arranque del mes
nuevo, sin tope de mensajes. Contando mensajes se republicó dos veces, porque la ventana se quedaba corta cada
vez que el canal crecía.

#### Scenario: la comprobación alcanza los días que el cron corre
- **WHEN** se comprueba si el mes ya se celebró y el mensaje original quedó más atrás de 150 mensajes
- **THEN** se lee desde una fecha anterior al arranque del mes nuevo, se encuentra y no se republica

## ADDED Requirements

### Requirement: El cierre de mes se intenta los tres primeros días

#### Scenario: el cierre se intenta los tres primeros días
- **WHEN** se programa la publicación del cierre de mes
- **THEN** el cron corre los días 1, 2 y 3 del mes; si GitHub se salta uno, se publica al siguiente
