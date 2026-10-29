# Tasks — feat-medallas-de-figuras

- [x] **Remedidos los umbrales antes de implementar**, sobre 122 pares jugador-mes con el clasificador
      calibrado. Dos de los cuatro estaban completamente descolocados (Florista 63%, Abstract@ 0,8%).
- [x] Comprobado que excluir agosto —el mes casi sin patrones— mueve cada cifra menos de dos puntos, así
      que no se excluye.
- [x] Slice con 8 escenarios · 15 tests (11 Python + 4 JS) · cobertura 8/8.
- [x] El recuento sale del **álbum**, no de un segundo recuento propio.
- [x] Arreglados dos fallos del resumen diario que este slice necesitaba: la temporada salía del prefijo de
      la fecha (tercera aparición de la misma causa raíz) y no se leía la columna `pattern`.
- [x] Sprite: `fontanero` → `abstracto` y símbolo nuevo `coleccionista`.
- [x] **Gate 4c — 6 mutantes, 0 supervivientes:**

| Mutante | Resultado |
|---|---|
| el umbral del loro baja de 5 a 3 | 🔴 `el-umbral-sale-de-lo-que-alguien-ha-logrado` |
| el umbral pasa a ser estricto (off-by-one) | 🔴 `cinco-medallas-de-figura` |
| Coleccionista se conforma con una categoría | 🔴 `cinco-medallas-de-figura` |
| el recuento de figuras llega vacío | 🔴 `el-recuento-es-el-del-album` |
| la temporada del resumen vuelve al prefijo de la fecha | 🔴 `la-temporada-del-resumen-sale-del-modelo` |
| el resumen deja de pedir el patrón | 🔴 `la-temporada-del-resumen-sale-del-modelo` |

- [x] **Un test pasó en verde con el sprite roto** y lo cazó el navegador: el símbolo nuevo se había
      insertado dentro del comentario de la cabecera. El test ahora quita los comentarios antes de mirar,
      cuadra los `<symbol>` abiertos y cerrados, y comprueba dónde termina el fichero.
- [x] Verificado en navegador: las doce tarjetas con icono, ninguna en blanco, sin errores de consola.

## Comandos

```bash
.venv/bin/python3 -B -m pytest tests/slices/medallas-de-figuras/
node --test tests/slices/medallas-de-figuras/
.venv/bin/python3 -B -m pytest
python3 -m tools.wslice verify gates --slice medallas-de-figuras --change-id feat-medallas-de-figuras
python3 tools/local_stack.py
```
