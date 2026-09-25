---
slice: ranking-del-juego
status: proposed
kind: action
actor: jugador
trigger:
  type: ui
  surface: web
  detail: "pestaña SuperWordleBros — /juego: elegir quién eres y terminar el nivel guarda tu tiempo en el ranking de ese nivel"
events:
  emits: []
  consumes: []
specs:
  - dashboard
  - resultados
tests_root: tests/slices/ranking-del-juego/
blocked: null
---

# Terminar el nivel deja tu tiempo en el ranking de esa jornada

**Actor:** quien juega a SuperWordleBros
**Trigger:** terminar el nivel con un nombre elegido

## Contexto

El juego ya se juega y se comparte copiando el texto al canal ([[juego-de-la-jornada]]), pero no hay dónde
comparar tiempos sin leer el hilo entero. El grupo quiere **un ranking debajo del juego**: cada uno elige su
nombre de la lista de jugadores, y al terminar el nivel su tiempo queda apuntado.

Se reintenta **sin límite**: la gracia es bajar la marca. Por eso el ranking guarda **la mejor marca de cada
jugador en ese nivel**, y un intento peor no la pisa. Hay **un ranking por nivel**, es decir por jornada: cada
día el escenario es otro, y comparar el tiempo de un nivel de 10 tramos con uno de 20 no dice nada.

**El modelo de confianza es el del grupo, y se declara:** no hay login. Cualquiera puede elegir cualquier
nombre, igual que cualquiera puede pegar en el canal un Wordle que no ha jugado. Lo que sí se impide es lo que
rompe el ranking para todos: escribir directamente en la tabla, borrar marcas ajenas, inventar jugadores o
jornadas, y tiempos que la física del juego no permite.

## Trigger técnico

- La pestaña `/juego` pinta, bajo el lienzo, un desplegable **«¿Quién eres?»** con los jugadores del grupo y
  el ranking del nivel que se está jugando.
- El motor dispara `superbros:fin` con `{ segundos, estrellas }` al llegar a la meta — en cada partida, también
  tras reiniciar con `R`.
- La página llama a la función `public.registrar_tiempo(p_jornada, p_jugador, p_segundos, p_estrellas)`, que
  es **la única vía de escritura** sobre la tabla nueva `public.game_times`, y vuelve a leer el ranking.

## Comportamiento observable

### elige-su-nombre-de-la-lista
**WHEN** se abre la pestaña del juego
**THEN** bajo el juego hay un desplegable «¿Quién eres?» con cada jugador del grupo una sola vez, por orden
alfabético y con su nombre de la tabla, y una opción vacía para quien aún no ha elegido

### recuerda-quien-eres
**WHEN** alguien elige su nombre y vuelve otro día al juego
**THEN** el desplegable ya lo tiene elegido; y si el navegador no deja guardar —navegación privada— o el nombre
guardado ya no está en la lista, sale sin elegir y el juego funciona igual

### terminar-registra-el-tiempo
**WHEN** alguien con nombre elegido llega a la meta
**THEN** su tiempo y sus estrellas se envían a `registrar_tiempo` para la jornada del nivel, y el ranking se
vuelve a leer y lo muestra

### sin-nombre-el-tiempo-espera
**WHEN** alguien llega a la meta sin haber elegido nombre
**THEN** se le pide que elija quién es, y al elegirlo se guarda **ese** tiempo, sin repetir el nivel

### solo-se-sobrescribe-si-mejora
**WHEN** un jugador registra un tiempo para un nivel en el que ya tiene marca
**THEN** la marca solo cambia si el tiempo nuevo es **menor**; si es igual o peor se queda la anterior, y la
página dice cuál de las dos cosas ha pasado

### se-puede-reintentar-sin-limite
**WHEN** alguien termina el nivel, pulsa `R` y lo vuelve a terminar
**THEN** cada llegada a la meta se registra, sin límite de intentos

### un-ranking-por-nivel
**WHEN** se pinta el ranking
**THEN** solo aparecen las marcas de la jornada del nivel, ordenadas de menor a mayor tiempo, con puesto,
nombre, tiempo con centésimas y estrellas; dos tiempos iguales comparten puesto, y la fila de quien juega se
distingue

### sin-marcas-lo-dice
**WHEN** nadie ha terminado todavía el nivel
**THEN** el ranking dice que nadie lo ha terminado en lugar de pintar una tabla vacía

### la-web-no-escribe-en-la-tabla
**WHEN** alguien usa la clave pública para insertar, cambiar o borrar filas de `game_times` directamente
**THEN** Postgres lo rechaza: la clave pública solo puede leer la tabla y ejecutar `registrar_tiempo`

### rechaza-lo-imposible
**WHEN** se llama a `registrar_tiempo` con un jugador que nunca ha jugado, una jornada sin nivel, más
estrellas que tramos, o un tiempo por debajo del que permite recorrer el nivel a la velocidad máxima del motor
**THEN** la llamada falla y no se escribe nada

### si-falla-el-guardado-se-dice
**WHEN** la llamada a `registrar_tiempo` falla —red, o una marca rechazada—
**THEN** la página dice que el tiempo no se ha podido guardar, el texto para compartir sigue ahí, y se puede
seguir jugando

## Estado después

- Una fila por `(jornada, jugador)` en `public.game_times` con la mejor marca: `segundos` (centésimas),
  `estrellas` y `updated_at`.
- Nada cambia en `wordle_results` ni en `season_snapshots`: la tabla es **aditiva** (ADR 0005).
- En el navegador, `localStorage['superbros:jugador']` con el nombre elegido.

## Edge cases

- **Mínimo de tiempo.** `tramos × 8 casillas × 32 px ÷ (300 px/s × 1,5)`: la distancia que hay que recorrer a
  la velocidad máxima del motor (`RUN_SPEED`, también la del impulso del pisotón), con un 50 % de margen para
  que un cambio de física de Joel no rechace tiempos honrados. Para un nivel de 15 tramos, 8,5 s.
- **Máximo.** Menos de una hora: más es una pestaña olvidada, no una partida.
- **Empate con la marca.** No la sobrescribe: la marca más antigua se queda, como en cualquier récord.
- **Jornada en curso.** No se puede registrar: desde [[nivel-congelado]] la función solo acepta jornadas con
  nivel congelado, y la de hoy no se congela nunca.
- **Suplantación.** Se acepta como parte del modelo de confianza; no hay forma de impedirla sin login.

## Slices compañeros
- [[juego-de-la-jornada]] — el nivel, el motor y el evento `superbros:fin` que este slice consume.
