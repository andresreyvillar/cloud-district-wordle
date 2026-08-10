---
slice: clasificacion-de-figuras
status: proposed
kind: scheduled
actor: sistema
trigger:
  type: cron
  surface: pipeline
  detail: "0 * * * * — workflow update_stats.yml: materialize_seasons.py"
events:
  emits: []
  consumes: []
specs:
  - ranking
  - resultados
tests_root: tests/slices/clasificacion-de-figuras/
blocked: null
---

# La instantánea publica el álbum de figuras de la temporada

**Actor:** sistema (workflow horario)
**Trigger:** la materialización de la temporada, después de ingerir

## Contexto

El patrón crudo ya se guarda ([[captura-del-patron]]) y el histórico está completo
([[backfill-de-patrones]]): 1502 de los 1502 resultados que cuentan en la temporada 0 tienen su
cuadrícula. El clasificador ya existe y está calibrado (`tools/figures.py`, 24 de 30 etiquetas humanas).
Lo que falta es **el paso que los une**: nadie deriva la categoría, así que ningún consumidor puede verla.

Este slice cierra ese hueco por el lado de los datos. La instantánea de temporada pasa a llevar el
**álbum**: cuántas partidas de cada categoría lleva cada jugador, qué proporción de sus partidas dejó una
figura reconocible, y en qué puesto del ranking de belleza queda.

La categoría **no se almacena en ninguna columna**: se deriva del patrón cada vez que se materializa. Es lo
que hace que recalibrar un umbral reclasifique el histórico solo, sin migración
([brief](../../../docs/context/briefs/ranking-de-figuras.md)).

El cálculo vive en Python y no en la web por la misma razón que el resto del ranking
([ADR 0008](../../decisions/0008-donde-vive-el-calculo.md)): el bot va a publicar el álbum en el canal y la
web va a pintarlo, así que las dos cosas tienen que salir del mismo cálculo por construcción. Un
clasificador reimplementado en JavaScript sería una segunda verdad.

## Trigger técnico

`materialize_seasons.py`, que el workflow `update_stats.yml` ejecuta cada hora tras la ingesta. Lee
`wordle_results` —ahora también la columna `pattern`— y escribe la carga útil de la temporada en
`season_snapshots`.

## Comportamiento observable

### figura-de-cada-partida
**WHEN** se materializa una temporada
**THEN** cada jugador lleva el recuento de sus partidas por categoría, derivado del patrón crudo de cada
resultado y sin que la categoría se almacene en ninguna columna.

### espejo-exacto-es-geometrico
**WHEN** una cuadrícula que iba a salir abstracta tiene todas las filas del cuerpo iguales leídas al revés
**THEN** cuenta como geométrica, aunque tenga demasiada tinta para el techo de densidad.

### una-celda-rota-no-es-espejo
**WHEN** una sola celda rompe la simetría de una cuadrícula
**THEN** el espejo no se le concede, y la partida sigue siendo abstracta.

### el-espejo-no-le-quita-figura-a-nadie
**WHEN** una cuadrícula simétrica ya se reconoce como loro, como flor o como geométrica por su densidad
**THEN** conserva esa categoría: el espejo solo se consulta cuando ninguna otra regla reconoce nada.

### cuerpo-vacio-no-es-espejo
**WHEN** se acierta a la primera y la cuadrícula es solo la banda verde
**THEN** la partida sigue siendo abstracta: no hay cuerpo que pueda ser simétrico.

### patron-fallado-no-es-espejo
**WHEN** una cuadrícula simétrica no llega a resolver la palabra
**THEN** la partida sigue siendo abstracta, porque sin banda final no hay dibujo que reconocer.

### sin-patron-no-cuenta
**WHEN** un resultado que cuenta en la temporada no tiene patrón
**THEN** no se le inventa categoría —no cuenta como figura ni como abstracto— y la instantánea publica
cuántas partidas se quedaron sin clasificar.

### tasa-de-figuras-por-partida
**WHEN** un jugador tiene partidas clasificadas
**THEN** su puntuación del álbum es la proporción de esas partidas que dejaron una figura reconocible, no
el recuento absoluto, de modo que quien juega más no gana por jugar más.

