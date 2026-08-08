# Tasks — chore-nombres-como-botones

- [x] Enumerados **todos** los enlaces de la web antes de tocar el CSS, para no dejarse ninguno ni pisar los
      que sí deben parecer enlaces.
- [x] Nombres pulsables → botón; enlaces de prosa → tinta del sitio con subrayado verde.
- [x] `align-self` además de `justify-self`: sin ella el título de la tarjeta de temporada se estiraba.
- [x] Recorte con puntos suspensivos en el marcador, para que un nombre largo no descuadre las columnas.
- [x] Foco de teclado visible.
- [x] Verificado en navegador en las seis vistas, sin errores de consola.
- [x] Suite completa sin regresiones (97 tests JS, 388 Python).

Sin Gate 4c: no hay lógica nueva que mutar — el cambio es una hoja de estilos.

## Comandos

```bash
python3 tools/local_stack.py       # y mirar /2/, /2/temporadas, /2/hoy y una ficha
node --test tests/
.venv/bin/python3 -B -m pytest
```
