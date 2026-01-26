document.addEventListener('DOMContentLoaded', () => {
    fetch('data/data.json')
        .then(response => response.json())
        .then(data => {
            initDashboard(data);
        })
        .catch(err => console.error('Error cargando datos:', err));
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
    
    if(tabId === 'graph') {
        setTimeout(() => { Plotly.Plots.resize('plotly-graph'); }, 50);
    }
}

function initDashboard(rawData) {
    const users = [...new Set(rawData.map(d => d.user))].sort();

    // 1. Renderizar Gráfico
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
        title: { text: 'Evolución de Puntuaciones', font: { family: 'Open Sans', size: 24, color: '#212121' } },
        xaxis: { title: 'Fecha', type: 'date', gridcolor: '#eee' },
        yaxis: { title: 'Intentos', range: [0.5, 6.5], dtick: 1, gridcolor: '#eee' },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        hovermode: 'closest',
        font: { family: 'Open Sans' },
        margin: { t: 50, b: 50, l: 50, r: 20 },
        legend: { orientation: 'v', x: 1.02, y: 1 }
    };
    
    Plotly.newPlot('plotly-graph', traces, layout, { responsive: true });

    // 2. Renderizar Estadísticas
    const statsBody = document.getElementById('statsBody');
    const userStats = users.map(user => {
        const scores = rawData.filter(d => d.user === user).map(d => d.score);
        const total = scores.length;
        const avg = (scores.reduce((a, b) => a + b, 0) / total).toFixed(2);
        const fails = scores.filter(s => s > 6).length;
        
        const dist = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0};
        let maxCount = 0;
        scores.forEach(s => {
            if(s <= 6) {
                dist[s] = (dist[s] || 0) + 1;
                if(dist[s] > maxCount) maxCount = dist[s];
            }
        });

        return { user, total, avg, fails, dist, maxCount };
    });

    userStats.forEach(stat => {
        let barsHtml = '<div class="dist-wrapper">';
        for(let i=1; i<=6; i++) {
            const count = stat.dist[i];
            const pct = stat.maxCount > 0 ? (count / stat.maxCount) * 100 : 0;
            const height = pct > 0 ? pct : 2;
            const isMode = (count === stat.maxCount && count > 0);
            const classMode = isMode ? 'mode' : '';
            barsHtml += `<div class="dist-bar ${classMode}" style="height: ${height}%;" data-count="${i}: ${count} veces"></div>`;
        }
        barsHtml += '</div>';

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td class="user-name">${stat.user}</td>
            <td class="stat-number">${stat.total}</td>
            <td class="stat-number">${stat.avg}</td>
            <td>${barsHtml}</td>
            <td>${stat.fails > 0 ? '<span style="color:var(--orange); font-weight:bold;">'+stat.fails+'</span>' : '0'}</td>
        `;
        statsBody.appendChild(tr);
    });

    // 3. Renderizar Datos Brutos
    const dataBody = document.getElementById('dataBody');
    const sortedData = [...rawData].sort((a, b) => new Date(b.date) - new Date(a.date));
    sortedData.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${row.date}</td><td>${row.user}</td><td>${row.num}</td><td>${row.score}</td>`;
        dataBody.appendChild(tr);
    });
}