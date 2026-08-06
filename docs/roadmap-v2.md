# Roadmap v2.0 — propuesta

> **Estado: propuesta.** Este documento ordena el trabajo; no lo autoriza. Cada línea marcada como
> slice se especifica con `/slice-propose` y se implementa con `/slice-implement`, con su change pack.
>
> **Qué está cerrado y qué no.** Lo único decidido por el grupo es que **el ranking pasa a ser mensual
> con reset el día 1** (votación 6-0). Todo lo demás que salió en el hilo de Slack son ideas en bruto:
> están en el backlog de la Fase 3 y **no se especifican hasta que el grupo las cierre**. Registradas
> en `context/sources/2026-08-04-hilo-reglas-temporadas.md`.

## Qué es realmente la v2.0

No es "añadir temporadas al ranking actual". Es **reestructurar la web** alrededor de un eje que hoy no
existe: el tiempo. La estructura de la v1 —cuatro pestañas que agregan todo el histórico— no puede
representar un marcador que se reinicia cada mes, y la pregunta "¿quién ganó en marzo?" no tiene dónde
vivir.

La estructura acordada está en [ADR 0006](../openspec/decisions/0006-estructura-de-informacion-v2.md):
cinco secciones, selector de temporada como eje, URL propia por vista. El stack, en
[ADR 0004](../openspec/decisions/0004-stack-de-la-v2.md): vanilla con módulos ES y el dominio separado
del render, sin build.

**Y nace con contenido.** Aplicando temporadas mensuales al histórico existente hay **9 temporadas
cerradas y 6 ganadores distintos** desde noviembre de 2025. El archivo no es una promesa: es lo primero
que el grupo va a querer mirar.

## Fecha que manda

El grupo arranca la etapa nueva el **1 de septiembre de 2026**: unas cuatro semanas. El orden importa
más que la ambición, y hay un bloqueo duro.

```
Fase 0  cimientos ──▶ Fase 1  identidad ──▶ Fase 2  la web nueva ──▶ Fase 3  reglas del juego
                                                                     (bloqueada por el grupo)
Fase 4  robustez del pipeline (en paralelo, independiente)
```

**La identidad va antes que la web nueva.** No es preferencia técnica: la sección Jugador necesita un
identificador que hoy no existe (la ruta sería el nombre mostrado de Slack, que cambia), y cualquier
clasificación mensual cuenta mal a quien esté partido en dos por un renombre. Es el único bloqueo duro
del roadmap.

---

## Fase 0 — Cimientos

Sin producto visible. Desbloquea todo lo demás.

| # | Qué | Artefacto | Estado |
|---|---|---|---|
| 0.1 | Confirmar el mecanismo de deploy actual en Cloudflare | investigación | Los tres `?` del [ADR 0005](../openspec/decisions/0005-hosting-y-convivencia-v1-v2.md). **Nada se escribe hasta cerrarlos** |
| 0.2 | Crear el Worker `cloud-district-wordle-2` con fallback SPA | change pack `Slice: N/A` | `not_found_handling: single-page-application`. La v1 no se toca |
| 0.3 | Esqueleto de la v2.0: módulos, router, arranque | change pack `Slice: N/A` | Separado del primer slice a propósito, para que el Gate 4c distinga plantilla de comportamiento |

## Fase 1 — Identidad

| # | Slice candidato | Capabilities | Qué resuelve |
|---|---|---|---|
| 1.1 | `identidad-estable-por-id-de-slack` | ingesta · identidad · resultados | El extractor emite el ID de Slack, no el nombre mostrado. Hoy 1234 de 1532 filas guardan un nombre en la columna de ID. Define el identificador de la ruta `/j/<jugador>` |
| 1.2 | `fusion-de-jugadores-duplicados` | identidad · resultados | Un jugador partido en dos por un renombre; 8 filas atribuidas al jugador equivocado; 6 filas duplicadas |

Restricción del [ADR 0005](../openspec/decisions/0005-hosting-y-convivencia-v1-v2.md): **el esquema
solo crece**. La fusión no puede hacerse borrando `player_name` — la v1 lo lee.

## Fase 2 — La web nueva

El corazón de la v2.0 y lo imprescindible para el 1 de septiembre.

