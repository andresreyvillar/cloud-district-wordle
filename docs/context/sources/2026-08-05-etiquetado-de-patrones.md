---
fuente: etiquetado-de-patrones
tipo: conjunto-de-calibracion
fecha: 2026-08-05
autoridad: decisión (es la verdad contra la que se mide el clasificador)
capabilities: [estadisticas, ranking, dashboard]
estado: vigente
original: 30 cuadrículas del histórico, etiquetadas a mano por el dueño del proyecto
---

> **Conjunto dorado.** Estas 30 etiquetas no clasifican nada en producción: son el **examen** del
> clasificador automático. Cada cambio de peso se mide contra ellas, y sin ellas ajustar pesos es adivinar.
> Vocabulario fijado el 2026-08-05: `flores` · `abstracto` · `geometrico` · `loro`.
> Reparto medido: flores 11 (con la de `loto` plegada) · abstracto 10 · loro 5 · geometrico 4.

# Etiquetado de patrones — conjunto de calibración

> Escribe una etiqueta en cada `etiqueta:` y devuélvemelo (o pégame solo la lista: `01 loro`,
> `02 caca`…). Con esto calibro los pesos del clasificador y mido su acierto real.

**Etiquetas válidas:** `loro` · `flor` · `escuadra` · `caca`

Notas:

- Los patrones van **completos**, como se ven en el canal: la última fila cuenta como parte del dibujo.
- Si dudas entre dos, pon la que verías a primera vista. Si no ves nada, `caca` — es una respuesta
  válida y de las más útiles para calibrar.
- Puedes añadir una nota entre paréntesis si quieres explicar algo: `07 loro (el pico se ve clarísimo)`.
- Sin sugerencias del algoritmo a propósito: si te dijera lo que cree, tu etiqueta dejaría de servir
  para medirlo.

---

## 01 · #1611 · 3 intentos
```
🟨⬛🟩⬛🟨
⬛🟩🟩🟩🟩
🟩🟩🟩🟩🟩
```
etiqueta: flores

## 02 · #1644 · 3 intentos
```
⬛🟩⬛⬛⬛
⬛🟩⬛⬛⬛
🟩🟩🟩🟩🟩
```
etiqueta: geometrico

## 03 · #1601 · 3 intentos
```
🟨⬛⬛⬛⬛
⬛🟨⬛⬛🟨
🟩🟩🟩🟩🟩
```
etiqueta: flores

## 04 · #1560 · 3 intentos
```
🟩⬛⬛🟩⬛
🟩⬛⬛🟩🟨
🟩🟩🟩🟩🟩
```
etiqueta: loro

## 05 · #1566 · 3 intentos
```
🟨⬛⬛⬛⬛
⬛🟩🟩🟩⬛
🟩🟩🟩🟩🟩
```
etiqueta: geometrico

## 06 · #1575 · 3 intentos
```
⬛🟨⬛⬛🟩
🟨⬛🟨⬛🟩
🟩🟩🟩🟩🟩
```
etiqueta: flores

## 07 · #1671 · 4 intentos
```
⬛🟨⬛🟩🟨
⬛🟩🟨🟩⬛
⬛🟩⬛🟩🟩
🟩🟩🟩🟩🟩
```
etiqueta: abstracto

## 08 · #1545 · 4 intentos
```
⬛🟩⬛⬛⬛
⬛🟩⬛⬛⬛
⬛🟩⬛⬛⬛
🟩🟩🟩🟩🟩
```
etiqueta: geometrico

## 09 · #1573 · 4 intentos
```
⬛⬛⬛⬛🟨
🟨⬛⬛⬛🟨
🟨🟨🟨🟨⬛
🟩🟩🟩🟩🟩
```
etiqueta: flores

## 10 · #1568 · 4 intentos
```
⬛⬛⬛⬛⬛
⬛🟩⬛🟩🟩
⬛🟩🟩🟩🟩
🟩🟩🟩🟩🟩
```
etiqueta: abstracto

## 11 · #1621 · 4 intentos
```
⬛⬛⬛⬛🟩
⬛⬛🟨⬛🟩
⬛🟨⬛⬛🟩
🟩🟩🟩🟩🟩
```
etiqueta: abstracto

## 12 · #1601 · 4 intentos
```
⬛⬛🟨⬛⬛
⬛⬛⬛🟨⬛
⬛🟩🟩🟩⬛
🟩🟩🟩🟩🟩
```
etiqueta: flores

## 13 · #1621 · 4 intentos
```
⬛⬛⬛⬛🟩
⬛🟩⬛⬛🟩
🟨🟩⬛⬛🟩
🟩🟩🟩🟩🟩
```
etiqueta: loro

## 14 · #1594 · 4 intentos
```
⬛⬛🟨🟨🟨
⬛🟩🟨⬛🟨
🟨🟩⬛🟨⬛
🟩🟩🟩🟩🟩
```
etiqueta: flores

