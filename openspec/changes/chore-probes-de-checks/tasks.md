# Tasks — chore-probes-de-checks

## 1 · Los probes

- [x] `tools/wslice/probes.py` con siete probes, cada uno con el fallo real que justifica su existencia
      escrito en el módulo.
- [x] `Veredicto(tipo, estado, detalle)`. **Ningún probe lanza**: un check mal escrito es `indeterminate`
      con su motivo, no una excepción que tumbe el `verify`.
- [x] Los cuatro tipos que necesitan base de datos devuelven `indeterminate` **diciendo por qué**.

## 2 · Los gates

- [x] Gate `checks-probe` en `verify gates --slice X --change-id Y`: ejecuta los `checks:` de los deltas.
      Va ahí y no en `verify slice` porque `verify slice` lee las **specs consolidadas**, que no existen
      hasta el archive — los checks viven en los deltas mientras el pack está abierto.
- [x] `verify slice`: un check en rojo manda sobre un `verified-by` en verde.

## 3 · Tests

- [x] 20 tests en `tests/harness/test_probes.py`, cada probe contra un repositorio de mentira en `tmp_path`.
- [x] El test que más importa: `env-var` **mira el paso, no el workflow entero**. Un `in contenido` daría
      un falso `pass` cuando la variable existe en otro paso — que es exactamente la forma del fallo real.

## 4 · Los tres hallazgos del gate

- [x] `config-key` sin `file:` → `regex` con fichero y patrón.
- [x] `regex` sin `file:` ni `pattern:` → completado.
- [x] `index` declarado donde no hay doble → reemplazado por lo que ese slice sí demuestra, con la prosa
      apuntando a los dos slices donde el doble existe.

## 5 · Verificación

- [x] Los cinco packs con `checks:`: `checks-probe` en verde, 4 probes `pass`, 7 `indeterminate`, 0 `fail`.
- [x] Suite completa en verde (73 tests de harness incluidos).
- [x] **Una trampa conocida, repetida:** el gate parecía no ejecutarse por la **caché de bytecode** de
      `tools/wslice/__pycache__`. Es la misma causa que ya tiene lección en este repo. Y la segunda:
      `set -- $par` no parte la variable en zsh, así que el bucle de comprobación medía cero en todo.
