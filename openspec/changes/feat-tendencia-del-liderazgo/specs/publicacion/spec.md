# publicacion — delta

## MODIFIED Requirements

### Requirement: El resumen diario cuenta cómo va la pelea por la cabeza del mes

El mensaje diario, además de anunciar el relevo de la jornada, sitúa ese relevo en el mes: cuántas veces ha
cambiado la cabeza y cómo se reparten las jornadas **los dos que se la juegan**. Cuando no hay relevo pero
alguien lleva varias jornadas seguidas sin soltarla, se dice eso en su lugar.

La tendencia **no tiene línea propia**: acompaña al relevo o no aparece. Una línea diaria de tendencia se
simuló sobre un mes real y salía casi todos los días, repitiéndose, y llegaba a atribuir el liderazgo a quien
ya no lideraba.

#### Scenario: la tendencia del mes acompaña al relevo
- **WHEN** el relevo se anuncia y la cabeza ya había cambiado antes ese mes
- **THEN** se añade cuántas veces ha cambiado y el reparto de jornadas de los dos que se la juegan
- **AND** con un solo cambio no se añade nada

#### Scenario: el dominio en cabeza se cuenta
- **WHEN** nadie le quita la cabeza al líder desde varias jornadas seguidas
- **THEN** se dice cuántas lleva, en el mismo hueco que el relevo
- **AND** no se dice de dos empatados, porque un empate no es dominio de nadie


### Requirement: La tensión del empate sube cuando el empate se repite

Cuando la misma pareja vuelve a compartir el primer puesto, la frase no se repite igual: sube de tono con las
veces que llevan y dice cuántas son.

La escalada va por **recurrencia y no por duración**, y eso lo decide la medida: los empates consecutivos casi
no existen —los cinco de agosto de 2026 duran una sola jornada, y de las doce rachas del histórico once duran
una y solo una llegó a tres—, mientras que la misma pareja llega a empatar cuatro veces en jornadas salteadas.

#### Scenario: la tensión sube cuando el empate se repite
- **WHEN** la misma pareja vuelve a empatar en cabeza en la temporada
- **THEN** la frase es neutra la primera vez, insistente a partir de la segunda y tensa a partir de la cuarta
- **AND** dice cuántas veces llevan empatados