### abstracto-se-registra-y-no-puntua
**WHEN** una partida sale abstracta
**THEN** aparece en el recuento del jugador y **rebaja** su tasa, en lugar de desaparecer del álbum.

### minimo-de-partidas-para-clasificar
**WHEN** un jugador tiene menos partidas clasificadas que el mínimo
**THEN** su álbum se publica igual pero sin puesto, y no puede encabezar el ranking de belleza.

### orden-determinista-del-album
**WHEN** dos jugadores empatan en tasa
**THEN** va delante quien aportó más figuras, y a igualdad de figuras, el orden es por nombre — nunca el
orden en que la base de datos devolvió las filas.

### el-album-hereda-los-dias-de-la-temporada
**WHEN** un resultado no cuenta en la temporada
**THEN** su patrón tampoco entra en el álbum, sin una segunda definición de qué día cuenta.

### temporada-sin-patrones-no-inventa-ranking
**WHEN** ninguna partida de la temporada tiene patrón
**THEN** el álbum sale vacío y declarado como tal, sin ranking ni campeón de belleza.

## Estado después

La carga útil de `season_snapshots` gana una clave `album` con el reparto de la temporada, el vocabulario
de emojis y una fila por jugador. Ninguna clave anterior cambia, así que la web actual sigue funcionando
sin tocarla.

Con los datos de hoy:

| Temporada | Cuentan | Con patrón | Álbum |
|---|---|---|---|
| 0 · el histórico | 1502 | 1502 (100%) | 21 jugadores, 18 con puesto · líder al 83% (71/86) |
| 1 · agosto 2026 | 80 | 19 (24%) | 11 jugadores, **ninguno con puesto** |

Agosto está así porque `captura-del-patron` **todavía no está en `main`**: el cron que escribe a diario
corre con el código anterior y descarta la cuadrícula, así que 61 de sus 80 filas no tienen patrón. Nadie
llega a cinco partidas clasificadas y el mes se queda sin ranking de belleza hasta que la rama se mergee.
Publicar el hueco es deliberado — un ranking calculado sobre el 24% de las partidas sería una tabla falsa
con aspecto de tabla buena.

Nadie pinta esto todavía: la vista es [[album-de-figuras]] (TBD), el punto 5.4 del roadmap.

## Edge cases

- **Partida sin patrón**: no entra en el denominador de la tasa. Contarla como abstracta castigaría a quien
  jugó cuando el pipeline aún no guardaba cuadrículas, que es un fallo del sistema y no del jugador.
- **Temporada 0 y los fines de semana**: la temporada 0 cuenta todas las jornadas con resultados, fines de
  semana incluidos, porque se rige por las reglas que estaban en vigor cuando se jugó. El álbum hereda esa
  definición en lugar de tener la suya: dos definiciones de "qué día cuenta" ya divergieron dos veces en
  este repositorio.
- **Jugador con una sola partida**: sale en el álbum sin puesto. Verse en el sitio de uno informa más que no
  verse, y es lo mismo que hace la tabla de puntuación.
- **Reejecución**: el álbum se recalcula entero en cada materialización. No acumula ni depende de la
  instantánea anterior.
- **Recalibrar el clasificador**: cambia el álbum de todo el mundo en la siguiente materialización, sin
  migración. Es el precio declarado de no almacenar la categoría.
- **Simetría y densidad se contradicen**: un dibujo regular con mucha tinta cumple el espejo y no cumple el
  techo de densidad. Manda el espejo, porque es la señal que no crece con el tamaño de la cuadrícula.
- **Simetría solo respecto al eje vertical**: una escalera es regular respecto a la diagonal y no cumple el
  espejo. Sigue saliendo abstracta, y es una limitación conocida, no un descuido.

## Slices compañeros

- [[captura-del-patron]] — guarda la cuadrícula que aquí se clasifica.
- [[backfill-de-patrones]] — la trajo para el histórico.
- [[album-de-figuras]] (TBD) — la vista: la tira agrupada y el ranking de belleza.
- [[clasificacion-de-temporada]] — el otro ranking, el de puntuación. Independiente por decisión explícita.
