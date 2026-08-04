# Diario de desarrollo — wordle-stats

> **Propósito:** registro didáctico y cronológico de cómo se construye este proyecto: qué se hizo,
> por qué, qué alternativas se descartaron y qué se aprendió. Si alguien (humano o agente) llega
> nuevo, este documento cuenta la historia que el código no cuenta.
>
> **Convención de entradas:** fecha + qué / por qué / decisión (con descartes) / aprendizaje.
> Se añade entrada en cada hito: decisión de arquitectura, slice completado, cambio de método.
> Estilo: presente atemporal, honesto con los errores.

---

## 2025-11 a 2026-05 — La v1: de un JSON a un pipeline automático

**Qué.** El proyecto nace como una web estática con los resultados escritos a mano en
`data/data.json` y evoluciona hasta el pipeline actual: un bot lee el canal de Slack cada hora,
parsea los mensajes de resultado, los sube a Supabase, y un workflow diario publica una captura del
ranking en el canal.

**Decisiones que quedaron en el código, sin documentar en su momento:**
- **La fecha se deriva del número de puzzle, no del timestamp del mensaje** (ancla: el #1485 es el
  2026-01-30). Es lo que hace que el dato sea correcto aunque alguien publique su resultado con dos
  días de retraso. Verificado: las 1530 filas son coherentes con el ancla.
- **Supabase con RLS de solo lectura** para la clave pública: la web lee directamente desde el
  navegador sin backend propio. Verificado: con la clave publicable, insert da 401 y delete no borra.
- **El almacenamiento pasó de JSON a Supabase** y `data/data.json` quedó congelado (251 registros,
  hasta el 2026-01-30) sin que el README lo reflejara.

**Aprendizaje.** El sistema funciona y lleva meses en pie, pero todo el conocimiento está implícito:
los umbrales del ranking, el mapeo de nombres, el ancla de fechas. Nada de eso es verificable ni
tiene tests, y los intentos de arreglar la identidad de jugadores dejaron el código con una migración
a medias (ver `docs/lecciones.md`).

## 2026-08-04 — Adopción del desarrollo por specs y slices

**Qué.** Antes de abrir la v2.0 se instala el método spec-driven por slices de `pga-cms`: la
constitución (`openspec/slice-system.md`), las tres capas (slice → capability spec → tests), los
change packs con deltas, los ADRs, el pipeline de contexto, el registro de lecciones y un harness
que hace los gates mecánicos.

**Por qué ahora.** La v2.0 va a tocar exactamente lo que hoy está sin especificar: identidad de
jugadores, temporadas y ranking. Hacerlo sin especificación previa repetiría el patrón de la
migración a medias. Y hay una fecha real: el grupo acordó reiniciar el marcador el 1 de septiembre.

**Decisiones (con descartes):**
- **Harness en Python** (`tools/wslice`), no el port TypeScript de `slspec`. El repo no tiene Node ni
  build y Python ya es el stack del pipeline. El escáner de `@scenarios` se hizo **multi-lenguaje**
  (Python, JS, TS) a propósito: así el harness no ata la decisión de stack de la v2.0.
  *Descartado:* copiar `slspec` tal cual — habría metido pnpm y tsc en un repo de HTML estático.
  *Descartado:* renunciar al harness y dejar los gates como checklist — es justo lo que hace que el
  método se relaje cuando aprieta el tiempo.
- **7 capabilities** inferidas del sistema en producción, separando `resultados` (el almacén) de
  `ingesta` (la captura) y sacando `identidad` como dominio propio, porque ahí están los bugs.
  *Descartado:* 4 dominios más gruesos — habrían escondido identidad dentro de ingesta.
- **Protocolo completo**, incluidos los gates de mutación (4c) y adversarial (4d). Este repo no tiene
  usuarios de pago ni datos críticos: es el sitio ideal para rodar el método completo y aprender
  dónde duele.
- **Ramas `feat/… → main`** sin `develop`: un solo desarrollador. Con una consecuencia que hay que
  tener presente — **mergear a `main` despliega** (ADR 0003).

**Aprendizaje.** El primer artefacto que produce el método es el registro de sus propias deudas: el
gate de `test-commands` solo comprueba una expresión regular, y eso queda escrito como lección
pendiente en lugar de disimulado. Un harness honesto sobre sus límites es más útil que uno que
aparenta cubrirlo todo.

**Y el método se estrenó cazando cosas en su propia instalación.** La prueba de mutación (Gate 4c)
sobre el harness dio tres hallazgos que ninguna revisión de código habría dado:

1. Un mutante **sobrevivió** — el filtro `.md` del gate `federated-untouched` no estaba cubierto por
   ningún test. Al escribir los tests que faltaban, uno falló contra el código sano y destapó un
   agujero real heredado del port: `git status --porcelain` colapsa un directorio entero sin trackear
   en una línea, así que una capability nueva completa esquivaba el gate. Arreglado con
   `--untracked-files=all`.
2. El **bytecode cacheado** falseó un veredicto: tras restaurar un mutante, los tests seguían rojos
   con el código ya correcto porque el `.pyc` del mutante tenía el mismo tamaño y el mismo mtime al
   segundo. Podría haber fallado al revés — un mutante dando el gate por bueno. De ahí que ahora todo
   comando de test lleve `-B`.
3. Un `git restore` se llevó un arreglo hecho a mitad del gate, porque el index no se había
   actualizado. Ahora el procedimiento lo dice.

Las tres son reglas codificadas, no anécdotas (`docs/lecciones.md`). El orden importa: el mutante que
sobrevive no se tapa reforzando el test a ojo — se investiga, y a veces lo que aparece es un bug.
