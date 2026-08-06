# Deltas de `ranking` — feat-temporada-mensual

## ADDED Requirements

### Requirement: Una temporada es un mes natural y se reinicia el día 1

La temporada de un resultado es el mes de su fecha, en formato `AAAA-MM`. El marcador se reinicia el día 1:
un resultado del día 1 pertenece a la temporada nueva, sin periodo de gracia ni solapamiento.

El grupo la decidió por votación: 6 a favor, 0 en contra.

#### Scenario: un resultado del día 1 pertenece a la temporada nueva
- GIVEN un resultado con fecha del día 1 de un mes
- WHEN se determina su temporada
- THEN es la de ese mes, no la del anterior

#### Scenario: la temporada sale de la fecha del puzzle
- GIVEN un resultado publicado con retraso
- WHEN se determina su temporada
- THEN es la del puzzle, no la del día en que se publicó

verified-by:
  - tests/slices/temporada-mensual/test_temporada_mensual.py

### Requirement: Una temporada son sus días laborables con muestra suficiente

Un día forma parte de una temporada si cumple **las dos** condiciones:

1. es de lunes a viernes;
2. lo jugaron al menos cinco personas.

Los dos filtros son independientes y hacen falta los dos: el primero excluye el fin de semana por regla; el
segundo, los laborables en que el grupo tampoco jugó (festivos, agosto). Sin el segundo, una ausencia
penalizaría en un día en que nadie estaba.

La definición de día laborable es **una sola en el proyecto** (`tools/calendario.py`), compartida con las
medallas: dos definiciones de lo mismo divergen, y aquí una divergencia cambia quién gana el mes.

#### Scenario: el fin de semana no forma parte de la temporada
- GIVEN una temporada con resultados en sábado y en domingo
- WHEN se determinan sus días
- THEN esos días no están

#### Scenario: un día de pocos jugadores no forma parte de la temporada
- GIVEN un día laborable jugado por menos de cinco personas
- WHEN se determinan los días de la temporada
- THEN ese día no está

#### Scenario: una temporada puede quedar vacía y sigue existiendo
- GIVEN un mes en el que ningún día alcanza la muestra mínima
- WHEN se lista el archivo de temporadas
- THEN la temporada aparece con cero días, en lugar de desaparecer

verified-by:
  - tests/slices/temporada-mensual/test_temporada_mensual.py

### Requirement: La temporada en curso se deriva de los datos, no del reloj

La temporada en curso es la más reciente con resultados; las anteriores están cerradas. El cálculo no
consulta la fecha del sistema, y por eso es reproducible con datos fijos (§10 del protocolo).

#### Scenario: la más reciente con datos está en curso
- GIVEN resultados que abarcan varios meses
- WHEN se listan las temporadas
- THEN la más reciente consta como en curso y las demás como cerradas

#### Scenario: dos cálculos sobre los mismos datos coinciden
- GIVEN un conjunto de resultados
- WHEN se calcula el modelo dos veces, y una de ellas con las filas en otro orden
- THEN el resultado es idéntico

verified-by:
  - tests/slices/temporada-mensual/test_temporada_mensual.py
