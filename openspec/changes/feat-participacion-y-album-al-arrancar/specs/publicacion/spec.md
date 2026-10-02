# Deltas de `publicacion` — feat-participacion-y-album-al-arrancar

## ADDED Requirements

### Requirement: El resumen cuenta la participación cuando es noticia

Tras la jornada, el resumen dice cuántos han jugado si la jornada bate el récord del canal, trae
`DEBUTANTES_NOTICIA` o más debutantes, o junta `AFLUENCIA_NOTICIA` veces la mediana de las últimas
`JORNADAS_DE_REFERENCIA` jornadas de temporada. Da la bienvenida a los debutantes por su nombre —como mucho
`NOMBRES_DE_BIENVENIDA`, el resto resumido— y cierra con una coletilla pop que rota por jornada. Un día
normal, o sin jornadas anteriores, no sale.

#### Scenario: un récord con debutantes se cuenta
- GIVEN una jornada con más jugadores que ninguna anterior y cinco debutantes
- WHEN se compone el resumen
- THEN dice cuántos son, que es récord, cuánto es lo normal, nombra a tres y resume a dos

#### Scenario: un día normal no lo menciona
- GIVEN una jornada con la gente de siempre
- WHEN se compone el resumen
- THEN no hay bloque de participación

verified-by:
  - tests/slices/resumen-diario-compuesto/test_participacion.py

## MODIFIED Requirements

### Requirement: El juego y las figuras van en lista; el podio ASCII es del marcador

En el resumen diario, los tres primeros del SuperWordleBros del mes y del álbum de figuras van en una lista,
una línea por puesto («1º Ana · 18 pts»), con los empatados en la misma línea y como mucho tres nombres por
puesto. Solo el marcador general lleva el podio dibujado: es el protagonista (decisión del dueño, 2026-10-02).
El mensaje de la victoria del mes no cambia con este requisito.

#### Scenario: el juego y las figuras no llevan dibujo
- GIVEN un resumen con marcador, juego y figuras
- WHEN se compone
- THEN solo hay un bloque de código, el del marcador, y el juego y las figuras van en lista

#### Scenario: la frase de varios concuerda en plural
- GIVEN dos jugadores que comparten el hecho del día
- WHEN se escribe su comentario
- THEN el verbo va en plural para todas las claves de frases

verified-by:
  - tests/slices/resumen-diario-compuesto/test_podios.py
  - tests/slices/comentarios-de-la-jornada/test_comentarios.py
