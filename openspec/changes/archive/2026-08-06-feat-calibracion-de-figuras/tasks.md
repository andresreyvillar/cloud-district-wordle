# Tasks — feat-calibracion-de-figuras

> **Slice:** N/A. No hay escenarios que cubrir: lo que se verifica es el **acuerdo con las etiquetas
> humanas**, y vive en `tests/figuras/test_clasificador.py` como gate.

## 1 · El examen, antes del clasificador

- [x] `tests/figuras/test_clasificador.py` parsea las 30 fichas **del propio source**, no una copia.
      Un test comprueba que se leen las 30 y que el reparto es 11/10/5/4: si el parseo se rompe, el examen
      se aprobaría con cero preguntas.
- [x] `ACUERDO_MINIMO = 24` declarado en el test. Es lo medido, no una aspiración.
- [x] Rojo comprobado: los 12 tests fallan por `ModuleNotFoundError` antes de escribir el módulo.

## 2 · Calibrar con dos criterios

- [x] Banco de calibración con **acuerdo** (30 fichas) y **reparto** (1521 patrones reales).
- [x] Nueve candidatos medidos. El primero —83% de acuerdo— **descartado por el segundo criterio**: marcaba
      flor el 55% de producción porque su regla se cumplía más según crecía la cuadrícula.
- [x] Dos rasgos nuevos, sacados de mirar qué separa de verdad las etiquetas: **el amarillo del loro toca el
      cuerpo** y **la flor necesita pétalos libres**.
- [x] Candidato adoptado: **24/30 (80%)** de acuerdo · reparto 47/32/14/7 frente al 37/33/17/13 humano,
      desvío total del 10%.

## 3 · El clasificador

- [x] `tools/figures.py`: función pura, cuatro reglas en cascada, umbrales con su motivo y su medida.
- [x] Acepta las dos formas del patrón: emoji (el conjunto dorado) y `G/Y/.` con barras (la ingesta).
- [x] `tools/calibrate_figures.py`: rehace las dos medidas. Solo lectura, `--sin-red` para el acuerdo solo.

## 4 · Gates

- [x] Suite completa en verde (`pytest -B`), 14 tests del pack.
- [x] **Gate 4c — mutación: 5 mutantes, 1 supervivencia corregida.**

| Mutante | Resultado |
|---|---|
| el amarillo del loro puede flotar | 🔴 caza el gate de acuerdo y el test del pico |
| basta un pétalo libre para que sea flor | 🟢 **SOBREVIVIÓ** → ver abajo |
| una cuadrícula sin resolver sí tiene figura | 🔴 caza el gate de acuerdo |
| la forma con barras no se normaliza | 🔴 caza tres casos del vocabulario |
| la fila de pétalos admite verde | 🔴 caza el caso de la ficha 11 |

- [x] **La supervivencia era un hueco real.** Bajar el mínimo de pétalos de 3 a 1 **sube** el acuerdo a
      25/30 (rescata las fichas 01 y 26) y empeora el reparto. El umbral estaba justificado solo por el
      segundo criterio, que necesita red y no cabe en la suite. Corregido con dos tests: el caso
      discriminante de la ficha 11, y la propiedad de que **alargar la cuadrícula no puede convertir el
      ruido en flor** —que es exactamente cómo falló el candidato descartado—. Los dos mutantes mueren ya.

## 5 · Lo que este pack NO hace

- **No clasifica nada en producción.** Nadie llama al clasificador todavía; la columna `pattern` solo se lee.
- **No crea la capability `patrones`.** Requiere acuerdo explícito y no lo hay.
- **No decide la puntuación del álbum** (recuento absoluto o ponderado por rareza): sigue abierto en el brief.
- **No separa `loto`.** Un ejemplo no calibra nada; sigue plegada en `flores`.
