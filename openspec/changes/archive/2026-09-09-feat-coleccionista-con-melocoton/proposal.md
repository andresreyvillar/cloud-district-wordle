# El Coleccionista cuenta el melocotón, sin quitárselo a nadie

## Por qué

Con el culo, la medalla se había quedado desfasada: su regla decía «las cuatro figuras en la misma temporada»
cuando ya hay cinco. El dueño pidió añadirlo.

## El problema que se midió antes de aplicarlo

Exigir las cinco a secas **le quita la medalla a 25 personas** que ya la tienen publicada:

```
              Coleccionista ahora   la mantendrían con las cinco
septiembre            3                    2
agosto                8                    0   ← todos la pierden
temporada 0          17                    0   ← todos la pierden
```

Porque el culo no existe antes del corte de reglas y en agosto no le salió a nadie. Sería castigar por una
regla que no existía cuando jugaron.

## La regla que lo arregla

El Coleccionista pide **una de cada categoría que haya salido en esa temporada**, derivado del reparto del
propio álbum:

```
temporada 0   vistas: abstracto, flores, geometrico, loro          → 17 la mantienen
agosto        vistas: abstracto, flores, geometrico, loro          →  8 la mantienen
septiembre    vistas: abstracto, culo, flores, geometrico, loro    →  2 (el melocotón ya cuenta)
```

Se ajusta solo, sin un corte más, y de paso **la medalla dice lo que su nombre promete**: has coleccionado
todo lo que se ha dibujado este mes. Una lista escrita a mano se queda desfasada cada vez que se añade una
categoría, que es exactamente lo que acababa de pasar.

## Detalle que parecía inofensivo

`all()` de un conjunto vacío es `True`. Si `vistas` llegara vacío, **cualquiera sería coleccionista**. De ahí
el respaldo a las cuatro de siempre y el test que lo fija.

## Qué no hace

- No toca las otras cuatro medallas de figura ni sus umbrales.
- No añade una medalla propia del melocotón: el dueño pidió solo esto.
