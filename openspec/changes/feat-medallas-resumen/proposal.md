# Proposal — feat-medallas-resumen

> **Slice:** [`medallas-en-el-resumen-diario`](../../slices/estadisticas/medallas-en-el-resumen-diario.md)

## Why

El ranking dice quién va primero y nada más. Quien no falta ni un día, quien resuelve el día que el resto
se atasca o quien acierta a la primera no tiene dónde lucirlo, y eso es justo lo que el grupo lleva
pidiendo entre bromas desde el hilo de reglas: reconocimiento arriba y abajo de la tabla.

Las medallas son ese tercer eje, calibrado contra datos y no a ojo. La propuesta inicial pedía "más de 10
loros en un mes", y medido resulta **imposible**: el máximo histórico de una figura en un mes es 6 y la
mediana de partidas por jugador-mes es 14. Los umbrales de este pack están puestos donde alguien ha
llegado de verdad, con su rareza medida sobre 123 pares jugador-mes
([brief](../../../docs/context/briefs/medallas.md)).

Este pack implementa **las siete medallas que no dependen del clasificador de figuras**. Sus umbrales solo
usan puntuaciones y fechas, que están verificadas, así que no van a moverse. Las cinco de figuras esperan
la calibración del clasificador y van en su propio pack.

## What Changes

- **`tools/badges.py`** — el catálogo y el cálculo: funciones puras, sin reloj, con los resultados y la
  temporada por parámetro.
- **`tools/post_ranking.py`** — el texto del resumen gana la sección de medallas.
- **Tests de escenario** en `tests/slices/medallas-en-el-resumen-diario/`.

No toca el esquema, no toca la ingesta y no escribe nada en la base de datos.

## Out of Scope

| Fuera | Disparador que lo traería |
|---|---|
| Las cinco medallas de figuras (Ornitólog@, Arquitect@, Florista, Coleccionista, Abstract@) | La calibración del clasificador. Sus umbrales saldrían de un clasificador que manda el 69% a caca |
| Medallas de racha y de remontada | Que el grupo cierre qué es una racha y respecto a qué se mide una remontada |
| Mostrar el palmarés en la web | La ficha de jugador, en la Fase 2 |
| Medallas explícitamente negativas | El grupo pidió un "muro de la vergüenza" pero no lo ha cerrado |
| Almacenar las medallas | Son derivadas por diseño. Congelar un palmarés histórico sería otro ADR |
| Rediseñar el resumen diario | `resumen-diario-compuesto`: aquí se **añade** una sección al mensaje actual, no se sustituye el mensaje |

## Impact

| Dimensión | Detalle |
|---|---|
| **Slices** | Crea `medallas-en-el-resumen-diario` |
| **Capabilities** | `estadisticas` (3 Requirements) · `publicacion` (3 Requirements) |
| **Archivos nuevos** | `tools/badges.py`, `tests/slices/medallas-en-el-resumen-diario/test_medallas.py` |
| **Archivos modificados** | `tools/post_ranking.py` |
| **Migraciones** | Ninguna. Las medallas no se almacenan |
| **Compatibilidad** | La web no cambia. El mensaje del canal gana una sección y conserva captura y enlace |
| **Riesgo** | **Medio, y de un tipo nuevo: reputacional.** No corrompe datos, pero **publica delante de todo el grupo**. Un umbral mal calculado o un nombre mal atribuido se lee en el canal, y eso no se revierte con un `git revert` |

### Capabilities

| Capability | Toca | Por qué |
|---|---|---|
| `estadisticas` | sí | El cálculo de una medalla es una métrica derivada de los resultados |
| `publicacion` | sí | El texto que sale al canal es su responsabilidad |
| `ranking` | no | Las medallas **no** alteran la clasificación, por decisión explícita |
| `resultados`, `ingesta`, `identidad` | no | Nada se escribe ni se captura |

## Validation Gates

```bash
# 1 · Harness
python3 -m tools.wslice slice validate medallas-en-el-resumen-diario
python3 -m tools.wslice verify gates --slice medallas-en-el-resumen-diario --change-id feat-medallas-resumen
python3 -m tools.wslice slice coverage medallas-en-el-resumen-diario

# 2 · Tests
.venv/bin/python3 -B -m pytest tests/slices/medallas-en-el-resumen-diario -q
.venv/bin/python3 -B -m pytest -q

# 3 · Sintaxis del pipeline
python3 -m py_compile tools/badges.py tools/post_ranking.py

# 4 · Ensayo con datos reales SIN publicar: se imprime el texto que se publicaría
python3 -c "
import sys; sys.path.insert(0,'tools')
from badges import texto_de_medallas
# … con los resultados de producción y la temporada en curso
"
```

**Gate 4c (mutación)** aplica: candidatos son los comparadores de umbral (`>=` por `>`), la condición
doble del día imposible y el filtro de muestra mínima del día.

**Gate 4e (security review)** aplica por una razón distinta a la habitual: el cambio **publica texto en un
canal con quince personas**. Lo que hay que revisar no es una credencial, es que el texto no pueda
contener nada que no sea un nombre de jugador y un número.

## Notas de honestidad

- **Este pack activa el límite declarado del [ADR 0004](../../decisions/0004-stack-de-la-v2.md).** Ese ADR
  eligió mantener el dominio en JavaScript y dejó un disparador explícito: "si aparece un segundo
  consumidor del mismo cálculo, esta decisión se revisa". Las medallas tienen **dos** consumidores
  previstos: este resumen (Python) y la ficha de jugador de la web (JavaScript). Implementarlas en Python
  es lo correcto para el consumidor que existe hoy, pero **el ADR 0004 debería revisarse antes de escribir
  el dominio de la web**, o habrá dos implementaciones de los mismos umbrales. Queda anotado, no resuelto.
- **El ensayo no puede ser completo.** Se puede imprimir el texto que se publicaría, pero comprobar que
  Slack lo renderiza bien exige publicar. La primera publicación real es la verificación, y va delante de
  todo el grupo.
- **La medalla del día imposible depende de un umbral de dificultad (≥5,5) que solo se ha cumplido una vez
  en nueve meses.** Es deliberado —es la más legendaria de las siete— pero significa que su escenario se
  verifica con fixtures y no con un caso reciente.
