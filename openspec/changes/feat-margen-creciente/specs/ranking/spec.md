# ranking — delta

## MODIFIED Requirements

### Requirement: El castigo por faltar crece con las ausencias

La nota que se imputa a un día no jugado lleva un margen que **crece con el número de ausencias** del jugador
en la temporada: la primera falta suma el margen base y cada siguiente un paso más, siempre con el tope del
fallo.

Un margen igual para cada falta seguía premiando no aparecer, porque el suelo de la propia media protege a
quien casi no juega: medido sobre un mes real, quien jugó 1 jornada de 21 quedaba por delante de quien jugó 18.

El paso se eligió midiendo: concentra el castigo en quien no aparece sin mover a quien falta poco por un
imprevisto, que es la mitad de la regla que no se puede romper.

#### Scenario: faltar mucho cuesta más que faltar poco
- **WHEN** dos jugadores faltan un número muy distinto de días
- **THEN** el coste por ausencia crece con las ausencias
- **AND** quien juega casi todos los días queda por delante de quien juega uno solo

#### Scenario: faltar un solo día apenas penaliza
- **WHEN** alguien falta una vez en el mes
- **THEN** el margen es el base, igual que antes del cambio
