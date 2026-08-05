# Proposal — feat-clasificacion-de-temporada

> **Slice:** [`clasificacion-de-temporada`](../../slices/ranking/clasificacion-de-temporada.md)

## Why

Es la vista que el grupo abre a diario y la primera con contenido real de la v2.0. Hoy la web pinta un
marcador de posición: julio está calculado y materializado, y no hay tabla que lo muestre.

Y trae el modelo de imputación, que es lo que hace que la clasificación mida participación y no solo
aciertos.

## What Changes

- **`tools/standings.py`** (nuevo, puro) — el modelo de imputación y el orden de la tabla.
- **`tools/seasons.py`** — la instantánea gana `clasificacion`, `dificultad` por jornada, `mas_dificil`,
  `mas_facil`, `media_grupo` y los totales del HUD.
- **`v2/js/ui/temporada.js`** + estilos — la vista con la dirección visual de la
  [liga arcade](../../../docs/context/sources/2026-08-05-diseno-liga-arcade.md).

### Qué se toma del diseño y qué no

**Sí:** la paleta de puntuación (1-3 verde, 4-5 amarillo, 6 morado, fallo rojo, no jugada en contorno), las
tipografías (Poppins, DM Mono, Silkscreen), la barra superior con HUD, el titular grande con entradilla en
serif itálica, el podio de tres, el `MARCADOR`, la sección de `LOGROS` con los iconos SVG, y las columnas de
dificultad por jornada.

**No:** los doce motes, los dorsales de tres letras y el Δ de posición. Son reglas de juego sin decidir —dos
de ellas bloqueadas por el grupo— y el Δ además exigiría guardar la clasificación de la jornada anterior.
Quedan registradas en la fuente del diseño.

## Out of Scope

| Fuera | Disparador |
|---|---|
| Motes, dorsales y Δ | Decisión del grupo; el Δ además exige versionar la clasificación |
| El álbum de figuras en esta vista | El clasificador no está calibrado |
| Podios separados | Fase 3, sin decidir |

## Impact

| Dimensión | Detalle |
|---|---|
| **Slices** | Implementa `clasificacion-de-temporada` (8 escenarios) |
| **Capabilities** | `ranking` · `dashboard` |
| **Migraciones** | Ninguna: claves nuevas en la carga útil JSONB |
| **Riesgo** | **Alto en percepción.** Esta tabla cambia el campeón en 6 de 8 meses del histórico. No se publica hasta el merge, pero es lo que el grupo va a discutir |

## Validation Gates

```bash
python3 -m tools.wslice slice validate clasificacion-de-temporada
python3 -m tools.wslice verify gates --slice clasificacion-de-temporada --change-id feat-clasificacion-de-temporada
python3 -m tools.wslice slice coverage clasificacion-de-temporada
.venv/bin/python3 -B -m pytest -q
node --test tests/v2/
python3 tools/local_stack.py --temporada 2026-07     # y mirar julio en el navegador
```

**Gate 4c (mutación):** el `max` que impide que faltar mejore la media, el margen, el tope del fallo y el
criterio de orden.

## Notas de honestidad

- **El modelo sigue sin validar por el grupo.** Implementarlo no lo publica, pero cada día que pasa con esto
  construido y sin conversación es un día en que la sorpresa será mayor.
- **La media imputada de la temporada en curso es volátil** por construcción: el día 3 una ausencia es un
  tercio de la nota. Julio, cerrado y con 23 días, es la vista que se parece a lo que verá el grupo.
- **El diseño trae más de lo que se implementa.** Lo que falta no es por falta de tiempo sino porque son
  reglas sin decidir, y meterlas sin decisión es exactamente lo que este método evita.
