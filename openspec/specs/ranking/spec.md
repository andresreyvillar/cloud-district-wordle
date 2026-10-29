# Spec de `ranking`

Spec **viva** del dominio `ranking` (ver `openspec/README.md`). Se edita directamente en la rama de cada cambio,
junto al código y los tests que la cumplen ([ADR 0009](../../decisions/0009-specs-vivas.md)). Cada Requirement
lleva en un comentario los change packs de los que sale, archivados en `openspec/changes/archive/`.

## Requirement: Una temporada es un mes natural y se reinicia el día 1

<!-- origen: feat-temporada-mensual (added) -->

La temporada de un resultado es el mes de su fecha, en formato `AAAA-MM`. El marcador se reinicia el día 1:
un resultado del día 1 pertenece a la temporada nueva, sin periodo de gracia ni solapamiento.

El grupo la decidió por votación: 6 a favor, 0 en contra.

#### Scenario: un resultado del día 1 pertenece a la temporada nueva
- GIVEN un resultado con fecha del día 1 de un mes
- WHEN se determina su temporada
- THEN es la de ese mes, no la del anterior

#### Scenario: la temporada sale de la fecha del puzzle
- GIVEN un resultado publicado con retraso
- WHEN se determina su temporada
- THEN es la del puzzle, no la del día en que se publicó

verified-by:
  - tests/slices/temporada-mensual/test_temporada_mensual.py

## Requirement: Una temporada son sus días laborables con muestra suficiente

<!-- origen: feat-temporada-mensual (added) -->

Un día forma parte de una temporada si cumple **las dos** condiciones:

1. es de lunes a viernes;
2. lo jugaron al menos cinco personas.

Los dos filtros son independientes y hacen falta los dos: el primero excluye el fin de semana por regla; el
segundo, los laborables en que el grupo tampoco jugó (festivos, agosto). Sin el segundo, una ausencia
penalizaría en un día en que nadie estaba.

La definición de día laborable es **una sola en el proyecto** (`tools/calendario.py`), compartida con las
medallas: dos definiciones de lo mismo divergen, y aquí una divergencia cambia quién gana el mes.

#### Scenario: el fin de semana no forma parte de la temporada
- GIVEN una temporada con resultados en sábado y en domingo
- WHEN se determinan sus días
- THEN esos días no están

#### Scenario: un día de pocos jugadores no forma parte de la temporada
- GIVEN un día laborable jugado por menos de cinco personas
- WHEN se determinan los días de la temporada
- THEN ese día no está

#### Scenario: una temporada puede quedar vacía y sigue existiendo
- GIVEN un mes en el que ningún día alcanza la muestra mínima
- WHEN se lista el archivo de temporadas
- THEN la temporada aparece con cero días, en lugar de desaparecer

verified-by:
  - tests/slices/temporada-mensual/test_temporada_mensual.py

## Requirement: La temporada en curso se deriva de los datos, no del reloj

<!-- origen: feat-temporada-mensual (added) -->

La temporada en curso es la más reciente con resultados; las anteriores están cerradas. El cálculo no
consulta la fecha del sistema, y por eso es reproducible con datos fijos (§10 del protocolo).

#### Scenario: la más reciente con datos está en curso
- GIVEN resultados que abarcan varios meses
- WHEN se listan las temporadas
- THEN la más reciente consta como en curso y las demás como cerradas

#### Scenario: dos cálculos sobre los mismos datos coinciden
- GIVEN un conjunto de resultados
- WHEN se calcula el modelo dos veces, y una de ellas con las filas en otro orden
- THEN el resultado es idéntico

verified-by:
  - tests/slices/temporada-mensual/test_temporada_mensual.py

## Requirement: Un parámetro publicado es el mismo que usa el cálculo

<!-- origen: feat-reglas-explicadas (added) -->

Cuando una regla se enuncia con un número —cinco jugadores de muestra mínima, quince partidas para Fondista,
margen de 0,5— ese número **se lee de la constante que el cálculo usa**, nunca de una copia.

Es lo único que impide que la página de reglas mienta: un umbral recalibrado en el código y no en el texto
produciría una explicación falsa en la que el grupo confiaría.

```yaml
checks:
  - type: cli-command
    describe: cada parámetro del catálogo coincide con la constante que documenta
```

#### Scenario: el parámetro mostrado es el del cálculo
- GIVEN una regla con un umbral
- WHEN se compara el valor publicado con la constante que usa el cálculo
- THEN son el mismo valor

#### Scenario: recalibrar un umbral cambia lo publicado
- GIVEN un umbral que cambia en el código
- WHEN se vuelve a materializar
- THEN la regla publicada muestra el valor nuevo sin tocar su texto

verified-by:
  - tests/slices/reglas-explicadas/test_reglas.py

## Requirement: Las reglas viajan con la temporada

<!-- origen: feat-reglas-explicadas (added) -->

La instantánea de una temporada incluye las reglas con las que se calculó, así que una temporada cerrada
conserva las suyas aunque las de hoy hayan cambiado.

#### Scenario: una temporada cerrada conserva sus reglas
- GIVEN una temporada materializada con unos parámetros
- WHEN los parámetros cambian y se materializa otra temporada
- THEN la instantánea de la primera sigue mostrando los parámetros con los que se calculó

verified-by:
  - tests/slices/reglas-explicadas/test_reglas.py

## Requirement: La clasificación se calcula sobre los días de la temporada, no sobre las partidas jugadas

<!-- origen: feat-clasificacion-de-temporada (added) -->

Todo día válido de la temporada tiene una nota para cada jugador. Si jugó, la suya; si no:

```
imputado(día) = min( max( dificultad(día), media_personal ) + margen , 7 )
```

donde `dificultad(día)` es la media del grupo ese día y `media_personal` la media del jugador contando
**solo sus días jugados** — usar la ya imputada volvería la fórmula circular.

Cada pieza responde a un fallo medido: `dificultad` hace que faltar un día fácil apenas penalice;
`max(…, media_personal)` impide que faltar mejore la media, que ocurría en 9 ocasiones del histórico;
`margen` impide que callarse un mal resultado salga mejor que publicarlo; `min(…, 7)` pone el tope en el
fallo.

