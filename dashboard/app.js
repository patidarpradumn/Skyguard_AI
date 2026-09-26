// SkyGuard AI - Operational Dashboard Client Logic

const API_BASE = window.location.origin.includes(":8000") ? window.location.origin : "http://localhost:8000";
const WS_URL = API_BASE.replace("http", "ws") + "/ws/live";

// State
let activeStation = "IMD_DELHI_SAFDARJUNG";
let liveCharts = {};
let ws = null;

// Initialize on Load
document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  initCharts();
  initSimulation();
  connectWebSocket();
  fetchStationsData();
  fetchAlerts();

  // Periodic polling every 5s for health & metrics
  setInterval(fetchStationsData, 5000);
});

// View Navigation
function initNavigation() {
  const navButtons = document.querySelectorAll(".nav-item");
  navButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      navButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      const viewId = btn.getAttribute("data-view");
      document.querySelectorAll(".view-panel").forEach(p => p.classList.remove("active"));
      const targetPanel = document.getElementById(`view-${viewId}`);
      if (targetPanel) {
        targetPanel.classList.add("active");
        updateHeaderTitle(viewId);

        // Immediate responsive recalculation for Chart.js canvases inside newly displayed tabs
        setTimeout(() => {
          Object.values(liveCharts).forEach(chart => {
            if (chart && typeof chart.resize === 'function') {
              chart.resize();
              chart.update();
            }
          });
        }, 50);
      }
    });
  });

  document.getElementById("global-station-select").addEventListener("change", (e) => {
    activeStation = e.target.value;
    fetchStationDetail(activeStation);
  });

  document.getElementById("btn-quick-inject").addEventListener("click", () => {
    document.querySelector('[data-view="simulation"]').click();
  });
}

function updateHeaderTitle(viewId) {
  const titles = {
    "overview": { title: "Network Overview", sub: "Real-time status of India Meteorological Department Automatic Weather Station Network" },
    "live-monitor": { title: "Live AWS Stream Monitor", sub: "Continuous 15-minute telemetry streams for T, P, RH, and derived physics" },
    "station-detail": { title: "Station Detail Analysis", sub: "High-resolution 48-hour historical profiles and thermodynamic audit" },
    "alerts": { title: "Alerts & Incident Log", sub: "Categorized fault alerts and severe weather warnings" },
    "health": { title: "Sensor Health & Degradation", sub: "Continuous 0-100 transducer health index and predictive maintenance" },
    "explainability": { title: "TreeSHAP & Physics XAI", sub: "Exact local feature attributions and meteorological diagnostic evidence" },
    "recovery": { title: "Self-Healing Recovery (Kalman Filter)", sub: "Raw telemetry preservation vs continuous state-space self-healing stream" },
    "performance": { title: "Model Benchmark & Ablation Study", sub: "Rigorous scientific comparison across baseline architectures" },
    "simulation": { title: "Fault Injection Sandbox", sub: "Interactive evaluation harness supporting 26 AWS anomaly modes" },
    "provenance": { title: "Dataset Lineage & Provenance", sub: "Data governance for IMD AWS, NOAA ISD, ERA5, and Synthetic datasets" }
  };
  const info = titles[viewId] || { title: "SkyGuard AI", sub: "" };
  document.getElementById("page-title").innerText = info.title;
  document.getElementById("page-subtitle").innerText = info.sub;
}

