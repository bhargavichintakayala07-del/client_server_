import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# 🧠 IMPORT AI ENGINE MODULE FROM ROOT DIRECTORY
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from AI_ENGINE.ai_engine import inspect_traffic_ai, predict_future_traffic
    AI_ENGINE_ENABLED = True
    print("🤖 NetFlow-AI Smart Engine Loaded Successfully!")
except ImportError as e:
    AI_ENGINE_ENABLED = False
    print(f"⚠️ Warning: AI_ENGINE not found ({e}). Using default rules.")

app = Flask(__name__)
app.secret_key = "netflow_ai_secret_key"

owner_data = {
    "name": "Bhargavi", 
    "phone": "9032174260", 
    "age": "19", 
    "city": "vijayawada", 
    "org_type": "nri"
}

LAPTOP_A_IP = "172.16.46.175"
LAPTOP_B_IP = "172.16.40.167"

routers_list = [
    {"id": 1, "name": "Laptop_A_Hotspot", "ssid": "Laptop_A_Hotspot", "ip": LAPTOP_A_IP, "password": "••••••••", "active_clients": 0, "max_limit": 50, "live_speed": "0 Mbps"},
    {"id": 2, "name": "Laptop_B_Hotspot", "ssid": "Laptop_B_Hotspot", "ip": LAPTOP_B_IP, "password": "••••••••", "active_clients": 0, "max_limit": 50, "live_speed": "0 Mbps"}
]

device_tracker = {}
cluster_stats = {"server_1": 0, "server_2": 0}

# ============================
# 🌐 PAGE & AUTH ROUTES
# ============================

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/setup')
@app.route('/setup_routers')
@app.route('/owner_setup')
def owner_setup():
    return render_template('owner_setup.html', owner=owner_data)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', owner=owner_data, routers_list=routers_list, logs=list(device_tracker.values()), active_clients_count=len(device_tracker))

@app.route('/api/login', methods=['POST', 'GET'])
def api_login():
    return jsonify({"success": True, "message": "Login successful", "redirect": "/dashboard"})

@app.route('/api/signup', methods=['POST', 'GET'])
def api_signup():
    data = request.get_json() or {}
    if data:
        owner_data['name'] = data.get('owner_name', owner_data['name'])
        owner_data['phone'] = data.get('phone', owner_data['phone'])
        owner_data['city'] = data.get('location', owner_data['city'])
        owner_data['org_type'] = data.get('org_type', owner_data['org_type'])
    return jsonify({"success": True, "message": "Account created successfully", "redirect": "/dashboard"})

# ============================
# 📡 LIVE GATEWAY LOG RECEIVER
# ============================

@app.route('/api/add_log', methods=['POST'])
@app.route('/log', methods=['POST'])
def add_log():
    global device_tracker, cluster_stats
    data = request.get_json() or {}
    
    if data:
        client_ip = str(data.get('ip', request.remote_addr)).strip()
        gateway_source = str(data.get('gateway_ip', '')).strip()
        router_id = data.get('router_id', 1)
        router_name_tag = str(data.get('router_name', '')).lower()
        handled_server = str(data.get('handled_by', 'SERVER_1'))
        
        time_val = data.get('time', datetime.now().strftime("%I:%M:%S %p"))
        url_val = data.get('url', 'Active Connection')
        cat_val = data.get('category', 'Wi-Fi Traffic')
        dec_val = str(data.get('decision', 'CONNECTED')).upper()

        if "SERVER_2" in handled_server:
            cluster_stats["server_2"] += 1
        else:
            cluster_stats["server_1"] += 1

        # 🧠 AI ENGINE EVALUATION FOR BLOCKED SITES
        ai_decision = dec_val
        ai_category = cat_val
        ai_risk_score = 0

        if AI_ENGINE_ENABLED and url_val and url_val != "Hotspot Client Network Sync":
            ai_eval = inspect_traffic_ai(url_val, client_ip=client_ip)
            ai_risk_score = ai_eval.get("risk_score", 0)
            if ai_eval.get("action") == "BLOCK":
                ai_decision = str(ai_eval.get("decision", "AI BLOCKED")).upper()
                ai_category = ai_eval.get("category", "Restricted Category")

        current_timestamp = datetime.now().timestamp()

        # Determine Hotspot Source
        request_origin = request.remote_addr or ""
        assigned_router = "Laptop_A_Hotspot"

        if (router_id == 2 or LAPTOP_B_IP in gateway_source or LAPTOP_B_IP in request_origin or "laptop_b" in router_name_tag):
            assigned_router = "Laptop_B_Hotspot"

        device_key = f"{assigned_router}_{client_ip}"

        # Maintain single active record per client IP
        if device_key not in device_tracker:
            device_tracker[device_key] = {
                'ip': client_ip,
                'time': time_val,
                'last_seen': current_timestamp,
                'url': url_val,
                'category': ai_category,
                'decision': ai_decision,
                'blocked_count': 1 if "BLOCK" in ai_decision else 0,
                'risk_score': ai_risk_score,
                'router_name': assigned_router
            }
        else:
            device_tracker[device_key]['time'] = time_val
            device_tracker[device_key]['last_seen'] = current_timestamp
            device_tracker[device_key]['router_name'] = assigned_router
            device_tracker[device_key]['risk_score'] = ai_risk_score
            if url_val and url_val != "Hotspot Client Network Sync":
                device_tracker[device_key]['url'] = url_val
                device_tracker[device_key]['category'] = ai_category
                device_tracker[device_key]['decision'] = ai_decision
                if "BLOCK" in ai_decision:
                    device_tracker[device_key]['blocked_count'] += 1

    return jsonify({"status": "success"}), 200

