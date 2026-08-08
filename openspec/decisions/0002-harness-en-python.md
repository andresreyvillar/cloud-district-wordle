---
adr: 0002
titulo: Harness en Python, agnóstico del stack de producto
estado: aceptado
fecha: 2026-08-04
decide: Andrés Rey
afecta: [todas]
---

## Contexto

El método adoptado en [ADR 0001](0001-desarrollo-por-slices.md) necesita un harness que ejecute los
gates mecánicos: validar el frontmatter de los slices, comprobar la cobertura escenario↔test,
verificar los Requirements y agregar los run records.

En `pga-cms` ese harness es `@pga-cms/slspec`: ~1300 líneas de TypeScript ESM con pnpm, zod,
gray-matter, js-yaml y commander, dentro de un monorepo con Turborepo.

Este repo no tiene nada de eso: es HTML + CSS + JavaScript vanilla servido como assets estáticos, y
scripts Python 3.12 para el pipeline (`slack_sdk`, `supabase`, `python-dotenv`). No hay `package.json`,
ni build, ni test runner. Y el stack de la v2.0 está sin decidir ([ADR 0004](0004-stack-de-la-v2.md)).

## Opciones

**A. Portar `slspec` tal cual (TypeScript).**
*Pro:* fidelidad literal a `pga-cms`; el harness sería reutilizable entre los dos proyectos; zod da
validación declarativa. *Contra:* mete Node 20, pnpm y tsc en un repo que hoy no los necesita para
nada más; añade un paso de build antes de poder ejecutar un gate.

**B. Harness en Python.**
*Pro:* Python ya está en el repo y en los workflows; única dependencia nueva es PyYAML, que además
es transitiva de otras; se ejecuta sin build (`python3 -m tools.wslice`). *Contra:* dos
implementaciones del mismo protocolo que pueden divergir; la validación se escribe a mano en lugar de
declararla con zod.

**C. Sin harness: gates como checklist en las skills.**
*Pro:* cero código. *Contra:* un gate sin exit code no es un gate. Es lo primero que se relaja
cuando aprieta el tiempo, y el método entero depende de que los gates sean mecánicos.

## Decisión

**Opción B**, con una condición de diseño: el escáner de anotaciones `@scenarios` es
**multi-lenguaje** desde el principio — entiende comentarios y docstrings de Python y bloques JSDoc
de JavaScript/TypeScript. Así el harness no ata la decisión de stack de la v2.0: si el frontend pasa
a TypeScript con Vitest o Playwright, la cobertura sigue midiéndose sin tocar el harness.

La divergencia con `slspec` se acepta y se acota: el protocolo (`openspec/slice-system.md`) es la
fuente de verdad compartida; las dos implementaciones son intercambiables mientras produzcan los
mismos veredictos. Los nombres de comandos, gates y estados se mantienen idénticos a propósito.

## Consecuencias

**Se vuelve fácil:** ejecutar un gate sin instalar nada (`PyYAML` ya está); testear el harness con
pytest (52 tests hoy); usar el mismo harness cuando el frontend cambie de tecnología.

**Se vuelve difícil:** mantener la paridad con `slspec`. Si `pga-cms` añade un probe nuevo, aquí no
aparece solo. Mitigación: el protocolo manda, y los probes de `checks:` son `indeterminate` en las
dos implementaciones, así que la divergencia real hoy es cero.

**Deuda declarada:** los probes de `checks:` no están implementados en ninguna de las dos
implementaciones. Todo el peso de la verificación recae en `verified-by:`, es decir, en los tests.
Es coherente con el método (TDD obligatorio) pero conviene no llamarlo "verificación mecánica del
contrato" cuando aún no lo es.
