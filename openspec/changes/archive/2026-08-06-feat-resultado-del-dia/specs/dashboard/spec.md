# Deltas de `dashboard` — feat-resultado-del-dia

## ADDED Requirements

### Requirement: Los umbrales que la web aplica salen de las reglas publicadas

Cuando una vista necesita un umbral del juego —la muestra mínima de un día, por ejemplo— lo lee de las
**reglas que viajan dentro de la instantánea**, y esas salen de la constante que usa el cálculo en Python.

Escribir el número en el JavaScript de la vista sería exactamente la divergencia que la página de reglas
existe para evitar: recalibrar en Python dejaría la web afirmando otra cosa.

Si la instantánea no trae el umbral, la vista **no lo inventa**: declara que no puede afirmarlo.

#### Scenario: recalibrar el umbral en Python cambia la vista sin tocarla
- GIVEN una jornada con tres resultados
- WHEN el umbral publicado es cinco
- THEN la vista dice que la jornada no cuenta
- WHEN el umbral publicado es tres
- THEN la vista dice que cuenta, sin cambiar el código de la vista

#### Scenario: sin umbral publicado no se afirma nada
- GIVEN una instantánea sin reglas
- WHEN se muestra el día
- THEN la vista declara que no puede afirmar si la jornada cuenta

verified-by:
  - tests/slices/resultado-del-dia/dia.test.js
