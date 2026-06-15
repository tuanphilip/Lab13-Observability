DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Day 13 - Observability Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-color: #0b0b14;
            --card-bg: rgba(255, 255, 255, 0.03);
            --card-border: rgba(255, 255, 255, 0.07);
            --primary-glow: rgba(0, 242, 254, 0.15);
            --text-color: #f3f4f6;
            --text-muted: #9ca3af;
            --accent-cyan: #00f2fe;
            --accent-pink: #ff007f;
            --accent-emerald: #10b981;
            --accent-purple: #8b5cf6;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            background-image: radial-gradient(circle at top right, #1a1a2e, #0b0b14 70%);
            color: var(--text-color);
            min-height: 100vh;
            padding: 2rem;
            overflow-x: hidden;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 1.5rem;
        }

        h1 {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(to right, #00f2fe, #4facfe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .header-controls {
            display: flex;
            gap: 1rem;
            align-items: center;
        }

        .btn {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--card-border);
            color: var(--text-color);
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            cursor: pointer;
            font-family: inherit;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .btn:hover {
            background: var(--accent-cyan);
            color: #000;
            box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
            transform: translateY(-2px);
        }

        .btn-danger {
            background: rgba(239, 68, 68, 0.1);
            border-color: rgba(239, 68, 68, 0.3);
            color: #f87171;
        }

        .btn-danger:hover {
            background: #ef4444;
            color: #fff;
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
        }

        /* KPI Panel */
        .kpis-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }

        .kpi-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
            position: relative;
            overflow: hidden;
        }

        .kpi-card:hover {
            transform: translateY(-5px);
            border-color: rgba(0, 242, 254, 0.3);
            box-shadow: 0 10px 30px rgba(0, 242, 254, 0.05);
        }

        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
            opacity: 0;
            transition: opacity 0.3s;
        }

        .kpi-card:hover::before {
            opacity: 1;
        }

        .kpi-title {
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            color: var(--text-muted);
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }

        .kpi-value {
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        /* Layout Grid */
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .chart-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
            transition: border-color 0.3s;
        }

        .chart-card:hover {
            border-color: rgba(255, 255, 255, 0.15);
        }

        .chart-card.col-6 {
            grid-column: span 6;
        }

        .chart-card.col-4 {
            grid-column: span 4;
        }

        .chart-card.col-8 {
            grid-column: span 8;
        }

        @media (max-width: 1024px) {
            .chart-card.col-6, .chart-card.col-4, .chart-card.col-8 {
                grid-column: span 12;
            }
        }

        .chart-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chart-badge {
            font-size: 0.75rem;
            background: rgba(255, 255, 255, 0.08);
            padding: 0.25rem 0.5rem;
            border-radius: 6px;
            font-weight: 400;
            color: var(--text-muted);
        }

        .chart-container {
            position: relative;
            height: 250px;
            width: 100%;
        }

        /* Incident Controller */
        .incident-card {
            background: rgba(239, 68, 68, 0.03);
            border: 1px solid rgba(239, 68, 68, 0.15);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }

        .incident-card h3 {
            font-size: 1.2rem;
            font-weight: 600;
            color: #f87171;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .incident-controls {
            display: flex;
            gap: 1.5rem;
            flex-wrap: wrap;
        }

        .incident-switch {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            background: rgba(0, 0, 0, 0.2);
            padding: 0.75rem 1.2rem;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            cursor: pointer;
            user-select: none;
            transition: all 0.3s ease;
        }

        .incident-switch:hover {
            border-color: rgba(239, 68, 68, 0.3);
        }

        .incident-switch.active {
            background: rgba(239, 68, 68, 0.15);
            border-color: rgba(239, 68, 68, 0.5);
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.1);
        }

        .switch-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #4b5563;
            transition: background 0.3s, transform 0.3s;
        }

        .incident-switch.active .switch-dot {
            background: #ef4444;
            box-shadow: 0 0 8px #ef4444;
            transform: scale(1.2);
        }

        .switch-label {
            font-size: 0.95rem;
            font-weight: 600;
        }

        .switch-desc {
            font-size: 0.8rem;
            color: var(--text-muted);
            font-weight: 400;
        }

        footer {
            text-align: center;
            padding: 2rem 0;
            color: var(--text-muted);
            font-size: 0.9rem;
            border-top: 1px solid var(--card-border);
            margin-top: 2rem;
        }
    </style>
