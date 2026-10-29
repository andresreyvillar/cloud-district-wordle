# Tareas — feat-resumen-con-podios

Rama: `feat/feat-resumen-con-podios`, **después** de mergear `feat-juego-en-la-temporada` (usa
`tools/juego.py`). Tests de escenario escritos y pendientes: `test_podios.py` y `test_momento_del_mes.py`, con
el mes sintético de `fixtures_mes.py`.

## 1. `tools/podios.py` — el podio en texto

`podio_de_texto(titulo, puestos)`: `puestos` son `{posicion, nombre, cifra}` de los puestos 1 a 3 (ya
cortados por puesto). Tres columnas de 10 con escalones de `█` de 8 —el 1º en el centro con 4 filas, el 2º a
la izquierda con 2, el 3º a la derecha con 1—; encima de cada escalón el puesto, los nombres (hasta tres, y
«y N más») y la cifra. Nombres de más de 10 caracteres se acortan. Ninguna línea pasa de 32. Devuelve
`titulo + "\n```\n" + podio + "\n```"`.

```bash
.venv/bin/python3 -B -m pytest tests/slices/resumen-diario-compuesto/test_podios.py
```

## 2. `tools/resumen.py`

- `bloque_top` → podio del marcador (título `📊 *Marcador · <etiqueta>*`), cortado por puesto ≤ 3.
- `bloque_juego(resultados, temporada, jornada, niveles, marcas)`: el nivel del día es el último de `niveles`
  con jornada anterior a `jornada`; línea `🎮 *SuperWordleBros* — el nivel #N lo gana <nombre> en <m:ss.cc>
  (<n> jugadores)`; debajo, el podio de `juego.clasificacion_del_juego(...)` con `<puntos> pts`.
- `bloque_album` → podio de figuras con `<media> pts`.
- `bloque_momento_del_mes(resultados, temporada, jornada, niveles=(), marcas=())`: fecha de la jornada desde
  `resultados`; laborables que quedan en el mes con el calendario. Arranque si la jornada es de las tres
  primeras de `dias_de_temporada`; recta final si quedan ≤ 4 laborables después; última jornada si quedan 0.
  Puntos en juego = 10 × (nivel abierto si es del mes + laborables desde la jornada incluida).
- `resumen_del_dia(..., niveles=None, marcas=None)`: el momento del mes justo antes de los podios; los
  podios en orden marcador → juego → figuras, cada uno con su pulla pegada como hasta ahora.
- Reescribir `test_el_top_cinco_*` y `test_la_cabeza_del_album_*` (y sus `@scenarios`, que ya no existen)
  como tests de podio.

```bash
.venv/bin/python3 -B -m pytest tests/slices/resumen-diario-compuesto
```

## 3. `tools/refranero.py` y `tools/post_ranking.py`

- Frases de arranque, recta final y última jornada: varias por forma, elegidas por jornada (§10), con el tono
  jocoso del resto del resumen.
- `post_ranking.py`: leer `game_levels` y `game_times` (paginando) y pasarlos a `resumen_del_dia`.

## Cierre

Gates de `proposal.md`, suite completa, mutación, y **el mensaje real impreso** con los datos de hoy
(`python3 tools/post_ranking.py` en modo sin publicar) leído de principio a fin, también en el móvil.
