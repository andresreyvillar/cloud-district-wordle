# Lecciones → Reglas (bucle error→regla)

> **Principio (§11 slice-system.md):** la lección NO es el artefacto — **la regla codificada lo es**.
> Todo fallo de proceso (gate en rojo con causa raíz, error del agente, hallazgo humano) produce una
> regla permanente en el punto ejecutable más fuerte posible, en esta cascada:
>
> **1. gate/CI** (mecánico) > **2. protocolo** (slice-system) > **3. skill** (fase) > **4. CLAUDE.md** (agente)
>
> Una lección con `estado: pendiente` es DEUDA — `/slice-audit` la reporta. Se registra con `/leccion`.

## Formato de entrada

```markdown
### AAAA-MM-DD — <síntoma en una frase>
- **Qué pasó:** ...
- **Causa raíz:** ...
- **Regla:** ...
- **Codificada en:** <archivo/gate/regla concreta> · **estado:** codificada | pendiente
```

---

### 2026-08-04 — Una migración de identidad se dio por hecha sin verificarla contra los datos
- **Qué pasó:** el commit que cambiaba la identidad de jugador a `slack_user_id` dejó el código con
  la apariencia de estar migrado (diccionario de IDs, `on_conflict` por ID), pero el extractor seguía
  emitiendo nombres mostrados. Resultado: 1234 de 1532 filas guardan un nombre en la columna de ID,
  el diccionario de identidades quedó inerte y hay jugadores duplicados por renombre en Slack.
- **Causa raíz:** el cambio se validó leyendo el código, no consultando el estado de los datos que
  produce. Nada obligaba a demostrar el comportamiento observable end-to-end.
- **Regla:** un cambio de comportamiento se demuestra con un test de escenario que observe el efecto
  (la fila resultante), no con la lectura del código que lo intenta. Y antes de tocar identidad,
  ranking o deduplicación, se comprueba el estado real de la columna en Supabase.
- **Codificada en:** `openspec/slice-system.md` §6 Fase 2 (TDD rojo obligatorio antes de implementar)
  y Gate 4c (mutación: un test que no cae al mutar el código no protege nada) ·
  **estado:** codificada

### 2026-08-04 — El método no se aplicaba porque no existía
- **Qué pasó:** el proyecto creció a base de commits directos a `main` sin especificación ni tests;
  las decisiones (ancla de fechas, umbrales del ranking, unificación de nombres) viven solo en el
  código y en scripts one-shot ya ejecutados.
- **Causa raíz:** no había método ni artefactos donde registrar el comportamiento esperado.
- **Regla:** todo comportamiento observable nuevo pasa por slice + change pack + TDD antes de
  implementarse; los cambios sin comportamiento observable van como change pack `Slice: N/A`.
- **Codificada en:** `openspec/slice-system.md` (constitución completa), `.claude/skills/*` y
  `CLAUDE.md` · **estado:** codificada

### 2026-08-04 — El bytecode cacheado falseó el resultado de una prueba de mutación
- **Qué pasó:** durante el Gate 4c del pack de adopción, tras restaurar el segundo mutante
  (`DOCSTRING_LOOKAHEAD = 0` → `3`) los tests seguían en rojo con el archivo ya correcto. El
  diagnóstico mostró que el `.pyc` del mutante y el `.py` restaurado tenían **el mismo tamaño y el
  mismo mtime al segundo** (1785840201), así que Python reutilizó el bytecode del mutante.
- **Causa raíz:** la invalidación de bytecode de CPython compara mtime con resolución de segundo.
  Mutar y restaurar dentro del mismo segundo, cambiando un solo carácter, cae justo en el hueco.
  Podía haber fallado en la dirección contraria y peor: un mutante ejecutándose como código sano
  habría dado el gate por bueno.
- **Regla:** todo comando de test del protocolo se ejecuta con `python3 -B` (no escribe bytecode).
  Si ya hay `__pycache__` sospechoso, purgarlo antes de creerse un veredicto.
