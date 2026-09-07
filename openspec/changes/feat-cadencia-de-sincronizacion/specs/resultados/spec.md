# resultados — delta

## MODIFIED Requirements

### Requirement: La frescura se persigue con dos mecanismos que se complementan

La ingesta se dispara por ventanas frecuentes **y** cada ejecución cubre varias horas sincronizando
repetidamente. Las dos piezas responden a fallos distintos del planificador y ninguna sobra:

- las **ventanas** dan frecuencia cuando el planificador responde;
- la **cobertura por ejecución** da continuidad cuando el planificador calla.

El sistema se adapta solo: con el planificador sano, cada ventana cancela la ejecución en curso y sincroniza,
así que el bucle nunca pasa de su primera vuelta; con el planificador callado, la ejecución viva sigue
sincronizando y cubre el silencio.

Cancelar una ejecución a media sincronización es seguro porque la ingesta y la materialización son
idempotentes.

#### Scenario: las ventanas y la cobertura se complementan
- **WHEN** el planificador descarta la mayoría de las ventanas
- **THEN** la ejecución que sí arrancó sigue sincronizando y la cadencia se mantiene
