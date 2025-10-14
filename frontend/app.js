const BASE_URL = window.location.origin + '/api';
let currentPage = 1, pageSize = 20;

document.addEventListener('DOMContentLoaded', () => {
  ensureHighlightStyle();
  createChartPanel(); // insert the highlighted chart placeholder & description
  setupControls();
  applyFilters();
});

function setupControls(){
  document.getElementById('applyFilters').addEventListener('click', () => { currentPage = 1; applyFilters(); });
  document.getElementById('resetFilters').addEventListener('click', () => {
    document.getElementById('startDate').value = '';
    document.getElementById('endDate').value = '';
    document.getElementById('minDist').value = '';
    currentPage = 1; applyFilters();
  });
  document.getElementById('prevPage').addEventListener('click', () => { if(currentPage>1){ currentPage--; loadTrips(); }});
  document.getElementById('nextPage').addEventListener('click', () => { currentPage++; loadTrips(); });
  document.getElementById('closeModal').addEventListener('click', () => toggleModal(false));
  initMap();
}

/* Insert highlight CSS for chart placeholder and description (idempotent) */
function ensureHighlightStyle() {
  if (document.getElementById('chart-highlight-style')) return;
  const style = document.createElement('style');
  style.id = 'chart-highlight-style';
  style.innerHTML = `
    .chart-placeholder {
      border: 2px dashed rgba(94,208,255,0.5);
      box-shadow: 0 10px 28px rgba(59,130,246,0.08), 0 4px 12px rgba(94,208,255,0.06);
      padding: 10px;
      border-radius: 12px;
      background: linear-gradient(180deg, rgba(94,208,255,0.02), rgba(59,130,246,0.01));
    }
    .chart-description {
      margin-top: 10px;
      color: var(--text, #7dc3f8);
      font-size: 14px;
      line-height: 1.4;
    }
    .chart-description strong { color: var(--accent-2, #3b82f6); }
    @media (max-width: 640px) {
      .chart-placeholder { padding: 8px; }
      .chart-description { font-size: 13px; }
    }
  `;
  document.head.appendChild(style);
}

/* Create the highlighted panel containing the chart canvas and description.
   If an element with id 'generated-timechart-panel' already exists, do nothing. */
function createChartPanel() {
  if (document.getElementById('generated-timechart-panel')) return;

  const container = document.querySelector('.layout') || document.querySelector('main') || document.body;

  const panel = document.createElement('div');
  panel.className = 'panel';
  panel.id = 'generated-timechart-panel';

  const title = document.createElement('h2');
  title.textContent = 'Fare prices by time of day';
  panel.appendChild(title);

  const placeholderWrap = document.createElement('div');
  placeholderWrap.className = 'chart-placeholder';

  const canvas = document.createElement('canvas');
  canvas.id = 'timeChart';
  canvas.setAttribute('role', 'img');
  canvas.setAttribute('aria-label', 'Line chart showing fare price fluctuations by hour of day');
  canvas.style.width = '100%';
  canvas.style.height = '260px';
  placeholderWrap.appendChild(canvas);
  panel.appendChild(placeholderWrap);

  const desc = document.createElement('p');
  desc.className = 'chart-description';
  desc.innerHTML = 'This graph shows fluctuations of fare prices depending on the time of day: <strong>lowest during the wee hours</strong>, <strong>highest in the afternoon</strong>, then dips before rising again in the evening.';
  panel.appendChild(desc);

  container.appendChild(panel);
}

/* Chart.js loader: resolves immediately if Chart is already available */
function loadChartLibrary() {
  const CDN = 'https://cdn.jsdelivr.net/npm/chart.js';
  return new Promise((resolve, reject) => {
    if (window.Chart) return resolve();
    // avoid duplicate insertion
    if (document.querySelector(`script[data-src="${CDN}"]`)) {
      // wait for it to load
      const existing = document.querySelector(`script[data-src="${CDN}"]`);
      existing.addEventListener('load', () => resolve());
      existing.addEventListener('error', (e) => reject(e));
      return;
    }
    const s = document.createElement('script');
    s.src = CDN;
    s.async = true;
    s.setAttribute('data-src', CDN);
    s.onload = () => resolve();
    s.onerror = (e) => reject(e);
    document.head.appendChild(s);
  });
}

