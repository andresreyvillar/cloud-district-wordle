# resultados — delta

## MODIFIED Requirements

### Requirement: La frescura de los datos se defiende con cobertura, no con más disparos

Cuando el planificador que dispara la ingesta no cumple lo declarado y no hay reloj externo que funcione, la
cadencia no se consigue pidiendo más disparos: se consigue haciendo que **cada disparo cubra más tiempo**.

Una ejecución sincroniza repetidamente durante horas en lugar de una sola vez, de modo que unos pocos disparos
al día bastan para una cadencia horaria. El intervalo entre sincronizaciones se elige para que ningún hueco
supere la hora, y el número de repeticiones para cubrir el hueco máximo medido en el planificador.

Solo hay una ejecución viva: un disparo nuevo cancela la anterior y reinicia la ventana de cobertura, en lugar
de acumular ejecuciones solapadas. Cancelar a media sincronización es seguro porque la ingesta y la
materialización son idempotentes.

Un fallo de una repetición no aborta las siguientes: perder una hora es preferible a perder el resto de la
ventana.

#### Scenario: unos pocos disparos dan cobertura horaria
- **WHEN** el planificador dispara la ingesta unas pocas veces al día
- **THEN** cada disparo sincroniza repetidamente hasta cubrir el hueco típico entre disparos
- **AND** ningún intervalo entre sincronizaciones supera la hora

#### Scenario: un fallo aislado no cuesta la ventana
- **WHEN** una de las sincronizaciones de la ventana falla
- **THEN** las siguientes se ejecutan igual, y la ejecución termina en error para que el fallo se vea