El denominador es el mismo para todos, así que las medias se comparan sin reglas añadidas y **no hace falta
un umbral mínimo de días para clasificar**.

#### Scenario: los jugadores se ordenan por su media imputada
- GIVEN una temporada con varios jugadores
- WHEN se calcula la clasificación
- THEN salen ordenados por media imputada de menor a mayor

#### Scenario: faltar nunca mejora la media
- GIVEN un jugador cuya media personal es peor que la dificultad de un día
- WHEN falta ese día
- THEN su media final no baja respecto a haberlo jugado con su media habitual

#### Scenario: la ausencia en un día difícil penaliza más
- GIVEN dos jugadores idénticos que faltan un día cada uno, uno fácil y otro difícil
- WHEN se calcula la clasificación
- THEN el que faltó el día difícil queda por detrás

#### Scenario: jugar poco no da ventaja
- GIVEN un jugador con muy buena media que solo juega unos pocos días
- WHEN se calcula la clasificación
- THEN no adelanta a quien jugó todos los días con media parecida

#### Scenario: el empate se rompe por participación
- GIVEN dos jugadores con la misma media imputada
- WHEN se ordena la tabla
- THEN va delante el que jugó más días

verified-by:
  - tests/slices/clasificacion-de-temporada/test_clasificacion.py

## Requirement: La imputación es auditable

<!-- origen: feat-clasificacion-de-temporada (added) -->

Cada fila de la clasificación publica sus **días jugados** y su **media real** además de la imputada, y el
detalle por jornada dice si esa nota se jugó o se imputó.

Sin eso la tabla es una caja negra: el grupo no podría comprobar de dónde sale la diferencia entre lo que
jugó y lo que puntúa.

#### Scenario: cada fila muestra lo jugado y lo imputado
- GIVEN una clasificación calculada
- WHEN se inspecciona una fila
- THEN incluye días jugados, media real, media imputada y el detalle por jornada marcando lo imputado

verified-by:
  - tests/slices/clasificacion-de-temporada/test_clasificacion.py

## Requirement: Las temporadas están numeradas desde un límite, y antes del límite todo es la temporada 0

<!-- origen: feat-temporada-cero (modified) -->

Existe una fecha límite. **Todo lo jugado antes es la temporada 0**, un solo bloque con todo el histórico.
Desde el límite, cada mes natural es una temporada y lleva su número de orden: el mes del límite es la 1, el
siguiente la 2.

El número de orden **se deriva** del límite, no se almacena, así que no puede desincronizarse del modelo.

El identificador de un mes sigue siendo `AAAA-MM`, para que un enlace compartido en el canal diga de qué mes
habla; el de la temporada 0 es `0`.

#### Scenario: lo anterior al límite es la temporada 0
- GIVEN un resultado con fecha anterior al límite
- WHEN se determina su temporada
- THEN es la temporada 0, sea de qué mes sea

#### Scenario: el mes del límite es la temporada 1
- GIVEN un resultado del mes del límite
- WHEN se determina su temporada y su número de orden
- THEN es ese mes, y su número de orden es 1

#### Scenario: la temporada 0 es un solo bloque
- GIVEN resultados repartidos en varios meses anteriores al límite
- WHEN se listan las temporadas
- THEN aparece **una sola** entrada para todo ese periodo, no una por mes

verified-by:
  - tests/slices/temporada-mensual/test_temporada_mensual.py

## Requirement: La temporada 0 se rige por las reglas que estaban en vigor cuando se jugó

<!-- origen: feat-temporada-cero (added) -->

La clasificación de la temporada 0 replica las reglas de la v1 (`js/script.js`):

| Regla | Temporada 0 (legacy) | Temporada numerada |
|---|---|---|
| Jornadas que cuentan | **todas** las que tengan algún resultado | laborables con ≥5 jugadores |
| Media | de las partidas jugadas | con las ausencias imputadas |
| Mínimo para clasificar | **5 partidas** (`MIN_GAMES_FOR_BEST_AVG`) | ninguno: la imputación ya lo hace |

Aplicar hacia atrás las reglas nuevas cambiaría el resultado de un partido ya jugado. Y está medido lo que
pasaría: de los 159 días que quedarían filtrando, **siete de veinte jugadores tendrían más del 70% de la
temporada imputada** —a quien se incorporó el 22 de julio se le contarían 156 ausencias desde noviembre—, lo
que produce un artefacto y no una clasificación.

**Única desviación del legacy, y es deliberada:** se agrupa por **identidad de Slack** y no por nombre
mostrado. El legacy agrupaba por nombre, lo que partía en dos a quien se hubiera renombrado — y con los datos
reales eso coronaba a la mitad de una identidad partida (9 partidas de un lado, 6 del otro). El arreglo de
identidad es una corrección de datos, no un cambio de regla.

La instantánea **declara que no está imputada**, para que la vista no presente su media como comparable con
la de las numeradas.

#### Scenario: la temporada 0 no imputa ausencias
- GIVEN un jugador que solo jugó unos pocos días del periodo anterior al límite
- WHEN se calcula la clasificación de la temporada 0
- THEN su media es la de sus partidas jugadas, y no se le añade ninguna ausencia

#### Scenario: la temporada 0 no filtra jornadas
- GIVEN una jornada de fin de semana y otra con dos jugadores, las dos anteriores al límite
- WHEN se determinan los días de la temporada 0
- THEN las dos cuentan, como hacía la v1

#### Scenario: por debajo del mínimo del legacy no se clasifica
- GIVEN un jugador con menos de cinco partidas en la temporada 0
- WHEN se calcula la clasificación
- THEN aparece en la tabla sin puesto, aunque su media sea la mejor

#### Scenario: la instantánea declara el criterio
- GIVEN la instantánea de la temporada 0
- WHEN se inspecciona
- THEN dice que su clasificación no está imputada

#### Scenario: una temporada numerada sí imputa
- GIVEN una temporada posterior al límite con un jugador que faltó un día
- WHEN se calcula su clasificación
- THEN ese día se le imputa

