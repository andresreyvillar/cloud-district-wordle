/** Presentación F1 del evento: lectura del tablero cerrado y revelado manual; nunca escribe datos. */
import { escapar as escapeHtml } from '../ui/shell.js';
import { presentationMarkup } from './resultados-layout.js';

const round = value => Math.round(Number(value) * 100) / 100;
const format = value => Number(value).toLocaleString('es-ES', { maximumFractionDigits: 2 });

export function prepareResults(panel) {
  if (!panel.terminado) return null;
  const groups = (panel.grupos_f1 ?? []).map(team => team.grupo);
  const people = (panel.grupos_f1 ?? []).flatMap(team => (team.personas ?? []).map(person => ({
    name: person.nombre, group: team.grupo, rank: Number(person.puesto), points: Number(person.puntos),
  }))).filter(person => person.points > 0);
  const ranks = [...new Set(people.map(person => person.rank))].sort((left, right) => right - left);
  const awards = ranks.map(rank => ({ rank, people: people.filter(person => person.rank === rank) }));
  return { groups, awards, total: round(people.reduce((sum, person) => sum + person.points, 0)) };
}

export function buildStandings(results, step) {
  const revealed = results.awards.slice(0, step).flatMap(award => award.people);
  const teams = results.groups.map(name => {
    const people = revealed.filter(person => person.group === name);
    return { name, people, points: round(people.reduce((sum, person) => sum + person.points, 0)) };
  });
  teams.sort((left, right) => right.points - left.points || left.name.localeCompare(right.name, 'es'));
  return teams.map(team => ({ ...team, rank: 1 + teams.filter(other => other.points > team.points).length }));
}

export function createResultsController(api) {
  const state = { results: null, step: 0, loading: true, error: null };
  let busy = false;
  async function refresh() {
    if (state.results || busy) return;
    busy = true;
    try {
      state.results = prepareResults(await api.tablero());
      state.error = null;
    } catch {
      state.error = 'No se han podido leer los resultados. Puedes reintentarlo.';
    } finally {
      state.loading = false;
      busy = false;
    }
  }
  return { state, refresh,
    advance: () => { state.step = Math.min(state.results?.awards.length ?? 0, state.step + 1); },
    back: () => { state.step = Math.max(0, state.step - 1); },
    reset: () => { state.step = 0; },
  };
}

export function podiumAnimation(rank, reducedMotion) {
  if (reducedMotion || rank > 3 || rank < 1) return null;
  return { className: `podium-${rank}`, fireworks: rank === 1 };
}

function teamMarkup(team, latest, maximum, step) {
  const awarded = latest?.people.some(person => person.group === team.name);
  const people = team.people.map(person => `${escapeHtml(person.name)} +${format(person.points)}`).join(' · ');
  return `<li class="team ${awarded ? 'just-awarded' : ''}" data-team="${escapeHtml(team.name)}" style="--fill:${team.points / maximum * 100}%">
    <span class="rank">${step ? team.rank : '—'}</span><div><div class="team-title">${escapeHtml(team.name)}</div>${people ? `<div class="contributors">${people}</div>` : ''}</div><span class="points ${team.points ? '' : 'zero'}">${format(team.points)}</span></li>`;
}

function spotlightMarkup(latest, step, count) {
  if (!count) return '<h2 class="intro-title">No hay puntos F1 para repartir.</h2>';
  if (!latest) return '<p class="intro-number">10→1</p><h2 class="intro-title">Puntos F1<br>por equipos.</h2><p class="intro-caption">Revela cada premio del último puesto premiado al primero.</p>';
  const points = latest.people.map(person => person.points);
  const label = points.every(point => point === points[0]) ? `+${format(points[0])}` : points.map(point => `+${format(point)}`).join(' / ');
  const people = latest.people.map(person => `<div class="award-person"><h2 class="award-name">${escapeHtml(person.name)}</h2><p class="award-group">suma para <strong>${escapeHtml(person.group)}</strong></p></div>`).join('');
  return `<div class="award-entrance ${latest.people.length > 1 ? 'is-tied' : ''}"><p class="award-points">${label}</p><p class="award-unit">${latest.people.length > 1 ? 'PUNTOS POR PERSONA · PUESTO COMPARTIDO' : 'PUNTOS PARA EL EQUIPO'}</p><div class="award-people">${people}</div><p class="award-group"><small>${step === count ? 'EL REPARTO HA TERMINADO.' : 'PREMIO INDIVIDUAL.'}</small></p></div>`;
}

function nextLabel(results, step) {
  return step === results.awards.length ? 'Reparto completado ✓' : `Revelar el ${results.awards[step].rank}.º →`;
}

