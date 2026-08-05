# Proposal — feat-temporada-mensual

> **Slice:** [`temporada-mensual`](../../slices/ranking/temporada-mensual.md)

## Why

Es la única regla que el grupo cerró por votación (6-0) y de la que dependen las cuatro vistas de la v2.0.
Sin el concepto de temporada no hay clasificación mensual, ni archivo, ni ficha de jugador: hoy el ranking
agrega todo el histórico y "¿quién ganó en marzo?" no tiene dónde vivir.

Y nace con contenido: aplicada al histórico, la web arranca con **9 temporadas cerradas**.

## What Changes

Primer slice bajo el [ADR 0008](../../decisions/0008-donde-vive-el-calculo.md): **el cálculo vive en Python
y se materializa**.

- **`tools/seasons.py`** (nuevo, puro) — el modelo: qué temporadas hay, qué días forman cada una, qué
  resultados cuentan y cuál está en curso. Reutiliza `tools/calendario.py` para el día laborable, en lugar
  de tener una segunda definición.
- **Tabla `season_snapshots`** (nueva, aditiva) — `temporada` como clave, `payload` JSONB y `updated_at`.
  No toca ninguna columna que lea la v1 ([ADR 0005](../../decisions/0005-hosting-y-convivencia-v1-v2.md)).
- **`tools/materialize_seasons.py`** (nuevo) — calcula y escribe instantáneas, con `--dry-run` y con
  `--todas` para recalcular el histórico. Sin `--todas`, solo la temporada en curso.
- **`update_stats.yml`** — tras ingerir, materializa la temporada en curso.

## Out of Scope

| Fuera | Disparador que lo traería |
|---|---|
| La clasificación y el modelo de imputación | `clasificacion-de-temporada`. Este slice no ordena a nadie |
| Las medallas en la instantánea | El slice del medallero. Están calculadas y sin materializar |
| Que la web lea la instantánea | Llega con la primera vista que la use |
| Que la web avise de una instantánea rancia | Requirement de `dashboard`, con su vista |
| El cierre de la etapa del 31 de agosto | Fase 3: el grupo no ha decidido si se corona un ganador del periodo |

## Impact

| Dimensión | Detalle |
|---|---|
| **Slices** | Crea `temporada-mensual` (7 escenarios) |
| **Capabilities** | `ranking` · `resultados` |
| **Archivos nuevos** | `tools/seasons.py`, `tools/materialize_seasons.py`, `tests/slices/temporada-mensual/` |
| **Archivos modificados** | `.github/workflows/update_stats.yml` |
| **Migraciones** | **Sí**: tabla `season_snapshots`. Aditiva, con RLS de solo lectura para la clave publicable |
| **Compatibilidad** | La v1 no nota nada: no se toca `wordle_results` ni ninguna columna suya |
| **Riesgo** | **Medio.** Escribe en producción, pero en una tabla nueva y derivada: borrarla y recalcularla no pierde nada. El riesgo real es que el cron escriba una instantánea mal calculada y la web la pinte como verdad |

## Validation Gates

```bash
python3 -m tools.wslice slice validate temporada-mensual
python3 -m tools.wslice verify gates --slice temporada-mensual --change-id feat-temporada-mensual
python3 -m tools.wslice slice coverage temporada-mensual
.venv/bin/python3 -B -m pytest -q
.venv/bin/python3 -B -m py_compile tools/seasons.py tools/materialize_seasons.py

# Ensayo obligatorio antes de escribir: el modelo contra los datos reales, sin materializar
.venv/bin/python3 -B tools/materialize_seasons.py --todas --dry-run
```

**Gate 4c (mutación)** aplica. Candidatos: el filtro de día laborable, el umbral de muestra mínima, el
recorte del mes de la fecha y cuál es la temporada en curso.

**Gate 4e (security review):** la tabla nueva necesita **RLS de solo lectura** para la clave publicable,
igual que `wordle_results`. Sin eso, la clave que va en el código de la web podría escribir la instantánea.
Hay que comprobarlo activamente, no suponerlo.

## Notas de honestidad

- **La cifra de "9 temporadas cerradas" hay que volver a medirla**, no heredarla. Viene de un análisis
  anterior a la regla de días laborables y a la limpieza de identidad, y este proyecto ya ha propagado dos
  cifras falsas por no remedirlas (`docs/lecciones.md`). El ensayo de este pack la mide.
- **Agosto de 2026 va a salir raro y es correcto.** Lleva tres días de datos y arranca en fin de semana, así
  que la temporada en curso tendrá muy pocos días. No es un fallo del cálculo.
- **La instantánea introduce estado derivado que puede quedar rancio.** Este slice registra `updated_at`
  precisamente para que se pueda detectar, pero **nadie lo mira todavía**: hasta que la web avise, una
  instantánea de hace tres días se pinta igual que una de hace un minuto.