| # | Slice candidato | Capabilities | Ruta | Qué resuelve |
|---|---|---|---|---|
| 2.1 | `temporada-mensual` | ranking · resultados | — | El modelo: qué es una temporada, cómo se deriva del histórico, reset el día 1. **Lo único cerrado por el grupo** |
| 2.2 | `clasificacion-de-temporada` | ranking · estadisticas · dashboard | `/` · `/t/<AAAA-MM>` | La vista del mes: clasificación y podio, con el **modelo de imputación** ya acordado ([brief](context/briefs/reglas-temporadas.md)) |
| 2.3 | `archivo-de-temporadas` | ranking · dashboard | `/temporadas` | Las 9 cerradas con su ganador + medallero acumulado |
| 2.4 | `resultado-del-dia` | estadisticas · dashboard | `/hoy` | Quién ha jugado, quién falta, cómo se ha dado la palabra |
| ~~2.5~~ | ~~`ficha-de-jugador`~~ | estadisticas · identidad · dashboard | `/t/<AAAA-MM>/j/<x>` | **HECHO el 2026-08-06**: puesto, coste de faltar, desglose jornada a jornada, distribución, medallas y palmarés. La evolución espera la escala fija (4.4) |
| 2.6 | `ruta-invalida` | dashboard | cualquiera | Con el fallback SPA el 404 desaparece: la ruta inválida se detecta en cliente o el usuario ve una página vacía |
| 2.7 | `tabla-de-datos` | dashboard | `/datos` | Portar la tabla cruda de la v1 |

**Lo que NO entra en la Fase 2** aunque parezca que toca: los podios separados por intentos y por
participación (¿cuál es el criterio del podio principal?), el umbral de elegibilidad y la nota
ponderada. Todo eso es Fase 3: son reglas del juego sin decidir. La Fase 2 muestra la clasificación con
el criterio actual (media de intentos) y deja el resto como espacio reservado.

## Fase 3 — Reglas del juego (bloqueada por el grupo)

**Ninguna de estas líneas se especifica hasta que el grupo cierre la regla.** El roadmap no las ordena
por prioridad técnica sino por dependencia de una decisión humana.

| # | Idea del hilo | Qué falta decidir |
|---|---|---|
| ~~3.1~~ | ~~Umbral de participación~~ → **CERRADO**: modelo de imputación por dificultad | Ya no es un umbral. Modelo completo y calibrado en [`context/briefs/reglas-temporadas.md`](context/briefs/reglas-temporadas.md). Pasa a la Fase 2 como parte de la clasificación |
| 3.2 | Podios separados de intentos y de participación | Si son dos podios iguales en jerarquía o uno principal y otro secundario |
| 3.3 | Nota ponderada (media + participación) | Con el modelo de imputación la participación **ya está dentro de la media**: una ponderación extra la contaría dos veces. Probablemente sobra |
| 3.4 | Rachas (mejor y peor) | Qué es una racha: acertar N días seguidos, o mejorar N días seguidos |
| 3.5 | Mayor remontada | Respecto a qué: posición del mes anterior, o dentro del propio mes |
| 3.6 | Cierre de la etapa actual el 31 de agosto | Si se corona un ganador del periodo completo y con qué criterio |
| 3.7 | Ausencias justificadas | Sin decisión del grupo; hoy es una idea suelta |

Recomendación de proceso: llevar al canal **solo el modelo de participación** ya cerrado, para que el
grupo lo valide antes de implementarlo — afecta a quién gana, así que conviene el acuerdo explícito. El
argumento que lo justifica no es la fórmula sino el diagnóstico: **hoy el ranking lo gana quien juega
tres días** (en 6 de 8 meses del histórico el campeón cambia, y en cinco de ellos el campeón actual
jugó menos de la mitad de los días).

Las demás líneas de esta fase pueden esperar sin bloquear el 1 de septiembre. Preguntarlas todas de
golpe en un hilo garantiza que no se cierre ninguna.

## Fase 5 — Ranking de figuras (nonogramas)

Independiente del ranking de puntuación: **no influye en él** por decisión explícita. Diseño completo
en [`context/briefs/ranking-de-figuras.md`](context/briefs/ranking-de-figuras.md).

