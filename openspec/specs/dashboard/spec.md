# Spec de `dashboard`

Spec **viva** del dominio `dashboard` (ver `openspec/README.md`). Se edita directamente en la rama de cada cambio,
junto al código y los tests que la cumplen ([ADR 0009](../../decisions/0009-specs-vivas.md)). Cada Requirement
lleva en un comentario los change packs de los que sale, archivados en `openspec/changes/archive/`.

## Requirement: Las reglas que se aplican son legibles desde la web

<!-- origen: feat-reglas-explicadas (added) -->

Existe una vista en `/reglas` que explica **todas** las reglas del juego, agrupadas por eje. Cada regla dice
qué hace, **por qué existe** y en qué estado está.

Una regla sin motivo se lee como arbitrariedad, así que el motivo no es adorno: es parte del requisito.

#### Scenario: las reglas se agrupan por eje
- GIVEN el catálogo de reglas
- WHEN el grupo abre la página
- THEN las ve agrupadas por eje y no como una lista plana

#### Scenario: cada regla explica por qué existe
- GIVEN cualquier regla del catálogo
- WHEN se muestra
- THEN incluye su motivo, no solo su enunciado

#### Scenario: sin instantánea la página lo explica
- GIVEN que no hay instantánea de la que leer
- WHEN se abre la página
- THEN se explica el motivo en lugar de mostrar una página vacía

verified-by:
  - tests/slices/reglas-explicadas/test_reglas.py

## Requirement: El estado de una regla se muestra, y se distingue de si el grupo la votó

<!-- origen: feat-reglas-explicadas (added) -->

Cada regla lleva **dos marcadores independientes**:

- **estado**: `aplicada` · `acordada-sin-aplicar` · `sin-decidir`;
- **votada**: si el grupo la aprobó en el canal.

Son independientes a propósito, porque hoy hay reglas **aplicadas y no votadas** —la temporada 0 y los
umbrales de las medallas— y esconderlo sería el peor uso posible de esta página.

Una regla `sin-decidir` dice además **qué falta decidir**.

#### Scenario: una regla acordada sin implementar no se presenta como vigente
- GIVEN una regla decidida pero sin implementar
- WHEN se muestra
- THEN su estado dice que todavía no se aplica

#### Scenario: una regla aplicada y no votada lo declara
- GIVEN una regla que el cálculo usa y que el grupo no votó
- WHEN se muestra
- THEN aparece como aplicada y como no votada

#### Scenario: una regla sin decidir dice qué falta
- GIVEN una regla en discusión
- WHEN se muestra
- THEN incluye qué queda por decidir

verified-by:
  - tests/slices/reglas-explicadas/test_reglas.py

## Requirement: La vista de temporada muestra la clasificación y su contexto

<!-- origen: feat-clasificacion-de-temporada (added) -->

La vista de una temporada muestra el podio, la tabla completa y el contexto que la hace legible: cuántos
jugaron, cuántos días válidos tuvo, la media del grupo y qué jornada fue la más dura.

Y dice **cuándo se calculó**, porque es un dato derivado que puede quedar rancio si el cron falla
([ADR 0008](../../../decisions/0008-donde-vive-el-calculo.md)).

#### Scenario: una temporada poblada muestra su tabla
- GIVEN una temporada con clasificación materializada
- WHEN el grupo la abre
- THEN ve el podio y una fila por jugador con su posición y sus medias

#### Scenario: una temporada sin días válidos lo explica
- GIVEN una temporada cuyos días no alcanzan la muestra mínima
- WHEN el grupo la abre
- THEN la vista lo explica en lugar de mostrar una tabla vacía

#### Scenario: la vista dice cuándo se calculó
- GIVEN una clasificación materializada
- WHEN se muestra
- THEN indica la antigüedad del cálculo

verified-by:
  - tests/slices/clasificacion-de-temporada/test_clasificacion.py

## Requirement: El marcador es la puerta de entrada a la ficha de cada jugador

<!-- origen: feat-ficha-de-jugador (added) -->

La clasificación lista a todos los jugadores de la temporada y cada uno **enlaza a su ficha de esa misma
temporada**. Sin ese enlace la ficha existe y nadie la encuentra.

La ruta lleva la temporada, así que el enlace que alguien pega en el canal sigue hablando del mes del que
hablaba, y no del mes en que se abre.

#### Scenario: cada fila del marcador enlaza a la ficha
- GIVEN una temporada con clasificación
- WHEN se pinta el marcador
- THEN cada jugador enlaza a su ficha de esa temporada, con su identificador de Slack en la ruta

#### Scenario: un jugador sin resultados en la temporada lo dice
- GIVEN un identificador de jugador que no tiene resultados en la temporada abierta
- WHEN se abre su ficha
- THEN la vista lo declara y ofrece las temporadas en que sí jugó, en lugar de una página vacía

#### Scenario: un identificador desconocido no rompe la vista
- GIVEN un identificador que no aparece en ninguna temporada
- WHEN se abre su ficha
- THEN la vista lo declara sin fallar, porque con el fallback SPA cualquier ruta responde 200

verified-by:
  - tests/slices/ficha-de-jugador/ficha.test.js

## Requirement: Los umbrales que la web aplica salen de las reglas publicadas

<!-- origen: feat-resultado-del-dia (added) -->

Cuando una vista necesita un umbral del juego —la muestra mínima de un día, por ejemplo— lo lee de las
**reglas que viajan dentro de la instantánea**, y esas salen de la constante que usa el cálculo en Python.

Escribir el número en el JavaScript de la vista sería exactamente la divergencia que la página de reglas
existe para evitar: recalibrar en Python dejaría la web afirmando otra cosa.

Si la instantánea no trae el umbral, la vista **no lo inventa**: declara que no puede afirmarlo.

#### Scenario: recalibrar el umbral en Python cambia la vista sin tocarla
- GIVEN una jornada con tres resultados
- WHEN el umbral publicado es cinco
- THEN la vista dice que la jornada no cuenta
- WHEN el umbral publicado es tres
- THEN la vista dice que cuenta, sin cambiar el código de la vista

#### Scenario: sin umbral publicado no se afirma nada
- GIVEN una instantánea sin reglas
- WHEN se muestra el día
- THEN la vista declara que no puede afirmar si la jornada cuenta

verified-by:
  - tests/slices/resultado-del-dia/dia.test.js

## Requirement: El medallero acumula todas las temporadas

<!-- origen: feat-archivo-de-temporadas (added) -->

El archivo publica un medallero con las medallas de cada jugador **sumadas sobre todas las temporadas**,
desglosadas por tipo, y cuántas temporadas ha ganado. Ganar cuenta solo en temporadas cerradas: en una
abierta se va ganando, no se ha ganado.

#### Scenario: el medallero suma todas las temporadas
- GIVEN medallas repartidas en varias temporadas
- WHEN se muestra el medallero
- THEN cada jugador aparece con su total, su desglose por tipo y sus temporadas ganadas, de más a menos

