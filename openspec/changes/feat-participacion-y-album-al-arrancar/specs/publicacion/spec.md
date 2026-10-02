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
