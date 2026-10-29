# Deltas de `ranking` — feat-figuras-simetricas

## MODIFIED Requirements

### Requirement: Una cuadrícula simétrica es geométrica, aunque tenga demasiada tinta

El geométrico se reconoce por **dos vías**, y basta una:

| Vía | Condición | Cuándo se evalúa |
|---|---|---|
| escasez de tinta | densidad ≤ 0,40 y como mucho un amarillo | antes de la flor, como siempre |
| **espejo** | todas las filas del cuerpo son iguales leídas al revés | **en último lugar** |

Antes solo existía la primera, y dejaba fuera dibujos regulares con masa: un arco de densidad 0,60 salía
abstracto. Lo que hace geométrico a un geométrico es la forma; la escasez de tinta era un sustituto de la
regularidad, y no la mide.

**El espejo se consulta al final, cuando ninguna otra regla ha reconocido nada.** Es lo que hace el cambio
seguro, y no es un detalle de orden: unos pétalos son simétricos por naturaleza, así que un espejo evaluado
antes de la flor le robaría la categoría a flores legítimas. Puesto al final, el espejo **solo puede ascender
abstractos** — ninguna cuadrícula que hoy tiene figura la pierde. La alternativa medida, exigirle al espejo
como mucho un amarillo igual que a la otra vía, protege lo mismo y rescata dos casos menos.

El espejo se calcula sobre el **cuerpo** —la cuadrícula sin la banda verde final—, igual que el resto de los
rasgos. La banda es el suelo del dibujo y es simétrica siempre, así que incluirla concedería el espejo a
cualquier partida resuelta.

**La simetría es exacta: cero celdas rotas.** Admitir una sola llevaría la cobertura del 1,1% al 7,7% de
producción y costaría una ficha del conjunto dorado. La medida acompaña esta decisión en el proposal, porque
el reparto mejora y el acuerdo empeora: es el canje que ya tumbó a un candidato anterior.

Solo cuenta la simetría respecto al **eje vertical**. Un dibujo regular respecto a la diagonal —una
escalera— no cumple el espejo y sigue saliendo abstracto: es una limitación conocida.

```yaml
checks:
  - type: cli-command
    command: python3 tools/calibrate_figures.py
    expect: acuerdo ≥ 24 fichas y geométrico por debajo del 13% del reparto en producción
```

#### Scenario: un dibujo simétrico con mucha tinta es geométrico
- GIVEN una cuadrícula resuelta cuyas filas son todas palíndromas y cuya densidad supera 0,40
- WHEN se clasifica
- THEN la categoría es geométrico

#### Scenario: una sola celda rota niega el espejo
- GIVEN una cuadrícula por lo demás simétrica en la que una celda rompe el espejo
- WHEN se clasifica
- THEN la categoría es abstracto

#### Scenario: el espejo no le quita la flor a unos pétalos simétricos
- GIVEN una cuadrícula simétrica que cumple lo que define una flor
- WHEN se clasifica
- THEN la categoría es flores

#### Scenario: el espejo no le quita el loro a un loro simétrico
- GIVEN una cuadrícula simétrica que cumple lo que define un loro
- WHEN se clasifica
- THEN la categoría es loro

#### Scenario: ninguna cuadrícula con figura pierde su figura
- GIVEN el conjunto de patrones reales
- WHEN se clasifican con el espejo y sin él
- THEN las únicas que cambian de categoría son las que salían abstractas

#### Scenario: acertar a la primera no es un espejo
- GIVEN una cuadrícula que es solo la banda verde final
- WHEN se clasifica
- THEN la categoría es abstracto, porque no hay cuerpo

#### Scenario: sin resolver no hay figura, aunque haya simetría
- GIVEN una cuadrícula simétrica que no resuelve la palabra
- WHEN se clasifica
- THEN la categoría es abstracto

#### Scenario: la simetría se mide sin contar el suelo
- GIVEN dos cuadrículas iguales salvo que una resuelve la palabra y la otra no
- WHEN se clasifican
- THEN la banda verde final no es lo que concede el espejo

verified-by:
  - tests/slices/clasificacion-de-figuras/test_simetria.py
