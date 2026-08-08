# Deltas de `publicacion` — feat-comentarios-de-la-jornada

## ADDED Requirements

### Requirement: El resumen comenta los hechos notables de la jornada

El mensaje diario termina con una sección de comentarios sobre lo que ha pasado: quién resolvió un día
imposible, quién quedó muy por encima o por debajo de la media, y quién no apareció el día duro.

**Los hechos se detectan de forma determinista y la frase sale de un catálogo.** Los detectores emiten
hechos, no texto, de modo que cambiar quién redacta —una plantilla hoy, un modelo mañana— no toca la
detección.

Los umbrales están **calibrados por frecuencia**: un chiste que sale a diario deja de ser chiste. El de día
difícil se **reutiliza** del catálogo de medallas en lugar de declarar uno propio.

Una persona aparece **una sola vez** por jornada, la sección se limita a unos pocos comentarios, y una
jornada sin hechos no produce sección.

El texto es **reproducible**: dos ejecuciones sobre la misma jornada dan exactamente el mismo mensaje, sin
azar y sin reloj.

#### Scenario: resolver rápido un día duro se señala
- GIVEN una jornada de media alta y alguien que resuelve en dos intentos o menos
- WHEN se componen los comentarios
- THEN se comenta ese hecho

#### Scenario: quedarse muy por encima de la media se comenta
- GIVEN alguien cuyo resultado está muy por encima de la media del día
- WHEN se componen los comentarios
- THEN se comenta, con el margen calibrado y no con uno menor

#### Scenario: la ausencia en día difícil usa el umbral de las medallas
- GIVEN un día difícil y alguien de la temporada que no publica
- WHEN se componen los comentarios
- THEN se comenta la ausencia, con el mismo umbral de día difícil que usan las medallas

#### Scenario: una persona no sale dos veces
- GIVEN alguien que dispara más de un detector el mismo día
- WHEN se componen los comentarios
- THEN aparece una sola vez

#### Scenario: la sección se limita
- GIVEN una jornada que dispara muchos detectores
- WHEN se componen los comentarios
- THEN se publican como mucho unos pocos

#### Scenario: sin hechos no hay sección
- GIVEN una jornada sin ningún hecho notable
- WHEN se compone el resumen
- THEN no aparece la sección de comentarios

#### Scenario: el mismo día produce el mismo texto
- GIVEN una jornada concreta
- WHEN se compone el resumen dos veces
- THEN el texto es idéntico

#### Scenario: sin dificultad calculable no se comenta
- GIVEN una jornada con menos jugadores de los que hacen falta para calibrar la media
- WHEN se componen los comentarios
- THEN no se comenta nada, porque no hay contra qué comparar

verified-by:
  - tests/slices/comentarios-de-la-jornada/test_comentarios.py
