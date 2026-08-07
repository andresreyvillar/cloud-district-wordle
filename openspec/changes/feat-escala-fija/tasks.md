# Tasks — feat-escala-fija

- [x] Slice con 6 escenarios y la tabla de qué escala usa cada gráfico, con su porqué.
- [x] 7 tests · cobertura 6/6 · `v2/js/data/escala.js` puro.
- [x] Conectado a las dos gráficas y **declarada la escala** en las dos cabeceras.
- [x] **Gate 4c — 5 mutantes, 2 supervivientes corregidos, 0 al final:**

| Mutante | Resultado |
|---|---|
| la escala de intentos baja a 6 | 🔴 |
| la distribución se escala al primer jugador | 🟢 → fixture con el máximo en la primera fila. Corregido |
| los valores fuera de escala no se recortan | 🔴 |
| una barra mínima se queda en cero | 🔴 |
| sin guarda de escala cero | 🟢 → `recortar` convertía el infinito en 100 y la aserción medía finitud. Corregido |

- [x] Verificado en navegador con datos reales: temporada 0 al 83% y agosto al 56% (antes, las dos al 100%);
      Claire al 70% y Javi Calvo, con una partida, al 1% (antes, los dos al 100%).
- [x] Corregido «1 partidas jugadas» al verlo en el navegador.
