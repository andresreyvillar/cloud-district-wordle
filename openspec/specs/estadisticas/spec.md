# Spec de `estadisticas`

Spec **viva** del dominio `estadisticas` (ver `openspec/README.md`). Se edita directamente en la rama de cada cambio,
junto al código y los tests que la cumplen ([ADR 0009](../../decisions/0009-specs-vivas.md)). Cada Requirement
lleva en un comentario los change packs de los que sale, archivados en `openspec/changes/archive/`.

## Requirement: Una medalla es una función de los resultados, no un dato almacenado

<!-- origen: feat-medallas-resumen (added) -->

Las medallas se calculan a partir de los resultados cada vez que se necesitan. No hay tabla, columna ni
caché de medallas.

La consecuencia buscada: cambiar un umbral recalcula el palmarés histórico completo sin migrar nada. La
consecuencia aceptada: el cálculo se repite en cada consumidor.

```yaml
checks:
  - type: cli-command
    describe: el cálculo no consulta ninguna tabla de medallas
```

#### Scenario: dos cálculos sobre los mismos datos coinciden
- GIVEN un conjunto de resultados y una temporada
- WHEN se calculan las medallas dos veces
- THEN el resultado es idéntico

#### Scenario: el orden de las filas no altera el resultado
- GIVEN los mismos resultados en distinto orden
- WHEN se calculan las medallas
- THEN el resultado es el mismo

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py

## Requirement: El cálculo de medallas es determinista y sin reloj

<!-- origen: feat-medallas-resumen (added) -->

La temporada entra **por parámetro**, igual que los resultados. El cálculo no lee la fecha del sistema, y
por eso se puede verificar con datos fijos (§10 del protocolo).

#### Scenario: la temporada se pasa como argumento
- GIVEN unos resultados que abarcan varios meses
- WHEN se calculan las medallas de una temporada concreta
- THEN solo se consideran los resultados de esa temporada para las medallas de temporada

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py

## Requirement: Las medallas tienen dos alcances, y el alcance determina la ventana

<!-- origen: feat-medallas-resumen (added), feat-solo-dias-laborables (modified), chore-nombres-de-logros (modified) -->

Cada medalla es **de temporada** o **permanente**:

- Las de temporada se evalúan sobre los resultados de una temporada y se pueden ganar en varias.
- Las permanentes se evalúan sobre **todo el histórico** y no se repiten: la gesta ya está hecha.

En los dos casos la ventana contiene **solo días laborables**.

| Medalla | Alcance | Condición | Nivel |
|---|---|---|---|
| Suertud@ | permanente | resolver en un intento | legendario |
| El día imposible | permanente | resolver en ≤4 un día cuya media del grupo sea ≥5,5 | legendario |
| Superviviente | temporada | resolver en ≤4 tres días de media ≥4,5 | legendario |
| **Metrónom@** | temporada | no faltar **ningún día laborable** de la temporada (mínimo 10 días) | raro |
| Verdugo | temporada | ser el mejor del día cinco veces | común |
| Impecable | temporada | ninguna partida fallada, con 10 partidas mínimo | común |
| Fondista | temporada | 15 partidas o más | común |

`Metrónom@` se llamaba `Pleno`. El nombre estaba declarado abierto en
[el brief](../../../../docs/context/briefs/medallas.md) y se adopta el del
[diseño de la liga arcade](../../../../docs/context/sources/2026-08-05-diseno-liga-arcade.md). **La regla no
cambia.**

`Impecable` **no** pasa a llamarse `Superviviente` aunque el diseño lo proponga: ese nombre ya está en la
regla de los tres días duros, y dos medallas distintas no pueden llamarse igual.

#### Scenario: el umbral se cumple con igualdad
- GIVEN un jugador con exactamente 15 partidas laborables en la temporada
- WHEN se calculan sus medallas
- THEN obtiene Fondista

#### Scenario: no faltar ningún día laborable otorga Metrónom@
- GIVEN un jugador que juega todos los días laborables de una temporada de al menos diez días
- WHEN se calculan las medallas de la temporada
- THEN obtiene Metrónom@

#### Scenario: dos medallas nunca comparten nombre
- GIVEN el catálogo de medallas
- WHEN se listan sus nombres
- THEN no hay dos iguales

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py

## Requirement: Una temporada son sus días laborables

<!-- origen: feat-solo-dias-laborables (added) -->

Solo cuentan los resultados de **lunes a viernes**. Sábado y domingo no forman parte de ninguna temporada:
no fijan la dificultad de un día, no cuentan para ningún umbral y no son días que un jugador pueda faltar.

