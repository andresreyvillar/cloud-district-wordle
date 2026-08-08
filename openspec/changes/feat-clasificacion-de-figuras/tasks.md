# Tasks — feat-clasificacion-de-figuras

- [x] Medido el criterio de puntuación (4 candidatos) y el mínimo de partidas (3/5/8/10) sobre datos reales,
      antes de escribir el slice.
- [x] Slice con 8 escenarios y la tabla de qué publica cada temporada, con las cifras reales.
- [x] 16 tests · cobertura 8/8 · `tools/album.py` puro (sin reloj ni red).
- [x] Conectado: `seasons.instantanea` gana la clave `album` y `materialize_seasons` lee `pattern`.
- [x] **Un test verifica los fixtures contra el clasificador** antes de usarlos: un fixture que creyera
      dibujar un loro y dibujara un abstracto haría pasar tests que no prueban nada.
- [x] **Gate 4c — 5 mutantes, 0 supervivientes:**

| Mutante | Resultado |
|---|---|
| el mínimo baja de 5 a 3 | 🔴 `minimo-de-partidas-para-clasificar` |
| la tasa pasa a ser el recuento absoluto | 🔴 `tasa-de-figuras-por-partida` |
| una partida sin patrón cuenta como abstracto | 🔴 `sin-patron-no-cuenta` |
| el desempate pone delante a quien aporta menos figuras | 🔴 `orden-determinista-del-album` |
| el álbum se calcula sobre todos los resultados, no los de la temporada | 🔴 `el-album-hereda-los-dias-de-la-temporada` |

- [x] El fixture del mínimo pasa a cantidades **literales** (4 y 5), y la razón está **comprobada, no
      supuesta**: con el fixture derivado de la constante (`[FLOR] * (MINIMO - 1)`) el mutante 5→3 **pasa en
      verde** — se comprobó rehaciendo el test en su forma original y ejecutándolo. El fixture se ajustaba
      solo al umbral y dejaba de medir cuál es.
- [x] Ensayo contra los datos reales (`--dry-run`, sin escribir): temporada 0 con 1502 clasificadas y 21
      jugadores, agosto con 19 de 80 y nadie con puesto. Payload de 141 KB.
- [x] Corregido el brief: las rarezas citadas eran del clasificador desmentido, y la pregunta abierta
      «recuento o ponderado» queda cerrada con la medida que la decide.

## Comandos

```bash
.venv/bin/python3 -B -m pytest tests/slices/clasificacion-de-figuras/
.venv/bin/python3 -B -m pytest
python3 -m tools.wslice slice validate clasificacion-de-figuras
python3 -m tools.wslice slice coverage clasificacion-de-figuras
python3 -m tools.wslice verify gates --slice clasificacion-de-figuras --change-id feat-clasificacion-de-figuras
python3 tools/materialize_seasons.py --todas --dry-run
```
