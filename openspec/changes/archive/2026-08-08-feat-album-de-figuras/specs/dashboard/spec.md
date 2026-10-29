# Deltas de `dashboard` — feat-album-de-figuras

## ADDED Requirements

### Requirement: El álbum se muestra agrupado y con el vocabulario que publica el cálculo

La tira de figuras de un jugador se muestra **agrupada** —cada categoría una vez, con su recuento— y no
repitiendo un emoji por partida: con 135 partidas la tira literal satura la línea.

Los emojis **salen de la instantánea**, no de un mapa escrito en la web. Renombrar o añadir una categoría en
Python cambia lo que se ve sin tocar el frontend. Si una categoría llega sin emoji, se muestra su nombre en
lugar de inventar uno.

El catálogo llega como **lista ordenada**, no como diccionario: JSONB no conserva el orden de las claves —
Postgres las devuelve por longitud y luego alfabéticamente—, así que un diccionario pondría el ruido en
medio de las figuras que puntúan.

La vista **declara su cobertura**: cuántas partidas de la temporada se quedaron sin clasificar. Un álbum
calculado sobre la cuarta parte de las partidas no se presenta igual que uno completo.

Y una instantánea **sin álbum** —las que escribe el pipeline anterior— se pinta sin el bloque, no con un
error.

#### Scenario: la tira va agrupada
- GIVEN un jugador con muchas partidas de la misma categoría
- WHEN se muestra su álbum
- THEN cada categoría aparece una sola vez con su recuento, y las que no tiene no aparecen

#### Scenario: el emoji sale del payload
- GIVEN una instantánea cuyo catálogo asigna otro emoji a una categoría
- WHEN se pinta la tira
- THEN se usa el emoji de la instantánea, no uno fijo en la web

#### Scenario: el orden lo manda el catálogo, no las claves
- GIVEN un recuento cuyas claves llegan en otro orden
- WHEN se pinta la tira
- THEN el orden es el del catálogo publicado

#### Scenario: el ranking de belleza se muestra aparte del marcador
- GIVEN una temporada con jugadores clasificados en el álbum
- WHEN se pinta
- THEN aparece el ranking con puesto, nombre, tasa y tira, en el orden en que llega

#### Scenario: la cobertura se declara
- GIVEN una temporada con partidas sin patrón
- WHEN se pinta el álbum
- THEN dice cuántas se quedaron sin clasificar

#### Scenario: sin nadie clasificado se explica el porqué
- GIVEN una temporada en la que nadie alcanza el mínimo de partidas
- WHEN se pinta el álbum
- THEN se explica que aún no hay ranking, sin tabla vacía ni campeón inventado

#### Scenario: una instantánea sin álbum se pinta igual
- GIVEN una instantánea sin la clave del álbum
- WHEN se pinta la temporada
- THEN se pinta el resto de la vista, sin el bloque y sin errores

verified-by:
  - tests/slices/album-de-figuras/album.test.js
