/** Plantilla de la presentación; solo interpola texto ya escapado o valores numéricos. */
export function presentationMarkup({ results, step, standings, latest, maximum, total }, helpers) {
  const { format, teamMarkup, spotlightMarkup, nextLabel, standingsNote } = helpers;
  return `<div class="er">
<div class="presentation">
  <header>
    <div class="edition"><span class="brand">W<span>·</span>B</span><span>EL BARRIO<br>SE JUEGA EN EQUIPO.</span></div>
    <div class="heading"><p class="eyebrow">EL MOMENTO DE SUMAR</p><h1>Resultados de<br>wordle del barrio<span>.</span></h1></div>
    <p class="source">RESULTADOS DEL EVENTO<br><strong>${results.groups.length} equipos · ${format(results.total)} puntos</strong></p>
  </header>
  <main>
    <section class="scoreboard" aria-labelledby="er-standings-heading">
      <div class="board-heading"><h2 id="er-standings-heading" data-er="standings-heading">Se suman al barrio los siguientes puntos:</h2><span>PUNTOS F1</span></div>
      <ol id="er-teams" data-er="teams" aria-label="Clasificación por equipos">${standings.map(team => teamMarkup(team, latest, maximum, step)).join('')}</ol>
      <p class="board-note" id="er-board-note" data-er="board-note">${standingsNote(results, standings, step)}</p>
    </section>
    <section class="reveal" aria-live="polite" aria-atomic="true">
      <div class="reveal-top"><span id="er-award-label" data-er="award-label">${latest ? `${latest.rank}.º PUESTO INDIVIDUAL` : "EL REPARTO"}</span><span id="er-award-counter" data-er="award-counter">${String(step).padStart(2, "0")} / ${results.awards.length}</span></div>
      <div id="er-spotlight" data-er="spotlight">${spotlightMarkup(latest, step, results.awards.length)}</div>
      <div class="reveal-bottom"><span>DE LA PERSONA AL EQUIPO.</span><span aria-hidden="true">↗</span></div>
    </section>
  </main>
  <footer>
    <div class="progress-area"><div class="progress-label"><span id="er-progress-label" data-er="progress-label">${format(total)} de ${format(results.total)} puntos repartidos</span><button id="er-reset" data-er-action="reset" class="text-button">Reiniciar</button></div><div class="track"><div id="er-progress" data-er="progress" style="width:${results.total ? total / results.total * 100 : 0}%"></div></div><p class="keyboard">ESPACIO / → para avanzar <span>·</span> ← para volver</p></div>
    <div class="actions"><button id="er-fullscreen" data-er-action="fullscreen" class="secondary" aria-label="Pantalla completa">Pantalla completa ↗</button><button id="er-previous" data-er-action="previous" class="secondary" ${step ? "" : "disabled"}>← Anterior</button><button id="er-next" data-er-action="next" class="primary" ${step === results.awards.length ? "disabled" : ""}>${nextLabel(results, step)}</button></div>
  </footer>
</div>

<div id="er-celebration" data-er="celebration" aria-hidden="true"></div>
</div>`;
}
