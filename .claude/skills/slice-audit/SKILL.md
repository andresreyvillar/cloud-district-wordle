---
name: slice-audit
description: Auditoría determinista de TODO el inventario de slices (Fase 6 del protocolo) — trigger rules, multi-spec, wikilinks, validate+verify por slice, métricas y lecciones pendientes. Usar tras un lote de slices nuevos, antes de un release, o cuando el usuario pida "audita los slices".
---

# /slice-audit — Fase 6 del protocolo

**Constitución:** `openspec/slice-system.md` §6 Fase 6 y §8 (anti-patrones).
**Herramienta:** `python3 -m tools.wslice`.

## Checks (en orden)

1. **Inventario + validate global** (FAIL si exit≠0):
   ```bash
   python3 -m tools.wslice slice list
   python3 -m tools.wslice slice validate
   ```
   Cubre mecánicamente: triggers ilegales (§3), specs[] rotos, escenarios duplicados,
   mismo-evento emit+consume, wikilinks sin `(TBD)`.

2. **Verify por slice** (FAIL si algún slice `shipped` da fail; los `proposed` pueden dar
   `indeterminate` — anotarlos):
   ```bash
   python3 -m tools.wslice verify slice <cada-slug>
   ```

3. **Heurística single-spec** (WARN): slices con `specs:[]` de una sola capability cuyo body
   mencione otras capabilities o emita eventos → candidato a slice mal acotado.

4. **Cobertura pendiente envejecida** (WARN): slices `shipped` con escenarios en `pending`
   (skip/fixme) — un shipped no puede tener TDD rojo residual.

5. **Observabilidad y lecciones (§11)**:
   ```bash
   python3 -m tools.wslice metrics
   ```
   - runs.yaml malformados (FAIL — exit≠0 del comando).
   - mutantes supervivientes > 0 en el agregado (WARN — tests débiles en algún slice).
   - lecciones con `estado: pendiente` en `docs/lecciones.md` (WARN — deuda del bucle
     error→regla; listar cada una con su destino de codificación).

6. **Deriva del harness** (WARN): la suite del propio harness en verde
   (`.venv/bin/python3 -B -m pytest tests/harness`). Un harness roto invalida los demás checks.

## Reporte

Tabla final:

| Slice | validate | verify | cobertura | Notas |
|---|---|---|---|---|

- **FAIL** (bloquea release): cualquier check 1-2 en rojo, o runs.yaml malformado.
- **WARN**: checks 3-6 — listar con recomendación.

No modificar nada durante la auditoría — es solo lectura + reporte. Las correcciones van por
`/slice-propose` (modificación) o `/slice-implement`.