verified-by:
  - tests/slices/temporada-mensual/test_temporada_mensual.py
  - tests/slices/clasificacion-de-temporada/test_clasificacion.py

## Requirement: El archivo guarda quién ganó cada temporada

<!-- origen: feat-archivo-de-temporadas (added) -->

Con temporadas mensuales el histórico deja de ser una lista de partidas y pasa a ser un **palmarés
colectivo**. El archivo lista cada temporada materializada con su campeón, su media y sus totales, de la más
reciente a la más antigua.

Una temporada **en curso no tiene campeón**: tiene quien va ganando. Y la temporada 0 va marcada como
**bloque histórico jugado con otras reglas**, para que su media de 181 jornadas sin imputar no se lea como
comparable con la de un mes.

#### Scenario: el archivo ordena de la más reciente a la más antigua
- GIVEN varias temporadas materializadas
- WHEN se abre el archivo
- THEN aparecen ordenadas por número de orden descendente, con la temporada 0 al final

#### Scenario: una temporada cerrada muestra su campeón
- GIVEN una temporada cerrada con clasificación
- WHEN se muestra en el archivo
- THEN muestra a quien la ganó con su media, y sus jornadas, jugadores y resultados

#### Scenario: una temporada en curso no corona a nadie
- GIVEN una temporada cuyo estado es en curso
- WHEN se muestra en el archivo
- THEN aparece marcada como abierta y su primero se presenta como quien va ganando, no como campeón

#### Scenario: la temporada 0 se marca como bloque histórico
- GIVEN la temporada 0
- WHEN se muestra en el archivo
- THEN queda marcada como bloque histórico jugado con otras reglas

#### Scenario: una temporada vacía no desaparece
- GIVEN un mes sin ningún día con muestra suficiente
- WHEN se muestra el archivo
- THEN esa temporada aparece con cero jornadas y sin campeón

verified-by:
  - tests/slices/archivo-de-temporadas/archivo.test.js

## Requirement: El álbum ordena por tasa de figuras, no por volumen

<!-- origen: feat-clasificacion-de-figuras (added) -->

Cada temporada publica un segundo ranking, **independiente del de puntuación**: el álbum de figuras. La
puntuación de un jugador es la **proporción de sus partidas clasificadas que dejaron una figura
reconocible** (loro, flores o geométrico), no el recuento absoluto.

Medido sobre la temporada 0: el recuento absoluto corona a quien más juega y el ponderado por rareza corona
al segundo de la tabla de puntuación, que es justo lo que este eje existe para evitar.

Hace falta un **mínimo de 5 partidas clasificadas** para tener puesto. Con 3, el líder es alguien con un
100% de tres partidas; con 5, 8 o 10 el líder es el mismo. Quien no llega al mínimo aparece igual, sin
puesto.

El orden es determinista: tasa descendente, a igualdad más figuras delante, y a igualdad de figuras por
nombre.

#### Scenario: la tasa mide figuras por partida
- GIVEN un jugador con partidas clasificadas
- WHEN se calcula su puntuación del álbum
- THEN es la proporción de esas partidas con figura reconocible, y jugar más no la sube por sí solo

#### Scenario: un abstracto rebaja la tasa
- GIVEN un jugador con una partida abstracta
- WHEN se calcula su álbum
- THEN la partida aparece en su recuento y le baja la tasa, en lugar de desaparecer

#### Scenario: por debajo del mínimo no hay puesto
- GIVEN un jugador con menos partidas clasificadas que el mínimo
- WHEN se ordena el álbum
- THEN aparece sin puesto y no encabeza el ranking, aunque su tasa sea la más alta

#### Scenario: el empate se rompe siempre igual
- GIVEN dos jugadores con la misma tasa
- WHEN se ordena el álbum
- THEN va delante quien aportó más figuras, y a igualdad el orden es por nombre

#### Scenario: sin patrones no hay ranking
- GIVEN una temporada en la que ninguna partida tiene patrón
- WHEN se calcula el álbum
- THEN sale vacío y declarado como tal, sin campeón de belleza

verified-by:
  - tests/slices/clasificacion-de-figuras/test_album.py

## Requirement: Los empates comparten puesto

<!-- origen: feat-empates-comparten-puesto (added) -->

Dos jugadores con la misma media de temporada ocupan **el mismo puesto**, y el siguiente salta tantos
números como gente haya empatada por delante.

El desempate interno —más días jugados, luego el nombre— **sigue existiendo** y decide el orden en que se
listan, porque el resultado tiene que ser el mismo en cada ejecución. Lo que deja de hacer es fabricar una
diferencia de puesto que no existe.

Dos medias cuentan como iguales cuando coinciden **con los decimales que se publican**: si a la vista son el
mismo número, separarlas es incomprensible para quien lee.

#### Scenario: dos con la misma media comparten puesto
- GIVEN dos jugadores con idéntica media de temporada
- WHEN se calcula la clasificación
- THEN los dos tienen el mismo número de puesto

#### Scenario: después de un empate, el puesto salta
- GIVEN dos jugadores empatados en el segundo puesto
- WHEN se calcula la clasificación
- THEN el siguiente ocupa el cuarto

#### Scenario: el orden de la lista sigue siendo determinista
- GIVEN dos jugadores empatados
- WHEN se calcula la clasificación dos veces con las filas en distinto orden
- THEN se listan en el mismo orden las dos veces

#### Scenario: una diferencia invisible es un empate
- GIVEN dos medias que solo difieren por debajo de los decimales publicados
- WHEN se calcula la clasificación
- THEN comparten puesto

#### Scenario: quien no clasifica no comparte puesto
- GIVEN alguien por debajo del mínimo para clasificar
- WHEN se calcula la clasificación
- THEN sigue sin puesto

verified-by:
  - tests/slices/empates-comparten-puesto/test_empates.py

## Requirement: El desempate ordena la lista, no reparte puestos

<!-- origen: feat-empates-comparten-puesto (modified) -->

Cuando dos jugadores tienen la misma media, el desempate —más días jugados, luego el nombre— **decide en qué
orden se listan** y ya no en qué puesto quedan.