## 15 · #1617 · 5 intentos
```
⬛⬛🟨🟩🟨
🟩⬛🟩🟩⬛
🟩⬛🟩🟩🟩
🟩⬛🟩🟩🟩
🟩🟩🟩🟩🟩
```
etiqueta: loro

## 16 · #1545 · 5 intentos
```
⬛⬛⬛⬛🟨
⬛🟩⬛⬛⬛
⬛🟩⬛🟨⬛
⬛🟩🟨⬛⬛
🟩🟩🟩🟩🟩
```
etiqueta: abstracto

## 17 · #1644 · 5 intentos
```
⬛⬛⬛⬛🟨
⬛🟩⬛⬛🟨
⬛🟩🟩⬛⬛
🟩🟩🟩⬛⬛
🟩🟩🟩🟩🟩
```
etiqueta: abstracto

## 18 · #1574 · 5 intentos
```
⬛⬛⬛🟩🟨
⬛🟩⬛🟩⬛
⬛🟩⬛🟩⬛
⬛🟩🟩🟩⬛
🟩🟩🟩🟩🟩
```
etiqueta: loro

## 19 · #1586 · 5 intentos
```
⬛⬛⬛⬛⬛
⬛🟩🟩⬛🟩
⬛🟩🟩⬛🟩
⬛🟩🟩⬛🟩
🟩🟩🟩🟩🟩
```
etiqueta: abstracto

## 20 · #1659 · 5 intentos
```
🟨⬛🟨🟨🟨
⬛🟨🟨🟨🟨
🟨🟨🟨⬛🟨
🟩⬛🟩🟩🟩
🟩🟩🟩🟩🟩
```
etiqueta: flores

## 21 · #1638 · 5 intentos
```
🟨⬛⬛🟨⬛
⬛🟨🟩⬛🟨
⬛🟩🟩🟩⬛
⬛🟩🟩🟩🟨
🟩🟩🟩🟩🟩
```
etiqueta: flores

## 22 · #1561 · 5 intentos
```
⬛🟩⬛⬛⬛
⬛🟩⬛⬛⬛
⬛🟩🟨⬛⬛
⬛🟩⬛🟩🟩
🟩🟩🟩🟩🟩
```
etiqueta: loro

## 23 · #1582 · 6 intentos
```
🟨🟩⬛🟨⬛
⬛🟩🟩🟩🟩
⬛🟩🟩🟩🟩
⬛🟩🟩🟩🟩
⬛🟩🟩🟩🟩
⬛🟩🟩🟩🟩
```
etiqueta: abstracto

## 24 · #1604 · 6 intentos
```
⬛⬛⬛🟨⬛
🟩⬛⬛⬛🟩
🟩⬛🟩⬛⬛
🟩⬛🟩⬛🟩
🟩⬛🟩⬛🟩
🟩🟩🟩⬛🟩
```
etiqueta: abstracto

## 25 · #1533 · 6 intentos
```
⬛🟨⬛⬛⬛
⬛⬛⬛🟨⬛
⬛🟨🟨⬛🟩
⬛🟩⬛🟨🟩
🟩🟩🟩⬛🟩
🟩🟩🟩⬛🟩
```
etiqueta: abstracto

## 26 · #1649 · 6 intentos
```
🟨🟩⬛⬛⬛
⬛🟩⬛🟨🟨
⬛🟩🟩🟩⬛
⬛🟩🟩🟩⬛
🟨🟩🟩🟩⬛
🟩🟩🟩🟩🟩
```
etiqueta: flores

## 27 · #1537 · 6 intentos
```
⬛🟩⬛⬛🟩
⬛🟩🟩⬛🟩
⬛🟩🟩⬛🟩
⬛🟩🟩⬛🟩
⬛🟩🟩⬛🟩
🟩🟩🟩🟩🟩
```
etiqueta: abstracto

## 28 · #1558 · 6 intentos
```
🟨⬛⬛⬛⬛
⬛🟩⬛🟨⬛
⬛🟩🟩⬛🟩
⬛🟩🟩⬛🟩
⬛🟩🟩🟩🟩
🟩🟩🟩🟩🟩
```
etiqueta: flores

## 29 · #1562 · 6 intentos
```
⬛⬛⬛🟩🟩
⬛⬛🟨🟩🟩
🟩⬛⬛🟩🟩
🟩🟩⬛🟩🟩
🟩🟩⬛🟩🟩
🟩🟩🟩🟩🟩
```
etiqueta: loto

## 30 · #1538 · 6 intentos
```
⬛⬛🟩⬛🟩
⬛🟩🟩🟨🟩
🟩🟩🟩⬛🟩
🟩🟩🟩⬛🟩
⬛🟨⬛⬛🟩
🟩🟩🟩🟩🟩
```
etiqueta: geometrico
