// Configuración de Supabase
// REEMPLAZA ESTOS VALORES CON LOS DE TU PROYECTO SUPABASE
const SUPABASE_URL = 'https://oogturrjjcyrvzmiufff.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_h92oql1czQVyp30m49uxFA_23airRWH';

const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Consulta a Supabase
        const { data, error } = await supabase
            .from('wordle_results')
            .select('*')
            .order('wordle_id', { ascending: false });

        if (error) throw error;

        // Mapear datos de DB (snake_case) a formato interno (camelCase/legacy)
        // DB: player_name, wordle_id, score, date
        // JS espera: user, num, score, date
        const mappedData = data.map(row => ({
            user: row.player_name,
            num: row.wordle_id.toString(), // El código original espera string a veces
            score: row.score,
            date: row.date
        }));

        initDashboard(mappedData);

    } catch (err) {
        console.error('Error cargando datos de Supabase:', err);
        // Fallback opcional o mensaje de error en UI
        document.querySelector('.container').innerHTML = '<h3 style="text-align:center; margin-top:50px">Error cargando datos. Revisa la consola.</h3>';
    }
});

function openTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    
    const btns = document.getElementsByClassName('tab-btn');
    for(let btn of btns) {
        if(btn.getAttribute('onclick').includes(tabId)) {
            btn.classList.add('active');
        }
    }
    
    // Redimensionar gráficos de Plotly para que ocupen todo el ancho
    setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
    }, 50);
}

function initDashboard(rawData) {
    const users = [...new Set(rawData.map(d => d.user))].sort();
    const totalDays = [...new Set(rawData.map(d => d.num))].length;

    // 1. Calcular estadísticas extendidas
    const userStats = users.map(user => {
        const userRows = rawData.filter(d => d.user === user);
        const scores = userRows.map(d => d.score);
        const total = scores.length;
        const avg = (scores.reduce((a, b) => a + b, 0) / total).toFixed(2);
        const fails = scores.filter(s => s >= 7).length;
        const successRate = (((total - fails) / total) * 100).toFixed(1);
        const participation = ((total / totalDays) * 100).toFixed(1);
        
        const dist = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0};
        let maxCount = 0;
        scores.forEach(s => {
            if(s <= 6) {
                dist[s] = (dist[s] || 0) + 1;
                if(dist[s] > maxCount) maxCount = dist[s];
            }
        });

        return { user, total, avg, fails, dist, maxCount, successRate, participation };
    });

    // Renderizar componentes en sus pestañas
    renderSummary(userStats);
    renderBubbleChart(userStats);
    renderStatsTable(userStats);
    renderEvolutionChart(rawData, users);
    renderDataTable(rawData);
}

function renderSummary(stats) {
    const mostConsistent = [...stats].sort((a, b) => b.total - a.total)[0];
    const bestAvg = [...stats].filter(s => s.total >= 5).sort((a, b) => a.avg - b.avg)[0];
    
    const container = document.getElementById('ranking');
    const summaryHtml = `
        <div class="summary-cards">
            <div class="card">
                <h3>Más Constante</h3>
                <div class="value">${mostConsistent.user}</div>
                <div style="font-size: 12px; color: var(--gray)">${mostConsistent.total} partidas</div>
            </div>
            <div class="card">
                <h3>Mejor Media (min. 5)</h3>
                <div class="value">${bestAvg ? bestAvg.user : '-'}</div>
                <div style="font-size: 12px; color: var(--gray)">Media: ${bestAvg ? bestAvg.avg : '-'}</div>
            </div>
            <div class="card">
                <h3>Participación Grupal</h3>
                <div class="value">${stats.reduce((a, b) => a + b.total, 0)}</div>
                <div style="font-size: 12px; color: var(--gray)">Resultados registrados</div>
            </div>
        </div>
    `;
    container.innerHTML = summaryHtml;
}

function renderEvolutionChart(rawData, users) {
    const traces = users.map(user => {
        const userEntries = rawData.filter(d => d.user === user).sort((a,b) => new Date(a.date) - new Date(b.date));
        return {
            x: userEntries.map(e => e.date),
            y: userEntries.map(e => e.score),
            name: user,
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
    const container = document.getElementById('ranking');
    const chartDiv = document.createElement('div');
    chartDiv.id = 'bubble-chart';
    chartDiv.className = 'chart-container';
    chartDiv.style.height = '500px';
    container.appendChild(chartDiv);

    // Filtrar usuarios con al menos 3 partidas
    const filteredStats = stats.filter(s => s.total >= 3);

    const trace = {
        x: filteredStats.map(s => s.avg),
        y: filteredStats.map(s => s.total),
        text: filteredStats.map(s => s.user),
        mode: 'markers+text',
        textposition: 'top center',
        marker: {
            size: filteredStats.map(s => Math.max(s.successRate, 10)),
            sizemode: 'area',
            sizeref: 2.0 * Math.max(...filteredStats.map(s => s.successRate)) / (40**2),
            color: filteredStats.map(s => s.avg),
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
        title: 'Habilidad (Media) vs. Participación (Mín. 3 partidas)',
        xaxis: { title: 'Media de Intentos (Menos es mejor)' },
        yaxis: { title: 'Partidas Jugadas (Más es mejor)' },
        hovermode: 'closest',
        font: { family: 'Open Sans' },
        margin: { t: 50, b: 100, l: 80, r: 20 }
    };

    Plotly.newPlot('bubble-chart', [trace], layout, { responsive: true });
}

function renderStatsTable(stats) {
    const statsBody = document.getElementById('statsBody');
    statsBody.innerHTML = '';
    
    // Ordenar por media por defecto
    const sortedStats = [...stats].sort((a, b) => a.avg - b.avg);

    sortedStats.forEach(stat => {
        let barsHtml = '<div class="dist-wrapper">';
        for(let i=1; i<=6; i++) {
            const count = stat.dist[i];
            const pct = stat.maxCount > 0 ? (count / stat.maxCount) * 100 : 0;
            const height = pct > 0 ? pct : 2;
            const isMode = (count === stat.maxCount && count > 0);
            barsHtml += `<div class="dist-bar ${isMode ? 'mode' : ''}" style="height: ${height}%;" data-count="${i}: ${count} veces"></div>`;
        }
        barsHtml += '</div>';

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <div class="user-name">${stat.user}</div>
                <div class="participation-bar-container">
                    <div class="participation-bar-fill" style="width: ${stat.participation}%"></div>
                </div>
                <div style="font-size: 10px; color: var(--gray)">${stat.participation}% participación</div>
            </td>
            <td class="stat-number">${stat.total}</td>
            <td class="stat-number">${stat.avg}</td>
            <td>${barsHtml}</td>
            <td>${stat.successRate}%</td>
        `;
        statsBody.appendChild(tr);
    });
}

function renderDataTable(rawData) {
    const dataBody = document.getElementById('dataBody');
    dataBody.innerHTML = '';
    const sortedData = [...rawData].sort((a, b) => new Date(b.date) - new Date(a.date));
    sortedData.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${row.date}</td><td>${row.user}</td><td>${row.num}</td><td>${row.score}</td>`;
        dataBody.appendChild(tr);
    });
}