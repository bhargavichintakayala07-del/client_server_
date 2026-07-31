import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
import joblib

# 🧠 IMPORT AI ENGINE MODULE FROM ROOT DIRECTORY
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from AI_ENGINE.ai_engine import inspect_traffic_ai
    AI_ENGINE_ENABLED = True
    print("🤖 NetFlow-AI Smart Engine Loaded Successfully!")
except ImportError as e:
    AI_ENGINE_ENABLED = False
    print(f"⚠️ Warning: AI_ENGINE not found ({e}). Using default rules.")

try:
    from tracker import get_active_client_count
    TRACKER_ENABLED = True
except ImportError:
    TRACKER_ENABLED = False
    def get_active_client_count():
        return 0

try:
    from database import save_log, get_logs, get_statistics
    DB_ENABLED = True
except ImportError:
    DB_ENABLED = False

app = Flask(__name__)
app.secret_key = "netflow_ai_secret_key"

# Memory State Fallbacks
owner_data = {
    "name": "Bhargavi", 
    "phone": "9032174260", 
    "age": "19", 
    "city": "vijayawada", 
    "org_type": "nri"
}

# 📡 REAL-TIME NETWORK CONFIGURATION (UPDATED IPs)
LAPTOP_A_IP = "172.16.46.175"
LAPTOP_B_IP = "172.16.40.167"

routers_list = [
    {
        "id": 1,
        "name": "Laptop_A_Hotspot",
        "ssid": "Laptop_A_Hotspot",
        "ip": LAPTOP_A_IP,
        "password": "••••••••",
        "active_clients": 0,
        "max_limit": 50,
        "live_speed": "0 Mbps"
    },
    {
        "id": 2,
        "name": "Laptop_B_Hotspot",
        "ssid": "Laptop_B_Hotspot",
        "ip": LAPTOP_B_IP,
        "password": "••••••••",
        "active_clients": 0,
        "max_limit": 50,
        "live_speed": "0 Mbps"
    }
]

device_tracker = {}

# ============================
# 🌐 PAGE ROUTES
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
    return render_template('dashboard.html', 
                           owner=owner_data, 
                           routers_list=routers_list, 
                           logs=list(device_tracker.values()), 
                           active_clients_count=len(device_tracker))

# ============================
# 📡 GATEWAY & DASHBOARD APIs
# ============================

@app.route('/api/signup', methods=['POST'])
def api_signup():
    global owner_data
    data = request.get_json() or {}
    owner_data["name"] = data.get("name", owner_data["name"])
    owner_data["phone"] = data.get("phone", owner_data["phone"])
    owner_data["city"] = data.get("location", owner_data["city"])
    owner_data["org_type"] = data.get("org_type", owner_data["org_type"])
    return jsonify({"success": True})

@app.route('/api/login', methods=['POST'])
def api_login():
    return jsonify({"success": True})

@app.route('/api/save_setup', methods=['POST'])
def save_setup():
    global owner_data, routers_list
    data = request.get_json() or {}
    owner_data["name"] = data.get("name", owner_data["name"])
    owner_data["phone"] = data.get("phone", owner_data["phone"])
    owner_data["city"] = data.get("city", owner_data["city"])
    owner_data["org_type"] = data.get("org_type", owner_data["org_type"])
    
    if "routers" in data and len(data["routers"]) > 0:
        new_list = []
        for idx, r in enumerate(data["routers"]):
            new_list.append({
                "id": idx + 1,
                "name": r.get("name", f"Router_{idx+1}"),
                "ssid": r.get("name", f"Router_{idx+1}"),
                "ip": r.get("ip", LAPTOP_A_IP if idx == 0 else LAPTOP_B_IP),
                "password": r.get("password", "12345678"),
                "active_clients": 0,
                "max_limit": 50,
                "live_speed": "0 Mbps"
            })
        routers_list = new_list
    return jsonify({"success": True})

