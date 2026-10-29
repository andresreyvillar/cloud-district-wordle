# Ontología del dominio

## a. Propósito y alcance

Este documento describe **qué cosas existen** en wordle-stats, cómo se relacionan, dónde vive cada una, qué
estados atraviesan y qué reglas no pueden romperse nunca. Complementa al [glosario](glosario.md), que define
las palabras; aquí se dibuja la estructura.

Alcance: el dominio del juego (resultados, temporadas, clasificaciones, figuras, medallas, publicación), el
SuperWordleBros, el debate de reglas, los indicadores de juego y, al final, la ontología del propio método de
trabajo. Todo sale del código, las migraciones, los slices y los ADRs; cada afirmación cita su fuente
(`ruta:línea`). No incluye nombres de jugadores ni palabras del día: el repositorio es público.

Jerarquía de verdad: **specs + slices > ADRs / glosario > briefs > sources** (`docs/context/INDEX.md:11`).

## b. Conceptos y relaciones

### b.1 Núcleo: resultados, temporadas y clasificaciones

```mermaid
classDiagram
  direction LR
  Jugador : +slack_user_id text
  Jugador : +player_name text
  Apodo : +texto_visible text
  Resultado : +wordle_id int
  Resultado : +score int
  Cuadricula : +pattern text
  Jornada : +wordle_id int
  PalabraDelDia : +solution text
  Temporada : +temporada text
  Temporada : +estado text
  DiaValido : +jornada int
  Clasificacion : +media_temporada float
  Clasificacion : +media_jugada float
  Clasificacion : +posicion int
  Figura : +categoria text
  Album : +media float
  Medalla : +clave text
  Medalla : +nivel text
  Instantanea : +payload jsonb
  Regla : +id text
  ResumenDiario : +jornada int
  PodioDeCierre : +temporada text

  Jugador "1" --> "0..*" Resultado : publica
  Jugador "1" --> "0..1" Apodo : se pinta con, solo en la web
  Resultado "0..*" --> "1" Jornada : es de
  Resultado "1" *-- "0..1" Cuadricula : lleva
  Cuadricula "1" --> "1" Figura : se clasifica como
  Jornada "1" --> "1" PalabraDelDia : tiene por solución
  Jornada "0..*" --> "1" Temporada : pertenece a
  Temporada "1" *-- "0..*" DiaValido : se forma con
  DiaValido "1" --> "1" Jornada : es
  Temporada "1" *-- "0..*" Clasificacion : marcador, una fila por jugador
  Temporada "1" *-- "0..*" Album : álbum, una fila por jugador
  Clasificacion "0..*" --> "1" Jugador : de
  Album "0..*" --> "1" Jugador : de
  Album "1" --> "0..*" Figura : suma puntos de
  Medalla "0..*" --> "0..*" Jugador : la ganan
  Instantanea "1" --> "1" Temporada : materializa
  Instantanea "1" o-- "1..*" Regla : lleva el catálogo
  ResumenDiario "0..*" --> "1" Jornada : resume
  PodioDeCierre "0..1" --> "1" Temporada : celebra, si está cerrada
```

- **Jugador ↔ Resultado**: como mucho un resultado por (jugador, jornada), por el índice único
  (`openspec/decisions/0005-hosting-y-convivencia-v1-v2.md:102`, `tools/add_results.py:34`).
- **Jornada → Temporada**: `temporada_de(fecha)` da `AAAA-MM`, o `"0"` antes de `INICIO_TEMPORADAS`
  (`tools/seasons.py:51`); la fecha se deriva del número de jornada (`tools/add_results.py:60`).
- **DiaValido**: las jornadas laborables con al menos `MUESTRA_MINIMA_DEL_DIA = 5` resultados; en la
  temporada 0, todas (`tools/seasons.py:99`).
- **Cuadrícula 0..1**: sin patrón no hay figura y la partida no cuenta en el álbum (`tools/album.py:128`).
- **Figura** y **Medalla** no se almacenan: se derivan en cada cálculo (`tools/figures.py:9`,
  `tools/badges.py:8`); las medallas viajan como `logros: {clave: [jugadores]}` (`tools/seasons.py:225`).
