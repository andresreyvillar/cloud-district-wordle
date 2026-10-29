# La cuadrícula de ayer se convierte en un nivel jugable

> Slice: `juego-de-la-jornada`.

## Por qué

Joel ha construido un plataformas donde las cuadrículas del grupo son el escenario: cada jugador ocupa un
tramo, sus verdes y amarillos son las plataformas y debajo va su nombre con la nota. Está en un HTML suelto
que alguien tiene que regenerar y repartir a mano cada día.

El dueño quiere que viva en la web, con una pestaña propia, **y que el juego lo siga desarrollando Joel por
PR**. Así que lo que hace falta no es el juego: es lo que el juego necesita para existir dentro de la web.

## Qué cambia

1. **El generador del nivel** (`v2/js/domain/superbros.js`), función pura de los resultados a la estructura
   que el juego consume.
2. **La pestaña** `/juego`, con la atribución a Joel visible.
3. **El contrato** entre las dos piezas, documentado, para que el PR de Joel encaje sin negociación.

### Las reglas del nivel, deducidas y verificadas

Se sacaron de los dos prototipos de Joel (22 y 23 de septiembre) y **se comprobaron contra la tabla**:
reconstruyendo el patrón desde sus bloques sale exactamente el `pattern` guardado, en los seis jugadores
comprobados.

| Regla | Valor |
|---|---|
| Ancho | `N * 8 + 5` columnas |
| Alto | `max(nota) + 3` |
| Tramo | 8 columnas por jugador; la cuadrícula en las 5 centrales |
| Filas | de abajo arriba: fila 1 = último intento |
| Bloques | acierto → `green`, letra desplazada → `orange`, ausente → hueco |
| Etiqueta | `nombre  nota/6` en la fila `nota + 2` |
| Meta | columna `ancho - 3`, fila 1 |

**Dos cosas se cambian a propósito respecto al prototipo.** La fuente pasa a ser la tabla y no el canal: el
prototipo usa nombres de display (`carlos.h` frente a `Carlos H.`) y se deja jugadores fuera —dos de doce el
22 de septiembre—. Y el coleccionable deja de colocarse al azar: en 23 tramos no encaja ninguna regla
deducible, y este proyecto exige que la misma jornada dé siempre el mismo nivel.

## Fuera de alcance

- **El juego.** Lo desarrolla Joel. Aquí se define qué recibe y dónde se monta.
- **El ranking por tiempo.** Slice siguiente: necesita identidad y una tabla con escritura anónima, que es
  una decisión con coste propio y ya está tomada por el dueño —marcador compartido y confiado— pero no entra
  en este paquete.
- **Subir código en caliente.** Un campo donde se pegue JavaScript y se ejecute comparte origen con la página
  que habla con Supabase. El código entra por rama.
- **Tocar la instantánea o el esquema.** Este slice no escribe nada.

## Impact

| Qué | Detalle |
|---|---|
| Slices | `juego-de-la-jornada` (nuevo, 11 escenarios) |
| Capabilities | `dashboard` (4 ADDED) |
| Archivos nuevos | `v2/js/domain/superbros.js`, `v2/js/ui/juego.js`, `tests/slices/juego-de-la-jornada/nivel.test.js`, `docs/juego-contrato.md` |
| Archivos tocados | `v2/js/router.js`, `v2/js/ui/shell.js`, `v2/js/app.js` |
| Esquema | Ninguno |
| Compatibilidad | Pestaña nueva; ninguna vista existente cambia |
| Riesgo | Bajo. Solo lectura, sin red nueva, sin dependencias nuevas hasta que llegue el PR de Joel |

## Validation Gates

```bash
python3 -m tools.wslice slice validate juego-de-la-jornada
python3 -m tools.wslice slice coverage juego-de-la-jornada
python3 -m tools.wslice verify gates --slice juego-de-la-jornada --change-id feat-juego-de-la-jornada
node --test tests/slices/juego-de-la-jornada/
node --check v2/js/domain/superbros.js
.venv/bin/python3 -B -m pytest -q
```

## Capabilities

| Capability | Requirements | Qué aporta |
|---|---|---|
| `dashboard` | 4 ADDED | El nivel derivado, el escenario, los nombres canónicos y lo que pasa cuando falta algo |
