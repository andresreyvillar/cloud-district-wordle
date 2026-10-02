# Los autores externos se guardan con su nombre

> Slice: `ingesta-por-id-de-slack` (modificación).

## Why

El 2026-10-02 entraron en el canal usuarios externos (Slack Connect). `users.list` solo devuelve miembros
del workspace, así que el resultado de uno de ellos se guardó con su identificador como nombre. Slack sí da
su nombre: lo trae el propio mensaje (`user_profile`) y lo devuelve `users.info`.

## What Changes

- `tools/extract_slack.py`: `completar_directorio` añade al directorio los autores de la ventana que no
  están en él, con el nombre del perfil del mensaje o de `users.info`.
- `tools/personas.py`: el dueño declara la forma masculina del primer usuario externo.

## Out of Scope

- La fila ya guardada no se corrige a mano: la ingesta es un `upsert` que reescribe `player_name` mientras
  la fila esté en la ventana, así que el siguiente cron la arregla.

## Impact

- Toca el pipeline: el siguiente cron escribe con este código (solo cambia el nombre de autores externos).

## Validation Gates

```bash
python3 -m tools.wslice slice validate ingesta-por-id-de-slack
python3 -m tools.wslice slice coverage ingesta-por-id-de-slack
python3 -m tools.wslice verify gates --slice ingesta-por-id-de-slack --change-id fix-nombre-de-autores-externos
.venv/bin/python3 -B -m pytest tests/slices/ingesta-por-id-de-slack
```

## Capabilities

| Capability | Requirements |
|---|---|
| `ingesta` | un autor que no está en el directorio se nombra por su perfil |
