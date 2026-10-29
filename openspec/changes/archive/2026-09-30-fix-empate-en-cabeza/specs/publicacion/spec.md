# Deltas de `publicacion` — fix-empate-en-cabeza

## ADDED Requirements

### Requirement: El podio de cierre felicita en plural a quienes comparten el título

Si el primer puesto del mes que cierra está compartido, el mensaje del podio felicita a todos los empatados con
una frase **escrita para varios**, que dice que comparten el primer puesto, elegida por jornada como las demás.
Nunca usa una frase escrita para un campeón solo: «Cata y Joel se lleva el mes» es un error de concordancia
delante de todo el grupo. Con un único campeón, el mensaje no cambia.

#### Scenario: dos campeones, frase en plural
- GIVEN un mes cerrado con dos jugadores empatados en el primer puesto
- WHEN se compone el podio
- THEN la felicitación nombra a los dos y dice que comparten el primer puesto, para cualquier jornada

#### Scenario: un campeón, frase de siempre
- GIVEN un mes cerrado con un único primero
- WHEN se compone el podio
- THEN la felicitación es una de las frases de campeón único

verified-by:
  - tests/slices/podio-de-cierre-de-mes/test_podio.py
