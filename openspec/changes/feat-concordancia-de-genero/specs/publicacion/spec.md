# publicacion — delta

## ADDED Requirements

### Requirement: Las frases concuerdan en género con una forma declarada

Los adjetivos y participios de las frases concuerdan con la forma gramatical de la persona nombrada, y esa
forma **está declarada en una tabla**: no se deduce del nombre en tiempo de ejecución.

El motivo es que equivocarse aquí no es un fallo de concordancia — es dirigirse mal a un compañero
identificable delante de todo el grupo. Una tabla concentra el dato en un sitio, así que un error se corrige
una vez, y hace explícito quién lo declaró.

Con varias personas se usa la forma femenina solo si todas la tienen declarada así, y la masculina en
cualquier grupo mixto. **Con alguien sin declarar se usa la forma neutra**: el sistema no supone nada de quien
no consta, así que un jugador nuevo no hereda la suposición de nadie.

#### Scenario: la frase concuerda en género
- **WHEN** una frase lleva un participio que cambia con el género
- **THEN** concuerda con la forma declarada de esa persona

#### Scenario: quien no está declarado sale en neutro
- **WHEN** se nombra a alguien que no está en la tabla
- **THEN** se usa la forma neutra en lugar de suponer una

#### Scenario: un grupo mixto va en masculino
- **WHEN** se nombra a varias personas con formas distintas
- **THEN** se usa la masculina; y la femenina solo si todas lo son
