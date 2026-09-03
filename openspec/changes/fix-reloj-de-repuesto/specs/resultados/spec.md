# resultados — delta

## MODIFIED Requirements

### Requirement: La frescura de los resultados no puede depender de un servicio que no la garantiza

Los resultados que la web enseña son tan recientes como la última sincronización, y esa sincronización se
apoya en un reloj externo al sistema. Cuando ese reloj no garantiza nada, **la frescura de los datos tampoco
está garantizada**, aunque el código sea correcto.

Es lo que ocurrió: el pipeline funcionaba y la web mostraba datos de hasta seis horas antes, porque las
ejecuciones simplemente no se lanzaban. Ningún test podía cazarlo — no había nada roto que probar.

De ahí dos exigencias sobre la ingesta: que se despierte desde **más de un reloj**, de modo que la
indisponibilidad de uno no detenga los datos; y que **un fallo transitorio no consuma la ventana**, porque
cuando las ventanas son escasas perder una por un timeout de un segundo cuesta horas de retraso.

#### Scenario: los datos siguen llegando aunque un reloj falle
- **WHEN** el planificador que dispara la ingesta descarta su ventana
- **THEN** otro reloj la dispara, y los resultados se sincronizan igual dentro de la hora
