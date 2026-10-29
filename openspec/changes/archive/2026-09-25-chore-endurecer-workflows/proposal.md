# Proposal — chore-endurecer-workflows

> **Slice:** N/A — endurecimiento de CI. Ningún workflow cambia lo que hace ni cuándo lo hace.

## Why

Dos avisos bajos de la revisión de seguridad de `feat-nivel-congelado`, los dos anteriores a ese cambio:

- **L-1.** `update_stats.yml` metía `${{ inputs.vueltas }}` directamente en el script de `run:`. Lo que llega de
  `workflow_dispatch` es texto de quien lo dispara, y así se ejecutaría como shell. Explotarlo exige ya
  permiso de escritura en el repositorio, pero es el patrón clásico de inyección en Actions.
- **L-2.** Las actions iban fijadas por tag (`@v4`), que se puede mover. Fijarlas por SHA protege de un tag
  reescrito.

## Qué cambia

- `vueltas` entra por `env:` (`VUELTAS_PEDIDAS`) y se exige que sea un número; sin input —las ejecuciones del
  cron— sigue siendo 7.
- `actions/checkout`, `actions/setup-python` y `actions/setup-node` fijadas por el SHA de su `v4` actual, con
  el tag en un comentario, en los tres workflows.

## Verificación

- Los tres YAML se cargan.
- La guarda con el mismo bash: vacío → 7, `3` → 3, `7; echo PWNED` y `abc` → rechazados.
- SHAs resueltos con `gh api repos/<action>/git/ref/tags/v4` el 2026-09-25.
