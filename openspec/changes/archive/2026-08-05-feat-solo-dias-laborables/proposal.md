# Proposal — feat-solo-dias-laborables

> **Slice:** [`medallas-en-el-resumen-diario`](../../slices/estadisticas/medallas-en-el-resumen-diario.md)
> (modificación) · Regla de temporada nueva, acordada el 2026-08-04.

## Why

El grupo cierra una regla más: **las temporadas son de lunes a viernes**. El fin de semana no cuenta.

Medido antes de escribir nada, la regla resulta ser dos cosas a la vez:

**Para casi todo, formaliza lo que ya pasaba por accidente.** Los fines de semana son 13 resultados de
1533 (0,85%), repartidos en 10 jornadas, y **ninguna llega a los cinco jugadores** del umbral de muestra.
Todo lo que ya dependía de ese umbral —la dificultad del día, `El día imposible`, `Superviviente`, y los
días que forman la temporada en el modelo de participación— no cambia de resultado. Lo que cambia es que
deja de depender de una coincidencia: si un sábado jugaran cinco personas, hoy contaría.

**Para `Pleno`, arregla un fallo que la hacía inganable.** Los días de la temporada se derivan de los datos,
así que **una sola persona jugando un domingo se lo bloquea a todo el grupo**. Medido sobre 123 parejas
jugador-mes: hoy lo logran **0**; solo con días laborables, **6 (4,9%)**. Cinco de los nueve meses del
histórico tienen una jornada de fin de semana, y nueve de esas diez jornadas son **un único jugador**.

De paso: el brief afirmaba que `Pleno` lo lograba el 12%. Es falso, son 0. La cifra se midió con una
definición de "día del mes" distinta de la que implementa el código.

## What Changes

- **`tools/calendario.py`** (nuevo) — la **única** definición de día laborable del proyecto, como función
  pura sobre la fecha de la fila. Un módulo propio y no una función escondida en `badges.py` porque la
  regla la van a consumir tres dominios: medallas, participación y figuras. La lección de no tener dos
  definiciones de "día difícil" aplica igual a "día laborable".
- **`tools/badges.py`** — filtra por día laborable en las dos entradas públicas del cálculo.
- **Tests de escenario** — cuatro escenarios nuevos, y los fixtures existentes pasan a fechas laborables:
  `dia=(i % 28) + 1` sobre agosto de 2026 cae en sábado o domingo cinco veces de quince.
- **`.github/workflows/post_ranking.yml`** — el cron pasa a `0 17 * * 1-5`. Necesario, no cosmético: la
  jornada se deriva de `max(wordle_id)`, y en fin de semana no llegan filas nuevas, así que un cron
  dominical republicaba la jornada del viernes con sus medallas. La ingesta horaria (`update_stats.yml`)
  **no** se toca: sigue los siete días, que es lo que sostiene la decisión de seguir capturando el fin de
  semana.
- **Briefs** — la regla en `reglas-temporadas.md`, la recalibración en `medallas.md`, el alcance en
  `ranking-de-figuras.md`.

No toca el esquema, no toca la ingesta y no escribe nada en la base de datos.

## Out of Scope

| Fuera | Disparador que lo traería |
|---|---|
| **Que `ser el mejor del día` exija muestra mínima** | Decisión del grupo. Medido: 25 de los 447 créditos históricos salen de días con menos de cinco jugadores, y la regla de días laborables solo tapa 10. Es una regla distinta con el mismo síntoma; anotada como abierta en el brief |
| Dejar de ingerir los resultados de fin de semana | Decisión tomada al contrario: se siguen capturando y guardando, y la exclusión vive en el cálculo. Nada destructivo y reversible si el grupo cambia de opinión |
| Aplicar la regla al modelo de participación | No está implementado todavía. La regla queda escrita en su brief y el slice nacerá con ella |
| Aplicar la regla al ranking de figuras | Igual: el clasificador no está calibrado. Alcance decidido (sí aplica) y anotado en el brief |
| Ocultar los resultados de fin de semana en la web | La v1 no cambia ([ADR 0005](../../decisions/0005-hosting-y-convivencia-v1-v2.md)). Cómo se muestran es cosa del rediseño |
| Días festivos y vacaciones | Un festivo laborable con poca gente ya lo absorbe el umbral de muestra. Un calendario de festivos es un dominio nuevo y nadie lo ha pedido |

