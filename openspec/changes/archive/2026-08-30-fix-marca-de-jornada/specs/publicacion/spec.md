# publicacion — delta

## MODIFIED Requirements

### Requirement: La guarda de duplicados no depende de cómo Slack guarde el título

Para saber si la jornada ya se publicó se busca **la marca de la jornada** dentro del título de la captura, no
el título completo.

Comparar el título entero falló en producción: Slack convierte el emoji a su código corto, así que el texto
que devuelve el canal nunca es igual al que se envió, la guarda no detectaba nada y el grupo recibió el
resumen por triplicado dos días seguidos.

La marca va anclada para que no coincida por prefijo con una jornada de más cifras.

#### Scenario: la guarda reconoce el título tal como lo devuelve Slack
- **WHEN** el canal devuelve el título con el emoji convertido a su código corto
- **THEN** la jornada se reconoce como ya publicada

#### Scenario: la marca no confunde jornadas que comparten dígitos
- **WHEN** el título lleva una jornada cuyo número empieza por el de la buscada
- **THEN** no se da por publicada
