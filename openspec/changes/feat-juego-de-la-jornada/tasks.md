# Tareas — feat-juego-de-la-jornada

## 1. `v2/js/domain/superbros.js` — el generador

Función pura. Entra la lista de resultados, sale la estructura del nivel. **Sin reloj, sin azar, sin red.**

- `jornadaDelNivel(resultados)` — la última jornada **cerrada**, es decir la anterior a la más alta.
- `nivelDe(resultados, jornada)` — el nivel, o `null` si esa jornada no tiene a nadie con patrón.
- Constantes con nombre: `COLUMNAS_POR_JUGADOR = 8`, `COLUMNAS_DE_META = 5`, `PRIMERA_COLUMNA_DE_REJILLA = 3`.
- Orden de los tramos: por `wordle_id` y luego por nombre, para que sea estable.
- El coleccionable va **una fila por encima de la plataforma más alta** del tramo, la más a la izquierda si
  empatan. Determinista y siempre apoyado.

Verificación: `node --test tests/slices/juego-de-la-jornada/`

## 2. `v2/js/ui/juego.js` — la vista

Pinta la cabecera de la pestaña con **la atribución a Joel visible**, el contenedor del juego y, mientras no
exista el juego, un aviso de que llega por PR. Si no hay nivel, lo dice.

La vista **no carga Phaser ni ningún motor**: eso llega con el PR de Joel. Lo que hace es dejar el nivel
disponible en el contenedor para que su código lo monte.

## 3. Cablear la pestaña

- `v2/js/router.js`: `VISTAS.JUEGO` y la ruta `/juego`.
- `v2/js/ui/shell.js`: entrada en `SECCIONES` con etiqueta `Juego`.
- `v2/js/app.js`: despachar la vista.

## 4. `docs/juego-contrato.md` — lo que Joel necesita

El contrato: la forma exacta del objeto del nivel, qué función le entrega el nivel, dónde monta su código y
qué NO puede hacer (pedir datos por su cuenta, ejecutar código subido, escribir en Supabase). Con el esquema
verificado contra sus dos prototipos.

## Cierre

```bash
python3 -m tools.wslice slice validate juego-de-la-jornada
python3 -m tools.wslice slice coverage juego-de-la-jornada
python3 -m tools.wslice verify gates --slice juego-de-la-jornada --change-id feat-juego-de-la-jornada
node --test tests/slices/juego-de-la-jornada/
.venv/bin/python3 -B -m pytest -q
```

Gate 4c: romper el orden de las filas (pintar de arriba abajo) o quitar el suelo de la última columna tiene
que poner en rojo su escenario y ninguno más.