Las partidas de fin de semana **se siguen capturando y guardando**. La exclusión vive en el cálculo, no en
la ingesta: así la regla es reversible sin haber perdido nada.

La regla **no depende del umbral de muestra**. Hoy los dos coinciden por accidente —ninguna de las 10
jornadas de fin de semana del histórico llega a cinco jugadores— pero un sábado con seis jugadores tampoco
contaría.

El día de la semana se deriva de la **fecha de la fila**, nunca del reloj: el cálculo sigue siendo
reproducible con datos fijos (§10 del protocolo).

```yaml
checks:
  - type: cli-command
    describe: el día de la semana sale de la fecha de la fila, no de la fecha del sistema
```

#### Scenario: una partida de sábado no cuenta para un umbral
- GIVEN un jugador con 15 partidas de las que una cae en sábado
- WHEN se calculan sus medallas de la temporada
- THEN no obtiene Fondista, porque solo tiene 14 partidas que cuenten

#### Scenario: un fin de semana con muestra suficiente tampoco fija dificultad
- GIVEN un domingo que juegan cinco personas con media 5,8, y alguien que resuelve en 4
- WHEN se calculan las medallas permanentes
- THEN no obtiene El día imposible

#### Scenario: el cálculo no lee el reloj para saber qué día es
- GIVEN los mismos resultados con sus fechas
- WHEN se calculan las medallas dos veces
- THEN el resultado es idéntico, y depende solo de las fechas de las filas

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py

## Requirement: Un jugador puede ver de qué se compone su media de temporada

<!-- origen: feat-ficha-de-jugador (added) -->

La media de temporada de un jugador **incluye jornadas que no jugó**, porque el modelo imputa las
ausencias. Un número así no se sostiene sin poder mirarse dentro: la ficha desglosa la temporada jornada a
jornada, distingue lo jugado de lo imputado y publica **la diferencia entre las dos medias**, que es
exactamente lo que le costó faltar.

Nada de esto se recalcula en la vista: todo está en la instantánea que publica el bot
([ADR 0008](../../../decisions/0008-donde-vive-el-calculo.md)), así que la ficha y el canal no pueden
divergir.

#### Scenario: la ficha resume la temporada del jugador
- GIVEN un jugador con resultados en una temporada
- WHEN se abre su ficha
- THEN muestra su puesto, su media de temporada, su media de las partidas jugadas, las jornadas que jugó de
  las que la temporada tiene, y su mejor y su peor partida

#### Scenario: el desglose distingue lo jugado de lo imputado
- GIVEN una temporada con jornadas imputadas al jugador
- WHEN se mira el desglose
- THEN cada jornada aparece con su nota, su fecha y su número, y las imputadas se distinguen de las jugadas

#### Scenario: la ficha publica el coste de faltar
- GIVEN un jugador con al menos una jornada imputada
- WHEN se abre su ficha
- THEN dice cuántas ausencias tiene y cuánto separan su media de temporada de la de sus partidas jugadas

#### Scenario: una temporada sin imputación no inventa un coste
- GIVEN una temporada que no imputa ausencias
- WHEN se abre la ficha de uno de sus jugadores
- THEN la ficha declara que esa temporada no imputa, en lugar de publicar un coste de cero

#### Scenario: la distribución de intentos cuadra con lo jugado
- GIVEN un jugador con partidas en la temporada
- WHEN se mira su distribución por número de intentos
- THEN suma exactamente sus partidas jugadas, con el fallo como último cajón

verified-by:
  - tests/slices/ficha-de-jugador/ficha.test.js

## Requirement: La jornada en curso se puede mirar, y dice si cuenta todavía

<!-- origen: feat-resultado-del-dia (added) -->

La vista del día muestra la **última jornada con resultados** —derivada de los datos, no del reloj—, quién ha
jugado con sus intentos, quién falta, y cómo se ha dado la palabra comparada con la media de la temporada.

Y declara si esa jornada **cuenta ya para la temporada**. Un día entra si es laborable y lo juegan al menos
la muestra mínima, así que a media mañana la jornada existe, tiene resultados y todavía no puntúa. Sin
decirlo, alguien mira su nota, la ve cambiar y concluye que el sistema miente.

#### Scenario: la jornada en curso se deriva de los datos
- GIVEN resultados de varias jornadas
- WHEN se abre la vista del día
- THEN muestra la jornada más alta con resultados, no la que diga el reloj del navegador

