# Tasks — feat-captura-del-titular

- [x] La v2 pasa a fotografiar `.hero` en lugar de la vista entera.
- [x] Se espera al mismo selector que se fotografía.
- [x] Un selector que no encaja falla nombrando el selector y la URL.
- [x] **Captura tomada de verdad** contra la web local: 1232 × 530 px, 79 KB.
- [x] **Gate 4c — 3 mutantes, 1 superviviente corregido, 0 al final:**

| Mutante | Resultado |
|---|---|
| vuelve a fotografiar la página entera | 🔴 |
| espera un selector y fotografía otro | 🔴 |
| la guarda del selector inexistente desaparece | 🟢 → el fixture hacía fallar antes al `wait_for_selector`, así que la guarda no se ejercitaba. Corregido |

## Comandos

```bash
.venv/bin/python3 -B -m pytest tests/slices/captura-apunta-a-la-v2/
python3 -m tools.wslice verify gates --slice captura-apunta-a-la-v2 --change-id feat-captura-del-titular
```