- **Codificada en:** `openspec/slice-system.md` §6 Fase 4.1 y Gate 4c · `.claude/skills/slice-implement/SKILL.md`
  (paso 5.c y "trampas del procedimiento") · `CLAUDE.md` (Commands) · `README.md` ·
  **estado:** codificada

### 2026-08-04 — Un `git restore` se llevó por delante un arreglo hecho durante el gate
- **Qué pasó:** al reforzar `tools/wslice/gates.py` en medio del Gate 4c, el arreglo se hizo después
  del `git add -A` inicial. El `git restore` de la mutación siguiente restauró el index — que no
  tenía el arreglo — y lo borró sin aviso.
- **Causa raíz:** el procedimiento describe el index como red de seguridad para deshacer mutaciones,
  pero no dice que hay que actualizarlo cuando aparece un cambio legítimo a mitad del gate.
- **Regla:** durante el Gate 4c, todo arreglo real (test reforzado o código corregido) se stagea
  inmediatamente antes de aplicar la siguiente mutación.
- **Codificada en:** `openspec/slice-system.md` §6 Gate 4c (viñeta "el index es la única red") +
  `.claude/skills/slice-implement/SKILL.md` ("trampas del procedimiento") · **estado:** pendiente
- **REINCIDENCIA (misma fecha, slice de medallas):** la regla ya estaba escrita en el protocolo Y en la
  skill, y aun así se incumplió **dos veces más** en la misma sesión, perdiendo un arreglo cada vez. Según
  la cascada del §11, una regla que no se aplica pese a estar codificada indica que **el punto de
  codificación es demasiado débil**: dos niveles de documentación no bastan para un paso manual que se
  repite. Sube a nivel mecánico. *Destino: un comando `wslice mutate <archivo> --expr <a> <b>` que haga el
  ciclo completo —stage, mutar, ejecutar, restaurar, verificar verde— sin que el operador pueda saltarse
  el stage.*

### 2026-08-04 — El gate `federated-untouched` no veía una capability nueva completa
- **Qué pasó:** el mutante que quitaba el filtro `.md` del gate sobrevivió: ningún test lo cubría. Al
  escribir los tests que faltaban, uno de ellos falló contra el código sano y destapó un agujero real
  heredado del port: `git status --porcelain` colapsa un directorio enteramente sin trackear en una
  sola línea (`?? openspec/`), así que crear `openspec/specs/<nueva>/spec.md` en una capability nueva
  esquivaba el gate por completo.
- **Causa raíz:** el gate se portó de `slspec` literalmente, incluida esa suposición sobre la salida
  de git, y no había test que la ejercitase porque depende del repo real y no de un fixture.
- **Regla:** el gate usa `git status --porcelain --untracked-files=all`. Y ningún gate se considera
  cubierto sin al menos un test que monte el estado del que depende (aquí: un repo git temporal).
- **Codificada en:** `tools/wslice/gates.py` (`--untracked-files=all` + comentario del por qué) y
  `tests/harness/test_gates.py` (5 tests nuevos: pass, fail, staged, no-markdown, sin-repo) ·
  **estado:** codificada — *el mismo agujero existe en `slspec` de pga-cms; conviene avisar allí*

### 2026-08-04 — Una cifra medida sobre una página se propagó como hecho a cinco documentos
- **Qué pasó:** el análisis inicial de la tabla midió "1312 de 1530 filas guardan un nombre en la columna
  de ID" sobre un volcado que solo traía **la primera página de 1000 filas** de PostgREST. La cifra real,
  consultada por SQL, es **1234 de 1532**. El número equivocado llegó a dos proposals, el registro de
  lecciones y el roadmap, y se citó varias veces como argumento.
- **Causa raíz:** PostgREST pagina a 1000 filas por defecto y devuelve un `Content-Range` que lo dice. El
  primer análisis paginó para el conteo total pero no para esa métrica concreta, y nadie volvió a
  comprobarla porque ya estaba escrita en un documento.
- **Regla:** toda cifra que entre en un proposal, un ADR o una lección se mide con una consulta que
  devuelva el agregado completo —`count(*)` en SQL, o paginación explícita comprobada contra
  `Content-Range`—, nunca contando filas de un volcado parcial. Y una cifra ya escrita no se hereda: se
  vuelve a medir cuando el documento que la cita se revisa.