#### Scenario: cada temporada del archivo enlaza a su marcador
- GIVEN el archivo con temporadas
- WHEN se pulsa una
- THEN se abre su marcador

#### Scenario: sin instantáneas el archivo lo declara
- GIVEN ninguna temporada materializada
- WHEN se abre el archivo
- THEN lo declara en lugar de mostrar una lista vacía

verified-by:
  - tests/slices/archivo-de-temporadas/archivo.test.js

## Requirement: Una ruta que no existe se declara, porque el fallback SPA no lo hará

<!-- origen: feat-ruta-invalida (added) -->

El Worker sirve la v2 con `not_found_handling: single-page-application`, así que **cualquier ruta devuelve
200**. Eso es lo que permite que `/t/2026-07` funcione sin servidor de rutas, y a la vez elimina el 404 que
avisaría de un enlace roto: sin él, una ruta mal escrita no falla, simplemente no pinta nada.

La detección es por tanto **del cliente**, y tiene que decir qué ruta se pidió y ofrecer la salida.

#### Scenario: una ruta desconocida se declara con la ruta pedida
- GIVEN una ruta que el router no reconoce
- WHEN se abre
- THEN la vista lo declara y muestra la ruta pedida, en lugar de una página en blanco

#### Scenario: un mes imposible no es una temporada
- GIVEN una ruta con un mes que no existe, como `2026-13`
- WHEN se resuelve
- THEN es ruta desconocida, no una temporada vacía

#### Scenario: una ruta de jugador mal formada no abre ficha
- GIVEN una ruta de jugador cuyo identificador no tiene forma de identificador de Slack
- WHEN se resuelve
- THEN es ruta desconocida

#### Scenario: la vista ofrece volver
- GIVEN la vista de ruta desconocida
- WHEN se muestra
- THEN ofrece volver a la temporada en curso

#### Scenario: una ruta desconocida no pertenece a ninguna sección
- GIVEN una ruta desconocida
- WHEN se pinta la navegación
- THEN ninguna sección aparece como actual

#### Scenario: la ruta pedida se muestra escapada
- GIVEN una ruta que contiene marcado
- WHEN se muestra
- THEN aparece como texto y no se interpreta

verified-by:
  - tests/slices/ruta-invalida/ruta.test.js

## Requirement: La tabla cruda permite comprobar que el marcador no se ha inventado nada

<!-- origen: feat-tabla-de-datos (added) -->

Hay una vista con **un resultado por fila, sin filtrar ni agregar**: fecha, jugador, jornada e intentos, de
la más reciente a la más antigua. Es la que se mira cuando alguien no se fía de una cifra, y por eso filtrar
sería justo lo que le quitaría el sentido.

Lleva una columna que la v1 no podía tener: **si esa fila cuenta para su temporada**, con el motivo cuando no
cuenta. Con las reglas nuevas, «¿por qué mi resultado del sábado no sale en el marcador?» tiene respuesta, y
su sitio es esta tabla.

#### Scenario: la tabla lista todos los resultados
- GIVEN resultados guardados
- WHEN se abre la tabla
- THEN hay una fila por resultado, sin filtrar ninguno

#### Scenario: el orden es estable y de lo más reciente a lo más antiguo
- GIVEN resultados de varios días
- WHEN se listan
- THEN salen de la fecha más reciente a la más antigua, y dos cargas dan la misma lista

#### Scenario: una fila que no cuenta lo declara con su motivo
- GIVEN una fila cuya jornada no está entre los días válidos de su temporada
- WHEN se muestra
- THEN declara que no cuenta y dice si es por fin de semana o por falta de muestra

#### Scenario: el fallo se distingue de un seis
- GIVEN un resultado sin resolver
- WHEN se muestra
- THEN aparece como fallo, no como un 7

verified-by:
  - tests/slices/tabla-de-datos/tabla.test.js


## Requirement: La temporada de un resultado la decide el modelo, también en la web

<!-- origen: feat-tabla-de-datos (added) -->

En la web, la temporada de una fecha se resuelve con **una única función** que lee el límite de las reglas
publicadas en la instantánea. Comparar el mes de la fecha con el identificador de una temporada está
prohibido: con la temporada 0 no coincide nunca y falla en silencio.

El borde de datos llama `mes` al mes de una fila, no `temporada`, para que el error no vuelva a estar a
un descuido de distancia.

#### Scenario: una fila anterior al límite pertenece a la temporada 0
- GIVEN una fila con fecha anterior al mes en que empiezan las temporadas numeradas
- WHEN se resuelve su temporada
- THEN es la temporada 0, y se compara con la instantánea de la 0

#### Scenario: sin el límite publicado no se adivina la temporada
- GIVEN una instantánea sin las reglas
- WHEN se resuelve la temporada de una fila
- THEN no se afirma ninguna

verified-by:
  - tests/slices/tabla-de-datos/tabla.test.js

## Requirement: Dos gráficos del mismo tipo se comparan mirándolos

<!-- origen: feat-escala-fija (added) -->

Las gráficas usan **escalas fijas**, no el máximo de lo que cada una dibuja. Un gráfico autoescalado no
miente en sus números pero sí en lo que sugiere de un vistazo, que es como se leen.

| Gráfico | Escala |
|---|---|
| Dificultad por jornada | 1 a 7 intentos, fija |
| Distribución de intentos | el mayor recuento de la temporada, común a todos sus jugadores |

Y la escala **se anuncia**: una escala fija que no se declara es indistinguible de una automática.

#### Scenario: la dificultad va en la escala de intentos
- GIVEN una jornada con su dificultad
- WHEN se pinta
- THEN su altura sale de la escala fija de 1 a 7, no del máximo del mes

#### Scenario: la misma dificultad se ve igual en dos temporadas
- GIVEN la misma dificultad en dos temporadas distintas
- WHEN se pintan
- THEN tienen la misma altura, y la temporada más fácil no toca el techo

#### Scenario: la distribución comparte escala entre jugadores
- GIVEN dos jugadores de la misma temporada, uno con muchas partidas y otro con pocas
- WHEN se pintan sus distribuciones
- THEN el mismo recuento da la misma altura y quien jugó poco se ve pequeño

#### Scenario: la escala se declara
- GIVEN un gráfico con escala fija
- WHEN se muestra
- THEN dice cuál es su escala

#### Scenario: un valor fuera de escala se recorta
- GIVEN un valor por encima del máximo de la escala
- WHEN se pinta
- THEN se recorta al máximo en lugar de desbordar

#### Scenario: sin datos no se divide por cero
- GIVEN una temporada sin recuentos
- WHEN se calcula la escala
- THEN sigue siendo utilizable y no produce alturas inválidas

verified-by:
  - tests/slices/escala-fija-comparable/escala.test.js

## Requirement: El álbum se muestra agrupado y con el vocabulario que publica el cálculo

