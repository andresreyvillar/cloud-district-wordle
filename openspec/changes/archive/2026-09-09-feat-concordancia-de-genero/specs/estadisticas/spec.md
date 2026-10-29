# estadisticas — delta

## ADDED Requirements

### Requirement: Lo que el sistema afirma de una persona sale de un dato, no de una deducción

Cuando el mensaje necesita saber algo de un jugador que no está en sus resultados —cómo referirse a él, por
ejemplo— ese dato **se declara**, no se infiere de lo que hay a mano.

La diferencia importa porque los sujetos son personas identificables y el mensaje se publica delante de todo
el grupo: una media mal calculada es un error que se corrige, y dirigirse mal a alguien no. Deducirlo del
nombre habría sido gratis de implementar y de coste desigual — lo pagaría siempre la misma persona.

Un dato declarado además se puede **corregir en un sitio** y deja constancia de quién lo declaró. Y lo que no
está declarado no se rellena con una suposición: se usa la forma que no afirma nada.

#### Scenario: un dato sobre una persona no se deduce
- **WHEN** el mensaje necesita un dato de un jugador que no está en sus resultados
- **THEN** sale de una declaración explícita, y si no la hay se usa la forma que no supone nada