| # | Slice candidato | Capabilities | Qué resuelve |
|---|---|---|---|
| ~~5.0~~ | ~~*(previo, sin slice)* calibrar el clasificador~~ | pack `feat-calibracion-de-figuras` | **HECHO el 2026-08-06**: `tools/figures.py` acierta 24/30 (80%) y el acuerdo es un gate. Desbloquea el resto de la fase |
| 5.1 | `captura-del-patron` | ingesta · resultados | Columna nueva con el patrón crudo (aditivo). Hoy se descarta: solo se guarda la primera línea del mensaje |
| 5.2 | `backfill-de-patrones` | ingesta · resultados | Recuperar el histórico del canal: comprobado que Slack conserva las cuadrículas a 240 días |
| 5.3 | `clasificacion-de-figuras` | patrones `?` | 🦜 🌷 📐 💩 y 🤔 (no puntúa). Determinista y con golden tests |
| 5.4 | `album-de-figuras` | ranking · dashboard | El ranking de belleza y la tira de emojis por jugador |
| 5.5 | `resumen-diario-compuesto` | publicacion | Sustituye la captura por texto: jugador del día, obra del día, top 5, álbum y comentarios |
| 5.6 | `comentarios-de-la-jornada` | publicacion · estadisticas | Detectores deterministas (sospechoso, sembrado, no inspirado, rajado) + redacción generativa |
| 5.7 | `imagen-de-la-obra-del-dia` | publicacion | Generación de la ilustración. Una al día por coste |

Dos premios separados, no uno: exigir mejor puntuación **y** figura reconocible deja el premio vacío el
94% de las jornadas (medido). La figura sale de las partidas malas — los dos rankings premian a gente
distinta, y eso es deliberado.

## Fase 4 — Robustez del pipeline

Independiente de todo lo anterior. No se ve, pero es donde se pierden datos.

| # | Slice candidato | Capabilities | Qué resuelve |
|---|---|---|---|
| 4.1 | `resultados-publicados-en-hilos` | ingesta | Un resultado dentro de un hilo no se captura: `conversations.history` solo devuelve mensajes raíz, y el grupo usa hilos a diario |
| 4.2 | `ventana-de-ingesta-robusta` | ingesta | La ventana de 50 mensajes y `users_list` sin paginar. Cubre ~5 días: un puente largo con Actions caído pierde días |
| 4.3 | `captura-apunta-a-la-v2` | publicacion | El corte real: una línea en `tools/post_ranking.py`. Aprovechar para que la URL sea configurable |
| 4.4 | `escala-fija-comparable` | dashboard | Misma escala horizontal en todos los gráficos, requisito previo de cualquier animación |

## Fase 6 — Medallas

Tercer eje de juego, independiente del ranking y del álbum. Diseño y umbrales calibrados en
[`context/briefs/medallas.md`](context/briefs/medallas.md).

| # | Slice candidato | Capabilities | Qué resuelve |
|---|---|---|---|
| 6.1 | `medallas-de-rendimiento-y-constancia` | estadisticas · ranking · dashboard | Las siete que **no** dependen del clasificador: Suertud@, El día imposible, Superviviente, Verdugo, Impecable, Pleno, Fondista. Umbrales firmes, calculados sobre puntuaciones y fechas |
| 6.2 | `medallas-de-figuras` | estadisticas · dashboard | Ornitólog@, Arquitect@, Florista, Coleccionista, Abstract@. **Bloqueadas por la calibración del clasificador** (5.0) |
| 6.3 | `anuncio-de-medalla` | publicacion | Anunciar en el resumen diario la medalla que alguien acaba de ganar |

Las medallas son **derivadas, no almacenadas**: se calculan a partir de los resultados. Eso permite
recalibrar un umbral y que el palmarés histórico se recalcule solo, y es la razón por la que 6.1 puede
implementarse aunque los umbrales de figuras cambien después.

## Fuera del roadmap v2.0

| Fuera | Disparador que lo traería |
|---|---|
| Sección de palabras / dificultad del día | Que el grupo la pida. Datos ya disponibles, barata: primera candidata para después del 1 de septiembre |
| Comparador entre jugadores | Que alguien lo pida más de una vez |
| Premios y patrocinios | Broma del hilo |
| Distinciones semanales | Tono, no requisito |
| Retirar la v1 · dominio propio | ADRs propios cuando llegue el momento |
| CI que ejecute los gates, linter, probes de `checks:` | Deuda del harness anotada en el pack de adopción |