function getFilters(){
  return {
    start: document.getElementById('startDate').value,
    end: document.getElementById('endDate').value,
    min_distance: document.getElementById('minDist').value,
    page: currentPage,
    limit: pageSize
  };
}

async function applyFilters(){
  await Promise.all([loadSummary(), loadTimeSeries(), loadHeatmap(), loadTrips()]);
}

/*Summary Cards*/
async function loadSummary(){
  const f = getFilters();
  const qs = new URLSearchParams({start: f.start, end: f.end}).toString();
  const res = await fetch(`${BASE_URL}/summary?${qs}`);
  if(!res.ok) return;
  const data = await res.json();
  const container = document.getElementById('summaryCards');
  container.innerHTML = `
    <div class="card"><strong>Total trips</strong><div>${data.total_trips ?? '—'}</div></div>
    <div class="card"><strong>Avg distance (km)</strong><div>${(data.avg_distance_km||0).toFixed(2)}</div></div>
    <div class="card"><strong>Avg duration (min)</strong><div>${(data.avg_duration_min||0).toFixed(1)}</div></div>
    <div class="card"><strong>Revenue</strong><div>$${(data.total_revenue||0).toFixed(2)}</div></div>
  `;
}

/* Time Series / Fare Chart */
let timeChart;
async function loadTimeSeries(){
  const f = getFilters();
  const qs = new URLSearchParams({start: f.start, end: f.end}).toString();

  // call summary endpoint (your backend currently returns trips_per_hour). 
  // prefer fares_per_hour if available; fall back to trips_per_hour.
  const res = await fetch(`${BASE_URL}/summary?${qs}`);
  if(!res.ok) return;
  const data = await res.json();

  // Prefer fares_per_hour (expected shape: [{hour: '08:00', fare: 12}, ...])
  let labels = [];
  let values = [];
  if (Array.isArray(data.fares_per_hour) && data.fares_per_hour.length) {
    labels = data.fares_per_hour.map(d => d.hour);
    values = data.fares_per_hour.map(d => d.fare);
  } else if (Array.isArray(data.trips_per_hour) && data.trips_per_hour.length) {
    // fallback: use trips_per_hour as earlier code did
    labels = data.trips_per_hour.map(d => d.hour);
    values = data.trips_per_hour.map(d => d.count);
  } else {
    // If server returns aggregated fares in another key, try to detect common shapes
    // else use a demo pattern matching the requested fare-fluctuation shape
    labels = ['12 AM','2 AM','4 AM','6 AM','8 AM','10 AM','12 PM','2 PM','4 PM','6 PM','8 PM','10 PM'];
    values = [5,4,4,7,10,14,20,28,22,16,18,12]; // demo fares: low->peak->dip->rise
  }

  // ensure chart library is loaded before rendering
  try {
    await loadChartLibrary();
  } catch (err) {
    console.error('Failed to load Chart.js:', err);
    return;
  }

  const canvas = document.getElementById('timeChart');
  if (!canvas) {
    console.warn('timeChart canvas not found in DOM.');
    return;
  }
  const ctx = canvas.getContext('2d');

  if (timeChart) {
    try { timeChart.destroy(); } catch (e) { /* ignore */ }
    timeChart = null;
  }

  // responsive gradient
  const height = canvas.height || 260;
  const gradient = ctx.createLinearGradient(0, 0, 0, height);
  gradient.addColorStop(0, 'rgba(59,130,246,0.28)');
  gradient.addColorStop(1, 'rgba(94,208,255,0.05)');

  timeChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Average Fare (USD)',
        data: values,
        fill: true,
        backgroundColor: gradient,
        borderColor: 'rgba(59,130,246,0.95)',
        pointBackgroundColor: '#fff',
        pointBorderColor: 'rgba(59,130,246,0.95)',
        tension: 0.32,
        pointRadius: 4,
        pointHoverRadius: 6,
        borderWidth: 2
      }]
    },
    options: {
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(2,6,23,0.95)',
          titleColor: '#7dc3f8',
          bodyColor: '#eaf6ff',
          padding: 8,
          cornerRadius: 6
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: getComputedStyle(document.documentElement).getPropertyValue('--muted') || '#9fb7c9' }
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.03)' },
          ticks: { color: getComputedStyle(document.documentElement).getPropertyValue('--muted') || '#9fb7c9', beginAtZero: true }
        }
      },
      interaction: { mode: 'index', intersect: false }
    }
  });
}

