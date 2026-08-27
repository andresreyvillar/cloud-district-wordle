# Tareas

- [x] Listar el registro entero y comprobar que no había ninguna referencia reconocible.
- [x] 110 plantillas nuevas con referencias adaptadas al juego, repartidas por las 11 condiciones.
- [x] Intercalarlas con las genéricas, porque apiladas al final no salían nunca.
- [x] Los ausentes en orden de clasificación, respetando el que ya trae `con_puesto`.
- [x] Escenario nuevo para el orden de los ausentes, con su test.
- [x] Gate 4c: tres mutaciones, cada una mata su escenario.
- [x] Suite completa, `slice coverage`, `slice validate`, `verify gates`.
- [ ] Handoff staged: lo mergea el humano.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
python3 -m tools.wslice slice coverage resumen-diario-compuesto
python3 -m tools.wslice verify gates --slice resumen-diario-compuesto --change-id feat-memes-con-referencias
```