<!-- origen: feat-album-de-figuras (added) -->

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

## Requirement: Las medallas de figura se ven con las demás

<!-- origen: feat-medallas-de-figuras (added) -->

La vista de temporada muestra las doce medallas del catálogo, no siete, y cada una con su icono. La ficha de
jugador las pinta en su palmarés igual que las otras.

El icono sale del mismo sprite. **`Fontaner@` se renombra a `Abstract@` también en el sprite**: la categoría
dejó de llamarse `caca` y el chiste de fontanero se quedó sin referente, así que un símbolo con el nombre
viejo era la última copia de un vocabulario ya cambiado.

#### Scenario: las doce medallas aparecen en la temporada
- GIVEN una temporada calculada
- WHEN se pinta el bloque de logros
- THEN aparecen también las cinco de figuras, con su nombre y su regla

#### Scenario: cada medalla de figura tiene su icono
- GIVEN las cinco medallas de figuras
- WHEN se pintan
- THEN cada una referencia un símbolo que existe en el sprite

verified-by:
  - tests/slices/medallas-de-figuras/medallas.test.js

## Requirement: La jornada en curso enseña lo que ha dibujado cada uno

<!-- origen: feat-figuras-de-la-jornada (added) -->

La vista `/hoy` muestra, junto a los intentos de cada participante, **el emoji de la figura que dibujó**.

La categoría **llega calculada** en la instantánea. El navegador no interpreta la cuadrícula: portar el
clasificador a JavaScript crearía una segunda verdad que divergiría en la primera recalibración.

Consecuencia declarada del reparto: quien publique **después de la última materialización** aparece con su
puntuación y sin figura. La vista lo dice —llega con la siguiente actualización— en lugar de dejar un hueco
sin explicar.

Una instantánea que no traiga las figuras se pinta como hasta ahora.

#### Scenario: cada participante lleva su figura
- GIVEN una jornada cuyas figuras están publicadas
- WHEN se pinta la vista de hoy
- THEN cada participante que dibujó aparece con su emoji

#### Scenario: quien llegó tarde no tiene figura, y se explica
- GIVEN un participante cuyo resultado es posterior a la última materialización
- WHEN se pinta la vista
- THEN aparece sin figura y la vista explica que llega con la siguiente actualización

#### Scenario: el emoji sale de la instantánea
- GIVEN una instantánea cuyo catálogo asigna otro emoji a una categoría
- WHEN se pinta la vista de hoy
- THEN se usa el emoji publicado, no uno fijo en la web

#### Scenario: sin figuras publicadas la vista no cambia
- GIVEN una instantánea sin las figuras de la jornada
- WHEN se pinta la vista de hoy
- THEN se pinta igual que antes, sin emojis y sin errores

verified-by:
  - tests/slices/figuras-de-la-jornada/hoy.test.js

## Requirement: El bloque de logros muestra el catálogo completo

<!-- origen: feat-logro-espejo-perfecto (modified) -->

La pestaña de temporada lista **todas** las medallas del catálogo, cada una con su nombre, su regla y su
icono. El número no se escribe en la especificación: cada logro nuevo lo dejaba desfasado.

Los dos catálogos —el del pipeline y el de la web— tienen que coincidir. Al añadir el espejo perfecto se vio
que nada lo impedía: cada lado tiene su lista y sus tests, así que el resumen diario podía anunciar un logro
que la pestaña de temporada no sabe explicar.

#### Scenario: el catálogo completo aparece en la temporada
- **WHEN** se pinta el bloque de logros de una temporada
- **THEN** aparecen todas las del catálogo con nombre, regla e icono
- **AND** el catálogo del pipeline y el de la web tienen las mismas claves

verified-by:
  - tests/slices/medallas-de-figuras/medallas.test.js
  - tests/slices/medallas-de-figuras/test_espejo_perfecto.py
  - tests/slices/medallas-de-figuras/test_medallas_de_figuras.py


## Requirement: La página de reglas explica el margen creciente y sus dos parámetros

<!-- origen: feat-margen-creciente (modified) -->

La regla de imputación se explica con el margen que crece: qué cuesta la primera falta, cuánto sube cada
siguiente y por qué. Los dos parámetros —el margen base y el paso— aparecen con su valor y su origen en el
código, como el resto.

Se explica también **por qué** creció: con un margen igual para cada falta la regla premiaba no aparecer, y eso
es lo que el grupo necesita entender para juzgar si la regla le parece justa.

#### Scenario: la página de reglas explica el margen creciente
- **WHEN** se pinta la regla de imputación
- **THEN** dice que el margen crece con las ausencias y muestra sus dos parámetros

verified-by:
  - tests/slices/clasificacion-de-temporada/test_clasificacion.py


## Requirement: La página de reglas enumera todas las categorías del álbum

<!-- origen: feat-categoria-culo (modified) -->

La regla del álbum dice cuántas categorías hay y las nombra con su emoji, y la de ponderación dice qué vale
cada una. Añadir una categoría sin tocar este texto dejaría al grupo leyendo que hay cuatro cuando hay cinco.

#### Scenario: la página de reglas enumera todas las categorías
- **WHEN** se pinta la regla del álbum
- **THEN** nombra todas las categorías vigentes con su emoji y su valor

verified-by:
  - tests/slices/album-de-figuras/album.test.js
  - tests/slices/clasificacion-de-figuras/test_album.py
  - tests/slices/clasificacion-de-figuras/test_orden_de_reglas.py
  - tests/slices/voz-de-la-jornada/test_memes.py


## Requirement: La pestaña de temporada explica qué es cada dibujo

<!-- origen: feat-categoria-culo (added) -->

Debajo de los logros hay un glosario con cada categoría del álbum: su emoji, qué forma la define, cuántos
puntos vale y cuántos han salido en el mes.

**Sale del catálogo publicado en la instantánea**, no de una lista escrita en la vista, así que una categoría
nueva en el pipeline aparece sola. Las descripciones sí viven en la vista, porque son texto de interfaz y no
dato del cálculo; una categoría sin descripción sale con su nombre, su valor y su recuento en lugar de
desaparecer, porque esa es la información que hay.

Sin catálogo el glosario no se pinta, en lugar de pintarse vacío.

#### Scenario: el glosario explica cada dibujo
- **WHEN** se pinta la pestaña de temporada
- **THEN** aparece cada categoría del catálogo con su emoji, sus puntos y cuántos han salido
- **AND** una categoría sin descripción sale con lo que se sepa de ella
- **AND** sin catálogo no se pinta nada

verified-by:
  - tests/slices/album-de-figuras/album.test.js
  - tests/slices/clasificacion-de-figuras/test_album.py
  - tests/slices/clasificacion-de-figuras/test_orden_de_reglas.py
  - tests/slices/voz-de-la-jornada/test_memes.py


## Requirement: La regla del Coleccionista no nombra un número de categorías

