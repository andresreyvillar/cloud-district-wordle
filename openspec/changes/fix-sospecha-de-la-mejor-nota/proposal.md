# La sospecha va a la mejor nota del día, no a cualquiera que baje de tres

> Slice: `comentarios-de-la-jornada` (modificación: cambia la condición de un hecho ya especificado).

## Por qué

El mensaje de la jornada 1709 salía así:

```
• Dani Sanchez ha resuelto en 1. Sin comentarios 🍀
• Me niego a aceptar el 2 de Paula Granado y Raquel. Y lo digo pataleando 🤨
```

Se queja del 2 **teniendo un 1 delante**. La pulla salta con `score <= 2` sin mirar lo que hizo el resto, así
que ese día puso en duda a las segundas y dejó pasar al primero.

El dueño lo señaló con la regla ya razonada: *«no puede ser que se queje del 2 cuando hay notas mejores;
cuando hay más de un 2 se entiende que la palabra es fácil; en este caso la reacción de incredulidad es para
el que ha sacado 1»*.

## Lo medido, sobre 194 jornadas con tres o más jugadores

| | jornadas | % |
|---|---:|---:|
| Regla actual (`score <= 2`) | 63 | 32% |
| …de ellas, señalando a alguien que **no** tiene la mejor nota | **1** | 1% |
| Regla nueva (mejor nota del día, y sin compartir) | 47 | 24% |
| Mejor nota ≤2 pero **compartida** | 16 | 8% |

La queja injusta había ocurrido **una sola vez en toda la historia: hoy**. No es casualidad — una nota de 1
aparece en 3 jornadas de 194, así que el fallo estaba desde el principio esperando al día en que se notara.

## Qué cambia

La pulla de la sospecha exige ahora tres cosas en lugar de una: dos intentos o menos, **ser la mejor nota del
día**, y **no compartirla**. Lo demás del hecho —las frases, la prioridad, la concordancia— no se toca.

## Fuera de alcance

- **Tocar `clavada`.** Resolver en 1 sigue teniendo su propio hecho, con o sin sospecha.
- **Los otros hechos.** `sembrado` y `no-inspirado` ya se miden contra la media del día y quedan igual.
- **Penalizar a nadie.** Esto cambia lo que se comenta, no lo que se puntúa.

## Impact

| Qué | Detalle |
|---|---|
| Slices | `comentarios-de-la-jornada` (1 escenario modificado, 2 añadidos) |
| Capabilities | `publicacion` (1 MODIFIED), `estadisticas` (1 MODIFIED) |
| Archivos | `tools/comentarios.py` |
| Esquema | Ninguno |
| Compatibilidad | El chiste sale en el 24% de las jornadas en lugar del 32%: se pierden las 16 de mejor nota compartida, que es la intención |
| Riesgo | Bajo. Un hecho deja de emitirse en casos acotados y medidos |

## Validation Gates

```bash
python3 -m tools.wslice slice validate comentarios-de-la-jornada
python3 -m tools.wslice slice coverage comentarios-de-la-jornada
python3 -m tools.wslice verify gates --slice comentarios-de-la-jornada --change-id fix-sospecha-de-la-mejor-nota
.venv/bin/python3 -B -m pytest tests/slices/comentarios-de-la-jornada -q
.venv/bin/python3 -B -m pytest -q
```

## Capabilities

| Capability | Requirements | Qué aporta |
|---|---|---|
| `publicacion` | 1 MODIFIED | A quién se le lanza la pulla |
| `estadisticas` | 1 MODIFIED | Que la nota se lea contra las del mismo día |
