# publicacion — delta

## ADDED Requirements

### Requirement: El mensaje abre con la palabra de la jornada y su significado

El resumen empieza con la palabra que el grupo ha jugado, en mayúsculas, y su primera acepción. Es el único
dato que el mensaje puede aportar que el grupo no tenga ya: cada uno conoce su resultado, pero nadie ve la
palabra escrita ni lo que significa.

Sin acepción se publica la palabra sola. Sin palabra el mensaje sale igual, sin esa línea, y la ejecución no
falla: es un adorno, no un requisito.

La palabra entra en el compositor **por parámetro**: averiguarla es red, y la red vive en el borde, así que el
mensaje entero sigue fijándose en un test.

#### Scenario: la palabra abre el mensaje
- **WHEN** se conoce la palabra de la jornada
- **THEN** es la primera línea del mensaje, en mayúsculas y con su primera acepción

#### Scenario: sin acepción se publica la palabra sola
- **WHEN** la palabra no tiene definición disponible
- **THEN** se publica la palabra sin acepción

#### Scenario: sin palabra el mensaje sale igual
- **WHEN** no se puede averiguar la palabra
- **THEN** el mensaje se publica sin esa línea y la ejecución no falla

### Requirement: El sistema no entrega palabras de partidas sin jugar

Pedir la palabra de una jornada posterior a la última que existe en la tabla **no devuelve nada**, aunque esté
disponible en el origen.

El origen trae dos mil entradas, así que sin esta condición bastaría cambiar un número para leer meses por
delante. El repositorio es público y la liga es competitiva: la propiedad de no poder mirar por delante tiene
que estar en el código y defendida por un test, no en la buena voluntad de quien lo ejecute.

#### Scenario: nunca una palabra sin jugar
- **WHEN** se pide la palabra de una jornada posterior a la última jugada
- **THEN** no se devuelve, ni por la función que la busca ni por el flujo completo

#### Scenario: nada de la palabra se guarda
- **WHEN** se publica el mensaje
- **THEN** ni la palabra ni la lista de soluciones se escriben en ningún sitio