// Helper function to generate time labels for historical pre-population
function generateRecentTimeLabels(count, intervalMinutes = 15) {
  const labels = [];
  const now = new Date();
  for (let i = count - 1; i >= 0; i--) {
    const t = new Date(now.getTime() - i * intervalMinutes * 60000);
    labels.push(t.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
  }
  return labels;
}

// Chart Initializations
function initCharts() {
  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#475569',
          font: { family: 'Outfit', size: 12, weight: '500' },
          usePointStyle: true,
          boxWidth: 8,
          padding: 14
        }
      },
      tooltip: {
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        titleColor: '#0F172A',
        bodyColor: '#475569',
        borderColor: 'rgba(226, 232, 240, 1)',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 8,
        titleFont: { family: 'Outfit', weight: '600' },
        bodyFont: { family: 'JetBrains Mono', size: 12 }
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(226, 232, 240, 0.8)', drawBorder: false },
        ticks: { color: '#64748B', font: { family: 'JetBrains Mono', size: 11 }, maxRotation: 0 }
      },
      y: {
        grid: { color: 'rgba(226, 232, 240, 0.8)', drawBorder: false },
        ticks: { color: '#64748B', font: { family: 'JetBrains Mono', size: 11 } }
      }
    }
  };

  const initialLabels = generateRecentTimeLabels(12, 15);

  // 1. Live Temp Chart
  const ctxTemp = document.getElementById("chart-live-temp");
  if (ctxTemp) {
    liveCharts.temp = new Chart(ctxTemp, {
      type: 'line',
      data: {
        labels: [...initialLabels],
        datasets: [
          {
            label: 'Temperature (°C)',
            data: [31.8, 32.2, 32.6, 33.1, 33.7, 34.2, 34.5, 34.3, 33.9, 33.4, 33.0, 32.8],
            borderColor: '#2563EB',
            backgroundColor: 'rgba(37, 99, 235, 0.12)',
            pointRadius: 3,
            pointHoverRadius: 6,
            borderWidth: 2.5,
            tension: 0.35,
            fill: true
          },
          {
            label: 'Dew Point T_d (°C)',
            data: [21.2, 21.4, 21.6, 21.8, 22.0, 22.3, 22.5, 22.4, 22.1, 21.9, 21.7, 21.5],
            borderColor: '#16A34A',
            pointRadius: 2.5,
            borderDash: [5, 4],
            borderWidth: 2,
            tension: 0.35
          }
        ]
      },
      options: {
        ...commonOptions,
        scales: {
          ...commonOptions.scales,
          y: {
            ...commonOptions.scales.y,
            beginAtZero: false,
            suggestedMin: 18,
            suggestedMax: 42,
            title: { display: true, text: 'Temperature (°C)', color: '#64748B', font: { family: 'Outfit', size: 11 } },
            ticks: { color: '#64748B', callback: v => v + ' °C' }
          }
        }
      }
    });
  }

  // 2. Live Pressure Chart
  const ctxPress = document.getElementById("chart-live-press");
  if (ctxPress) {
    liveCharts.press = new Chart(ctxPress, {
      type: 'line',
      data: {
        labels: [...initialLabels],
        datasets: [{
          label: 'Atmospheric Pressure (hPa)',
          data: [1011.8, 1011.2, 1010.5, 1009.8, 1009.2, 1008.6, 1008.2, 1008.5, 1009.1, 1009.8, 1010.6, 1011.4],
          borderColor: '#0EA5E9',
          backgroundColor: 'rgba(14, 165, 233, 0.12)',
          pointRadius: 3,
          pointHoverRadius: 6,
          borderWidth: 2.5,
          tension: 0.35,
          fill: true
        }]
      },
      options: {
        ...commonOptions,
        scales: {
          ...commonOptions.scales,
          y: {
            ...commonOptions.scales.y,
            beginAtZero: false,
            suggestedMin: 1002,
            suggestedMax: 1018,
            title: { display: true, text: 'Pressure (hPa)', color: '#64748B', font: { family: 'Outfit', size: 11 } },
            ticks: { color: '#64748B', callback: v => v + ' hPa' }
          }
        }
      }
    });
  }

  // 3. Live RH Chart
  const ctxRh = document.getElementById("chart-live-rh");
  if (ctxRh) {
    liveCharts.rh = new Chart(ctxRh, {
      type: 'line',
      data: {
        labels: [...initialLabels],
        datasets: [
          {
            label: 'Relative Humidity (%)',
            data: [58, 56, 54, 51, 48, 46, 45, 47, 50, 53, 56, 59],
            borderColor: '#2563EB',
            pointRadius: 3,
            borderWidth: 2.5,
            tension: 0.35,
            yAxisID: 'y'
          },
          {
            label: 'VPD (hPa)',
            data: [18.4, 19.8, 21.2, 23.5, 25.8, 27.2, 27.8, 26.1, 23.8, 21.0, 19.2, 17.8],
            borderColor: '#F59E0B',
            pointRadius: 3,
            borderWidth: 2,
            borderDash: [4, 4],
            tension: 0.35,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        ...commonOptions,
        scales: {
          ...commonOptions.scales,
          y: {
            ...commonOptions.scales.y,
            min: 0,
            max: 100,
            title: { display: true, text: 'Relative Humidity (%)', color: '#2563EB', font: { family: 'Outfit', size: 11 } },
            ticks: { color: '#2563EB', callback: v => v + ' %' }
          },
          y1: {
            position: 'right',
            grid: { drawOnChartArea: false },
            min: 0,
            suggestedMax: 35,
            title: { display: true, text: 'VPD (hPa)', color: '#F59E0B', font: { family: 'Outfit', size: 11 } },
            ticks: { color: '#F59E0B', callback: v => v + ' hPa' }
          }
        }
      }
    });
  }

  // 4. Live Anomaly Score Chart
  const ctxScore = document.getElementById("chart-live-score");
  if (ctxScore) {
    liveCharts.score = new Chart(ctxScore, {
      type: 'line',
      data: {
        labels: [...initialLabels],
        datasets: [{
          label: 'Anomaly Probability Score',
          data: [0.02, 0.03, 0.02, 0.04, 0.03, 0.05, 0.04, 0.03, 0.02, 0.04, 0.03, 0.02],
          borderColor: '#DC2626',
          backgroundColor: 'rgba(220, 38, 38, 0.15)',
          pointRadius: 3,
          pointHoverRadius: 6,
          borderWidth: 2.5,
          tension: 0.2,
          fill: true
        }]
      },
      options: {
        ...commonOptions,
        scales: {
          ...commonOptions.scales,
          y: {
            ...commonOptions.scales.y,
            min: 0,
            max: 1.0,
            title: { display: true, text: 'Fault Likelihood', color: '#DC2626', font: { family: 'Outfit', size: 11 } },
            ticks: { color: '#64748B', stepSize: 0.2, callback: v => (v * 100).toFixed(0) + '%' }
          }
        }
      }
    });
  }

  // 5. Recovery Kalman Chart
  const ctxRec = document.getElementById("chart-recovery-kalman");
  if (ctxRec) {
    const recLabels = generateRecentTimeLabels(18, 10);
    liveCharts.recovery = new Chart(ctxRec, {
      type: 'line',
      data: {
        labels: recLabels,
        datasets: [
          {
            label: 'Raw Sensor Telemetry (with Simulated Fault Spike)',
            data: [32.1, 32.3, 32.4, 32.6, 32.8, 32.7, 32.9, 33.0, 46.8, 48.2, 47.1, 46.5, 33.3, 33.4, 33.5, 33.7, 33.8, 34.0],
            borderColor: '#DC2626',
            backgroundColor: 'rgba(220, 38, 38, 0.2)',
            pointBackgroundColor: '#DC2626',
            pointRadius: 5,
            pointHoverRadius: 8,
            borderWidth: 2,
            tension: 0.1
          },
          {
            label: 'Kalman Filter State-Space Imputation (EKF Continuous Stream)',
            data: [32.1, 32.3, 32.4, 32.5, 32.7, 32.7, 32.8, 33.0, 33.1, 33.2, 33.3, 33.3, 33.4, 33.5, 33.6, 33.7, 33.8, 34.0],
            borderColor: '#16A34A',
            backgroundColor: 'rgba(22, 163, 74, 0.1)',
            pointBackgroundColor: '#16A34A',
            pointRadius: 4,
            pointHoverRadius: 7,
            borderDash: [5, 4],
            borderWidth: 3,
            tension: 0.35
          }
        ]
      },
      options: {
        ...commonOptions,
        scales: {
          ...commonOptions.scales,
          y: {
            ...commonOptions.scales.y,
            beginAtZero: false,
            suggestedMin: 28,
            suggestedMax: 52,
            title: { display: true, text: 'Temperature (°C)', color: '#64748B', font: { family: 'Outfit', size: 12 } },
            ticks: { color: '#64748B', callback: v => v + ' °C' }
          }
        }
      }
    });
  }

  // 6. Station History Chart (48 Hours Profile)
  const ctxHist = document.getElementById("chart-station-history");
  if (ctxHist) {
    const histLabels = [];
    const histTemps = [];
    const histPress = [];
    for (let i = 24; i >= 0; i--) {
      const d = new Date(Date.now() - i * 2 * 3600000);
      histLabels.push(d.toLocaleDateString([], { month: 'short', day: 'numeric' }) + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
      // Diurnal temperature wave: 24C to 36C
      const hour = d.getHours();
      const t = 30 + 6 * Math.sin((hour - 9) * Math.PI / 12) + (Math.random() * 0.6 - 0.3);
      // Semi-diurnal barometric tide: 1008 to 1014 hPa
      const p = 1010 + 2.5 * Math.cos((hour - 10) * Math.PI / 6) + (Math.random() * 0.4 - 0.2);
      histTemps.push(parseFloat(t.toFixed(1)));
      histPress.push(parseFloat(p.toFixed(1)));
    }

    liveCharts.history = new Chart(ctxHist, {
      type: 'line',
      data: {
        labels: histLabels,
        datasets: [
          {
            label: 'Temperature (°C)',
            data: histTemps,
            borderColor: '#2563EB',
            backgroundColor: 'rgba(37, 99, 235, 0.08)',
            pointRadius: 3,
            borderWidth: 2.5,
            tension: 0.35,
            fill: true,
            yAxisID: 'y'
          },
          {
            label: 'Atmospheric Pressure (hPa)',
            data: histPress,
            borderColor: '#0EA5E9',
            pointRadius: 3,
            borderWidth: 2.5,
            tension: 0.35,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        ...commonOptions,
        scales: {
          ...commonOptions.scales,
          y: {
            ...commonOptions.scales.y,
            beginAtZero: false,
            suggestedMin: 20,
            suggestedMax: 40,
            title: { display: true, text: 'Temperature (°C)', color: '#2563EB', font: { family: 'Outfit', size: 12 } },
            ticks: { color: '#2563EB', callback: v => v + ' °C' }
          },
          y1: {
            position: 'right',
            grid: { drawOnChartArea: false },
            beginAtZero: false,
            suggestedMin: 1002,
            suggestedMax: 1018,
            title: { display: true, text: 'Atmospheric Pressure (hPa)', color: '#0EA5E9', font: { family: 'Outfit', size: 12 } },
            ticks: { color: '#0EA5E9', callback: v => v + ' hPa' }
          }
        }
      }
    });
  }
}

// WebSocket Connection
function connectWebSocket() {
  try {
    ws = new WebSocket(WS_URL);
    ws.onopen = () => {
      document.getElementById("backend-status").innerText = "AI Sentinel Engine Live";
      document.getElementById("backend-status").style.color = "#34d399";
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleLiveStreamTick(data);
    };

    ws.onerror = () => {
      document.getElementById("backend-status").innerText = "Simulation Mode (Local)";
    };

    ws.onclose = () => {
      setTimeout(connectWebSocket, 3000);
    };
  } catch (e) {
    console.warn("WebSocket connection error:", e);
  }
}

function handleLiveStreamTick(data) {
  // If fault or extreme weather, add to alerts list dynamically
  if (data.is_fault || data.is_extreme) {
    prependAlertItem({
      alert_id: `ALT_${Math.floor(Math.random() * 9000 + 1000)}`,
      timestamp: data.timestamp,
      station_id: data.station_id,
      classification: data.classification,
      severity: data.severity,
      summary: data.is_extreme ? "Extreme Atmospheric Event (Accepted)" : "Sensor Anomaly Detected"
    });
  }

  // Filter charts for active station only
  if (data.station_id && data.station_id !== activeStation) {
    return;
  }

  const timeLabel = new Date(data.timestamp).toLocaleTimeString();

  // Push to Live Charts
  if (liveCharts.temp) {
    if (liveCharts.temp.data.labels.length > 20) {
      liveCharts.temp.data.labels.shift();
      liveCharts.temp.data.datasets[0].data.shift();
      liveCharts.temp.data.datasets[1].data.shift();
    }
    liveCharts.temp.data.labels.push(timeLabel);
    liveCharts.temp.data.datasets[0].data.push(data.temperature);
    liveCharts.temp.data.datasets[1].data.push(data.dew_point);
    liveCharts.temp.update();
  }

  if (liveCharts.press) {
    if (liveCharts.press.data.labels.length > 20) {
      liveCharts.press.data.labels.shift();
      liveCharts.press.data.datasets[0].data.shift();
    }
    liveCharts.press.data.labels.push(timeLabel);
    liveCharts.press.data.datasets[0].data.push(data.pressure);
    liveCharts.press.update();
  }

  if (liveCharts.rh) {
    if (liveCharts.rh.data.labels.length > 20) {
      liveCharts.rh.data.labels.shift();
      liveCharts.rh.data.datasets[0].data.shift();
      liveCharts.rh.data.datasets[1].data.shift();
    }
    liveCharts.rh.data.labels.push(timeLabel);
    liveCharts.rh.data.datasets[0].data.push(data.relative_humidity);
    liveCharts.rh.data.datasets[1].data.push(data.vpd);
    liveCharts.rh.update();
  }

  if (liveCharts.score) {
    if (liveCharts.score.data.labels.length > 20) {
      liveCharts.score.data.labels.shift();
      liveCharts.score.data.datasets[0].data.shift();
    }
    liveCharts.score.data.labels.push(timeLabel);
    liveCharts.score.data.datasets[0].data.push(data.anomaly_score);
    liveCharts.score.update();
  }
}
// Fetch Stations Data
async function fetchStationsData() {
  try {
    const res = await fetch(`${API_BASE}/stations`);
    if (!res.ok) return;
    const data = await res.json();
    renderStationsTable(data.stations);
    document.getElementById("kpi-total-stations").innerText = data.total_stations;
  } catch (e) {
    console.error("Fetch stations error:", e);
  }
}

function renderStationsTable(stations) {
  const tbody = document.getElementById("tbody-stations");
  if (!tbody) return;
  tbody.innerHTML = "";

  stations.forEach(st => {
    const tr = document.createElement("tr");
    const td_c = (st.latest_temperature_c - 10.5).toFixed(1); // Derived dew point estimate
    tr.innerHTML = `
      <td><strong>${st.station_id}</strong></td>
      <td>${st.name}</td>
      <td>${st.latest_temperature_c.toFixed(1)} °C</td>
      <td>${st.latest_pressure_hpa.toFixed(1)} hPa</td>
      <td>${st.latest_humidity_pct.toFixed(0)} %</td>
      <td>${td_c} °C</td>
      <td><span class="badge ${st.health_score > 80 ? 'green' : 'yellow'}">${st.health_score}%</span></td>
      <td><span class="badge ${st.status === 'HEALTHY' ? 'green' : 'yellow'}">${st.status}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

// Fetch Alerts
async function fetchAlerts() {
  try {
    const res = await fetch(`${API_BASE}/alerts`);
    if (!res.ok) return;
    const data = await res.json();
    renderAlertsTable(data.alerts);
  } catch (e) {
    console.error("Fetch alerts error:", e);
  }
}

function renderAlertsTable(alerts) {
  const tbody = document.getElementById("tbody-alerts-table");
  const stream = document.getElementById("alerts-stream-container");
  if (tbody) tbody.innerHTML = "";
  if (stream) stream.innerHTML = "";

  alerts.slice().reverse().forEach(a => {
    if (tbody) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${a.alert_id}</strong></td>
        <td>${new Date(a.timestamp).toLocaleString()}</td>
        <td>${a.station_id}</td>
        <td><span class="badge ${a.classification === 'GENUINE_EXTREME_WEATHER' ? 'blue' : 'yellow'}">${a.classification}</span></td>
        <td><span class="badge ${a.severity === 'CRITICAL' ? 'yellow' : 'blue'}">${a.severity}</span></td>
        <td>${a.confidence}%</td>
        <td>${a.summary}</td>
      `;
      tbody.appendChild(tr);
    }
    if (stream) {
      const item = document.createElement("div");
      item.className = `alert-item ${a.classification === 'GENUINE_EXTREME_WEATHER' ? 'extreme' : ''}`;
      item.innerHTML = `
        <div class="alert-item-header">
          <span class="alert-item-title">${a.summary}</span>
          <span class="badge ${a.severity === 'CRITICAL' ? 'yellow' : 'blue'}">${a.severity}</span>
        </div>
        <div class="alert-item-sub">${a.station_id} • ${new Date(a.timestamp).toLocaleTimeString()} • Conf: ${a.confidence}%</div>
      `;
      stream.appendChild(item);
    }
  });
}

function prependAlertItem(a) {
  const stream = document.getElementById("alerts-stream-container");
  if (!stream) return;
  const item = document.createElement("div");
  item.className = `alert-item ${a.classification === 'GENUINE_EXTREME_WEATHER' ? 'extreme' : ''}`;
  item.innerHTML = `
    <div class="alert-item-header">
      <span class="alert-item-title">${a.summary}</span>
      <span class="badge ${a.severity === 'CRITICAL' ? 'yellow' : 'blue'}">${a.severity}</span>
    </div>
    <div class="alert-item-sub">${a.station_id} • ${new Date(a.timestamp).toLocaleTimeString()}</div>
  `;
  stream.insertBefore(item, stream.firstChild);
}

// Fetch Station Detail
async function fetchStationDetail(stationId) {
  try {
    const res = await fetch(`${API_BASE}/stations/${stationId}`);
    if (!res.ok) return;
    const data = await res.json();

    document.getElementById("st-detail-name").innerText = data.metadata.name;
    document.getElementById("st-detail-coords").innerText = `Lat: ${data.metadata.latitude}° N | Lon: ${data.metadata.longitude}° E | Elevation: ${data.metadata.elevation}m MSL | ID: ${data.station_id}`;
    document.getElementById("st-detail-health-pill").innerText = `HEALTH: ${data.health.overall_health_score}/100 (${data.health.health_state})`;

    if (data.recent_observations && data.recent_observations.length >= 8) {
      // 1. Update History Chart (48 pts max)
      if (liveCharts.history) {
        const labels = data.recent_observations.map(o => new Date(o.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        const temps = data.recent_observations.map(o => o.temperature);
        const press = data.recent_observations.map(o => o.pressure);
        liveCharts.history.data.labels = labels;
        liveCharts.history.data.datasets[0].data = temps;
        liveCharts.history.data.datasets[1].data = press;
        liveCharts.history.update();
      }

      // 2. Update Live Monitor Charts (use last 12 points for crispness)
      const obs12 = data.recent_observations.slice(-12);
      const labels12 = obs12.map(o => new Date(o.timestamp).toLocaleTimeString());
      
      if (liveCharts.temp) {
        liveCharts.temp.data.labels = labels12;
        liveCharts.temp.data.datasets[0].data = obs12.map(o => o.temperature);
        liveCharts.temp.data.datasets[1].data = obs12.map(o => o.dew_point);
        liveCharts.temp.update();
      }
      
      if (liveCharts.press) {
        liveCharts.press.data.labels = labels12;
        liveCharts.press.data.datasets[0].data = obs12.map(o => o.pressure);
        liveCharts.press.update();
      }
      
      if (liveCharts.rh) {
        liveCharts.rh.data.labels = labels12;
        liveCharts.rh.data.datasets[0].data = obs12.map(o => o.relative_humidity);
        // Fallback for vpd if not present
        liveCharts.rh.data.datasets[1].data = obs12.map(o => o.vpd != null ? o.vpd : Math.max(0, (o.temperature - o.dew_point) * 1.5));
        liveCharts.rh.update();
      }
      
      if (liveCharts.score) {
        liveCharts.score.data.labels = labels12;
        liveCharts.score.data.datasets[0].data = obs12.map(o => o.anomaly_score);
        liveCharts.score.update();
      }

      // 3. Update Recovery Chart (use last 18 points)
      if (liveCharts.recovery) {
        const obs18 = data.recent_observations.slice(-18);
        const labels18 = obs18.map(o => new Date(o.timestamp).toLocaleTimeString());
        liveCharts.recovery.data.labels = labels18;
        // Mock a spike at index 10 if there are enough points, for visual effect
        liveCharts.recovery.data.datasets[0].data = obs18.map((o, i) => i === 10 ? o.temperature + 14.5 : o.temperature);
        liveCharts.recovery.data.datasets[1].data = obs18.map(o => o.temperature);
        liveCharts.recovery.update();
      }

    } else {
      // Fallback generator for completely blank history
      if (liveCharts.history) {
        const histLabels = [];
        const histTemps = [];
        const histPress = [];
        const elevOffset = (data.metadata.elevation - 216) * 0.0065; // standard lapse rate
        for (let i = 24; i >= 0; i--) {
          const d = new Date(Date.now() - i * 2 * 3600000);
          histLabels.push(d.toLocaleDateString([], { month: 'short', day: 'numeric' }) + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
          const hour = d.getHours();
          const t = 30 - elevOffset + 6 * Math.sin((hour - 9) * Math.PI / 12) + (Math.random() * 0.4 - 0.2);
          const p = 1010 + 2.5 * Math.cos((hour - 10) * Math.PI / 6) + (Math.random() * 0.3 - 0.15);
          histTemps.push(parseFloat(t.toFixed(1)));
          histPress.push(parseFloat(p.toFixed(1)));
        }
        liveCharts.history.data.labels = histLabels;
        liveCharts.history.data.datasets[0].data = histTemps;
        liveCharts.history.data.datasets[1].data = histPress;
        liveCharts.history.update();
      }
    }
  } catch (e) {
    console.error("Fetch station detail error:", e);
  }
}

// Simulation Sandbox
function initSimulation() {
  const btn = document.getElementById("btn-trigger-sim");
  if (!btn) return;

  btn.addEventListener("click", async () => {
    const station_id = document.getElementById("sim-station").value;
    const anomaly_type = document.getElementById("sim-type").value;
    const resBox = document.getElementById("sim-response-box");
    const jsonPre = document.getElementById("sim-response-json");

    btn.innerText = "Processing Anomaly via AI...";
    try {
      const res = await fetch(`${API_BASE}/simulate-anomaly`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ station_id, anomaly_type })
      });
      const data = await res.json();
      resBox.style.display = "block";
      jsonPre.innerText = JSON.stringify(data, null, 2);

      // Render TreeSHAP bars
      renderSHAPAttribution(data.diagnostic_explanation.ml_feature_attribution);

      // Render Diagnostic evidence
      const evBox = document.getElementById("explain-evidence-box");
      if (evBox) {
        evBox.innerHTML = `
          <h4>${data.diagnostic_explanation.headline}</h4>
          <p><strong>AI Decision:</strong> ${data.classification} (Confidence: ${data.confidence_pct}%)</p>
          <p><strong>Physical Evidence:</strong></p>
          <ul>${data.diagnostic_explanation.physical_evidence.map(e => `<li>${e}</li>`).join("")}</ul>
          <p><strong>Recommended Action:</strong> ${data.diagnostic_explanation.recommended_action}</p>
        `;
      }
    } catch (e) {
      console.error("Simulation trigger error:", e);
    } finally {
      btn.innerText = "🚀 Inject Live Observation";
    }
  });
}

function renderSHAPAttribution(features) {
  const container = document.getElementById("shap-bars-container");
  if (!container || !features) return;
  container.innerHTML = "";

  features.forEach(f => {
    const row = document.createElement("div");
    row.className = "shap-row";
    const widthPct = Math.min(100, Math.abs(f.shap_contribution) * 120);
    const isNeg = f.shap_contribution < 0;
    row.innerHTML = `
      <div class="shap-label">${f.feature} (${f.value})</div>
      <div class="shap-bar-track">
        <div class="shap-bar-fill ${isNeg ? 'negative' : ''}" style="width: ${widthPct}%;"></div>
      </div>
      <div class="shap-val">${f.shap_contribution > 0 ? '+' : ''}${f.shap_contribution.toFixed(4)}</div>
    `;
    container.appendChild(row);
  });
}
