# Deltas de `ranking` — feat-victoria-el-ultimo-dia

## MODIFIED Requirements

### Requirement: El SuperWordleBros se clasifica en el mes por puntos por puesto en cada nivel

La temporada tiene una clasificación del juego además de la general y la de figuras. Los tiempos de niveles
distintos no se suman —cada nivel tiene otro largo—, así que se puntúa **por puesto en cada nivel**: 10 al
primero, 8 al segundo, 6, 5, 4, 3, 2, y 1 del octavo en adelante, en el orden del ranking del nivel: **más
estrellas primero** y, con las mismas estrellas, menos tiempo. Las mismas estrellas y el mismo tiempo en
centésimas comparten puesto y puntos (1, 1, 3). El mes suma los puntos de cada jugador; a igualdad de puntos se
comparte puesto, y las victorias y el nombre solo ordenan la lista.

Solo puntúan los niveles de jornadas que cuentan para la temporada de su fecha (laborables con al menos cinco
jugadores). Cada nivel cuenta en el mes de su jornada **salvo el del último día laborable del mes, que cuenta
en el mes siguiente**: se juega ya en él, y así el juego cierra con el mes y su campeón se puede coronar la
noche del último día (decisión del dueño).

#### Scenario: el nivel del último día cuenta en el mes siguiente
- GIVEN el nivel de la jornada del último día laborable de septiembre, con marcas
- WHEN se calculan septiembre y octubre
- THEN sus puntos están en octubre y no en septiembre

#### Scenario: un nivel de otro día cuenta en su mes
- GIVEN el nivel de un laborable que no es el último del mes
- WHEN se calcula su mes
- THEN sus puntos están en ese mes

```yaml
checks:
  - type: regex
    file: tools/juego.py
    pattern: 'if es_ultimo_laborable_del_mes\(fecha\):'
    describe: "el nivel del último laborable puntúa en el mes siguiente"
```

verified-by:
  - tests/slices/clasificacion-del-juego/test_clasificacion_del_juego.py
