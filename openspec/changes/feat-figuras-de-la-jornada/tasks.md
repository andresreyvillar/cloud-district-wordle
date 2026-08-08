# Tasks — feat-figuras-de-la-jornada

- [x] Slice con 6 escenarios · 12 tests (6 Python + 6 JS) · cobertura 6/6.
- [x] **La web no clasifica**: la categoría llega calculada de Python. Un test lo fija usando un catálogo
      con emojis distintos de los reales, para que un mapa escrito a mano no pueda pasar.
- [x] Las figuras de la jornada salen de **todos los resultados de la temporada**, no del álbum: una jornada
      abierta todavía no cuenta y sus dibujos existen igual.
- [x] **Gate 4c — 6 mutantes, 0 supervivientes:**

| Mutante | Resultado |
|---|---|
| solo las jornadas que ya cuentan | 🔴 `la-jornada-abierta-tambien-tiene-figuras` |
| la jornada más antigua en vez de la más reciente | 🔴 `la-figura-de-cada-participante` |
| se incluye a quien no tiene cuadrícula | 🔴 `sin-cuadricula-no-hay-figura` |
| se pintan las figuras de otra jornada | 🔴 `instantanea-sin-figuras-no-rompe` |
| el emoji sale de un mapa escrito en la web | 🔴 `la-web-no-clasifica` |
| el desfase no se declara | 🔴 `el-desfase-se-declara` |

- [x] Corregido un comentario `//` en el CSS antes de que llegara a ninguna parte: no es sintaxis válida y
      habría roto la regla entera de la tarjeta.
- [x] Verificado en navegador contra datos reales, sin errores de consola.

## Comandos

```bash
.venv/bin/python3 -B -m pytest tests/slices/figuras-de-la-jornada/
node --test tests/slices/figuras-de-la-jornada/
python3 -m tools.wslice verify gates --slice figuras-de-la-jornada --change-id feat-figuras-de-la-jornada
python3 tools/local_stack.py
```