- **Apodo** se indexa por nombre de Slack, no por id, y solo afecta a la pintura (`v2/js/domain/apodos.js:18`).
- **PodioDeCierre** es el mensaje que el código llama «victoria»: sale la noche del último laborable y, si
  faltara, lo publica el cron de los días 1 a 3 (`tools/post_ranking.py:688`, `tools/podio.py:129`,
  `.github/workflows/post_podium.yml:15`).

### b.2 El SuperWordleBros

```mermaid
classDiagram
  direction LR
  Jugador : +slack_user_id text
  Jornada : +wordle_id int
  Temporada : +temporada text
  Nivel : +collectibles list
  NivelCongelado : +jornada int
  NivelCongelado : +nivel jsonb
  Marca : +segundos numeric
  Marca : +estrellas int
  ClasificacionDelJuego : +puntos int
  Instantanea : +payload jsonb

  Jornada "1" --> "0..1" Nivel : se convierte en
  NivelCongelado "1" *-- "1" Nivel : guarda
  NivelCongelado "0..1" --> "1" Jornada : de
  Jugador "1" --> "0..*" Marca : registra
  Marca "0..*" --> "1" NivelCongelado : en
  NivelCongelado "0..*" --> "1" Temporada : puntúa en
  ClasificacionDelJuego "1" --> "1" Temporada : de
  ClasificacionDelJuego "1" --> "0..*" Marca : reparte puntos por puesto
  Instantanea "1" *-- "1" ClasificacionDelJuego : clave juego
```

- **Nivel 0..1 por jornada**: solo si la jornada es día de temporada y alguien publicó cuadrícula
  (`v2/js/domain/superbros.js:112`, `v2/js/domain/superbros.js:173`).
- **Marca**: como mucho una por (jornada, jugador) (`supabase/migrations/20260925120000_create_game_times.sql:16`).
- **Puntúa en** la temporada de su fecha, salvo el nivel del último laborable del mes, que puntúa en la
  siguiente (`tools/juego.py:78`).

### b.3 Debate de reglas e indicadores de juego

```mermaid
classDiagram
  direction LR
  Jugador : +slack_user_id text
  Votacion : +abierta bool
  Opcion : +texto text
  Voto : +opcion text
  Propuesta : +autor text
  Propuesta : +estado text
  VotoDePropuesta : +voto text
  Instantanea : +payload jsonb
  Indicadores : +referencia float
  IndicadoresDeJugador : +suerte float
  PalabraDelDia : +solution text

  Votacion "1" *-- "2..*" Opcion : ofrece
  Voto "0..*" --> "1" Votacion : en
  Voto "0..*" --> "1" Opcion : elige
  Jugador "1" --> "0..*" Voto : emite, uno por votación
  Jugador "1" --> "0..*" Propuesta : firma
  Propuesta "1" *-- "0..*" VotoDePropuesta : recibe
  Jugador "1" --> "0..*" VotoDePropuesta : emite, uno por propuesta
  Instantanea "1" *-- "0..1" Indicadores : clave indicadores
  Indicadores "1" *-- "0..*" IndicadoresDeJugador : por jugador
  Indicadores ..> PalabraDelDia : lee hasta la última jornada
```

- **Votación con 2 o más opciones**: `check (jsonb_array_length(opciones) >= 2)`
  (`supabase/migrations/20261014120000_create_rule_debate.sql:21`).
- **Jugador** en el debate es cualquiera con al menos un resultado: las funciones rechazan a quien no ha jugado
  nunca (`supabase/migrations/20261014120000_create_rule_debate.sql:87`).
- **Indicadores 0..1**: solo si la lista de soluciones se pudo leer en el borde (`tools/seasons.py:239`); por
  jugador, cifras solo con `MINIMO_DE_PARTIDAS = 5` (`tools/indicadores.py:196`).

## c. Modelo de datos

Las tablas del juego y del debate tienen migración en `supabase/migrations/`. `wordle_results` y
`season_snapshots` **no**: su esquema está documentado en los ADRs 0005 y 0008 y lo confirman las columnas que
lee y escribe el código.