Antes decidía las dos cosas, y eso fabricaba una diferencia que no existe: quien juega un día más no ha
hecho una temporada mejor que quien empata con él, ha jugado más. Si esa participación tiene que valer, lo
hace la imputación, que ya está dentro de la media.

El desempate sigue siendo obligatorio: sin él, el orden de la lista dependería del orden en que la base de
datos devuelve las filas, y dos ejecuciones darían resultados distintos.

#### Scenario: el desempate ordena
- GIVEN dos jugadores con la misma media y distinto número de días jugados
- WHEN se calcula la clasificación
- THEN va antes en la lista el que jugó más días

#### Scenario: pero comparten puesto
- GIVEN esos mismos dos jugadores
- WHEN se mira su número de puesto
- THEN es el mismo para los dos

verified-by:
  - tests/slices/empates-comparten-puesto/test_empates.py
  - tests/slices/clasificacion-de-temporada/test_clasificacion.py

## Requirement: El álbum ordena por puntos por partida, y no todas las figuras valen igual

<!-- origen: feat-figuras-ponderadas (modified) -->

La puntuación del álbum es la **media de puntos por partida clasificada**, con las figuras valoradas según
lo raras que son:

| Figura | Puntos | Frecuencia medida |
|---|---|---|
| 📐 geométrico | 3 | 7,4% |
| 🦜 loro | 2 | 13,6% |
| 🌷 flores | 1 | 46,5% |
| 🌀 abstracto | 0 | 32,4% |

Antes todas las figuras reconocibles valían lo mismo y la puntuación era la proporción de partidas con
figura. **Decisión del dueño el 2026-08-09.**

Lo que **no** cambia, y es lo que sostiene el criterio: sigue siendo **por partida**. Ese punto se midió al
elegirlo — el total corona a quien más juega, que es un ranking de asistencia con otro nombre.

La escala se queda en 3/2/1 aunque la rareza medida dé una proporción de unos 6:3:1, porque con 5/3/1 el
podio es idéntico: la escala corta se explica igual y se recuerda mejor.

**Coste declarado.** Con todas las figuras valiendo lo mismo, el podio de belleza no compartía a nadie con
el de puntuación — que es la razón de existir de este segundo eje. Ponderando, el segundo clasificado en
puntuación entra en el podio de belleza. Se acepta como decisión del dueño, no porque la medida lo
recomiende.

La escala **se publica en el catálogo** de la instantánea y la vista la anuncia, porque un número como
«1,14» no dice nada sin saber contra qué se mide.

#### Scenario: un geométrico vale más que un loro, y un loro más que una flor
- GIVEN tres jugadores con el mismo número de partidas, uno solo de geométricos, otro solo de loros y otro
  solo de flores
- WHEN se ordena el álbum
- THEN quedan en ese orden

#### Scenario: la puntuación sigue siendo por partida
- GIVEN dos jugadores con la misma mezcla de figuras y uno con diez veces más partidas
- WHEN se calcula su puntuación
- THEN es la misma para los dos

#### Scenario: un abstracto no suma y baja la media
- GIVEN un jugador con una partida abstracta
- WHEN se calcula su puntuación
- THEN esa partida cuenta en el denominador y no aporta puntos

#### Scenario: la escala viaja con los datos
- GIVEN el catálogo de categorías de una instantánea
- WHEN se lee
- THEN cada categoría dice cuántos puntos vale, de modo que la vista no tiene su propia tabla

verified-by:
  - tests/slices/clasificacion-de-figuras/test_album.py
  - tests/slices/album-de-figuras/album.test.js

## Requirement: El álbum deshace sus empates con la tabla de puntuación

<!-- origen: feat-desempate-del-album (modified) -->

Cuando dos jugadores tienen los mismos puntos por partida, el álbum los ordena por su **media en la tabla de
puntuación**: delante quien mejor puntúa. Solo comparten puesto quienes no se distinguen **ni por ahí**.

Antes compartían puesto en cuanto empataban en la puntuación del álbum, y eso producía una tabla sin segundo
ni cuarto puesto. **Decisión del dueño el 2026-08-09.**

El problema no era de redondeo: en una temporada de cinco jornadas jugadas por todo el mundo, los puntos por
partida solo pueden tomar seis valores, así que siete de ocho jugadores empataban — y con **colecciones
idénticas**, las mismas figuras en el mismo número. Ningún criterio sacado del propio álbum podía
separarlos.

Se consideró y **se descartó** premiar a quien publica antes: la marca de tiempo disponible es la de la
escritura del cron, que trabaja por lotes cada hora. Medido sobre el histórico, solo el **34%** de los
resultados de una jornada tienen minuto distinto y en **ninguna** jornada son todos distintos. Ordenar por
ahí premiaría a quien cayó del lado bueno de una hora en punto.

**Precio declarado:** acopla los dos ejes. El álbum existe para premiar a otra gente que el marcador, y
ahora el marcador decide sus empates — pero solo cuando el criterio propio ya no distingue.

#### Scenario: dos con los mismos puntos por partida se ordenan por el marcador
- GIVEN dos jugadores con colecciones idénticas y distinta media de puntuación
- WHEN se ordena el álbum
- THEN va delante quien mejor puntúa, y ocupan puestos distintos

#### Scenario: sin nada que los separe, siguen compartiendo puesto
- GIVEN dos jugadores idénticos también en la tabla de puntuación
- WHEN se ordena el álbum
- THEN comparten puesto

#### Scenario: el desempate no altera el criterio principal
- GIVEN un jugador con más puntos por partida y peor media de puntuación que otro
- WHEN se ordena el álbum
- THEN va delante el de más puntos por partida

verified-by:
  - tests/slices/clasificacion-de-figuras/test_album.py

## Requirement: Una cuadrícula simétrica es geométrica, aunque tenga demasiada tinta

<!-- origen: feat-figuras-simetricas (modified) -->

El geométrico se reconoce por **dos vías**, y basta una:

| Vía | Condición | Cuándo se evalúa |
|---|---|---|
| escasez de tinta | densidad ≤ 0,40 y como mucho un amarillo | antes de la flor, como siempre |
| **espejo** | todas las filas del cuerpo son iguales leídas al revés | **en último lugar** |