- **Codificada en:** este registro y la corrección de los cuatro documentos afectados ·
  **estado:** pendiente — *destino: probe `row-count` en `tools/wslice` que verifique las cifras
  declaradas en los `checks:` de un delta contra la base de datos. **El mecanismo ya existe** desde el
  2026-08-07 (`tools/wslice/probes.py`, gate `checks-probe`): falta el probe, que necesita credenciales y un
  tipo nuevo en §4 para declarar la cifra esperada*

### 2026-08-04 — Un test pendiente contaba como cubierto y verde
- **Qué pasó:** el primer slice escribió sus siete tests en rojo usando `pytestmark = pytest.mark.skip`
  a nivel de módulo. `wslice slice coverage` los marcó `covered` en lugar de `pending`, así que el Gate 2
  no distinguía TDD rojo de implementación terminada.
- **Causa raíz:** el escáner detecta lo pendiente por decorador inmediatamente anterior al `def` o por
  `pytest.skip()` en el cuerpo, y `pytestmark` de módulo es una tercera forma idiomática que no contempla.
- **Regla:** en los tests de escenario, el estado pendiente se declara **por test** con
  `@pytest.mark.skip`, nunca con `pytestmark` de módulo, hasta que el escáner entienda las dos formas.
- **Codificada en:** `.claude/skills/slice-propose/SKILL.md` (ejemplo de la Fase 2, ya usaba el decorador
  por test) y este registro · **estado:** pendiente — *destino: que `tools/wslice/coverage.py` reconozca
  `pytestmark` y `pytest.mark.skipif` a nivel de módulo, con su test en `tests/harness/test_coverage.py`*

### 2026-08-04 — El entorno de test no tenía las dependencias que el repo declara
- **Qué pasó:** el venv se creó instalando `pytest` y `PyYAML` a mano en lugar de
  `requirements-dev.txt`. El desfase no se notó durante cuatro slices, porque sus tests solo tocaban el
  harness y funciones puras. Apareció al primer test que importó código de producción: `slack_sdk` no
  estaba en el venv y el test falló por una razón que no tenía nada que ver con lo que probaba.
- **Causa raíz:** se instaló lo que hacía falta en ese momento en vez de lo que el repo declara, y nada
  comprobaba que el entorno coincidiese con `requirements-dev.txt`.
- **Regla:** el entorno de desarrollo se crea **siempre** con `pip install -r requirements-dev.txt`,
  nunca instalando paquetes sueltos. Si un test falla por un `ModuleNotFoundError`, lo primero es
  comprobar el entorno contra el archivo declarado, no tocar el test.
- **Codificada en:** `README.md` y `CLAUDE.md` (puesta en marcha) · **estado:** pendiente —
  *destino: check de entorno en `wslice verify gates` que compare lo instalado con requirements-dev.txt*

### 2026-08-04 — Dos cifras de calibración se midieron con una definición distinta de la que implementa el código
- **Qué pasó:** al medir el impacto de la regla de días laborables aparecieron dos cifras falsas en
  `docs/context/briefs/medallas.md`, las dos escritas el mismo día: `Pleno` decía que lo lograba el **12%**
  y el valor real era **0 de 123** parejas jugador-mes (la medalla era literalmente inganable), y
  `El día imposible` decía "2 personas, una vez" cuando son **4 personas en 2 días**.
- **Causa raíz:** las dos se midieron con una consulta *ad hoc* escrita para el análisis, cuya semántica
  divergía de la que implementa el código. En `Pleno`, la consulta contaba "días del mes" de una forma y
  `medallas_de_temporada` deriva los días de la temporada de los datos, así que un domingo con un solo
  jugador entraba como día que todos los demás habían faltado. En `El día imposible`, la consulta encontró
  un día y había dos. Ninguna de las dos se validó contra el catálogo real.
- **Regla:** una cifra de rareza o calibración de una medalla se mide **ejecutando el código que la
  implementa** sobre los datos, no con una consulta paralela que reimplemente la condición. Si hace falta
  SQL, es como *segunda* vía de verificación y las dos tienen que coincidir — que es como se detectaron
  estas dos.
