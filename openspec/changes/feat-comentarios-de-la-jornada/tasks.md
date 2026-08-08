# Tasks — feat-comentarios-de-la-jornada

- [x] **Frecuencias remedidas** sobre las 186 jornadas que cuentan, antes de fijar ningún margen.
- [x] Slice con 9 escenarios · 15 tests · cobertura 9/9 · `tools/comentarios.py` puro y sin azar.
- [x] Los detectores emiten **hechos**, no texto, para que la redacción se pueda cambiar sin tocarlos.
- [x] El umbral de día difícil se reutiliza de `badges`, no se declara otro.
- [x] **Gate 4c — 7 mutantes, 1 superviviente corregido, 0 al final:**

| Mutante | Resultado |
|---|---|
| el margen de «no inspirado» vuelve a ser laxo | 🔴 |
| el umbral de día difícil deja de ser el de las medallas | 🔴 |
| se comenta sin muestra para calibrar | 🔴 |
| se permite repetir el mismo tipo de chiste | 🟢 → el test usaba las ausencias, que van agrupadas. Rehecho con tres «no inspirado». Corregido |
| las ausencias se miden contra quien jugó alguna vez | 🔴 |
| la frase es siempre la misma | 🔴 |
| se ignora la concordancia en plural | 🔴 |

- [x] **Tres fallos vistos en el mensaje real, no en un test:** el mismo chiste tres veces, la concordancia
      en plural, y llamar «rajada» a alguien que jugó una vez en marzo.
- [x] El test de concordancia estaba mal: con la jornada 1600 salía la frase sin verbo concordado y pasaba
      sin comprobar lo que decía comprobar. Ahora recorre todo el ciclo de frases.
- [x] Fuera de alcance declarado: la redacción generativa.

## Comandos

```bash
.venv/bin/python3 -B -m pytest tests/slices/comentarios-de-la-jornada/
.venv/bin/python3 -B -m pytest
python3 -m tools.wslice verify gates --slice comentarios-de-la-jornada --change-id feat-comentarios-de-la-jornada
python3 tools/local_stack.py --seco --sin-web
```
