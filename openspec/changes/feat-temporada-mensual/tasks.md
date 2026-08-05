# Tasks — feat-temporada-mensual

Plan para un implementador **sin contexto previo**. Si un paso no verifica, **para** y reporta.
Máximo **3 intentos** ante un gate que falla.

⚠️ Escribe en producción, pero en una tabla **nueva y derivada**: borrarla y recalcularla no pierde nada. El
riesgo real es que el cron materialice una instantánea mal calculada y la web la pinte como verdad.

## Tarea 0 — Preflight

```bash
python3 -m tools.wslice slice validate temporada-mensual
.venv/bin/python3 -B -m pytest -q
```

## Tarea 1 — Tests de escenario (Fase 2, TDD rojo)

Archivo: `tests/slices/temporada-mensual/test_temporada_mensual.py`

Siete escenarios sobre fixtures a mano y un doble de la tabla con la semántica del `upsert` real (la clave
decide si inserta o actualiza). El doble imita la restricción, no solo la interfaz: un doble más permisivo
que producción ya dejó pasar un fallo que reventó una migración (`docs/lecciones.md`, 2026-08-05).

Interfaz que los tests asumen:

```python
from tools.seasons import MUESTRA_MINIMA_DEL_DIA, dias_de_temporada, instantanea, temporada_de, temporadas
from tools.materialize_seasons import CLAVE, materializar
```

**Ojo con las fechas de los fixtures:** agosto de 2026 empieza en sábado. Un fixture que numere del 1 al 15
mete cinco fines de semana. Usar helpers que devuelvan el n-ésimo día laborable, como en los tests de
medallas.

```bash
.venv/bin/python3 -B -m pytest tests/slices/temporada-mensual -q     # esperado: 7 skipped
python3 -m tools.wslice slice coverage temporada-mensual             # esperado: 7/7
```

## Tarea 2 — `tools/seasons.py`

El modelo, en funciones puras:

| Función | Devuelve |
|---|---|
| `temporada_de(fecha)` | `'AAAA-MM'` |
| `dias_de_temporada(resultados, temporada)` | las jornadas que cuentan, ordenadas |
| `resultados_de_temporada(resultados, temporada)` | las filas que cuentan |
| `temporadas(resultados)` | una entrada por temporada, de más reciente a más antigua, con su estado |
| `instantanea(resultados, temporada)` | la carga útil que se materializa |

Dos reglas, y hacen falta las dos: **día laborable** (de `tools/calendario.py`, no una segunda definición) y
**muestra mínima de 5 jugadores**.

`MUESTRA_MINIMA_DEL_DIA` pasa a vivir **aquí**, porque es parte de qué es un día de temporada, y
`tools/badges.py` lo importa de aquí en lugar de tener su propia copia. Su docstring ya decía que quería ser
el mismo criterio; ahora lo es de verdad.

## Tarea 3 — La tabla

```sql
create table season_snapshots (
  temporada  text primary key,
  payload    jsonb not null,
  updated_at timestamptz not null default now()
);
alter table season_snapshots enable row level security;
create policy "lectura publica" on season_snapshots for select using (true);
```

**Comprobar la RLS activamente**, no suponerla: con la clave publicable, un `insert` tiene que fallar. Sin
eso, la clave que va en el código de la web podría reescribir la instantánea.

## Tarea 4 — `tools/materialize_seasons.py`

`materializar(resultados, objetivo, tabla, ahora, dry_run=False)`. `ahora` entra **por parámetro**: el
cálculo no lee el reloj (§10), y el borde es `main`.

CLI: sin argumentos, solo la temporada en curso; `--todas` recalcula el histórico; `--dry-run` no escribe.

## Tarea 5 — Ensayo con datos reales, sin escribir

```bash
set -a; . ./.env; set +a
.venv/bin/python3 -B tools/materialize_seasons.py --todas --dry-run
```

**Medir aquí la cifra de temporadas cerradas** en lugar de heredarla: el "9 temporadas" de los documentos
viene de antes de la regla de días laborables y de la limpieza de identidad. Si sale otra cosa, la cifra
nueva es la buena y hay que corregir los documentos que citan la vieja.

Después, la ejecución real y la verificación por SQL de que hay una fila por temporada.

## Tarea 6 — El cron

`update_stats.yml`: tras ingerir, materializar la temporada en curso.

## Tarea 7 — Gates

```bash
python3 -m tools.wslice verify slice temporada-mensual
python3 -m tools.wslice verify gates --slice temporada-mensual --change-id feat-temporada-mensual
.venv/bin/python3 -B -m pytest -q
```

**Gate 4c — mutación** (`-B`, `git add -A` antes, re-stagear tras cualquier arreglo; en zsh el comando de
test va escrito en línea, que una variable sin comillas no se parte en palabras):

| Mutación | Test que debe caer |
|---|---|
| quitar el filtro de día laborable | `solo-los-dias-laborables-forman-la-temporada` |
| `>=` por `>` en la muestra mínima | `dia-sin-muestra-no-forma-parte` |
| la temporada sale de los 4 primeros caracteres de la fecha | `temporada-es-el-mes-de-la-fecha` |
| la temporada en curso es la primera en lugar de la última | `temporada-en-curso-se-deriva-de-los-datos` |
| ignorar `dry_run` | `el ensayo no escribe` |

**Gate 4e — security review:** la RLS de la tabla nueva, comprobada con la clave publicable. Y que la carga
útil no contenga nada que no esté ya publicado en la web.

## Tarea 8 — Registrar y cerrar

1. Entrada en `runs.yaml` con las cifras del ensayo.
2. `git add -A` y **parar**.
