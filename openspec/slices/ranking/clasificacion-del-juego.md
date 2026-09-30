---
slice: clasificacion-del-juego
status: proposed
kind: scheduled
actor: sistema
trigger:
  type: cron
  surface: pipeline
  detail: "0 * * * * — workflow update_stats.yml: materialize_seasons.py añade la clasificación del juego a la instantánea"
events:
  emits: []
  consumes: []
specs:
  - ranking
  - resultados
tests_root: tests/slices/clasificacion-del-juego/
blocked: null
---

# El SuperWordleBros tiene su clasificación del mes

**Actor:** el sistema (materialización de temporadas)
**Trigger:** cada materialización horaria de `update_stats.yml`

## Contexto

Cada día el grupo juega el nivel congelado de la jornada anterior ([[nivel-congelado]]) y deja su mejor
tiempo en el ranking de ese nivel ([[ranking-del-juego]]). Ese ranking dura un día: nadie ve quién ha
jugado mejor en todo el mes.

Los tiempos de niveles distintos **no se pueden sumar**: cada nivel tiene otro largo, según cuántos jugaron ese
día. Así que el mes se puntúa **por puesto en cada nivel** (decisión del dueño): el primero se lleva 10
puntos, el segundo 8, luego 6, 5, 4, 3 y 2, y del octavo en adelante 1. Se suman en el mes. Premia ganar y
también jugar a menudo.

La clasificación se calcula **en el pipeline**, como el resto de la temporada ([ADR 0008](../../decisions/0008-donde-vive-el-calculo.md)):
se guarda en la instantánea y la web y el resumen diario la leen de ahí, sin una segunda versión de las reglas.

## Trigger técnico

- `materialize_seasons.py`, en cada vuelta de `update_stats.yml`, lee además `game_levels` (jornada y fecha
  de cada nivel congelado) y `game_times` (jornada, jugador, segundos, estrellas) con la clave de servicio.
- La función pura `clasificacion_del_juego(resultados, niveles, marcas, temporada)` recibe todo por parámetro
  (§10) y su resultado entra en la instantánea como la clave `juego`.

## Comportamiento observable

### puntua-cada-nivel-por-puesto
**WHEN** se materializa una temporada con marcas en sus niveles
**THEN** en cada nivel, en el orden de su ranking —de más a menos estrellas y, con las mismas, de menor a mayor
tiempo—, el primero recibe 10 puntos, el segundo 8, el tercero 6, el cuarto 5, el quinto 4, el sexto 3, el
séptimo 2, y del octavo en adelante 1

### las-estrellas-pesan-mas-que-el-tiempo
**WHEN** en un nivel alguien tiene más estrellas que otro que fue más rápido
**THEN** queda por delante quien tiene más estrellas, y recibe los puntos de ese puesto

### los-empates-en-un-nivel-comparten-puntos
**WHEN** dos jugadores tienen las mismas estrellas y el mismo tiempo, en centésimas, en un nivel
**THEN** comparten puesto y reciben los puntos de ese puesto, y el siguiente salta tantos puestos como gente
lleva por delante (1, 1, 3)

### el-mes-suma-los-puntos
**WHEN** se compone la clasificación del mes
**THEN** cada jugador suma los puntos de sus niveles y la tabla va de más a menos puntos, con los niveles
jugados y las victorias de cada uno

### los-empates-del-mes-comparten-puesto
**WHEN** dos jugadores acaban el mes con los mismos puntos
**THEN** comparten puesto; más victorias y luego el nombre solo deciden en qué orden se listan

### solo-puntuan-los-niveles-de-dias-de-temporada
**WHEN** un nivel es de una jornada que no cuenta para la temporada —fin de semana, o un laborable con menos
de cinco jugadores—
**THEN** sus marcas no dan puntos, igual que esa jornada no cuenta en la clasificación general

### el-nivel-cuenta-en-el-mes-de-su-jornada
**WHEN** el nivel de la última jornada de un mes se juega ya en el mes siguiente
**THEN** sus puntos cuentan en el mes de su jornada, no en el de la partida

### sin-marcas-la-clasificacion-esta-vacia
**WHEN** nadie ha terminado ningún nivel de la temporada
**THEN** la clave `juego` de la instantánea tiene la clasificación vacía, y el resto de la instantánea no
cambia

### los-nombres-son-los-del-grupo
**WHEN** se nombra a un jugador en la clasificación del juego
**THEN** lleva el nombre de su fila más reciente en `wordle_results`, el mismo que en el resto de la web; una
marca de alguien sin filas sale con su identificador

### la-clasificacion-es-determinista
**WHEN** se calcula dos veces con los mismos resultados, niveles y marcas, llegados en cualquier orden
**THEN** sale la misma clasificación: sin reloj, sin azar y sin depender del orden de las filas

### la-materializacion-lee-niveles-y-marcas
**WHEN** corre la materialización
**THEN** lee de `game_levels` la jornada y la fecha de cada nivel y de `game_times` las marcas, paginando, y
no escribe en ninguna de las dos tablas

## Estado después

- `season_snapshots.payload.juego` = `{ escala, niveles, clasificacion: [{ posicion, jugador, nombre, puntos,
  niveles, victorias }] }` para cada temporada materializada.
- Nada cambia en `wordle_results`, `game_levels` ni `game_times`: el pipeline solo los lee.

## Edge cases

- **Un cambio en la escala no se ve hasta la siguiente materialización**, como cualquier regla que vive en la
  instantánea.
- **Temporada 0**: no hay juego antes de septiembre de 2026, así que su `juego` sale vacío.
- **Marcas de un nivel que aún está abierto** cuentan con su valor del momento; la materialización horaria las
  actualiza hasta que el nivel se cierra ([[ranking-del-juego]]).

## Slices compañeros
- [[ranking-del-juego]] — las marcas por nivel que esto puntúa, y el cierre del nivel.
- [[nivel-congelado]] — la jornada y la fecha de cada nivel.
- [[marcador-del-juego]] — el bloque de la web que pinta esta clasificación.
- [[resumen-diario-compuesto]] — el podio del juego en el resumen del canal.
- [[temporada-mensual]] — qué jornadas forman la temporada.
