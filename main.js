/* ======================================================
    LIVE CHART CONFIG
====================================================== */
let liveChart;
const chartLabels = [];
const chartData = [];

function initChart() {
    const canvas = document.getElementById('liveChart');
    if (!canvas) return;
    liveChart = new Chart(canvas.getContext('2d'), {
        type: 'line',
        data: {
            labels: chartLabels,
            datasets: [{
                label: 'Soil Moisture %',
                data: chartData,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16,185,129,0.2)',
                fill: true,
                tension: 0.4
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: 0, max: 100 } } }
    });
}

/* ======================================================
    CORE LOGIC
====================================================== */

async function updateDashboard() {
    try {
        const res = await fetch('/api/sensor-data');
        const json = await res.json();
        if (!json.success) return;

        const d = json.data;

        // 1. Update Numerical Values
        const fields = {
            "temp": d.temperature_in_C?.toFixed(1),
            "hum": d.humidity?.toFixed(1),
            "soil": d.moisture?.toFixed(1),
            "ph": d.phValue?.toFixed(2),
            "n_val": d.N,
            "p_val": d.P,
            "k_val": d.K,
            "pred": d.predicted_moisture?.toFixed(1),
            "irrigation-decision": d.decision
        };

        for (const [id, val] of Object.entries(fields)) {
            const el = document.getElementById(id);
            if (el) el.innerText = val ?? "--";
        }

        // 2. Chart Update
        if (liveChart && d.moisture != null) {
            chartLabels.push(new Date().toLocaleTimeString());
            chartData.push(d.moisture);
            if (chartLabels.length > 15) { chartLabels.shift(); chartData.shift(); }
            liveChart.update('none');
        }

        // 3. UI Element Sync
        const pumpStatus = document.getElementById("pump-status");
        const modeLabel = document.getElementById("mode-label");
        const manualControls = document.getElementById("manual-controls");
        const motorBtn = document.getElementById("motor-btn");

        const isPumpOn = (d.motor === 1 || d.motor === "1");

        if (pumpStatus) {
            pumpStatus.innerText = isPumpOn ? "PUMP ON" : "PUMP OFF";
            pumpStatus.className = isPumpOn ? "status-badge on" : "status-badge off";
        }

        // Mode Logic
        if (d.control_mode === "auto") {
            if (modeLabel) { modeLabel.innerText = "AUTO"; modeLabel.className = "mode-badge auto"; }
            if (manualControls) manualControls.style.display = "none";
        } else {
            if (modeLabel) { modeLabel.innerText = "MANUAL"; modeLabel.className = "mode-badge manual"; }
            if (manualControls) manualControls.style.display = "block";
            if (motorBtn) motorBtn.innerText = isPumpOn ? "TURN PUMP OFF" : "TURN PUMP ON";
        }

    } catch (err) { console.error("Update Error:", err); }
}

async function setControlMode(mode) {
    console.log("SENDING MODE CHANGE:", mode);
    try {
        const res = await fetch('/api/control-mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: mode })
        });
        const data = await res.json();
        console.log("SERVER RESPONDED:", data);
        updateDashboard();
    } catch (err) { console.error("Error setting mode:", err); }
}

/* ======================================================
    EVENT LISTENERS
====================================================== */
window.onload = () => {
    initChart();
    updateDashboard();
    setInterval(updateDashboard, 3000);

    // Bind Auto Button
    const autoBtn = document.getElementById("auto-btn");
    if (autoBtn) autoBtn.onclick = () => setControlMode('auto');

    // Bind Manual Mode Button
    const manualModeBtn = document.getElementById("manual-mode-btn");
    if (manualModeBtn) manualModeBtn.onclick = () => setControlMode('manual');

    // Bind Motor Toggle Button
    const motorBtn = document.getElementById("motor-btn");
    if (motorBtn) {
        motorBtn.onclick = async () => {
            const modeLabel = document.getElementById("mode-label");
            
            // Critical Check: Server must be in manual mode
            if (modeLabel.innerText.trim().toUpperCase() !== "MANUAL") {
                alert("Please switch to MANUAL MODE first!");
                return;
            }

            const pumpStatus = document.getElementById("pump-status");
            const isCurrentlyOff = pumpStatus.innerText.includes("OFF");
            const targetState = isCurrentlyOff ? 1 : 0;

            console.log("SENDING MOTOR COMMAND:", targetState);

            const res = await fetch('/api/motor/control', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: targetState })
            });
            
            if (res.ok) {
                console.log("MOTOR COMMAND SUCCESSFUL");
                updateDashboard();
            } else {
                console.error("MOTOR COMMAND FAILED");
            }
        };
    }
};