<!-- origen: feat-coleccionista-con-melocoton (modified) -->

El texto que el grupo lee dice **qué** hay que coleccionar y no **cuántas** cosas son: «una de cada figura que
haya salido en la temporada». Un número escrito a mano se queda desfasado cada vez que se añade una categoría,
y entonces la página explica una regla que el sistema ya no aplica.

#### Scenario: la regla del coleccionista no nombra un número
- **WHEN** se pinta la tarjeta del Coleccionista
- **THEN** su regla describe la condición sin fijar cuántas categorías hay

verified-by:
  - tests/slices/medallas-de-figuras/test_espejo_perfecto.py


## Requirement: El nivel del juego se deriva de la jornada anterior, y es una función pura

<!-- origen: feat-juego-de-la-jornada (added) -->

La web ofrece el nivel de un plataformas cuyos escenarios son las cuadrículas del grupo. El nivel se calcula
**a partir de los resultados ya publicados**, en JavaScript (`nivelDe`), y es una función pura de ellos:
mismos resultados, mismo nivel, sin reloj y sin azar. Quién lo ejecuta y cuándo lo decide `nivel-congelado`
(el cron, una vez por jornada).

Vive en JavaScript porque **no es una regla del juego sino un render**: no clasifica nada ni decide nada que
la tabla no diga ya. Un clasificador reimplementado en JavaScript sería una segunda verdad; dibujar una
cuadrícula que ya existe, no.

La jornada es la **anterior**, no la en curso: la de hoy sigue abierta, así que quien aún no haya jugado
aparecería sin cuadrícula y el nivel cambiaría bajo los pies de quien lo está jugando.

#### Scenario: el nivel usa la última jornada cerrada
- GIVEN resultados de varias jornadas, la última de ellas en curso
- WHEN se genera el nivel
- THEN los tramos son los de la jornada anterior a la última

#### Scenario: la misma jornada da el mismo nivel
- GIVEN los mismos resultados
- WHEN se genera el nivel dos veces
- THEN los dos niveles son idénticos

verified-by:
  - tests/slices/juego-de-la-jornada/nivel.test.js

## Requirement: La cuadrícula de cada jugador es el escenario de su tramo

<!-- origen: feat-juego-de-la-jornada (added) -->

Cada jugador ocupa **ocho columnas**, y las cinco centrales llevan su cuadrícula: un acierto es una
plataforma verde, una letra desplazada una naranja, y una letra ausente es hueco. Las filas se colocan **de
abajo arriba** —la fila 1 es el último intento, el que resolvió— así que el escenario se lee como se leyó la
partida: cuanto más arriba, más lejos estaba de acertar.

El ancho del nivel es `N * 8 + 5`, con las cinco columnas de cola para la meta. Y hay suelo bajo **todas** las
columnas: un hueco en el suelo es una caída por la que se pierde la partida sin haber fallado.

Bajo la cuadrícula de cada tramo va una etiqueta con el nombre del jugador y su nota.

#### Scenario: los verdes y amarillos se convierten en plataformas
- GIVEN un jugador con un patrón conocido
- WHEN se genera su tramo
- THEN cada acierto es una plataforma verde y cada letra desplazada una naranja, en su columna

#### Scenario: la última fila es la de abajo
- GIVEN un jugador que resolvió en varios intentos
- WHEN se genera su tramo
- THEN la fila 1 corresponde a su último intento

#### Scenario: el suelo cubre el nivel entero
- GIVEN una jornada cualquiera
- WHEN se genera el nivel
- THEN hay suelo en todas las columnas, de la primera a la última

verified-by:
  - tests/slices/juego-de-la-jornada/nivel.test.js

## Requirement: A los jugadores se les nombra como en el resto de la web

<!-- origen: feat-juego-de-la-jornada (added) -->

El nivel usa el nombre que la tabla guarda para cada jugador, que es el mismo que aparece en el marcador y en
las fichas. El prototipo leía los mensajes del canal y arrastraba dos defectos: identificadores de display
—`carlos.h` donde la web dice `Carlos H.`— y jugadores que se quedaban fuera, dos de doce en una jornada
medida. Leyendo la tabla no pasa ninguna de las dos cosas.

#### Scenario: el nombre del nivel es el de la tabla
- GIVEN un jugador cuyo nombre mostrado difiere de su identificador
- WHEN se genera su etiqueta
- THEN lleva el nombre de la tabla

verified-by:
  - tests/slices/juego-de-la-jornada/nivel.test.js

## Requirement: Lo que falta no rompe el nivel

<!-- origen: feat-juego-de-la-jornada (added) -->

Un resultado **sin patrón** no puede pintarse, así que su jugador se queda fuera y el resto del nivel se
genera igual; contarlo con un tramo vacío dejaría ocho columnas de nada en mitad del recorrido.

Una jornada **sin nadie** no produce nivel: la vista lo dice en lugar de pintar un escenario vacío.

El coleccionable de cada tramo **descansa sobre una plataforma** de ese tramo. Dónde exactamente lo decide el
repositorio y no el azar: el prototipo lo colocaba aleatoriamente, y este proyecto exige que la misma jornada
dé siempre el mismo nivel.

#### Scenario: un resultado sin patrón no genera tramo
- GIVEN una jornada donde un resultado no trae patrón
- WHEN se genera el nivel
- THEN ese jugador no aparece y los demás sí

#### Scenario: sin resultados no hay nivel
- GIVEN una jornada anterior sin resultados
- WHEN se genera el nivel
- THEN no se devuelve nivel

#### Scenario: el coleccionable se apoya en una plataforma
- GIVEN el tramo de un jugador con cuadrícula
- WHEN se coloca su coleccionable
- THEN hay una plataforma justo debajo

verified-by:
  - tests/slices/juego-de-la-jornada/nivel.test.js

## Requirement: La puntuación se comparte como se comparte el Wordle — la pega quien juega

<!-- origen: feat-juego-de-la-jornada (added) -->

Al terminar el nivel, la vista ofrece un texto con la jornada, el tiempo y las estrellas, y lo copia al
portapapeles. **Lo publica la persona, no el bot.**

Es el mismo modelo que ya usan los resultados de Wordle —cada uno pega el suyo— y hay dos razones para no
hacerlo de otra forma. La primera es que **la web no puede usar el token del bot**: es estática, sin servidor,
y el token vive solo en los secrets del workflow. Que el bot publicara la puntuación de alguien exigiría un
endpoint con el token dentro, expuesto a la web pública — una vía de escritura al canal desde fuera del
workflow, que es lo que las reglas de este repositorio prohíben.

El bot sí publica texto en el canal, pero **siempre pegado a un fichero**: el resumen diario es el
`initial_comment` de la subida de la captura, que cabe en su scope `files:write`. Lo que no tiene es
`chat:write`, para mensajes sueltos. Esa limitación no es la razón de este diseño; la razón es la anterior.