```mermaid
erDiagram
  wordle_results {
    uuid id PK
    text slack_user_id UK "único junto con wordle_id"
    text player_name
    int wordle_id UK
    int score "1 a 6, o 7 si es fallo"
    date date
    text raw_text
    text pattern "filas de G, Y y punto separadas por barra"
    timestamptz created_at
  }
  season_snapshots {
    text temporada PK "AAAA-MM o 0"
    jsonb payload
    timestamptz updated_at
  }
  game_levels {
    int jornada PK
    date fecha
    jsonb nivel "labels y collectibles obligatorios"
    timestamptz frozen_at
  }
  game_times {
    int jornada PK
    text jugador PK
    numeric segundos "mayor que 0 y menor que 3600"
    int estrellas
    timestamptz updated_at
  }
  rule_polls {
    text id PK
    text titulo
    jsonb opciones "al menos 2"
    boolean abierta
  }
  rule_votes {
    text votacion PK "FK a rule_polls.id"
    text votante PK
    text opcion
  }
  rule_proposals {
    bigint id PK
    text autor
    text titulo "3 a 120 caracteres"
    text texto "10 a 2000 caracteres"
    text estado "pendiente, aprobada o rechazada"
  }
  rule_proposal_votes {
    bigint propuesta PK "FK a rule_proposals.id"
    text votante PK
    text voto "a_favor o en_contra"
  }

  rule_polls ||--o{ rule_votes : "recibe"
  rule_proposals ||--o{ rule_proposal_votes : "recibe"
  game_levels ||..o{ game_times : "marcas del nivel, relación lógica"
  wordle_results }o..o{ game_times : "jugador es un slack_user_id"
  wordle_results }o..o{ rule_votes : "votante es un slack_user_id"
  wordle_results }o..o{ rule_proposals : "autor es un slack_user_id"
  wordle_results }o..o{ rule_proposal_votes : "votante es un slack_user_id"
  wordle_results }o..o{ season_snapshots : "se materializa en"
```

Solo hay dos claves foráneas reales (`rule_votes.votacion` y `rule_proposal_votes.propuesta`, con `on delete
cascade`); las relaciones punteadas son lógicas y las comprueban las funciones RPC, no el esquema. Fuentes de
cada tabla: las de la tabla siguiente.

### Concepto → dónde vive

| Concepto | Dónde vive | Fuente |
|---|---|---|
| Jugador | `wordle_results.slack_user_id` (no hay tabla de jugadores) | `tools/add_results.py:83` |
| Nombre mostrado | `wordle_results.player_name`; en cálculos, el de la fila más reciente | `tools/juego.py:65` |
| Apodo | constante de la web, aplicada al pintar | `v2/js/domain/apodos.js:18` |
| Forma gramatical | constante del pipeline, por nombre mostrado | `tools/personas.py:30` |
| Resultado / partida | fila de `wordle_results` | `tools/add_results.py:81`, `openspec/decisions/0005-hosting-y-convivencia-v1-v2.md:101` |
| Cuadrícula | `wordle_results.pattern` | `tools/patterns.py:6` |
| Jornada | `wordle_results.wordle_id` | `tools/palabra.py:5` |
| Palabra del día | lista de soluciones del juego, leída en el borde y nunca guardada | `tools/palabra.py:63` |
| Temporada | cálculo `temporada_de(date)` | `tools/seasons.py:51` |
| Instantánea | fila de `season_snapshots` (`temporada`, `payload`, `updated_at`) | `openspec/decisions/0008-donde-vive-el-calculo.md:75` |
| Estado de temporada | clave `estado` de la instantánea | `tools/seasons.py:211` |
| Día válido | clave `dias` (lista de jornadas) | `tools/seasons.py:212` |
| Dificultad del día | claves `dificultad`, `mas_dificil`, `mas_facil` | `tools/seasons.py:221` |
| Clasificación (marcador) | clave `clasificacion` | `tools/seasons.py:220` |
| Medallas | clave `logros`; nunca en una tabla | `tools/seasons.py:225` |
| Figura y álbum | clave `album`; la figura se deriva del patrón | `tools/seasons.py:228` |
| Figuras de la última jornada | `album.ultima_jornada` | `tools/album.py:157` |
| Clasificación del juego | clave `juego` | `tools/seasons.py:231` |
| Reglas | clave `reglas`, generada con `rules.catalogo()` | `tools/seasons.py:217` |
| Indicadores de juego | clave `indicadores` (opcional) | `tools/seasons.py:244` |
| Procedencia | clave `calculado_con` (commit) | `tools/seasons.py:234` |
| Nivel congelado | `game_levels.nivel` | `supabase/migrations/20260925140000_create_game_levels.sql:11` |
| Marca | fila de `game_times` | `supabase/migrations/20260925120000_create_game_times.sql:10` |
| Votación, opción | `rule_polls`, `rule_polls.opciones` | `supabase/migrations/20261014120000_create_rule_debate.sql:16` |
| Voto | `rule_votes` | `supabase/migrations/20261014120000_create_rule_debate.sql:26` |
| Propuesta | `rule_proposals` | `supabase/migrations/20261014120000_create_rule_debate.sql:35` |
| Voto de propuesta | `rule_proposal_votes` | `supabase/migrations/20261015090000_public_votable_proposals.sql:14` |
| Resumen diario, podio de cierre | mensajes de Slack; el título de la imagen es la marca de idempotencia | `tools/post_ranking.py:546`, `tools/post_ranking.py:173` |
| Señales y tono del hilo | memoria de la ejecución; no se persisten | `tools/senales.py:12` |

