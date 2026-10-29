# Tareas

- [x] Medir el reparto real de memes sobre 199 jornadas antes de tocar nada.
- [x] Medir el molde de la sospecha (emoji y nota) y comprobar que la rotación sí funciona.
- [x] `MEMES` de tupla de pares a `dict[str, tuple[str, ...]]` con 79 plantillas.
- [x] Implementar las cuatro condiciones muertas que se pueden definir sin duplicar criterios.
- [x] Pasar al meme los datos que le faltaban: figuras reconocibles, empate en cabeza, plantilla, cuadrículas.
- [x] Ampliar la sospecha con frases sin emoji y sin citar la nota, en singular y en plural.
- [x] Escenarios nuevos en `voz-de-la-jornada` y `comentarios-de-la-jornada`, con sus tests.
- [x] Gate 4c: seis mutaciones, cada una mata su escenario.
- [x] Suite completa, `slice coverage`, `slice validate`, `verify gates`.
- [ ] Handoff staged: lo mergea el humano.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
python3 -m tools.wslice slice coverage voz-de-la-jornada
python3 -m tools.wslice slice coverage comentarios-de-la-jornada
python3 -m tools.wslice slice validate
python3 -m tools.wslice verify gates --slice voz-de-la-jornada --change-id fix-variedad-de-frases
```