Antes solo existía la primera, y dejaba fuera dibujos regulares con masa: un arco de densidad 0,60 salía
abstracto. Lo que hace geométrico a un geométrico es la forma; la escasez de tinta era un sustituto de la
regularidad, y no la mide.

**El espejo se consulta al final, cuando ninguna otra regla ha reconocido nada.** Es lo que hace el cambio
seguro, y no es un detalle de orden: unos pétalos son simétricos por naturaleza, así que un espejo evaluado
antes de la flor le robaría la categoría a flores legítimas. Puesto al final, el espejo **solo puede ascender
abstractos** — ninguna cuadrícula que hoy tiene figura la pierde. La alternativa medida, exigirle al espejo
como mucho un amarillo igual que a la otra vía, protege lo mismo y rescata dos casos menos.

El espejo se calcula sobre el **cuerpo** —la cuadrícula sin la banda verde final—, igual que el resto de los
rasgos. La banda es el suelo del dibujo y es simétrica siempre, así que incluirla concedería el espejo a
cualquier partida resuelta.

**La simetría es exacta: cero celdas rotas.** Admitir una sola llevaría la cobertura del 1,1% al 7,7% de
producción y costaría una ficha del conjunto dorado. La medida acompaña esta decisión en el proposal, porque
el reparto mejora y el acuerdo empeora: es el canje que ya tumbó a un candidato anterior.

Solo cuenta la simetría respecto al **eje vertical**. Un dibujo regular respecto a la diagonal —una
escalera— no cumple el espejo y sigue saliendo abstracto: es una limitación conocida.

```yaml
checks:
  - type: cli-command
    command: python3 tools/calibrate_figures.py
    expect: acuerdo ≥ 24 fichas y geométrico por debajo del 13% del reparto en producción
```

#### Scenario: un dibujo simétrico con mucha tinta es geométrico
- GIVEN una cuadrícula resuelta cuyas filas son todas palíndromas y cuya densidad supera 0,40
- WHEN se clasifica
- THEN la categoría es geométrico

#### Scenario: una sola celda rota niega el espejo
- GIVEN una cuadrícula por lo demás simétrica en la que una celda rompe el espejo
- WHEN se clasifica
- THEN la categoría es abstracto

#### Scenario: el espejo no le quita la flor a unos pétalos simétricos
- GIVEN una cuadrícula simétrica que cumple lo que define una flor
- WHEN se clasifica
- THEN la categoría es flores

#### Scenario: el espejo no le quita el loro a un loro simétrico
- GIVEN una cuadrícula simétrica que cumple lo que define un loro
- WHEN se clasifica
- THEN la categoría es loro

#### Scenario: ninguna cuadrícula con figura pierde su figura
- GIVEN el conjunto de patrones reales
- WHEN se clasifican con el espejo y sin él
- THEN las únicas que cambian de categoría son las que salían abstractas

#### Scenario: acertar a la primera no es un espejo
- GIVEN una cuadrícula que es solo la banda verde final
- WHEN se clasifica
- THEN la categoría es abstracto, porque no hay cuerpo

#### Scenario: sin resolver no hay figura, aunque haya simetría
- GIVEN una cuadrícula simétrica que no resuelve la palabra
- WHEN se clasifica
- THEN la categoría es abstracto

#### Scenario: la simetría se mide sin contar el suelo
- GIVEN dos cuadrículas iguales salvo que una resuelve la palabra y la otra no
- WHEN se clasifican
- THEN la banda verde final no es lo que concede el espejo

verified-by:
  - tests/slices/clasificacion-de-figuras/test_simetria.py

## Requirement: El orden de las reglas de figura está versionado por jornada

<!-- origen: feat-geometria-antes-que-loro (added) -->

La geometría se comprueba antes que el loro y, si acierta, no se avanza: una pirámide con un amarillo suelto
es un geométrico y no un loro.

El cambio **no es retroactivo**. Rige a partir de una jornada determinada, inclusive, y las cuadrículas
anteriores conservan la categoría que tenían cuando se jugaron — igual que la temporada 0 se rige por las
reglas que estaban en vigor entonces.

El motivo es que el geométrico puntúa más que el loro: aplicarlo hacia atrás subiría la puntuación de quien
tenga esas partidas ya jugadas y ya comentadas, reescribiendo un álbum que el grupo ya ha visto. Medido, el
reorden movería 42 de las 1.706 cuadrículas del histórico.

Clasificar un patrón **sin jornada** usa el orden histórico, porque las herramientas que lo hacen fuera de
contexto —la calibración contra el etiquetado humano— se hicieron con las reglas de entonces.

#### Scenario: la geometría se decide antes que el loro
- **WHEN** se clasifica una cuadrícula de una jornada a partir de la que rige el orden nuevo
- **THEN** si es geométrica se devuelve geométrico sin comprobar el loro

#### Scenario: el cambio de orden no es retroactivo
- **WHEN** se clasifica una cuadrícula anterior a esa jornada
- **THEN** conserva la categoría del orden antiguo
- **AND** clasificar sin jornada también usa el orden antiguo

verified-by:
  - tests/slices/clasificacion-de-figuras/test_orden_de_reglas.py
  - tests/slices/figuras-de-la-jornada/test_ultima_jornada.py


## Requirement: El espejo reconocible gana a la flor desde el corte de reglas

<!-- origen: feat-espejo-gana-a-la-flor (modified) -->

A partir del corte, una cuadrícula que es un espejo reconocible se clasifica como geométrica **antes** de
comprobar la flor: un palíndromo perfecto es más difícil que unos pétalos.

Antes del corte se conserva el orden histórico, en el que el espejo se consulta en último lugar y por tanto
solo asciende abstractos. Esa invariante existía para no robarle la figura a flores ya jugadas, y el corte la
protege mejor de lo que la protegía el orden.

Un espejo **reconocible** exige un mínimo de filas de cuerpo, y es **el mismo mínimo que pide el logro**: con
umbrales distintos, un espejo de dos filas —simetría por casualidad— le quitaba la categoría a una flor
legítima. El predicado vive en un solo sitio.

