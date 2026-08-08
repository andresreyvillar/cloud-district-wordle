---
name: slice-implement
description: Implementa un slice ya propuesto (Fases 3-4 del protocolo) — carga el change pack como contrato, plan confirmado por humano, TDD rojo→verde, y gates de verify incluidos mutación y adversarial. Usar cuando el usuario pida "implementa el slice X" o tras un /slice-propose aprobado.
---

# /slice-implement <slug> — Fases 3-4 del protocolo

**Constitución:** `openspec/slice-system.md` (§5, §6 Fases 3-4, §7, §8).
**Prerequisito:** slice + change pack existentes (salida de `/slice-propose`). Si no hay change pack
(`grep -l "<slug>" openspec/changes/*/proposal.md`), parar y proponer `/slice-propose`.

## Fase 3.1 — Cargar contexto (el contrato)
Leer, en este orden:
1. `openspec/changes/<change-id>/proposal.md` — Why, Impact, Validation Gates.
2. `openspec/changes/<change-id>/tasks.md` — el plan numerado.
3. `openspec/changes/<change-id>/specs/<capability>/spec.md` — **los deltas SON el contrato**.
4. `openspec/specs/<capability>/spec.md` — estado consolidado (SOLO LECTURA).
5. `openspec/slices/<capability>/<slug>.md` — narrativa y escenarios.

Verificar rama: nunca implementar en `main` → `git switch -c feat/<change-id>`.

## Fase 3.2 — Plan + confirmación humana
Presentar el plan derivado de `tasks.md` (paso → archivos → Requirement que cumple → test).
**Esperar confirmación explícita del usuario antes de tocar código.**

## Fase 3.3 — Implementar (acotado)
- Tocar SOLO módulos de las capabilities en `specs:[]`. NUNCA inventar funcionalidad fuera del delta.
- NUNCA editar `openspec/specs/` ni el slice `.md` durante la implementación.
- **Determinismo (§10):** la fecha y los datos entran por parámetro. Sin `datetime.now()` ni
  `Date.now()` fuera del borde (CLI, cron, carga de página). Es lo que permite golden tests.
- **TDD:** quitar los `skip`/`fixme` de los tests de la Fase 2 → confirmarlos en rojo → implementar
  hasta verde. PROHIBIDO debilitar/vaciar un test para ponerlo verde.
- Nada de escrituras exploratorias contra la tabla de producción: los tests usan fixtures locales.
- Actualizar `verified-by:` en los deltas apuntando a los tests que demuestran cada Requirement.

## Fase 4 — Gates de "aprobable" (todo verde o no hay handoff)
```bash
.venv/bin/python3 -B -m pytest                                                     # 1 tests
node --check js/script.js                                                       # 1 sintaxis del frontend
python3 -m tools.wslice verify slice <slug>                                     # 2 Gate 4a
python3 -m tools.wslice verify gates --slice <slug> --change-id <change-id>     # 3 Gate 1b/4
```
4. **Gate 4b:** por cada Requirement del delta, tabla manual: código localizable (`path:line`) + test.
5. **Gate 4c (prueba de mutación — eficacia de los tests):**
   *(Si `mutmut` está configurado: ejecutarlo sobre los archivos del diff y exigir 0 mutantes
   supervivientes en código nuevo. El procedimiento manual de abajo es el fallback.)*
   a. `git add -A` — fija la implementación en el index (la restauración será desde ahí).
   b. Elegir 1-3 mutaciones sobre el código NUEVO del slice (invertir una condición, alterar un
      operador/constante, eliminar una llamada). Solo código de producción — NUNCA los tests.
   c. Ejecutar la suite **con `-B`** → DEBE fallar, y el test caído debe ser el que cubre el escenario
      mutado (comprobar contra sus `@scenarios`). Si sigue verde → los tests no protegen ese punto:
      reforzar el test (volver a Fase 3.3) antes de continuar.
   d. Restaurar: `git restore <archivo-mutado>`. La mutación NUNCA se stagea ni committea.
   e. Suite en verde de nuevo. Registrar en el reporte: mutación → test que la cazó.
   f. Si un mutante sobrevive por ser **equivalente** (no cambia comportamiento observable),
      demostrarlo con un experimento antes de tocar el test, y decirlo.

   **Dos trampas del procedimiento, comprobadas:**
   - **Siempre `-B`.** Sin él, el `.pyc` del mutante puede sobrevivir al `git restore` (mismo tamaño
     y mismo mtime al segundo ⇒ Python lo reutiliza) y el veredicto del gate es falso. Si ya pasó:
     `find . -name __pycache__ -type d -not -path "./.venv/*" -exec rm -rf {} +`.
   - **Re-stagear tras cada arreglo real.** Si durante el gate se refuerza un test o se corrige el
     código, `git add` inmediatamente: el `git restore` de la siguiente mutación restaura el index,
     y un index desactualizado se lleva el arreglo por delante.
6. **Gate 4d (auditoría adversarial):** lanzar 2-3 verificadores independientes (sin el contexto de
   esta implementación) con el prompt: *"Intenta REFUTAR que el escenario <WHEN/THEN> se cumple en
   este código"*. ≥1 refutación sostenida = volver a Fase 3.3.
7. **Gate 4e:** si toca credenciales, RLS, esquema de la tabla, secrets de workflows o el token de
   Slack → revisión de seguridad explícita antes del handoff.
8. README tocado: actualizado o declarar "sin cambios — verificado".

Máximo 3 intentos por gate fallido; al 3º → parar y reportar al humano (regla de la casa).

## Handoff
- **Registrar el run** (§11): añadir entrada a `openspec/changes/<change-id>/runs.yaml` con fase,
  actor, resultado por gate, rondas de corrección y datos de mutación/adversarial.
- **Si hubo gates en rojo con causa raíz** (o se agotaron los 3 intentos): ejecutar `/leccion` antes
  de cerrar — el fallo debe dejar una regla, no solo un fix.
- Archivos staged, **NUNCA commit/push automático**.
- Reporte: tabla Requirement→código→test, resultado de todos los gates, findings de seguridad, y
  registro de mutaciones (mutación → test que la cazó).
- **Veredicto final obligatorio**: `LISTO PARA COMMIT` (todos los gates verdes) o
  `REQUIERE FIXES` (lista de qué falta, por gate).
- Recordar los pasos post-merge: **el merge a `main` despliega** (Cloudflare + cron) y después toca
  el archive (deltas → specs consolidadas, slice `proposed → shipped`).