## d. Ciclos de vida

### Temporada

```mermaid
stateDiagram-v2
  state "en curso" as EnCurso
  state "cerrada" as Cerrada
  state "temporada 0, el histórico" as Cero
  [*] --> EnCurso : primer resultado de un mes desde 2026-08
  EnCurso --> Cerrada : aparece un resultado de un mes posterior
  Cerrada --> Cerrada : rematerialización, la recién cerrada en el cron o todas a mano
  [*] --> Cero : resultados anteriores a INICIO_TEMPORADAS
  Cero : no imputa, no filtra días y no se celebra
```

El estado se **deriva de los datos**: la temporada más reciente con resultados está en curso y las demás
cerradas (`tools/seasons.py:131`). Como el estado viaja en la instantánea, el cron rematerializa también
`RECIEN_CERRADAS = 1` temporada cerrada (`tools/materialize_seasons.py:228`). Una temporada sin días válidos
sigue existiendo, con cero días (`tools/seasons.py:137`).

### Nivel del SuperWordleBros

```mermaid
stateDiagram-v2
  state "jornada abierta, hoy" as Abierta
  state "sin nivel" as SinNivel
  state "congelado y abierto a marcas" as Vigente
  state "congelado y cerrado" as Cerrado
  [*] --> Abierta : primer resultado de la jornada
  Abierta --> Vigente : el cron la congela desde las 2 h de Madrid del día siguiente
  Abierta --> SinNivel : no es día de temporada o nadie publicó cuadrícula
  Vigente --> Cerrado : se congela el nivel siguiente
  Cerrado --> [*]
  SinNivel --> [*]
```

`HORA_DE_CONGELAR = "02:00"` (`v2/js/domain/superbros.js:67`, `tools/juego.py:30`); antes de esa hora se
congela la de anteayer, y la de hoy nunca (`v2/js/domain/superbros.js:105`). Un nivel congelado no se cambia ni
se borra (`supabase/migrations/20260925140000_create_game_levels.sql:41`). Solo el último congelado admite
marcas (`supabase/migrations/20260930120000_close_levels_and_rank_by_stars.sql:54`): el del viernes sigue
abierto el fin de semana, porque un fin de semana no crea nivel.

### Propuesta de regla

```mermaid
stateDiagram-v2
  state "pendiente" as Pendiente
  state "aprobada" as Aprobada
  state "rechazada" as Rechazada
  [*] --> Pendiente : proponer_regla
  Pendiente --> Aprobada : update manual del dueño
  Pendiente --> Rechazada : update manual del dueño
  Aprobada --> Rechazada : el esquema no lo impide
  Rechazada --> [*]
```

