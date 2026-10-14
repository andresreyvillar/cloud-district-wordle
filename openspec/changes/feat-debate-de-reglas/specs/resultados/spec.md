# Deltas de `resultados` — feat-debate-de-reglas

## ADDED Requirements

### Requirement: El debate vive en tablas aditivas que solo escriben sus funciones

`rule_polls`, `rule_votes` y `rule_proposals` son **aditivas** (ADR 0005). Con la clave pública se leen —las
propuestas, solo las aprobadas— y no se escriben: insert, update, delete y truncate están revocados. Las únicas
escrituras son `votar_regla` (votación abierta, opción existente, votante que ha jugado; un voto por persona,
cambiable) y `proponer_regla` (autor que ha jugado, título de 3 a 120 caracteres, explicación de 10 a 2000, como
mucho tres pendientes por persona), y toda propuesta entra pendiente.

#### Scenario: la clave pública no escribe en las tablas
- GIVEN los roles `anon` y `authenticated`
- WHEN intentan insertar, cambiar, borrar o vaciar las tablas del debate
- THEN Postgres lo rechaza

#### Scenario: una votación cerrada no admite votos
- GIVEN una votación cerrada
- WHEN llega un voto
- THEN se rechaza y no se guarda

```yaml
checks:
  - type: regex
    file: supabase/migrations/20261014120000_create_rule_debate.sql
    pattern: 'revoke insert, update, delete, truncate on public\.rule_polls, public\.rule_votes, public\.rule_proposals'
    describe: la clave pública no tiene privilegios de escritura sobre las tablas del debate
  - type: regex
    file: supabase/migrations/20261014120000_create_rule_debate.sql
    pattern: "for select using \\(estado = 'aprobada'\\)"
    describe: con la clave pública solo se leen las propuestas aprobadas
```

verified-by:
  - tests/slices/debate-de-reglas/test_debate_sql.py
