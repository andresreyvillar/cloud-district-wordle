# La victoria del mes sale la noche del último día

> Slices: `podio-de-cierre-de-mes` · `resumen-diario-compuesto` · `clasificacion-del-juego` (modificaciones).

## Why

El 30 de septiembre fue el último día del mes y el resumen de esa noche se publicó como si quedara mes por
delante (corría el código anterior al momento del mes). Y aun con el código nuevo, la victoria no se anunciaba
hasta el día 1 a las 11:00, con el cron del podio de cierre.

El dueño pide que **la noche del último día salga el mensaje de la victoria en lugar del resumen diario**.
Decisiones:
- **Podio + lo del día**: la victoria lleva debajo, en corto, la última jornada (palabra, mejor del día, obra).
- **Los tres campeones desde octubre**: marcador, SuperWordleBros y figuras.
- **El nivel del último día laborable puntúa en el mes siguiente**, que es cuando se juega: así el juego cierra
  con el mes y su campeón se puede coronar esa noche.

## What Changes

- `tools/calendario.py`: `ultimo_laborable_del_mes` / `es_ultimo_laborable_del_mes`, una sola definición.
- `tools/juego.py`: `mes_en_que_puntua` y la validez del nivel en el mes de su jornada.
- `tools/resumen.py`: `bloque_ultima_jornada`; los niveles por jugar no cuentan el del último día.
- `tools/podio.py`: los campeones del juego y de figuras desde `2026-10`; la última jornada antes de la
  despedida.
- `tools/post_ranking.py`: `publicar_la_victoria` el último laborable, con el título del podio; el título y la
  comprobación de «ya celebrado» se mueven aquí desde `post_podium.py`, que los importa.
- `tools/post_podium.py`: lee el juego (solo desde octubre) y pasa a ser la red del día 1.

## Out of Scope

- El cron del podio no cambia de horario: sigue del 1 al 7 a las 11:00 como red.
- La victoria no lleva las medallas del día.
- Festivos: no se conocen; el último laborable es el del calendario.

## Impact

- **Septiembre cambia al recalcularse**: su nivel del 30 pasa a octubre (el bloque del juego de septiembre baja
  de 6 niveles a 5). En el archivo no se nota: septiembre solo enseña el marcador.
- **Ventana declarada**: la victoria se calcula esa noche; una cuadrícula del último día que llegue después no
  entra, y una marca del nivel de la víspera entre la publicación y las 02:00 tampoco.

## Validation Gates

```bash
python3 -m tools.wslice slice validate podio-de-cierre-de-mes
python3 -m tools.wslice slice validate resumen-diario-compuesto
python3 -m tools.wslice slice validate clasificacion-del-juego
python3 -m tools.wslice slice coverage podio-de-cierre-de-mes
python3 -m tools.wslice slice coverage resumen-diario-compuesto
python3 -m tools.wslice slice coverage clasificacion-del-juego
python3 -m tools.wslice verify gates --slice podio-de-cierre-de-mes --change-id feat-victoria-el-ultimo-dia
python3 -m tools.wslice verify gates --slice resumen-diario-compuesto --change-id feat-victoria-el-ultimo-dia
python3 -m tools.wslice verify gates --slice clasificacion-del-juego --change-id feat-victoria-el-ultimo-dia
.venv/bin/python3 -B -m pytest tests/slices/podio-de-cierre-de-mes tests/slices/clasificacion-del-juego tests/slices/resumen-diario-compuesto
```

## Capabilities

| Capability | Requirements |
|---|---|
| `publicacion` | la victoria sale la última noche en lugar del resumen · los tres campeones desde octubre |
| `ranking` | el nivel del último día laborable puntúa en el mes siguiente (MODIFIED) |
| `resultados` | la fecha del nivel decide su mes (MODIFIED) |