Nace `pendiente` (`supabase/migrations/20261014120000_create_rule_debate.sql:131`). **Pendientes y aprobadas
son públicas y se pueden votar**; solo `rechazada` se oculta a la clave pública y deja de admitir votos
(`supabase/migrations/20261015090000_public_votable_proposals.sql:11`,
`supabase/migrations/20261015090000_public_votable_proposals.sql:38`). Las transiciones son `update` manuales
del dueño desde Supabase (`supabase/migrations/20261014120000_create_rule_debate.sql:12`); el esquema solo
restringe los valores, no el orden.

### Votación

```mermaid
stateDiagram-v2
  state "abierta" as Abierta
  state "cerrada" as Cerrada
  [*] --> Abierta : alta manual, abierta por defecto
  Abierta --> Abierta : votar o cambiar el voto
  Abierta --> Cerrada : update manual de abierta a false
  Cerrada --> [*]
```

`abierta boolean not null default true` (`supabase/migrations/20261014120000_create_rule_debate.sql:22`);
`votar_regla` rechaza los votos de una votación cerrada (`supabase/migrations/20261014120000_create_rule_debate.sql:75`).

### Slice

```mermaid
stateDiagram-v2
  state "proposed" as Proposed
  state "shipped" as Shipped
  state "blocked" as Blocked
  state "deprecated" as Deprecated
  [*] --> Proposed : slice-propose
  Proposed --> Shipped : en la propia rama, antes del merge
  Shipped --> [*]
  Blocked : valor admitido, con reason, since y by
  Deprecated : valor admitido
```

El estado es monotónico (`openspec/slice-system.md:34`). Con specs vivas, el slice pasa a `shipped` en la rama
antes de mergear, porque mergear despliega (`openspec/slice-system.md:226`). El protocolo no define las
transiciones hacia `blocked` y `deprecated`; por eso aparecen sin flechas.

## e. Invariantes del dominio

1. **Una X vale 7** y ninguna nota imputada lo supera (`FALLO = 7`): `tools/patterns.py:63`, `tools/standings.py:92`.
2. **La identidad es el id de Slack; el nombre es presentación**: ni un renombre ni un apodo cambian quién es
   alguien. `tools/add_results.py:5`, `v2/js/router.js:19`, `v2/js/domain/apodos.js:4`.
3. **Un resultado por jugador y jornada**; reingerir actualiza, no duplica. `tools/add_results.py:34`,
   `openspec/decisions/0005-hosting-y-convivencia-v1-v2.md:102`.
4. **La fecha sale del número de jornada**, nunca del reloj ni de la hora de publicación: `tools/add_results.py:60`.
5. **Una temporada es un mes natural**; lo anterior a `INICIO_TEMPORADAS = "2026-08"` es la temporada 0:
   `tools/seasons.py:39`, `tools/seasons.py:51`.
6. **Un día cuenta si es laborable y lo jugaron al menos `MUESTRA_MINIMA_DEL_DIA = 5` personas** (salvo en la
   temporada 0); la web repite la constante y un test exige que coincidan. `tools/seasons.py:30`,
   `tools/seasons.py:99`, `tools/calendario.py:42`, `v2/js/domain/superbros.js:79`.
7. **La temporada en curso se deriva de los datos**, no del reloj: `tools/seasons.py:131`.
8. **Faltar nunca mejora la media**: la imputación es al menos la media personal más un margen creciente; en el
   álbum, el denominador son las jornadas de la temporada. `tools/standings.py:90`, `tools/album.py:95`,
   `openspec/slices/ranking/clasificacion-de-temporada.md:64`.
9. **La misma cifra publicada comparte puesto** (1, 1, 3) y quien no clasifica aparece sin puesto:
   `tools/standings.py:185`, `openspec/slices/ranking/empates-comparten-puesto.md:41`.
10. **Figuras y medallas se derivan, no se guardan**: `tools/figures.py:9`, `tools/badges.py:8`.
11. **Un cambio de reglas de figuras no es retroactivo** (`PRIMERA_JORNADA_DEL_ORDEN_NUEVO = 1694`): `tools/figures.py:86`.
12. **El álbum y las medallas no alteran el marcador**; el álbum solo lo usa para desempatar:
    `tools/seasons.py:226`, `tools/rules.py:267`, `tools/album.py:211`.
13. **La web no recalcula**: pinta la instantánea que materializa Python, así que bot y web dicen lo mismo.
    `openspec/decisions/0008-donde-vive-el-calculo.md:61`, `tools/seasons.py:218`.