#### Scenario: desde el corte el espejo gana a la flor
- **WHEN** una cuadrícula a partir del corte es un espejo reconocible y además cumple la regla de la flor
- **THEN** se clasifica como geométrica
- **AND** la misma cuadrícula antes del corte sigue siendo flor

#### Scenario: el espejo de una o dos filas no cuenta
- **WHEN** una cuadrícula simétrica tiene el cuerpo por debajo del mínimo
- **THEN** no se le reconoce el espejo, ni para la categoría ni para el logro

verified-by:
  - tests/slices/clasificacion-de-figuras/test_orden_de_reglas.py
  - tests/slices/clasificacion-de-figuras/test_simetria.py
  - tests/slices/figuras-de-la-jornada/test_ultima_jornada.py
  - tests/slices/medallas-de-figuras/test_espejo_perfecto.py


## Requirement: Al cerrar un mes su instantánea se actualiza

<!-- origen: fix-cierre-de-temporada (modified) -->

Una ejecución normal del pipeline materializa la temporada en curso **y la última que se cerró**.

Hace falta porque el estado —«en curso» o «cerrada»— viaja dentro de la instantánea y no se calcula al
pintarla: una temporada que sale del filtro de «en curso» sin volver a escribirse conserva para siempre el
estado del último día que lo estuvo, y la web la anuncia abierta después de haber cerrado.

Basta con la última cerrada: las anteriores ya se escribieron estando cerradas. El histórico completo sigue
detrás de una opción explícita, porque recalcularlo cada hora son 181 jornadas para arreglar una etiqueta.

#### Scenario: al cerrar un mes su instantánea se actualiza
- **WHEN** una temporada deja de estar en curso porque empieza la siguiente
- **THEN** se rematerializa también ella
- **AND** las temporadas cerradas anteriores no se recalculan

verified-by:
  - tests/slices/temporada-mensual/test_temporada_mensual.py


## Requirement: El castigo por faltar crece con las ausencias

<!-- origen: feat-margen-creciente (modified) -->

La nota que se imputa a un día no jugado lleva un margen que **crece con el número de ausencias** del jugador
en la temporada: la primera falta suma el margen base y cada siguiente un paso más, siempre con el tope del
fallo.

Un margen igual para cada falta seguía premiando no aparecer, porque el suelo de la propia media protege a
quien casi no juega: medido sobre un mes real, quien jugó 1 jornada de 21 quedaba por delante de quien jugó 18.

El paso se eligió midiendo: concentra el castigo en quien no aparece sin mover a quien falta poco por un
imprevisto, que es la mitad de la regla que no se puede romper.

#### Scenario: faltar mucho cuesta más que faltar poco
- **WHEN** dos jugadores faltan un número muy distinto de días
- **THEN** el coste por ausencia crece con las ausencias
- **AND** quien juega casi todos los días queda por delante de quien juega uno solo

#### Scenario: faltar un solo día apenas penaliza
- **WHEN** alguien falta una vez en el mes
- **THEN** el margen es el base, igual que antes del cambio

verified-by:
  - tests/slices/clasificacion-de-temporada/test_clasificacion.py


## Requirement: La sincronización horaria no depende de un solo reloj

<!-- origen: fix-reloj-de-repuesto (added) -->

El workflow de datos se despierta desde **dos relojes independientes**: el planificador de la forja y un cron
externo que lo lanza por API.

Hace falta porque el planificador de la forja no garantiza sus ventanas: su documentación admite que los
trabajos en cola pueden descartarse, y medido sobre este repositorio salían 5 o 6 de las 24 esperadas al día,
con huecos de hasta seis horas. Mover el cron a otro minuto —lo único que la forja recomienda— se probó y no
mejoró.

Despertar el workflow dos veces **no duplica nada**: la ingesta no reescribe resultados ya guardados y la
materialización actualiza en lugar de insertar. El disparador externo está apagado mientras no tenga
credencial, y un fallo suyo no puede afectar a la web que sirve el mismo proceso.

#### Scenario: el pipeline tiene un reloj de repuesto
- **WHEN** el planificador de la forja descarta la ventana horaria
- **THEN** el reloj independiente despierta el mismo workflow
- **AND** sin credencial configurada el disparador no hace nada

verified-by:
  - tests/slices/temporada-mensual/disparador.test.js
  - tests/slices/temporada-mensual/test_temporada_mensual.py


## Requirement: Un fallo transitorio de red no cuesta la ejecución

<!-- origen: fix-reloj-de-repuesto (added) -->

Las lecturas y escrituras de la instantánea se reintentan unas cuantas veces con espera creciente antes de
rendirse. Un error que no es de red falla a la primera.

Medido: 4 de 200 ejecuciones del cron murieron por un timeout de red, y sin reintento cada una costaba la hora
completa.

#### Scenario: un fallo de red se reintenta
- **WHEN** una operación contra la base falla por un problema transitorio
- **THEN** se reintenta antes de rendirse
- **AND** un error de credenciales o de esquema falla a la primera

verified-by:
  - tests/slices/temporada-mensual/disparador.test.js
  - tests/slices/temporada-mensual/test_temporada_mensual.py


## Requirement: Reconocer un espejo y premiarlo piden cuerpos distintos

<!-- origen: feat-espejo-de-dos-filas (modified) -->

Una cuadrícula simétrica de **dos filas de cuerpo** se clasifica como geométrica, pero **no** se lleva el logro
del espejo perfecto, que exige más.

Son dos decisiones separadas: la categoría dice «esto es un espejo» y el logro dice «esto casi no pasa nunca».
Con el umbral del logro bajado a dos lo tendrían nueve de veintitrés jugadores y dejaría de distinguir a nadie.

Una sola fila de cuerpo no cuenta para ninguna de las dos cosas: una banda sobre el suelo es palíndroma por
casualidad y no por dibujo, y son siete de los veinte espejos del histórico.

#### Scenario: el espejo de una fila no cuenta
- **WHEN** una cuadrícula simétrica tiene una sola fila de cuerpo
- **THEN** no se le reconoce el espejo