function standingsNote(results, standings, step) {
  if (!results.awards.length) return 'No se han obtenido puntos F1.';
  if (step !== results.awards.length) return 'Clasificación provisional. Los empates comparten puesto.';
  const leaders = standings.filter(team => team.rank === 1).map(team => escapeHtml(team.name));
  return `${leaders.length > 1 ? 'Empate en cabeza: ' : 'En cabeza: '}${leaders.join(' y ')} · ${format(standings[0].points)} puntos.`;
}

export function renderResults(state) {
  if (!state.results) {
    const message = state.error || (state.loading ? 'Cargando resultados…' : 'Los resultados se desvelan cuando termine el evento.');
    return `<section class="er er-wait"><h1>Resultados de wordle del barrio.</h1><p role="status">${escapeHtml(message)}</p>${state.error ? '<button data-er-action="retry">Reintentar</button>' : ''}</section>`;
  }
  const results = state.results;
  const step = state.step;
  const standings = buildStandings(results, step);
  const latest = results.awards[step - 1];
  const maximum = Math.max(1, ...standings.map(team => team.points));
  const total = round(standings.reduce((sum, team) => sum + team.points, 0));
  return presentationMarkup({ results, step, standings, latest, maximum, total }, { format, teamMarkup, spotlightMarkup, nextLabel, standingsNote });
}

function fireworkParticle(document, index) {
  const angle = index * 2.39996;
  const radius = 100 + (index % 19) * 13;
  const particle = document.createElement('span');
  particle.className = 'spark';
  const color = ['#d8f15c', '#f2b84b', '#ffffff', '#b0d73b'][index % 4];
  particle.style.cssText = `left:${[24, 76, 51][index % 3]}%;top:${[32, 27, 48][index % 3]}%;--dx:${Math.cos(angle) * radius}px;--dy:${Math.sin(angle) * radius}px;--delay:${(index % 3) * 0.5}s;--spark-color:${color}`;
  return particle;
}

function celebrateAward(container, award) {
  const effect = award && podiumAnimation(award.rank, container.ownerDocument.defaultView.matchMedia('(prefers-reduced-motion: reduce)').matches);
  if (!effect) return;
  container.querySelector('.award-points').classList.add(effect.className);
  if (!effect.fireworks) return;
  container.querySelector('.reveal').classList.add('champion-impact');
  container.querySelector('[data-er="celebration"]').replaceChildren(...Array.from({ length: 150 }, (_, index) => fireworkParticle(container.ownerDocument, index)));
}

function animateStandings(container, positions) {
  if (container.ownerDocument.defaultView.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  container.querySelectorAll('.team').forEach(row => {
    const previous = positions.get(row.dataset.team);
    const distance = previous === undefined ? 0 : previous - row.getBoundingClientRect().top;
    if (distance) row.animate([{ transform: `translateY(${distance}px)` }, { transform: 'translateY(0)' }], { duration: 550, easing: 'cubic-bezier(.2,.75,.3,1)' });
  });
}

export async function mountResults(container, control, timer) {
  const document = container.ownerDocument;
  function paint() {
    const action = document.activeElement?.dataset.erAction;
    const positions = new Map([...container.querySelectorAll('.team')].map(row => [row.dataset.team, row.getBoundingClientRect().top]));
    container.innerHTML = renderResults(control.state);
    animateStandings(container, positions);
    if (action) container.querySelector(`[data-er-action="${action}"]`)?.focus({ preventScroll: true });
  }
  function move(action) {
    if (!control.state.results) return;
    const previous = control.state.step;
    if (action === 'next') control.advance();
    if (action === 'previous') control.back();
    if (action === 'reset') control.reset();
    if (previous === control.state.step) return;
    paint();
    if (control.state.step > previous) celebrateAward(container, control.state.results.awards[control.state.step - 1]);
  }
  container.addEventListener('click', async event => {
    const action = event.target.closest('[data-er-action]')?.dataset.erAction;
    if (['next', 'previous', 'reset'].includes(action)) move(action);
    if (action === 'retry') { await control.refresh(); paint(); }
    if (action === 'fullscreen') {
      try {
        if (document.fullscreenElement) await document.exitFullscreen();
        else await document.documentElement.requestFullscreen();
      } catch { /* El navegador conserva la presentación cuando no permite pantalla completa. */ }
    }
  });
  document.addEventListener('keydown', event => {
    if (event.repeat || event.altKey || event.ctrlKey || event.metaKey || event.target.isContentEditable || event.target.closest('input, textarea, select')) return;
    if (event.key === ' ' && event.target.closest('button')) return;
    if (['ArrowRight', ' ', 'PageDown'].includes(event.key)) { event.preventDefault(); move('next'); }
    if (['ArrowLeft', 'PageUp'].includes(event.key)) { event.preventDefault(); move('previous'); }
  });
  document.title = 'Resultados de wordle del barrio';
  paint();
  await control.refresh(); paint();
  timer.cada(3000, async () => { if (!control.state.results) { await control.refresh(); paint(); } });
}
