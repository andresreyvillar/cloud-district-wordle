# Proposal — chore-probes-de-checks

> **Slice:** N/A — es harness. No añade comportamiento del producto: hace que una declaración que ya existía
> deje de ser decorativa.

## Why

El protocolo (§4) permite que un Requirement se verifique con `checks:`, un bloque YAML con probes
mecánicos. El harness los parseaba y **devolvía `indeterminate` para todos**, así que declarar una
invariante mecánica no comprobaba nada: todo el peso lo llevaba `verified-by`.

Cuatro lecciones pendientes apuntaban a este hueco. Al leer sus destinos, **tres necesitan la base de datos
o un formato de cifras que no existe**, así que la promesa de «un probe cancela cuatro lecciones» era mía y
era falsa. Lo que sí se puede cerrar es distinto y resulta más útil: **los probes que se deciden leyendo el
repositorio son justo los que habrían cazado los dos fallos silenciosos de esta semana.**

| Probe | El fallo real que habría cazado |
|---|---|
| `env-var` | `post_ranking.yml` no pasaba `SUPABASE_URL` al paso que publica, así que **el mensaje diario nunca llevó medallas**. Encontrado a mano dos días después |
| `dom-selector` | la captura esperaba `.summary-cards`, que **no existe en la v2**: apuntar la URL habría dejado el resumen sin publicar |
| `index` | un doble más permisivo que la tabla. Costó una migración parada a mitad, con 18 de 1233 filas escritas |

## What Changes

```
tools/wslice/probes.py        siete probes: regex · workflow · cron · env-var · config-key · dom-selector · index
tools/wslice/gates.py         gate nuevo `checks-probe`: ejecuta los checks de los deltas del pack
tools/wslice/verify.py        un check en rojo manda sobre un verified-by en verde
tests/harness/test_probes.py  20 tests, cada probe contra un repositorio de mentira
```

**Un probe en rojo tumba el Requirement aunque su `verified-by` esté verde.** Es la decisión menos obvia:
si una invariante declarada se puede decidir y sale falsa, un test verde no la arregla — solo significa que
el test no la cubría.

**Lo que no se puede decidir lo dice.** `column`, `table`, `constraint` y `rls-policy` siguen
`indeterminate`, **con el motivo escrito**: sin credenciales no se pueden comprobar, y un probe que dijera
`pass` sin mirar sería peor que no tenerlo.

## Tres hallazgos del propio gate, la primera vez que se ejecutó

1. **Un `config-key` sin `file:`** en `feat-captura-del-patron`: no verificaba nada. Además el tipo era el
   equivocado —es una constante de Python, no una clave de configuración—, así que pasa a `regex`.
2. **Un `regex` sin `file:` ni `pattern:`**, con solo un `describe:`. Completado.
3. **Un `checks: index` declarado en un slice cuyos tests no escriben en ninguna tabla.** La invariante es
   cierta, pero ese slice no es quien la demuestra: su `tests_root` no tiene doble que imponer. Reemplazado
   por lo que ese slice sí puede demostrar —que el upsert usa esa pareja como clave de conflicto— con la
   prosa apuntando a los dos slices donde el doble vive de verdad.

Ninguno de los tres se habría visto leyendo. Los tres los señaló el gate en su primera ejecución.

## Lecciones que cierra, y las que no

- **CERRADA** — «el gate de `test-commands` se satisface con una expresión regular»: ahora hay un gate que
  **ejecuta** los checks en lugar de buscar cadenas. El de `test-commands` sigue siendo un regex y se declara
  como tal; lo que cambia es que ya no es el único gate mecánico del pack.
- **CERRADA** — «el doble en memoria era más permisivo que la tabla»: el probe `index` compara el índice
  declarado con lo que imponen los dobles del `tests_root`, que es literalmente el destino que la lección
  pedía.
- **SIGUEN PENDIENTES, con el motivo afinado** — las dos de cifras heredadas (`row-count` y las cifras de
  calibración de un brief): necesitan credenciales de la base y un formato para declarar una cifra esperada.
  El mecanismo para colgarlas ya existe: un probe nuevo en `PROBES` y un tipo en §4.

## Impact

- Los cinco packs con `checks:` pasan el gate: 4 probes en verde, 7 indeterminados declarados, 0 en rojo
  después de arreglar los tres hallazgos.
- Nada del producto cambia. Ni un fichero de `tools/` fuera del harness, ni la web.
