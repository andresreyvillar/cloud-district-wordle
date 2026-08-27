# publicacion — delta

## ADDED Requirements

### Requirement: La jornada no se publica dos veces

Antes de publicar, se comprueba si el canal ya tiene la captura de la jornada que toca. Si la tiene, la
ejecución termina con éxito sin publicar y **sin sacar la captura**.

La jornada viaja en el título de la captura, que es lo que hace la comprobación posible sin guardar estado en
ninguna parte ni consultar el reloj. Se prefirió a comparar fechas porque una publicación muy retrasada puede
cruzar la medianoche UTC.

Existe porque el grupo recibió el mismo resumen dos veces: el cron no se disparó por una caída de Actions, se
lanzó a mano, y el programado llegó dos horas tarde y publicó de nuevo.

#### Scenario: la jornada no se publica dos veces
- **WHEN** el canal ya tiene la captura de la jornada que toca publicar
- **THEN** no se vuelve a publicar y la ejecución termina bien
- **AND** no se saca la captura, porque es el paso caro

#### Scenario: solo cuenta lo que publicó el bot
- **WHEN** un mensaje de una persona lleva un fichero con ese mismo título
- **THEN** no bloquea la publicación

#### Scenario: si el canal no se puede leer se publica
- **WHEN** no se puede comprobar si ya se publicó porque el canal no responde
- **THEN** se publica igualmente, porque un canal caído no puede dejar al grupo sin mensaje
