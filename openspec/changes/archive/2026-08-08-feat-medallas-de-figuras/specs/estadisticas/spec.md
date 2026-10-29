# Deltas de `estadisticas` — feat-medallas-de-figuras

## ADDED Requirements

### Requirement: Cinco medallas premian el dibujo, con umbrales medidos

El catálogo incluye cinco medallas que dependen de la figura: **Ornitólog@**, **Arquitect@**, **Florista**,
**Abstract@** y **Coleccionista**. Las cuatro primeras exigen un número de partidas de una categoría; la
última, al menos una de cada.

Sus umbrales se fijan **por rareza medida**, y están puestos justo por debajo del máximo que alguien ha
llegado a hacer: ahí un logro es difícil sin ser imposible. Los del brief anterior no valen — se midieron
con un clasificador que luego se desmintió.

Los recuentos son **los del álbum**, no un segundo recuento: la tira de un jugador y su medalla tienen que
decir lo mismo.

Un jugador sin cuadrículas guardadas no gana ninguna, y eso no afecta a los demás.

#### Scenario: alcanzar el umbral de una categoría da su medalla
- GIVEN un jugador con suficientes partidas de una categoría en la temporada
- WHEN se calculan las medallas
- THEN gana la medalla de esa categoría

#### Scenario: quedarse a una partida no la da
- GIVEN un jugador con una partida menos que el umbral
- WHEN se calculan las medallas
- THEN no la gana

#### Scenario: Coleccionista exige las cuatro categorías
- GIVEN un jugador con tres categorías distintas y muchas partidas
- WHEN se calculan las medallas
- THEN no gana Coleccionista; sí la gana quien tiene al menos una de cada

#### Scenario: el recuento es el del álbum
- GIVEN una temporada cuyo álbum cuenta N partidas de una categoría para un jugador
- WHEN se calcula su medalla de esa categoría
- THEN se usa ese mismo N

#### Scenario: sin cuadrícula no hay medalla de figura
- GIVEN un jugador cuyas partidas no tienen patrón
- WHEN se calculan las medallas
- THEN no gana ninguna de figura, y quien sí tiene patrones conserva las suyas

verified-by:
  - tests/slices/medallas-de-figuras/test_medallas_de_figuras.py

### Requirement: El resumen diario deriva la temporada del modelo

El resumen diario decide de qué temporada son las medallas con **la misma función que el resto del
sistema**, no recortando el prefijo de la fecha.

Recortar la fecha funciona solo mientras toda temporada sea un `AAAA-MM`. Con la temporada 0 devuelve un
identificador que no existe, y las medallas del día salen calculadas sobre una temporada vacía. Es la
tercera vez que la misma causa raíz aparece en este repositorio.

Y el resumen lee la columna del patrón: sin ella, ninguna medalla de figura puede anunciarse nunca.

#### Scenario: una fecha anterior al límite pertenece a la temporada 0
- GIVEN un resumen cuya última jornada es anterior al inicio de las temporadas numeradas
- WHEN se decide la temporada de las medallas
- THEN es la temporada 0, no el mes de esa fecha

#### Scenario: el resumen lee el patrón
- GIVEN el resumen diario leyendo resultados
- WHEN consulta la tabla
- THEN pide también la columna del patrón, de modo que las medallas de figura pueden calcularse

verified-by:
  - tests/slices/medallas-de-figuras/test_medallas_de_figuras.py