#### Scenario: quien ha jugado aparece con su resultado
- GIVEN resultados de la jornada
- WHEN se muestran
- THEN aparece cada jugador con sus intentos, del mejor al peor, y el fallo se distingue de un 6

#### Scenario: quien falta aparece contado
- GIVEN un jugador de la temporada sin resultado en la jornada
- WHEN se muestra el día
- THEN aparece entre quien falta, con su nombre y contado

#### Scenario: el día se compara con la temporada
- GIVEN al menos un resultado en la jornada
- WHEN se muestra el día
- THEN se ve su media y si ha salido más dura o más fácil que la de la temporada, con la diferencia

#### Scenario: una jornada por debajo de la muestra mínima lo declara
- GIVEN una jornada con menos resultados que la muestra mínima
- WHEN se muestra
- THEN declara que aún no cuenta y cuántos faltan para que cuente

#### Scenario: un día no laborable no cuenta aunque tenga muestra
- GIVEN una jornada en sábado jugada por todo el grupo
- WHEN se muestra
- THEN los resultados aparecen y la vista declara que ese día no puntúa

#### Scenario: sin resultados no hay jornada
- GIVEN ningún resultado
- WHEN se abre la vista del día
- THEN lo declara en lugar de inventar una jornada

verified-by:
  - tests/slices/resultado-del-dia/dia.test.js

## Requirement: La ventana de una temporada la decide el modelo, no el prefijo de la fecha

<!-- origen: fix-medallas-temporada-cero (modified) -->

Cuando un cálculo necesita las filas de una temporada, la pertenencia la decide **la función del modelo de
temporadas**, no una comparación de cadenas contra la fecha.

Comparar el identificador con el principio de la fecha funcionaba mientras toda temporada era un `AAAA-MM`.
Con la temporada 0 dejó de funcionar **en silencio**: ninguna fecha empieza por `0`, así que el histórico
entero se quedó sin una sola medalla de temporada mientras las permanentes seguían apareciendo.

#### Scenario: la temporada 0 reparte medallas sobre todo el histórico
- GIVEN partidas repartidas en meses anteriores al límite de temporadas
- WHEN se piden las medallas de la temporada 0
- THEN se calculan sobre todas ellas, y quien llegue al umbral de Fondista la gana

#### Scenario: la misma medalla en dos temporadas numeradas cuenta dos veces
- GIVEN quince partidas en agosto y quince en septiembre
- WHEN se piden las medallas de cada temporada
- THEN Fondista aparece en las dos

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py

## Requirement: La ficha muestra el álbum de ese jugador

<!-- origen: feat-album-de-figuras (added) -->

La ficha de un jugador incluye **su** álbum: la tira agrupada de lo que ha dibujado, su tasa de figuras y su
puesto en el ranking de belleza de esa temporada.

Un jugador que no llega al mínimo ve **cuántas partidas le faltan**, no un puesto en blanco: el mínimo es
una regla del juego y decirla convierte "no apareces" en "te faltan dos".

Un jugador sin partidas clasificadas no ve un 0% —que diría que dibujó mal— sino que todavía no tiene álbum.

#### Scenario: la ficha trae la tira, la tasa y el puesto
- GIVEN un jugador clasificado en el álbum de su temporada
- WHEN abre su ficha
- THEN ve su tira agrupada, su tasa de figuras y su puesto

#### Scenario: por debajo del mínimo se dice cuánto falta
- GIVEN un jugador con menos partidas clasificadas que el mínimo
- WHEN abre su ficha
- THEN ve cuántas partidas le faltan para entrar en el ranking

#### Scenario: sin partidas clasificadas no hay un cero
- GIVEN un jugador cuyas partidas de la temporada no tienen patrón
- WHEN abre su ficha
- THEN se le dice que aún no tiene álbum, en lugar de una tasa del 0%

verified-by:
  - tests/slices/album-de-figuras/album.test.js

## Requirement: Cinco medallas premian el dibujo, con umbrales medidos

<!-- origen: feat-medallas-de-figuras (added) -->

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

## Requirement: El resumen diario deriva la temporada del modelo

<!-- origen: feat-medallas-de-figuras (added) -->

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

## Requirement: Los hechos notables de una jornada se detectan, no se narran

<!-- origen: feat-comentarios-de-la-jornada (added), feat-comentarios-por-la-hora (modified) -->

Una jornada produce **hechos**: quién resolvió muy rápido un día duro, quién quedó muy por encima o por
debajo de la media, quién no apareció el día difícil, y —esto es lo nuevo— **cuándo** publicó cada uno.

