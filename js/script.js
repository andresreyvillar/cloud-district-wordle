const SUPABASE_URL = 'https://oogturrjjcyrvzmiufff.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_h92oql1czQVyp30m49uxFA_23airRWH';

const PAGE_SIZE = 1000;
const MAX_ATTEMPTS = 6;
const FAIL_SCORE = 7;
const MIN_GAMES_FOR_BEST_AVG = 5;
const MIN_GAMES_FOR_BUBBLE = 3;
const MIN_BUBBLE_SIZE = 10;
const MAX_BUBBLE_DIAMETER = 40;
const RESIZE_DEBOUNCE_MS = 50;

const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

async function fetchAllResults() {
    const rows = [];
    for (let offset = 0; ; offset += PAGE_SIZE) {
        const { data, error } = await supabaseClient
            .from('wordle_results')
            .select('*')
            .order('wordle_id', { ascending: false })
            .range(offset, offset + PAGE_SIZE - 1);

        if (error) throw error;
        if (!data || data.length === 0) break;

        rows.push(...data);
        if (data.length < PAGE_SIZE) break;
    }
    return rows;
}

function mapRow(row) {
    return {
        playerName: row.player_name,
        wordleNumber: row.wordle_id,
        score: row.score,
        date: row.date
    };
}

document.addEventListener('DOMContentLoaded', async () => {
    bindTabButtons();
    try {
        const rows = await fetchAllResults();
        initDashboard(rows.map(mapRow));
    } catch (err) {
        console.error('Error cargando datos de Supabase:', err);
        document.querySelector('.container').innerHTML =
            '<h3 style="text-align:center; margin-top:50px">Error cargando datos. Revisa la consola.</h3>';
    }
});

function bindTabButtons() {
    document.querySelectorAll('.tab-btn[data-tab]').forEach(btn => {
        btn.addEventListener('click', () => openTab(btn.dataset.tab));
    });
}