Y tiene una consecuencia que vale más que la comodidad: **un mensaje de Slack lleva autor de verdad**. Una
puntuación pegada por su dueño está firmada por quien la hizo, sin desplegable de «elige tu usuario» y sin
escritura anónima contra la base de datos. El texto se escribe con una cabecera estable y legible por si algún
día se quiere leer el ranking del canal, igual que se leen los resultados.

El texto es **función pura** del resultado de la partida: la misma partida da siempre el mismo texto.

#### Scenario: al terminar se ofrece compartir
- GIVEN una partida terminada con su tiempo y sus estrellas
- WHEN la vista recibe el final
- THEN ofrece un texto para compartir

#### Scenario: el texto lleva jornada, tiempo y estrellas
- GIVEN un resultado de partida
- WHEN se genera el texto
- THEN incluye el número de jornada, el tiempo y las estrellas sobre el total

#### Scenario: el mismo resultado da el mismo texto
- GIVEN el mismo resultado
- WHEN se genera el texto dos veces
- THEN los dos textos son idénticos

#### Scenario: sin partida terminada no se ofrece compartir
- GIVEN que nadie ha terminado el nivel
- WHEN se pinta la vista
- THEN no hay nada que compartir

verified-by:
  - tests/slices/juego-de-la-jornada/compartir.test.js

## Requirement: El pisotón rebota cinco casillas

<!-- origen: feat-juego-de-la-jornada (added) -->

Con la física del motor de Joel el salto máximo es 3,52 casillas, y una cuadrícula puede levantar una columna
de hasta 6, así que un escalón de 4 es un muro: el nivel del 24 de septiembre no se podía terminar. El dueño
probó primero una casilla más y la subió a **cinco en total**: con +1, la parte de Luis del 24 de septiembre
solo se pasaba rebotando en el último bloque de Juan con media casilla de margen, y en la práctica no salía.

En el aire, ↓ (o S) hace caer en picado; si al tocar suelo se pulsa Espacio dentro de una ventana corta, el
rebote sube **cinco casillas** desde donde se pisa, con un destello y chispas para que se note que salió. La
velocidad se deriva de la gravedad en lugar de escribirse a mano, así que sigue siendo cinco aunque cambie.

**Cinco casillas no salvan una pared de 6 desde el suelo** —17 de 221 jornadas la tienen—, pero sí desde lo
alto del tramo anterior, que es un reto y es lo que se pidió: el muro lo pone el grupo con sus propias
partidas, y le cuesta, porque una pared de altura *h* exige una cuadrícula de al menos *h* intentos. Y una de 5
se pasa desde el suelo por un margen de cinco píxeles que depende de la duración del fotograma: en una
pantalla de más refresco podría no pasarse.

#### Scenario: el rebote sube cinco casillas
- GIVEN la física del motor
- WHEN se calcula el salto del rebote
- THEN su altura máxima es de cinco casillas

#### Scenario: el rebote sale hacia delante
- GIVEN un rebote del pisotón
- WHEN sale bien
- THEN el personaje sale a velocidad de carrera hacia donde se pulsa, o hacia donde mira

#### Scenario: el pisotón pasa un muro que el salto normal no
- GIVEN un muro de cuatro casillas
- WHEN se intenta con el salto normal y con el pisotón
- THEN el normal se queda delante y el pisotón lo pasa

```yaml
checks:
  - type: regex
    file: v2/js/juego/motor.js
    pattern: 'rebote \? REBOTE_VELOCITY : JUMP_VELOCITY'
    describe: el motor usa el rebote al saltar dentro de la ventana del pisotón, no solo lo calcula
  - type: regex
    file: v2/js/juego/motor.js
    pattern: 'setVelocityX\(impulsoDelRebote\('
    describe: el rebote sale hacia delante, no solo hacia arriba
```

verified-by:
  - tests/slices/juego-de-la-jornada/pisoton.test.js

## Requirement: El tutorial del pisotón sale justo cuando hace falta

<!-- origen: feat-juego-de-la-jornada (added) -->

La primera vez que el jugador se acerca a un muro que el salto normal no sube, el juego se pausa y enseña un
tutorial breve: un GIF grabado del propio motor y los tres pasos del combo. Se enseña **una sola vez por
navegador** —si saliera cada día, al tercero sería un estorbo—, y la guía de controles tiene un enlace para
volver a verlo.

El sitio lo decide **el motor con su propia física**, no el generador: si el salto cambia, el aviso sigue
saliendo delante del muro correcto. Y cuenta como muro solo lo apilado desde el suelo sin huecos: un bloque
flotante se pasa por debajo, y avisar delante de él sería enseñar a resolver un problema que no existe.

La pausa no es cortesía: el tutorial sale con el cronómetro corriendo, justo delante de un muro, y leerlo
costaría segundos en el ranking.

#### Scenario: el tutorial sale antes del primer muro que pide pisotón
- GIVEN un nivel con un muro más alto que el salto normal
- WHEN el jugador se acerca a él por primera vez
- THEN se abre el tutorial

#### Scenario: el tutorial sale una sola vez
- GIVEN que el tutorial ya se vio en ese navegador
- WHEN el jugador llega a un muro que pide pisotón
- THEN no se abre solo

#### Scenario: el tutorial pausa la partida
- GIVEN el tutorial abierto
- WHEN pasa el tiempo
- THEN el cronómetro no avanza, y al cerrarlo la partida sigue

```yaml
checks:
  - type: regex
    file: v2/js/juego/motor.js
    pattern: 'dispatchEvent\(new CustomEvent\("superbros:pista-pisoton"'
    describe: el motor avisa a la página delante del primer muro que pide pisotón
  - type: regex
    file: v2/js/ui/juego.js
    pattern: 'addEventListener\(EVENTO_PISTA'
    describe: la página escucha ese aviso para abrir el tutorial
```

verified-by:
  - tests/slices/juego-de-la-jornada/tutorial.test.js

## Requirement: Las teclas del juego no mueven la página, y lo demás sí

<!-- origen: feat-juego-de-la-jornada (added) -->

Con el juego enfocado, el espacio y las flechas son del juego **también con Shift**. Phaser bloquea el scroll de
sus teclas, pero deja de hacerlo cuando va pulsado un modificador, y el pisotón se hace corriendo con Shift:
Shift + Espacio —«subir la página» en cualquier navegador— mandaba la página arriba justo al rebotar.

La rueda, el trackpad, la barra y Re Pág / Av Pág siguen moviendo la página con el juego enfocado —Phaser se
quedaba la rueda por defecto, y con el puntero encima del juego no se podía bajar—. Con el foco fuera del
juego, las flechas mueven la página y el personaje no se mueve, porque el motor escucha el teclado en el
lienzo y no en toda la ventana. Un clic en el juego le devuelve el foco, y mientras no lo tiene un aviso lo
dice.