14. **Una instantánea por temporada, con su procedencia** (`calculado_con`): `tools/materialize_seasons.py:38`,
    `tools/seasons.py:234`.
15. **La lista de soluciones nunca se lee más allá de la última jornada jugada** y nada calculado lleva palabras:
    `tools/palabra.py:63`, `tools/indicadores.py:157`, `tools/seasons.py:243`.
16. **Un nivel congelado no cambia y solo el último congelado admite marcas**:
    `supabase/migrations/20260925140000_create_game_levels.sql:41`, `supabase/migrations/20260930120000_close_levels_and_rank_by_stars.sql:54`.
17. **Una marca solo se sobrescribe si mejora** (más estrellas, o las mismas en menos tiempo) y nunca baja del
    tiempo mínimo físico del nivel: `supabase/migrations/20260930120000_close_levels_and_rank_by_stars.sql:62`,
    `supabase/migrations/20260930120000_close_levels_and_rank_by_stars.sql:71`.
18. **Una persona, un voto**, por votación y por propuesta; votar otra vez lo cambia:
    `supabase/migrations/20261014120000_create_rule_debate.sql:32`, `supabase/migrations/20261015090000_public_votable_proposals.sql:20`.
19. **Solo vota, propone o registra marca quien ha jugado alguna vez**: `supabase/migrations/20261014120000_create_rule_debate.sql:87`,
    `supabase/migrations/20261014120000_create_rule_debate.sql:112`, `supabase/migrations/20260930120000_close_levels_and_rank_by_stars.sql:40`.
20. **Una votación cerrada no admite votos; una propuesta rechazada ni se ve ni se vota; como mucho tres
    pendientes por autor**: `supabase/migrations/20261014120000_create_rule_debate.sql:75`,
    `supabase/migrations/20261014120000_create_rule_debate.sql:105`,
    `supabase/migrations/20261015090000_public_votable_proposals.sql:38`.
21. **La clave pública no escribe en ninguna tabla**, solo lee y llama a funciones RPC:
    `openspec/decisions/0005-hosting-y-convivencia-v1-v2.md:105`, `supabase/migrations/20261014120000_create_rule_debate.sql:56`.
22. **Todo cambio de esquema es aditivo** mientras la v1 siga publicada:
    `openspec/decisions/0005-hosting-y-convivencia-v1-v2.md:90`.
23. **Del canal solo se persiste el resultado**; las señales son números y horas, sin texto: `tools/senales.py:8`.
24. **Sin reloj ni azar fuera del borde**: la fecha y los datos entran por parámetro. `openspec/slice-system.md:309`.

## f. Flujos

```mermaid
flowchart LR
  subgraph sgSlack["Slack"]
    canal["Canal del grupo"]
  end
  subgraph sgPipe["Pipeline, GitHub Actions"]
    extract["extract_slack.py"]
    add["add_results.py"]
    mat["materialize_seasons.py"]
    cong["congelar_nivel.mjs"]
    rank["post_ranking.py"]
    pod["post_podium.py"]
  end
  subgraph sgSupa["Supabase"]
    wr[("wordle_results")]
    ss[("season_snapshots")]
    gl[("game_levels")]
    gt[("game_times")]
    deb[("rule_polls, rule_votes, rule_proposals, rule_proposal_votes")]
    fnT{{"registrar_tiempo"}}
    fnD{{"votar_regla, proponer_regla, votar_propuesta"}}
  end
  subgraph sgWeb["Web v2, Cloudflare"]
    web["Vistas de la v2"]
  end
  sol["Lista de soluciones del juego"]
  ia["Clasificador externo del tono"]
  dueno["Dueño, SQL manual"]

  canal -->|"ventana de 14 días"| extract
  extract -->|"líneas USER_START"| add
  add -->|"upsert por jugador y jornada"| wr
  wr & gl & gt --> mat
  sol -->|"solo hasta la última jornada"| mat
  mat -->|"upsert por temporada"| ss
  wr --> cong
  cong -->|"insert, después inmutable"| gl
  ss & gl & gt & deb --> web
  wr -->|"vistas hoy y datos"| web
  web --> fnT --> gt
  web --> fnD --> deb
  dueno -->|"aprobar, rechazar, abrir o cerrar"| deb
  wr & gl & gt & sol --> rank
  canal -->|"señales e hilo del día"| rank
  rank -->|"hilo"| ia
  ia -->|"tono, sin texto libre"| rank
  web -->|"captura de pantalla"| rank
  rank -->|"captura y mensaje, noches laborables"| canal
  wr --> pod
  pod -->|"podio del mes, días 1 a 3"| canal
```

