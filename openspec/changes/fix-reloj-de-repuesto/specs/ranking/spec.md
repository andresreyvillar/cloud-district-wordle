# ranking — delta

## ADDED Requirements

### Requirement: La sincronización horaria no depende de un solo reloj

El workflow de datos se despierta desde **dos relojes independientes**: el planificador de la forja y un cron
externo que lo lanza por API.

Hace falta porque el planificador de la forja no garantiza sus ventanas: su documentación admite que los
trabajos en cola pueden descartarse, y medido sobre este repositorio salían 5 o 6 de las 24 esperadas al día,
con huecos de hasta seis horas. Mover el cron a otro minuto —lo único que la forja recomienda— se probó y no
mejoró.

Despertar el workflow dos veces **no duplica nada**: la ingesta no reescribe resultados ya guardados y la
materialización actualiza en lugar de insertar. El disparador externo está apagado mientras no tenga
credencial, y un fallo suyo no puede afectar a la web que sirve el mismo proceso.

#### Scenario: el pipeline tiene un reloj de repuesto
- **WHEN** el planificador de la forja descarta la ventana horaria
- **THEN** el reloj independiente despierta el mismo workflow
- **AND** sin credencial configurada el disparador no hace nada

### Requirement: Un fallo transitorio de red no cuesta la ejecución

Las lecturas y escrituras de la instantánea se reintentan unas cuantas veces con espera creciente antes de
rendirse. Un error que no es de red falla a la primera.

Medido: 4 de 200 ejecuciones del cron murieron por un timeout de red, y sin reintento cada una costaba la hora
completa.

#### Scenario: un fallo de red se reintenta
- **WHEN** una operación contra la base falla por un problema transitorio
- **THEN** se reintenta antes de rendirse
- **AND** un error de credenciales o de esquema falla a la primera