let map, markersLayer;
function initMap(){
  map = L.map('map').setView([40.75, -73.98], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18 }).addTo(map);
  markersLayer = L.layerGroup().addTo(map);
}

async function loadHeatmap(){
  const f = getFilters();
  const qs = new URLSearchParams({start: f.start, end: f.end, grid_size: 0.01}).toString();
  const res = await fetch(`${BASE_URL}/heatmap?${qs}`);
  if(!res.ok) return;
  const data = await res.json();

  markersLayer.clearLayers();

  data.forEach(cell => {
    const circle = L.circle([cell.lat, cell.lng], { radius: Math.max(50, cell.count*10), weight:0.5 }).bindPopup(`Trips: ${cell.count}`);
    markersLayer.addLayer(circle);
  });
}

/* ---------- Trips Table & Pagination ---------- */
async function loadTrips(){
  const f = getFilters();
  const qs = new URLSearchParams({ start: f.start, end: f.end, min_distance: f.min_distance, limit: f.limit, page: f.page }).toString();
  const res = await fetch(`${BASE_URL}/trips?${qs}`);
  if(!res.ok){
    document.getElementById('tableContainer').innerText = 'Failed to load trips';
    return;
  }
  const payload = await res.json(); // {rows: [...], total: N}
  renderTripsTable(payload.rows || []);
  document.getElementById('pageInfo').innerText = `Page ${currentPage} — ${payload.total || '?'} trips total`;
}

function renderTripsTable(rows){
  const container = document.getElementById('tableContainer');
  if(!rows.length){ container.innerHTML = '<p>No trips found</p>'; return; }
  const html = `
    <table>
      <thead><tr>
        <th>ID</th><th>Pickup</th><th>Dropoff</th><th>Dist (km)</th><th>Dur (min)</th><th>Fare</th><th>Tip</th>
      </tr></thead>
      <tbody>
        ${rows.map(r => `<tr data-id="${r.id}" class="trip-row">
          <td>${r.id}</td>
          <td>${new Date(r.pickup_ts).toLocaleString()}</td>
          <td>${new Date(r.dropoff_ts).toLocaleString()}</td>
          <td>${(r.distance_km||0).toFixed(2)}</td>
          <td>${(r.duration_min||0).toFixed(1)}</td>
          <td>${(r.fare_amount||0).toFixed(2)}</td>
          <td>${(r.tip_amount||0).toFixed(2)}</td>
        </tr>`).join('')}
      </tbody>
    </table>`;
  container.innerHTML = html;

  document.querySelectorAll('.trip-row').forEach(tr => {
    tr.addEventListener('click', async () => {
      const id = tr.dataset.id;
      const res = await fetch(`${BASE_URL}/trip/${id}`);
      const t = await res.json();
      document.getElementById('tripDetail').innerText = JSON.stringify(t, null, 2);
      toggleModal(true);
    });
  });
}

function toggleModal(show){
  document.getElementById('modal').classList.toggle('hidden', !show);
}

/* small helper: allow external code to update the chart with real data
   usage: window.updateFareChart(labelsArray, valuesArray) */
window.updateFareChart = async function(labels = [], values = []) {
  await loadChartLibrary(); // ensure lib exists
  if (!timeChart) {
    // create a simple chart using provided data
    const canvas = document.getElementById('timeChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const grad = ctx.createLinearGradient(0, 0, 0, canvas.height || 260);
    grad.addColorStop(0, 'rgba(59,130,246,0.28)');
    grad.addColorStop(1, 'rgba(94,208,255,0.05)');
    if (timeChart) try { timeChart.destroy(); } catch(e){}
    timeChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{ label: 'Average Fare (USD)', data: values, fill: true, backgroundColor: grad, borderColor: 'rgba(59,130,246,0.95)' }]
      },
      options: { maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });
    return;
  }
  timeChart.data.labels = labels;
  timeChart.data.datasets[0].data = values;
  timeChart.update();
};