#### Scenario: reconocer un espejo y premiarlo piden cuerpos distintos
- **WHEN** una cuadrícula simétrica tiene dos filas de cuerpo
- **THEN** se clasifica como geométrica
- **AND** no se lleva el logro del espejo perfecto

verified-by:
  - tests/slices/clasificacion-de-figuras/test_album.py
  - tests/slices/clasificacion-de-figuras/test_orden_de_reglas.py
  - tests/slices/figuras-de-la-jornada/test_ultima_jornada.py
  - tests/slices/medallas-de-figuras/test_espejo_perfecto.py
  - tests/slices/medallas-de-figuras/test_medallas_de_figuras.py
  - tests/slices/resumen-diario-compuesto/test_resumen.py


## Requirement: La cadencia de sincronización es un requisito medible

<!-- origen: feat-cadencia-de-sincronizacion (added) -->

Que los datos estén frescos deja de depender de que un planificador ajeno sea puntual y pasa a expresarse con
dos números: **ejecuciones mínimas por día** y **silencio máximo entre ejecuciones**. No se pide puntualidad.

El criterio se evalúa sobre el histórico de ejecuciones y el veredicto no depende de cuándo se mire: el
instante de referencia entra por parámetro y nunca se lee del reloj.

Los silencios se cuentan también en los bordes —desde el comienzo del día hasta la primera ejecución y desde
la última hasta el instante de referencia—, porque midiendo solo entre ejecuciones un grupo apretado seguido
de un día entero de nada pasaba por bueno.

El día del instante de referencia no se juzga por su recuento: se presume en curso, y exigirle el mínimo a
media mañana suspendería siempre al día de hoy. Sus silencios sí cuentan.

Sin ejecuciones no se afirma que la cadencia se cumpla: la ausencia de datos no es un aprobado.

#### Scenario: la cadencia es un requisito medible
- **WHEN** se juzga la sincronización
- **THEN** el veredicto sale de los dos números y del histórico, no de una impresión

#### Scenario: un día flojo se nombra
- **WHEN** un día completo no alcanza el mínimo
- **THEN** se dice cuál

#### Scenario: el silencio se mide también en los bordes
- **WHEN** las ejecuciones se agrupan y dejan el resto del día sin ninguna
- **THEN** no se cumple, aunque el recuento diario baste

#### Scenario: sin ejecuciones no se inventa un veredicto
- **WHEN** no hay ejecuciones que juzgar
- **THEN** no se afirma que la cadencia se cumpla

verified-by:
  - tests/slices/cadencia-de-sincronizacion/test_cadencia.py


## Requirement: La forma de las tres filas de abajo tiene su propia categoría

<!-- origen: feat-categoria-culo (added) -->

Una cuadrícula cuyas tres últimas filas dibujan un verde central entre dos huecos, sobre `G.G.G` y sobre el
suelo, se clasifica en una categoría propia con su emoji, y puntúa como el geométrico.

Se reconoce **por el patrón y no por los rasgos**, porque no es una propiedad agregada —cuántos verdes, cuánta
densidad— sino una forma concreta en un sitio concreto. Los extremos de la fila de arriba son libres: lo que da
la silueta es el verde central entre sus dos huecos.

Se comprueba **después del espejo**, así que una cuadrícula que sea las dos cosas se queda en geométrico. Eso
deja la categoría en minoría a propósito: de las cinco cuadrículas del histórico que dibujan la forma, dos son
espejos.

#### Scenario: el culo es su propia categoría
- **WHEN** las tres últimas filas dibujan la forma
- **THEN** se clasifica en su categoría, cuenta como figura reconocible y puntúa como el geométrico
- **AND** los extremos de la fila de arriba no cambian el veredicto
- **AND** la fila del medio y el suelo sí se exigen

#### Scenario: el espejo gana al culo
- **WHEN** una cuadrícula es a la vez espejo reconocible y dibuja la forma
- **THEN** se clasifica como geométrico

verified-by:
  - tests/slices/album-de-figuras/album.test.js
  - tests/slices/clasificacion-de-figuras/test_album.py
  - tests/slices/clasificacion-de-figuras/test_orden_de_reglas.py
  - tests/slices/voz-de-la-jornada/test_memes.py


## Requirement: Un primer puesto compartido tiene varios líderes y varios campeones

<!-- origen: fix-empate-en-cabeza (added) -->

Cuando varios jugadores comparten el primer puesto de una temporada —misma media publicada, que es cuando la
clasificación les da el mismo puesto—, **todos** son quienes van ganando mientras está en curso y **todos** son
campeones cuando se cierra. El archivo de temporadas trae `lideres` y `campeones` como listas con todos los del
primer puesto, y el medallero suma la temporada ganada a cada campeón. `lider` y `campeon` se conservan como el
primero de esas listas, para quien solo necesite uno.

#### Scenario: un empate en cabeza da dos líderes
- GIVEN una temporada en curso con dos jugadores en el puesto 1
- WHEN se construye el archivo
- THEN `lideres` tiene a los dos

#### Scenario: un título compartido da dos campeones
- GIVEN una temporada cerrada con dos jugadores en el puesto 1
- WHEN se construyen el archivo y el medallero
- THEN `campeones` tiene a los dos, y cada uno suma una temporada ganada

verified-by:
  - tests/slices/archivo-de-temporadas/archivo.test.js

## Requirement: El SuperWordleBros se clasifica en el mes por puntos por puesto en cada nivel

<!-- origen: feat-juego-en-la-temporada (added), feat-victoria-el-ultimo-dia (modified) -->

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

## Requirement: La temporada enseña la clasificación del juego debajo del álbum de figuras

<!-- origen: feat-juego-en-la-temporada (added) -->

La vista de temporada pinta, justo después del álbum de figuras y antes de las estadísticas, un bloque
SUPERWORDLEBROS con la clasificación de `carga.juego`: puesto —escrito solo cuando cambia—, nombre escapado,
puntos, niveles jugados y victorias, y una línea que explica la escala y cuántos niveles lleva el mes. Sin
clasificación, o con una instantánea sin la clave `juego`, el bloque no se pinta.