**El bloqueo del scroll se engancha en el padre del lienzo, no en el lienzo.** Phaser descarta las teclas que
le llegan ya bloqueadas, y enganchado en el lienzo el bloqueo iba antes que él: el juego se quedaba sin
teclas. Se detectó repitiendo las pruebas de juego tras arreglar el scroll, no con la prueba del scroll, que
solo miraba la página.

#### Scenario: el pisotón con Shift no mueve la página
- GIVEN el juego enfocado
- WHEN se hace el pisotón corriendo con Shift
- THEN la página no se mueve y el personaje sí

#### Scenario: la rueda sigue moviendo la página
- GIVEN el juego enfocado
- WHEN se usa la rueda del ratón encima del juego
- THEN la página se mueve

#### Scenario: con el foco fuera, las flechas son de la página
- GIVEN el foco fuera del juego
- WHEN se pulsa una flecha
- THEN la página se mueve y el personaje no

```yaml
checks:
  - type: regex
    file: v2/js/ui/juego.js
    pattern: "lienzo\\.parentElement\\.addEventListener\\('keydown'"
    describe: el bloqueo del scroll va en el padre; en el lienzo le quitaba las teclas al juego
  - type: regex
    file: v2/js/juego/motor.js
    pattern: 'keyboard: \{ target: lienzo \}'
    describe: el motor escucha el teclado en el lienzo, no en toda la ventana
  - type: regex
    file: v2/js/juego/motor.js
    pattern: 'preventDefaultWheel: false'
    describe: la rueda no se la queda el juego
```

verified-by:
  - tests/slices/juego-de-la-jornada/teclado.test.js

## Requirement: La pestaña juega el último nivel congelado, no uno calculado al abrirla

<!-- origen: feat-nivel-congelado (added) -->

La pestaña del juego lee de `game_levels` **el último nivel congelado** —jornada, fecha y nivel— y lo juega;
el ranking que enseña es el de esa jornada. La web ya no ejecuta `nivelDe`: así el nivel de ayer no cambia
durante la madrugada porque llegue tarde una cuadrícula, y todos los tiempos de un ranking son sobre el mismo
escenario.

Si no hay ningún nivel congelado, o no se puede leer, la pestaña lo dice en lugar de pintar un escenario.

#### Scenario: se juega lo que dice game_levels
- GIVEN niveles congelados de varias jornadas
- WHEN se abre la pestaña
- THEN se lee el de jornada más alta y se juega ese, con su jornada y su fecha en la cabecera

#### Scenario: sin nivel congelado, se dice
- GIVEN ningún nivel congelado, o un fallo al leerlos
- WHEN se abre la pestaña
- THEN dice que todavía no hay nivel y no monta el lienzo

```yaml
checks:
  - type: regex
    file: v2/js/ui/juego.js
    pattern: 'const congelado = await nivelParaJugar\(niveles\);'
    describe: la pestaña juega el nivel que lee de la fuente de niveles congelados
  - type: regex
    file: v2/js/data/results.js
    pattern: "\\.from\\('game_levels'\\)[\\s\\S]*?\\.order\\('jornada', \\{ ascending: false \\}\\)[\\s\\S]*?\\.limit\\(1\\)"
    describe: se lee el último nivel congelado
```

verified-by:
  - tests/slices/nivel-congelado/web.test.js

## Requirement: Quien juega elige su nombre de la lista de jugadores, y la web lo recuerda

<!-- origen: feat-ranking-del-juego (added) -->

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

## Requirement: Cada llegada a la meta va al ranking del nivel

<!-- origen: feat-ranking-del-juego (added) -->

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

## Requirement: El ranking es uno por nivel y comparte puesto en el empate

<!-- origen: feat-ranking-del-juego (added) -->

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

## Requirement: El cron congela el nivel de la jornada de ayer a partir de las 02:00 de Madrid

<!-- origen: feat-nivel-congelado (added), renombra «El cron congela el nivel de la jornada de ayer a partir de las 04:00 de Madrid», fix-hora-de-congelar (modified) -->

Tras cada sincronización de `update_stats.yml`, `node tools/congelar_nivel.mjs` congela en `game_levels` el
nivel de la **última jornada asentada**: desde las **02:00** de Madrid, la de ayer; antes, la de anteayer
—que normalmente ya estará congelada—. La de hoy, nunca. El nivel lo genera el **mismo** `nivelDe` que la web
usaba, ejecutado con Node: una sola implementación.

La hora la decide el dueño. Primero se fijó a las 04:00, que recogía todas las llegadas tardías medidas; se
adelanta a las 02:00 para que el nivel nuevo llegue antes, **sabiendo lo que cuesta**: en 60 días, 1 de 490
cuadrículas llegó después de las 02:00 (a las 02:57), y una así ya no entra en el nivel de su jornada —sí en
todo lo demás, que no depende del nivel—. El reloj entra solo en el borde (`ahoraEnMadrid`), y
`--hoy`/`--hora` lo sustituyen.

El script dice qué congela —jornada, fecha, tramos— antes de escribir, o por qué no congela nada; con `--seco`
no escribe. Una jornada ya congelada no se reescribe: la consulta lo ve antes, y la inserción ignora el
duplicado si otra ejecución se adelantó.

#### Scenario: a las 02:00 se congela la de ayer
- GIVEN el día D a las 02:00 o después, sin nivel congelado para D-1
- WHEN corre el cron
- THEN guarda el nivel de `nivelDe` para D-1 con su jornada y su fecha

#### Scenario: antes de las 02:00 no
- GIVEN el día D antes de las 02:00
- WHEN corre el cron
- THEN no congela D-1; congela D-2 solo si no lo estaba

#### Scenario: lo ya congelado no se reescribe
- GIVEN una jornada congelada y una cuadrícula suya que llega tarde
- WHEN corre el cron otra vez
- THEN no escribe nada y el nivel sigue igual

#### Scenario: dice lo que hace
- GIVEN cualquier ejecución
- WHEN el script decide
- THEN escribe una línea con la jornada que congela antes de escribir, o con el motivo por el que no

```yaml
checks:
  - type: regex
    file: v2/js/domain/superbros.js
    pattern: "export const HORA_DE_CONGELAR = '02:00';"
    describe: la hora que decidió el dueño
  - type: regex
    file: .github/workflows/update_stats.yml
    pattern: '&& node tools/congelar_nivel\.mjs; then'
    describe: el cron congela el nivel en cada vuelta, después de sincronizar
  - type: regex
    file: v2/js/ui/juego.js
    pattern: 'se congela a las 02:00 del día siguiente'
    describe: la pestaña dice la hora de verdad cuando aún no hay nivel
```

verified-by:
  - tests/slices/nivel-congelado/congelar.test.js

## Requirement: Cada pestaña de la navegación lleva a su propia vista

<!-- origen: fix-enlace-de-la-pestana-del-juego (added) -->

