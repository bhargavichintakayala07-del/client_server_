// ==========================================
// 🚀 NETFLOW-AI LIVE DASHBOARD CONTROL ENGINE
// ==========================================

document.addEventListener("DOMContentLoaded", function () {
    console.log("⚡ NetFlow-AI Dashboard Engine Loaded!");
    
    // Initial fetch
    fetchLiveStats();

    // Auto-refresh Dashboard Stats & Logs every 2 seconds
    setInterval(fetchLiveStats, 2000);
});

// 🔄 FETCH LIVE STATS & LOGS FROM FLASK SERVER
function fetchLiveStats() {
    fetch('/api/get_live_stats')
        .then(response => response.json())
        .then(data => {
            updateConnectedClientsUI(data.active_clients_count || data.active_clients || 0);
            updateLogsTableUI(data.logs || []);
        })
        .catch(error => {
            console.error("⚠️ Error fetching live stats:", error);
        });
}

// 📱 1. UPDATE CONNECTED CLIENTS COUNT IN UI
function updateConnectedClientsUI(count) {
    // Dynamic Fallback: Gateway active connection unte Minimum 1 device
    const displayCount = count > 0 ? count : 1;

    // Update all matching elements on Dashboard UI
    const clientElems = document.querySelectorAll('.connected-clients-count, #activeClientsCount, [data-client-count]');
    
    clientElems.forEach(el => {
        el.innerText = `${displayCount} Connected Device(s)`;
    });

    // Specific Badge UI Updates if present
    const statusBadges = document.querySelectorAll('.client-status-badge');
    statusBadges.forEach(badge => {
        badge.innerText = `${displayCount} Active`;
    });
}

// 📋 2. UPDATE LIVE TRAFFIC LOGS TABLE
function updateLogsTableUI(logs) {
    const tableBody = document.getElementById('logsTableBody') || document.querySelector('table tbody');
    
    if (!tableBody || !logs) return;

    if (logs.length === 0) {
        return; // Empty state default HTML rendering
    }

    let rowsHTML = "";

    logs.forEach((log, index) => {
        const isBlocked = log.decision && log.decision.toUpperCase().includes("BLOCK");
        const statusClass = isBlocked ? "status-blocked" : "status-allowed";
        const badgeStyle = isBlocked 
            ? "background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3);" 
            : "background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3);";

        rowsHTML += `
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); transition: 0.2s;">
                <td style="padding: 12px 16px; color: #94a3b8; font-size: 13px;">${log.time || '--:--'}</td>
                <td style="padding: 12px 16px; font-weight: 600; color: #f8fafc; font-size: 13px;">${log.ip || '192.168.137.1'}</td>
                <td style="padding: 12px 16px; color: #38bdf8; font-weight: 500; font-size: 13px;">${log.url || log.website || 'General Traffic'}</td>
                <td style="padding: 12px 16px; color: #cbd5e1; font-size: 13px;">${log.category || 'Wi-Fi Traffic'}</td>
                <td style="padding: 12px 16px;">
                    <span style="padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 11px; ${badgeStyle}">
                        ${log.decision || 'CONNECTED'}
                    </span>
                </td>
            </tr>
        `;
    });

    tableBody.innerHTML = rowsHTML;
}

// 🎯 MANUAL MODEL TEST TRIGGER (If search test present in UI)
function testDomainAI(websiteUrl) {
    if (!websiteUrl) return;

    fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ website: websiteUrl })
    })
    .then(res => res.json())
    .then(data => {
        console.log("🧠 AI Prediction Result:", data);
    })
    .catch(err => console.error("AI Prediction Error:", err));
}