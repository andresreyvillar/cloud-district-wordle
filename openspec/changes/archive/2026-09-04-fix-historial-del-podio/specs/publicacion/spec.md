# publicacion — delta

## MODIFIED Requirements

### Requirement: La comprobación de duplicados alcanza los días que el disparador corre

Cuánto historial hay que leer para saber si algo ya se publicó **depende de qué se busca**: un mensaje diario
se reconoce minutos después de publicarse, pero uno mensual puede llevar días en el canal cuando se comprueba.

El cierre de mes lee bastante historial para cubrir todos los días en que su cron puede dispararse. Con la
ventana del mensaje diario se republicó: el original estaba más atrás de lo que la comprobación alcanzaba.

#### Scenario: la comprobación alcanza los días que el cron corre
- **WHEN** se comprueba si el mes ya se celebró y el mensaje original quedó fuera de la primera página
- **THEN** se sigue leyendo historial hasta encontrarlo, y no se republica
