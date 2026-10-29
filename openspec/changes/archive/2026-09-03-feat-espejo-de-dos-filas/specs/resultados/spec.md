# resultados — delta

## MODIFIED Requirements

### Requirement: Un fixture que representa una categoría no puede cumplir otra

Los patrones que los tests usan como ejemplo de una categoría tienen que cumplir **solo** esa: un fixture
llamado «flor» que además es un espejo hace que su test mida la regla del espejo sin declararlo, y cambia de
significado cuando esa otra regla cambia.

Ocurrió: `Y...Y/..Y../GGGGG` se usaba como flor en cuatro ficheros de test y es palíndromo en sus dos filas.
Al bajar el umbral del espejo, esos tests se pusieron en rojo por un motivo que no era el suyo.

Cuando un test dependa de que su fixture sea inequívoco, esa condición **se comprueba** en el propio test en
lugar de suponerse.

#### Scenario: un fixture no ambiguo se comprueba, no se supone
- **WHEN** un test necesita un patrón que solo cumpla una regla de clasificación
- **THEN** el test verifica que cumple exactamente una antes de usarlo
