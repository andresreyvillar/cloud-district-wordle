# Tasks — feat-reglas-explicadas

Si un paso no verifica, **para** y reporta. Máximo **3 intentos** ante un gate que falla.

## Tarea 1 — Tests de escenario (Fase 2, TDD rojo)

`tests/slices/reglas-explicadas/test_reglas.py`, sobre el catálogo puro.

El test que **no puede faltar** es el de coherencia: cada parámetro publicado tiene que ser idéntico a la
constante que documenta. Es lo único que impide que la página mienta.

```bash
.venv/bin/python3 -B -m pytest tests/slices/reglas-explicadas -q
python3 -m tools.wslice slice coverage reglas-explicadas
```

## Tarea 2 — `tools/rules.py`

Catálogo puro. Cada regla: `id`, `eje`, `titulo`, `que_hace`, `por_que`, `estado`, `votada`,
`falta_decidir`, `parametros`.

Los parámetros se **importan** de donde viven (`seasons`, `badges`, `calendario`); no se escriben literales.

## Tarea 3 — La instantánea

`tools/seasons.py`: `instantanea()` gana la clave `reglas`.

## Tarea 4 — La vista

`v2/js/ui/reglas.js`, la ruta `/reglas` en el router y la entrada en la navegación. Todo lo que entra al DOM
pasa por `escapar()`.

```bash
node --test tests/v2/
```

## Tarea 5 — Verificación en navegador

```bash
python3 tools/serve_v2.py &
# /reglas pinta los grupos, cada regla con su estado y su motivo, y la consola sin errores
```

## Tarea 6 — Gates

```bash
python3 -m tools.wslice verify gates --slice reglas-explicadas --change-id feat-reglas-explicadas
.venv/bin/python3 -B -m pytest -q
```

**Gate 4c — mutación** (en zsh el comando de test va escrito en línea):

| Mutación | Test que debe caer |
|---|---|
| un parámetro del catálogo pasa a ser un literal distinto de su constante | el test de coherencia |
| una regla `acordada-sin-aplicar` pasa a `aplicada` | `cada-regla-dice-si-se-aplica` |
| `votada` siempre verdadero | `una regla aplicada y no votada lo declara` |
| una regla `sin-decidir` sin `falta_decidir` | `una regla sin decidir dice qué falta` |

## Tarea 7 — Cerrar

Entrada en `runs.yaml`, `git add -A` y parar.
