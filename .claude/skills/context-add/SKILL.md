---
name: context-add
description: Ingesta de contexto al proyecto — conversaciones del canal de Slack, hilos con propuestas de reglas, capturas, notas o datos de la BD. Ejecuta el pipeline ficha → destilado (tabla a validar) → brief → propuesta de canonización. Usar cuando el usuario aporte material nuevo ("mete lo que se dijo en el hilo", "ingesta esta conversación", archivos en docs/context/inbox/) o pegue información del grupo en la conversación.
---

# /context-add [ruta | "hilo de Slack" | "nota: ..."]

**Modelo completo:** `docs/context/INDEX.md` (jerarquía de verdad y convenciones).
**Principio:** el contexto crudo NUNCA llega a un slice — solo lo destilado y canonizado.

## Entradas aceptadas
1. **Canal o hilo de Slack** — la fuente principal de requisitos de este proyecto. El grupo decide
   las reglas del juego conversando; esas decisiones son el material de entrada.
2. **Archivo**: ruta pasada como argumento, o todo lo que haya en `docs/context/inbox/`.
3. **Nota de conversación**: texto directo ("nota: acordamos que los findes no cuentan").
4. **Estado de los datos**: una consulta a Supabase que revele un hecho relevante (p. ej. cuántos
   jugadores duplicados hay). Se ficha como fuente con la consulta exacta usada.

## Pipeline (por cada pieza)

### 1. Ficha → `docs/context/sources/<fecha>-<slug>.md`
Usar `docs/context/_ficha-template.md`. Inferir todo lo posible (tipo, fecha, capabilities);
preguntar SOLO lo no inferible (típicamente `autoridad`: ¿es una decisión del grupo o una opinión?).
De un hilo de Slack: extraer decisiones, propuestas y objeciones — **jamás volcarlo entero**.

### 2. Destilado → tabla de validación (ÚNICO punto de decisión humana)
Clasificar cada afirmación relevante y presentar tabla ANTES de escribir:

| Afirmación | Clasificación |
|---|---|
| cambia comportamiento observable | → escenario/Requirement (candidato a slice) |
| explica un porqué con alternativas | → ADR |
| define un término del dominio (temporada, racha, fallo) | → glosario |
| es forma de trabajar | → CLAUDE.md / skill |
| contexto de fondo útil | → brief |
| no afecta al producto | → paja (queda en la ficha como "no destilado") |

Esperar confirmación/corrección del usuario.

### 3. Escribir brief → `docs/context/briefs/<tema>.md`
- **Por TEMA, no por fuente**: si el brief del tema existe, ACTUALIZARLO (no crear otro).
- Máx 1-2 páginas · presente atemporal · **cada afirmación cita su fuente** (`../sources/...`).
- Si la nueva info contradice un brief/ficha existente → marcar lo viejo `superseded`, actualizar,
  y añadir entrada al diario (`docs/diario-desarrollo.md`).

### 4. Actualizar `INDEX.md`
Fila en Fuentes (+ Briefs si hay nuevo) con estado y capabilities.

### 5. Proponer canonización (NUNCA ejecutarla en caliente)
- Candidatos a slice → ofrecer `/slice-propose`.
- Términos → ofrecer añadir al glosario.
- Decisiones → ofrecer ADR en `openspec/decisions/`.
El usuario decide; specs/slices/ADRs siempre pasan por su confirmación.

## Guardarraíles
- NUNCA borrar material: la paja se declara en la ficha, no se elimina.
- **Privacidad:** los mensajes son de compañeros de trabajo reales. En fichas y briefs se registran
  las decisiones, no las conversaciones personales; nada de citas literales innecesarias ni de
  material sensible. El repo es público.
- NUNCA meter en el repo capturas con información de terceros ni exports crudos del canal.
- NUNCA editar `openspec/specs/` desde esta skill (federated-untouched — eso es de los slices).