## Impact

| Dimensión | Detalle |
|---|---|
| **Slices** | Modifica `medallas-en-el-resumen-diario` (+4 escenarios: 10 → 14) |
| **Capabilities** | `estadisticas` (1 ADDED, 1 MODIFIED) · `publicacion` (1 MODIFIED) |
| **Archivos nuevos** | `tools/calendario.py` |
| **Archivos modificados** | `tools/badges.py`, `tests/slices/medallas-en-el-resumen-diario/test_medallas.py`, `.github/workflows/post_ranking.yml` |
| **Migraciones** | Ninguna |
| **Compatibilidad** | La web no cambia. El mensaje del canal conserva su formato. Los sábados y domingos **no se publica resumen**: el cron pasa a lunes-viernes |
| **Riesgo** | **Bajo en datos, medio en percepción.** No escribe nada. Pero cambia retroactivamente un palmarés: `Pleno` pasa de inganable a tener 6 ganadores históricos, y una persona pierde `Fondista` en un mes (59 → 58 parejas). Las medallas son derivadas, así que el cambio es automático y visible el día que se publique |

### Capabilities

| Capability | Toca | Por qué |
|---|---|---|
| `estadisticas` | sí | Qué días entran en el cálculo es parte de la métrica |
| `publicacion` | sí | En sábado y domingo el resumen no lleva sección de medallas |
| `ranking` | no | El modelo de participación no está implementado; la regla queda en su brief |
| `resultados`, `ingesta`, `identidad` | no | Se sigue capturando y guardando exactamente igual |

## Validation Gates

```bash
# 1 · Harness
python3 -m tools.wslice slice validate medallas-en-el-resumen-diario
python3 -m tools.wslice verify gates --slice medallas-en-el-resumen-diario --change-id feat-solo-dias-laborables
python3 -m tools.wslice slice coverage medallas-en-el-resumen-diario

# 2 · Tests
.venv/bin/python3 -B -m pytest tests/slices/medallas-en-el-resumen-diario -q
.venv/bin/python3 -B -m pytest -q

# 3 · Sintaxis del pipeline
.venv/bin/python3 -B -m py_compile tools/calendario.py tools/badges.py

# 4 · Ensayo con datos reales SIN publicar: el palmarés antes y después de la regla,
#     que es la única forma de comprobar las cifras de este proposal
```

**Gate 4c (mutación)** aplica. Candidatos: el comparador del día de la semana (`<= 5` por `< 5`), el
filtro aplicado en una sola de las dos entradas públicas, y devolver la lista sin filtrar.

**Gate 4e (security review)** no aplica: no hay superficie nueva, ni credenciales, ni datos nuevos que
salgan al canal. El cambio solo quita filas de un cálculo.

## Notas de honestidad

- **La regla no viene del canal, viene del dueño del proyecto.** Las temporadas mensuales se votaron en
  Slack (6-0); esto no. Queda anotado en el brief como acordado con esa procedencia, y conviene llevarlo al
  canal junto al modelo de participación, que arrastra la misma deuda.
- **El efecto medido es casi nulo por una razón que puede cambiar.** Los fines de semana no cuentan hoy
  porque nadie juega: 1,3 jugadores de media. Si el grupo empezara a jugar en sábado, esta regla pasaría de
  formalidad a decisión con consecuencias. La cifra del 0,85% es de hoy, no una propiedad del juego.
- **El arreglo de `Pleno` cambia el pasado.** Seis parejas jugador-mes que nunca vieron la medalla la
  tendrían. Como las medallas se calculan y no se guardan, no hay nada que migrar — pero tampoco hay aviso:
  el palmarés simplemente será distinto. Es el precio de la decisión de no almacenarlas, y aquí se cobra.
- **Una cifra de calibración estaba mal y nadie lo detectó** hasta medir para este pack. El brief decía 12%
  para `Pleno`; eran 0. Es la segunda vez que una cifra escrita en un documento se hereda sin volver a
  medirla, y va como lección con destino mecánico.
