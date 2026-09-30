---
slice: marcador-del-juego
status: proposed
kind: action
actor: jugador
trigger:
  type: ui
  surface: web
  detail: "/ y /t/<AAAA-MM> — el bloque SUPERWORDLEBROS de la temporada, debajo del álbum de figuras"
events:
  emits: []
  consumes: []
specs:
  - dashboard
  - ranking
tests_root: tests/slices/marcador-del-juego/
blocked: null
---

# La temporada enseña quién manda en el SuperWordleBros

**Actor:** quien mira la temporada en la web
**Trigger:** la vista de una temporada

## Contexto

La clasificación del juego del mes ([[clasificacion-del-juego]]) llega en la instantánea. La vista de la
temporada ya tiene el marcador general y el álbum de figuras; el juego va **debajo del álbum** (decisión del
dueño), con el mismo estilo de tabla.

## Trigger técnico

La vista `/` y `/t/<AAAA-MM>` pinta `bloqueDelJuego(carga)` a partir de `carga.juego`, sin recalcular nada.

## Comportamiento observable

### el-bloque-va-debajo-del-album
**WHEN** se pinta una temporada con clasificación del juego
**THEN** aparece un bloque SUPERWORDLEBROS justo después del álbum de figuras y antes de las estadísticas

### cada-fila-lleva-puesto-puntos-niveles-y-victorias
**WHEN** se pinta el bloque
**THEN** cada jugador sale con su puesto, su nombre, sus puntos, los niveles que ha jugado y sus victorias, en
el orden de la clasificación

### los-empates-se-ven-como-empates
**WHEN** dos jugadores comparten puesto
**THEN** el número del puesto solo se escribe en la primera de las dos filas, como en el marcador general

### la-escala-se-explica
**WHEN** se pinta el bloque
**THEN** dice cómo se puntúa —10, 8, 6, 5, 4, 3, 2 y 1 por puesto en cada nivel— y cuántos niveles lleva el
mes

### sin-marcas-no-hay-bloque
**WHEN** la clasificación del juego está vacía, o la instantánea no trae la clave `juego`
**THEN** el bloque no se pinta y el resto de la temporada sale igual

### los-nombres-se-escapan
**WHEN** un nombre trae caracteres de HTML
**THEN** sale escapado

## Estado después

Solo lectura: la vista no escribe nada.

## Edge cases

- **Instantáneas antiguas** sin la clave `juego` —las de antes de este slice, o la temporada 0— no pintan el
  bloque.

## Slices compañeros
- [[clasificacion-del-juego]] — de dónde sale la tabla.
- [[album-de-figuras]] — el bloque que va justo encima.
- [[clasificacion-de-temporada]] — la vista en la que vive.