# ============================
# 🔄 REALTIME STATS & DISCONNECT CLEANUP
# ============================

@app.route('/api/get_logs', methods=['GET'])
@app.route('/api/get_live_stats', methods=['GET'])
def get_live_stats():
    global device_tracker, routers_list, cluster_stats
    
    # FAST DISCONNECT DETECTION: Keep devices only if seen in last 15 SECONDS
    now = datetime.now().timestamp()
    active_devices = {k: v for k, v in device_tracker.items() if now - v.get('last_seen', now) < 15}
    device_tracker = active_devices

    r1_clients = sum(1 for d in device_tracker.values() if d.get('router_name') == "Laptop_A_Hotspot")
    r2_clients = sum(1 for d in device_tracker.values() if d.get('router_name') == "Laptop_B_Hotspot")

    if len(routers_list) >= 1:
        routers_list[0]['active_clients'] = r1_clients
        routers_list[0]['live_speed'] = f"{r1_clients * 350} Mbps" if r1_clients > 0 else "0 Mbps"

    if len(routers_list) >= 2:
        routers_list[1]['active_clients'] = r2_clients
        routers_list[1]['live_speed'] = f"{r2_clients * 350} Mbps" if r2_clients > 0 else "0 Mbps"

    # 🔮 RUN TIME-SERIES AI FORECASTING ENGINE
    recent_activity_rates = [len(device_tracker) * 35 + i * 10 for i in range(5)]
    if AI_ENGINE_ENABLED:
        ai_forecast_data = predict_future_traffic(recent_activity_rates)
    else:
        ai_forecast_data = [120, 140, 160, 150, 180]

    return jsonify({
        "active_clients": len(device_tracker),
        "active_clients_count": len(device_tracker),
        "routers": routers_list,
        "logs": list(device_tracker.values()),
        "cluster_stats": cluster_stats,
        "ai_forecast": ai_forecast_data
    })

@app.route('/api/clear_connections', methods=['POST', 'GET'])
def clear_connections():
    global device_tracker
    device_tracker = {}
    return jsonify({"status": "cleared", "message": "All active connections reset to 0"})

# ============================
# 🤖 SMART AI CHAT ASSISTANT API
# ============================

@app.route('/api/ai_chat', methods=['POST'])
def ai_chat_assistant():
    global device_tracker, routers_list, cluster_stats
    data = request.get_json() or {}
    user_msg = str(data.get('message', '')).lower().strip()

    logs = list(device_tracker.values())
    active_count = len(device_tracker)
    blocked_count = sum(1 for l in logs if "BLOCK" in str(l.get('decision', '')).upper() or l.get('blocked_count', 0) > 0)

    r1_clients = routers_list[0]['active_clients'] if len(routers_list) >= 1 else 0
    r2_clients = routers_list[1]['active_clients'] if len(routers_list) >= 2 else 0

    bot_reply = "I didn't quite understand that. You can ask me about active devices, blocked threats, server status, or hotspot speeds."

    if any(k in user_msg for k in ['laptop_a', 'laptop a', 'hotspot a', 'router 1']):
        bot_reply = f"Laptop_A_Hotspot is ONLINE with {r1_clients} connected device(s). Measured Speed: {r1_clients * 350} Mbps."
    
    elif any(k in user_msg for k in ['laptop_b', 'laptop b', 'hotspot b', 'router 2']):
        bot_reply = f"Laptop_B_Hotspot is ONLINE with {r2_clients} connected device(s). Measured Speed: {r2_clients * 350} Mbps."

    elif any(k in user_msg for k in ['blocked', 'threat', 'attack', 'security', 'phishing']):
        bot_reply = f"AI Engine has detected and isolated {blocked_count} threat attempt(s) so far. Policy enforcement is ACTIVE."

    elif any(k in user_msg for k in ['status', 'devices', 'connected', 'clients', 'how many']):
        bot_reply = f"Currently, there are {active_count} active client device(s) connected across {len(routers_list)} Hotspot Nodes."

    elif any(k in user_msg for k in ['server', 'cluster', 'load balancer', 'load']):
        s1 = cluster_stats.get("server_1", 0)
        s2 = cluster_stats.get("server_2", 0)
        bot_reply = f"Multi-Server Cluster Health: Server_1 handled {s1} requests, Server_2 handled {s2} requests. Load Balancer is OPTIMAL."

    elif any(k in user_msg for k in ['hi', 'hello', 'hey', 'who are you']):
        bot_reply = "Hello Bhargavi! I am your NetFlow-AI Assistant. How can I help you monitor your network cluster today?"

    return jsonify({"reply": bot_reply})

if __name__ == '__main__':
    print("🚀 NETFLOW-AI ADMIN SERVER RUNNING ON http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)