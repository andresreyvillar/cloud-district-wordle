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

      **Las mutaciones se derivan de lo que el delta PROHÍBE, no de lo que se te ocurra.** Quien
      implementa muta lo que ya tenía en la cabeza, así que la elección propia confirma en vez de
      refutar: en `feat-tono-del-hilo` las cinco mutaciones elegidas así cayeron y aun así los
      verificadores del Gate 4d sostuvieron siete refutaciones con la suite verde. Recorre los
      Requirements y, por cada frase de la forma «nunca X» / «solo Y» / «no puede Z», escribe la
      mutación que **hace ocurrir X**. Esa lista es obligatoria; las de intuición van después.

      Tres moldes de guardián vacuo, los tres vistos en verde:
      - **Guardián por subcadena literal**: comprobar que no aparece `"es un tramposo"` no impide
        `"hizo trampas"`. Fijar la raíz, la propiedad o la **forma del objeto** — nunca el ejemplo.
      - **Determinismo probado llamando dos veces en el mismo proceso**: eso es idempotencia. La
        reproducibilidad se fija comprobando **la regla** (índice cíclico por jornada), porque una
        elección con `hash()` pasa el test y cambia el texto en cada ejecución del cron.
      - **El borde que falla, probado desde el compositor**: pasar `None` a la función pura no ejerce
        ninguna caída. Si el Requirement dice «si el borde falla, se publica igual», el test tiene que
        **hacer fallar al borde**.
   c. Ejecutar la suite **con `-B`** → DEBE fallar, y el test caído debe ser el que cubre el escenario
      mutado (comprobar contra sus `@scenarios`). Si sigue verde → los tests no protegen ese punto:
      reforzar el test (volver a Fase 3.3) antes de continuar.
   d. Restaurar: `git restore <archivo-mutado>`. La mutación NUNCA se stagea ni committea.

   **Tres formas de que este gate mienta, vistas las tres en una misma sesión:**
   - **Verde falso: la mutación no se aplicó.** El mutador no existía y falló a stderr mientras la suite
     seguía verde. Comprobar que el fichero cambió antes de leer el resultado.
   - **Rojo falso: la mutación rompió la compilación.** Un error de sintaxis tumba todos los tests que
     importan el módulo y se lee como «cazada». Tras mutar, `node --check` / `python3 -m py_compile` en
     verde **antes** de ejecutar la suite; y el rojo tiene que caer en **un** escenario, no en todos.
   - **Mutación equivocada: el separador del bucle partió el código.** Un `IFS='|'` sobre código con `||`
     sustituye un trozo que no era el pensado. No pasar código por bucles con separadores; llamar al
     mutador directamente, una vez por mutación.
   - **Rojo en cascada: el mutante destruye estado compartido.** Con un fixture de módulo (una base de
     datos local, un servidor), la escritura que el mutante deja pasar borra los datos de los demás tests y
     el rojo cae en escenarios ajenos. Los intentos destructivos van **dentro de una transacción que se
     deshace** (o con estado propio por test), para que una regresión ponga en rojo solo su escenario.
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
   **La prueba de un arreglo mide también la función que arregla, no solo el síntoma.** Arreglar «la
   página hace scroll al jugar» se verificó midiendo el scroll —quieto, verde— mientras el arreglo le había
   quitado las teclas al juego: la página no se movía porque ya no se movía nada. Si la prueba del arreglo
   no puede fallar cuando la función muere, no prueba el arreglo.

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
