---
name: leccion
description: Ejecuta el bucle error→regla (§11 del protocolo) — convierte un fallo de proceso, error del agente o hallazgo en una regla permanente codificada en el punto más fuerte posible, y la registra en docs/lecciones.md. Usar cuando algo falle con causa raíz identificable, tras un post-mortem, o cuando el usuario diga "hemos aprendido que...", "esto falló", "que no vuelva a pasar".
---

# /leccion "<qué pasó>"

**Principio:** la lección NO es el artefacto — **la regla codificada lo es**. Registrar sin codificar
es acumular deuda (el audit la reporta).

## Pipeline

### 1. Causa raíz (breve, sin ceremonia)
Del síntoma a la causa: ¿qué permitió que pasara? Si la causa es ambigua, 5-whys corto.
Distinguir: fallo del proceso (falta regla) vs fallo puntual sin patrón (no merece regla — decirlo).

### 2. Elegir el punto de codificación (cascada — SIEMPRE el más fuerte alcanzable)
| Nivel | Cuándo | Ejemplos en este repo |
|---|---|---|
| **1. Mecánico** | verificable por máquina | gate nuevo en `tools/wslice`, check en el workflow de Actions, test de regresión |
| **2. Protocolo** | regla del método | `openspec/slice-system.md` (§ que toque) |
| **3. Skill** | operativa de una fase | paso nuevo en `slice-propose/implement/audit`, `context-add` |
| **4. CLAUDE.md** | disciplina del agente | guardrail o convención |

Si el nivel 1 es posible pero costoso ahora → codificar en 2-4 YA y dejar el nivel 1 como
`estado: pendiente` con destino explícito (p. ej. "→ gate en wslice cuando exista X").

### 3. Codificar la regla
Editar el archivo destino. La regla en presente atemporal, accionable, sin narrativa del incidente.

### 4. Registrar → `docs/lecciones.md`
Entrada con el formato del registro (fecha, qué pasó, causa raíz, regla, codificada-en, estado).

### 5. Difundir si procede
- Si la lección cambia el método o una decisión → entrada en `docs/diario-desarrollo.md`.
- Si nace de un run → referenciar el run (`openspec/changes/<id>/runs.yaml`).

## Guardarraíles
- NUNCA registrar sin intentar codificar (o sin destino explícito si queda pendiente).
- NUNCA reglas vagas ("tener cuidado con X") — si no es accionable, no es regla.
- No duplicar: si ya existe regla que debió aplicar, la lección es "¿por qué no se aplicó?"
  (quizá el punto de codificación era débil → subir de nivel en la cascada).
