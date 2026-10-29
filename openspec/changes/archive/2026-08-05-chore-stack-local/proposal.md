# Proposal — chore-stack-local

> **Slice:** N/A — herramienta de desarrollo, sin comportamiento observable de producto.

## Why

Probar la v2.0 con datos reales exigía lanzar cuatro comandos a mano en el orden correcto y recordar cuál de
ellos escribe dónde. Eso se olvida, y el que se olvida es el que publica en Slack.

## What Changes

`tools/local_stack.py`: un comando que corre **la misma secuencia que los cron** contra la Supabase de
producción, y que **declara en voz alta qué va a tocar** antes de tocarlo.

### La decisión: apuntar a producción, y separar el riesgo por paso

La primera idea fue montar un Supabase local con el CLI para aislar las escrituras. Se descartó al mirar
**qué escribe cada paso** en lugar de razonar sobre local-contra-remoto:

| Paso | Escribe en | Por defecto |
|---|---|---|
| ingesta del canal | `wordle_results`, el registro real de partidas de personas | **apagada** |
| materializar temporadas | `season_snapshots`, **derivada** | encendida |
| resumen diario | Slack | **siempre en seco** |
| servir la web | nada | encendida |

`season_snapshots` es derivada: se borra y se recalcula sin perder nada, y es justo la pieza que se quiere
recalcular veinte veces mientras se afina un umbral. Aislarla no aporta nada y costaba Docker, el CLI y
varios gigas de imágenes.

La ingesta va apagada porque es la única que toca el registro real, y **no hace falta para probar**: el cron
ya la ejecuta cada hora. Y el resumen no publica nunca: compone y imprime.

## Out of Scope

| Fuera | Disparador |
|---|---|
| Un Supabase local con el CLI | Que haga falta probar una **migración** de esquema. Para eso sí: una migración no es idempotente y no se ensaya contra producción |
| Una rama de Supabase | Igual, y además el MCP no la alcanza hoy |
| Cron de verdad en local | Lo dispara el operador; automatizarlo escondería justo lo que esta herramienta declara |

## Impact

| Dimensión | Detalle |
|---|---|
| **Archivos nuevos** | `tools/local_stack.py` |
| **Migraciones** | Ninguna |
| **Riesgo** | Bajo, y **declarado en pantalla**: escribe una tabla derivada y nada más, salvo que se pida la ingesta a propósito |

## Validation Gates

```bash
.venv/bin/python3 -B -m py_compile tools/local_stack.py
python3 tools/local_stack.py --seco --sin-web      # no escribe nada
python3 tools/local_stack.py --temporada 2026-08   # escribe una sola instantánea
.venv/bin/python3 -B -m pytest -q
```

**Gate 4c (mutación):** no aplica de forma útil. La herramienta no tiene lógica propia: orquesta módulos que
ya tienen sus escenarios y su prueba de mutación.

## Notas de honestidad

- **Esta herramienta escribe en producción**, aunque sea en una tabla derivada. Por eso lo primero que hace
  es imprimir qué toca y qué no. Una herramienta sigilosa que escribe en producción es una trampa.
- **`--seco` no cubre la ingesta.** Si se pide `--con-ingesta --seco`, la ingesta se salta en lugar de
  simularse: `add_results.py` no tiene modo seco, y fingir que lo tiene sería peor que no ofrecerlo.
- **El enlace del resumen sigue apuntando a la v1.** Es correcto hoy —es la web publicada— y lo cambia
  `captura-apunta-a-la-v2` cuando la v2 exista en Cloudflare.