# 📡 REALTIME GATEWAY RECEIVER API WITH GUARANTEED SOURCE MATCHING
@app.route('/api/add_log', methods=['POST'])
@app.route('/log', methods=['POST'])
def add_log():
    global device_tracker, routers_list
    data = request.get_json() or {}
    
    if data:
        client_ip = str(data.get('ip', '127.0.0.1')).strip()
        gateway_source = str(data.get('gateway_ip', '')).strip()
        router_id = data.get('router_id', None)
        router_name_tag = str(data.get('router_name', '')).lower()
        
        # Ignore Host Direct Gateways / Self-IPs
        if client_ip in [LAPTOP_A_IP, LAPTOP_B_IP, "192.168.137.1", "127.0.0.1"]:
            return jsonify({"status": "ignored"}), 200

        time_val = data.get('time', datetime.now().strftime("%I:%M:%S %p"))
        url_val = data.get('url', data.get('website', ''))
        cat_val = data.get('category', 'Wi-Fi Traffic')
        dec_val = str(data.get('decision', 'CONNECTED')).upper()

        # 🧠 AI ENGINE INSPECTION
        ai_decision = dec_val
        ai_category = cat_val

        if url_val and AI_ENGINE_ENABLED:
            ai_eval = inspect_traffic_ai(url_val)
            if ai_eval["action"] == "BLOCK":
                ai_decision = str(ai_eval["decision"]).upper()
                ai_category = ai_eval["category"]

        current_timestamp = datetime.now().timestamp()

        # 🎯 STRICT ROUTER MATCHING (Source Header & IP Subnet Fallbacks)
        request_origin = request.remote_addr or ""
        assigned_router = "Laptop_A_Hotspot"

        if (router_id == 2 or 
            LAPTOP_B_IP in gateway_source or 
            LAPTOP_B_IP in request_origin or 
            "172.16.40." in client_ip or 
            "172.16.40." in request_origin or 
            "laptop_b" in router_name_tag or 
            "b_hotspot" in router_name_tag):
            assigned_router = "Laptop_B_Hotspot"

        device_key = f"{assigned_router}_{client_ip}"

        if device_key not in device_tracker:
            device_tracker[device_key] = {
                'ip': client_ip,
                'time': time_val,
                'last_seen': current_timestamp,
                'url': 'Active Connection',
                'category': 'Wi-Fi Access',
                'decision': 'CONNECTED',
                'blocked_count': 0,
                'router_name': assigned_router
            }
        
        device_tracker[device_key]['time'] = time_val
        device_tracker[device_key]['last_seen'] = current_timestamp
        device_tracker[device_key]['router_name'] = assigned_router

        if "BLOCK" in ai_decision or "RESTRICTED" in ai_category.upper() or (url_val and url_val != "Hotspot Client Network Sync"):
            if "BLOCK" in ai_decision or "RESTRICTED" in ai_category.upper():
                device_tracker[device_key]['url'] = url_val
                device_tracker[device_key]['category'] = ai_category
                device_tracker[device_key]['decision'] = ai_decision
                device_tracker[device_key]['blocked_count'] += 1
            elif url_val != "Hotspot Client Network Sync":
                device_tracker[device_key]['url'] = url_val

    return jsonify({"status": "success"}), 200


# 🔄 REALTIME DASHBOARD STATS API (AUTO INSTANT DECREASE ON DISCONNECT)
@app.route('/api/get_logs', methods=['GET'])
@app.route('/api/get_live_stats', methods=['GET'])
def get_live_stats():
    global device_tracker, routers_list
    
    # Strict 10-Second Timeout: Disconnected devices are dropped automatically!
    now = datetime.now().timestamp()
    active_devices = {}
    for dev_key, dev in device_tracker.items():
        if now - dev.get('last_seen', now) < 10:
            active_devices[dev_key] = dev

    device_tracker = active_devices

    r1_clients = 0
    r2_clients = 0

    for dev in device_tracker.values():
        r_name = dev.get('router_name', '')
        if r_name == "Laptop_B_Hotspot":
            r2_clients += 1
        elif r_name == "Laptop_A_Hotspot":
            r1_clients += 1

    if len(routers_list) >= 1:
        routers_list[0]['active_clients'] = r1_clients
        routers_list[0]['live_speed'] = f"{r1_clients * 350} Mbps" if r1_clients > 0 else "0 Mbps"

    if len(routers_list) >= 2:
        routers_list[1]['active_clients'] = r2_clients
        routers_list[1]['live_speed'] = f"{r2_clients * 350} Mbps" if r2_clients > 0 else "0 Mbps"

    return jsonify({
        "active_clients": len(device_tracker),
        "active_clients_count": len(device_tracker),
        "routers": routers_list,
        "logs": list(device_tracker.values())
    })

# 🧹 RESET CONNECTIONS ROUTE
@app.route('/api/clear_connections', methods=['POST', 'GET'])
def clear_connections():
    global device_tracker
    device_tracker = {}
    return jsonify({"status": "cleared", "message": "All active connections reset to 0"})

if __name__ == '__main__':
    print("🚀 NETFLOW-AI ADMIN SERVER RUNNING ON http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)