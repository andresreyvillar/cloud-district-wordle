---
adr: 0009
titulo: Specs vivas en lugar de deltas y archive
estado: aceptado
fecha: 2026-10-29
decide: Andrés Rey
afecta: [todas]
sustituye: la parte de change packs de ADR 0001 (§5 y fase 5 de la constitución)
---

## Contexto

El método de [ADR 0001](0001-desarrollo-por-slices.md) tomó de `pga-cms` la convención de OpenSpec: los cambios
de spec se escriben como **deltas** (`ADDED / MODIFIED / REMOVED Requirements`) dentro de un change pack, y tras
el merge un paso de **archive** los consolida en `openspec/specs/<capability>/spec.md`.

Dos meses y medio después, el 2026-10-29:

| | |
|---|---|
| Change packs | 91, **ninguno archivado** |
| Specs consolidadas | **0**: las siete carpetas solo tenían `.gitkeep` |
| Requirements | 187 distintos, repartidos en 137 ficheros de delta |
| Slices | 34, **todos `proposed`** aunque todos estaban en producción |

No había ningún sitio donde leer qué hace un dominio: había que reconstruirlo aplicando 24 deltas en orden. La
CLI oficial de OpenSpec (1.2.0, instalada pero nunca usada) rechazaba además los 91 packs: el formato había
divergido. Del método, lo que funcionaba eran los slices, los tests, los gates y las mutaciones; lo que no se
hacía era justo la consolidación diferida.

## Opciones

**A. Seguir con el protocolo y hacer los 91 archives.** Recupera el método escrito. *Contra:* el coste de cada
cambio sigue igual, y es el que llevó a no archivar nunca.

**B. Specs vivas.** Se consolida una vez y, desde entonces, cada rama edita la spec directamente; el diff del PR
es el delta. *Pro:* una sola fuente de verdad, siempre al día; menos ceremonia. *Contra:* se pierde el delta
como artefacto separado —lo sustituye `git diff`— y la disciplina de «spec antes que código» depende del diff de
la rama, no de una carpeta aparte.

**C. Mixta.** Como B, con `proposal.md` obligatorio solo en cambios grandes.

## Decisión

**Opción B** (decisión del dueño). Concretamente:

- **Consolidación única.** Los deltas de los 91 packs se aplicaron en el orden en que entraron en git (ADDED
  añade, MODIFIED sustituye por título): 186 Requirements en 7 specs. Un MODIFIED que había cambiado el título
  de un Requirement («a partir de las 04:00» → «02:00») se trató como renombre para no dejar los dos. Los packs
  pasaron a `openspec/changes/archive/<fecha>-<id>/`, y los 34 slices a `shipped`.
- **La spec se edita en la rama** del cambio, junto al slice, el código y los tests. Un comentario
  `<!-- origen: <change-id> -->` en cada Requirement dice de qué cambio sale.
- **Lo que queda de cada cambio** es `openspec/changes/<id>/runs.yaml` (la observabilidad, §11), con
  `proposal.md` y `tasks.md` opcionales.
- **Harness:** desaparece `federated-untouched`; `specs-coverage` y `checks-probe` miran la spec viva;
  `test-commands` solo actúa si hay `tasks.md`; `--change-id` es opcional.

## Consecuencias

**Al consolidar salió deuda escondida en los deltas.** 48 Requirements no tenían ni `checks:` ni
`verified-by:` y nadie lo había visto, porque el harness nunca verificaba la spec entera. Se enlazaron con sus
tests a partir de los commits que los introdujeron. También salió un fallo del parser: un comentario `#` dentro de
un bloque de código cortaba el Requirement y ocultaba sus `checks:`. Tras corregirlo, los 34 slices pasan
`verify` y los gates.

**Se vuelve fácil:** leer qué hace un dominio; revisar la spec junto al código; los cambios pequeños.

**Se vuelve difícil:** separar en el tiempo «decidir la spec» de «implementarla». Se compensa con el orden de
fases (el slice y la spec se escriben y se revisan antes de quitar el rojo a los tests) y con la regla de que
una corrección de spec durante la implementación queda a la vista en el diff.