El enlace de cada pestaña se construye con `rutaDe`, la inversa de `resolver`, y lleva a la vista de esa
pestaña, con la web montada en `/` o en `/2/`. La pestaña SuperWordleBros lleva a `/juego`.

Se escapó a producción: `resolver` conocía `/juego` pero `rutaDe` no tenía su caso, caía al `default` y el
enlace apuntaba a la portada. Escribir la URL funcionaba y pulsar la pestaña no. Por eso la verificación
recorre **todas** las pestañas: una nueva que se olvide de su ruta da rojo aquí.

#### Scenario: la pestaña del juego lleva al juego
- GIVEN la navegación pintada desde cualquier sección, con base `/` o `/2/`
- WHEN se lee el enlace de SuperWordleBros
- THEN apunta a `<base>juego` y `resolver` lo lleva a la vista del juego

#### Scenario: ninguna pestaña cae a la portada por defecto
- GIVEN todas las pestañas de la navegación
- WHEN se resuelven sus enlaces
- THEN cada una lleva a una vista distinta

```yaml
checks:
  - type: regex
    file: v2/js/router.js
    pattern: "case VISTAS\\.JUEGO:\\s+return '/juego';"
    describe: la ruta canónica del juego existe para construir el enlace de la pestaña
```

verified-by:
  - tests/slices/juego-de-la-jornada/navegacion.test.js

## Requirement: La tarjeta de la temporada presenta el empate como empate

<!-- origen: fix-empate-en-cabeza (added) -->

La tarjeta de cada temporada en `/temporadas` nombra a **todos** los que comparten el primer puesto. En curso,
dice «empate en cabeza» en lugar de «va ganando»; cerrada, dice «campeones» y que comparten el primer puesto,
en lugar de coronar al primero de la lista. Con un único primero, la tarjeta no cambia.

#### Scenario: en curso y empatados
- GIVEN una temporada en curso con dos jugadores en el puesto 1
- WHEN se pinta su tarjeta
- THEN dice empate en cabeza y nombra a los dos

#### Scenario: cerrada y empatados
- GIVEN una temporada cerrada con dos jugadores en el puesto 1
- WHEN se pinta su tarjeta
- THEN dice campeones, nombra a los dos y dice que comparten el primer puesto

#### Scenario: un solo primero no cambia
- GIVEN una temporada cerrada con un único primero
- WHEN se pinta su tarjeta
- THEN dice campeón y nombra solo a ese jugador

verified-by:
  - tests/slices/archivo-de-temporadas/archivo.test.js

## Requirement: La pestaña dice cuándo el nivel ya está cerrado

<!-- origen: feat-juego-en-la-temporada (added) -->

Si alguien termina el nivel en una pestaña abierta antes de que se congelara el siguiente, `registrar_tiempo`
lo rechaza por nivel cerrado. La página no enseña entonces el aviso genérico de fallo: dice que ese nivel ya
está cerrado y que recargue para jugar el nuevo. El texto para compartir sigue apareciendo.

#### Scenario: una marca de un nivel cerrado lo dice
- GIVEN un nombre elegido y la API del ranking que rechaza la marca por nivel cerrado
- WHEN se llega a la meta
- THEN el estado dice que el nivel ya está cerrado y que se recargue

```yaml
checks:
  - type: regex
    file: v2/js/ui/juego.js
    pattern: 'nivel ya está cerrado/.test\('
    describe: la pestaña distingue el rechazo por nivel cerrado
```

verified-by:
  - tests/slices/ranking-del-juego/marcas.test.js

## Requirement: La clasificación del juego de la temporada se pinta sin recalcular

<!-- origen: feat-juego-en-la-temporada (added) -->

El bloque SUPERWORDLEBROS de la temporada lee `carga.juego` tal cual lo dejó el pipeline: no ordena, no
puntúa y no lee `game_times`. Así la web y el resumen del canal enseñan la misma tabla.

#### Scenario: cada fila sale con sus cifras
- GIVEN una clasificación del juego con empates
- WHEN se pinta el bloque
- THEN cada fila lleva puesto, nombre, puntos, niveles y victorias, y el puesto compartido solo se escribe una
  vez

verified-by:
  - tests/slices/marcador-del-juego/marcador.test.js

## Requirement: Solo se congelan los niveles de días que cuentan para la temporada

<!-- origen: feat-juego-en-la-temporada (added) -->

El cron congela únicamente jornadas **laborables con al menos cinco jugadores**, las mismas que cuentan para la
temporada y que puntúan en el juego. Una jornada de fin de semana o de un laborable con menos jugadores no crea
nivel, así que no cierra el que está en juego: **el nivel del viernes se juega el sábado, el domingo y el
lunes**, y todas esas marcas cuentan. El del lunes se congela el martes a partir de las 02:00 y cierra el del
viernes.

El mínimo de cinco jugadores es el de `tools/seasons.py::MUESTRA_MINIMA_DEL_DIA`; el script del cron, en
JavaScript, usa la misma cifra, y un test comprueba que las dos coinciden.

#### Scenario: un sábado con partidas no crea nivel
- GIVEN el nivel del viernes congelado y resultados del sábado
- WHEN corre el cron el domingo a las 02:00 o después
- THEN no se congela nada y el nivel del viernes sigue siendo el último

#### Scenario: un laborable con cuatro jugadores no crea nivel
- GIVEN una jornada laborable con cuatro jugadores
- WHEN corre el cron al día siguiente
- THEN se congela la anterior que cuenta, no esa

#### Scenario: los dos mínimos son el mismo
- GIVEN el mínimo de jugadores del pipeline y el del script
- WHEN se comparan
- THEN son iguales

```yaml
checks:
  - type: regex
    file: v2/js/domain/superbros.js
    pattern: 'return jornadaDelNivel\(deDiasQueCuentan\(resultados\)'
    describe: el cron solo congela días que cuentan
```

verified-by:
  - tests/slices/nivel-congelado/congelar.test.js

## Requirement: El ranking de cada nivel pone las estrellas por delante del tiempo

<!-- origen: feat-juego-en-la-temporada (added) -->

El ranking bajo el juego ordena de más a menos estrellas y, con las mismas estrellas, de menor a mayor tiempo.
Comparten puesto solo dos marcas con las mismas estrellas y el mismo tiempo. Cuando una partida no mejora la
marca, la página dice cuál es la marca que se queda, con sus estrellas y su tiempo.

#### Scenario: más estrellas va delante aunque sea más lento
- GIVEN una marca de 9 estrellas en 12,03 s y otra de 13 estrellas en 13 s
- WHEN se pinta el ranking del nivel
- THEN la de 13 estrellas va primera

#### Scenario: si no mejora, se dice la marca que se queda
- GIVEN una partida que no mejora la marca
- WHEN la base de datos responde
- THEN la página dice las estrellas y el tiempo de la marca que se queda

verified-by:
  - tests/slices/ranking-del-juego/marcas.test.js

## Requirement: La tarjeta de la temporada enseña los tres campeones desde octubre