function escapeHtml(value) {
    if (value === null || value === undefined) return '';
    return String(value).replace(/[&<>"']/g, ch => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }[ch]));
}

function openTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');

    const targetBtn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
    if (targetBtn) targetBtn.classList.add('active');

    // Plotly necesita un resize event para recalcular el ancho del contenedor recién visible
    setTimeout(() => window.dispatchEvent(new Event('resize')), RESIZE_DEBOUNCE_MS);
}

function computeUserStats(results, totalDays) {
    const players = [...new Set(results.map(r => r.playerName))].sort();

    return players.map(playerName => {
        const playerRows = results.filter(r => r.playerName === playerName);
        const scores = playerRows.map(r => r.score);
        const total = scores.length;
        const avg = (scores.reduce((a, b) => a + b, 0) / total).toFixed(2);
        const fails = scores.filter(s => s >= FAIL_SCORE).length;
        const successRate = (((total - fails) / total) * 100).toFixed(1);
        const participation = ((total / totalDays) * 100).toFixed(1);

        const distribution = {};
        for (let i = 1; i <= MAX_ATTEMPTS; i++) distribution[i] = 0;

        let maxCount = 0;
        scores.forEach(s => {
            if (s <= MAX_ATTEMPTS) {
                distribution[s] += 1;
                if (distribution[s] > maxCount) maxCount = distribution[s];
            }
        });

        return { playerName, total, avg, distribution, maxCount, successRate, participation };
    });
}

function initDashboard(results) {
    if (results.length === 0) {
        document.querySelector('.container').innerHTML =
            '<h3 style="text-align:center; margin-top:50px">No hay resultados todavía.</h3>';
        return;
    }

    const totalDays = new Set(results.map(r => r.wordleNumber)).size;
    const stats = computeUserStats(results, totalDays);
    const players = stats.map(s => s.playerName);

    renderSummary(stats);
    renderBubbleChart(stats);
    renderStatsTable(stats);
    renderEvolutionChart(results, players);
    renderDataTable(results);
}

function renderSummary(stats) {
    const container = document.getElementById('summary-container');
    if (stats.length === 0) {
        container.innerHTML = '';
        return;
    }

    const mostConsistent = [...stats].sort((a, b) => b.total - a.total)[0];
    const bestAvg = [...stats]
        .filter(s => s.total >= MIN_GAMES_FOR_BEST_AVG)
        .sort((a, b) => Number(a.avg) - Number(b.avg))[0];
    const totalResults = stats.reduce((acc, s) => acc + s.total, 0);

    container.innerHTML = `
        <div class="summary-cards">
            <div class="card">
                <h3>Más Constante</h3>
                <div class="value">${escapeHtml(mostConsistent.playerName)}</div>
                <div style="font-size: 12px; color: var(--gray)">${mostConsistent.total} partidas</div>
            </div>
            <div class="card">
                <h3>Mejor Media (min. ${MIN_GAMES_FOR_BEST_AVG})</h3>
                <div class="value">${bestAvg ? escapeHtml(bestAvg.playerName) : '-'}</div>
                <div style="font-size: 12px; color: var(--gray)">Media: ${bestAvg ? escapeHtml(bestAvg.avg) : '-'}</div>
            </div>
            <div class="card">
                <h3>Participación Grupal</h3>
                <div class="value">${totalResults}</div>
                <div style="font-size: 12px; color: var(--gray)">Resultados registrados</div>
            </div>
        </div>
    `;
}

function renderEvolutionChart(results, players) {
    const traces = players.map(playerName => {
        const entries = results
            .filter(r => r.playerName === playerName)
            .sort((a, b) => new Date(a.date) - new Date(b.date));
        return {
            x: entries.map(e => e.date),
            y: entries.map(e => e.score),
            name: playerName,
            mode: 'lines+markers',
            marker: { size: 6 },
            line: { width: 2 }
        };
    });

    const layout = {
        title: 'Evolución de Puntuaciones Diarias',
        xaxis: { type: 'date', gridcolor: '#eee' },
        yaxis: { title: 'Intentos', range: [0.5, 7.5], dtick: 1, gridcolor: '#eee' },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        hovermode: 'closest',
        font: { family: 'Open Sans' },
        margin: { t: 50, b: 50, l: 50, r: 20 }
    };

    Plotly.newPlot('plotly-graph', traces, layout, { responsive: true });
}

function renderBubbleChart(stats) {
    const filteredStats = stats.filter(s => s.total >= MIN_GAMES_FOR_BUBBLE);
    if (filteredStats.length === 0) {
        Plotly.purge('bubble-chart');
        return;
    }

    const successRates = filteredStats.map(s => Number(s.successRate));
    const maxSuccessRate = Math.max(...successRates);
    const sizeRef = 2.0 * maxSuccessRate / (MAX_BUBBLE_DIAMETER ** 2);

    const trace = {
        x: filteredStats.map(s => Number(s.avg)),
        y: filteredStats.map(s => s.total),
        text: filteredStats.map(s => s.playerName),
        mode: 'markers+text',
        textposition: 'top center',
        marker: {
            size: successRates.map(rate => Math.max(rate, MIN_BUBBLE_SIZE)),
            sizemode: 'area',
            sizeref: sizeRef,
            color: filteredStats.map(s => Number(s.avg)),
            colorscale: 'Viridis',
            reversescale: true,
            showscale: true,
            colorbar: {
                title: 'Media',
                orientation: 'h',
                y: -0.2,
                yanchor: 'top',
                thickness: 15
            }
        }
    };

    const layout = {
        title: `Habilidad (Media) vs. Participación (Mín. ${MIN_GAMES_FOR_BUBBLE} partidas)`,
        xaxis: { title: 'Media de Intentos (Menos es mejor)' },
        yaxis: { title: 'Partidas Jugadas (Más es mejor)' },
        hovermode: 'closest',
        font: { family: 'Open Sans' },
        margin: { t: 50, b: 100, l: 80, r: 20 }
    };

    Plotly.newPlot('bubble-chart', [trace], layout, { responsive: true });
}

function buildDistributionBars(stat) {
    let html = '<div class="dist-wrapper">';
    for (let i = 1; i <= MAX_ATTEMPTS; i++) {
        const count = stat.distribution[i];
        const pct = stat.maxCount > 0 ? (count / stat.maxCount) * 100 : 0;
        const height = pct > 0 ? pct : 2;
        const isMode = count === stat.maxCount && count > 0;
        html += `<div class="dist-bar ${isMode ? 'mode' : ''}" style="height: ${height}%;" data-count="${i}: ${count} veces"></div>`;
    }
    html += '</div>';
    return html;
}

function renderStatsTable(stats) {
    const statsBody = document.getElementById('statsBody');
    statsBody.innerHTML = '';

    const sortedStats = [...stats].sort((a, b) => Number(a.avg) - Number(b.avg));

    sortedStats.forEach(stat => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <div class="user-name">${escapeHtml(stat.playerName)}</div>
                <div class="participation-bar-container">
                    <div class="participation-bar-fill" style="width: ${stat.participation}%"></div>
                </div>
                <div style="font-size: 10px; color: var(--gray)">${stat.participation}% participación</div>
            </td>
            <td class="stat-number">${stat.total}</td>
            <td class="stat-number">${stat.avg}</td>
            <td>${buildDistributionBars(stat)}</td>
            <td>${stat.successRate}%</td>
        `;
        statsBody.appendChild(tr);
    });
}

function renderDataTable(results) {
    const dataBody = document.getElementById('dataBody');
    dataBody.innerHTML = '';
    const sortedData = [...results].sort((a, b) => new Date(b.date) - new Date(a.date));
    sortedData.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${escapeHtml(row.date)}</td><td>${escapeHtml(row.playerName)}</td><td>${escapeHtml(row.wordleNumber)}</td><td>${escapeHtml(row.score)}</td>`;
        dataBody.appendChild(tr);
    });
}
