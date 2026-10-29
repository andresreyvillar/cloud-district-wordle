# El SuperWordleBros entra en la temporada

> Slices: `clasificacion-del-juego` (nuevo) · `marcador-del-juego` (nuevo) · `ranking-del-juego`
> (modificación: el nivel se cierra).

## Why

El grupo ya juega cada día al SuperWordleBros y deja su mejor tiempo en el ranking de ese nivel, pero ese
ranking dura un día. El dueño quiere una **clasificación del juego en la temporada**, debajo del ranking de
figuras, construida con las marcas diarias; y que el resumen del canal la mencione (eso va en
`feat-resumen-con-podios`, que depende de este paquete).

Decisiones del dueño:
- **Puntos por puesto en cada nivel**: 10, 8, 6, 5, 4, 3, 2 y 1 del octavo en adelante; empates comparten
  puesto y puntos; se suman en el mes.
- **Un nivel se cierra al congelarse el siguiente**: `registrar_tiempo` deja de aceptar marcas de niveles
  anteriores, para que la clasificación no se reescriba hacia atrás.

## What Changes

1. **Pipeline** — `tools/juego.py` (nuevo): `puntos_de_nivel` y `clasificacion_del_juego(resultados, niveles,
   marcas, temporada)`, puras. `tools/seasons.py::instantanea` recibe niveles y marcas y añade la clave
   `juego`. `tools/materialize_seasons.py` los lee de `game_levels` y `game_times`.
2. **Web** — `v2/js/ui/temporada.js`: `bloqueDelJuego(carga)` entre `bloqueDeAlbum` y `estadisticas`, con su
   CSS.
3. **Base de datos** — migración nueva que reemplaza `registrar_tiempo` para rechazar niveles que no sean el
   último congelado.
4. **Pestaña del juego** — `controlDelRanking` distingue el rechazo por nivel cerrado y lo dice.

## Out of Scope

- **El resumen diario**: el podio del juego, el orden de los podios y el momento del mes van en
  `feat-resumen-con-podios`.
- La ficha de jugador no enseña todavía su historial del juego.
- No se cambia cómo se juega ni el ranking diario por nivel, salvo el cierre.
- No se toca la clasificación general ni la de figuras.

## Impact

| Pieza | Efecto |
|---|---|
| `season_snapshots.payload` | clave nueva `juego`; aditivo, las vistas viejas la ignoran |
| `registrar_tiempo` | rechaza niveles anteriores al último congelado |
| Web | bloque nuevo en la temporada |
| Despliegue | la web al mergear; la clave `juego` **en la siguiente materialización**, no con el push |

## Validation Gates

```bash
python3 -m tools.wslice slice validate clasificacion-del-juego
python3 -m tools.wslice slice validate marcador-del-juego
python3 -m tools.wslice slice validate ranking-del-juego
python3 -m tools.wslice slice coverage clasificacion-del-juego
python3 -m tools.wslice slice coverage marcador-del-juego
python3 -m tools.wslice slice coverage ranking-del-juego
python3 -m tools.wslice verify gates --slice clasificacion-del-juego --change-id feat-juego-en-la-temporada
python3 -m tools.wslice verify gates --slice marcador-del-juego --change-id feat-juego-en-la-temporada
python3 -m tools.wslice verify gates --slice ranking-del-juego --change-id feat-juego-en-la-temporada
```

Toca el esquema (función con `security definer`) y un workflow lee con la clave de servicio: **la Fase 4
incluye revisión de seguridad** (Gate 4e).

## Capabilities

| Capability | Requirements |
|---|---|
| `ranking` | clasificación del juego por puntos por puesto · bloque de la temporada |
| `resultados` | el nivel se cierra al congelarse el siguiente · la materialización lee niveles y marcas |
| `dashboard` | la pestaña dice cuándo el nivel está cerrado · el bloque se pinta sin recalcular |