Un hecho sigue siendo un dato, no una frase.

Se añaden tres, y los tres por su rareza medida sobre las 186 jornadas que cuentan:

| Hecho | Disparador | Frecuencia |
|---|---|---|
| acertar a la primera | 1 intento | 0,01 |
| llegar el último **y** con nota muy por encima de la media | último, 4h+ de hueco, tarde, y ventaja | 0,06 |
| llegar el último | último, 4h+ de hueco, y con el día avanzado | 0,24 |

La hora **solo se usa si es utilizable**: si la marca de registro cae el mismo día que el puzzle. Las filas
del backfill se insertaron todas de golpe en otra fecha.

Y la notabilidad ordena por esa frecuencia: cuando alguien dispara dos hechos, sale por el más raro.

#### Scenario: la hora entra en la detección
- GIVEN una jornada con marcas de registro utilizables
- WHEN se detectan los hechos
- THEN quien publica muy por detrás del resto produce un hecho

#### Scenario: una hora no utilizable no produce hechos
- GIVEN resultados cuya marca de registro es de otro día
- WHEN se detectan los hechos
- THEN ninguno depende de la hora

#### Scenario: el más raro gana cuando coinciden
- GIVEN alguien que acierta a la primera en un día duro, que dispara dos hechos
- WHEN se detectan los hechos
- THEN sale por el más raro de los dos

verified-by:
  - tests/slices/comentarios-de-la-jornada/test_comentarios.py

## Requirement: La instantánea publica las figuras de la última jornada

<!-- origen: feat-figuras-de-la-jornada (added) -->

Además del álbum agregado, la instantánea de una temporada publica **la figura de cada resultado de su
jornada más reciente**: el número de jornada y, por jugador, la categoría que dibujó.

Se calcula sobre **todos los resultados de la temporada, cuenten o no sus días**. El álbum agregado solo
cuenta lo que puntúa; esta clave responde otra pregunta —qué se ha dibujado hoy— y una jornada abierta
todavía no alcanza la muestra mínima a media mañana.

Se publica **una sola jornada**, no el histórico: acotarlo es lo que permite que la vista de hoy tenga el
dato sin engordar la instantánea con miles de entradas que nadie lee.

Un resultado sin cuadrícula no aparece: no se le inventa categoría.

#### Scenario: la jornada más reciente trae sus figuras
- GIVEN una temporada con resultados en varias jornadas
- WHEN se materializa
- THEN publica el número de la jornada más reciente y la figura de cada jugador que dibujó ese día

#### Scenario: una jornada que aún no cuenta también publica sus figuras
- GIVEN una jornada con menos jugadores de los que hacen falta para que cuente
- WHEN se materializa la temporada
- THEN sus figuras se publican igual

#### Scenario: sin cuadrícula no hay entrada
- GIVEN un resultado de esa jornada sin patrón
- WHEN se materializa
- THEN ese jugador no aparece en las figuras de la jornada

#### Scenario: una temporada sin resultados no publica jornada
- GIVEN una temporada sin ningún resultado
- WHEN se materializa
- THEN la clave existe pero sin jornada ni figuras, y nada la da por buena

verified-by:
  - tests/slices/figuras-de-la-jornada/test_ultima_jornada.py

## Requirement: Las señales del canal producen menciones, y cada una exige evidencia

<!-- origen: feat-voz-de-la-jornada (added) -->

De las señales del día se derivan menciones, y **ninguna se concede por defecto**. Cada una tiene su umbral, y
si no se cumple, no sale nadie nombrado — igual que la obra del día se declara desierta antes que dársela a un
abstracto.

| Mención | Señal | Cuándo se concede |
|---|---|---|
| madrugador | hora del mensaje | publicó destacadamente antes que el resto del grupo |
| rezagado | hora del mensaje | publicó destacadamente después que el resto |
| más aplaudido | reacciones | su resultado recibió más reacciones que cualquier otro, y al menos una |
| más comentado | respuestas del hilo | abrió el hilo con más respuestas del día, y con al menos una |
| ausente | falta de mensaje | juega habitualmente y hoy no publicó |

Los umbrales de «destacadamente» **se miden antes de fijarlos**, sobre el histórico del canal, y no se
escriben a ojo: un umbral que nombra a alguien todos los días deja de ser una mención y pasa a ser una
columna, y uno que no nombra a nadie nunca es código muerto. El criterio es que la mención salga **en una
minoría clara de las jornadas**.