</head>
<body>

    <header>
        <div>
            <h1>📊 Day 13 Observability Dashboard</h1>
            <p style="color: var(--text-muted); margin-top: 0.25rem;">Live metrics visualization, SLO monitoring, and incident injection control.</p>
        </div>
        <div class="header-controls">
            <button class="btn" onclick="fetchData()">🔄 Refresh Data</button>
            <button class="btn btn-danger" onclick="triggerLoadTest()">⚡ Run Load Test</button>
        </div>
    </header>

    <!-- Incident Control Panel -->
    <div class="incident-card">
        <h3>🚨 Live Incident Injection Control</h3>
        <div class="incident-controls">
            <div class="incident-switch" id="switch-rag_slow" onclick="toggleIncident('rag_slow')">
                <div class="switch-dot"></div>
                <div>
                    <div class="switch-label">RAG Slowdown</div>
                    <div class="switch-desc">Injects 2.5s delay to mock_rag retrieve</div>
                </div>
            </div>
            <div class="incident-switch" id="switch-tool_fail" onclick="toggleIncident('tool_fail')">
                <div class="switch-dot"></div>
                <div>
                    <div class="switch-label">Vector Store Timeout</div>
                    <div class="switch-desc">Fails retrieval with RuntimeError</div>
                </div>
            </div>
            <div class="incident-switch" id="switch-cost_spike" onclick="toggleIncident('cost_spike')">
                <div class="switch-dot"></div>
                <div>
                    <div class="switch-label">LLM Token Inflation</div>
                    <div class="switch-desc">Multiplies output tokens by 4x</div>
                </div>
            </div>
        </div>
    </div>

    <!-- KPIs Header -->
    <div class="kpis-grid">
        <div class="kpi-card">
            <div class="kpi-title">Total Traffic</div>
            <div class="kpi-value" id="kpi-traffic">0</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">P95 Latency</div>
            <div class="kpi-value" id="kpi-latency" style="color: var(--accent-cyan);">0ms</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Error Rate</div>
            <div class="kpi-value" id="kpi-error-rate" style="color: var(--accent-pink);">0%</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Quality Avg</div>
            <div class="kpi-value" id="kpi-quality" style="color: var(--accent-emerald);">0.00</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Total Cost</div>
            <div class="kpi-value" id="kpi-cost" style="color: var(--accent-purple);">$0.00</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Langfuse Traces</div>
            <div class="kpi-value" id="kpi-langfuse-traces" style="color: var(--accent-cyan);">0</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">LF Cost (USD)</div>
            <div class="kpi-value" id="kpi-langfuse-cost" style="color: var(--accent-purple);">$0.00</div>
        </div>
    </div>

    <!-- Charts Grid -->
    <div class="dashboard-grid">
        <!-- Latency Chart -->
        <div class="chart-card col-6">
            <div class="chart-title">
                <span>Latency Over Time</span>
                <span class="chart-badge">SLO Target &lt; 3000ms</span>
            </div>
            <div class="chart-container">
                <canvas id="latencyChart"></canvas>
            </div>
        </div>

        <!-- Traffic & Error Rate Chart -->
        <div class="chart-card col-6">
            <div class="chart-title">
                <span>Traffic & Error Rate</span>
                <span class="chart-badge">SLO Target &lt; 2% Errors</span>
            </div>
            <div class="chart-container">
                <canvas id="trafficChart"></canvas>
            </div>
        </div>

        <!-- Cumulative Cost Chart -->
        <div class="chart-card col-4">
            <div class="chart-title">
                <span>Cumulative Cost (USD)</span>
                <span class="chart-badge">Budget &lt; $2.50</span>
            </div>
            <div class="chart-container">
                <canvas id="costChart"></canvas>
            </div>
        </div>

        <!-- Token Usage Chart -->
        <div class="chart-card col-4">
            <div class="chart-title">
                <span>Token Usage (Tokens)</span>
                <span class="chart-badge">Total Tokens In/Out</span>
            </div>
            <div class="chart-container">
                <canvas id="tokenChart"></canvas>
            </div>
        </div>

        <!-- Heuristic Quality Score Chart -->
        <div class="chart-card col-4">
            <div class="chart-title">
                <span>Quality Score Moving Avg</span>
                <span class="chart-badge">Target &gt; 0.75</span>
            </div>
            <div class="chart-container">
                <canvas id="qualityChart"></canvas>
            </div>
        </div>
    </div>

    <!-- Langfuse Traces Table -->
    <div class="chart-card" style="grid-column: span 12; margin-bottom: 2rem;">
        <div class="chart-title">
            <span>🔍 Langfuse Traces (Real-Time)</span>
            <span class="chart-badge" id="langfuse-status">Disconnected</span>
        </div>
        <div style="overflow-x: auto; max-height: 400px; overflow-y: auto;">
            <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
                <thead>
                    <tr style="border-bottom: 1px solid var(--card-border); color: var(--text-muted); text-align: left;">
                        <th style="padding: 0.5rem;">Trace ID</th>
                        <th style="padding: 0.5rem;">Name</th>
                        <th style="padding: 0.5rem;">Timestamp</th>
                        <th style="padding: 0.5rem;">Latency (s)</th>
                        <th style="padding: 0.5rem;">Cost ($)</th>
                        <th style="padding: 0.5rem;">Session</th>
                        <th style="padding: 0.5rem;">Tags</th>
                    </tr>
                </thead>
                <tbody id="langfuse-tbody">
                    <tr><td colspan="7" style="padding: 1rem; text-align: center; color: var(--text-muted);">Loading Langfuse traces...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <footer>
        <p>Day 13 Observability Lab • Pair Programmed with Antigravity</p>
    </footer>

    <script>
        let charts = {};

        // Auto refresh
        setInterval(fetchData, 15000);

        // Run load test trigger
        async function triggerLoadTest() {
            try {
                alert("Triggering requests generator in background...");
                fetch("/run-load-test-api", { method: "POST" });
                setTimeout(fetchData, 1500);
            } catch (e) {
                console.error(e);
            }
        }

        async function toggleIncident(name) {
            const el = document.getElementById(`switch-${name}`);
            const isActive = el.classList.contains("active");
            const action = isActive ? "disable" : "enable";
            
            try {
                const response = await fetch(`/incidents/${name}/${action}`, { method: "POST" });
                const data = await response.json();
                updateIncidentUI(data.incidents);
                fetchData();
            } catch (e) {
                console.error("Error toggling incident:", e);
            }
        }

        function updateIncidentUI(incidents) {
            for (const [name, active] of Object.entries(incidents)) {
                const el = document.getElementById(`switch-${name}`);
                if (el) {
                    if (active) {
                        el.classList.add("active");
                    } else {
                        el.classList.remove("active");
                    }
                }
            }
        }

        async function fetchData() {
            try {
                const response = await fetch("/api/dashboard-data");
                const data = await response.json();
                
                // Update KPIs
                document.getElementById("kpi-traffic").innerText = data.metrics.traffic || 0;
                document.getElementById("kpi-latency").innerText = `${data.metrics.latency_p95 || 0}ms`;
                
                const totalRequests = data.metrics.traffic || 0;
                const totalErrors = Object.values(data.metrics.error_breakdown || {}).reduce((a, b) => a + b, 0);
                const errorPct = totalRequests > 0 ? ((totalErrors / totalRequests) * 100).toFixed(1) : "0.0";
                document.getElementById("kpi-error-rate").innerText = `${errorPct}%`;
                
                document.getElementById("kpi-quality").innerText = (data.metrics.quality_avg || 0).toFixed(2);
                document.getElementById("kpi-cost").innerText = `$${(data.metrics.total_cost_usd || 0).toFixed(4)}`;
                
                // Langfuse KPIs
                const lf = data.langfuse || {};
                document.getElementById("kpi-langfuse-traces").innerText = lf.trace_count || 0;
                document.getElementById("kpi-langfuse-cost").innerText = `$${(lf.total_cost || 0).toFixed(4)}`;
                
                const statusBadge = document.getElementById("langfuse-status");
                if (lf.connected) {
                    statusBadge.innerText = `Connected (${lf.trace_count} traces)`;
                    statusBadge.style.color = "#10b981";
                } else {
                    statusBadge.innerText = "Disconnected";
                    statusBadge.style.color = "#ef4444";
                }
                
                // Render Langfuse traces table
                renderLangfuseTraces(lf.traces || []);
                
                // Get incident statuses
                const healthResponse = await fetch("/health");
                const healthData = await healthResponse.json();
                updateIncidentUI(healthData.incidents);

                renderCharts(data.series);
            } catch (e) {
                console.error("Error fetching dashboard data:", e);
            }
        }

        function renderCharts(series) {
            const labels = series.map((_, idx) => `Req ${idx + 1}`);
            
            // 1. Latency Chart
            const latencies = series.map(s => s.latency || 0);
            const latencySLO = series.map(() => 3000);
            updateLineChart("latencyChart", labels, [
                { label: "Request Latency (ms)", data: latencies, color: "#00f2fe", fill: true },
                { label: "SLO Limit (3000ms)", data: latencySLO, color: "#ef4444", borderDash: [5, 5] }
            ]);

            // 2. Traffic and Error Rate
            const errorRates = series.map(s => s.error_rate || 0);
            const errorSLO = series.map(() => 2);
            updateLineChart("trafficChart", labels, [
                { label: "Error Rate (%)", data: errorRates, color: "#ff007f", fill: true },
                { label: "SLO Limit (2%)", data: errorSLO, color: "#ef4444", borderDash: [5, 5] }
            ]);

            // 3. Cost Chart
            const costs = series.map(s => s.cumulative_cost || 0);
            const costSLO = series.map(() => 2.5);
            updateLineChart("costChart", labels, [
                { label: "Cumulative Cost ($)", data: costs, color: "#8b5cf6", fill: true },
                { label: "Budget Limit ($2.50)", data: costSLO, color: "#ef4444", borderDash: [5, 5] }
            ]);

            // 4. Token Chart
            const tokensIn = series.map(s => s.cumulative_tokens_in || 0);
            const tokensOut = series.map(s => s.cumulative_tokens_out || 0);
            updateLineChart("tokenChart", labels, [
                { label: "Tokens In", data: tokensIn, color: "#3b82f6" },
                { label: "Tokens Out", data: tokensOut, color: "#10b981" }
            ]);

            // 5. Quality Chart
            const qualities = series.map(s => s.quality || 0);
            const qualityTarget = series.map(() => 0.75);
            updateLineChart("qualityChart", labels, [
                { label: "Quality Score", data: qualities, color: "#10b981", fill: true },
                { label: "SLO Target (0.75)", data: qualityTarget, color: "#eab308", borderDash: [5, 5] }
            ]);
        }

        function updateLineChart(canvasId, labels, dataSets) {
            if (charts[canvasId]) {
                charts[canvasId].data.labels = labels;
                charts[canvasId].data.datasets = dataSets.map((ds, idx) => {
                    const existing = charts[canvasId].data.datasets[idx];
                    return {
                        ...existing,
                        data: ds.data,
                        label: ds.label
                    };
                });
                charts[canvasId].update();
                return;
            }

            const ctx = document.getElementById(canvasId).getContext("2d");
            
            const datasetsConfig = dataSets.map(ds => {
                let fillConfig = false;
                if (ds.fill) {
                    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
                    gradient.addColorStop(0, `${ds.color}33`);
                    gradient.addColorStop(1, `${ds.color}00`);
                    fillConfig = { target: 'origin', above: gradient };
                }

                return {
                    label: ds.label,
                    data: ds.data,
                    borderColor: ds.color,
                    borderWidth: 2,
                    borderDash: ds.borderDash || [],
                    pointRadius: ds.borderDash ? 0 : 2,
                    pointHoverRadius: 5,
                    fill: fillConfig,
                    tension: 0.3
                };
            });

            charts[canvasId] = new Chart(ctx, {
                type: "line",
                data: { labels, datasets: datasetsConfig },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: "#9ca3af", font: { family: "Outfit" } }
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: "rgba(255, 255, 255, 0.03)" },
                            ticks: { color: "#6b7280", font: { family: "Outfit", size: 9 } }
                        },
                        y: {
                            grid: { color: "rgba(255, 255, 255, 0.03)" },
                            ticks: { color: "#6b7280", font: { family: "Outfit" } }
                        }
                    }
                }
            });
        }

        function renderLangfuseTraces(traces) {
            const tbody = document.getElementById("langfuse-tbody");
            if (!traces.length) {
                tbody.innerHTML = '<tr><td colspan="7" style="padding: 1rem; text-align: center; color: var(--text-muted);">No Langfuse traces yet. Send requests to /chat to generate traces.</td></tr>';
                return;
            }
            tbody.innerHTML = traces.map(t => {
                const ts = t.timestamp ? new Date(t.timestamp).toLocaleString() : "-";
                const latency = t.latency != null ? t.latency.toFixed(2) : "-";
                const cost = t.total_cost != null ? t.total_cost.toFixed(6) : "-";
                const traceId = (t.id || "").substring(0, 12) + "...";
                const sessionId = (t.session_id || "-").substring(0, 10);
                const tags = (t.tags || []).join(", ") || "-";
                return `<tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 0.5rem; font-family: monospace; color: var(--accent-cyan);">${traceId}</td>
                    <td style="padding: 0.5rem;">${t.name || "-"}</td>
                    <td style="padding: 0.5rem;">${ts}</td>
                    <td style="padding: 0.5rem;">${latency}s</td>
                    <td style="padding: 0.5rem;">$${cost}</td>
                    <td style="padding: 0.5rem; font-family: monospace;">${sessionId}</td>
                    <td style="padding: 0.5rem;">${tags}</td>
                </tr>`;
            }).join("");
        }

        // Initial load
        fetchData();
    </script>
</body>
</html>
"""
