# Tasks — feat-album-de-figuras

- [x] Slice con 7 escenarios, incluido el que la vista tiene que saber hacer primero: instantánea sin álbum.
- [x] **Comprobado antes de diseñar el formato** que JSONB no conserva el orden de las claves, contra la
      instantánea real. El catálogo pasa de diccionario a lista ordenada, y un test lo fija.
- [x] 10 tests · cobertura 7/7 · `v2/js/data/album.js` puro; los dos bloques exportados y verificados como
      cadena de HTML, sin navegador.
- [x] **Gate 4c — 6 mutantes, 0 supervivientes:**

| Mutante | Resultado |
|---|---|
| el orden lo marcan las claves del recuento, no el catálogo | 🔴 `emoji-del-payload` |
| las categorías sin partidas también se pintan | 🔴 `tira-agrupada` |
| una categoría sin emoji recibe uno inventado | 🔴 `emoji-del-payload` |
| nunca faltan partidas para clasificar | 🔴 `album-en-la-ficha` |
| cuenta como clasificados a todos | 🔴 `sin-nadie-clasificado-se-dice` |
| una instantánea sin álbum pinta el bloque igual | 🔴 `instantanea-sin-album-no-rompe` |

- [x] **Tres aserciones débiles corregidas antes de la mutación**: `/12/`, `/5/` y `/2/` casaban con
      cualquier cifra de la página —12 era además el recuento de loros de Raquel—. Atadas a la frase que las
      explica y el fixture cambiado a cifras que no aparecen en ningún otro sitio.
- [x] Verificado en navegador con datos reales, escritorio y móvil: temporada 0 con 18 puestos, la ficha del
      líder, agosto con el aviso y sin errores de consola.
- [x] Corregida en el navegador la cabecera del bloque: las columnas decían «Figuras / De» sobre el
      porcentaje y el recuento, que era justo al revés. Ahora «Tasa / Figuras».
- [x] Corregido que «83 %» partiera en dos líneas en móvil. **En CSS, no con un espacio duro en el fuente**:
      un carácter invisible en el código es una trampa para quien lo lea después.
- [x] Arreglada una llamada rota en `tools/local_stack.py`, ajena a este slice pero que bloqueaba la
      verificación local.

## Comandos

```bash
node --test tests/slices/album-de-figuras/
node --test tests/
.venv/bin/python3 -B -m pytest
python3 -m tools.wslice slice validate album-de-figuras
python3 -m tools.wslice slice coverage album-de-figuras
python3 -m tools.wslice verify gates --slice album-de-figuras --change-id feat-album-de-figuras
python3 tools/local_stack.py           # materializa y sirve en :8788
```