Un empate no se rompe con el orden en que llegaron los mensajes: se nombran todos los empatados, igual que
hace el jugador del día. Con diez personas y recuentos pequeños, el empate es lo normal.

Estas menciones **no tocan la clasificación**. No dan puntos, no quitan puntos y no aparecen en el marcador:
son texto para el canal. Es la misma frontera que ya separa el álbum del marcador.

```yaml
checks:
  - type: cli-command
    command: python3 tools/calibrate_menciones.py
    note: mide la frecuencia de cada mención sobre el histórico del canal antes de fijar su umbral
```

#### Scenario: la mención sin evidencia no se concede
- GIVEN un día en que ningún resultado recibió reacciones
- WHEN se derivan las menciones
- THEN no hay más aplaudido

#### Scenario: el empate nombra a todos
- GIVEN dos resultados con el mismo número de reacciones, y es el máximo del día
- WHEN se deriva la mención
- THEN se nombran los dos

#### Scenario: con una sola persona no hay madrugador
- GIVEN una jornada con un único resultado
- WHEN se derivan las menciones
- THEN no hay madrugador ni rezagado, porque no hay con quién comparar

#### Scenario: las menciones no dan puntos
- GIVEN una jornada con menciones
- WHEN se calcula la clasificación de la temporada
- THEN es la misma que sin ellas

verified-by:
  - tests/slices/voz-de-la-jornada/test_menciones.py

## Requirement: El espejo perfecto es un logro permanente

<!-- origen: feat-logro-espejo-perfecto (added) -->

Una cuadrícula simétrica fila a fila y con cuerpo suficiente concede un logro permanente, que se anuncia el
día que ocurre.

El umbral de cuerpo es lo que hace el logro. Medido sobre 1.706 cuadrículas: sin umbral hay 19 espejos y los
tendría el 43% del grupo, porque siete son de una sola fila y simétricos por accidente; con tres filas quedan
siete espejos de siete personas distintas, uno cada cinco meses.

Se concede mirando **el rasgo de simetría y no la categoría**: en la clasificación el espejo se consulta en
último lugar, así que una cuadrícula simétrica puede acabar etiquetada como flor, y el logro se perdería justo
en el mejor dibujo.

#### Scenario: el espejo perfecto tiene su logro
- **WHEN** alguien deja una cuadrícula simétrica fila a fila con cuerpo suficiente
- **THEN** gana el logro y se anuncia ese día
- **AND** una cuadrícula simétrica de una sola fila no lo gana
- **AND** una cuadrícula alta pero asimétrica tampoco

#### Scenario: el logro mira el rasgo y no la categoría
- **WHEN** la cuadrícula simétrica está clasificada como flor o como loro
- **THEN** el logro se concede igualmente

verified-by:
  - tests/slices/medallas-de-figuras/medallas.test.js
  - tests/slices/medallas-de-figuras/test_espejo_perfecto.py
  - tests/slices/medallas-de-figuras/test_medallas_de_figuras.py


## Requirement: Lo que el sistema afirma de una persona sale de un dato, no de una deducción

<!-- origen: feat-concordancia-de-genero (added) -->

Cuando el mensaje necesita saber algo de un jugador que no está en sus resultados —cómo referirse a él, por
ejemplo— ese dato **se declara**, no se infiere de lo que hay a mano.

La diferencia importa porque los sujetos son personas identificables y el mensaje se publica delante de todo
el grupo: una media mal calculada es un error que se corrige, y dirigirse mal a alguien no. Deducirlo del
nombre habría sido gratis de implementar y de coste desigual — lo pagaría siempre la misma persona.

Un dato declarado además se puede **corregir en un sitio** y deja constancia de quién lo declaró. Y lo que no
está declarado no se rellena con una suposición: se usa la forma que no afirma nada.

#### Scenario: un dato sobre una persona no se deduce
- **WHEN** el mensaje necesita un dato de un jugador que no está en sus resultados
- **THEN** sale de una declaración explícita, y si no la hay se usa la forma que no supone nada

verified-by:
  - tests/slices/comentarios-de-la-jornada/test_comentarios.py


## Requirement: El Coleccionista colecciona lo que se ha dibujado en su temporada

<!-- origen: feat-coleccionista-con-melocoton (modified) -->

La medalla se concede a quien tenga al menos una partida de **cada categoría que haya aparecido en esa
temporada**, no de una lista fija de categorías.

