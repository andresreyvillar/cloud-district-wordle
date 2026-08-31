# publicacion — delta

## ADDED Requirements

### Requirement: Al empezar el mes se publica el podio del que cierra

Una vez al mes, el canal recibe el podio de la temporada cerrada con su imagen, la felicitación al campeón y
el ánimo para la que empieza.

**Qué mes se celebra sale de los datos, no del reloj**: es el anterior al del último resultado de la tabla, y
tiene que ser consecutivo. Si el mes nuevo aún no tiene resultados no se celebra nada, porque «el anterior»
sería un mes ya celebrado. La temporada histórica no se celebra: no cerró un mes.

El podio lleva los empates enteros, igual que el marcador diario. Con empate en el primer puesto se felicita a
todos los empatados y no se atribuyen medallas a uno solo.

La imagen es **la captura del podio de esa temporada en la web**, para que el mensaje y la página no puedan
decir cosas distintas.

El mensaje es idempotente: el título de la imagen lleva el mes celebrado, y si el canal ya lo tiene no se
repite. Eso es lo que permite que el cron corra varios días seguidos sin duplicar, y lo que hace que una
ventana descartada no pierda el cierre.

#### Scenario: el mes que cierra sale de los datos
- **WHEN** se decide qué mes celebrar
- **THEN** es el anterior al del último resultado, y consecutivo con él

#### Scenario: sin mes nuevo no se celebra nada
- **WHEN** el mes nuevo todavía no tiene resultados
- **THEN** no se publica nada, no se saca la captura y la ejecución termina bien

#### Scenario: el podio lleva los empates enteros
- **WHEN** varias personas comparten un puesto del podio
- **THEN** suben todas

#### Scenario: el cierre no se publica dos veces
- **WHEN** el canal ya tiene el podio de ese mes
- **THEN** no se vuelve a publicar
