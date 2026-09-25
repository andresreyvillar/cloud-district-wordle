# Tareas — chore-endurecer-workflows

1. `update_stats.yml`: `vueltas` por `env:` con guarda numérica.
2. Los tres workflows: actions fijadas por SHA con `# v4`.

```bash
python3 -c "import yaml; [yaml.safe_load(open(f)) for f in ['.github/workflows/update_stats.yml', '.github/workflows/post_ranking.yml', '.github/workflows/post_podium.yml']]"
node --test tests/
```