La lista fija se quedaba desfasada al añadir una categoría, y exigirla hacia atrás **quita medallas ya
concedidas**: medido al añadir el melocotón, 25 personas la habrían perdido por una regla que no existía
cuando jugaron. Derivarlo de lo que ha salido lo evita sin necesidad de un corte de fechas, y hace que la
medalla signifique lo que su nombre promete.

Si no se sabe qué ha salido, se cae a las categorías con umbral propio en lugar de dar la medalla por buena:
la condición de «todas» sobre un conjunto vacío se cumple siempre, y eso la concedería a cualquiera.

#### Scenario: el coleccionista se ajusta a lo que ha salido
- **WHEN** una categoría nueva aparece en una temporada
- **THEN** el Coleccionista la exige en esa temporada
- **AND** no la exige en las temporadas donde no apareció
- **AND** sin saber qué ha salido, no se concede a quien no tiene variedad

verified-by:
  - tests/slices/medallas-de-figuras/test_espejo_perfecto.py


## Requirement: El recuento de respuestas no es, por sí solo, un reconocimiento

<!-- origen: feat-tono-del-hilo (modified) -->

Las respuestas que cuelgan del mensaje de un jugador se cuentan igual que antes, y siguen eligiendo el hilo
del día. Lo que cambia es cómo se **lee** esa cifra: un recuento alto deja de valer por sí mismo como mérito.

Medido sobre la jornada que motivó el cambio: el resultado más comentado acumuló 26 respuestas y **cero
reacciones**, mientras el resto del día repartía 46 reacciones y ni un solo hilo. Las dos señales apuntaban en
direcciones opuestas y la mención solo miraba una, así que el mensaje coronó como triunfador a quien el grupo
estaba acusando.

Cuando la clasificación del hilo dice que aquello fue una acusación, a quien lo abrió no se le nombra como si
el recuento fuera un premio.

#### Scenario: un hilo de acusaciones no corona a nadie
- GIVEN el hilo más comentado de la jornada, clasificado como acusación
- WHEN se componen las menciones del mensaje
- THEN a quien lo abrió no se le nombra como si el recuento de respuestas fuera un reconocimiento

#### Scenario: un hilo sin acusación mantiene la mención de siempre
- GIVEN un hilo comentado y no clasificado como acusación
- WHEN se componen las menciones
- THEN la mención del hilo es la que había

verified-by:
  - tests/slices/voz-de-la-jornada/test_tono.py

## Requirement: Una nota se lee contra las del mismo día, no en solitario

<!-- origen: fix-sospecha-de-la-mejor-nota (modified) -->

Que alguien resuelva en dos intentos no significa lo mismo según lo que haya hecho el resto: con un 1 en la
mesa es la segunda mejor marca, y compartida con otra persona es señal de que la palabra era fácil.

Los hechos que se derivan de una nota baja se calculan por tanto **relativos a la jornada**: cuál fue la mejor
nota y cuánta gente la firmó. Es el mismo principio que ya gobierna `sembrado` y `no-inspirado`, que se miden
contra la media del día en lugar de contra un umbral fijo.

#### Scenario: la mejor nota de la jornada se calcula antes de juzgar ninguna
- GIVEN los resultados de una jornada
- WHEN se derivan los hechos comentables
- THEN la nota de cada jugador se compara con la mejor de ese día y con cuántos la firman

verified-by:
  - tests/slices/comentarios-de-la-jornada/test_comentarios.py

## Requirement: Los indicadores de juego salen de las cuadrículas, sin publicar palabras

<!-- origen: feat-indicadores-de-juego (added) -->

Para cada partida con cuadrícula se estiman las candidatas —soluciones aún posibles— antes de cada intento, con
el coloreado del juego (sin tildes, con Ñ) y la lista de soluciones hasta la última jornada jugada. De ahí salen,
por jugador y temporada: la media frente al grupo y al solucionador de referencia, la mediana de candidatas tras el
primer y el segundo intento, la suerte (Σ acierto − 1/candidatas por intento) y la partida resuelta con más
candidatas. El cálculo es determinista y la instantánea no contiene palabras.

#### Scenario: acertar con una sola candidata no es suerte
- GIVEN una partida cuyo intento ganador llega con una candidata
- WHEN se calcula su suerte
- THEN ese intento suma cero

#### Scenario: la instantánea no lleva palabras
- GIVEN una temporada materializada con la lista de soluciones
- WHEN se serializa la instantánea
- THEN no contiene ninguna palabra de la lista

verified-by:
  - tests/slices/indicadores-de-juego/test_indicadores.py
