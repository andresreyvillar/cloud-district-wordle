---
adr: 0001
titulo: Desarrollo por specs y slices verificables
estado: aceptado
fecha: 2026-08-04
decide: Andrés Rey
afecta: [todas]
---

## Contexto

La v1 lleva meses funcionando (1530 resultados, ~13 jugadores activos, publicación diaria en Slack) y
se construyó a base de commits directos a `main` sin especificación ni tests. El conocimiento del
dominio vive implícito en el código: el ancla de fechas del puzzle, los umbrales del ranking (mínimo
5 partidas para "mejor media", 3 para el gráfico de burbujas), el mapeo de nombres de jugadores, la
regla de que una X cuenta como 7.

Eso ya produjo un fallo concreto: el cambio que debía pasar la identidad de jugador a
`slack_user_id` quedó a medias — el código lo aparenta pero el extractor sigue emitiendo nombres
mostrados, y hay jugadores duplicados por renombre en Slack (`Marcos Granado` / `marcos.granado`) y
resultados mal atribuidos (ver `docs/lecciones.md`).

La v2.0 va a tocar justo lo que hoy no está especificado: identidad, temporadas y ranking, con una
fecha real de por medio (el grupo acordó reiniciar el marcador el 1 de septiembre).

## Opciones

**A. Seguir como hasta ahora.** Commits directos, verificación a ojo.
*Pro:* velocidad inmediata, cero ceremonia. *Contra:* es el proceso que produjo la migración a
medias; con temporadas y fusión de jugadores el riesgo de corromper el histórico es real.

**B. Añadir tests sin método.** Suite de pytest sobre el código actual.
*Pro:* barato, ataca lo más urgente. *Contra:* los tests fijarían el comportamiento actual sin que
nadie haya decidido cuál debe ser; no hay dónde escribir la decisión ("¿los findes cuentan?").

**C. Método spec-driven por slices de `pga-cms`.** Tres capas (slice → capability spec → tests),
change packs con deltas, gates mecánicos, TDD rojo antes de implementar.
*Pro:* la decisión de producto queda escrita y verificable antes del código; el repo se convierte en
campo de pruebas del método sin riesgo de producción real. *Contra:* ceremonia notable para un
proyecto pequeño; cada cambio cuesta más que un commit directo.

## Decisión

**Opción C.** Se adopta el protocolo completo, incluidos los gates de mutación (4c) y auditoría
adversarial (4d), con las desviaciones documentadas en §9 de la constitución.

El argumento decisivo no es el tamaño del proyecto sino la naturaleza del cambio que viene: reiniciar
el marcador y unificar identidades toca datos históricos de personas reales, y eso conviene decidirlo
por escrito antes de escribirlo en código.

## Consecuencias

**Se vuelve fácil:** decidir reglas del juego por escrito antes de implementarlas; saber qué protege
cada test; revertir un cambio entero de un tirón; que un agente implemente sin inventar.

**Se vuelve difícil:** los cambios pequeños. Un arreglo de una línea pasa por change pack
`Slice: N/A`. Se acepta a cambio de que lo que toca comportamiento observable no pueda colarse sin
especificación.

**Coste asumido:** el propio harness es código sin producto detrás. Se limita a lo que hace de
verdad un gate mecánico (~1200 líneas Python con 52 tests) y se declara honestamente lo que solo
aparenta verificar (ver la lección del gate `test-commands`).