- **Codificada en:** `docs/context/briefs/medallas.md` (las cifras corregidas y la tabla "Dos cifras que
  estaban mal", con la vía de medición declarada) y la tarea 4 de
  `openspec/changes/feat-solo-dias-laborables/tasks.md`, que ejecuta el catálogo contra producción y
  declara el resultado esperado · **estado:** pendiente — *destino: extender el probe `row-count` ya
  propuesto para que verifique también las cifras declaradas en un brief ejecutando el módulo del dominio,
  no una consulta paralela. Mismo bloqueo que la anterior: el mecanismo está, falta el probe y un formato
  para declarar la cifra*
- **Relación:** es la segunda vez que una cifra escrita en un documento se hereda sin volver a medirla (ver
  la lección de la página única de PostgREST). El patrón repetido no es el error de medida, es **que nadie
  vuelve a medir lo que ya está escrito**.

### 2026-08-04 — El gate de `test-commands` se satisface con una expresión regular
- **Qué pasó:** al portar el harness se replicó el gate que busca comandos de test en `tasks.md`
  mediante regex. Que pase no demuestra que los comandos existan, sean correctos ni se ejecuten.
- **Causa raíz:** el gate mide la presencia de una cadena, no la ejecución.
- **Regla:** el `ok` de `verify gates` no sustituye a la ejecución real de la suite; los Validation
  Gates de cada proposal listan los comandos que hay que ejecutar y el reporte de la Fase 4 debe
  incluir su salida.
- **Codificada en:** `openspec/slice-system.md` §7 (comandos deterministas), nota de honestidad en el
  proposal del pack de adopción y —el 2026-08-07— el gate **`checks-probe`** de `tools/wslice/gates.py`, que
  **ejecuta** los `checks:` de los deltas contra el repositorio en lugar de buscar cadenas. Siete probes
  implementados; los que necesitan la base de datos devuelven `indeterminate` diciendo por qué ·
  **estado:** codificada — *el gate de `test-commands` sigue siendo un regex y se declara como tal; lo que
  cambia es que ya no es el único gate mecánico de un pack*

### 2026-08-05 — El doble en memoria era más permisivo que la tabla real y la migración reventó a mitad
- **Qué pasó:** los 10 tests de `identidad-canonica-de-jugador` en verde, 6 mutantes muertos, y la
  ejecución real falló a mitad con `duplicate key value violates unique constraint`. La tabla tiene un
  índice único `(slack_user_id, wordle_id)`; el `TablaFalsa` de los tests no imponía nada, así que aceptaba
  escrituras que producción rechaza. El fallo dejó la tabla parcialmente migrada (18 de 1233 filas).
- **Causa raíz:** el doble se escribió para observar llamadas (`escrituras`, `borrados`), no para imitar
  las **restricciones** de lo que sustituye. Un doble que acepta lo que la tabla rechaza no prueba nada
  sobre la tabla, y ningún mutante puede cazarlo porque el hueco está en el test, no en el código.
- **Regla:** un doble de una tabla **imita sus restricciones**, no solo su interfaz: índices únicos, NOT
  NULL y claves ajenas se comprueban en el doble y se lanza como lanzaría el motor. Antes de escribir un
  doble se leen las restricciones reales del objeto que sustituye.
- **Codificada en:** `tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py`
  (`TablaFalsa` impone el índice único y lanza `ViolacionDeIndiceUnico`) y el escenario
  `clave-ocupada-se-declara-y-no-se-fuerza` del slice, y —el 2026-08-07— el **probe `index`** de
  `tools/wslice/probes.py`: compara el índice declarado en un delta con lo que imponen los dobles del
  `tests_root` y falla si ningún doble lo impone lanzando · **estado:** codificada — *en su primera
  ejecución encontró una segunda instancia: un `checks: index` declarado en un slice cuyos tests no escriben
  en ninguna tabla, así que reclamaba un doble que no podía existir. La invariante era cierta y el sitio,
  equivocado*
- **Segunda lección de la misma ejecución:** una migración que deja filas "intactas" por prudencia puede
  **bloquear** a otras. La fila conflictiva del puzzle 1481 se queda donde está por diseño, y donde está es
  la clave que necesita su dueña legítima. Lo prudente no es neutral: hay que declararlo (`bloqueadas`) en
  lugar de suponer que no tocar nada no tiene consecuencias.

### 2026-08-05 — Cambié a quién pertenecen unas partidas razonando sobre la base de datos en vez de mirar la fuente
- **Qué pasó:** el slice de identidad especificaba **eliminar** las 8 filas con el identificador de una
  persona y el nombre de otra, por ser "producto de un cruce de mapeo y no de una partida jugada". Lo
  cambié a **reatribuirlas** al dueño del nombre, apoyándome en que 5 de las 6 que ese dueño ya tenía
  registradas coincidían en puntuación exacta. Ejecutado contra producción, aquello **fabricó dos partidas**
  (puzzles #1477 y #1488, de días en que esa persona no publicó nada) y dejó una tercera (#1481) como copia
  byte a byte de la cuadrícula de otra jugadora.
- **Causa raíz:** deduje la propiedad de una fila de la **coherencia interna de la tabla** en lugar de
  consultar el sistema de registro, que es el canal de Slack y estaba disponible todo el tiempo: una sola
  búsqueda por `"#1477"` lo habría zanjado antes de escribir. La coincidencia de puntuaciones era evidencia
  real para 5 filas, y la extendí a 3 que no la tenían.
- **Regla:** antes de cambiar **a quién pertenece** un dato, se verifica contra la fuente de registro, no
  contra la consistencia interna del almacén. Y para contradecir una especificación que declara un dato
  espurio hace falta evidencia del mismo tipo que la produjo, no una inferencia estadística sobre lo ya
  guardado.
- **Codificada en:** `openspec/slices/identidad/identidad-canonica-de-jugador.md` (el escenario pasa a
  `atribucion-cruzada-se-declara-y-no-se-toca`: ni reatribuir ni borrar, porque las dos alternativas se
  probaron y las dos fallan) y el delta de `resultados`, que documenta las dos y por qué ·
  **estado:** codificada
- **El detector que apareció solo:** el backfill de patrones barrió el histórico completo y dejó
  **exactamente 2 filas sin patrón** — las 2 que yo había fabricado. Una partida real deja su cuadrícula en
  el canal; una fila fantasma no. *Destino mecánico: un probe que reporte las filas sin patrón tras un
  backfill completo como candidatas a fila fantasma, que es un detector barato y objetivo de un problema
  que hasta hoy solo se veía a mano.*

### 2026-08-05 — El clasificador se diseñó sobre supuestos visuales que nadie había comprobado con un humano
- **Qué pasó:** el brief de figuras fijó dos criterios como hechos medidos: que la última fila (`GGGGG`) no
  se analiza "porque dispararía la señal de flor en casi todos los aciertos", y que "en dos filas no hay
  figura posible". Con las 30 etiquetas humanas delante, **los dos son falsos**: esa banda verde **es** el
  suelo de la flor y los amarillos dispersos encima son los pétalos, y hay flores con dos filas sobre la
  base. El resultado medible del error: la heurística mandaba el **69%** de los patrones a la papelera y el
  humano manda el **33%**, con las flores casi invertidas (12% frente a 37%).
- **Causa raíz:** los dos criterios eran **intuiciones de quien escribió el clasificador sobre cómo mira un
  humano**, y se escribieron en el brief con el mismo formato que los hechos que sí estaban medidos (el 97%
  de cuadrículas que acaban en `GGGGG`, la retención del canal a 240 días). Un lector no podía distinguir
  una medición de una conjetura.
- **Regla:** un cálculo que **interpreta algo para personas** —clasificar un dibujo, elegir un tono, decidir
  qué es "bonito"— no puede calibrarse contra la intuición de quien lo escribe. Necesita un conjunto de
  etiquetas humanas **antes** de que sus parámetros entren en un documento, y hasta que exista, sus criterios
  se escriben marcados como conjetura, no en la sección de hechos medidos.
- **Codificada en:** `docs/context/briefs/ranking-de-figuras.md` (los dos supuestos tachados y marcados como
  DESMENTIDOS, con las cuadrículas que lo demuestran) y
  `docs/context/sources/2026-08-05-etiquetado-de-patrones.md`, que pasa a ser el conjunto dorado contra el
  que se mide cualquier cambio de peso · **estado:** codificada (2026-08-06) —
  `tests/figuras/test_clasificador.py::test_el_acuerdo_con_las_etiquetas_humanas_no_baja` ejecuta las 30
  etiquetas en cada suite y falla por debajo de `ACUERDO_MINIMO = 24`. El conjunto dorado **no se copia**:
  el test lo parsea del source, así que reetiquetar una ficha mueve el examen. La calibración ya es un gate.
- **Y una tercera cifra a remedir:** la correlación −0,37 entre media de intentos y número de cacas —el
  argumento de que los dos rankings premian a gente distinta— **se midió con el clasificador desmentido**.
  Quedó marcada como pendiente en el brief en lugar de seguir citándose. Es la tercera vez en dos días que
  una cifra derivada se hereda sin volver a medirla; el patrón ya no es casualidad.
  **Remedida el 2026-08-06 con el clasificador calibrado: −0,22**, y por tramos de media sin tendencia
  monótona (33% · 44% · 31% · 34% de abstractos). El signo aguanta, la fuerza no: pasa a citarse como señal
  débil. El diseño de dos premios separados se sostiene en la otra medida, la del 94%, que no depende del
  clasificador.

### 2026-08-06 — Un umbral que solo justifica un criterio fuera de la suite queda sin proteger
- **Qué pasó:** el clasificador de figuras se calibró contra dos criterios: el acuerdo con las 30 etiquetas
  humanas (en la suite) y el reparto sobre los 1521 patrones reales (necesita red, no cabe en la suite). El
  Gate 4c mutó el umbral de pétalos libres de 3 a 1 y **la suite siguió verde**, porque ese cambio *sube* el
  acuerdo a 25/30. Solo empeoraba el segundo criterio, que ningún test podía ejecutar.
- **Causa raíz:** el criterio que decidía el valor del umbral vivía en un informe, no en un test. El gate de
  acuerdo medía el agregado, y un agregado puede mejorar mientras el caso que discrimina el umbral se rompe.
- **Regla:** cuando un parámetro se elige por un criterio que **no puede ejecutarse en la suite** (necesita
  red, datos de producción o un humano), hay que fijar en un test el **caso concreto que lo discrimina**, y
  además la **propiedad** que el criterio protege. Un agregado no sustituye al caso: puede subir mientras el
  caso cae.
- **Codificada en:** `tests/figuras/test_clasificador.py::test_dos_amarillos_perdidos_no_hacen_una_flor` (el
  caso de la ficha 11, que el umbral decide) y `::test_alargar_la_cuadricula_no_convierte_el_ruido_en_flor`
  (la propiedad: una regla de figura no puede volverse más probable porque la partida sea larga, que es
  exactamente cómo falló el candidato descartado) · **estado:** codificada

### 2026-08-07 — El mismo fallo dos veces: derivar la temporada de una fecha por tu cuenta
- **Qué pasó:** la tabla cruda decía «1543 resultados · **70** cuentan para su temporada». Buscaba la
  instantánea con el mes de la fecha, y las 1502 filas anteriores a agosto tienen meses (`2026-05`, `2026-06`…)
  que **no existen como temporada**: todas son la temporada 0. Un día antes, exactamente la misma causa había
  dejado 181 jornadas sin una sola medalla en `tools/badges.py`.
- **Causa raíz:** el modelo de temporadas cambió (la 0 dejó de ser un `AAAA-MM`) y **todo el código que
  reimplementaba «a qué temporada pertenece esto» siguió compilando**. Comparar cadenas no lanza: devuelve
  vacío. Y el borde de datos ayudaba, porque llamaba `temporada` a un campo que era el mes.
- **Regla:** una pregunta del modelo se le hace **al modelo**. Ni `startswith`, ni `slice(0,7)`, ni comparar
  el identificador de una temporada con una fecha. Cada lenguaje tiene **una** función que responde, y sus
  parámetros —el límite— se leen de las reglas publicadas, no se copian. Si el dato para responder no está,
  se devuelve `null` y **no se adivina**: las dos veces el fallo fue silencioso porque algo asumió un valor.
  Y un campo se llama por lo que es: `mes` no es `temporada`.
- **Codificada en:** `v2/js/data/temporada.js` (única definición en la web, con el límite leído de las reglas
  y `null` cuando no hay límite), `tools/badges.py::_de_la_temporada` (usa `seasons.temporada_de`),
  `v2/js/data/results.js` (`normalizar()` devuelve `mes`, no `temporada`) y los tests
  `la-temporada-de-una-fila-la-decide-el-modelo` y `la-temporada-cero-tambien-reparte-medallas` ·
  **estado:** codificada
- **Y una observación sobre cómo se cazó:** ninguna de las dos veces lo encontró un test. Las dos las
  encontró **una vista enseñando un agregado absurdo** —cero medallas en 181 jornadas, 70 filas de 1543—. Un
  agregado a la vista es un detector de fallos silenciosos que ningún unitario sustituye, y es un argumento
  para que las vistas publiquen totales aunque nadie los haya pedido.


### 2026-09-11 — Las mutaciones que elige quien implementa confirman; no refutan
- **Qué pasó:** en `feat-tono-del-hilo` el Gate 4c pasó limpio —cinco mutaciones, las cinco cazadas por el
  escenario correcto— y a continuación el Gate 4d sostuvo **siete refutaciones**, todas con la suite entera en
  verde. Entre ellas: añadir a la clase de la clasificación un campo de texto poblado por el modelo y
  concatenarlo en la frase publicada, y meter al registro «{jugador} hizo trampas y el canal lo sabe».
- **Causa raíz:** la regla de mutación ya existía y se aplicó. Lo que falla es **de dónde salen las
  mutaciones**: quien implementa muta lo que ya tenía en la cabeza, así que prueba las defensas que recuerda
  haber puesto. Las siete refutaciones atacaban justo lo que no se le había ocurrido defender. Un gate cuya
  entrada la elige el propio implementador confirma su modelo mental en lugar de romperlo.
- **Regla:** las mutaciones del Gate 4c **se derivan del delta, no de la intuición**. Por cada frase de un
  Requirement con forma «nunca X» / «solo Y» / «no puede Z», la mutación obligatoria es la que **hace ocurrir
  X**. Y tres moldes de guardián quedan prohibidos por vacuos: comprobar **subcadenas literales** en vez de la
  raíz o la forma del objeto; probar determinismo **llamando dos veces en el mismo proceso** —eso es
  idempotencia, no reproducibilidad: una elección por `hash()` lo pasa y cambia el texto en cada cron—; y
  cubrir «si el borde falla, se publica igual» **desde el compositor**, pasándole `None`, sin hacer fallar al
  borde.
- **Codificada en:** `.claude/skills/slice-implement/SKILL.md` Gate 4c paso (b), con los tres moldes nombrados ·
  **estado:** codificada · **destino mecánico pendiente:** un gate de `tools/wslice` que extraiga las
  prohibiciones de los deltas y exija una mutación por cada una.
- **Y una segunda, más barata de recordar:** un comentario que afirma una garantía es tan comprobable como el
  código. En este mismo cambio escribí que un tope de lectura acotaba el tiempo de espera; medido, con plazo
  declarado de 2 s la lectura bloqueó **40 s**, porque el `timeout` de un socket no es un plazo total. La
  afirmación falsa en un comentario sobrevive a las revisiones mejor que un error en el código, porque nadie
  la ejecuta.

### 2026-09-25 — El gate de mutación miente en las dos direcciones
- **Qué pasó:** en `feat-juego-de-la-jornada` el Gate 4c dio veredictos falsos **dos veces seguidas y en
  sentidos opuestos**. Primero cuatro verdes falsos: el mutador vivía en el scratchpad de una sesión anterior,
  había desaparecido, y las cuatro llamadas fallaron a stderr mientras la suite seguía verde. Después un rojo
  falso: un bucle con `IFS='|'` partió el código a mutar por su `||`, el mutador sustituyó otro trozo, dejó un
  error de sintaxis y los tres ficheros de test reventaron al importar el módulo. Se leyó como «mutación
  cazada» y **la mutación real sobrevivía**: la promesa de acotar las estrellas al total no tenía test.
- **Causa raíz:** el veredicto del gate se leía del estado de la suite y nunca de si la mutación pensada era
  la que había corrido. Un gate que no verifica su propia entrada puede afirmar cualquier cosa, en cualquier
  color.
- **Regla:** antes de leer el resultado de una mutación se comprueban tres cosas: que el fichero **cambió**,
  que **sigue compilando** (`node --check` / `py_compile`), y que el rojo cae en **un** escenario y no en
  todos. Un rojo en ficheros que no usan el código mutado es un error de sintaxis, no una cazada. Y el
  código no se pasa por bucles con separadores: una llamada al mutador por mutación.
- **Codificada en:** `.claude/skills/slice-implement/SKILL.md` Gate 4c, con las tres formas nombradas ·
  **estado:** codificada · **destino mecánico pendiente:** que `mutar.py` viva en el repositorio y no en el
  scratchpad, y que compile el fichero tras mutar y aborte si no compila.

### 2026-09-25 — Un arreglo que mide el síntoma puede estar rompiendo la función
- **Qué pasó:** en `feat-juego-de-la-jornada` la página hacía scroll al hacer el pisotón. Se arregló bloqueando
  el scroll de las teclas del juego y se verificó midiendo el scroll: quieto con todas las teclas, en verde.
  Pero el bloqueo iba en el mismo elemento que escucha Phaser y se ejecutaba antes que él, y Phaser descarta
  las teclas que le llegan ya bloqueadas: **el juego se había quedado sin teclas**. La página no se movía
  porque no se movía nada. Lo cazó repetir las pruebas de juego de antes, no la prueba del arreglo.
- **Causa raíz:** la prueba del arreglo solo podía fallar si volvía el síntoma, y nunca si moría la función.
  Un arreglo que apaga la función hace desaparecer el síntoma, así que esa prueba lo daba por bueno.
- **Regla:** la prueba de un arreglo incluye una aserción de que **la función sigue viva**, y va primero:
  antes de medir que el scroll no se mueve, medir que el personaje se mueve. Y tras cualquier arreglo que toque
  la entrada, el render o el orden de los eventos, se repiten las pruebas de juego anteriores, no solo la
  nueva.
- **Codificada en:** `.claude/skills/slice-implement/SKILL.md` Fase 4, y en el propio caso: un `checks:` del
  delta fija que el bloqueo vaya en el padre del lienzo, y la prueba de navegador empieza por «¿el personaje
  responde?» · **estado:** codificada · **destino mecánico pendiente:** pruebas de navegador en el
  repositorio; hoy viven en el scratchpad porque no hay infraestructura de e2e.

### 2026-09-25 — Un mutante que borra datos compartidos pone en rojo a todo el mundo
- **Qué pasó:** en `feat-nivel-congelado`, la mutación que quitaba `delete` del trigger de inmutabilidad
  puso en rojo nueve tests de tres escenarios. El `delete` mutado **borraba el único nivel del fixture**, que
  es de módulo, y los tests siguientes fallaban por no encontrarlo: parecía una cazada amplia y era una
  cascada.
- **Causa raíz:** los tests que intentan escribir lo prohibido compartían el estado que esa escritura
  destruye. Un rojo en cascada no dice qué escenario protege el mutado.
- **Regla:** un test que intenta una escritura prohibida contra estado compartido la hace **dentro de una
  transacción que se deshace**. Si una regresión la deja pasar, cae ese test y el estado sigue intacto.
- **Codificada en:** `.claude/skills/slice-implement/SKILL.md` Gate 4c (cuarta forma de que el gate mienta)
  y `tests/slices/nivel-congelado/test_game_levels.py::intentar` · **estado:** codificada.
