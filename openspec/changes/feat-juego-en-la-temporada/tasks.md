# Tareas — feat-juego-en-la-temporada

Rama: `feat/feat-juego-en-la-temporada`. Tests de escenario ya escritos y pendientes (TDD rojo).

## 1. `tools/juego.py` — la clasificación, pura

- `ESCALA = (10, 8, 6, 5, 4, 3, 2)`, `PUNTOS_DESDE_EL_OCTAVO = 1`.
- `puntos_de_nivel(marcas_del_nivel) -> dict[jugador, (puesto, puntos)]`: orden por `segundos` redondeado a
  centésimas; empate comparte puesto (1, 1, 3) y puntos del puesto.
- `clasificacion_del_juego(resultados, niveles, marcas, temporada) -> dict`: solo niveles cuya jornada está en
  `seasons.dias_de_temporada(resultados, temporada)` y cuya fecha es del mes (`temporada_de(fecha)`); suma
  puntos, cuenta niveles y victorias; puesto compartido a igualdad de puntos; orden de lista: puntos desc,
  victorias desc, nombre. Nombre: fila más reciente del jugador en `resultados`, o su identificador.
- Devuelve `{ "escala": [...], "niveles": n, "clasificacion": [...] }`.

```bash
.venv/bin/python3 -B -m pytest tests/slices/clasificacion-del-juego
```

## 2. Instantánea y materialización

- `seasons.instantanea(resultados, temporada, version, niveles=(), marcas=())` añade `"juego"`.
- `materialize_seasons.py`: `leer_niveles` y `leer_marcas` (paginadas, clave de servicio) y pasarlas.
- Comprobar en seco: `python3 tools/materialize_seasons.py --dry-run` (no escribe) enseña la clave `juego`.

## 3. Web — `v2/js/ui/temporada.js` y `v2/css/styles.css`

- `bloqueDelJuego(carga)`: vacío sin `carga.juego?.clasificacion?.length`. Cabecera
  `SUPERWORDLEBROS`, línea de la escala y los niveles, filas con puesto (solo cuando cambia), nombre escapado,
  puntos, niveles y victorias.
- En `pintarTemporada`, entre `bloqueDeAlbum(carga)` y `estadisticas(carga)`.

```bash
node --test tests/slices/marcador-del-juego/
```

## 4. Cierre del nivel

- Migración `supabase/migrations/<AAAAMMDDHHMMSS>_close_previous_levels.sql`: `create or replace` de
  `registrar_tiempo` con la comprobación `p_jornada = (select max(jornada) from public.game_levels)`, error
  `ese nivel ya está cerrado`, mismos `revoke`/`grant`.
- `v2/js/ui/juego.js::controlDelRanking`: si el error contiene `nivel ya está cerrado`, estado `cerrado` con
  el texto de recargar.
- En producción, solo dentro de un bloque que se deshace (como en `ranking-del-juego`).

```bash
.venv/bin/python3 -B -m pytest tests/slices/ranking-del-juego
node --test tests/slices/ranking-del-juego/
```

## Cierre

Los comandos de *Validation Gates* de `proposal.md`, la suite completa y la prueba de navegador de la
temporada (entrando por la pestaña Temporada, no por URL).
