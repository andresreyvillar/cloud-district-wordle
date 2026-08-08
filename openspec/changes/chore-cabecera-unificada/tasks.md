# Tasks — chore-cabecera-unificada

- [x] Cabecera reescrita con los tokens de la liga; Poppins activada en todo el sitio.
- [x] Navegación de píldoras, pegada arriba, con estado activo en verde y foco de teclado visible.
- [x] Ancho útil 60rem → 84rem, con margen lateral compartido por cabecera y contenido.
- [x] Responsive por debajo de 780px, sin desplegable.
- [x] Marca duplicada eliminada del cuerpo; la tira de cifras se reparte a lo ancho.
- [x] **Hover ilegible corregido** (lo reportó el dueño): tinta fija en vez de una variable que se invierte
      con el tema. Contraste medido 11,09:1 en claro y en oscuro.
- [x] Tres desbordamientos corregidos: el lateral de `main`, `.columnas` y `.distribucion .barra`.
- [x] Verificado: 7 vistas × 5 combinaciones de ancho y tema, sin desbordes ni errores.
- [x] Suite completa sin regresiones (97 JS, 388 Python).

Sin Gate 4c: no hay lógica nueva que mutar.

## Comandos

```bash
python3 tools/local_stack.py     # y mirar /2/ a 390, 768 y 1440 px, en claro y oscuro
node --test tests/
.venv/bin/python3 -B -m pytest
```
