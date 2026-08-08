# Deltas de `publicacion` — feat-comentarios-por-la-hora

## ADDED Requirements

### Requirement: El resumen comenta también a qué hora se juega

Además de las notas, el resumen mira **cuándo** se publicó cada resultado: quién llega el último con el día
ya vencido, y quién llega el último **y además** con una nota muy por encima de lo que ha hecho el grupo —
que es el chiste de haber visto antes los resultados de los demás.

La hora sale de cuándo se registró la fila, que aproxima la publicación con un margen de hasta una hora
—lo que tarda el cron—: suficiente para distinguir «por la mañana» de «a media tarde», que es lo único que
estos comentarios necesitan.

**Solo se usa si esa marca cae el mismo día que el puzzle.** Las filas recuperadas en el backfill se
insertaron todas de golpe en otra fecha: ahí el margen no es de una hora sino de meses, y el comentario
señalaría a alguien por algo que no hizo.

Y se añade el caso más raro de todos: **acertar a la primera**.

#### Scenario: el último en publicar con mucho hueco se comenta
- GIVEN una jornada en la que el último publica muy por detrás del resto y con el día avanzado
- WHEN se componen los comentarios
- THEN se comenta su retraso

#### Scenario: publicar a la vez que los demás no es llegar tarde
- GIVEN una jornada en la que todos publican seguidos
- WHEN se componen los comentarios
- THEN no se comenta ningún retraso

#### Scenario: sin hora utilizable no se comenta el retraso
- GIVEN resultados cuya marca de registro es de otro día
- WHEN se componen los comentarios
- THEN no se comenta el retraso, porque esa hora no dice cuándo se publicó

#### Scenario: llegar tarde y además clavarla es otro chiste
- GIVEN alguien que publica el último y con una nota muy por encima de la media del día
- WHEN se componen los comentarios
- THEN se comenta la sospecha, no el simple retraso

#### Scenario: acertar a la primera se señala
- GIVEN alguien que resuelve en un solo intento
- WHEN se componen los comentarios
- THEN es lo primero que se comenta

verified-by:
  - tests/slices/comentarios-de-la-jornada/test_comentarios.py
