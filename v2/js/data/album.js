/**
 * El álbum de figuras, proyectado desde la instantánea.
 *
 * Slice: `album-de-figuras` (openspec/slices/dashboard/album-de-figuras.md).
 *
 * Funciones **puras**: entra la instantánea y salen objetos. Ni reloj, ni DOM, ni red (§10 del protocolo).
 *
 * Aquí **no se clasifica nada ni se reordena nada**. El recuento por categoría, la tasa, el puesto y el
 * orden llegan calculados desde Python ([ADR 0008](../../../openspec/decisions/0008-donde-vive-el-calculo.md)):
 * el bot publica el álbum en el canal y la web lo pinta, así que tienen que salir del mismo cálculo por
 * construcción. Un clasificador reimplementado en JavaScript sería una segunda verdad.
 */

/**
 * La tira agrupada de un jugador: una entrada por categoría con partidas, en el orden del catálogo.
 *
 * **El orden lo manda el catálogo, no las claves del recuento.** JSONB no conserva el orden de las claves —
 * Postgres las devuelve por longitud y luego alfabéticamente— así que iterar el recuento pondría el ruido
 * (`abstracto`) en medio de las figuras que puntúan.
 *
 * Una categoría sin emoji se muestra por su nombre: inventar uno aquí sería exactamente el mapa duplicado
 * que el catálogo existe para evitar.
 */
export function tira(recuento, categorias) {
  return (categorias ?? [])
    .map(({ clave, emoji }) => ({
      categoria: clave,
      emoji: emoji ?? clave,
      partidas: recuento?.[clave] ?? 0,
    }))
    .filter((entrada) => entrada.partidas > 0);
}

/**
 * El álbum de una temporada, o `null` si esa instantánea no lo trae.
 *
 * `null` no es un caso raro: la web publicada lee lo que escribe el cron, y hasta que el pipeline nuevo
 * llegue a `main` ninguna instantánea tiene álbum. La vista tiene que funcionar sin él.
 */
export function albumDeTemporada(carga) {
  const album = carga?.album;
  if (!album) return null;

  const categorias = album.categorias ?? [];
  const jugadores = (album.jugadores ?? []).map((fila) => ({
    ...fila,
    tira: tira(fila.recuento, categorias),
  }));

  return {
    minimo: album.minimo ?? 0,
    clasificadas: album.clasificadas ?? 0,
    sin_patron: album.sin_patron ?? 0,
    categorias,
    jugadores,
    clasificados: jugadores.filter((fila) => fila.clasificado).length,
  };
}

/**
 * El álbum de un jugador dentro de una temporada.
 *
 * `existe: false` cuando ese jugador no tiene ninguna partida clasificada — no aparece en el álbum porque no
 * hay nada que clasificar. Es distinto de tener un 0%, que diría que dibujó mal.
 */
export function albumDeJugador(carga, jugador) {
  const album = albumDeTemporada(carga);
  if (!album) return null;

  const fila = album.jugadores.find((entrada) => entrada.jugador === jugador);
  if (!fila) {
    return { existe: false, jugador, minimo: album.minimo };
  }

  return {
    ...fila,
    existe: true,
    minimo: album.minimo,
    faltan: fila.clasificado ? 0 : Math.max(0, album.minimo - fila.partidas),
  };
}
