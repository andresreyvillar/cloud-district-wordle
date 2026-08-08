---
slice: album-de-figuras
status: proposed
kind: action
actor: jugador
trigger:
  type: ui
  surface: web
  detail: "/t/<AAAA-MM> y /t/<AAAA-MM>/j/<U…> — el bloque de álbum en la temporada y en la ficha"
events:
  emits: []
  consumes: []
specs:
  - dashboard
  - estadisticas
tests_root: tests/slices/album-de-figuras/
blocked: null
---

# Un jugador puede ver qué ha dibujado, no solo cuánto ha acertado

**Actor:** cualquiera del grupo
**Trigger:** abrir una temporada o su propia ficha

## Contexto

El álbum ya se calcula y viaja en la instantánea ([[clasificacion-de-figuras]]): el recuento por categoría
de cada jugador, su tasa de figuras reconocibles y su puesto. **Nadie lo ve.** Este slice es la vista, y
nada más: no calcula ni reordena, selecciona y pinta.

Es el segundo eje del juego y premia a otra gente que el marcador — en la temporada 0, los dos podios no
comparten a nadie. Enseñarlo junto al marcador es lo que convierte esa afirmación en algo que el grupo
puede comprobar de un vistazo.

La tira va **agrupada** (`🦜1 🌷2 📐1 🌀12`) y no repitiendo emojis: con 135 partidas y un tercio de
abstractos, la tira literal satura la línea ([brief](../../../docs/context/briefs/ranking-de-figuras.md)).

Y los emojis salen del **vocabulario que publica la instantánea**. Un mapa de categoría a emoji escrito en
JavaScript sería una segunda verdad que se queda atrás en cuanto se añada o renombre una categoría — es el
mismo error que ya costó dos correcciones en este repositorio.

## Trigger técnico

Las dos vistas que ya existen: `pintarTemporada` (`/t/<AAAA-MM>`) y `pintarJugador`
(`/t/<AAAA-MM>/j/<U…>`), leyendo la clave `album` de la instantánea que la web ya tiene cargada.

**La instantánea puede no traerla.** La web publicada lee lo que escribe el cron de `main`, que todavía no
materializa el álbum, así que la vista tiene que funcionar sin él.

## Comportamiento observable

### tira-agrupada
**WHEN** se muestra el álbum de un jugador
**THEN** cada categoría aparece una sola vez con su recuento, en el orden en que puntúan, y las categorías
sin partidas no aparecen.

### emoji-del-payload
**WHEN** se pinta una categoría
**THEN** el emoji y el orden son los que publica la instantánea, de modo que renombrar o añadir una
categoría en Python cambia la web sin tocarla, y una categoría sin emoji se muestra por su nombre.

### ranking-de-belleza-en-la-temporada
**WHEN** se mira una temporada con jugadores clasificados
**THEN** aparece el ranking de belleza con puesto, nombre, tasa y tira, ordenado como viene, y separado del
marcador de puntuación.

### cobertura-declarada
**WHEN** parte de las partidas de la temporada no tienen patrón
**THEN** la vista dice cuántas se quedaron sin clasificar, en lugar de presentar el álbum como si cubriera
toda la temporada.

### sin-nadie-clasificado-se-dice
**WHEN** ninguna persona alcanza el mínimo de partidas
**THEN** se explica por qué no hay ranking todavía, en lugar de una tabla vacía o un campeón inventado.

### album-en-la-ficha
**WHEN** un jugador abre su ficha
**THEN** ve su tira, su tasa y su puesto en el álbum; y si no llega al mínimo, ve cuántas partidas le faltan.

### instantanea-sin-album-no-rompe
**WHEN** la instantánea no trae la clave del álbum
**THEN** la temporada y la ficha se pintan igual, sin el bloque y sin errores.

## Estado después

La vista de temporada gana un bloque **ÁLBUM DE FIGURAS** debajo de los logros, y la ficha una tarjeta con
la tira del jugador. Ninguna vista existente cambia de contenido: el marcador, el podio, los logros y las
estadísticas se pintan exactamente igual.

Con los datos de hoy, la temporada 0 muestra 18 jugadores con puesto encabezados por un 83%, y agosto
muestra el aviso de que 61 de sus 80 partidas no tienen dibujo todavía.

## Edge cases

- **Instantánea antigua**: sin clave `album`, el bloque no se pinta. Es el estado de producción hasta que
  la rama se mergee, así que no es hipotético.
- **Álbum sin vocabulario**: no se inventa emoji; se muestra el nombre de la categoría.
- **Jugador sin partidas clasificadas**: su ficha dice que aún no tiene álbum, no un 0%.
- **Temporada 0**: 181 jornadas y hasta 135 partidas por jugador. La tira agrupada no crece con eso, que es
  justo la razón de agruparla.

## Slices compañeros

- [[clasificacion-de-figuras]] — calcula y publica lo que aquí se pinta.
- [[ficha-de-jugador]] — la ficha en la que se inserta la tarjeta del álbum.
- [[escala-fija-comparable]] — la otra regla de "dos gráficos del mismo tipo se comparan mirándolos".
