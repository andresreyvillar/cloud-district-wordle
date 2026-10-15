# Deltas de `resultados` — feat-propuestas-votables

## MODIFIED Requirements

### Requirement: El debate vive en tablas aditivas que solo escriben sus funciones

Con la clave pública se leen las propuestas que no están rechazadas. `rule_proposal_votes` guarda un voto por
`(propuesta, votante)`, `a_favor` o `en_contra`; solo lo escribe `votar_propuesta`, que rechaza propuestas
inexistentes o rechazadas, sentidos desconocidos y a quien no ha jugado nunca.

#### Scenario: una propuesta rechazada no admite votos
- **WHEN** llega un voto a una propuesta rechazada
- **THEN** se rechaza como propuesta desconocida

#### Scenario: la clave pública no escribe en los votos de propuestas
- **WHEN** se intenta insertar o borrar directamente en `rule_proposal_votes`
- **THEN** Postgres lo rechaza

```yaml
checks:
  - type: regex
    file: supabase/migrations/20261015090000_public_votable_proposals.sql
    pattern: 'revoke insert, update, delete, truncate on public\.rule_proposal_votes from anon, authenticated;'
    describe: la clave pública no tiene privilegios de escritura sobre los votos de propuestas
```

verified-by:
  - tests/slices/debate-de-reglas/test_debate_sql.py