#### Scenario: el bloque va entre el álbum y las estadísticas
- GIVEN una instantánea con clasificación del juego
- WHEN se pinta la temporada
- THEN el bloque SUPERWORDLEBROS aparece después de ÁLBUM DE FIGURAS y antes de ESTADÍSTICAS

#### Scenario: sin clasificación no hay bloque
- GIVEN una instantánea con `juego.clasificacion` vacía, u otra sin la clave `juego`
- WHEN se pinta la temporada
- THEN no aparece el bloque SUPERWORDLEBROS

```yaml
checks:
  - type: regex
    file: v2/js/ui/temporada.js
    pattern: '\$\{bloqueDeAlbum\(carga\)\}\s+\$\{bloqueDelJuego\(carga\)\}\s+\$\{estadisticas\(carga\)\}'
    describe: el bloque va entre el álbum y las estadísticas
```

verified-by:
  - tests/slices/marcador-del-juego/marcador.test.js

## Requirement: Desde octubre, cada temporada tiene tres campeones

<!-- origen: feat-tres-campeones (added) -->

Desde la temporada de octubre de 2026, una temporada tiene **tres competiciones**: el marcador general, el
SuperWordleBros (`carga.juego.clasificacion`) y las figuras (`carga.album.jugadores`, solo los clasificados).
El archivo trae `competiciones`: una entrada por competición con `clave` (`marcador`, `juego`, `figuras`),
`lideres` —todos los de su primer puesto— y `campeones` —los mismos, si la temporada está cerrada—. Antes de
octubre, `competiciones` trae solo el marcador. `campeones`/`lideres` de nivel superior siguen siendo los del
marcador.

El medallero cuenta los títulos de temporadas cerradas **por competición**, en `titulos: { marcador, juego,
figuras }`; el juego y las figuras solo desde octubre. `temporadas_ganadas` sigue contando los del marcador.

#### Scenario: una temporada de octubre trae las tres
- GIVEN una temporada 2026-10 con marcador, juego y figuras
- WHEN se construye el archivo
- THEN trae tres competiciones con sus líderes, y un empate en cualquiera de ellas trae a todos los empatados

#### Scenario: septiembre trae solo el marcador
- GIVEN una temporada 2026-09 con juego y figuras en la instantánea
- WHEN se construye el archivo
- THEN trae solo la competición del marcador

#### Scenario: el medallero separa los títulos
- GIVEN una temporada 2026-10 cerrada en la que una persona gana el marcador y otra el juego y las figuras
- WHEN se construye el medallero
- THEN la primera tiene un título del marcador y la segunda uno del juego y uno de figuras

```yaml
checks:
  - type: regex
    file: v2/js/data/archivo.js
    pattern: 'export const DESDE_TRES_COMPETICIONES = .2026-10.;'
    describe: "las tres competiciones cuentan desde octubre"
  - type: regex
    file: v2/js/data/archivo.js
    pattern: 'cuenta.get\(nombre\).titulos\[clave\] \+= 1;'
    describe: "los títulos se cuentan por competición"
```

verified-by:
  - tests/slices/archivo-de-temporadas/archivo.test.js

## Requirement: El catálogo de reglas incluye el SuperWordleBros y distingue las históricas

<!-- origen: feat-pestana-info (added) -->

El catálogo (`tools/rules.py`) tiene un eje **`juego`** con las reglas del SuperWordleBros que ya se aplican:
puntos por puesto en cada nivel, las estrellas por delante del tiempo, cuándo se congela y se cierra cada nivel,
que solo los días que cuentan crean nivel, y que el nivel del último día laborable puntúa en el mes siguiente.
Sus números se leen de las constantes del cálculo (`juego.ESCALA`, `juego.PUNTOS_DESDE_EL_OCTAVO`,
`juego.HORA_DE_CONGELAR`, `seasons.MUESTRA_MINIMA_DEL_DIA`).

Cada regla lleva además `historica`: verdadera en las que solo valen para la temporada 0, para que la web pueda
dejarlas fuera de las vigentes sin borrarlas del catálogo. Las propuestas siguen en el catálogo como
`sin-decidir`, con lo que falta decidir.

`juego.HORA_DE_CONGELAR` es la misma hora que usa el cron (`v2/js/domain/superbros.js`), y un test comprueba
que coinciden.

#### Scenario: el juego tiene sus reglas con números del código
- GIVEN el catálogo
- WHEN se buscan las reglas del eje juego
- THEN están las cinco, aplicadas, y sus parámetros son los que usa el cálculo

#### Scenario: las de la temporada 0 son históricas
- GIVEN el catálogo
- WHEN se miran las reglas de la temporada 0
- THEN están marcadas como históricas, y ninguna otra lo está

#### Scenario: la hora es la misma que la del cron
- GIVEN la hora del catálogo y la del script del cron
- WHEN se comparan
- THEN son iguales

verified-by:
  - tests/slices/reglas-explicadas/test_reglas.py

## Requirement: El mínimo de partidas del álbum crece con el mes

<!-- origen: feat-participacion-y-album-al-arrancar (modified) -->

En una temporada mensual, para tener puesto en el ranking de belleza hacen falta tantas partidas como
jornadas lleva la temporada, con tope en `MINIMO_PARA_EL_ALBUM`. En la temporada 0 el mínimo es fijo. La
media sigue siendo sobre las jornadas de la temporada, así que faltar no mejora la de nadie.

```yaml
checks:
  - type: regex
    file: tools/album.py
    pattern: '^    return max\(1, min\(MINIMO_PARA_EL_ALBUM, jornadas\)\)$'
    describe: el mínimo de una temporada mensual son las jornadas que lleva, con tope en el de siempre
```

#### Scenario: el segundo día basta con haber jugado los dos
- GIVEN una temporada mensual con dos jornadas
- WHEN se calcula el álbum
- THEN clasifica quien jugó las dos, y no quien jugó una

#### Scenario: la temporada 0 conserva el mínimo fijo
- GIVEN la temporada 0
- WHEN se calcula el álbum
- THEN el mínimo es `MINIMO_PARA_EL_ALBUM`

verified-by:
  - tests/slices/clasificacion-de-figuras/test_album.py