- **Sincronización** (`update_stats.yml`): un latido que encadena `extract_slack.py | add_results.py`,
  `materialize_seasons.py` y `congelar_nivel.mjs` (`.github/workflows/update_stats.yml:112`). Requisito:
  `MINIMO_DIARIO = 12` ejecuciones al día y huecos de como mucho `HUECO_MAXIMO_EN_HORAS = 2.0`
  (`tools/cadencia.py:18`, `tools/cadencia.py:21`).
- **Publicación diaria** (`post_ranking.yml`): tres ventanas de lunes a viernes por la noche; vuelve a ingerir
  antes de capturar y es idempotente por el título de la imagen (`.github/workflows/post_ranking.yml:22`,
  `tools/post_ranking.py:567`). El último laborable del mes publica la victoria en lugar del resumen
  (`tools/post_ranking.py:688`).
- **Cierre de mes** (`post_podium.yml`): días 1 a 3, solo si el mes no se celebró ya
  (`.github/workflows/post_podium.yml:15`, `tools/post_ranking.py:185`).
- **Escrituras de la web**, siempre por RPC (`v2/js/data/results.js:111`, `v2/js/data/results.js:189`); el bot
  no recalcula a su manera: usa los mismos módulos que la instantánea (`tools/resumen.py:8`).

## g. Ontología del método

```mermaid
classDiagram
  direction LR
  Slice : +status text
  Capability : +nombre text
  CapabilitySpec : +ruta path
  Requirement : +checks list
  Requirement : +verified_by list
  Escenario : +slug text
  Test : +scenarios list
  Trigger : +type text
  Surface : +nombre text
  ChangePack : +change_id text
  RunRecord : +gates map
  Leccion : +estado text

  Slice "0..*" --> "1..*" Capability : cruza
  Capability "1" *-- "1" CapabilitySpec : se describe en
  CapabilitySpec "1" *-- "1..*" Requirement : contiene
  Slice "1" *-- "1..*" Escenario : declara
  Escenario "1" --> "1..*" Test : demostrado por
  Requirement "1" --> "0..*" Test : demostrado por
  Slice "1" --> "1" Trigger : se dispara por
  Trigger "0..*" --> "1" Surface : vive en
  Gate ..> Slice : valida
  Gate ..> Requirement : valida
  ChangePack "1" *-- "1..*" RunRecord : registra
  RunRecord ..> Gate : anota el resultado de
  Leccion ..> Gate : nace de un fallo en
```

- Un slice **cruza** todas las capabilities que declara en `specs:[]`; multi-spec es la norma
  (`openspec/slice-system.md:21`). La capability spec es una **spec viva** que se edita en la misma rama que el
  código (`openspec/slice-system.md:121`); el change pack queda como registro mínimo con `runs.yaml`
  obligatorio (`openspec/slice-system.md:132`).
- Un Requirement necesita `checks:` o `verified-by:` (`openspec/slice-system.md:87`); cada escenario, al menos
  un test que lo declare con `@scenarios` (Gate 2, `openspec/slice-system.md:151`).
- Las lecciones se codifican en el punto más fuerte posible y se registran en `docs/lecciones.md`
  (`openspec/slice-system.md:334`).

Reglas de trigger y surface (`openspec/slice-system.md:61`, `openspec/README.md:40`):

| Trigger | Surface válida | Estado |
|---|---|---|
| `ui` | `web` | disponible; nunca sobre un módulo interno |
| `cron` | `pipeline` (GitHub Actions) | disponible |
| `command` | `pipeline` (script a mano) | disponible |
| `http` | ninguna todavía | reservado |
| `event` | ninguna todavía | reservado |
