# Deltas de `publicacion` — fix-sospecha-de-la-mejor-nota

## MODIFIED Requirements

### Requirement: La sospecha se lanza a la mejor nota del día, y solo si nadie la comparte

La pulla de la sospecha salía para **cualquiera** que bajara de tres intentos, sin mirar qué había hecho el
resto. Eso produce dos mensajes que no se sostienen leídos por alguien del grupo:

- **Dudar de quien lo hizo peor.** Con un 1 en la mesa, quejarse de un 2 es poner en duda al segundo mientras
  se deja pasar al primero. Medido sobre 194 jornadas, esto había ocurrido **una sola vez**, porque una nota
  de 1 aparece en 3 jornadas de 194 — y ocurrió el día en que más se notaba.
- **Dudar de una coincidencia.** Cuando la mejor nota la firman varias personas, lo que dice el dato es que la
  palabra era fácil, no que nadie hiciera nada raro. Son 16 jornadas de 194.

La pulla va por tanto a quien firma la mejor nota del día, con dos intentos o menos, **y solo si la firma
solo**. El chiste sigue saliendo en una de cada cuatro jornadas (24%, antes 32%).

#### Scenario: con una nota mejor en la mesa, la sospecha no va al segundo
- GIVEN una jornada donde alguien resuelve en 1 y otras personas en 2
- WHEN se eligen los hechos comentables
- THEN la sospecha señala a quien resolvió en 1
- AND no se comenta la nota de quienes resolvieron en 2

#### Scenario: una mejor nota compartida no levanta sospecha
- GIVEN una jornada donde dos personas comparten la mejor nota, de dos intentos
- WHEN se eligen los hechos comentables
- THEN no se lanza la pulla de la sospecha a ninguna de las dos

#### Scenario: la mejor nota en solitario sigue teniendo su pulla
- GIVEN una jornada donde una sola persona firma la mejor nota, de dos intentos
- WHEN se eligen los hechos comentables
- THEN esa persona recibe la pulla de la sospecha

verified-by:
  - tests/slices/comentarios-de-la-jornada/test_comentarios.py
