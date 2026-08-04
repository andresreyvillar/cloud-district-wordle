# Decisiones de arquitectura (ADRs) — wordle-stats

Registro de las decisiones que condicionan el resto del proyecto. Una decisión vive aquí cuando
**explica un porqué con alternativas descartadas** — si es solo una regla de trabajo, va a
`CLAUDE.md`; si es comportamiento observable, es un slice.

## Convención

- Nombre: `NNNN-<slug-kebab>.md`, numeración correlativa y estable.
- `estado`: `propuesto` → `aceptado` | `descartado` | `superseded por NNNN`.
- Un ADR **aceptado no se reescribe**: si la decisión cambia, se escribe uno nuevo que lo supersede.
  Historia inmutable, igual que los slices.
- Toda decisión se **firma por un humano**. El agente propone; nunca acepta un ADR por su cuenta.
- Cada afirmación de contexto cita su fuente (código, consulta a la BD, brief de `docs/context/`).

## Estructura de un ADR

```markdown
---
adr: NNNN
titulo: <frase>
estado: propuesto
fecha: AAAA-MM-DD
decide: <quién firma>
afecta: [capabilities o "todas"]
---

## Contexto        ← qué problema, con evidencia citada
## Opciones        ← las reales, con pros y contras honestos
## Decisión        ← EN BLANCO hasta que un humano la firme
## Consecuencias   ← qué se vuelve fácil y qué se vuelve difícil
```

## Índice

| ADR | Título | Estado |
|---|---|---|
| [0001](0001-desarrollo-por-slices.md) | Desarrollo por specs y slices | **aceptado** |
| [0002](0002-harness-en-python.md) | Harness en Python, agnóstico de stack | **aceptado** |
| [0003](0003-modelo-de-ramas-y-despliegue.md) | Modelo de ramas — el merge a `main` es el despliegue | **aceptado** |
| [0004](0004-stack-de-la-v2.md) | Stack de la v2.0 | **aceptado** — vanilla + módulos ES, sin build |
| [0005](0005-hosting-y-convivencia-v1-v2.md) | Hosting de la v2.0 y convivencia con la v1 | **aceptado** |
| [0006](0006-estructura-de-informacion-v2.md) | Estructura de información y rutas de la v2.0 | **aceptado** |
| [0007](0007-libreria-de-graficos.md) | Librería de gráficos y forma de las visualizaciones | **aceptado** — la forma antes que la librería |
