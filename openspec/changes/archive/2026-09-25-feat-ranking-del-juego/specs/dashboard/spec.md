# Deltas de `dashboard` — feat-ranking-del-juego

## ADDED Requirements

### Requirement: Quien juega elige su nombre de la lista de jugadores, y la web lo recuerda

Bajo el juego hay un desplegable «¿Quién eres?» con **todos los jugadores que han jugado alguna vez**, una vez
cada uno, por orden alfabético y con el nombre de su fila más reciente. No solo los de la jornada del nivel: al
juego puede jugar quien ese día no hizo el Wordle.

La elección se recuerda **por navegador** (`localStorage['superbros:jugador']`). Si el almacén falla o el nombre
guardado ya no está en la lista, sale sin elegir y el juego funciona igual. No hay login: elegir un nombre es
un acto de confianza, como pegar un Wordle en el canal.

#### Scenario: el desplegable trae a cada jugador una vez
- GIVEN resultados de varias jornadas
- WHEN se abre la pestaña del juego
- THEN el desplegable tiene una opción vacía y una por jugador, en orden alfabético, con los nombres escapados

#### Scenario: el nombre elegido vuelve elegido
- GIVEN alguien que eligió su nombre
- WHEN vuelve a abrir la pestaña
- THEN el desplegable ya lo tiene elegido, salvo que el almacén falle o el nombre ya no exista

verified-by:
  - tests/slices/ranking-del-juego/marcas.test.js


### Requirement: Cada llegada a la meta va al ranking del nivel

Al terminar el nivel, la página manda la marca —jornada del nivel, jugador, segundos con centésimas y
estrellas acotadas al total— a `registrar_tiempo`, y vuelve a leer el ranking. **En cada partida**: tras
reiniciar con `R` se vuelve a terminar, y reintentar no tiene límite.

Sin nombre elegido, **la partida espera**: se pide que elija quién es, y al elegirlo se guarda esa misma, una
vez. La página dice si fue marca nueva o cuál es la que se queda; si la llamada falla, lo dice y se sigue
jugando.

#### Scenario: con nombre, terminar manda la marca
- GIVEN un nombre elegido
- WHEN se llega a la meta
- THEN se manda la marca de la jornada del nivel con las estrellas acotadas al total

#### Scenario: sin nombre, la marca espera a que elija
- GIVEN nadie elegido
- WHEN se llega a la meta y después se elige un nombre
- THEN no se manda nada hasta elegir, y entonces se manda esa marca una sola vez

#### Scenario: se dice si mejora o no
- GIVEN una marca mandada
- WHEN la base de datos responde
- THEN la página dice «nueva marca» o cuál es la mejor que se queda, y si falla, que no se pudo guardar

#### Scenario: cada partida se registra
- GIVEN varias llegadas a la meta seguidas
- WHEN se termina cada una
- THEN se manda cada una

```yaml
checks:
  - type: regex
    file: v2/js/ui/juego.js
    pattern: 'lienzo\.addEventListener\(EVENTO_FIN, alTerminar\);'
    describe: el aviso de fin se escucha en cada partida, no solo en la primera (sin `once`)
  - type: regex
    file: v2/js/ui/juego.js
    pattern: 'await control\.terminar\(\{ segundos, estrellas \}\)'
    describe: la llegada a la meta pasa por el control del ranking, no solo por el texto para compartir
```

verified-by:
  - tests/slices/ranking-del-juego/marcas.test.js


### Requirement: El ranking es uno por nivel y comparte puesto en el empate

El ranking bajo el juego enseña solo las marcas de la jornada del nivel, de menor a mayor tiempo, con puesto,
nombre, tiempo con centésimas y estrellas. Dos tiempos iguales comparten puesto y el siguiente salta (1, 1, 3),
como en el resto de la web. La fila de quien juega se distingue. Sin marcas, se dice que nadie lo ha terminado.

#### Scenario: se ordena por tiempo y comparte puesto
- GIVEN marcas de varios jugadores, dos con el mismo tiempo
- WHEN se pinta el ranking
- THEN salen de menor a mayor tiempo y las dos iguales comparten puesto

#### Scenario: sin marcas se dice
- GIVEN un nivel que nadie ha terminado
- WHEN se pinta el ranking
- THEN dice que nadie lo ha terminado en lugar de pintar una tabla vacía

```yaml
checks:
  - type: regex
    file: v2/js/data/results.js
    pattern: "\\.from\\('game_times'\\)[\\s\\S]*?\\.eq\\('jornada', jornada\\)"
    describe: el ranking se lee filtrado por la jornada del nivel
```

verified-by:
  - tests/slices/ranking-del-juego/marcas.test.js
