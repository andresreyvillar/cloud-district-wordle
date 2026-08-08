---
slice: figuras-de-la-jornada
status: proposed
kind: action
actor: jugador
trigger:
  type: ui
  surface: web
  detail: "/hoy — la jornada en curso, con lo que ha dibujado cada participante"
events:
  emits: []
  consumes: []
specs:
  - estadisticas
  - dashboard
tests_root: tests/slices/figuras-de-la-jornada/
blocked: null
---

# En la jornada de hoy se ve qué ha dibujado cada uno

**Actor:** cualquiera del grupo
**Trigger:** abrir `/hoy`

## Contexto

`/hoy` dice quién ha jugado, en cuántos intentos y si la jornada cuenta ya. No dice **qué ha dibujado cada
uno**, que es la mitad del juego desde que existe el álbum: el segundo eje se ve en la temporada y en la
ficha, pero no en la única vista de la jornada abierta — justo donde la gente mira cuando acaba de publicar.

**No se clasifica en el navegador.** `results.js` ya trae la cuadrícula cruda, así que la tentación es
portar el clasificador a JavaScript. Serían 120 líneas de reglas calibradas contra 30 fichas etiquetadas, y
en la primera recalibración dirían cosas distintas que el álbum y que el bot. En este repositorio, dos
definiciones de lo mismo han divergido tres veces.

La figura la publica **la instantánea**, calculada en Python como todo lo demás
([ADR 0008](../../decisions/0008-donde-vive-el-calculo.md)).

**Y no salen del álbum.** El álbum cuenta solo lo que cuenta para la temporada, y una jornada abierta
todavía no alcanza la muestra mínima a media mañana: sus figuras existen igual y se pueden mirar. Son dos
preguntas distintas —«qué puntúa» y «qué se ha dibujado hoy»— y se responden por separado.

## Trigger técnico

`pintarHoy` (`/hoy`), leyendo una clave nueva de la instantánea de la temporada en curso, que el cron
horario materializa después de ingerir.

## Comportamiento observable

### la-figura-de-cada-participante
**WHEN** se abre la jornada en curso
**THEN** cada participante que haya publicado su cuadrícula aparece con la figura que dibujó.

### la-jornada-abierta-tambien-tiene-figuras
**WHEN** la jornada todavía no alcanza la muestra mínima para contar
**THEN** sus figuras se muestran igual, porque existir y contar son cosas distintas.

### el-desfase-se-declara
**WHEN** alguien ha publicado después de la última materialización
**THEN** su resultado aparece con su puntuación y **sin figura**, y la vista dice que llega con la siguiente
actualización, en lugar de dejar un hueco sin explicar.

### sin-cuadricula-no-hay-figura
**WHEN** un resultado no trae cuadrícula
**THEN** no se le inventa figura ni se le pone la de otro.

### la-web-no-clasifica
**WHEN** se pinta la figura de un resultado
**THEN** la categoría es la que publica la instantánea, sin que el navegador interprete la cuadrícula.

### instantanea-sin-figuras-no-rompe
**WHEN** la instantánea no trae las figuras de la jornada
**THEN** `/hoy` se pinta igual que hasta ahora, sin ellas y sin errores.

## Estado después

La carga útil gana `album.ultima_jornada`: el número de jornada y la figura de cada jugador que publicó
cuadrícula ese día. Está acotado —una jornada, una decena de personas— así que no engorda la instantánea
como lo haría publicar el histórico entero.

La vista `/hoy` muestra el emoji junto a los intentos de cada tarjeta.

## Edge cases

- **Jornada sin ninguna cuadrícula**: no aparece ningún emoji y la vista no cambia de forma.
- **Fin de semana**: la jornada no cuenta, pero las figuras se ven igual; es coherente con que la vista ya
  diga que ese día no puntúa.
- **Instantánea rancia**: cuanto más vieja, más resultados sin figura. Es el mismo desfase que ya tiene el
  resto de la instantánea, y la vista ya publica su antigüedad.

## Slices compañeros

- [[resultado-del-dia]] — la vista en la que se inserta.
- [[album-de-figuras]] — el mismo dato, agregado por temporada.
- [[clasificacion-de-figuras]] — quien calcula la categoría, en Python.