<!-- origen: feat-tres-campeones (added) -->

Desde octubre de 2026, la tarjeta de cada temporada en `/temporadas` tiene un hueco por competición —MARCADOR,
SUPERWORDLEBROS, FIGURAS—, cada uno con su corona («CAMPEÓN», «CAMPEONES», «VA GANANDO» o «EMPATE EN
CABEZA»), sus nombres enlazados y su cifra: la media, los puntos del juego y los puntos por partida de las
figuras. Una competición sin nadie clasificado dice «sin campeón». Antes de octubre la tarjeta no cambia.

El medallero desglosa la columna de temporadas ganadas por competición, nombrando solo las que tienen algún
título.

#### Scenario: la tarjeta de octubre enseña las tres
- GIVEN una temporada 2026-10 cerrada con un campeón en cada competición
- WHEN se pinta su tarjeta
- THEN aparecen MARCADOR, SUPERWORDLEBROS y FIGURAS, cada una con su campeón y su cifra

#### Scenario: una competición vacía dice sin campeón
- GIVEN una temporada 2026-10 sin clasificación del juego
- WHEN se pinta su tarjeta
- THEN el hueco del SUPERWORDLEBROS dice «sin campeón» y los otros dos salen con su campeón

```yaml
checks:
  - type: regex
    file: v2/js/ui/temporadas.js
    pattern: 'const huecos = competiciones.map\(\(c\) => hueco\(t, c, varias\)\)'
    describe: "un hueco por competición"
```

verified-by:
  - tests/slices/archivo-de-temporadas/archivo.test.js

## Requirement: La pestaña Info explica cómo se juega y enseña las reglas vigentes

<!-- origen: feat-pestana-info (added) -->

La pestaña **Info** (`/info`) sustituye a Reglas. Tiene cuatro apartados, en este orden:

1. **Cómo se juega**: se juega la palabra de https://lapalabradeldia.com, se pega el resultado en el canal
   #wordle-line y el bot hace el resto.
2. **Las competiciones**: el marcador, el SuperWordleBros, el álbum de figuras y las medallas, un párrafo cada
   una.
3. **Lo que publica el bot**: el resumen de cada noche y la victoria la noche del último día laborable.
4. **Reglas vigentes**: las reglas del catálogo de la temporada en curso con estado «aplicada» y que no son
   históricas (la temporada 0), agrupadas por eje, sin marcas de estado ni de votación.

La explicación **no escribe cifras a mano**: los números solo aparecen en las reglas, que los leen de las
constantes del cálculo, así que la explicación no puede contradecirlas. `/reglas` y `/t/<AAAA-MM>/reglas`
llevan a `/info`: ningún enlace viejo da error.

#### Scenario: Info explica cómo se juega, las competiciones y el bot
- GIVEN la instantánea de la temporada en curso
- WHEN se abre /info
- THEN hay cuatro apartados en orden, con el enlace a lapalabradeldia.com y el nombre del canal

#### Scenario: la explicación no lleva números
- GIVEN la pestaña Info pintada
- WHEN se mira el texto de los tres primeros apartados
- THEN no hay ninguna cifra

#### Scenario: solo salen las reglas vigentes
- GIVEN un catálogo con reglas aplicadas, propuestas sin decidir y reglas históricas
- WHEN se pintan las reglas de Info
- THEN solo salen las aplicadas no históricas, y no hay marcas de «sin decidir» ni de votación

#### Scenario: los enlaces viejos llevan a Info
- GIVEN las rutas /reglas y /t/2026-09/reglas
- WHEN se resuelven
- THEN llevan a la vista Info, y la pestaña de la navegación dice «Info»

verified-by:
  - tests/slices/reglas-explicadas/info.test.js

## Requirement: La web nombra con su apodo a quien lo tiene declarado, sin cambiar su identidad

<!-- origen: feat-apodos-en-la-web (added) -->

Una tabla declarada (`v2/js/domain/apodos.js`) asigna un apodo de presentación a un nombre de jugador. Toda
vista de la v2 que pinta el nombre de un jugador pinta su apodo si lo tiene, escapado como cualquier nombre;
la etiqueta de su tramo en el SuperWordleBros también, al montar el nivel y sin cambiar el nivel guardado.
La identidad no cambia: rutas de ficha, valor del selector del juego y marcas siguen usando el id de Slack.
El bot de Slack no usa apodos.

#### Scenario: el apodo sustituye al nombre en cada vista
- GIVEN un jugador con apodo declarado que aparece en la temporada, hoy, su ficha, el archivo, los datos y el juego
- WHEN se pinta cada vista
- THEN sale el apodo y no el nombre a secas

#### Scenario: la identidad no cambia
- GIVEN un jugador con apodo
- WHEN se pinta su enlace a la ficha y su opción en el selector del juego
- THEN siguen llevando su id de Slack

#### Scenario: el nivel del juego pinta el apodo
- GIVEN un nivel congelado con la etiqueta «Carrillo  4/6»
- WHEN se prepara para el motor
- THEN la etiqueta lleva el apodo y el nivel original no cambia

verified-by:
  - tests/slices/apodos-en-la-web/apodos.test.js
  - tests/slices/apodos-en-la-web/test_slack.py


## Requirement: Info tiene un apartado para debatir las reglas

<!-- origen: feat-debate-de-reglas (added), feat-pestana-debate (modified), feat-propuestas-votables (modified) -->

Las propuestas se publican al enviarlas y cada una se vota a favor o en contra, eligiendo quién eres: un voto
por persona y propuesta, cambiable, con el recuento y los nombres a la vista. Una propuesta rechazada por el dueño
no se ve.

#### Scenario: las propuestas se votan
- **WHEN** alguien elige su nombre y vota una propuesta a favor o en contra
- **THEN** su voto se guarda y la propuesta enseña cuántos y quiénes están a favor y en contra

#### Scenario: una propuesta se publica al momento
- **WHEN** alguien envía una propuesta
- **THEN** se le dice que está publicada y aparece en el debate

verified-by:
  - tests/slices/debate-de-reglas/debate.test.js

## Requirement: La ficha pinta el bloque «Cómo juegas»

<!-- origen: feat-indicadores-de-juego (added) -->

La ficha de un jugador enseña eficiencia, apertura, suerte y acierto más milagroso de la temporada, comparados
con el grupo. Con pocas partidas dice cuántas faltan; sin indicadores en la instantánea dice que no están
disponibles. El bloque no habla de trampas.

#### Scenario: el bloque sale en la ficha
- GIVEN una instantánea con indicadores del jugador
- WHEN se abre su ficha
- THEN se ven los cuatro indicadores

#### Scenario: el bloque no habla de trampas
- WHEN se pinta el bloque
- THEN no contiene «trampa», «tramposo» ni «sospecha»

verified-by:
  - tests/slices/indicadores-de-juego/indicadores.test.js
